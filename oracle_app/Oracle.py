"""sloads — the **oracle GUI** entry point (design note 32, step OG-D).

Run with:  streamlit run oracle_app/Oracle.py    (or: sloads-oracle)

A second, independently launched front-end over the *same* ``sloads`` calc
package, exposing only the capability of the original McMaster **FAR 23 LOADS**
suite: the original programs' inputs, and nothing this replication added. It is
not a mode of ``app/`` and shares no page with it — the two are peers over one
analysis model (OG-1), and everything they genuinely share (the project in
session state, the dirty guard, the units toggle, the project-file widget, the
unit-input boundary) lives in :mod:`app_shell`, owned once (OG-4/G8).

**Its page set is derived, not listed** (OG-2, gate G2):
:func:`sloads.workflow.oracle_steps` is the owner, and the rule is *runs a
``.BAS`` program, or produces a slice such a step requires*. Adding a ``bas`` to
a workflow step therefore adds a page here with no edit to this file. There are
no per-page view files either: every page is :func:`oracle_app.form.render_step`
bound to a step key, and what it shows comes from
:mod:`sloads.field_registry` — which is why fourteen pages cost one renderer.

**What it deliberately does not have.** The sbeam decks, the workbook,
``app/``'s summary report and the concept-mode pages: all still fully available
in ``app/`` and none of them reachable from here. **Plots left that list at #267
(note 60 D-60.1):** every figure the oracle report carries is drawn on the page
that produces it, in two marked stages -- what is entered, and what was computed
-- from the report's own ``PlotData`` producers through
:mod:`app_shell.plots`. This GUI derives no figure data of its own, which is why
gaining twenty figures cost it no second owner of anything.
**The sloads-only fields are
no longer on that list (#266, note 57 D-57.2, amending OG-1/OG-2 above):** every
registry input path renders here now, the ones the original programs never asked
for marked and stating why sloads asks for them
(:data:`oracle_app.form.EXTENSION_MARK`). The charter that survives is the one
that was always the point -- *this front-end leads with the original suite's own
inputs, and leaving the marked fields unfilled asks exactly what the original
programs asked* -- rather than the one enforced by dropping fields out of a page
definition, which made a concept field enterable in no form at all. What no
widget can address is declared with its reason in
:data:`sloads.field_registry.JSON_ONLY_RECORDS` and entered in the JSON editor.
**Amended for milestone 0.8.2 (design note 44, OR-3/OR-16):** this GUI now
carries one page that is not a workflow step -- ``Report``, which generates a
formal technical report of *this* front end's own analysis and writes it as an
issue package. It is registered on ``st.navigation`` below and deliberately not
in ``register_pages``: that mapping is the derived step set (gate G2) and stays
exactly that, so the report page can never be mistaken for an analysis step or
be reached by a cross-page step link. **Amended for milestone 0.8.4 (design
note 57, D-57.5):** a third such page joins them -- ``Aircraft Comparison``,
which places this airplane against a reference fleet by wing loading, power
loading, weight and geometry. It is the Phase-C *assess against similar
airplanes* requirement, so it is capability rather than decoration; it runs no
``.BAS`` program, which is why it carries the extension mark, is registered on
the navigation only, and reads nothing any FAR computation reads.
**Amended for milestone 0.8.4 (design
note 57, D-57.3):** a second such page joins it -- the ``Project JSON Editor``,
owned in :mod:`app_shell.project_editor` and registered the same way. It is the
escape hatch for the field delta above -- and since #266 built D-57.2's two
tiers, for the far smaller delta that remains: the records
:data:`sloads.field_registry.JSON_ONLY_RECORDS` names, which live inside a list
row and which no widget can name. The editor edits the project, not a form. A
project saved by
either GUI opens in the other unchanged (OG-13, gate G6) — this front-end asks
for less, it does not store anything different.
"""

from __future__ import annotations

import streamlit as st

from app_shell.nav import register_pages
from app_shell.project_editor import (
    EDITOR_TITLE,
    EDITOR_URL_PATH,
    render_project_editor,
)
from app_shell.project_state import ensure_project
from app_shell.sidebar import render_shell_sidebar
from oracle_app.fleet import PAGE_TITLE as FLEET_TITLE
from oracle_app.fleet import render_fleet_page
from oracle_app.form import render_step
from oracle_app.report import PAGE_TITLE as REPORT_TITLE
from oracle_app.report import render_report_page
from sloads import workflow as wf

# The first Streamlit call, and the ONLY set_page_config in this entry point --
# exactly one per GUI entry point (note 32, OG-10). The shell imports above
# define widgets but emit nothing, so they do not consume it.
st.set_page_config(page_title="sloads — oracle", layout="wide", page_icon="📐")


def _page(step: wf.WorkflowStep, *, default_key: str) -> st.Page:
    """A navigable page for an oracle step.

    The page *is* the generic renderer bound to this step's key. A callable
    rather than a ``views/<key>.py`` path on purpose: a file per page would be a
    hand-maintained page list wearing a different hat, and gate G2 requires that
    adding a ``bas`` to a workflow step adds a page with no GUI edit at all.

    ``default_key`` is the first oracle step's key, resolved once by the caller
    rather than per page (CR-A-9) -- the page set is still derived, the landing
    page is still the first step, and ``oracle_steps()`` is walked once.
    """
    def render() -> None:
        render_step(step.key)

    render.__name__ = step.key
    return st.Page(render, title=step.title, url_path=step.key,
                   default=(step.key == default_key))


project = ensure_project()
_steps = wf.oracle_steps()
_pages = {step.key: _page(step, default_key=_steps[0].key) for step in _steps}
# This GUI's page set, so a cross-page link resolves to a page it actually
# carries rather than to app/'s directory layout (note 32, OG-F).
register_pages(_pages)

# The editor and the report are appended to the navigation only --
# ``register_pages`` above still receives exactly ``oracle_steps()``, in order
# (note 44, OR-16). Neither is an oracle step: the report is a document *about*
# the analysis, and the JSON editor edits the project every step reads, so
# putting either in the derived mapping would make it reachable as a step and
# as a cross-page step link (note 57, D-57.3).
_editor_page = st.Page(render_project_editor, title=EDITOR_TITLE,
                       url_path=EDITOR_URL_PATH)
_report_page = st.Page(render_report_page, title=REPORT_TITLE, url_path="report")
# The third such page (#268, note 57 D-57.5): the fleet comparison. It runs no
# program of the original suite -- which is why its title carries the extension
# mark and why it is registered here rather than in the derived step set.
_fleet_page = st.Page(render_fleet_page, title=FLEET_TITLE,
                      # ``fleet`` rather than ``aircraft_comparison``: the latter is a
                      # workflow step key -- the app's GUI-only page -- and a
                      # URL that collides with one would make a non-step
                      # reachable as a step link (gate G2).
                      url_path="fleet")
pg = st.navigation(
    list(_pages.values()) + [_fleet_page, _editor_page, _report_page],
    expanded=True)
# The sidebar wraps the page: its project-file block renders *after* the page
# has persisted this rerun's edit, so the download and the dirty flag are
# never one keystroke stale (#64, PB-4).
with render_shell_sidebar(project):
    st.sidebar.caption(
        "**Oracle interface** — the original suite's inputs only. "
        "The full sloads app is `streamlit run app/Home.py`."
    )
    pg.run()
