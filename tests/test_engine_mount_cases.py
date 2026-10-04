"""The engine-mount family in the assembled deck (design note 66, #286): G-66.x.

ENGLOADS's 23.361/23.371 conditions (and the FAR 25 equivalents) become
balanced cases: an assembled flight case in SELECT's PHAA block scaled to the
load factor ENGLOADS states for the engine, plus the engine's own torque,
gyroscopic couples and thrust at its own mount and hub nodes. 23.363 and
23.361(b)(1) are mount-local (note 66 Q1) and recorded as not assembled.
"""

import math
import os
import sys
from dataclasses import replace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.cg_cases import flight_cases
from sloads.export.coordinates import engine_applied_load, engine_thrust_axis
from sloads.export.lra_model import build_lra_model, transferred_case_loads
from sloads.load_keys import FX_THRUST, MX_MOUNT_TORQUE, parse_gyro_key
from sloads.mass_distribution import derive_case_loadings
from sloads.models import BalancedLoad
from sloads.modules import engine
from sloads.modules.balance import build_balanced_cases, is_engine_mount, reflect_load
from sloads.modules.balance.air import assemble
from sloads.modules.balance.applied import HUB_THRUST_SOURCE
from sloads.modules.balance.engine_cases import (
    AILERON_TRIM_SOURCE,
    EM_BALANCED,
    EM_MOUNT_LOCAL,
    ENGINE_MOUNT_THRUST_SOURCE,
    ROTATION_FIXED_SOURCES,
    _scaled,
)
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.structural_speeds import design_speed_values
from sloads.report.render import load_cases_to_rows
from sloads.units import format_value

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_ENGINE_FIXTURES = ("ga6_normal", "baron_58", "atr42_100", "concept_regional_jet")

#: G-66.2, measured: the EM cases each fixture assembles and the ENGLOADS
#: conditions it records as mount-local. ga6 and the Baron are reciprocating
#: (23.361(a)(1)/(a)(2) assemble, 23.363 is local); the ATR is a turboprop
#: (+(a)(3) and 23.371(b)'s four sign cases; 23.361(b)(1) local); the RJ adds
#: FAR 25.361(a)(3)(i)/(ii) and 25.371's four.
_EXPECTED = {
    "ga6_normal": (["EM-01", "EM-02"], ["EM-03"]),
    "baron_58": (["EM-01", "EM-02", "EM-04", "EM-05"], ["EM-03", "EM-06"]),
    "atr42_100": (["EM-01", "EM-02", "EM-04", "EM-06", "EM-07", "EM-08", "EM-09",
                   "EM-10", "EM-11", "EM-13", "EM-15", "EM-16", "EM-17", "EM-18"],
                  ["EM-03", "EM-05", "EM-12", "EM-14"]),
    "concept_regional_jet": (
        [f"EM-{i:02d}" for i in (1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                                 16, 17, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30)],
        ["EM-03", "EM-05", "EM-18", "EM-20"]),
}


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _built(name):
    project = _project(name)
    skipped = []
    cases = build_balanced_cases(project, skipped)
    return project, cases, skipped


def _em(cases):
    return [c for c in cases if is_engine_mount(c)]


def _by_id(project):
    return {c.case_ref.case_id: c for c in engine.run(project).conditions}


@pytest.mark.parametrize("name", _ENGINE_FIXTURES)
def test_the_deck_carries_exactly_the_ruled_engine_set(name):
    """**G-66.2** (note 66 Q1, D-66.3): the paired conditions assemble, the
    mount-local ones are recorded with their reason, and nothing else."""
    project, cases, skipped = _built(name)
    assembled = [c.case_ref.case_id for c in _em(cases)]
    conds = _by_id(project)
    recorded = [cid for cid, c in conds.items()
                if any(s.component == "engine_mount" and s.label == c.title
                       and s.code == "mount-local" for s in skipped)]
    assert (assembled, recorded) == _EXPECTED[name]
    for cid in assembled:
        assert conds[cid].far_reference in EM_BALANCED
    for cid in recorded:
        assert conds[cid].far_reference in EM_MOUNT_LOCAL


