"""Design note 73 (#404): the balance-feasibility owner -- gate G-73.4 and the
stabiliser-type logic of D-73.5.

Every case here is constructed: a tail state is built to sit just inside or just
outside one limit, and exactly that check must fire. The fixture gates (G-73.1 to
G-73.3, G-73.5) run against the shipped airplanes once the families are wired.
"""

import glob
import math
import os
from dataclasses import replace

import pytest

from sloads import io
from sloads.constants import DEG_PER_RAD, TAIL_STALL_ALPHA_DEG, dynamic_pressure_psf
from sloads.feasibility import FLAG_PREFIX, clh_limit, htail_state, is_prescribed, vtail_state
from sloads.models import MissingInputError, TailLoadsInput
from sloads.modules._vtail import lift_curve_slope
from sloads.modules.balance.air import build_balanced_cases
from sloads.modules.balance.queries import FEASIBILITY_FAMILIES, feasibility_family
from sloads.modules.select import default_critical
from sloads.validation import consistency_warnings

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

# Appendix A "General input for calculation of horiz tail loads" (the GA6), as
# tests/test_select.py carries it: stops 30 deg TE-up / 20 deg TE-down.
_TAIL = TailLoadsInput(
    tail_incidence_deg=2.0, wing_zero_lift_cruise_deg=3.988146,
    aspect_ratio_wing=6.095, aspect_ratio_htail=4.017, htail_area_sqft=36.944,
    elevator_effectiveness=0.614, xt25=261.027, xt50=270.357,
    elevator_te_up_deg=30.0, elevator_te_down_deg=20.0, elevator_area_sqft=16.403,
    elevator_fwd_hinge_sqft=1.639, elevator_aft_hinge_sqft=14.792,
    wing_lift_slope_per_rad=4.605,
)
_V = 150.0                                     # kt EAS
_QS = dynamic_pressure_psf(_V) * _TAIL.htail_area_sqft
_A_H = lift_curve_slope(_TAIL.aspect_ratio_htail) / DEG_PER_RAD


def _state(alpha=2.0, cl=0.1, delta=-5.0, ti=_TAIL, **kw):
    """A state at tail angle ``alpha`` (deg), lift coefficient ``cl`` and elevator ``delta``."""
    return htail_state(alpha * _A_H * _QS, cl * _QS, delta, _V, ti, **kw)


def _fired(f):
    return [c.name for c in f.checks if not c.ok]


def test_a_comfortable_state_fires_nothing():
    f = _state()
    assert f.feasible and f.flags == ()
    assert [c.name for c in f.checks] == ["elevator_stop", "tail_alpha", "tail_cl"]


@pytest.mark.parametrize("delta, fires", [
    (-30.0, False), (-30.01, True),            # TE-up stop, on it and past it
    (20.0, False), (20.01, True),              # TE-down stop
])
def test_the_elevator_stop_fires_past_each_stop_and_not_on_it(delta, fires):
    """G-73.4: inclusive at the stop, so the 23.423(a) full-throw cases, built
    exactly on it, stay silent."""
    assert _fired(_state(delta=delta)) == (["elevator_stop"] if fires else [])


@pytest.mark.parametrize("alpha", [TAIL_STALL_ALPHA_DEG + 0.01, -(TAIL_STALL_ALPHA_DEG + 0.01)])
def test_the_tail_alpha_fires_on_both_sides(alpha):
    """G-73.4 with owner ruling Q1: the positive limit mirrors the negative."""
    f = _state(alpha=alpha)
    assert _fired(f) == ["tail_alpha"]
    assert f.flags[0].startswith(FLAG_PREFIX) and "stall" in f.flags[0]
    assert _fired(_state(alpha=math.copysign(TAIL_STALL_ALPHA_DEG, alpha))) == []


def test_the_tail_alpha_is_backed_out_of_the_aoa_load():
    """D-73.2: the angle is LT25/(a_h*q*S_h), so an increment carried in LT25
    (a gust) moves it, whatever trim angle the case publishes."""
    f = _state(alpha=7.25)
    assert math.isclose(next(c.value for c in f.checks if c.name == "tail_alpha"), 7.25, rel_tol=1e-12)


def test_the_tail_cl_fires_past_the_roskam_fixed_cap_on_both_sides():
    cap = 0.35 * _TAIL.aspect_ratio_htail ** (1 / 3)        # Roskam Pt VII p44, 0.556 at A_h 4.017
    assert math.isclose(clh_limit(_TAIL)[0], cap, rel_tol=1e-12)
    assert math.isclose(cap, 0.5559, rel_tol=1e-3)
    for cl in (cap + 1e-3, -(cap + 1e-3)):
        assert _fired(_state(cl=cl)) == ["tail_cl"]
    assert _fired(_state(cl=-cap)) == []


