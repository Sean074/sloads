"""An envelope point no loading can produce makes the envelope not valid (#309).

Owner ruling 2026-09-27: a limit or case that no loading of the weight database
reaches within every row's limits is flagged, never dropped or ballasted over.
No printed oracle tests reachability, so rule 2's second branch applies: every
gate here is an identity or a closure, with the #309 measurements pinned.

* **R-1** the reachable CG interval at a vertex weight is WTENV's own vertex,
  on both edges -- the test and the printed envelope are one construction.
* **R-2** the five fixtures, measured: one point is unreachable, ``baron_58``'s
  forward-regardless limit (as limit and as case), and nothing on
  ``ga6_normal``, whose CG1..CG3 need Appendix A's own ballast.
* **R-3** the least ballast is exact: it closes the point from the fuselage's
  end, and 1 % less does not.
* **R-4** a no-ballast witness is a loading: replayed as an entered loading it
  reproduces the point, mirrored pairs carried equally.
* **R-5** Baron's ``fwd gross`` is entered with no ballast, echoes its case and
  reaches the deck; ``fwd regardless`` does not, and is warned.
* **R-6** the search's own miss is named with a loading that reaches it.
* **R-7** the warning, the document and the owner agree.
"""

import dataclasses
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.mass_distribution import (
    BALLAST_CREDIBLE_FRACTION,
    case_loading_checks,
    cg_match_tolerance,
    derive_case_loadings,
    entered_loading,
    envelope_point_reach,
)
from sloads.models import CgCase, LoadingDefinition
from sloads.modules.balance import build_balanced_cases
from sloads.modules.weight_envelope import _fuselage_extent, loading_envelope
from sloads.report.oracle_sections import _cg_case_table
from sloads.units import UnitSystem
from sloads.validation import consistency_warnings

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = ("atr42_100", "baron_58", "concept_heavy", "concept_regional_jet",
             "ga6_normal")


def _project(name):
    return io.load_project(os.path.join(_ROOT, "examples", f"{name}.project.json"))


def _reach(project, name):
    return next(r for r in envelope_point_reach(project) if r.name == name)


@pytest.mark.parametrize("name", _EXAMPLES)
def test_the_reachable_interval_is_wtenvs_own_edges(name):
    """R-1: at each vertex weight the interval's ends are the two edges' vertices."""
    p = _project(name)
    fwd, aft = loading_envelope(p), loading_envelope(p, aft=True)
    for edge, side in ((fwd, "fwd_x"), (aft, "aft_x")):
        for v in edge:
            case = CgCase(name="probe", weight_lb=v.weight, xcg=v.station, zcg=v.waterline)
            probe = dataclasses.replace(p, weight=dataclasses.replace(
                p.weight, cg_cases=[case], envelope=None))
            r = envelope_point_reach(probe)[0]
            assert getattr(r, side) == pytest.approx(v.station, abs=1e-9), (name, v)
            assert r.reachable and r.ballast_lb == 0.0


def test_the_five_fixtures_have_one_unreachable_point():
    """R-2: measured on all five before any flag shipped (#309 scope item 1)."""
    bad = {(n, r.name) for n in _EXAMPLES for r in envelope_point_reach(_project(n))
           if not r.reachable}
    assert bad == {("baron_58", "forward regardless limit"),
                   ("baron_58", "fwd regardless")}
    r = _reach(_project("baron_58"), "fwd regardless")
    # The most-forward 4,200 lb loading: the airplane, unusable fuel and 100 lb
    # of nose baggage (#309's measurement), 2.85 in aft of the limit.
    assert r.fwd_x == pytest.approx(76.85, abs=0.005)
    assert r.ballast_lb is None


