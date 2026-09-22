"""The mass SSOT (step B1): ``weight.items`` -> per-component station inertia.

Plan 11 decision **B-2**. Before this step the suite carried two mass models —
the itemized ``weight.items`` database and a short hand-entered
``fuselage_mass.stations`` lump table — and **nothing compared them**. The
entered table was short of the item model by 10 % to 100 % of the beam on every
shipped fixture, so every fuselage inertia load, shear, bending moment and
exported body card was computed from a beam carrying less mass than the airplane
weighed.

This module is the structural guard half of the fix (``CLAUDE.md`` required
practice 3: a single owner *plus* a drift test). The invariants:

* the partition is complete — wing items + beam stations == every item == W;
* the wing tie — ``Σ(items tagged wing) == 2 × (panel + concentrated)``, the two
  models of the same physical wing agreeing;
* the derived beam is what ``body_loads`` actually integrates;
* an untagged (pre-B1) file still loads, and its inference is conservative.

The three fixtures where the wing tie did **not** hold (wing-tank fuel inside an
undivided fuel row) were pinned open to the pound until design note 29 gave
``MassItem`` a ``wing_fraction``; the pin survives as the reduction gate
:func:`test_stripping_the_fraction_reopens_exactly_the_wing_tank_fuel`.

Since **#257** the file also gates *who states a check*. A reconciliation
between the two mass models is only worth computing where a reader of the
issued document can see it, and three of the four reached the Weight & Mass
screen and no document at all —
:func:`test_every_mass_reconciliation_is_read_by_the_issued_document` forbids
that by name, and
:func:`test_the_issued_document_states_every_mass_gap_it_ships_with` asks the
rendered document for the numbers, so a check routed through a function nobody
renders still fails.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from imperial_baseline import EXAMPLES

from sloads import io
from sloads import mass_distribution as md
from sloads.models import MassComponent
from sloads.modules.body_loads import build_body_loads
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.select import build_critical
from sloads.report.render import format_value
from sloads.units import Channel, UnitSystem, deliverable_units

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _project(example: str):
    return io.load_project(os.path.join(_ROOT, "examples", example))


# --------------------------------------------------------------------------- #
# Tagging
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_every_shipped_item_is_explicitly_tagged(example):
    """No shipped fixture relies on inference.

    ``infer_component`` exists for pre-B1 files, and it is a fallback with a
    documented blind spot (every item sits at ``y = 0``, so nothing distinguishes
    a wing-mounted engine from a fuselage one). Shipped data must not depend on
    it, or the SSOT's authority rests on a guess.
    """
    dist = md.distribution(_project(example))
    assert dist.inferred == (), f"{example}: untagged items {list(dist.inferred)}"


def test_an_untagged_file_gets_a_complete_beam_and_a_loud_wing_tie():
    """A pre-B1 project has no ``component`` anywhere and must still work.

    The fallback refuses to guess and puts every untagged pound on the fuselage
    beam — so the beam is *complete* (heavier than the truth by the wing panel,
    never lighter, never mis-attributed to a surface). What must **not** happen
    is an untagged file passing as tagged, so the wing tie fails loudly: nothing
    is claimed for the wing, and the tie reads 0 against 2 x panel_weight_lb.
    That failure is the instruction to tag the items. Since design note 63 the
    signal is the derived panel itself: nothing tagged ``wing`` means WINGINER
    integrates **no** panel, the state's tie holds trivially at zero, and the
    ``wing_panel_empty`` validator is what says so (``tests/test_validation.py``).
    """
    p = _project("ga6_normal.project.json")
    for it in p.weight.items:
        it.component = None
    dist = md.distribution(p)
    assert len(dist.inferred) == len(p.weight.items)
    assert not dist.by_component[MassComponent.WING], \
        "the fallback must never claim an item for the wing on y=0 data"
    assert dist.weight(MassComponent.FUSELAGE) == sum(it.weight_lb for it in p.weight.items)
    assert md.partition_closes(p).ok, "the partition still closes"

    assert md.derived_panel_weight(p) == 0.0 and md.panel_weight(p) == 0.0
    assert md.wing_mass_tie(p) is None, "no override, nothing to tie against"


def test_an_explicit_tag_beats_the_fallback():
    p = _project("ga6_normal.project.json")
    item = next(it for it in p.weight.items if it.name == "Wing, outboard")
    assert item.component is MassComponent.WING
    assert md.component_of(item, p) is MassComponent.WING
    assert md.infer_component(item, p) is MassComponent.FUSELAGE
    item.component = None
    assert md.component_of(item, p) is MassComponent.FUSELAGE


def test_the_component_tag_round_trips_through_json():
    """``component`` must survive save/load, or the SSOT is one file-write from
    reverting to inference."""
    p = _project("atr42_100.project.json")
    before = [(it.name, it.component) for it in p.weight.items]
    after = io.project_from_dict(io.project_to_dict(p))
    assert [(it.name, it.component) for it in after.weight.items] == before
    assert any(c is MassComponent.WING for _, c in before)


# --------------------------------------------------------------------------- #
# The partition
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_the_partition_closes(example):
    """wing + fuselage beam == every item == W, to the pound.

    The structural guard on the partition: no item is lost between the two
    distributions and none is counted twice. Fails if a member is added to
    ``MassComponent`` without a home in ``BEAM_COMPONENTS``.
    """
    check = md.partition_closes(_project(example))
    assert check.ok, f"{example}: {check.detail}"


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_beam_carries_the_empennage_but_not_the_wing(example):
    """The h-tail and v-tail hang off the aft fuselage, so the beam carries them;
    the wing enters as the carry-through *reaction*, never as mass.

    Applying the wing as both would double-count it — the seam rule (plan 11 §4:
    *a load that a free-body cut introduces is never applied in the assembled
    model*).
    """
    p = _project(example)
    dist = md.distribution(p)
    beam = sum(s.weight_lb for s in md.derived_fuselage_stations(p))
    want = dist.weight(*md.BEAM_COMPONENTS)
    assert MassComponent.WING not in md.BEAM_COMPONENTS
    assert abs(beam - want) < 1e-6, example


def test_stations_at_the_same_x_merge_into_one_node():
    """ga6 has four items at x = 97/1 (the gear) and two at x = 75 (the pilots);
    a beam node is a station, not an item."""
    p = _project("ga6_normal.project.json")
    stations = md.derived_fuselage_stations(p)
    xs = [s.x for s in stations]
    assert xs == sorted(xs), "nose->tail"
    assert len(xs) == len(set(xs)), "no duplicate stations"
    assert len(stations) < len(p.weight.items)
    gear = next(s for s in stations if abs(s.x - 97.0) < 1e-9)
    assert gear.weight_lb == 45.0 + 110.0     # wheel + structure, one node


# --------------------------------------------------------------------------- #
# The wing's one mass model (design note 63), and the row->parts split (note 29)
# --------------------------------------------------------------------------- #
#: The per-side panel weight each fixture derives from its WING-tagged PANEL
#: items (D-63.2) -- the value ``wing_mass.panel_weight_lb`` entered before v67,
#: to the pound, so no fixture carries an override (G-63.4).
_DERIVED_PANEL = {
    "atr42_100.project.json": 1750.0,   # 3,500 lb wing since #260
    "baron_58.project.json": 280.0,
    "concept_heavy.project.json": 900.0,
    "concept_regional_jet.project.json": 2100.0,
    "ga6_normal.project.json": 165.0,
}


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_panel_is_derived_and_no_fixture_overrides_it(example):
    """D-63.2 / G-63.4: half the WING PANEL items is the panel WINGINER
    integrates, the entered value of every fixture before v67; the override is
    ``None`` on all five, so ``wing_mass_tie`` -- the override against the
    derived value, all that is left of the note 29 tie -- has nothing to say."""
    p = _project(example)
    assert p.wing_mass.panel_weight_override_lb is None
    assert md.derived_panel_weight(p) == pytest.approx(_DERIVED_PANEL[example])
    assert md.panel_weight(p) == md.derived_panel_weight(p)
    assert md.wing_mass_tie(p) is None
    p.wing_mass.panel_weight_override_lb = _DERIVED_PANEL[example] * 1.1
    check = md.wing_mass_tie(p)
    assert check is not None and not check.ok
    assert check.gap == pytest.approx(0.1 * _DERIVED_PANEL[example])
    assert md.panel_weight(p) == _DERIVED_PANEL[example] * 1.1, "the override governs"


def test_a_fraction_row_still_splits_and_the_split_reaches_the_wing_state():
    """WF-5's mechanism survives the fixtures no longer needing it: a fuselage
    row with ``wing_fraction`` puts its wing share in the state's PANEL parts
    at the row's carriage, and strips out when the fraction is cleared."""
    p = _project("concept_regional_jet.project.json")
    fuel = next(it for it in p.weight.items if it.name == "Mission fuel")
    before = md.derived_panel_weight(p)
    fuel.wing_fraction = 0.5
    assert md.derived_panel_weight(p) == pytest.approx(before + 0.25 * fuel.weight_lb)
    assert md.partition_closes(p).ok
    state = md.database_mass_state(p)
    assert md.wing_state_tie(state).ok
    fuel.wing_fraction = 0.0
    assert md.derived_panel_weight(p) == pytest.approx(before)


