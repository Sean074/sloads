"""Schema gate: a ``project.json`` is read at the current version, or not at all.

**The rule (#93, 2026-08-25).** This project is pre-production. No analysis
performed with an earlier build has to stay readable, so a file is accepted only
when its ``schema_version`` is :data:`~sloads.models.SCHEMA_VERSION` or a
version the hop chain reaches it from (:data:`SUPPORTED_FLOOR`); anything
older, newer or unversioned raises :class:`SchemaVersionError` naming both
versions. Refusing is the honest answer — an old file's numbers were produced by
a different tool, and silently reshaping them into the current schema presents
them as this build's.

The gate lives here rather than in a front-end because
:func:`sloads.io.project_from_dict` funnels every load — CLI, GUI, every
test — through :func:`migrate`. One owner, one refusal, no front-end deciding
compatibility for itself. The standing guard is
``tests/test_app_shell.py::test_no_gui_decides_whether_a_file_is_readable``.

**The machinery is kept, empty.** :data:`MIGRATIONS` is a ``{from_version: hop}``
chain applied in ascending order, each hop turning a file of version *n* into
*n+1* shape:

    v_file --hop--> v_file+1 --hop--> ... --> SCHEMA_VERSION --> one tolerant reader

The chain holds one live hop today — the v55→v56 identity of note 36's additive
fields (OV-10, #97) — so :data:`SUPPORTED_FLOOR` is 55. The hops since have been
identities over additive fields; :func:`_hop_60` is the first that **converts a
value**, because dropping a field whose replacement is computable from the same
file would lose an entered carry-through (note 50 OR-127), and :func:`_hop_66`
the second, moving the wing's mass into the item database (note 63). A hop that
has something to tell the user writes it to the transient ``migration_notes``
list, which ``io.project_from_dict`` carries onto ``Project.migration_notes``
(never persisted) for ``validation`` to state once. At production the floor
drops to whatever version ships and hops register from there forward — the
shape of that work is unchanged.

**The twelve retired hops** (v18–v54, plus the v0 bare-``EngineInput`` branch
from the Phase-0 ``engloads`` era) covered every shape change from v18 to v55.
They are recorded, with the archaeology table that reconstructed which schema
version each legacy path belonged to, in
``docs/90_record/11_completed_development_to_0.5.0.md`` (M4-10) and in this
file's own git history. The six bundled examples were re-stamped through that
chain at the cut, verified output-neutral: the ``Project`` loaded from each old
file and from its re-stamped replacement are identical dicts, and
``tests/fixtures_imperial/digests.json`` did not move.

The examples are now the floor's only customers, so
``tests/test_schema_guards.py::test_every_bundled_example_is_written_at_the_current_version``
turns the next ``SCHEMA_VERSION`` bump into a red suite until they are re-stamped.

Pure: dicts in, dicts out, no I/O.
"""

from __future__ import annotations

import copy
import math
from typing import Any, Callable, Dict, List, Mapping

from .models import SCHEMA_VERSION


class SchemaVersionError(ValueError):
    """A project file is not at the version this build reads.

    A ``ValueError``, so it lands in the documented error contract
    (``00_program_overview.md``) and every front-end's existing load handling
    reports it without a new branch.
    """


def _hop_55(d: Dict[str, Any]) -> Dict[str, Any]:
    """v55 -> v56 (note 36 OV-10, #97): **identity**.

    v56 adds three input fields with backward-benign defaults --
    ``SurfaceInput.tip_cap_width_in`` (0.0 = square tip, the v55 meaning) and
    the ``EngineInput.engine_mass_item``/``prop_mass_item`` selectors ("" = no
    derivation, the v55 behaviour). The readers take the defaults for absent
    keys, so the hop changes nothing; it exists because the gate refuses any
    version it has no hop for, and an additive field is still a shape change.
    """
    return d


def _hop_56(d: Dict[str, Any]) -> Dict[str, Any]:
    """v56 -> v57 (note 37 LF-8, #123): **semantic** -- the landing N inversion.

    ``landing.gear_load_factor`` (an NLG override, ``0.0`` = unset) is replaced
    by ``landing.airplane_load_factor`` (the governing N, ``None`` = unset):
    ``N = NLG_old + L``, the vertical-equilibrium identity at peak load. Not an
    identity hop, deliberately -- the field's role inverts from input to derived,
    and re-pointing an old project at the energy equation instead would move its
    NLG (ga6 p230: 2.5 entered vs 2.4281 energy). The hop reproduces every NLG
    the reaction path read, so no load number moves.
    """
    landing = d.get("landing")
    if isinstance(landing, dict):
        nlg = landing.pop("gear_load_factor", 0.0)
        if nlg:
            landing["airplane_load_factor"] = nlg + landing.get("lift_factor", 0.667)
    return d


