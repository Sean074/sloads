"""sloads — the GUI entry point (design note 32 step OG-D; note 57, D-57.1).

Run with:  streamlit run oracle_app/Oracle.py    (or: sloads-oracle)

**The single front-end.** It was the second of two until #270: a peer over the
same calc package, exposing only the capability of the original McMaster
**FAR 23 LOADS** suite, beside an ``app/`` that carried everything this
replication added. Note 57 retired that front-end -- 22 pages over the same
analysis model was a drift class, not a feature (§1.5) -- and what remains is
this one, with everything worth keeping ported into it first (D-57.8: the
survivor was complete before anything was removed). The name and the
``sloads-oracle`` entry point stand for now; R-57.5 took that branch and
deferred the rename mechanics.

**Its page set is derived, not listed** (OG-2, gate G2, as re-cut by D-57.1):
:func:`sloads.workflow.gui_pages` is the owner. Its derived half is
:func:`sloads.workflow.oracle_steps` -- *runs a ``.BAS`` program, or produces a
slice such a step requires* -- so adding a ``bas`` to a workflow step adds a page
here with no edit to this file. Its stated half is
:data:`sloads.workflow.NON_STEP_PAGES`, the three pages that are not steps of the
analysis at all, each declaring why. There are no per-page view files either:
every analysis page is :func:`oracle_app.form.render_step` bound to a step key,
and what it shows comes from :mod:`sloads.field_registry` -- which is why
fourteen pages cost one renderer.

**Two field tiers, one renderer** (#266, note 57 D-57.2, amending OG-1/OG-2):
every registry input path renders here, the ones the original programs never
asked for marked and stating why sloads asks for them
(:data:`oracle_app.form.EXTENSION_MARK`). The charter that survives is the one
that was always the point -- *this front-end leads with the original suite's own
inputs, and leaving the marked fields unfilled asks exactly what the original
programs asked* -- rather than the one enforced by dropping fields out of a page
definition, which made a concept field enterable in no form at all. What no
widget can address is declared with its reason in
:data:`sloads.field_registry.JSON_ONLY_RECORDS` and entered in the JSON editor.

**The figures are on the pages that produce them** (#267, note 60 D-60.1), in
two marked stages -- what is entered, and what was computed -- from the report's
own ``PlotData`` producers through :mod:`app_shell.plots`. This GUI derives no
figure data of its own, which is why gaining twenty figures cost it no second
owner of anything.

**What retired without a port** (D-57.6, §1.3): the dashboard (the shell's
sidebar carries the project), the results review (:mod:`oracle_app.results`),
the export page (the CLI writes the decks and the Report page writes the issue
package, whose ``data/`` is the tabular channel -- the ``.xlsx`` workbook went
with it), the tail-span page (the report's tail-span appendix) and the balanced
cases page (the balanced deck and the report's ``balanced_case_rows``). Two of
those are still steps of :data:`sloads.workflow.STEPS` and always were analysis
rather than presentation; the other three were pages and nothing else.

Everything genuinely shared with the retired front-end -- the project in session
state, the dirty guard, the units toggle, the project-file widget, the
unit-input boundary -- lives in :mod:`app_shell`, owned once (OG-4/G8), and a
project saved by the retired GUI opens here unchanged (OG-13, gate G6): one
schema, and retirement strands no saved file.
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

# The pages that are not analysis steps are appended to the navigation only --
# ``register_pages`` above still receives exactly ``oracle_steps()``, in order
# (note 44, OR-16): putting any of them in the derived mapping would make it
# reachable as a step and as a cross-page step link.
#
# Which pages those are, in what order, and *why* each is not a step are
# declared in ``workflow.NON_STEP_PAGES`` (note 57, D-57.1) -- so this file
# names no page set of its own. What it owns is the one thing workflow.py
# cannot: which callable renders each. A row added there with no renderer here
# is a ``KeyError`` at import, which is the drift this mapping is allowed to
# have.
_RENDERERS = {
    EDITOR_URL_PATH: render_project_editor,
    "fleet": render_fleet_page,
    "report": render_report_page,
}
_TITLES = {EDITOR_URL_PATH: EDITOR_TITLE, "fleet": FLEET_TITLE, "report": REPORT_TITLE}
_extra_pages = [
    st.Page(_RENDERERS[page.key], title=_TITLES[page.key], url_path=page.key)
    for page in wf.NON_STEP_PAGES
]
pg = st.navigation(list(_pages.values()) + _extra_pages, expanded=True)
# The sidebar wraps the page: its project-file block renders *after* the page
# has persisted this rerun's edit, so the download and the dirty flag are
# never one keystroke stale (#64, PB-4).
with render_shell_sidebar(project):
    st.sidebar.caption(
        "**sloads** — FAR 23 structural design loads. "
        "Fields the original suite never asked for are marked where they appear."
    )
    pg.run()
