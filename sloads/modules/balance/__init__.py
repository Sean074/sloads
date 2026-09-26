"""Balanced free-free airplane cases -- wing tip to wing tip, nose to tail.

Plan 11 (``docs/25_notes/11_balanced_airframe_cases_plan.md``) step **B2**,
decisions B-1…B-5. Conventions: ``docs/10_standard/CONVENTIONS.md``.

The goal, in the user's words: *a full airplane balanced case with no need for a
constraint, because the loads balance.* The airplane already balances at trim --
``flight_envelope._balance`` closes ``LZW + LT = Nz*W`` exactly, and
``test_concept_closure`` has asserted it for a long time. What was missing is
that the **distributed** loads never inherited that balance: the wing
distribution, the tail load, the fuselage inertia and the trim solve were four
separate calculations that nothing assembled.

This module assembles them and reports what is left over.

Three things had to be got right, and each was measured rather than assumed
-------------------------------------------------------------------------
**1. A cumulative torsion is not a free moment.** ``WingStationLoad.myy`` is the
torsion about the *root* 25 % chord, and it already contains the sweep and
dihedral transfer of outboard shear inboard (``tyy``/``tvyy`` in
``airloads.py``). Assembling from it *and* applying the strip's position offset
counts the transfer twice: on ``ga6_normal`` PHAA that puts the pitching-moment
residual at **20.5 %** of ``n*W*MAC`` instead of 0.15 %. Only the section
pitching moment ``ml`` is a free moment, and :func:`_free_moments` recovers it by
subtracting the two transfer accumulations back out.

**2. The wing load must be at the balanced case's own flight condition.** The
entered ``wing_mass.cases`` carry a hand-written ``cl``/``v_eas_kt`` that is a
*different condition* from the V-n point SELECT pairs them with -- ``atr42_100``
enters CL 1.55 at 170 kt against its V-n point's 1.7283 at 185.85 kt. Assembling
the two halves then compares different flight conditions, and the force residual
runs 10-37 % of ``n*W``. So the wing distribution is **recomputed at the V-n
point's own** ``cl``/``v``/``nz`` (:func:`wing_sets`). The entered distributions
are untouched and remain the FAR 23 deliverables -- this adds a case, it does not
change one, and no Appendix A oracle moves.

**3. The mass model is the items, not WINGINER's own.** Wing inertia comes from
the ``WING``-tagged items of the case's derived loading (step B1/C1) -- read as
**reacted parts** (:func:`~sloads.mass_distribution.reacted_parts`, design note
29), so a fuel row partly carried by the wing contributes its wing share here and
its body share to :func:`body_inertia` -- spread over WINGINER's spanwise shape --
decision B-2 and plan 11 §4. Taking it from
``wing_mass.panel_weight_lb + concentrated`` instead double-counts anything that
is in both models: on ``atr42_100`` and ``dhc8_dash8`` the wing-tank fuel is, and
the residual runs 12-13 % rather than 1.9 %.

What the assembled case carries, and what it must not
-----------------------------------------------------
The seam rule (plan 11 §4; owner ``CONVENTIONS.md`` §Seam, where note 56 D-56.2
retired it as a *live* rule): **a load that a free-body cut introduces is never
applied in the assembled model.** Each of the five per-component decks took a
cut and carried the cut reaction as an applied load, and in the assembled model
the solver recovers it instead. No cut model ships any more, so the rule now
records why this module is shaped as it is. Concretely the wing carry-through
reaction
(``BodyStationLoad.source == "reaction"``, note 64 D-64.5) is *excluded* --
:func:`assemble` never reads ``body_loads``, and :func:`carry_sources_absent`
is the guard.

The fuselage pitching moment
----------------------------
The trim carries ``Cm`` for the airplane **less tail** -- wing *and* fuselage --
while the distributed wing carries only its own section ``Cm``. The difference is
the fuselage's Munk moment, and it has no distributed carrier until backlog item
M4-19 lands the Multhopp/Nelson body moment. It is applied here as a single free
moment on the fuselage (``source="fuselage-cm"``), which preserves the total
exactly and is labelled as lumped wherever it is rendered. Omitting it would
leave a moment residual of the same size for the closure to absorb silently -- a
real aero load disguised as a correction.

Its size is **not** a small positive constant. Measured across the fixtures that
have flight cases it runs **-6.6 to +4.9 %** of ``n*W*MAC`` on ``ga6_normal`` and
**-8.5 to +5.8 %** on ``concept_regional_jet``, and it changes sign -- with
``alpha``, as a slope term must (``NMAA`` is the negative-``alpha`` case on the
ga6). An earlier "+4.3 to +6.3 %, positive" reading here was taken over the
symmetric wing conditions only and did not survive the negative-``alpha`` and
lateral points (corrected 2026-08-15).

Residual closure (B-3)
----------------------
Whatever is left is closed as mass-proportional inertia relief in two decoupled
degrees of freedom -- ``delta_n`` on every mass, and a pitch term
``+k*(x_i - x_cg)*w_i``. They do not fight each other: the pitch term sums to
zero force because ``sum(w_i*(x_i - x_cg)) == 0`` by the definition of the CG,
and the ``delta_n`` term sums to zero moment for the same reason. Both magnitudes
are recorded on the result, and the gate is on the residual **before** closure --
the physics, not the correction.

The antisymmetric cases (B7)
----------------------------
**Only ``ACRL`` is antisymmetric, and it is measured, not assumed.** The
handedness of a wing case lives entirely in its resolved UNB (FAR 23.349,
``WingLoadCase.unbal_moment``), and UNB is non-zero on ``ACRL`` alone --
derived from condition A's root bending since design note 52 (D-52.2; an
entered value still wins), zero everywhere else including ``TORS`` on every
fixture. That is not a fixture accident: a *steady* roll has no
unbalanced rolling moment by definition (the aileron moment is balanced by roll
damping), and the up-going/down-going aero asymmetry that remains has no
spanwise representation anywhere in this suite. ``TORS`` is therefore assembled
as the symmetric case it is, and :func:`test_only_acrl_carries_roll` pins that
finding so a fixture that ever enters a non-zero UNB for it goes red.

**The applied couple is lumped; the reaction is distributed.** WINGINER's model
-- the one Appendix A is locked to -- never distributes the aileron's own lift
increment: it takes only the *inertia reaction* to the roll acceleration UNB
causes (``fz_r``, the unit-roll distribution). The assembled case matches that
exactly: the aero rolling moment enters as a single labelled free couple at the
wing aerodynamic centre (``source="aileron-roll"``, the same treatment and the
same honesty as ``fuselage-cm``), and the distributed antisymmetric load the
wing actually carries comes out of the **roll degree of freedom of the closure**.
The consequence is stated wherever the case is rendered: the aileron's spanwise
lift increment is not modelled, because ``AileronLoadsInput`` carries areas and
no butt lines (filed in the backlog).

**And that closure is checkable against an independent producer.** Closing the
roll residual with ``k_roll*w_i*y_i`` -- physically ``-m_i*p_dot*y_i``, the roll
analog of the pitch term, decoupled from all three symmetric DOF because
``sum(w_i*y_i) == 0`` for a mirror-symmetric mass model -- reproduces WINGINER's
``ur*fz_r`` distribution **strip for strip**: ratio 1.000000 on both fixtures,
with the wing-item/panel scale cancelling identically. Two producers, one answer:
WINGINER's oracle-locked recurrence and this module's ``p_dot`` solve. That
identity is the B7 closure gate (``test_roll_closure_reproduces_winginer``),
standing in for the printed oracle concept mode does not have.

The lateral cases (B8a)
-----------------------
Plan 13 (``docs/25_notes/18_b8a_lateral_closure_plan.md``), decisions L-1…L-8.
SELECT's four rational v-tail conditions -- sudden rudder, yaw to sideslip, yaw
15 neutral, side gust -- assemble as balanced cases too, and they are the first
lateral load factors this suite has ever produced. All four sit on V-n points at
``n_z ~ 1``, so the vertical/longitudinal/pitch half is the symmetric machinery
unchanged; what is added is the fin's distributed side load (:func:`vtail_sets`)
and the three lateral degrees of freedom of the closure B8a-2 built.

**Nothing balances a rudder kick, and nothing is supposed to.** In the symmetric
case aero and inertia nearly cancel and a residual over 1 % means something is
missing. Laterally there is nothing to cancel against: the pre-closure ``Fy`` and
``Mz`` residuals **are** the fin load, in full, by construction. So
:data:`RESIDUAL_GATE` does not apply to them -- the same standing as ``ACRL``'s
roll residual -- and the gate that does is that the case's *symmetric half*, with
the fin load removed, still closes inside 1 %.

**The fin is the only lateral aero the suite computes** (decision L-7). Fuselage
and wing side force in sideslip exist on the airplane and nowhere in these 22
programs, and the two degrees of freedom they are missing from err in **opposite
directions**. The body's yawing couple is destabilizing and opposes the fin's, so
the yaw acceleration is **over-stated** and the inertia it drives is
conservative. The body-and-wing side force, however, acts the *same* way as the
fin's restoring load at ``+beta`` -- it **adds** -- so ``n_y`` is
**under-stated** and the lateral translational inertia it drives is **not**
conservative. Neither is the airplane's real acceleration. That is said in-band,
on every lateral case, through :data:`LATERAL_AERO_NOTE`. Both magnitudes are
stated as *unknown*, because quantifying them is building the missing model
(backlog L-7); this is the weaker of the suite's two honesty statements and is
not dressed up as the stronger one (the lumped fuselage ``Cm``, whose size can be
quoted).

The unsymmetrical horizontal tail (D-R8)
---------------------------------------
Decision **D-R8** (2026-08-10), review finding **F-R5**. FAR **23.427(a)** is the
one horizontal-tail condition with a genuine hand: SELECT takes the
largest-magnitude symmetric tail load and puts 100 % of half of it on one side
and ``pc = min(100 - 10(n-1), 80)`` percent on the other. Every other h-tail
condition is symmetric and already rides the wing cases as the trim tail load
``vn.lt``; this one has left/right content that a lumped centreline force cannot
carry, and the full-span tail topology (plan 09 decision T-8) was built for it.

**The applied tail load is SELECT's own, and it replaces the trim load** rather
than adding to it: ``RH + LH`` *is* the condition's total tail load, and applying
``vn.lt`` beside it would count the balancing part twice. The h-tail strips come
from :func:`htail_sets`, the exact analogue of :func:`vtail_sets` -- air only, with
the surface's mass left in :func:`body_inertia` to ride the closure field, so
each mass still enters exactly one set.

**The pre-closure residual is the maneuver, not an error.** The 23.427(a) load is
a *maneuver* load (the unchecked maneuver governs on both fixtures that assemble)
and its V-n point is a balanced one at ``n_z ~ 1``, so the airplane is genuinely
not in trim: on ``ga6_normal`` the applied tail load is -1204.7 lb against a trim
-177.7, and the difference -- 49.8 % of ``n*W``, 144 % of ``n*W*MAC`` -- comes out
as ``delta_n = -0.496 g`` and ``q_dot = +637 deg/s^2``. That is what an abrupt
elevator input does, and closing it in the pitch degree of freedom is the
standard treatment of an unbalanced pitching maneuver, not a correction applied
to a broken balance. :data:`RESIDUAL_GATE` therefore does not apply to this
family's ``Fz``/``My`` either -- the same standing as the lateral cases -- and the
gate that does is that the case's **trim half**, with the 23.427(a) set replaced
by the lumped ``vn.lt``, still closes inside it
(``test_the_trim_half_of_an_unsymmetrical_case_still_closes``).

Two independent producers check what is applied: the set's per-side sums are
SELECT's own ``RH``/``LH`` to the last digit, and its rolling moment about the
centreline is the closed form ``(RH - LH) * y_bar`` with ``y_bar`` the
chord-weighted centroid of the half planform -- ratio 1.000000000 on both
fixtures.

**The twins come from reflection, not recomputation** (decisions B-6/B-7). Every
case with antisymmetric content is emitted as a handed pair, the port case being
the mirror image of the starboard one through
:func:`sloads.export.coordinates.reflect_load`. The FAR 23 core never sees
handedness; the id gains an ``L``/``R`` suffix and the unhanded id remains the
physical condition.
"""

