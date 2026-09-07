"""The oracle report's section 5, Horizontal Tail and Elevator Loads (note 44 §17).

Assertions are made against the **content model**, never by matching LaTeX, for
the reason ``test_oracle_report.py`` states: the document must be checkable
independently of how it is typeset.

Gates covered:

* **G-OR-80** -- section 5 renders four subsections numbered by the numbering
  owner, and the tail appendices are D and E behind A, B and C.
* **G-OR-81** -- *(the OR-129 partition gate)* every condition the tail step
  publishes lands in exactly one section, and every tail section names the step
  and component it was built from. Asserted in both directions, so a dropped
  condition and a duplicated one each fail.
* **G-OR-82** -- every load section 5 and Appendix D print is LIMIT, states its
  condition's factor, and carries no ``-ULT`` marker; asserted both ways.
* **G-OR-83** -- the printed totals are the module's own unscaled values, and
  reproduce the Appendix A horizontal-tail oracles.
* **G-OR-84** -- the chordwise pressures reproduce printed p237; the chord
  stations print once and the aerodynamic constants are reference data.
* **G-OR-85** -- every condition states its aerodynamic state or the reason the
  method defines none, never a blank.
* **G-OR-86** -- *(OR-132)* every horizontal-tail condition states an elevator
  load, so the summary table has no blank in that column.
* **G-OR-88** -- *(OR-135)* the unsymmetrical row states its RH/LH split
  **adjacent** to its elevator load, and the checked pair states its pitch
  inertia.

Also here: OR-130a (the spanwise loads are appendix content, and Appendix D is a
view of the export owner, not a second assembler), OR-133's Section 5 pointer,
and OR-137's statement of the registered 23.427(a) deviation.
"""

import csv
import io as _io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io  # noqa: E402
from sloads.export.sbeam_bridge import tail_span_csv  # noqa: E402
from sloads.models.report import ReportSpec  # noqa: E402
from sloads.modules.select import default_critical  # noqa: E402
from sloads.modules.taildist import build_tail_chordwise  # noqa: E402
from sloads.report import oracle_content as oc  # noqa: E402
from sloads.report.render import format_value  # noqa: E402

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")
_TWIN = os.path.join(_EXAMPLES, "baron_58.project.json")

_SECTION = "htail_loads"


def _spec(**kw):
    return ReportSpec(**kw)


def _doc(path=_GA, **kw):
    return oc.build_oracle_document(io.load_project(path), _spec(), **kw)


def _section(doc, title_starts="5."):
    return next(s for s in doc.sections if s.title.startswith(title_starts))


def _appendix(doc, title):
    return next(s for s in doc.sections
                if s.title == oc.appendix_heading(title))


def _tables(section):
    """Every table in a section and its subsections, depth-first."""
    out = list(section.tables)
    for sub in section.subsections:
        out.extend(_tables(sub))
    return out


def _cells(table, column):
    i = next(i for i, c in enumerate(table.columns) if c.startswith(column))
    return [row[i] for row in table.rows]


def _prose(section):
    """All prose of a section and its subsections, joined."""
    text = " ".join(section.body) + " " + section.absent_reason
    for table in section.tables:
        text += " " + (table.note or "")
    for sub in section.subsections:
        text += " " + _prose(sub)
    return text


# --------------------------------------------------------------------------- #
# G-OR-80 -- shape, numbering and appendix lettering
# --------------------------------------------------------------------------- #
def test_the_tail_is_two_sections_and_five_renders_five_subsections():
    """OR-128: split by surface, because an analyst reads by surface.

    Numbered by :func:`oracle_content.subsection_number`, the one numbering
    owner, and never by a literal -- a number typed here would not move when a
    section is inserted above it.
    """
    doc = _doc()
    section = _section(doc, "5.")
    assert section.title == "5. Horizontal Tail and Elevator Loads"
    assert [s.title for s in section.subsections] == [
        oc.heading(oc.subsection_number("5", i), title) for i, title in enumerate(
            ["Horizontal tail input data", "Design conditions",
             "Critical horizontal tail loads", "Chordwise load distribution",
             "Spanwise loads"])]
    # The vertical tail is section 6 and is declared even before it is built,
    # which is what keeps the partition total (OR-129) and the numbering below
    # it honest from the first commit.
    assert _section(doc, "6.").title == "6. Vertical Tail and Rudder Loads"


