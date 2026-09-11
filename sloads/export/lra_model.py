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
from typing import Callable, Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from ..derived_geometry import (
    carry_through,
    fuselage_centreline,
    fuselage_lra,
    sob_station,
)
from ..joints import JointName, wing_lra_point
from ..joints import joints as joint_register
from ..models import BalancedCaseResult, BalancedLoad, LraMeshInput, Project
from ..models.enums import GearCarrier
from ..modules.balance import build_balanced_cases
from ..modules.tail_span import ATTACH_STRIP_PAIR, build_tail_span, htail_attachment
from ..modules.wing_geometry import require_integrable_planform
from ..picks import extreme
from ..tail_geometry import HTAIL, VTAIL, h_tail_waterline, resolve_tail_planform
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

Vec3 = Tuple[float, float, float]

_TOL = 1e-9
#: **Float equality on a coordinate** (in) -- two numbers that came from the same
#: arithmetic and must compare equal despite association. This is *not* a
#: geometric tolerance: it answers "is this the same number", never "is this the
#: same station". The two questions shared this constant until design note 55
#: D-55.3, and using the epsilon for the geometric one is what let a joint land
#: 0.0769 in from a strip station and emit a sliver element (D-55.2).
_COINCIDENT_TOL = 1e-6

#: **The shortest element the mesh may emit**, as a fraction of the member's own
#: target element length (note 56 D-56.4). It replaces ``JOINT_MERGE_FRACTION``,
#: and the thing it guards is not the thing that one guarded.
#:
#: Note 55's sliver came from *inserting* a joint into a mesh fixed by the load
#: model: the joint landed 0.0769 in from a strip station on ``cessna_210``
#: (1.07 % of a strip, a 1638:1 element ratio) and 0.1266 in on ``baron_58``,
#: and the fix was a merge band wide enough to absorb the station. Under D-56.4
#: nothing is inserted: the owned points come **first** and the equally spaced
#: grids are laid strictly *between* consecutive owned points, so an
#: insertion-induced sliver is not a thing that can happen. That is the class
#: the note says dies structurally, and it does.
#:
#: What survives is narrower and is a **data** condition rather than an sloads
#: defect: two *owned* locations -- two joints, a joint and a gear trunnion --
#: genuinely close together on one member. Both must be nodes (dropping either
#: drops a load path), so the element between them is as short as the airplane
#: says it is, and the honest answer is to refuse and name them rather than to
#: merge one away.
#:
#: **1:200 of the member's target element length**, and the two numbers it sits
#: between are measured rather than chosen. The one observed singular solve
#: (note 55, ``cessna_210``'s h-tail attachment) was at **1:1638**. The tightest
#: *legitimate* element across the four shipped fixtures at three mesh
#: settings -- default, and counts coarse and fine enough to be unreasonable --
#: is **1:38**, on ``ga6_normal``'s fuselage, where two body ties really are
#: close together. So this is an order of magnitude clear of the worst honest
#: geometry and still an order clear of the failure. Note 55's 5 % band is not
#: the precedent: that number decided whether to *merge* a station, which is a
#: question about strip scale, and this one decides whether to *refuse* a
#: solve, which is a question about stiffness contrast.
_MIN_ELEMENT_FRACTION = 0.005

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


class _Owned(NamedTuple):
    """A point the mesh must carry whatever the node count says.

    ``param`` is the member's own span coordinate (butt line on the wing and
    h-tail, waterline on the fin, fuselage station on the body). ``pos`` is the
    **owned** airplane location when an owner states one -- the joint register's
    location, never a second resolution of the same geometry (note 54 D-54.5);
    ``None`` means "put it on the member's own line", which is what a gear or
    engine station is.
    """

    param: float
    pos: Optional[Vec3] = None
    family: str = ""
    side: str = ""
    #: A named node's own id, when its family has a band of its own (the side
    #: of body is the standing case). ``None`` takes the member band's next id
    #: like any other grid.
    gid: Optional[int] = None


