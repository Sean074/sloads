"""The oracle report's section 6, Vertical Tail and Rudder Loads (note 44 §17).

Assertions are made against the **content model**, never by matching LaTeX, for
the reason ``test_oracle_report.py`` states: the document must be checkable
independently of how it is typeset.

Section 5's file owns the machinery both sections share -- the OR-129 partition,
the LIMIT basis, the appendix lettering. This file owns what is *only* true of
the vertical tail, which is the whole reason OR-128 made it a section of its own:
its four conditions rather than nine, its rudder, its own Appendix A oracles,
and the restriction OR-133 places on it and on nothing else.

Gates covered:

* **G-OR-80** -- section 6 renders five subsections numbered by the numbering
  owner (OR-130 agreed four; the input-data subsection was added to both
  sections by the owner's review of 2026-09-07, and the mirror carried it).
* **G-OR-83** -- the printed totals are SELECT's own unscaled values, and every
  condition Appendix A names is present under the name the oracle uses.
* **G-OR-86** -- *(OR-132)* every vertical-tail condition states a rudder load,
  so the summary table has no blank in that column.
* **G-OR-87** -- *(OR-133/OR-134)* on a non-conventional tail, 6.5 and Appendix
  E render the stated state and no table, the restriction is stated in full in
  section 6 and pointed at from section 5, and **section 5, 6.4 and Appendix D
  are byte-identical** to the conventional build. Its companion: the calc is
  untouched -- ``build_tail_span`` still returns the vertical tail's results and
  the balanced deck still assembles its lateral cases.
* **G-OR-88** -- *(OR-135)* the ``SIDE GUST`` row states whether its yaw inertia
  was entered or estimated.

Also here: OR-133a (the condition register and the summary table name the case
the set is short, rather than looking complete), and the owner's 2026-09-07
ruling that 6.1's loads-reference-axis stations survive the withholding because
they are geometry.
"""

import copy
import glob
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io  # noqa: E402
from sloads.models import TailType  # noqa: E402
from sloads.models.report import ReportSpec  # noqa: E402
from sloads.modules.select import default_critical  # noqa: E402
from sloads.modules.tail_span import build_tail_span  # noqa: E402
from sloads.report import oracle_content as oc  # noqa: E402
from sloads.report.render import format_value  # noqa: E402
from sloads.tail_geometry import is_conventional_tail, tail_layout  # noqa: E402

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")
_TWIN = os.path.join(_EXAMPLES, "baron_58.project.json")
#: The shipped T-tails -- the only arrangement OR-134 names that a fixture
#: exercises. ``V_TAIL`` and ``CRUCIFORM`` are run on constructed projects.
_T_TAIL = os.path.join(_EXAMPLES, "atr42_100.project.json")


def _project(path=_GA):
    return io.load_project(path)


def _doc(project=None, path=_GA):
    return oc.build_oracle_document(project or _project(path), ReportSpec())


def _section(doc, title_starts="6."):
    return next(s for s in doc.sections if s.title.startswith(title_starts))


def _appendix(doc, title):
    return next(s for s in doc.sections if s.title == oc.appendix_heading(title))


def _tables(section):
    out = list(section.tables)
    for sub in section.subsections:
        out.extend(_tables(sub))
    return out


def _table(section, starts):
    return next(t for t in _tables(section) if t.title.startswith(starts))


def _cells(table, column):
    i = next(i for i, c in enumerate(table.columns) if c.startswith(column))
    return [row[i] for row in table.rows]


def _prose(section):
    text = " ".join(section.body) + " " + section.absent_reason
    for table in section.tables:
        text += " " + (table.note or "")
    for sub in section.subsections:
        text += " " + _prose(sub)
    return text


def _relaid(path, tail_type):
    """``path``'s project re-entered with a different empennage arrangement."""
    project = copy.deepcopy(_project(path))
    project.geometry.parametric.tail_type = tail_type
    return project


