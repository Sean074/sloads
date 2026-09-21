"""Which test is each registered module's benchmark-first gate (#186, R-16).

**The defect class this closes.** `CLAUDE.md` rule 2 makes an oracle test
(±0.1 %, page-cited) or a stated physics-closure gate in CI the definition of
done for every module — and until this manifest existed, nothing asserted that a
registered module *had* one. The rule lived in prose, which is precisely what
practice 3 says a cross-cutting convention may never be: a module could register,
ship, and appear in every front end with no gate at all, and the suite would stay
green. The 2026-09-04 project review found the coverage complete by inspection
(R-16) — inspection is not a guard, and the next module is the one nobody
inspects.

**One row per registered module, and the registry is the other half.**
``tests/test_module_gates.py`` walks :func:`sloads.registry.available` and
requires the two sets to match exactly, so a module that registers without a row
fails at the moment it is added rather than at the next review. A row whose
module stops registering fails the same way: a manifest that outlives its
subject is how the statement and the code come apart.

**Two kinds, because the manual gives two.** ``ORACLE`` is Reference 1's printed
figures — Appendix A (the 6-place GA single, p131), or the Ch 9 worked hand-calc
— matched within ±0.1 % with the printed number and its page kept in the test.
``CLOSURE`` is rule 2's substitute where no printed figure exists: a stated
physics invariant. The split is not a quality ranking and must not be read as
one — ``tail_span``'s analytic closures are stronger evidence than a
three-significant-figure page match — it records *what the evidence is*, which is
what a reviewer needs and what `20_theory/00_theory_sources.md`'s Oracle-status
section states in prose. **The prose stays normative; this is its machine-readable
half**, and the guard checks each ORACLE row's citation actually appears in the
test file, so a citation deleted from a test fails here rather than going unnoticed.

Appendix B (the 10-place twin turboprop) is **absent** from the bundled
`reference/FAR23Loads_Code.pdf`, so no module has a printed twin oracle; the
twin-only paths are closure-locked by that fact and not by preference
(`00_theory_sources.md` § Oracle status).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

#: A printed figure in Reference 1, matched within ±0.1 % (Decision 3).
ORACLE = "oracle"

#: Rule 2's substitute where no printed figure exists: a stated physics closure.
CLOSURE = "closure"


@dataclass(frozen=True)
class Gate:
    """One module's benchmark-first gate.

    ``tests`` are function names in ``tests/test_<module>.py`` — the file is
    derived from the module name rather than stored, so the two cannot disagree.
    ``cites`` is the printed source for an :data:`ORACLE` (the guard requires one
    of its page/appendix tokens to appear in the test file) or the invariant in
    words for a :data:`CLOSURE`.
    """

    kind: str
    tests: Tuple[str, ...]
    cites: str


#: Module name -> its gate. Keys must match ``registry.available()`` exactly.
GATES: Dict[str, Gate] = {
    # -- Oracle-locked: Appendix A prints the figures ----------------------- #
    "weight_estimate": Gate(
        ORACLE, ("test_summary_matches_manual", "test_structure_group_matches_manual"),
        "Appendix A p133 — the 6-place GA weight statement, group by group"),
    "weight_onecg": Gate(
        ORACLE, ("test_weight_and_cg_match_manual", "test_inertias_airplane_axes_match_manual"),
        "Appendix A p136 — weight, CG and the airplane-axes inertias"),
    "weight_envelope": Gate(
        ORACLE, ("test_both_edges_reproduce_appendix_a_p139", "test_structural_limit_stations"),
        "Appendix A p139 — all 16 printed rows on both envelope edges (note 45 WE-5)"),
    "wing_geometry": Gate(
        ORACLE, ("test_wing_matches_manual",),
        "Appendix A p141 — MAC 69.246, XLEMAC 63.641 and the per-surface tables"),
    "structural_speeds": Gate(
        ORACLE, ("test_design_speeds_match_manual", "test_vd_floor_no_chosen_speeds"),
        "Appendix A — VA 121.3, VC 170, VD 212.5, VF 105.5 KEAS; n +3.8/-1.52"),
    "mach_limit": Gate(
        ORACLE, ("test_mne", "test_line_at_shoulder_altitude"),
        "Appendix A p160 — MNE 0.3627 and the Mach-limited equivalent airspeeds"),
    "airloads": Gate(
        ORACLE, ("test_additive_distribution_matches_appendix_a",
                 "test_basic_distribution_matches_appendix_a"),
        "Appendix A p161-162 — the additive and basic spanwise tables"),
    "flight_envelope": Gate(
        ORACLE, ("test_design_speeds_match_appendix_a", "test_cg1_corner_speeds_and_load_factors"),
        "Appendix A p179-180 — the cruise balanced V-n matrix per CG case"),
    "select": Gate(
        ORACLE, ("test_critical_wing_conditions_match_appendix_a",
                 "test_critical_htail_balancing_match_appendix_a"),
        "Appendix A — the printed critical wing / h-tail / v-tail / fuselage summaries"),
    "balloads": Gate(
        ORACLE, ("test_case_202_up_balancing_load", "test_matches_select_balancing"),
        "Reference 1 Ch 9 case-202 hand-calc — LT 519.845, LT25 +907.62, LT50 -387.78"),
    "wing_inertia": Gate(
        ORACLE, ("test_root_tip_density_match_appendix_a",
                 "test_combined_torsion_case_matches_appendix_a"),
        "Appendix A p217-221 — root/tip density and the combined case 138"),
    "net_loads": Gate(
        ORACLE, ("test_net_loads_case22_matches_appendix_a",
                 "test_air_load_distribution_matches_appendix_a"),
        "Appendix A p222 — net loads case 22 PHAA, the algebraic sum of p206 and the inertia"),
    "taildist": Gate(
        ORACLE, ("test_horizontal_chordwise_oracle", "test_vertical_chordwise_oracle"),
        "Appendix A p237 + p245 — 13 horizontal and 4 vertical PSI(X1..X5) rows"),
    "aileron": Gate(
        ORACLE, ("test_aileron_oracle",),
        "Appendix A p200 — critical aileron loads, down 271.44 / up -180.96 lb at 170 kt"),
    "flap": Gate(
        ORACLE, ("test_flap_clf_oracle", "test_flap_critical_load_oracle"),
        "Appendix A p201 — CLf, the 629 lb critical load, slipstream and gust factors"),
    "tab": Gate(
        ORACLE, ("test_tab_oracle",),
        "Appendix A p202 — h-tail tab E 0.17735, LTAB 84.62 lb"),
    "engine": Gate(
        ORACLE, ("test_361_a1", "test_derived_quantities"),
        "Appendix A p131 (Continental IO-520-BB) — with the 23.361 approved corrections"),
    "landing": Gate(
        ORACLE, ("test_landload_p231_ground_line_table", "test_landload_p232_airplane_datum_table",
                 "test_landload_p233_unbalanced_moments_table", "test_lgfactor_oracle"),
        "Appendix A p231/p232/p233 — every printed cell of all 33 cases, plus p236 LGFACTOR"),

    # -- Closure-locked: no printed figure exists (rule 2's substitute) ----- #
    "configuration": Gate(
        CLOSURE, ("test_mac_matches_closed_form", "test_appendix_a_sanity"),
        "a modern addition with no manual oracle: the generated polygon's MAC/XLEMAC/"
        "Y_MAC equal the trapezoid closed form, and Appendix A p141's wing is "
        "reproduced to a stated plausibility band"),
    "body_loads": Gate(
        CLOSURE, ("test_the_two_cantilevers_and_the_box_close_the_free_body",
                  "test_a_positive_load_factor_bends_both_bodies_down"),
        "Ch 15 ships no program and no printed station table (Ref 1 p103), so the "
        "gate is equilibrium: the forward body's terminal at the front spar, the "
        "aft body's at the rear spar, the box's applied rows and the wing reaction "
        "at the wing station sum to zero force and zero moment, and a positive load "
        "factor bends both bodies down (design note 64 gates 4 and 5)"),
    "one_engine_out": Gate(
        CLOSURE, ("test_thrust_and_windmill_drag_formula", "test_time_history_matches_case",
                  "test_the_shipped_turboprops_execute_onengout"),
        "the printed Appendix B twin oracle is absent from the bundled reference, so "
        "the gate is sub-formula exactness against ONENGOUT.BAS 205-208 plus "
        "integration closure, with the twin oracle recorded as a deferred item"),
    "tail_span": Gate(
        CLOSURE, ("test_the_strip_loads_sum_to_the_select_total_plus_the_inertia",
                  "test_the_root_bending_is_the_half_load_times_the_area_centroid",
                  "test_the_symmetric_cases_roll_the_centreline_by_nothing",
                  "test_the_torsion_is_the_area_weighted_closed_form",
                  "test_the_inertia_sums_to_minus_n_times_the_surface_weight"),
        "Appendix A stops at the totals (SELECT) and the chordwise profile "
        "(TAILDIST), so the gate is plan 09 section 4's five analytic closures: "
        "force, bending, centreline rolling, torsion and inertia"),
    "balance": Gate(
        CLOSURE, ("test_the_case_closes_in_all_six_dof",
                  "test_the_case_closes_in_all_three_symmetric_dof",
                  "test_the_deck_balances_from_its_own_cards"),
        "a full-airplane assembly no appendix prints: every balanced case closes in "
        "all six DOF within RESIDUAL_GATE (1 % of n*W / n*W*MAC), and the exported "
        "deck re-closes from its own card text"),
}
