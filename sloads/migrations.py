"""Schema gate: a ``project.json`` is read if a release wrote it, or not at all.

**The rule (#310, owner 2026-09-26).** A file written by any release from 0.8.7
on stays readable by every later release; a schema version that existed only on
a development branch between two releases is never promised. So a file is
accepted when its ``schema_version`` is :data:`~sloads.models.SCHEMA_VERSION` or
a version the hop chain reaches it from (:data:`SUPPORTED_FLOOR`, the oldest
released schema); anything older, newer or unversioned raises
:class:`SchemaVersionError` naming both versions. Refusing is the honest answer
-- silently reshaping a file this build cannot read would present its numbers
as this build's.

The gate lives here rather than in a front-end because
:func:`sloads.io.project_from_dict` funnels every load -- CLI, GUI, every
test -- through :func:`migrate`. One owner, one refusal, no front-end deciding
compatibility for itself. The standing guard is
``tests/test_app_shell.py::test_no_gui_decides_whether_a_file_is_readable``.

**The chain.** :data:`MIGRATIONS` is a ``{from_version: hop}`` chain applied in
ascending order, each hop turning a file of version *n* into *n+1* shape:

    v_file --hop--> v_file+1 --hop--> ... --> SCHEMA_VERSION --> one tolerant reader

Every ``SCHEMA_VERSION`` bump from the first released schema on registers its
hop, identity or not -- the reader drops a key it does not know, so a bump with
no hop would not refuse a stale file, it would misread it. A hop that has
something to tell the user writes it to the transient ``migration_notes`` list,
which ``io.project_from_dict`` carries onto ``Project.migration_notes`` (never
persisted) for ``validation`` to state once.

**Released schemas.** :data:`RELEASED_SCHEMAS` records the version each release
shipped, added at the release cut with a frozen copy of one example at that
version (``tests/fixtures_schema/release_<X.Y.Z>.json``,
``RELEASE_PROCESS.md`` section 4). ``tests/test_migrations.py`` holds the policy
structurally: every release the changelog names from 0.8.7 on has a row, every
row's fixture loads through the chain, and the chain runs without a gap from the
oldest released schema to the current one.

The hops from v55 to v69 were deleted at #310 with their fixtures: no release
from 0.8.7 on wrote those versions. They are in this file's git history.

Pure: dicts in, dicts out, no I/O.
"""

import copy
from typing import Any, Callable, Dict, List, Mapping

from .models import SCHEMA_VERSION


class SchemaVersionError(ValueError):
    """A project file is not at a version this build reads.

    A ``ValueError``, so it lands in the documented error contract
    (``00_program_overview.md``) and every front-end's existing load handling
    reports it without a new branch.
    """


#: The schema version each release shipped, keyed by release, from 0.8.7 on
#: (#310). A row is added at the release cut, never on a development branch.
RELEASED_SCHEMAS: Dict[str, int] = {
    "0.8.7": 70,
    "0.8.8": 73,
}

def _hop_70(d: Dict[str, Any]) -> Dict[str, Any]:
    """v70 -> v71 (design note 66 D-66.12a, #319): ``EngineInput`` gains
    ``windmill_drag_cd``, optional, whose blank is exactly the v70 meaning (the
    one-engine-out hub drag is the Glauert bound). An identity."""
    return d


def _hop_71(d: Dict[str, Any]) -> Dict[str, Any]:
    """v71 -> v72 (design note 51 §9, #328): ``TipTransfer`` gains ``mxx``,
    ``paired_case`` and ``induced``, each defaulted to the v71 meaning (no roll
    at the fin tip, no pairing record). An identity."""
    return d


def _hop_72(d: Dict[str, Any]) -> Dict[str, Any]:
    """v72 -> v73 (design note 67 D-67.10, #283): ``MassItem`` gains
    ``usable_fuel``, defaulted ``False``. An identity, and deliberately so: which
    rows are fuel is an input (note 63 OV-1), so the hop names no tank by its
    name -- the OEW mass set states every row it kept instead."""
    return d


def _hop_73(d: Dict[str, Any]) -> Dict[str, Any]:
    """v73 -> v74 (#333): ``OneEngineOutInput`` gains ``vmc_kt`` (blank: VS
    stands as the substitute, the v73 low end) and ``takeoff_altitude_ft``
    (default 0). An identity -- but not a no-op on loads: the low-end case
    moves from the shoulder altitude to the take-off altitude, which is the
    ruling, not the hop's doing."""
    return d


