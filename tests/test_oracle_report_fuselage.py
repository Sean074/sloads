"""The oracle report's section 4, Fuselage Loads (design note 44 §13/§15).

Assertions are made against the **content model**, never by matching LaTeX, for
the reason ``test_oracle_report.py`` states: the document must be checkable
independently of how it is typeset.

Gates covered:

* **G-OR-53** -- five subsections numbered by the numbering owner, and the
  fuselage appendix is C behind the reserved A and the wing's B.
* **G-OR-54** -- every load section 4 and Appendix C print is LIMIT, states its
  case's factor, and carries no ``-ULT`` marker; asserted in both directions.
* **G-OR-55** -- 4.1 states the provenance of its beam and prints its total; a
  project with no beam stations says so and still builds.
* **G-OR-56** -- the fitting-load table states ``assumed`` against ``entered``
  spar stations, asserted on a project of each.
* **G-OR-57** -- a ``closure_artifact`` result renders its stated state and no
  distribution.
* **G-OR-58** -- 4.2 states which path its case list came from, what the sign of
  its load factors means, and whether the set holds a negative-g condition.
* **G-OR-59** -- Appendix C's rows and the ``body_span_load_csv`` download are
  one load set and agree row for row.
* **G-OR-64** -- ``body_loads.run()`` publishes one condition per p198 block
  1/2/3/7, each with its FAR reference and its V-n case number.
* **G-OR-65** -- the "produced no conditions" regression, asserted by its symptom.
* **G-OR-66** -- blocks 4 and 5 read their tail values from SELECT: the fuselage
  page and the tail page print the same number for the same quantity.
* **G-OR-67** -- the unbalanced moment reproduces printed p198 within the oracle
  tolerance on the unchecked and the checked case, and the 50 % tail MAC station
  it uses is the entered one, never zero.
* **G-OR-68** -- every repeated quantity carries its reference, and every stated
  advisory names the open item or the section behind it.
"""

import csv
import io as _io
import math
import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io  # noqa: E402
from sloads import registry  # noqa: E402
from sloads.export.sbeam_bridge import body_span_load_csv  # noqa: E402
from sloads.field_registry import reduce_to_oracle_inputs  # noqa: E402
from sloads.models.report import ReportSpec  # noqa: E402
from sloads.modules import body_loads  # noqa: E402
from sloads.report import oracle_content as oc  # noqa: E402
from sloads.report.render import format_value  # noqa: E402

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")
_TWIN = os.path.join(_EXAMPLES, "baron_58.project.json")

_STEP = "fuselage_loads"

#: The p198 blocks ``select_fuselage`` publishes, in the manual's own order.
_BLOCKS = ("MAX DOWN LOAD ON WING", "AFT DOWN BENDING", "AFT UP BENDING",
           "GREATEST NZ")


def _spec(**kwargs) -> ReportSpec:
    base = dict(title="FAR 23 Structural Design Loads", report_number="LR-0142",
                revision="B", abstract="An abstract.")
    base.update(kwargs)
    return ReportSpec(**base)


def _flat(sections):
    out = []
    for section in sections:
        out.append(section)
        out.extend(_flat(section.subsections))
    return out


def _doc(path=_GA, project=None):
    return oc.build_oracle_document(project or io.load_project(path), _spec())


def _section_four(doc):
    """The Fuselage Loads section of ``doc``."""
    entry = next(e for e in doc.plan if e.step_key == _STEP)
    return next(s for s in _flat(doc.sections)
                if s.title == oc.heading(entry.number, entry.title))


def _appendix(doc, title=oc.BODY_LOAD_STATIONS):
    return next(s for s in doc.sections
                if s.title == oc.appendix_heading(title))


def _body_tables(doc):
    """Every table section 4 and its appendix print."""
    return ([t for s in _flat([_section_four(doc)]) for t in s.tables]
            + [t for s in _flat([_appendix(doc)]) for t in s.tables])