def test_an_engineless_project_has_no_engine_cases():
    _, cases, skipped = _built("concept_heavy")
    assert not _em(cases)
    assert not [s for s in skipped if s.component == "engine_mount"]


@pytest.mark.parametrize("name", _ENGINE_FIXTURES + ("concept_heavy",))
def test_every_balanced_case_states_the_tables_factor(name):
    """**G-66.1** (D-66.1): every assembled case carries its factor -- 1.0 on
    23.367(a)(2), which the regulation prescribes already ultimate, and 1.5 on
    every other family, the EM cases among them. Pinned by rule, not asked of
    ``safety_factors.table_for`` as the stamp itself does (#318: a gate that
    calls the code's owner passes whatever that owner answers). Before #286
    the field was never set."""
    _, cases, _ = _built(name)
    for c in cases:
        want = 1.0 if c.case_ref.far_reference == "23.367(a)(2)" else 1.5
        assert c.safety_factor == want, (c.label, c.case_ref.far_reference, c.safety_factor)
    assert {c.safety_factor for c in _em(cases)} <= {1.5}


@pytest.mark.parametrize("name", _ENGINE_FIXTURES)
def _pinned_n(far_reference, limnz):
    """The load factor each paired condition names, from the rule and the
    engine's entered ``limit_load_factor`` -- not from ENGLOADS's vertical,
    which is what the code divides (#318). 23.361(a)(1): 75 % of condition A;
    (a)(2): 100 %; (a)(3) and 25.361(a)(3): 1 g; 23.371(b): 2.5; 25.371: the A2
    factor (25.333(b)), which ENGLOADS reads as the engine's LIMNZ."""
    return {"23.361(a)(1)": 0.75 * limnz, "23.361(a)(2)": limnz,
            "23.361(a)(3)": 1.0, "25.361(a)(3)(i)": 1.0, "25.361(a)(3)(ii)": 1.0,
            "23.371(b)": 2.5, "25.371": limnz}[far_reference]


def _engine_index(project):
    """``{EM id: 1-based engine}`` from ENGLOADS's own per-engine condition
    lists, in the order ``engine.run`` mints ids over them."""
    out, conds = {}, engine.run(project).conditions
    taken = 0
    for i, eng in enumerate(engine.resolved_engines(project), start=1):
        count = len(engine.mount_conditions(eng, include_far25=project.include_far25))
        out.update({c.case_ref.case_id: i for c in conds[taken:taken + count]})
        taken += count
    return out


def _engine_of(case, project):
    """The engine an EM case is for: the one its EM id was minted for. A
    gyroscopic case carries every engine's loads (D-66.4a), so the loads
    cannot say."""
    i = _engine_index(project)[case.case_ref.case_id]
    return project.engines[i - 1], f"engine-{i}"


def _gyro_sub(cond):
    return next(p[0] for p in (parse_gyro_key(v.key) for v in cond.values) if p)


@pytest.mark.parametrize("name", _ENGINE_FIXTURES)
def test_the_case_flies_at_the_load_factor_engloads_states(name):
    """**G-66.3**, the no-double-count identity's first half: each case flies
    at the load factor its condition names, stated independently of ENGLOADS
    (:func:`_pinned_n`) -- so a wrong ENGLOADS vertical fails here -- and the
    engine's mass, already in the parent's inertia, is loaded at that ``n``
    with no vertical re-applied. The factor is the engine's own
    ``limit_load_factor`` (#318 ruling 1a), and on every fixture it is the
    airplane's own n1 -- the condition A the parent flew. On ``baron_58``
    both are the POH's 4.2, entered as STRSPEED's chosen n (#331 ruling (d));
    before #331 n1 fell to the 23.337 minimum of 3.648 and the torque cases
    flew 15 % above condition A."""
    project, cases, _ = _built(name)
    n1 = design_speed_values(project, project.speeds).n
    for c in _em(cases):
        eng, _ = _engine_of(c, project)
        assert math.isclose(eng.limit_load_factor, n1, rel_tol=1e-9), (
            c.label, eng.limit_load_factor, n1)
        want = _pinned_n(c.case_ref.far_reference, eng.limit_load_factor)
        assert math.isclose(c.nz, want, rel_tol=1e-9), (c.label, c.nz, want)
        # ...and no load in the case is a re-applied engine vertical.
        assert not [ld for ld in c.loads if ld.source.startswith("engine-") and ld.fz
                    and ld.source != ENGINE_MOUNT_THRUST_SOURCE]


