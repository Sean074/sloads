# sloads Documentation — Index

This directory is organised into seven numbered sections by **document type**.
Lower numbers are the day-to-day references; higher numbers are planning, and
`90_record/` is the record — what happened and when, deliberately out of the
way of a search for what is true now (design note 61). **This file is
generated** by `scripts/build_index.py` from each document's own title; edit
the document, then regenerate.

| Section | Type | Contents |
|---------|------|----------|
| `10_standard/` | **Code standard** | The authoritative description of how the suite works *today* — architecture, the per-module spec, the conventions charter, and the process guides. Update these whenever code changes. |
| `20_theory/` | **Theory & equation sources** | Where each module's equations and regression oracles come from (the `reference/` PDFs), plus per-module page citations as modules are ported. |
| `25_notes/` | **Design notes** | Every design note and plan, **whatever its status** — the agreed rationale behind the physics, the conventions and the process, and the standing citation target for the tests that assert them. Filed by function, not by date (design note 61 CV-3): a note that has shipped is still the authority for what it decided. |
| `30_future/` | **Future development** | The mission-tagged backlog, the parked-items file, and the plan-of-record documents. Design notes live in `25_notes/` from the day they are written. |
| `90_record/` | **The record** (out of the default search path) | What happened and when: the frozen completed-development archives, the changelog and its archives, the per-release verification baselines. Consulted when the question is explicitly *when* or *why did this change*; it is not where current truth lives (design note 61 CV-4). |
| `50_reviews/` | **Process reviews** | Periodic development-process assessments and the recommendations driving process changes. |
| `60_guide/` | **Oracle GUI user guide** | Page-by-page illustrated guide to the oracle GUI (design note 34): front matter, one generated-and-authored chapter per oracle page in workflow order, worked-example appendices. Field tables and the chapter list are generated (`docs/generate_data_dict.py`); screenshots by `scripts/capture_guide_shots.py`. |

---

## 10_standard — Code standard

| File | Title |
|------|-------|
| [`00_program_overview.md`](10_standard/00_program_overview.md) | sloads — Program Code Standard & Developer Guide |
| [`CODE_REVIEW_PROCESS.md`](10_standard/CODE_REVIEW_PROCESS.md) | Code Review Process — sloads |
| [`CONVENTIONS.md`](10_standard/CONVENTIONS.md) | Conventions Charter — Axes, Signs, Units, Load Contract, Case Identity |
| [`DATA_DICTIONARY.md`](10_standard/DATA_DICTIONARY.md) | `project.json` Input Data Dictionary |
| [`DEVELOPMENT_PROCESS.md`](10_standard/DEVELOPMENT_PROCESS.md) | sloads — Development Process (multi-developer) |
| [`GUI_USER_GUIDE.md`](10_standard/GUI_USER_GUIDE.md) | GUI User Guide |
| [`GUI_design.md`](10_standard/GUI_design.md) | sloads — GUI Design & Structure |
| [`ORACLE_REPORT.md`](10_standard/ORACLE_REPORT.md) | The oracle technical report — content standard |
| [`PROGRAM_SPEC.md`](10_standard/PROGRAM_SPEC.md) | sloads — Program Specification |
| [`PROJECT_GUIDE.md`](10_standard/PROJECT_GUIDE.md) | sloads — Project Guide |
| [`RELEASE_PROCESS.md`](10_standard/RELEASE_PROCESS.md) | Release Process — sloads |
| [`SUMMARY_REPORT.md`](10_standard/SUMMARY_REPORT.md) | Summary Report — document standard |
| [`WORKFLOW_COMMANDS.txt`](10_standard/WORKFLOW_COMMANDS.txt) | sloads — standard workflow commands (solo profile) |

## 20_theory — Theory & equation sources (the theory manual)

The hub plus the chaptered theory manual: each `chNN_` chapter follows one
template (scope, cases analyzed, method, **assumptions & limitations**, worked
example, validation, sources); stub chapters ship the template with
assumptions and validation populated first.