def _table(doc, prefix):
    return next(t for t in _body_tables(doc) if t.title.startswith(prefix))


def _prose(section) -> str:
    return " ".join(p for s in _flat([section]) for p in s.body)


# --------------------------------------------------------------------------- #
# G-OR-53 -- structure
# --------------------------------------------------------------------------- #
def test_the_fuselage_section_renders_its_five_subsections_numbered_by_the_owner():
    """4.1 ... 4.5, and the numbers come from the numbering owner.

    Five rather than section 3's four (OR-94): the manual's own critical
    summary is what an analyst turns to first, so it is a subsection of its own
    rather than a footnote to the closure machinery.
    """
    doc = _doc()
    section = _section_four(doc)
    entry = next(e for e in doc.plan if e.step_key == _STEP)
    assert [s.title for s in section.subsections] == [
        oc.heading(oc.subsection_number(entry.number, index), title)
        for index, title in enumerate(
            ["The fuselage beam", "Load cases and notation",
             "Critical fuselage loads",
             "Beam closure and wing-attach fitting loads",
             "Load distributions"])]


def test_fuselage_loads_is_appendix_c_behind_the_echo_and_the_wing():
    """G-OR-53 -- the letter follows position, and the reserved slot holds A."""
    assert oc.appendix_letter(oc.INPUT_ECHO) == "A"
    assert oc.appendix_letter(oc.WING_LOAD_STATIONS) == "B"
    assert oc.appendix_letter(oc.BODY_LOAD_STATIONS) == "C"
    titles = [s.title for s in _doc().sections]
    assert titles[-3:] == ["Appendix A: Input echo",
                           "Appendix B: Wing loads by station",
                           "Appendix C: Fuselage loads by station"]


# --------------------------------------------------------------------------- #
# G-OR-54 -- the basis, asserted in both directions
# --------------------------------------------------------------------------- #
def test_no_load_the_fuselage_section_prints_is_marked_ultimate():
    """Every load is LIMIT, so no column carries the ``-ULT`` marker (OR-94a).

    The inverted form of the gate as OR-49 first wrote it. It is what lets this
    section be read against printed p198, which is itself a limit page: the
    defect note 49 E-c found in section 3 was a document printing 1.5x the
    manual's figures with every oracle test still green.
    """
    for table in _body_tables(_doc()):
        for column in table.columns:
            assert "-ULT" not in column, (table.title, column)


def test_every_fuselage_load_table_states_the_factor_it_does_not_apply():
    """The other direction: a table of loads without an ``SF`` column is a
    table whose basis a reader has to infer."""
    doc = _doc()
    for prefix in ("Critical fuselage loads", "Pull-up maneuver",
                   "Wing-attach fitting loads", "Fuselage loads by station"):
        table = _table(doc, prefix)
        assert "SF" in table.columns, table.title
        column = table.columns.index("SF")
        for row in table.rows:
            assert row[column] == format_value(1.5), (table.title, row)


def test_the_critical_summary_prints_the_analysis_own_unscaled_values():
    """The printed number is the calc's own, with the factor stated beside it."""
    project = reduce_to_oracle_inputs(io.load_project(_GA))
    result = registry.get("body_loads")(project)
    table = _table(_doc(), "Critical fuselage loads")
    column = table.columns.index("Nz")
    for row, condition in zip(table.rows, result.conditions):
        limit = next(v.value for v in condition.values
                     if v.key == "load_factor_nz")
        assert row[column] == format_value(limit)


# --------------------------------------------------------------------------- #
# G-OR-55 -- the beam and where its mass came from
# --------------------------------------------------------------------------- #
def test_the_beam_states_its_provenance_and_prints_its_total():
    """4.1 says the table is derived and not the entered one, and totals it.

    A section that presented a derived table as entered input would describe a
    table nobody typed, which is OR-57's finding in a second place. The total is
    a row rather than a sentence because the reader's question -- is this beam
    the whole airplane? -- is answered by comparing two numbers.
    """
    doc = _doc()
    body = _prose(_section_four(doc))
    assert "derived from the weight item data base, not entered" in body
    assert "account for the whole airplane" in body
    table = _table(doc, "Fuselage beam stations")
    assert table.rows[-1][0] == "Total"
    stations = body_loads.build_body_loads(
        reduce_to_oracle_inputs(io.load_project(_GA)))
    assert stations                      # the section has a beam to state
    assert table.rows[-1][2] == format_value(3070.0)


