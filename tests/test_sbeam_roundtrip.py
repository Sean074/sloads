"""The round-trip gate: exported decks solved in the **real** sbeam.

Design note: ``docs/40_history/17_sbeam_roundtrip_ci_harness_plan.md``
(decisions S-1...S-9, assertions §4). Machinery:
:mod:`sloads.export.roundtrip`. Sibling gate, card-text only:
``tests/test_export_equilibrium.py``.

The mission's core claim is that *an exported deck solves in sbeam with verified
global equilibrium, continuously in CI*. Until this module that rested on a
manual check performed once, in 2026, and never repeated. What is new here is
not the physics -- the 2026-08-08 spike found the round trip already agreed
exactly -- but that it is now a standing gate: the day a card format, a GID
scheme, a unit factor or a case-control block drifts, this goes red.

Why a solver, when the card sum already closes
----------------------------------------------
``test_export_equilibrium`` re-derives each deck's resultant from its own card
text. That catches suppression, truncation, SID misrouting and an inconsistent
unit set. It cannot catch what only another program's reader can: a card sbeam
rejects, a ``LOAD`` id no ``SUBCASE`` selects, a GID that resolves to nothing, a
frame or sign convention that differs from the one the deck assumes. And it is
blind to whether the deck is *solvable* at all.

The strongest assertions here are the ones with two independent producers:

* **W-c / W-d** compare a solver-recovered internal load against the **NETLOADS
  quadrature** (``r.stations[...]``). The deck's cards come from
  ``wing_nodal_loads``, the target from the cumulative table -- different code.
* **B-c** does the same along the fuselage beam, station by station: sbeam
  reassembles the Ch 15 cumulative shear and bending from the ``FORCE`` cards
  and the ``GRID`` coordinates alone, and it must reproduce ``body_loads``'
  table. (The design note asked only for "aft-most element shear ~ 0" here; that
  turned out to be neither true nor meaningful -- the last element carries the
  last station's load -- while the whole-beam comparison is both, so it is what
  is asserted. See :func:`test_body_deck_recovers_the_cumulative_beam`.)
* **B-b** and the assembled leg target the constant **zero**, which no
  producer can bias.

Scope (S-2/S-3/S-4): ``ga6_normal`` + ``concept_regional_jet``, Imperial + SI,
across the wing stick deck, test-only body/tail wrappers, and the assembled
full-span deck; the wing leg adds ``atr42_100`` and ``concept_heavy`` for the
routes that pair cannot reach (see ``WING_MATRIX``). Control-surface decks are
permanently out -- their chordwise
``x`` is a fraction of chord with no chord length on the result, so there is no
geometry to solve (S-3).

Tolerances are :mod:`sloads.export.equilibrium`'s, not this file's, so the two
export gates can never disagree about what "equal" means.
"""

import math
import os
import re
import sys
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from sloads import io
from sloads.export import mass_cards as mc
from sloads.export.balanced_deck import (
    balanced_deck,
    case_sids,
)
from sloads.export.coordinates import (
    to_force,
)
from sloads.export.equilibrium import (
    closes,
    parse_cards,
    resultant,
)
from sloads.export.roundtrip import (
    solve_deck,
    total_reaction,
)
from sloads.mass_distribution import derive_case_loadings
from sloads.modules.balance import (
    build_balanced_cases,
    is_lateral,
    vtail_load,
)
from sloads.modules.body_loads import build_body_loads
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.net_loads import build_net_loads, loads_ref_axis_results
from sloads.modules.select import build_critical
from sloads.modules.taildist import build_tail_chordwise
from sloads.units import Channel, UnitSystem, deliverable_units

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Decision S-4. ``ga6_normal`` is the FAR23 Appendix-A oracle fixture;
#: ``concept_regional_jet`` is the flagship concept fixture and the mission's own
#: subject. ``concept_heavy`` is wing-only (see ``WING_MATRIX``); the twins add
#: solve time without adding a deck family.
MATRIX = ("ga6_normal.project.json", "concept_regional_jet.project.json")

#: The wing leg adds two fixtures, each for a route the MATRIX pair cannot reach.
#:
#: ``atr42_100`` is the only fixture whose wing hangs **concentrated** masses
#: (engines, nacelles, wing fuel), and therefore the only one whose deck carries
#: the offset-couple ``MOMENT`` cards that restore their lever arms. Both MATRIX
#: fixtures are mass-free, so before this the solver leg could not tell whether
#: sbeam *honours* an ``Mx`` component or silently drops it -- and W-d, which
#: compares element 1's end-B bending with the NETLOADS root ``Mxx``, is exactly
#: the assertion that would catch it (it read 1.91 % high here until the couples
#: existed).
#:
#: ``concept_heavy`` is the fixture whose wing case names **only** a V-n case
#: reference (``case: 3``, no ``cl``/``v_eas_kt``), so its cards come from the
#: *derived* CL/V route -- the route review F-C6 found broken and closed on
#: 2026-08-10, and the one no other member of this matrix exercises. It also
#: carries a second, differently-shaped concentrated item (a 600 lb store per
#: side, offset in ``z`` as well as ``x``).
#:
#: Wing-only, both of them: neither fixture assembles a balanced case, so
#: neither has any business in the other legs.
WING_MATRIX = MATRIX + ("atr42_100.project.json", "concept_heavy.project.json")

