# Completed Development

The authoritative record of what has shipped: completed modules/phases, key
decisions, and resolved defects. Items move here from
[`../30_future/00_backlog.md`](../30_future/00_backlog.md) the moment they close,
with a matching `CHANGELOG.md` entry.

Each entry uses the step format: **Objective**, **Deliverables**, **Test /
Acceptance**, **Key decisions**.

**Live cycle only.** This file holds the current release cycle plus the previous
release cut. Older blocks roll into frozen, do-not-edit archives at each release
(`RELEASE_PROCESS.md` §4): the 0.8.1 cycle and the 0.8.0 cut are in
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

## Release cut: **sloads 0.8.2** (the oracle technical report, LIMIT with the factor stated), tag `v0.8.2`, 2026-09-08

**Objective.** Close band **B3** — the oracle technical report (design note 44,
milestone row #151): a clean, modern formal LaTeX report of the oracle GUI's
analysis, generated from a new `oracle_app` page, built one owner-agreed
iteration at a time under the OR-13 freeze (solver and existing oracle GUI
frozen additive-only, a hashed manifest, defects in frozen code filed not
fixed, OR-15 the sole admission mechanism).

**Deliverables** (the `[0.8.2]` changelog section is the release note):
- **The report, whole:** iterations 1–10 all shipped — front matter and the
  issue-package build (`ReportSpec`, fingerprint provenance, `MANIFEST.txt`);
  §2 Loads Configuration with the planform, weight-envelope and V-n figures;
  §3 Wing Loads + Appendix B (applied split from carried); §4 Fuselage Loads +
  Appendix C (the p198 conditions published, the carry-through entered as a
  station, notes 46/47/48/50); §5/§6 the two tail sections + Appendices D/E;
  §7–§9 aileron, flap and tab as pressure sections with no appendix by gate;
  §10 engine mount, §11 OEI, §12 landing; and Appendix A as the balanced V-n
  condition register — the candidate set every selection is made from,
  published as a page and as `<project>_vn_conditions.csv`. Byte-deterministic
  from `ga6_normal` and `baron_58` in CI, concept-content-free by guard.
- **The load-output contract inverted (note 49, OR-116/OR-117):** every load
  sloads delivers is **LIMIT with the safety factor stated per case and
  applied nowhere** — module views, both reports, the CSVs and the sbeam deck
  — gated tree-wide (G-OR-71…G-OR-74), with the two prescribed-ultimate
  families (23.367(a)(2), 23.561(b)) the stated exception at SF 1.0. The GUI's
  21 stale ULTIMATE claims swept by an AST gate (#192).
- **The review that would not let Rev A leave DRAFT:** the owner-commissioned
  2026-09-08 GUI/report/CSV review filed **#227–#246** in-session (rule 5);
  the 0.8.2 subset **#227–#238** all fixed — ground-attitude labels read the
  owner not the tuple order, every cross-reference resolves, gyro prose
  follows the printed case set, SF columns and SI conversion completed.
- **Cut hygiene as its own items:** #190 (ten shipped notes archived keeping
  their numbers, the backlog re-cut, parked rows promoted to #247–#252) and
  the review quartet — #183 (a note closed by a history fragment says SHIPPED,
  guarded), #184 (the tag waits for a green `main`: `--check-main-run`),
  #187 (a live note's INDEX row is a pointer, capped and status-free by
  guard), #189 (process docs describe the process that exists;
  `GIT_FLOW_GUIDE.docx` demoted, the standard tree guardable-formats-only by
  guard). Found at the §3.5 walk and fixed pre-cut: the three-view drew the
  fin's loads reference axis in the top view (`lra_overlays`, the last OR-15
  admission of the milestone).
