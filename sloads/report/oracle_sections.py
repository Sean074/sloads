"""The oracle report's analysis sections, built from ``ModuleResult`` values.

Design note 44, OR-8 iteration 2. :mod:`sloads.report.oracle_content` owns the
document's *structure* -- which sections exist, what state each is in, how they
are numbered. This module owns their *content*: one builder per step key,
turning the result the analysis already produced into
:class:`sloads.report.content.Section` tables and figures. Each future OR-8
iteration adds a builder here rather than growing the structure module without
limit.

**Nothing here computes.** OR-6 makes the report a view: every number it prints
is a value some module returned, reproduced without re-derivation. The only
arithmetic is unit conversion and the ULTIMATE boundary, and neither is done
here either -- :func:`sloads.units.convert_results` and
:func:`sloads.report.render.ultimate_units` is their owner, and it is asked
rather than re-implemented. That is what makes G-OR-4 hold by construction: this
module never decides what a load is, so it cannot mark a load factor as one.

**Section 2 states no load in force or moment units.** Its load factors *are*
loads -- n is a limit load factor, and calling it otherwise is the error this
paragraph used to make (owner, 2026-08-30) -- but they are dimensionless and
LIMIT, so the ultimate boundary passes them through unscaled, as it does the
geometry, mass and speeds beside them. The tables are still routed through that
boundary rather than formatted by hand, because a section that formats its own
numbers is one that will eventually format a load it should have marked.

**Known upstream oddity, filed not yet fixed** (note 44 §10): a
``ConditionResult`` holding no load value still carries ``safety_factor = 1.5``,
because that is the dataclass default. No value is affected -- the boundary
scales by units and quantity, not by the stamp -- but a wing span has no safety
factor, and the owner has ruled that such a condition shall carry ``None``,
rendered "N/A". Until that lands, this module never prints a condition's SF, so
no section 2 table can inherit a claim that does not apply to it.
"""

from __future__ import annotations

import math
import re
from dataclasses import replace
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from ..constants import IN2_PER_FT2, ULTIMATE_FACTOR
from ..derived_geometry import (
    MacReference,
    mac_reference,
    station_to_pct_mac,
    wing_reference,
)
from ..models import MissingInputError, Project
from ..models.enums import AnalysisKind
from ..models.inputs import EngineInput, FuselageStation
from ..models.results import (
    BodyLoadResult,
    ConditionResult,
    ControlSurfaceLoadResult,
    ControlSurfaceStation,
    CriticalCondition,
    LoadValue,
    ModuleResult,
    TailChordResult,
    TailSpanResult,
    WingLoadResult,
)
from ..picks import extreme
from ..units import UnitSystem, convert_results
from .content import Figure, PlotData, Section, Series, Table, Units, speed_altitude_plot_data, weight_cg_plot_data
from .oracle_content import (
    BODY_LOAD_STATIONS,
    HTAIL_LOAD_STATIONS,
    VTAIL_LOAD_STATIONS,
    WING_LOAD_STATIONS,
    SectionPlan,
    appendix_ref,
    section_ref,
    subsection_ref,
)
from .render import format_value, ultimate_units


# --------------------------------------------------------------------------- #
# Reading a result
# --------------------------------------------------------------------------- #
def _conditions(result: Optional[ModuleResult],
                system: UnitSystem) -> List[ConditionResult]:
    """``result``'s conditions in the document's unit system.

    :func:`sloads.units.convert_results` is the single conversion owner and
    keys off the value's own unit string and quantity hint, so this module needs
    no unit table of its own. Imperial is the identity, which is why an Imperial
    report is byte-for-byte unaffected by the conversion path existing.
    """
    if result is None:
        return []
    return list(convert_results(list(result.conditions), system))


def _find(conditions: Sequence[ConditionResult], prefix: str,
          ) -> Optional[ConditionResult]:
    """The first condition whose title starts with ``prefix``."""
    for condition in conditions:
        if condition.title.startswith(prefix):
            return condition
    return None


def _cell(value: LoadValue) -> Tuple[str, str]:
    """``(formatted value, units)`` for one result value, through the boundary.

    Nothing is scaled anywhere since note 49 OR-116, so the value passes
    through and only the marking is decided here. Section 2 holds no loads, so
    ``ultimate_units`` returns the plain unit for everything it sees; if a load
    ever reaches here the marking will be wrong and visible, which is better
    than a silently plausible number.
    """
    units = ultimate_units(value.units, value.quantity)
    return format_value(value.value), units


def _rows(condition: Optional[ConditionResult], *, skip: Sequence[str] = (),
          ) -> List[List[str]]:
    """``[label, value, units]`` per value, minus the keys in ``skip``."""
    if condition is None:
        return []
    rows = []
    for value in condition.values:
        if value.key in skip:
            continue
        formatted, units = _cell(value)
        rows.append([value.label, formatted, units])
    return rows


def _value_table(title: str, condition: Optional[ConditionResult], *,
                 note: str = "", skip: Sequence[str] = ()) -> Optional[Table]:
    """A plain quantity/value/units table, or ``None`` when there is nothing."""
    rows = _rows(condition, skip=skip)
    if not rows:
        return None
    return Table(title=title, columns=["Quantity", "Value", "Units"], rows=rows,
                 note=note)


def _by_key(condition: Optional[ConditionResult]) -> Dict[str, LoadValue]:
    """``{value key: value}`` for one condition."""
    if condition is None:
        return {}
    return {value.key: value for value in condition.values}


def _far_note(condition: Optional[ConditionResult]) -> str:
    """The condition's own FAR reference and note, as a sentence for the prose.

    ``far_reference`` is not always a regulation. The configuration module sets
    it to ``"configuration"`` -- a category, not a clause -- and printing that
    verbatim produced "Certification basis: 14 CFR configuration" in the first
    build of this section. A reference is a regulation only if it begins with a
    part number, and anything else is dropped rather than dressed up as one.
    """
    if condition is None:
        return ""
    parts = []
    reference = (condition.far_reference or "").strip()
    if reference[:1].isdigit():
        parts.append(f"Certification basis: 14 CFR {reference}.")
    if condition.note:
        parts.append(condition.note)
    return " ".join(parts)


# --------------------------------------------------------------------------- #
# 2.1 Geometry
# --------------------------------------------------------------------------- #
#: The condition of ``configuration`` the report carries.
#:
#: The module also returns *Longitudinal stability (estimate)* and *Landing-gear
#: geometry (estimate)*, both of which note themselves as first-order with no
#: oracle. Neither is loads configuration, and a first-order estimate printed
#: beside oracle-locked geometry in a certification document reads as though it
#: carried the same standing. Excluded by the owner, GUI review 2026-08-30.
_GEOMETRY_CONDITION = "Wing planform"

#: ``(attribute, printed label, units)`` per surface, read from the project.
#:
#: **These are inputs, not results.** Everything else in section 2 reproduces a
#: ``ModuleResult``; no module echoes a control-surface area or a throw, so the
#: only honest source is the definition the analysis was given. Echoing an input
#: is not recomputation (OR-6 forbids re-deriving, not reporting), but the tables
#: say so in their own note, because a reader must not take an entered number for
#: a computed one.
#:
#: Declared as data so a renamed or dropped input field fails
#: ``test_oracle_report.py`` rather than silently emptying a row -- the same
#: reason ``_FACTOR_PAIRS`` and ``_SPEED_PAIRS`` are tables.
_HTAIL_ROWS: Tuple[Tuple[str, str, str], ...] = (
    ("htail_area_sqft", "Horizontal tail area", "ft^2"),
    ("aspect_ratio_htail", "Aspect ratio", ""),
    ("htail_semispan_in", "Semispan", "in"),
    ("tail_incidence_deg", "Tail incidence", "deg"),
    ("xt25", "Quarter-chord station XT25", "in"),
    ("xt50", "Half-chord station XT50", "in"),
    ("elevator_area_sqft", "Elevator area", "ft^2"),
    ("elevator_fwd_hinge_sqft", "Elevator area forward of hinge", "ft^2"),
    ("elevator_aft_hinge_sqft", "Elevator area aft of hinge", "ft^2"),
    ("elevator_te_up_deg", "Elevator deflection, trailing edge up", "deg"),
    ("elevator_te_down_deg", "Elevator deflection, trailing edge down", "deg"),
)

_VTAIL_ROWS: Tuple[Tuple[str, str, str], ...] = (
    ("vtail_area_sqft", "Vertical tail area", "ft^2"),
    ("aspect_ratio_vtail", "Aspect ratio", ""),
    ("vtail_span_in", "Span", "in"),
    ("vtail_mac_in", "MAC", "in"),
    ("xv25", "Quarter-chord station XV25", "in"),
    ("rudder_area_sqft", "Rudder area", "ft^2"),
    ("rudder_fwd_hinge_sqft", "Rudder area forward of hinge", "ft^2"),
    ("rudder_aft_hinge_sqft", "Rudder area aft of hinge", "ft^2"),
    ("rudder_deflection_deg", "Rudder deflection", "deg"),
)

_AILERON_ROWS: Tuple[Tuple[str, str, str], ...] = (
    ("area_fwd_hinge_sqft", "Aileron area forward of hinge", "ft^2"),
    ("area_aft_hinge_sqft", "Aileron area aft of hinge", "ft^2"),
    ("down_deflection_deg", "Aileron deflection, trailing edge down", "deg"),
    ("up_deflection_deg", "Aileron deflection, trailing edge up", "deg"),
)

_FLAP_ROWS: Tuple[Tuple[str, str, str], ...] = (
    ("flap_area_one_side_sqft", "Flap area, one side", "ft^2"),
    ("flap_chord_ratio", "Flap chord ratio", ""),
    ("flap_deflection_deg", "Flap deflection", "deg"),
)

_TAB_ROWS: Tuple[Tuple[str, str, str], ...] = (
    ("area_sqft", "Tab area", "ft^2"),
    ("mac_in", "Tab MAC", "in"),
    ("station_in", "Tab station", "in"),
    ("airfoil_chord_in", "Airfoil chord at the tab", "in"),
    ("deflection_deg", "Tab deflection", "deg"),
)

#: Said once, in section 2.1's prose, and never under a table.
#:
#: Six surface tables each carrying it read as boilerplate, which is how a
#: reader learns to skip the notes that matter -- the same finding that moved
#: the units note out of the tables earlier in this review.
_AS_ENTERED_SENTENCE = (
    "The empennage and control-surface values below are the configuration as "
    "entered for this analysis: they are input values, reproduced so the loads "
    "that follow can be read against the surfaces they were computed for, and "
    "they are not analysis output."
)

#: Surface key -> what the document calls it.
#:
#: ``TabInput.surface`` carries the analysis's own key ("htail"), which is our
#: machinery again -- the same reason ``DOCUMENT_TITLES`` exists one level up.
_SURFACE_NAMES = {
    "htail": "horizontal tail",
    "vtail": "vertical tail",
    "wing": "wing",
}


def _input_table(title: str, source: object,
                 rows: Sequence[Tuple[str, str, str]],
                 system: UnitSystem) -> Optional[Table]:
    """One surface's definition, echoed from the project.

    Routed through :class:`LoadValue` and
    :func:`sloads.units.convert_results` rather than formatted here, so an
    echoed input converts and marks by exactly the path a computed value takes.
    A value that is absent or ``None`` is dropped rather than printed as zero --
    an unset station is not a station at the datum.
    """
    if source is None:
        return None
    values = []
    for attr, label, units in rows:
        value = getattr(source, attr, None)
        if value is None:
            continue
        values.append(LoadValue(label=label, value=value, units=units, key=attr))
    if not values:
        return None
    condition = ConditionResult(title=title, far_reference="", values=values)
    converted = convert_results([condition], system)[0]
    return _value_table(title, converted)


#: How a tail table reports where its planform came from.
#:
#: The suite carries the empennage as **scalars** -- area and span -- because
#: that is all SELECT, TAILDIST and BALLOADS ever needed, and those scalars are
#: oracle-authoritative. A spanwise distribution needs a chord at every station,
#: which comes from an ``"htail"``/``"vtail"`` entry in ``geometry.surfaces``
#: with the same leading- and trailing-edge polylines as the wing (plan 09, T-1).
#: Where that entry is absent the planform is derived as a rectangle and marked
#: assumed.
#:
#: The report **asks** :func:`sloads.tail_geometry.resolve_tail_planform` rather
#: than asserting either state. A first draft of this section told every reader
#: that both tails were rectangles, which would have been false for a project
#: that had entered its polylines -- the document stating an assumption the
#: analysis did not make.
_PLANFORM_BASIS = {
    True: "DERIVED rectangle from area and span",
    False: "entered leading- and trailing-edge polylines",
}


def _planform_assumed(project: Project, component: str) -> bool:
    """Whether ``component``'s planform was derived rather than entered."""
    from ..tail_geometry import resolve_tail_planform

    try:
        planform = resolve_tail_planform(project, component)
    except (ValueError, AttributeError):
        return False
    return bool(planform is not None and planform.assumed)


def _tail_table(title: str, project: Project, component: str, source: object,
                rows: Sequence[Tuple[str, str, str]],
                system: UnitSystem) -> Optional[Table]:
    """A tail's definition, with the basis of its planform stated on it."""
    table = _input_table(title, source, rows, system)
    if table is None:
        return None
    from ..tail_geometry import resolve_tail_planform

    try:
        planform = resolve_tail_planform(project, component)
    except (ValueError, AttributeError):
        planform = None
    if planform is not None:
        table.rows.append(["Planform basis", _PLANFORM_BASIS[planform.assumed], ""])
    return table


#: ``(figure key, parent surface, printed title, control surfaces, frame)``.
#:
#: The three main surfaces a reader sizes to, each with the control surfaces
#: that live on it. Declared as data for the same reason ``_HTAIL_ROWS`` is: a
#: renamed surface fails ``test_oracle_report.py`` rather than silently drawing
#: a parent with nothing on it.
#:
#: The frame is not decoration. A wing or horizontal tail is entered as
#: ``(station, butt line)`` and is symmetric about the centre plane, so it is
#: drawn with its mirror; a **vertical tail's second coordinate is a waterline**
#: -- the GA6 fin root is ``(240.912, 117.0)``, station 240.912 at waterline
#: 117.0 -- and mirroring it about ``y = 0`` would draw a second fin hanging
#: below the airplane. The frame decides that, never ``SurfaceInput.symmetric``,
#: which ``examples/baron_58.project.json`` sets ``true`` on its fin.
_PLANFORM_FIGURES: Tuple[Tuple[str, str, str, Tuple[str, ...], str], ...] = (
    ("planform_wing", "wing", "Wing planform", ("aileron", "flap"), "butt"),
    ("planform_htail", "htail", "Horizontal tail planform", ("elevator",), "butt"),
    ("planform_vtail", "vtail", "Vertical tail planform", ("rudder",), "water"),
)

#: The axis labels of each frame, without units -- those are appended from the
#: converted length channel, so an SI report says mm on both axes.
#:
#: A butt-line surface is drawn **span across, station down**: a wing is 402 in
#: of span against a 101 in root chord, and on the equal axes the figure exists
#: to hold, station-across is four times taller than it is wide. The emitter
#: reverses that vertical axis (``planform_tex.NOSE_UP_KEYS``) so the stations
#: still read in the airplane's own numbers with the nose at the top.
_PLANFORM_AXES = {
    "butt": ("Butt line Y", "Fuselage station X"),
    "water": ("Fuselage station X", "Waterline Z"),
    # Section 10's front view (note 44 §20, OR-168). Added here rather than
    # beside the figure that wanted it, because the axis labels of a view are
    # exactly the kind of thing two figures would otherwise word two ways.
    "front": ("Butt line Y", "Waterline Z"),
}


def _oriented(frame: str, x_in: float, y_in: float) -> Tuple[float, float]:
    """An entered ``(station, span)`` point on the frame's plotted axes."""
    return (y_in, x_in) if frame == "butt" else (x_in, y_in)

#: Surface key -> what the figure legend calls it.
#:
#: §3.3's "a surface key SHALL NOT reach a heading" for the same reason one
#: level down: a legend a reviewer reads is not a place for the analysis's own
#: identifiers.
_REGION_NAMES = {
    "wing": "Wing",
    "aileron": "Aileron",
    "flap": "Flap",
    "htail": "Horizontal tail",
    "elevator": "Elevator",
    "vtail": "Vertical tail",
    "rudder": "Rudder",
}

#: ``(surface key, project slice, attribute, printed label)`` for the area a
#: region is labelled with.
#:
#: Every one is a value 2.1 **already prints in a table**, read from the same
#: attribute, so a figure cannot label a surface with a second number for the
#: same quantity ("a number is printed once", §3.3). The wing is not here: its
#: area is produced by the speeds module and is passed in already converted.
#: Neither is the aileron -- ``AileronInput`` carries its areas forward and aft
#: of the hinge and no total, and summing them here would be the report deriving
#: a quantity no module returned (OR-6). It is drawn and named without an area.
_REGION_AREAS: Tuple[Tuple[str, str, str, str], ...] = (
    ("htail", "htail", "htail_area_sqft", "Horizontal tail"),
    ("elevator", "htail", "elevator_area_sqft", "Elevator"),
    ("vtail", "vtail", "vtail_area_sqft", "Vertical tail"),
    ("rudder", "vtail", "rudder_area_sqft", "Rudder"),
    ("flap", "flap_loads", "flap_area_one_side_sqft", "Flap, one side"),
)


def _length_channel(system: UnitSystem) -> Tuple[float, str]:
    """``(scale, units)`` taking an entered inch coordinate into ``system``.

    Asked of :func:`sloads.units.convert_results` through a probe value rather
    than multiplied by a constant here. The conversion has one owner and this
    module is not it; a hard-coded 25.4 is exactly the drift the units history
    is the cautionary precedent for.
    """
    probe = ConditionResult(title="", far_reference="",
                            values=[LoadValue("probe", 1.0, "in", key="probe")])
    converted = convert_results([probe], system)[0].values[0]
    return float(converted.value), converted.units


def _region_areas(project: Project, wing_area: Optional[LoadValue],
                  system: UnitSystem) -> Dict[str, LoadValue]:
    """The area each drawn region is labelled with, converted once."""
    empennage = getattr(project.geometry, "empennage", None) if project.geometry else None
    slices = {
        "htail": getattr(empennage, "htail", None),
        "vtail": getattr(empennage, "vtail", None),
        "flap_loads": project.flap_loads,
    }
    values = []
    for key, slice_name, attr, label in _REGION_AREAS:
        source = slices.get(slice_name)
        value = getattr(source, attr, None) if source is not None else None
        if value is None:
            continue
        values.append(LoadValue(label=label, value=value, units="ft^2", key=key))
    areas: Dict[str, LoadValue] = {}
    if values:
        condition = ConditionResult(title="", far_reference="", values=values)
        areas = {v.key: v for v in convert_results([condition], system)[0].values}
    if wing_area is not None:
        areas["wing"] = wing_area
    return areas


def _region_label(name: str, area: Optional[LoadValue]) -> str:
    """A legend entry: the surface's name, and its area where one is tabulated."""
    printed = _REGION_NAMES.get(name, name)
    if area is None:
        return printed
    formatted, units = _cell(area)
    return f"{printed}: {formatted} {units}".strip()


def _region_series(project: Project, name: str, style: str, label: str,
                   mirror: bool, frame: str, scale: float) -> List[Series]:
    """One surface as closed outlines: the entered side, and its mirror.

    The outline itself comes from :func:`sloads.modules.wing_geometry.surface_top_outline`,
    which is already the shared "edge polylines -> closed outline" owner for the
    two GUI pages that draw a planform. The report asks it rather than walking
    the polylines again, so the document and the pages cannot disagree about
    where a surface ends.

    The mirror carries no name, so it is drawn ``forget plot`` and takes no
    legend entry of its own -- it is the same surface, not a second one.
    """
    from ..derived_geometry import require_integrable_planform
    from ..modules.wing_geometry import surface_top_outline

    surface = project.geometry.by_name(name) if project.geometry else None
    if surface is None:
        return []
    # The same precondition every other consumer of an edge polyline asks
    # (#71/PB-21, ``derived_geometry`` is its one owner). A half-entered
    # planform -- one point on an edge, or a repeated butt line -- is the state
    # the curve editor persists mid-row, and a figure drawn from it is a shape
    # nobody entered rather than an obviously broken one. The ``ValueError`` is
    # caught by the caller into a stated absence: G-OR-7 says a half-filled
    # project still builds a complete document.
    require_integrable_planform(surface)
    outlines = surface_top_outline(surface.leading_edge, surface.trailing_edge,
                                   mirror)
    series = []
    for index, (xs, ys) in enumerate(outlines):
        oriented = [_oriented(frame, x * scale, y * scale)
                    for x, y in zip(xs, ys)]
        series.append(Series(label if index == 0 else "",
                             [x for x, _y in oriented],
                             [y for _x, y in oriented], style, closed=True))
    return series


def _planform_figure(project: Project, key: str, parent: str, title: str,
                     children: Sequence[str], frame: str,
                     areas: Mapping[str, LoadValue],
                     system: UnitSystem) -> Figure:
    """One surface's to-scale planform, with its control surfaces on it."""
    from .planform_tex import OUTLINE_STYLE, REGION_STYLES

    printed = _REGION_NAMES.get(parent, parent)
    surface = project.geometry.by_name(parent) if project.geometry else None
    if surface is None:
        # Stated, never an empty axis (§3.4). For a tail this is the same state
        # the table above reports as a DERIVED planform: the rectangle the
        # analysis assumes is not a shape worth drawing, and drawing it would
        # give the assumption the standing of entered geometry.
        derived = (" The table above reports its planform DERIVED for the same "
                   "reason." if _planform_assumed(project, parent) else "")
        return Figure(
            key=key, title=title,
            absent_reason=(
                f"the project defines no {printed.lower()} leading- and "
                "trailing-edge polylines, so there is no planform to draw."
                + derived))

    scale, length_units = _length_channel(system)
    mirror = bool(surface.symmetric) and frame == "butt"
    try:
        series = _region_series(project, parent, OUTLINE_STYLE,
                                _region_label(parent, areas.get(parent)),
                                mirror, frame, scale)
    except ValueError as problem:
        # The precondition owner's refusal, in the document's own voice. Not a
        # traceback and not a drawing: G-OR-7 keeps the report buildable over a
        # half-filled project, and §3.4 makes it say what is missing.
        return Figure(key=key, title=title,
                      absent_reason=(f"the {printed.lower()} planform cannot be "
                                     f"drawn as entered -- {problem}"))
    drawn = []
    # ``zip`` stops at the shorter: a parent grown a third control surface would
    # lose it silently, so ``test_oracle_report.py`` holds every spec's child
    # count against the number of fills there are to tell them apart with.
    for child, style in zip(children, REGION_STYLES):
        try:
            child_series = _region_series(project, child, style,
                                          _region_label(child, areas.get(child)),
                                          mirror, frame, scale)
        except ValueError:
            # A control surface mid-entry costs the reader the shading, not the
            # parent's planform, which is the figure they came for.
            continue
        if child_series:
            drawn.append(child)
            series += child_series

    x_label, y_label = _PLANFORM_AXES[frame]
    entered = list(surface.leading_edge) + list(surface.trailing_edge)
    if mirror:
        entered += [(x, -y) for x, y in entered]
    points = [("",) + _oriented(frame, x * scale, y * scale)
              for x, y in entered]

    caption = [
        f"The {printed.lower()} as entered, drawn to scale on equal axes: the "
        "outline is the leading- and trailing-edge polylines the analysis "
        "integrated, and the marked points are the entered vertices.",
    ]
    if drawn:
        names = [_REGION_NAMES.get(c, c).lower() for c in drawn]
        named = (names[0] if len(names) == 1
                 else ", ".join(names[:-1]) + " and " + names[-1])
        caption.append(f"The {named} is shaded on it." if len(names) == 1
                       else f"The {named} are shaded on it.")
    caption.append(
        "Areas are the values tabulated above, not measured off the drawing. "
        "Nothing here is a load: no value is scaled to ultimate and none "
        "carries a safety factor.")
    if mirror:
        caption.append("The surface is symmetric about the airplane centre "
                       "plane and both sides are drawn.")
    caption.append(
        "The hinge line is not drawn: the analysis carries the control "
        "surface's areas forward and aft of the hinge as scalars and no hinge "
        "geometry, so a line here would be an inference rather than the "
        "configuration.")

    return Figure(
        key=key, title=title,
        data=PlotData(f"{x_label} ({length_units})",
                      f"{y_label} ({length_units})", series, points),
        caption=" ".join(caption))