#: Varying the unit system is what makes a *solve* catch a
#: ``moment.factor != force.factor x length.factor`` slip (plan 07's G2), which a
#: force-only check is structurally blind to.
SYSTEMS = (UnitSystem.IMPERIAL, UnitSystem.SI)

#: Load factor the mass leg accelerates at. Deliberately not 1.0: at unity a
#: deck that dropped ``Nz`` from the ``GRAV`` magnitude entirely would still pass
#: every assertion.
NZ = 2.5

_CACHE = {}


def _project(example: str):
    p = io.load_project(os.path.join(_ROOT, "examples", example))
    if p.envelope is None:
        p.envelope = build_envelope(p)
    if p.envelope.critical is None:
        p.envelope.critical = build_critical(p)
    return p


def _components(example: str):
    if example not in _CACHE:
        p = _project(example)
        net = build_net_loads(p)
        _CACHE[example] = (
            p,
            loads_ref_axis_results(p, net.wing_net),
            build_body_loads(p),
            build_tail_chordwise(p),
        )
    return _CACHE[example]


def _units(system):
    return deliverable_units(system, Channel.SOLVER)






def _solved(text):
    """``(solutions, grids)`` for a deck -- solve it and keep its geometry."""
    return solve_deck(text), parse_cards(text)[0]


def _bulk_of(text):
    """A deck's parsed ``BulkData`` -- sbeam's own reader, no solve.

    The mass model's grids are unconnected by design (note 56 ruling 9), so it is
    read rather than solved: ``compute_gpwg`` needs the parse and nothing else.
    sbeam's reader takes a path, so the deck goes through a temp file -- the same
    round trip through text a recipient makes, which is the point of the gate.
    """
    import tempfile

    from sbeam.parser.bdf_reader import parse_bdf

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "deck.bdf")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        out = parse_bdf(path)
    return out[-1] if isinstance(out, tuple) else out




#: The two matrix members whose projects state a side of body (a published
#: fuselage outline -> the BM-1 half-width fallback): the flagship concept
#: fixture, and the one wing that hangs concentrated masses -- so the SOB gate
#: sees both a clean wing and one whose offset couples must carry lever arms
#: across the cut. ``concept_heavy`` has no body data and ships no SOB node,
#: by design.
SOB_MATRIX = ("concept_regional_jet.project.json", "atr42_100.project.json")

#: **Every fixture the CLI will export an LRA deck for** (design note 55
#: D-55.4). The mission claim is that the exported deck *solves*; until this
#: existed the solve gate ran on :data:`SOB_MATRIX` -- the two fixtures that
#: passed -- so the claim was tested on the set selected for passing it.
#: ``ga6_normal`` failed on a rigid chain (D-55.1) and ``cessna_210`` on a
#: sliver element (D-55.2); ``baron_58`` carried the same sliver and was in no
#: gate to say so. ``concept_heavy`` is absent because it *refuses* (no body
#: data, the BM-1 posture), which is the honest other half of the claim.
LRA_SOLVE_MATRIX = (
    "ga6_normal.project.json",
    "baron_58.project.json",
    "atr42_100.project.json",
    "concept_regional_jet.project.json",
)
















# --------------------------------------------------------------------------- #
# The assembled full-span deck -- solved here until note 56 D-56.8
# --------------------------------------------------------------------------- #
# **What was here, and where it went.** ``_assembled_deck`` wrapped the shipped
# balanced deck in a star of invented ``CBAR``s -- the deck was a load set on a
# node cloud, which is all a load deliverable needs to be and is singular to a
# linear static solve -- and ``test_assembled_deck_reacts_to_zero`` solved it on
# both fixtures in both unit systems, asserting six zero reactions per case.
#
# D-56.8 stopped that deck being a shipped artifact. What ships is the **LRA
# beam model**, which writes its own chains, its own properties and its own
# support, so it is solved exactly as it ships; the wrapper is retired
# (``roundtrip``'s docstring is the account). The free-free claim did not
# retire with it: ``test_the_lra_model_solves_and_reacts_only_the_residual``
# makes it against the deck a reader is actually handed, over four fixtures
# rather than two, through real structure rather than a star of bars the
# harness made up. The load sets are the same ones -- the transfer preserves
# each case's resultant exactly, and that identity is itself gated
# (``test_lra_model.test_the_transferred_set_has_the_balanced_decks_resultant``).
#
# **Two narrowings, stated rather than absorbed.** (1) The LRA leg xfails on the
# SI decks of ``ga6_normal`` and ``concept_regional_jet`` -- sbeam's dense-path
# condition heuristic, see that test's docstring -- so those two fixtures lose
# their SI free-free solve, which the wrapped assembled deck did carry. SI is
# still solved on ``baron_58`` and ``atr42_100``. (2) "Every assembled case
# reaches the deck, and the lateral ones carry real side load" was asserted
# inside that solve; it is a property of the deck's text, so it is asserted on
# the deck's text below, where no solver is needed and every fixture is covered.


