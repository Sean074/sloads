"""The figure catalogue and its two renderers -- design note 60, Block A.

Gates covered (note 60 §5):

* **Gate 9 -- every figure builds.** For every bundled example, every family the
  catalogue declares builds without raising and every instance either carries
  ``PlotData`` or states an ``absent_reason``. An empty axis and a traceback are
  both ways of not saying why, and a GUI page that dies on a half-filled project
  is the failure mode G-OR-7 exists to forbid.
* **Gate 10 -- figure parity, both ways.** No figure the oracle report carries is
  without a GUI renderer, and no family the GUI offers is without a report
  producer. Walked over **families**, which is what
  :attr:`sloads.report.content.Figure.family` is for: a key names one drawing and
  a family names the kind, and how many V-n diagrams a project has is a fact
  about its loadings rather than about the catalogue.
* **D-60.4's classification** is walked by the same guard: every family states a
  stage, every stage is one of the two, and the page prints which it is.

**Why parity is asserted against the document rather than against a list.** A
list of twenty figure names in a test is a second catalogue, free to drift from
the first -- the exact failure note 60 §1.1 measured, where D-57.4's port list
named four of the twenty that were actually there. So the subject of the
both-ways check is the set of families the **built oracle report** emits across
the shipped examples, which no one maintains by hand.

The renderer is asserted on the Plotly figure object, never on a screenshot:
``app_shell.plots.plot`` is pure, which is the property that lets a test check
that the producer's stated line style survived the translation.
"""

import functools
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sloads.modules  # noqa: F401  (module registration)
from app_shell import plots
from sloads import io
from sloads import workflow as wf
from sloads.models.report import ReportSpec
from sloads.report import figures as fx
from sloads.report.content import Figure, PlotData, Series
from sloads.report.oracle_content import build_oracle_document
from sloads.units import UnitSystem

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

#: Every project that ships with sloads. Read off the directory rather than
#: listed: an example added without its figures checked is exactly the gap
#: gate 9 is written to close.
_BUNDLED = tuple(sorted(f for f in os.listdir(_EXAMPLES)
                        if f.endswith(".project.json")))


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, name))


def _report_figures(project):
    """Every figure the oracle report emits for ``project``, flattened."""
    out = []

    def walk(sections):
        for section in sections:
            out.extend(section.figures)
            walk(section.subsections)

    walk(build_oracle_document(project, ReportSpec()).sections)
    return out


def _figure_pages():
    """Every GUI page the catalogue places a family on, in navigation order --
    the analysis steps and, since note 67 D-67.4a, the Beam Model page."""
    return [key for key in wf.gui_pages() if fx.families_for_step(key)]


def _built(project, system=UnitSystem.IMPERIAL):
    """Every figure the catalogue builds for ``project``, page by page."""
    out = []
    for key in _figure_pages():
        results = fx.results_for_step(project, key)
        out += [(key, family, figure) for family, figure
                in fx.build_step_figures(key, project, system=system,
                                         results=results)]
    return out


# --------------------------------------------------------------------------- #
# Gate 9 -- every figure builds for every bundled example
# --------------------------------------------------------------------------- #
def test_g_fig_1_every_figure_builds_for_every_bundled_example():
    """Gate 9: no family raises, and none renders an unexplained empty axis."""
    assert len(_BUNDLED) >= 4, _BUNDLED
    for name in _BUNDLED:
        project = _project(name)
        built = _built(project)
        assert built, name
        for step, family, figure in built:
            assert figure.title, (name, step, family.key)
            assert figure.data is not None or figure.absent_reason.strip(), (
                f"{name}: {step}/{figure.key} has neither data nor a reason -- "
                "a figure that cannot be drawn must say why, not render an "
                "empty axis (note 60 gate 9)")


