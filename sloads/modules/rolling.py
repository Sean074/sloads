"""The FAR 23.349 rolling conditions arrive complete -- design note 52.

The roll physics already lived in WINGINER (the unit-roll distribution) and
SELECT (the ACRL and TORS picks); what was missing was the delivery. This
module holds the note's **owners** (``CONVENTIONS.md`` §7), each the one place
its quantity is made:

* :func:`condition_a_point` -- the air point of the delivered ACRL semispan
  (D-52.10). 23.349(a) modifies symmetric **condition A** -- the stall line at
  the limit load factor, FLTLOADS's ``STALL +N`` corner -- 100 % on the
  governing side; the AC ROLL point SELECT picks is balanced at the
  *airplane-average* factor ``(100 + p)/200 * n1`` and so carries the average
  of the two sides' lift. The 100 % side's air load is condition A's at the
  picked point's weight, altitude, CG and configuration; the inertia is the
  AC ROLL point's own (the airplane-average factor is the acceleration the
  airplane feels).
* :func:`accel_roll_unbalanced_moment` -- ``UNB = -(1 - p/100) * condition A
  root Mxx`` (D-52.2, Ref 1 Ch 12 p. 92, Ch 13 pp. 95-96). The unbalanced
  rolling moment is derived from the condition A air load and the other-side
  percentage; no aileron geometry enters it (Ref 1 Ch 16 computes aileron
  *surface* loads only). Negative in WINGINER's sense: the printed case 160
  enters ``UNB -149,043`` against a ``+514,475`` root (Appendix A pp. 212, 219).
* :func:`steady_roll_deflection` -- the CAM 3.222 down-aileron schedule at a
  steady-roll point (SELECT.BAS 3372-3465), shared by SELECT's torsion proxy
  and the applied TORS ``Δcm`` increment (D-52.5) so the selected and applied
  deflection are one number.
* :func:`complete_rolling_case` -- a wing case of a rolling slot filled from
  the owners: an **entered** value always wins (the 2026-08-13 ruling), a
  blank one is derived.

The percentage itself is :func:`sloads.constants.other_side_percent`
(D-52.1/D-52.11): 75 % flat under Amdt 23-48, acrobatic refused by name.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple

from ..cg_cases import max_takeoff_weight
from ..constants import IN_PER_FT, G, other_side_percent
from ..derived_geometry import wing_plane
from ..models import AeroSurfaceInput, MissingInputError, Project, VnPoint, WingLoadCase
from .airloads import _interp_yv, air_load_distribution

__all__ = [
    "ACCEL_ROLL_SLOTS",
    "CONDITION_A",
    "STEADY_ROLL_SLOTS",
    "RollDerivation",
    "accel_roll_unbalanced_moment",
    "aileron_cm_increment",
    "complete_rolling_case",
    "condition_a_point",
    "condition_a_root_mxx",
    "derive_accel_roll",
    "roll_acceleration",
    "roll_other_side_percent",
    "steady_roll_aero",
    "steady_roll_deflection",
    "steady_roll_schedule",
]

#: The wing slot of the 23.349(a) accelerated roll -- the one condition whose
#: inertia carries an unbalanced rolling moment.
ACCEL_ROLL_SLOTS: Tuple[str, ...] = ("ACRL",)

#: The wing slot of the 23.349(b) steady roll -- the one condition whose air
#: load carries the aileron ``Δcm`` increment (D-52.5).
STEADY_ROLL_SLOTS: Tuple[str, ...] = ("TORS",)

#: FLTLOADS's name for symmetric condition A: the positive stall line at the
#: limit load factor (23.333(d)), *not* the point at VA (Ref 1 Ch 12 p. 92).
CONDITION_A = "STALL +N"

#: The steady-roll conditions FLTLOADS balances, by the speed they sit at.
_STEADY_ROLL = {"ST ROL A": "A", "ST ROL C": "C", "ST ROL D": "D"}

#: WINGINER's gravitational constant in in/s^2: ``theta_ddot = UNB*g/Iwxx``
#: (WINGINER.BAS 1350-1610; the print used 386).
_G_IN_S2 = G * IN_PER_FT


def roll_other_side_percent(project: Project) -> float:
    """The project's 23.349(a) other-side percentage ``p`` -- the one owner
    (:func:`sloads.constants.other_side_percent`) at the design maximum weight
    (D-52.8) and the project's category (D-52.7/D-52.13 refuse acrobatic)."""
    category = project.speeds.category if project.speeds is not None else "N"
    return other_side_percent(max_takeoff_weight(project, required=False) or 0.0, category)