@pytest.mark.roundtrip
@pytest.mark.parametrize("example", MATRIX)
def test_every_assembled_case_reaches_the_beam_deck_carrying_its_lateral_load(
        sbeam, example):
    """The non-vacuity half of the retired assembled solve (plan 13 G3).

    A zero-target gate says nothing if the load never arrived. Two ways it
    could not: a case silently absent from the deck, or a lateral case present
    with no side load in it. Both are properties of the card text -- so they are
    checked there, on the shipped beam deck, rather than being carried along
    inside a solve that would report them as a passing zero.
    """
    project = io.load_project(os.path.join(_ROOT, "examples", example))
    cases = build_balanced_cases(project)
    _, text = _lra_deck(example)
    _, _, _, forces, _ = parse_cards(text)

    by_sid = dict(zip(case_sids(cases), cases))
    assert set(forces) == set(by_sid), (
        f"{example}: the deck loads {sorted(forces)} against {sorted(by_sid)}")
    lateral = [c for c in cases if is_lateral(c)]
    assert len(lateral) == 8, f"{example}: {len(lateral)} lateral subcases"

    u = _units(UnitSystem.IMPERIAL)
    for sid, case in by_sid.items():
        if not is_lateral(case):
            continue
        side = sum(abs(scale * n[1]) for _, scale, n in forces[sid])
        _, floor, _ = to_force(0.0, 0.1 * abs(vtail_load(case)), 0.0, u)
        assert side > abs(floor), (
            f"{example} SID {sid} {case.label}: only {side} of side load is in "
            "the deck")


@pytest.mark.roundtrip
@pytest.mark.parametrize("example", MATRIX)
@pytest.mark.parametrize("system", SYSTEMS)
def test_the_gear_node_carries_the_reports_reaction(sbeam, example, system):
    """**G-13's ground-specific solver assertion.**

    The free-free leg can pass *vacuously* for the ground family: "reactions ~ 0"
    proves the assembled set balances, but a transfer that dropped its lever-arm
    couple **consistently** would still sum to zero at the determinate support.
    So this closes the loop between G-12's two artifacts through a **third
    party** -- the deck is read back card by card, and the resultant found at
    each gear reference point must be the gear report's reference-point
    reaction.

    A transfer error, a frame error and a dropped couple all surface here, in one
    assertion, because all three change what is reconstructed about that node.
    Finding the node is by **GID band** rather than by coordinate, which is what
    the gear band of decision G-2 exists for.

    **Why this leg stayed on the assembled set at note 56 D-56.8**, when the
    free-free proof moved to the beam deck. It was tried on the beam deck first
    and it does not belong there: the deck's gear trunnion carries the gear
    reaction *plus whatever else D-56.9 summed onto the same grid* -- on
    ``concept_regional_jet``'s nose leg, 3334.8 lb against the report's 3597.8.
    That is the aggregation working as specified, not a defect, and Appendix G
    is where its size is published. Asserting the report's number at that grid
    would be asserting the lumping away. So the check stays where a gear
    reference point is still a node of its own: the assembled set, which is an
    internal producer now but is still the un-aggregated load set at its true
    positions, and is still the reference resultant the beam deck is gated
    against. No solver is in this leg and never was -- it reads card text -- so
    nothing is lost by it not being the shipped artifact.
    """
    from sloads.export.balanced_deck import BALANCED_GEAR_BASE, deck_nodes
    from sloads.gear_loads import gear_case_loads
    from sloads.modules.balance import is_ground

    project = io.load_project(os.path.join(_ROOT, "examples", example))
    cases = build_balanced_cases(project)
    ground = [c for c in cases if is_ground(c)]
    assert ground, f"{example}: no assembled ground case to check"

    nodes = deck_nodes(cases, project)
    gear_gids = {gid for gid in nodes.values()
                 if BALANCED_GEAR_BASE <= gid < BALANCED_GEAR_BASE + 100}
    assert gear_gids, f"{example}: the set allocated no gear reference point"

    text = balanced_deck(project, system=system)
    _, _, _, forces, _ = parse_cards(text)
    u = _units(system)
    report = {c.case: c for c in gear_case_loads(project)}
    sids = dict(zip(case_sids(cases), cases))

    checked = 0
    for sid, case in sids.items():
        if not is_ground(case):
            continue
        legs = {leg.leg: leg for leg in report[case.vn_case].legs}
        side_total = 0.0
        for load in case.loads:
            if not load.source.startswith("gear-"):
                continue
            gid = nodes[(load.side, round(load.x, 6), round(load.y, 6),
                         round(load.z, 6))]
            assert gid in gear_gids, (example, gid)
            leg_name = load.source.split("-", 1)[1]
            # What the cards alone put at this node.
            got = [0.0, 0.0, 0.0]
            for card_gid, scale, n in forces[sid]:
                if card_gid == gid:
                    for i in range(3):
                        got[i] += scale * n[i]
            want = to_force(*(v for v in legs[leg_name].airplane), u)
            # **Vertical and drag are per leg and identical on both wheels**, so
            # they are the direct comparison G-13 asks for -- and they are also
            # where a transfer error, a frame error or a dropped couple would
            # show, since all three change what is reconstructed here.
            for i in (0, 2):
                assert math.isclose(got[i], want[i], rel_tol=1e-6,
                                    abs_tol=1e-6 * max(1.0, abs(want[i]))), (
                    f"{example} {system.value} SID {sid} GID {gid} axis {i}: "
                    f"the cards give {got[i]} against the gear report's "
                    f"{want[i]}")
            if leg_name == "main":
                side_total += got[1]
            checked += 1
        # **Side load is the one component the report cannot state per wheel**,
        # and that is a property of 23.485(c) rather than a gap: the side
        # condition puts 0.5 W inboard on one wheel and 0.33 W outboard on the
        # other, acting the same way globally, while ``GearReactionCase`` carries
        # a single ``SMP`` per case (decision G-8's implementation note). What is
        # well defined is their **sum**, which is what ``NS`` states -- so that is
        # what is checked, and it closes the same loop.
        ns_w = case.delta_ny * case.weight_lb
        _, want_side, _ = to_force(0.0, ns_w, 0.0, u)
        assert math.isclose(side_total, want_side, rel_tol=1e-6,
                            abs_tol=1e-6 * max(1.0, abs(want_side))), (
            f"{example} {system.value} SID {sid}: main-wheel side load "
            f"{side_total} against NS*W {want_side}")
    assert checked, f"{example}: no gear card reached the set"


