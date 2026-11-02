"""Balance feasibility: is a balanced case's tail state one the airplane can reach?

Design note 73 (#404, review A-2). The rational h-tail balance
(``select.htail_balance``, Ref 1 Ch 9) solves whatever elevator angle closes
the CG moment, and the fin march (ONENGOUT) forms whatever fin angle the yaw
needs. Neither was checked. This module is the one owner of that check
(D-73.1): every balanced family calls it, and nothing re-derives a limit.

It **states**, it never re-solves. A flagged case is delivered as it stands,
with its flag (D-73.9, Q6); no load is read or changed here.

The checks, all on magnitudes where the limit is a stall (owner ruling Q1:
the positive side mirrors the negative):

* **Tail lift** ``|C_L,h| <= clh_max``, ``C_L,h = LT/(q*S_h)``. The default
  cap is Roskam Pt VII p44 by stabiliser type (``constants.CLH_MAX_*``).
* **Tail angle** ``|alpha_eff| <= tail_stall_alpha_deg``, with ``alpha_eff``
  backed out of the angle-of-attack load, ``LT25/(a_h/57.3*q*S_h)`` (D-73.2),
  so the gust and pitch-acceleration increments count.
* **Authority by stabiliser type** (D-73.5, sconfig ``LowSpeedTrim.check``):
  ``F`` the elevator against its stops; ``A`` the stabiliser takes the 1 g
  trim within its travel and the residual elevator is checked; ``M`` the
  surface angle ``IT + tau*delta`` against the travel, no elevator.
* **Fin angle** ``|alpha| <= vtail_stall_alpha_deg``, only when entered
  (D-73.6, Q3).

Signs follow ``CONVENTIONS.md`` §2: elevator TE-down +, incidence LE-up +.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional, Tuple

from .constants import (
    CLH_MAX_ADJUSTABLE,
    CLH_MAX_ALL_MOVING,
    CLH_MAX_FIXED_COEFF,
    DEG_PER_RAD,
    dynamic_pressure_psf,
)
from .models.inputs import STABILISER_TYPES, MissingInputError, TailLoadsInput, normalise_code
from .units import format_value

#: The prefix every flag carries, so a reader of the deck or the report can find
#: them all, and a test can count them.
FLAG_PREFIX = "FEASIBILITY:"

#: The words every flag on a regulation-prescribed angle or throw carries
#: (23.423(a), 23.441(a)(2)/(3)). Such a flag is stated in the report and the deck
#: but raises no input warning: the state is the rule's, and the linear load past
#: it is conservative (owner ruling 2026-11-02; ``validation._check_balance_feasibility``).
PRESCRIBED_MARK = "prescribed by "


def is_prescribed(flag: str) -> bool:
    """Is ``flag`` on a state the regulation itself prescribes?"""
    return PRESCRIBED_MARK in flag


#: Slack on a limit comparison: a case *on* its limit is feasible (G-73.4), and
#: the 23.423(a) full-throw cases are built exactly on the stop.
_ON_LIMIT = 1e-9


@dataclass(frozen=True)
class Check:
    """One feasibility check: what was compared with what, and whether it held."""
    name: str            # elevator_stop | stabiliser_travel | tail_alpha | tail_cl | vtail_alpha
    value: float
    limit: float
    ok: bool
    text: str            # the flag sentence, without the prefix; stated whether or not it fires


@dataclass(frozen=True)
class Feasibility:
    """The checks one balanced case ran (D-73.1)."""
    checks: Tuple[Check, ...]

    @property
    def flags(self) -> Tuple[str, ...]:
        """The failed checks as prefixed sentences, in check order."""
        return tuple(f"{FLAG_PREFIX} {c.text}" for c in self.checks if not c.ok)

    @property
    def feasible(self) -> bool:
        return all(c.ok for c in self.checks)


def _deg(value: float) -> str:
    """A signed angle at the unit's precision (design note 65)."""
    return f"{format_value(value, 'deg', signed=True)} deg"


def _within(value: float, lo: float, hi: float) -> bool:
    return lo - _ON_LIMIT <= value <= hi + _ON_LIMIT


def stabiliser_type(ti: TailLoadsInput) -> str:
    """``ti.stabiliser`` as its code, with a movable stabiliser's travel required."""
    code = normalise_code(ti.stabiliser, STABILISER_TYPES, "stabiliser type")
    if code != "F" and (ti.stabiliser_incidence_nu_deg is None or ti.stabiliser_incidence_nd_deg is None):
        raise MissingInputError(
            f"a {STABILISER_TYPES[code].split(',')[0].lower()} needs its trim travel: "
            "geometry.empennage.htail.stabiliser_incidence_nu_deg and _nd_deg (the most "
            "nose-up and nose-down incidences, LE-up +) -- the feasibility check holds "
            "the stabiliser within them (design note 73 D-73.4).")
    return code


def clh_limit(ti: TailLoadsInput) -> Tuple[float, str]:
    """The h-tail lift-coefficient limit as a magnitude, and where it came from."""
    if ti.clh_max is not None:
        return abs(ti.clh_max), "entered"
    code = stabiliser_type(ti)
    if code == "A":
        return CLH_MAX_ADJUSTABLE, "Roskam Pt VII p44, adjustable stabiliser at full elevator"
    if code == "M":
        return CLH_MAX_ALL_MOVING, "Torenbeek p325, all-moving stabiliser"
    return (CLH_MAX_FIXED_COEFF * ti.aspect_ratio_htail ** (1.0 / 3.0),
            f"Roskam Pt VII p44, fixed stabiliser, 0.35 A_h^(1/3) at A_h {format_value(ti.aspect_ratio_htail)}")


