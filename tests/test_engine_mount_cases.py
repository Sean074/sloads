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
from sloads.modules.balance.applied import _ROTATION_FIXED_SOURCES, HUB_THRUST_SOURCE
from sloads.modules.balance.engine_cases import (
    AILERON_TRIM_SOURCE,
    EM_BALANCED,
    EM_MOUNT_LOCAL,
    ENGINE_MOUNT_THRUST_SOURCE,
    ROTATION_FIXED_SOURCES,
    _scaled,
)
from sloads.modules.flight_envelope import build_envelope
from sloads.report.render import load_cases_to_rows

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


def _engine_of(case, project):
    """The engine an EM case is for: the one whose loads it carries."""
    member = next(ld.carrier for ld in case.loads
                  if ld.source in ("engine-torque", "engine-gyro"))
    return project.engines[int(member.split("-")[1]) - 1], member


@pytest.mark.parametrize("name", _ENGINE_FIXTURES)
def test_the_case_flies_at_the_load_factor_engloads_states(name):
    """**G-66.3**, the no-double-count identity's first half: each case flies
    at the load factor its condition names, stated independently of ENGLOADS
    (:func:`_pinned_n`) -- so a wrong ENGLOADS vertical fails here -- and the
    engine's mass, already in the parent's inertia, is loaded at that ``n``
    with no vertical re-applied. The factor is the engine's own
    ``limit_load_factor``: on ``baron_58`` that is the entered 4.2 against the
    airplane's 23.337 n1 of 3.648, a disagreement filed for the owner's ruling
    rather than pinned here (#318 ruling 1a)."""
    project, cases, _ = _built(name)
    for c in _em(cases):
        eng, _ = _engine_of(c, project)
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
    thrust at the hub."""
    project, cases, _ = _built(name)
    conds = _by_id(project)
    model = build_lra_model(project)
    engines = engine.resolved_engines(project)
    for c in _em(cases):
        cond = conds[c.case_ref.case_id]
        values = {v.key: v.value for v in cond.values}
        own = [ld for ld in c.loads
               if ld.source in ("engine-torque", "engine-gyro", ENGINE_MOUNT_THRUST_SOURCE)]
        member = own[0].carrier
        index = int(member.split("-")[1])
        axis, _ = engine_thrust_axis(engines[index - 1])
        if "torque" in {ld.source.split("-")[1] for ld in own}:
            _, m = engine_applied_load(axis, torque=values[MX_MOUNT_TORQUE])
            torque = next(ld for ld in own if ld.source == "engine-torque")
            assert (torque.mx, torque.my, torque.mz) == pytest.approx(tuple(12 * v for v in m))
        else:
            myy = mzz = 0.0
            for v in cond.values:
                parsed = parse_gyro_key(v.key)
                if parsed:
                    myy, mzz = (v.value, mzz) if parsed[1] == "myy" else (myy, v.value)
            _, m = engine_applied_load(axis, myy=myy, mzz=mzz)
            gyro = next(ld for ld in own if ld.source == "engine-gyro")
            assert (gyro.mx, gyro.my, gyro.mz) == pytest.approx(tuple(12 * v for v in m))
            f, _ = engine_applied_load(axis, thrust=values[FX_THRUST])
            thrust = next(ld for ld in own if ld.source == ENGINE_MOUNT_THRUST_SOURCE)
            assert (thrust.fx, thrust.fy, thrust.fz) == pytest.approx(f)
        gids = {n.gid for n in model.members[member]}
        landed = transferred_case_loads(c, model)
        eng_nodes = {n.gid for n in model.nodes if n.family.startswith("lra-engine")}
        assert {g for g in landed if g in eng_nodes} <= gids, c.label


@pytest.mark.parametrize("name", _ENGINE_FIXTURES)
def test_the_case_is_the_scaled_parent_plus_the_increment(name):
    """**G-66.5** (D-66.4), as the note agreed: the EM case minus its engine
    increment equals the scaled parent, load for load.

    The parent is built here, on its own -- the flight case at the EM case's
    V-n point and CG case, assembled without the engine's entered thrust on a
    gyroscopic case (#313) -- and scaled by hand by ``k`` = the pinned load
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
        eng, member = _engine_of(c, project)
        gyro = any(ld.source == "engine-gyro" for ld in c.loads)
        parent = assemble(project, c.label, vn[c.vn_case], loadings[c.cg], cgs[c.cg],
                          thrust_replaced=(member,) if gyro else ())
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
    under a reflection (their position mirrors), and the two restatements of
    the source list are one list."""
    assert tuple(_ROTATION_FIXED_SOURCES) == ROTATION_FIXED_SOURCES
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
