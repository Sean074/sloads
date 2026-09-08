"""The oracle report's Appendix A -- the balanced V-n conditions (note 44 §23).

Assertions are made against the **content model**, never by matching LaTeX, for
the reason ``test_oracle_report.py`` states: the document must be checkable
independently of how it is typeset.

Gates covered:

* **G-OR-131** -- *(OR-194/OR-196)* Appendix A renders on every shipped example
  with one row per V-n point and no others, in the agreed columns, in the
  manual's own row order, landscape; and the retired input echo leaves no
  dangling reference behind it.
* **G-OR-132** -- *(OR-195)* nothing in Appendix A duplicates a table another
  section carries, except the mass cases.
* **G-OR-133** -- *(OR-197/OR-200)* every stamped case id appears in exactly one
  row, a multiply-selected point shows **all** of its ids, and no ``EM-``/``LG-``
  id appears anywhere.
* **G-OR-134** -- *(OR-198)* every row's NX is ``-DX/W`` through the owner
  ``select`` and ``wing_inertia`` read, and the thrust statement is present.
* **G-OR-135** -- *(OR-199)* the CG id map is a bijection over ``flight_cases``
  order and agrees with section 2.2; on ``ga6_normal`` it reproduces the
  manual's own ``CG1``..``CG4``.
* **G-OR-136** -- *(OR-201)* the CSV's rows are the appendix's rows.
* **G-OR-137** -- *(OR-202)* every ``OR-n``/``G-OR-n`` cited anywhere in the tree
  is defined in a design note. The gate that would have caught the missing
  OR-193 row.
* **G-OR-138** -- *(OR-193/OR-202)* a condition with no point of application
  takes the point of the condition it follows, and on a multi-engine airplane
  that is the **same engine's** -- the property, not a digest.

**The numbers are not re-oracled here.** The V-n matrix is oracle-locked against
Ref 1 Appendix A p179-180 by ``tests/test_flight_envelope.py``, whose tolerances
are each derived from a stated effect (review CR-B-5). Appendix A is a *view* of
that matrix, so what this file owes is **view fidelity** -- every printed cell is
its point's own value through the document's formatter, and nothing is rounded,
reordered or dropped on the way to the page. A second set of assertions against
the manual here would be a second owner for one fact, which is what required
practice 3 exists to prevent.
"""

import csv
import io as _io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.aero_curves import inertia_drag_factor
from sloads.cg_cases import flight_case_ids, flight_cases
from sloads.models.report import ReportSpec
import sloads.modules  # noqa: F401  (module registration)
from sloads.modules.select import default_critical, default_envelope
from sloads.registry import run_all_modules
from sloads.report import oracle_content as oc
from sloads.report.oracle_sections import vn_conditions_csv
from sloads.units import UnitSystem

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = os.path.join(_ROOT, "examples")

#: The three shipped reports, plus the two shapes that stress the CG id map: a
#: five-case project and a single-case one.
_SHIPPED = ("ga6_normal", "baron_58", "concept_regional_jet")
_ALL = _SHIPPED + ("atr42_100", "concept_heavy")


def _project(name):
    """One fixture, **with its modules run**.

    The V-n matrix is balanced against the *computed* structural speeds, which
    the ``structural_speeds`` module writes back into the project -- on
    ``concept_regional_jet`` a matrix built before that runs balances MAN D at
    350 kt instead of 387.5. Every real caller (the report builder, the export
    page) runs the pipeline first; a test that does not is comparing two
    different airplanes.
    """
    project = io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))
    run_all_modules(project)
    return project


def _doc(name):
    return _doc_for(_project(name))


def _doc_for(project):
    return oc.build_oracle_document(project, ReportSpec())


def _appendix_a(doc):
    letter = oc.appendix_letter(oc.VN_CONDITIONS)
    assert letter == "A", letter
    return next(s for s in doc.sections if s.title.startswith("Appendix A"))


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