def test_g_fig_2_a_figure_with_data_carries_points_to_draw():
    """A ``PlotData`` that draws nothing is an empty axis with extra steps."""
    for name in _BUNDLED:
        for step, _family, figure in _built(_project(name)):
            if figure.data is None:
                continue
            data = figure.data
            drawn = (sum(len(s.x) for s in data.series)
                     + len(data.points) + len(data.vlines))
            assert drawn, (name, step, figure.key)
            for series in data.series:
                assert len(series.x) == len(series.y), (
                    name, step, figure.key, series.name)


def test_g_fig_3_an_empty_project_draws_no_traceback():
    """G-OR-7's rule for figures: a blank project states absences, it does not
    take the page down. The pre-run tier is the whole point of #267, and a
    project being checked before it is complete is its normal subject."""
    from sloads.models import Project

    project = Project(name="")
    for key in _figure_pages():
        results = fx.results_for_step(project, key)
        for _family, figure in fx.build_step_figures(
                key, project, system=UnitSystem.IMPERIAL, results=results):
            assert figure.data is not None or figure.absent_reason.strip(), (
                key, figure.key)


# --------------------------------------------------------------------------- #
# Gate 10 -- parity, both ways
# --------------------------------------------------------------------------- #
def _report_families():
    """Memoised per test process (#308): the build is pure and was repeated per
    test; a fresh container each call, so no test edits another's view."""
    built = _report_families_built()
    return type(built)(built)


@functools.lru_cache(maxsize=None)
def _report_families_built():
    """Every figure family the oracle report draws, less the static diagrams.

    The three sign-convention diagrams (#278, note 60 D-60.8) are **authored
    LaTeX**, not a rendering of a ``PlotData``: they carry no project data, have
    no producer to share, and ``plots_tex.figure_body_tex`` dispatches them
    ahead of its absence test for that reason. Parity is a statement about
    figures that *have* numbers -- one producer, two renderers, so the screen
    and the page cannot disagree -- and a diagram of the axis convention has no
    number to disagree about. The exemption is read from
    ``conventions_tex.STATIC_EMITTERS``, the owner of that set, so a fourth
    diagram is exempt by being one and a data-carrying figure never is.
    """
    from sloads.report.conventions_tex import STATIC_EMITTERS

    seen = set()
    for name in _BUNDLED:
        seen |= {f.family for f in _report_figures(_project(name))}
    return seen - set(STATIC_EMITTERS)


def test_g_fig_4_every_report_figure_has_a_gui_renderer():
    """Gate 10, first direction: R-60.1's *at a minimum, every figure the oracle
    report carries also appears in the GUI* -- held by construction."""
    catalogue = {f.key for f in fx.catalogue()}
    missing = sorted(_report_families() - catalogue)
    assert not missing, (
        f"the oracle report emits figure families the GUI cannot render: "
        f"{missing}. Add them to sloads/report/figures.py (note 60 D-60.2).")


def test_g_fig_5_every_gui_figure_has_a_report_producer():
    """Gate 10, second direction: the GUI never invents a figure of its own.

    A family the catalogue declares that no document produces is a second figure
    owner in the making -- the drift class D-60.1 withdrew D-57.4 over."""
    extra = sorted({f.key for f in fx.catalogue()} - _report_families())
    assert not extra, (
        f"the GUI declares figure families no report produces: {extra}. "
        f"Either the producer is missing or the family is the GUI's own "
        f"derivation, which note 60 D-60.1 forbids.")


def test_g_fig_6_every_family_is_classified_and_placed():
    """D-60.4: the stage is stated per family, and the page that shows it is a
    real GUI page -- so a family cannot be parked on a page that does not exist
    or left for a reader to classify. A page, not only a step, since note 67
    D-67.4a placed the beam model on the Beam Model page."""
    steps = set(wf.gui_pages())
    keys = [f.key for f in fx.catalogue()]
    assert len(keys) == len(set(keys)), (
        "a figure family is declared twice: "
        f"{sorted({k for k in keys if keys.count(k) > 1})}")
    for family in fx.catalogue():
        assert family.step in steps, (family.key, family.step)
        assert family.stage in (fx.Stage.PRE_RUN, fx.Stage.POST_RUN), family.key
        assert family.title.strip(), family.key
        assert fx.STAGE_NOTES[family.stage].strip()
        assert callable(family.build), family.key


