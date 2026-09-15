"""The wing-body sideslip terms a lateral case carries (decision L-7).

Part of :mod:`sloads.modules.balance` (#191); the subsystem docstring is the
package's. Owner of the ``body-aero`` source tag: the estimator itself lives in
:mod:`sloads.lateral_body_aero`, and what is here is the balance's side of it --
the per-case terms, the two loads they become, and the sentence the case states
whether or not the term was applied.
"""

from __future__ import annotations

from typing import List, NamedTuple, Optional, Tuple

from ... import atmosphere, lateral_body_aero
from ...constants import dynamic_pressure_psf
from ...derived_geometry import fuselage_centreline, fuselage_width_at, require_wing_reference
from ...lateral_body_aero import LateralBodyAeroEstimate
from ...models import BalancedLoad, CriticalCondition, Project, VnPoint
from .constants import BODY_AERO_SOURCE


class LateralAeroTerms(NamedTuple):
    """One lateral case's L-7 numbers, computed whether or not the term is
    applied so the case can *say* what it did (decision L-7.16).

    Derivatives per degree, suite sign, about ``x_ref = xw`` (the wing 25 %-MAC
    station); ``side_force`` (lb, ``+`` starboard) and ``yaw_moment_ref`` (lb-in
    about ``x_ref``, ``+`` nose to port) are what applying them at
    ``beta_deg`` gives at the case's dynamic pressure; ``x_force``/``z_force``
    is the station the side force acts at (the body side-area centroid on the
    fuselage centreline, decision L-7.5). ``cn_beta_fin`` is SELECT's, so
    ``cn_beta_net`` is the fin + body sum about ``x_ref`` -- the static
    directional-stability check of note 19 G3 (negative = restoring).
    ``basis`` names where the derivatives came from (``"DATCOM"``, ``"entered"``
    or a mix); ``estimate`` is the DATCOM estimate when one could be made."""
    enabled: bool
    available: bool
    beta_deg: float
    cy_beta: float
    cn_beta: float
    x_ref: float
    x_force: float
    z_force: float
    side_force: float
    yaw_moment_ref: float
    cy_beta_fin: Optional[float]
    cn_beta_fin: Optional[float]
    cn_beta_net: Optional[float]
    basis: str
    estimate: Optional[LateralBodyAeroEstimate]
    reason: str = ""


def _wing_height_inputs(project: Project) -> Tuple[float, float, float]:
    """``(z_w, d_body, dihedral)`` for DATCOM's ``K_i``: the wing root
    quarter-chord's depth below the fuselage centreline (in, positive below),
    the body width there, and the wing dihedral. Zeros -- ``K_i = 1``, a
    mid-wing -- when the project has no parametric wing or no centreline; the
    default centreline IS the wing reference plane, so that is honest rather
    than a guess."""
    geom = project.geometry
    par = geom.parametric if geom is not None else None
    if geom is None or par is None:
        return 0.0, 0.0, 0.0
    dihedral = par.dihedral_deg
    surf = geom.by_name("wing")
    if surf is None or not surf.leading_edge or not surf.trailing_edge:
        return 0.0, 0.0, dihedral
    root_chord = surf.trailing_edge[0][0] - surf.leading_edge[0][0]
    x_c4 = surf.leading_edge[0][0] + 0.25 * root_chord
    line = fuselage_centreline(project)
    if line is None or line.assumed:
        return 0.0, 0.0, dihedral
    # centreline waterline at x_c4 by clamped interpolation of the entered points
    pts = line.points
    z_body = pts[0][1]
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        if xa <= x_c4 <= xb:
            z_body = za if xb == xa else za + (zb - za) * (x_c4 - xa) / (xb - xa)
            break
    else:
        if x_c4 > pts[-1][0]:
            z_body = pts[-1][1]
    width = fuselage_width_at(geom.fuselage, x_c4) or 0.0
    return z_body - par.root_waterline_z, width, dihedral


