"""The one-engine-out fin in the assembled deck (design note 66, #285): G-66.8-16.

ONENGOUT's peak instant, assembled quasi-statically on a 1 g parent with the
live-thrust / windmill-drag pair; one engine's failure computed per speed and
the mirrored engine's as its reflected twin under its own id.
"""

import math
import os
import sys
from dataclasses import replace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.constants import LBIN2_PER_SLUGFT2
from sloads.modules.balance import (
    RESIDUAL_GATE,
    build_balanced_cases,
    is_engine_out,
    residual_gate_applies,
)
from sloads.modules.balance.closure import resultant6
from sloads.modules.balance.engine_out_cases import OEI_L7_NOTE, OEI_PARENT
from sloads.modules.one_engine_out import _moment, engine_forces_at, engine_thrust_and_drag, vtail_cases
from sloads.modules.select import default_critical
from sloads.rigid_body import radians_per_s2

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_TWINS = ("atr42_100", "baron_58")

#: G-66.8, measured: (computed id, twin id) per assembled speed. The ATR's VS
#: march does not recover on either engine (OR-174); the Baron's does.
_EXPECTED = {
    "atr42_100": [("VT-30", "VT-33"), ("VT-31", "VT-34")],
    "baron_58": [("VT-30", "VT-33"), ("VT-31", "VT-34"), ("VT-32", "VT-35")],
}

#: G-66.9's band: the closure yaw (on the assembled tensor, about the loading's
#: own CG) against ONENGOUT's (on WTONECG's Izz, about its heaviest mass case's
#: CG), after the Izz ratio. Measured 2.1 / 2.0 % (ATR VC / VD) and 2.8 / 2.9 /
#: 3.2 % (Baron): the CG arm (404.1 vs 401.2 in on the ATR) and the coupled
#: tensor's Ixz, which a single-DOF march does not have.
_YAW_BAND = 0.05


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _built(name):
    project = _project(name)
    skipped = []
    return project, build_balanced_cases(project, skipped), skipped


def _oei(cases):
    return [c for c in cases if is_engine_out(c)]


def _marches(project):
    return {f"ONE ENGINE OUT — {f.load_case.label}{f.engine_label}": f for f in vtail_cases(project)}


@pytest.mark.parametrize("name", _TWINS)
def test_each_speed_is_one_computed_case_and_its_twin(name):
    """**G-66.8**: per recovered speed, the first engine's failure is computed
    and the mirrored engine's is its reflected twin under its own id."""
    _, cases, _ = _built(name)
    ids = [c.case_ref.case_id for c in _oei(cases)]
    assert ids == [i for pair in _EXPECTED[name] for i in pair]


def test_an_airplane_without_a_failure_case_has_none():
    for name in ("ga6_normal", "concept_heavy"):
        _, cases, _ = _built(name)
        assert not _oei(cases), name


@pytest.mark.parametrize("name", _TWINS)
def test_the_closure_yaw_is_onengouts(name):
    """**G-66.9** (D-66.12): with the engine pair beside the fin, the closure's
    yaw acceleration is ONENGOUT's at the peak -- fin moment less engine moment
    -- after the Izz ratio, inside :data:`_YAW_BAND`, and with its sign."""
    project, cases, _ = _built(name)
    marches = _marches(project)
    for c in _oei(cases):
        if c.label not in marches:
            continue            # a twin, checked through its computed case
        fc = marches[c.label]
        closure = math.degrees(radians_per_s2((0.0, 0.0, c.r_dot))[2])
        izz = c.closure_inertia.izz / LBIN2_PER_SLUGFT2
        scaled = closure * izz / fc.inputs.izz
        march = -fc.sense * fc.peak.theta_2dot        # airplane axes, nose sense
        assert math.copysign(1.0, scaled) == math.copysign(1.0, march), c.label
        assert abs(scaled - march) <= _YAW_BAND * abs(march), (c.label, scaled, march)


