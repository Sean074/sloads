"""Design note 75 D-75.8 - D-75.11 (#424): standard weight definitions, no
structural-reserve credit, and the fuel basis stated in every artifact --
gates G-75.6 to G-75.9.

References: 14 CFR 23.25(b) as DOT/FAA/AR-96/46 §4.3.1.2 p4-3 quotes it (the
minimum weight is *not more than* empty + minimum crew + half an hour of fuel);
14 CFR 23.343 (61 FR 5144, 1996) and 25.343 (a structural reserve fuel *may* be
selected, and then owes a zero-wing-fuel case at 90 % n / +2.25 g and 85 %
gust); Lomax, *Structural Loads Analysis for Commercial Transport Aircraft*
(1996) §14.1 p233 (MZFW: "zero usable fuel"). McMaster's Appendix A airplane
carries "30 MIN FUEL 71.0" among its minimum-weight items (Ref. 1 App. A p136).
"""

import glob
import os

import pytest

from sloads import io
from sloads.cg_cases import flight_cases, max_zero_fuel_weight
from sloads.mass_distribution import derive_case_loadings, fuel_basis
from sloads.models.enums import MassItemKind
from sloads.report.methods import bundle_stamps, methods_statement
from sloads.units import UnitSystem
from sloads.validation import consistency_warnings

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_PATHS = sorted(glob.glob(os.path.join(_EXAMPLES, "*.project.json")))
_CODE = "minimum_fuel_in_zero_fuel_weight"


def _load(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _fires(project):
    return _CODE in {w.code for w in consistency_warnings(project)}


@pytest.mark.parametrize("path", _PATHS, ids=os.path.basename)
def test_only_the_appendix_a_airplane_keeps_minimum_fuel(path):
    """G-75.6: the reserve folded into the tanks on every fixture but ga6,
    whose 71 lb half hour is the oracle's own minimum-weight item."""
    project = io.load_project(path)
    fuel = [it for it in project.weight.items
            if it.kind == MassItemKind.MINIMUM and it.usable_fuel]
    if os.path.basename(path) == "ga6_normal.project.json":
        assert [(it.name, it.weight_lb) for it in fuel] == [("30 min fuel", 71.0)]
    else:
        assert fuel == []
    assert not _fires(project)


def test_the_guard_fires_on_minimum_fuel_under_an_mzfw():
    """G-75.7: a MINIMUM fuel row is quiet without an MZFW (the Appendix A
    airplane) and warned, by name, once one is stated."""
    project = _load("ga6_normal")
    assert not _fires(project)
    project.weight.max_zero_fuel_weight_lb = 2913.0
    (w,) = [w for w in consistency_warnings(project) if w.code == _CODE]
    assert "'30 min fuel'" in w.message


@pytest.mark.parametrize("path", _PATHS, ids=os.path.basename)
def test_every_zero_fuel_case_carries_no_usable_fuel(path):
    """G-75.8: an `mzfw` case flies with zero usable fuel (Lomax p233) and no
    heavier than MZFW."""
    project = io.load_project(path)
    zero = [c for c in flight_cases(project) if c.name.startswith("mzfw")]
    if not zero:
        pytest.skip("no zero-fuel case")
    mzfw = max_zero_fuel_weight(project)
    for ld in derive_case_loadings(project, zero):
        assert ld.derivable, ld.name
        assert not any(it.usable_fuel for it in ld.items), (path, ld.name)
        assert ld.weight_lb <= mzfw + 1e-6, (path, ld.name)


@pytest.mark.parametrize("path", _PATHS, ids=os.path.basename)
def test_every_artifact_states_the_fuel_basis(path):
    """G-75.9: the three sentences are in the methods statement, so in the
    report, METHODS.txt and both stamps (CSV and deck), in either unit system."""
    project = io.load_project(path)
    basis = fuel_basis(project)
    assert len(basis.lines) == 3
    assert basis.lines[0].startswith("Minimum flight weight:")
    assert basis.lines[1].startswith("Structural reserve fuel: not selected")
    assert basis.lines[2].startswith("Zero-fuel case:")
    for system in UnitSystem:
        text = methods_statement(project, system=system)
        assert "FUEL BASIS: " + " ".join(basis.lines) in text
        for stamp in bundle_stamps(project, system):
            flat = " ".join(ln[2:] for ln in stamp.splitlines())
            assert "FUEL BASIS:" in flat and "Structural reserve fuel: not selected" in flat


def test_the_oracle_states_its_rule_and_its_assumption():
    """G-75.9, the owner's rule for the oracle: ga6 says where its minimum weight
    comes from and that the zero-fuel case is not run, assumed not critical."""
    basis = fuel_basis(_load("ga6_normal"))
    assert basis.minimum_fuel == ["30 min fuel"]
    assert "23.25(b)(3)" in basis.lines[0]
    assert basis.zero_fuel_cases == []
    assert basis.lines[2].startswith("Zero-fuel case: not run; assumed not critical.")


def test_a_fixture_with_zero_fuel_cases_names_them():
    basis = fuel_basis(_load("baron_58"))
    assert basis.minimum_fuel == []
    assert "no fuel is credited" in basis.lines[0]
    assert basis.zero_fuel_cases == ["mzfw aft", "mzfw fwd"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
