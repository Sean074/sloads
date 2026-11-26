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

**Early structural loads for FAR 23 and FAR 25 airplanes, delivered to a stress
team as a documented report and a standard NASTRAN deck** (restated 2026-11-21,
#435; the 2026-08-05 sbeam-loop statement it replaces is in the issue). sloads
takes a project file whose origin it does not care about (sconfig, a user, a
seed) and delivers two things: a fully documented loads report — every case, its
basis, its safety factor **stated per case and applied nowhere** (note 49
OR-116; note 58 D-58.1: delivery stays LIMIT permanently), its validation
record — and the loads as **NASTRAN bulk data on the LRA beam model**: standard
cards only, read by pyNastran as the conformance gate, solvable in any
NASTRAN-format beam solver (sbeam is the one in CI, with verified global
equilibrium). The FAR 23 core stays oracle-locked to Appendix A (±0.1 %); the
FAR 25 basis is a superset selected per project. Long term: toward near-final
loads for FAR 23 airplanes (band D). The primary model is still the **full-span
balanced free-free airplane** (2026-08-08; plan 11 §2 B-1…B-8, plan 12 C-1…C-6,
note 24 BM-1…BM-5). Items are tagged **[E]** (essential to a delivery) or **[V]**
(valuable, not blocking). **Definition of done** for a calc step: module merged
and self-registered; `tests/test_<module>.py` passing (±0.1 % oracle where
printed, else a stated closure gate in CI, benchmark-first); a page in
`workflow.py`; the `Project` schema round-trips with `SCHEMA_VERSION` bumped and
older files loading; docs synced per the closure tier.

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
| **B13 — 0.12.0: the two contracts and the validation record (re-cut 2026-11-21, #435; no physics)** ||||||
| 1 | **The exported deck is standard NASTRAN bulk data: MASSSET retired for a standard mass-case construction, pyNastran cross-parse in CI, sbeam pin bumped to v0.4.0** (#436) | Design note amending note 56 at AGREED first; the writers changed; pyNastran reads every exported deck with field agreement; `pytest -m roundtrip` green on the new pin; #400 closes on the first green weekly run | E | L / M | design note; sbeam v0.4.0 tagged |
| 2 | **Document the project-file schema** (#348) | The design note, then the document and the generator; #355's schema is its generated half | V | L / M | design note first |
| 3 | **Publish the project JSON Schema with each release** (#351) | `RELEASE_PROCESS.md` §4 gains the step; the published file equals the generated schema | V | S / S | #348, #355 |
| 4 | **No readable validation matrix; the last verification baseline is 0.7.0 (review D-2)** (#413) | A generated VALIDATION.md and the baseline step restored at release cut; the scope page (D-3) shipped as #431 | V | M / M | #304 |
| 5 | **Every oracle-locked module needs an independent physics closure beside its printed figure; the oracle cannot see a source error (review §1.2, the #401 class)** (#406) | A closure gate per oracle-locked module, recorded in module_gates.py, and a guard refusing a module with an oracle alone | E | M / M | #401 (G-72.1 is the first) |
| 6 | **R-4's tolerance class is suite-wide, not `test_structural_speeds`'s alone** (#304) | Each site read and tightened or justified on its line; then the structural half — a guard refusing a tolerance looser than the file's stated band without a reason on the line | V | M / M | — |
| 7 | **One full CI run per release, not two** (#434) | The release workflow runs the suite once; the tag job reuses the result | V | S / S | — |
| **B14 — 0.13.0: the ATR on its Part 25 basis (re-cut 2026-11-21, #435)** ||||||
| 8 | **F25-1: the transport gust and manoeuvre envelope: VB and the 66 fps line, the 25.337 n₁ check, VC ≥ VMO (review A-1)** (#410) | Design note at AGREED, then VB, the VB gust line, the n₁ and VC checks, and the ATR fixtures re-derived on the transport basis | E | L / L | design note |
| 9 | **F25-4: the Part 25 landing variant: L = 1.0, 6 fps at MTOW, the LDW/MTOW pairing (review A-1)** (#411) | The 25.473 case set beside the Part 23 one, selected by basis, with the pairing stated per case and a closure gate on the energy balance at each weight | E | M / M | #401 |
| 10 | **The remaining Part 25 gaps for an ATR-class airplane: per-wheel loads, 25.343(b), transport MFC, 25.351 overswing, 25.345 flaps-down (review §2)** (#412) | Each gap measured and ranked by rule 6, then split into its own step or parked with its number | V | M / M | F25-1 |
| 11 | **25.341 dynamic gust: rank the tuned and PSD omission by rule 6** (#432) | The tuned-gust-to-Pratt ratio measured or cited for an ATR-class wing and fin, then ranked or parked with its number; the gap analysis and the scope page cite it | V | M / M | #410 |
| 12 | **25.349(a) zero-g rolling condition, selected and released through SELECT to the wing cases** (#437) | Design note 77 (AGREED 2026-11-25), then the zero-g steady-roll points on the Part 25 basis, their own wing slot, and an end-to-end gate that every slot SELECT delivers reaches the released wing cases | E | L / M | #410 |
| 13 | **Steady roll, up-going aileron side: the nose-up wing torsion case** (#438) | Design note 78 (AGREED 2026-11-25), then an up-aileron steady-roll wing slot with the per-basis up deflection schedule and the note 77 pass-through guards | E | L / M | #437 |
| 14 | **Accelerated roll 100/75 as two wing loads on the full airplane, reacted by the whole airplane's roll inertia** (#440) | The per-side wing air factor in the balanced case with the lumped couple retired, one whole-airplane roll acceleration for wing chain and deck, both hands, and the interface loads stated in the report | E | L / M | — |
| 15 | **25.349(b) unsymmetrical gust, 100/80: a released wing case and a full-airplane balanced case, both hands** (#439) | Design note 79 (AGREED 2026-11-26), then the positive and negative 100/80 gust as wing slots and as handed full-airplane cases with a per-side wing factor, stated in the report | E | L / L | #410, #437, #440 |
| 16 | **AIRLOADS produces no flaps-down span load (OR-53)** (#163) | The cosine fairing across the flap discontinuity (Ref 1 p47) and a flaps-down span load, with the ATR given a flaps-down coefficient set | V | L / L | #412 (25.345 ranked) |
| 17 | **Wing fuel (and any tank/store band) is a point mass in WINGINER** (#111) | the per-side tank item row (note 63 D-63.4, `carriage` POINT) gains a spanwise extent (`y_span`) folded into the per-strip density `w[i]`, reducing exactly to today's point when the band collapses — **not** a `WingMassInput` field, which D-63.2 empties of mass; Appendix A oracle case (concentrated gear only) untouched, lock holds. Interim: N item rows across the tank span with the same centroid — root bending and total shear identical | V | L / M | #289 and #292 shipped 2026-09-18 with the per-tank rows; **the park condition note 63 §6 set was never met** — the ATR point-vs-band number was not measured, and the metric it named (root bending) is zero by construction for a band with the same centroid. First deliverable is the tier-S measurement: mid-tank-band station shear and bending on `atr42_100`, point vs band, against the Schrenk 5–10 % datum; then rank or park on that number; design note first (physics/L) |
| 18 | **Directional stability and the body's share on the Aerodynamic Data page** (#390) | The page block, the flag primary, the OEI sensitivity term off by default; note 33's section | V | M / M | #226's number |
| 19 | **Documentation for a reviewer: ch11 deck walk-through and the stub chapters, reference access, the twin checkpoint table, results-affecting changelog, register magnitudes, fixture provenance (review D-4, D-7, D-9…D-13)** (#414) | ch11 written, then ch08 and a control-surface chapter; the reference-access section; D-9…D-13 each closed | V | M / L | #401 (ch08) |
| **C — 1.0.0: early loads, FAR 23 and FAR 25, documented (re-described 2026-11-21, #435; gate: a colleague runs a GA6 and an ATR-class case from the README in an afternoon and finds the validation record for any number in a minute)** ||||||
| 20 | **sconfig R2: Accept a seed (partial) project and derive the rest on load** (#349) | The input contract completed for any writer: CG cases, derived fields and validation derived on load; design note first | V | L / M | #348 |
| 21 | **sconfig R3: Migrate every published schema version, seed projects included** (#350) | Every published schema version loads and migrates; seeds included; sconfig never migrates | V | M / M | #348, #351 |
| 22 | **One Mach-correction owner for wing and tail, finite-wing form; the downwash constant 36 → 36.48 (review P-4)** (#415) | A single compressibility owner used by FLTLOADS and SELECT, with a guard that no module scales a slope on its own | V | M / M | — |
| 23 | **Appendix A printed results with no home in the report and no registered exclusion** (#246) | Each added or registered as an exclusion beside the others, walked with the owner | V | M / S | owner decisions |
| 24 | **The load-case index carries no loads for 344 of 347 rows** (#209) | A decision on what the file is, then the columns to match it — the candidate being that it becomes an index in name as well as in fact, with the per-element files carrying the loads. D-56.1 moved the case index into `report/tables.py`; its six load columns still come from `report/render.py`'s `load_cases_to_rows` and the file itself from `io.py`'s `load_cases_csv`, so the decision touches three owners | V | M / M | a decision on the file's purpose |
| 25 | **The oracle prints an aileron deflection schedule the module does not publish** (#305) | One `LoadValue` per deflection on `AileronResult`, the p200 figures as the oracle (±0.1 %), §7 printing them | V | M / S | — |
| 26 | **Split the four maintainability-index-0 modules** (#398) | `oracle_sections.py`, `io.py`, `mass_distribution.py`, `validation.py` split with every gate value unchanged | V | M / M | — |
| 27 | **Calc-side function size (CH-8)** (#17) | Split when touched; the view functions wait for the page-by-page GUI reviews. `_manifest_rows` 131, `landing_reactions` 276, `envelope` 195, `build_tail_span` 176 and the three `balance` assemblers stand | V | S / S | — |
| 28 | **mypy strictness ratchet** (#19) | `sloads.export.*`, `sloads.io`, then `sloads.modules.*` added to the `[[tool.mypy.overrides]]` list and narrowed to zero under ST-4; then `warn_return_any`/`disallow_any_generics` toward `--strict` | V | S / S per stage | — |
| 29 | **The calc-purity contract is prose plus scattered guards** (#357) | Verify no equivalent gate exists (close as no-op if one does); else an AST test over `sloads/`: no `streamlit`/`app_shell`/`oracle_app` import, no I/O outside `io.py`/`report/`/`export/`, new modules layer-assigned | V | S / S | — |
| 30 | **`PROGRAM_SPEC.md`'s per-module I/O tables are hand-written and can go stale with CI green** (#358) | The inputs/outputs tables generated from the code-owned field registry and result keys, with a regenerate-and-compare drift guard; prose stays hand-written | V | M / M | — |
| 31 | **`solo_close.sh` verifies fragment existence, not tier content** (#185) | The preflight enforcing the checkable closure obligations and validating the subject it writes | V | M / M | — |
| 32 | **130 test files carry a `sys.path.insert` shim** (#340) | Every shim deleted and a guard in `test_ci_conformance.py` refusing one | V | S / S | — |
| 33 | **The 0.8.8 structural gates have five probed blind spots** (#345) | Each gate widened to its blind spot, with the synthetic violation as its test | V | S / S | — |
| 34 | **Test-debt remainder from the 0.8.8 pre-release review** (#346) | The VC rows pinned, the decorator removed, the three patterns made exact | V | S / S | — |
| 35 | **Whole-pipeline-per-assertion tests, re-aimed at the coverage leg** (#92) | The repeated-pipeline shape gone from the coverage leg's `--durations`; the local command stays the clause's datum. **No `slow` marker** — `00_program_overview.md` §Testing states why | V | S / S–M | — |
| 36 | **The oracle form reaches into a `field_registry` private** (#130) | `field_registry` exposes the lookup publicly and `row_class` calls it; the private stays private | V | S / S | when `field_registry` is next touched |
| 37 | **Review 2026-08-10 unscheduled findings m3–m13, m15–m18 + NITs** (#18) | Swept opportunistically (practice 4) or promoted individually | V | S / S–M | — |
| 38 | **D-5 — Appendix B twin fixture (blocks parked L-9)** (#20) | The decision recorded; the fixture built or the exclusion registered | E | M / M | owner decision |
| 39 | **Mach-capped balanced points publish past-fit extrapolated coefficients with no marking** (#32) | The extrapolated points marked in every output that carries them | V | M / M | — |
| **D — 2.0.0: toward near-final FAR 23 loads (given a meaning 2026-11-21, #435; design note and a named consumer before any item starts)** ||||||
| 40 | **No inbound channel for an externally computed load distribution** (#279) | An agreed import contract, the channel, and the imported-against-computed overlay as its first consumer | V | L / M | a design note at AGREED first |
| 41 | **The aileron's own lift increment is not distributed** (#14) | `ACRL` wing cards gain the aero half of the couple (~70 % span); the schema fields shipped v52 and wait for data and a consumer | V | L / M | only if a consumer sizes to `ACRL` |
| 42 | **Ground-case fuselage station distribution** (#31) | Per-station shear/bending/torsion for the ground family on the fuselage beam, its own envelope beside the flight one and never merged with it, each station naming its ground case | V | L / M | a frame-sizing consumer; design note first |
| 43 | **Aileron hinge moment: integrate the hinge moment for every wing load case and for the two AILERON pressure cases** (#375) | The hinge moment per case beside the aileron loads, with its oracle or closure gate | V | L / M | design note first |
| 44 | **Sourced windmilling-propeller drag at the fine-pitch limit (ESDU, Torenbeek Ref. G-100) (review A-3 remainder)** (#421) | The sourced drag replacing the placeholder, ranked by rule 6 against the OEI yaw case | E | M / M | design note first |
| 45 | **Per-tank fuel burn order for the corner solver, fuel vector and G-5 burn-down (note 76 Q3)** (#425) | The burn order as a project field, the corner solver and G-5 honouring it | V | L / M | note 76 |