def test_appendix_a_is_reached_with_its_own_ballast():
    """R-2: the Appendix A airplane's gross weight (3,400 lb) is above its
    heaviest loading, so CG1 and CG2 need ballast by weight alone -- CG1's is
    the 78 lb WTENV prints (Appendix A; ``weight_envelope`` docstring) -- and
    every point is inside the credibility gate, as the no-ballast reading of the
    rule would have denied."""
    p = _project("ga6_normal")
    w_max = loading_envelope(p)[-1].weight
    cg1 = _reach(p, "CG1")
    assert cg1.fwd_x is None                                   # above every loading
    assert cg1.ballast_lb == pytest.approx(3400.0 - w_max, abs=1e-6)
    assert cg1.ballast_lb == pytest.approx(78.0, abs=0.5)
    for r in envelope_point_reach(p):
        assert r.reachable, r
        assert (r.ballast_fraction or 0.0) <= BALLAST_CREDIBLE_FRACTION


@pytest.mark.parametrize("name,point", [("ga6_normal", "CG3"), ("ga6_normal", "CG2"),
                                        ("atr42_100", "fwd light"),
                                        ("concept_regional_jet", "aft gross")])
def test_the_least_ballast_is_exact(name, point):
    """R-3: ``b`` closes the point with the ballast at the fuselage's end and
    the rest of the loading on an edge; ``0.99 b`` cannot."""
    p = _project(name)
    r = _reach(p, point)
    assert r.ballast_lb and r.ballast_lb > 0.0
    nose, tail = _fuselage_extent(p, p.weight.envelope)

    def span(b):
        probe = dataclasses.replace(p, weight=dataclasses.replace(
            p.weight, envelope=None, cg_cases=[CgCase(
                name="probe", weight_lb=r.weight_lb - b, xcg=r.xcg, zcg=0.0)]))
        q = envelope_point_reach(probe)[0]
        if q.fwd_x is None:
            return None
        w = r.weight_lb - b
        return ((w * q.fwd_x + b * nose) / r.weight_lb,
                (w * q.aft_x + b * tail) / r.weight_lb)

    lo, hi = span(r.ballast_lb)
    assert lo - 1e-6 <= r.xcg <= hi + 1e-6
    tight = span(0.99 * r.ballast_lb)
    assert tight is None or not (tight[0] <= r.xcg <= tight[1])


@pytest.mark.parametrize("name", _EXAMPLES)
def test_a_witness_is_a_loading_of_the_database(name):
    """R-4: every no-ballast witness replays through ``entered_loading`` to the
    point it claims, and a mirrored pair is carried equally."""
    p = _project(name)
    for r in envelope_point_reach(p):
        if r.fractions is None:
            continue
        ld = LoadingDefinition(aboard=list(r.fractions),
                               fractions={k: v for k, v in r.fractions.items() if v < 1.0})
        case = CgCase(name=r.name, weight_lb=r.weight_lb, xcg=r.xcg, zcg=0.0,
                      loading=ld)
        got = entered_loading(p.weight.items, case)
        assert got.weight_lb == pytest.approx(r.weight_lb, abs=1e-6), r
        assert abs(got.cg_x - r.xcg) <= cg_match_tolerance() + 1e-9, r
        for a in r.fractions:
            for b in r.fractions:
                ia = next(i for i in p.weight.items if i.name == a)
                ib = next(i for i in p.weight.items if i.name == b)
                if (a != b and ia.weight_lb == ib.weight_lb and ia.x == ib.x
                        and ia.z == ib.z and abs(ia.y) == abs(ib.y)):
                    assert r.fractions[a] == pytest.approx(r.fractions[b])


def test_baron_fwd_gross_is_entered_and_reaches_the_deck():
    """R-5: the [A] forward limit at gross is a loading with no ballast,
    its case echoes it, and the deck assembles at it; ``fwd regardless`` is
    not a loading, reaches no deck, and is warned as limit and case."""
    p = _project("baron_58")
    case = next(c for c in p.weight.cg_cases if c.name == "fwd gross")
    assert case.loading is not None and case.loading.ballast is None
    got = entered_loading(p.weight.items, case)
    assert got.weight_lb == pytest.approx(5500.0, abs=0.5)
    assert got.cg_x == pytest.approx(78.3, abs=1e-3)
    assert got.cg_z == pytest.approx(case.zcg, abs=0.01)          # its own waterline
    assert all(c.ok for c in case_loading_checks(p))
    cgs = {c.cg for c in build_balanced_cases(p)}
    assert "fwd gross" in cgs and "fwd regardless" not in cgs
    codes = [(w.code, w.message.split("'")[1]) for w in consistency_warnings(p)
             if w.code == "envelope_point_unreachable"]
    assert codes == [("envelope_point_unreachable", "forward regardless limit"),
                     ("envelope_point_unreachable", "fwd regardless")]


