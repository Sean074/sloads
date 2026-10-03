# Completed Development

The authoritative record of what has shipped: completed modules/phases, key
decisions, and resolved defects. Items move here from
[`../30_future/00_backlog.md`](../30_future/00_backlog.md) the moment they close,
with a matching `CHANGELOG.md` entry.

Each entry uses the step format: **Objective**, **Deliverables**, **Test /
Acceptance**, **Key decisions**.

**Live cycle only.** This file holds the current release cycle plus the previous
release cut. Older blocks roll into frozen, do-not-edit archives at each release
(`RELEASE_PROCESS.md` §4): the 0.8.6, 0.8.5 and 0.8.4 cycles with the 0.8.5,
0.8.4 and 0.8.3 cuts are in
[`67_completed_development_to_0.8.6.md`](67_completed_development_to_0.8.6.md),
the 0.8.3 cycle and the 0.8.2 cut in
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

## Release cut: **sloads 0.8.8** (the deck's delivered loads are right, and the user can reach them — the beam model in the GUI, the T-tail fin's asymmetry, the engine axial loads, refusals by name), tag `v0.8.8`, 2026-10-03

**Objective.** Close band **B9**, re-chartered on 2026-09-28 by the 0.8.8
planning review as *the deck's delivered loads are right, and the user can
reach them*. Three rows were the milestone: the beam model reaching the GUI
(#283 with #244, note 67), the T-tail fin carrying the horizontal tail's
asymmetry (#328, note 51) and the engine axial loads of both deck families
(#319, note 66 D-66.12a/D-66.4a). The rest were the refusal sweep that keeps a
NaN or a calc defect from shipping as a silent absence (#316, #330), the
residues of the 0.8.7 release review (#318–#322), the interpreter pin (#327),
the CI read in `solo_close.sh` (#329), and the polish that had waited behind
#283 (#240, #243, #256). The band emptied on 2026-10-02; the pre-release
review found two MAJOR (#341, #342), both closed on the branch before the
cut, and the owner split 0.9.0 by chartering **B10 (0.8.9)** for the
ATR-class correctness rows the review measured.

**Deliverables** (the `[0.8.8]` changelog section is the release note):
- **The beam model reaches the GUI (#283, #244, note 67, tier L).** A Beam
  Model page shows the axes, owns the mesh, draws it to scale and writes the
  deck with the operating empty weight's mass set beside it; a row counter is
  bounded everywhere.
- **A T-tail's fin carries the horizontal tail's asymmetry (#328, note 51,
  tier L).** The AC 23-9 induced rolling moment in every fin condition,
  one-engine-out included, and the 23.427 case through the fin.
- **The engine axial loads of both deck families (#319, note 66, tier L).**
  The one-engine-out hub carries the propeller's windmill drag when entered
  and the stated Glauert bound otherwise; every gyroscopic case applies every
  engine.
- **Refusals by name (#316, #330, #341, tier S/M).** A half-entered input is
  refused by name rather than raising a bare `ZeroDivisionError`; no handler
  in `sloads/` swallows a calc defect; a NaN or an infinity cannot reach a
  report section, a package file or a deck card.
- **Mass and envelope (#309, #312, #320, #321, tier M/S).** An envelope point
  no loading can produce is flagged; the calc package writes no digit count
  of its own; SELECT's roll pick is decided outside the balance tolerance.
- **Units, gates and tooling (#318, #322, #327, #329, #338, #342, tier S/M).**
  SI artifacts state every number in SI, their prose included; the note 66/52
  gates compare against independent figures; sloads requires Python 3.12 on
  every gate; `solo_close.sh` refuses a close while the branch's CI is red;
  the current-truth docs state the LIMIT basis the code ships.
- **Report polish (#240, #243, #256, tier S).**
- **Version** `0.8.7` → **`0.8.8`**. Schema **v70 → v73**: v71 at #319
  (`EngineInput.windmill_drag_cd`), v72 at #328 (`TipTransfer` gains `mxx`,
  `paired_case`, `induced`), v73 at #283 (`MassItem`'s usable-fuel tag), each
  with an identity hop. **`RELEASED_SCHEMAS` gains `"0.8.8": 73`**, frozen as
  `tests/fixtures_schema/release_0.8.8.json` (a copy of
  `examples/ga6_normal.project.json`).
- **Changelog cut** — `scripts/build_changelog.py 0.8.8 --date 2026-10-03`:
  **19 fragments** consumed — 11 into `## [0.8.8]` directly and **8 history
  entries** rolled to the top of this file, their changelog bullets derived
  from their leads — and a fresh empty `[Unreleased]` opened.
- **Record roll** (`RELEASE_PROCESS.md` §4 step 3): no note moves (note 61
  CV-3). This file stood at 611 lines before the cut and 923 after the
  fragments; the changelog at 1,139 and 1,415. Both are under 1,500; neither
  rolled.
- **Verification baseline** (§4 step 5): unchanged from the 0.8.7 cut —
  [`36_verification_baseline_0.7.0.md`](36_verification_baseline_0.7.0.md)
  plus the one 23.349(a)(2) correction registered at 0.8.7. No entry was added
  to `02_approved_corrections.md` this cycle, and every Appendix A assertion
  is the same test on the same printed number.
- **Gates at cut:** `pytest` **4,267 passed / 13 skipped / 2 xfailed / 0
  failed** (3,901 passed / 11 skipped / 2 xfailed at the 0.8.7 cut) on
  `c7a8ccf`, the tip before the cut commits; `ruff` clean, `mypy` clean
  (`sloads/`, 114 source files), `scripts/smoke_test.sh` **PASS**,
  `scripts/build_changelog.py --dry-run` clean,
  `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on 7 tracked keys,
  the §3.5 by-hand walk done by the owner (2026-10-03);
  the cut's own guards (migrations, doc currency, links, fragments, backlog,
  version owner) re-run green after the cut commits. Of the 0.8.8 pre-release
  review's findings, both MAJOR (#341, #342) closed on the branch; no
  CRITICAL or MAJOR is open, and its minors are filed — #343 and #344 in
  B10, #345 and #346 on milestone 0.9.0.

**Key decisions.** *A delivered load the user cannot reach is not
delivered.* The band was re-chartered on that sentence, and its first row put
the primary deliverable — the LRA beam model — on a page for the first time.
The second decision repeats the last two cuts': an emptied band is not a
release until a critical read of the whole branch says so. This one found two
MAJOR and closed both before the cut, with no round trip back into the band.
The third is the split: the review measured the open 0.9.0 work at twice the
§2 cadence, so its near-term correctness half became its own milestone (B10,
0.8.9) instead of a release that would have carried a month of unreleased
work.

---

## Step — The beam model reaches the GUI: a Beam Model page shows its axes, owns its mesh, draws it and writes the deck with the operating empty weight's mass set beside it, every drawing is drawn to scale, and a stray keystroke can no longer commit 4,501 rows (#283 with #244 riding, design note 67 D-67.1–D-67.12, tier L, 2026-10-01)

**Objective.** Close #283 and #244. The LRA free-free beam model is the primary deliverable, and the GUI had no route to it:

- the deck was written only by `cli.py --export-target lra`;
- the model was drawn only by `scripts/plot_lra_model.py`;
- note 57 D-57.6 had retired the export page without a port.

Measured first (note 67 §1):

- **The stamp was CLI-private.** It read the tool version from `importlib.metadata`, the install-time snapshot `sloads/_version.py` exists to replace.
- **The folder picker was private to the Report page.**
- **The axis and the mesh were already editable on Geometry.** The backlog row said otherwise.
- **"OEW" had no typed partition.** Four of five fixtures keep reserve fuel in `MINIMUM` with `consumable` False, by G-4's design.
- **#244's counter lived in `oracle_app/form.py`,** not in `app_shell`. Nothing bounded the mesh counts either.

**Deliverables.**
- **One owner each for the stamp, the names and the picker (D-67.6–D-67.8).**
  - `report.bundle_stamps` reads the version from `_version`.
  - `export/deliverables` holds the file names and the one render-then-write both routes take. `render_set` renders a whole set before `write_set` opens a file, and `write_lra_model_bdf` retires.
  - `app_shell/folder_picker.folder_picker` keeps one session key per page.
  - The stale "the BDF stamp is always ULTIMATE" prose in `cli.py` and `report.methods` is corrected.
- **The OEW mass set (D-67.9–D-67.11).**
  - `MassItem.usable_fuel` (schema v73, identity `_hop_72`). Mission and reserve fuel are usable; unusable fuel and oil are not, per 14 CFR 23.29(a).
  - `mass_distribution.oew_items`: `EMPTY` + `MINIMUM` less usable fuel.
  - `mass_cards.oew_fragment`: GRID + CONM2, no MASSSET. Its header names every `MINIMUM` row it kept and every fuel row it left out.
  - The CLI gains `--export-target oew`.
  - The five fixtures tag 13 rows. The ATR's OEW is 22,674 lb with both reserve tanks left out.
- **The drawing (D-67.4/D-67.5, amended in §10).**
  - `oracle_sections.beam_model_figures`: four views (iso, plan, side, front), drawn from `build_lra_model`, the deck's own builder.
  - The orthographic outlines come from `_airframe_series`, the engine views' owner. A refusal is stated verbatim in each view.
  - Catalogued on the `beam_model` page, and printed at the head of the oracle report's Appendix G, so note 60's parity holds.
  - The script, its test and `examples/*_lra_views.png` are deleted.
- **Drawings to scale (§10, owner-confirmed).**
  - `PlotData.to_scale` is stated by the producer, and both renderers read it.
  - Before, the screen derived it from "every series closed", and print never set it outside the four planform keys. The engine views, ground attitudes, tail LRA planforms and fuselage side view were drawn on free axes under captions saying "to scale on equal axes".
  - Seven producers set the flag.
  - A drawing's printed legend is offset in baselines, so a thin drawing's legend clears its axis label.
  - Unnamed series take no legend row on screen, as in print.
- **The page (D-67.1–D-67.3).**
  - `NON_STEP_PAGES` gains `beam_model`.
  - The axes are shown read-only by `lra_model.reference_axis_rows`, over the same `LRA_SURFACES` the exporter refuses on.
  - The four `lra_mesh` rows move from Geometry, rendered through `form.render_page_inputs`, which shares `render_step`'s group loop.
  - The write needs a named confirmation before replacing a file. The page catches the deck's own `ValueError`, not only `LraRefusal`.
  - The registry and figure-family guards widen from analysis steps to GUI pages.
- **The bounded count (D-67.12, #244).** `app_shell.components.count_input` covers every row counter and every `field_registry.COUNT_RULES` field:
  - rows are capped at 500, and mesh counts run 2–200 (`LRA_GRID_BOUNDS`, the exporter's own range);
  - an increase of more than 10 is held until its named button is pressed;
  - the widget re-seeds whenever the model moved underneath it;
  - a file carrying an out-of-range mesh count is refused by the exporter, naming the field.
- **Docs:**
  - `PROGRAM_SPEC.md`: the export menu (stale "default" and "Export page bundles" text removed), the Beam Model page, the `usable_fuel` consumer row, the mesh range.
  - `CONVENTIONS.md` §7: six owner rows.
  - `theory_sources.md`: the OEW definition.
  - `GUI_design.md` and `GUI_USER_GUIDE.md`.
  - The guide's getting-started, troubleshooting and where-next chapters.
  - `PROJECT_GUIDE.md` §4.
  - `DATA_DICTIONARY.md` and the guide's generated tables, regenerated.
- **Digests.** One new channel per example, `sbeam/oew_mass` (258 → 263). No existing channel moved. The oracle report has no digest channel.

**Test.**
- `tests/test_beam_model_page.py` (new):
  - gate 1: page and CLI byte-identical, four airplanes, both systems;
  - a refusal writes nothing and is stated verbatim on the page;
  - the file prefix rule and replace detection;
  - the page under AppTest: shipped airplane, blank project, write click;
  - one picker owner.
- `tests/test_bounded_count.py` (new), gate 9:
  - the cap, a held jump, a small step committing normally, the re-seed;
  - the mesh bounds equal the exporter's;
  - a blank mesh count's jump is measured from its default;
  - a file count of 1 or 4,501 is refused by name.
- `tests/test_figures.py`:
  - the beam model's plan view carries every CBAR, tie and owned node;
  - a refusal is stated verbatim;
  - both renderers honour `to_scale`, and a caption claiming "to scale" carries the flag;
  - G-FIG-1/3/6 walk GUI pages.
- `tests/test_mass_cards.py`: the fixture tags, the exact partition, one card per kept row, the header naming every `MINIMUM` row, an untagged reserve kept by name.
- `tests/test_sbeam_roundtrip.py`: GPWG recovers the OEW in both systems.
- `tests/test_migrations.py`: the v73 hop.
- `tests/test_cli.py`:
  - the `oew` target;
  - the CLI builds no stamp and spells no file name;
  - the stamp carries `_version`'s version.
- Re-cut:
  - `test_field_registry.py`: pages are GUI pages, and the mesh renders on the beam page alone.
  - `test_lra_model.py` and `test_deliverable_units.py`: the writer moved to `deliverables`.
  - `test_oracle_report.py`: picker keys.
  - `test_schema_guards.py`: the v73 hash.
  - `test_oracle_journey.py`: the harness clicks a held jump, as it clicks the #143 Add gestures.

**Key decisions.**
1. **A non-step page, not a fifth phase.** The model is the deliverable built from the analysis. Its page runs no `.BAS` program and fills no slice a computation reads, and `workflow.py` already said deliverables are not steps.
2. **The axis stays where its other consumer is.** `net_loads` and `tail_span` torsion read `ref_axis_pct`, so it is entered on Geometry and shown on the beam page. The mesh, which only the exporter reads, moved beside its own drawing.
3. **OEW is a typed partition, never a name match.** `consumable` already means "G-5 may burn it down", and reserve fuel is deliberately not consumable. Unusable fuel and oil stay in OEW on the regulation's own empty-weight definition.
4. **The report prints the beam model (owner ruling A).** This keeps note 60 D-60.1 whole, so the GUI shows no figure the document lacks, rather than carving out the first exemption.
5. **"To scale" is the producer's statement.** It is a property of what is drawn, like `log_x`, and both renderers must answer it alike. Deriving it from closed outlines was wrong in both directions on the shipped catalogue.
6. **A file's out-of-range mesh count is the exporter's refusal, not a validation warning.** Validation warnings target analysis-step pages only, and the refusal reaches both the CLI and the beam page verbatim.

- **The calc package writes no digit count of its own: every number in a result note, a validation warning or a condition title prints at its unit's row, and note 65's gate scans all of `sloads/` (#312, tier M, 2026-10-01)** — note 65's gate 4 read `sloads/report/` and the two GUI packages, and 388 hand-written float formats sat in the rest of the calc package, each line choosing its own precision (`:,.0f`, `:.4f`, `:g`). About 235 now go through `units.format_value` with the Imperial unit the number is in, which gained `signed=` for a sentence that states a direction by its sign. The rest are exempt, each with its reason on the statement: the solver channel's text, including the balanced-case summary rows that must print what the case header prints (#324); an identifier whose digits are part of it, such as the D-63.11 run key, a re-weighted ground case or a V-n point's title; an arithmetic `round`; and an entered value's echo. The 52 that were exception messages are exempt by one rule: the walk skips a `raise` statement whole. The walk also judges each expression once now; it used to re-read a nested expression under every enclosing statement. An area in ft² now prints to 0.1 ft² rather than the whole foot (owner ruling, amending D-65.4): a 5.2 ft² rudder had printed `5`, and an area in in² stays whole, so the SI m² row does not move. Thousands separators leave the prose, and a number reads at its row (a landing load factor `3.10`, not `3.0970`). 70 Imperial digests moved across the five fixtures, all on human channels plus the internal balanced deck's echoed notes. No shipped solver digest moved. The SI rendering of this text stays #339's question, and #338's SI gate shows none of it reaches an SI artifact. Note 65 §7c records the amendment; `CONVENTIONS.md` §7's precision row now names the wider scope.

## Step — The engine axial loads of both deck families: the one-engine-out hub carries the propeller's own windmill drag when entered and the stated Glauert bound otherwise, and every gyroscopic case applies every engine at one airplane state (#319, design note 66 D-66.12a/D-66.4a, tier L, 2026-09-29)

**Objective.** Close #319, the 0.8.7 release review's question whether the axial loads the two new families put at the hubs stand as LIMIT loads. The one-engine-out case delivered ONENGOUT's Glauert windmill drag (on the ATR +13,004 lb at VC and +20,319 lb at VD at the failed hub), a term the method used only as a yaw forcing and the manual calls the most the drag "can not be more than" (Ch 11 p88); nothing said it was a bound. Each 23.371(b)/25.371 case thrust its own engine alone, so on the ATR 10,865 lb at y = ±161 in, a 1.75 M lb-in yaw that the closure reacted with an acceleration no part of the airplane produced.

**Deliverables.**
- **The windmill drag (D-66.12a).** A new optional input, `EngineInput.windmill_drag_cd`: the windmilling propeller's disc drag coefficient, from the maker's data or the 23.367(a)(3) history. Schema v71; `_hop_70` is an identity and the first hop after a released schema.
  - When it is entered, the failed hub carries `C_D · q · πD²/4` on the march's own ramp. The owner is `one_engine_out.windmill_drag_from_cd`. `disc_drag_coefficient` reads the bound back from the Glauert term (0.502), so the coefficient is never restated.
  - When it is blank, the hub carries the Glauert term, and every case states it as the method's conservative upper bound and names the input that replaces it.
  - The ONENGOUT march and the fin loads always use the bound.
  - A twin is reflected only when both engines enter the same coefficient.
- **The gyroscopic cases (D-66.4a).**
  - Every engine's ENGLOADS thrust and couples are applied at the same sub-case, and every entered hub thrust is replaced.
  - ENGLOADS now signs the propeller's spin by `prop_direction` (`engine.spin_sense`, `engine.angular_momentum`), as it already signed a turbine rotor's by its `max_rpm`. A sub-case's signs are therefore the airplane's rates on every engine. This amends note 53 D-53.6. No ENGLOADS number moves, because every fixture propeller is clockwise.
  - The case keeps its engine's EM id. It states the net axial force the `n_x` relief reacts, and whether the engines spin together.
  - On the ATR, co-rotating: the couples add, `ṙ` goes from −0.0022 to ±0.0004 (in the closure's per-inch units), and `Δn_x` from −0.79 to −1.12.
  - On the RJ, whose fans counter-rotate: the couples cancel.
  - The report's §10 rotation statement is corrected to match.
- **The #321 engine riders.**
  - `IN_PER_FT` and `VERTICAL_KEYS` are used instead of local copies.
  - `ROTATION_FIXED_SOURCES` and `engine_member` have one owner, in `balance.applied`, which `lra_model` uses too. The restatement and its guard are gone.
  - `coordinates.side_of` is the one side tag.
  - `_MIRROR_TOL` is split into a length tolerance and a load tolerance.
  - Two cases are now recorded instead of shipped: a case scaled by zero (`unscalable`) and a hub off the engine's butt line (`hub-off-arm`).
  - The missing type hints are added.
- **The digest wave: 10 Imperial channels.**
  - `atr42_100` and `concept_regional_jet`: the balance CSV and text, the balanced deck and the LRA deck, from the gyroscopic cases.
  - `baron_58`: the balanced deck and the balance text, from the one-engine-out statement alone. No OEI number moves.
  - `ga6_normal` and `concept_heavy` are unchanged.

**Test.**
- `tests/test_engine_mount_cases.py`:
  - G-66.4 carries every engine's increment at its own nodes.
  - G-66.5 builds the parent without every entered thrust.
  - G-66.17: every gyroscopic case thrusts every engine and, on a symmetric installation, yaws on none.
  - The sub-case is the airplane's rates on every engine: the ATR's couples add, the RJ's cancel, and a counter-clockwise propeller's are reversed.
  - A zero scale is recorded.
- `tests/test_engine_out_cases.py`:
  - The entered coefficient is delivered and the bound is stated.
  - G-66.9 as amended: `[I]{Δω̇} = ΔM` of the drag difference.
  - A twin needs both engines' coefficients to agree.
  - A hub off the arm is recorded.
- `tests/test_hub_thrust.py`: G-12b as amended.

**Key decisions.**
1. **The pairing rule was re-ruled in the build.** Note 66 §12 as first agreed paired counter-rotating engines by flipping both signs, keyed on `prop_direction`. The RJ showed that ENGLOADS already signed a rotor's spin and not a propeller's. The owner ruled (a): sign the propeller's spin too, and pair sub-case k with k. `Rotor.direction`, which no code reads while the sign lives in `max_rpm`, is filed as #332.
2. **The fin load keeps the bound's forcing.** An entered coefficient moves only the hub load and the closure's yaw, by exactly its own moment. Owner ruling (a′).

- **An envelope point no loading can produce is flagged: every entered CG limit and weight/CG case is tested against the loadings the database can hold, `baron_58`'s forward-regardless limit is the one that fails, and its `fwd gross` reaches the deck as an entered loading (#309, tier M, 2026-09-29)** —
  The owner ruled on 2026-09-27 that an envelope point no loading can produce within the database's limits makes the envelope not valid, and must be flagged rather than dropped or ballasted over. Nothing tested it. `baron_58`'s two forward limits sat outside the balanced deck, and the only sign was a searched loading marked not derivable.
  `mass_distribution.envelope_point_reach` is the one owner of the test. It checks each entered structural limit (`weight_envelope.structural_limit_points`, which WTENV's limits table now reads too) and each case against every loading within the rows' limits: discretionary rows at any fraction, and ballast only inside the fuselage and within the 10 % credibility gate.
  At one weight the reachable CGs are exactly the interval between WTENV's two edges filled to that weight (`weight_envelope.sweep_order` owns the sort). The least closing ballast is then solved segment by segment.
  Credible ballast counts because the Appendix A airplane needs it: its 3,400 lb gross is above its heaviest loading. Measured on all five fixtures, a no-ballast rule would have flagged four of them, ga6 included. With the gate, the only point flagged is Baron's `fwd regardless` (4,200 lb at 74.0 in), 2.85 in forward of the most-forward 4,200 lb loading, which no ballast closes.
  It warns `envelope_point_unreachable`, as the limit and as the case, and the 2.2 case table names it from the same owner.
  A case the whole-row search misses, but part-filled rows reach, warns `case_loading_search_missed` with a loading to enter. The search is unchanged.
  Baron's database now carries its [A] baggage: nose 300 lb, where it had 150, and a new 400 lb rear row at +150 (waterline [E]). The loadings entered before the correction carry the nose hold at 0.5, so they are unchanged.
  `fwd gross` is entered as a no-ballast loading: pilot row, full fuel, nose hold 0.4881, mid passengers 0.5693. Its waterline is its own 95.75, where the case had an unsourced 100.0, and it is now an assembled flight state of the deck.
  The corrected payload also raises `mlw_below_landing_estimate` on Baron (OEW + max payload + reserve 5,820 lb against a 5,400 lb MLW), which is true of the airplane.
  Rider (rule 4): both seeds wrote each case's waterline rounded to 0.01 in, and a small solved ballast re-solved from it moves by the rounding times `W / ballast`. Re-seeding Baron's corrected database gave a 20 lb ballast 1 in off its loading's line, breaking #314's fixed point. `cg_cases` now writes the loading's own waterline unrounded. No shipped case is a fresh seed, so nothing delivered moves.
  **Delivered effect, Baron only** (30 Imperial channels; `ga6_normal`, `atr42_100`, `concept_regional_jet` and `concept_heavy` are byte-identical):
  - `fwd gross` assembles SIDE GUST L/R at 1,015.6 lb of fin load. The pre-closure force residual is 0.376 %, so the lateral ratchet is re-pinned to 0.40 %. Izz at `fwd gross` is 7,136.3 slug-ft².
  - SELECT's NHAA (STALL −N at `fwd gross`) goes from 8,011 to 7,978 lb (−0.4 %) with the waterline correction.
  - ONENGOUT reads WTONECG's all-items loading, which now carries 550 lb more baggage: 6,540 lb against 5,990, both above the 5,500 lb MTOW. Its fin load rises 2.1 % (VD 2,159 → 2,205 lb, VS 676 → 702 lb).
  - `fwd regardless` still supplies SELECT's NMAA, NLAA and PNZ air picks; their delivered runs are re-pointed to `mzfw fwd` (D-63.7). The warning now says the point they come from is not a loading.
  Filed from here as #337: Baron has no minimum-crew row, and its `aft max landing` flies without a pilot.

- **sloads requires Python 3.12, and the developer's gate, every pull request and the push to `main` run that one interpreter (#327, tier M, 2026-09-28)** —
  The package declared `>=3.10`, a floor taken from streamlit (#132) rather
  than from anything the code needs, and CI carried 3.10/3.11 legs that ran
  only on the push to `main`, while the developer's `.venv` was 3.11 and every
  pull request and `dev/**` push ran 3.12. 0.8.7 paid for that split twice: a
  deck byte that differed between 3.11 and 3.12 kept `dev/v0.8.7`'s CI red
  from #286 to the cut while every local gate passed (#324), and a 3.11-only
  regex failed the 3.10 leg after the milestone had merged (#325). Now
  `requires-python` is `>=3.12`, the 3.10/3.11 classifiers are gone, and the
  `test` and `sbeam-roundtrip` jobs run `["3.12"]` on every event, so the push
  to `main` adds only the coverage measurement. `tests/test_ci_conformance.py`
  holds two new rules: a pull request runs every interpreter the push to `main`
  runs, and the suite fails when it runs on an interpreter the `ci.yml` `test`
  job does not, which makes a stale `.venv` one named failure instead of a
  gate that silently differs from CI. The asymmetry guard it replaces and the
  doc-wording check for the three-version list retire with the matrix. ruff's
  py312 target raises no new finding. Installing on 3.10 or 3.11 is refused
  from 0.8.8. `CLAUDE.md`, `README.md`, `CONTRIBUTING.md` (the venv command),
  `00_program_overview.md`, `DEVELOPMENT_PROCESS.md` §0/§2, `RELEASE_PROCESS.md`
  §4 and `WORKFLOW_COMMANDS.txt` state the one interpreter.

- **A half-entered h-tail, landing gear or negative stall CL is refused by name instead of stopping the report with a bare ZeroDivisionError, and no handler in `sloads/` swallows a calc defect (#330, tier M, 2026-09-28)** —
  #316 narrowed the report's handlers to the two refusals, `MissingInputError`
  and a plain `ValueError`, and left two catch-alls outside its scope:
  `fleet._wtestima_value`, which turned any WTESTIMA failure into a quiet change
  of source on the fleet chart, and `validation`'s mass-state check, which
  dropped its warning on any exception. Measuring what the second one caught
  over the whole suite found two `ZeroDivisionError`s, and building the report
  over every Optional record the GUI can add, at its blank defaults, on all five
  examples found the rest: three divisors an input can zero, each raising a bare
  `ZeroDivisionError` — SELECT's rational h-tail balance on a freshly added
  h-tail record (elevator effectiveness 0), LANDLOAD's ground angle on a freshly
  added gear record (main and nose axles both at the datum), and the flight
  envelope's STALL −N / STALL −1G on a flaps-up set with no negative stall CL.
  Since #316 each stopped the whole report with a message that named nothing,
  where before it printed as an absent section. Each is now refused where it
  divides, by `MissingInputError` naming the field (`select.htail_balance`,
  `landing.ground_angles`, `flight_envelope.balance_configs`); no number moves
  on a valid project. `REFUSALS` moved from `report/render.py` to
  `sloads.models`, beside `MissingInputError`, because the calc layer never
  imports `report`; the two handlers catch it and nothing wider, and a defect in
  either now raises. `tests/test_report_absence.py`'s scan covers all of
  `sloads/`, with the registry's run-all and the three typing-introspection
  handlers exempted on their lines by `# broad-except: <reason>`, and a slow-lane
  sweep builds the document and package over every blank record. The rule — a
  divisor an input can zero is refused by name where it divides — is a row of
  `00_program_overview.md` §Error handling; the three refusals are stated in
  `PROGRAM_SPEC.md` under FLTLOADS, SELECT and LANDLOAD.

- **An SI artifact states every number in SI, its prose included: provenance notes carry their quantities live and render in the channel written to, a persisted record keeps its numbers in values, and case names stay identifiers (#338, tier M, 2026-09-30)** —
  #312's SI check came first, as its row asked, and found the defect. `units.convert_results` converts values and never text, so a number a calc builder formatted into a string stayed in inches and pounds in an SI artifact. Measured on the five fixtures:
  - the SI LRA deck said "side of body ASSUMED at BL 23.00 in" beside GRIDs in mm (8–13 `$` lines per fixture);
  - both SI mass decks captioned every MASSSET in lb and in;
  - `concept_heavy`'s SI document placed its wing station "at FS 236.0 in";
  - Baron's SI WTENV table had "station -105 in" inside a label.

  Each named its unit, so nothing was mislabelled; the artifacts mixed units.
  **The owner (D1).** `units.UnitText` (built with `unit_text`/`Quantity`) is a sentence whose numbers stay Imperial values until a writer calls `render(system)`. It converts them through the tables a `LoadValue` goes through and prints them through `format_value`, which moved into `units.py` for it (`report/render.py` re-exports it). It has no implicit `str()`. These provenance records carry it:
  - `SobStation`, `FuselageCentreline`, `FuselageLra`, `VtailRoot`, `HTailWaterline`, `HTailAttachment`;
  - the planform notes;
  - `Joint.note`;
  - the LRA model's `assumed_notes`, including its gear-carrier and engine-mount sentences.

  The LRA deck renders them in its own system, and both mass decks' captions render in theirs. `BodyDragWaterline` keeps a plain `str`: its notes state no quantity.
  **Persisted records keep the number in a value (D2).**
  - The body result's `wing_station_note` is now a clause with no number in it (`joints.WING_STATION_CENTRELINE_REASON`), and §8 states the station from the result's `x_wing`.
  - WTENV's `(none -- ...)` ballast marker names no station. The moment-balance station and the fuselage nose and tail stations are value rows of their own.
  - The derived loading notes drop their ballast weight, which the loading carries.
  - A result's persisted `notes` render in Imperial (`tail_span.imperial_notes`); the rest of that class is #312's and #339's.

  **Case names are identifiers (D3).** A re-weighted ground case keeps "at 36,817 lb" in every system, and the SI LRA deck says so once above its case map.
  **Gate** (`tests/test_si_artifacts.py`):
  - SA-1, the rule;
  - SA-2, every provenance record a deck reads types `note` as `UnitText`;
  - SA-3, no Imperial-unit number in the SI LRA and mass decks of any fixture, or (slow lane) in the SI document and its `data/`, once identifiers are removed. The scan names the words that make `in` a preposition, so "-105 in is outside" counts as a station and is caught.

  **Delivered effect.** No load, card or GRID moves. Text moves in Imperial as well, because the notes now print at their units' precision (note 65): "BL 23.00 in" becomes "BL 23.0 in", and the spar fractions print through `format_value`. Imperial digests moved on 15 channels:
  - every fixture's `sbeam/mass_model` and `sbeam/mass_check` (caption text only);
  - the `sbeam/lra_model` of `ga6_normal`, `baron_58` and `concept_regional_jet` (`ASSUMED:` text only; the ATR's notes state no quantity);
  - Baron's `csv/weight_envelope` and `txt/weight_envelope` (the forward-regardless and aft-gross markers lose their stations and gain the station rows).

  No load-case channel moved.

## Step — A T-tail's fin carries the horizontal tail's asymmetry: the AC 23-9 induced rolling moment in every fin condition, one-engine-out included, and the 23.427(a) case through the fin, with the horizontal-tail assumption checked (#328, design note 51 D-51.1a–D-51.11, tier L, 2026-09-29)

**Objective.** Close #328. Note 51 had been AGREED since 2026-09-06 with no issue and no code, and was written against the per-component fin deck note 56 deleted. It was re-scoped against the LRA deck and re-AGREED in session (§9). What the tree did on the two shipped T-tails, measured first:

- **The 23.427(a) roll.** It reached the fin root in the deck exactly (RJ ±72,547, ATR ±30,622 lb-in), but no gate asserted it and the fin view never showed it.
- **The AC 23-9 ¶5a induced rolling moment.** It was absent everywhere. On the RJ it is 27–73 % of the fin's root bending.
- **The ATR's one-engine-out cases.** They govern its fin (889,475 lb-in, 3.6× the four 23.441/23.443 conditions), which meets the trigger note 51 §8 had set for adding them.

**Deliverables.**
- **The induced rolling moment (D-51.3a/D-51.3b).** `tail_span.induced_roll_moment` computes `M_r = 0.3 q S_H b_H β` and returns an `InducedRoll` record: the moment, β, q, Mach, altitude, basis and dihedral.
  - **β.** The fin's own side load, expressed as an angle on SELECT's AVT. This reproduces `RD·EFV·EFFECTV`, the owner's net 19.5° − that, and 15° exactly, and gives each engine-out case its peak fin load as an angle. The side gust takes the AC's `1.2 U/V`.
  - **Sense.** The moment has the sign of the fin's own root rolling moment (AC ¶5d).
  - **Magnitudes.** RJ 137–374k lb-in. ATR 54–162k lb-in in the four fin conditions, and 329k (VC, ultimate) and 459k (VD) lb-in in the engine-out cases.
- **The fin view (D-51.1, D-51.1a, D-51.10).**
  - `TipTransfer.mxx` carries the induced moment, along with its record (`induced`) and the pairing point (`paired_case`). T-16 is narrowed to the symmetric pairing.
  - An engine-out fin result is paired at the 1 g parent the deck assembles it on. That lookup now has one owner, `engine_out_cases.oei_parent_point`, and the march altitude has one owner, `one_engine_out.case_altitude_ft`.
  - `ttail_transfer_to_airplane` passes `mxx` through, and the applied-load row carries it.
  - Each fin result publishes its root rolling moment including the tip set (`vtail_root_mxx_with_tip`).
- **`HTAIL UNSYM` (D-51.2a).** A new fin condition, VT-20, in a new band `VTAIL_BAND_TTAIL` (23.427(c)).
  - Its tip carries the 23.427(a) table's own stations: `fz`, `myy` about the tip, and the net roll `mxx`. The fin carries no air load of its own in it.
  - It is in the fin view only. The deck's 23.427(a) case already carries the roll, as strips (D-51.5a).
- **The deck (D-51.4a).** Each T-tail lateral and one-engine-out case carries one free couple at the fin tip, source `vtail-induced-roll`, read from the transfer's `induced` record and never from `mxx`.
  - The closure's roll acceleration ṗ reacts it, and the case states it in band (`INDUCED_ROLL_NOTE`).
  - The deck's fin-root moment goes up by exactly `M_r`: RJ yaw 15° from 522,579 to 833,148 lb-in; ATR engine-out VD from 889,475 to 1,348,459 lb-in.
- **The stated limits (D-51.7, D-51.8).**
  - `check_htail_under_induced_roll` compares `M_r/2` per side with the horizontal tail's governing root bending, on one factor basis, and states the ratio on each result. RJ ≤ 53.4 %; ATR VC 67.9 %. The ATR's VD engine-out case is **142.2 %**, so its warning fires on the shipped fixture.
  - `validation._check_ttail_induced_roll` raises three warnings on the Tail Loads page: `ttail_induced_roll_sizes_htail`, `ttail_induced_roll_mach` (above 0.6, owner Q2; the RJ's side gust is Mach 0.692) and `ttail_htail_dihedral`.
- **The report (D-51.11).**
  - A T-tail's fin is no longer withheld: 6.5 and Appendix E publish, and 6.5 states the three tip sets and each condition's numbers.
  - Section 5's pointer says the horizontal tail's loads exclude the induced moment.
  - A V-tail and a cruciform still withhold. The dead T-tail branches of the withholding text are removed.
- **Rider (rule 4).** The 23.333(c) gust velocity had four copies (`flight_envelope`, `vn_diagram`, and SELECT's lateral and h-tail gusts). It now has one owner, `constants.gust_ude_fps`, and no conventional fixture's digest moved.
- **Schema v72, with an identity `_hop_71`.** `TipTransfer` is persisted, so the new fields (`mxx`, `paired_case` and `induced`, which holds an `InducedRoll`) change a persisted shape. Note 51 D-51.1's "no hop" predated #310's released-schema rule and is corrected in §9.7. The five examples are re-stamped.
- **Note 21 §5** now letters the fin-with-horizontal case 23.427(c).
- **The digest wave: 16 Imperial channels**, the same 8 on each T-tail (`concept_regional_jet`, `atr42_100`): the case index, the balance CSV and text, the tail-span CSV and text, the balanced deck, the LRA deck, and the fin's applied deck. `ga6_normal`, `baron_58` and `concept_heavy` do not move.

**Test.**
- `tests/test_ttail_induced_roll.py` (new) covers G-51.1 to G-51.11:
  - the (b) roll at the deck's fin root;
  - the engine-out pairing is the deck's own;
  - `HTAIL UNSYM` is its table's own set;
  - the deck carries one couple and never the lumped set, and its fin root equals the fin's own load plus `M_r`;
  - the formula identity and the note's measured figures;
  - the sense;
  - the fin view's root with the tip set;
  - the AC's own 4–6× band (RJ 4.28×/5.15×, ATR 4.18×/5.29×);
  - the h-tail check warns on the ATR's VD engine-out case alone;
  - the Mach warning fires on the RJ side gust alone;
  - an entered dihedral is warned and scales nothing;
  - a conventional layout carries none of it;
  - the gust rule has one owner (an AST check).
- Re-cut tests:
  - `test_balance.py`: the fin set includes the couple, and the lateral pins moved (ṗ +27–83 %, ṙ < 4 %; fin load and Ny unchanged).
  - `test_tail_span.py`: `HTAIL UNSYM` is excepted from the SELECT-pairing and chordwise gates.
  - `test_oracle_report_vtail.py`: a V-tail and a cruciform withhold and a T-tail publishes, and the case-keyed tables allow VT-20 in the spanwise pair.
  - `test_lumping.py` and `test_tail_transforms.py`.

**Key decisions.**
1. **One β rule instead of four.** Expressing each condition's own fin load as an angle makes the owner's net-β ruling (D-51.3a) fall out with no special case, and gives the engine-out cases a β without a second model.
2. **The couple is read from `induced`, never from `mxx`.** `mxx` also carries the 23.427(a) roll on `HTAIL UNSYM`, which the deck already has as strips. Reading `mxx` would count it twice.
3. **The h-tail check is on one factor basis.** The engine-out VC case is ultimate (SF 1.0) and the horizontal tail's governing case is limit. Compared raw, it would read 101.8 %; on one basis it is 67.9 %.
4. **Open: D-51.9, the ATR's tailplane dihedral.** No citable value was found in session (neither Jane's [C] nor a measurable [A] three-view was available), so the fixture still enters 0. The guard is gated on a constructed project. **Deferred with its trigger met:** the ATR's VD engine-out case puts `M_r/2` at 142 % of the horizontal tail's root bending, and the horizontal tail's own loads do not carry it. That is filed as its own issue.

## Release cut: **sloads 0.8.7** (the deck carries what the airplane carries — the engine, the one-engine-out fin, the complete rolling conditions), tag `v0.8.7`, 2026-09-27

**Objective.** Close band **B8**, re-chartered on 2026-09-22 as *the deck
carries what the airplane carries*: the report polish the band was first named
for moved behind #283, and the rows that left a load the airplane flies out of
the one deck that ships moved in. Three were the milestone: the engine-mount
conditions (#286) and the one-engine-out fin (#285), designed in one pass as
design note 66, and the accelerated roll derived as the regulation states it
(#306, note 52 re-agreed). The rest were the mass-state residues note 63 left
(#221, #300, #301) and the precision residues of note 65 (#302, #303). The
band emptied on 2026-09-27 with #310, #276 and #311; the pre-cut release
review (#313–#322) found the cut not clean — one CRITICAL, five MAJOR — and
the owner banded the four that block it back into B8 (#313–#315, #317), the
third milestone running to take that round trip.

**Deliverables** (the `[0.8.7]` changelog section is the release note):
- **The rolling conditions arrive complete (#306, note 52, tier L).** The
  delivered `ACRL` side carries condition A's lift, not the roll point's
  average; the other side is the Amdt 23-48 75 % at every weight (registered
  in `02_approved_corrections.md`); the unbalanced moment derives from the
  pair and the TORS case carries its aileron increment. #315 made the couple
  SELECT and report 3.3 publish the one the chain flies when a user enters it.
- **The deck carries the engine (#286, #285, note 66, tier L each).** Every
  23.361/23.371 mount condition that pairs with a flight state is an assembled
  free-free case at the engine's own nodes; ONENGOUT's peak instant is an
  assembled lateral case on a 1 g parent with the engine pair beside the fin,
  and the fin load now resists its engine's yaw — the sign OR-173 was
  implemented with is reversed, approved by the owner in session on
  2026-09-26 after the fix had shipped (note 44, note 66 §11). #313 made a
  condition that prescribes an engine's thrust replace the entered one, so no
  hub carries two.
- **The mass state holds (#221, #300, #301, #314, tier M each).** The oracle
  reduction keeps each case's loading; a case's waterline is its loading's,
  checked to 0.5 in on station and waterline both, and re-seeding is a fixed
  point; the half-span wing models are fed through one projection that
  refuses an unmirrored wing mass state.
- **Files a release wrote stay readable (#310, #276, tier M/S).** From this
  release on every release's schema is recorded in `RELEASED_SCHEMAS` with a
  frozen fixture, and the hop chain must reach it without a gap; the v55–v69
  hops and the readers' legacy branches are gone.
- **Precision and tooling (#302, #303, #308, #311, note 66 follow-up, tier S).**
  Every delivered and on-screen number takes its digits from its unit; a
  non-finite value is refused; the balanced deck resolves the envelope once;
  the suite's shared bundles build once per worker behind a `slow` lane; the
  oracle journey converges on `atr42_100` again.
- **A zero prints unsigned whatever the Python version (#324, tier S).** The
  release PR's CI (#323) failed on the regional jet's balanced-deck digest,
  and so had every `dev/v0.8.7` push since #286: the gyroscopic engine-mount
  headers printed a zero-by-construction closure load factor with the sign of
  its solve residue, `+0.00000` on Python 3.11 and `-0.00000` on 3.12. Both
  print sites now read one snapped owner; the ATR 42's eight such headers move
  to `+0.00000` and its deck digest is regenerated, and no load card moves.
- **A test regex that loads on Python 3.10 (#325, tier S).** `main`'s full
  CI run after the merge failed on the 3.10 leg alone: #303's unit guard in
  `tests/test_joints.py` used a 3.11-only atomic group. It now uses the
  lookahead-and-backreference spelling, and the tag waited for the fix.
- **The release review's closure debt (#317, tier S).** Note 66 gained its
  theory citation and gate rows, note 63 records the symmetric wing mass rule,
  and no fragment describes the deleted hop.
- **Docs-only commits on the branch:** design note 66 PROPOSED and AGREED
  (Q1–Q7 as recommended), note 44 OR-173 amended, and the owner's bandings of
  #312/#309 into B9 and #313–#315/#317 into B8.
- **Version** `0.8.6` → **`0.8.7`**. Schema **v68 → v70**: v69 at #306
  (`WingLoadCase.unbal_moment` optional) and v70 at #276 (`engine_count`),
  both with no hop, since #310 made the first released schema the floor and
  neither was released. **`RELEASED_SCHEMAS` gains its first row,
  `"0.8.7": 70`**, frozen as `tests/fixtures_schema/release_0.8.7.json`
  (a copy of `examples/ga6_normal.project.json`).
- **Changelog cut** — `scripts/build_changelog.py 0.8.7 --date 2026-09-27`:
  **17 fragments** consumed — 7 into `## [0.8.7]` directly and **10 history
  entries** rolled to the top of this file, their changelog bullets derived
  from their leads — and a fresh empty `[Unreleased]` opened. #324's bullet
  was written into `## [0.8.7]` by hand afterwards: the release PR's CI found
  it after the cut (below).
- **Record roll** (`RELEASE_PROCESS.md` §4 step 3): no note moves (note 61
  CV-3). This file stood at 1,461 lines before the cut and 1,803 after
  the fragments, over 1,500, so everything below the 0.8.6 release-cut block
  (the 0.8.6 cycle and the 0.8.5, 0.8.4 and 0.8.3 cuts) moved verbatim to
  [`67_completed_development_to_0.8.6.md`](67_completed_development_to_0.8.6.md);
  587 lines remain. The changelog stood at 967 and 1,110; it did not
  roll.
- **Verification baseline** (§4 step 5): unchanged from
  [`36_verification_baseline_0.7.0.md`](36_verification_baseline_0.7.0.md)
  but for the one registered correction: the 23.349(a)(2) 75 % moves the
  Appendix A airplane's derived unbalanced rolling moment from the printed
  149,043 to 128,619 lb-in and the `AC ROLL` load factor to `0.875·n₁`, each
  figure stated in `02_approved_corrections.md` and asserted in
  `tests/test_rolling_conditions.py`. Every other Appendix A assertion is the
  same test on the same printed number.
- **Gates at cut:** `pytest` **3,901 passed / 11 skipped / 2 xfailed / 0
  failed** (3,742 passed / 9 skipped / 2 xfailed at the 0.8.6 cut) on
  `28b72d4`, the tip before the cut commits, with the cut's own guards
  (migrations, doc currency, links, fragments, backlog) re-run green after
  them; `ruff` clean, `mypy` clean (`sloads/`, 112 source files),
  `scripts/smoke_test.sh` **PASS**, `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on
  7 tracked keys, the §3.5 by-hand walk done by the owner
  (2026-09-28). Of the 2026-09-27 review's CRITICAL/MAJOR findings,
  #313–#315 and #317 closed on the branch;
  **two MAJOR stay open by the owner's banding ruling of 2026-09-27**, which
  named the four above as the cut's blockers and left the rest unbanded: #316
  (a NaN still swallowed by `package_data` and the report's broad
  `except Exception` sites — #303's rule not yet swept) and #318 (note 66 and
  52 gates that re-derive what they check). #319–#322 are decisions and
  minors.

**Key decisions.** *A load the airplane carries is not delivered until the
deck carries it.* The band was re-chartered on that sentence, and each of its
three large rows found a quantity the report printed and the one shipped deck
did not hold — the engine, the one-engine-out fin, condition A's lift on the
rolling side. The second decision repeats 0.8.6's: an emptied band is not a
release until a critical read of the whole branch says so. This one found a
thrust counted twice on a gyroscopic case and a published couple that was not
the one flown; the round trip cost a day and four rows. The third is recorded
where it was made late: #285 reversed the fin-load sign OR-173 was
implemented with before the owner saw it, and the approval stands in three
places that now say the same thing. The last was learned at the merge: the
fast gate on `dev/v0.8.7` was red on every push from #286 to the cut, on one
Python-version byte (#324), and no close stopped on it because
`solo_close.sh` gates locally and reads CI after the push. The release PR was
the first place anyone read it; a close that waits for CI is left to the owner.
The merge then found the other half of the same gap: 3.10 and 3.11 run only on
the push to `main`, so a 3.11-only regex in a test (#325) surfaced after the
milestone PR had merged, and the tag waited on a second PR.

- **The accelerated roll's published couple is the one flown: the variant table resolves ACRL through the same owner as the wing chain and the balanced deck, so an entered unbalanced rolling moment reaches SELECT, report 3.3 and the Wing Loads caption (#315, tier M, 2026-09-27)** —
  The wing chain and the balanced deck resolve the ACRL case through
  `rolling.complete_rolling_case`, where an entered `unbal_moment`, `cl` or
  `v_eas_kt` wins over the condition A derivation (design note 52). The
  `wing_variants` table derived all three regardless, and SELECT publishes
  the governing row, so the regional jet flew its entered -600,000 lb-in
  while SELECT and report 3.3 published the derived -1,614,422 lb-in and a
  roll acceleration built from it. The table now resolves each ACRL row
  through `complete_rolling_case`, with the entered case named by the new
  `rolling.entered_rolling_case`. The row records which fields were entered
  and keeps condition A's CL, speed and root bending as separate fields.
  SELECT labels an entered couple *(entered)* and publishes an entered air
  point beside condition A's. Report 3.3 names the entered value and states
  the derivation for comparison, and the GUI caption decides entered versus
  derived from the input instead of comparing numbers. On the regional jet
  every ACRL row's net root bending rises by about 480,000 lb-in (less roll
  relief), the governing row is unchanged (fwd gross, case 180), and so is
  every delivered wing and deck load; the other four fixtures enter no
  couple and do not move. The Imperial baseline moves on the regional jet's
  SELECT CSV and text report alone, and the digest is regenerated. A gate
  in `tests/test_rolling_conditions.py` holds SELECT's published couple to
  the wing chain's and the balanced deck's on every fixture.

- **A case's waterline is its loading's: a loading with no ballast counts as its case only within 0.5 in on station and waterline both, both seeds write back the waterline of the loading that closes each case, and `case_loading_checks` holds every case to that and is stated under the oracle report's 2.2 case table (#300, tier M, 2026-09-26)** —
  The subset search accepted a no-ballast loading (a subset that already
  weighs the case, or a ground case's fuel burn-down) on its station alone, so
  a loading could sit anywhere in waterline under a case whose `zcg` every
  balance, trim and gear module reads. The check meant to see that was wrong
  and unrouted: it held a no-ballast loading to 1e-9 — false failures on
  `ga6_normal`'s CG4 (0.0024 in, the very precedent the 0.5 in tolerance was
  written for) and `baron_58`'s `aft gross` xcg (0.35 in) — read flight cases
  only, and sat on `_UNSTATED_CHECKS` with no consumer. The search now tests
  both coordinates (`mass_distribution._cg_matches`); the check applies that
  band, covers ground cases, and is stated in the 2.2 case-table note, naming
  any case whose loading is not the case; `_UNSTATED_CHECKS` is empty. The
  sweep found the class three times. `baron_58` `aft gross` flew at 95.88
  against a stated 100.0 (4.12 in) and `concept_regional_jet` `fwd max
  landing` at 64.82 against 62.66 (2.16 in). And `cg_cases.seed_landing_cases`
  wrote every ground case's `zcg` as the whole database's waterline and never
  re-echoed it (D-26a), so the search solved ballast to reach that
  placeholder: 1,607 lb at the lowest item of `atr42_100` (z 60) under both
  max-landing cases, 1,946 lb near its top (z 218.7) under `fwd light`. Both
  seeds now share `cg_cases._echo_loading_waterlines` (search on station, write
  the found loading's waterline back); `derive_case_loadings(...,
  match_waterline=False)` exists for that step alone. Owner rulings: each case
  takes its loading's own waterline rather than a solved ballast the airplane
  does not carry — Baron `aft gross` 95.88, RJ ground 61.96 / 64.82 / 63.08,
  ATR ground 141.56 / 141.56 / 132.33; ATR's `aft max landing` ballast falls to
  1,007 lb at z 163.4 and the others move onto their loading's line. Delivered
  effect, three fixtures (`ga6_normal` and `concept_heavy` are byte-identical):
  Baron's governing horizontal-tail up-gust root bending 36,248 → 36,543 lb-in
  (+0.8 %), CHECKED MAN UP 13,398 → 12,926 (−3.5 %), the non-governing BAL UP
  RETRACTED 3,889 → 3,133; its one-engine-out pre-closure My residuals mostly
  fall now that the reference is the mass centre (VD −11,102 → 1,697, VC
  −7,055 → 95 lb-in) while VS rises to 0.7 % of n·W·MAC (−762 → −2,542). The
  critical nose-gear reactions rise 1.5 % on ATR (level landing Fz 21,918 →
  22,248 lb) and 1.2 % on the RJ (braked roll 8,752 → 8,859 lb); no flight,
  net or body load moves on either. The Imperial baseline was regenerated for
  those three (Baron 24 channels, ATR 8, RJ 8). Not in scope and unchanged:
  Baron's `fwd gross` and `fwd regardless` need 720 lb (13 %) of ballast, past
  the credibility gate, and reach no deck (filed as #309).

- **A condition that prescribes an engine's thrust replaces the entered one: the 23.371(b)/25.371 gyroscopic case's engine carries ENGLOADS's max-continuous thrust alone and a one-engine-out case ONENGOUT's pair alone (#313, design note 66, tier M, 2026-09-27)** —
  An entered `thrust_lb` (#10) is applied at every engine's hub in every
  flight case, and the engine-mount builder keeps it unscaled on purpose; the
  gyroscopic increment then added ENGLOADS's thrust at the same hub, and the
  one-engine-out case added ONENGOUT's live-thrust / windmill-drag pair beside
  the entered thrust on both engines. On an `atr42_100` copy with 4,000 lb
  entered per engine the left engine's gyroscopic case carried 14,865 lb
  (10,865 + 4,000), and the one-engine-out case gave the failed engine 4,000
  lb of thrust beside its 13,004 lb windmill drag and the live engine 5,921 lb
  (1,921 + 4,000). `hub_thrust_set` now tags each hub force with its engine
  (`carrier = engine-<i>`, the D-66.6 rule, so an entered thrust also routes
  to its own engine's LRA member) and leaves out the engines a condition names
  as `replaced`, saying so in band: a gyroscopic case's parent is assembled
  without its own engine's entered thrust, the other engines keep theirs, a
  torque case keeps all, and an engine-out case — ONENGOUT models a twin, so
  its pair is the whole thrust state — carries none. The "Applied engine
  thrust" row and `is_powered` read the entered thrust only, as they did; the
  engine-mount docstring's claim that ENGLOADS's thrust made a case powered is
  corrected (the family's gate exemption is `is_engine_mount`). Latent: no
  shipped fixture enters thrust, so no delivered load, card or case moves.
  Gate G-12 in `tests/test_hub_thrust.py` — no hub in any case of a powered
  build carries two thrusts; the gyroscopic engine's thrust is the unpowered
  build's; the engine-out pair is the unpowered build's.

## Step — The deck carries the engine: every 23.361/23.371 mount condition that pairs with a flight state is an assembled free-free case at the engine's own nodes, and every balanced case states its own safety factor (#286, design note 66 D-66.1…D-66.9, tier L, 2026-09-26)

**Objective.** Close #286: ENGLOADS computed every engine-mount condition and
the LRA deck had a mount and a hub node per engine since note 24 R-9, yet no
engine condition reached the deck — a nacelle, mount or attachment sized from
it saw no engine case, and the deck said nothing about the absence. The owner
agreed design note 66 the same day (Q1–Q7 as recommended).

**Deliverables.** A new balanced family, `balance/engine_cases.py`, appended
after the ground families: per engine, never mirrored, ids ENGLOADS's own
`EM-nn`. Each case is an assembled flight case in SELECT's delivered PHAA block
(PHAA's point for 23.361(a)(1)/(a)(2), `BAL C` for (a)(3) and FAR
25.361(a)(3)(i)/(ii), `MAN A` for 23.371(b)/25.371) scaled by one constant to
the load factor ENGLOADS states for the engine, plus the engine's own torque,
gyroscopic couples and thrust through `coordinates.engine_applied_load`, at the
mount and hub nodes of that engine. ENGLOADS's vertical is never re-applied —
the engine's mass is in the parent's inertia at that `n`. The torque is trimmed
by an equal and opposite `aileron-trim` couple (note 21 P-9); the gyro couples
and thrust are closed by the rigid-body relief. 23.363 and 23.361(b)(1) are
mount-local and named in the deck's not-assembled block with their reason. The
LRA model gains a member per engine and routes an EM load by its `carrier`.
Every balanced case now stamps its own safety factor from the governing table
(`safety_factors.stamp`), so the deck's basis sentence states the case's factor
rather than the field's default — 1.5 everywhere today. Each gyroscopic sign
combination is now a condition with its own `EM` id (`engine.split_gyro`,
`mount_conditions`; the render-time `a`–`d` suffix retired), and 25.371's A2
vertical is read wherever the 2.5 g one was (`load_keys.FZ_VERTICAL_A2`).
One Imperial digest wave, 26 channels: the balanced and LRA decks, the balance module's CSV and text and the case index move on the four engine fixtures (the EM subcases, the not-assembled engine lines); the engine CSV, text and applied-load file move on the two turboprops (the gyro split's ids; the RJ's 25.371 vertical, 0 before). `concept_heavy` has no engine and did not move.

**Test.** `tests/test_engine_mount_cases.py`: the deck carries exactly the
ruled set per fixture (G-66.2); every case's SF is the table's (G-66.1); each
EM case flies at ENGLOADS's `n` with no re-applied vertical, and the itemised
engine weighs ENGLOADS's `PPWT` to the pound where the database itemises it
(G-66.3); the increment is `engine_applied_load` of ENGLOADS's scalars and
lands on its own engine's nodes (G-66.4); every case closes in six DOF (G-66.5);
the torque nets no roll and no EM case is handed (G-66.7); the RJ's 25.371
rows carry their vertical (G-66.12). The round-trip solve gate passes on every
engine fixture with the new subcases (G-66.6).

**Key decisions.** (1) The regional jet's database lumps both engines as one
3,400 lb centreline row against ENGLOADS's 2 × 1,550 lb: its EM cases are
correct for the airplane as entered, and the discrepancy is recorded in note
66 §10, not fixed. (2) The family is exempt from the flight trim gate — the
case it scales is gated as itself — and is judged by G-66.x. (3) The gyro split
renumbers the turboprops' later EM ids (the ATR's right engine moves from
EM-07… to EM-10…).

## Step — The one-engine-out fin reaches the deck: ONENGOUT's peak instant is an assembled lateral case on a 1 g parent with the engine pair beside the fin, and the fin load it publishes now resists its engine's yaw (#285, design note 66 D-66.10…D-66.16, tier L, 2026-09-26)

**Objective.** Close #285: SELECT names ONENGOUT's 23.367 fin conditions on
every twin — on the ATR 3.6x its largest static fin case, the fin and aft
fuselage's sizing load — and the assembler skipped all of them as out of
family, on a deferral to a per-component fin deck that note 56 deleted.

**Deliverables.** A new balanced family, `balance/engine_out_cases.py`,
appended after the engine-mount family: each recovered ONENGOUT condition at
its instant of peak total fin load, assembled on FLTLOADS's 1 g point for the
speed (`BAL C` / `BAL D` / `STALL 1G`) at the heaviest derivable FLIGHT CG case
and the V-n altitude nearest ONENGOUT's, carrying the fin distribution
`tail_span` builds and the engine pair at that instant — the live engine's
thrust at the mirror of the failed hub and the failed engine's remaining
thrust and windmill drag at its hub, from `one_engine_out.engine_forces_at`,
the march's own schedule. One engine's failure is computed per speed; the
mirrored engine's is its reflected twin under its own VT id. No L-7 term, said
in band; unrecovered marches recorded (`not-recovered`). The 23.367(a)(2) cases
state `ULT SF=1.0` through #286's stamp. **The published fin sign is
corrected**: ONENGOUT gave every fin load (and δ, α_tail) the sense that adds
to its own engine's yaw while its β carried the nose's; the fin now resists
(`+y` engine → `+y` fin load, SELECT's static convention) and β keeps the
nose's sense. Magnitudes and the fin envelope are unchanged; which engine's
case carries which sign flips. One Imperial digest wave, 32 channels: on the two twins the balanced and LRA decks, the balance output and the case index gain the family, and the one-engine-out, tail-span, chordwise and v-tail applied outputs move with the sign correction (12 each); on the other three fixtures only the deck headers and the balance text move, for the reworded out-of-family sentence.

**Test.** `tests/test_engine_out_cases.py`: one computed case and its twin per
recovered speed (G-66.8); the closure's yaw is ONENGOUT's ψ̈ after the Izz ratio
to 2–3 % (G-66.9, gated at 5 %); the fin opposes the engine pair, and a
positive β carries a negative fin load; each twin carries the other engine's
own fin load (G-66.10); the ATR's unrecovered VS is recorded (G-66.11); SF 1.0
on 23.367(a)(2) (G-66.14); no L-7 load and the statement in band (G-66.15);
the 1 g half closes inside 1 % (G-66.16); `engine_forces_at` reproduces the
march's engine moment at every instant.

**Key decisions.** (1) The sign correction reverses the fin-load sign note
44 OR-173 was implemented with (its one-case-per-engine rule stands) — found
because the balanced case is the first place the fin and the engine met;
recorded in note 66 §11 and approved by the owner in session, 2026-09-26
(after the fact: the fix shipped in 60c90ab before the owner reviewed it).
(2) The family is exempt from the trim gate for the engine pair's pitch couple (6.4 % of n·W·MAC on the
ATR's VC case — the pair's axial force at the hub waterline), the powered
cases' standing; the 1 g half is gated instead.

- **The half-span wing models are fed through one projection, `mass_distribution.half_span`, which refuses a wing mass state whose off-centreline parts are not mirrored pairs instead of running it as one side doubled (#301, tier M, 2026-09-26)** —
  The item database is full span (every row at its own butt line), but
  WINGINER (whose BASIC hangs every concentrated weight at a positive butt
  line), the balanced deck's wing set (the starboard half, mirrored) and the
  per-case tie are half-span models. The symmetry they depend on was checked
  in three places over three different sets of rows. The subset search and
  the seed search tested the discretionary subset alone, never the empty and
  minimum rows under it. Only POINT rows were counted, and by weight sum. The
  deck built its own starboard point set with its own copy of the centreline
  half-weight rule. Measured on `ga6_normal` with one 50 lb `EMPTY` wing row
  at y = ±100: a starboard POINT row reached the half-span models doubled
  (100 lb) and a port one was dropped (0 lb), each behind a warning while the
  search still called the loading valid. A one-sided PANEL row was halved
  onto both wings with no finding at all. Owner ruling (in session): build the
  projection now rather than a per-side deck (tier L, parked while no
  delivered load comes from an asymmetric mass state), and **refuse**; design
  note 63 §13 records the rule and supersedes its §10 amendment (a). The
  projection is the one place the rule lives: every off-centreline `WING`
  part, PANEL or POINT, must have a mirror image (same weight, x and z,
  opposite y, within `RECONCILE_REL_TOL` and 0.5 in). This is a pairing, not
  a weight sum, and a state that fails raises `WingAsymmetric` naming the
  parts. The search and seed search test base and subset together through
  `wing_symmetric`, and the seed search no longer trims one row of a mirrored
  pair. An asymmetric entered loading is not derivable, so the deck, WINGINER
  and the body beam refuse it by the route they already take for an
  unreachable case, with the parts in the reason. `validation`'s
  `wing_mass_asymmetric` now names a database that fails; the deck's point set
  and `WingMassState` read the projection (`port_point_weight_lb` and
  `_wing_points_symmetric` are gone). Every shipped fixture's database and
  every loading already pair exactly, so no output, digest or baseline moves.
  Guards: every shipped mass state is an exact half span; a one-sided POINT
  (either side) or PANEL row is refused by name at the projection, the mass
  state and the validator; the search refuses an asymmetric base; and a
  weight-balanced pair at unmirrored stations is refused. The SSOT row is in
  `CONVENTIONS.md` §7.

- **The oracle reduction keeps each case's mass state: the `consumable` flag and an entered `loading` survive it, so the oracle report names the loading the analysis flew and a loading edit moves its fingerprint (#221, tier M, 2026-09-26)** —
  `field_registry.reduce_to_oracle_inputs`, which the oracle document and its
  fingerprint are built from, reset every field outside the oracle input set,
  and the loading model is sloads-only: every tank read as payload and every
  entered loading was replaced by a search. Measured on `atr42_100` before the
  fix: fuel 9,874 → 0 lb at MTOW and 700 → 0 at MZFW on all eleven cases,
  eight entered loadings searched instead, and the search adding up to
  1,669 lb of ballast the airplane does not carry; all five fixtures moved.
  Wing loads did not (total weight, CG and wing mass are unchanged) — the
  defect was in what the document states. The fix is a new registry
  declaration, `KEPT_BY_REDUCTION`, each entry with its reason, which the
  reduction honours and the GUI tiers and the supplied-set dial do not see
  (`supplied` was rejected: it would render the fields as original-suite
  inputs, and no Appendix A oracle depends on them). One reduction serves G5
  and the document alike. The G5 module comparison could not see the defect
  (fuel reclassified as payload moves no oracle-page value), so the guard
  compares the mass state itself — `mass_case_summary` equal on the full and
  reduced project for every shipped example — and the test that asserted the
  loading was dropped now asserts it is kept. The backlog row's `carriage` was
  already `supplied` (design note 63). MZFW and crew were swept and stay
  plain: they seed and check cases, and state no case's mass.

- **A project file is readable if a release wrote it: from 0.8.7 on every release's schema is recorded and frozen, and the hop chain must reach it without a gap; the v55–v69 hops, their fixtures and the readers' legacy branches are gone (#310, tier M, 2026-09-26)** —
  Owner ruling (in session): compatibility is kept at release level, starting
  at 0.8.7. A file any release from 0.8.7 on wrote stays readable by every
  later release; a schema version that lived only on a development branch is
  never promised. Before this the gate read v55 onward through fourteen hops
  that carried files no one holds (the project is pre-production and the owner
  keeps no project files outside `examples/`), and #276 was waiting for a
  schema hop to ride. `sloads.migrations` now keeps the gate and the machinery
  (`migrate`, the `MIGRATIONS` chain, `migration_notes`) and adds
  `RELEASED_SCHEMAS`, empty until the 0.8.7 cut. `SUPPORTED_FLOOR` is the
  oldest released schema, or the current one while none is recorded. The rule
  is held by `tests/test_migrations.py`. Every release the changelog names from
  0.8.7 on must have a row, so the cut's new header turns the suite red until
  it does. Every row's frozen `tests/fixtures_schema/release_<X.Y.Z>.json` must
  load. And the chain must run from the floor to the current version without a
  gap, since the reader drops unknown keys and a bump with no hop would misread
  a stale file rather than refuse it. The step is in `RELEASE_PROCESS.md` §4.
  With no hop left to reach them, the readers' legacy branches went too: the
  singular `engine` key, a V-n point's singular `case_ref`, the retired
  stall-speed and `units` keys, the gear built from retired layout fields, and
  the fuselage outline built from the parametric length/width/height (with
  `default_fuselage_outline`, now unused). The reader no longer takes those
  three scalars at all, since they are never written. One of the branches was
  a live defect: a surface's `ref_axis_pct` entered as 0.25 read back as "not
  entered", a rule written for files the pre-v52 writer saved. An entered 0.25
  now stays entered. No shipped example carried any of these shapes, and no
  load, deck or digest moves.

## Step — The rolling conditions arrive complete: condition A's lift on the delivered ACRL side, the Amdt 23-48 75 %, a derived unbalanced moment and the TORS aileron increment (#306, design note 52 D-52.1…D-52.13, tier L, 2026-09-25)

**Objective.** Deliver FAR 23.349's two rolling cases whole. SELECT always
picked `ACRL` and `TORS`, and WINGINER always had the unit-roll physics, but
the unbalanced rolling moment had to be typed by hand (a derived `ACRL`
carried zero, #258), the delivered `ACRL` variant flew the `AC ROLL` point's
airplane-average lift rather than condition A's (≈ 19 % low on the governing
side's net root bending), the other-side percentage was the manual's
pre-1996 70→75 % rule where 23.349(a)(2) as amended by Amdt 23-48 says 75 %
flat, the TORS `Δcm = −0.01·δ` increment was selected on but never applied,
the variant table ranked `ACRL` without its couple (#295), and an acrobatic
project got the normal percentage silently.

**Deliverables.** `constants.other_side_percent` (75 %, acrobatic refused
with `UnsupportedCategoryError`) is the one percentage owner, read by
FLTLOADS's `AC ROLL` factor `(100 + p)/200 · n₁` (3.25 → 3.325 on the GA6).
A new `modules/rolling.py` owns condition A's point and root bending, the
derived `UNB = −(1 − p/100) · M_root(A)`, the roll acceleration, the CAM 3.222
steady-roll schedule SELECT's torsion proxy now reads, and the TORS `Δcm`
table built on the existing v52 aileron butt lines. `resolve_wing_cases`
completes every `ACRL` case from those owners (entered values win); the
variant table builds `ACRL` rows at condition A's air with the derived couple
in the inertia; the balanced deck reads the same resolved couple, deriving it
at the balanced case's own point where an entered filter list omits `ACRL`.
The delivered wing conditions publish the derivation (percentage, condition
A's CL/V/root, UNB, θ̈ on `ACRL`; the deflection schedule on `TORS`). Schema
v69: `WingLoadCase.unbal_moment` is optional, blank derived; no hop (v69
was never released, #310). `ga6_normal`'s `ACRL` row is retired to
derived. The three "UNB comes from AILERON" statements are corrected.
`CONVENTIONS.md` §7 gains three owner rows; the approved-corrections entry,
ch04, ch09, `theory_sources.md`, `PROGRAM_SPEC.md` and D-29 carry the
shipped statement. One Imperial digest wave, 66 channels: FLTLOADS, SELECT, BALLOADS and the balanced and LRA decks moved on every fixture (the `AC ROLL` factor, the published derivation, every `ACRL` now a handed pair with its couple); NETLOADS, WINGINER and the wing applied deck on the GA6, the ATR and the RJ, whose wing lists run `ACRL`; the case index on all but the RJ. AIRLOADS, AILERON, the body, gear and tail channels did not move. Report §3 gains 3.3 *Rolling conditions* (the method, the percentage, the UNB derivation table and the deflection schedule; the two subsections after it renumber through the owner) and the Wing Loads page a caption stating the couple.

**Test.** `tests/test_rolling_conditions.py` holds G-52.1–G-52.13: the
Appendix A case 160 as a **test-built case** at its printed inputs reproduces
WINGINER p. 219 (θ̈ −13.287, root Sz −1126, Mxx −124,095, Myy +30,410) and
NETLOADS p. 225, so the `.BAS` math stays locked under the amended rule; the
derived UNB at the printed condition A is 128,619; the delivered `ACRL` air
equals condition A's to the identity on every variant; TORS with blank butt
lines is p. 226, with BL 109.28–201 its root ΔMyy is −18,667; drift guards
forbid the retired rule's literals and a second producer of the couple.
FLTLOADS case 20 is held at the manual's factor and asserted at the amended
one. D-29's divergence pin is replaced by the condition A equality.

**Key decisions.** (1) SELECT's `ACRL` pick on the GA6 moved from 12,000 ft
to sea level (V-n case 40): at the amended factor the CG2 roll points' LZW
tie across altitude to 0.13 %, inside the balance's 0.5 %; the build follows
SELECT's criterion and note 52 §9 leaves a tie band to the owner. The GA6
delivers UNB −129,142 and a net root MX of +400,817 (+2.7 % on the print).
(2) θ̈ is published in rad/s² — WINGINER prints it unlabelled and
`UNB·g/I_wxx` is 1/s². (3) Every fixture's `ACRL` is now a handed pair: the
ATR, the Baron and `concept_heavy` assembled a symmetric `ACRL` with no couple
before. (4) The TORS increment is wing-chain only; the balanced TORS stays the
symmetric trim case.

- **A seeded case's waterline is a fixed point: with no waterline target the search puts a solved ballast on the candidate loading's own waterline, so the placeholder no longer chooses the loading and re-seeding returns the same `zcg` (#314, tier M, 2026-09-27)** —
  Both seeds search for the loading that closes each case on a placeholder
  waterline and write the found loading's waterline back (D-26a, #300).
  `match_waterline=False` dropped the waterline from the match test but
  still solved the ballast's waterline from the placeholder and rejected
  any ballast that fell outside the airframe, so the placeholder decided
  which candidates survived. ATR's `aft max landing` searched on WTONECG's
  137.93, lost its least-ballast loading to that filter, and seeded 141.56;
  the flown search at 141.56 then chose the least-ballast loading after all
  and closed it with 1,007 lb of ballast at waterline 163.4, 22.5 in above
  the rest of a loading at 140.93. `case_loading_checks` could not see it,
  because the ballast made the totals match. The ballast now sits at the
  candidate's own waterline when there is no target, so the seed's choice
  is independent of the placeholder and the flown search keeps it. Measured
  on every seeded case of every fixture, ATR's `aft max landing` is the only
  one that moves: its fixture `zcg` is 140.93 (amending the #300 ruling's
  141.56) with the same loading and ballast weight, the ballast at 140.8.
  The Imperial baseline moves for ATR only, and only on that case: the gear
  loads read the CG height, so its landing moments and gear reactions shift
  by 0.1-0.6 % (landing and balance CSV/TXT, gear report, applied gear CSV),
  and the balanced and LRA decks carry the ballast at 140.8 instead of
  163.4; the digest is regenerated. A guard in `tests/test_cg_cases.py` holds every
  seed of every fixture to its own re-echo and every solved ballast to its
  loading's waterline within the 0.5 in match band.

## Release cut: **sloads 0.8.6** (the baseline wave — one mass model, the negative wing slots, the wing-body joint, delivered precision), tag `v0.8.6`, 2026-09-23

**Objective.** Close band **B7** — the rows that move delivered numbers and
regenerate the digests, sequenced after 0.8.5 so the regeneration is paid
once, and gated on one decision: #164's case-set shape. Taking that decision
opened the band wider than its five rows. Design note 62 (the negative
angle-of-attack wing slots) answered the case-set question; note 63 (one mass
model) answered what mass each case carries; note 64 (the wing-body joint)
answered where the body reacts the wing; note 65 (delivered precision)
answered how a number becomes text. The band emptied on 2026-09-22, the
pre-cut critical review found the cut not clean — one CRITICAL, ten MAJOR —
and it re-opened for six fixes (#294–#299, #295 folded into #306), the round
trip the 0.8.3 cut also took: a release cannot knowingly carry a wrong
delivered load.

**Deliverables** (the `[0.8.6]` changelog section is the release note):
- **The wing case set is complete on both sides (#288, note 62, tier L).**
  SELECT.BAS carried three positive angle-of-attack slots and one negative;
  NHAA (W-07) and NLAA (W-08) are added, NMAA narrowed to the VC pair, a
  negative slot admits negative lift only, and the load-factor-extreme pair
  PNZ (W-09) and NNZ (W-10) delivers the point that sizes the wing-mounted
  masses whatever weight it occurs at. The six Appendix A picks are locked and
  the new slots closure-gated on every fixture's frozen pick.
- **One mass model (#289, #292, #290, note 63, tier L/L/M).** The case's D-25
  loading is the mass state of every inertia load: `WingMassInput` loses its
  mass (schema **v67**), the panel is derived from the `PANEL` rows and the
  concentrated masses are the loading's `POINT` rows, fuel is entered per tank,
  MZFW is a design weight that seeds the zero-fuel and full-fuel cases, every
  SELECT wing slot runs at every FLIGHT mass state with the net-governing run
  delivered, `CaseRef` carries the run key beside the slot id, and the Payload
  Cases group edits the loading the distributions read.
- **The wing-to-body joint (#275, note 64, tier L).** One vertical post at the
  wing station, the fuselage beam through the box with grids at both spars,
  the body integrated as two cantilevers positive-up, the box's loads applied
  and never integrated, M4-1's linear smear and the whole-body closure
  correction retired; a project that cannot place the wing post is refused by
  name (schema **v68**).
- **The baseline wave proper (#164, #222, #260, #293, #161, tier M each).**
  The GA6 fixture balances at Appendix A's three altitudes; the fuselage
  critical set publishes one key per quantity; the ATR 42 fixture is
  reconciled end to end from the published 42-300 data; a closure load lands
  on the member that carries its mass; and every delivered cell prints at the
  precision its unit prescribes (note 65) — no exponent form on the human
  channel, one owner for the digit count, the solver channel untouched.
- **The deck says what it does not carry (#284, #210, #291, tier S).** The LRA
  deck states the SELECT conditions it does not assemble; every engine-mount
  condition states its own point of application; the heavy's drag polar has
  its minimum at the wing's zero-alpha lift coefficient.
- **The pre-cut review's fixes (#294, tier M; #296, #297, #298, #299, tier S).**
  D-62.8's coincidence rule runs once, on the delivered wing set, so the NNZ
  extreme is delivered by somebody whatever mass state NMAA moves to (the
  CRITICAL: `baron_58` case 153 at −2.345 g and the RJ's case 213 were absent
  from the one deck that ships); the v67 migration keeps a converted
  centreline wing mass a point mass; the LRA exporter refuses an unbracketed
  wing station by name instead of a `KeyError`; an SI cell resolves no
  coarser than the Imperial cell it converted from (a 31.2 ft² tail printed
  `3` m²); the live corpus states shipped 0.8.6 and a tier-M closure can no
  longer leave its note at AGREED.
- **Docs-only commits on the branch:** the 2026-09-22 re-cut (B8 re-chartered
  "the deck carries what the airplane carries", #300–#305 filed, rule 6
  applied to #226, #111 and #32) and design note 52 amended and re-agreed
  (D-52.10–D-52.13; the 23.349(a)(2) 75 % correction registered ahead of its
  implementation, #306, with the register's `ships with` marker).
- **Version** `0.8.5` → **`0.8.6`**. Schema **v66 → v68**: v67 at #289 (the
  hop drops `wing_mass.concentrated`, stamps carriage and reports what it
  converted; #296 fixed its stamp order), v68 at #275 (an identity hop on the
  input model — two result dataclasses changed shape).
- **Changelog cut** — `scripts/build_changelog.py 0.8.6 --date 2026-09-23`:
  **19 fragments** consumed — 8 into `## [0.8.6]` directly and **11 history
  entries** rolled to the top of this file, their changelog bullets derived
  from their leads — and a fresh empty `[Unreleased]` opened.
- **Record roll** (`RELEASE_PROCESS.md` §4 step 3): no note moves (note 61
  CV-3). This file stood at 966 lines before the cut and 1,461
  after it; the changelog at 870 and 967. Neither crossed
  1,500, so nothing rolled.
- **Verification baseline** (§4 step 5): unchanged from
  [`36_verification_baseline_0.7.0.md`](36_verification_baseline_0.7.0.md).
  No FAR 23 oracle figure moved: the Appendix A assertions are the same tests
  on the same printed numbers (note 62 G-62.2 locks the six Appendix A wing
  picks by name, #164 re-pins the GA6 conditions at the altitudes the manual
  states). What moved is the delivered set above the oracle — the new slots,
  the per-case mass states, the two-cantilever body, the ATR and heavy
  fixtures, every human-channel digit — each pinned by its own closure gate
  in the notes' §4 tables and regenerated digests, and each recorded in its
  history entry below. A new baseline document would restate 0.7.0's numbers
  verbatim.
- **Gates at cut:** `pytest` **3,742 passed / 9 skipped / 2 xfailed / 0 failed** (3,591 passed / 7 skipped /
  2 xfailed at the 0.8.5 cut), `ruff` clean, `mypy` clean (`sloads/`, 109
  source files), `scripts/smoke_test.sh` **PASS**, `scripts/backlog_issues.py
  check` clean, `scripts/branch_protection_snapshot.py --check`
  matches on 7 tracked keys, the §3.5 by-hand walk done by the owner (2026-09-24), no open CRITICAL/MAJOR review
  findings (the 2026-09-22 review's eleven closed in #294–#299 and #306's
  charter). The **9 skips are fixture-conditional** (§3.3): a parametrized check that a bundled example carries no input for — an entered station table, a WTENV envelope, a fuselage outline, a geometry slice to half-enter — states so and skips, and the three `concept_heavy` LRA skips state the exporter's refusal on a fixture where no side of body resolves (note 64); the set grew by two since 0.8.5 within those. The **2 xfails are the same pair as at 0.8.4 and 0.8.5**: the SI-frame LRA round trips on `concept_regional_jet` and `ga6_normal`, refused by sbeam's dense-path condition heuristic and solving exactly in Imperial (note 55 §8).

**Key decisions.** *A case set is not complete until both sides of it are.*
The band opened on one question — what shape the case set takes — and the
honest answer was three notes deep: a slot for the negative side needs a mass
state to run at, a mass state needs one model that every consumer reads, and
a body that reacts the wing needs a station the beam model actually has. Each
note was PROPOSED and AGREED in session under the solo profile and shipped
within days, with the shipping measurements recorded in the note itself (§8
of note 62, §10–§12 of note 63, §7b of notes 64 and 65) so a decision and its
amendment sit on one page. The second decision was the review's: a band that
has emptied is not a release until a critical read of the whole branch says
so, and this one did not — the coincidence rule on the wrong set would have
shipped a 23.337 design condition to nobody. The round trip cost a day and
six tier-S rows; the alternative was a known-wrong deck under a release tag.
