"""The LRA beam model (step 12) -- skeleton, transfer rule, refusals, import.

Design notes: ``docs/40_history/24_lra_beam_model_review_note.md`` (BM-1..BM-5)
and ``docs/40_history/27_lra_model_implementation_note.md`` (LM-1..LM-7, the
gates this file pins). The solver half of the gates -- reactions, the SOB and
post internal loads through sbeam -- lives in ``tests/test_sbeam_roundtrip.py``.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import pytest

from sloads import io
from sloads.export import bands as bd
from sloads.export.balanced_deck import balanced_deck
from sloads.export.coordinates import transfer_couple
from sloads.export.equilibrium import closes, deck_resultants, parse_cards, resultant
from sloads.export.lra_import import (
    LRA_IMPORT_TOL_IN,
    lra_loads_on_imported_model,
    read_lra_model,
    validate_imported_model,
)
from sloads.export.lra_model import (
    JOINT_MERGE_FRACTION,
    LraRefusal,
    build_lra_model,
    lra_model_bdf,
    transferred_case_loads,
)
from sloads.export.mass_cards import mass_check_deck
from sloads.tail_geometry import HTAIL, VTAIL, resolve_tail_planform

_EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def _project(name: str):
    return io.load_project(os.path.join(_EXAMPLES, name))


_ORIGIN = (0.0, 0.0, 0.0)


def _origin_ref(sid, grids, cards):
    return _ORIGIN


# --------------------------------------------------------------------------- #
# LM-1 -- the transfer rule and its single owner
# --------------------------------------------------------------------------- #
def test_the_transfer_couple_is_the_exact_lever_arm_cross_product():
    """``(p - n) x F``, right-handed, in the identity frame -- the drift guard
    on the one owner every mover in the export channel instantiates (R-11)."""
    p, n, f = (10.0, 20.0, 30.0), (1.0, 2.0, 3.0), (5.0, -7.0, 11.0)
    dx, dy, dz = 9.0, 18.0, 27.0
    expected = (dy * f[2] - dz * f[1], dz * f[0] - dx * f[2],
                dx * f[1] - dy * f[0])
    assert transfer_couple(p, n, f) == expected
    # Moving a load to its own point carries no couple -- the identity that
    # makes an on-node transfer exact rather than approximately zero.
    assert transfer_couple(p, p, f) == (0.0, 0.0, 0.0)


# --------------------------------------------------------------------------- #
# The skeleton (LM-2..LM-6) on the shipped fixtures
# --------------------------------------------------------------------------- #
def test_the_skeleton_carries_every_named_node_family():
    """Conventional layout with a centreline engine (ga6_normal;
    cessna_210 held this slot until #264 -- the surviving twins are either
    T-tails or wing-engined): SOB pair, posts, fin root, h-tail attachment
    pair, gear, engine -- each tagged, each tied (BM-5)."""
    model = build_lra_model(_project("ga6_normal.project.json"))
    families = {(n.family, n.side) for n in model.nodes if n.family}
    for expected in (("lra-sob", "R"), ("lra-sob", "L"), ("lra-post", "F"),
                     ("lra-post", "A"), ("lra-fin-root", "C"),
                     ("lra-attach", "R"), ("lra-attach", "L"),
                     ("lra-centre", "C"), ("lra-engine-mount", "C"),
                     ("lra-gear", "L"), ("lra-gear", "R")):
        assert expected in families, expected
    # Every tagged special node is tied into the structure: it is either a
    # chain member (attachments are inserted into the h-tail chain) or an
    # RBE2 dependent -- an orphan node would make the solve singular.
    chained = {g for ga, gb in model.cbars for g in (ga, gb)}
    tied = model.dependent_gids | {gn for gn, *_ in model.rbe2s}
    for n in model.nodes:
        assert n.gid in chained or n.gid in tied, (n.family, n.side, n.gid)


def test_the_t_tail_htail_hangs_on_the_fin_tip_not_the_fuselage():
    """concept_regional_jet declares a T-tail: the h-tail's one support is the
    centreline joint tied to the fin tip (R-6), and no lra-attach R/L pair
    exists -- a fuselage-side pair would describe a load path this airplane
    does not have."""
    model = build_lra_model(_project("concept_regional_jet.project.json"))
    families = {(n.family, n.side) for n in model.nodes if n.family}
    assert ("lra-attach", "C") in families
    assert ("lra-attach", "R") not in families
    # The fin beam runs to the fin TIP, which is a node because it is a joint
    # (note 54 D-54.5). Before the register the chain stopped at the outermost
    # strip midpoint and this tie spanned an arm the airplane does not have.
    assert ("lra-fin-tip", "C") in families
    joint = next(n for n in model.nodes if n.family == "lra-attach")
    vtail_tip_ties = [(gn, gms) for gn, _cm, gms, label in model.rbe2s
                      if "fin tip" in label]
    assert vtail_tip_ties and joint.gid in vtail_tip_ties[0][1]
    # ...and it spans the arm the two planform owners state: the h-tail
    # centreline LRA sits 26.68 in forward of the fin-tip LRA, in the SAME
    # waterline (note 54 gate 2). The z member is zero by construction -- the
    # h-tail waterline's fin-tip branch IS fin root + fin span.
    tip = next(n for n in model.nodes if n.family == "lra-fin-tip")
    assert tip.gid == vtail_tip_ties[0][0]
    assert joint.pos[0] - tip.pos[0] == pytest.approx(-26.68, abs=5e-3)
    assert joint.pos[2] - tip.pos[2] == pytest.approx(0.0, abs=1e-9)


def test_the_split_fuselage_has_no_element_through_the_carry_through():
    """BM-2 structurally: no CBAR spans the front->rear spar region, so the
    forward and aft cantilever sums are recoverable element end forces."""
    from sloads.derived_geometry import carry_through

    project = _project("atr42_100.project.json")
    ct = carry_through(project)
    model = build_lra_model(project)
    pos = {n.gid: n.pos for n in model.nodes}
    for ga, gb in model.cbars:
        xa, xb = pos[ga][0], pos[gb][0]
        # Only fuselage elements have both ends on the centreline plane and
        # a run along x (the fin runs along z at y = 0 but shares one x).
        if abs(pos[ga][1]) < 1e-9 and abs(pos[gb][1]) < 1e-9 \
                and abs(xa - xb) > 1e-9:
            lo, hi = min(xa, xb), max(xa, xb)
            assert not (lo < ct.x_f - 1e-6 and hi > ct.x_r + 1e-6), (
                f"element {ga}-{gb} spans the carry-through "
                f"({lo:.1f}..{hi:.1f} vs spars {ct.x_f:.1f}/{ct.x_r:.1f})")


def test_the_wing_chain_starts_at_the_sob_and_inboard_strips_collapse_there():
    """R-3: the wing member's inboard-most node is the SOB, and every wing
    strip load inboard of it lands ON that node -- the sob_collapsed_load
    behaviour, produced by the one transfer rule rather than a special case."""
    from sloads.derived_geometry import sob_station
    from sloads.modules.balance import build_balanced_cases

    project = _project("atr42_100.project.json")
    sob = sob_station(project)
    model = build_lra_model(project)
    right = model.members["wing-R"]
    assert abs(right[0].pos[1] - sob.y) < 1e-6 and right[0].family == "lra-sob"

    case = build_balanced_cases(project, [])[0]
    inboard = [ld for ld in case.loads
               if ld.source.startswith("wing-") and ld.side == "R"
               and ld.y < sob.y - 1e-6]
    assert inboard, "the centre box carries strips inboard of the SOB"
    loads = transferred_case_loads(case, model)
    sob_gid_r = right[0].gid
    assert sob_gid_r in loads
    # The collapse is resultant-preserving by LM-1 (the invariant test below
    # proves it); what this pins is the ROUTING: every inboard strip's nearest
    # wing-chain node is the SOB itself, so none lands anywhere outboard.
    nearest = {min(right, key=lambda n: (n.pos[1] - ld.y) ** 2
               + (n.pos[0] - ld.x) ** 2 + (n.pos[2] - ld.z) ** 2).gid
               for ld in inboard}
    assert nearest == {sob_gid_r}


def test_missing_data_refuses_with_the_datum_named():
    """BM-3/LM-4: a project with no fuselage data refuses on the SOB; a wing
    with no entered LRA refuses on the axis; a strip-pair h-tail attachment
    refuses. The error is the fix's name, never a default. (``ga6_normal`` was
    the no-body fixture until the Pri 1 fixture-data pass gave it the Appendix
    A outline; ``concept_heavy`` still has none.)"""
    with pytest.raises(LraRefusal, match="side of body"):
        build_lra_model(_project("concept_heavy.project.json"))
    ga = _project("ga6_normal.project.json")
    ga.geometry.fuselage = None
    with pytest.raises(LraRefusal, match="no fuselage outline"):
        build_lra_model(ga)

    project = _project("atr42_100.project.json")
    project.geometry.by_name("wing").ref_axis_pct = None
    with pytest.raises(LraRefusal, match="ref_axis_pct"):
        build_lra_model(project)


def test_discrete_control_nodes_ship_as_tagged_skeleton(monkeypatch):
    """LM-6: with T6 hinge geometry entered the elevator's hinge/actuator
    nodes appear, tagged, each rigidly tied to an inserted parent node -- and
    with no chain of their own (that would be R-12's redundant hinge set)."""
    from sloads.models import TailMassInput

    project = _project("atr42_100.project.json")
    project.tail_mass.append(TailMassInput(
        surface="htail", control_load_mode="discrete",
        hinges_span_in=[30.0, 90.0], actuator_span_in=55.0))
    model = build_lra_model(project)
    hinges = [n for n in model.nodes if n.family == "lra-hinge"]
    actuators = [n for n in model.nodes if n.family == "lra-actuator"]
    assert len(hinges) == 4 and len(actuators) == 2   # both sides
    chained = {g for ga, gb in model.cbars for g in (ga, gb)}
    for n in hinges + actuators:
        assert n.gid in model.dependent_gids     # tied to the parent
        assert n.gid not in chained              # no chain of their own


# --------------------------------------------------------------------------- #
# The plan-07 invariant on the transferred set (gate 1)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", ["atr42_100.project.json",
                                     "concept_regional_jet.project.json"])
