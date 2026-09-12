"""Export bridges from SLOADS results to external structural tools.

**One solver artifact** (note 56): the full-span balanced free-free airplane
model on the loads reference axis — :mod:`sloads.export.lra_model` — plus the
``CONM2`` mass model beside it. The five families of *per-component* deck this
package used to ship (wing stick BDF, body, tail chordwise, tail spanwise,
control surface, each with a CSV companion) were deleted by **D-56.2**. They
were parallel model concepts sharing one ID space with the deliverable, none of
them the deliverable, and the GIDs the deliverable needed it was borrowing from
them.

- **The airplane model** — :mod:`sloads.export.lra_model`: the LRA beam with
  aero and inertia together, left and right cases, closing against ``nz × W``
  without the safety factor (gate G-OR-72). :mod:`sloads.export.lra_import`
  reads a user-defined LRA definition back in, so an imported beam and a
  generated one are the same contract at different vintages.
- **The applied load set** — **no longer here.** :func:`applied_loads`, its
  five row builders, the side-of-body internal loads and the station numbering
  that goes with them are report infrastructure, not a bridge to sbeam, and note
  56 D-56.1 moved them to :mod:`sloads.report.applied`, which is where their
  consumers already were. Import them from there, not from this package.
- **Mass model** — :mod:`sloads.export.mass_cards`: :func:`conm2_fragment` and
  :func:`mass_check_deck`, the ``CONM2``/``MASSSET`` export that gives sbeam an
  *independently parsed* mass model. Self-contained since note 56 D-56.6: one
  ``GRID`` per item at its own CG, zero offset, **unconnected by design** — read
  by a grid-point weight recovery, not by a stiffness solve. Deliberately not
  re-exported at package level: reaching them stays an explicit import.
- **Closure gate** — :mod:`sloads.export.equilibrium`: :func:`parse_cards`,
  :func:`deck_resultants` and :func:`closes`, the single owner of "re-derive a
  deck's Σ force / Σ moment from its own card text and check the claim its
  header makes". Every deck-closure check in the suite goes through it.
- **Case index, safety-factor table, gear report** — **no longer here.** They
  emit no bulk data and know nothing of a GRID; they are documents, and note 56
  D-56.1 moved them to :mod:`sloads.report.tables`, which is where their
  consumers already were. Import them from there, not from this package.

:mod:`sloads.export.pdf` (Step G8.6) also lives here but is **deliberately not
re-exported**: it is the one module in the codebase that runs a subprocess and
writes a temp directory (compiling the summary report's ``.tex``), so reaching it
stays an explicit ``from sloads.export.pdf import compile_pdf`` at the two call
sites that want it. See its docstring for the documented I/O exemption.
"""

from __future__ import annotations

from .coordinates import SBEAM_CID, to_force, to_grid, to_moment, to_pressure
from .equilibrium import (
    CardTotals,
    Resultant,
    card_totals,
    closes,
    deck_resultants,
    parse_cards,
    ref_aftmost_loaded,
    ref_first_loaded,
    resultant,
)
from .workbook import build_workbook

__all__ = [
    "SBEAM_CID",
    "CardTotals",
    "Resultant",
    "build_workbook",
    # Export-boundary closure gate (sloads.export.equilibrium)
    "card_totals",
    "closes",
    "deck_resultants",
    "parse_cards",
    "ref_aftmost_loaded",
    "ref_first_loaded",
    "resultant",
    "to_force",
    "to_grid",
    "to_moment",
    "to_pressure",
]