def _geometry(project: Project,
              results: Mapping[str, Optional[ModuleResult]], *,
              system: UnitSystem,
              plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    conditions = _conditions(results.get("configuration_layout"), system)
    planform = _find(conditions, _GEOMETRY_CONDITION)

    # Wing area is produced by structural_speeds, not by the geometry module,
    # but it is geometry and this is where a reader looks for it. Taken from the
    # producing result rather than recomputed, and omitted from the section 2.3
    # table so the document states it once.
    speeds = _conditions(results.get("structural_speeds"), system)
    area = _by_key(_find(speeds, "Structural design speeds")).get("wing_area_s")

    table = _value_table("Wing planform geometry", planform)
    if table is not None and area is not None:
        formatted, units = _cell(area)
        table.rows.append([area.label, formatted, units])

    body = [
        "The wing planform the spanwise loads of the following sections are "
        "distributed over. The mean aerodynamic chord and its leading-edge "
        "station are the strip integrations of the planform itself, not "
        "closed-form approximations to it.",
    ]
    far = _far_note(planform)
    if far:
        body.append(far)
    body.append(
        "The empennage and control surfaces follow, with the areas and control "
        "deflections the analysis was given. " + _AS_ENTERED_SENTENCE)
    if any(_planform_assumed(project, component)
           for component in ("htail", "vtail")):
        body.append(
            "Where a tail table below states a DERIVED planform, that surface "
            "has no entered leading- and trailing-edge polylines and is treated "
            "as a rectangle of its stated area and span. A tapered surface "
            "carries its load further inboard, so the root bending reported "
            "later is conservative, while the station-by-station distribution "
            "is not the surface's own. Entering the polylines removes the "
            "assumption.")

    empennage = getattr(project.geometry, "empennage", None) if project.geometry else None
    tables = [table]
    tables.append(_tail_table("Horizontal tail and elevator", project, "htail",
                              getattr(empennage, "htail", None),
                              _HTAIL_ROWS, system))
    tables.append(_tail_table("Vertical tail and rudder", project, "vtail",
                              getattr(empennage, "vtail", None),
                              _VTAIL_ROWS, system))
    tables.append(_input_table("Aileron", project.aileron_loads,
                               _AILERON_ROWS, system))
    tables.append(_input_table("Flap", project.flap_loads, _FLAP_ROWS, system))
    for tab in getattr(project.tab_loads, "tabs", ()) or ():
        key = (getattr(tab, "surface", "") or "").strip()
        surface = _SURFACE_NAMES.get(key, key)
        tables.append(_input_table(
            f"Trim tab, {surface}" if surface else "Trim tab",
            tab, _TAB_ROWS, system))

    # One planform per main surface (OR-45). The renderer puts a section's
    # figures ahead of its tables, so the three drawings open 2.1 and the tables
    # that state their numbers follow -- the reader sees the airplane before the
    # arithmetic, which is the order the section was asked for in.
    areas = _region_areas(project, area, system)
    figures = [_planform_figure(project, key, parent, figure_title, children,
                                frame, areas, system)
               for key, parent, figure_title, children, frame in _PLANFORM_FIGURES]
    return Section("", body=body, figures=figures,
                   tables=[t for t in tables if t is not None])


# --------------------------------------------------------------------------- #
# 2.2 Weight and mass properties
# --------------------------------------------------------------------------- #
#: The order analyses are listed in, so a set never reaches the page unsorted.
#:
#: ``CgCase.analyses`` is a ``set`` by design (G-3), and set iteration order is
#: not a document property. Printing it directly would put the determinism gates
#: G-OR-5 and G-OR-16 at the mercy of hash ordering.
_ANALYSIS_ORDER = (AnalysisKind.FLIGHT, AnalysisKind.GROUND)

#: What the role and analysis columns of the CG-case table mean.
_CG_CASE_NOTE = (
    "ANALYSIS is which load families a case is carried into. A flight case "
    "feeds the V-n envelope, the balancing tail loads and the selected design "
    "cases; a ground case feeds the landing and ground-handling families "
    "(14 CFR 23.471-23.511). The two are separate governing families and are "
    "never compared for a maximum. A case may carry both tags. "
    "ROLE applies to ground cases only: the landing-load analysis takes exactly "
    "three loadings and indexes them by position, so the role states which of "
    "the three a case supplies -- aft max landing, forward max landing or "
    "forward light -- rather than leaving it to be recovered from the case "
    "name. A further ground case carrying no role is assembled and distributed "
    "but is not one of the three fed to the landing analysis. "
    "Weight and centre of gravity are the case as entered."
)


def _pct_mac_note(ref: MacReference, u: Units) -> str:
    """The relation the %MAC column applies, and the reference it applies it to.

    Stated rather than assumed: a %MAC is meaningless without the XLEMAC and MAC
    it is measured from, and this suite resolves that pair two ways (a typed
    ``envelope.xlemac``/``mac`` override, else the wing planform of 2.1). A
    reader checking a station against the entered CG limits -- which are given
    in %MAC -- needs to know which pair produced the column and be able to
    invert it, so both forms of the relation are printed.
    """
    length = u.label("length")
    where = ("the entered XLEMAC and MAC, which override the planform"
             if ref.source == "override"
             else f"the {ref.surface_name} planform stated in 2.1")
    return (
        "Xcg (% MAC) is that same station expressed in percent of the mean "
        "aerodynamic chord -- a change of reference, not a second analysis: "
        "%MAC = 100 (X - XLEMAC) / MAC, and inverted, "
        "X = XLEMAC + (%MAC / 100) MAC. Here XLEMAC = "
        f"{u.plain(ref.xlemac, 'length')} {length} and MAC = "
        f"{u.plain(ref.mac, 'length')} {length}, from {where}. The CG limits "
        "drawn in the figure below are entered in %MAC and are converted to "
        "stations through the same relation and the same pair, so a case and a "
        "limit on this page are always measured from one reference."
    )


def _cg_case_table(project: Project, system: UnitSystem) -> Optional[Table]:
    """The weight and CG cases analysed, one row each."""
    weight = project.weight
    cases = list(getattr(weight, "cg_cases", ()) or ()) if weight else []
    if not cases:
        return None
    u = Units(system)
    # The one resolver (C210-13) -- never a second reading of the planform
    # here. A degenerate MAC is treated as unresolved rather than divided by:
    # ``station_to_pct_mac`` answers 0.0 on it, which would print a column of
    # zeroes that looks like an answer.
    ref = mac_reference(project)
    if ref is not None and not ref.mac:
        ref = None
    rows = []
    for case in cases:
        analyses = [kind.value for kind in _ANALYSIS_ORDER
                    if kind in (case.analyses or ())]
        role = getattr(case, "role", None)
        rows.append([
            case.name or "unnamed",
            role.value.replace("_", " ") if role is not None else "--",
            u.plain(case.weight_lb, "mass"),
            u.plain(case.xcg, "length"),
            # ``case.xcg`` is internal inches and a percentage is dimensionless,
            # so this converts once, through the relation's owner, and not again.
            format_value(station_to_pct_mac(case.xcg, ref)) if ref else "--",
            u.plain(case.zcg, "length"),
            ", ".join(analyses) or "--",
        ])
    length = u.label("length")
    note = _CG_CASE_NOTE
    note += (" " + _pct_mac_note(ref, u) if ref is not None else
             " Xcg is not stated in %MAC: neither an entered XLEMAC and MAC nor "
             "a wing planform to read them from is present, so there is no "
             "reference to measure a percentage against.")
    return Table(
        title="Weight and centre-of-gravity cases",
        columns=["Case", "Role", f"Weight ({u.label('mass')})",
                 f"Xcg ({length})", "Xcg (% MAC)", f"Zcg ({length})",
                 "Analysis"],
        rows=rows, note=note)


#: What the weight/CG figure states about itself, beyond the caption.
#:
#: G-OR-4: section 2 marks nothing ultimate and states no safety factor. A
#: weight and a station are not load quantities, so the sentence is a statement
#: of fact rather than a disclaimer -- but it is stated, because this is the one
#: figure in section 2 whose axes carry pounds.
_ENVELOPE_NOTE = (
    "The two loading envelopes are the discretionary items of the weight data "
    "base added cumulatively, most-forward first and most-aft first, from the "
    "minimum flight weight. Both begin at that weight and end at the same "
    "full loading, so together they close the envelope of every loading the "
    "airplane can physically hold. The structural limit envelope is the "
    "entered CG limits: constant at the forward-regardless station below the "
    "reduced weight, linear in weight to the forward-gross station at gross "
    "weight, and constant at the aft-gross station. A loading vertex outside "
    "that envelope is expected and is not a defect -- the limits bound the "
    "loadings that may be flown, not those that can be loaded. Weights, "
    "stations and waterlines are not load quantities: nothing here is scaled "
    "to ultimate and no safety factor applies."
)


#: ``(printed edge name, condition-title prefix, LoadValue key prefix)``.
#:
#: WTENV publishes the forward edge under the keys it has carried since the
#: module was written and the aft edge -- added by design note 45 -- under an
#: ``aft_`` prefix, so the two stay distinguishable wherever conditions are
#: flattened together. Declared as data and guarded against the module's own
#: keys, so a renamed key fails the suite instead of silently emptying the table.
_ENVELOPE_EDGES = (("Forward", "Forward loading envelope", "point"),
                   ("Aft", "Aft loading envelope", "aft_point"))


def _envelope_vertex_table(result: Optional[ModuleResult],
                           system: UnitSystem) -> Optional[Table]:
    """The plotted vertices, numbered as the figure numbers them.

    The figure marks vertices and the table names their coordinates; a reader
    checking a corner against a number should not have to measure it off an
    axis. Read from WTENV's own ``ModuleResult`` (G-OR-3) rather than swept
    here. Which *item* each vertex adds is not stated because the analysis does
    not carry it -- see the note below the table.
    """
    conditions = _conditions(result, system)
    u = Units(system)
    rows = []
    for edge, title, prefix in _ENVELOPE_EDGES:
        condition = _find(conditions, title)
        if condition is None:
            continue
        by_index: Dict[int, Dict[str, float]] = {}
        for value in condition.values:
            parts = (value.key or "").rsplit("_", 1)
            stem, field = (parts + [""])[:2]
            if not stem.startswith(f"{prefix}_"):
                continue
            try:
                index = int(stem[len(prefix) + 1:])
            except ValueError:
                continue
            by_index.setdefault(index, {})[field] = value.value
        for index in sorted(by_index):
            cell = by_index[index]
            if not {"weight", "station"} <= set(cell):
                continue
            waterline = cell.get("waterline")
            # ``_conditions`` has already converted to the document's system,
            # so these format only -- ``u.plain`` would convert a second time.
            # The vertex names itself ("Forward 4") rather than carrying a bare
            # ordinal in its own column: an ordinal is not a quantity, and a
            # column of naked integers beside three of measurements invites the
            # reader to read one as the other.
            rows.append([f"{edge} {index}", format_value(cell["weight"]),
                         format_value(cell["station"]),
                         format_value(waterline) if waterline is not None
                         else "--"])
    if not rows:
        return None
    length = u.label("length")
    return Table(
        title="Loading envelope vertices",
        columns=["Vertex", f"Weight ({u.label('mass')})",
                 f"Station ({length})", f"Waterline ({length})"],
        rows=rows,
        note="Vertex 1 is the minimum flight weight on both edges; each "
             "subsequent vertex adds one discretionary item, in fuselage-station "
             "order. The item added at a vertex is not stated: the analysis "
             "reports the cumulative weight and centre of gravity, not the "
             "loading behind them. The items and their stations are listed in "
             "the weight data base above, in the order the vertices follow.",
    )


def _weight_cg_figure(project: Project, system: UnitSystem) -> Figure:
    """Section 2.2's weight/CG envelope -- both edges, limits, entered cases."""
    data = weight_cg_plot_data(project, Units(system))
    if data is None:
        return Figure(
            "weight_cg", "Weight and centre-of-gravity envelope",
            absent_reason="this airplane has no itemized weight data base, so "
                          "there are no loadings to sweep and no envelope to draw",
        )
    marked = (" Each entered weight and centre-of-gravity case is marked; two "
              "cases at the same weight and station share one marker and both "
              "names." if data.points else "")
    limits = ("" if any(s.name == "Structural limits" for s in data.series)
              else " No structural limit envelope is drawn: the CG limits are "
                   "not entered for this airplane.")
    return Figure(
        "weight_cg", "Weight and centre-of-gravity envelope",
        data=data,
        caption="Weight against centre-of-gravity station for every loading of "
                "the weight data base, with the structural limit envelope."
                + marked + limits,
    )


def _weights(project: Project,
             results: Mapping[str, Optional[ModuleResult]], *,
             system: UnitSystem,
             plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    conditions = _conditions(results.get("weight_mass"), system)
    tables = []
    for condition in conditions:
        # The module's condition title names the analysis ("...for one
        # loading"), which is our machinery describing itself. With a single
        # loading the document says what the table *is*; with several, the
        # condition title is the only thing that tells them apart and is kept.
        title = ("Mass properties" if len(conditions) == 1
                 else f"Mass properties -- {condition.title}")
        table = _value_table(title, condition)
        if table is not None:
            tables.append(table)
    cases = _cg_case_table(project, system)
    if cases is not None:
        tables.append(cases)
    vertices = _envelope_vertex_table(results.get("weight_envelope"), system)
    if vertices is not None:
        tables.append(vertices)

    body = [
        "The weight, centre of gravity and mass moments of inertia of each "
        "loading analysed. The inertias are stated twice, in slug-ft^2 and in "
        "lb-in^2, because the two conventions are both current and a factor of "
        "12^2 between them is not a difference a reader should have to detect. "
        "The principal-axis set and its inclination follow; the angle is "
        "measured up from the waterline and aft from the centre of gravity.",
        _ENVELOPE_NOTE,
    ]
    far = _far_note(conditions[0] if conditions else None)
    if far:
        body.append(far)
    return Section("", body=body, tables=tables,
                   figures=[_weight_cg_figure(project, system)])


# --------------------------------------------------------------------------- #
# 2.3 Structural design speeds
# --------------------------------------------------------------------------- #
#: ``(printed name, as-computed key, FAR-minimum key)`` for the paired tables.
#:
#: The pairing is the section's whole point: a design speed or a limit load
#: factor means nothing to a reviewer without the regulation's floor beside it.
#: Declared as data and guarded against the module's own value keys, so a
#: renamed or dropped result key fails the suite instead of silently emptying a
#: compliance column.
_FACTOR_PAIRS: Tuple[Tuple[str, str, str], ...] = (
    ("Positive limit manoeuvre load factor", "limit_positive_load_factor",
     "minimum_required_positive_factor"),
    ("Negative limit manoeuvre load factor", "limit_negative_load_factor",
     "minimum_required_negative_factor"),
)

_SPEED_PAIRS: Tuple[Tuple[str, str, str], ...] = (
    ("Design manoeuvring speed VA", "maneuver_speed_va", "minimum_maneuver_va_min"),
    ("Design cruising speed VC", "cruise_speed_vc", "minimum_cruise_vc_min"),
    ("Design dive speed VD", "dive_speed_vd", "minimum_dive_vd_min"),
    ("Design flap speed VF", "flap_speed_vf", "minimum_flap_vf_min"),
)


def _paired_table(title: str, condition: Optional[ConditionResult],
                  pairs: Sequence[Tuple[str, str, str]]) -> Optional[Table]:
    """As-computed beside the regulation's minimum, one row per pair.

    No verdict column: whether a value complies is the reviewer's finding, and a
    generator that printed "complies" would be asserting a conclusion it is not
    the authority for. The two numbers side by side are the evidence.
    """
    values = _by_key(condition)
    rows = []
    for name, computed_key, minimum_key in pairs:
        computed = values.get(computed_key)
        minimum = values.get(minimum_key)
        if computed is None:
            continue
        formatted, units = _cell(computed)
        floor = _cell(minimum)[0] if minimum is not None else ""
        rows.append([name, formatted, floor, units])
    if not rows:
        return None
    # A units column every row leaves blank is dropped rather than printed
    # empty. The limit manoeuvre load factors are the case that found this: n
    # is dimensionless -- the section body says so, and "g" would name an
    # acceleration this table does not state -- so the column carried nothing
    # but the suggestion that a unit had gone missing. Done here rather than at
    # the one table, so any dimensionless pairing added later behaves the same.
    if not any(row[3] for row in rows):
        return Table(title=title,
                     columns=["Quantity", "As computed", "FAR 23 minimum"],
                     rows=[row[:3] for row in rows])
    return Table(title=title,
                 columns=["Quantity", "As computed", "FAR 23 minimum", "Units"],
                 rows=rows)


def _speeds(project: Project,  # noqa: ARG001
            results: Mapping[str, Optional[ModuleResult]], *,
            system: UnitSystem,
            plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    conditions = _conditions(results.get("structural_speeds"), system)
    factors = _find(conditions, "Limit maneuver load factors")
    speeds = _find(conditions, "Structural design speeds")
    mach = _find(conditions, "Cruise/dive Mach")

    # Everything the paired table already states, plus the wing area printed in
    # section 2.1 -- so no number appears in two tables.
    paired_keys = [key for _n, a, b in _SPEED_PAIRS for key in (a, b)]
    tables = [
        _paired_table("Limit manoeuvre load factors", factors, _FACTOR_PAIRS),
        _value_table("Wing loading", factors,
                     skip=[key for _n, a, b in _FACTOR_PAIRS for key in (a, b)]),
        _paired_table("Structural design speeds", speeds, _SPEED_PAIRS),
        _value_table("Cruise and dive Mach numbers", mach),
    ]
    if speeds is not None:
        leftover = _value_table("Design speed reference values", speeds,
                                skip=paired_keys + ["wing_area_s"])
        if leftover is not None:
            tables.append(leftover)

    body = [
        "The limit manoeuvre load factors and structural design speeds the "
        "flight envelope is built on, each stated beside the minimum 14 CFR "
        "Part 23 Subpart C requires of it. Speeds are equivalent airspeeds; "
        "load factors are dimensionless and are LIMIT values.",
    ]
    far = _far_note(speeds)
    if far:
        body.append(far)
    return Section("", body=body, tables=[t for t in tables if t is not None])


# --------------------------------------------------------------------------- #
# 2.4 Flight envelope
# --------------------------------------------------------------------------- #
#: The envelope boundary, in traversal order, by the case names FLTLOADS emits.
#:
#: These nine cases are the boundary itself; the balance, rolling and asymmetric
#: cases the same module produces sit inside it and belong to the load-case
#: section. The order is a closed traversal from the 1 g stall up the positive
#: boundary, across the dive line and back along the negative one -- guarded
#: against the module's own emission order, so this declaration cannot come to
#: disagree with the analysis about which way the envelope goes.
_BOUNDARY_CASES: Tuple[str, ...] = (
    "STALL 1G", "STALL +N", "MAN A", "MAN C", "MAN D",
    "MAN -D", "MAN -C", "STALL -N", "STALL -1G",
)

#: The gust cases, drawn as marked points rather than joined into the boundary.
#:
#: They are separate design points, not vertices of the manoeuvre envelope, and
#: joining them would draw a boundary the analysis never computed.
_GUST_CASES: Tuple[str, ...] = ("GUST +C", "GUST +D", "GUST -D", "GUST -C")

#: ``(printed name, case name, value key)`` of the corner table's columns.
_CORNERS: Tuple[Tuple[str, str], ...] = (
    ("n+ at VA", "MAN A"),
    ("n+ at VD", "MAN D"),
    ("n- at VC", "MAN -C"),
    ("n- at VD", "MAN -D"),
)

#: The reference speeds drawn as vertical lines, by structural_speeds' keys.
_ENVELOPE_VLINES: Tuple[Tuple[str, str], ...] = (
    ("VA", "maneuver_speed_va"),
    ("VC", "cruise_speed_vc"),
    ("VD", "dive_speed_vd"),
)


#: How every V-n diagram in 2.4 is constructed -- stated once, above them.
#:
#: It was each figure's caption until 2026-08-31, which printed the same three
#: sentences under four figures that differ only in their loading. A caption
#: distinguishes a figure; this describes all of them, so it belongs to the
#: subsection and the caption line is left carrying the block name alone.
_VN_CONSTRUCTION = (
    "Each boundary is drawn through the design points the analysis computed and "
    "is curved between them: the stall boundary follows the section lift curve "
    "and the compressibility correction, not a constant-CLmax parabola. Gust "
    "points are design points in their own right and are not vertices of the "
    "manoeuvre boundary. Load factors are LIMIT and dimensionless."
)


def _split_case(title: str) -> Tuple[str, str]:
    """``"CRUISE CG1 @ 0 ft, case 3: MAN A"`` -> ``("CRUISE CG1 @ 0 ft", "MAN A")``.

    Returns ``("", "")`` for a title that is not a case, so a module that grows
    a summary condition does not become a phantom envelope block.
    """
    block, _, rest = title.partition(", case ")
    if not rest:
        return "", ""
    _number, _, name = rest.partition(": ")
    return (block, name) if name else ("", "")


def _blocks(conditions: Sequence[ConditionResult],
            ) -> List[Tuple[str, Dict[str, ConditionResult]]]:
    """The envelope's loading/altitude blocks, in order, each keyed by case name."""
    order: List[str] = []
    found: Dict[str, Dict[str, ConditionResult]] = {}
    for condition in conditions:
        block, case = _split_case(condition.title)
        if not block:
            continue
        if block not in found:
            order.append(block)
            found[block] = {}
        found[block][case] = condition
    return [(block, found[block]) for block in order]


def _point(condition: ConditionResult) -> Optional[Tuple[float, float]]:
    """``(V, n)`` for one case, or ``None`` when either is missing."""
    values = _by_key(condition)
    speed = values.get("v_eas")
    factor = values.get("load_factor_nz")
    if speed is None or factor is None:
        return None
    return float(speed.value), float(factor.value)


def _envelope_figure(block: str, cases: Mapping[str, ConditionResult],
                     vlines: Sequence[Tuple[str, float]], index: int) -> Figure:
    """One block's V-n diagram: boundary polyline, gust points, speed lines."""
    boundary = [_point(cases[name]) for name in _BOUNDARY_CASES if name in cases]
    joined = [p for p in boundary if p is not None]
    series = []
    if joined:
        # Closed: back to the first vertex, so the envelope reads as a boundary
        # rather than an open path that happens to end near where it began.
        closed = joined + [joined[0]]
        series.append(Series("Manoeuvre and stall boundary",
                             [v for v, _n in closed], [n for _v, n in closed],
                             "solid"))
    points = []
    for name in _GUST_CASES:
        condition = cases.get(name)
        if condition is None:
            continue
        point = _point(condition)
        if point is not None:
            points.append((name, point[0], point[1]))
    # No caption. What the four V-n figures would each say is the same sentence
    # about the same construction, and a caption repeated once per loading is
    # not a caption but a refrain -- it is stated once in the subsection body
    # (:data:`_VN_CONSTRUCTION`) instead. The block is in the title, which is
    # what distinguishes one figure from another and all the caption line needs
    # to carry (owner, 2026-08-31).
    return Figure(
        key=f"vn_{index}",
        title=f"Flight envelope -- {block}",
        data=PlotData("V (KEAS)", "Load factor n", series, points, list(vlines),
                      points_label="Gust design points"),
    )


def _corner_table(blocks: Sequence[Tuple[str, Dict[str, ConditionResult]]],
                  ) -> Optional[Table]:
    """The manoeuvre corner load factors, one row per block."""
    rows = []
    for block, cases in blocks:
        row = [block]
        for _name, case in _CORNERS:
            condition = cases.get(case)
            point = _point(condition) if condition is not None else None
            row.append(format_value(point[1]) if point is not None else "")
        rows.append(row)
    if not rows:
        return None
    return Table(
        title="Manoeuvre envelope corner load factors",
        columns=["Loading and altitude"] + [name for name, _c in _CORNERS],
        rows=rows,
        note="Dimensionless LIMIT load factors, read from the design cases "
             "plotted above. The negative boundary closes to zero at the dive "
             "speed (14 CFR 23.333(d)), so the n- at VD column is that closure "
             "point and is zero to within the solution tolerance of the balance "
             "it was found by; it is reproduced as computed rather than "
             "rounded.")


#: ``(printed name, MACHLIM value key)`` of the speed/altitude table's columns.
#:
#: Guarded against the module's own keys, so a renamed key empties the table in
#: the suite rather than on the page.
_MACH_LIMIT_COLUMNS: Tuple[Tuple[str, str], ...] = (
    ("V(MC) cruise", "v_mc"),
    ("V(MNE) never-exceed", "v_mne"),
    ("V(MD) dive", "v_md"),
)


def _speed_altitude_figure(project: Project) -> Figure:
    """2.4's first figure: the operating envelope in speed and altitude.

    Placed ahead of the V-n diagrams because it is the envelope the V-n
    diagrams are cut from: each one is a slice at a stated altitude, and the
    speeds their boundaries run to are the speeds this figure draws.

    One builder, shared with the summary report (OR-7) --
    :func:`sloads.report.content.speed_altitude_plot_data`.
    """
    data = speed_altitude_plot_data(project)
    if data is None:
        return Figure(
            "speed_altitude", "Speed and altitude envelope",
            absent_reason="this airplane has no Mach-limited boundary -- no "
                          "MACHLIM inputs are entered, so the operating envelope "
                          "is bounded by the design speeds of 2.3 alone",
        )
    return Figure(
        "speed_altitude", "Speed and altitude envelope",
        data=data,
        caption="The operating envelope from sea level to the maximum operating "
                "altitude. Each boundary is constant in equivalent airspeed below "
                "the shoulder altitude and Mach-limited above it, so the kink in "
                "each line is the shoulder. Vh is marked at sea level, where it is "
                "entered: it is the maximum level-flight speed, not a limit, and "
                "the analysis carries no altitude variation of it. Speeds are "
                "equivalent airspeeds and are LIMIT design speeds; nothing here "
                "is scaled to ultimate.",
    )


def _mach_limit_table(result: Optional[ModuleResult],
                      system: UnitSystem) -> Optional[Table]:
    """The plotted speed/altitude boundaries, from MACHLIM's own result.

    The figure's numeric corners (SS 4.3), read rather than re-derived (G-OR-3).
    Only the Mach-limited rows are tabulated: below the shoulder each speed is
    its shoulder value held constant, which the note states rather than the
    table repeating it as though it were a further computed row.
    """
    rows = []
    units = ""
    for condition in _conditions(result, system):
        values = _by_key(condition)
        if "altitude" not in values:
            continue
        row = [format_value(values["altitude"].value)]
        for _name, key in _MACH_LIMIT_COLUMNS:
            value = values.get(key)
            row.append(format_value(value.value) if value is not None else "")
            if value is not None and not units:
                units = value.units
        rows.append(row)
    if not rows:
        return None
    speed = f" ({units})" if units else ""
    return Table(
        title="Mach-limited speeds by altitude",
        columns=["Altitude (ft)"] + [f"{name}{speed}"
                                     for name, _key in _MACH_LIMIT_COLUMNS],
        rows=rows,
        note="The Mach-limited half of the figure above, from the shoulder "
             "altitude to the maximum operating altitude. Below the shoulder "
             "each boundary is constant in equivalent airspeed at its value in "
             "the first row, which is what the shoulder altitude is: the "
             "altitude at which an EAS limit becomes a Mach limit. MNE = 0.9 MD "
             "(Ch 6). These are LIMIT design speeds.",
    )


def _envelope(project: Project,
              results: Mapping[str, Optional[ModuleResult]], *,
              system: UnitSystem,
              plan: Sequence[SectionPlan]) -> Section:
    conditions = _conditions(results.get("flight_envelope"), system)
    blocks = _blocks(conditions)

    speeds = _by_key(_find(_conditions(results.get("structural_speeds"), system),
                           "Structural design speeds"))
    vlines = [(name, float(speeds[key].value))
              for name, key in _ENVELOPE_VLINES if key in speeds]

    # The speed/altitude envelope opens the subsection: the V-n diagrams that
    # follow are slices of it, and a reader meets the envelope before its cuts.
    figures = [_speed_altitude_figure(project)]
    figures += [_envelope_figure(block, cases, vlines, index)
                for index, (block, cases) in enumerate(blocks)]
    table = _corner_table(blocks)
    mach = _mach_limit_table(results.get("mach_limit"), system)

    cases_ref = section_ref(plan, "flight_envelope_cases")
    body = [
        "The operating envelope in speed and altitude, and then the flight "
        "envelope itself, one diagram per loading and altitude analysed. "
        "Each diagram shows the manoeuvre and stall boundary of that "
        "condition together with the gust design points at the cruise and dive "
        "speeds, against the design speeds of the preceding section.",

        _VN_CONSTRUCTION,

        "The design cases selected on these envelopes -- the speed, load factor, "
        "attitude and balance of each condition carried into the component load "
        f"analyses -- are tabulated in {cases_ref}.",
    ]
    far = _far_note(conditions[0] if conditions else None)
    if far:
        body.append(far)
    return Section("", body=body, figures=figures,
                   tables=[t for t in (mach, table) if t is not None])


# --------------------------------------------------------------------------- #
# Section 3 -- Wing Loads (OR-48 ... OR-56)
# --------------------------------------------------------------------------- #
#: The step whose result this section reports, named once.
_WING_STEP = "wing_loads"

#: Positions of the subsections other prose points at, so a cross-reference is
#: composed from the numbering owner rather than typed as "3.1" (F-R2).
_WING_INPUTS = 0
_WING_CASES = 1
_WING_ASSESSED = 2
_WING_DISTRIBUTIONS = 3


def _load_cell(value: LoadValue, sf: float) -> Tuple[str, str]:
    """``(formatted value, units)`` for one **load**, through the boundary.

    :func:`_cell`'s sibling, and deliberately a separate function rather than a
    parameter on it. Section 2 passes ``sf=1.0`` because it holds no loads and a
    factor there would encode a claim it does not make (OR-44).

    **The boundary no longer scales** (note 49 OR-89/OR-116): the value printed
    is the calc's own and the case's factor is stated in the table's ``SF``
    column. This is what lets the report be read against Appendix A, which is a
    **limit** oracle — the defect note 49 E-c found was §3 printing 1.5x the
    manual's figures with every oracle test still green, because the oracle
    tests compare below this line and never cross it.

    A load computed already ultimate keeps its ``-ULT`` marker (OR-118); section
    2's ``sf=1.0`` cannot trip that, because it passes no loads.
    """
    marked = ultimate_units(value.units, value.quantity) if sf == 1.0 else value.units
    return format_value(value.value), marked


def _required_sf(condition) -> float:
    """The case's factor, refusing a condition that prescribes none.

    These tables render load cases only, so ``None`` here is a defect upstream
    rather than a cell to render — the same loud failure the render boundary
    takes (OR-82). (Note 48 OR-78 made the report ULTIMATE; note 49 OR-116 made
    it LIMIT like everything else. Either way a load case has a factor and a
    non-load case is not in this table.)
    """
    sf = condition.safety_factor
    if sf is None:
        raise ValueError(
            f"{condition.title!r} (FAR {condition.far_reference}) prescribes no "
            "safety factor but is rendered in a load-case report table; see "
            "sloads.safety_factors.prescribes_factor (design note 48)")
    return sf


def _wing_net(project: Project) -> List[WingLoadResult]:
    """The net wing load distributions, transferred to the surface's LRA.

    Asked of ``net_loads``' own builders -- the same pair the Export page and the
    summary report call -- so the section, the appendix and the exported deck
    describe one set of numbers. Returns ``[]`` rather than raising: G-OR-7 keeps
    a half-filled project building a complete document, and the callers turn an
    empty list into a stated absence.
    """
    from ..modules.net_loads import build_net_loads, loads_ref_axis_results

    try:
        net = build_net_loads(project)
        return list(loads_ref_axis_results(project, net.wing_net))
    except Exception:
        return []


def _torsion_axis(results: Sequence[object]) -> str:
    """What the distributions' torsion is stated about, from the results."""
    return str(getattr(results[0], "torsion_axis", "")) if results else ""


def _wing_surface_name(project: Project) -> str:
    """The surface the wing-load chain runs on, as WINGINER names it."""
    return getattr(project.wing_mass, "surface", "wing") or "wing"


_LRA_NOTE = (
    "The loads reference axis (LRA) is the chordwise line every distributed "
    "load in this section is stated about: the shears and bending moments are "
    "unaffected by the choice, and the torsion is not. The replicated "
    "programs accumulate torsion about the local 25 per cent chord, so for the "
    "oracle the LRA is the quarter chord; in this suite the axis is entered per "
    "surface, and the torsion is transferred to it at the delivery boundary by "
    "Myy(LRA) = Myy(25%) + Sz (X(LRA) - X(25%)). The table gives the axis "
    "point at each load station and the figure draws it on the planform, so the "
    "axis a torsion is measured about can be read off the airplane rather than "
    "assumed."
)


def _lra_station_table(net: Sequence[object],
                       system: UnitSystem) -> Optional[Table]:
    """The loads reference axis, station by station.

    The axis coordinates are the transferred results' own station points -- the
    transform's output, not a second reading of the planform (OR-6). Coordinates
    are geometry: nothing here is scaled to ultimate and nothing is marked.
    """
    if not net:
        return None
    stations = list(getattr(net[0], "stations", ()))
    if not stations:
        return None
    u = Units(system)
    length = u.label("length")
    rows = [[str(index), u.plain(s.y, "length"), u.plain(s.x, "length"),
             u.plain(s.z, "length")]
            for index, s in enumerate(stations, start=1)]
    axis = _torsion_axis(net)
    return Table(
        title=f"Loads reference axis by station ({axis})",
        columns=["Station", f"Butt line Y ({length})",
                 f"Station X on the axis ({length})", f"Waterline Z ({length})"],
        rows=rows,
        note=("The stations are the load stations the air-load and inertia "
              "distributions are evaluated at, root to tip. These are "
              "coordinates, not loads: nothing in this table is scaled to "
              "ultimate and nothing carries a safety factor."))


def _lra_planform_figure(project: Project, net: Sequence[object],
                         system: UnitSystem) -> Figure:
    """The wing planform with its loads reference axis drawn on it."""
    from .planform_tex import LRA_STYLE, OUTLINE_STYLE

    key, title = "planform_wing_lra", "Wing loads reference axis"
    name = _wing_surface_name(project)
    surface = project.geometry.by_name(name) if project.geometry else None
    if surface is None:
        return Figure(key=key, title=title,
                      absent_reason=("the project defines no wing planform, so "
                                     "there is no surface to draw an axis on."))
    if not net:
        return Figure(key=key, title=title,
                      absent_reason=("the wing load distributions were not "
                                     "produced, so the axis they are stated "
                                     "about cannot be drawn."))
    scale, length_units = _length_channel(system)
    mirror = bool(surface.symmetric)
    try:
        series = _region_series(project, name, OUTLINE_STYLE, "Wing planform",
                                mirror, "butt", scale)
    except ValueError as problem:
        return Figure(key=key, title=title,
                      absent_reason=("the wing planform cannot be drawn as "
                                     f"entered -- {problem}"))
    axis = _torsion_axis(net)
    stations = list(getattr(net[0], "stations", ()))
    points = [_oriented("butt", s.x * scale, s.y * scale) for s in stations]
    series.append(Series(f"Loads reference axis ({axis})" if axis
                         else "Loads reference axis",
                         [x for x, _y in points], [y for _x, y in points],
                         LRA_STYLE))
    if mirror:
        series.append(Series("", [-x for x, _y in points],
                             [y for _x, y in points], LRA_STYLE))
    x_label, y_label = _PLANFORM_AXES["butt"]
    return Figure(
        key=key, title=title,
        data=PlotData(f"{x_label} ({length_units})",
                      f"{y_label} ({length_units})", series,
                      [("", x, y) for x, y in points],
                      # Named, or the marker inherits the V-n figure's default
                      # and this figure's stations are legended "Design CG
                      # cases" -- a legend naming a different figure entirely,
                      # which is the defect ``points_label`` was added for.
                      points_label="Load stations"),
        caption=("The wing as entered, with the loads reference axis of this "
                 f"analysis ({axis}) drawn through the load stations every "
                 "distributed load in this section is stated at. The marked "
                 "points are those stations. Nothing in this figure is a load."))


#: The wing lift coefficients the span load is drawn at, and how each is named.
#:
#: ``None`` means *the airplane's own CLmax*, taken from the aero set's
#: ``stall_cl`` rather than typed here: a span load drawn to a constant somebody
#: chose would be a plot of this module's opinion (OR-52).
_SPAN_LOAD_CASES: Tuple[Tuple[str, Optional[float]], ...] = (
    ("CL = 0 (basic distribution)", 0.0),
    ("CL = 1.0", 1.0),
    ("CL = CLmax", None),
)

_SPAN_LOAD_STYLES = ("dotted", "solid", "dashed")


def _wing_aero_row(project: Project):
    """The aero input row the wing's span load is built from, or ``None``."""
    from ..models import same_name
    from ..modules.airloads import resolve_aero_surfaces

    name = _wing_surface_name(project)
    try:
        rows = resolve_aero_surfaces(project)
    except Exception:
        return None
    for row in rows:
        if same_name(row.name, name):
            return row
    return None


def _span_load_figure(project: Project, clmax: Optional[float],
                      system: UnitSystem) -> Figure:
    """``c*cl`` along the span at the three reference lift coefficients.

    Each curve is AIRLOADS' own distribution evaluated at a target ``CL`` -- the
    report calls the owner once per coefficient rather than combining the
    additive and basic parts itself, which is what keeps a three-curve figure
    inside OR-6.

    **These are LIMIT.** A span load at a target ``CL`` is an input to the load
    cases below, not a delivered load, so it is neither scaled nor marked -- and
    it says so, because a figure in a section whose every other number is
    LIMIT must not leave the reader to assume which kind this is (OR-49, OR-94a).
    """
    from dataclasses import replace as _replace

    from ..modules.airloads import schrenk_distribution

    key, title = "wing_span_load", "Wing span loading (LIMIT)"
    name = _wing_surface_name(project)
    surface = project.geometry.by_name(name) if project.geometry else None
    aero = _wing_aero_row(project)
    if surface is None or aero is None:
        return Figure(key=key, title=title,
                      absent_reason=("the project carries no wing planform and "
                                     "aerodynamic row to distribute a lift "
                                     "coefficient over."))
    u = Units(system)
    series: List[Series] = []
    for (label, target), style in zip(_SPAN_LOAD_CASES, _SPAN_LOAD_STYLES):
        cl = clmax if target is None else target
        if cl is None:
            continue
        try:
            table = schrenk_distribution(surface, _replace(aero, target_cl=cl))
        except Exception:
            continue
        printed = (label if target is not None
                   else f"CL = CLmax = {format_value(cl)}")
        series.append(Series(
            printed,
            [u.plain_value(y, "length") for y in table.ye],
            [u.plain_value(v, "length") for v in table.ccl_total], style))
    if not series:
        return Figure(key=key, title=title,
                      absent_reason=("the wing span load could not be "
                                     "distributed from the planform and "
                                     "aerodynamic data as entered."))
    length = u.label("length")
    return Figure(
        key=key, title=title,
        data=PlotData(f"Butt line Y ({length})", f"Span load c*cl ({length})",
                      series),
        caption=("The Schrenk span load along the semi-span at three wing lift "
                 "coefficients: the basic distribution alone, which carries no "
                 "net lift but is not zero locally; unit CL; and the airplane's "
                 "own CLmax. This is span load c*cl, not running load -- it is "
                 "the shape the air load is distributed to, and it is an input "
                 "to the cases below. All three curves are LIMIT: no safety "
                 "factor is applied to any of them."))


def _flaps_down_span_load(project: Project) -> Figure:
    """The flaps-down span load -- stated absent, with the reason (OR-53)."""
    flaps = getattr(project.aero_coeffs, "flaps_down", None)
    entered = (" This project enters no flaps-down aerodynamic set either."
               if flaps is None else "")
    return Figure(
        key="wing_span_load_flaps",
        title="Wing span loading, flaps down (LIMIT)",
        absent_reason=(
            "the air-load distribution does not model the lift discontinuity a "
            "deflected flap puts in the basic distribution, so a flaps-down "
            "span load is not produced by this analysis at all." + entered))


#: ``(figure key, title, curve attribute, points attribute, y label)`` for the
#: two airplane-coefficient figures 3.1 carries.
_AERO_CURVE_FIGURES: Tuple[Tuple[str, str, str, str, str], ...] = (
    ("aero_cl_alpha", "Airplane-less-tail lift coefficient (LIMIT)",
     "lift", "cl", "CL"),
    ("aero_cm_alpha", "Airplane-less-tail pitching moment (LIMIT)",
     "moment", "cm", "CM"),
)


def _aero_curves(project: Project):
    """``(curves, config)`` for the cruise configuration, or ``(None, None)``.

    Built through :mod:`sloads.aero_curves` -- the single authority the FLTLOADS
    balance itself evaluates -- and overlaid with the balanced points that
    balance produced, so the curve and the points on it cannot come from two
    readings of the same polynomial.
    """
    from ..aero_curves import build_aero_curves, operating_points
    from ..derived_geometry import wing_reference
    from ..modules.flight_envelope import build_envelope

    config = getattr(project.aero_coeffs, "cruise", None)
    if config is None:
        return None, None
    points = None
    try:
        reference = wing_reference(project, _wing_surface_name(project))
        if reference is not None:
            points = operating_points(build_envelope(project), config.name,
                                      wing_area_sqft=reference.s_sqft,
                                      mac_in=reference.mac)
    except Exception:
        points = None
    return build_aero_curves(config, points=points), config


def _aero_curve_figure(curves, config, key: str, title: str,
                       curve_attr: str, point_attr: str, y_label: str) -> Figure:
    """One coefficient curve, with the balanced operating points on it."""
    if curves is None:
        return Figure(key=key, title=title,
                      absent_reason=("the project carries no airplane-less-tail "
                                     "aerodynamic coefficients, so there is no "
                                     "curve to draw."))
    trace = getattr(curves, curve_attr)
    series = [Series(f"Airplane less tail, as entered ({config.name})",
                     list(trace.x), list(trace.y), "solid")]
    points = curves.points
    marked = ([("", a, v) for a, v in zip(points.alpha_deg,
                                          getattr(points, point_attr))]
              if points is not None and len(points) else [])
    return Figure(
        key=key, title=title,
        data=PlotData("Angle of attack (deg)", y_label, series, marked,
                      points_label="Balanced envelope points (tail on)"),
        caption=(
            "The entered coefficient curve of the airplane less its horizontal "
            "tail -- the tail-off data the flight balance solves against -- "
            "with every balanced condition marked on it. A marked point is the "
            "tail-on solution at that angle of attack, recovered from the "
            "point's own dimensional output rather than from a second "
            "evaluation of the polynomial: it sits on the curve because the "
            "balance carries the tail load as a separate force rather than "
            "inside this coefficient, and any visible departure is the "
            "compressibility correction at that point's Mach. The tail load "
            "itself is a load and is reported with the tail. Coefficients are "
            "dimensionless and are stated LIMIT; nothing in this figure is "
            "scaled or marked ultimate."))


def _wing_inputs(project: Project, *, system: UnitSystem,
                 plan: Sequence[SectionPlan]) -> Section:
    """3.1 -- the wing data the load cases were run from."""
    net = _wing_net(project)
    curves, config = _aero_curves(project)
    clmax = getattr(config, "stall_cl", None) or None
    figures = [_lra_planform_figure(project, net, system),
               _span_load_figure(project, clmax, system),
               _flaps_down_span_load(project)]
    figures += [_aero_curve_figure(curves, config, *spec)
                for spec in _AERO_CURVE_FIGURES]
    table = _lra_station_table(net, system)
    body = [
        "This subsection states the wing data the load cases of this section "
        "were run from: the axis the loads are stated about, the span load the "
        "air load is distributed to, and the airplane lift and moment "
        "coefficients the flight cases were balanced against. The planform "
        "itself is stated in " + section_ref(plan, "configuration_layout")
        + " and is not repeated here.",

        "The coefficients are the airplane less its horizontal tail, which "
        "is the form the balance requires and the form the aerodynamic data "
        "was produced in. The tail-on airplane is the balanced solution at each "
        "condition: the same angle of attack with the balancing tail load "
        "carried as a separate force, which is why the balanced conditions are "
        "marked on the tail-off curve rather than drawn as a second curve. "
        "This analysis publishes no tail-on lift coefficient of its own.",
        _LRA_NOTE,
        "The span loading and the coefficient curves below are inputs to the "
        "load cases and are stated LIMIT. Every load case in the rest of this "
        "section is delivered LIMIT. Both kinds carry the label wherever "
        "they are printed, so no number in this section leaves its basis to be "
        "inferred.",
    ]
    return Section("", body=body, figures=figures,
                   tables=[t for t in (table,) if t is not None])


def _sign_note(plan: Sequence[SectionPlan]) -> str:
    """The axes and sign statement, with its own cross-reference composed."""
    return (
        "Loads are stated in airplane axes, and both moments are stated about "
        "the loads reference axis given in "
        + subsection_ref(plan, _WING_STEP, _WING_INPUTS) + ". The symbols, "
        "their units and whether each is an applied increment or a cumulative "
        "load are tabulated below; the full sign convention is the "
        "analysis-wide one and is not restated per section.")


def _cg_weight(project: Project, name: str) -> Optional[float]:
    """The entered weight of the CG case ``name`` (OR-46: as entered, labelled)."""
    for case in list(getattr(project.weight, "cg_cases", ()) or ()):
        if case.name == name:
            return case.weight_lb
    return None


#: What the sign of the register's load factors means.
#:
#: Not a footnote. ``Nz`` here is the **inertia** load factor -- the negative of
#: the airplane's flight load factor, because the inertia opposes the air load
#: (``wing_inertia._resolve_case``: ``Nz = -NZ``) -- so a +3.8 g manoeuvre is
#: printed as -3.8. A reader who does not know that reads a table of positive-g
#: conditions as a table of negative ones, which is exactly what happened in the
#: owner's review of this section (2026-09-03).
_LOAD_FACTOR_SIGN = (
    "Nz is the inertia load factor, which opposes the air load and is therefore "
    "the negative of the airplane's flight load factor: a case printed at "
    "Nz = -3.8 is a +3.8 g condition. Nx is the inertia drag factor on the same "
    "convention.")


def _negative_case_sentence(net: Sequence[object]) -> str:
    """Whether the analysed set contains a negative-flight-load-factor case.

    A wing is enveloped by its positive *and* its negative conditions -- FAR
    23.333(c)'s negative manoeuvre and the negative gust reverse the bending the
    positive cases produce. A set holding only positive-g cases does not envelop
    the wing, and on the printed sign convention that is not visible at a glance:
    every load factor in the table is a negative number either way. So it is
    stated (OR-58).
    """
    if not net:
        return ""
    # Inertia Nz < 0 is a positive-g condition; > 0 is a negative-g one.
    negative = [r for r in net if float(getattr(r, "nz", 0.0)) > 0.0]
    if negative:
        names = ", ".join(getattr(r, "case", "") for r in negative)
        return (f"The set includes {len(negative)} negative-load-factor "
                f"condition{'' if len(negative) == 1 else 's'} ({names}), which "
                "reverse the bending the positive cases produce.")
    return (
        "Every case run here is a positive-load-factor condition. The set holds "
        "no negative-load-factor case, so the distributions in this section do "
        "not envelop the wing: the negative manoeuvre and negative gust "
        "conditions of 14 CFR 23.333(c), which reverse the bending, are not "
        "among them.")


def _wing_selection(project: Project):
    """``(SELECT's wing conditions, the V-n matrix it searched)``, or ``([], None)``.

    The selection is asked for even when it is overridden, because *whether it was
    overridden* is a fact the register has to state (OR-57): a section that
    presents three entered cases as the outcome of a search is describing an
    analysis nobody ran.
    """
    from ..modules.flight_envelope import build_envelope
    from ..modules.select import build_critical

    try:
        conditions = [c for c in build_critical(project).conditions
                      if getattr(c, "component", "") == "wing"]
    except Exception:
        conditions = []
    try:
        envelope = build_envelope(project)
    except Exception:
        envelope = None
    return conditions, envelope


def _matrix_sentence(envelope) -> str:
    """What the V-n matrix the selection searched actually enumerates.

    The reader's question this answers is a real one: a V-n diagram states a
    speed and a load factor and says nothing about weight, centre of gravity or
    altitude, so the set of *points* behind it has to be described or the
    selection looks like it ran on twenty conditions rather than on every
    combination of them.
    """
    if envelope is None or not envelope.vn:
        return ("The balanced V-n matrix the selection searches was not "
                "produced for this project.")
    points = envelope.vn
    configs = sorted({p.config for p in points})
    cgs = sorted({p.cg for p in points})
    altitudes = sorted({p.altitude_ft for p in points})
    conditions = len({p.condition for p in points})
    altitude_text = (f"the single altitude {format_value(altitudes[0])} ft"
                     if len(altitudes) == 1
                     else "the altitudes "
                          + ", ".join(f"{format_value(a)} ft" for a in altitudes))
    return (
        f"The selection searches the balanced V-n matrix: {len(points)} points, "
        f"every combination of {len(configs)} configuration"
        f"{'' if len(configs) == 1 else 's'} "
        f"({', '.join(configs)}), {len(cgs)} weight and centre-of-gravity "
        f"case{'' if len(cgs) == 1 else 's'} ({', '.join(cgs)}), "
        f"{altitude_text}, and {conditions} flight conditions. A V-n diagram "
        "states a speed and a load factor and nothing about loading or "
        "altitude; the matrix behind it carries all three, and it is the matrix "
        "that is searched.")


def _selection_table(conditions: Sequence[object],
                     run: Sequence[str]) -> Optional[Table]:
    """Every wing condition the selection names, and whether it was run.

    Printed whether or not the two agree, because the case a section does *not*
    carry is the one a reader has no other way of finding.
    """
    if not conditions:
        return None
    rows = []
    for condition in conditions:
        ref = getattr(condition, "case_ref", None)
        label = getattr(condition, "label", "")
        rows.append([
            getattr(ref, "case_id", "") or "--",
            label or "--",
            getattr(ref, "far_reference", "") or "--",
            str(getattr(condition, "case", "") or "--"),
            getattr(ref, "cg", "") or "--",
            "yes" if label in run else "no",
        ])
    return Table(
        title="Critical wing conditions named by the selection",
        columns=["Case", "Condition", "14 CFR", "V-n point", "CG case",
                 "Run here"],
        rows=rows,
        note=("The governing wing condition of each FAR family, as the "
              "critical-load selection found it in the V-n matrix. A condition "
              "marked 'no' is named by the selection and is not carried into "
              "the wing analysis of this project, because the project enters "
              "its own wing case list and an entered list is used as entered."))


def _wing_case_table(project: Project, net: Sequence[object],
                     system: UnitSystem) -> Optional[Table]:
    """3.2's run register: one row per selected wing case."""
    if not net:
        return None
    u = Units(system)
    rows = []
    for result in net:
        ref = getattr(result, "case_ref", None)
        cg = getattr(ref, "cg", "") or ""
        weight = _cg_weight(project, cg)
        rows.append([
            getattr(ref, "case_id", "") or "--",
            getattr(result, "case", "") or "--",
            getattr(ref, "far_reference", "") or "--",
            cg or "--",
            u.plain(weight, "mass") if weight is not None else "--",
            format_value(getattr(ref, "speed_kt", 0.0) or 0.0),
            format_value(getattr(ref, "altitude_ft", 0.0) or 0.0),
            format_value(getattr(result, "nz", 0.0)),
            format_value(getattr(result, "nx", 0.0)),
        ])
    return Table(
        title="Wing load cases run",
        columns=["Case", "Condition", "14 CFR", "CG case",
                 f"Weight ({u.label('mass')})", "V (KEAS)", "Altitude (ft)",
                 "Nz", "Nx"],
        rows=rows,
        note=("The cases carried into the wing analysis, each with the loading "
              "it was run at and the paragraph of 14 CFR Part 23 it is required "
              "by. Speed is equivalent airspeed and altitude is feet: both are "
              "aviation standard in either unit system and are never converted. "
              "The weight is the CG case as entered. "
              + _LOAD_FACTOR_SIGN
              + " Nz and Nx are LIMIT and dimensionless, and the loads they "
              "produce are delivered LIMIT below."))


def _provenance_sentence(entered: bool, named: Sequence[str],
                         run: Sequence[str], missing: Sequence[str]) -> str:
    """Where the analysed case list came from -- selection, or entry (OR-57).

    Two different statements, and the report may not make the first while the
    second is true. An entered list is legitimate and is sometimes necessary --
    the selection names a condition but not the unbalanced rolling moment an
    accelerated-roll case needs, which only an entered case can carry -- but it
    is the project's list, not the selection's, and the difference is the
    reader's to see (OR-46's rule, applied to a case set rather than a value).
    """
    if not entered:
        return ("The cases below are the critical-load selection's own result: "
                "the governing condition of each FAR family, taken from the "
                "matrix without further choice.")
    sentence = (
        "The cases below are the wing case list entered in this project, not "
        "the selection's own result. An entered list is used exactly as "
        "entered, and it is what the loads were computed from. It exists "
        "because a condition can carry data the selection does not name -- an "
        "accelerated-roll case needs an unbalanced rolling moment, which comes "
        "from the aileron analysis and not from the V-n matrix.")
    if missing:
        sentence += (
            " The selection names "
            f"{len(named)} governing wing conditions and {len(run)} "
            f"{'is' if len(run) == 1 else 'are'} carried here; "
            f"{', '.join(missing)} "
            f"{'is' if len(missing) == 1 else 'are'} named and not run, and "
            "the table below states which is which.")
    return sentence


#: The symbols section 3 uses, in the order a reader meets them: the point
#: first, then what is applied at it, then what the structure carries there.
#:
#: A table rather than a sentence because the distinction the section turns on
#: -- which quantities are per-strip increments and which are running totals --
#: is a property of each symbol, and prose that carries it for ten symbols at
#: once is prose nobody checks a column heading against (owner review,
#: 2026-09-03).
_NOMENCLATURE: Tuple[Tuple[str, str, str, str], ...] = (
    ("X", "Station, positive aft along the fuselage reference line",
     "length", "coordinate"),
    ("Y", "Butt line, positive outboard on the starboard wing",
     "length", "coordinate"),
    ("Z", "Waterline, positive up", "length", "coordinate"),
    ("Fx", "Chordwise force applied at the station", "force", "increment"),
    ("Fy", "Spanwise force applied at the station (none in this suite)",
     "force", "increment"),
    ("Fz", "Normal force applied at the station", "force", "increment"),
    ("Mx", "Free moment applied about X (none under strip theory)",
     "moment", "increment"),
    ("My", "Free torsion applied about Y", "moment", "increment"),
    ("Mz", "Free moment applied about Z (none under strip theory)",
     "moment", "increment"),
    ("Sz", "Normal shear carried across the station", "force", "cumulative"),
    ("Sx", "Chordwise shear carried across the station", "force", "cumulative"),
    ("Mxx", "Bending moment about X", "moment", "cumulative"),
    ("Myy", "Torsion carried across the station", "moment", "cumulative"),
    ("Mzz", "Chord bending moment about Z", "moment", "cumulative"),
)


def _nomenclature_table(net: Sequence[object], system: UnitSystem) -> Table:
    """The symbols of section 3, each stated as increment or cumulative.

    The one owner of the distinction: a column heading anywhere in section 3 or
    its appendix names a symbol from this table and nothing else.
    """
    u = Units(system)
    axis = _torsion_axis(net) or "loads reference axis"
    rows = [[symbol, quantity, u.label(dim), sense]
            for symbol, quantity, dim, sense in _NOMENCLATURE]
    return Table(
        title="Notation", columns=["Symbol", "Quantity", "Units", "Sense"],
        rows=rows,
        note=("An increment is the load applied at that station alone. A "
              "cumulative value is the load the structure carries there: the "
              "sum of everything outboard of it, accumulated from the tip "
              f"inboard. Torsion is stated about the {axis}. "
              "The applied moments Mx, My and Mz are right-handed about the "
              "airplane axes; the carried Mxx, Myy and Mzz are the beam's own "
              "positive-magnitude bending and torsion, so Mxx and Mx share a "
              "sense while Mzz is the negation of a body-axis Mz. "
              "Coordinates are geometry -- they are neither scaled to ultimate "
              "nor marked."))


def _derivation_note(net: Sequence[object]) -> str:
    """How the cumulative loads are built from the applied ones.

    Written out because the appendix is a deck: a reader assembling a structural
    model from it has to know which of these terms the model will generate for
    itself, and there is no way to tell that from the column headings alone.
    """
    axis = _torsion_axis(net) or "loads reference axis"
    reference = appendix_ref(WING_LOAD_STATIONS)
    tail = (f" That is why {reference} tabulates the applied vector at each "
            "station's own point rather than the differences of the cumulative "
            "columns: the differences are mostly transfer, and a model given "
            "them would count it twice.") if reference else ""
    return (
        "The cumulative loads are the applied loads summed from the tip "
        "inboard. Writing i for a station, i+1 for the station outboard of it "
        f"and dy for the strip width, all moments about the {axis}:\n"
        "  Sz(i) = Sz(i+1) + Fz(i)\n"
        "  Sx(i) = Sx(i+1) + Fx(i)\n"
        "  Mxx(i) = Mxx(i+1) + Sz(i+1) dy\n"
        "  Myy(i) = Myy(i+1) - Sz(i+1) [X(i+1) - X(i)] + Sx(i+1) [Z(i+1) - "
        "Z(i)] + Myy free(i)\n"
        "  Mzz(i) = Mzz(i+1) + Sx(i+1) dy\n\n"
        "The two terms carrying Sz and Sx into Myy, and the terms carrying Sz "
        "into Mxx and Sx into Mzz, are position transfers -- the shear already "
        "carried at the station, moved across the sweep, dihedral and span of "
        "the bay. They are not applied loads, and a structural model generates "
        "them itself from its own geometry. Of the six applied components only "
        "My is non-zero: Fx and Fz are the applied forces, and Fy, Mx and Mz "
        "are zero for every row of this load set." + tail)


def _point_load_note(net: Sequence[object]) -> str:
    """How a concentrated wing mass enters, stated only where there is one."""
    if not any(getattr(r, "point_loads", ()) for r in net):
        return ""
    return (
        "A concentrated wing mass -- an engine, a gear leg, fuel, a store -- is "
        "not part of any strip. It applies a point force at its own X, Y and Z, "
        "and enters the cumulative loads of every station inboard of it: Fz and "
        "Fx into the shears, and their moments about that station's axis into "
        "Mxx and Myy. It carries no free moment of its own, because every "
        "moment it produces is that force acting through an arm the geometry "
        "already states.")


def _wing_cases(project: Project, *, system: UnitSystem,
                plan: Sequence[SectionPlan]) -> Section:
    """3.2 -- what was run, at what condition, under which rule."""
    net = _wing_net(project)
    table = _wing_case_table(project, net, system)
    conditions, envelope = _wing_selection(project)
    run = [getattr(r, "case", "") for r in net]
    entered = bool(getattr(project.wing_mass, "cases", ()) or ())
    named = [getattr(c, "label", "") for c in conditions]
    missing = [name for name in named if name not in run]
    body = [
        "The wing is analysed at a subset of the flight envelope: not every "
        "point of it, but the conditions that govern the wing structure. Those "
        "cases are listed below, and they are the same cases the summary, the "
        "distributions and the station-by-station appendix state -- one set, "
        "projected four ways.",
        _matrix_sentence(envelope),
        _provenance_sentence(entered, named, run, missing),
        _negative_case_sentence(net),
        _sign_note(plan),
        _derivation_note(net),
        _point_load_note(net),
    ]
    body = [paragraph for paragraph in body if paragraph]
    tables = [t for t in (table, _selection_table(conditions, run),
                          _nomenclature_table(net, system))
              if t is not None]
    if table is None:
        return Section("", body=body,
                       absent_reason=("No wing load cases were produced for "
                                      "this project, so there is nothing to "
                                      "register."))
    return Section("", body=body, tables=tables)


def _wing_summary_table(result: Optional[ModuleResult],
                        system: UnitSystem) -> Optional[Table]:
    """3.3's root values, one row per case, LIMIT with each case's own factor
    stated beside it.

    Built from the module's own conditions, so the quantities printed are the
    ones ``net_loads`` publishes -- including both torsions where the loads
    reference axis is not the quarter chord, which is the pair OR-51 requires
    the section to keep distinct.
    """
    conditions = _conditions(result, system)
    if not conditions:
        return None
    first = conditions[0]
    keys = [value.key for value in first.values]
    labels = {value.key: value for value in first.values}
    columns = ["Case", "Condition", "SF"]
    for key in keys:
        _text, units = _load_cell(labels[key], _required_sf(first))
        columns.append(f"{labels[key].label} ({units})".replace(" ()", ""))
    rows = []
    for condition in conditions:
        ref = condition.case_ref
        by_key = {value.key: value for value in condition.values}
        row = [getattr(ref, "case_id", "") or "--",
               getattr(ref, "condition", "") or condition.title,
               format_value(_required_sf(condition))]
        for key in keys:
            value = by_key.get(key)
            row.append(_load_cell(value, _required_sf(condition))[0]
                       if value is not None else "--")
        rows.append(row)
    return Table(
        title="Wing root loads by case (LIMIT)",
        columns=columns, rows=rows, small=True,
        note=("Root values of each selected case. Every load is LIMIT: the "
              "limit load the analysis computed multiplied by the safety factor "
              "stated in its own row, applied once at this boundary. The "
              "torsion names the axis it is stated about; where the loads "
              "reference axis is not the quarter chord both are given, and they "
              "are the same load about two axes rather than two loads."))


def _wing_summary(results: Mapping[str, Optional[ModuleResult]], *,
                  system: UnitSystem,
                  plan: Sequence[SectionPlan]) -> Section:
    """3.3 -- the load cases assessed, at the root."""
    table = _wing_summary_table(results.get(_WING_STEP), system)
    body = [
        "The root of the wing carries the whole of each distribution, so the "
        "values below size the wing and are the ones a reader checks first. "
        "The distributions they are the root of are plotted in "
        + subsection_ref(plan, _WING_STEP, _WING_DISTRIBUTIONS)
        + " and tabulated station by station in "
        + (appendix_ref(WING_LOAD_STATIONS) or "the appendix") + ".",
    ]
    if table is None:
        return Section("", body=body,
                       absent_reason=("The wing load analysis produced no "
                                      "conditions for this project."))
    return Section("", body=body, tables=[table])


#: ``(figure key, station attribute, dimension, title)`` for 3.4's distributions.
#:
#: Chord bending Mzz is here (OR-72, superseding OR-55). OR-55 left it out as a
#: load "nobody reads off a plot"; at the root it is larger than the torsion
#: that does get a figure on four of the five example cases, so the reason did
#: not survive its own numbers. The five figures are the five columns of the
#: cumulative appendix, in the same order -- one projection each, and no
#: quantity the appendix tabulates goes unplotted.
_DISTRIBUTION_FIGURES: Tuple[Tuple[str, str, str, str], ...] = (
    ("wing_shear_sz", "sz", "force", "Vertical shear Sz"),
    ("wing_bending_mxx", "mxx", "moment", "Bending moment Mxx"),
    ("wing_torsion_myy", "myy", "moment", "Torsion Myy"),
    ("wing_shear_sx", "sx", "force", "Drag shear Sx"),
    ("wing_chord_bending_mzz", "mzz", "moment", "Chord bending Mzz"),
)

_CASE_STYLES = ("solid", "dashed", "dotted", "dashdotted", "densely dashed")


def _distribution_figure(net: Sequence[object], key: str, attr: str, dim: str,
                         title: str, system: UnitSystem, assessed: str) -> Figure:
    """One quantity along the span, every selected case on one axes."""
    axis = _torsion_axis(net)
    named = f"{title} ({axis})" if attr == "myy" and axis else title
    if not net:
        return Figure(key=key, title=f"{named} (LIMIT)",
                      absent_reason=("the wing load distributions were not "
                                     "produced for this project."))
    u = Units(system)
    series = []
    for result, style in zip(net, _CASE_STYLES * 4):
        stations = list(getattr(result, "stations", ()))
        if not stations:
            continue
        sf = float(getattr(result, "safety_factor", ULTIMATE_FACTOR))
        ref = getattr(result, "case_ref", None)
        name = getattr(ref, "case_id", "") or getattr(result, "case", "")
        series.append(Series(
            f"{name} {getattr(result, 'case', '')}".strip(),
            [u.plain_value(s.y, "length") for s in stations],
            [u.load_value(getattr(s, attr), dim, sf) for s in stations], style))
    if not series:
        return Figure(key=key, title=f"{named} (LIMIT)",
                      absent_reason=("the wing load distributions carry no "
                                     "stations to plot."))
    return Figure(
        key=key, title=f"{named} (LIMIT)",
        data=PlotData(f"Butt line Y ({u.label('length')})",
                      f"{named} ({u.ult_label(dim)})", series),
        caption=(f"{named} along the semi-span, every selected wing case on one "
                 "axes. The quantity is cumulative: it is summed from the tip "
                 "inboard, so a value is what the wing carries across that "
                 "station and not the load applied at it. All values are "
                 "LIMIT, each case stating its own safety factor as "
                 f"stated in {assessed}."))


def _wing_distributions(project: Project, *, system: UnitSystem,
                        plan: Sequence[SectionPlan]) -> Section:
    """3.4 -- the net distributions of every selected case."""
    net = _wing_net(project)
    axis = _torsion_axis(net)
    assessed = subsection_ref(plan, _WING_STEP, _WING_ASSESSED)
    figures = [_distribution_figure(net, key, attr, dim, title, system, assessed)
               for key, attr, dim, title in _DISTRIBUTION_FIGURES]
    body = [
        "The distributions below are the net wing loads: the air load and "
        "the inertia load of the same case summed station by station, which is "
        "what the structure carries. Air and inertia are not shown separately; "
        "the loads shown are the net external load, referred to the loads "
        "reference axis" + (f" ({axis})" if axis else "") + ".",
        "Every case selected for the wing is drawn on each axes, so the "
        "governing case for a quantity can be read off the figure rather than "
        "taken on assertion. The station values behind these curves are "
        "tabulated in "
        + (appendix_ref(WING_LOAD_STATIONS) or "the appendix") + ".",
    ]
    return Section("", body=body, figures=figures)


def _wing_loads(project: Project, results: Mapping[str, Optional[ModuleResult]],
                *, system: UnitSystem, plan: Sequence[SectionPlan]) -> Section:
    """Section 3 -- Wing Loads, in its four subsections (OR-48).

    The subsections carry no numbers of their own: each is titled here and
    numbered by :func:`build_section`, so a subsection cannot be renumbered
    without the section it sits under moving with it.
    """
    return Section("", body=[
        "This section states the wing loads: the data they were run from, the "
        "cases run, the loads at the wing root, and the distributions along "
        "the span. Every load case delivered here is LIMIT with its safety "
        "factor stated and not applied, and every quantity that is not a "
        "delivered load says which it is.",
    ], subsections=[
        replace(_wing_inputs(project, system=system, plan=plan),
                title="Wing input data"),
        replace(_wing_cases(project, system=system, plan=plan),
                title="Load cases and sign convention"),
        replace(_wing_summary(results, system=system, plan=plan),
                title="Load cases assessed"),
        replace(_wing_distributions(project, system=system, plan=plan),
                title="Critical load distributions"),
    ])


# --------------------------------------------------------------------------- #
# Appendix B -- wing loads by station (OR-56)
# --------------------------------------------------------------------------- #
#: ``(station attribute, dimension, label)`` of each column the appendix prints.
#:
#: ``fz``/``fx`` are the **increment** each strip contributes; the rest are the
#: cumulative quantities of 3.4. Both are printed because the reader checking a
#: distribution needs the thing being summed as well as the sum, and neither is
#: recoverable from the other on a page.
#: The cumulative channels of B.2, in the order the structure carries them.
#:
#: ``Mzz`` is the chord bending the wing carries, and it is here (OR-71): it is
#: computed for every case, oracle-locked at the root (Appendix A p222), printed
#: by ``wing_span_loads.csv``, printed at the root by 3.3, and named by the
#: closure gate this appendix is written under -- and at the root it *exceeds*
#: the torsion beside it on four of the five example cases. The earlier omission
#: was recorded as "not delivered by this analysis", which was never true of the
#: number; see design note 47 section 1.3.
_CUMULATIVE_LOADS: Tuple[Tuple[str, str, str], ...] = (
    ("sz", "force", "Sz"),
    ("sx", "force", "Sx"),
    ("mxx", "moment", "Mxx"),
    ("myy", "moment", "Myy"),
    ("mzz", "moment", "Mzz"),
)

#: The applied channels of B.1 -- what a structural model is given, not what it
#: carries. All six body-axis components are stated, in vector order, three of
#: them structurally zero: the wing chain has no producer for a spanwise strip
#: load and no wing condition is lateral (``Fy``), and a strip applies forces
#: and a section moment and nothing else, so there is no free ``Mx`` or ``Mz``
#: (all of the cumulative bending is those forces through spanwise arms). The
#: zeros are printed rather than omitted because a reader building cards from
#: this table cannot otherwise tell a zero from an omission. See
#: :func:`_derivation_note`.
_APPLIED_LOADS: Tuple[Tuple[str, str], ...] = (
    ("force", "Fx"),
    ("force", "Fy"),
    ("force", "Fz"),
    ("moment", "Mx"),
    ("moment", "My"),
    ("moment", "Mz"),
)


def applied_load_table(rows: Sequence[object], *, title: str,
                       note: str, system: UnitSystem,
                       small: bool = True) -> Optional[Table]:
    """The one applied-load appendix table, for every component (OR-139).

    B.1, C.1, D and E are this function with different rows. One column set,
    one order, one set of headings: a reader who has learnt one applied
    appendix has learnt all four, and a heading cannot drift between them
    because there is only one place it is written.

    ``Station`` and ``GID`` are both printed and are not the same identity. A
    concentrated wing mass has a name and no grid (the exported stick model
    nodes the load stations only), so a table keyed on ``GID`` alone would
    print a nameless blank row for every mass -- and a table keyed on
    ``Station`` alone could not be matched to the deck, which is the whole
    claim these appendices make. The columns are the applied CSV's, so the page
    and the file are the same row.

    The moments come through
    :func:`~sloads.export.sbeam_bridge.applied_body_moments` rather than off the
    record, because a beam stores its torsion about its own span axis and only
    that owner knows which airplane axis that is for the component in hand.
    """
    from ..export.sbeam_bridge import applied_body_moments

    if not rows:
        return None
    u = Units(system)
    length = u.label("length")
    columns = ["Case", "Station", "GID", f"X ({length})", f"Y ({length})",
               f"Z ({length})"]
    columns += [f"{label} ({u.ult_label(dim)})" for dim, label in _APPLIED_LOADS]
    columns.append("SF")
    out: List[List[str]] = []
    for load in rows:
        values = ((load.fx, load.fy, load.fz)          # type: ignore[attr-defined]
                  + applied_body_moments(load))        # type: ignore[arg-type]
        sf = load.safety_factor                        # type: ignore[attr-defined]
        out.append(
            [load.case_id or load.case, load.label,    # type: ignore[attr-defined]
             "" if load.gid is None else str(load.gid)]  # type: ignore[attr-defined]
            + [u.plain(getattr(load, a), "length") for a in ("x", "y", "z")]
            + [u.load(value, dim, sf)
               for value, (dim, _label) in zip(values, _APPLIED_LOADS)]
            + [format_value(sf)])
    return Table(title=title, columns=columns, rows=out, small=small, note=note)


def _case_name(result: object) -> str:
    """The case identity a table row is keyed by."""
    ref = getattr(result, "case_ref", None)
    return getattr(ref, "case_id", "") or getattr(result, "case", "")


def _applied_table(net: Sequence[WingLoadResult], system: UnitSystem,
                   assessed: str) -> Optional[Table]:
    """B.1 -- the applied wing set: every strip, and every point mass.

    Deck-grade, which is why the point travels with the load: ``Fz`` applied at
    a station other than the one stated here produces a different ``Myy``, so a
    table that left the coordinates to a cross-reference would be half a load
    definition. The rows come from the export channel and the shape from
    :func:`applied_load_table`, so this function is now a title and a note.
    """
    from ..export.sbeam_bridge import applied_loads

    if not net:
        return None
    axis = _torsion_axis(net) or "loads reference axis"
    return applied_load_table(
        applied_loads("wing", list(net)),
        title="Applied wing loads by station (LIMIT)", system=system,
        note=("The load applied at each station's own point: a strip row per "
              "load station, root to tip, and a row per concentrated wing mass "
              "at its own coordinates. Together they are the whole applied "
              "set, as the six body-axis components a model is given. Three of "
              "them are zero for every row, and are printed so that a zero "
              "cannot be read as an omission: Fy because the wing chain "
              "produces no spanwise strip load and no wing condition is "
              "lateral, Mx and Mz because a strip applies forces and a section "
              "moment and nothing else -- the whole of the cumulative Mxx and "
              "Mzz is those forces acting through the spanwise arms these "
              f"coordinates state. My is the free torsion about the {axis}; a "
              "point mass carries none, because every moment it produces is "
              "its force acting through an arm the coordinates already state. "
              "A concentrated mass has a name and no GID: the exported stick "
              "model nodes the load stations only, so there is no grid at its "
              "coordinates to reference. "
              "Moments are right-handed about the airplane axes. Every load is "
              "LIMIT, with its case's safety factor stated in its own row and "
              f"applied to nothing, as set out in {assessed}; the coordinates "
              "are geometry and are neither scaled nor marked."))


def _cumulative_table(net: Sequence[object], system: UnitSystem,
                      notation: str) -> Optional[Table]:
    """B.2 -- what the structure carries at each station."""
    if not net:
        return None
    u = Units(system)
    length = u.label("length")
    columns = ["Case", "Station", f"Y ({length})"]
    columns += [f"{label} ({u.ult_label(dim)})"
                for _attr, dim, label in _CUMULATIVE_LOADS]
    rows: List[List[str]] = []
    for result in net:
        name = _case_name(result)
        sf = float(getattr(result, "safety_factor", ULTIMATE_FACTOR))
        for index, station in enumerate(getattr(result, "stations", ()), start=1):
            rows.append([name, str(index), u.plain(station.y, "length")]
                        + [u.load(getattr(station, attr), dim, sf)
                           for attr, dim, _label in _CUMULATIVE_LOADS])
    if not rows:
        return None
    axis = _torsion_axis(net)
    return Table(
        title="Cumulative wing loads by station (LIMIT)", columns=columns,
        rows=rows, small=True,
        note=("What the wing carries at each station: the applied loads of the "
              "table above, summed from the tip inboard by the relations in "
              f"{notation}. The station coordinates are printed once, with the "
              "applied set. Torsion is stated about the "
              f"{axis or 'loads reference axis'}. These are the beam's own "
              "quantities and not the body-axis vector of the table above: "
              "Mxx and Mzz are positive-magnitude bending integrals, so Mxx "
              "shares its sense with the applied Mx while Mzz is the negation "
              f"of a body-axis Mz. The distinction is defined once, in "
              f"{notation}. Every load is LIMIT; its case's safety factor is stated but not applied. Its "
              "safety factor."))


def _station_appendix(project: Project, *, system: UnitSystem,
                      plan: Sequence[SectionPlan]) -> Section:
    """Appendix B's content: the applied set, then the cumulative one."""
    net = _wing_net(project)
    assessed = subsection_ref(plan, _WING_STEP, _WING_ASSESSED)
    notation = subsection_ref(plan, _WING_STEP, _WING_CASES)
    applied = _applied_table(net, system, assessed)
    carried = _cumulative_table(net, system, notation)
    body = [
        "This appendix carries the wing load distributions of "
        + section_ref(plan, _WING_STEP) + " in full: every selected case at "
        "every load station, in the airplane axes and about the loads "
        "reference axis stated in "
        + subsection_ref(plan, _WING_STEP, _WING_INPUTS) + ". It is the same "
        "result the figures are drawn from, printed rather than plotted.",
        "It is given in two parts, because they are two different quantities "
        "and a reader who takes one for the other builds the wrong model. The "
        "first is the load applied at each station -- what a structural model "
        "is given. The second is the load carried across each station -- what "
        "that model should return. The symbols and the relation between them "
        "are stated in " + notation + ".",
    ]
    if applied is None or carried is None:
        return Section("", body=body,
                       absent_reason=("The wing load distributions were not "
                                      "produced for this project, so there is "
                                      "nothing to tabulate."),
                       page_break=True)
    return Section("", body=body, page_break=True, landscape=True,
                   subsections=[Section("Applied loads", tables=[applied]),
                                Section("Cumulative loads", tables=[carried])])


# --------------------------------------------------------------------------- #
# Section 4 -- Fuselage Loads (note 44 section 13, OR-94 ... OR-102, and
# section 15, OR-108 ... OR-113)
# --------------------------------------------------------------------------- #
_BODY_STEP = "fuselage_loads"

#: The folded module that owns the pull-up maneuver quantities of blocks 4 and 5.
#:
#: ``run_sections`` keys a folded module by its own name, so SELECT's result is
#: reachable from here without re-running it -- which is the whole of OR-109:
#: the fuselage page states the number the tail analysis made.
_SELECT_MODULE = "select"

#: 4.x positions, for the cross-references the subsections make to each other.
_BODY_BEAM = 0
_BODY_CASES = 1
_BODY_CRITICAL = 2
_BODY_CLOSURE = 3
_BODY_DISTRIBUTIONS = 4

#: The two h-tail conditions the manual prints in its *fuselage* summary.
#:
#: ``(block heading, SELECT's own condition label)``. p198's blocks 4 and 5 are
#: the down-tail-load pull-ups -- H5CASE and H7CASE in the source -- and not
#: their up-load siblings, which the manual prints on the tail page alone.
_PULL_UP_BLOCKS: Tuple[Tuple[str, str], ...] = (
    ("Unchecked pull-up maneuver (down tail load)", "UNCHECKED MAN DN"),
    ("Checked pull-up maneuver (down tail load)", "CHECKED MAN DN"),
)

#: ``(condition label -> the increment key that condition publishes)``.
#:
#: The unchecked cases carry an elevator-deflection increment and the checked
#: ones a pitch-acceleration increment; they are different quantities with
#: different keys, and the block prints whichever its own case has.
_PULL_UP_INCREMENT = {
    "UNCHECKED MAN DN": "elevator_deflection_increment_cp_50_pct",
    "CHECKED MAN DN": "maneuver_load_increment",
}


def _body_net(project: Project) -> List[BodyLoadResult]:
    """The net fuselage load distributions, or ``[]``.

    Asked of ``body_loads``' own builder -- the same one the Export bundle and
    the Fuselage Loads page call -- so the section, the appendix and the
    exported CSV describe one set of numbers. Returns ``[]`` rather than
    raising, on ``_wing_net``'s reasoning: G-OR-7 keeps a half-filled project
    building a complete document.

    This is the **only** thing section 4 reads from the builder rather than from
    the published result (OR-95, as rewritten under OR-108): the stations live
    here and no result type carries them. The case set, the root quantities and
    the register come from the ``ModuleResult``, exactly as section 3's do.
    """
    from ..modules.body_loads import build_body_loads

    try:
        return list(build_body_loads(project))
    except Exception:
        return []


def _beam_stations(project: Project) -> List[FuselageStation]:
    """The station table the Ch 15 beam was integrated over, or ``[]``."""
    from ..mass_distribution import fuselage_beam_stations

    try:
        return list(fuselage_beam_stations(project))
    except Exception:
        return []


def _beam_is_derived(project: Project) -> bool:
    """Whether the beam is the mass SSOT's derived table or the entered one.

    **Asked, never asserted** (OR-96). In this document it is always the derived
    table -- ``stations_are_override`` is ``Origin.SLOADS``, so OR-43's
    projection strips it before the section sees it -- but a section that stated
    a derivation the analysis had not made would be OR-57's defect in a second
    place, and the honest form costs one attribute read.
    """
    fm = project.fuselage_mass
    return not bool(getattr(fm, "stations_are_override", False))


def _fuselage_lra(project: Project):
    """The body beam's LRA waterline, asked of its owner (never re-derived)."""
    from ..derived_geometry import fuselage_lra

    try:
        return fuselage_lra(project)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def _beam_table(project: Project, system: UnitSystem) -> Optional[Table]:
    """4.1's station table, with the beam's own total as its last row.

    The total is a row rather than a sentence because the reader's question --
    is this beam the whole airplane? -- is answered by comparing two numbers,
    and a number in prose is a number nobody adds up.
    """
    beam = _beam_stations(project)
    if not beam:
        return None
    u = Units(system)
    length = u.label("length")
    rows = [[str(index), u.plain(station.x, "length"),
             u.plain(station.y, "length"), u.plain(station.z, "length"),
             u.plain(station.weight_lb, "mass")]
            for index, station in enumerate(beam, start=1)]
    total = math.fsum(station.weight_lb for station in beam)
    rows.append(["Total", "--", "--", "--", u.plain(total, "mass")])
    lra = _fuselage_lra(project)
    return Table(
        title="Fuselage beam stations",
        columns=["Station", f"X ({length})", f"Y ({length})", f"Z ({length})",
                 f"Weight ({u.label('mass')})"],
        rows=rows, small=True,
        note=("The lumped mass the Ch 15 beam integrates, station by station. "
              "The weights are mass and are not loads: they carry no safety "
              "factor, and the inertia forces they produce are the load, "
              "computed at each case's own load factor. "
              "Y and Z are where that mass acts -- the weight-weighted centroid "
              "of the items lumped at the station -- and are not where the beam "
              "runs: the beam is a line along "
              + (f"waterline {u.plain(lra.z_at(beam[0].x), 'length')} {length}. "
                 if lra is not None else "the body. ")
              + "Chapter 15 solves the body as a symmetric-flight vertical beam, "
                "so a mass's Y and Z enter neither its shear nor its bending; "
                "only X does. They place the mass in the exported model and in "
                "the side view above."))


def _beam_provenance(project: Project) -> str:
    """Where the beam's mass came from, and whether the beam is whole (OR-96)."""
    from ..mass_distribution import partition_closes

    beam = _beam_stations(project)
    entered = list(getattr(project.fuselage_mass, "stations", ()) or ())
    if not _beam_is_derived(project):
        sentence = (
            f"The beam is the fuselage station table entered in this project, "
            f"{len(entered)} stations, marked an explicit override and used "
            "exactly as entered.")
    else:
        sentence = (
            f"The beam is derived from the weight item data base, not entered: "
            f"{len(beam)} stations, lumped from the items this airplane is "
            f"weighed from. The project also carries {len(entered)} entered "
            "fuselage stations, which are an override and are not taken here.")
    try:
        check = partition_closes(project)
    except Exception:
        return sentence
    return sentence + " " + (
        "The beam and the wing together account for the whole airplane: "
        f"{check.detail}."
        if check.ok else
        "The beam and the wing do not account for the whole airplane: "
        f"{check.detail}. The distributions below integrate the beam as it "
        "stands.")


def _carry_through(project: Project):
    """The wing carry-through, asked of its owner; ``None`` when it refuses."""
    from ..derived_geometry import carry_through

    try:
        return carry_through(project)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def _body_side_view(project: Project, system: UnitSystem) -> Figure:
    """4.1's side view: the body mass, the beam it runs on, and what loads it.

    A station table answers "how much, where along the body"; it cannot answer
    "does this look like the airplane". Drawn in the X-Z plane because that is
    the plane Chapter 15 solves in, with the three things a reader checks the
    beam against: where the mass sits, where the wing takes it out, and where
    the tail puts it back in.
    """
    key, title = "body_side_view", "Fuselage mass, beam and load introduction"
    beam = _beam_stations(project)
    if not beam:
        return Figure(key=key, title=title, absent_reason=(
            "the project has no fuselage beam stations, so there is no body to "
            "draw."))
    u = Units(system)
    scale, length = _length_channel(system)
    lra = _fuselage_lra(project)
    xs = [station.x for station in beam]
    series = []
    if lra is not None:
        # The beam itself, sampled at every station so a body-following axis
        # draws as the line it is rather than as a chord between its ends.
        series.append(Series(
            "Fuselage beam (LRA)", [x * scale for x in xs],
            [lra.z_at(x) * scale for x in xs], "solid"))
    points = [(format_value(station.weight_lb * u.plain_value(1.0, "mass")),
               station.x * scale, station.z * scale)
              for station in beam if station.weight_lb]
    vlines = []
    carry = _carry_through(project)
    if carry is not None:
        vlines += [("front spar", carry.x_f * scale),
                   ("rear spar", carry.x_r * scale)]
    ti = project.tail_loads
    if ti is not None and ti.xt25:
        vlines.append(("h-tail load", ti.xt25 * scale))
    if not points and not series:
        return Figure(key=key, title=title, absent_reason=(
            "the fuselage beam carries no mass and no resolvable axis to draw."))
    spar = ("the wing carry-through, where the body's load is reacted into the "
            "wing, " if carry is not None else "")
    return Figure(
        key=key, title=title,
        data=PlotData(f"Fuselage station X ({length})",
                      f"Waterline Z ({length})", series,
                      points=points, vlines=vlines,
                      points_label="Body mass stations"),
        caption=(
            f"The airplane in side view, to scale on equal axes. Each marker is "
            f"one beam station at the waterline its mass acts at, labelled with "
            f"that mass in {u.label('mass')}; the line is the beam those masses "
            f"are carried on. The vertical lines mark {spar}"
            "and the station the horizontal tail's balancing load is applied at. "
            "Chapter 15 solves this plane, but as a vertical beam: a mass's "
            "waterline enters neither the shear nor the bending, only its "
            "station does. The spread of the markers about the beam is therefore "
            "a fact about the airplane rather than about the loads below."))


def _carry_through_sentence(project: Project) -> str:
    """The carry-through the unbalanced moment is reacted over (OR-97, note 50).

    Stated in 4.1 because it is geometry, and stated again beside the fitting
    loads in 4.4 because that is where a reader meets the numbers it sized. The
    provenance travels with it in both places: an assumed spar station is never
    reported as input.
    """
    from ..derived_geometry import carry_through

    try:
        carry = carry_through(project)
    except Exception:
        carry = None
    if carry is None:
        return (
            "The wing carry-through could not be derived for this project, so "
            "the unbalanced moment has no wing attachment to be reacted at. "
            "The consequence is stated with the distributions.")
    if carry.assumed:
        return (
            "The wing carry-through runs from fuselage station "
            f"{format_value(carry.x_f)} to {format_value(carry.x_r)} in, and "
            "neither station was entered for this airplane: both are the "
            "estimator's, placed at "
            f"{format_value(carry.front_pct * 100.0)} and "
            f"{format_value(carry.rear_pct * 100.0)} per cent of the root "
            "chord. Every wing-attach fitting load in this document is "
            "therefore sized on assumed geometry. The spar stations are an "
            "input of this analysis, so entering the measured ones replaces "
            "the estimate.")
    return (
        "The wing carry-through runs from fuselage station "
        f"{format_value(carry.x_f)} to {format_value(carry.x_r)} in, entered "
        "for this airplane. The wing-attach fitting loads below are sized on "
        "that geometry as entered.")


def _body_beam(project: Project, *, system: UnitSystem,
               plan: Sequence[SectionPlan]) -> Section:
    """4.1 -- the fuselage beam the loads were run on."""
    table = _beam_table(project, system)
    body = [
        "This subsection states the beam the fuselage loads were run on: the "
        "mass it carries at each station, where that mass came from, and the "
        "wing carry-through the unbalanced moment is reacted over. The "
        "fuselage geometry itself is stated in "
        + section_ref(plan, "configuration_layout") + " and is not repeated "
        "here.",
        _beam_provenance(project),
        _carry_through_sentence(project),
        "The fuselage beam excludes the wing mass outside the fuselage, which "
        "the wing analysis carries: the two together are the whole airplane, "
        "and the carry-through enters this beam as a reaction rather than as "
        "mass, so applying both would count it twice.",
    ]
    if table is None:
        return Section("", body=body,
                       absent_reason=("This project carries no fuselage beam "
                                      "stations, so there is no beam to "
                                      "state."))
    return Section("", body=body, tables=[table],
                   figures=[_body_side_view(project, system)])


#: How the report names the p198 quantities that SELECT publishes twice.
#:
#: ``select_fuselage`` labels the same quantity -- the fuselage load reacted at
#: the wing, ``LZW - NZ*WW`` -- ``fuselage_down_load_on_wing`` on the two down
#: blocks and ``fuselage_load_on_wing`` on the up one, and the balancing tail
#: load ``tail_load`` on three blocks and ``balancing_tail_load`` on the fourth.
#: They are one quantity under two keys, which is the M4-9 key contract read the
#: wrong way round; the table folds them so the reader gets one column rather
#: than two half-empty ones.
#:
#: **Filed, not fixed** (OR-14): renaming a published key changes every CSV
#: column built from it, which is not the additive change OR-13 admits. See the
#: backlog entry raised with this section.
_BODY_QUANTITIES: Tuple[Tuple[str, Tuple[str, ...], str], ...] = (
    ("Total fuselage load on wing",
     ("fuselage_down_load_on_wing", "fuselage_load_on_wing"), "force"),
    ("Nz", ("load_factor_nz",), ""),
    ("Tail load", ("tail_load", "balancing_tail_load"), "force"),
)


def _first_value(condition: ConditionResult,
                 keys: Sequence[str]) -> Optional[LoadValue]:
    """The first of ``keys`` this condition publishes, or ``None``."""
    by_key = _by_key(condition)
    for key in keys:
        if key in by_key:
            return by_key[key]
    return None


def _case_list_source(project: Project) -> str:
    """Which of the two paths the fuselage case list came from (OR-99).

    Asked of the module that makes the choice, so the sentence and the analysis
    cannot disagree about it.
    """
    from ..modules.body_loads import case_list_source

    return case_list_source(project)


def _body_conditions(results: Mapping[str, Optional[ModuleResult]],
                     system: UnitSystem) -> List[ConditionResult]:
    """The published fuselage conditions, in the document's units."""
    return _conditions(results.get(_BODY_STEP), system)


def _vn_points(project: Project) -> Dict[str, int]:
    """``{condition label: V-n point}`` for the fuselage cases.

    Identity, not load: the V-n row a condition was selected at is part of what
    names the case, and no result type carries it. Read from the same helper the
    module published its conditions from, so there is one case list and not two.
    """
    from ..modules.body_loads import critical_fuselage_conditions

    try:
        conditions = critical_fuselage_conditions(project)
    except Exception:
        return {}
    return {c.label: c.case for c in conditions if c.case is not None}


def _body_case_table(project: Project,
                     results: Mapping[str, Optional[ModuleResult]],
                     system: UnitSystem) -> Optional[Table]:
    """4.2's run register: one row per fuselage condition carried."""
    conditions = _body_conditions(results, system)
    if not conditions:
        return None
    u = Units(system)
    vn = _vn_points(project)
    rows = []
    for condition in conditions:
        ref = condition.case_ref
        label = getattr(ref, "condition", "") or condition.title
        cg = getattr(ref, "cg", "") or ""
        weight = _cg_weight(project, cg)
        rows.append([
            getattr(ref, "case_id", "") or "--",
            label,
            condition.far_reference or "--",
            str(vn.get(label, "--")),
            cg or "--",
            u.plain(weight, "mass") if weight is not None else "--",
            format_value(_required_sf(condition)),
        ])
    return Table(
        title="Fuselage load cases run",
        columns=["Case", "Condition", "14 CFR", "V-n point", "CG case",
                 f"Weight ({u.label('mass')})", "SF"],
        rows=rows,
        note=("The conditions carried into the fuselage analysis, each with the "
              "V-n point it was selected at and the paragraph of 14 CFR Part 23 "
              "it is required by. The weight is the CG case as entered. Every "
              "case states the safety factor 14 CFR 23.303 prescribes for it; "
              "no load in this section has been multiplied by it."))


#: The three symbols section 4 uses, and nothing else (OR-100).
_BODY_NOMENCLATURE: Tuple[Tuple[str, str, str, str], ...] = (
    ("X", "Fuselage station, positive aft along the fuselage reference line",
     "length", "coordinate"),
    ("Fz", "Normal force applied at the station", "force", "increment"),
    ("Sz", "Normal shear carried across the station", "force", "cumulative"),
    ("Myy", "Bending moment carried across the station, about the lateral axis",
     "moment", "cumulative"),
)

#: What section 4 does not deliver, said once and never tabulated as zeros.
#:
#: Ch 15 p103 is a symmetric-flight vertical beam solve. The lateral body case
#: is a different analysis with a different producer, so a lateral shear or a
#: lateral bending column here would be a measured zero rather than an absent
#: quantity -- OR-61's finding, applied one section over.
_BODY_ABSENCES = (
    "This analysis delivers three quantities along the body and no others: the "
    "applied normal force Fz, and the normal shear Sz and bending moment Myy "
    "the structure carries. There is no lateral shear and no lateral bending "
    "here, and they are not tabulated as zeros: Chapter 15's beam is a "
    "symmetric-flight vertical solve, so a lateral quantity is a load this "
    "section does not produce rather than a load it measured to be zero. The "
    "torsion the body carries is likewise not part of this solve.")

#: What the sign of the register's load factors means -- and it is not
#: section 3's.
#:
#: Section 3 prints the **inertia** load factor, whose sign is the negative of
#: the airplane's; section 4's Nz is the airplane's own flight load factor,
#: straight off the V-n row. Two sections, two conventions, one document: a
#: reader who carries section 3's rule into this table reads every condition
#: backwards. So it is stated here in its own words rather than cross-referenced
#: (OR-58, applied to a section whose convention differs).
_BODY_LOAD_FACTOR_SIGN = (
    "Nz in this section is the airplane's flight load factor, taken from the "
    "V-n point that selected the condition: a +3.8 g manoeuvre is printed as "
    "+3.8 and a negative-g condition is printed negative. This is not the "
    "convention of the wing section, which prints the inertia load factor and "
    "therefore the opposite sign; the two sections state their own.")


def _body_negative_sentence(conditions: Sequence[ConditionResult]) -> str:
    """Whether the analysed fuselage set holds a negative-g condition (OR-58).

    From the analysed set, never by assertion. The condition *names* carry the
    sense in words -- ``AFT UP BENDING`` -- and a name is not a number, which is
    exactly the trap this sentence exists to close.
    """
    negative = []
    for condition in conditions:
        value = _first_value(condition, ("load_factor_nz",))
        if value is not None and value.value < 0.0:
            label = getattr(condition.case_ref, "condition", "") or condition.title
            negative.append(label)
    if negative:
        one = len(negative) == 1
        return (f"The set includes {len(negative)} negative-load-factor "
                f"condition{'' if one else 's'} ({', '.join(negative)}), which "
                f"{'reverses' if one else 'reverse'} the bending the positive "
                "cases produce.")
    return (
        "Every condition run here is a positive-load-factor case. The set holds "
        "no negative-load-factor condition, so the distributions in this "
        "section do not envelop the fuselage: the negative-g conditions, which "
        "reverse the bending, are not among them.")


def _body_nomenclature_table(system: UnitSystem) -> Table:
    """Section 4's notation, restricted to the three symbols it uses."""
    u = Units(system)
    rows = [[symbol, quantity, u.label(dim) if dim else "--", sense]
            for symbol, quantity, dim, sense in _BODY_NOMENCLATURE]
    return Table(
        title="Notation", columns=["Symbol", "Quantity", "Units", "Sense"],
        rows=rows,
        note=("An increment is the load applied at that station alone. A "
              "cumulative value is the load the structure carries there: "
              "everything forward of it, accumulated nose to tail. X is "
              "geometry -- it is neither scaled nor marked. Fz, Sz and Myy are "
              "LIMIT, each case stating the factor it does not apply."))


def _body_derivation_note() -> str:
    """How the fuselage beam is built, in the manual's own two passes."""
    return (
        "The beam is solved in the two passes of Reference 1 page 103. The "
        "first applies the inertia of each station weight at that case's load "
        "factor, and the balancing tail air load at the tail station, and "
        "integrates nose to tail; the moment left at the aft end of that set is "
        "the unbalanced moment. The second reacts the unbalanced moment, and "
        "the residual vertical force with it, at the wing carry-through, and "
        "re-integrates the whole set. Writing i for a station and i+1 for the "
        "station aft of it:\n"
        "  Fz(i) = -Nz W(i)\n"
        "  Sz(i) = Sz(i-1) + Fz(i)\n"
        "  Myy(i) = Myy(i-1) + Sz(i-1) [X(i) - X(i-1)]\n\n"
        "The reactions are applied as the statically equivalent linear "
        "distribution over the carry-through rather than as the manual's two "
        "point loads: same resultant, same first moment, and no shear spike "
        "across a short carry-through. The front and rear fitting loads are "
        "reported separately and are not applied again on top of it.")


def _body_cases(project: Project, results: Mapping[str, Optional[ModuleResult]],
                *, system: UnitSystem,
                plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    """4.2 -- what was run, at what condition, under which rule."""
    conditions = _body_conditions(results, system)
    table = _body_case_table(project, results, system)
    source = _case_list_source(project)
    provenance = (
        "The cases below are the fuselage conditions carried on this project's "
        "persisted critical-load set, as the selection wrote them: they were "
        "not re-selected for this report."
        if source == "envelope" else
        "The cases below are the critical-load selection's own result, "
        "computed from the V-n matrix for this analysis: this project carries "
        "no persisted fuselage conditions.")
    body = [
        "The fuselage is analysed at the conditions that govern it, not at "
        "every point of the flight envelope. Those conditions are listed below, "
        "and they are the same set the critical summary, the closure and the "
        "distributions state -- one case list, projected four ways.",
        provenance,
        _body_negative_sentence(conditions),
        _BODY_LOAD_FACTOR_SIGN,
        _BODY_ABSENCES,
        _body_derivation_note(),
    ]
    if table is None:
        return Section("", body=body,
                       absent_reason=("No fuselage load cases were produced "
                                      "for this project, so there is nothing "
                                      "to register."))
    return Section("", body=body,
                   tables=[table, _body_nomenclature_table(system)])


def _critical_summary_table(project: Project,
                            results: Mapping[str, Optional[ModuleResult]],
                            system: UnitSystem) -> Optional[Table]:
    """4.3's blocks 1, 2, 3 and 7 -- the balanced-airplane fuselage conditions.

    One table rather than four blocks of prose: the manual prints them as four
    stanzas of the same three quantities, and four stanzas is a format a reader
    cannot compare across.
    """
    conditions = _body_conditions(results, system)
    if not conditions:
        return None
    u = Units(system)
    vn = _vn_points(project)
    columns = ["Case", "Condition", "14 CFR", "V-n point", "SF"]
    for label, _keys, dim in _BODY_QUANTITIES:
        columns.append(f"{label} ({u.ult_label(dim)})" if dim else label)
    rows = []
    for condition in conditions:
        ref = condition.case_ref
        name = getattr(ref, "condition", "") or condition.title
        sf = _required_sf(condition)
        row = [getattr(ref, "case_id", "") or "--", name,
               condition.far_reference or "--", str(vn.get(name, "--")),
               format_value(sf)]
        for _label, keys, dim in _BODY_QUANTITIES:
            value = _first_value(condition, keys)
            if value is None:
                row.append("--")
            elif dim:
                row.append(_load_cell(value, sf)[0])
            else:
                row.append(format_value(value.value))
        rows.append(row)
    return Table(
        title="Critical fuselage loads (LIMIT)", columns=columns, rows=rows,
        note=("The manual's own critical-fuselage summary (Reference 1 page "
              "198): the maximum total fuselage load acting down on the wing, "
              "the maximum aft-fuselage down and up bending, and the greatest "
              "vertical inertia factor for concentrated-weight installations. "
              "Every load is LIMIT and states the safety factor prescribed for "
              "its case; nothing here has been multiplied by it. The fuselage "
              "load on the wing is the fuselage weight reacted at the wing at "
              "that case's load factor, less the wing's own weight."))


def _pull_up_table(project: Project,
                   results: Mapping[str, Optional[ModuleResult]],
                   system: UnitSystem, tail_ref: str) -> Optional[Table]:
    """4.3's blocks 4 and 5 -- the pull-up maneuvers, read from SELECT (OR-109).

    The quantities are the tail analysis's, printed here because the fuselage
    question is asked here, and **read from SELECT's own h-tail conditions**
    rather than reassembled, so the fuselage page and the tail page cannot
    disagree about a number they both print.

    Weight and CG are case identity and are stated by lookup from the case's own
    CG name (OR-110), not recomputed. The 50 per cent tail MAC station is the
    entered one (OR-112): the manual prints zero in these two blocks while its
    own tail-loads echo states the real station, and its own arithmetic closes
    only with the real one.
    """
    conditions = _conditions(results.get(_SELECT_MODULE), system)
    if not conditions:
        return None
    u = Units(system)
    xt50 = getattr(project.tail_loads, "xt50", None)
    rows = []
    for _block, label in _PULL_UP_BLOCKS:
        condition = next(
            (c for c in conditions
             if getattr(c.case_ref, "condition", "") == label), None)
        if condition is None:
            continue
        ref = condition.case_ref
        cg = getattr(ref, "cg", "") or ""
        case = _cg_case_named(project, cg)
        sf = _required_sf(condition)
        by_key = _by_key(condition)

        def cell(key: str, _by_key=by_key, _sf=sf) -> str:
            value = _by_key.get(key)
            return _load_cell(value, _sf)[0] if value is not None else "--"

        rows.append([
            getattr(ref, "case_id", "") or "--",
            condition.far_reference or "--",
            cg or "--",
            u.plain(getattr(case, "weight_lb", None), "mass") if case else "--",
            u.plain(getattr(case, "xcg", None), "length") if case else "--",
            u.plain(xt50, "length") if xt50 else "--",
            cell("balanced_tail_load"),
            cell(_PULL_UP_INCREMENT[label]),
            cell("total_tail_load"),
            cell("unbalanced_moment_about_cg"),
            format_value(sf),
        ])
    if not rows:
        return None
    return Table(
        title="Pull-up maneuver fuselage loads (LIMIT)",
        columns=["Case", "14 CFR", "CG case",
                 f"Weight ({u.label('mass')})", f"XCG ({u.label('length')})",
                 f"FS 50% h-tail ({u.label('length')})",
                 f"Balanced tail load ({u.ult_label('force')})",
                 f"Unbalanced increment ({u.ult_label('force')})",
                 f"Total tail load ({u.ult_label('force')})",
                 f"Unbalanced moment about CG ({u.ult_label('moment')})", "SF"],
        rows=rows, small=True,
        note=("The two pull-up maneuvers the manual prints in its fuselage "
              "summary. The tail loads and the unbalanced pitching moment are "
              "the horizontal-tail analysis's own values, reproduced here and "
              "derived in " + tail_ref + "; the weight and CG are the case's, "
              "stated by its CG name so the rest of the case is found where it "
              "is defined. The unbalanced moment is the pitching moment the "
              "increment leaves about the CG, and it is the fuselage's to "
              "carry. All loads are LIMIT with the factor stated and not "
              "applied."))


def _cg_case_named(project: Project, name: str):
    """The entered CG case ``name``, or ``None`` (OR-110: identity by lookup)."""
    for case in list(getattr(project.weight, "cg_cases", ()) or ()):
        if case.name == name:
            return case
    return None


def _body_advisories(plan: Sequence[SectionPlan]) -> List[str]:
    """The manual's own advisories, carried because each names something true.

    Block 1's is about where the down shear lands, block 6 is the landing
    advisory and block 7 the pitching-acceleration one. The last is carried
    because it states a limitation this analysis still has (OR-113): the linear
    half of page 103's "linear and pitching load factors" is modelled and the
    pitching half is not, so the manual's warning is a true statement about
    these numbers rather than decoration. Reproducing an advisory that named
    nothing would be decoration, which is the only reason to carry prose from a
    printed page at all.
    """
    landing = section_ref(plan, "landing_loads")
    return [
        "The maximum down load on the wing may be critical for down shear just "
        "aft of the rear wing attachment, just forward of the front wing "
        "attachment, or both, and is probably the most critical aft-fuselage "
        "down bending and shear condition for an aft-mounted engine "
        "configuration.",

        "Landing conditions are not among the cases above. The forward "
        "fuselage is critical for up bending in the three-wheel level landing "
        "and may be critical for down bending in the two-wheel level landing; "
        "those conditions are analysed in " + landing + ", and the fuselage "
        "loads of this section are flight loads only.",

        "Pitching acceleration adds algebraically to the vertical inertia at "
        "every fuselage station, and this analysis does not model it. Chapter "
        "15 resolves the fuselage inertia into a linear and a pitching load "
        "factor; the loads delivered here carry the linear half only, with the "
        "pitching acceleration taken as zero on the balanced trim cases these "
        "conditions come from. Closing that gap is open item M4-21. The "
        "greatest-vertical-inertia condition above is the one this limitation "
        "bears on most directly.",
    ]


def _body_critical(project: Project,
                   results: Mapping[str, Optional[ModuleResult]], *,
                   system: UnitSystem, plan: Sequence[SectionPlan]) -> Section:
    """4.3 -- the critical fuselage loads, as the manual summarises them."""
    tail_ref = section_ref(plan, "tail_loads")
    summary = _critical_summary_table(project, results, system)
    pull_up = _pull_up_table(project, results, system, tail_ref)
    body = [
        "This subsection is the critical-fuselage summary of Reference 1 page "
        "198: the conditions that size the fuselage, each stated with the "
        "quantities the manual prints for it. It is the first thing a reader "
        "of this section wants and is therefore given before the machinery "
        "that produces the distributions.",
        "Two of the seven conditions are pull-up maneuvers whose quantities "
        "are derived in the tail analysis. They are printed here, where the "
        "fuselage question is asked, with a reference to " + tail_ref + ", "
        "where they are derived; they are read from that analysis and not "
        "recomputed, so the two sections state the same numbers.",
    ]
    body += _body_advisories(plan)
    tables = [t for t in (summary, pull_up) if t is not None]
    if not tables:
        return Section("", body=body,
                       absent_reason=("The fuselage analysis produced no "
                                      "conditions for this project."))
    return Section("", body=body, tables=tables)


def _fitting_table(project: Project, system: UnitSystem) -> Optional[Table]:
    """4.4's wing-attach fitting loads, with their spar provenance beside them.

    The provenance is in the table and not in a footnote, because these are the
    sizing loads for the wing-attach fittings and on an airplane whose spar
    stations were never entered they are sized on an estimate (OR-97).
    """
    net = _body_net(project)
    if not net:
        return None
    u = Units(system)
    rows = []
    for result in net:
        if result.r_front is None or result.r_rear is None:
            continue
        sf = float(getattr(result, "safety_factor", ULTIMATE_FACTOR))
        ref = getattr(result, "case_ref", None)
        rows.append([
            getattr(ref, "case_id", "") or "--",
            u.plain(result.x_front, "length"),
            u.load(result.r_front, "force", sf),
            u.plain(result.x_rear, "length"),
            u.load(result.r_rear, "force", sf),
            u.load(result.m_unbalanced, "moment", sf),
            "assumed" if result.spars_assumed else "entered",
            format_value(sf),
        ])
    if not rows:
        return None
    return Table(
        title="Wing-attach fitting loads (LIMIT)",
        columns=["Case", f"X front ({u.label('length')})",
                 f"R front ({u.ult_label('force')})",
                 f"X rear ({u.label('length')})",
                 f"R rear ({u.ult_label('force')})",
                 f"M unbalanced ({u.ult_label('moment')})", "Spars", "SF"],
        rows=rows, small=True,
        note=("The front and rear spar reactions that close the beam -- the "
              "sizing loads for the wing-attach fittings. The Spars column "
              "states where their stations came from: 'entered' is the "
              "geometry this airplane was measured at, 'assumed' is the "
              "estimator's, and a fitting load marked assumed is sized on a "
              "spar location nobody entered. The unbalanced moment is the "
              "moment the first pass leaves at the aft end, which these "
              "reactions carry. Every load is LIMIT with the factor stated and "
              "applied nowhere; the stations are geometry and are neither "
              "scaled nor marked."))


def _closure_sentence(project: Project, system: UnitSystem) -> str:
    """What the beam closed to, read off the aft end of each case.

    Chapter 15 ships no printed station oracle, so equilibrium closure is what
    this analysis is held to; a section that claims a beam closes and does not
    say to what is asking to be taken on trust.
    """
    net = _body_net(project)
    if not net:
        return ""
    u = Units(system)
    end_sz = end_myy = peak_sz = peak_myy = 0.0
    for result in net:
        stations = list(getattr(result, "stations", ()))
        if not stations:
            continue
        end_sz = max(end_sz, abs(stations[-1].sz))
        end_myy = max(end_myy, abs(stations[-1].myy))
        peak_sz = max(peak_sz, *(abs(s.sz) for s in stations))
        peak_myy = max(peak_myy, *(abs(s.myy) for s in stations))
    return (
        "The beam closes. Across every case in this section the shear left at "
        f"the aft-most station is at most {u.plain(end_sz, 'force')} "
        f"{u.label('force')} and the bending moment at most "
        f"{u.plain(end_myy, 'moment')} {u.label('moment')}, against peaks "
        f"along the body of {u.plain(peak_sz, 'force')} {u.label('force')} and "
        f"{u.plain(peak_myy, 'moment')} {u.label('moment')}: the residue of "
        "the integration, not a load. Chapter 15 publishes no "
        "station-by-station figures, so this closure is the acceptance "
        "criterion the distributions are held to, in place of a printed "
        "oracle.")


def _body_closure(project: Project, *, system: UnitSystem,
                  plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    """4.4 -- the closure of the beam and the wing-attach fitting loads."""
    table = _fitting_table(project, system)
    body = [
        "The fuselage beam is not in equilibrium under its inertia and its tail "
        "load alone: the two leave a vertical force and a moment over, and the "
        "wing carries both. This subsection states what the wing attachment "
        "carries and what is left at the aft end once it does.",
        _carry_through_sentence(project),
        _closure_sentence(project, system),
        "Every load in this subsection is LIMIT. The safety factor 14 CFR "
        "23.303 prescribes for each case is stated in its own row and is "
        "applied to nothing: this analysis delivers the loads, and the sizing "
        "analysis applies the factor. No special factor of 14 CFR Part 23 "
        "Subpart D -- the casting, bearing, fitting and control-surface-hinge "
        "factors of 23.619, 23.621, 23.623 and 23.625 -- is applied to any "
        "load in this document either. Those factors qualify a material "
        "allowable or a fitting's strength at the stress analysis, not the "
        "external load a loads analysis delivers, and the fitting loads above "
        "are the external loads. A fitting factor applied here would be "
        "applied twice.",
    ]
    body = [paragraph for paragraph in body if paragraph]
    if table is None:
        return Section("", body=body,
                       absent_reason=("This project produced no wing-attach "
                                      "fitting loads: see the distributions "
                                      "for why."))
    return Section("", body=body, tables=[table])


#: ``(figure key, station attribute, dimension, title)`` for 4.5.
#:
#: The two cumulative quantities, in the order the beam produces them. The
#: applied Fz is not plotted: it is an increment at a station, not a curve, and
#: it is tabulated in the appendix beside the shear it produces.
_BODY_DISTRIBUTION_FIGURES: Tuple[Tuple[str, str, str, str], ...] = (
    ("body_shear_sz", "sz", "force", "Vertical shear Sz"),
    ("body_bending_myy", "myy", "moment", "Bending moment Myy"),
)


def _body_distribution_figure(net: Sequence[BodyLoadResult], key: str, attr: str,
                              dim: str, title: str, system: UnitSystem,
                              critical: str) -> Figure:
    """One quantity along the body, every fuselage case on one axes."""
    if not net:
        return Figure(key=key, title=f"{title} (LIMIT)",
                      absent_reason=("the fuselage load distributions were not "
                                     "produced for this project."))
    u = Units(system)
    series = []
    for result, style in zip(net, _CASE_STYLES * 4):
        stations = list(getattr(result, "stations", ()))
        if not stations:
            continue
        sf = float(getattr(result, "safety_factor", ULTIMATE_FACTOR))
        ref = getattr(result, "case_ref", None)
        name = getattr(ref, "case_id", "") or getattr(result, "case", "")
        series.append(Series(
            f"{name} {getattr(result, 'case', '')}".strip(),
            [u.plain_value(s.x, "length") for s in stations],
            [u.load_value(getattr(s, attr), dim, sf) for s in stations], style))
    if not series:
        return Figure(key=key, title=f"{title} (LIMIT)",
                      absent_reason=("the fuselage load distributions carry no "
                                     "stations to plot."))
    return Figure(
        key=key, title=f"{title} (LIMIT)",
        data=PlotData(f"Fuselage station X ({u.label('length')})",
                      f"{title} ({u.ult_label(dim)})", series),
        caption=(f"{title} along the fuselage, every fuselage case on one axes. "
                 "The quantity is cumulative: it is accumulated nose to tail, "
                 "so a value is what the body carries across that station and "
                 "not the load applied at it. Both curves return to zero at the "
                 "aft end, which is the closure the beam is held to. All values "
                 "are LIMIT, each case stating the safety factor it does not "
                 f"apply, as set out in {critical}."))


def _body_distributions(project: Project, *, system: UnitSystem,
                        plan: Sequence[SectionPlan]) -> Section:
    """4.5 -- the net distributions of every fuselage case."""
    net = _body_net(project)
    critical = subsection_ref(plan, _BODY_STEP, _BODY_CRITICAL)
    body = [
        "The distributions below are the net fuselage loads: the inertia of "
        "the station masses, the balancing tail air load and the wing "
        "carry-through reaction, summed nose to tail, which is what the body "
        "structure carries. The station values behind these curves are "
        "tabulated in "
        + (appendix_ref(BODY_LOAD_STATIONS) or "the appendix") + ".",
    ]
    # A closure-artifact result has no wing attachment to react at: the beam was
    # closed by a correction spread over the whole body, which relieves the wing
    # region and loads the tail cone with a moment nothing applies there. Its
    # station table is a closure artifact and not a load distribution, and
    # printing it would publish a load with no physical source (OR-98). Stated
    # through the same gap-state machinery an unbuilt section uses.
    if net and any(getattr(r, "closure_artifact", False) for r in net):
        return Section("", body=body, absent_reason=(
            "The wing carry-through could not be derived for this project, so "
            "the unbalanced moment was closed by a self-equilibrated "
            "correction spread over the whole body rather than reacted where "
            "the wing attaches. The beam closes, but the correction has no "
            "physical source: it relieves the wing region and loads the tail "
            "cone with a moment nothing applies there. The resulting station "
            "table is a closure artifact and is not published as a load "
            "distribution. Entering the wing front and rear spar stations "
            "gives the Chapter 15 carry-through reaction and this subsection "
            "its distributions."), absent_lead="Not published")
    figures = [_body_distribution_figure(net, key, attr, dim, title, system,
                                         critical)
               for key, attr, dim, title in _BODY_DISTRIBUTION_FIGURES]
    return Section("", body=body, figures=figures)


def _fuselage_loads(project: Project,
                    results: Mapping[str, Optional[ModuleResult]], *,
                    system: UnitSystem, plan: Sequence[SectionPlan]) -> Section:
    """Section 4 -- Fuselage Loads, in its five subsections (OR-94).

    Five rather than section 3's four: the manual's own critical-fuselage
    summary is what an analyst turns to first, and folding it into a subsection
    about closure machinery would make it a footnote to the machinery.
    """
    return Section("", body=[
        "This section states the fuselage loads: the beam they were run on, "
        "the cases run, the critical fuselage loads the manual summarises, the "
        "closure of the beam and the loads it puts into the wing attachment, "
        "and the distributions along the body. Every load case delivered here "
        "is LIMIT with its safety factor stated and not applied, and every "
        "quantity that is not a delivered load says which it is.",
    ], subsections=[
        replace(_body_beam(project, system=system, plan=plan),
                title="The fuselage beam"),
        replace(_body_cases(project, results, system=system, plan=plan),
                title="Load cases and notation"),
        replace(_body_critical(project, results, system=system, plan=plan),
                title="Critical fuselage loads"),
        replace(_body_closure(project, system=system, plan=plan),
                title="Beam closure and wing-attach fitting loads"),
        replace(_body_distributions(project, system=system, plan=plan),
                title="Load distributions"),
    ])


# --------------------------------------------------------------------------- #
# Appendix C -- fuselage loads by station (OR-101)
# --------------------------------------------------------------------------- #
def _body_station_appendix(project: Project, *, system: UnitSystem,
                           plan: Sequence[SectionPlan]) -> Section:
    """Appendix C: the fuselage set, applied in C.1 and carried in C.2.

    Split on OR-59's reasoning unchanged (OR-144): the applied load and the
    load carried are different quantities, and a reader who takes one for the
    other builds the wrong model. They shared one table until 2026-09-07, with
    the distinction carried by a sentence in the note -- the arrangement §12
    rejected for the wing, for a reason that was never the wing's alone.

    A **view of the export owner**, not a second assembler: C.1's rows are
    ``sbeam_bridge.applied_loads("fuselage", ...)``, the same list
    ``fuselage_applied_loads.csv`` is written from, converted at this
    document's own boundary rather than the solver deck's.
    """
    from ..export.sbeam_bridge import applied_loads, body_station_gids

    net = _body_net(project)
    body = [
        "This appendix carries the fuselage load distributions of "
        + section_ref(plan, _BODY_STEP) + " in full: every case at every "
        "station of the beam stated in "
        + subsection_ref(plan, _BODY_STEP, _BODY_BEAM) + ". It is the same "
        "result the figures are drawn from, printed rather than plotted, and "
        "the same rows the fuselage span-load export writes.",
        "It is given in two parts, because they are two different quantities "
        "and a reader who takes one for the other builds the wrong model. The "
        "first is the load applied at each station -- what a structural model "
        "is given. The second is the load carried across it -- what that model "
        "should return. The grid identifier is the one the exported deck uses, "
        "so a row here can be found in the model it built.",
    ]
    absent_c = Section("", body=body, absent_reason=(
        "The fuselage load distributions were not produced for this project, "
        "so there is nothing to tabulate."), page_break=True)
    if not net:
        return absent_c
    u = Units(system)
    lra = _fuselage_lra(project)
    applied = applied_load_table(
        applied_loads("fuselage", net, project), system=system,
        title="Applied fuselage loads by station (LIMIT)",
        note=("The load applied at each station of the body beam. X, Y and Z "
              "place the station on the airplane: the beam runs down the "
              "centre plane on the fuselage loads reference axis, so Y is zero "
              "by construction and Z is that axis's waterline -- the position "
              "of the structure, not of the mass it carries, which the beam "
              "table states separately. All six components are printed so that "
              "a zero cannot be read as an omission. Fz is the whole applied "
              "set: Fx and Fy are zero for every row because the body beam has "
              "no fore-aft or lateral producer, and Mx, My and Mz because a "
              "station applies a force and no free moment -- every moment the "
              "beam carries is those forces acting through the arms these "
              "coordinates state. Moments are right-handed about the airplane "
              "axes. Every load is LIMIT and states in its own row the factor "
              "it does not apply; the station is geometry and is neither "
              "scaled nor marked."))
    rows = []
    for result in net:
        ref = getattr(result, "case_ref", None)
        name = getattr(ref, "case_id", "") or getattr(result, "case", "")
        sf = float(getattr(result, "safety_factor", ULTIMATE_FACTOR))
        for gid, station in zip(body_station_gids(result), result.stations):
            rows.append([
                name, str(gid), u.plain(station.x, "length"),
                u.load(station.sz, "force", sf),
                u.load(station.myy, "moment", sf),
                format_value(sf),
            ])
    if applied is None or not rows:
        return absent_c
    carried = Table(
        title="Cumulative fuselage loads by station (LIMIT)",
        columns=["Case", "GID", f"X ({u.label('length')})",
                 f"Sz ({u.ult_label('force')})",
                 f"Myy ({u.ult_label('moment')})", "SF"],
        rows=rows, small=True,
        note=("What the fuselage carries at each station: the applied loads of "
              "C.1 accumulated nose to tail, as defined in the notation of "
              + subsection_ref(plan, _BODY_STEP, _BODY_CASES) + ". The station "
              "coordinates are printed once, with the applied set. These are "
              "the beam's own quantities and not the body-axis vector of the "
              "table above; Myy is about the fuselage loads reference axis, "
              "which runs fore and aft, so the letter and the airplane axis "
              "agree here. The cumulative columns close to zero at the aft "
              "end. Every load is LIMIT and states the factor it does not "
              "apply."))
    if lra is None:
        body.append(
            "The fuselage loads reference axis is not resolvable for this "
            "project, so the waterline column states zero rather than a "
            "guessed height. The station X and every load are unaffected.")
    return Section("", body=body, page_break=True, landscape=True,
                   subsections=[
                       Section("Applied loads", tables=[applied]),
                       Section("Cumulative loads", tables=[carried]),
                   ])


# --------------------------------------------------------------------------- #
# Sections 5 and 6 -- tail loads, by surface (OR-128 ... OR-137)
# --------------------------------------------------------------------------- #
#: The surface each tail section is about, and how the document names it.
#:
#: Read by every builder below, so the horizontal and the vertical section are
#: one set of code parameterised by component rather than two that have to be
#: kept in step -- the partition of OR-129 expressed once. ``surface`` is the
#: reader's noun, ``control`` the movable surface's, and ``span_axis`` names what
#: the spanwise coordinate *is*, which differs between the two: a horizontal
#: tail's is a butt line and a fin's is a waterline.
_TAIL_SURFACES = {
    "htail": {
        "surface": "horizontal tail", "control": "elevator",
        "span_axis": "butt line", "control_load_key": "elevator_load",
        "control_load_label": "Elevator load",
    },
    "vtail": {
        "surface": "vertical tail", "control": "rudder",
        "span_axis": "waterline", "control_load_key": "load_on_rudder",
        "control_load_label": "Rudder load",
    },
}


def _tail_critical(project: Project, component: str) -> List[CriticalCondition]:
    """The critical conditions for one surface, from SELECT's single owner.

    :func:`sloads.modules.select.default_critical` is the owner every other
    consumer reads -- TAILDIST distributes exactly this list -- so the report
    states the same case set the analysis ran and cannot select a tenth of its
    own. The same route section 4 takes to the fuselage blocks (OR-109).
    """
    from ..modules.select import default_critical

    try:
        return [c for c in default_critical(project).conditions
                if c.component == component]
    except (ValueError, TypeError, ZeroDivisionError):
        return []


def _tail_chordwise(project: Project, component: str) -> List[TailChordResult]:
    """The chordwise distributions for one surface (TAILDIST's own builder)."""
    from ..modules.taildist import build_tail_chordwise

    try:
        return [r for r in build_tail_chordwise(project) if r.component == component]
    except (ValueError, TypeError, ZeroDivisionError, KeyError):
        return []


def _tail_spanwise(project: Project, component: str) -> List[TailSpanResult]:
    """The spanwise results for one surface (plan 09's ``tail_span``).

    Read from the builder rather than from a ``ModuleResult``, which is OR-95's
    ruling one section over: the station tables live nowhere else. That the
    producer is **not an oracle step** is the whole of OR-130a -- the spanwise
    loads are a modern deliverable and enter as appendix content on the
    Appendix B precedent, not as a derived section claiming a program that
    never existed.
    """
    from ..modules.tail_span import build_tail_span

    try:
        return list(build_tail_span(project).get(component, []))
    except (ValueError, TypeError, ZeroDivisionError, KeyError):
        return []


def _value_of(condition, key: str):
    """One published ``LoadValue`` of ``condition`` by key, or ``None``."""
    return next((v for v in getattr(condition, "loads", ()) if v.key == key), None)


def _tail_case_id(condition) -> str:
    """The case identity a tail row prints: the stamped id, else the V-n case."""
    ref = getattr(condition, "case_ref", None)
    return getattr(ref, "case_id", "") or str(getattr(condition, "case", "") or "--")


# --- 5.1 / 6.1 -- the surface the loads were run on ------------------------- #
def _tail_lra_planform_figure(project: Project, component: str,
                              results: Sequence[TailSpanResult],
                              system: UnitSystem) -> Figure:
    """The tail planform with its control surface and its loads reference axis.

    Section 3.1's figure for the wing, one surface over: the outline a reader
    recognises, with the axis every distributed load in the section is stated
    about drawn through the stations it is evaluated at. Section 2.1 draws the
    same planform without the axis -- that figure answers "what shape is it",
    this one answers "where are the loads".
    """
    from .planform_tex import LRA_STYLE, OUTLINE_STYLE, REGION_STYLES

    names = _TAIL_SURFACES[component]
    key = f"planform_{component}_lra"
    title = f"{names['surface'].capitalize()} loads reference axis"
    surface = project.geometry.by_name(component) if project.geometry else None
    if surface is None:
        return Figure(key=key, title=title, absent_reason=(
            f"the project defines no {names['surface']} planform, so there is "
            "no surface to draw an axis on."))
    if not results:
        return Figure(key=key, title=title, absent_reason=(
            f"the {names['surface']} spanwise loads were not produced, so the "
            "axis they are stated about cannot be drawn."))
    scale, length_units = _length_channel(system)
    frame = "butt" if component == "htail" else "water"
    mirror = bool(surface.symmetric) and frame == "butt"
    try:
        series = _region_series(project, component, OUTLINE_STYLE,
                                names["surface"].capitalize(), mirror, frame, scale)
        control = _CONTROL_OF[component]
        if project.geometry is not None and project.geometry.by_name(control):
            series += _region_series(project, control, REGION_STYLES[0],
                                     names["control"].capitalize(), mirror,
                                     frame, scale)
    except ValueError as problem:
        return Figure(key=key, title=title, absent_reason=(
            f"the {names['surface']} planform cannot be drawn as entered -- "
            f"{problem}"))
    stations = list(getattr(results[0], "stations", ()))
    # The in-plane pair of the resolved airplane point: a butt-line frame plots
    # (X, Y) and a waterline frame (X, Z). Taking the *station's* own second
    # coordinate instead is what drew the fin's axis flat along its root.
    airplane = [_station_point(st, component) for st in stations]
    points = [_oriented(frame, x * scale,
                        (y if frame == "butt" else z) * scale)
              for x, y, z in airplane]
    axis = getattr(results[0], "torsion_axis", "") or "loads reference axis"
    series.append(Series(f"Loads reference axis ({axis})",
                         [x for x, _y in points], [y for _x, y in points],
                         LRA_STYLE))
    x_label, y_label = _PLANFORM_AXES[frame]
    return Figure(
        key=key, title=title,
        data=PlotData(f"{x_label} ({length_units})",
                      f"{y_label} ({length_units})", series,
                      [("", x, y) for x, y in points],
                      points_label="Load stations"),
        caption=(f"The {names['surface']} and its {names['control']} as "
                 f"entered, with the loads reference axis of this analysis "
                 f"({axis}) drawn through the load stations every distributed "
                 f"load in this section is stated at. The marked points are "
                 f"those stations. Nothing in this figure is a load."))


#: The movable surface each tail component carries, for the planform figure.
_CONTROL_OF = {"htail": "elevator", "vtail": "rudder"}


def _station_point(station, component: str) -> Tuple[float, float, float]:
    """One tail station as an airplane ``(x, y, z)`` point.

    Through :func:`sloads.export.coordinates.tail_station_to_airplane`, the
    owner the exported deck and Appendices D and E already use -- never off
    ``station.y``/``station.z``, which are **not** airplane axes on a fin.

    ``WingStationLoad`` calls its coordinates airplane axes and for the
    horizontal tail they are, which is why reading them directly worked in
    section 5 and was wrong in section 6: on the vertical tail ``y`` is the
    span coordinate in the surface's own plane and ``z`` is the root offset the
    span is measured from. Read at face value, the fin's loads reference axis
    drew as a flat line along its root waterline (owner, 2026-09-07) and its
    station table labelled the height above the root a butt line. One owner
    rather than a second convention here is what makes the figure, the table
    and the deck agree by construction.
    """
    from ..export.coordinates import tail_station_to_airplane

    return tail_station_to_airplane(station.x, station.y, component, station.z)


def _tail_lra_station_table(results: Sequence[TailSpanResult], component: str,
                            system: UnitSystem, *,
                            withheld: bool = False) -> Optional[Table]:
    """The tail's loads reference axis, station by station.

    Printed even where OR-133 withholds the loads applied at these stations
    (owner, 2026-09-07). These are entered geometry resolved through a planform
    -- the same numbers Section 2's three-view is drawn from -- and withholding
    verifiable geometry to document a *load* limitation would cost the reader
    something real while documenting nothing. ``withheld`` puts the reason in
    the table's own note, so a station list above a withheld subsection cannot
    read as loads that merely failed to compute.
    """
    if not results:
        return None
    stations = list(getattr(results[0], "stations", ()))
    if not stations:
        return None
    names = _TAIL_SURFACES[component]
    u = Units(system)
    length = u.label("length")
    rows = []
    for index, station in enumerate(stations, start=1):
        x, y, z = _station_point(station, component)
        rows.append([str(index), u.plain(x, "length"), u.plain(y, "length"),
                     u.plain(z, "length")])
    axis = getattr(results[0], "torsion_axis", "") or "loads reference axis"
    return Table(
        title=f"Loads reference axis by station ({axis})",
        columns=["Station", f"Station X ({length})", f"Butt line Y ({length})",
                 f"Waterline Z ({length})"],
        rows=rows, small=True,
        note=("The load stations the distributed air load and the surface's own "
              "inertia are evaluated at, tip to tip. These are geometry: "
              "nothing here is a load, nothing is scaled and nothing carries a "
              f"safety factor. The point is in airplane axes, so the "
              f"{names['span_axis']} is the coordinate that runs with the span "
              f"and the other two are fixed by where the surface is mounted."
              + (" The loads applied at these stations are withheld for this "
                 "airplane's tail arrangement, and the reason is stated in "
                 "full with this section's spanwise loads. The stations "
                 "themselves are unaffected by that restriction: they are "
                 "where the loads act, not what the loads are."
                 if withheld else "")))


def _tail_inputs(project: Project, component: str, *, system: UnitSystem,
                 plan: Sequence[SectionPlan]) -> Section:
    """5.1 / 6.1 -- the surface data the load cases were run from."""
    names = _TAIL_SURFACES[component]
    results = _tail_spanwise(project, component)
    figure = _tail_lra_planform_figure(project, component, results, system)
    withheld = _vtail_withheld(project, component)
    tables = [t for t in (_tail_constants_table(project, component),
                          _tail_lra_station_table(results, component, system,
                                                  withheld=withheld))
              if t is not None]
    body = [
        f"This subsection states the {names['surface']} data the load cases of "
        f"this section were run from: the surface and its {names['control']}, "
        f"the axis the distributed loads are stated about, and the aerodynamic "
        f"constants inside every load below. The planform's own dimensions are "
        f"stated in " + section_ref(plan, "configuration_layout") + " and are "
        "not repeated here.",
        f"The loads reference axis is the beam the {names['surface']}'s "
        f"distributed loads are applied to and its torsion is stated about. It "
        f"is a structural axis, not an aerodynamic one: the chordwise pressures "
        f"later in this section are stated about the surface's own chord, and "
        f"the two are related by geometry rather than by a further analysis.",
    ]
    return Section("", body=body, figures=[figure], tables=tables)


# --- 5.2 / 6.2 -- the conditions and how they were chosen ------------------- #
#: What each section says its method searched, in the section's own terms
#: (OR-131): the categories differ, so neither section may borrow the other's.
_TAIL_METHOD = {
    "htail": (
        "The horizontal tail's design conditions are the largest up and down "
        "balancing loads of 14 CFR 23.421, the unchecked and checked manoeuvre "
        "loads of 23.423(a) and 23.423(b), the positive and negative gust loads "
        "of 23.425(a)(1), and the unsymmetrical load of 23.427(a) taken over "
        "them."),
    "vtail": (
        "The vertical tail's design conditions are the sudden full rudder "
        "deflection of 14 CFR 23.441(a)(1), the yaw to a 19.5 degree sideslip "
        "with the rudder held of 23.441(a)(2), the 15 degree yaw with the "
        "rudder neutral of 23.441(a)(3), and the lateral gust at the design "
        "cruising speed of 23.443(b)."),
}


def _tail_conditions_section(project: Project, component: str, *,
                             system: UnitSystem,  # noqa: ARG001
                             plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    """5.1 / 6.1 -- the design conditions and the search that produced them."""
    names = _TAIL_SURFACES[component]
    conditions = _tail_critical(project, component)
    body = [
        _TAIL_METHOD[component],
        "The candidate set for every one of them is the entire balanced "
        "flight envelope -- one balanced point per condition, loading and "
        "altitude -- filtered only by the flight condition each requirement "
        "names, from which the governing point is the extreme of that "
        "requirement's own measure. The requirement of 23.333(b) that each "
        "combination of airspeed and load factor be investigated is discharged "
        "by balancing the whole matrix; the selection below is the reduction of "
        "that matrix to design conditions, not a sample of it.",
        "Every condition carries its load resolved into two parts: an "
        "angle-of-attack load acting at the quarter chord of the mean "
        "aerodynamic chord, and a camber load acting at the half chord. Their "
        "sum is the total load on the surface. The split is not presentational "
        "-- it is what the chordwise distribution is built from, and it is the "
        "reason the same total can produce different pressures on the surface "
        "in two different conditions.",
    ]
    if component == "htail":
        body.append(
            "The unsymmetrical condition of 23.427(a) is a redistribution of "
            "the largest of the conditions above, not an eleventh search: the "
            "governing magnitude is applied to one side and a stated percentage "
            "of it to the other. This analysis includes the unchecked manoeuvre "
            "conditions among the candidates it is taken over. The worked "
            "example in the reference does not, and reports a smaller load in "
            "consequence; the program listing the reference itself prints "
            "does, and 23.427(a) applies to the loads prescribed in 23.421 "
            "through 23.425, which spans the 23.423 unchecked case. The listing "
            "and the regulation govern here, the difference is a registered "
            "deviation from the printed example, and the methods statement "
            "accompanying this analysis declares it.")
    # OR-131, both halves: the flaps-extended gust of 23.425(a)(2) is a
    # *horizontal* tail requirement, and stating it under the vertical tail --
    # which 23.441 and 23.443 give no flapped counterpart -- would have section
    # 6 borrowing section 5's method to describe an absence that is not its own.
    absences = []
    if component == "htail":
        absences.append(
            "This analysis selects its conditions with the flaps retracted. The "
            "flaps-extended gust conditions of 23.425(a)(2) are computed where a "
            "flapped envelope is present and are absent here rather than assumed "
            "to be non-critical.")
    if component == "htail":
        # The pointer, not the statement: OR-133 puts the statement in full with
        # the loads it withholds, and a reader who starts at the horizontal tail
        # must not meet the restriction for the first time two sections later.
        absences.append(_NON_CONVENTIONAL_POINTER)
    body.extend(absences)
    if not conditions:
        return Section("", absent_reason=(
            f"no {names['surface']} design conditions were produced for this "
            "project, so there is nothing to state a method for."))
    return Section("", body=body, tables=[
        _tail_category_table(conditions,
                             short=_vtail_withheld(project, component))])


def _tail_category_table(conditions: Sequence[CriticalCondition], *,
                         short: bool = False) -> Table:
    """The register: one row per condition, with the requirement it answers.

    ``short`` is OR-133a: on a non-conventional tail this set omits a condition,
    and a four-row table that looks complete reads as a measured completeness
    (OR-61's argument, one deliverable over). The note names the missing case.
    """
    return Table(
        title="Design conditions analysed",
        columns=["Case", "Condition", "14 CFR", "SF"],
        rows=[[_tail_case_id(c), getattr(c, "label", ""),
               getattr(c, "far_reference", "") or "--",
               format_value(_required_sf(c))] for c in conditions],
        note=("One governing case per requirement, identified by the case "
              "reference every table in this section keys on. The safety factor "
              "is the one 14 CFR 23.303 prescribes for that requirement; it is "
              "stated here and with every load, and applied nowhere."
              + (_MISSING_CONDITION_NOTE if short else "")))


# --- 5.2 / 6.2 -- the critical-case summary --------------------------------- #
def _tail_summary_table(project: Project, component: str,
                        system: UnitSystem) -> Optional[Table]:
    """5.2 / 6.2 -- one row per design condition, read across.

    The split and the control-surface load are taken from the condition's own
    published values, so this table states what the analysis produced and
    computes nothing. ``LT25``/``LT50`` come from the condition's fields rather
    than from a load key, because the label those keys carry differs by
    condition family -- balancing calls the camber term an elevator load and the
    manoeuvre families call it a deflection increment -- while the field is one
    quantity with one meaning across all of them (M4-9: the key is the machine
    identity, the label is display text).
    """
    conditions = _tail_critical(project, component)
    if not conditions:
        return None
    names = _TAIL_SURFACES[component]
    u = Units(system)
    force = u.ult_label("force")
    columns = ["Case", f"Total load ({force})",
               f"AoA load, quarter chord ({force})",
               f"Camber load, half chord ({force})",
               f"{names['control_load_label']} ({force})",
               "Sides RH / LH", "SF"]
    rows = []
    for condition in conditions:
        sf = _required_sf(condition)
        total = _value_of(condition, "total_tail_load") \
            or _value_of(condition, "total_tail_load_cp_25_pct")
        control = _value_of(condition, names["control_load_key"])
        rh, lh = _value_of(condition, "rh_side_load"), _value_of(condition, "lh_side_load")
        sides = "--"
        if rh is not None and lh is not None:
            # OR-135: the split is printed in the row that carries the load, and
            # never in a table of its own. Alone, a control-surface load on an
            # unsymmetrical case reads as one surface's load, when the case's
            # whole content is that the two sides differ.
            sides = f"{u.load(rh.value, 'force', sf)} / {u.load(lh.value, 'force', sf)}"
        rows.append([
            _tail_case_id(condition),
            u.load(total.value, "force", sf) if total is not None else "--",
            u.load(getattr(condition, "lt25", None), "force", sf)
            if getattr(condition, "lt25", None) is not None else "--",
            u.load(getattr(condition, "lt50", None), "force", sf)
            if getattr(condition, "lt50", None) is not None else "--",
            u.load(control.value, "force", sf) if control is not None else "--",
            sides, format_value(sf)])
    return Table(
        title=f"Critical {names['surface']} loads (LIMIT)",
        columns=columns, rows=rows,
        note=(f"Every load is LIMIT and states the safety factor 14 CFR 23.303 "
              f"prescribes for its condition; nothing in this table has been "
              f"multiplied by it. The angle-of-attack and camber loads sum to "
              f"the total. The {names['control']} load is the part of the total "
              f"the {names['control']} itself carries -- the camber share aft of "
              f"the hinge line plus its share of the angle-of-attack load -- and "
              f"is what the {names['control']} and its system are sized to, not "
              f"the surface total beside it."
              + (_MISSING_CONDITION_NOTE
                 if _vtail_withheld(project, component) else "")))


def _tail_state_table(project: Project, component: str,
                      system: UnitSystem) -> Optional[Table]:
    """The aerodynamic state each condition was computed at (note 35 AS-2).

    Beside the loads rather than inside them: an angle and a dynamic pressure
    are not loads, carry no safety factor and must not be scaled or marked, so
    putting them in the load table above would mean a table whose columns obey
    two different rules (CONVENTIONS section 3).
    """
    conditions = _tail_critical(project, component)
    if not conditions:
        return None
    names = _TAIL_SURFACES[component]
    angle = "deg"
    basis = _inertia_basis(project, component)
    q_scale, q_units = _scalar_channel("lb/ft^2", system)
    i_scale, i_units = _scalar_channel("slug-ft^2", system)
    rows = []
    for condition in conditions:
        extra = _value_of(condition, "pitch_inertia_iyy") \
            or _value_of(condition, "yaw_inertia_izz")
        rows.append([
            _tail_case_id(condition),
            _fmt_angle(getattr(condition, "alpha_tail_deg", None)),
            _fmt_angle(getattr(condition, "delta_deg", None)),
            _fmt_angle(getattr(condition, "beta_deg", None)),
            _scalar_cell(getattr(condition, "q_psf", None), q_scale),
            _scalar_cell(extra.value if extra is not None else None, i_scale),
        ])
    return Table(
        title="Aerodynamic state of each condition",
        columns=["Case", f"Surface angle of attack ({angle})",
                 f"{names['control'].capitalize()} deflection ({angle})",
                 f"Sideslip ({angle})",
                 f"Dynamic pressure ({q_units})", f"Inertia ({i_units})"],
        rows=rows,
        note=(basis +
              "The state each load was computed at, published by the condition "
              "itself rather than reconstructed here. An empty cell is a "
              "quantity the method does not define for that condition -- a "
              "symmetric pitch-plane condition has no sideslip, the checked "
              "manoeuvre increment is a pitching-acceleration inertia term with "
              "no deflection of its own, and the lateral gust requirement is "
              "linear in airspeed and so has no dynamic-pressure term. None of "
              "these is a load: none is scaled and none carries a factor."))


def _inertia_basis(project: Project, component: str) -> str:
    """Whether the inertia in the state table was entered or estimated (OR-135).

    Provenance in the same visual field as the value (OR-97): the rod estimate
    measured **49 per cent** over WTONECG's database value on the Cessna 210
    with nothing on the page saying an estimate was in play (C210-25), and a
    number that large cannot be read correctly without its basis.

    Read off the entered field rather than recomputed: ``izz_slugft2`` blank is
    what selects ``select.default_side_gust_izz``, so the field *is* the
    provenance and asking it is not a second derivation of one.
    """
    if component != "vtail":
        # The horizontal tail's checked pair states its own pitch inertia, which
        # SELECT takes from the weight data base in every case; there is no
        # second route for it to have come by, so there is nothing to state.
        return ""
    vtail = getattr(project, "vtail_loads", None)
    entered = float(getattr(vtail, "izz_slugft2", 0.0) or 0.0) > 0.0
    if entered:
        return ("The yaw inertia is the value entered for this airplane. ")
    return (
        "The yaw inertia was not entered for this airplane and is estimated "
        "from the airplane's weight and length on a uniform-rod idealisation. "
        "That estimate has been measured 49 per cent above a database value on "
        "a comparable airplane, and the lateral gust load of 14 CFR 23.443(b) "
        "varies with it, so the condition below is stated on an estimate and "
        "not on a measurement. Entering the yaw inertia replaces it. ")


def _fmt_angle(value) -> str:
    """An angle cell: the value, or empty where the method defines none."""
    return "--" if value is None else format_value(value)


def _tail_summary(project: Project, component: str, *,
                  system: UnitSystem,
                  plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    """5.2 / 6.2 -- the critical loads, with the state that produced them."""
    names = _TAIL_SURFACES[component]
    table = _tail_summary_table(project, component, system)
    if table is None:
        return Section("", absent_reason=(
            f"no {names['surface']} design conditions were produced, so there "
            "are no critical loads to summarise."))
    state = _tail_state_table(project, component, system)
    # The state ahead of the loads (owner, 2026-09-07): a reader checks what the
    # airplane was doing before reading what that did to the surface, and the
    # loads table is the one they stop at.
    tables = ([state] if state is not None else []) + [table]
    return Section("", body=[
        f"The design loads for the {names['surface']}, one row per condition. "
        f"These are the loads the {names['surface']} and its supporting "
        f"structure are sized to; the distributions in the subsections that "
        f"follow spread exactly these totals over the surface and introduce no "
        f"load of their own.",
    ], tables=tables)


def _scalar_channel(units: str, system: UnitSystem) -> Tuple[float, str]:
    """``(scale, units)`` taking one entered Imperial scalar into ``system``.

    :func:`_length_channel` generalised to any unit string, and for its reason:
    :func:`sloads.units.convert_results` is the single conversion owner, and a
    constant multiplied in here would be the drift the units history is the
    cautionary precedent for. Used for the quantities that are neither loads nor
    lengths -- a dynamic pressure in pounds per square foot, a mass moment of
    inertia in slug-feet squared -- which have no column in the deliverable unit
    set because nothing is ever sized to them.
    """
    probe = ConditionResult(title="", far_reference="",
                            values=[LoadValue("probe", 1.0, units, key="probe")])
    converted = convert_results([probe], system)[0].values[0]
    return float(converted.value), converted.units


def _scalar_cell(value, scale: float) -> str:
    """One converted scalar cell, or ``--`` where the method defines none."""
    return "--" if value is None else format_value(value * scale)


# --- 5.3 / 6.3 -- the chordwise distribution -------------------------------- #
def _tail_chord_stations_table(results: Sequence[TailChordResult],
                               system: UnitSystem) -> Optional[Table]:
    """The five chord stations the pressure profile is defined at.

    Printed once rather than repeated per condition: the stations are a property
    of the surface's geometry -- the average chord and the hinge line -- and are
    identical in every condition. Repeating them per case would invite a reader
    to look for a difference that cannot exist.
    """
    if not results:
        return None
    scale, length = _length_channel(system)
    stations = list(getattr(results[0], "stations", ()))
    if not stations:
        return None
    meanings = ["Leading edge", "Quarter chord", "Trailing edge",
                "Hinge line", "Chord less the hinge-line station"]
    rows = [[f"X{i}", meaning, format_value(station.x * scale)]
            for i, (station, meaning) in enumerate(zip(stations, meanings), start=1)]
    return Table(
        title="Chord stations of the pressure profile",
        columns=["Station", "Location", f"Distance aft of the leading edge ({length})"],
        rows=rows,
        note=("The profile is defined on the surface's average chord, which is "
              "its area divided by its span. The stations are geometry and are "
              "the same in every condition; only the pressures at them change."))


def _tail_pressure_table(results: Sequence[TailChordResult],
                         system: UnitSystem) -> Optional[Table]:
    """One row per condition, the net pressure at each of the five stations."""
    if not results:
        return None
    u = Units(system)
    force = u.ult_label("force")
    pressure = _scalar_channel("lb/in^2", system)
    columns = ["Case", f"AoA load ({force})", f"Camber load ({force})"] + [
        f"psi(X{i}) ({pressure[1]})" for i in range(1, 6)] + ["SF"]
    rows = []
    for result in results:
        sf = float(getattr(result, "safety_factor", ULTIMATE_FACTOR) or ULTIMATE_FACTOR)
        row = [_tail_case_id(result),
               u.load(getattr(result, "lt25", None), "force", sf),
               u.load(getattr(result, "lt50", None), "force", sf)]
        row += [_scalar_cell(s.psi, pressure[0])
                for s in getattr(result, "stations", ())]
        row.append(format_value(sf))
        rows.append(row)
    return Table(
        title="Net chordwise pressure (LIMIT)", columns=columns, rows=rows,
        note=("The net pressure at each chord station: the sum of an additive "
              "distribution carrying the angle-of-attack load -- four times the "
              "average pressure at the leading edge, the average at the quarter "
              "chord, zero at the trailing edge -- and a camber distribution "
              "carrying the camber load, constant from the hinge line aft. "
              "Every pressure is LIMIT and states the factor its condition does "
              "not apply."))


def _tail_chord_figure(results: Sequence[TailChordResult], component: str,
                       system: UnitSystem) -> Figure:
    """The pressure profile, every condition on one axes."""
    names = _TAIL_SURFACES[component]
    key = f"chordwise_{component}"
    title = f"{names['surface'].capitalize()} chordwise pressure"
    if not results:
        return Figure(key=key, title=f"{title} (LIMIT)", absent_reason=(
            f"the {names['surface']} chordwise distributions were not produced "
            "for this project."))
    scale, length = _length_channel(system)
    p_scale, p_units = _scalar_channel("lb/in^2", system)
    series = []
    for result, style in zip(results, _CASE_STYLES * 4):
        stations = sorted(getattr(result, "stations", ()), key=lambda s: s.x)
        if not stations:
            continue
        series.append(Series(str(getattr(result, "case", "")),
                             [s.x * scale for s in stations],
                             [s.psi * p_scale for s in stations], style))
    if not series:
        return Figure(key=key, title=f"{title} (LIMIT)", absent_reason=(
            f"the {names['surface']} distributions carry no chord stations to plot."))
    return Figure(
        key=key, title=f"{title} (LIMIT)",
        data=PlotData(f"Distance aft of the leading edge ({length})",
                      f"Net pressure ({p_units})", series),
        caption=(f"Net pressure along the {names['surface']}'s average chord, "
                 "every design condition on one axes. The profiles cross zero "
                 "where the angle-of-attack and camber contributions cancel, "
                 "which is why a condition with a large total load can carry "
                 "little pressure over part of the chord. All values are LIMIT."))


def _tail_constants_table(project: Project, component: str) -> Optional[Table]:
    """AHT, or AVT and the rudder effectiveness -- once per section (AS-5)."""
    from ..modules.taildist import component_constants

    try:
        constants = component_constants(project, component)
    except (ValueError, TypeError, ZeroDivisionError):
        constants = None
    if constants is None or not constants.values:
        return None
    return Table(
        title="Aerodynamic constants of the surface",
        columns=["Quantity", "Value", "Units"],
        rows=[[v.label, format_value(v.value), v.units] for v in constants.values],
        note=("Reference constants, not loads: they carry no safety factor and "
              "nothing here is sized to them. Printed once because they are the "
              "same constants inside every condition above -- read from the "
              "owner the loads themselves were computed with, so the printed "
              "intermediate is arithmetically the one used."))


def _tail_chordwise_section(project: Project, component: str, *,
                            system: UnitSystem,
                            plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    """5.3 / 6.3 -- the chordwise pressure distribution."""
    names = _TAIL_SURFACES[component]
    results = _tail_chordwise(project, component)
    if not results:
        return Section("", absent_reason=(
            f"the {names['surface']} chordwise distributions were not produced "
            "for this project: no design condition carries the load split they "
            "are built from, or the surface's chordwise geometry is not entered."))
    tables = [t for t in (_tail_chord_stations_table(results, system),
                          _tail_pressure_table(results, system)) if t is not None]
    return Section("", body=[
        f"Each design condition's total load is spread along the "
        f"{names['surface']}'s chord as a net pressure. The distribution is the "
        f"sum of two shapes: an additive shape carrying the angle-of-attack "
        f"load, largest at the leading edge and zero at the trailing edge, and "
        f"a camber shape carrying the {names['control']} load, constant from "
        f"the hinge line aft. These replace the generalised profiles of the "
        f"regulation's own appendix with distributions computed for this "
        f"surface and this condition.",
        "The distribution conserves the total: integrating the pressure over "
        "the surface returns the condition's total load, so nothing in this "
        "subsection adds load to or removes load from the summary above.",
    ], tables=tables, figures=[_tail_chord_figure(results, component, system)])


# --- 5.4 / 6.4 -- the spanwise loads ---------------------------------------- #
#: The one sentence Section 5 carries about the limitation Section 6 owns
#: (OR-133): stated where the loads are withheld, pointed at from here.
_NON_CONVENTIONAL_POINTER = (
    "This analysis treats the empennage as a conventional tail, with the "
    "horizontal and the vertical surface each carried by the fuselage and each "
    "loaded independently. For any other arrangement the vertical tail also "
    "carries the horizontal tail, and the loads that creates are not modelled; "
    "the limitation is stated in full with the vertical tail's loads, and it "
    "does not affect anything in this section.")

#: What the reader is told a non-conventional layout is, in the report's words.
#:
#: Read off :class:`sloads.models.TailType` rather than spelled out per value:
#: a fifth arrangement added to the enum must not silently acquire the wording
#: of a fourth.
_LAYOUT_NAMES = {
    "t_tail": "a T-tail, with the horizontal tail mounted on top of the fin",
    "v_tail": "a V-tail, whose two surfaces are neither horizontal nor vertical",
    "cruciform": "a cruciform tail, with the horizontal tail mounted part-way "
                 "up the fin",
}


def _layout_phrase(project: Project) -> str:
    """"a T-tail, with ..." -- the arrangement this project declares."""
    from ..tail_geometry import tail_layout

    layout = tail_layout(project)
    value = getattr(layout, "value", "") if layout is not None else ""
    return _LAYOUT_NAMES.get(value, f"a {value.replace('_', ' ')} tail" if value
                             else "an arrangement other than a conventional tail")


def _vtail_withheld(project: Project, component: str) -> bool:
    """Whether OR-133 withholds this component's spanwise loads.

    The vertical tail only, and only on a non-conventional layout. The
    horizontal tail's loads are unaffected in every arrangement -- OR-133 says
    so in its own words, and G-OR-87 asserts it by diffing the two builds.
    """
    from ..tail_geometry import is_conventional_tail

    return component == "vtail" and not is_conventional_tail(project)


def _non_conventional_statement(project: Project) -> str:
    """The lead sentence 6.5 renders in place of the loads it withholds."""
    return (
        f"This analysis models the empennage as a conventional tail: a "
        f"horizontal and a vertical surface each carried by the fuselage and "
        f"each loaded independently. This airplane is entered as "
        f"{_layout_phrase(project)}, and in that arrangement the vertical tail "
        f"is additionally the supporting structure of the horizontal tail in "
        f"the sense of 14 CFR 23.427(a). That load path is not modelled, so the "
        f"vertical tail's spanwise loads are withheld rather than printed.")


#: The paragraphs 6.5 carries under the statement above: what is missing, what
#: is not affected, and what the withholding does *not* reach (OR-133).
_NON_CONVENTIONAL_BODY = (
    "Two load paths are unmodelled, and they fail differently. The horizontal "
    "tail's unsymmetrical condition of 23.427(a) is never reacted through the "
    "vertical tail, so the vertical tail's design conditions omit a case "
    "rather than understate one -- there is no row in this section that is too "
    "small; there is a row that is not there. Separately, the four conditions "
    "that are analysed transfer a symmetric horizontal-tail set onto the fin, "
    "in precisely the cases where sideslip and rudder deflection load the "
    "horizontal surface asymmetrically.",
    "The second of these is quantified: the induced rolling moment reaches 27 "
    "to 73 per cent of the governing vertical-tail case's own root bending on "
    "the configurations it has been measured on. A distribution carrying an "
    "error of that size is not a conservative distribution, and it is not "
    "published under a factor of safety as though it were.",
    "What is unaffected, stated positively rather than left to inference. The "
    "vertical tail's total loads and the conditions they were selected at, "
    "earlier in this section, are the surface's own and are unchanged -- what "
    "is missing there is the additional condition named above. The chordwise "
    "pressure distribution is unchanged: it distributes this surface's own "
    "total across its own chord and is indifferent to what the fin carries "
    "above it. The horizontal tail's loads and distributions are unchanged "
    "entirely. And the loads reference axis stated earlier in this section is "
    "geometry, which this restriction does not touch: it is where the loads "
    "would be applied, and it is stated so that what is withheld is legible "
    "as a withholding rather than as a gap in the data.",
)

#: The note OR-133a attaches to the condition register and the summary table on
#: a non-conventional layout: the set is short a case, and the case is named.
#:
#: Named rather than merely counted, because OR-133's own distinction is that
#: this is an omitted condition and not an understated one -- and because a
#: statement that names the missing case is one a reader can check and one a
#: later step can delete, where a hedge is neither.
_MISSING_CONDITION_NOTE = (
    " This airplane is not entered as a conventional tail, and on any other "
    "arrangement this set is short one condition: the horizontal tail's "
    "unsymmetrical load of 14 CFR 23.427(a), reacted through the vertical "
    "tail as the horizontal tail's supporting structure. It is not analysed "
    "and it is not tabulated below. The restriction is stated in full with "
    "this section's spanwise loads.")

#: A beam-frame torsion symbol follows its surface's **span** axis (OR-146).
#:
#: The wing and the horizontal tail span ``y``, so their torsion is ``Myy`` and
#: the letter happens to agree with the airplane axis. A fin spans ``z``. Until
#: 2026-09-07 section 6.5 printed ``Myy`` for the fin too -- 4,561 lb-in at
#: ``ga6_normal``'s fin root, under the name of a component whose body-axis
#: value is **identically zero**: a lateral load can make no moment about the
#: ``y`` axis at all. Section 3.2 maps the beam symbols onto body axes two
#: chapters earlier, so a reader carries that map into section 6, where it was
#: wrong by ninety degrees. The exported deck has called it ``mzz`` since it was
#: written (``coordinates.tail_torsion_to_airplane``).
_TAIL_TORSION_SYMBOL = {"htail": "Myy", "vtail": "Mzz"}
#: The airplane axis each surface's torsion is about, named beside the symbol so
#: the letter is never the only thing carrying the claim.
_TAIL_TORSION_AXIS_NAME = {"htail": "y", "vtail": "z"}


def _tail_span_symbols(component: str) -> Tuple[Tuple[str, str, str, str], ...]:
    """The spanwise notation of 5.5 / 6.5, in this surface's own frame."""
    torsion = _TAIL_TORSION_SYMBOL[component]
    axis = _TAIL_TORSION_AXIS_NAME[component]
    return (
        ("Fn", "Load applied at a station, normal to the surface",
         "force", "applied"),
        ("Sn", "Shear carried across a station, normal to the surface",
         "force", "cumulative"),
        ("Mxx", "Bending moment carried across a station, about the airplane "
         "x axis", "moment", "cumulative"),
        (torsion, "Torsion carried across a station, about the load reference "
         f"axis -- which runs along this surface's span, the airplane {axis} "
         "axis", "moment", "cumulative"),
    )


def _tail_span_notation_table(system: UnitSystem, component: str) -> Table:
    """5.5 / 6.5's symbol table: symbol, quantity, units, and its sense."""
    u = Units(system)
    torsion = _TAIL_TORSION_SYMBOL[component]
    return Table(
        title="Notation for the spanwise loads",
        columns=["Symbol", "Quantity", "Units", "Sense"],
        rows=[[symbol, text, u.ult_label(dim), sense]
              for symbol, text, dim, sense in _tail_span_symbols(component)],
        note=("An applied quantity is the load put on the surface at that "
              "station; a cumulative quantity is what the structure carries "
              "across it, accumulated from the tip. A column heading in this "
              "subsection or its appendix names a symbol from this table and "
              "nothing else. These are the beam's own quantities, not the "
              "body-axis vector the appendix tabulates: the torsion symbol "
              f"names the axis it is about, which is why it is {torsion} here "
              "and not the other surface's letter."))


def _tail_span_root_table(results: Sequence[TailSpanResult], component: str,
                          system: UnitSystem) -> Optional[Table]:
    """The root values and the control-surface loads, one row per condition."""
    from ..modules.tail_span import air_total, root_index

    if not results:
        return None
    names = _TAIL_SURFACES[component]
    u = Units(system)
    force, moment = u.ult_label("force"), u.ult_label("moment")
    torsion = _TAIL_TORSION_SYMBOL[component]
    columns = ["Case", f"Root Sn ({force})", f"Root Mxx ({moment})",
               f"Root {torsion} ({moment})", f"Applied air load ({force})", "SF"]
    rows = []
    for result in results:
        sf = float(getattr(result, "safety_factor", ULTIMATE_FACTOR) or ULTIMATE_FACTOR)
        stations = list(getattr(result, "stations", ()))
        if not stations:
            continue
        root = stations[root_index(result)]
        rows.append([
            _tail_case_id(result),
            u.load(root.sz, "force", sf), u.load(root.mxx, "moment", sf),
            u.load(root.myy, "moment", sf),
            u.load(air_total(result), "force", sf),
            format_value(sf)])
    if not rows:
        return None
    return Table(
        title=f"{names['surface'].capitalize()} spanwise loads at the root (LIMIT)",
        columns=columns, rows=rows,
        note=("The shear, bending and torsion the structure carries at its root "
              "attachment, which is where each of them is greatest, with the "
              "applied air load they accumulate from. Torsion is about the "
              "loads reference axis, not the quarter chord, and that axis runs "
              f"along this surface's span -- the airplane "
              f"{_TAIL_TORSION_AXIS_NAME[component]} axis, which is why it is "
              f"{torsion}."))


def _control_load_mode_sentence(project: Project, component: str) -> str:
    """How the control surface's load is carried, and what the other mode needs.

    Stated because its absence is otherwise invisible: a reader who expects a
    hinge moment and finds none cannot tell whether the analysis computed zero,
    could not compute one, or chose a model in which there is none to compute.
    """
    from ..modules.tail_span import control_load_mode

    names = _TAIL_SURFACES[component]
    try:
        mode = control_load_mode(project, component)
    except (ValueError, TypeError):
        mode = ""
    if mode == "discrete":
        return (
            f"The {names['control']}'s load is reacted at its hinges and its "
            f"actuator, so this analysis states the load the {names['control']} "
            f"carries, the moment about its hinge line, and the arm that moment "
            f"acts on.")
    return (
        f"The {names['control']}'s load is carried into the "
        f"{names['surface']} rather than reacted at discrete hinges, so no "
        f"hinge moment is stated. That is a modelling choice and not a missing "
        f"calculation: the hinge line itself is known -- it is the chordwise "
        f"station the pressure distribution above is built on -- but a hinge "
        f"moment needs the hinges' and the actuator's positions along the span, "
        f"and this project states neither. Entering at least two hinge span "
        f"stations and the actuator span station selects the discrete load "
        f"path, in which the {names['control']} load is concentrated where the "
        f"structure actually takes it and the hinge moment and its arm are "
        f"reported with it.")


def _tail_span_section(project: Project, component: str, *,
                       system: UnitSystem,
                       plan: Sequence[SectionPlan]) -> Section:  # noqa: ARG001
    """5.4 / 6.4 -- the spanwise loads, with the station table in the appendix."""
    names = _TAIL_SURFACES[component]
    appendix = (HTAIL_LOAD_STATIONS if component == "htail"
                else VTAIL_LOAD_STATIONS)
    # OR-133, ahead of the results test: the withholding is a statement about
    # the airplane's arrangement and must not depend on whether the builder
    # happened to produce anything. It does -- `build_tail_span` is untouched,
    # which is what keeps the balanced deck's lateral cases assembling -- and a
    # reader must not be told "not produced" about loads that were.
    if _vtail_withheld(project, component):
        return Section("", body=list(_NON_CONVENTIONAL_BODY),
                       absent_reason=_non_conventional_statement(project),
                       absent_lead="Not supported")
    results = _tail_spanwise(project, component)
    if not results:
        return Section("", absent_reason=(
            f"the {names['surface']} spanwise loads were not produced for this "
            "project: the surface has no entered planform, or no design "
            "condition carries the load split they are distributed from."))
    table = _tail_span_root_table(results, component, system)
    body = [
        f"Each design condition's total load is distributed along the "
        f"{names['surface']}'s span in proportion to the local chord, and the "
        f"surface's own weight is applied against it at the condition's load "
        f"factor. The result is the load set a beam model of the "
        f"{names['surface']} is built from: what is applied at each station, "
        f"and what the structure carries across it.",
        f"This distribution has no counterpart in the original analysis, which "
        f"gives the {names['surface']}'s totals and its chordwise profile and "
        f"stops. It is therefore held to stated closures rather than to a "
        f"published example: the distributed air load sums to the condition's "
        f"own total, and the applied set reproduces the carried set at every "
        f"station. The per-station numbers are in "
        f"{appendix_ref(appendix)}; the values below are the root, where each "
        f"carried quantity is greatest.",
        _control_load_mode_sentence(project, component),
    ]
    tables = [_tail_span_notation_table(system, component)]
    if table is not None:
        tables.append(table)
    return Section("", body=body, tables=tables)


# --- the sections ----------------------------------------------------------- #
def _tail_section(project: Project, component: str, *, system: UnitSystem,
                  plan: Sequence[SectionPlan]) -> Section:
    """Sections 5 and 6 -- one surface's loads, in five subsections (OR-130).

    One builder for both surfaces rather than two that must be kept in step:
    the partition of OR-129 is a parameter here, not a pair of copies, which is
    what makes the two sections provably the same analysis read twice. OR-130
    agreed four subsections; the input-data subsection was added to both by the
    owner's review of 2026-09-07 and the mirror is what carried it into Section
    6 for free -- which is the argument for one builder, demonstrated.
    """
    names = _TAIL_SURFACES[component]
    return Section("", body=[
        f"This section states the {names['surface']}'s loads: the surface they "
        f"were run on, the design "
        f"conditions and how they were selected, the critical loads themselves, "
        f"their distribution along the chord, and their distribution along the "
        f"span. Every load delivered here is LIMIT, states the safety factor 14 "
        f"CFR 23.303 prescribes for its condition, and has been multiplied by "
        f"nothing.",
    ], subsections=[
        replace(_tail_inputs(project, component, system=system, plan=plan),
                title=f"{names['surface'].capitalize()} input data"),
        replace(_tail_conditions_section(project, component, system=system, plan=plan),
                title="Design conditions"),
        replace(_tail_summary(project, component, system=system, plan=plan),
                title=f"Critical {names['surface']} loads"),
        replace(_tail_chordwise_section(project, component, system=system, plan=plan),
                title="Chordwise load distribution"),
        replace(_tail_span_section(project, component, system=system, plan=plan),
                title="Spanwise loads"),
    ])


def _htail_loads(project: Project,
                 results: Mapping[str, Optional[ModuleResult]], *,  # noqa: ARG001
                 system: UnitSystem, plan: Sequence[SectionPlan]) -> Section:
    """Section 5 -- Horizontal Tail and Elevator Loads."""
    return _tail_section(project, "htail", system=system, plan=plan)


def _vtail_loads(project: Project,
                 results: Mapping[str, Optional[ModuleResult]], *,  # noqa: ARG001
                 system: UnitSystem, plan: Sequence[SectionPlan]) -> Section:
    """Section 6 -- Vertical Tail and Rudder Loads."""
    return _tail_section(project, "vtail", system=system, plan=plan)


# --------------------------------------------------------------------------- #
# Appendix D -- horizontal tail loads by station (OR-130a / OR-136)
# --------------------------------------------------------------------------- #
#: Index of the spanwise subsection within a tail section, for cross-references.
#: Composed rather than typed as "5.5": a literal is a reference that does not
#: move when a subsection is inserted above it (OR-2, F-R2).
_TAIL_SPAN_SUBSECTION = 4


def _tail_section_key(component: str) -> str:
    """The plan key of the section a component's loads are printed in."""
    return f"{component}_loads"


def _tail_station_appendix(project: Project, component: str, *,
                           system: UnitSystem,
                           plan: Sequence[SectionPlan]) -> Section:
    """Every tail case's **applied** load at every station, in airplane axes.

    An applied-load deck and nothing else (owner, 2026-09-07). Appendix B splits
    applied from carried because the wing section is where a reader checks a
    beam model's own answer; the empennage appendix is a deck to load a model
    *with*, so the carried set would be a second thing to keep in step for a
    question this appendix is not asked. What the structure carries is stated at
    the root in the section itself.

    The point is in **airplane axes**, not the surface's own: ``X``, ``Y`` and
    ``Z`` are where the load acts on the airplane, taken from the same mapper
    the exported deck uses (``export.coordinates.tail_station_to_airplane``), so
    a row here and a card in the deck place the same load at the same point.
    """

    names = _TAIL_SURFACES[component]
    if _vtail_withheld(project, component):
        # An appendix is a second projection of its section, so it inherits the
        # section's state rather than deciding one (OR-136). Two appendices
        # rather than one exist for exactly this: a shared tail appendix could
        # only express this by going half empty.
        return Section("", body=[
            "The station-by-station loads this appendix would carry are the "
            "ones withheld with this surface's spanwise loads. The reason is "
            "stated in full there and is not repeated here."],
            absent_reason=_non_conventional_statement(project),
            absent_lead="Not supported", page_break=True)
    results = _tail_spanwise(project, component)
    if not results:
        return Section("", absent_reason=(
            f"the {names['surface']} spanwise loads were not produced for this "
            "project, so there are no stations to list."), page_break=True)
    from ..export.sbeam_bridge import applied_loads

    torsion = "My" if component == "htail" else "Mz"
    normal = "Fz" if component == "htail" else "Fy"
    # Every zero column is named with the producer it lacks, and every non-zero
    # one with the producer it has. The fin's list is not the h-tail's: a fin
    # spans vertically, so vertical acceleration on its own mass is an axial
    # column load and ``Fz`` is **not** zero -- which is what this appendix
    # asserted, of a component the deck has been emitting all along (OR-143).
    if component == "htail":
        absent = (f"Fz is the normal load and {torsion} the strip torsion about "
                  "the surface's span axis, which for a horizontal tail is "
                  "airplane y. Fx and Fy are zero for every row: this analysis "
                  "models no chordwise load on either tail surface, and no "
                  "spanwise acceleration reaches a horizontal tail. Mx and Mz "
                  "are zero because a strip applies forces and a torsion and "
                  "nothing else -- the bending the structure carries is those "
                  "forces acting through the arms these coordinates state.")
    else:
        absent = (f"{normal} is the normal load and {torsion} the strip torsion "
                  "about the surface's span axis, which for a fin is airplane "
                  "z. My is zero for every row, and cannot be otherwise: a "
                  "lateral load makes no moment about the y axis. Fz is not "
                  "zero -- a fin's span is vertical, so vertical acceleration "
                  "on its own mass is an axial column load, carried on the same "
                  "card as the side load. Fx and Mx are zero: this analysis "
                  "models no chordwise load on either tail surface, and the "
                  "bending the structure carries is the normal load acting "
                  "through the arms these coordinates state.")
    table = applied_load_table(
        applied_loads(component, results), system=system,
        title=f"Applied {names['surface']} loads by station (LIMIT)",
        note=("Every load is LIMIT and states the factor 14 CFR 23.303 "
              "prescribes for its condition, which is applied to none of them. "
              "The station point is the loads reference axis of the surface, "
              "mapped to airplane axes, and the moments are right-handed about "
              f"those axes about that point. {absent}"))
    if table is None:
        return Section("", absent_reason=(
            f"the {names['surface']} spanwise loads produced no applied "
            "stations for this project, so there is nothing to tabulate."),
            page_break=True)
    return Section("", body=[
        f"Every {names['surface']} design condition's applied load, at every "
        f"station of its beam. This is the load set a structural model is "
        f"given: one row per load, at the point stated beside it, in airplane "
        f"axes. The grid identifiers are the ones the exported deck uses, so a "
        f"row here and the card that carries it are the same load -- every "
        f"card, not the normal force alone: the strip torsion is a MOMENT card "
        f"at the same grid, and its column is beside the forces here.",
        "The rows are the surface's strips, in span order, followed by any "
        "discrete control-surface node and, on a T-tail, the transfer node "
        "where the horizontal tail sits on the fin. All six components are "
        "printed for every row, so that a zero cannot be read as an omission. "
        + absent.split(". ", 1)[0] + ".",
        "What the structure carries across each station -- shear, bending and "
        "torsion -- is not repeated here. It is stated at the root, where each "
        "is greatest, in " + subsection_ref(plan, _tail_section_key(component),
                                             _TAIL_SPAN_SUBSECTION) + ".",
    ], tables=[table], page_break=True, landscape=True)


def _htail_station_appendix(project: Project, *, system: UnitSystem,
                            plan: Sequence[SectionPlan]) -> Section:
    """Appendix D's content."""
    return _tail_station_appendix(project, "htail", system=system, plan=plan)


def _vtail_station_appendix(project: Project, *, system: UnitSystem,
                            plan: Sequence[SectionPlan]) -> Section:
    """Appendix E's content."""
    return _tail_station_appendix(project, "vtail", system=system, plan=plan)


# =========================================================================== #
# Sections 7, 8 and 9 -- the control-surface pressures (note 44 §19)
# =========================================================================== #
#: The host each control surface is cut into, the frame it is drawn in, and the
#: airplane axis its outward normal is (OR-149, OR-150).
#:
#: The normal is the axis a reader applies the pressure in, and it is a property
#: of the *host*, not of the control surface: an aileron and a flap hang off a
#: wing and push in airplane z, a rudder hangs off a fin and pushes in airplane
#: y. Declared as data for the reason ``_PLANFORM_FIGURES`` is: a surface added
#: to the schema without a normal fails the suite rather than inheriting one.
_CONTROL_HOSTS: Dict[str, Tuple[str, str, str]] = {
    #  control surface -> (host surface, planform frame, airplane normal axis)
    "aileron": ("wing", "butt", "z"),
    "flap": ("wing", "butt", "z"),
    "elevator": ("htail", "butt", "z"),
    "rudder": ("vtail", "water", "y"),
}

#: Which control surface a tab is cut into, per host surface (OR-149).
#:
#: A tab is not cut into the fixed surface. ``TabSpec.surface`` names the wing,
#: the horizontal tail or the fin, and the tab sits in that surface's *control*
#: surface -- so the locator is drawn on the aileron, the elevator or the
#: rudder, which are the outlines §2.1 already carries as regions.
_TAB_HOSTS = {"wing": "aileron", "htail": "elevator", "vtail": "rudder"}

#: The station name a tab's ``station_in`` is, per host (OR-157).
_TAB_STATION_NAMES = {"wing": "Butt line", "htail": "Butt line",
                      "vtail": "Waterline"}

#: How far the entered analysis area and the entered outline may differ before
#: the section says so (OR-152). Measured on the shipped examples: +0.2 % on
#: ``ga6_normal``, +4.0 % on ``baron_58``, -4.5 % on ``cessna_210`` and **+77 %**
#: on ``concept_regional_jet``. The owner set the threshold where the middle two
#: speak as well as the outlier, because a 4 % disagreement between the area a
#: pressure was computed from and the area it is drawn over is worth a sentence.
_AREA_TOLERANCE = 0.02


def _control_sign_convention(surface: str, host: str, *,
                             label: str = "") -> str:
    """The one sign-convention paragraph all three sections carry (OR-150).

    Stated in the same words in each, and in the same words §5.3 and §6.3 state
    the elevator's and the rudder's -- three sections that each phrased one
    convention their own way would read as three conventions.
    """
    axis = _CONTROL_HOSTS.get(surface, (host, "butt", "z"))[2]
    # ``label`` names the surface the pressure is *on* where that is not the
    # surface the axis is read from -- a tab, whose own plane is the one it is
    # applied normal to and whose host chain ends at the airplane axis two
    # surfaces up. Without it §9 stated the convention about the elevator, and
    # a reader would have had to decide for themselves which hinge line "the
    # hinge line" was.
    printed = (label or _REGION_NAMES.get(surface, surface)).lower()
    carrier = _REGION_NAMES.get(surface, surface).lower()
    host_printed = _REGION_NAMES.get(host, host).lower()
    if label:
        host_printed = f"{carrier}, which the {host_printed} carries"
    return (
        f"Pressure is positive acting normal to the {printed}'s own plane, in "
        f"the sense a trailing-edge-down deflection produces. A positive "
        f"pressure gives a nose-down moment about the hinge line -- the "
        f"{printed}'s own, leading edge down, trailing edge up -- and a "
        f"negative pressure, which is what a trailing-edge-up throw produces, "
        f"gives a trailing-edge-down moment about it. The {printed} is carried "
        f"by the {host_printed}, so that normal is the airplane {axis} axis.")


#: How the pressure varies along the span, and why that is not an assumption
#: added by this document (OR-151).
_SPANWISE_RULE = (
    "The pressure is uniform along the span of the surface, and the chordwise "
    "profile is stated in fractions of the local surface chord. That is what "
    "the analysis does rather than a rule added here: the load is divided by an "
    "area to obtain the pressure, so the pressure is uniform over that area by "
    "construction. It follows that the load per unit span is proportional to "
    "the local chord -- a tapered surface carries more load per inch of span at "
    "its wide end at the same pressure -- and that the total is recovered by "
    "integrating the pressure over the surface's area, not by multiplying it by "
    "a mean chord.")

#: The hinge-moment absence, stated where a reader meets it (OR-154).
_HINGE_MOMENT_ABSENCE = (
    "No hinge moment is stated. The analysis produces the surface's load and "
    "its pressure distribution and does not produce a hinge moment, and this "
    "document reports what the analysis produced rather than deriving a "
    "quantity beside it. Nor is that a gap in this analysis against the method "
    "it follows: the method sizes control surfaces for their air load and does "
    "not limit any of them by pilot effort, which is the one place a hinge "
    "moment enters the regulation it is drawn from (CAM 3.224-1(a), as a cap on "
    "tab deflection). The sense of the moment is the sign convention above; "
    "the magnitude is the reader's to take from the pressure and their own "
    "hinge geometry. One thing goes with it, because it is met immediately: the "
    "area forward of the hinge line carries the same-signed pressure and "
    "contributes the opposite moment about the hinge, which is what that area "
    "is for.")


def _control_records(project: Project, kind: str) -> List[ControlSurfaceLoadResult]:
    """One module's control-surface records, or ``[]`` where it cannot run.

    Read from the module's own builder -- the same records the export channel
    consumes -- rather than reconstructed from the rendered condition, which is
    OR-95's ruling: a section projects the published result and reads the
    builder only for what the result does not carry. Here that is the chordwise
    profile, which is on the record and not on the ``ConditionResult``.
    """
    from ..modules.aileron import build_aileron
    from ..modules.flap import build_flap
    from ..modules.tab import build_tabs

    builders = {"aileron": build_aileron, "flap": build_flap, "tab": build_tabs}
    try:
        return list(builders[kind](project))
    except (MissingInputError, ValueError, TypeError, ZeroDivisionError,
            AttributeError, IndexError):
        # G-OR-7: a half-filled project still builds a complete document. The
        # section states the absence; it does not raise through the builder.
        return []


def _profile_centroid(stations: Sequence[ControlSurfaceStation]) -> Optional[float]:
    """Chordwise centroid of a pressure profile, as a fraction of chord.

    Where the resultant of the printed profile acts -- the one thing a reader
    applying it as a single force needs and the profile does not say. It is a
    property of the drawn shape, not a load: the same number for both throws of
    an aileron, whose profiles differ only in sign.
    """
    points = sorted(stations, key=lambda s: s.x)
    if len(points) < 2:
        return None
    areas, moments = [], []
    for first, second in zip(points, points[1:]):
        dx = second.x - first.x
        if dx <= 0:
            continue
        delta = second.psi - first.psi
        areas.append(dx * (first.psi + delta / 2.0))
        moments.append(dx * (first.x * first.psi
                             + (first.x * delta + dx * first.psi) / 2.0
                             + dx * delta / 3.0))
    total = math.fsum(areas)
    if not areas or abs(total) < 1e-12:
        return None
    return math.fsum(moments) / total


def _control_chord_figure(records: Sequence[ControlSurfaceLoadResult], *,
                          key: str, title: str, surface: str, host: str,
                          system: UnitSystem,
                          hinge: Optional[float] = None,
                          label: str = "") -> Figure:
    """The chordwise application diagram: how the pressure is applied (OR-153).

    Built from the module's own station profile and nothing else, so it is
    available on every project that runs the module -- unlike the locator
    beside it, which needs an outline the project may not enter.
    """
    # ``label`` for the same reason the sign convention takes one: a tab's
    # profile is over the tab's chord, not over the chord of the control
    # surface it is cut into, and the caption must not say otherwise.
    printed = (label or _REGION_NAMES.get(surface, surface)).lower()
    if not records:
        return Figure(key=key, title=title, absent_reason=(
            f"the {printed} loads were not produced for this project."))
    p_scale, p_units = _scalar_channel("lb/in^2", system)
    series = []
    for record, style in zip(records, _CASE_STYLES * 4):
        stations = sorted(record.stations, key=lambda s: s.x)
        if not stations:
            continue
        series.append(Series(str(record.case),
                             [s.x for s in stations],
                             [s.psi * p_scale for s in stations], style))
    if not series:
        return Figure(key=key, title=title, absent_reason=(
            f"the {printed} loads carry no chord stations to plot."))
    vlines = []
    if hinge is not None:
        vlines.append(("Hinge line", hinge))
    centroid = _profile_centroid(records[0].stations)
    if centroid is not None:
        vlines.append(("Resultant acts here", centroid))
    axis = _CONTROL_HOSTS.get(surface, (host, "butt", "z"))[2]
    caption = [
        f"How to apply the {printed} pressure. The horizontal axis is the "
        f"fraction of the {printed}'s local chord, 0 at its leading edge and 1 "
        f"at its trailing edge, so the profile is applied at every station of "
        f"the span at the same pressures. A positive pressure acts normal to "
        f"the surface in the airplane {axis} direction.",
        "The resultant of the profile acts at the marked chord fraction; the "
        "profile itself is the load, and the resultant is where a reader "
        "replacing it by a single force would put that force.",
        "All values are LIMIT and state the factor their condition does not "
        "apply.",
    ]
    return Figure(
        key=key, title=title,
        data=PlotData("Fraction of the surface chord (0 = LE, 1 = TE)",
                      f"Pressure ({p_units})", series, vlines=vlines),
        caption=" ".join(caption))


def _outline_series(project: Project, name: str, style: str, mirror: bool,
                    frame: str, scale: float) -> List[Series]:
    """One surface's outline, or ``[]`` where it is not entered or half entered."""
    try:
        return _region_series(project, name, style,
                              _REGION_NAMES.get(name, name), mirror, frame,
                              scale)
    except ValueError:
        return []


def _control_locator_figure(project: Project, *, key: str, title: str,
                            surface: str, host: str, system: UnitSystem,
                            extra: Sequence[Series] = (),
                            extra_note: str = "", label: str = "") -> Figure:
    """Where the pressure acts: §2's entered outline, with the surface on it.

    The outline is Section 2's, read through the same owner 2.1 draws it with
    (OR-148), so the two figures cannot disagree about the shape. Where the
    outline is not entered the figure states the absence rather than drawing
    a shape nobody entered -- measured, that is the flap on three of the four
    examples and the elevator on three.
    """
    from .planform_tex import OUTLINE_STYLE, REGION_STYLES

    printed = _REGION_NAMES.get(surface, surface).lower()
    host_printed = _REGION_NAMES.get(host, host).lower()
    frame = _CONTROL_HOSTS.get(surface, (host, "butt", "z"))[1]
    host_surface = project.geometry.by_name(host) if project.geometry else None
    if host_surface is None:
        return Figure(key=key, title=title, absent_reason=(
            f"the project enters no {host_printed} planform, so there is "
            f"nothing to locate the {printed} on."))
    scale, length_units = _length_channel(system)
    mirror = bool(host_surface.symmetric) and frame == "butt"
    series = _outline_series(project, host, OUTLINE_STYLE, mirror, frame, scale)
    if not series:
        return Figure(key=key, title=title, absent_reason=(
            f"the {host_printed} planform cannot be drawn as entered, so there "
            f"is nothing to locate the {printed} on."))
    region = _outline_series(project, surface, REGION_STYLES[0], mirror, frame,
                             scale)
    if not region and not extra:
        return Figure(key=key, title=title, absent_reason=(
            f"the project enters no {printed} leading- and trailing-edge "
            f"polylines, so its outline cannot be drawn. The loads and the "
            f"pressures above are unaffected: they are computed from the "
            f"entered areas, not from a drawn shape."))
    series += list(region) + list(extra)
    x_label, y_label = _PLANFORM_AXES[frame]
    if label:
        opening = (f"Where the {label} pressure acts: the {label} drawn on the "
                   f"{printed}, which is itself shaded on the {host_printed}, "
                   f"all to scale on equal axes.")
        applied = (f"The pressure of the profile beside this figure is applied "
                   f"over the {label}, uniformly along its span.")
    else:
        opening = (f"Where the pressure acts: the {printed} shaded on the "
                   f"{host_printed} as both are entered, drawn to scale on "
                   f"equal axes.")
        applied = ("The pressure of the profile beside this figure is applied "
                   "over the shaded region, uniformly along its span.")
    caption = [
        opening + " The outlines are Section 2's own and are drawn from the "
        "same entered polylines.",
        applied,
    ]
    if extra_note:
        caption.append(extra_note)
    caption.append("Nothing here is a load: no value is scaled and none carries "
                   "a safety factor.")
    return Figure(
        key=key, title=title,
        data=PlotData(f"{x_label} ({length_units})",
                      f"{y_label} ({length_units})", series),
        caption=" ".join(caption))


def _area_discrepancy(project: Project, surface: str, entered_sqft: float,
                      system: UnitSystem) -> str:
    """OR-152: the sentence a disagreeing pair of entered areas earns.

    Two *entered* numbers are compared -- the area the analysis was run on and
    the area the drawn outline encloses -- and neither is derived into a load.
    That distinction is the whole of why this is allowed where §2.1 refuses to
    label a region with a summed area: a legend entry reads as a tabulated
    quantity, and this reads as what it is, a disagreement between two inputs.
    """
    from ..derived_geometry import planform_area_sqft

    if entered_sqft <= 0:
        return ""
    try:
        drawn = planform_area_sqft(project, surface)
    except (ValueError, TypeError, ZeroDivisionError):
        drawn = None
    if drawn is None or drawn <= 0:
        return ""
    if abs(drawn - entered_sqft) <= _AREA_TOLERANCE * entered_sqft:
        return ""
    scale, units = _scalar_channel("ft^2", system)
    printed = _REGION_NAMES.get(surface, surface).lower()
    difference = (drawn - entered_sqft) / entered_sqft * 100.0
    sense = "larger" if difference > 0 else "smaller"
    return (
        f"The two entered areas of this {printed} disagree: the analysis was "
        f"run on {format_value(entered_sqft * scale)} {units} and the entered "
        f"outline encloses {format_value(drawn * scale)} {units}, "
        f"{abs(difference):.0f} % {sense} than the area the pressure was "
        f"computed from. The "
        f"pressures above are the analysis's own and were computed from the "
        f"first of those; the figure below draws the second. Which is the "
        f"airplane is a question for the configuration, not for this document, "
        f"and it is stated here rather than resolved silently in either "
        f"direction.")


def _control_case_table(records: Sequence[ControlSurfaceLoadResult],
                        system: UnitSystem, *, title: str,
                        note: str) -> Optional[Table]:
    """Case, speed, load and the whole profile -- one row per case.

    Every station of the profile gets a column, headed by the chord fraction it
    sits at, rather than the leading-edge pressure alone: the figure beside it
    draws the shape and this states its numbers, and a reader applying the load
    needs both ends of a taper. It is also what stops a printed profile being
    half a profile -- the aileron's zero at the trailing edge is a value of the
    distribution, not an omission from it.
    """
    if not records:
        return None
    u = Units(system)
    p_scale, p_units = _scalar_channel("lb/in^2", system)
    stations = sorted({round(s.x, 6) for r in records for s in r.stations})
    rows = []
    for record in records:
        sf = float(record.safety_factor or ULTIMATE_FACTOR)
        by_x = {round(s.x, 6): s.psi for s in record.stations}
        rows.append([
            str(record.case),
            _tail_case_id(record) if record.case_ref else "--",
            format_value(record.v_kt),
            u.load(record.load_lb, "force", sf),
        ] + [_scalar_cell(by_x.get(x), p_scale) for x in stations] + [
            format_value(sf)])
    return Table(
        title=title,
        columns=["Condition", "Case ID", "Speed (KEAS)",
                 f"Load ({u.ult_label('force')})"]
                + [f"psi at {x:.2f}c ({p_units})" for x in stations]
                + ["SF"],
        rows=rows, note=note)





# --- Section 7 -- the aileron ------------------------------------------------ #
def _aileron_loads(project: Project,
                   results: Mapping[str, Optional[ModuleResult]], *,  # noqa: ARG001
                   system: UnitSystem,
                   plan: Sequence[SectionPlan]) -> Section:
    """Section 7 -- the aileron's critical loads and the pressure to apply."""
    records = _control_records(project, "aileron")
    inputs = project.aileron_loads
    if not records or inputs is None:
        return Section("", absent_reason=(
            "the aileron loads were not produced for this project: the aileron "
            "geometry or the design speeds they are computed at are not "
            "entered."))
    geometry_ref = section_ref(plan, "configuration_layout")
    hinge = next((s.x for s in sorted(records[0].stations, key=lambda s: s.x)
                  if s.x not in (0.0, 1.0)), None)
    entered_area = float(inputs.area_fwd_hinge_sqft or 0.0) + float(
        inputs.area_aft_hinge_sqft or 0.0)
    table = _control_case_table(
        records, system, title="Critical aileron loads (LIMIT)",
        note=("The largest down load and the largest up load, each at the speed "
              "it occurs at. Both are LIMIT and state the factor 14 CFR 23.303 "
              "prescribes for the condition, which is applied to neither. The "
              "pressure columns are the profile itself, at fractions of the "
              "aileron's local chord: constant from its leading edge to the "
              "hinge line, then tapering to zero at its trailing edge."))
    body = [
        f"The ailerons are sized for the deflected rolling conditions of 14 CFR "
        f"23.455(a)(2); the symmetrical undeflected case is never critical. The "
        f"load is the CAM 3.222(c) simplified coefficient over the aileron "
        f"area, evaluated at the three rolling-condition speeds -- full "
        f"deflection at VA, (VA/VC) of it at VC per 23.455(a)(2)(ii), and half "
        f"of (VA/VD) of it at VD -- for the up and "
        f"the down throw, with the largest of each governing. The aileron's "
        f"geometry, its deflection limits and its areas forward and aft of the "
        f"hinge line are stated in {geometry_ref} and are not repeated "
        f"here.",
        _control_sign_convention("aileron", "wing"),
        "Both throws are printed and they carry opposite signs: the down "
        "throw's positive pressure gives a nose-down moment about the hinge "
        "line, and the up throw's negative pressure gives a trailing-edge-down "
        "moment about it. They are one rule read from the two throws.",
        _SPANWISE_RULE,
        "The chord fraction the profile breaks at is the aileron's area "
        "forward of the hinge line as a fraction of its total area. That is a "
        "chord fraction only where the ratio of hinge-forward chord to total "
        "chord is constant along the span; where it is not, it is the span "
        "mean of it.",
    ]
    discrepancy = _area_discrepancy(project, "aileron", entered_area, system)
    if discrepancy:
        body.append(discrepancy)
    body.append(_HINGE_MOMENT_ABSENCE)
    figures = [
        _control_chord_figure(records, key="chordwise_aileron",
                              title="Aileron chordwise pressure (LIMIT)",
                              surface="aileron", host="wing", system=system,
                              hinge=hinge),
        _control_locator_figure(project, key="locator_aileron",
                                title="The aileron on the wing",
                                surface="aileron", host="wing", system=system),
    ]
    return Section("", body=body,
                   tables=[t for t in (table,) if t is not None],
                   figures=figures)


# --- Section 8 -- the flap --------------------------------------------------- #
#: The four flaps-extended conditions the critical flap load is chosen from,
#: as ``(load key, lift-coefficient key, printed name)`` (OR-156).
#:
#: Every one is a value ``flap.run`` already publishes, so the table is a
#: projection of the published result and derives nothing: a pick printed
#: without the set it was picked from is a number a reader cannot check.
_FLAP_CANDIDATES = (
    ("flap_load_1g_stall", "flap_cl_1g_stall", "1G stall"),
    ("flap_load_2g_stall", "flap_cl_2g_stall", "2G stall"),
    ("flap_load_2g_at_vf", "flap_cl_2g_at_vf", "2G at VF"),
    ("flap_load_gust_at_vf", "flap_cl_gust_at_vf", "Gust at VF"),
)


def _flap_candidate_table(condition: Optional[ConditionResult],
                          system: UnitSystem) -> Optional[Table]:
    """The four conditions and the pick, as ``flap.run`` published them."""
    values = _by_key(condition)
    if not values:
        return None
    u = Units(system)
    sf = float(getattr(condition, "safety_factor", ULTIMATE_FACTOR)
               or ULTIMATE_FACTOR)
    loads = [values.get(load_key) for load_key, _cl, _name in _FLAP_CANDIDATES]
    governing = max(
        (v.value for v in loads if v is not None), default=None)
    rows = []
    for (_load_key, cl_key, name), load in zip(_FLAP_CANDIDATES, loads):
        if load is None:
            continue
        cl = values.get(cl_key)
        critical = (governing is not None
                    and math.isclose(load.value, governing, rel_tol=1e-9))
        rows.append([name,
                     format_value(cl.value) if cl is not None else "--",
                     u.load(load.value, "force", sf),
                     format_value(sf),
                     "critical" if critical else ""])
    if not rows:
        return None
    return Table(
        title="Flaps-extended conditions (LIMIT)",
        columns=["Condition", "Flap CL", f"Load ({u.ult_label('force')})",
                 "SF", ""],
        rows=rows,
        note=("The four conditions of 14 CFR 23.345(a) the critical flap load "
              "is the largest of, printed with the pick so that the pick can be "
              "read against what it was chosen from. Every load is LIMIT and "
              "states the factor its condition does not apply."))


def _flap_slipstream_table(result: Optional[ModuleResult],
                           system: UnitSystem) -> Optional[Table]:
    """The 23.457(b) slipstream condition, where the airplane has one.

    Built through :class:`~sloads.report.content.Units` rather than through
    :func:`_value_table`, which is section 2's shape and marks a load it meets
    ``-ULT`` by design -- it is the input echo's table and no load is meant to
    reach it. This one carries a load, so it states the factor in an ``SF``
    column and marks nothing (note 49 OR-116).
    """
    condition = _find(getattr(result, "conditions", ()) or (), "Flap loads in")
    if condition is None:
        return None
    u = Units(system)
    sf = float(getattr(condition, "safety_factor", ULTIMATE_FACTOR)
               or ULTIMATE_FACTOR)
    rows = []
    for value in convert_results([condition], system)[0].values:
        is_load = value.units.startswith("lb") or value.units.startswith("N")
        rows.append([value.label,
                     u.load(value.value, "force", sf) if is_load
                     else format_value(value.value),
                     (u.ult_label("force") if is_load else value.units),
                     format_value(sf) if is_load else ""])
    return Table(
        title="Flap loads in the propeller slipstream (LIMIT)",
        columns=["Quantity", "Value", "Units", "SF"], rows=rows,
        note=("The 14 CFR 23.457(b) slipstream condition. The load inside the "
              "slipstream is the flap load raised by the stated factor, over "
              "the span between the two butt lines given. Loads are LIMIT and "
              "state the factor the condition does not apply; the factor and "
              "the velocity are not loads and carry none."))


def _flap_loads(project: Project,
                results: Mapping[str, Optional[ModuleResult]], *,
                system: UnitSystem,
                plan: Sequence[SectionPlan]) -> Section:
    """Section 8 -- the critical flap load and the pressure to apply."""
    from ..modules.flap import slipstream_is_available

    records = _control_records(project, "flap")
    inputs = project.flap_loads
    result = results.get("flap_loads")
    if not records or inputs is None:
        return Section("", absent_reason=(
            "the flap loads were not produced for this project: the flap "
            "geometry, the design speeds or the flaps-extended lift "
            "coefficients they are computed from are not entered."))
    geometry_ref = section_ref(plan, "configuration_layout")
    conditions = list(getattr(result, "conditions", ()) or ())
    critical = conditions[0] if conditions else None
    entered_area = float(inputs.flap_area_one_side_sqft or 0.0)
    tables = [t for t in (_flap_candidate_table(critical, system),
                          _control_case_table(
                              records, system,
                              title="Critical flap loads (LIMIT)",
                              note=("The load applied to the flap on one side "
                                    "of the airplane, and the profile it is "
                                    "applied as, at fractions of the flap's "
                                    "local chord: the trailing-edge pressure "
                                    "is half the leading-edge pressure. Every "
                                    "load is LIMIT and states the factor its "
                                    "condition does not apply.")),
                          _flap_slipstream_table(result, system))
              if t is not None]
    body = [
        f"The flap is sized for the flaps-extended conditions of 14 CFR "
        f"23.345: the critical load is the largest of a 1G stall, a 2G stall, "
        f"2G at the design flap speed VF and the flaps-extended gust at VF, "
        f"with the flap's section lift built from the wing angle of attack and "
        f"the flap deflection. The flap's area, deflection and chord ratio are "
        f"stated in {geometry_ref} and are not repeated here.",
        _control_sign_convention("flap", "wing"),
        _SPANWISE_RULE,
        "The chordwise profile tapers from the leading edge of the flap to half "
        "that pressure at its trailing edge, so the mean pressure is three "
        "quarters of the leading-edge value and the load is that mean over the "
        "flap's area.",
    ]
    if slipstream_is_available(project):
        body.append(
            "The propeller slipstream case of 23.457(b) applies: the load "
            "inside the slipstream is raised by the factor stated above, over "
            "the span the slipstream covers, and the gust-combined load of "
            "23.345(b)(1) is stated beside it.")
    else:
        body.append(
            "The propeller slipstream case of 14 CFR 23.457(b) is not analysed "
            "for this airplane: it exists only where an engine record supplies "
            "take-off power and a propeller diameter, and none does. The flap "
            "is therefore sized on the conditions above alone. Where a "
            "slipstream case does exist it raises the flap load materially -- "
            "on the suite's own light-twin example by about a fifth -- so this "
            "is an absence to close before the flap is sized, not a case that "
            "was found not to govern.")
    discrepancy = _area_discrepancy(project, "flap", entered_area, system)
    if discrepancy:
        body.append(discrepancy)
    body.append(_HINGE_MOMENT_ABSENCE)
    figures = [
        _control_chord_figure(records, key="chordwise_flap",
                              title="Flap chordwise pressure (LIMIT)",
                              surface="flap", host="wing", system=system),
        _control_locator_figure(project, key="locator_flap",
                                title="The flap on the wing",
                                surface="flap", host="wing", system=system),
    ]
    return Section("", body=body, tables=tables, figures=figures)


# --- Section 9 -- the tabs --------------------------------------------------- #
def _tab_rectangle(project: Project, spec, host: str,
                   scale: float) -> Tuple[List[Series], str]:
    """The tab drawn as the rectangle of its entered area at its station (OR-155).

    A tab has no entered outline anywhere in the schema: it is placed by
    ``station_in`` and sized by ``mac_in`` and ``area_sqft``. The rectangle is
    the entered area at the entered station, of chord ``MACTAB`` and span
    ``STAB/MACTAB``, with its trailing edge on the host's -- and the caption
    says so in as many words, because a shape a reader could mistake for
    entered geometry is exactly what this document must not draw silently.
    """
    surface = project.geometry.by_name(host) if project.geometry else None
    mac = float(getattr(spec, "mac_in", 0.0) or 0.0)
    area_sqin = float(getattr(spec, "area_sqft", 0.0) or 0.0) * IN2_PER_FT2
    if surface is None or mac <= 0 or area_sqin <= 0:
        return [], ""
    edge = sorted(((float(v[0]), float(v[1])) for v in surface.trailing_edge),
                  key=lambda point: point[1])
    if len(edge) < 2:
        return [], ""

    def station_at(y: float) -> float:
        """The host's trailing-edge station at butt line ``y``, clamped."""
        if y <= edge[0][1]:
            return edge[0][0]
        if y >= edge[-1][1]:
            return edge[-1][0]
        for first, second in zip(edge, edge[1:]):
            if first[1] <= y <= second[1]:
                span = second[1] - first[1]
                if span <= 0:
                    return first[0]
                return first[0] + (second[0] - first[0]) * (y - first[1]) / span
        return edge[-1][0]

    span_in = area_sqin / mac
    centre = float(getattr(spec, "station_in", 0.0) or 0.0)
    y0, y1 = centre - span_in / 2.0, centre + span_in / 2.0
    corners = [(station_at(y0), y0), (station_at(y0) - mac, y0),
               (station_at(y1) - mac, y1), (station_at(y1), y1)]
    from .planform_tex import REGION_STYLES

    frame = _CONTROL_HOSTS.get(host, ("htail", "butt", "z"))[1]
    oriented = [_oriented(frame, x * scale, y * scale) for x, y in corners]
    note = (
        "The tab planform is not entered anywhere in the project: it is placed "
        "by the station of its MAC and sized by its MAC and its area. The "
        "rectangle drawn here is that entered area at that entered station -- "
        "its chord is the entered MAC and its span is the area divided by it, "
        "with its trailing edge on the host surface's. It is a drawing, not "
        "geometry the analysis used.")
    return [Series("Tab (drawn from its entered area)",
                   [x for x, _y in oriented], [y for _x, y in oriented],
                   REGION_STYLES[1], closed=True)], note


def _tab_table(result: Optional[ModuleResult], project: Project,
               system: UnitSystem) -> Optional[Table]:
    """One row per tab: where it is, what it is, and the pressures to apply."""
    conditions = list(getattr(result, "conditions", ()) or ())
    specs = list(getattr(project.tab_loads, "tabs", ()) or ())
    if not conditions:
        return None
    u = Units(system)
    scale, length = _length_channel(system)
    area_scale, area_units = _scalar_channel("ft^2", system)
    p_scale, p_units = _scalar_channel("lb/in^2", system)
    rows = []
    for condition, spec in zip(conditions, specs + [None] * len(conditions)):
        values = _by_key(condition)
        host = (getattr(spec, "surface", "") or "").strip().lower()
        station = _TAB_STATION_NAMES.get(host, "Station")
        rows.append([
            _REGION_NAMES.get(_TAB_HOSTS.get(host, host), host or "--"),
            f"{station} {format_value((getattr(spec, 'station_in', 0.0) or 0.0) * scale)} {length}"
            if spec is not None else "--",
            _scalar_cell(getattr(spec, "area_sqft", None), area_scale)
            if spec is not None else "--",
            _scalar_cell(getattr(spec, "mac_in", None), scale)
            if spec is not None else "--",
            format_value(values["tab_chord_ratio_e"].value)
            if "tab_chord_ratio_e" in values else "--",
            u.load(values["tab_load"].value, "force",
                   float(getattr(condition, "safety_factor", ULTIMATE_FACTOR)
                         or ULTIMATE_FACTOR))
            if "tab_load" in values else "--",
            _scalar_cell(values["tab_le_pressure"].value, p_scale)
            if "tab_le_pressure" in values else "--",
            _scalar_cell(values["tab_te_pressure"].value, p_scale)
            if "tab_te_pressure" in values else "--",
            format_value(float(getattr(condition, "safety_factor",
                                       ULTIMATE_FACTOR) or ULTIMATE_FACTOR)),
        ])
    return Table(
        title="Tab loads at full deflection at VC (LIMIT)",
        columns=["Tab in", "Station of the MAC", f"Area ({area_units})",
                 f"MAC ({length})", "Chord ratio E",
                 f"Load ({u.ult_label('force')})",
                 f"LE pressure ({p_units})", f"TE pressure ({p_units})", "SF"],
        rows=rows,
        note=("One row per tab. The station column names which station it is: a "
              "butt line for a tab in a wing or horizontal-tail control "
              "surface, a waterline for one in a rudder, never a bare number. "
              "Every load is LIMIT and states the factor its condition does "
              "not apply."))


def _tab_loads(project: Project,
               results: Mapping[str, Optional[ModuleResult]], *,
               system: UnitSystem,
               plan: Sequence[SectionPlan]) -> Section:
    """Section 9 -- the control-surface tabs."""
    records = _control_records(project, "tab")
    specs = list(getattr(project.tab_loads, "tabs", ()) or ())
    if not records or not specs:
        return Section("", absent_reason=(
            "no control-surface tab is entered for this project, so there is "
            "no tab load to state."))
    geometry_ref = section_ref(plan, "configuration_layout")
    result = results.get("tab_loads")
    scale, _length = _length_channel(system)
    # The convention is one statement, and every tab in a project is cut into a
    # control surface whose normal is read the same way; the first tab names
    # which host that is, and G-OR-100 holds the sentence to it.
    _first_tab_host = _TAB_HOSTS.get(
        (specs[0].surface or "").strip().lower(), "elevator")
    body = [
        f"Tabs are designed for full deflection at the design cruising speed "
        f"VC, per 14 CFR 23.409. The tab's lift is built from its chord as a "
        f"fraction of the host airfoil's, and the lift the tab carries from the "
        f"host surface's own lift is neglected. Each tab's geometry -- its MAC, "
        f"its area, the station of its MAC and the host airfoil chord there -- "
        f"is stated in {geometry_ref} and is not repeated here.",
        "A tab is cut into a control surface, not into the fixed surface it "
        "hangs from, so the figures below draw it on the elevator, the rudder "
        "or the aileron rather than on the horizontal tail, the fin or the "
        "wing.",
        _control_sign_convention(_first_tab_host,
                                 _CONTROL_HOSTS[_first_tab_host][0],
                                 label="tab"),
        _SPANWISE_RULE,
        "The chordwise profile is trapezoidal per CAM 3.224-1(b): the pressure "
        "at the leading edge is twice the pressure at the trailing edge, so the "
        "mean is one and a half times the trailing-edge value and the load is "
        "that mean over the tab's area.",
        _HINGE_MOMENT_ABSENCE,
    ]
    figures = []
    for index, (record, spec) in enumerate(zip(records, specs)):
        host = _TAB_HOSTS.get((spec.surface or "").strip().lower(), "elevator")
        printed = _REGION_NAMES.get(host, host).lower()
        figures.append(_control_chord_figure(
            [record], key=f"chordwise_tab_{index}",
            title=f"Tab chordwise pressure, {printed} (LIMIT)",
            surface=host, host=_CONTROL_HOSTS.get(host, ("htail", "butt", "z"))[0],
            system=system, label="tab"))
        extra, note = _tab_rectangle(project, spec, host, scale)
        figures.append(_control_locator_figure(
            project, key=f"locator_tab_{index}",
            title=f"The tab on the {printed}",
            surface=host,
            host=_CONTROL_HOSTS.get(host, ("htail", "butt", "z"))[0],
            system=system, extra=extra, extra_note=note, label="tab"))
    return Section("", body=body,
                   tables=[t for t in (_tab_table(result, project, system),)
                           if t is not None],
                   figures=figures)


# --------------------------------------------------------------------------- #
# Section 10 -- engine mount loads (note 44 §20)
# --------------------------------------------------------------------------- #
#: ``(frame, figure key, title, what the view is)`` for the three views OR-168
#: asks for. The frame keys are :data:`_PLANFORM_AXES`' own, so a figure asks for
#: the view it plots and the axis labels come from the one owner of them.
_ENGINE_VIEWS: Tuple[Tuple[str, str, str, str], ...] = (
    ("water", "engine_side_view", "The engine installation in side view",
     "Looking at the left-hand side of the airplane"),
    ("front", "engine_front_view", "The engine installation in front view",
     "Looking aft, from ahead of the airplane"),
    ("butt", "engine_plan_view", "The engine installation in plan view",
     "Looking down on the airplane"),
)

#: The two panels of :func:`sloads.modules.configuration.tail_planform` this
#: section draws. The elevator and rudder bands it also returns belong to
#: sections 7-9, and drawing them here would put a control surface on a figure
#: whose subject is an engine.
_ENGINE_TAIL_PANELS = (("h_tail", "Horizontal tail"), ("v_tail", "Vertical tail"))

#: ``_ENGINE_VIEWS`` frame -> the view key ``tail_planform`` returns it under.
_TAIL_VIEW_OF_FRAME = {"butt": "top", "water": "side", "front": "front"}

#: ``(attribute, unit string, printed name)`` of every engine input 10.1 prints.
#:
#: A row every engine leaves blank is dropped, which is how a reciprocating
#: installation prints no turbopropeller rows and a turbopropeller one prints no
#: cylinder count. That is *not* OR-140's zero-column rule read backwards: OR-140
#: is about a delivered load component, where a zero is a result; this is an
#: input nobody entered because the condition it feeds does not exist.
_ENGINE_INPUT_FIELDS: Tuple[Tuple[str, str, str], ...] = (
    ("engine_designation", "", "Engine designation"),
    ("prop_designation", "", "Propeller designation"),
    ("engine_type", "", "Engine type"),
    ("mounted_on", "", "Reacted into"),
    ("limit_load_factor", "", "Limit manoeuvre load factor n"),
    ("engine_weight_lb", "lb", "Engine weight"),
    ("prop_weight_lb", "lb", "Propeller weight"),
    ("hub_weight_lb", "lb", "Hub weight"),
    ("prop_diameter_in", "in", "Propeller diameter"),
    ("prop_blades", "", "Number of propeller blades"),
    ("takeoff_rpm", "", "Propeller take-off RPM"),
    ("max_cont_rpm", "", "Propeller max continuous RPM"),
    ("takeoff_hp", "", "Take-off horsepower"),
    ("max_cont_hp", "", "Max continuous horsepower"),
    ("cylinders", "", "Number of cylinders"),
    ("max_engine_torque", "ft-lb", "Max engine torque"),
    ("cruise_torque", "ft-lb", "Cruise torque"),
    ("stop_time_s", "", "Time to sudden stoppage (s)"),
)

#: The printed name of each engine type, so a schema code never reaches a table.
_ENGINE_TYPE_NAMES = {"R": "Reciprocating", "T": "Turbopropeller"}


class _EngineCase(NamedTuple):
    """One printed engine-mount case: its identity and its two published forms.

    ``force``/``moment`` are the OR-160 set -- what the engine applies to the
    airframe, in airplane axes, at ``point``. ``torque``/``thrust`` are the two
    scalars about the engine's own thrust line that ``force``/``moment`` were
    resolved from, and they are carried rather than re-derived so **G-OR-104**
    can compare the two forms without either side re-computing the other.
    """
    engine: int
    case_id: str
    far: str
    condition: str
    sf: float
    point: Tuple[float, float, float]
    force: Tuple[float, float, float]
    moment: Tuple[float, float, float]
    torque: float
    thrust: float


class _EngineRecord(NamedTuple):
    """One engine, its thrust axis and the conditions the module ran for it.

    ``number`` rather than ``index`` because a ``NamedTuple`` is a tuple and
    ``index`` is one of the two methods a tuple already has.
    """
    number: int
    engine: EngineInput
    axis: Tuple[float, float, float]
    axis_assumed: bool
    cases: List[_EngineCase]


def _engine_number(value) -> float:
    """A ``LoadValue`` cell as a float, with the model's "not applicable" empties.

    ``_gyro_subcases`` yields ``""`` for a component a sub-case does not carry,
    and a condition simply omits a key it has no value for. Both mean zero *for
    the purpose of assembling a six-component set*, which is exactly OR-140's
    reading: a component that does not apply is a zero in an applied set, and it
    is printed rather than left blank so nobody reads the gap as an omission.
    """
    if value is None or value == "":
        return 0.0
    return float(value)


def _engine_value(values: Mapping[str, LoadValue], key: str) -> float:
    """One published component of a condition, or zero where it has none."""
    found = values.get(key)
    return _engine_number(found.value) if found is not None else 0.0


def _engine_cases(number: int, eng: EngineInput, axis: Tuple[float, float, float],
                  conditions: Sequence[ConditionResult]) -> List[_EngineCase]:
    """Every printed case for one engine, resolved onto the airplane axes.

    Nothing is resolved here: :func:`sloads.export.coordinates.engine_applied_load`
    is asked, on OR-161's reasoning that an axis resolution has one owner and the
    report is not it. The gyroscopic sign combinations are fanned out through
    ``render._gyro_subcases`` and identified with ``render._gyro_subcase_id``,
    the owners that already mint those a/b/c/d ids for the CSV (OR-165).
    """
    from ..export.coordinates import engine_applied_load
    from ..load_keys import FY_SIDE, FZ_VERTICAL, MX_MOUNT_TORQUE
    from ..modules.engine import combined_cg
    from .render import _gyro_subcases, _has_gyro_subcases

    point = combined_cg(eng)
    out: List[_EngineCase] = []
    for condition in conditions:
        sf = float(condition.safety_factor or ULTIMATE_FACTOR)
        base = condition.case_ref.case_id if condition.case_ref else ""
        if _has_gyro_subcases(condition):
            for desc, myy, mzz, thrust, vertical, case_id in _gyro_subcases(condition):
                force, moment = engine_applied_load(
                    axis, thrust=_engine_number(thrust),
                    vertical_down=_engine_number(vertical),
                    myy=_engine_number(myy), mzz=_engine_number(mzz))
                out.append(_EngineCase(
                    number, case_id or base, condition.far_reference,
                    _engine_condition_name(desc), sf, point, force, moment,
                    0.0, _engine_number(thrust)))
            continue
        values = _by_key(condition)
        torque = _engine_value(values, MX_MOUNT_TORQUE)
        force, moment = engine_applied_load(
            axis, torque=torque,
            vertical_down=_engine_value(values, FZ_VERTICAL),
            side=_engine_value(values, FY_SIDE))
        out.append(_EngineCase(
            number, base, condition.far_reference,
            _engine_condition_name(condition.title), sf, point, force, moment,
            torque, 0.0))
    return out


def _engine_condition_name(title: str) -> str:
    """A condition's name with the module's multi-engine ``[designation]`` tag off.

    The tag exists so a concatenated ``ModuleResult`` keeps its per-engine groups
    distinct; here the engine is a column of its own, and repeating a
    designation on every row of a two-engine airplane would push the name that
    actually varies off the page.
    """
    if title.startswith("[") and "] " in title:
        return title.split("] ", 1)[1]
    return title


#: FAR reference -> the short name 10.2's tables print for that condition.
#:
#: A second name for a condition, and deliberately so, on the same reasoning that
#: gives this document its own section headings rather than the workflow's step
#: titles: the module's title is a full sentence written for a results page, and
#: ten of them down a ten-column table push the numbers off the page. 10.1's case
#: list prints the module's own title against the same case ID, so both names are
#: in the document and the mapping between them is visible rather than implied.
#: **G-OR-112** holds every reference the module can produce to an entry here, so
#: a condition added later cannot print a blank.
_ENGINE_SHORT_NAMES = {
    "23.361(a)(1)": "Take-off torque, 75 % n",
    "23.361(a)(2)": "Max continuous torque, 100 % n",
    "23.361(a)(3)": "Propeller control malfunction",
    "23.361(b)(1)": "Sudden stoppage",
    "23.363(a)&(b)": "Side load",
    "23.371(b)": "Gyroscopic",
    "25.361(a)(3)(i)": "Sudden deceleration with 1 g",
    "25.361(a)(3)(ii)": "Max accelerating torque",
    "25.371": "Gyroscopic",
}

#: The sign-combination tag inside a gyro sub-case description ("(+Myy, -Mzz)").
#:
#: Matched on the exact shape ``_gyro_subcases`` builds rather than on "a
#: parenthesis containing an M": a condition title is prose, and
#: 23.361(a)(1)'s own reads "(factor x mean)". A loose pattern would print that
#: as a sub-case tag.
_GYRO_COMBINATION = re.compile(r"\(([+-]M(?:yy|zz),\s*[+-]M(?:yy|zz))\)")


def _engine_short_name(far: str, description: str) -> str:
    """The short condition name a load table prints, with its sub-case tag."""
    name = _ENGINE_SHORT_NAMES.get(far, _engine_condition_name(description))
    found = _GYRO_COMBINATION.search(description)
    return f"{name} ({found.group(1)})" if found else name


def _engine_records(project: Project,
                    results: Mapping[str, Optional[ModuleResult]],
                    ) -> List[_EngineRecord]:
    """Each engine with its axis and its own slice of the module's conditions.

    The module concatenates every engine's conditions into one ``ModuleResult``
    and ties them to an engine only by a title prefix, which two engines of the
    same designation share (``baron_58``). So the grouping is rebuilt by asking
    the module how many conditions *this* engine produces and taking that many in
    order -- the order ``engine.run`` itself allocates case ids in. It is checked,
    not assumed: a slice that does not consume every condition exactly returns
    nothing, and the section states its absence rather than printing rows against
    the wrong engine.
    """
    from ..export.coordinates import engine_thrust_axis
    from ..modules.engine import resolved_engines, run_all

    result = results.get("engine_mount")
    if result is None or not project.engines:
        return []
    conditions = list(result.conditions)
    try:
        engines = resolved_engines(project)
    except MissingInputError:
        return []
    records: List[_EngineRecord] = []
    taken = 0
    for number, eng in enumerate(engines, start=1):
        try:
            count = len(run_all(eng, include_far25=project.include_far25))
        except MissingInputError:
            return []
        mine = conditions[taken:taken + count]
        if len(mine) != count:
            return []
        taken += count
        axis, assumed = engine_thrust_axis(eng.engine_cg, eng.prop_cg)
        records.append(_EngineRecord(
            number, eng, axis, assumed, _engine_cases(number, eng, axis, mine)))
    return records if taken == len(conditions) else []


# --- 10.1 -- the inputs, the stations and the cases -------------------------- #
def _engine_input_cell(value, units: str, system: UnitSystem) -> str:
    """One entered engine quantity in the document's units, or an empty cell."""
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return _ENGINE_TYPE_NAMES.get(value, value)
    if not units:
        return format_value(value)
    scale, _label = _scalar_channel(units, system)
    return format_value(float(value) * scale)


def _engine_entered(value) -> bool:
    """Whether an optional engine input was entered at all.

    A blank *and* a zero both mean "not entered" for these fields -- the schema
    defaults every optional number to ``0.0`` and the module reads a zero
    propeller diameter as no propeller -- so a turbofan entered with no
    propeller prints no propeller rows instead of eight zeros. This is the
    opposite of OR-140's rule for a *delivered* component, where a zero is the
    result and is printed: an input nobody typed is not a measurement.
    """
    if value is None or value == "":
        return False
    if isinstance(value, str):
        return True
    try:
        return float(value) != 0.0
    except (TypeError, ValueError):
        return True


def _engine_input_table(records: Sequence[_EngineRecord],
                        system: UnitSystem) -> Optional[Table]:
    """The entered engine and propeller data, one column per engine."""
    if not records:
        return None
    rows = []
    for attr, units, label in _ENGINE_INPUT_FIELDS:
        cells, entered = [], False
        for record in records:
            raw = getattr(record.engine, attr, None)
            raw = getattr(raw, "value", raw)
            entered = entered or _engine_entered(raw)
            cells.append(_engine_input_cell(raw, units, system))
        if not entered:
            continue
        printed = label
        if units:
            _scale, label_units = _scalar_channel(units, system)
            printed = f"{label} ({label_units})"
        rows.append([printed] + cells)
    if not rows:
        return None
    return Table(
        title="Engine and propeller data as entered",
        columns=["Quantity"] + [f"Engine {r.number}" for r in records],
        rows=rows,
        note=("Every value is the project's own input, reproduced unconverted "
              "except into this document's units. A row no engine fills is not "
              "printed: a reciprocating installation states no cruise torque and "
              "a turbopropeller states no cylinder count, because the conditions "
              "those feed do not exist for it."))


def _engine_point_cell(point: Sequence[float], scale: float) -> str:
    """An ``(x, y, z)`` station as the one cell the oracle prints it as."""
    return ", ".join(format_value(v * scale) for v in point)


def _engine_station_table(records: Sequence[_EngineRecord],
                          system: UnitSystem) -> Optional[Table]:
    """Where each engine sits, and the axis its torque and thrust act about."""
    if not records:
        return None
    scale, length = _length_channel(system)
    rows = []
    for record in records:
        eng = record.engine
        rows.append([
            str(record.number),
            eng.engine_designation or "--",
            _engine_point_cell(eng.engine_cg, scale),
            _engine_point_cell(eng.prop_cg, scale),
            _engine_point_cell(record.cases[0].point if record.cases
                               else (0.0, 0.0, 0.0), scale),
            ", ".join(f"{c:.4f}" for c in record.axis)
            + (" (ASSUMED)" if record.axis_assumed else ""),
        ])
    return Table(
        title="Where the loads act",
        columns=["Engine", "Designation",
                 f"Mount node X, Y, Z ({length})",
                 f"Hub node X, Y, Z ({length})",
                 f"Application point X, Y, Z ({length})",
                 "Thrust axis l, m, n"],
        rows=rows,
        note=("Three stations, and the loads are quoted about exactly one of "
              "them. The application point is the combined engine and "
              "propeller CG -- the point the oracle prints as APPLIED AT X,Y,Z "
              "-- and every component in the next section acts there. The mount "
              "and hub nodes are the beam model's own and are printed because "
              "a reader transferring "
              "this set to a mount plane needs the offsets; no load is quoted "
              "about them. The thrust axis is the direction from the mount node "
              "to the hub node, forward; where the two coincide it cannot be "
              "derived, and the airplane's forward axis is used and marked "
              "ASSUMED. It is the best statement of the thrust line the entered "
              "data supports and not a measured one: the true line is the shaft "
              "axis, and an engine CG that sits off that axis inclines the "
              "derived direction by the offset over the mount-to-hub distance. "
              "Where that matters, entering the engine CG and the hub on the "
              "shaft axis states it."))


def _engine_case_list_table(records: Sequence[_EngineRecord]) -> Optional[Table]:
    """Every case the module ran, by regulation, with the factor it prescribes."""
    rows = [[str(case.engine), case.case_id or "--", case.far, case.condition,
             format_value(case.sf)]
            for record in records for case in record.cases]
    if not rows:
        return None
    return Table(
        title="Load cases assessed",
        columns=["Engine", "Case ID", "FAR", "Condition", "SF"],
        rows=rows,
        note=("The conditions are enumerated by the regulation, not selected "
              "from a sweep: every one listed is assessed and every one is "
              "reported in the next section. Each of the four 23.371(b) "
              "gyroscopic sign combinations is its own case, carrying the base "
              "case ID with an a/b/c/d suffix. Every case is LIMIT and states "
              "the factor 14 CFR 23.303 prescribes for it, which is applied to "
              "none of them."))


_ENGINE_SIGN_CONVENTION = (
    "The loads in this section are what the engine applies to the airframe. "
    "That is the sense every other applied load set in this document is "
    "published in, and it is what a mount is sized for. It is stated plainly "
    "because the oracle's own output, and the load-case file the Engine Mount "
    "page writes, print the same load under the heading ENG MOUNT TORQUE as a "
    "single negative number about the thrust line, and a reader who takes one "
    "for the other will size a mount backwards."
)

_ENGINE_AXES = (
    "Components are airplane axes throughout: X positive aft, Y positive to "
    "starboard, Z positive up, and moments right-handed about them. About the "
    "engine's own thrust line the positive sense is clockwise seen from the "
    "pilot's seat, which is the right-hand sense about that line because the "
    "pilot looks along it. The thrust line points forward, so the two sign "
    "conventions run opposite ways along the fore-and-aft axis: a conventional "
    "propeller turning clockwise from the seat delivers a counter-clockwise, "
    "negative torque to the airframe about its thrust line, and that same load "
    "about the aft-positive X axis is a positive Mx, which rolls the airplane "
    "to the left. Both numbers are printed, in the two tables of the next "
    "subsection, and they are one load."
)

_ENGINE_THRUST_ABSENCE = (
    "Thrust appears in the gyroscopic case and in no other. 14 CFR 23.361 and "
    "23.363 prescribe a torque, a vertical load factor and a side load, and no "
    "thrust at all; 23.371(b) prescribes the max continuous thrust explicitly, "
    "acting with the gyroscopic moments. The zeros in the other rows are "
    "therefore results and not omissions. They are not filled from the engine's "
    "entered design thrust, which is a flight input applied at the hub in the "
    "assembled balanced cases and is not a component of any engine-mount "
    "condition."
)

_ENGINE_SIDE_LOAD_SENSE = (
    "The 23.363 side load acts in either direction and the analysis publishes "
    "one signed value, so it is printed as acting to starboard and the mount is "
    "to be checked for both senses. It is not printed twice: the gyroscopic "
    "combinations are four cases because the analysis ran four, and a second "
    "side-load row would be this document inventing a case that was not run."
)


def _engine_inputs(records: Sequence[_EngineRecord], *,
                   system: UnitSystem, plan: Sequence[SectionPlan]) -> Section:
    """10.1 -- what the analysis was run from, and where its loads act."""
    geometry_ref = section_ref(plan, "configuration_layout")
    assumed = [r for r in records if r.axis_assumed]
    body = [
        f"The engine mount loads are the conditions of 14 CFR 23.361, 23.363 "
        f"and, for a turbopropeller installation, 23.371(b). They are computed "
        f"per engine from the engine and propeller weights, their stations and "
        f"the engine's rated powers or torques; the airplane geometry they sit "
        f"in is stated in {geometry_ref} and is not repeated here.",
        _ENGINE_SIGN_CONVENTION,
        _ENGINE_AXES,
        _ENGINE_THRUST_ABSENCE,
        _ENGINE_SIDE_LOAD_SENSE,
    ]
    if assumed:
        which = ", ".join(str(r.number) for r in assumed)
        body.append(
            f"The thrust axis of engine {which} is ASSUMED: the project "
            f"enters the propeller hub at the engine CG, so there is no "
            f"direction to derive it from and the airplane's forward axis is "
            f"used. Enter the propeller CG to state it. Nothing else in this "
            f"section changes -- the torque and thrust magnitudes are the "
            f"analysis's own -- but the axis they are resolved onto is this "
            f"document's assumption and is marked as one wherever it appears.")
    tables = [t for t in (_engine_input_table(records, system),
                          _engine_station_table(records, system),
                          _engine_case_list_table(records)) if t is not None]
    return Section("", body=body, tables=tables)


# --- 10.2 -- the loads ------------------------------------------------------- #
def _engine_moment_channel(records: Sequence[_EngineRecord],
                           system: UnitSystem) -> Tuple[float, str]:
    """``(scale, label)`` for the moment columns, marked ULT only if every case is.

    Every engine-mount condition classifies ``flight`` in the governing
    safety-factor table, so in practice the label is plain and each row states
    its 1.5 in the SF column. The check is written anyway, because a column
    header that cannot become ``-ULT`` is a header that will be wrong the day a
    condition prescribing an already-ultimate load joins the set.
    """
    scale, label = _scalar_channel("ft-lb", system)
    factors = {case.sf for record in records for case in record.cases}
    return scale, (ultimate_units(label) if factors == {1.0} else label)


def _engine_components_table(records: Sequence[_EngineRecord],
                             system: UnitSystem) -> Optional[Table]:
    """OR-163's first table: the six components, in airplane axes, per case."""
    if not records:
        return None
    u = Units(system)
    scale, moment_label = _engine_moment_channel(records, system)
    rows = []
    for record in records:
        for case in record.cases:
            rows.append(
                [str(case.engine), case.case_id or "--",
                 _engine_short_name(case.far, case.condition)]
                + [u.load(component, "force", case.sf) for component in case.force]
                + [format_value(component * scale) for component in case.moment]
                + [format_value(case.sf)])
    force_label = u.ult_label("force", 1.0 if {c.sf for r in records
                                              for c in r.cases} == {1.0} else 0.0)
    return Table(
        title="Engine mount loads in airplane axes (LIMIT)",
        columns=["Engine", "Case ID", "Condition",
                 f"Fx ({force_label})", f"Fy ({force_label})",
                 f"Fz ({force_label})",
                 f"Mx ({moment_label})", f"My ({moment_label})",
                 f"Mz ({moment_label})", "SF"],
        rows=rows,
        note=("All six components of the load the engine applies to the "
              "airframe, at the application point stated in the previous "
              "subsection and about no other point. Every one is LIMIT and "
              "states the factor 14 CFR 23.303 prescribes, which is applied to "
              "none of them. A zero is a component the condition does not "
              "prescribe, and it is printed as one. The regulation each case is "
              "drawn from, and the condition's full name, are in the case list "
              "of the previous subsection against the same case ID."))


def _engine_thrust_line_table(records: Sequence[_EngineRecord],
                              system: UnitSystem) -> Optional[Table]:
    """OR-163's second table: the two scalars the six components resolve from."""
    if not records:
        return None
    u = Units(system)
    scale, moment_label = _engine_moment_channel(records, system)
    rows = [[str(case.engine), case.case_id or "--",
             _engine_short_name(case.far, case.condition),
             format_value(case.torque * scale),
             u.load(case.thrust, "force", case.sf),
             format_value(case.sf)]
            for record in records for case in record.cases]
    return Table(
        title="Engine torque and thrust about the thrust line (LIMIT)",
        columns=["Engine", "Case ID", "Condition",
                 f"Torque about thrust line ({moment_label})",
                 f"Thrust along thrust line ({u.ult_label('force')})", "SF"],
        rows=rows,
        note=("The same cases in the engine's own axis: the torque about the "
              "thrust line and the thrust along it, thrust positive forward and "
              "torque positive clockwise from the pilot's seat. These are the "
              "two scalars the table above was resolved from, printed so the "
              "resolution can be repeated with the direction cosines of the "
              "previous subsection rather than taken on trust; they are also "
              "the numbers the oracle prints, unchanged. A conventional "
              "propeller's torque on the airframe is counter-clockwise from the "
              "seat, so this column is negative where the Mx beside it is "
              "positive: the same load, once about a forward-pointing axis and "
              "once about the aft-positive X axis."))


def _engine_cases_section(records: Sequence[_EngineRecord], *,
                          system: UnitSystem) -> Section:
    """10.2 -- the critical cases, in both forms."""
    body = [
        "Every case of every engine is printed: the conditions are prescribed "
        "by regulation rather than selected, so there is no case that was "
        "assessed and not reported. Each engine carries its own rows at its own "
        "butt line -- two mounts are two structures, and neither is the mirror "
        "of the other for the purpose of sizing one.",
        "The first table is the load the engine applies to the airframe, "
        "resolved onto the airplane axes; the second is the same load as the "
        "torque and thrust about the engine's own thrust line, which is what "
        "the first was resolved from.",
    ]
    tables = [t for t in (_engine_components_table(records, system),
                          _engine_thrust_line_table(records, system))
              if t is not None]
    return Section("", body=body, tables=tables)


# --- 10's figures -- three views, with whatever airframe is entered ---------- #
#: The barb length and half-angle of a drawn arrow head, as a fraction of the
#: shaft and in radians. An arrow is a polyline here because a figure carries no
#: arrow primitive, and it must stay legible in greyscale like every other line
#: (§4.3).
_ARROW_BARB = 0.22
_ARROW_ANGLE = 0.42


def _arrow(x0: float, y0: float, dx: float, dy: float,
           ) -> Tuple[List[float], List[float]]:
    """One arrow from ``(x0, y0)`` along ``(dx, dy)``, as a single polyline."""
    tip_x, tip_y = x0 + dx, y0 + dy
    length = math.hypot(dx, dy)
    if length <= 0:
        return [x0], [y0]
    ux, uy = dx / length, dy / length
    barb = _ARROW_BARB * length
    cos_a, sin_a = math.cos(_ARROW_ANGLE), math.sin(_ARROW_ANGLE)
    left = (-ux * cos_a + uy * sin_a, -uy * cos_a - ux * sin_a)
    right = (-ux * cos_a - uy * sin_a, -uy * cos_a + ux * sin_a)
    return (
        [x0, tip_x, tip_x + barb * left[0], tip_x, tip_x + barb * right[0]],
        [y0, tip_y, tip_y + barb * left[1], tip_y, tip_y + barb * right[1]],
    )


def _edge_points(edge) -> List[Tuple[float, float]]:
    """One entered edge polyline as ``(station, butt line)`` pairs.

    The schema stores a point as a pair, and a future named type would store it
    as attributes; both are read, so this section does not have to be revisited
    to keep drawing a wing.
    """
    points = []
    for point in edge or ():
        x = getattr(point, "x", None)
        y = getattr(point, "y", None)
        if x is None or y is None:
            try:
                x, y = point[0], point[1]
            except (TypeError, IndexError, KeyError):
                continue
        points.append((float(x), float(y)))
    return points


def _wing_view_series(project: Project, frame: str, scale: float) -> List[Series]:
    """The wing in one view: its entered planform, or the line the view sees.

    A planform is a shape in one view and a line in the other two, and the two
    lines are not the planform rotated -- they are the wing reference plane,
    which is geometry the entered polylines do not carry. Both come from
    :func:`sloads.derived_geometry.wing_reference`, the owner of the reference
    plane's waterline and dihedral, so this figure and Section 2 place the same
    wing.
    """
    from .planform_tex import OUTLINE_STYLE

    if frame == "butt":
        return _outline_series(project, "wing", OUTLINE_STYLE, True, "butt", scale)
    surface = project.geometry.by_name("wing") if project.geometry else None
    reference = wing_reference(project)
    if surface is None or reference is None:
        return []
    leading, trailing = _edge_points(surface.leading_edge), _edge_points(surface.trailing_edge)
    if not leading or not trailing:
        return []
    wrp = reference.wrp_waterline
    if frame == "water":
        # The innermost point of each edge, through the tie owner: an edge
        # polyline that repeats its root butt line is the state the curve editor
        # persists mid-row, and the two would otherwise be picked differently.
        root_le = extreme(leading, key=lambda p: abs(p[1]), largest=False)[0]
        root_te = extreme(trailing, key=lambda p: abs(p[1]), largest=False)[0]
        points = [_oriented(frame, root_le * scale, wrp * scale),
                  _oriented(frame, root_te * scale, wrp * scale)]
        return [Series("Wing root chord", [p[0] for p in points],
                       [p[1] for p in points], OUTLINE_STYLE)]
    tip = max(abs(p[1]) for p in leading + trailing)
    rise = tip * math.tan(math.radians(reference.dihedral_deg))
    points = [_oriented(frame, -tip * scale, (wrp + rise) * scale),
              _oriented(frame, 0.0, wrp * scale),
              _oriented(frame, tip * scale, (wrp + rise) * scale)]
    return [Series("Wing reference plane", [p[0] for p in points],
                   [p[1] for p in points], OUTLINE_STYLE)]


def _tail_view_series(project: Project, frame: str, scale: float) -> List[Series]:
    """Both empennage surfaces in one view, through the three-view's own owner.

    :func:`sloads.modules.configuration.tail_planform` already returns each panel
    in all three views and already reads ``tail_geometry.fin_root_waterline`` for
    where the fin's root sits, so asking it is what stops this figure putting the
    fin at a second waterline (``CONVENTIONS.md`` §7 rule 2).
    """
    from ..modules.configuration import tail_planform
    from .planform_tex import OUTLINE_STYLE

    geometry = project.geometry
    layout = geometry.parametric if geometry is not None else None
    if layout is None or geometry is None:
        return []
    try:
        panels = tail_planform(layout, geometry.empennage, project)
    except (ValueError, TypeError, ZeroDivisionError, AttributeError):
        return []
    view = _TAIL_VIEW_OF_FRAME[frame]
    series = []
    for key, label in _ENGINE_TAIL_PANELS:
        polyline = (panels.get(key) or {}).get(view) or []
        if len(polyline) < 2:
            continue
        points = [_oriented(frame, a * scale, b * scale) for a, b in polyline]
        series.append(Series(label, [p[0] for p in points], [p[1] for p in points],
                             OUTLINE_STYLE, closed=len(points) > 2))
    return series


def _airframe_series(project: Project, frame: str,
                     scale: float) -> Tuple[List[Series], List[str]]:
    """Every airframe outline this view can draw, and the names of the ones drawn."""
    from ..derived_geometry import fuselage_outline
    from .planform_tex import OUTLINE_STYLE

    series: List[Series] = []
    drawn: List[str] = []
    body = fuselage_outline(project, frame)
    if body:
        points = [_oriented(frame, a * scale, b * scale) for a, b in body]
        series.append(Series("Fuselage", [p[0] for p in points],
                             [p[1] for p in points], OUTLINE_STYLE, closed=True))
        drawn.append("the fuselage")
    wing = _wing_view_series(project, frame, scale)
    if wing:
        series += wing
        drawn.append("the wing")
    tails = _tail_view_series(project, frame, scale)
    if tails:
        series += tails
        drawn.append("the empennage")
    return series, drawn


def _extent(series: Sequence[Series]) -> float:
    """The larger side of the drawn bounding box, for sizing what is drawn on it."""
    xs = [v for s in series for v in s.x]
    ys = [v for s in series for v in s.y]
    if not xs or not ys:
        return 0.0
    return max(max(xs) - min(xs), max(ys) - min(ys))


def _axis_key_series(series: Sequence[Series],
                     points: Sequence[Tuple[str, float, float]]) -> List[Series]:
    """Two arrows in a free corner, showing the view's positive axes.

    OR-168 asks each view to draw the positive senses that lie in its plane, and
    a figure carries no arrow primitive, so they are polylines like everything
    else. Named from :data:`_PLANFORM_AXES` rather than spelled out here: the
    axis a view plots and the axis its key labels cannot then be two answers.
    """
    xs = [v for s in series for v in s.x] + [x for _l, x, _y in points]
    ys = [v for s in series for v in s.y] + [y for _l, _x, y in points]
    if not xs or not ys:
        return []
    width, height = max(xs) - min(xs), max(ys) - min(ys)
    reach = 0.10 * min(width or height, height or width)
    if reach <= 0:
        return []
    x0, y0 = min(xs) + 0.02 * width, min(ys) + 0.02 * height
    out: List[Series] = []
    for index, (dx, dy) in enumerate(((reach, 0.0), (0.0, reach))):
        arrow_x, arrow_y = _arrow(x0, y0, dx, dy)
        out.append(Series("Positive axes" if index == 0 else "",
                          arrow_x, arrow_y, "solid"))
    return out


def _engine_view_figure(project: Project, records: Sequence[_EngineRecord], *,
                        frame: str, key: str, title: str, view: str,
                        system: UnitSystem) -> Figure:
    """One of the three views: the airframe as entered, and the engines on it."""
    if not records:
        return Figure(key=key, title=title, absent_reason=(
            "the project enters no engine, so there is no installation to draw."))
    scale, length_units = _length_channel(system)
    series, drawn = _airframe_series(project, frame, scale)
    # A thrust line long enough to read against whatever was drawn, and a fixed
    # two feet where nothing was: the figure is still the engines, and an
    # unlabelled line of arbitrary length is worse than a stated default.
    reach = _extent(series) * 0.12 or 24.0 * scale
    points: List[Tuple[str, float, float]] = []
    assumed_any = False
    for record in records:
        mount = _oriented(frame, *_projected(frame, record.engine.engine_cg, scale))
        hub = _oriented(frame, *_projected(frame, record.engine.prop_cg, scale))
        applied = _oriented(frame, *_projected(
            frame, record.cases[0].point if record.cases else record.engine.engine_cg,
            scale))
        if record.axis_assumed:
            assumed_any = True
            axis = _oriented(frame, *_projected(frame, record.axis, 1.0))
            hub = (mount[0] + axis[0] * reach, mount[1] + axis[1] * reach)
        label = f"Engine {record.number} thrust line"
        if record.axis_assumed:
            label += " (ASSUMED)"
        arrow_x, arrow_y = _arrow(mount[0], mount[1], hub[0] - mount[0],
                                  hub[1] - mount[1])
        series.append(Series(label, arrow_x, arrow_y, "dashed"))
        points.append((f"{record.number}", applied[0], applied[1]))
    series += _axis_key_series(series, points)
    x_label, y_label = _PLANFORM_AXES[frame]
    outlines = (", ".join(drawn[:-1]) + " and " + drawn[-1]) if len(drawn) > 1 else (
        drawn[0] if drawn else "")
    caption = [
        f"{view}, to scale on equal axes."
        + (f" The airplane is drawn from {outlines} as the project enters them, "
           f"through the owners Section 2 and the configuration three-view draw "
           f"them with, so no shape here is this figure's own."
           if drawn else
           " The project enters no airframe outline this view can draw, so the "
           "engines are drawn alone; the loads and the stations above are "
           "unaffected, since neither is read from a drawn shape."),
        "Each arrow runs from the engine's mount node to its propeller hub and "
        "is the thrust line the torque and the thrust act about, pointing "
        "forward. Each numbered marker is that engine's application point -- the "
        "combined engine and propeller CG -- which is where every component in "
        "the table above acts.",
        f"The two arrows in the corner are the positive senses of this view's "
        f"axes, {x_label} and {y_label}, both in {length_units}. A moment is "
        "positive right-handed about its axis, so a positive torque about a "
        "thrust line is clockwise to somebody looking along it -- which is what "
        "the pilot does, and why the engine's own torque is signed that way.",
    ]
    if assumed_any:
        caption.append(
            "A thrust line marked ASSUMED is not entered geometry: its "
            "direction is the airplane's forward axis and its length is drawn, "
            "not stated. Enter the propeller CG to replace it.")
    caption.append("Nothing here is a load: no value is scaled and none carries "
                   "a safety factor.")
    return Figure(
        key=key, title=title,
        data=PlotData(f"{x_label} ({length_units})",
                      f"{y_label} ({length_units})", series,
                      points=points, points_label="Application points"),
        caption=" ".join(caption))


def _projected(frame: str, point: Sequence[float],
               scale: float) -> Tuple[float, float]:
    """An airplane ``(x, y, z)`` point as the entered pair this frame plots."""
    x, y, z = (float(v) * scale for v in point)
    if frame == "water":
        return x, z
    if frame == "front":
        return y, z
    return x, y


# --- the section ------------------------------------------------------------- #
def _engine_mount(project: Project, results: Mapping[str, Optional[ModuleResult]],
                  *, system: UnitSystem, plan: Sequence[SectionPlan]) -> Section:
    """Section 10 -- Engine Mount Loads, in its two subsections (note 44 §20)."""
    records = _engine_records(project, results)
    if not records:
        return Section("", absent_reason=(
            "the engine mount loads were not produced for this project: no "
            "engine is entered, or the powers and torques the conditions are "
            "computed from are missing."))
    figures = [
        _engine_view_figure(project, records, frame=frame, key=key, title=title,
                            view=view, system=system)
        for frame, key, title, view in _ENGINE_VIEWS
    ]
    inputs = _engine_inputs(records, system=system, plan=plan)
    return Section("", body=[
        "This section states the engine mount loads: what they were computed "
        "from, where they act, and all six components of each at its point of "
        "application. Every case is LIMIT with its safety factor stated and "
        "applied nowhere.",
    ], subsections=[
        replace(inputs, title="Input data", figures=figures),
        replace(_engine_cases_section(records, system=system),
                title="Critical cases"),
    ])


# --------------------------------------------------------------------------- #
# Dispatch
# --------------------------------------------------------------------------- #
#: Step key -> the builder that produces its section body.
#:
#: A step with no entry renders as its plan state, which is how a not-yet-built
#: section stays a stated placeholder rather than an empty heading.
#:
#: The builders share one signature so that this stays a table of callables
#: rather than four shapes and a dispatch that knows which is which. ``plan`` is
#: unused by three of them today -- hence the ARG001 waivers -- because only a
#: builder that cross-references another section needs it, and section 2.4 is
#: the first that does.
BUILDERS = {
    "configuration_layout": _geometry,
    "weight_mass": _weights,
    "structural_speeds": _speeds,
    "flight_envelope": _envelope,
    "wing_loads": _wing_loads,
    "fuselage_loads": _fuselage_loads,
    # *Split* section keys, not step keys (OR-129).
    "htail_loads": _htail_loads,
    "vtail_loads": _vtail_loads,
    # Sections 7-9: a pressure over a surface Section 2 already draws, and no
    # appendix of their own (note 44 §19, OR-147).
    "aileron_loads": _aileron_loads,
    "flap_loads": _flap_loads,
    "tab_loads": _tab_loads,
    # Section 10: six components at one point, and no appendix either -- an
    # engine mount takes a point load, not a distribution (note 44 §20).
    "engine_mount": _engine_mount,
}

#: Appendix title -> the builder that produces its body.
#:
#: Separate from :data:`BUILDERS` because an appendix is not a step: it is keyed
#: by the slot it occupies, and a reserved slot has no builder at all -- which is
#: what makes "reserved" renderable rather than a special case in the loop.
APPENDIX_BUILDERS = {
    WING_LOAD_STATIONS: _station_appendix,
    BODY_LOAD_STATIONS: _body_station_appendix,
    HTAIL_LOAD_STATIONS: _htail_station_appendix,
    VTAIL_LOAD_STATIONS: _vtail_station_appendix,
}


def build_section(project: Project, entry: SectionPlan,
                  results: Mapping[str, Optional[ModuleResult]], *,
                  system: UnitSystem,
                  plan: Sequence[SectionPlan]) -> Section:
    """One analysis section, headed and either built or stated as absent.

    A section that is not included carries its state's lead and reason and no
    content -- the states are :mod:`.oracle_content`'s to decide, and this
    module only renders what it was told.
    """
    from .oracle_content import heading

    title = heading(entry.number, entry.title)
    builder = BUILDERS.get(entry.step_key)
    if not entry.included or builder is None:
        return Section(title,
                       absent_reason=entry.reason,
                       absent_lead=entry.lead or "Not analysed")
    section = builder(project, results, system=system, plan=plan)
    if section.absent_reason and not section.body and not section.tables:
        # A builder can only discover an absence the plan could not: the plan
        # tests that a step's *slices* are populated, and a module can still
        # decline to produce a result from populated ones. It renders as the
        # ABSENT state, through that state's own lead, so a builder cannot word
        # absence a second way (found while building Section 10; the same hole
        # was under every builder that returns one).
        from .oracle_content import STATE_TEXT, SectionState

        return Section(title, absent_reason=section.absent_reason,
                       absent_lead=STATE_TEXT[SectionState.ABSENT][0])
    return Section(title, body=section.body, tables=section.tables,
                   figures=section.figures,
                   subsections=_numbered(entry.number, section.subsections))


def _numbered(parent: str, subsections: Sequence[Section]) -> List[Section]:
    """A builder's own subsections, numbered under ``parent``.

    A step that renders as subsections (section 3) titles them and does not
    number them, exactly as a *group* of steps does not number its members --
    :func:`sloads.report.oracle_content.subsection_number` is the one owner of
    the child form, and a builder that wrote "3.1" into a title would be a
    second numbering scheme that cannot renumber itself when a section is
    inserted above it.
    """
    from .oracle_content import heading, subsection_number

    return [replace(child, title=heading(subsection_number(parent, index),
                                         child.title))
            for index, child in enumerate(subsections)]


def build_appendix(project: Project, entry: SectionPlan,
                   results: Mapping[str, Optional[ModuleResult]], *,  # noqa: ARG001
                   system: UnitSystem,
                   plan: Sequence[SectionPlan]) -> Section:
    """One appendix, lettered and either built or stated as reserved (OR-50).

    The same shape as :func:`build_section` and deliberately not folded into it:
    an appendix is lettered rather than numbered, and its state comes from the
    slot and its step rather than from a plan row of its own.
    """
    from .oracle_content import appendix_heading, appendix_letter

    title = appendix_heading(entry.title)
    builder = APPENDIX_BUILDERS.get(entry.title)
    if not entry.included or builder is None:
        return Section(title, absent_reason=entry.reason,
                       absent_lead=entry.lead or "Not analysed",
                       page_break=True)
    section = builder(project, system=system, plan=plan)
    return Section(title, body=section.body, tables=section.tables,
                   figures=section.figures,
                   # An appendix' children are lettered from their parent by the
                   # same owner a section's are numbered from theirs, so "B.1"
                   # cannot be written down anywhere but here.
                   subsections=_numbered(appendix_letter(entry.title),
                                         section.subsections),
                   absent_reason=section.absent_reason,
                   absent_lead=section.absent_lead,
                   page_break=section.page_break,
                   landscape=section.landscape)


__all__ = [
    "APPENDIX_BUILDERS",
    "BUILDERS",
    "build_appendix",
    "build_section",
]