def lateral_aero_terms(project: Project, cond: CriticalCondition,
                       vn: VnPoint) -> LateralAeroTerms:
    """The L-7 wing-body term for one lateral case (design note 19 §6).

    Reads the sideslip and the fin derivatives **from SELECT's condition**
    (decisions L-7.6 / L-7.11) and the body derivatives from
    :func:`sloads.lateral_body_aero.estimate` at this case's speed and altitude
    (``K_Rl`` is a Reynolds-number function, so the computed default is per
    case) -- unless ``aero_coeffs.lateral_body_aero`` enters a value, which then
    stands for every case. Nothing here is a second opinion of an oracle-locked
    quantity: ``q`` is the V-n point's, ``S`` and ``b`` the project's.
    """
    # No ``flight_loads`` read left here at all (note 33): the wing area and the
    # reference station this needs are the planform's.
    wr = require_wing_reference(project)
    aero = project.aero_coeffs
    inp = aero.lateral_body_aero if aero is not None else None
    enabled = bool(inp is not None and inp.enabled)
    beta = float(cond.beta_deg) if cond.beta_deg is not None else 0.0
    x_ref = wr.xw
    span = _wing_span_in(project)
    unavailable = LateralAeroTerms(
        enabled, False, beta, 0.0, 0.0, x_ref, x_ref, wr.zw, 0.0, 0.0,
        cond.cy_beta_fin, cond.cn_beta_fin, None, "none", None, "")
    if cond.beta_deg is None:
        return unavailable._replace(
            reason="the critical set does not publish the case's sideslip (it "
                   "predates L-7) -- re-run SELECT")
    if span <= 0.0:
        return unavailable._replace(reason="no wing span")
    geom = project.geometry
    outline = geom.fuselage if geom is not None else None
    z_w, d_body, dihedral = _wing_height_inputs(project)
    est = lateral_body_aero.estimate(
        outline, wr.s_sqft, span, x_ref,
        atmosphere.reynolds_per_ft(vn.v_eas_kt, vn.altitude_ft),
        z_w_in=z_w, d_body_in=d_body, dihedral_deg=dihedral)
    entered_cy = inp.cy_beta if inp is not None else None
    entered_cn = inp.cn_beta if inp is not None else None
    if est is None and (entered_cy is None or entered_cn is None):
        return unavailable._replace(
            reason="no fuselage outline to estimate the wing-body derivatives "
                   "from, and none entered (aero_coeffs.lateral_body_aero)")
    cy = entered_cy if entered_cy is not None else est.cy_beta   # type: ignore[union-attr]
    cn = entered_cn if entered_cn is not None else est.cn_beta   # type: ignore[union-attr]
    basis = ("entered" if entered_cy is not None and entered_cn is not None
             else "DATCOM" if entered_cy is None and entered_cn is None
             else "DATCOM/entered")
    x_force = est.x_force if est is not None else x_ref
    z_force = _centreline_z_at(project, x_force, wr.zw)
    q_s = dynamic_pressure_psf(vn.v_eas_kt) * wr.s_sqft
    side_force = cy * q_s * beta
    yaw_ref = cn * q_s * span * beta
    cn_net = (cond.cn_beta_fin + cn) if cond.cn_beta_fin is not None else None
    return LateralAeroTerms(enabled, True, beta, cy, cn, x_ref, x_force, z_force,
                            side_force, yaw_ref, cond.cy_beta_fin, cond.cn_beta_fin,
                            cn_net, basis, est)


def _wing_span_in(project: Project) -> float:
    """The wing span the lateral derivatives are referred to (``b``, in):
    the v-tail slice's ``wing_span_in`` -- SELECT's own reference for the fin
    -- else twice the wing surface's outermost butt line."""
    vt = project.vtail_loads
    if vt is not None and vt.wing_span_in > 0.0:
        return vt.wing_span_in
    geom = project.geometry
    surf = geom.by_name("wing") if geom is not None else None
    if surf is not None and surf.leading_edge:
        return 2.0 * surf.leading_edge[-1][1]
    return 0.0