def _stamped_envelope(project):
    """The matrix with its ids on it, **through the oracle reducer**.

    Resolved once and threaded, as the appendix does, because the selection must
    run against *this* instance. Reduced first for the same reason
    ``build_oracle_document`` reduces (OR-21): the document is a function of the
    oracle projection, and on ``concept_regional_jet`` the file's entered VD of
    350 kt and the projection's computed 387.5 give two different matrices.
    """
    from sloads.field_registry import reduce_to_oracle_inputs

    project = reduce_to_oracle_inputs(project)
    env = default_envelope(project)
    default_critical(project, env)
    return env


def _critical_conditions(project):
    """Every critical condition the selection produced, flattened.

    The independent side of the case-id assertion: these are the conditions the
    ids were minted *for*, so comparing the appendix against them tests the
    stamp rather than agreeing with it.
    """
    import dataclasses

    from sloads.modules.select import build_critical
    from sloads.field_registry import reduce_to_oracle_inputs

    project = reduce_to_oracle_inputs(project)
    result = build_critical(project, default_envelope(project))
    out = []
    for field in dataclasses.fields(result):
        value = getattr(result, field.name)
        if isinstance(value, list) and value and hasattr(value[0], "component"):
            out += value
    return out


def _flat(sections):
    for section in sections:
        yield section
        yield from _flat(section.subsections)


# --------------------------------------------------------------------------- #
# G-OR-131 -- one row per point, and the echo is gone
# --------------------------------------------------------------------------- #
def test_appendix_a_carries_every_balanced_point_and_no_others():
    """G-OR-131. The count is the envelope's, asserted against a fresh build
    rather than a stored number, and every case number appears exactly once."""
    for name in _ALL:
        project = _project(name)
        expected = [p.case for p in _stamped_envelope(project).vn]
        appendix = _appendix_a(_doc_for(project))
        for fragment in ("the flight state", "balancing loads"):
            table = _table(appendix, fragment)
            cases = [int(row[_column(table, "Case")]) for row in table.rows]
            assert cases == expected, (name, fragment)
            assert len(set(cases)) == len(cases), (name, fragment)
        assert appendix.landscape and appendix.page_break, name


def test_the_columns_are_the_agreed_set_and_the_row_order_is_the_manuals():
    """G-OR-131/OR-196. The split is by column group, never by row: both tables
    walk the envelope in its own order, which is the manual's block order
    flattened in place, so a reader holding p180 against the page reads the same
    sequence."""
    project = _project("ga6_normal")
    env = _stamped_envelope(project)
    appendix = _appendix_a(_doc_for(project))

    state = _table(appendix, "the flight state")
    assert state.columns == ["CG", "Config", "Altitude (ft)", "Case",
                             "Condition", "V (kt(EAS))", "NZ", "Alpha (deg)",
                             "G corr", "CL"]
    loads = _table(appendix, "balancing loads")
    assert loads.columns == ["CG", "Case", "Condition", "M(W+F) (lb-in)",
                             "LZW (lb)", "LT (lb)", "DX (lb)", "NX",
                             "W", "F", "HT", "VT"]
    # Keyed by the same CG and case, row for row -- the property that lets the
    # two be read as one table.
    for row_s, row_l, point in zip(state.rows, loads.rows, env.vn):
        assert (row_s[0], row_s[3]) == (row_l[0], row_l[1])
        assert row_s[4] == row_l[2] == point.condition