# --------------------------------------------------------------------------- #
# G-OR-80 -- shape and numbering
# --------------------------------------------------------------------------- #
def test_section_six_renders_five_subsections_mirroring_section_five():
    """OR-130's mirror, which is the argument for one builder demonstrated.

    A reader who has read section 5 knows where to look in section 6, and the
    two sections are provably the same analysis read twice -- so the subsection
    titles are asserted to differ only in the surface they name.
    """
    doc = _doc()
    section = _section(doc, "6.")
    assert section.title == "6. Vertical Tail and Rudder Loads"
    assert [s.title for s in section.subsections] == [
        oc.heading(oc.subsection_number("6", i), title)
        for i, title in enumerate(
            ["Vertical tail input data", "Design conditions",
             "Critical vertical tail loads", "Chordwise load distribution",
             "Spanwise loads"])]


def test_neither_section_borrows_the_others_selection_method():
    """OR-131: the categories differ, and a reader carrying one section's list
    into the other reads a different airplane."""
    doc = _doc()
    vtail = _prose(_section(doc, "6."))
    assert "23.441(a)(1)" in vtail and "23.443(b)" in vtail
    # The horizontal tail's own requirements are named in section 5 and are not
    # borrowed here as though they had been searched for this surface.
    for far in ("23.421", "23.423", "23.425"):
        assert far not in vtail, far


# --------------------------------------------------------------------------- #
# G-OR-83 / G-OR-86 -- the printed values, and the rudder column
# --------------------------------------------------------------------------- #
def test_the_printed_totals_are_selects_own_unscaled_values():
    """The boundary states the factor and applies nothing (note 49 OR-116)."""
    for path in (_GA, _TWIN):
        project = _project(path)
        conditions = [c for c in default_critical(project).conditions
                      if c.component == "vtail"]
        summary = _table(_section(_doc(project), "6."), "Critical")
        printed = dict(zip(_cells(summary, "Case"), _cells(summary, "Total load")))
        for condition in conditions:
            total = next((v for v in condition.loads
                          if v.key in ("total_tail_load",
                                       "total_tail_load_cp_25_pct")), None)
            assert total is not None, condition.label
            assert printed[condition.case_ref.case_id] == format_value(total.value)


def test_every_appendix_a_vertical_tail_condition_is_present_and_named():
    """G-OR-83's identity half.

    The printed Appendix A figures -- sudden full rudder **+591** (rudder load
    **167**), yaw to sideslip **-92**, yaw 15 neutral **-526**, side gust
    **+604** at ``IZZ`` **4169.164** -- are compared against the fixture that
    selects them in ``test_select.py::test_critical_vtail_match_appendix_a``,
    page-cited and toleranced there. What the *document* owes is that every
    condition the oracle names is present under the name the oracle uses, and
    that it states the requirement it answers from the analysis's own
    ``far_reference`` rather than from a literal typed here.
    """
    project = _project()
    register = _table(_section(_doc(project), "6."), "Design conditions analysed")
    assert set(_cells(register, "Condition")) == {
        "SUDDEN RUDDER", "YAW TO SIDESLIP", "YAW 15 NEUTRAL", "SIDE GUST"}
    want = {c.case_ref.case_id: (c.label, c.far_reference)
            for c in default_critical(project).conditions if c.component == "vtail"}
    assert {r[0]: (r[1], r[2]) for r in register.rows} == want


def test_every_vertical_tail_condition_states_a_rudder_load():
    """G-OR-86 / OR-132: no blank in that column, on either fixture.

    The column is the point of the table -- what the rudder and its system are
    sized to is not the surface total beside it -- and a blank on half the rows
    would be an absence the analysis could not state a reason for, since
    ``select.rudder_load_parts`` is a pure function of a split every one of
    these conditions already carries.
    """
    for path in (_GA, _TWIN):
        summary = _table(_section(_doc(path=path), "6."), "Critical")
        rudder = _cells(summary, "Rudder load")
        assert len(rudder) == 4, path
        assert all(cell and cell != "--" for cell in rudder), (path, rudder)