def test_reacted_parts_splits_a_row_by_weight_and_inertia_at_one_position():
    """WF-2/WF-3: two parts, the row's position, weight and own inertias in the
    fraction; every part ``wing_fraction == 0`` so ``component_of`` is exact;
    a zero-fraction row is returned as the very same object (identity keys the
    CONM2 overlay matching). On the RJ's fuselage fuel row with a fraction set
    here -- no shipped fixture carries one since note 63 moved the wing-tank
    fuel to per-side WING rows."""
    p = _project("concept_regional_jet.project.json")
    row = next(it for it in p.weight.items if it.name == "Mission fuel")
    row.wing_fraction = 0.4142140833
    row.ixx, row.iyy, row.izz = 1000.0, 2000.0, 3000.0
    parts = md.reacted_parts([row], p)
    assert [pt.name for pt in parts] == ["Mission fuel [fuselage]", "Mission fuel [wing]"]
    body, wing = parts
    f = row.wing_fraction
    assert wing.component is MassComponent.WING and body.component is MassComponent.FUSELAGE
    assert wing.weight_lb == pytest.approx(row.weight_lb * f)
    assert body.weight_lb + wing.weight_lb == pytest.approx(row.weight_lb, rel=1e-12)
    assert (wing.ixx, wing.iyy, wing.izz) == pytest.approx((1000 * f, 2000 * f, 3000 * f))
    assert body.izz + wing.izz == pytest.approx(3000.0, rel=1e-12)
    for pt in parts:
        assert (pt.x, pt.y, pt.z) == (row.x, row.y, row.z)
        assert pt.wing_fraction == 0.0
        assert pt.kind is row.kind and pt.consumable is row.consumable
    plain = next(it for it in p.weight.items if it.name == "Wing structure")
    assert md.reacted_parts([plain], p)[0] is plain
    row.wing_fraction = 1.0
    (only,) = md.reacted_parts([row], p)
    assert only.component is MassComponent.WING and only.weight_lb == row.weight_lb


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_mass_properties_path_reads_rows_not_parts(example):
    """WTONECG/WTENV read the rows: total weight and CG from ``weight.items``
    are unchanged by the split to the last digit (both parts sit at the row's
    position), which is what keeps every Appendix A number where it is."""
    p = _project(example)
    rows = p.weight.items
    parts = md.reacted_parts(rows, p)
    for axis in ("x", "z"):
        assert math.fsum(pt.weight_lb * getattr(pt, axis) for pt in parts) == \
            pytest.approx(math.fsum(it.weight_lb * getattr(it, axis) for it in rows), rel=1e-12)
    assert math.fsum(pt.weight_lb for pt in parts) == \
        pytest.approx(math.fsum(it.weight_lb for it in rows), rel=1e-12)