def test_the_transferred_set_has_the_balanced_decks_resultant(example):
    """Every case, all six components, about one reference point: the LRA
    deck's card resultant equals the assembled balanced deck's -- the transfer
    is exact (LM-1) and nothing was dropped or double-routed (LM-7)."""
    from sloads.export.balanced_deck import balanced_deck

    project = _project(example)
    lra = deck_resultants(lra_model_bdf(project), _origin_ref)
    bal = deck_resultants(balanced_deck(project), _origin_ref)
    assert set(lra) == set(bal) and lra
    for sid in bal:
        a, b = lra[sid], bal[sid]
        for comp in ("fx", "fy", "fz", "mx", "my", "mz"):
            scale = a.force_scale if comp.startswith("f") else a.moment_scale
            assert closes(getattr(a, comp), getattr(b, comp), scale=scale), (
                sid, comp, getattr(a, comp), getattr(b, comp))


# --------------------------------------------------------------------------- #
# Import (note 25 §6)
# --------------------------------------------------------------------------- #
def test_an_exported_model_reimports_with_every_family_mapped():
    project = _project("concept_regional_jet.project.json")
    deck = lra_model_bdf(project)
    imported = read_lra_model(deck)
    families = {key.split()[0] for key in imported.tags}
    assert {"lra-sob", "lra-post", "lra-fin-root", "lra-fin-tip",
            "lra-attach", "lra-centre", "lra-gear"} <= families
    notes = validate_imported_model(project, imported)
    assert any("validated" in n for n in notes)


