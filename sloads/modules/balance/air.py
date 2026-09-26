"""Assembly: one flight case, its handed twin, and the case set.

Part of :mod:`sloads.modules.balance` (#191); the subsystem docstring is the
package's. :func:`assemble` builds one condition's applied set and closes it;
:func:`handed_twin` mints the port case as the mirror image of the starboard
one; :func:`build_balanced_cases` walks SELECT's conditions, records what it
skipped, and appends the ground families.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Dict, List, Optional, Sequence

from ... import safety_factors
from ...case_ids import handed_case_id
from ...cg_cases import flight_cases
from ...derived_geometry import require_wing_reference, sync_geometry_derived
from ...export.coordinates import reflect_side
from ...mass_distribution import CaseLoading, derive_case_loadings
from ...models import (
    BalancedCaseResult,
    BalancedLoad,
    CgCase,
    CriticalCondition,
    MissingInputError,
    Project,
    VnPoint,
    WingLoadCase,
)
from ...tail_geometry import HTAIL, VTAIL
from ..rolling import complete_rolling_case
from ..select import default_critical, default_envelope
from ..tail_span import build_tail_span
from ..wing_inertia import WingCaseSources, resolve_wing_cases
from .applied import (
    _flight_loads,
    _mirror,
    _wing_slices,
    body_axial_set,
    body_inertia,
    htail_sets,
    hub_thrust_set,
    place_wing_inertia,
    reflect_load,
    vtail_sets,
    wing_sets,
)
from .closure import _closure, resultant6
from .constants import (
    AILERON_COUPLE_NOTE,
    BALANCED_HTAIL_CONDITIONS,
    BALANCED_VTAIL_CONDITIONS,
    BALANCED_WING_CONDITIONS,
    LATERAL_AERO_NOTE,
    ROLLING_WING_CONDITIONS,
)
from .lateral import LateralAeroTerms, body_aero_loads, lateral_aero_case_note, lateral_aero_terms
from .queries import is_handed, point_mass_self_inertia
from .skipped import SkippedCondition, _skip


def unbalanced_rolling_moment(project: Project, condition: str,
                              point: Optional[VnPoint] = None,
                              vn: Optional[Dict[int, VnPoint]] = None,
                              sources: Optional[WingCaseSources] = None) -> float:
    """The resolved ``UNB`` of wing condition ``condition`` (FAR 23.349), or 0.

    **One owner for both readers** (design note 52, D-52.3): the value the wing
    chain runs -- ``wing_inertia.resolve_wing_cases``, which fills a blank
    ``ACRL`` couple from condition A through ``rolling.complete_rolling_case``
    and keeps an entered one -- so the balanced deck and WINGINER can never
    carry two different moments for one physical condition. Where the wing case
    list does not run the condition (an entered list is a filter, D-63.7, and
    may omit ``ACRL`` while SELECT still names it), the couple is derived by the
    same owner at the balanced case's own V-n ``point``. Before note 52 this read
    the *entered* table alone, and a derived ``ACRL`` assembled symmetric.
    """
    wm = project.wing_mass
    if wm is None:
        return 0.0
    case = next((c for c in resolve_wing_cases(project, wm, sources)
                 if c.name == condition), None)
    if case is None and point is not None and vn is not None:
        case = complete_rolling_case(project, WingLoadCase(name=condition, case=point.case), vn)
    return (case.unbal_moment or 0.0) if case is not None else 0.0


def assemble(project: Project, condition: str, vn: VnPoint,
             loading: CaseLoading, cg: CgCase,
             case_ref=None, unb: float = 0.0,
             lateral: Sequence[BalancedLoad] = (),
             htail: Sequence[BalancedLoad] = (),
             lateral_aero: Optional[LateralAeroTerms] = None,
             extra: Sequence[BalancedLoad] = (),
             sources: Optional[WingCaseSources] = None) -> BalancedCaseResult:
    """Assemble one balanced case and close its residual.

    ``unb`` is the unbalanced rolling moment (FAR 23.349) for an accelerated-roll
    condition; zero makes the case symmetric and is the default, so every
    symmetric caller is unchanged.

    ``lateral`` is the applied side-load set -- the fin distribution of a
    23.441/23.443 condition (B8a-3, :func:`vtail_sets`). The symmetric half of the
    case is assembled from the V-n point exactly as it always was: all four
    v-tail conditions sit at ``n_z ~ 1``, so nothing about the vertical,
    longitudinal or pitching physics changes when a side load is added beside it,
    and ``test_the_symmetric_half_still_closes`` is the guard that it did not.

    ``htail`` is the distributed horizontal-tail load of the 23.427(a)
    unsymmetrical condition (D-R8, :func:`htail_sets`). It **replaces** the
    lumped trim tail load: SELECT's ``RH + LH`` is the condition's whole tail
    load, and applying ``vn.lt`` beside it would carry the balancing part twice.
    The mismatch between the two is the maneuver -- see the module docstring --
    and the pitch degree of freedom of the closure is what reacts it.

    ``lateral_aero`` is the case's L-7 wing-body term (:func:`lateral_aero_terms`):
    when enabled and available its one applied load joins the fin's beside it,
    and either way the case's note says what the term did or would have done
    (decision L-7.16). A caller that passes ``lateral`` without it -- the direct
    per-condition tests -- gets the standing statement alone.

    **Handedness is measured, not declared** (decision L-6): the case gets a hand
    when its *applied* set has lateral content or a net rolling moment, whatever
    put it there -- the aileron couple of ``ACRL``, the fin load of a rudder kick
    or the left/right split of 23.427(a). Before B8a-3 the first two would have
    been separate flags; :func:`is_handed` is the one predicate.
    """
    fl = _flight_loads(project)
    wr = require_wing_reference(project)
    notes: List[str] = []

    wing_r, panel_both, _cm_free = wing_sets(project, vn, sources)
    wing_r, scale_notes = place_wing_inertia(wing_r, loading, project, panel_both, vn.nz)
    notes += scale_notes

    loads: List[BalancedLoad] = list(wing_r) + _mirror(wing_r)
    if htail:
        loads += list(htail)
        applied_ht = math.fsum(ld.fz for ld in htail)
        notes.append(
            f"UNSYMMETRICAL (FAR 23.427(a)): the applied tail load is SELECT's "
            f"own left/right split, {applied_ht:+.0f} lb, and it REPLACES the "
            f"trim tail load {vn.lt:+.0f} lb this V-n point balances at. The "
            f"difference is the maneuver -- 23.427(a) distributes a maneuver "
            f"tail load, and the airplane is not in trim under it -- so the "
            f"pre-closure Fz and My are that difference in full and are NOT a "
            f"balance error: the vertical and pitch degrees of freedom of the "
            f"closure are the motion it causes. The 1 % residual gate is on the "
            f"case's trim half, which is unchanged")
    else:
        loads.append(BalancedLoad(x=fl.xtc, y=0.0, z=wr.zw, fz=vn.lt,
                                  source="tail-air", side="C"))
    loads += body_inertia(loading, project, vn.nz)

    # The fuselage's share of the trim pitching moment: what the airplane-less-tail
    # Cm carries that the distributed wing does not (see the module docstring).
    wing_about_ac = math.fsum(
        ld.my + (ld.z - wr.zw) * ld.fx - (ld.x - wr.xw) * ld.fz
        for ld in loads if ld.source == "wing-air")
    fuselage_cm = vn.m_wf - wing_about_ac
    loads.append(BalancedLoad(x=wr.xw, y=0.0, z=wr.zw, my=fuselage_cm,
                              source="fuselage-cm", side="C"))

    # The airplane's NON-WING drag (see "The body-axial load" in the docstring).
    body_axial, delta_cd, body_axial_clamped, drag_loads, drag_notes = body_axial_set(
        loads, project, vn, loading)
    loads += drag_loads
    notes += drag_notes

    # The user-entered engine thrust (backlog #10) -- the assembled model's only
    # forward force, and the only load here that nothing balances by design.
    thrust_loads, thrust_notes = hub_thrust_set(project, cg)
    loads += thrust_loads
    notes += thrust_notes

    # The aileron's rolling moment (FAR 23.349), applied as a labelled free
    # couple at the wing aerodynamic centre. Sign: WINGINER's unit-roll inertia
    # set produces a rolling moment of exactly ``+UNB`` (verified: its
    # normalisation makes ``sum(y*fz_r)`` equal 100,000 for a unit case), and
    # NETLOADS enters inertia opposing the air load -- so the *aero* moment this
    # is the couple for is ``-UNB``. The closure's roll DOF then reproduces
    # WINGINER's distribution strip for strip, which is the check that this sign
    # is right rather than merely consistent.
    if unb:
        loads.append(BalancedLoad(x=wr.xw, y=0.0, z=wr.zw, mx=-unb,
                                  source="aileron-roll", side="C"))
        notes.append(f"aileron rolling moment {-unb:+.0f} lb-in applied as a "
                     f"lumped free couple: {AILERON_COUPLE_NOTE}")

    body_side_force = body_yaw_moment_ref = 0.0
    beta_deg: Optional[float] = None
    cn_beta_net: Optional[float] = None
    if lateral:
        loads += list(lateral)
        notes.append(LATERAL_AERO_NOTE)
        if lateral_aero is not None:
            body_loads = body_aero_loads(lateral_aero)
            loads += body_loads
            notes.append(lateral_aero_case_note(lateral_aero))
            beta_deg = lateral_aero.beta_deg
            cn_beta_net = lateral_aero.cn_beta_net
            if body_loads:
                body_side_force = lateral_aero.side_force
                body_yaw_moment_ref = lateral_aero.yaw_moment_ref

    # Loads a family applies beside its defining set -- the one-engine-out
    # case's live-thrust / windmill-drag pair (design note 66, D-66.12) --
    # present before the residual is summed, so the closure reacts them.
    loads += list(extra)

    wm, geometry, _ = _wing_slices(project)
    geom = geometry.by_name(wm.surface)
    semi_span = geom.leading_edge[-1][1] if geom else 0.0
    ref = (cg.xcg, 0.0, cg.zcg)
    handed = is_handed(loads, abs(vn.nz * cg.weight_lb), semi_span)
    residual = resultant6(loads, ref)
    fx, fy, fz, mx, my, mz = residual
    n, omega_dot, tensor = _closure(
        loads, cg, residual, point_mass_self_inertia(loading, project))

    return BalancedCaseResult(
        label=condition, vn_case=vn.case, cg=cg.name, nz=vn.nz,
        weight_lb=cg.weight_lb, mac=wr.mac, cg_x=cg.xcg, cg_z=cg.zcg,
        semi_span=semi_span, loads=loads,
        residual_fz=fz, residual_fx=fx, residual_my=my,
        residual_fy=fy, residual_mx=mx, residual_mz=mz,
        delta_n=n[2], delta_nx=n[0], delta_ny=n[1],
        p_dot=omega_dot[0], q_dot=omega_dot[1], r_dot=omega_dot[2],
        closure_inertia=tensor,
        unbal_moment=unb, fuselage_cm=fuselage_cm,
        body_axial=body_axial, delta_cd=delta_cd,
        body_axial_clamped=body_axial_clamped,
        body_side_force=body_side_force,
        body_yaw_moment=(body_yaw_moment_ref
                         - (cg.xcg - (lateral_aero.x_ref if lateral_aero else cg.xcg))
                         * body_side_force),
        beta_deg=beta_deg, cn_beta_net=cn_beta_net,
        case_ref=_handed_ref(case_ref, "R") if handed else case_ref,
        hand="R" if handed else "", notes=notes,
    )


def _handed_ref(ref, hand: str):
    """``CaseRef`` with the handedness suffix on its id (B-7), or ``None``."""
    if ref is None:
        return None
    return replace(ref, case_id=handed_case_id(ref.case_id, hand))


def _flip(value: float) -> float:
    """``-value``, with IEEE negative zero normalised away.

    A symmetric quantity on a handed pair is exactly ``0.0``, and negating it
    gives ``-0.0`` -- which renders as ``-0.00000`` in the port twin's deck
    header beside the starboard twin's ``+0.00000``, reading as a difference
    where there is none. ``-0.0 + 0.0`` is ``+0.0``; adding zero is the identity
    on every other value.
    """
    return -value + 0.0


def handed_twin(case: BalancedCaseResult, case_ref=None) -> BalancedCaseResult:
    """The opposite-hand twin of an antisymmetric case, by reflection (B-6).

    ``case_ref`` overrides the twin's identity instead of deriving it by suffixing
    the computed case's id, and exists for exactly one family: the 23.485 side
    condition, whose twin **already has an id of its own** (``LG-20`` beside
    ``LG-19``) because LANDLOAD supplies both drift directions. Minting
    ``LG-19L``/``LG-19R`` beside a shipped ``LG-20`` would put two ids on one
    physical condition, which M4-2 decision 1 forbids. Everywhere else the twin is
    derived and this stays ``None`` (decision G-8).

    Derived from the computed case rather than recomputed, which is the whole
    point: the oracle-locked FAR 23 path never sees handedness. Every quantity
    that is odd under the mirror flips through the single owner in
    :mod:`sloads.export.coordinates` -- positions, side tags, the applied couple,
    the fin's side load and torsion, the lateral relief -- and everything even is
    untouched, so the twin's vertical, longitudinal and pitching balance is
    *identical* and only its lateral half reverses. On a v-tail case that is the
    ``-beta`` condition of a ``+beta`` one, got for the cost of a sign flip and
    without SELECT ever seeing the question.
    """
    if not case.hand:
        raise ValueError(
            f"balanced case {case.label} has no hand -- a symmetric case is its "
            "own mirror image, and minting a twin for it would put the same "
            "load set in the deck twice")
    ref = case.case_ref
    twin_ref = (case_ref if case_ref is not None
                else _handed_ref(ref, reflect_side(case.hand)))
    return replace(
        case,
        loads=[reflect_load(ld) for ld in case.loads],
        residual_mx=-case.residual_mx,
        residual_mz=-case.residual_mz,
        residual_fy=_flip(case.residual_fy),
        delta_ny=_flip(case.delta_ny),
        p_dot=_flip(case.p_dot),
        r_dot=_flip(case.r_dot),
        unbal_moment=-case.unbal_moment,
        body_side_force=_flip(case.body_side_force),
        body_yaw_moment=-case.body_yaw_moment,
        beta_deg=None if case.beta_deg is None else _flip(case.beta_deg),
        hand=reflect_side(case.hand),
        case_ref=twin_ref,
    )


def _tail_distributions(project: Project, component: str, builder) -> dict:
    """``{condition label: load set}`` for one empennage surface, or ``{}``.

    Built once per project rather than per case: ``build_tail_span`` re-resolves
    both planforms and re-runs SELECT, and the conditions of a surface share V-n
    points. A project whose chain does not exist yields nothing here and simply
    assembles no case of that family -- the same "the whole chain must exist"
    rule the symmetric families follow.
    """
    try:
        spans = build_tail_span(project)
    except MissingInputError:
        return {}
    return {r.case: builder(r) for r in spans.get(component, ())}


def _vtail_distributions(project: Project) -> dict:
    """``{condition label: fin load set}`` for every v-tail condition, or ``{}``.

    Built once per project rather than per case: ``build_tail_span`` re-resolves
    the planform and re-runs SELECT, and three of the four conditions share a
    V-n point. A project with no ``vtail_loads`` yields nothing here and simply
    assembles no lateral case -- the same "the whole chain must exist" rule the
    symmetric families follow.
    """
    return _tail_distributions(project, VTAIL, vtail_sets)


def _htail_distributions(project: Project) -> dict:
    """``{condition label: h-tail load set}`` for every h-tail condition (D-R8).

    Only ``UNSYMMETRICAL`` is ever asked for (:data:`BALANCED_HTAIL_CONDITIONS`);
    the whole table is built because the underlying span build produces it in one
    pass either way.
    """
    return _tail_distributions(project, HTAIL, htail_sets)


def build_balanced_cases(
        project: Project,
        skipped: Optional[List[SkippedCondition]] = None,
) -> List[BalancedCaseResult]:
    """One :class:`BalancedCaseResult` per condition SELECT picked -- **two** for
    a condition that has a hand.

    Three families, assembled by the same machinery (B8a-3, D-R8):

    * the **wing** conditions of :data:`BALANCED_WING_CONDITIONS` -- symmetric,
      plus ``ACRL``'s applied aileron couple;
    * the **vertical-tail** conditions of :data:`BALANCED_VTAIL_CONDITIONS` --
      the fin's distributed side load riding on the same symmetric case its V-n
      point already describes;
    * the **horizontal-tail** condition of :data:`BALANCED_HTAIL_CONDITIONS` --
      FAR 23.427(a)'s left/right split, distributed over the full-span tail in
      place of the lumped trim tail load every other case carries.

    A condition is assembled only when the whole chain exists for it: SELECT
    named it, it has a V-n point, and its CG case resolves to a **derivable**
    loading (step C1). A case whose CG the weight database cannot produce has no
    honest inertia set, and inventing one would put fictitious mass into the very
    balance the case exists to demonstrate.

    A case with lateral content in its applied set is emitted as a **handed
    pair** -- the computed starboard case and its port mirror (B-6/B-7). A
    condition that is merely *allowed* a hand and turns out not to have one (a
    rolling condition whose ``UNB`` is zero) is emitted once, unhanded: the twins
    exist for cases that have a hand.

    **Every condition that does not assemble is recorded** (review F-C7): pass a
    list as ``skipped`` and it is extended with one :class:`SkippedCondition` per
    dropped condition, in SELECT's order. Before this, a missing V-n point or a
    non-derivable loading dropped a condition out of the primary deliverable in
    silence, and only the shipped fixtures' drop set was pinned. Callers that
    want the record alone use :func:`skipped_conditions`.
    """
    sync_geometry_derived(project)
    if project.flight_loads is None or project.wing_mass is None:
        raise MissingInputError("balance needs 'flight_loads' and 'wing_mass'")
    # Both through their single owners (review F-C6). ``project.envelope or
    # build_envelope(project)`` duplicated the owner's rule and got it wrong at the
    # edge: a persisted envelope carrying an *empty* ``vn`` was accepted, and every
    # condition then dropped out of the assembly under a misleading "nothing to
    # balance". ``default_envelope`` rebuilds in that case; ``default_critical``
    # applies the same rule to the critical set.
    envelope = default_envelope(project)
    critical = default_critical(project)
    vn = {p.case: p for p in envelope.vn}
    cgs = {c.name: c for c in flight_cases(project)}
    loadings = {ld.name: ld for ld in derive_case_loadings(project)}
    vtails = _vtail_distributions(project)
    htails = _htail_distributions(project)
    # What ``wing_inertia.wing_case_sources`` would resolve, from the envelope
    # and critical set already in hand: every case's wing set asks for the wing
    # case list, and without this each ``assemble`` rebuilt the V-n matrix and
    # SELECT's set from scratch -- 46 envelope builds for the ATR's deck once
    # the engine families (design note 66) added their parents.
    sources = WingCaseSources(
        vn=vn, wing_conditions=[c for c in critical.conditions if c.component == "wing"])

    record: List[SkippedCondition] = skipped if skipped is not None else []

    from .engine_out_cases import build_engine_out_cases, is_engine_out_condition

    out: List[BalancedCaseResult] = []
    engine_out: List[CriticalCondition] = []
    for cond in critical.conditions:
        if is_engine_out_condition(cond):
            # ONENGOUT's 23.367 conditions: a family of their own, appended
            # last (design note 66, #285).
            engine_out.append(cond)
            continue
        unb = 0.0
        lateral: Sequence[BalancedLoad] = ()
        htail: Sequence[BalancedLoad] = ()
        lateral_cond: Optional[CriticalCondition] = None
        if cond.component == "wing" and cond.label in BALANCED_WING_CONDITIONS:
            pass    # a rolling condition's couple is resolved at its V-n point below
        elif cond.component == VTAIL and cond.label in BALANCED_VTAIL_CONDITIONS:
            lateral = vtails.get(cond.label, ())
            if not lateral:
                record.append(_skip(cond, "no-fin-loads"))
                continue
            lateral_cond = cond
        elif cond.component == HTAIL and cond.label in BALANCED_HTAIL_CONDITIONS:
            htail = htails.get(cond.label, ())
            if not htail:
                record.append(_skip(cond, "no-htail-loads"))
                continue
        elif cond.component == HTAIL:
            record.append(_skip(cond, "htail-symmetric"))
            continue
        else:
            record.append(_skip(cond, "out-of-family"))
            continue
        point = vn.get(cond.case) if cond.case is not None else None
        if point is None:
            record.append(_skip(cond, "no-vn-point"))
            continue
        cg = cgs.get(point.cg)
        loading = loadings.get(point.cg)
        if cg is None or loading is None:
            record.append(_skip(cond, "no-cg-case"))
            continue
        if not loading.derivable:
            record.append(_skip(cond, "loading-not-derivable"))
            continue
        if cond.component == "wing" and cond.label in ROLLING_WING_CONDITIONS:
            unb = unbalanced_rolling_moment(project, cond.label, point, vn, sources)
        terms = (lateral_aero_terms(project, lateral_cond, point)
                 if lateral_cond is not None else None)
        case = assemble(project, cond.label, point, loading, cg, sources=sources,
                        case_ref=cond.case_ref, unb=unb, lateral=lateral,
                        htail=htail, lateral_aero=terms)
        out.append(case)
        if case.hand:
            out.append(handed_twin(case))
    # The ground families join the same deck (decision G-1) -- they are balanced
    # free-free cases like every other, and building them in a per-component view
    # first would put the primary deliverable second. They are appended rather
    # than interleaved so the flight families' order, and therefore every shipped
    # deck's existing subcase sequence, is untouched.
    #
    # Imported here rather than at the top because the two files genuinely need
    # each other: this one builds the case set the ground families belong to,
    # and ``ground`` mints its twins with ``handed_twin``/``_handed_ref`` from
    # here. The cycle is the families' real shape -- one assembly machinery, two
    # sources of case -- so it is deferred at the single call rather than broken
    # by moving the twins somewhere neither family owns (#191).
    from .ground import build_ground_cases

    out += build_ground_cases(project, record)
    # The engine-mount family joins last (design note 66, D-66.2): appended, so
    # every shipped deck's subcase sequence ahead of it is untouched.
    from .engine_cases import build_engine_cases

    out += build_engine_cases(project, critical.conditions, vn, cgs, loadings, record,
                              sources=sources)
    out += build_engine_out_cases(project, engine_out, vn, cgs, loadings, vtails, record,
                                  sources=sources)
    # Every case states its own factor (design note 66, D-66.1): the governing
    # table's answer for the FAR reference its ``CaseRef`` carries -- the same
    # owner every other deliverable is stamped by (note 48), so the deck header's
    # basis sentence and the case can never disagree. Before #286 nothing set
    # it and every assembled case said SF 1.5 by the field's default -- right for
    # every family then, wrong the moment a 23.367(a)(2) case (already
    # ultimate) joins.
    safety_factors.stamp(project, out)
    return out