def htail_state(lt25: float, lt: float, delta_deg: Optional[float], v_eas_kt: float,
                ti: TailLoadsInput, *, trim_delta_deg: Optional[float] = None,
                basis: str = "rational balance", prescribed_by: str = "") -> Feasibility:
    """The feasibility of one balanced h-tail state (D-73.2 … D-73.5).

    ``lt25``/``lt`` are the angle-of-attack and total tail loads (lb, the case's
    own, gust or pitch increment included); ``delta_deg`` the balancing elevator
    angle, TE-down + (``None`` where the method has no elevator angle -- the
    23.423(b) checked manoeuvre -- so no authority check runs). ``ti`` must be
    the *effective* inputs (``select.effective_tail_inputs``). ``trim_delta_deg``
    is the 1 g trim elevator of the case's own CG, weight and speed, required
    for an adjustable stabiliser. ``basis`` names the balance judged, in the text.
    ``prescribed_by`` names the rule when the elevator throw is the regulation's
    own (23.423(a)): the checks still run, and each flag says so (owner ruling,
    2026-11-02, the Q4 wording carried to the h-tail).
    """
    # The one a_h owner (note 35 AS-5); imported here because select imports this module.
    from .modules._vtail import lift_curve_slope

    code = stabiliser_type(ti)
    q_s = dynamic_pressure_psf(v_eas_kt) * ti.htail_area_sqft
    a_h = lift_curve_slope(ti.aspect_ratio_htail) / DEG_PER_RAD      # per degree
    tau = ti.elevator_effectiveness
    checks = []

    # Where a movable stabiliser sits, and what is left to the elevator.
    shift = 0.0                      # stabiliser incidence change from IT, deg
    residual = delta_deg
    if delta_deg is not None and code == "A":
        if trim_delta_deg is None:
            raise ValueError("an adjustable stabiliser's check needs the case's 1 g trim elevator angle")
        nu, nd = ti.stabiliser_incidence_nu_deg, ti.stabiliser_incidence_nd_deg
        assert nu is not None and nd is not None
        i_h = min(max(ti.tail_incidence_deg + tau * trim_delta_deg, nu), nd)
        shift = i_h - ti.tail_incidence_deg
        residual = delta_deg - shift / tau
    if delta_deg is not None and code == "M":
        nu, nd = ti.stabiliser_incidence_nu_deg, ti.stabiliser_incidence_nd_deg
        assert nu is not None and nd is not None
        surface = ti.tail_incidence_deg + tau * delta_deg
        shift = tau * delta_deg
        checks.append(Check(
            "stabiliser_travel", surface, nd if surface > 0 else nu, _within(surface, nu, nd),
            f"stabiliser at {_deg(surface)} incidence, outside its {_deg(nu)} to {_deg(nd)} travel ({basis})"))
        residual = None

    if residual is not None:
        up, dn = ti.elevator_te_up_deg, ti.elevator_te_down_deg
        if residual < 0:
            text = f"elevator {_deg(residual)} past the {format_value(up, 'deg')} deg TE-up stop"
        else:
            text = f"elevator {_deg(residual)} past the {format_value(dn, 'deg')} deg TE-down stop"
        if code == "A":
            text += f" after {_deg(shift)} of stabiliser trim"
        checks.append(Check("elevator_stop", residual, -up if residual < 0 else dn,
                            _within(residual, -up, dn), f"{text} ({basis})"))

    alpha = lt25 / (a_h * q_s) + shift if q_s and a_h else 0.0
    a_lim = ti.tail_stall_alpha_deg
    checks.append(Check("tail_alpha", alpha, a_lim, abs(alpha) <= a_lim + _ON_LIMIT,
                        f"tail angle of attack {_deg(alpha)} past the ±{format_value(a_lim, 'deg')} deg "
                        f"stall ({basis})"))

    cl = lt / q_s if q_s else 0.0
    c_lim, source = clh_limit(ti)
    checks.append(Check("tail_cl", cl, c_lim, abs(cl) <= c_lim + _ON_LIMIT,
                        f"tail C_L,h {format_value(cl, signed=True)} past the ±{format_value(c_lim)} limit "
                        f"({source}; {basis})"))
    if prescribed_by:
        checks = [replace(c, text=f"{c.text}; the elevator throw is {PRESCRIBED_MARK}{prescribed_by}, "
                          "so the method's linear load is conservative") for c in checks]
    return Feasibility(tuple(checks))


def vtail_state(alpha_deg: float, limit_deg: Optional[float], *,
                prescribed_by: str = "", basis: str = "") -> Feasibility:
    """The feasibility of one fin state (D-73.6): no check without an entered limit.

    ``prescribed_by`` names the rule when the angle is the regulation's own
    (23.441(a)(2), (a)(3)), so the flag says it is the rule's angle, not the
    balance's (Q4)."""
    if limit_deg is None:
        return Feasibility(())
    lim = abs(limit_deg)
    origin = f", {PRESCRIBED_MARK}{prescribed_by}" if prescribed_by else ""
    where = f" ({basis})" if basis else ""
    return Feasibility((Check(
        "vtail_alpha", alpha_deg, lim, abs(alpha_deg) <= lim + _ON_LIMIT,
        f"fin angle of attack {_deg(alpha_deg)}{origin} past the ±{format_value(lim, 'deg')} deg stall{where}"),))


#: What a report says once when no fin limit is entered (D-73.6).
VTAIL_NOT_CHECKED = "Fin stall not checked: no geometry.empennage.vtail.vtail_stall_alpha_deg entered."
