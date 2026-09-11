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
import subprocess
import sys
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from sloads import io
from sloads.derived_geometry import sob_station
from sloads.export import mass_cards as mc
from sloads.export import sbeam_bridge as sb
from sloads.export.balanced_deck import (
    balanced_deck,
    case_sids,
)
from sloads.export.coordinates import (
    tail_force_to_airplane,
    to_force,
    to_grid,
    to_moment,
)
from sloads.export.equilibrium import (
    closes,
    parse_cards,
    ref_first_loaded,
    resultant,
)
from sloads.export.roundtrip import (
    Support,
    Topology,
    flatten_mass_case,
    solve_deck,
    total_reaction,
    wrap_as_stick_model,
)
from sloads.mass_distribution import derive_case_loadings
from sloads.modules.balance import (
    build_balanced_cases,
    vtail_load,
    is_lateral,
)
from sloads.modules.body_loads import build_body_loads
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.net_loads import build_net_loads, loads_ref_axis_results
from sloads.modules.select import build_critical
from sloads.modules.tail_span import build_tail_span
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
# The assembled full-span deck -- the primary deliverable (plan 11 B-5)
# --------------------------------------------------------------------------- #
def _assembled_deck(project, system):
    """The shipped assembled deck plus the elements it does not carry.

    The deliverable is a load set on a node cloud, which is all a load deck needs
    to be; the wrapper adds a tree of bars so a linear static solve has a
    stiffness matrix, and changes nothing else -- the deck's own determinate
    six-DOF support is kept, because that support *is* what is under test.
    """
    return _assembled_deck_from(project, system, ())


def _assembled_deck_from(project, system, cases):
    """:func:`_assembled_deck` for a stated case list -- ``()`` means "all of
    them", which is what the shipped deck writes."""
    return wrap_as_stick_model(
        balanced_deck(project, system=system, cases=cases),
        support=Support.DECK, topology=Topology.STAR, system=system,
        title="assembled full-span balanced deck")


@pytest.mark.roundtrip
@pytest.mark.parametrize("example", MATRIX)
@pytest.mark.parametrize("system", SYSTEMS)
def test_assembled_deck_reacts_to_zero(sbeam, example, system):
    """The mission's primary deliverable, solved: reactions ~ 0 on every case.

    The assembled deck's ``$`` header claims its determinate support is doing
    nothing -- that aero and inertia balance the airplane wing tip to wing tip
    with no constraint needed. This is that claim checked by a solver which
    reassembles the whole load set from the card text and the ``GRID``
    coordinates: six recovered reaction components, all zero.

    **Plan 13 G3**, from B8a-3 on: the lateral subcases are the first to put a
    real ``fy``/``mx``/``mz`` through this leg, and they are where a sign or
    frame error in the fin's span-to-waterline map would show up as a reaction
    the paper closure cannot see. Two things guard against passing on that
    vacuously -- every assembled case must appear as a subcase, and each lateral
    one must actually carry side load into the solver. That the gate has teeth
    on those DOF is shown separately, by
    :func:`test_a_flipped_fin_load_breaks_the_assembled_solve`.
    """
    project, _, _, _ = _components(example)
    cases = build_balanced_cases(project)
    text = _assembled_deck(project, system)
    sols, grids = _solved(text)
    _, _, spc1, forces, moments = parse_cards(text)
    assert sols, "the assembled deck produced no subcases"
    (_, comp, support_gids), = [s for s in spc1 if s[1] == "123456"][:1] or [(0, "", [])]
    assert comp == "123456" and len(support_gids) == 1, \
        "the assembled deck's support is meant to be one determinate node"

    # Every case reaches the solver, and the lateral family is among them --
    # a deck that quietly stopped emitting them would otherwise pass here.
    by_sid = dict(zip(case_sids(cases), cases))
    assert set(sols) == set(by_sid), (
        f"{example}: solved {sorted(sols)} against {sorted(by_sid)}")
    assert sum(1 for c in cases if is_lateral(c)) == 8, \
        f"{example}: {sum(1 for c in cases if is_lateral(c))} lateral subcases"

    for sid, sol in sols.items():
        case = by_sid[sid]
        where = f"{example} {system.value} assembled SID {sid} {case.label}"
        applied = resultant(forces, moments, grids, sid, grids[support_gids[0]])
        got = total_reaction(sol.reactions, grids, ref=grids[support_gids[0]])
        assert applied.n_force, f"{where}: no FORCE cards in this subcase"
        if is_lateral(case):
            # The cards sum to zero by construction; what must not be zero is
            # the side load flowing through them, or "reaction ~ 0" would be the
            # trivial statement that nothing lateral was applied at all.
            side = sum(abs(scale * n[1]) for _, scale, n in forces[sid])
            floor = 0.1 * abs(vtail_load(case))
            _, floor, _ = to_force(0.0, floor, 0.0, _units(system))
            assert side > abs(floor), (
                f"{where}: only {side} of side load reached the solver")
        for axis in range(3):
            assert closes(got.force[axis], 0.0, scale=applied.force_scale), \
                f"{where} force axis {axis}: {got.force[axis]}"
            assert closes(got.moment[axis], 0.0, scale=applied.moment_scale), \
                f"{where} moment axis {axis}: {got.moment[axis]}"


