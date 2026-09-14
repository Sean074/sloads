"""The oracle GUI's **Aircraft Comparison** page -- this airplane against a fleet.

Design note 57 D-57.5. The retiring front-end's fleet page answers the Phase-C
charter question -- *how does this configuration compare with similar
airplanes?* (``01_concept_loads_plan.md`` §1) -- and that is a capability, not a
page decoration, so it lands here rather than retiring with ``app/views/``.

**It is a marked sloads extension, and it is not an oracle step.** The original
McMaster suite has no fleet comparison; #266's convention is that capability
this replication added says so where it appears, so the page title and its lead
caption carry :data:`oracle_app.form.EXTENSION_MARK`. It is registered on the
navigation only -- like ``Report`` and the ``Project JSON Editor`` -- never in
``register_pages``, which stays exactly :func:`sloads.workflow.oracle_steps`
(gate G2). Nothing here runs a ``.BAS`` program, and no figure or number on this
page enters a FAR computation.

**It owns none of what it shows.** The subject's metrics come from
:func:`sloads.fleet.subject_from_project`, the comparators from
:func:`sloads.fleet.reference_fleet`, the placement from
:func:`sloads.fleet.fleet_stats`, the six scatters from
:mod:`sloads.report.fleet_figures`, and the rendering of all three from
:mod:`app_shell.fleet_view`, which the app's page uses unchanged until it
retires. That is note 60 D-60.1 applied to the one figure set outside the step
catalogue: this module decides what the page says, and nothing else.
"""

from __future__ import annotations

import streamlit as st

from app_shell.components import active_project
from app_shell.fleet_view import render_figures, render_fleet_table, render_readout
from oracle_app.form import EXTENSION_MARK
from sloads import workflow as wf
from sloads.fleet import reference_fleet, subject_from_project
from sloads.report.fleet_figures import fleet_figures

#: The label is ``workflow.NON_STEP_PAGES``' (note 57, D-57.1) -- typed once,
#: where the page is declared and its reason for not being a step is stated. The
#: extension mark is added here because it is this page's own claim about itself,
#: not part of its name.
PAGE_TITLE = f"{EXTENSION_MARK} {wf.non_step_page('fleet').title}"


def render_fleet_page() -> None:
    """The page. Nothing is computed here that the calc package does not own."""
    project = active_project()
    st.title(PAGE_TITLE)
    st.caption(
        f"**{EXTENSION_MARK} An sloads extension** — the original FAR 23 LOADS "
        "suite has no fleet comparison. This airplane is placed against a "
        "reference fleet by wing loading (W/S), power loading (W/P), weight and "
        "geometry. The reference figures are nominal published specifications "
        "in Imperial units, for comparison only: they never enter a FAR "
        "computation and the unit toggle does not convert them. Jets carry no "
        "shaft power and so no W/P."
    )

    fleet = reference_fleet()
    if not fleet:
        st.info("The bundled reference fleet could not be read, so there is "
                "nothing to compare against.")
        return

    subject = subject_from_project(project)
    if subject is not None:
        render_readout(subject, fleet)
    else:
        st.info("Enter a design weight — on Structural Speeds, or through the "
                "weight estimate or the mass data base — to place this airplane "
                "against the fleet. The fleet itself is drawn below.")

    render_figures(fleet_figures(subject, fleet), key_prefix="fleet.figure")
    render_fleet_table(fleet)


__all__ = ["PAGE_TITLE", "render_fleet_page"]