def test_the_imported_loads_reproduce_the_exported_resultant():
    """Export -> import -> transfer lands the same load sets: identical
    resultant per case, under the imported (here: the exported) GIDs."""
    project = _project("atr42_100.project.json")
    deck = lra_model_bdf(project)
    imported = read_lra_model(deck)
    cards = lra_loads_on_imported_model(project, imported)
    grids, _, _, f1, m1 = parse_cards(deck)
    _, _, _, f2, m2 = parse_cards(cards)
    assert set(f1) == set(f2)
    for sid in f1:
        a = resultant(f1, m1, grids, sid, _ORIGIN)
        b = resultant(f2, m2, grids, sid, _ORIGIN)
        for comp in ("fx", "fy", "fz", "mx", "my", "mz"):
            scale = a.force_scale if comp.startswith("f") else a.moment_scale
            assert closes(getattr(a, comp), getattr(b, comp), scale=scale), (
                sid, comp)


def test_a_divergent_tagged_node_fails_loudly():
    """An import whose tagged SOB sits beyond LRA_IMPORT_TOL_IN of the
    geometry-derived position raises, naming both points -- the T1 validator
    pattern; loads must never be exported onto the wrong structure."""
    project = _project("atr42_100.project.json")
    deck = lra_model_bdf(project)
    # Found by its BM-5 tag, not by a literal id: the gid moved once already
    # (note 56 D-56.3 renumbered the LRA onto its own run) and the tag is the
    # identity this validator is about.
    sob = read_lra_model(deck).tags["lra-sob R"]
    doctored = []
    hit = False
    for line in deck.splitlines():
        if not hit and line.startswith(f"GRID, {sob},"):
            f = [c.strip() for c in line.split(",")]
            f[4] = f"{float(f[4]) + 2 * LRA_IMPORT_TOL_IN:.6E}"
            line = ", ".join(f)
            hit = True
        doctored.append(line)
    assert hit
    imported = read_lra_model("\n".join(doctored))
    with pytest.raises(ValueError, match="disagree"):
        validate_imported_model(project, imported)