def test_every_printed_cell_is_its_own_points_value():
    """G-OR-131. View fidelity, which is what this appendix owes: the table is
    the matrix formatted, not the matrix re-derived.

    Asserted cell by cell against the ``VnPoint`` the row came from, through
    ``format_value`` and ``Units`` -- the document's own formatter and unit
    boundary -- so a column that silently rounded, converted twice or reached
    for the wrong field fails here. The *numbers* are oracle-locked one level
    down, in ``tests/test_flight_envelope.py`` against Ref 1 Appendix A p179-180.
    """
    from sloads.report.content import Units
    from sloads.report.render import format_value

    for name in _SHIPPED:
        project = _project(name)
        env = _stamped_envelope(project)
        ids = flight_case_ids(project)
        u = Units(UnitSystem.IMPERIAL)
        appendix = _appendix_a(_doc_for(project))
        state = _table(appendix, "the flight state")
        loads = _table(appendix, "balancing loads")

        for row_s, row_l, point in zip(state.rows, loads.rows, env.vn):
            assert row_s == [
                ids[point.cg], point.config, format_value(point.altitude_ft),
                str(point.case), point.condition,
                format_value(point.v_eas_kt), format_value(point.nz),
                format_value(point.alpha_deg), format_value(point.g_corr),
                format_value(point.cl)], (name, point.case)
            assert row_l[3:8] == [
                u.load(point.m_wf, "moment", 0.0),
                u.load(point.lzw, "force", 0.0),
                u.load(point.lt, "force", 0.0),
                u.load(point.dx, "force", 0.0),
                format_value(inertia_drag_factor(
                    point.dx,
                    {c.name: c.weight_lb
                     for c in flight_cases(project)}[point.cg]))], (
                name, point.case)


def test_the_input_echo_is_retired_and_leaves_no_dangling_reference():
    """G-OR-131/OR-194. The symbol is gone, the slot is filled, and the sentence
    that used to carry the forward reference names the project file instead."""
    assert not hasattr(oc, "INPUT_ECHO")
    assert "Input echo" not in [a.title for a in oc.APPENDICES]
    prose = "\n".join(oc.group_prose("loads_configuration"))
    assert "project file" in prose
    assert "(see Appendix A)" in prose
    # Every appendix slot is now built: the reservation mechanism did its job
    # and there is nothing left holding a letter it does not use.
    assert all(a.built for a in oc.APPENDICES)


# --------------------------------------------------------------------------- #
# G-OR-132 -- the one thing it repeats, and nothing else
# --------------------------------------------------------------------------- #
def test_appendix_a_repeats_no_other_sections_table_except_the_mass_cases():
    """G-OR-132 *(OR-195)*. p179 holds five blocks and four of them are section
    2's -- geometry, structural speeds, altitudes, aero coefficients. Only the
    mass cases cross, because the CG column is unreadable without them.

    Swept by column signature across the whole document rather than asserted
    against a list, so a later section that starts duplicating the matrix fails
    here.
    """
    for name in _SHIPPED:
        doc = _doc(name)
        appendix = _appendix_a(doc)
        mine = {tuple(t.columns) for t in appendix.tables}
        elsewhere = {tuple(t.columns)
                     for s in _flat(doc.sections) if s is not appendix
                     for t in s.tables}
        shared = mine & elsewhere
        assert not shared, (name, shared)
        # ...and the mass-case table is present, carrying p179's own quantities.
        mass = _table(appendix, "mass cases")
        assert mass.columns[:2] == ["CG", "Case"]
        for header in ("Weight", "XCG", "ZCG"):
            _column(mass, header)


# --------------------------------------------------------------------------- #
# G-OR-133 -- every id, all of them, and no engine or gear
# --------------------------------------------------------------------------- #
def test_every_selected_case_id_appears_against_its_own_point():
    """G-OR-133 *(OR-200)*. Asserted against a fresh ``build_critical`` rather
    than a literal: the ids are what the selection minted, and a point selected
    more than once shows all of them."""
    for name in _SHIPPED:
        project = _project(name)
        # Expectations from the **critical conditions**, not from the points'
        # own ``case_refs``: reading the field on both sides would let a lossy
        # stamp lose on both and pass. ``CriticalCondition`` carries its own
        # ``case_ref`` and the V-n case it came from, which is the independent
        # source of the same fact.
        expected = {}
        for condition in _critical_conditions(project):
            if condition.case is not None and condition.case_ref is not None:
                expected.setdefault(condition.case, []).append(
                    condition.case_ref.case_id)
        assert expected, name

        loads = _table(_appendix_a(_doc_for(project)), "balancing loads")
        case_col = _column(loads, "Case")
        columns = {p: _column(loads, p) for p in ("W", "F", "HT", "VT")}
        for row in loads.rows:
            printed = [cell for prefix in ("W", "F", "HT", "VT")
                       for cell in row[columns[prefix]].split(", ") if cell]
            assert sorted(printed) == sorted(
                expected.get(int(row[case_col]), [])), (name, row[case_col])


