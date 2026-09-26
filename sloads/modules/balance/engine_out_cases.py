"""The one-engine-out fin conditions as assembled balanced cases (design note 66, #285).

Part of :mod:`sloads.modules.balance`; the subsystem docstring is the
package's. ONENGOUT marches a twin's yaw transient after one engine fails
(14 CFR 23.367) and SELECT names its peak as a fin condition -- on a
wing-mounted twin the largest fin load the airplane sees (3.6x the ATR's
largest static fin case). Until #285 none reached a solver deck: plan 13 §4
kept "a transient" out of the balanced families, and the per-component fin
deck the deferral rested on was deleted by note 56 D-56.2.

**The transient is not re-run; its governing instant is assembled** (D-66.10):
the instant of peak total fin load ONENGOUT already names (OR-175), taken
quasi-statically, which is what every other fin condition is. Each case is

* a **1 g parent** (D-66.11) -- FLTLOADS's ``BAL C`` / ``BAL D`` /
  ``STALL 1G`` for the VC / VD / VS case, at the heaviest FLIGHT CG case with
  a derivable loading and the V-n altitude nearest ONENGOUT's;
* the **fin distribution** at the peak, the one ``tail_span`` already builds
  for the condition (the B8a-3 lateral machinery);
* the **engine pair** at that instant (D-66.12) -- the live engine's thrust
  at the mirror of the failed hub (ONENGOUT's own arm) and the failed engine's
  remaining thrust and windmill drag at its hub, from
  :func:`sloads.modules.one_engine_out.engine_forces_at`, the schedule the
  march turned into its yawing moment. With them the closure's yaw is the
  march's (fin moment less engine moment), not a fin-only yaw about twice as
  large;
* **no L-7 term** (D-66.15): ONENGOUT's angle is a yaw angle, not a sideslip.

One engine's failure is computed per speed; the mirrored engine's is its
**reflected twin under its own id** (D-66.13, the ``LG-19``/``LG-20``
precedent), valid on a mirror-symmetric installation and computed on its own
otherwise. A case that did not recover (OR-174) is recorded, not assembled.
The 23.367(a)(2) cases state ``ULT SF=1.0`` through the D-66.1 stamp.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Optional, Sequence

from ...cg_cases import flight_cases
from ...mass_distribution import CaseLoading
from ...models import (
    BalancedCaseResult,
    BalancedLoad,
    CgCase,
    CriticalCondition,
    MissingInputError,
    Project,
    VnPoint,
)
from ...picks import extreme
from .skipped import SkippedCondition, _skip

#: The 1 g parent point of each ONENGOUT speed case, by its label's speed.
OEI_PARENT: Dict[str, str] = {"VC": "BAL C", "VD": "BAL D", "VS": "STALL 1G"}

#: The label prefix SELECT gives an ONENGOUT fin condition.
ENGINE_OUT_PREFIX = "ONE ENGINE OUT"

#: The sources of the engine pair a one-engine-out case applies (its own, not
#: the entered hub thrust's): the live engine's thrust and the failed engine's
#: remaining thrust plus windmill drag.
OEI_LIVE_THRUST_SOURCE = "engine-out-live-thrust"
OEI_FAILED_ENGINE_SOURCE = "engine-out-failed-engine"

#: The statement every one-engine-out case carries in band (D-66.15).
OEI_L7_NOTE = (
    "ONE ENGINE OUT (design note 66): the wing-body side force of L-7 is NOT "
    "estimated for this case -- the transient's angle is a yaw angle, not a "
    "sideslip, and no fin stability derivatives are published for it.")

_MIRROR_TOL = 1e-6

__all__ = ["ENGINE_OUT_PREFIX", "OEI_FAILED_ENGINE_SOURCE", "OEI_L7_NOTE",
           "OEI_LIVE_THRUST_SOURCE", "OEI_PARENT", "build_engine_out_cases",
           "is_engine_out_condition"]


def is_engine_out_condition(cond: CriticalCondition) -> bool:
    """Is this SELECT condition one of ONENGOUT's 23.367 fin conditions?"""
    return cond.component == "vtail" and cond.label.startswith(ENGINE_OUT_PREFIX)


class _MarchCondition:
    """An unrecovered ONENGOUT case wearing the shape :func:`_skip` expects --
    it never reaches SELECT's set (OR-174), so the record is the only place the
    deck can state it."""

    component = "vtail"
    case = None

    def __init__(self, title: str) -> None:
        self.label = title


def _parent_name(label: str) -> Optional[str]:
    return next((p for k, p in OEI_PARENT.items() if label.startswith(k)), None)


def _heaviest_derivable(project: Project, loadings: Dict[str, CaseLoading],
                        cgs: Dict[str, CgCase]) -> Optional[CgCase]:
    """The heaviest FLIGHT CG case whose loading the database can produce --
    ONENGOUT's own mass basis (its Izz is the heaviest mass case's)."""
    usable = [c for c in flight_cases(project)
              if c.name in cgs and loadings.get(c.name) is not None
              and loadings[c.name].derivable]
    return extreme(usable, lambda c: c.weight_lb) if usable else None