def _hop_57(d: Dict[str, Any]) -> Dict[str, Any]:
    """v57 -> v58 (design note 38 GF-6/GF-7, #134): **identity**.

    v58 adds ``LoadValue.frame`` -- the reference frame a value is stated in
    (:mod:`sloads.frames`), which the delivered CSV reads to keep the ground-line
    set out of it. ``""`` (no frame named) is exactly the v57 meaning, and it is
    the default, so a v57 file loads bit-identical. ``LoadValue`` is persisted
    inside ``critical.conditions[].loads``, which is why an added display-neutral
    field is still a shape change and still gets a hop.
    """
    return d


def _hop_58(d: Dict[str, Any]) -> Dict[str, Any]:
    """v58 -> v59 (#141): **identity**.

    v59 adds ``LoadValue.point`` -- the named application point a force is
    delivered to (:data:`sloads.gear_loads.AXLE` /
    :data:`~sloads.gear_loads.GROUND_CONTACT`), which the delivered CSV states
    beside the coordinates so a standalone consumer no longer has to compare
    x/y/z back to the geometry to learn whether a case acts at the axle. ``""``
    (no point named) is exactly the v58 meaning and is the default, so a v58
    file loads bit-identical. This is ``_hop_57`` one step on, for the same
    reason: ``LoadValue`` is persisted inside ``critical.conditions[].loads``,
    so an added display-neutral field is still a shape change and still gets a
    hop.
    """
    return d


def _hop_59(d: Dict[str, Any]) -> Dict[str, Any]:
    """v59 -> v60 (design note 47 OR-74): **identity**.

    v60 adds ``LoadValue.symbol`` -- the notation symbol the quantity is written
    as, held on the value so a document's symbol-table guard reads a field
    rather than parsing display prose. ``""`` (no symbol named) is exactly the
    v59 meaning and is the default, so a v59 file loads bit-identical. This is
    ``_hop_58`` one step on, for the same reason: ``LoadValue`` is persisted
    inside ``critical.conditions[].loads``, so an added display-neutral field is
    still a shape change and still gets a hop.
    """
    return d


def _hop_60(d: Dict[str, Any]) -> Dict[str, Any]:
    """v60 -> v61 (design note 50 OR-121/OR-127): **the spar pair becomes stations**.

    ``SurfaceInput.front_spar_pct``/``.rear_spar_pct`` -- fractions of the
    centreline root chord -- are replaced by ``front_spar_x_in``/
    ``rear_spar_x_in``, the fuselage station itself. The first hop in the live
    chain that is not an identity, because it must not lose an entered
    carry-through: a v60 file that typed a fraction has its station computed
    here from **its own polylines**, by the same expression ``carry_through``
    used to apply::

        x = x_LE(root) + pct * (x_TE(root) - x_LE(root))

    so the airplane keeps the carry-through it was analysed with rather than
    silently reverting to the (also changed, 15/65 -> 20/60) default. A ``null``
    fraction hops to a ``null`` station, which is the same "not entered" it
    already meant. A surface whose polylines cannot give a positive root chord
    yields ``null`` too -- there is no station to compute, and ``carry_through``
    already refuses that geometry from the other side.

    No bundled example takes the converting branch: all seven write both keys
    ``null``. It is guarded on a constructed dict
    (``tests/test_schema_guards.py``), which is the only place it can be.
    """
    for surface in (d.get("geometry") or {}).get("surfaces") or []:
        if not isinstance(surface, dict):
            continue
        le = surface.get("leading_edge") or []
        te = surface.get("trailing_edge") or []
        x_le = le[0][0] if le and len(le[0]) >= 1 else None
        x_te = te[0][0] if te and len(te[0]) >= 1 else None
        c_root = None if x_le is None or x_te is None else x_te - x_le
        for pct_key, x_key in (("front_spar_pct", "front_spar_x_in"),
                               ("rear_spar_pct", "rear_spar_x_in")):
            pct = surface.pop(pct_key, None)
            converted = (x_le + pct * c_root
                         if pct is not None and c_root is not None and c_root > 0.0
                         else None)
            # Idempotent, and non-destructive in that order: an entered fraction
            # converts and wins; otherwise the key is only *created*, never
            # overwritten. Without the guard a second pass -- and there is one,
            # because ``project_from_dict`` funnels every load through
            # ``migrate`` -- would find no fraction left to convert and write the
            # station it had just computed back to ``None``.
            if converted is not None or x_key not in surface:
                surface[x_key] = converted
    return d


