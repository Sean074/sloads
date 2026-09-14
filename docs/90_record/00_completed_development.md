# Completed Development

The authoritative record of what has shipped: completed modules/phases, key
decisions, and resolved defects. Items move here from
[`../30_future/00_backlog.md`](../30_future/00_backlog.md) the moment they close,
with a matching `CHANGELOG.md` entry.

Each entry uses the step format: **Objective**, **Deliverables**, **Test /
Acceptance**, **Key decisions**.

**Live cycle only.** This file holds the current release cycle plus the previous
release cut. Older blocks roll into frozen, do-not-edit archives at each release
(`RELEASE_PROCESS.md` §4): the 0.8.3 cycle and the 0.8.2 cut are in
[`62_completed_development_to_0.8.3.md`](62_completed_development_to_0.8.3.md),
the 0.8.2 cycle and the 0.8.1 cut in
[`59_completed_development_to_0.8.2.md`](59_completed_development_to_0.8.2.md),
the 0.8.1 cycle and the 0.8.0 cut in
[`51_completed_development_to_0.8.1.md`](51_completed_development_to_0.8.1.md),
the 0.7.1 and 0.7.2 release cuts in
[`41_completed_development_to_0.8.0.md`](41_completed_development_to_0.8.0.md),
the 0.7.0 cycle and the 0.7.0 cut in
[`37_completed_development_to_0.7.1.md`](37_completed_development_to_0.7.1.md),
the 0.6.0 cycle and the 0.5.0 cut in
[`35_completed_development_to_0.6.0.md`](35_completed_development_to_0.6.0.md),
everything before 0.5.0 in
[`11_completed_development_to_0.5.0.md`](11_completed_development_to_0.5.0.md).
Tier S closures do not write here (a `changes/` fragment is their record); tier M
writes one paragraph, tier L the full step format — **as a `changes/<slug>.history.md`
fragment** (design note 28 MD-4), rolled to the top of this file at release cut, so
concurrent PRs never edit the same line here. Only the release-cut block itself is
written directly, by the release manager.

---

## Release cut: **sloads 0.8.4** (the two front-ends converge on one), tag `v0.8.4`, 2026-09-14

**Objective.** Close band **B5**. The suite had grown **two** Streamlit
front-ends over the same calc package — `app/Home.py` with 21 `app/views/`
pages, and the oracle GUI derived from `workflow.py` — and every cross-cutting
change was being paid twice, in two dialects, with the two disagreeing about
what the program does. Design note **57** ruled that one survives and named the
rule that made the removal safe: **D-57.8, the survivor is complete before
anything is removed.** Design note **60**, written immediately after the 0.8.3
cut, amended it with what a page-level audit could not see — the retiring
front-end carried **twenty** figures, not the four D-57.4 named, and
`app/views/export_report.py` was the only production consumer of
`content.build_report`, so retiring the pages would have retired the **summary
report** without naming it. The milestone is therefore mostly *port*, and the
deletion is its last step rather than its first.

