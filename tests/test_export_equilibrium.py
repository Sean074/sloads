"""Export-boundary closure gate: every deck, every example, both unit systems.

Concept mode has no printed oracle, so a *stated physics-closure gate in CI* is
what stands in for one (``CLAUDE.md`` required practice 2). Four such checks
already existed, but all four were force-only, Imperial-only, and hand-rolled
four separate times. This module is the gate in its intended form -- one
parameterised sweep over

    every shipped example  x  {Imperial, SI}  x  {wing, body, tail, control}

asserting that each deck's Σ``FORCE`` **and** Σ``MOMENT``, re-derived from the
deck's own card text via :mod:`sloads.export.equilibrium`, equal that
component's own stated resultant. What it adds over what existed:

* **moment closure at all** -- nothing verified a moment from any deck's text.
  In particular the body deck's ``$`` header has claimed "Terminal Myy ...
  (moment equilibrium)" since step C6 with nothing checking it;
* **SI** -- ``system=`` was never varied, so a unit set with
  ``moment.factor != force.factor x length.factor`` (the exact D-19 failure mode)
  passed the whole suite, force-only sums being blind to it;
* **the ga6 oracle fixture's body / tail / control decks**, previously covered on
  the concept fixture only.

Reference points are the per-component convention (``CONVENTIONS.md``; design
note ``docs/40_history/15_export_equilibrium_invariant_plan.md`` §3, E-2): wing ->
its root station, body -> its aft-most station, tail -> its leading-edge chord
station. Tolerances are :mod:`sloads.export.equilibrium`'s, not this file's.

Physics basis: Ref 1 Ch 14 (net wing loads), Ch 15 p103 (the free-free fuselage
beam), Ch 10 (chordwise tail distribution).
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from imperial_baseline import EXAMPLES, _try

from sloads import io
from sloads.report import applied as ap
from sloads.export.bands import band
from sloads.export.coordinates import (
    bending_moment_vector,
    tail_force_to_airplane,
    to_force,
    to_grid,
    to_moment,
)
from sloads.export.equilibrium import (
    closes,
    deck_resultants,
    parse_cards,
    ref_aftmost_loaded,
    ref_first_loaded,
    resultant,
)
from sloads.modules.aileron import build_aileron
from sloads.export.balanced_deck import balanced_deck, case_sids
from sloads.modules.balance import build_balanced_cases
from sloads.modules.body_loads import build_body_loads
from sloads.modules.flap import build_flap
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.net_loads import build_net_loads, loads_ref_axis_results
from sloads.modules.select import build_critical
from sloads.modules.tab import build_tabs
from sloads.modules.tail_span import axial_total as ts_axial
from sloads.modules.tail_span import build_tail_span
from sloads.modules.tail_span import inertia_total as ts_inertia
from sloads.modules.taildist import build_tail_chordwise
from sloads.units import Channel, UnitSystem, deliverable_units

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SYSTEMS = (UnitSystem.IMPERIAL, UnitSystem.SI)


def _project(example: str):
    """One example with its envelope + critical set materialised."""
    p = io.load_project(os.path.join(_ROOT, "examples", example))
    if p.envelope is None:
        p.envelope = build_envelope(p)
    if p.envelope.critical is None:
        p.envelope.critical = build_critical(p)
    return p


def _components(example: str):
    """``(wing, body, tail, control)`` for one example; a missing slice is ``[]``.

    ``_try`` is ``imperial_baseline``'s: an example that lacks the inputs for a
    component has no deck, and the sweep skips it *with a reason* rather than
    quietly passing an empty assertion (see :func:`test_every_example_has_decks`,
    which pins what each fixture is expected to produce)."""
    p = _project(example)
    net = _try(build_net_loads, p)
    wing = loads_ref_axis_results(p, net.wing_net) if net is not None else []
    body = _try(build_body_loads, p) or []
    tail = _try(build_tail_chordwise, p) or []
    control = []
    for build in (build_aileron, build_flap, build_tabs):
        control += _try(build, p) or []
    spans = _try(build_tail_span, p) or {}
    return wing, body, tail, control, spans.get("htail", []), spans.get("vtail", [])


_CACHE = {}


def _cached(example: str):
    if example not in _CACHE:
        _CACHE[example] = _components(example)
    return _CACHE[example]


def _units(system):
    return deliverable_units(system, Channel.SOLVER)


def _skip_if_empty(results, example, what):
    if not results:
        pytest.skip(f"{example}: no {what} slice (fixture carries no {what} inputs)")




#: Nodes carrying an offset couple, per fixture that hangs a point mass on the
#: wing -- one per strip that holds one. See
#: :func:`test_offset_couples_exist_only_where_a_concentrated_mass_does`.
_COUPLE_NODES = {
    "atr42_100.project.json": 1,      # engine + fuel, one strip
    "baron_58.project.json": 4,       # engine/gear/fuel/systems, four strips
    "concept_heavy.project.json": 1,  # engine + fuel, one strip
}


def _has_concentrated_wing_mass(example: str) -> bool:
    """True if the fixture hangs point masses (engine, gear, fuel, store) on the
    wing -- ``atr42_100``, ``baron_58`` and ``concept_heavy`` do; the rest
    do not."""
    wm = _project(example).wing_mass
    return bool(wm and wm.concentrated)




@pytest.mark.parametrize("example", EXAMPLES)
@pytest.mark.parametrize("system", _SYSTEMS)
def test_wing_deck_reproduces_the_station_table_at_every_node(example, system):
    """Shear **and** bending match the NETLOADS table at *every* station, not
    just the root -- the property the offset couples buy.

    A force split between the bracketing nodes (the fix as originally filed)
    would also close at the root, but only by moving load outboard, which
    corrupts the shear at that node by 22 % on ``atr42_100``. This test is what
    separates the two: it re-derives, from the deck's own text, the shear and
    bending carried by everything outboard of each station and compares with
    that station's published cumulative values. Design note 14 D-1.

    **Summed from the applied load set itself since note 56 D-56.2**, which
    deleted the wing stick deck this used to re-derive from. The claim is
    unchanged and so is the arithmetic -- the deck's cards *were* this set,
    written out -- and under D-56.9 the applied set is the authority the
    delivered cards are written from, so this is the gate moving one step
    closer to its own subject rather than losing it.
    """
    wing, _, _, _, _, _ = _cached(example)
    _skip_if_empty(wing, example, "wing")
    u = _units(system)
    for r in wing:
        loads = ap.wing_nodal_loads(r)
        gid_of = {ap.station_gid(i): i for i in range(len(r.stations))}
        for k, st in enumerate(r.stations):
            ref = (st.x, st.y, st.z)
            # Everything this station carries: its own applied load and every
            # applied load outboard of it, summed with its lever arm.
            f = [0.0, 0.0, 0.0]
            m = [0.0, 0.0, 0.0]
            f_scale = m_scale = 0.0
            for nl in loads:
                idx = gid_of.get(nl.gid)
                if idx is not None and idx < k:
                    continue
                if idx is None and nl.y < st.y - 1e-9:
                    continue
                comps = (nl.fx, 0.0, nl.fz)
                r_vec = (nl.x - ref[0], nl.y - ref[1], nl.z - ref[2])
                f = [a + b for a, b in zip(f, comps)]
                cross = (r_vec[1] * comps[2] - r_vec[2] * comps[1],
                         r_vec[2] * comps[0] - r_vec[0] * comps[2],
                         r_vec[0] * comps[1] - r_vec[1] * comps[0])
                bx, _, bz = bending_moment_vector(nl.mx, nl.mz, u)
                free = (bx / (u.moment.factor or 1.0), nl.my,
                        bz / (u.moment.factor or 1.0))
                m = [a + c + fr for a, c, fr in zip(m, cross, free)]
                f_scale = max(f_scale, max(abs(v) for v in comps))
                m_scale = max(m_scale, max(abs(v) for v in cross))
            got_fz = to_force(0.0, 0.0, f[2], u)[2]
            got_mx, got_my, got_mz = to_moment(m[0], m[1], m[2], u)
            _, _, want_fz = to_force(0.0, 0.0, st.sz, u)
            want_mx, _, want_mz = bending_moment_vector(st.mxx, st.mzz, u)
            _, want_my, _ = to_moment(0.0, st.myy, 0.0, u)
            fs = to_force(0.0, 0.0, f_scale, u)[2]
            ms = to_moment(0.0, m_scale, 0.0, u)[1]
            where = f"{example} {system.value} wing {r.case} station {k}"
            assert closes(got_fz, want_fz, scale=fs), f"{where} Sz"
            assert closes(got_mx, want_mx, scale=ms), f"{where} Mxx"
            assert closes(got_mz, want_mz, scale=ms), f"{where} Mzz"
            # Torsion too, and by the same rigid-body sum: G-OR-37, the gate
            # that the delivered loads are the applied set and not a
            # differenced column.
            assert closes(got_my, want_my, scale=ms), f"{where} Myy"


@pytest.mark.parametrize("example", EXAMPLES)
def test_offset_couples_exist_only_where_a_concentrated_mass_does(example):
    """The couples are non-zero at exactly the nodes bracketing a concentrated
    mass, and identically zero on a wing that carries none.

    This is the drift guard behind the claim that the fix is a **no-op** on the
    Appendix A fixture: ``ga6_normal``, ``cessna_210`` and
    ``concept_regional_jet`` must export not merely small couples but zero ones,
    so their decks are byte-identical to what they were before the couples
    existed. It also pins the converse -- if a fixture ever gains a wing point
    mass, its couples appear and this test says so.
    """
    wing, _, _, _, _, _ = _cached(example)
    _skip_if_empty(wing, example, "wing")
    expected = _has_concentrated_wing_mass(example)
    for r in wing:
        loads = ap.wing_nodal_loads(r)
        nodes = [i for i, nl in enumerate(loads)
                 if abs(nl.mx) > 1e-6 or abs(nl.mz) > 1e-6]
        where = f"{example} wing {r.case}"
        if expected:
            assert nodes, f"{where}: concentrated mass but no offset couple"
            # One bracketing node per strip that holds a mass. atr42 and
            # concept_heavy put all of theirs in one strip; the Dash 8's
            # nacelle-mounted main gear (butt line 75) sits well inboard of its
            # engine and fuel (168 / 180), so it brackets a second node. A count
            # that moves means the station set or the mass placement moved.
            assert len(nodes) == _COUPLE_NODES[example], \
                f"{where}: couples at {nodes}, expected {_COUPLE_NODES[example]}"
        else:
            assert not nodes, (
                f"{where}: offset couples at {nodes} on a wing with no "
                "concentrated mass -- the correction is not a no-op here")








@pytest.mark.parametrize("example", EXAMPLES)
def test_body_grids_match_station_geometry(example):
    """Every body applied-load row sits at its station's ``x``, under that
    station's GID.

    The check above is only as good as the coordinates it integrates; before
    this step the body decks named GIDs that had no ``GRID`` card in any file.
    Read off the applied load set since note 56 D-56.2 deleted the deck -- the
    rows carry the same GID and the same point, which is what the deck was
    writing.
    """
    project, body = _project(example), _cached(example)[1]
    _skip_if_empty(body, example, "body")
    want = {gid: s.x
            for r in body for gid, s in zip(ap.body_station_gids(r), r.stations)}
    rows = ap.applied_loads("fuselage", body, project=project)
    assert {ld.gid for ld in rows} == set(want)
    for ld in rows:
        assert math.isclose(ld.x, want[ld.gid], rel_tol=1e-6, abs_tol=1e-6)
        assert ld.y == 0.0


















# --------------------------------------------------------------------------- #
# GID-block disjointness (design note §5 step 3)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_gid_blocks_are_disjoint(example):
    """Every GID a deck family actually emits sits inside its **registered**
    band, and no two families collide.

    The band-to-band question is settled once, exhaustively, in
    ``tests/test_bands.py`` -- this test used to hand-enumerate the bands it knew
    about, which is exactly how it stayed blind to the balanced deck's collision
    with the tail-span decks for two months (review F-C1). What is left here is
    the half a registry cannot answer: that the GIDs this example's load sets
    actually state are the ones their owner claims, so an assembled
    multi-component model (L-1) really does compose.

    The chordwise-tail and control-surface rows left with their allocators at
    note 56 D-56.2, and so did the wing stick model's clamped root -- ``GID 1``
    is unallocated until D-56.3's renumber, which is recorded in the registry
    rather than here.
    """
    wing, body, _tail, _control, htail_span, vtail_span = _cached(example)
    emitted = {}   # band name -> GIDs the applied load sets state
    if wing:
        emitted["wing-stick"] = {
            ap.station_gid(i) for i in range(len(wing[0].stations))}
    if body:
        mass, reaction = set(), set()
        for r in body:
            for gid, s in zip(ap.body_station_gids(r), r.stations):
                (reaction if s.source in ap._BODY_REACTION_SOURCES else mass).add(gid)
        emitted["body-mass"] = mass
        emitted["body-reaction"] = reaction
    for component, results in (("htail", htail_span), ("vtail", vtail_span)):
        if results:
            emitted[f"tail-span-{component}"] = {
                ap.tail_span_gid(component, i)
                for r in results for i in range(len(r.stations))}
            control = {ap.tail_control_gid(component, i)
                       for r in results for i in range(len(r.control_loads))}
            if control:
                emitted[f"tail-control-{component}"] = control
    assert emitted, f"{example}: no exportable component at all"
    for name, gids in emitted.items():
        stray = {g for g in gids if g not in band(name)}
        assert not stray, f"{example}: {name} emitted GIDs outside its band: {sorted(stray)}"
    names = sorted(emitted)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            overlap = emitted[a] & emitted[b]
            assert not overlap, f"{example}: {a} and {b} share GIDs {sorted(overlap)}"


@pytest.mark.parametrize("example", EXAMPLES)
@pytest.mark.parametrize("system", _SYSTEMS)
def test_deck_comments_fit_the_free_field_card_width(example, system):
    """No ``$`` line in a shipped deck exceeds 72 columns, in either unit system.

    Swept over the **balanced and LRA decks** since note 56 D-56.2 deleted the
    per-component families this used to walk. Those are the decks that ship, so
    they are the ones whose comment lines a bulk-data reader has to fit.

    Free-field bulk data is 72 columns wide, and the body deck already had a
    one-off assertion of this. It was a one-off: the tail deck's "Applied Fz set
    sums to ... = SF x (LT25 + LT50) = ..." line overran on any five-figure load
    (73 columns on ``ga6_normal``), unnoticed, because nothing swept the other
    deck families. SI makes it worse -- the same number in newtons is wider.

    **Widened to the wing decks, 2026-08-10.** They overran too (the ``$ Axes:``
    line, and ``$ FORCE set sums to root Sz ... Myy ...`` at up to ~100 columns
    in SI); the carve-out existed only because fixing it moves exported wing
    Imperial bytes, which the sweep's own step was not allowed to do. Both wing
    channels are now built through ``deck_format.comment``, so the width is a
    property of the emitter rather than of each hand-fitted sentence.
    """
    from sloads.export.balanced_deck import balanced_deck
    from sloads.export.lra_model import lra_model_bdf

    project = _project(example)
    decks = []
    for name, build in (("balanced", balanced_deck), ("lra_model", lra_model_bdf)):
        try:
            decks.append((name, build(project, system=system)))
        except (ValueError, KeyError, AttributeError):
            continue          # a refused model is a stated absence, not a deck
    if not decks:
        pytest.skip(f"{example}: no deck ships for this fixture")
    for name, text in decks:
        over = [ln for ln in text.splitlines()
                if ln.startswith("$") and len(ln) > 72]
        assert not over, f"{example} {system.value} {name}: {over}"


def test_body_gid_block_capacity_still_guarded():
    """``body_station_gids`` still refuses to run past its 500-GID block into the
    tail's -- the guard that keeps the disjointness above true by construction
    rather than by fixture size."""
    import copy

    _, body, _, _, _, _ = _cached("ga6_normal.project.json")
    assert body
    r = copy.deepcopy(body[0])
    proto = [s for s in r.stations if s.source not in ap._BODY_REACTION_SOURCES][0]
    r.stations = [copy.deepcopy(proto)
                  for _ in range(band("body-mass").size + 1)]
    with pytest.raises(ValueError, match="exceed"):
        ap.body_station_gids(r)


# --------------------------------------------------------------------------- #
# Sweep coverage -- what each fixture is expected to produce
# --------------------------------------------------------------------------- #
def test_every_example_has_decks():
    """Pin which components each fixture exports, so a skip above is a recorded
    fact about the fixture and not a silently-vanished check.

    Order is ``(wing, body, tail, control, htail_span, vtail_span)``. The reference aircraft carry no
    ``aileron_loads`` / ``flap_loads`` / ``tab_loads`` input slices, so they have
    no control-surface deck; ``concept_heavy`` additionally has no tail slice.
    ``ga6_normal``, ``cessna_210`` and ``concept_regional_jet`` export all four
    families.

    ``concept_heavy`` **gained a body deck at step B1**: it carries no
    ``fuselage_mass.stations`` at all, and was the one fixture with no fuselage
    loads for that reason. The beam is now derived from ``weight.items`` (the
    mass SSOT), so a project needs no hand-entered station table to have a
    fuselage.
    """
    coverage = {ex: tuple(bool(c) for c in _cached(ex)) for ex in EXAMPLES}
    assert coverage == {
        "atr42_100.project.json": (True, True, True, False, True, True),
        "baron_58.project.json": (True, True, True, True, True, True),
        "concept_heavy.project.json": (True, True, False, False, False, False),
        "concept_regional_jet.project.json": (True, True, True, True, True, True),
        "ga6_normal.project.json": (True, True, True, True, True, True),
    }


if __name__ == "__main__":
    sys.exit(pytest.main([os.path.abspath(__file__), "-q"]))


# --------------------------------------------------------------------------- #
# G-OR-72 -- the deck's *basis*, not only its balance (design note 49 OR-116)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_the_balanced_deck_is_limit_and_no_existing_gate_can_see_it(example):
    """The gate the suite could not previously provide.

    Every other deck check in this file is an **equilibrium** check, and
    equilibrium is scale-invariant: multiply every card by 1.5 and each one
    still passes, because both sides of the comparison move together. That is
    exactly why note 49 §2 could argue the deck's basis "needs deciding in a
    design note rather than discovering in a diff" -- the whole suite was green
    at either basis. This asserts the basis itself.

    **Measured, 2026-09-05.** Re-applying ``case.safety_factor`` in
    ``balanced_deck._load_lines`` -- the multiply OR-116 removed -- fails this
    gate on **all six fixtures** and leaves **all 154 other checks in this file
    green**. The mutation is the regression this exists to catch, and nothing
    else in the suite can see it.

    Two independent statements, because one alone is weak:

    1. **The physics.** For a balanced free-free case the inertia load set sums
       to ``-nz * W`` exactly -- measured -1.000 on every case of every fixture.
       The airplane's own load factor and weight are the datum, so the assertion
       is against the regulation's quantity rather than against another of our
       own numbers. With the 23.303 factor applied this would read ``-1.5 nz W``.
    2. **The shipped artifact.** The written deck's ``FORCE`` cards carry the
       calc's own magnitudes. This reads the file rather than the model, which
       is the project's standing lesson about gates that read what actually
       ships.
    """
    project = io.load_project(os.path.join(_ROOT, "examples", example))
    built = _try(build_balanced_cases, project)
    cases = (built[0] if isinstance(built, tuple) else built) or []
    if not cases:
        pytest.skip(f"{example} assembles no balanced case")

    checked = 0
    for case in cases:
        # (1) the basis, against nz * W. Flight cases only: a ground case carries
        # gear reactions rather than a distributed inertia set, so the identity
        # is not defined for it -- ``checked`` keeps the gate from going vacuous
        # if that ever becomes true of every case.
        inertia = math.fsum(lv.fz for lv in case.loads if "inertia" in lv.source)
        if inertia == 0.0:
            continue
        checked += 1
        nz_w = case.nz * case.weight_lb
        sf = case.safety_factor or 1.0
        assert math.isclose(inertia, -nz_w, rel_tol=1e-6), (
            f"{example}/{case.label}: inertia resultant {inertia:.1f} is not "
            f"-nz*W = {-nz_w:.1f}; at SF={sf} an ULTIMATE deck "
            f"would read {-nz_w * sf:.1f}")
        # ...and, where the factor is not unity, the ultimate value is excluded
        # by name rather than merely not matched by the line above.
        if sf != 1.0:
            assert not math.isclose(inertia, -nz_w * sf, rel_tol=1e-6), (
                f"{example}/{case.label}: inertia resultant carries its factor")
    assert checked, f"{example}: no case carried an inertia set -- gate vacuous"

    # (2) the same statement read off the written deck.
    #
    # The *signed* total is useless here: the deck is balanced, so both sides
    # are zero and the comparison is dominated by the card format's rounding.
    # The scale-carrying quantity is the sum of absolute card loads, which is
    # what a factor at the writer would multiply.
    #
    # One card per load, not one per node: ``_load_lines`` writes a card for
    # every load and several may share a GID, which the solver sums. Merging
    # the model side first would cancel opposite-signed loads at a node and
    # under-count by ~0.3 % -- enough to look like a real discrepancy and not
    # enough to look like a factor.
    text = balanced_deck(project, system=UnitSystem.IMPERIAL, cases=cases)
    for sid, case in zip(case_sids(cases), cases):
        want = math.fsum(
            abs(lv.fz) for lv in case.loads
            if max(abs(lv.fx), abs(lv.fy), abs(lv.fz)) > 1e-9)
        got = math.fsum(
            abs(float(ln.split(",")[7]))
            for ln in text.splitlines()
            if ln.startswith(f"FORCE, {sid},"))
        assert want > 0.0, f"{example}/{case.label}: no nodal load to check"
        assert math.isclose(got, want, rel_tol=1e-4), (
            f"{example}/{case.label}: the deck's total |Fz| {got:.1f} is not "
            f"the calc's {want:.1f} (ratio {got / want:.4f}) -- a factor was "
            f"applied at the writer")
