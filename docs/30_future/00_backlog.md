# Backlog — Open Work & Development Plan

The authoritative list of **open** items, mission-tagged, in one order — the
**priority table** below; item bodies follow it. Rules of the road (closure
tiers, definition of done, the removal rule, naming) are in
[`../../CLAUDE.md`](../../CLAUDE.md) and restated once above the table; they
are not repeated here. Off-mission items live in [`02_parked.md`](02_parked.md);
completed work in [`../90_record/00_completed_development.md`](../90_record/00_completed_development.md)
and [`90_record/CHANGELOG.md`](../90_record/CHANGELOG.md); the pre-2026-08-16 running
"current state" narrative is archived in
[`../90_record/10_backlog_state_narrative_to_2026-08-16.md`](../90_record/10_backlog_state_narrative_to_2026-08-16.md).
Narratives and plans: [`01_concept_loads_plan.md`](01_concept_loads_plan.md)
(concept mode), [`03_gui_rework_plan.md`](03_gui_rework_plan.md) (GUI),
design notes per step ([`../00_INDEX.md`](../00_INDEX.md) is the guarded index
of the live set — no list is kept here; every note, whatever its status,
lives in [`../25_notes/`](../00_INDEX.md) and keeps its number (note 61 CV-3;
the status-driven move at each cut is retired); the pre-2026-08-29 "where
things stand" narrative and superseded re-cut preambles are in
[`../90_record/44_backlog_state_narrative_to_2026-08-29.md`](../90_record/44_backlog_state_narrative_to_2026-08-29.md)); architecture
[`../10_standard/PROJECT_GUIDE.md §7`](../10_standard/PROJECT_GUIDE.md); per-module
spec [`PROGRAM_SPEC.md`](../10_standard/PROGRAM_SPEC.md).

> **Invariant:** no calc-math change to the FAR23 path — Appendix A oracles pass
> throughout; concept mode reduces exactly to FAR23 on GA inputs; ultimate-load
> output rules hold; `workflow.py` stays the single source of navigation truth.

## Mission

**A demonstrated concept-loads → sbeam sizing loop** (2026-08-05): a concept
configuration goes in, distributed **LIMIT** loads come out as `FORCE`/`MOMENT`
cards (the 23.303 factor stated per subcase and applied nowhere — note 49
OR-116, confirmed by note 58 D-58.1: delivery stays LIMIT permanently, and
comparisons between cases are made on the ultimate basis), and the exported deck solves in sbeam with verified global equilibrium,
continuously in CI; the FAR23 core stays oracle-locked. **Primary deliverable
(2026-08-08):** the **full-span balanced free-free airplane model** — mass
model exported (CONM2), wing/fuselage/empennage/landing cases carrying aero +
inertia, left/right twins by reflection, and an LRA beam model exported and
importable — decisions of record plan 11 §2 (B-1…B-8), plan 12 (C-1…C-6),
note 24 (BM-1…BM-5). **Order of work (2026-08-09):** the sbeam
`FORCE`/`MOMENT` cards for the wing, body and tail cases. Items are tagged
**[E]** (essential to the loop) or **[V]** (valuable, not blocking).
**Definition of done** for a calc step: module merged and self-registered;
`tests/test_<module>.py` passing (±0.1 % oracle where printed, else a stated
closure gate in CI, benchmark-first); a page in `workflow.py`; the `Project`
schema round-trips with `SCHEMA_VERSION` bumped and older files loading; docs
synced per the closure tier.

Reference-authority hierarchy: (1) `.BAS` listings + Appendix A printed output,
(2) User's Guide CFR quotes (Jan-1994), (3) Code-manual 1990 prose.

---

# Priority table (the single order of work)

**Ordering rules (cumulative):**

- *2026-08-09:* wrong cards outrank missing cards; [V] items are ranked, not
  opportunistic.
