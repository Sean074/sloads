"""The oracle GUI's **figure block** -- the catalogue rendered on a page.

Design note 60, Block A. The surviving front-end carried no chart of any kind
(note 57 §1.3, still true at 0.8.3) while the retiring one carried twenty, nine
of them on pages this GUI already renders. #267 ports them, and the port is
deliberately thin: this module decides *where on a page* a figure goes and *what
the page says about it*, and nothing else. Which figures exist is
:mod:`sloads.report.figures`; what each one is, is a ``PlotData`` from the same
producer the report prints; how a line looks is :mod:`app_shell.plots`.

**Two blocks, because there are two kinds of figure** (D-60.4). A *pre-run*
figure is entered data drawn -- the planform, the CG envelope, the flap on the
wing -- and it renders directly under the form, which is the use the port was
asked for: checking the inputs before running the whole process. A *post-run*
figure is a result and renders under the Results heading, with the loads it
draws. Each block states which it is, once, above its figures, so a reader is
never left to work out whether they are looking at an input or an answer.

**Withheld the same way the tables are.** A page whose inputs disagree shows no
figures either: :func:`oracle_app.form.render_step` returns before either
function here is reached, exactly as it does for ``render_results``. A figure
that could be drawn from a half-entered project would be a picture of an
airplane the analysis has just refused to run.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import streamlit as st

from app_shell.plots import render_figure
from sloads.models import Project
from sloads.report import figures as fx
from sloads.report.content import Figure
from sloads.units import UnitSystem


def _block(project: Project, key: str, system: UnitSystem, stage: fx.Stage,
           ) -> List[Tuple[fx.FigureFamily, Figure]]:
    """This page's figures of one stage, built through the catalogue.

    The module results are run only for the post-run block: a pre-run figure is
    entered data by definition, and paying for the analysis to draw the planform
    would defeat the reason the pre-run tier exists.
    """
    if not any(f.stage is stage for f in fx.families_for_step(key)):
        return []
    results = (fx.results_for_step(project, key)
               if stage is fx.Stage.POST_RUN else None)
    return [(family, figure)
            for family, figure in fx.build_step_figures(
                key, project, system=system, results=results)
            if family.stage is stage]


def _render(built: List[Tuple[fx.FigureFamily, Figure]], key: str,
            stage: fx.Stage, heading: str) -> None:
    if not built:
        return
    st.header(heading)
    st.caption(fx.STAGE_NOTES[stage])
    for _family, figure in built:
        render_figure(figure, key=f"{key}.figure.{figure.key}")


def render_input_figures(project: Project, key: str,
                         system: UnitSystem) -> None:
    """The page's pre-run figures: what has been entered, drawn."""
    _render(_block(project, key, system, fx.Stage.PRE_RUN), key,
            fx.Stage.PRE_RUN, "Figures — what is entered")


def render_result_figures(project: Project, key: str,
                          system: UnitSystem) -> None:
    """The page's post-run figures: what this page's programs produced."""
    _render(_block(project, key, system, fx.Stage.POST_RUN), key,
            fx.Stage.POST_RUN, "Figures — what was computed")


def page_figures(project: Project, key: str, system: UnitSystem,
                 stage: Optional[fx.Stage] = None,
                 ) -> List[Tuple[fx.FigureFamily, Figure]]:
    """Every figure one page draws, as data. The figure gate's subject.

    The same reason :func:`oracle_app.results.page_artifacts` exists: a gate
    that walks what the page actually renders cannot be satisfied by a source
    pattern that merely resembles it.
    """
    stages = (stage,) if stage is not None else (fx.Stage.PRE_RUN,
                                                 fx.Stage.POST_RUN)
    return [item for s in stages for item in _block(project, key, system, s)]


__all__ = ["page_figures", "render_input_figures", "render_result_figures"]