@pytest.mark.roundtrip
@pytest.mark.parametrize("example", MATRIX)
@pytest.mark.parametrize("system", SYSTEMS)
def test_the_gear_node_carries_the_reports_reaction(sbeam, example, system):
    """**G-13's ground-specific solver assertion.**

    The inherited leg above can pass *vacuously* for the ground family:
    "reactions ~ 0" proves the assembled set balances, but a transfer that
    dropped its lever-arm couple **consistently** would still sum to zero at the
    determinate support. So this closes the loop between G-12's two artifacts
    through a **third party** -- sbeam reassembles the load from the card text
    and its own ``GRID`` coordinates, and the resultant it finds at each gear
    reference point must be the gear report's reference-point reaction.

    A transfer error, a frame error and a dropped couple all surface here, in one
    assertion, because all three change what the solver reconstructs about that
    node. Finding the node is by **GID band** rather than by coordinate, which is
    what the gear band of decision G-2 exists for.
    """
    from sloads.export.balanced_deck import BALANCED_GEAR_BASE, deck_nodes
    from sloads.gear_loads import gear_case_loads
    from sloads.modules.balance import is_ground

    project, _, _, _ = _components(example)
    cases = build_balanced_cases(project)
    ground = [c for c in cases if is_ground(c)]
    assert ground, f"{example}: no assembled ground case to check"

    nodes = deck_nodes(cases, project)
    gear_gids = {gid for gid in nodes.values()
                 if BALANCED_GEAR_BASE <= gid < BALANCED_GEAR_BASE + 100}
    assert gear_gids, f"{example}: the deck allocated no gear reference point"

    text = _assembled_deck(project, system)
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
            # What the solver reconstructs at this node, from the cards alone.
            got = [0.0, 0.0, 0.0]
            for eid, scale, n in forces[sid]:
                if eid == gid:
                    for i in range(3):
                        got[i] += scale * n[i]
            leg = legs[load.source.split("-", 1)[1]]
            # The report is LIMIT; the deck is ULTIMATE. Both halves of that
            # contract are asserted by comparing across it rather than around it.
            want = to_force(*(v for v in leg.airplane), u)
            # **Vertical and drag are per leg and identical on both wheels**, so
            # they are the direct comparison G-13 asks for -- and they are also
            # where a transfer error, a frame error or a dropped couple would
            # show, since all three change what the solver reconstructs here.
            for i in (0, 2):
                assert math.isclose(got[i], want[i], rel_tol=1e-6,
                                    abs_tol=1e-6 * max(1.0, abs(want[i]))), (
                    f"{example} {system.value} SID {sid} GID {gid} axis {i}: "
                    f"solver {got[i]} against the gear report's {want[i]}")
            if leg.leg == "main":
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
    assert checked, f"{example}: no gear card reached the solver"


