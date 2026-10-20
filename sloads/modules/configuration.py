"""General configuration & layout (modern addition -- no original ``.BAS``).

This module is the geometric **source of truth** for an initial concept: from the
parametric ``LayoutInput`` slice it derives the wing planform, the mean
aerodynamic chord and its leading-edge station, a tail-volume neutral-point /
static-margin estimate, and the landing-gear tip-back / overturn angles and prop
ground clearance. It then *seeds* the downstream pages (WINGGEOM polylines,
WTENV/STRSPEED ``XLEMAC``/``MAC``).

There is **no manual regression oracle** for this page; the Appendix A/B geometry
is used only as a *sanity* fixture (the derived MAC/XLEMAC must match what
WINGGEOM reproduces -- see ``tests/test_configuration.py``). To honour the rule
that a module must not recompute a quantity another module owns, the MAC /
XLEMAC / aspect ratio / span are obtained by generating the WINGGEOM edge
polylines and running them through WINGGEOM's planform integration
(:func:`sloads.modules.wing_geometry.surface_properties`), not by an
independent integration.

Method references (Reference 1, McMaster):
- trapezoidal MAC / Y_MAC closed form, Ch 5 (cross-checked against WINGGEOM);
- tail-volume neutral point / static margin, Ch 8 (tail-volume coefficient
  ``V_H = S_t·l_t / (S_w·MAC)``; ``h_n = h_acw + V_H·(a_t/a_w)·(1 - dε/dα)``);
- tip-back / overturn (turnover) angles, standard landing-gear geometry
  (Roskam/Raymer first-cut; no FAR23 oracle).

All estimates use first-order method assumptions (documented constants below) and
are surfaced as *estimates* in the UI -- in concept mode they are flagged as
unverified extrapolation, consistent with the Phase-C validation contract.
"""

from __future__ import annotations

import contextlib
import math
from typing import Dict, List, Optional, Tuple

from ..constants import GEAR_OVERTURN_MAX_DEG, GEAR_OVERTURN_NEVER_DEG, GEAR_TIPBACK_MIN_DEG, IN2_PER_FT2
from ..derived_geometry import MacReference, pct_mac_to_station, require_integrable_planform
from ..models import (
    ConditionResult,
    EmpennageInput,
    LandingGearGeometry,
    LayoutInput,
    LoadValue,
    MassCase,
    MissingInputError,
    ModuleResult,
    Project,
    SurfaceInput,
    TailType,
    Vec3,
)
from ..picks import extreme
from ..registry import register
from ..tail_geometry import (
    SurfacePlane,
    h_tail_waterline,
    surface_plane,
    vtail_root,
    vtail_root_waterline,
)
from ..units import format_value
from .wing_geometry import interp_x, surface_properties

_FAR = "configuration"  # modern addition; no FAR condition / no .BAS oracle
_IN = "in"
_DEG = "deg"

# Method assumptions for the tail-volume neutral-point estimate (Ref 1 Ch 8).
# First-order defaults: wing aerodynamic centre at 25% MAC, tail/wing lift-curve
# slope ratio ~1, and a typical downwash factor (1 - dε/dα) ~ 0.6. Documented and
# centralized here so a refinement is a one-line change.
_H_AC_WING = 0.25          # wing aerodynamic centre, fraction of MAC
_LIFT_SLOPE_RATIO = 1.0    # a_t / a_w
_DOWNWASH_FACTOR = 0.6     # (1 - dε/dα)

#: The planform ``_wing_geometry`` integrates: the stored ``wing`` surface.
_WING = "wing"


# V-tail panels have no dedicated dihedral field (Step: tail-type usability pass);
# a fixed typical value keeps the sketch simple. Documented so a refinement is a
# one-line change, same convention as the neutral-point assumptions above.
_V_TAIL_DIHEDRAL_DEG = 40.0


def _hinge_fraction(aft_hinge_sqft: float, area_sqft: float) -> float:
    """Elevator/rudder chord fraction (hinge line to TE) from the native areas.

    ``Saft/S`` is the control-surface area aft of the hinge as a fraction of the
    surface area -- for a full-span control the chordwise fraction the movable
    surface occupies (Step G6: the three-view draws the surface from the same
    analysis-native areas, not a separate hingeline input). Clamped to a sensible
    sketch band."""
    if area_sqft <= 0 or aft_hinge_sqft <= 0:
        return 0.0
    return max(0.05, min(0.9, aft_hinge_sqft / area_sqft))