def test_a_model_with_no_grids_is_refused():
    with pytest.raises(ValueError, match="no GRID"):
        read_lra_model("$ empty\nCBAR, 1, 1, 2, 3, 0., 0., 1.\n")


# --------------------------------------------------------------------------- #
# Section families (backlog Pri 7 -- step 14 descoped)
# --------------------------------------------------------------------------- #
def test_every_cbar_references_its_family_section_and_the_four_pairs_are_identical():
    """One ``MAT1``/``PBAR`` pair per :data:`SECTION_FAMILIES`, ``MID == PID`` in
    family order, **identical values** (a different default per family would be
    invented stiffness), and every ``CBAR`` carries the PID of the chain it is
    in -- so a sizing tool overwrites one card per family and nothing else."""
    from sloads.export.lra_model import SECTION_FAMILIES, section_id
    project = _project("atr42_100.project.json")
    model = build_lra_model(project)
    assert len(model.cbar_families) == len(model.cbars)
    assert set(model.cbar_families) == set(SECTION_FAMILIES)
    text = lra_model_bdf(project)
    mat1 = [l for l in text.splitlines() if l.startswith("MAT1,")]
    pbar = [l for l in text.splitlines() if l.startswith("PBAR,")]
    assert [l.split(",")[1].strip() for l in mat1] == ["1", "2", "3", "4"]
    assert [l.split(",")[1].strip() for l in pbar] == ["1", "2", "3", "4"]
    assert [l.split(",")[2].strip() for l in pbar] == ["1", "2", "3", "4"], "PID -> its own MID"
    assert len({",".join(l.split(",")[2:]) for l in mat1}) == 1, "identical MAT1 values"
    assert len({",".join(l.split(",")[3:]) for l in pbar}) == 1, "identical PBAR values"
    for family in SECTION_FAMILIES:
        assert f"$ SLOADS-SECTION {family}" in text
    cbar_pids = [int(l.split(",")[2]) for l in text.splitlines() if l.startswith("CBAR,")]
    assert cbar_pids == [section_id(f) for f in model.cbar_families]
    # The families sit where they should: wing chains outboard, fin vertical.
    positions = {n.gid: n.pos for n in model.nodes}
    for (ga, gb), family in zip(model.cbars, model.cbar_families):
        a, b = positions[ga], positions[gb]
        if family == "wing":
            assert a[1] != 0.0 or b[1] != 0.0
        elif family == "vtail":
            assert a[2] != b[2] and a[1] == b[1] == 0.0
        elif family == "fuselage":
            assert a[1] == b[1] == 0.0 and a[0] != b[0]


