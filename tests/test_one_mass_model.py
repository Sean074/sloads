"""Design note 63's gates for #289 -- the one-model step.

The case's D-25 loading is the mass state of every inertia load: WINGINER,
NETLOADS, ``body_loads`` and the balanced deck read one mass model per case,
and the wing's own mass fields are gone from ``wing_mass``. The gates here are
note 63 §4's as ruled for #289 (R-63.4): gate 1 (the oracle lock and the stated
body correction), G-63.1 (one model per case), the identity half of G-63.3a
(the run key beside the slot id), G-63.4 (the migrated fixtures) and G-63.5
(the body per case). The variants step's gates (G-63.2, G-63.3, the rest of
G-63.3a) are #292's.

Reference: ``docs/25_notes/63_one_mass_model_note.md``; Ref 1 Ch 13 p93
(WINGINER's panel and concentrated masses, per side) and Ch 15 p103 (the body
beam carries what the wing does not).
"""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperial_baseline import EXAMPLES  # noqa: E402

from sloads import io  # noqa: E402
from sloads import mass_distribution as md  # noqa: E402
from sloads.cg_cases import flight_cases, ground_cases  # noqa: E402
from sloads.models import MassComponent, WingCarriage  # noqa: E402
from sloads.modules import body_loads  # noqa: E402
from sloads.modules.net_loads import build_net_loads  # noqa: E402
from sloads.modules.select import build_critical, default_envelope  # noqa: E402
from sloads.modules.wing_inertia import build_wing_inertia, resolve_mass_case  # noqa: E402

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = "ga6_normal.project.json"
_BARON = "baron_58.project.json"


def _project(example: str):
    return io.load_project(os.path.join(_EXAMPLES, example))


# --------------------------------------------------------------------------- #
# G-63.1 -- one model, per case
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_every_delivered_wing_case_distributes_its_own_loadings_wing_parts(example):
    """**G-63.1.** For every wing case WINGINER delivers: the case names its
    mass state, that state's WING parts are what the distribution carries --
    ``2 x (panel + Σ points)`` to ``RECONCILE_REL_TOL`` -- and the published
    point loads are the state's POINT rows by name and weight. The #257
    statement therefore reads "0 lb apart" on every case of every fixture, or
    this fails first.
    """
    p = _project(example)
    results = build_wing_inertia(p)
    assert results
    for r in results:
        assert r.mass_state, r.case
        state = md.wing_mass_state(p, r.case_ref.cg or None)
        assert r.mass_state == state.label, r.case
        tie = md.wing_state_tie(state)
        assert tie.ok, f"{example} {r.case}: {tie.detail}"
        assert [pl.name for pl in r.point_loads] == [m.name for m in state.point_masses]
        for pl, m in zip(r.point_loads, state.point_masses):
            assert pl.fx == pytest.approx(r.nx * m.weight_lb, rel=1e-12), pl.name
        # The strips integrate the state's panel inside WINGINER.BAS's own
        # +-1 % band (lines 730-880); the identity above is on the state. Read
        # off the drag distribution, ``fx = nx * w`` -- the vertical one also
        # carries the unit-roll term on an ACRL case.
        if r.nx:
            strips = math.fsum(s.fx for s in r.stations) / r.nx
            assert strips == pytest.approx(state.panel_weight_lb, rel=0.0101), r.case


@pytest.mark.parametrize("example", EXAMPLES)
def test_every_flight_case_has_one_mass_state_and_the_body_reads_it_too(example):
    """**G-63.1 / D-63.8.** Each FLIGHT case resolves to one state; its WING
    parts and its body parts partition the loading exactly, and the beam the
    body integrates for it is that partition's body half."""
    p = _project(example)
    for case in flight_cases(p):
        state = md.wing_mass_state(p, case.name)
        if state.source == "database":
            continue                              # the Baron's two, named by validation
        total = math.fsum(it.weight_lb for it in state.items)
        beam = math.fsum(s.weight_lb for s in md.fuselage_beam_stations(p, state.loading))
        assert state.wing_weight_lb + beam == pytest.approx(total, rel=1e-9), case.name
        assert total == pytest.approx(state.loading.weight_lb, rel=1e-9), case.name