def test_a_point_selected_by_three_conditions_prints_all_three():
    """G-OR-133, the named instance. On ``ga6_normal`` V-n case 14 is the source
    of VT-01, VT-02 **and** VT-03; before OR-200 the single ``case_ref`` slot
    kept only the last write, so two of the three were lost."""
    loads = _table(_appendix_a(_doc("ga6_normal")), "balancing loads")
    case_col, vt = _column(loads, "Case"), _column(loads, "VT")
    row = next(r for r in loads.rows if r[case_col] == "14")
    assert row[vt] == "VT-01, VT-02, VT-03"
    # ...and the two-component case, which the same slot also truncated.
    row30 = next(r for r in loads.rows if r[case_col] == "30")
    assert row30[_column(loads, "W")] == "W-03"
    assert row30[_column(loads, "F")] == "F-01"


def test_no_engine_or_gear_case_id_reaches_the_vn_register():
    """G-OR-133 *(OR-197)*. ``EM-`` and ``LG-`` ids are minted from engine
    geometry and ground attitudes at prescribed factors; no V-n point is their
    source, which is why there is no column for them and why the absence is
    stated in the body rather than printed as a blank column."""
    for name in _SHIPPED:
        appendix = _appendix_a(_doc(name))
        assert "W" in _table(appendix, "balancing loads").columns
        cells = "\n".join(" ".join(row) for t in appendix.tables for row in t.rows)
        assert not re.search(r"\b(EM|LG)-\d", cells), name
        body = "\n".join(appendix.body)
        assert "Engine mount and landing gear cases do not appear" in body, name


# --------------------------------------------------------------------------- #
# G-OR-134 -- where the drag went
# --------------------------------------------------------------------------- #
def test_every_printed_nx_is_the_inertia_drag_factor_of_its_own_row():
    """G-OR-134 *(OR-198)*. Compared through ``inertia_drag_factor``, the owner
    ``select`` and ``wing_inertia`` both read, so a change to the sign convention
    fails here rather than printing two answers in one report."""
    from sloads.report.render import format_value

    for name in _SHIPPED:
        project = _project(name)
        weights = {c.name: c.weight_lb for c in flight_cases(project)}
        ids = flight_case_ids(project)
        by_id = {ids[n]: w for n, w in weights.items()}
        env = _stamped_envelope(project)
        loads = _table(_appendix_a(_doc_for(project)), "balancing loads")
        nx, cg = _column(loads, "NX"), _column(loads, "CG")
        # Against the raw ``dx``, not the printed cell: the DX column is already
        # rounded to four significant figures, and recomputing from it would be
        # asserting the round trip rather than the derivation.
        for row, point in zip(loads.rows, env.vn):
            expected = inertia_drag_factor(point.dx, by_id[row[cg]])
            assert row[nx] == format_value(expected), (name, row)


def test_the_thrust_assumption_is_stated_in_the_appendix():
    """G-OR-134. The question the table provokes and the manual never answers.
    Thrust is off *by construction* -- the balance writes no X-equation and the
    drag leaves as NX -- and a reader who finds DX with nothing opposing it must
    not be left to infer that the balance is incomplete."""
    for name in _SHIPPED:
        body = "\n".join(_appendix_a(_doc(name)).body)
        assert "Thrust is not modelled" in body, name
        assert "NX = -DX/W" in body, name