# --------------------------------------------------------------------------- #
# Solvability (design note 55) -- the skeleton a solver will actually factor
# --------------------------------------------------------------------------- #
_SOLVE_FIXTURES = ("ga6_normal", "baron_58",
                   "atr42_100", "concept_regional_jet")


@pytest.mark.parametrize("name", _SOLVE_FIXTURES)
def test_no_grid_is_rigidly_tied_on_both_sides(name):
    """Note 55 gate 1 (D-55.1): no chain of rigid elements, any fixture.

    A ``GRID`` that is an ``RBE2`` dependent *and* an ``RBE2`` independent
    states ``a -> b -> c`` in rigid links, which sbeam refuses outright -- the
    reported ``ga6_normal`` failure, where the rear-spar post hung on the
    centre-box hub (BM-2) and also carried both main-gear ties, because the
    nearest body station to the trunnions is the post.

    Exact, no threshold: the assertion is a property of the topology.
    """
    model = build_lra_model(_project(f"{name}.project.json"))
    dependents = {}
    independents = set()
    for gn, _cm, gms, _lbl in model.rbe2s:
        independents.add(gn)
        for g in gms:
            dependents[g] = dependents.get(g, 0) + 1
    for gid, count in dependents.items():
        node = model.node(gid)
        where = f"{node.family} {node.side}".strip() or f"GRID {gid}"
        assert count == 1, f"{name}: {where} is dependent in {count} RBE2s"
        assert gid not in independents, (
            f"{name}: {where} (GRID {gid}) is dependent in one RBE2 and "
            "independent in another -- a rigid chain")


@pytest.mark.parametrize("name", _SOLVE_FIXTURES)
def test_no_tail_chain_carries_a_sliver_element(name):
    """Note 55 gate 2 (D-55.2): a joint insertion never leaves a sliver.

    ``cessna_210``'s h-tail attachment landed 0.0769 in from a strip station --
    1.07 % of that chain's ``ds`` -- for a 1638:1 element-length ratio and the
    singular solve #172 reported; ``baron_58`` was next at 0.1266 in / 1.33 %.
    Every tail ``CBAR`` is now at least ``JOINT_MERGE_FRACTION`` of its own
    chain's strip width, because a station that close is absorbed *into* the
    joint instead of leaving a bar between the two.

    The wing and fuselage chains are deliberately not checked -- the fuselage
    has no strip mesh (its spacing is entered stations plus inserted tie
    points, legitimately down to 0.087 of its own median here) and the wing's
    SOB node is placed by position rather than inserted. See
    ``_refuse_unsolvable_skeleton``.
    """
    project = _project(f"{name}.project.json")
    model = build_lra_model(project)
    planforms = {c: resolve_tail_planform(project, c) for c in (HTAIL, VTAIL)}
    pos = {n.gid: n.pos for n in model.nodes}
    for (ga, gb), family in zip(model.cbars, model.cbar_families):
        planform = planforms.get(family)
        if planform is None:
            continue
        floor = JOINT_MERGE_FRACTION * (
            planform.span / max(2, planform.elements))
        length = sum((pos[ga][i] - pos[gb][i]) ** 2 for i in range(3)) ** 0.5
        assert length >= floor, (
            f"{name}: {family} element {ga}-{gb} is {length:.4f} in, below the "
            f"{floor:.4f} in floor")