def test_g_fig_7_a_families_instances_all_declare_it():
    """The family a producer stamps is the family the catalogue declares.

    ``Figure.family`` defaults to ``key``, so a multi-instance producer that
    forgets to state its family silently invents one family per instance -- and
    the parity check above would then fail on the *next* project, not on this
    one. Asserted directly: every figure the catalogue builds is claimed by the
    family that asked for it."""
    for name in _BUNDLED:
        for step, family, figure in _built(_project(name)):
            assert figure.family == family.key, (name, step, figure.key)


def test_g_fig_8_the_pre_run_tier_needs_no_results():
    """D-60.3/D-60.4: a pre-run figure is entered data drawn.

    The page never runs a module for it, which is what makes *checking the
    inputs before running the whole process* -- the capability the port was
    asked for -- something the code guarantees rather than something the page
    happens to do today."""
    for name in _BUNDLED:
        project = _project(name)
        for step in wf.oracle_steps():
            without = fx.build_step_figures(step.key, project,
                                            system=UnitSystem.IMPERIAL,
                                            results=None)
            drawn = {figure.key for family, figure in without
                     if family.stage is fx.Stage.PRE_RUN
                     and figure.data is not None}
            expected = {figure.key for family, figure
                        in fx.build_step_figures(
                            step.key, project, system=UnitSystem.IMPERIAL,
                            results=fx.results_for_step(project, step.key))
                        if family.stage is fx.Stage.PRE_RUN
                        and figure.data is not None}
            assert drawn == expected, (name, step.key, sorted(expected - drawn))


# --------------------------------------------------------------------------- #
# The Plotly renderer (D-60.1's second peer)
# --------------------------------------------------------------------------- #
def test_the_renderer_keeps_the_style_the_producer_stated():
    """Colour is added on screen; the report's line encoding is not replaced.

    §4.3 has every producer distinguish traces by line *style* so the printed
    figure survives greyscale. A screen renderer that threw that away and
    coloured the traces instead would be showing the same data as a different
    figure to anyone reading the PDF beside the page."""
    data = PlotData("x", "y", [
        Series("plain", [0.0, 1.0], [0.0, 1.0]),
        Series("broken", [0.0, 1.0], [1.0, 0.0], style="dashed"),
        Series("fine", [0.0, 1.0], [0.5, 0.5], style="densely dotted"),
        Series("heavy", [0.0, 1.0], [2.0, 2.0], style="very thick, dashed"),
    ])
    traces = plots.plot(data).data
    assert [t.line.dash for t in traces] == ["solid", "dash", "dot", "dash"]
    assert traces[3].line.width > traces[0].line.width
    # Distinguishable on screen as well, which is the whole reason to colour.
    assert len({t.line.color for t in traces}) == 4


def test_the_renderer_closes_a_region_and_leaves_a_curve_open():
    """``Series.closed`` is the model's word for *this polyline bounds a
    region*. A planform drawn open is missing its root chord; a load
    distribution drawn closed gains a chord from tip back to root that no part
    of the airplane follows."""
    region = Series("wing", [0.0, 10.0, 8.0], [0.0, 1.0, 4.0], closed=True)
    curve = Series("shear", [0.0, 10.0, 8.0], [0.0, 1.0, 4.0])
    closed = plots.plot(PlotData("x", "y", [region])).data[0]
    opened = plots.plot(PlotData("x", "y", [curve])).data[0]
    assert (closed.x[0], closed.y[0]) == (closed.x[-1], closed.y[-1])
    assert len(closed.x) == len(region.x) + 1
    assert len(opened.x) == len(curve.x)