def test_the_tail_appendices_are_d_and_e_behind_the_first_three():
    """The letter follows position (OR-50), and D is built while E is not."""
    assert oc.appendix_letter(oc.HTAIL_LOAD_STATIONS) == "D"
    assert oc.appendix_letter(oc.VTAIL_LOAD_STATIONS) == "E"
    doc = _doc()
    appendix = _appendix(doc, oc.HTAIL_LOAD_STATIONS)
    assert appendix.landscape and appendix.page_break
    assert appendix.tables and appendix.tables[0].rows
    reserved = _appendix(doc, oc.VTAIL_LOAD_STATIONS)
    assert reserved.absent_reason and not reserved.tables


def test_the_sections_below_the_tail_take_the_numbers_position_gives_them():
    """Splitting the tail moved every section below it, and that is free.

    ``section_number`` derives from position and no cross-reference is written
    as a literal (OR-2), so this asserts the property rather than the numbers:
    the analysis body is consecutively numbered with no gap and no repeat.
    """
    plan = [e for e in _doc().plan if e.number]
    numbers = [e.number for e in plan if "." not in e.number]
    assert numbers == [str(i + 1) for i in range(len(numbers))]


# --------------------------------------------------------------------------- #
# G-OR-81 -- the partition, both directions
# --------------------------------------------------------------------------- #
def test_every_tail_condition_lands_in_exactly_one_section():
    """OR-129's gate, and it is stronger than the counting rule it replaced.

    Every condition the tail step publishes must be printed by exactly one of
    the declared sections -- so a condition that lands in none, or in two, fails
    here. The horizontal half is asserted against the document; the vertical
    half against the declaration, because section 6 is not built yet and its
    conditions must still be accounted for.
    """
    project = io.load_project(_GA)
    published = [c for c in default_critical(project).conditions
                 if c.component in ("htail", "vtail")]
    assert published, "the fixture publishes no tail conditions to partition"

    components = [s.component for s in oc.SECTION_SPLITS]
    assert len(components) == len(set(components)), "two sections claim one surface"
    assert {c.component for c in published} <= set(components), (
        "a published tail condition belongs to no declared section")

    # ...and the horizontal section prints exactly its own share, no more.
    section = _section(_doc(), "5.")
    summary = next(t for t in _tables(section) if t.title.startswith("Critical"))
    printed = set(_cells(summary, "Case"))
    assert printed == {c.case_ref.case_id for c in published
                       if c.component == "htail"}
    assert not printed & {c.case_ref.case_id for c in published
                          if c.component == "vtail"}


def test_each_tail_section_names_the_step_and_component_it_is_built_from():
    """The backward half: a section that named no step would be unaccounted for."""
    for split in oc.SECTION_SPLITS:
        assert split.step_key in {s.key for s in oc.analysis_steps()}
        assert split.component and split.title.strip()
        assert oc.split_for(split.key) is split
    assert {s.key for s in oc.splits_for("tail_loads")} == {
        s.key for s in oc.SECTION_SPLITS}


# --------------------------------------------------------------------------- #
# G-OR-82 -- the basis, asserted in both directions
# --------------------------------------------------------------------------- #
def test_no_load_the_tail_section_prints_is_marked_ultimate():
    """Every load is LIMIT (note 49 OR-116), so no column carries ``-ULT``."""
    doc = _doc()
    for section in (_section(doc, "5."), _appendix(doc, oc.HTAIL_LOAD_STATIONS)):
        for table in _tables(section):
            assert not any("-ULT" in c for c in table.columns), table.title
            assert not any("-ULT" in cell for row in table.rows for cell in row)


