"""The Project JSON Editor renders the project it is given -- at every generation.

The 0.8.4 closure review found the editor empty after the first project load,
with Apply reporting *Invalid JSON: Expecting value: line 1 column 1*. The page
stamped its text key at import time (``widget_key`` evaluated once per process,
at generation 0) and re-stamped it per render, so after ``adopt()`` bumped the
generation the seed was written to ``g0::_project_editor_text`` while the widget
read ``g1::g0::_project_editor_text`` -- and Reload wrote the same dead key. No
test rendered the editor at all, which is how a page that is the declared escape
hatch for ``JSON_ONLY_RECORDS`` (note 57 D-57.3) shipped unusable.

These tests drive the page body under ``AppTest`` at generation 0 and at a bumped
generation, and round-trip an edit through Apply.
"""

import json
import logging
import os
import sys

import pytest

logging.disable(logging.CRITICAL)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from sloads import io as sloads_io  # noqa: E402

_SCRIPT = ("from app_shell.project_editor import render_project_editor\n"
           "render_project_editor()\n")


def _project():
    return sloads_io.load_project(os.path.join(_ROOT, "examples", "ga6_normal.project.json"))


def _editor(generation):
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string(_SCRIPT, default_timeout=120)
    at.session_state["project"] = _project()
    if generation:
        at.session_state["_project_generation"] = generation
    at.run()
    assert not at.exception, [e.message for e in at.exception]
    return at


@pytest.mark.parametrize("generation", [0, 1, 3])
def test_the_editor_shows_the_project_at_every_generation(generation):
    """The text area holds the project's JSON whether or not a load has happened.

    Generation 0 is the fresh session and always worked; 1 is the state after
    the first Load example / Open / Upload, which is where the editor went blank.
    """
    at = _editor(generation)
    text = at.text_area[0].value or ""
    assert text, f"the editor is empty at generation {generation}"
    assert json.loads(text)["name"] == _project().name


def test_reload_refills_the_editor_after_a_load():
    at = _editor(1)
    next(b for b in at.button if b.label == "Reload").click().run()
    assert not at.exception, [e.message for e in at.exception]
    assert json.loads(at.text_area[0].value)["name"] == _project().name


def test_apply_round_trips_an_edit_after_a_load():
    """An edit typed after a load reaches the session project.

    Apply bumps the generation itself (it replaces the project without saving
    it), so a key that could not follow one bump could not follow this one
    either: the text area must still hold the applied project afterwards.
    """
    at = _editor(1)
    edited = json.loads(at.text_area[0].value)
    edited["name"] = "edited after a load"
    at.text_area[0].set_value(json.dumps(edited, indent=2)).run()
    next(b for b in at.button if b.label == "Apply").click().run()
    assert not at.exception, [e.message for e in at.exception]
    assert not at.error, [e.value for e in at.error]
    assert at.session_state["project"].name == "edited after a load"
    assert json.loads(at.text_area[0].value)["name"] == "edited after a load"


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-q"]))