def test_the_gear_keeps_the_carrier_the_project_entered():
    """Note 55 gate 3: D-55.1 re-parents, it does not re-route.

    The alternative D-55.1 rejected was folding the gear into the centre-box
    hub tie, as the engine path folds its hub. ``ga6_normal`` enters
    ``carrier BODY``, so its gear must still reach a **fuselage** node -- one
    station off the rear post -- and never the wing hub, which would state a
    load path the project did not enter.
    """
    model = build_lra_model(_project("ga6_normal.project.json"))
    body = {n.gid for n in model.members["fuselage"]}
    hub = next(n.gid for n in model.nodes if n.family == "lra-centre")
    gear_ties = [(gn, gms) for gn, _cm, gms, lbl in model.rbe2s
                 if "gear" in lbl and "carrier BODY" in lbl]
    assert gear_ties, "ga6_normal enters BODY-carried gear"
    for gn, _gms in gear_ties:
        assert gn in body, "a BODY-carried gear leg parents on the fuselage"
        assert gn != hub, "never on the wing centre-box hub"


@pytest.mark.parametrize("name", _SOLVE_FIXTURES)
def test_the_support_node_is_in_no_rbe2_at_all(name):
    """Note 55 gate 5's precondition (D-55.6): the clamp is untied, both ends.

    ``roundtrip._supportable`` has always applied both exclusions, and its
    docstring records why the second is load-bearing: sbeam's
    ``recover_reactions`` subtracts the raw applied vector at the constrained
    DOFs, so a load a rigid element transfers *onto* a constrained node is
    never subtracted and comes back out as reaction. This picker implemented
    only the first, so the rule's two halves lived in two files -- the same
    shape as D-55.1's tie-parent defect, one file down.

    Measured before the fix: ``ga6_normal`` recovered 569.49 lb of Fx against
    an applied set closing to 0.0002 lb, and ``baron_58`` the same through its
    nose-gear tie. Both now solve exactly.
    """
    model = build_lra_model(_project(f"{name}.project.json"))
    tied = model.dependent_gids | {gn for gn, _cm, _gms, _lbl in model.rbe2s}
    assert model.support_gid not in tied, (
        f"{name}: the support node is an RBE2 member, so its recovered "
        "reaction carries the rigidly-transferred load")


def test_a_project_with_no_vertical_tail_still_builds():
    """The chain branches are optional, and the D-55.2 tolerances outlive them.

    Both merge tolerances are read when the control-node parents are inserted,
    which happens whether or not either tail chain exists -- so a project with
    no fin must not reach an unbound local. Caught during D-55.2's own
    implementation, which is exactly the shape of project no fixture is.
    """
    project = _project("ga6_normal.project.json")
    project.geometry.surfaces = [s for s in project.geometry.surfaces
                                 if s.name not in ("vtail", "rudder")]
    if project.geometry.empennage is not None:
        project.geometry.empennage.vtail = None
    project.vtail_loads = None
    model = build_lra_model(project)
    assert model.nodes and "vtail" not in model.members


# --------------------------------------------------------------------------- #
# D-56.3 -- the LRA model owns every grid it writes
# --------------------------------------------------------------------------- #
#: The LRA's own contiguous run (note 56 D-56.3), read off the registry rather
#: than spelled out, so a sub-band added or resized here cannot drift from
#: ``bands.py``.
_LRA_GID_BANDS = tuple(b for b in bd.BANDS
                       if b.kind is bd.IdKind.GID and b.name.startswith("lra-"))


def _grid_positions(deck_text):
    """``{gid: (x, y, z)}`` from a deck's free-field ``GRID`` cards."""
    out = {}
    for line in deck_text.splitlines():
        if not line.startswith("GRID,"):
            continue
        f = [c.strip() for c in line.split(",")]
        out[int(f[1])] = (float(f[3]), float(f[4]), float(f[5]))
    return out


