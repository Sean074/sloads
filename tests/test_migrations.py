"""The schema gate and the release-level compatibility rule (#310).

A file written by any release from 0.8.7 on stays readable by every later
release; a schema version that lived only on a development branch is never
promised. `sloads.migrations.migrate` admits the current ``SCHEMA_VERSION`` and
every version the hop chain reaches it from, and raises `SchemaVersionError` for
anything else: older than the floor, newer, or unversioned.

This file pins the gate (section 1), the machinery the chain runs on (section
2), the rule itself (section 3: every release has its schema recorded and
frozen, every frozen file still loads, and the chain has no gap), and that a
load changes no current project (section 4).

The fourteen hops that ran v55 to v69, and their frozen fixtures, were deleted
at #310: no release from 0.8.7 on wrote those versions.
"""

import copy
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.migrations import (
    MIGRATIONS,
    RELEASED_SCHEMAS,
    SUPPORTED_FLOOR,
    SchemaVersionError,
    applied_hops,
    migrate,
    source_schema_version,
)
from sloads.models import SCHEMA_VERSION

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_FIXTURES = os.path.join(_HERE, "fixtures_schema")
_EXAMPLES = os.path.join(_ROOT, "examples")
_RECORD = os.path.join(_ROOT, "docs", "90_record")
_CURRENT = os.path.join(_EXAMPLES, "ga6_normal.project.json")

#: The first release the rule covers (owner, 2026-09-26).
_FIRST_COVERED = (0, 8, 7)


def _load(path=_CURRENT):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# 1. The gate
# --------------------------------------------------------------------------- #
def test_a_current_file_passes_through_untouched():
    current = _load()
    assert current["schema_version"] == SCHEMA_VERSION, "the example went stale"
    assert migrate(current) == current


@pytest.mark.parametrize("version", [SUPPORTED_FLOOR - 1, SUPPORTED_FLOOR - 10, 55, 0])
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
# 2. The machinery the chain runs on
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


def test_the_v73_hop_reads_every_row_as_not_usable_fuel():
    """Gate 8's hop half (note 67 D-67.10): a v72 file loads, and the hop infers
    no tank from its name -- every row, and every entered ballast, reads False."""
    d = _load()
    d["schema_version"] = 72
    for item in d["weight"]["items"]:
        item.pop("usable_fuel", None)
    project = io.project_from_dict(d)
    assert project.weight.items
    assert not any(it.usable_fuel for it in project.weight.items)


def test_the_v74_hop_reads_a_v73_one_engine_out_slice_as_vs_at_sea_level():
    """#333: a v73 ``one_engine_out`` slice loads with no VMC (VS stands in,
    stated) and the low end at sea level -- the hop adds nothing, the
    dataclass defaults are the meaning."""
    path = os.path.join(os.path.dirname(_CURRENT), "atr42_100.project.json")
    d = _load(path)
    d["schema_version"] = 73
    d["one_engine_out"].pop("vmc_kt", None)
    d["one_engine_out"].pop("takeoff_altitude_ft", None)
    project = io.project_from_dict(d)
    assert project.one_engine_out.vmc_kt is None
    assert project.one_engine_out.takeoff_altitude_ft == 0.0


def test_a_hops_note_reaches_the_project_and_is_stated_once():
    """A hop that changes an entered value says so through ``migration_notes``,
    which the reader carries onto the project (never persisted) and
    ``validation`` states."""
    from sloads import validation

    def _hop(d):
        d.setdefault("migration_notes", []).append("test hop: nothing lost")
        return d

    original = dict(MIGRATIONS)
    try:
        MIGRATIONS[SCHEMA_VERSION] = _hop
        project = io.project_from_dict(_load())
    finally:
        MIGRATIONS.clear()
        MIGRATIONS.update(original)
    assert project.migration_notes == ["test hop: nothing lost"]
    assert "migration_notes" not in io.project_to_dict(project)
    said = [w.message for w in validation.consistency_warnings(project)
            if w.code == "migration_note"]
    assert said == ["test hop: nothing lost"]


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
    assert applied_hops(SUPPORTED_FLOOR) == sorted(MIGRATIONS)


# --------------------------------------------------------------------------- #
# 3. The rule: every release's schema is recorded, frozen and still read
# --------------------------------------------------------------------------- #
def _released_versions():
    """Every release the changelog and its archives name, as version tuples."""
    found = set()
    for name in os.listdir(_RECORD):
        if name.startswith("CHANGELOG") and name.endswith(".md"):
            with open(os.path.join(_RECORD, name), encoding="utf-8") as fh:
                found.update(re.findall(r"^## \[(\d+)\.(\d+)\.(\d+)\]", fh.read(), re.M))
    return {tuple(int(p) for p in v) for v in found}