def _nearest_altitude(points: Sequence[VnPoint], altitude_ft: float) -> VnPoint:
    """The point balanced at the altitude nearest ``altitude_ft`` (ties: the
    first, through :func:`~sloads.picks.extreme`)."""
    def gap(p: VnPoint) -> float:
        return abs(p.altitude_ft - altitude_ft)
    return extreme(points, gap, largest=False)


def _engine_pair(project: Project, fc) -> List[BalancedLoad]:
    """The engine loads at the peak instant, at the hubs (D-66.12)."""
    from ..engine import resolved_engines
    from ..one_engine_out import engine_forces_at

    eng = resolved_engines(project)[fc.engine_index]
    hub = tuple(float(v) for v in (eng.prop_cg if any(eng.prop_cg) else eng.engine_cg))
    live, remaining, windmill = engine_forces_at(fc.peak.time, fc.inputs)
    side = "R" if hub[1] > 0 else "L"
    other = "L" if side == "R" else "R"
    return [
        # The live engine: full thrust, forward (-x), at the mirror of the failed
        # hub -- the arm ONENGOUT's moment is built on.
        BalancedLoad(x=hub[0], y=-hub[1], z=hub[2], fx=-live,
                     source=OEI_LIVE_THRUST_SOURCE, side=other),
        # The failed engine: what thrust it still gives, less its windmill drag.
        BalancedLoad(x=hub[0], y=hub[1], z=hub[2], fx=-remaining + windmill,
                     source=OEI_FAILED_ENGINE_SOURCE, side=side),
    ]


def build_engine_out_cases(project: Project, conditions: Sequence[CriticalCondition],
                           vn: Dict[int, VnPoint], cgs: Dict[str, CgCase],
                           loadings: Dict[str, CaseLoading], vtails: Dict[str, Sequence],
                           skipped: Optional[List[SkippedCondition]] = None,
                           sources=None,
                           ) -> List[BalancedCaseResult]:
    """The one-engine-out family, per speed: one computed case and its
    reflected twin (note 66 D-66.10…D-66.16). ``conditions`` are SELECT's
    23.367 conditions; ``vtails`` the fin distributions by label."""
    from ..one_engine_out import vtail_cases
    from .air import assemble, handed_twin

    record: List[SkippedCondition] = skipped if skipped is not None else []
    by_label = {c.label: c for c in conditions}
    try:
        marches = vtail_cases(project)
    except (MissingInputError, ValueError):   # ONENGOUT refuses: no family
        return []
    for fc in marches:
        if not fc.recovered:
            record.append(_skip(_MarchCondition(f"{ENGINE_OUT_PREFIX} — "
                                                f"{fc.load_case.label}{fc.engine_label}"),
                                "not-recovered"))
    cg = _heaviest_derivable(project, loadings, cgs)

    out: List[BalancedCaseResult] = []
    done: set = set()
    for fc in marches:
        label = f"{ENGINE_OUT_PREFIX} — {fc.load_case.label}{fc.engine_label}"
        cond = by_label.get(label)
        if cond is None or label in done:
            continue
        parent_name = _parent_name(fc.load_case.label)
        point = None
        if parent_name is not None and cg is not None:
            candidates = [p for p in vn.values() if p.condition == parent_name and p.cg == cg.name]
            if candidates:
                point = _nearest_altitude(candidates, fc.inputs.alt_ft)
        if point is None or cg is None:
            record.append(_skip(cond, "no-parent"))
            continue
        lateral = vtails.get(label, ())
        if not lateral:
            record.append(_skip(cond, "no-fin-loads"))
            continue
        case = assemble(project, label, point, loadings[cg.name], cg,
                        case_ref=cond.case_ref, lateral=lateral,
                        extra=_engine_pair(project, fc), sources=sources)
        hand = "R" if fc.sense > 0 else "L"      # the failed engine's side
        case = replace(case, case_ref=cond.case_ref, hand=hand,
                       notes=list(case.notes) + [
                           OEI_L7_NOTE,
                           f"The instant of peak total fin load, t = {fc.peak.time:g} s "
                           f"(ONENGOUT OR-175), on the 1 g point {point.case} "
                           f"({point.condition}, {point.cg}, {point.altitude_ft:.0f} ft) "
                           f"against ONENGOUT's {fc.inputs.alt_ft:.0f} ft; the live "
                           "engine's thrust and the failed engine's remaining thrust "
                           "and windmill drag at that instant are applied at the hubs."])
        out.append(case)
        done.add(label)
        twin = _mirror_of(fc, marches, by_label)
        if twin is not None:
            out.append(replace(handed_twin(case, case_ref=twin.case_ref),
                               label=twin.label))
            done.add(twin.label)
    return out


def _mirror_of(fc, marches, by_label) -> Optional[CriticalCondition]:
    """The other engine's condition at the same speed, when its march is the
    mirror image of ``fc``'s -- the case :func:`handed_twin` reproduces."""
    for other in marches:
        if other is fc or other.load_case.label != fc.load_case.label:
            continue
        if (other.sense == -fc.sense and other.recovered
                and abs(other.inputs.bleng - fc.inputs.bleng) <= _MIRROR_TOL
                and abs(other.summary.max_tail_load_lb - fc.summary.max_tail_load_lb) <= _MIRROR_TOL
                * max(1.0, fc.summary.max_tail_load_lb)):
            return by_label.get(f"{ENGINE_OUT_PREFIX} — {other.load_case.label}{other.engine_label}")
    return None