def test_every_tail_load_table_states_the_factor_it_does_not_apply():
    """The other direction: a load table without an ``SF`` column states nothing.

    Exempted are the tables that hold no load -- the notation table, the chord
    stations, the aerodynamic constants and the aerodynamic state -- each of
    which would be making a claim it does not make by carrying a factor
    (CONVENTIONS section 3, OR-44).
    """
    doc = _doc()
    no_loads = {"Notation for the spanwise loads",
                "Chord stations of the pressure profile",
                "Aerodynamic constants of the surface",
                "Aerodynamic state of each condition"}
    # The register states a factor without stating a load, which is the one
    # table that carries an ``SF`` column and no load column (OR-132's ruling
    # that the factor is stated wherever the case is named).
    geometry = {"Loads reference axis by station"}
    for section in (_section(doc, "5."), _appendix(doc, oc.HTAIL_LOAD_STATIONS)):
        for table in _tables(section):
            if table.title in no_loads or any(
                    table.title.startswith(t) for t in geometry):
                assert "SF" not in table.columns, table.title
                continue
            assert "SF" in table.columns, table.title
            assert all(cell for cell in _cells(table, "SF")), table.title


# --------------------------------------------------------------------------- #
# G-OR-83 -- the printed value is the module's own
# --------------------------------------------------------------------------- #
def test_the_printed_totals_are_the_modules_own_unscaled_values():
    """The boundary states the factor and applies nothing (note 49 OR-116).

    Matched through the content model against the analysis's own numbers, not
    against a literal: a gate that re-derived the value would be checking its
    own arithmetic.
    """
    project = io.load_project(_GA)
    conditions = [c for c in default_critical(project).conditions
                  if c.component == "htail"]
    summary = next(t for t in _tables(_section(_doc(), "5."))
                   if t.title.startswith("Critical"))
    printed = dict(zip(_cells(summary, "Case"), _cells(summary, "Total load")))
    for condition in conditions:
        total = next(v for v in condition.loads if v.key == "total_tail_load")
        assert printed[condition.case_ref.case_id] == format_value(total.value), \
            condition.case_ref.case_id


def test_every_appendix_a_condition_is_present_and_named_as_the_oracle_names_it():
    """G-OR-83's identity half, and a limitation of the fixture stated outright.

    **The shipped ``ga6_normal`` does not reproduce the Appendix A tail figures,
    and cannot.** The oracle values (balancing +519.85 / -613.92, unchecked
    -1397.8 / +1227.2, checked -671.5 / +787.8, gust +908.6 / -1292.8,
    unsymmetrical -1204.7) are selected from a **three-altitude** envelope --
    ``test_select.py::_ga6_three_altitudes`` -- while every case the shipped
    example delivers is at sea level, so the search governs on different points
    and lands 0.3-3 % away. That is backlog **#164** (*"every delivered case
    states 0 ft where Appendix A names its critical wing conditions at 12,000
    ft"*), an open item this section did not create and must not paper over.

    So the oracle comparison stays where the right fixture is --
    ``test_select.py::test_critical_htail_balancing_match_appendix_a`` and its
    siblings, page-cited and toleranced there -- and this gate asserts what the
    *document* is responsible for: that every condition the oracle names is
    present, under the name the oracle uses. Pinning the document to the printed
    numbers would mean pinning it to a fixture defect.
    """
    register = next(t for t in _tables(_section(_doc(), "5."))
                    if t.title == "Design conditions analysed")
    assert set(_cells(register, "Condition")) == {
        "BAL UP RETRACTED", "BAL DN RETRACTED",
        "UNCHECKED MAN DN", "UNCHECKED MAN UP",
        "CHECKED MAN DN", "CHECKED MAN UP",
        "GUST UP RETRACTED", "GUST DN RETRACTED", "UNSYMMETRICAL"}
    # ...and each states the requirement it answers, from the analysis's own
    # ``far_reference`` rather than from a literal typed here.
    project = io.load_project(_GA)
    register = next(t for t in _tables(_section(_doc(), "5."))
                    if t.title == "Design conditions analysed")
    want = {c.case_ref.case_id: (c.label, c.far_reference)
            for c in default_critical(project).conditions if c.component == "htail"}
    printed = {r[0]: (r[1], r[2]) for r in register.rows}
    assert printed == want