def test_the_side_gust_row_states_where_its_yaw_inertia_came_from():
    """G-OR-88 / OR-135: provenance in the same visual field as the value.

    The rod estimate measured **+49 %** over WTONECG's database value on the
    C210 with nothing on the page saying an estimate was in play (C210-25), so
    the number is stated with its basis or not at all.
    """
    doc = _doc()
    state = _table(_section(doc, "6."), "Aerodynamic state")
    izz = [c for c in _cells(state, "Inertia") if c and c != "--"]
    assert izz, "no condition states a yaw inertia"
    text = _prose(_section(doc, "6."))
    assert "estimate" in text.lower() or "entered" in text.lower()


# --------------------------------------------------------------------------- #
# G-OR-87 -- the non-conventional withholding (OR-133 / OR-134)
# --------------------------------------------------------------------------- #
def test_a_conventional_tail_publishes_its_spanwise_loads():
    """The control: the withholding must not fire on the airplanes G-OR-1 builds."""
    for path in (_GA, _TWIN):
        project = _project(path)
        assert is_conventional_tail(project), path
        doc = _doc(project)
        span = _section(doc, "6.").subsections[-1]
        assert not span.absent_reason, path
        assert _appendix(doc, oc.VTAIL_LOAD_STATIONS).tables[0].rows, path


def test_every_arrangement_other_than_conventional_withholds_the_span_loads():
    """OR-134: ``T_TAIL``, ``V_TAIL`` and ``CRUCIFORM`` alike.

    A cruciform fin carries the same horizontal-tail reaction a T-tail's does,
    and a V-tail has no separable vertical surface for the analysis to be about,
    so the gate is over the enum rather than over the one value a fixture
    happens to exercise.
    """
    for tail_type in TailType:
        project = _relaid(_GA, tail_type)
        doc = _doc(project)
        span = _section(doc, "6.").subsections[-1]
        appendix = _appendix(doc, oc.VTAIL_LOAD_STATIONS)
        if tail_type is TailType.CONVENTIONAL:
            assert not span.absent_reason and not appendix.absent_reason
            continue
        assert span.absent_reason and not span.tables, tail_type
        assert appendix.absent_reason and not appendix.tables, tail_type
        # Stated as unsupported, never as unproduced: the loads exist.
        assert span.absent_lead == "Not supported", tail_type
        assert "23.427(a)" in _prose(span), tail_type


def test_the_shipped_t_tails_withhold_and_say_which_arrangement_they_are():
    """The fixture half -- the enum sweep above is on a constructed project."""
    project = _project(_T_TAIL)
    assert tail_layout(project) is TailType.T_TAIL
    doc = _doc(project)
    span = _section(doc, "6.").subsections[-1]
    assert span.absent_reason and not span.tables
    assert "T-tail" in _prose(span)


def _shape(section):
    """A section's whole printed content, for a diff that misses nothing."""
    return (section.title, section.body, section.absent_reason,
            [(t.title, t.columns, t.rows, t.note) for t in _tables(section)])