@pytest.mark.parametrize("name", _TWINS)
def test_the_fin_opposes_the_engine(name):
    """The sign D-66.12 turned up: the fin's yawing moment opposes the engine
    pair's, and a positive yaw angle (nose left, SELECT's convention) carries a
    negative fin load, as SELECT's static fin conditions do."""
    project, cases, _ = _built(name)
    for c in _oei(cases):
        ref = (c.cg_x, 0.0, c.cg_z)
        fin = resultant6([ld for ld in c.loads if ld.source == "vtail-air"], ref)
        pair = resultant6([ld for ld in c.loads if ld.source.startswith("engine-out-")], ref)
        assert fin[5] * pair[5] < 0, c.label
    crit = {x.label: x for x in default_critical(project).conditions if x.component == "vtail"}
    for label, cond in crit.items():
        if label.startswith("ONE ENGINE OUT") and cond.beta_deg:
            assert cond.beta_deg * cond.lt25 < 0, label


def _load_key(ld):
    return (ld.source, round(ld.x, 6), round(ld.y, 6), round(ld.z, 6))


@pytest.mark.parametrize("name", _TWINS)
def test_each_twin_is_the_other_engines_own_condition(name, monkeypatch):
    """**G-66.10** (D-66.13): the reflected twin reproduces the mirrored
    engine's own condition, load for load at rel 1e-9 -- fin strips, engine
    pair, relief -- against that engine's case **built directly** from its own
    ONENGOUT march with the reflection switched off, and its engine pair is
    ``engine_forces_at`` of that march at that engine's hub. Before #318 the
    gate compared one sum (the fin's ``fy``) and the id."""
    from sloads.modules.balance import engine_out_cases
    from sloads.modules.balance.engine_out_cases import (
        OEI_FAILED_ENGINE_SOURCE,
        OEI_LIVE_THRUST_SOURCE,
    )
    from sloads.modules.engine import resolved_engines

    project, cases, _ = _built(name)
    crit = {x.label: x for x in default_critical(project).conditions if x.component == "vtail"}
    computed = {c.label for c in _oei(cases)[::2]}
    twins = [c for c in _oei(cases) if c.label not in computed]
    assert twins, "no reflected twin: the gate proves nothing"
    monkeypatch.setattr(engine_out_cases, "_mirror_of", lambda *_a, **_kw: None)
    direct = {c.label: c for c in _oei(build_balanced_cases(_project(name)))}
    marches = _marches(project)
    for twin in twins:
        own = direct[twin.label]
        assert twin.case_ref.case_id == own.case_ref.case_id == crit[twin.label].case_ref.case_id
        assert twin.hand == own.hand
        got, want = sorted(twin.loads, key=_load_key), sorted(own.loads, key=_load_key)
        assert [_load_key(ld) for ld in got] == [_load_key(ld) for ld in want], twin.label
        for a, b in zip(got, want, strict=True):
            for q in ("fx", "fy", "fz", "mx", "my", "mz"):
                assert getattr(a, q) == pytest.approx(getattr(b, q), rel=1e-9, abs=1e-9), \
                    (twin.label, a.source, q)
        for q in ("p_dot", "q_dot", "r_dot", "delta_ny"):
            assert getattr(twin, q) == pytest.approx(getattr(own, q), rel=1e-9, abs=1e-12), q
        fc = marches[twin.label]
        eng = resolved_engines(project)[fc.engine_index]
        hub = eng.prop_cg if any(eng.prop_cg) else eng.engine_cg
        live, remaining, windmill = engine_forces_at(fc.peak.time, fc.inputs)
        pair = {ld.source: ld for ld in twin.loads
                if ld.source in (OEI_LIVE_THRUST_SOURCE, OEI_FAILED_ENGINE_SOURCE)}
        failed, alive = pair[OEI_FAILED_ENGINE_SOURCE], pair[OEI_LIVE_THRUST_SOURCE]
        assert (failed.y, alive.y) == pytest.approx((hub[1], -hub[1]))
        assert failed.fx == pytest.approx(-remaining + windmill, rel=1e-9)
        assert alive.fx == pytest.approx(-live, rel=1e-9)


def test_an_unrecovered_march_is_recorded():
    """**G-66.11**: the ATR's VS march does not recover (OR-174); it is never a
    SELECT condition, and the record names it for the deck."""
    _, _, skipped = _built("atr42_100")
    recorded = [s.label for s in skipped if s.code == "not-recovered"]
    assert recorded == ["ONE ENGINE OUT — VS (engine 1)", "ONE ENGINE OUT — VS (engine 2)"]