# --------------------------------------------------------------------------- #
# G-OR-84 -- the chordwise distribution
# --------------------------------------------------------------------------- #
def test_the_printed_pressures_are_taildists_own():
    """G-OR-84 -- the printed profile is the module's, matched value for value.

    The Appendix A comparison (p237: ``LT25 +907.62 / LT50 -387.77`` giving
    ``0.682 / 0.095 / 0 / 0.015 / -0.030``) lives in
    ``test_taildist.py``, against the fixture that selects the printed
    condition; the shipped example selects a different governing point, for the
    reason the balancing gate above states. What the *document* owes is that it
    prints what TAILDIST produced and rounds nothing into a different number.
    """
    project = io.load_project(_GA)
    results = {r.case_ref.case_id: r for r in build_tail_chordwise(project)
               if r.component == "htail"}
    table = next(t for t in _tables(_section(_doc(), "5."))
                 if t.title.startswith("Net chordwise pressure"))
    for row in table.rows:
        result = results[row[0]]
        for i, station in enumerate(result.stations):
            assert row[3 + i] == format_value(station.psi), (row[0], i)


def test_the_chord_stations_print_once_and_the_constants_are_reference_data():
    """The stations are geometry, identical in every condition (OR-131's cousin).

    Repeating them per case would invite a reader to look for a difference that
    cannot exist. The aerodynamic constants carry no factor because nothing is
    sized to a lift-curve slope.
    """
    tables = _tables(_section(_doc(), "5."))
    stations = next(t for t in tables
                    if t.title == "Chord stations of the pressure profile")
    assert len(stations.rows) == 5
    assert [r[0] for r in stations.rows] == [f"X{i}" for i in range(1, 6)]
    constants = next(t for t in tables
                     if t.title == "Aerodynamic constants of the surface")
    assert constants.rows and "SF" not in constants.columns
    assert "no safety factor" in (constants.note or "")


def test_the_chordwise_figure_plots_every_condition_once():
    section = _section(_doc(), "5.")
    figure = next(f for sub in section.subsections for f in sub.figures
                  if f.key == "chordwise_htail")
    assert figure.data is not None and not figure.absent_reason
    labels = [s.name for s in figure.data.series]
    htail = [r for r in build_tail_chordwise(io.load_project(_GA))
             if r.component == "htail"]
    assert len(labels) == len(set(labels)) == len(htail)
    assert set(labels) == {r.case for r in htail}


# --------------------------------------------------------------------------- #
# G-OR-85 / G-OR-86 / G-OR-88 -- what every row states
# --------------------------------------------------------------------------- #
def test_every_condition_states_its_elevator_load():
    """G-OR-86, and it is the reason for the OR-132 admission over ``select.py``.

    Before it, the elevator load was published on two of nine conditions, so
    this column would have been blank on seven rows for no reason the analysis
    could give -- the load is a pure function of the split every one of them
    already carries.
    """
    for path in (_GA, _TWIN):
        summary = next(t for t in _tables(_section(_doc(path), "5."))
                       if t.title.startswith("Critical"))
        cells = _cells(summary, "Elevator load")
        assert cells and all(c and c != "--" for c in cells), path