def _mesh_params(owned: Sequence[float], n: int) -> List[float]:
    """Every owned parameter, plus near-uniform grids laid **between** them.

    The D-56.4 mesh rule, and the reason note 55's sliver class cannot recur.
    The owned points divide the member into segments; the target element length
    is the member's length over ``n - 1``; each segment takes the whole number
    of elements closest to its own length and splits itself equally into them.
    So every grid is strictly interior to a segment and no grid can land beside
    an owned point -- which is what "joints are mesh points by construction"
    has to mean to be true.

    ``n`` is a **target**, not the node count: a member whose owned points are
    unevenly spread rounds segment by segment, so the total lands near ``n``
    rather than on it. Trading the exact count for the sliver is the right way
    round -- one is a number in a form, the other is a singular stiffness
    matrix.

    Decided from ``owned`` and ``n`` alone, both geometry, so the result cannot
    coincide with the load stations: that is the whole argument of note 56
    SS1.4, and it is what keeps the LM-1 transfer a real transfer in CI rather
    than an identity.
    """
    pts = sorted(owned)
    if len(pts) < 2:
        return list(pts)
    length = pts[-1] - pts[0]
    if length <= _COINCIDENT_TOL:
        return [pts[0]]
    h = length / (n - 1)
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        seg = b - a
        elements = max(1, round(seg / h))
        out += [a + seg * i / elements for i in range(1, elements)]
        out.append(b)
    return out


def _mesh_chain(owned: Sequence[_Owned], n: int, band,
                point_at: Callable[[float], Vec3],
                first_index: int = 0) -> List[LraNode]:
    """The member's nodes, in order: :func:`_mesh_params` turned into grids.

    Owned points keep their owner's position and identity tag; every other node
    is placed on the member's own line by ``point_at``. Ids come from ``band``
    in mesh order, so reading a deck top to bottom walks the beam.
    """
    by_param: Dict[float, _Owned] = {}
    for o in owned:
        match = next((p for p in by_param if abs(p - o.param) <= _COINCIDENT_TOL),
                     None)
        if match is None:
            by_param[o.param] = o
        elif by_param[match].pos is None and o.pos is not None:
            by_param[match] = o._replace(param=match)
    nodes: List[LraNode] = []
    for i, param in enumerate(_mesh_params(list(by_param), n)):
        own = next((by_param[p] for p in by_param
                    if abs(p - param) <= _COINCIDENT_TOL), None)
        pos = own.pos if own is not None and own.pos is not None else point_at(param)
        gid = own.gid if own is not None and own.gid is not None \
            else band.allocate(first_index + i)
        nodes.append(LraNode(gid, pos,
                             own.family if own else "", own.side if own else ""))
    return nodes


def _control_spans(spans: Mapping[str, Sequence], component: str) -> List:
    """The control-surface fittings on ``component`` -- hinges and actuators.

    One reader for the three places that need them: the two chains, which carry
    a node at each fitting's span (D-56.4), and the tie loop that hangs the
    fitting node off it. ``y`` is the surface's own span coordinate on both
    surfaces -- a butt line on the h-tail, a waterline above the root on the fin
    -- which is why one accessor serves both.
    """
    rs = spans.get(component) or []
    return list(rs[0].control_loads) if rs and rs[0].control_loads else []


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