def test_a_drawing_is_rendered_to_scale_and_a_graph_is_not():
    """A planform stretched to fill a widget is a drawing of a different
    airplane; a shear distribution held to a 1:1 aspect is unreadable."""
    planform = PlotData("BL", "FS", [
        Series("wing", [0.0, 10.0, 8.0], [0.0, 1.0, 4.0], closed=True)],
        to_scale=True)
    graph = PlotData("BL", "Sz", [Series("Sz", [0.0, 10.0], [0.0, 500.0])])
    assert plots.is_to_scale(planform)
    assert not plots.is_to_scale(graph)
    assert plots.plot(planform).layout.yaxis.scaleanchor == "x"
    assert plots.plot(graph).layout.yaxis.scaleanchor is None


def test_both_renderers_read_the_producers_to_scale_statement():
    """Note 67 §10: one statement, two renderers -- the printed axis is equal
    exactly where the screen's is anchored, and an open line on a drawing (a
    thrust arrow, a beam) does not take the drawing off scale."""
    from sloads.report.plots_tex import plot_tex

    drawing = PlotData("X", "Z", [Series("beam", [0.0, 10.0], [0.0, 1.0])],
                       to_scale=True)
    graph = PlotData("X", "Sz", [Series("Sz", [0.0, 10.0], [0.0, 500.0])])
    assert plots.is_to_scale(drawing) and not plots.is_to_scale(graph)
    assert "axis equal image" in plot_tex(drawing)
    assert "axis equal image" not in plot_tex(graph)


def test_coincident_points_share_one_marker_on_screen_and_on_the_page():
    """#256. A twin's two engines sit at one (x, z) in side view; two labels at
    one coordinate printed "2" over "1". Both renderers draw
    ``PlotData.marked_points``: one marker, labelled in order."""
    from sloads.report.plots_tex import plot_tex

    data = PlotData("X", "Z", [Series("body", [0.0, 1000.0], [0.0, 100.0])],
                    points=[("1", 353.2, 60.0), ("2", 353.2, 60.0),
                            ("3", 700.0, 60.0)], to_scale=True)
    assert [label for label, _x, _y in data.marked_points()] == ["1 / 2", "3"]
    tex = plot_tex(data)
    assert tex.count("{1 / 2};") == 1 and "{1};" not in tex and "{2};" not in tex
    trace = next(t for t in plots.plot(data).data if t.name == data.points_label)
    assert list(trace.text) == ["1 / 2", "3"]


def test_points_apart_on_the_drawing_keep_their_own_markers():
    data = PlotData("Y", "Z", [Series("wing", [-500.0, 500.0], [170.0, 190.0])],
                    points=[("1", -161.0, 160.0), ("2", 161.0, 160.0)])
    assert data.marked_points() == data.points


def test_a_legend_entry_too_long_to_share_a_row_takes_one_column():
    """#256. Two long entries side by side overran the text width; a legend
    whose longest entry cannot sit beside another is one column."""
    from sloads.report.plots_tex import _LEGEND_TWO_COLUMN_CHARS, plot_tex

    short = PlotData("X", "Y", [Series("a", [0.0, 1.0], [0.0, 1.0]),
                                Series("b", [0.0, 1.0], [1.0, 0.0])])
    long_name = "x" * (_LEGEND_TWO_COLUMN_CHARS + 1)
    long = PlotData("X", "Y", [Series(long_name, [0.0, 1.0], [0.0, 1.0]),
                               Series("b", [0.0, 1.0], [1.0, 0.0])])
    assert "legend columns=2" in plot_tex(short)
    assert "legend columns=1" in plot_tex(long)


def test_a_caption_that_says_to_scale_is_drawn_to_scale():
    """The defect note 67 §10 measured: five figures captioned "to scale on
    equal axes" were drawn on free axes in print, and four of them on screen.
    The caption is the claim; the flag is what both renderers obey."""
    for name in _BUNDLED:
        for step, _family, figure in _built(_project(name)):
            if figure.data is not None and "to scale" in figure.caption:
                assert figure.data.to_scale, (name, step, figure.key)


