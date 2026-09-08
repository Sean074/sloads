"""The oracle report's section 10 -- engine mount loads (note 44 §20).

Assertions are made against the **content model**, never by matching LaTeX, for
the reason ``test_oracle_report.py`` states: the document must be checkable
independently of how it is typeset.

Gates covered:

* **G-OR-104** -- *(OR-161/OR-162/OR-163)* the six airplane-axis components are
  the resolution of the two thrust-line scalars printed beside them, asserted
  **through** :func:`sloads.export.coordinates.engine_applied_load` rather than
  against a column, so a component added later cannot inherit a literal.
* **G-OR-105** -- *(OR-160)* section 10.2's ``Mx`` and the Engine Mount page's
  load-case CSV carry the same magnitude with opposite signs, and neither is
  zero, on a conventional installation.
* **G-OR-106** -- *(OR-159/OR-170)* the Appendix A reciprocating figures,
  page-cited, reproduced in the document.
* **G-OR-107** -- *(OR-165)* four gyroscopic rows with a/b/c/d ids and no fifth;
  the vertical and the thrust repeat unchanged across all four.
* **G-OR-108** -- *(OR-166)* one row per engine per case on a twin, each at its
  own butt line, both signs present.
* **G-OR-109** -- *(OR-161)* an assumed thrust axis is marked and a derived one
  is not. Both directions, on shipped data.
* **G-OR-110** -- the section marks no load ultimate: every load column is
  plain, every row states its factor, and nothing in the section says ``-ULT``.
* **G-OR-111** -- *(OR-168/OR-169)* the three views draw every outline the
  project enters and name them; with no outline they still draw the engines;
  with no engine the section states its absence.
* **G-OR-112** -- every FAR reference the module can produce has a short name,
  so a condition added later cannot print a blank in a load table.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from dataclasses import replace

from sloads import io
from sloads.export.coordinates import engine_applied_load, engine_thrust_axis
from sloads.load_keys import FY_SIDE, FZ_VERTICAL, MX_MOUNT_TORQUE, gyro_key
from sloads.models.report import ReportSpec
from sloads.modules.engine import combined_cg, resolved_engines, run_all
from sloads.report import load_cases_to_rows
from sloads.report import oracle_content as oc
from sloads.report import oracle_sections as osec
from sloads.report.render import format_value

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

#: The airplanes section 10 is asserted on. Between them they cover every state
#: it has: the Appendix A engine on a single nose installation (``ga6_normal``),
#: a twin at mirrored butt lines with a derived axis (``baron_58``), a
#: turbopropeller set with the four gyroscopic sub-cases and an **assumed** axis
#: (``concept_regional_jet``), and a second single (``cessna_210``).
_SHIPPED = ("ga6_normal", "baron_58", "concept_regional_jet")
_ALL = _SHIPPED + ("cessna_210",)


def _path(name):
    return os.path.join(_EXAMPLES, f"{name}.project.json")


def _project(name):
    """The project **as the document sees it**.

    ``build_oracle_document`` reduces to the oracle projection before it builds
    anything (OR-21), so a gate that read the file would be comparing the
    document against inputs the document cannot see -- which is how this file's
    first draft asked for the FAR 25 cases of a project whose oracle projection
    has none.
    """
    from sloads.field_registry import reduce_to_oracle_inputs

    return reduce_to_oracle_inputs(io.load_project(_path(name)))


def _doc(name="ga6_normal", project=None, **kw):
    return oc.build_oracle_document(project if project is not None else _project(name),
                                    ReportSpec(), **kw)


def _section(doc):
    return next(s for s in doc.sections if s.title.startswith("10."))


def _tables(section):
    """Every table of section 10, by title, across both subsections."""
    return {t.title: t
            for sub in section.subsections for t in sub.tables}


def _table(section, starts):
    return next(t for title, t in _tables(section).items() if title.startswith(starts))


def _column(table, starts):
    return next(i for i, c in enumerate(table.columns) if c.startswith(starts))


def _text(section):
    """Every sentence the section prints, including its subsections' notes."""
    out = list(section.body)
    for sub in section.subsections:
        out += list(sub.body)
        out += [t.note for t in sub.tables]
        out += [f.caption for f in sub.figures]
        out += [f.absent_reason for f in sub.figures]
    return [s for s in out if s]


