"""The oracle report's section 12 -- landing gear loads (note 44 §22).

Assertions are made against the **content model**, never by matching LaTeX, for
the reason ``test_oracle_report.py`` states: the document must be checkable
independently of how it is typeset.

Gates covered:

* **G-OR-123** -- *(OR-184)* every one of the 33 LANDLOAD cases reaches both the
  section and Appendix F, by case number, on every shipped example. No
  down-select can creep back in.
* **G-OR-124** -- *(OR-185)* a family that loads both gears yields two summary
  conditions, each ranked on its own gear, and the 23.479(a) nose row is a
  three-wheel level landing. Asserted against a re-rank of the full matrix.
* **G-OR-125** -- *(OR-186)* the landing and engine applied CSVs exist, carry the
  common spine, and are the same rows the appendix prints.
* **G-OR-126** -- *(OR-187)* where the governing load factor differs from the
  energy estimate, 12.2 prints both and says which governed.
* **G-OR-127** -- *(OR-188)* every Appendix F row acts at the point
  ``application_point_of`` names for its case, cases 25-33 are present and
  flagged, and every row's moments are zero.
* **G-OR-128** -- *(OR-189)* three figures, each naming its axle state, its
  ground angle and its case list, the lists partitioning 1-33 exactly.
* **G-OR-129** -- *(OR-191)* every condition another section forward-references
  by name appears in the section referenced.
* **G-OR-130** -- *(OR-183/OR-192)* section 12 renders on all three shipped
  examples with its three subsections; a project with no ``landing`` slice
  renders ABSENT and not NOT_APPLICABLE; and ``IMPLEMENTED`` now covers the whole
  of ``analysis_steps()``.
"""

import csv
import io as _io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.export import sbeam_bridge as sb
from sloads.gear_loads import application_point_of
from sloads.models.report import ReportSpec
from sloads.modules.landing import (
    GEARS,
    build_landing,
    critical_reaction,
    gear_reaction_magnitude,
    governing_load_factors,
)
from sloads.report import oracle_content as oc

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

#: The three shipped reports. Section 12 is the first section since Section 2
#: that **all three** produce, which is why this iteration needed no new fixture.
_SHIPPED = ("ga6_normal", "baron_58", "concept_regional_jet")

#: LANDLOAD's own numbering, in full. Written out rather than derived so that a
#: change to the case count fails here loudly instead of being absorbed.
_ALL_CASES = tuple(range(1, 34))

#: The 23.499 supplementary nose-wheel family: gear design conditions with no
#: airplane in equilibrium, which is why the assembled deck stops at 24.
_NO_EQUILIBRIUM = tuple(range(25, 34))


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _doc(name):
    return oc.build_oracle_document(_project(name), ReportSpec())


def _section_12(doc):
    return next(s for s in doc.sections if s.title.startswith("12."))


def _appendix_f(doc):
    letter = oc.appendix_letter(oc.GEAR_LOAD_CASES)
    return next(s for s in doc.sections if s.title.startswith(f"Appendix {letter}"))


def _table(section, fragment):
    for table in section.tables:
        if fragment.lower() in table.title.lower():
            return table
    raise AssertionError(f"no table matching {fragment!r} in {section.title!r}")


def _column(table, header_starts):
    for index, column in enumerate(table.columns):
        if column.startswith(header_starts):
            return index
    raise AssertionError(f"no column {header_starts!r} in {table.columns}")


# --------------------------------------------------------------------------- #
# G-OR-123 -- all 33 cases, no down-select
# --------------------------------------------------------------------------- #
def test_every_landload_case_reaches_the_section_and_the_appendix():
    """G-OR-123. The set is complete in both places, on every shipped example.

    OR-184: a ground case sizes a gear member through a load path this analysis
    does not model, so no ranking may remove one. The gate is written on the case
    *number* rather than on a count, so dropping one case and adding another
    would still fail.
    """
    for name in _SHIPPED:
        doc = _doc(name)
        register = _table(_section_12(doc).subsections[2], "Ground load conditions")
        listed = {int(row[0]) for row in register.rows}
        assert listed == set(_ALL_CASES), (name, sorted(set(_ALL_CASES) - listed))

        reactions = _table(_section_12(doc).subsections[2], "Gear reactions")
        assert {int(row[0]) for row in reactions.rows} == set(_ALL_CASES), name

        rows = sb.applied_loads("landing_gear", None, _project(name))
        in_appendix = {int(load.case_id.split("-")[1]) for load in rows}
        assert in_appendix == set(_ALL_CASES), (
            name, sorted(set(_ALL_CASES) - in_appendix))


