"""The Beam Model page and the files it writes -- design note 67.

Gates covered (note 67 §4):

* **Gate 1 -- parity.** The page's write path and the CLI's ``lra`` and ``oew``
  targets produce byte-identical files, given the same ``generated`` stamp, in
  both unit systems: one render, one stamp, one name per artifact.
* **Gate 2 -- one owner each.** The page builds no path, no stamp and no deck
  text of its own; it asks :mod:`sloads.export.deliverables`.
* **Gate 4 -- refusal.** A model the exporter refuses is stated verbatim and
  nothing is written.
* The page renders on a shipped airplane and on a blank project without a
  traceback, and an existing file is not replaced without the named
  confirmation (D-67.8).
"""

from __future__ import annotations

import os
import sys

import pytest
from streamlit.testing.v1 import AppTest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cli
from sloads import io as sloads_io
from sloads.export import deliverables
from sloads.export.lra_model import LraRefusal
from sloads.models import Project
from sloads.report import bundle_stamps
from sloads.units import UnitSystem

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = os.path.join(_ROOT, "examples")
_STAMP_TIME = "2026-10-01 12:00"

#: Every shipped airplane the exporter builds a model for.
_BUILDS = ("atr42_100", "baron_58", "concept_regional_jet", "ga6_normal")


def _project(name: str) -> Project:
    return sloads_io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


@pytest.mark.parametrize("name", _BUILDS)
@pytest.mark.parametrize("system", (UnitSystem.IMPERIAL, UnitSystem.SI))
def test_the_page_and_the_cli_write_the_same_bytes(tmp_path, name, system):
    """Gate 1: the page's render of both files, against the CLI's, to the byte."""
    project = _project(name)
    _csv, stamp = bundle_stamps(project, system, _STAMP_TIME)
    page_prefix = os.path.join(str(tmp_path), "page")
    rendered, absences = deliverables.render_page_set(
        project, page_prefix, system=system, header_comment=stamp)
    assert not absences, absences
    cli_prefix = os.path.join(str(tmp_path), "cli")
    for artifact in deliverables.BEAM_PAGE_ARTIFACTS:
        assert cli.main([os.path.join(_EXAMPLES, f"{name}.project.json"),
                         "--export-sbeam", cli_prefix, "--export-target", artifact,
                         "--units", system.value, "--generated", _STAMP_TIME]) == 0
        with open(deliverables.deliverable_path(cli_prefix, artifact),
                  encoding="utf-8") as fh:
            headless = fh.read()
        assert rendered[deliverables.deliverable_path(page_prefix, artifact)] == headless, (
            name, system.value, artifact)


def test_the_page_names_its_files_after_the_saved_project():
    """D-67.8: the project file's stem, or the stated default when unsaved."""
    folder = os.path.join("some", "folder")
    assert deliverables.page_prefix(folder, "/x/atr42_100.project.json") == \
        os.path.join(folder, "atr42_100")
    assert deliverables.page_prefix(folder, None) == \
        os.path.join(folder, deliverables.UNSAVED_STEM)


def test_a_refused_model_writes_nothing(tmp_path):
    """Gate 4: the deck's refusal propagates before any file is opened."""
    project = _project("atr42_100")
    project.geometry.by_name("wing").ref_axis_pct = None
    with pytest.raises(LraRefusal):
        deliverables.render_page_set(project, os.path.join(str(tmp_path), "x"))
    assert os.listdir(str(tmp_path)) == []


def test_a_project_with_no_operating_rows_still_gets_its_deck(tmp_path, monkeypatch):
    """The OEW set is the deck's companion: its absence is said, not fatal."""
    from sloads.export import mass_cards

    def refuse(*_a, **_k):
        raise ValueError("Project has no empty or minimum-flight-weight rows")

    monkeypatch.setattr(mass_cards, "oew_fragment", refuse)
    project = _project("atr42_100")
    rendered, absences = deliverables.render_page_set(
        project, os.path.join(str(tmp_path), "x"))
    assert list(rendered) == [os.path.join(str(tmp_path), "x.lra_model.bdf")]
    assert absences and "operating empty weight" in absences[0]


def test_an_existing_file_is_reported_before_it_is_replaced(tmp_path):
    prefix = os.path.join(str(tmp_path), "atr")
    paths = [deliverables.deliverable_path(prefix, a)
             for a in deliverables.BEAM_PAGE_ARTIFACTS]
    assert deliverables.existing(paths) == []
    with open(paths[0], "w", encoding="utf-8") as fh:
        fh.write("old")
    assert deliverables.existing(paths) == [paths[0]]


def test_the_folder_chooser_has_one_owner():
    """D-67.7: the OS dialog is raised from ``app_shell.folder_picker`` alone, so
    a second page that writes cannot grow a second picker (the #239 class)."""
    import glob

    callers = []
    for package in ("app_shell", "oracle_app"):
        for path in glob.glob(os.path.join(_ROOT, package, "*.py")):
            with open(path, encoding="utf-8") as fh:
                if "choose_directory(" in fh.read():
                    callers.append(os.path.relpath(path, _ROOT))
    assert callers == [os.path.join("app_shell", "folder_picker.py")], callers


# --------------------------------------------------------------------------- #
# The page itself, under AppTest
# --------------------------------------------------------------------------- #
_SCRIPT = '''
from oracle_app.beam_model import render_beam_model_page
render_beam_model_page()
'''


def _render(project: Project, folder: str = "") -> AppTest:
    at = AppTest.from_string(_SCRIPT, default_timeout=120)
    at.session_state["project"] = project
    if folder:
        at.session_state["beam_model_root"] = folder
    at.run()
    assert not at.exception, [e.message for e in at.exception]
    return at


def test_the_page_renders_a_shipped_airplane(tmp_path):
    at = _render(_project("atr42_100"), str(tmp_path))
    assert not at.error, [e.value for e in at.error]
    assert any("Loads reference axes" in h.value for h in at.subheader)
    assert any(b.label == "Write the deck and the OEW mass set" for b in at.button)


def test_the_page_states_a_refusal_verbatim_and_offers_no_write(tmp_path):
    """Gate 4 on the page: the exporter's words, and no write control."""
    project = _project("atr42_100")
    project.geometry.by_name("wing").ref_axis_pct = None
    try:
        from sloads.export.lra_model import build_lra_model

        build_lra_model(project)
    except LraRefusal as exc:
        reason = str(exc)
    at = _render(project, str(tmp_path))
    assert [e.value for e in at.error] == [reason]
    assert not any(b.label == "Write the deck and the OEW mass set" for b in at.button)


def test_a_blank_project_renders_without_a_traceback():
    at = _render(Project(name=""))
    assert at.error, "a blank project has no model; the page must say why"


def test_the_write_button_writes_both_files(tmp_path):
    at = _render(_project("atr42_100"), str(tmp_path))
    next(b for b in at.button if b.label == "Write the deck and the OEW mass set").click().run()
    assert not at.exception, [e.message for e in at.exception]
    assert sorted(os.listdir(str(tmp_path))) == ["sloads.lra_model.bdf",
                                                  "sloads.oew_mass.bdf"]
    assert at.success


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