def test_the_withholding_reaches_nothing_it_was_not_agreed_to_reach():
    """G-OR-87's diff, run on the arrangement that isolates the report's switch.

    **Not against ``T_TAIL``.** A T-tail is not only a report state: ``is_t_tail``
    moves the horizontal tail onto the fin and adds the tip transfer, so a
    conventional-versus-T-tail diff of section 5 would fail on real geometry and
    prove nothing about the withholding. ``CRUCIFORM`` is read by the report and
    by nothing else in the package, so diffing against it changes exactly one
    thing -- OR-133's own switch -- and every difference the diff finds is
    attributable to it.

    Section 5 entire, the vertical tail's chordwise distribution and Appendix D
    are asserted **identical**: OR-133 states positively what it does not
    affect, and a restriction that quietly reached one of them would be a
    different ruling than the one that was agreed.
    """
    plain = _doc(_relaid(_GA, TailType.CONVENTIONAL))
    other = _doc(_relaid(_GA, TailType.CRUCIFORM))

    assert _shape(_section(plain, "5.")) == _shape(_section(other, "5."))
    assert _shape(_appendix(plain, oc.HTAIL_LOAD_STATIONS)) == \
        _shape(_appendix(other, oc.HTAIL_LOAD_STATIONS))
    chord_plain = _section(plain, "6.").subsections[3]
    chord_other = _section(other, "6.").subsections[3]
    assert chord_plain.title.endswith("Chordwise load distribution")
    assert _shape(chord_plain) == _shape(chord_other)
    # ...and the vertical tail's own totals, which OR-133 leaves standing.
    assert _shape(_section(plain, "6.").subsections[2]) != \
        _shape(_section(other, "6.").subsections[2]), \
        "the summary must differ -- by the OR-133a note and nothing else"
    assert _table(_section(plain, "6."), "Critical").rows == \
        _table(_section(other, "6."), "Critical").rows


def test_a_t_tail_still_renders_everything_the_withholding_does_not_reach():
    """The shipped-arrangement half of G-OR-87.

    A T-tail's horizontal tail really does sit on the fin, so its section 5 is
    not byte-identical to a conventional one and must not be asserted to be.
    What is asserted is that nothing there is withheld: every subsection of
    section 5, the vertical tail's chordwise distribution and Appendix D all
    render their content.
    """
    doc = _doc(_project(_T_TAIL))
    five = _section(doc, "5.")
    assert not five.absent_reason
    for sub in five.subsections:
        assert not sub.absent_reason, sub.title
    assert _appendix(doc, oc.HTAIL_LOAD_STATIONS).tables[0].rows
    chord = _section(doc, "6.").subsections[3]
    assert not chord.absent_reason and chord.tables


def test_the_withholding_stays_inside_the_report():
    """OR-133's scope, and the gate that it did not reach the mission deliverable.

    ``build_tail_span`` still returns the vertical tail's results on every
    shipped T-tail -- they are what the balanced deck's lateral cases close
    ``sum(Fy) = 0`` against, and withholding them in the calc would stop those
    cases assembling on three fixtures to document a limitation in them.
    """
    for name in ("atr42_100", "dhc8_dash8", "concept_regional_jet"):
        project = _project(os.path.join(_EXAMPLES, f"{name}.project.json"))
        assert not is_conventional_tail(project), name
        results = build_tail_span(project).get("vtail", [])
        assert results, name
        assert all(r.stations for r in results), name


def test_section_five_points_at_the_restriction_without_stating_it():
    """OR-133: stated in full where the loads are withheld, pointed at from 5.

    A reader who starts at the horizontal tail must not meet the restriction for
    the first time two sections later -- and must not meet it twice, in two
    wordings that could drift apart.
    """
    doc = _doc(_relaid(_GA, TailType.T_TAIL))
    five = _prose(_section(doc, "5."))
    assert "conventional tail" in five
    assert "does not affect anything in this section" in five
    # The quantified statement belongs to section 6 alone.
    assert "27" not in five.split("conventional tail")[1][:400]
    span = _section(doc, "6.").subsections[-1]
    assert "27" in _prose(span) and "73" in _prose(span)


# --------------------------------------------------------------------------- #
# OR-133a -- the condition set says what it is short, and names it
# --------------------------------------------------------------------------- #
def test_the_condition_set_names_the_case_it_is_short_on_a_non_conventional_tail():
    """OR-133a (owner, 2026-09-07).

    OR-133's own distinction is that this is an **omitted** condition and not an
    understated one: there is no row that is too small, there is a row that is
    not there. A four-row table that looks complete reads as a measured
    completeness -- OR-61's argument, one deliverable over -- so both the
    register and the summary say so, and both name the case. Named rather than
    hedged, because a named case is one a reader can check and one note 51's
    D-51.1 can delete.
    """
    section = _section(_doc(_relaid(_GA, TailType.T_TAIL)), "6.")
    for starts in ("Design conditions analysed", "Critical"):
        note = _table(section, starts).note or ""
        assert "short one condition" in note, starts
        assert "23.427(a)" in note, starts


