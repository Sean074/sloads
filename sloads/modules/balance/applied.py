"""The applied sets -- every load an assembled case carries before closure.

Part of :mod:`sloads.modules.balance` (#191); the subsystem docstring is the
package's, and the seam rule it states is what decides membership here: a load a
free-body cut introduces is never applied. Wing air and inertia, the body's
inertia and axial force, the entered hub thrust and the two tail distributions,
plus :func:`_free_moments`, which recovers the section pitching moment AIRLOADS
reports cumulatively.
"""

from __future__ import annotations

import math
from dataclasses import replace
from math import cos, pi, radians, sin
from typing import List, Sequence, Tuple

from ...constants import POLAR_TRUSTED_ALPHA_DEG, dynamic_pressure_psf
from ...derived_geometry import body_drag_waterline, require_wing_reference, wing_plane
from ...export.coordinates import (
    reflect_force,
    reflect_moment,
    reflect_point,
    reflect_side,
    tail_force_to_airplane,
    tail_station_to_airplane,
    tail_torsion_to_airplane,
)
from ...mass_distribution import (
    CaseLoading,
    assembly_distributes_mass,
    component_of,
    half_span,
    panel_weight,
    reacted_parts,
    wing_parts,
)
from ...models import (
    AeroInput,
    BalancedLoad,
    CgCase,
    FlightLoadsInput,
    GeometryInput,
    MissingInputError,
    Project,
    TailSpanResult,
    VnPoint,
    WingCarriage,
    WingLoadResult,
    WingMassInput,
)
from ...tail_geometry import HTAIL, VTAIL
from ..airloads import air_load_distribution
from ..wing_inertia import inertia_units, resolve_wing_cases
from .constants import HANDEDNESS_TOL


def _free_moments(result: WingLoadResult) -> List[float]:
    """Per-strip **free** pitching moment (the section ``Cm`` term alone).

    ``AIRLOADS`` accumulates ``myy = tyy + tvyy + trq``: the sweep transfer of
    outboard shear (``tyy``), the dihedral transfer of outboard drag (``tvyy``)
    and the section pitching moment (``trq``). Only the last is a free moment;
    the other two are position transfers that an assembly applies for itself.
    Both are reconstructed here from the station table by the same recurrence
    ``airloads`` builds them with, and subtracted back out.

    On ``ga6_normal`` PHAA the root torsion is -79,003 lb-in, of which -60,474 is
    sweep transfer and -9,594 dihedral -- so the free moment is -8,935, and using
    the -79,003 figure as if it were free is the 20 % error.
    """
    s = result.stations
    h = len(s)
    tyy = [0.0] * h
    tvyy = [0.0] * h
    for i in range(h - 2, -1, -1):
        tyy[i] = tyy[i + 1] - s[i + 1].sz * (s[i + 1].x - s[i].x)
        tvyy[i] = tvyy[i + 1] + s[i + 1].sx * (s[i + 1].z - s[i].z)
    trq = [s[i].myy - tyy[i] - tvyy[i] for i in range(h)]
    return [trq[i] - (trq[i + 1] if i + 1 < h else 0.0) for i in range(h)]


def reflect_load(load: BalancedLoad) -> BalancedLoad:
    """One load's mirror image through the centreline plane (decision B-6).

    Every component goes through the single owner in
    :mod:`sloads.export.coordinates`, including the ones that are zero today, so
    the sign convention lives in exactly one place and the lateral families of
    B8a inherit it already checked.
    """
    x, y, z = reflect_point(load.x, load.y, load.z)
    fx, fy, fz = reflect_force(load.fx, load.fy, load.fz)
    mx, my, mz = reflect_moment(load.mx, load.my, load.mz)
    if load.source in _ROTATION_FIXED_SOURCES:
        # A propeller's torque and gyroscopic couples keep their sense: the
        # mirrored airplane's propeller turns the same way (note 21 §4.4,
        # design note 66 D-66.7). Its position mirrors; its couple does not.
        mx, my, mz = load.mx, load.my, load.mz
    return replace(load, x=x, y=y, z=z, fx=fx, fy=fy, fz=fz,
                   mx=mx, my=my, mz=mz, side=reflect_side(load.side))


#: The couples :func:`reflect_load` does not mirror -- the owner is
#: ``engine_cases.ROTATION_FIXED_SOURCES``; restated here only because that
#: module imports this one (a guard test holds the two equal).
_ROTATION_FIXED_SOURCES = ("engine-torque", "engine-gyro")