@pytest.mark.parametrize("name", ("ga6_normal", "baron_58", "atr42_100"))
def test_the_itemised_engine_weighs_what_englods_weighs(name):
    """**G-66.3**'s second half, where the database itemises the engine: its
    engine and propeller rows equal ENGLOADS's ``PPWT`` to the pound, so the
    inertia the parent carries at ``n`` is ENGLOADS's ``n * PPWT``. (The RJ
    carries its two engines as one 3,400 lb centreline lump against 2 x 1,550
    -- a data statement, not this gate's.)"""
    project = _project(name)
    engines = engine.resolved_engines(project)
    rows = [it for it in project.weight.items
            if it.name.lower().startswith(("engine", "propeller"))
            and not it.name.lower().startswith("engine accessories")]
    assert math.isclose(sum(r.weight_lb for r in rows),
                        sum(engine.combined_weight(e) for e in engines), abs_tol=1e-9)


@pytest.mark.parametrize("name", _ENGINE_FIXTURES)
def test_the_increment_is_the_mount_modules_on_its_own_engine(name):
    """**G-66.4** (D-66.5/D-66.6): the engine loads are
    ``engine_applied_load`` of ENGLOADS's scalars, and they land on **their
    own** engine's nodes in the LRA model -- torque and couples at the mount,
    thrust at the hub. A gyroscopic case carries **every** engine's couples and
    thrust (G-66.4 as amended at #319, D-66.4a), each from that engine's own
    condition of the same FAR reference and sub-case."""
    project, cases, _ = _built(name)
    conds = _by_id(project)
    owner = _engine_index(project)
    model = build_lra_model(project)
    engines = engine.resolved_engines(project)
    eng_nodes = {n.gid for n in model.nodes if n.family.startswith("lra-engine")}
    for c in _em(cases):
        cond = conds[c.case_ref.case_id]
        index = owner[c.case_ref.case_id]
        own = [ld for ld in c.loads
               if ld.source in ("engine-torque", "engine-gyro", ENGINE_MOUNT_THRUST_SOURCE)]
        if any(ld.source == "engine-torque" for ld in own):
            values = {v.key: v.value for v in cond.values}
            axis, _ = engine_thrust_axis(engines[index - 1])
            _, m = engine_applied_load(axis, torque=values[MX_MOUNT_TORQUE])
            (torque,) = own
            assert torque.carrier == f"engine-{index}"
            assert (torque.mx, torque.my, torque.mz) == pytest.approx(tuple(12 * v for v in m))
            members = {torque.carrier}
        else:
            members = set()
            for j, eng in enumerate(engines, start=1):
                partner = next(x for x in conds.values()
                               if owner[x.case_ref.case_id] == j
                               and x.far_reference == cond.far_reference
                               and any(parse_gyro_key(v.key) for v in x.values)
                               and _gyro_sub(x) == _gyro_sub(cond))
                values = {v.key: v.value for v in partner.values}
                myy = mzz = 0.0
                for v in partner.values:
                    parsed = parse_gyro_key(v.key)
                    if parsed:
                        myy, mzz = (v.value, mzz) if parsed[1] == "myy" else (myy, v.value)
                axis, _ = engine_thrust_axis(eng)
                _, m = engine_applied_load(axis, myy=myy, mzz=mzz)
                gyro = next(ld for ld in own if ld.source == "engine-gyro"
                            and ld.carrier == f"engine-{j}")
                assert (gyro.mx, gyro.my, gyro.mz) == pytest.approx(tuple(12 * v for v in m))
                f, _ = engine_applied_load(axis, thrust=values[FX_THRUST])
                thrust = next(ld for ld in own if ld.source == ENGINE_MOUNT_THRUST_SOURCE
                              and ld.carrier == f"engine-{j}")
                assert (thrust.fx, thrust.fy, thrust.fz) == pytest.approx(f)
                members.add(f"engine-{j}")
            assert len(own) == 2 * len(engines), c.label
        gids = {n.gid for m in members for n in model.members[m]}
        landed = transferred_case_loads(c, model)
        assert {g for g in landed if g in eng_nodes} <= gids, c.label
        for ld in own:
            mine = {n.gid for n in model.members[ld.carrier]}
            single = transferred_case_loads(replace(c, loads=[ld]), model)
            assert {g for g in single if g in eng_nodes} <= mine, (c.label, ld.carrier)