# --------------------------------------------------------------------------- #
# Gate 1 -- the oracle lock, and the body correction stated
# --------------------------------------------------------------------------- #
def test_ga6_runs_every_wing_case_at_the_appendix_a_panel_with_no_point_mass():
    """**Gate 1.** On the Appendix A airplane every wing case's state is a
    searched loading whose WING parts are the 330 lb "Wing, outboard" row and
    nothing else: panel 165 lb per side, no POINT row, so WINGINER, NETLOADS,
    the deck's wing sets and CONM2 are the pre-v67 bytes (the digests hold the
    proof; this is the reason they can)."""
    p = _project(_GA)
    assert md.panel_weight(p) == 165.0 and p.wing_mass.panel_weight_override_lb is None
    for r in build_wing_inertia(p):
        state = md.wing_mass_state(p, r.case_ref.cg or None)
        assert state.source == "searched", r.case
        assert state.panel_weight_lb == 165.0 and not state.point_masses, r.case
        assert not r.point_loads
    net = build_net_loads(p)
    phaa = next(r for r in net.wing_net if r.case == "PHAA")
    # Appendix A "Net Loads, Case 22 PHAA" p222 -- the oracle, unmoved.
    assert math.isclose(phaa.stations[0].sz, 5837, rel_tol=2e-3, abs_tol=2.0)
    assert math.isclose(phaa.stations[0].mxx, 455555, rel_tol=2e-3, abs_tol=2.0)


#: Gate 1's stated correction (R-63.1): the body mass each GA6 fuselage
#: condition integrates, at the condition's own CG case. Until v67 all four
#: integrated the whole data base, 3,070 lb.
_GA6_BODY_MASS = {
    "MAX DOWN LOAD ON WING": ("CG2", 3070.0),   # six aboard less one, 248 lb ballast in
    "AFT DOWN BENDING": ("CG3", 2470.0),
    "AFT UP BENDING": ("CG1", 3070.0),          # unchanged
    "GREATEST NZ": ("CG4", 1733.0),             # a 2,063 lb airplane
}


def test_ga6_body_loads_integrate_each_conditions_own_body_mass():
    """**Gate 1 / D-63.8.** The Ch 15 beam carries the condition's loading."""
    p = _project(_GA)
    results = body_loads.build_body_loads(p)
    assert {r.case for r in results} == set(_GA6_BODY_MASS)
    for r in results:
        cg, body = _GA6_BODY_MASS[r.case]
        assert r.case_ref.cg == cg, r.case
        assert r.mass_state == f"loading '{cg}' (searched)", r.case
        integrated = math.fsum(s.fz for s in r.stations if s.source == "mass")
        # ``fz = -nz * w`` per station: the mass integrated is the sum over w.
        got = -integrated / _nz_of(p, r)
        assert got == pytest.approx(body, abs=0.5), (r.case, got)


def _nz_of(p, r):
    vn = {pt.case: pt for pt in default_envelope(p).vn}
    cond = next(c for c in body_loads.critical_fuselage_conditions(p) if c.label == r.case)
    return vn[cond.case].nz


# --------------------------------------------------------------------------- #
# G-63.3a (identity half) -- the run key beside the slot id
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_the_run_key_names_the_point_and_the_slot_id_stays_the_deliverable(example):
    """**G-63.3a, identity half (D-63.11).** Every condition SELECT takes from
    a V-n point carries the point's manoeuvre label and configuration beside
    its CG and altitude; within one component no two conditions share a run
    key (one physical condition, one id); and WINGINER/NETLOADS deliver each
    W id under the same run key SELECT minted it with -- the slot id is the
    deliverable's number, the run key the condition's name, and neither is
    the V-n integer."""
    p = _project(example)
    envelope = default_envelope(p)
    vn = {pt.case: pt for pt in envelope.vn}
    critical = build_critical(p, envelope)
    seen = {}
    for c in critical.conditions:
        ref = c.case_ref
        assert ref is not None, c.label
        if c.case is None:
            continue
        pt = vn[c.case]
        assert (ref.run, ref.config, ref.cg, ref.altitude_ft) == \
            (pt.condition, pt.config, pt.cg, pt.altitude_ft), c.label
        assert ref.run_key == f"{pt.condition}, {pt.cg}, {pt.altitude_ft:.0f} ft, {pt.config}"
        # Within the wing family a run key names one slot (D-62.8's coincidence
        # rule); the empennage families legitimately derive several conditions
        # from one point (the balancing pair and the unsymmetrical case from
        # BAL A), so the uniqueness claim is the wing's.
        if c.component == "wing":
            key = ref.run_key
            assert key not in seen, (key, seen[key], ref.case_id)
            seen[key] = ref.case_id
    by_id = {c.case_ref.case_id: c.case_ref for c in critical.conditions if c.case_ref}
    for r in build_net_loads(p).wing_net:
        ref = r.case_ref
        assert ref.run and ref.config, r.case
        if ref.case_id in by_id and by_id[ref.case_id].cg == ref.cg:
            assert ref.run_key == by_id[ref.case_id].run_key, r.case