# --------------------------------------------------------------------------- #
# G-OR-135 -- the CG ordinal
# --------------------------------------------------------------------------- #
def test_the_cg_ids_are_a_bijection_over_the_flight_cases_in_entry_order():
    """G-OR-135 *(OR-199)*. One id per flight case, positional, and no ground
    case has one -- a ground loading is never balanced over the envelope."""
    for name in _ALL:
        project = _project(name)
        cases = flight_cases(project)
        ids = flight_case_ids(project)
        assert list(ids) == [c.name for c in cases], name
        assert list(ids.values()) == [f"CG{i}" for i in
                                      range(1, len(cases) + 1)], name
        assert len(set(ids.values())) == len(ids), name


def test_on_the_manuals_own_airplane_the_ids_are_the_manuals_own_names():
    """G-OR-135. Ref 1 Appendix A p179 names the mass cases ``CG1``..``CG4`` in
    entry order, and ``ga6_normal`` is that airplane -- so the derivation
    reproduces the manual exactly rather than merely resembling it."""
    assert flight_case_ids(_project("ga6_normal")) == {
        "CG1": "CG1", "CG2": "CG2", "CG3": "CG3", "CG4": "CG4"}


def test_the_appendix_and_section_two_index_the_same_cases_by_the_same_id():
    """G-OR-135. A reader meeting ``CG1`` in Appendix A must find it in section
    2.2; the two render through one owner, so they cannot disagree."""
    for name in _SHIPPED:
        project = _project(name)
        doc, ids = _doc_for(project), flight_case_ids(project)
        mass = _table(_appendix_a(doc), "mass cases")
        assert {row[0]: row[1] for row in mass.rows} == \
               {v: k for k, v in ids.items()}, name

        two = next(t for s in _flat(doc.sections) for t in s.tables
                   if t.title == "Weight and centre-of-gravity cases")
        printed = {row[1]: row[0] for row in two.rows}
        for case_name, case_id in ids.items():
            assert printed[case_name] == case_id, (name, case_name)
        # A ground-only case is marked, not blank, and not given an id.
        assert all(printed[n] == "--" for n in printed if n not in ids), name

        # ...and every CG the conditions name is one of them.
        state = _table(_appendix_a(doc), "the flight state")
        assert {row[0] for row in state.rows} <= set(ids.values()), name


# --------------------------------------------------------------------------- #
# G-OR-136 -- the file and the page are one object
# --------------------------------------------------------------------------- #
def test_the_csv_carries_exactly_the_rows_the_appendix_prints():
    """G-OR-136 *(OR-201)*. Same count, same order, same values -- the file is
    built from the same rows, joined back into the one flat table OR-196 asked
    for, which the page can only show as two."""
    for name in _ALL:
        project = _project(name)
        appendix = _appendix_a(_doc_for(project))
        state = _table(appendix, "the flight state")
        loads = _table(appendix, "balancing loads")

        rows = list(csv.reader(_io.StringIO(vn_conditions_csv(project))))
        assert rows[0] == list(state.columns) + list(loads.columns[3:]), name
        assert len(rows) - 1 == len(state.rows) == len(loads.rows), name
        for out, row_s, row_l in zip(rows[1:], state.rows, loads.rows):
            assert out == row_s + row_l[3:], (name, out)


def test_the_csv_is_empty_rather_than_a_bare_header_when_there_is_no_envelope():
    """G-OR-136. An optional bundle member states "nothing here" by being
    absent, never by shipping a header-only file that reads as "no conditions"."""
    from sloads.models import Project

    assert vn_conditions_csv(Project()) == ""


# --------------------------------------------------------------------------- #
# G-OR-137 -- the register keeps its promises
# --------------------------------------------------------------------------- #
#: Where a decision or a gate may be *defined*. A citation anywhere in the tree
#: must resolve to one of these files.
_NOTE_DIR = os.path.join(_ROOT, "docs", "30_future")
_CITING = ("sloads", "tests", "app", "app_shell", "oracle_app", "scripts",
           "changes", "docs")
