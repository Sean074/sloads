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
  large. **The windmill drag is the failed engine's own when entered**
  (``EngineInput.windmill_drag_cd``, D-66.12a, #319), else ONENGOUT's Glauert
  term, which the manual calls the most it can be -- delivered as that bound
  and stated so in band. The march, and so the fin load, always uses the bound;
  with an entered coefficient the closure's yaw differs from the march's by
  the drag difference times the arm, and the case says so;
* **no L-7 term** (D-66.15): ONENGOUT's angle is a yaw angle, not a sideslip.

One engine's failure is computed per speed; the mirrored engine's is its
**reflected twin under its own id** (D-66.13, the ``LG-19``/``LG-20``
precedent), valid on a mirror-symmetric installation and computed on its own
otherwise. A case that did not recover (OR-174) is recorded, not assembled.
The 23.367(a)(2) cases state ``ULT SF=1.0`` through the D-66.1 stamp.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Set, Tuple

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
from ...units import format_value
from .applied import engine_member
from .skipped import SkippedCondition, _skip, family_refused

if TYPE_CHECKING:
    from ..one_engine_out import VtailCase
    from ..wing_inertia import WingCaseSources

#: The 1 g parent point of each ONENGOUT speed case, by its label's speed.
#: The low end -- VMC when entered, else VS standing in for it (#333) -- is
#: assembled on the 1 g stall point either way: the nearest 1 g flight state of
#: the airplane at low speed that the V-n set carries.
OEI_PARENT: Dict[str, str] = {"VC": "BAL C", "VD": "BAL D", "VS": "STALL 1G",
                              "VMC": "STALL 1G"}

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

#: A mirrored engine's lateral arm matches within this length (in) ...
_MIRROR_ARM_TOL_IN = 1e-6
#: ... and its march's peak fin load within this fraction of the load.
_MIRROR_LOAD_REL = 1e-6
#: The propeller hub's butt line matches the engine's (the march's arm) within
#: this length (in); a hub off the arm cannot carry the march's engine pair.
_HUB_ARM_TOL_IN = 1e-6

__all__ = ["ENGINE_OUT_PREFIX", "OEI_FAILED_ENGINE_SOURCE", "OEI_L7_NOTE",
           "OEI_LIVE_THRUST_SOURCE", "OEI_PARENT", "build_engine_out_cases",
           "is_engine_out_condition", "oei_parent_point", "speed_label_of"]


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


def oei_parent_point(project: Project, speed_label: str, altitude_ft: float,
                     vn_points: Sequence[VnPoint], cgs: Dict[str, CgCase],
                     loadings: Dict[str, CaseLoading],
                     ) -> Tuple[Optional[VnPoint], Optional[CgCase]]:
    """The 1 g V-n point a one-engine-out case is assembled on (D-66.11).

    **The one owner of the pairing** (design note 51 D-51.1a): the balanced
    deck assembles the case on this point, and ``tail_span`` pairs the same
    case's T-tail transfer with it, so the fin view and the deck cannot put
    one transient on two different flight states. ``speed_label`` is the
    ONENGOUT case's (``"VC (ultimate)"``...), mapped by :data:`OEI_PARENT`;
    the point is that parent condition at the heaviest FLIGHT CG case with a
    derivable loading (ONENGOUT's own mass basis) and at the balanced altitude
    nearest ``altitude_ft``. ``(None, cg)`` -- or ``(None, None)`` with no
    usable loading -- when no parent resolves; the deck records that as
    ``no-parent``.
    """
    cg = _heaviest_derivable(project, loadings, cgs)
    parent_name = _parent_name(speed_label)
    if parent_name is None or cg is None:
        return None, cg
    candidates = [p for p in vn_points
                  if p.condition == parent_name and p.cg == cg.name]
    if not candidates:
        return None, cg
    return _nearest_altitude(candidates, altitude_ft), cg


def speed_label_of(cond: CriticalCondition) -> str:
    """The ONENGOUT speed label inside a 23.367 fin condition's label --
    ``"VC (ultimate) (engine 1)"`` from ``"ONE ENGINE OUT — VC (ultimate)
    (engine 1)"`` -- which :data:`OEI_PARENT` is keyed by the start of."""
    return cond.label[len(ENGINE_OUT_PREFIX):].lstrip(" —-")


def _heaviest_derivable(project: Project, loadings: Dict[str, CaseLoading],
                        cgs: Dict[str, CgCase]) -> Optional[CgCase]:
    """ONENGOUT's own mass basis (:func:`~sloads.modules.one_engine_out.mass_basis`,
    #333 ruling 4), so the deck assembles the case on the CG case the march
    took its IZZ and CG from -- one airplane state, not two."""
    from ..one_engine_out import mass_basis

    basis = mass_basis(project, loadings)
    return cgs.get(basis[0].name) if basis is not None else None


def unrecovered_detail(fc: "VtailCase") -> str:
    """What an unrecovered case reached, so its record is a statement rather
    than an absence (#333 ruling 2): its speed and altitude, and the fin
    incidence when the march stopped. KEAS, ft and deg only -- the deck's
    record carries it into the SI deck as written. The validation warning
    adds the fin load in its own units."""
    c = fc.inputs
    return (f" ({format_value(c.v_kt, 'kt')} KEAS at {format_value(c.alt_ft, 'ft')} ft, "
            f"{format_value(fc.vtail_alpha_deg, 'deg')} deg fin incidence at the "
            f"{format_value(fc.summary.time_to_recovery_s, 's')} s bound)")


def _nearest_altitude(points: Sequence[VnPoint], altitude_ft: float) -> VnPoint:
    """The point balanced at the altitude nearest ``altitude_ft`` (ties: the
    first, through :func:`~sloads.picks.extreme`)."""
    def gap(p: VnPoint) -> float:
        return abs(p.altitude_ft - altitude_ft)
    return extreme(points, gap, largest=False)


def _thrust_replaced(project: Project) -> Tuple[str, ...]:
    """Every engine whose entered thrust the case leaves out (#313).

    ONENGOUT models the airplane as a twin -- the failed engine and a live one
    at its mirror -- so :func:`_engine_pair` is the case's whole thrust state,
    and an entered hub thrust beside it would give the live engine two thrusts
    and the dead one a thrust it no longer makes.
    """
    return tuple(engine_member(i) for i in range(1, len(project.engines or []) + 1))


def _hub(eng) -> Tuple[float, float, float]:
    """The failed engine's hub: the propeller CG, else the engine CG."""
    x, y, z = eng.prop_cg if any(eng.prop_cg) else eng.engine_cg
    return float(x), float(y), float(z)


def _windmill_note(project: Project, fc: "VtailCase") -> str:
    """What the failed hub's drag is, stated per case (D-66.12a)."""
    from ..engine import resolved_engines
    from ..one_engine_out import GLAUERT_DISC_CD_BOUND, entered_windmill_cd

    cd = entered_windmill_cd(resolved_engines(project)[fc.engine_index], fc.engine_index)
    bound_cd = GLAUERT_DISC_CD_BOUND
    if cd is None:
        return ("WINDMILL DRAG (design note 66 D-66.12a): the failed engine's "
                "windmilling drag at its hub is the upper bound of the method, the "
                f"Glauert disc drag coefficient {format_value(bound_cd)} (manual Ch 11 p88: the "
                "drag \"can not be more than\" this), delivered as a conservative "
                "bound on the mount and hub loads. Enter the propeller's own "
                "windmilling disc drag coefficient to deliver its own drag.")
    return ("WINDMILL DRAG (design note 66 D-66.12a): the failed engine's "
            "windmilling drag at its hub is its entered disc drag coefficient "
            f"{format_value(cd)}, on the transient's own ramp. The fin load "
            f"is the one-engine-out march's, forced by the bound ({format_value(bound_cd)}), "
            "so the yaw this case closes with differs from the march's by the "
            "drag difference times the engine arm.")


def _engine_pair(project: Project, fc: "VtailCase") -> List[BalancedLoad]:
    """The engine loads at the peak instant, at the hubs (D-66.12, D-66.12a)."""
    from ..engine import resolved_engines
    from ..one_engine_out import engine_forces_at, entered_windmill_cd

    eng = resolved_engines(project)[fc.engine_index]
    hub = _hub(eng)
    live, remaining, windmill = engine_forces_at(
        fc.peak.time, fc.inputs, windmill_cd=entered_windmill_cd(eng, fc.engine_index))
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
                           sources: Optional["WingCaseSources"] = None,
                           ) -> List[BalancedCaseResult]:
    """The one-engine-out family, per speed: one computed case and its
    reflected twin (note 66 D-66.10…D-66.16). ``conditions`` are SELECT's
    23.367 conditions; ``vtails`` the fin distributions by label."""
    from ..engine import resolved_engines
    from ..one_engine_out import entered_windmill_cd, vtail_cases
    from .air import assemble, handed_twin

    record: List[SkippedCondition] = skipped if skipped is not None else []
    by_label = {c.label: c for c in conditions}
    try:
        marches = vtail_cases(project)
    except MissingInputError:   # refusal: no 23.367 condition (absent slice, or not applicable)
        return []
    except ValueError as exc:   # refusal: recorded, not swallowed into an empty family (#344)
        record.append(family_refused("vtail", f"{ENGINE_OUT_PREFIX} cases", exc))
        return []
    for fc in marches:
        if not fc.recovered:
            record.append(_skip(_MarchCondition(f"{ENGINE_OUT_PREFIX} — "
                                                f"{fc.load_case.label}{fc.engine_label}"),
                                "not-recovered", unrecovered_detail(fc)))
    out: List[BalancedCaseResult] = []
    done: Set[str] = set()
    engines = resolved_engines(project)
    # Refused here, outside the march's ``except`` above and before any case is
    # skipped, so a coefficient that cannot be right stops the family by name
    # rather than vanishing with it or riding only the cases that assemble (#343).
    for fc in marches:
        entered_windmill_cd(engines[fc.engine_index], fc.engine_index)
    for fc in marches:
        label = f"{ENGINE_OUT_PREFIX} — {fc.load_case.label}{fc.engine_label}"
        cond = by_label.get(label)
        if cond is None or label in done:
            continue
        # The march's arm is the engine's butt line; the pair lands at the hub.
        # A hub off that line would carry a yaw the march never had (#321).
        if abs(_hub(engines[fc.engine_index])[1] - fc.inputs.bleng * fc.sense) > _HUB_ARM_TOL_IN:
            record.append(_skip(cond, "hub-off-arm"))
            continue
        point, cg = oei_parent_point(project, fc.load_case.label, fc.inputs.alt_ft,
                                     list(vn.values()), cgs, loadings)
        if point is None or cg is None:
            record.append(_skip(cond, "no-parent"))
            continue
        lateral = vtails.get(label, ())
        if not lateral:
            record.append(_skip(cond, "no-fin-loads"))
            continue
        case = assemble(project, label, point, loadings[cg.name], cg,
                        case_ref=cond.case_ref, lateral=lateral,
                        extra=_engine_pair(project, fc), sources=sources,
                        thrust_replaced=_thrust_replaced(project))
        hand = "R" if fc.sense > 0 else "L"      # the failed engine's side
        case = replace(case, case_ref=cond.case_ref, hand=hand,
                       notes=list(case.notes) + [
                           OEI_L7_NOTE,
                           _windmill_note(project, fc),
                           f"The instant of peak total fin load, t = {format_value(fc.peak.time, 's')} s "
                           f"(ONENGOUT OR-175), on the 1 g point {point.case} "
                           f"({point.condition}, {point.cg}, {format_value(point.altitude_ft, 'ft')} ft) "
                           f"against ONENGOUT's {format_value(fc.inputs.alt_ft, 'ft')} ft; the live "
                           "engine's thrust and the failed engine's remaining thrust "
                           "and windmill drag at that instant are applied at the hubs."])
        out.append(case)
        done.add(label)
        twin = _mirror_of(fc, marches, by_label, engines)
        if twin is not None:
            out.append(replace(handed_twin(case, case_ref=twin.case_ref),
                               label=twin.label))
            done.add(twin.label)
    return out


def _mirror_of(fc: "VtailCase", marches: Sequence["VtailCase"],
               by_label: Dict[str, CriticalCondition],
               engines: Sequence[Any]) -> Optional[CriticalCondition]:
    """The other engine's condition at the same speed, when its march is the
    mirror image of ``fc``'s -- the case :func:`handed_twin` reproduces. The
    two engines' entered windmill drag coefficients must agree too (D-66.12a):
    the twin reflects the failed hub's drag, not recomputes it."""
    from ..one_engine_out import entered_windmill_cd

    for other in marches:
        if other is fc or other.load_case.label != fc.load_case.label:
            continue
        if (other.sense == -fc.sense and other.recovered
                and abs(other.inputs.bleng - fc.inputs.bleng) <= _MIRROR_ARM_TOL_IN
                and abs(other.summary.max_tail_load_lb - fc.summary.max_tail_load_lb)
                <= _MIRROR_LOAD_REL * max(1.0, fc.summary.max_tail_load_lb)
                and entered_windmill_cd(engines[other.engine_index], other.engine_index)
                == entered_windmill_cd(engines[fc.engine_index], fc.engine_index)):
            return by_label.get(f"{ENGINE_OUT_PREFIX} — {other.load_case.label}{other.engine_label}")
    return None
