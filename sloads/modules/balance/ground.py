"""The ground families (step 10 piece 3 -- decisions G-1, G-6, G-7/G-7a, G-8).

Part of :mod:`sloads.modules.balance` (#191); the subsystem docstring is the
package's. A ground case is assembled from LANDLOAD's reactions rather than a
V-n point, and closes against the same six degrees of freedom; the twins it
mints are :mod:`~sloads.modules.balance.air`'s, which is why these two files
import each other (see :func:`~sloads.modules.balance.air.build_balanced_cases`).
"""

from __future__ import annotations

import math
from dataclasses import replace
from math import cos, radians, sin
from typing import Dict, List, Optional, Sequence, Tuple

from ...cg_cases import ground_cases, landing_role_cases
from ...derived_geometry import wing_plane, wing_reference
from ...gear_loads import GearCaseLoads, applied_wheels, gear_case_loads
from ...mass_distribution import CaseLoading, derive_case_loadings
from ...models import BalancedCaseResult, BalancedLoad, CgCase, LandingInput, MissingInputError, Project
from ..airloads import air_load_distribution
from ..landing import BALANCED_GROUND_CASES, GROUND_LIFT_CASES, GROUND_ONE_WHEEL_CASES, GROUND_SIDE_CASES
from .air import _handed_ref, handed_twin
from .applied import _mirror, _wing_slices, body_inertia, place_wing_inertia, wing_inertia_strips
from .closure import _closure, resultant6
from .queries import is_handed, point_mass_self_inertia
from .skipped import SkippedCondition, _GroundCondition, _skip

# The LANDLOAD case families -- ``GROUND_LIFT_CASES``,
# ``GROUND_ONE_WHEEL_CASES``, ``GROUND_SIDE_CASES`` and
# ``BALANCED_GROUND_CASES`` -- were declared here until design note 38 GF-6
# (#134). They are now owned by ``modules/landing.py``, which *is* the case
# numbering: it draws exactly these lines in ``_family``, ``_loading_index``
# and the reaction loops, and applies the ``lf*WL`` term in ``nvp`` to
# precisely the lift family. The deck reads them from there (imported above)
# rather than restating them beside the code that consumes them.

#: The G-7a statement of record, carried in-band on every ground case that
#: carries lift. The tilt is small and the reason it exists is not obvious from
#: the cards, so it travels with them rather than sitting in a document beside.
GROUND_LIFT_NOTE = (
    "the wing lift is L x W on the AIRLOADS spanwise shape, and it acts along "
    "the GROUND LINE rather than the airplane z axis: lift is perpendicular to "
    "the flight path, and at touchdown that is the runway, so the airplane's "
    "attitude tilts the lift vector by the ground angle. Only the SHAPE is "
    "borrowed from AIRLOADS -- the magnitude is L x W, so no speed, CL or V-n "
    "point is involved and no new aerodynamics is invented")

#: The G-7 statement of record for the ground-handling families, which carry no
#: lift at all. Said explicitly because "no lift" and "no load" are easy to
#: confuse, and the wing is emphatically not load-free in a braked roll.
GROUND_NO_LIFT_NOTE = (
    "no wing lift in this family (FAR 23.485 / 23.493 are ground-handling "
    "conditions): the gear loads are balanced by inertia alone. The wing still "
    "carries its OWN inertia at the case's solved load factor, so it is "
    "lift-free, not load-free")

#: The G-6 statement of record: what closes a ground case, and what does not.
GROUND_CLOSURE_NOTE = (
    "closed by the six-DOF rigid-body field, not by LANDLOAD's NVP/NDP/NS. "
    "Those are translation only -- the rotational half sits unreacted in "
    "PITCHP/ROLLP/YAWP -- and they are stated about the ground line, so "
    "consuming them would put a frame rotation in the load path. They are the "
    "independent closed-form check on the solve instead (FAR 23.471: the "
    "external reactions must be placed in equilibrium with the linear and "
    "angular inertia forces)")