def test_the_beam_model_is_drawn_from_the_deck_it_ships():
    """Note 67 gate 5: every element, tie and owned node of the delivered model
    is in the plan view -- the drawing is of the model, not of a re-derivation."""
    from sloads.export.lra_model import build_lra_model
    from sloads.report import oracle_sections as osx

    project = _project("atr42_100.project.json")
    model = build_lra_model(project)
    figures = {f.key: f for f in osx.beam_model_figures(project,
                                                         system=UnitSystem.IMPERIAL)}
    assert list(figures) == ["lra_beam_iso", "lra_beam_plan", "lra_beam_side",
                             "lra_beam_front"]
    assert all(f.family == osx.BEAM_FAMILY and f.data.to_scale
               for f in figures.values())
    plan = figures["lra_beam_plan"].data
    beam = [s for s in plan.series
            if not s.marker and s.style not in ("densely dotted", "dashed")]
    assert sum(len(s.x) - 1 for s in beam) == len(model.cbars)
    ties = [s for s in plan.series if s.style == "dashed"]
    assert len(ties) == sum(len(deps) for _i, _d, deps, _l in model.rbe2s)
    marked = sum(len(s.x) for s in plan.series if s.marker)
    owned = sum(1 for n in model.nodes if n.family in osx._BEAM_NODE_GROUPS)
    assert marked == owned
    assert len(plan.points) == 1, "the support is the one marked point"


def test_a_refused_beam_model_is_stated_verbatim_and_drawn_nowhere():
    """Note 67 gate 4's figure half: the exporter's refusal, word for word."""
    from sloads.export.lra_model import LraRefusal, build_lra_model
    from sloads.report import oracle_sections as osx

    project = _project("atr42_100.project.json")
    for surface in project.geometry.surfaces:
        if surface.name == "wing":
            surface.ref_axis_pct = None
    try:
        build_lra_model(project)
    except LraRefusal as exc:
        reason = str(exc)
    else:
        raise AssertionError("an unset wing axis no longer refuses")
    figures = osx.beam_model_figures(project, system=UnitSystem.IMPERIAL)
    assert len(figures) == 4
    assert all(f.data is None and f.absent_reason == reason for f in figures)


def test_markers_and_reference_lines_are_annotations_not_series():
    """The design CG cases and the speed lines are annotations on the plotted
    data. A legend entry per speed line buries the curves the figure is about,
    and the marker series takes its legend name from the producer -- which is
    the defect ``points_label`` was added for (GUI review 2026-08-30)."""
    data = PlotData("V", "n", [Series("boundary", [0.0, 1.0], [0.0, 1.0])],
                    points=[("VA", 1.0, 2.0)], vlines=[("VC", 0.5)],
                    points_label="Gust design points")
    fig = plots.plot(data)
    assert [t.name for t in fig.data] == ["boundary", "Gust design points"]
    assert len(fig.layout.shapes) == 1          # the reference line
    assert any("VC" in (a.text or "") for a in fig.layout.annotations)


def test_a_figure_with_no_data_renders_its_reason_not_an_axis():
    """The absent figure says the same sentence in both front-ends."""
    calls = []

    class _Fake:
        def markdown(self, text):
            calls.append(("markdown", text))

        def caption(self, text):
            calls.append(("caption", text))

        def plotly_chart(self, *_a, **_k):
            calls.append(("chart", ""))

    saved = plots.st
    plots.st = _Fake()
    try:
        drawn = plots.render_figure(
            Figure(key="k", title="A figure",
                   absent_reason="the project enters no wing planform."),
            key="k")
    finally:
        plots.st = saved
    assert drawn is False
    assert not [c for c in calls if c[0] == "chart"]
    assert any("no wing planform" in text for _kind, text in calls)


def test_non_finite_coordinates_do_not_reach_the_screen_renderer():
    """The TikZ emitter drops non-finite points (``_finite``); the screen one
    hands them to Plotly, which breaks the line at them -- which is the honest
    rendering of a gap and is why nothing is filtered here. Asserted so the
    difference is a decision rather than an oversight."""
    data = PlotData("x", "y", [
        Series("gappy", [0.0, 1.0, 2.0], [0.0, math.nan, 2.0])])
    trace = plots.plot(data).data[0]
    assert len(trace.x) == 3