def test_the_lra_run_is_contiguous_and_the_family_is_readable_off_the_id():
    """The shape D-56.3 chose, pinned: one unbroken run of equal sub-bands.

    The point of the run is that ``gid // 1000 - 20`` is the family index, so a
    grid id in a deck or a solver echo says what kind of point it is without a
    lookup. That only holds while the sub-bands stay 999 wide on a 1000 stride,
    which is the thing a later edit would silently break -- a band widened to
    1000 puts its last id in the next family's thousand.
    """
    bands = sorted(_LRA_GID_BANDS, key=lambda b: b.start)
    assert bands, "the LRA owns no GID band at all"
    for i, b in enumerate(bands):
        assert b.start == 20001 + 1000 * i, f"{b.name} breaks the run"
        assert b.size == 999, f"{b.name} is {b.size} wide, not 999"
        assert b.start // 1000 - 20 == i
        assert b.end // 1000 - 20 == i, f"{b.name}'s last id lands in family {i + 1}"
        assert b.owner.startswith("lra_model."), f"{b.name} is owned by {b.owner}"


@pytest.mark.parametrize("example", ("ga6_normal.project.json",
                                     "baron_58.project.json",
                                     "atr42_100.project.json",
                                     "concept_regional_jet.project.json"))
def test_every_lra_grid_comes_from_the_lra_s_own_band(example):
    """Note 56 gate 4, asserted from the emitted deck rather than the builder.

    This is the gate the note is named for. The deliverable used to take its
    right-wing station ids from the wing stick deck's band, its tail-chain ids
    from the two spanwise decks', its control-node ids from the chordwise
    decks' and its gear ids from the balanced deck's -- so four artifacts
    defined the grids of the one that ships, three of them were not
    deliverables, and two of them no longer exist. Reading the deck text rather
    than ``build_lra_model`` is deliberate: an id that reaches a file is the
    thing a solver splices on, and a builder-side assertion would not have
    caught the borrowing either, since the borrowed ids were perfectly valid.
    """
    deck = lra_model_bdf(_project(example))
    gids = set(_grid_positions(deck))
    assert gids, f"{example}: the LRA deck wrote no GRID at all"
    stray = {g for g in gids if not any(g in b for b in _LRA_GID_BANDS)}
    assert not stray, (
        f"{example}: LRA grids outside the LRA's run -- "
        f"{sorted(stray)[:8]} (owners: "
        f"{sorted({bd.owner_of(g) for g in sorted(stray)[:8]})})")


@pytest.mark.parametrize("example", ("ga6_normal.project.json",
                                     "concept_regional_jet.project.json"))
def test_no_gid_is_defined_at_two_positions_across_the_shipped_decks(example):
    """Note 56 gate 3 -- the collision test at the artifact level.

    ``tests/test_bands.py`` proves the *registry* is disjoint; this proves the
    files are, which is a different claim, because a deck can emit an id its
    registered band does not contain (that is gate 4) or two decks can each
    emit correctly from bands that were never compared. The failure this
    forecloses is the D-19 class applied to ids: two decks that splice cleanly
    and silently sum unrelated loads on one node.

    It passes today by construction, and that is the point of writing it: note
    56 asserts (SS1.2) that ``GID 7`` named one point in ``wing_loads.bdf`` and
    another in ``lra_model.bdf``, and on measurement it did not -- the LRA took
    the wing stick band's ids for the stations it shares, so the shared ids
    named the same point. The **borrowing** was real and gate 4 above is what
    catches it; the position collision was not, and the only one on record
    (balanced deck into the spanwise h-tail band, review F-C1) was closed by
    the registry two months ago. So this gate guards a property that is
    currently true rather than reporting one that is broken, which is the
    honest reason to pin it: it was true by accident before, and the next deck
    family is what would re-open it.
    """
    project = _project(example)
    decks = {"lra_model": lra_model_bdf(project),
             "balanced_deck": balanced_deck(project),
             "mass_check_deck": mass_check_deck(project)}
    seen = {}   # gid -> (deck name, position)
    for name, text in decks.items():
        for gid, pos in _grid_positions(text).items():
            prior = seen.setdefault(gid, (name, pos))
            if prior[0] == name:
                continue
            assert prior[1] == pos, (
                f"{example}: GID {gid} is {prior[1]} in {prior[0]} and {pos} "
                f"in {name} -- two artifacts define one node")


if __name__ == "__main__":  # pragma: no cover - self-runner
    import subprocess

    raise SystemExit(subprocess.call(
        [sys.executable, "-m", "pytest", "-q", __file__]))
