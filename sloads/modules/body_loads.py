"""Net fuselage loads -- the body analogue of NETLOADS (Reference 1 Ch 15).

Ch 15 ("Net Fuselage Loads") gives a *suggested procedure* rather than a ported
``.BAS`` program: the fuselage is a simple beam carrying the inertia of the
fuselage mass items reacted by the air load on the tail and the wing-attach
reaction. For each critical fuselage condition (selected by SELECT, R5) this
module:

  1. multiplies each fuselage station weight by the linear load factor ``NZ`` to
     get its inertia force (``fz = -NZ*w``, down for positive NZ);
  2. applies the balancing tail air load ``LT`` at the tail station;
  3. closes the free body with **the wing reaction at one station** -- the
     wing station ``x_w``, where the wing post stands (design note 64 D-64.5):
     the force ``R = -sum(fz)`` and the couple ``M_w`` that zero the moment of
     the whole set about ``x_w``;
  4. integrates the **forward body from the nose to the front spar** and the
     **aft body from the tail to the rear spar**, each from its free end toward
     the wing box (D-64.2).

**The box is not a beam region** (note 64 ruling 1). A station at or between
the spars -- a mass item that sits there, the wing reaction itself -- is an
applied load the box reacts, published as a ``"box"`` row with no running
shear or moment; no integration runs through it, so the ``+/-M/d`` question
p103's two point reactions raise never arises and the linear smear M4-1 used
to answer it (2026-08-03 .. 2026-09-21) retires. The front/rear spar **fitting
loads** are still reported (:func:`fitting_load_rows`): the static equivalent
of ``(R, M_w)`` at the two spar stations, the same 2x2 as p103's, applied
nowhere.

**Sign (D-64.4).** In either body, shear and bending are **positive for an up
load**: forward ``V(x) = sum(fz_i, x_i <= x)``,
``M(x) = sum(fz_i (x - x_i), x_i <= x)``; aft ``V(x) = sum(fz_i, x_i >= x)``,
``M(x) = sum(fz_i (x_i - x), x_i >= x)``. A positive-``nz`` inertia set
therefore bends both bodies **down**, negative, which is what a reader of a
2.5 g case expects to see. Owner: :func:`cantilever_sign` -- the aft body's
bending is the negative of the right-handed ``My`` about the cut, and the
report's Appendix G reads the sign from here rather than restating it.

There is **no printed station-by-station oracle** (Ch 15 ships no program), so
the result is validated by **equilibrium closure**: the forward table's
terminal shear and moment at the front spar are the forward set's resultant
and moment, the aft table's at the rear spar likewise, and the two terminals,
the box's applied rows and the reaction sum to zero force and zero moment.
The fuselage station weights (``Project.fuselage_mass``) should already exclude
the wing mass outside the fuselage, per Ch 15.

The spar stations come from :func:`sloads.derived_geometry.carry_through` and
the wing station from the joint register (:func:`sloads.joints.wing_station`).
A project that cannot place the wing post -- no side of body, no
carry-through, or a wing station outside its spars -- is **refused by name**
(note 64 §8 ruling 1); the whole-body "closure artifact" correction that used
to close such a beam had no physical source and is gone.

Still open, split out of M4-1: the **pitching** half of p103's "linear and
pitching load factors" (**M4-21**; ``theta_ddot = 0`` on these balanced trim
cases, so it does not affect this closure) and the distributed body aero moment
(**M4-19**).

Coordinates are the airplane body axes (fuselage station X aft, waterline Z up),
pounds and inch-pounds.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from ..derived_geometry import (
    CarryThrough,
    carry_through,
    require_wing_reference,
    sync_geometry_derived,
)
from ..joints import wing_station
from ..mass_distribution import WingMassState, fuselage_beam_stations, wing_mass_state
from ..models import (
    BodyLoadResult,
    BodyStationLoad,
    ConditionResult,
    CriticalCondition,
    MissingInputError,
    ModuleResult,
    Project,
    VnPoint,
)
from ..registry import register
from .select import _stamp_case_refs, default_envelope, select_fuselage

MODULE_NAME = "body_loads"

#: The three regions of the body beam (note 64 D-64.2), as ``BodyStationLoad.region``.
FORWARD = "forward"
AFT = "aft"
BOX = "box"

#: A station this close to a spar (in) is at it, and at a spar is the box's
#: (note 64 §8 ruling 2).
_AT_SPAR_TOL = 1e-9


def cantilever_sign(aft: bool) -> float:
    """The factor that turns the right-handed ``My`` about a cut into the body
    beam's published bending (note 64 D-64.4): ``+1`` for the forward body,
    ``-1`` for the aft.

    Bending is **positive for an up load in either body**. For a load forward
    of a cut the right-handed moment about +y is already that; for a load aft
    of a cut it is the opposite, so the aft cantilever's published moment is
    its negative. Read by the report's Appendix G so its fuselage curves and
    this table cannot disagree about a sign.
    """
    return -1.0 if aft else 1.0


def _tail_station(project: Project, fallback: float) -> float:
    """Fuselage station of the tail air load (25% h-tail MAC) if available."""
    ti = project.tail_loads
    return ti.xt25 if ti is not None and ti.xt25 else fallback


def _cantilever(points: Sequence[Tuple[float, float, str]], x_root: float,
                aft: bool) -> List[BodyStationLoad]:
    """One body cantilever integrated from its free end to ``x_root``.

    ``points`` are the applied ``(x, fz, source)`` rows strictly on this
    cantilever's side of its spar. The running shear at a station is the sum of
    the loads from the free end **through** that station, and the running
    moment the sum of those loads times their arm to the station -- both
    positive for an up load (D-64.4). A terminal ``"root"`` row at the spar
    carries the cantilever's whole resultant and moment and applies nothing.
    """
    region = AFT if aft else FORWARD
    ordered = sorted(points, key=lambda pt: pt[0], reverse=aft)
    out: List[BodyStationLoad] = []
    sz = 0.0
    prev_x: Optional[float] = None
    myy = 0.0
    for x, fz, source in ordered:
        if prev_x is not None:
            myy += sz * abs(x - prev_x)      # the running shear over the bay
        sz += fz
        prev_x = x
        out.append(BodyStationLoad(x=x, fx=0.0, fy=0.0, fz=fz, sx=0.0, sy=0.0,
                                   sz=sz, mxx=0.0, myy=myy, mzz=0.0,
                                   source=source, region=region))
    if prev_x is not None:
        myy += sz * abs(x_root - prev_x)
    out.append(BodyStationLoad(x=x_root, fx=0.0, fy=0.0, fz=0.0, sx=0.0, sy=0.0,
                               sz=sz, mxx=0.0, myy=myy, mzz=0.0,
                               source="root", region=region))
    if aft:
        out.reverse()
    return out


def _spar_reactions(r_wing: float, m_wing: float, x_wing: float,
                    x_f: float, x_r: float) -> Tuple[float, float]:
    """The front/rear spar fitting loads ``(R_f, R_r)``: the static equivalent
    of the one reaction ``(R, M_w)`` at the wing station (note 64 D-64.5).

    ``R_f + R_r = R`` and the pair's right-handed moment about ``x_wing``
    equals ``M_w``::

        R_r = (R (x_w - x_f) - M_w) / (x_r - x_f)
        R_f = R - R_r
    """
    r_r = (r_wing * (x_wing - x_f) - m_wing) / (x_r - x_f)
    return r_wing - r_r, r_r


def closure_residuals(result: BodyLoadResult) -> Tuple[float, float]:
    """``(force, moment)`` left over when the two cantilevers, the box's applied
    rows and the wing reaction are summed -- both ~0 (note 64 gate 4).

    The forward terminal ``(V, M)`` at the front spar and the aft terminal at
    the rear spar are each the resultant of their own cantilever's loads, so
    summing them with the box's rows and the reaction is summing the whole
    applied set. The moment is taken about the wing station, right-handed
    about +y: the forward moment is already that sense, the aft one is
    published positive-for-up and is negated back (:func:`cantilever_sign`).
    """
    x_w = result.x_wing if result.x_wing is not None else 0.0
    force = 0.0
    moment = 0.0
    for s in result.stations:
        if s.source == "root":
            aft = s.region == AFT
            force += s.sz
            moment += cantilever_sign(aft) * s.myy - (s.x - x_w) * s.sz
        elif s.region == BOX:
            force += s.fz
            moment += s.couple - (s.x - x_w) * s.fz
    return force, moment


def body_distribution(stations, nz: float, tail_load: float, tail_x: float,
                      x_wing: float, carry: CarryThrough,
                      ) -> Tuple[List[BodyStationLoad], Dict[str, float]]:
    """The two body cantilevers for one condition (Ref 1 Ch 15 p103, note 64).

    Returns the station table nose -> tail -- the forward cantilever's rows,
    the box's applied rows (region ``"box"``, no running load), the aft
    cantilever's rows -- and the closure quantities: ``r_wing``/``m_wing`` at
    ``x_wing`` (the wing reaction and its couple, D-64.5), the fitting pair
    ``r_front``/``r_rear`` at ``x_front``/``x_rear``, and ``m_unbalanced``, the
    p103 pass-1 terminal moment of the inertia + tail set about its aft-most
    station.
    """
    applied: List[Tuple[float, float, str]] = [(x, -nz * w, "mass") for x, w in stations]
    applied.append((tail_x, tail_load, "tail"))
    x_ref = max(pt[0] for pt in applied)
    m_ub = math.fsum(fz * (x_ref - x) for x, fz, _ in applied)

    # The wing reaction closes the whole set at the wing station: force and
    # right-handed couple about +y (a load fz at arm dx makes My = -dx fz).
    r_wing = -math.fsum(fz for _, fz, _ in applied)
    m_wing = math.fsum((x - x_wing) * fz for x, fz, _ in applied)
    applied.append((x_wing, r_wing, "reaction"))
    r_f, r_r = _spar_reactions(r_wing, m_wing, x_wing, carry.x_f, carry.x_r)

    fwd = [pt for pt in applied if pt[0] < carry.x_f - _AT_SPAR_TOL]
    aft = [pt for pt in applied if pt[0] > carry.x_r + _AT_SPAR_TOL]
    box = [pt for pt in applied if pt not in fwd and pt not in aft]
    rows = _cantilever(fwd, carry.x_f, aft=False)
    rows += [BodyStationLoad(x=x, fx=0.0, fy=0.0, fz=fz, sx=0.0, sy=0.0, sz=0.0,
                             mxx=0.0, myy=0.0, mzz=0.0, source=source, region=BOX,
                             couple=(m_wing if source == "reaction" else 0.0))
             for x, fz, source in sorted(box, key=lambda pt: pt[0])]
    rows += _cantilever(aft, carry.x_r, aft=True)
    info: Dict[str, float] = {
        "m_unbalanced": m_ub, "r_wing": r_wing, "m_wing": m_wing, "x_wing": x_wing,
        "r_front": r_f, "r_rear": r_r, "x_front": carry.x_f, "x_rear": carry.x_r,
    }
    return rows, info


def _critical_fuselage(project: Project) -> List[CriticalCondition]:
    """The SELECT-critical fuselage conditions -- the persisted ``envelope.critical``
    if present (its ``CaseRef``s already stamped), else freshly computed.

    Calls ``select_fuselage`` directly (not ``build_critical``) so this module
    doesn't require ``tail_loads``/``vtail_loads`` to be well-formed just to get
    fuselage conditions -- it reuses SELECT's own ``_stamp_case_refs`` helper so
    the ``F-`` ids agree with a full SELECT run byte-for-byte (only the fuselage
    entries advance the fuselage counter, regardless of what other components are
    in the list)."""
    if project.envelope is not None and project.envelope.critical is not None:
        cached = [c for c in project.envelope.critical.conditions if c.component == "fuselage"]
        if cached:
            return cached
    conditions = select_fuselage(project)
    _stamp_case_refs(project, conditions)
    return conditions


def critical_fuselage_conditions(project: Project) -> List[CriticalCondition]:
    """The fuselage conditions this module runs, as the selection names them.

    The public form of :func:`_critical_fuselage`, for a consumer that needs the
    *identity* of a case rather than its loads -- the V-n point it was selected
    at, which no result type carries. Published rather than let each consumer
    call ``select_fuselage`` for itself: the report's run register and the
    conditions of :func:`critical_conditions` are then two views of one list,
    which is the drift OR-108 was chosen to prevent.
    """
    return _critical_fuselage(project)


def case_list_source(project: Project) -> str:
    """``"envelope"`` or ``"selection"`` -- where the case list came from.

    :func:`_critical_fuselage` takes the persisted ``envelope.critical`` when it
    carries fuselage conditions and re-selects otherwise, and note 44 OR-99
    requires the report to *say which*. Asked of the module that makes the
    choice, so the statement and the analysis cannot disagree about it.
    """
    envelope = project.envelope
    if (envelope is not None and envelope.critical is not None
            and any(c.component == "fuselage"
                    for c in envelope.critical.conditions)):
        return "envelope"
    return "selection"


def build_body_loads(project: Project) -> List[BodyLoadResult]:
    """Net fuselage load distribution for each critical fuselage condition."""
    sync_geometry_derived(project)
    fl = project.flight_loads
    # The station table is the mass SSOT's (step B1): derived from ``weight.items``
    # unless the project explicitly overrides it. Before B1 this read
    # ``fuselage_mass.stations`` directly, and every fixture's beam carried less
    # mass than the airplane weighed -- see :mod:`sloads.mass_distribution`.
    # Since design note 63 (D-63.8) the table is **per condition**: the
    # condition's own CG case resolves to its loading, and the beam lumps that
    # loading's body parts -- on ``ga6_normal`` 1,733 lb at GREATEST NZ (CG4,
    # a 2,063 lb airplane), not the data base's 3,070. The project-level read
    # below is the refusal check and the fallback for a case without a loading.
    beam = fuselage_beam_stations(project)
    if not beam or fl is None:
        raise MissingInputError("body_loads needs 'fuselage_mass' stations and 'flight_loads'")
    # Through the single owner (``select.default_envelope``), not a fresh
    # ``build_envelope``: a project that carries a persisted envelope had its
    # conditions taken from that one by ``_critical_fuselage``, so integrating them
    # against a *rebuilt* V-n matrix could pair a condition with an ``nz``/``lt``
    # from a different envelope than the one that selected it (review F-C6). The
    # raising read, not the tolerant one: a body deck with no V-n matrix behind it
    # is an input error, not a deck with no cases.
    vn: Dict[int, VnPoint] = {p.case: p for p in default_envelope(project).vn}
    require_wing_reference(project)
    tail_x = _tail_station(project, max(s.x for s in beam))
    # The wing reacts the body at the wing post (note 64 D-64.5). No post, no
    # beam: the register's own sentence is the refusal (§8 ruling 1).
    carry = carry_through(project)
    station = wing_station(project)
    if carry is None or station.refused is not None:
        raise MissingInputError(
            "body_loads cannot place the wing reaction -- "
            + (station.refused or "no wing carry-through resolves (degenerate "
                                  "root chord or spar stations)"))
    x_wing = station.x

    results: List[BodyLoadResult] = []
    states: Dict[str, WingMassState] = {}
    for cond in _critical_fuselage(project):
        p = vn.get(cond.case) if cond.case is not None else None
        if p is None:
            continue
        # One resolution per CG case: the same loading the balanced deck and
        # WINGINER read for it (D-63.1), so the body and the wing describe one
        # state. A loading the search cannot produce falls back to the data
        # base with the reason in the result's ``mass_state``.
        state = states.get(p.cg)
        if state is None:
            state = states[p.cg] = wing_mass_state(project, p.cg or None)
        case_beam = fuselage_beam_stations(project, state.loading) or beam
        stations = [(s.x, s.weight_lb) for s in case_beam]
        rows, info = body_distribution(stations, p.nz, p.lt, tail_x, x_wing, carry)
        results.append(BodyLoadResult(
            case=cond.label, stations=rows, case_ref=cond.case_ref,
            safety_factor=cond.safety_factor, mass_state=state.label,
            m_unbalanced=info["m_unbalanced"],
            r_front=info["r_front"], r_rear=info["r_rear"],
            x_front=info["x_front"], x_rear=info["x_rear"],
            spars_assumed=carry.assumed,
            x_wing=info["x_wing"], r_wing=info["r_wing"], m_wing=info["m_wing"],
            wing_station_note=station.note,
        ))
    return results


def body_load_rows(results: List[BodyLoadResult]) -> List[Dict[str, str]]:
    """One CSV row per fuselage station per condition.

    All loads are **LIMIT** (the oracle-traceable calc values), stated in-band by
    the ``Basis`` column so the basis travels with any table/CSV built from these
    rows (defect M4-15). The delivered form of the same loads is
    ``report.applied.applied_load_csv("fuselage", ...)`` and the LRA deck's
    cards -- both LIMIT too, since note 49 OR-116.

    ``Sz``/``Myy`` are the cantilever's running loads, positive for an up load
    (note 64 D-64.4), and are **blank on a box row**: a station at or between
    the spars is an applied load the box reacts, not a point of either
    integration (D-64.2). ``Region`` names which. ``My_free`` is the couple
    applied at the station -- the wing reaction's, zero elsewhere.
    """
    rows: List[Dict[str, str]] = []
    for r in results:
        for s in r.stations:
            box = s.region == BOX
            rows.append({
                "Case": r.case, "X": f"{s.x:.3f}", "Fz": f"{s.fz:.2f}",
                "My_free": f"{s.couple:.1f}",
                "Sz": "" if box else f"{s.sz:.2f}",
                "Myy": "" if box else f"{s.myy:.1f}",
                "Region": s.region,
                "Basis": "LIMIT",
            })
    return rows


def fitting_load_rows(results: List[BodyLoadResult]) -> List[Dict[str, str]]:
    """One row per condition of the wing-attachment fitting loads (**LIMIT**).

    The front/rear spar reactions -- the static equivalent at the two spars of
    the one reaction the wing post carries (note 64 D-64.5; the same 2x2 as
    Ref 1 p103's) -- the sizing loads for the wing-attach fittings, applied
    nowhere. The reaction itself is stated beside them."""
    rows: List[Dict[str, str]] = []
    for r in results:
        if r.r_front is None or r.r_rear is None:
            continue
        rows.append({
            "Case": r.case,
            "X front": f"{r.x_front:.3f}", "R front": f"{r.r_front:.2f}",
            "X rear": f"{r.x_rear:.3f}", "R rear": f"{r.r_rear:.2f}",
            "X wing": f"{(r.x_wing or 0.0):.3f}", "R wing": f"{(r.r_wing or 0.0):.2f}",
            "M wing": f"{(r.m_wing or 0.0):.1f}",
            "M unbalanced": f"{r.m_unbalanced:.1f}",
            "Spars": "assumed" if r.spars_assumed else "entered",
            "Basis": "LIMIT",
        })
    return rows


def critical_conditions(project: Project) -> List[ConditionResult]:
    """The SELECT-critical fuselage conditions as published results (note 44 OR-108).

    Blocks 1, 2, 3 and 7 of the manual's own **CRITICAL FUSELAGE LOADS** summary
    (Ref 1 p198). ``select_fuselage`` has always computed them; until OR-108 the
    module discarded them, so the oracle GUI's Fuselage Loads page said "Body
    Loads produced no conditions" beside a full station table where the manual
    prints its summary.

    Published here, from the one ``ModuleResult`` every surface already reads,
    rather than by each surface calling ``select_fuselage`` for itself: one
    quantity, one owner, so the GUI, the CLI, ``load_cases_csv`` and the oracle
    report's section 4 cannot show different case sets.

    Blocks 4 and 5 are the pull-up maneuvers, whose quantities belong to the tail
    analysis; they are read from SELECT's own h-tail conditions where they are
    printed (OR-109), never reassembled. Block 6 is the manual's landing advisory.

    All values are **LIMIT** (note 49 OR-116): each condition states the factor
    23.303 prescribes for it and nothing here applies it.
    """
    return [ConditionResult(
        title=f"Critical fuselage load {cond.label} (case {cond.case})",
        far_reference=cond.far_reference,
        values=list(cond.loads),
        safety_factor=cond.safety_factor,
        case_ref=cond.case_ref,
    ) for cond in _critical_fuselage(project)]


def run(project: Project) -> ModuleResult:
    """Run the fuselage net-load distribution.

    The conditions are the p198 critical-fuselage summary
    (:func:`critical_conditions`); the station table behind them is consumed via
    ``build_body_loads`` / the CSV, because no result type carries stations.
    """
    build_body_loads(project)
    return ModuleResult(module=MODULE_NAME,
                        conditions=critical_conditions(project))


register(MODULE_NAME, run)