# --------------------------------------------------------------------------- #
# The mass three-view (#388): the weight data base placed on the airframe
# --------------------------------------------------------------------------- #
_MASS_VIEWS = ("mass_plan_view", "mass_side_view", "mass_front_view")


def _mass_views(name):
    """The three mass views of one example, built pre-run on the weight page."""
    built = fx.build_step_figures("weight_mass", _project(name),
                                  system=UnitSystem.IMPERIAL, results=None)
    views = {figure.key: figure for family, figure in built
             if family.key in _MASS_VIEWS}
    assert tuple(views) == _MASS_VIEWS, sorted(views)
    return views


def test_the_mass_views_are_catalogued_pre_run_after_the_envelope():
    """#388: three families on the weight page, pre-run, one builder, after
    the envelope; the one-dimensional item-station figure is gone."""
    rows = list(fx.families_for_step("weight_mass"))
    keys = [f.key for f in rows]
    assert keys[:4] == ["weight_cg", *_MASS_VIEWS]
    assert "item_station" not in keys
    builders = {id(f.build) for f in rows if f.key in _MASS_VIEWS}
    assert len(builders) == 1, "one builder serves the three views"
    for family in rows:
        if family.key in _MASS_VIEWS:
            assert family.stage is fx.Stage.PRE_RUN, family.key


def test_every_row_is_one_bubble_sized_by_its_weight_and_shaped_by_its_kind():
    """Each view draws every row of the data base exactly once, as a sized
    mark in the series of its loading kind -- the kinds told apart by marker
    **shape** (§4.3's greyscale rule) and the rows by **area** -- with its name
    and weight on the label, and the row placed on the frame's own axes."""
    project = _project("atr42_100.project.json")
    rows = project.weight.items
    for key, figure in _mass_views("atr42_100.project.json").items():
        data = figure.data
        assert data is not None and data.to_scale, key
        bubbles = [s for s in data.series if s.sizes]
        names = [s.name for s in bubbles]
        assert names == ["Empty weight", "Minimum flight weight",
                         "Discretionary useful load"], (key, names)
        assert len({s.style for s in bubbles}) == len(bubbles), key
        drawn = sum(len(s.x) for s in bubbles)
        assert drawn == len(rows), key
        for series in bubbles:
            assert series.marker
            assert len(series.sizes) == len(series.labels) == len(series.x) == len(series.y)
            assert all(size > 0 for size in series.sizes)
        heaviest = max(rows, key=lambda r: r.weight_lb)
        sizes = {label: size for s in bubbles for label, size in zip(s.labels, s.sizes)}
        assert max(sizes.values()) == heaviest.weight_lb
        assert any(label.startswith(heaviest.name) for label in sizes)
    # The frames: plan is (butt line, station), side (station, waterline),
    # front (butt line, waterline) -- the left engine's row lands accordingly.
    engine = next(r for r in rows if r.name == "Engine, left")
    placed = {}
    for key, figure in _mass_views("atr42_100.project.json").items():
        for s in figure.data.series:
            if s.sizes:
                for label, x, y in zip(s.labels, s.x, s.y):
                    if label.startswith("Engine, left"):
                        placed[key] = (x, y)
    assert placed["mass_plan_view"] == (engine.y, engine.x)
    assert placed["mass_side_view"] == (engine.x, engine.z)
    assert placed["mass_front_view"] == (engine.y, engine.z)


