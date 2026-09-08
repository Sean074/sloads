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