def tail_planform(layout: LayoutInput,
                  empennage: Optional["EmpennageInput"] = None,
                  project: Optional[Project] = None) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
    """Tail-surface sketch polylines for the three-view, keyed by panel name.

    Each panel maps to ``{"top": [(x, y), ...], "side": [(x, z), ...], "front":
    [(y, z), ...]}`` -- ready-to-plot polylines/outlines in the three-view's Top
    (X, Y) / Side (X, Z) / Front (Y, Z) axes. A first-order rectangular-planform
    sketch (constant chord = area / span; the empennage carries no tail taper or
    sweep), not a structural surface definition.

    Step G6: the tail geometry is read from the single-source ``empennage``
    (``htail``/``vtail`` = the analysis-native :class:`TailLoadsInput`/
    :class:`VTailLoadsInput`) -- area ``ST``/``SV``, span (``2*htail_semispan_in`` /
    ``vtail_span_in``) and the 25%-tail-MAC station (``xt25``/``xv25``) place each
    surface, and the elevator/rudder are drawn as the aft ``Saft/S`` chord band
    (``elevator``/``rudder`` panels) so the movable surfaces come from the same data
    the loads use. Returns ``{}`` when no empennage/tail geometry is present.

    The vertical-tail root comes from ``tail_geometry``'s single owner -- with
    ``project`` given, the full resolution order including the fuselage-outline
    datum ``z_centre(x_vtail) + height(x_vtail)/2`` (backlog Pri 1); layout-only,
    the ``root_waterline_z + fuselage_height / 2`` fallback. ``layout.h_tail_z``
    is a further user offset; if left at ``0`` for ``T_TAIL``/``CRUCIFORM`` a
    sensible default (top of fin / mid-fin) is used instead of the fuselage
    centreline.
    """
    ht = empennage.htail if empennage is not None else None
    vt = empennage.vtail if empennage is not None else None
    if project is not None:
        # The resolved records (note 36 OV-1; design note 69 D-69.17): a blank
        # hinge half derives from the control's boundary lines, and the band
        # this sketch shades is the aft share SELECT loads.
        from .select import effective_tail_inputs, effective_vtail_inputs
        with contextlib.suppress(ValueError):    # the ARW refusal is SELECT's to make
            ht = effective_tail_inputs(project) or ht
        vt = effective_vtail_inputs(project) or vt
    h_area = ht.htail_area_sqft if ht is not None else 0.0
    h_span_in = 2.0 * ht.htail_semispan_in if ht is not None else 0.0
    v_area = vt.vtail_area_sqft if vt is not None else 0.0
    v_span_in = vt.vtail_span_in if vt is not None else 0.0
    if h_span_in <= 0 and v_span_in <= 0:
        return {}

    # One owner for where the fin's root sits (plan 13 L-1): the sketch and the
    # load deck read the same function, so they cannot place one fin twice. With
    # the project in hand the project-level resolver supplies the fuselage
    # outline datum too (backlog Pri 1); layout-only callers get the same
    # resolution order minus the outline branch.
    if project is not None:
        vtail_root_z = vtail_root(project).z
    else:
        vtail_root_z = vtail_root_waterline(
            layout, v_span_in, vt.vtail_root_waterline_z if vt is not None else 0.0).z
    panels: Dict[str, Dict[str, List[Tuple[float, float]]]] = {}

    if layout.tail_type == TailType.V_TAIL:
        if vt is not None and v_area > 0 and v_span_in > 0:  # v_area > 0 already implies vt
            area_in2 = (v_area * IN2_PER_FT2) / 2.0  # per panel
            chord = area_in2 / v_span_in
            x_mac = vt.xv25
            x_le, x_te = x_mac - 0.25 * chord, x_mac + 0.75 * chord
            dihedral = math.radians(_V_TAIL_DIHEDRAL_DEG)
            proj_y = v_span_in * math.cos(dihedral)
            proj_z = v_span_in * math.sin(dihedral)
            for sgn, side in ((1, "right"), (-1, "left")):
                panels[f"v_tail_{side}"] = {
                    "top": [(x_le, 0.0), (x_te, 0.0), (x_te, sgn * proj_y),
                            (x_le, sgn * proj_y), (x_le, 0.0)],
                    "side": [(x_le, vtail_root_z), (x_te, vtail_root_z),
                             (x_te, vtail_root_z + proj_z), (x_le, vtail_root_z + proj_z),
                             (x_le, vtail_root_z)],
                    "front": [(0.0, vtail_root_z), (sgn * proj_y, vtail_root_z + proj_z)],
                }
        return panels

    if vt is not None and v_area > 0 and v_span_in > 0:  # v_area > 0 already implies vt
        area_in2 = v_area * IN2_PER_FT2
        chord = area_in2 / v_span_in
        x_mac = vt.xv25
        x_le, x_te = x_mac - 0.25 * chord, x_mac + 0.75 * chord
        z1 = vtail_root_z + v_span_in
        panels["v_tail"] = {
            "top": [(x_le, 0.0), (x_te, 0.0)],
            "side": [(x_le, vtail_root_z), (x_te, vtail_root_z), (x_te, z1),
                     (x_le, z1), (x_le, vtail_root_z)],
            "front": [(0.0, vtail_root_z), (0.0, z1)],
        }
        # Rudder: aft Saft/S chord band over the fin height (Side view).
        r_frac = _hinge_fraction(vt.rudder_aft_hinge_sqft, v_area)
        if r_frac > 0:
            x_hinge = x_te - r_frac * chord
            panels["rudder"] = {
                "top": [(x_hinge, 0.0), (x_te, 0.0)],
                "side": [(x_hinge, vtail_root_z), (x_te, vtail_root_z), (x_te, z1),
                         (x_hinge, z1), (x_hinge, vtail_root_z)],
                "front": [(0.0, vtail_root_z), (0.0, z1)],
            }

    if ht is not None and h_area > 0 and h_span_in > 0:  # h_area > 0 already implies ht
        area_in2 = h_area * IN2_PER_FT2
        chord = area_in2 / h_span_in
        x_mac = ht.xt25
        x_le, x_te = x_mac - 0.25 * chord, x_mac + 0.75 * chord
        h_half = h_span_in / 2.0

        # One owner for where the h-tail sits (#236, completed D-54.4): with
        # the project in hand the sketch reads ``h_tail_waterline`` -- the
        # same resolution the load path places stations and GRIDs with, so the
        # drawing cannot disagree with the deck (rule 2; on ``cessna_210`` the
        # sketch's own entered-else-wing-root logic sat 14 in below the
        # mass-item placement the owner now resolves). Layout-only callers
        # keep the local first-order branches, like the fin's root above.
        if project is not None:
            h_z = h_tail_waterline(project).z
        else:
            h_tail_z = layout.h_tail_z
            if h_tail_z == 0.0 and layout.tail_type == TailType.T_TAIL:
                h_z = vtail_root_z + v_span_in
            elif h_tail_z == 0.0 and layout.tail_type == TailType.CRUCIFORM:
                h_z = vtail_root_z + v_span_in * 0.5
            else:
                h_z = layout.root_waterline_z + h_tail_z

        panels["h_tail"] = {
            "top": [(x_le, h_half), (x_te, h_half), (x_te, -h_half),
                    (x_le, -h_half), (x_le, h_half)],
            "side": [(x_le, h_z), (x_te, h_z)],
            "front": [(-h_half, h_z), (h_half, h_z)],
        }
        # Elevator: aft Saft/S chord band over the full h-tail span (Top view).
        e_frac = _hinge_fraction(ht.elevator_aft_hinge_sqft, h_area)
        if e_frac > 0:
            x_hinge = x_te - e_frac * chord
            panels["elevator"] = {
                "top": [(x_hinge, h_half), (x_te, h_half), (x_te, -h_half),
                        (x_hinge, -h_half), (x_hinge, h_half)],
                "side": [(x_hinge, h_z), (x_te, h_z)],
                "front": [(-h_half, h_z), (h_half, h_z)],
            }

    return panels