def _hop_74(d: Dict[str, Any]) -> Dict[str, Any]:
    """v74 -> v75 (#332): ``Rotor.direction`` is retired; a rotor's spin
    sense is its signed ``max_rpm`` alone. The key is dropped.

    No delivered number moves: the field was read by nothing, so every load
    a v74 file produced already followed the sign of ``max_rpm``. A rotor
    whose retired field said ``CC`` against a positive rpm is the one case
    where the file disagreed with itself; the hop keeps the rpm -- what the
    loads were always computed from -- and says so, naming the rotor, rather
    than refusing a file a release wrote. ``CW`` (the default the writer
    stamped on every rotor) against a negative rpm carries no intent and is
    dropped silently.
    """
    for e_i, engine in enumerate(d.get("engines") or []):
        for r_i, rotor in enumerate(engine.get("rotors") or []):
            direction = rotor.pop("direction", None)
            rpm = rotor.get("max_rpm")
            if direction == "CC" and isinstance(rpm, (int, float)) and rpm > 0:
                d.setdefault("migration_notes", []).append(
                    f"engines[{e_i}].rotors[{r_i}]: the retired rotor direction "
                    f"said counter-clockwise but max_rpm is +{rpm}; the rotor "
                    "spins clockwise, as every earlier load assumed. Enter a "
                    "negative max_rpm if it counter-rotates (#332).")
    return d


#: ``{from_version: hop}`` -- applied in ascending order, each turning a file of
#: version *n* into version *n+1* shape.
MIGRATIONS: Dict[int, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    70: _hop_70,
    71: _hop_71,
    72: _hop_72,
    73: _hop_73,
    74: _hop_74,
}

#: The oldest project version this build reads: the oldest released schema, or
#: the current one while no release has been recorded.
SUPPORTED_FLOOR = min(RELEASED_SCHEMAS.values(), default=SCHEMA_VERSION)


def source_schema_version(d: Mapping[str, Any]) -> int:
    """The ``schema_version`` a project dict carries, or ``-1`` if it carries none.

    ``-1`` rather than a floor default: an unversioned dict is not an old project
    file, it is a dict nobody wrote as one (``project_to_dict`` has stamped the
    version since the versioned era began). The gate must be able to say so.
    """
    if not isinstance(d, Mapping):
        # A JSON file whose top level is a list (or a bare scalar) is not a
        # project of any version. Said as the error contract's ``ValueError``
        # rather than an ``AttributeError`` on ``.get`` -- which reached the
        # CLI as a traceback on all four routes (the 0.8.4 closure review).
        raise ValueError(
            f"a project file must hold a JSON object, not {type(d).__name__}")
    version = d.get("schema_version")
    return version if isinstance(version, int) else -1


def migrate(d: Dict[str, Any]) -> Dict[str, Any]:
    """Return ``d`` at the current schema, or raise :class:`SchemaVersionError`.

    Works on a deep copy -- the caller's dict is never mutated, which matters
    because the GUI hands the same dict to the JSON editor.
    """
    version = source_schema_version(d)
    if version < SUPPORTED_FLOOR or version > SCHEMA_VERSION:
        found = "no schema_version" if version < 0 else f"schema {version}"
        supported = (f"schema {SCHEMA_VERSION} only" if SUPPORTED_FLOOR == SCHEMA_VERSION
                     else f"schemas {SUPPORTED_FLOOR}-{SCHEMA_VERSION}")
        raise SchemaVersionError(
            f"This file is not readable by this build: {found}; this build reads "
            f"{supported}. A file no release wrote is not migrated -- rebuild "
            "the project on the current version."
        )

    out = copy.deepcopy(d)
    for hop_from in sorted(MIGRATIONS):
        if version <= hop_from:
            out = MIGRATIONS[hop_from](out)
    out["schema_version"] = SCHEMA_VERSION
    return out


def applied_hops(from_version: int) -> List[int]:
    """Which hops :func:`migrate` would run for a file of ``from_version``.

    Empty while the chain is. Kept as the chain's own accessor, so the
    tests and a future "this file was migrated from vN" provenance line read the
    answer from one place.
    """
    return [h for h in sorted(MIGRATIONS) if from_version <= h]
