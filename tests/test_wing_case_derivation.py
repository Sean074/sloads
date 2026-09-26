"""Deriving the wing structural cases from SELECT (Step M4-2, decisions 2 and 7).

``WingMassInput.cases`` used to be a hand-authored second entry of conditions
SELECT had already searched the V-n matrix for. M4-2 makes SELECT the authority:
an empty ``cases`` list derives from ``envelope.critical``.

**The gate (decision 7).** There is no printed oracle for the derivation, so the
benchmark-first requirement is met by a *closure* check instead: derive
``ga6_normal``'s wing cases from its own envelope and compare them against the
hand-typed values in the fixture, which are the Appendix A worked example's
printed figures (Ref 1 p217-221). Derivation never fires for ga6 in normal use
(its ``cases`` list is non-empty, so the Appendix A oracles are untouched by
construction) -- this test exists to check that the two routes *agree*, i.e. that
turning derivation on for a project would not quietly change the loads.

What it locks, and what design note 52 changed
----------------------------------------------
Nz and Nx agree closely for every shared condition. The air-load CL/V agree for
the balanced picks (PHAA, TORS). ACRL used to be the one that did not: SELECT's
23.349(a)(2) pick is the AC ROLL point, balanced at the airplane-average factor,
whose own CL is the average of the two sides' -- while the manual's 100 % side
flies condition A (CL 1.55 at 116 kt in the worked example). D-29 accepted that
divergence on the premise that every fixture entered its ACRL; note 63 removed
the premise, and **note 52 D-52.10 closes it**: a derived ACRL takes its air
point from condition A (``rolling.condition_a_point``), its couple from
condition A's root bending (D-52.2), and ``ga6_normal``'s ACRL row is itself
derived since #306 (D-52.12) -- the Appendix A case 160 is held by a test-built
case in ``tests/test_rolling_conditions.py``.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.models import WingLoadCase, WingMassInput
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.net_loads import _air_cl_v
from sloads.modules.select import build_critical
from sloads.modules.wing_inertia import (
    _resolve_case,
    resolve_wing_cases,
    wing_case_ref,
)

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")

# Tolerances the derivation is held to, per quantity. Nz is the load factor
# itself and must land on the same V-n point; Nx = -DX/W is a small difference of
# larger numbers and is allowed more room; V is the point's own speed.
_NZ_TOL = 5e-3      # 0.5%
_NX_TOL = 5e-2      # 5%
_V_TOL = 1.5e-2     # 1.5%

#: Conditions whose air-load CL/V the fixture still enters by hand, so the two
#: routes can be compared (ACRL is derived on the fixture since #306).
_AIR_LOAD_AGREES = ("PHAA", "TORS")


def _selected_project():
    """ga6 with its envelope and SELECT critical-load set computed and persisted."""
    project = io.load_project(_GA)
    project.envelope = build_envelope(project)
    project.envelope.critical = build_critical(project)
    return project


def test_an_empty_case_list_derives_from_select():
    """Decision 2: no cases entered -> SELECT's wing conditions, by name."""
    project = _selected_project()
    derived = resolve_wing_cases(project, WingMassInput())
    assert derived, "SELECT produced no wing conditions to derive from"
    names = [c.name for c in derived]
    assert names == [c.label for c in project.envelope.critical.conditions
                     if c.component == "wing"]
    # Every derived case references a real V-n point, which is what lets
    # _resolve_case fill Nz/Nx and _air_cl_v fill the air-load condition.
    for c in derived:
        assert c.case is not None
        assert any(p.case == c.case for p in project.envelope.vn)


def test_an_entered_list_is_a_filter_on_the_slots():
    """Decision 2 as narrowed by design note 63 D-63.7 (#292): a non-empty list
    decides *which* slots run and keeps every value it enters (the Appendix A
    nz/nx/CL/V on the GA6, an ACRL couple), and an entry naming a slot with no
    ``case`` of its own takes the slot's delivered V-n point -- never a second
    source of points. An entry that names no slot is returned untouched."""
    from dataclasses import replace

    project = _selected_project()
    slots = {c.label: c.case for c in project.envelope.critical.conditions
             if c.component == "wing"}
    got = resolve_wing_cases(project, project.wing_mass)
    entered = project.wing_mass.cases
    # Every entered value is kept; the one completion is the accelerated roll's,
    # whose blanks the note 52 owners fill (D-52.2/D-52.10).
    assert [replace(c, case=None) for c in got if c.name != "ACRL"] == \
        [c for c in entered if c.name != "ACRL"]
    acrl = next(c for c in got if c.name == "ACRL")
    assert acrl.cl is not None and acrl.v_eas_kt is not None and acrl.unbal_moment
    assert [c.case for c in got] == [slots[c.name] for c in entered]
    # An explicit case reference, or a name outside the slots, is left alone.
    wm = replace(project.wing_mass, cases=[
        replace(project.wing_mass.cases[0], case=5),
        WingLoadCase(name="HAND", nz=-2.0, nx=0.1, cl=1.0, v_eas_kt=100.0)])
    assert resolve_wing_cases(project, wm) == wm.cases


