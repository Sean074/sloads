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

import dataclasses
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
    # The ATR re-entered at #260 (2026-09-21): wing 3,500 lb, engines,
    # propellers and nacelles per side, the same 9,874 lb of fuel.
    "atr42_100.project.json": 3500.0 + 1780.0 + 620.0 + 640.0 + 9174.0 + 700.0,
    "baron_58.project.json": 2941.0,
    "concept_heavy.project.json": 1800.0 + 5500.0,
    "concept_regional_jet.project.json": 4200.0,
    "ga6_normal.project.json": 330.0,
}

#: The starboard POINT rows per fixture -- WINGINER's per-side point-mass list
#: at every state that carries them all -- and their total, which on the Baron
#: is exactly the 1,190.5 lb its four lumped ``concentrated`` entries summed to.
_POINT_ROWS = {
    "atr42_100.project.json": (5, 890.0 + 310.0 + 320.0 + 4587.0 + 350.0),
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


# --------------------------------------------------------------------------- #
# #292 -- the variants step (design note 63 D-63.5 / D-63.7; G-63.2, G-63.3,
# the rest of G-63.3a)
# --------------------------------------------------------------------------- #
def _variants(p):
    from sloads.modules.wing_variants import wing_variant_table
    envelope = default_envelope(p)
    return envelope, wing_variant_table(p, envelope)


@pytest.mark.parametrize("example", ["atr42_100.project.json", "baron_58.project.json"])
def test_zero_fuel_removes_the_relief_and_the_sign_is_right(example):
    """**G-63.2.** On the two wing-fuel fixtures, for the PHAA slot, net root
    bending at the zero-fuel state exceeds net root bending at the full-fuel
    state **at equal air load**; on NHAA the inequality reverses. Read off
    the variant table's inertia half, so the comparison is the relief alone."""
    p = _project(example)
    _, table = _variants(p)
    full = "full fuel aft" if example.startswith("atr42") else "aft gross"
    for slot, sign in (("PHAA", +1.0), ("NHAA", -1.0)):
        rows = {v.cg: v for v in table.by_slot(slot)}
        zero, fuel = rows["mzfw aft"], rows[full]
        assert zero.mass_state_case == "mzfw aft" and fuel.mass_state_case == full
        # The relief: at the same nz the zero-fuel inertia moment is smaller in
        # magnitude, so air + inertia is larger in the slot's own sign.
        net_zero = zero.air_root_mxx + zero.inertia_root_mxx * (fuel.nz / zero.nz)
        assert sign * (zero.air_root_mxx + zero.inertia_root_mxx * (fuel.nz / zero.nz)) > 0
        assert sign * (net_zero - (zero.air_root_mxx + fuel.inertia_root_mxx)) > 0, (
            example, slot, zero.inertia_root_mxx, fuel.inertia_root_mxx)
        assert abs(zero.inertia_root_mxx) < abs(fuel.inertia_root_mxx), (example, slot)


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_variant_table_is_complete_and_the_slot_is_delivered_at_its_governing_run(example):
    """**G-63.3.** Slots × FLIGHT cases rows -- every slot the family criterion
    can fill within a case has a row at that case; exactly one governing
    per slot; SELECT's delivered condition for the slot *is* the governing
    run; the balanced deck's ``$`` header names that run key and its case is
    that CG case (the subcase's mass set is the governing run's loading)."""
    from sloads.modules.balance import build_balanced_cases
    from sloads.modules.select import AIR_PICK_SLOTS, wing_slot_picks

    p = _project(example)
    envelope, table = _variants(p)
    assert table.variants, table.reason
    by_case = {pt.case: pt for pt in envelope.vn}
    # Completeness: the family pick within each case is a row, and so is
    # every air pick at its own case (#294) -- the search is the same
    # criterion within the case, so the two sets normally coincide.
    expected = set()
    for k in flight_cases(p):
        vn_k = [pt for pt in envelope.vn if pt.cg == k.name]
        for label, _, pt in wing_slot_picks(p, vn_k):
            if pt is not None:
                expected.add((label, k.name, pt.case))
    for label, _, pt in wing_slot_picks(p, envelope.vn):
        if pt is not None:
            expected.add((label, pt.cg, pt.case))
    assert {(v.slot, v.cg, v.case) for v in table.variants} == expected
    # Exactly one governing per slot, on a row of that slot; the air-pick
    # slots keep their air pick, without exception (#294: before, a slot
    # whose air pick the coincidence rule had emptied was "assessed and not
    # delivered", which is how NNZ left the Baron's deck).
    governing = table.governing()
    assert set(governing) == set(table.slots)
    for slot, g in governing.items():
        assert sum(1 for v in table.by_slot(slot) if v.governing) == 1, slot
        if slot in AIR_PICK_SLOTS:
            assert g.air_pick, slot
    # The delivered condition is the governing run; a slot the table
    # assessed and the deck omits is a coincidence (D-62.8) with a delivered
    # slot at that very case, never a loss.
    delivered = {c.label: c for c in build_critical(p, envelope).conditions
                 if c.component == "wing"}
    for slot, g in governing.items():
        if slot not in delivered:
            assert any(c.case == g.case for c in delivered.values()), (slot, g.case)
    for slot, c in delivered.items():
        g = governing[slot]
        assert c.case == g.case, (slot, c.case, g.case)
        assert c.case_ref is not None and c.case_ref.cg == g.cg
        assert c.case_ref.run_key == g.run_key, slot
        assert by_case[c.case].cg == g.cg
    # The deck: header run key and case both the governing run's.
    for case in build_balanced_cases(p):
        if case.label in delivered and not case.hand:
            g = governing[case.label]
            assert case.case_ref.run_key == g.run_key, case.label
            assert case.cg == g.cg, (case.label, case.cg, g.cg)
            assert case.vn_case == g.case


@pytest.mark.parametrize("example", EXAMPLES)
def test_no_w_id_is_carried_by_two_runs_and_the_ga6_delivers_its_air_picks(example):
    """**G-63.3a, the rest.** Across a full run no two ``CaseRef``s share a
    run key with different loads and no W id is carried by more than one
    run; on ``ga6_normal`` the governing run of every slot has the run key of
    SELECT's air pick (the Appendix A set reproduced), and ``select.air_picks``
    asserts the six Appendix A points unchanged."""
    from sloads import registry
    from sloads.modules.select import air_picks

    p = _project(example)
    envelope, table = _variants(p)
    seen_key = {}
    seen_id = {}
    for result in registry.run_all_modules(p):
        for cond in result.conditions:
            ref = cond.case_ref
            if ref is None or ref.component != "wing" or not ref.run:
                continue
            if not ref.case_id.startswith("W-"):
                continue
            key = ref.run_key
            loads = tuple((lv.key, round(lv.value, 6)) for lv in cond.values)
            # One run key, one W id -- and the W id names one run key.
            assert seen_key.setdefault(key, ref.case_id) == ref.case_id, (key, ref.case_id)
            assert seen_id.setdefault(ref.case_id, key) == key, (ref.case_id, key)
    picks = {c.label: c for c in air_picks(p, envelope)}
    if example == "ga6_normal.project.json":
        for slot, g in table.governing().items():
            assert g.air_pick and g.case == picks[slot].case, (slot, g.run_key)
        # The six Appendix A runs by name and CG case; their CL/V are
        # ``tests/test_select.py``'s, on the three-altitude project.
        expect = {"PHAA": ("STALL +N", "CG2"), "PLAA": ("MAN D", "CG2"),
                  "PMAA": ("GUST +C", "CG2"), "NMAA": ("GUST -C", "CG3"),
                  "ACRL": ("AC ROLL", "CG2"), "TORS": ("ST ROL C", "CG1")}
        vn = {pt.case: pt for pt in envelope.vn}
        for slot, (run, cg) in expect.items():
            c = picks[slot]
            assert (vn[c.case].condition, vn[c.case].cg) == (run, cg), slot


def test_a_repointed_slot_says_so_and_a_project_without_a_wing_keeps_its_air_picks():
    """A delivered condition that moved names both runs in its ``note``; a
    project the wing analysis cannot run on (no ``wing_mass``) delivers the
    air picks unchanged with an empty table stating why."""
    from dataclasses import replace
    from sloads.modules.select import air_picks
    from sloads.modules.wing_variants import wing_variant_table

    p = _project("baron_58.project.json")
    envelope = default_envelope(p)
    picks = {c.label: c.case for c in air_picks(p, envelope)}
    moved = [c for c in build_critical(p, envelope).conditions
             if c.component == "wing" and c.case != picks[c.label]]
    assert moved, "the Baron re-points seven slots at #292"
    for c in moved:
        assert "net-governing run" in c.note and f"V-n case {picks[c.label]}" in c.note, c.label
    bare = replace(p, wing_mass=None)
    table = wing_variant_table(bare, envelope)
    assert not table.variants and "wing_mass" in table.reason
    delivered = {c.label: c.case for c in build_critical(bare, envelope).conditions
                 if c.component == "wing"}
    # The air picks, with D-62.8's coincidence rule applied at delivery
    # (#294): NNZ shares NMAA's point and nothing re-points, so it is empty.
    assert delivered == {k: v for k, v in picks.items() if k != "NNZ"}
    assert picks["NNZ"] == picks["NMAA"]


# --------------------------------------------------------------------------- #
# D-63.5 -- the MZFW seeds
# --------------------------------------------------------------------------- #
def test_the_mzfw_seeds_on_the_appendix_a_airplane():
    """Seeded in memory (the fixture carries no MZFW so its V-n numbering does
    not move): ``mzfw aft`` is the six people and the ballast row clipped
    onto the aft line; ``mzfw fwd`` coincides with CG4 and ``full fuel aft``
    with CG1 (note 63 §8.1's skip rule), so neither is written."""
    from sloads.cg_cases import (MZFW_CASE_NAMES, max_zero_fuel_weight_estimate,
                                 seed_flight_cases)

    p = _project("ga6_normal.project.json")
    p.weight.max_zero_fuel_weight_lb = max_zero_fuel_weight_estimate(p)
    assert p.weight.max_zero_fuel_weight_lb == pytest.approx(2913.0)
    seeded, missing = seed_flight_cases(p)
    assert not missing
    by_name = {c.name: c for c in seeded}
    assert [c.name for c in seeded if c.name in MZFW_CASE_NAMES] == ["mzfw aft"]
    aft = by_name["mzfw aft"]
    assert aft.weight_lb == pytest.approx(2900.84, abs=0.01)
    assert aft.xcg == pytest.approx(85.09, abs=0.01)
    assert aft.loading is not None
    assert set(aft.loading.aboard) == {"Copilot", "3rd person", "4th person",
                                       "5th person", "6th person", "Ballast"}
    assert list(aft.loading.fractions) == ["5th person"]
    assert 0.46 < aft.loading.fractions["5th person"] < 0.48


def test_the_atr_mzfw_aft_seed_is_note_63s_row_and_is_entered_from_birth():
    """Note 63 §8.3's mechanism on the #260 fixture: ``mzfw aft`` is the MZFW
    cap itself, 33,510 lb, with the forward cabin trimmed to 4,056 lb so the
    loading sits under the cap inside the aft line (403.69 in against the
    404.11 in limit) -- the search's answer to the pound; and the seeded case
    is an entered loading, so D-25a's echo reads it. (Before #260 the sample
    was 28,410 lb with the aft hold trimmed to 853 lb onto the aft line.)"""
    from sloads.cg_cases import seed_flight_cases
    from sloads.mass_distribution import derive_case_loadings

    p = _project("atr42_100.project.json")
    seeded, missing = seed_flight_cases(p)
    assert not missing
    aft = next(c for c in seeded if c.name == "mzfw aft")
    assert aft.weight_lb == pytest.approx(33510.0, abs=0.05)
    assert aft.loading.fractions["Passengers, fwd cabin (24)"] * 4080.0 == pytest.approx(4056.0, abs=0.5)
    assert aft.xcg == pytest.approx(403.69, abs=0.01)          # inside the aft line
    ld = derive_case_loadings(p, [aft])[0]
    assert ld.entered and ld.derivable and ld.weight_lb == pytest.approx(aft.weight_lb, abs=0.05)
    # The fixture carries exactly the seed (its own drift guard is test_cg_cases).
    assert [c.name for c in flight_cases(p)][-3:] == ["mzfw aft", "mzfw fwd", "full fuel aft"]


def test_the_seed_search_clips_and_never_trims_a_loading_that_is_inside():
    """The search's contract: a whole-row loading inside the limits is taken
    as it is; only a loading outside is clipped, by one row, by the least it
    takes; the cap is honoured exactly; nothing is found under a cap the
    fixed rows alone exceed."""
    from sloads.mass_distribution import seed_loading_search

    p = _project("ga6_normal.project.json")
    aft, fwd = 85.09396, (lambda w: 72.62436)
    # A cap below the base + reserve rows: nothing.
    assert seed_loading_search(p, fuel="none", cap_lb=2000.0, edge="aft",
                               aft_limit=aft, fwd_limit_at=fwd) is None
    # Cap binds: the heaviest zero-fuel loading is clipped onto the cap exactly.
    found = seed_loading_search(p, fuel="none", cap_lb=2500.0, edge="aft",
                                aft_limit=aft, fwd_limit_at=fwd)
    assert found is not None and found.weight_lb == pytest.approx(2500.0, abs=1e-6)
    assert len(found.loading.fractions) == 1 and found.trimmed
    # Aft line binds: one row clipped, the CG on the line to the search's step.
    found = seed_loading_search(p, fuel="none", cap_lb=10000.0, edge="aft",
                                aft_limit=aft, fwd_limit_at=fwd)
    assert found.cg_x <= aft + 1e-6 and found.cg_x > aft - 0.05
    assert len(found.loading.fractions) == 1
    # Forward edge on a loading already inside: whole rows, no fraction.
    found = seed_loading_search(p, fuel="none", cap_lb=10000.0, edge="fwd",
                                aft_limit=aft, fwd_limit_at=fwd)
    assert found.loading.fractions == {} and found.weight_lb == pytest.approx(2063.0)
    # Full fuel: every consumable row aboard at 1.0.
    found = seed_loading_search(p, fuel="full", cap_lb=3400.0, edge="aft",
                                aft_limit=aft, fwd_limit_at=fwd)
    assert "Fuel to gross wt" in found.loading.aboard
    assert found.weight_lb == pytest.approx(3400.0, abs=1e-6)


def test_mzfw_is_a_design_weight_in_the_mlw_shape():
    """``0`` = not entered and refuses when required; the ordering chain
    names it; the estimate is OEW + max payload and is never written."""
    from sloads import validation
    from sloads.cg_cases import max_zero_fuel_weight, max_zero_fuel_weight_estimate
    from sloads.models import MissingInputError

    p = _project("ga6_normal.project.json")
    assert max_zero_fuel_weight(p, required=False) == 0.0
    with pytest.raises(MissingInputError, match="max_zero_fuel_weight_lb"):
        max_zero_fuel_weight(p)
    assert max_zero_fuel_weight_estimate(p) == pytest.approx(2913.0)
    assert p.weight.max_zero_fuel_weight_lb == 0.0
    p.weight.max_zero_fuel_weight_lb = 3500.0          # above MTOW: the chain says so
    codes = [w.code for w in validation.consistency_warnings(p)]
    assert "weight_order_chain" in codes


# --------------------------------------------------------------------------- #
# D-63.9 / #290: the loading editor's owners -- the entered form of a searched
# loading, the Mass cases summary and the per-case WING parts
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_entering_a_searched_loading_as_found_changes_nothing(example):
    """G-63.6's GUI half: ``loading_definition_of`` is the *Add loading*
    gesture, and replaying its result through ``entered_loading`` reproduces
    the searched item set, weight and CG exactly -- so entering a case as the
    search found it moves no load, and every later edit is the user's."""
    project = _project(example)
    items = project.weight.items
    all_cases = list(project.weight.cg_cases)
    before = {ld.name: ld for ld in md.derive_case_loadings(project, all_cases)}
    checked = 0
    for case in all_cases:
        found = before[case.name]
        definition = md.loading_definition_of(found, items)
        if not found.derivable:
            assert definition is None
            continue
        replay = md.entered_loading(items, dataclasses.replace(case, loading=definition))
        assert [it.name for it in replay.items] == [it.name for it in found.items], case.name
        assert replay.weight_lb == pytest.approx(found.weight_lb, abs=1e-9)
        assert replay.cg_x == pytest.approx(found.cg_x, abs=1e-9)
        assert replay.cg_z == pytest.approx(found.cg_z, abs=1e-9)
        assert all(0.0 < f <= 1.0 for f in definition.fractions.values())
        checked += 1
    assert checked >= 1


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_mass_cases_summary_reads_its_owners_and_computes_nothing(example):
    """One row per CG case, every column equal to the owner it is read from:
    the case scalars, ``derive_case_loadings`` (the D-25a echo values, fuel by
    the item ``consumable`` flag, payload, ballast) and ``wing_mass_state``
    (panel, points, source, reason) -- design note 63 D-63.9."""
    project = _project(example)
    rows = md.mass_case_summary(project)
    cases = project.weight.cg_cases
    assert [r.case for r in rows] == [c.name for c in cases]
    loadings = {ld.name: ld for ld in md.derive_case_loadings(project, cases)}
    for row, case in zip(rows, cases):
        assert (row.weight_lb, row.xcg, row.zcg) == (case.weight_lb, case.xcg, case.zcg)
        assert row.entered == (case.loading is not None)
        ld = loadings[case.name]
        if not ld.derivable:
            assert row.loading_weight_lb is None and row.reason == ld.note
            continue
        assert row.loading_weight_lb == ld.weight_lb
        assert row.fuel_lb == pytest.approx(
            math.fsum(it.weight_lb for it in ld.items if it.consumable))
        assert row.ballast_lb == (ld.ballast.weight_lb if ld.ballast else 0.0)
        assert row.ballast_fraction == ld.ballast_fraction
        if case.name in {c.name for c in flight_cases(project)}:
            state = md.wing_mass_state(project, case.name)
            assert row.source == state.source
            assert row.panel_weight_lb == state.panel_weight_lb
            assert row.point_weight_lb == pytest.approx(
                math.fsum(it.weight_lb for it in state.point_masses))
            assert row.point_count == len(state.point_masses)
        else:
            assert row.panel_weight_lb is None
            assert row.source == ("entered" if ld.entered else "searched")


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_wing_parts_view_is_the_mass_state_panel_first(example):
    """The Wing Loads page's read-only view lists, per FLIGHT case, the panel
    row then each per-side POINT part exactly as ``wing_mass_state`` hangs
    them (design note 63 D-63.3 / D-63.9)."""
    project = _project(example)
    rows = md.wing_parts_summary(project)
    for case in flight_cases(project):
        state = md.wing_mass_state(project, case.name)
        mine = [r for r in rows if r.case == case.name]
        assert mine[0].part == "panel (per side)"
        assert mine[0].weight_lb == state.panel_weight_lb
        assert mine[0].carriage == WingCarriage.PANEL.value
        assert [(r.part, r.weight_lb, r.y) for r in mine[1:]] == \
            [(it.name, it.weight_lb, it.y) for it in state.point_masses]
        assert {r.source for r in mine} == {state.source}
