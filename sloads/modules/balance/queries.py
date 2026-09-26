"""What a case *is*: the predicates and labels every surface reads.

Part of :mod:`sloads.modules.balance` (#191); the subsystem docstring is the
package's. These are the single owners `CONVENTIONS.md` §7 names for handedness,
the residual-gate family, the source-case label and what makes a case lateral,
ground or powered -- one reading, so the report, the deck header and the case
table cannot disagree about what a case was.
"""

from __future__ import annotations

import math
from typing import List, Sequence, Tuple

from ...mass_distribution import CaseLoading, assembly_distributes_mass, component_of, reacted_parts
from ...models import BalancedCaseResult, BalancedLoad, Project
from ...rigid_body import SelfInertia
from .applied import HUB_THRUST_SOURCE
from .constants import HANDEDNESS_TOL


def is_unsymmetrical_htail(case: BalancedCaseResult) -> bool:
    """Does this case carry the distributed 23.427(a) tail load? (D-R8)

    The ``htail-air`` tag has one reader -- here -- so the deck header, the case
    table, the report and the gates all agree on what the family *is*, the same
    single-owner rule :func:`is_lateral` follows for the fin.
    """
    return any(ld.source == "htail-air" for ld in case.loads)


def htail_load(case: BalancedCaseResult) -> float:
    """The **net** applied horizontal-tail load; ``0.0`` when there is no set.

    Equal to SELECT's ``RH + LH`` for a 23.427(a) case, which is the identity the
    composition gate asserts. Use :func:`is_unsymmetrical_htail` to ask whether
    the case *has* the set: a tail load that happened to sum to zero would still
    be one, because it is the distribution that is handed.
    """
    return math.fsum(ld.fz for ld in case.loads if ld.source == "htail-air")


def htail_side_loads(case: BalancedCaseResult) -> Tuple[float, float]:
    """``(starboard, port)`` halves of the applied h-tail load -- SELECT's own
    ``RH``/``LH`` on the computed case, and swapped on its port twin.

    Split by the strip's side of the centreline rather than by its ``side`` tag,
    so the two agree only because the tag is right -- a reflection that failed to
    swap the tags would show up here rather than being echoed back.
    """
    rh = math.fsum(ld.fz for ld in case.loads if ld.source == "htail-air" and ld.y > 0)
    lh = math.fsum(ld.fz for ld in case.loads if ld.source == "htail-air" and ld.y < 0)
    return rh, lh


def is_powered(case: BalancedCaseResult) -> bool:
    """Does this case carry an applied engine thrust? (backlog #10)

    The one reader of :data:`HUB_THRUST_SOURCE`, so the deck header, the case
    table, the report and the gates cannot disagree about what a powered case
    is -- the same single-owner rule :func:`is_ground` follows for the gear and
    :func:`is_unsymmetrical_htail` for the 23.427(a) tail.

    It matters most to the gates. A powered case is **not in longitudinal or
    pitch trim by construction** (:func:`hub_thrust_set`): the V-n point it is
    assembled at is thrust-free, so the applied thrust and its couple are the
    pre-closure ``Fx`` and ``My`` in full, reacted by ``delta_nx`` and
    ``q_dot``. :data:`RESIDUAL_GATE` therefore does not apply to its pitch
    residual, exactly as it does not to a 23.427(a) case's.
    """
    return any(ld.source == HUB_THRUST_SOURCE for ld in case.loads)


def hub_thrust(case: BalancedCaseResult) -> float:
    """The net applied thrust, **lb forward**; ``0.0`` on an unpowered case.

    Positive forward, i.e. the negated sum of the hub forces' ``fx`` -- read as
    thrust rather than as the ``x`` force it is applied as, because that is the
    number the user entered and the sense ``n_x = (D - sum T)/W`` reads in.
    """
    return -math.fsum(ld.fx for ld in case.loads
                      if ld.source == HUB_THRUST_SOURCE)


