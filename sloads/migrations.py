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
    "0.8.9": 76,
    "0.9.0": 80,
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


def _hop_75(d: Dict[str, Any]) -> Dict[str, Any]:
    """v75 -> v76 (design note 51 D-51.7a/D-51.12, #334): ``InducedRoll``
    drops ``htail_ratio`` and gains ``stations``. Both are result fields no
    project file carries, so there is no key to drop. An identity -- the
    horizontal tail's new conditions are the ruling's, not the hop's."""
    return d


#: The five parametric wing scalars v77 drops (design note 69 D-69.2): copies
#: of the stored ``wing`` planform that nothing reads for a load.
_PARAMETRIC_WING_KEYS = ("wing_area_sqft", "aspect_ratio", "taper_ratio",
                         "le_sweep_deg", "le_root_x")


def _hop_76(d: Dict[str, Any]) -> Dict[str, Any]:
    """v76 -> v77 (design note 69 D-69.12, #377/#378): one owner per geometry
    quantity on the Geometry page.

    * ``geometry.parametric.body_drag_waterline_z`` moves to
      ``geometry.fuselage.body_drag_waterline_z`` (unchanged meaning);
    * ``geometry.empennage.airplane_length_in`` (SELECT LF) moves to
      ``geometry.fuselage.airplane_length_in``, where it is now a collapsed
      override of the outline's own length;
    * the five parametric wing keys are dropped -- the stored ``wing`` surface
      is the planform, and ``configuration`` integrates it directly;
    * ``geometry.fuselage`` is created with an empty section table when a
      moved value is non-zero and the file had no outline, so the value is
      kept.

    No delivered load moves: a typed LF stays typed (it governs as before), the
    drag waterline keeps its value, and the dropped keys fed no load. A dropped
    wing value that is non-zero is stated once in the migration notes, so the
    user knows the file carried one.
    """
    geometry = d.get("geometry")
    if not isinstance(geometry, dict):
        return d
    moved: Dict[str, float] = {}
    parametric = geometry.get("parametric")
    if isinstance(parametric, dict):
        bdw = parametric.pop("body_drag_waterline_z", None)
        if bdw:
            moved["body_drag_waterline_z"] = bdw
        dropped = {k: parametric.pop(k) for k in _PARAMETRIC_WING_KEYS
                   if k in parametric}
        stated = {k: v for k, v in dropped.items()
                  if v and not (k == "taper_ratio" and v == 1.0)}
        if stated:
            d.setdefault("migration_notes", []).append(
                "geometry.parametric: the parametric wing scalars "
                + ", ".join(f"{k}={v}" for k, v in stated.items())
                + " were dropped at v77 (design note 69 D-69.2); the stored "
                "wing surface is the planform the analysis integrates.")
    empennage = geometry.get("empennage")
    if isinstance(empennage, dict):
        lf = empennage.pop("airplane_length_in", None)
        if lf:
            moved["airplane_length_in"] = lf
    if moved:
        fuselage = geometry.get("fuselage")
        if not isinstance(fuselage, dict):
            fuselage = {"sections": []}
            geometry["fuselage"] = fuselage
        fuselage.update(moved)
    return d


def _hop_77(d: Dict[str, Any]) -> Dict[str, Any]:
    """v77 -> v78 (design note 70 D-70.3, #382): ``MassCase`` gains
    ``ceiling`` and ``Project.mass`` becomes one row per CG case plus the
    labelled database-ceiling row, last. The stored v77 block is the one
    all-items row under the name "itemized loading", which is now the
    ceiling: it is dropped here and re-derived at the next persist (the GUI
    calls ``refresh_derived`` after every one) -- ``Project.mass`` is derived
    data (``derived.py``; ``refresh_mass`` is its one writer), so nothing the
    user entered is lost and the slice cannot carry a stale shape. No
    delivered load moves: no load module reads the slice.
    """
    d.pop("mass", None)
    return d


def _hop_78(d: Dict[str, Any]) -> Dict[str, Any]:
    """v78 -> v79 (#384): ``MassItem`` gains ``gear`` (``None`` = not a gear
    row, which is exactly the v78 meaning of every row). An identity hop: an
    additive field whose absence is its own default (#310)."""
    return d


