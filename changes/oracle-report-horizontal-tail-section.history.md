## Step 157 — The oracle report states the horizontal tail's loads (tier L, 2026-09-06)

**Objective.** Give the oracle technical report its third load-bearing section: the
horizontal tail, as four subsections and a lettered appendix, built from the
`tail_loads` step (`TAILDIST`, Reference 1 Ch 10) without the report computing
anything of its own — and settle how a step that publishes two surfaces becomes two
sections.

**Agreed first.** Design note 44 §17 (**OR-128 … OR-138**), settled with the owner in
session on 2026-09-06 before any code, and corrected in place before implementation
when one of its premises turned out to be wrong (OR-129/OR-130a, below). Gates
**G-OR-80 … G-OR-88**.

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
the section renders four subsections numbered by the numbering owner and the tail
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
