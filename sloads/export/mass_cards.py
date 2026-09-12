"""CONM2 / MASSSET mass export -- an *independent* mass model for sbeam.

Plan 12 (``docs/40_history/32_conm2_mass_export_plan.md``), steps C3/C4,
decisions C-2/C-3/C-6. Conventions: ``docs/10_standard/CONVENTIONS.md``.

Why this exists
---------------
The ``FORCE``/``MOMENT`` deck is the **total** applied load -- aero plus inertia
-- and stays that way; it is the deliverable. But it is also *self-consistent by
construction*: the inertia half is computed by the same code that writes the
cards, so nothing outside sloads can contradict it. There is no printed oracle
for a distributed inertia load, so that half has, until now, been checked only
against itself.

Exporting the mass distribution as ``CONM2`` cards breaks the circularity. sbeam
parses the mass model independently, applies the case acceleration through a
``GRAV`` card, recovers the nodal inertia loads itself, and the two can be
compared. That is a genuine external check on the half of the load set with no
oracle -- and it is precisely the class of error step B1 turned up (two mass
models disagreeing by up to 41 % of the fuselage beam, unnoticed for want of
anything comparing them).

Not double-counting inertia, structurally
-----------------------------------------
The total ``FORCE``/``MOMENT`` set already contains inertia. A deck that applies
those cards *and* accelerates the CONM2 masses counts it twice -- and decision
C-6 is that this is made impossible rather than warned about, because it is the
one error here that produces a *plausible* wrong answer (a heavier airplane, not
a crash). So:

* :func:`conm2_fragment` is the mass model entire -- ``GRID`` + ``CONM2`` +
  ``MASSSET``, self-contained since note 56 D-56.6, every mass on a grid at its
  own CG with a zero offset. Its header says in as many words that it must not
  be applied together with the total load set.
* :func:`mass_check_deck` wraps that fragment in case control and a ``GRAV``
  field, and emits **no** ``FORCE``/``MOMENT`` cards at all. It is read by a
  grid-point weight recovery, **not** by a stiffness solve: the grids are
  unconnected by design, so ``SOL 101`` over them is singular and the header
  says so.

Card syntax is sbeam's own (``sbeam/model/mass.py``,
``sbeam/parser/bdf_reader.py``): ``CONM2, EID, GID, CID, M, X1, X2, X3, I11,
I21, I22, I31, I32, I33`` and ``MASSSET, SID, LABEL, SCALE`` followed by
``+, ADD|REPLACE|DELETE, eid...`` continuation rows. A ``MASSSET`` modifies a
**baseline** (the model's own mass plus baseline ``CONM2``s); EIDs named by
``ADD`` are overlay-only and are excluded from that baseline. This module uses
that split directly: the always-aboard items are the baseline, and each payload
case ``ADD``s the discretionary items and ballast it carries.

Units
-----
``CONM2``'s ``M`` is **mass**, and the weight database stores **weight**. The
conversion is the ``mass`` channel added at step C2
(:func:`sloads.units.deliverable_units`), which is the only dimension in the
suite whose Imperial factor is not 1.0 -- see :data:`sloads.units.LB_TO_SLINCH`.
A mass set written with a weight-valued ``M`` is wrong by 386x in a file that
parses cleanly, so :func:`_checked_mass_units` refuses a unit set that does not
satisfy ``force / (mass x length) == g``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Sequence, Tuple

from ..mass_distribution import (
    CaseLoading,
    derive_case_loadings,
)
from ..models import MassItem, Project
from ..units import DeliverableUnits, UnitSystem
from .bands import band
from .coordinates import SBEAM_CID, to_grid
from .deck_format import fmt, fmt3, sf_str, solver_units, stamped

# --------------------------------------------------------------------------- #
# EID / SID bands -- declared in :mod:`sloads.export.bands`, the single owner of
# every id run in the suite; that module's guard proves them disjoint from every
# GID band, which is what lets a CONM2 set be spliced into a load deck.
# --------------------------------------------------------------------------- #
_BASELINE_BAND = band("mass-baseline")
_DISCRETIONARY_BAND = band("mass-discretionary")
_BALLAST_BAND = band("mass-ballast")
_PART_FULL_BAND = band("mass-part-full")
_MASSSET_BAND = band("massset")
_GRAV_BAND = band("grav")
_MASS_CG_BAND = band("mass-cg")


def mass_cg_gid(index: int) -> int:
    """GRID id of the ``index``-th ``CONM2``'s own CG node (note 56 D-56.6).

    One grid per card, at the item's own centre of gravity, carrying a zero
    offset. Its own band because these grids are **unconnected by design**
    (ruling 9): they are not stations of any beam and nothing ties them to one,
    so numbering them out of a beam run would assert a relationship that does
    not exist.
    """
    return _MASS_CG_BAND.allocate(index)

#: Always-aboard items (empty + minimum weight) -- the MASSSET **baseline**.
MASS_EID_BASELINE = _BASELINE_BAND.start
#: Discretionary items -- overlay-only, named by a case's ``ADD`` row.
MASS_EID_DISCRETIONARY = _DISCRETIONARY_BAND.start
#: Per-case ballast -- one overlay card per derived loading.
MASS_EID_BALLAST = _BALLAST_BAND.start
#: Per-case part-full consumable rows -- one overlay card per (case, scaled row).
MASS_EID_PART_FULL = _PART_FULL_BAND.start
#: MASSSET SIDs, one per payload case.
MASSSET_SID_BASE = _MASSSET_BAND.start
#: GRAV SIDs, one per payload case.
GRAV_SID_BASE = _GRAV_BAND.start


def _checked_mass_units(units: DeliverableUnits) -> DeliverableUnits:
    """Reject a unit set whose mass pair is not dimensionally consistent (C-5).

    The mass analogue of ``coordinates._checked``, and needed for the same
    reason: the human channel's mass is a pound (or a kilogram), which is a
    *weight*, and writing it into ``CONM2``'s ``M`` gives a deck that parses
    cleanly and accelerates to 386x the right force.
    """
    if not units.is_mass_consistent:
        raise ValueError(
            f"{units.channel.value} unit set (mass {units.mass.label}) is not "
            "dimensionally consistent -- F = m*a does not hold in it, so it must "
            "not be written to a CONM2 card. Resolve it with "
            "solver_units(system)"
        )
    return units


# --------------------------------------------------------------------------- #
# Item -> (EID, GID) assignment
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MassCard:
    """One ``CONM2``, on its **own** ``GRID`` at the item's own CG.

    **There is no offset** (note 56 D-56.6). The card used to hang on the
    nearest fuselage beam station and carry ``x1/x2/x3`` back to the item's true
    position -- exact in mass, CG and inertia, but it made the attachment node a
    presentational choice (decision C-3) and it made the wing items' node a
    stated limitation, since a wing item on a fuselage station is not where the
    mass is. Each item now gets a grid at its own centre of gravity and the
    offset is identically zero, so the model needs no explaining: a card is one
    mass at one point.

    These grids are **unconnected by design** (ruling 9). sloads ships no tie.
    sbeam's GPWG reads mass and CG from the cards and the grid positions with no
    stiffness matrix, so the check the export exists for is unaffected; a
    stiffness solve over them is singular, and the deck header says so.
    """

    eid: int
    gid: int
    item: MassItem
    overlay: bool
    #: Which loading this card belongs to, for the overlay cards that exist
    #: **per case** rather than per database row -- the solved/entered ballast and
    #: a consumable row carried part-full. ``None`` on a card that is shared, i.e.
    #: one whose item is a database row at its own weight.
    case_index: Optional[int] = None


def mass_cards(project: Project) -> Tuple[List[MassCard], List[CaseLoading]]:
    """``(cards, loadings)`` -- the baseline + overlay ``CONM2`` set for ``project``.

    Baseline cards are the always-aboard items (empty + minimum weight); overlay
    cards are the discretionary items and each derived loading's ballast. Only
    **derivable** loadings (plan 12 C-1's credibility gate) contribute: a case
    needing 20 % of the airplane as ballast is not a mass model and is reported,
    not exported.
    """
    items = project.weight.items if project.weight is not None else []
    if not items:
        return [], []
    loadings = [ld for ld in derive_case_loadings(project) if ld.derivable]

    from ..models import MassItemKind

    # The overlay set is built from what the loadings actually carry, not from
    # "every discretionary item" -- and that is structural, not tidiness.
    #
    # sbeam's baseline is *every CONM2 no MASSSET names* (overlay-only status
    # comes from being referenced by an ADD/REPLACE row). So an overlay card that
    # no case adds does not sit out: it silently joins the baseline and is
    # counted in EVERY case. Caught 2026-08-08 by running sbeam's own GPWG over
    # the exported ga6 deck -- it recovered 9.0083 slinch against sloads'
    # 8.8063, exactly 78 lb too much, which is the database's own "Ballast" row.
    # That row is superseded by the per-case ballast this export derives, so
    # emitting it at all was double-counting the same physical thing.
    #
    # Deriving the overlay list from the loadings makes an unreferenced overlay
    # card impossible to write; :func:`unreferenced_overlay_eids` is the guard
    # that keeps it that way.
    baseline = [it for it in items if it.kind != MassItemKind.DISCRETIONARY]
    rows = {id(it) for it in items}
    carried = {id(it) for ld in loadings for it in ld.items}
    discretionary = [it for it in items
                     if it.kind == MassItemKind.DISCRETIONARY and id(it) in carried]

    cards: List[MassCard] = []
    for eid_band, group, overlay in ((_BASELINE_BAND, baseline, False),
                                     (_DISCRETIONARY_BAND, discretionary, True)):
        for i, it in enumerate(group):
            cards.append(MassCard(eid=eid_band.allocate(i), gid=0, item=it,
                                  overlay=overlay))
    # A loading may carry a consumable row **part-full** -- a D-25 entered
    # fraction, or the G-5 burn-down a GROUND target runs -- and that item is a
    # scaled copy, not the database row. It therefore cannot share the row's
    # overlay card: one card is one mass, and the same tank at two fuel states is
    # two masses. Each gets its own card, named only by its own case's ADD row.
    #
    # Found 2026-08-15, when the Pri 5 loadings made part-full fuel the norm: the
    # scaled copy matched no card, so the row left the deck entirely and the
    # exported mass model weighed *less* than the loading it declared (dhc8's MLW
    # case by 4,160 lb). It parsed, and it solved.
    part_full = 0
    for i, loading in enumerate(loadings):
        for it in loading.items:
            if id(it) in rows or it is loading.ballast:
                continue        # a database row at its own weight, or the ballast
            if it.kind != MassItemKind.DISCRETIONARY:
                raise ValueError(
                    f"weight/CG case '{loading.name}' carries '{it.name}' "
                    f"part-full, but that row is {it.kind.value} and so sits in "
                    "the MASSSET baseline, which every case shares. Expressing it "
                    "would need a REPLACE row; today only a discretionary row may "
                    "be part-full. Make the row discretionary, or carry it whole.")
            cards.append(MassCard(eid=_PART_FULL_BAND.allocate(part_full), gid=0,
                                  item=it, overlay=True, case_index=i))
            part_full += 1
    for i, loading in enumerate(loadings):
        if loading.ballast is None:
            continue
        cards.append(MassCard(eid=_BALLAST_BAND.allocate(i), gid=0,
                              item=loading.ballast, overlay=True, case_index=i))
    # Every card gets its own GRID at its own item's CG (note 56 D-56.6),
    # numbered in the order the cards were built so a card's grid is stable for
    # a given database. Assigned here, once, rather than at each construction
    # site: one card is one mass at one point, and one counter is what makes
    # that true by construction rather than by three sites agreeing.
    cards = [replace(c, gid=mass_cg_gid(i)) for i, c in enumerate(cards)]
    return cards, loadings


def unreferenced_overlay_eids(project: Project) -> List[int]:
    """Overlay ``CONM2`` EIDs that no ``MASSSET`` names -- must always be empty.

    sbeam decides overlay-only status by *reference*: a card no ADD/REPLACE row
    names belongs to the baseline and is therefore in every payload case. An
    overlay card that slipped through would not fail to load, it would quietly
    make every case heavier -- the exact plausible-wrong-answer failure mode
    decision C-6 exists to rule out. Structural by construction (the overlay list
    is built from the loadings); this is the drift guard.
    """
    cards, loadings = mass_cards(project)
    named = {e for i, ld in enumerate(loadings) for e in _overlay_eids(cards, ld, i)}
    return sorted(c.eid for c in cards if c.overlay and c.eid not in named)


def _overlay_eids(cards: Sequence[MassCard], loading: CaseLoading,
                  index: int) -> List[int]:
    """The overlay EIDs one case's ``ADD`` row names.

    Two kinds of card, and the distinction is the whole correctness argument:
    a **shared** card (``case_index is None``) is a database row at its own
    weight, and any case carrying that row names it; a **per-case** card is one
    this case alone owns -- its ballast, or a row it carries part-full -- and is
    named by case index rather than by item.

    Shared cards are matched on object identity, not on name: two items may
    legitimately share a name (``"3rd person"`` / ``"4th person"`` differ only by
    station in some databases), and a MASSSET that named an EID twice is a parse
    error in sbeam by design.
    """
    aboard = {id(it) for it in loading.items}
    return [c.eid for c in cards if c.overlay
            and (c.case_index == index
                 or (c.case_index is None and id(c.item) in aboard))]


# --------------------------------------------------------------------------- #
# Card text
# --------------------------------------------------------------------------- #
def _conm2_line(card: MassCard, u: DeliverableUnits) -> str:
    m = card.item.weight_lb * u.mass.factor
    k = u.mass_inertia.factor
    # i21/i31/i32 are the products of inertia. ``MassItem`` carries none, and a
    # laterally symmetric airplane has Ixy = Iyz = 0 exactly; Ixz is generally
    # non-zero but the database has no field for it. Emitted as 0 with the
    # header's note rather than silently -- see plan 12 risk R2.
    # Zero offset, always: the grid IS the item's CG (note 56 D-56.6).
    return (f"CONM2, {card.eid}, {card.gid}, {SBEAM_CID}, {fmt(m)}, "
            f"{fmt3(0.0, 0.0, 0.0)}, "
            f"{fmt(card.item.ixx * k)}, 0.0, {fmt(card.item.iyy * k)}, "
            f"0.0, 0.0, {fmt(card.item.izz * k)}")


#: An 8-character alphanumeric field, which is sbeam's, not ours to widen.
_MASSSET_LABEL_LEN = 8


def massset_labels(loadings: Sequence[CaseLoading]) -> List[str]:
    """The ``MASSSET`` label of every loading in the derivable list, made unique.

    The label is the case name upper-cased, stripped to alphanumerics and cut to
    eight characters, which is a **lossy** map: "Max take-off forward CG" and
    "Max take-off aft CG" both reach ``MAXTAKEO`` (review CR-C-4). The SIDs stay
    distinct, so a solver is unaffected -- but the deck's comment block, the
    report's mass-case table and any label-reading consumer then show two payload
    cases, at two weights and two CGs, under one name.

    A collision is disambiguated rather than refused: the truncation is ours and
    the eight characters are sbeam's, so a project is not blocked over a display
    label it did not choose. The second and later claimants take a numeric suffix
    in list order (``MAXTAKEO``, ``MAXTAKE2``, ``MAXTAKE3``), so the labels are a
    function of the derivable list alone and two runs of the same project agree.
    """
    out: List[str] = []
    taken: set = set()
    for index, loading in enumerate(loadings):
        base = "".join(ch for ch in loading.name.upper()
                       if ch.isalnum())[:_MASSSET_LABEL_LEN] or f"CASE{index}"
        label = base
        n = 2
        while label in taken:
            suffix = str(n)
            label = base[:_MASSSET_LABEL_LEN - len(suffix)] + suffix
            n += 1
        taken.add(label)
        out.append(label)
    return out


def massset_identity(loadings: Sequence[CaseLoading], index: int) -> Tuple[int, str]:
    """``(SID, LABEL)`` -- the identity the exported mass model gives one loading.

    Minted here and nowhere else, so the ``MASSSET`` card, the report's mass-case
    table and the bundle manifest name one payload case the same way. ``index``
    is the loading's position in ``loadings``, the **derivable** list (the order
    :func:`mass_cards` returns and :func:`conm2_fragment` writes), which is what
    the SID band is allocated against.

    The whole list is taken rather than the one loading because uniqueness is a
    property of the set: a label cannot be checked against the others it has to
    differ from without them (:func:`massset_labels`).
    """
    return _MASSSET_BAND.allocate(index), massset_labels(loadings)[index]


def mass_case_rows(project: Project) -> List[Dict[str, object]]:
    """One row per payload case: what the exported mass model calls it, or why not.

    Every case in ``flight_loads.cg_cases`` appears -- a case the weight database
    cannot produce as a loading is reported with ``exported=False`` and its
    reason, never dropped, because "absent from the mass model" is exactly the
    fact a consumer needs (plan 12 C-1's credibility gate). ``entered`` says
    whether the loading was **stated on the case** (D-25) or searched for.

    Values are raw Imperial (lb, in) as everywhere else in the calc; the report
    converts at its own boundary.
    """
    loadings = derive_case_loadings(project)
    derivable = [ld for ld in loadings if ld.derivable]
    order = {id(ld): i for i, ld in enumerate(derivable)}
    rows: List[Dict[str, object]] = []
    for loading in loadings:
        index = order.get(id(loading))
        sid, label = (massset_identity(derivable, index) if index is not None
                      else (None, ""))
        rows.append({
            "case": loading.name,
            "exported": loading.derivable,
            # D-25: which route produced this loading. A consumer reading a mass
            # model needs to know whether the loading was stated by the engineer
            # or reconstructed by the search -- the two carry different authority.
            "entered": loading.entered,
            "massset_sid": sid,
            "massset_label": label,
            "weight_lb": loading.weight_lb,
            "cg_x": loading.cg_x,
            "cg_z": loading.cg_z,
            "ballast_lb": loading.ballast.weight_lb if loading.ballast else 0.0,
            "ballast_fraction": loading.ballast_fraction,
            "note": loading.note,
        })
    return rows


def _massset_block(cards: Sequence[MassCard], loadings: Sequence[CaseLoading],
                   index: int) -> List[str]:
    loading = loadings[index]
    sid, label = massset_identity(loadings, index)
    eids = _overlay_eids(cards, loading, index)
    lines = [
        f"$ {loading.name}: {loading.weight_lb:.0f} lb at "
        f"x {loading.cg_x:.2f} in, z {loading.cg_z:.2f} in"
        + (f"; ballast {loading.ballast.weight_lb:.0f} lb "
           f"({loading.ballast_fraction * 100:.1f} %) at x {loading.ballast.x:.1f}"
           if loading.ballast is not None else "; no ballast"),
        f"MASSSET, {sid}, {label}, 1.0",
    ]
    # ADD rows carry up to 7 EIDs each (sbeam's reader).
    for start in range(0, len(eids), 7):
        chunk = ", ".join(str(e) for e in eids[start:start + 7])
        lines.append(f"+, ADD, {chunk}")
    return lines


def _header(project: Project, u: DeliverableUnits, cards: Sequence[MassCard]) -> List[str]:
    total = math.fsum(c.item.weight_lb for c in cards if not c.overlay)
    # The wing share used to be totalled here, to caption the standing
    # limitation that wing items hung on a fuselage node. Note 56 D-56.6 retired
    # both: every item is on a grid at its own CG, so a wing mass is at the wing
    # mass's position and there is nothing to caption.
    skipped = [ld for ld in derive_case_loadings(project) if not ld.derivable]
    lines = [
        "$ ==================================================== SLOADS MASS MODEL",
        "$ CONM2 distributed mass from the itemized weight database, with one",
        "$ MASSSET per derivable payload case (baseline = always-aboard items;",
        "$ each case ADDs the discretionary items and ballast it carries).",
        f"$ Mass in {u.mass.label}; inertia in {u.mass_inertia.label}; "
        f"grid coordinates in {u.length.label}.",
        f"$ Baseline (empty + minimum flight weight): {total:.0f} lb.",
        "$",
        "$ DO NOT apply this set together with the FORCE/MOMENT load deck: those",
        "$ cards are the TOTAL applied load and already contain inertia. Using",
        "$ both counts the inertia twice.",
        "$",
        "$ THESE GRIDS ARE UNCONNECTED, ON PURPOSE (note 56 D-56.6). One GRID per",
        "$ item, at that item's own CG, with a zero CONM2 offset -- so the model",
        "$ needs no beam to be read and states no attachment it does not have.",
        "$ A grid-point weight recovery (GPWG) reads this as it stands: mass and",
        "$ CG come from the cards and the grid positions, with no stiffness",
        "$ matrix. A STIFFNESS SOLVE OVER IT IS SINGULAR and will report exactly",
        "$ that -- it is not a failure of the deck, it is a mass model with no",
        "$ structure. To splice it into one, RBE2 each grid to your own model.",
        "$",
        "$ Products of inertia I21/I31/I32 are 0: the database carries none, and",
        "$ Ixy = Iyz = 0 exactly on a laterally symmetric airplane. Ixz is not",
        "$ generally zero and is not modelled.",
    ]
    if skipped:
        lines += ["$", "$ Payload cases NOT exported (not loadings this database can produce):"]
        for ld in skipped:
            lines.append(f"$   {ld.name} -- {ld.note}")
    lines.append("$ ----------------------------------------------------------------------")
    return lines


def conm2_fragment(project: Project, *,
                   header_comment: str = "",
                   system: UnitSystem = UnitSystem.IMPERIAL) -> str:
    """``GRID`` + ``CONM2`` + ``MASSSET`` bulk data -- the mass model, entire.

    **Self-contained since note 56 D-56.6.** It used to emit no ``GRID`` cards
    and hang each ``CONM2`` on a node the receiving deck already defined, which
    made the mass model's validity depend on a beam it did not own. It now
    carries one grid per card at that item's own CG, with a zero offset, so the
    fragment *is* the mass model and nothing else has to be true for it to be
    read.

    The grids are **unconnected** -- no element, no ``SPC``, no tie -- which is
    the design (ruling 9) and not an omission. sbeam's GPWG recovers mass and CG
    from the cards and grid positions alone; a stiffness solve over them is
    singular. Splice this into a stiffness model only after tying each grid to
    that model with an ``RBE2`` of your own.

    ``header_comment`` is the ``$``-prefixed methods & units block
    (:func:`~sloads.report.bdf_comment_block`), applied through the same
    :func:`~sloads.export.deck_format.stamped` owner the load decks use, so a
    mass model forwarded on its own states its own basis and unit set. A blank
    value leaves the fragment byte-identical -- which is what keeps
    :func:`mass_check_deck` (which embeds this fragment) from carrying two
    stamps.
    """
    u = _checked_mass_units(solver_units(system))
    cards, loadings = mass_cards(project)
    if not cards:
        raise ValueError(
            "Project has no 'weight.items' database to export as CONM2 cards")
    out = _header(project, u, cards)
    out += ["$ ------------------------------------------------- GRIDS (one per item CG)"]
    out += [f"GRID, {c.gid}, {SBEAM_CID}, "
            f"{fmt3(*to_grid(c.item.x, c.item.y, c.item.z, units=u))}"
            for c in cards]
    out += ["$ ------------------------------------------------ BASELINE (always aboard)"]
    out += [_conm2_line(c, u) for c in cards if not c.overlay]
    out += ["$ ------------------------------------------------------- OVERLAY (per case)"]
    out += [_conm2_line(c, u) for c in cards if c.overlay]
    for i in range(len(loadings)):
        out += ["$"] + _massset_block(cards, loadings, i)
    return stamped(header_comment, "\n".join(out) + "\n")


def mass_properties(project: Project, loading: CaseLoading,  # noqa: ARG001  -- public signature (project reserved for the LRA transfer)
                    system: UnitSystem = UnitSystem.IMPERIAL) -> Dict[str, float]:
    """``{weight/mass/cg_x/cg_z/iyy}`` of one loading, in deck units.

    The numbers a consumer checks the ``CONM2`` set against (plan 12 acceptance
    2). ``iyy`` is the airplane pitch inertia about the loading's own CG --
    parallel-axis transferred, so it is sensitive to *where* each mass sits and
    not only to how much there is, which is the point of checking a distribution
    rather than a total.
    """
    u = _checked_mass_units(solver_units(system))
    items = loading.items
    w = math.fsum(it.weight_lb for it in items)
    if not w:
        return {"weight": 0.0, "mass": 0.0, "cg_x": 0.0, "cg_z": 0.0, "iyy": 0.0}
    cx = math.fsum(it.weight_lb * it.x for it in items) / w
    cz = math.fsum(it.weight_lb * it.z for it in items) / w
    iyy = math.fsum(it.iyy + it.weight_lb * ((it.x - cx) ** 2 + (it.z - cz) ** 2)
              for it in items)
    return {
        "weight": w,
        "mass": w * u.mass.factor,
        "cg_x": to_grid(cx, 0.0, 0.0, u)[0],
        "cg_z": to_grid(0.0, 0.0, cz, u)[2],
        "iyy": iyy * u.mass_inertia.factor,
    }


# --------------------------------------------------------------------------- #
# The runnable mass-check deck (C-4) -- MASSSET + GRAV, and no load cards
# --------------------------------------------------------------------------- #
def mass_check_deck(project: Project, *,
                    header_comment: str = "",
                    system: UnitSystem = UnitSystem.IMPERIAL,
                    nz: float = 1.0) -> str:
    """The mass model with case control and a ``GRAV`` field around it.

    One ``SUBCASE`` per derivable payload case, each selecting that case's
    ``MASSSET`` and a ``GRAV`` carrying ``nz x g`` downward.

    **It is checked by a grid-point weight recovery, not by a solve** (note 56
    D-56.6/D-56.7, ruling 16). The ``CONM2`` grids are unconnected by design, so
    a stiffness solve over this deck is singular -- the header says so plainly
    rather than letting a reader discover it by running one, which is the defect
    class #173 was filed for. What replaced the solve is stronger where it
    counts: ``sbeam.gpwg.compute_gpwg`` reads mass and CG off **this deck as
    shipped**, per mass case, because GPWG honours ``MASSSET`` where ``SOL 101``
    does not -- the three solver legs it replaces had to flatten each case into
    a baseline deck to work around that gap.

    **What the retired solve legs used to add**, recorded rather than dropped
    silently: sbeam's own mass-matrix assembly and the ``GRAV`` acceleration
    path stopped being exercised, in both unit systems, and the SI one is what
    caught a 25.4x ``GRAV`` slip in the 2026-08-10 review. GPWG still runs in
    both systems, so the SI channel is still checked -- without the acceleration
    path. ``GRAV`` is also a uniform *translational* field and sbeam has no
    ``RFORCE``, so rotational-acceleration inertia was never recoverable from a
    ``CONM2`` set this way and stays checked by sloads-side closure.

    Carries **no** ``FORCE``/``MOMENT`` cards, by construction (C-6).
    """
    u = _checked_mass_units(solver_units(system))
    _, loadings = mass_cards(project)
    if not loadings:
        raise ValueError(
            "no payload case is derivable from this weight database -- nothing "
            "to build a mass-check deck from (see mass_distribution."
            "derive_case_loadings for why each case was rejected)")
    g = u.gravity                       # g in deck units -- single owner, units.py

    head: List[str] = ["SOL 101", "$"]
    for i, loading in enumerate(loadings):
        head += [
            f"SUBCASE {_MASSSET_BAND.allocate(i)}",
            f"  LABEL = {loading.name}",
            f"  TITLE = mass check, Nz={nz:g} (SF={sf_str(1.0)}, no load cards)",
            f"  MASSSET = {_MASSSET_BAND.allocate(i)}",
            f"  LOAD = {_GRAV_BAND.allocate(i)}",
            "$",
        ]
    head.append("BEGIN BULK")

    # No nodes, no elements, no constraints. Note 56 D-56.6 deleted the
    # placeholder massless fuselage beam that used to be here: it existed only
    # because the CONM2 cards had to hang on something, and they now carry their
    # own grids. Nothing is left for it to support, and a beam with no purpose
    # in a mass model is the sort of scaffold a reader mistakes for structure.
    # The SPC1 went with it -- there is nothing to constrain.
    bulk: List[str] = [
        "$ ------------------------------------------------------ ACCELERATION",
        f"$ GRAV carries Nz x g = {nz:g} x {g:.4f} = {nz * g:.4f} "
        f"{u.length.label}/s^2, down (-z).",
        "$ Translational only: sbeam has no RFORCE, so pitch/yaw angular",
        "$ acceleration inertia is NOT recoverable from this set and stays",
        "$ checked by sloads-side closure.",
    ]
    for i, _ in enumerate(loadings):
        bulk.append(f"GRAV, {_GRAV_BAND.allocate(i)}, 0, {fmt(nz * g)}, 0.0, 0.0, -1.0")
    bulk += ["$"] + conm2_fragment(project, system=system).splitlines()
    return stamped(header_comment, "\n".join(head + bulk + ["ENDDATA"]) + "\n")


# --------------------------------------------------------------------------- #
# Retired by note 56 D-56.7: ``inertia_only_cards`` and ``case_station_weights``
# --------------------------------------------------------------------------- #
# Both existed to cross-check sloads' *reduction* of a mass to a beam station
# against sbeam's recovery of it: ``case_station_weights`` gathered a loading's
# items onto their attachment nodes through the very ``_attach_gid`` the cards
# used, and ``inertia_only_cards`` wrote the resulting ``-w x nz`` as FORCE cards
# for the round-trip leg to compare against.
#
# D-56.6 puts every mass on a GRID at its own CG with a zero offset, so there is
# no reduction left to check -- the comparison would be an identity against
# itself. The three solver legs that consumed it retire with it (ruling 16);
# gate 6 is now GPWG, which reads mass and CG off the shipped deck per mass case
# without a stiffness solve, and needs no second card set to compare against.
#
# The ``grav`` SID band survives: ``mass_check_deck`` still writes GRAV.


__all__ = [
    "GRAV_SID_BASE",
    "MASSSET_SID_BASE",
    "MASS_EID_BALLAST",
    "MASS_EID_BASELINE",
    "MASS_EID_DISCRETIONARY",
    "MassCard",
    "conm2_fragment",
    "mass_cards",
    "mass_case_rows",
    "mass_check_deck",
    "mass_properties",
    "massset_identity",
    "massset_labels",
    "unreferenced_overlay_eids",
]