def condition_a_point(vn: Iterable[VnPoint], pick: VnPoint) -> VnPoint:
    """Symmetric condition A at ``pick``'s weight, altitude, CG and
    configuration -- the delivered ACRL semispan's air point (D-52.10).

    FLTLOADS balances ``STALL +N`` in the same config/CG/altitude block as the
    ``AC ROLL`` point it then flies at that corner's speed, so the pair is one
    lookup. A matrix without it is a defect in what was persisted and is
    refused by name, never replaced by the roll point's averaged lift.
    """
    for p in vn:
        if (p.condition == CONDITION_A and p.cg == pick.cg and p.config == pick.config
                and p.altitude_ft == pick.altitude_ft):
            return p
    raise MissingInputError(
        f"the accelerated-roll point V-n case {pick.case} ({pick.condition}, {pick.cg}, "
        f"{pick.altitude_ft:.0f} ft, {pick.config}) has no condition A ({CONDITION_A}) "
        "point beside it -- re-run the flight envelope (FLTLOADS); 23.349(a) builds "
        "the delivered side from condition A (design note 52, D-52.10)")


def condition_a_root_mxx(project: Project, point: VnPoint) -> float:
    """Root air bending (lb-in) of the wing at ``point``'s CL and speed -- the
    AIRLOADS run the unbalanced rolling moment is derived from."""
    wm = project.wing_mass
    surface = wm.surface if wm is not None else "wing"
    geom = project.geometry.by_name(surface) if project.geometry is not None else None
    aero = project.aero.by_name(surface) if project.aero is not None else None
    if geom is None or aero is None:
        raise MissingInputError(
            f"the accelerated-roll unbalanced moment needs the '{surface}' geometry and "
            "aero surfaces (its condition A air load, design note 52 D-52.2)")
    air = air_load_distribution(geom, aero, point.cl, point.v_eas_kt,
                                *wing_plane(project, surface))
    return air.stations[0].mxx


def accel_roll_unbalanced_moment(root_mxx: float, percent: float) -> float:
    """``UNB = -(1 - p/100) * root_mxx`` (D-52.2) -- the **only** producer of a
    derived case's ``unbal_moment`` (G-52.9).

    ``root_mxx`` is condition A's air root bending; the sign is WINGINER's, so
    the inertia it drives relieves the 100 % side (Appendix A p. 219: ``-149,043``
    against ``+514,475`` at the manual's 71.03 %).
    """
    return -(1.0 - percent / 100.0) * root_mxx


def roll_acceleration(unbal_moment: float, iwxx: float) -> float:
    """WINGINER's roll acceleration ``theta_ddot = UNB * g / Iwxx`` (rad/s^2),
    ``Iwxx`` the semispan roll inertia (lb-in^2). Appendix A p. 219 prints
    ``-13.287`` for ``UNB -149,043``."""
    return unbal_moment * _G_IN_S2 / iwxx if iwxx else 0.0


class RollDerivation(NamedTuple):
    """Everything the D-52.4 publication states about one accelerated-roll run."""
    percent: float          # the 23.349(a) other-side percentage p
    cond_a: VnPoint         # condition A at the run's weight/altitude/CG/config
    root_mxx: float         # condition A's air root bending, lb-in
    unbal_moment: float     # the derived UNB, lb-in (WINGINER's sign)


