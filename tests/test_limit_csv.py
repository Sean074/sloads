"""The analysis pages' LIMIT station tables follow the unit toggle and label units (L-8i).

Before L-8i the Wing/Fuselage/Tail Loads pages built their table and their LIMIT
download inline from the raw Imperial row dicts: an SI session read Imperial
numbers under unit-less headers. ``app_shell/limit_csv.py`` is now the single
owner per page of the column->unit map, the conversion and the header. This is
the drift guard:

1. **Imperial in, Imperial out** -- the Imperial table's numbers are the row
   builders' own strings, headers ``(in)``/``(lbf)``/``(lb-in)``/``(psi)``.
2. **SI converts** -- every load cell equals ``to_si_scalar`` of the Imperial
   one, headers ``(mm)``/``(N)``/``(N·m)``/``(kPa)``.
3. **No bare load header** in either system: every non-identity column states
   its unit; the tail table also states LIMIT in-band (it has no ``Basis``
   column); the wing/fuselage ``Basis`` column still says ``LIMIT``.

The CSV half of the module retired with ``app/views/`` at the end of 0.8.4 (note
57 §8): the three ``*_limit_csv`` builders had no surviving caller once #245 made
the issue package's ``data/`` the one tabular channel. The assertions moved to
the rows themselves rather than going with the writer -- they were always about
the conversion and the header, and the CSV was one way of reading them.
"""

import math
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest  # noqa: E402

from app_shell.limit_csv import (  # noqa: E402
    body_limit_rows,
    tail_limit_rows,
    wing_limit_rows,
)
from sloads import UnitSystem  # noqa: E402
from sloads import io as sloads_io  # noqa: E402
from sloads.modules.body_loads import body_load_rows, build_body_loads  # noqa: E402
from sloads.modules.net_loads import build_net_loads, wing_load_rows  # noqa: E402
from sloads.modules.taildist import build_tail_chordwise  # noqa: E402
from sloads.units import to_si_scalar  # noqa: E402

_GA = os.path.join(_ROOT, "examples", "ga6_normal.project.json")
_IDENTITY = {"Case", "MyyAxis", "Basis", "Component", "Condition", "Region"}
_IMPERIAL = {"in", "lbf", "lb-in", "psi"}
_SI = {"mm", "N", "N·m", "kPa"}


def _project():
    return sloads_io.load_project(_GA)


def _unit_of(header: str) -> str:
    """``"Fz (lbf)"`` -> ``"lbf"``; ``"LT25 (lbf, LIMIT)"`` -> ``"lbf"``."""
    assert header.endswith(")"), header
    inner = header[header.rindex("(") + 1:-1]
    return inner.split(",")[0].strip()


def _check_headers(headers, expected_units, limit_in_band: bool):
    for h in headers:
        if h in _IDENTITY:
            continue
        assert "(" in h, f"bare load header {h!r}"
        assert _unit_of(h) in expected_units, h
        if limit_in_band:
            assert h.endswith(", LIMIT)"), h


# --------------------------------------------------------------------------- #
# Wing
# --------------------------------------------------------------------------- #
def test_wing_imperial_table_is_the_row_builder_bit_for_bit():
    rows = wing_load_rows(build_net_loads(_project()).wing_net)
    parsed = wing_limit_rows(rows, UnitSystem.IMPERIAL)
    _check_headers(parsed[0].keys(), _IMPERIAL, limit_in_band=False)
    assert {r["Basis"] for r in parsed} == {"LIMIT"}
    for src, out in zip(rows, parsed):
        assert math.isclose(float(out["Sz (lbf)"]), float(src["Sz"]), rel_tol=0, abs_tol=0.05)
        assert math.isclose(float(out["Mxx (lb-in)"]), float(src["Mxx"]), abs_tol=0.5)
        assert out["Case"] == src["Case"] and out["MyyAxis"] == src["MyyAxis"]