def _hop_61(d: Dict[str, Any]) -> Dict[str, Any]:
    """v61 -> v62 (owner, 2026-09-07): **identity**.

    v62 adds ``FuselageStation.y``/``.z`` -- the butt line and waterline the
    lumped mass acts at, distinct from ``FuselageMassInput.ref_waterline``, which
    is where the *beam* runs. ``0.0`` on both is exactly the v61 meaning ("not
    entered") and is the default, so a v61 file loads bit-identical and the
    resolver supplies the item database's own weight-weighted centroid as it does
    for a station that never stated one. Ch 15's solve is a symmetric-flight
    vertical beam and reads neither coordinate, so no delivered fuselage load can
    move across this hop.
    """
    return d


def _hop_62(d: Dict[str, Any]) -> Dict[str, Any]:
    """v62 -> v63 (design note 53, owner 2026-09-07): **identity**.

    v63 gives ``EngineInput`` a thrust line as two entered points and the
    propeller's rotation direction. ``None`` on both points is exactly the v62
    state -- the schema carried no thrust line at all -- and the axis then falls
    back to the airplane's forward direction, marked ASSUMED (D-53.3).
    ``CLOCKWISE`` is what every published engine torque already assumed before
    the field existed (D-53.4), so a v62 file loads bit-identical and no
    delivered load moves across this hop.

    The one number that *does* move on a v62 file is the oracle report's section
    10.2, and it moves because D-53.3 supersedes note 44 OR-161: the axis is no
    longer derived from the engine CG to the hub. That is a change of published
    view, not of stored data, so it is not this hop's to carry.
    """
    return d


def _hop_63(d: Dict[str, Any]) -> Dict[str, Any]:
    """v63 -> v64 (design note 44 OR-200, owner 2026-09-07): **identity**.

    v64 replaces ``VnPoint.case_ref`` (one slot) with ``VnPoint.case_refs`` (a
    list): a V-n point is routinely the source of more than one critical
    condition -- on ``ga6_normal`` case 14 is VT-01, VT-02 and VT-03 -- and the
    single slot kept only the last stamp. Nothing read the field outside
    serialisation, so no delivered load moves.

    Identity here because the *reader* carries the hop: a pre-v64 file could
    never hold more than one ref, so ``io._vn_point_from_dict`` reads the
    singular key into a one-element list, which is exactly what the list would
    have held. Rewriting the key here as well would be the same conversion in
    two places, and the reader must keep it regardless -- a persisted envelope
    reaches it through paths that do not run this chain.
    """
    return d


def _hop_64(d: Dict[str, Any]) -> Dict[str, Any]:
    """v64 -> v65 (design note 54 D-54.1/D-54.8, #25 step 2): **identity**.

    v65 is the boundary-line model: ``SurfaceInput.hinge_line`` (the control's
    aerodynamic hinge axis; empty = not entered), a control surface's
    ``trailing_edge`` allowed empty (it then derives from the parent's TE --
    physically one line, D-54.1), and ``LayoutInput.htail_dihedral_deg``
    (declared, physics deferred, D-54.8). The two tail input blocks are also
    physically regrouped into the D-54.1 seam order, which JSON -- storing
    fields by name -- cannot see. Every addition's default is exactly the v64
    meaning: no hinge line existed, every control TE was entered, no dihedral
    was declared. A v64 file therefore loads bit-identical, every typed scalar
    stays authoritative (blank-derives is note 36 OV-1's contract, and blank
    meant "not modelled or derived elsewhere" before too), and no delivered
    load or ``GRID`` moves.
    """
    return d