def lra_overlays(
    surfaces: List[SurfaceInput],
) -> List[Dict[str, object]]:
    """Loads-reference-axis polylines for the three-view, one per surface.

    Each entry is ``{"name", "ref_axis", "view", "x", "y"}``: the LRA
    (``SurfaceInput.ref_axis`` fraction of local chord, the beam-model elastic
    axis) sampled at every polyline span station, ready to plot. ``view`` names
    the three-view panel the polyline belongs in -- ``"top"`` (X vs butt line)
    for butt-line-span surfaces, ``"side"`` (X vs waterline) for waterline-span
    ones, which the Top view therefore cannot show (found at the 0.8.2
    pre-release walk: the fin's LRA drew in the x-y plane, off past the
    wingtip). Which is which is :func:`sloads.tail_geometry.surface_plane`'s
    to say (D-54.2/#220), and the frame also decides mirroring: a symmetric
    butt-line surface is mirrored about the centreline; a waterline-span
    surface never is, whatever its ``symmetric`` flag says.
    """
    out: List[Dict[str, object]] = []
    for s in surfaces:
        # The strip-sweep precondition owner (#71, PB-21): interp_x divides by
        # the butt-line difference of the segment it lands on. A half-entered
        # planform is skipped -- the sketch must not crash mid-entry -- and
        # every shipped fixture surface passes (checked 2026-09-08).
        try:
            require_integrable_planform(s)
        # refusal: a half-entered planform has no LRA to draw yet
        except ValueError:
            continue
        spans = sorted({p[1] for p in s.leading_edge} | {p[1] for p in s.trailing_edge})
        xa = [
            interp_x(s.leading_edge, sp)
            + s.ref_axis * (interp_x(s.trailing_edge, sp) - interp_x(s.leading_edge, sp))
            for sp in spans
        ]
        vertical = surface_plane(s.name) is SurfacePlane.WATERLINE
        if s.symmetric and not vertical:
            xs = xa[::-1] + xa
            ys = [-sp for sp in spans[::-1]] + spans
        else:
            xs, ys = list(xa), list(spans)
        out.append({
            "name": s.name,
            "ref_axis": s.ref_axis,
            "view": "side" if vertical else "top",
            "x": xs,
            "y": ys,
        })
    return out