from __future__ import annotations

from math import degrees
from typing import List

from ...models import (
    ConditionResult,
    LoadValue,
    MissingInputError,
    ModuleResult,
    Project,
)
from ...registry import register
from ...rigid_body import radians_per_s2
from .air import (  # noqa: F401
    _vtail_distributions,
    assemble,
    build_balanced_cases,
    handed_twin,
    unbalanced_rolling_moment,
)
from .applied import (  # noqa: F401
    HUB_THRUST_SOURCE,
    _free_moments,
    _wing_inertia_scale,
    body_axial_set,
    body_inertia,
    htail_sets,
    hub_thrust_set,
    place_wing_inertia,
    polar_alpha_trusted,
    reflect_load,
    vtail_sets,
    wing_inertia_strips,
    wing_sets,
)
from .closure import (  # noqa: F401
    _closure,
    resultant,
    resultant6,
)

# The package's public surface, re-exported so the split of #191 is invisible
# to every consumer: `from sloads.modules.balance import X` and `balance.X`
# both still resolve for every name the single file exported. ``__all__``
# below is unchanged -- it is the curated statement of what this module is for,
# and the names outside it are exported because code already imports them.
from .constants import (  # noqa: F401
    AILERON_COUPLE_NOTE,
    BALANCED_HTAIL_CONDITIONS,
    BALANCED_VTAIL_CONDITIONS,
    BALANCED_WING_CONDITIONS,
    BODY_AERO_SOURCE,
    CLOSURE_DIAGNOSTIC,
    FORCE_RESIDUAL_ACCEPTANCE,
    HANDEDNESS_TOL,
    LATERAL_AERO_NOTE,
    MODULE_NAME,
    RESIDUAL_GATE,
    ROLLING_WING_CONDITIONS,
    SYMMETRIC_WING_CONDITIONS,
)
from .ground import (  # noqa: F401
    GROUND_CLOSURE_NOTE,
    GROUND_LIFT_NOTE,
    GROUND_NO_LIFT_NOTE,
    assemble_ground,
    build_ground_cases,
    gear_sets,
    ground_lift_sets,
)
from .lateral import (  # noqa: F401
    LateralAeroTerms,
    body_aero_loads,
    lateral_aero_case_note,
    lateral_aero_terms,
)
from .queries import (  # noqa: F401
    FLIGHT_SOURCE_STEM,
    GROUND_SOURCE_STEM,
    case_source_name,
    htail_load,
    htail_side_loads,
    hub_thrust,
    is_ground,
    is_handed,
    is_lateral,
    is_powered,
    is_unsymmetrical_htail,
    point_mass_self_inertia,
    residual_gate_applies,
    residual_gate_exemptions,
    residual_gate_family,
    source_case_name,
    vtail_load,
)
from .skipped import (
    SKIP_REASONS,
    SKIPPED_RECORD_TITLE,
    SkippedCondition,
    _skipped_record,
    carry_sources_absent,
    skipped_block,
    skipped_condition_lines,
)


