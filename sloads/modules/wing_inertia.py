"""Wing inertia loads along the 25% chord, from WINGINER.BAS.

WINGINER computes the spanwise inertia load, shear, bending moment and torsion of
the wing (FAR 23.301(b): the air loads must be balanced by the inertia forces of
each item of mass). The outboard wing-panel mass is modelled as an area density
that tapers linearly from root to tip; the root density is iterated until the
integrated panel mass equals the entered panel weight (WINGINER.BAS lines
690-880). Concentrated wing masses (gear, engine, fuel, stores) are added as
spanwise steps.

**One mass model (design note 63, v67).** The panel weight and the concentrated
masses are not entered here: the panel is half the ``WING``-carried ``PANEL``
parts of the item database (:func:`sloads.mass_distribution.panel_weight`,
override allowed) and the concentrated masses are the ``POINT``-carriage WING
rows of **the case's own loading** (:func:`sloads.mass_distribution.wing_mass_state`).
The panel *shape* -- the root-density iteration -- is built once per run at the
project panel weight; each case folds its own panel scale and point list onto
it (:func:`fold_units`), so a zero-fuel case carries no wing-fuel relief and a
full-fuel case carries all of it. Every result names the mass state it ran at.

Three unit distributions are formed along the quarter chord (airplane axes):

* **1g vertical** -- ``Fz = W``; ``Sz`` cumulative; ``Mxx = Σ Sz·dy``; torsion
  ``Tyy = −Σ Sz·Δx25 − Σ W·(x50−x25)`` (lines 950-1110);
* **1g drag** -- ``Fx = W``; ``Sx`` cumulative; ``Mzz = Σ Sx·dy``; torsion from the
  mass Z offset ``Σ Sx·Δz`` (lines 1150-1310);
* **unit roll** (100 000 in-lb) -- ``Fz = W·Y·1e5/Iwxx`` with ``Iwxx = 2·Σ W·Y²``,
  integrated like the vertical case (lines 1350-1610).

For a condition ``(Nz, Nx, unbalanced rolling moment)`` they combine (lines
1740-1820): ``Fz = Nz·W + UNB/1e5·Fz_roll``, ``Fx = Nx·W``, and likewise for the
shears/moments; torsion ``Myy = Nz·Tyy + Nx·Tvyy + UNB/1e5·Tuyy``. The signs are
entered so the inertia acts opposite the air load (up and aft positive), i.e.
``Nz`` is the negative of the air-load load factor -- NETLOADS then *adds* air and
inertia.

Reference: WINGINER.BAS (Appendix C p455-458), Ref 1 Ch 13; worked example
Appendix A "Wing Inertia Loads" p217-221 (panel 165 lb, density ratio 0.95, rib
BL 23: root density 2.213 lb/ft²; case 138 Nz −2.54 Nx −0.1318 root Mxx −41041).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Dict, List, NamedTuple, Optional, Sequence

from ..aero_curves import inertia_drag_factor
from ..basic import basic_trunc3
from ..case_ids import COMPONENT_PREFIX, WING_BAND_EXTRA, WING_SLOTS, wing_case_id
from ..cg_cases import flight_cases
from ..constants import DEG_PER_RAD, IN2_PER_FT2
from ..convergence import solver_failure
from ..derived_geometry import require_integrable_planform, sync_geometry_derived, wing_plane
from ..mass_distribution import WingMassState, panel_weight, wing_mass_state
from ..models import (
    CaseRef,
    ConcentratedLoad,
    ConditionResult,
    CriticalCondition,
    LoadValue,
    MassItem,
    MissingInputError,
    ModuleResult,
    Project,
    SurfaceInput,
    VnPoint,
    WingLoadCase,
    WingLoadResult,
    WingMassInput,
    WingStationLoad,
)
from ..registry import register
from .rolling import complete_rolling_case
from .select import default_critical, default_envelope
from .wing_geometry import interp_x

# Trip bound on the root-density iteration (WINGINER.BAS spun it unbounded). At
# 1e-5 per trip this is a density excursion of 1.0 from a 0.02 start: exhausting
# it is a defect, not a tuning knob.
_DENSITY_TRIPS = 100000


@dataclass
class _UnitPointMass:
    """One concentrated wing mass with its unit-roll force, before Nz/Nx/UNB."""
    name: str
    x: float
    y: float
    z: float
    w: float
    fz_r: float


@dataclass
class _InertiaUnits:
    """Per-strip mass distribution and the three unit inertia distributions.

    All lists are root->tip, one entry per strip. ``w`` is the strip mass (lb);
    the ``*_v`` are the 1g-vertical, ``*_d`` the 1g-drag and ``*_r`` the unit-roll
    (100 000 in-lb) cumulative distributions."""
    ye: List[float] = field(default_factory=list)
    c25x: List[float] = field(default_factory=list)
    #: 50% chord -- where WINGINER models the panel mass CG (see ``tyy_v``).
    c50x: List[float] = field(default_factory=list)
    z: List[float] = field(default_factory=list)
    w: List[float] = field(default_factory=list)
    sz_v: List[float] = field(default_factory=list)
    mxx_v: List[float] = field(default_factory=list)
    tyy_v: List[float] = field(default_factory=list)
    sx_d: List[float] = field(default_factory=list)
    mzz_d: List[float] = field(default_factory=list)
    tvyy_d: List[float] = field(default_factory=list)
    fz_r: List[float] = field(default_factory=list)
    sz_r: List[float] = field(default_factory=list)
    mxx_r: List[float] = field(default_factory=list)
    tyy_r: List[float] = field(default_factory=list)
    #: The entered concentrated masses, each with the unit-roll force
    #: ``fz_r = W*y*1e5/Iwxx`` that pairs with ``w``'s ``fz_r`` for a strip.
    #: Held so :func:`wing_inertia_distribution` can scale a point mass by the
    #: case's Nz/Nx/UNB exactly as it scales a strip -- the cumulative
    #: distributions below already have them folded in and cannot be read back
    #: apart (OR-15 admission #166, 2026-09-03).
    point_masses: List["_UnitPointMass"] = field(default_factory=list)
    density_root: float = 0.0
    density_tip: float = 0.0
    #: The semispan roll inertia ``Iwxx = 2*sum(W*y^2)`` (lb-in^2), strips and
    #: point masses -- the denominator of the unit-roll forces and of the roll
    #: acceleration published beside an ACRL case (design note 52, D-52.4).
    iwxx: float = 0.0


def _root_density(dA, ye, c, dy, ytip, wm: WingMassInput, ii: int,
                  target: float):
    """Iterate the root area density until the panel mass equals ``target``.

    Mirrors WINGINER.BAS lines 730-880 (a partial first-strip correction at the
    inboard rib, ±1% tolerance, 1e-5 density steps).

    A **non-positive target** short-circuits to an empty panel. The iteration has
    no fixed point there -- its ±1% band is empty at zero, so it walks the density
    down past zero and returns *negative* strip masses (-0.108 lb on ``ga6_normal``
    with the panel weight cleared), which is not a lighter wing but a sign-flipped
    one. Reported with review F-C5, whose partition gate in :mod:`sloads.modules.balance`
    is what turns an empty panel into an error where it is one.

    Exhausting the trips **raises** (#33, :mod:`sloads.convergence`): the density
    would have walked 1.0 from its 0.02 start without the panel mass ever entering
    the ±1 % band, and the last density is then a value the loop was passing
    through, not the answer."""
    dr = wm.tip_root_density_ratio
    rsta = wm.inboard_rib_y
    if target <= 0.0:
        return [0.0] * len(ye), 0.0
    span_out = ytip - rsta
    densr = 0.02
    w = [0.0] * len(ye)
    tw = 0.0
    for _ in range(_DENSITY_TRIPS):
        tw = 0.0
        for i in range(ii, len(ye)):
            w[i] = dA[i] * densr * (1.0 - (ye[i] - rsta) * (1.0 - dr) / span_out)
            tw += w[i]
        # Subtract the part of the first strip inboard of the rib.
        d = dy / 2.0 - (ye[ii] - rsta)
        dw = d * c[ii] * densr
        tw -= dw
        w[ii] -= dw
        if 0.99 * target < tw < 1.01 * target:
            break
        if tw >= 1.01 * target:
            densr -= 0.00001
        else:
            densr += 0.00001
    else:  # the density never brought the panel mass into the +-1% band
        raise solver_failure(
            "the wing panel root-density iteration",
            trips=_DENSITY_TRIPS,
            detail=(f"target panel weight {target:.6g} lb, reached {tw:.6g} lb at "
                    f"root density {densr:.6g}, tip/root ratio {dr:.6g}"),
        )
    return w, densr


@dataclass
class _PanelShape:
    """The tapered panel, integrated once: strips root->tip at one target weight.

    Design note 63 D-63.6: the *shape* is built once per run, at the project's
    panel weight, and every case scales it (``fold_units``). ``target`` is the
    weight the iteration was aimed at, so a case whose panel equals it scales by
    exactly 1.0 -- which is what keeps Appendix A bit-for-bit -- and a case with
    less or more panel mass (a PANEL-carriage row not aboard) scales by the
    ratio rather than re-running the ±1 % iteration to a different band.
    """
    ye: List[float]
    c25x: List[float]
    c50x: List[float]
    z: List[float]
    w: List[float]
    dy: float
    target: float
    density_root: float
    density_tip: float


def panel_shape(geom: SurfaceInput, wm: WingMassInput,
                wrp_waterline: float, dihedral_deg: float,
                panel_weight_lb: float) -> _PanelShape:
    """The wing-panel mass distribution at ``panel_weight_lb`` per side.

    ``wrp_waterline``/``dihedral_deg`` describe the wing plane and are passed in
    (note 33, DS-4): they belong to the *parametric* wing, which ``geom`` — a
    single ``SurfaceInput`` — does not carry. Resolve them once per run with
    :func:`sloads.derived_geometry.wing_plane`. ``panel_weight_lb`` is passed
    in for the same reason (note 63): it belongs to the item database, read
    through :func:`sloads.mass_distribution.panel_weight`, not to this slice.

    This is the second entry into the WINGGEOM strip sweep, and it had none of
    the precondition ``surface_properties`` enforces: a mid-entry planform
    reached ``leading_edge[-1]`` and ``interp_x``'s ``pts[-2]`` and came back as
    a raw ``IndexError`` (#71, PB-21). Both entries now ask the one owner.
    """
    require_integrable_planform(geom)
    yroot = geom.leading_edge[0][1]
    ytip = geom.leading_edge[-1][1]
    h = geom.elements
    dy = (ytip - yroot) / h
    ye = [yroot + dy / 2 + j * dy for j in range(h)]
    c = [interp_x(geom.trailing_edge, y) - interp_x(geom.leading_edge, y) for y in ye]
    c25x = [interp_x(geom.leading_edge, y) + 0.25 * cc for y, cc in zip(ye, c)]
    c50x = [interp_x(geom.leading_edge, y) + 0.50 * cc for y, cc in zip(ye, c)]
    dA = [cc * dy for cc in c]
    z = [wrp_waterline + math.tan(dihedral_deg / DEG_PER_RAD) * y for y in ye]

    ii = next((i for i, y in enumerate(ye) if y >= wm.inboard_rib_y), 0)
    w, densr = _root_density(dA, ye, c, dy, ytip, wm, ii, panel_weight_lb)
    return _PanelShape(ye=ye, c25x=c25x, c50x=c50x, z=z, w=w, dy=dy, target=panel_weight_lb,
                       density_root=basic_trunc3(IN2_PER_FT2 * densr),
                       density_tip=basic_trunc3(IN2_PER_FT2 * wm.tip_root_density_ratio * densr))


def fold_units(shape: _PanelShape, panel_weight_lb: float,
               point_masses: Sequence[MassItem] = ()) -> _InertiaUnits:
    """The three unit inertia distributions for one mass state.

    The panel strips are ``shape`` scaled to ``panel_weight_lb`` (exactly 1.0
    when it is the shape's own target); ``point_masses`` are this state's
    per-side concentrated masses, each at its own ``x``/``y``/``z`` (a
    :class:`~sloads.models.MassItem` part, note 63 D-63.3). The roll inertia
    ``Iwxx`` and the unit-roll forces are built from both, per WINGINER.BAS
    1350-1610, so a case with a different point list has its own roll
    distribution as the ``.BAS`` would give it.
    """
    ye, c25x, c50x, z, dy = shape.ye, shape.c25x, shape.c50x, shape.z, shape.dy
    h = len(ye)
    scale = (panel_weight_lb / shape.target) if shape.target > 0.0 else 0.0
    w = [wi * scale for wi in shape.w] if scale != 1.0 else list(shape.w)

    u = _InertiaUnits(ye=list(ye), c25x=list(c25x), c50x=list(c50x), z=list(z), w=w,
                      density_root=shape.density_root, density_tip=shape.density_tip)

    iwxx = 2.0 * (math.fsum(w[i] * ye[i] ** 2 for i in range(h))
                  + math.fsum(cw.weight_lb * cw.y ** 2 for cw in point_masses)) or 1.0
    fz_r = [w[i] * ye[i] * 100000.0 / iwxx for i in range(h)]
    u.fz_r = fz_r
    u.iwxx = iwxx

    # Cumulative integration tip->root for the vertical, drag and roll cases.
    sz_v = [0.0] * h
    mxx_v = [0.0] * h
    tyy_v = [0.0] * h
    sx_d = [0.0] * h
    mzz_d = [0.0] * h
    tvyy_d = [0.0] * h
    sz_r = [0.0] * h
    mxx_r = [0.0] * h
    tyy_r = [0.0] * h
    sz_v[h - 1] = w[h - 1]
    sx_d[h - 1] = w[h - 1]
    sz_r[h - 1] = fz_r[h - 1]
    tyy_v[h - 1] = -w[h - 1] * (c50x[h - 1] - c25x[h - 1])
    tyy_r[h - 1] = -fz_r[h - 1] * (c50x[h - 1] - c25x[h - 1])
    for i in range(h - 2, -1, -1):
        sz_v[i] = sz_v[i + 1] + w[i]
        sx_d[i] = sx_d[i + 1] + w[i]
        sz_r[i] = sz_r[i + 1] + fz_r[i]
        mxx_v[i] = mxx_v[i + 1] + sz_v[i + 1] * dy
        mzz_d[i] = mzz_d[i + 1] + sx_d[i + 1] * dy
        mxx_r[i] = mxx_r[i + 1] + sz_r[i + 1] * dy
        tyy_v[i] = tyy_v[i + 1] - sz_v[i + 1] * (c25x[i + 1] - c25x[i]) - w[i] * (c50x[i] - c25x[i])
        tvyy_d[i] = tvyy_d[i + 1] + sx_d[i + 1] * (z[i + 1] - z[i])
        tyy_r[i] = tyy_r[i + 1] - sz_r[i + 1] * (c25x[i + 1] - c25x[i]) - fz_r[i] * (c50x[i] - c25x[i])

    # Concentrated wing masses (gear, engine, fuel, store) add spanwise steps to
    # the shears/moments/torsion of every strip inboard of the weight (WINGINER.BAS
    # lines 1180-1270, 1570-1610). The per-strip Fz/Fx stay panel-only; the weight
    # is a point load carried in the cumulative shear.
    for cw in point_masses:
        fzcwt = cw.weight_lb * cw.y * 100000.0 / iwxx
        u.point_masses.append(_UnitPointMass(
            name=getattr(cw, "name", ""), x=cw.x, y=cw.y, z=cw.z,
            w=cw.weight_lb, fz_r=fzcwt))
        for i in range(h):
            if ye[i] < cw.y:
                sz_v[i] += cw.weight_lb
                mxx_v[i] += cw.weight_lb * (cw.y - ye[i])
                tyy_v[i] += cw.weight_lb * (c25x[i] - cw.x)
                sx_d[i] += cw.weight_lb
                mzz_d[i] += cw.weight_lb * (cw.y - ye[i])
                tvyy_d[i] += cw.weight_lb * (cw.z - z[i])
                sz_r[i] += fzcwt
                mxx_r[i] += fzcwt * (cw.y - ye[i])
                tyy_r[i] += fzcwt * (c25x[i] - cw.x)

    u.sz_v, u.mxx_v, u.tyy_v = sz_v, mxx_v, tyy_v
    u.sx_d, u.mzz_d, u.tvyy_d = sx_d, mzz_d, tvyy_d
    u.sz_r, u.mxx_r, u.tyy_r = sz_r, mxx_r, tyy_r
    return u


def inertia_units(geom: SurfaceInput, wm: WingMassInput,
                  wrp_waterline: float, dihedral_deg: float, *,
                  panel_weight_lb: float,
                  point_masses: Sequence[MassItem] = ()) -> _InertiaUnits:
    """Build the panel distribution and the three unit inertia cases in one call.

    :func:`panel_shape` at ``panel_weight_lb`` folded with ``point_masses``
    (:func:`fold_units`) -- the form a single-state caller wants: a test against
    Appendix A (panel 165 lb, no points), or the balanced deck's shape read.
    Per-case runs build the shape once and fold per case.
    """
    shape = panel_shape(geom, wm, wrp_waterline, dihedral_deg, panel_weight_lb)
    return fold_units(shape, panel_weight_lb, point_masses)


def wing_inertia_distribution(case: WingLoadCase, units: _InertiaUnits
                              ) -> WingLoadResult:
    """Combine the unit inertia distributions for one condition's Nz/Nx/UNB.

    ``units`` is required (note 33, DS-2). It used to default to ``None`` and
    rebuild itself, which was a second construction path that read the wing plane
    from a different place than its callers did — exactly the kind of duplicate
    resolution this note exists to remove.
    """
    u = units
    nz = case.nz if case.nz is not None else 0.0
    nx = case.nx if case.nx is not None else 0.0
    ur = (case.unbal_moment or 0.0) / 100000.0
    stations: List[WingStationLoad] = []
    for i in range(len(u.ye)):
        stations.append(WingStationLoad(
            x=u.c25x[i], y=u.ye[i], z=u.z[i],
            fx=nx * u.w[i],
            fz=nz * u.w[i] + ur * u.fz_r[i],
            sx=nx * u.sx_d[i],
            sz=nz * u.sz_v[i] + ur * u.sz_r[i],
            mxx=nz * u.mxx_v[i] + ur * u.mxx_r[i],
            myy=nz * u.tyy_v[i] + nx * u.tvyy_d[i] + ur * u.tyy_r[i],
            mzz=nx * u.mzz_d[i],
            # The panel mass acts at the 50% chord, the axis is at the 25%, so
            # the strip's own inertia force carries an offset moment about the
            # axis -- the ``- w*(c50x - c25x)`` and ``- fz_r*(c50x - c25x)``
            # terms of ``tyy_v``/``tyy_r``. The drag case has no free term:
            # ``tvyy_d`` is transfer only.
            myy_free=(nz * -u.w[i] * (u.c50x[i] - u.c25x[i])
                      + ur * -u.fz_r[i] * (u.c50x[i] - u.c25x[i])),
        ))
    # The same three factors the strips are scaled by, applied to the point
    # masses -- so the published applied set sums to the published cumulative
    # one. A concentrated mass carries no free moment: its whole contribution to
    # ``mxx``/``myy`` above is the transfer of this force to the station's axis.
    points = [ConcentratedLoad(name=pm.name, x=pm.x, y=pm.y, z=pm.z,
                               fx=nx * pm.w, fz=nz * pm.w + ur * pm.fz_r)
              for pm in u.point_masses]
    return WingLoadResult(case=case.name, nz=nz, nx=nx, stations=stations,
                          point_loads=points)


# --------------------------------------------------------------------------- #
# Project entry point + registration
# --------------------------------------------------------------------------- #
class WingCaseSources(NamedTuple):
    """The two upstream reads every wing-case helper needs, resolved once per build.

    ``wing_inertia`` and ``net_loads`` walk the same resolved case list and ask the
    project the same two questions of each case -- *which V-n point does it
    reference* and *did SELECT already name this condition* -- so both answers come
    from the ``select`` **single owners** (:func:`select.vn_by_case`,
    :func:`select.default_critical`) and are threaded, not re-read per case. Reading
    ``project.envelope`` directly here silently emptied both on the
    ``registry.run_all_modules`` path, which never assigns it: a SELECT-derived
    wing case raised ``MissingInputError`` in ``net_loads`` and yielded *no cases at
    all* in ``wing_inertia`` (review F-C6). Threading also keeps the envelope from
    being rebuilt once per case, the same reason ``build_critical`` threads
    ``envelope=`` into every ``select_*`` helper (M2R-8).
    """

    #: V-n points by case number -- ``{}`` when no matrix can be built at all.
    vn: Dict[int, VnPoint]
    #: SELECT's **wing** conditions -- ``[]`` when SELECT cannot run.
    wing_conditions: List[CriticalCondition]


def wing_case_sources(project: Project) -> WingCaseSources:
    """Resolve :class:`WingCaseSources` for ``project`` through the owners.

    Tolerant by construction: a project with no flight-loads inputs cannot have a
    V-n matrix or a critical set, and that is not an error *here* -- a case with
    explicit ``nz``/``nx`` needs neither. The loud failure belongs to the consumer
    that actually needs the missing value (``_resolve_case``,
    ``net_loads._air_cl_v``), which names the case it could not resolve.

    The matrix is resolved once and threaded into ``default_critical`` (which would
    otherwise rebuild it inside ``build_critical``), so one call costs one envelope.
    """
    try:
        envelope = default_envelope(project)
    except MissingInputError:
        return WingCaseSources(vn={}, wing_conditions=[])
    conditions = [c for c in default_critical(project, envelope).conditions
                  if c.component == "wing"]
    return WingCaseSources(vn={p.case: p for p in envelope.vn},
                           wing_conditions=conditions)


def _sources(project: Project,
             sources: Optional[WingCaseSources]) -> WingCaseSources:
    """The threaded sources when the build supplies them, else resolved once."""
    return sources if sources is not None else wing_case_sources(project)


def _resolve_case(project: Project, case: WingLoadCase,
                  sources: Optional[WingCaseSources] = None) -> WingLoadCase:
    """Fill Nz/Nx from the referenced V-n point when not given explicitly.

    The C3-before-SELECT bridge: ``Nz = −NZ`` and ``Nx = −DX/W`` come straight from
    the FLTLOADS V-n point (inertia opposes the air load), reached through
    :class:`WingCaseSources`."""
    if case.nz is not None and case.nx is not None:
        return case
    vn = _sources(project, sources).vn
    if case.case is None or not vn:
        raise MissingInputError(
            f"wing load case '{case.name}' needs explicit nz/nx or a 'case' "
            "reference into the V-n matrix (Project.envelope or 'flight_loads')"
        )
    vp = vn.get(case.case)
    if vp is None:
        raise ValueError(f"wing load case '{case.name}' references unknown V-n case {case.case}")
    nz = case.nz if case.nz is not None else -vp.nz
    nx = case.nx
    if nx is None:
        weight = _case_weight(project, vp.cg)
        nx = inertia_drag_factor(vp.dx, weight)
    return WingLoadCase(name=case.name, case=case.case, nz=nz, nx=nx,
                        unbal_moment=case.unbal_moment, cl=case.cl, v_eas_kt=case.v_eas_kt)


def resolve_wing_cases(project: Project, wm: WingMassInput,
                       sources: Optional[WingCaseSources] = None) -> List[WingLoadCase]:
    """``wm.cases``, or -- when it is empty -- the cases derived from SELECT's
    wing ``CriticalCondition`` list (M4-2 decision 2).

    SELECT is the case authority: it already searched the V-n matrix for the
    governing wing points, so re-typing them into ``WingMassInput.cases`` is a
    second, silently-divergent entry of the same conditions. A derived case
    carries only its name and its V-n case number; ``_resolve_case`` and
    ``net_loads._air_cl_v`` fill Nz/Nx/CL/V from that point exactly as they do
    for a hand-authored case that gives only a ``case`` reference.

    **An entered list is a filter on the slot list, never a second source of
    points** (design note 63, D-63.7, narrowing M4-2 decision 2's "explicit
    entries always win"): an entered case that names a SELECT wing slot and
    gives no ``case`` of its own takes the slot's delivered V-n point -- the
    net-governing run since #292 -- so its mass state, run key and CG follow
    the selection while the entry decides *which* slots run and carries what
    the selection cannot name (an ACRL case's ``unbal_moment``, an explicit
    ``cg`` mass state per D-63.6, an explicit speed per the 2026-08-13 ruling
    in :func:`wing_case_ref`). An entry with explicit ``nz``/``nx`` and no
    matching slot -- a project with no flight-loads inputs, the
    C3-before-SELECT bridge -- runs as entered. Derivation is the fallback for
    a project that never filled the table, and the *Wing Loads* page's "pull
    from SELECT" button materialises the same list into the editable table.

    **The accelerated roll arrives complete** (design note 52, D-52.2/D-52.10):
    an ``ACRL`` case -- derived, or entered with blanks -- takes its unbalanced
    rolling moment and its condition A air point from
    :func:`sloads.modules.rolling.complete_rolling_case`, the owners every reader
    of the case shares. UNB is ``-(1 - p/100)`` of condition A's root air
    bending (Ref 1 Ch 12 p. 92, Ch 13 pp. 95-96); an entered value still wins.
    """
    src = _sources(project, sources)
    conditions = src.wing_conditions
    if wm.cases:
        by_label = {c.label: c for c in conditions if c.case is not None}
        cases = [replace(c, case=by_label[c.name].case)
                 if c.case is None and c.name in by_label else c
                 for c in wm.cases]
    else:
        cases = [WingLoadCase(name=c.label, case=c.case) for c in conditions]
    return [complete_rolling_case(project, c, src.vn) for c in cases]


def _stated_speed(case: WingLoadCase, vp: Optional[VnPoint],
                  fallback: Optional[float] = None) -> Optional[float]:
    """The speed the case's loads are **computed at** -- the case's own
    ``v_eas_kt`` when it states one, else its V-n point's, else ``fallback``.

    Same precedence as ``net_loads._air_cl_v``, which is the point: the speed a
    deliverable names and the speed its numbers were built from come from one
    rule (user decision 2026-08-13, backlog priority 1).
    """
    if case.v_eas_kt is not None:
        return case.v_eas_kt
    if vp is not None:
        return vp.v_eas_kt
    return fallback


def wing_case_ref(project: Project, index: int, case: WingLoadCase,
                  sources: Optional[WingCaseSources] = None) -> CaseRef:
    """The :class:`CaseRef` for wing structural case ``index`` (0-based) in the
    resolved case list (:func:`resolve_wing_cases`).

    **One ID per physical condition** (M4-2 decision 1): when SELECT has already
    named this condition, its :class:`CaseRef`'s ``case_id`` is kept -- the
    spanwise distribution WINGINER/NETLOADS produce is another deliverable of the
    same case, not a second case, which is exactly what
    ``report.tables.case_index_rows_from``'s dedupe-by-``case_id`` assumes. Failing
    that (SELECT not run, or a case the engineer added by hand), the ID comes from
    the fixed ``case_ids.WING_SLOTS`` table by **name** -- so ``PHAA`` is ``W-01``
    either way -- and a name outside the table takes the next
    ``case_ids.WING_BAND_EXTRA`` slot.

    **The flight condition is the case's own** (user decision 2026-08-13): where
    ``WingLoadCase`` states a ``v_eas_kt``, that speed is what the loads were
    computed at (``net_loads._air_cl_v``), so it is the speed the row states --
    even when SELECT named the same condition at a different V-n point. On
    ``atr42_100`` the fixture enters ``PHAA`` at 170 kt while SELECT's ``PHAA``
    point is 185.85 kt (``balance/applied.py`` records the same divergence), and before
    this the case-index row read 185.9 kt beside loads built at 170. CG, altitude
    and the FAR reference stay SELECT's: the case states none of them, and they
    are properties of the physical condition the shared ``case_id`` names.

    Still a **pure function** of the project and the case's position, not a
    stateful allocator, so ``wing_inertia.py`` and ``net_loads.py`` -- two
    independent modules iterating the same list -- agree on the identical
    ``CaseRef`` without sharing runtime state.
    """
    src = _sources(project, sources)
    vp = src.vn.get(case.case) if case.case is not None else None
    for c in src.wing_conditions:
        if c.label == case.name and c.case_ref is not None:
            speed = _stated_speed(case, vp, fallback=c.case_ref.speed_kt)
            if speed == c.case_ref.speed_kt:
                return c.case_ref
            return replace(c.case_ref, speed_kt=speed)
    if case.name in WING_SLOTS:
        case_id = wing_case_id(case.name)
    else:
        # Extra-band cases number by their order among the *other* extras, so
        # adding a slot case in front of one does not renumber it.
        cases = resolve_wing_cases(project, project.wing_mass or WingMassInput(), src)
        extras = [i for i, c in enumerate(cases) if c.name not in WING_SLOTS]
        seq = WING_BAND_EXTRA + (extras.index(index) if index in extras else index)
        case_id = f"{COMPONENT_PREFIX['wing']}-{seq:02d}"
    return CaseRef(
        case_id=case_id,
        component="wing",
        condition=case.name,
        cg=vp.cg if vp else "",
        speed_kt=_stated_speed(case, vp),
        altitude_ft=vp.altitude_ft if vp else None,
        far_reference="23.301(b)",
        run=vp.condition if vp else "",
        config=vp.config if vp else "",
    )


def resolve_mass_case(project: Project, case: WingLoadCase,
                      sources: Optional[WingCaseSources] = None) -> Optional[str]:
    """The FLIGHT CG case whose loading is ``case``'s mass state (note 63, D-63.6).

    In order: the case's own ``cg``; the CG case of the V-n point it references;
    the CG case of SELECT's wing condition of the same label (a hand-entered
    case that restates a selected condition, ``atr42_100``'s ``PHAA``); else
    ``None`` -- the item database with every row aboard, which
    :func:`sloads.mass_distribution.wing_mass_state` labels as such and
    ``validation`` names (``wing_case_mass_state_unnamed``).
    """
    if case.cg:
        return case.cg
    src = _sources(project, sources)
    if case.case is not None:
        vp = src.vn.get(case.case)
        if vp is not None and vp.cg:
            return vp.cg
    for c in src.wing_conditions:
        if c.label == case.name and c.case is not None:
            vp = src.vn.get(c.case)
            if vp is not None and vp.cg:
                return vp.cg
    return None


def case_mass_state(project: Project, case: WingLoadCase,
                    sources: Optional[WingCaseSources] = None) -> WingMassState:
    """The resolved :class:`~sloads.mass_distribution.WingMassState` of ``case``."""
    return wing_mass_state(project, resolve_mass_case(project, case, sources))


def _with_mass_state(ref: CaseRef, state: WingMassState) -> CaseRef:
    """The case ref naming the mass state it ran at: ``cg`` is the state's case.

    A wing case may restate a selected condition at a different mass state
    (an explicit ``cg``), and the row that names the loads must name the
    loading they were built from -- the same rule ``wing_case_ref`` applies to
    the speed. Left as it was when the state is the database (``cg`` then
    keeps the V-n point's name, which is where the *air* load came from).
    """
    if state.case and ref.cg != state.case:
        return replace(ref, cg=state.case)
    return ref


def _case_weight(project: Project, cg_name: str) -> float:
    for cg in flight_cases(project):
        if cg.name == cg_name:
            return cg.weight_lb
    return 0.0


MODULE_NAME = "wing_inertia"


def build_wing_inertia(project: Project) -> List[WingLoadResult]:
    """Compute the wing inertia distribution for every configured load case."""
    sync_geometry_derived(project)
    wm = project.wing_mass
    if wm is None:
        raise MissingInputError("Project has no 'wing_mass' inputs for the wing_inertia module")
    if project.geometry is None or project.geometry.by_name(wm.surface) is None:
        raise MissingInputError(f"wing_inertia needs a '{wm.surface}' geometry surface")
    # Resolved once for the whole build and threaded into every helper (M2R-8).
    src = wing_case_sources(project)
    cases = resolve_wing_cases(project, wm, src)
    if not cases:
        raise MissingInputError(
            "wing_inertia needs at least one load case -- enter them in "
            "'wing_mass.cases' or give the flight-loads inputs SELECT needs so "
            "they can be derived from the critical set")
    geom = project.geometry.by_name(wm.surface)
    if geom is None:  # already refused above; narrows for the calls below
        raise MissingInputError(f"wing_inertia needs a '{wm.surface}' geometry surface")
    # The shape once, at the project panel; each case folds its own state
    # (note 63 D-63.6) -- the panel it carries and the POINT rows aboard.
    shape = panel_shape(geom, wm, *wing_plane(project, wm.surface), panel_weight(project))
    results = []
    for i, c in enumerate(cases):
        state = case_mass_state(project, c, src)
        units = fold_units(shape, state.panel_weight_lb, state.point_masses)
        r = wing_inertia_distribution(_resolve_case(project, c, src), units)
        r.case_ref = _with_mass_state(wing_case_ref(project, i, c, src), state)
        r.mass_state = state.label
        results.append(r)
    return results


def run(project: Project) -> ModuleResult:
    """Run WINGINER against a :class:`Project`'s wing-mass inputs."""
    results = build_wing_inertia(project)
    conditions: List[ConditionResult] = []
    for r in results:
        root = r.stations[0]
        conditions.append(ConditionResult(
            title=f"Wing inertia loads: {r.case} (Nz={r.nz:g}, Nx={r.nx:g})",
            far_reference="23.301(b)",
            values=[
                LoadValue("Root shear Sz", root.sz, "lb", key="root_shear_sz"),
                LoadValue("Root bending Mxx", root.mxx, "lb-in", key="root_bending_mxx"),
                LoadValue("Root torsion Myy (25% chord)", root.myy, "lb-in", key="root_torsion_myy_25_pct_chord"),
                LoadValue("Root drag shear Sx", root.sx, "lb", key="root_drag_shear_sx"),
                LoadValue("Root chord bending Mzz", root.mzz, "lb-in", key="root_chord_bending_mzz"),
            ],
            case_ref=r.case_ref,
        ))
    return ModuleResult(module=MODULE_NAME, conditions=conditions)


register(MODULE_NAME, run)
