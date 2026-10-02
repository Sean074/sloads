"""#244: a count a stray keystroke can blow up -- design note 67 D-67.12, gate 9.

One mistyped digit committed 4,501 weight items in the 2026-09-08 GUI review,
and the spinner then showed 1 while the state held 4,501. Three guards, one
owner (``app_shell.components.count_input``), on every row counter and on the
LRA mesh counts the Beam Model page renders:

* a value above the cap never commits;
* an increase of more than ``COUNT_CONFIRM_JUMP`` waits for a named click;
* the widget re-seeds when the model's count changes underneath it.

And the exporter refuses a mesh count a project file carries past the range,
naming the field, since a file is the one route the widget does not guard.
"""

from __future__ import annotations

import os
import sys

import pytest
from streamlit.testing.v1 import AppTest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import field_registry as fr
from sloads import io as sloads_io
from sloads.export.lra_model import LraRefusal, build_lra_model
from sloads.models import LraMeshInput, MassItem
from sloads.models.inputs import LRA_GRID_BOUNDS

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _project(name: str):
    return sloads_io.load_project(os.path.join(_ROOT, "examples", f"{name}.project.json"))


_STEP = '''
from oracle_app.form import render_step
render_step("weight_mass")
'''

_BEAM = '''
from oracle_app.beam_model import render_beam_model_page
render_beam_model_page()
'''


def _run(script: str, project) -> AppTest:
    at = AppTest.from_string(script, default_timeout=120)
    at.session_state["project"] = project
    at.run()
    assert not at.exception, [e.message for e in at.exception]
    return at


def _widget(at: AppTest, label: str):
    return next(n for n in at.number_input if n.label == label)


def _with_mesh(at: AppTest) -> AppTest:
    """The mesh is an Optional record, added by name (#143) before it has widgets."""
    next(b for b in at.button if b.label.endswith("Add LRA Mesh")).click().run()
    assert not at.exception, [e.message for e in at.exception]
    return at


def _wing(at: AppTest):
    return next(n for n in at.number_input if "wing grids" in n.label.lower())


def test_the_row_counter_is_capped():
    at = _run(_STEP, _project("ga6_normal"))
    assert _widget(at, "Items — rows").max == fr.ROW_COUNT_CAP


def test_a_large_jump_in_rows_waits_for_the_named_click():
    project = _project("ga6_normal")
    at = _run(_STEP, project)
    _widget(at, "Items — rows").set_value(24 + 50).run()
    assert len(at.session_state["project"].weight.items) == 24, (
        "a jump of 50 committed without confirmation")
    confirm = next(b for b in at.button if b.label == "Set Items rows to 74")
    confirm.click().run()
    assert not at.exception, [e.message for e in at.exception]
    assert len(at.session_state["project"].weight.items) == 74


def test_a_small_step_commits_as_before():
    at = _run(_STEP, _project("ga6_normal"))
    _widget(at, "Items — rows").set_value(26).run()
    assert len(at.session_state["project"].weight.items) == 26


def test_the_counter_re_seeds_when_the_model_moves_underneath_it():
    """The spinner said 1 while the state held 4,501: never again."""
    at = _run(_STEP, _project("ga6_normal"))
    items = at.session_state["project"].weight.items
    items.extend(MassItem(name=f"added {i}", weight_lb=1.0) for i in range(5))
    at.run()
    assert _widget(at, "Items — rows").value == 29


def test_a_mesh_count_is_bounded_by_the_exporters_own_range():
    at = _with_mesh(_run(_BEAM, _project("atr42_100")))
    floor, cap = LRA_GRID_BOUNDS
    for path, rule in fr.COUNT_RULES.items():
        assert (rule.floor, rule.cap) == (floor, cap), path
    wing = _wing(at)
    assert (wing.min, wing.max) == (floor, cap)


def test_a_large_mesh_jump_from_blank_waits_for_the_named_click():
    """Blank means the default (20 on the wing), and the jump is measured from it."""
    at = _with_mesh(_run(_BEAM, _project("atr42_100")))
    _wing(at).set_value(150).run()
    mesh = at.session_state["project"].lra_mesh
    assert mesh is None or mesh.wing_grids is None
    next(b for b in at.button if b.label.startswith("Set ") and "150" in b.label).click().run()
    assert not at.exception, [e.message for e in at.exception]
    assert at.session_state["project"].lra_mesh.wing_grids == 150


@pytest.mark.parametrize("count", [1, 4501])
def test_the_exporter_refuses_a_file_count_outside_the_range_by_name(count):
    project = _project("atr42_100")
    project.lra_mesh = LraMeshInput(wing_grids=count)
    with pytest.raises(LraRefusal, match="lra_mesh.wing_grids"):
        build_lra_model(project)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