def test_baron_database_is_its_a_source():
    """R-5: nose baggage 300 lb at +15 and rear baggage 400 lb at +150
    (``examples/baron_58.sources.md``, grade [A]); every loading entered
    before the correction carries the nose hold at 0.5."""
    p = _project("baron_58")
    rows = {it.name: it for it in p.weight.items}
    assert (rows["Nose baggage"].weight_lb, rows["Nose baggage"].x) == (300, 15)
    assert (rows["Rear baggage"].weight_lb, rows["Rear baggage"].x) == (400, 150)
    for c in p.weight.cg_cases:
        if c.loading is not None and "Nose baggage" in c.loading.aboard and c.name != "fwd gross":
            assert c.loading.fractions["Nose baggage"] == 0.5, c.name


def test_a_case_the_search_misses_is_named_with_a_loading():
    """R-6: ``fwd gross`` as it shipped before #309 -- no loading, the
    unsourced waterline 100.0 -- is one the whole-row search cannot produce
    (it asks for 12 % ballast); the warning names a no-ballast loading."""
    p = _project("baron_58")
    cases = [dataclasses.replace(c, loading=None, zcg=100.0) if c.name == "fwd gross"
             else c for c in p.weight.cg_cases]
    q = dataclasses.replace(p, weight=dataclasses.replace(p.weight, cg_cases=cases))
    target = next(c for c in cases if c.name == "fwd gross")
    assert not derive_case_loadings(q, [target])[0].derivable
    missed = [w for w in consistency_warnings(q) if w.code == "case_loading_search_missed"]
    assert len(missed) == 1 and "'fwd gross'" in missed[0].message
    r = _reach(q, "fwd gross")
    assert r.fractions is not None and r.ballast_lb == 0.0
    assert "with no ballast" in missed[0].message


def test_a_point_below_the_minimum_flight_weight_says_so():
    p = _project("baron_58")
    light = CgCase(name="too light", weight_lb=3000.0, xcg=80.0, zcg=95.0)
    q = dataclasses.replace(p, weight=dataclasses.replace(
        p.weight, cg_cases=[*p.weight.cg_cases, light]))
    msg = next(w.message for w in consistency_warnings(q)
               if w.code == "envelope_point_unreachable" and "'too light'" in w.message)
    assert "less than the minimum flight weight" in msg


@pytest.mark.parametrize("name", _EXAMPLES)
def test_the_warning_and_the_document_agree(name):
    """R-7: the page and the 2.2 case table name the same points, from one owner."""
    p = _project(name)
    bad = [r.name for r in envelope_point_reach(p) if not r.reachable]
    warned = [w.message.split("'")[1] for w in consistency_warnings(p)
              if w.code == "envelope_point_unreachable"]
    assert warned == bad
    note = _cg_case_table(p, UnitSystem.IMPERIAL).note
    if bad:
        assert "makes the envelope not valid" in note
        assert all(f"'{n}'" in note for n in bad)
    else:
        assert "Every one is such a loading." in note


if __name__ == "__main__":
    import traceback

    runs = []
    for key, fn in sorted(globals().items()):
        if not key.startswith("test_") or not callable(fn):
            continue
        marks = getattr(fn, "pytestmark", [])
        params = next((m for m in marks if m.name == "parametrize"), None)
        if params is None:
            runs.append((key, fn, ()))
        else:
            for vals in params.args[1]:
                args = vals if isinstance(vals, tuple) else (vals,)
                runs.append((f"{key}{list(args)}", fn, args))
    failed = 0
    for label, fn, args in runs:
        try:
            fn(*args)
            print(f"PASS {label}")
        except Exception:
            failed += 1
            print(f"FAIL {label}")
            traceback.print_exc()
    print(f"\n{len(runs) - failed}/{len(runs)} passed")
    sys.exit(1 if failed else 0)
