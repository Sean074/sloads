"""The **Project JSON Editor**, owned by the shell and registered by the GUI.

Design note 57, **D-57.3** — the first row of band B5. The editor is the
*escape hatch* that decouples every other port from the convergence schedule:
once the surviving GUI carries it, every sloads-only field is reachable there
before D-57.2's two field tiers render a widget for any of them, so there is no
capability window in which a concept field is unenterable.

It lives here rather than in the GUI because it was rendered by both while
both existed (``app/views/project_editor.py`` was a two-line wrapper over it
until D-57.1 deleted that tree) — and because the GUI may not import ``json``
at all (note 32,
gate G1: no second analysis path). The editor's ``json`` use is presentation —
it serialises the project ``sloads.io`` already built and parses the text back
for ``sloads.io`` to rebuild — and the gate is scoped to ``oracle_app/``, so
the shared owner is where this capability can live at all.

The canonical ``project.json`` on disk (and every calc module) is always
Imperial -- see ``sloads/units.py`` and CLAUDE.md's units discussion. This
page is a presentation-layer convenience only: it shows the *same* project as
JSON, converted into the sidebar's selected Imperial/SI display units
(``sloads.units.project_dict_to_display``), so a user reviewing or
hand-editing weight/geometry data can work in whichever system they think in.
Apply converts the edited JSON back to Imperial
(``sloads.units.project_dict_to_imperial``) and replaces the in-session
project; the existing sidebar Open/Save/Download widget then persists it
exactly as it always has -- one Imperial project.json, with all project data in
it. No new file, no stored unit tag.

Fields with no known unit conversion (airspeed/altitude -- deliberately kept
aviation-standard in both systems -- plus any field not yet in the project
schema's unit table) are shown/edited in their native Imperial value
regardless of the toggle; see the caption below for the exact list.
"""

from __future__ import annotations

import json
from typing import Any, List, Tuple

import streamlit as st

from app_shell.components import active_system, stop_page
from app_shell.widget_keys import bump_generation, widget_key
from sloads import Project, UnitSystem
from sloads import io as sloads_io
from sloads import workflow as wf
from sloads.units import project_dict_to_display, project_dict_to_imperial
from sloads.validation import safety_factor_valid

#: The page this module *is*. The editor is not a step of the analysis -- it
#: edits the project every step reads -- so it is registered on
#: ``st.navigation`` only: the OR-16 pattern the Report page established, and for
#: the same reason: ``register_pages`` is the derived step set (gate G2) and
#: stays exactly that. It was a step of the retired front-end's page set until
#: #270, and is now one of ``workflow.NON_STEP_PAGES`` (note 57, D-57.1), which
#: is where the title and the reason are owned rather than typed again here. The
#: names carry the ``EDITOR_`` prefix because a shell symbol is owned for the
#: whole app: a bare ``PAGE_TITLE`` here would collide with the one the Report
#: page already owns (gate G8).
EDITOR_STEP_KEY = "project_editor"
EDITOR_TITLE = wf.non_step_page(EDITOR_STEP_KEY).title
EDITOR_URL_PATH = EDITOR_STEP_KEY

#: The **unstamped** base of the text widget's key. It is stamped with the
#: project generation at every use (``widget_key(_TEXT_KEY)``), never here:
#: a module-level stamp is evaluated once per process, at generation 0, and
#: every widget seeded from the project must not outlive the project it was
#: read from (``app_shell.widget_keys``). Stamped at import until the 0.8.4
#: closure review, which is why the editor showed an empty text area after the
#: first load: the seed went to the frozen key and the widget read the live one.
#: Guard: ``tests/test_widget_freshness.py::test_no_gui_module_stamps_a_key_at_import``.
_TEXT_KEY = "_project_editor_text"
_LOADED_SNAPSHOT_KEY = "_project_editor_loaded_for"