@pytest.mark.parametrize("example", ["ga6_normal.project.json"])
def test_every_consumer_agrees_with_the_owner_on_the_wing_share(example):
    """The WF-3 drift guard: ``balance``'s wing/body split, the CONM2 header's
    wing total and ``distribution()`` all read the same parts. Measured on the
    gross-weight loading, where the whole fuel row is aboard -- with a fraction
    put on the GA6's fuselage fuel row here, since note 63 left no fixture with
    one (the wing-tank fuel is per-side WING rows now)."""
    from sloads.export import mass_cards
    from sloads.modules import balance
    p = _project(example)
    next(it for it in p.weight.items if it.name == "Fuel to gross wt").wing_fraction = 0.3
    loading = max(md.derive_case_loadings(p), key=lambda ld: ld.weight_lb)
    parts = md.reacted_parts(loading.items, p)
    w_all = math.fsum(pt.weight_lb for pt in parts)
    w_wing = math.fsum(pt.weight_lb for pt in parts
                       if md.component_of(pt, p) is MassComponent.WING)
    w_rows_wing = math.fsum(it.weight_lb for it in loading.items
                            if it.component is MassComponent.WING)
    assert w_all == pytest.approx(loading.weight_lb, rel=1e-9)
    assert w_wing > w_rows_wing, "the fuel's wing share is not on the wing"
    body = balance.body_inertia(loading, p, nz=1.0)
    assert math.fsum(ld.weight_lb for ld in body) == pytest.approx(w_all - w_wing, rel=1e-9)
    _, panel_both = balance.wing_inertia_strips(p, 1.0)
    scale = balance._wing_inertia_scale(loading, p, panel_both)
    assert scale * panel_both == pytest.approx(w_wing, rel=1e-9)
    cards, _ = mass_cards.mass_cards(p)
    card_wing = math.fsum(pt.weight_lb for c in cards
                          for pt in md.reacted_parts([c.item], p)
                          if md.component_of(pt, p) is MassComponent.WING)
    assert card_wing > math.fsum(c.item.weight_lb for c in cards
                                 if c.item.component is MassComponent.WING)
    # The CONM2 header's wing total was the third consumer this guard compared
    # against, until note 56 D-56.6 retired the line: with every mass on a grid
    # at its own CG, a wing item is at the wing item's position and there is no
    # provisional attachment left to caption. The card-side reading of the split
    # is still checked, two assertions up -- it is the *header sentence* that is
    # gone, not the consumer.