def test_derived_load_factors_match_the_worked_example():
    """Decision 7's closure gate: the derived Nz/Nx reproduce the hand-typed
    Appendix A figures for every condition the fixture and SELECT share."""
    project = _selected_project()
    # The rows the fixture still enters by hand (PHAA, TORS); ACRL is derived on
    # the fixture since #306, and its factor is the amended one below.
    hand = {c.name: c for c in project.wing_mass.cases if c.nz is not None}
    assert set(hand) == {"PHAA", "TORS"}
    derived = [c for c in resolve_wing_cases(project, WingMassInput()) if c.name in hand]
    assert {c.name for c in derived} == set(hand), "fixture and SELECT name different conditions"
    acrl = next(c for c in resolve_wing_cases(project, WingMassInput()) if c.name == "ACRL")
    # 23.349(a)(2) as amended (D-52.11): (100 + 75)/200 * 3.8, not the printed 3.25.
    assert math.isclose(_resolve_case(project, acrl).nz, -0.875 * 3.8, rel_tol=_NZ_TOL)

    for case in derived:
        got = _resolve_case(project, case)
        want = _resolve_case(project, hand[case.name])
        assert math.isclose(got.nz, want.nz, rel_tol=_NZ_TOL), f"{case.name} Nz {got.nz} vs {want.nz}"
        assert math.isclose(got.nx, want.nx, rel_tol=_NX_TOL), f"{case.name} Nx {got.nx} vs {want.nx}"


def test_derived_air_load_matches_for_the_balanced_conditions():
    """The air-load half of the same gate, for the conditions where the two
    routes genuinely name the same point (see the module docstring for ACRL)."""
    project = _selected_project()
    hand = {c.name: c for c in project.wing_mass.cases}
    for case in resolve_wing_cases(project, WingMassInput()):
        if case.name not in _AIR_LOAD_AGREES or case.name not in hand:
            continue
        cl, v = _air_cl_v(project, case)
        cl_want, v_want = _air_cl_v(project, hand[case.name])
        assert math.isclose(cl, cl_want, rel_tol=1e-2), f"{case.name} CL {cl} vs {cl_want}"
        assert math.isclose(v, v_want, rel_tol=_V_TOL), f"{case.name} V {v} vs {v_want}"


def test_a_derived_acrl_flies_condition_a():
    """**G-52.10 on the derived route** (design note 52, D-52.10; supersedes the
    D-29 divergence pin this test replaced). A derived ACRL's air point is
    condition A -- ``STALL +N`` at the picked AC ROLL point's weight, altitude,
    CG and configuration -- not the roll point's airplane-average lift, and its
    couple is ``-(1 - p/100)`` of that point's root air bending."""
    from sloads.modules.rolling import condition_a_root_mxx

    project = _selected_project()
    vn = {p.case: p for p in project.envelope.vn}
    acrl = next(c for c in resolve_wing_cases(project, WingMassInput()) if c.name == "ACRL")
    pick = vn[acrl.case]
    assert pick.condition == "AC ROLL"
    cond_a = next(p for p in vn.values() if p.condition == "STALL +N" and p.cg == pick.cg
                  and p.config == pick.config and p.altitude_ft == pick.altitude_ft)
    assert _air_cl_v(project, acrl) == (cond_a.cl, cond_a.v_eas_kt)
    assert cond_a.cl > pick.cl, "the 100 % side carries more lift than the average"
    assert acrl.unbal_moment == -0.25 * condition_a_root_mxx(project, cond_a)


def test_an_entered_acrl_value_still_wins():
    """D-52.2/D-52.10: the derivation fills blanks only -- an entered CL, speed
    or couple is the project's statement and is kept (the 2026-08-13 ruling)."""
    from dataclasses import replace

    project = _selected_project()
    wm = replace(project.wing_mass, cases=[
        WingLoadCase(name="ACRL", cl=1.55, v_eas_kt=116.0, unbal_moment=-149043.0)])
    got = resolve_wing_cases(project, wm)[0]
    assert (got.cl, got.v_eas_kt, got.unbal_moment) == (1.55, 116.0, -149043.0)
    # A partly entered row keeps what it states and derives the rest.
    half = resolve_wing_cases(project, replace(wm, cases=[
        WingLoadCase(name="ACRL", unbal_moment=-1.0)]))[0]
    assert half.unbal_moment == -1.0 and half.cl is not None and half.cl != 1.55


