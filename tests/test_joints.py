"""The joint register and its drift guard (design note 54, D-54.5 / D-54.7).

The register (``sloads/joints.py``) states, per project, where two components
meet: an owned location, the offset arm to the counterpart node, a DOF set and
a basis. ``export/lra_model`` places its tie nodes by *reading* it, so the
exported positions are copies of one owner rather than a second measurement --
and that is precisely what D-54.7 asks be guarded:

    "one registry-walking test -- for every joint on every fixture, the
    exported tie-node positions equal the register's location, the tie's offset
    arms equal the stated arms, and the tie exists. Exact (rel_tol=1e-9):
    positions are copies of one owner, not measurements"

The walk goes through the **emitted deck text**, not the ``LraModel`` object.
That is deliberate: once ``lra_model`` reads the register, comparing the two
in memory would be very nearly tautological, while parsing the ``GRID`` cards
and their ``$ SLOADS-NODE`` tags out of the bytes proves the joint survives
``to_grid``, the unit channel and the formatter -- which is what an analyst
importing the deck actually receives.

Four guards, in the shapes the suite already uses:

* ``test_the_joint_set_partitions_by_layout`` -- the totality/disjointness
  shape of ``test_empennage.test_the_boundary_derived_marking_partitions_the_tail_blocks``.
  It is also the guard-on-the-guard for the walk: the walk iterates the
  register, so it can only be blind if the register is silently empty.
* ``test_every_joint_is_exported_where_the_register_puts_it`` -- the walk.
  No list of its own, so a joint added to the register is checked the day it
  exists (``test_bands`` style).
* ``test_the_walk_would_have_caught_the_tip_joint_arm`` -- has-teeth, the
  ``test_bands.test_the_registry_would_have_caught_the_balanced_deck_collision``
  shape, and unusually well founded here because the defect is real and
  measured rather than hypothesised.
* ``test_the_assumed_grade_survives_into_the_register_and_the_deck`` -- gate 4,
  both directions, written data-driven so it survives #260 (D-54.6) flipping
  any fixture's spar stations from assumed to entered with no edit here.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import pytest

from sloads import io
from sloads.derived_geometry import carry_through
from sloads.export.lra_model import build_lra_model, lra_model_bdf
from sloads.joints import (
    SPAR_ENTERED,
    SPAR_ESTIMATOR,
    JointName,
    joints,
)

_EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")

#: Every shipped fixture that builds an LRA model -- the walk covers the
#: whole set (the note 54 gate tables named six; two retired at #264).
FIXTURES = ("ga6_normal", "baron_58",
            "atr42_100", "concept_regional_jet")

#: The three T-tails, whose tip joint is the arm note 51's transfer moments
#: are computed across (note 54 §5).
T_TAILS = ("atr42_100", "concept_regional_jet")

#: D-54.7's tolerance: "positions are copies of one owner, not measurements".
#: Applied to the built model, where the copy is exact.
REL_TOL = 1e-9

#: ``abs_tol`` alongside it, because several arm components are exactly ``0.0``
#: (the tip joint's ``z``, the fin-root joint's ``x`` and ``y``) and
#: ``isclose(a, 0.0, rel_tol=...)`` is False for every non-zero ``a``.
ABS_TOL = 1e-9

#: What the **writer** costs, in inches. The deck emits ``%E`` at six decimal
#: places, so a station near 1,000 in keeps about 1e-4 in -- and an *arm*, being
#: the difference of two such stations, carries that same absolute error however
#: short the arm is (which is why this is an absolute tolerance and not a
#: relative one: the T-tail tip arm is 26 in built from stations near 1,060).
#:
#: This is the format's precision, not the geometry's -- the 1e-9 copy identity
#: is asserted against the model. 1e-3 in still sits an order of magnitude below
#: the smallest defect this guard exists to catch (``baron_58``'s 0.010 in
#: attachment gap), so nothing real hides under it.
DECK_TOL_IN = 1e-3


def _project(name: str):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _deck_nodes_and_ties(deck: str):
    """``({(family, side): gid}, {gid: pos}, [(gn, cm, [gm...])])`` from the bytes.

    The deck is the artifact under test, so this reads the cards rather than
    the model: a ``$ SLOADS-NODE <family> <side>`` comment tags the ``GRID``
    that follows it (BM-5), and ``RBE2, eid, gn, cm, gm...`` is the tie.
    """
    tags, pos, ties = {}, {}, []
    pending = None
    for line in deck.splitlines():
        line = line.strip()
        if line.startswith("$ SLOADS-NODE"):
            parts = line.split()
            pending = (parts[2], parts[3] if len(parts) > 3 else "")
        elif line.startswith("GRID"):
            f = [c.strip() for c in line.split(",")]
            gid = int(f[1])
            pos[gid] = (float(f[3]), float(f[4]), float(f[5]))
            if pending is not None:
                tags[pending] = gid
                pending = None
        elif line.startswith("RBE2"):
            f = [c.strip() for c in line.split(",")]
            ties.append((int(f[2]), f[3], [int(g) for g in f[4:] if g]))
        elif line:
            pending = None if not line.startswith("$") else pending
    return tags, pos, ties


def _close(a, b) -> bool:
    return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)


def _deck_close(a, b) -> bool:
    return abs(a - b) <= DECK_TOL_IN


def _deck_prose(deck: str) -> str:
    """The deck's comment prose as one whitespace-normalised string.

    The header wraps its ASSUMED sentences across ``$``-prefixed lines, so a
    substring test against the owner's wording has to unwrap them first --
    otherwise the guard passes or fails on the column width.
    """
    words = []
    for line in deck.splitlines():
        line = line.strip()
        if line.startswith("$"):
            words += line.lstrip("$").split()
    return " ".join(words)


# --------------------------------------------------------------------------- #
# The partition -- and the guard on the walk below
# --------------------------------------------------------------------------- #
def test_the_joint_set_partitions_by_layout():
    """Which joints exist is decided by the layout, and the two tail joints
    are mutually exclusive.

    A T-tail horizontal surface is not fuselage-attached at all -- it sits on
    the fin -- so a T-tail register carries ``vtail_tip_htail`` and **no**
    ``htail_attach``, and a conventional one the reverse. The register gets
    that by asking ``htail_attachment`` for its basis (note 24 BM-3's own
    discriminator) rather than by testing a layout flag, so this asserts the
    partition the owners produce.

    It is also what keeps the walk honest: the walk iterates the register and
    would pass vacuously on an empty one, so every fixture is pinned to a
    non-empty, layout-correct joint set here first.
    """
    seen = set()
    for name in FIXTURES:
        reg = joints(_project(name))
        got = reg.names
        seen |= got
        assert JointName.WING_SOB in got, name
        assert JointName.WING_SPAR_POST in got, name
        assert JointName.VTAIL_ROOT in got, name
        tail = {JointName.VTAIL_TIP_HTAIL, JointName.HTAIL_ATTACH} & got
        assert len(tail) == 1, (name, sorted(j.value for j in tail))
        expected = (JointName.VTAIL_TIP_HTAIL if name in T_TAILS
                    else JointName.HTAIL_ATTACH)
        assert tail == {expected}, name
        # Both members of every pair are present -- a joint that lost a side
        # would leave a tie with one end.
        for pair in (JointName.WING_SOB, JointName.HTAIL_ATTACH):
            sides = {j.side for j in reg.by_name(pair)}
            assert sides in ({"R", "L"}, set()), (name, pair, sides)
        assert {j.side for j in reg.by_name(JointName.WING_SPAR_POST)} == {"F", "A"}
        # No joint is silently half-built.
        for j in reg:
            assert j.basis, (name, j.name)
            assert j.node_family and j.dof, (name, j.name)
    # Every joint kind the enum declares has a producer somewhere in the
    # fixture set: a kind added with nothing to build it fails here.
    assert seen == set(JointName)


# --------------------------------------------------------------------------- #
# D-54.7 -- the registry-walking drift guard
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", FIXTURES)
def test_every_joint_is_exported_where_the_register_puts_it(name):
    """For every joint of every fixture: the deck tags a node of that identity,
    it sits **on** the register's location, a tie reaches its counterpart, and
    that tie spans exactly the stated arm.

    This test has no list of joints of its own -- it walks whatever the
    register produced -- so a joint added to ``sloads/joints.py`` is guarded
    from the moment it exists rather than when somebody remembers to extend a
    fixture list here.

    The arm is compared **direction-agnostically**: which end of a tie is the
    ``RBE2``'s independent node is the exporter's topology choice (the hub is
    independent of its posts, the fin tip independent of the h-tail it
    carries), and this guard is about geometry, not about that choice.
    """
    project = _project(name)
    reg = joints(project)
    model = build_lra_model(project)
    model_pos = {(n.family, n.side): n.pos for n in model.nodes if n.family}
    tags, pos, ties = _deck_nodes_and_ties(lra_model_bdf(project))
    assert reg.joints, name

    for j in reg:
        key = (j.node_family, j.side)
        assert key in tags, f"{name}: the deck tags no {key} node"
        gid = tags[key]
        here = pos[gid]
        # The copy identity, at D-54.7's tolerance, against the model the deck
        # is written from -- this is the clause that says the position is not a
        # second measurement.
        for i, axis in enumerate("xyz"):
            assert _close(model_pos[key][i], j.location[i]), (
                f"{name} {j.name.value} {j.side}: the model puts the node at "
                f"{axis}={model_pos[key][i]!r} and the register owns "
                f"{j.location[i]!r}")
        # ...and it survives the writer, to the format's own precision.
        for i, axis in enumerate("xyz"):
            assert _deck_close(here[i], j.location[i]), (
                f"{name} {j.name.value} {j.side}: the deck puts the node at "
                f"{axis}={here[i]:.6f} and the register owns "
                f"{j.location[i]:.6f}")
        # The tie exists, and spans the stated arm.
        arms = []
        for gn, cm, gms in ties:
            if gn == gid:
                arms += [(cm, tuple(pos[g][i] - here[i] for i in range(3)))
                         for g in gms]
            elif gid in gms:
                arms.append((cm, tuple(pos[gn][i] - here[i] for i in range(3))))
        assert arms, f"{name}: {j.name.value} {j.side} is in no RBE2 at all"
        matched = [cm for cm, arm in arms
                   if all(_deck_close(arm[i], j.arm[i]) for i in range(3))]
        assert matched, (
            f"{name} {j.name.value} {j.side}: no tie spans the stated arm "
            f"{tuple(round(a, 3) for a in j.arm)} -- the deck's ties from this "
            f"node span {[tuple(round(a, 3) for a in arm) for _cm, arm in arms]}")
        assert j.dof in matched, (
            f"{name} {j.name.value} {j.side}: the tie on the stated arm "
            f"constrains {matched} where the register states {j.dof}")


def test_the_register_states_the_note_54_gate_numbers():
    """Note 54 §4's expected values, as printed in the agreed note.

    Against the owners these are exact; against the note's own one-decimal
    figures they are compared at ``abs=0.05``, which is what a printed 1-dp
    number is worth.
    """
    # Gate 1 -- the fin-root joint sits on the L-1 owner's resolution.
    roots = {"ga6_normal": 111.5, "baron_58": 110.0,
             "atr42_100": 191.2, "concept_regional_jet": 87.0}
    for name, z in roots.items():
        reg = joints(_project(name))
        joint = reg.one(JointName.VTAIL_ROOT)
        assert joint.location[2] == pytest.approx(z, abs=0.05), name
        # ...with the vertical arm to the fuselage-LRA node STATED -- the
        # thing that did not exist before D-54.5. It is purely vertical: the
        # body chain carries a node at the fin-root station.
        assert joint.arm[0] == pytest.approx(0.0, abs=ABS_TOL), name
        assert joint.arm[1] == pytest.approx(0.0, abs=ABS_TOL), name
        assert abs(joint.arm[2]) > 1.0, name
        assert joint.to == "fuselage-lra"

    # Gate 2 -- the T-tail tip joint: waterline == fin root + fin span, and the
    # stated x-arm IS the measured LRA offset. The z member is zero by
    # construction (h_tail_waterline's fin-tip branch is that same sum), which
    # is the tell that both ends come from one owner pair.
    tips = {"atr42_100": (316.2, -25.6),
            "concept_regional_jet": (225.0, -26.7)}
    for name, (z, dx) in tips.items():
        reg = joints(_project(name))
        joint = reg.one(JointName.VTAIL_TIP_HTAIL)
        assert joint.location[2] == pytest.approx(z, abs=0.05), name
        assert joint.arm[0] == pytest.approx(dx, abs=0.05), name
        assert joint.arm[2] == pytest.approx(0.0, abs=ABS_TOL), name
        assert joint.basis == "fin-tip", name

    # Gate 3 -- the conventional attachment pair equals htail_attachment with
    # its basis, on the D-54.4 waterline.
    pairs = {"ga6_normal": (6.7, 111.0), "baron_58": (4.6, 105.0)}
    for name, (y, z) in pairs.items():
        reg = joints(_project(name))
        right = reg.one(JointName.HTAIL_ATTACH, "R")
        left = reg.one(JointName.HTAIL_ATTACH, "L")
        assert right.location[1] == pytest.approx(y, abs=0.05), name
        assert left.location[1] == pytest.approx(-y, abs=0.05), name
        assert right.location[2] == pytest.approx(z, abs=0.05), name
        assert right.assumed is True, name          # all three are outline-derived
    # ga6_normal's h-tail waterline is ENTERED and unchanged at 111.0. (The
    # register-carries-the-mass-item-branch assertion retired with cessna_210,
    # #264 -- the branch itself stays pinned in test_tail_geometry on
    # concept_heavy, which enters no tail outline and so builds no register
    # joint to assert it through.)


def test_the_walk_would_have_caught_the_tip_joint_arm():
    """Has teeth, on the defect that motivated the register.

    Two controls. The first perturbs a location by 1 inch and asserts the
    comparison the walk makes actually fails -- a guard whose assertion cannot
    fail is decoration. The second restores the **pre-register construction**
    and states what it cost: the R-6 tie's independent node was the outermost
    fin *strip midpoint* rather than the fin tip, so on ``concept_regional_jet``
    the tie spanned -20.876 in of x where the owners say -26.680, and 6.9 in of
    z that does not exist at all.
    """
    project = _project("concept_regional_jet")
    reg = joints(project)
    joint = reg.one(JointName.VTAIL_TIP_HTAIL)

    # (i) the assertion has teeth.
    moved = (joint.location[0] + 1.0, joint.location[1], joint.location[2])
    assert not all(_close(moved[i], joint.location[i]) for i in range(3))

    # (ii) the historical arm, reconstructed from the same inputs the old code
    # used: the fin's outermost STRIP station, and the h-tail chain
    # interpolated at y = 0 (which on a swept surface answers with the
    # innermost strip's x, not the centreline's).
    from sloads.export.coordinates import tail_station_to_airplane
    from sloads.modules.tail_span import build_tail_span
    from sloads.tail_geometry import HTAIL, VTAIL

    spans = build_tail_span(project)
    v_last = spans[VTAIL][0].stations[-1]
    old_tip = tail_station_to_airplane(v_last.x, v_last.y, VTAIL, v_last.z)
    h_inner = min(spans[HTAIL][0].stations, key=lambda s: abs(s.y))
    old_centre = tail_station_to_airplane(h_inner.x, h_inner.y, HTAIL, h_inner.z)

    assert old_tip[0] - joint.location[0] == pytest.approx(-3.17, abs=0.05)
    old_arm_x = old_centre[0] - old_tip[0]
    assert old_arm_x == pytest.approx(-20.876, abs=0.01)
    assert joint.arm[0] == pytest.approx(-26.680, abs=0.01)
    # 5.8 in of arm -- 22 % -- that the tie spanned and nothing measured.
    assert abs(old_arm_x - joint.arm[0]) == pytest.approx(5.80, abs=0.01)
    # ...and a vertical arm the airplane does not have.
    assert joint.location[2] - old_tip[2] == pytest.approx(6.9, abs=0.05)
    assert joint.arm[2] == pytest.approx(0.0, abs=ABS_TOL)


# --------------------------------------------------------------------------- #
# Gate 4 -- the provenance grade reaches the deliverable
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", FIXTURES)
def test_the_assumed_grade_survives_into_the_register_and_the_deck(name):
    """The spar posts' ASSUMED/entered grade is the carry-through owner's, and
    the sentence it owes its consumer appears in the deck **iff** it is assumed.

    Written against ``carry_through(project).assumed`` rather than against a
    list of which fixtures are currently assumed, so #260 (D-54.6) entering
    real spar stations on any fixture flips both sides of this together and
    needs no edit here.
    """
    project = _project(name)
    ct = carry_through(project)
    deck = lra_model_bdf(project)
    for joint in joints(project).by_name(JointName.WING_SPAR_POST):
        assert joint.assumed == ct.assumed, name
        assert joint.basis == (SPAR_ESTIMATOR if ct.assumed else SPAR_ENTERED)
        if ct.assumed:
            assert joint.note and joint.note in _deck_prose(deck), name
        else:
            assert joint.note == "", name


def test_entered_spar_stations_flip_the_grade_and_drop_the_note():
    """The other direction of gate 4, on a constructed project.

    No shipped fixture enters its spar stations -- all six are on the
    %-of-root-chord estimator -- so the entered branch is exercised the way
    the suite exercises every state no fixture is in (note 54 gate 6 builds a
    contradicting-``h_tail_z`` project the same way). When D-54.6 enters real
    stations this stops being hypothetical, and the parametrized test above
    picks it up with no edit.
    """
    import dataclasses

    project = _project("ga6_normal")
    assert carry_through(project).assumed is True
    wing = project.geometry.by_name("wing")
    entered = dataclasses.replace(wing, front_spar_x_in=70.0, rear_spar_x_in=110.0)
    project.geometry.surfaces = [entered if s is wing else s
                                 for s in project.geometry.surfaces]

    assert carry_through(project).assumed is False
    posts = joints(project).by_name(JointName.WING_SPAR_POST)
    assert {j.side for j in posts} == {"F", "A"}
    for joint in posts:
        assert joint.assumed is False
        assert joint.basis == SPAR_ENTERED
        assert joint.note == ""
    assert [j.location[0] for j in posts if j.side == "F"] == [70.0]
    assert [j.location[0] for j in posts if j.side == "A"] == [110.0]
    # The sentence is gone from the deliverable, not merely from the flag.
    assert "wing spar stations ASSUMED" not in _deck_prose(lra_model_bdf(project))


if __name__ == "__main__":
    test_the_joint_set_partitions_by_layout()
    print("ok partition by layout")
    for _f in FIXTURES:
        test_every_joint_is_exported_where_the_register_puts_it(_f)
    print("ok every joint exported where the register puts it")
    test_the_register_states_the_note_54_gate_numbers()
    print("ok note 54 gate numbers")
    test_the_walk_would_have_caught_the_tip_joint_arm()
    print("ok the walk has teeth")
    for _f in FIXTURES:
        test_the_assumed_grade_survives_into_the_register_and_the_deck(_f)
    print("ok assumed grade reaches the deck")
    test_entered_spar_stations_flip_the_grade_and_drop_the_note()
    print("ok entered spar stations flip the grade")
    print("all joint-register tests passed")