| File | Title |
|------|-------|
| [`00_theory_sources.md`](20_theory/00_theory_sources.md) | Theory & Equation Sources |
| [`02_approved_corrections.md`](20_theory/02_approved_corrections.md) | Approved corrections to the source (oracle deviations) — register of record |
| [`ch01_introduction.md`](20_theory/ch01_introduction.md) | Chapter 1 — Introduction: What sloads Computes, and How to Read This Manual |
| [`ch02_conventions.md`](20_theory/ch02_conventions.md) | Chapter 2 — Conventions: Axes, Signs, Units and the Load Contract, Explained |
| [`ch03_airspeeds_envelope.md`](20_theory/ch03_airspeeds_envelope.md) | Chapter 3 — Design Airspeeds and the V-n Envelope (STRSPEED / MACHLIM / FLTLOADS) |
| [`ch04_wing_loads.md`](20_theory/ch04_wing_loads.md) | Chapter 4 — Wing Loads: Selection, Distribution, and the Roll Cases |
| [`ch05_empennage_loads.md`](20_theory/ch05_empennage_loads.md) | Chapter 5 — Empennage Loads: Horizontal Tail, Vertical Tail, and One Engine Out |
| [`ch06_body_loads.md`](20_theory/ch06_body_loads.md) | Chapter 6 — Fuselage (Body) Loads |
| [`ch07_engine_loads.md`](20_theory/ch07_engine_loads.md) | Chapter 7 — Engine-Mount Loads (ENGLOADS) |
| [`ch08_ground_loads.md`](20_theory/ch08_ground_loads.md) | Chapter 8 — Ground and Landing Loads |
| [`ch09_balanced_airplane.md`](20_theory/ch09_balanced_airplane.md) | Chapter 9 — The Balanced Free-Free Airplane: the Balancing Method |
| [`ch10_mass_model.md`](20_theory/ch10_mass_model.md) | Chapter 10 — The Mass Model and Inertia Loads |
| [`ch11_export_sbeam.md`](20_theory/ch11_export_sbeam.md) | Chapter 11 — Export and the sbeam Bridge |

## 25_notes — Design notes