@pytest.mark.roundtrip
@pytest.mark.parametrize("system", SYSTEMS)
def test_a_flipped_fin_load_breaks_the_free_free_solve(sbeam, system):
    """**G3's teeth**: reverse the fin load alone and the solver reacts it.

    A zero-target gate is only worth what its sensitivity is, and "the reactions
    came out zero" proves nothing unless a wrong deck would have made them
    non-zero. The mutation is the exact defect plan 13 §3.3 found in the fin's
    waterline and the one L-6's frame map could reintroduce: the fin's side load
    with its sign reversed, everything else -- including the closure field that
    balanced the *original* load -- left untouched. The airplane is then carrying
    twice the fin load with nothing to react it, and the support must say so.

    Run against the **beam deck** since note 56 D-56.8, and on ``atr42_100``:
    the mutation is a property of the assembly, not of a fixture, and this is
    the fixture whose beam deck solves in both unit systems (``ga6_normal``, the
    old subject, xfails in SI on sbeam's condition heuristic -- see the free-free
    leg's docstring). Mutating the case *before* the transfer is deliberate: the
    reversed load then travels the whole delivery path, so the gate calibrates
    the transfer as well as the solve.
    """
    example = "atr42_100.project.json"
    project = io.load_project(os.path.join(_ROOT, "examples", example))
    cases = build_balanced_cases(project)
    case = next(c for c in cases if is_lateral(c) and c.hand == "R")
    flipped = replace(case, loads=[
        replace(ld, fy=-ld.fy, mz=-ld.mz) if ld.source == "vtail-air" else ld
        for ld in case.loads])

    from sloads.export.lra_model import lra_model_bdf

    text = lra_model_bdf(project, system=system, cases=[flipped])
    sols, grids = _solved(text)
    _, _, spc1, forces, moments = parse_cards(text)
    (_, _, support_gids), = [c for c in spc1 if c[1] == "123456"]
    (sid, sol), = sols.items()

    ref = grids[support_gids[0]]
    applied = resultant(forces, moments, grids, sid, ref)
    got = total_reaction(sol.reactions, grids, ref=ref)
    assert not closes(got.force[1], 0.0, scale=applied.force_scale), (
        f"a reversed fin load left the support reacting {got.force[1]} in y -- "
        "this gate cannot see a lateral sign error")
    # ...and it is the fin load **twice over**: the deck now applies the reversed
    # load *and* the relief that was solved to cancel the original one, so it
    # carries -2*L_v and the support reacts +2*L_v. Asserting the number and not
    # merely "non-zero" is what makes this a calibration of the gate rather than
    # a smoke test -- it says how much of a sign error it would take to hide.
    _, want, _ = to_force(0.0, 2.0 * vtail_load(case), 0.0, _units(system))
    assert closes(got.force[1], want, scale=applied.force_scale), got.force[1]

    # The roll and yaw reactions move with it -- the two moment DOF the lateral
    # family is the first to exercise, and the two the paper closure and the
    # card sum share an assumption about (the lever arms). Here they are the
    # solver's own, computed from the GRID cards.
    for axis, name in ((0, "roll"), (2, "yaw")):
        assert not closes(got.moment[axis], 0.0, scale=applied.moment_scale), (
            f"a reversed fin load left the support's {name} reaction at "
            f"{got.moment[axis]}")


