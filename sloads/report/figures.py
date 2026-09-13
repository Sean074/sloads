"""The **figure catalogue** -- one producer set, two renderers (design note 60).

Until #267 a figure existed only inside a document. ``content.PlotData`` was
already renderer-agnostic and ``plots_tex`` already emitted TikZ from it, but the
only way to obtain one was to build a report bundle, so the oracle GUI -- the
front-end note 57 D-57.1 makes the survivor -- carried no chart of any kind while
``app/views/`` carried twenty. Note 57 D-57.4 would have closed that by writing
the GUI's figures fresh from the result slices; note 60 D-60.1 withdraws that,
because it creates a **second owner** of what a figure is, and two owners of one
picture is the drift class (#239) the whole convergence exists to end.

**What this module is.** The one table that says which figures exist, what kind
of drawing each is, which page shows it, and which function builds it. The
builders themselves live next to the sections they were lifted out of
(:mod:`sloads.report.oracle_sections`), because that is where the figure is
constructed and note 60 asks for one construction, not for a second copy here.
This module is data plus two accessors.

**Families, not keys** (D-60.2). A key names one drawing; a *family* names the
kind. ``vn_0 .. vn_14`` is one family at fifteen keys, because how many V-n
diagrams a project has is a fact about its loadings, not about the catalogue.
:attr:`sloads.report.content.Figure.family` carries it, stated by the producer;
the guard walks families and never parses a key.

**Pre-run and post-run** (D-60.4). The GUI's use for a figure is *checking the
inputs before running the whole process*, and a reader must never take an echo
of what they typed for a result. So every family says which it is, and the page
prints it beside the drawing.

The rule, stated once: **pre-run means the drawing is entered data** -- a
planform, a CG envelope, a control surface on its host -- **and no load has been
computed to make it.** D-60.4 words this as "buildable from the ``Project``
alone", and for the three producers §1.3 measured that is the same sentence.
It is not the same sentence everywhere else, because several producers reach the
calc directly rather than through a ``ModuleResult`` mapping: ``_wing_net``
builds the net wing loads from a ``Project`` and nothing else, and the shear it
draws is a result however few arguments its builder takes. Classifying on the
argument list would therefore have labelled five delivered load distributions
"pre-run", which is precisely the mistake D-60.4 exists to prevent, so the stage
is stated per family rather than derived.

**Gates.** ``tests/test_figures.py`` holds note 60 §5's gates 9 and 10: every
family builds for every bundled example without raising and states an
``absent_reason`` where it has no data, and the catalogue and the oracle report
cover each other both ways.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Set, Tuple

from ..models import Project
from ..models.results import ModuleResult
from ..units import UnitSystem
from .content import Figure


class Stage(Enum):
    """When a figure can be drawn -- and therefore what it is showing."""

    #: Entered data: nothing has been computed to draw it.
    PRE_RUN = "pre-run"
    #: A result: a load, an envelope or a march this analysis produced.
    POST_RUN = "post-run"


#: What a page says beside a figure, so the reader is never left to infer it.
STAGE_NOTES: Dict[Stage, str] = {
    Stage.PRE_RUN: ("**Pre-run** — drawn from what is entered. Nothing here "
                    "has been computed; it is this page's own input, shown as "
                    "a picture so it can be checked before the analysis runs."),
    Stage.POST_RUN: ("**Post-run** — a result of this analysis. Every load "
                     "drawn is LIMIT, with the factor 14 CFR 23.303 prescribes "
                     "stated per case and applied nowhere."),
}

#: ``(project, *, system, results) -> figures``. ``results`` is the
#: ``run_sections`` mapping, or ``None`` where the analysis has not been run.
Builder = Callable[..., Sequence[Figure]]


@dataclass(frozen=True)
class FigureFamily:
    """One kind of drawing: where it belongs, what it shows, who builds it."""

    #: :attr:`Figure.family` of every instance this row covers.
    key: str
    #: How a page names it. Not the figure's own title -- an instance carries
    #: that, and where a family is a run the instances differ by it.
    title: str
    #: The :func:`sloads.workflow.oracle_steps` key of the page that shows it.
    step: str
    stage: Stage
    #: The one function that constructs it. Shared where one producer emits
    #: several families; :func:`build_step_figures` calls each builder once.
    build: Builder


def _catalogue() -> Tuple[FigureFamily, ...]:
    """The catalogue, built behind a function so the import stays lazy.

    ``oracle_sections`` imports ``oracle_content``, which imports this package;
    resolving the builders at module scope would close that circle. Called once
    by :func:`CATALOGUE`.
    """
    from . import oracle_sections as osx

    pre, post = Stage.PRE_RUN, Stage.POST_RUN

    def rows(step: str, build: Builder, stage: Stage,
             *families: Tuple[str, str]) -> List[FigureFamily]:
        return [FigureFamily(key, title, step, stage, build)
                for key, title in families]

    out: List[FigureFamily] = []
    out += rows("configuration_layout", osx.geometry_figures, pre,
                ("planform_wing", "Wing planform"),
                ("planform_htail", "Horizontal tail planform"),
                ("planform_vtail", "Vertical tail planform"))
    out += rows("weight_mass", osx.weight_cg_figures, pre,
                ("weight_cg", "Weight and centre-of-gravity envelope"))
    out += rows("structural_speeds", osx.speed_altitude_figures, pre,
                ("speed_altitude", "Speed and altitude envelope"))
    out += rows("flight_envelope", osx.vn_figures, post,
                ("vn", "Flight envelope (V-n)"))
    out += rows("flight_envelope", osx.trim_figures, post,
                ("trim_tail_load", "Balancing tail load against CG"),
                ("static_margin", "Static margin against CG"))
    out += rows("aero_coefficients", osx.aero_curve_figures, post,
                ("aero_cl_alpha", "Airplane-less-tail lift coefficient"),
                ("aero_cm_alpha", "Airplane-less-tail pitching moment"))
    out += rows("wing_loads", osx.wing_axis_figures, post,
                ("planform_wing_lra", "Wing loads reference axis"))
    out += rows("wing_loads", osx.wing_span_load_figures, post,
                ("wing_span_load", "Wing span loading"),
                ("wing_span_load_flaps", "Wing span loading, flaps down"))
    out += rows("wing_loads", osx.wing_distribution_figures, post,
                ("wing_shear_sz", "Vertical shear Sz"),
                ("wing_bending_mxx", "Bending moment Mxx"),
                ("wing_torsion_myy", "Torsion Myy"),
                ("wing_shear_sx", "Drag shear Sx"),
                ("wing_chord_bending_mzz", "Chord bending Mzz"))
    out += rows("wing_loads", osx.lumping_figures, post,
                ("lumping_wing", "Wing lumping deviation"))
    out += rows("fuselage_loads", osx.body_side_view_figures, pre,
                ("body_side_view", "Fuselage mass, beam and load introduction"))
    out += rows("fuselage_loads", osx.body_distribution_figures, post,
                ("body_shear_sz", "Vertical shear Sz"),
                ("body_bending_myy", "Bending moment Myy"))
    out += rows("fuselage_loads", osx.lumping_figures, post,
                ("lumping_fuselage", "Fuselage lumping deviation"))
    out += rows("tail_loads", osx.tail_axis_figures, post,
                ("planform_htail_lra", "Horizontal tail loads reference axis"),
                ("planform_vtail_lra", "Vertical tail loads reference axis"))
    out += rows("tail_loads", osx.tail_chord_figures, post,
                ("chordwise_htail", "Horizontal tail chordwise pressure"),
                ("chordwise_vtail", "Vertical tail chordwise pressure"))
    out += rows("tail_loads", osx.lumping_figures, post,
                ("lumping_htail", "Horizontal tail lumping deviation"),
                ("lumping_vtail", "Vertical tail lumping deviation"))
    out += rows("aileron_loads", osx.aileron_figures, post,
                ("chordwise_aileron", "Aileron chordwise pressure"))
    out += rows("aileron_loads", osx.aileron_figures, pre,
                ("locator_aileron", "The aileron on the wing"))
    out += rows("flap_loads", osx.flap_figures, post,
                ("chordwise_flap", "Flap chordwise pressure"))
    out += rows("flap_loads", osx.flap_figures, pre,
                ("locator_flap", "The flap on the wing"))
    out += rows("tab_loads", osx.tab_figures, post,
                ("chordwise_tab", "Tab chordwise pressure"))
    out += rows("tab_loads", osx.tab_figures, pre,
                ("locator_tab", "The tab on its host surface"))
    out += rows("engine_mount", osx.engine_view_figures, post,
                ("engine_side_view", "The engine installation in side view"),
                ("engine_front_view", "The engine installation in front view"),
                ("engine_plan_view", "The engine installation in plan view"))
    out += rows("one_engine_out", osx.oei_figures, post,
                ("oei_yaw", "Yaw response"),
                ("oei_load", "Fin load history"))
    out += rows("landing_loads", osx.attitude_figures, post,
                ("ground_attitude", "Ground attitudes"))
    return tuple(out)


@lru_cache(maxsize=1)
def catalogue() -> Tuple[FigureFamily, ...]:
    """Every figure family, in page order. Built once."""
    return _catalogue()


def families_for_step(step: str) -> Tuple[FigureFamily, ...]:
    """The families one oracle page shows, pre-run first.

    Pre-run ahead of post-run because that is the order the page is used in: a
    reader checks the shape they entered, then looks at what it produced.
    """
    rows = [f for f in catalogue() if f.step == step]
    return tuple([f for f in rows if f.stage is Stage.PRE_RUN]
                 + [f for f in rows if f.stage is Stage.POST_RUN])


def stage_of(family: str) -> Optional[Stage]:
    """``family``'s stage, or ``None`` if the catalogue does not carry it."""
    return next((f.stage for f in catalogue() if f.key == family), None)