def test_wing_si_table_converts_every_load_column():
    rows = wing_load_rows(build_net_loads(_project()).wing_net)
    parsed = wing_limit_rows(rows, UnitSystem.SI)
    _check_headers(parsed[0].keys(), _SI, limit_in_band=False)
    for src, out in zip(rows, parsed):
        for col, unit, hdr in (("Y", "in", "Y (mm)"), ("Sz", "lbf", "Sz (N)"),
                               ("Mxx", "lb-in", "Mxx (N·m)")):
            want = to_si_scalar(float(src[col]), unit, UnitSystem.SI)
            assert math.isclose(float(out[hdr]), want, rel_tol=1e-3, abs_tol=0.6), (col, want, out[hdr])


def test_the_wing_table_states_one_row_per_station():
    rows = wing_load_rows(build_net_loads(_project()).wing_net)
    assert len(wing_limit_rows(rows, UnitSystem.SI)) == len(rows) > 0


# --------------------------------------------------------------------------- #
# Fuselage
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("system", [UnitSystem.IMPERIAL, UnitSystem.SI])
def test_body_table_labels_and_converts(system):
    rows = body_load_rows(build_body_loads(_project()))
    parsed = body_limit_rows(rows, system)
    expected = _IMPERIAL if system == UnitSystem.IMPERIAL else _SI
    _check_headers(parsed[0].keys(), expected, limit_in_band=False)
    assert {r["Basis"] for r in parsed} == {"LIMIT"}
    myy_hdr = "Myy (lb-in)" if system == UnitSystem.IMPERIAL else "Myy (N·m)"
    boxes = 0
    for src, out in zip(rows, parsed):
        if src["Region"] == "box":
            # A box row's running load is structurally absent (note 64 D-64.2)
            # and stays blank in every unit system rather than reading as zero.
            assert src["Myy"] == "" and out[myy_hdr] == ""
            boxes += 1
            continue
        want = to_si_scalar(float(src["Myy"]), "lb-in", system)
        assert math.isclose(float(out[myy_hdr]), want, rel_tol=1e-3, abs_tol=0.06)
    assert boxes, "ga6_normal carries stations inside its wing box"


# --------------------------------------------------------------------------- #
# Tail chordwise
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("system", [UnitSystem.IMPERIAL, UnitSystem.SI])
def test_tail_table_labels_units_and_limit_in_band(system):
    results = build_tail_chordwise(_project())
    assert results
    parsed = tail_limit_rows(results, system)
    expected = _IMPERIAL if system == UnitSystem.IMPERIAL else _SI
    _check_headers(parsed[0].keys(), expected, limit_in_band=True)
    lbf = "lbf" if system == UnitSystem.IMPERIAL else "N"
    psi = "psi" if system == UnitSystem.IMPERIAL else "kPa"
    for src, out in zip(results, parsed):
        assert out["Component"] == src.component and out["Condition"] == src.case
        assert math.isclose(float(out[f"LT25 ({lbf}, LIMIT)"]),
                            to_si_scalar(src.lt25, "lbf", system), rel_tol=1e-3, abs_tol=0.006)
        assert math.isclose(float(out[f"PSI(X1) ({psi}, LIMIT)"]),
                            to_si_scalar(src.stations[0].psi, "psi", system), rel_tol=1e-3, abs_tol=6e-5)


def test_no_results_give_no_rows():
    assert wing_limit_rows([], UnitSystem.SI) == []
    assert tail_limit_rows([], UnitSystem.SI) == []


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        marks = getattr(t, "pytestmark", [])
        params = [m for m in marks if m.name == "parametrize"]
        arg_sets = params[0].args[1] if params else [None]
        for a in arg_sets:
            try:
                t(a) if params else t()
                print(f"PASS {t.__name__} {a if params else ''}")
            except Exception:
                failed += 1
                print(f"FAIL {t.__name__} {a if params else ''}")
                traceback.print_exc()
    print(f"\n{failed} failed")
    sys.exit(1 if failed else 0)