# --------------------------------------------------------------------------- #
# The mass-check deck -- the fourth family (plan 12 C6, review F-G2 / C1)
# --------------------------------------------------------------------------- #
def _loadings(project):
    return [ld for ld in derive_case_loadings(project) if ld.derivable]


def _nodal_inertia(sol, grids, support_gid):
    """``{gid: Fz}`` -- the inertia load sbeam put on each node, recovered.

    The mass-check deck is a clamped chain, so the load at a node is the jump in
    element shear across it: element ``i`` joins node ``i-1`` to node ``i``, and
    what enters at node ``i`` is ``shear(i) - shear(i+1)``. At the clamped node
    the reaction also passes through, and is subtracted.

    Element shear rather than the reaction *is* the point: the reaction is one
    number and would be satisfied by any distribution summing to it, while this
    is the card-for-card comparison plan 12 C6 asks for -- and it is recovered
    from sbeam's own assembly of the ``CONM2`` cards, never from sloads' idea of
    where the mass is.
    """
    order = sorted(grids)
    shear = {eid: bar.shear1 for eid, bar in sol.bar_forces.items()}
    out = {}
    for i, gid in enumerate(order):
        out[gid] = shear.get(i, 0.0) - shear.get(i + 1, 0.0)
        if gid == support_gid:
            out[gid] -= sol.reactions[gid][2]
    return out


#: Fixtures with at least one derivable payload case *and* a place in the
#: matrix. ``atr42_100`` joins for the same reason it joins the wing leg: it is
#: the fixture whose wing carries concentrated mass, so its CONM2 set is the one
#: where the wing items hung on the fuselage beam actually weigh something.
MASS_MATRIX = MATRIX + ("atr42_100.project.json",)


# --------------------------------------------------------------------------- #
# The mass model -- checked by GPWG, not by a solve (note 56 D-56.6, ruling 16)
# --------------------------------------------------------------------------- #
# **Five legs were deleted here and this is the account of what they did.**
# D-56.6 puts every CONM2 on a GRID at its own item's CG, unconnected by design
# (ruling 9), so a stiffness solve over the mass deck is singular and the legs
# that reacted it against an SPC1 clamp through CBARs have no load path:
#
#   * ``test_mass_deck_recovers_the_inertia_cards_case_for_case`` (M-a total,
#     M-b card-for-card, M-c the cases differ). M-b compared against
#     ``inertia_only_cards``, which D-56.7 retires, so it goes by design; M-a and
#     M-c are the real loss -- sbeam's own mass-matrix assembly and the GRAV
#     acceleration path stop being exercised.
#   * ``test_the_shipped_mass_deck_hits_the_sbeam_massset_gap``, the pin that
#     SOL 101 ignores a subcase's MASSSET. It pinned a *solver* limitation on a
#     deck no longer solved. GPWG does **not** have the gap (see below), so the
#     workaround it justified is gone rather than merely unused.
#   * the two ``flatten_mass_case`` legs and the C1 mutation. Flattening existed
#     only to work around that MASSSET gap for these solves; with no solve and no
#     gap it has no caller, so ``roundtrip.flatten_mass_case`` retires with them
#     and §8's collapse has that much less to weigh.
#
# **The C1 defect class did not go with the mutation leg**, which is why the leg
# could go. The 2026-08-10 defect was an SI GRAV magnitude 25.4x low, and it is
# caught today by card text against an independently written constant, in both
# systems, at rel=1e-12: ``test_mass_cards.test_the_grav_card_carries_g_in_deck_units``
# and ``::test_deck_gravity_is_g_in_the_decks_own_length_unit``. A solve was
# never the only thing that could see it -- it was only the thing that did.