def test_the_unsymmetrical_row_states_its_split_beside_its_elevator_load():
    """G-OR-88 / OR-135: adjacency is the whole of the ruling.

    A gate that only checked both values appeared *somewhere* would pass the
    arrangement the owner rejected -- the split in one table and the elevator
    load in another. Alone, an elevator load on an unsymmetrical case reads as
    one surface's load, when the case's whole content is that the sides differ.
    """
    summary = next(t for t in _tables(_section(_doc(), "5."))
                   if t.title.startswith("Critical"))
    row = next(r for r in summary.rows if r[0] == "HT-09")
    sides = row[summary.columns.index("Sides RH / LH")]
    elevator = row[next(i for i, c in enumerate(summary.columns)
                        if c.startswith("Elevator load"))]
    assert "/" in sides and sides != "--", sides
    assert elevator and elevator != "--"
    # Every other condition is symmetric and states no split, rather than
    # repeating its own total in two columns.
    others = [r[summary.columns.index("Sides RH / LH")]
              for r in summary.rows if r[0] != "HT-09"]
    assert all(cell == "--" for cell in others)


def test_every_condition_states_its_aero_state_or_the_reason_there_is_none():
    """G-OR-85 -- note 35's AS-3 carried into the document.

    A blank cell is a quantity the method does not define, and the table says
    which ones and why, rather than leaving the reader to guess whether a zero
    was measured.
    """
    table = next(t for t in _tables(_section(_doc(), "5."))
                 if t.title == "Aerodynamic state of each condition")
    assert len(table.rows) == 9
    # The trim angle of attack is published by every horizontal-tail condition.
    assert all(cell not in ("", "--") for cell in _cells(table, "Surface angle"))
    # The checked pair defines no elevator deflection -- the increment is a
    # pitching-acceleration inertia term -- and the note says exactly that.
    checked = [r for r in table.rows if r[0] in ("HT-05", "HT-06")]
    assert checked and all(
        r[table.columns.index(next(c for c in table.columns
                                   if c.startswith("Elevator deflection")))] == "--"
        for r in checked)
    assert "pitching-acceleration inertia term" in (table.note or "")


def test_the_checked_pair_states_the_pitch_inertia_it_was_computed_with():
    """G-OR-88 -- OR-135's third quantity: provenance beside the number."""
    table = next(t for t in _tables(_section(_doc(), "5."))
                 if t.title == "Aerodynamic state of each condition")
    inertia = dict(zip(_cells(table, "Case"), _cells(table, "Inertia")))
    assert math.isclose(float(inertia["HT-05"]), 2242.8, rel_tol=2e-3)
    assert inertia["HT-01"] == "--"


# --------------------------------------------------------------------------- #
# OR-130a -- the spanwise loads are appendix content, and D is a view
# --------------------------------------------------------------------------- #
def test_appendix_d_and_the_tail_span_csv_are_one_load_set():
    """OR-64's ruling one surface over: a view of the export owner, not a
    second assembler. Compared as numbers over the columns both carry, because
    the two round for different readers; the identity that matters is the load.
    """
    from sloads.modules.tail_span import build_tail_span
    project = io.load_project(_GA)
    results = build_tail_span(project)["htail"]
    rows = list(csv.DictReader(_io.StringIO(tail_span_csv(results, "htail"))))
    table = _appendix(_doc(), oc.HTAIL_LOAD_STATIONS).tables[0]
    assert len(table.rows) == len(rows)
    gid = table.columns.index("GID")
    ids = {r.case: r.case_ref.case_id for r in results}
    for row, want in zip(table.rows, rows):
        assert row[0] == ids[want["Case"]] and row[gid] == want["GID"]
        # The applied normal force is the identity that matters: the deck and
        # the appendix are the same load set, printed for two readers.
        i = next(i for i, c in enumerate(table.columns) if c.startswith("Fz"))
        assert math.isclose(float(row[i].replace(",", "")), float(want["Fn (lb)"]),
                            rel_tol=1e-3, abs_tol=1.0), (row[i], want["Fn (lb)"])
    # ...and the carried set is deliberately absent (owner, 2026-09-07).
    assert not any(c.startswith(("Sn", "Mxx", "Myy")) for c in table.columns)


