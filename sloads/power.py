"""The power state of a flight case -- the single owner (design note 21 §10, #226).

14 CFR 25.321(b): "Critical thrust values in the range from zero to maximum
continuous thrust must be considered." The suite delivers the two ends of that
range (note 21 §10.2a: the balancing tail load is linear in thrust, so no
intermediate thrust lies outside the pair):

* **power off** -- zero thrust, every case the suite has always delivered, and
  the only state McMaster's FLTLOADS knows (Appendix A);
* **power on** -- each flaps-up V-n point re-balanced at the same ``(n, V)``
  (P-10) with every engine at its rated maximum-continuous thrust (P-14), acting
  along the entered thrust line (P-17). Its condition carries the
  :data:`POWER_SUFFIX` (``MAN A-P``, ``PHAA-P``), so a power-off search cannot
  see a power-on point by construction (P-15).

``AeroCoefficientsInput.power_cases`` chooses between ``"off"`` (the default, the
oracle's output) and ``"off_and_on"`` (both sets, P-18). A jet -- an engine with
no ``max_cont_hp`` -- has no P-14 rating, so ``"off_and_on"`` is refused with the
reason (P-19).

The rating (P-14): ``T = eta * P_MC / V_TAS`` per engine, capped by the
momentum-theory static thrust ``(2 rho A (eta P_MC)^2)^(1/3)`` at the point's
density and **not** by the drag -- the pilot may hold full power at any V-n
point. ``eta`` is :data:`~sloads.constants.PROP_EFFICIENCY`. Power is not lapsed
with altitude (a flat-rated turboprop), which the basis statement says.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, NamedTuple, Optional, Tuple

from .constants import (
    FT_LB_S_PER_HP,
    IN_PER_FT,
    KT_TO_FPS,
    PROP_EFFICIENCY,
    RHO_SL,
    standard_atmosphere,
)
from .models import POWER_CASE_CHOICES, MissingInputError
from .units import format_value

if TYPE_CHECKING:
    from .models import CgCase, Project, VnPoint

#: The label suffix of a power-on condition (P-15): ``MAN A`` -> ``MAN A-P``.
POWER_SUFFIX = "-P"

POWER_OFF = "off"
POWER_OFF_AND_ON = "off_and_on"
#: The ``AeroCoefficientsInput.power_cases`` values (P-18), default first --
#: the vocabulary owned beside the dataclass.
POWER_CASES: Tuple[str, ...] = tuple(POWER_CASE_CHOICES)

#: ``VnPoint.power_state`` values.
STATE_OFF = "off"
STATE_ON = "on"

Vec3 = Tuple[float, float, float]


def power_label(label: str) -> str:
    """The power-on twin's label: ``"PHAA"`` -> ``"PHAA-P"``."""
    return label + POWER_SUFFIX


def is_power_on(label: str) -> bool:
    """Whether ``label`` names a power-on condition."""
    return label.endswith(POWER_SUFFIX)


def base_label(label: str) -> str:
    """The condition a label is a twin of: ``"PHAA-P"`` -> ``"PHAA"``; a
    power-off label is returned unchanged. Every family table is keyed on the
    base label, so this is the one place the suffix is stripped."""
    return label[:-len(POWER_SUFFIX)] if is_power_on(label) else label


def power_cases(project: "Project") -> str:
    """The project's ``power_cases`` setting, ``"off"`` when no aero slice;
    a value outside :data:`POWER_CASES` is refused by name (the coded-field
    rule: the consumer refuses, the dataclass stores what was written)."""
    aero = project.aero_coeffs
    value = aero.power_cases if aero is not None else POWER_OFF
    if value not in POWER_CASES:
        raise ValueError(
            f"power_cases {value!r} is not one of "
            + ", ".join(f"{k} = {v}" for k, v in POWER_CASE_CHOICES.items())
            + " -- set it on the Aerodynamic Data page")
    return value


def power_rating_refusal(project: "Project") -> Optional[str]:
    """Why this project cannot rate a power-on case, or ``None`` when it can.

    P-14 needs every engine's maximum-continuous shaft power and propeller
    diameter (the static cap). A jet enters neither, and has no rating (P-19).
    Read from the entered engines, not their resolved mass rows, so a statement
    about power never fails on a mass selector (the run that needs the hubs
    resolves them, :func:`rated_thrusts`)."""
    engines = list(project.engines or [])
    if not engines:
        return ("the project has no engines, so there is no thrust to rate; "
                "set power_cases to 'off'")
    for i, eng in enumerate(engines, start=1):
        if not eng.max_cont_hp:
            return (f"engine {i} enters no max_cont_hp, so it has no rated "
                    f"maximum-continuous thrust (eta*P/V_TAS, 14 CFR 25.321(b)). "
                    f"A jet has no shaft-power rating here (design note 21 P-19); "
                    f"set power_cases to 'off'")
        if not eng.prop_diameter_in:
            return (f"engine {i} enters no prop_diameter_in, so its static "
                    f"thrust cap (momentum theory) cannot be computed")
    return None


def power_on(project: "Project") -> bool:
    """Whether the project's cases include the power-on set, refused by name
    when it asks for them and cannot rate them (P-19)."""
    if power_cases(project) != POWER_OFF_AND_ON:
        return False
    reason = power_rating_refusal(project)
    if reason is not None:
        raise MissingInputError(f"power_cases = 'off_and_on' is refused: {reason}.")
    return True