def _release_key(version):
    return ".".join(str(p) for p in version)


def test_every_release_from_0_8_7_records_its_schema():
    """The cut adds the row: ``build_changelog`` writes the release header, and
    this goes red until ``RELEASED_SCHEMAS`` names the schema that release
    shipped (``RELEASE_PROCESS.md`` section 4)."""
    released = _released_versions()
    assert (0, 8, 6) in released, "the changelog parse found nothing -- the guard would pass vacuously"
    missing = sorted(_release_key(v) for v in released
                     if v >= _FIRST_COVERED and _release_key(v) not in RELEASED_SCHEMAS)
    assert not missing, (
        f"releases {missing} are in the changelog but not in "
        "sloads.migrations.RELEASED_SCHEMAS: add each with the SCHEMA_VERSION it "
        "shipped, and freeze tests/fixtures_schema/release_<X.Y.Z>.json")


def test_released_schemas_are_releases_and_rise_with_them():
    rows = sorted(RELEASED_SCHEMAS.items(),
                  key=lambda kv: tuple(int(p) for p in kv[0].split(".")))
    for release, version in rows:
        assert tuple(int(p) for p in release.split(".")) >= _FIRST_COVERED, release
        assert isinstance(version, int) and version <= SCHEMA_VERSION, (release, version)
    versions = [v for _, v in rows]
    assert versions == sorted(versions), "a later release shipped an older schema"


def test_every_released_schema_is_frozen_and_still_loads():
    """The promise itself: the frozen file each release wrote reads today."""
    frozen = {f for f in os.listdir(_FIXTURES) if f.endswith(".json")} \
        if os.path.isdir(_FIXTURES) else set()
    expected = {f"release_{release}.json" for release in RELEASED_SCHEMAS}
    assert frozen == expected, (
        f"tests/fixtures_schema holds {sorted(frozen)} but RELEASED_SCHEMAS "
        f"expects {sorted(expected)}: one frozen file per released schema, no other")
    for release, version in RELEASED_SCHEMAS.items():
        d = _load(os.path.join(_FIXTURES, f"release_{release}.json"))
        assert d["schema_version"] == version, release
        io.project_from_dict(d)


def _leaves(node, path=()):
    """``(path, value)`` for every scalar in a JSON tree."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _leaves(value, path + (key,))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _leaves(value, path + (i,))
    else:
        yield path, node


def _at(tree, path):
    for key in path:
        tree = tree[key]
    return tree


@pytest.mark.parametrize("release", sorted(RELEASED_SCHEMAS))
def test_every_value_a_released_file_carries_survives_the_read(release):
    """Loading is not reading (#322): the reader drops a key it does not know,
    so a hop that misses a later rename still loads -- with the renamed value
    silently gone. Every scalar the migrated frozen file carries must come back
    out of the model at the same path with the same value. A hop that renames a
    field moves the value; a hop that drops it states so here, by path."""
    migrated = migrate(_load(os.path.join(_FIXTURES, f"release_{release}.json")))
    read = io.project_to_dict(io.project_from_dict(copy.deepcopy(migrated)))
    lost, changed = [], []
    for path, value in _leaves(migrated):
        try:
            got = _at(read, path)
        except (KeyError, IndexError, TypeError):
            lost.append(path)
            continue
        if got != value:
            changed.append((path, value, got))
    assert not lost, f"release {release}: the read dropped {lost[:10]}"
    assert not changed, f"release {release}: the read changed {changed[:10]}"


def test_the_chain_runs_without_a_gap_from_the_oldest_released_schema():
    """The floor is the oldest released schema, and every bump from there to
    current registered its hop -- a bump with no hop would not refuse a stale
    file, the tolerant reader would misread it."""
    assert SUPPORTED_FLOOR == min(RELEASED_SCHEMAS.values(), default=SCHEMA_VERSION)
    assert sorted(MIGRATIONS) == list(range(SUPPORTED_FLOOR, SCHEMA_VERSION))


def test_the_release_parse_reads_a_header():
    """Test the parse, so the changelog guard cannot pass on a format drift."""
    assert re.findall(r"^## \[(\d+)\.(\d+)\.(\d+)\]", "x\n## [0.8.7] — 2026-10-01\n", re.M) \
        == [("0", "8", "7")]


# --------------------------------------------------------------------------- #
# 4. The acceptance criterion: no project changes on the way through
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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