def test_an_entered_clh_max_bypasses_the_default_as_a_magnitude():
    ti = replace(_TAIL, clh_max=-0.9)
    assert clh_limit(ti) == (0.9, "entered")
    assert _fired(_state(cl=0.85, ti=ti)) == []


def test_the_default_cap_follows_the_stabiliser_type():
    travel = dict(stabiliser_incidence_nu_deg=-6.0, stabiliser_incidence_nd_deg=2.0)
    assert clh_limit(replace(_TAIL, stabiliser="A", **travel))[0] == 1.2
    assert clh_limit(replace(_TAIL, stabiliser="m", **travel))[0] == 1.0   # case forgiven


def test_a_movable_stabiliser_without_its_travel_is_refused_by_name():
    with pytest.raises(MissingInputError, match="stabiliser_incidence_nu_deg"):
        _state(ti=replace(_TAIL, stabiliser="A"), trim_delta_deg=-3.0)
    with pytest.raises(ValueError, match="not one of"):
        _state(ti=replace(_TAIL, stabiliser="X"))


def test_an_adjustable_stabiliser_takes_the_trim_and_leaves_the_residual_to_the_elevator():
    """D-73.5: the stabiliser sets IT + tau*delta_trim (within its travel) and the
    elevator check sees only what is left. -34 deg is past the 30 deg stop on a
    fixed tail; with -8 deg of trim taken by the stabiliser it clears."""
    ti = replace(_TAIL, stabiliser="A", stabiliser_incidence_nu_deg=-6.0, stabiliser_incidence_nd_deg=4.0)
    assert _fired(_state(delta=-34.0)) == ["elevator_stop"]                    # fixed
    f = _state(delta=-34.0, ti=ti, trim_delta_deg=-8.0)
    stop = next(c for c in f.checks if c.name == "elevator_stop")
    assert math.isclose(stop.value, -34.0 + 8.0, rel_tol=1e-12) and stop.ok
    # Travel-limited: nu = IT - 1 gives one degree of stabiliser, so most of the
    # trim stays on the elevator and the stop still fires.
    tight = replace(ti, stabiliser_incidence_nu_deg=_TAIL.tail_incidence_deg - 1.0)
    f = _state(delta=-34.0, ti=tight, trim_delta_deg=-8.0)
    stop = next(c for c in f.checks if c.name == "elevator_stop")
    assert math.isclose(stop.value, -34.0 + 1.0 / _TAIL.elevator_effectiveness, rel_tol=1e-12)
    assert not stop.ok and "stabiliser trim" in f.flags[0]


def test_an_all_moving_stabiliser_checks_its_travel_and_no_elevator():
    ti = replace(_TAIL, stabiliser="M", stabiliser_incidence_nu_deg=-15.0, stabiliser_incidence_nd_deg=5.0)
    names = [c.name for c in _state(delta=-5.0, ti=ti).checks]
    assert "elevator_stop" not in names and "stabiliser_travel" in names
    # IT 2 + 0.614*(-30) = -16.4 deg, past the -15 deg nose-up travel. The whole
    # surface turns, so its angle of attack is alpha_eff + tau*delta: +6 - 18.4 =
    # -12.4 deg, inside the stall, so only the travel fires.
    f = _state(delta=-30.0, ti=ti, alpha=6.0)
    assert _fired(f) == ["stabiliser_travel"]
    alpha = next(c.value for c in f.checks if c.name == "tail_alpha")
    assert math.isclose(alpha, 6.0 - 30.0 * _TAIL.elevator_effectiveness, rel_tol=1e-12)


def test_no_elevator_angle_runs_no_authority_check():
    """The 23.423(b) checked manoeuvre publishes no delta (an inertia increment)."""
    names = [c.name for c in _state(delta=None).checks]
    assert names == ["tail_alpha", "tail_cl"]


def test_the_vtail_is_checked_only_against_an_entered_limit():
    """D-73.6, owner ruling Q3: no default; Q4: a prescribed angle says so."""
    assert vtail_state(24.7, None).checks == ()
    f = vtail_state(-19.5, 18.0, prescribed_by="23.441(a)(2)")
    assert _fired(f) == ["vtail_alpha"] and "prescribed by 23.441(a)(2)" in f.flags[0]
    assert vtail_state(18.0, -18.0).feasible



# --------------------------------------------------------------------------- #
# The shipped airplanes (G-73.1 ... G-73.3, G-73.5, G-73.6), measured 2026-11-02
# --------------------------------------------------------------------------- #
def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _flags(project):
    """``{label: [flag, ...]}`` of the flagged critical conditions."""
    return {f"{c.component} {c.label}": c.feasibility
            for c in default_critical(project).conditions if c.feasibility}


def _value(flag):
    """The first signed number in a flag sentence (the state it judged)."""
    return float(flag.split(" past ")[0].split()[-2])