def is_ground(case: BalancedCaseResult) -> bool:
    """Does this case carry applied gear reactions? (i.e. is it a ground case.)

    The ``gear-*`` tag has one reader -- here -- so the deck header, the case
    table, the report and the gates all agree on what the ground family *is*, the
    same single-owner rule :func:`is_lateral` follows for the fin and
    :func:`is_unsymmetrical_htail` for the 23.427(a) tail.

    It matters most to the gates. A ground case has **nothing to trim against**,
    so :data:`RESIDUAL_GATE` -- which asks "did the aero and inertia that should
    have cancelled actually cancel?" -- has no meaning for it: the pre-closure
    residual is the whole applied gear load by construction, exactly as a rudder
    kick's is the whole fin load. The gate that does apply is G-6's, and it is
    stronger: the solved rigid-body field, rotated back to the ground line, must
    reproduce LANDLOAD's ``NVP``/``NDP``/``NS`` -- which it does exactly.
    """
    return any(ld.source.startswith("gear-") for ld in case.loads)


def is_engine_mount(case: BalancedCaseResult) -> bool:
    """Is this an engine-mount case (design note 66, #286)?

    Read off the case's identity -- the ``EM`` family ENGLOADS mints -- not off
    its loads: an EM case is a scaled flight case plus the engine's own loads,
    and a flight case with entered hub thrust also carries ``engine-thrust``.
    """
    ref = case.case_ref
    return ref is not None and ref.component == "engine_mount"


def residual_gate_applies(case: BalancedCaseResult) -> bool:
    """Is this case's pre-closure ``Fz``/``My`` residual a **gate-comparable**
    trim statement? (CR-C-2, #41.)

    THE owner of the :data:`RESIDUAL_GATE` exemption. The families above each
    state their own exemption in prose -- the deck ``$`` header, the case-table
    note, the report and the GUI all repeated it -- and every surface that
    summarises a *worst* residual has to agree on which cases that maximum is
    taken over. It did not: §6 maximised over all cases (143.885 % on
    ``ga6_normal``, which is the 23.427(a) maneuver), the Balanced Cases page
    excluded only the 23.427(a) family (100.000 %, which is a ground case's
    applied gear load), and the gate-applicable family sat at 0.624 %.

    Exempt, because their pre-closure ``Fz``/``My`` **is an applied load in
    full** and no arithmetic makes it comparable to 1 %:

    * :func:`is_ground` -- the gear reaction; nothing trims against a wheel.
    * :func:`is_unsymmetrical_htail` -- the 23.427(a) maneuver tail load, which
      replaces the trim load rather than adding to it.
    * :func:`is_powered` -- the thrust couple about the CG, applied at a
      thrust-free V-n point.

    **A lateral case is not exempt, and that is deliberate.** What 23.441/23.443
    exempts is the ``Fy``/``Mz`` pair -- and neither appears in
    :attr:`~BalancedCaseResult.force_residual_fraction` (``|Fz|/n*W``) or
    :attr:`~BalancedCaseResult.moment_residual_fraction` (``|My|/(n*W*MAC)``).
    Those two measure precisely the *symmetric half* that :func:`is_lateral`'s
    own docstring names as the gate that does apply, so excluding the family here
    would delete a live gate rather than correct one. It passes on every shipped
    fixture (worst 0.614 %), which is the check working, not an argument for
    turning it off.
    """
    return not (is_ground(case) or is_unsymmetrical_htail(case) or is_powered(case)
                or is_engine_mount(case))


#: The exempt families in the order :func:`residual_gate_exemptions` states them,
#: as ``(predicate, phrase)``. One row per exemption, so a surface never spells a
#: family name itself and a new exemption reaches all of them at once.
_GATE_EXEMPTIONS = (
    (is_ground, "ground (FAR 23.471-23.499; the applied gear load in full)"),
    (is_unsymmetrical_htail,
     "unsymmetrical h-tail (FAR 23.427(a); the maneuver tail load in full)"),
    (is_powered, "powered (the applied thrust couple in full)"),
    (is_engine_mount,
     "engine mount (a scaled flight case plus the engine's own loads; the "
     "flight case it scales is gated as itself)"),
)