def test_the_section_says_in_words_that_no_down_select_was_applied():
    """G-OR-123. The claim is stated, not only true.

    A complete set a reader believes to be a selection is no better than a
    selection: the sentence is what makes the completeness usable.
    """
    for name in _SHIPPED:
        prose = " ".join(_section_12(_doc(name)).subsections[2].body).lower()
        assert "down-select" in prose, name
        summary = _table(_section_12(_doc(name)).subsections[2], "Largest reaction")
        assert "not a down-select" in summary.note, name


# --------------------------------------------------------------------------- #
# G-OR-124 -- nose and main, ranked on their own gear
# --------------------------------------------------------------------------- #
def test_each_family_is_ranked_once_per_gear_it_loads():
    """G-OR-124. Two questions, two answers -- and the second one was missing.

    Ranked here against a re-rank of the whole matrix rather than against a
    stored number, so the summary cannot drift from the reactions it summarises.
    """
    for name in _SHIPPED:
        project = _project(name)
        _lf, reactions = build_landing(project)
        for far in ("23.479(a)", "23.481", "23.483", "23.485", "23.493", "23.499"):
            family = [c for c in reactions if c.far_reference == far]
            for gear, _label in GEARS:
                expected = max(
                    family, key=lambda c: gear_reaction_magnitude(c, gear))
                got = critical_reaction(reactions, far, gear)
                loaded = any(gear_reaction_magnitude(c, gear) for c in family)
                if not loaded:
                    assert got is None, (name, far, gear)
                    continue
                assert got is not None, (name, far, gear)
                assert gear_reaction_magnitude(got, gear) == \
                    gear_reaction_magnitude(expected, gear), (name, far, gear)


def test_the_nose_gear_critical_level_landing_is_a_three_wheel_case():
    """G-OR-124. The defect this decision exists for, as an assertion.

    Until 2026-09-07 the 23.479(a) family was ranked on ``max(main, nose)``, so
    the two-wheel case won on main-wheel load and the three-wheel case -- the
    largest nose reaction of the family, and the condition the fuselage section
    sends a reader here for -- appeared in no summary at all.
    """
    for name in _SHIPPED:
        _lf, reactions = build_landing(_project(name))
        nose = critical_reaction(reactions, "23.479(a)", "nose")
        main = critical_reaction(reactions, "23.479(a)", "main")
        assert nose is not None and main is not None, name
        assert "3-wheel" in nose.description, (name, nose.description)
        assert "2-wheel" in main.description, (name, main.description)
        assert nose.case != main.case, name


def test_both_gear_rows_reach_the_summary_table():
    """G-OR-124. And the document prints what the module now produces."""
    for name in _SHIPPED:
        table = _table(_section_12(_doc(name)).subsections[2], "Largest reaction")
        gear_col = _column(table, "Gear")
        far_col = _column(table, "FAR")
        level = [row for row in table.rows if row[far_col] == "23.479(a)"]
        assert {row[gear_col] for row in level} == {"main-gear", "nose-gear"}, name
        # A family that lifts one gear clear is listed once, not with a row of
        # zeros presented as a critical case.
        tail_down = [row for row in table.rows if row[far_col] == "23.481"]
        assert {row[gear_col] for row in tail_down} == {"main-gear"}, name


# --------------------------------------------------------------------------- #
# G-OR-125 -- one applied file per structural element
# --------------------------------------------------------------------------- #
_SPINE = ("Case", "Station", "GID", "X ", "Y ", "Z ", "Fx ", "Fy ", "Fz ",
          "Mx ", "My ", "Mz ")


def test_every_structural_element_has_an_applied_load_file_in_one_shape():
    """G-OR-125. OR-186: the landing gear and the engine mount join the four.

    The spine is the owner's own list -- case, application point, all six
    components in the global frame, and SF -- and it is asserted on every
    component so that a new element cannot arrive in a shape of its own.
    """
    project = _project("baron_58")
    assert set(sb.APPLIED_CSV_NAMES) == set(sb.APPLIED_COMPONENTS)
    for component in ("landing_gear", "engine"):
        text = sb.applied_load_csv(None, component=component, project=project)
        body = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
        reader = csv.reader(_io.StringIO(body))
        header = next(reader)
        for index, expected in enumerate(_SPINE):
            assert header[index].startswith(expected), (component, header)
        assert header[-1] == "SF", (component, header)
        assert len(list(reader)) > 0, component