class EngineThrust(NamedTuple):
    """One engine's rated thrust at a point: its magnitude, where it acts (the
    hub) and the unit vector it acts along (the entered thrust line, P-17)."""
    engine: int
    thrust_lb: float
    hub: Vec3
    axis: Vec3

    @property
    def force(self) -> Vec3:
        """The thrust force in airplane axes (``x`` aft, ``z`` up)."""
        return (self.thrust_lb * self.axis[0], self.thrust_lb * self.axis[1],
                self.thrust_lb * self.axis[2])


def rated_thrusts(project: "Project", v_eas_kt: float, altitude_ft: float) -> List[EngineThrust]:
    """Every engine's P-14 thrust at ``v_eas_kt`` and ``altitude_ft``.

    ``T_e = min(eta * P_e / V_TAS, (2 rho A_e (eta P_e)^2)^(1/3))``, along the
    entered thrust line (``export.coordinates.engine_thrust_axis``; blank is the
    airplane's forward axis) at the hub -- ``prop_cg``, else ``engine_cg``, the
    station ``balance.hub_thrust_set`` already uses."""
    from .export.coordinates import engine_thrust_axis
    from .modules.engine import resolved_engines

    sigma = standard_atmosphere(altitude_ft)[1]
    rho = RHO_SL * sigma
    v_tas = v_eas_kt / math.sqrt(sigma) * KT_TO_FPS
    out: List[EngineThrust] = []
    for i, eng in enumerate(resolved_engines(project), start=1):
        p = PROP_EFFICIENCY * float(eng.max_cont_hp or 0.0) * FT_LB_S_PER_HP
        area = math.pi * (float(eng.prop_diameter_in or 0.0) / IN_PER_FT / 2.0) ** 2
        static = (2.0 * rho * area * p * p) ** (1.0 / 3.0)
        thrust = min(p / v_tas, static) if v_tas > 0.0 else static
        hub = tuple(eng.prop_cg) if any(eng.prop_cg) else tuple(eng.engine_cg)
        if not any(hub):
            raise MissingInputError(
                f"engine {i} has neither a hub (prop_cg) nor an engine_cg, so its "
                "power-on thrust has no station to act at")
        axis, _ = engine_thrust_axis(eng)
        out.append(EngineThrust(engine=i, thrust_lb=thrust,
                                hub=(float(hub[0]), float(hub[1]), float(hub[2])),
                                axis=axis))
    return out


class PitchTerms(NamedTuple):
    """The thrust's share of the symmetric balance about a CG: the total
    magnitude, its ``x`` and ``z`` force and its moment in the FLTLOADS sense
    (the term added to the tail-load numerator, ``LT*(XT - Xcg)``)."""
    thrust_lb: float
    fx: float
    fz: float
    moment: float


def pitch_terms(thrusts: List[EngineThrust], cg: "CgCase") -> PitchTerms:
    """``sum F_z (x_cg - x_hub) - F_x (z_cg - z_hub)`` -- the FLTLOADS moment
    convention, in which the wing's ``LZ`` at ``Xw`` contributes
    ``LZ (Xcg - Xw)`` and its ``DX`` at ``Zw`` contributes ``-DX (Zcg - Zw)``.
    An axial thrust ``F_x = -T`` above the CG (``z_hub > z_cg``) is therefore
    negative: nose down, a larger tail download."""
    fx = math.fsum(t.force[0] for t in thrusts)
    fz = math.fsum(t.force[2] for t in thrusts)
    m = math.fsum(t.force[2] * (cg.xcg - t.hub[0]) - t.force[0] * (cg.zcg - t.hub[2])
                  for t in thrusts)
    return PitchTerms(thrust_lb=math.fsum(t.thrust_lb for t in thrusts), fx=fx, fz=fz, moment=m)


def point_thrusts(project: "Project", point: "VnPoint") -> List[EngineThrust]:
    """The thrusts a V-n point was balanced with: P-14's at its speed and
    altitude when it is power-on, none when it is power-off."""
    if point.power_state != STATE_ON:
        return []
    return rated_thrusts(project, point.v_eas_kt, point.altitude_ft)


def power_basis(project: "Project") -> str:
    """The in-band statement of the power state every artifact carries."""
    setting = power_cases(project)
    if setting == POWER_OFF_AND_ON:
        return ("Power: off and on (14 CFR 25.321(b), zero to maximum continuous "
                "thrust). Each flaps-up V-n point has a power-on twin ('-P') at the "
                "same n and V, re-balanced with every engine at "
                f"T = {format_value(PROP_EFFICIENCY)} x P_MC / V_TAS, capped by its "
                "momentum-theory static thrust, along its thrust line at the hub; "
                "power not lapsed with altitude. Flaps-down cases are power-off "
                "only (take-off power and slipstream are not modelled).")
    reason = power_rating_refusal(project)
    tail = (" No power-on case can be rated: " + reason.split(";")[0] + "."
            if reason is not None and project.engines else "")
    return ("Power: off. Every case carries zero thrust, the lower end of 14 CFR "
            "25.321(b)'s range; the power-on end is not analysed." + tail)