@pytest.mark.parametrize("name", _TWINS)
def test_the_ultimate_cases_state_one(name):
    """**G-66.14** (D-66.1): 23.367(a)(2) is already ultimate -- SF 1.0 -- and
    every other one-engine-out case 1.5."""
    _, cases, _ = _built(name)
    for c in _oei(cases):
        want = 1.0 if c.case_ref.far_reference == "23.367(a)(2)" else 1.5
        assert c.safety_factor == want, c.label


@pytest.mark.parametrize("name", _TWINS)
def test_no_l7_term_and_the_case_says_so(name):
    """**G-66.15** (D-66.15): no body side force is applied, and the case
    states why."""
    _, cases, _ = _built(name)
    for c in _oei(cases):
        assert not [ld for ld in c.loads if ld.source == "body-aero"], c.label
        assert OEI_L7_NOTE in c.notes, c.label


@pytest.mark.parametrize("name", _TWINS)
def test_the_one_g_half_closes_inside_the_gate(name):
    """**G-66.16**: take the fin, the engine pair and the relief away and the 1 g
    parent closes inside :data:`RESIDUAL_GATE`; the pitch residual the case
    reports is the pair's own couple in full, hence its exemption."""
    _, cases, _ = _built(name)
    for c in _oei(cases):
        assert not residual_gate_applies(c)
        half = [ld for ld in c.loads if ld.source != "vtail-air"
                and not ld.source.startswith(("engine-out-", "closure"))]
        fx, fy, fz, mx, my, mz = resultant6(half, (c.cg_x, 0.0, c.cg_z))
        n_w = c.nz * c.weight_lb
        assert abs(fz) / n_w < RESIDUAL_GATE, c.label
        assert abs(my) / (n_w * c.mac) < RESIDUAL_GATE, c.label
        assert c.vn_case and c.label[len("ONE ENGINE OUT — "):][:2] in OEI_PARENT


@pytest.mark.parametrize("name", _TWINS)
def test_the_engine_schedule_is_the_marchs(name):
    """``engine_forces_at`` is the schedule ``_moment`` builds its engine term
    from, at every instant of every march: ``(live - remaining + drag) * arm``."""
    project = _project(name)
    for fc in vtail_cases(project):
        c = fc.inputs
        thrust, drag, _ = engine_thrust_and_drag(c)
        for t in (0.0, 0.5 * c.time2decay, c.time2decay,
                  0.5 * (c.time2decay + c.time2drag), c.time2drag, fc.peak.time):
            live, remaining, windmill = engine_forces_at(t, c)
            want = _moment(t, c, thrust * c.bleng, drag * c.bleng, 0.0, 0.0)
            assert (live - remaining + windmill) * c.bleng == pytest.approx(want, abs=1e-6)


def _with_cd(project, cds):
    """``project`` with ``windmill_drag_cd`` entered per engine (``None`` keeps
    the bound)."""
    return replace(project, engines=[replace(e, windmill_drag_cd=cd)
                                     for e, cd in zip(project.engines, cds, strict=True)])


def _pair(case):
    from sloads.modules.balance.engine_out_cases import OEI_FAILED_ENGINE_SOURCE
    return next(ld for ld in case.loads if ld.source == OEI_FAILED_ENGINE_SOURCE)


