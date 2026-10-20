  # Changelog

All notable changes to **sloads** (the FAR 23 LOADS replication and
initial-concept distributed-loads tool) are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Live cycle only.** This file holds `[Unreleased]` plus the two newest release
blocks; older ones roll into frozen, do-not-edit archives at a cut (note 61
CV-5): 0.8.7 back to 0.8.4 are in
[`CHANGELOG_to_0.8.7.md`](CHANGELOG_to_0.8.7.md), 0.8.3 in
[`CHANGELOG_to_0.8.3.md`](CHANGELOG_to_0.8.3.md), 0.8.2 and everything before
it in [`CHANGELOG_to_0.8.2.md`](CHANGELOG_to_0.8.2.md).

---

## [Unreleased]

## [0.9.0] — 2026-10-20

### Added

- **The Weight & Mass Properties page shows its totals, its partition by component and every mass-model check, and the envelope figure states its limits in % MAC with the reachable band drawn (#386, tier S, 2026-10-18).** Three read-only tables under the Items grid (`oracle_app.form._mass_database_tables`, a `GROUP_TABLES` builder that may now return several): the data base summed by loading kind with each sum's CG and the design-weight chain's state (`weight_order_chain`); the partition by component the beams read (`mass_distribution.distribution`, which had no GUI caller since #270); and every reconciliation — wing panel tie, fuselage station table, each tail panel, the partition closure, each case loading, the tail surface tags, unplaced rows — with holds / differs and its detail, where the mass is edited rather than only on the Fuselage and Wing pages that read it. The empty Tail Mass table states each surface's derived weight (`derived_tail_surface_weight`). The weight/CG envelope gains a reference line per structural limit labelled in % MAC and the closed band of CG the data base can reach at each entered weight (`envelope_point_reach`), so an unreachable limit is seen, not only warned. GUI_design.md §3 and PROGRAM_SPEC's two rows and merge-write sentence stop describing the retired front-end's tabs and "Apply weight items" handler. The review's B7 — "engines (entered on Engine Mount Loads)" — stands as correct: the weight page's engine dependency is the power rating, which `entering_step` resolves to the later page that enters it, Engine Mount; the engine locations on Geometry are read through the mass rows' selectors, not this read. No load moves; no digest moves.

### Changed

- **Band B2 is re-ordered for the ATR-class objective: #368 and #362 enter at Pri 9 and 10, and the two rule-6 measurements on `atr42_100` run next (backlog amendment, tier S, 2026-10-19).** The owner set the remaining 0.9.0 order by one question — does the row change a load the analysis delivers for an ATR 42-class airplane? The Munk k2−k1 table defect (#368) leads as the one open item with a sourced first-order effect and no owner decision; the overturn-angle citation (#362) follows; then the power-on-balance and body-`Fx` measurement (#226 with #217/#218) and the fuel point-versus-band measurement (#111, whose physics stays in C) decide whether their tier-L steps are scheduled or parked with the number. #32 and #163 stay on 1.0.0. No renumber.

- **Band B2's surviving rows are re-chartered as band B11 for 0.10.0, and 0.9.0 is cut on its delivered-load work (backlog amendment, tier S, 2026-10-20).** 0.9.0 can produce loads for an ATR 42-class airplane and is cut on that work rather than on an empty band. B2's twelve open rows (#185, #92, #130, #209, #226, #304, #246, #355–#359) move under one header, band B11 on milestone 0.10.0, keeping their ordinals, with #226's rule-6 measurement worked first. The ten issues on 0.9.0 with no row (#390, #337, #339, #340, #345, #346, #217, #218, #348, #351) move to 0.10.0 unbanded and are walked at the band's start. No delivered load moves.

- **The CG-case editor is read against its summary and the CG cases can be seeded again (#387, tier M, 2026-10-18)**

- **Fixture mass data agrees with its own mass database, and the links that keep it so exist (#384, tier M, 2026-10-17)**

- **Step — One owner per geometry quantity on the Geometry page: the parametric wing scalars and fuselage summaries deleted, LF and the drag waterline moved to the outline, the control areas derived from the drawn surfaces, an Engines section and a pre-run airplane three-view (#378, design note 69, tier L, 2026-10-16; closes #377, #379, #380, #381)**

- **Step — One owner per mass quantity: the fin's typed design weight deleted, STRSPEED's weight a collapsed override of MTOW, the engine masses derived from their rows on every fixture, the yaw-inertia, wing-mass and fuselage-station overrides on the weight page, the beam waterline and the control-load geometry on the Geometry page, and a wing spanwise-mass figure (#383, design note 71, tier L, 2026-10-18)**

- **The mass three-view: the weight data base placed on the airplane, one bubble per row (#388, tier M, 2026-10-18)**

- **The Munk apparent-mass factor is Lamb's closed form, gated by TR-184 Table I and DATCOM Fig. 4.2.1.1-20a (#368, tier M, 2026-10-19)**

- **Step — WTONECG reports every CG case's loading of record and labels the all-items sum as the database ceiling: per-case mass properties on the page and in the report, the Geometry gear angles per case, one owner for the mass state (#382, design note 70, tier L, 2026-10-17)**

### Fixed

- **The aileron travel is entered in one place, and each deflection says what reads it (#374, tier S, 2026-10-15).** The Aileron Loads page's only deflection widget was SELECT's full-down DN, which feeds the 23.349(b) steady-roll torsion and never the aileron pressures — those read ADEG/AUPDEG on the Geometry page, so changing the widget beside the pressures moved nothing. `select_input.full_down_aileron_deg` now renders on Geometry directly under the aileron travel, each of the three in a titled section whose help names its consumer (ADEG/AUPDEG → AILERON 23.455 loads, ADEG also the roll-torsion default; DN → SELECT/ROLLING 23.349(b) only, blank follows ADEG). Display-only; no delivered load moves.

- **`atr42_100`'s tail surfaces are rebuilt from the airplane's: the fin 125.5 sq ft exposed above the fuselage top line with its root on the body, the stabiliser 125.0 sq ft on its measured 7.23 m span (#389, tier S, 2026-10-19).** Both were statistical entries: a 70 sq ft fin whose root floated 33 in above the fuselage outline, and an 85 sq ft stabiliser on a 220 in span. Two sources close on each other for each surface: the factsheet measurements sconfig's validation rows record (V1.4 fin 125.5 sq ft exposed, no dorsal fin, ±4 %; V1.3 stabiliser span 7.23 m, 125–129 sq ft; [A] p. 4) and the owner's chart planforms (fin AR 1.6 / taper 0.55 / LE sweep 37° referenced to the fuselage centreline, whose part above the fuselage top line integrates to the measured area — a published S_v is to the centreline, 167.1 sq ft here; stabiliser AR 4.5 / taper 0.65, which on the measured span gives 125.0 sq ft). The fin polyline is the exposed part (root 144.1 in, tip 87.2 in, height 156.3 in, sweep 37°, AR 1.35); the stabiliser keeps its root leading edge on the fin tip's so the T-tail root chord sits inside the fin tip chord. The typed tail scalars are re-typed to the polylines' values and both controls keep their chord fractions (SE 26.0 → 38.3, SR 22.0 → 39.6 sq ft). Every delivered ATR tail load moves: the fin cases by about +60 % (YAW 15 NEUTRAL −4,461 → −7,258 lb, SIDE GUST 4,140 → 6,721 lb), the engine-out peaks by +21 % (VD 16,040 → 19,368 lb), the VS engine-out case now recovers (23.6° peak yaw) and is delivered where it ran to the 60 s bound and was excluded (the non-recovery gates run on a constructed ATR with an 8° rudder throw, `tests/fixtures.unrecovered_turboprop`), and every balanced case re-trims on the larger stabiliser. The static directional margin is restoring at twice the body's share (fin −0.00368, body +0.00201, net −0.00167 /deg) where the old fin left 0.00055. The T-tail's induced rolling moments move with `S_H b_H` (the 23.441/23.443 rows about 1.9×, the engine-out rows 1.4×, the 23.427(a) roll −30,622 → −57,894 lb-in, so AC 23-9's 4–6× band still holds at 4.21× / 5.33×; the governing h-tail root bending 233,122 → 329,026 lb-in), the fin-root joint sits at waterline 159.9 where the register had 191.2, and the T-tail tip joint's x-arm closes from −25.6 to −4.5 in with the stabiliser root on the fin tip (notes 51 and 54 carry the re-pins). Imperial digests re-baselined for this fixture alone; the guard pins the fin to the measured area, the published height, the chart sweep and the body top. Found on the way and filed: the ATR's distributed wing lift closes about 2 % short of the balanced point at the stall angle of attack (0.979 at α 20.7°, every stall-parented case), which the newly delivered VS engine-out case exposes against the 1 % one-g closure gate; the exceedance is pinned there with its number.

- **`atr42_100`'s fuselage is the airplane's own: a nose, a cabin, an up-swept tail cone, and a beam on the body centre (#378 part 1, design note 69 D-69.11, tier S, 2026-10-16).** The example described its body with three sections, with full section from station 312 and a straight cone to the tail, and no centre waterline. Its entered fuselage beam waterline (`fuselage_mass.ref_waterline` 179.6) had been copied from the body-drag default, the wing plane, and its sources file called that "the body's own section-centre line". Corrected to the body it described, the two disagreed: the beam ran 16 in above the crown, the high wing's root sat mid-body, and the nose-gear attach hung 12 in below the underside. Changes:
  - **The outline:** 18 sections, sconfig's layout of the same airplane. Length 892.8 in and maximum section 106.3 in are unchanged ([A]); the nose, tail cone and a centre waterline of WL 110.2 rising to 131.1 at the tail are [E]. `fuselage_centreline` now reports an entered line, not an assumed one.
  - **The beam waterline** goes 179.6 → **110.2**, the cabin centreline.
  - **The nose-gear attach** goes WL 50 → **62**, the body's underside at station 95 (owner ruling).
  - **Not changed:** the body-drag line, which stays derived at the wing plane, so no flight-balance or module load moves. The balance spreads the same non-wing drag, at the same waterline, over the 18 body stations instead of 3; its note says so. The only module value that changes is the landing module's nose node z (50 → 62).
  - **What moves is the LRA deck:** 27 GRIDs (the 26 fuselage axis nodes down 69.4 in, plus the nose-gear node), and about 7,300 FORCE/MOMENT cards on the fuselage, redistributed over the new section areas and lever arms. The deck grows from 9,151 to 9,603 lines. Equilibrium closes as before (G-OR-72).
  - **Four tests that had encoded the old body** now state the corrected one. No other example changes. The Imperial digests are regenerated for `atr42_100` only, deliberately.

- **Four mass quantities the Weight & Mass Properties page derives or states instead of asking for (#385, tier M, 2026-10-18)**

- **The GUI review umbrella closes on its two residues: deleted surplus rows no longer return, and the one-basis `channel` parameter is gone (#29, tier S, 2026-10-19).** #29 was re-scoped from the GUI review — the pages are reviewed one at a time, Geometry and Weight & Mass are done — to the two items nothing else covered. The L-8d mutation-half audit read every widget passing both `key=` and `value=` against the four freshness mechanisms `GUI_design.md` §6 now lists and found one live instance: the surplus-delete button ran `del rows[count:]` in its `if` body, so counting back up found the grid's cached frame and editor state keyed to the old count and persisted the deleted rows back — on `ga6_normal`, *Fuel to gross wt* and *Ballast* returned. It is an `on_click` callback that retires the deleted rows' state (`form._delete_surplus`); guard `test_deleted_surplus_rows_do_not_return_when_the_count_goes_back_up`, both table shapes. The CLI-vs-UI check found every registered module on one page and on the CLI, with the intended asymmetries stated in `00_program_overview.md` §Entry points, whose export-target list named six retired targets. `report.LoadChannel` and every `channel=`/`csv_channel=` parameter are removed (note 49 OR-116 had left them one legal value); G-OR-44 now asserts no renderer takes a basis argument and no shipped source names one. No delivered byte moves: the Imperial digests are unchanged.

- **The ATR's 2 % high-α lift shortfall is measured and stated: the strips carry the point's lift, and the gap is the non-wing drag's normal component and the strip-vs-polar angle (#391, tier S, 2026-10-20).** At the #389 close the ATR's distributed wing load closed 2.1 % short of the balanced point's normal force at the stall α, crossing the 1 % one-g gate on its VS engine-out cases. Measured on the four fixtures' stall points: the strip lift recovered at its own angle matches `CL q S` to 0.07 %, so the strip integration, the carry-through and the tip strips are not the cause. The point's normal force `lzw = L cos α + D sin α` carries the **airplane** polar's drag, while the distributed set carries the wing's own drag and `body_axial_set` applies the non-wing drag along `x` only, so `D_nw sin α` reaches the closure (ATR 1.9 % of `lzw`); the strips also resolve at `CL/m − Awo` where the point resolves at the polar's α (ATR 0.4 %; `concept_regional_jet` −3.3 %, which turns its total into a 1.5 % excess). The closure spreads the difference as a uniform load factor, so every deck stays in equilibrium and only the wing/body split moves. Carrying the drag term on the body instead (scratch run, nothing in the tree) moves the governing wing-root bending by at most 0.24 % and the governing body bending by at most 0.62 % on the four fixtures, and one non-governing case by 9.7 % (the ATR's VS engine-out body bending): inside the base-method band, so the carrier is parked with that number (rule 6) and measured with the body-force question it belongs to, backlog Pri 15 (#226 with #218). `CONVENTIONS.md`'s residual bullets state the characteristic; G-66.16's pin keeps its number and now names its cause; a new guard (`tests/test_balance.py::test_the_high_alpha_lift_shortfall_is_the_two_resolution_terms`) holds the statement true — strips equal the point's lift to 0.1 %, and the point's normal and axial forces name one airplane drag larger than the wing's. No delivered load or digest moves.

- **The release tag gate judges CI's run of `main`'s tip, not the newest run of any workflow (#370, tier S, 2026-10-20).** `scripts/branch_protection_snapshot.py --check-main-run` is the §4 step-4 precondition that refuses a red or still-running run on `main` before the tag (#184). It read `actions/runs?branch=main&per_page=1`, the newest run of *any* workflow, and at the 0.8.9 tag answered "run (`sbeam drift`) completed green — clear to tag": the CI run of record happened to be green, but a red or unfinished CI would have passed the gate behind any later green run of the scheduled drift workflow. The fetch is now the CI workflow's own runs endpoint (`CI_WORKFLOW = "ci.yml"`), the branch tip is read beside it, and the verdict (`judge_main_run`, credential-free) clears only a completed, green run **of the tip** — a green CI run of an older commit, which a tag could otherwise sit on, is refused with the reason. Guards in `tests/test_ci_conformance.py`: six verdict cases, and a source check that the fetch names the CI workflow and the tip and no longer the all-workflows endpoint. The sweep found the close-time CI check (`ci_state.py`, `solo_close.sh`) already filtered to `ci.yml` and judged the pushed tip (#329). Rider: `ci.yml`'s "~7.3 min" advisory-gate comment is re-dated — branch runs measured 36–68 min in 2026-10. `RELEASE_PROCESS.md` §4 step 4 states what the check refuses. No calc or delivered output changes.

- **The landing-gear angles are read against cited design guidelines: overturn ≤ 55° on a hard surface, tip-back ≥ 15° (#362, tier S, 2026-10-20).** The configuration page's gear condition compared the overturn (lateral tip-over) angle with an uncited "~63 deg", which is Roskam Pt IV Fig. 2.48a's land-based US Navy entry, and its tip-back minimum with an uncited "~15 deg". Both numbers now have one owner in `constants` (`GEAR_TIPBACK_MIN_DEG`, `GEAR_OVERTURN_MAX_DEG`, `GEAR_OVERTURN_NEVER_DEG`), the note states them with their sources (Roskam Pt II p. 218 and Fig. 9.1a p. 219, Pt IV Fig. 2.48a p. 76; Torenbeek §10.3.2 pp. 352–353, 55–57° a maximum safe limit and never over 60°; Raymer 4th ed. §11.2 p. 265) and says they are guidelines, not requirements, whose exceedance raises operational risk rather than failing the design. A hand check of the overturn geometry (ψ = atan(h_cg / (l_n sin θ)), 60.11° on a stated gear) gates the formula with the page cited. No load moves; the guideline sentence enters the configuration text report, so the Imperial baseline's `txt/configuration` digest is re-pinned on the four gear-carrying examples (D-21, intended). Read against the new guideline the fixtures stand at: `atr42_100` 64.1° (above even the old 63°; the real airplane's 4.10 m track against the fixture's deserves a look with the #226/#111 measurements), `ga6_normal` 52.9°, `baron_58` 50.5°, the RJ 46.3°.

- **The 0.9.0 pre-release review's findings are closed: the wing spanwise-mass figure names each curve only by the cases that carry its point masses, #385 is recorded as the tier-M change it is, and nine residues are swept (#392, tier S, 2026-10-20).** The figure grouped FLIGHT cases on the panel weight alone, so on `atr42_100` (eight cases, one panel, two point-mass sets) and `baron_58` one case's wing fuel was drawn under the zero-fuel and minimum-weight cases' names; it now groups on the panel weight plus the point-mass set, and `test_the_wing_mass_span_figure_names_each_curve_only_by_cases_that_carry_it` holds it, refusing to pass vacuously. #385 moved the ATR's peak fuselage load on the wing −9.4 % and was closed at tier S; its fragment is now the tier-M history paragraph. The residues: the Tail Mass note states the derived surface weights in the page's own units; list-row ownership (D-69.14) is kept in the session's state, not shared module state; the Ch 9 wing-weight stand-in is one constant in `constants.py`, read by SELECT's fuselage conditions and its rod-estimate IZZ alike; a duplicate projection helper is gone; PROGRAM_SPEC, the fin-root docstrings and four comments are corrected after the v77–v80 moves, and PROGRAM_SPEC states the sbeam SI xfail as it is (two decks, by name). Fragment lead phrases use the `(#N` form, with two dates corrected. No delivered load moves.

- **The parametric-wing seed button keeps the values it shows (#376, tier S, 2026-10-16).** "Seed from the wing planform" named the planform's area, AR, taper, LE sweep and LE root station and then left every field at 0: it wrote them in the button's `if` body, the block's number widgets — drawn on the pass before the click — kept their retained `0.0`, which outvotes `value=`, and the render persisted that over the seed in the same rerun. The write is now an `on_click` callback that also drops each seeded field's widget state (`form._seed_record`, the `_seed_rows` remedy of the 0.8.4 closure review, the same class), so the fields re-seed from the record. The class sweep found no other live instance: every other button that writes in its `if` body either replaces the project (a generation bump), reruns before any of its fields render, or — "Switch to Concept" — is never offered by the oracle GUI. Guard: `test_the_record_seed_keeps_the_values_it_offers` clicks the seed on a drawn block in both unit systems and fails on the old code with `0.0`. No delivered load moves. The button itself retired later in this release with the parametric wing scalars it seeded (#378, design note 69).

## [0.8.9] — 2026-10-04

### Changed

- **The Baron's POH limit load factor of 4.2 is entered as its chosen n, so condition A flies at the factor its engine-mount cases scale to, and a typed LIMNZ that disagrees with the airplane's n₁ now warns (#331, tier M, 2026-10-03)**

- **CI runs on a pinned `ubuntu-24.04` image and on the Node 24 action majors (`actions/checkout@v5`, `actions/setup-python@v6`) in both workflows, and a guard refuses a floating runner or a Node 20 action (#363, tier S, 2026-10-04).**
  `ubuntu-latest` moves to Ubuntu 26 on 2026-10-19 with no commit in this
  repository to point at, so a red after that date could not be told from a
  code regression, and the first run on the new image would have been the
  0.8.9 release cut's push to `main`. The Node 20 runtime of `checkout@v4` and
  `setup-python@v5` is deprecated, and every run since the 0.8.8 cut carried
  the annotation. Moving the image is now a deliberate edit.
  `tests/test_ci_conformance.py` checks every workflow: every `runs-on` must
  be a pinned `ubuntu-NN.04`, and every action must be at or above its floor in
  a total per-action table, so an action added later has to be decided there.
  No calc or delivered output changes.

- **The one-engine-out low end takes an entered VMC and flies at the take-off altitude, an unrecovered case is stated wherever it would have appeared, and every 23.367 case is sized at the heaviest FLIGHT loading instead of the all-items one (#333, tier M, 2026-10-03)**

- **A rotor's spin sense is its signed rpm alone, and the sudden-stoppage torque reads the same signed spin momentum the gyroscopic cases do, so a mirrored engine publishes the exact negative (#332, tier M, 2026-10-03)**

- **Step — sloads complies with sstandards Rev B: a conformance test checks sloads' own owners against the vendored vectors, `CONVENTIONS.md` states compliance with the deviations D-SL1 and D-SL2, and the standard's §8 row cites #354 (#354, design note 68 D-68.1…D-68.10, tier L, 2026-10-04)**

- **Step — A T-tail's horizontal tail carries the AC 23-9 induced rolling moment: each fin condition carrying it gets its own horizontal-tail condition, the deck applies the moment on the horizontal tail rather than as a fin-tip couple, and the one-engine-out march reads an entered windmill drag coefficient (#334 with #335 riding, design note 51 D-51.12/D-51.4b/D-51.7a/D-51.13 and design note 66 D-66.12b, tier L, 2026-10-04)**

### Fixed

- **The ATR's tailplane dihedral is 0°, owner-supplied, and the unsourced claim that the real ATR 42 shows visible dihedral is withdrawn (#336, design note 51 D-51.9, tier S, 2026-10-04).**
  No published value was found. The owner supplied 0°, cross-checked against
  ATR's 42-300/-320 brochure front elevation, which draws none (the tailplane
  centreline rises one pixel over its semispan). Recorded in
  `atr42_100.sources.md`. D-51.9 closes, and the dihedral warning stays gated
  on G-51.10's constructed project. No load or fixture value moves.

- **Every case-id band has a stated top edge, and a band that fills is refused by name instead of minting the next band's ids (#366, tier S, 2026-10-04).**
  `tail_span` minted `HT-{20+k}` per T-tail induced-roll carrier (#334) with
  `k` unbounded, so a 31st carrier would have minted `HT-50`, the tab band's
  first id, and corrupted the case index and the deck's subcase numbering
  without a word. The same shape was in `wing_inertia`'s hand-authored extra
  band, and every allocator band was open at the top. `case_ids.BAND_LAST` is
  now the one owner of each band's edge: a band ends where the next starts,
  and the last ends at the 100-wide subcase block. Both the allocator and the
  new `band_case_id` read it. A drift guard refuses an id formatted by hand
  from `COMPONENT_PREFIX` outside `case_ids`. The fullest band in any shipped
  example reaches 33 of its 99. No shipped fixture or delivered load moves.

- **Every engine rpm, weight and diameter is refused by name unless zero or positive, and a hub heavier than its propeller is refused (#364, tier S, 2026-10-04).**
  The #343 sweep stopped one field short. A negative `takeoff_rpm` or
  `max_cont_rpm` reversed the stoppage torque and the gyroscopic couples, a
  second spin-sign owner beside `prop_direction` (the #332 class). A zero rpm
  divided by zero in the reciprocating torque from horsepower, where it is now
  refused unless positive. A negative propeller, hub, engine or rotor weight,
  diameter or measured rotor inertia reversed an inertia load. A hub weight
  above the propeller weight gave the blades a negative inertia. All of these
  now go through the same `_positive` refusal as the #343 fields. Zero stays
  admissible wherever it means *none*: the regional jet's fans enter no
  propeller. No shipped fixture or delivered load moves.

- **Five nits from the 0.8.9 pre-release review: warnings number engines from 1, the silent-refusal guard sees a multi-statement body, the validation march states its cost, an entered VMC is tested through the deck, and a doubled word is gone (#367, tier S, 2026-10-04).**
  The windmill-coefficient warning and refusal named an engine `engines[0]`
  while the #331 warning said `engine 1`. Every warning and refusal now names
  it through one owner, `engine.engine_name`: one-based, with the
  designation, as the engine-loads section and the case labels number it
  (#231). The #344 AST guard scanned only one-statement handler bodies, so
  `x = []` then `continue` would have landed unflagged. It now scans a body
  of any length, and a probe test keeps that edge closed; no unstated catch
  surfaced. `_check_oei_not_recovered` re-runs the ONENGOUT march because
  `Project` publishes no result to read. The cost is stated where the check
  lives: 5 ms on the ATR and 9 ms on the Baron, against 0.27 s and 0.14 s for
  the whole validation pass. A deck-level test enters the Baron's published
  VMC (84 KIAS) and asserts that the pair reaches the deck on the same 1 g
  stall point as VS, not on VC's. No shipped fixture or delivered load moves.

- **A refused input is now stated as a refusal: a broken wing is no longer reported as a missing one, the flap gust factor's fallback to NG = 0 is warned and stated, and the report says when entered inputs were refused (#361, tier S, 2026-10-04).**
  The #344 sweep found four places where a refusal was reported as a different
  fact. `derived_geometry.require_wing_reference` now re-raises an
  unintegrable planform's own `ValueError`, so the user sees "needs >= 2 LE and
  TE points", not "add the surface". It raises `MissingInputError` only for a
  wing that is not there. A blank flap `gust_load_factor` that the flight
  envelope cannot derive still stands at 0. That makes the 23.345 gust at VF
  condition non-critical, and it is now stated: `flap.ng_fallback_reason`
  names why (from `flight_envelope.gust_at_vf_absence`, the same walk as the
  derivation), the flap result's note says so, and `validation` warns
  `flap_ng_fallback`. Only `atr42_100` falls back, and only its flap note text
  changes. Its 2g condition at VF governs the critical flap load at NG = 0 and
  at the 1.64 estimated from its flaps-up slope alike, so no delivered load
  moves (owner ruling (a): state the fallback, change no data). Three groups of
  report sections now quote a refusal in the #316 `REFUSED_REASON` shape, in
  place of a false "not entered": the tail chordwise, spanwise and station
  appendix; the aileron, flap and tab sections; and Appendix A. Appendix A
  also says whether the flight envelope refused or only the critical-condition
  selection did. The 2.2 case-loading and envelope-reach statements state a
  refusal instead of vanishing. Gate: `tests/test_refusals_stated.py`. The
  Imperial baseline moves on one channel, `atr42_100` `txt/flap`.

- **A refused input no longer goes silent: the T-tail checks say they could not run, a refused engine or one-engine-out family is recorded in the deck, and the dihedral warning reads the entered field (#344, tier S, 2026-10-04).**
  The T-tail induced-roll check returned no warnings at all when the spanwise
  tail build refused its input, and its dihedral warning fired only when a fin
  condition resolved. The engine-mount and one-engine-out deck families were
  emptied, unrecorded, when ENGLOADS or ONENGOUT refused. Each now states the
  refusal — `ttail_induced_roll_unchecked` on the tail page, a `family-refused`
  entry in the record of conditions not assembled — and the dihedral is read
  through one typed reader, `tail_geometry.htail_dihedral_deg`. The sweep
  found three more of the class, now refused by name: ONENGOUT read a refused
  STRSPEED input as "no VS" and dropped the 23.367 low-end case (and flew a
  refused engine on the right-hand fin sense), and a tail outline entered but
  not integrable read as "no planform entered" or an elevator of area 0. Every other
  silent `ValueError` catch in `sloads/` states its reason
  (`# refusal:`), held by a new AST guard. No shipped fixture or delivered
  load moves.

- **The speed derivation is proved to refuse only by name, so the one-engine-out family cannot crash on a zero wing area (#365, tier S, 2026-10-04).**
  The 0.8.9 pre-release review asked whether the #344 narrowing of ONENGOUT's
  VS read to `MissingInputError` let a `ZeroDivisionError` escape to the deck
  build. It cannot: `design_speed_values` refuses a non-positive weight, the
  WINGGEOM integral refuses a degenerate or zero-area planform before it
  divides, `stall_speed_kt` refuses a negative typed area, and the atmosphere
  is positive at every altitude. The contract is stated on the function, the
  three dead `ZeroDivisionError` catches around it in `validation.py` are
  removed, and a guard test drives each degenerate area to its named refusal.
  No shipped fixture or delivered load moves.

- **An entered windmill drag coefficient must be positive, and one above the Glauert bound is warned with both numbers; every entered engine magnitude is refused by name unless positive (#343, tier S, 2026-10-04).**
  A negative `windmill_drag_cd` delivered a forward thrust at the failed
  engine's hub in the balanced one-engine-out cases, and zero delivered no
  drag; either closed as cleanly as a right value. Both are now refused by
  name before any case is assembled, and warned on the engine page
  (`windmill_drag_cd_range`); a value above the bound the manual says the drag
  cannot exceed (0.502) is delivered as entered and warned. The same class
  swept through ENGLOADS: `takeoff_hp`, `max_cont_hp`, `max_engine_torque`,
  `cruise_torque`, `stop_time_s` and an entered `max_accel_torque` are refused
  unless positive (a zero stoppage time divided by zero), and an entered
  `prop_inertia` unless zero or positive. No shipped fixture or delivered load
  moves.

## [0.8.8] — 2026-10-03

### Breaking

- **sloads requires Python 3.12, and the developer's gate, every pull request and the push to `main` run that one interpreter (#327, tier M, 2026-09-28)**

### Added

- **Step — The beam model reaches the GUI: a Beam Model page shows its axes, owns its mesh, draws it and writes the deck with the operating empty weight's mass set beside it, every drawing is drawn to scale, and a stray keystroke can no longer commit 4,501 rows (#283 with #244 riding, design note 67 D-67.1–D-67.12, tier L, 2026-10-01)**

- **`solo_close.sh` reads CI on the branch's pushed tip before its gate and refuses a close while it is red (#329, tier S, 2026-09-28).**
  The 0.8.7 milestone was red on `dev/v0.8.7` from #286 to the release cut
  (#324, a byte every local gate passed) because nothing read the branch's CI
  between closes. #327 made the developer's interpreter CI's; this closes the
  rest of the gap. In preflight, before the gate, the script lists the
  branch's `ci.yml` runs and `scripts/ci_state.py` judges the one for
  `origin/<branch>`. Only that run counts, because `ci.yml` cancels a
  superseded commit's run. A `failure`, `timed_out` or `startup_failure`
  refuses unless `--ci-red-ok "<reason>"` is given, and the reason goes into
  the commit body; that is how the close that fixes the red goes in. A run
  still going, no run yet, `cancelled`, or an unreadable answer warns and
  carries on. The check runs whenever `gh` is authenticated, with or without
  an issue number, and says "CI unread" when `gh` is not. Riders from the #327
  review in `tests/test_ci_conformance.py`:
  - every interpreter `ci.yml` names, the `typecheck` job's scalar
    `python-version` included, is one the `test` job runs;
  - no current-truth doc names another, except an allowlisted mention with its
    reason: the retired 3.10/3.11 legs and branch coverage's CPython 3.14 in
    §0.

  `CONVENTIONS.md` §7's `math.fsum` rationale no longer lists interpreters.
  The verdicts are tested from JSON alone in `tests/test_solo_scripts.py`,
  with no credentials.

- **Step — A T-tail's fin carries the horizontal tail's asymmetry: the AC 23-9 induced rolling moment in every fin condition, one-engine-out included, and the 23.427(a) case through the fin, with the horizontal-tail assumption checked (#328, design note 51 D-51.1a–D-51.11, tier L, 2026-09-29)**

### Changed

- **The calc package writes no digit count of its own: every number in a result note, a validation warning or a condition title prints at its unit's row, and note 65's gate scans all of `sloads/` (#312, tier M, 2026-10-01)**

- **Step — The engine axial loads of both deck families: the one-engine-out hub carries the propeller's own windmill drag when entered and the stated Glauert bound otherwise, and every gyroscopic case applies every engine at one airplane state (#319, design note 66 D-66.12a/D-66.4a, tier L, 2026-09-29)**

- **An envelope point no loading can produce is flagged: every entered CG limit and weight/CG case is tested against the loadings the database can hold, `baron_58`'s forward-regardless limit is the one that fails, and its `fwd gross` reaches the deck as an entered loading (#309, tier M, 2026-09-29)**

### Fixed

- **SELECT's accelerated-roll pick is no longer decided inside the balance's tolerance: roll points whose wing lift ties to 0.5 % go to the larger net root bending (#320, tier S, 2026-09-29).**
  SELECT took the `AC ROLL` point with the largest `LZW`, and the points it
  chose between differ by less than FLTLOADS balances to (0.04–0.41 % on the
  fixtures against 0.5 %), so any change to the iteration could move the slot
  and every digest that reads it. Points within `select.LZW_TIE_REL` (the
  balance's `NZ_BALANCE_TOL`, as a fraction of the lift) of the largest are now
  one lift, and the tie goes to the point whose net root `Mxx` — the variant row
  the slot would deliver, through the new `wing_variants.Assessor`, the one row
  builder the table also uses — is the largest; a project without a wing model
  keeps the largest `LZW` and its `ACRL` note says so. `ga6_normal`,
  `atr42_100` and `concept_heavy` deliver the same case (the GA6's Appendix A
  pick stays at sea level, 400,817 against 400,315 lb-in). `concept_regional_jet`
  moves from V-n case 180 (20,000 ft) to 40 (sea level), root `Mxx`
  5,486,079 → 5,527,521 lb-in (+0.76 %); `baron_58`'s mzfw aft row moves from
  case 80 (sea level) to 180 (10,000 ft), +32 lb-in (+0.006 %). Imperial digest:
  12 regional-jet channels and 7 Baron channels. From #321: `Δcm = −0.01·δ` is
  `constants.AILERON_DCM_PER_DEG`, the CAM 3.222 schedule is one function
  (`aileron.cam_3222_deflection`) that AILERON and the steady roll call with
  their own speeds, and a project with no category or a wing with `Iwxx = 0`
  is refused by name, no longer given the normal rule or a zero roll
  acceleration.

- **The mass tolerances are read through their owners, the FAR 23 exceedance line states its unit, §2.2 groups its checks by a field, and the one-engine-out yaw figure is signed like the fin load beside it (#321, tier S, 2026-10-01).**
  The remainder of the 0.8.7 review's calc-side minors; the engine items rode
  #319 and the rolling/select items #320. `validation` rebuilt the entered-loading
  weight band from `mass_distribution`'s two private halves and read its private
  `_CG_MATCH_TOL`, the owner did the same inside `case_loading_checks`, and the
  oracle report imported `_ECHO_WEIGHT_REL` to print "0.1 %": all now call
  `echo_weight_tolerance()`, `cg_match_tolerance()` and the new
  `echo_weight_rel()`, and `tests/test_mass_distribution.py` refuses any module
  outside the owner that reads one of the private names. The mirror-pair test
  has its own `_MIRROR_POSITION_TOL` (0.5 in, the hand-entry resolution, owner
  2026-10-01) instead of borrowing the CG search's band. `Exceedance` carries
  its `dim`, and `report.methods.exceedance_statement` is the one wording the
  methods block and the GUI banner print: an SI file's comment block said
  `20,000 exceeds the limit of 12,500` with no unit and now says
  `9071.8 kg exceeds the limit of 5669.9 kg`; both note 65 exemptions are gone.
  That unit exposed a defect it had been hiding: `package_data.data_header`
  built each `data/` file's methods block without the document's system, so
  every file of an SI issue package stated `UNITS: Imperial (lb, in, lb-in,
  lb/in^2) throughout` above its SI numbers. It now passes `doc.system`, and
  `tests/test_si_artifacts.py` checks each file's `UNITS:` line in both systems
  (the leak scan reads numbers with a unit after them and could not see it).
  `MassCheck.case` names the case a per-case check is about, so §2.2 no longer
  `rsplit`-parses the display string. The OEI yaw figure drew the march's
  magnitudes beside a fin load signed by the failed engine's side; yaw angle and
  rate now read nose to port positive (SELECT's β) and the rudder in the sense
  that loads the fin `+y`, stated in the caption (owner option (a)). BALANCE
  passes its resolved envelope to `default_critical`. No delivered load moves.

- **A non-finite number cannot reach a delivered deck: the card formatter refuses a NaN or an infinity by name, as every other delivered channel already does (#341, tier S, 2026-10-03).**
  `%E` of a NaN is the string `NAN`, and `deck_format.fmt` had no finite
  guard, so the solver channel — the primary deliverable — was the one
  channel that would print an upstream defect into a shipped `.bdf` while
  the Beam Model page showed the success toast (`units.format_value` has
  guarded every human/CSV cell since #303/#316). `fmt` now raises
  `NonFiniteValue`, and because every `.bdf` writer formats its card values
  through `fmt`/`fmt3`, the single raise covers the package. `fmt3` refuses
  before its dust snap, where the guard found a second path worse than the
  first: an infinite component is also the card's own scale, so `snap_zero`
  floored every component against it and the card printed all zeros —
  silently. Found by the 0.8.8 pre-release review.

- **The capability summary and the report standard state the delivered basis the code ships: LIMIT, with the factor stated and applied nowhere (#342, tier S, 2026-10-03).**
  Three current-truth documents still carried the contract note 49 OR-116
  reversed — `CAPABILITIES.md` ("Everything deliverable is ULTIMATE … the
  safety factor is applied once at the render/export boundary", plus the five
  per-component decks note 56 deleted and the `ULTIMATE twin` OR-81 retired),
  `SUMMARY_REPORT.md` §5's exclusion row ("The deliverable is ultimate
  throughout") with its §4.6 and SI-marker siblings, and
  `ch09_balanced_airplane.md`'s units line ("applied once at the export
  boundary") — so the first document a new reader opens told an analyst not
  to apply the factor the deck did not apply. All three now state the shipped
  contract, and the class is structural (rule 3):
  `tests/test_doc_currency.py` scans every current-truth doc,
  `CAPABILITIES.md` included, for the retired-contract phrase class — which
  found the `ch09` instance the hand sweep had missed, on its first run.
  `90_record/` stays out of scope, where the sentences state what was true on
  a date. Found by the 0.8.8 pre-release review.

- **The engine-installation views name each thrust line by its engine's number, state each designation once, keep the legend inside the text, and mark coincident application points once (#256, tier S, 2026-10-02).**
  Found building the ATR-42 issue package (2026-09-09 review §3 A3). Each
  thrust line's legend entry carried the engine designation -- "PRATT &
  WHITNEY CANADA PW120 (LH) thrust line (ASSUMED)" -- and two of them side by
  side were a 167 pt overfull box on all three views; on the Baron and the
  regional jet, whose engines share a designation, the two rows were
  identical and named neither arrow. `derived_geometry.engine_thrust_segments`
  now labels each "Engine N thrust line", matching its numbered marker, and
  the caption states "Engine N is the <designation>" once per engine. Both
  engines sit at one (x, z) in side view, so marker "2" printed over "1":
  `PlotData.marked_points` merges points within `COINCIDENT_REL` of the
  figure's span into one marker labelled "1 / 2", and both renderers --
  `plots_tex.plot_tex` and `app_shell.plots.plot` -- draw it, so the screen
  and the page agree. The weight/CG envelope's own copy of the merge
  ("CG3 / fwd light") is retired into it, keeping its separator. Sweeping the class, `plot_tex` drops any legend to one
  column when its longest entry cannot share a row
  (`_LEGEND_TWO_COLUMN_CHARS`). No delivered load moves.

- **The note 66 and note 52 gates compare against figures that do not share the code's derivation, and G-66.5 is the gate the note agreed (#318, tier S, 2026-09-28).**
  The 0.8.7 review found gates that re-derived what they checked (P-2). G-66.5
  now assembles each engine-mount case's parent itself, scales it by hand, and
  finds it load for load at the head of the case with only the engine increment
  and its relief after it. Before, it checked a closure true by construction
  and skipped every gyroscopic and inclined-torque case. G-66.3 pins each case's
  load factor from the rule and the engine's entered `limit_load_factor`, not
  from ENGLOADS's vertical ÷ PPWT. G-66.1 pins 1.0 on 23.367(a)(2) and 1.5
  elsewhere, not the safety-factor table the stamp itself asks. G-66.10 compares
  the reflected twin, load for load at rel 1e-9, with the mirrored engine's case
  built directly from its own march (6e-15 on both twins), and its engine pair
  with `engine_forces_at`. The report's OEI butt-line checks compare against
  the entered `engine_cg` rather than the side owner under test; the printed
  butt line itself is unchanged (−66/+66 in on the Baron, −161/+161 on the ATR,
  the entered positions — #285 reversed the fin-load sign, not this). Note 52's
  delivered condition A root and aileron deflection are asserted against the
  print (+516,955 lb-in p. 206, 10.703° p. 93, ±0.1 %), the literal-arithmetic
  knit test is removed, and note 52 states that G-52.4/G-52.11 are
  characterization pins under the amended 75 % rule. From #322:
  `test_rolling_conditions.py` gains its `__main__` runner, loses its
  `sys.path` shim and states UNB with its sign, and the ENGLOADS test name is
  spelled right. No delivered load moves. Found on the way and filed for the
  owner: `baron_58`'s engines enter `limit_load_factor` 4.2 against the
  airplane's 23.337 n₁ of 3.648, so its 23.361(a)(1)/(a)(2) cases fly the
  airplane at 3.15 / 4.2 g.

- **An override cross-check warns only on a difference it can show: one owner judges the disagreement at the ±0.1 % band and the printed digits, and an exact-equality check prints its drift apart (#243, tier S, 2026-10-02).**
  The 2026-09-08 GUI review (G6) found the form's override warnings firing on
  any difference above `1e-9` and printing both numbers at four significant
  figures -- "This is 0.4356 but the paired planform's tip/centreline chord
  says 0.4356" -- and a 0.02 % aspect-ratio rounding flagged with the weight
  of a real data error. The new `sloads/cross_check.py` owns the comparison:
  `cross_check_disagrees` warns only past `CROSS_CHECK_REL` (0.1 %, the
  oracle band) **and** when the warning's own formatter prints the two
  differently. Both `oracle_app/form.py` warnings call it, and so, sweeping
  the class, do `validation`'s `aileron_deflection_mismatch` and
  `engine_mass_row_mismatch`, which compared at `1e-6` and printed at the
  unit's row. The two exact-equality checks, `landing_case_weight_is_mlw`
  (G-4) and `mtow_representation_drift` (G-14), still warn on any
  difference, but print through `shown_apart`, so a 0.4 lb drift reads
  `5000.0 lb ... 4999.6 lb` rather than `5000 lb ... 5000 lb`. The wing-area
  (5 %) and hinge-halves (1 %) checks keep their stated bands.
  `tests/test_cross_check.py` pins the review's pairs and walks both files'
  ASTs, refusing a near-zero `abs(a - b) >` test unless its function prints
  through `shown_apart`; `CONVENTIONS.md` §7 gains the owner's row. No
  delivered load moves.

- **A half-entered h-tail, landing gear or negative stall CL is refused by name instead of stopping the report with a bare ZeroDivisionError, and no handler in `sloads/` swallows a calc defect (#330, tier M, 2026-09-28)**

- **A NaN or a calc defect no longer ships as an absent section or a missing package file, and a section the analysis refused says why instead of "not present" (#316, tier S, 2026-09-28).**
  Twenty-one handlers in `sloads/report/` caught `Exception` — `package_data.add()`
  and its two siblings, fourteen section helpers in `oracle_sections.py`,
  `run_sections` and the GUI's `figures.results_for_step` among them — and
  `NonFiniteValue` was a `ValueError`, so the ~30 handlers #303 had narrowed to
  `ValueError` could catch it too. A NaN bound for a delivered cell dropped its
  file from `data/` without a word, a calc defect printed as an absent section,
  and a section whose inputs were present but refused (a curve half entered, an
  area typed as zero) told its reader the inputs "are not present in the
  project". Now `report.render.REFUSALS` — `MissingInputError` and a plain
  `ValueError`, the two halves of the error contract — is the one owner of what
  a report or package path may read as an absence, and every one of the
  twenty-one catches it and nothing wider; a report built mid-entry keeps
  building (#71). A section absent by a `ValueError` states the module's own
  message after `oracle_content.REFUSED_REASON` (on `ga6_normal` with a
  one-point wing leading edge, sections 6.3, 7, 11, 12 and 16 now say so).
  `NonFiniteValue` derives from `Exception`, so no refusal handler can catch
  it, and the package build re-raises it naming the file; any other exception
  stops the build by name. The six "no … loads to export" raises in
  `report/applied.py` are `MissingInputError`, which is what they are, and
  `applied.py`'s guard around the total `fuselage_lra` is removed. Guard:
  `tests/test_report_absence.py` (no report or export handler can catch
  `NonFiniteValue`; a NaN stops the package naming the file; a refused input is
  stated; a `KeyError`, `ZeroDivisionError` or `NonFiniteValue` from a module is
  neither an absent file nor an absent section). No delivered byte moves on the
  shipped examples. The contract is stated in `00_program_overview.md` §Error
  handling.

- **The 2026-09-08 review's report-polish rollup is closed: one moment unit, a side-load row that names its wheel, labels that do not stack, captions that describe what is drawn, a true airspeed tagged as one, the pitch inertia's basis stated, a references list, and appendices that promise no row they do not print (#240, tier S, 2026-10-02).**
  Each of R13-R23 read against the 0.8.8 report. **R13:** the engine-mount
  moment and torque columns were the document's one ft-lb channel; they are
  stated in lb-in like every other moment, and the torque note says the oracle
  prints them in ft-lb. **R14:** the per-wheel table's note says each 23.485
  row is one main wheel -- the odd case the 0.5 W inboard wheel, the even the
  0.33 W outboard -- and that the other wheel's is its partner's. **R16:**
  `plots_tex`'s label placer scores a label against the labels already placed,
  scales its footprint to a drawing's own aspect, and steps a crowded label out
  onto a leader line; the ground attitudes' three landing-CG labels no longer
  stack. **R18:** the engine views' caption said every arrow ran from the
  mount node to the hub, which an ASSUMED arrow does not, and told the reader
  to enter the propeller CG to replace one; it describes both kinds of arrow
  and names the thrust line's two points. **R19:** the tail appendices said
  their rows were strips followed by control and T-tail transfer nodes, rows
  note 56 D-56.9 folded into the grids; the sentence says so, and names the
  transfer only on a T-tail. Appendix B states that W-50 and up are the
  aileron's, flap's and tabs' ids, from `case_ids`' bands. **R20:** the speed
  of sound is tagged `kt(TAS)`, a new unconverted row beside `kt(EAS)`, not
  "633 kt(EAS)"; the frozen Imperial baseline is regenerated for it, and the
  only channels that move are each example's `csv/` and `txt/`
  `structural_speeds`, by that unit tag alone. **R21:** a comment said SELECT reads the h-tail pitch inertia
  from the weight database "in every case" and suppressed its basis; it is
  always the rod estimate x 0.44, and the state table says so beside the
  v-tail's yaw-inertia statement. **R22:** "Reference 1" is defined in a
  References subsection owned by `report.methods.REFERENCES`. **R23:** the
  fuselage Sz/Myy captions say "every curve", and Appendix A states that its
  nineteen columns are printed as two tables. R15's empty continuation page,
  R16's mass labels and R23's lowercase lead no longer reproduce.
  `tests/test_oracle_report_polish.py` pins each. No delivered load moves.

- **An SI artifact states every number in SI, its prose included: provenance notes carry their quantities live and render in the channel written to, a persisted record keeps its numbers in values, and case names stay identifiers (#338, tier M, 2026-09-30)**

- **A test file's self-runner starts, every test file has one, CI cannot drop the slow lane in silence, a misspelt marker is an error, and a released file's values survive the read (#322, tier S, 2026-10-02).**
  The remainder of the 0.8.7 review's test-infrastructure minors; the
  ENGLOADS spelling and `test_rolling_conditions.py`'s items rode #318. The
  three memoised builders in `tests/test_deck_basis.py` handed out a shallow
  copy whose `ModuleResult`s every test in the worker shared; they now return
  `copy.deepcopy`, and a test edits one and reads the next caller's.
  `addopts` gains `--strict-markers`, and `tests/test_ci_conformance.py`
  refuses a `ci.yml` pytest step that deselects `slow` or selects any marker
  but the solver job's `roundtrip`. The shadowed first copy of
  `test_every_example_round_trips_unchanged` is deleted, so the file's section
  headers match its docstring. Five test files gained the `__main__` runner
  CLAUDE.md requires, and sweeping that class found the runners that existed
  broken: 26 passed `-p no:xdist`, which unloads the plugin that owns
  `addopts`' `-n auto`, so each failed at startup with "unrecognized
  arguments: -n". They pass `-n 0`, as `pyproject.toml` and
  `00_program_overview.md` now advise, and a guard requires a runner in
  every `tests/test_*.py` and refuses `no:xdist` in one. The frozen
  `release_<X.Y.Z>.json` test checked only that the file loads, which a hop
  missing a later rename passes because the reader drops unknown keys; a new
  test requires every scalar of the migrated file back at its path with its
  value. No delivered load moves.