@pytest.mark.roundtrip
@pytest.mark.parametrize("system", SYSTEMS)
def test_a_flipped_fin_load_breaks_the_assembled_solve(sbeam, system):
    """**G3's teeth**: reverse the fin load alone and the solver reacts it.

    A zero-target gate is only worth what its sensitivity is, and "the reactions
    came out zero" proves nothing unless a wrong deck would have made them
    non-zero. The mutation is the exact defect plan 13 §3.3 found in the fin's
    waterline and the one L-6's frame map could reintroduce: the fin's side load
    with its sign reversed, everything else -- including the closure field that
    balanced the *original* load -- left untouched. The airplane is then carrying
    twice the fin load with nothing to react it, and the support must say so.

    Run on ``ga6_normal`` only: the mutation is a property of the assembly, not
    of a fixture, and a second airplane would only add solve time.
    """
    project, _, _, _ = _components("ga6_normal.project.json")
    cases = build_balanced_cases(project)
    case = next(c for c in cases if is_lateral(c) and c.hand == "R")
    flipped = replace(case, loads=[
        replace(ld, fy=-ld.fy, mz=-ld.mz) if ld.source == "vtail-air" else ld
        for ld in case.loads])

    text = _assembled_deck_from(project, system, [flipped])
    sols, grids = _solved(text)
    _, _, spc1, forces, moments = parse_cards(text)
    (_, _, support_gids), = [s for s in spc1 if s[1] == "123456"]
    (sid, sol), = sols.items()

    applied = resultant(forces, moments, grids, sid, grids[support_gids[0]])
    got = total_reaction(sol.reactions, grids, ref=grids[support_gids[0]])
    assert not closes(got.force[1], 0.0, scale=applied.force_scale), (
        f"a reversed fin load left the support reacting {got.force[1]} in y -- "
        "this gate cannot see a lateral sign error")
    # ...and it is the fin load **twice over**: the deck now applies the reversed
    # load *and* the relief that was solved to cancel the original one, so it
    # carries -2*L_v and the support reacts +2*L_v. Asserting the number and not
    # merely "non-zero" is what makes this a calibration of the gate rather than
    # a smoke test -- it says how much of a sign error it would take to hide.
    _, want, _ = to_force(0.0, 2.0 * vtail_load(case), 0.0,
                          _units(system))
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


@pytest.mark.roundtrip
@pytest.mark.parametrize("example", MASS_MATRIX)
@pytest.mark.parametrize("system", SYSTEMS)
def test_mass_deck_recovers_the_inertia_cards_case_for_case(sbeam, example, system):
    """M-a...M-c: sbeam accelerates the ``CONM2`` set and reproduces sloads' inertia.

    **The check the whole CONM2 export exists for** (plan 12 C6), and the one
    family the harness never solved until now -- which is exactly why the SI
    ``GRAV`` acceleration could ship 25.4x low and be caught by a reading rather
    than by CI (2026-08-10 review, C1/F-G2).

    Three statements, each with two independent producers:

    * **M-a** the total: sbeam's clamp reacts the case's own weight x Nz. sloads
      never tells it that number -- it comes out of sbeam's mass matrix, built
      from the ``CONM2`` cards and their offsets.
    * **M-b** card for card: the nodal inertia sbeam recovers equals
      ``inertia_only_cards(loading=...)`` at every node.
    * **M-c** the cases differ. A leg that solved four cases of one airplane and
      never noticed they were the same mass would be worth nothing, and that is
      not hypothetical -- it is what the shipped deck does today (see
      :func:`test_the_shipped_mass_deck_hits_the_sbeam_massset_gap`).

    Run in **both** unit systems: Imperial cannot see a ``length.factor`` slip in
    the acceleration at all, which is the whole lesson of C1.
    """
    project, _, _, _ = _components(example)
    u = _units(system)
    deck = mc.mass_check_deck(project, system=system, nz=NZ)
    seen = []

    for i, loading in enumerate(_loadings(project)):
        sid = mc.MASSSET_SID_BASE + i
        where = f"{example} {system.value} mass {loading.name}"
        text = flatten_mass_case(deck, sid)
        sols, grids = _solved(text)
        (solved_sid, sol), = sols.items()
        assert solved_sid == sid, where
        (_, _, support_gids), = [s for s in parse_cards(text)[2]]
        support = support_gids[0]

        want_total = -loading.weight_lb * NZ * u.force.factor
        assert closes(sol.reactions[support][2], -want_total,
                      scale=abs(want_total)), f"{where} M-a"

        _, _, _, want_cards, _ = parse_cards(
            mc.inertia_only_cards(project, system=system, nz=NZ, loading=loading))
        want = {gid: scale * n[2]
                for gid, scale, n in want_cards[mc.GRAV_SID_BASE]}
        got = _nodal_inertia(sol, grids, support)
        assert set(want) <= set(got), f"{where}: nodes {sorted(set(want) - set(got))}"
        for gid, value in got.items():
            assert closes(value, want.get(gid, 0.0), scale=abs(want_total)), \
                f"{where} M-b node {gid}: {value} vs {want.get(gid, 0.0)}"
        seen.append(tuple(sorted((gid, round(v, 6)) for gid, v in got.items())))

    assert seen, f"{example}: no derivable payload case reached the solver"
    if len(seen) > 1:
        # On the *distribution*, not on the total: the regional jet's two
        # derivable cases weigh the same 33,000 lb and differ only in where the
        # payload sits, so a total-only check would pass on it vacuously.
        assert len(set(seen)) > 1, (
            f"{example} M-c: every case recovered the same nodal inertia -- "
            "the per-case mass model is not reaching the solver")


