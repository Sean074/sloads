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
the thrust are reacted by the closure (their ``q_dot``/``r_dot``/``n_x``); the
thrust makes the case :func:`~sloads.modules.balance.queries.is_powered`, the
standing exemption from the trim residual gate.

EM cases are **per engine and never mirrored**: ENGLOADS computes every engine
and every gyroscopic sign combination, so a reflected twin would be a second
copy of a case already delivered. They are appended after the ground families
(D-66.2) so every shipped deck's subcase sequence is untouched, and the
conditions not assembled are recorded (D-66.3): 23.363 and 23.361(b)(1) are
mount-local by the owner's ruling (note 66 Q1).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Optional, Sequence, Tuple

from ...derived_geometry import require_wing_reference
from ...export.coordinates import ThrustLineError, engine_applied_load, engine_thrust_axis
from ...load_keys import (
    FX_THRUST,
    FZ_VERTICAL,
    FZ_VERTICAL_2_5G,
    FZ_VERTICAL_A2,
    MX_MOUNT_TORQUE,
    parse_gyro_key,
)
from ...mass_distribution import CaseLoading
from ...models import (
    BalancedCaseResult,
    BalancedLoad,
    CgCase,
    ConditionResult,
    CriticalCondition,
    MissingInputError,
    Project,
    VnPoint,
)
from .applied import HUB_THRUST_SOURCE
from .closure import _closure, resultant6
from .queries import point_mass_self_inertia
from .skipped import SkippedCondition, _skip

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

#: The couple sources an engine applies, which keep their sense under a
#: reflection (note 21 §4.4, note 66 D-66.7): a mirrored airplane's propeller
#: still turns the same way.
ROTATION_FIXED_SOURCES: Tuple[str, ...] = ("engine-torque", "engine-gyro")

#: The free couple that trims the propeller torque in roll (note 21 P-9).
AILERON_TRIM_SOURCE = "aileron-trim"

#: The 23.371 / 25.371 max-continuous thrust an EM gyroscopic case applies at
#: the hub. Its own source, not the entered hub thrust's (#10,
#: ``HUB_THRUST_SOURCE``): that one is a project input every flight family
#: carries, this one is ENGLOADS's number for one condition.
ENGINE_MOUNT_THRUST_SOURCE = "engine-mount-thrust"

#: ft-lb (ENGLOADS) -> lb-in (the balanced cases).
_IN_PER_FT = 12.0

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


def engine_member(index: int) -> str:
    """The LRA member name of engine ``index`` (1-based): its mount and hub."""
    return f"engine-{index}"


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
    engine-plus-propeller weight -- 0.75 n1, n1, 1 g, 2.5 g or the A2 factor."""
    values = {v.key: v.value for v in cond.values}
    for key in (FZ_VERTICAL, FZ_VERTICAL_2_5G, FZ_VERTICAL_A2):
        if key in values:
            return values[key] / weight_lb if weight_lb else 0.0
    raise ValueError(f"engine condition {cond.far_reference} states no vertical load")


def _increment(project: Project, index: int, eng, cond: ConditionResult,
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
    side = "C" if abs(mount[1]) < 1e-9 else ("R" if mount[1] > 0 else "L")
    member = engine_member(index)
    loads: List[BalancedLoad] = []
    if kind == "torque":
        _, m = engine_applied_load(axis, torque=values.get(MX_MOUNT_TORQUE, 0.0))
        m_in = tuple(c * _IN_PER_FT for c in m)
        loads.append(BalancedLoad(x=mount[0], y=mount[1], z=mount[2],
                                  mx=m_in[0], my=m_in[1], mz=m_in[2],
                                  source="engine-torque", side=side, carrier=member))
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
                                  mx=m[0] * _IN_PER_FT, my=m[1] * _IN_PER_FT,
                                  mz=m[2] * _IN_PER_FT,
                                  source="engine-gyro", side=side, carrier=member))
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
                       sources=None,
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
    except (MissingInputError, ValueError):
        return []

    phaa = next((c for c in critical if c.component == "wing" and c.label == "PHAA"
                 and c.case is not None), None)
    anchor = vn.get(phaa.case) if phaa is not None and phaa.case is not None else None

    out: List[BalancedCaseResult] = []
    # Many engine cases share one parent point (the ATR's 14 share 3): each is
    # assembled once and scaled per case.
    parents: Dict[int, BalancedCaseResult] = {}
    taken = 0
    for index, eng in enumerate(engines, start=1):
        count = len(mount_conditions(eng, include_far25=project.include_far25))
        conditions = delivered[taken:taken + count]
        taken += count
        weight = combined_weight(eng)
        for cond in conditions:
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
            try:
                increment, assumed = _increment(project, index, eng, cond, kind)
            except ThrustLineError:
                record.append(_skip(_EngineCondition(cond), "thrust-line"))
                continue
            target = _target_n(cond, weight)
            if point.case not in parents:
                parents[point.case] = assemble(project, cond.title, point, loading, cg,
                                               sources=sources)
            parent = parents[point.case]
            k = target / parent.nz if parent.nz else 0.0
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
                f"({point.condition}) scaled x{k:.4f} to n = {target:.4f}. The "
                "engine's own inertia is the parent's, at the parent's n -- "
                "ENGLOADS's vertical load is not re-applied.",
                ("Thrust axis ASSUMED airplane-forward (no thrust line entered)."
                 if assumed else "Thrust axis: the entered thrust line."),
            ]
            if kind == "torque":
                notes.append("The propeller torque is trimmed by an equal and "
                             "opposite aileron couple at the wing aerodynamic "
                             "centre (note 21 P-9).")
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

