  # Changelog

All notable changes to **sloads** (the FAR 23 LOADS replication and
initial-concept distributed-loads tool) are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Live cycle only.** This file holds `[Unreleased]` plus the two newest release
blocks; older ones roll into frozen, do-not-edit archives at a cut (note 61
CV-5): 0.8.2 and everything before it is in
[`CHANGELOG_to_0.8.2.md`](CHANGELOG_to_0.8.2.md).

---

## [Unreleased]

## [0.8.4] — 2026-09-14

### Added

- **The last of note 60 §1.1's twenty figures is settled (note 60 §9 amended
  2026-09-13, tier M, 2026-09-13).** Three figures had no report producer at
  #267 and were reported at its close rather than left for `app/views/`'s
  deletion to discover. Each now has a ruling: one ports, one retires
  superseded, one is deferred with the capability it actually needs.

- **Item weight against fuselage station ports (note 60 §1.1 figure 6).** Every
  row of the weight data base drawn at its entered station, split by loading
  kind — empty weight, minimum flight weight, discretionary — each kind with its
  own marker shape, because *when* an item is aboard is the first thing a mass
  at an extreme station has to be read against. It is a **pre-run** family on
  the Weight & Mass page and the oracle report's section 2.2 prints it, so it
  meets the parity gate like every other figure. It was blocked at #267 only
  because the model had no way to say "a cloud of named points"; #268 added
  exactly that for the fleet scatters, so the blocker was gone as soon as they
  landed.

- **A marker series may state its shape (`mark=…` in `Series.style`).** Honoured
  by both renderers — `plots_tex` emits the pgfplots mark, `app_shell/plots.py`
  maps it to a Plotly symbol. Shape rather than colour, because
  `SUMMARY_REPORT.md` §4.3 requires a printed figure to read in greyscale and
  three clouds of identical dots are one cloud. No new member: the style channel
  the producers already write was the right place.

- **The wing + fuselage total-loads snapshot retires superseded (figure 18).**
  Its two halves are the wing and fuselage net-load distributions, which #267
  put on the pages that compute them; a third axis carrying both adds a view,
  not a fact.

- **Imported against computed is deferred, not retired (figure 19).** It needs
  an **inbound** CSV channel the survivor does not have — which columns, which
  stations, which units, and what a disagreement between the two is *said* to
  be: a design note's worth of questions, not figure plumbing. Filed as backlog
  band C — *additional analysis capability, design notes first* — with the
  figure named as its first consumer. #245 settles `data/` as
  the single *outbound* tabular channel and does not cover this direction.

