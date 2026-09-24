  # Changelog

All notable changes to **sloads** (the FAR 23 LOADS replication and
initial-concept distributed-loads tool) are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Live cycle only.** This file holds `[Unreleased]` plus the two newest release
blocks; older ones roll into frozen, do-not-edit archives at a cut (note 61
CV-5): 0.8.3 is in [`CHANGELOG_to_0.8.3.md`](CHANGELOG_to_0.8.3.md), 0.8.2 and
everything before it in [`CHANGELOG_to_0.8.2.md`](CHANGELOG_to_0.8.2.md).

---

## [Unreleased]

## [0.8.6] — 2026-09-23

### Changed

- **The ATR 42 fixture is reconciled end to end from the published 42-300 data, so the concept turboprop demonstrates the suite on an airplane whose inputs agree with each other (#260, tier M, 2026-09-21).**

- **A closure load lands on the member that carries its mass, so a symmetric landing loads the deck's two main-gear grids identically (#293, tier M, 2026-09-21).**

- **Every delivered cell prints at the precision its unit prescribes, so a 13,360 lb load reads `13360` beside its neighbours instead of `1.336e+04` (#161, design note 65, tier M, 2026-09-21).**

- **The fuselage critical set publishes each quantity under one key and one label, so the report reads a single key per column and folds nothing (#222, tier M, 2026-09-20).**

- **The GA6 fixture balances at Appendix A's three altitudes, so every delivered case states the altitude the manual states (#164, tier M, 2026-09-20).**

- **The case's loading is entered on the case: the Payload Cases group edits it, the Mass cases table and the Wing Loads page's WING parts read it (#290, design note 63 D-63.9, tier M, 2026-09-18)**

- **Step — The negative angle-of-attack wing slots and the load-factor-extreme pair, above SELECT.BAS (#288, design note 62 D-62.1…D-62.8, tier L, 2026-09-17)**

- **Step — One mass model: the case's loading is the mass state of every inertia load (#289, design note 63 D-63.1…D-63.4, D-63.6, D-63.8, D-63.10, D-63.11, tier L, 2026-09-17)**

- **The load-factor extremes reach the deck whatever mass state their bending twin moves to: D-62.8's coincidence rule runs once, on the delivered wing set, and the PNZ/NNZ tie is the balance's own band (#294, tier M, 2026-09-22).**

- **Step — The wing-to-body joint is one post, two body cantilevers, and nothing integrated through the box (#275, design note 64 D-64.1…D-64.9, tier L, 2026-09-21)**

- **Step — Each SELECT wing slot runs at every FLIGHT mass state and the net-governing run is the delivered case; MZFW seeds the zero-fuel cases with their loadings (#292, design note 63 D-63.5 and D-63.7, tier L, 2026-09-18)**

### Fixed

- **The LRA deck states the SELECT conditions it does not assemble (#284, tier S, 2026-09-20).**
  The assembler records every condition it drops through one owner, but the block
  that rendered the record lived in the assembled deck note 56 D-56.8 stopped
  shipping, and the LRA deck -- the one solver deck that ships -- wrote none: a
  sizing loop reading it was never told that a quarter of SELECT's set is absent
  (ATR 47 assembled / 28 recorded). The `$ CONDITIONS NOT ASSEMBLED` block now
  renders under the LRA deck's case map from the wording owner
  (`balance.skipped_block`, moved beside `SKIP_REASONS` so the shipping deck does
  not import it from the internal producer), derived when the caller supplies no
  record. The `out-of-family` reason no longer sends the reader to the
  per-component analyses D-56.2 deleted: it names the report and case index that
  carry the fuselage conditions, the report alone for the one-engine-out fin
  conditions, and states that none reaches a solver deck (#285 is the fin's
  return). Guard: `tests/test_lra_model.py::test_the_lra_deck_states_what_it_does_not_cover`
  holds deck block == record on every CLI-exportable fixture, on the derived,
  supplied and written paths. Statement only -- no load moved; the fourteen digest
  channels that carry the wording (balance txt, balanced_deck, lra_model)
  regenerated.

- **Every engine-mount condition states its own point of application (#210, tier S, 2026-09-22).**
  The 23.361(b)(1) sudden-stoppage torque, the 23.371(b) gyroscopic condition and
  the FAR 25 supplemental 25.371 case carried no `loc_*` values while the
  conditions beside them for the same engine did, and the render boundary filled
  the gap from the condition each followed (note 44 OR-193) -- the proper repair,
  the producer stating the point, waited on the 0.8.2 freeze of `modules/engine.py`.
  The producer states it now: one owner, `engine._applied_at`, emits the three
  values on all nine conditions at the engine's combined engine-plus-propeller CG,
  the point the six torque and side-load cases always stated; `render._running_locations`
  is the identity it was filed to become: a condition's own point or a blank,
  never a neighbour's -- the one-engine-out fin and rudder cases, which state
  no single point, stay blank as they always printed. A pure couple and a three-point condition each state one
  point, so each says what it means: the stoppage note records that a free couple
  about the thrust line takes the combined CG for indexing only; the two
  gyroscopic notes record that the stated point is where the vertical load acts,
  the couples are free, and the thrust acts on the thrust line at the propeller
  hub, offset by the CG-to-hub distance -- the moment a reader summing about the
  mount from the index would otherwise lose. Which beam-model grid takes the
  couple stays with #286. Gates: G-OR-138 rewritten as the producer's property
  (`tests/test_oracle_report_vn.py::test_every_engine_condition_states_its_own_point`,
  every condition at its engine's combined CG, no two engines sharing one, a
  pointless condition left blank rather than filled) plus
  `::test_the_pointless_conditions_say_what_their_point_means`. No load and no
  point moved on any fixture; the one digest channel that moved is the engine
  text report (`txt/engine`, ATR 42), which now prints the three point rows and
  the note on each formerly pointless condition, and it is regenerated.

- **`concept_heavy`'s drag polar re-entered with its minimum at the wing's zero-alpha lift coefficient (#291, tier S, 2026-09-20).**
  The fixture's `CD = 0.025 + 0.05·CL²` had its minimum at `CL = 0` on a wing whose
  lift fit reads `CL = 0.3` at zero alpha, so at negative CL the airplane-less-tail
  polar under-read the drag and the non-wing axial force came out forward inside the
  polar's trusted window on the NMAA case note 62 narrowed to the VC pair (dCD
  +0.0169, note 62 §8.3). Re-entered as `CD = 0.0295 − 0.03·CL + 0.05·CL²`, the same
  quadratic with its minimum moved, NMAA reads −0.0039 and every heavy case inside
  the window is negative, so `tests/test_balance.py::_DELTA_CD_FORWARD_INSIDE_WINDOW`
  is empty again; the heavy's dCD band, clamp ceilings and residual ratchets are
  re-pinned with the cause stated (symmetric force worst 1.99 % → 1.21 %, pitch
  0.84 % → 0.52 %; NHAA still clamps outside the window). Fixture data only, no
  physics or schema change; the heavy's sixteen digest channels regenerated.

- **The v67 migration keeps a converted centreline wing mass as a point mass** (tier S, 2026-09-23, #296, 0.8.6 pre-cut review) — `_hop_66` stamped every item row's `carriage` *after* converting an open-tie `wing_mass.concentrated` list, so an entry at y = 0 (one doubled WING row, tagged POINT by the conversion) was re-typed PANEL by the *point iff wing and y ≠ 0* rule: the mass left the point list, WINGINER integrated it into the panel, and a spurious `panel_weight_override_lb` was written with a misleading note. The stamp now runs over the rows the file already holds, before the conversion; the centreline case joins the migration test beside the ±y one.

- **The LRA exporter refuses a wing station its spars do not bracket by name** (tier S, 2026-09-23, #297, 0.8.6 pre-cut review) — `build_lra_model` looked the wing post up in the joint register unguarded, so a project whose side-of-body station lies outside its front/rear spar stations died with a bare `KeyError` ("0 joints match 'wing_post'"): not a `ValueError`, it escaped the importer's position check, the report's lumping handler and the CLI error contract, while the calc side (note 64 gate 9) already refused with the register's own sentence naming the three stations. The exporter now raises `LraRefusal` with that same sentence, like every other missing-datum path, and gate 9 asserts the exporter carries the register's wording the calc side already ends with.

- **The methods-stamp guard reads the register's `ships with` marker** (tier S, 2026-09-23, folded into #296) — the note 52 amendment (d3b75d4) registered the 23.349(a)(2) 75 % correction ahead of its implementation (#306), and `test_statement_lists_every_approved_correction` demanded it in `report/methods.APPROVED_CORRECTIONS` at once, which would have stamped every CSV, deck and report with a deviation the delivered numbers do not carry. The register's policy now defines `ships with <note/issue>` in a heading suffix as approved-but-pending; the guard requires such an entry to be *absent* from the statement until the implementing step drops the marker and declares it in the same change.

- **The live corpus states shipped 0.8.6, and a tier-M closure can no longer leave its note at AGREED** (tier S, 2026-09-23, #299, 0.8.6 pre-cut review) — note 65's header read `AGREED` three days after #161 shipped it, because `tests/test_doc_currency.py` read the note a fragment ships only from a tier-L `## Step` heading; it now also reads the tier-M bold lead's parenthetical (`(#290, design note 63 D-63.9, tier M, …)`, the form `changes/README.md` states), note 65 says SHIPPED with its §7b amendments (D-65.3 one-figure floor, D-65.2's `int`, D-65.5 at #298) named in the header and a pointer under D-65.3. Six tier-M fragments opened with a bare `**` and would have rolled into the record un-bulleted: prefixed, and `scripts/build_changelog.py` now refuses a bare `**` that is not the tier-L `**Step` form. The statements shipped code had moved past are corrected in place: `theory_sources.md`'s body closure row and theory chapter 6's method section state note 64's two cantilevers, the one wing reaction and the fitting pair (the nose-to-tail integration, M4-1's linear carry-through distribution and `closure_artifact` are gone from the live corpus; chapter 10 and the twin walkthrough swept with them); the wing-loads guide teaches the derived panel and the loading's `POINT` wing parts, not an entered panel and a concentrated list; the fuselage-loads guide teaches the two cantilevers and the fitting loads, not the carry-through peak; the FAR 25 gap row for 25.343 rests on per-tank fuel and the MZFW seeds (note 63 D-63.4/D-63.5) with the reserve-fuel case named as what remains; the index rows for notes 62, 63 and 65 describe the shipped scope (D-62.8's PNZ/NNZ pair, D-63.11's run key, the one-figure floor and the #298 SI rule).

- **An SI cell resolves no coarser than the Imperial cell it converted from** (tier S, 2026-09-23, #298, 0.8.6 pre-cut review) — the SI precision rows copied the Imperial decimal count on the premise that every SI unit is "finer than, or within a factor of 2.2 of" its source (note 65 D-65.5), which held for N, mm and kPa and failed for area (ft² → m² 10.8×), moment (lb-in → N·m 8.9×), inertia (lb-in² → kg·m² 3418×) and wing loading (lb/ft² → kN/m² 20.9×): a 31.2 ft² tail printed as `3` m² (−3.4 %) and an inertia to one or two significant figures, and the report's own `Units` passed the Imperial label as the precision key whatever system it printed in. The SI row is now the Imperial row plus one decimal per decade the conversion factor divides by (`units.si_decimals`, the one owner; `kg`, `N·m`, `kW` gain one decimal, `m/s` two, `kg·m²`, `kN/m²` and `m²` four — the wing geometry emits its areas in `in^2` under the label the tail's `ft^2` shares — while `N`, `mm`, `kPa` keep theirs), the report keys precision on the document's own label, and the gate that asserted SI row == Imperial row now derives each label's need from the units the shipped fixtures and the report actually convert and asserts the row equals it; note 65 §7b records the amendment.

## [0.8.5] — 2026-09-16

### Added

- **Benchmark-first gets its presence guard (#186, review R-16, tier S, 2026-09-15).**
  `CLAUDE.md` rule 2 makes an oracle test (±0.1 %, page-cited) or a stated
  physics-closure gate the definition of done for every module, and until now
  nothing asserted a registered module *had* one: a module could register, run in
  the front end and ship with no gate at all while the suite stayed green.
  `tests/module_gates.py` is the manifest — one row per registered module giving
  its kind (`ORACLE` / `CLOSURE`), its gate test functions and either the printed
  source or the invariant it closes on — and `tests/test_module_gates.py` walks
  `registry.available()` against it. Six ways to fail, each verified to bite: a
  module that registers without a row, a row whose module stopped registering, a
  gate naming a test that no longer exists, an oracle whose cited page appears
  nowhere in its test file, a closure that states no invariant or whose test file
  stops saying why no printed oracle exists, and an unknown kind. All 23 modules
  are covered — 18 oracle-locked against Appendix A (or Ch 9's hand-calc, which
  is BALLOADS' only printed figure), 5 closure-locked because no printed figure
  exists for them: `balance`, `body_loads`, `configuration`, `one_engine_out` and
  `tail_span`. `20_theory/00_theory_sources.md`'s Oracle-status section stays
  normative and now names its machine-readable half, which a guard holds in place.

### Changed

- **Band B6 re-cut as 0.8.5 opens: four rows pulled forward from 0.9.0, two
  label drifts corrected, the beam-model page filed (tier S, 2026-09-14).**
  #272, #257, #280 and #210 move from band B2 into B6 under rule 6 and the
  band's own charter — the first two are shipped statements that are wrong or
  missing, #280 is the backlog tool this milestone runs at every closure, and
  #210 was stranded on a freeze that lifted at 0.8.2. #282 gains its band label
  and its row, #191 its tier, kind and tag labels. #283 files the beam-model
  page to 0.9.0 with the ruling that the report package does not carry the
  deck. The priority table is renumbered densely, Pri 1–40.

- **Band B6 split into four milestones: 0.8.5 correctness and tooling, 0.8.6
  the baseline wave, 0.8.7 report polish, 0.8.8 the LRA mesh rule with the
  beam-model page (tier S, 2026-09-14).** The same twenty-five rows, cut by
  what each touches so the two owner decisions gate only the milestone that
  consumes them and each cut's baseline regeneration is paid once. B7 takes
  #164, #222, #260, #161 and #210; B8 takes #243, #240, #256, #258 and #276;
  B9 pairs #275 with #283, pulled forward from 0.9.0, so the D-56.4 amendment
  and the page's note are one design pass. Milestones 0.8.6–0.8.8 and labels
  `band:B7`–`band:B9` created; the table renumbered densely, Pri 1–40.

- **Band B7 (0.8.6) re-cut against an ATR-class aircraft sized from the LRA
  deck: three issues filed, #275 pulled forward, the table renumbered (tier S,
  2026-09-16).** The review measured the band's five rows against a new
  ATR-class project delivering the free-free deck and found the gaps outside
  it. **#284** (B7, tier S): the one deck that ships states nothing about the
  SELECT conditions it does not assemble — 28 on the ATR, 24 on GA6, 0 stated
  — and the reason it would give names the per-component decks note 56
  deleted. **#285** (B2, tier L): the one-engine-out fin conditions reach no
  shipped deck since that deletion. **#286** (B2, tier L): no engine-mount
  case reaches the LRA deck, promoted from nine days in *Open defects* without
  a number. **#275** moves B9 → B7 with its milestone and label: the
  carry-through mesh defect is largest on the high-wing fuselage the review
  ran against, and a deck row outranks the two report rows it now precedes.
  #260 gains E6 — the ATR fixture enters one wing case, reaching WINGINER and
  the report but not the deck, whose six come from SELECT. Renumbered densely,
  Pri 1–29; `backlog_issues.py check` green.

- **The backlog tool stops throwing away a defect's body: a defect folds into a table row only on an explicit pin, and no bullet with a body is collapsed onto another item's issue number (#280, tier M, 2026-09-15)**

- **`modules/balance.py` is the `modules/balance/` package: eight files on the
  banners the single file already carried (#191, review R-23, tier S,
  2026-09-15).** 2,845 lines — the file where every full-airplane change lands —
  split by pure moves along its own section boundaries: `constants.py` (which
  conditions assemble, the two residual acceptances, the stated notes),
  `lateral.py` (the L-7 wing-body sideslip terms, owner of the `body-aero`
  source), `skipped.py` (the F-C7 record), `applied.py` (the applied sets),
  `queries.py` (what a case *is* — handedness, the residual-gate family,
  lateral/ground/powered), `closure.py` (resultants and the six-DOF closure),
  `air.py` (assembly, the handed twin, the case set) and `ground.py` (the ground
  families). The subsystem's own explanation — the three things that had to be
  got right, the seam rule, the lateral and unsymmetrical-tail sections — stays
  whole as the package docstring. No behavior moved with the code: the existing
  oracle and closure gates are the guard, and `build_balanced_cases` returns the
  same cases in the same order, so no deck's subcase sequence changes.
  **The split is invisible to consumers.** 42 names are imported from
  `sloads.modules.balance` across `sloads/`, `tests/` and `export/`, and 11 more
  are reached as `balance.X`; `__init__.py` re-exports every one of them, so not
  a single import line elsewhere changed. `air` and `ground` import each other —
  one assembly machinery, two sources of case — and the cycle is deferred at the
  single call in `build_balanced_cases` rather than broken by moving the twins
  somewhere neither family owns. `skipped_conditions`, a facade that re-runs
  assembly, sits with `run()` in `__init__.py` so the record type does not point
  at the assembly that produces it.
  **The prose that named the file was swept with it** (practice 4): eight SSOT
  owner cells in `CONVENTIONS.md` §7 now name the file inside the package that
  owns the convention, `PROJECT_GUIDE.md` §4's tree lists all eight (its guard
  fails both ways), and `PROGRAM_SPEC.md`, `ch09_balanced_airplane.md`,
  `02_approved_corrections.md` and fourteen design notes were re-pointed —
  including three markdown links into `sloads/modules/balance.py` that would
  have failed `test_doc_links.py`. Twelve `balance.py:NNN` citations lost their
  line numbers rather than gaining new ones: a line number into a 2,845-line
  file was never stable, and three of the twelve had already drifted off the
  statement they cited.
  **Three tools assumed a module was one file, and the sweep fixed all three**
  (practice 4): `test_workflow.py`'s slice sweep read `modules/<name>.py` and so
  saw a split module read nothing at all, `docs/generate_data_dict.py` attributed
  consumers by globbing `modules/*.py`, and `test_deliverable_units.py`'s
  conversion-at-the-boundary guard listed that directory flat — the first two
  failed loudly, the third would have gone on passing while silently no longer
  covering the largest module in the tree. Each now resolves a module to its file
  *or* its package.

- **The governing safety-factor table reaches its "flagged, never defaulted" promise by one path: an exact-reference row classifies the one reference it names instead of returning outright, and a section number the classifier reads must be one a family can place (#179, tier M, 2026-09-15)**

- **Every reconciliation between the suite's two mass models is stated in the issued document, gated by name and by effect (#257, tier M, 2026-09-16)**

- **No reader on the delivery side defaults a safety factor: the five dedicated load carriers read theirs through `export.deck_format.case_sf`, a condition's is read off the condition and may be `None`, and every SF cell is rendered by `report.render.sf_cell`, which prints `N/A` where the governing table prescribed nothing (#180, tier M, 2026-09-15)**

- **Every runner the registry hands out stamps: `register` stores the module's `run` wrapped in the project's governing safety-factor table, so a result that has not been past the table is not something a caller can obtain (#177, tier M, 2026-09-15)**

- **Every section of the oracle report reads SELECT's critical set through its one owner, gated by name and by effect (#272, tier M, 2026-09-16)**

- **One owner per issue-package filename, and G-12's inertia notes reach the delivered file (#273, tier M, 2026-09-14)**

- **A red sbeam-drift run files an issue, not just a red square (#188, review R-18, tier S, 2026-09-15).**
  The weekly `sbeam drift` workflow runs the round-trip gate against sbeam `main`
  rather than the pinned commit, `continue-on-error` throughout — but its result
  was delivered only on the Actions page, which nothing requires anyone to open,
  so drift could sit unread indefinitely. It now opens one **pinned drift issue**
  on the first red run, comments on it on every red run after that, and
  comments-then-closes it on the first run that is green again, so an open issue
  means *drifting now* and the signal leaves the board the same way it arrived. A
  gate that never ran (setup failed) moves nothing: closing a live drift report on
  the strength of a test that did not execute is the one wrong answer available.
  The wiring is guarded by `tests/test_sbeam_drift_notification.py`, which holds
  the three details that delete cleanly and fail silently — the gate step's
  *step-level* `continue-on-error` (without it a red gate skips the very step that
  reports it), the `steps.<id>.outcome` key (`failure()` can never be true for a
  step that continues on error), and the single spelling of the issue title that
  is both search key and created title, whose drift would open a fresh issue every
  Monday. `PROJECT_GUIDE.md`'s sbeam-pin procedure now says where the notice
  arrives.

- **Every `test_structural_speeds` assertion holds at ±0.1 %, or says on its own
  line why it cannot (#175, review R-4, tier S, 2026-09-15).** Five assertions sat
  at 2e-3…1e-2 in a file headed "matched within ±0.1 % per Decision 3", with
  nothing recording whether the width was a rounding limit or an unexamined
  disagreement — a passing assertion keeps no margin, so the reason is not
  recoverable afterwards. Three were simply loose and now hold at `TOL`: the GA6
  wing loading (1.7e-4 — the manual's hand area 2·13257/144 = 184.125 against
  WINGGEOM's polygon 184.157), VC(min) 141.8 kt (3.9e-5) and the regional jet's
  Mach margin 0.09728 (9.7e-5). MC/MD at the 12 000 ft shoulder are genuinely
  rounding-limited — the manual prints three decimals, so ±0.0005 is ±0.15 % at
  MC 0.323 and ±0.1 % is finer than the oracle resolves — and are now asserted as
  agreement *to the printed precision* (`round(value, 3) == 0.323`), which is both
  tighter than the 3e-3 band it replaces and self-explaining. The file's docstring
  states the rule for the next assertion added to it.

- **Every shipped control surface is drawn over the area its loads were run on: the two estimated aileron polylines are reconciled to their entered areas, and the report's disagreement statement now has nothing to say on any shipped airplane (#216, tier M, 2026-09-16)**

- **The user guide is a gated channel: G-OR-74 walks `docs/60_guide/` as prose, and the sixteen sentences that still taught the pre-OR-116 contract are corrected (#282, tier M, 2026-09-15)**

- **The oracle report's non-conventional-tail withholding says what the calc actually did, per arrangement, and is gated against it (#254, tier M, 2026-09-16)**

### Fixed

- **The GUI journey carries its session through Streamlit's public tester API, and every reach past it is now declared (tier S, 2026-09-16).**
  `AppTest.session_state` was the internal `SafeSessionState` through Streamlit
  1.63, and one line of `tests/test_gui_journey.py` read its private
  `filtered_state` property to carry widget state from page to page. 1.64 wrapped
  that object in a documented tester-facing one and moved the real state to
  `_session_state`; the reach stopped resolving and the wrapper's `__getattr__`
  reported it as a missing *key* — `AttributeError: filtered_state not found in
  session_state` — which is an API change wearing a state defect's error message.
  It failed all five fixtures on CI while the local gate stayed green, because a
  developer's venv is pinned by whatever was current when it was made and CI
  installs the newest release every run. The walk now calls the public
  `to_dict()` where it exists and falls back to the private property below 1.64,
  so it holds across the whole supported range (`streamlit>=1.51`, no ceiling);
  the carried view — user state and keyed widgets, internal keys excluded — is
  identical either way, and the journey passes on 1.58.0 and 1.64.0 alike.
  This is the unbounded-ceiling policy doing exactly what `pyproject.toml` says
  it is for, so the finding is that the warning was worth less than it should
  have been: a reach into internals turns an upstream-API alarm into noise about
  a key. `tests/test_ci_conformance.py` — which already owns the unpinned-install
  policy this rests on — now scans `tests/` for private Streamlit spellings and
  requires each one to be declared with its reason, with a companion that fails
  when a declaration outlives the reach it excused.

- **The 0.8.5 pre-cut review's three residues closed (tier S, 2026-09-16).**
  `report/lumping.CaseComparison.safety_factor` loses its `0.0` default — #180
  removed the read that defaulted to it and left the dataclass default that
  would print the same SF 0; `oracle_sections._beam_provenance` builds 4.1's
  two #257 reconciliation sentences once instead of twice; and the four
  tier-M history fragments written as bare paragraphs take the bullet form
  `changes/README.md` states, so the roll at the cut lands every tier-M entry
  in the record in one shape.

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