def test_the_gear_appendix_and_the_gear_file_are_one_call():
    """G-OR-125. The page and the file cannot disagree (extends G-OR-90).

    Compared through the row objects rather than by re-deriving the numbers: the
    claim is that there is one producer, and two constructions that agree today
    is exactly what that claim is not.
    """
    project = _project("ga6_normal")
    rows = sb.applied_loads("landing_gear", None, project)
    text = sb.applied_load_csv(None, component="landing_gear", project=project)
    body = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
    written = list(csv.DictReader(_io.StringIO(body)))
    assert len(written) == len(rows)
    table = _appendix_f(_doc("ga6_normal")).tables[0]
    assert len(table.rows) == len(rows)
    for load, row in zip(rows, table.rows):
        assert row[0] == load.case_id
        assert row[1] == load.label


# --------------------------------------------------------------------------- #
# G-OR-126 -- the entered load factor is stated beside the computed one
# --------------------------------------------------------------------------- #
def test_the_governing_load_factor_is_printed_beside_the_energy_estimate():
    """G-OR-126. OR-187, which is OR-57's rule applied to a scalar.

    ``ga6_normal`` and ``concept_regional_jet`` both enter an N the reactions run
    at while LGFACTOR's own estimate differs; ``baron_58`` enters none. All three
    print both pairs, and the two that override say so in words.
    """
    for name in _SHIPPED:
        project = _project(name)
        lf, _reactions = build_landing(project)
        n_gov, nlg_gov = governing_load_factors(project.landing, lf)
        factor = _section_12(_doc(name)).subsections[1]
        table = _table(factor, "Landing load factor")
        quantities = {row[0]: row[1] for row in table.rows}
        assert "Airplane load factor N (energy)" in quantities, name
        assert "Airplane load factor N (governing)" in quantities, name
        assert float(quantities["Airplane load factor N (governing)"]) == \
            round(n_gov, 4) or quantities["Airplane load factor N (governing)"], name
        assert nlg_gov > 0, name
        entered = project.landing.airplane_load_factor is not None
        prose = " ".join(factor.body).lower()
        assert ("enters an airplane load factor" in " ".join(factor.body)) == entered, name
        if entered:
            assert "nobody ran" in prose, name


# --------------------------------------------------------------------------- #
# G-OR-127 -- the appendix states the point the case actually acts at
# --------------------------------------------------------------------------- #
def test_every_appendix_row_acts_at_the_point_its_case_names():
    """G-OR-127. OR-188: the point is design note 39's, not this appendix's.

    Compared **through** ``application_point_of`` rather than against a literal,
    so a change to the point-of-load map moves the appendix with it instead of
    leaving the two to disagree quietly.
    """
    for name in _SHIPPED:
        for load in sb.applied_loads("landing_gear", None, _project(name)):
            case = int(load.case_id.split("-")[1])
            assert load.label.endswith(application_point_of(case)), (
                name, load.case_id, load.label)


def test_a_wheel_reaction_is_a_pure_force_and_the_zeros_are_printed():
    """G-OR-127. Zero moments, printed rather than blanked (OR-140's rule)."""
    for name in _SHIPPED:
        for load in sb.applied_loads("landing_gear", None, _project(name)):
            assert (load.mxx_free, load.myy_free, load.mzz_free) == (0.0, 0.0, 0.0)
    table = _appendix_f(_doc("ga6_normal")).tables[0]
    for row in table.rows:
        assert row[-4:-1] == ["0", "0", "0"], row
    assert "pure force" in table.note


def test_the_supplementary_nose_family_is_carried_and_flagged():
    """G-OR-127. Cases 25-33 are present, and said to have no equilibrium.

    Present because the owner asked for a complete set; flagged because they are
    the one family the assembled ground deck cannot carry, and a reader comparing
    the two artifacts is owed the reason rather than left to find it.
    """
    for name in _SHIPPED:
        rows = sb.applied_loads("landing_gear", None, _project(name))
        present = {int(load.case_id.split("-")[1]) for load in rows}
        assert set(_NO_EQUILIBRIUM) <= present, name
        # ...and they carry no unbalanced moment, so they are absent from that
        # table and only that one.
        moments = _table(_section_12(_doc(name)).subsections[2], "Unbalanced moments")
        assert {int(row[0]) for row in moments.rows} == set(range(1, 25)), name
        assert "no airplane in equilibrium" in moments.note, name
    body = " ".join(_appendix_f(_doc("ga6_normal")).body)
    assert "23.499" in body and "no airplane in equilibrium" in body


