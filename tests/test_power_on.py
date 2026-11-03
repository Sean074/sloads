"""Design note 21 §10 (#226): the power-on flight cases -- gates G10-1 to G10-8.

References: 14 CFR 25.321(b), "Critical thrust values in the range from zero to
maximum continuous thrust must be considered" (the current eCFR); the balance is
Ref 1 Ch 8 "Equations" (FLTLOADS.BAS subroutine 3900, Appendix C p421-428) with
the thrust's moment and normal force added; the rating is P-2/P-14,
``T = 0.85 * P_MC / V_TAS`` (ONENGOUT.BAS's live-engine thrust, Appendix C)
capped by the momentum-theory static thrust ``(2 rho A P^2)^(1/3)``.
"""

import math
import os
from dataclasses import replace

import pytest

from sloads import io
from sloads.case_ids import WING_SLOTS, wing_case_id
from sloads.models import MissingInputError
from sloads.modules import flight_envelope as fe
from sloads.modules.balance import build_balanced_cases
from sloads.modules.balance.applied import HUB_THRUST_SOURCE
from sloads.modules.body_loads import body_distribution, build_body_loads
from sloads.modules.select import build_critical, split_power_states
from sloads.power import (
    STATE_ON,
    EngineThrust,
    PitchTerms,
    base_label,
    is_power_on,
    pitch_terms,
    point_thrusts,
    power_basis,
    power_label,
    rated_thrusts,
)
from sloads.report.methods import methods_statement
from sloads.validation import consistency_warnings

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_POWERED = ("atr42_100", "atr42_300_seed", "baron_58")


def _load(name, power=None):
    p = io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))
    if power is not None:
        p.aero_coeffs.power_cases = power
    return p


def _off_and_on(name):
    """The same fixture power-off and power-on, one input apart."""
    return _load(name, "off"), _load(name, "off_and_on")


# --------------------------------------------------------------------------- #
# Labels and identity
# --------------------------------------------------------------------------- #
def test_the_suffix_round_trips():
    assert power_label("PHAA") == "PHAA-P" and is_power_on("PHAA-P")
    assert base_label("PHAA-P") == "PHAA" and base_label("PHAA") == "PHAA"
    assert not is_power_on("MAN A")


def test_power_on_wing_slots_take_their_own_fixed_band():
    """P-15: ``PHAA-P`` is ``W-40``, slot for slot after the power-off slots,
    so no power-off id depends on whether a project runs power on."""
    for label, slot in WING_SLOTS.items():
        assert wing_case_id(power_label(label)) == f"W-{39 + slot:02d}"
        assert wing_case_id(label) == f"W-{slot:02d}"


@pytest.mark.parametrize("name", _POWERED)
def test_power_on_conditions_carry_their_own_bands_and_twins(name):
    """Every ``-P`` condition names a power-on V-n point under its base label,
    and takes an id in its component's power band (W-40, HT-80, F-50); the fin
    gets none (P-11)."""
    project = _load(name)
    env = fe.build_envelope(project)
    vn = {p.case: p for p in env.vn}
    on = [c for c in build_critical(project, env).conditions if is_power_on(c.label)]
    assert on
    bands = {"wing": range(40, 50), "htail": range(80, 100), "fuselage": range(50, 100)}
    for c in on:
        assert c.component in bands, c.label
        assert int(c.case_ref.case_id.split("-")[1]) in bands[c.component], c.case_ref.case_id
        point = vn[c.case]
        assert point.power_state == STATE_ON and is_power_on(point.condition)