def test_the_oracle_airplane_flags_only_what_the_regulation_prescribes():
    """G-73.1: on ``ga6_normal`` every flag is on a 23.423(a) full throw (or the
    23.427(a) case distributing one), and no warning is raised. The Appendix A
    figures are the oracle tests', unchanged."""
    flags = _flags(_project("ga6_normal"))
    assert sorted(flags) == ["htail UNCHECKED MAN DN", "htail UNCHECKED MAN UP", "htail UNSYMMETRICAL"]
    assert all(is_prescribed(f) and "23.423(a)" in f for fs in flags.values() for f in fs)
    assert not [w for w in consistency_warnings(_project("ga6_normal")) if w.code == "balance_infeasible"]


@pytest.mark.parametrize("name, delta", [("atr42_100", -27.90), ("atr42_300_seed", -27.54)])
def test_the_atr_flags_its_balancing_elevator_past_the_stop(name, delta):
    """G-73.2, review A-2: the 23.421 down balancing load runs the elevator past
    the 25 deg TE-up stop. The delivered wing cases sit at the aft-CG mass state
    (note 63) and inside the stops, so they carry no flag."""
    flags = {k: [f for f in v if not is_prescribed(f)] for k, v in _flags(_project(name)).items()}
    flags = {k: v for k, v in flags.items() if v}
    assert list(flags) == ["htail BAL DN RETRACTED"]
    (flag,) = flags["htail BAL DN RETRACTED"]
    assert "TE-up stop" in flag and _value(flag) == pytest.approx(delta, abs=0.005)
    codes = [w.code for w in consistency_warnings(_project(name))]
    assert codes.count("balance_infeasible") == 1


def test_the_regional_jet_flags_its_stall_line_cases():
    """G-73.3: stop and tail-alpha flags on the stall-line wing cases and the up
    balancing load; the balanced cases built from them carry the flags."""
    flags = _flags(_project("concept_regional_jet"))
    want = {"wing PHAA": [-34.68, 18.52], "wing ACRL": [-29.47, 15.45], "wing NHAA": [23.72],
            "htail BAL UP RETRACTED": [-25.79, 17.40]}
    for key, values in want.items():
        assert [_value(f) for f in flags[key]] == pytest.approx(values, abs=0.005), key
    cases = build_balanced_cases(_project("concept_regional_jet"))
    flagged = sorted({(c.label, c.hand) for c in cases if any(n.startswith(FLAG_PREFIX) for n in c.notes)})
    assert flagged == [("ACRL", "L"), ("ACRL", "R"), ("NHAA", ""), ("PHAA", ""),
                       ("UNSYMMETRICAL", "L"), ("UNSYMMETRICAL", "R")]


def test_a_movable_stabiliser_clears_the_atr_balancing_case_only_with_travel():
    """G-73.5: as an adjustable stabiliser with 6 deg of nose-up travel the ATR's
    -27.9 deg is inside the stop once the stabiliser takes the 1 g trim; with no
    travel beyond its incidence the flag stays. All-moving drops the elevator."""
    def bal_dn(stab, nu, nd):
        project = _project("atr42_100")
        project.tail_loads = replace(project.tail_loads, stabiliser=stab,
                                     stabiliser_incidence_nu_deg=nu, stabiliser_incidence_nd_deg=nd)
        return next(c for c in default_critical(project).conditions if c.label == "BAL DN RETRACTED")

    assert bal_dn("A", -6.0, 2.0).feasibility == []
    (flag,) = bal_dn("A", -1.0, 2.0).feasibility        # nu = IT: no nose-up travel
    assert "TE-up stop after" in flag
    assert bal_dn("M", -20.0, 5.0).feasibility == []


@pytest.mark.parametrize("path", sorted(glob.glob(os.path.join(_EXAMPLES, "*.project.json"))),
                         ids=os.path.basename)
def test_every_balanced_case_is_in_a_feasibility_family_and_carries_its_flags(path):
    """G-73.6, the drift guard (D-73.10): every assembled case is claimed by one
    family row, and every case of a checked family carries exactly the flags of
    the SELECT condition it was built from (the twin included)."""
    project = io.load_project(path)
    by_label = {c.label: c.feasibility for c in default_critical(project).conditions
                if c.component in ("wing", "htail", "vtail")}
    for case in build_balanced_cases(project):
        family, standing = feasibility_family(case)
        flags = [n for n in case.notes if n.startswith(FLAG_PREFIX)]
        if standing.startswith("checked"):
            assert flags == list(by_label.get(case.label, [])), (case.label, case.hand)
        else:
            assert flags == [], (family, case.label)
    assert {row[0] for row in FEASIBILITY_FAMILIES} == {
        "ground", "engine mount", "engine out", "unsymmetrical h-tail", "lateral fin", "wing"}


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
