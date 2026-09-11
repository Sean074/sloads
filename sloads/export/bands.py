"""The single owner of every exported id band -- GID, EID and SID.

Why this module exists
----------------------
Bulk-data ids are a shared namespace across deck families that were written
months apart. Two decks that number their nodes from the same base do not fail:
they *splice*, and an assembled airframe then sums two unrelated loads on one
node. That is the D-19 failure class -- a deck that parses cleanly and is
silently wrong -- applied to ids instead of units.

It happened. The balanced deck (plan 11) allocated ``4001+`` for its right wing
while the spanwise h-tail deck already owned ``4001-4499``; both files' own
docstrings claimed disjointness, and both guard tests hand-enumerated the bands
they knew about, so neither saw it (review 2026-08-10 **F-C1**/**F-G3**). The
structural fix is ``CLAUDE.md`` practice 3: **one owner plus a drift guard**, not
prose. Every band is declared here, every allocator goes through
:meth:`Band.allocate`, and :mod:`tests.test_bands` proves the registry is both
internally disjoint and exhaustive -- a base constant defined anywhere in
``sloads/export`` that is not a registered band's ``start`` fails the guard, so a
new deck family cannot re-open the blind spot.

The map
-------
::

    GID   1-1000    applied-load model, wing stations
       1001-1500    applied-load model, fuselage mass stations + tail air load
       1501-2000    applied-load model, wing carry-through / correction nodes
       4001-4500    applied-load model, spanwise h-tail stations
       4501-5000    applied-load model, spanwise v-tail stations
       5001-5300    applied-load model, elevator hinge / actuator nodes
       5301-5600    applied-load model, rudder hinge / actuator nodes
       6001-6200    balanced deck, right wing
       6201-6400    balanced deck, left wing
       6401-7000    balanced deck, centreline
      10001-10100   balanced deck, gear reference points

      20001-30999   **the LRA model's own run** (note 56 D-56.3). One 999-wide
                    sub-band per node family, so the family is readable off the
                    id: family index = gid // 1000 - 20.

      20001-20999    0  right wing chain     25001-25999   5  side of body
      21001-21999    1  left wing chain      26001-26999   6  wing centre box
      22001-22999    2  fuselage centreline  27001-27999   7  attachments
      23001-23999    3  h-tail chain         28001-28999   8  hinge / actuator
      24001-24999    4  fin chain            29001-29999   9  engine hub + mount
                                             30001-30999  10  gear attachments

    EID      1-1000  stick-model CBAR chain
          9001-9100  CONM2 baseline (always-aboard items)
          9101-9200  CONM2 discretionary overlay items
          9201-9300  CONM2 per-case ballast
          9501-9700  CONM2 per-case part-full consumable rows
         11001-11999  LRA model CBAR chains
         12001-12500  LRA model RBE2 ties (production, BM-5)
        900001-901000  round-trip harness RBE2 ties (test scaffolding)

    SID          1  SPC set (constraints, not loads)
           101-199  wing subcases          (case_ids.SUBCASE_BLOCK)
           201-299  h-tail subcases
           301-399  v-tail subcases
           401-499  fuselage subcases
           501-599  empennage subcases
           601-699  landing-gear subcases
          5001-5100  balanced-deck subcases, positional fallback (no CaseRef)
          5101-5699  balanced-deck subcases, symmetric  (case_ids.
          7101-7699  balanced-deck subcases, starboard   balanced_subcase_id:
          8101-8699  balanced-deck subcases, port        block + subcase_id)
          9301-9400  MASSSET sets, one per payload case
          9401-9500  GRAV sets, one per payload case

The ``CONM2`` EID bands are additionally kept clear of **GID** space, which
NASTRAN does not require: it makes every id in a spliced mass-plus-load deck
traceable to one owner by inspection. Bands say so for themselves
(:attr:`Band.clear_of_gids`); the stick model's ``CBAR`` chain declines, having
numbered 1..n alongside its own GRIDs since the first deck.

One deliberate mirror: the per-component subcase blocks are **allocated** by
:data:`sloads.case_ids.SUBCASE_BLOCK` -- and the balanced deck's per-hand blocks
by :data:`sloads.case_ids.BALANCED_HAND_BLOCK` -- which are calc-side and must
not import the export package. They are registered here so the disjointness
question has one place to be asked, and ``tests/test_bands.py`` pins the two
against each other so neither can move alone.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterator, Tuple


class IdKind(Enum):
    """The bulk-data namespace a band allocates in."""

    GID = "GID"
    EID = "EID"
    SID = "SID"


@dataclass(frozen=True)
class Band:
    """One contiguous, exclusively-owned run of ids.

    ``start`` is the first id and ``size`` the count, so the band owns
    ``start .. start + size - 1``. ``owner`` names the code that allocates from
    it -- the answer to "who put this id in my deck?" -- and ``note`` carries
    the reason the band exists where it does, when that is not obvious.
    """

    name: str
    kind: IdKind
    start: int
    size: int
    owner: str
    note: str = ""
    #: EID bands only: also keep clear of every GID band. NASTRAN does not
    #: require it -- elements and grids are separate namespaces -- but a deck
    #: that splices a ``CONM2`` set into a load deck is much easier to read (and
    #: to debug) when an id belongs to exactly one owner. The stick model's
    #: ``CBAR`` chain deliberately declines: it numbers 1..n alongside the
    #: GRIDs it connects, and always has.
    clear_of_gids: bool = False

    @property
    def end(self) -> int:
        """The last id in the band (inclusive)."""
        return self.start + self.size - 1

    def allocate(self, index: int) -> int:
        """The ``index``-th id in this band (0-based), or raise.

        Raising on overflow rather than returning ``start + index`` is the whole
        point: an unchecked allocator walks into the next band and the deck it
        writes is still valid bulk data.
        """
        if not 0 <= index < self.size:
            raise ValueError(
                f"{self.owner}: {self.kind.value} index {index} is outside the "
                f"{self.size}-id band '{self.name}' at {self.start}-{self.end}")
        return self.start + index

    def __contains__(self, value: int) -> bool:
        return self.start <= value <= self.end

    def ids(self) -> range:
        """Every id the band owns -- for the disjointness guard."""
        return range(self.start, self.end + 1)


def _band(*args, **kwargs) -> Band:
    return Band(*args, **kwargs)


#: Every band in the suite, in id order within each kind. **The registry.**
#: Adding a deck family means adding a row here first; nothing else may invent a
#: base constant (guarded by ``tests/test_bands.py``).
BANDS: Tuple[Band, ...] = (
    # ----------------------------------------------------------------- GIDs
    _band("wing-stick", IdKind.GID, 1, 1000, "sbeam_bridge.station_gid",
          "Station i takes 2 + i. GID 1 was the stick model's clamped root and "
          "is unallocated since note 56 D-56.2 deleted that deck. The hole "
          "stays: D-56.3 moved the LRA off this band but the applied-load "
          "model still allocates from it, and D-56.9 retires the band whole "
          "when that model re-states its gids at the LRA grids -- so closing "
          "the hole now would renumber every station twice for no gain."),
    _band("body-mass", IdKind.GID, 1001, 500, "sbeam_bridge.beam_station_gid",
          "Fuselage mass stations and the tail air load, nose->tail."),
    _band("body-reaction", IdKind.GID, 1501, 500, "sbeam_bridge.body_station_gids",
          "Wing carry-through / fallback correction nodes -- a separate band so "
          "inserting one never renumbers a mass station."),
    # 2001-2200 (tail chordwise) and 3001-4000 (control surface) were retired
    # by note 56 D-56.2 with the decks that allocated them: a chordwise tail
    # station and a control-surface chord station are points no delivered
    # artifact states any more. The ranges are left unregistered rather than
    # reused, so a band that reappears there is a new decision and not an
    # accidental collision with a published map. D-56.3 did not close them --
    # it moved the LRA out to 20001+ rather than backfilling here; the bands
    # still registered below this line belong to the applied-load model and go
    # with it at D-56.9.
    _band("tail-span-htail", IdKind.GID, 4001, 500, "sbeam_bridge.tail_span_gid"),
    _band("tail-span-vtail", IdKind.GID, 4501, 500, "sbeam_bridge.tail_span_gid"),
    _band("tail-control-htail", IdKind.GID, 5001, 300,
          "sbeam_bridge.tail_control_gid",
          "Elevator hinge and actuator nodes (plan 09 T6). Their own band rather "
          "than a continuation of the spanwise one: a hinge station is not a "
          "strip midpoint, so it is a different point, and adding hinges must "
          "never renumber the strips beside them."),
    _band("tail-control-vtail", IdKind.GID, 5301, 300,
          "sbeam_bridge.tail_control_gid", "Rudder hinge and actuator nodes."),
    _band("balanced-wing-right", IdKind.GID, 6001, 200, "balanced_deck.deck_nodes",
          "Left and right are separate runs so an antisymmetric case can load "
          "them differently without renumbering (plan 11 B7). The name records "
          "what first needed the split; the run carries every load on that side "
          "of the centreline, which from D-R8 includes the 23.427(a) h-tail "
          "strips."),
    _band("balanced-wing-left", IdKind.GID, 6201, 200, "balanced_deck.deck_nodes"),
    _band("balanced-centreline", IdKind.GID, 6401, 600, "balanced_deck.deck_nodes",
          "Fuselage masses, the tail air load, the lumped body Cm, and every "
          "closure point on the centreline."),
    # 7001-7880 held the LRA model's six families while it borrowed the rest of
    # its grids from decks that are now deleted. Note 56 D-56.3 moved the whole
    # model to its own run at 20001+; the range is left unregistered rather than
    # reused, for the same reason as 2001-4000 above.
    _band("balanced-gear", IdKind.GID, 10001, 100, "balanced_deck.deck_nodes",
          "The gear reference points a ground case's reactions are transferred "
          "to (decision G-2) -- at most one node per leg per side, since a "
          "trunnion is fixed to the airframe and does not move between "
          "attitudes. Its own band rather than a continuation of the three "
          "position runs so the node is identifiable BY ID: G-13's solver "
          "assertion compares the reaction sbeam recovers at this GID against "
          "the gear report's reference-point reaction, and a gear node sharing "
          "a run with wing strips could only be found by matching coordinates. "
          "Numbered clear of 6001-7000 so that range keeps its published "
          "meaning as the balanced deck's wing and centreline nodes."),

    # ------------------------------------------------- the LRA model's own run
    # Note 56 D-56.3. Every grid of the one shipped solver artifact comes from
    # here, so no id it writes is defined at a second position in any other
    # artifact -- which is the defect the note is named for: the deliverable
    # was taking its wing station ids straight from the wing stick deck's band
    # and its gear ids from the balanced deck's, so GID 7 named one point in
    # `wing_loads.bdf` and another in `lra_model.bdf`.
    #
    # One 999-wide sub-band per node family, contiguous and in a fixed order,
    # so `gid // 1000 - 20` is the family index and an id read off a deck or a
    # solver echo says what kind of point it is without a lookup. 999 rather
    # than 1000 is what keeps that arithmetic true at the last id of each band.
    # The width is deliberate headroom for D-56.4: the mesh becomes `n` equally
    # spaced grids per member with `n` settable per component, so a band sized
    # to today's node count would be the next thing to move.
    _band("lra-wing-right", IdKind.GID, 20001, 999, "lra_model.right_wing_gid",
          "The right wing chain outboard of the side of body. Until D-56.3 "
          "these were the wing stick deck's own station ids (`wing-stick`, "
          "1+) -- the borrowing the note exists to end."),
    _band("lra-wing-left", IdKind.GID, 21001, 999, "lra_model.left_wing_gid",
          "The mirror. Separate from the right so an antisymmetric case loads "
          "the two sides without renumbering, exactly as the balanced deck "
          "splits 6001/6201."),
    _band("lra-fuselage", IdKind.GID, 22001, 999, "lra_model.fuselage_gid",
          "Fuselage section-centre-line nodes (x, 0, z_c(x)) -- note 24 R-4. "
          "Includes the inserted special stations (posts, fin root x, h-tail "
          "x, gear/engine x), each tagged '$ SLOADS-NODE' where it is a named "
          "node of the BM-5 contract."),
    _band("lra-htail", IdKind.GID, 23001, 999, "lra_model.htail_gid",
          "The h-tail spanwise chain, both sides. Previously borrowed from "
          "`tail-span-htail`, which the applied-load model still owns."),
    _band("lra-vtail", IdKind.GID, 24001, 999, "lra_model.vtail_gid",
          "The fin chain, root joint to fin tip. Previously borrowed from "
          "`tail-span-vtail`."),
    _band("lra-sob", IdKind.GID, 25001, 999, "lra_model.sob_gid",
          "The wing side-of-body reporting nodes, tagged "
          "'$ SLOADS-NODE lra-sob <side>' so a consumer (or a re-import) finds "
          "them by identity rather than by coordinates -- the first of the "
          "note 24 R-10 named-node families (decision BM-5). Index 0 is the "
          "right SOB, 1 the left."),
    _band("lra-centre", IdKind.GID, 26001, 999, "lra_model.centre_gid",
          "The wing centre-box hub node C at BL 0 -- the independent node of "
          "the rigid centre-box/post tie (note 25 LM-3). A rigid link, "
          "deliberately not a CBAR: the stiffness carry-through element is "
          "step 14's (R-12)."),
    _band("lra-attach", IdKind.GID, 27001, 999, "lra_model.attach_gid",
          "Attachment nodes that are not stations of any chain: the h-tail "
          "fuselage-attachment pair (or its T-tail centreline joint), the fin "
          "root, the fin tip, and the chain nodes inserted to carry a control "
          "node's parent. Their own band for the registry's standing reason -- "
          "an attachment is a different point from a strip midpoint, and "
          "adding one must never renumber the stations beside it."),
    _band("lra-control", IdKind.GID, 28001, 999, "lra_model.control_gid",
          "Hinge and actuator nodes (plan 09 T6). Previously borrowed from "
          "`tail-control-htail` / `tail-control-vtail`, which the applied-load "
          "model still owns; one band here rather than two, because the LRA "
          "model numbers them in one pass across both surfaces."),
    _band("lra-engine", IdKind.GID, 29001, 999, "lra_model.engine_gid",
          "Engine hub (thrust point, P-6) and mount nodes, two per engine "
          "(note 24 R-9). The hub FORCE is absent until the power-effects "
          "cases ship -- the skeleton is complete before the load exists."),
    _band("lra-gear", IdKind.GID, 30001, 999, "lra_model.gear_gid",
          "The gear attachment (trunnion) nodes. Previously borrowed from "
          "`balanced-gear`, so the same id named a gear reference point in one "
          "deck and a trunnion in the other. Identifiable BY ID for the same "
          "reason that band gives: G-13's solver assertion finds the node "
          "without matching coordinates."),
    # ----------------------------------------------------------------- EIDs
    # EID 1-1000 was the wing stick model's CBAR chain, retired with the deck
    # (note 56 D-56.2). Left unregistered for the reason the GID holes above
    # are: the published map said what lived there.
    _band("mass-baseline", IdKind.EID, 9001, 100, "mass_cards.mass_cards",
          "Always-aboard items -- the MASSSET baseline (plan 12 C-1).",
          clear_of_gids=True),
    _band("mass-discretionary", IdKind.EID, 9101, 100, "mass_cards.mass_cards",
          "Overlay-only items, named by a case's ADD row.", clear_of_gids=True),
    _band("mass-ballast", IdKind.EID, 9201, 100, "mass_cards.mass_cards",
          "One per derived loading.", clear_of_gids=True),
    _band("mass-part-full", IdKind.EID, 9501, 200, "mass_cards.mass_cards",
          "A consumable row a case carries part-full -- a D-25 fraction or a G-5 "
          "burn-down. The same tank at two fuel states is two different masses, "
          "so it cannot be one shared overlay card: this band is per (case, row). "
          "Numbered above the MASSSET/GRAV SID runs so a spliced deck's ids stay "
          "readable by inspection, and clear of the 10001+ gear GIDs.",
          clear_of_gids=True),
    _band("lra-cbar", IdKind.EID, 11001, 999, "lra_model.lra_model_bdf",
          "The LRA model's CBAR chains (wing L/R, split fuselage, fin, "
          "h-tail, control). Clear of GID space, unlike the wing stick "
          "model's 1..n chain, because this deck splices many families and "
          "readability-by-inspection is the registry's stated contract.",
          clear_of_gids=True),
    _band("lra-rbe2", IdKind.EID, 12001, 500, "lra_model.lra_model_bdf",
          "PRODUCTION rigid ties (note 24 R-10): the centre-box/post hub, "
          "fin root, h-tail attachments, gear links, engine mounts. Promoted "
          "from the round-trip wrapper's test-only 900001+ band, which stays "
          "test scaffolding.", clear_of_gids=True),
    _band("roundtrip-rbe2", IdKind.EID, 900001, 1000, "roundtrip.wrap_as_stick_model",
          "Test scaffolding: numbered well clear of the CBAR chain so a wrapped "
          "deck's ties are never mistaken for exported structure.",
          clear_of_gids=True),
    # ----------------------------------------------------------------- SIDs
    _band("spc", IdKind.SID, 1, 1, "balanced_deck / lra_model / roundtrip",
          "The constraint set. A different NASTRAN namespace from LOAD, but "
          "registered so nothing quietly allocates a load set at 1."),
    _band("subcase-W", IdKind.SID, 101, 99, "case_ids.subcase_id"),
    _band("subcase-HT", IdKind.SID, 201, 99, "case_ids.subcase_id"),
    _band("subcase-VT", IdKind.SID, 301, 99, "case_ids.subcase_id"),
    _band("subcase-F", IdKind.SID, 401, 99, "case_ids.subcase_id"),
    _band("subcase-EM", IdKind.SID, 501, 99, "case_ids.subcase_id"),
    _band("subcase-LG", IdKind.SID, 601, 99, "case_ids.subcase_id"),
    _band("balanced-subcase-unmapped", IdKind.SID, 5001, 100,
          "balanced_deck.case_sids",
          "The positional fallback, for an assembled case carrying no CaseRef "
          "at all (a bare case list built in a test). Every case the suite "
          "assembles is minted; this band is what an unidentifiable one gets "
          "instead of colliding with a minted id."),
    _band("balanced-subcase", IdKind.SID, 5101, 599, "case_ids.balanced_subcase_id",
          "Minted, symmetric hand (D-R7): 5000 + the case's own subcase_id."),
    _band("balanced-subcase-stbd", IdKind.SID, 7101, 599,
          "case_ids.balanced_subcase_id",
          "Minted, starboard twin. 6000 is skipped: it is this same deck's "
          "wing/centreline GID range, and repeating those numbers as load-set "
          "ids in one file is a readability trap for no gain."),
    _band("balanced-subcase-port", IdKind.SID, 8101, 599,
          "case_ids.balanced_subcase_id", "Minted, port twin."),
    _band("massset", IdKind.SID, 9301, 100, "mass_cards.mass_check_deck"),
    _band("grav", IdKind.SID, 9401, 100, "mass_cards.inertia_only_cards"),
)

_BY_NAME: Dict[str, Band] = {b.name: b for b in BANDS}


def band(name: str) -> Band:
    """The registered band called ``name``, or raise."""
    try:
        return _BY_NAME[name]
    except KeyError:
        raise ValueError(
            f"no id band named {name!r} -- registered: "
            f"{', '.join(sorted(_BY_NAME))}") from None


def bands_of_kind(kind: IdKind) -> Tuple[Band, ...]:
    """Every band in one namespace, in id order."""
    return tuple(b for b in BANDS if b.kind is kind)


def owner_of(value: int, kind: IdKind) -> str:
    """The band name owning ``value``, or ``""`` -- for error messages and tests."""
    for b in bands_of_kind(kind):
        if value in b:
            return b.name
    return ""


def _compared(a: Band, b: Band) -> bool:
    """Do these two bands have to be disjoint?

    Same namespace: always. Different namespaces: only where an EID band asked
    to stay clear of GID space (:attr:`Band.clear_of_gids`) -- NASTRAN keeps the
    namespaces apart, so this is a readability contract, declared per band
    rather than assumed for all of them.
    """
    if a.kind is b.kind:
        return True
    kinds = {a.kind, b.kind}
    if kinds == {IdKind.GID, IdKind.EID}:
        eid = a if a.kind is IdKind.EID else b
        return eid.clear_of_gids
    return False


def overlaps() -> Iterator[Tuple[Band, Band]]:
    """Every colliding pair in the registry -- the disjointness guard's engine."""
    numbered = tuple(BANDS)
    for i, a in enumerate(numbered):
        for b in numbered[i + 1:]:
            if not _compared(a, b):
                continue
            if a.start <= b.end and b.start <= a.end:
                yield (a, b)


__all__ = [
    "BANDS",
    "Band",
    "IdKind",
    "band",
    "bands_of_kind",
    "overlaps",
    "owner_of",
]