def _mirror(loads: Sequence[BalancedLoad]) -> List[BalancedLoad]:
    """The port-side image of a starboard set.

    The *geometric* half of building a full-span airplane out of a half-span
    calculation -- distinct from :func:`reflect_load`'s use in
    :func:`handed_twin`, which mirrors a whole assembled case to get its
    opposite-hand twin. Same operator either way, which is the point of giving it
    one owner.
    """
    return [reflect_load(ld) for ld in loads]


def _wing_slices(project: Project) -> Tuple[WingMassInput, GeometryInput, AeroInput]:
    """The three slices every wing set reads, present -- or the module's refusal.

    :func:`run` checks ``wing_mass`` at entry; the helpers below are also called
    directly (ground cases, tests), so the same refusal lives here once instead
    of an ``AttributeError`` at the first dereference.
    """
    wm, geometry, aero = project.wing_mass, project.geometry, project.aero
    if wm is None or geometry is None or aero is None:
        raise MissingInputError("balance needs 'wing_mass', 'geometry' and 'aero'")
    return wm, geometry, aero


def _flight_loads(project: Project) -> FlightLoadsInput:
    fl = project.flight_loads
    if fl is None:
        raise MissingInputError("balance needs 'flight_loads'")
    return fl


def wing_sets(project: Project, vn: VnPoint,
              sources=None) -> Tuple[List[BalancedLoad], float, float]:
    """Starboard wing air + inertia loads, at ``vn``'s own flight condition.

    Returns ``(loads, wing_item_weight, cm_free_total)`` where ``cm_free_total``
    is the section-``Cm`` free moment of **both** wings -- the caller needs it to
    work out the fuselage's share of the trim moment.

    ``sources`` is the caller's already-resolved
    :class:`~sloads.modules.wing_inertia.WingCaseSources`; without it the case
    list re-resolves the V-n matrix and SELECT's set, once per call.
    """
    wm, geometry, aero_in = _wing_slices(project)
    geom = geometry.by_name(wm.surface)
    aero = aero_in.by_name(wm.surface)
    base = next((c for c in resolve_wing_cases(project, wm, sources)), None)
    if geom is None or aero is None or base is None:
        raise MissingInputError("balance needs a wing surface, aero set and load case")

    air = air_load_distribution(geom, aero, vn.cl, vn.v_eas_kt,
                                *wing_plane(project, wm.surface))
    ml = _free_moments(air)
    loads = [
        BalancedLoad(x=s.x, y=s.y, z=s.z, fx=s.fx, fz=s.fz, my=ml[i],
                     source="wing-air", side="R")
        for i, s in enumerate(air.stations)
    ]
    cm_free = 2.0 * math.fsum(ml)

    inertia, panel_both = wing_inertia_strips(project, vn.nz)
    return loads + inertia, panel_both, cm_free


def wing_inertia_strips(project: Project,
                        nz: float) -> Tuple[List[BalancedLoad], float]:
    """Starboard wing inertia strips at load factor ``nz``, plus the panel mass.

    Returns ``(strips, panel_weight_both_sides)``, **centred on their own
    centroid** -- :func:`place_wing_inertia` is what moves them onto the loading's
    WING items and scales them to it. The two halves are separate because the
    ground families need the same shape at ``nz = 0`` (their load factor is
    solved, not given: decision G-6), and a second copy of this construction
    beside them is the drift ``CLAUDE.md`` practice 3 forbids.

    Inertia strips take WINGINER's **spanwise shape** at the 50 % chord (where it
    models the panel mass CG -- its torsion carries ``-w*(c50x - c25x)`` for
    exactly that reason).

    The split of authority is decision B-2: the item database owns *where* the
    mass is, WINGINER owns *how it is spread along the span*. Without the shift
    the two disagree -- ga6's wing item sits at x 97.87 while the 50 % chord line
    runs 78-95 -- and the difference lands in the pitching residual as a moment
    the trim does not have, because the trim lumps all mass at the CG. It is
    worth 2.8-4.3 % of ``n*W*MAC`` on ``concept_regional_jet``.

    A strip carries ``weight_lb`` whatever ``nz`` is, which is what lets a ground
    case work: at ``nz = 0`` the strips apply no force and the closure field
    accelerates them, so the wing's mass is in the model exactly once either way.

    The shape is WINGINER's at the **project** panel weight
    (:func:`~sloads.mass_distribution.panel_weight`, note 63): the strips carry
    the panel's own shape only, and :func:`place_wing_inertia` scales them to the
    loading's ``PANEL`` parts and adds its ``POINT`` parts at their own stations.
    """
    wm, geometry, _ = _wing_slices(project)
    geom = geometry.by_name(wm.surface)
    if geom is None:
        raise MissingInputError(f"balance: wing surface {wm.surface!r} is not in 'geometry'")
    u = inertia_units(geom, wm, *wing_plane(project, wm.surface),
                      panel_weight_lb=panel_weight(project))
    panel = math.fsum(u.w)
    strips = [(i, w) for i, w in enumerate(u.w) if w]
    if strips and panel:
        x_shape = math.fsum(w * u.c50x[i] for i, w in strips) / panel
        z_shape = math.fsum(w * u.z[i] for i, w in strips) / panel
    else:
        x_shape = z_shape = 0.0
    return ([BalancedLoad(x=u.c50x[i] - x_shape, y=u.ye[i], z=u.z[i] - z_shape,
                          fz=-w * nz, weight_lb=w, source="wing-inertia", side="R")
             for i, w in strips], 2.0 * panel)