def test_the_spanwise_notation_defines_every_symbol_a_column_uses():
    """Section 3.2's rule (OR-62) applied to the empennage: a column heading
    names a symbol from the notation table and nothing else."""
    doc = _doc()
    notation = next(t for t in _tables(_section(doc, "5."))
                    if t.title == "Notation for the spanwise loads")
    defined = {r[0] for r in notation.rows}
    assert defined == {"Fn", "Sn", "Mxx", "Myy"}
    assert {r[3] for r in notation.rows} == {"applied", "cumulative"}
    root = next(t for t in _tables(_section(doc, "5."))
                if t.title.endswith("at the root (LIMIT)"))
    for column in root.columns:
        symbol = column.replace("Root ", "").split(" ")[0]
        if symbol in ("Case", "Applied", "SF"):
            continue
        assert symbol in defined, column


def test_the_spanwise_subsection_states_it_has_no_printed_oracle():
    """The absence is content (OR-5): the reference gives the tail's totals and
    its chordwise profile and stops, so this deliverable is held to stated
    closures instead, and says so where it is delivered."""
    span = _section(_doc(), "5.").subsections[4]
    assert "no counterpart in the original analysis" in " ".join(span.body)
    assert "closure" in " ".join(span.body)


# --------------------------------------------------------------------------- #
# OR-133 / OR-137 -- what section 5 states about what it is not
# --------------------------------------------------------------------------- #
def test_section_five_points_at_the_non_conventional_tail_limitation():
    """OR-133: stated in full where the loads are withheld, pointed at from here.

    Section 5's own loads are unaffected by the limitation, so it gets the
    pointer and not the statement -- but it gets the pointer, because a reader
    who starts at the horizontal tail must not meet the restriction for the
    first time two sections later.
    """
    prose = _prose(_section(_doc(), "5."))
    assert "conventional tail" in prose
    assert "does not affect anything in this section" in prose


def test_the_23_427_deviation_is_stated_where_the_case_is_introduced():
    """OR-137 -- OR-112's treatment one section over: an analyst comparing
    against the printed example finds the difference explained rather than
    discovering it."""
    prose = _prose(_section(_doc(), "5.").subsections[1])
    assert "23.427(a)" in prose
    assert "registered deviation" in prose and "methods statement" in prose


# --------------------------------------------------------------------------- #
# G-OR-7 -- absence is content
# --------------------------------------------------------------------------- #
def test_a_project_with_no_tail_states_its_absence_and_still_builds():
    """A half-filled project yields a complete document, never a traceback."""
    project = io.load_project(_GA)
    project.tail_loads = None
    doc = oc.build_oracle_document(project, _spec())
    section = _section(doc, "5.")
    assert section.absent_reason or all(
        sub.absent_reason for sub in section.subsections)
    appendix = _appendix(doc, oc.HTAIL_LOAD_STATIONS)
    assert appendix.absent_reason and not appendix.tables
    from sloads.report.oracle_latex import render_oracle_document
    assert render_oracle_document(doc)



# --------------------------------------------------------------------------- #
# 5.1 -- the surface the loads were run on (owner, 2026-09-07)
# --------------------------------------------------------------------------- #
def test_the_input_data_subsection_draws_the_surface_with_its_axis():
    """Section 3.1's shape, one surface over.

    Section 2.1 draws the same planform without the axis: that figure answers
    "what shape is it", this one answers "where are the loads". The axis is
    drawn through the very stations the distributed loads are stated at, so the
    figure cannot show an axis the analysis did not use.
    """
    from sloads.modules.tail_span import build_tail_span

    inputs = _section(_doc(), "5.").subsections[0]
    assert inputs.title.endswith("Horizontal tail input data")
    figure = next(f for f in inputs.figures if f.key == "planform_htail_lra")
    assert figure.data is not None and not figure.absent_reason
    names = [series.name for series in figure.data.series]
    assert any("Horizontal tail" in n for n in names)
    assert any("Elevator" in n for n in names), "the control surface is drawn on it"
    assert any("Loads reference axis" in n for n in names)
    stations = build_tail_span(io.load_project(_GA))["htail"][0].stations
    assert len(figure.data.points) == len(stations)