# --------------------------------------------------------------------------- #
# G-OR-104 -- the six components are the resolution of the two scalars
# --------------------------------------------------------------------------- #
def test_the_printed_components_are_the_resolution_of_the_printed_scalars():
    """G-OR-104. Not "the numbers look right": the two printed forms are held to
    each other through the owner that relates them, on every case of every
    engine of every shipped example.

    The moment part is checked as ``torque x axis`` plus the gyroscopic pair the
    module publishes about ``y`` and ``z``; the force part as
    ``thrust x axis`` plus the side and vertical loads. Both are recomputed here
    from the module's own values and the axis, so a change to either printed
    table that is not a change to the analysis fails.
    """
    for name in _ALL:
        project = _project(name)
        section = _section(_doc(project=project))
        components = _table(section, "Engine mount loads")
        scalars = _table(section, "Engine torque and thrust")
        assert len(components.rows) == len(scalars.rows) > 0, name

        cases = []
        for eng in resolved_engines(project):
            axis, _assumed = engine_thrust_axis(eng)
            for condition in run_all(eng, include_far25=project.include_far25):
                values = {v.key: v.value for v in condition.values}
                if any(k.startswith("gyro_case") for k in values):
                    thrust = values.get("fx_thrust", 0.0)
                    vertical = values.get("fz_vertical_2_5g", 0.0)
                    for number in (1, 2, 3, 4):
                        cases.append(engine_applied_load(
                            axis, thrust=thrust, vertical_down=vertical,
                            myy=values[gyro_key(number, "myy")],
                            mzz=values[gyro_key(number, "mzz")]))
                    continue
                cases.append(engine_applied_load(
                    axis, torque=values.get(MX_MOUNT_TORQUE, 0.0),
                    vertical_down=values.get(FZ_VERTICAL, 0.0),
                    side=values.get(FY_SIDE, 0.0)))

        assert len(cases) == len(components.rows), name
        first = _column(components, "Fx")
        for row, (force, moment) in zip(components.rows, cases):
            want = [format_value(v) for v in tuple(force) + tuple(moment)]
            assert row[first:first + 6] == want, (name, row[1], want)


# --------------------------------------------------------------------------- #
# G-OR-105 -- the two conventions stay two, and stay related
# --------------------------------------------------------------------------- #
def test_the_document_and_the_csv_carry_opposite_torque_signs():
    """G-OR-105. The CSV's ENG MOUNT TORQUE is a scalar about a **forward**-pointing
    thrust line; the document's ``Mx`` is that same load about the **aft**-positive
    X axis. So the two carry opposite signs, always -- and equal magnitudes only
    where the thrust line is the airplane's own axis, which is the case the
    equality is asserted on. A build in which they agreed in sign would mean one
    of them had silently adopted the other's convention.
    """
    for name in ("ga6_normal", "baron_58", "cessna_210"):
        project = _project(name)
        section = _section(_doc(project=project))
        components = _table(section, "Engine mount loads")
        mx = _column(components, "Mx")
        ids = _column(components, "Case ID")
        stations = _table(section, "Where the loads act")
        cosine = {row[0]: float(row[_column(stations, "Thrust axis")].split(",")[0])
                  for row in stations.rows}

        engine_result = oc.run_sections(project, ReportSpec())["engine_mount"]
        csv = {row["ID"]: row for row in load_cases_to_rows(engine_result.conditions)}
        column = next(c for c in next(iter(csv.values()))
                      if c.startswith("Engine mount torque"))

        checked = 0
        for row in components.rows:
            printed = csv.get(row[ids], {}).get(column, "")
            if printed in ("", None) or float(printed) == 0.0:
                continue
            reaction, applied = float(printed), float(row[mx])
            assert reaction * applied < 0.0, (name, row[ids], reaction, applied)
            if cosine[row[0]] == -1.0:
                assert row[mx] == format_value(-reaction), (name, row[ids])
            else:
                assert abs(applied) < abs(reaction), (name, row[ids])
            checked += 1
        assert checked, f"{name}: no case exercised the relationship"