def test_a_conventional_tails_condition_set_claims_nothing_about_a_missing_case():
    """The other direction: the note is absent where nothing is missing."""
    section = _section(_doc(), "6.")
    for starts in ("Design conditions analysed", "Critical"):
        assert "short one condition" not in (_table(section, starts).note or "")


def test_the_loads_reference_axis_survives_the_withholding_and_says_why():
    """The owner's 2026-09-07 ruling: geometry is not withheld to document a
    load limitation, and a station list above a withheld subsection must not
    read as loads that merely failed to compute."""
    section = _section(_doc(_relaid(_GA, TailType.T_TAIL)), "6.")
    axis = _table(section, "Loads reference axis by station")
    assert axis.rows, "the stations are geometry and are printed"
    assert "withheld" in (axis.note or "")
    # ...and it still makes no claim to be a load.
    assert "SF" not in axis.columns


# --------------------------------------------------------------------------- #
# OR-134 -- the field that stopped being a sketch
# --------------------------------------------------------------------------- #
def test_the_tail_arrangement_survives_the_oracle_reduction():
    """The defect this iteration found, gated.

    The document is a function of ``reduce_to_oracle_inputs`` (OR-43). While
    ``tail_type`` was unsupplied it was reset to ``CONVENTIONAL`` before the
    report ever read it, and every airplane -- three shipped T-tails among them
    -- printed the vertical-tail loads OR-133 withholds. The field is
    load-bearing, therefore in the oracle input set (``SUPPLIED_RULE``).
    """
    from sloads.field_registry import oracle_input_paths, reduce_to_oracle_inputs

    assert "geometry.parametric.tail_type" in oracle_input_paths()
    for name, want in (("ga6_normal", TailType.CONVENTIONAL),
                       ("atr42_100", TailType.T_TAIL),
                       ("dhc8_dash8", TailType.T_TAIL)):
        project = _project(os.path.join(_EXAMPLES, f"{name}.project.json"))
        assert tail_layout(reduce_to_oracle_inputs(project)) is want, name


def test_an_undeclared_arrangement_reads_as_conventional():
    """It is the arrangement every other default already assumes -- the planform
    resolver, the beam model and the balanced deck all place two
    fuselage-carried surfaces -- so a project that declares nothing gets the
    analysis it is actually being given, and the layout is a section 2 input the
    document echoes."""
    project = copy.deepcopy(_project())
    project.geometry.parametric = None
    assert tail_layout(project) is None
    assert is_conventional_tail(project)


# --------------------------------------------------------------------------- #
# Appendix E -- a view of the export owner, not a second assembler
# --------------------------------------------------------------------------- #
def test_appendix_e_places_every_load_where_the_deck_places_it():
    """OR-64/OR-101/OR-136: the appendix and the deck are the same load."""
    from sloads.export.coordinates import tail_station_to_airplane

    project = _project()
    table = _appendix(_doc(project), oc.VTAIL_LOAD_STATIONS).tables[0]
    want = [tail_station_to_airplane(st.x, st.y, "vtail", st.z)
            for r in build_tail_span(project).get("vtail", []) for st in r.stations]
    assert len(table.rows) == len(want)
    for row, (x, y, z) in zip(table.rows, want):
        assert row[2] == format_value(x)
        assert row[3] == format_value(y)
        assert row[4] == format_value(z)
    # The fin spans in Z and loads in Y -- the column that makes this the
    # vertical tail's appendix and not a copy of the horizontal tail's.
    assert any(c.startswith("Fy") for c in table.columns)
    zs = [float(r[4]) for r in table.rows]
    assert max(zs) > min(zs), "the fin's stations do not span a waterline range"