@pytest.mark.parametrize("name", _TWINS)
def test_an_entered_windmill_coefficient_is_delivered_and_the_bound_otherwise(name):
    """**D-66.12a** (#319): blank, the failed hub carries ONENGOUT's Glauert
    drag and the case states it as the method's upper bound (C_D,disc 0.50,
    manual Ch 11 p88); entered, it carries ``C_D * q * pi D^2 / 4`` on the same
    ramp, stated as the entered coefficient. The fin load is the march's either
    way, so no ``vtail-air`` load moves."""
    from sloads.modules.one_engine_out import disc_drag_coefficient

    project = _project(name)
    bound = {c.label: c for c in _oei(build_balanced_cases(project))}
    entered = {c.label: c for c in _oei(build_balanced_cases(_with_cd(project, [0.25, 0.25])))}
    marches = _marches(project)
    assert bound.keys() == entered.keys()
    for label, b in bound.items():
        e = entered[label]
        assert any("upper bound" in n and "0.50" in n and "can not be more than" in n
                   for n in b.notes), label
        assert any("entered disc drag coefficient 0.25" in n for n in e.notes), label
        fc = marches.get(label)
        if fc is not None:
            live, remaining, windmill = engine_forces_at(fc.peak.time, fc.inputs)
            full = engine_thrust_and_drag(fc.inputs)[1]
            assert disc_drag_coefficient(fc.inputs, full) == pytest.approx(0.502, abs=5e-4)
            assert _pair(b).fx == pytest.approx(-remaining + windmill, rel=1e-12)
            assert _pair(e).fx == pytest.approx(-remaining + windmill * 0.25
                                                / disc_drag_coefficient(fc.inputs, full),
                                                rel=1e-9)
        fin_b = [ld for ld in b.loads if ld.source == "vtail-air"]
        fin_e = [ld for ld in e.loads if ld.source == "vtail-air"]
        assert [(ld.fy, ld.y) for ld in fin_b] == [(ld.fy, ld.y) for ld in fin_e], label


@pytest.mark.parametrize("name", _TWINS)
def test_an_entered_coefficient_moves_the_closure_yaw_by_its_own_moment(name):
    """**G-66.9** as amended (#319, D-66.12a): with the bound the closure's yaw
    is ONENGOUT's (above); with an entered coefficient it differs by exactly the
    drag difference's moment through the case's own inertia tensor --
    ``[I]{delta omega_dot} = delta M`` about the CG -- and by nothing else."""
    project = _project(name)
    bound = {c.label: c for c in _oei(build_balanced_cases(project))}
    entered = {c.label: c for c in _oei(build_balanced_cases(_with_cd(project, [0.25, 0.25])))}
    for label, b in bound.items():
        e = entered[label]
        ref = (b.cg_x, 0.0, b.cg_z)
        dm = [x - y for x, y in zip(resultant6([_pair(e)], ref)[3:],
                                    resultant6([_pair(b)], ref)[3:], strict=True)]
        dw = (e.p_dot - b.p_dot, e.q_dot - b.q_dot, e.r_dot - b.r_dot)
        got = [math.fsum(row[i] * dw[i] for i in range(3)) for row in b.closure_inertia.matrix()]
        scale = max(abs(v) for v in dm)
        assert scale > 0, label
        for g, want in zip(got, dm, strict=True):
            assert g == pytest.approx(want, abs=1e-3 * scale), label


def test_a_twin_needs_both_engines_to_windmill_alike():
    """D-66.12a: the twin reflects the failed hub's drag, so it stands only when
    both engines enter the same coefficient; otherwise the mirrored engine's
    failure is computed on its own, with its own (here, the bound's) drag."""
    project = _with_cd(_project("baron_58"), [0.25, None])
    cases = _oei(build_balanced_cases(project))
    marches = _marches(project)
    assert {c.label for c in cases} == set(marches)     # the Baron recovers at every speed
    for c in cases:
        fc = marches[c.label]
        live, remaining, windmill = engine_forces_at(
            fc.peak.time, fc.inputs, windmill_cd=project.engines[fc.engine_index].windmill_drag_cd)
        assert _pair(c).fx == pytest.approx(-remaining + windmill, rel=1e-9), c.label


def test_a_hub_off_the_engines_butt_line_is_recorded():
    """#321 (note 66 §12 riders): the march's arm is the engine's butt line and
    the pair lands at the hub, so a hub off that line is recorded by name
    instead of carrying a yaw the fin load was never found against."""
    project = _project("baron_58")
    eng = project.engines[0]
    x, y, z = eng.prop_cg
    moved = replace(project, engines=[replace(eng, prop_cg=(x, y + 3.0, z)), project.engines[1]])
    skipped = []
    cases = _oei(build_balanced_cases(moved, skipped))
    off = [s for s in skipped if s.code == "hub-off-arm"]
    assert off and all("(engine 1)" in s.label for s in off)
    assert all("(engine 1)" not in c.label or c.hand for c in cases)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
