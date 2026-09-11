"""Deck-writing primitives shared by every bulk-data writer in this package.

One owner for *how a card is written* — number format, dust snapping, ``$``
comment wrapping, the ``$``-block stamp, and the placeholder section properties
a determinate stick model needs to be solvable. It also owns the load-output
contract's *statements* — the basis sentence, the ``-ULT`` marker, the per-case
factor and the solver unit set — which note 56 D-56.1 brought here when
``sbeam_bridge`` was dissolved.

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
from typing import List, Optional, Union

from ..constants import ULTIMATE_FACTOR
from ..models import (
    BodyLoadResult,
    ControlSurfaceLoadResult,
    TailChordResult,
    TailSpanResult,
    WingLoadResult,
)
from ..units import (
    Channel,
    DeliverableUnits,
    UnitSystem,
    canonical,
    deliverable_units,
)

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


# --------------------------------------------------------------------------- #
# The load-output contract: solver unit set, column label, per-case factor
# --------------------------------------------------------------------------- #
# Promoted here from ``sbeam_bridge`` with note 56 D-56.1, for the reason this
# module's docstring already gives for the format helpers: they were private
# names that siblings reached across the package to import through the
# underscore. ``_units`` had gone further and drifted into **four identical
# copies** -- ``sbeam_bridge``, ``balanced_deck``, ``roundtrip`` and
# ``lra_model`` -- each re-deciding which unit set a deck may use.
#
# D-56.1 dissolves ``sbeam_bridge`` and sends its report half to ``report/``, so
# a helper both halves need must have one owner or it becomes a fifth copy.
# The authority for *which* factor a case carries is still
# :mod:`sloads.safety_factors` (M4-8 / G-11); these only render what it decides.


def solver_units(system: UnitSystem) -> DeliverableUnits:
    """The **solver** unit set for ``system`` -- the only one a deck may use (D-19).

    Resolved per writer rather than passed around as a bare factor, so a caller
    cannot hand one file a different set from the file beside it: the writer's
    parameter is a *system*, and which units that means for a deck is decided
    here, once.
    """
    return deliverable_units(system, Channel.SOLVER)


def load_label(label: str, table_sf: Optional[float] = None) -> str:
    """The unit label for a load column in an export CSV.

    LIMIT is the project's only basis (note 49 OR-116) and every export file
    states it in the comment stamp, so a load column normally carries its plain
    unit and the row's ``SF`` cell states the factor that was not applied.

    ``table_sf`` is the table's **shared** basis from
    :func:`sloads.safety_factors.shared_basis_factor` -- ``1.0`` only when every
    row of the file is already ultimate, which earns the ``-ULT`` marker on the
    header, and ``None`` for a mixed file, whose header stays plain (OR-118a).

    **This used to be a guarded assumption and is now a computation.** The
    already-ultimate families -- ``engine_ultimate`` (23.367(a)(2)) and
    ``emergency`` (23.561(b)) -- reached no per-component CSV when this was
    written, and ``test_sbeam_bridge.py`` asserted it rather than trusting it.
    Note 44 OR-172 admitted 23.367 to the fin's critical set, an
    ``engine_ultimate`` case went into the v-tail chordwise and spanwise files
    beside five LIMIT ones, and the guard fired on the first run -- which is
    exactly what it was for. The mixed file keeps a plain header and states the
    rule in its stamp; only an all-ultimate file is marked.
    """
    return ult_label(label) if table_sf == 1.0 else label


def ult_label(label: str) -> str:
    """``label`` with the already-ultimate marker (note 49 OR-118)."""
    return f"{label}-ULT"


# Every exported force / moment / pressure magnitude is the calc's LIMIT value,
# unscaled (note 49 OR-116). The *case's* factor (``result.safety_factor``;
# 14 CFR 23.303 -> 1.5 by default, 1.0 for a case whose values are already
# ultimate) is stated beside the cards, never multiplied into them.
# ``SUITE_SF`` is the suite default constant (kept for the closure tests, which
# read it); :func:`case_sf` reads each result's own field directly (M4-13/M4-16).
SUITE_SF = ULTIMATE_FACTOR


def case_sf(result: Union[WingLoadResult, BodyLoadResult, TailChordResult,
                          TailSpanResult, ControlSurfaceLoadResult]) -> float:
    """The limit->ultimate factor to scale ``result``'s loads by (defect M4-7).

    Read off the result so each exported load set carries its own case's factor,
    rather than a flat suite-wide constant that would double-factor a case already
    at ultimate (``safety_factor = 1.0``). Every producer mints the field
    (M4-13), so the attribute is read directly — no ``getattr`` fallback that
    would mask an attribute rename (M4-16)."""
    return result.safety_factor


def basis_sentence(sf: float) -> str:
    """The per-subcase basis line every deck carries (note 49 OR-117).

    The deck is read by a program, so the factor it does not apply is stated
    where a person opening the file cannot miss it. A case computed already
    ultimate says so instead, and asks for nothing further (OR-118).
    """
    if sf == 1.0:
        return ("Loads are ALREADY ULTIMATE (SF=1.0) -- apply no further "
                "factor.")
    return (f"Loads are LIMIT. The 14 CFR 23.303 safety factor "
            f"SF={sf_str(sf)} is NOT applied here -- apply it in the sizing "
            f"analysis.")