@pytest.mark.roundtrip
@pytest.mark.parametrize("example", MASS_MATRIX)
@pytest.mark.parametrize("system", SYSTEMS)
def test_gpwg_recovers_each_payload_case_from_the_shipped_mass_deck(
        sbeam, example, system):
    """**Gate 6**: sbeam's own mass recovery agrees with sloads, case by case.

    The check the CONM2 export exists for, in the form D-56.6 leaves it. sbeam
    parses the deck independently and computes total mass and CG from the CONM2
    cards and the grid positions -- sloads never tells it either number.

    Three things make this stronger than the solve it replaces, and one weaker;
    all four are stated because a replaced gate should be argued, not asserted.

    * It reads **the deck as shipped**. GPWG honours ``MASSSET`` where ``SOL 101``
      does not, so there is no flattening transform between the artifact and the
      claim -- the old legs had to fold each case into a baseline deck first, and
      a gate that tests a transformed artifact is a gate with a caveat.
    * It needs no connectivity, so it works on the unconnected CG grids that are
      now the model, without sloads shipping a tie it does not believe in.
    * It is per case *and* per unit system, as before.
    * **Weaker:** the ``GRAV`` acceleration path and sbeam's mass-matrix assembly
      are no longer exercised. See the block above for why that is affordable.

    **The tolerance is the deck's own print precision, and is measured.**
    ``deck_format.fmt`` writes seven significant figures and GPWG reads the
    printed cards, so agreement is bounded at ~1e-7 by the artifact itself --
    worst observed over five fixtures x two systems x every case is 1.3e-7, on
    ``concept_heavy`` (``46.62142525735088`` prints as ``4.662143E+01``). A
    tighter tolerance would assert that a seven-figure field carries more than
    seven figures.
    """
    from sbeam.gpwg import compute_gpwg

    project, _, _, _ = _components(example)
    deck = mc.mass_check_deck(project, system=system, nz=NZ)
    bulk = _bulk_of(deck)
    loadings = _loadings(project)
    seen = []

    for i, loading in enumerate(loadings):
        where = f"{example} {system.value} mass {loading.name}"
        got = compute_gpwg(bulk, mc.MASSSET_SID_BASE + i)
        want = mc.mass_properties(project, loading, system=system)
        assert got.total_mass == pytest.approx(want["mass"], rel=1e-6), \
            f"{where}: sbeam recovered {got.total_mass} against {want['mass']}"
        for axis in ("cg_x", "cg_z"):
            assert getattr(got, axis) == pytest.approx(want[axis], rel=1e-6), \
                f"{where} {axis}: {getattr(got, axis)} vs {want[axis]}"
        seen.append((round(got.total_mass, 6), round(got.cg_x, 6)))

    assert seen, f"{example}: no derivable payload case reached the recovery"
    if len(seen) > 1:
        # On the *distribution*, not the total: the regional jet's two derivable
        # cases weigh the same 33,000 lb and differ only in where the payload
        # sits, so a total-only check would pass on it vacuously. This is M-c,
        # kept in the form the new authority allows.
        assert len(set(seen)) > 1, (
            f"{example}: every case recovered the same mass and CG -- the "
            "per-case mass model is not reaching sbeam")


# --------------------------------------------------------------------------- #
# The negative tests -- a gate nobody has seen fail is a gate nobody knows works
# --------------------------------------------------------------------------- #
def _mutate(text, predicate, transform):
    """Rewrite the first deck line satisfying ``predicate``; assert one matched."""
    out, hit = [], False
    for line in text.splitlines():
        if not hit and predicate(line):
            line, hit = transform(line), True
        out.append(line)
    assert hit, "the mutation matched no line -- the deck format changed"
    return "\n".join(out) + "\n"




@pytest.mark.roundtrip
def test_swapped_subcase_load_ids_break_the_per_case_assertions(sbeam):
    """Mutation 2: swap two ``SUBCASE``s' ``LOAD`` ids -> the per-case checks fail.

    Symmetry is the risk this rules out: if every case were checked against a
    deck-wide total, a routing error would pass. Case identity (M4-2 decisions
    8/9) is only real if a mis-selected load set is detectable.

    **This became a deck-text check at note 56 D-56.2, and that is a real
    narrowing worth stating.** It used to mutate the wing stick deck and watch
    a clamped reaction move, because that deck reacted each case's own non-zero
    resultant. No free-free deck can host the same mutation: every balanced
    case has a zero resultant *by construction*, so swapping two subcases' load
    sets leaves all six reactions at zero and no reaction-based gate can see it.
    Rather than write a solve that proves nothing, the property is asserted
    where it is observable -- a subcase selects its own case's ``LOAD`` set, in
    the deck's own text. Read off the **shipped** deck since D-56.8.
    """
    _, text = _lra_deck("atr42_100.project.json")
    pairs = re.findall(r"SUBCASE (\d+)\n(?:.*\n)*?  LOAD = (\d+)", text)
    assert len(pairs) >= 2, "the deck must carry several subcases"
    for subcase, load in pairs:
        assert subcase == load, (
            f"SUBCASE {subcase} selects LOAD {load}: a subcase must select its "
            "own case's load set, or the deck routes a condition's loads to "
            "another condition's name (M4-2 decisions 8/9)")