def derive_accel_roll(project: Project, vn: Iterable[VnPoint], pick: VnPoint,
                      percent: Optional[float] = None) -> RollDerivation:
    """Condition A, its root bending and the derived UNB for the AC ROLL
    point ``pick`` -- the one chain the wing cases, the variant table and the
    balanced deck all read (D-52.3)."""
    p = roll_other_side_percent(project) if percent is None else percent
    cond_a = condition_a_point(vn, pick)
    root = condition_a_root_mxx(project, cond_a)
    return RollDerivation(p, cond_a, root, accel_roll_unbalanced_moment(root, p))


def complete_rolling_case(project: Project, case: WingLoadCase,
                          vn: Dict[int, VnPoint]) -> WingLoadCase:
    """``case`` with its accelerated-roll quantities filled from the owners.

    Applies to the :data:`ACCEL_ROLL_SLOTS` alone; every other case is
    returned unchanged. An **entered** ``cl``/``v_eas_kt``/``unbal_moment``
    wins (existing projects keep what they typed); a blank one is derived from
    condition A at the case's V-n point (D-52.2, D-52.10). A case with no V-n
    point to derive from (the C3-before-SELECT bridge) keeps what it has --
    its blank couple is zero, and the report says so in band.
    """
    if case.name not in ACCEL_ROLL_SLOTS:
        return case
    if case.cl is not None and case.v_eas_kt is not None and case.unbal_moment is not None:
        return case
    pick = vn.get(case.case) if case.case is not None else None
    if pick is None:
        return case
    d = derive_accel_roll(project, vn.values(), pick)
    return replace(
        case,
        cl=case.cl if case.cl is not None else d.cond_a.cl,
        v_eas_kt=case.v_eas_kt if case.v_eas_kt is not None else d.cond_a.v_eas_kt,
        unbal_moment=(case.unbal_moment if case.unbal_moment is not None
                      else d.unbal_moment))


# --------------------------------------------------------------------------- #
# The steady roll (23.349(b)): the CAM 3.222 schedule and the Δcm increment
# --------------------------------------------------------------------------- #
def steady_roll_schedule(vn: Iterable[VnPoint], aileron_deg: float
                         ) -> Dict[float, Dict[str, float]]:
    """``{altitude: {"A"|"C"|"D": down deflection deg}}`` -- CAM 3.222: full
    down at VA, ``VA/VC`` of it at VC, half of ``VA/VD`` of it at VD.

    The speeds are each altitude's ``ST ROL A/C/D`` speeds, **last wins**
    across the CG blocks, faithful to SELECT.BAS 3395-3405 (the program
    overwrites ``VA(J)`` as it scans).
    """
    speeds: Dict[float, Dict[str, float]] = {}
    for p in vn:
        tag = _STEADY_ROLL.get(p.condition)
        if tag is not None:
            speeds.setdefault(p.altitude_ft, {})[tag] = p.v_eas_kt
    out: Dict[float, Dict[str, float]] = {}
    for alt, sp in speeds.items():
        va, vc, vd = sp.get("A", 0.0), sp.get("C", 0.0), sp.get("D", 0.0)
        out[alt] = {
            "A": aileron_deg,
            "C": (va / vc * aileron_deg) if vc else 0.0,
            "D": (0.5 * va / vd * aileron_deg) if vd else 0.0,
        }
    return out


def steady_roll_deflection(schedule: Dict[float, Dict[str, float]],
                           point: VnPoint) -> float:
    """The down-aileron deflection (deg) at steady-roll point ``point`` --
    SELECT's own schedule value, which the applied increment also uses."""
    tag = _STEADY_ROLL.get(point.condition)
    if tag is None:
        return 0.0
    return schedule.get(point.altitude_ft, {}).get(tag, 0.0)