#: ``{from_version: hop}`` -- applied in ascending order, each turning a file of
#: version *n* into version *n+1* shape. A version that changes shape adds its
def _hop_65(d: Dict[str, Any]) -> Dict[str, Any]:
    """v65 -> v66 (design note 56 D-56.4, #263): **identity**.

    v66 adds one optional slice, ``lra_mesh`` -- four per-member node counts
    for the LRA beam model, each ``None`` for "the default". Absent is exactly
    the v65 meaning, since v65 had no counts at all.

    A v65 file therefore loads bit-identical **and its delivered loads are
    unchanged**, but its *LRA deck* is not: the same hop ships the mesh that
    those counts govern, so the beam is meshed from geometry rather than welded
    to the load stations, and a v65 file reopened here exports different GRIDs.
    That is the point of D-56.4 and not a migration artifact -- the resultant
    of every case is identical, gated by ``test_the_lra_mesh_is_load_blind``,
    and ruling 1 (nothing downstream reproduces an sbeam output) is what makes
    it free to happen.
    """
    return d


#: Relative tolerance the v67 hop calls the wing tie closed at -- the mass
#: owner's own :data:`sloads.mass_distribution.RECONCILE_REL_TOL`, restated
#: here because a migration is pure over dicts and imports no calc.
_V67_TIE_REL_TOL = 1e-6


def _v67_wing_share(item: Dict[str, Any]) -> float:
    """The pounds of one item row the wing reacts, both sides (note 29 WF-3)."""
    w = float(item.get("weight_lb", 0.0) or 0.0)
    if item.get("component") == "wing":
        return w
    return w * min(max(float(item.get("wing_fraction", 0.0) or 0.0), 0.0), 1.0)


def _hop_66(d: Dict[str, Any]) -> Dict[str, Any]:
    """v66 -> v67 (design note 63, #289): **one mass model** -- not an identity.

    The wing's mass leaves ``wing_mass`` for the item database (D-63.2, as
    amended by R-63.3), in four moves, each reasoned from what the file holds:

    1. **The wing tie decides ``concentrated``.** ``Σ WING-reacted pounds of the
       items`` against ``2 x (panel_weight_lb + Σ concentrated)``. Where it
       **closes** (every shipped fixture) the items already carry every
       concentrated mass in some form -- per-side rows, or ``wing_fraction``
       slices of a fuselage row -- and converting the entries to new rows would
       double-count them (2,381 lb on ``baron_58``, 3,800 on ``atr42_100``), so
       they are **dropped** and named once in ``migration_notes``, which
       ``validation`` states on the Weight & CG page until the file is saved.
       Where the tie is **open** the entries are mass the items never had, so
       each becomes two ``EMPTY`` WING rows, carriage ``POINT``, at ``±y``.
    2. **Every WING row at a non-zero butt line is stamped ``POINT``**, every
       centreline row ``PANEL`` -- a one-time default for rows that exist,
       after which every row is typed (this is not the classification
       heuristic D-63.3 rejects). Rows the fuselage carries take ``PANEL``, the
       value the tag has no reading for.
    3. **``panel_weight_lb`` becomes derived.** Half the WING-carried PANEL
       pounds is what WINGINER integrates from now on; the entered value
       survives as ``panel_weight_override_lb`` **only** where it differs by
       more than the tie tolerance, so ``ga6_normal`` (165 = 330 / 2) carries
       no override and reproduces Appendix A bit-for-bit.
    4. ``weight.max_zero_fuel_weight_lb``, ``WingLoadCase.cg`` and
       ``CaseRef.run``/``config`` are additive with not-entered defaults and
       need no write.
    """
    weight = d.get("weight")
    items: List[Dict[str, Any]] = list(weight.get("items", []) or []) if isinstance(weight, dict) else []
    wm = d.get("wing_mass")
    notes: List[str] = list(d.get("migration_notes", []) or [])

    if isinstance(wm, dict):
        panel = float(wm.pop("panel_weight_lb", 0.0) or 0.0)
        concentrated = list(wm.pop("concentrated", []) or [])
        conc_total = math.fsum(float(c.get("weight_lb", 0.0) or 0.0) for c in concentrated)
        wing_items = math.fsum(_v67_wing_share(it) for it in items)
        want = 2.0 * (panel + conc_total)
        closes = abs(wing_items - want) <= _V67_TIE_REL_TOL * max(abs(want), 1.0)
        if concentrated and closes:
            named = ", ".join(
                f"{c.get('name', '(unnamed)')} {float(c.get('weight_lb', 0.0) or 0.0):g} lb/side"
                for c in concentrated)
            notes.append(
                f"v67 migration: wing_mass.concentrated dropped ({named}) -- the "
                f"wing tie closed ({wing_items:.1f} lb of WING-reacted items against "
                f"2 x ({panel:g} + {conc_total:g}) = {want:.1f} lb), so the item "
                "database already carries these masses; WINGINER now reads them "
                "from the WING rows tagged carriage POINT (design note 63 D-63.2)")
        elif concentrated:
            for c in concentrated:
                w = float(c.get("weight_lb", 0.0) or 0.0)
                y = abs(float(c.get("y", 0.0) or 0.0))
                base = {"x": float(c.get("x", 0.0) or 0.0), "z": float(c.get("z", 0.0) or 0.0),
                        "ixx": 0.0, "iyy": 0.0, "izz": 0.0, "kind": "empty",
                        "component": "wing", "consumable": False,
                        "wing_fraction": 0.0, "carriage": "point"}
                name = str(c.get("name", "wing mass"))
                if y == 0.0:
                    items.append({"name": name, "weight_lb": 2.0 * w, "y": 0.0, **base})
                else:
                    items.append({"name": f"{name}, left", "weight_lb": w, "y": -y, **base})
                    items.append({"name": f"{name}, right", "weight_lb": w, "y": y, **base})
            notes.append(
                f"v67 migration: wing_mass.concentrated converted to per-side WING "
                f"item rows, carriage POINT ({len(concentrated)} entries, "
                f"{2.0 * conc_total:g} lb both sides) -- the wing tie was open by "
                f"that amount ({wing_items:.1f} lb of WING-reacted items against "
                f"2 x ({panel:g} + {conc_total:g}) = {want:.1f} lb), so the item "
                "database did not carry these masses (design note 63 D-63.2)")

    # 2. the carriage stamp, on every row (and on an entered ballast row)
    def _stamp(row: Dict[str, Any]) -> None:
        y = float(row.get("y", 0.0) or 0.0)
        row["carriage"] = "point" if (row.get("component") == "wing" and y != 0.0) else "panel"

    for it in items:
        _stamp(it)
    if isinstance(weight, dict):
        weight["items"] = items
        for case in weight.get("cg_cases", []) or []:
            loading = case.get("loading") if isinstance(case, dict) else None
            ballast = loading.get("ballast") if isinstance(loading, dict) else None
            if isinstance(ballast, dict):
                _stamp(ballast)

    # 3. the derived panel, and the override only where the entered one differs
    if isinstance(wm, dict):
        derived = 0.5 * math.fsum(_v67_wing_share(it) for it in items
                            if it.get("carriage") == "panel")
        if abs(panel - derived) > _V67_TIE_REL_TOL * max(abs(derived), 1.0):
            wm["panel_weight_override_lb"] = panel
            notes.append(
                f"v67 migration: the entered wing panel weight {panel:g} lb/side "
                f"differs from the {derived:.1f} lb/side derived from the "
                "WING-tagged PANEL items and is kept as panel_weight_override_lb; "
                "clear the override to run on the item database (note 50's OV-1 "
                "shape, design note 63 D-63.2)")
    if notes:
        d["migration_notes"] = notes
    return d