def gear_sets(wheels: Sequence) -> List[BalancedLoad]:
    """The applied gear reactions of one ground case, at their reference points.

    A pure consumer of :mod:`sloads.gear_loads`, which is itself a pure consumer
    of :mod:`sloads.modules.landing` -- so the reaction an assembled ground case
    carries is the Appendix-A-locked one, per wheel, and no oracle is at risk from
    assembling it. What this adds is the ``BalancedLoad`` wrapper and the
    ``source``/``side`` tags the deck bands by.

    Each wheel arrives as a force **and** the lever-arm couple that carried it
    from the tyre contact patch to the trunnion, so the pair together has the
    identical resultant the reaction had at the patch (G-2's third guard asserts
    exactly that, at ``rel_tol 1e-12``). Applying the force without the couple is
    the failure mode the guard exists for: it still sums to zero at a determinate
    support, so the assembled residual alone would never catch it.

    No load-factor argument on purpose: the leg's own mass rides the closure
    field through its ``weight.items`` rows, exactly as the empennage surfaces'
    does, so that each mass enters exactly one set.
    """
    loads: List[BalancedLoad] = []
    for wheel in wheels:
        fx, fy, fz = wheel.force
        mx, my, mz = wheel.couple
        loads.append(BalancedLoad(
            x=wheel.node[0], y=wheel.node[1], z=wheel.node[2],
            fx=fx, fy=fy, fz=fz, mx=mx, my=my, mz=mz,
            source=f"gear-{wheel.leg}", side=wheel.side))
    return loads


def ground_lift_sets(project: Project, lift_lb: float,
                     rotation_deg: float) -> List[BalancedLoad]:
    """The starboard wing's share of the ground-case lift (G-7, G-7a).

    ``lift_lb`` is the **whole airplane's** lift, ``L x W_case``; this returns one
    half of it, and the caller mirrors. The shape is the AIRLOADS Schrenk
    distribution, rescaled -- only the shape, so no speed, ``CL`` or V-n point is
    needed and the oracle-locked spanwise integrator is reused rather than a
    lumped force invented. That matters structurally: a lumped force gives the
    inboard wing none of the ground-case bending relief it actually gets.

    **The vector lies along the ground line** (decision G-7a), so it enters
    airplane axes as ``(L sin rho, 0, L cos rho)``. Lift is perpendicular to the
    flight path; at touchdown the flight path is the runway to within the descent
    angle; and the airplane sits at ``rho`` to it. On ``ga6_normal``'s level
    families that puts ~152 lb of the 2,154 lb lift forward, and it is what keeps
    G-6's ``NVP``/``NDP`` gate an identity rather than a tolerance -- LANDLOAD
    sums ``lf*WL`` into the ground-line vertical, so a lift applied along ``z``
    would enter that sum short by ``cos rho``.

    The section ``Cm`` and the induced ``fx`` of the aerodynamic distribution are
    deliberately **not** carried: they scale with ``q*CL`` and this case has
    neither. Borrowing them would be inventing aerodynamics the condition does
    not define.
    """
    wm, geometry, aero_in = _wing_slices(project)
    geom = geometry.by_name(wm.surface)
    aero = aero_in.by_name(wm.surface)
    if geom is None or aero is None:
        raise MissingInputError("a ground case needs a wing surface and aero set")
    # Any (cl, v) gives the same *shape*: the Schrenk distribution scales with
    # ``q*CL`` as a whole. Unit values make that explicit at the call site rather
    # than borrowing a flight condition this case does not have.
    shape = air_load_distribution(geom, aero, 1.0, 100.0,
                                  *wing_plane(project, wm.surface))
    total = math.fsum(s.fz for s in shape.stations)
    if not total:
        raise MissingInputError(
            "the wing spanwise distribution integrates to zero lift, so a ground "
            "case's lift has no shape to be distributed on")
    k = (lift_lb / 2.0) / total
    a = radians(rotation_deg)
    return [BalancedLoad(x=s.x, y=s.y, z=s.z,
                         fx=s.fz * k * sin(a), fz=s.fz * k * cos(a),
                         source="ground-lift", side="R")
            for s in shape.stations]


