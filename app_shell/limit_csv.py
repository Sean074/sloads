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
``wing_load_rows``/``body_load_rows``, return the calc's floats with no
quantity kind); the table states its units in the headers and its basis in the
``Basis`` column -- **no** ``units_statement`` line, because this is the LIMIT
analysis-page channel, not a deliverable (``CONVENTIONS.md`` §3). The
sbeam/export channel (``sloads.export``) is untouched: it never converts here and
keeps its own writers.

**How many digits a cell keeps is the unit's** (design note 65, #302): each
converted value is read back from ``report.render.format_value`` under the
label its header shows, so the screen holds what the report would print while
the column stays numeric and sorts as numbers. The map names units, never a
digit count.

Pure functions, no Streamlit -- ``tests/test_limit_csv.py`` is the drift guard.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from sloads import UnitSystem, si_scalar_label, to_si_scalar
from sloads.models.results import TailChordResult
from sloads.report.render import format_value

_UnitMap = Dict[str, str]

# Column -> Imperial unit key of ``sloads.units._SCALAR_TO_SI``.
# Mxx/Myy/Mzz are all "lb-in" per ``net_loads.run`` (its ``LoadValue`` entries),
# matching WINGINER/NETLOADS; ``Case``/``MyyAxis``/``Basis`` are identity columns.
_WING_UNITS: _UnitMap = {
    "X": "in", "Y": "in", "Z": "in",
    "Fx": "lbf", "Fz": "lbf", "Sx": "lbf", "Sz": "lbf",
    "Mxx": "lb-in", "Myy": "lb-in", "Mzz": "lb-in",
}
_BODY_UNITS: _UnitMap = {
    "X": "in", "Fz": "lbf", "My_free": "lb-in", "Sz": "lbf", "Myy": "lb-in",
}


def _cell(value: object, unit: str, system: UnitSystem) -> object:
    """``value`` (Imperial ``unit``) in ``system``, kept to the digits its
    label prints at (note 65) and still a number. ``None`` is a structurally
    absent value -- a body-loads box row's running shear or moment (note 64
    D-64.2) -- and stays blank in every unit system rather than reading as zero."""
    if value is None:
        return ""
    return float(format_value(to_si_scalar(float(value), unit, system),  # type: ignore[arg-type]
                              si_scalar_label(unit, system)))


def _header(col: str, unit: str, system: UnitSystem) -> str:
    return f"{col} ({si_scalar_label(unit, system)})"


def _convert_rows(rows: Iterable[Dict[str, object]], units: _UnitMap,
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
                conv[_header(key, units[key], system)] = _cell(val, units[key], system)
            else:
                conv[key] = val
        out.append(conv)
    return out


# --------------------------------------------------------------------------- #
# Wing (``wing_load_rows``) and fuselage (``body_load_rows``) station tables
# --------------------------------------------------------------------------- #
def wing_limit_rows(rows: Iterable[Dict[str, object]], system: UnitSystem) -> List[Dict[str, object]]:
    """``wing_load_rows`` output converted to ``system`` with unit-suffixed headers."""
    return _convert_rows(rows, _WING_UNITS, system)


def body_limit_rows(rows: Iterable[Dict[str, object]], system: UnitSystem) -> List[Dict[str, object]]:
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
         f"LT25 ({lbf}, LIMIT)": _cell(r.lt25, "lbf", system),
         f"LT50 ({lbf}, LIMIT)": _cell(r.lt50, "lbf", system),
         **{f"PSI(X{i}) ({psi}, LIMIT)": _cell(s.psi, "psi", system)
            for i, s in enumerate(r.stations, start=1)}}
        for r in results
    ]