def residual_gate_family(
    cases: Sequence[BalancedCaseResult],
) -> Tuple[List[BalancedCaseResult], List[BalancedCaseResult]]:
    """``(judged, clamped)`` -- the gated cases split by whether the **flat**
    acceptances (:data:`FORCE_RESIDUAL_ACCEPTANCE`, :data:`RESIDUAL_GATE`) are
    the right thing to judge them against.

    A case whose forward non-wing axial force was **not applied** (design note 20
    D-4: the trim ``alpha`` is outside :data:`POLAR_TRUSTED_ALPHA_DEG` and the
    airplane-less-tail polar less the wing strips came out forward) is out of trim
    by exactly that clamped force and the couple it made about the CG. Its
    residuals are therefore a *known, measured* quantity, not a balance quality:
    they are gated per case, against what was measured when the clamp was decided
    (``tests/test_balance.py::_CLAMPED_BODY_AXIAL``). Judging them against the
    flat acceptance instead reports a modelling decision as a failure -- the
    CR-C-2 defect again, one layer down. Split here rather than at each surface so
    the report and the GUI cannot draw the line differently.

    ``judged``: pitch 0.07-0.84 % and force 0.48-2.36 % across the six fixtures.
    ``clamped``: at most three cases on a fixture, none on ``ga6_normal``.
    """
    gated = [c for c in cases if residual_gate_applies(c)]
    return ([c for c in gated if not c.body_axial_clamped],
            [c for c in gated if c.body_axial_clamped])


def residual_gate_exemptions(cases: Sequence[BalancedCaseResult]) -> List[str]:
    """``["27 ground (…)", "2 unsymmetrical h-tail (…)"]`` -- the exempt families
    actually present in ``cases``, counted, for a surface to state beside the
    worst gated residual.

    Stating the standing beside the number is the point: a reader who is shown
    "0.624 % over 7 cases" and not told that 27 ground cases sit at 100 % by
    construction has been given a true number and a false impression.
    """
    out = []
    for predicate, phrase in _GATE_EXEMPTIONS:
        n = sum(1 for c in cases if predicate(c))
        if n:
            out.append(f"{n} {phrase}")
    return out


#: What the integer in :attr:`BalancedCaseResult.vn_case` actually names, by
#: family (R6-C3). The field holds the **source case number**: FLTLOADS' V-n
#: point for a flight case, LANDLOAD's case number for a ground one -- two
#: different tables that both number from 1, so a label naming the wrong one
#: sends a reader to a real and unrelated row.
FLIGHT_SOURCE_STEM = "V-n point"
GROUND_SOURCE_STEM = "LANDLOAD case"


def source_case_name(case_number: int, ground: bool, *,
                     short: bool = False) -> str:
    """The source case, named as the family that produced it names it (R6-C3).

    **The one owner of this wording.** Every surface that prints the number --
    the assembled deck's ``$`` header and case map, :func:`run`'s condition
    titles, the balanced-case rows table and :attr:`SkippedCondition.name` --
    goes through here, so none of them can drift into calling a LANDLOAD case a
    V-n point again. Display wording only: the number and the case identity are
    untouched (the join key is the ``CaseRef`` id, not this string).

    ``short`` is the compact form the case map and the parenthesised titles use.
    The ground stem has no short form on purpose -- abbreviating it would invent
    a fourth name for the same number, and it is the family that was being
    mislabelled.
    """
    if ground:
        return f"{GROUND_SOURCE_STEM} {case_number}"
    stem = "V-n" if short else FLIGHT_SOURCE_STEM
    return f"{stem} {case_number}"


def case_source_name(case: BalancedCaseResult, *, short: bool = False) -> str:
    """:func:`source_case_name` for an assembled case, family read off the case."""
    return source_case_name(case.vn_case, is_ground(case), short=short)


def is_lateral(case: BalancedCaseResult) -> bool:
    """Does this case carry an applied fin load? (i.e. is it one of B8a-3's.)

    The ``vtail-air`` tag has exactly one reader -- here and in
    :func:`vtail_load` -- so the deck header, the row table and the gates all agree
    on what a lateral case *is* (``CLAUDE.md`` practice 3). Asked of the tag and
    not of :func:`vtail_load`'s net, because a fin set whose strips happened to sum
    to zero would still be a lateral case: it is the distribution that is
    handed, not the resultant (the same distinction :func:`is_handed` draws).
    """
    return any(ld.source == "vtail-air" for ld in case.loads)


def vtail_load(case: BalancedCaseResult) -> float:
    """The **net** applied fin side load; ``0.0`` when there is no fin set.

    The number the deck reports and the gates pin. Use :func:`is_lateral` to ask
    whether the case *has* a fin set.
    """
    return math.fsum(ld.fy for ld in case.loads if ld.source == "vtail-air")


