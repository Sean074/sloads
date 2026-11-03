"""Design note 76 (#422, #423): the payload corners built to note 75 §2's rule,
the limit points' real loadings, and the fuel vector -- gates G-76.1 to G-76.7.

References: 14 CFR 25.321(b)(3), loads "for any practicable distribution of
disposable load within the operating limitations"; Lomax, *Structural Loads
Analysis for Commercial Transport Aircraft* (1996) §14.1 p233 (MZFW: zero
usable fuel), Eq 14.1 p234 (payload = MZFW - OEW), §11.4 pp199-202 (MZFW at the
forward CG, payload end-loaded) and §10.11 p183 / Fig 10.21 p184 (fuel usage
and wing bending).
"""

import math
import os

import pytest

from sloads import io
from sloads.cg_cases import (
    MZFW_CASE_NAMES,
    flight_cases,
    ground_cases,
    max_takeoff_weight,
    max_zero_fuel_weight,
    seed_flight_cases,
    seed_landing_cases,
)
from sloads.mass_distribution import (
    _corner_rows,
    cg_match_tolerance,
    derive_case_loadings,
    fuel_vector,
    limit_point_loading,
)
from sloads.report.content import Units, weight_cg_plot_data
from sloads.units import UnitSystem
from sloads.validation import _wtenv_stations, wtenv_fwd_cg_limit_line

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_MZFW_FIXTURES = ("atr42_100", "atr42_300_seed", "baron_58", "concept_regional_jet")


