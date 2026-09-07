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