@pytest.mark.roundtrip
def test_a_displaced_grid_breaks_the_free_free_reaction(sbeam):
    """Mutation 3: displace one loaded ``GRID``'s ``x`` by 1% -> the gate fails.

    This is the assertion a card-sum check **cannot** make. The applied ``FORCE``
    cards are untouched, so every force sum in the deck still closes exactly;
    what moves is a lever arm the solver reads from the file, and only a solve
    that assembles the model from those coordinates can see it. If this test
    ever stops failing, the free-free gate has stopped being a geometry check.

    Run against the **beam deck** since note 56 D-56.8 unshipped the assembled
    one. That is where it belongs, and it is stronger there: the deck a reader
    is handed is the one whose header claims its support does nothing, and its
    ``GRID`` cards are the coordinates a sizing run would build its own model
    from. ``atr42_100`` is the subject because its deck solves in both unit
    systems.
    """
    example = "atr42_100.project.json"
    _, text = _lra_deck(example)
    # Displace a loaded node well away from the support: moving a support node
    # would change the support geometry rather than a load's lever arm.
    _, _, spc1, forces0, _ = parse_cards(text)
    (_, _, support_gids), = [c for c in spc1 if c[1] == "123456"]
    sid0 = sorted(forces0)[0]
    loaded = sorted({g for g, _, _ in forces0[sid0]} - set(support_gids))
    target = loaded[len(loaded) // 2]

    def shift(line):
        f = line.split(",")
        f[3] = f" {float(f[3]) * 1.01:.6E}"
        return ",".join(f)

    broken = _mutate(text, lambda ln: ln.startswith(f"GRID, {target},"), shift)
    sols, broken_grids = _solved(broken)
    _, _, _, forces, moments = parse_cards(broken)
    sol = sols[sid0]

    ref = broken_grids[support_gids[0]]
    applied = resultant(forces, moments, broken_grids, sid0, ref)
    assert closes(applied.fz, 0.0, scale=applied.force_scale), \
        "the force sum must still close -- only geometry was mutated"
    got = total_reaction(sol.reactions, broken_grids, ref=ref)
    assert not closes(got.moment[1], 0.0, scale=applied.moment_scale)


# --------------------------------------------------------------------------- #
# The wrapper itself -- retired at note 56 D-56.8
# --------------------------------------------------------------------------- #
# Three legs stood here, all solver-free, all about ``wrap_as_stick_model``: it
# refuses a deck with no ``GRID`` cards, it refuses a node left out of every
# group, and wrapping the assembled deck keeps that deck's own support and adds
# nothing but elements. They were good tests of a good harness, and they go with
# it: there is no elementless deck left to wrap, so the refusals guard nothing
# and the "adds only elements" property has no subject. Its own third guard --
# it refuses a deck that already carries ``CBAR``s, because a wrapped copy is
# not the shipped artifact -- is the one that says why the wrapper had to end
# when the last elementless deck did.
#
# What replaced them is not another unit test but a change of subject: every
# solve in this file now runs the deck as it ships.


if __name__ == "__main__":
    sys.exit(pytest.main([os.path.abspath(__file__), "-q"]))


# --------------------------------------------------------------------------- #
# The LRA beam model (step 12) -- solves free-free; named-node internal loads
# --------------------------------------------------------------------------- #
def _lra_deck(example, system=UnitSystem.IMPERIAL):
    from sloads.export.lra_model import lra_model_bdf

    project = io.load_project(os.path.join(_ROOT, "examples", example))
    return project, lra_model_bdf(project, system=system)


def _rigid_edges(text):
    """``(gn, gm)`` pairs of every RBE2 card -- the graph edges the CBAR parse
    does not carry, needed to partition the model at a cut element."""
    edges = []
    for raw in text.splitlines():
        f = [c.strip() for c in raw.strip().split(",")]
        if f and f[0].upper() == "RBE2":
            gn = int(f[2])
            edges += [(gn, int(g)) for g in f[4:] if g]
    return edges


def _side_gids(cbars, rigid, cut_eid, start):
    """The connected component containing ``start`` once ``cut_eid`` is gone.

    The model is a tree (implementation note 25 LM-3/R-12), so cutting one
    element splits it in two; the returned set is "everything on ``start``'s
    side of the cut" -- the free body whose applied resultant the cut element's
    end force must equal.
    """
    adj = {}
    for eid, ga, gb in cbars:
        if eid == cut_eid:
            continue
        adj.setdefault(ga, set()).add(gb)
        adj.setdefault(gb, set()).add(ga)
    for a, b in rigid:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen, stack = {start}, [start]
    while stack:
        for nxt in adj.get(stack.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


@pytest.mark.roundtrip
@pytest.mark.parametrize("example", LRA_SOLVE_MATRIX)
@pytest.mark.parametrize("system", SYSTEMS)
def test_the_lra_model_solves_and_reacts_only_the_residual(sbeam, example, system):
    """The step-12 free-free proof, through real structure this time.

    The assembled balanced deck proved the load sets close on a node cloud;
    the LRA model routes the same sets through CBAR chains and rigid ties, so
    a wrong tie, a singular hinge set or an orphan node fails HERE. The
    support node's recovered reaction must be exactly minus the applied
    resultant (the solver's own assembly of the transferred set), and that
    resultant is the case residual: ~0 against the applied scale.

    Known sbeam limitation, pinned strict: some SI (mm) decks are refused by
    sbeam's dense-path 1e15 condition heuristic, which reads the raw 1-norm
    estimate of a matrix whose translation/rotation spread is a units artifact
    -- Jacobi-equilibrated the same matrix conditions at ~1.3e9, and the
    Imperial twin of the identical model solves exactly. The deck is valid bulk
    data; the day sbeam equilibrates before its check, the strict xfails below
    go green and get removed.

    Two fixtures sit on that heuristic, for opposite reasons: the regional jet
    because it is the largest airframe, and ``ga6_normal`` because it is the
    smallest *and* has only two untied fuselage nodes (nose and tail), so
    D-55.6 leaves the clamp far from the wing and the flexible paths long. Both
    solve exactly in Imperial, which is what says the deck is sound and the
    heuristic is the limit. ``ga6_normal`` is the one fixture whose LRA deck a
    future support node beside the carry-through would move off this edge --
    filed as note 55 §8's deferred item, not guessed at here.
    """
    if system is UnitSystem.SI and example.startswith(
            ("concept_regional_jet", "ga6_normal")):
        pytest.xfail("sbeam dense-path condition heuristic refuses this mm "
                     "frame (see docstring)")
    _, text = _lra_deck(example, system)
    sols, grids = _solved(text)
    _, _, _, forces, moments = parse_cards(text)
    assert sols
    for sid in sols:
        applied = resultant(forces, moments, grids, sid, (0.0, 0.0, 0.0))
        rx = total_reaction(sols[sid].reactions, grids)
        where = f"{example} {system.value} SID {sid}"
        for i, comp in enumerate(("fx", "fy", "fz")):
            assert closes(rx.force[i], -getattr(applied, comp),
                          scale=applied.force_scale), f"{where} {comp}"
            assert closes(rx.force[i], 0.0,
                          scale=applied.force_scale), f"{where} {comp} != 0"
        for i, comp in enumerate(("mx", "my", "mz")):
            assert closes(rx.moment[i], -getattr(applied, comp),
                          scale=applied.moment_scale), f"{where} {comp}"
            assert closes(rx.moment[i], 0.0,
                          scale=applied.moment_scale), f"{where} {comp} != 0"


@pytest.mark.roundtrip
@pytest.mark.parametrize("example", SOB_MATRIX)
def test_the_lra_named_node_internal_loads_are_the_cut_side_sums(sbeam, example):
    """Gates 3 and 4 of implementation note 25 §5, on the model itself.

    The model is a tree, so cutting one element defines a free body, and the
    solver's CBAR end force in that element must equal the applied resultant
    of everything on the far side of the cut -- computed here from the deck's
    own cards by graph partition, with the element frame built from geometry
    (the step-13 sign map). Asserted at the two joints the deliverable exists
    to state: the wing side of body (first element outboard of the tagged SOB
    node) and the front-spar post (the forward-fuselage cantilever's last
    element, whose far side is everything BUT the forward body -- BM-2's sum,
    seen from the other end).
    """
    import numpy as np

    from sloads.export.lra_import import read_lra_model

    _, text = _lra_deck(example)
    sols, grids = _solved(text)
    _, cbars, _, forces, moments = parse_cards(text)
    rigid = _rigid_edges(text)
    tags = read_lra_model(text).tags

    cuts = []
    sob_r = tags["lra-sob R"]
    cuts.append(("SOB", next((eid, ga, gb) for eid, ga, gb in cbars
                             if ga == sob_r)))
    post_f = tags["lra-post F"]
    cuts.append(("post-F", next((eid, ga, gb) for eid, ga, gb in cbars
                                if gb == post_f)))

    for name, (eid, ga, gb) in cuts:
        a = np.array(grids[ga])
        b = np.array(grids[gb])
        e_x = (b - a) / np.linalg.norm(b - a)
        v = np.array([0.0, 0.0, 1.0])
        v_perp = v - v.dot(e_x) * e_x
        if np.linalg.norm(v_perp) < 1e-6:      # vertical element fallback
            v_perp = np.array([0.0, 1.0, 0.0])
            v_perp -= v_perp.dot(e_x) * e_x
        e_y = v_perp / np.linalg.norm(v_perp)
        rot = np.vstack([e_x, e_y, np.cross(e_x, e_y)])
        far = _side_gids(cbars, rigid, eid, gb)
        assert ga not in far, f"{example} {name}: the cut did not split the tree"

        for sid in sols:
            where = f"{example} {name} SID {sid}"
            f_g = np.zeros(3)
            m_g = np.zeros(3)
            f_scale = 0.0
            for gid, scale, n in forces.get(sid, ()):
                if gid not in far:
                    continue
                f = scale * np.array(n)
                f_g += f
                m_g += np.cross(np.array(grids[gid]) - a, f)
                f_scale += float(np.abs(f).max())
            for gid, scale, n in moments.get(sid, ()):
                if gid in far:
                    m_g += scale * np.array(n)
            m_scale = float(np.abs(m_g).max())
            f_e = rot @ f_g
            m_e = rot @ m_g
            bar = sols[sid].bar_forces[eid]
            assert closes(bar.axial, f_e[0], scale=f_scale), f"{where} axial"
            assert closes(bar.shear1, f_e[1], scale=f_scale), f"{where} shear1"
            assert closes(bar.shear2, f_e[2], scale=f_scale), f"{where} shear2"
            assert closes(bar.torque, m_e[0], scale=m_scale), f"{where} torque"
            assert closes(bar.bm1_a, -m_e[1], scale=m_scale), f"{where} bm1_a"
            assert closes(bar.bm2_a, -m_e[2], scale=m_scale), f"{where} bm2_a"