_ID = re.compile(r"\b(G-OR-\d+|OR-\d+)\b")


def _defined_ids():
    defined = set()
    for entry in sorted(os.listdir(_NOTE_DIR)):
        if not entry.endswith(".md"):
            continue
        with open(os.path.join(_NOTE_DIR, entry), encoding="utf-8") as fh:
            defined |= set(_ID.findall(fh.read()))
    return defined


def test_every_or_id_cited_anywhere_is_defined_in_a_design_note():
    """G-OR-137 *(OR-202)*. The gate that would have caught the missing OR-193
    row: shipped code cited "note 44 OR-193" while the register stopped at
    OR-192, so the citation pointed outside the record it named.

    A citation is a promise the register keeps -- the same shape OR-191 gave
    cross-section references, one level up.
    """
    defined = _defined_ids()
    assert "OR-193" in defined, "the row this gate exists for is still missing"
    dangling = {}
    for top in _CITING:
        for root, _dirs, files in os.walk(os.path.join(_ROOT, top)):
            if "__pycache__" in root:
                continue
            for entry in files:
                if not entry.endswith((".py", ".md")):
                    continue
                path = os.path.join(root, entry)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for cited in set(_ID.findall(fh.read())) - defined:
                        dangling.setdefault(cited, os.path.relpath(path, _ROOT))
    assert not dangling, (
        "these decision/gate ids are cited but defined in no design note "
        "under docs/30_future/: " + ", ".join(
            f"{k} ({v})" for k, v in sorted(dangling.items())))


# --------------------------------------------------------------------------- #
# G-OR-138 -- a point of application is the same engine's
# --------------------------------------------------------------------------- #
def test_a_condition_with_no_point_takes_the_point_of_its_own_engine():
    """G-OR-138 *(OR-193)*. The property, asserted per engine, rather than the
    frozen digest that was holding it -- a digest fails as a *changed number*, so
    a change that moved the locations and regenerated the baseline would pass.

    Two of the six engine-mount conditions carry no ``loc_*`` values: the
    sudden-stoppage torque of 23.371(c) and the gyroscopic condition of
    23.371(b). The old fallback reached for the first location in the whole set,
    so a twin printed the right engine's stoppage torque and its four gyroscopic
    sub-cases at the **left** engine's butt line -- ten rows on ``atr42_100``,
    fifteen on ``concept_regional_jet``. Stated as: every condition an engine
    emits sits at one point, and no two engines share it.
    """
    from sloads.registry import get
    from sloads.report.render import point_load_records

    for name in ("atr42_100", "dhc8_dash8", "concept_regional_jet"):
        project = _project(name)
        assert len(project.engines) > 1, name
        records = point_load_records(get("engine")(project).conditions)
        assert records, name

        # The producer emits one engine's conditions **together**, which is the
        # premise the fix rests on, so the grouping is the emission block. Not
        # the engine designation: a twin routinely carries the same designation
        # on both engines (``concept_regional_jet`` does), and grouping by it
        # would merge exactly the two sets this gate must keep apart.
        count = len(project.engines)
        assert len(records) % count == 0, (name, len(records), count)
        per = len(records) // count
        blocks = [records[i * per:(i + 1) * per] for i in range(count)]

        seen = []
        for index, block in enumerate(blocks):
            points = {(round(r.x, 6), round(r.y, 6), round(r.z, 6))
                      for r in block}
            assert len(points) == 1, (name, index, sorted(points))
            seen.append(next(iter(points)))
        # ...and the engines are at *different* points, which is the half the
        # defect broke: it collapsed every block onto the first engine's
        # coordinate, so the butt lines stopped being distinct.
        assert len(set(seen)) == count, (name, seen)
        assert len({y for _x, y, _z in seen}) == count, (name, seen)


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