# --------------------------------------------------------------------------- #
# Derived beam vs entered override
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_the_shipped_fixtures_use_the_derived_beam(example):
    p = _project(example)
    if p.fuselage_mass is not None:
        assert not p.fuselage_mass.stations_are_override
    assert md.fuselage_beam_stations(p) == md.derived_fuselage_stations(p)


def test_an_explicit_override_wins_and_is_still_reconciled():
    """The entered table is a deliberate act, not a stale default — but the
    difference from the SSOT is reported either way, so an override is a decision
    made in front of the number rather than instead of it."""
    p = _project("ga6_normal.project.json")
    p.fuselage_mass.stations_are_override = True
    assert md.fuselage_beam_stations(p) == p.fuselage_mass.stations
    check = md.fuselage_reconciliation(p)
    assert check is not None and not check.ok
    assert check.gap == pytest.approx(2578.0 - 3070.0)


def test_a_project_with_no_items_falls_back_to_the_entered_table():
    """The SSOT does not strand a project that only ever had the lump table."""
    p = _project("ga6_normal.project.json")
    entered = list(p.fuselage_mass.stations)
    p.weight = None
    assert md.derived_fuselage_stations(p) == []
    assert md.fuselage_beam_stations(p) == entered


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_entered_tables_are_all_short_of_the_item_model(example):
    """Pins the finding that motivated B1, per fixture.

    Every hand-entered table understates the beam — never overstates it — which
    is the signature of items being forgotten rather than of a different
    modelling choice. Recorded so the fixtures cannot quietly drift back.
    """
    p = _project(example)
    check = md.fuselage_reconciliation(p)
    if check is None:
        pytest.skip(f"{example}: no entered station table to compare")
    # (The ATR enters no station table since #260, so it skips above.)
    assert check.gap < 0, f"{example}: entered table now exceeds the item model"
    assert not check.ok, f"{example}: gap closed — update this test"