@pytest.mark.parametrize("name", _ENGINE_FIXTURES)
def test_the_case_is_the_scaled_parent_plus_the_increment(name):
    """**G-66.5** (D-66.4), as the note agreed: the EM case minus its engine
    increment equals the scaled parent, load for load.

    The parent is built here, on its own -- the flight case at the EM case's
    V-n point and CG case, assembled without every engine's entered thrust on
    a gyroscopic case (#313, D-66.4a) -- and scaled by hand by ``k`` = the pinned load
    factor over its own ``nz``: every load times ``k`` except an entered hub
    thrust, which is the engine's and does not scale. The EM case must open
    with exactly those loads, in order, and carry nothing after them but the
    engine increment (its torque or couples, thrust and trim) and the relief
    that closes it. Before #318 the gate never built the parent: it checked a
    closure true by construction, and skipped every gyroscopic and inclined
    torque case, whose increment resultant is non-zero."""
    project, cases, _ = _built(name)
    vn = {p.case: p for p in build_envelope(project).vn}
    cgs = {c.name: c for c in flight_cases(project)}
    loadings = {ld.name: ld for ld in derive_case_loadings(project)}
    increment = {"engine-torque", "engine-gyro", ENGINE_MOUNT_THRUST_SOURCE, AILERON_TRIM_SOURCE}
    for c in _em(cases):
        eng, _ = _engine_of(c, project)
        gyro = any(ld.source == "engine-gyro" for ld in c.loads)
        every = tuple(f"engine-{j}" for j in range(1, len(project.engines) + 1))
        parent = assemble(project, c.label, vn[c.vn_case], loadings[c.cg], cgs[c.cg],
                          thrust_replaced=every if gyro else ())
        k = _pinned_n(c.case_ref.far_reference, eng.limit_load_factor) / parent.nz
        head, tail = c.loads[:len(parent.loads)], c.loads[len(parent.loads):]
        for got, base in zip(head, parent.loads, strict=True):
            scale = 1.0 if base.source == HUB_THRUST_SOURCE else k
            assert (got.source, got.x, got.y, got.z) == (base.source, base.x, base.y, base.z)
            for q in ("fx", "fy", "fz", "mx", "my", "mz"):
                assert getattr(got, q) == pytest.approx(scale * getattr(base, q),
                                                        rel=1e-12, abs=1e-9), (c.label, q)
        assert {ld.source for ld in tail} - increment <= {
            s for s in (ld.source for ld in tail) if s.startswith("closure-")}, c.label
        assert {ld.source for ld in tail} & increment, c.label