def steady_roll_aero(project: Project, aero: AeroSurfaceInput, label: str,
                     point: Optional[VnPoint], vn: Iterable[VnPoint]
                     ) -> AeroSurfaceInput:
    """The aero surface a wing case's **air load** is built from -- ``aero``
    itself, except on the steady roll with the aileron's butt lines entered
    (design note 52, D-52.5).

    23.349(b) modifies the section pitching moment over the aileron portion by
    ``Δcm = -0.01 * δ`` (Ref 1 Ch 12 p. 93), ``δ`` the down deflection at the
    case's own speed -- :func:`steady_roll_deflection`, the value SELECT's
    torsion proxy ranked the point on. **Blank butt lines reduce to exactly
    the printed Appendix A path** (uniform cm, p. 216): the manual's worked
    example skipped its own instruction, and the oracle stays locked on it.
    Wing chain only (WINGINER/NETLOADS and the variant table): the balanced
    deck's TORS is the symmetric trim case, and the increment is antisymmetric
    between the down- and up-going ailerons.
    """
    if label not in STEADY_ROLL_SLOTS or point is None:
        return aero
    ail = project.aileron_loads
    if ail is None or ail.inboard_y_in is None or ail.outboard_y_in is None:
        return aero
    from .select import resolved_full_down_aileron_deg  # lazy: select imports this module

    vn_list = list(vn)
    delta = steady_roll_deflection(
        steady_roll_schedule(vn_list, resolved_full_down_aileron_deg(project)), point)
    wm = project.wing_mass
    geom = (project.geometry.by_name(wm.surface)
            if project.geometry is not None and wm is not None else None)
    tip = geom.leading_edge[-1][1] if geom is not None else max(ail.outboard_y_in, ail.inboard_y_in)
    return replace(aero, section_cm=aileron_cm_increment(
        aero.section_cm, ail.inboard_y_in, ail.outboard_y_in, delta, tip))


def aileron_cm_increment(section_cm: Sequence[Tuple[float, float]],
                         inboard_y: float, outboard_y: float, delta_deg: float,
                         tip_y: float) -> List[Tuple[float, float]]:
    """``section_cm`` with ``Δcm = -0.01 * delta_deg`` added over the aileron
    span ``[inboard_y, outboard_y]`` (23.349(b), Ref 1 Ch 12 p. 93; D-52.5).

    The step is entered the way the manual's flap case enters its own
    (pp. 165-166, ``-.45`` at BL 0/109.279, ``-.03`` at 109.280/201): a
    **double station** at each aileron end, the unmodified value
    :data:`_STEP_IN` outside the boundary and the modified one on it, on the
    same per-station table AIRLOADS interpolates (``airloads._interp_yv``, whose
    reading of the base table this reuses so the shape between the table's own
    stations is unchanged). The root and the tip are always stations of the
    result, so no extrapolated segment can carry the step outside the aileron.
    """
    base = list(section_cm)

    def at(y: float) -> float:
        return _interp_yv(base, y)

    inb, outb = sorted((inboard_y, outboard_y))
    dcm = -0.01 * delta_deg
    ys = sorted({float(y) for y, _ in base} | {0.0, float(tip_y)})
    rows: List[Tuple[float, float]] = [(y, at(y)) for y in ys if y < inb - _STEP_IN]
    if inb - _STEP_IN >= 0.0:
        rows.append((inb - _STEP_IN, at(inb - _STEP_IN)))
    rows.append((inb, at(inb) + dcm))
    rows += [(y, at(y) + dcm) for y in ys if inb < y < outb]
    rows.append((outb, at(outb) + dcm))
    if outb + _STEP_IN <= tip_y:
        rows.append((outb + _STEP_IN, at(outb + _STEP_IN)))
        rows += [(y, at(y)) for y in ys if y > outb + _STEP_IN]
    return rows


#: The width of the double station (in): the manual's own 109.279/109.280.
_STEP_IN = 1e-3