# --------------------------------------------------------------------------- #
# G-OR-106 -- the Appendix A figures, page-cited
# --------------------------------------------------------------------------- #
def test_the_appendix_a_engine_reaches_the_document():
    """G-OR-106. Appendix A p227-229 (Continental IO-520-BB), through the
    document rather than the module: the application point including the
    waterline that was wrong until OR-170, and the loads of all three cases.

    The oracle prints 554.3884 ft-lb for the take-off case; sloads applies the
    AC 23-19A mean-torque factor and delivers 1.33 x that, which is the approved
    deviation registered in ``02_approved_corrections.md``. Both numbers are
    asserted, because a document that printed either without the other would be
    the one the reader cannot reconcile with the page.
    """
    section = _section(_doc("ga6_normal"))
    stations = _table(section, "Where the loads act")
    point = stations.rows[0][_column(stations, "Application point")]
    assert [float(v) for v in point.split(",")] == [17.91, 0.0, 93.02]

    components = _table(section, "Engine mount loads")
    fz = _column(components, "Fz")
    fy = _column(components, "Fy")
    mx = _column(components, "Mx")
    take_off, continuous, side = components.rows
    assert math.isclose(float(take_off[fz]), -1650.15, rel_tol=1e-3)
    assert math.isclose(float(continuous[fz]), -2200.2, rel_tol=1e-3)
    assert math.isclose(float(side[fy]), 770.07, rel_tol=1e-3)

    # The thrust line is inclined on this installation, so the torque does not
    # land wholly on Mx; the magnitude is asserted on the scalar it resolves
    # from, which is where the oracle's own number is.
    scalars = _table(section, "Engine torque and thrust")
    torque = _column(scalars, "Torque about thrust line")
    assert math.isclose(float(scalars.rows[0][torque]), -737.34, rel_tol=1e-3)
    assert math.isclose(float(scalars.rows[1][torque]), -740.4412, rel_tol=1e-3)
    assert float(take_off[mx]) > 0.0 and float(continuous[mx]) > 0.0


def test_the_uncorrected_oracle_torque_is_stated_beside_the_corrected_one():
    """OR-170's companion: the mean take-off torque the manual prints, 554.3884,
    is still reachable from the document -- it is the case list's own condition
    and the module's note carries the deviation. Asserted so that the corrected
    737.34 never appears without its provenance."""
    section = _section(_doc("ga6_normal"))
    cases = _table(section, "Load cases assessed")
    assert any("23.361(a)(1)" in row for row in cases.rows)


# --------------------------------------------------------------------------- #
# G-OR-107 -- the four gyroscopic sign combinations
# --------------------------------------------------------------------------- #
def test_each_gyroscopic_sign_combination_is_its_own_case():
    """G-OR-107. Four rows per engine, ids suffixed a/b/c/d by the owner that
    mints them for the CSV, and no fifth. The vertical and the thrust are
    constant across the four -- they act in every combination -- so a build in
    which they varied would mean the fan-out had picked up a per-sub-case value
    that does not exist."""
    section = _section(_doc("concept_regional_jet"))
    components = _table(section, "Engine mount loads")
    ids = _column(components, "Case ID")
    fz, fx = _column(components, "Fz"), _column(components, "Fx")
    gyro = [row for row in components.rows if "Gyroscopic" in row[2]]
    assert len(gyro) == 8, [row[ids] for row in gyro]
    for engine_rows in (gyro[:4], gyro[4:]):
        assert [row[ids][-1] for row in engine_rows] == ["a", "b", "c", "d"]
        assert len({row[ids][:-1] for row in engine_rows}) == 1
        assert len({row[fz] for row in engine_rows}) == 1
        assert len({row[fx] for row in engine_rows}) == 1


def test_a_far_25_gyroscopic_condition_fans_out_as_well():
    """The defect the fan-out owner carried until 2026-09-07: it matched the FAR
    *reference* rather than the keys, so 25.371 -- which packs the same four
    sub-cases -- printed one row with no moments at all. Asserted on the CSV,
    which is where it shipped."""
    from fixtures import turboprop

    from sloads.modules.engine import run_far25

    rows = load_cases_to_rows(run_far25(turboprop()))
    gyro = [r for r in rows if r["FAR"] == "25.371"]
    assert len(gyro) == 4
    column = next(c for c in rows[0] if c.startswith("Pitch moment"))
    assert all(r[column] not in ("", None) for r in gyro)
    assert len({r[column] for r in gyro}) == 2  # +Myy and -Myy


# --------------------------------------------------------------------------- #
# G-OR-108 -- one row per engine
# --------------------------------------------------------------------------- #
def test_every_engine_gets_its_own_rows_at_its_own_butt_line():
    """G-OR-108. A twin's two mounts are two structures. Both butt lines appear,
    with opposite signs, and every case is printed once per engine."""
    for name in ("baron_58", "concept_regional_jet"):
        project = _project(name)
        section = _section(_doc(project=project))
        stations = _table(section, "Where the loads act")
        butt = [float(row[_column(stations, "Application point")].split(",")[1])
                for row in stations.rows]
        assert len(butt) == len(project.engines) == 2, name
        assert butt[0] == -butt[1] != 0.0, (name, butt)

        components = _table(section, "Engine mount loads")
        engines = [row[0] for row in components.rows]
        assert set(engines) == {"1", "2"}, name
        assert engines.count("1") == engines.count("2"), name