Every design note and plan, whatever its status. A note that has shipped is
still the authority for what it decided, so it is filed by what it *is* and not
by whether its work is done (design note 61 CV-3). The note's own **Status**
line is the single owner of that question; a row here never repeats it (#187).

| File | Title |
|------|-------|
| [`03_resolved_decisions.md`](25_notes/03_resolved_decisions.md) | Resolved Design Decisions (register) |
| [`04_m4-1_body_moment_closure.md`](25_notes/04_m4-1_body_moment_closure.md) | M4-1 — Fuselage body loads: moment closure (design note) |
| [`05_phase_d_gui_workflow_plan.md`](25_notes/05_phase_d_gui_workflow_plan.md) | Phase D — GUI Workflow Restructure (development plan) |
| [`07_m4_maintainability_sequence_plan.md`](25_notes/07_m4_maintainability_sequence_plan.md) | M4 maintainability sequence — execution plan (M4-12 → M4-11 → G8 views → M4-10 → M4-9) |
| [`09_distributed_empennage_loads_plan.md`](25_notes/09_distributed_empennage_loads_plan.md) | Design note — Distributed empennage loads → sbeam FORCE/MOMENT export |
| [`11_balanced_airframe_cases_plan.md`](25_notes/11_balanced_airframe_cases_plan.md) | Design note — Balanced full-airframe load cases (free-free) |
| [`13_step_g8_summary_report_plan.md`](25_notes/13_step_g8_summary_report_plan.md) | Step G8 — Consolidated Summary Report (Export phase) — implementation plan |
| [`14_m4-20_deliverable_units_plan.md`](25_notes/14_m4-20_deliverable_units_plan.md) | M4-20 — Deliverables render in the user-selected unit system (implementation plan) |
| [`15_export_equilibrium_invariant_plan.md`](25_notes/15_export_equilibrium_invariant_plan.md) | Design note — Global equilibrium invariant on exported decks |
| [`16_f25-2_speeds_placards_plan.md`](25_notes/16_f25-2_speeds_placards_plan.md) | Design note — F25-2: Speeds & placards, Part 25 variant (Mach-margin VD route) |
| [`17_sbeam_roundtrip_ci_harness_plan.md`](25_notes/17_sbeam_roundtrip_ci_harness_plan.md) | Design note — sbeam round-trip CI harness |
| [`18_b8a_lateral_closure_plan.md`](25_notes/18_b8a_lateral_closure_plan.md) | Design note — B8a lateral closure: the ±β empennage cases |
| [`19_concentrated_wing_mass_nodal_split_plan.md`](25_notes/19_concentrated_wing_mass_nodal_split_plan.md) | Design note — concentrated wing masses smeared to the nearest node |
| [`20_sign_convention_report_section.md`](25_notes/20_sign_convention_report_section.md) | Sign-Convention Summary & Report Section — design note |
| [`21_d_r8_unsymmetrical_htail_note.md`](25_notes/21_d_r8_unsymmetrical_htail_note.md) | Design note — the 23.427(a) handed balanced h-tail family (D-R8) |
| [`21_power_effects_wing_note.md`](25_notes/21_power_effects_wing_note.md) | Design note — power effects on the wing: thrust and propeller-wake loads (wing-mounted propellers) |
| [`22_case_load_id_linkage_note.md`](25_notes/22_case_load_id_linkage_note.md) | Design note — case identity ↔ deck LOAD id linkage (report + GUI) |
| [`23_step10_ground_cases_plan.md`](25_notes/23_step10_ground_cases_plan.md) | Step 10 — ground/landing cases: design note |
| [`24_body_drag_carrier_note.md`](25_notes/24_body_drag_carrier_note.md) | Design note — a carrier for non-wing drag in the assembled model |
| [`24_lra_beam_model_review_note.md`](25_notes/24_lra_beam_model_review_note.md) | Design review — the LRA beam model (steps 12 / 13 / 14 against the stated target) |
| [`25_d25_cgcase_loading_note.md`](25_notes/25_d25_cgcase_loading_note.md) | D-25 — `CgCase` explicit loading definition (design note) |
| [`26_pri5_fixture_loadings_note.md`](25_notes/26_pri5_fixture_loadings_note.md) | Pri 5 — payload loadings for the four silent fixtures (design note) |
| [`27_lra_model_implementation_note.md`](25_notes/27_lra_model_implementation_note.md) | Step 12 implementation note — the LRA beam model (export + import) |
| [`28_doc_volume_reduction_note.md`](25_notes/28_doc_volume_reduction_note.md) | Design note 26 — documentation volume: archive, fragments, tier S |
| [`29_static_typing_lint_note.md`](25_notes/29_static_typing_lint_note.md) | Design note 27 — static typing and lint depth |
| [`30_multi_developer_process_note.md`](25_notes/30_multi_developer_process_note.md) | Design note 28 — multi-developer development: process, ownership, and the shape of `30_future/` |
| [`31_wing_tank_fuel_separability_note.md`](25_notes/31_wing_tank_fuel_separability_note.md) | Wing-tank fuel separability — `MassItem.wing_fraction` (design note) |
| [`32_conm2_mass_export_plan.md`](25_notes/32_conm2_mass_export_plan.md) | Design note — CONM2 distributed-mass export per payload case |
| [`32_oracle_gui_note.md`](25_notes/32_oracle_gui_note.md) | Oracle GUI — a second front-end over the one analysis model |
| [`33_l7_lateral_body_aero_note.md`](25_notes/33_l7_lateral_body_aero_note.md) | Design note — lumped lateral body aero, `Cy_β` and `Cn_β` (L-7) |
| [`34_derived_scalar_consolidation_note.md`](25_notes/34_derived_scalar_consolidation_note.md) | Note 33 — Derived-scalar consolidation: one owner per quantity, in the dataclasses |
| [`34_oracle_user_guide_note.md`](25_notes/34_oracle_user_guide_note.md) | Oracle GUI User Guide — style and contents |
| [`38_taildist_aero_state_note.md`](25_notes/38_taildist_aero_state_note.md) | TAILDIST states the aero state of each case it distributes |
| [`39_derive_override_note.md`](25_notes/39_derive_override_note.md) | One derive-by-default override mechanism for the duplicated inputs |
| [`40_landing_load_factor_note.md`](25_notes/40_landing_load_factor_note.md) | The landing load factor is entered as N, not NLG |
| [`42_ground_frame_note.md`](25_notes/42_ground_frame_note.md) | The ground-roll attitude's airplane-datum resolution rotates the wrong way |
| [`43_application_point_note.md`](25_notes/43_application_point_note.md) | The ground reaction is transferred from the contact patch on every case; the manual applies the landing attitudes at the axle |
| [`44_oracle_report_note.md`](25_notes/44_oracle_report_note.md) | Oracle technical report — scope, shape and development protocol |
| [`45_wtenv_aft_edge_note.md`](25_notes/45_wtenv_aft_edge_note.md) | WTENV's aft edge — completing the loading-envelope port |
| [`46_applied_wing_load_set_note.md`](25_notes/46_applied_wing_load_set_note.md) | The applied wing load set — six components, and a deck built from them |
| [`47_appendix_b2_chord_bending_note.md`](25_notes/47_appendix_b2_chord_bending_note.md) | Appendix B.2 and chord bending — reopening OR-70 |
| [`48_limit_channel_note.md`](25_notes/48_limit_channel_note.md) | Module analysis is a LIMIT channel — #154 and the boundary it exposed |
| [`49_stated_never_applied_note.md`](25_notes/49_stated_never_applied_note.md) | The factor is stated, never applied — closing OR-86's endpoint |
| [`50_fuselage_carry_through_note.md`](25_notes/50_fuselage_carry_through_note.md) | The wing carry-through is entered as a fuselage station |
| [`51_ttail_asymmetric_transfer_note.md`](25_notes/51_ttail_asymmetric_transfer_note.md) | The T-tail fin carries the horizontal tail's asymmetry (design note 51) |
| [`52_wing_roll_cases_note.md`](25_notes/52_wing_roll_cases_note.md) | The wing's rolling cases arrive complete (design note 52) |
| [`53_engine_thrust_line_note.md`](25_notes/53_engine_thrust_line_note.md) | The engine's thrust line is an input (design note 53) |
| [`54_geometry_joint_model_note.md`](25_notes/54_geometry_joint_model_note.md) | The geometry model owns the joints (design note 54) |
| [`55_lra_deck_solvability_note.md`](25_notes/55_lra_deck_solvability_note.md) | Every exported LRA deck solves, or the export refuses (design note 55) |
| [`56_export_reduction_note.md`](25_notes/56_export_reduction_note.md) | The export package reduces to one solver artifact (design note 56) |
| [`57_gui_convergence_note.md`](25_notes/57_gui_convergence_note.md) | The two front-ends converge on one (design note 57) |
| [`58_ultimate_basis_selection_note.md`](25_notes/58_ultimate_basis_selection_note.md) | Down-select on the ultimate basis; deliver LIMIT (design note 58) |
| [`60_figures_and_one_report_note.md`](25_notes/60_figures_and_one_report_note.md) | The figures and the one report (design note 60) |
| [`61_record_corpus_note.md`](25_notes/61_record_corpus_note.md) | Design note 61 — the record corpus: split by function, quarantine, one telling |
| [`62_negative_wing_slots_note.md`](25_notes/62_negative_wing_slots_note.md) | The negative angle-of-attack wing slots, above SELECT.BAS (design note 62) |
| [`63_one_mass_model_note.md`](25_notes/63_one_mass_model_note.md) | One mass model: the case's loading is the mass state of every inertia load (design note 63) |
| [`64_wing_body_joint_note.md`](25_notes/64_wing_body_joint_note.md) | The wing-to-body joint: one post, two body cantilevers, and nothing integrated through the box (design note 64) |
| [`65_delivered_precision_note.md`](25_notes/65_delivered_precision_note.md) | Every delivered cell prints at the precision its unit prescribes (design note 65) |
| [`66_engine_and_oei_deck_cases_note.md`](25_notes/66_engine_and_oei_deck_cases_note.md) | The deck carries the engine: mount cases and the one-engine-out fin (design note 66) |
| [`67_beam_model_page_note.md`](25_notes/67_beam_model_page_note.md) | The beam model reaches the GUI: the LRA drawn, the deck and the OEW mass set written (design note 67) |
| [`68_sstandards_rev_a_adoption_note.md`](25_notes/68_sstandards_rev_a_adoption_note.md) | sloads complies with sstandards Rev A: the conformance test, the statement and the recorded deviations (design note 68) |
| [`69_geometry_duplicates_note.md`](25_notes/69_geometry_duplicates_note.md) | One owner per geometry quantity on the Geometry page: the parametric wing, the fuselage scalars and the control-surface areas (design note 69) |
| [`70_per_case_mass_properties_note.md`](25_notes/70_per_case_mass_properties_note.md) | Mass properties per CG case: WTONECG reports every loading of record, and the all-items total becomes the labelled database ceiling (design note 70) |
| [`71_mass_owners_note.md`](25_notes/71_mass_owners_note.md) | One owner per mass quantity: the engine, gear, tail, wing-panel and fuselage masses typed on other pages, and the fuselage beam waterline (design note 71) |
| [`72_lgfactor_lift_double_count_note.md`](25_notes/72_lgfactor_lift_double_count_note.md) | LGFACTOR's energy ratio is the gear factor: the wing lift is subtracted twice (design note 72; #401) |
| [`73_balance_feasibility_flags_note.md`](25_notes/73_balance_feasibility_flags_note.md) | Balanced cases are flagged past the elevator stop, tail stall and fin stall (design note 73; #404) |
| [`74_oei_feathering_basis_note.md`](25_notes/74_oei_feathering_basis_note.md) | OEI basis for feathering turboprops: feather credit, a distinct 23.367(a)(2) and a VMC–V speed sweep (design note 74; #405) |

## 30_future — Future development

| File | Title |
|------|-------|
| [`00_backlog.md`](30_future/00_backlog.md) | Backlog — Open Work & Development Plan |
| [`01_concept_loads_plan.md`](30_future/01_concept_loads_plan.md) | Phase C — Initial-Concept Loads Tool (development plan) |
| [`02_parked.md`](30_future/02_parked.md) | Parked Items — off the mission path |
| [`03_gui_rework_plan.md`](30_future/03_gui_rework_plan.md) | Phase G — Workflow-aligned GUI rework (design & specification) |
| [`04_far25_gap_analysis.md`](30_future/04_far25_gap_analysis.md) | FAR 25 Gap Analysis — Extending the FAR23 Loads Methods to Transport-Category Concepts |

## 90_record — The record (out of the default search path)

| File | Title |
|------|-------|
| [`00_completed_development.md`](90_record/00_completed_development.md) | Completed Development |
| [`01_verification_baseline_0.2.0.md`](90_record/01_verification_baseline_0.2.0.md) | Verification Baseline — Release 0.2.0 |
| [`02_verification_baseline_0.3.0.md`](90_record/02_verification_baseline_0.3.0.md) | Verification Baseline — Release 0.3.0 |
| [`06_m3-1_rename_procedure.md`](90_record/06_m3-1_rename_procedure.md) | M3-1 Execution Runbook — Rename `FAR23LOADS`/`farloads` → **`sloads`** (+ split `models.py`) |
| [`08_verification_baseline_0.4.0.md`](90_record/08_verification_baseline_0.4.0.md) | Verification Baseline — Release 0.4.0 |
| [`09_verification_baseline_0.5.0.md`](90_record/09_verification_baseline_0.5.0.md) | Verification Baseline — Release 0.5.0 |
| [`10_backlog_state_narrative_to_2026-08-16.md`](90_record/10_backlog_state_narrative_to_2026-08-16.md) | Backlog "Current state" narrative — archived 2026-08-16 |
| [`11_completed_development_to_0.5.0.md`](90_record/11_completed_development_to_0.5.0.md) | Completed Development — archive to 0.5.0 |
| [`12_verification_baseline_0.6.0.md`](90_record/12_verification_baseline_0.6.0.md) | Verification Baseline — Release 0.6.0 |
| [`35_completed_development_to_0.6.0.md`](90_record/35_completed_development_to_0.6.0.md) | Completed Development — archive to 0.6.0 |
| [`36_verification_baseline_0.7.0.md`](90_record/36_verification_baseline_0.7.0.md) | Verification Baseline — Release 0.7.0 |
| [`37_completed_development_to_0.7.1.md`](90_record/37_completed_development_to_0.7.1.md) | Completed Development — archive to 0.7.1 |
| [`41_completed_development_to_0.8.0.md`](90_record/41_completed_development_to_0.8.0.md) | Completed Development — archive to 0.8.0 |
| [`44_backlog_state_narrative_to_2026-08-29.md`](90_record/44_backlog_state_narrative_to_2026-08-29.md) | Backlog state narrative & superseded re-cut preambles, to 2026-08-29 |
| [`49_git_flow_guide_to_2026-08-16.docx`](90_record/49_git_flow_guide_to_2026-08-16.docx) | 49_git_flow_guide_to_2026-08-16 |
| [`51_completed_development_to_0.8.1.md`](90_record/51_completed_development_to_0.8.1.md) | Completed Development — archive to 0.8.1 |
| [`59_completed_development_to_0.8.2.md`](90_record/59_completed_development_to_0.8.2.md) | Completed Development — archive to 0.8.2 |
| [`62_completed_development_to_0.8.3.md`](90_record/62_completed_development_to_0.8.3.md) | Completed Development — archive to 0.8.3 |
| [`67_completed_development_to_0.8.6.md`](90_record/67_completed_development_to_0.8.6.md) | Completed Development — archive to 0.8.6 |
| [`CHANGELOG.md`](90_record/CHANGELOG.md) | Changelog |
| [`CHANGELOG_to_0.8.2.md`](90_record/CHANGELOG_to_0.8.2.md) | Changelog archive — releases up to and including 0.8.2 |
| [`CHANGELOG_to_0.8.3.md`](90_record/CHANGELOG_to_0.8.3.md) | Changelog archive — releases up to and including 0.8.3 |
| [`CHANGELOG_to_0.8.7.md`](90_record/CHANGELOG_to_0.8.7.md) | Changelog archive — releases up to and including 0.8.7 |
| [`README.md`](90_record/README.md) | `90_record/` — the record |

## 50_reviews — Process reviews

| File | Title |
|------|-------|
| [`PROJECT_REVIEW_2026-07-19.md`](50_reviews/PROJECT_REVIEW_2026-07-19.md) | FAR23LOADS — Critical Project Review |
| [`CODE_REVIEW_2026-07-21.md`](50_reviews/CODE_REVIEW_2026-07-21.md) | Critical Code & Documentation Review — 2026-07-21 |
| [`2026-11-01_critical_review_physics_atr42_docs.md`](50_reviews/2026-11-01_critical_review_physics_atr42_docs.md) | Critical review — physics, ATR 42 capability, user documentation, issue priority |
| [`2026-10-17_weight_mass_page_review.md`](50_reviews/2026-10-17_weight_mass_page_review.md) | Weight & Mass Properties page — critical review (2026-10-17) |
| [`2026-09-09_ga6_atr42_concept_capability_review.md`](50_reviews/2026-09-09_ga6_atr42_concept_capability_review.md) | 2026-09-09 — GA6 + ATR-42 concept capability review (both GUIs) |
| [`2026-09-08_oracle_report_gui_csv_review.md`](50_reviews/2026-09-08_oracle_report_gui_csv_review.md) | 2026-09-08 — Oracle GUI, oracle report and sectional-CSV review |
| [`2026-09-04_project_review.md`](50_reviews/2026-09-04_project_review.md) | sloads Project Review — 2026-09-04 |
| [`2026-08-27_oracle_gui_production_review.md`](50_reviews/2026-08-27_oracle_gui_production_review.md) | Oracle GUI production-release review (milestone 0.8.0) |
| [`2026-08-24_oracle_gui_code_review.md`](50_reviews/2026-08-24_oracle_gui_code_review.md) | Oracle GUI code review + backlog re-cut (milestone 0.7.2) |
| [`2026-08-23_c210_oracle_gui_build_review.md`](50_reviews/2026-08-23_c210_oracle_gui_build_review.md) | Cessna 210 from blank — oracle GUI build review (milestone 0.7.1) |
| [`2026-08-22_pre_cut_beta_review.md`](50_reviews/2026-08-22_pre_cut_beta_review.md) | Pre-cut beta review — the oracle GUI's function end-to-end (2026-08-22) |
| [`2026-08-22_backlog_review_0_7_0_beta.md`](50_reviews/2026-08-22_backlog_review_0_7_0_beta.md) | Backlog review before the 0.7.0 cut — the beta scope re-cut (2026-08-22) |
| [`2026-08-20_critical_review.md`](50_reviews/2026-08-20_critical_review.md) | Critical review — Oracle GUI, core analysis, above-oracle layer, main GUI & CI (2026-08-20) |
| [`2026-08-17_constants_and_conversions_review.md`](50_reviews/2026-08-17_constants_and_conversions_review.md) | Constants and conversion factors — ownership review (2026-08-17) |
| [`2026-08-17_backlog_review_0_7_0.md`](50_reviews/2026-08-17_backlog_review_0_7_0.md) | Backlog review after the 0.6.0 cut — the 0.7.0 re-cut (2026-08-17) |
| [`2026-08-16_scope_and_deficiency_review.md`](50_reviews/2026-08-16_scope_and_deficiency_review.md) | Scope and deficiency review — the code base and the open backlog (2026-08-16) |
| [`2026-08-16_gui_user_review.md`](50_reviews/2026-08-16_gui_user_review.md) | User GUI review |
| [`2026-08-15_review_0_6_0_candidate.md`](50_reviews/2026-08-15_review_0_6_0_candidate.md) | Critical review — the 0.6.0 candidate (2026-08-15) |
| [`2026-08-10_code_review_0_5_0.md`](50_reviews/2026-08-10_code_review_0_5_0.md) | Critical code review — path to 0.5.0 (2026-08-10) |
| [`2026-08-05_development_process_review.md`](50_reviews/2026-08-05_development_process_review.md) | Development Process Review — 2026-08-05 |

## 60_guide — Oracle GUI user guide

Structure per design note 34 ([`25_notes/34_oracle_user_guide_note.md`](25_notes/34_oracle_user_guide_note.md), decisions UG-1…UG-12): chapters follow `sloads.workflow.oracle_steps()` order; per-page field tables and the chapter list live under `60_guide/_generated/` (written by `docs/generate_data_dict.py`, never hand-edited); screenshots in `60_guide/img/` come from `scripts/capture_guide_shots.py`. Gates G-UG-1…G-UG-6: `tests/test_guide.py`.

| File | Title |
|------|-------|
| [`00_index.md`](60_guide/00_index.md) | Oracle GUI User Guide |
| [`01_configuration_layout.md`](60_guide/01_configuration_layout.md) | 1. Geometry |
| [`01_getting_started.md`](60_guide/01_getting_started.md) | Getting started |
| [`02_before_you_start.md`](60_guide/02_before_you_start.md) | Before you start |
| [`02_weight_mass.md`](60_guide/02_weight_mass.md) | 2. Weight & Mass Properties |
| [`03_aero_coefficients.md`](60_guide/03_aero_coefficients.md) | 3. Aerodynamic Data |
| [`03_conventions.md`](60_guide/03_conventions.md) | Conventions |
| [`04_structural_speeds.md`](60_guide/04_structural_speeds.md) | 4. Structural Speeds |
| [`05_flight_envelope.md`](60_guide/05_flight_envelope.md) | 5. Flight Envelope (V-n) |
| [`06_wing_loads.md`](60_guide/06_wing_loads.md) | 6. Wing Loads |
| [`07_fuselage_loads.md`](60_guide/07_fuselage_loads.md) | 7. Fuselage Loads |
| [`08_tail_loads.md`](60_guide/08_tail_loads.md) | 8. Tail Loads |
| [`09_aileron_loads.md`](60_guide/09_aileron_loads.md) | 9. Aileron Loads |
| [`10_flap_loads.md`](60_guide/10_flap_loads.md) | 10. Flap Loads |
| [`11_tab_loads.md`](60_guide/11_tab_loads.md) | 11. Tab Loads |
| [`12_engine_mount.md`](60_guide/12_engine_mount.md) | 12. Engine Mount Loads |
| [`13_one_engine_out.md`](60_guide/13_one_engine_out.md) | 13. One Engine Out |
| [`14_landing_loads.md`](60_guide/14_landing_loads.md) | 14. Landing Loads |
| [`A_worked_single.md`](60_guide/A_worked_single.md) | Appendix A — Worked example: the single (`ga6_normal`) |
| [`B_worked_twin.md`](60_guide/B_worked_twin.md) | Appendix B — Worked example: the twin (`baron_58`) |
| [`C_troubleshooting.md`](60_guide/C_troubleshooting.md) | Appendix C — Troubleshooting |
| [`D_where_next.md`](60_guide/D_where_next.md) | Appendix D — Where next |

---

> Root-level docs live outside `docs/`: [`../README.md`](../README.md) (user
> front page), [`../CONTRIBUTING.md`](../CONTRIBUTING.md) (the human on-ramp),
> [`90_record/CHANGELOG.md`](90_record/CHANGELOG.md) (release notes — `[Unreleased]`
> is generated from [`../changes/`](../changes/README.md) fragments at release cut), and
> [`../CLAUDE.md`](../CLAUDE.md) (guidance for Claude Code). The authoritative
> theory/oracle PDFs live in [`../reference/`](../reference/), alongside the
> **CFR/AC text extracts** cited by the calc and the F25 gap analysis —
> `14CFR_factor_of_safety.md`, `14CFR_operating_limitations.md`,
> `14CFR_MC_MD_speed_margin.md`, `14CFR_Part25_engine_torque.md`,
> `AC_23-19A_engine_torque.md`, `23_427_unsymmetrical_candidate_set.md`, and
> `fuselage_pitching_moment.md`.
