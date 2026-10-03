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

import math
import functools
import os
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
# The weight data base, drawn (note 60 §1.1 figure 6, ported after #268)
# --------------------------------------------------------------------------- #
def test_the_item_figure_splits_the_data_base_by_when_it_is_aboard():
    """A mass at an extreme station reads differently depending on whether it is
    empty weight or a loading, so the kinds are separate series -- and they are
    told apart by marker **shape**, because §4.3 requires a printed figure to
    read in greyscale and three clouds of identical dots are one cloud."""
    from sloads.report.content import Units, item_station_plot_data

    project = io.load_project(os.path.join(_EXAMPLES, "ga6_normal.project.json"))
    data = item_station_plot_data(project, Units(UnitSystem.IMPERIAL))
    assert data is not None
    names = [s.name for s in data.series]
    assert names == ["Empty weight", "Minimum flight weight",
                     "Discretionary useful load"]
    marks = {s.style for s in data.series}
    assert len(marks) == len(data.series), f"two kinds share a marker: {marks}"
    for series in data.series:
        assert series.marker and series.labels
        assert len(series.labels) == len(series.x) == len(series.y)
    # Every row of the data base is drawn exactly once.
    drawn = sum(len(s.x) for s in data.series)
    assert drawn == len(project.weight.items)


def test_the_item_figure_is_entered_data_and_needs_no_results():
    """It is the weight data base, so it is pre-run by construction: a page that
    had to run its programs to draw what was typed into it would defeat the
    reason the pre-run tier exists (D-60.4)."""
    family = fx.stage_of("item_station")
    assert family is fx.Stage.PRE_RUN
    project = io.load_project(os.path.join(_EXAMPLES, "ga6_normal.project.json"))
    built = fx.build_step_figures("weight_mass", project,
                                  system=UnitSystem.IMPERIAL)
    keys = [figure.key for _family, figure in built]
    assert "item_station" in keys


def test_an_empty_data_base_says_so_rather_than_drawing_an_empty_axis():
    from sloads.models import Project
    from sloads.report import oracle_sections as osx
    from sloads.report.content import Units, item_station_plot_data

    assert item_station_plot_data(Project(name=""), Units(UnitSystem.IMPERIAL)) is None
    figures = osx.item_station_figures(Project(name=""),
                                       system=UnitSystem.IMPERIAL)
    assert figures[0].data is None and figures[0].absent_reason


def test_a_marker_shape_survives_both_renderers():
    """The producer states the shape once; neither renderer may drop it."""
    from sloads.report.content import Units, item_station_plot_data
    from sloads.report.plots_tex import plot_tex

    project = io.load_project(os.path.join(_EXAMPLES, "ga6_normal.project.json"))
    data = item_station_plot_data(project, Units(UnitSystem.IMPERIAL))
    symbols = [t.marker.symbol for t in plots.plot(data).data]
    assert len(set(symbols)) == len(data.series), symbols
    tex = plot_tex(data)
    assert "only marks" in tex
    for series in data.series:
        assert series.style in tex, series.style


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