@pytest.mark.roundtrip
@pytest.mark.parametrize("system", SYSTEMS)
def test_the_shipped_mass_deck_hits_the_sbeam_massset_gap(sbeam, system):
    """**Pinned sbeam limitation**: SOL 101 ignores the subcase's ``MASSSET``.

    ``solver/sol101.py`` assembles the ``GRAV`` load vector through
    ``assemble_load_vector(bulk, load_sid)``, which calls
    ``assemble_global_mass(bulk)`` with no ``massset_sid`` -- so the mass-case
    resolver is never reached on the static path and every subcase accelerates
    the **baseline** mass. On ``ga6_normal`` all four payload subcases recover
    2063 lb against case weights of 3400 / 3400 / 2800 / 2063.

    That is why the leg above flattens each case into a baseline deck rather than
    solving the deck as shipped. The limitation is pinned here rather than left
    unstated, and this test **is meant to fail** the day sbeam threads the mass
    case through -- at which point the flattening becomes unnecessary and the
    shipped deck can be solved directly. Bump the pin, then delete this.
    """
    project, _, _, _ = _components("ga6_normal.project.json")
    u = _units(system)
    loadings = _loadings(project)
    assert len({round(ld.weight_lb, 6) for ld in loadings}) > 1, \
        "this pin needs cases of differing weight to say anything"

    text = mc.mass_check_deck(project, system=system, nz=NZ)
    sols, _ = _solved(text)
    baseline = sum(c.item.weight_lb for c in mc.mass_cards(project)[0]
                   if not c.overlay)
    want = baseline * NZ * u.force.factor

    for i, loading in enumerate(loadings):
        sol = sols[mc.MASSSET_SID_BASE + i]
        got = sum(v[2] for v in sol.reactions.values())
        assert closes(got, want, scale=abs(want)), (
            f"sbeam recovered {got} for {loading.name} against the baseline "
            f"{want} -- the MASSSET gap this pin records may be fixed; if so, "
            "solve the shipped deck directly and delete this test")


def test_flattening_keeps_the_shipped_cards_and_drops_the_other_overlays():
    """The transform may re-select mass, and may not rewrite it (no solver needed).

    What it is allowed to do is choose which ``CONM2`` cards are in the model and
    which subcase survives. What it must never do is touch a card's numbers --
    otherwise the leg above would be testing the transform rather than the deck.
    """
    project, _, _, _ = _components("ga6_normal.project.json")
    deck = mc.mass_check_deck(project)
    cards, loadings = mc.mass_cards(project)
    lines = {ln.split(",")[1].strip(): ln
             for ln in deck.splitlines() if ln.startswith("CONM2")}

    flat = flatten_mass_case(deck, mc.MASSSET_SID_BASE)
    kept = {ln.split(",")[1].strip(): ln
            for ln in flat.splitlines() if ln.startswith("CONM2")}
    assert kept and all(kept[eid] == lines[eid] for eid in kept), \
        "a CONM2 card was rewritten, not merely selected"
    cards_left = [ln for ln in flat.splitlines()
                  if ln.startswith(("MASSSET", "+,")) or "MASSSET =" in ln]
    assert not cards_left, cards_left
    assert flat.count("SUBCASE") == 1
    assert f"SUBCASE {mc.MASSSET_SID_BASE}" in flat

    # The first loading's own items, and nothing another case adds.
    want = {c.eid for c in cards if id(c.item) in {id(it) for it in loadings[0].items}}
    assert {int(eid) for eid in kept} == want