def place_wing_inertia(loads: Sequence[BalancedLoad], loading: CaseLoading,
                       project: Project, panel_both: float,
                       nz: float = 0.0) -> Tuple[List[BalancedLoad], List[str]]:
    """Scale ``loads``' wing inertia onto the loading's WING items and place it.

    The other half of :func:`wing_inertia_strips`: WINGINER supplies the spanwise
    shape, the item database supplies the mass and where its centroid sits
    (decision B-2), and this is where the two are married. Returns the loads with
    every ``wing-inertia`` strip scaled and shifted, plus the notes the scale owes
    the reader -- a scale that is not 1.0 means the two mass models disagree, and
    the case says by how much rather than absorbing it.

    **Carriage (design note 63, D-63.3).** The strips are scaled to the loading's
    ``PANEL`` parts and shifted onto *their* centroid; the loading's ``POINT``
    parts are appended as their own ``wing-inertia`` loads at their own
    ``x``/``y``/``z`` -- the :func:`~sloads.mass_distribution.half_span`
    starboard half, since the caller mirrors the set (a centreline POINT part
    at half its weight, mirroring to the whole).
    ``nz`` scales the point forces exactly as the strips were scaled (0 for a
    ground case, whose closure field accelerates the mass instead). On a
    loading with no POINT part this is bit-for-bit the pre-v67 placement.
    """
    notes: List[str] = []
    scale = _wing_inertia_scale(loading, project, panel_both)
    if scale == 0.0:
        notes.append("the loading carries no WING-tagged PANEL item mass -- "
                     "no distributed wing inertia")
    elif abs(scale - 1.0) > 1e-6:
        notes.append(
            f"wing inertia scaled x{scale:.4f} onto the loading's WING PANEL items "
            f"({scale * panel_both:.0f} lb); WINGINER's integrated panel mass is "
            f"{panel_both:.0f} lb")
    panel_items = wing_parts(loading.items, project, WingCarriage.PANEL)
    w_wing = math.fsum(it.weight_lb for it in panel_items)
    x_wing = (math.fsum(it.weight_lb * it.x for it in panel_items) / w_wing) if w_wing else 0.0
    z_wing = (math.fsum(it.weight_lb * it.z for it in panel_items) / w_wing) if w_wing else 0.0
    placed = [replace(ld, fz=ld.fz * scale, weight_lb=ld.weight_lb * scale,
                      x=ld.x + x_wing, z=ld.z + z_wing)
              if ld.source == "wing-inertia" else ld
              for ld in loads]
    # The starboard half through the one projection (#301): the caller mirrors it.
    points = [BalancedLoad(x=it.x, y=it.y, z=it.z, fz=-it.weight_lb * nz,
                           weight_lb=it.weight_lb, source="wing-inertia", side="R")
              for it in half_span(loading.items, project).points]
    if points:
        notes.append(
            f"{len(points)} wing POINT mass(es) applied at their own stations, "
            f"{2.0 * math.fsum(p.weight_lb for p in points):,.0f} lb both sides "
            "(design note 63 D-63.3)")
    return placed + points, notes