def _load(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _corners(project):
    return [c for c in seed_flight_cases(project)[0] if c.name in MZFW_CASE_NAMES]


def _independent_extreme(project, weight_lb, fuel_lb, aft_first):
    """The rows' extreme, filled here by station without the solver: units
    taken whole from one end, the last one part-filled -- the vertex of the
    linear programme ``place_payload`` falls back to."""
    base, tanks, payload = _corner_rows(project)
    cap = math.fsum(it.weight_lb for it in tanks)
    w = math.fsum(it.weight_lb for it in base) + fuel_lb
    m = (math.fsum(it.weight_lb * it.x for it in base)
         + (fuel_lb / cap if cap else 0.0) * math.fsum(it.weight_lb * it.x for it in tanks))
    need = min(weight_lb - w, math.fsum(it.weight_lb for it in payload))
    for it in sorted(payload, key=lambda it: it.x, reverse=aft_first):
        take = min(it.weight_lb, max(need, 0.0))
        need -= take
        w += take
        m += take * it.x
    return w, m / w


def test_the_solver_reproduces_the_baron_corners_337_entered():
    """G-76.1: the corners #337 entered by hand come out of the solver."""
    project = _load("baron_58")
    seeded = {c.name: c for c in seed_flight_cases(project)[0]}
    for name, (w, x) in {"mzfw fwd": (5270.0, 79.61), "mzfw aft": (5270.0, 86.00),
                         "full fuel aft": (5500.0, 85.37)}.items():
        assert seeded[name].weight_lb == pytest.approx(w, abs=0.01), name
        assert seeded[name].xcg == pytest.approx(x, abs=0.011), name
    # The full-fuel forward corner is `fwd gross` itself (5,500 lb on 78.30),
    # so the skip rule does not write it twice.
    assert "full fuel fwd" not in seeded
    found = limit_point_loading(project, 5500.0, seeded["fwd gross"].xcg)
    assert found is not None and found[1] == "full fuel + least payload"


@pytest.mark.parametrize("name", _MZFW_FIXTURES)
def test_every_corner_is_on_its_limit_or_at_the_rows_extreme(name):
    """G-76.2: no ballast, no fuel at MZFW, at most two part-filled payload
    rows, and the CG on the limit or at the extreme computed independently."""
    project = _load(name)
    stations = _wtenv_stations(project)
    aft, fwd_line = stations["Aft gross station"], wtenv_fwd_cg_limit_line(project)
    _, tanks, _ = _corner_rows(project)
    tank_names = {it.name for it in tanks}
    mzfw, mtow = max_zero_fuel_weight(project), max_takeoff_weight(project)
    corners = _corners(project)
    assert corners, name
    for case in corners:
        ld = case.loading
        assert ld is not None and ld.ballast is None, case.name
        # At most two part-filled units; a mirrored pair is one unit, its two
        # rows sharing one fraction.
        partial = {round(f, 9) for n, f in ld.fractions.items() if n not in tank_names}
        assert len(partial) <= 2, case.name
        edge = "aft" if case.name.endswith("aft") else "fwd"
        limit = aft if edge == "aft" else fwd_line(case.weight_lb)
        if case.name.startswith("mzfw"):
            assert not tank_names & set(ld.aboard), case.name
            fuel = 0.0
        else:
            fuel = math.fsum(it.weight_lb for it in tanks) * ld.fractions.get(
                next(iter(tank_names)), 1.0)
        if abs(case.xcg - limit) > cg_match_tolerance():
            w, x = _independent_extreme(project, mzfw if fuel == 0.0 else mtow, fuel,
                                        aft_first=edge == "aft")
            assert case.weight_lb == pytest.approx(w, abs=0.01), case.name
            assert case.xcg == pytest.approx(x, abs=0.011), case.name


@pytest.mark.parametrize("name", _MZFW_FIXTURES)
def test_every_limit_point_keeps_its_place_and_carries_the_first_real_loading(name):
    """G-76.3: each limit point keeps its seeded weight and station, and when a
    rule of D-76.3 reaches it, its loading is that rule's, with no ballast."""
    project = _load(name)
    seeded = seed_flight_cases(project)[0] + seed_landing_cases(project)[0]
    for case in seeded:
        if case.name in MZFW_CASE_NAMES or case.name == "min weight":
            continue
        found = limit_point_loading(project, case.weight_lb, case.xcg)
        if found is None:
            continue
        assert case.loading == found[0].loading, (name, case.name)
        assert case.loading.ballast is None, (name, case.name)


def test_the_regional_jet_gross_cases_carry_no_ballast():
    """G-76.3 / G-76.4: the RJ's `fwd gross` takes full fuel and the least
    payload; `_HELD_UNTIL_422` is gone, and the clamped-NHAA ceiling it was
    held for is re-measured in ``test_balance``."""
    project = _load("concept_regional_jet")
    cases = {c.name: c for c in flight_cases(project) + ground_cases(project)}
    found = limit_point_loading(project, 33000.0, cases["fwd gross"].xcg)
    assert found is not None and found[1] == "full fuel + least payload"
    assert cases["fwd gross"].loading.ballast is None


@pytest.mark.parametrize("name", ("ga6_normal", "concept_heavy"))
def test_a_project_with_no_mzfw_is_untouched(name):
    """G-76.5: no MZFW, no corner and no limit-point loading -- the Appendix A
    airplane's cases are D-27's search, as before."""
    project = _load(name)
    assert max_zero_fuel_weight(project, required=False) == 0.0
    assert _corners(project) == []
    for case in seed_flight_cases(project)[0] + seed_landing_cases(project)[0]:
        assert limit_point_loading(project, case.weight_lb, case.xcg) is None


@pytest.mark.parametrize("name", _MZFW_FIXTURES + ("ga6_normal",))
def test_a_fuel_vector_runs_from_zero_fuel_to_its_case(name):
    """G-76.6: the vector ends on its case's own loading, starts at
    the zero-fuel loading, rises monotonically in weight, and is one point when
    the case carries no fuel."""
    project = _load(name)
    for case in flight_cases(project) + ground_cases(project):
        path = fuel_vector(project, case)
        ld = derive_case_loadings(project, [case])[0]
        if not ld.derivable:
            assert path == []
            continue
        assert path[-1][0] == pytest.approx(ld.weight_lb, rel=1e-12), case.name
        assert path[-1][1] == pytest.approx(ld.cg_x, abs=1e-9), case.name
        fuel = math.fsum(it.weight_lb for it in ld.items if it.usable_fuel)
        if fuel <= 1e-6:
            assert len(path) == 1, case.name
            continue
        assert path[0][0] == pytest.approx(ld.weight_lb - fuel, rel=1e-12), case.name
        assert all(b[0] > a[0] for a, b in zip(path, path[1:])), case.name


def test_the_baron_aft_gross_vector_is_its_mzfw_payload_plus_fuel():
    """G-76.6's example: `aft gross` is the MZFW payload plus 230 lb of fuel,
    so its vector starts at MZFW."""
    project = _load("baron_58")
    case = next(c for c in flight_cases(project) if c.name == "aft gross")
    path = fuel_vector(project, case)
    assert path[0][0] == pytest.approx(5270.0, abs=0.5)
    assert path[-1][0] == pytest.approx(5500.0, abs=0.5)


@pytest.mark.parametrize("system", list(UnitSystem))
def test_the_weight_cg_figure_draws_one_vector_per_fuelled_case(system):
    """G-76.7: one dotted series per case that carries fuel, in either unit
    system -- the figure the GUI page and both reports draw."""
    project = _load("atr42_100")
    data = weight_cg_plot_data(project, Units(system))
    drawn = {s.name for s in data.series if s.name.startswith("Fuel vector, ")}
    fuelled = {f"Fuel vector, {c.name}" for c in project.weight.cg_cases
               if len(fuel_vector(project, c)) > 1}
    assert fuelled and drawn == fuelled
    assert all(s.style == "dotted" for s in data.series if s.name in drawn)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
