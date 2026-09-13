"""Solve an exported deck in the real sbeam -- the round-trip gate's machinery.

Design note: ``docs/40_history/17_sbeam_roundtrip_ci_harness_plan.md`` (decisions
S-1...S-9). Sibling authority, which this module consumes rather than
reimplements: :mod:`sloads.export.equilibrium`.

The two export-boundary gates answer different questions. ``equilibrium``
re-derives a deck's resultant **from its own card text** -- "do the cards sum to
what the header claims?". This one hands the deck to **another program** and asks
"does a real solver read this file and recover the same loads?". Only the second
one catches card syntax sbeam rejects, a GID reference to nothing, a frame or
sign mismatch, or a case-control error -- and only the second one is evidence
about the mission's actual claim, which is that the deck *solves*.

Production module, test-only *use* -- exactly as ``equilibrium`` is. Nothing in
the shipping path imports it today, and it must stay that way: acceptance point 6
of the design note is that this step changes no exported byte. It lives in
``sloads/`` rather than ``tests/`` because a later runtime "validate this deck"
surface has to consume this authority instead of hand-rolling a second one.

What this module stopped being (note 56 D-56.8, §8)
---------------------------------------------------
It was 529 lines, and roughly two-thirds of them were
``wrap_as_stick_model``: a harness that read a deck's ``GRID`` cards and
**invented** a tree of ``CBAR``s, a ``MAT1``/``PBAR`` placeholder section, a
determinate support and a case control, so that an **elementless** deck -- a
load set on a node cloud -- could be handed to a linear static solve at all.

Every deck that needed it is gone. D-56.2 deleted the per-component decks;
D-56.8 stopped the assembled balanced deck being a shipped artifact. What
remains to solve is the **LRA beam model**, which writes its own ``CBAR``
chains, its own properties and its own support, and so is handed to
:func:`solve_deck` exactly as it ships. The wrapper's own guard said as much
before it was deleted -- it *refused* a deck that already carried elements, on
the grounds that a wrapped copy is not the shipped artifact.

So the whole wrapping half retired with the last elementless deck, and with it
``Support``, ``Topology``, ``SPC_SID``, the property/element/constraint/case-
control builders and the coincident-node collapse. What is left is the part
that was always the point: hand a deck to sbeam, and read back what it says.
``_orientation`` moved to :func:`sloads.export.deck_format.orientation_vector`,
because ``lra_model`` -- the one deck writer left -- was importing a private
name out of a test harness to build its bars.

**Four solver assertions moved rather than retired**, and that is the reason
the collapse costs nothing: the free-free reaction, the gear reference-point
reaction, the flipped-fin sensitivity and the displaced-grid sensitivity all
now run against the LRA deck. They are stronger there. The assembled deck's
version of each ran through elements the harness made up; the LRA deck's runs
through the structure that ships.

The support is the point, not a workaround
------------------------------------------
sbeam's SOL 101 has no inertia relief -- ``SUPORT`` is honoured by the SOL 144
trim partition only -- so a free-free deck cannot simply be solved. It is
constrained instead at a **statically determinate** set of DOFs, which carries
exactly the residual the applied set fails to balance, and the assertion is that
the recovered reaction is **zero**. That is a stronger statement than the card
sum: it proves free-free equilibrium through the solver's own assembly, using the
lever arms *it* computes from the deck's ``GRID`` cards rather than sloads' idea
of them. A deck that closes on paper but reacts non-zero here has a geometry
error no card sum can see. The deck under test states that support itself; this
module no longer has an opinion about where it goes.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

Vec3 = Tuple[float, float, float]


class SbeamUnavailable(RuntimeError):
    """Raised when a solve is requested and sbeam is not installed.

    Its own type so the caller can distinguish "the solver is absent" (a skip,
    or a hard failure under ``SLOADS_REQUIRE_SBEAM=1`` -- decision S-7) from
    "the solver rejected the deck", which is the finding this gate exists for.
    """


# --------------------------------------------------------------------------- #
# Retired by note 56 D-56.6/D-56.7: ``flatten_mass_case``
# --------------------------------------------------------------------------- #
# It folded one MASSSET case of a mass-check deck into a baseline deck, to work
# around sbeam's SOL 101 assembling GRAV from the *baseline* mass matrix and
# never reaching the subcase's MASSSET selection. Its whole purpose was to get
# the mass-check deck solved.
#
# D-56.6 makes that impossible and unnecessary in one step: the CONM2 grids are
# unconnected by design, so the deck is not solved at all, and gate 6 is now
# ``sbeam.gpwg.compute_gpwg`` -- which honours MASSSET, so it reads the shipped
# deck per case with no transform between the artifact and the claim. The
# workaround is gone rather than merely unused, and the sbeam limitation it was
# built around no longer touches anything sloads ships.


# --------------------------------------------------------------------------- #
# Solving
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Reaction:
    """The total constraint reaction of one subcase, summed over every node.

    ``force`` is Σ of the reaction force components; ``moment`` is Σ of the
    reaction moments **plus** the reaction forces' lever arms about ``ref``, so a
    multi-node determinate support reports one rigid-body resultant rather than
    six numbers the caller has to recombine. For a determinate support the whole
    thing is the negative of the applied resultant about ``ref``, and for a deck
    claiming free-free equilibrium it is zero.

    ``scale`` is Σ\\|term\\| over the same sum, for
    :func:`sloads.export.equilibrium.closes` to size a zero-target tolerance
    with -- the same definition of "small" as the card-sum gate uses, so the two
    can never disagree about it.
    """

    force: Vec3
    moment: Vec3
    ref: Vec3
    force_scale: float
    moment_scale: float


def total_reaction(reactions: Dict[int, Sequence[float]], grids: Dict[int, Vec3],
                   ref: Vec3 = (0.0, 0.0, 0.0)) -> Reaction:
    """Sum sbeam's ``{gid: (6,)}`` reaction map into one :class:`Reaction`."""
    f = [0.0, 0.0, 0.0]
    m = [0.0, 0.0, 0.0]
    f_abs = [0.0, 0.0, 0.0]
    m_abs = [0.0, 0.0, 0.0]
    for gid, vec in reactions.items():
        fx, fy, fz = float(vec[0]), float(vec[1]), float(vec[2])
        mx, my, mz = float(vec[3]), float(vec[4]), float(vec[5])
        gx, gy, gz = grids[gid]
        dx, dy, dz = gx - ref[0], gy - ref[1], gz - ref[2]
        # r x F, right-handed, in the SLOADS/CID-0 identity frame -- the same
        # transfer equilibrium.resultant() applies to the applied cards.
        tx, ty, tz = dy * fz - dz * fy, dz * fx - dx * fz, dx * fy - dy * fx
        for axis, (fv, mv) in enumerate(((fx, mx + tx), (fy, my + ty),
                                         (fz, mz + tz))):
            f[axis] += fv
            m[axis] += mv
            f_abs[axis] += abs(fv)
            m_abs[axis] += abs(mv)
    return Reaction(force=(f[0], f[1], f[2]), moment=(m[0], m[1], m[2]), ref=ref,
                    force_scale=max(f_abs) if f_abs else 0.0,
                    moment_scale=max(m_abs) if m_abs else 0.0)


def solve_deck(deck_text: str) -> Dict[int, "object"]:
    """``{subcase id: Sol101Result}`` -- parse and solve every subcase in the deck.

    Goes through sbeam's own reader (``parse_bdf``) rather than any sloads
    parser, deliberately: a deck this gate accepts is a deck sbeam accepts.
    Raises :class:`SbeamUnavailable` if sbeam is not installed; anything the
    solver itself raises (a parse error, a singular stiffness matrix) is left to
    propagate, because that *is* the finding.
    """
    try:
        from sbeam.parser.bdf_reader import parse_bdf
        from sbeam.solver.sol101 import run_sol101
    except ImportError as exc:  # pragma: no cover - exercised by the skip path
        raise SbeamUnavailable(
            "sbeam is not installed -- `pip install -e '.[solver]'` to run the "
            "round-trip gate") from exc

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "deck.bdf")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(deck_text)
        cc, bulk = parse_bdf(path)
    if cc.sol != 101:
        raise ValueError(f"deck is SOL {cc.sol}; this harness solves SOL 101 only")
    return {sc.subcase_id: run_sol101(bulk, sc) for sc in cc.subcases}


__all__ = [
    "Reaction",
    "SbeamUnavailable",
    "solve_deck",
    "total_reaction",
]
