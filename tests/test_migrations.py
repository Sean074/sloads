"""The schema gate (#93), and the migration machinery kept behind it.

Pre-production a project file is read at the current ``SCHEMA_VERSION`` or a
version the hop chain reaches it from — v55, through the additive-identity
55→56 hop (note 36 OV-10, #97), the semantic 56→57 landing-N hop (note 37
LF-8, #123) and the two additive-identity ``LoadValue`` hops that follow it
(57→58 ``frame``, note 38 GF-6/#134; 58→59 ``point``, #141) — and
`sloads.migrations.migrate`
raises `SchemaVersionError` for anything else: older than the floor, newer, or
unversioned. This file pins that gate, and pins that the hop chain works
(`migrations.py` module docstring).

Until #93 this file tested twelve hops against eleven frozen legacy fixtures
(M4-10). Those hops and fixtures went out together; what remains of that
discipline is `tests/fixtures_schema/v55_current.json`, one frozen file at the
version this build reads, and the examples-are-current guard in
`test_schema_guards.py`.
"""

import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.migrations import (
    MIGRATIONS,
    SUPPORTED_FLOOR,
    SchemaVersionError,
    applied_hops,
    migrate,
    source_schema_version,
)
from sloads.models import SCHEMA_VERSION
from sloads.models.enums import RotorDirection

_HERE = os.path.dirname(os.path.abspath(__file__))
_FIXTURES = os.path.join(_HERE, "fixtures_schema")
_EXAMPLES = os.path.join(os.path.dirname(_HERE), "examples")
_CURRENT = "v69_current.json"