def _bad_safety_factors(node: Any, path: str = "") -> List[Tuple[str, Any]]:
    """``(json_path, value)`` for every ``safety_factor`` in the dict tree that
    fails ``sloads.validation.safety_factor_valid`` (M4-14)."""
    found: List[Tuple[str, Any]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            sub = f"{path}.{key}" if path else key
            if key == "safety_factor" and not safety_factor_valid(value):
                found.append((sub, value))
            else:
                found.extend(_bad_safety_factors(value, sub))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found.extend(_bad_safety_factors(item, f"{path}[{i}]"))
    return found


def _current_display_text(project: Project, system: UnitSystem) -> str:
    raw = sloads_io.project_to_dict(project)
    display = project_dict_to_display(raw, system)
    return json.dumps(display, indent=2, sort_keys=False)


def render_project_editor() -> None:
    """Render the editor page. The whole page body, in either front-end."""
    st.title(EDITOR_TITLE)
    st.caption(
        "The whole project, shown as JSON in the sidebar's selected units. Calc "
        "and the saved project.json are always Imperial -- this is a "
        "display/edit convenience; **Apply** converts back to Imperial before "
        "updating the session, and the existing sidebar **Save to disk** / "
        "**Download** writes the same single Imperial project.json as every "
        "other page."
    )

    # D-16: ``active_system()`` is the single read of the unit selection.
    # Reading ``session_state["unit_system"]`` here was a second authority for
    # the same decision -- since M4-20 step 2 the project field is the source,
    # and the session key is only the no-project-yet fallback inside
    # ``active_system()``.
    system: UnitSystem = active_system()
    project: Project = st.session_state.get("project", Project(name=""))

    if system == UnitSystem.SI:
        st.info(
            "Showing **SI**. Airspeed (KEAS) and altitude (ft) fields stay "
            "aviation-standard regardless of this toggle -- they are not "
            "converted. Any field this page doesn't yet recognize also stays in "
            "its native Imperial value; check the field name's unit suffix if "
            "unsure."
        )

    # Re-seed the text area whenever the project or the unit system changes
    # underneath it (e.g. applied on another page, or the sidebar toggle
    # flipped) -- but never clobber an in-progress hand-edit that hasn't been
    # applied yet.
    snapshot_id = (id(project), system.value, sloads_io.project_to_json(project))
    if st.session_state.get(_LOADED_SNAPSHOT_KEY) != snapshot_id:
        st.session_state[widget_key(_TEXT_KEY)] = _current_display_text(project, system)
        st.session_state[_LOADED_SNAPSHOT_KEY] = snapshot_id

    c1, _ = st.columns([1, 5])
    if c1.button("Reload",
                 help="Discard edits below and reload from the current project."):
        st.session_state[widget_key(_TEXT_KEY)] = _current_display_text(project, system)
        st.session_state[_LOADED_SNAPSHOT_KEY] = snapshot_id
        st.rerun()

    edited_text = st.text_area(
        "project.json (selected units)", key=widget_key(_TEXT_KEY), height=560,
        label_visibility="collapsed",
    )

    apply_col, _ = st.columns([1, 5])
    if apply_col.button("Apply", type="primary"):
        try:
            edited_display = json.loads(edited_text)
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
            stop_page()
        try:
            imperial_dict = project_dict_to_imperial(edited_display, system)
            new_project = sloads_io.project_from_dict(imperial_dict)
        except (TypeError, ValueError, KeyError, AttributeError) as exc:
            st.error(f"Could not build a project from this JSON: {exc}")
            stop_page()
        # No schema classification here: pasting a project of any other version
        # is refused by the gate inside project_from_dict (#93), so it has
        # already been reported by the except above. The editor asks about
        # content, not vintage.
        # Surface an invalid per-case safety_factor at the hand-edit entry point
        # (M4-14). Checked on the *raw* dict: project_from_dict has already
        # reset any invalid value to the conservative 1.5 default, so the built
        # project can't show what was typed.
        for _path, _v in _bad_safety_factors(imperial_dict):
            st.warning(
                f"`{_path}`: safety_factor = {_v!r} is outside the legal "
                "[1.0, 1.5] band (14 CFR 23.303; the factor is set by the "
                "load-case definition) and was reset to the conservative "
                "default 1.5."
            )
        st.session_state["project"] = new_project
        # A hand-edit is a *replacement*, like a load: every widget on every
        # other page was seeded from the project this one just discarded, and
        # would write those values back on its next Apply. Not ``adopt()`` --
        # these edits are not saved to disk, so the dirty baseline must stay
        # where it is.
        bump_generation()
        st.session_state[_LOADED_SNAPSHOT_KEY] = None  # force a re-seed
        st.success(
            "Applied. The session project now reflects your edits (converted "
            "back to Imperial). Use the sidebar's Save/Download to write it to "
            "disk."
        )
        st.rerun()


__all__ = ["EDITOR_STEP_KEY", "EDITOR_TITLE", "EDITOR_URL_PATH",
           "render_project_editor"]