def test_the_input_data_subsection_states_the_axis_station_by_station():
    """The axis is a table as well as a line: a figure cannot be read off."""
    from sloads.modules.tail_span import build_tail_span

    inputs = _section(_doc(), "5.").subsections[0]
    table = next(t for t in inputs.tables
                 if t.title.startswith("Loads reference axis by station"))
    stations = build_tail_span(io.load_project(_GA))["htail"][0].stations
    assert len(table.rows) == len(stations)
    assert "SF" not in table.columns, "geometry carries no factor"
    # The constants moved here from the chordwise subsection: they are derived
    # from the surface's geometry, not from the pressures they scale.
    assert any(t.title == "Aerodynamic constants of the surface"
               for t in inputs.tables)
    chordwise = _section(_doc(), "5.").subsections[3]
    assert not any(t.title == "Aerodynamic constants of the surface"
                   for t in chordwise.tables)


def test_the_spanwise_subsection_says_why_there_is_no_hinge_moment():
    """Absence-is-content, and the specific absence a reader will look for.

    The hinge line is known -- it is the chordwise station the pressure
    distribution is built on -- so a missing hinge moment is a modelling choice,
    not a missing calculation, and the subsection names the two inputs that
    would change it rather than leaving the reader to find them.
    """
    span = _section(_doc(), "5.").subsections[4]
    prose = " ".join(span.body)
    assert "no hinge moment is stated" in prose
    assert "hinge line itself is known" in prose
    assert "actuator" in prose and "span" in prose
    root = next(t for t in span.tables if t.title.endswith("at the root (LIMIT)"))
    assert not any("Hinge" in c for c in root.columns), (
        "a column of dashes is not a statement")


def test_appendix_d_places_every_load_on_the_airplane():
    """The deck is loadable: every row carries the point its force acts at.

    In airplane axes, from the same mapper the exported deck uses, so a row here
    and a card in the deck place the same load at the same point.
    """
    from sloads.export.coordinates import tail_station_to_airplane
    from sloads.modules.tail_span import build_tail_span

    table = _appendix(_doc(), oc.HTAIL_LOAD_STATIONS).tables[0]
    assert [c.split(" ")[0] for c in table.columns[:6]] == [
        "Case", "GID", "X", "Y", "Z", "Fz"]
    # Built from the **projected** inputs, which is what the document is a
    # function of (OR-43): the loads reference axis is an sloads-only field, so
    # the projection returns it to the quarter chord and the axis moves with it.
    # Comparing against the raw file would be comparing two different airplanes.
    from sloads.field_registry import reduce_to_oracle_inputs

    results = build_tail_span(reduce_to_oracle_inputs(io.load_project(_GA)))["htail"]
    want = [tail_station_to_airplane(st.x, st.y, "htail", st.z)
            for r in results for st in r.stations]
    for row, (x, y, z) in zip(table.rows, want):
        assert row[2] == format_value(x) and row[3] == format_value(y)
        assert row[4] == format_value(z)
    # Both surfaces span in ``y`` and load in ``z`` here, so the appendix spans
    # the airplane rather than one side of it -- the check that this is the
    # full-span set and not a half read twice.
    ys = {float(r[3]) for r in table.rows}
    assert min(ys) < 0 < max(ys)


if __name__ == "__main__":                                    # pragma: no cover
    import sys as _sys
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  ok   {name}")
            except Exception as exc:                          # noqa: BLE001
                failed += 1
                print(f"  FAIL {name}: {exc}")
    print(f"\n{failed} failed")
    _sys.exit(1 if failed else 0)
