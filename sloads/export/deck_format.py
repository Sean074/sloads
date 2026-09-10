"""Deck-writing primitives shared by every bulk-data writer in this package.

One owner for *how a card is written* — number format, dust snapping, ``$``
comment wrapping, the ``$``-block stamp, and the placeholder section properties
a determinate stick model needs to be solvable. Nothing here knows what a load
*is*: the contract statements (basis sentence, ``-ULT`` marker, the per-case
factor) stay with the writers in :mod:`sloads.export.sbeam_bridge`, which is
where the load-output contract lives.

**Why it is its own module (CH-4, #15).** These helpers were private names in
``sbeam_bridge``, and five sibling writers — ``mass_cards``, ``balanced_deck``,
``lra_model``, ``lra_import``, ``roundtrip`` — reached across the package to
import them through the underscore. A private imported from another module is
not private; it is an undeclared API whose every rename is a silent breakage.
They are public here, under the names the card writers actually mean, so there
is one import path and one place a format rule changes.

Every name is byte-critical: :func:`fmt`, :func:`fmt3` and :func:`snap_zero`
each exist because a printed deck differed across platforms for a load that did
not (see their docstrings and ``tests/test_platform_stability.py``).
"""

from __future__ import annotations

import textwrap
from typing import List

from ..units import canonical

# --------------------------------------------------------------------------- #
# Number formatting
# --------------------------------------------------------------------------- #

# Loads below this magnitude are treated as zero and not emitted (matches
# sbeam/results/load_export.py).
CARD_TOL = 1e-9


def fmt(val: float) -> str:
    """Format a load/coordinate component in NASTRAN 6-digit scientific style.

    Canonicalised first: seven printed digits is finer than a computed load is
    reproducible across platforms, and a value on the tie of its seventh digit
    prints two ways for one load. :func:`sloads.units.canonical` is the owner of
    that rule for every channel -- see it for the two cases that earned it.
    """
    return f"{canonical(val):.6E}"


def fmt3(x: float, y: float, z: float) -> str:
    """The three components of one FORCE/MOMENT card, **dust snapped to zero**.

    A component that is zero by construction -- ``Fy`` of a symmetric case, the
    off-axis terms of a transferred couple -- lands on ~1e-14 of cancellation
    residue after the coordinate transfers, and :func:`fmt` would print that
    residue to seven significant digits: ``6.101335E-15`` on one machine,
    ``1.987480E-14`` on another. Every digit of it is libm/FMA/reassociation
    noise, so the byte differs across platforms and Python versions while the
    load does not (the same failure class :func:`snap_zero` fixed for the stated
    totals; this is the per-component form, found on the LRA deck's cards in CI).

    The floor is the card's own scale (:data:`CARD_TOL` relative to its largest
    component, or absolute for an all-tiny card), so a real small component on a
    light airplane is never masked -- and a card whose components are *all* under
    the emitter's threshold is not emitted at all, as before.
    """
    scale = max(abs(x), abs(y), abs(z), 1.0)
    return ", ".join(fmt(snap_zero(v, scale)) for v in (x, y, z))


def snap_zero(value: float, scale: float) -> float:
    """A quantity that is zero **by construction** renders as an unsigned zero.

    The fuselage set closes exactly in exact arithmetic -- ``sum(Fz) == 0`` and
    the terminal ``Myy == 0`` are the equilibrium the deck claims -- but in
    floating point the sum lands on ~1e-11 of accumulated cancellation dust. Its
    magnitude is irrelevant at any printed precision; its **sign is not
    reproducible across platforms** (x86 vs ARM, different libm/FMA builds
    reassociate the upstream arithmetic), so ``f"{total:.2f}"`` prints ``0.00``
    on one machine and ``-0.00`` on another. That is a byte difference in a
    deliverable, and it is what failed the Imperial digest baseline in CI
    (``sbeam/body_cards``) while the same commit passed locally.

    Cards already have this rule -- nothing under :data:`CARD_TOL` is emitted at
    all. This gives the *stated totals* the same one, relative to the set's own
    scale so it cannot mask a real residual on a heavy airplane: a genuine
    imbalance is orders above ``1e-9 x`` the largest load in the same column.
    """
    return 0.0 if abs(value) <= CARD_TOL * max(abs(scale), 1.0) else value


def sf_str(sf: float) -> str:
    """``SF`` as it appears on a deliverable: ``1.0``/``1.5``/``1.25`` — always
    with a decimal point (``SF=1`` reads poorly on an engineering document,
    M4-16)."""
    s = f"{sf:g}"
    return s if "." in s else f"{sf:.1f}"


# --------------------------------------------------------------------------- #
# ``$`` comment channel
# --------------------------------------------------------------------------- #


def comment(text: str) -> List[str]:
    """``text`` as ``$`` comment lines, wrapped inside the 72-column card width.

    Free-field bulk data is 72 columns; ``$ `` costs two of them, so the text
    wraps at 70. Every generated ``$`` sentence goes through here rather than
    being hand-fitted, because the same sentence is wider in SI (the same load in
    newtons carries more digits) -- which is exactly how the wing deck's ``$``
    lines reached ~100 columns unnoticed. Guarded by
    ``test_deck_comments_fit_the_free_field_card_width``.
    """
    return [f"$ {ln}" for ln in textwrap.wrap(text, width=70)]


def stamped(header_comment: str, deck: str) -> str:
    """Prepend a ``$``-comment block to a bulk-data deck (M4-20 step 5).

    Every BDF writer takes a ``header_comment`` for the same reason the CSV
    writers do: a deck forwarded on its own must still state which basis its
    loads are on and which unit set it is in. Until step 5 the Export page built a
    ``bdf_comment_block`` and then never applied it, so the four decks were the
    one channel in the bundle carrying no statement at all.

    ``$`` is a comment to every bulk-data parser, so the block is inert; a blank
    ``header_comment`` returns the deck untouched, which keeps every existing
    caller (and the frozen Imperial comparison) byte-identical.
    """
    if not header_comment:
        return deck
    return header_comment.rstrip("\n") + "\n" + deck


# --------------------------------------------------------------------------- #
# Placeholder section properties for the minimal stick models
# --------------------------------------------------------------------------- #
# Nominal placeholder structural properties, quoted in the Imperial inch /
# pound-force set and converted with the rest of the deck. A clamped cantilever
# loaded only at its nodes is statically determinate, so the reaction loads sbeam
# recovers are independent of these values; they exist only to make the deck
# solvable. They are converted anyway because a deck that mixes an Imperial
# modulus with millimetre GRIDs is wrong on its face -- someone will read it, or
# swap in a real section, long before anyone re-derives that the reactions do not
# depend on it.
MAT1_E = 1.0e7      # psi (aluminium-ish placeholder)
MAT1_NU = 0.33      # dimensionless
PBAR_A = 1.0        # in^2
PBAR_I = 1.0        # in^4 (I1 = I2)
PBAR_J = 1.0        # in^4