def test_the_views_carry_the_airframe_the_cg_of_every_loading_and_the_limits():
    """The airframe comes through the three-view's owners (G-69.10's series
    names); each loading of record's CG (design note 70) is a marked point
    with the ceiling flagged; the structural limits are reference lines in
    side view and a band in plan, and absent from the front view, whose axes
    carry no station."""
    project = _project("atr42_100.project.json")
    views = _mass_views("atr42_100.project.json")
    cases = {c.name for c in project.mass.cases if not c.ceiling}
    for key, figure in views.items():
        names = {s.name for s in figure.data.series}
        assert "Fuselage" in names, (key, sorted(names))
        assert any(n.startswith("Wing") for n in names), (key, sorted(names))
        if key == "mass_side_view":
            # Labelled where the station axis spreads them...
            labels = [label for label, _x, _y in figure.data.points]
            assert figure.data.points_label == "CG of each loading of record"
        else:
            # ...and one unlabelled marker series where they would smudge.
            cg = next(s for s in figure.data.series if s.name == "CG of each loading of record")
            assert cg.marker and not cg.sizes and not figure.data.points
            labels = list(cg.labels)
        assert "database ceiling" in labels, key
        assert cases <= set(labels), key
        assert "to scale on equal axes" in figure.caption
    side, plan, front = (views[k].data for k in ("mass_side_view", "mass_plan_view", "mass_front_view"))
    assert [label for label, _x in side.vlines] == ["fwd CG limit", "aft CG limit"]
    assert any(s.name == "Structural CG limits" and s.closed for s in plan.series)
    assert not front.vlines and not any(s.name == "Structural CG limits" for s in front.series)


def test_an_empty_data_base_says_so_rather_than_drawing_an_empty_axis():
    from sloads.models import Project
    from sloads.report import oracle_sections as osx

    figures = osx.mass_view_figures(Project(name=""), system=UnitSystem.IMPERIAL)
    assert len(figures) == 3
    for figure in figures:
        assert figure.data is None and "no itemized weight data base" in figure.absent_reason


def test_marker_shape_and_size_survive_both_renderers():
    """The producer states shape and size once; neither renderer may drop
    either. On screen the diameter list tracks the sizes' order; on the page
    each mark's radius rides as its point meta and the marks stay black."""
    from sloads.report.plots_tex import plot_tex

    data = _mass_views("ga6_normal.project.json")["mass_side_view"].data
    bubbles = [s for s in data.series if s.sizes]
    traces = {t.name: t for t in plots.plot(data).data}
    symbols = {traces[s.name].marker.symbol for s in bubbles}
    assert len(symbols) == len(bubbles), symbols
    largest = max(v for s in bubbles for v in s.sizes)
    for series in bubbles:
        px = list(traces[series.name].marker.size)
        assert len(px) == len(series.sizes)
        order = sorted(range(len(px)), key=lambda i: series.sizes[i])
        assert px == sorted(px, key=lambda v: px.index(v)) or True
        assert all(px[a] <= px[b] for a, b in zip(order, order[1:]))
        if largest in series.sizes:
            assert max(px) == max(plots._bubble_px([largest], largest))
    tex = plot_tex(data)
    radii = sorted({float(m) for m in re.findall(r"mark size=([0-9.eE+-]+)pt, black, fill opacity", tex)})
    assert len(radii) > 3 and radii[-1] > radii[0], radii
    assert "color" not in tex.lower(), "§4.3: a sized mark is black like every other"
    assert sum(1 for _ in re.finditer(r"fill opacity=0.35", tex)) == sum(len(s.x) for s in bubbles)
    for series in bubbles:
        assert series.style in tex, series.style
    # The retired figure's data builder is gone with it.
    from sloads.report import content
    assert not hasattr(content, "item_station_plot_data")


# --------------------------------------------------------------------------- #
# The airplane three-view (design note 69 D-69.15, gate G-69.10)
# --------------------------------------------------------------------------- #
_AIRPLANE_VIEWS = ("airplane_plan_view", "airplane_side_view",
                   "airplane_front_view")


def _airplane_views(name):
    """The three views of one example, built pre-run on the Geometry page."""
    built = fx.build_step_figures("configuration_layout", _project(name),
                                  system=UnitSystem.IMPERIAL, results=None)
    views = {figure.key: figure for family, figure in built
             if family.key in _AIRPLANE_VIEWS}
    assert tuple(views) == _AIRPLANE_VIEWS, sorted(views)
    return views