def _wing_geometry(project: Project) -> dict:
    """The stored wing's MAC/XLEMAC/Y_MAC/AR/span/area, by WINGGEOM's label.

    Design note 69 D-69.2: the planform this module reports is the one the
    analysis integrates -- the ``wing`` entry of ``geometry.surfaces``, read
    through :func:`wing_geometry.surface_properties` so WINGGEOM stays the
    single owner of the integration. Until v77 it integrated a two-point
    trapezoid regenerated from five parametric scalars, which on ``ga6_normal``
    put XLEMAC 7 in off the planform the loads were computed on. The root and
    tip chords are the polylines' own, at their innermost and outermost butt
    lines. A project with no ``wing`` surface is not ready, by name.
    """
    geometry = project.geometry
    surf = geometry.by_name(_WING) if geometry is not None else None
    if surf is None:
        raise MissingInputError(
            f"Project has no '{_WING}' surface in geometry.surfaces: the "
            "configuration module integrates the stored planform (design note 69 D-69.2)")
    result = surface_properties(surf)
    geom = {v.label: v.value for v in result.values}
    y_root = max(surf.leading_edge[0][1], surf.trailing_edge[0][1])
    y_tip = min(surf.leading_edge[-1][1], surf.trailing_edge[-1][1])
    geom["Root chord"] = interp_x(surf.trailing_edge, y_root) - interp_x(surf.leading_edge, y_root)
    geom["Tip chord"] = interp_x(surf.trailing_edge, y_tip) - interp_x(surf.leading_edge, y_tip)
    return geom


def _wing_area_sqft(geom: dict) -> float:
    """The planform's total (both-sides) area in ft², from WINGGEOM's in²."""
    return geom["Total area"] / IN2_PER_FT2


# --------------------------------------------------------------------------- #
# Component stations -- Weight DB seeding (Step D4.3)
# --------------------------------------------------------------------------- #
# Alias substrings (lowercased) that identify a Weight-DB item as belonging to a
# derived component, most-specific first so "Horizontal tail" matches "h_tail"
# rather than the lumped "tail" catch-all (WTESTIMA's single "Tail" structure-group
# item, which has no h/v breakdown -- see estimate_to_mass_items).
_COMPONENT_ALIASES: Dict[str, Tuple[str, ...]] = {
    "h_tail": ("horizontal tail", "h-tail", "h_tail", "htail"),
    "v_tail": ("vertical tail", "v-tail", "v_tail", "vtail"),
    "main_gear": ("main gear", "main_gear"),
    "nose_gear": ("nose gear", "nose_gear"),
    "landing_gear": ("landing gear", "gear"),
    "wing": ("wing",),
    "fuselage": ("fuselage",),
    "tail": ("tail",),
}
_COMPONENT_MATCH_ORDER: Tuple[str, ...] = (
    "h_tail", "v_tail", "main_gear", "nose_gear", "landing_gear", "wing", "fuselage", "tail",
)


def gear_stations(layout: LayoutInput, landing_gear: Optional[LandingGearGeometry]) -> Optional[dict]:
    """Coarse gear geometry derived from the single-source LANDLOAD axle geometry
    (Step G6b), or ``None`` when no gear geometry is present.

    Returns ``{main_x, nose_x, track, gear_height, ground_z}`` (inches). The main/nose
    stations are the **static-axle X**; ``track`` is the tread; the ground line is the
    lowest static wheel contact (static axle ``Z`` minus rolling radius), and
    ``gear_height`` = root waterline − ground (replacing the retired coarse
    ``LayoutInput.gear_height`` — the native axle geometry is authoritative).
    """
    if landing_gear is None:
        return None
    mg, ng = landing_gear.main_gear, landing_gear.nose_gear
    main_x, nose_x = mg.axle_static[0], ng.axle_static[0]
    if main_x <= 0 and nose_x <= 0:
        return None
    wheels = []
    if main_x > 0:
        wheels.append(mg.axle_static[1] - mg.rolling_radius_in)
    if nose_x > 0:
        wheels.append(ng.axle_static[1] - ng.rolling_radius_in)
    ground_z = min(wheels) if wheels else layout.root_waterline_z
    return {"main_x": main_x, "nose_x": nose_x, "track": landing_gear.tread_in,
            "gear_height": layout.root_waterline_z - ground_z, "ground_z": ground_z}