def _wing_inertia_scale(loading: CaseLoading, project: Project,
                        panel_both_sides: float) -> float:
    """Factor bringing WINGINER's panel mass onto the loading's WING PANEL weight.

    Decision B-2: the items are the mass SSOT, and WINGINER supplies the *shape*.
    Where the two models already agree the factor is exactly 1.0 (``ga6_normal``
    330 = 2 x 165); where they do not it is what stops the disagreement becoming
    a load. Since note 63 the scale reads the loading's ``PANEL`` parts alone
    -- its ``POINT`` parts are placed, not spread -- so on a project with no
    override the factor is the loading's share of the database's panel rows.

    **The partition gate (review F-C5).** WING-tagged items are excluded from
    :func:`body_inertia` precisely because the wing set carries them, so a wing
    set scaled to zero would delete their whole weight from the model and let
    the closure absorb it silently. When the loading has WING PANEL items and
    WINGINER integrates no panel at all there is no spanwise shape to put them
    on, and that is an inconsistent input rather than a load case: it raises.
    Only a loading with **no** PANEL item mass scales to 0.0, and then nothing is
    lost -- :func:`assemble` notes that case.
    """
    wing_items = math.fsum(it.weight_lb for it in
                           wing_parts(loading.items, project, WingCarriage.PANEL))
    if panel_both_sides <= 0.0:
        if wing_items:
            raise MissingInputError(
                f"the loading carries {wing_items:.0f} lb of WING-tagged PANEL items "
                "but the wing mass model integrates no panel mass "
                "(wing_mass.panel_weight_override_lb = 0): there is no spanwise "
                "shape to distribute them over. Clear the override to derive the "
                "panel from the items, or retag them POINT or onto a component "
                "the fuselage beam carries")
        return 0.0
    return wing_items / panel_both_sides


def body_inertia(loading: CaseLoading, project: Project,
                 nz: float) -> List[BalancedLoad]:
    """Inertia of everything the wing does not carry, at each item's own station.

    The wing enters the fuselage as the carry-through *reaction*, which the
    assembled model's solver recovers -- so no ``carry`` load appears here, and
    none may (plan 11 §4).

    "What the wing does not carry" is asked through
    :func:`~sloads.mass_distribution.assembly_distributes_mass`, the same
    predicate :func:`point_mass_self_inertia` uses, so the set of items carried
    as points and the set contributing a self-inertia free moment cannot drift
    apart (decision L-3).
    """
    return [
        BalancedLoad(x=it.x, y=it.y, z=it.z, fz=-it.weight_lb * nz,
                     weight_lb=it.weight_lb, source="body-inertia", side="C")
        for it in reacted_parts(loading.items, project)
        if not assembly_distributes_mass(component_of(it, project))
    ]