#: hop here; :data:`SUPPORTED_FLOOR` names the oldest version the chain starts
#: from.
MIGRATIONS: Dict[int, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    55: _hop_55,
    56: _hop_56,
    57: _hop_57,
    58: _hop_58,
    59: _hop_59,
    60: _hop_60,
    61: _hop_61,
    62: _hop_62,
    63: _hop_63,
    64: _hop_64,
    65: _hop_65,
    66: _hop_66,
}

#: The oldest project version this build reads. It sat at ``SCHEMA_VERSION``
#: while the chain was empty (#93: pre-production, nothing older worth
#: reading); the v56 additive bump (note 36 OV-10) keeps v55 readable through
#: the identity hop, so the floor is the oldest version a hop starts from.
SUPPORTED_FLOOR = min(MIGRATIONS) if MIGRATIONS else SCHEMA_VERSION


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
            f"{supported}. Older projects are not migrated -- rebuild the "
            "project on the current version."
        )

    out = copy.deepcopy(d)
    for hop_from in sorted(MIGRATIONS):
        if version <= hop_from:
            out = MIGRATIONS[hop_from](out)
    out["schema_version"] = SCHEMA_VERSION
    return out


def applied_hops(from_version: int) -> List[int]:
    """Which hops :func:`migrate` would run for a file of ``from_version``.

    Empty while the chain is (#93). Kept as the chain's own accessor, so the
    tests and a future "this file was migrated from vN" provenance line read the
    answer from one place.
    """
    return [h for h in sorted(MIGRATIONS) if from_version <= h]