def _load(name=_CURRENT):
    with open(os.path.join(_FIXTURES, name), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# 1. The gate
# --------------------------------------------------------------------------- #
def test_the_floor_is_the_oldest_hop():
    """#93's gate with note 36's one live hop: the floor is where the chain
    starts, and every version from there to current is a registered hop."""
    assert SUPPORTED_FLOOR == min(MIGRATIONS) == 55
    assert sorted(MIGRATIONS) == list(range(SUPPORTED_FLOOR, SCHEMA_VERSION))


def test_a_current_file_passes_through_untouched():
    current = _load()
    assert current["schema_version"] == SCHEMA_VERSION, "the frozen fixture went stale"
    assert migrate(current) == current


@pytest.mark.parametrize("version", [SUPPORTED_FLOOR - 1, SUPPORTED_FLOOR - 10, 18, 0])
def test_an_older_file_is_refused_and_says_both_versions(version):
    d = {**_load(), "schema_version": version}
    with pytest.raises(SchemaVersionError) as exc:
        migrate(d)
    assert f"schema {version}" in str(exc.value)
    assert str(SCHEMA_VERSION) in str(exc.value)


def test_a_newer_file_is_refused_too():
    """Symmetry is the point: a file this build cannot fully read is refused
    whichever side it comes from. The old chain let a newer file through on
    'read what you understand', which pre-production means presenting a partial
    read of someone else's schema as this build's answer."""
    d = {**_load(), "schema_version": SCHEMA_VERSION + 5}
    with pytest.raises(SchemaVersionError):
        migrate(d)


def test_an_unversioned_dict_is_refused_by_name():
    """Including the bare ``EngineInput`` file that used to be discriminated by
    key-sniffing: no stamp, no read."""
    with pytest.raises(SchemaVersionError) as exc:
        migrate({"engine_designation": "CONTINENTAL IO-520-BB", "engine_type": "R"})
    assert "no schema_version" in str(exc.value)


def test_a_string_version_is_not_mistaken_for_the_number():
    with pytest.raises(SchemaVersionError):
        migrate({"schema_version": str(SCHEMA_VERSION), "geometry": {}})


def test_the_refusal_reaches_every_front_end_through_one_funnel():
    """``project_from_dict`` is what CLI, both GUIs and the tests all call."""
    with pytest.raises(SchemaVersionError):
        io.project_from_dict({**_load(), "schema_version": 41})


def test_the_refusal_is_a_value_error():
    """So it lands in the documented error contract and every existing load
    handler reports it without a new except branch."""
    assert issubclass(SchemaVersionError, ValueError)


def test_source_schema_version_reads_the_file_not_the_default():
    assert source_schema_version({"schema_version": 41}) == 41
    assert source_schema_version({}) == -1
    assert source_schema_version({"schema_version": "41"}) == -1


def test_a_file_that_is_not_an_object_is_refused_under_the_error_contract():
    """A JSON list or scalar at the top level is a ``ValueError``, not an
    ``AttributeError`` on ``.get`` -- which reached the CLI as a traceback on
    every route (the 0.8.4 closure review)."""
    for not_a_project in ([], [1, 2], "text", 3):
        with pytest.raises(ValueError):
            source_schema_version(not_a_project)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# 2. The machinery, kept
# --------------------------------------------------------------------------- #
def test_a_registered_hop_still_runs():
    """This is what a migration looks like: register the hop, lower the floor."""
    def _hop(d):
        d["migrated"] = True
        return d

    original = dict(MIGRATIONS)
    try:
        MIGRATIONS[SCHEMA_VERSION] = _hop
        out = migrate(_load())
        assert out["migrated"] is True
        assert out["schema_version"] == SCHEMA_VERSION
        assert applied_hops(SCHEMA_VERSION) == [SCHEMA_VERSION]
    finally:
        MIGRATIONS.clear()
        MIGRATIONS.update(original)
    assert applied_hops(SCHEMA_VERSION) == [], "the chain did not reset"


def test_a_v55_file_loads_through_the_identity_hop_unchanged():
    """Gate G-OV-5 (note 36, OV-10): the 55->56 hop is an identity -- a v55
    file passes through it with nothing moved (the chain then applies 56->57
    like any v56 file), ``applied_hops(55)`` names both hops, and the loaded
    ``Project`` equals the same airplane's current fixture."""
    v55 = _load("v55_current.json")
    assert v55["schema_version"] == 55
    hopped = MIGRATIONS[55](copy.deepcopy(v55))
    assert hopped == v55, "the 55->56 identity hop moved something"
    assert applied_hops(55) == list(range(55, SCHEMA_VERSION))
    assert io.project_to_dict(io.project_from_dict(v55)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def test_the_v56_hop_inverts_the_landing_override():
    """Gate G-LF-5 (note 37, LF-8, #123): the 56->57 hop is *semantic* --
    ``airplane_load_factor = gear_load_factor + lift_factor`` where the old NLG
    override was non-zero (3.167 = 2.5 + 0.667 on the frozen fixture), the
    ``0.0`` sentinel loads to unfilled, and the old key is gone either way."""
    v56 = _load("v56_current.json")
    assert v56["schema_version"] == 56
    assert v56["landing"]["gear_load_factor"] == 2.5
    out = migrate(v56)
    assert out["schema_version"] == SCHEMA_VERSION
    assert "gear_load_factor" not in out["landing"]
    assert out["landing"]["airplane_load_factor"] == 3.167
    assert applied_hops(56) == list(range(56, SCHEMA_VERSION))
    # The 0.0 sentinel meant "unset": it loads to an unfilled Optional.
    sentinel = copy.deepcopy(v56)
    sentinel["landing"]["gear_load_factor"] = 0.0
    out0 = migrate(sentinel)
    assert "gear_load_factor" not in out0["landing"]
    assert "airplane_load_factor" not in out0["landing"]
    assert io.project_from_dict(sentinel).landing.airplane_load_factor is None
    # The whole point (LF-11): the hop reproduces every NLG the reaction path
    # read, so the migrated project's 33-case matrix is bit-identical to the
    # same airplane's current fixture.
    from sloads.modules.landing import build_landing
    _, rx_hop = build_landing(io.project_from_dict(v56))
    _, rx_cur = build_landing(io.project_from_dict(_load()))
    assert [(c.vmp, c.dmp, c.smp, c.vnp, c.dnp, c.snp) for c in rx_hop] == \
           [(c.vmp, c.dmp, c.smp, c.vnp, c.dnp, c.snp) for c in rx_cur]


def test_a_v57_file_loads_through_the_identity_hop_unchanged():
    """Design note 38 GF-6 (#134): the 57->58 hop is an identity.

    v58 adds ``LoadValue.frame``, whose ``""`` default means exactly what v57
    meant -- no frame named. The field is persisted (``LoadValue`` rides inside
    ``critical.conditions[].loads``), so an added display-neutral field is still
    a shape change and still gets a hop; what the hop has to do is nothing.
    """
    v57 = _load("v57_current.json")
    assert v57["schema_version"] == 57
    hopped = MIGRATIONS[57](copy.deepcopy(v57))
    assert hopped == v57, "the 57->58 identity hop moved something"
    assert applied_hops(57) == list(range(57, SCHEMA_VERSION))
    assert io.project_to_dict(io.project_from_dict(v57)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def test_a_v58_file_loads_through_the_identity_hop_unchanged():
    """#141: the 58->59 hop is an identity, on the 57->58 precedent above.

    v59 adds ``LoadValue.point``, whose ``""`` default means exactly what v58
    meant -- no application point named. The field is persisted for the same
    reason ``frame`` is (``LoadValue`` rides inside
    ``critical.conditions[].loads``), so the display-neutral addition is still a
    shape change and still gets a hop; what the hop has to do is nothing.
    """
    v58 = _load("v58_current.json")
    assert v58["schema_version"] == 58
    hopped = MIGRATIONS[58](copy.deepcopy(v58))
    assert hopped == v58, "the 58->59 identity hop moved something"
    assert applied_hops(58) == list(range(58, SCHEMA_VERSION))
    assert io.project_to_dict(io.project_from_dict(v58)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def test_a_v59_file_loads_through_the_identity_hop_unchanged():
    """Design note 47 OR-74: the 59->60 hop is an identity, on the same precedent.

    v60 adds ``LoadValue.symbol``, whose ``""`` default means exactly what v59
    meant -- no notation symbol named. The field is persisted for the same
    reason ``frame`` and ``point`` are (``LoadValue`` rides inside
    ``critical.conditions[].loads``), so the display-neutral addition is still a
    shape change and still gets a hop; what the hop has to do is nothing.
    """
    v59 = _load("v59_current.json")
    assert v59["schema_version"] == 59
    hopped = MIGRATIONS[59](copy.deepcopy(v59))
    assert hopped == v59, "the 59->60 identity hop moved something"
    assert applied_hops(59) == list(range(59, SCHEMA_VERSION))
    assert io.project_to_dict(io.project_from_dict(v59)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def test_the_v60_hop_converts_an_entered_carry_through(tmp_path):
    """**G-OR-79** (design note 50 OR-127): the 60->61 hop is the first in the
    live chain that is not an identity.

    v61 replaces ``SurfaceInput.front_spar_pct``/``.rear_spar_pct`` -- fractions
    of the centreline root chord -- with the fuselage station itself. A file that
    *entered* a fraction must keep the carry-through it was analysed with, so the
    hop computes the station from that surface's own polylines rather than
    dropping the value and letting the (also changed) default take over. A
    ``null`` fraction is "not entered" in both schemas and hops to ``null``.

    No bundled example takes the converting branch -- all seven write both keys
    ``null``, which ``test_the_v60_fixture_hops_its_nulls_through`` pins -- so
    the branch is asserted on a constructed dict. That is not a weaker test: it
    is the only place the branch exists.
    """
    v60 = _load("v60_current.json")
    surfaces = v60["geometry"]["surfaces"]
    wing = surfaces[0]
    x_le, x_te = wing["leading_edge"][0][0], wing["trailing_edge"][0][0]
    c_root = x_te - x_le
    assert c_root > 0.0, "the fixture wing has no root chord to convert against"
    wing["front_spar_pct"], wing["rear_spar_pct"] = 0.18, 0.62

    out = MIGRATIONS[60](copy.deepcopy(v60))
    hopped = out["geometry"]["surfaces"][0]
    # The station the entered fraction described, on this airplane's own wing.
    assert hopped["front_spar_x_in"] == pytest.approx(x_le + 0.18 * c_root)
    assert hopped["rear_spar_x_in"] == pytest.approx(x_le + 0.62 * c_root)
    # The old keys are gone, not left behind as a second copy of the quantity.
    assert "front_spar_pct" not in hopped and "rear_spar_pct" not in hopped
    # And it is a *representation* change: the carry-through the hopped file
    # resolves is the one the pre-hop fractions described, to machine precision.
    # Loading re-runs the hop (``project_from_dict`` funnels every load through
    # ``migrate``), so this also pins that the hop is idempotent -- the first
    # draft was not, and the second pass wrote the converted station back to
    # ``None``.
    from sloads.derived_geometry import carry_through

    ct = carry_through(io.project_from_dict(out))
    assert ct is not None and not ct.assumed
    assert ct.x_f == pytest.approx(x_le + 0.18 * c_root)
    assert ct.x_r == pytest.approx(x_le + 0.62 * c_root)


def test_a_v62_file_loads_through_the_identity_hop_unchanged():
    """Design note 53 (D-53.1/D-53.4): the 62->63 hop is an identity.

    v63 gives ``EngineInput`` a thrust line as two entered points and the
    propeller's rotation direction. ``None`` on both points is exactly the v62
    state -- the schema carried no thrust line at all -- and ``CLOCKWISE`` is
    what every published engine torque already assumed before the field
    existed, so a v62 file loads bit-identical and no delivered load moves.
    """
    v62 = _load("v62_current.json")
    assert v62["schema_version"] == 62
    hopped = MIGRATIONS[62](copy.deepcopy(v62))
    assert hopped == v62, "the 62->63 identity hop moved something"
    assert applied_hops(62) == list(range(62, SCHEMA_VERSION))
    assert io.project_to_dict(io.project_from_dict(v62)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def test_a_v63_file_loads_through_the_identity_hop_unchanged():
    """Design note 44 OR-200: the 63->64 hop is an identity.

    v64 replaces ``VnPoint.case_ref`` (one slot) with ``case_refs`` (a list). A
    pre-v64 file could never hold more than one ref, so the reader turns the
    singular key into a one-element list and the hop itself has nothing to do.
    """
    v63 = _load("v63_current.json")
    assert v63["schema_version"] == 63
    hopped = MIGRATIONS[63](copy.deepcopy(v63))
    assert hopped == v63, "the 63->64 identity hop moved something"
    assert applied_hops(63) == list(range(63, SCHEMA_VERSION))
    assert io.project_to_dict(io.project_from_dict(v63)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def test_a_v64_file_loads_through_the_identity_hop_unchanged():
    """Design note 54 D-54.1/D-54.8 (#25 step 2): the 64->65 hop is an identity.

    v65 is the boundary-line model: ``SurfaceInput.hinge_line`` (empty = not
    entered), a control ``trailing_edge`` allowed empty (it derives from the
    parent's), ``LayoutInput.htail_dihedral_deg`` (declared, physics
    deferred), and the two tail input blocks regrouped into the D-54.1 seam
    order -- which JSON, storing fields by name, cannot see. Every default is
    exactly the v64 meaning, so a v64 file loads to the same airplane as the
    current fixture and no delivered load or GRID moves.
    """
    v64 = _load("v64_current.json")
    assert v64["schema_version"] == 64
    hopped = MIGRATIONS[64](copy.deepcopy(v64))
    assert hopped == v64, "the 64->65 identity hop moved something"
    assert applied_hops(64) == list(range(64, SCHEMA_VERSION))
    assert io.project_to_dict(io.project_from_dict(v64)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def test_a_v65_file_loads_through_the_identity_hop_unchanged():
    """Design note 56 D-56.4 (#263): the 65->66 hop is an identity -- ``lra_mesh``
    absent is exactly the v65 meaning."""
    v65 = _load("v65_current.json")
    assert v65["schema_version"] == 65
    hopped = MIGRATIONS[65](copy.deepcopy(v65))
    assert hopped == v65, "the 65->66 identity hop moved something"


def test_the_v67_hop_is_an_identity():
    """v67 -> v68 (design note 64, #275): result shapes only, so a v67 file
    migrates to the v68 fixture with nothing but its stamp changed."""
    v67 = _load("v67_current.json")
    assert v67["schema_version"] == 67
    migrated = migrate(copy.deepcopy(v67))
    assert migrated["schema_version"] == SCHEMA_VERSION
    assert MIGRATIONS[67](copy.deepcopy(v67)) == v67, "the 67->68 hop moved something"
    assert migrated == _load()          # through the v68 hop below, to the v69 fixture


def test_the_v68_hop_blanks_the_default_couple_and_keeps_an_entered_one():
    """v68 -> v69 (design note 52, #306): ``unbal_moment`` is blank-means-derived.

    A stored ``0`` was the old default, never a statement, so it becomes
    ``null`` -- on ``ACRL`` the derivation the default stood in for (#258), on
    every other case the same zero. A non-zero entered couple is kept (entered
    wins, D-52.2): the frozen v68 fixture's Appendix A ``-149,043`` survives."""
    v68 = _load("v68_current.json")
    assert v68["schema_version"] == 68
    hopped = MIGRATIONS[68](copy.deepcopy(v68))
    got = {c["name"]: c["unbal_moment"] for c in hopped["wing_mass"]["cases"]}
    assert got == {"PHAA": None, "TORS": None, "ACRL": -149043}
    assert migrate(copy.deepcopy(v68)) == _load()
    # A v68 dict with no wing_mass, or no cases, passes through.
    bare = {k: v for k, v in copy.deepcopy(v68).items() if k != "wing_mass"}
    assert MIGRATIONS[68](copy.deepcopy(bare)) == bare


def test_the_v66_hop_moves_the_wing_mass_into_the_item_database():
    """Design note 63 D-63.2 (#289, G-63.4): the 66->67 hop is **not** an identity.

    On a file whose wing tie closes (the frozen v66 fixture, the Appendix A
    airplane: 330 lb of WING items against 2 x 165) ``concentrated`` is dropped
    and ``panel_weight_lb`` leaves without an override -- the derived panel is
    the entered one to the pound -- so the loaded airplane equals the current
    fixture's and no delivered number moves. Every row gains a ``carriage``:
    POINT at a non-zero butt line on a WING row, PANEL everywhere else.
    """
    v66 = _load("v66_current.json")
    assert v66["schema_version"] == 66
    assert v66["wing_mass"]["panel_weight_lb"] == 165
    hopped = MIGRATIONS[66](copy.deepcopy(v66))
    assert "panel_weight_lb" not in hopped["wing_mass"]
    assert "concentrated" not in hopped["wing_mass"]
    assert "panel_weight_override_lb" not in hopped["wing_mass"], "165 = 330 / 2: no override"
    assert "migration_notes" not in hopped, "nothing dropped, nothing to say"
    for row in hopped["weight"]["items"]:
        want = "point" if row.get("component") == "wing" and row.get("y") else "panel"
        assert row["carriage"] == want, row["name"]
    assert applied_hops(66) == [66, 67, 68]   # v67 (note 64) is an identity; v68 (note 52) blanks zeros
    assert io.project_to_dict(io.project_from_dict(v66)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def _v66_with_wing_masses(panel=165.0, concentrated=(), items=None):
    """A v66 dict built from the frozen fixture with the wing mass edited."""
    d = copy.deepcopy(_load("v66_current.json"))
    d["wing_mass"]["panel_weight_lb"] = panel
    d["wing_mass"]["concentrated"] = [dict(c) for c in concentrated]
    if items is not None:
        d["weight"]["items"] = items
    return d


def test_the_v66_hop_drops_a_concentrated_list_the_items_already_carry():
    """R-63.3: where the tie closes the entries are dropped and named once.

    The items carry a 100 lb wing row at butt line 40 and the ``concentrated``
    list carries the same 50 lb per side: converting it would double-count.
    The hop drops it, stamps the row POINT, and the note names what went; the
    loaded ``Project`` states it on ``migration_notes`` and ``validation``
    on the Weight & CG page, and a save has nothing left to say.
    """
    d = _v66_with_wing_masses(
        concentrated=[{"name": "store", "weight_lb": 50.0, "x": 83.0, "y": 40.0, "z": 87.0}])
    d["weight"]["items"].append({
        "name": "Store, right", "weight_lb": 50.0, "x": 83.0, "y": 40.0, "z": 87.0,
        "ixx": 0.0, "iyy": 0.0, "izz": 0.0, "kind": "empty", "component": "wing",
        "consumable": False, "wing_fraction": 0.0})
    d["weight"]["items"].append({
        "name": "Store, left", "weight_lb": 50.0, "x": 83.0, "y": -40.0, "z": 87.0,
        "ixx": 0.0, "iyy": 0.0, "izz": 0.0, "kind": "empty", "component": "wing",
        "consumable": False, "wing_fraction": 0.0})
    hopped = MIGRATIONS[66](copy.deepcopy(d))
    names = [r["name"] for r in hopped["weight"]["items"]]
    assert names.count("Store, right") == 1 and "store, right" not in names
    assert [r["carriage"] for r in hopped["weight"]["items"] if r["name"].startswith("Store")] == ["point", "point"]
    (note,) = hopped["migration_notes"]
    assert "dropped" in note and "store 50 lb/side" in note
    from sloads.validation import consistency_warnings
    project = io.project_from_dict(d)
    assert project.migration_notes == [note]
    assert [w.code for w in consistency_warnings(project) if w.code == "migration_note"] == ["migration_note"]
    assert "migration_notes" not in io.project_to_dict(project)
    assert io.project_from_dict(io.project_to_dict(project)).migration_notes == []


def test_the_v66_hop_converts_a_concentrated_list_the_items_never_had():
    """R-63.3's other branch: an open tie means the mass really is missing, so
    each entry becomes two EMPTY WING rows, carriage POINT, at +-y -- and the
    tie closes on the migrated file (G-63.4's synthetic case)."""
    d = _v66_with_wing_masses(
        concentrated=[{"name": "tip tank", "weight_lb": 40.0, "x": 90.0, "y": 200.0, "z": 88.0}])
    hopped = MIGRATIONS[66](copy.deepcopy(d))
    added = [r for r in hopped["weight"]["items"] if r["name"].startswith("tip tank")]
    assert [(r["name"], r["weight_lb"], r["y"], r["carriage"], r["component"], r["kind"])
            for r in added] == [("tip tank, left", 40.0, -200.0, "point", "wing", "empty"),
                                ("tip tank, right", 40.0, 200.0, "point", "wing", "empty")]
    assert "converted" in hopped["migration_notes"][0]
    project = io.project_from_dict(d)
    from sloads import mass_distribution as md
    state = md.database_mass_state(project)
    assert md.wing_state_tie(state).ok
    assert [m.name for m in state.point_masses] == ["tip tank, right"]
    assert project.wing_mass.panel_weight_override_lb is None


def test_the_v66_hop_keeps_a_converted_centreline_entry_as_a_point_mass():
    """#296: a ``concentrated`` entry at y = 0 converts to one doubled WING row,
    carriage POINT, and the stamp does not re-type it PANEL -- the mass stays
    in the point list and no ``panel_weight_override_lb`` is written."""
    d = _v66_with_wing_masses(
        concentrated=[{"name": "centre tank", "weight_lb": 40.0, "x": 90.0, "y": 0.0, "z": 88.0}])
    hopped = MIGRATIONS[66](copy.deepcopy(d))
    added = [r for r in hopped["weight"]["items"] if r["name"] == "centre tank"]
    assert [(r["weight_lb"], r["y"], r["carriage"], r["component"], r["kind"])
            for r in added] == [(80.0, 0.0, "point", "wing", "empty")]
    assert "panel_weight_override_lb" not in hopped["wing_mass"]
    assert [n for n in hopped["migration_notes"] if "converted" in n] and len(hopped["migration_notes"]) == 1
    project = io.project_from_dict(d)
    from sloads import mass_distribution as md
    state = md.database_mass_state(project)
    assert md.wing_state_tie(state).ok
    assert [m.name for m in state.point_masses] == ["centre tank"]
    assert project.wing_mass.panel_weight_override_lb is None


def test_the_v66_hop_keeps_an_entered_panel_that_differs_as_the_override():
    """D-63.2: ``panel_weight_lb`` survives only where the derived value differs."""
    d = _v66_with_wing_masses(panel=150.0)
    hopped = MIGRATIONS[66](copy.deepcopy(d))
    assert hopped["wing_mass"]["panel_weight_override_lb"] == 150.0
    assert any("panel_weight_override_lb" in n for n in hopped["migration_notes"])
    project = io.project_from_dict(d)
    from sloads import mass_distribution as md
    assert md.panel_weight(project) == 150.0 and md.derived_panel_weight(project) == 165.0


def test_a_v63_vn_point_reads_its_single_case_ref_into_the_list():
    """The identity above, said in the field it is about (note 44 OR-200).

    A persisted v63 envelope carries at most one ``case_ref`` per point; it must
    come back as a one-element ``case_refs``, and a point with none as an empty
    list -- not as a list holding ``None``, which every reader would then have to
    filter.
    """
    point = {"case": 14, "condition": "BAL A", "config": "CRUISE", "cg": "CG1",
             "altitude_ft": 0.0, "v_eas_kt": 121.3, "nz": 1.0, "alpha_deg": 0.6,
             "g_corr": 1.017, "cl": 0.37, "m_wf": -9420.0, "lzw": 3397.0,
             "lt": 19.3, "dx": 278.7,
             "case_ref": {"case_id": "VT-01", "component": "vtail",
                          "condition": "23.441", "far_reference": "23.441"}}
    carried = io._vn_point_from_dict(point)
    assert [r.case_id for r in carried.case_refs] == ["VT-01"]
    assert carried.case_refs[0].component == "vtail"

    bare = dict(point)
    del bare["case_ref"]
    assert io._vn_point_from_dict(bare).case_refs == []
    assert io._vn_point_from_dict(dict(bare, case_ref=None)).case_refs == []


def test_a_v62_engine_reads_back_with_no_thrust_line_and_a_clockwise_propeller():
    """The identity above, said in the fields it is about: a file written before
    the thrust line existed comes back with both points at the origin -- this
    schema's "not entered" for an optional station, the sentinel
    ``LandingGearInput.attach`` already uses -- and clockwise rotation."""
    project = io.project_from_dict(_load("v62_current.json"))
    for engine in project.engines:
        assert engine.thrust_line_aft == (0.0, 0.0, 0.0)
        assert engine.thrust_line_fwd == (0.0, 0.0, 0.0)
        assert engine.prop_direction is RotorDirection.CLOCKWISE


def test_the_v60_fixture_hops_its_nulls_through():
    """The branch every shipped file actually takes: not entered stays not
    entered, and the result is the current fixture."""
    v60 = _load("v60_current.json")
    assert all(s.get("front_spar_pct") is None and s.get("rear_spar_pct") is None
               for s in v60["geometry"]["surfaces"]), "the fixture stopped being blank"
    assert applied_hops(60) == list(range(60, SCHEMA_VERSION))
    assert io.project_to_dict(io.project_from_dict(v60)) == \
           io.project_to_dict(io.project_from_dict(_load()))


def test_a_degenerate_planform_hops_to_not_entered():
    """No positive root chord, no station to compute -- and ``carry_through``
    already refuses that geometry from the other side, so ``null`` is the honest
    answer rather than a station derived from a chord that does not exist."""
    d = {"geometry": {"surfaces": [
        {"leading_edge": [[45.0, 0.0]], "trailing_edge": [[45.0, 0.0]],
         "front_spar_pct": 0.20, "rear_spar_pct": 0.60},
        {"leading_edge": [], "trailing_edge": [], "front_spar_pct": 0.20,
         "rear_spar_pct": 0.60},
    ]}}
    out = MIGRATIONS[60](d)
    for surface in out["geometry"]["surfaces"]:
        assert surface["front_spar_x_in"] is None
        assert surface["rear_spar_x_in"] is None


def test_migrate_does_not_mutate_the_callers_dict():
    """The GUI hands the same dict to the JSON editor after loading it."""
    original = _load()
    snapshot = copy.deepcopy(original)
    migrate(original)
    assert original == snapshot


def test_migrate_is_idempotent():
    once = migrate(_load())
    assert migrate(once) == once


def test_applied_hops_matches_the_chain():
    assert applied_hops(SCHEMA_VERSION) == []            # nothing at/above current
    assert applied_hops(SUPPORTED_FLOOR) == sorted(MIGRATIONS) == \
        list(range(SUPPORTED_FLOOR, SCHEMA_VERSION))


# --------------------------------------------------------------------------- #
# 3. The acceptance criterion: no project changes on the way through
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "name", sorted(f for f in os.listdir(_EXAMPLES) if f.endswith(".project.json"))
)
def test_every_example_round_trips_unchanged(name):
    """Assert on the round-tripped dict, not the file: the load must be a no-op
    for a current project, or a user's saved work drifts every time they open it."""
    path = os.path.join(_EXAMPLES, name)
    once = io.project_to_dict(io.load_project(path))
    twice = io.project_to_dict(io.project_from_dict(once))
    assert twice == once


def test_the_frozen_fixture_and_the_examples_agree_on_the_version():
    """Two independent copies of 'current' -- if they can disagree, one of them
    is stale and the gate's own tests would be testing the wrong number."""
    fixture = _load()["schema_version"]
    for name in sorted(f for f in os.listdir(_EXAMPLES) if f.endswith(".project.json")):
        with open(os.path.join(_EXAMPLES, name), encoding="utf-8") as fh:
            assert json.load(fh)["schema_version"] == fixture, name


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