def body_axial_set(loads: Sequence[BalancedLoad], project: Project,
                   vn: VnPoint, loading: CaseLoading,
                   ) -> Tuple[float, float, bool, List[BalancedLoad], List[str]]:
    """The airplane's **non-wing** drag: ``(applied, dCD, clamped, loads, notes)``.

    Design note: ``docs/25_notes/24_body_drag_carrier_note.md``.

    The FLTLOADS trim balances the airplane-less-tail drag from the **polar**
    (``aero_curves.drag_cd``, the ``CD(CL)`` polynomial the project enters);
    the assembled model's only ``fx`` is the wing strips' own chordwise force
    (``airloads``: section profile drag plus the lifting-line induced drag,
    resolved with lift through the case ``alpha``). The difference is the
    fuselage, the nacelles and every other non-wing parasite contribution, and
    before this it was simply absent -- ``residual_fx`` *equalled* the wing
    strips' sum, and the couple the missing force left about the CG was the
    whole of the pre-closure pitch residual.

    That it is genuinely parasite drag, and not a bookkeeping artefact, is
    measurable: both the trim and the strips resolve through the same ``alpha``,
    so the body-axis gap splits exactly into wind-axis parts,

        dD = dFx*cos(a) + dFz*sin(a)        dL = dFz*cos(a) - dFx*sin(a)

    and ``dL/L`` comes out <= 0.6 % everywhere while ``dD/(q*S)`` is a near
    constant **-0.018 across all seven** ``ga6_normal`` cases -- a ``CD`` offset
    independent of ``CL``, which is what a missing parasite term looks like and
    what a lift-model disagreement does not.

    ``dCD`` is returned as that **wind-axis** increment rather than the axial one
    (the two differ by the negligible ``dL*sin(a)`` tilt), because the physical
    content of the diagnostic is the drag-coefficient offset.

    **Sign.** ``CONVENTIONS.md`` §1: ``x`` is +aft, so both ``vn.dx`` and the
    strips' ``fx`` are already body-axis ``x`` forces and the correction is a
    subtraction in one frame, needing no rotation. Positive is aft, i.e. drag.

    **A forward value is a defect in one of the two drag models, not a load**
    (D-4 as revised 2026-08-17, backlog Pri 2). Where it appears is what
    decides the treatment, and the deciding quantity is the trim's ``alpha``
    against the polar's trusted window :data:`~sloads.constants.POLAR_TRUSTED_ALPHA_DEG`
    (:func:`polar_alpha_trusted`):

    * **outside the window** the polar is being read where it was never fitted
      -- above it the strip model's induced drag overshoots
      (``concept_regional_jet``, +20/+22 deg), below it the fit is 13 deg under
      zero lift (``NMAA`` on the three crudest-polar fixtures) -- so a forward
      difference is **not applied**: no ``body-axial`` card, ``body_axial`` = 0,
      ``body_axial_clamped`` set, and the raw value in the note. ``dCD`` is
      still computed and reported from the unclamped difference, so the G10
      diagnostic keeps its signal; ``residual_fx`` re-opens by exactly the
      clamped amount on those cases and only those, and the G1/G5 gates read
      the same flag. Revision 1 of D-4 refused to clamp because that would
      "reopen ``residual_fx`` and hide the overshoot"; it hid neither once the
      window is stated and ``dCD`` stays reported, and it put a forward
      "drag" of 1.0-1.4 klb on three ``NMAA`` decks (backlog Pri 2).
    * **inside the window** both models are trusted, so a forward value cannot
      be excused: it is applied as computed **and** noted, and
      ``tests/test_balance.py``'s G10 gate fails on it -- the fixture's aero
      data is wrong, not the assembly.

    **Placement.** The waterline is the single owner
    :func:`~sloads.derived_geometry.body_drag_waterline` and is the only free
    parameter here (decision D-1). The fuselage station reaches no gate -- a pure
    axial force contributes ``my = (z-zcg)*fx`` with no ``x`` term -- so it is
    spread over the body outline by cross-section-area share where one exists,
    and lumped at the body masses' own centroid where it does not. Both are
    stated; neither can move a number.
    """
    wr = require_wing_reference(project)
    wing_fx = math.fsum(ld.fx for ld in loads if ld.source == "wing-air")
    wing_fz = math.fsum(ld.fz for ld in loads if ld.source == "wing-air")
    total = vn.dx - wing_fx
    if not total:
        return 0.0, 0.0, False, [], []

    # The wind-axis drag increment, for the G10 consistency diagnostic.
    a = radians(vn.alpha_deg)
    q_psf = dynamic_pressure_psf(vn.v_eas_kt)
    qs = q_psf * wr.s_sqft
    delta_cd = ((-total) * cos(a)
                + (wing_fz - vn.lzw) * sin(a)) / qs if qs else 0.0

    wl = body_drag_waterline(project)
    notes: List[str] = []
    if wl.note:
        notes.append(wl.note)
    if total < 0.0:
        lo, hi = POLAR_TRUSTED_ALPHA_DEG
        if not polar_alpha_trusted(vn.alpha_deg):
            side = "above" if vn.alpha_deg > hi else "below"
            notes.append(
                f"the non-wing axial force comes out FORWARD ({total:+,.0f} lb; "
                f"dCD = {delta_cd:+.5f}) at alpha {vn.alpha_deg:+.1f} deg, "
                f"{side} the polar's trusted window ({lo:+.0f}, {hi:+.0f}) deg, "
                f"where the airplane-less-tail polar and the strip model are "
                f"not both trusted: NOT applied (dCD reported unclamped; "
                f"residual_fx re-opens by this amount) -- design note 20 D-4 "
                f"as revised 2026-08-17")
            return 0.0, delta_cd, True, [], notes
        notes.append(
            f"the non-wing axial force is FORWARD ({total:+,.0f} lb; dCD = "
            f"{delta_cd:+.5f}) INSIDE the polar's trusted window "
            f"({lo:+.0f}, {hi:+.0f}) deg -- the fixture's aero data is "
            f"inconsistent where both drag models are trusted; applied as "
            f"computed and flagged (D-4)")

    stations = _body_drag_stations(project, loading)
    if not stations:
        return total, delta_cd, False, [], [
            *notes, "the non-wing drag has no body station to act at and is NOT applied"]
    notes.append(
        f"non-wing drag {total:+,.0f} lb applied at waterline {wl.z:.1f} "
        f"({wl.basis}) over {len(stations)} body station(s); dCD = {delta_cd:+.5f}")
    return total, delta_cd, False, [
        BalancedLoad(x=x, y=0.0, z=wl.z, fx=total * frac,
                     source="body-axial", side="C")
        for x, frac in stations
    ], notes