def component_stations(project: Project) -> Dict[str, Vec3]:
    """Approximate ``(x, y, z)`` station (fuselage station / butt line / waterline,
    inches) for each named airframe component, derived from the entered geometry
    -- a rough first-cut for seeding the Weight DB (WTONECG), not a
    new schema field (Step D4.3; no per-component station sub-model was added --
    see the D-5 decision in ``docs/25_notes/05_phase_d_gui_workflow_plan.md``). A seeded
    ``MassItem.x/y/z`` is always overridable by hand afterward.

    Keys present depend on what is entered: ``"wing"`` (25% MAC of the stored
    ``wing`` planform, matching the CG first-cut used elsewhere in this module),
    ``"fuselage"`` (the outline's length midpoint, design note 69 D-69.3),
    ``"h_tail"``/``"v_tail"`` (the 25%-tail-MAC station ``xt25``/``xv25`` from the
    Step-G6 single-source ``empennage``), ``"tail"`` (area-weighted h/v average, for
    a single lumped "Tail" item), ``"main_gear"``/``"nose_gear"`` (gear station,
    strut mid-height) and ``"landing_gear"`` (weight-weighted ~3:1 main:nose
    average). All at butt line ``y=0`` (centreline).
    """
    from ..derived_geometry import fuselage_summary

    geometry = project.geometry
    layout = (geometry.parametric if geometry is not None else None) or LayoutInput()
    empennage = geometry.empennage if geometry is not None else None
    landing_gear = geometry.landing_gear if geometry is not None else None
    ht = empennage.htail if empennage is not None else None
    vt = empennage.vtail if empennage is not None else None
    stations: Dict[str, Vec3] = {}
    try:
        geom = _wing_geometry(project)
    # refusal: no integrable wing, no wing station -- the seed leaves the item alone
    except (MissingInputError, ValueError, ZeroDivisionError):
        geom = None
    if geom is not None:
        wing_x = geom["XLE(MAC) station of MAC LE"] + 0.25 * geom["MAC"]
        stations["wing"] = (wing_x, 0.0, layout.root_waterline_z)
    summary = fuselage_summary(geometry.fuselage if geometry is not None else None)
    if summary is not None and summary[0] > 0:
        stations["fuselage"] = (
            layout.datum_x + summary[0] / 2.0, 0.0, layout.root_waterline_z,
        )
    if ht is not None and ht.xt25 > 0:
        stations["h_tail"] = (ht.xt25, 0.0, layout.root_waterline_z)
    if vt is not None and vt.xv25 > 0:
        stations["v_tail"] = (vt.xv25, 0.0, layout.root_waterline_z)
    tail_pts: List[Tuple[float, Tuple[float, float, float]]] = []
    if "h_tail" in stations:
        tail_pts.append((ht.htail_area_sqft if ht is not None else 0.0, stations["h_tail"]))
    if "v_tail" in stations:
        tail_pts.append((vt.vtail_area_sqft if vt is not None else 0.0, stations["v_tail"]))
    if tail_pts:
        total_area = math.fsum(a for a, _ in tail_pts) or float(len(tail_pts))
        tail_x = math.fsum((a or 1.0) * pt[0] for a, pt in tail_pts) / total_area
        stations["tail"] = (tail_x, 0.0, layout.root_waterline_z)
    gc = gear_stations(layout, landing_gear)
    if gc is not None and gc["gear_height"] > 0:
        gear_z = layout.root_waterline_z - gc["gear_height"] / 2.0
        if gc["main_x"] > 0:
            stations["main_gear"] = (gc["main_x"], 0.0, gear_z)
        if gc["nose_x"] > 0:
            stations["nose_gear"] = (gc["nose_x"], 0.0, gear_z)
    gear_pts: List[Tuple[float, Tuple[float, float, float]]] = []
    if "main_gear" in stations:
        gear_pts.append((3.0, stations["main_gear"]))
    if "nose_gear" in stations:
        gear_pts.append((1.0, stations["nose_gear"]))
    if gear_pts:
        total_w = math.fsum(w for w, _ in gear_pts)
        gx = math.fsum(w * pt[0] for w, pt in gear_pts) / total_w
        gz = math.fsum(w * pt[2] for w, pt in gear_pts) / total_w
        stations["landing_gear"] = (gx, 0.0, gz)
    return stations