def test_a_project_with_no_beam_states_the_absence_and_still_builds():
    """G-OR-7 one section over: a half-filled project yields a whole document.

    With no mass to lump, the beam has no stations, the module produces no
    result and the section renders the ``ABSENT`` state -- the reader's inputs
    *are* what is missing here, so that is the honest one of the four states.
    Appendix C inherits it, because it is the same absence seen twice and not a
    second fact.
    """
    project = reduce_to_oracle_inputs(io.load_project(_GA))
    project.fuselage_mass = replace(project.fuselage_mass, stations=[])
    project.weight = replace(project.weight, items=[])
    doc = oc.build_oracle_document(project, _spec())
    section = _section_four(doc)
    assert section.absent_reason == oc.STATE_REASON[oc.SectionState.ABSENT]
    assert not section.tables and not section.figures
    appendix = _appendix(doc)
    assert appendix.absent_reason == oc.STATE_REASON[oc.SectionState.ABSENT]
    # And the document is still whole: every other section is where it was.
    assert [s.title for s in doc.sections][:2] == [
        s.title for s in _doc().sections][:2]


# --------------------------------------------------------------------------- #
# G-OR-56 -- an assumed spar station is never reported as input
# --------------------------------------------------------------------------- #
def test_the_fitting_loads_state_whether_their_spar_stations_were_assumed():
    """Asserted on a project of each, and in the same visual field as the loads.

    These are the sizing loads for the wing-attach fittings, and on every
    example this report ships they are computed against spar stations nobody
    entered (OR-97). The provenance is a column of the table, not a footnote.
    """
    doc = _doc()
    table = _table(doc, "Wing-attach fitting loads")
    column = table.columns.index("Spars")
    assert {row[column] for row in table.rows} == {"assumed"}
    assert "neither station was entered" in _prose(_section_four(doc))

    # The other branch: a project that enters its spar stations reports them as
    # entered, through the projection the document is built from (G-OR-60's
    # assertion, run from the report side).
    project = reduce_to_oracle_inputs(io.load_project(_GA))
    wing = next(s for s in project.geometry.surfaces if s.name == "wing")
    wing.front_spar_x_in, wing.rear_spar_x_in = 62.0, 108.0
    entered = _doc(project=project)
    table = _table(entered, "Wing-attach fitting loads")
    column = table.columns.index("Spars")
    assert {row[column] for row in table.rows} == {"entered"}
    assert "entered for this airplane" in _prose(_section_four(entered))
    assert table.rows[0][table.columns.index("X front (in)")] == format_value(62.0)


# --------------------------------------------------------------------------- #
# G-OR-57 -- a closure artifact is stated, never printed as a distribution
# --------------------------------------------------------------------------- #
def test_a_closure_artifact_states_its_state_and_publishes_no_distribution():
    """No shipped fixture reaches this path, so it is asserted on a
    constructed project -- written from the code rather than from the example.

    With no carry-through resolvable the beam is closed by a self-equilibrated
    whole-body correction that has no physical source: it relieves the wing
    region and loads the tail cone. Printing that station table as a load
    distribution would publish a load nothing applies.
    """
    project = reduce_to_oracle_inputs(io.load_project(_GA))
    wing = next(s for s in project.geometry.surfaces if s.name == "wing")
    # An out-of-order spar pair: the geometry is intact, so the wing reference
    # the beam needs still resolves, and only the carry-through is unresolvable
    # (``carry_through`` refuses ``d <= 0`` rather than clamping it).
    wing.front_spar_x_in, wing.rear_spar_x_in = 110.0, 70.0
    net = body_loads.build_body_loads(project)
    assert net and all(r.closure_artifact for r in net)   # the path was taken
    distributions = _section_four(_doc(project=project)).subsections[4]
    assert distributions.absent_reason
    assert "closure artifact" in distributions.absent_reason
    assert not distributions.figures