def _hop_79(d: Dict[str, Any]) -> Dict[str, Any]:
    """v79 -> v80 (design note 71, #383): one owner per mass quantity.

    * ``geometry.empennage.vtail.gross_weight_lb`` (SELECT GW) is **deleted**
      (D-71.4): the fin's design weight is the airplane's MTOW. A stored value
      that differs from the file's MTOW is stated once in the migration notes;
      one that equals it (every shipped fixture) is dropped silently.
    * ``fuselage_mass.ref_waterline`` **moves** to
      ``geometry.fuselage.beam_waterline_z`` (D-71.7): the body beam's
      waterline is geometry. The outline record is created with an empty
      section table when the value is non-zero and the file had none.
    * ``tail_mass[].control_load_mode`` / ``hinges_span_in`` /
      ``actuator_span_in`` **move** to the tail's control surface row in
      ``geometry.surfaces[]`` (D-71.9; htail -> elevator, vtail -> rudder): a
      row with no such surface has its values stated once and dropped.

    No delivered load moves: every moved value keeps its reader, and the
    deleted one equalled MTOW on every shipped file.
    """
    notes: List[str] = []
    geometry = d.get("geometry")
    if not isinstance(geometry, dict):
        geometry = {}
        d["geometry"] = geometry
    empennage = geometry.get("empennage")
    if isinstance(empennage, dict) and isinstance(empennage.get("vtail"), dict):
        gw = empennage["vtail"].pop("gross_weight_lb", None)
        weight = d.get("weight") if isinstance(d.get("weight"), dict) else {}
        mtow = weight.get("max_takeoff_weight_lb") if weight else None
        if gw and (mtow is None or abs(float(gw) - float(mtow)) > 1e-9):
            notes.append(
                f"geometry.empennage.vtail.gross_weight_lb={gw} was dropped at v80 "
                "(design note 71 D-71.4): the fin's design weight is the airplane's "
                f"max take-off weight ({mtow if mtow is not None else 'not entered'}).")
    fm = d.get("fuselage_mass")
    if isinstance(fm, dict):
        wl = fm.pop("ref_waterline", None)
        if wl:
            fuselage = geometry.get("fuselage")
            if not isinstance(fuselage, dict):
                fuselage = {"sections": []}
                geometry["fuselage"] = fuselage
            fuselage["beam_waterline_z"] = wl
    raw_surfaces = geometry.get("surfaces")
    surfaces: List[Any] = list(raw_surfaces) if isinstance(raw_surfaces, list) else []
    by_name = {str(s.get("name", "")).strip().casefold(): s
               for s in surfaces if isinstance(s, dict)}
    control_of = {"htail": "elevator", "vtail": "rudder"}
    raw_rows = d.get("tail_mass")
    tail_rows: List[Any] = list(raw_rows) if isinstance(raw_rows, list) else []
    for row in tail_rows:
        if not isinstance(row, dict):
            continue
        moved = {k: row.pop(k) for k in ("control_load_mode", "hinges_span_in", "actuator_span_in")
                 if k in row}
        stated = {k: v for k, v in moved.items() if v and v != "smeared"}
        if not stated:
            continue
        control = by_name.get(control_of.get(str(row.get("surface", "")), ""))
        if control is None:
            notes.append(
                f"tail_mass[{row.get('surface')}]: "
                + ", ".join(f"{k}={v}" for k, v in stated.items())
                + " was dropped at v80 (design note 71 D-71.9): the control-load "
                "geometry lives on the control surface's geometry.surfaces[] row, "
                "and this file has none for that tail.")
            continue
        control.update(moved)
    if notes:
        d.setdefault("migration_notes", []).extend(notes)
    return d


#: ``{from_version: hop}`` -- applied in ascending order, each turning a file of
#: version *n* into version *n+1* shape.
MIGRATIONS: Dict[int, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    70: _hop_70,
    71: _hop_71,
    72: _hop_72,
    73: _hop_73,
    74: _hop_74,
    75: _hop_75,
    76: _hop_76,
    77: _hop_77,
    78: _hop_78,
    79: _hop_79,
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
