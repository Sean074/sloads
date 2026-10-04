"""The engine-mount conditions as assembled balanced cases (design note 66, #286).

Part of :mod:`sloads.modules.balance`; the subsystem docstring is the
package's. ENGLOADS publishes every 14 CFR 23.361/23.363/23.371 condition as a
mount-local load at the engine's combined CG -- the torque, the gyroscopic
couples, the thrust and a vertical ``n * W`` on the engine alone -- and until
#286 none of them reached the LRA deck, although the deck has had a mount and a
hub node for every engine since note 24 R-9. The regulation pairs most of them
with a flight state of the whole airplane:

* 23.361(a)(1): take-off torque "acting simultaneously with 75 percent of the
  limit loads from flight condition A"; (a)(2): max-continuous torque with
  100 %; (a)(3) and FAR 25.361(a)(3)(i)/(ii): with "1 g level flight loads";
* 23.371(b): the gyroscopic couples, max-continuous thrust and n = 2.5; FAR
  25.371 the same at the A2 load factor.

**The case is a scaled parent plus the engine increment** (D-66.4/D-66.5). The
parent is an assembled flight case at a V-n point in the block of SELECT's
delivered PHAA run (condition A: its own point; 1 g: ``BAL C``; the gyro:
``MAN A``), scaled to the load factor ENGLOADS states for the engine. A closed
balanced set scaled by a constant stays closed, so the parent's air, inertia and
relief scale together and the engine increment is the only new content. The
engine's **vertical is not re-applied**: the engine's mass is already in the
parent's inertia, at the parent's ``n``, and adding ENGLOADS's ``n * W`` at the
mount would count it twice.

**The increment lands on the engine's own nodes** (D-66.6): the couples at the
mount (``engine_cg``), the thrust at the hub (``prop_cg``), each load carrying
``carrier = "engine-<i>"`` so the LRA router puts it on that engine's pair and
not on the nearest node of another. **The propeller torque is trimmed by
aileron** (D-66.7, note 21 P-9): an equal and opposite ``aileron-trim`` free
couple at the wing aerodynamic centre, so the case stays unhanded and in roll
balance, and a counter-rotating pair applies none. The gyroscopic couples and
the thrust are reacted by the closure (their ``q_dot``/``r_dot``/``n_x``), and
the family is exempt from the trim residual gate as itself
(:func:`~sloads.modules.balance.queries.is_engine_mount`). ENGLOADS's thrust
does **not** make the case
:func:`~sloads.modules.balance.queries.is_powered`: that reads the entered hub
thrust (#10) alone, and the "Applied engine thrust" row it drives reports that
input, not the condition's own thrust, which the increment carries.

**A gyroscopic case applies every engine at one airplane state** (D-66.4a,
#319). 23.371(b) is a flight state -- a yaw rate, a pitch rate, n = 2.5 and
max-continuous thrust -- and every engine is in it: each engine's ENGLOADS
thrust at its hub and gyroscopic couples at its mount, at the sub-case with
the same airplane rates -- the same sub-case, whose signs are the rates on
every engine (:data:`~sloads.modules.engine.GYRO_SIGNS`; a counter-rotating
engine's couples come out reversed through its signed
:func:`~sloads.modules.engine.angular_momentum`). Until #319 the case thrust its
own engine alone, and the closure reacted the asymmetric thrust -- 1.75 M
lb-in on the ATR -- with a yaw acceleration nothing in the airplane made. The
ENGLOADS thrust replaces each engine's entered hub thrust, which the parent is
assembled without (#313, :func:`~sloads.modules.balance.hub_thrust_set`'s
``replaced``). The net axial force is reacted by the airplane's longitudinal
inertia and stated in band. The case keeps its own engine's EM id -- the mount
it sizes -- so on a co-rotating installation the left and right engines'
cases of one sign combination are the same airplane state, which each states.
A torque case applies no thrust of its own and keeps every entered thrust.

EM cases are **per engine and never mirrored**: ENGLOADS computes every engine
and every gyroscopic sign combination, so a reflected twin would be a second
copy of a case already delivered. They are appended after the ground families
(D-66.2) so every shipped deck's subcase sequence is untouched, and the
conditions not assembled are recorded (D-66.3): 23.363 and 23.361(b)(1) are
mount-local by the owner's ruling (note 66 Q1).
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Dict, List, Optional, Sequence, Tuple

from ...constants import IN_PER_FT
from ...derived_geometry import require_wing_reference
from ...export.coordinates import ThrustLineError, engine_applied_load, engine_thrust_axis, side_of
from ...load_keys import FX_THRUST, MX_MOUNT_TORQUE, VERTICAL_KEYS, parse_gyro_key
from ...mass_distribution import CaseLoading
from ...models import (
    BalancedCaseResult,
    BalancedLoad,
    CgCase,
    ConditionResult,
    CriticalCondition,
    EngineInput,
    MissingInputError,
    Project,
    VnPoint,
)
from ...units import format_value
from ..wing_inertia import WingCaseSources
from .applied import (
    ENGINE_GYRO_SOURCE,
    ENGINE_TORQUE_SOURCE,
    HUB_THRUST_SOURCE,
    ROTATION_FIXED_SOURCES,
    engine_member,
)
from .closure import _closure, resultant6
from .queries import point_mass_self_inertia
from .skipped import SkippedCondition, _skip, family_refused

#: How each ENGLOADS condition is assembled, by FAR reference (note 66 Q1):
#: ``(parent V-n condition or None for condition A itself, the kind)``.
#: Condition A is SELECT's delivered PHAA run; the others are the point of the
#: same name in PHAA's configuration/CG/altitude block.
EM_BALANCED: Dict[str, Tuple[Optional[str], str]] = {
    "23.361(a)(1)": (None, "torque"),
    "23.361(a)(2)": (None, "torque"),
    "23.361(a)(3)": ("BAL C", "torque"),
    "25.361(a)(3)(i)": ("BAL C", "torque"),
    "25.361(a)(3)(ii)": ("BAL C", "torque"),
    "23.371(b)": ("MAN A", "gyro"),
    "25.371": ("MAN A", "gyro"),
}

#: The conditions the owner ruled mount-local (note 66 Q1): 23.363 "may be
#: assumed to be independent of other flight conditions", and the turbine's
#: sudden stoppage carries no flight state in FAR 23.
EM_MOUNT_LOCAL: Tuple[str, ...] = ("23.363(a)&(b)", "23.361(b)(1)")

#: The free couple that trims the propeller torque in roll (note 21 P-9).
AILERON_TRIM_SOURCE = "aileron-trim"

#: The 23.371 / 25.371 max-continuous thrust an EM gyroscopic case applies at
#: the hub. Its own source, not the entered hub thrust's (#10,
#: ``HUB_THRUST_SOURCE``): that one is a project input every flight family
#: carries, this one is ENGLOADS's number for one condition.
ENGINE_MOUNT_THRUST_SOURCE = "engine-mount-thrust"

__all__ = ["AILERON_TRIM_SOURCE", "EM_BALANCED", "EM_MOUNT_LOCAL", "ENGINE_MOUNT_THRUST_SOURCE",
           "ROTATION_FIXED_SOURCES", "build_engine_cases", "engine_member"]


class _EngineCondition:
    """An ENGLOADS condition wearing the shape :func:`_skip` expects (the
    ``_GroundCondition`` precedent): the deliverable's completeness statement
    reads as one list."""

    def __init__(self, cond: ConditionResult) -> None:
        self.cond = cond

    component = "engine_mount"
    case = None

    @property
    def label(self) -> str:
        # The title an assembled EM case carries as its label, so a condition
        # is named the same whether it was assembled or recorded.
        return self.cond.title


def _scaled(case: BalancedCaseResult, k: float) -> BalancedCaseResult:
    """``case`` with every load, residual and acceleration multiplied by ``k``.

    Masses (``weight_lb``) do not scale -- they are the airplane -- so the
    relief ``-w (n + omega_dot x r)`` scales exactly because ``n`` and
    ``omega_dot`` do. **An entered hub thrust (#10) does not scale either**: it
    is the engine's thrust, not a load-factor quantity. Kept at its value, it
    leaves ``(1 - k)`` of its own resultant unclosed, which the caller closes
    with the engine increment.
    """
    loads = [ld if ld.source == HUB_THRUST_SOURCE
             else replace(ld, fx=ld.fx * k, fy=ld.fy * k, fz=ld.fz * k,
                          mx=ld.mx * k, my=ld.my * k, mz=ld.mz * k)
             for ld in case.loads]
    return replace(
        case, loads=loads, nz=case.nz * k,
        residual_fx=case.residual_fx * k, residual_fy=case.residual_fy * k,
        residual_fz=case.residual_fz * k, residual_mx=case.residual_mx * k,
        residual_my=case.residual_my * k, residual_mz=case.residual_mz * k,
        delta_n=case.delta_n * k, delta_nx=case.delta_nx * k,
        delta_ny=case.delta_ny * k, p_dot=case.p_dot * k,
        q_dot=case.q_dot * k, r_dot=case.r_dot * k,
        unbal_moment=case.unbal_moment * k, fuselage_cm=case.fuselage_cm * k,
        body_axial=case.body_axial * k)


def _target_n(cond: ConditionResult, weight_lb: float) -> float:
    """The load factor ENGLOADS states for the engine: its vertical over the
    engine-plus-propeller weight -- 0.75 n1, n1, 1 g, 2.5 g or the A2 factor.
    ``0`` when the engine carries no weight to state one (the caller records
    the case as unscalable)."""
    values = {v.key: v.value for v in cond.values}
    for key in VERTICAL_KEYS:
        if key in values:
            return values[key] / weight_lb if weight_lb else 0.0
    raise ValueError(f"engine condition {cond.far_reference} states no vertical load")


def _gyro_case(cond: ConditionResult) -> int:
    """The sign combination a split gyroscopic condition carries."""
    return next(p[0] for p in (parse_gyro_key(v.key) for v in cond.values) if p)


def _gyro_partners(index: int, cond: ConditionResult, engines: Sequence[EngineInput],
                   by_engine: Dict[int, List[ConditionResult]],
                   ) -> List[Tuple[int, EngineInput, ConditionResult]]:
    """Every engine's condition at the airplane rates of engine ``index``'s
    gyroscopic ``cond`` (D-66.4a): its own, and each other engine's of the same
    FAR reference and sub-case -- a sub-case's signs are the airplane's rates on
    every engine. An engine with no such condition (not a turboprop)
    contributes nothing."""
    case = _gyro_case(cond)
    out: List[Tuple[int, EngineInput, ConditionResult]] = []
    for j, eng in enumerate(engines, start=1):
        if j == index:
            out.append((j, eng, cond))
            continue
        match = next((c for c in by_engine.get(j, ())
                      if c.far_reference == cond.far_reference and _gyro_case(c) == case), None)
        if match is not None:
            out.append((j, eng, match))
    return out


def _gyro_notes(index: int, partners: Sequence[Tuple[int, EngineInput, ConditionResult]],
                loads: Sequence[BalancedLoad], weight_lb: float) -> List[str]:
    """What a gyroscopic case states about its engines (D-66.4a)."""
    fx = math.fsum(ld.fx for ld in loads if ld.source == ENGINE_MOUNT_THRUST_SOURCE)
    pairs = ", ".join(f"engine {j} {c.title.rsplit('— ', 1)[-1]}" for j, _, c in partners)
    notes = [
        f"GYROSCOPIC (design note 66 D-66.4a): every engine's max-continuous "
        f"thrust and gyroscopic couples at one airplane yaw and pitch rate -- "
        f"{pairs}. The net axial force, {format_value(abs(fx), 'lb')} lb "
        f"({format_value(abs(fx) / weight_lb, 'g')} g), is reacted by the airplane's "
        "longitudinal inertia." if weight_lb else "",
    ]
    from ..engine import angular_momentum

    spins = {angular_momentum(eng) > 0 for _, eng, _ in partners}
    if len(partners) > 1 and len(spins) == 1:
        others = ", ".join(str(j) for j, _, _ in partners if j != index)
        notes.append(
            "Every engine spins the same way, so the case of these rates for "
            f"engine {others} is this same airplane state; both are delivered, "
            "each under the id of the mount it sizes.")
    elif len(partners) > 1:
        notes.append(
            "The engines do not all spin the same way, so their gyroscopic "
            "couples at these rates partly or wholly oppose.")
    return [n for n in notes if n]


def _increment(project: Project, index: int, eng: EngineInput, cond: ConditionResult,
               kind: str) -> Tuple[List[BalancedLoad], bool]:
    """The engine's own loads for ``cond`` and whether the axis was assumed.

    Through :func:`~sloads.export.coordinates.engine_applied_load` -- the one
    owner of the axis resolution (note 21 §2.3) -- with the vertical left out
    (D-66.5). The torque rides at the mount with its P-9 trim couple at the wing
    a.c.; the gyroscopic couples at the mount; the thrust at the hub.
    """
    axis, assumed = engine_thrust_axis(eng)
    values = {v.key: v.value for v in cond.values}
    mount = tuple(float(c) for c in eng.engine_cg)
    hub = tuple(float(c) for c in eng.prop_cg) if any(eng.prop_cg) else mount
    side = side_of(mount[1])
    member = engine_member(index)
    loads: List[BalancedLoad] = []
    if kind == "torque":
        _, m = engine_applied_load(axis, torque=values.get(MX_MOUNT_TORQUE, 0.0))
        m_in = tuple(c * IN_PER_FT for c in m)
        loads.append(BalancedLoad(x=mount[0], y=mount[1], z=mount[2],
                                  mx=m_in[0], my=m_in[1], mz=m_in[2],
                                  source=ENGINE_TORQUE_SOURCE, side=side, carrier=member))
        wr = require_wing_reference(project)
        loads.append(BalancedLoad(x=wr.xw, y=0.0, z=wr.zw, mx=-m_in[0],
                                  source=AILERON_TRIM_SOURCE, side="C"))
    else:
        myy = mzz = 0.0
        for v in cond.values:
            parsed = parse_gyro_key(v.key)
            if parsed is not None:
                if parsed[1] == "myy":
                    myy = v.value
                else:
                    mzz = v.value
        _, m = engine_applied_load(axis, myy=myy, mzz=mzz)
        loads.append(BalancedLoad(x=mount[0], y=mount[1], z=mount[2],
                                  mx=m[0] * IN_PER_FT, my=m[1] * IN_PER_FT,
                                  mz=m[2] * IN_PER_FT,
                                  source=ENGINE_GYRO_SOURCE, side=side, carrier=member))
        f, _ = engine_applied_load(axis, thrust=values.get(FX_THRUST, 0.0))
        loads.append(BalancedLoad(x=hub[0], y=hub[1], z=hub[2],
                                  fx=f[0], fy=f[1], fz=f[2],
                                  source=ENGINE_MOUNT_THRUST_SOURCE, side=side,
                                  carrier=member))
    return loads, assumed


def build_engine_cases(project: Project, critical: Sequence[CriticalCondition],
                       vn: Dict[int, VnPoint], cgs: Dict[str, CgCase],
                       loadings: Dict[str, CaseLoading],
                       skipped: Optional[List[SkippedCondition]] = None,
                       sources: Optional[WingCaseSources] = None,
                       ) -> List[BalancedCaseResult]:
    """The EM family: one balanced case per ENGLOADS condition that pairs with
    a flight state, per engine, in ENGLOADS's own order (note 66 D-66.4).

    Every other ENGLOADS condition is recorded in ``skipped`` with its reason.
    A project with no engine, or whose ENGLOADS cannot run, has none.
    """
    # Imported here: ``air`` imports this module to append the family, and the
    # engine module reaches back into the model layer this package sits on.
    from ..engine import combined_weight, mount_conditions, resolved_engines
    from ..engine import run as engine_run
    from .air import assemble

    record: List[SkippedCondition] = skipped if skipped is not None else []
    if not project.engines:
        return []
    try:
        engines = resolved_engines(project)
        delivered = engine_run(project).conditions
    except MissingInputError:   # refusal: the chain does not exist -- no family to state
        return []
    except ValueError as exc:   # refusal: recorded, not swallowed into an empty family (#344)
        record.append(family_refused("engine", "ENGINE MOUNT cases", exc))
        return []

    phaa = next((c for c in critical if c.component == "wing" and c.label == "PHAA"
                 and c.case is not None), None)
    anchor = vn.get(phaa.case) if phaa is not None and phaa.case is not None else None

    out: List[BalancedCaseResult] = []
    # Many engine cases share one parent point (the ATR's 14 share 3): each is
    # assembled once per set of replaced entered thrusts (#313) and scaled per
    # case.
    parents: Dict[Tuple[int, Tuple[str, ...]], BalancedCaseResult] = {}
    by_engine: Dict[int, List[ConditionResult]] = {}
    taken = 0
    for index, eng in enumerate(engines, start=1):
        count = len(mount_conditions(eng, include_far25=project.include_far25))
        by_engine[index] = list(delivered[taken:taken + count])
        taken += count
    for index, eng in enumerate(engines, start=1):
        weight = combined_weight(eng)
        for cond in by_engine[index]:
            rule = EM_BALANCED.get(cond.far_reference)
            if rule is None:
                record.append(_skip(_EngineCondition(cond), "mount-local"))
                continue
            parent_name, kind = rule
            point = anchor
            if anchor is not None and parent_name is not None:
                point = next((p for p in vn.values()
                              if p.condition == parent_name and p.cg == anchor.cg
                              and p.config == anchor.config
                              and p.altitude_ft == anchor.altitude_ft), None)
            if point is None:
                record.append(_skip(_EngineCondition(cond), "no-parent"))
                continue
            cg, loading = cgs.get(point.cg), loadings.get(point.cg)
            if cg is None or loading is None:
                record.append(_skip(_EngineCondition(cond), "no-cg-case"))
                continue
            if not loading.derivable:
                record.append(_skip(_EngineCondition(cond), "loading-not-derivable"))
                continue
            partners = (_gyro_partners(index, cond, engines, by_engine)
                        if kind == "gyro" else [(index, eng, cond)])
            try:
                increment: List[BalancedLoad] = []
                assumed = False
                for j, eng_j, cond_j in partners:
                    loads_j, assumed_j = _increment(project, j, eng_j, cond_j, kind)
                    increment += loads_j
                    assumed = assumed or assumed_j
            except ThrustLineError:
                record.append(_skip(_EngineCondition(cond), "thrust-line"))
                continue
            target = _target_n(cond, weight)
            replaced = (tuple(engine_member(j) for j, _, _ in partners)
                        if kind == "gyro" else ())
            if (point.case, replaced) not in parents:
                parents[point.case, replaced] = assemble(
                    project, cond.title, point, loading, cg, sources=sources,
                    thrust_replaced=replaced)
            parent = parents[point.case, replaced]
            if not target or not parent.nz:
                # A zero scale would ship a case of no load (#321).
                record.append(_skip(_EngineCondition(cond), "unscalable"))
                continue
            k = target / parent.nz
            case = _scaled(parent, k)
            loads = list(case.loads) + increment
            ref = (cg.xcg, 0.0, cg.zcg)
            # What the scaled parent leaves open (only an entered hub thrust's
            # unscaled share) plus the engine increment -- closed together.
            inc = resultant6(loads, ref)
            n = omega = (0.0, 0.0, 0.0)
            if any(abs(c) > 1e-9 for c in inc):
                n, omega, _ = _closure(loads, cg, inc,
                                       point_mass_self_inertia(loading, project))
            notes = list(case.notes) + [
                f"ENGINE MOUNT (design note 66): engine {index}, "
                f"{cond.far_reference}, on the V-n point {point.case} "
                f"({point.condition}) scaled x{format_value(k)} to n = {format_value(target, 'g')}. The "
                "engine's own inertia is the parent's, at the parent's n -- "
                "ENGLOADS's vertical load is not re-applied.",
                ("Thrust axis ASSUMED airplane-forward (no thrust line entered)."
                 if assumed else "Thrust axis: the entered thrust line."),
            ]
            if kind == "torque":
                notes.append("The propeller torque is trimmed by an equal and "
                             "opposite aileron couple at the wing aerodynamic "
                             "centre (note 21 P-9).")
            else:
                notes += _gyro_notes(index, partners, increment, case.weight_lb)
            out.append(replace(
                case, label=cond.title, loads=loads, hand="",
                case_ref=cond.case_ref, notes=notes,
                residual_fx=case.residual_fx + inc[0], residual_fy=case.residual_fy + inc[1],
                residual_fz=case.residual_fz + inc[2], residual_mx=case.residual_mx + inc[3],
                residual_my=case.residual_my + inc[4], residual_mz=case.residual_mz + inc[5],
                delta_nx=case.delta_nx + n[0], delta_ny=case.delta_ny + n[1],
                delta_n=case.delta_n + n[2], p_dot=case.p_dot + omega[0],
                q_dot=case.q_dot + omega[1], r_dot=case.r_dot + omega[2]))
    return out

