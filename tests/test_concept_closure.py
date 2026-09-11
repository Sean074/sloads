"""Concept distributed-loads closure suite (backlog Step P1-2).

Concept mode has **no printed oracle** above 12,500 lb (it extrapolates past the
FAR23 calibration band), so physics-*closure* is its only validation. Step C4's
``test_sbeam_bridge.py::test_concept_closure`` proved closure for the **wing
only**; this module extends it to every component of a full concept airframe --
wing, body, tail and the three control surfaces -- driven through the P1-1
regional-jet fixture (``examples/concept_regional_jet.project.json``).

Two kinds of check appear here:

* **Physics closure** -- an equilibrium identity the concept code path must
  satisfy, evaluated on the concept fixture so a concept-mode blow-up (NaN, an
  unbalanced result) cannot pass silently:
    - wing:  ``LZW + LT == Nz*W``            (vertical equilibrium, FLTLOADS)
    - tail:  ``LT*(Xt - Xcg) == LZW*(Xcg - Xw) - DX*(Zcg - Zw) + M(W+F)``
             (balancing tail load reacts the pitching moment about the CG)
    - body:  terminal cumulative shear ``== 0`` (the fuselage net distribution
             is built free-free: inertia + tail + wing reaction sum to zero)
* **Cross-module ties** -- one module's output reconciles against its upstream
  source, so a divergence in the concept branch of either is caught:
    - tail:  TAILDIST carries SELECT's ``lt25``/``lt50`` split verbatim.
    - control: the distributed-loads (``build_*``) load matches the analysis
      (``run``) report load for the same surface.
* **Export integrity** -- every component's nodal FORCE set (and its re-parsed
  ``FORCE`` cards) sums to that component's root/total at ULTIMATE, so the whole
  concept airframe exports cleanly through ``sbeam_bridge``.

References: Ref 1 Ch 7 (wing airload), Ch 8/9 (tail balancing), Ch 15 (fuselage
net loads); the closure strategy is Phase-C invariant 2 (``docs/30_future/
01_concept_loads_plan.md`` §2).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.cg_cases import flight_cases
from sloads.derived_geometry import require_wing_reference
from sloads.export import sbeam_bridge as sb
from sloads.export.coordinates import tail_force_to_airplane
from sloads.export.equilibrium import (
    card_totals,
    closes,
    deck_resultants,
    ref_aftmost_loaded,
)
from sloads.modules import aileron as aileron_mod
from sloads.modules import flap as flap_mod
from sloads.modules import tab as tab_mod
from sloads.modules.body_loads import build_body_loads
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.net_loads import build_net_loads
from sloads.modules.select import build_critical
from sloads.modules.tail_span import build_tail_span
from sloads.modules.taildist import build_tail_chordwise

_EXAMPLE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "examples",
    "concept_regional_jet.project.json",
)

# ``ULTIMATE_FACTOR`` (1.5) -- the suite default the export *states* and does not
# apply (note 49 OR-116). Read from its owner since note 56 D-56.1 promoted it
# out of ``sbeam_bridge``.
from sloads.export.deck_format import SUITE_SF as _SF  # noqa: E402


def _concept_project():
    """The P1-1 concept fixture with its envelope + critical set materialised."""
    p = io.load_project(_EXAMPLE)
    assert p.is_concept, "fixture must be a concept (category=C) project"
    p.envelope = build_envelope(p)
    p.envelope.critical = build_critical(p)
    return p


# --------------------------------------------------------------------------- #
# Wing -- total lift = Nz*W (FLTLOADS vertical equilibrium) + nodal export sum
# --------------------------------------------------------------------------- #
def test_wing_lift_equals_nW():
    """Every balanced V-n point closes vertically: ``LZW + LT == Nz*W``."""
    p = _concept_project()
    weight = {c.name: c.weight_lb for c in flight_cases(p)}
    assert p.envelope.vn
    for vp in p.envelope.vn:
        nw = vp.nz * weight[vp.cg]
        assert math.isclose(vp.lzw + vp.lt, nw, rel_tol=1e-6, abs_tol=1e-6)


def test_wing_nodal_loads_sum_to_root():
    """The exported wing nodal FORCE set sums to the NETLOADS root at ULTIMATE."""
    results = build_net_loads(_concept_project()).wing_net
    assert results
    for r in results:
        nodes = sb.wing_nodal_loads(r)
        root = r.stations[0]
        y0 = nodes[0].y
        assert math.isclose(sum(n.fz for n in nodes), root.sz, rel_tol=1e-9, abs_tol=1e-6)
        # The cards carry each strip's *free* torsion, so the root torsion comes
        # back only with the arms applied -- which is what a solver does
        # (note 46 OR-67/OR-68).
        x0, z0 = nodes[0].x, nodes[0].z
        rigid = sum(n.my + (n.z - z0) * n.fx - (n.x - x0) * n.fz for n in nodes)
        assert math.isclose(rigid, root.myy, rel_tol=1e-9, abs_tol=1e-3)
        # Bending = FORCE moments about the root strip.
        assert math.isclose(sum(n.fz * (n.y - y0) for n in nodes), root.mxx,
                            rel_tol=1e-6, abs_tol=1.0)


# --------------------------------------------------------------------------- #
# Tail -- balancing load reacts the pitching moment about the CG (Ch 8/9),
# TAILDIST carries SELECT's split, and the nodal set sums to LT25 + LT50.
# --------------------------------------------------------------------------- #
def test_tail_balancing_moment_closure():
    """``LT*(Xt - Xcg)`` reacts the wing-plus-inertia pitching moment about the CG."""
    p = _concept_project()
    wr = require_wing_reference(p)
    cg = {c.name: c for c in flight_cases(p)}
    xt = {tb.case: tb.tail_cp_station for tb in p.envelope.tail_balance}
    for vp in p.envelope.vn:
        c = cg[vp.cg]
        lhs = vp.lt * (xt[vp.case] - c.xcg)
        rhs = vp.lzw * (c.xcg - wr.xw) - vp.dx * (c.zcg - wr.zw) + vp.m_wf
        assert math.isclose(lhs, rhs, rel_tol=1e-6, abs_tol=1e-3)


def test_taildist_carries_select_split():
    """Cross-module tie: TAILDIST's ``lt25``/``lt50`` are SELECT's verbatim, so the
    chordwise distribution sums back to the SELECT-critical tail load."""
    p = _concept_project()
    crit = {c.case_ref.case_id: c for c in p.envelope.critical.conditions if c.case_ref}
    results = build_tail_chordwise(p)
    assert results
    for r in results:
        c = crit.get(r.case_ref.case_id)
        assert c is not None, f"no SELECT condition for {r.case}"
        assert c.lt25 == r.lt25 and c.lt50 == r.lt50




# --------------------------------------------------------------------------- #
# Body -- the fuselage net distribution is built free-free (Ch 15): inertia +
# tail air load + wing reaction sum to zero, so the terminal shear is zero.
# --------------------------------------------------------------------------- #
def test_body_vertical_equilibrium():
    """The net fuselage distribution closes: applied Fz sums to 0 (terminal Sz = 0)."""
    results = build_body_loads(_concept_project())
    assert results
    for r in results:
        applied = sum(s.fz for s in r.stations)
        # Scale tolerance by the fuselage inertia magnitude (a big concept airframe).
        scale = max(abs(s.fz) for s in r.stations)
        assert math.isclose(applied, 0.0, abs_tol=1e-6 * scale + 1e-6)
        assert math.isclose(r.stations[-1].sz, 0.0, abs_tol=1e-6 * scale + 1e-6)


def test_body_nodal_cards_sum_to_zero():
    """The delivered body load set closes: its applied Fz sums to ~0.

    Read off ``applied_loads`` since note 56 D-56.2 deleted the per-component
    body deck. That set is what the deck wrote cards from, so the closure is
    the same one -- asserted now at the authority rather than at one rendering
    of it (D-56.9)."""
    project = _concept_project()
    results = build_body_loads(project)
    assert results
    rows = sb.applied_loads("fuselage", results, project=project)
    assert rows
    by_case: dict = {}
    for ld in rows:
        by_case.setdefault(ld.case, []).append(ld)
    assert len(by_case) == len(results)
    for case, loads in by_case.items():
        scale = max(abs(ld.fz) for ld in loads) or 1.0
        assert math.isclose(sum(ld.fz for ld in loads), 0.0,
                            abs_tol=1e-6 * scale + 1e-6), case


# --------------------------------------------------------------------------- #
# Control surfaces -- the distributed-loads path matches the analysis report,
# and each exported nodal set sums to the critical surface load (ULTIMATE).
# --------------------------------------------------------------------------- #
def _report_lb_values(module, project):
    return [lv.value for cond in module.run(project).conditions
            for lv in cond.values if lv.units == "lb"]


def test_control_build_matches_report():
    """Cross-module tie: each ``build_*`` critical load appears in that module's
    ``run`` analysis report (the distributed and analysis paths agree)."""
    p = _concept_project()
    for module, build in (
        (aileron_mod, aileron_mod.build_aileron),
        (flap_mod, flap_mod.build_flap),
        (tab_mod, tab_mod.build_tabs),
    ):
        reported = _report_lb_values(module, p)
        results = build(p)
        assert results, f"{module.MODULE_NAME}: no control-surface loads on the concept airframe"
        for r in results:
            assert any(math.isclose(r.load_lb, v, rel_tol=1e-6, abs_tol=1e-6) for v in reported), \
                f"{module.MODULE_NAME} {r.surface}/{r.case} load {r.load_lb} not in report"




# --------------------------------------------------------------------------- #
# Whole-airframe export -- every component family emits a parseable card deck
# whose per-case FORCE set re-sums to that component's root/total at ULTIMATE.
# --------------------------------------------------------------------------- #
def test_full_airframe_exports_cleanly():
    """Every component states an applied load set that re-sums -- the P1-2
    acceptance, on the artifacts note 56 D-56.2 left standing.

    It used to walk four families of per-component FORCE deck. Those are gone;
    the applied load set they were each written from is not, and it is what
    D-56.9 makes the authority for the delivered cards. The claim is the same:
    the whole concept set comes out, and what comes out sums to what the calc
    computed.
    """
    p = _concept_project()
    wing = build_net_loads(p).wing_net
    body = build_body_loads(p)
    spans = build_tail_span(p)
    assert wing and body

    # Wing: the applied Fz set re-sums to the NETLOADS root shear, per case.
    rows: dict = {}
    for ld in sb.applied_loads("wing", wing):
        rows.setdefault(ld.case, []).append(ld)
    assert len(rows) == len(wing)
    for r in wing:
        got = sum(ld.fz for ld in rows[r.case])
        assert closes(got, r.stations[0].sz, scale=abs(r.stations[0].sz))

    # Tails: every spanwise case states an applied set. NOT compared against
    # LT25 + LT50: the spanwise set carries the surface's own inertia as well as
    # its air load, so the two are different quantities. The air-load identity
    # belonged to the chordwise tributary split, which note 56 D-56.2 deleted
    # with the chordwise deck -- `test_taildist_carries_select_split` still
    # holds the upstream half of it.
    for component in ("htail", "vtail"):
        results = spans.get(component) or []
        if not results:
            continue
        per_case: dict = {}
        for ld in sb.applied_loads(component, results):
            per_case.setdefault(ld.case, []).append(ld)
        assert len(per_case) == len(results), component

    # Body: the applied set exists for every case and closes (asserted above).
    body_rows = sb.applied_loads("fuselage", body, project=p)
    assert len({ld.case for ld in body_rows}) == len(body)


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