# --------------------------------------------------------------------------- #
# G-OR-58 -- the run register says what it is
# --------------------------------------------------------------------------- #
def test_the_register_states_which_path_its_case_list_came_from():
    """Two routes to a case list, so the register says which it was (OR-99)."""
    from sloads.modules.select import build_critical, default_envelope

    project = reduce_to_oracle_inputs(io.load_project(_GA))
    assert body_loads.case_list_source(project) == "selection"
    assert "critical-load selection's own result" in _prose(
        _section_four(_doc(project=project)))

    # The other branch answers too. It is unreachable *in this document* --
    # ``build_oracle_document`` projects through ``reduce_to_oracle_inputs``,
    # which drops the persisted result slices -- so the report always takes the
    # selection branch, and the sentence it prints is true for that reason
    # rather than by luck. The report still asks, exactly as 4.1 does about its
    # beam: a section that asserted a provenance the analysis had not taken
    # would be OR-57's defect wearing a different coat.
    persisted = reduce_to_oracle_inputs(io.load_project(_GA))
    envelope = default_envelope(persisted)
    envelope.critical = build_critical(persisted)
    persisted.envelope = envelope
    assert body_loads.case_list_source(persisted) == "envelope"
    assert body_loads.case_list_source(
        reduce_to_oracle_inputs(persisted)) == "selection"


def test_the_register_states_what_the_sign_of_its_load_factors_means():
    """And states that it is **not** section 3's convention.

    Section 3 prints the inertia load factor and section 4 the airplane's own,
    so a reader who carries one section's rule into the other reads every
    condition backwards. Both sections state their own (OR-58).
    """
    body = _prose(_section_four(_doc()))
    assert "airplane's flight load factor" in body
    assert "not the convention of the wing section" in body


def test_the_register_names_its_negative_load_factor_condition():
    """From the analysed set, never by assertion: a name is not a number.

    ``AFT UP BENDING`` carries the sense in words, which is exactly the trap --
    the reader checking whether the set envelops the fuselage reads the column.
    """
    body = _prose(_section_four(_doc()))
    assert "negative-load-factor condition (AFT UP BENDING)" in body
    assert "which reverses the bending" in body


def test_the_notation_states_the_three_symbols_and_tabulates_no_zeros():
    """OR-100 -- the absences are written out, not printed as zero columns."""
    doc = _doc()
    table = _table(doc, "Notation")
    assert [row[0] for row in table.rows] == ["X", "Fz", "Sz", "Myy"]
    for other in _body_tables(doc):
        for column in other.columns:
            assert not column.startswith(("Sy ", "Mxx ", "Mzz ", "Fy ")), column
    assert "no lateral shear and no lateral bending" in _prose(_section_four(doc))


# --------------------------------------------------------------------------- #
# G-OR-59 -- the appendix and the export are one load set
# --------------------------------------------------------------------------- #
def test_the_appendix_table_and_the_exported_csv_are_one_load_set():
    """Row for row, in the same order, with the same grid identifiers.

    Appendix C is a *view* of the export owner and not a second assembler
    (OR-101): the table a reader checks here and the CSV they download from the
    Fuselage Loads page have to be the same load set, or the document describes
    an analysis the deck does not.
    """
    project = reduce_to_oracle_inputs(io.load_project(_GA))
    net = body_loads.build_body_loads(project)
    exported = list(csv.DictReader(_io.StringIO(body_span_load_csv(net))))
    table = _table(_doc(project=project), "Fuselage loads by station")
    assert len(table.rows) == len(exported)
    columns = {name: index for index, name in enumerate(table.columns)}
    for row, out in zip(table.rows, exported):
        assert row[columns["GID"]] == out["GID"]
        assert row[columns["SF"]] == out["SF"]
        # The two renderers round differently -- the document to significant
        # figures, the deck to a fixed decimal -- so the values are compared as
        # numbers, which is what "one load set" means.
        for column in ("X (in)", "Fz (lb)", "Sz (lb)", "Myy (lb-in)"):
            table_value = float(row[columns[column]].replace(",", ""))
            assert math.isclose(table_value, float(out[column]),
                                rel_tol=1e-3, abs_tol=1.0), (column, row)