def test_a_hand_entered_wing_case_resolves_its_mass_state_in_the_stated_order():
    """**D-63.6.** Explicit ``cg`` wins; else the referenced V-n point's CG
    case; else SELECT's condition of the same label; else the database."""
    from sloads.models import WingLoadCase
    p = _project(_GA)
    assert resolve_mass_case(p, WingLoadCase("PHAA", cg="CG4")) == "CG4"
    assert resolve_mass_case(p, WingLoadCase("PHAA", case=53)) == "CG3"      # GUST -C at CG3
    assert resolve_mass_case(p, WingLoadCase("PHAA", nz=-3.8, nx=0.6)) == "CG2"
    assert resolve_mass_case(p, WingLoadCase("STORE DROP", nz=-2.0, nx=0.1)) is None
    state = md.wing_mass_state(p, None)
    assert state.source == "database" and state.label.startswith("item database")
    missing = md.wing_mass_state(p, "no such case")
    assert missing.source == "database" and "not a FLIGHT weight/CG case" in missing.label


# --------------------------------------------------------------------------- #
# G-63.4 -- the migrated fixtures
# --------------------------------------------------------------------------- #
#: Σ WING-carried item weight per fixture after the v67 hop **and** the hand
#: corrections of D-63.2/D-63.4 (both sides), with what the corrections moved:
#: nothing on the GA6 and the RJ; the Baron's centreline fuel-system row split
#: per side (no change in total); the ATR's engines and nacelles per side and
#: its 9,174 lb fuel-to-gross and 700 lb reserve rows into per-side wing tank
#: rows (+6,074 lb: the 41 % ``wing_fraction`` slice was 3,800); the heavy's
#: 5,500 lb fuel row into per-side tank rows (+4,300 lb: the slice was 1,200).
_WING_ITEM_WEIGHT = {
    "atr42_100.project.json": 2650.0 + 1780.0 + 600.0 + 9174.0 + 700.0,
    "baron_58.project.json": 2941.0,
    "concept_heavy.project.json": 1800.0 + 5500.0,
    "concept_regional_jet.project.json": 4200.0,
    "ga6_normal.project.json": 330.0,
}

#: The starboard POINT rows per fixture -- WINGINER's per-side point-mass list
#: at every state that carries them all -- and their total, which on the Baron
#: is exactly the 1,190.5 lb its four lumped ``concentrated`` entries summed to.
_POINT_ROWS = {
    "atr42_100.project.json": (4, 890.0 + 300.0 + 4587.0 + 350.0),
    "baron_58.project.json": (9, 1190.5),
    "concept_heavy.project.json": (1, 2750.0),
    "concept_regional_jet.project.json": (0, 0.0),
    "ga6_normal.project.json": (0, 0.0),
}


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_migrated_fixture_carries_its_wing_mass_in_the_items_alone(example):
    """**G-63.4.** No ``concentrated``, no override, every off-centreline WING
    row POINT and every centreline one PANEL, the WING weight as pinned, and
    the per-side point list what the ``concentrated`` entries used to sum to."""
    p = _project(example)
    assert not hasattr(p.wing_mass, "concentrated") and not hasattr(p.wing_mass, "panel_weight_lb")
    assert p.wing_mass.panel_weight_override_lb is None
    wing = md.wing_parts(p.weight.items, p)
    assert math.fsum(it.weight_lb for it in wing) == pytest.approx(_WING_ITEM_WEIGHT[example])
    for it in p.weight.items:
        if it.component is MassComponent.WING:
            assert it.carriage is (WingCarriage.POINT if it.y else WingCarriage.PANEL), it.name
    state = md.database_mass_state(p)
    n, total = _POINT_ROWS[example]
    assert len(state.point_masses) == n
    assert math.fsum(m.weight_lb for m in state.point_masses) == pytest.approx(total)
    assert all(m.y > 0 for m in state.point_masses)
    assert md.wing_state_tie(state).ok
    assert p.migration_notes == [], "a saved v67 file has nothing left to say"


# --------------------------------------------------------------------------- #
# G-63.5 -- the body per case
# --------------------------------------------------------------------------- #
def test_the_barons_fwd_light_beam_integrates_the_loadings_body_weight():
    """**G-63.5.** ``baron_58`` "fwd light" is an entered loading (D-25): the
    pilot and front passenger aboard, no fuel. The beam derived for it weighs
    that loading's body parts -- 4,440 lb less the 2,221 lb of wing rows --
    and not the data base's 3,049."""
    p = _project(_BARON)
    case = next(c for c in ground_cases(p) if c.name == "fwd light")
    (loading,) = md.derive_case_loadings(p, [case])
    assert loading.entered
    beam = md.fuselage_beam_stations(p, loading)
    body = math.fsum(s.weight_lb for s in beam)
    wing = math.fsum(it.weight_lb for it in md.wing_parts(loading.items, p))
    assert body == pytest.approx(loading.weight_lb - wing, rel=1e-9)
    assert body != pytest.approx(math.fsum(s.weight_lb for s in md.fuselage_beam_stations(p)))
    assert wing == pytest.approx(2221.0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