# --------------------------------------------------------------------------- #
# The row states the condition its numbers were computed at (user decision
# 2026-08-13, backlog priority 1)
# --------------------------------------------------------------------------- #
def _atr42_project(phaa_speed_kt=None):
    """ATR-42 with a persisted envelope + critical set. ``phaa_speed_kt`` restates
    the speed the shipped fixture entered on PHAA until #292 made its list a
    filter (170 kt against SELECT's pick), for the tests of that ruling."""
    from sloads.models.inputs import WingLoadCase

    project = io.load_project(os.path.join(_EXAMPLES, "atr42_100.project.json"))
    if phaa_speed_kt is not None:
        # The shipped table is empty since #260 (every slot derives, note 62
        # D-62.7), so the filter row is entered here: a PHAA that names the
        # slot and states only its own speed.
        project.wing_mass.cases = [WingLoadCase(name="PHAA", v_eas_kt=phaa_speed_kt)]
    project.envelope = build_envelope(project)
    project.envelope.critical = build_critical(project)
    return project


def test_every_wing_case_row_names_the_speed_its_loads_were_computed_at():
    """The gate for the decision: for every entered case on every fixture, the
    ``CaseRef`` speed is the speed ``net_loads`` built the air load from. Before
    this, a case SELECT had already named kept SELECT's V-n speed instead."""
    for name in sorted(f for f in os.listdir(_EXAMPLES) if f.endswith(".project.json")):
        project = io.load_project(os.path.join(_EXAMPLES, name))
        if project.wing_mass is None or not project.wing_mass.cases:
            continue
        if project.flight_loads is None:
            continue
        project.envelope = build_envelope(project)
        project.envelope.critical = build_critical(project)
        cases = resolve_wing_cases(project, project.wing_mass)
        for i, case in enumerate(cases):
            _, v = _air_cl_v(project, case)
            ref = wing_case_ref(project, i, case)
            assert ref.speed_kt is not None and math.isclose(ref.speed_kt, v, rel_tol=1e-12), (
                f"{name} {case.name}: row states {ref.speed_kt} kt, loads computed at {v} kt")


def test_the_case_id_stays_selects_when_the_speed_is_the_cases_own():
    """The other half of the decision: only the flight-condition fields move.
    ``case_id`` remains SELECT's (M4-2 decision 1 -- one ID per physical
    condition, which the case-index dedupe assumes), and CG / altitude / FAR stay
    SELECT's too, since the case states none of them."""
    project = _atr42_project(phaa_speed_kt=170.0)
    select_refs = {c.label: c.case_ref for c in project.envelope.critical.conditions
                   if c.component == "wing" and c.case_ref is not None}
    cases = resolve_wing_cases(project, project.wing_mass)
    diverged = 0
    for i, case in enumerate(cases):
        want = select_refs.get(case.name)
        if want is None:
            continue
        ref = wing_case_ref(project, i, case)
        assert ref.case_id == want.case_id, case.name
        assert (ref.cg, ref.altitude_ft, ref.far_reference) == (
            want.cg, want.altitude_ft, want.far_reference), case.name
        if want.speed_kt is not None and case.v_eas_kt is not None \
                and not math.isclose(ref.speed_kt, want.speed_kt, rel_tol=1e-9):
            diverged += 1
        # SELECT's own CaseRef is never mutated -- the wing row takes a copy.
        assert want.speed_kt == select_refs[case.name].speed_kt
    assert diverged, "the entered 170 kt PHAA did not diverge from SELECT's pick"


def test_the_atr42_phaa_divergence_is_pinned():
    """The measured instance behind the decision: the fixture enters PHAA at
    170 kt, SELECT's PHAA point is 147.55 kt. The row now reads 170.

    SELECT's pick moved from 185.85 kt with Pri 5 / D-26: PHAA is flown at
    ``CGmid``, whose station and waterline are now its loading's own rather than
    an unreachable corner point, so the balanced V-n point behind it moved with
    them. **And back to 185.36 kt with D-27 (2026-08-17):** the flight cases are
    the WTENV limit points now, PHAA is flown at ``fwd gross`` (MTOW at the
    forward-gross limit), and the balanced point moved with the case once more.
    The divergence the decision exists for is unchanged in kind and in sign.
    **Since #292 the shipped fixture enters a filter** (note 63 D-63.7: its
    PHAA carries no speed of its own), so the 170 kt entry is restated here in
    memory -- the mechanism is the fixture's to use, and this pins it. **And
    147.55 kt since #260 (2026-09-21):** the fixture's wing was redrawn to the
    type's area and its CLmax re-entered, so the STALL +N point moved; the
    shipped table is now empty and the PHAA row is entered here.
    """
    project = _atr42_project(phaa_speed_kt=170.0)
    cases = resolve_wing_cases(project, project.wing_mass)
    phaa = next(((i, c) for i, c in enumerate(cases) if c.name == "PHAA"), None)
    assert phaa is not None, "atr42_100 no longer enters a PHAA wing case"
    i, case = phaa
    select_ref = next(c.case_ref for c in project.envelope.critical.conditions
                      if c.component == "wing" and c.label == "PHAA")
    assert math.isclose(case.v_eas_kt, 170.0, rel_tol=1e-9)
    assert math.isclose(select_ref.speed_kt, 147.55, rel_tol=1e-3), select_ref.speed_kt
    assert math.isclose(wing_case_ref(project, i, case).speed_kt, 170.0, rel_tol=1e-9)


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