# --------------------------------------------------------------------------- #
# G10-1 -- power off is today's analysis
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", _POWERED)
def test_g10_1_the_power_off_matrix_picks_and_deck_are_unchanged(name):
    """G10-1: with power on, the power-off half of the matrix, the power-off
    conditions and the power-off deck cases are exactly the ``"off"`` run's --
    the twins are appended after it, searched in a pass of their own and
    minted from bands of their own."""
    off_p, on_p = _off_and_on(name)
    off_env, on_env = fe.build_envelope(off_p), fe.build_envelope(on_p)
    assert on_env.vn[:len(off_env.vn)] == off_env.vn
    assert all(p.power_state == STATE_ON for p in on_env.vn[len(off_env.vn):])
    key = [(c.component, c.label, c.case, c.case_ref.case_id)
           for c in build_critical(off_p, off_env).conditions]
    assert [(c.component, c.label, c.case, c.case_ref.case_id)
            for c in build_critical(on_p, on_env).conditions
            if not is_power_on(c.label)] == key
    off_deck = {(c.label, c.hand): c for c in build_balanced_cases(off_p)}
    on_deck = {(c.label, c.hand): c for c in build_balanced_cases(on_p)
               if not is_power_on(c.label)}
    assert set(on_deck) == set(off_deck)
    for k, case in off_deck.items():
        assert [(ld.x, ld.fx, ld.fz, ld.my) for ld in on_deck[k].loads] == \
               [(ld.x, ld.fx, ld.fz, ld.my) for ld in case.loads], k


def test_g10_1_ga6_runs_power_off_and_says_so():
    """The Appendix A airplane is power-off (McMaster's FLTLOADS knows no
    thrust) and its methods statement says which end of 25.321(b) it is."""
    p = _load("ga6_normal")
    assert all(pt.power_state != STATE_ON for pt in fe.build_envelope(p).vn)
    assert "POWER BASIS: Power: off." in methods_statement(p)


# --------------------------------------------------------------------------- #
# G10-2 -- the closed form
# --------------------------------------------------------------------------- #
def test_g10_2_one_thrust_moves_the_tail_load_by_its_moment_over_the_tail_arm():
    """G10-2: at fixed LZ, DX and M, a thrust T at height dz above the CG moves
    LT by exactly ``-T dz / (XT - Xcg)`` -- ``ga6_normal``'s CG1 geometry, one
    axial 1,000 lb engine 10 in above the CG."""
    p = _load("ga6_normal")
    cg = fe.flight_cases(p)[0]
    wr = fe.require_wing_reference(p)
    xt = p.flight_loads.xtc
    t = EngineThrust(engine=1, thrust_lb=1000.0, hub=(cg.xcg - 80.0, 0.0, cg.zcg + 10.0),
                     axis=(-1.0, 0.0, 0.0))
    terms = pitch_terms([t], cg)
    assert terms.moment == pytest.approx(-1000.0 * 10.0, rel=1e-12)
    assert terms.fx == -1000.0 and terms.fz == 0.0
    base = fe._tail_load(2000.0, 150.0, -30000.0, cg, wr, xt, None)
    moved = fe._tail_load(2000.0, 150.0, -30000.0, cg, wr, xt, terms)
    assert moved - base == pytest.approx(-1000.0 * 10.0 / (xt - cg.xcg), rel=1e-12)


def test_the_rating_is_eta_p_over_v_capped_by_static_thrust():
    """P-14: ``0.85 P / V_TAS`` per engine, and at low speed the momentum-theory
    static thrust of ``0.85 P`` through the disc -- never the drag."""
    p = _load("atr42_100")
    eng = p.engines[0]
    power = 0.85 * eng.max_cont_hp * 550.0
    fast = rated_thrusts(p, 250.0, 0.0)
    v_tas = 250.0 * 1.6878098571011957
    assert fast[0].thrust_lb == pytest.approx(power / v_tas, rel=1e-9)
    area = math.pi * (eng.prop_diameter_in / 24.0) ** 2
    static = (2.0 * 0.002378 * area * power ** 2) ** (1.0 / 3.0)
    assert rated_thrusts(p, 20.0, 0.0)[0].thrust_lb == pytest.approx(static, rel=1e-9)


# --------------------------------------------------------------------------- #
# G10-3 -- the ATR pin
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name, ratio", [("atr42_100", 1.0645), ("atr42_300_seed", 1.0310),
                                         ("baron_58", 0.9933)])
def test_g10_3_the_governing_balancing_tail_load_moves_by_the_measured_share(name, ratio):
    """G10-3: the power-on governing balancing tail load against the power-off
    one -- +6.45 % on the ATR 42-100, the number that ranked the term (note 21
    §10.2a, Q6); the seed +3.1 %; the Baron, whose hubs sit on its CG line,
    -0.7 %."""
    off, on = split_power_states(fe.build_envelope(_load(name)))
    gov = max(abs(p.lt) for p in off.vn)
    assert max(abs(p.lt) for p in on.vn) / gov == pytest.approx(ratio, abs=5e-4)