# --------------------------------------------------------------------------- #
# The consumer
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_body_loads_integrates_the_ssot_beam(example):
    """``body_loads`` reads the SSOT, not ``fuselage_mass.stations``.

    The point of the whole step: the module that computes fuselage shear and
    bending now integrates every pound the airplane weighs outside the wing --
    and since design note 63 (D-63.8) every pound **the condition's own
    loading** carries there: each result's mass stations are the beam derived
    from its mass state, not the whole database's.
    """
    p = _project(example)
    if p.envelope is None:
        p.envelope = build_envelope(p)
    if p.envelope.critical is None:
        p.envelope.critical = build_critical(p)
    results = build_body_loads(p)
    assert results
    for r in results:
        state = md.wing_mass_state(p, r.case_ref.cg or None)
        assert r.mass_state == state.label
        beam = md.fuselage_beam_stations(p, state.loading)
        mass_x = {round(s.x, 6) for s in beam}
        got = {round(s.x, 6) for s in r.stations if s.source == "mass"}
        assert mass_x <= got | {round(s.x, 6) for s in r.stations}, example
        # ...and the beam still closes free-free, which is the Ch 15 invariant.
        scale = max(abs(s.fz) for s in r.stations)
        assert abs(sum(s.fz for s in r.stations)) <= 1e-6 * scale + 1e-6


def test_concept_heavy_gained_a_fuselage_it_never_had():
    """The fixture with no ``fuselage_mass.stations`` at all now has a beam.

    It was the one example with no body deck, purely because the only input the
    Ch 15 module read was a table nobody had entered. 16,200 lb of airplane had
    no fuselage loads; it does now -- 15,000 lb of it after design note 29 moved
    1,200 lb of wing-tank fuel onto the wing, and 10,700 lb since design note
    63 moved the whole 5,500 lb fuel row into per-side wing tank rows (D-63.4).
    """
    p = _project("concept_heavy.project.json")
    assert not (p.fuselage_mass and p.fuselage_mass.stations)
    beam = md.fuselage_beam_stations(p)
    assert beam
    assert sum(s.weight_lb for s in beam) == pytest.approx(10700.0)


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_component_summary_covers_the_whole_airplane(example):
    rows = md.component_summary(_project(example))
    assert rows
    total = sum(float(r["Weight (lb)"]) for r in rows)
    assert total == pytest.approx(md.distribution(_project(example)).weight(), rel=1e-6)


# --------------------------------------------------------------------------- #
# #257 -- a mass check the document does not state is a check nobody reads
# --------------------------------------------------------------------------- #
#: Functions in ``mass_distribution`` that compare the two mass models and are
#: **not** read by any section of the oracle report, with the reason. Empty on
#: purpose: every reconciliation this module computes is stated on the page that
#: ships. An entry here is a deliberate exemption and must say why the reader of
#: a certification document does not need the number.
_UNSTATED_CHECKS = {
    "case_loading_checks":
        "not the two mass models: it compares a derived loading against the "
        "flight case's own weight/CG echo, and its derived branch holds that "
        "to 1e-9 where its owner documents the match as _CG_MATCH_TOL (0.5 in) "
        "for a zero-ballast loading -- so it reports a failure on four of the "
        "five shipped fixtures that is not one. Routing it to the document "
        "today would print those false alarms. Filed with a body in the "
        "backlog's Open defects index (2026-09-16), with the one real "
        "disagreement underneath it: baron_58's `aft gross` loading sits "
        "4.12 in below the zcg the case states, past that same 0.5 in.",
}


