"""The balanced case's vocabulary: which conditions assemble, and at what gates.

Part of :mod:`sloads.modules.balance` (#191) -- the subsystem's own explanation,
including the three things that had to be got right and the seam rule, is the
package docstring. This file holds the values every other file in the package
reads and nothing that computes.
"""

from __future__ import annotations

MODULE_NAME = "balance"

#: Quantity hint on the **pre-closure residual** force and moment: a statement
#: about how well the case closed, not a load the airframe carries (review
#: 2026-09-04 R-8, #170). The closed case is what it carries; these are what was
#: left over before the residual was distributed, so 14 CFR 23.303's factor states
#: a design quantity where there is none. Vocabulary owner:
#: :data:`sloads.units.NON_LOAD_QUANTITIES`.
CLOSURE_DIAGNOSTIC = "diagnostic"

#: Wing conditions whose load set is symmetric about the centreline. ``TORS``
#: joined this list at B7 **by measurement**: its ``unbal_moment`` is zero on
#: every fixture, because a steady roll has no unbalanced rolling moment (see the
#: module docstring). Assembling it as symmetric is therefore not an
#: approximation -- it is what the case contains. ``NHAA``, ``NLAA``, ``PNZ``
#: and ``NNZ`` are design note 62's slots above SELECT.BAS (D-62.4): none is a
#: roll point, so none carries an unbalanced rolling moment, exactly as NMAA.
SYMMETRIC_WING_CONDITIONS = ("PHAA", "PLAA", "PMAA", "NMAA", "TORS",
                             "NHAA", "NLAA", "PNZ", "NNZ")

#: Wing conditions that may carry an unbalanced rolling moment, hence a handed
#: pair. Membership here does **not** by itself make a case antisymmetric: a
#: condition whose ``unbal_moment`` is zero assembles symmetrically and is minted
#: unhanded, so the twins never appear for a case that has no hand.
ROLLING_WING_CONDITIONS = ("ACRL",)

#: Every wing condition the assembled deck covers.
BALANCED_WING_CONDITIONS = SYMMETRIC_WING_CONDITIONS + ROLLING_WING_CONDITIONS

#: SELECT's four rational vertical-tail conditions (FAR 23.441 maneuver, 23.443
#: gust), each assembled as a **lateral** balanced case at B8a-3. All four sit on
#: V-n points at ``n_z ~ 1``, so the vertical/longitudinal/pitch half of the case
#: is the shipped symmetric machinery unchanged and only the applied set grows.
#: ONENGOUT's 23.367 conditions are not in this tuple: since design note 66
#: (#285) they are a family of their own (``balance.engine_out_cases``), their
#: peak instant assembled quasi-statically on a 1 g parent -- plan 13 §4's
#: "a transient, not a balanced steady case" narrowed, not reversed.
BALANCED_VTAIL_CONDITIONS = ("SUDDEN RUDDER", "YAW TO SIDESLIP",
                             "YAW 15 NEUTRAL", "SIDE GUST")

#: The horizontal-tail conditions assembled as balanced cases (D-R8) -- the
#: 23.427(a) unsymmetrical load and nothing else, because it is the only h-tail
#: condition with a hand. The symmetric ones are *already* in the deliverable, as
#: the trim tail load ``vn.lt`` of every wing case's balanced assembly; giving
#: them a second assembled case would put the same physics in the deck twice
#: under a different name (:data:`SKIP_REASONS` ``htail-symmetric`` says so on
#: the record rather than dropping them silently).
BALANCED_HTAIL_CONDITIONS = ("UNSYMMETRICAL",)

#: Acceptance gate (plan 11 §6): the residual **before** closure, as a fraction
#: of ``n*W`` for force and ``n*W*MAC`` for moment.
#:
#: **It does not apply laterally, and that is physics rather than an exemption**
#: (plan 13 §2). A symmetric case's aero and inertia nearly cancel, so a residual
#: above 1 % means something is missing. A rudder kick has *nothing to cancel
#: against*: the fin load is reacted by inertia alone, so the pre-closure lateral
#: residual **is** the whole fin load by construction -- the same standing as
#: ``ACRL``'s roll residual, which plan 11 §10 already records. The lateral gate
#: is instead that the case's **symmetric half** still closes inside this bound
#: with the fin load removed (``test_the_symmetric_half_still_closes``).
RESIDUAL_GATE = 0.01