@pytest.mark.parametrize("name", _ENGINE_FIXTURES)
def test_the_torque_is_trimmed_in_roll_and_no_case_is_handed(name):
    """**G-66.7** (D-66.7, note 21 P-9): every torque case carries the equal
    and opposite aileron-trim couple, so its engine loads net no rolling
    moment; no EM case is handed and none is mirrored."""
    _, cases, _ = _built(name)
    for c in _em(cases):
        assert c.hand == "" and not c.case_ref.case_id.endswith(("R", "L")), c.label
        torque = [ld for ld in c.loads if ld.source == "engine-torque"]
        trim = [ld for ld in c.loads if ld.source == AILERON_TRIM_SOURCE]
        assert len(torque) == len(trim)
        assert math.fsum(ld.mx for ld in torque + trim) == pytest.approx(0.0, abs=1e-9)


def test_a_reflection_keeps_the_propellers_sense():
    """D-66.7 / note 21 §4.4: the rotation-fixed couples keep their sense
    under a reflection (their position mirrors)."""
    assert ROTATION_FIXED_SOURCES == ("engine-torque", "engine-gyro")
    ld = BalancedLoad(x=50.0, y=66.0, z=97.0, mx=1000.0, my=-20.0, mz=30.0,
                      source="engine-torque", side="R")
    mirrored = reflect_load(ld)
    assert (mirrored.y, mirrored.side) == (-66.0, "L")
    assert (mirrored.mx, mirrored.my, mirrored.mz) == (1000.0, -20.0, 30.0)


def test_a_scaled_case_keeps_its_masses():
    """The scaling that builds the parent multiplies loads, never masses."""
    _, cases, _ = _built("ga6_normal")
    c = cases[0]
    s = _scaled(c, 0.75)
    assert [ld.weight_lb for ld in s.loads] == [ld.weight_lb for ld in c.loads]
    assert s.nz == pytest.approx(0.75 * c.nz)


def test_the_far_25_gyro_carries_its_a2_vertical():
    """**G-66.12** (D-66.8): 25.371's vertical, at the A2 load factor, reaches
    the rendered rows -- before #286 every reader looked for the 2.5 g key only
    and printed 0 on all four sign cases."""
    project = _project("concept_regional_jet")
    rows = [r for r in load_cases_to_rows(engine.run(project).conditions)
            if r["FAR"] == "25.371"]
    assert len(rows) == 8                      # 4 sign cases x 2 engines
    verticals = [row["Vertical load (lb)"] for row in rows]
    assert all(v not in (0, 0.0, "", None) for v in verticals), verticals


def test_each_gyroscopic_sign_case_has_its_own_id():
    """Note 66 Q7: each sign combination is a condition of its own with its
    own EM id, four per gyroscopic condition, consecutive, no suffix."""
    conds = engine.run(_project("atr42_100")).conditions
    gyro = [c.case_ref.case_id for c in conds if c.far_reference == "23.371(b)"]
    assert gyro == ["EM-06", "EM-07", "EM-08", "EM-09", "EM-15", "EM-16", "EM-17", "EM-18"]
    assert all(c.case_ref.case_id[-1].isdigit() for c in conds)


@pytest.mark.parametrize("name", ("atr42_100", "concept_regional_jet"))
def test_a_gyroscopic_case_thrusts_every_engine_and_yaws_on_none(name):
    """**G-66.17** (D-66.4a, #319): each 23.371(b)/25.371 case carries every
    engine's max-continuous thrust, so on a symmetric installation the thrusts'
    yawing moment about the CG is zero -- before #319 the ATR's case thrust its
    own engine alone, 10,865 lb at y = +/-161 in, a 1.75 M lb-in yaw. The net
    axial force is stated in band."""
    project, cases, _ = _built(name)
    gyros = [c for c in _em(cases) if any(ld.source == "engine-gyro" for ld in c.loads)]
    assert gyros
    for c in gyros:
        thrusts = [ld for ld in c.loads if ld.source == ENGINE_MOUNT_THRUST_SOURCE]
        assert {ld.carrier for ld in thrusts} == {f"engine-{j}"
                                                  for j in range(1, len(project.engines) + 1)}
        one = max(abs(ld.fx * ld.y) for ld in thrusts)
        yaw = math.fsum(ld.x * ld.fy - ld.y * ld.fx for ld in thrusts)
        assert abs(yaw) <= 1e-9 * max(one, 1.0), (c.label, yaw)
        net = abs(math.fsum(ld.fx for ld in thrusts))
        assert any(n.startswith("GYROSCOPIC") and f"{format_value(net, 'lb')} lb" in n for n in c.notes), c.label


