"""The oracle report's sections 7, 8 and 9 -- control-surface pressures (note 44 §19).

Assertions are made against the **content model**, never by matching LaTeX, for
the reason ``test_oracle_report.py`` states: the document must be checkable
independently of how it is typeset.

Gates covered:

* **G-OR-95** -- the three sections add no appendix, no manifest row and no CSV:
  the appendix set stays A-E and the artifact list is unchanged.
* **G-OR-96** -- every load and pressure they print is the module's own
  unscaled value, matched through the content model. The Appendix A tolerances
  live in ``test_aileron.py`` / ``test_flap.py`` / ``test_tab.py``, which run the
  oracle's own inputs; this gate holds the *document* to the module, which is
  the half a report can be wrong about.
* **G-OR-97** -- *(OR-151)* the printed pressure profile integrates back to the
  printed load over the entered area, on every case of every shipped example.
* **G-OR-98** -- *(OR-152)* no pressure in these sections is computed from a
  drawn outline; asserted on ``concept_regional_jet``, whose outline and entered
  area differ by 44 %.
* **G-OR-99** -- *(OR-152)* a disagreeing pair of entered areas is stated and an
  agreeing pair is not. Asserted in both directions.
* **G-OR-100** -- *(OR-150)* the sign convention is stated in every section in
  the same words, names the airplane axis, and the aileron prints both throws
  with opposite signs.
* **G-OR-101** -- *(OR-153, OR-155)* the chordwise figure is built wherever the
  module runs; the locator renders either an outline or a stated absence, never
  an empty axis; the tab rectangle is labelled as drawn.
* **G-OR-102** -- *(OR-148)* no geometry input these sections reference is
  printed by them.
* **G-OR-103** -- *(OR-156)* the flap prints four candidates and names the
  critical one; with no engine record it states the slipstream absence.

Also here: OR-154 (the hinge-moment absence) and OR-157 (one row per tab, naming
which station its station is).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.constants import IN2_PER_FT2
from sloads.derived_geometry import planform_area_sqft
from sloads.models.report import ReportSpec
from sloads.modules.aileron import build_aileron
from sloads.modules.flap import build_flap
from sloads.modules.tab import build_tabs
from sloads.report import oracle_content as oc
from sloads.report import oracle_sections as os_
from sloads.report.render import format_value

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

#: The airplanes these sections are asserted on. Between them they cover every
#: state the sections have: an outline entered for all three surfaces
#: (``ga6_normal``), an aileron outline alone with a slipstream case
#: (``baron_58``), the same without one (``concept_regional_jet``), and the
#: under sense of the area disagreement (``baron_58``; the over sense lost its
#: shipped exerciser when ``cessna_210`` retired, #264).
_SHIPPED = ("ga6_normal", "baron_58", "concept_regional_jet")
_ALL = _SHIPPED

#: Section number -> the module's own record builder, so a gate can compare the
#: document against what it was built from without knowing which section it is.
_BUILDERS = {"7.": build_aileron, "8.": build_flap, "9.": build_tabs}


def _path(name):
    return os.path.join(_EXAMPLES, f"{name}.project.json")


def _doc(name="ga6_normal", **kw):
    return oc.build_oracle_document(io.load_project(_path(name)),
                                    ReportSpec(), **kw)


def _section(doc, starts):
    return next(s for s in doc.sections if s.title.startswith(starts))


def _control_sections(doc):
    return [_section(doc, n) for n in ("7.", "8.", "9.")]


def _prose(section):
    text = " ".join(section.body) + " " + section.absent_reason
    for table in section.tables:
        text += " " + (table.note or "")
    for figure in section.figures:
        text += " " + (figure.caption or "") + " " + (figure.absent_reason or "")
    return text


def _cells(table, column):
    index = next(i for i, c in enumerate(table.columns) if c.startswith(column))
    return [row[index] for row in table.rows]


# --------------------------------------------------------------------------- #
# G-OR-95 -- a pressure, and no appendix
# --------------------------------------------------------------------------- #
def test_the_three_sections_are_built_rather_than_placeholders():
    """OR-147: they carry their analysis on every airplane that enters one."""
    for name in _ALL:
        doc = _doc(name)
        for section in _control_sections(doc):
            assert not section.absent_reason, (name, section.title)
            assert section.tables, (name, section.title)
            assert section.figures, (name, section.title)


def test_the_control_sections_add_no_appendix_and_no_manifest_row():
    """OR-147: the appendix set stays A-E, and no artifact is added.

    The gate that "no appendix" stayed a property of the document rather than an
    intention: a builder registered for one of these steps in
    ``APPENDIX_BUILDERS`` would fail here, not in review.
    """
    doc = _doc()
    # Asserted as the property this decision *is* -- no appendix belongs to any
    # of these three steps -- rather than by pinning the whole appendix list.
    # The list form failed the day the landing gear earned Appendix F, which
    # said nothing about control surfaces (note 44 §22).
    owned = {a.step_key for a in oc.APPENDICES if a.step_key}
    for step in ("aileron_loads", "flap_loads", "tab_loads"):
        assert step not in owned, step
        assert step not in os_.APPENDIX_BUILDERS
    assert [s.title for s in doc.sections if s.title.startswith("Appendix")]
    for step in ("aileron_loads", "flap_loads", "tab_loads"):
        assert not any(a.step_key == step for a in oc.APPENDICES), step


# --------------------------------------------------------------------------- #
# G-OR-96 / G-OR-98 -- the printed numbers are the modules' own
# --------------------------------------------------------------------------- #
def test_the_printed_loads_and_pressures_are_the_modules_own():
    """OR-152: one owner for the pressure, and the document projects it.

    Matched through :func:`format_value` rather than by parsing the cell, so the
    gate compares numbers the way the document rounds them and cannot pass on a
    coincidence of formatting.
    """
    for name in _ALL:
        project = io.load_project(_path(name))
        doc = _doc(name)
        for starts, builder in _BUILDERS.items():
            records = builder(project)
            printed = " ".join(
                " ".join(cell for row in table.rows for cell in row)
                for table in _section(doc, starts).tables)
            for record in records:
                assert format_value(record.load_lb) in printed, (
                    name, starts, record.case)
                for station in record.stations:
                    if station.psi:
                        assert format_value(station.psi) in printed, (
                            name, starts, record.case, station.x)


def test_no_pressure_is_computed_from_a_drawn_outline():
    """G-OR-98: the regional jet's outline is 44 % under its analysis area.

    A figure that shaded the outline and divided the load by it would print
    1.364 * 15.0 / 8.458 psi. That the printed value is the module's, on the one
    airplane where the two are far apart, is what makes the single-owner rule
    checkable rather than a claim.
    """
    project = io.load_project(_path("concept_regional_jet"))
    entered = (project.aileron_loads.area_fwd_hinge_sqft
               + project.aileron_loads.area_aft_hinge_sqft)
    drawn = planform_area_sqft(project, "aileron")
    assert abs(drawn - entered) / entered > 0.4, "fixture no longer disagrees"
    section = _section(_doc("concept_regional_jet"), "7.")
    printed = _cells(section.tables[0], "psi at 0.00c")
    module = build_aileron(project)
    assert printed[0] == format_value(module[0].stations[0].psi)
    assert format_value(module[0].stations[0].psi * entered / drawn) not in printed


# --------------------------------------------------------------------------- #
# G-OR-97 -- the stated spanwise rule is the one the numbers were built with
# --------------------------------------------------------------------------- #
def _entered_area_sqft(project, kind, index=0):
    """The area the module divided by, per OR-151."""
    if kind == "aileron":
        return (project.aileron_loads.area_fwd_hinge_sqft
                + project.aileron_loads.area_aft_hinge_sqft)
    if kind == "flap":
        return project.flap_loads.flap_area_one_side_sqft
    return project.tab_loads.tabs[index].area_sqft


def _profile_mean(stations):
    """Chordwise mean of a profile defined at fractions of chord."""
    points = sorted(stations, key=lambda s: s.x)
    return math.fsum((second.x - first.x) * (first.psi + second.psi) / 2.0
                     for first, second in zip(points, points[1:]))


def test_the_printed_profile_integrates_back_to_the_printed_load():
    """G-OR-97: uniform along the span, in fractions of the local chord.

    The rule OR-151 states is checkable exactly because it is the rule the
    equations already used: mean pressure times the entered area is the load. If
    a future edit changed the profile or the area without the other, this fails.
    """
    for name in _ALL:
        project = io.load_project(_path(name))
        for kind, builder in (("aileron", build_aileron), ("flap", build_flap),
                              ("tab", build_tabs)):
            for index, record in enumerate(builder(project)):
                area = _entered_area_sqft(project, kind, index) * IN2_PER_FT2
                recovered = _profile_mean(record.stations) * area
                assert math.isclose(recovered, record.load_lb, rel_tol=1e-3), (
                    name, kind, record.case, recovered, record.load_lb)


# --------------------------------------------------------------------------- #
# G-OR-99 -- the area disagreement, both ways
# --------------------------------------------------------------------------- #
def test_a_disagreeing_pair_of_entered_areas_is_stated():
    """OR-152: stated, not resolved silently in either direction.

    Both shipped exercisers now disagree in the same direction -- the
    "larger" sense lost its fixture with ``cessna_210`` (#264); the wording
    branch itself is direction-symmetric.
    """
    for name, sense in (("baron_58", "smaller"),
                        ("concept_regional_jet", "smaller")):
        prose = _prose(_section(_doc(name), "7."))
        assert "The two entered areas of this aileron disagree" in prose, name
        assert sense in prose, name


def test_an_agreeing_pair_is_not_stated():
    """The other direction: a statement that always fires says nothing.

    ``ga6_normal`` enters 6.488 sq ft of aileron and draws 6.474 -- 0.2 % apart,
    inside the 2 % the owner set -- and its flap agrees to 0.2 % as well.
    """
    doc = _doc("ga6_normal")
    for starts in ("7.", "8."):
        assert "disagree" not in _prose(_section(doc, starts)), starts


# --------------------------------------------------------------------------- #
# G-OR-100 -- one sign convention
# --------------------------------------------------------------------------- #
def test_every_control_section_states_the_sign_convention_in_the_same_words():
    """OR-150: three sections phrasing one convention three ways is three
    conventions, so the sentence itself is the gate."""
    for name in _ALL:
        for section in _control_sections(_doc(name)):
            prose = _prose(section)
            assert "Pressure is positive acting normal to" in prose, section.title
            assert "nose-down moment about the hinge line" in prose, section.title
            assert "trailing-edge-down moment about it" in prose, section.title
            assert "the airplane z axis" in prose or "the airplane y axis" in prose


def test_the_aileron_prints_both_throws_with_opposite_signs():
    """OR-150: the rule read from both throws, which is why both are printed."""
    for name in _ALL:
        table = _section(_doc(name), "7.").tables[0]
        pressures = [float(c) for c in _cells(table, "psi at 0.00c")]
        assert len(pressures) == 2, name
        assert pressures[0] > 0 > pressures[1], (name, pressures)


def test_every_control_section_states_the_spanwise_rule():
    """OR-151: the ambiguity the oracle leaves is closed in every section."""
    for section in _control_sections(_doc()):
        prose = _prose(section)
        assert "uniform along the span" in prose, section.title
        assert "fractions of the local surface chord" in prose, section.title


def test_every_control_section_says_why_there_is_no_hinge_moment():
    """OR-154: the absence §5.5 states, stated here for the same reason."""
    for section in _control_sections(_doc()):
        prose = _prose(section)
        assert "No hinge moment is stated" in prose, section.title
        assert "forward of the hinge line" in prose, section.title


# --------------------------------------------------------------------------- #
# G-OR-101 -- the two figures
# --------------------------------------------------------------------------- #
def test_the_chordwise_figure_is_built_wherever_the_module_runs():
    """OR-153: it is the module's own profile and needs no geometry."""
    for name in _ALL:
        doc = _doc(name)
        for starts in ("7.", "8.", "9."):
            figures = [f for f in _section(doc, starts).figures
                       if f.key.startswith("chordwise")]
            assert figures, (name, starts)
            for figure in figures:
                assert figure.data is not None and figure.data.series
                assert not figure.absent_reason
                assert figure.data.x_label.startswith("Fraction of the surface")


def test_the_locator_states_its_absence_rather_than_drawing_nothing():
    """OR-153: either the entered outline or a sentence -- never an empty axis.

    Measured: the flap outline is entered on ``ga6_normal`` alone, and so is the
    elevator, so both states are exercised by the shipped set.
    """
    seen = set()
    for name in _ALL:
        doc = _doc(name)
        for starts in ("7.", "8.", "9."):
            for figure in _section(doc, starts).figures:
                if not figure.key.startswith("locator"):
                    continue
                assert bool(figure.data) != bool(figure.absent_reason), (
                    name, figure.key)
                seen.add(bool(figure.data))
    assert seen == {True, False}, "both figure states must be exercised"


def test_the_tab_rectangle_is_labelled_as_drawn():
    """OR-155: a shape a reader could mistake for entered geometry is not drawn
    silently. ``ga6_normal`` is the one shipped example that draws it."""
    figure = next(f for f in _section(_doc(), "9.").figures
                  if f.key.startswith("locator"))
    assert figure.data is not None
    assert "The tab planform is not entered" in figure.caption
    assert "It is a drawing, not" in figure.caption
    tab = io.load_project(_path("ga6_normal")).tab_loads.tabs[0]
    span = tab.area_sqft * IN2_PER_FT2 / tab.mac_in
    drawn = next(s for s in figure.data.series if s.name.startswith("Tab"))
    assert math.isclose(max(drawn.x) - min(drawn.x), span, rel_tol=1e-6)


# --------------------------------------------------------------------------- #
# G-OR-102 -- the geometry is Section 2's
# --------------------------------------------------------------------------- #
def test_no_control_section_reprints_a_geometry_input():
    """OR-148: a deflection limit or an area printed twice is two numbers."""
    project = io.load_project(_path("ga6_normal"))
    doc = _doc("ga6_normal")
    echoed = [project.aileron_loads.down_deflection_deg,
              project.aileron_loads.up_deflection_deg,
              project.aileron_loads.area_fwd_hinge_sqft,
              project.aileron_loads.area_aft_hinge_sqft,
              project.flap_loads.flap_deflection_deg,
              project.flap_loads.flap_chord_ratio]
    for starts in ("7.", "8."):
        cells = {cell for table in _section(doc, starts).tables
                 for row in table.rows for cell in row}
        for value in echoed:
            assert format_value(value) not in cells, (starts, value)


def test_every_control_section_points_at_the_geometry_section():
    """OR-148: referenced through the numbering owner, never as a literal."""
    doc = _doc()
    reference = oc.section_ref(doc.plan, "configuration_layout")
    assert reference
    for section in _control_sections(doc):
        assert reference in " ".join(section.body), section.title
        # ...and exactly once, not doubled by prose that writes "section" itself.
        assert f"section {reference}" not in " ".join(section.body), section.title


# --------------------------------------------------------------------------- #
# G-OR-103 -- the flap, and OR-157 -- the tabs
# --------------------------------------------------------------------------- #
def test_the_flap_prints_four_candidates_and_names_the_critical_one():
    """OR-156: a pick printed without its set is a number nobody can check."""
    for name in _ALL:
        table = next(t for t in _section(_doc(name), "8.").tables
                     if t.title.startswith("Flaps-extended conditions"))
        assert [r[0] for r in table.rows] == ["1G stall", "2G stall",
                                              "2G at VF", "Gust at VF"], name
        assert sum(1 for r in table.rows if r[-1] == "critical") == 1, name


def test_a_flap_with_no_engine_record_states_the_slipstream_absence():
    """OR-156: an absence with a stated consequence, not a smaller number."""
    prose = _prose(_section(_doc("concept_regional_jet"), "8."))
    assert "is not analysed for this airplane" in prose
    assert "an absence to close before the flap is sized" in prose
    with_engine = _prose(_section(_doc("ga6_normal"), "8."))
    assert "The propeller slipstream case of 23.457(b) applies" in with_engine


def test_the_tab_table_has_a_row_per_tab_and_names_its_station():
    """OR-157: never a bare station number, because BL and WL are not one axis."""
    for name in _ALL:
        project = io.load_project(_path(name))
        table = _section(_doc(name), "9.").tables[0]
        assert len(table.rows) == len(project.tab_loads.tabs), name
        for cell in _cells(table, "Station"):
            assert cell.startswith(("Butt line", "Waterline")), (name, cell)


def test_no_load_the_control_sections_print_is_marked_ultimate():
    """Note 49 OR-116, carried into these three: every load is LIMIT and states
    the factor it does not apply."""
    for name in _ALL:
        for section in _control_sections(_doc(name)):
            for table in section.tables:
                assert "SF" in table.columns, (name, table.title)
                assert not any("-ULT" in c for c in table.columns), table.title
                for row in table.rows:
                    assert not any("-ULT" in cell for cell in row), table.title


if __name__ == "__main__":                                    # pragma: no cover
    import sys as _sys
    failed = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
                print(f"  ok   {_name}")
            except Exception as exc:
                failed += 1
                print(f"  FAIL {_name}: {exc}")
    print(f"\n{failed} failed")
    _sys.exit(1 if failed else 0)
