# The two front-ends converge on one (design note 57)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-11** (owner, in session, under the solo profile —
`DEVELOPMENT_PROCESS.md` §0; rule 1's working-alone branch). Drafted 2026-09-10
from the owner-commissioned scope-reduction review of that day, whose boundary
answers are the governing basis in §2.1; the five rulings in §2.2 were **taken
as proposed on 2026-09-11**. Implementation waits for the **0.8.3 cut** — band
B4 is still in flight — so the milestone's issues are filed and sequenced but
not started. **Milestone 0.8.4 created and the work filed 2026-09-11** as
[#265](https://github.com/Sean074/sloads/issues/265) (D-57.3, the editor)
→ [#266](https://github.com/Sean074/sloads/issues/266) (D-57.2, the tiers)
→ [#267](https://github.com/Sean074/sloads/issues/267) (D-57.4, plots)
→ [#268](https://github.com/Sean074/sloads/issues/268) (D-57.5, fleet)
→ [#269](https://github.com/Sean074/sloads/issues/269) (D-57.7, the seed)
→ [#270](https://github.com/Sean074/sloads/issues/270) (D-57.1/D-57.6, the
retirement), backlog band **B5**; the band is gated on the 0.8.3 cut, not on
this note (AGREED same day).

**Amended again 2026-09-11, at the milestone re-cut** (owner, in session).
The band gains three issues and loses none. **#245** (the issue package's
`data/` becomes the oracle GUI's CSV channel) moves **0.8.3 → 0.8.4**: §1.3
of this note already names `data/` as `export_report`'s successor channel, so
**D-57.6 cannot retire that page until #245 lands** — a dependency this note
stated in prose and the milestones contradicted. **#241** (case identity on the
applied-load CSVs) and **#242** (the axis stanza) follow it in, so `data/` is
born corrected rather than corrected after shipping; the price is that the
0.8.5 baseline wave regenerates digests twice, booked in the backlog's re-cut
preamble. **#255** (the Tail Span Loads page's unconditional conventional-tail
prose) joins the band to **close superseded at #270**, since D-57.1 deletes the
page. D-57.8's sequence is otherwise unchanged: #265 → #266 →
#267/#268/#269 → **#241 → #242 → #245** → #270. The band's gate is
still the 0.8.3 cut, which the same re-cut narrowed to #263's remaining slices.

**Amended 2026-09-11** (owner, in session): the **xlsx workbook retires
with #270** — D-57.6's retirement of `export_report` takes `build_workbook`'s
only consumer, the oracle GUI excludes the workbook by charter (note 32), and
the owner ruled no one uses it; `sloads/export/workbook.py`, its test file,
the download button and the methods stamp's workbook channel sentence are
deleted in the same step. The issue package's `data/` channel (#245) is the
single tabular home; no `data/`-derived workbook is built.

**Tier L.** A front-end retires and the surviving one's charter changes. **No
delivered load changes, no calc change, no schema change** — every module,
report, deck and CSV is untouched; the work is entirely in the shell layer
(`app/`, `oracle_app/`, `app_shell/`, `sloads/workflow.py`'s derived page rule,
and `sloads/field_registry.py`'s visibility filter).

Measurements in §1 are taken at `dev/v0.8.3`, 2026-09-10, with note 56 at AGREED
and its implementation in flight.

---

## 1. What the code does today, and what it costs

### 1.1 Two peers over one analysis model

`app/views/` is **22 pages, 8,802 lines**; `oracle_app/` is **5 modules, 3,031
lines** (of which `form.py`, the one registry-driven renderer, is 1,759).
`sloads/workflow.py` derives the split: **14 steps render in both** (the
`.BAS`-backed steps plus the slices they require, `wf.oracle_steps()`), and
**8 steps are app-only**: `dashboard`, `project_editor`, `tail_span_loads`,
`balanced_cases`, `loads_plots`, `aircraft_comparison`, `results_review`,
`export_report`.

### 1.2 The field delta is 79 paths, and the barrier is charter, not code

The field registry carries **307 input entries; 228 are oracle input paths**
(`fr.oracle_input_paths()`). The remaining **79 sloads-only fields** — thrust,
the rotor/gyro sets, the Part-25 toggle, Mach-margin basis and target speeds,
fuselage moment and lateral body aero, the fuselage 3-D stations,
control-surface span/actuator geometry, and the rest — are enterable only in
`app/` forms or by editing JSON. Rendering them in `oracle_app` is mechanically
cheap: the one renderer already builds any page from registry rows, so the cost
of a field is its classification, not a widget. What excludes them is the
**charter** — note 32 OG-1/OG-2 define the oracle GUI as *"the original suite's
inputs only"*, and gate G2 plus `oracle_input_paths` enforce it.

### 1.3 The oracle GUI has no plotting; everything else it lacks is superseded

`oracle_app/` contains **zero chart calls of any kind** (measured, all five
modules). Of the 8 app-only pages, only four carry capability the surviving
front-end has no equivalent for: the **JSON editor**, the **plots** (V-n,
three-view, span/VMT envelopes, trim sweep), the **fleet comparison**, and the
**WTESTIMA seed button** (which exists unhardened — #78). The other pages are
already superseded: `results_review` by `oracle_app/results.py` (548 lines,
and without L-8c's folded-module omission), `export_report` by the CLI (the
deck delivery path) plus the oracle Report page and issue package (#245 makes
its `data/` the CSV channel), `dashboard` by the derived linear nav (#259 is
its open defect), and `tail_span_loads` / `balanced_cases` by the report's own
tail-span appendix and `balanced_case_rows` — with note 56 D-56.2/D-56.8
already deleting their deck downloads.

### 1.4 Where the open work is going

Nearly the whole **0.9.0 band is `app/views/` hardening**: #29 (the five-section
GUI review that anchors the milestone), #78, #148 (ten `KNOWN_OPEN` silent Apply
writes, including a turboprop's entered engine power erased by its own page on
two shipped fixtures), #247 (M4-11b — six view functions at CC E/F, worst
F(72)), #248 (tooltips, ~45 % coverage), #249 (L-8c), #250 (L-8d's mutation
half), #251 (L-8e), #252 (L-8f); plus #255 (band B5 since the 2026-09-11 re-cut, closing
superseded at #270) and the seven `app/views/`
consumers note 56 D-56.2 must touch. Against that, the four capabilities worth
keeping (§1.3) are roughly **S + M + S–M + S of new, clean work** on the smaller
codebase.

### 1.5 The drift class two front-ends create

#239 is the exhibit: `oracle_app` results captions still claimed ULTIMATE after
note 49 made every delivered load LIMIT — the two GUIs disagreed about the
load-output contract, and G-OR-74's screen sweep covered only one of them.
Every future contract change pays this tax twice while two front-ends exist.

---

## 2. Governing basis

### 2.1 The mission bar (owner, 2026-09-10, in session)

The scope-reduction review's boundary answers: **loads → sbeam and loads →
oracle report are the required deliverables**; the supported aircraft classes
are **GA6, ATR42 and baron_58 at a minimum**; and the front-ends and artifact
set are **on the table**. Nothing in that bar is served by `app/views/`: the
deck path is the CLI, the document path is the oracle Report page, and the 14
shared analysis steps render in `oracle_app`.

Three standing rulings make the convergence lawful rather than novel:

* **C210-15** (oracle GUI fidelity ruling): the fidelity target is the
  *analysis contract*, not the original prompt sequence — UX improvements are
  free so long as consumed values stay correct. Plots and a seed button do not
  breach the charter's spirit; only the *field set* does.
* **OR-16** (note 44): the Report page is the precedent for a page outside the
  derived step set, registered on navigation without entering
  `register_pages`, so gate G2's derived mapping survived an extension once
  already.
* **OG-13 / gate G6**: a project saved by either GUI opens in the other
  unchanged — so retirement of one front-end strands no saved file.

### 2.2 Rulings (owner, 2026-09-11, in session — each taken as proposed)

1. **R-57.1 — the convergence itself.** `oracle_app` becomes *the* sloads GUI
   and `app/views/` retires (deleted, with `app/Home.py`). The alternative —
   harden `app/views/` through the 0.9.0 band and keep two peers — is the
   status quo this note prices in §1.4/§1.5.
2. **R-57.2 — the field-tier presentation.** The 79 sloads-only fields render
   in the surviving GUI as a **marked second tier** — original-suite fields
   keep their `.BAS` provenance exactly as today; sloads-extension fields are
   visually distinguished and each states its own basis. (The registry's
   `Origin` classification already carries the split; `oracle_input_paths`
   survives as the *tier* filter, no longer a *visibility* filter.)
3. **R-57.3 — what ports and what retires.** Port: JSON editor, plots (V-n,
   three-view, span/VMT, trim sweep), fleet comparison, seed button (built
   fresh with #78's hardening). Retire without port: `dashboard`,
   `results_review`, `export_report`, `tail_span_loads`, `balanced_cases`
   (successors named in §1.3). Any line of this table the owner moves, moves.
4. **R-57.4 — the 0.9.0 band's disposition.** With `app/views/` gone, #29,
   #148, #247, #248, #249, #250, #251 and #252 close **superseded** (their
   defect classes die with the forms; anything with an oracle_app analogue is
   re-filed against it at close, per rule 5); #78 re-scopes to the fresh seed
   build; #130 (oracle-side), #34 and #19 stand. The 0.9.0 milestone is
   re-anchored or dissolved.
5. **R-57.5 — naming.** Whether the surviving GUI keeps the "oracle" name and
   `sloads-oracle` entry point, or takes a neutral name with the oracle tier as
   its stated default view. Presentation only, but it gates the docs re-cut.
   **Taken as the first branch:** the name and entry point stand for now; the
   rename mechanics stay deferred (§8) and can be picked up at any later
   milestone without touching this note's decisions.

---

## 3. Decisions proposed

| # | Decision | Alternative rejected |
|---|---|---|
| **D-57.1** | **One GUI.** `oracle_app` (with `app_shell/`) is the single front-end; `app/views/`, `app/Home.py` and the app-only page files are deleted at the end of the milestone. The page set **stays derived** from `sloads/workflow.py`; the derivation rule widens from `oracle_steps()` to a stated set (the 14 analysis steps + the ported pages), and gate G2 is re-cut to that rule — still *derived, not listed*. | *Keep two peers and run the 0.9.0 band.* Rejected on §1.4 (the band's cost buys hardening of a surface the mission bar does not need) and §1.5 (the drift class is structural while two front-ends exist). |
| **D-57.2** | **Two field tiers, one renderer.** Every registry input path renders in the GUI: original-suite fields exactly as today (provenance as help text), sloads-extension fields in a marked section per page, each stating its basis. `oracle_input_paths` becomes the tier classifier. A field neither tier admits is a registry defect, not a hidden field. | *Keep extension fields JSON-only.* Rejected: it re-creates L-8e's uncovered-field class permanently and makes the JSON editor a load-bearing input path. *A mode toggle hiding the extension tier.* Deferred (§8) — marking is required, hiding is optional polish. |
| **D-57.3** | **The JSON editor moves to `app_shell/`** and registers in the surviving GUI first — the escape hatch that decouples every other port from the schedule. | *Port it last.* Rejected: sequencing it first means no capability window in which a concept field is unenterable. |
| **D-57.4** | **Plots port as render-only helpers, written fresh.** One plotting module in the shell; V-n chart, three-view, span shear/BM/torsion and the VMT envelope overlays (with `loads_plots`' external-CSV comparison), reading the same result slices the pages already render as tables. The app's implementations are the *spec*, not the source — `_tab_design_speeds` F(72) and `_three_view` F(63) are M4-11b's own exhibit for why the code is not worth importing. | *Import the existing view functions.* Rejected: it ports the complexity debt the 0.9.0 band existed to pay. *No plots (report figures only).* Rejected: the interactive overlays are genuinely used in concept work and the report cannot carry them. |
| **D-57.5** | **Fleet comparison ports.** It is the Phase-C *"assess vs similar airplanes"* requirement (plan §1), so it lands with the extension tier it belongs to, reading `reference_aircraft.csv` unchanged. | *Retire it.* Rejected: it is mission-traceable, mature, and cheap (S–M). |
| **D-57.6** | **Five pages retire without port** — `dashboard`, `results_review`, `export_report`, `tail_span_loads`, `balanced_cases` — each closing citing its successor (§1.3). #259 closes superseded with the dashboard; the L-8c omission dies with `results_review`; #255's fix site vanishes if it has not already landed in 0.8.3. *(Amended 2026-09-11:)* the **xlsx workbook** goes with `export_report` — module + test + button + methods-stamp sentence — the owner having ruled it unused; `data/` (#245) is the tabular channel and no replacement is built. | *Port them for completeness.* Rejected under the mission bar: each duplicates a surviving owner, and duplication is the #239 class. |
| **D-57.7** | **The seed button is built fresh in the surviving GUI with #78's hardening in its first version** — seeded rows loudly incomplete until positioned and tagged; merge/refuse/replace stated before the click. #78 re-scopes to this. | *Port then harden.* Rejected: rule 4 — building the known defect into the new home to fix it later is the anti-pattern. |
| **D-57.8** | **Sequencing: after note 56's implementation lands.** Note 56 already edits seven `app/views/` files in 0.8.3; this note deletes them in 0.8.4. Within 0.8.4: D-57.3 (editor) → D-57.2 (field tiers) → D-57.4/D-57.5 (plots, fleet) → D-57.7 (seed) → D-57.6 + deletion + the guard re-cuts, so the surviving GUI is complete before anything is removed. | *Interleave with 0.8.3.* Rejected: two agents editing `app/views/` in one milestone, one improving and one deleting. |

---

## 4. Gates

1. **No load moves.** Appendix A oracles, twin closure suites, the report
   baselines and every delivered CSV are byte-identical — this note touches no
   calc, report or export module.
2. **Every fixture saved by the retired GUI loads and re-runs identically** in
   the surviving one (OG-13 widened to "the retired GUI's files"): all bundled
   examples plus the frozen schema fixture, asserted by round-trip.
3. **Every registry input path is enterable** in the surviving GUI or carries a
   documented JSON-only classification with a reason — a registry-walking
   guard, closing L-8e's class structurally (rule 3: the drift guard lands with
   the convention).
4. **Every sloads-extension widget states its basis** and is visually marked;
   the same guard walks the tier split.
5. **G-OR-74's screen sweep covers the whole surviving GUI** — `_GUI_TREES`
   re-cut to the single front-end; the #239 class has one tree to drift in and
   the sweep reads all of it.
6. **Exactly one `st.set_page_config` remains** in the repository
   (`tests/test_app_shell.py`'s existing guard, now over one entry point).
7. **The no-edit journey holds on the survivor**: the whole-GUI journey walk
   re-aims at the surviving GUI — every bundled example through every page,
   every Apply pressed with nothing entered, project byte-identical. The
   `KNOWN_OPEN` list dies with the pages that own its entries; the gate starts
   empty and stays empty.
8. **No retired page is reachable**: `workflow.py`'s derived set, the nav
   registration and `tests/test_workflow.py`'s drift guard agree; deleted view
   files leave no import edge (ruff/mypy clean is the existing merge gate).

---

## 5. Effect vs error bar (rule 6)

This is not a physics/fidelity item and rule 6 does not gate it: **no delivered
load changes** (gate 1 asserts it). The justification is measured maintenance
and drift-class removal: **~8,800 lines** of frozen UI retired against roughly
four small-to-medium fresh builds; the 0.9.0 band's **~8 rows** closed
superseded; the two-front-end contract-drift class (#239's) structurally dead;
and the L-8e uncovered-field class converted from a backlog item into a guard.

---

## 6. What this supersedes / corrects

* **`03_gui_rework_plan.md` (Phase G) becomes historical** — its shipped steps
  (G0–G6b) stand as history; its unshipped remainder is the 0.9.0 band this
  note closes. Roll to `40_history/` at the 0.8.4 cut.
* **#29, #148, #247–#252** close superseded per R-57.4; **#78** re-scopes
  (D-57.7); **#259** closes with the dashboard; **#255**'s fix site is deleted
  if still open. **#130, #34, #19** are untouched.
* **The `app/views/` freeze** (backlog *Frozen* list) and its OR-15 admission
  machinery for that tree become moot — there is no tree to freeze.
* **Note 32's OG-1/OG-2** are amended, not withdrawn: the page set stays
  derived and the renderer stays single; only the *"original suite's inputs
  only"* clause is replaced by the two-tier rule (D-57.2). Gate G2 survives
  re-cut, per the OR-16 precedent.
* **Note 56 is unaffected** — its seven `app/views/` consumer edits land first
  (D-57.8); this note then removes the files they touched.

---

## 7. Closure obligations (tier L)

* `changes/<slug>.changed.md` + `changes/<slug>.history.md` in **full step
  format**.
* `docs/10_standard/PROGRAM_SPEC.md` — the front-end section re-cut to one GUI.
* `docs/10_standard/PROJECT_GUIDE.md` §4/§7 — package tree without `app/views/`;
  the two-front-end paragraph rewritten.
* `docs/10_standard/00_program_overview.md` — entry points re-cut per R-57.5.
* `docs/10_standard/GUI_design.md` — re-pointed at the surviving GUI.
* `CLAUDE.md` — the Architecture summary's two-front-end sentence and the lint
  paths (`app/` scope) re-cut; the ruff/CI path lists updated with
  `tests/test_ci_conformance.py` kept green.
* `sloads/workflow.py` — the derived-set rule re-cut (D-57.1), drift guard
  updated with it.
* `docs/00_INDEX.md` — row for this note *(landed with the draft)*.
* **No `theory_sources.md` citation** — stated explicitly: this note changes no
  equation and cites no oracle. Gate 1 is why.
* **No schema change** — `SCHEMA_VERSION` stands; field *visibility* moves,
  field *storage* does not.

---

## 8. Deferred

* **R-57.5's rename mechanics** (entry-point names, `pyproject.toml` scripts,
  README) — decided with the ruling, executed at the end of the milestone.
* **A view toggle hiding the extension tier** (a "replication only" display
  mode) — polish over D-57.2's marking; take up only if the mixed page proves
  noisy in use.
* **Porting the trim & stability sweep** (G5) — a plots follow-on once D-57.4's
  helper exists; it re-runs the balance, so it ports against the same calc
  surface with no new physics.
* **`app_shell/` slimming** — widgets that existed only for `app/views/`
  callers (if any survive the deletion unused) are #16-class dead code, swept
  under rule 4 at the end of the milestone.