def polar_alpha_trusted(alpha_deg: float) -> bool:
    """Is the trim ``alpha`` inside the polar's trusted window?

    The one predicate on :data:`~sloads.constants.POLAR_TRUSTED_ALPHA_DEG`,
    read by :func:`body_axial_set` and by the G10 gate in ``tests/test_balance.py``
    so the code and the test cannot disagree about where a forward non-wing
    force is a defect (inside) and where it is an untrusted difference that
    is not applied (outside).
    """
    lo, hi = POLAR_TRUSTED_ALPHA_DEG
    return lo <= alpha_deg <= hi


def _body_drag_stations(project: Project,
                        loading: CaseLoading) -> List[Tuple[float, float]]:
    """``[(x, fraction)]`` the body-axial load is spread over; sums to 1.0.

    Cross-section-area share over the fuselage outline where there is one -- each
    interior station taking half of each adjoining trapezoidal segment, so the
    ends are not over-weighted -- else a single station at the body masses' own
    centroid. Neither choice can move a gate (see :func:`body_axial_set`); the
    outline branch exists so the deck's axial load path is physical where the
    geometry supports one.
    """
    outline = project.geometry.fuselage if project.geometry is not None else None
    sections = list(outline.sections) if outline is not None else []
    if len(sections) >= 2:
        area = [pi / 4.0 * s.width * s.height for s in sections]
        w = [0.0] * len(sections)
        for i in range(len(sections) - 1):
            seg = 0.5 * (area[i] + area[i + 1]) * (sections[i + 1].x - sections[i].x)
            w[i] += 0.5 * seg
            w[i + 1] += 0.5 * seg
        total = math.fsum(w)
        if total > 0.0:
            return [(s.x, wi / total) for s, wi in zip(sections, w) if wi]
    body = [it for it in reacted_parts(loading.items, project)
            if not assembly_distributes_mass(component_of(it, project))]
    weight = math.fsum(it.weight_lb for it in body)
    if weight:
        return [(math.fsum(it.x * it.weight_lb for it in body) / weight, 1.0)]
    return []


#: The ``source`` tag of the per-engine hub thrust force (backlog #10). One
#: reader -- :func:`is_powered` -- so the deck header, the case table, the report
#: and the gates all agree on what a *powered* case is, the same single-owner
#: rule :func:`is_ground` follows for the gear and :func:`is_lateral` for the fin.
HUB_THRUST_SOURCE = "engine-thrust"