- **Version** `0.8.1` → **`0.8.2`** (a new GUI capability — the report page —
  and no schema break: the v60 → v61 hop converts the spar-station entry by
  the airplane's own polylines, old saves migrating).
- **Changelog cut** — `scripts/build_changelog.py 0.8.2 --date 2026-09-08`:
  **91 fragments** consumed into `## [0.8.2]`, **39 history entries** rolled
  to the top of this file, a fresh empty `[Unreleased]` opened.
- **History roll** (`RELEASE_PROCESS.md` §4.3): notes **44** (the report — the
  milestone's plan of record) and **53** (thrust line) move to `40_history/`;
  note **49** stays live — its header states an unshipped 0.8.3 half (OR-81's
  marker sweep, OR-90…OR-92), and the mechanical rule rolls a note whole when
  its status reads shipped, not by halves; notes 21/51/52 stay with their open
  milestones.
  The live file passed the **1,500-line threshold**, so everything below the
  0.8.1 cut block froze verbatim into
  [`51_completed_development_to_0.8.1.md`](51_completed_development_to_0.8.1.md).
  `tests/test_frozen_set.py` is deleted — the OR-13 freeze is milestone-scoped
  and lapses with this cut, which is also what admits 0.8.3's #25 (empennage
  geometry) and the frozen-code defect queue (#177, #210, the `tail_span.py`/
  `balance.py` docstrings citing archived notes' old paths).
- **Gates at cut:** `pytest` **3809 passed / 32 skipped / 1 xfailed / 0
  failed**, `ruff` clean, `mypy` clean (`sloads/`), `scripts/smoke_test.sh`
  **PASS** (both front-ends boot, CLI CSV checked),
  `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on 7 tracked keys,
  the §3.5 by-hand walk done (it found the fin LRA defect above), no open
  CRITICAL/MAJOR review findings.

**Key decisions.** *A report is a view, and building a view is not an occasion
to adjust what is viewed:* the OR-13 freeze held for the whole milestone as a
hashed manifest, and every one of its admissions is a scoped OR-15 comment on
the hash it moved — the freeze ends by deletion at the cut, not by erosion.
*The factor is stated, never applied* (note 49): the milestone that documented
the analysis is also the one that made every delivered load say what has not
been done to it. The review's findings became milestoned issues in-session,
and the ones that could not ship in 0.8.2 are 0.8.3/0.9.0 rows, not prose.
**Band B3 retired with the cut; band B4 (0.8.3 — the empennage geometry model,
unblocked by this cut's freeze lift) is the milestone in flight.**

## Step 166 — Appendix A is the candidate set (design note 44 §23, tier L, 2026-09-07)

**Objective.** Replace the reserved "Input echo" slot with the balanced V-n
condition register: every point the flight envelope produces, reproducing Ref 1
Appendix A p179 (the mass cases) and p180-185 (the balanced-flight columns), with
the CG, the altitude and the configuration as columns rather than as block
headings, and with the case ids each point was selected as. The document had been
naming 23 critical conditions without ever showing the reader the 80, 180 or 200
they were selected out of, and a selection whose candidate set is not published
is a claim rather than a result.

**Agreed first.** Design note 44 §23 (**OR-193 … OR-202**, gates **G-OR-131 …
G-OR-138**), settled with the owner in session on 2026-09-07 before any code,
from the owner's instruction and eight answered questions. **No load equation is
touched by this step**: the matrix has always existed in memory, and `VnPoint`
already carried every column the owner asked for, `config`, `cg` and
`altitude_ft` among them. What changes is that it is published.

**The first appendix that is not a projection of a section.** B through F each
restate one section's loads at a finer grain and their state follows that
section's. Appendix A follows none: it is the matrix every section selected
*from*. That is why its component columns are columns on the matrix rather than a
table beside it — the survivors are marked within the candidate set, in place.

**The reservation is spent, and it worked.** OR-50 held slot A empty for an input
echo and argued it on lettering stability: shipping the wing appendix into an
empty tuple would have printed it as A and moved it to B the moment the echo
landed, so an issue signed in between would have disagreed with its own reissue.
OR-194 **fills** that slot, so B through F never moved — the reservation is
vindicated rather than merely retired. The echo itself is dropped on the owner's
ruling (*"drop it and just reference the json file"*), and the reason stands
independently: `project.json` **is** the input echo, exactly and machine-readably,
and a table transcribing it is a second copy that can disagree with the first.
The document names the file.

**A latent defect, fixed at its first reader.** `select._stamp_case_refs` wrote
`p.case_ref = ref` onto the originating point — but a point is routinely selected
more than once. On `ga6_normal` V-n case 14 is `VT-01`, `VT-02` **and** `VT-03`;
case 74 is `HT-03` and `HT-09`; case 30 is `W-03` and `F-01`. Measured across the
three shipped examples: 4, 5 and 4 multiply-selected points, and last write won
every time. Nothing shipped was wrong, because the field had exactly one writer
and no reader in `sloads/` outside serialisation — which is what makes it latent
rather than live, and why it is fixed here, at the table that becomes its first
consumer, rather than ranked against the fidelity backlog under rule 6. The field
is **replaced** by `case_refs` rather than joined by a plural sibling, because a
dead singular beside a live plural is decoration; schema 63 → 64, an identity hop
carried by the reader, since a pre-v64 file could never hold more than one ref.
The stamp clears before appending, so stamping one envelope twice is the same as
stamping it once — the idempotency assignment gave for free and appending does
not.

**The question the table provoked, and its answer.** Reviewing the columns the
owner asked *"we don't have any cases defined as thrust on or off, are all
assumed off?"* Read from `_balance`: the balance solves the normal force and the
pitching moment about the CG and writes **no** longitudinal force equation. But
the drag does not vanish — `select` and `wing_inertia` both take `NX = −DX/W` and
hand it to WINGINER as a longitudinal inertia load factor, so the airplane *is*
in longitudinal equilibrium, by d'Alembert: the whole of DX is reacted as a
deceleration. Thrust is therefore off **by construction and consistently**, a
modelled assumption rather than an omission. `NX` is now a printed column beside
DX, because it is the answer to where the drag went and because DX alone invites
a reader to conclude the balance is incomplete; and it acquired an owner,
`aero_curves.inertia_drag_factor`, on the way, replacing two spellings that a
third would have joined. Modelling power — a reduced NX and a thrust-line
pitching moment about the CG, for which design note 53's thrust-line geometry
already exists — would move every balanced point, and is filed rather than done.

**Nineteen columns do not fit A4.** Measured at the point of writing the gate:
662.7pt of content against 424.9pt of page, the column separators alone taking
228pt of the 652.85pt landscape width. Merging the four component columns into
one loses which structure selected the point; rounding the loads to the manual's
own fixed precision would replace the house formatter for one table. Split into
two column groups — the flight state, and the balancing loads with the selection
— both fit with 164pt and 119pt to spare, at full precision, with every column
the owner asked for. The split is by **column group and never by row**: no
`FOR CG1 FS= …` heading returns, both tables walk the envelope in its own order,
and they are keyed by the same CG and case, which the gate asserts row for row.
The CSV has no page to overrun and carries all nineteen in one flat row, which is
the single table the decision asked for.

**The gate caught a real disagreement before it shipped.** G-OR-136 holds the CSV
to the appendix's own rows, and it failed: `build_oracle_document` builds from
the **oracle projection**, not from the file (OR-21, G-OR-13), and a CSV built
from the file disagreed with the page it claimed to be — on
`concept_regional_jet` the projection balances MAN D at 387.5 kt against the
file's entered 350, and every load in the row moves with it. `vn_conditions_csv`
now reduces through the same owner.

**A register that a citation can point outside of is not a register.**
`report/render.py`, step 165's own history fragment and backlog row 38 all cite
"note 44 OR-193", and design note 44 defined OR-183 … OR-192. The row is added,
and what stops the next one is structural: **G-OR-137** sweeps every `OR-n` and
`G-OR-n` cited anywhere under `sloads/`, `tests/`, `docs/` or `changes/` and
requires each to be defined in a design note — the same shape OR-191 gave
cross-section references, one level up. OR-193's own gate was in the same
condition: its docstring claimed the fix was gated, and the only thing holding it
was the frozen Imperial baseline, which fails as a *changed number* rather than
as a stated property, so a change that moved the engine locations and regenerated
the baseline would have passed. **G-OR-138** states the property — every
condition an engine emits sits at one point, and no two engines share it — and
was verified to fail against the defect it names before being kept.

**The admission.** One OR-15 grant, given in session on 2026-09-07 and recorded
as OR-203: two lines and an import in `modules/select.py` (the stamp, and the NX
owner) and one line and an import in `modules/wing_inertia.py` (the same NX
owner). No selection criterion, no balance, no arithmetic. The consequence,
stated and then measured: **none** — the frozen Imperial digests are unmoved and
all 49 unit-deliverable gates pass unedited, which is what turns "behaviour
preserving" from a claim into a number. Both files re-pinned with the scope
recorded beside the hash, as OR-190 did for `landing.py`.

**Verification.** Seventeen gates in `tests/test_oracle_report_vn.py`, over five
fixtures. The numbers are deliberately **not** re-oracled there: the matrix is
already locked against Ref 1 p179-180 by `tests/test_flight_envelope.py`, whose
tolerances are each derived from a stated effect, so what this file owes is view
fidelity — every printed cell is its point's own value through the document's
formatter — and a second comparison against the manual would be a second owner
for one fact. The two defect gates were each run against the defect they name and
observed to fail: reverting the stamp to last-write-wins fails the case-id gates,
reverting `_running_locations` to the first location in the set fails G-OR-138.
The case-id gate takes its expectations from the **critical conditions**, not
from the points' own `case_refs`, because reading the field on both sides would
let a lossy stamp lose on both and pass.

**And the documents were compiled**, for the first time in four iterations. The
standing caveat — "no `pdflatex` in this shell" — was wrong: the project's own
`export.pdf.find_engine` resolves **tectonic**, which is installed, and the
caveat came from checking for the wrong binary rather than asking the owner that
exists for the question. All three reports build clean (exit 0, 112 / 119 / 113
pages). Appendix A sets as designed: both tables upright in landscape with room
to spare, no column overprinting its neighbour, and the widest cell in the
document — `VT-01, VT-02, VT-03` on `ga6_normal` case 14 — wrapping onto two
lines *inside* its column, which is what the width solver's floor exists to
guarantee. The three overfull `\hbox`es on `baron_58` and
`concept_regional_jet` are 0.88pt each, in Section 10's engine-installation
`tikzpicture`, and predate this step.

## Step 160 — The applied appendices are one deck in one frame (note 44 §18, tier L, 2026-09-07)

**Objective.** Make every appendix that gives an applied load give the same thing in
the same frame — the case, the point it acts at, all six body-axis components and the
factor — across the wing, the fuselage and both tails; and give each surface that set
as a file. Reviewing the proposal found that two of the four appendices were **wrong**,
not merely inconsistent, so the step carries a defect as well as a format.

**Agreed first.** Design note 44 §18 (**OR-139 … OR-146**, with **OR-141a** added on
agreeing it), settled with the owner in session on 2026-09-07 before any code. Gates
**G-OR-89 … G-OR-94**. Under `CLAUDE.md` rule 6 the defect outranked the consistency
work; the owner's ruling was that they close as one step, because the single-owner
change is the fix that stops the defect recurring.

**The defect (OR-143).** Appendices D and E both stated "a row here and the card that
carries it are the same load". Per station the spanwise deck writes a `MOMENT` card from
the strip torsion and folds the span-axis axial into the `FORCE` card; the appendix
printed one force column. First case, summed over stations: h-tail applied torsion
6,689 lb-in on `ga6_normal` and 232,139 on `concept_regional_jet`; fin torsion 2,351 and
80,117, with 23.1 lb and 638.5 lb of axial. Appendix E's note called those components
"absent by construction" — for the fin `Fz` is neither. Three examples also carry a
T-tail transfer node neither appendix printed.

**The other half (OR-142/OR-146).** `applied_body_moments` returned the wing's map for
every component, so the fin's torsion was published as `My` — a component whose true
value on a fin is identically zero, because a lateral load makes no moment about `y` at
all. Section 6.5 printed the same quantity as `Myy` = 4,561 lb-in at `ga6_normal`'s
root, two chapters after section 3.2 taught the reader to map the beam symbols onto body
axes. `coordinates.tail_torsion_to_airplane` had owned the correct map since the deck
was written, sign derived rather than asserted; the report never called it.

**Deliverables.**
- `export/sbeam_bridge.py` — `AppliedLoad` gains `component` and `body_moments`;
  `applied_loads(component, arg, project)` is the one entry point, with
  `fuselage_applied_load_rows` and `tail_applied_load_rows` beside the existing wing
  producer. `applied_body_moments` becomes component-aware and routes the fin through
  `tail_torsion_to_airplane` rather than restating its sign. `APPLIED_CSV_NAMES` and
  `_APPLIED_CSV_NOTES` — one file and one conventions block per surface, each naming
  the producer its zero columns lack.
- `report/oracle_sections.py` — `applied_load_table`, the one appendix table for all
  four components; Appendix C split into C.1 and C.2; `_TAIL_TORSION_SYMBOL` and a
  component-aware spanwise notation table, so §5.5 prints `Myy` and §6.5 `Mzz`.
- `report/content.py` — manifest rows for the three new CSVs, each stating which axis
  its free torsion is about.
- `app/views/export_report.py` — the three files in the bundle, on the Export page and
  in the workbook.
- `tests/test_oracle_report_applied.py` — new, 26 gates, the six of §18 across three
  shipped examples including the T-tail.

**Test.** **G-OR-90** is the one that matters: for every case of every tail surface, each
card the deck writes at a grid is compared against the appendix's rows at that grid —
components, sign and point — with cards at a repeated grid summed rather than replaced,
because a T-tail's tip node legitimately carries two. It fails outright against the
document as it stood. Beside it: one column set across all four appendices; the fin's
torsion asserted **through the mapper** rather than on a column, so a component added
later cannot inherit the wing's map by defaulting into it; no note calling a live
component absent; every all-zero column named in its own note; Appendix C two
subsections sharing no load column; and neither tail printing the other's torsion
symbol, both directions. Suite **3655 passed**, ruff and mypy clean, and all three
shipped reports still compile with no LaTeX warnings at thirteen columns.

**Key decisions.** OR-140 supersedes OR-61 for the applied appendix and only there —
the zero-column rule keeps its reach over every results table, because the argument
against it is a property of decks, not of tables. OR-141 extends OR-64's single-owner
ruling from the wing to the airframe, which is what makes OR-143 a defect that cannot
recur rather than one that was fixed in four places. B.2 and the new C.2 stay and say
what they are for: the carried set is what a model built from the applied set should
return, which is why its frame is the beam's own.

## Step — Chord bending is stated, and a symbol is data (design note 47, tier L, 2026-09-03)

**Objective.** Close OR-70, which note 46 had filed as *not done*, by testing its
reasoning rather than inheriting it — and fix what testing it turned up. OR-70
held that Appendix B.2 should not gain `Mzz` because a beam-convention `Mzz`
beside B.1's body-axis `Mz` would put two conventions in one appendix without a
reader-visible reason.

**What the review found.** The reason does not survive. B.2 already prints `Mxx`
beside B.1's `Mx` — the same pair of conventions — and section 3.2's notation
table already carried the sentence that separates them, written as a forward
reference to a column that was not there: *"so `Mxx` and `Mx` share a sense and a
chordwise bending would not."* OR-69 had settled the identical question one file
away, for `wing_span_loads.csv`, which prints both in the same row. Meanwhile
three statements in the tree disagreed about `Mzz`'s status: the code called it
"not delivered by this analysis" (it is delivered, and oracle-locked at the root
to Appendix A p222), OR-55 omitted it from the *figures* for a reason about
plotting that was never claimed to cover tables, and the standard's own closure
gate named it among "the published" quantities while the appendix did not publish
it. Measured at the root on today's build, `|Mzz|` exceeds the `|Myy|` that does
get both a column and a figure on four of the five example cases — 1.80x on
`ga6_normal` ACRL, 1.34x on its PHAA, 1.05x on `baron_58` PHAA.

**Deliverables.** B.2 states `Mzz` as its fifth cumulative column and 3.2 prints
its recurrence `Mzz(i) = Mzz(i+1) + Sx(i+1) dy` beside the other four, naming the
`Sx`-into-`Mzz` term as a position transfer a structural model generates for
itself (**OR-71**, superseding OR-70). 3.4 gains the fifth figure, and the
figures are tied to B.2's columns by gate rather than by list (**OR-72**,
superseding OR-55 on this point). B.2's note restates the sign instead of only
citing it, because the reader it is written for looks a number up rather than
reading the section through, and B.1's `Mz` being identically zero means nothing
else on the page would warn them (**OR-73**). The notation table gains its `Mzz`
row and its note now names all three beam symbols.

Found in passing and independent of the ruling: 3.3 was printing the heading
`Root chord bending Mzz` against a notation table that defined no `Mzz`, against
the report's own SHALL, and the guard walked only the two appendix tables.
`LoadValue` gains `symbol` — the notation symbol as data on the value, the third
instance of the move `frame` and `point` already made — and `net_loads`
populates it for the six wing root values (**OR-74**). The guard reads the field
and now walks section 3's own tables as well (**OR-75**), additionally asserting
that each label prints the symbol it declares. Parsing the heading was never
available: `Root torsion Myy (25% chord)` does not end in its symbol, and both
torsion labels carry the same one.

**Test.** `test_the_cumulative_table_carries_the_chord_bending` (G-OR-39) checks
every printed `Mzz` against the module's own station value scaled by that case's
safety factor, for every row of every case;
`test_the_cumulative_table_says_its_moments_are_the_beams_own` (G-OR-40) holds
OR-73's restatement; `test_every_cumulative_column_is_also_plotted` (G-OR-41)
asserts the figure set and the column set are the same set;
`test_section_three_defines_every_symbol_its_tables_use` (G-OR-42) is widened to
3.3 and to the label-prints-its-symbol check;
`test_section_three_states_how_the_cumulative_loads_are_built` (G-OR-43) requires
a recurrence for every column B.2 carries.

**Key decisions.** OR-71 … OR-75, design note 47, agreed by the owner in session
2026-09-03. `sloads/modules/net_loads.py` is frozen; the `symbol=` keywords are
the **second OR-15 admission of 2026-09-03**, granted on the ground that the
report cannot be built truthfully while it breaks a rule it prints about itself,
and that the guard cannot be widened without the fix. No oracle moves and no
Imperial digest moves: the change is a defaulted field on a result type,
`report.render.results_to_rows` builds its columns explicitly, and nothing in
`sloads/export/` changed. `SCHEMA_VERSION` **does** bump, to 60 with an identity
hop: `LoadValue` is persisted inside `critical.conditions[].loads`, so a
display-neutral addition to it is still an on-disk shape change — the third
instance of exactly that, after v58's `frame` and v59's `point`. The fields-hash
tripwire is what established it, against a first reading that had filed the
class as an unpersisted result.

## Step — The wing carry-through is entered as a fuselage station (design note 50, tier L, 2026-09-05)

**Objective.** Discharge design note 44 §13's **OR-97** finding — that every
wing-attach fitting load the oracle technical report can print is derived from
*assumed* spar stations — by making the station enterable, rather than by
stating the assumption more loudly. OR-97 called the exposure structural, and it
was: `front_spar_pct`/`rear_spar_pct` were `Origin.SLOADS` and unmarked, so the
oracle GUI never offered them and `reduce_to_oracle_inputs` stripped them,
which meant no project the report could be built from could carry a real
carry-through whatever it held on disk.

**Deliverables.** `SurfaceInput.front_spar_x_in`/`.rear_spar_x_in` replace the
chord-fraction pair (**schema v60 → v61**); `derived_geometry.carry_through`
reads the entered stations and falls back to the new
`derived_geometry.default_spar_station`, the one owner of the
`x_LE(root) + pct × c_root` estimator; `constants.DEFAULT_FRONT_SPAR_PCT` /
`_REAR_SPAR_PCT` move 0.15/0.65 → 0.20/0.60 and are re-cast as that estimator;
the two registry rows carry `governs=True` + `supplied=True` with an
`EXTERNAL_VALUES` resolver, which makes the pair a note 36 collapsed override
(blank derives, typed overrides) and puts it inside the oracle input set; the
geometry page renders the stations in the display system's length units with the
derivation captioned; `units.py` classifies them as lengths, where the fractions
they replaced were dimensionless; `migrations._hop_60` converts an entered
fraction to the station its own polylines describe; `report/content.py` echoes
only an *entered* station; the LRA export's assumed-joint note names the new
field. `PROGRAM_SPEC`, `theory_sources`, `ORACLE_REPORT` §7, the data dictionary
and the generated guide follow; the seven bundled examples are re-stamped at v61.

**Test.** Five gates. **G-OR-75/G-OR-77** — an entered station survives
`reduce_to_oracle_inputs` and `assumed` is False through the projection, with
the blank case asserted in the same test so promotion in either direction fails
(`test_oracle_inputs.py`; this is OR-97's own experiment kept as a gate and run
the other way round). **G-OR-76** — the G5 demonstration earning the `supplied`
mark: entering 70/100 in on `ga6_normal` moves the front fitting load by more
than 1 lb, so the mark is not speculative. **G-OR-78**'s other half —
`test_the_estimator_has_one_owner` pins that the caption's number and the
analysis's number come from the same function, which is what stops the page
describing a station nothing uses. **G-OR-79** — the hop converts an entered
0.18/0.62 to that airplane's own stations and the loaded project resolves the
pre-hop carry-through exactly; a `null` file hops to `null`; a degenerate
planform yields `null` rather than a station off a chord that does not exist.
The Imperial baseline is regenerated: 23 of 330 digests move, all in the body
channels, which is the default change and nothing else.

**Key decisions.** *A percentage could never have held the answer.* The datum is
measured at the fuselage; the fraction is taken on the centreline root chord, and
on a swept or cranked wing the two are different stations that no value of the
fraction reconciles. %MAC was put up as an alternative unit and measured out:
`ga6_normal`'s MAC leading edge sits 18.6 in aft of its root leading edge, so
20 % root chord is **2.28 %MAC** there against 18.57 % on `baron_58` and 12.64 %
on `cessna_210` — not a unit conversion but a different quantity — and `MAC`/
`XLEMAC` are themselves derived from the polylines, so a station stored that way
would migrate whenever anyone refined the wing outline. *The percentages left
rather than staying beside the station*: two stored fields for one quantity with
only one of them rendered is the duplicate-owner shape this project removes, and
because the replacement is computable from the same file the hop could convert
instead of dropping — the first live hop that is not an identity. Its first
draft was **not idempotent**, and `project_from_dict` re-runs `migrate`, so the
second pass wrote the freshly converted station back to `None`; the guard is now
that an entered fraction converts and wins while the key is otherwise only
created, never overwritten. *Note 44 §14 is superseded whole* — its OR-103
(mark the fractions), OR-105 (store them as percent) and OR-106 (blank widget)
answered a question this note removes; **OR-107 stands**, the change touching no
file frozen by OR-13, so no OR-15 admission was needed. OR-105's premise is
corrected on the way past: the spar pair were not the only `_pct` leaves holding
a fraction — `ref_axis_pct` is a third, filed rather than swept because the
two-front-end trap OR-105 named cannot reach a field the oracle GUI never
offers. The owner's related proposal — publishing the fuselage as two
cantilevers off the carry-through, with the between-spar VMT withdrawn — is
**not** in this step: it edits the frozen `body_loads.py` and gets its own note,
with its measurements parked in note 50 §7.

## Step 161 — Control surfaces deliver a pressure (note 44 §19, tier L, 2026-09-07)

**Objective.** Give the oracle report its aileron, flap and tab sections — the
geometry, the critical condition and the resulting load, as the printed oracle gives
them on pages 200, 201 and 202 — plus what the oracle does not give: a drawing of the
surface, a drawing of how the pressure is applied to it, a sign convention, and a
statement of the spanwise distribution, which the oracle leaves ambiguous.

**Agreed first.** Design note 44 §19 (**OR-147 … OR-157**), settled with the owner in
session on 2026-09-07 before any code, from the ruling that opens it: *these surfaces
are just pressure loads, so no appendix B, C, D type distributed loads; the aileron and
flap geometry is defined with the main surface in Section 2, use that definition; the
tab is defined with the elevator; the purpose is to show how to apply the pressure load
to the control surface.* Gates **G-OR-95 … G-OR-103**.

**What the analysis leaves ambiguous, and how it is closed.** The oracle prints a
chordwise rule in words and says nothing about the span. The rule is recoverable from
its own equations rather than assumable: the aileron's `W = LAIL/(SAFWD + ½·SAAFT)`, the
flap's `LF = 0.75·p_LE·SF` and the tab's `W = LTAB/1.5/STAB` each divide a load by an
**area**, so the pressure is uniform along the span and the chordwise profile is in
fractions of the local surface chord. Checked against Appendix A exactly: flap
`629/(10.7·144) ÷ 0.75 = 0.5443` against the printed 0.545 psi; tab `84.618/226 × 4/3 =
0.4992` against 0.4992 / 0.2496; aileron `271.44/3.894/144 = 0.4841` against 0.484. Two
consequences are stated rather than left to be inferred — the load per unit span goes
with the local chord, and the aileron's chordwise breakpoint is an *area* fraction, a
chord fraction only where the hinge-chord ratio is constant along the span.

**What the review found.** The area a surface's loads are run on and the area its
entered outline encloses are two entered numbers, and they disagree: the aileron's
outline is −0.2 % against its analysis area on `ga6_normal`, −4 % on `baron_58`, +5 % on
`cessna_210` and **−44 %** on `concept_regional_jet`. Had the locator figure shaded the
outline and divided the load by it — the obvious way to draw it — the regional jet would
have printed a pressure 77 % high for a load nothing had changed: the milestone's
recurring defect, an entered value shadowed by a derived stand-in with nothing saying
so. The pressure therefore has one owner and a drawn outline is never a divisor, and
past 2 % the document states the disagreement instead of resolving it in either
direction. **G-OR-98** asserts it on the airplane where the two are furthest apart.

**Deliverables.**
- `report/oracle_sections.py` — `_aileron_loads`, `_flap_loads` and `_tab_loads` behind
  three new `BUILDERS` entries, on shared owners: `_control_sign_convention` (one
  convention, one wording), `_SPANWISE_RULE`, `_HINGE_MOMENT_ABSENCE`,
  `_control_chord_figure`, `_control_locator_figure`, `_control_case_table`,
  `_profile_centroid`, `_tab_rectangle` and `_area_discrepancy`. `_CONTROL_HOSTS` and
  `_TAB_HOSTS` declare which surface each is cut into and which airplane axis its
  normal is, as data, so a surface added to the schema without a normal fails the suite
  rather than inheriting one.
- `report/oracle_content.py` — the three step keys join `IMPLEMENTED`, which is all it
  takes to turn a stated placeholder into a section.
- `tests/test_oracle_report_control.py` — new, 19 gates over four examples.
- `docs/10_standard/ORACLE_REPORT.md` §3.9 and ten register rows; note 44 §19.

**Test.** The gate that matters is **G-OR-97**, because it holds the *stated* spanwise
rule to the numbers the analysis was built with rather than asserting it in prose. Two
gates were written to fail in both directions — the area disagreement must fire on the
three that disagree and stay silent on the two that agree, and the locator must render
an outline or a sentence and never an empty axis, with both states exercised by the
shipped set. Two defects were caught by the new gates before they shipped: the flap's
slipstream table reached section 2's `_value_table`, which marks a load `-ULT` by
design because no load is meant to reach it, and the flaps-extended candidate table
printed four loads with no `SF` column. Suite green, ruff and mypy clean, and all three
shipped reports compile with no LaTeX warnings.

**Key decisions.** OR-147 is the one the rest follows from: the A–E appendix pattern
does **not** extend to a control surface, because that pattern exists for a load a
structures model integrates station by station and this is a pressure over a surface the
document already draws. OR-154 states no hinge moment at all — no module produces one,
and the sense of it is the sign convention, which is what a reader actually needs to
apply the load. Both are the same restraint the milestone has been applying throughout:
report what the analysis produced, and say plainly what it did not.

- **Deliverable bytes survive a rounding tie (tier M, 2026-09-06)** — the Linux
  CI leg had been red since `2d263f1` (note 49's LIMIT sweep), failing the frozen
  Imperial digest on one channel of one fixture while the full local gate stayed
  green. The cause was not note 49: `export.sbeam_bridge._fmt` prints seven
  significant digits of quantities that reproduce across platforms only to about
  twelve, so any value landing on the decimal rounding tie of its seventh digit
  resolves round-half-even off bits that x86 and ARM do not agree on. Note 49
  moved values onto ties; the fragility was always there, and measurement showed
  **all six shipped examples exposed** (248 tie-fragile values of 159,407 emitted,
  concept_regional_jet worst at 80) with only one having flipped so far. The
  human channel had already met this class at #147 and answered it by quantizing
  to twelve significant figures before formatting; the solver channel never
  inherited that rule. Rather than copy it, the quantization became one owner —
  `units.canonical` — that `report.render.format_value` and
  `export.sbeam_bridge._fmt` both read, recorded as clause (e) of
  `CONVENTIONS.md` §7's platform-stable-bytes row beside the (d) it generalises.
  Cost: 36 emitted lines moved across 4 of 330 digest channels, each a single
  seventh-place digit. One of them was a defect in a delivered artifact rather
  than a CI colour — `atr42_100`'s gear report stated the same load as
  `2.448331E+04` in its *Ground-line V* column and `2.448330E+04` in its *Datum
  Fz* column on the same row, the two straddling the tie from opposite sides.
  The guard is the population rather than a sample: every value every deck emits,
  on all six examples, invariant under ±3 ulp, so the next emitter that formats a
  solved scalar by hand fails the day it is written — verified by reverting the
  fix and watching it fail.

## Step 164 — The engine that fails is the one that sizes the fin (design note 44 §21, tier L, 2026-09-07)

**Objective.** Build Section 11, One Engine Inoperative — the eleventh section of
the oracle report and the only one whose subject is an *event* rather than a
state of the airplane. The section was scoped, and the scoping turned it into
something larger: measuring its loads against Section 6's showed it could not be
a report section alone.

**Agreed first.** Design note 44 **§21** (**OR-171 … OR-182**, gates **G-OR-113 …
G-OR-122**), settled with the owner in session before any code, from eleven
answered questions across two rounds. The note carries **two OR-15 admissions**
(**OR-181**), both narrow and both granted after a prototype had established
exactly what they needed to cover: `modules/one_engine_out.py` for four named
changes with `simulate` and `_moment` untouched, and `modules/select.py` for one
insertion point. Explicitly not admitted and not touched: `tail_span.py` and
`taildist.py` — the prototype proved they needed nothing.

**The measurement that reorganised the step.** LIMIT against LIMIT, total fin
load:

| Airplane | Largest SELECT fin case | 23.367 at VD | Ratio |
|---|---|---|---|
| `baron_58` | 1357.2 lb (YAW 15 NEUTRAL) | **2155.8 lb** | 1.6x |
| `atr42_100` | 4878.1 lb (YAW 15 NEUTRAL) | **12 829.3 lb** | 2.6x |
| `dhc8_dash8` | 4527.1 lb (SIDE GUST) | **14 780.8 lb** | 3.3x |

On every twin in the fixture set the one-engine-out case is the **governing** fin
load, by up to 3.3x, and the fin was sized without it: 23.367 was in no critical
set, no distribution, no appendix and no deck. Under rule 6 a defect with
first-order effect on shipped content outranks the iteration that found it, so
the section and the admission landed together. A document that printed a
governing load in Section 11 while Section 6 five pages earlier called a smaller
one critical would have published the contradiction rather than fixed it.

**Deliverables.**
- `modules/one_engine_out.py` — `fin_conditions` publishes the recovered cases as
  fin design conditions; `_fin_cases` is the one enumeration the section and the
  envelope both walk, so the printed cases and the admitted ones cannot come from
  two sets. Every entered engine is failed in turn, signed by its butt line.
- `modules/select.py` — `_with_engine_failure`, one insertion point in
  `default_critical`, idempotent because that function serves a persisted set as
  readily as a computed one.
- `report/oracle_content.py` — `SectionState.NOT_APPLICABLE`, ranked above
  `ABSENT`, its reason read from `applicability.step_not_applicable`.
- `report/oracle_sections.py` — the section, in three subsections, with the load
  table, the transient-response table and six figures.
- `safety_factors.shared_basis_factor` — the OR-118a per-table basis rule, given
  one owner and read by both the document and the export.
- `docs/10_standard/PROGRAM_SPEC.md` ONENGOUT, `docs/20_theory/00_theory_sources.md`
  C9, and the backlog row for the 0.9.x ultimate down-select.

**Test.** **G-OR-113** is the one that matters: Section 6 and Section 11 must
name the same critical fin case, which is the whole argument for OR-172 written
as an assertion. Beside it: every admitted case reaches the chordwise
distribution, the spanwise distribution, the appendix and the deck, asserted by
case ID through all four; a non-recovering case reaches **none** of them, checked
in both directions on `atr42_100`, whose VS case does not recover while its VC
and VD cases from the same run do; the published aero state reconstructs the
split it came from, each method through its own large-deflection factor; and a
mixed-basis file keeps a plain header while an all-ultimate one is marked. Suite
green — 3720 passed — ruff and mypy clean.

**Key decisions.** OR-172 is the step: the 23.367 cases are fin design conditions
and travel with them, which cost nothing downstream because ONENGOUT already
published the `LT25`/`LT50` split at the stations `taildist` and `tail_span`
distribute from. OR-174 is its necessary limit — a load at the simulation bound
is not a design load, and an envelope that absorbed one would have accepted a
number nobody has; such a case is printed in full, referred to stability and
control, and excluded. OR-178 was found rather than planned: implementing the
section would have dropped `ga6_normal` from "not yet implemented" to *"Not
analysed — the inputs this section needs are not present"*, which is false about
a single-engine airplane, so "not applicable" became a state of its own with the
predicate that already existed as its owner. OR-173 refuses to mirror: one engine
gives the fin one sense, and asserting the other would be the report minting a
case the analysis did not run.

**What this step states rather than solves.** Two consequences of a transient
having no V-n point are carried in the results' own notes and left there. The
fin's lateral inertia relief is switched off on exactly the cases that govern —
safe, because the relief is unconservative and worth 0.7-1.8 %. On a **T-tail**
the concurrent horizontal-tail tip transfer cannot be resolved for the same
reason, which on a T-tail twin means the case that sizes the fin is the case
whose tip load is missing; that is design note 51's, with the rest of the T-tail,
and it is why `atr42_100` does not join the shipped report set until note 51
lands (OR-182).

## Step 162 — The engine mount takes six components at one point (note 44 §20, tier L, 2026-09-07)

**Objective.** Give the oracle report its Section 10: what the engine-mount
conditions were computed from, where their loads act, and all six components of
each in the airplane's own axes — the oracle prints a load factor, one load, a
point and a single torque with no axis at all. Building it turned up two defects
and a wrong sign of my own, and the sign is the part worth recording.

**Agreed first.** Design note 44 §20 (**OR-158 … OR-170**), settled with the
owner in session on 2026-09-07 before any code, from seven answered questions:
the application point stays the oracle's, the published sense is what the engine
applies to the airframe and is to be stated explicitly, the thrust axis is
resolved into the global frame with a second table giving the torque and thrust
about the thrust line, thrust is not a component of the 23.361/23.363 cases, each
gyroscopic sign combination is its own case, one row per engine, and all three
views draw the airframe outlines where they are available. Gates **G-OR-104 …
G-OR-112**.

**The sign, derived rather than chosen (OR-162).** The first implementation
negated the module's torque to turn "the reaction" into "the applied load", which
made Section 10's `Mx` equal to the load-case file's `ENG MOUNT TORQUE` — the two
conventions agreeing, which is the one outcome that means one of them has been
lost. Third law, twice, settles it: a propeller turning clockwise from the
pilot's seat is driven by `+Q`, returns `−Q` to the engine, is held by `+Q` from
the mount, and the engine therefore delivers **`−Q`** to the airframe. `−Q` is
exactly what `mx_mount_torque` already carries, so nothing is negated — it is
*rotated*. With the thrust line pointing forward, `−Q` about it is `mx = +Q`
about the aft-positive `x` axis, which carries starboard up: the left roll a
clockwise propeller produces. Two independent readings agreeing is what makes the
sign derived, and it is why the printed scalar and the printed `Mx` carry
opposite signs — which **G-OR-105** now holds them to, in both the equal-magnitude
case and the inclined-axis case.

**The defect in the fixture (OR-170).** Measuring for OR-159 found `ga6_normal`
printing its application point at waterline **3.166** where Appendix A p227
prints **93.022**. Both entered CG waterlines were wrong — the propeller's `x`
in the engine's `z` slot, the printed *combined* `z` in the propeller's — and the
page supplies the right pair (92 and 100) exactly. The fixture's own comment
recorded why it survived: *"XPROP chosen so combined XPP = 17.91"*, and no test
asserted `zpp`. Under rule 6 the defect outranked the iteration it was found in.
`cessna_210` carries the same shape of error with no page to correct it from and
is filed with its number.

**The defect in the owner.** `load_cases_to_rows` decided whether a condition
fans into sign combinations by matching its FAR *reference* against `23.371(b)`.
`25.371` packs the same four sub-cases under a different reference, so on any
FAR-25-enabled turbopropeller project the Engine Mount page's load-case file
printed one row with **no moments at all**. Fixed at the owner by asking the
keys the sub-cases are carried in, which is what identifies them (rule 4).

**Deliverables.**
- `export/coordinates.py` — `engine_thrust_axis` and `engine_applied_load`, the
  one owner of the thrust line and of the resolution onto airplane axes, with
  `ASSUMED_THRUST_AXIS` for the installation that locates no hub.
- `derived_geometry.py` — `fuselage_outline(project, frame)`, the first and only
  producer of a drawn body, in each of the three views, reading
  `fuselage_centreline` for the side view's datum.
- `report/oracle_sections.py` — `_engine_mount` and its two subsections, the two
  load tables, the three view figures, and `_ENGINE_SHORT_NAMES` so a
  ten-column table carries a name and not a sentence. `build_section` now renders
  a builder-discovered absence instead of dropping it.
- `report/render.py` — `_has_gyro_subcases`, and both fan-out branches through it.
- `tests/test_oracle_report_engine.py` — new, 19 gates, the nine of §20 across
  four shipped examples including the twin and the assumed-axis turbopropeller.

**Test.** **G-OR-104** is the one that matters: for every case of every engine of
every shipped example, the six printed components are recomputed from the
module's own values **through `engine_applied_load`** and compared cell for cell,
so a component added later cannot inherit a literal at a call site. Beside it:
the Appendix A engine reaching the document including the waterline OR-170 fixed;
the four gyroscopic ids `a`–`d` with the vertical and thrust constant across
them; both engines of a twin at mirrored butt lines; an assumed axis marked and a
derived one not, asserted in both directions on shipped data; and the three views
built on a project with no geometry at all. Suite **3695 passed**, ruff and mypy
clean, and all three shipped reports still compile with no LaTeX warnings.

**Key decisions.** OR-159 keeps three stations in the document and quotes the
loads about exactly one — the other two are the deck's nodes, and a reader
transferring the set needs the offsets more than they need them hidden. OR-164
prints `Fx = 0` in the torque cases rather than filling it from the engine's
entered design thrust, because that is a flight input and not a 23.361 component;
OR-167 prints one sense of the side load and states the other, because fanning it
into two would be the report minting a case the analysis did not run — which is
the line OR-165's four gyroscopic cases are on the other side of.

## Step 163 — The engine's thrust line is an input (design note 53, tier L, 2026-09-07)

**Landed in Step 162's commit, `175369e`.** The two steps were built in one
working tree and `solo_close.sh` gates and stages the whole of it, so this step's
files went in under *"The engine mount takes six components at one point"*. Both
are recorded here as the separate steps they are — separate design notes,
separate gate sets, separate fragments — and the changelog is assembled from
these fragments rather than from commit messages, so nothing is lost by the
sharing. Noted because a reader tracing this step to a commit of its own will not
find one.

**Objective.** Section 10 shipped a day earlier resolving each engine's torque
and thrust onto the airplane axes, and it needed an axis to resolve them about.
The schema had never carried one, so note 44 OR-161 derived it from the engine CG
to the propeller hub — with a caveat printed beside it and a backlog entry filed
the same day. This step replaces the derivation with an input, and makes the
propeller's rotation an input beside it.

**Agreed first.** Design note 53 (**D-53.1 … D-53.9**, gates **G-53.1 …
G-53.9**), settled with the owner in session on 2026-09-07 before any code, from
six answered questions. The note **carries two of the owner's OR-15 admissions**, both narrow:
`sloads/modules/engine.py` for the torque sign and nothing else — not a refactor,
not a rename, not formatting in the same file — and `oracle_app/form.py` for two
`MEMBER_LABELS` rows, asked for only once it was clear there was no way round it
(a composite field in the oracle input set renders as "1, 2" unless its members
are named, and that table is the only place the naming lives). Both files are
re-pinned in the frozen manifest with the scope recorded beside the hash.

**Why a derived axis had to go (D-53.3).** The line from an engine's CG to its
hub is not the shaft; it is a line between two *mass* stations, and it inherits
every error in either. Measured: **14.0°** off the airplane axis on
`ga6_normal`, whose stations are correct against Appendix A p227 — which put an
`Mz` of −178.8 ft-lb into section 10.2 for an airplane that has no such moment —
and **71.6°**, very nearly straight up, on `cessna_210`, whose engine CG
waterline is a filed defect. A derivation that turns a station error into an
orientation is worse than an assumption that says it is one. So: **two grades of
provenance, not three** — entered, or the airplane's forward axis marked ASSUMED.
The move was checked through the owner before it was agreed: `ga6_normal`'s
23.361(a)(1) goes from `Mx +715.32 / Mz −178.83` to `Mx +737.34 / Mz 0`, with
`Mx == −torque` an **exact** float equality and `|M|` unchanged at 737.3383. The
axis was spreading one torque across two axes, not adding one.

**The sign, and the flooring (D-53.5).** A propeller turning clockwise from the
pilot's seat delivers `−Q` to the airframe, so a counter-clockwise one delivers
`+Q`. That reaches every deliverable carrying a torque — the load-case file, the
case index, the text report, section 10 — because a direction honoured in one
and assumed in another is two conventions for one load, which is the defect
G-OR-105 exists to prevent. **G-53.1 failed on its first run**, and usefully:
BASIC's `INT` *floors*, so applying the sign inside the flooring made a
counter-clockwise stoppage torque 1 ft-lb smaller in magnitude than a clockwise
one — a rounding difference presented as a load difference. `_floored_torque`
now floors the oracle's own clockwise value and mirrors it.

**Deliverables.**
- `models/inputs.py` + `io.py` + `migrations.py` + `models/project.py` —
  `thrust_line_aft`/`thrust_line_fwd`/`prop_direction` on `EngineInput`, the
  round trip that keeps `None` distinct from `(0, 0, 0)`, and schema **v62 →
  v63** as an identity hop.
- `export/coordinates.py` — `engine_thrust_axis` becomes the entered-line owner
  with `ThrustLineError` for a half-entered pair; `ASSUMED_THRUST_AXIS` names the
  fallback.
- `modules/engine.py` — `torque_sense` and `_floored_torque`, and nothing else.
  The whole of the frozen file's part in this note, under the grant.
- `derived_geometry.py` — `engine_thrust_segments`, one owner for both
  three-views, written at the second time of asking after it was briefly a copy
  in each (rule 3).
- `field_registry.py` — three rows, all `supplied` with the G5 result that earns
  the mark stated in the basis, and both points registered in
  `SENTINEL_DEFAULTS`. Without it the oracle projection strips them and the
  report cannot see a line the user entered.
- `app/views/engine_mount.py` — the controls, with the sign convention stated
  beside them (D-53.7, the owner's requirement in as many words);
  `app/views/configuration_layout.py` — the line drawn on the three-view.
- `tests/test_engine_thrust_line.py` — new, 19 gates, the nine of note 53.

**Test.** **G-53.1** is the one that matters: a counter-clockwise engine's
torque is the *exact* negative of the same engine's clockwise torque, condition
for condition, in the module, the load-case file and the text report — and it is
what found the flooring defect. Beside it: the axis is not moved by moving either
CG station (D-53.3 said as the thing it forbids); a half-entered line refused by
name in both directions; a pusher resolving to the same sign as a tractor, which
is what makes "no tractor assumption" true rather than merely stated; the
gyroscopic set unchanged either way; and clockwise costing nothing, with the
Appendix A figures held through the default. Suite green, ruff and mypy clean.

**Key decisions.** D-53.2 states which point is forward rather than inferring it,
and that single choice is what removes every tractor assumption from the section.
D-53.6 exempts the gyroscopic condition and *says so in the document*, on the
same reasoning that has the thrust zeros printed rather than blanked: an omission
a reader can mistake for an oversight is worth a sentence. D-53.8 stops at the
input — `hub_thrust_set` still applies a pure `−x` thrust, gated by G-53.9,
because honouring an inclined line changes the trim solution and not just the
card it writes, and that needs a note of its own.

## Step 153 — Entered polylines are the geometry source of record (tier L, 2026-08-30)

**Objective.** Where a user enters a surface's leading- and trailing-edge definition, derive
its area, aspect ratio, MAC and quarter-MAC station from that definition; and give the GA6
example the planforms Appendix A actually prints for it.

**The finding that prompted it.** `sloads/tail_geometry.py` justified deriving a rectangular
tail planform on the grounds that "no shipped fixture carries tail polylines, and requiring
them would mean hand-entering planform data for six airplanes with no oracle to check it
against", and `tests/test_tail_geometry.py` pinned the consequence: "`ga6_normal` stays
derived on purpose: **Appendix A prints no tail chords**." Appendix A prints them. Its
contents list nine WINGGEOM runs beyond the wing and aileron already in the fixture —
vertical tail p147, vertical stabilizer p148, rudder p149, horizontal tail p151, horizontal
stabilizer p152, elevator p153, elevator fwd/aft of hinge p155/p156, elevator tab p157 —
each with its entered coordinate table and its computed properties. The fixture had kept the
outputs and dropped the inputs, while four *other* fixtures were given taper estimated from
published three-views. The one airplane with printed oracle geometry was the only one
running on an assumed rectangle.

**Deliverables.**
- `wing_geometry.planform_boundary` — the closed planform, one owner. Leading edge, tip
  chord, trailing edge, root chord; where the two edges span the same stations the closing
  chords are degenerate and it reduces to `chord = X_TE − X_LE`.
- `wing_geometry.surface_properties` — closed-form integrals in place of the strip sum.
- `examples/ga6_normal.project.json` — h-tail, v-tail, elevator, rudder and flap polylines.
- `tail_geometry._polyline_area_and_span` / `_polyline_mac_and_x25` / `TailPlanform.chord`
  — all now ask the shared owner.

**Test.** New oracle coverage on every transcribed surface against its printed AREA/SIDE,
MAC, YLE(MAC), XLE(MAC) and AR; worst 0.084 %. The v-tail, whose own table is on a leaf
missing from the bundled scan, is gated by closure against the fixture's scalars instead and
reproduces area to 0.014 % with span and aspect ratio exact.

**Key decisions.**
- **The polylines are the input; the manual's derived values are its output** (owner, in
  session). WINGGEOM's `H` is an unprinted convergence parameter, so its printed figures
  carry whichever discretisation each run used — demonstrated by the manual's own three
  elevator figures failing to sum (1181 − 1065 = 116, printed 118).
- **Span is measured across both edges**, root to tip, so a fin whose trailing edge reaches
  below its leading edge measures its full height. Every surface entered before this change
  has matching edge ranges, for which the value is unchanged.
- **The oracle chain moved and was re-pinned** rather than preserved. For the wing the
  manual used `H = 20`, and the 20-strip sum reproduces its printed MAC to 0.0006 % where
  the exact integral is 0.042 % away — so this trades fidelity to the manual's arithmetic
  for fidelity to the planform it drew. Six printed Appendix A figures move, the largest by
  0.51 %; all are registered in `02_approved_corrections.md` with the owner's approval and
  the full trail.
- **Two findings filed against frozen code** (OR-14), both later admitted under OR-15 and
  fixed in this milestone — see the two entries that follow: **#153**, the per-row delete on
  the Geometry page removes the last row rather than the one it names, which *this step* made
  reachable by taking the fixture past two surfaces (pinned meanwhile by a strict `xfail`
  asserting the correct contract); and **#155**, the configuration module's note still says
  MAC/XLEMAC/AR come "via the WINGGEOM strip integrator", which is now the method this step
  removed and is reproduced verbatim in §2.1 of the report.

**Authority.** `sloads/modules/wing_geometry.py` is hash-frozen for milestone 0.8.2 by
design note 44 OR-13; the owner admitted this change under OR-15 in session on 2026-08-30,
and the manifest hash is updated in the same commit.

- **Marker-label placement and axis ticks in the shared figure emitter (tier M, 2026-09-01)** —
  both documents' figures come from one emitter, and it had two habits that only showed up once
  the figures got crowded enough to matter. Every marker label was emitted `anchor=south`,
  directly above its point, which is the right answer until something is there: the GA6's V-n
  diagrams wrote all four gust labels across the manoeuvre boundary, the weight/CG figure wrote
  two CG cases across the loading edges, and the new speed/altitude figure put `Vh` on the
  never-exceed line. The fix is a placement rule rather than a table of offsets — a per-figure
  offset is correct for the project it was tuned on and silently wrong for the next one, and
  these figures are built for whatever project a reader loads. Each candidate position is scored
  by the clearance of the **box the text occupies** from every plotted segment, every reference
  line and every other marker, in normalised axis units so the two axes are comparable. Two
  earlier attempts are recorded in the code because both were wrong in instructive ways: scoring
  a single point beside the marker placed `CG3 / fwd light` so that its first character cleared
  the loading edge and its remaining fourteen did not, and taking the *roomiest* position rather
  than the first acceptable one moved every label in the document, including the ones nothing was
  near — a figure whose labels sit above their markers except where they cannot reads as a
  convention, one whose labels each point a different way reads as a fault. The box-to-segment
  distance is exact (Liang-Barsky clip, then corner and endpoint distances) because sampling
  points around the box let a box straddle a line with samples either side and none on it. The
  second defect was smaller: pgfplots reaches for a shared `·10ⁿ` multiplier past a certain
  exponent, so the altitude axis read `0.5 1 1.5` under a `·10⁴`. Every other axis in both
  documents was already fixed-notation, so turning scaled ticks off changed the one figure with a
  large range and no other — and forecloses the question for the next one.

## Step 158 — The fuselage beam states its geometry, and the body LRA is read (tier L, 2026-09-07)

**Objective.** Answer the owner's review of sections 4 and 5 against the built
document: give the fuselage beam table the coordinates it was missing, draw the body
in side view, and settle where the body beam actually runs — which turned out to be
the question the review was really asking.

**Agreed first.** With the owner in session on 2026-09-07, in four questions asked one
at a time, each answered before the next was framed. The fourth was asked only because
the third's answer failed a test the moment it was implemented.

**Deliverables.**
- `models/inputs.py`, `mass_distribution.py`, `migrations.py` — schema **v62**:
  `FuselageStation.y`/`.z`, blank-deriving from the item database's weight-weighted
  centroid; identity hop.
- `derived_geometry.py` — `FuselageLra` and `fuselage_lra`, the single owner of where
  the body beam runs, with the out-of-body guard.
- `export/lra_model.py` — the body chain asks that owner instead of the centre line.
- `examples/*.json` — six corrected `ref_waterline` values.
- `report/oracle_sections.py` — 4.1's side view; Table 21's Y and Z; the case
  reference as the key of the pull-up, fitting and tail tables; Appendix C's X/Y/Z;
  section 5's input-data subsection, reordered state table, hinge-moment statement and
  applied-load Appendix D.

**Key decisions.**
- **Where the mass is and where the beam runs are two statements, and both are
  kept.** The first framing of the schema change treated `FuselageStation.z` and
  `ref_waterline` as two spellings of one quantity, which is the duplication class this
  milestone has removed twice. The owner corrected it: `ref_waterline` was always meant
  to be the fuselage LRA. They are different quantities about the same station, and on
  `ga6_normal` they differ by up to 50 in.
- **`ref_waterline` was read by nothing, and the field registry said so.** *"Reserved:
  stored and round-tripped, but consumed by no current calculation … any value, 0
  included, is currently equivalent (#94, C210-34 owner ruling)."* The component deck
  put the beam at `z = 0`; the airplane model ran it on the section-centre line. That
  sentence is now false and the row says what replaced it.
- **The fixture data was placeholder, and the test that proved it was a solve.** Wiring
  the entered values up dropped the ATR-42's body beam 77 in below its body and made
  the LRA deck singular. Measured across the fleet: four of six waterlines lay outside
  their own fuselage, the Dash-8's by 47 in, with three unrelated airplanes entering the
  same round `100.0`. The owner ruled the values corrected rather than the wiring
  softened, so each is set to its own body's centre line — which reproduces the previous
  node positions to 0.03 in, the rounding of an entered number, so no deck geometry
  moves and no load changes.
- **The correction carries a stated risk.** Entering a value that equals the derived
  one, and having it then report `assumed=False`, is exactly the mechanism that produced
  the fin-root defect (note 19 §10.2's "pin today's assumed value as a stated one"). It
  was flagged before the values were written, and the mitigation is the guard rather
  than the note: `fuselage_lra` states a waterline that lies outside its own body, so
  the specific failure these six values had cannot recur unnoticed. Entering measured
  LRA waterlines remains open work.
- **A guard that breaks a shipped input field is the wrong guard.** The first
  implementation raised on an out-of-body waterline. That would have made
  `ref_waterline` untypable on any project whose body is entered, so it states instead
  — the same ruling the fin root's disagreement note carries, and for the same reason.
- **Absence is stated where a reader will look for it.** The owner asked why there is no
  hinge moment. It is not a missing input: the hinge line is known, and the elevator
  load is modelled smeared into the surface. 5.5 now says so and names the two inputs
  that would change it, and the two empty columns are removed — a column of dashes is
  not a statement.
- **Appendix D is a deck, so it carries only what a deck needs.** Applied load, at its
  point, in airplane axes. No `Fx` column: this analysis models no chordwise tail force
  and no empennage dihedral, so the other components are absent by construction rather
  than zero by measurement (OR-61), and the appendix states both absences.

**Test.** Three gates on the new owner in `test_derived_geometry.py` — the entered
waterline leads and is straight, a blank one derives station by station from the centre
line, neither gives a zero that announces itself; a waterline outside its own body says
so while still being used; and no shipped fixture carries one. Four new gates in
`test_oracle_report_fuselage.py` (the side view draws mass, beam and both load paths;
the beam table states both waterlines and which the analysis reads; the fuselage tables
key on the case reference; Appendix C places every station) and four in
`test_oracle_report_tail.py` (the input-data subsection draws the surface with its axis
and states it station by station; the hinge-moment absence is stated and its columns
removed; Appendix D places every load on the airplane in airplane axes). The schema hop
is guarded as an identity, and the Imperial baseline moves on `sbeam/lra_model` alone,
on the five fixtures with a fuselage outline and on none without one.

- **The GUI states LIMIT, and the sweep that found it becomes a gate (#192,
  tier M, 2026-09-05)** — design note 49 removed the safety-factor multiply from
  81 sites and left every delivered load LIMIT, then closed the prose surface
  with **G-OR-74**, whose scope sentence reads *"rendered output only: what a
  recipient actually reads."* A Streamlit caption is exactly that, but the
  checker only ever read the documents note 49 enumerated — the summary and
  oracle reports, the methods stamp, the workbook, the package README — so the
  **GUI was gated by nothing at all**, and the AST sweep the note describes
  stayed a discovery pass rather than becoming the standing check its own
  finding argued for. Twenty-one live false claims survived in fifteen `app/`
  files. The sharpest is a download button: *"Download net wing loads —
  ULTIMATE (CSV)"* over `sb.span_load_csv`, whose station-0 `Sz` for `ga6_normal`
  case PHAA writes `5831.6` beside `SF,1.5` while the module's LIMIT value is
  `5831.646378463103` — the same number, so a reader who believed the label
  under-sized by a factor of 1.5. The rest are captions asserting *"the
  Review/Export pages report **ULTIMATE** = limit × 1.5"* on six control-surface
  and landing pages, and *"Load columns are **ULTIMATE** (limit × SF)"* on
  Results Review and the Flight Envelope SELECT tab.
  Fixing the strings was the smaller half. The durable half is rule 3: the sweep
  is now `test_no_gui_string_claims_ultimate`, walking the `app/` and
  `app_shell/` **sources** with `ast` and asserting each non-docstring literal
  through the same `assert_states_limit` the document gates use — one checker,
  not a second implementation of the rule (P-1). Source-walking rather than
  driving Streamlit is deliberate: these claims are static text no session state
  can alter, and an AST pass cannot miss a page whose branch a journey test never
  entered. Docstrings stay excluded on G-OR-74's own scope rule, and
  `oracle_app/` stays out because it is frozen under OR-13 and its three claims
  are filed, not fixed (OR-14).
  Widening the gate exposed two defects in the *checker*, both of the class the
  gate exists to prevent. `_CLAIMS` was a list of substrings, so
  `**ULTIMATE** = limit` escaped it — markdown emphasis split the phrase — and
  `limit × SF` escaped it because the pattern spelled the multiplication sign
  ASCII `x` where every artifact writes U+00D7. A gate defeatable by typography
  is not a gate; text is now normalised (emphasis, dashes, `×`) before scanning,
  and the patterns are regexes whose boundary excludes a trailing hyphen, which
  removes the one false positive the widening produced — Structural Speeds'
  perfectly true *"All speeds are ULTIMATE-independent design limit speeds"*,
  which a bare `\b` had matched and which would otherwise have needed a
  hand-written exemption, the very mechanism `_SANCTIONED` is documented as
  avoiding. Each pattern now carries a witness quoted from the artifact that
  shipped it, and the meta-test asserts both directions: every witness fails the
  gate, and every pattern catches some witness, so a pattern cannot rot into one
  that matches nothing unnoticed.
  One find was not a string at all.
  `test_deliverable_units.py::test_the_export_page_states_the_system_it_will_write`
  asserted the Export page caption **contains** "ULTIMATE" — a green test
  requiring the false claim, which is why the residue could not have been found
  by making the suite stricter alone. It now requires LIMIT.
  A second-order consequence settled a display question. The Wing and Fuselage
  pages offered two downloads distinguished *by basis* — LIMIT table versus
  ULTIMATE bridge — and OR-116 made both LIMIT, so the distinction the labels
  drew no longer exists and swapping the word would have produced two adjacent
  buttons with identical labels over different bytes. They are relabelled by
  **channel** (*analysis table* / *sbeam bridge*, owner ruling 2026-09-05),
  the vocabulary `CONVENTIONS.md` already uses internally, with the shared LIMIT
  basis stated once beneath them. The `*_ULT.csv` file names are left alone:
  OR-81 retires them in 0.8.3, and until then a truthful label over a stale name
  is strictly better than the reverse.
  No calc changes and no schema hop. `app/views/` is pre-assigned to the #29
  rework, and touching it now is a deliberate exception taken on rule 6 — a
  defect with first-order effect on shipped content outranks the freeze, and the
  alternative was shipping the 0.8.2 report beside a GUI contradicting it.
  `CONVENTIONS.md` §OR-117 and `00_program_overview.md` carry the widened G-OR-74
  scope; note 49's gate section records the widening and both checker defects.

## Step — Every load is LIMIT: stated, never applied (design note 49, tier L, 2026-09-05)

**Objective.** Carry the owner's ruling — *"FAR 23.303 safety factor IS an
external loads factor; for this version of sloads all loads will be identified as
limit loads WITHOUT the safety factor applied"* — through the whole project.
This is **OR-116/OR-117**, and it overrules note 48's OR-87 and OR-93, which had
kept the deck and the summary report on the ultimate basis. It also dissolves the
cost note 49 §3 accepted under protest: *"the project ends 0.8.3 with two reports
on two bases."* The reasoning is a division of responsibility, not a tolerance:
sloads is an external-loads program, and 14 CFR 23.303 says the factor must be
applied without saying by whom. The loads program delivers the prescribed limit
load and states the factor; the sizing step applies it.

**Deliverables.** The multiply is **removed** from 81 sites across 7 files —
`report/render.py`, `report/content.py`, `report/oracle_sections.py`,
`export/sbeam_bridge.py` (73 sites), `export/balanced_deck.py`,
`export/lra_import.py`, `export/lra_model.py` — rather than neutralised: a
`_sf()` returning 1.0 would have left every `* sf` as dead arithmetic that still
read as if a factor were applied. `_sf` survives as the *stated* factor.
`report.LoadChannel` loses its `ULTIMATE` member, so a stale caller fails at
import instead of silently receiving limit loads; `to_ultimate` and `_ult` are
deleted. `export.sbeam_bridge.basis_sentence` becomes the single owner of the
deck's per-subcase statement (OR-117) across all eight deck writers. Every
in-band basis statement on every shipped artifact was rewritten to match its
contents, and the standard docs record the inverted contract:
`CONVENTIONS.md` §3 (retitled), `CLAUDE.md`'s Phase C mission sentence,
`PROGRAM_SPEC.md` M4-15, `SUMMARY_REPORT.md` §3.1, `ORACLE_REPORT.md` §3/§3.4,
`00_program_overview.md`, `PROJECT_GUIDE.md`, `GUI_design.md`,
`GUI_USER_GUIDE.md`, `theory_sources.md`, `safety_factors.py`'s row bases
(OR-88's rewording: `SF=1.0` reads *"already ultimate; apply nothing"*).

**Test / Acceptance.** Full suite green (3515 passed), `ruff` and `mypy` clean.
Three new gates, because **the existing suite could not see this change at all**:

* **G-OR-71** (`tests/test_limit_channel.py`) — a text scan asserting no path in
  `sloads/` multiplies a load by a safety factor. Its own teeth test found a real
  gap in the scan on the first run: the pattern was anchored to the bare name and
  matched neither `* c.safety_factor` nor `* r.safety_factor`, which are exactly
  the spellings removed from `content.py`. One documented carve-out, named with
  its reason: `flap.py`'s `sf` is FLAPLOAD.BAS's name for the flap area of one
  side.
* **G-OR-72** (`tests/test_export_equilibrium.py`) — the balanced deck's `FORCE`
  resultant closes against `nz × W` **without** the factor. Every pre-existing
  deck check is scale-invariant, so all 3400 tests were green at either basis;
  the 1.5000 ratio between the two (27,037.996 vs 40,556.996) was measured by
  hand before this gate existed. Mutation-verified: it fires on all six fixtures
  while 154 other equilibrium checks stay green.
* **G-OR-73** (`tests/test_deck_basis.py`) and **G-OR-74**
  (`tests/test_basis_statements.py`) — the deck and every rendered document must
  state, per subcase, the factor they did not apply, and the stated number must
  be the case's own. Both mutation-verified.

The Imperial baseline was regenerated twice, deliberately, and each move was
accounted for before the regeneration: **208 of 330 digests** for the basis change
itself (all `sbeam/*`, `gear_report`, all `txt/*` headers; the 122 unmoved are
`csv/*`, LIMIT since note 48, and `case_index`, which carries no load value), then
**2 channels × 5 examples** for the two deck sentences corrected afterwards.

**Key decisions.** OR-116 … OR-120 and OR-118a, design note 49 §8, ruled by the
owner in session on 2026-09-04/05. **OR-120** moved the LIMIT core from 0.8.3
into 0.8.2 so that the oracle report's new §4 is written once, on the final basis,
rather than twice. **OR-119** resolves review R-12 (#182) as *decided, not fixed*:
G-OR-49 was unsatisfiable while OR-93 kept the summary report ultimate, and
becomes satisfiable as written once OR-93 falls.

Four gates and two documents were found to be **passing while wrong**, which is
the substance of this step beyond the arithmetic. The oracle technical report was
printing 1.5× Appendix A's figures — the oracle tests compare at calc level and
never cross the render boundary — against a document whose purpose is to be read
against p131. Seven deck comments asserted their cards were ultimate over LIMIT
numbers, two of them printing a `1.5 ×` derivation for a sum that no longer had
it. Appendix A's bundle manifest had called the per-module CSVs ULTIMATE since
note 48, because its guard pins prose against a hand-written map and so detects
drift between the two rather than falsehood in the pair. And
`test_ultimate_markers_and_sf_columns_are_present` passed on the methods stamp's
*explanation* of the `-ULT` marker rather than on any marked cell.

The first version of G-OR-73 shared that weakness: it matched one phrasing and
missed two live sites saying the same thing in other words. It now scans a list
of spellings — a gate that catches one phrasing of a false statement licenses
every other phrasing. Following CLAUDE.md practice 4, the same generalisation
produced `test_every_test_a_standard_doc_cites_exists`, after two conformance
rows were found naming tests renamed by this milestone; it immediately found
three more dead citations and one live defect, a broken zero-dependency
self-runner in `tests/test_data_dictionary.py`.

- **The methods statement declares every approved correction (#174, review R-3,
  tier M, 2026-09-05)** — `report/methods.APPROVED_CORRECTIONS` had drifted four
  entries behind `docs/20_theory/02_approved_corrections.md`, and its guard could
  not see it: `test_statement_lists_every_approved_correction` looped over the
  tuple and asserted each key appeared in the statement rendered from that same
  tuple, so it proved the renderer worked and nothing else — the P-2 shape, in
  the project's own vocabulary. The four missing entries (the 2026-08-17
  constants sweep, LANDLOAD #133 and #134, WINGGEOM's 2026-08-30 closed-form
  integration) are the three most recent approvals plus one, and three of them
  change figures an analyst would compare against the printed manual, so the
  omission was not cosmetic: a stamped CSV said the numbers agreed with the
  source except in three named ways, when there were seven. The tuple grows a
  third field — the register entry's own `###` heading — which never prints and
  exists solely so the guard has a non-circular key; the guard now parses the
  register, scoped to its `## Register` section, and asserts the declared
  headings equal the approved ones in the register's own order. A companion test
  reads the *Withdrawn from scope* and *Considered and declined* sections and
  asserts none of their headings is declared, closing the inverse drift, which is
  the worse one: a refused deviation advertised as approved is a false claim, not
  a silent omission. The printed reference stops meaning "FAR" — it is the
  governing paragraph where a single paragraph governs and the source program
  otherwise (owner ruling, 2026-09-05), because `WINGGEOM` and `CONSTANTS`
  deviate from no regulation and the LANDLOAD pair span 23.479–23.493; the report
  table's column follows, `FAR` → `Reference`. No calc changes and no schema hop;
  `sloads/report/methods.py` is not in the note 44 OR-13 frozen manifest, so no
  OR-15 admission was needed. `SUMMARY_REPORT.md` §4.4 carries the completeness
  contract and the reference rule.

## Step — Module analysis is a LIMIT channel (design note 48, tier L, 2026-09-04)

**Objective.** Close **#154** — a `ConditionResult` holding no load still
carrying `safety_factor = 1.5`, so a geometry table prints an ULTIMATE banner —
and the larger finding the review of it turned up: the factor was applied on far
more surfaces than the contract's purpose requires. The `engine` CLI report was
scaling a mean takeoff torque 554.4 → 831.6 ft-lb, and every per-module analysis
page was reporting ultimate loads to an engineer reading limit values.

**Deliverables.** `report.LoadChannel` splits the per-module renderers
(`results_to_rows`, `critical_rows`, `summary_rows`, `load_cases_to_rows`,
`module_text_report`, `text_report`) into two channels, threaded through
`io.load_cases_csv`, `report.results_zip`, `report.methods` and
`app_shell.sidebar`. Fourteen call sites opt into LIMIT: `cli.py` (2),
`app/Home.py`, and eleven in `app/views/`. The parameter **defaults to
ULTIMATE** — the inversion of the usual instinct, and the only arrangement in
which the frozen `oracle_app` output is unchanged by construction rather than by
inspection. `ConditionResult.safety_factor` becomes `Optional[float]` with
`safety_factors.prescribes_factor` as the single owner of "prescribes none";
`units.LOAD_UNITS` / `units.is_load_unit` move to `units.py` now that the
boundary has a second consumer. `CONVENTIONS.md` §3, `CLAUDE.md`,
`PROGRAM_SPEC.md` and `GUI_design.md` record the contract;
`ORACLE_REPORT.md` is deliberately unchanged (OR-78).

**Test / Acceptance.** New `tests/test_limit_channel.py` (G-OR-44, G-OR-47): the
renderers default to ULTIMATE and the frozen `oracle_app/results.py` names no
channel; a LIMIT render emits no `-ULT`, states its basis, points at the ultimate
deliverables, and reports the calc's own value; a factorless condition prints no
factor on either channel. `tests/test_safety_factors.py` gains G-OR-46 — both
directions of the factorless rule across all seven fixtures, the stamp path
rather than the constructor, and the `case_ref` clause asserted against SELECT.
`tests/test_ultimate_contract.py` inverts into a channel table: a download built
by a channelled renderer must name its channel, because the ULTIMATE default
means silence is not neutral. That gate found a fourteenth call site
(`engine_mount.py`'s `load_cases_to_rows`) on its first run, which the note's
inventory had missed. The Imperial baseline was regenerated deliberately —
**184 of 330 digests moved**, all 118 `txt/*` and 66 of 118 `csv/*`, with every
`sbeam/*` (83), `case_index` (6) and `gear_report` (5) unmoved. `case_index`'s
immobility is the empirical check that SELECT's six critical wing cases were not
blanked. Full suite green; `ruff` and `mypy` clean.

**Key decisions.** OR-76 … OR-86, design note 48, agreed by the owner in session
on 2026-09-03 (R1–R4) and 2026-09-04 (R5, D-a … D-f). Four of the six D-items
were ruled against the note's first recommendation, each because tracing or
measuring the code changed the answer: D-a's scope (thirteen callers in four
groups, including the results zip reached from both GUIs), D-b (flipped to LIMIT
once the same string proved to have a second exit as a bare page download), D-c
(the marking convention already existed as M4-15, so the ruling retires it
rather than inventing another), and D-e (the family/`_EXACT` approach withdrawn;
the discriminator was already in the data model). **OR-86** adopts the owner's
principle that the factor is *stated, never applied*, and splits its scope:
0.8.2 takes the module-view half, and 0.8.3 removes the last multiply from
`sloads/export/` under its own boundary note, where `CONVENTIONS.md` §3 and the
Phase C mission statement change together. The `safety_factor` field survives
that endpoint because two families are computed already-ultimate at SF = 1.0
(23.367(a)(2), 23.561(b)) and nothing else records it. **G-OR-44 was amended
during implementation**: it promised byte-identity for the ULTIMATE default,
which cannot hold alongside OR-82, since a factorless condition now prints `N/A`
on both channels. The owner ruled the change correct on its merits — geometry,
weights and speeds should never have carried a factor — so the oracle GUI's
Results page shows `N/A` where it showed `1.5`. No number moves, no frozen file
is edited, and no OR-15 admission arises. Two items are filed and not fixed:
`is_load_unit` tests the unit alone, so ENGLOADS' mean takeoff torque still
reads as a load; and two examples are stored at 1-space JSON indent.

- **Xcg in %MAC in the oracle report's CG-case table (tier M, 2026-08-31)** — §2.2 stated
  every CG case as a fuselage station while the structural CG limits beside it, in the same
  subsection and on the same figure, are entered in percent of MAC. The reader was left to
  convert, by hand, against whichever XLEMAC and MAC they could find — and this suite resolves
  that pair two ways, a typed `envelope.xlemac`/`mac` override or the wing planform, so "the"
  MAC was not a single number a reader could safely assume. The table now carries the
  percentage beside the station and the note carries the relation in both directions together
  with the pair it applied and where that pair came from, which is what makes the column
  checkable rather than merely convenient. It is a change of reference, not a second analysis:
  the column reads `derived_geometry.station_to_pct_mac` against `mac_reference`, the same
  owners the limit lines use, and the section-2 guard that says the report invents no number
  was widened to admit exactly that — a case's own entered station, through that one relation,
  against that one reference — rather than by exempting the column. Where nothing resolves the
  cell is a dash with a stated reason, because `station_to_pct_mac` answers `0.0` on a
  degenerate MAC by contract and a column of zeroes reads as a centre of gravity sitting on
  the leading edge.

- **Report dates became pickers, and an unsigned row stopped printing one
  (`ORACLE_REPORT.md` §4, tier M, 2026-08-30)** — Asking whether the report's date fields should be pickers turned up a defect in
what was already there. The pickers themselves are straightforward — ISO storage,
one format per document, `sloads.models.report.parse_date` as the only place that
knows the format, since `oracle_app` may not import `datetime` (gate G1). The two
things worth recording are what the obvious implementation would have got wrong.

`st.date_input` defaults its `value` to **today**. Dropped in without thought, it
stamps the current date onto an issue date and three signature dates that nobody
filled in, and the title page then states that the report was issued and signed
today — the same class as the placeholder that printed "Not analysed" over the
generator's own gap, a control putting words in the author's mouth. Every picker
passes `value=` explicitly and an AST guard fails any `date_input` that does not.

The second was already shipped and the picker only made it easy to reach: the
document printed a signature date beside a ruled *name* blank, which reads as an
approval that occurred and was signed illegibly. An unsigned row now prints no
date; the value stays in the spec, because a planned date is legitimate, and it
is the printing of it against an absent name that is refused. The role is still
shown — naming who is due to sign claims nothing about whether they have.
Recorded as three SHALLs in `ORACLE_REPORT.md` §4, which previously said the
opposite by omission, with a **Dates and signatures** row in the section register.

- **The report's front matter became editable, and deselection became silent
  (`ORACLE_REPORT.md` §3, §3.2, §5, tier M, 2026-08-30)** — Four owner decisions
  from the GUI review, one of which reverses a standing rule and is recorded as
  a deviation rather than quietly applied.

  Section 1's prose and a new *Limitations and scope* subsection are now spec
  fields the page pre-fills and the author owns. The limitations default comes
  from `sloads.report.methods.methods_statement`, the single owner of that
  statement across every export channel, so the report opens saying what the
  CSVs and decks say; its own banner is stripped because the subsection already
  carries the title. Author ownership makes both a **snapshot** — they will not
  track a later change to the project or to the shared statement — which was the
  explicit trade: a signed issue must keep saying what it said when it was
  signed. An empty field still means *not yet edited*, so the renderer falls back
  to the default and a spec written before these fields existed renders in full.

  The analysis basis drops to project name and FAR 23 category, the category
  spelled out through `models.inputs.CATEGORIES` rather than a second mapping
  that could disagree with the widgets. The cost is stated in `ORACLE_REPORT.md`
  §5 rather than glossed: with weight, wing area and the design speeds gone,
  name and category are a weak answer to *is this the same airplane*, so the
  fingerprint is now the only thing printed in the document that detects a
  changed input — which is why it was kept. `_fmt` and `_wing_area_sqft` were
  deleted rather than left behind; an unused helper reads as one still wired in.

  **Deselection is now silent**, reversing OR-19 and departing from
  `SUMMARY_REPORT.md` §3.4, which this document otherwise inherits verbatim
  under OR-5 and whose purpose is that an analyst never receives a reduced
  document without being told. The deviation is recorded in `ORACLE_REPORT.md`
  §3.1 with its reasoning; `SUMMARY_REPORT.md` governs a different document and
  is untouched. The half that bites is numbering: sections are numbered by
  position among those that *render*, because numbering by workflow position
  would leave a hole in the printed sequence and every reference after it would
  name the wrong section. The excluded step keeps its plan row so the page's
  preflight still shows the author their choice registered.

  Two follow-ups from the same review. The limitations pre-fill drops six of the
  statement's blocks, and the filtering lives in the report's `default_limitations`
  rather than in `methods.py` — that statement is the single owner for the CSV
  and deck exports too, and dropping blocks at the source would silently thin
  what a forwarded file carries, which is the one thing an in-band
  self-describing block exists to prevent. The guard asserts both halves: gone
  from the pre-fill, still present in the shared statement.

  The analysis basis regained two rows: the sloads version that wrote the
  document and the schema version of the project definition it read. The tool
  version is handed to `anchors()` rather than looked up there — reading
  installed package metadata is filesystem work `sloads.report` does not do, and
  the build already resolves it once for `build.json`, so resolving it twice is
  how a document and its own stamp come to disagree. With no version supplied
  the row is omitted rather than invented: a document naming a build it did not
  come from is worse than one that is silent.

## Step 155 — The oracle report states the fuselage loads (tier L, 2026-09-06)

**Objective.** Give the oracle technical report its second load-bearing section: the
fuselage loads, as five subsections and a lettered appendix, built from the
`fuselage_loads` step (`NETLOADS`, Reference 1 Ch 15 p103) without the report computing
anything of its own.

**Agreed first.** Design note 44 §13 (**OR-94 … OR-102**), §15 (**OR-108 … OR-113**) and
§16 (**OR-114/OR-115**), with the carry-through half answered by design note 50 — all
settled with the owner in session on 2026-09-05, before any code. Gates **G-OR-53 …
G-OR-59** and **G-OR-64 … G-OR-68**.

**Deliverables.**
- `report/oracle_sections.py` — 4.1 the fuselage beam, 4.2 the run register and notation,
  4.3 the critical fuselage loads, 4.4 the beam closure and the wing-attach fitting loads,
  4.5 the distributions, and Appendix C's station table. The subsections are titled here
  and numbered by `subsection_number`, the one numbering owner.
- `report/oracle_content.py` — `BODY_LOAD_STATIONS` in third appendix position, and
  `"fuselage_loads"` in `IMPLEMENTED`, which is the whole of the switch: the OR-32
  placeholder that had been holding the slot becomes a section.
- `modules/body_loads.py` — `run()` publishes the p198 conditions; `critical_fuselage_conditions`
  and `case_list_source` publish the case identity and the provenance a consumer needs
  without a second call to SELECT.
- `modules/select.py` — the unbalanced pitching moment about the CG on the four maneuver
  conditions.

**Key decisions.**
- **Five subsections rather than section 3's four.** §15 gave the section a summary an
  analyst turns to first, and folding the manual's own summary into a subsection about
  closure machinery would have made it a footnote to the machinery.
- **The section projects the published `ModuleResult`; the builder is read for the station
  table only.** This is OR-95 rewritten rather than withdrawn, because it turned over: the
  original ruling had section 4 read `build_body_loads` throughout, on the grounds that
  there was no result to project. There was no result because the module was discarding
  one, which is the defect below.
- **`body_loads.run()` returns the four conditions it already builds (OR-108).**
  `select_fuselage` computes blocks 1, 2, 3 and 7 of p198 — labels, FAR references, V-n
  case numbers and three quantities each — and `run()` returned an empty `ModuleResult`,
  so the oracle GUI's Fuselage Loads page said *"Body Loads produced no conditions."*
  beside a 92-row station table. One owner, not four: the same result now feeds both GUIs,
  the CLI, `load_cases_csv` and the report, through renderers that needed no edit. The
  alternative — each surface calling `select_fuselage` for itself — is rule 3's failure
  mode with a deliverable on the end of it. **Admitted under OR-15** by the owner on
  2026-09-05; additive, no value changes, and the frozen manifest is updated in the same
  commit per G-OR-9.
- **The unbalanced pitching moment is published from SELECT with its equation recovered
  and cited (OR-111).** It was the one field of p198 this project could not state, and it
  is *not* reconstructible from the printed page by inspection: the arm closes against
  neither the 25 % nor the 50 % MAC until the balanced elevator load is subtracted. From
  Appendix C, `SELECT.BAS` 5210: `PITCHMOMH5CASE = -(LT50UPTEUNCK - LT50) * (XT50 -
  XXCG(H5CASE))`, and 5410 for the checked pair. The increment is measured from the
  balanced 50 %-chord load and the arm runs from the CG to the 50 % tail MAC; verified
  against the printed page on both, `-(-1346.496 - (-113.6319)) × (270.357 - 73.09) =
  +243,203.9` against a printed `243203.5` and `-218.3436 × (270.357 - 72.64) = -43,169.9`
  against `-43170.23`. **The sign asymmetry is the original's** — the unchecked expression
  negates and the checked one does not — and is ported as found, not tidied. Second
  **OR-15 admission**, over `sloads/modules/select.py`.
- **`FS 50 PERCENT HORIZ TAIL` prints the real station (OR-112).** The manual prints `0`
  in both fuselage blocks while its own tail-loads echo states `270.357`. OR-111's
  arithmetic settles it independently: the moment closes only with the real station, so
  the original computed with it and printed zero — a defect in its print, not a modelling
  choice. Registered in `docs/20_theory/02_approved_corrections.md`, so an analyst
  comparing against the page finds it explained rather than discovering it.
- **Blocks 4 and 5 are read from SELECT and carry their reference (OR-109/OR-110).** The
  manual's own device — *"SEE HORIZONTAL TAIL LOADS FOR FURTHER DATA"* — is the answer to
  the two-pages-one-number objection: the reader gets the value where the fuselage question
  is asked and is told where it is derived. Weight and CG are case identity and are stated
  by lookup from the case's CG name, which is why `CG4 → 73.09 in` and `CG3 → 72.64 in`
  reproduce p198's printed `XCG` to the digit.
- **The advisories are carried because each names something true (OR-113).** Block 7's
  pitching-acceleration warning states a limitation this analysis still has: Ch 15 resolves
  the fuselage inertia into a linear and a pitching load factor, and only the linear half
  is modelled (**M4-21**, `θ̈ = 0` on these balanced trim cases). Reproducing it therefore
  states a true property of the delivered numbers rather than decorating them, which is the
  one good reason to carry printed prose at all.
- **The section states what it does not deliver rather than tabulating zeros (OR-100).**
  Ch 15's beam is a symmetric-flight vertical solve, so there is no lateral shear and no
  lateral bending here; a column of zeros would read as a measured zero. The notation table
  names the three symbols the section uses and nothing else.
- **4.2 states its own load-factor sign convention, and states that it is not section 3's.**
  Section 3 prints the inertia load factor and section 4 the airplane's own, so a reader
  carrying one section's rule into the other reads every condition backwards. This is
  OR-58 applied to a section whose convention differs, and it is why the sentence is
  written out here rather than cross-referenced.
- **An assumed spar station is stated beside the numbers it sized (OR-97).** The
  wing-attach fitting loads are the sizing loads for the fittings, and on both report
  fixtures they are computed against a carry-through nobody entered. The provenance is a
  column of the fitting-load table, in the same visual field as the loads, and it is stated
  as a fact about the airplane rather than about the tool. The structural half of the
  finding was fixed rather than filed, by design note 50: the carry-through is an entered
  fuselage station, so the field a reader would go looking for exists.
- **No sloads load carries a Subpart D special factor (OR-114/OR-115).** 4.4 states the
  consequence where the fitting loads are printed — the casting, bearing, fitting and
  hinge factors of 23.619/621/623/625 qualify a material allowable or a fitting's strength
  at the stress analysis, not the external load a loads analysis delivers, and a fitting
  factor applied here would be applied twice.

**Test.** Twenty-one gates in a new `tests/test_oracle_report_fuselage.py`, one file for
one section's gate set. Among them: the five subsections are numbered by the numbering
owner and the appendix letters to C behind the reserved A and the wing's B; every load
column carries no `-ULT` **and** every load table carries an `SF` column, asserted in both
directions; the printed value is the module's own unscaled result; 4.1 states its beam
derived and prints its total; a project with no beam mass renders the `ABSENT` state in
both the section and its appendix and still builds a whole document; the fitting table
reads `assumed` on the shipped fixture and `entered` on a project that enters its spar
stations, through the projection; a constructed closure-artifact project states its state
and plots nothing; the register names its path, its sign convention and its one
negative-load-factor condition from the analysed set; Appendix C and
`body_span_load_csv` agree row for row on GID, station, load and factor; `body_loads`
publishes one condition per printed block on both fixtures, each with its FAR reference and
V-n point; blocks 4 and 5 equal SELECT's own values by comparison rather than by both
matching a literal; and OR-111's two reconstructions reproduce the printed page within the
oracle tolerance with the 50 % tail station entered and never zero.

Two existing wing gates were restated rather than relaxed, both position-dependent
assertions that a third appendix broke without saying anything untrue: the appendix
lettering test now slices from the first appendix instead of from the end of the document,
and the landscape test counts one balanced environment per landscape section instead of
exactly one. The frozen Imperial baseline moves on two channels only — `body_loads` and
`select`, in every example — which is the shape an additive publication should have.

## Step 157 — The oracle report states the horizontal tail's loads (tier L, 2026-09-07)

**Objective.** Give the oracle technical report its third load-bearing section: the
horizontal tail, as five subsections and a lettered appendix, built from the
`tail_loads` step (`TAILDIST`, Reference 1 Ch 10) without the report computing
anything of its own — and settle how a step that publishes two surfaces becomes two
sections.

**Agreed first.** Design note 44 §17 (**OR-128 … OR-138**), settled with the owner in
session on 2026-09-06 before any code, and corrected in place before implementation
when one of its premises turned out to be wrong (OR-129/OR-130a, below). Gates
**G-OR-80 … G-OR-88**. The section was then reviewed by the owner against the built
document on 2026-09-07 and amended: a fifth subsection, the case reference as the key
of every table, the aerodynamic state ahead of the loads it produced, the
hinge-moment absence stated, and Appendix D reduced to an applied-load deck.

**Deliverables.**
- `report/oracle_content.py` — `SectionSplit`, `SECTION_SPLITS` and the split run in
  `section_plan`: one declared partition per step, numbered like any other section.
  `HTAIL_LOAD_STATIONS`/`VTAIL_LOAD_STATIONS` join `APPENDICES` as D and E.
- `report/oracle_sections.py` — one builder for both surfaces, parameterised by
  component, so sections 5 and 6 are provably the same analysis read twice rather
  than two copies kept in step. Plus `_tail_station_appendix` and `_scalar_channel`,
  which generalises `_length_channel` to the quantities the deliverable unit set has
  no column for.
- `modules/select.py` — the elevator load on every horizontal-tail condition and the
  rudder load on every vertical-tail one (OR-132).
- `tests/test_oracle_report_tail.py` — 22 gates, one file for one section's set.

**Key decisions.**
- **The tail is two sections (OR-128).** One grouped section with the steps as
  subsections forces method-major numbering — chordwise, then spanwise — and splits
  each surface across two headings. An analyst reads by surface: the horizontal
  tail's totals, its chordwise profile and its span loads are one story.
- **G-OR-2 becomes coverage rather than identity (OR-129).** The old gate asserted
  the section list *equals* `oracle_steps()`. With one step across two sections the
  rule becomes *one step, one declared partition*, and the replacement gate is
  stronger than the one it replaces: every published condition must land in exactly
  one section, so a condition that lands in none — or in two — fails. The partition
  key is `component`, already a field on both tail result types, so nothing enters
  the analysis to serve the report.
- **A premise of the note was wrong, and was corrected before implementation, not
  after (OR-129/OR-130a).** The drafted §17 said the tail was *two* module-backed
  steps and sized the amendment against that. It is one: `tail_span_loads` carries
  `bas=None` and produces no slice a `.BAS` step requires, so `oracle_steps()`
  excludes it — it is not an oracle GUI page and cannot be a derived section. The
  correction makes the amendment smaller and leaves the agreed section shape intact,
  but it moves where 5.4's numbers come from: the spanwise loads are **appendix
  content read from a non-step producer**, which is the shape the wing already has
  (§3.2 owns the notation, Appendix B carries the stations as a view of the export
  owner, OR-59/OR-64). Recorded in the note in place rather than quietly.
- **Every condition states its control-surface load (OR-132).** Measured before
  deciding: 2 of 9 h-tail conditions carried an elevator load and 2 of 4 fin
  conditions a rudder load. 5.2 exists to be read across, and a column blank on seven
  of nine rows states nothing the analysis could not supply — `elevator_load` and
  `rudder_load_parts` are pure functions of the split every condition already holds.
  Published in `_htail_condition`, the one constructor they all pass through: one
  owner, not nine call sites. **Second OR-15 admission**, and additive by
  construction — the one insertion that would have reordered an existing CSV column
  (`SIDE GUST`'s `Yaw inertia IZZ`) was rewritten to append, because OR-13 admits
  additive and a reorder is not.
- **The unsymmetrical row states its split beside its elevator load (OR-135).**
  Adjacency is the ruling, not presence: alone, an elevator load on a 23.427(a) case
  reads as one surface's load when the case's whole content is that the two sides
  differ. So the gate asserts them same-table, same-row — a gate checking only that
  both appear *somewhere* would pass the arrangement the owner rejected. The split
  itself needed no code: the condition already published `rh_side_load`,
  `lh_side_load` and `other_side_percent`.
- **The document is not pinned to the Appendix A tail figures, and says why.**
  Writing G-OR-83 found that the shipped `ga6_normal` cannot reproduce them: the
  printed values are selected from a three-altitude envelope while every case the
  example delivers is at sea level, so the search governs on different points and
  lands 0.3–3 % away. That is backlog **#164**, an open item this section did not
  create. Pinning the document to those numbers would pin it to a fixture defect, so
  the oracle comparison stays in `test_select.py`/`test_taildist.py` where the right
  fixture is, and the document's gates assert what the document owes: that it prints
  the module's own values unscaled, and that every condition the oracle names is
  present under the name the oracle uses. Stated in `ORACLE_REPORT.md` §3.6 and in
  `theory_sources.md` rather than left for the next reader to rediscover.
- **Section 5 carries the pointer to the non-conventional-tail limitation, not the
  statement (OR-133).** Its own loads are unaffected, so the statement belongs in
  section 6 where the loads are withheld — but a reader who starts at the horizontal
  tail must not meet the restriction for the first time two sections later.

**Test.** Twenty-two gates in a new `tests/test_oracle_report_tail.py`. Among them:
the section renders five subsections numbered by the numbering owner and the tail
appendices are D and E behind A, B and C; the analysis body is consecutively numbered
with no gap after the split; every published tail condition lands in exactly one
section and every section names the step and component it was built from, asserted in
both directions; every load column carries no `-ULT` **and** every load table carries
an `SF` column, with the four tables that hold no load asserted to carry none; the
printed totals and pressures are the module's own, matched value for value rather
than against a literal; the chord stations print once and the aerodynamic constants
carry no factor; every condition states its aerodynamic state or the fixed reason the
method defines none; every condition states an elevator load on both fixtures; the
unsymmetrical row states its split adjacent to that load while every symmetric row
states none; Appendix D and `tail_span_csv` agree row for row on identity and load;
every symbol an appendix column uses is defined in 5.4's notation table; and a project
with no tail renders the absent state and still builds a whole document.

Six existing gates were restated rather than relaxed, all of them encoding the
pre-split assumption: the G-OR-2 derivation gate became the partition gate, two
state-precedence gates now key on section rather than step keys, the document-title
gate accepts a split step taking its headings from its splits (and asserts it carries
no step-level title nothing would print), and the fuselage appendix-lettering gate now
slices from the first appendix instead of the end of the document — the same
position-dependence a third appendix broke one iteration ago, in a second place.

**Amended in review (owner, 2026-09-07).**
- **The section opens with the surface it was run on.** A fifth subsection ahead of the
  rest, on section 3.1's shape: the planform with its elevator, the loads reference axis
  drawn through the very stations the distributed loads are stated at, and the axis
  station by station. The aerodynamic constants move here from the chordwise subsection
  — they are derived from the surface's geometry, not from the pressures they scale.
- **Every table keys on the case reference.** `HT-01`, not the condition name: the case
  reference is the machine identity every other deliverable uses (M4-9), so the name and
  its regulation are stated once, in the register, instead of repeated in four tables.
  The register gains the safety factor, so the factor is stated wherever the case is
  named. The aerodynamic-state table prints ahead of the loads table — a reader checks
  what the airplane was doing before reading what that did to the surface.
- **5.5 says why there is no hinge moment.** The question was the owner's, and the
  answer is not "missing input": the hinge line is known — it is the chordwise station
  the pressure distribution is built on — and the elevator load is modelled smeared into
  the surface. A hinge moment needs the hinges' and the actuator's *span* stations,
  which no fixture enters. The subsection names both and says entering them selects the
  discrete load path. The two control columns go rather than print dashes, because a
  column of dashes is not a statement.
- **Appendix D is an applied-load deck and nothing else.** `Case | GID | X | Y | Z |
  Fz | SF`, the point in airplane axes from the same mapper the exported deck uses.
  Appendix B keeps both halves because the wing section is where a reader checks a beam
  model's own answer; the empennage appendix is a deck to load a model *with*, so what
  the structure carries is stated at the root in the section. **There is no `Fx`
  column**: this analysis models no chordwise force on either tail surface and no
  empennage dihedral, so the other components are absent by construction rather than
  zero by measurement — OR-61's ruling, that a column of zeros reads as a measured zero.
  The appendix states both absences rather than leaving the frame to be inferred.

## Step 0.8.2-1 — The oracle technical report: page, spec and issue package (note 44 §7–§9, tier L, 2026-08-30)

**Objective.** Deliver iteration 1 of the oracle technical report (backlog row
24, #151): a working end-to-end artifact — fill in a report's identity in the
oracle GUI, press *Build issue package*, and get a directory on disk holding a
compilable document and everything needed to reproduce and audit it. The report
is a *view* of an analysis that is already oracle-locked, so the milestone runs
under note 44 §6's freeze throughout.

**Deliverables.**
- `oracle_app/report.py` — the Report page: package location and picker,
  document identity, abstract, signatures, distribution and marking, the
  document's unit system, section selection, a preflight table, provenance, and
  the build control. Registered on `st.navigation` in `oracle_app/Oracle.py`
  (the one admitted edit to a frozen file, OR-13 item 2 as widened by OR-16) and
  deliberately **not** in `register_pages`, which stays exactly `oracle_steps()`.
- `sloads/models/report.py` — `ReportSpec`, `SignatureRow`, `RevisionRow`,
  `ProjectIdentity`, `REPORT_SCHEMA_VERSION`, `default_spec`, `is_draft`.
- `sloads/io.py` — `load_report`/`save_report`/`report_spec_to_json` and the
  package's path owners (`report_package_dirname`, `default_report_root`).
- `sloads/report/fingerprint.py`, `oracle_content.py`, `oracle_latex.py`,
  `oracle_package.py`; `sloads/export/report_package.py` for the writing.
- `docs/10_standard/ORACLE_REPORT.md`, created per OR-9 with its section
  register and conformance list.

**Test.** `tests/test_report_spec_io.py`, `tests/test_oracle_report.py` and
`tests/test_oracle_report_package.py` carry G-OR-1 (both example airplanes),
G-OR-2, G-OR-5/16, G-OR-6, G-OR-7, G-OR-10, G-OR-11, G-OR-12, G-OR-13, G-OR-14
as widened by OR-35, and the new G-OR-18/G-OR-19. G-OR-15 and G-OR-17 are
written but **vacuous until the first analysis section ships data**, and their
docstrings say so rather than letting a green tick imply coverage. The
summary report gained a structural companion to its standalone guard
(`test_the_summary_content_sets_no_data_ref`).

**Key decisions.**
- *One renderer, two emission modes.* `Table` gained an optional `data_ref` and
  `report/latex.py`'s emitters were promoted to public names; the oracle
  renderer owns only its furniture and borrows every emitter. Forking the
  renderer would have duplicated the column-width model and the `longtable`
  machinery, and would have made the eventual main-report merge a rewrite. The
  summary report's bytes did not move, which its existing byte-identical test
  proves.
- *The package directory is the spec's home* (OR-28, superseding OR-24), and the
  as-built stamp moved to `build.json` (OR-30). One issue, one directory; and
  because the builder never writes the file the user edits, the byte-identical
  rebuild gate needs no list of stamped fields to exclude — a carve-out that
  would have had to be maintained for every field the spec ever grows.
- *A third gap state.* "Not yet implemented" is distinct from "excluded by user
  selection" and "absent for missing inputs" (OR-32), with a precedence that
  changes once a section is built. Collapsing it into either would have told the
  reader that a colleague chose to omit a section, or that their own data was
  incomplete, when neither was true — and it is what lets G-OR-2 hold from the
  first commit.
- *The manifest is a real §4.7 manifest* (OR-35). The `SUMMARY_REPORT.md` §2
  *Data reference* clause conditions the packaged-report permission on a §4.7
  manifest, so the lighter name-and-hash list OR-22 described would not have met
  the rule this milestone itself wrote.
- *The fingerprint rides on `field_registry.reduce_to_oracle_inputs`*, the
  existing owner of oracle scope, so G-OR-6 and G-OR-13 are the same guarantee
  rather than two scope lists that can drift. Free-text document control is
  excluded from the hash: renaming the engineer cannot move a load, and a
  warning that fires on noise is ignored on signal.
- *The DRAFT watermark adds no LaTeX package* — TikZ machinery the shared
  preamble already loads. The preamble is shared with the summary report, and
  acquiring a dependency there should be earned.
- *The page computes nothing* — no path, hash or clock read. The oracle GUI's
  import gate forbids `os`, `json`, `hashlib` and `datetime` outright, which
  turns that from a convention into something enforced.
- *Deferred, with reasons stated:* the PDF compile (OR-36 — `compile_pdf` takes
  a source string and cannot resolve a package's relative reads) and the example
  report file (OR-37 — OR-28 leaves nowhere for it to live).

**Found by compiling the document rather than by reading it.** Five defects
survived a green test suite and were only visible in the rendered PDF, which is
the argument for OR-8's rendered-sample approval step:

1. Every placeholder printed under a bold **"Not analysed"** — *absence's*
   wording — because that lead was hard-coded in the shared renderer. The model
   had three correct sentences and the reader saw one wrong phrase. `Section`
   gained an `absent_lead`, the states own their leads, and the guard now
   asserts the **rendered** lead rather than the model's strings.
2. The title page listed all thirteen not-yet-implemented sections as though the
   reader's issue had been cut down. They are now summarised in one sentence,
   with only the per-issue exclusions and absences itemised.
3. The footer overprinted the classification marking, the load basis and the
   draft sentence on one line. The centre slot is stacked and the footskip grows
   on a draft.
4. `\begin{titlepage}` reset the page counter, so a two-sheet cover produced
   "Page 1 of 4" on the third sheet — and suppressed the page style, dropping the
   classification marking from the page most likely to be photocopied alone.
   Dropped in favour of a plain page and `\clearpage`.
5. The provenance block printed a fingerprint with no anchors, because the
   builder never computed them. It does now: the human half of OR-21 is the half
   that actually gets used.

Also fixed before it could bite: Streamlit resolves a keyed widget from session
state and ignores a later `value=`, so opening a second issue would have redrawn
the first one's fields over it and saved them back. The page retires its spec
widgets on a switch, with a drift guard over the retirement list — the failure
mode of forgetting one is silent data loss, not an error.

**Found by using the page.** A GUI review against `ga6_normal` changed how the
report's location is chosen, twice. The first build offered a free-text path
box, which is the one control the rest of the app deliberately does not have:
the sidebar's *Save to disk* offers no location choice at all (#94, C210-48)
because a browser page cannot open an OS dialog for a server-side write. That
was replaced with a resolved root and a click-through folder browser — and the
answer was still wrong, because a new report has to be able to go somewhere the
browser cannot reach in a reasonable number of clicks.

The resolution takes the constraint apart rather than working around it: the
oracle GUI is run **locally**, so the machine serving the page is the machine
the user is sitting at (OR-22), and the operating system's own folder chooser is
reachable after all. `sloads/export/directory_dialog.py` runs it in a
subprocess — `osascript` on macOS, `FolderBrowserDialog` on Windows,
`zenity`/`kdialog` otherwise — on the same footing as `export/pdf.py` shelling
out to a TeX engine. Not `tkinter`: this interpreter has no `_tkinter`, and on
macOS Tk must own the main thread, which a Streamlit script never does, so an
in-process dialog would abort the app rather than open one. Every non-answer —
no helper, Cancel, timeout, a path that is not a directory — returns `None`
alike, because the caller's response to all four is to leave the folder alone;
the click-through browser stays as the fallback, since a chooser that silently
does nothing would leave no way to set the location at all.

Three defects came out of the same review, one of them shipped:

1. **Browsing to `~/Desktop` crashed the page.** macOS keeps Desktop, Documents
   and Downloads behind TCC, and `discover_packages` called `listdir`
   unguarded. The first fix was worse than none: it hardened the sibling
   `list_subdirs` and left `discover_packages` bare, which is precisely the
   half-swept fix rule 4 exists to forbid. Swept properly, the same shape turned
   up in shipped code — `io.list_saved_projects` guarded a *missing* projects
   directory and not an unreadable one, carrying the identical crash into the
   sidebar for anyone whose projects folder sat somewhere protected. Both now
   answer "no packages / no projects *that this process can open*", which is the
   question the caller is actually asking, and both are held by a test that
   `chmod 000`s a real directory.
2. **Choosing a folder is not being granted it.** The OS chooser returns a
   TCC-protected path quite happily and the write then fails at the end of a
   page the user has already filled in. `is_writable` is checked when the folder
   is chosen, and the warning names the remedy; `Save spec` now reports that
   failure as a message, which only *Build* did before.
3. **Opening a package discarded unsaved spec edits silently.** Selection change
   loaded immediately, where the sidebar puts the same act behind a button and a
   guard. Selecting is now browsing, an explicit **Open** does the discard, and
   an unsaved spec warns first.

And one caught before it could ship: the first test written for the folder
dialog *called it*, which on any machine with a desktop session opens a Finder
window and holds the suite behind it — visible only as a jump from 2 s to 31 s.
It is stubbed at the subprocess boundary now, testing the decision logic without
opening a window. The same test carried an `assert x is None or True`, which
would have passed for ever.

- **Section 2.1's planform figures (note 44 OR-45, tier M, 2026-08-31)** — iteration 2
  shipped section 2.1's surface tables and left the "planform figures" half of OR-45
  unbuilt, so 2.1 was the only Loads Configuration subsection with no drawing. It now
  carries one per main surface: wing, horizontal tail and vertical tail, each the entered
  edge polylines closed into an outline with its control surfaces filled on top and every
  region labelled with the area its own table prints. The work is a new emitter,
  `sloads/report/planform_tex.py`, dispatched by figure key rather than through
  `plots_tex._EMITTERS` because a planform needs `axis equal image` and therefore takes no
  height — and dispatched on the *exact* key, because the V-n figures' `vn_<index>` keys
  already miss `_EMITTERS["vn"]` and fall through to the default emitter harmlessly, which
  a planform would not: it would silently lose its equal axes and be drawn to the wrong
  shape. Three decisions carried it. Figures stay TikZ source rather than becoming
  matplotlib PNGs: `SUMMARY_REPORT.md` §2's image prohibition was reaffirmed verbatim by
  the 2026-08-30 *Data reference* amendment, `PackageMember.content` is a string, a PNG
  cannot be self-describing to §3.1, and a polygon needs none of it. No hinge line is
  drawn while the suite carries only the fwd/aft-of-hinge *areas* and derives a chord
  station from their ratio — drawing that would print an inference on a
  rectangle-equivalent with the standing of entered geometry — and the caption says so;
  the real line arrives with #156 (band B4). And the vertical tail is drawn in the
  fuselage-station/waterline plane and never mirrored, decided by the figure's frame rather
  than by `SurfaceInput.symmetric`, which `examples/baron_58.project.json` sets `true` on
  its fin. The areas are read from the owners 2.1 already cites, so no number in the
  section can be printed twice with two values; a region whose total area no table states
  (the aileron, which carries only its areas forward and aft of the hinge) is drawn and
  named without one rather than summed here. Guards in `test_oracle_report.py` hold the
  figure set against the declaration both directions, every plotted vertex against the
  entered polylines, every labelled area against the table cells, the absent-surface state
  against an empty axis, and the fin against the mirror flag.

## Step 152 — The oracle technical report, section 2: Loads Configuration (tier L, 2026-08-30)

**Objective.** Deliver the first analysis section of the oracle technical report under
design note 44's OR-8 protocol — content spec agreed with the owner, implemented, and
approved from the rendered PDF — covering the airplane configuration the design loads
were computed for.

**Deliverables.**
- `sloads/report/oracle_sections.py` — one content builder per step key, turning a
  `ModuleResult` into `Section` tables and figures. Computes nothing: unit conversion is
  `units.convert_results` and the ultimate boundary is `report.render`, both asked rather
  than re-implemented, which is what makes G-OR-4 hold by construction rather than by
  inspection.
- `oracle_content.DOCUMENT_TITLES` — the heading a section prints, separate from
  `WorkflowStep.title`. The workflow label exists for the oracle GUI's navigation; a
  reader of the PDF has no concept of it, and renaming a nav item must not retitle a
  report somebody has already signed. Guarded both directions.
- `oracle_content.SECTION_GROUPS` + parent/child numbering (`subsection_number`,
  `heading`) — Section 2 groups four steps as 2.1–2.4. Declared as data, so a later
  grouping needs no new logic; members are guarded contiguous in workflow order, because
  a group that skipped a step would collect whatever sat between its members.
- `oracle_content.run_sections` — the one place a module is run for the report, so the
  page's preflight and the document it writes can never describe different analyses.
- Section 2.4's V-n figures, one per loading/altitude block, plus a corner load-factor
  table.
- `ORACLE_REPORT.md` §3.3 (the section's SHALL list) and §3.3.1; note 44 §10
  (OR-38…OR-44); register rows and conformance items.

**Test.** Twelve new gates in `tests/test_oracle_report.py`: every printed number is one
a module produced, checked against the modules run independently of the report; nothing in
Section 2 is marked ultimate or states a safety factor; the declared envelope traversal
matches FLTLOADS' own case order; every plotted vertex is a produced case; one figure per
block; the paired tables' keys still exist upstream; wing area is stated once in the whole
section; a `far_reference` that is not a regulation is not cited as one; every analysis
step has a document title distinct from its workflow label; group members are contiguous.
The existing structural gates were rewritten for a section tree rather than a flat list.

**Key decisions.**
- **The V-n envelope is the polyline through the produced design points, not
  `build_vn_diagram`'s curve** (OR-40). That builder's own docstring calls it an
  approximate Structural-Speeds sanity plot; its stall boundary assumes constant CLmax and
  predicts n = 3.51 at the STALL +N corner of the reference GA wing where FLTLOADS
  computes 3.80 — 8% low, because the real boundary follows CL rising 1.395 → 1.512 with
  α plus compressibility. Drawing it would put the report's own design points visibly off
  their own boundary. Sampling the true curve is frozen-module work, backlogged and parked
  with that number.
- **The document is built from the oracle projection** (OR-43). `build_oracle_document`
  now reduces through `field_registry.reduce_to_oracle_inputs` — the same reducer the
  fingerprint hashes through — so "a field the oracle GUI cannot set moves neither the
  hash nor the document" is one guarantee with one owner. This was found by G-OR-6
  failing, not by inspection: Section 2 quotes each module's certification basis, and on a
  concept project the speeds module takes the Part 25 Mach-margin route and says so in its
  note, so a concept-only field reached the printed page. Suppressing that one field would
  have left every later section free to find another.
- **Section 2 states no load in force or moment units** (OR-44). Values still route through
  the ultimate boundary rather than being hand-formatted, so the section never decides what
  a load is. A first draft explained the absent `-ULT` marker with a note saying geometry,
  mass, speeds and load factors "are not loads"; the owner corrected that — **n is a limit
  load factor, so a load factor is a load** — and the note was removed rather than reworded.
  Where a load factor is reported the document identifies it as LIMIT, at point of use.
- **The `data/*.csv` externalisation of OR-23 is deferred to its own iteration** (OR-42),
  taking G-OR-15 and G-OR-17 with it.
- **Two upstream findings recorded rather than fixed**, `sloads/modules/**` being frozen
  (OR-14): the four modules stamp `safety_factor=1.5` on non-load conditions — geometry,
  inertia, design speeds — which affects no value but is a false claim, filed as an issue;
  and the configuration module's `far_reference` is `"configuration"`, which printed as
  "Certification basis: 14 CFR configuration" until the report learned to cite only
  references that begin with a part number.

- **The speed/altitude envelope in the oracle report's §2.4 (tier M, 2026-08-31)** — §2.4
  drew four V-n diagrams and nothing that showed what they are slices of. The operating
  envelope itself was in the tool (the Structural Speeds page has drawn it since Step E7) and
  in the summary report, but the summary report's version began at the shoulder altitude,
  which is where MACHLIM's table begins — and that is exactly the half of the boundary where
  nothing is happening. Below the shoulder each limit is constant in equivalent airspeed;
  above it, Mach-limited; the kink between them is the shoulder, and it is the one feature of
  the figure a reader is looking for. Drawing from sea level costs no arithmetic: the
  sub-shoulder segment is the shoulder row's own speed held constant, which is what the
  shoulder altitude means, so every speed on the figure is still a value MACHLIM returned.
  Vh is marked rather than drawn: `speeds.vh_kt` is a sea-level maximum level-flight speed and
  the analysis carries no altitude variation of it, so a full-height line would assert a
  boundary nothing computed — as a sea-level marker it still shows the thing worth seeing,
  where Vh sits against VC, whose FAR floor is capped at 0.9 Vh. The figure has one builder
  shared with the summary report rather than an oracle-only copy (OR-7), so the summary
  report's own speed/altitude figure changed in the same step — deliberately, and for the same
  reason the weight/CG figure did a day earlier: two documents drawing one airplane two ways
  is the defect the shared-owner rule exists to prevent.

- **The title page reduced to identity and signatures; front-matter defects
  fixed (`ORACLE_REPORT.md` §3–§5, tier M, 2026-08-30)** — Reading the compiled PDF, rather than the renderer's output, is what produced
this change — the third time in this milestone that a green suite and a correct
model still put something wrong on the page.

The cover was carrying identity, document control, the analysis basis, the input
fingerprint, a thirteen-item list of sections the generator cannot yet build,
the signatures and the distribution statement. It ran to two sheets and broke
where it hurts: the signature block landed alone on sheet two, so the approval
record sat on a page carrying no report number, no revision and no title. The
anchors and the not-carried list moved to the end of the introduction, which is
where a reader meets them before any analysis; the cover keeps what identifies
the document and who signed it. `ORACLE_REPORT.md` §3, §4 and §5 previously
required the gap list *on the title page* and are amended, and the guard is on
the cover rather than on the introduction because the failure mode is additive —
a block added back renders perfectly and only the layout suffers.

Three defects came out of the same two pages. The footer printed the
classification marking through the load-basis sentence: `fancyhdr` places `[L]`,
`[C]` and `[R]` independently and nothing stops them colliding, so the two
statements a reader most needs to trust were illegible whenever the marking was
a real phrase. It is now one full-width `tabular*` whose columns share the line
by construction rather than by fitting. The gap sentences were written to follow
a colon and are printed after a bold lead and a full stop, so every placeholder
read "**Not yet implemented.** this revision…". And the introduction still told
the reader that sections not carried were "listed on the title page" after they
had moved — a cross-reference that a reader follows and finds nothing at, now
checked against the location it names.

Checking the remaining pages found the document breaking its own rule in the
front matter. The List of Figures and List of Tables rendered as headings with
nothing beneath them — an absence stated by omission, which is precisely what
every placeholder section exists to avoid, and which a reader is more likely to
read as a generator failure than as "there are none". Both now carry a sentence,
and both are added to the Contents, since the abstract already was and two kinds
of front matter treated differently in one document reads as an oversight. The
emptiness test recurses into subsections: a table one level down still puts a
line in the list, and the document would otherwise state the opposite of what
the reader is looking at.

That fix cost a page — the List of Tables landed alone on a sheet — which
exposed the cause as `\parskip`. The document sets it to 0.6 em and a contents
list inherits it, so seventeen entries spaced like paragraphs filled the page by
themselves. Confined to a group around the front matter, which leaves the body's
paragraph spacing alone and puts all three lists back on one page.

## Step 159 — The oracle report states the vertical tail's loads (tier L, 2026-09-07)

**Objective.** Close the tail partition: give the oracle technical report its fourth
load-bearing section, the vertical tail and its rudder, as the mirror of section 5 —
and make the restriction sloads has always had on non-conventional empennages a thing
the document *states* rather than a thing a reader has to know.

**Agreed first.** Design note 44 §17 (**OR-128 … OR-138**), agreed with the owner on
2026-09-06, which had already settled section 6 in full when section 5 was built. Two
questions the note could not reach were put to the owner before any code and answered
in session on 2026-09-07: whether the loads reference axis survives the withholding
(it does — question (a)), and whether the condition register may look complete when it
is not (it may not — **OR-133a**). A third amendment, **OR-134a**, was forced by
implementation and is the substance of half this step.

**Deliverables.**
- `report/oracle_sections.py` — `_vtail_loads` and `_vtail_station_appendix`, which are
  two lines each: section 5's builder took the surface as a parameter, so the whole of
  section 6 and the 2026-09-07 review's five rulings arrived in it for free. Plus the
  OR-133 withholding (`_vtail_withheld`, `_non_conventional_statement`,
  `_NON_CONVENTIONAL_BODY`), the OR-133a note on the register and the summary, and
  `_inertia_basis` for OR-135's yaw-inertia provenance.
- `report/oracle_content.py` — `vtail_loads` joins `IMPLEMENTED`; Appendix E is built.
- `tail_geometry.py` — `tail_layout` and `is_conventional_tail`, the owners every
  consumer reads the arrangement through. `models/enums.py` — `TailType` stops calling
  itself "a layout sketch distinction only".
- `field_registry.py` — `geometry.parametric.tail_type` and
  `geometry.surfaces[].ref_axis_pct` marked `supplied`, each with its G5 measurement in
  the basis cell.
- `tests/test_oracle_report_vtail.py` — 22 gates, including the class drift guard.

**Key decisions.**
- **6.1's station table survives the withholding (owner, question (a)).** The loads
  reference axis is entered geometry resolved through a planform — the same numbers
  §2.1's three-view is drawn from — and withholding verifiable geometry to document a
  *load* limitation costs the reader something and documents nothing. The reason goes
  in the table's own note, so a station list above a withheld subsection cannot read as
  loads that merely failed to compute.
- **A short condition set says so, and names the case (OR-133a).** OR-133's scope was
  6.5 and Appendix E, but it names two unmodelled paths and only one is about the
  loads; the other is about the *condition list*, which 6.2 and 6.3 still print in full.
  A four-row table that looks complete reads as a measured completeness — OR-61's
  argument one deliverable over — and the summary is the table an analyst stops at.
  Named rather than counted, because OR-133's own distinction is that this is an
  omitted condition and not an understated one, and because a named case is one note
  51's D-51.1 can delete when it ships.
- **The withholding is stated ahead of the results test.** `build_tail_span` still
  returns the vertical tail's loads — they are what the balanced deck's lateral cases
  close ΣFy = 0 against, so withholding them in the calc would stop three fixtures
  assembling to document a limitation in them. The report must therefore never say
  "not produced" about loads that were, so the arrangement is checked first and the
  lead is **"Not supported"**.
- **G-OR-87 diffs against `CRUCIFORM`, not `T_TAIL`.** A T-tail is not only a report
  state: `is_t_tail` moves the horizontal tail onto the fin and adds the tip transfer,
  so a conventional-versus-T-tail diff of section 5 fails on real geometry and proves
  nothing about the withholding. `CRUCIFORM` is read by the report and by nothing else,
  so the diff changes exactly one thing and every difference it finds is attributable
  to it.

**The defect this step found (OR-134a).** OR-134 had required the `TailType` docstring
and a `CONVENTIONS.md` §7 row. That was not sufficient, and the insufficiency was
invisible until the feature was built against it: **the document is a function of
`reduce_to_oracle_inputs`** (OR-43), and `tail_type` sat outside the oracle input set,
so it was reset to `CONVENTIONAL` before the report ever read it. OR-133 fired on
nothing — `atr42_100` printed 40 rows of the loads the ruling withholds. Marking the
field `supplied` fixes it and needs no frozen-file edit, because the oracle form builds
from the registry.

Generalising on first find (rule 4) turned up the same defect one field over, and a
worse one: **`geometry.surfaces[].ref_axis_pct` was reset too.** All seven shipped
examples enter 40 % of chord; the document stated 25 %. `ga6_normal`'s horizontal-tail
root torsion printed **34.5 lb-in** where the analysis computes **60.8**,
`concept_regional_jet`'s **3645.3** against **4141.7**, and every applied-load `X` in
Appendices D and E sat **3–6 in** off the deck card the appendix says it is the same
load as. This had shipped with section 5 six days earlier, and it contradicted an
agreed ruling: **OR-51** says *"`ga6_normal` enters `ref_axis: 0.4`, so its wing
torsion is delivered about the LRA 40 % chord with the 25 %-chord oracle value beside
it — the report must not print one and call it the other."* The section 3 gate written
on 2026-09-01 had asserted `25% chord` and explained the defect in its own docstring as
though it were the ruling. Both fields are `supplied` now, the gate reads the axis from
the project, and the class has a **drift guard** rather than a prose rule: for every
shipped example and both surfaces, the beam the document states its loads about is the
beam the analysis ran.

This is the fourth instance this milestone of one defect class — *an entered value with
the right intent, shadowed by a derived stand-in, with nothing saying so* — after the
fin root waterline, the fin `symmetric` flag and the fuselage LRA. It is the first in
which the shadowing agent was the oracle projection rather than a resolution order, and
the first where a gate had been written that locked the defect in place. Filed and not
fixed: `weight.items[].consumable` is reset the same way, moving
`concept_regional_jet`'s horizontal-tail root `Fz` **−175.6 → −214.5 lb** — same class,
weight slice, on a fixture the report is not built for; the drift guard names it rather
than exempting it silently.

**The owner's review of the built section, and the typeset page (2026-09-07).** Two
findings came from reading the document rather than the code, and both are in this step.

*The vertical tail's loads reference axis was drawn along its root.* `WingStationLoad`
says its coordinates are airplane axes; for the wing and the horizontal tail they are,
which is why section 5 read them directly and was correct, and why the error was
invisible until a second surface used the same builder. On the fin `y` is the span
coordinate in the surface's own plane and `z` is the root waterline it is measured from,
so 6.1's figure drew a flat row of markers along the constant 111.5 root instead of
climbing to 167.1, and its station table called the height above the root a butt line.
The mapping already had an owner — `export.coordinates.tail_station_to_airplane`, which
is why the deck and Appendices D and E were right — and 6.1 now goes through it. This is
the same shape as OR-134a one layer down: a value whose meaning is decided elsewhere,
with the type it is stored in asserting the opposite. The docstring that asserted it has
been corrected.

*A table printed one column on top of another.* The width solver documents a floor — a
column is never narrower than its longest unbreakable token — and its last fallback
scaled every column straight past it. Table 25's `14 CFR` column needed 63pt for
`23.423(a)(1)` and was given 26, so the regulation overprinted the CG case as
`23.423(a)(1)G4`: not a tight table but a corrupt one, in which case identity could not
be read. The floor is absolute now, and a table that cannot be set upright is **turned**
(owner, 2026-09-07) rather than shrunk a third time — another size step buys about 12 %
and fails on the next wide table, while turning the page buys 53 % and never puts 8pt
type in a signed document. Fixing it exposed two more: every landscape appendix was
being sized against the portrait width, and `fancyhdr` had been warning once per page,
77 times, that the running head did not fit. Building `ga6_normal` went from 33 overfull
boxes and 77 `fancyhdr` warnings, worst 23.3pt, to **4 overfull boxes, worst 0.79pt**.

**Filed, not fixed.** The fin's root is raked — `ga6_normal`'s vertical tail meets the
body with its leading edge at waterline 117.0 and its trailing edge at 111.5 — and the
planform resolver rebases both onto a single root at 111.5. The bottom two load stations
then sit at X 284.9 and 268.9 against 262.9 immediately above them, so the axis kinks aft
at the root. Visible in Figure 24 now that the axis is drawn in the right plane at all.

**Test.** `tests/test_oracle_report_vtail.py` — G-OR-80 (five subsections, mirrored),
G-OR-83 (SELECT's own unscaled totals; every Appendix A condition present under the
oracle's name), G-OR-86 (a rudder load on all four conditions, both fixtures), G-OR-87
(the withholding over every `TailType`, the shipped T-tails, the `CRUCIFORM` diff, and
the companion gate that the calc still produces the loads on all three T-tail
fixtures), G-OR-88 (the yaw inertia's provenance), OR-131 (neither section borrows the
other's requirements), OR-133a both ways, and the reduction drift guard, plus three
gates on the loads reference axis: the fin's stations climb a waterline and stay on the
centreline, the horizontal tail's still span a butt line and share one waterline, and
each figure draws its axis in the plane its surface is in. `tests/test_report_latex.py`
— no column narrower than its own floor and the widths still fitting the page, on every
table of both shipped reports; a table turned only when no upright size holds it, both
directions, with the one that is pinned; exactly one landscape environment per turned
table; both renderers declaring their head height; and the glyph tables held to eight
words TeX itself measured. The widths behind that floor are now measurements rather
than a four-class model, which is what closed the last four warnings: all three shipped
examples build clean. Suite **3629 passed**, ruff and mypy clean.

- **Section 2.2's weight/CG envelope figure (note 44 OR-45, note 45 WE-8, tier M, 2026-08-31)** —
  section 2.2 stated the mass properties and the CG cases in tables and drew nothing, while
  the analysis it documents has a figure in the manual: Appendix A p140 plots the useful-load
  envelope against the structural limits, and Ch 3 p21 tells the reader to plot both. It now
  carries that figure. Three decisions shaped it. The limits are drawn as one **closed**
  envelope rather than as the manual's three vertical rules, and are omitted entirely when a
  corner is unentered — a boundary with a side missing reads as permission, which is the one
  way this figure could actively mislead. Both loading edges are drawn, which is why design
  note 45 preceded this step at all: the port computed only the forward one, and on the GA6
  that is the edge which never approaches a limit while the aft edge passes 2.2 in beyond the
  aft-gross station, so the figure that was buildable before this work would have shown
  containment it had not demonstrated. And the figure has one builder shared with the summary
  report (OR-7) rather than an oracle-only copy, which means the summary report's own weight/CG
  figure gained the aft edge and the closed limit envelope in the same change — a tier-M
  behaviour change to a delivered capability, taken deliberately rather than as a side effect,
  because two documents drawing one airplane two ways is the defect the shared-owner rule
  exists to prevent. Two smaller things fell out. The vertices are tabulated from WTENV's own
  `ModuleResult` rather than swept in the report, which required `run_sections` to run a step's
  **folded** modules as well as its primary one — `weight_mass` names `WTESTIMA+WTONECG+WTENV`
  and its numbers legitimately come from all three — and the guard that says section 2 invents
  no number was widened the same way, through `workflow.step_modules` rather than by exemption.
  The table does **not** name the item added at each vertex: the analysis does not carry it
  (note 45 WE-3, amended), so the note under the table says so rather than the report inferring
  it from a sort it does not own.

## Step 154 — The oracle report states the wing loads (tier L, 2026-09-01)

**Objective.** Give the oracle technical report its first load-bearing section: the wing
loads, as four subsections and a lettered appendix, built from the `wing_loads` step
(`AIRLOADS+WINGINER+NETLOADS`) without the report computing anything of its own.

**Agreed first.** Design note 44 §11, decisions **OR-48 … OR-56** and gates
**G-OR-20 … G-OR-26**, settled with the owner in session before any code.

**Deliverables.**
- `report/oracle_sections.py` — 3.1 wing input data, 3.2 the run register and sign
  convention, 3.3 the root loads assessed, 3.4 the net distributions, and Appendix B's
  station table. A step that renders as subsections titles them and does not number them;
  `build_section` numbers them through `subsection_number`, the one numbering owner.
- `report/oracle_content.py` — the `Appendix` slot type, `APPENDICES` with the input echo
  **reserved** and the wing appendix built, `appendix_letter`/`appendix_heading`/
  `appendix_plan`, and `subsection_ref` so a "3.1" in prose is composed rather than typed
  (F-R2, one level down).
- `report/content.py` — `Series.closed`, and `Units.load_value`/`plain_value`.
- `report/planform_tex.py` — an open path is drawn open; `planform_wing_lra` registered.

**Key decisions.**
- **The 25 % chord is the LRA for oracle loads.** The suite accumulates torsion about the
  local quarter chord and transfers it to the surface's entered axis at the delivery
  boundary. The report is a function of the oracle projection (OR-43), and that projection
  resets the entered axis — so an oracle report cannot print a 40 %-chord torsion for a
  project that enters one, which is what `ga6_normal` does. Every torsion names its axis.
- **The three span-load curves call AIRLOADS once each.** `CL = 0`, `1.0` and the aero set's
  own `stall_cl`; the report never combines the additive and basic distributions itself.
- **The flaps-down span load cannot be produced at all** — AIRLOADS does not model the lift
  discontinuity a deflected flap puts in the basic distribution — so it is stated absent with
  its reason rather than filled with the clean set, and the capability gap is filed
  as **#163**.
- **There is no tail-on lift coefficient in this suite.** The balance carries the tail load
  as a separate force rather than inside the coefficient, so the tail-off curve is drawn with
  the balanced conditions marked on it and the section says that, rather than implying a
  second curve exists.
- **SELECT's subset is the critical set.** No second criticality rule is invented for the
  report; 3.2, 3.3, 3.4 and Appendix B are four projections of one set, in one order.
- **The register says where its case list came from (OR-57, owner's review 2026-09-03).**
  Two paths reach a wing case set — the selection's search, and a list entered on the project,
  which wins when present — and the first draft of 3.2 claimed the first while `ga6_normal`
  runs the second: three entered cases against the six the selection names. The section now
  states which path produced the list, counts the V-n matrix by every dimension it enumerates
  (80 points over four CG cases, twenty conditions and one altitude), and tabulates every named
  condition against whether it was run, so PLAA, PMAA and NMAA are visible as named-not-run
  rather than absent without trace. The same review established that the fixture balances at
  sea level only while Appendix A names five of the six conditions at 12,000 ft — filed as
  **#164**, since adding the altitude renumbers every V-n case.
- **The register states the load-factor sign convention and whether the set envelops the wing
  (OR-58, same review).** `Nz` in a wing case is the *inertia* load factor, the negative of
  the flight load factor, so a +3.8 g manoeuvre prints as −3.8 — and every load factor in the
  table is negative whichever kind of condition it is, which is how the review came to read a
  set of positive-g cases as negative ones. 3.2 now states the convention, and states from the
  analysed set whether it holds a negative-load-factor case. On `ga6_normal` it does not, and
  the section says the distributions therefore do not envelop the wing — the analysis half of
  that, adding the selection's NMAA beside the entered oracle cases, is filed as **#165**.

**Test.** Thirteen new gates in `tests/test_oracle_report.py`, including: every load column
in the section and the appendix carries `-ULT`; each root value equals the module's own LIMIT
result times that case's stated factor; the span-load series equal `schrenk_distribution`'s
own output at each target `CL`; the reference axis is emitted as an open path while the
outlines close; the four projections state one set of cases; and a project with no wing loads
states the absence in both the section and its appendix and still builds a complete document.
Three existing structural tests were restated rather than relaxed: a rendered section is now a
plan row, a builder's own subsection, or an appendix, so plan and document are paired **by
number** instead of by position.
- **Appendix B became a structures deck, and the concentrated wing masses turned out to be
  missing from it (OR-59 … OR-63, second review round, 2026-09-03).** The owner's ruling —
  *the aim of the Appendix B table is to give the sectional loads to apply to a structures
  model* — settled three questions and exposed a fourth. The table is now two: **B.1** the
  applied loads, each with the point it acts at, and **B.2** the loads carried. The applied
  moment is the **free** moment, not a difference of the cumulative column: `Myy` accumulates
  a section moment and two position transfers of the outboard shear, and at `ga6_normal`
  PHAA's outboard strip the free moment and the column difference are +5,917 and −5,313
  lb·in — opposite in sign, so applying the difference double-counts the transfer. `Mxx`,
  `Mzz` and `Fy` get no applied column for the same reason: a strip applies forces and a
  section moment and nothing else, and the wing has no producer for a spanwise strip load.
  3.2 gains the notation table and the recurrences that connect the two halves.

  Writing the closure check — the applied set, summed tip inboard, must reproduce the
  published cumulative loads — turned up the fourth. It closed to machine precision on
  `ga6_normal` and failed on `baron_58` by 4,821.5 lb of a 5,004.1 lb root shear: `WINGINER`
  steps the cumulative shear at each concentrated wing mass and leaves the per-strip loads
  panel-only, so the mass was published nowhere as an applied load. `ga6_normal` enters none,
  which is why nothing had caught it. **Admitted under OR-15** by the owner in session and filed as **#166**, since
  an appendix whose stated purpose is to be applied to a model cannot be written truthfully
  around losing most of the inertia relief: `wing_inertia` now publishes each mass as a
  `ConcentratedLoad`, and `airloads`/`wing_inertia`/`net_loads` populate the long-empty
  `WingStationLoad.myy_free` — the recovery from the cumulative column that would otherwise
  have served is exact for an air load and wrong the moment a point mass steps the shear.
  Every change is additive, no cumulative value moves, and the frozen manifest is updated in
  the same commit per G-OR-9.

**Test (second round).** The closure identity is the gate: `test_net_loads.py` re-accumulates
`Fz`, `Fx` and `myy_free` — with each point mass entering through the arms its own coordinates
state — and compares against the published `Sz`, `Sx`, `Mxx` and `Myy` at every station of
every case on **both** example airplanes, with a companion assertion that the strip set alone
is visibly short on the Baron, so the guard cannot pass vacuously. Beside it: the published
free moment agrees with `balance._free_moments` on the air loads where both are valid; the
axis transfer moves the free moment on the strip's own force and leaves a point load
untouched; point loads survive the I/O round trip. In the report, eight more gates cover the
two-table split, the point every applied load acts at, a row per concentrated mass carrying
zero free moment, the symbol table's coverage of every column heading, the printed
recurrences, and the page break and landscape environment.

- **Self-containment split into an image rule and a data rule (`SUMMARY_REPORT.md`
  §2, tier M, 2026-08-30)** — The standard read "the `.tex` SHALL NOT reference
  external image files", and the oracle technical report (design note 44, OR-23)
  needed its LaTeX to read the CSVs shipped in the issue package so the document
  draws the delivered data instead of restating it — the only way two renderings of
  the same numbers cannot drift. The clause was first *read* as already permitting
  it, a CSV being no image; that reading was rejected as a rule meaning something
  its words do not say, and the standard was amended instead. The image prohibition
  is unchanged and absolute, and §2 now states the properties it exists to protect
  (deterministic, diffable, unit-testable as text, vector in the document's own
  fonts, no non-TeX toolchain) — none of which a plain-text data file costs. The
  new *Data reference* clause is scoped to **delivery mode, not to the document**:
  a packaged report may read in-package data given manifest membership, a relative
  in-root path, §3.1 self-description and whole-package determinism; a standalone
  `.tex` may reference nothing. That scoping is what keeps the Export page's own
  `.tex` download from becoming a file that fails to compile, and it is held by a
  new guard rather than by the sentence
  (`test_report_latex.py::test_the_standalone_tex_references_no_external_file`,
  which rejects `\input`, `\includegraphics`, `\pgfplotstableread` and the
  `\addplot table {file}` form alike). The amendment formalises what §1.5, §4.7 and
  §5 already required — that the report travel with companion data files and point
  the reader at them — by making the reference mechanical instead of editorial, so
  the document can no longer misquote its own companion. Note 44 OR-26, which had
  carried the reading, is now a citation of the rule.

- **A deleted row is the row the button names (#153, tier M, 2026-08-30)** — the
  oracle form's per-row delete removed the last row instead of the named one, silently
  and with no undo, on the Geometry page the 0.8.2 report review is conducted from. The
  filed root cause was wrong: it blamed `_delete_row`'s `on_click` args binding a list
  detached by the next run, so that `del rows[index]` never reached the project.
  Instrumented, the callback receives the project's own attached list and the deletion
  lands every time; the *render* undid it, because a row widget keys itself by row index
  and Streamlit's retained state outvotes the model-seeded `value=`, renumbering every
  row below the deletion onto its neighbour's state. This is `app_shell.widget_keys`'
  generation argument at table scope — a renumbered row is a different widget and
  re-seeding cannot fix it — and it is now stated in `GUI_design.md` beside the row-counter
  rule it belongs with. Fixed as a class rather than in the shape that showed it: the flat
  grid's `st.data_editor` holds index-keyed pending edits and the cached frame of a
  polyline in a renumbered row draws the row that used to be there, so both are retired
  too, and both delete tests now snapshot whole rows rather than names — the shift moved
  values between rows, which is how the flat shape's test passed against a defect it
  shared. The defect was unreachable while every fixture carried two surfaces (deleting
  row 2 of 2 removes the last row either way) and this milestone made it reachable by
  giving `ga6_normal` seven. `oracle_app/form.py` is hash-frozen for 0.8.2 by design note
  44 OR-13; the owner lifted OR-14 and admitted the fix under OR-15 in session on
  2026-08-30, on the reasoning that the milestone created the exposure, and the manifest
  hash is updated in the same commit.

## Step 165 — The ground delivers every case (design note 44 §22, tier L, 2026-09-07)

**Objective.** Section 12, Landing Gear Loads — the oracle report's last derived
analysis section. With it the body is complete: every `oracle_steps()` step with
a `bas` that produces results has a built section, and `IMPLEMENTED` stops being
a subset of `analysis_steps()`. It is also the first section since Section 2 that
all three shipped reports carry, which is why the iteration needed no new
fixture.

**Agreed first.** Design note 44 §22 (**OR-183 … OR-193**, gates **G-OR-123 …
G-OR-130**), settled with the owner in session on 2026-09-07 before any code,
from three findings and eleven answered questions. The note carries **one OR-15
admission**, scoped to `modules/landing.py` and to two changes in it, re-pinned
in the frozen manifest with the scope recorded beside the hash.

**The finding that reshaped the section (OR-185).** Scoping the section against
the module showed the per-family "critical reaction" summaries were answering the
wrong question. `_critical` ranked each FAR family on `max(main-wheel resultant,
nose-wheel resultant)` and returned one case — which is not a tie-break between
two candidates for one title but a **comparison between two different gears**:
the winner sizes one of them and the loser's larger reaction on the other was
discarded. Measured: on all three shipped examples the two-wheel level landing
wins 23.479(a) on main-wheel load, so the **three-wheel level landing appeared in
no summary at all**, although its nose reaction is the largest of the family —
`1786.8` lb on `ga6_normal`, `4194.3` on `baron_58`, `8178.8` on
`concept_regional_jet` — and it is the condition Section 4's own advisory sends a
reader to Section 12 by name to find. A cross-reference is a promise the target
keeps; before this step the target did not contain it. Each family is now ranked
once per gear it loads, 40 conditions become 42, and **G-OR-129** asserts the
class rather than the instance.

**And the deeper one the owner ruled on (OR-184).** Presented with the fix, the
owner's answer went further: *"add all conditions, no critical case down-select
can be done without considering the airplane loads."* A ground case sizes a gear
member through a load path this analysis does not model — a drag brace, a side
brace, a trunnion — so ranking 33 conditions on any single scalar removes the
case a reader needs. Section 12 and Appendix F therefore carry **every** case,
the summaries are labelled a reading aid in the table's own note, and the CSV
header says so in capitals. What was scoped as a report section became a ruling
about what a loads analysis may hand a downstream discipline.

**A second defect, found building the engine file (OR-193).** Two of the six
engine-mount conditions — the 23.361(b)(1) sudden-stoppage torque and the 23.371(b)
gyroscopic condition — carry no `loc_*` values while the four beside them for the
same engine do, and `load_cases_to_rows` filled the gap with the **first**
location in the whole set. The right-hand engine's stoppage torque and its four
gyroscopic sub-cases were therefore published at the **left-hand** engine's butt
line: ten rows on `atr42_100` and `dhc8_dash8`, fifteen on
`concept_regional_jet`. Not a blank column — a real load at a point on the wrong
side of the airplane, which a blank would at least have invited a reader to ask
about. A condition with no location of its own now takes the point of the
condition it follows, verified against every shipped example and gated. The
producer stating the point on every condition it emits is the proper repair and
is filed: `modules/engine.py` is frozen.

**The 344 of 347 (OR-186).** The measurement that answered a question filed at
the end of §21. Every landing row reached the load-case index with no load — 40
of 40 — and sweeping the registry the figure is **344 of 347** rows on
`ga6_normal`, **543 of 555** on `baron_58`, **587 of 617** on
`concept_regional_jet`. Not a landing defect: `load_cases_to_rows`' own docstring
says its columns are *"the load components an engine mount must react"*, and a
landing case has three legs at three points and cannot be expressed in it at all.
The owner's ruling — *"a separate CSV file for each structural element … then
they can be specifically shaped for the loads presented in that csv"* — is the
general form of what four components already had, and the landing gear and the
engine mount now join them. The index itself is left unchanged and filed, because
reshaping it is a schema decision touching every producer.

**Deliverables.**
- `modules/landing.py` — the whole of the frozen file's part, under the grant:
  `landing_geometry` public so §12.1 can print the p230 oracle from the function
  the reactions were computed by, and `critical_reaction` with a gear argument.
- `export/sbeam_bridge.py` — `gear_applied_load_rows`, `engine_applied_load_rows`,
  two new `APPLIED_COMPONENTS` and two new `APPLIED_CSV_NAMES`, each with the
  in-file note its element needs.
- `report/render.py` — `point_load_records` as the single owner of the
  six-components-at-one-point extraction the index performed inline, with the
  ft-lb → lb-in conversion read off the value's own units; `_running_locations`
  carrying OR-193's fix; `_global_location` removed rather than left beside its
  replacement.
- `report/oracle_content.py` — `GEAR_LOAD_CASES` and Appendix F;
  `landing_loads` in `IMPLEMENTED`.
- `report/oracle_sections.py` — `_landing_loads` and its three subsections, six
  tables, `_attitude_figure` × 3 and `_gear_appendix`.
- `tests/test_oracle_report_landing.py` — new, 20 gates, the eight of §22.

**Test.** **G-OR-124** is the one that matters: the 23.479(a) nose row is a
three-wheel level landing and its main row is a two-wheel one, on every shipped
example, asserted against a **re-rank of the full matrix** rather than a stored
number. Beside it: all 33 cases in both the section and the appendix by case
number, so no down-select can creep back in; every appendix row's point compared
*through* `application_point_of` rather than against a literal; the three
figures' case lists asserted to partition 1-33 exactly and against `attitude_of`,
so a figure cannot come to claim geometry the reactions were not computed in; and
the fuselage advisory's forward reference swept across `_body_advisories`. Two
sibling tests that pinned the whole appendix list were rewritten to assert the
property they were about — that *their* step owns no appendix — since the list
form failed the day another section earned one and said nothing about theirs.

Lever arms verified against the manual's own figures: p235's braked roll prints
`AP 77.052 / BP 17.760 / DP 94.811 / CP 42.981` and §12.1 reproduces all four;
p234's level landing prints `K = .324`, `GAMMA = 17.978`, `BETA = 13.921` at a
ground angle of `4.057`, and so does the table. Suite green, ruff and mypy clean.
The Imperial baseline moved on exactly four channels — the landing CSV and text
report (two new summary conditions) and the case index and engine CSV (OR-193) —
and `csv/engine` moved only on the multi-engine examples, which is the location
defect confirming its own scope.

**Key decisions.** OR-184 is the one with reach beyond this section: it says that
where the loads analysis cannot see the load path, completeness beats ranking,
and it is the first time this project has stated that. OR-183 folds the free body
into the conditions subsection rather than giving it a fourth, because a reaction
and the point it is delivered at are one statement. OR-192 leaves a project with
no `landing` slice in the ABSENT state and **not** in §21's `NOT_APPLICABLE`: it
is missing an input, not exempt from a regulation, and the distinction is the
whole reason that state was created.

- **The h-tail sits at its own waterline (#236, 2026-09-08 review R12, tier M,
  2026-09-08)** — `LayoutInput.h_tail_z`, until now a three-view sketch offset,
  became a real analysis input: the new single owner
  `tail_geometry.h_tail_waterline` (the fin root's twin — fin tip on a T-tail,
  mid-fin on a defaulted cruciform, `root_waterline_z + h_tail_z` where entered,
  the wing-root plane marked ASSUMED with a loud note otherwise) places the
  h-tail's load stations through `tail_span`, so §5.1's station table,
  Appendix D and the exported GRIDs moved together from the GA-6's wing-root
  placeholder (WL 78.5, printed as an airplane coordinate — 32.5 in below the
  real surface for any reader importing the points) to the entered WL 111. Both
  report tables state the waterline's provenance from the same owner, the
  reviewed filed scope (a disclosure sentence) having been widened to this by
  the owner's option-B ruling with an OR-15 admission over
  `sloads/modules/tail_span.py`. No delivered load moved — the surface loads in
  fz only, so z places points, not forces. `ga6_normal` and `baron_58` enter
  their offsets; the blank fixtures print the ASSUMED disclosure. Guards: the
  owner's branches, a three-view-vs-load-path drift guard, and a two-direction
  report guard on the entered and blanked GA-6.

- **The sloads version got a single owner (`RELEASE_PROCESS.md`, tier M,
  2026-08-30)** — Found by reading a generated report: it stated sloads 0.8.0
  while `pyproject.toml` said 0.8.1, which is the basis of the branch that built
  it. Not a display bug. `tool_version()` asked `importlib.metadata`, which reads
  `PKG-INFO` — a snapshot written at install time. The 0.8.1 bump edited
  `pyproject.toml`, nobody re-ran `pip install -e .`, and every report since had
  been stamping the previous version into its analysis basis and its
  `build.json`. A provenance field that is wrong but plausible is worse than one
  that is absent, and this one appears on a page a reader trusts.

  Fixed structurally rather than by reinstalling (CLAUDE.md rule 3: one owner
  plus a drift guard, never a prose rule). `sloads/_version.py` holds the
  literal and imports nothing; `pyproject.toml` declares `dynamic = ["version"]`
  and points `[tool.setuptools.dynamic]` at the attribute; `tool_version()`
  reads the same attribute, so it tracks an edit with no install step. The
  version lives in its own module rather than in `sloads/__init__.py` because
  setuptools falls back to *importing* the module when it cannot read the
  attribute statically, and `__init__.py` pulls in the whole package, whose
  dependencies a build environment does not have.

  Four guards in `tests/test_version_owner.py`: packaging declares the version
  dynamic and names the owner, `[project]` carries no literal of its own, the
  report stamp does not import `importlib`, and the literal stays a plain
  module-level string setuptools can parse without importing anything. The third
  is scanned as an *import* via AST rather than as text — the function's own
  docstring explains why `importlib.metadata` is not used, and a substring
  search failed on the very comment documenting the fix.

## Step 156 — One vertical tail, one size, one place (#160, tier L, 2026-09-06)

**Objective.** Close #160 — *"the Baron's fin is entered symmetric and zero-based"* —
and the defect class behind it: the vertical tail's size and its placement were each
stated twice, in two places, with nothing checking the copies agree.

**Agreed first.** With the owner in session on 2026-09-06, in four steps, after the
investigation quantified each half. `CLAUDE.md` rule 1's chat route (working alone);
the numbers that justified each step are in the deliverables below and pinned in CI.

**Deliverables.**
- `tail_geometry.fin_root_waterline` — the entered `vtail` polyline becomes the first
  branch of the resolution order, ahead of the explicit scalar, and a disagreeing pair
  is resolved to the polyline with `FinRoot.note` naming the value not used.
  `tail_geometry.entered_fin_root` is the one reader of the polyline's datum.
- `examples/` — five fins re-entered as single surfaces on absolute waterlines;
  `ga6_normal`'s `vtail_root_waterline_z` pin cleared.
- `tests/test_tail_geometry.py` — `test_no_fixture_places_its_fin_twice` and
  `test_no_fixture_doubles_its_fin`, the two drift guards; `_FIN_ROOT` re-pinned.
- `CONVENTIONS.md` §7 (SSOT row + two §7.2 rules), `theory_sources.md` (the lateral
  balance's measured lever-arm sensitivity).

**Key decisions.**
- **The entered polyline leads the explicit scalar.** Every other branch reconstructs
  the fin's placement from something else — a scalar typed on another page, the T-tail
  relation, the body's top at the fin station. The polyline states it. The two are
  therefore **not** note 36 OV-1's blank-derives / typed-overrides pair but two
  spellings of one measurement, which is why precedence alone is not the whole answer
  and the disagreement is stated as well as resolved.
- **Stated in band, not refused.** `validate_tail_planform` raises on the same
  duplication class one level down (area against span), and the difference is
  deliberate: that conflict has no rule to pick between its two representations, this
  one does. Raising here would also make `vtail_root_waterline_z` un-typable on any
  project with an entered fin, which is a shipped input field — a guard that breaks an
  input field is the wrong guard.
- **`ga6_normal`'s 78.5 was scaffolding, not a measurement.** Note 19 §10.2 step (i)
  entered it on 2026-08-17 as "a zero-movement change that pins today's assumed value
  as a stated one", so that step (ii)'s body outline would land with an attributable
  digest wave. Step (ii) shipped in the same pass and was shadowed by step (i) from the
  moment it landed, because `explicit` led the order. Three answers for one waterline
  — 78.5 pinned, 98.44 from the outline entered to supersede it, 111.5 from the fin's
  own edges — and the one that won was the one nobody measured, reported
  `assumed=False`. **The lesson is the ordering, not the number:** scaffolding entered
  at the top of a resolution order is indistinguishable from data.
- **The roll arm is where it lands, and the load is the control.** `z_fin − z_cg` goes
  11.89 → 44.89 in on ga6 and the four lateral roll accelerations move 5–12×
  (`SUDDEN RUDDER` −6.888 → −85.952 deg/s²); yaw moves ~2 % through `Ixz`. `L_v` and
  `n_y` are **bit-identical on all five lateral fixtures**, 0.0000 % on every case,
  which is what makes this a lever arm moving rather than the aerodynamics. No
  Appendix A oracle moves: the lateral cases have never had a printed one and are
  pinned by measurement in both directions.
- **`SurfaceInput.symmetric` is load-bearing on a fin, in two places.**
  `wing_geometry.surface_properties` reads it for the area/span/AR bookkeeping, and
  `airloads.resolve_aero_surfaces` reads it as the predicate for *"is this a lifting
  surface AIRLOADS analyses"*. The five mis-flagged fins were therefore reported at
  twice their own area and span **and** shipped a Schrenk symmetric spanwise lift
  distribution for a vertical tail, on the doubled aspect ratio, under `FAR 23.301`.
  The second consequence was not in #160 as filed and was found by asking why
  `csv/airloads` moved in the digest wave — the drift check earning its keep.
- **The guards check effects, not flags.** `test_no_fixture_doubles_its_fin` asserts
  WINGGEOM's reported fin area and span against the entered `vtail_area_sqft` /
  `vtail_span_in` and asserts the fin is absent from `resolve_aero_surfaces`, rather
  than asserting `symmetric is False`. It is then the same gate the day the same wrong
  number is reached by another route.
- **One convention for a fin polyline's second coordinate:** a waterline in the
  airplane datum, which is how `ga6_normal` always entered its own. The five that were
  root-relative are rebased onto their own resolved roots, rounded to the 0.1 in an
  entered waterline is measured to (≤ 0.05 in of lever arm, ~0.1 % of `ṗ` on three
  fixtures, nothing on the RJ).

**Test.** Five new or re-aimed gates plus the pinned baselines. The two drift guards
run per fixture; `_FIN_ROOT` re-pins every fin as `basis="geometry"`, `assumed=False`;
the three derivation-branch tests now strip the polyline first, since a fixture that
has one no longer reaches a derivation branch at all — which is the ordering working.
`test_the_vertical_tail_is_drawn_in_its_own_frame_and_never_mirrored` sets the
`symmetric` flag itself instead of borrowing `baron_58`'s (a guard whose premise is a
bug elsewhere dies when the bug is fixed) and checks the plotted waterlines against the
fin's own root rather than against zero — `y >= 0` is true of a fin lying on the datum,
which was the defect. The frozen Imperial baseline moves on six channel families, each
mapped to the edit that caused it before it was regenerated: `airloads` and
`wing_geometry` on the five flag fixes, `balance` on the roll arm, `tail_span` /
`vtail_span_cards` / `lra_model` / `balanced_deck` on the fin waterlines, and
`htail_span_cards` on the two T-tails whose horizontal surface sits on the fin tip.
`concept_heavy`, which enters no `vtail` surface, does not move at all.

- **The applied wing load set becomes a deliverable (OR-64, tier M, 2026-09-03)**
  — Appendix B.1 was written as a report table, but the ruling that opened design
  note 44 §12 makes it a deliverable *format*: it exists to give the sectional
  loads to a structures model. A format only the report can produce is one the
  analyst retypes, so the row shape moved to the export channel
  (`sbeam_bridge.applied_load_rows`) with a CSV writer beside it
  (`wing_applied_loads.csv`), and B.1 became a consumer that converts and marks
  at the report's own boundary — the pattern §6 already uses for `mass_case_rows`
  and `balanced_case_rows`. The file is offered on the Wing Loads page and in the
  Export bundle. Two facts made this worth doing rather than exporting the
  existing span-load CSV: that file's applied moment `My` is the *increment of
  the cumulative* `Myy`, which on `ga6_normal` PHAA is opposite in sign to the
  free moment at the inboard strips and double-counts the sweep/dihedral transfer
  a geometric model regenerates for itself; and its concentrated masses are
  lumped onto the nearest node with a synthetic offset couple, so on `baron_58`
  PHAA an exported station force reads −2,612.9 lb-ULT where the strip load is
  +883.3. Both are properties of `wing_nodal_loads`, which the sbeam deck still
  uses and which this step deliberately did **not** change — reworking the deck
  means reworking its equilibrium gate, is tier L, and is filed rather than done
  inside a report milestone. The new set's own gate is stronger than the deck's:
  the free moments plus the applied forces' own arms reproduce the cumulative
  root `Myy` exactly on both example airplanes, `baron_58`'s four concentrated
  masses included, where the deck can only claim its `MOMENT` cards sum to the
  root torsion about nothing in particular.

## Step — Six components, and a deck built from them (design note 46, tier L, 2026-09-03)

**Objective.** Make the wing's applied load set usable as what it claims to be:
the deliverable a stress analyst builds a model from. Two defects stood between
it and that claim. It published three of the six components a body-axis load
needs — leaving the reader to decide whether a missing column was a zero or an
omission — and the sbeam deck written from the same wing results carried a
torsion that did not survive being applied at a point.

**Deliverables.** `AppliedLoad` carries `fx`/`fy`/`fz` and
`mxx_free`/`myy_free`/`mzz_free`, with the three structural zeros named at their
single point of construction (`_NO_SPANWISE_STRIP_LOAD`, `_NO_FREE_BENDING`)
rather than written `0.0` inline, so the day a lateral wing condition arrives
the search finds everything that assumed it away. `applied_body_moments` maps
the record's moments to right-handed CID-0 components through
`coordinates.bending_moment_vector`, and both views of B.1 — the report table
and `applied_load_csv` — go through it, so neither carries sign logic.
`wing_nodal_loads` is rebuilt from the applied set: each strip's own load at its
own node, each concentrated mass reduced to the node inboard of it as a force
plus the full three-component `r × F` couple. `_moment_defect` and its relative
tolerance are deleted — the defect they recovered from the cumulative column is
now read from the mass's own coordinates. `sob_internal_loads` and
`sob_collapsed_load` transfer torsion to a shared `sob_reference_point` (the LRA
interpolated at the cut), which a free-moment card set makes load-bearing where
a differenced one did not. Both wing CSVs state their moment conventions in-band.
`equilibrium.py`'s wing claim strengthens from `m0.y` to `m.y`, and its
tolerance scale stops understating the budget of a cancelling cross product.

**Test.** `test_the_applied_set_reproduces_the_whole_vmt_at_every_station`
(G-OR-35) — the applied set's six-component resultant against `Sx`, `Sz`,
`Mxx`, `Myy` and `−Mzz` at **every** station of every case of `ga6_normal` and
`baron_58`, the latter with four concentrated wing masses; worst residual
2.5e-15 relative. `test_the_applied_set_states_all_six_components` (G-OR-36)
pins the zeros as published values and fails if a real component is dropped into
one. `test_wing_deck_resultants` and
`test_wing_deck_reproduces_the_station_table_at_every_node` (G-OR-37) assert the
rigid-body `m.y` from the deck's own text, in both unit systems, on every
example. `test_the_appendix_table_and_the_exported_csv_are_one_load_set`
(G-OR-38) compares all six columns row for row.
`test_each_wing_csv_states_the_moment_convention_it_uses` (OR-69).

**Key decisions.** *The zeros are printed, not omitted, and that reverses an
earlier rule.* The standard had said `Fy` must not be a column lest a zero read
as a measured zero; a partial vector traded one misreading for a worse one, and
the fix is to print the zero **with its reason** in the table's own note.
*Differencing was not a shortcut, it was the only thing available before
`myy_free` and `point_loads` were published* — which is why the deck kept it
after those fields arrived, and why the error survived a full closure sweep:
shear and both bending columns close under differencing, and only torsion does
not. *Building from additive fields needs a guard, not a hope.* `myy_free` and
`point_loads` both default to empty on a `Project` written before they existed,
and a deck built from such a result would be short the whole free torsion and
look exactly like a complete one — so `wing_nodal_loads` checks the root closure
of its source and raises with the recompute instruction rather than exporting a
short deck. *The tolerance owner had a real defect of its own.* `equilibrium`'s
moment scale budgeted each cross-product component by `|t|`, after its two
products had cancelled; on a swept, dihedralled wing the torsion is a small
difference of two large products, and the understated budget called a 44 N·mm
text-rounding residue a physics failure. It now budgets the products separately
and against the absolute coordinate the card format rounds. *Appendix B.2 is not
widened to match.* It states what the structure carries, in the beam's own
convention; putting `Mzz` beside B.1's body-axis `Mz` would place two
conventions in one appendix without a reader-visible reason (OR-70, filed).
*No frozen file was touched:* the whole change lives in `sloads/export/` and
`sloads/report/`, the FAR23 core is untouched, and B.2's numbers are the same
numbers they were.

- **WINGGEOM is not a strip integrator any more, and the prose says so (#155, tier M,
  2026-08-30)** — the closed-form planform integration approved the same day
  (`02_approved_corrections.md`) changed the method but not the twelve places that
  described it, one of which the oracle report prints verbatim in §2.1. This is
  CLAUDE.md rule 4 applied to a documentation defect: the false statement was swept
  across `sloads/`, `tests/` and the standard docs in one change rather than fixed at
  the single site #155 named, and the true uses of "strip" — AIRLOADS' own span loop
  over the load stations, `tail_geometry`'s spanwise integrator, and the historical
  references in the correction register — were deliberately left in place. Two
  substantive consequences came out of the sweep. The WINGGEOM surface table's
  `Integration elements` row became `Load stations`, because `elements` stopped being
  an integration parameter when the integral went closed-form and is now only the
  user's load-station count; and the Appendix A aileron oracle, loosened to ±2 %
  precisely because the strip result depended on an untabulated element count, was
  tightened back to the suite's ±0.1 % (it reaches 0.037 %). The Imperial baseline
  drifts in the `wing_geometry` and `configuration` channels only, and within those
  only in that row label and that note — no load number moves, which is the oracle
  lock holding. **Authority:** `wing_geometry.py`, `configuration.py` and
  `airloads.py` are hash-frozen for 0.8.2 by design note 44 OR-13; the owner admitted
  this change under **OR-15** in session, on the reasoning that OR-14 defers defects
  the report *exposes* while this one the milestone's own correction *created*. The
  manifest hashes are updated in the same commit. Supersedes the "#155 filed, not
  fixed" line in the preceding entry; #153 was admitted separately, on its own
  reasoning, in the entry that follows.

## Step — WTENV's aft edge: the half of the envelope we never ported (design note 45, tier L, 2026-08-31, issue #157)

**Objective.** Complete the WTENV port. `WTENV.BAS` (Appendix C p382–383) sorts
the discretionary items ascending by fuselage station, sweeps them cumulatively
from the minimum flight weight (line 330, *"NOW PRINTING FORWARD EDGE OF
ENVELOPE"*), re-sorts descending and calls the identical subroutine again (line
500, *"NOW PRINTING AFT EDGE OF ENVELOPE"*), printing `XBAR`, `ZBAR` and the
cumulative weight per vertex. The replication emitted the ascending sweep alone,
in `(weight, station)` pairs — so three of the original's outputs were missing:
the aft edge, the per-vertex waterline, and the name of the item added. Found by
reading frozen code while specifying §2.2 of the oracle technical report, where
the p140 figure is to be drawn.

**Deliverables.** `_forward_sequence` becomes `_sweep(start, items, *, aft)` —
one walk, two calls, mirroring the `.BAS`'s one subroutine and two `GOSUB`s — and
returns `EnvelopeVertex(weight, station, waterline)`. New public
`loading_envelope(project, aft=...)`; `loading_envelope_points` remains as its
station-only projection, so the Weight/CG Envelope page and the ballast calc are
untouched. `_weight_and_cg` adds the waterline the sweep needs while
`_weight_and_station` stays exactly as its three existing callers use it. A fifth
`ConditionResult`, *"Aft loading envelope (weight, station, waterline)"*, is
**appended** after the four that existed, its keys `aft_`-prefixed so the edges
stay distinguishable wherever conditions are flattened. WTENV's summary shape
(`report.render.weight_station_rows`) learns a third column: `_waterline` joins
the pair-folding suffixes, and routing moves from `LoadValue.quantity` to the key,
because a waterline and a station are both lengths with the same empty dimension
hint. The frozen-set manifest is re-hashed with its authority named beside it.

**Test.** `test_both_edges_reproduce_appendix_a_p139` — both printed blocks, all
16 rows, all three printed columns, ±0.1 %; worst disagreement 0.01 in on a
waterline, the page's own last digit. It runs on a **test-local transcription of
the Appendix A p138 data base, not `ga6_normal`**. Four further gates:
`test_the_two_edges_close_the_envelope` (both sweeps share their first and last
vertex, which is what makes them one envelope);
`test_the_aft_edge_adds_a_condition_and_changes_no_existing_one` (G-WE-2, the
additive claim);`test_the_forward_edge_has_exactly_one_owner` across four
fixtures; `test_an_edge_is_invariant_to_the_entry_order_of_equal_station_items`.
Every pre-existing test in `test_weight_envelope.py` passes **unedited**, which is
where the numeric invariance actually lives.

**Key decisions.** *The fixture is not the manual's fixture, and that is
load-bearing.* The manual runs WTENV twice on two different data bases:
Chapter 3's, with no baggage row and a maximum loading of 3322 @ 84.56, and
Appendix A's, which adds `BAGGAGE 120 @ 180` and reaches 3442 @ 87.89.
`ga6_normal` is the Chapter 3 one, and the standing ballast oracle (78 / 418 /
158 lb) is computed *from* its no-baggage maximum — so "completing" the fixture to
match Appendix A, the obvious move, would have broken an existing lock to gain a
new one. The only printed edge tables are p139's, on the other data base, hence a
transcription in the test rather than a shipped example. *The manual's printed tie
order is not an oracle.* Simulating its own sort on its own data base reproduces
the forward edge's labels exactly and fails on the aft edge: lines 220/420 compare
strictly, so equal elements swap, and the sort runs over the whole dimensioned
array whose blank records migrate through it — the printed order is a function of
the user's answer to *"maximum number of weight items"*, not of the airplane. It
cannot move a number, because tied items share a station. Ties are therefore
broken stably and the gate asserts invariance to their entry order. *The item name
was dropped, not deferred by choice.* `LoadValue`'s value is a float and its
`label` is cosmetic with M4-9 forbidding downstream matching on it;
`ConditionResult.title` is per-group; `CaseRef` is the delivered-load-case identity
with a fixed component taxonomy. Emitting a per-row string needs a
`models/results.py` contract change, which is its own note — so the note's WE-3 was
amended mid-implementation and the vertex→item mapping is left recoverable by the
reader instead of restated. *And the freeze was honoured by proof rather than by
distance:* this is milestone 0.8.2's first OR-15 row 1 admission, and what makes it
safe is not that the diff is small but that the four pre-existing `ConditionResult`s
are asserted unchanged and every prior oracle passes unedited.

## Release cut: **sloads 0.8.1** (the defects the 0.8.0 cut shipped, and the gates that let them ship), tag `v0.8.1`, 2026-08-29

**Objective.** Close band **B1** — the patch band the owner opened 2026-08-28
against defects found in *released* 0.8.0 output — and cut when it is empty.
The band was extended twice in flight by owner ruling, both on 2026-08-29: with
the three documentation items the independent review of `dev/v0.8.1` raised
(#140–#142, folded in rather than opening a 0.8.2 band), and with the two
process gates the post-0.8.0 escape assessment filed the same day (#145/#146).
Band B1 emptied 2026-08-29.

**Deliverables** (the `[0.8.1]` changelog section is the release note):
- **The LANDLOAD correction train** (notes 38/39, tier L): `BETA`'s sign on the
  ground-roll and tail-down attitudes, corrected at the origin on the evidence
  of Appendix A's own braked-roll construction figure (#133, with the
  datum-frame lift term and moment transform swept as the same sign class —
  both entered in the approved-corrections register); the ground reaction
  applied where the manual applies it — axle on the landing attitudes, ground
  contact on the ground-roll families, the manual's own printed column — ending
  up to 524,302 lb-in of invented pitching moment (#139); and the half of the
  printout the replication never shipped (#134): every case now emits three
  wheels with airplane-datum `Fx/Fy/Fz`, the application point `x/y/z`, the
  fuselage-axis angle, the datum load factors NR/NV/ND and the unbalanced
  moments, frame and point named **on the value** (`LoadValue.frame`/`.point`,
  schema **v57 → v59** in two recorded identity hops, #141).
- **The oracle is whole again:** p231–p233 re-rendered legible at 200 dpi and
  every printed LANDLOAD cell locked (72 more cells, all 33 cases); the ga6
  light-landing fixture weight restored to the manual's **2800 lb**, un-hiding
  the light-loading WR defect its back-solved 2803 lb had been absorbing — an
  input derived from an output cannot also test it.
- **The GUI defect pair from the GA6 V-n diagnosis:** an Optional record block
  is created and removed by a named gesture — a stray touch no longer attaches
  a phantom zero-coefficient set that saves with the file (#143); a lift
  polynomial with no alpha lever is refused as a named `MissingInputError`
  instead of iterated 400 trips into a `SolverFailure` (#144). Beside them: a
  `null` in a project file refused by name, one failing module no longer takes
  a whole results page down, a blank LIMNZ no longer resolves to zero through a
  half-entered planform, and the last-ulp formatting hang (#147).
- **The escape assessment's process gates,** closed in-band: the CI **GUI
  journey** — every bundled example walked through every `workflow.py` step
  with the project asserted byte-identical, now named in `RELEASE_PROCESS`
  §3.5 beside the boot smoke and a manual walkthrough line (#145); and **oracle
  provenance / gate independence** — every oracle cell states where its number
  came from, a back-solved input is disqualified, and no gate may re-derive the
  rule it checks (#146).
- **Breaking:** Python **3.10 is the floor** (#132) — 0.8.0's `>= 3.9` claim
  was refused at install by Streamlit 1.51's own metadata; the classifier set,
  CI matrix and floor are now one guarded claim.
- **Version** `0.8.0` → **`0.8.1`** (owner re-cut ruling 2026-08-28: a patch
  band for released-defect correction; the schema hops are additive/identity
  with old saves migrating, so the load-case CSV widens by two stated columns
  without breaking shape).
- **Changelog cut** — `scripts/build_changelog.py 0.8.1 --date 2026-08-29`:
  **20 fragments** consumed into `## [0.8.1]` across Breaking / Added /
  Changed / Fixed, **14 history entries** rolled to the top of this file, a
  fresh empty `[Unreleased]` opened; released sections byte-untouched.
- **History roll** (`RELEASE_PROCESS.md` §4.3): notes **38** (ground frame) and
  **39** (application point) carry *SHIPPED* headers and move to `40_history/`
  (42/43); notes 32/34 stay with their open GUI milestones. The live file
  passed the **1,500-line threshold**, so everything below the 0.8.0 cut block
  froze verbatim into
  [`41_completed_development_to_0.8.0.md`](41_completed_development_to_0.8.0.md)
  (the 0.7.2 and 0.7.1 release cuts).
- **Verification baseline:** the corrected LANDLOAD figures are pinned by the
  full Appendix A p230–p233 page locks in `tests/test_landing.py` — the printed
  pages are the baseline of record, cell for cell, which is stronger than a
  recorded-output archive; the two deliberate departures from the manual's
  *program* (the `BETA` sign class) are in
  [`../20_theory/02_approved_corrections.md`](../20_theory/02_approved_corrections.md).
- **Gates at cut:** `pytest` **3177 passed / 32 skipped / 1 xfailed / 0
  failed**, `ruff` clean, `mypy` clean (`sloads/`), `scripts/smoke_test.sh`
  **PASS** (both front-ends boot, CLI CSV checked),
  `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on 7 tracked keys,
  no open CRITICAL/MAJOR review findings.

**Key decisions.** *The assessment ran before the cut, and its findings became
band rows, not prose.* The post-0.8.0 escape assessment traced every escape to
a gate that measured the wrong thing — a boot check where use was the risk, a
binary oracle rule where provenance was the risk — and both fixes shipped
inside the same milestone as the defects they answer (#145/#146), per rule 3:
structural gates, never prose rules. The owner's re-cut rulings held the line
against milestone sprawl twice: the documentation band folded into B1 rather
than becoming 0.8.2, and the milestone list stayed 0.8.1 → 0.9.0 → 1.0.0.
The `BETA` sign was corrected **at the origin** on the manual's own
construction figures rather than patched downstream, and #139's lesson — the
gate that should have caught it was making the correction itself — is now the
named gate-independence rule. **Band B1 retired with the cut; band B2 (0.9.0 —
main-GUI development, anchored by #29) is the milestone in flight.**

- **The word travels with the value: frame and application point stated in-band
  in the delivered CSV (tier M, schema v59, 2026-08-29)** — the 2026-08-29
  independent review of `dev/v0.8.1` raised that the corrected landing output
  #133/#134/#139 shipped is not self-describing: the CSV names neither the frame
  its numbers are in nor the point each force acts at. Both facts already existed
  on the calc side — `LoadValue.frame` since schema v58 (note 38 GF-6/GF-7), the
  point in `landing.case_note()` and both GUI captions — and this one channel
  dropped them, because `results_to_rows` reads neither the note nor the frame
  for output. The point therefore reached a consumer as coordinates alone, and
  the axle and the ground contact point are a rolling radius apart, so guessing
  wrong is a moment arm rather than a caption. Two channels were on the table
  (the issue left it open): the project-scoped methods preamble, which prints on
  every module's CSV and could not name a *per-case* point when cases 1–33 split
  between the two, and per-row columns. The columns won, and the point took the
  same posture the frame already had rather than a second one: `LoadValue.point`,
  a vocabulary (`gear_loads.POINTS`) and not free text, stamped per leg from
  `application_point_of` — the single owner design note 39 AP-1 already
  established — and read once, at the render boundary, into an `Applied at`
  column beside a new `Frame` column. Deriving it there instead, by parsing the
  note or re-deriving from the case number, was rejected: it re-establishes
  exactly the label/note string-matching M4-9 removed, where a reworded sentence
  silently blanks a column. The reference-node rows deliberately name no point —
  the node is where the reaction is transferred *to*, and stamping it would say
  one force is applied in two places at once. No load moved: five landing CSV
  digests changed, every other frozen Imperial channel is byte-identical, and the
  Appendix A oracles and twin closures are untouched. Guards:
  `test_the_delivered_csv_states_its_frame_and_its_application_point` (every
  delivered force row on every fixture names both),
  `test_the_csv_point_is_appendix_as_printed_column_case_by_case` (the column is
  the manual's, so a constant word would read correct on half the matrix),
  `test_the_reference_node_names_no_application_point`,
  `test_every_landing_value_names_a_known_point_or_none` and
  `test_a_module_that_names_neither_gets_neither_column` — the last pinning that
  #141 states the landing output and does not widen every CSV. **The schema hops
  v58 → v59**, an identity (`_hop_58`; `""` means exactly what v58 meant) for the
  reason v58 itself hopped: `LoadValue` is persisted inside
  `critical.conditions[].loads`, so a display-neutral addition is still a shape
  change. It stays tier M under the 2026-08-29 re-cut's second ruling — no load,
  no quantity, no physics and no theory citation to make — with the hop named
  here so the schema move is on the record rather than inferred from a diff
  (issue #141).

- **The set that carries no airplane (#144, tier M, 2026-08-29)** — Found
  diagnosing a GA6 V-n failure that named nothing: a coefficient set had reached
  the balance with every lift coefficient zero, and the only evidence the user
  got was "did not converge in 400 iterations … reached NZ=0 at alpha=41.3861
  deg". The refusal is stated where the value is consumed, for every writer,
  because more than one can produce it (#143 is the writer this one came from,
  and it is fixed separately) — the same ruling the #81 stall-CL, weightless-CG
  and tail-CP-at-datum guards on that function already carry.
  The line is drawn at *no alpha lever*, `C1..C4` all zero, rather than at the
  identically-zero polynomial the report showed. A constant-CL set (`C0`
  non-zero, no slope) hangs the inner loop the same way and for the same reason:
  NZ cannot move, so the iteration has nothing to iterate. That is unsolvable,
  not merely implausible, which is what separates it from the neighbouring
  `aero_lift_slope_sign` warning — a negative or over-large slope still
  balances, and stays a `ConsistencyWarning` rather than becoming a run failure.
  The other two polynomials are ruled on explicitly in the guard's docstring and
  executed in the test: an all-zero drag or moment polynomial must still run,
  because `CD = 0` and `CM = 0` are values a set may honestly carry, while an
  all-zero lift polynomial is a statement that there is no airplane to balance.
  The test drives both entry points that share `balance_configs`, and builds its
  phantom set the way the GUI does — blank coefficients with `stall_cl` filled
  from `clmax_flap` — asserting that fill first, so the case cannot quietly stop
  proving anything by starting to trip the #81 guard instead.

- **The printer that amplified the noise the package had already been taught to
  suppress (#147, tier M, 2026-08-29)** — Found running down a red fast gate on
  a **docs-only** commit: `test_imperial_output_matches_the_frozen_baseline`
  failed on the Linux 3.12 leg naming `concept_regional_jet`'s landing channels,
  and passed on macOS. `CONVENTIONS.md` §7 already carried the rule this
  violates — a byte in a deck or report must not depend on the libm build, FMA
  or the interpreter's `sum()` — with three owners: `picks.extreme` for keyed
  picks, `sbeam_bridge._fmt3` for card-component dust, and `math.fsum` at every
  summation. The human-channel formatter was never one of them, and it was the
  one place where an ulp of difference was not damped but *amplified*: its two
  branches are `str(int(value))` and `f"{value:.4g}"`, and the test between them
  was exact equality with the integer.
  The evidence that settled it needed no second platform. The shipped output
  already disagreed with itself: case 12 of `concept_regional_jet` prints the
  unbalanced yawing moment as `-687258` on the datum row and `-6.873e+05` on the
  body-frame row — the same load, one ulp apart, two precisions — and case 18
  prints the main drag reaction as `12768` on one row and `1.277e+04` on
  another. A sweep found 95 ulp-unstable cells in that one example's landing
  output alone. Landing is where it surfaced because landing is the trig-heavy
  path the #133/#134/#139 rotations built, and `sin`/`cos` are exactly where two
  libm builds part company.
  The fix is one line of quantization rather than a widened branch, because the
  quantity being made stable is *what the reader sees*: rounding to twelve
  significant figures first makes both branches read the same number, and the
  residual knife edge — a value within an ulp of a twelfth-digit boundary — is
  one no deliverable distinguishes. The guard is stated on real values, not
  invented ones (`test_no_printed_deliverable_cell_hangs_on_the_last_ulp` walks
  every value of every condition of the failing example's landing module under
  ±4 ulp, with a non-vacuity floor), and the row in §7 gains the formatter as an
  owner so the next printer added has somewhere to be listed. `tests/
  test_platform_stability.py`'s docstring had recorded the precedent a week
  earlier: 3.12's compensated `sum()` moved values "where a value sat on a print
  boundary" and the digest failed on the 3.12 leg only. That fix removed a
  source of noise; this one removes the amplifier, which is why the class is
  closed at the printer and not at the next quantity to land on an integer.

- **A back-solved input, an unusable oracle page, and the loop that closed between them (tier M, 2026-08-29)** —
  Step C10 recorded that Appendix A's wheel-load table was OCR-garbled and that
  the GA6 light-landing weight "was back-solved from the legible side-load cell
  (½·1.33·W = 1864)". Two consequences followed from that one move and neither
  was visible from inside the codebase: the fixture carried **2803 lb** where
  every other statement of the same quantity said 2800 (WTENV's
  forward-regardless weight, the `CG3` flight point at the identical station and
  waterline, and `cg_cases.seed_landing_cases`, which takes this case's weight
  straight from the envelope anchor), and the braked-roll family was left with
  **no printed-value oracle at all** — an input derived from an output cannot
  also test it. The family ran on internal identities, which is what let #135's
  `WR` defect sit undetected in shipped ULTIMATE loads.
  Reading the rendered p231 broke the circle: the cell prints **1862**, not
  1864, and `1862/0.665 = 2800.0` exactly. The fixture is corrected to 2800,
  which closes the +0.107 % residual #135 deliberately left rather than absorbed
  into a widened tolerance, and the ground `fwd light` case becomes identical to
  the flight `CG3` point it was always the same corner of. Cases 15, 18, 23, 24
  and 31–33 move 0.107 %; no other fixture is affected. The page then yields
  what it had been assumed not to: `test_landload_braked_roll_printed_cells`
  locks cases 16/17 and 18 on p231 and case 18's airplane-datum pair on p232 at
  ±0.1 %, the 23.493 family's first printed-value oracle, and the cells are
  recorded in `theory_sources.md` as **transcriptions from the rendered page,
  not OCR extractions**, since that distinction is exactly what failed here.
  Two structural consequences beyond the number. The drift that hid for a year
  was that `seed_landing_cases` is only ever *offered* to the GUI and never
  checked against what a project carries, so
  `test_a_seeded_fwd_light_case_weighs_what_the_seed_gives_it` now makes the
  seed a checked invariant on every fixture, exempting a case that states its
  own D-25 loading (`baron_58`'s fwd light closes at 4,440 lb against a 4,200 lb
  anchor — a different quantity, correctly not a drift). And the p232 pair gives design note 38's
  open GF-1 question its first transcribed deviated-from cells (Fz 1733 /
  Fx 1638), which the blocking GF-3″ register entry needs. It was first read, the
  same day, as *refuting* GF-1 — the shipped `PHIM = atan(0.8) + GRA2` gives
  1733.0 / 1637.9 where GF-1's `atan(0.8) − GRA2` gives 1978.4 / 1331.2 — and
  that reading was withdrawn within the day (note 38 §1.12): `LANDLOAD.BAS`
  computes the pair *from* the printed angle on the same line
  (`VM(L)=RMP(L)*COS(PHIM(L)/57.3)`), so the two cells are one measurement and
  cannot adjudicate the sign of the rotation that produced them. A printed
  number overrules an argument only when it is independent of it.

- **Where the load acts: the printed column the OCR lost, and a gate that was
  correcting the code instead of testing it (tier L, 2026-08-29)** —

  **Objective.** Give the landing deliverable a point of application that is the
  manual's, opening issue #134 (design note 38 GF-6, "a load and its point are
  one statement"). The first check made before emitting anything was whether the
  point about to be emitted was the point the deck already transferred from. It
  was not, on twelve of the 33 cases, and the item stopped there: a defect with
  first-order effect on shipped content outranks the fidelity item that exposes
  it (`CLAUDE.md` rule 6), so #139 was filed, design note 39 written and agreed,
  and #134 re-ordered behind it — the same sequence #133 forced a day earlier,
  for the same reason.

  **What was wrong.** `gear_loads` transferred every case from the tyre contact
  patch. Appendix A applies cases 1–12 at the **axle** ("CENTER OF EACH WHEEL")
  and 13–24 at the **ground contact point**, with 25/26, 28/29, 31/32 at "CL
  AXLE" and 27, 30, 33 at "GROUND" — a column in the p231/p232/p233 headers that
  had been unreadable in the scan since 2026-08-15 and was recovered at 200 dpi
  on 2026-08-29. The consequence is a spurious `r × F` pitching moment on every
  balanced landing case, absorbed into the solved `q̈` and shipped in the deck's
  `MOMENT` cards. The split is not editorial: level-landing drag is a **spin-up**
  load, whose reaction reaches the leg through the bearing at the axle, while
  braking torque is internal to the wheel/leg free body and leaves the patch
  force where it acts.

  **The evidence, and why it counts.** LANDLOAD prints its own unbalanced
  pitching moment `PITCHP`; the assembled case reports a pre-closure residual;
  the two are the same quantity up to G-7a's distributed lift, which the manual
  nets at the CG. Nothing in `residual My − G-7a lift == PITCHP` is derived from
  the application point, so it adjudicates it — and it reproduces the printed
  column on all six fixtures with gear, closing to ≤62 lb-in at the column's
  point against 20,964–665,862 lb-in at the other one, splitting exactly at the
  column's own family boundary. On ga6's LG-01/02/03 `PITCHP` is exactly zero, so
  the entire patch residual was invented; at the axle what remains is the lift
  moment the suite knowingly adds, to 0.1 / −1.8 / −0.5 lb-in.

  **Deliverables.** `application_point` / `application_point_of` (`AXLE` /
  `GROUND_CONTACT`) own the point; `GearLegLoad.point` and `AppliedWheel.point`
  carry it beside `patch`, which stays reported because a gear analysis starts
  there (AP-3); `transfer_couple` takes it. No reaction changes — the forces are
  LANDLOAD's own — so every Appendix A oracle and printed-cell lock passes
  unmodified, which is itself the acceptance criterion G-AP-5 states. `LG-04`'s
  pre-closure `My` moves −179,232 → −158,271 lb-in, `q̈` −1.925e-2 → −1.701e-2;
  the frozen Imperial digest, `balanced_cases.md` §9.5, `CONVENTIONS.md` §1/§7,
  `PROGRAM_SPEC.md` and `theory_sources.md` move with them. The sbeam roundtrip
  stayed green, as note 39's OQ-A2 predicted and did not assume.

  **Test.** **G-AP-1** — the identity on every balanced ground case of every
  bundled fixture at `1e-4 · n·W·MAC` (worst measured 2.65e-5, baron_58 LG-17).
  **G-AP-2** — the point against a case-by-case *transcription* of the printed
  column, never against the rule the code applies, since two copies of one rule
  cannot disagree. **G-AP-3** — a structural guard that the package builds an
  application point in exactly one place. The two existing negative controls were
  re-anchored to `point`: one of them, the static-axle control, had read `patch`
  and would have silently lost the ability to fire.

  **Key decisions.** AP-1 the printed column, as physics and not as a label; AP-2
  one owner for the point; AP-3 the patch stays reported; AP-4 no reaction moves,
  which keeps the whole oracle surface outside the change; AP-5 ship the gate
  that found it rather than a widened tolerance; AP-6 tier L, ahead of #134.

  **The lesson, which is about a test and not about the code.** The rotational
  gate had been moving the applied load from the tyre to the axle *inside the
  test* since 2026-08-15, on exactly cases 1–12, with a comment recording that
  getting it wrong "is not subtle: the level family misses by 12 % (21,000 lb-in
  on ga6_normal case 4)". The number was right, measured, and written down; it
  was read as bookkeeping between two conventions rather than as a defect,
  because the point the code used had no independent statement to be wrong
  against until the column was recovered. A gate that corrects the code before
  comparing is not testing the code — it is agreeing with it. The correction now
  lives at the origin and the gate makes none of its own, which also let the
  braked-roll pitch line drop the 5 % slack it had carried for #133: **every
  family closes on one bound.** Design note 38 §1.7 had audited this chain
  end-to-end and passed it, checking that the transfer was consistent — which is
  precisely what a wrong point preserves. Its verdict is overturned in place.

  **A duplicate removed on the way through** (rule 4): `transfer_couple` was
  implemented twice, identically, in `gear_loads` and in `export/coordinates`,
  each docstring claiming to be note 24 R-11's single owner. Consolidated onto
  the calc layer, since the export side can import it and not the reverse, with
  the name re-exported so no export call site moved.

- **The gate that proved boot, and the walk that proved use (#145, tier M,
  2026-08-29)** — The GUI release gate started both front-ends and checked the
  root page answered 200. Every automated test above it rendered **one** page,
  with a **fresh** session, on a **fresh** project, and almost always on
  `ga6_normal`. Between those two shapes sat the defect class that had produced
  both post-0.8.0 escapes: load an example, touch something, find the damage two
  pages later. `tests/test_gui_journey.py` closes it by walking every bundled
  example through every `workflow.py` step in order — one session carried
  forward, widget state included, since the stale-widget class `widget_keys`
  exists for lives in exactly that carry-over — pressing every Apply over
  untouched widgets and then running every registered module. Its assertion is
  that the project comes out byte-identical, because nothing was entered.
  It failed on its first run, and what it found was the reason to have written
  it. #143's ruling — an `Optional` record is created and removed by a named
  gesture, never attached by a touch — had been implemented in the oracle GUI
  through its field registry, and the main GUI, whose pages are hand-written, had
  never received it. Pressing Apply on a page nobody had filled in attached a
  zero-valued slice; on the sparser examples the walk collected eight of them,
  and two were load-bearing: a zero-area `flap_loads` and a zero-cylinder engine
  make their modules raise, so **Results Review and Export were both dead on
  three of the seven shipped examples** — reachable by opening a bundled project
  and clicking Apply. `app_shell/optional_slice.py` is the single owner of the
  app-side rule, which is narrower than the oracle GUI's add/remove pair because
  here the Apply *is* the named gesture: it may fill a slice in and may empty one
  out, but it may not create one out of nothing. "Entered nothing" is read off
  the dataclass defaults rather than a per-page field list, with a `seed=` form
  for the forms whose widget defaults are not the dataclass's, and the walk is
  the drift guard — a new page that writes an `Optional` slice directly fails the
  day it is written.
  The sweep (practice 4) found the same shape inverted three more times: a
  wholesale rebuild that enumerates the fields its own form renders **deletes**
  every field it does not. The Aero Apply destroyed a populated `lateral_body_aero`
  block and re-derived `cruise.stall_cl` from CLmax — the exact failure the
  neighbouring fuselage-moment form carries a paragraph of comment about guarding
  against, worth +30 % on the atr42_100 stall clamp; the Payload Cases Apply
  deleted the `LoadingDefinition` off three of baron_58's six CG cases, which is
  what produces their mass model; the engine form wrote unset `Optional` power
  fields back as stated zeros, #121's class from the writing side.
  The crash had a second cause, and the first attempt at it was wrong. Two modules
  raise a plain `ValueError` for a slice that exists with nothing in it, and the
  obvious move — refuse by name so "run every module" skips them — was made and
  then reverted: `test_cli.py::test_an_invalid_control_surface_input_fails_rather_than_vanishing`
  is m2 ruling that a zero aileron area is an *invalid* input and must fail the
  run, not an absent one to be skipped, precisely so a deck cannot come out one
  case short in silence. The ruling stands and the fix moved to the consumer:
  `run_all_modules_reporting` hands the failures back beside the results, and the
  two pages name the module instead of dying with it. The lesson is the cheaper
  one to have learned from a red test than from a review — a page crashing is not
  evidence that the exception is wrong, only that its reader is.
  The residue is ten writes the walk still sees, kept in the file's `KNOWN_OPEN`
  list with a backlog row and — the part that matters — a test asserting each one
  still reproduces, so an entry cannot outlive the defect it names. The lesson is
  narrower than "test the GUI": per-page coverage and a boot check are both real
  gates and neither can see a journey, and the cheapest thing that can is a walk
  that enters nothing and demands the project come back unchanged.

- **A load and a point and a named frame: the half of LANDLOAD's printout the
  replication had never shipped (tier L, 2026-08-29)** —

  **Objective.** Close design note 38's second deliverable (GF-6/GF-7, issue
  #134): make the landing output what a stress model can consume. LANDLOAD
  prints its whole 33-case matrix **twice** — once with respect to the ground
  line, once with respect to the airplane datum, each under its own banner — and
  `run()` shipped the first set only, with no application point, no attitude and
  no frame label, while the export deck consumed the other frame. A reader
  moving between the Oracle's table and the deck had no stated bridge, and the
  two differ by a rotation of the ground angle. The item waited on two ordering
  conditions and outlived both in the same session: the `BETA` sign (#133) and
  the application point (#139), each of which would otherwise have shipped a
  number this item then had to move.

  **What was missing.** Five things, all of them printed in 1990: the
  fuselage-axis angle per case (p231's own column); the airplane-datum table
  (p232 — `vm/dm/vn/dn` were computed and never reached `ModuleResult`); the
  NR/NV/ND datum load factors (not computed at all); the frame labels (the main
  GUI said "(ground line)" in prose, the Oracle said nothing); and the point of
  application, which lived only in the gear free-body report and the deck.

  **Deliverables.** New `sloads/frames.py` — the two frames, the manual's own
  caption words (`LANDLOAD.BAS` lines 5140/5230), the report-vs-deliver rule
  (`is_report_only`) and the rotation between the frames (`rotation_deg`,
  `to_airplane_datum`, `to_ground_line`, moved down from `gear_loads` so
  `landing` can reach them). `LoadValue` gains `frame` — **schema v57 → v58**
  with an identity hop, because `LoadValue` is persisted inside
  `critical.conditions[].loads`. `gear_loads` gains `DeliveredLeg` and
  `delivered_legs` / `delivered_gear_legs`: the three wheels of a case, in report
  order, built *from* `applied_wheels` rather than beside it, with the wheels it
  drops emitted at zero and their point and node still stated. `landing.run()`
  emits, per case: the three wheels' `Fx, Fy, Fz` and `x, y, z` and node, the
  fuselage-axis angle, NR/NV/ND, and p233's datum unbalanced moments — with the
  strut state and Appendix A's point-of-load column in the condition note. The
  critical-reaction summaries render through the same builder, so a family's
  summary cannot state its case differently from the matrix row it points at.
  Both GUIs gain the datum table and caption every reactions table from
  `frames.caption`. The main GUI's landing page and the Oracle's landing block
  both say which frame each row is in, in the manual's words.

  **Two more sign errors, and the reason they could not be typed.** The datum
  drag load factor's lift term is written `+LF*SIN(GRA)` in the `.BAS` and the
  datum moment transform rotates by `+GRA` — the third and fourth instances of
  the class #133 adjudicated, in the two quantities that entry could not reach
  because neither existed in sloads. Neither is written longhand here: the lift
  is `to_airplane_datum(LF, 0, ρ)` and the moments are
  `to_airplane_datum(YAWP, ROLLP, ρ)`, rotated through the case's own **measured**
  `ρ`. The corrected value is what a rotation gives; there is no second place a
  `+` could be typed for a `−`. Approved deviation registered under #134.

  **Test.** New `tests/test_landing_deliverable.py` (18 gates, G-GF-6/G-GF-7):
  three legs on every case of every bundled example and the *right* wheels
  unloaded per family; the point is the printed column and is the axle or the
  patch and nothing between, checked against the geometry rather than against
  `gear_loads`' own construction; the three legs **sum to p232's own force
  cells** and the datum factors are that sum through the printed loops — derived
  from the page, never from the module under test; case 1 and case 16 lock at the
  ruled numbers; the datum moments preserve their magnitude and leave pitch
  invariant; the CSV/text split guarded **both ways**; the frame split owned by
  one predicate; neither GUI writing the frame words itself. Plus 72 new
  Appendix A cells in `test_landing.py::test_landload_p232_airplane_datum_load_factors`.

  **Key decisions.** *(1)* The primed set leaves the CSV, so the datum moments
  had to be built — otherwise the deliverable would carry no moment at all. That
  answers design note 38 §5.4's one open disposition, in the item that needed it.
  *(2)* Three legs always, zeros included: which gears a family lifts is a fact
  about the case, and omitting them makes the reader reconstruct the rule from
  the case number. *(3)* The deliverable is built from the deck's own wheels, not
  beside them — #139 had just shown what two constructions of the same statement
  cost. *(4)* The LANDLOAD case families moved to `modules/landing.py`, which
  draws those lines already, and `attitude_of` with them; the 23.485 pairing that
  `NS` and the deck each derived separately became one `side_partner`.

  **What the numbers said back.** Three invariants the correction did not aim at:
  the tail-down family reproduces **all three** printed p232 cells exactly, because
  the `.BAS` already carries the corrected sign there — the manual is internally
  inconsistent, and one of its attitudes is right; `NV` does not move on cases
  1–12, because a cosine is even; and `NR` stays printed to the digit on the
  wheels-only families 16–24 (1.703, 1.330), because a rotation preserves a
  resultant. A correction that broke any of the three would have been the wrong
  correction.

- **The pages were never illegible (tier M, 2026-08-29)** — Step C10 recorded
  Appendix A's three LANDLOAD result pages as OCR-garbled, and the project took
  that as a property of the pages rather than of the extraction method. For a
  year the module's 24-main/33-nose matrix was validated by formula closure plus
  whichever cells happened to survive the text layer, with cases 13–33 resting
  on internal identities alone. Two defects lived in exactly that gap and were
  found the day before this one, both by reading a single rendered cell: the
  gross-weight ratio applied to LANDLOAD's light loading (#135) and a fixture
  weight back-solved from a mis-OCR'd number (#137), the second of which had
  quietly made an input a function of the output it was used to check.
  Rendered at 200 dpi the pages read cleanly, so all three were transcribed:
  p231 ground line, p232 airplane datum and p233 limit unbalanced moments, every
  cell of every one of the 33 cases, now locked at each page's own print
  resolution. The port reproduced all of it with no calc change — the coverage
  was missing, not the physics. Three things follow. The open sub-finding on
  design note 38 §1.11 is closed, and with it the property that a 40 % move in
  the supplementary-nose reactions could leave the suite green. Design note 38's
  blocking gate GF-3″ — a register entry stating its whole deviation surface in
  values transcribed from the page rather than computed from the pre-fix code —
  now has that set, in executable form, and it shows GF-1 and GF-2′ costing
  different things: GF-1 departs only from p232, while GF-2′ additionally departs
  from p231 and p233 rows that match the port exactly today, so the register must
  price them apart. And p233 turned out to print a **second** ground-to-datum
  rotation, `RMOM = RMOMP·cos GA + YMOMP·sin GA`, applied with the same sign on
  every attitude where PHIM/PHIN switch sign between them — a third instance of
  the note's own sweep class, after PHIM/PHIN and the datum ND lift term, and
  like that one it is not ported and can only arrive through the #134 reporting
  item. The standing lesson is narrower than "read the sources": an OCR failure
  and an illegible page are not the same finding, and the citations now record
  which of the two a cell came from.