def _centreline_z_at(project: Project, x: float, fallback: float) -> float:
    """Fuselage centreline waterline at station ``x`` (clamped interpolation of
    :func:`fuselage_centreline`), else ``fallback``."""
    line = fuselage_centreline(project)
    if line is None or not line.points:
        return fallback
    pts = line.points
    if x <= pts[0][0]:
        return pts[0][1]
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        if x <= xb:
            return za if xb == xa else za + (zb - za) * (x - xa) / (xb - xa)
    return pts[-1][1]


def body_aero_loads(terms: LateralAeroTerms) -> List[BalancedLoad]:
    """The applied L-7 set: **one** load -- the side force at the body
    side-area centroid plus the free couple that makes the pair reproduce
    ``(Cy_beta, Cn_beta)`` about ``x_ref`` exactly (decision L-7.5; gate G6).
    Empty when the term is not enabled or not available, and exactly empty at
    ``beta = 0`` (gate G2: ``SUDDEN RUDDER`` takes no body load)."""
    if not (terms.enabled and terms.available) or terms.beta_deg == 0.0:
        return []
    couple = terms.yaw_moment_ref - (terms.x_force - terms.x_ref) * terms.side_force
    return [BalancedLoad(x=terms.x_force, y=0.0, z=terms.z_force,
                         fy=terms.side_force, mz=couple,
                         source=BODY_AERO_SOURCE, side="C")]


def lateral_aero_case_note(terms: LateralAeroTerms) -> str:
    """The per-case L-7 sentence (decision L-7.16): what was applied, or what
    would have been. Numbers are the case's own, so a deck header never quotes
    a figure this tool did not compute for that case."""
    stability = ""
    if terms.cn_beta_net is not None and terms.cn_beta_fin is not None:
        verdict = "restoring" if terms.cn_beta_net < 0.0 else "NOT RESTORING -- DIRECTIONALLY UNSTABLE (FAR 23.177)"
        stability = (f"; static directional stability: fin {terms.cn_beta_fin:+.5f} + "
                     f"body {terms.cn_beta:+.5f} = net Cn_beta {terms.cn_beta_net:+.5f}/deg "
                     f"about xw, {verdict}")
    if terms.enabled and terms.available:
        if terms.beta_deg == 0.0:
            return ("lateral body aero (L-7) ENABLED but beta = 0 on this case: no "
                    "wing-body sideslip load exists and none is applied" + stability)
        return (f"lateral body aero (L-7) APPLIED: Cy_beta {terms.cy_beta:+.5f}/deg, "
                f"Cn_beta {terms.cn_beta:+.5f}/deg about xw ({terms.basis}); at "
                f"beta {terms.beta_deg:+.2f} deg the wing-body side force is "
                f"{terms.side_force:+.0f} lb at FS {terms.x_force:.1f} (side-area "
                f"centroid) with a free couple closing the yawing moment to "
                f"{terms.yaw_moment_ref:+.0f} lb-in about xw; versus the fin-only "
                f"case |n_y| is raised (the side force adds to the fin's) and the "
                f"yaw acceleration lowered (the couple opposes the fin's)"
                + stability)
    if not terms.available:
        return ("lateral body aero (L-7) NOT applied and NOT estimable on this case: "
                + terms.reason)
    state = "DISABLED" if not terms.enabled else "NOT applied"
    return (f"lateral body aero (L-7) {state} -- estimated for this case: "
            f"Cy_beta {terms.cy_beta:+.5f}/deg, Cn_beta {terms.cn_beta:+.5f}/deg "
            f"about xw ({terms.basis}), i.e. {terms.side_force:+.0f} lb side force "
            f"and {terms.yaw_moment_ref:+.0f} lb-in yawing moment at beta "
            f"{terms.beta_deg:+.2f} deg NOT carried; enabling it raises |n_y| and "
            f"lowers the yaw acceleration" + stability)