def _refuse_unsolvable_skeleton(model: LraModel, mesh: LraMeshInput) -> None:
    """Refuse a skeleton this exporter knows a solver will not factor (D-55.5).

    The backstop, not the fix. It exists because the mission claim is that *the
    exported deck solves* -- so the one thing the exporter must never do is hand
    over a deck that dies in the user's solver with a diagnostic about the
    matrix rather than about the airplane. LM-4's contract: name the condition,
    because the fix is never a default.

    Two conditions:

    * **A chain of rigid elements.** A ``GRID`` that is an ``RBE2`` dependent
      and also an ``RBE2`` independent (or a dependent twice over) states
      ``a -> b -> c`` in rigid links, which sbeam refuses outright. This is
      ``ga6_normal``'s pre-D-55.1 state: the rear-spar post hung on the hub and
      carried both main-gear ties. Unchanged.

    * **A sliver element**, and this one changed its subject at note 56 D-56.4.
      It used to catch a joint *inserted* a percent of a strip from a load
      station -- an sloads defect, which the merge band existed to prevent.
      Nothing is inserted now: the owned points come first and the grids are
      laid strictly between them, so the only way two nodes land close together
      is that two **owned locations** are close together, which is a statement
      about the airplane. So the message changed too: it names the two points
      and asks for the geometry, rather than asking for a bug report. The floor
      is :data:`_MIN_ELEMENT_FRACTION` of the member's own target element
      length, which is the member's length over its node count -- a scale the
      mesh rule already has, rather than a strip width the beam no longer
      borrows. No shipped fixture comes near it.
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
    for family, nodes in model.members.items():
        if len(nodes) < 2:
            continue
        ends = [nodes[0].pos, nodes[-1].pos]
        length = _dist2(ends[0], ends[1]) ** 0.5
        member = "wing" if family == "wing" else family
        try:
            count = mesh.count(member)
        except ValueError:                  # pragma: no cover -- every chain maps
            continue
        floor = _MIN_ELEMENT_FRACTION * length / max(1, count - 1)
        if floor <= 0.0:
            continue
        for ga, gb in ((a, b) for (a, b), f in zip(model.cbars, model.cbar_families)
                       if f == family):
            element = _dist2(pos[ga], pos[gb]) ** 0.5
            if element < floor:
                raise LraRefusal(
                    f"the {family} chain carries a {element:.4f} in element "
                    f"between GRID {ga} and {gb}, below the {floor:.4f} in "
                    "floor (note 56 D-56.4). Two locations this model must "
                    "carry as separate nodes -- joints, attachments, the "
                    "member's own ends -- are that close together in the "
                    "entered geometry, and a sliver element conditions the "
                    "stiffness matrix to the point of a singular solve. "
                    "Check those two points, or raise the member's grid count "
                    "so the mesh either side of them is no finer than they are")


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
    mesh = project.lra_mesh or LraMeshInput()

    # ------------------------------------------------------------- wing chains
    # **The beam is meshed from the geometry, not from the load stations**
    # (note 56 D-56.4). Until this it *was* the load stations: the chain was the
    # WINGGEOM strips outboard of the side of body, which made the spanwise half
    # of the LM-1 transfer an identity on every fixture -- so the arbitrary-grid
    # routing a real user hits first was the least-tested path in the package,
    # and the strip mesh that the replication contract freezes at 20 was also,
    # silently, the structural model. They are separate now: the strips stay
    # oracle-locked and stop being the beam.
    wing_surf = geom.by_name("wing")
    if wing_surf is None:                   # pragma: no cover -- refused above
        raise LraRefusal("the LRA beam model needs a 'wing' geometry surface")
    require_integrable_planform(wing_surf)
    tip_y = max(pt[1] for pt in
                list(wing_surf.leading_edge) + list(wing_surf.trailing_edge))
    if tip_y <= sob.y + _COINCIDENT_TOL:
        raise LraRefusal(
            f"the side of body (BL {sob.y:.2f}) is at or outboard of the wing "
            f"tip (BL {tip_y:.2f}) -- there is no wing beam outboard of the "
            "joint to build")

    def _wing_point(y: float) -> Vec3:
        pt = wing_lra_point(project, y)
        if pt is None:                      # pragma: no cover -- guarded above
            raise LraRefusal("the wing beam's own line cannot be resolved")
        return pt

    j_sob = reg.one(JointName.WING_SOB, "R")
    # **The beam runs to the tip.** It used to stop at the outermost strip
    # *midpoint*, half a strip inboard of the surface -- 5.0 in on
    # ``ga6_normal`` (2.5 % of semispan), 12.1 in on ``atr42_100``. That is the
    # same omission design note 54 D-54.5 fixed for the fin, where it only got
    # fixed because the T-tail tie made the tip a joint; here there is no tie to
    # force the issue, which is exactly why it survived. A member's end is its
    # end (D-56.4).
    # The gear trunnions and the engine mount/hub are nodes of the model in
    # their own right, tied to the chain by the RBE2s below; they are not chain
    # stations, and D-56.4's "its gear / engine / hinge / actuator nodes" is
    # read that way here. The hinge and actuator nodes on the tail chains are
    # the exception and stay chain-inserted, because they already were.
    wing_owned = [_Owned(sob.y, j_sob.location, "lra-sob", "R", gid=sob_gid()),
                  _Owned(tip_y, None, "lra-wing-tip", "R")]
    right = _mesh_chain(wing_owned, mesh.count("wing"), _RIGHT_BAND, _wing_point)
    sob_r = right[0]
    left = [LraNode(_SOB_BAND.allocate(1) if n.family == "lra-sob"
                    else _LEFT_BAND.allocate(i),
                    _mirror(n.pos), n.family, "L" if n.side else "")
            for i, n in enumerate(right)]
    sob_l = left[0]
    hub_c = LraNode(_CENTRE_BAND.allocate(0), j_sob.counterpart,
                    "lra-centre", "C")
    model.nodes += right + left + [hub_c]
    model.add_chain(right, "wing")
    model.add_chain(left, "wing")
    model.rbe2s.append((hub_c.gid, "123456", [sob_r.gid, sob_l.gid],
                        "centre box: the two SOB nodes move with the hub -- "
                        "rigid, NOT a stiffness carry-through (step 14 / R-12)"))

    # -------------------------------------------------------------- fin chain
    # Both tail chains are meshed by D-56.4 exactly as the wing is: the surface's
    # own ends and its owned joints, with equally spaced grids laid between them.
    # They used to be the spanwise **load** stations, which is what made a joint
    # an *insertion* into someone else's mesh -- and an insertion landing a
    # percent of a strip from a station is note 55's sliver. Nothing is inserted
    # any more, so that class cannot arise (see _MIN_ELEMENT_FRACTION).
    try:
        spans = build_tail_span(project)
    except (ValueError, KeyError):
        spans = {}
    vtail_chain: List[LraNode] = []
    vtail_tip: Optional[LraNode] = None
    planform_v = resolve_tail_planform(project, VTAIL)
    if planform_v is not None and planform_v.span > 0.0:
        root_j = reg.one(JointName.VTAIL_ROOT)
        root_z = planform_v.root_z

        def _vtail_point(s_local: float) -> Vec3:
            return tail_station_to_airplane(
                planform_v.x_at(s_local, planform_v.ref_axis_pct),
                s_local, VTAIL, root_z)

        vtail_owned = [_Owned(0.0, root_j.location, "lra-fin-root", "C",
                            gid=_ATTACH_BAND.allocate(0))]
        if JointName.VTAIL_TIP_HTAIL in reg.names:
            vtail_owned.append(_Owned(planform_v.span,
                                    reg.one(JointName.VTAIL_TIP_HTAIL).location,
                                    "lra-fin-tip", "C",
                                    gid=_ATTACH_BAND.allocate(3)))
        else:
            vtail_owned.append(_Owned(planform_v.span, None, "lra-fin-tip", "C"))
        vtail_owned += [_Owned(cp.y) for cp in _control_spans(spans, VTAIL)]
        vtail_chain = _mesh_chain(vtail_owned, mesh.count("vtail"),
                                  _VTAIL_BAND, _vtail_point)
        root = vtail_chain[0]
        vtail_tip = next((n for n in vtail_chain if n.family == "lra-fin-tip"), None)
        if JointName.VTAIL_TIP_HTAIL not in reg.names:
            vtail_tip = None
        pending_body_ties.append((root.pos[0], [root.gid],
                                  "fin root -> fuselage (R-5)"))

    # ------------------------------------------------------------ h-tail chain
    htail_chain: List[LraNode] = []
    planform_h = resolve_tail_planform(project, HTAIL)
    if planform_h is not None and planform_h.span > 0.0:
        att = htail_attachment(project, planform_h)
        if att.basis == ATTACH_STRIP_PAIR:
            raise LraRefusal(_refusal_reason(reg, JointName.HTAIL_ATTACH))
        h_wl = h_tail_waterline(project, planform_v).z

        def _htail_point(y: float) -> Vec3:
            return tail_station_to_airplane(
                planform_h.x_at(abs(y), planform_h.ref_axis_pct),
                y, HTAIL, h_wl)

        # One chain across the whole span, tip to tip -- the h-tail is one beam
        # and the centreline is not an end of it. The count is per side, so the
        # target for the chain is twice it.
        span_h = planform_h.span
        h_owned = [_Owned(-span_h, None, "lra-htail-tip", "L"),
                   _Owned(span_h, None, "lra-htail-tip", "R")]
        if att.y == [0.0]:
            if vtail_tip is None:
                raise LraRefusal(
                    "T-tail layout with no fin beam -- the h-tail's only "
                    "support is the fin-tip joint, which does not exist "
                    "without a modelled vertical tail")
            h_owned.append(_Owned(
                0.0, reg.one(JointName.VTAIL_TIP_HTAIL).counterpart,
                "lra-attach", "C", gid=_ATTACH_BAND.allocate(1)))
        else:
            if att.assumed:
                notes.append(att.note)
            y_att = max(att.y)
            # Both ends of this tie come from the register, so the attachment
            # node and the body station it reacts against are one construction.
            j_r = reg.one(JointName.HTAIL_ATTACH, "R")
            j_l = reg.one(JointName.HTAIL_ATTACH, "L")
            h_owned += [_Owned(y_att, j_r.location, "lra-attach", "R",
                               gid=_ATTACH_BAND.allocate(1)),
                        _Owned(-y_att, j_l.location, "lra-attach", "L",
                               gid=_ATTACH_BAND.allocate(2))]
        h_owned += [_Owned(cp.y) for cp in _control_spans(spans, HTAIL)]
        htail_chain = _mesh_chain(h_owned, 2 * mesh.count("htail"),
                                  _HTAIL_BAND, _htail_point)
        if att.y == [0.0]:
            assert vtail_tip is not None    # refused above when it is missing
            joint = next(n for n in htail_chain if n.family == "lra-attach")
            model.rbe2s.append((vtail_tip.gid, "123456", [joint.gid],
                                "T-tail joint: h-tail centreline -> fin tip "
                                "(R-6; the fin deck's T7 lumped transfer is "
                                "NEVER applied to this model)"))
        else:
            att_r = next(n for n in htail_chain
                         if n.family == "lra-attach" and n.side == "R")
            att_l = next(n for n in htail_chain
                         if n.family == "lra-attach" and n.side == "L")
            pending_body_ties.append((j_r.counterpart[0], [att_l.gid, att_r.gid],
                                      "h-tail attachments -> fuselage; the "
                                      "span between them is placeholder-"
                                      "stiffness-dependent (R-12)"))

    # ------------------------------------- control-surface nodes (T6 discrete)
    # A hinge or actuator fitting is an owned point of its chain (above), so its
    # parent is a node **at** its span rather than the nearest station to it --
    # which is what LM-6 always meant and what the strip mesh could only
    # approximate.
    control_nodes: List[LraNode] = []
    for comp, chain, axis in ((HTAIL, htail_chain, 1), (VTAIL, vtail_chain, 2)):
        if not chain:
            continue
        for cp in _control_spans(spans, comp):
            family = "lra-hinge" if cp.kind == "hinge" else "lra-actuator"
            side = ("C" if comp == VTAIL or abs(cp.y) <= _COINCIDENT_TOL
                    else ("R" if cp.y > 0 else "L"))
            node = LraNode(_CONTROL_BAND.allocate(len(control_nodes)),
                           tail_station_to_airplane(cp.x, cp.y, comp, cp.z),
                           family, side)
            control_nodes.append(node)
            # Through the platform-stable owner: a fitting on the centreline
            # of a symmetric surface is equidistant from the two nodes either
            # side of it, and a bare min() would hand that tie to whichever way
            # the local libm rounded (CONVENTIONS.md SS7).
            here = node.pos[axis]

            def _gap(n: LraNode, a: int = axis, p: float = here) -> float:
                return abs(n.pos[a] - p)

            parent = extreme(chain, _gap, largest=False)
            model.rbe2s.append((parent.gid, "123456", [node.gid],
                                f"{comp} {cp.kind} node -> parent LRA (LM-6)"))
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
    # Meshed like every other member (D-56.4): the cantilever's two ends, every
    # station a tie lands on, and equally spaced grids between them. It used to
    # be the fuselage **outline's** section stations, which is not the load mesh
    # -- so this member was never the degenerate case note 56 SS1.4 is about --
    # but it made the beam's discretisation a consequence of how finely someone
    # drew the body, which is a different quantity from how finely they want it
    # analysed.
    outline = geom.fuselage
    if outline is None:  # fuselage_centreline() above has already refused in this case
        raise LraRefusal("no fuselage outline -- the fuselage LRA needs its sections")
    section_xs = [sec.x for sec in outline.sections]
    nose_x, tail_x = min(section_xs), max(section_xs)
    tie_xs = [x for x, _gids, _label in pending_body_ties
              if not ct.x_f + _COINCIDENT_TOL < x < ct.x_r - _COINCIDENT_TOL]

    def _body_point(x: float) -> Vec3:
        return (x, 0.0, lra.z_at(x))

    n_fus = mesh.count("fuselage")
    fwd_owned = [_Owned(min(nose_x, ct.x_f), None, "", ""),
                 _Owned(ct.x_f, None, "lra-post", "F")]
    fwd_owned += [_Owned(x) for x in tie_xs if x < ct.x_f - _COINCIDENT_TOL]
    aft_owned = [_Owned(ct.x_r, None, "lra-post", "A"),
                 _Owned(max(tail_x, ct.x_r), None, "", "")]
    aft_owned += [_Owned(x) for x in tie_xs if x > ct.x_r + _COINCIDENT_TOL]
    fus_fwd = _mesh_chain(fwd_owned, n_fus, _FUSELAGE_BAND, _body_point)
    fus_aft = _mesh_chain(aft_owned, n_fus, _FUSELAGE_BAND, _body_point,
                          first_index=len(fus_fwd))
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
    _refuse_unsolvable_skeleton(model, mesh)
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
