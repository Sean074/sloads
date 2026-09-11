"""The joint register -- where two components meet, and on whose authority.

Design note: ``docs/30_future/54_geometry_joint_model_note.md`` (D-54.5, with
D-54.7's drift guard). Conventions: ``docs/10_standard/CONVENTIONS.md`` §7.

Every inter-component transfer in the LRA beam model is an ``RBE2``, and a rigid
tie across a real offset carries the exact lever-arm couple -- so the *mechanism*
is statically exact by construction. What was never owned is the **node
positions**: each end of each tie was resolved independently, from separately
entered data, by whichever expression was nearest to hand. Two spellings of one
formula, and nothing compared them.

What that cost, measured on the shipped fixtures before this module existed::

    T-tail R-6 tie      exported arm        the owners' arm      error
    atr42_100           dx -23.228, dz 6.250   dx -25.600, dz 0   2.4 in, 6.2 in
    dhc8_dash8          dx -23.753, dz 6.500   dx -26.100, dz 0   2.4 in, 6.5 in
    concept_regional_jet dx -20.876, dz 6.900  dx -26.680, dz 0   5.8 in (-22 %)

The fin beam stopped half a strip short of its own top (``vtail_chain[-1]`` is
the outermost strip *midpoint*, not the tip), which is the whole of the spurious
``dz``; and the h-tail centreline node was interpolated off the strip-station
polyline at ``y = 0``, which on a swept surface answers with the innermost
strip's station rather than the centreline's. The conventional attachment pair
had the same defect in miniature -- the attach node interpolated off the chain
while the body-side station came from the planform owner, 0.36 in apart on
``ga6_normal``. Note 51's T-tail transfer moments are computed across exactly
these arms, so nothing there can be certified until they are owned.

One statement covers the class (note 54 §1): **a joint between two components
must be a first-class geometric entity -- an owned location, stated offset arms,
a DOF set and a basis -- not an emergent coincidence of separately-entered
surfaces.** This module is that entity. It resolves nothing itself: every
location is read from the owner that already resolves it (``tail_geometry``'s
fin root and h-tail waterline, ``tail_span.htail_attachment``,
``derived_geometry``'s side of body, carry-through and fuselage LRA), and the
ASSUMED/entered grade, the basis string and the in-band note are copied from
that owner **verbatim** -- the register re-states nothing and re-derives nothing.

``export/lra_model`` places its nodes by reading this register, so the exported
tie positions are *copies* of one owner rather than a second measurement; the
drift guard (``tests/test_joints.py``) walks every joint on every fixture
through the emitted deck text and asserts exactly that, at ``rel_tol=1e-9``.

Layering: this is calc-side and imports no ``export`` module -- ``lra_model``
importing ``joints`` is the correct direction, and it is why the register names
its nodes by their BM-5 ``$ SLOADS-NODE`` family rather than by GID.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from .derived_geometry import (
    carry_through,
    fuselage_lra,
    require_integrable_planform,
    sob_station,
    wing_plane,
)
from .models import Project
from .modules.tail_span import ATTACH_STRIP_PAIR, ATTACH_VTAIL_TIP, htail_attachment
from .modules.wing_geometry import chord_fraction_x
from .tail_geometry import HTAIL, VTAIL, h_tail_waterline, resolve_tail_planform

Vec3 = Tuple[float, float, float]

#: The DOF set every production tie carries today. Stated rather than left
#: implicit in a string literal at the six call sites that used to spell it.
ALL_SIX = "123456"


class JointName(str, Enum):
    """The joints the airplane model has. ``str`` so a value is its own label."""

    VTAIL_ROOT = "vtail_root"              # fin -> fuselage LRA (R-5)
    VTAIL_TIP_HTAIL = "vtail_tip_htail"    # T-tail: h-tail centreline -> fin tip (R-6)
    HTAIL_ATTACH = "htail_attach"      # conventional: the pair -> fuselage LRA
    WING_SOB = "wing_sob"              # side-of-body -> centre-box hub (BM-2)
    WING_SPAR_POST = "wing_spar_post"  # front/rear post -> centre-box hub (BM-2)


#: ``basis`` values this module mints itself, where the owner it reads has a
#: provenance flag but no basis string of its own (``CarryThrough``). Deriving
#: the string here rather than widening the NamedTuple keeps every existing
#: ``carry_through`` consumer untouched.
SPAR_ENTERED = "entered spar stations"
SPAR_ESTIMATOR = "%-of-root-chord estimator -- assumed"


@dataclass(frozen=True)
class Joint:
    """One joint: an owned location, a stated arm, a DOF set and a basis.

    ``location`` is always a full airplane point, never a station scalar -- the
    two joints that were wrong were wrong in a coordinate a scalar form would
    have dropped (the T-tail tip joint's spurious 6.25 in of ``z``). ``arm`` is
    the vector from :attr:`location` to the counterpart node the tie reaches,
    in airplane axes, and ``to`` names that counterpart in words: exactly one
    arm per joint is total, because every production ``RBE2`` here is one
    (independent, dependent) pair.

    A **pair of fittings is two joints, not one joint with a list** -- the
    h-tail attachments, the two SOB nodes and the two spar posts are each two
    physical points with two GIDs already. Flattening them makes the register a
    plain tuple of rows, which is what lets the drift guard walk it with no
    per-kind branch (a ``Union`` of per-joint types would put ``isinstance``
    into the guard, which is the per-defect shape D-54.7 rejects).

    ``basis``, ``assumed`` and ``note`` are copied verbatim from the resolving
    owner. ``node_family``/``side`` are the BM-5 ``$ SLOADS-NODE`` identity the
    deck tags the node with -- not a GID, which is export-side.
    """

    name: JointName
    side: str            # C / R / L / F / A -- BM-5's own vocabulary
    location: Vec3       # airplane coordinates, in
    arm: Vec3            # location -> the counterpart node, in
    to: str              # what the arm reaches, in words
    node_family: str     # the BM-5 node tag this joint is exported as
    dof: str             # the RBE2 CM string
    basis: str           # copied from the resolving owner
    assumed: bool        # copied from the resolving owner
    note: str = ""       # copied from the resolving owner

    @property
    def counterpart(self) -> Vec3:
        """Where the other end of the tie sits (``location + arm``)."""
        return (self.location[0] + self.arm[0],
                self.location[1] + self.arm[1],
                self.location[2] + self.arm[2])


@dataclass(frozen=True)
class Refusal:
    """A joint this project states no geometry for, and the datum that is missing.

    Carried as a grade rather than raised, because this module is read by
    consumers that must not refuse -- the report's provenance sentences today,
    ``body_loads``' T-tail entry point in phase 2. Whether a missing joint is
    fatal is the *exporter's* policy (BM-3), so ``lra_model`` keeps raising
    ``LraRefusal``, reading its reason from here so the two cannot drift.
    """

    name: JointName
    reason: str


@dataclass(frozen=True)
class JointRegister:
    """Every joint this project resolves, and every one it refuses."""

    joints: Tuple[Joint, ...] = ()
    refusals: Tuple[Refusal, ...] = ()

    def __iter__(self):
        return iter(self.joints)

    def __len__(self) -> int:
        return len(self.joints)

    @property
    def names(self) -> frozenset:
        """The :class:`JointName` set this project resolves."""
        return frozenset(j.name for j in self.joints)

    def by_name(self, name: JointName) -> Tuple[Joint, ...]:
        """Every joint of ``name``, in register order."""
        return tuple(j for j in self.joints if j.name == name)

    def one(self, name: JointName, side: str = "") -> Joint:
        """The single joint of ``name`` (and ``side``, when given).

        Raises ``KeyError`` rather than returning ``None``: a caller that asks
        for one joint has already decided the layout has it, and a silent
        ``None`` there is how a node ends up at the origin.
        """
        found = [j for j in self.by_name(name) if not side or j.side == side]
        if len(found) != 1:
            raise KeyError(
                f"{len(found)} joints match {name.value!r}"
                f"{f' side {side!r}' if side else ''} -- expected exactly one")
        return found[0]

    def refusal(self, name: JointName) -> Optional[Refusal]:
        """The refusal recorded for ``name``, if any."""
        return next((r for r in self.refusals if r.name == name), None)

def _wing_lra_point(project: Project, y: float,
                    surface_name: str = "wing") -> Optional[Vec3]:
    """The wing loads-reference-axis point at butt line ``y``.

    The same construction the delivered wing stations are on
    (``net_loads.to_loads_ref_axis`` -- one chord-fraction owner) lifted onto
    the wing plane (``derived_geometry.wing_plane``, note 33 DS-2), so the SOB
    and hub joints sit on the beam the loads are already stated along.
    """
    geom = project.geometry
    surf = geom.by_name(surface_name) if geom is not None else None
    if surf is None or not surf.leading_edge or not surf.trailing_edge:
        return None
    # Interpolating an edge means asking the precondition owner first (#71/PB-21)
    # -- a half-entered planform divides by a zero span-coordinate difference,
    # and a joint placed on that is worse than a joint refused.
    require_integrable_planform(surf)
    wrp, dihedral = wing_plane(project, surface_name)
    return (chord_fraction_x(surf.leading_edge, surf.trailing_edge, y,
                             surf.ref_axis),
            y,
            wrp + math.tan(math.radians(dihedral)) * y)


def _sub(a: Vec3, b: Vec3) -> Vec3:
    """``a - b``."""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _mirror(p: Vec3) -> Vec3:
    """``p`` reflected across the airplane's plane of symmetry."""
    return (p[0], -p[1], p[2])


def _vtail_joints(project: Project, joints: List[Joint]) -> None:
    """The fin root, and -- on a T-tail -- the fin-tip joint the h-tail sits on.

    No refusal leg: a project with no vertical tail simply has no fin joints,
    which is absence rather than a missing datum -- ``lra_model`` builds such a
    model happily. Only a joint the geometry *implies* but cannot place is a
    refusal (the h-tail attachment's strip-pair fallback, below).
    """
    vtail = resolve_tail_planform(project, VTAIL)
    if vtail is None or vtail.span <= 0.0:
        return
    lra = fuselage_lra(project)
    x_root = vtail.x_at(0.0, vtail.ref_axis_pct)
    root: Vec3 = (x_root, 0.0, vtail.root_z)
    joints.append(Joint(
        name=JointName.VTAIL_ROOT, side="C", location=root,
        arm=(0.0, 0.0, lra.z_at(x_root) - vtail.root_z),
        to="fuselage-lra", node_family="lra-fin-root", dof=ALL_SIX,
        basis=vtail.root_z_basis, assumed=vtail.root_z_assumed,
        note="; ".join(vtail.notes)))

    htail = resolve_tail_planform(project, HTAIL)
    if htail is None or htail.span <= 0.0:
        return
    att = htail_attachment(project, htail)
    if att.basis != ATTACH_VTAIL_TIP:
        return
    # The T-tail tip joint. Both ends come from the SAME owner evaluated at the
    # two surfaces' own root/tip span stations -- which is the whole point: the
    # arm's z member is identically zero because ``h_tail_waterline``'s fin-tip
    # branch IS ``root_z + span``, so gate 2's first clause holds by
    # construction rather than by assertion.
    waterline = h_tail_waterline(project, vtail)
    tip: Vec3 = (vtail.x_at(vtail.span, vtail.ref_axis_pct), 0.0,
                 vtail.root_z + vtail.span)
    centreline: Vec3 = (htail.x_at(0.0, htail.ref_axis_pct), 0.0, waterline.z)
    joints.append(Joint(
        name=JointName.VTAIL_TIP_HTAIL, side="C", location=tip,
        arm=_sub(centreline, tip), to="htail-centreline",
        node_family="lra-fin-tip", dof=ALL_SIX,
        basis=waterline.basis, assumed=waterline.assumed, note=waterline.note))


def _htail_joints(project: Project, joints: List[Joint],
                  refusals: List[Refusal]) -> None:
    """The conventional attachment pair, reacted on the fuselage LRA."""
    htail = resolve_tail_planform(project, HTAIL)
    if htail is None or htail.span <= 0.0:
        return
    att = htail_attachment(project, htail)
    if att.basis == ATTACH_VTAIL_TIP:
        return                              # a T-tail joint, handled above
    if att.basis == ATTACH_STRIP_PAIR:
        refusals.append(Refusal(JointName.HTAIL_ATTACH, (
            "the h-tail attachment resolves to the innermost-strip-pair "
            "fallback, which is not a fuselage dimension at all (BM-3) -- "
            "enter the h-tail attachment butt line (sob_y_in) or a "
            "fuselage outline")))
        return
    lra = fuselage_lra(project)
    waterline = h_tail_waterline(project)
    # The body-side station is the h-tail's own LRA at the centreline -- the
    # station ``htail_attachment``'s outline branch measured the body width at,
    # so both ends of this tie are one construction (before D-54.5 the node was
    # interpolated off the strip chain and the body station was this, 0.36 in
    # apart on ga6_normal).
    x_body = htail.x_at(0.0, htail.ref_axis_pct)
    body: Vec3 = (x_body, 0.0, lra.z_at(x_body))
    for side, y in (("R", max(att.y)), ("L", -max(att.y))):
        here: Vec3 = (htail.x_at(abs(y), htail.ref_axis_pct), y, waterline.z)
        joints.append(Joint(
            name=JointName.HTAIL_ATTACH, side=side, location=here,
            arm=_sub(body, here), to="fuselage-lra",
            node_family="lra-attach", dof=ALL_SIX,
            basis=att.basis, assumed=att.assumed, note=att.note))


def _wing_joints(project: Project, joints: List[Joint],
                 refusals: List[Refusal]) -> None:
    """The side-of-body pair and the two spar posts, tied to the centre-box hub."""
    hub = _wing_lra_point(project, 0.0)
    if hub is None:
        return
    sob = sob_station(project)
    if sob is None:
        refusals.append(Refusal(JointName.WING_SOB, (
            "no side of body resolves (no entered sob_y_in and no fuselage "
            "width) -- the wing beam starts at the SOB (note 24 R-3) and this "
            "exporter will not invent a body (BM-1)")))
    else:
        right = _wing_lra_point(project, abs(sob.y)) or hub  # hub resolved => so does this
        for side, here in (("R", right), ("L", _mirror(right))):
            # The left joint is the RIGHT one mirrored, never a second
            # evaluation at -y: the chord-fraction owner extrapolates its
            # nearest segment, so asking it for a negative butt line answers
            # with the root polyline run backwards rather than with the other
            # wing (ga6_normal: 81.0 against the true 89.8). A symmetric
            # airplane's two joints are one geometry reflected -- which is what
            # the deck does, and this register may not spell it a second way.
            joints.append(Joint(
                name=JointName.WING_SOB, side=side, location=here,
                arm=_sub(hub, here), to="wing-hub",
                node_family="lra-sob", dof=ALL_SIX,
                basis=sob.basis, assumed=sob.assumed, note=sob.note))

    ct = carry_through(project)
    if ct is None:
        refusals.append(Refusal(JointName.WING_SPAR_POST, (
            "no wing carry-through resolves (degenerate root chord or spar "
            "stations) -- the split-fuselage posts sit at the front/rear-spar "
            "stations (BM-2) and cannot be placed")))
        return
    lra = fuselage_lra(project)
    # The ASSUMED sentence lives here, not at the deck writer, so the grade and
    # the wording the deliverable prints are one thing (gate 4).
    note = "" if not ct.assumed else (
        f"wing spar stations ASSUMED -- derived at "
        f"{ct.front_pct * 100.0:.0f}/{ct.rear_pct * 100.0:.0f} % of the root "
        f"chord, so the posts sit at fuselage stations "
        f"{ct.x_f:.1f}/{ct.x_r:.1f}. Enter front/rear_spar_x_in to state "
        "the joint")
    for side, x in (("F", ct.x_f), ("A", ct.x_r)):
        post: Vec3 = (x, 0.0, lra.z_at(x))
        joints.append(Joint(
            name=JointName.WING_SPAR_POST, side=side, location=post,
            arm=_sub(hub, post), to="wing-hub",
            node_family="lra-post", dof=ALL_SIX,
            basis=SPAR_ESTIMATOR if ct.assumed else SPAR_ENTERED,
            assumed=ct.assumed, note=note))


def joints(project: Project) -> JointRegister:
    """Every joint this project states, resolved once from the owners (D-54.5).

    Nothing here resolves a position of its own: the fin root comes from the
    L-1 owner through ``resolve_tail_planform``, the h-tail waterline from
    :func:`~sloads.tail_geometry.h_tail_waterline`, the attachment pair from
    ``tail_span.htail_attachment``, the side of body and carry-through from
    ``derived_geometry``, and every ``basis``/``assumed``/``note`` is a copy.

    **The layout branches by asking its owners, never by testing a flag.** The
    fin joints exist iff a fin planform resolves; the tip joint exists iff
    ``htail_attachment`` returns the fin-tip basis -- the discriminator note 24
    BM-3 already tells consumers to gate on -- and the attachment pair exists
    iff it returns anything else. So a T-tail register has no ``htail_attach``
    and a conventional one has no ``fin_tip_htail`` *by construction*, and the
    guard asserts that partition rather than this function enforcing it.
    """
    out: List[Joint] = []
    refusals: List[Refusal] = []
    if project.geometry is None:
        return JointRegister((), (Refusal(
            JointName.WING_SOB, "the joint register needs Project.geometry"),))
    _wing_joints(project, out, refusals)
    _vtail_joints(project, out)
    _htail_joints(project, out, refusals)
    return JointRegister(tuple(out), tuple(refusals))


__all__ = [
    "ALL_SIX",
    "SPAR_ENTERED",
    "SPAR_ESTIMATOR",
    "Joint",
    "JointName",
    "JointRegister",
    "Refusal",
    "Vec3",
    "joints",
]