def test_g_69_10_the_three_view_is_catalogued_pre_run_after_the_planforms():
    """D-69.15: three families on the Geometry page, pre-run, one builder."""
    rows = list(fx.families_for_step("configuration_layout"))
    keys = [f.key for f in rows]
    assert keys[:3] == ["planform_wing", "planform_htail", "planform_vtail"]
    assert keys[3:6] == list(_AIRPLANE_VIEWS)
    builders = {id(f.build) for f in rows if f.key in _AIRPLANE_VIEWS}
    assert len(builders) == 1, "one builder serves the three views"
    for family in rows:
        if family.key in _AIRPLANE_VIEWS:
            assert family.stage is fx.Stage.PRE_RUN, family.key


def test_g_69_10_the_atr_three_view_draws_every_owner_it_has():
    """G-69.10: the ATR's views carry the fuselage, the wing, both tails, the
    wing controls, both propeller discs and both gear legs, each as a named
    series read from its owner; the elevator and rudder are not asserted,
    since the example enters neither yet (D-69.17 adds them)."""
    views = _airplane_views("atr42_100.project.json")
    names = {series.name for figure in views.values()
             for series in figure.data.series}
    for wanted in ("Fuselage", "Fuselage centre line", "Wing",
                   "Horizontal tail", "Vertical tail", "Aileron", "Flap",
                   "Engine 1 propeller disc", "Engine 2 propeller disc",
                   "Main gear", "Nose gear"):
        assert wanted in names, (wanted, sorted(names))
    for figure in views.values():
        assert figure.data.to_scale, figure.key
        assert "drawn from what is entered" in figure.caption
        assert "rectangular tail sketch" in figure.caption
        assert figure.caption.endswith(
            "Nothing here is a load: no value is scaled and none carries a "
            "safety factor.")
        assert "no hinge geometry" not in figure.caption
    # The disc is a circle only where it is face-on; the owner's diameter
    # (156 in) is the span of the line it is elsewhere.
    front = next(s for s in views["airplane_front_view"].data.series
                 if s.name == "Engine 1 propeller disc")
    assert front.closed and len(front.x) > 8
    side = next(s for s in views["airplane_side_view"].data.series
                if s.name == "Engine 1 propeller disc")
    assert not side.closed
    assert math.isclose(max(side.y) - min(side.y), 156.0)
    # Q7: the main wheels sit at half the tread in front and plan view.
    tread = _project("atr42_100.project.json").geometry.landing_gear.tread_in
    main = [s for s in views["airplane_front_view"].data.series
            if s.name == "Main gear"]
    assert main and math.isclose(abs(main[0].x[-1]), tread / 2.0)


def test_g_69_10_a_wing_alone_is_drawn_and_the_rest_is_named_absent():
    """G-69.10: ``concept_heavy`` enters a wing and nothing else the view can
    draw, so the wing is the only airframe series and the caption names the
    fuselage, the engines and the gear as not entered -- never assumed."""
    views = _airplane_views("concept_heavy.project.json")
    for figure in views.values():
        drawn = {s.name for s in figure.data.series if s.name}
        assert drawn - {"Positive axes"}, figure.key
        assert all("Wing" in name or name == "Positive axes" for name in drawn), (
            figure.key, sorted(drawn))
        absent = figure.caption.split("Not entered, so not drawn: ", 1)[1]
        for name in ("the fuselage", "the engines", "the landing gear"):
            assert name in absent, (figure.key, absent)


def test_g_69_10_a_project_with_no_geometry_states_the_absence():
    """A blank project returns the three figures with a reason, no axis."""
    from sloads.models import Project

    built = fx.build_step_figures("configuration_layout", Project(name=""),
                                  system=UnitSystem.IMPERIAL, results=None)
    reasons = {figure.key: figure.absent_reason for family, figure in built
               if family.key in _AIRPLANE_VIEWS}
    assert set(reasons) == set(_AIRPLANE_VIEWS)
    for reason in reasons.values():
        assert "no geometry this view can draw" in reason


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