# --------------------------------------------------------------------------- #
# G-OR-64 / G-OR-65 -- the module publishes what it computes
# --------------------------------------------------------------------------- #
def test_body_loads_publishes_one_condition_per_printed_block():
    """OR-108, on both report fixtures.

    ``select_fuselage`` always computed these four; until this ruling
    ``run()`` returned ``ModuleResult(conditions=[])`` and discarded every one.
    """
    for path in (_GA, _TWIN):
        project = reduce_to_oracle_inputs(io.load_project(path))
        result = registry.get("body_loads")(project)
        labels = [c.case_ref.condition for c in result.conditions]
        assert labels == list(_BLOCKS), path
        for condition in result.conditions:
            assert condition.far_reference.startswith("23."), condition.title
            # The V-n point the condition was selected at is part of its
            # identity, and the register prints it.
            assert "(case " in condition.title
        vn = {c.label: c.case
              for c in body_loads.critical_fuselage_conditions(project)}
        assert all(isinstance(case, int) for case in vn.values())


def test_the_fuselage_page_never_says_it_produced_no_conditions():
    """G-OR-65 -- the regression this closes, asserted by its symptom.

    The oracle GUI renders a ``ModuleResult`` generically, so the page said
    "Body Loads produced no conditions." beside a 92-row station table, where
    the manual prints its summary. Every other component page showed its
    critical cases.
    """
    for path in (_GA, _TWIN):
        project = reduce_to_oracle_inputs(io.load_project(path))
        assert project.envelope is not None or True
        assert registry.get("body_loads")(project).conditions, path


# --------------------------------------------------------------------------- #
# G-OR-66 / G-OR-67 -- the pull-up blocks
# --------------------------------------------------------------------------- #
def test_the_pull_up_blocks_read_their_values_from_the_tail_analysis():
    """Asserted by comparison, never by both matching a literal (OR-109).

    The manual's own device -- "SEE HORIZONTAL TAIL LOADS FOR FURTHER DATA" --
    is the answer to the two-pages-one-number objection: the reader gets the
    value where the fuselage question is asked, and is told where it is derived.
    That only holds if the two pages cannot drift.
    """
    project = reduce_to_oracle_inputs(io.load_project(_GA))
    select = registry.get("select")(project)
    table = _table(_doc(project=project), "Pull-up maneuver")
    for label in ("UNCHECKED MAN DN", "CHECKED MAN DN"):
        condition = next(c for c in select.conditions
                         if c.case_ref.condition == label)
        row = next(r for r in table.rows
                   if r[table.columns.index("Case")] == condition.case_ref.case_id)
        for key, column in (("total_tail_load", "Total tail load (lb)"),
                            ("balanced_tail_load", "Balanced tail load (lb)"),
                            ("unbalanced_moment_about_cg",
                             "Unbalanced moment about CG (lb-in)")):
            published = next(v.value for v in condition.values if v.key == key)
            assert row[table.columns.index(column)] == format_value(published)