def test_a_sub_case_is_the_airplanes_rates_on_every_engine():
    """D-66.4a / note 53 D-53.6 as amended at #319: the propeller's spin is
    signed by ``prop_direction`` as a rotor's is by its rpm, so sub-case ``k``
    is the same airplane yaw and pitch rate on every engine. A clockwise
    propeller's couples are unchanged; a counter-clockwise one's reverse; the
    RJ's counter-rotating fans (signed rotor rpm) cancel at one state, and the
    ATR's co-rotating propellers add -- and each case says which."""
    ga6 = _project("ga6_normal")
    cw = engine.resolved_engines(ga6)[0]
    ccw = replace(cw, prop_direction=type(cw.prop_direction).COUNTERCLOCKWISE)
    assert engine.spin_sense(cw) == 1.0 and engine.spin_sense(ccw) == -1.0
    atr = engine.resolved_engines(_project("atr42_100"))[0]
    flipped = replace(atr, prop_direction=type(atr.prop_direction).COUNTERCLOCKWISE,
                      rotors=[replace(r, max_rpm=-r.max_rpm) for r in atr.rotors])
    assert engine.angular_momentum(flipped) == pytest.approx(-engine.angular_momentum(atr))
    for a, b in zip(engine.condition_371_b(atr).values, engine.condition_371_b(flipped).values,
                    strict=True):
        if parse_gyro_key(a.key):
            assert b.value == pytest.approx(-a.value), a.key
    for name, spin_note in (("atr42_100", "spins the same way"),
                            ("concept_regional_jet", "do not all spin the same way")):
        project, cases, _ = _built(name)
        for c in _em(cases):
            gyro = [ld for ld in c.loads if ld.source == "engine-gyro"]
            if not gyro:
                continue
            total = math.fsum(ld.my for ld in gyro)
            one = abs(gyro[0].my)
            assert total == pytest.approx(0.0 if name == "concept_regional_jet" else 2 * gyro[0].my,
                                          abs=1e-9 * one), c.label
            assert any(spin_note in n for n in c.notes), c.label


def test_a_case_scaled_by_zero_is_recorded_not_shipped(monkeypatch):
    """#321 (note 66 §12 riders): an engine with no weight to state a load
    factor, or a parent at zero load factor, gave ``k = 0`` and shipped a case
    of no load with no record; it is recorded as unscalable."""
    from sloads.modules.balance import engine_cases

    monkeypatch.setattr(engine_cases, "_target_n", lambda *_a, **_kw: 0.0)
    _, cases, skipped = _built("ga6_normal")
    assert not _em(cases)
    assert {s.label for s in skipped if s.code == "unscalable"} == {
        c.title for cid, c in _by_id(_project("ga6_normal")).items()
        if c.far_reference in EM_BALANCED}


def test_a_refused_engine_family_is_recorded_not_swallowed():
    """#344. ENGLOADS refusing a present-but-invalid input used to empty the
    engine-mount family with nothing said, so the deck shipped without it. It
    is now one ``family-refused`` entry in the record of conditions not
    assembled, quoting the refusal; a project that runs records none."""
    project = _project("atr42_100")
    bad = replace(project, engines=[replace(project.engines[0], stop_time_s=-1.0),
                                    *project.engines[1:]])
    skipped = []
    cases = build_balanced_cases(bad, skipped)
    assert not [c for c in cases if is_engine_mount(c)]
    refused = [s for s in skipped if s.code == "family-refused"]
    assert len(refused) == 1 and refused[0].component == "engine", refused
    assert "stop_time_s" in refused[0].name and "must be positive" in refused[0].name
    clean = []
    build_balanced_cases(project, clean)
    assert not [s for s in clean if s.code == "family-refused"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