def skipped_conditions(project: Project) -> List[SkippedCondition]:
    """The F-C7 record alone, for a caller that already has the cases.

    Assembly is re-run, so a caller that wants both takes the sink form of
    :func:`build_balanced_cases` instead -- one pass, one record.

    A package entry point rather than a member of
    :mod:`~sloads.modules.balance.skipped`: the record type is the lower layer
    and this is a facade over assembly, so putting it there would point the
    record at the assembly that produces it (#191).
    """
    record: List[SkippedCondition] = []
    build_balanced_cases(project, record)
    return record


def run(project: Project) -> ModuleResult:
    """Registry entry point: the balanced cases as a reportable result.

    The last condition is always the F-C7 skipped-conditions record
    (:func:`_skipped_record`), so a consumer of this result can always state what
    the assembled deliverable does *not* cover.
    """
    skipped: List[SkippedCondition] = []
    cases = build_balanced_cases(project, skipped)
    if not cases:
        raise MissingInputError(
            "no wing or vertical-tail condition has both a V-n point and a "
            "derivable payload loading -- nothing to balance")
    conditions = []
    for c in cases:
        hand = {"R": " starboard", "L": " port"}.get(c.hand, "")
        roll_values = [
            # Applied, not unbalanced: the airplane is *meant* not to balance a
            # rolling case. See BalancedCaseResult.roll_moment_fraction.
            LoadValue("Applied aileron rolling moment", -c.unbal_moment, "lb-in",
                      key="balanced_roll_moment"),
            LoadValue("Roll couple (% of n*W*b/2)",
                      100.0 * c.roll_moment_fraction, "%",
                      key="balanced_roll_moment_pct"),
        ] if c.unbal_moment else []
        unsymmetrical = is_unsymmetrical_htail(c)
        rh, lh = htail_side_loads(c)
        htail_values = [
            # The case's defining applied load and the split that gives it its
            # hand, reported before the motion the mismatch with trim causes.
            LoadValue("Applied horizontal-tail load", htail_load(c), "lb",
                      key="balanced_htail_load"),
            LoadValue("Starboard half", rh, "lb", key="balanced_htail_rh"),
            LoadValue("Port half", lh, "lb", key="balanced_htail_lh"),
            LoadValue("Pitch acceleration", degrees(radians_per_s2(
                (0.0, c.q_dot, 0.0))[1]), "deg/s^2", key="balanced_q_dot"),
        ] if unsymmetrical else []
        # A powered case reports the thrust it carries and the longitudinal
        # acceleration that reacts it (backlog #10) -- and only a powered case
        # does, so an unpowered fixture's condition rows are unchanged.
        powered_values = [
            LoadValue("Applied engine thrust", hub_thrust(c), "lb",
                      key="balanced_hub_thrust"),
            LoadValue("Closure dnx", c.delta_nx, "g", key="balanced_delta_nx"),
        ] if is_powered(c) else []
        lateral = is_lateral(c)
        lateral_values = [
            # The case's defining applied load, reported before the motion it
            # causes: nothing balances it, so the three below ARE its reaction.
            LoadValue("Applied fin side load", vtail_load(c), "lb",
                      key="balanced_fin_load"),
            LoadValue("Lateral load factor Ny", c.delta_ny, "g",
                      key="balanced_ny"),
            LoadValue("Yaw acceleration", degrees(radians_per_s2(
                (0.0, 0.0, c.r_dot))[2]), "deg/s^2", key="balanced_r_dot"),
            LoadValue("Roll acceleration", degrees(radians_per_s2(
                (c.p_dot, 0.0, 0.0))[0]), "deg/s^2", key="balanced_p_dot"),
        ] if lateral else []
        # A lateral case names the rule SELECT picked it under (23.441(a)(1)
        # ... 23.443(b)) and a ground case the condition LANDLOAD computed it
        # under (23.479 ... 23.493, R6-C1 -- 23.471 is the family's general
        # sentence, the fallback a ref-less ground case would deserve). The
        # symmetric flight families keep their literals: their CaseRefs name
        # the V-n envelope source (23.333), but the *balancing* of that point
        # is 23.321's requirement, so the row keeps citing it.
        ground = is_ground(c)
        if lateral or unsymmetrical or ground:
            far = (c.case_ref.far_reference if c.case_ref else "") or (
                "23.471" if ground else "23.321")
        else:
            far = "23.349" if c.unbal_moment else "23.321"
        conditions.append(ConditionResult(
            title=(f"Balanced case {c.label}{hand} "
                   f"({case_source_name(c, short=True)}, {c.cg})"),
            far_reference=far,
            values=roll_values + htail_values + lateral_values
            + powered_values + [
                LoadValue("Load factor Nz", c.nz, "g", key="balanced_nz"),
                LoadValue("Weight", c.weight_lb, "lb", quantity="mass",
                          key="balanced_weight"),
                LoadValue("Residual Fz (pre-closure)", c.residual_fz, "lb",
                          quantity=CLOSURE_DIAGNOSTIC,
                          key="balanced_residual_fz"),
                LoadValue("Residual Fz (% of n*W)",
                          100.0 * c.force_residual_fraction, "%",
                          key="balanced_residual_fz_pct"),
                LoadValue("Residual My (pre-closure)", c.residual_my, "lb-in",
                          quantity=CLOSURE_DIAGNOSTIC,
                          key="balanced_residual_my"),
                LoadValue("Residual My (% of n*W*MAC)",
                          100.0 * c.moment_residual_fraction, "%",
                          key="balanced_residual_my_pct"),
                LoadValue("Closure dn", c.delta_n, "g", key="balanced_delta_n"),
                LoadValue("Lumped fuselage Cm moment", c.fuselage_cm, "lb-in",
                          key="balanced_fuselage_cm"),
                LoadValue("Non-wing drag (body-axial)", c.body_axial, "lb",
                          key="balanced_body_axial"),
                LoadValue("Non-wing drag dCD", c.delta_cd, "",
                          key="balanced_delta_cd"),
            ],
            note="; ".join(c.notes),
        ))
    conditions.append(_skipped_record(skipped))
    return ModuleResult(module=MODULE_NAME, conditions=conditions)