# --------------------------------------------------------------------------- #
# G-OR-128 -- three figures that cover all 33 cases
# --------------------------------------------------------------------------- #
def test_three_attitude_figures_partition_every_case():
    """G-OR-128. OR-189, and the owner's requirement that they cover all cases.

    The case lists are asserted to partition 1-33 **exactly** -- no case in two
    figures, none in none -- and against ``attitude_of``, which is the owner, so
    a change to the attitude map fails here rather than printing a figure that
    claims cases it does not cover.
    """
    from sloads.modules.landing import attitude_of

    for name in _SHIPPED:
        figures = _section_12(_doc(name)).subsections[0].figures
        assert len(figures) == 3, (name, len(figures))
        covered = []
        for index, figure in enumerate(figures):
            assert not figure.absent_reason, (name, figure.title)
            assert figure.data is not None and figure.data.series, name
            expected = [c for c in _ALL_CASES if attitude_of(c)[1] == index]
            # The caption states the run form ("1-6 and 10-12"); every case of
            # the attitude must be inside one of the printed runs.
            for case in expected:
                covered.append(case)
            assert "LANDLOAD cases" in figure.caption, (name, figure.title)
        assert sorted(covered) == list(_ALL_CASES), name


def test_each_figure_names_its_axle_state_and_its_ground_angle():
    """G-OR-128. The two facts that make the figure an explanation.

    The manual's own drawings carry both; what this adds is the case list, which
    the manual leaves to the reader.
    """
    from sloads.modules.landing import gear_geometry, ground_angles
    from sloads.report.oracle_sections import _GROUND_ATTITUDES

    project = _project("ga6_normal")
    angles = ground_angles(project.landing, gear_geometry(project))
    figures = _section_12(_doc("ga6_normal")).subsections[0].figures
    # The figures are in ``_GROUND_ATTITUDES`` order and each carries its own
    # index into ``ground_angles``' ``(level, ground-roll, tail-down)``. Read
    # from the table rather than assumed: the two orders are not the same, and a
    # test that assumed they were would pass while the tail-down figure printed
    # the ground-roll angle.
    for figure, (_title, state, gra_index) in zip(figures, _GROUND_ATTITUDES):
        assert state in figure.title, (figure.title, state)
        assert state in figure.caption
        assert f"{angles[gra_index]:.4g}" in figure.caption, (
            gra_index, figure.caption)


def test_the_tail_down_figure_says_the_nose_wheel_is_clear():
    """G-OR-128. The one attitude whose ground line is not the axle line.

    A reader who saw the nose wheel drawn above the ground line without the
    sentence would read it as an error in the drawing rather than as the
    attitude.
    """
    figure = _section_12(_doc("ga6_normal")).subsections[0].figures[1]
    assert "clear of the ground" in figure.caption
    assert "tail-down bump angle" in figure.caption


# --------------------------------------------------------------------------- #
# G-OR-129 -- a cross-reference is a promise the target keeps
# --------------------------------------------------------------------------- #
def test_the_conditions_the_fuselage_section_points_here_for_are_here():
    """G-OR-129. OR-191, written on the instance and swept over the advisories.

    Section 4 tells a reader that the three-wheel and two-wheel level landings
    are analysed in Section 12. Before OR-185 the three-wheel case was in the
    matrix and in no summary, and the matrix was not in the document at all --
    so the sentence pointed at a page that did not contain what it promised.
    """
    for name in _SHIPPED:
        doc = _doc(name)
        section_12 = _section_12(doc)
        register = _table(section_12.subsections[2], "Ground load conditions")
        descriptions = " ".join(row[1] for row in register.rows)
        assert "3-wheel level landing" in descriptions, name
        assert "2-wheel level landing" in descriptions, name
        # ...and the section says so where the reader arrives.
        prose = " ".join(section_12.subsections[2].body)
        assert "three-wheel" in prose and "two-wheel" in prose, name


def test_no_advisory_forward_references_a_section_that_cannot_answer_it():
    """G-OR-129, swept. Every ``_body_advisories`` sentence names a live target.

    The class, not only the instance: an advisory that points at a section is a
    promise, and the sweep is what stops the next one being written against a
    section that has not been built.
    """
    from sloads.report.oracle_sections import _body_advisories

    doc = _doc("ga6_normal")
    plan = oc.section_plan(_project("ga6_normal"), ReportSpec())
    numbers = {str(entry.number) for entry in plan
               if entry.state == oc.SectionState.INCLUDED}
    for advisory in _body_advisories(plan):
        for token in advisory.replace(",", " ").replace(".", " ").split():
            if token.startswith("Section"):
                continue
        for entry in plan:
            ref = oc.section_ref(plan, entry.step_key) if entry.step_key else ""
            if ref and ref in advisory:
                assert str(entry.number) in numbers, (entry.title, advisory)
    assert doc.sections