def assemble_ground(project: Project, gear: "GearCaseLoads", wheels: Sequence,
                    loading: CaseLoading, cg: CgCase, lift_factor: float,
                    rotation_deg: float, *, case_ref=None,
                    hand: str = "") -> BalancedCaseResult:
    """Assemble one **ground** case and close it in six DOF (G-1, G-6, G-7).

    The sibling of :func:`assemble`, and deliberately not a branch inside it: a
    ground case has no V-n point, so it has no ``cl``, no ``lt`` trim tail load
    and no ``m_wf`` -- three of the four things the flight assembly is built
    around. What the two share is everything that matters, and they share it as
    code: :func:`wing_inertia_strips`, :func:`place_wing_inertia`,
    :func:`body_inertia`, :func:`resultant6`, :func:`point_mass_self_inertia` and
    :func:`_closure`.

    **Nothing is applied at a flight load factor, because there is not one.** The
    inertia set enters at ``nz = 0`` and the closure solves the whole rigid-body
    field, which is what G-6 asks for and what FAR **23.471** asks for: *"the
    external reactions must be placed in equilibrium with the linear and angular
    inertia forces in a rational or conservative manner."* The solved ``n_z``
    rotated back to the ground line **is** ``NVP``, exactly -- that identity is
    this step's benchmark-first gate, and it is content-carrying because LANDLOAD
    reaches those factors by lever arms and FAR percentages rather than by a mass
    matrix.

    **The pre-closure residual is the whole applied load and is not an error.**
    A ground case has nothing to cancel against -- there is no trim -- so
    :data:`RESIDUAL_GATE` does not apply to it, the same standing as the lateral
    families and the 23.427(a) h-tail case. Nothing trims the case in pitch
    either: distributing the lift at the wing rather than netting it at the CG
    (as LANDLOAD does, via ``NLG = N - L``) leaves a pitching moment, measured at
    1.26-1.47 % of ``n*W*MAC`` on ``ga6_normal``, reacted by pitch acceleration
    alone. An airplane at touchdown is an accelerating body, not a trimmed one,
    and Ch 20 has no balancing tail load to invent.

    ``hand`` is passed in rather than measured for the 23.485 family, where the
    *manual* decides which hand a case is: ``LG-19`` is the port drift and
    ``LG-20`` the starboard, and both ids already exist. Left blank, the hand is
    measured by :func:`is_handed` as it is for every other family.
    """
    # Tolerant, as the ``flight_loads`` read it replaces was: a ground case that
    # cannot name a MAC reports 0.0 rather than refusing (note 33 keeps the
    # contract, only moves the source).
    wr = wing_reference(project)
    notes: List[str] = [GROUND_CLOSURE_NOTE]

    inertia, panel_both = wing_inertia_strips(project, 0.0)
    wing_r, scale_notes = place_wing_inertia(inertia, loading, project, panel_both, 0.0)
    notes += scale_notes

    lift_lb = lift_factor * gear.weight_lb if gear.case in GROUND_LIFT_CASES else 0.0
    if lift_lb:
        wing_r = list(wing_r) + ground_lift_sets(project, lift_lb, rotation_deg)
        notes.append(f"applied wing lift {lift_lb:+.0f} lb (L = {lift_factor:g} x "
                     f"{gear.weight_lb:,.0f} lb, FAR 23.473(a)): {GROUND_LIFT_NOTE}")
    else:
        notes.append(GROUND_NO_LIFT_NOTE)

    loads: List[BalancedLoad] = list(wing_r) + _mirror(wing_r)
    loads += gear_sets(wheels)
    loads += body_inertia(loading, project, 0.0)

    # Entered thrust is a *flight* input here (backlog #10, :func:`hub_thrust_set`)
    # and is stated rather than dropped in silence: rating thrust per case family
    # -- take-off on a ground roll, max-continuous elsewhere -- is design note
    # 21's parked power_policy table, and this carve-out has no rating to give.
    entered = math.fsum(e.thrust_lb or 0.0 for e in (project.engines or []))
    if entered:
        notes.append(
            f"the project enters {entered:+,.0f} lb of engine thrust; it is NOT "
            "applied to a ground case -- a ground condition's thrust rating is "
            "design note 21's parked power-policy table, and this step (#10) "
            "carries one user-entered value with no per-family rating. The "
            "flight families carry it")

    wm, geometry, _ = _wing_slices(project)
    geom = geometry.by_name(wm.surface)
    semi_span = geom.leading_edge[-1][1] if geom else 0.0
    ref = (cg.xcg, 0.0, cg.zcg)
    # The 23.485 family's hand is the manual's (both ids exist, so it is passed
    # in); every other family's is measured from the applied set, exactly as the
    # flight families' is. The one-wheel case is caught by ``is_handed``'s third
    # source -- a net rolling moment made by the distribution itself -- which was
    # added for the 23.427(a) h-tail and covers this without a change: all the
    # vertical reaction sits at one ``y`` and there is no side force at all, so a
    # lateral-content-only predicate would have minted it unhanded.
    if not hand and is_handed(loads, abs(gear.weight_lb), semi_span):
        # A *measured* hand suffixes the id, exactly as the flight families do:
        # the 23.483 one-wheel condition has only ``LG-10``, so its two hands are
        # ``LG-10L``/``LG-10R``. A hand that was **passed in** does not, because
        # it came from the 23.485 family where LANDLOAD already supplies both
        # drift directions under ids of their own (G-8).
        hand = "R"
        case_ref = _handed_ref(case_ref, hand)
    residual = resultant6(loads, ref)
    fx, fy, fz, mx, my, mz = residual
    n, omega_dot, tensor = _closure(
        loads, cg, residual, point_mass_self_inertia(loading, project))

    carriers = sorted({w.carrier.value for w in wheels if w.carrier is not None})
    if carriers:
        notes.append(
            "gear reactions are transferred from the tyre contact patch to each "
            f"leg's own reference point ({', '.join(carriers)}-carried) with the "
            "lever-arm couple, so the load at the node has the identical "
            "resultant it had at the patch")

    return BalancedCaseResult(
        label=gear.description, vn_case=gear.case, cg=cg.name,
        # A ground case's ``nz`` is an OUTPUT, not an input: it is solved, and
        # ``delta_n`` carries it. Reported here as the solved value so every
        # consumer of ``BalancedCaseResult.nz`` -- the deck header, the row
        # table, the report -- states the load factor the case actually runs at
        # rather than a placeholder 1.0 nobody computed.
        nz=n[2], weight_lb=gear.weight_lb, mac=wr.mac if wr else 0.0,
        cg_x=cg.xcg, cg_z=cg.zcg,
        semi_span=semi_span, loads=loads,
        residual_fz=fz, residual_fx=fx, residual_my=my,
        residual_fy=fy, residual_mx=mx, residual_mz=mz,
        delta_n=n[2], delta_nx=n[0], delta_ny=n[1],
        p_dot=omega_dot[0], q_dot=omega_dot[1], r_dot=omega_dot[2],
        closure_inertia=tensor, fuselage_cm=0.0,
        case_ref=case_ref, hand=hand, notes=notes,
    )