register(MODULE_NAME, run)


__all__ = [
    "AILERON_COUPLE_NOTE",
    "BALANCED_HTAIL_CONDITIONS",
    "BALANCED_VTAIL_CONDITIONS",
    "BALANCED_WING_CONDITIONS",
    "FLIGHT_SOURCE_STEM",
    "FORCE_RESIDUAL_ACCEPTANCE",
    "GROUND_SOURCE_STEM",
    "HANDEDNESS_TOL",
    "HUB_THRUST_SOURCE",
    "LATERAL_AERO_NOTE",
    "RESIDUAL_GATE",
    "ROLLING_WING_CONDITIONS",
    "SKIPPED_RECORD_TITLE",
    "SKIP_REASONS",
    "SYMMETRIC_WING_CONDITIONS",
    "SkippedCondition",
    "assemble",
    "body_inertia",
    "build_balanced_cases",
    "carry_sources_absent",
    "case_source_name",
    "handed_twin",
    "htail_load",
    "htail_sets",
    "htail_side_loads",
    "hub_thrust",
    "hub_thrust_set",
    "is_ground",
    "is_handed",
    "is_lateral",
    "is_powered",
    "is_unsymmetrical_htail",
    "reflect_load",
    "residual_gate_applies",
    "residual_gate_exemptions",
    "residual_gate_family",
    "resultant",
    "resultant6",
    "skipped_block",
    "skipped_condition_lines",
    "skipped_conditions",
    "source_case_name",
    "unbalanced_rolling_moment",
    "vtail_load",
    "vtail_sets",
    "wing_sets",
]
