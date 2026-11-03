"""Design note 75 (#337): the required crew is in the zero-fuel weight, and the
Baron's payload cases are built to MZFW and full fuel at both limits -- gates
G-75.1 to G-75.5.

References: 14 CFR 23.25(b)(2), "the weight of the required minimum crew
(assuming a weight of 170 pounds for each crewmember)", as DOT/FAA/AR-96/46
§4.3.1.2 p4-3 quotes it; Lomax, *Structural Loads Analysis for Commercial
Transport Aircraft* (1996) §14.1 p233 (MZFW) and Eq 14.1 p234 (maximum design
payload = MZFW - OEW).
"""

import glob
import math
import os
from dataclasses import replace

import pytest

from sloads import io
from sloads.cg_cases import max_takeoff_weight, max_zero_fuel_weight
from sloads.mass_distribution import entered_loading, loading_kind_totals
from sloads.migrations import MIGRATIONS
from sloads.models.enums import MassItemKind
from sloads.validation import consistency_warnings, wtenv_cg_limits, wtenv_fwd_cg_limit_at_weight

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_CODES = ("minimum_crew_missing", "crew_not_minimum")


def _load(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _codes(project):
    return {w.code for w in consistency_warnings(project)} & set(_CODES)


@pytest.mark.parametrize("path", sorted(glob.glob(os.path.join(_EXAMPLES, "*.project.json"))),
                         ids=os.path.basename)
def test_every_shipped_fixture_carries_its_crew_in_the_minimum_weight(path):
    """G-75.1: every fixture tags a crew row of kind minimum, and no other."""
    project = io.load_project(path)
    assert _codes(project) == set()
    crew = [it for it in project.weight.items if it.required_crew]
    assert crew and all(it.kind == MassItemKind.MINIMUM for it in crew)


def test_each_warning_fires_on_the_database_it_names():
    """G-75.2: no crew tag at all, then the Baron's old combined row tagged crew
    while it is still discretionary."""
    project = _load("baron_58")
    untagged = [replace(it, required_crew=False) for it in project.weight.items]
    project.weight.items = untagged
    assert _codes(project) == {"minimum_crew_missing"}

    combined = [replace(it, name="Pilot & front passenger", weight_lb=340.0,
                        kind=MassItemKind.DISCRETIONARY, required_crew=True)
                if it.name == "Pilot" else it for it in untagged]
    project.weight.items = combined
    assert _codes(project) == {"minimum_crew_missing", "crew_not_minimum"}


def test_the_baron_minimum_flight_weight_carries_the_pilot():
    """G-75.3: 4,100 lb at 78.36 with nobody aboard became 4,270 lb at 78.22."""
    totals = {t.name: t for t in loading_kind_totals(_load("baron_58"))}
    minimum = next(t for name, t in totals.items() if name.startswith("Minimum flight weight"))
    assert math.isclose(minimum.weight_lb, 4270.0, abs_tol=1e-6)
    assert math.isclose(minimum.xcg, 78.22, abs_tol=0.005)


def _payload_extreme(project, weight_lb, fuel_full, *, forward):
    """The most forward (or aft) CG at ``weight_lb`` the payload rows reach: a
    station-order fill of the non-fuel discretionary rows on top of the minimum
    flight weight, plus every consumable full when ``fuel_full``. Independent
    of the fixture's own loadings."""
    items = project.weight.items
    base = [it for it in items if it.kind in (MassItemKind.EMPTY, MassItemKind.MINIMUM)]
    if fuel_full:
        base += [it for it in items if it.kind == MassItemKind.DISCRETIONARY and it.consumable]
    w = math.fsum(it.weight_lb for it in base)
    m = math.fsum(it.weight_lb * it.x for it in base)
    payload = sorted((it for it in items
                      if it.kind == MassItemKind.DISCRETIONARY and not it.consumable),
                     key=lambda it: it.x, reverse=not forward)
    left = weight_lb - w
    for it in payload:
        take = min(it.weight_lb, left)
        m += take * it.x
        left -= take
    assert left <= 1e-9, "the payload rows cannot reach the weight"
    return m / weight_lb


def test_the_baron_corners_sit_on_the_limit_or_on_the_rows_extreme():
    """G-75.4: each note 75 §2 corner holds its weight, and its CG is the limit
    where the rows reach it and the rows' extreme where they do not."""
    project = _load("baron_58")
    cases = {c.name: c for c in project.weight.cg_cases}
    mzfw, mtow = max_zero_fuel_weight(project), max_takeoff_weight(project)
    _, aft = wtenv_cg_limits(project)
    corners = [  # (case, weight, fuel full, forward?)
        ("mzfw aft", mzfw, False, False),
        ("mzfw fwd", mzfw, False, True),
        ("fwd gross", mtow, True, True),
        ("full fuel aft", mtow, True, False),
    ]
    for name, weight, full, forward in corners:
        case = cases[name]
        assert math.isclose(case.weight_lb, weight, abs_tol=0.01), name
        limit = wtenv_fwd_cg_limit_at_weight(project, weight) if forward else aft
        extreme = _payload_extreme(project, weight, full, forward=forward)
        reach = max(limit, extreme) if forward else min(limit, extreme)
        assert case.xcg == pytest.approx(reach, abs=0.01), name
    # The two the rows cannot reach, with the gaps the sources file states.
    assert cases["mzfw fwd"].xcg - wtenv_fwd_cg_limit_at_weight(project, mzfw) == pytest.approx(2.07, abs=0.01)
    assert aft - cases["full fuel aft"].xcg == pytest.approx(0.63, abs=0.01)


def test_the_baron_landing_cases_are_the_mzfw_payloads_plus_fuel():
    """G-75.4: the max-landing cases carry the MZFW payload of their side, plus
    fuel to the landing weight."""
    project = _load("baron_58")
    cases = {c.name: c for c in project.weight.cg_cases}
    for landing, zero_fuel in (("aft max landing", "mzfw aft"), ("fwd max landing", "mzfw fwd")):
        lc, zc = cases[landing].loading, cases[zero_fuel].loading
        fuel = {n: f for n, f in lc.fractions.items() if n.startswith("Fuel")}
        assert set(lc.aboard) - set(fuel) == set(zc.aboard)
        assert {n: f for n, f in lc.fractions.items() if n not in fuel} == zc.fractions
        loading = entered_loading(project.weight.items, cases[landing])
        assert math.isclose(loading.weight_lb, 5400.0, abs_tol=0.5)


def test_the_v82_hop_is_an_identity():
    """G-75.5: ``required_crew`` is additive, and the hop infers nothing from a name."""
    d = {"schema_version": 82, "weight": {"items": [{"name": "Pilot", "weight_lb": 170.0,
                                                     "kind": "minimum"}]}}
    assert MIGRATIONS[82](dict(d)) == d


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