def _ground_target(base: CgCase, weight_lb: float) -> CgCase:
    """The weight/CG an assembled ground case sits at.

    The roled loading's **CG station** at the case's **own design weight**, which
    are not always the same weight: 23.473(a) lets 23.479/481/483 be met at the
    design landing weight while 23.485/23.493 are met at the maximum take-off
    weight, and LANDLOAD applies that as ``WR`` on cases 13-22. Renaming the case
    when the weight moves keeps the two apart in the derivation record and in the
    deck, so a reader is never shown "aft max landing" against a take-off weight.

    **The entered loading is dropped with the weight (D-25 / D-26).** A
    ``LoadingDefinition`` states which items are aboard, not what the airplane
    weighs, so carrying it onto a re-weighted target would assemble the landing
    loading's inertia set against take-off-weight gear reactions and call the
    result balanced -- measured on ``concept_regional_jet`` 2026-08-15 as 31,000 lb
    of modelled mass under a case declaring 33,000. Setting it to ``None`` sends
    the re-weighted target through the subset search, which is what produced these
    cases before any loading was entered and is the one route that solves for the
    *weight* as well as the station. A target the search cannot reach is skipped
    and recorded, never invented, exactly as before.
    """
    if abs(weight_lb - base.weight_lb) <= 1e-6:
        return base
    return replace(base, name=f"{base.name} at {weight_lb:,.0f} lb",
                   weight_lb=weight_lb, loading=None)


def _ground_loadings(project: Project,
                     gear: Sequence[GearCaseLoads]) -> Dict[int, Tuple[CgCase, Optional[CaseLoading]]]:
    """``{LANDLOAD case number: (CgCase, CaseLoading)}`` for every ground case.

    Keyed by **case number** rather than by loading name, because the name alone
    does not identify the target: cases 1-12 and 19-22 both name ``aft max
    landing`` and sit at different design weights (23.473(a) again), so a
    name lookup silently returns whichever was derived first -- which on
    ``ga6_normal`` put the side family's inertia set 170 lb light and its ``n_y``
    5 % high.

    Derived through the **same** :func:`~sloads.mass_distribution.derive_case_loadings`
    every flight case uses, with the same ``derivable`` gate: a ground case whose
    loading the weight database cannot produce is skipped and recorded, never
    invented (decision G-3). Ground cases *inherit* the already-pinned
    "payload cases are not loadings the weight database can produce" limitation;
    they do not create one and they do not wait on it.
    """
    base = {c.name: c for c in landing_role_cases(project)}
    per_case: Dict[int, CgCase] = {}
    distinct: Dict[str, CgCase] = {}
    for g in gear:
        anchor = base.get(g.cg_name)
        if anchor is None:
            continue
        target = _ground_target(anchor, g.weight_lb)
        per_case[g.case] = target
        distinct[target.name] = target
    loadings = {ld.name: ld for ld in
                derive_case_loadings(project, list(distinct.values()))}
    return {case: (target, loadings.get(target.name))
            for case, target in per_case.items()}