def match_component_station(name: str, stations: Dict[str, Vec3]) -> Optional[Vec3]:
    """Match a ``MassItem.name`` to a :func:`component_stations` entry by
    substring alias (case-insensitive), most-specific key first. Returns
    ``None`` when no alias matches (the item is left untouched by the seed
    button)."""
    lname = name.lower()
    for key in _COMPONENT_MATCH_ORDER:
        if key not in stations:
            continue
        if any(alias in lname for alias in _COMPONENT_ALIASES[key]):
            return stations[key]
    return None


def _planform_condition(geom: dict) -> ConditionResult:
    return ConditionResult(
        title="Wing planform (WINGGEOM)",
        far_reference=_FAR,
        values=[
            LoadValue("Reference area S", _wing_area_sqft(geom), "ft^2", key="wing_area_s"),
            LoadValue("Span", geom["Span"], _IN, key="span"),
            LoadValue("Root chord", geom["Root chord"], _IN, key="root_chord"),
            LoadValue("Tip chord", geom["Tip chord"], _IN, key="tip_chord"),
            LoadValue("MAC", geom["MAC"], _IN, key="mac"),
            LoadValue("XLE(MAC) station of MAC LE", geom["XLE(MAC) station of MAC LE"], _IN,
                key="xle_mac_station_of_mac_le"),
            LoadValue("YLE(MAC) butt line of MAC", geom["YLE(MAC) butt line of MAC"], _IN,
                key="yle_mac_butt_line_of_mac"),
            LoadValue("Aspect ratio", geom["Aspect ratio"], key="aspect_ratio"),
        ],
        note=("S/MAC/XLEMAC/AR via WINGGEOM's planform integration of the stored "
              "wing surface (design note 69 D-69.2); the chords are the polylines' "
              "own at the root and tip butt lines."),
    )


def _stability_condition(project: Project, geom: dict) -> Optional[ConditionResult]:
    """Tail-volume neutral point + static margin (Ref 1 Ch 8 first-cut).

    Reads the h-tail area and 25%-MAC station from the Step-G6 single-source
    ``geometry.empennage.htail``; the tail arm is derived as ``xt25`` minus the 25%
    wing-MAC station (``XLEMAC + 0.25*MAC``), so it is not stored twice. The wing
    area and MAC frame are the stored planform's (D-69.2), as ``MacReference``
    below has always claimed.
    """
    emp = project.geometry.empennage if project.geometry is not None else None
    ht = emp.htail if emp is not None else None
    mac = geom["MAC"]
    xlemac = geom["XLE(MAC) station of MAC LE"]
    wing_area_sqft = _wing_area_sqft(geom)
    if ht is None or ht.htail_area_sqft <= 0 or wing_area_sqft <= 0 or mac <= 0:
        return None
    # The MAC frame is one relation (#80): the 25%-MAC station and the neutral
    # point below are both a percentage of MAC off XLEMAC, and both read the
    # *planform* reference -- these are aerodynamic quantities, so the weight
    # envelope's XLEMAC/MAC override deliberately does not reach them.
    mac_ref = MacReference(xlemac, mac, "planform", "wing")
    h_arm = ht.xt25 - pct_mac_to_station(25.0, mac_ref)
    if h_arm <= 0:
        return None
    v_h = (ht.htail_area_sqft * h_arm) / (wing_area_sqft * mac)
    h_n = _H_AC_WING + v_h * _LIFT_SLOPE_RATIO * _DOWNWASH_FACTOR
    np_station = pct_mac_to_station(h_n * 100.0, mac_ref)

    values = [
        LoadValue("Horizontal tail volume V_H", v_h, key="horizontal_tail_volume_v_h"),
        LoadValue("Neutral point (%MAC)", h_n * 100.0, "%MAC", key="neutral_point_pct_mac"),
        LoadValue("Neutral point station", np_station, _IN, key="neutral_point_station"),
    ]
    note = (
        "Tail-volume estimate (h_acw=0.25, a_t/a_w=1.0, 1-dε/dα=0.6); "
        "first-order, no oracle."
    )

    # Static margin needs a CG; use the aft-gross %MAC limit from WTENV when present
    # (the critical aft CG). Reported as an estimate; left out if no CG is known.
    env = project.weight.envelope if project.weight is not None else None
    if env is not None and env.aft_gross_pct_mac:
        h_cg = env.aft_gross_pct_mac / 100.0
        values.append(LoadValue("CG (%MAC, aft-gross limit)", env.aft_gross_pct_mac, "%MAC",
            key="cg_pct_mac_aft_gross_limit"))
        values.append(LoadValue("Static margin (%MAC)", (h_n - h_cg) * 100.0, "%MAC", key="static_margin_pct_mac"))
    else:
        note += " Static margin needs a CG (WTENV aft-gross %MAC) -- not in project."

    return ConditionResult(title="Longitudinal stability (estimate)", far_reference=_FAR,
                           values=values, note=note)