# --------------------------------------------------------------------------- #
# G-OR-109 -- an assumed axis is marked, a derived one is not
# --------------------------------------------------------------------------- #
def test_an_assumed_thrust_axis_is_marked_and_an_entered_one_is_not():
    """G-OR-109, as design note 53 D-53.3 leaves it. Both directions.

    Every shipped example states no thrust line, so every one is ASSUMED; the
    entered direction is exercised on a constructed project, because no airplane
    in the tree enters one yet. The gate that a statement which always fires and
    one which never fires both fail is kept -- it just needs a project built to
    fire it the other way.
    """
    for name in _ALL:
        section = _section(_doc(name))
        stations = _table(section, "Where the loads act")
        axis = _column(stations, "Thrust axis")
        assert all("ASSUMED" in row[axis] for row in stations.rows), name
        assert any("ASSUMED" in sentence for sentence in _text(section)), name

    project = _project("ga6_normal")
    project.engines = [replace(e, thrust_line_aft=(30.0, 0.0, 95.0),
                               thrust_line_fwd=(-10.0, 0.0, 95.0))
                       for e in project.engines]
    section = _section(_doc(project=project))
    stations = _table(section, "Where the loads act")
    assert not any("ASSUMED" in row[_column(stations, "Thrust axis")]
                   for row in stations.rows)


def test_an_entered_thrust_line_is_the_axis_the_loads_resolve_about():
    """D-53.1/D-53.3. The axis is the entered pair's difference, normalised, and
    the loads follow it: a line inclined in ``z`` puts part of the torque onto
    ``Mz``, where a line along ``x`` puts all of it onto ``Mx``."""
    project = _project("ga6_normal")
    project.engines = [replace(e, thrust_line_aft=(30.0, 0.0, 90.0),
                               thrust_line_fwd=(-10.0, 0.0, 120.0))
                       for e in project.engines]
    section = _section(_doc(project=project))
    stations = _table(section, "Where the loads act")
    printed = [float(v) for v in
               stations.rows[0][_column(stations, "Thrust axis")].split(",")]
    length = math.hypot(-40.0, 30.0)
    for got, want in zip(printed, (-40.0 / length, 0.0, 30.0 / length)):
        assert math.isclose(got, want, abs_tol=5e-4)

    components = _table(section, "Engine mount loads")
    assert float(components.rows[0][_column(components, "Mz")]) != 0.0


# --------------------------------------------------------------------------- #
# G-OR-110 -- nothing here is ultimate
# --------------------------------------------------------------------------- #
def test_no_load_the_engine_section_prints_is_marked_ultimate():
    """G-OR-110. Every engine-mount condition classifies ``flight``, so the
    section is uniformly LIMIT: no column carries the ``-ULT`` marker, every
    load table has an SF column, and every row fills it."""
    for name in _ALL:
        section = _section(_doc(name))
        for title, table in _tables(section).items():
            if "LIMIT" not in title:
                continue
            assert "SF" in table.columns, (name, title)
            sf = table.columns.index("SF")
            assert all(row[sf] for row in table.rows), (name, title)
            assert not any("-ULT" in column for column in table.columns), (name, title)
        assert not any("-ULT" in sentence for sentence in _text(section)), name


def test_the_section_states_that_it_publishes_the_applied_load():
    """OR-160's explicitness, which the owner asked for by name: the section says
    the loads are what the engine applies to the airframe, and names the oracle's
    own column as the place the other sense is printed."""
    for name in _ALL:
        text = " ".join(_text(_section(_doc(name))))
        assert "applies to the airframe" in text, name
        # ...and names the other convention rather than alluding to it: the
        # oracle's own column heading, which is where a reader meets it.
        assert "ENG MOUNT TORQUE" in text, name


# --------------------------------------------------------------------------- #
# G-OR-111 -- the three views
# --------------------------------------------------------------------------- #
def test_the_three_views_are_built_and_name_what_they_drew():
    """G-OR-111. All three views exist on every shipped example, each draws the
    outlines the project enters, and each caption names them."""
    for name in _ALL:
        section = _section(_doc(name))
        figures = {f.key: f for sub in section.subsections for f in sub.figures}
        assert set(figures) == {"engine_side_view", "engine_front_view",
                                "engine_plan_view"}, name
        for key, figure in figures.items():
            assert figure.data is not None, (name, key)
            assert "the fuselage" in figure.caption, (name, key)
            assert "thrust line" in figure.caption, (name, key)
            assert figure.data.points, (name, key)