@pytest.mark.parametrize("name", _POWERED)
def test_a_twin_flies_its_points_speed_or_its_stall_line(name):
    """P-10 as clarified: a twin keeps its point's speed, unless the point is on
    the stall line -- a stall point, or a manoeuvre corner whose speed is below
    the stall line's (``MAN A`` at VA on the ATR) -- where the twin stays on the
    line: its CL no further above the Mach-adjusted stall CL than FLTLOADS'
    own +0.005 band, the speed moving by the thrust's share of the lift
    (<= 1.1 %)."""
    from sloads.aero_curves import clmax_curve

    project = _load(name)
    off, on = split_power_states(fe.build_envelope(project))
    cruise = fe.balance_configs(project.aero_coeffs)[0]
    kmn = clmax_curve(project.flight_loads.mn)
    by = {(p.condition, p.config, p.cg, p.altitude_ft): p for p in off.vn}
    for p in on.vn:
        twin = by[(p.condition, p.config, p.cg, p.altitude_ft)]
        if p.v_eas_kt == pytest.approx(twin.v_eas_kt, rel=1e-9):
            continue
        mach = (p.v_eas_kt / math.sqrt(fe.density_ratio(p.altitude_ft))
                / fe._speed_of_sound(p.altitude_ft))
        assert p.cl <= cruise.stall_cl * clmax_curve(mach) / kmn + 0.005 + 1e-12, p.condition
        assert p.v_eas_kt == pytest.approx(twin.v_eas_kt, rel=1.1e-2), p.condition


# --------------------------------------------------------------------------- #
# G10-4 -- the deck's power-on cases are trimmed
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", ("atr42_100", "baron_58"))
def test_g10_4_a_power_on_deck_case_carries_its_rating_and_is_trimmed(name):
    """G10-4: each ``-P`` wing case applies the rated thrust its V-n point was
    balanced with, at the hubs, and its pitch closes with ``q_dot ~ 0`` -- the
    trim carries the couple the #10 entered card leaves to the closure."""
    p = _load(name)
    env = fe.build_envelope(p)
    vn = {q.case: q for q in env.vn}
    cases = [c for c in build_balanced_cases(p)
             if is_power_on(c.label) and c.label[:-2] in WING_SLOTS and not c.hand]
    assert cases
    for case in cases:
        hub = [ld for ld in case.loads if ld.source == HUB_THRUST_SOURCE]
        want = point_thrusts(p, vn[case.vn_case])
        assert len(hub) == len(want)
        assert math.fsum(ld.fx for ld in hub) == pytest.approx(
            math.fsum(t.force[0] for t in want), rel=1e-12)
        assert abs(case.q_dot) < 1e-3, (case.label, case.q_dot)
        assert any("POWER ON" in n for n in case.notes)


# --------------------------------------------------------------------------- #
# G10-5 -- the body beam carries the longitudinal inertia (P-16)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", ("ga6_normal", "atr42_100"))
def test_g10_5_the_body_axial_inertia_is_reacted_at_the_wing(name):
    """G10-5: the wing reaction's ``Rx`` is minus the body's whole axial
    inertia, the axial column is non-zero, and the free body closes."""
    for r in build_body_loads(_load(name)):
        masses = [s for s in r.stations if s.source == "mass"]
        reaction = next(s for s in r.stations if s.source == "reaction")
        assert reaction.fx == pytest.approx(-math.fsum(s.fx for s in masses), rel=1e-12)
        assert any(s.sx for s in r.stations), r.case


def test_g10_5_no_axial_inertia_reproduces_the_vertical_beam():
    """With ``nx = 0`` the beam is the note 64 vertical beam, row for row."""
    from sloads.derived_geometry import carry_through

    p = _load("ga6_normal")
    carry = carry_through(p)
    stations = [(100.0, 300.0, 12.0), (180.0, 500.0, -4.0), (260.0, 200.0, 20.0)]
    with_z, _ = body_distribution(stations, 2.0, -400.0, 300.0, 120.0, carry, 0.0)
    without, _ = body_distribution([s[:2] for s in stations], 2.0, -400.0, 300.0, 120.0, carry)
    assert [(s.fz, s.sz, s.myy) for s in with_z] == [(s.fz, s.sz, s.myy) for s in without]