def hub_thrust_set(project: Project, cg: CgCase
                   ) -> Tuple[List[BalancedLoad], List[str]]:
    """The user-entered engine thrust: one hub force per engine, ``(loads, notes)``.

    Carved out of design note 21 (``docs/25_notes/21_power_effects_wing_note.md``),
    whose seven-step wake plan stays parked. What ships here is the one piece
    that needs no estimator: the user enters ``EngineInput.thrust_lb`` and it
    becomes a ``FORCE`` at that engine's hub -- the node the LRA skeleton has
    carried since R-9 and has never had a load on
    (:mod:`sloads.export.lra_model`).

    **Sign and station.** ``CONVENTIONS.md`` §1: ``x`` is +aft, so thrust is
    ``fx = -T``. It acts at ``prop_cg`` -- ``XPROP/YPROP/ZPROP``, the hub -- and
    falls back to ``engine_cg`` only when no hub is entered; thrust with neither
    raises rather than being placed on a guess, the refusal rule the LRA
    exporter already follows for its missing datums.

    **The thrust line is axial.** The P-6 incidence/toe angles (``i_T``, ``tau``)
    have no fields and no estimator, and inventing them would put a lateral and
    a vertical component into every case on an assumed geometry. So this is a
    pure ``-x`` force, said in-band, and note 21 keeps the rest.

    **Nothing balances it, and that is the point.** The V-n trim this case is
    assembled at is thrust-free -- ``fltloads`` balances the airplane's drag from
    the polar and knows nothing about power -- so the applied thrust is a genuine
    unbalance in two degrees of freedom: ``Fx`` in full, and its couple
    ``-T*(z_hub - z_cg)`` in pitch. Both are reacted by the closure, which is
    exactly where they belong:

        ``n_x = (D - sum T) / W``

    -- the suite's ``x`` being +aft, so a thrust that exactly cancels the drag
    gives ``n_x = 0`` and thrust in excess of it gives a forward (negative)
    ``n_x``. That is FAR 23's longitudinal load factor, and the carrier this module's
    docstring records the suite as lacking (**"the suite has no distributed
    thrust"**, :func:`_closure`). ``q_dot`` reacts the couple. A powered case is
    therefore *not* in longitudinal or pitch trim by construction, and
    :data:`RESIDUAL_GATE` does not apply to its ``My`` -- the same standing as
    the 23.427(a) maneuver tail load and the lateral families' ``Fy``/``Mz``.
    The gate that does apply is the six-DOF closure itself, and the closed form
    :func:`hub_thrust` states: a constructed case whose thrust equals its drag
    closes at ``n_x = 0``.

    **Flight only.** A ground case gets no thrust: rating it per family is note
    21's parked ``power_policy`` table, and a landing case has no thrust rating
    here to give. :func:`assemble_ground` says so in-band rather than dropping
    the input in silence.

    ``thrust_lb`` of ``None`` or ``0`` applies nothing at all, which is every
    shipped fixture: today's cases are exactly zero-thrust and stay bit-for-bit
    identical (``test_hub_thrust.py`` G-1).
    """
    loads: List[BalancedLoad] = []
    applied: List[str] = []
    from ..engine import resolved_engines
    for i, eng in enumerate(resolved_engines(project) if project.engines else []):
        thrust = eng.thrust_lb
        if not thrust:
            continue
        hub = tuple(eng.prop_cg) if any(eng.prop_cg) else tuple(eng.engine_cg)
        if not any(hub):
            raise MissingInputError(
                f"engine {i + 1} enters thrust_lb = {thrust:,.0f} lb but has "
                "neither a hub (prop_cg) nor an engine_cg to apply it at -- a "
                "thrust force needs a station, and this suite does not guess one")
        x, y, z = hub
        loads.append(BalancedLoad(x=x, y=y, z=z, fx=-thrust,
                                  source=HUB_THRUST_SOURCE,
                                  side="R" if y > 0 else "L" if y < 0 else "C"))
        applied.append(f"engine {i + 1} {thrust:+,.0f} lb at "
                       f"({x:,.1f}, {y:,.1f}, {z:,.1f})")
    if not loads:
        return [], []

    total = math.fsum(-ld.fx for ld in loads)
    couple = math.fsum((ld.z - cg.zcg) * ld.fx for ld in loads)
    # An asymmetric installation (different thrust per engine, or one engine of
    # a pair) yaws the airplane -- and :func:`is_handed` cannot see it, because
    # it measures lateral force and rolling moment and a pure axial force at
    # ``y != 0`` makes neither. Rather than change that frozen predicate for
    # this step, the yaw is measured and stated: the case is emitted UNHANDED,
    # the closure's ``r_dot`` carries the moment in full, and the note names
    # both consequences -- no twin from the asymmetry, and a twin got from
    # anywhere else mirrors the installation with everything else (note 21
    # section 4.4's parked decision) -- so neither is discovered from a number.
    yaw = math.fsum(-ld.y * ld.fx for ld in loads)
    arm = max(abs(ld.y) for ld in loads)
    notes = []
    if abs(yaw) > HANDEDNESS_TOL * max(abs(total) * arm, 1.0):
        notes.append(
            f"the entered thrust is ASYMMETRIC: it yaws the airplane "
            f"{yaw:+,.0f} lb-in about the CG, carried in full by the closure's "
            f"yaw acceleration. Two consequences are stated rather than "
            f"handled, both owned by design note 21 section 4.4 (reflection "
            f"with engine loads): the asymmetry mints NO port twin of its own "
            f"-- is_handed measures lateral force and rolling moment (decision "
            f"L-6) and an axial force off the centreline makes neither -- and "
            f"where the case has a hand from something else, the twin operator "
            f"mirrors the installation with everything else, so that twin is "
            f"the mirror-image airplane's case, not this one's. Enter the "
            f"mirror installation as its own project if that is the case "
            f"wanted")
    return loads, [
        f"engine thrust APPLIED at the hub: {'; '.join(applied)} -- "
        f"{total:+,.0f} lb forward in total (fx = {-total:+,.0f} lb; "
        f"CONVENTIONS.md section 1, x is +aft), taken axial (the thrust-line "
        f"incidence and toe angles stay parked with design note 21). The V-n "
        f"trim this case is assembled at is thrust-free, so NOTHING balances "
        f"it: the pre-closure Fx and its couple about the CG "
        f"({couple:+,.0f} lb-in) are carried in full by the closure's "
        f"longitudinal and pitch degrees of freedom -- nx = (D - sum T)/W is "
        f"the carrier the assembled model has always lacked -- and the 1 % "
        f"residual gate does not apply to a powered case's My, the same "
        f"standing as the 23.427(a) maneuver tail load"] + notes