#: The **force** half of the acceptance, as a fraction of ``n*W`` (owner's
#: decision, 2026-08-22, closing CR-C-2).
#:
#: Plan 11 stated one flat 1 % for both components, and the pitch residual meets
#: it everywhere with an order of magnitude to spare (0.014-0.086 %). Force does
#: not: the four type fixtures reach 1.209-2.360 %, an ordering that tracks
#: **fixture lift-model quality** rather than the assembly -- ``ga6_normal``, the
#: one fixture whose aero and planform come from a printed source, is best at
#: 0.624 %, and the concept configurations are worst. Every case still closes
#: exactly after correction, and the DOF that would expose a mis-placed force --
#: pitch -- stays at a tenth of its own gate.
#:
#: None of these six is a printed oracle: the balanced full-span model is a
#: mission-extension deliverable with no Appendix A/B figure behind it (the
#: FAR23 replication core is oracle-locked separately and is untouched by this
#: number). So the acceptance is set where the suite already enforced it -- this
#: was ``tests/test_balance.py``'s hard stop, the level at which "a small
#: correction to a balance that nearly held" stops being a fair description --
#: and the controlling document now judges force against the same value the
#: tests do, instead of reporting a failure against an acceptance nothing
#: enforced. The per-fixture, per-family ``_FORCE_RESIDUAL_RATCHET`` in that test
#: is unchanged and remains the regression guard: a fixture drifting from
#: 2.360 % toward this bound still fails loudly, well before it arrives.
FORCE_RESIDUAL_ACCEPTANCE = 0.025

#: Applied lateral content below this fraction of ``n*W`` is summation noise, not
#: a hand (decision L-6). It serves the rolling test of :func:`is_handed` too,
#: against ``n*W*(b/2)``: the margin there is fifteen orders of magnitude -- a
#: mirror-symmetric applied set nets 1e-17 of ``n*W*b/2`` in roll, and the
#: 23.427(a) h-tail case 6e-3 to 1.7e-2 -- so one threshold serves both.
HANDEDNESS_TOL = 1e-9

#: The B7 statement of record for the lumped aileron couple, carried in-band on
#: every ``ACRL`` case (the case's ``notes``, hence the deck header and the UI)
#: and in the report's standing limitations (review F-R4) — one wording for both,
#: because the deck and the controlling document must not caveat the same
#: modelling choice differently. The couple's *magnitude* is per case and is
#: stated beside this sentence; what is standing is the modelling choice.
AILERON_COUPLE_NOTE = (
    "the suite has no aileron spanwise geometry, so its own lift increment is "
    "not distributed (WINGINER carries only the inertia reaction, which IS "
    "distributed here)")

#: The L-7 statement of record, carried in-band on every lateral case: on the
#: result's ``notes``, hence in the deck header and the UI. Design note 19
#: (rev. 3, 2026-08-17) closed the "unknown amount" this sentence carried
#: until then: the wing-body side force and yawing moment in sideslip are now
#: computed (DATCOM 5.2.1.1 / 5.2.3.1, :mod:`sloads.lateral_body_aero`) and
#: applied when ``aero_coeffs.lateral_body_aero.enabled`` -- **off by default**
#: (decision L-7.3), because the term raises the load on one lateral degree of
#: freedom and lowers it on the other. So the standing statement says what the
#: term is and which way each degree of freedom errs when it is NOT applied,
#: and every lateral case adds one of two per-case sentences (decision L-7.16):
#: :func:`lateral_aero_case_note` -- the *estimated* effect on this case when
#: the term is off, or the applied numbers and the net static-stability check
#: when it is on. The *direction* is stated per degree of freedom because the
#: two differ (2026-08-15 defect fix): the body's yawing couple is destabilizing
#: and OPPOSES the fin's, so ``psi_dd`` is over-stated without it and its
#: inertia is conservative; the body-and-wing side force ADDS to the fin's at
#: ``+beta``, so ``n_y`` is UNDER-stated without it and its inertia is not.
LATERAL_AERO_NOTE = (
    "the fin's sideslip load is SELECT's, unchanged; the wing-body side force "
    "and yawing moment in sideslip are the L-7 term (DATCOM 5.2.1.1 / 5.2.3.1 "
    "from the fuselage outline, aero_coeffs.lateral_body_aero, OFF by default) "
    "-- where it is NOT applied the two lateral degrees of freedom err in "
    "OPPOSITE directions: the yaw acceleration is OVER-STATED (the body's "
    "couple is destabilizing and opposes the fin's) and the inertia it drives "
    "is conservative, while n_y is UNDER-STATED (the body-and-wing side force "
    "adds to the fin's at +beta) so the lateral translational inertia it drives "
    "is NOT conservative on any component -- each by the estimated amount the "
    "case states; where it IS applied the case states the derivatives, the "
    "applied force and couple, and the net fin+body Cn_beta")

#: The applied load's ``source`` tag -- routed to the fuselage member by the LRA
#: exporter like ``fuselage-cm`` and ``body-axial``.
BODY_AERO_SOURCE = "body-aero"