- **The oracle GUI gains every figure the oracle report carries, under one owner
  (#267, design note 60 D-60.1…D-60.6, tier L, 2026-09-13).** The surviving
  front-end carried no chart of any kind while the retiring one carried twenty,
  nine of them on pages the survivor already rendered. `sloads/report/figures.py`
  is the new **figure catalogue** — one row per figure *family*, naming the page
  that shows it, the producer that builds it, and whether it is **pre-run**
  (entered data drawn, rendered under the form so a shape can be checked before
  the analysis is run) or **post-run** (a result, rendered under the results,
  every load on it LIMIT). `app_shell/plots.py` renders a `PlotData` as Plotly
  and is a **peer** of `plots_tex`'s TikZ over the same producer set: the GUI
  derives no figure data of its own, and a guard walks the GUI trees for a
  `PlotData` or `Series` constructor to keep it that way.

- **Nineteen figure producers become callable per figure (#267, note 60 D-60.3).**
  They were reachable only through a built report bundle, which defeats the use
  the port was asked for — checking the inputs *before* running the whole
  process. Each is now a public function of `oracle_sections.py` taking a
  `Project` and, where the figure genuinely needs them, the module results; the
  report's own section builders call the same functions, so there is one
  construction of each figure and not two.

- **The report gains the balancing tail load and the static margin against CG
  (#267, note 60 §7).** The two figures note 57 §8 deferred, built from the
  existing `trim_sweep` and the Configuration module's tail-volume neutral
  point — swept at the heaviest loading over the entered CG range, with the
  project's own cases marked on the curve. The interactive sweep (a reader
  choosing the loading, the range and the station count) stays deferred.

- **`Figure.family` (#267, note 60 D-60.2).** A key names one drawing, a family
  names the kind, and the two differ wherever a producer emits a run — `vn_0 …
  vn_14` is one family, because how many V-n diagrams a project has is a fact
  about its loadings. Carried as data stated by the producer, not pattern-matched
  out of a key by the guard.

- **The fleet comparison ports to the surviving GUI, and stops owning anything
  (#268, design note 57 D-57.5, tier M, 2026-09-13).** The Phase-C *assess
  against similar airplanes* requirement is now a page of the oracle GUI —
  `oracle_app/fleet.py`, marked **✦** as an sloads extension because the
  original suite has no such program, registered on the navigation only and
  never in the derived step set (gate G2). The airplane is placed against the bundled
  reference fleet by wing loading, power loading, weight and geometry, with the
  nearest comparators named, the p10–p90 band flagged, and six scatter tabs.
  The reference figures are nominal published specifications in Imperial units
  and never enter a computation.

- **The reference fleet moves into the package it belongs to (#268).**
  `app/data/reference_aircraft.csv` → `sloads/data/reference_aircraft.csv`, read
  by `sloads.fleet.reference_fleet` and shipped as package data. It had been
  sitting inside a Streamlit app nothing imports, so a `pip install sloads`
  carried no fleet to compare against; the front-end that carried it retires at
  #270.

- **`sloads.fleet` gains the subject's priority chain (#268).**
  `subject_from_project` — MTOW from `cg_cases.max_takeoff_weight` then
  WTESTIMA, empty weight from the item database then WTESTIMA, area / aspect
  ratio / span from the parametric layout then the WINGGEOM wing surface — moves
  out of the retiring page unchanged. D-57.5 asked for it to be *rewritten, not
  imported*; note 60 D-60.1 had already withdrawn that rule for figures on the
  ground that a second derivation is a second owner, and this chain carries the
  2026-08-15 fix that stopped a regional jet being plotted 1,800 lb heavy.

- **Moving the chain into `sloads/` put it under a guard that caught it
  (#268).** Gate DG-3 (`tests/test_derived_geometry.py`) forbids a module in
  `sloads/` from integrating the wing planform itself — the defect #70 found
  after four numbers for one wing turned up in the tree. The comparison page had
  been a fifth, invisible to the guard because it lived in `app/`. The subject
  now reads area, aspect ratio and span through `derived_geometry`'s resolvers,
  which is *what the analysis actually uses*; the placement is unchanged to the
  last ulp on every bundled example.

- **A scatter is now something the figure model can say (#268).**
  `Series.marker` (points, not a polyline), `Series.labels` (which airplane each
  point is, shown on hover) and `PlotData.log_x` / `log_y` (a fleet spanning a
  factor of thirty in weight). The six figures are built by
  `sloads/report/fleet_figures.py` and drawn by `app_shell/plots.py`, with
  `plots_tex` honouring the marker and the log axes too — so the port adds no
  second figure owner, and both front-ends render one implementation
  (`app_shell/fleet_view.py`) until `app/views/` retires.

- **The weight data base gains a seed button that adds rather than replaces
  (#269, design note 57 D-57.7, tier M, 2026-09-13).** WTESTIMA's component
  weights can now be copied into the itemized data base from the surviving GUI,
  which had no such action at all. Of D-57.7's three permitted answers — merge,
  refuse, or state the replacement before the click — the answer is **merge**:
  the seed matches on item name, adds only the components the data base does not
  already name, and never overwrites or deletes an entered row. Seeding twice is
  a no-op, so it is safe to press beside half-finished work. What the click will
  do is built as a plan and shown *above* the button
  (`weight_estimate.seed_plan` / `SEED_CONTRACT`), naming how many rows it adds
  and how many it leaves alone.

- **A seeded row says what it still owes, until it stops owing it (#269).**
  WTESTIMA supplies component weights and nothing else, so a seeded item arrives
  at station 0, untagged, with zero inertias — and `infer_component` then carries
  it on the fuselage beam at zero moment arm, moving the CG and the body shear
  while looking like entered data. `mass_distribution.unplaced_items` /
  `unplaced_warning` name exactly those rows, and both GUIs show the warning for
  as long as it is true rather than once in a success message. The predicate is
  general: a row counted into existence and left blank is the same row.

- **The main GUI's seed button stops being destructive (#269, closing #78).** It
  had replaced `Project.weight.items` wholesale — a data base positioned and
  tagged over an afternoon was one click from gone — and its caption said so
  after the fact. It now asks the same owner the new page asks, so the two
  cannot answer differently and the page that retires at #270 owns none of it.

- **`field_registry.TABLE_SEEDS` (#269)** — `RECORD_SEEDS`' analogue for a
  `…[]` list: a table whose rows a program the project has already run can
  propose, offered by the one registry-driven renderer and stated by the plan
  itself.

### Changed

- **The Project JSON Editor moves to `app_shell/` and the oracle GUI carries it
  (#265, note 57 D-57.3, tier S, 2026-09-13).** The editor's page body is now
  `app_shell/project_editor.py`, owned once and rendered by both front-ends;
  `app/views/project_editor.py` is the two-line `app/` page that calls it, and
  `oracle_app/Oracle.py` registers the editor on `st.navigation` only — never in
  `register_pages`, which stays exactly `workflow.oracle_steps()` (gate G2), on
  the OR-16 pattern the Report page established. Title and URL path are read from
  `workflow.py` rather than typed again. First row of band B5: the editor is the
  escape hatch that makes every sloads-only field enterable in the surviving GUI
  before D-57.2 builds a widget for any of them, so no later port waits on the
  field tiers. Behaviour is unchanged — the same display-unit round trip, the
  same Apply-side safety-factor warning, the same session replacement — and the
  `st.session_state` scan in `tests/test_persistence.py` follows the page into
  the shell so its coverage did not lapse with the move.

- **Design note 60 amends the convergence plan: twenty figures, one owner, and one report (note 60 AGREED 2026-09-13, band B5 re-cut, tier S).**
  The critical review of band B5, taken immediately after the 0.8.3 cut, found
  two measurements design note 57 did not make. **The front-end carries twenty
  figures, not the four D-57.4 names** — thirteen of the 22 `app/views/` pages
  chart at twenty call sites, and **nine of those pages are shared analysis
  steps** the survivor renders today with no figure, which a page-level audit
  cannot see going. And **`app/views/export_report.py` is the only production
  consumer of `content.build_report`**, so D-57.6 retires the 2,632-line
  summary report without naming it — taking the only statement of the axis
  system and sign conventions either front-end makes (`conventions_tex.py`,
  276 lines, sole consumer, three static TikZ diagrams) and the only FAR 23
  Subpart C coverage matrix (`coverage.py`, 241 lines, sole consumer).

  **Block A (D-60.1…D-60.6)** withdraws D-57.4's *written fresh* ruling:
  `content.PlotData` — already frozen, renderer-agnostic and already shared by
  both documents — stays the single owner of what a figure is, `plots_tex`
  emits LaTeX and a new `app_shell/plots.py` emits Plotly, and a both-ways
  parity guard holds them together, so *"every report figure appears in the
  GUI"* is structural rather than diligent (practice 3). Producers become
  callable per figure from a `Project` (pre-run) or from the module results
  (post-run), classified as one; #267 is re-tiered **M → L** and gains the
  figure gate it shipped without (practice 2).

  **Block B (D-60.7…D-60.12)** merges four cross-cutting sections into the
  oracle report — axes and sign conventions, the FAR coverage matrix, the
  governing safety-factor table and the bundle manifest — as a front-matter
  group after the Introduction via `oracle_content.FRONT_SECTIONS`, so the
  section plan stays **derived** and G-OR-2 survives re-cut on the OR-16
  pattern. Every other `content.SECTIONS` key is declared superseded with its
  successor or its reason in an audit table a guard reads, and `build_report`
  is deleted at #270 only after the merge has landed. #245 is confirmed and
  widened: the per-module CSV and text buttons retire with the results zip and
  `data/` is the single tabular channel.

  Band **B5 gains two rows** — **#239** pulled forward from B6, because note
  57's gates 4 and 5 are enforced by `tests/test_basis_statements.py` whose
  `_GUI_TREES` excludes `oracle_app` and including it *is* that row, and the
  **report-merge** row filed new — and re-tiers **#267**. Note 57's gates 4 and
  5 move from #270 to #266 and gate 7 is asserted after #266, since that row
  adds 79 fields to the survivor's renderer and could re-import the no-op-Apply
  class. Note 57's D-57.8 rule is unchanged and is what the additions serve:
  the surviving GUI is complete before anything is removed. The priority table
  is renumbered densely with the re-cut (**Pri 1–57**).

- **The summary report's cross-cutting sections merge into the oracle report, and
  the retiring document's every section is accounted for in writing (#278, note 60
  D-60.7…D-60.11, tier M, 2026-09-13).** `app/views/export_report.py` is the only
  production consumer of `content.build_report`, so note 57 D-57.1's deletion of
  `app/views/` retires the summary report — and with it the **only** statement of
  the axis system and sign conventions either front end makes, and the **only**
  FAR 23 Subpart C coverage matrix. Four assets moved into the surviving document
  first, as numbered front matter after the introduction: axes and sign
  conventions, the governing safety-factor table, the FAR coverage matrix and the
  bundle manifest.
- **The front-matter slot is data, so the section plan stays derived.**
  `oracle_content.FRONT_SECTIONS` is now a table of `(key, title)` rather than one
  literal, and the analysis body renumbers itself around it because numbering is a
  function of position (G-OR-2 survives the re-cut on the OR-16 pattern, note 60
  D-60.9). Cross-references to front matter go through `front_ref`, like every
  other reference in the document. Appendices were the rejected alternative: an
  appendix is appended, never inserted, and a section stating the frame every later
  number is in belongs before what it governs.
- **One builder, two documents.** `sloads/report/front_sections.py` owns the four
  sections and takes its heading as an argument; `content.py` calls it rather than
  keeping a second copy, so the two reports print the same table rows until the
  first is deleted (practice 3 — a merge implemented as a copy is the drift the
  convergence exists to end). `conventions_tex.py` and `coverage.py` keep a
  consumer that outlives the page, asserted rather than assumed.
- **The document states what travels with it.** `OracleDocument` now carries its
  own `data/` file list, so the bundle-manifest section is an ordinary built
  section listing the control files and the data files together — a list computed
  only at packaging time would leave a section INCLUDED in the plan and absent in
  the render. #245's *Data reference* table is that section now, widened to the
  whole package; `MANIFEST.txt` still states the same set with hashes, from the
  same two owners.
- **Nothing leaves unaccounted.** Every key of `content.SECTIONS` is declared in
  `front_sections.SUMMARY_DISPOSITION` with the front section it merged into, its
  successor, or the reason it retires — a table `tests/test_front_sections.py`
  reads, so a section cannot be dropped silently (note 60 gates 11 and 12). The
  audit is what turned up the cases that needed a decision rather than a
  presumption: the approved-corrections table, which describes the tool and
  reaches a reader through the methods statement in every shipped file's header;
  and the balanced free-free cases, whose honesty statement is written in band on
  the deck that carries each case.
- **`build_report` is untouched and still builds.** It is deleted with the page at
  #270, after the merge and never before it (D-60.11) — the document's content
  reaches its new home before its old home is removed.

- **The oracle GUI renders every input field, in two marked tiers (#266, design note 57 D-57.2, tier M, 2026-09-13).**
  Until now a page of that front-end showed only `field_registry.oracle_input_paths()`, and the **83** sloads-only
  fields it dropped — thrust, the Part-25 speeds and Mach-margin basis, fuselage moment and lateral body aero, the
  fuselage 3-D stations, control-surface span and actuator geometry, the LRA beam mesh, and the rest — were enterable
  in no form at all. The charter said *the original suite's inputs and nothing this replication added*; the code said it
  by filtering a page definition, so a concept field's only way in was hand-edited JSON. Every registry path now
  renders. A field the original programs never asked for carries **✦** on its label and *"sloads extension, not an
  input of the original suite"* before its basis in its help, and the page says once what the mark means — so what the
  suite asked for is still legible at a glance, and leaving the marked fields unfilled asks exactly what the original
  programs asked.
- **The tier is marked on the field, not on a section, and the basis states a reason rather than a citation.**
  `field_registry.tier_of` is the one classifier (`SUITE` / `EXTENSION` / `JSON_ONLY`) and the mark is applied in
  `form._field_label` and `form._help` alone, so every shape a field renders in — scalar, tuple, curve, enum set and
  the grid columns a `data_editor` hides inside a canvas — inherits it. A section per page cannot work: a record holds
  fields of both tiers, and a second section over that record re-emits its row counter, its seed and its remove control
  under the same Streamlit key. The 63 extension rows' `basis` strings were rewritten in place — they cited the
  decision that added the field and said nothing about why sloads asks for it, which is the question this GUI's reader
  has just been handed. The `DATA_DICTIONARY.md` and the illustrated guide read the same strings and improve with them.
- **What no widget can address is declared with a reason, not dropped (note 57 gate 3).**
  Twenty fields sit on three records whose path crosses a `[]` hop — an engine's rotor set, a CG case's loading and its
  ballast — so addressing one means naming *which row*, which `form.record_at` cannot: it returns `None`, and
  `rows_at` returns a list detached from the project that would take an edit and drop it. `field_registry.JSON_ONLY_RECORDS`
  names all three with that reason; they are entered on the Project JSON Editor page (D-57.3, which is why that row was
  sequenced first). The guard re-derives the classification from the renderer's own addressing and fails both ways, so
  a record declared JSON-only that a widget could in fact take fails as loudly as the omission it replaced.

- **The issue package's `data/` becomes the oracle GUI's only tabular channel
  (#245, tier M, 2026-09-13).** Three channels carried the same numbers, and the
  one an analyst actually needed carried nothing. Every results block offered a
  CSV and a McMaster print-format text twin (~20 blocks × 2); the sidebar built
  a whole-project results zip; the applied load sets shipped from `app/`'s
  export page and therefore not from the surviving front end at all — while the
  oracle report's Appendix F said in printed prose that its table is "the same
  set as the file `landing_gear_applied_loads.csv`", a file no production path
  wrote anywhere. OR-23 planned `data/` for this at design note 44 and OR-42
  deferred it; a package held five control files and no data. It now ships the
  six `*_applied_loads.csv`, `vn_conditions.csv`, `case_index.csv`,
  `safety_factors.csv`, `gear_loads.csv`, one `load_cases/<module>.csv` per
  module that produced a result, one file per appendix table no named file
  carries, and one file per figure the document draws. Owner:
  `sloads/report/package_data.py`; the rules are `ORACLE_REPORT.md` §1a.

- **One generation path, from one built document (#245).** `OracleDocument` now
  carries the reduced project and the module results its sections were built
  from, and the data emitter reads both off it. Not tidiness: the document is
  built from the *oracle projection* rather than from the project file, and an
  emitter handed the caller's own project would write files that disagree with
  the pages they are shipped beside — the failure `vn_conditions_csv` already
  had to guard against alone (G-OR-136). There is no second run of any module
  and no second formatter, so a file and the page that summarises it cannot
  describe different analyses.

- **The per-module downloads and the results zip retire, with nothing built to
  replace them (#245, note 60 D-60.12).** `sloads/report/results_zip.py` and its
  test are deleted; `app_shell/sidebar.py`'s two-step build-and-download block
  goes with them, and the `channel` parameter it was the only consumer of —
  every load sloads delivers has been LIMIT since note 49 OR-116, so the
  argument named a choice with one value. `oracle_app/results.py` loses
  `Artifact` and `page_artifacts` and renders a single caption per page saying
  where the files are instead. The text twins were porting-era verification
  artifacts and are not reproduced: the page-cited oracle tests carry that
  comparison.

- **The column inventory #245 required is a test, not a one-pass check (#245).**
  `tests/test_package_data.py::test_every_retired_per_module_csv_is_in_the_package_byte_for_byte`
  compares each `load_cases/<module>.csv` against `io.load_cases_csv` itself —
  the call the retired button made — on every bundled example, so "no column was
  lost" is asserted on every build rather than remembered from one session. The
  two checks the issue named by hand both came back clean and are recorded here:
  the **balanced V-n matrix** and the envelope module's own 300-point table are
  different quantities and both ship (`vn_conditions.csv` and
  `load_cases/flight_envelope.csv`); LANDLOAD's **primed ground-line set** is in
  `gear_loads.csv`'s `Ground-line V/D/S` columns, so retiring the text report it
  used to be read from loses nothing.

- **The one-engine-inoperative yaw march gets a file, and so does every other
  figure (#245).** The inventory's real find: section 11 draws the transient as
  two figures per case and has no printed table of it, the module's own CSV
  carries six summary rows, and the finer time history existed only behind a
  button on a page #270 deletes — so the march would have been lost between two
  changes that each looked complete. The emitter is generic over
  `content.PlotData` rather than special-cased for it: `figures/<key>.csv`,
  long form, one row per plotted point with the series it belongs to, for every
  figure the document draws. 44 to 54 files on the bundled examples, and the
  next curve whose numbers a reader wants needs no second discovery.

- **Every shipped file is self-describing, and the document lists them (#245).**
  G-OR-15 and G-OR-17 had bodies written at design note 44 and were vacuous for
  a fortnight because there was no data to assert them over. Each file now
  carries its own four-line header — what it is, which step produced it, where
  the document summarises it, and the build's analysis fingerprint — above the
  methods statement that supplies the units, the axes and the factor stated and
  not applied. The document's front matter gained a **Data reference** table
  built from the file list itself, so the `.tex` names every file the package
  carries and the package carries every file the `.tex` names.

- **G-OR-73 re-cut to the consolidated set (#245).** Its document half read four
  applied CSVs this repository's test file rebuilt by hand; it now also scans
  every file `package_data.data_files` decides to ship — the gear and engine
  applied sets, the V-n conditions, the gear report and every module's load
  cases, none of which had a basis gate at all. A file added to the package is
  gated the day it is added rather than the day somebody remembers the list.

- **The record stops outnumbering the authority: notes split out, the record filed apart, one telling per closure (note 61, tier M, 2026-09-14)**

### Fixed

- **Every applied-load CSV row now states which case it is (#241, tier M,
  2026-09-13).** The files led with a `Case` column holding the case's
  *description*, which is prose and is not an identity: LANDLOAD's 33 ground
  conditions collapsed onto the eight descriptions they share, so a reader
  loading `landing_gear_applied_loads.csv` could not tell the aft-max-landing
  3-wheel case from the forward-light one, and a twin's two engine mounts shared
  all three of theirs. The minted `case_id` was populated on every row and
  emitted on none. All six files now lead with `Case ID`, `Case` and `Loading` —
  the id the load-case index is keyed by, the description, and the named CG the
  case was computed at — so a delivered row joins to the condition, CG, speed,
  altitude and FAR paragraph the index states for it. Both strings are copied
  off the case's own `CaseRef` by one owner (`report/applied.case_identity`),
  and the file's header block says what each column is.

- **A twin's two engine mounts are told apart, in the index as well as the file
  (#241).** The Baron fits two `CONTINENTAL IO-550-C`, and the per-engine tag on
  each condition title was the designation alone, so `EM-01` and `EM-04` carried
  identical descriptions and the load-case index described them identically.
  `modules/engine.engine_tags` now qualifies a shared designation with the
  engine's side, read off its own butt line, and the tag is applied **before**
  the `CaseRef` is minted. An installation whose engines already differ is
  untouched, so no shipped single-engine title moves.

- **`case_ids.index_case_id` (#241)** — the one owner of which suffixes a
  delivered case id may carry over the id the case index lists: a handed twin
  (`W-05R`), and the 23.371(b) gyro condition's four sign combinations
  (`EM-06a…d`), which one `ConditionResult` cannot carry four `CaseRef`s for.
  `report/render`'s sub-case minter now reads the same suffix alphabet it strips.

- **The Imperial baseline pins the gear and engine applied sets (#241).** Four of
  the six applied channels were digested and two were not, so the bytes of the
  file with the most cases in it moved unguarded.

- **The 0.8.4 closure review: the JSON editor works again after a load, and every
  delivered file states the moment senses the right way round (tier S,
  2026-09-14).** The review of the converged front-end before the cut found four
  defects the green gate could not see, three of them in shipped content or the
  page the convergence depends on.

- **The Project JSON Editor was empty after the first project load.**
  `app_shell/project_editor.py` stamped its text key at import — `widget_key`
  evaluated once per process, at generation 0 — and re-stamped it per render,
  so after `adopt()` bumped the generation the seed was written to
  `g0::_project_editor_text` while the widget read `g1::g0::…`; Apply reported
  *Invalid JSON: Expecting value: line 1 column 1* and Reload wrote the same
  dead key. The escape hatch note 57 D-57.3 sequenced first was unusable on any
  loaded project, and no test rendered it. The key is now stamped at the use
  site; `widget_key` replaces a stale stamp instead of nesting one (rule 4 — the
  class, not the instance); `tests/test_widget_freshness.py` refuses a
  module-level `widget_key(...)` in any GUI source; and the new
  `tests/test_project_editor.py` renders the page at generations 0, 1 and 3 and
  round-trips an edit through Apply.

- **The AXES stanza on every delivered file had +Mx and +Mz backwards.**
  `export/coordinates.AXES_NOTES` said *positive Mx rolls right wing down …
  positive Mz yaws nose right*; for the frame the same stanza declares (x aft,
  y starboard, z up) the right-hand rule gives starboard wing **up** and nose to
  **port** — which is what `CONVENTIONS.md` §7, the report's own *Axes and sign
  conventions* section and `bending_moment_vector` all say, so the built
  `report.tex` contradicted itself between its methods stamp and its front
  matter, and the wrong sentence landed in band on all six applied CSVs, the
  case index, the gear and safety-factor tables, every module CSV, `METHODS.txt`
  and both decks. The senses now live once as `coordinates.MOMENT_SENSES`, the
  stamp and `conventions_tex` both read the sentence built from them, and
  `tests/test_delivered_frame_statement.py` derives each sense from the axes by
  the cross product rather than asserting the words are present.

- **The six applied CSV headers pointed at a file nothing writes.** The `Case ID`
  header sent the reader to `<project>_case_index.csv`, the retired export
  bundle's name; the index that ships is the package's `data/case_index.csv` —
  the #245 defect class a second time, three weeks after #245. The name is
  `report/tables.CASE_INDEX_FILENAME`, read by the package writer and the
  header alike, and `tests/test_package_data.py` asserts the header names a file
  the package carries. `CONVENTIONS.md` and `PROGRAM_SPEC.md` follow.

- **The weight seed button then offered to delete what it had seeded.** #269's
  seed extended the rows in the button body, which cannot move the retained
  row counter, so the next render warned *the row count says 24, but Items
  still holds 41* and rendered **Delete the last 17 row(s)** — the rows just
  added, under a contract that says *never deletes*. The seed is an `on_click`
  callback now, moving the counter the way row deletion always has
  (`tests/test_weight_seed.py`).

- **Swept with them.** `cli.py` still tracebacked on a project file whose top
  level is a JSON list (`AttributeError` out of the schema gate); the gate now
  refuses it as the error contract's `ValueError`, on every route.
  `GUI_USER_GUIDE.md` §6 said the *Export phase applies the ×1.5 factor* and
  shipped ultimate CSVs — contradicting §1 of the same document and note 49 —
  and §6/§8 still routed users through a Start phase, six phases and an editor
  that loads files; all re-cut to the converged GUI. The backlog rows that
  ruling 4 of the 2026-09-11 re-cut said close at #270 (#148, #247–#252, #259)
  are removed with their `app/views/` bodies, #29 is re-scoped to the surviving
  GUI and inherits L-8d's mutation half, and the two `40_history/` references
  follow note 61.

- **Every delivered file now states the frame its numbers are in (#242, tier M,
  2026-09-13).** The requirement the CSVs exist to serve — contents in airplane
  global coordinates, readable without the repository — was met by the data and
  not by the self-description: the per-file blocks said "right-handed about the
  airplane axes" and named torsion axes, and no delivered file anywhere said
  that `x` is the fuselage station positive aft. An **AXES** stanza now sits
  beside the UNITS one in the methods stamp, so it lands in band on the six
  applied CSVs, the case index, the gear report, the safety-factor table, the
  per-module CSVs, the V-n conditions file, `METHODS.txt` and the decks at once.
  The words are owned by `export/coordinates.AIRPLANE_AXES` / `AXES_NOTES` —
  beside the map they describe, which is already the declared single edit-point
  for an axis flip — and are rendered by one block and nothing else.

- **The one file that carries two frames now names both (#242).** The gear load
  report states each reaction twice: `Ground-line V/D/S` in the manual's
  ground-line frame at the contact patch, and `Patch`/`Datum`/`Ref point`/
  `Transfer` in airplane axes. A stanza saying "airplane axes" above a file
  where nine columns are not would have been worse than saying nothing, so the
  exception is stated in the file's own header block, beside the columns it
  applies to, and stands on its own for the one caller that downloads the file
  unstamped.

- **`MyyAxis` is `TorsionAxis`, because the fin's torsion is `Mz` (#242).** A
  lateral load makes no moment about `y`, and `applied_body_moments` has put the
  fin's torsion in `Mz` since note 44 OR-142 — so on one of the six applied
  files the column naming the torsion axis asserted an axis the data beside it
  did not honour. One name, true on every file. `net_loads.wing_load_rows` keeps
  `MyyAxis`: it is a wing-only table where the torsion really is `Myy`, and its
  schema is the published interchange format the external-comparison import
  reads.

- **A control-surface row says it is a surface-normal load (#242).** The
  deleted `control_surface_loads.csv` labelled that column `Fz` on every surface
  including the rudder. The rows survived into the h-tail and fin applied files
  correctly resolved — the numbers were never wrong — but nothing told the
  reader that the number in `Fy` on a fin row is the surface normal rather than
  a sideslip load. Both tail files now say so.

- **A file's structural zeros are measured, not asserted (#242).** OR-140's rule
  is that a zero column is published, never dropped, and the reason it is zero
  is published beside it. Both halves were prose — and note 56 D-56.9 then
  re-aggregated the delivered set onto the LRA grids, where each load carries
  the lever-arm couple of its own offset, so moments appeared on three axes that
  four of the six files still called zero "throughout". The claim is now read
  off the rows being written and the prose supplies only the reason; a column
  this configuration happens to leave empty is stated as that and not as
  something the model cannot fill; and a re-aggregated file states that its rows
  are at grids and that its moment columns therefore carry arms as well as free
  moments — the sentence whose absence let the zeros go stale.

- **The V-n conditions file carries the definitions its page prints (#242).** It
  had nineteen columns and left `M(W+F)`, `LZW`, `LT`, `DX` and `NX` defined only
  in the appendix's table notes. It now carries both notes, read off the same
  `Table` objects the appendix renders, and the notes lost their "above"/"below"
  so that they are true of a file that joins the two tables into one row.

- **A delivered CSV has one line ending (#242).** Every stamped file was LF in
  its comment block and CRLF in its rows, the prose being joined by hand and the
  data coming from `csv`'s default. `sloads/csv_text.py` owns the terminator and
  the two writer constructions the package makes; no call site passes
  `lineterminator=`, because a writer added without it produces a file that
  looks right in every viewer and is mixed on disk.

- **The doc-link guard stops failing CI on links into the local-only
  `reference/` tree (tier S, 2026-09-14).** Note 61's CV-6 guard
  (`tests/test_doc_links.py`) went red on its own closure commit: three links
  into `reference/` resolved locally and not on the runner, because that
  directory is gitignored whole — the manuals and circulars are copyright
  material kept on the developer's machine, as CLAUDE.md says. A link into a
  local-only tree is now accepted rather than checked; every other relative
  link is held to existing exactly as before.

- **The oracle GUI's results captions state LIMIT, and the GUI-source sweep has one owner (#239, note 60 §5, tier S, 2026-09-13).**
  `oracle_app/results.py` captioned every load-case table *"ULTIMATE loads (= limit x
  the case safety factor)"* over bytes that had been LIMIT since note 48 and were
  gated as LIMIT by G7 the whole time — the understrength direction, and the second
  front-end's half of #192. The caption is now the sentence `app/views/results_review.py`
  already carried: load columns LIMIT, the `SF` column stating the 14 CFR 23.303 factor
  the tool applies nowhere, and the `-ULT` marker only on a load the regulation already
  prescribes ultimate (23.367(a)(2), 23.561(b)).
- **The `ResultBlock` basis discriminator is retired with the claim it carried.**
  Since note 49 OR-116 there is one basis, so `ULTIMATE`/`LIMIT` are replaced by
  `CASE_TABLE`/`STATION_TABLE` — a block now selects its caption by the *shape* of its
  table (per-case `SF` column vs. station `Basis` column), which is the thing that
  actually still varies, and no value exists that could claim ULTIMATE again.
- **G-OR-74's screen sweep covers the oracle GUI.** `tests/test_basis_statements.py`
  excluded `oracle_app/` as a tree under note 44's OR-13 freeze, sweeping only
  `oracle_app/report.py` by name; the freeze lifted with 0.8.2 and the exclusion did
  not, which is why the false caption ran green beside the gate for a whole milestone.
  779 further literals are now in scope. Design note 57's gates 4 and 5 are asserted
  through this sweep, so #266 can depend on it.
- **`_GUI_TREES` converges on one owner** (`tests/helpers.GUI_TREES`, rule 4 / practice 3,
  note 60 §3). `test_basis_statements.py` and `test_app_shell.py` each kept a tuple of
  their own and disagreed about what "the GUI" is; a guard can no longer narrow its own
  scope without editing the owner every other guard reads. The shared tuple walks `app`
  whole rather than `app/views`, so `app/Home.py` is swept too.

### Removed

- **The shell is slimmed of what only the retired front-end called, and the
  statements that outlived it are re-cut (note 57 §8, tier S, 2026-09-13).**
  The end-of-milestone sweep #270 deferred: what the deletion left unreachable,
  measured by reachability from the production trees rather than by reading.
  Five public names had no caller outside the tests that pinned them.
  `app_shell/limit_csv.py` loses `wing_limit_csv` / `body_limit_csv` /
  `tail_limit_csv` — the per-page CSV download builders, whose callers were
  `app/views/` and whose channel is now the issue package's `data/` (#245); the
  `*_limit_rows` half they wrapped feeds the analysis pages' on-screen station
  tables and stays, with the units contract asserted on the rows rather than on
  the file. `app_shell/optional_slice.py` goes whole: its rule was *an Apply may
  not create an `Optional` slice out of nothing*, and the surviving GUI has no
  Apply step — it has #143's named add/remove gestures, which is the same rule
  in its stronger form. `CONVENTIONS.md` §7's row for it is re-pointed at those
  gestures rather than deleted, because the convention outlived its
  Apply-button owner. Nothing else in the shell was orphaned, which is what
  OG-B was for.

- **The release-state sentence stops naming a GUI that does not exist (tier S,
  2026-09-13).** `app_shell.components.RELEASE_STATE` — carried verbatim by
  `README.md`, `CAPABILITIES.md` and the About panel — said *"the oracle GUI
  production-ready; additional features and the full sloads GUI in beta"*. Half
  of that named the front-end #270 deleted, and "oracle" no longer distinguishes
  one GUI from another. It now reads *"Core analysis developed per FAR 23 LOADS
  and the GUI production-ready; concept-mode features in beta"*: the same mixed
  claim, about the software that exists. Its own docstring says to update it at
  a cut and not between them, and this is the cut. R-57.5's rename of the
  package and console script stays deferred and is now the only thing that
  claim's wording waits on.

- **Every statement in the code that still described two front-ends is re-cut
  (tier S, 2026-09-13).** Roughly forty sites across `sloads/`, `app_shell/` and
  `oracle_app/` said *"both GUIs"*, *"either GUI"* or *"the main GUI's <page>"*
  in the present tense — the standing justification for a single owner, written
  when there were two consumers to keep in step. The rule survives the second
  consumer; the sentence has to say so. Where the reason was historical it is
  put in the past tense and kept, because *why* an owner is where it is remains
  the useful half. Three were wrong rather than merely dated: `sloads/io.py`
  told a reader to run `streamlit run app/Home.py`; the Tail Loads page's
  caption sent them to a **Tail Span Loads** page that no longer exists, for the
  spanwise station table that is in the report's *Spanwise loads* subsections
  and the export decks; and `README.md`'s layout tree still drew `app/Home.py`
  and `app/views/` (and, from further back, `sloads/report.py` and
  `sloads/models.py` as modules).

- **The second front-end retires: 22 pages, 8,461 lines, and the document that
  shipped from one of them (#270, design note 57 D-57.1 + D-57.6 as amended by
  note 60 D-60.11, tier L, 2026-09-13).** `app/Home.py` and its 21 `app/views/`
  pages are deleted, and `oracle_app/` is *the* sloads GUI. The convergence's
  closing step: note 57 measured two front-ends over one calc package as a
  structural drift class rather than a capability, and D-57.8 required the
  survivor complete before anything was removed — which #265–#269 and #278 did,
  so this step only removes.

  **Deleted with the page set:** `content.build_report` and its nine section
  builders (`content.py` 2,639 → 653 lines); `latex.render_document` /
  `render_report` and the title page and running heads with them, leaving
  `latex.py` the section/table/figure emitters `oracle_latex.py` builds on;
  `sloads/report/bundle.py`, the Export zip's member list, whose only consumer
  was the page; and `sloads/export/workbook.py` with its `openpyxl` dependency
  (the owner having ruled the `.xlsx` unused, and #245's `data/` being the
  single tabular channel — no replacement is built). Five pages retired without
  port, each citing its successor: `dashboard` (the shell's sidebar carries the
  project), `results_review` (`oracle_app/results.py`), `export_report` (the CLI
  and the Report page), `tail_span_loads` (the report's tail-span appendix) and
  `balanced_cases` (the balanced deck and `balanced_case_rows`).

- **The page set is still derived, and now states its exceptions (D-57.1).**
  `workflow.gui_pages()` is the owner: the fourteen derived analysis pages
  (`oracle_steps()` — *runs a `.BAS` program, or produces a slice such a step
  requires*) plus `workflow.NON_STEP_PAGES`, three pages that are not steps of
  the analysis and each declare why — the Project JSON Editor, the Aircraft
  Comparison and the Report. Gate G2 survives the re-cut on the OR-16 pattern:
  adding a `bas` to a step still adds a page with no GUI edit, and what is
  listed is only the set no analysis can derive. `STEPS` loses the six GUI-only
  rows that were page declarations and nothing else, and `PHASES` drops from
  seven to four — `Start`, `Load-case plotting` and `Export` held those rows
  and would otherwise be phases no step can be in, which a new guard refuses.
  `tail_span_loads` and `balanced_cases` stay: they run registered calc modules
  and always were analysis rather than presentation.

- **Two claims about the retired front-end turned out to be wrong, and both had
  no test.** `cli.py --report` was a second production consumer of
  `content.build_report` — note 60 and #278's backlog row both called the Export
  page the only one — so the flag broke silently when the builder went and the
  suite stayed green. It now renders the surviving document (the document alone;
  the issue package is the Report page's) and `tests/test_cli.py` holds it to
  the reachability rule the export menu has always had. Widening that guard
  found the CLI's one error contract covered everything the *analysis* could
  refuse and not the thing every route does first: `io.load_project` sat outside
  every route's `try`, so a file that was not JSON came out as a traceback on all
  four. `cli._load` is now the single entry and `cli.main` the single handler
  (rule 4 — the fix sweeps the class it was found in).

- **`data/case_index.csv` gains the assembled column it shipped without.** The
  package's case index was built from the applied sets and the module results
  and not from the assembled cases, so its `LOAD/SUBCASE (assembled)` column was
  empty on every row: a reader holding the LRA beam model — the primary
  deliverable — could not trace a `SUBCASE` back through the one tabular channel
  there is. It shipped that way from #245 and was invisible while the summary
  report printed a complete index beside it. Found by re-pointing that report's
  index-agreement test at the artifact that ships.

## [0.8.3] — 2026-09-13

### Added

- **The LRA beam model gets a three-view renderer (`scripts/plot_lra_model.py`, tier S, 2026-09-10).**
  A display-only analyst tool over the public exporter API: project JSON in, one
  4-panel PNG out (isometric + plan + side + front) of the step-12 skeleton --
  CBAR chains by section family, RBE2 ties, BM-5 tagged nodes, the SPC support
  -- with the planform/body outlines overlaid from the same geometry owners the
  exporter reads (`--no-outlines` to omit; wing/h-tail edges are draped at the
  beam chain's waterline, a stated picture convention). The exporter's refusal
  contract is kept verbatim: an `LraRefusal` prints its named datum and exits 2,
  never defaulting it. matplotlib joins the `dev` extra; smoke-tested on the
  conventional, T-tail and twin example projects (`tests/test_plot_lra_model.py`).

- **The oracle report states what the beam grids cost the distribution (note 56
  D-56.10, tier L, 2026-09-12).** New **Appendix G**: one table of the widest
  gap in each internal-load channel of each member, over every case, and four
  figures — wing, fuselage, horizontal tail, fin — plotting that gap along the
  span for the case that bends the member hardest. It is the counterpart to
  D-56.9, which sums the applied set onto the beam's grids: the set's
  **resultant** is preserved exactly and gated, and this is where the
  **distribution** it moves is stated instead of left to be discovered.
- **New owner `sloads/report/lumping.py`.** The internal load at a cut is the
  static resultant of everything outboard of it, transferred to the cut through
  the same LM-1 owner the aggregation uses — one rule for shear, bending and
  torsion on all four members — evaluated twice about the same cuts, once from
  the load stations and once from the delivered set. **No solver is in the
  loop**, so the figure is a discretization comparison and not an idealisation
  one, and it is reproducible in CI. Cross-checked against
  `sob_internal_loads`, the single-cut instance it generalises, at the wing root
  of every case of four fixtures.
- **There is no acceptance tolerance, and the appendix says so.** The size of
  the difference is a function of the grid counts the project sets, so a fixed
  limit would fail a coarse mesh behaving exactly as specified.

### Changed

- **The applied load set gets its right address and `sbeam_bridge.py` ceases to
  exist (note 56 D-56.1, tier M, 2026-09-11).** `AppliedLoad`,
  `applied_loads` and its five component row builders, `applied_body_moments`,
  `applied_load_csv`, the side-of-body internal loads and the station numbering
  they state all live there now. It was never a bridge to sbeam: it is the record
  of what is applied and where, which the oracle report's applied appendices are
  built from directly.
- **Import from `sloads.report.applied`.** No shim is left at the old address and
  the export package no longer re-exports any of it — a guard refuses both.
- **Nothing delivered changed.** Module views, the case index, both reports,
  every CSV and every deck are byte-identical across the move.

- **The applied load set is stated at the LRA grids (note 56 D-56.9, tier L,
  2026-09-12).** `applied_loads` returns one row per (case, grid): every
  aerodynamic station and every concentrated mass is summed onto the nearest
  node of the member that carries it, with the exact lever-arm couple. The two
  grid sets do not align — the beam mesh is decided from geometry alone — so
  several stations generally land on one grid. The appendix row, the
  `*_applied_loads.csv` row and the `FORCE`/`MOMENT` card are now one object at
  one point.
- **`station_applied_loads` is the set before it is lumped**, and stays public:
  the calc's own distribution at the load-integration stations, which is both
  the aggregation's input and the reference curve of the VMT comparison.
- **`project` is now required** by `applied_loads` and `applied_load_csv` — the
  beam is built from it, and a caller without one cannot be handed the delivered
  set. Ask for `station_applied_loads` by name when that is what you want.
- **The resultant is unchanged and gated; the distribution is not.** LM-1
  preserves each load's resultant about every reference exactly, per component
  and per case. What moves is where the set says a load is carried — a real
  discretization difference, which the report will state as a VMT comparison.
  One consequence is visible today: a moment component that is zero at a station
  is generally **not** zero at a grid, because moving a force across an offset
  makes a couple. The applied appendices say so.

- **The assembled full-span deck stops being a shipped artifact (note 56 D-56.8,
  tier L, 2026-09-12).** Four surfaces retire in one change: the Balanced Cases
  page's stamped download, the Export & Report page's row, the `.bdf` inside the
  bundle `.zip`, and `cli.py --export-target balanced`. The report's Appendix A
  manifest loses its row with them — a controlling document naming a file the
  reader was never given is review F-D2's defect pointing the other way.
  `EXPORT_TARGETS` goes 4 → **3**: `gear` stays because D-56.1 reclassified the
  gear interface report as a *document* and this is its only headless route.
- **What ships in its place already did.** The **LRA beam model** carries the
  same assembled cases, transferred onto the beam's own grids, free-free, one
  `SUBCASE` per case — so nothing left the deliverable, one of two files
  carrying the same load sets did.
  `tests/test_cli.py::test_the_beam_deck_is_reachable_headless` is review F-D1's
  gate moved to follow the artifact rather than retired with the file it was
  first written about.
- **One stale manifest description swept with it (rule 4).** The mass model's
  row still said "for splicing into a model that already has nodes" — untrue
  since D-56.6 gave every `CONM2` its own `GRID` at its own CG. It now states
  what the file is and what splicing it costs: an `RBE2` per mass.
- **`balanced_deck` stays, as a genuine internal producer.** Its text is the
  un-aggregated load set at each load's true position, and its resultant is what
  the transferred set is gated against (`test_the_transferred_set_has_the_
  balanced_decks_resultant`). Deleting it would have deleted the reference the
  deliverable is checked against.

- **The boundary-derived seam is marked in the tail input blocks (#25 step 1,
  note 54 D-54.1, tier M, 2026-09-10).** The planform-geometry scalars the
  boundary-line model will derive — every area, span, MAC, MAC station and
  aspect ratio (9 of the h-tail block's 17 fields, 10 of the v-tail's 15, the
  wing-sourced `ARW` and `B` included) — are named in the new machine-readable
  maps `models.inputs.HTAIL_BOUNDARY_DERIVED` / `VTAIL_BOUNDARY_DERIVED`
  (`{field: deriving surface}`), which step 2's derivation consumes, and each
  carries a `[D]` mark that travels into the generated `DATA_DICTIONARY.md`;
  the aero, control-setting and mass/inertia fields are the stated remainder,
  and `vtail_root_waterline_z` is called out as placement (the L-1 owner's
  field), not planform. Field order is untouched — it is a persisted shape
  (`test_schema_guards.fields_hash`), so the physical regrouping rides step
  2's own schema bump rather than spending a version hop on cosmetics. No
  behavior change: every scalar stays entered and oracle-authoritative until
  step 2. Guard: `tests/test_empennage.py::
  test_the_boundary_derived_marking_partitions_the_tail_blocks` — every field
  of both blocks must declare its side of the seam.

- **The boundary-line model: entered lines derive the tail scalars (#25 step 2,
  note 54 D-54.1/D-54.8, tier L, schema v65, 2026-09-10).** The tail group's
  geometry is now entered as its **five boundary lines** — tail LE, tail TE and
  control LE (the `geometry.surfaces` polylines), the control's new
  `hinge_line` (v65), and the control's TE, which **is the parent's** along the
  interior of its span and therefore derives instead of being entered a second
  time (`tail_geometry.derived_control_trailing_edge`; an entered copy is held
  on the parent's line by `validate_control_trailing_edge`, hard on the tail
  groups — the wing controls join at the #260/D-54.6 fixture wave, whose
  estimated aileron polylines sit up to 9.4 in off their wing TE today). Every
  `[D]`-marked scalar of the two tail blocks (`HTAIL_BOUNDARY_DERIVED` /
  `VTAIL_BOUNDARY_DERIVED`, the #25 step 1 seam) **blank-derives** from the
  lines through `tail_geometry.boundary_derived_scalars`, consumed by
  `select.effective_tail_inputs`/`effective_vtail_inputs` and by
  `resolve_tail_planform` (note 36 OV-1: typed overrides, blank derives); the
  hinge halves SEFWDHL/SEAFTHL and SRFWDHL/SRAFTHL derive from the hinge
  line's area split (`control_hinge_areas`). A typed scalar stays
  authoritative — every Appendix A pin is untouched, `ga6_normal`'s
  elevator/rudder TEs are removed from the fixture because the derivation
  reproduces the printed tables byte-for-byte, and the Imperial digests did
  not move. Appendix A's printed h-tail/elevator/rudder figures are now
  **±0.1 % predictions** of the model (page-cited gate in
  `tests/test_tail_geometry.py`), and `validate_tail_planform` compares
  entered scalars only, retiring field-by-field as they stop being typed.
  `LayoutInput.htail_dihedral_deg` (D-54.8) is **declared, not modelled**: no
  load reads it (guarded) until note 51's dihedral guard and method spend it.
  The two tail input blocks are physically regrouped into the seam order with
  this bump — the regrouping step 1 deferred to the change that earned the
  version hop; the 64→65 migration is an identity.

- **The certification-basis / case-coverage matrix leaves the ranked backlog
  (#47 closed not-planned, tier S, 2026-09-11).** Owner ruling from the
  2026-09-10 scope-reduction review: the matrix is a DER-package feature off
  the mission bar (loads → sbeam + oracle report), so band C's row moves to
  `02_parked.md` as off-mission with its body preserved on the closed issue.
  Activation is stated — the methods-manual/DER-package direction, or before
  the next FAR 25 case build, design note first. Decided, not built.

- **The load-output contract's statements get one owner, and eight copies of the
  solver unit set collapse to it (note 56 D-56.1, tier M, 2026-09-10).**
  `export/deck_format.py` — the card-writing primitives module #15 created for
  exactly this defect class — now also owns *what a load is stated to be*:
  `solver_units`, `basis_sentence`, `load_label`, `ult_label`, `case_sf` and
  `SUITE_SF`, promoted out of `sbeam_bridge`'s underscore namespace under the
  names the writers actually mean. The authority for *which* factor a case
  carries is unchanged — `safety_factors.py` (M4-8 / G-11) decides, these only
  render it.

  `deliverable_units(system, Channel.SOLVER)` — the choice of which unit set a
  deck may be written in — had been copied into a private `_units` helper in
  **four** export modules (`sbeam_bridge`, `balanced_deck`, `roundtrip`,
  `lra_model`) and written inline in **four** more (`mass_cards` ×4,
  `lra_import`, `workbook`, `coordinates`). All eight now read one owner, and
  `tests/test_deliverable_units.py::test_only_deck_format_resolves_the_solver_channel_in_the_export_package`
  fails the day a ninth appears (rule 3: the owner *and* the drift guard).

  **Found while doing it: the rename would have silently blinded G-OR-71.**
  `tests/test_limit_channel.py` scans the whole tree for a surviving
  limit→ultimate multiply, and its pattern matched `* _sf(` and `\bsf\b` — but
  `\bsf\b` does **not** match inside `case_sf`, because `_` is a word character
  and there is no boundary before `sf`. A text guard that matches nothing still
  passes, so nothing in the suite would have gone red. The pattern now names
  `case_sf` explicitly, including its dotted form, with three teeth assertions
  and the reason recorded in the source.

  No delivered byte changes: the Imperial digest's 330 channels are identical,
  and the whole suite is green.

- **The deck-writing primitives get their own module (CH-4, #15, tier S, 2026-09-09).**
  `sloads/export/deck_format.py` is now the single owner of *how a bulk-data card is
  written* — the NASTRAN number format (`fmt`), the vector-card triple with its dust
  snapping (`fmt3`, `snap_zero`, `CARD_TOL`), the `SF` spelling (`sf_str`), the 72-column
  `$` comment wrap (`comment`), the `$`-block stamp (`stamped`) and the placeholder
  `MAT1`/`PBAR` section properties a determinate stick model needs to be solvable. Five
  sibling writers — `mass_cards`, `balanced_deck`, `lra_model`, `lra_import`, `roundtrip`
  — reached across the package for these through `sbeam_bridge`'s underscore; a private
  imported from another module is not private, it is an undeclared API whose every rename
  is a silent breakage. The names are public at their new owner and the cross-imports are
  gone. Pure move: no deck byte, CSV cell or printed figure changes, and the oracle,
  closure and frozen-Imperial-digest suites are unmoved. `CONVENTIONS.md` §7's
  platform-stable-bytes row and `PROJECT_GUIDE.md` §4 name the new owner.
  `test_platform_stability.py`'s emitted-value sweep now patches the formatter at **every**
  binding rather than at one module's — with the primitive outside `sbeam_bridge`, the old
  single patch would have shrunk a 159,407-value population sweep to one file's cards
  without failing.

- **The export package closes on one solver artifact (design note 56, #263, tier L, 2026-09-12).**
  The tier-L closure of a ten-slice change. `sloads/export/` goes from **8,603
  lines across 15 modules to 5,307**; four parallel model concepts become two;
  `cli.EXPORT_TARGETS` goes from ten targets to three (`lra`, `gear`, `mass`).
  What ships to a solver is the **LRA beam model** of the whole free-free
  airplane, plus the **CONM2 mass model**. The five per-component decks are
  deleted, the elementless assembled deck no longer leaves the tool, and
  `sbeam_bridge.py` — which the oracle report reached into at seven sites — no
  longer exists: the applied-load model and the deliverable tables that were
  never decks are `report/applied.py` and `report/tables.py`.

  This entry closes the sweep rather than the code. `CONVENTIONS.md` §7 gains a
  row for D-56.3 (every `GRID` in a deliverable comes from one contiguous band
  that deliverable owns) and re-cuts the joint-register and
  skeleton-solvability rows — the latter named `JOINT_MERGE_FRACTION`, retired
  at D-56.4, and the floor that replaced it guards a different thing. Two §1
  conventions are **retired in place**, struck and explained rather than
  deleted: "a load that a free-body cut introduces is never applied in the
  assembled model" and E-2's per-component moment reference, both of which
  argued about artifacts that no longer exist. `PROGRAM_SPEC.md`'s artifact
  statement and its D-R5 bullet are re-cut — D-R5 named a guard deleted with
  the wing deck, and the rule it protected now holds by construction, one
  producer with every consumer a view of it. `PROJECT_GUIDE.md`'s
  frozen-baseline paragraph loses four wrong facts in one clause and gains one
  that was never stated: the Imperial baseline digests one **non**-deliverable,
  the assembled deck, because gate 13 checks the beam model's re-aggregated
  load set against its resultant. `docs/20_theory/ch11_export_sbeam.md` is
  swept under rule 4 — its two validation tables are kept as the record of
  gates written against retired artifacts, each saying what it now applies to.

- **The LRA beam gets its own mesh, decided from geometry (note 56 D-56.4,
  tier L, 2026-09-11).** The beam *was* the load mesh: the wing chain was the
  WINGGEOM strips outboard of the side of body and the tail chains were the
  spanwise load stations. So the spanwise half of the LM-1 transfer was an
  **identity on every CI fixture**, and the arbitrary-grid routing a real user
  hits first was the least-covered path in the package — a degenerate special
  case hiding the general one. It also made one mesh serve two contracts: the
  strip count the replication oracle freezes at 20 was also, silently, the
  structural model.

  Each member's node set is now its own two **ends**, the joint register's
  owned locations on it, and `n` grids laid at equal spacing *between*
  consecutive owned points. `n` is per component and settable —
  `Project.lra_mesh` (**schema v66**, identity hop from v65) — defaulting to
  **wing 20 per side, fuselage 12 per cantilever, h-tail 12 per side, fin 10**.
  Blank means the default and every bundled example is blank. The WINGGEOM
  strips stay oracle-locked at 20 and simply stop being the beam.

  **A member runs to its own tip.** The wing chain used to stop at the
  outermost strip *midpoint* — 5.0 in inboard of the tip on `ga6_normal`
  (2.5 % of semispan), 12.1 in on `atr42_100`. That is the omission design note
  54 D-54.5 fixed for the fin, where it only got fixed because the T-tail tie
  made the tip a joint; with no tie to force the issue on the wing it survived.

  **The sliver class dies structurally.** Nothing is inserted any more, so a
  joint cannot land a percent of a strip from a station: the owned points come
  first and the grids are strictly interior to the segments between them.
  `JOINT_MERGE_FRACTION` retires. What replaces it is narrower and means
  something different — `_MIN_ELEMENT_FRACTION`, 1:200 of a member's target
  element length, catching two **owned** locations genuinely that close in the
  entered geometry, which is a data condition and gets a message that names the
  two points rather than asking for a bug report.

  Three gates land: no member can carry a sliver (by construction, on every
  member rather than the two tail chains the merge band covered); **the mesh is
  load-blind** — no chain node sits on a load station, and changing a grid
  count moves no delivered resultant; and a count below 2 is refused by name.
  Only `sbeam/lra_model` re-stamps — four channels. Every other deliverable is
  byte-identical and the round-trip solve gate passes unchanged.

- **The LRA model owns every grid it writes (note 56 D-56.3, tier M,
  2026-09-11).** The one shipped solver artifact took its right-wing station
  ids from the deleted wing stick deck's band, its two tail chains from the
  deleted spanwise decks', its hinge and actuator nodes from the deleted
  chordwise decks' and its gear nodes from the balanced deck's — four artifacts
  numbering the grids of the one that ships, three of them not deliverables and
  two of them gone. The model now allocates from **its own contiguous run,
  `20001–30999`**, one 999-wide sub-band per node family in a fixed order, so
  `gid // 1000 - 20` is the family index and a grid id read off a deck or a
  solver echo says what kind of point it is without a lookup. `sob_gid` moves
  to `lra_model` with it — one consumer, and this was it.

  Eleven bands replace six; the old `7001–7880` run and the borrowed ranges are
  left **unregistered rather than reused**, as D-56.2's retirements were. The
  bands still registered below the retirement line belong to the **applied-load
  model**, which keeps its own station numbering until D-56.9 re-states it at
  the LRA grids — so `bands.py`'s collapse to ~8 completes there, not here.

  Two gates land with it: **every LRA grid comes from the LRA's own band**,
  asserted from the emitted deck text on four fixtures (note 56 gate 4), and
  **no GID is defined at two positions across the shipped decks** (gate 3). One
  latent alias goes with the renumber: the fin tip and the h-tail's left
  attachment shared attachment index 2, safe only because a T-tail has no left
  attachment.

  Only `sbeam/lra_model` re-stamps — four digest channels, one per fixture with
  an LRA deck. Every applied-load CSV, the balanced deck, the mass deck and
  both reports are byte-identical, and the round-trip solve gate passes with
  its two known SI xfails unchanged.

- **Every `CONM2` sits on its own `GRID` at its own item's CG (note 56 D-56.6,
  tier M, 2026-09-12).** A mass card used to hang on the nearest fuselage beam
  station and carry `x1/x2/x3` back to the item's true position. It now has a
  grid of its own, at that position, with a **zero** offset — so the mass model
  is self-contained and states no attachment it does not have. The wing-item
  limitation retires with it: a wing mass is at the wing mass's position, not on
  a fuselage node with a caption explaining why.
- **The grids are unconnected by design, and the deck says so.** sloads ships no
  tie, so a stiffness solve over the mass model is singular. The header names the
  condition, the reason, and the remedy (an `RBE2` per grid) rather than letting
  a reader discover it by running one. The placeholder massless beam and its
  `SPC1` are deleted — nothing is left for them to support.
- **The mass model is checked by a grid-point weight recovery, not by a solve**
  (D-56.7). `inertia_only_cards`, `case_station_weights` and
  `roundtrip.flatten_mass_case` are retired: they cross-checked sloads' reduction
  of a mass to a beam station, and there is no reduction left. sbeam's GPWG reads
  mass and CG off the deck **as shipped**, per payload case, in both unit
  systems. `--export-conm2` and the bundle now write two files, not three.

- **The development plan re-cuts into three milestones: 0.8.3 closes the export
  contract, 0.8.4 converges the front-ends, 0.8.5 cleans up (backlog re-cut,
  tier S, 2026-09-11).** 0.8.3's named deliverable — the T-tail empennage
  geometry model — shipped with #25, leaving one L-tier note in flight (#263,
  note 56) behind a 21-row defect-and-polish tail, while note 57 sat **AGREED**
  and gated on "the 0.8.3 cut". Band **B4** is now #263 plus the rows that close
  with it (#173, #176) and #16 as note 56's pre-clean; band **B5** keeps note
  57's D-57.8 sequence with **#241, #242 and #245 inserted before #270** —
  #245's `data/` is the successor channel note 57 §1.3 names for
  `export_report`, so the retirement cannot precede it — and #255 closing
  superseded at #270; new band **B6** (milestone **0.8.5**) carries the
  remaining eighteen, landed once against one front-end. Band **B2** is
  re-chartered to calc, report and process work: the "main sloads GUI
  development" it was named for retires with #270. The whole table is
  renumbered densely (Pri 1–57) and the superseded preambles roll to
  `90_record/44_backlog_state_narrative_to_2026-08-29.md`.

  Two costs are booked rather than discovered: the baseline wave splits
  (#241/#242 move to 0.8.4, so digests regenerate twice — both are column
  additions to files the wave already rewrites), and **#179/#180 are deferred
  as latent**, not as polish — #179's first-match hole has no current producer
  and #180's `getattr` fallbacks are dead defaults, so rule 6 permits the
  deferral, and it is named here so it is a decision. The efficiency claim is
  stated narrowly because it was measured: the convergence avoids **one**
  tier-S row of duplicated effort (#255); `format_value` has zero `app/` call
  sites, #243/#177/#239 are on the survivor, and D-56.2's seven `app/views/`
  consumers were already paid.

- **The backlog is re-scoped onto the package note 56 left behind (tier S, 2026-09-12).**
  Seven surviving rows carried note 56 as a *forecast*; each now states what
  landed. #241's `AppliedLoad` fix has an address (`report/applied.py`) and the
  six `*_applied_loads.csv` files are the only applied-load CSVs left; #242
  narrows to the report's own files, with the control-surface `Fz` question
  surviving as rows *inside* the h-tail and fin files rather than as a file;
  #209's case index landed at `report/tables.py`, so its decision now touches
  three owners (`load_cases_to_rows`, `load_cases_csv`, the index itself);
  #191 loses the `sbeam_bridge.py` half and re-measures its candidates
  (`balance.py` 2,842, `report/content.py` 2,625, the new `report/applied.py`
  1,561); #254 and #245 restate their narrowings as landed. **#17's forecast was
  wrong in one half and says so**: `_export_sbeam` was not deleted with the
  per-component targets — it lost its branches and stands at 53, off the list —
  and `_manifest_rows` measures 131, not the 155 the row carried.

- **Three findings owed since note 56 are filed, and band B4 re-opens for one of
  them (tier S, 2026-09-12).** #274: the oracle report's balanced-cases
  paragraph and the Balanced Cases page still call the assembled model the
  primary deliverable and the per-component decks its analysis views, and the
  wing-root note attributes the `lra-sob` reporting node to the deleted wing
  stick deck — three false statements in shipped content, which the ordering
  rules put above every [V] item, so 0.8.3 does not cut over them. #275: the LRA
  mesh guarantees no fuselage owned point at the spar carry-through, and
  Appendix G measures the cost (fuselage shear 82–197 % of the channel's own
  peak; a ~107,000 lb reaction one bay from where it acts on
  `concept_regional_jet`). #276: `WeightEstimationInput.engines` is a count
  where `Project.engines` is a list, invisible to the units walker's totality
  gate and pinned meanwhile in `_KNOWN_AMBIGUOUS`.

- **The deliverable tables that are not decks move to `report/` (note 56 D-56.1,
  tier M, 2026-09-10).** The case index, the governing safety-factor table, the
  gear interface report and the export-scope filter they share are now
  `sloads/report/tables.py` (409 lines). None of them emits bulk data or knows
  what a GRID is — they are documents, and `report/` is where documents are
  assembled, which is why `report/content.py` and the oracle sections were
  already reaching back across the package to import them.

  Every row, column, header and byte is unchanged; the frozen Imperial digest is
  the proof. `sbeam_bridge.py` drops 3,013 → **2,639** lines.

  **The export package no longer re-exports them**, and a guard asserts it does
  not: a re-export would leave one name at two addresses, which is the condition
  D-56.1 exists to end. `sloads.export.__init__`'s docstring says where they went
  instead. Consumers re-pointed: `report/content.py`, `cli.py`, the Export page
  and the Landing-loads page.

  Two allowlists keyed on the old path were corrected — `test_envelope_owner`'s
  `_ALLOWED` (the reason belongs to the table, not to the bridge) and
  `test_ultimate_contract`'s `_ULT_CHANNEL`, which reads download-call text and
  would have passed silently on a page whose call had moved to a new alias. That
  is the second text guard this note has caught keyed to a name it was about to
  lose, after G-OR-71 in the previous slice.

- **The plane a surface is defined in has one owner (#220, tier S,
  2026-09-09).** Design note 54 D-54.2: whether a surface's span coordinate is
  a butt line (wing, h-tail, their controls) or a waterline (fin, rudder) is
  now answered once, by `sloads.tail_geometry.surface_plane` returning
  `SurfacePlane`, replacing the five per-call-site name tests — the four
  local→airplane maps in `export/coordinates.py` and the three-view's
  mirror/view branch in `modules/configuration.py` (its private
  `_WATERLINE_SPAN_SURFACES` tuple removed). Docstrings that claimed the
  second polyline coordinate is a butt line (`XYPoint`, `SurfaceInput`,
  `wing_geometry.interp_x`) corrected. New guards tie the coordinate maps and
  the report's declared frame/span-axis data back to the owner; `CONVENTIONS.md`
  §7 gains the SSOT row. No user-selected plane field yet (deferred with
  V-tail/cruciform support, note 54 §8). No load, deck byte, or delivered
  file changes.

- **The theory documentation becomes a chaptered manual (tier S, 2026-09-10).**
  `docs/20_theory/` is restructured for an engineer reader: eleven `chNN_`
  chapters on one template (scope, cases analyzed, method, assumptions &
  limitations, worked example, validation, sources) beside the slimmed hub
  `00_theory_sources.md` (sources, oracle status, citation rules, provenance
  policy, per-module citations, chapter map). New chapters: introduction
  (ch01, incl. the two front-ends and the no-physics-in-front-ends
  invariant), illustrated conventions (ch02, four script-generated SVG
  figures — `scripts/render_theory_figures.py`, new), wing (ch04), empennage
  incl. one-engine-out (ch05), fuselage (ch06), ground (ch08) and mass model
  (ch10) — the last four as stubs with assumptions and validation populated
  first. Renames: `design_airspeeds.md` → `ch03_airspeeds_envelope.md`
  (+ a new V-n envelope / case-inventory section), `engine_loads.md` →
  `ch07_engine_loads.md`, `balanced_cases.md` → `ch09_balanced_airplane.md`
  (+ §11, the closure-gate record). The hub's concept-mode closure
  narratives moved into the chapters' validation sections with a pointer map
  left behind; `01_far25_gap_analysis.md` relocated to
  `docs/30_future/04_far25_gap_analysis.md` (a plan, not theory). Link sweep
  across `PROGRAM_SPEC.md`, the corrections register, `30_future/` notes,
  two test comments and `00_INDEX.md`; historic documents (`40_history/`,
  `50_reviews/`, `CHANGELOG.md`) keep the names of their day.

- **Down-select on the ultimate basis; deliver LIMIT (#193, note 58, tier M,
  2026-09-11).** Comparisons *between* load cases — governing-case picks and
  cross-case envelopes — now key on `safety_factors.ultimate_basis`
  (`|value| × prescribed SF`, the quantity structure is sized to), while every
  delivered load stays LIMIT with the factor stated and applied nowhere: note
  49 OR-116 is confirmed by explicit ruling and #193's deliver-at-ULTIMATE
  half closes **decided, not done**. A full sweep found exactly one
  mixed-factor reduction in the suite — the Loads Plots pointwise envelope
  over the fin's chordwise set, SF 1.0 OEI curves against SF 1.5 SELECT
  curves on raw LIMIT magnitude — and `report.envelope_extremes` now takes
  the per-series factors and **refuses a mixed selection by name**
  (`safety_factors.uniform_factor` owns "same basis"); the page draws the
  per-case curves and states the withholding in band. G-OR-113 re-keys to the
  ultimate basis with the pin that no shipped pick flips (the governing VD
  case leads by ~2.2× on both twins). No delivered byte moves; `CONVENTIONS.md`
  §7 carries the owner row. The set-membership defect the sweep found (the
  summary report's v-tail governing table omits the OEI rows its chordwise
  table carries) is filed as #272, not folded in.

- **One surface, one name: `fin_*` identifiers retired for `vtail_*` (#223,
  tier S, 2026-09-09).** The mechanical sweep of the 2026-09-06 ruling
  (`CONVENTIONS.md` §7.2): every production identifier spelling the vertical
  tail "fin" — `fin_root`, `fin_root_waterline`, `FinRoot`, `FinCase`,
  `fin_sets`, `fin_load`, `ATTACH_FIN_TIP` and their kin — renamed to the
  `vtail` token across `sloads/`, the front-ends and the tests, first in the
  tail-geometry cluster so #219/#220/#54-series edits land on the agreed
  names. Serialized names are deliberately kept (`cy_beta_fin`/`cn_beta_fin`
  schema fields; the `balanced_fin_load`/`fin_angle_of_attack` LoadValue keys
  — renaming those is a schema/baseline change, not a spelling fix), prose may
  still say "fin", and the guard
  `tests/test_tail_geometry.py::test_no_fin_identifier_survives_or_returns`
  walks every production identifier so the seam cannot reopen. No load, deck
  byte, or delivered file changes.

### Fixed

- **#273 takes its row and the priority table is dense again (backlog hygiene,
  tier S, 2026-09-11).** The #16 sweep's residue was filed against milestone
  0.8.5 with a `band:` label and no row, which `scripts/backlog_issues.py check`
  refuses — and rightly: a banded issue outside the table is work with no place
  in the single order. It enters **band B6** at the hygiene front, where its two
  halves belong together: `io.py` and `report/oracle_package.py` each declare
  their own constants for `report.json` and `build.json` (two owners for one
  filename, the class practice 3 exists to prevent), and
  `gear_loads.LEG_WEIGHT_UNSET_NOTE` is public, in `__all__` and read by nothing,
  so a leg with no entered weight shows an OPEN free body with the explanation
  written and unrendered. The table renumbers densely 1–57, closing the gap the
  2026-09-11 re-cut left at Pri 4 when #16 closed. One stale ordinal goes with
  it: #191's `after #15 (Pri 14)` — a doubled reference that survived the re-cut
  pointing at neither the issue nor the row it meant — now reads `after #186 at
  the hygiene front`, named by issue so the next re-cut cannot strand it.

- **The open-defects index loses two wrong issue numbers, a deleted body and
  three closed entries (backlog hygiene, tier S, 2026-09-11).** The 2026-09-08
  index tidy (`07b24e2`) collapsed the *Open defects* bodies to one-line
  `#N — title` stubs and assigned the numbers positionally, which mis-stapled
  two: **"No engine-mount case reaches the LRA deck"** — an unfiled 2026-09-07
  finding with a full body — became `#209`, which is the load-case index's
  blank-load-columns defect, and its body was deleted; **"Review 2026-09-04
  small items"** became `#16`, which is Dead code (CH-5), now a 0.8.3 row. The
  engine-mount body is restored verbatim with the number struck and the gap
  re-verified live (the `lra-engine` band still allocates grids at
  `bands.py:274`; `transferred_case_loads` still takes a `BalancedCaseResult`,
  so no 23.361/23.363/23.371(b) condition reaches the deck); the small-items
  entry is deleted as redundant — all six are rowed (#175, #176, #179, #180,
  #188) or closed (#178). Three closed entries leave under the removal rule:
  **#170** (with the stale `Pri 49` ordinal the rows-never-cite-ordinals rule
  bars), **#181** and **#182**, whose "close on GitHub" instruction is
  discharged. Notes 56 and 57 lose their stale band/ordinal citations
  (`band B4 Pri 29` → `band B4`; `#255 in band B4` → band B5).

- **`baron_58` joins the Imperial output baseline — and every EXAMPLES-driven
  sweep — and the baseline's example list becomes structural (#271, tier S,
  2026-09-11).** The D-21 guard's hand-kept `EXAMPLES` tuple claimed "every
  shipped example" but was never extended when `baron_58` shipped, so the
  closure-locked twin's delivered bytes — 54 channels, more than any pinned
  fixture — had no byte-level drift guard; and since six other suites use
  `EXAMPLES` as *the* fixture walk, baron was also absent from the pinned
  assembly, ground-case, lateral, Izz, dCD, payload-derivability, couple-node
  and tail-coverage sweeps. All are now pinned from measurement (its SIDE
  GUST and wing families drop on non-derivable loadings, recorded per F-C7;
  the lateral pin's full-set assert relaxes to legality with the exact set
  per fixture), the digest fixture is regenerated additively (every existing
  digest byte-identical), and the prose claim gets its rule-3 drift guard:
  `test_deliverable_units.py::test_the_baseline_pins_every_bundled_example`
  ties `EXAMPLES` to the `examples/` directory, so a fixture added or removed
  without a deliberate regeneration fails loudly. Found while retiring two
  fixtures at #264.

- **The conventional h-tail no longer sits on the wing-root waterline (#261,
  design note 54 D-54.4, tier M, 2026-09-10).** `tail_geometry.h_tail_waterline`
  is completed: a conventional tail with no entered `h_tail_z` now takes the
  h-tail **mass items' weight-weighted `z`** (ASSUMED, basis `mass-item`)
  before falling back to the wing-root plane, now loud and last — an entered
  statement of where the surface's mass sits beats a placeholder printed as an
  airplane coordinate. And the **two-spellings rule**: a declared T-tail whose
  entered `h_tail_z` contradicts the fin tip by more than `PLANFORM_TOLERANCE`
  of the fin span gets the fin tip *and an in-band note naming the entered
  value NOT USED* (the #260 E5 pattern made loud). Swept per rule 4: the
  three-view sketch (`configuration.tail_planform`) now reads the owner with
  the project in hand instead of its own entered-else-wing-root copy, and the
  report's provenance sentences gain the mass-item and NOT-USED branches.
  **Delivered coordinates move**: `cessna_210`'s h-tail rises 86.0 → 100.0 in
  and `concept_heavy`'s drops 100.0 → 90.0 in (station points and exported
  `GRID`s only — the h-tail loads in `fz`, so no load moves); the Imperial
  baseline re-froze `cessna_210`'s three deck channels. Both moves are the
  note 54 gate-3 fixes, pinned in `tests/test_tail_geometry.py`.

- **The joint register: a joint is an owned location, a stated arm, a DOF set
  and a basis (#262, note 54 D-54.5/D-54.7, tier L, 2026-09-10).** Every
  inter-component tie in the LRA beam model now has its nodes placed by one
  owner, `sloads/joints.py` — the fin root→fuselage tie, the T-tail
  fin-tip↔h-tail-centreline pair, the conventional attachment pair, the wing
  side of body and the two spar posts. `joints(project)` resolves nothing
  itself: it reads the owners that already resolve each position
  (`tail_geometry`'s fin root and `h_tail_waterline`, `tail_span.htail_attachment`,
  `derived_geometry`'s `sob_station`/`carry_through`/`fuselage_lra`) and copies
  their location, ASSUMED/entered grade, basis and in-band note **verbatim**;
  `export/lra_model` places its nodes and raises its refusals by reading the
  register, so the two ends of a rigid tie can no longer be two spellings of one
  formula. **This corrects real geometry.** The R-6 tie hung the horizontal tail
  off the outermost fin *strip midpoint* rather than the fin tip: measured
  against the planform owners it spanned −23.228/−23.753/−20.876 in of x where
  the surfaces state −25.600/−26.100/−26.680 (5.80 in, −22 %, on
  `concept_regional_jet`), plus 6.25/6.5/6.9 in of `z` the airplane does not
  have — the arms note 51's D-51.2/D-51.3 transfer moments are computed across.
  The fin chain now runs **root → strips → tip** (`lra-fin-tip`), and the h-tail
  centreline and conventional attachment nodes are placed at their own LRA
  stations instead of being interpolated off the strip polyline (which put
  `ga6_normal`'s attachment pair 0.356 in off the body station it reacts
  against). D-54.7's drift guard (`tests/test_joints.py`) walks every joint of
  every fixture out of the **emitted deck text** and asserts the node is where
  the register put it, that a tie exists, that it constrains the stated DOF set,
  and that it spans the stated arm. No delivered load moves: of 330 baseline
  channels only `sbeam/lra_model` changed, on five of six fixtures, and the
  per-subcase deck resultant is unchanged (LM-1 preserves it wherever the nodes
  sit). Alongside it, `wing_geometry.chord_fraction_x` becomes the single owner
  of the chord-fraction line, which `TailPlanform.x_at` and
  `net_loads.to_loads_ref_axis` had each spelled out separately.

- **Every exported LRA deck solves, and the solve gate covers every fixture
  (#172, design note 55 D-55.1…D-55.6, tier L, 2026-09-10).** The mission claim
  is that the exported deck solves in sbeam with verified global equilibrium;
  it was demonstrated on two of six shipped fixtures, and the CLI exported the
  other four without a word. Three defects, all in **how a joint node joins the
  structure** — the sibling of note 54's *where a joint node sits*:
  **(1)** a body tie could parent on a node that was already an `RBE2`
  dependent, so `ga6_normal` stated `gear → rear-spar post → hub` as a chain of
  rigid elements, which sbeam refuses outright; the tie parent now takes the
  same not-already-a-dependent rule the support picker had carried since the
  model shipped. **(2)** A joint inserted near an existing strip station left a
  **sliver element** — `cessna_210`'s h-tail attachment landed 0.0769 in from a
  station (1.07 % of that chain's `ds`) for a 1638:1 element-length ratio and
  the singular solve the issue reported, with `baron_58` next at 0.1266 in /
  1.33 % and in no gate to say so. A station that close is now absorbed
  **into** the joint, which keeps the register's owned location (note 54
  D-54.5 is not negotiable) while the merged node keeps the station's `GID`, so
  its load routes there unchanged under LM-1. The governing tolerance is
  `JOINT_MERGE_FRACTION` — a fraction of the chain's own strip width, because
  "is this the same station" is a geometric question and had been answered by a
  1e-6 float-equality epsilon. **(3)** The support picker excluded `RBE2`
  dependents but not independents, although `roundtrip._supportable` applies
  both and documents why: `recover_reactions` never subtracts a load a rigid
  element transfers *onto* a constrained node, so it returns as reaction —
  measured at **569.49 lb** of Fx on `ga6_normal` against an applied set closing
  to 0.0002 lb. All three are now gated invariants, and a skeleton that still
  violates one is an `LraRefusal` naming it rather than a deck that dies in the
  user's solver. The solve gate widens from the two fixtures that passed to
  **every CLI-exportable fixture**: all six now solve in Imperial, with
  `concept_regional_jet` and `ga6_normal` remaining strict `xfail` in SI only on
  sbeam's pre-existing dense-path condition heuristic. No delivered load moves;
  `sbeam/lra_model` bytes move on `ga6_normal`, `baron_58` and `cessna_210`.

- **A machine rating in load units is no longer a load (#170, review R-8, tier M, 2026-09-09).**
  `units.is_load_unit` decided what a safety factor may be stated for by testing the
  **unit string alone**, so an engine's own torque rating read as a structural load:
  ENGLOADS published GA-6's mean takeoff torque as 554.4 ft-lb and the ULTIMATE channel
  stated it as 831.6, a number with no meaning — 14 CFR 23.303's factor belongs to the
  *design* torque the same condition publishes beside it, not to a powerplant rating.
  `units.NON_LOAD_QUANTITIES` is now the owner of that distinction, and the producer has
  the last word: `"mass"` (unchanged), plus `"characteristic"` for an engine rating and
  `"diagnostic"` for `balance`'s pre-closure residual. Five quantities across two modules
  leave the class — `mean_takeoff_torque` (23.361(a)(1) and the turboprop (a)(3)),
  `max_continuous_torque` (23.361(a)(2)), `max_accelerating_torque` (25.361(a)(3)(ii)),
  `balanced_residual_fz` and `balanced_residual_my` — each losing its `SF` cell and its
  `-ULT` eligibility while the `mx_mount_torque`, the gyroscopic couples and the applied
  loads of the same conditions keep both. The class was swept, not the filed row: review
  R-8 found it three rows wide on the engine side and two more in the balance residuals.
  No load value changes anywhere. `CONVENTIONS.md`'s "Loads only" rule names the
  vocabulary; guards in `tests/test_safety_factors.py` pin the discrimination both ways on
  every fixture, assert every key of the class is actually reached, reject a `quantity`
  hint outside the owner's vocabulary, and check the delivered row itself — the rating's
  `SF` cell empty, the mount torque's filled, in one condition.
  The frozen Imperial baseline was regenerated deliberately and moved in **6 of 330**
  digests — `csv/balance` on each example, the 176 pre-closure residual rows whose `SF`
  cell is now blank like the percentage rows beside them; the 104 applied-load rows of the
  same files keep `1.5`, and no deck, report or load-case CSV byte moved.

- **A raked fin root no longer kinks the loads reference axis (#219, design
  note 54 D-54.3, tier M, 2026-09-09).** Where a surface's edge polylines do
  not cover the same span, the chord keeps the closed-polygon clamp
  (`wing_geometry.planform_boundary` — the 8 % GA6 area over-read stands
  fixed), but a chord-fraction *line* — the LRA, the 25/50 % load points, the
  hinge — is now evaluated on the edges' own slopes (`TailPlanform.x_at`)
  instead of pointwise on the collapsing closure chord, which swung the GA6
  fin's LRA 33.5 in aft onto the trailing-edge root point over the last 5.5 in
  of span (Figure 24's kink). The GA6 fin axis is now one straight line root
  to tip (gate: slope constant to 1e-9); surfaces whose edges cover the same
  span are byte-unchanged. **Delivered numbers move on `ga6_normal` only**
  (the one raked fixture): the fin's load application stations in the raked
  region shift forward, so the lateral cases' yaw acceleration falls 0.6–2.9 %
  (p_dot ~0.1 % through the Ixz coupling) — fin loads and Ny bit-identical,
  the lever-arm-moved diagnostic — and the GA6 tail/balance CSVs and decks
  re-baseline with it. Rule-4 ride-alongs: `interp_x` extrapolates the
  *nearest* segment below range as its docstring always promised (it used the
  last segment's slope — the wrong end of the surface), and the dead clamped
  copy `tail_geometry._interp` is removed.

- **The shipped text stops naming the export package note 56 deleted (#274, tier
  S, 2026-09-12).** D-56.2 deleted the five per-component decks and D-56.8
  unshipped the assembled one, and the sweep that closed note 56 reached the
  standard docs but stopped short of the rendered strings — so the actively-used
  deliverable went on describing artifacts the package no longer builds. Seven
  statements a reader actually sees were false: the oracle report's §7 paragraph
  called the assembled model *"this deliverable's primary load output"* and the
  per-component decks *"analysis views cut out of this model"*; its wing-root
  note attributed the `lra-sob` tagged reporting node to *"the wing stick deck"*
  when `export/lra_model.py` writes that tag at GID 25001; its gear section and
  the Landing Loads page both sourced the reference-point reaction to *"the
  assembled deck"*; the Balanced Cases page repeated the first two claims in its
  caption; the Export page offered *"FORCE/MOMENT cards (and the wing stick
  model)"* and pointed the `MyyAxis` column at a span CSV that is gone; and the
  Configuration & Layout side-of-body help named the stick deck as the reporting
  node's consumer. Each is re-cut onto what the bundle carries — the LRA beam
  model as the solver artifact, the assembled set as the internal reference
  resultant its transfer is gated against — with the free-free equilibrium
  argument (G-OR-72) unchanged: it was always a claim about the model, never
  about which file it shipped in.

- **The same sweep runs through the deck's own header and the docstrings behind
  it (#274, tier S, 2026-09-12).** The LRA model's `$` header told its reader
  that *"the assembled balanced deck remains the equilibrium proof and the
  per-component decks the oracle views"* — text inside the one deck that ships —
  and its per-case and constraint comments sourced the residual to a deck no one
  receives; all three now name the model that carries them. Present-tense
  docstrings naming the deleted decks are corrected in `export/lra_model.py`,
  `export/bands.py`, `report/applied.py`, `report/tables.py`, `report/render.py`,
  `report/oracle_sections.py`, `modules/balance.py` (whose copy of the
  free-body-cut rule now points at `CONVENTIONS.md`, which retired it in place)
  and `app/views/loads_plots.py`. Only `sbeam/lra_model` moves in the Imperial
  baseline, on the four fixtures that build one, and only in `$` lines: every
  edit sits inside a `comment()` argument, which emits nothing else. **One thing
  is deliberately not fixed:** the case index still ships the headers
  `LOAD/SUBCASE (component)` and `LOAD/SUBCASE (assembled)`, naming two decks
  that no longer exist. Renaming them moves a shipped CSV header across three
  owners and is **#209**'s decision, not this sweep's, so `report/tables.py`
  states the mismatch where the columns are defined rather than leaving the next
  reader to infer it.

### Removed

- **Six dead public names leave `sloads/`, and a gate keeps the seventh from
  arriving (#16 / CH-5, tier S, 2026-09-11).** `balanced_deck.write_balanced_deck`,
  `mass_cards.write_conm2_fragment`, `mass_cards.write_mass_check_deck` and
  `mass_distribution.all_checks` — the four the 2026-08-16 scope review named,
  re-verified on this tree as definition-plus-`__all__` and nothing else — are
  deleted. Under rule 4 the sweep took the same class across the tree and found
  two more with no consumer *anywhere*: `report.tables.write_safety_factors_csv`,
  a fifth instance of the identical `write_X(project, path)`-wrapping-`X(project)`
  shape, orphaned when note 56 D-56.1 moved the report tables out of the export
  bridge, and `field_registry.paths_for_page`. New guard
  `tests/test_no_orphan_writers.py` fails when any `write_*` in `sloads/` has no
  caller in the calc package, either shell, the scripts, the CLI entry points or
  the suite — proven against a reintroduced orphan before it was removed.

  **The "demote the ~12 no-consumer public names" half does not ship, and the
  number is why.** Re-measured on this tree, `sloads/` carries **200** public
  top-level names with no consumer outside their own module, not twelve — and
  the review's own two examples have both evaporated: `gear_loads.contact_patch`
  gained an external consumer since 2026-08-16, and `sbeam_bridge.subcase_map`
  sits in the file note 56 D-56.1 dissolves, so demoting it is churn on a
  deletion. The 200 are dominated by module result dataclasses (`DesignSpeeds`,
  `MassCheck`, `Joint`) and single-source constant families whose members are
  public by declaration — the `MASS_EID_*` id bands, `WING_BAND_*`, and the
  encoded-but-dormant commuter tier that `GUI_design.md` documents as dormant
  and a blind sweep would have deleted. Demoting those would fight rule 3, not
  serve it. The mechanical part of the row shipped with a gate; the judgment
  part is closed **decided, not done**, with the measurement above as the record.

- **`cessna_210` and `dhc8_dash8` retire from the bundled example set (#264,
  tier M, 2026-09-11).** Owner ruling from the 2026-09-10 scope-reduction
  review: GA-single (`ga6_normal`), closure-locked-twin (`baron_58`) and
  ATR42-class (`atr42_100`) coverage is sufficient, with the two concept
  configurations kept; the two fixtures move to unmaintained parking outside
  the repository (recoverable from history at the `v0.8.2` tag). Full retire:
  both leave every CI matrix, parametrized fixture list, pinned baseline and
  sbeam digest (the Imperial baseline drops from six fixtures to four with
  **every surviving digest byte-identical**); fixture-specific tests re-pin to
  a surviving fixture or to a constructed case (the below-energy landing
  caution, the gear-carrier mistag guard, the no-balanced-case deck refusal);
  the GUI example listings, `README.md`, `GUI_USER_GUIDE.md`,
  `PROJECT_GUIDE.md` and `PROGRAM_SPEC.md` state the surviving five. The
  unfixable `cessna_210` engine/prop CG waterline defect (filed 2026-09-07,
  no printed page to correct it from) closes parked-with-fixture, and #216's
  `cessna_210` half goes with it.

- **The five per-component solver decks are deleted (note 56 D-56.2, tier L,
  2026-09-11).** The wing stick BDF and its span-load CSV, the fuselage FORCE
  deck with its span-load and fitting CSVs, the chordwise tail deck and CSV, the
  two spanwise empennage decks and CSVs, and the control-surface deck and CSV —
  every per-component structural model sloads shipped. They were four parallel
  model concepts sharing one ID space with the deliverable, none of them the
  deliverable, and the deliverable was borrowing its GIDs from them.

  **What ships is unchanged**: the full-span balanced free-free airplane deck,
  the LRA beam model, the CONM2 mass model, the gear interface report, the
  oracle report and the per-component **applied load sets** — the record of what
  is applied, where, for which case, at what factor, which is what every deleted
  deck was written from. `sbeam_bridge.py` 2,639 → **1,413** lines; `sloads/`
  and `tests/` together lose ~3,800.

  `EXPORT_TARGETS` goes **ten to four** — `balanced`, `gear`, `lra`, `mass` —
  and there is no default target any more (`wing` was the default because it was
  the first thing the bridge could write). The note's summary says two; `gear`
  survives because D-56.1 reclassified the gear report as a *document*, and
  `balanced` because demoting the balanced deck turns on whether `roundtrip.py`
  collapses, which is still open (note 56 §8). Dropping either on a count would
  remove a live deliverable ahead of its replacement.

  **Three standing limitations retire** rather than reword: `centerline-clamp`,
  `flight-only-body-deck` and `export-case-filter`. Each described a limitation
  of a per-component view and pointed the reader at the assembled deck, which is
  now the only view there is. Retiring a caveat is the one edit that can quietly
  widen a claim, so all three go in the same commit as the deletion, against the
  pinned key set in `tests/test_methods_stamp.py`.

  The GUI loses the per-page deck downloads on the wing, fuselage, aileron, flap
  and tab pages and ten rows from the Export page and the bundle manifest. The
  band registry retires `tail-chord-htail`, `tail-chord-vtail`,
  `control-surface` and the `stick-element` EID block, leaving their ranges
  **unregistered rather than reused** — a published map said what lived there,
  and D-56.3's renumber is where the holes close.

- **The round-trip stick-model wrapper retires with the last elementless deck
  (note 56 §8, tier L, 2026-09-12).** `sloads/export/roundtrip.py` 529 → **186**
  lines. `wrap_as_stick_model` read a deck's `GRID` cards and **invented** a tree
  of `CBAR`s, a `MAT1`/`PBAR` section, a determinate support and a case control,
  so that a load set on a node cloud could be handed to a linear static solve at
  all. D-56.2 deleted the per-component decks and D-56.8 unshipped the assembled
  one; the LRA beam model writes its own elements and its own support, so it goes
  to the solver exactly as it ships. Retired with the wrapper: `Support`,
  `Topology`, the property / element / constraint / case-control builders, the
  coincident-node collapse, the `roundtrip-rbe2` EID band and three wrapper unit
  tests. What is left is what was always the point — hand a deck to sbeam and
  read back what it says.
- **Two names moved to the owner that allocates them.** `_orientation` becomes
  `deck_format.orientation_vector`: `lra_model`, the one deck writer left, was
  importing a private name out of a test harness to build its bars. `SPC_SID`
  becomes `deck_format.SPC_SID` and both writers now read it — the harness held
  the constant while the two writers each spelled `1` into an f-string, so the
  band registry's declared owner was not the code that allocates the id.