def vtail_sets(result: TailSpanResult) -> List[BalancedLoad]:
    """The fin's distributed side load, in airplane axes (decision L-6, plan 13 §2).

    A pure consumer of :mod:`sloads.modules.tail_span`, which is itself a pure
    consumer of SELECT -- so the load a lateral balanced case carries is the
    Appendix-A-locked side load, strip for strip, and no oracle is at risk from
    assembling it. What this function adds is the **frame change**, and it makes
    it through the single owner in :mod:`sloads.export.coordinates` rather than
    by hand:

    * the fin's span is ``z``, so a station at span ``s`` sits at
      ``z = root_waterline + s`` -- the waterline B8a-1 gave it, without which
      the roll moment ``-Fy*(z - z_cg)`` comes out with the wrong **sign** on
      ``ga6_normal`` (plan 13 §3.3);
    * the fin's normal force is a **side** force, ``fy``, not ``fz``;
    * the fin's torsion is about its span axis, so it is ``mz``, and it is the
      **negated** stored value -- the derivation is in
      :func:`~sloads.export.coordinates.tail_torsion_to_airplane`.

    The set is air only, and deliberately: fin **inertia** rides in the closure
    field at the case's own ``n_y``/``omega_dot``, through the ``VTAIL``-tagged
    mass items :func:`body_inertia` already carries (decision L-8).

    Which is why the strip's air load is taken as ``fz - f_inertia`` rather than
    as ``fz``. Since the tail-mass SSOT step the per-condition fin deck carries
    its own lateral inertia, and reading the net here would apply the fin's mass
    **twice** in an assembled case -- once relieving the applied side load, once
    in the closure field. The seam is the same one the wing's carry-through has,
    and it is held the same way: each mass enters exactly one set.
    """
    loads: List[BalancedLoad] = []
    for st in result.stations:
        x, y, z = tail_station_to_airplane(st.x, st.y, VTAIL, root_z=st.z)
        fx, fy, fz = tail_force_to_airplane(st.fz - st.f_inertia, VTAIL)
        mx, my, mz = tail_torsion_to_airplane(st.myy_free, VTAIL)
        loads.append(BalancedLoad(x=x, y=y, z=z, fx=fx, fy=fy, fz=fz,
                                  mx=mx, my=my, mz=mz,
                                  source="vtail-air", side="C"))
    return loads


def htail_sets(result: TailSpanResult) -> List[BalancedLoad]:
    """The horizontal tail's distributed load, in airplane axes (D-R8, F-R5).

    :func:`vtail_sets`' sibling, and deliberately built the same way: a pure
    consumer of :mod:`sloads.modules.tail_span`, which is a pure consumer of
    SELECT, so the 23.427(a) load an assembled case carries is SELECT's own
    RH/LH split strip for strip and no oracle is at risk from assembling it.

    The frame change goes through the single owner in
    :mod:`sloads.export.coordinates`, with ``component=HTAIL``: the h-tail's span
    is ``y``, so a station sits at its own span coordinate on both halves of the
    full-span table (plan 09 decision T-8); its normal force is vertical, so it
    is ``fz``; and its torsion is about the ``y`` axis, so it is a free ``my``,
    the stored value unchanged. The strips carry the tail's waterline in ``z``,
    which is where they are, not the trim load's reference plane.

    **Air only**, exactly as the fin set is: the surface's mass items stay in
    :func:`body_inertia` and are accelerated by the closure field, so the tail's
    weight enters the case once. Reading the strips' net ``fz`` instead would
    apply it twice, once as the per-condition deck's own d'Alembert term and once
    in the relief.

    The ``side`` tag is the half of the airplane the strip is on -- which is what
    ``side`` has always meant, the wing being the only carrier of it until now --
    so :func:`reflect_load` swaps the two halves when the port twin is minted.
    """
    loads: List[BalancedLoad] = []
    for st in result.stations:
        x, y, z = tail_station_to_airplane(st.x, st.y, HTAIL, root_z=st.z)
        fx, fy, fz = tail_force_to_airplane(st.fz - st.f_inertia, HTAIL)
        mx, my, mz = tail_torsion_to_airplane(st.myy_free, HTAIL)
        loads.append(BalancedLoad(x=x, y=y, z=z, fx=fx, fy=fy, fz=fz,
                                  mx=mx, my=my, mz=mz,
                                  source="htail-air", side="R" if y > 0 else "L"))
    return loads