def is_handed(applied: Sequence[BalancedLoad], n_w: float,
              ref_length: float = 0.0) -> bool:
    """Does this **applied** load set have a hand? (decision L-6, D-R8)

    Three sources of handedness, and the third is what D-R8 added: a free
    ``mx``/``mz`` (the aileron couple), lateral force content (a fin load), and a
    **net rolling moment made by the distribution itself** -- which is the only
    thing the 23.427(a) h-tail case has. Its asymmetry is 100 % of half the tail
    load on one side against 72-80 % on the other, all of it in ``fz`` at
    opposite ``y``: no side force, no free moment, and a predicate reading only
    the first two would mint it unhanded and emit one twin where 23.427(a)
    requires both sides considered.

    ``ref_length`` is the semi-span the rolling moment is judged against; with
    none supplied there is no length scale to form a fraction from, so the roll
    test is skipped rather than run against a number whose units decide the
    answer. :func:`assemble` always supplies it.

    Two properties, both deliberate and both lost by the obvious alternatives:

    **It reads the distribution, not the resultant.** ``ga6_normal``'s
    ``YAW TO SIDESLIP`` nets only -97.8 lb of side force out of parts worth
    -683 (yaw) and +586 (rudder), so ``sum|fy| ~ 1270`` while ``|sum fy| ~ 98``.
    A net-based predicate would mint a rudder-kick case *unhanded* on the
    strength of a near-cancellation and assemble it as a symmetric one -- the
    same silent-symmetry failure plan 11 §10 records for ``TORS``, arrived at
    from the opposite direction.

    **It is evaluated pre-closure, so it cannot feed on its own output.** From
    B8a-2 the closure gives any rolling case a lateral relief field, so a
    predicate reading the *final* load set would find lateral content in every
    case that rolls and hand every one of them.

    The threshold is a fraction of ``n*W`` rather than an absolute pound, so it
    means the same thing on a 3,400 lb trainer and a 33,000 lb jet.
    """
    # The free-moment test reads the **net**, not "any load carries one". It was
    # ``any(ld.mx or ld.mz ...)`` until the ground families arrived, which was
    # indistinguishable while the aileron couple was the suite's only free
    # ``mx``: one lumped couple at the centreline is its own net. A ground case
    # transfers every wheel reaction from its contact patch to its trunnion with
    # a lever-arm couple, so *both* main wheels carry an ``mx`` -- equal and
    # opposite, cancelling exactly -- and an "any" test minted every symmetric
    # level-landing case handed, emitting a twin that is the same load set
    # mirrored onto itself. The net is the question that was always meant.
    free = (math.fsum(ld.mx for ld in applied), math.fsum(ld.mz for ld in applied))
    if ref_length <= 0.0:
        if any(free):
            return True
    elif max(abs(v) for v in free) > HANDEDNESS_TOL * n_w * ref_length:
        return True
    if math.fsum(abs(ld.fy) for ld in applied) > HANDEDNESS_TOL * n_w:
        return True
    # The rolling test reads the **net**, unlike the lateral one above, and for
    # the opposite reason: a mirror-symmetric set cancels to exactly zero here
    # (each pair contributes ``y*f + (-y)*f``), so the net is a clean signal
    # rather than a near-cancellation of large parts. Measured, the two
    # populations do not overlap: symmetric wing cases net 1e-17 of ``n*W*b/2``
    # in roll and the 23.427(a) case nets 6e-3 to 1.7e-2.
    if ref_length <= 0.0:
        return False
    roll = math.fsum(ld.mx + ld.y * ld.fz - ld.z * ld.fy for ld in applied)
    return abs(roll) > HANDEDNESS_TOL * n_w * ref_length


def point_mass_self_inertia(loading: CaseLoading, project: Project):
    """``[((x, y, z), SelfInertia)]`` for every item carried as a point mass.

    Decision **L-3**: an item the assembly does not spread still resists angular
    acceleration about its own centre, and that resistance has no other carrier
    in the model. Items with no entered inertia are dropped rather than emitted
    as zeros, so the deck gains a ``MOMENT`` card only where the database
    actually says something -- on ``ga6_normal`` that is a handful of lumps
    worth 13.3 % of ``Izz``, and on ``concept_regional_jet`` it is nothing at
    all, because that database enters no self-inertias.
    """
    out = []
    for it in reacted_parts(loading.items, project):
        if assembly_distributes_mass(component_of(it, project)):
            continue
        if it.ixx or it.iyy or it.izz:
            out.append(((it.x, it.y, it.z),
                        SelfInertia(it.ixx, it.iyy, it.izz)))
    return out
