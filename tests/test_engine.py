"""Validate the calculation core against the FAR 23 LOADS manual appendices.

The reciprocating reference is the Continental IO-520-BB example printed in the
manual (full.txt:24910-25028). The comparison values below are the manual's
*printed* figures; per Decision 3 ("modernize the math", pi -> math.pi) they are
matched with an engineering tolerance of ±0.1% (rel_tol=1e-3) rather than exact
equality, so genuine drift still fails loudly while the pi modernization does not.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixtures import io520bb, turboprop
from helpers import value_of

from sloads import run_all
from sloads.basic import basic_int
from sloads.modules import engine as calc

# Engineering tolerance for matching the manual's printed figures (see Decision 3).
TOL = 1e-3  # ±0.1% relative


def test_derived_quantities():
    inp = io520bb()
    assert calc.combined_weight(inp) == 579  # integers, pi-independent
    assert math.isclose(calc.takeoff_torque(inp), 554.3884, rel_tol=TOL)
    assert math.isclose(calc.max_cont_torque(inp), 556.7227, rel_tol=TOL)
    assert calc.torque_factor(inp) == 1.33
    # The printed combined CG, all three components (p227 "APPLIED AT X,Y,Z").
    # ``zpp`` went unasserted until 2026-09-07 and both entered waterlines were
    # wrong under it (note 44 §20, OR-170), so it is asserted here as well.
    xpp, ypp, zpp = calc.combined_cg(inp)
    assert math.isclose(xpp, 17.91, abs_tol=0.01)
    assert math.isclose(ypp, 0.0, abs_tol=1e-9)
    assert math.isclose(zpp, 93.022, abs_tol=0.01)


def test_361_a1():
    # Approved correction (AC 23-19A): 23.361(c) applies the mean-torque factor to
    # the takeoff case too (1.33 for the 6-cyl IO-520-BB). The manual's printed p131
    # figure is the pre-Amdt-45 UNFACTORED value (554.3884, asserted below as the
    # mean torque); the corrected design torque is 1.33 x 554.3884 = 737.34 ft-lb.
    # Vertical loads are unchanged. See CLAUDE.md "Approved corrections to the source".
    r = calc.condition_361_a1(io520bb())
    assert math.isclose(value_of(r, "vertical_load_factor"), 2.85, abs_tol=1e-9)
    assert math.isclose(value_of(r, "fz_vertical"), 1650.15, rel_tol=TOL)
    assert math.isclose(value_of(r, "torque_factor"), 1.33, abs_tol=1e-9)
    assert math.isclose(value_of(r, "mean_takeoff_torque"), 554.3884, rel_tol=TOL)
    assert math.isclose(value_of(r, "mx_mount_torque"), -737.337, rel_tol=TOL)


def test_361_a2():
    r = calc.condition_361_a2(io520bb())
    assert math.isclose(value_of(r, "fz_vertical"), 2200.2, rel_tol=TOL)
    assert math.isclose(value_of(r, "torque_factor"), 1.33, abs_tol=1e-9)
    assert math.isclose(value_of(r, "max_continuous_torque"), 556.7227, rel_tol=TOL)
    assert math.isclose(value_of(r, "mx_mount_torque"), -740.4412, rel_tol=TOL)


def test_363():
    r = calc.condition_363(io520bb())
    assert math.isclose(value_of(r, "side_load_factor"), 1.33, abs_tol=1e-9)
    assert math.isclose(value_of(r, "fy_side"), 770.07, rel_tol=TOL)


def test_reciprocating_runs_three_conditions():
    assert len(run_all(io520bb())) == 3


def test_prop_inertia_matches_manual():
    # Manual hand calc: IProp = 50/32.174*(50.5/12)^2/3 = 9.174 slug-ft^2
    inp = turboprop()
    assert math.isclose(calc._prop_inertia(inp), 9.174, abs_tol=1e-2)


# --------------------------------------------------------------------------- #
# 23.361(b)(1) sudden stoppage -- formula-closure gate (CR-B-3).
#
# Twin-only condition: Appendix B is not bundled, so there is no printed figure
# to lock (CONVENTIONS.md §6 -- "no oracle" never means "no gate"). The gate is
# the formula ENGLOADS.BAS lines 850-926 evaluate, restated here from the
# rotor-by-rotor inputs rather than from the module's own summation, so a
# regression in the loop, in a rotor's sign, or in the Delta-t division fails.
# --------------------------------------------------------------------------- #

def test_361_b1_closes_on_the_angular_momentum_formula():
    """torque == I_prop*omega_prop/dt + SUM_i I_rotor(i)*omega_rotor(i)/dt.

    Independently re-derived from the fixture's own numbers (ENGLOADS.BAS 853-926,
    reference/FAR23Loads_Code.pdf p466). Rotor 1 spins counter-clockwise
    (max_rpm < 0), so its contribution *subtracts*: this pins the signed summation,
    not just its magnitude.
    """
    inp = turboprop()
    dt = inp.stop_time_s
    expected = calc._prop_inertia(inp) * calc._omega(inp.takeoff_rpm) / dt
    contributions = [calc._rotor_inertia(r) * calc._omega(r.max_rpm) / dt for r in inp.rotors]
    expected += sum(contributions)
    assert min(contributions) < 0 < max(contributions)  # the counter-rotating pair

    r = calc.condition_361_b1(inp)
    assert value_of(r, "time_to_stop") == dt
    assert math.isclose(value_of(r, "ixx_propeller"), calc._prop_inertia(inp), abs_tol=1e-9)
    # Reported torque is the negated total, floored (see the truncation test below).
    assert math.isclose(value_of(r, "mx_mount_torque"), -expected, abs_tol=1.0)
    assert math.isclose(expected, 6824.62, rel_tol=TOL)  # today's value, pinned


def test_361_b1_torque_is_floored_as_basic_int_did():
    """``INT(-TORQSUDSTOP)`` floors; Python's ``int()`` truncates toward zero.

    ENGLOADS.BAS line 944 prints ``INT(-TORQSUDSTOP)`` and the argument is negative
    by construction (reaction torque is reported negative, CONVENTIONS.md §5), so
    the two differ by exactly 1 ft-lb -- and ``int()`` was the non-conservative
    one. -6824.624... floors to -6825, truncates to -6824.
    """
    r = calc.condition_361_b1(turboprop())
    assert value_of(r, "mx_mount_torque") == -6825.0
    assert value_of(r, "mx_mount_torque") == basic_int(-6824.624095864674)
    assert int(-6824.624095864674) == -6824  # what the port used to report


# --------------------------------------------------------------------------- #
# #332 -- one spin-sign owner for the stoppage torque
# --------------------------------------------------------------------------- #
def _mirrored(inp):
    """The same engine turning the other way: propeller and every rotor."""
    from dataclasses import replace

    from sloads.models.enums import RotorDirection
    flip = (RotorDirection.COUNTERCLOCKWISE
            if inp.prop_direction is RotorDirection.CLOCKWISE else RotorDirection.CLOCKWISE)
    return replace(inp, prop_direction=flip,
                   rotors=[replace(r, max_rpm=-r.max_rpm) for r in inp.rotors])


def _stoppages(inp):
    return {c.far_reference: value_of(c, "mx_mount_torque")
            for c in (calc.condition_361_b1(inp), calc.condition_25_361_a3i(inp))}


def test_a_mirrored_engine_publishes_the_exact_negative_stoppage():
    """#332 gate. A mirrored engine publishes its twin's stoppage torque
    negated, to the pound-foot, on both the 23.361(b)(1) and 25.361(a)(3)(i)
    cases: the floor is taken on the magnitude, the sign read from the shed
    momentum. Before #332 the RJ's fans published -50,577 / +50,576, and an
    ATR-42 engine mirrored lost 29 % of its torque (+17,333 against 24,473)."""
    from sloads import io
    examples = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "examples")
    from sloads.modules.engine import resolved_engines

    # Through the resolver: the fixtures' engine and propeller weights derive
    # from their weight rows since v80 (design note 71 D-71.3).
    atr = resolved_engines(io.load_project(os.path.join(examples, "atr42_100.project.json")))[0]
    rj = resolved_engines(io.load_project(os.path.join(examples, "concept_regional_jet.project.json")))
    for engine in (turboprop(), atr):
        a, b = _stoppages(engine), _stoppages(_mirrored(engine))
        for far, value in a.items():
            assert b[far] == -value, far
    assert _stoppages(atr)["23.361(b)(1)"] == -24473.0  # unchanged by #332
    left, right = (_stoppages(e)["23.361(b)(1)"] for e in rj)
    assert (left, right) == (-50577.0, 50577.0)


def test_the_stoppage_signs_the_propeller_as_the_gyro_does():
    """#332 gate. A clockwise propeller and a clockwise rotor shed momentum the
    same way, so their torques add; reversing the propeller alone subtracts it.
    The stoppage total is the signed spin momentum at take-off rpm over the
    stop time -- the owner the gyroscopic conditions read at max-continuous."""
    from dataclasses import replace

    from sloads.models.enums import RotorDirection
    base = turboprop()
    dt = base.stop_time_s
    prop = calc._prop_inertia(base) * calc._omega(base.takeoff_rpm) / dt
    rotors = sum(calc._rotor_inertia(r) * calc._omega(r.max_rpm) / dt for r in base.rotors)
    ccw_prop = replace(base, prop_direction=RotorDirection.COUNTERCLOCKWISE)
    torque, _ = calc._stoppage_torque(ccw_prop)
    assert math.isclose(torque, -prop + rotors, rel_tol=1e-12)
    assert math.isclose(torque * dt, calc.spin_momentum(ccw_prop, base.takeoff_rpm),
                        rel_tol=1e-12)
    assert math.isclose(calc.angular_momentum(ccw_prop),
                        calc.spin_momentum(ccw_prop, base.max_cont_rpm), rel_tol=1e-12)


def test_a_rotors_spin_sense_has_one_reader():
    """#332 drift guard. ``Rotor`` carries no direction field (the signed
    ``max_rpm`` is the one owner), and inside the engine module a rotor's rpm
    is read only by ``spin_momentum`` -- so the stoppage and the gyro cannot
    drift onto two readings of the spin again."""
    import ast
    import dataclasses
    import inspect

    from sloads.models.inputs import Rotor
    assert "direction" not in {f.name for f in dataclasses.fields(Rotor)}
    tree = ast.parse(inspect.getsource(calc))
    readers = {fn.name for fn in ast.walk(tree) if isinstance(fn, ast.FunctionDef)
               for node in ast.walk(fn)
               if isinstance(node, ast.Attribute) and node.attr == "max_rpm"}
    assert readers == {"spin_momentum"}, readers


# --------------------------------------------------------------------------- #
# #343 sweep -- an entered engine magnitude is refused by name unless positive
# --------------------------------------------------------------------------- #
def test_an_entered_engine_magnitude_must_be_positive():
    """#343 sweep (rule 4, the windmill coefficient's class). Each of these is a
    magnitude the engine's convention signs (``torque_sense``,
    ``spin_momentum``): a negative entry reversed a delivered mount load as
    cleanly as a right one closes, and a zero stoppage time divided by zero.
    Each is refused by name -- through ``_required`` for the fields a condition
    needs, ``_positive`` for the two entered overrides."""
    import re
    from dataclasses import replace

    cases = [("stop_time_s", calc.condition_361_b1, turboprop),
             ("max_engine_torque", calc.condition_361_a3, turboprop),
             ("cruise_torque", calc.condition_361_a2, turboprop),
             ("max_accel_torque", calc.condition_25_361_a3ii, turboprop),
             ("takeoff_hp", calc.condition_361_a1, io520bb)]
    for field, condition, make in cases:
        condition(make())                                  # the entered value runs
        for bad in (0.0, -1.0):
            try:
                condition(replace(make(), **{field: bad}))
            except ValueError as err:
                assert re.search(rf"EngineInput\.{field} is .*must be positive", str(err)), err
            else:
                raise AssertionError(f"{field}={bad} was not refused")
    # A measured propeller inertia is refused only below zero: 0 is a fan with
    # no propeller (the regional jet enters it so).
    calc.condition_361_b1(replace(turboprop(), prop_inertia=0.0))
    try:
        calc.condition_361_b1(replace(turboprop(), prop_inertia=-1.0))
    except ValueError as err:
        assert "prop_inertia is -1.000: it is a magnitude and must be zero or positive" in str(err), err
    else:
        raise AssertionError("prop_inertia=-1 was not refused")



def test_the_rpm_weight_and_diameter_reads_are_refused_by_name():
    """#364, the #343 sweep finished. A negative rpm reversed the stoppage
    torque and the gyroscopic couples -- a second spin-sign owner beside
    ``prop_direction`` (the #332 class) -- and a zero one divided by zero in
    ``torque_from_hp``; a negative weight reversed the inertia load, and a hub
    heavier than its propeller gave the blades a negative inertia. Zero stays
    admissible wherever it means *none* (the regional jet's fans enter no
    propeller), except where the rpm divides."""
    import re
    from dataclasses import replace

    def refused(condition, inp, pattern):
        try:
            condition(inp)
        except ValueError as err:
            assert re.search(pattern, str(err)), err
        else:
            raise AssertionError(f"{pattern!r} was not refused")

    # Where the rpm divides (reciprocating torque from hp), zero is refused too.
    for field, condition in (("takeoff_rpm", calc.condition_361_a1),
                             ("max_cont_rpm", calc.condition_361_a2)):
        for bad in (0.0, -1.0):
            refused(condition, replace(io520bb(), **{field: bad}),
                    rf"EngineInput\.{field} is .*must be positive")
    # Elsewhere a magnitude is refused only below zero.
    tp = turboprop()
    rotor = tp.rotors[0]
    cases = [(calc.condition_361_b1, replace(tp, takeoff_rpm=-1.0), "takeoff_rpm"),
             (calc.condition_371_b, replace(tp, max_cont_rpm=-1.0), "max_cont_rpm"),
             (calc.condition_25_371, replace(tp, max_cont_rpm=-1.0), "max_cont_rpm"),
             (calc.condition_361_a3, replace(tp, prop_weight_lb=-1.0), "prop_weight_lb"),
             (calc.condition_361_a3, replace(tp, engine_weight_lb=-1.0), "engine_weight_lb"),
             (calc.condition_361_b1, replace(tp, hub_weight_lb=-1.0), "hub_weight_lb"),
             (calc.condition_361_b1, replace(tp, prop_diameter_in=-1.0), "prop_diameter_in"),
             (calc.condition_361_b1, replace(tp, rotors=[replace(rotor, weight_lb=-1.0)]),
              r"rotors\[\]\.weight_lb"),
             (calc.condition_361_b1, replace(tp, rotors=[replace(rotor, diameter_in=-1.0)]),
              r"rotors\[\]\.diameter_in"),
             (calc.condition_361_b1, replace(tp, rotors=[replace(rotor, inertia=-1.0)]),
              r"rotors\[\]\.inertia")]
    for condition, inp, field in cases:
        refused(condition, inp, rf"EngineInput\.{field} is .*must be zero or positive")
    refused(calc.condition_361_b1, replace(tp, hub_weight_lb=tp.prop_weight_lb + 1.0),
            r"hub_weight_lb .* exceeds prop_weight_lb")
    # A fan with no propeller: every prop magnitude zero, and it still runs.
    calc.condition_361_b1(replace(tp, takeoff_rpm=0.0, max_cont_rpm=0.0, prop_weight_lb=0.0,
                                  hub_weight_lb=0.0, prop_diameter_in=0.0))
    calc.condition_371_b(replace(tp, max_cont_rpm=0.0))

def test_measured_prop_inertia_overrides_geometry():
    from dataclasses import replace
    inp = replace(turboprop(), prop_inertia=12.5)
    assert calc._prop_inertia(inp) == 12.5  # geometry (9.174) ignored


def test_measured_rotor_inertia_overrides_geometry():
    from dataclasses import replace
    base = turboprop()
    geom = calc._rotor_inertia(base.rotors[0])
    measured = replace(base.rotors[0], inertia=0.5)
    assert calc._rotor_inertia(measured) == 0.5
    assert not math.isclose(geom, 0.5)  # the disk approximation differs


def test_361_a3_applies_mean_torque_factor():
    # Approved correction (AC 23-19A): 23.361(c) applies the 1.25 turbopropeller
    # mean-torque factor to *all* of paragraph (a), so the malfunction torque is
    # 1.6 x 1.25 x mean takeoff torque, not 1.6 x mean alone. The manual /
    # ENGLOADS.BAS (TTP=1.6*ENGTORQ) encode the pre-Amdt-45 unfactored form:
    #   manual:    1.6 x 1970          = 3152 ft-lb
    #   corrected: 1.6 x 1.25 x 1970   = 3940 ft-lb
    # See CLAUDE.md "Approved corrections to the source".
    r = calc.condition_361_a3(turboprop())
    assert math.isclose(value_of(r, "torque_factor"), 1.25, abs_tol=1e-9)
    assert math.isclose(value_of(r, "malfunction_factor"), 1.6, abs_tol=1e-9)
    assert math.isclose(value_of(r, "mean_takeoff_torque"), 1970, abs_tol=1e-9)
    assert math.isclose(value_of(r, "mx_mount_torque"), -3940, rel_tol=TOL)
    assert math.isclose(value_of(r, "fz_vertical"), 450, abs_tol=1e-9)  # 1g x PPWT


def test_gyro_thrust_matches_manual():
    # Manual: THRUST = 1970 * 230.38 / 101.2 = 4484.7 lb
    r = calc.condition_371_b(turboprop())
    assert math.isclose(value_of(r, "fx_thrust"), 4484.7, abs_tol=1.0)


# --------------------------------------------------------------------------- #
# Gyroscopic thrust basis (#408, review P-6): max-continuous power, ideal-disc bound
# --------------------------------------------------------------------------- #
def _example(name):
    from sloads import io
    examples = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
    return io.load_project(os.path.join(examples, f"{name}.project.json"))


def test_ideal_static_thrust_is_flaploads_momentum_equation_at_rest():
    """The bound is FLAPLOAD.BAS sub 500's momentum equation (Ref 1 Appendix C)
    at V = 0: the wake velocity U1 that absorbs P through the disc,
    ``P = rho*A*U1^3/4``, makes ``T = rho*A*U1^2/2`` -- solved here for U1 and
    checked against the flap module's own power expression."""
    from sloads.constants import FT_LB_S_PER_HP, RHO_SL
    hp, dia_in = 1700.0, 156.0
    area = math.pi * (dia_in / 12.0) ** 2 / 4.0
    u1 = (4.0 * hp * FT_LB_S_PER_HP / (RHO_SL * area)) ** (1.0 / 3.0)
    # flap._slipstream_velocity's absorbed power at VF = 0
    assert math.isclose(area * RHO_SL * u1 * u1 ** 2 / (4.0 * FT_LB_S_PER_HP), hp, rel_tol=1e-12)
    assert math.isclose(calc.ideal_static_thrust(hp * FT_LB_S_PER_HP, dia_in),
                        RHO_SL * area * u1 ** 2 / 2.0, rel_tol=1e-9)


def test_gyro_thrust_never_exceeds_the_ideal_disc_bound():
    """**Closure gate (#408)**: on every shipped turboprop that enters its
    max-continuous power, the delivered gyro thrust is no more than an ideal
    disc of its diameter makes from that power -- a real propeller makes less."""
    import glob
    from sloads import io
    from sloads.constants import FT_LB_S_PER_HP
    examples = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
    checked = 0
    for path in sorted(glob.glob(os.path.join(examples, "*.project.json"))):
        for eng in calc.resolved_engines(io.load_project(path)):
            if not eng.is_turboprop or eng.max_cont_hp is None or eng.prop_diameter_in <= 0:
                continue
            bound = calc.ideal_static_thrust(eng.max_cont_hp * FT_LB_S_PER_HP, eng.prop_diameter_in)
            for cond in (calc.condition_371_b(eng), calc.condition_25_371(eng)):
                assert value_of(cond, "fx_thrust") <= bound * (1.0 + 1e-9), (path, cond.far_reference)
            checked += 1
    assert checked >= 2  # both ATR fixtures, both engines each -- never vacuous


def test_atr_gyro_thrust_is_its_max_continuous_ideal_disc_bound():
    """The ATR's PW120 at 1700 shp max continuous through the 156 in disc:
    P = 1700 x 550 = 935,000 ft-lb/s, A = pi x 13^2 / 4 = 132.73 sq ft,
    T = (2 x 0.002378 x 132.73 x 935,000^2)^(1/3) = 8202.5 lb. Power over VSF
    is 9239 lb, so the bound governs; before #408 the take-off torque at
    eta = 1 delivered 10,865 lb, labelled max continuous."""
    eng = calc.resolved_engines(_example("atr42_100"))[0]
    r = calc.condition_371_b(eng)
    assert math.isclose(value_of(r, "fx_thrust"), 8202.5, rel_tol=TOL)
    label = next(v.label for v in r.values if v.key == "fx_thrust")
    assert label == "Max continuous thrust (MCP, ideal-disc bound)"
    assert "ideal-disc bound of maximum-continuous power" in r.note


def test_engloads_basis_is_labelled_and_flagged_above_the_bound():
    """Blank ``max_cont_hp`` keeps ENGLOADS's printed arithmetic (the oracle
    above, 4484.7 lb) under a label that says what it is, and the note says the
    value exceeds the 101 in disc's ideal bound at that power (3792 lb)."""
    r = calc.condition_371_b(turboprop())
    label = next(v.label for v in r.values if v.key == "fx_thrust")
    assert label == "Thrust at VSF from max engine torque (ENGLOADS basis)"
    assert "above the ideal-disc bound 3792 lb; enter max_cont_hp" in r.note


def test_gyro_thrust_has_one_owner_for_23_371_and_25_371():
    for eng in (turboprop(), calc.resolved_engines(_example("atr42_100"))[0]):
        assert value_of(calc.condition_25_371(eng), "fx_thrust") == value_of(
            calc.condition_371_b(eng), "fx_thrust") == calc.gyro_thrust(eng)[0]


def test_turboprop_runs_six_conditions():
    assert len(run_all(turboprop())) == 6


# --------------------------------------------------------------------------- #
# Multi-engine layout (first-class; loads loop over every engine)
# --------------------------------------------------------------------------- #
def test_single_engine_run_matches_run_all():
    from sloads import EngineLayout, Project

    project = Project(name="single", engines=[io520bb()], engine_layout=EngineLayout.SINGLE_NOSE)
    mr = calc.run(project)
    ref = run_all(io520bb())
    # One engine: run(project) is byte-identical to run_all (no title prefixes).
    assert [c.title for c in mr.conditions] == [c.title for c in ref]
    assert len(mr.conditions) == 3


def test_twin_wing_loops_over_each_engine():
    from dataclasses import replace

    from sloads import EngineLayout, Project

    left = replace(io520bb(), engine_designation="LEFT", engine_cg=(22.0, -60.0, -10.0))
    right = replace(io520bb(), engine_designation="RIGHT", engine_cg=(22.0, 60.0, -10.0))
    project = Project(name="twin", engines=[left, right], engine_layout=EngineLayout.TWIN_WING)
    mr = calc.run(project)
    # Two reciprocating engines -> 2 x 3 conditions, each tagged by designation.
    assert len(mr.conditions) == 6
    assert mr.conditions[0].title.startswith("[LEFT]")
    assert mr.conditions[3].title.startswith("[RIGHT]")


def test_engine_layout_count_is_asked_not_enforced():
    """TWIN_WING with one engine constructs (a saved file must reopen, #66) and
    says what is wrong through the rule's one owner."""
    from sloads import EngineLayout, Project

    project = Project(name="bad", engines=[io520bb()], engine_layout=EngineLayout.TWIN_WING)
    assert project.engine_layout_problem() == "engine_layout 2W expects 2 engine(s), got 1"


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
