"""The LRA beam model -- the third deliverable (step 12, note 24 R-1).

Design notes: ``docs/40_history/24_lra_beam_model_review_note.md`` (the agreed
target, decisions BM-1..BM-5) and
``docs/40_history/27_lra_model_implementation_note.md`` (the implementation
decisions LM-1..LM-7 this module encodes). Conventions:
``docs/10_standard/CONVENTIONS.md``.

The suite's other two solver artifacts make different claims. The
per-component decks are oracle-backing free-body **views**; the assembled
balanced deck is the **equilibrium proof** -- nodes at load positions, no
elements, a determinate support whose reaction is the residual. This one is a
**structural idealization**: node lines on the load reference axes, ``CBAR``
chains, rigid ties for the posts / attachments / gear / engine, and the same
balanced cases' load sets **transferred onto the model's nodes** -- so its
value is the *internal* loads a solver recovers at the named nodes (the wing
side of body, the front/rear-spar posts, the fin root, the h-tail
attachments), which neither of the other artifacts can state.

Topology (implementation note 25 §3)
------------------------------------
Free-free like the balanced deck: one node clamped in six DOF (the forward
chain node nearest the front post -- see the support comment in
:func:`build_lra_model`), and the recovered reaction IS the case residual,
~0. The members:

* the **wing**, one chain per side, **starting at the side-of-body node**
  (note 24 R-3) and running to the tip on the surface's entered LRA;
* the **split fuselage** (decision BM-2): the forward body a cantilever ending
  at the front-spar post, the aft body + empennage a cantilever starting at
  the rear-spar post, on the section-centre line ``(x, 0, z_c(x))`` (R-4).
  No element spans the carry-through region -- each mid-body load routes to
  the nearer post, which is exactly the two-sums idealization;
* a rigid **centre-box hub** tying the two SOB nodes and the two posts to the
  wing LRA centreline point. Rigid (``RBE2``), deliberately not a ``CBAR``:
  a stiffness carry-through element is step 14's (R-12);
* the **fin**, root node at the fin-root waterline, rigid to the fuselage
  node inserted at that station (R-5);
* the **h-tail**, full span; its attachment pair rigid to the fuselage node
  at the h-tail station (conventional, basis-gated per BM-3), or its
  centreline node rigid to the **fin tip** (T-tail -- and the fin deck's T7
  lumped transfer is then never applied here, plan 11 §4);
* **gear** nodes at each leg's trunnion, rigid to the parent ``carrier``
  names (BM-4's gear half, the shipped G-2 field); **engine** hub + mount
  nodes rigid to the parent ``mounted_on`` names (R-9), the hub carrying the
  entered thrust ``FORCE`` (backlog #10,
  :func:`sloads.modules.balance.hub_thrust_set`) -- the rest of the
  power-effects set waits for design note 21;
* elevator/rudder **hinge/actuator** nodes where a surface runs discrete
  control mode, each rigid to an inserted parent-chain node (LM-6).

With placeholder ``PBAR``/``MAT1`` -- one identical pair per section family,
:data:`SECTION_FAMILIES`, so a sizing tool overwrites one card per family
(backlog Pri 7, step 14 descoped 2026-08-16) -- only the **determinate** paths
give honest internal loads -- the wing outboard of the SOB, the fin, the two fuselage
cantilever sums, the gear/engine links (note 24 R-12); the h-tail span between
its two rigid attachments is placeholder-stiffness-dependent and the header
says so.

Loads (LM-1/LM-7)
-----------------
Every ``BalancedLoad`` of every assembled case transfers to the nearest node
of the member its ``source`` names, carrying the exact lever-arm couple
``(p - n) x F`` -- single owner :func:`sloads.export.coordinates
.transfer_couple`. Wing strips inboard of the SOB therefore land **on** the
SOB node (R-3's collapse, by the same rule); the balanced strips sit on the
calc's 25 %-chord line, so the chordwise part of the couple *is* the torsion
transfer to the LRA. The transferred set has the identical resultant the
balanced deck's set has, which is the plan-07 acceptance gate.

Refusals (BM-3 / LM-4)
----------------------
The exporter raises, naming the missing datum, rather than building a beam on
a guess: an unset ``ref_axis_pct`` on an entered wing/tail surface (R-7c), no
resolvable side of body, no fuselage outline, no carry-through spar stations,
or an h-tail attachment on the ``ATTACH_STRIP_PAIR`` fallback. Geometry it
accepts **assumed** (section centres, spar fractions, the SOB fallback, an
outline-derived attachment) is stated in the deck header.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ..derived_geometry import (
    carry_through,
    fuselage_centreline,
    fuselage_lra,
    sob_station,
)
from ..joints import JointName
from ..joints import joints as joint_register
from ..models import BalancedCaseResult, BalancedLoad, Project
from ..models.enums import GearCarrier
from ..modules.balance import build_balanced_cases
from ..modules.net_loads import build_net_loads, loads_ref_axis_results
from ..modules.tail_span import ATTACH_STRIP_PAIR, build_tail_span, htail_attachment
from ..picks import extreme
from ..tail_geometry import HTAIL, VTAIL, resolve_tail_planform
from ..units import UnitSystem
from .balanced_deck import case_sids
from .bands import band
from .coordinates import SBEAM_CID, tail_station_to_airplane, to_force, to_grid, to_moment, to_pressure, transfer_couple
from .deck_format import (
    MAT1_E,
    MAT1_NU,
    PBAR_A,
    PBAR_I,
    PBAR_J,
    basis_sentence,
    comment,
    fmt,
    fmt3,
    solver_units,
    stamped,
)
from .roundtrip import _orientation
from .sbeam_bridge import wing_nodal_loads

Vec3 = Tuple[float, float, float]

_TOL = 1e-9
#: **Float equality on a coordinate** (in) -- two numbers that came from the same
#: arithmetic and must compare equal despite association. This is *not* a
#: geometric tolerance: it answers "is this the same number", never "is this the
#: same station". The two questions shared this constant until design note 55
#: D-55.3, and using the epsilon for the geometric one is what let a joint land
#: 0.0769 in from a strip station and emit a sliver element (D-55.2).
_COINCIDENT_TOL = 1e-6

#: **Is this the same station?** -- the geometric question, as a fraction of the
#: chain's own strip width ``ds`` (design note 55 D-55.2, owner 2026-09-10). A
#: station within this of an inserted joint is absorbed *into* the joint: the
#: merged node keeps the station's ``gid`` and the **joint's** owned position,
#: so no element shorter than ``JOINT_MERGE_FRACTION * ds`` is ever emitted.
#:
#: 5 % separates the shipped data with a 25x margin either way: the two slivers
#: it absorbs sat at 1.07 % (``cessna_210``) and 1.33 % (``baron_58``) of a
#: strip, and the nearest legitimate neighbour it must *not* absorb is
#: ``ga6_normal``'s at 33.66 %. The note records that anything from ~3 % to
#: ~25 % would separate them, so this is a judgement inside a wide band, not a
#: fitted threshold.
JOINT_MERGE_FRACTION = 0.05

#: Every grid this model writes comes from one of these -- the D-56.3 identity.
#: There is no id here the model did not allocate itself: before note 56 the
#: right wing chain took the wing stick deck's station ids, the tail chains the
#: spanwise decks', the control nodes the chordwise decks' and the gear nodes
#: the balanced deck's, so the deliverable's grids were defined by four
#: artifacts, three of which were not deliverables and two of which are now
#: deleted. ``wing_nodal_loads`` is still read below, for the station
#: **positions**; its ``gid`` is no longer this model's.
_RIGHT_BAND = band("lra-wing-right")
_LEFT_BAND = band("lra-wing-left")
_FUSELAGE_BAND = band("lra-fuselage")
_HTAIL_BAND = band("lra-htail")
_VTAIL_BAND = band("lra-vtail")
_SOB_BAND = band("lra-sob")
_CENTRE_BAND = band("lra-centre")
_ATTACH_BAND = band("lra-attach")
_CONTROL_BAND = band("lra-control")
_ENGINE_BAND = band("lra-engine")
_GEAR_BAND = band("lra-gear")
_CBAR_BAND = band("lra-cbar")
_RBE2_BAND = band("lra-rbe2")


def sob_gid() -> int:
    """GRID id of the wing side-of-body reporting node (right half-span).

    Lived in ``sbeam_bridge`` while that module owned every band; it has one
    consumer and this is it (note 56 D-56.3).
    """
    return _SOB_BAND.allocate(0)

#: The four section families of the LRA deck, in ``MID``/``PID`` order 1..4
#: (backlog Pri 7 -- step 14 descoped, 2026-08-17). Each family gets its own
#: ``MAT1``/``PBAR`` pair so a sizing tool overwrites **one card per family**;
#: the values are the same placeholder in all four (a different default per
#: family would be invented stiffness and would move the indeterminate paths
#: for no reason). The left wing shares the right's; the fwd/aft fuselage
#: chains share one. sloads takes **no** section input: section properties are
#: the sizing half's output (scope review 2026-08-16 §2.3), so the seam is the
#: deck, not the schema.
SECTION_FAMILIES: Tuple[str, ...] = ("wing", "fuselage", "htail", "vtail")


def section_id(family: str) -> int:
    """The ``MID`` == ``PID`` of ``family`` (1-based, in :data:`SECTION_FAMILIES` order)."""
    return SECTION_FAMILIES.index(family) + 1


class LraRefusal(ValueError):
    """The project lacks a datum the beam model must not guess (BM-3/LM-4)."""


@dataclass(frozen=True)
class LraNode:
    """One node of the skeleton: position, id, and its BM-5 identity tag."""
    gid: int
    pos: Vec3
    family: str = ""      # "" = untagged chain node
    side: str = ""        # R / L / C / F / A


@dataclass
class LraModel:
    """The built skeleton -- geometry and topology, no units, no loads.

    ``members`` is the LM-7 routing table: member key -> the nodes a load
    routed there may land on. ``all`` is every node (the fallback member).
    ``rbe2s`` are ``(gn, cm, [gm...], label)``; ``cbars`` are ``(ga, gb)`` in
    chain order (EIDs are assigned at emission from the ``lra-cbar`` band).
    """
    nodes: List[LraNode] = field(default_factory=list)
    cbars: List[Tuple[int, int]] = field(default_factory=list)
    #: The section family of each ``cbars`` entry, index-aligned (backlog Pri 7,
    #: descoped step 14): one of :data:`SECTION_FAMILIES`. Decides which of the
    #: four ``PBAR``/``MAT1`` pairs the element references.
    cbar_families: List[str] = field(default_factory=list)
    rbe2s: List[Tuple[int, str, List[int], str]] = field(default_factory=list)
    members: Dict[str, List[LraNode]] = field(default_factory=dict)
    support_gid: int = 0
    #: The header's honesty block: every assumed datum the model accepted.
    assumed_notes: List[str] = field(default_factory=list)

    def add_chain(self, nodes: Sequence[LraNode], family: str) -> None:
        """Register the ``CBAR`` chain through ``nodes`` under a section family."""
        if family not in SECTION_FAMILIES:
            raise ValueError(f"unknown LRA section family {family!r}")
        pairs = list(zip((n.gid for n in nodes), (n.gid for n in nodes[1:])))
        self.cbars += pairs
        self.cbar_families += [family] * len(pairs)

    def node(self, gid: int) -> LraNode:
        for n in self.nodes:
            if n.gid == gid:
                return n
        raise KeyError(gid)

    @property
    def dependent_gids(self) -> set:
        return {gm for _gn, _cm, gms, _lbl in self.rbe2s for gm in gms}


def _interp_chain(chain: List[Tuple[float, Vec3]], key: float) -> Vec3:
    """Position at coordinate ``key`` on a (coordinate, position) polyline --
    linearly interpolated between the bracketing entries, extrapolated from the
    end pair outside them (the fin root sits below the first strip midpoint)."""
    pts = sorted(chain, key=lambda cp: cp[0])
    if len(pts) == 1:
        return pts[0][1]
    if key <= pts[0][0]:
        (ka, pa), (kb, pb) = pts[0], pts[1]
    elif key >= pts[-1][0]:
        (ka, pa), (kb, pb) = pts[-2], pts[-1]
    else:
        (ka, pa), (kb, pb) = next(
            ((a, b) for a, b in zip(pts, pts[1:]) if a[0] <= key <= b[0]))
    t = 0.0 if kb == ka else (key - ka) / (kb - ka)
    return (pa[0] + t * (pb[0] - pa[0]), pa[1] + t * (pb[1] - pa[1]),
            pa[2] + t * (pb[2] - pa[2]))


def _mirror(pos: Vec3) -> Vec3:
    return (pos[0], -pos[1], pos[2])


def _dist2(a: Vec3, b: Vec3) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def nearest_node(nodes: Sequence["LraNode"], p: Vec3) -> "LraNode":
    """The node of ``nodes`` closest to point ``p``, ties to the first in order.

    Equidistant nodes are the rule on a symmetric airplane, not the exception, so
    the pick goes through :func:`sloads.picks.extreme` -- otherwise which node
    carries a load (and therefore the deck's bytes) could depend on the platform
    (review 2026-08-20 CR-B-1).
    """
    return extreme(nodes, lambda n: _dist2(n.pos, p), largest=False)


def _nearest_station(nodes: Sequence["LraNode"], x: float) -> "LraNode":
    """The node of ``nodes`` nearest fuselage station ``x`` (tie rule, CR-B-1)."""
    return extreme(nodes, lambda n: abs(n.pos[0] - x), largest=False)


def _insert_on_chain(chain: List[LraNode], key_fn, key: float, gid: int,
                     family: str, side: str,
                     pos: Optional[Vec3] = None,
                     merge_tol: float = _COINCIDENT_TOL) -> Tuple[List[LraNode], LraNode]:
    """``chain`` with a node at coordinate ``key`` -- a near station **absorbed**
    into the joint, or a new node inserted in order. Returns ``(chain, node)``.

    ``pos`` is the node's **owned** position, from the joint register: a joint
    is placed where its owner says, not where the chain's polyline happens to
    pass. Interpolating instead is what put the T-tail h-tail centreline node on
    the innermost *strip's* station rather than the centreline's -- 2.6 in out
    on ``concept_regional_jet``, on a swept surface where the two differ.
    Omitted (``None``) for a node with no joint of its own, which interpolates
    onto the chain's own line as before.

    ``merge_tol`` is how close an existing station has to be to count as **the
    same station** (design note 55 D-55.2/D-55.3). It is a *geometric* question
    and belongs on the scale of the chain's own strip width, which is why the
    caller passes :data:`JOINT_MERGE_FRACTION` of ``ds`` rather than letting it
    default to the float-equality epsilon. At the epsilon it never fires on a
    real near-miss, and a 1 %-of-a-strip miss becomes a **sliver element**:
    ``cessna_210``'s h-tail attachment landed 0.0769 in from a station (1.07 %
    of ``ds``) for a 1638:1 element-length ratio, on a deck already running
    within ~4x of sbeam's 1e15 singularity refusal -- that is the singular
    matrix #172 reported. ``baron_58`` was next at 0.1266 in / 1.33 %.

    **The station is absorbed into the joint, never the other way round.** The
    merged node keeps the station's ``gid`` (so every load routed there still
    lands on it, resultant-preserving under LM-1) and the **joint's** position.
    Snapping the joint onto the station instead would place an owned location by
    the mesh, which is note 54 D-54.5 inverted -- guarded by
    ``tests/test_joints.py``'s walk, which must keep passing unchanged.
    """
    for i, node in enumerate(chain):
        if abs(key_fn(node) - key) <= merge_tol:
            tagged = LraNode(node.gid, pos if pos is not None else node.pos,
                             family or node.family, side or node.side)
            chain[i] = tagged
            return chain, tagged
    line = [(key_fn(n), n.pos) for n in chain]
    node = LraNode(gid, pos if pos is not None else _interp_chain(line, key),
                   family, side)
    chain.append(node)
    chain.sort(key=key_fn)
    return chain, node


def _refuse_unsolvable_skeleton(model: LraModel,
                                merge_tols: Dict[str, float]) -> None:
    """Refuse a skeleton this exporter knows a solver will not factor (D-55.5).

    The backstop, not the fix: D-55.1 and D-55.2 are what keep these conditions
    from arising, and neither fires on any shipped fixture. It exists because
    the mission claim is that *the exported deck solves* -- so the one thing the
    exporter must never do is hand over a deck that dies in the user's solver
    with a diagnostic about the matrix rather than about the airplane. LM-4's
    contract: name the condition, because the fix is never a default.

    Two conditions, both exact -- neither invents a threshold:

    * **A chain of rigid elements.** A ``GRID`` that is an ``RBE2`` dependent
      and also an ``RBE2`` independent (or a dependent twice over) states
      ``a -> b -> c`` in rigid links, which sbeam refuses outright. This is
      ``ga6_normal``'s pre-D-55.1 state: the rear-spar post hung on the hub and
      carried both main-gear ties.
    * **A sliver element on a chain that has a strip width.** Every ``CBAR`` of
      the tail chains is at least that chain's own
      :data:`JOINT_MERGE_FRACTION` of ``ds`` -- which D-55.2 guarantees by
      absorbing near stations into the joint, so a violation here is an sloads
      defect rather than a data one. The wing and fuselage chains are
      deliberately **not** checked: the fuselage has no strip mesh at all (its
      spacing is entered stations plus inserted tie points, legitimately down
      to 0.087 of its own median on ``ga6_normal``), and the wing's SOB node is
      placed by position rather than inserted. A threshold invented for those
      would be a guess, and this function does not guess.
    """
    dependents: Dict[int, int] = {}
    independents = set()
    for gn, _cm, gms, _lbl in model.rbe2s:
        independents.add(gn)
        for g in gms:
            dependents[g] = dependents.get(g, 0) + 1
    for gid, count in sorted(dependents.items()):
        if count > 1 or gid in independents:
            node = model.node(gid)
            where = f"{node.family} {node.side}".strip() or f"GRID {gid}"
            raise LraRefusal(
                f"the node {where} (GRID {gid}) is rigidly tied on both sides "
                f"-- dependent in {count} RBE2(s) and independent in "
                f"{sum(1 for gn, _c, _g, _l in model.rbe2s if gn == gid)} -- "
                "which states a chain of rigid elements that sbeam refuses "
                "(design note 55 D-55.1). This is an sloads defect, not a "
                "data one: please report it with the project file")

    pos = {n.gid: n.pos for n in model.nodes}
    for (ga, gb), family in zip(model.cbars, model.cbar_families):
        floor = merge_tols.get(family)
        if not floor:
            continue                        # no strip width -- see the docstring
        length = _dist2(pos[ga], pos[gb]) ** 0.5
        if length < floor:
            raise LraRefusal(
                f"the {family} chain carries a {length:.4f} in element between "
                f"GRID {ga} and {gb}, below the {floor:.4f} in floor a joint "
                "insertion may leave (design note 55 D-55.2). A sliver element "
                "conditions the stiffness matrix to the point of a singular "
                "solve. This is an sloads defect, not a data one: please "
                "report it with the project file")


def _refusal_reason(reg, name: JointName) -> str:
    """The register's reason for refusing ``name`` -- the one wording (D-54.5).

    The register grades a joint it cannot place and names the missing datum;
    this exporter decides that the grade is fatal (BM-3/LM-4) and raises it. A
    second copy of the sentence here is the same drift in prose that the node
    positions had in numbers, so there is no fallback text: a refusal path the
    register does not know about is a bug, not a default.
    """
    refusal = reg.refusal(name)
    if refusal is None:                     # pragma: no cover -- see docstring
        raise LraRefusal(
            f"the LRA beam model cannot place the {name.value!r} joint and the "
            "joint register states no reason -- this is an sloads defect")
    return refusal.reason


def build_lra_model(project: Project) -> LraModel:
    """Build the skeleton (geometry + topology; no loads, no units).

    Raises :class:`LraRefusal` on every BM-3/LM-4 missing-datum condition --
    the error names the datum, because "enter it" is the fix, never a default.
    """
    geom = project.geometry
    if geom is None:
        raise LraRefusal("the LRA beam model needs Project.geometry")
    for name in ("wing", HTAIL, VTAIL):
        surf = geom.by_name(name)
        if surf is not None and surf.ref_axis_pct is None:
            raise LraRefusal(
                f"surface {name!r} has no entered loads reference axis "
                "(ref_axis_pct) -- a beam on an unstated axis is the silently-"
                "defaulted case this exporter refuses (note 24 R-7c). Enter "
                "the axis (typically 0.40) on the Geometry page")
    if geom.by_name("wing") is None:
        raise LraRefusal("the LRA beam model needs a 'wing' geometry surface")

    # **Where the joints are is their own owner** (design note 54 D-54.5). Every
    # node this function places at an inter-component tie is a *copy* of the
    # register's location rather than a second resolution of the same geometry:
    # before it, each end of each tie was resolved independently and the T-tail
    # R-6 arm was out by up to 5.8 in (22 %) with 6.9 in of z that does not
    # exist. The register reads the same owners this function already reads
    # (``sob_station``, ``carry_through``, ``fuselage_lra``,
    # ``htail_attachment``, the planforms), so nothing new is resolved here --
    # only the two spellings collapse into one.
    #
    # It is resolved before the missing-datum checks below so those can raise
    # the register's own refusal *reason*: which datum is missing is a fact
    # about the geometry, and a second copy of the sentence here is the same
    # drift in prose that the positions had in numbers. **Whether** a missing
    # joint is fatal stays the exporter's policy (BM-3) -- the register only
    # grades it.
    reg = joint_register(project)

    sob = sob_station(project)
    if sob is None:
        raise LraRefusal(_refusal_reason(reg, JointName.WING_SOB))
    centreline = fuselage_centreline(project)
    if centreline is None:
        raise LraRefusal(
            "no fuselage outline -- the fuselage beam's stations come from its "
            "sections and there are none to build them from")
    # **Where the body beam sits is its own owner** (2026-09-07): the entered
    # ``fuselage_mass.ref_waterline`` if the project states one, else the
    # section-centre line. Until this call the model ran the chain on the centre
    # line unconditionally and the entered waterline -- documented as this very
    # quantity -- was read by nothing, putting ``ga6_normal``'s body beam 23.5 in
    # from where its own project file says it is.
    lra = fuselage_lra(project)
    ct = carry_through(project)
    if ct is None:
        raise LraRefusal(_refusal_reason(reg, JointName.WING_SPAR_POST))

    model = LraModel()
    notes = model.assumed_notes
    if sob.assumed:
        notes.append(sob.note)
    if lra.note:
        notes.append(lra.note)
    # The spar-station sentence is the register's, so the grade the deliverable
    # prints and the grade the register carries are one wording (note 54 gate 4).
    # Appended here, where this block already builds the header's honesty list
    # in order -- the SOB and attachment sentences are appended by the branches
    # that own them, below.
    post_note = reg.by_name(JointName.WING_SPAR_POST)
    if post_note and post_note[0].assumed:
        notes.append(post_note[0].note)

    pending_body_ties: List[Tuple[float, List[int], str]] = []

    # ------------------------------------------------------------- wing chains
    net = build_net_loads(project)
    wing_results = loads_ref_axis_results(project, net.wing_net)
    base = wing_nodal_loads(wing_results[0])
    outboard = [nl for nl in base if nl.y > sob.y + _COINCIDENT_TOL]
    if not outboard:
        raise LraRefusal(
            f"the side of body (BL {sob.y:.2f}) is outboard of the last wing "
            "station -- there is no wing beam outboard of the joint to build")
    j_sob = reg.one(JointName.WING_SOB, "R")
    # The SOB node is the LRA's named node whether or not a load station falls
    # on it: before D-56.3 a coincident station handed over its own gid, which
    # is how a wing-stick id came to be tagged as an LRA named node.
    sob_r = LraNode(sob_gid(), j_sob.location, "lra-sob", "R")
    right = [sob_r] + [LraNode(_RIGHT_BAND.allocate(i), (nl.x, nl.y, nl.z))
                       for i, nl in enumerate(outboard)]
    sob_l = LraNode(_SOB_BAND.allocate(1), _mirror(sob_r.pos), "lra-sob", "L")
    left = [sob_l] + [LraNode(_LEFT_BAND.allocate(i),
                              _mirror((nl.x, nl.y, nl.z)))
                      for i, nl in enumerate(outboard)]
    hub_c = LraNode(_CENTRE_BAND.allocate(0), j_sob.counterpart,
                    "lra-centre", "C")
    model.nodes += right + left + [hub_c]
    model.add_chain(right, "wing")
    model.add_chain(left, "wing")
    model.rbe2s.append((hub_c.gid, "123456", [sob_r.gid, sob_l.gid],
                        "centre box: the two SOB nodes move with the hub -- "
                        "rigid, NOT a stiffness carry-through (step 14 / R-12)"))

    # -------------------------------------------------------------- fin chain
    try:
        spans = build_tail_span(project)
    except (ValueError, KeyError):
        spans = {}
    vtail_chain: List[LraNode] = []
    vtail_tip: Optional[LraNode] = None
    # The D-55.2 "same station" tolerances, bound before either chain branch:
    # a project with no fin (or no h-tail) skips that branch entirely, and the
    # control-node loop below reads both eagerly.
    h_merge = v_merge = _COINCIDENT_TOL
    vt = spans.get(VTAIL) or []
    planform_v = resolve_tail_planform(project, VTAIL) if vt else None
    if vt and planform_v is not None:  # spans exist only where the planform resolved
        stations = [LraNode(_VTAIL_BAND.allocate(i),
                            tail_station_to_airplane(st.x, st.y, VTAIL, st.z))
                    for i, st in enumerate(vt[0].stations)]
        root = LraNode(_ATTACH_BAND.allocate(0),
                       reg.one(JointName.VTAIL_ROOT).location,
                       "lra-fin-root", "C")
        vtail_chain = [root, *sorted(stations, key=lambda n: n.pos[2])]
        v_merge = JOINT_MERGE_FRACTION * (
            planform_v.span / max(2, planform_v.elements))
        # **The fin beam runs to the fin tip** (D-54.5). Until the register the
        # chain stopped at the outermost strip *midpoint*, half a strip below
        # the top of the surface, and the T-tail R-6 tie hung the horizontal
        # tail off that -- a 6.25/6.5/6.9 in vertical arm the airplane does not
        # have, and 2.4-5.8 in of x with it. The tip is a joint, so it is a
        # node.
        if JointName.VTAIL_TIP_HTAIL in reg.names:
            vtail_tip = LraNode(_ATTACH_BAND.allocate(3),
                                reg.one(JointName.VTAIL_TIP_HTAIL).location,
                                "lra-fin-tip", "C")
            vtail_chain.append(vtail_tip)
        pending_body_ties.append((root.pos[0], [root.gid],
                                  "fin root -> fuselage (R-5)"))

    # ------------------------------------------------------------ h-tail chain
    htail_chain: List[LraNode] = []
    ht = spans.get(HTAIL) or []
    attach_x: Optional[float] = None
    planform_h = resolve_tail_planform(project, HTAIL) if ht else None
    if ht and planform_h is not None:  # spans exist only where the planform resolved
        att = htail_attachment(project, planform_h)
        if att.basis == ATTACH_STRIP_PAIR:
            raise LraRefusal(_refusal_reason(reg, JointName.HTAIL_ATTACH))
        htail_chain = [LraNode(_HTAIL_BAND.allocate(i),
                               tail_station_to_airplane(st.x, st.y, HTAIL, st.z))
                       for i, st in enumerate(ht[0].stations)]
        htail_chain.sort(key=lambda n: n.pos[1])
        # The geometric "same station" tolerance for every joint inserted on
        # this chain (D-55.2): a fraction of the h-tail's own strip width.
        h_merge = JOINT_MERGE_FRACTION * (
            planform_h.span / max(2, planform_h.elements))
        if att.y == [0.0]:
            if vtail_tip is None:
                raise LraRefusal(
                    "T-tail layout with no fin beam -- the h-tail's only "
                    "support is the fin-tip joint, which does not exist "
                    "without a modelled vertical tail")
            htail_chain, joint = _insert_on_chain(
                htail_chain, lambda n: n.pos[1], 0.0,
                _ATTACH_BAND.allocate(1), "lra-attach", "C",
                pos=reg.one(JointName.VTAIL_TIP_HTAIL).counterpart,
                merge_tol=h_merge)
            model.rbe2s.append((vtail_tip.gid, "123456", [joint.gid],
                                "T-tail joint: h-tail centreline -> fin tip "
                                "(R-6; the fin deck's T7 lumped transfer is "
                                "NEVER applied to this model)"))
        else:
            if att.assumed:
                notes.append(att.note)
            y_att = max(att.y)
            # Both ends of this tie come from the register, so the attachment
            # node and the body station it reacts against are one construction:
            # interpolating the node off the strip chain while taking the body
            # station from the planform put them 0.36 in apart on ga6_normal.
            j_r = reg.one(JointName.HTAIL_ATTACH, "R")
            j_l = reg.one(JointName.HTAIL_ATTACH, "L")
            htail_chain, att_r = _insert_on_chain(
                htail_chain, lambda n: n.pos[1], y_att,
                _ATTACH_BAND.allocate(1), "lra-attach", "R", pos=j_r.location,
                merge_tol=h_merge)
            htail_chain, att_l = _insert_on_chain(
                htail_chain, lambda n: n.pos[1], -y_att,
                _ATTACH_BAND.allocate(2), "lra-attach", "L", pos=j_l.location,
                merge_tol=h_merge)
            attach_x = j_r.counterpart[0]
            pending_body_ties.append((attach_x, [att_l.gid, att_r.gid],
                                      "h-tail attachments -> fuselage; the "
                                      "span between them is placeholder-"
                                      "stiffness-dependent (R-12)"))

    # ------------------------------------- control-surface nodes (T6 discrete)
    control_nodes: List[LraNode] = []
    # The same "is this the same station" tolerance the attachment joints use
    # (D-55.2, swept per CLAUDE.md rule 4): a hinge or actuator fitting that
    # lands a fraction of a strip from an existing station would insert the
    # identical sliver element, on the identical chains.
    for comp, chain, key_fn, merge in (
            (HTAIL, htail_chain, lambda n: n.pos[1], h_merge),
            (VTAIL, vtail_chain, lambda n: n.pos[2], v_merge)):
        rs = spans.get(comp) or []
        if not rs or not rs[0].control_loads or not chain:
            continue
        for cp in rs[0].control_loads:
            family = "lra-hinge" if cp.kind == "hinge" else "lra-actuator"
            side = ("C" if comp == VTAIL or abs(cp.y) <= _COINCIDENT_TOL
                    else ("R" if cp.y > 0 else "L"))
            node = LraNode(_CONTROL_BAND.allocate(len(control_nodes)),
                           tail_station_to_airplane(cp.x, cp.y, comp, cp.z),
                           family, side)
            control_nodes.append(node)
            span_key = node.pos[1] if comp == HTAIL else node.pos[2]
            chain, parent = _insert_on_chain(  # noqa: PLW2901  -- the chain grows by the inserted node
                chain, key_fn, span_key,
                _ATTACH_BAND.allocate(4 + len(control_nodes)), "", "",
                merge_tol=merge)
            model.rbe2s.append((parent.gid, "123456", [node.gid],
                                f"{comp} {cp.kind} node -> parent LRA (LM-6)"))
    # Chains are registered only now: a control node's parent may have been
    # inserted into them, and a chain frozen earlier would orphan it.
    for chain, family in ((vtail_chain, "vtail"), (htail_chain, "htail")):
        model.nodes += chain
        model.add_chain(chain, family)
    model.nodes += control_nodes

    # ------------------------------------------------------------------- gear
    gear_nodes: List[LraNode] = []
    lg = geom.landing_gear
    if lg is not None:
        legs = [("main", lg.main_gear), ("nose", lg.nose_gear)]
        n_gear = 0
        gear_band = _GEAR_BAND
        for leg_name, leg in legs:
            ax, ay, az = leg.attach
            if not any(leg.attach):
                notes.append(
                    f"{leg_name} gear has no attach (trunnion) point entered "
                    "-- its node is omitted from this model")
                continue
            carrier = leg.carrier
            if carrier is None:
                carrier = (GearCarrier.WING if abs(ay) > sob.y
                           else GearCarrier.BODY)
                notes.append(
                    f"{leg_name} gear carrier ASSUMED {carrier.value} -- "
                    f"inferred from |attach BL {ay:.1f}| vs the side of body "
                    f"(BL {sob.y:.2f}). Enter carrier to state it (BM-4/G-2)")
            sides = ([("R", (ax, abs(ay), az)), ("L", (ax, -abs(ay), az))]
                     if abs(ay) > _COINCIDENT_TOL else [("C", (ax, 0.0, az))])
            for side, pos in sides:
                node = LraNode(gear_band.allocate(n_gear), pos,
                               "lra-gear", side)
                n_gear += 1
                gear_nodes.append(node)
                if carrier is GearCarrier.WING:
                    wing_chain = right if side != "L" else left
                    parent = nearest_node(wing_chain[1:] or wing_chain, pos)
                    model.rbe2s.append((parent.gid, "123456", [node.gid],
                                        f"{leg_name} gear ({side}) -> wing "
                                        "LRA (carrier WING, G-2)"))
                else:
                    pending_body_ties.append(
                        (ax, [node.gid],
                         f"{leg_name} gear ({side}) -> fuselage (carrier "
                         "BODY, G-2)"))
    model.nodes += gear_nodes

    # ---------------------------------------------------------------- engines
    engine_nodes: List[LraNode] = []
    from ..modules.engine import resolved_engines
    for i, eng in enumerate(resolved_engines(project) if project.engines else []):
        mount_pos: Tuple[float, float, float] = (eng.engine_cg[0], eng.engine_cg[1], eng.engine_cg[2])
        hub_pos: Tuple[float, float, float] = (eng.prop_cg[0], eng.prop_cg[1], eng.prop_cg[2])
        if not any(mount_pos) and not any(hub_pos):
            continue
        if not any(hub_pos):
            hub_pos = mount_pos
        mounted = eng.mounted_on
        if mounted is None:
            mounted = "wing" if abs(mount_pos[1]) > sob.y else "fuselage"
            notes.append(
                f"engine {i + 1} mounted_on ASSUMED {mounted!r} -- inferred "
                f"from |CG BL {mount_pos[1]:.1f}| vs the side of body (BL "
                f"{sob.y:.2f}). Enter mounted_on to state it (BM-4)")
        side = ("C" if abs(mount_pos[1]) <= _COINCIDENT_TOL
                else ("R" if mount_pos[1] > 0 else "L"))
        mount = LraNode(_ENGINE_BAND.allocate(2 * i), mount_pos,
                        "lra-engine-mount", side)
        hub = LraNode(_ENGINE_BAND.allocate(2 * i + 1), hub_pos,
                      "lra-engine-hub", side)
        engine_nodes += [mount, hub]
        deps = [mount.gid] + ([hub.gid] if hub.pos != mount.pos else [])
        if hub.pos == mount.pos:
            # Coincident hub and mount cannot both exist (zero-length tie adds
            # nothing); keep the mount, drop the hub node.
            engine_nodes.pop()
        if mounted == "wing":
            wing_chain = right if side != "L" else left
            parent = nearest_node(wing_chain[1:] or wing_chain, mount_pos)
            model.rbe2s.append((parent.gid, "123456", deps,
                                f"engine {i + 1} mount+hub -> wing LRA (R-9; "
                                "one RBE2, hub folded in -- sbeam refuses "
                                "chained rigid elements)"))
        else:
            pending_body_ties.append(
                (mount_pos[0], deps,
                 f"engine {i + 1} mount+hub -> fuselage (R-9)"))
    model.nodes += engine_nodes

    # -------------------------------------------------------- fuselage chains
    inserts: Dict[float, str] = {ct.x_f: "post-F", ct.x_r: "post-A"}
    for x, _gids, _label in pending_body_ties:
        if ct.x_f + _COINCIDENT_TOL < x < ct.x_r - _COINCIDENT_TOL:
            continue          # inside the carry-through: ties to the nearer post
        inserts.setdefault(x, "")
    outline = geom.fuselage
    if outline is None:  # fuselage_centreline() above has already refused in this case
        raise LraRefusal("no fuselage outline -- the fuselage LRA needs its sections")
    xs = sorted({round(s.x, 6) for s in outline.sections}
                | {round(x, 6) for x in inserts})
    fwd_xs = [x for x in xs if x < ct.x_f - _COINCIDENT_TOL] + [ct.x_f]
    aft_xs = [ct.x_r] + [x for x in xs if x > ct.x_r + _COINCIDENT_TOL]
    fus_fwd: List[LraNode] = []
    fus_aft: List[LraNode] = []
    n_fus = 0
    for chain, chain_xs in ((fus_fwd, fwd_xs), (fus_aft, aft_xs)):
        for x in chain_xs:
            family, side = "", ""
            if abs(x - ct.x_f) <= _COINCIDENT_TOL:
                family, side = "lra-post", "F"
            elif abs(x - ct.x_r) <= _COINCIDENT_TOL:
                family, side = "lra-post", "A"
            chain.append(LraNode(_FUSELAGE_BAND.allocate(n_fus),
                                 (x, 0.0, lra.z_at(x)), family, side))
            n_fus += 1
    model.nodes += fus_fwd + fus_aft
    model.add_chain(fus_fwd, "fuselage")
    model.add_chain(fus_aft, "fuselage")
    post_f = fus_fwd[-1]
    post_a = fus_aft[0]
    model.rbe2s.append((hub_c.gid, "123456", [post_f.gid],
                        "front-spar post (BM-2): the forward-body cantilever "
                        "hangs here; its sum is the last forward element's "
                        "end force"))
    model.rbe2s.append((hub_c.gid, "123456", [post_a.gid],
                        "rear-spar post (BM-2): the aft body + empennage "
                        "cantilever hangs here"))
    fus_all = fus_fwd + fus_aft
    # **A body tie never parents on a node that is already a dependent**
    # (design note 55 D-55.1). A GRID that is dependent in one RBE2 and
    # independent in another states a chain of rigid elements, which sbeam
    # refuses -- and `ga6_normal` had exactly one: the rear-spar post hangs on
    # the centre-box hub (BM-2) *and* carried both main-gear ties, because the
    # nearest body station to the trunnions is the post. The rule is not new;
    # the support picker below has always read "a forward node that is in no
    # RBE2", and the engine path folds its two ties into one for the same
    # reason (R-9). This is that rule, applied to the tie parents too.
    #
    # The gear keeps its **entered** carrier: it re-parents to a neighbouring
    # *fuselage* station, never to the wing centre-box hub, which would state a
    # load path the project did not enter (D-55.1's rejected alternative).
    for x, gids, label in pending_body_ties:
        free = [n for n in fus_all if n.gid not in model.dependent_gids]
        parent = _nearest_station(free or fus_all, x)
        model.rbe2s.append((parent.gid, "123456", gids, label))

    # ------------------------------------------------------- support + members
    # The clamp sits on the forward-chain node NEAREST the front post (that is
    # in no RBE2 -- roundtrip._supportable's reaction-recovery rule): free-free
    # proof either way, but clamping beside the wing keeps every flexible path
    # short, and the difference is not cosmetic -- clamped at the nose the SI
    # (mm) stiffness conditions at 1.6e15, over sbeam's 1e15 singularity
    # refusal; here it is 2.8e14. Measured on atr42_100, 2026-08-16.
    # **The support node is in NO RBE2 -- neither end** (design note 55 D-55.6).
    # ``roundtrip._supportable`` has always applied both exclusions and records
    # why the second is load-bearing: sbeam's ``recover_reactions`` subtracts
    # the raw applied vector at the constrained DOFs, so a load a rigid element
    # transfers *onto* a constrained node is never subtracted and comes back out
    # as reaction. This picker implemented only the first, and the rule's two
    # halves lived in two files -- the same shape as D-55.1's tie-parent defect,
    # one file down. Measured here: with the support on a gear-tie parent,
    # ``ga6_normal`` recovered 569.49 lb of Fx against an applied set closing to
    # 0.0002 lb, and ``baron_58`` the same through its nose-gear tie.
    # Among the untied nodes, clamp the one **nearest the carry-through**. That
    # is the intent the old `reversed(fus_fwd)` encoded positionally -- "clamped
    # beside the wing keeps every flexible path short" -- and with D-55.6
    # excluding more candidates the positional form walked the clamp toward the
    # nose, which is the case that comment warns about: `ga6_normal`'s SI (mm)
    # deck conditioned past sbeam's 1e15 refusal and went singular. Stated as
    # the distance it was always a proxy for, the clamp stays beside the wing
    # and both chains are eligible. Ties go through `extreme` (CR-B-1), so the
    # deck's bytes cannot depend on the platform.
    tied = model.dependent_gids | {gn for gn, _cm, _gms, _lbl in model.rbe2s}
    support = next((n for n in reversed(fus_fwd) if n.gid not in tied), None)
    if support is None:
        support = next((n for n in fus_aft if n.gid not in tied), None)
    if support is None:
        raise LraRefusal(
            "every fuselage node is tied into an RBE2, so there is nowhere to "
            "put a support whose recovered reaction can be trusted (design "
            "note 55 D-55.6). This is an sloads defect, not a data one: please "
            "report it with the project file")
    model.support_gid = support.gid

    model.members = {
        "wing-R": right,
        "wing-L": left,
        "fuselage": fus_all,
        "all": list(model.nodes),
    }
    if htail_chain:
        model.members["htail"] = htail_chain
    if vtail_chain:
        model.members["vtail"] = vtail_chain
    if gear_nodes:
        model.members["gear"] = gear_nodes
    if engine_nodes:
        model.members["engine"] = engine_nodes
    _refuse_unsolvable_skeleton(model, {"htail": h_merge, "vtail": v_merge})
    return model


# --------------------------------------------------------------------------- #
# Load routing (LM-7) + transfer (LM-1)
# --------------------------------------------------------------------------- #
def _member_key(load: BalancedLoad, members: Dict[str, List[LraNode]]) -> str:
    """Which member a balanced load's ``source`` routes it to.

    ``ground-lift`` is the wing spanwise shape, so it rides with the wing
    strips. ``engine-thrust`` routes to the engine member, where the nearest
    node is the hub the load was built at -- so the transfer couple is exactly
    zero and the thrust lands on the hub node as an undisturbed ``FORCE``
    (backlog #10). It would land there anyway through the ``all`` fallback; the
    rule is explicit so a future nacelle stick cannot silently re-route it.

    Anything unrecognised -- the closure relief fields, the aileron
    couple -- goes to the nearest node in the whole skeleton: relief acts at
    each mass's own position, and nearest-node with the exact couple preserves
    the resultant wherever it lands. A member the model could not build falls
    back the same way rather than dropping the load; the invariant gate is on
    the full set.
    """
    s, side = load.source, load.side
    if s.startswith("wing-") or s == "ground-lift":
        key = {"R": "wing-R", "L": "wing-L"}.get(side, "all")
    elif s == "tail-air" or s.startswith("htail"):
        key = "htail"
    elif s.startswith("vtail"):
        key = "vtail"
    elif s.startswith("gear-"):
        key = "gear"
    elif s.startswith("engine-"):
        key = "engine"
    elif s.startswith("body") or s == "fuselage-cm":
        key = "fuselage"
    else:
        key = "all"
    return key if members.get(key) else "all"


def transferred_case_loads(case: BalancedCaseResult, model: LraModel
                           ) -> Dict[int, Tuple[List[float], List[float]]]:
    """``{gid: (F, M)}`` -- one case's loads on the model's nodes, **LIMIT**.

    Each :class:`~sloads.models.BalancedLoad` lands on the nearest node of the
    member its source names (LM-7) with the exact lever-arm couple
    ``(p - n) x F`` (LM-1, owner
    :func:`sloads.export.coordinates.transfer_couple`), so this set's resultant
    about any point is identical to the balanced case's -- the plan-07 gate.
    """
    acc: Dict[int, Tuple[List[float], List[float]]] = {}
    for load in case.loads:
        member = model.members[_member_key(load, model.members)]
        p = (load.x, load.y, load.z)
        node = nearest_node(member, p)
        f = (load.fx, load.fy, load.fz)
        cx, cy, cz = transfer_couple(p, node.pos, f)
        force, moment = acc.setdefault(node.gid, ([0.0] * 3, [0.0] * 3))
        force[0] += load.fx
        force[1] += load.fy
        force[2] += load.fz
        moment[0] += load.mx + cx
        moment[1] += load.my + cy
        moment[2] += load.mz + cz
    return acc


# --------------------------------------------------------------------------- #
# The deck
# --------------------------------------------------------------------------- #
#: The R-12 statement every LRA deck header carries -- one wording.
STIFFNESS_NOTE = (
    "placeholder PBAR/MAT1, one pair per section family (wing = MID/PID 1, "
    "fuselage 2, htail 3, vtail 4; identical values): only the DETERMINATE "
    "paths give honest internal loads -- the wing outboard of each SOB node, "
    "the fin, the two split-fuselage cantilever sums at the posts, and the "
    "rigid gear/engine links. The h-tail span between its two attachments "
    "(conventional layout) is placeholder-stiffness-dependent. sloads takes "
    "no section input: overwrite the four cards with the sizing tool's own "
    "sections to make the indeterminate paths its (backlog Pri 7, step 14 "
    "descoped)."
)


def _case_header(case: BalancedCaseResult, sid: int) -> List[str]:
    label = case.case_ref.case_id if case.case_ref else case.label
    return comment(
        f"LRA model case {label} -- {case.label}"
        f"{('-' + case.hand) if case.hand else ''}, SID {sid}: the balanced "
        f"case's load set transferred onto the beam nodes. "
        f"{basis_sentence(case.safety_factor)} Identical resultant to the "
        "assembled deck's set by the transfer rule (note 25 LM-1).")


def lra_model_bdf(project: Project, *,
                  header_comment: str = "",
                  system: UnitSystem = UnitSystem.IMPERIAL,
                  cases: Sequence[BalancedCaseResult] = ()) -> str:
    """The LRA beam model as one solvable SOL 101 deck.

    ``cases`` defaults to :func:`~sloads.modules.balance.build_balanced_cases`
    -- the same set, ids and factors as the assembled balanced deck, expressed
    on this model. Raises :class:`LraRefusal` when the project lacks a datum
    the skeleton must not guess (see the module docstring), and ``ValueError``
    when no case assembles -- an empty model would read as a result.
    """
    model = build_lra_model(project)
    cases = list(cases) or build_balanced_cases(project, [])
    if not cases:
        raise ValueError(
            "no balanced case could be assembled -- the LRA model carries the "
            "assembled cases' load sets and has nothing to express")
    u = solver_units(system)
    sids = case_sids(cases)

    head: List[str] = ["SOL 101", "$"]
    head += comment(
        "LRA BEAM MODEL (step 12) -- a structural idealization: node lines "
        "on the load reference axes, CBAR chains, rigid posts/attachments/"
        "gear/engine ties, and the assembled balanced cases' load sets "
        "transferred onto the nodes. Its value is the INTERNAL loads at the "
        "$ SLOADS-NODE tagged nodes; the assembled balanced deck remains the "
        "equilibrium proof and the per-component decks the oracle views "
        "(note 24 R-1).")
    head += comment(
        "grid line = LRA = the assumed elastic axis at the entered ref_axis "
        "percent chord; torsion is about it (note 24 R-7d).")
    head += comment("Stiffness: " + STIFFNESS_NOTE)
    for note in model.assumed_notes:
        head += comment("ASSUMED: " + note)
    head.append("$ ------------------------------------------------- CASE MAP")
    for sid, case in zip(sids, cases):
        entry = (f"SUBCASE {sid} = "
                 f"{case.case_ref.case_id if case.case_ref else '(no id)'}"
                 f" -- {case.label}{('-' + case.hand) if case.hand else ''}"
                 f" -- {case.cg} -- Nz {case.nz:g}")
        head += [f"$ {ln}" for ln in textwrap.wrap(entry, width=70,
                                                   subsequent_indent="    ")]
    head.append("$")
    for sid, case in zip(sids, cases):
        head += [
            f"SUBCASE {sid}",
            f"  LABEL = {case.case_ref.case_id if case.case_ref else case.label}",
            f"  TITLE = {case.label} on the LRA model (Nz={case.nz:g}, {case.cg})",
            "  SPC = 1",
            f"  LOAD = {sid}",
            "  DISPLACEMENT = ALL",
            "  SPCFORCE = ALL",
            "  FORCE = ALL",
            "$",
        ]
    head.append("BEGIN BULK")

    bulk: List[str] = [
        "$ ------------------------------------------------------------ NODES",
    ]
    bulk += comment(
        "Named nodes carry a '$ SLOADS-NODE <family> <side>' tag (decision "
        "BM-5) -- the identity contract an imported model is mapped by. "
        "Sides: R/L/C, plus F/A for the front/rear-spar posts.")
    bulk.append(f"$ Lengths in {u.length.label}.")
    bulk.append("$ GRID, GID, CP, X1, X2, X3")
    for node in model.nodes:
        if node.family:
            bulk.append(f"$ SLOADS-NODE {node.family} {node.side}")
        gx, gy, gz = to_grid(*node.pos, units=u)
        bulk.append(f"GRID, {node.gid}, , {fmt3(gx, gy, gz)}")

    e_mod = to_pressure(MAT1_E, u)
    area = PBAR_A * u.length.factor ** 2
    inertia = PBAR_I * u.length.factor ** 4
    torsion_j = PBAR_J * u.length.factor ** 4
    bulk += [
        "$ --------------------------------------------------------- MATERIAL",
        *comment(STIFFNESS_NOTE),
        f"$ E in {u.pressure.label}; A in {u.length.label}^2; "
        f"I, J in {u.length.label}^4.",
        "$ MAT1, MID, E, G, NU, RHO   /   PBAR, PID, MID, A, I1, I2, J",
    ]
    for family in SECTION_FAMILIES:
        sid_ = section_id(family)
        bulk += [
            f"$ SLOADS-SECTION {family}",
            f"MAT1, {sid_}, {fmt(e_mod)}, , {MAT1_NU}, 0.0",
            f"PBAR, {sid_}, {sid_}, {fmt(area)}, {fmt(inertia)}, "
            f"{fmt(inertia)}, {fmt(torsion_j)}",
        ]
    bulk += [
        "$ --------------------------------------------------------- ELEMENTS",
        "$ CBAR, EID, PID, GA, GB, X1, X2, X3   (PID = section family)",
    ]
    positions = {n.gid: n.pos for n in model.nodes}
    for i, ((ga, gb), family) in enumerate(zip(model.cbars, model.cbar_families)):
        vx, vy, vz = _orientation(positions[ga], positions[gb])
        bulk.append(f"CBAR, {_CBAR_BAND.allocate(i)}, {section_id(family)}, "
                    f"{ga}, {gb}, {vx}, {vy}, {vz}")
    bulk.append("$ RBE2, EID, GN, CM, GM...  (rigid ties, production band)")
    for i, (gn, cm, gms, label) in enumerate(model.rbe2s):
        bulk += comment(label)
        bulk.append(f"RBE2, {_RBE2_BAND.allocate(i)}, {gn}, {cm}, "
                    + ", ".join(str(g) for g in gms))
    bulk += [
        "$ ------------------------------------------------------- CONSTRAINTS",
        *comment(
            "Determinate, free-free proof: one node, six DOF, on the forward "
            "fuselage chain node nearest the front post (touched by no rigid "
            "element) -- the recovered reaction IS the case residual stated "
            "by the balanced deck, ~0."),
        f"SPC1, 1, 123456, {model.support_gid}",
        "$ ------------------------------------------------------------ LOADS",
    ]
    for sid, case in zip(sids, cases):
        bulk += ["$", *_case_header(case, sid)]
        loads = transferred_case_loads(case, model)
        for gid in sorted(loads):
            force, moment = loads[gid]
            fx, fy, fz = to_force(force[0], force[1], force[2], u)
            if max(abs(v) for v in force) > _TOL:
                bulk.append(f"FORCE, {sid}, {gid}, {SBEAM_CID}, 1.0, "
                            f"{fmt3(fx, fy, fz)}")
            mx, my, mz = to_moment(moment[0], moment[1], moment[2], u)
            if max(abs(v) for v in moment) > _TOL:
                bulk.append(f"MOMENT, {sid}, {gid}, {SBEAM_CID}, 1.0, "
                            f"{fmt3(mx, my, mz)}")

    return stamped(header_comment, "\n".join(head + bulk + ["ENDDATA"]) + "\n")


def write_lra_model_bdf(project: Project, path: str, *,
                        header_comment: str = "",
                        system: UnitSystem = UnitSystem.IMPERIAL,
                        cases: Sequence[BalancedCaseResult] = ()) -> None:
    # Rendered before the file opens: this exporter legitimately refuses (an
    # LraRefusal names the missing datum), and a failed export must leave no
    # partial artifact.
    text = lra_model_bdf(project, header_comment=header_comment, system=system,
                         cases=cases)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


__all__ = [
    "SECTION_FAMILIES",
    "STIFFNESS_NOTE",
    "LraModel",
    "LraNode",
    "LraRefusal",
    "build_lra_model",
    "lra_model_bdf",
    "section_id",
    "transferred_case_loads",
    "write_lra_model_bdf",
]