def test_no_load_appendix_e_prints_is_marked_ultimate():
    """Every load is LIMIT (note 49 OR-116), and states the factor it applies not."""
    appendix = _appendix(_doc(), oc.VTAIL_LOAD_STATIONS)
    table = appendix.tables[0]
    assert not any("-ULT" in c for c in table.columns)
    assert not any("-ULT" in cell for row in table.rows for cell in row)
    assert "SF" in table.columns
    assert all(cell for cell in _cells(table, "SF"))
    assert all(math.isclose(float(c), 1.5) for c in _cells(table, "SF"))


# --------------------------------------------------------------------------- #
# The class guard: what the document states must survive the reduction
# --------------------------------------------------------------------------- #
def test_the_reduction_preserves_the_geometry_the_document_states_loads_about():
    """The drift guard for the defect class this iteration found twice.

    The oracle document is a function of ``reduce_to_oracle_inputs`` (OR-43), so
    an entered field outside the oracle input set is *silently replaced by its
    default* between the project and the page. Two shipped fields were:
    ``tail_type`` (every airplane read as a conventional tail) and
    ``ref_axis_pct`` (all seven examples enter 40 % of chord; the reduction gave
    25 %, moving ``ga6_normal``'s horizontal-tail root torsion 60.8 -> 34.5
    lb-in and every applied-load X in Appendices D and E 3-6 in off the deck
    card the appendix says it is the same load as).

    Prose could not have caught either. This asserts the property directly, over
    every shipped example and both surfaces: the beam the document states its
    loads about is the beam the analysis ran.
    """
    from sloads.field_registry import reduce_to_oracle_inputs

    for path in sorted(glob.glob(os.path.join(_EXAMPLES, "*.project.json"))):
        project = io.load_project(path)
        reduced = reduce_to_oracle_inputs(project)
        name = os.path.basename(path)
        assert tail_layout(reduced) == tail_layout(project), name
        for component in ("htail", "vtail"):
            full = build_tail_span(project).get(component, [])
            cut = build_tail_span(reduced).get(component, [])
            if not full:
                continue
            assert len(cut) == len(full), (name, component)
            assert cut[0].torsion_axis == full[0].torsion_axis, (name, component)
            for a, b in zip(full, cut):
                for sa, sb in zip(a.stations, b.stations):
                    for field in ("x", "y", "z"):
                        assert math.isclose(getattr(sa, field), getattr(sb, field),
                                            rel_tol=1e-9, abs_tol=1e-9), \
                            (name, component, a.case, field)


def test_the_two_airplanes_the_report_is_built_for_keep_their_loads_too():
    """The same guard one step further, on the fixtures G-OR-1 actually builds.

    Restricted to those two deliberately. ``concept_regional_jet``'s horizontal
    tail *does* move under the reduction -- root ``Fz`` -175.6 -> -214.5 lb,
    from ``weight.items[].consumable`` being reset -- which is the same defect
    class in the weight slice rather than the geometry one, found here on
    2026-09-07 and filed with that measurement rather than swept into a
    document-section change. Exempting it silently is what this gate exists to
    prevent, so it is named.
    """
    from sloads.field_registry import reduce_to_oracle_inputs

    for path in (_GA, _TWIN):
        project = io.load_project(path)
        reduced = reduce_to_oracle_inputs(project)
        for component in ("htail", "vtail"):
            full = build_tail_span(project).get(component, [])
            cut = build_tail_span(reduced).get(component, [])
            for a, b in zip(full, cut):
                for sa, sb in zip(a.stations, b.stations):
                    assert math.isclose(sa.fz, sb.fz, rel_tol=1e-9, abs_tol=1e-9), \
                        (os.path.basename(path), component, a.case)


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
