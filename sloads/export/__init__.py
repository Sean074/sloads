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
- **The applied load set** — :mod:`sloads.export.sbeam_bridge`:
  :func:`applied_loads`, what is applied, where, for which case, at what factor,
  in one row shape for all six components. The station numbering
  (:func:`station_gid`, :func:`beam_station_gids`, :func:`tail_span_gid`, …)
  stays with it: an applied-load row states which station it is at, and the LRA
  model and the mass export tie to the same points, so they must agree.
- **Mass model** — :mod:`sloads.export.mass_cards`: :func:`conm2_fragment`,
  :func:`mass_check_deck` and :func:`inertia_only_cards`, the ``CONM2``/
  ``MASSSET`` export that gives sbeam an *independently parsed* mass model to
  check sloads' inertia loads against. Deliberately **not** re-exported at
  package level beyond these three: the inertia-only set is a comparison
  artifact, never a deliverable, and reaching it stays an explicit import.
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
from .sbeam_bridge import (
    NodalLoad,
    applied_load_csv,
    applied_loads,
    beam_station_gid,
    body_station_gids,
    station_gid,
    wing_nodal_loads,
    write_applied_load_csv,
)
from .workbook import build_workbook

__all__ = [
    "SBEAM_CID",
    "CardTotals",
    "NodalLoad",
    "Resultant",
    # The applied load set (sloads.export.sbeam_bridge)
    "applied_load_csv",
    "applied_loads",
    "beam_station_gid",
    "body_station_gids",
    "build_workbook",
    # Export-boundary closure gate (sloads.export.equilibrium)
    "card_totals",
    "closes",
    "deck_resultants",
    "parse_cards",
    "ref_aftmost_loaded",
    "ref_first_loaded",
    "resultant",
    # Station numbering -- one owner, because the applied set, the LRA model
    # and the mass export all state which station they are at.
    "station_gid",
    "to_force",
    "to_grid",
    "to_moment",
    "to_pressure",
    "wing_nodal_loads",
    "write_applied_load_csv",
]