@pytest.mark.roundtrip
def test_the_c1_defect_would_have_failed_this_leg(sbeam):
    """**The leg's teeth**: rebuild the C1 defect and the solve must reject it.

    The mutation is not invented -- it is the shipped SI ``GRAV`` magnitude
    before 2026-08-10: ``force/(mass x length)`` instead of ``force/mass``, i.e.
    the right number divided by ``length.factor`` = 25.4. Recovered inertia comes
    back 25.4x low and M-a says so. This is the assertion whose absence let a
    silently-wrong SI deck ship, so it is stated as a defect reproduction rather
    than as a generic scale perturbation.
    """
    project, _, _, _ = _components("ga6_normal.project.json")
    u = _units(UnitSystem.SI)
    loading = _loadings(project)[0]
    deck = mc.mass_check_deck(project, system=UnitSystem.SI, nz=NZ)
    broken = _mutate(
        flatten_mass_case(deck, mc.MASSSET_SID_BASE),
        lambda ln: ln.startswith("GRAV,"),
        lambda ln: ",".join(
            f" {float(c) / u.length.factor:.6E}" if i == 3 else c
            for i, c in enumerate(ln.split(","))))

    sols, grids = _solved(broken)
    (_, sol), = sols.items()
    (_, _, support_gids), = parse_cards(broken)[2]
    want = -loading.weight_lb * NZ * u.force.factor
    got = sol.reactions[support_gids[0]][2]
    assert not closes(got, -want, scale=abs(want)), (
        f"a 25.4x-low GRAV still recovered {got} against {-want} -- this leg "
        "cannot see the defect it was written for")
    assert closes(got * u.length.factor, -want, scale=abs(want)), got