def cg_estimate(project: Project, layout: LayoutInput,
                mac: float, xlemac: float) -> Tuple[float, float, str]:
    """The best available CG station/waterline, and a short label for its source.

    True CG (Step D4.5, re-ruled by design note 70 D-70.4): when ``Project.mass``
    is populated, the **mass-basis FLIGHT loading's** row -- the heaviest
    FLIGHT case, aft-most on a tie (:func:`weight_onecg.basis_row`), the same
    pick ONENGOUT sizes at -- labelled by its case name; a slice holding only
    the ceiling row answers with the ceiling, labelled as such, because a CG
    the airplane cannot fly at is still better than a planform guess when it
    is *named*. Falls back to the 25 %-MAC / wing-reference-waterline first cut
    (the only option before a mass slice exists) -- geometric estimates, not
    certified figures. Callers surface the returned source label so the UI and
    report make clear which one is in play.

    Takes ``mac``/``xlemac`` as plain numbers rather than the geometry dict it
    used to index by label (M4-9).
    """
    from .weight_onecg import basis_row

    row = basis_row(project.mass, project)
    if row is not None:
        return row.cg_x, row.cg_z, _cg_label(row)
    return (pct_mac_to_station(25.0, MacReference(xlemac, mac, "planform", "wing")),
            layout.root_waterline_z, "25% MAC estimate")


def _cg_label(row: MassCase) -> str:
    return "Weight DB, database ceiling" if row.ceiling else f"Weight DB, {row.name}"


def _gear_angles(gc: dict, x_cg: float, z_cg: float) -> Tuple[float, Optional[float]]:
    """Tip-back and overturn angles (deg) for one CG, from the gear geometry.

    Tip-back: the angle of the main-wheel -> CG line from the vertical; CG
    forward of the main gear (positive) is required, ``GEAR_TIPBACK_MIN_DEG``
    the usual minimum. Overturn (lateral tip-over, Roskam's psi): from the CG
    to the nose-wheel -> main-wheel ground line, ``atan(h_cg / d)`` with ``d``
    the CG's perpendicular distance to that line in plan (Roskam Pt IV
    Fig. 2.48a p. 76; Torenbeek Sec. 10.3.2 pp. 352-353); lower is more stable,
    ``GEAR_OVERTURN_MAX_DEG`` the hard-surface guideline. ``None`` when the
    nose gear or track is absent.
    """
    h_cg = z_cg - gc["ground_z"]            # CG height above ground
    tipback = math.degrees(math.atan2(gc["main_x"] - x_cg, h_cg))
    if not (gc["nose_x"] and gc["track"]):
        return tipback, None
    xn, xm, half = gc["nose_x"], gc["main_x"], gc["track"] / 2.0
    # Perpendicular distance (plan view) from the CG (on the centreline) to the
    # nose-wheel -> main-wheel line.
    dx, dy = xm - xn, half - 0.0
    seg = math.hypot(dx, dy)
    d = abs(dx * (0.0 - 0.0) - dy * (x_cg - xn)) / seg  # |cross| / |seg|
    return tipback, math.degrees(math.atan2(h_cg, d))


def gear_guideline_note() -> str:
    """The design guidelines the gear angles are read against, with their
    sources (issue #362). Guidelines, not requirements: the owner of the two
    numbers is ``constants`` and this sentence is the only place they are stated."""
    return (f" Guidelines, not requirements: tip-back >= {format_value(GEAR_TIPBACK_MIN_DEG, 'deg')} deg "
            "(Roskam Pt II p. 218, Fig. 9.1a p. 219; Pt IV Fig. 2.48a p. 76; Raymer 4th ed. "
            f"Sec. 11.2 p. 265), overturn <= {format_value(GEAR_OVERTURN_MAX_DEG, 'deg')} deg on a hard surface "
            "(Roskam Pt IV Fig. 2.48a p. 76, Pt II Fig. 9.1a p. 219; Torenbeek Sec. 10.3.2 "
            "pp. 352-353: 55-57 deg a maximum safe limit, never over "
            f"{format_value(GEAR_OVERTURN_NEVER_DEG, 'deg')} deg). "
            "Exceeding one raises operational risk (tail strike, sideways turnover); it does "
            "not fail the design.")


