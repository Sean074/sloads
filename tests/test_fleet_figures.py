"""The fleet comparison's gates (#268, design note 57 D-57.5).

Three properties, and they are the three the port could have lost:

1. **The figures exist for every bundled example**, with data or a stated
   reason -- the same bar gate 9 (``tests/test_figures.py``) holds the step
   catalogue to, applied to the one figure set that sits outside it.
2. **Nothing is derived twice.** The subject's priority chain, the reference
   CSV and the six ``PlotData`` builds each have exactly one owner in the tree,
   and both front-ends call it. D-57.5 said the chain would be *rewritten, not
   imported*; note 60 D-60.1 withdrew that rule for figures on the ground that
   a second derivation is a second owner, and the chain is the same class of
   thing -- it has a defect history of its own (the MTOW source, corrected
   2026-08-15), and a rewrite would have been a rewrite of that fix.
3. **The scatter survives the model.** ``Series.marker``, ``Series.labels`` and
   ``PlotData.log_x``/``log_y`` were added for this figure set; a renderer that
   ignored one of them would draw a polyline through thirty airplanes, or put a
   fleet spanning a factor of thirty in weight on a linear axis.
"""

import ast
import os

import pytest

from app_shell.plots import plot
from sloads import io
from sloads.fleet import FleetPoint, Subject, reference_fleet, subject_from_project
from sloads.models import Project
from sloads.report.fleet_figures import FLEET_SERIES, SUBJECT_SERIES, fleet_figures

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = os.path.join(_ROOT, "examples")

#: Read off the directory rather than listed, so a new bundled example is
#: covered the day it lands rather than the day someone remembers this file.
_BUNDLED = sorted(os.path.join(_EXAMPLES, n) for n in os.listdir(_EXAMPLES)
                  if n.endswith(".project.json"))

#: Every figure the page shows, in the order the producer returns them.
_KEYS = [f.key for f in fleet_figures(None, [])]


def _fleet():
    return reference_fleet()


# --------------------------------------------------------------------------- #
# The data
# --------------------------------------------------------------------------- #
def test_the_bundled_reference_fleet_loads():
    """The CSV moved into the package at #268; a path that no longer resolves
    would show as an empty fleet rather than an error, so it is asserted."""
    fleet = _fleet()
    assert len(fleet) > 20, "the bundled reference fleet is missing or truncated"
    assert all(isinstance(p, FleetPoint) and p.name and p.mtow_lb > 0
               for p in fleet)


@pytest.mark.parametrize("path", _BUNDLED)
def test_every_bundled_example_places_against_the_fleet(path):
    """Each shipped project resolves a subject and draws all six figures.

    The bundled examples carry ``geometry.surfaces`` rather than a parametric
    layout, so this is also the guard on the surface fallback (M2-5): a chain
    that lost it would still produce a subject, with no wing area in it.
    """
    subject = subject_from_project(io.load_project(path))
    assert subject is not None, f"{os.path.basename(path)}: no subject"
    assert subject.mtow_lb > 0
    assert subject.w_s, "the surface fallback no longer fills the wing area"

    figures = fleet_figures(subject, _fleet())
    assert [f.key for f in figures] == _KEYS
    for figure in figures:
        assert figure.data is not None or figure.absent_reason, figure.key
        if figure.data is None:
            continue
        names = [s.name for s in figure.data.series]
        assert names == [FLEET_SERIES, SUBJECT_SERIES], figure.key
        assert len(figure.data.series[1].x) == 1, "one airplane, one point"


def test_an_empty_project_draws_the_fleet_and_says_why_it_is_not_on_it():
    """A project with no design weight has no point to plot. The fleet is still
    worth seeing -- the comparators exist before the airplane does -- so the
    figures are returned with the subject series absent, not the figures."""
    assert subject_from_project(Project(name="")) is None
    figures = fleet_figures(None, _fleet())
    assert [f.key for f in figures] == _KEYS
    for figure in figures:
        assert figure.data is not None, figure.key
        assert [s.name for s in figure.data.series] == [FLEET_SERIES]


def test_a_point_missing_one_coordinate_leaves_only_that_figure():
    """An aircraft with no published aspect ratio is absent from the aspect
    ratio scatter and present in every other one -- which is why each axis is
    asked for its own value rather than the fleet filtered once up front."""
    partial = FleetPoint(name="No AR", mtow_lb=3000, oew_lb=1800, max_hp=200,
                         wing_area_ft2=0, seats=4)
    figures = {f.key: f for f in fleet_figures(None, [partial])}
    assert figures["fleet_mtow_vs_empty"].data is not None
    assert figures["fleet_wing_vs_power"].data is None
    assert figures["fleet_wing_vs_power"].absent_reason


def test_the_whole_fleet_has_no_subject_of_its_own():
    """``fleet_figures`` never invents the airplane: with a fleet and no
    subject, no series is named for one."""
    for figure in fleet_figures(None, _fleet()):
        assert SUBJECT_SERIES not in [s.name for s in (figure.data.series
                                                       if figure.data else [])]


# --------------------------------------------------------------------------- #
# One owner (note 60 D-60.1, applied to D-57.5)
# --------------------------------------------------------------------------- #
_PAGES = ("oracle_app/fleet.py", "app/views/aircraft_comparison.py")