def _check_producers():
    """``{name: return annotation}`` for every public ``MassCheck`` producer.

    Parsed from the source rather than imported and introspected, for the reason
    ``tests/test_envelope_owner.py`` gives about the sibling scans: the module
    docstring names ``MassCheck`` several times in prose, and a text search would
    find those before it found a signature.
    """
    import ast

    with open(os.path.join(_ROOT, "sloads", "mass_distribution.py"),
              encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
            continue
        if node.returns is None:
            continue
        annotation = ast.unparse(node.returns)
        if "MassCheck" in annotation:
            out[node.name] = annotation
    return out


def _report_imports():
    """Every name ``sloads/report/`` imports from ``mass_distribution``."""
    import ast

    names = set()
    root = os.path.join(_ROOT, "sloads", "report")
    for dirpath, _dirs, files in os.walk(root):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            with open(os.path.join(dirpath, filename), encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            for node in ast.walk(tree):
                if (isinstance(node, ast.ImportFrom) and node.module
                        and node.module.endswith("mass_distribution")):
                    names.update(alias.name for alias in node.names)
    return names


def test_every_mass_reconciliation_is_read_by_the_issued_document():
    """#257: a check the GUI states and the document does not is half-routed.

    ``fuselage_reconciliation`` was exactly that for a milestone -- one consumer,
    the Weight & Mass screen -- while the entered station table it flags sits
    13-41 % under the beam on every shipped fixture, and ``tail_reconciliation``
    had no consumer at all. The rule is the routing, not those two functions: a
    fifth check added later is stated or exempted, never silently unread.
    """
    producers = _check_producers()
    # Proof the scan found the signatures rather than nothing: the module owns
    # at least the partition, the wing tie and the two reconciliations.
    assert len(producers) >= 4, sorted(producers)
    imported = _report_imports()
    for name in sorted(producers):
        if name in _UNSTATED_CHECKS:
            continue
        assert name in imported, (
            f"{name} compares the two mass models and no section of the oracle "
            f"report reads it; state it, or add it to _UNSTATED_CHECKS with the "
            f"reason. Imported by report/: {sorted(imported)}")


def test_the_unstated_check_exemptions_are_not_stale():
    """The anti-blanket rule the sibling allowlists carry."""
    producers = _check_producers()
    for name, reason in _UNSTATED_CHECKS.items():
        assert name in producers, f"_UNSTATED_CHECKS names {name}, which is not a check"
        assert reason, name


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_issued_document_states_every_mass_gap_it_ships_with(example):
    """The same rule asked of the rendered document, by effect rather than name.

    The name gate above passes on an import; this one fails unless the number
    reaches the page. Three statements, each on the fixtures that have the
    condition to state: the entered-vs-derived fuselage gap, a surface no item
    is tagged to, and the surface weight the spanwise distribution applied.
    """
    from sloads.field_registry import reduce_to_oracle_inputs
    from sloads.models.report import ReportSpec
    from sloads.report import oracle_content as oc
    from sloads.report import oracle_sections as osx

    project = reduce_to_oracle_inputs(_project(example))
    doc = oc.build_oracle_document(project, ReportSpec(
        title="FAR 23 Structural Design Loads", report_number="LR-0142",
        revision="B", abstract="An abstract."))

    def prose(section):
        out = list(section.body) + [section.absent_reason or ""]
        for sub in section.subsections:
            out += prose(sub)
        return out

    text = " ".join(p for s in doc.sections for p in prose(s))

    check = md.fuselage_reconciliation(project)
    if check is not None and not check.ok:
        assert "not the same airplane" in text, example
        for value in (check.got, check.want):
            assert format_value(value, "lb") in text, (example, value)
    untagged = md.untagged_tail_surfaces(project)
    if untagged and project.weight is not None and project.weight.items:
        assert "not separately accounted" in text, example
    # The spanwise subsection is where the surface weight is applied, so the
    # statement is asked of the fixtures that render one: the fin's spanwise
    # loads are withheld on every arrangement (OR-133/#254), and a surface with
    # no distribution states the absence. Neither renders a weight, because
    # neither applied one -- the statement belongs to the loads, not the page.
    for component in ("htail", "vtail"):
        if (osx._vtail_withheld(project, component)
                or not osx._tail_spanwise(project, component)):
            continue
        weight = md.tail_surface_weight(project, component)
        if weight:
            assert format_value(weight, "lb") in text, (example, component, weight)
        else:
            assert "absent inertia relief" in text, (example, component)
    # The wing tie is stated on every fixture, holding or not.
    if md.wing_mass_tie(project) is not None:
        assert "two models of the wing's mass" in text, example


if __name__ == "__main__":
    sys.exit(pytest.main([os.path.abspath(__file__), "-q"]))