def build_ground_cases(
        project: Project,
        skipped: Optional[List[SkippedCondition]] = None,
) -> List[BalancedCaseResult]:
    """The ground/landing conditions as assembled balanced cases (G-1).

    **Ground cases are born in the assembled free-free deck**, not in a
    per-component body view. A ground case is irreducibly three-dimensional --
    on ``ga6_normal`` braked roll is 2,261 lb vertical against 1,809 lb of drag
    per wheel, and the side family 2,261 against -1,700 lb of side load, applied
    at the contact patch ~41 in below the fuselage beam line and +-57 in off the
    centreline. Those lever arms *are* the load case, and the per-component
    fuselage deck is planar by construction, so building it there first and in
    the primary deliverable second would be backwards.

    Which of LANDLOAD's 33 cases assemble, and why the rest do not:

    * **1-24** assemble, one balanced case each, plus a twin where the family has
      a hand;
    * **20, 22, 24** are the even members of the 23.485 pairs: they are LANDLOAD's
      *own* opposite drift direction, and decision G-8 mints them by **reflecting**
      the odd member instead, so the reflection operator keeps its single owner
      and gains the only external check it will ever get. They are recorded as
      derived rather than dropped;
    * **25-33** are the 23.499 supplementary nose-wheel family, which carries nose
      reactions only -- no main-gear reaction exists in it -- so it is a local
      gear-design case, not an airplane in equilibrium. It is recorded, and it
      has a home: the gear load report carries all 33.

    Every skip is recorded through the same :class:`SkippedCondition` path the
    flight families use, so "here is every condition and what became of it"
    covers the ground family too.
    """
    record: List[SkippedCondition] = skipped if skipped is not None else []
    try:
        gear = gear_case_loads(project)
    except MissingInputError:
        return []
    if not ground_cases(project):
        return []

    loadings = _ground_loadings(project, gear)
    by_case = {g.case: g for g in gear}
    landing: Optional[LandingInput] = project.landing
    if landing is None:
        raise MissingInputError("ground cases need 'landing'")
    lift_factor = landing.lift_factor

    out: List[BalancedCaseResult] = []
    for g in gear:
        cond = _GroundCondition(g)
        if g.case not in BALANCED_GROUND_CASES:
            record.append(_skip(cond, "gear-design-only"))
            continue
        if g.case in GROUND_SIDE_CASES and g.case % 2 == 0:
            record.append(_skip(cond, "side-twin-by-reflection"))
            continue
        entry = loadings.get(g.case)
        if entry is None:
            record.append(_skip(cond, "no-cg-case"))
            continue
        cg, loading = entry
        if loading is None or not loading.derivable:
            record.append(_skip(cond, "loading-not-derivable"))
            continue

        one_wheel = g.case in GROUND_ONE_WHEEL_CASES
        partner = by_case.get(g.case + 1) if g.case in GROUND_SIDE_CASES else None
        wheels = applied_wheels(
            g.legs, one_wheel=one_wheel,
            partner_side_lb=(partner.legs[0].ground_line[2] if partner else None))
        rotation = g.legs[0].rotation_deg
        # The 23.485 family's hand is LANDLOAD's own: ``SMP`` is negative on the
        # odd member (0.5 W inboard to port) and positive on the even one, so the
        # computed case is the PORT drift and its twin the starboard. Every other
        # family lets ``is_handed`` measure it.
        hand = ""
        if partner is not None:
            hand = "L" if g.legs[0].ground_line[2] < 0 else "R"
        case = assemble_ground(project, g, wheels, loading, cg, lift_factor,
                               rotation, case_ref=g.case_ref, hand=hand)
        out.append(case)
        if case.hand:
            twin_ref = partner.case_ref if partner is not None else None
            out.append(handed_twin(case, case_ref=twin_ref))
    return out
