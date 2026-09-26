"""The one-engine-out fin in the assembled deck (design note 66, #285): G-66.8-16.

ONENGOUT's peak instant, assembled quasi-statically on a 1 g parent with the
live-thrust / windmill-drag pair; one engine's failure computed per speed and
the mirrored engine's as its reflected twin under its own id.
"""

import math
import os
import sys

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


@pytest.mark.parametrize("name", _TWINS)
def test_each_twin_is_the_other_engines_own_condition(name):
    """**G-66.10** (D-66.13): the reflected twin carries the mirrored engine's
    own fin load -- the reflection reproduces the march it stands for."""
    project, cases, _ = _built(name)
    crit = {x.label: x for x in default_critical(project).conditions if x.component == "vtail"}
    for c in _oei(cases):
        cond = crit[c.label]
        fy = math.fsum(ld.fy for ld in c.loads if ld.source == "vtail-air")
        assert fy == pytest.approx(cond.lt25 + cond.lt50, rel=1e-9), c.label
        assert c.case_ref.case_id == cond.case_ref.case_id


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