- *2026-08-16 — effect-vs-error-bar rule* — promoted to **`CLAUDE.md` rule 6**
  (the datum it measures against is
  [`../20_theory/00_theory_sources.md` §Base-method uncertainty](../20_theory/00_theory_sources.md#base-method-uncertainty)):
  a [V] item is ranked only if its stated effect exceeds that; below it, parked
  with the number. Defects with first-order effect on shipped content outrank
  every [V] item.
- *2026-08-16 — schema freeze through 0.6.0* (held: one hop, v53). *2026-08-17
  — 0.7.0:* lifted for exactly **one additive hop**, L-7's lateral inputs
  (off by default, note 19 L-7.3); any other field change in 0.7.0 rides that hop
  or waits for 0.8. v47 → v52 in nine days is the churn the rule answers.
  *2026-08-22 — 0.7.0 beta:* lifted for exactly **one hop**, #52's retirement
  of the two duplicate entries (v55) with a migration that takes the owner's
  value and warns on disagreement; anything else rides that hop or waits.


> **Removal rule (hard requirement, restating the lifecycle rule).** Once a
> step is complete it **SHALL be removed** from this table and this file in the
> same session, with its tiered closure trail. A closing change deletes **its
> own row and touches nothing else** — no renumbering (gaps in **Pri** are
> fine: it is the order at the last re-cut, not an ID; dense numbering returns
> only at a re-cut, which owns the whole table) — and rows never cite another
> row's ordinal (dependencies name the band or the `#N`), so two in-flight
> changes cannot conflict on this table (`DEVELOPMENT_PROCESS.md` §0).

**Frozen (review §3) — no further investment; tests and gates kept; touched
for defects only:** the FAR 23 core; the balanced assembler + handedness;
CONM2/MASSSET export; the sbeam round-trip harness; the ground/landing
families + gear report; the governing safety-factor table (Layer 2 parked);
distributed empennage loads, control surfaces, hinge moment, T-tail transfer;
the **LRA beam model at its determinate paths**; the summary report, PDF,
workbook, manifest and methods stamp; the GUI — `oracle_app/` + `app_shell/`, the one front-end since #270 —
pending the page-by-page GUI reviews (Geometry and Weight & Mass done 2026-10; the #29 umbrella re-scoped and closed 2026-10-18), whose findings decide what re-opens (the CLI is
the delivery path; the `app/views/`-only rows M4-11b and L-8b/c/e/f closed with
that tree on 2026-09-14; parked **L-8d**'s keyed data-loss half shipped 2026-08-21 as #51 —
`app_shell/widget_keys.py` — and its unkeyed half shipped 2026-08-22, closing
#51's reopen as one pass with #44's unit-boundary rollout: that pass consumed
**the one carve-out from this freeze** — `key=` plus the boundary helper at
exactly those call sites, no layout/behaviour rework — so the freeze is whole
again; L-8d's mutation case stays parked); F25-2.


**The table is a generated view of the open issues** (#359): one row per
issue, `| Pri | **title** (#N) | what ships | tag | tier / effort | depends |`,
regenerated by `scripts/backlog_issues.py render` (run by `solo_close.sh` at
every close) and held to the issues by `backlog_issues.py check`. The body is the
issue; nothing lives below the table. A re-cut renumbers the table in its own
tier-S commit and states its reasoning in the milestone description.

| Pri | Item (detail below / in its plan) | What ships | Tag | Tier / effort | Depends on |
|---|---|---|---|---|---|
| **B11 — 0.10.0: loads correctness on the Part 23 method, for ATR-sized airplanes (re-chartered 2026-11-01 after the physics review)** ||||||
| 4 | **The Python 3.12 requirement is invisible to a new clone** (#395) | README install section and `pyproject.toml` state 3.12 up front with the one-line reason; the refusal message points at it; no change to the policy | E | S / S | — |
| 5 | **README: quickstart first, phase narrative after** (#394) | The first screen is install (one command), run the GUI, run one CLI case, where the guide lives; the narrative moves below or into `docs/` | E | S / S | #395 |
| 6 | **Ten tags, no wheel, no GitHub release** (#396) | A release workflow (or a documented manual step) that builds the wheel on tag and attaches it to a GitHub release with that version's changelog section; v0.9.0 first, retroactively | E | S / S | — |
| 7 | **One clean install on another machine from the README alone** (#397) | On a machine that has never seen sloads (the Mini counts), follow the README on macOS and on Windows, run the GUI and one CLI case, file each break as its own issue | E | S / S | #394, #395, #396 |
| 8 | **The ATR 42-300 seed fixture's input errors and its round-trip failures, before it is committed (review A-4, T-1)** (#403) | Seed corrected per the table with sources, registered in the fixture guards, the round-trip failures diagnosed and fixed at their cause, suite green with the seed committed | E | S / M | #401 (N cleared per note 72 Q3) |
| 9 | **`atr42_100`'s `tread_in` is 150 in against the published 161.4 in** (#399) | `tread_in` 161.4 [A] with its source line, or the reason 150 is kept recorded beside it | E | S / S | — |
| 10 | **`baron_58` has no minimum-crew row** (#337) | The Baron's crew as a `MINIMUM` row, the minimum weight and the affected cases re-derived, and a guard that every fixture's minimum loading carries a crew | E | S / S | — |
| 11 | **Balanced cases run past the elevator stop, tail stall and fin stall with no flag (review A-2; absorbs #353)** (#404) | Per-case feasibility flags (elevator stop, h-tail α, fin α) on every balanced family, shown in the report and the deck, with a guard test | E | M / M | #401 |
| 12 | **OEI basis for feathering turboprops: windmill drag default, feather/autofeather, VMC–VD sweep, a distinct 23.367(a)(2) (review A-3, P-3)** (#405) | Design note at AGREED, then the feathering drag basis, the speed sweep and the (a)(2) schedule, with the ATR's governing fin case re-derived | E | L / L | design note; #353 class via the feasibility issue |
| 13 | **The flight balance models no thrust — the thrust-line re-trim, ranked by its number** (#226) | Note 21 §10 at AGREED (owner Q1–Q5), then one tier-L step: the policy table and `-P` identity (P-4/P-12, one additive schema hop), the thrust term in `_balance` with `nx = −(DX − ΣT)/W` and the `NX`/`T` columns, the h-tail `-P` families (P-11), the body beam's axial column (P-16, #218) and the entered line's direction (P-17, #217 — or parked with its number); the DATCOM slipstream estimator stays parked | V | L / L | note 21 §10 AGREED; re-tiered S → L 2026-10-27, the measurement done |
| 14 | **The weekly sbeam-drift gate against sbeam `main` is red** (#400) | The pin bumped per `PROJECT_GUIDE.md` "The `solver` extra and the sbeam pin", its step 3 (`pytest -m roundtrip` green before the bump is committed); the issue closes itself on the first green weekly run | V | S / S | — |
| 15 | **Every oracle-locked module needs an independent physics closure beside its printed figure; the oracle cannot see a source error (review §1.2, the #401 class)** (#406) | A closure gate per oracle-locked module, recorded in module_gates.py, and a guard refusing a module with an oracle alone | E | M / M | #401 (G-72.1 is the first) |
| 16 | **Appendix A page citations are wrong in six places, and three printed figures are compared with no page cited** (#371) | Each citation corrected against the printed page footers, the three figures given their page | V | S / S | — |
| 17 | **Reference 1 is cited without its grant and report numbers, and the report says Appendix B is "not bundled" when the available copy lacks it** (#373) | The full citation (Grant 93-G-051, DOT/FAA/AR-96/46) in the theory sources and the report; Appendix B stated as absent from the available copy | V | S / S | — |
| 18 | **Checked-manoeuvre pitch acceleration uses +39 for both directions; the 23.423 lineage has −26 nose-down (review P-2, confirm the text first)** (#407) | The regulation text transcribed and cited; the value kept-conservative with its number or corrected as an approved deviation | V | S / S | — |
| 19 | **Gyroscopic thrust basis: labelled max-continuous, computed from takeoff torque at 100 % efficiency, above the ideal-disc limit on the ATR (review P-6)** (#408) | Thrust from max-continuous power with η (or the ideal-disc cap), the label fixed, an ideal-disc closure gate | V | S / S | — |
| 20 | **DATA_DICTIONARY.md is broken: the generator swallows its exception and has not followed models/ becoming a package (review D-6)** (#409) | The generator fixed and failing loudly, the file regenerated, a guard that every input dataclass has a complete table | V | S / S | — |
| 21 | **Directional stability and the body's share on the Aerodynamic Data page** (#390) | The page block, the flag primary, the OEI sensitivity term off by default; note 33's section | V | M / M | #226's number |
| **B12 — 0.11.0: the ATR on its Part 25 basis, the validation record and the sconfig contract (opened 2026-11-01)** ||||||
| 22 | **F25-1: the transport gust and manoeuvre envelope: VB and the 66 fps line, the 25.337 n₁ check, VC ≥ VMO (review A-1)** (#410) | Design note at AGREED, then VB, the VB gust line, the n₁ and VC checks, and the ATR fixtures re-derived on the transport basis | E | L / L | design note |
| 23 | **F25-4: the Part 25 landing variant: L = 1.0, 6 fps at MTOW, the LDW/MTOW pairing (review A-1)** (#411) | The 25.473 case set beside the Part 23 one, selected by basis, with the pairing stated per case and a closure gate on the energy balance at each weight | E | M / M | #401 |
| 24 | **The remaining Part 25 gaps for an ATR-class airplane: per-wheel loads, 25.343(b), transport MFC, 25.351 overswing, 25.345 flaps-down (review §2)** (#412) | Each gap measured and ranked by rule 6, then split into its own step or parked with its number | V | M / M | F25-1 |
| 25 | **AIRLOADS produces no flaps-down span load (OR-53)** (#163) | The cosine fairing across the flap discontinuity (Ref 1 p47) and a flaps-down span load, with the ATR given a flaps-down coefficient set | V | L / L | #412 (25.345 ranked) |
| 26 | **Wing fuel (and any tank/store band) is a point mass in WINGINER** (#111) | the per-side tank item row (note 63 D-63.4, `carriage` POINT) gains a spanwise extent (`y_span`) folded into the per-strip density `w[i]`, reducing exactly to today's point when the band collapses — **not** a `WingMassInput` field, which D-63.2 empties of mass; Appendix A oracle case (concentrated gear only) untouched, lock holds. Interim: N item rows across the tank span with the same centroid — root bending and total shear identical | V | L / M | #289 and #292 shipped 2026-09-18 with the per-tank rows; **the park condition note 63 §6 set was never met** — the ATR point-vs-band number was not measured, and the metric it named (root bending) is zero by construction for a band with the same centroid. First deliverable is the tier-S measurement: mid-tank-band station shear and bending on `atr42_100`, point vs band, against the Schrenk 5–10 % datum; then rank or park on that number; design note first (physics/L). The measurement runs in B2 time, after #226's (B2 re-order 2026-10-19); the physics stays in C |
| 27 | **No readable validation matrix (last baseline 0.7.0) and no scope-and-applicability page (review D-2, D-3)** (#413) | A generated VALIDATION.md, the baseline step restored at release cut, one scope page stating which way each omission errs | V | M / M | #304 |
| 28 | **R-4's tolerance class is suite-wide, not `test_structural_speeds`'s alone** (#304) | Each site read and tightened or justified on its line; then the structural half — a guard refusing a tolerance looser than the file's stated band without a reason on the line | V | M / M | — |
| 29 | **Documentation for a reviewer: ch11 deck walk-through and the stub chapters, reference access, the twin checkpoint table, results-affecting changelog, register magnitudes, fixture provenance (review D-4, D-7, D-9…D-13)** (#414) | ch11 written, then ch08 and a control-surface chapter; the reference-access section; D-9…D-13 each closed | V | M / L | #401 (ch08) |
| 30 | **Document the project-file schema** (#348) | The design note, then the document and the generator; #355's schema is its generated half | V | L / M | design note first |
| 31 | **Publish the project JSON Schema with each release** (#351) | `RELEASE_PROCESS.md` §4 gains the step; the published file equals the generated schema | V | S / S | #348, #355 |
| **C — 1.0.0: additional analysis capability (consumer-gated; design notes first)** ||||||
| 32 | **GUI validation warnings ignore the SI toggle** (#339) | Warnings rendered in the page's unit system, one owner for the conversion, and a guard over every warning code | V | M / M | — |
| 33 | **The calc-purity contract is prose plus scattered guards** (#357) | Verify no equivalent gate exists (close as no-op if one does); else an AST test over `sloads/`: no `streamlit`/`app_shell`/`oracle_app` import, no I/O outside `io.py`/`report/`/`export/`, new modules layer-assigned | V | S / S | — |
| 34 | **`PROGRAM_SPEC.md`'s per-module I/O tables are hand-written and can go stale with CI green** (#358) | The inputs/outputs tables generated from the code-owned field registry and result keys, with a regenerate-and-compare drift guard (the `DATA_DICTIONARY.md` posture); prose — meanings, FAR citations — stays hand-written | V | M / M | — |
| 35 | **`solo_close.sh` verifies fragment existence, not tier content** (#185) | The preflight enforcing the checkable closure obligations and validating the subject it writes | V | M / M | — |
| 36 | **Whole-pipeline-per-assertion tests, re-aimed at the coverage leg** (#92) | The repeated-pipeline shape gone from the coverage leg's `--durations`; the local command stays the clause's datum. **No `slow` marker** — `00_program_overview.md` §Testing states why | V | S / S–M | — |
| 37 | **The oracle form reaches into a `field_registry` private** (#130) | `field_registry` exposes the lookup publicly and `row_class` calls it; the private stays private | V | S / S | when `field_registry` is next touched |
| 38 | **The load-case index carries no loads for 344 of 347 rows** (#209) | A decision on what the file is, then the columns to match it — the candidate being that it becomes an index in name as well as in fact, with the per-element files carrying the loads. **Unchanged in substance by note 56**, but D-56.1 moved the case index out of the export bridge into `report/tables.py` (`case_index_rows`, `case_index_csv`) — arguably where a decision about what a *report* table is always belonged; its six load columns still come from `report/render.py`'s `load_cases_to_rows` and the file itself from `io.py`'s `load_cases_csv`, so the decision now touches three owners | V | M / M | note 44 §22 shipped; a decision on the file's purpose |
| 39 | **Appendix A printed results with no home in the report and no registered exclusion** (#246) | Each added or registered as an exclusion beside the others, walked with the owner at the start of 0.9.0 | V | M / S | owner decisions |
| 40 | **130 test files carry a `sys.path.insert` shim** (#340) | Every shim deleted and a guard in `test_ci_conformance.py` refusing one | V | S / S | — |
| 41 | **The 0.8.8 structural gates have five probed blind spots** (#345) | Each gate widened to its blind spot, with the synthetic violation as its test | V | S / S | — |
| 42 | **Test-debt remainder from the 0.8.8 pre-release review** (#346) | The VC rows pinned, the decorator removed, the three patterns made exact | V | S / S | — |
| 43 | **One Mach-correction owner for wing and tail, finite-wing form; the downwash constant 36 → 36.48 (review P-4)** (#415) | A single compressibility owner used by FLTLOADS and SELECT, with a guard that no module scales a slope on its own | V | M / M | — |
| 44 | **The aileron's own lift increment is not distributed** (#14) | `ACRL` wing cards gain the aero half of the couple (~70 % span); the schema fields shipped v52 and wait for data and a consumer | V | L / M | only if a consumer sizes to `ACRL` |
| 45 | **Ground-case fuselage station distribution** (#31) | Per-station shear/bending/torsion for the ground family on the fuselage beam, its own envelope beside the flight one and never merged with it, each station naming its ground case | V | L / M | a frame-sizing consumer; design note first |
| 46 | **Calc-side function size (CH-8)** (#17) | Split when touched; **the view functions wait for the page-by-page GUI reviews**. **Re-measured at note 56's close (2026-09-12), and the forecast was wrong in one half**: `_export_sbeam` was not deleted — it lost its per-component branches and stands at **53**, off this list; `_manifest_rows` is **131**, not the 155 this row carried; `landing_reactions` (276), `envelope` (195) and `build_tail_span` (176 — untouched, but its deck consumer is gone) stand, as do the three `balance` assemblers | V | S / S | — |
| 47 | **Review 2026-08-10 unscheduled findings m3–m13, m15–m18 + NITs** (#18) | Swept opportunistically (practice 4) or promoted individually | V | S / S–M | — |
| 48 | **mypy strictness ratchet** (#19) | `sloads.export.*`, `sloads.io`, then `sloads.modules.*` added to the `[[tool.mypy.overrides]]` list and narrowed to zero under ST-4; then `warn_return_any`/`disallow_any_generics` toward `--strict` | V | S / S per stage | — |
| 49 | **No inbound channel for an externally computed load distribution** (#279) | An agreed import contract, the channel, and the imported-against-computed overlay as its first consumer | V | L / M | a design note at AGREED first |
| 50 | **The oracle prints an aileron deflection schedule the module does not publish** (#305) | One `LoadValue` per deflection on `AileronResult`, the p200 figures as the oracle (±0.1 %), §7 printing them | V | M / S | — |