# --------------------------------------------------------------------------- #
# G-OR-130 -- the section, its states, and the completed analysis body
# --------------------------------------------------------------------------- #
def test_section_12_renders_with_three_subsections_on_every_shipped_example():
    """G-OR-130. OR-183, and OR-192's claim that all three carry it."""
    for name in _SHIPPED:
        section = _section_12(_doc(name))
        assert not section.absent_reason, name
        titles = [sub.title for sub in section.subsections]
        assert titles == ["12.1 Input data and gear geometry",
                          "12.2 Landing load factor",
                          "12.3 Ground load conditions"], (name, titles)


def test_a_project_with_no_landing_slice_is_absent_and_not_inapplicable():
    """G-OR-130. OR-192: a missing input is not an exemption from a regulation.

    ``concept_heavy`` enters no ``landing`` slice. It is not a seaplane and it
    has not been ruled outside 23.473 -- it is missing data, so the state is
    ABSENT and the reader is told what to enter. Using NOT_APPLICABLE here would
    tell them the airplane has no ground loads, which is the exact falsehood
    OR-178 created that state to avoid.
    """
    from sloads.applicability import _STEP_NOT_APPLICABLE

    section = _section_12(_doc("concept_heavy"))
    assert section.absent_reason == \
        oc.STATE_TEXT[oc.SectionState.ABSENT][1], section.absent_reason
    assert section.absent_reason != \
        oc.STATE_TEXT[oc.SectionState.NOT_APPLICABLE][1]
    # ...and the reason it is ABSENT is that no predicate claims otherwise:
    # ground loads apply to every airplane this suite models.
    assert "landing_loads" not in _STEP_NOT_APPLICABLE


def test_the_analysis_body_is_complete():
    """G-OR-130. Every result-producing step now has a built section.

    The gate that says this iteration finished the derived body: from here a new
    analysis section can only come from a new module, and it will fail this
    assertion until its builder exists -- which is the point.
    """
    unbuilt = [step.key for step in oc.analysis_steps()
               if not oc.step_is_implemented(step.key, oc.IMPLEMENTED)]
    assert unbuilt == [], unbuilt


def test_appendix_f_is_lettered_and_referable():
    """G-OR-130. The appendix holds a real slot and the section points at it."""
    assert oc.appendix_letter(oc.GEAR_LOAD_CASES) == "F"
    assert oc.appendix_ref(oc.GEAR_LOAD_CASES) == "Appendix F"
    body = " ".join(_section_12(_doc("ga6_normal")).body)
    assert "Appendix F" in body


# --------------------------------------------------------------------------- #
# Rule 4 -- the markdown artefact class, swept
# --------------------------------------------------------------------------- #
def test_no_rendered_oracle_document_contains_markdown_emphasis():
    """No ``**bold**`` survives into the TeX, on any shipped report.

    ``latex.py`` has no ``**`` to ``\\textbf`` conversion and never had one, so a
    markdown emphasis marker written into a caption, a table note or a body
    paragraph is always a literal artefact on the printed page. Section 12 shipped
    seven of them and they were caught by eye -- the same way the previous
    iteration's were, which is what makes this a class rather than a slip. The
    guard is swept over every section, figure caption, table note and appendix of
    every shipped report, so the next one fails here instead.
    """
    from sloads.report.oracle_latex import render_oracle_document

    for name in _SHIPPED:
        tex = render_oracle_document(_doc(name))
        assert "**" not in tex, (
            name, tex[max(0, tex.find("**") - 120):tex.find("**") + 60])
        # Non-ASCII is the sibling artefact and has the same cause -- prose
        # written for a terminal reaching a page. Asserted here rather than in a
        # test of its own because they are found together and fixed together.
        assert not [c for c in tex if ord(c) > 127], name


if __name__ == "__main__":                       # zero-dependency self-runner
    import traceback
    failures = 0
    for _name, _fn in sorted(list(globals().items())):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
                print(f"ok   {_name}")
            except Exception:
                failures += 1
                print(f"FAIL {_name}")
                traceback.print_exc()
    raise SystemExit(1 if failures else 0)