def _gear_condition(project: Project, layout: LayoutInput, geom: dict) -> Optional[ConditionResult]:
    """Tip-back / overturn angles + prop clearance from the gear geometry.

    **Per CG case (design note 70 D-70.4, C3).** When ``Project.mass`` holds
    the per-case rows, every row that is a loading gets its own tip-back and
    overturn value, labelled by case, and the two headline values name the
    **governing** case: the minimum tip-back (the aft-most CG) and the maximum
    overturn. Until note 70 both were drawn at the all-items CG -- on
    ``atr42_100`` a 43,308 lb loading that cannot fly. Without the rows the
    headline pair is drawn at :func:`cg_estimate`'s fallback and says so. Prop
    clearance does not depend on the CG and is stated once.
    """
    gc = gear_stations(layout, project.geometry.landing_gear if project.geometry is not None else None)
    if gc is None or gc["main_x"] <= 0 or gc["gear_height"] <= 0:
        return None
    x_cg, z_cg, cg_source = cg_estimate(
        project, layout, geom["MAC"], geom["XLE(MAC) station of MAC LE"])
    ground_z = gc["ground_z"]

    values: List[LoadValue] = []
    rows = [c for c in (project.mass.cases if project.mass is not None else []) if not c.ceiling]
    if rows:
        per_case = [(c, *_gear_angles(gc, c.cg_x, c.cg_z)) for c in rows]
        tip_case, tip_min, _ = extreme(per_case, lambda r: r[1], largest=False)
        values.append(LoadValue(f"CG station ({cg_source})", x_cg, _IN, key="cg_station"))
        values.append(LoadValue(f"Tip-back angle, governing ({tip_case.name})", tip_min, _DEG,
                                key="tip_back_angle"))
        with_over = [(c, tb, ov) for c, tb, ov in per_case if ov is not None]
        if with_over:
            over_case, _, over_max = extreme(with_over, lambda r: r[2])
            values.append(LoadValue(f"Overturn (turnover) angle, governing ({over_case.name})",
                                    over_max, _DEG, key="overturn_turnover_angle"))
        for i, (c, tb, ov) in enumerate(per_case, start=1):
            values.append(LoadValue(f"CG station -- {c.name}", c.cg_x, _IN, key=f"cg_station_case_{i}"))
            values.append(LoadValue(f"Tip-back angle -- {c.name}", tb, _DEG, key=f"tip_back_angle_case_{i}"))
            if ov is not None:
                values.append(LoadValue(f"Overturn (turnover) angle -- {c.name}", ov, _DEG,
                                        key=f"overturn_turnover_angle_case_{i}"))
    else:
        tipback, overturn = _gear_angles(gc, x_cg, z_cg)
        values.append(LoadValue(f"CG station ({cg_source})", x_cg, _IN, key="cg_station"))
        values.append(LoadValue("Tip-back angle", tipback, _DEG, key="tip_back_angle"))
        if overturn is not None:
            values.append(LoadValue("Overturn (turnover) angle", overturn, _DEG, key="overturn_turnover_angle"))

    # Prop ground clearance: nose engine prop tip vs ground (needs engine + prop).
    from .engine import effective_engine
    eng = project.engine
    eng = effective_engine(project, eng) if eng is not None else None
    if eng is not None and eng.prop_diameter_in:
        prop_tip_z = eng.prop_cg[2] - eng.prop_diameter_in / 2.0
        values.append(LoadValue("Prop ground clearance", prop_tip_z - ground_z, _IN, key="prop_ground_clearance"))

    if rows:
        note = (f"Angles per CG case from the Weight DB's loadings of record ({len(rows)} cases); "
                "the governing values name their case: minimum tip-back, maximum overturn. "
                f"The CG station row is the {cg_source}.")
    else:
        note = (f"CG from the {cg_source}"
                + ("." if cg_source.startswith("Weight DB") else " (no mass slice present).")
                + " No per-case rows in the mass slice.")
    note += gear_guideline_note()
    return ConditionResult(
        title="Landing-gear geometry (estimate)", far_reference=_FAR, values=values, note=note,
    )


def configuration_properties(project: Project) -> List[ConditionResult]:
    """All configuration/layout derived quantities for a :class:`Project`."""
    layout = project.geometry.parametric if project.geometry is not None else None
    if layout is None:
        raise MissingInputError("Project has no 'geometry.parametric' slice for the configuration module")
    geom = _wing_geometry(project)
    results = [_planform_condition(geom)]
    for cond in (_stability_condition(project, geom),
                 _gear_condition(project, layout, geom)):
        if cond is not None:
            results.append(cond)
    if project.is_concept:
        results[0].note += " Concept mode: results are unverified extrapolation."
    return results


# --------------------------------------------------------------------------- #
# Project entry point + registration
# --------------------------------------------------------------------------- #
MODULE_NAME = "configuration"


def run(project: Project) -> ModuleResult:
    """Run the configuration/layout derivation against a :class:`Project`."""
    return ModuleResult(module=MODULE_NAME, conditions=configuration_properties(project))


register(MODULE_NAME, run)
