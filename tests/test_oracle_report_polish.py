"""The 2026-09-08 review's report-polish rollup (#240, R13-R23).

Ten presentation findings, each pinned where it still stood at 0.8.8. Three no
longer reproduced and are not pinned here: the empty continuation page of
R15, Figure 19's mass labels of R16 (the item figure carries no labels now) and
the lowercase sentence after a bold absence lead of R23.
"""

import functools
import os
import re

import pytest

import sloads.modules  # noqa: F401  (module registration)
from sloads import io, registry
from sloads.models.report import ReportSpec
from sloads.report import oracle_content as oc
from sloads.report import oracle_sections as osx
from sloads.report.content import PlotData, Series
from sloads.report.oracle_latex import render_oracle_document
from sloads.report.plots_tex import _label_anchors
from sloads.units import UnitSystem

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _project(name):
    return io.load_project(os.path.join(_ROOT, "examples", f"{name}.project.json"))


@functools.lru_cache(maxsize=None)
def _doc(name):
    return oc.build_oracle_document(_project(name), ReportSpec())


def _walk(sections):
    for section in sections:
        yield section
        yield from _walk(section.subsections)


def _tables(name):
    return [t for s in _walk(_doc(name).sections) for t in s.tables]


def _text(name):
    return "\n".join(p for s in _walk(_doc(name).sections) for p in s.body)


# R13 ----------------------------------------------------------------------- #
@pytest.mark.parametrize("name", ["ga6_normal", "baron_58"])
def test_the_document_states_every_moment_in_one_unit(name):
    """The engine mount was the document's one ft-lb channel."""
    columns = [c for t in _tables(name) for c in t.columns]
    assert not [c for c in columns if "ft-lb" in c], name
    assert any("Torque about thrust line (lb-in)" in c for c in columns)


# R14 ----------------------------------------------------------------------- #
def test_the_per_wheel_table_says_which_main_a_side_load_row_is():
    table = next(t for t in _tables("ga6_normal")
                 if t.title.startswith("Gear reactions per wheel"))
    assert "0.5 W on the wheel loaded inboard, the odd case" in table.note
    assert "the other wheel's is its partner's" in table.note


# R16 ----------------------------------------------------------------------- #
def test_close_markers_do_not_stack_their_labels():
    """Three landing loadings inside one label's width: before #240 two of the
    three labels took the same place above their markers."""
    data = PlotData("X", "Z", [Series("body", [-50.0, 350.0], [25.0, 180.0])],
                    points=[("fwd light", 72.6, 92.0),
                            ("fwd max landing", 76.0, 92.0),
                            ("aft max landing", 85.0, 92.0)], to_scale=True)
    placed = _label_anchors(data, [(s, list(zip(s.x, s.y))) for s in data.series])
    spots = {(anchor, round(lx, 6), round(ly, 6))
             for anchor, _label, _x, _y, lx, ly in placed}
    assert len(spots) == 3
    assert len({anchor for anchor, *_rest in placed}) > 1 or any(
        (lx, ly) != (x, y) for _a, _l, x, y, lx, ly in placed)


# R18 ----------------------------------------------------------------------- #
def test_the_engine_caption_describes_an_assumed_arrow_as_drawn():
    """The GA6's assumed arrow runs from the hub forward; the caption said it
    ran from the mount node to the hub, and named the wrong remedy."""
    figures = osx.engine_view_figures(
        _project("ga6_normal"), system=UnitSystem.IMPERIAL,
        results={"engine_mount": registry.get("engine")(_project("ga6_normal"))})
    caption = figures[0].caption
    assert "mount node to its propeller hub" not in caption
    assert "an ASSUMED one from the propeller hub forward" in caption
    assert "Enter the thrust line's two points to replace it." in caption


# R19 ----------------------------------------------------------------------- #
@pytest.mark.parametrize("name, ttail", [("ga6_normal", False), ("atr42_100", True)])
def test_the_tail_appendix_promises_no_row_it_does_not_print(name, ttail):
    text = _text(name)
    assert "followed by any discrete control-surface node" not in text
    assert "is part of that grid's row" in text
    assert ("transfer onto the fin" in text) is ttail


def test_appendix_b_says_where_a_control_surface_wing_id_is():
    text = _text("ga6_normal")
    assert "W-50 to W-59 are the aileron's conditions" in text
    assert "W-60 to W-69 the flap's" in text


# R20 ----------------------------------------------------------------------- #
def test_the_speed_of_sound_is_a_true_airspeed():
    project = _project("ga6_normal")
    result = registry.get("structural_speeds")(project)
    values = [v for c in result.conditions for v in c.values
              if v.key == "speed_of_sound"]
    assert values and {v.units for v in values} == {"kt(TAS)"}


# R21 ----------------------------------------------------------------------- #
def test_the_horizontal_tail_pitch_inertia_states_its_basis():
    table = next(t for t in _tables("ga6_normal")
                 if t.title == "Aerodynamic state of each condition"
                 and "SELECT's own estimate" in t.note)
    assert "uniform rod" in table.note and "0.44" in table.note


# R22 ----------------------------------------------------------------------- #
@pytest.mark.parametrize("name", ["ga6_normal", "atr42_100"])
def test_every_numbered_reference_the_document_cites_is_listed(name):
    tex = render_oracle_document(_doc(name))
    listed = set(re.findall(r"\\noindent (Reference \d+):", tex))
    cited = set(re.findall(r"Reference \d+", tex))
    assert listed, "no references list -- the guard would pass vacuously"
    assert cited <= listed, sorted(cited - listed)


# R23 ----------------------------------------------------------------------- #
def test_the_fuselage_curves_are_not_called_both():
    captions = [f.caption for s in _walk(_doc("ga6_normal").sections)
                for f in s.figures]
    assert not [c for c in captions if "Both curves" in c]
    assert any("Every curve returns to zero" in c for c in captions)


def test_appendix_a_states_its_split_and_the_split_is_nineteen_columns():
    state, loads = (t for t in _tables("ga6_normal")
                    if t.title.startswith("Balanced flight conditions"))
    assert len(set(state.columns) | set(loads.columns)) == 19
    assert "The matrix is one set of nineteen columns" in _text("ga6_normal")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