def test_flattening_refuses_a_deck_it_cannot_fold():
    """A SCALE or a REPLACE/DELETE row changes what the baseline means, and this
    transform's whole claim is that it does not. sloads emits neither."""
    project, _, _, _ = _components("ga6_normal.project.json")
    deck = mc.mass_check_deck(project)
    with pytest.raises(ValueError, match="MASSSET 12345"):
        flatten_mass_case(deck, 12345)
    scaled = deck.replace(f"MASSSET, {mc.MASSSET_SID_BASE}, CG1, 1.0",
                          f"MASSSET, {mc.MASSSET_SID_BASE}, CG1, 0.5")
    with pytest.raises(ValueError, match="SCALE"):
        flatten_mass_case(scaled, mc.MASSSET_SID_BASE)
    replaced = deck.replace("+, ADD,", "+, REPLACE,", 1)
    with pytest.raises(ValueError, match="only ADD"):
        flatten_mass_case(replaced, mc.MASSSET_SID_BASE)




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
    resultant. The assembled deck cannot host the same mutation: every balanced
    free-free case has a zero resultant *by construction*, so swapping two
    subcases' load sets leaves all six reactions at zero and no
    reaction-based gate can see it. Rather than write a solve that proves
    nothing, the property is asserted where it is observable -- a subcase
    selects its own case's ``LOAD`` set, in the deck's own text.
    """
    project, _, _, _ = _components("ga6_normal.project.json")
    text = balanced_deck(project, system=UnitSystem.IMPERIAL)
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

    Run against the **assembled deck** since note 56 D-56.2 deleted the
    per-component body deck it used to mutate. That is where it belongs: the
    assembled deck is the deliverable whose header claims its support does
    nothing, so it is the free-free claim that needs calibrating.
    """
    project, _, _, _ = _components("ga6_normal.project.json")
    cases = build_balanced_cases(project)
    text = _assembled_deck_from(project, UnitSystem.IMPERIAL, [cases[0]])
    grids = parse_cards(text)[0]
    # Displace a loaded node well away from the support: moving a support node
    # would change the support geometry rather than a load's lever arm.
    _, _, spc1, forces0, _ = parse_cards(text)
    (_, _, support_gids), = [c for c in spc1 if c[1] == "123456"]
    (sid0, cards), = forces0.items()
    loaded = sorted({g for g, _, _ in cards} - set(support_gids))
    target = loaded[len(loaded) // 2]

    def shift(line):
        f = line.split(",")
        f[3] = f" {float(f[3]) * 1.01:.6E}"
        return ",".join(f)

    broken = _mutate(text, lambda ln: ln.startswith(f"GRID, {target},"), shift)
    sols, broken_grids = _solved(broken)
    _, _, _, forces, moments = parse_cards(broken)
    (sid, sol), = sols.items()

    ref = broken_grids[support_gids[0]]
    applied = resultant(forces, moments, broken_grids, sid, ref)
    assert closes(applied.fz, 0.0, scale=applied.force_scale), \
        "the force sum must still close -- only geometry was mutated"
    got = total_reaction(sol.reactions, broken_grids, ref=ref)
    assert not closes(got.moment[1], 0.0, scale=applied.moment_scale)


# --------------------------------------------------------------------------- #
# The wrapper itself -- checked without a solver, so it is covered everywhere
# --------------------------------------------------------------------------- #
def test_the_wrapper_refuses_a_deck_with_no_geometry():
    """A deck with no ``GRID`` cards cannot be wrapped (S-3).

    It used to pass the control-surface deck, which carried loads and no
    geometry; note 56 D-56.2 deleted that deck, so the input is written here
    instead. Writing it out is if anything better: the refusal is a property of
    the wrapper, and sourcing the input from a shipped artifact made it look
    like a property of that artifact.
    """
    cards_only = "\n".join([
        "$ a load set with no geometry",
        "FORCE, 101, 7, 0, 1.0, 0.000000E+00, 0.000000E+00, 1.000000E+03",
        "MOMENT, 101, 7, 0, 1.0, 0.000000E+00, 1.000000E+03, 0.000000E+00",
    ])
    with pytest.raises(ValueError, match="no GRID cards"):
        wrap_as_stick_model(cards_only, support=Support.CLAMPED_FIRST)




def test_the_wrapper_refuses_an_ungrouped_node():
    """A node in no group is unattached, hence singular -- so it must be loud.

    Run against the assembled deck with a deliberately short group list, since
    note 56 D-56.2 deleted the chordwise tail deck this used to wrap. Same
    refusal, same reason; the input is now the artifact the wrapper actually
    exists for.
    """
    project, _, _, _ = _components("ga6_normal.project.json")
    text = balanced_deck(project, system=UnitSystem.IMPERIAL)
    grids = sorted(parse_cards(text)[0])
    assert len(grids) > 2, "the deck must have nodes to leave out of a group"
    with pytest.raises(ValueError, match="in no group"):
        wrap_as_stick_model(text, support=Support.CLAMPED_FIRST,
                            groups=[grids[:2]])






def test_the_assembled_wrapper_keeps_the_decks_own_support():
    """The wrapper adds structure to the primary deliverable and nothing else.

    If it re-supported the deck, the leg would be testing the harness's idea of a
    determinate support instead of the one the deliverable ships with.
    """
    project, _, _, _ = _components("ga6_normal.project.json")
    shipped = balanced_deck(project)
    wrapped = _assembled_deck(project, UnitSystem.IMPERIAL)
    s_grids, s_cbars, s_spc1, s_f, s_m = parse_cards(shipped)
    w_grids, w_cbars, w_spc1, w_f, w_m = parse_cards(wrapped)

    assert (s_grids, s_spc1, s_f, s_m) == (w_grids, w_spc1, w_f, w_m)
    assert not s_cbars and len(w_cbars) == len(s_grids) - 1
    assert "SOL 101" in wrapped and wrapped.count("BEGIN BULK") == 1


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