def results_for_step(project: Project, step: str,
                     ) -> Dict[str, Optional[ModuleResult]]:
    """Run one page's programs, keyed as ``run_sections`` keys them.

    The post-run families need module results and a GUI page has no report
    bundle to take them from, which is what D-60.3 is about. Keyed by step key
    *and* by module name for the same reason ``run_sections`` is: a page that
    names three programs produces numbers from all three.

    Catching broadly matches ``run_sections``: a half-filled project must still
    draw the figures it can, and a traceback out of here would take a page down
    over one absent slice.
    """
    from ..registry import get as get_module
    from ..workflow import BY_KEY, step_modules

    out: Dict[str, Optional[ModuleResult]] = {}
    modules = step_modules(step)
    primary = BY_KEY[step].module if step in BY_KEY else None
    for name in modules:
        try:
            result: Optional[ModuleResult] = get_module(name)(project)
        except Exception:  # see the docstring
            result = None
        out[step if name == primary else name] = result
    return out


def build_step_figures(step: str, project: Project, *, system: UnitSystem,
                       results: Optional[Mapping[str, Optional[ModuleResult]]] = None,
                       ) -> List[Tuple[FigureFamily, Figure]]:
    """Every figure one oracle page shows, each with the family it belongs to.

    One call per builder, however many families it serves, and the instances are
    then sorted back into the families that declared them -- so a producer that
    emits two families (the aileron's pressure profile and its locator) is not
    run twice, and a figure whose family this page does not declare is dropped
    rather than shown on a page that never asked for it.
    """
    families = families_for_step(step)
    if not families:
        return []
    wanted: Dict[str, FigureFamily] = {f.key: f for f in families}
    built: Dict[str, List[Figure]] = {}
    seen: Set[int] = set()
    for family in families:
        if id(family.build) in seen:
            continue
        seen.add(id(family.build))
        for figure in family.build(project, system=system, results=results):
            built.setdefault(figure.family, []).append(figure)
    out: List[Tuple[FigureFamily, Figure]] = []
    for family in families:
        for figure in built.get(family.key, ()):
            out.append((wanted[family.key], figure))
    return out


__all__ = [
    "STAGE_NOTES",
    "Builder",
    "FigureFamily",
    "Stage",
    "build_step_figures",
    "catalogue",
    "families_for_step",
    "results_for_step",
    "stage_of",
]