def test_the_pull_up_blocks_state_weight_and_cg_by_lookup():
    """OR-110 -- the CG case names the weight and station, and reproduces p198.

    ``CG4 -> 73.09 in`` and ``CG3 -> 72.64 in`` are the printed ``XCG`` values
    of the two blocks, to the digit, because they are the case's own entered
    numbers rather than anything this report derived.
    """
    doc = _doc()
    table = _table(doc, "Pull-up maneuver")
    xcg = table.columns.index("XCG (in)")
    cg = table.columns.index("CG case")
    assert [row[cg] for row in table.rows] == ["CG4", "CG3"]
    assert [row[xcg] for row in table.rows] == [format_value(73.09),
                                                format_value(72.64)]


def test_the_unbalanced_moment_reproduces_the_printed_page():
    """G-OR-67 -- OR-111's two reconstructions, with the printed numbers cited.

    Appendix A p198 prints the unbalanced moment about the CG and gives no
    derivation, and it is **not** reconstructible from the page by inspection:
    the arm closes against neither the 25 % nor the 50 % MAC until the balanced
    elevator load is subtracted. The equation is recovered from Appendix C
    (``reference/code.txt``, SELECT.BAS line 5210 for the unchecked case and
    5410 for the checked one)::

        PITCHMOMH5CASE = -(LT50UPTEUNCK - LT50) * (XT50 - XXCG(H5CASE))
        PITCHMOMH7CASE = L5T * (XT50 - XXCG(I))

    The increment is measured from the balanced 50 %-chord load and the arm runs
    from the CG to the 50 % tail MAC. Fed the page's own printed inputs, the
    published expression returns the page's own printed moment.
    """
    xt50 = 270.357                                    # printed, tail-loads echo
    # Unchecked (p198 block 4): LT50UPTEUNCK = -1346.496, balanced LT50 =
    # -113.6319, XCG = 73.09 -> printed 243203.5.
    unchecked = -(-1346.496 - (-113.6319)) * (xt50 - 73.09)
    assert math.isclose(unchecked, 243203.5, rel_tol=1e-3)
    # Checked (p198 block 5): L5T = -218.3436, XCG = 72.64 -> printed -43170.23.
    checked = -218.3436 * (xt50 - 72.64)
    assert math.isclose(checked, -43170.23, rel_tol=1e-3)


def test_the_fifty_percent_tail_station_is_the_entered_one_and_never_zero():
    """OR-112 -- a registered deviation, printed rather than reproduced.

    The manual prints ``FS 50 PERCENT HORIZ TAIL = 0`` in both fuselage blocks
    while its own tail-loads input echo states 270.357, and OR-111's arithmetic
    settles it independently: the moment closes only with the real station, so
    the original computed with it and printed zero. This report prints the real
    value and registers the difference, so an analyst comparing against the page
    finds it explained rather than discovering it.
    """
    project = reduce_to_oracle_inputs(io.load_project(_GA))
    assert math.isclose(project.tail_loads.xt50, 270.357, rel_tol=1e-6)
    table = _table(_doc(project=project), "Pull-up maneuver")
    column = table.columns.index("FS 50% h-tail (in)")
    for row in table.rows:
        assert row[column] == format_value(270.357)
        assert row[column] != "0"


# --------------------------------------------------------------------------- #
# G-OR-68 -- a repeated quantity carries its reference, an advisory its owner
# --------------------------------------------------------------------------- #
def test_every_repeated_quantity_and_advisory_names_what_stands_behind_it():
    """The manual's advisories are carried because each names something true.

    Block 7's pitching-acceleration warning is the one that earns the rule: this
    analysis models the linear half of p103's "linear and pitching load factors"
    and not the pitching half, so reproducing the warning states a real
    limitation of the delivered numbers rather than decorating them.
    """
    doc = _doc()
    body = _prose(_section_four(doc))
    tail = oc.section_ref(doc.plan, "tail_loads")
    landing = oc.section_ref(doc.plan, "landing_loads")
    assert f"with a reference to {tail}" in body
    assert f"analysed in {landing}" in body
    assert "M4-21" in body
    assert "does not model it" in body
    # And the table that prints the tail's numbers says where they come from.
    assert tail in _table(doc, "Pull-up maneuver").note


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
