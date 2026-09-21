"""The analysis pages' LIMIT station tables, converted and unit-labelled.

The Wing/Fuselage/Tail Loads pages show a **LIMIT** station table (the
oracle-traceable numbers, the CLAUDE.md analysis-page carve-out). They are LIMIT
since note 49 OR-116 and the headers name the channel, not the basis (#192).
Before L-8i each page built its table and its CSV download inline from the raw
Imperial row dicts, so an SI session downloaded Imperial numbers under unit-less
headers while the table above was converted -- the units-defect class M4-20
already paid for. These builders are the single owner per page of (a) the
column -> Imperial-unit map, (b) the display conversion and (c) the
unit-suffixed header.

**The download half retired at the end of 0.8.4** (note 57 §8, the ``app_shell/``
slimming). ``wing_limit_csv``/``body_limit_csv``/``tail_limit_csv`` wrote those
per-page files and their only callers were ``app/views/``; #245 made the issue
package's ``data/`` the one tabular channel and #270 deleted the pages, so what
survives is the on-screen half. The row builders are unchanged: a download
channel that wants these numbers converts through the same owner rather than
re-deriving the map.

Decisions (L-8i review, 2026-08-16): the map stays per page (the sources,
``wing_load_rows``/``body_load_rows``, return pre-formatted strings with no
quantity kind); the table states its units in the headers and its basis in the
``Basis`` column -- **no** ``units_statement`` line, because this is the LIMIT
analysis-page channel, not a deliverable (``CONVENTIONS.md`` §3). The
sbeam/export channel (``sloads.export``) is untouched: it never converts here and
keeps its own writers.

Pure functions, no Streamlit -- ``tests/test_limit_csv.py`` is the drift guard.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from sloads import UnitSystem, si_scalar_label, to_si_scalar
from sloads.models.results import TailChordResult

_UnitMap = Dict[str, Tuple[str, int]]

# Column -> (Imperial unit key of ``sloads.units._SCALAR_TO_SI``, rounding).
# Mxx/Myy/Mzz are all "lb-in" per ``net_loads.run`` (its ``LoadValue`` entries),
# matching WINGINER/NETLOADS; ``Case``/``MyyAxis``/``Basis`` are identity columns.
_WING_UNITS: _UnitMap = {
    "X": ("in", 3), "Y": ("in", 3), "Z": ("in", 3),
    "Fx": ("lbf", 1), "Fz": ("lbf", 1), "Sx": ("lbf", 1), "Sz": ("lbf", 1),
    "Mxx": ("lb-in", 0), "Myy": ("lb-in", 0), "Mzz": ("lb-in", 0),
}
_BODY_UNITS: _UnitMap = {
    "X": ("in", 3), "Fz": ("lbf", 2), "My_free": ("lb-in", 1),
    "Sz": ("lbf", 2), "Myy": ("lb-in", 1),
}


def _header(col: str, unit: str, system: UnitSystem) -> str:
    return f"{col} ({si_scalar_label(unit, system)})"


def _convert_rows(rows: Iterable[Dict[str, str]], units: _UnitMap,
                  system: UnitSystem) -> List[Dict[str, object]]:
    """Copy of the row dicts with load columns converted and unit-suffixed keys.

    Never mutates the source rows -- the export paths keep the Imperial originals.
    Column order is preserved; identity columns keep their bare names.
    """
    out: List[Dict[str, object]] = []
    for r in rows:
        conv: Dict[str, object] = {}
        for key, val in r.items():
            if key in units:
                unit, nd = units[key]
                # A blank cell is a structurally absent value -- a body-loads box
                # row's running shear or moment (note 64 D-64.2) -- and stays
                # blank in every unit system rather than reading as zero.
                conv[_header(key, unit, system)] = (
                    "" if val == "" else round(to_si_scalar(float(val), unit, system), nd))
            else:
                conv[key] = val
        out.append(conv)
    return out


# --------------------------------------------------------------------------- #
# Wing (``wing_load_rows``) and fuselage (``body_load_rows``) station tables
# --------------------------------------------------------------------------- #
def wing_limit_rows(rows: Iterable[Dict[str, str]], system: UnitSystem) -> List[Dict[str, object]]:
    """``wing_load_rows`` output converted to ``system`` with unit-suffixed headers."""
    return _convert_rows(rows, _WING_UNITS, system)


def body_limit_rows(rows: Iterable[Dict[str, str]], system: UnitSystem) -> List[Dict[str, object]]:
    """``body_load_rows`` output converted to ``system`` with unit-suffixed headers."""
    return _convert_rows(rows, _BODY_UNITS, system)


# --------------------------------------------------------------------------- #
# Tail chordwise distributions (``TailChordResult``)
# --------------------------------------------------------------------------- #
def tail_limit_rows(results: Iterable[TailChordResult], system: UnitSystem) -> List[Dict[str, object]]:
    """One row per ``TailChordResult``: LT25/LT50 and the station pressures.

    Headers carry the unit **and** the LIMIT marker (this table has no ``Basis``
    column). PSI stations are numbered leading-edge first.
    """
    lbf = si_scalar_label("lbf", system)
    psi = si_scalar_label("psi", system)
    return [
        {"Component": r.component, "Condition": r.case,
         f"LT25 ({lbf}, LIMIT)": round(to_si_scalar(r.lt25, "lbf", system), 2),
         f"LT50 ({lbf}, LIMIT)": round(to_si_scalar(r.lt50, "lbf", system), 2),
         **{f"PSI(X{i}) ({psi}, LIMIT)": round(to_si_scalar(s.psi, "psi", system), 4)
            for i, s in enumerate(r.stations, start=1)}}
        for r in results
    ]