# --------------------------------------------------------------------------- #
# G10-6 -- the thrust follows the entered line (P-17)
# --------------------------------------------------------------------------- #
def test_g10_6_an_inclined_line_adds_t_sin_i_and_a_blank_line_is_the_x_axis():
    p = _load("atr42_100")
    blank = rated_thrusts(p, 200.0, 0.0)
    i = math.radians(3.0)
    inclined = replace(p, engines=[
        replace(e, thrust_line_aft=(e.prop_cg[0] + 100.0, e.prop_cg[1],
                                    e.prop_cg[2] - 100.0 * math.tan(i)),
                thrust_line_fwd=tuple(e.prop_cg)) for e in p.engines])
    tilted = rated_thrusts(inclined, 200.0, 0.0)
    for a, b in zip(blank, tilted):
        assert a.axis == (-1.0, 0.0, 0.0)
        assert b.force[2] == pytest.approx(a.thrust_lb * math.sin(i), rel=1e-9)
    axial = replace(p, engines=[
        replace(e, thrust_line_aft=(e.prop_cg[0] + 100.0, e.prop_cg[1], e.prop_cg[2]),
                thrust_line_fwd=tuple(e.prop_cg)) for e in p.engines])
    for a, b in zip(blank, rated_thrusts(axial, 200.0, 0.0)):
        assert b.force == pytest.approx(a.force, abs=1e-9)


# --------------------------------------------------------------------------- #
# G10-7 -- a jet stays power-off, stated (P-19)
# --------------------------------------------------------------------------- #
def test_g10_7_a_jet_is_refused_power_on_and_states_zero_thrust():
    p = _load("concept_regional_jet")
    assert "Power: off." in power_basis(p)
    assert "power_cases_unrated" not in {w.code for w in consistency_warnings(p)}
    p.aero_coeffs.power_cases = "off_and_on"
    assert "power_cases_unrated" in {w.code for w in consistency_warnings(p)}
    with pytest.raises(MissingInputError, match="max_cont_hp"):
        fe.build_envelope(p)


def test_an_unknown_power_setting_is_refused_by_name():
    p = _load("baron_58", "sometimes")
    with pytest.raises(ValueError, match="off_and_on"):
        fe.build_envelope(p)


# --------------------------------------------------------------------------- #
# G10-8 -- the two ends bound the thrust range
# --------------------------------------------------------------------------- #
def test_g10_8_half_the_rated_thrust_lies_between_the_two_ends():
    """G10-8: 25.321(b)'s range is bounded by its ends -- on the ATR 42-100 a
    fixed-speed point flown at half its rated thrust has its balancing tail
    load between the power-off and power-on values (note 21 §10.2a)."""
    p = _load("atr42_100")
    fl, wr = p.flight_loads, fe.require_wing_reference(p)
    di = fe.design_inputs(p)
    cruise = fe.balance_configs(p.aero_coeffs)[0]
    cgs = {c.name: c for c in fe.flight_cases(p)}
    off, on = split_power_states(fe.build_envelope(p))
    by = {(q.condition, q.cg, q.altitude_ft): q for q in off.vn}
    checked = 0
    for q in on.vn:
        if q.condition not in ("MAN A", "MAN C", "MAN D", "BAL A", "BAL C", "BAL D"):
            continue
        base = by[(q.condition, q.cg, q.altitude_ft)]
        cap = di.md if q.condition.endswith("D") else di.mc

        def half(v, cg=cgs[q.cg], alt=q.altitude_ft):
            t = pitch_terms(rated_thrusts(p, v, alt), cg)
            return PitchTerms(t.thrust_lb / 2, t.fx / 2, t.fz / 2, t.moment / 2)

        b = fe._balance(di.n_pos if q.condition.startswith("MAN") else 1.0,
                        base.v_eas_kt, cap, cruise, cgs[q.cg], fl, wr, q.altitude_ft,
                        thrust=half)
        lo, hi = sorted((base.lt, q.lt))
        band = 2.0 * fe.NZ_BALANCE_TOL * cgs[q.cg].weight_lb
        assert lo - band <= b.lt <= hi + band, (q.condition, q.cg, q.altitude_ft)
        checked += 1
    assert checked


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