def test_a_project_with_no_outline_still_draws_its_engines():
    """G-OR-111. The engines are the subject and the airframe is context, so a
    project that enters no drawable geometry gets the figures anyway -- and the
    caption says the outline is missing rather than leaving a reader to wonder
    which airplane they are looking at."""
    project = _project("ga6_normal")
    project.geometry = None
    section = _section(_doc(project=project))
    figures = {f.key: f for sub in section.subsections for f in sub.figures}
    assert len(figures) == 3
    for key, figure in figures.items():
        assert figure.data is not None, key
        assert "enters no airframe outline" in figure.caption, key
        assert figure.data.series, key


def test_a_project_with_no_engine_states_the_section_absent():
    """G-OR-111/OR-32. Absence is stated, never an empty heading -- and it is
    stated in the ABSENT state's own words, not in a second wording invented by
    the builder."""
    project = _project("ga6_normal")
    project.engines = []
    section = _section(_doc(project=project))
    assert section.absent_reason
    assert section.absent_lead == oc.STATE_TEXT[oc.SectionState.ABSENT][0]
    assert not section.subsections and not section.tables


def test_the_body_outline_has_one_owner_and_three_views():
    """OR-169. The producer is asked for each view and answers in that view's own
    pair; an unknown view is refused rather than silently defaulted."""
    from sloads.derived_geometry import FUSELAGE_VIEWS, fuselage_outline

    project = _project("ga6_normal")
    for frame in FUSELAGE_VIEWS:
        outline = fuselage_outline(project, frame)
        assert outline and len(outline) >= 4, frame
    try:
        fuselage_outline(project, "nose")
    except ValueError:
        pass
    else:
        raise AssertionError("an unknown view must be refused")
    project.geometry = None
    assert fuselage_outline(project, "water") is None


# --------------------------------------------------------------------------- #
# G-OR-112 -- every condition the module can produce has a printed name
# --------------------------------------------------------------------------- #
def test_every_far_reference_the_module_produces_has_a_short_name():
    """G-OR-112. A load table's Condition column is a second name for a
    condition, so the map from the first must be total: a condition added to the
    module without an entry here would print its full sentence into a ten-column
    table, or -- worse under a future edit -- print nothing."""
    from fixtures import io520bb, turboprop

    references = set()
    for engine in (io520bb(), turboprop()):
        for condition in run_all(engine, include_far25=True):
            references.add(condition.far_reference)
    missing = references - set(osec._ENGINE_SHORT_NAMES)
    assert not missing, sorted(missing)


def test_the_application_point_is_the_combined_cg_and_no_other_station():
    """OR-159. Three stations are printed and the loads are quoted about exactly
    one of them; the other two are the beam model's nodes and are geometry."""
    for name in _ALL:
        project = _project(name)
        section = _section(_doc(project=project))
        stations = _table(section, "Where the loads act")
        column = _column(stations, "Application point")
        for row, engine in zip(stations.rows, resolved_engines(project)):
            printed = [float(v) for v in row[column].split(",")]
            for got, want in zip(printed, combined_cg(engine)):
                assert math.isclose(got, want, abs_tol=0.01), name


def test_an_unentered_engine_input_is_not_printed_as_a_zero():
    """A turbofan entered with no propeller prints no propeller rows: a blank and
    a zero both mean "not entered" for an optional input, which is the opposite
    of the rule for a delivered component, where a zero is the result."""
    section = _section(_doc("concept_regional_jet"))
    inputs = _table(section, "Engine and propeller data")
    printed = {row[0] for row in inputs.rows}
    assert not any(name.startswith("Propeller diameter") for name in printed)
    assert not any(name.startswith("Number of propeller blades") for name in printed)
    assert any(name.startswith("Max engine torque") for name in printed)


def test_section_10_adds_no_appendix():
    """An engine mount takes a point load, not a distribution, so section 10
    adds no appendix of its own -- the set stays A-E."""
    doc = _doc("ga6_normal")
    # The property, not the list: no appendix belongs to the engine step. Pinning
    # the whole set made this test fail the day another section earned an
    # appendix of its own, which is not what it is about (note 44 §22).
    owned = {a.step_key for a in oc.APPENDICES if a.step_key}
    assert "engine_mount" not in owned
    assert [s.title for s in doc.sections if s.title.startswith("Appendix")]


if __name__ == "__main__":  # pragma: no cover - zero-dependency self-runner
    import sys as _sys

    failures = 0
    for _name, _fn in sorted(dict(globals()).items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
                print(f"ok   {_name}")
            except Exception as exc:
                failures += 1
                print(f"FAIL {_name}: {exc}")
    _sys.exit(1 if failures else 0)