def _source(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def test_the_reference_csv_has_exactly_one_reader():
    """The SSOT row this step adds to ``CONVENTIONS.md`` §7, guarded.

    The file used to be read by the page that displayed it, which is how it came
    to live inside ``app/`` -- a front-end owning data the calc package needs.
    One reader, in ``sloads/fleet.py``; everything else asks it.
    """
    offenders = []
    for tree in ("sloads", "app", "app_shell", "oracle_app"):
        for root, _dirs, names in os.walk(os.path.join(_ROOT, tree)):
            if "__pycache__" in root:
                continue
            for name in sorted(n for n in names if n.endswith(".py")):
                path = os.path.join(root, name)
                rel = os.path.relpath(path, _ROOT)
                if "reference_aircraft" in _source(rel) and rel != os.path.join("sloads", "fleet.py"):
                    offenders.append(rel)
    assert not offenders, (
        "the bundled reference fleet is named outside its owner "
        f"(sloads/fleet.py): {offenders}. Call sloads.fleet.reference_fleet().")


@pytest.mark.parametrize("rel", _PAGES)
def test_neither_page_derives_the_subject_or_the_figures(rel):
    """Both front-ends carry this page until ``app/views/`` retires, and they
    carry the same one: each calls the owners and defines no chain of its own."""
    body = _source(rel)
    for call in ("subject_from_project", "reference_fleet", "fleet_figures"):
        assert call in body, f"{rel} does not call {call}()"
    # ``render_fleet_page`` is the page itself -- the oracle GUI navigates
    # callables, not view files (note 32, OG-D) -- so the one function that is
    # the page is not a derivation. Anything else here would be.
    defined = {n.name for n in ast.walk(ast.parse(body))
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               } - {"render_fleet_page"}
    assert not defined, (
        f"{rel} defines functions of its own ({sorted(defined)}); the readout, "
        "the figures and the fleet table are rendered by app_shell.fleet_view "
        "so the two pages cannot disagree while both exist")


# --------------------------------------------------------------------------- #
# The renderer honours what the producer stated
# --------------------------------------------------------------------------- #
def _first(subject=None):
    return fleet_figures(subject, _fleet())[0].data


def test_a_scatter_is_drawn_as_points_and_never_as_a_line():
    """The defect ``Series.marker`` exists to prevent: a polyline through
    unrelated airplanes, in the order the CSV happens to list them."""
    fig = plot(_first())
    assert fig.data, "nothing was drawn"
    for trace in fig.data:
        assert trace.mode == "markers", trace.name


def test_each_point_carries_the_aircraft_it_is():
    """``Series.labels`` reaches the hover, which is the question a scatter
    provokes -- which one is that?"""
    fleet = _fleet()
    trace = plot(_first())["data"][0]
    assert list(trace.text) and len(trace.text) <= len(fleet)
    assert set(trace.text) <= {p.name for p in fleet}
    assert "%{text}" in trace.hovertemplate


def test_the_weight_axes_are_logarithmic_on_both_renderers():
    """A fleet spanning a factor of thirty in weight has its whole
    general-aviation half in the first inch of a linear axis. The producer
    states the scale, so the printed figure and the screen figure agree."""
    from sloads.report.plots_tex import plot_tex

    data = {f.key: f.data for f in fleet_figures(None, _fleet())}
    assert data["fleet_mtow_vs_empty"].log_x and data["fleet_mtow_vs_empty"].log_y
    assert not data["fleet_wing_vs_power"].log_x

    fig = plot(data["fleet_mtow_vs_empty"])
    assert fig.layout.xaxis.type == "log" and fig.layout.yaxis.type == "log"
    assert plot(data["fleet_wing_vs_power"]).layout.xaxis.type != "log"

    tex = plot_tex(data["fleet_mtow_vs_empty"])
    assert "xmode=log" in tex and "ymode=log" in tex
    assert "only marks" in tex
    assert "xmode=log" not in plot_tex(data["fleet_wing_vs_power"])


def test_the_subject_is_a_second_series_and_not_a_design_point():
    """The airplane is one of the plotted quantities, not an annotation on
    them: it takes a legend entry and a colour of its own, which is what makes
    it findable in the cloud."""
    subject = Subject(name="Concept", mtow_lb=4000, oew_lb=2400,
                      wing_area_ft2=180, power_hp=300)
    data = _first(subject)
    assert not data.points, "the subject must not be a points annotation"
    traces = plot(data).data
    assert [t.name for t in traces] == [FLEET_SERIES, SUBJECT_SERIES]
    assert traces[0].marker.color != traces[1].marker.color


# --------------------------------------------------------------------------- #
# The page, headless
# --------------------------------------------------------------------------- #
def _page(project=None):
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string(
        "from oracle_app.fleet import render_fleet_page\nrender_fleet_page()\n",
        default_timeout=60)
    at.session_state["project"] = project or io.load_project(
        os.path.join(_EXAMPLES, "ga6_normal.project.json"))
    at.run()
    return at


def test_the_page_renders_the_readout_and_every_figure():
    at = _page()
    assert not at.exception, [e.message for e in at.exception]
    assert len(at.tabs) >= len(_KEYS)
    assert [m.label for m in at.metric] == ["Wing loading W/S (lb/ft²)",
                                            "Power loading W/P (lb/hp)"]


def test_the_page_opens_on_a_project_with_nothing_in_it():
    """Reachable before any input exists: the fleet is worth seeing first."""
    at = _page(project=Project())
    assert not at.exception, [e.message for e in at.exception]
    assert any("design weight" in i.value for i in at.info)


def test_the_page_states_that_it_is_an_extension_and_not_a_program():
    """#266's convention: capability the original suite never had says so where
    it appears. The fleet comparison is the whole page, so the page says it."""
    from oracle_app.form import EXTENSION_MARK

    at = _page()
    assert EXTENSION_MARK in [t.value for t in at.title][0]
    assert any(EXTENSION_MARK in c.value for c in at.caption)


if __name__ == "__main__":  # zero-dependency self-runner
    import sys

    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
