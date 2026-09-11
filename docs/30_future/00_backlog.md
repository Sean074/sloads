# Backlog — Open Work & Development Plan

The authoritative list of **open** items, mission-tagged, in one order — the
**priority table** below; item bodies follow it. Rules of the road (closure
tiers, definition of done, the removal rule, naming) are in
[`../../CLAUDE.md`](../../CLAUDE.md) and restated once above the table; they
are not repeated here. Off-mission items live in [`02_parked.md`](02_parked.md);
completed work in [`../40_history/00_completed_development.md`](../40_history/00_completed_development.md)
and [`../../CHANGELOG.md`](../../CHANGELOG.md); the pre-2026-08-16 running
"current state" narrative is archived in
[`../40_history/10_backlog_state_narrative_to_2026-08-16.md`](../40_history/10_backlog_state_narrative_to_2026-08-16.md).
Narratives and plans: [`01_concept_loads_plan.md`](01_concept_loads_plan.md)
(concept mode), [`03_gui_rework_plan.md`](03_gui_rework_plan.md) (GUI),
design notes per step ([`../00_INDEX.md`](../00_INDEX.md) is the guarded index
of the live set — no list is kept here; shipped notes roll to
[`../40_history/`](../00_INDEX.md#40_history--historic-record) at each cut,
keeping their numbers; the pre-2026-08-29 "where
things stand" narrative and superseded re-cut preambles are in
[`../40_history/44_backlog_state_narrative_to_2026-08-29.md`](../40_history/44_backlog_state_narrative_to_2026-08-29.md)); architecture
[`../10_standard/PROJECT_GUIDE.md §7`](../10_standard/PROJECT_GUIDE.md); per-module
spec [`PROGRAM_SPEC.md`](../10_standard/PROGRAM_SPEC.md).

> **Invariant:** no calc-math change to the FAR23 path — Appendix A oracles pass
> throughout; concept mode reduces exactly to FAR23 on GA inputs; ultimate-load
> output rules hold; `workflow.py` stays the single source of navigation truth.

## Mission

**A demonstrated concept-loads → sbeam sizing loop** (2026-08-05): a concept
configuration goes in, distributed **LIMIT** loads come out as `FORCE`/`MOMENT`
cards (the 23.303 factor stated per subcase and applied nowhere — note 49
OR-116; #193 is the standing proposal to reverse this), and the exported deck solves in sbeam with verified global equilibrium,
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

# Priority table (re-cut 2026-08-29, second — the single order of work)

**Re-cut 2026-08-29 (owner, in session; the second of the day — the first, the
band B3 fold, is kept in
[`../40_history/44_backlog_state_narrative_to_2026-08-29.md`](../40_history/44_backlog_state_narrative_to_2026-08-29.md)
with the rest of the superseded preambles).** Two defects found the same day diagnosing the
GA6 V-n failure — **#143** (the oracle GUI attaches a phantom zero-coefficient
LANDING set on one stray touch, and saves it into the project file) and **#144**
(the calc side launders a zero lift polynomial into a 400-trip `SolverFailure`
instead of refusing it by name) — **enter band B1 ahead of the documentation
rows**, and the table is renumbered densely (a re-cut owns the table). Nothing
else moves. Two rulings:

1. **They are one defect class in two fix sites, and both are fixed.** The
   phantom set is the writer; the missing refusal is why it presents as an
   opaque solver hang on a page the user never edited. This is the #121/#122
   binding of the 2026-08-28 re-cut applied again — rule 4 does not permit
   fixing the GUI that writes the set and leaving the guard that should have
   named it, and #144's refusal belongs at the consumer for **every** writer,
   not only this one. **#144 goes first:** it is the smaller, self-contained
   half, and landing it makes #143's repro produce a named `MissingInputError`
   to verify against instead of a 400-iteration failure.
2. **They rank ahead of #141/#140/#142 on rule 6, not on their tag** — a defect
   with first-order effect on shipped content outranks every non-defect row
   regardless of mission trace. #143 is the inverse of the #51 data-loss class,
   silent data *gain* that persists into a saved `.project.json` and takes
   Flight Envelope and SELECT down with it: a released-artefact defect of
   exactly the kind band B1 exists to correct. **The `app/views/` freeze is
   untouched** — #143's fix site is `oracle_app/`, open since band A, and
   #144's is `sloads/modules/flight_envelope.py`, which the frozen list admits
   for defects. No calc-math change: the guard is a refusal, and the GA6 oracle
   and twin closure suites are unmoved by it.

**Cut 0.8.1 when band B1 is empty, then 0.9.0 when band B2 is** — unchanged.
*(0.8.1 cut 2026-08-29; band **B3** worked ahead of B2 and retired at the
**0.8.2 cut, 2026-09-08** — **band B4 (0.8.3) is the milestone in flight**,
unblocked by that cut's OR-13 freeze lift; then B2/0.9.0 as ruled.)*

**System of record (design note 28 MD-5, 2026-08-16):** open work is **GitHub
Issues** (labels `tier:*`, `tag:*`, `band:*`, `kind:*`; a milestone per release;
the Project board is the view). This file keeps the **plan** — mission,
definition of done, the reference hierarchy, and this table — and each row names
its issue as `(#N)` once `scripts/backlog_issues.py create` + `rewrite` have run
(owner, once); item bodies then live in the issues, a PR says `Closes #N`, and
`scripts/backlog_issues.py check` holds table ↔ open issues both ways. Until the
migration runs, bodies stay where they are — a defect promoted into the table
keeps its body in *Open defects*, and the [E]/[V] detail sections hold the rest.

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

**Review additions 2026-09-04 ([`../50_reviews/2026-09-04_project_review.md`](../50_reviews/2026-09-04_project_review.md);
an addition, not a re-cut — the
2026-08-29 order stands).** The full-project review filed #172–#191 and put the
open defect set on milestones. New rows are appended to their bands (Pri 26+),
and the old **band D** (maintenance, milestone-less) is dissolved: its rows now
carry the milestones the review's triage assigned and sit in those bands,
keeping their Pri numbers. Findings, evidence and the triage tables are in
[`../50_reviews/2026-09-04_project_review.md`](../50_reviews/2026-09-04_project_review.md);
the small tier-S defects are indexed under *Open defects* below.

**Milestone-open addition 2026-09-09 (an addition, not a re-cut — the standing
order holds; new rows append at Pri 46+).** The 0.8.3 plan review at milestone
open found the GitHub milestone carrying 24 open issues where band B4 held 7
rows — the 2026-09-08 review's filings (#239–#243), the note-44-era defects it
milestoned per their own bodies (#216, #219, #220, #222, #223), and the
2026-09-04 review's 0.8.3 assignments that never got rows (#161, #170, #175,
#176, #179, #180, #188). All 24 now carry `band:B4` labels (12 had none, which
is why `backlog_issues.py check`'s reverse leg never saw them) and every one has
a row below. The appended rows are ordered by the review's working sequence:
the cheap hygiene front, the safety-factor cluster (one session, one code
region), the tail-geometry cluster (#223's rename first, before the files it
renames are edited by the rest), then the baseline-regeneration wave (#164 →
#222 → #241 → #242 → #161, landed adjacently so digests and report baselines
regenerate in one wave, #161 last since it reformats what the others produce),
then polish. The three L-tier decision processes (#156 note, #172
refuse-vs-fix note, #164 measurement + case-set ruling) start first, in
parallel with the hygiene front, so implementation never blocks on an
unwritten note.

**Milestone-created addition 2026-09-11 (an addition, not a re-cut — the
standing order holds; new rows append at Pri 71+).** The owner created
milestone **0.8.4** for design note 57 (the GUI convergence,
[`57_gui_convergence_note.md`](57_gui_convergence_note.md), **AGREED
2026-09-11** — the owner took rulings R-57.1…R-57.5 as proposed the same day,
so the band's gate is the **0.8.3 cut** (band B4 in flight), not the note).
Filed as #265–#270 in D-57.8's sequence and rowed in a new **band B5**
between B4 and B2, because it re-shapes B2: at #270's close, per ruling R-57.4,
#29/#148/#247–#252 close superseded and #78 re-scopes to #269 — each of those
issues carries a planned-supersession comment dated today, and they stay open
on their milestones until that close.

| Pri | Item (detail below / in its plan) | What ships | Tag | Tier / effort | Depends on |
|---|---|---|---|---|---|
| **B4 — 0.8.3: the empennage geometry model + the milestone's defect set (the OR-13 freeze lifted at the 0.8.2 cut)** ||||||
| 29 | **The export package reduces to one solver artifact** — four parallel model concepts (per-component decks, balanced deck, LRA beam, CONM2) share one id space, and the deliverable borrows its GIDs from artifacts that are not deliverables: `lra_model` imports `station_gid`/`tail_span_gid`/`tail_control_gid`/`sob_gid`, so GID 7 names one point in `wing_loads.bdf` and another in `lra_model.bdf`. ~2/3 of open export work is maintenance on the three concepts that are not the deliverable. `sbeam_bridge.py` is **not** mostly deletable — the oracle report reaches into it at seven sites, so the applied-load model is report infrastructure filed under the wrong name *(design note 56, owner rulings 2026-09-10)* (#263) | One LRA beam model with arbitrary properties proving the cases solve, plus a self-contained CONM2 mass model on its own CG grids; the applied-load model and report tables rehomed to `report/`; per-component decks deleted; `EXPORT_TARGETS` 10 → 2; id bands 25+ → ~8; 83 sbeam digest channels → ~11; two load-routing paths → one | V | L / L | design note 56 at AGREED. **Slices 1-3 shipped 2026-09-10/11**: the contract-statement owner, the report tables' move to `report/tables.py`, and the per-component deck deletion (`EXPORT_TARGETS` 10 → **4**, not 2 — `gear` is a document under D-56.1 and `balanced` waits on §8's `roundtrip.py` question; sbeam digest channels 83 → **33**). Remaining: the applied-load move to `report/applied.py`, D-56.3's band renumber, D-56.4's LRA mesh (schema 65 → 66), D-56.6's CONM2 CG grids, the oracle-GUI buttons |
| 30 | **The balanced deck never says it is an elementless load cloud** — 0 elements, `SOL 101` and `SPC = 1` invite a bare solve that dies "singular stiffness matrix", a misdiagnosis; the explanation lives only in a test docstring *(review R-2)* (#173) | ~~One KNOWN LIMITATIONS paragraph~~ — **moot under note 56 D-56.8**: the balanced deck demotes to an internal producer and no `.bdf` ships, so there is no deck left to caveat. Closes as **superseded**, not fixed, with #263 | V | M / S | #263 (closes with it) |
| 31 | **GA6 fixture: altitude identity + wing-case envelope, one package** — every delivered case states 0 ft where Appendix A names its critical wing conditions at 12,000 ft, and the wing export ships three cases with no negative-g, so the delivered distributions do not envelop the wing; each fix renumbers the V-n indices the other depends on, so this row is #164 **and #165 merged** — the renumber is paid once *(review R-26)* (#164) | Stated condition identities correct and the wing enveloped; the three oracle cases kept; oracle-locked fixtures renumbered in one pass | V | L / M | owner decision on the case-set shape |
| 32 | **Unstamped single-module runs bypass the governing SF table** — `oracle_app/results.py` and the comparison view call `registry.get(name)(project)` with no `stamp()`. *Re-scoped by note 49: nothing can factor any more*, but the **stated** factor is wrong on that path — a project `safety_factors.overrides` entry is silently ignored, and factorless conditions state the dataclass 1.5 where the stamped path states `N/A` *(review R-6)* (#177) | Stamping made structural at the registry entry point so an unstamped render is impossible | V | M / S | — *(the OR-13 lift landed at the 0.8.2 cut)* |
| 33 | **Benchmark-first gets its presence guard** — no test asserts that a registered module carries an oracle or closure test at all *(review R-16)* (#186) | A registry-walking guard plus a per-module gate manifest, which also becomes the coverage matrix's single source | V | S / S | — |
| 46 | **test_structural_speeds: four assertions at 2e-3…1e-2 in a file headed ±0.1 %, with no inline rounding-limited justification** *(review R-4)* (#175) | The one-line justification on each, or tightened where the printed precision allows | V | S / S | — |
| 47 | **Balanced-export CLI message states a count of unassembled conditions without pointing at the deck's itemized list** *(review R-5)* (#176) | ~~"…(itemized with reasons in the deck header)"~~ — **moot under note 56**: `EXPORT_TARGETS` drops `balanced`, so the message goes with the target. Closes as **superseded**, not fixed, with #263 | V | S / S | #263 (closes with it) |
| 48 | **sbeam-drift weekly workflow files/updates an issue on failure** instead of relying on the Actions page *(review R-18)* (#188) | A failure step opening or commenting on a pinned "sbeam drift" issue | V | S / S | — |
| 50 | **`safety_factors.classify`: exact-match reference returns before the multi-reference agreement check** — the one hole where "flagged, never defaulted" degrades to silently-first-match; latent, no current producer emits the string *(review R-9)* (#179) | After an exact hit the remaining references are still classified and factor agreement demanded; guard case added | V | S / S | — (the SF cluster) |
| 51 | **Report side keeps two `getattr(..., ULTIMATE_FACTOR)` fallbacks the M4-16 rule banned from export** — dead defaults that would silently resurrect a flat 1.5 on an attribute rename *(review R-10)* (#180) | Direct attribute access at the three sites, per the rule `sbeam_bridge._sf` already states | V | S / S | — (the SF cluster) |
| 55 | **Three examples enter a control-surface area they do not draw** — aileron entered-vs-outline disagreement 4 %/5 %/44 %; three fixtures carry `flap_loads` with no flap outline *(filed 2026-09-07; OR-152 states the disagreement meanwhile)* (#216) | Each pair reconciled from the airplane's data, per example | V | S / S | — |
| 56 | **One fuselage quantity is published under two `LoadValue` keys** — `select_fuselage`'s down/up blocks split one quantity across two keys; the report's §4.3 fold is the workaround *(found 2026-09-06, OR-14)* (#222) | Keys converge, labels survive as display text; rides the baseline wave (CSV columns move) | V | M / S | the baseline wave (#164 first) |
| 57 | **Applied-load CSVs drop the case identity: 33 gear cases collapse onto 8 Case strings** — `AppliedLoad.case_id` populated and never emitted *(2026-09-08 review C1)* (#241) | A `Case ID` column (+ `Loading` on the gear file) in `applied_load_csv`; round-trip assert into the case index; digest re-pin. **Survives note 56** — D-56.1 moves the `AppliedLoad` model to `report/`, it does not delete it, so the fix lands at the new address | V | M / S | the baseline wave; after #263 if that lands first (the file moves) |
| 58 | **No delivered CSV states the axis directions**, and two files make frame claims their data does not honour *(2026-09-08 review C2+C3)* (#242) | An AXES stanza in the methods stamp (one owner, every file); the control-surface `Fz` → surface-normal label; one meaning for `Axis`. **Narrows under note 56** — the deck-companion CSVs it also covered are deleted with their decks; the surviving files are the report's own | V | S / S | the baseline wave; narrows after #263 |
| 59 | **`format_value` prints inconsistent precision and flips notation on integral values** — `%g` strips significant zeros and switches notation at 1e5; ~84 call sites, every delivered table cell *(owner's PDF review 2026-09-01, OR-14)* (#161) | Consistent fixed-significant-figure rendering, design note first; lands **last** in the baseline wave since it reformats what the others produce | V | M / M | design note; the baseline wave |
| 60 | **oracle_app results captions still claim ULTIMATE over LIMIT tables** — the frozen half of #192; the understrength direction *(2026-09-08 review G1)* (#239) | `_ULT_NOTE`/the ULTIMATE default replaced with the LIMIT statement; `oracle_app` added to `_GUI_TREES` so G-OR-74's screen sweep covers this front-end | V | S / S | — (unblocked at the 0.8.2 cut) |
| 61 | **Override cross-check warnings fire below display precision and print two identical numbers** *(2026-09-08 review G6)* (#243) | One owner for the comparison tolerance (display precision or a stated rel-tol) so every cross-check warning behaves the same | V | S / S | — |
| 62 | **Report polish rollup from the 2026-09-08 review** — ten tier-S presentation items in one issue so none is lost *(R13–R23)* (#240) | The ten items closed or individually declined with a reason | V | S / S–M | — |
| 63 | **The issue package's `data/` becomes the oracle GUI's only CSV channel** — pulled into 0.8.3 by owner ruling (2026-09-09): implemented by consolidation, the per-module CSV/text buttons and the results zip retiring in the same change, preceded by the column-inventory pass (OEI march and V-n matrix named) (#245) | `data/` in every package build from the report's own owners, manifest rows, the intermediate channels gone, G-OR-73 re-cut to the consolidated set. **Note 56 does not supersede this row — ruling 6 *is* its scope.** #263 narrows the column inventory instead: the deck-companion span/chordwise/fitting CSVs are deleted with their decks, so `data/` need only carry what the document draws | V | M / M | after #241 and #242 (the wave), so `data/` is born corrected; coordinates with #263 |
| 65 | **Package-split `balance.py` (2,842 lines)** — where every full-airplane change lands; pure moves along its existing section boundaries, guarded by the existing oracle/closure tests. **Re-scoped by note 56:** `sbeam_bridge.py` (measured **3,091**, not the 2,701 this row carried) is not split but **dissolved** by D-56.1, so half this row leaves with #263; `report/content.py` becomes a *more* pressing candidate, since `report/` grows ~970 lines absorbing the applied-load model *(review R-23; moved from band C 2026-09-09 — note 49 §0's "stays 0.8.3" ruling honored over the banding drift; re-scoped 2026-09-10)* (#191) | `modules/balance/` as a package; `report/content.py` and `io.py` as later candidates; sequenced right after #15 at the hygiene front so the milestone's diffs land in the final layout | V | S / M | after #15 (Pri 14); the `sbeam_bridge` half goes to #263 |
| 66 | **OR-133's withholding statement claims the T-tail load path is not modelled; T7 models it** — the oracle report's Appendix E wording predates `tail_span`'s fin-tip transfer, so the two front-ends disagree about what the suite can do; owner decision: lift the withholding for T-tail projects or reword it as policy *(2026-09-09 review A1)* (#254) | The statement true again — Appendix E printed from the T7 set, or reworded with the gates re-cut deliberately (G-OR-87). **Narrows under note 56**: the spanwise fin deck that carried T7's lumped transfer is deleted, so the question survives against the LRA model's fin-tip joint alone | V | S / S–M | the note 51 implementation, if it lands this milestone; narrows after #263 |
| 67 | **Tail Span Loads page: fixed prose states fuselage attachments under its own T-TAIL one-support bullet** — #235's class, a conventional-tail sentence rendered unconditionally *(2026-09-09 review A2)* (#255) | The closing paragraph and marker label conditioned on the layout; rule-4 sweep of fixed prose in `app/views/` *(tail-geometry cluster: same files as #223/#220/#219/#216)* | V | S / S | — |
| 68 | **Engine-installation figure legends overflow the margin on long twin designations; coincident point labels overprint** — invisible on GA6, guaranteed on any real twin *(2026-09-09 review A3)* (#256) | Legend entries wrapped or stacked inside the text width; shared-coordinate labels offset or combined *(beside #240's polish)* | V | S / S | — |
| 69 | **A derived ACRL assembles with a zero aileron couple and the deck states nothing in band** — a reader cannot tell couple-free physics from couldn't-compute-the-couple *(2026-09-09 review A5)* (#258) | The zero-by-derivation stated in the case's notes, deck header and UI, like the ASSUMED thrust line; one guard test | V | S / S | — |
| 70 | **`atr42_100` is internally inconsistent** — planform 18 % under the type's area with the true value stored-but-ignored, wing items 3.4x the panel integration, fuselage stations 3,741 lb short, five override warnings on load, no control-surface slices *(2026-09-09 review §4)* (#260) | The fixture reconciled end-to-end from published ATR 42-300 data; in the CI matrices, so baselines move *(the baseline wave; #261 shipped 2026-09-10)* | V | M / M | the baseline wave (#164 → #222 → #241 → #242 → #161) |
| **B5 — 0.8.4: the two front-ends converge on one (design note 57 AGREED 2026-09-11; starts after the 0.8.3 cut)** ||||||
| 71 | **The JSON editor moves to `app_shell/`** and registers in the oracle GUI — the escape hatch that decouples every other port from the schedule *(note 57 D-57.3)* (#265) | The editor a page of the surviving GUI, registered on navigation per the OR-16 pattern; no re-charter needed (OG-13 already round-trips the JSON) | V | S / S | the 0.8.3 cut (first of the band, D-57.8) |
| 72 | **The oracle GUI renders every input path in two marked field tiers** — original-suite fields with their `.BAS` provenance as today; the ~79 sloads-only fields in a marked extension section, each stating its basis; `oracle_input_paths` becomes the tier classifier *(note 57 D-57.2 — the re-charter step, amending note 32 OG-1/OG-2)* (#266) | Every registry input path enterable or documented JSON-only with a reason (a registry-walking guard, closing the L-8e class structurally); every extension widget marked with a basis | V | M / M | the 0.8.3 cut; after #265 |
| 73 | **Plots port as render-only helpers, written fresh** — V-n chart, three-view, span shear/BM/torsion, VMT envelope overlays with the external-CSV comparison; the `app/` implementations are the spec, not the source (CC F(72)/F(63) are M4-11b's own exhibit) *(note 57 D-57.4; lawful under C210-15)* (#267) | One plotting module in the shell reading the same result slices the pages render as tables; trim & stability sweep deferred (note 57 §8) | V | M / M | after #266 |
| 74 | **The fleet comparison ports** — the Phase-C "assess vs similar airplanes" requirement lands with the extension tier it belongs to; `_subject_from_project` (CC E(34)) rewritten, not imported *(note 57 D-57.5)* (#268) | The fleet plots a page of the surviving GUI over `reference_aircraft.csv` unchanged | V | S / S–M | beside #267 |
| 75 | **The seed button is built fresh with its hardening** — seeded rows loudly incomplete until positioned and tagged; merge/refuse/replace stated before the click; port-then-harden rejected under rule 4 *(note 57 D-57.7; re-scopes #78)* (#269) | The WTESTIMA seed action in the surviving GUI with #78's hardening in its first version; #78 closes superseded when this lands | V | S / S | after #266 |
| 76 | **`app/views/` retires and the derived page set is re-cut** — 22 pages / ~8,800 lines deleted; five pages retire without port, each citing its successor; `workflow.py`'s derivation rule and gate G2 re-cut (still derived, not listed); at close #29/#148/#247–#252 close superseded (R-57.4), #259 with the dashboard, and the Phase G plan rolls to history *(note 57 D-57.1 + D-57.6)* (#270) | The single front-end: no load moves, old-GUI files round-trip (OG-13 widened), G-OR-74's `_GUI_TREES` covers the whole survivor, one `st.set_page_config`, the journey walk re-aimed with an empty `KNOWN_OPEN`, no retired page reachable | V | L / L | #265–#269 landed first (D-57.8) |
| **B2 — 0.9.0: main-GUI development and bug correction** ||||||
| 7 | **GUI review resumption** — the five unswept sections (Flight, Other, Ground, Plotting, Export) against the 0.7.2 deliverables; findings filed at close (rule 5); re-cut follows (#29) | The review body completed; the UI freeze on `app/views/` re-opened to the extent the findings justify — a reviewed list, not a rework. **The anchor of 0.9.0**, and the re-cut that promotes the parked main-GUI rows: **L-8c** (Results Review omits the 8 folded modules' results), **L-8e** (uncovered input fields + UX nits), **L-8f** (display-only nits), **M4-11b** (the six F/E-complexity view functions) and the **mutation half of L-8d** — which the 2026-08-24 code review showed is a live mechanism, not a theoretical one (a retained widget beat a model grown underneath it; the row-counter fix closed that instance, the class stays open) | V | S (review) / M | 0.8.1 cut |
| 8 | **Seeding the item table from the estimate is destructive, and its rows are silently zero-stationed** — the oracle half shipped **2026-08-25** (`changes/weight-estimate-advisory.changed.md`): WTESTIMA's block captioned with what reads it (nothing — WTONECG and WTENV read the itemized data base) and the estimate shown beside the entered empty weight and MTOW with the delta. The **seed button itself already exists** and has since before the review (`app/views/weight_mass.py`, `weight_estimate.estimate_to_mass_items`, specified in `PROGRAM_SPEC.md` §WTESTIMA) — C210-9, issue #78 and the 2026-08-24 re-cut all recorded it as unbuilt because the whole C210 build was in the oracle GUI, which has no such button. What is open is the #62-class hardening the issue actually asked for *(C210-9, class c; build review 2026-08-23)* (#78) | Seeded rows **loudly incomplete** until positioned and tagged, rather than arriving at station 0 and untagged — `mass_distribution.infer_component` then lumps every one of them on the fuselage beam, the defect `fuselage_mass_warnings` already reports from the other side; and the button either merges, refuses, or says before the click that it **replaces every item already entered** (its caption says so today, after the fact). Main GUI, so it lands with the `app/views/` freeze lift | V | S–M / S–M | #29 |
| 23 | **A no-op Apply still writes to the project — the residue after #145's sweep** — the whole-GUI journey test (`tests/test_gui_journey.py`) walks every bundled example through every `workflow.py` page pressing every Apply with nothing entered, and asserts the project byte-identical. #145 closed the *attachment* half of what it found (an Apply creating an `Optional` slice out of nothing, which crashed Results Review and Export on three shipped examples). Ten writes remain, carried as the file's `KNOWN_OPEN` list, each still asserted to reproduce so none can lapse into silence. **Silent gain:** `speeds.occupants` seeded from the WTESTIMA seat count on any Apply; `speeds.mach_limit` and `weight.envelope` attached with the form's defaults. **Silent loss** — a rebuild dropping what its form does not render, the same class #145 fixed in three other places: `speeds.wing_area_sqft` (the D4.4 Geometry read-through), `speeds.chosen_va`/`chosen_vf`, `weight.items[].wing_fraction` (not a column of the item table), and `engines[].max_cont_hp`/`takeoff_hp`/`hub_weight_lb` (the power fields render for reciprocating engines only, so a turboprop's entered 2000 hp is erased by its own page's Apply) *(filed 2026-08-29 from #145's journey walk)* (#148) | Each write either happens only on an edit to the field it writes, or is carried through the rebuild that drops it; `KNOWN_OPEN` empties as they close, and the journey test fails on the last entry's removal until the list goes with it. The engine-power erasure is the sharpest: it silently changes a shipped input on two bundled examples | V | M / M | #29 (the `app/views/` freeze lift) |
| 15 | Dead code (CH-5) — *moved from band D 2026-09-04; the four-symbol list re-verified consumer-free by the review* (#16) | Delete `write_balanced_deck`, `write_conm2_fragment`, `write_mass_check_deck`, `all_checks`; demote the ~12 no-consumer public names. **Three of the four sit in material note 56 deletes or rewrites** — either sequence this first as a trivial pre-clean, or absorb it into #263 | V | S / S | — (or absorbed by #263) |
| 34 | **`solo_close.sh` verifies fragment existence, not tier content** — nothing checks a tier-M closure touched `PROGRAM_SPEC.md`, a tier-L closure cited `theory_sources.md`, or that a physics change had a note at AGREED; hand-git bypasses are degrading the commit-subject record. The checkable subset gets scripted; the rest is named as discipline in `DEVELOPMENT_PROCESS.md` *(review R-15)* (#185) | The preflight enforcing the checkable closure obligations and validating the subject it writes | V | M / M | — |
| 19 | **Whole-pipeline-per-assertion tests, re-aimed at the coverage leg** — *moved from band D 2026-09-04* *(CR-D-6, filed from #46; hygiene; ruled 2026-08-26 (owner): option (b) — the trip figure was the coverage-instrumented run; the row is re-aimed at the run that pays for it)* (#92) | The repeated-pipeline shape gone from the coverage leg's `--durations`; the local command stays the clause's datum. **No `slow` marker** — `00_program_overview.md` §Testing states why | V | S / S–M | — |
| 20 | **The oracle form reaches into a `field_registry` private** — `oracle_app/form.py:709` calls `fr._locate(paths[0])`, the only access to a `sloads` private from either shell package *(production-release review 2026-08-27 §3.7; moved from band D 2026-09-04 — the GUI milestone is when `field_registry` is next touched)* (#130) | `field_registry` exposes the lookup publicly and `row_class` calls it; the private stays private | V | S / S | when `field_registry` is next touched |
| 36 | **Down-select at ULTIMATE, and deliver ultimate loads** — an envelope taken over cases whose *prescribed* factors differ is a maximum of quantities that are not comparable, so selecting the critical case at LIMIT can name the wrong case. The fin is where this first bites: note 44 OR-172 admits 23.367 to the v-tail critical set, and 23.367(a)(2) is classified **ULTIMATE** by the regulation (SF 1.0) while every case beside it is LIMIT at 1.5 — so a 2000 lb LIMIT case at 1.5 outranks a 2500 lb case at 1.0 on the ultimate basis the structure is actually sized to, and the LIMIT down-select picks the second. OR-176 marks the factor on every row and every plotted series, which makes the mismatch visible; it does not resolve it. **This reverses note 49 OR-116 for the delivered set** — every load sloads delivers is currently LIMIT with the factor stated and applied nowhere — so it is a load-output contract change and needs a design note at AGREED before any code, plus a sweep of G-OR-71/72/73/74 and the `-ULT` marker rules *(owner, 2026-09-07, in session: "in a later milestone this is the reason I want to do all down select at ultimate and convert all delivered loads to ultimate")* (#193) | Down-select performed on the ultimate basis, delivered loads converted to ULTIMATE, and the stated-factor contract re-expressed for a set that is no longer LIMIT — with the two prescribed-ultimate families (23.367(a)(2), 23.561(b)) no longer a special case because nothing is factored twice | V | L / M | design note first (contract change); note 44 §21 shipped |
| 37 | **The load-case index carries no loads for 344 of 347 rows** — its six load columns are the engine-mount shape (`render.load_cases_to_rows`' own docstring: *"the load components an engine mount must react"*, `load_keys.LOAD_CASE_KEYS`), and four of the five producers cannot express themselves in it: a landing case has three legs at three points, a wing case a distribution. Measured 2026-09-07: **344/347** rows on `ga6_normal`, **543/555** on `baron_58`, **587/617** on `concept_regional_jet` carry a blank load. Note 44 OR-186 answered the *deliverable* half — each structural element now has an applied-load CSV shaped for its own loads — and left the index itself, because removing or reshaping those columns touches every producer and every consumer of `load_cases_csv`. Either it is an index, in which case the load columns invite a reader to conclude a case carries nothing, or it is a load table, in which case most of it is missing *(note 44 §21 filed, §22 measured)* (#209) | A decision on what the file is, then the columns to match it — the candidate being that it becomes an index in name as well as in fact, with the per-element files carrying the loads. **Unchanged in substance by note 56**, but D-56.1 moves the case index out of the export bridge into `report/` — arguably where a decision about what a *report* table is always belonged | V | M / M | note 44 §22 shipped; a decision on the file's purpose |
| 38 | **Two engine-mount conditions per engine state no point of application** — the 23.361(b)(1) sudden-stoppage torque and the 23.371(b) gyroscopic condition carry no `loc_*` values while the four beside them for the same engine do. Until 2026-09-07 the index filled the gap with the *first* location in the set, publishing the right-hand engine's stoppage torque and its four gyroscopic sub-cases at the **left-hand** engine's butt line — ten rows on `atr42_100` and `dhc8_dash8`, fifteen on `concept_regional_jet`. Note 44 OR-193 carried the fix at the render boundary (a condition with no point takes the point of the condition it follows, which is that engine's, gated on every fixture); the **producer** stating the point on every condition it emits is the proper repair, and `modules/engine.py` is frozen for 0.8.2 *(note 44 §22, OR-193)* (#210) | `modules/engine.py` emitting `loc_x`/`loc_y`/`loc_z` on all six conditions, and `_running_locations` reduced to the identity it should be | V | S / S | the OR-13 freeze lifting |
| 39 | **The fuselage mass reconcile is a GUI-only warning; the report and deck deliver the shortfall unstated** — the issued document rides a station mass model short of the airplane's own item table with no flag a reader can see *(2026-09-09 review A4)* (#257) | The entered-vs-derived totals (and the delta past a stated tolerance) in the report's fuselage input data and the `fuselage_loads.bdf` header, from the same source the GUI check reads | V | M / M | — |
| 40 | **Dashboard 🟡 promises "open the page to compute" for modules whose own input slice does not exist** — the state actually means upstream-ready, own-inputs-missing *(2026-09-09 review A6)* (#259) | A fourth glyph or a legend rewording; display-only | V | S / S | — |
| 39 | **The flight balance models no thrust** — `flight_envelope._balance` solves the normal force and the pitching moment about the CG and writes **no** longitudinal force equation, so every balanced V-n point is thrust-off. That is consistent rather than absent: the drag leaves the balance as `NX = -DX/W` (`aero_curves.inertia_drag_factor`) and WINGINER applies it to the mass distribution, so the airplane is in longitudinal equilibrium as a decelerating body, and note 44 OR-198 makes Appendix A state it. Modelling power would reduce NX and add a thrust-line pitching moment about the CG — design note 53's `thrust_line_fwd`/`thrust_line_aft` already carry the geometry — and would move **every** balanced point, hence every selected condition and every delivered load. **Parked without a rank under rule 6:** its effect on a delivered load is unmeasured, so the first piece of work is the measurement, not the implementation; a power-on balance whose effect is below the base method's own uncertainty is not worth a contract change to an oracle-locked module *(owner's question, 2026-09-07: "we don't have any cases defined as thrust on or off, are all assumed off?"; note 44 §23, OR-198)* (#226) | The measurement first — how far a power-on balance moves a delivered load on a shipped fixture — and then, only if it clears the base-method error bar, a design note for a thrust term in `_balance` | V | M / L | a measurement; then a design note (oracle-locked module) |
| 40 | **M4-11b — Split the highest-complexity view functions** — six `app/views/` functions at CC E/F (worst `_tab_design_speeds` F(72)); split each into seed / form / render and finish `unit_number_input` adoption (body below) *(moved from `02_parked.md`, #190 — pre-assigned to the #29 band, so parked meant only "waiting for 0.9.0")* (#247) | The M4-11a scaffold adopted; no view function above CC D; `radon` re-measured before/after | V | M / M | #29 |
| 41 | **L-8b — `help=` tooltip rollout completion** — app-wide coverage ~45 %; worst pages 0/6 and 0/7 (body below) *(moved from `02_parked.md`, #190)* (#248) | Tooltips page by page to full coverage | V | S / M | #29 |
| 42 | **L-8c — Results/Export consolidation parity** — the 8 folded modules' results missing from "All results by section"; folded-module CSVs machine-labelled (body below) *(moved from `02_parked.md`, #190)* (#249) | Folded → host mapping in Results Review; descriptive CSV labels on Export | V | S / S | #29 |
| 43 | **L-8d — Widget freshness audit, the mutation half** — a widget that goes stale while the project is *mutated* underneath it, which no generation bump covers; both data-loss halves shipped #51 (body below) *(moved from `02_parked.md`, #190)* (#250) | The `key=`+`value=` audit closed for project mutation, or proven impossible | V | M / M | #29 |
| 44 | **L-8e — Uncovered input fields & UX nits** — remaining JSON-only fields, error-string de-jargonizing, sidebar anchoring, spinners (body below) *(moved from `02_parked.md`, #190)* (#251) | Every schema field entered somewhere or documented JSON-only; the listed UX nits closed | V | S / M | #29 |
| 45 | **L-8f — Display-only and numerically-inert nits** — none changes a load (body below) *(moved from `02_parked.md`, #190)* (#252) | The listed display nits closed or individually declined with a reason | V | S / S | #29 |
| **C — 1.0.0: additional analysis capability (consumer-gated; design notes first)** ||||||
| 9 | The aileron's own lift increment is not distributed (#14) | `ACRL` wing cards gain the aero half of the couple (~70 % span); the schema fields shipped v52 and wait for data and a consumer | V | L / M | only if a consumer sizes to `ACRL` |
| 10 | **Wing fuel (and any tank/store band) is a point mass in WINGINER** — faithful to WINGINER.BAS lines 1180–1270 (every concentrated mass is a spanwise step; only the structure panel is spread), but a wet wing's fuel occupies a span band, so the point model concentrates the inertia relief and puts a fictitious jump in mid-span shear/torsion (**owner, C210 build: "fuel should be spread through the wing not just at one point mass location"**, C210-50, build review 2026-08-23) (#111) | `WingMassInput` gains a distributed-mass band (y_start, y_end, weight, chordwise CG) folded into the per-strip density `w[i]`, reducing exactly to today's point when the band collapses; Appendix A oracle case (concentrated gear only) untouched, lock holds. Interim (documented in the review): split the fuel into N concentrated rows across the tank span with the same centroid — root bending and total shear identical | V | L / M | design note first (physics/L) |
| 11 | Ground-case fuselage station distribution — the ground family has no per-station view *(from the #11 closure, D-28)* (#31) | Per-station shear/bending/torsion for the ground family on the fuselage beam, its own envelope beside the flight one and never merged with it, each station naming its ground case | V | L / M | a frame-sizing consumer; design note first |
| 12 | Mach-capped balanced points are published with their coefficients extrapolated past the fitted stall alpha, and nothing says so *(from the #13 closure, D-30)* (#32) | A derived past-fit marker wherever a per-point quantity is published (BALLOADS' 300 rows first); rows stay published and marked, never withheld; no schema field — the marker reads `EnvelopeResult.is_clamped`, the owner #33 left (2026-08-22), rather than re-deriving the point's CL against its Mach-adjusted stall CL; the two are pinned to name the same rows | V | M / S–M | — |
| 13 | **Certification basis / case manifest** *(review 2026-08-20 §6 rank 7)* (#47) | The per-condition coverage matrix as a deliverable, so the next FAR 25 case lands against a stated basis rather than a blind matrix | V | L / M | design note first |
| 16 | Calc-side function size (CH-8) — *moved from band D 2026-09-04; re-cut with the review's numbers: `landing_reactions` now 276, plus `envelope` 195, `build_tail_span` 176, `_export_sbeam` 173, `_manifest_rows` 155 and the three `balance.py` assemblers (see the R-22 comment on the issue)* (#17) | Split when touched; **the view functions wait for the GUI review (#29)**. **Narrows under note 56**: `_export_sbeam` (173) is deleted with the per-component targets, and `build_tail_span` (176) is untouched but loses its deck consumer; the other named functions stand | V | S / S | — |
| 17 | Review 2026-08-10 unscheduled findings m3–m13, m15–m18 + NITs *(defect sweep; moved from band D 2026-09-04)* (#18) | Swept opportunistically (practice 4) or promoted individually | V | S / S–M | — |
| 18 | mypy strictness ratchet — stage 2 `export/`, stage 3 `modules/`, **plus `io.py` as its own stage** (95 `Any`-typed lines, the schema boundary — the R-25 comment on the issue) *(design note 27 ST-3; moved from band D 2026-09-04)* (#19) | `sloads.export.*`, `sloads.io`, then `sloads.modules.*` added to the `[[tool.mypy.overrides]]` list and narrowed to zero under ST-4; then `warn_return_any`/`disallow_any_generics` toward `--strict` | V | S / S per stage | — |

**Frozen (review §3) — no further investment; tests and gates kept; touched
for defects only:** the FAR 23 core; the balanced assembler + handedness;
CONM2/MASSSET export; the sbeam round-trip harness; the ground/landing
families + gear report; the governing safety-factor table (Layer 2 parked);
distributed empennage loads, control surfaces, hinge moment, T-tail transfer;
the **LRA beam model at its determinate paths**; the summary report, PDF,
workbook, manifest and methods stamp; the **`app/views/` UI — pending the
0.8.0 GUI review (#29)**, whose findings decide what re-opens
(`oracle_app/` + `app_shell/` are open for exactly the band-A rows; the CLI is
the delivery path — parked M4-11b and the L-8 UX rows stay parked until #29
closes; parked **L-8d**'s keyed data-loss half shipped 2026-08-21 as #51 —
`app_shell/widget_keys.py` — and its unkeyed half shipped 2026-08-22, closing
#51's reopen as one pass with #44's unit-boundary rollout: that pass consumed
**the one carve-out from this freeze** — `key=` plus the boundary helper at
exactly those call sites, no layout/behaviour rework — so the freeze is whole
again; L-8d's mutation case stays parked); F25-2.

---

## 0.9.0 band item bodies (moved from `02_parked.md`, #190)

Pre-assigned to the #29 main-GUI band by their own text, so keeping them in the
parked file made "parked" mean two things; moved 2026-09-08 so `02_parked.md`
returns to meaning **off-mission**. Bodies verbatim:

### M4-11b — Split the highest-complexity view functions **[maintainability]**
The scaffold helpers (`unit_number_input`, `page_header`/`page`) exist and are
tested (M4-11a); the complexity-splitting half did not ship. CC re-measured with
`radon` on 2026-08-04:

| function | file | CC |
|---|---|---|
| `_tab_design_speeds` | `structural_speeds.py` | **F (72)** |
| `_three_view` | `configuration_layout.py` | **F (63)** |
| `_tab_vn` | `flight_envelope.py` | **F (44)** |
| `_tab_cg_inertia` | `weight_mass.py` | **E (40)** |
| `_subject_from_project` | `aircraft_comparison.py` | **E (34)** |
| `_tab_trim` | `flight_envelope.py` | **E (33)** |

Split each into seed / form / render (and `landing_reactions` per attitude), and
finish adopting `unit_number_input` in the views that still hand-pair
`to_display`/`to_imperial_scalar`. **Note `engine_mount` is already correct by a
different route** — it converts the whole `EngineInput` at Apply via
`units.to_imperial`, so per-field adoption there would double-convert; either
leave it or migrate the whole page in one move. `radon` is in the `dev` extra
(D-17, reporting only) — re-measure before and after.

### L-8b — `help=` tooltip rollout completion
App-wide tooltip coverage is ~45%. Worst pages: flap loads 0/6, one-engine-out
0/7, wing loads 2/10 (structural speeds is complete at 21/21); the G6/G6b
sections add ~30 untooltipped widgets. Finish the rollout page by page.

### L-8c — Results/Export consolidation parity
Results Review "All results by section" omits the 8 folded modules' results —
map folded → host step so they appear. Human-label the folded-module CSVs on
Export ("balloads (CSV)" → a descriptive name).

### L-8d — Widget freshness audit (deferred from M2-7)
Input widgets pass both `key=` and `value=`, so Streamlit's session_state can win
over the project-seeded `value=` and show a stale field after the project changes
underneath (cross-page Apply, programmatic load). **Not a data-loss bug** (Apply
is required to persist, and per-page unit-suffixed keys limit the blast radius);
audit the `key=`+`value=` widgets and re-seed on a project change, or prove it
cannot occur. `tests/test_persistence.py` locks the data-persistence half.
**The keyed half of the data-loss class shipped 2026-08-21 as #51** — a *project
generation* stamped into every project-seeded widget key
(`app_shell/widget_keys.py`), bumped once per project replacement (`adopt`, and
the JSON editor's Apply) and guarded by `tests/test_widget_freshness.py`. That
sweep also settled the rationale above: `app/views/`' Apply step defers the
overwrite to the user's click rather than preventing it, so those views were
stamped too. **The unkeyed half shipped 2026-08-22, closing #51's reopen:** the
98 `app/views/` widgets that carried no `key=` at all — whose Streamlit identity
derived from their *arguments*, stable whenever the seed value repeats, so a
value typed before a load survived it (reproduced on `structural_speeds`' VB
against `atr42_100`) — now all carry stamped keys, landed as one pass with
#44's unit-boundary rollout (`unit_number_input` stamps for its callers). The
guard's "no `key=` is per-render" premise was inverted to fail closed, with a
type-then-load reproduction test and a per-key shell allowlist. What stays
parked *here* is the rest of the audit — a widget that goes stale while the
project is **mutated** underneath it (a cross-page Apply, a seed chain), which
no generation bump covers because the project was never replaced.

### L-8e — Uncovered input fields & UX nits
Add widgets (or a documented JSON-only status) for the remaining uncovered
fields: `speeds.chosen_va`/`chosen_vf`, `one_engine_out.speeds_kt`,
`weight.envelope.fuselage_nose_x`/`fuselage_tail_x`. Plus: de-jargonize error
strings (no internal slice names); move the Geometry parametric form and the
Flight-Envelope altitude Apply out of the sidebar (or visually anchor them);
first-run Loads Plots info should use the linked `gate()`; the OEO "define ≥2
engines" warning needs a page link; save-filename sanitization; `st.spinner` on
heavy recomputes. *(The `use_container_width` migration left this bullet on
2026-08-28: its shared-`app_shell/` half is band-B row #129 by the 2026-08-24
rule-2 fix-site placement — production-release review §3.7, owner ruling §5.4 —
and #129 carries the whole migration, `app/views/` included, because a
deprecated parameter removed upstream breaks both front-ends at once.)*

### L-8f — Display-only and numerically-inert nits **[lowest priority]**
None of these change a load. V-n plot negative closure should show −1.0 at VD for
U/A categories (loads are right; display only); chosen VA is silently clamped to
VC (BASIC only raises — warn instead); 190-lb occupant caption for U/A
(23.25(a)(2)); MC-vs-MD Mach cap on cruise stall-line conditions (numerically
inert — comment or match BASIC); ENGLOADS `prop_blades` captured but unused;
AILERON positive-deflection coercion undocumented; WTONECG YBAR omitted;
TAILDIST average-chord only (not the guide's N-station-chord variants,
Figs 20.7–20.10).

---

## Open defects (index)

- #18 — Review 2026-08-10 unscheduled findings [Minor/NIT].
- #170 — Mean takeoff torque is factored: `is_load_unit` tests the unit alone (rowed, Pri 49).
- #216 — Three examples enter a control-surface area they do not draw.

- #217 — An entered thrust line does not steer the thrust in the balanced cases.

- #209 — No engine-mount case reaches the LRA deck. *(Reworded 2026-09-10: note
  56 D-56.2 deletes the per-component decks, so "the sbeam deck" names the LRA
  model, which is the only load-carrying deck that survives.)*

- **No control-surface hinge moment is computed anywhere — in sloads or in the
  suite it replicates.** Checked against the source 2026-09-07: `AILERON.BAS`,
  `FLAPLOAD.BAS` and `TABLOADS.BAS` each end after printing their loads and
  chordwise pressures; chapter 16 (p105–106) claims only the constant pressure
  forward of the hinge line; and the words *hinge moment* occur once in the
  whole manual, in the quoted CAM 3.224-1(a) tab-deflection limit, which
  chapter 18 (p113) then declines to apply — *"the computer program for surface
  loads for the aileron, elevator and rudder are not limited to pilot effort."*
  So this is **not a replication gap**: note 44 §19 OR-154 states the *sense* of
  the moment as the sign convention and derives no magnitude. Whether sloads
  should produce one as a modern addition — it is what a control-surface
  attachment and its actuator are sized to, and `AileronLoadsInput.hinges_span_in`
  and `actuator_span_in` are already entered-never-invented and unconsumed — is a
  **scope question for a later milestone**, and one that needs a method the
  oracle cannot supply (a chordwise centre of pressure per throw, and a hinge
  line the schema does not carry as geometry). **Filed 2026-09-07.** Tier L if
  taken, and it would reach `modules/aileron.py`, frozen for 0.8.2 under OR-13.

- **The oracle prints an aileron deflection schedule the module does not
  publish.** Appendix A p200 prints the deflections at VA, VC and VD (15.00 /
  10.68 / 4.26 deg and their up throws) that the pick is made from;
  `aileron.aileron_loads` computes them internally and returns only the
  governing loads and speeds, so section 7 states the schedule as a rule in
  words and prints no numbers for it — the report may not re-derive what a
  module did not return (OR-6). Publishing them is additive, one `LoadValue`
  each. **Filed 2026-09-07.** Tier M, and it touches frozen `modules/aileron.py`
  (OR-13).

- #218 — The fuselage applied set is `Fz` alone — is that the model, or the airplane?



- #221 — The oracle reduction resets `weight.items[].consumable`, moving a load.

- #222 — One fuselage quantity is published under two `LoadValue` keys.
- #16 — Review 2026-09-04 small items
- **Overtaken by note 49, close on GitHub:** **#182** (the G-OR-49/OR-93
  contradiction — resolved *decided, not fixed* by **OR-119**: the gate is
  satisfiable as written once OR-93 falls, and OR-93 fell) and **#181** (the
  Subpart-D detail-factor statement — every basis statement now carries "the
  special factors of Subpart D … are the sizing analysis's and are applied by
  no part of sloads").

Two long-standing entries left this list on 2026-08-18 at the issue #13 closure —
**decided, not fixed**, which is why neither survives here under the removal
rule. Both keep their pins; the decisions carry what the bodies used to:

- The **derived `ACRL` air-load divergence** is **D-29**: SELECT's own
  23.349(a)(2) pick is what the derived case names, the ~19 % difference against
  the worked example is accepted and stated, and an `ACRL` case used for sizing is
  **entered, never derived**. Pin:
  `tests/test_wing_case_derivation.py::test_the_acrl_divergence_is_the_documented_one`.
- The **ATR-42 Mach-capped stall exceedance** is **D-30**: nine of 300 points at
  25,000 ft are ordinary stall/Mach-limited flight, not a defect — `nz = n` and
  `n·W` are exact and the fixture is not edited to hide the corner. What is real
  is that CM/CD are evaluated 0.9–3.1 deg past their fit there, moving the
  published tail split by 3.3–44 % with **0 of the 9 SELECTed**, so no sizing load
  moves: filed as **#32** (mark the rows, band B) and **#33** (the solver's own
  silence — **closed 2026-08-22**: the nine are reported *clamped*, and #32's
  marker reads that owner). Pin:
  `tests/test_aero_curves.py::test_the_atr42_stall_exceedance_is_the_documented_mach_capped_one`.
  The GA oracle and both concept fixtures close cleanly.

---

## Open design decisions requiring user input

- [ ] **D-5 — Appendix B twin fixture (blocks parked L-9).** The swept (C7) and
  ONENGOUT (C9) printed oracles want the 10-place twin turboprop as a fixture,
  but Appendix B is **not in the bundled PDF**. *Can the user supply a legible
  Appendix B or the original `.INP`/`.OUT` files?* Until then
  `examples/twin_turboprop.project.json` can't be built and these oracles stay
  blocked. **(Reviewed 2026-07-20: keep blocked as-is.)**

D-1 … D-18 (all but D-5) are answered and recorded in
[`../40_history/03_resolved_decisions.md`](../40_history/03_resolved_decisions.md).