**Deliverables** (the `[0.8.4]` changelog section is the release note):
- **One front-end (#270, note 57 D-57.1 + D-57.6, tier L).** `app/views/` and
  `app/Home.py` deleted — **22 pages, 8,461 lines** — with
  `content.build_report`, the summary report's LaTeX path, `report/bundle.py`
  and the `.xlsx` workbook. The page set is `workflow.gui_pages()`: the fourteen
  derived analysis steps plus three declared non-step pages, so a page cannot be
  added to the GUI without being a step or declaring itself an exception.
- **Twenty figures port under one owner (#267, note 60 D-60.1…D-60.6, tier L).**
  `sloads/report/figures.py` is the figure catalogue — one row per *family*,
  naming the page, the producer and whether it is pre-run or post-run;
  `app_shell/plots.py` renders a `PlotData` as Plotly and is a **peer** of
  `plots_tex`'s TikZ over the same producers, with a guard walking the GUI trees
  for a `PlotData` or `Series` constructor so the GUI derives no figure data of
  its own. Nineteen producers became callable per figure, which is the use the
  port was asked for: checking an input before running the whole process.
- **The fleet comparison ports and stops owning anything (#268, D-57.5, tier M).**
  Phase C's *assess against similar airplanes* is now `oracle_app/fleet.py`,
  marked ✦ as an sloads extension and registered on the navigation only. The
  reference fleet moved to `sloads/data/` (a `pip install sloads` had carried no
  fleet to compare against) and the subject's priority chain moved into
  `sloads.fleet` — where gate DG-3 caught it integrating the wing planform
  itself, a fifth owner invisible to the guard while it lived in `app/`.
- **The survivor completed before the removal (#266, #269, #245, the report
  merge, tier M each).** Every input field rendered, in two marked tiers; the
  weight data base's seed button adds rather than replaces (closing **#78**);
  the issue package's `data/` becomes the one tabular channel, with the
  per-module downloads and the results zip retired against a column inventory
  that is a test rather than a one-pass check; and the summary report's
  cross-cutting sections — the axis statement and the FAR 23 Subpart C coverage
  matrix — merge into the oracle report **before** `build_report` goes, so the
  document that ships is the one that carries them.
- **The delivered files say which case and which frame (#241, #242, tier M each).**
  A row's case was named by its *description*, and a description is not an
  identity — LANDLOAD's 33 ground conditions share eight of them, and a twin's
  two engine mounts published six conditions under three strings; `case_ids.index_case_id`
  is now the one owner of the suffixes. Every delivered file states the frame
  its numbers are in, `MyyAxis` becomes `TorsionAxis` because the fin's torsion
  is `Mz`, and the AXES stanza's **+Mx and +Mz were backwards on every file**.
- **The record corpus splits by function (note 61, tier M).** Design notes leave
  the status-driven move behind and are filed in `25_notes/` from the day they
  are written; `90_record/` leaves the default search path; a tier-M/L closure
  writes **one** fragment whose changelog bullet is derived from its lead phrase.
  This cut is the first run of that rule.
- **The end-of-milestone sweep (note 57 §6/§8, tier S).** The `app_shell/`
  slimming removed the five names the deletion left unreachable — the three
  `*_limit_csv` writers, whose only callers were the deleted pages once #245
  settled `data/`, and the whole of `optional_slice`, whose Apply-button form of
  the #143 rule has no Apply step left to serve (the rule survives at
  `oracle_app/form.py`'s named gestures, and `CONVENTIONS.md` §7 now points
  there). Around forty statements in the code that still described two
  front-ends are re-cut, and the **release-state sentence** stops naming a GUI
  that does not exist. **R-57.5's rename executes as nothing:** the ruling took
  the branch where the name and the `sloads-oracle` entry point stand, and the
  milestone changed the *argument* for a rename, not the decision — if it is
  taken up it is its own row with its own deprecation of the console script.
- **Found at the cut and fixed pre-cut (the §3.5 read):** the Tail Loads
  advisory sent readers to a **Tail Span Loads** page #270 had deleted, and its
  guard pinned the wording rather than the rule, so it passed over a caption
  pointing at nothing. The advisory now names the report's *Spanwise loads*
  subsections and the export decks, and the guard asserts that no caption names
  a step absent from `workflow.gui_pages()`. `README.md`'s layout tree, which
  still drew `sloads/report.py` and `sloads/models.py` as modules, went with it.
- **Version** `0.8.3` → **`0.8.4`**. Schema **v66 unchanged** — the milestone
  moved front-ends, not the input model.
- **Changelog cut** — `scripts/build_changelog.py 0.8.4 --date 2026-09-14 --roll`:
  **16 fragments** consumed into `## [0.8.4]`, **11 history entries** rolled to
  the top of this file, a fresh empty `[Unreleased]` opened.
- **Record roll** (`RELEASE_PROCESS.md` §4 step 3, amended by note 61): **no
  note moves** — CV-3 retired that step, and a note's Status line is what
  changes when its work ships. Both live record files were over the
  **1,500-line** threshold, so both rolled in the one pass: everything below the
  0.8.3 cut block froze into
  [`62_completed_development_to_0.8.3.md`](62_completed_development_to_0.8.3.md),
  and the changelog's blocks older than 0.8.3 into
  [`CHANGELOG_to_0.8.2.md`](CHANGELOG_to_0.8.2.md) — the first run of CV-5, and
  the reason the changelog had reached 11,249 lines.
- **Gates at cut:** `pytest` **3,539 passed / 7 skipped / 2 xfailed / 0 failed**
  (3,422 at the 0.8.3 cut), `ruff` clean, `mypy` clean (`sloads/`, 100 source
  files), `scripts/smoke_test.sh` **PASS** (the one GUI boots through the
  `sloads-oracle` console script, CLI CSV checked), `scripts/backlog_issues.py check`
  clean, `scripts/branch_protection_snapshot.py --check` matches on 7 tracked
  keys, the §3.5 by-hand walk done by the owner, no open CRITICAL/MAJOR review
  findings.

**Key decisions.** *Two implementations of one thing do not cost twice the
effort — they cost the ability to say what the program does.* The measured
saving from converging was **one** tier-S row of duplicated work, and that was
never the case for it: it was that a shipped statement had two owners, so the
GUI could describe a capability the other GUI had and this one did not, and no
gate could tell. The milestone's real deliverable is that there is now one
answer to every question a reader asks of the interface.

*Complete the survivor first, and the deletion becomes arithmetic.* D-57.8 is
why #270 is one commit at the end of a milestone rather than a fortnight of
regressions: by the time the pages went, everything they did was already done
somewhere the surviving GUI could reach. Note 60 is what that rule looks like
when it is enforced honestly — the audit that produced D-57.4's four figures was
wrong by a factor of five, and the correction cost two rows and a re-tier rather
than a shipped gap.

*A guard that pins wording outlives the thing it was guarding.* The Tail Loads
caption named a page that had been deleted, and its test passed the whole time
because it asserted the caption's *text*. The re-aimed guard asserts the
property — no caption names a step the GUI has no page for — which is the same
correction the milestone made to the figure catalogue and to `CONVENTIONS.md`
§7: state the rule at an owner, not the instance at a copy.

**Band B5 retired with the cut; band B6 (0.8.5 — the defect and polish cleanup,
on the converged surface) is the milestone in flight.**

- **The applied-load CSVs state their case identity (#241, 2026-09-08 review §4,
  tier M, 2026-09-13)** — the six delivered applied-load files named each row's
  case by its *description*, and a description is not an identity. LANDLOAD's 33
  ground conditions share eight of them — one description, three loadings, three
  different sets of wheel reactions — so the gear file delivered 33 cases a
  reader could separate into eight groups and no further, and the Baron's two
  `CONTINENTAL IO-550-C` mounts published six conditions under three strings. The
  id that would have settled it, `AppliedLoad.case_id`, was populated on every
  row by every producer and emitted by none; the report's own applied appendix
  printed it while the file beside it did not, so the page and the file were not
  in fact the same row. All six files now lead with `Case ID`, `Case` and
  `Loading`: the minted id the load-case index is keyed by, the description, and
  the named CG the case was computed at (blank where the case names none, never
  guessed). The two identity strings are read off the case's own `CaseRef` by one
  owner, `report/applied.case_identity`, rather than by each of the five
  producers spelling the read for itself, and the header block of every file says
  what the three columns are and that `Case` is not unique. The twin's half of
  the finding was not a file defect at all: the per-engine tag was the engine
  *designation*, which two engines of one model share, and it was applied to the
  title *after* the `CaseRef` was minted — so the index itself described `EM-01`
  and `EM-04` in the same words. `modules/engine.engine_tags` now mints one
  distinct label per installation — the designation where it already separates
  them, plus the side (off the engine's own butt line) where it does not, plus
  the engine's position in the rare case that still collides — and the tag goes
  on before the id is minted. Nothing renames on an installation whose engines
  differ, so no single-engine title in any shipped example moved. A delivered id
  the index lists under a shorter name now joins through one owner too,
  `case_ids.index_case_id`: a handed twin (`W-05R`) and the 23.371(b) gyro
  condition's four sign combinations (`EM-06a…d`, which one `ConditionResult`
  cannot carry four `CaseRef`s for, Step D1) are suffixes on an id that *is*
  listed, and `report/render`'s minter reads the same suffix alphabet that strip
  removes. Guarded by `tests/test_applied_case_identity.py`: the round trip —
  every delivered `Case ID`, on every bundled example and all six components, is
  an id the case index names, and every `Loading` cell is that index row's own
  `CG` — plus the two collapses asserted directly (33 ids under 8 descriptions;
  six mounts under six), the gyro suffix stated rather than tolerated, and an AST
  walk of `report/applied.py` that fails any `AppliedLoad` construction which
  does not state its identity, so a producer added later cannot half-fill the
  columns. The Imperial baseline gained the gear and engine applied channels in
  the same change: four of the six were digested and two were not, which is how
  the bytes of the file with the most cases in it came to move unguarded. Every
  digest that moved is one of those six files, the engine module's own CSV/text
  output on the three multi-engine examples, and their case index.

- **The delivered files start saying which way their axes point, and stop
  stating zeros their own rows fill (#242, 2026-09-08 review C2+C3+C4, tier M,
  2026-09-13)** — the review checked the CSVs against the requirement they exist
  to serve, found the *data* airplane-global and frame-correct throughout, and
  found the *self-description* missing the one sentence a forwarded file cannot
  do without: nothing anywhere said that `x` is the fuselage station positive
  aft. Note 56 narrowed the finding on its way here — the deck-companion span,
  chordwise and fitting CSVs it also covered went with their decks, and with
  them `tail_chordwise.csv`'s second meaning of `Axis` and
  `control_surface_loads.csv`'s `Fz`-on-a-lateral-normal — so what was left was
  the report's own set and the two halves of C3 that had survived into it. The
  fix is one stanza in the methods stamp, because the stamp is the single
  statement every channel already wraps (G8-3), and the axis words live in
  `export/coordinates` rather than in the stamp, because `CONVENTIONS.md` §1
  already names that module the single edit-point for the map and a sentence
  that is not beside the thing it describes is a sentence that outlives it. Two
  exceptions are declared rather than papered over: the gear report carries the
  manual's ground-line frame in three of its columns and airplane axes in every
  other, and says so in its own block; and the applied files' torsion-axis
  column was renamed `TorsionAxis` because the fin's torsion is `Mz` and a
  column asserting `Myy` was, on one of six files, exactly the class of claim
  the issue was filed about. Working the file set turned up the same defect from
  the direction prose cannot defend itself in: note 56 D-56.9 had re-aggregated
  the delivered rows onto the LRA grids, where each load carries the lever-arm
  couple of its own offset, and the hand-written structural-zero blocks — the
  numbers having moved and the sentences not — were declaring `Mx`, `My` or `Mz`
  zero "throughout" on four of the six files while the rows beside them were
  filled. So OR-140's apparatus was split: whether a column is zero is now
  **measured** from the rows being written, the prose supplies only the reason,
  a zero that belongs to this configuration rather than to the model is stated
  as that, and a file at grids says it is at grids. C4's riders were taken where
  they were the same defect class — the V-n file now carries the two table notes
  that define five of its nineteen columns, read off the `Table` objects the
  appendix renders so the two cannot drift, and `sloads/csv_text.py` owns the
  line terminator that every stamped file used to mix — and left where they were
  not: the `lbf`/`psi` display vocabulary lives entirely in `app/views/`, which
  #270 deletes, and the `N·m` middot is an encoding decision (a UTF-8 BOM, or an
  ASCII-ised SI vocabulary) that moves the whole SI channel and wants an owner
  ruling rather than a rider on an axis stanza. Guarded by
  `tests/test_delivered_frame_statement.py`: every stamped channel states all
  three axes and their senses; the axis words appear in no second place under
  `sloads/`; the stanza is identical on two different airplanes; the gear
  report places every one of its frame-bearing columns on one side of the split,
  checked against the field list so a column added later fails rather than
  passes; no applied file claims a zero its own rows fill and no reason outlives
  its column, over every bundled example and all six components; a file at grids
  says so and one that is not does not; and no delivered channel, decks
  included, contains a carriage return.

## Step — One front-end (#270, design note 57 D-57.1 + D-57.6, tier L, 2026-09-13)

**Objective.** End the two-front-end drift class by deleting the front-end the
mission bar does not need, after — and only after — everything worth keeping had
been ported into the one that survives. Note 57's §1.4/§1.5 priced the
alternative: hardening `app/views/` through the 0.9.0 band buys maintenance on a
surface whose every capability duplicates a surviving owner, while the drift
class is structural for as long as two front-ends exist. D-57.8's rule governed
the sequence and was honoured to the letter — #265 through #269 built the
survivor's editor, field tiers, plots, fleet page and seed button, and #278
merged the summary report's cross-cutting sections into the surviving document
— so this step removes and re-cuts, and adds no capability.

**Deliverables.** `app/` deleted: `Home.py` and 21 `views/*.py`, 8,461 lines.
With it, the artifacts whose only consumer it was: `content.build_report` and
its nine section builders, `latex.render_document`/`render_report` and the
document furniture (title page, running heads), `report/bundle.py`,
`export/workbook.py` and the `openpyxl` dependency. `content.py` falls from
2,639 lines to 653 — the content model (`Section`, `Table`, `Figure`,
`PlotData`, `Units`, `ComponentLoads`) plus the three plot-data producers the
document and the GUI both draw from — and `latex.py` becomes the emitters
`oracle_latex.py` assembles a document from. `workflow.py` gains `GuiPage`,
`NON_STEP_PAGES` and `gui_pages()`; `Oracle.py` builds its navigation from that
declaration and names no page set of its own. `validation.PAGE_EXPORT` becomes
`PAGE_REPORT` and its five checks re-point at the page that writes the
deliverable. `cli.py --report` renders the surviving document, `cli._load` gives
every route the one error contract, and `report/methods.py`'s channel sentence
names the surviving human channels.

**Test.** Note 57 §4's eight gates, each asserted rather than asserted-about.
**No load moves** (gate 1): the Appendix A oracles, twin closure suites, report
baselines and every delivered CSV are untouched — this step edits no calc
module. **A project the retired GUI saved opens here** (gate 2, OG-13 widened):
`test_oracle_gui.py` reverses the G6 round-trip, driving every bundled example's
full unreduced project through all fourteen pages, because the question a user
has is not whether two peers can read each other's files but whether the file
they already saved still opens. **`_GUI_TREES` covers the survivor whole** (5)
and **exactly one `st.set_page_config`** (6) hold unchanged over one tree. **The
no-edit journey** (7): `test_gui_journey.py` is re-aimed at the surviving
renderer, and its `KNOWN_OPEN` list is **empty and asserted empty** — it carried
five #148 diffs that the `app/views/` freeze forbade fixing, all of them
properties of a page that rebuilds its slice from its own widgets, which is what
a hand-written view does and a generic renderer over the field registry does
not. **No retired page is reachable** (8): `gui_pages()`, the navigation and the
workflow guards agree, and ruff/mypy leave no import edge. Six test files were
deleted with the pages they drove and fourteen re-aimed; three guards that read
`app/views/*.py` sources were re-cut to sweep the surviving display trees rather
than name files, because a surface that is not on a list is a surface the guard
does not reach.

**Key decisions.**

- **The page set stays derived and states its exceptions.** D-57.1 widened the
  rule from `oracle_steps()` to a stated set; the implementation makes the
  stated half a declaration with a reason per row (`NON_STEP_PAGES`) rather than
  three hand-appended blocks in the entry point. Gate G2's claim — *there is no
  page list* — then covers the whole page set instead of the derived part of it.
- **`PHASES` shrinks to four.** `Start`, `Load-case plotting` and `Export` held
  the six GUI-only steps and nothing else. Keeping them would leave three phases
  no step can ever be in, which is drift with a name; what they described did
  not retire with them — the project is carried by the shell, the figures are
  drawn on the pages that produce them (#267), and the deliverables leave through
  the CLI and the Report page — but none of those is a step of the analysis,
  which is what the tuple partitions.
- **Two analysis steps keep no page.** `tail_span_loads` and `balanced_cases`
  run registered calc modules whose deliverables are the report's tail-span
  appendix and the balanced deck. `STEPS` is what the suite does, not what the
  GUI shows, and saying so in the module docstring was cheaper than folding two
  real steps into a mapping built for contributors.
- **The audit outlives its subject.** `front_sections.SUMMARY_DISPOSITION` was
  written at #278 saying it would retire with `content.py`. It does not:
  `content.SECTIONS` moved beside it as `RETIRED_SUMMARY_SECTIONS`, because an
  accounting whose subject has been deleted accounts for nothing, and note 60's
  gate 12 would have stopped being enforced at exactly the commit that made it
  matter.
- **Three rules that lived in a page moved to an owner, rather than dying with
  it.** M4-17c's zero-waterline refusal is `validation.landing_cg_below_axle`,
  a pure predicate the GUI renders on the page its tag names. G-53.7's
  "clockwise seen from the pilot's seat" is the `prop_direction` field's own
  registry row, so it reaches the GUI, the data dictionary and the report's
  field provenance together. #124's horsepower precedence is guarded by a sweep
  asserting no display module reads the fields at all. Each was a caption in a
  deleted file; each is now the one place the rule is stated.
- **R-57.5's rename and the Phase G plan's roll to history stay deferred.**
  Note 57 §6/§8 puts both at the 0.8.4 cut rather than in a row, and the branch
  taken keeps the `oracle_app` name and the `sloads-oracle` entry point. What
  this step takes from that list is the lint-path half the issue names: `app/`
  leaves the ruff scope in CI, `solo_close.sh`, `CLAUDE.md` and `README.md`, and
  `smoke_test.sh` boots one front-end because there is one.

- **The two reports become one (#278, note 60 D-60.7…D-60.11, tier M, 2026-09-13)** —
  Note 57's convergence retired `app/views/` and, through it, a 2,632-line document
  it never named: `app/views/export_report.py` was the only production consumer of
  `content.build_report`, so deleting the page would have deleted the summary report
  and taken with it the only statement of the airplane reference frame either front
  end makes, the only FAR 23 Subpart C coverage matrix, and the document-level
  governing safety-factor table. Note 60 named the deletion and conditioned it on a
  merge; this step is the merge. Four cross-cutting sections now print as the oracle
  report's front matter after the introduction, through a declared
  `FRONT_SECTIONS` table that leaves the analysis section set derived from the
  workflow and lets the body renumber itself around them. They are built once, by
  `sloads/report/front_sections.py`, and printed by both documents while both exist,
  because a merge implemented as a copy is the drift the convergence was called for.
  The fourth asset — the bundle manifest — closed a gap of its own: the document now
  carries its own list of the files that travel with it, control files and `data/`
  alike, computed with the document rather than at packaging time. What is *not*
  merged is declared key by key in an audit table a guard test reads, so no section
  of the retiring document leaves without a successor or a stated reason; that audit
  is what forced decisions on the approved-corrections table and on the balanced
  free-free cases rather than letting either be lost between two changes that each
  looked complete. `build_report` itself is untouched: it is deleted with the page
  at #270, after its content has reached its new home.

- **The oracle GUI renders every input path in two marked field tiers (#266, design note 57 D-57.2, tier M, 2026-09-13)** —
  the second row of band B5 and the one the convergence depends on: `app/views/` cannot retire while 83 fields are
  enterable only there. The barrier was one line — `page_groups` filtering on `oracle_input_paths()` — and the charter
  it enforced (note 32 OG-1/OG-2, *"the original suite's inputs, and nothing this replication added"*) had no way to
  distinguish *not asked for by the original programs* from *unreachable*. Both tiers render now; `field_registry.tier_of`
  classifies every path `SUITE`/`EXTENSION`/`JSON_ONLY`, and the extension tier is marked on the widget rather than
  gathered into a section, because a record holds fields of both tiers and a second section over one record emits its
  row counter, its seed and its remove control a second time under the same Streamlit key — D-57.2's *"marked section
  per page"* amended to marking that travels with the field. Marking is applied in `form._field_label` and `form._help`
  alone, the two functions every widget passes through, so a grid column is marked in the only place a grid column can
  be. `oracle_input_paths()` keeps its name and its callers but stops claiming to bound what the GUI writes: what it
  bounds — and what gate G5 was always really testing — is the tier, *with only these fields populated every
  oracle-page module still runs and every Appendix A oracle still passes*. Twenty fields on three records whose path
  crosses a `[]` hop stay JSON-editor-only, declared in `JSON_ONLY_RECORDS` with the reason, and note 57 gate 3's
  registry-walking guard re-derives that classification from the renderer's own addressing so it cannot be used to hide
  anything. Gates 4 and 5 (note 60 §5) assert here: every extension widget marked and stating its basis, and G-OR-74's
  screen sweep reading the tree at all — which is #239, closed the day before for this row.

- **The figure residue is ruled on rather than deleted (note 60 §9 amended
  2026-09-13, tier M, 2026-09-13)** — #267 ported sixteen of note 60 §1.1's
  twenty figures and #268 took the fleet comparison, leaving three that had no
  report producer. They were reported at #267's close instead of being allowed
  to disappear with `app/views/` at #270, and the owner ruled on all three in
  session. **Figure 6, item weight against fuselage station, ports here.** The
  reason it could not port at #267 was that `PlotData` had no way to express a
  cloud of named points; #268 added `Series.marker` and `Series.labels` for the
  fleet scatters, which made this figure a producer of about fifty lines —
  `content.item_station_plot_data`, one series per `MassItemKind` so that a
  heavy item at an extreme station can be read as the airplane or as a loading,
  named points on hover, and the oracle report's section 2.2 printing it beside
  the weight/CG envelope so it satisfies gate 10 like every other family. The
  shapes that tell the three kinds apart are stated in the existing
  `Series.style` channel as a pgfplots `mark=` token and honoured by both
  renderers, shape and not colour because §4.3 requires the printed figure to
  read in greyscale. **Figure 18, the wing + fuselage snapshot, retires
  superseded** by the two distributions #267 put on the pages that compute them.
  **Figure 19, imported against computed, is deferred with the capability it
  needs** — an inbound channel for an externally computed load distribution,
  filed in backlog band C — *additional analysis
  capability, design notes first* — and requiring a design note at AGREED first,
  because the hard part is the contract (columns, stations, units, and what a
  disagreement means) and not the overlay. The point of the row is that #270
  now deletes a page and not a capability nobody decided about.

## Step — Twenty figures port under one owner (#267, design note 60 D-60.1…D-60.6, tier L, 2026-09-13)

**Objective.** Give the surviving front-end the figures it lacks, without
giving the project a second owner of what a figure is. Note 57 D-57.1 makes
`oracle_app/` the survivor and D-57.8 requires it complete before anything is
removed; at 0.8.3 it contained **zero chart calls** while `app/views/` carried
twenty at thirteen pages, **nine of which are shared analysis steps** the
survivor already rendered with no figure at all. Note 57 §1.3 had counted
app-only pages and so could not see the other sixteen figures going, and
D-57.4's *written fresh — the app's implementations are the spec, not the
source* would have built a second figure owner beside the report's, which is
the drift class (#239) the whole convergence exists to end.

**Agreed first.** Design note 60 (AGREED 2026-09-13, owner), Block A. It
amends note 57: D-57.4's four-figure port list and its *written fresh* ruling
are **withdrawn** (R-60.2, D-60.1), #267 is re-tiered M → L (R-60.3, D-60.5),
and gates 9 and 10 join note 57 §4 (D-60.6, D-60.2).

**Deliverables.** `sloads/report/figures.py` — the catalogue: `Stage`
(`PRE_RUN`/`POST_RUN`), `FigureFamily`, `catalogue()`, `families_for_step`,
`results_for_step` and `build_step_figures`, thirty-nine families over the
fourteen oracle pages. `Figure.family` on the content model, defaulted to the
key so a single-instance producer states nothing and a multi-instance one must.
Nineteen figure builders lifted out of `oracle_sections.py`'s section builders
into public functions (`geometry_figures`, `vn_figures`, `wing_distribution_figures`,
`tail_chord_figures`, `oei_figures`, `attitude_figures`, `lumping_figures`, …),
each taking a `Project` and, where needed, the module results — and the section
builders re-pointed at them, so the document and the screen are one
construction. `app_shell/plots.py` — the Plotly peer of `plots_tex`: it
translates the producers' pgfplots line styles to dash patterns and weights,
colours the traces (a screen has no greyscale constraint; the stated encoding
is kept as well, so a reader with the PDF open sees the same dashed curve),
closes and fills a `Series.closed` region, holds a drawing to a 1:1 aspect and
a graph to none, and renders a figure's `absent_reason` rather than an empty
axis. `oracle_app/figures.py` — two blocks per page, *what is entered* above the
results and *what was computed* below them, each stating which it is.
Two figures gained producers they never had: the balancing tail load against CG
and the static margin against CG (note 60 §7), built from `trim_sweep` and the
Configuration module's tail-volume neutral point and printed by the oracle
report's flight-envelope subsection.

**Test.** `tests/test_figures.py` holds note 60 §5's two new gates.
**Gate 9** — every family builds for every bundled example without raising and
every instance carries either `PlotData` or an `absent_reason`; asserted on a
blank `Project` too, because a project being checked before it is complete is
the pre-run tier's normal subject. **Gate 10** — parity both ways, walked over
families against the **built** oracle report rather than against a list: a
report figure with no catalogue row fails, and so does a catalogue row no
document produces. Both directions were mutation-checked (dropping
`lumping_wing`, adding a family nothing produces, and removing `family="vn"`
from the V-n producer each fail the suite). Beside them, the page-level half in
`tests/test_oracle_gui.py`: each of the fourteen pages renders exactly the
blocks its catalogue rows imply, the stage note is present, and no GUI module
anywhere constructs a `PlotData` or a `Series`.

**Key decisions.** *One producer set, two renderers* (D-60.1) — the alternative
was a second derivation, which is the defect. *Families, not keys* (D-60.2) —
the guard must not parse `vn_0` into `vn`, or it would be the guard and not the
producer deciding what a family is. *Pre-run means entered data drawn, and it is
stated per family rather than derived from the argument list* (D-60.4) — five
delivered load distributions reach the calc directly from a `Project`, so
classifying on "takes no results" would have labelled them input echoes, which
is precisely the mistake the classification exists to prevent. *Parity is
checked against the document, not a list* — a list in a test is a second
catalogue, and that is how D-57.4 came to name four of the twenty figures that
were actually there.

**Not ported, and why.** Three of note 60 §1.1's twenty have no report
producer and do not gain one here: *item weight against fuselage station* is a
stem/bar shape `PlotData` has no member for; the *wing + fuselage total-loads
snapshot* is a composite of two distributions that now render on their own
pages; and *imported against computed* needs an external-CSV import channel the
survivor has no page for and which #245 is still deciding. The *fleet
comparison* is #268. Each is a figure the retiring GUI carries, so they are
named here rather than left to be discovered when `app/views/` is deleted.
**Ruled 2026-09-13, after #268** (owner, in session; note 60 §9 amended): *item
weight against fuselage station* **ports** at the residue row — #268 gave
`PlotData` the cloud of named points it had been missing, so the blocker was
gone the moment the fleet scatters landed; the *snapshot* **retires superseded**
by the two distributions now drawn on the pages that compute them; and *imported
against computed* is **deferred with the inbound CSV channel it needs**
(backlog band C), not retired, so #270 removes a page and not a capability nobody
decided about.

- **The fleet comparison ports to the surviving GUI (#268, design note 57
  D-57.5, tier M, 2026-09-13)** — the Phase-C *assess against similar airplanes*
  requirement lands in `oracle_app/` as a marked **✦** extension page, on the
  navigation only and never in the derived step set, at the url path `fleet`
  because `aircraft_comparison` is a workflow step key and a non-step reachable
  at a step's URL is what gate G2 exists to prevent. The port's real content is
  what it stopped owning. The bundled reference fleet moved from `app/data/`
  into `sloads/data/` and is read by `sloads.fleet.reference_fleet`; the
  subject's priority chain moved out of the page as
  `sloads.fleet.subject_from_project`; the six scatters became `PlotData`
  producers in `sloads/report/fleet_figures.py`; and the readout, tabs and fleet
  table became `app_shell/fleet_view.py`, which the retiring page now calls
  unchanged — two pages, one implementation, for the milestone in which both
  exist. D-57.5's *rewritten, not imported* was not followed; the amendment
  was **ratified by the owner in session, 2026-09-13**: note 60 D-60.1
  withdrew exactly that rule for figures
  on the ground that a second derivation is a second owner, the subject chain is
  the same class of thing, and it carries the 2026-08-15 fix that had stopped a
  regional jet being plotted 1,800 lb above any weight its loadings can reach —
  a rewrite would have been a rewrite of that fix. The move paid for itself
  immediately: gate DG-3 forbids anything in `sloads/` from integrating the wing
  planform itself, the page had been doing exactly that since M2-5 and was
  invisible to the guard while it lived in `app/`, and the subject now reads
  area, aspect ratio and span through `derived_geometry`'s resolvers — the
  single owner of what area the analysis actually uses (#70) — with the
  placement unchanged to the last ulp on every bundled example. Making the figures
  producer-owned needed three additions to the figure model, which could not
  express a scatter at all: `Series.marker`, `Series.labels` and
  `PlotData.log_x`/`log_y`, honoured by the Plotly renderer and — bar the
  per-point labels, which are a hover and not a printed node — by `plots_tex`,
  so the set can be printed the day a document asks for it. The figures are
  deliberately **not** in `sloads/report/figures.py`'s step catalogue and not in
  the oracle report: every family in that catalogue is drawn on the page whose
  programs produce it and is held against the built document by gate 10, and the
  fleet comparison runs no program. Guarded by `tests/test_fleet_figures.py` —
  the six figures build for every bundled example, the CSV has exactly one
  reader in the whole tree, neither front-end defines a derivation of its own,
  and both renderers honour the marker and the log axes.

- **The weight-estimate seed is built fresh, and built merging (#269, design
  note 57 D-57.7, tier M, 2026-09-13)** — the surviving GUI had no way to copy
  WTESTIMA's component weights into the itemized data base WTONECG and WTENV
  actually read, and the retiring GUI had one that replaced every entered item
  and captioned the replacement underneath the button that had already done it
  (#78, C210-9). D-57.7 refused to port the defect into its new home and fix it
  later, so both halves land in the first version. Of *merge, refuse or
  replace*, the answer is **merge**, chosen because it is the only one of the
  three that is idempotent: the seed matches on item name, adds only what the
  data base does not already name, never overwrites and never deletes, so
  pressing it a second time after positioning half the rows picks up the other
  half and disturbs nothing. The plan is built before the click and states
  itself above the button — how many rows it adds, how many it leaves alone,
  and that nothing is replaced. The second half is the one the numbers care
  about: WTESTIMA gives weights and nothing else, so a seeded row arrives at
  station 0 untagged, where `infer_component` carries it on the fuselage beam
  at zero moment arm and it moves the CG and the body shear while looking like
  data the user entered. Both GUIs now show `mass_distribution.unplaced_warning`
  as a warning that persists until each row has an `x` station and a
  `component` tag, and the predicate is written generally — a row counted into
  existence and left blank is the same row. Every part of that is owned in
  `sloads/` (`weight_estimate.SEED_CONTRACT`/`SeedPlan`/`seed_plan`/`seeded_items`
  and `mass_distribution.unplaced_items`/`unplaced_warning`), reached from the
  oracle form through the new `field_registry.TABLE_SEEDS` — `RECORD_SEEDS`'
  analogue for a `…[]` table — which is what let the retiring `app/` page be
  pointed at the same owner instead of being left holding a live destructive
  button for the rest of the milestone. Nothing moved out of `app/`, so this is
  not the port D-57.7 rejected; it does mean #270 deletes a page that owns none
  of it, and it closes **#78** superseded. Guarded by
  `tests/test_weight_seed.py`: an entered row survives a seed unchanged in
  weight, station and tag; a second seed offers nothing; a name already present
  is matched regardless of case or spacing; a project with no mission inputs is
  told why rather than crashing; a seeded row is named as unplaced until it is
  both positioned and tagged, while a zero-weight blank is not; and
  `estimate_to_mass_items` has exactly one caller in the whole tree.

- **The issue package's `data/` becomes the oracle GUI's only tabular channel (#245, tier M, 2026-09-13)** — OR-23's `data/` externalisation, planned at design note 44, deferred by OR-42 and delivered here under the consolidation ruling of note 57 §1.3 and note 60 D-60.12. The defect was a shape rather than a number: three channels carried the same tables — a CSV and a text twin on every results block, the sidebar's whole-project results zip, and the applied load sets, which shipped only from `app/`'s export page and so were unobtainable from the front end that survives — while the package a report issue *is* held five control files and no data, and Appendix F named `landing_gear_applied_loads.csv` in printed prose that pointed at nothing. `sloads/report/package_data.py` now decides what `data/` carries and `oracle_package` places it: the six applied sets, the balanced V-n conditions, the case index, the governing safety-factor table, the gear report, one load-case file per module that produced a result, one file per appendix table no named file carries, and one file per figure the document draws. All of it comes from the owners the document renders from and from the *same* built document — `OracleDocument` gained the reduced project and the module results, so there is no second run and no second formatter — and each file states its units, its axes, the factor it does not apply, its producing step and the build fingerprint, with the document's own front matter listing them. The per-module buttons and the zip retired with no replacement built (`results_zip.py` deleted, `Artifact`/`page_artifacts` gone, the sidebar's `channel` parameter with them), and the column inventory the retirement was conditioned on became a test that compares each module file byte-for-byte against `io.load_cases_csv` rather than a check done once. Its two named cases came back clean — the V-n matrix and the envelope's 300-point table are different quantities and both ship; LANDLOAD's primed ground-line set is in `gear_loads.csv` — and its real find was the one-engine-inoperative yaw march, drawn as figures with no tabular channel anywhere and about to be deleted with `app/views/one_engine_out.py`: the fix is a generic emitter over `content.PlotData`, so every figure ships its numbers. G-OR-15 and G-OR-17, vacuous since they were written, got their real bodies; G-OR-73 widened from four hand-rebuilt CSVs to everything the package ships; gate G7 was re-cut from "one download call site" to "no download but the project file".

- **The record stops outnumbering the authority: notes split out, the record filed apart, one telling per closure (note 61, tier M, 2026-09-14)** — the documentation machinery was measured rather than described, and the cost turned out not to be volume but search. `10_standard` + `20_theory` held 12,489 lines against 27,928 lines of pure record with no reader, and every term a maintainer actually looks up returned two to three times more hits from the record than from the authority (`LRA` 34 against 14, `envelope` 42 against 19) — every one of them a dated snapshot, and the ratio worsening each cycle because the record grows with time while the live corpus grows with the code. The blocker was that `40_history/` was two corpora fused under one name: 52 of its 61 files were design notes that 18 files under `tests/` cite as the standing authority for physics, so the record could not be moved out of the way without exiling the physics with it. CV-3 split it by function — 54 notes to `docs/25_notes/` whatever their status, since a note that has shipped is still the authority for what it decided, which is why filing them by shipped-ness was wrong — and CV-4 then moved the remaining 18 record files and `CHANGELOG.md` to `docs/90_record/`, out of the default search path, with `CLAUDE.md` saying so. 72 files moved, no body edited, 114 files' references rewritten. CV-2 ended the tier-M duplicate telling: note 26's DV-4 had removed it at tier S on the premise that the two files answer different questions, which this cycle's 12 items falsified at 780 words each — the history fragment was a re-flowed compression of the changelog fragment, same findings, same causes. A tier-M/L closure now writes one fragment and `build_changelog.py` derives the changelog bullet from the lead phrase the entry already opens with, so nothing is capped and nothing is lost; a hand-written bullet still wins where the consumer-facing wording genuinely differs (this entry is the first use of the mechanism). CV-1 added the question that stops the leak recurring — *does a reader of the code today need this, or only a reader asking what happened?* — because durable understanding landing in the narrative is how the narrative became load-bearing in the first place. CV-5 gave `CHANGELOG.md` the archive rule note 26 DV-1 gave the history and not it: 11,249 lines against the history's rolled 1,388, now sharing the same 1,500-line trigger and `--roll`. CV-6 shipped the guard the move needed, `tests/test_doc_links.py`, and it paid immediately: twelve live links were already dead before the move — notes renumbered without their inbound links, a theory chapter renamed, the FAR 25 gap analysis cited under `20_theory/` — all fixed here. `docs/90_record/` is exempt from it, because a frozen archive links to the tree it was written against and DV-1 forbids editing it to keep a test green. Two links are left standing and named in `_KNOWN_DEAD`: note 40 cites two `app/views/` files, and `app/` was deleted wholesale at #270 — 37 live documents still reference it, seven of them in `10_standard/` and `CLAUDE.md`, which is the GUI retirement's currency debt and wants its own item; `CONTRIBUTING.md`'s lint command was the one instance that had actually gone wrong (it still named `app/` and omitted `oracle.py`/`oracle_app/`, so the command as printed exits 1) and is fixed here under practice 4. Retired with DV-5: the status-driven note move at release cut. Deferred: the length half of #187's INDEX-row rule still covers `30_future/` only — the status half was widened to the 54 note rows (20 cleaned), but 44 rows exceed the cap and trimming each is a content edit, not a consequence of re-filing.

## Release cut: **sloads 0.8.3** (the empennage geometry model, and the export package closing on one solver artifact), tag `v0.8.3`, 2026-09-13

**Objective.** Close band **B4**. The milestone opened on its named deliverable
— the **T-tail empennage geometry model** (#25) — and closed on the one that
grew out of it: `sloads/export/` shipped **four parallel model concepts** in one
ID space, three of which were not the deliverable, and the deliverable borrowed
GIDs from artifacts nobody consumed. Design note **56** reduced the package to
**one solver artifact plus the mass model**. The two are the same problem seen
twice — where a joint node *sits* (note 54) and how the model that carries it is
*built* (note 56) — which is why they landed in one milestone.

**Deliverables** (the `[0.8.3]` changelog section is the release note):
- **The empennage geometry model (#25, design note 54, tier L, schema v65).**
  The tail group's geometry is **entered once as boundary lines** and the
  scalars derive: the seam between fixed surface and control surface is marked
  in the input blocks (step 1), and the planform scalars each surface used to
  carry independently become reads of the entered polylines (step 2). Around it
  the cluster: the joint register — a joint is an **owned location, a stated arm
  and a DOF set** (#262, D-54.5/D-54.7, `sloads/joints.py`, importing three
  owners so it can live inside none of them); the conventional h-tail off the
  wing-root waterline (#261, D-54.4); a raked fin root that no longer kinks the
  loads reference axis (#219, D-54.3); one owner for the plane a surface is
  defined in (#220, D-54.2); one name per surface, `fin_*` retired for `vtail_*`
  (#223). **D-54.6 alone remains**, riding the baseline wave in 0.8.5, so note
  54 stays live.
- **The export package closes on one solver artifact (#263, design note 56,
  tier L, ten slices).** The five **per-component decks are deleted** (D-56.2);
  the assembled balanced deck is **unshipped**, demoted to an internal producer
  the LRA transfer and the report's tables consume (D-56.8); `sbeam_bridge.py`
  **ceases to exist** — the applied-load model and the report's deliverable
  tables were never a bridge to sbeam and move to `report/applied.py` and
  `report/tables.py` under their right names (D-56.1), with no shim and two
  guards refusing one. What ships is the **LRA beam model** and the CONM2 mass
  model: the LRA owns every grid it writes (D-56.3), takes a **joint-driven mesh
  decided from geometry** rather than one welded to the load stations (D-56.4),
  and carries the applied set summed onto its own grids with the exact
  lever-arm couple (D-56.9); every `CONM2` sits on its own `GRID` at its own
  item's CG (D-56.6). `EXPORT_TARGETS` 10 → **3**, `sloads/export/` 8,603 lines
  across 15 modules → **5,316 across 14**.
- **What the beam grids cost the distribution is published, not discovered
  (D-56.10).** New **Appendix G** and the new owner `report/lumping.py`: the
  widest gap in each internal-load channel of each member over every case, plus
  four figures along the span. The **resultant** is preserved exactly and gated
  by LM-1; the **distribution** it moves is a real discretization difference, so
  it is stated. No solver is in the loop and there is no acceptance tolerance —
  the size of the difference is a function of the grid counts the project sets.
- **Every exported LRA deck solves (#172, design note 55, tier L).** Three
  defects in *how a joint node joins the structure*: a body tie parenting on a
  node already an `RBE2` dependent (a rigid chain sbeam refuses outright), a
  joint inserted beside an existing station leaving a **sliver element**
  (`cessna_210` at 1.07 % of `ds`, 1638:1), and a support picker that excluded
  rigid dependents but not independents — **569.49 lb** of recovered reaction
  against an applied set closing to 0.0002 lb. All three are gated invariants,
  a skeleton that violates one is an `LraRefusal` naming it, and the solve gate
  widens from the two fixtures that passed to **every CLI-exportable fixture**.
  This is the milestone's mission claim made true rather than asserted.
- **The load-output contract consolidated (#193, note 58, tier M; #170; #175).**
  Governing-case comparisons key on **|value| × SF** so a 2,000 lb case at 1.5
  is not out-ranked by a 2,500 lb case at 1.0, and a mixed-factor envelope
  refuses by name; no delivered load value moves on any fixture. The contract's
  statements get **one owner** and eight copies collapse onto it; a machine
  rating in load units stops being a load (#170).
- **The plan re-cuts into three milestones (tier S, 2026-09-11).** 0.8.3 closes
  the export contract, **0.8.4** converges the two front-ends on one (note 57,
  AGREED), **0.8.5** takes the defect-and-polish tail on the converged surface —
  because note 57 sat AGREED, filed and sequenced, gated on a 21-row tail with
  no relation to this milestone's charter. Bands B5 and B6 carry them.
- **Hygiene as its own items:** the deck-writing primitives get their own module
  (#15, CH-4); six dead public names leave `sloads/` with a gate keeping the
  seventh from arriving (#16, CH-5); the round-trip stick-model wrapper retires
  with the last elementless deck, 529 → **186** lines; `cessna_210` and
  `dhc8_dash8` retire from the bundled examples (#264) while `baron_58` joins
  the Imperial output baseline and the example list becomes structural (#271);
  the theory documentation becomes a chaptered manual; the certification-basis
  matrix leaves the ranked backlog under rule 6 (#47, closed not-planned); the
  backlog is re-scoped onto the package note 56 left behind, and its open-defects
  index loses two wrong issue numbers, a deleted body and three closed entries.
- **The band re-opened once, and drained before the cut (#274).** The
  issue-bookkeeping pass that followed #263 found **seven** rendered statements
  — the oracle report's §7 and gear sections, four GUI captions and a help
  string — plus the `$` header inside the one deck that ships, all describing
  the export package the note had just deleted. A defect with first-order effect
  on shipped content outranks every [V] item, and 0.8.3 could not knowingly cut
  a report naming artifacts it does not build. Filed, fixed and closed the same
  day; the deliberate carve-out is the case index's `LOAD/SUBCASE (component)` /
  `(assembled)` headers, which move a shipped CSV header across three owners and
  are **#209**'s decision, stated at `LOAD_ID_COLUMN` rather than left to be
  inferred.
- **Found at the cut and fixed pre-cut (the §3.5 walk):** three more shipped
  statements of #274's class that its sweep had not reached — the Wing Loads
  caption offering "all three files" and describing the span-load file beside
  them, the Fuselage Loads caption offering "both files" and naming the body
  span CSV, and the SI methods stamp's "the sbeam solver decks **and their span
  CSVs**" — all naming companion files D-56.2 deleted. With them the last
  `*_ULT.csv` filename in the tree, `wing_applied_loads_ULT.csv`, which note 49
  **OR-81** had held for exactly this milestone: the file is LIMIT like every
  other, and a name asserting otherwise is the one statement a reader cannot
  check against the content.
- **Version** `0.8.2` → **`0.8.3`**. Schema **v61 → v66** across the cycle
  (the boundary-line model's v65 among them); `io.py` still loads older saves.
- **Changelog cut** — `scripts/build_changelog.py 0.8.3 --date 2026-09-13`:
  **34 fragments** consumed into `## [0.8.3]`, **20 history entries** rolled to
  the top of this file, a fresh empty `[Unreleased]` opened.
- **History roll** (`RELEASE_PROCESS.md` §4.3): notes **55** and **56** move to
  `40_history/` keeping their numbers; note **54** stays live on D-54.6 alone
  and note **58** on D-58.1 (decided, not done) — the mechanical rule rolls a
  note whole when its status reads shipped, never by halves; notes 21/49/51/52/57
  stay with their open milestones. The live file passed the **1,500-line
  threshold**, so everything below the 0.8.2 cut block froze verbatim into
  [`59_completed_development_to_0.8.2.md`](59_completed_development_to_0.8.2.md).
- **Gates at cut:** `pytest` **3,422 passed / 17 skipped / 2 xfailed / 0 failed**, `ruff` clean, `mypy` clean
  (`sloads/`, 98 source files), `scripts/smoke_test.sh` **PASS** (both front-ends boot, CLI CSV checked),
  `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on 7 tracked keys,
  the §3.5 by-hand walk done by the owner, no open CRITICAL/MAJOR review
  findings. The four statements above came out of a read of the pages that
  precedes that walk, not out of it.

**Key decisions.** *A deliverable is what a consumer holds, and everything else
is scaffolding that has to justify itself.* The package had grown four model
concepts because each was easier to add than to reconcile, and the cost was not
maintenance time but **truth**: the shipped model borrowed GIDs from decks that
were not deliverables, and the report described a package the bundle did not
carry. Two rulings made the reduction cheap enough to take. Nothing downstream
reproduces an sbeam output, so decks, digests and GIDs were free to move and the
renumber happened once. And sizing belongs to the stress analyst, outside
sloads: core sloads produces an LRA beam model with arbitrary beam properties
plus the load cards on its grids, to prove the cases solve — that is the whole
job, and it is what let ~4,000 lines go without withdrawing a claim.

*The mesh was the tell.* A beam welded to the load stations is a **degenerate
special case that hides the general one**: when beam nodes *are* load stations
the spanwise half of the transfer is identity, so every CI fixture exercised the
degenerate path while arbitrary-grid routing — what a real user meets first —
was least covered. Cutting the mesh loose made the generated model *one instance
of the contract the imported model obeys*, and note 55's sliver class died
structurally rather than by tolerance.

*Publish the cost of your own discretization.* D-56.9 sums the applied set onto
grids the mesh chose from geometry, so a moment that is zero at a station is
generally not zero at a grid. The resultant is gated; the distribution moves.
Appendix G exists because the honest response to "this changed something we
cannot bound" is to measure and print it, not to pick a tolerance that would
fail a coarse mesh behaving exactly as specified.

**Band B4 retired with the cut; band B5 (0.8.4 — the two front-ends converge on
one, design note 57) is the milestone in flight.**
