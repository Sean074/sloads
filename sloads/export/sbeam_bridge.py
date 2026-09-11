"""The applied load set: what a structures model has cards for, and where.

Until note 56 this module was the *export bridge* -- it rendered the suite's
loads as five families of per-component solver deck (wing stick BDF, body,
tail chordwise, tail spanwise, control surface), each with its own CSV
companion. **D-56.2 deleted all five.** They were parallel model concepts
sharing one ID space with the deliverable, none of them the deliverable: the
full-span balanced free-free airplane model is, and it is built in
:mod:`sloads.export.lra_model`.

What stayed is what the decks were built *from*, and what has consumers that
outlive them:

* **The applied load set** (note 44 OR-141) -- :func:`applied_loads`, one row
  shape for all six components of the airframe. This is the record of what is
  applied, where, for which case, at what factor. The oracle report's applied
  appendices are built from it directly, and under note 56 D-56.9 it is the
  authority the delivered cards are written from.
* **The station numbering** -- :func:`station_gid`, :func:`beam_station_gid`,
  :func:`body_station_gids`, :func:`tail_span_gid`, :func:`tail_control_gid`.
  Each is a thin view of a band in :mod:`sloads.export.bands`. The decks that
  consumed them are gone; the numbering is not, because an applied-load row
  states which station it is at. It numbers **nothing that ships** as of note
  56 D-56.3 -- the LRA model now allocates every grid it writes from its own
  run, rather than taking these -- so these five are the applied-load model's
  own stations and retire with it at D-56.9, when a row's station becomes the
  LRA grid the card is written at.
* **The side-of-body internal loads** (step 13, note 24 R-3) --
  :func:`sob_internal_loads`, the internal load at the wing-to-fuselage cut,
  which the oracle report states as the wing root design loads.

**This module is a way-station.** Note 56 D-56.1 sends the applied-load family
and the side-of-body loads to ``report/applied.py``; what is left after that is
the numbering, which belongs to the LRA model once D-56.4's mesh lands. The
name ``sbeam_bridge`` already describes something that no longer exists here --
there is no bridge to sbeam in this file, only the load set a bridge would
render -- and it is kept for one more step so the move is a move and not a move
plus a rename.

Case identity (M4-2)
--------------------
Every case's ``SID``/``SUBCASE`` number is its own id put through
:func:`sloads.case_ids.subcase_id` (``W-03`` -> ``103``), never its position in
a list, so a filtered export cannot renumber the cases that survive.
:func:`subcase_map_block` renders the ``$`` comment block naming the governing
condition behind each number.

All values are **LIMIT** (note 49 OR-116): the calc's own numbers, unscaled,
with each case's ``safety_factor`` **stated** beside them -- the ``SF`` column
here -- and applied nowhere. Sizing to ultimate is the sizing step's job
(OR-117, gate G-OR-73). The two families the regulation prescribes already
ultimate (23.367(a)(2), 23.561(b)) carry ``SF = 1.0`` and ask for nothing
further. Coordinates and chord fractions are geometry and were never scaled.
The factor is per *case*, so the statement is per case too.

The applied set is applied, never differenced
---------------------------------------------
``WingStationLoad`` stores per-strip forces *and* cumulative shears/moments
(root-first, i.e. ``stations[0]`` carries the integrated total). The applied
load at station ``i`` is the **strip's own** load -- ``fx``, ``fz`` and the free
torsion ``myy_free`` -- at that station's own point. It is never a difference of
a cumulative column.

That distinction is the difference between a load set that works and one that
does not. The cumulative ``Myy`` at a station already contains the sweep and
dihedral transfer of the shear carried outboard of it, so a MOMENT cut from its
increment and applied at a point by a solver -- which generates that transfer
itself, from the geometry -- counts the transfer twice. Measured against the
published cumulative table, accumulating the old cards tip-inboard with the
rigid-body transfer, the torsion was wrong by 151 % / 190 % / 120 % on
``ga6_normal`` (PHAA / TORS / ACRL) and 34 % / 21 % on ``baron_58``, while shear
and both bending columns closed exactly. Rebuilt from the applied set the worst
error over every station of every case of both airplanes is 2.5e-15. Design
note: ``docs/40_history/46_applied_wing_load_set_note.md`` (OR-67).

Concentrated masses: the offset couples
---------------------------------------
A **concentrated** wing mass (engine, gear, fuel, store) does not sit on a
station: WINGINER adds it to every station inboard of it at its *true* station
``y_c`` (``mxx[i] += w*(y_c - ye[i])``, WINGINER.BAS 1180-1270), and the station
set has no point there. It is therefore reduced to the node inboard of it as its
force plus the **full** three-component offset couple ``r x F`` about that node
-- the exact static equivalent, so nothing moves and the set reproduces the
cumulative shear, bending *and* torsion at every node. The bending members
``mx``/``mz`` are stored in the calc's positive-magnitude convention
(``coordinates.bending_moment_vector`` maps them to CID 0 at the point of use);
the ``my`` member is folded into the node's applied torsion, which is already
body-axis. All three are zero on a wing with no concentrated masses, which is
every fixture the printed oracle covers. Prior design note:
``docs/40_history/19_concentrated_wing_mass_nodal_split_plan.md``, whose
two-component couple this completes.

Torsion reference axis
----------------------
Every wing torsion states its chordwise reference axis in-band (the ``MyyAxis``
column). The calc produces torsion about the **25% chord** (oracle-locked); when
the set is built from a ``Project``, the wing results are first transferred to
the surface's **loads reference axis** (LRA, ``SurfaceInput.ref_axis_pct`` --
the beam-model elastic axis, typically 40-50% chord) via
``net_loads.loads_ref_axis_results``. Callers passing bare ``WingLoadResult``
lists are responsible for transferring first (the results' ``torsion_axis``
stamp travels either way, so the axis is always labelled).

Unit systems (M4-20 step 4)
---------------------------
Every public writer takes ``system=UnitSystem.IMPERIAL|SI`` and resolves it to
the **solver** unit set -- ``deck_format.solver_units(system)``, i.e.
N / mm / N*mm / MPa in SI. The solver set is deliberately *not* the one a report
uses (N*m, kPa): a model whose GRIDs are millimetres and whose forces are
newtons is only correct with N*mm moments, and an N*m moment in it is a silent
1000x torsion error in a file that parses cleanly (decision D-19).

No arithmetic here knows about units. Every dimensional value this module emits
goes through :mod:`sloads.export.coordinates`, which is the single scale point.
Imperial is the all-1.0 identity.

Reference: Ref 1 Ch 14 (net loads); note 44 (the applied load set), note 56
(what this module stopped being).
"""

from __future__ import annotations

import csv
import io as _io
import math
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Union

from ..case_ids import subcase_id
from ..models import (
    BodyLoadResult,
    ConcentratedLoad,
    Project,
    TailSpanResult,
    WingLoadResult,
    WingStationLoad,
)

# Single-sourced from the calc that owns the limitation (public symbol, no cycle:
# nothing under sloads/modules imports the export bridge).
from ..modules.net_loads import loads_ref_axis_results
from ..safety_factors import shared_basis_factor
from ..units import DeliverableUnits, UnitSystem
from .bands import band
from .coordinates import (
    Vec3,
    bending_moment_vector,
    tail_axial_to_airplane,
    tail_force_to_airplane,
    tail_station_to_airplane,
    tail_torsion_to_airplane,
    to_force,
    to_grid,
    to_moment,
    ttail_transfer_to_airplane,
)
from .deck_format import (
    CARD_TOL,
    case_sf,
    comment,
    load_label,
    sf_str,
    solver_units,
)

# --------------------------------------------------------------------------- #
# Wing station GIDs
# --------------------------------------------------------------------------- #
# The band the wing's spanwise stations number from. It kept the ``wing-stick``
# registry name after note 56 D-56.2 deleted the stick deck: the name is the
# band's identity in :mod:`sloads.export.bands`, and renaming a band renumbers
# nothing but breaks every citation of the map. See the registry for the whole
# GID/EID/SID layout and why one owner replaced the per-file constants.
_WING_BAND = band("wing-stick")

def station_gid(i: int) -> int:
    """GRID id of wing station ``i`` (0 = root), past the clamped root node.

    Allocated from the ``wing-stick`` band, so a station count that would have
    walked into the fuselage block at 1001 raises instead (review m5) -- the
    same guard every other family already had.
    """
    return _WING_BAND.allocate(1 + i)


@dataclass
class NodalLoad:
    """One wing station's exported nodal load (the applied FORCE/MOMENT content).

    ``fx``/``fz`` are the applied force components (lb) and ``my`` the applied
    torsion (lb-in) at the torsion-reference-axis point ``(x, y, z)`` (in) --
    the station ``x`` of the source result: 25% chord as computed, or the
    surface LRA after ``net_loads.to_loads_ref_axis`` -- taken from the strip's
    own applied load, never from a difference of a cumulative column (note 46
    OR-67). ``sz``/``mxx``/``myy`` are the cumulative shear / bending / torsion
    at the station, carried through for the span-load CSV's engineering columns.

    ``mx``/``mz`` are the bending members of the applied **offset couple**
    (lb-in) that reduces a concentrated mass sitting between two stations to the
    node inboard of it -- zero at every node of a wing that carries none; the
    couple's torsion member is folded into ``my``. See the module docstring;
    ``mx``/``mz`` are
    stored in the calc's own bending sign (positive-magnitude), and
    :func:`~sloads.export.coordinates.bending_moment_vector` owns the mapping to
    the card's CID-0 components."""
    gid: int
    x: float
    y: float
    z: float
    fx: float
    fz: float
    my: float
    sz: float
    sx: float
    mxx: float
    myy: float
    mzz: float
    mx: float = 0.0
    mz: float = 0.0


def wing_nodal_loads(result: WingLoadResult) -> List[NodalLoad]:
    """Applied nodal loads for one case -- the applied set, put on the deck's nodes.

    Each station node carries the **strip's own** load: ``fx``, ``fz`` and the
    free torsion ``myy_free``. Nothing here is a difference of a cumulative
    column, and that is the whole point (note 46 OR-67). The cumulative ``Myy``
    already contains the sweep and dihedral transfer of the shear carried
    outboard, so a card cut from its increment, applied at a point by a solver
    that generates the transfer itself, counts the transfer twice -- measured at
    21 % to 190 % of the root torsion across the two example airplanes before
    this was fixed.

    A concentrated wing mass has no grid of its own (the stick model nodes the
    load stations only), so it is reduced to the node inboard of it as its force
    plus the **full** three-component offset couple ``r x F`` about that node --
    the exact static equivalent. ``mx``/``mz`` are that couple's bending
    members, stored in the calc's positive-magnitude convention like the
    cumulative columns they must agree with; the ``my`` member is folded into
    the node's applied torsion, which is in body axes. Both are zero at every
    node of a wing with no concentrated masses, which is every fixture the
    printed oracle covers.

    The result reproduces the published ``Sx``/``Sz``/``Mxx``/``Myy``/``Mzz`` at
    **every** station under rigid-body transfer, not merely at the root
    (note 46 G-OR-37).

    Forces/moments are returned as LIMIT loads -- the calc's own values, with
    the case's ``safety_factor`` stated and applied nowhere (OR-116). Closure is
    therefore exact rather than scaled: ``sum(dFz) == root``.
    """
    s: List[WingStationLoad] = result.stations
    # LIMIT, per note 49 OR-116: nodal loads carry the calc's own values and the
    # 23.303 factor is stated by the deck header that writes them, never here.
    _require_applied_set_matches_cumulative(result)
    out: List[NodalLoad] = [
        NodalLoad(
            gid=station_gid(i), x=st.x, y=st.y, z=st.z,
            fx=st.fx, fz=st.fz, my=st.myy_free,
            sz=st.sz, sx=st.sx,
            mxx=st.mxx, myy=st.myy, mzz=st.mzz,
            mx=0.0, mz=0.0,
        )
        for i, st in enumerate(s)
    ]
    for mass in result.point_loads:
        node = out[_node_inboard_of(s, mass.y)]
        dx, dy, dz = mass.x - node.x, mass.y - node.y, mass.z - node.z
        node.fx += mass.fx
        node.fz += mass.fz
        # Bending members in the calc's positive-magnitude convention, so they
        # add to the cumulative columns as written; the CID-0 map is
        # ``coordinates.bending_moment_vector`` at the card writer.
        node.mx += dy * mass.fz
        node.mz += dy * mass.fx
        # Torsion is already body-axis: (r x F)_y.
        node.my += (dz * mass.fx - dx * mass.fz)
    return out


def _node_inboard_of(s: Sequence[WingStationLoad], y: float) -> int:
    """Index of the last station at or inboard of span ``y``.

    A mass outboard of the tip station reduces to the tip; a mass inboard of the
    root reduces to the root. Both are edge cases the entered geometry permits
    and neither may lose the load.
    """
    index = 0
    for i, st in enumerate(s):
        if st.y <= y:
            index = i
    return index


def _require_applied_set_matches_cumulative(result: WingLoadResult) -> None:
    """Fail loudly when the strips and masses cannot rebuild the root torsion.

    The deck is now assembled from ``myy_free`` and ``point_loads``, both of
    which are *additive* fields on the persisted result: a ``Project`` written
    before either existed loads back with them defaulted to empty, and a deck
    built from it would be short the whole free torsion, or the whole of a
    concentrated mass, and would look exactly like a complete one. Differencing
    the cumulative used to hide that, at the cost of the error this note fixes.

    So it is checked rather than assumed. The test is the root closure the deck
    claims (note 46 G-OR-37) applied to the source result, and it costs one pass
    over the stations.
    """
    s = result.stations
    if not s:
        return
    root = s[0]
    got = math.fsum(st.myy_free for st in s)
    got -= math.fsum(st.fz * (st.x - root.x) - st.fx * (st.z - root.z)
                     for st in s)
    got -= math.fsum(mass.fz * (mass.x - root.x) - mass.fx * (mass.z - root.z)
                     for mass in result.point_loads)
    scale = max(abs(root.myy), abs(got))
    if scale and abs(got - root.myy) > CARD_TOL * scale:
        raise ValueError(
            f"wing case {result.case!r}: the applied set does not rebuild the "
            f"cumulative root torsion ({got:.1f} against {root.myy:.1f} lb-in). "
            "The stations' free torsion or the concentrated wing masses are "
            "missing from this result -- most likely it was loaded from a "
            "project written before those fields existed. Recompute the loads "
            "(net_loads.build_net_loads) rather than exporting a short deck."
        )


# --------------------------------------------------------------------------- #
# Inputs: accept a Project, a list of results, or a single result
# --------------------------------------------------------------------------- #
ResultsArg = Union[Project, WingLoadResult, Sequence[WingLoadResult]]


def _as_results(arg: ResultsArg) -> List[WingLoadResult]:
    """Coerce the argument to the list of net wing-load results to export."""
    if isinstance(arg, Project):
        if arg.loads is None or not arg.loads.wing_net:
            raise ValueError(
                "Project has no net wing loads to export -- run the 'net_loads' "
                "module (build_net_loads) first so Project.loads.wing_net is set."
            )
        # Boundary transfer: exported wing torsion is stated about the surface's
        # loads reference axis (no-op when the LRA is the 25% chord).
        return loads_ref_axis_results(arg, list(arg.loads.wing_net))
    if isinstance(arg, WingLoadResult):
        return [arg]
    results = list(arg)
    if not results:
        raise ValueError("no wing-load results to export")
    return results


def _sid(sid_base: int, case_index: int, result=None) -> int:
    """Load-set id (== the ``SUBCASE`` id) for one exported case (M4-2 decisions 8/9).

    Derived from the case's own ``case_ref.case_id`` via
    :func:`sloads.case_ids.subcase_id` -- ``W-03`` -> ``103``, ``VT-31`` -> ``331``
    -- so:

    * a filtered export (:func:`filter_by_selected_case_ids`) cannot renumber the
      cases that survive: before M4-2 the SID/SUBCASE was the case's *position*,
      so deselecting one case silently shifted every deck number after it, and a
      solver result labelled ``SUBCASE 3`` meant a different case in two exports
      of the same project;
    * the per-component blocks keep wing / tail / body / gear sets disjoint, which
      is what an assembled multi-component deck (L-1) needs;
    * ``LOAD = 103`` inside ``SUBCASE 103`` is self-documenting, and the deck's
      ``$`` map block (:func:`subcase_map_block`) and the exported case index name
      the governing condition behind it.

    ``sid_base + case_index`` remains the fallback for a result carrying **no**
    ``CaseRef`` at all -- a bare ``WingLoadResult`` built in a test or a caller
    that never ran SELECT still gets a valid, contiguous deck. ``case_ref`` is a
    typed ``Optional`` field on every exportable result (CH-2: read, not probed).
    """
    ref = result.case_ref if result is not None else None
    if ref is not None:
        return subcase_id(ref.case_id)
    return sid_base + case_index


def subcase_map(results: Sequence) -> List[tuple]:
    """``[(subcase_id, case_id, condition, far_reference), ...]`` for ``results``.

    The deck-side half of the case index: what a consumer needs to trace a
    ``SUBCASE`` back to the governing condition without opening another file.
    A result with no ``CaseRef`` contributes its positional SID and an empty id.
    """
    out: List[tuple] = []
    for idx, r in enumerate(results):
        ref = r.case_ref
        out.append((
            _sid(1, idx, r),
            ref.case_id if ref else "",
            ref.condition if ref else str(r.case),
            ref.far_reference if ref else "",
        ))
    return out


def subcase_map_block(results: Sequence) -> List[str]:
    """The deck's ``$`` subcase-map comment block (M4-2 decision 10).

    One line per exported case::

        $ SUBCASE 103 = W-03 -- PHAA -- FAR 23.333(b)

    ``$`` is a comment to every bulk-data parser, so the block is inert; it exists
    so the deck states its own case identity rather than making the reader join it
    to the case-index CSV by position."""
    rows = subcase_map(results)
    if not rows:
        return []
    lines = ["$ ---------------------------------------------------- SUBCASE MAP",
             "$ SUBCASE/SID = SLOADS case id -- condition -- FAR reference"]
    for sid, case_id, condition, far in rows:
        far_txt = f" -- FAR {far}" if far else ""
        # Through the emitter, not hand-fitted. This block used to build its own
        # line and so carried its own width assumption -- fine while every
        # condition name was as short as ``PHAA``, and an overrun the moment one
        # was not: ``one engine out - VC (ultimate) (engine 0)`` (note 44 OR-172)
        # took the turboprop tail decks past 72 columns in both unit systems.
        # The width is the emitter's property, which is the rule the wing decks
        # were already moved to; this is the last block that had not been.
        lines += comment(
            f"SUBCASE {sid} = {case_id or '(no case id)'} -- {condition}{far_txt}")
    return lines





#: Prepended to :func:`applied_load_csv`. States the structural zeros, so a
#: consumer writing cards cannot read a printed zero as an omission (OR-65).
_APPLIED_CSV_CONVENTIONS = (
    "# The applied wing load set: one row per strip and one per concentrated\n"
    "# wing mass, each at its own point. Nothing here is a running total.\n"
    "# Moments are right-handed about the airplane axes, about the station's\n"
    "# own point on the axis named in MyyAxis.\n"
    "# Fy is zero throughout: the wing carries no spanwise strip load and no\n"
    "# wing condition in this suite is lateral. Mx and Mz are zero throughout:\n"
    "# a strip applies forces and a section moment, and every Mxx/Mzz the\n"
    "# structure carries is those forces acting through the arms stated here.\n"
)

#: Per component, what the file is and which of its columns are structural
#: zeros -- the same statement each appendix makes in prose (note 44 OR-140).
#:
#: A zero column is published, never dropped, and the reason it is zero is
#: published beside it. Dropping it leaves the reader to decide whether a
#: missing column is a zero or an omission; printing it without the reason
#: leaves them reading a *measured* zero. Both halves, per component, because
#: the reason differs: the wing has no lateral condition, the fin has no
#: chordwise one, and the body beam has no producer at all.
_APPLIED_CSV_NOTES = {
    "wing": _APPLIED_CSV_CONVENTIONS,
    "fuselage": (
        "# The applied fuselage load set: one row per station of the body beam,\n"
        "# at the point on the fuselage loads reference axis where the structure\n"
        "# is. Nothing here is a running total.\n"
        "# Moments are right-handed about the airplane axes, about the station's\n"
        "# own point on the axis named in MyyAxis.\n"
        "# Fz is the whole applied set. Fx and Fy are zero throughout because\n"
        "# the body beam has no fore-aft or lateral producer, and Mx, My and Mz\n"
        "# because a station applies a force and no free moment: every moment\n"
        "# the beam carries is those forces acting through the arms stated here.\n"),
    "htail": (
        "# The applied horizontal tail load set: one row per strip, plus any\n"
        "# discrete control-surface node. Nothing here is a running total, and\n"
        "# every row is a card the spanwise deck writes at the same GID.\n"
        "# Moments are right-handed about the airplane axes, about the station's\n"
        "# own point on the axis named in MyyAxis.\n"
        "# Fz is the normal load and My the strip torsion about the surface's\n"
        "# span axis, which for this surface is airplane y. Fx and Fy are zero\n"
        "# throughout: this analysis models no chordwise load on either tail\n"
        "# surface, and no spanwise acceleration reaches a horizontal tail.\n"
        "# Mx and Mz are zero: a strip applies forces and a torsion, and the\n"
        "# bending the structure carries is those forces through these arms.\n"),
    "vtail": (
        "# The applied vertical tail load set: one row per strip, plus any\n"
        "# discrete control-surface node and the T-tail transfer. Nothing here\n"
        "# is a running total, and every row is a card the spanwise deck writes\n"
        "# at the same GID.\n"
        "# Moments are right-handed about the airplane axes, about the station's\n"
        "# own point on the axis named in MyyAxis.\n"
        "# Fy is the normal load and Mz the strip torsion about the surface's\n"
        "# span axis, which for a fin is airplane z -- NOT My, which is zero\n"
        "# throughout: a lateral load can make no moment about the y axis.\n"
        "# Fz is NOT zero: the fin's span is vertical, so vertical acceleration\n"
        "# on its own mass is an axial column load carried in the same card.\n"
        "# Fx and Mx are zero: this analysis models no chordwise load on either\n"
        "# tail surface, and the bending the structure carries is the normal\n"
        "# load acting through the arms stated here.\n"),
    "landing_gear": (
        "# The applied landing gear load set: one row per LANDLOAD case per\n"
        "# loaded leg, all 33 cases, at the point that case's reaction is\n"
        "# applied at -- the axle or the ground contact point, per FAR 23\n"
        "# Appendix C and the manual's own point-of-load column. The point is\n"
        "# named in the Station column of every row, because it is not the same\n"
        "# point for every case.\n"
        "# NO CRITICAL-CASE DOWN-SELECT HAS BEEN APPLIED. A ground case sizes a\n"
        "# gear member through a load path this analysis does not model, so\n"
        "# every case is delivered and the ranking is the gear discipline's.\n"
        "# Cases 25-33 are the 23.499 supplementary nose-wheel family: gear\n"
        "# design conditions with no airplane in equilibrium, which is why the\n"
        "# assembled ground deck carries cases 1-24 only.\n"
        "# Mx, My and Mz are zero throughout: a wheel reaction is a pure force\n"
        "# at the point stated here. The couple that carries it to the gear\n"
        "# reference point is in the gear load report (gear_loads.csv), which\n"
        "# states both ends of the leg.\n"
        "# MyyAxis is n/a: a point load has no torsion reference axis.\n"),
    "engine": (
        "# The applied engine mount load set: six components at one point, one\n"
        "# row per case, at the combined engine and propeller CG. The 23.371(b)\n"
        "# gyroscopic condition appears as its four sign combinations, each its\n"
        "# own row and its own case id.\n"
        "# Moments are right-handed about the airplane axes at the point stated\n"
        "# here; Mx is the mount reaction torque about the thrust axis.\n"
        "# MyyAxis is n/a: a point load has no torsion reference axis.\n"),
}




# --------------------------------------------------------------------------- #
# The applied load set -- what a structures model has cards for
# --------------------------------------------------------------------------- #
#: The applied set's spanwise force component. Structurally zero for the wing:
#: no producer exists in the AIRLOADS/WINGINER chain and no delivered wing
#: condition is lateral. Named rather than written ``0.0`` inline so the day a
#: lateral wing condition arrives, the compiler's own search finds every place
#: that assumed it away.
_NO_SPANWISE_STRIP_LOAD = 0.0

#: The applied set's free bending. Structurally zero by strip theory: all of
#: ``Mxx``/``Mzz`` is the applied forces acting through the spanwise arms these
#: coordinates already state.
_NO_FREE_BENDING = 0.0
#: The body beam's structurally absent components, named rather than written
#: ``0.0`` four times: the fuselage stations carry vertical load only. Each is a
#: statement about the load set, and OR-140 prints the column either way -- so
#: the day a producer appears, the name is where it will be found.
_NO_BODY_AXIAL_LOAD = 0.0
_NO_BODY_LATERAL_LOAD = 0.0
_NO_BODY_FREE_TORSION = 0.0
#: What the body beam's ``Myy`` is stated about. ``BodyLoadResult`` carries no
#: ``torsion_axis`` of its own -- the beam has exactly one, it is the fuselage
#: loads reference axis, and it is named here so the row's in-band statement
#: reads the same as every other component's.
_BODY_TORSION_AXIS = "fuselage loads reference axis"


#: The components an applied set can be produced for (note 44 OR-141).
#:
#: One row shape for the whole airframe. Until 2026-09-07 this record was the
#: wing's alone and the other three appendices each assembled their own, which
#: is how Appendices D and E came to omit applied load the deck emits (OR-143):
#: four assemblers of one load set, three of them with no gate tying them to a
#: card. The component is carried on the row because the beam-frame -> body-axis
#: moment map depends on it -- a surface's torsion is about its **span** axis,
#: and the fin's span is not the wing's.
APPLIED_COMPONENTS = ("wing", "fuselage", "htail", "vtail",
                      "landing_gear", "engine")

#: The two components whose applied set is a **point load**, not a beam.
#:
#: A gear leg and an engine mount deliver a force (and, for the mount, a couple)
#: at a named point rather than a distribution along a station axis, so they have
#: no torsion reference axis and their free moments are already right-handed
#: about CID 0. They join the applied set anyway because the question a reader
#: asks of every element is the same one -- what do I apply, where, for which
#: case, at what factor -- and answering it in one shape for four components and
#: a different shape for two is what left the load-case index carrying no load on
#: 344 of ``ga6_normal``'s 347 rows (note 44 OR-186).
_POINT_LOAD_COMPONENTS = ("landing_gear", "engine")

#: What a point-load row states instead of a torsion reference axis.
_NO_TORSION_AXIS = "n/a (point load)"


@dataclass(frozen=True)
class AppliedLoad:
    """One applied load of an airframe component's set.

    A wing strip or concentrated wing mass, a fuselage beam station, or a tail
    strip / control-surface node / T-tail transfer node -- one shape for all of
    them, keyed by ``component`` (:data:`APPLIED_COMPONENTS`).

    The **applied** set, not the carried one: ``fz``/``fx`` are the load the
    strip or the mass exerts and ``myy_free`` the section moment that is not
    already a force acting through an arm. A model that puts ``fz``/``fx`` at
    ``(x, y, z)`` generates every transfer term itself from its own geometry,
    so re-applying them would count them twice -- which is why this record
    carries ``myy_free`` and not the increment of the cumulative ``myy``. The
    two are different quantities and can differ in sign (``ga6_normal`` PHAA,
    inboard strips).

    A concentrated mass is a pure force: ``myy_free`` is zero and ``gid`` is
    ``None``, because the exported deck has no grid at its coordinates (the
    stick model nodes the load stations only). Its ``label`` is the mass's
    entered name.

    **All six components are carried, three of them structurally zero.** A
    consumer building FORCE/MOMENT cards needs the whole vector, and a set that
    published only its non-zero half would leave the reader to decide whether a
    missing column is zero or merely unstated. So:

    * ``fy`` is ``0.0``. The wing chain has no producer for a spanwise strip
      load (``WingStationLoad.f_span`` is the fin's, whose span is airplane
      ``z``), and every delivered wing condition is symmetric or rolling -- no
      lateral condition exists for the wing -- so the zero is a property of the
      load set, not only of the model.
    * ``mxx_free`` and ``mzz_free`` are ``0.0``. A strip applies forces and a
      section moment about the span axis and nothing else; the whole of the
      cumulative ``Mxx`` and ``Mzz`` is those forces acting through spanwise
      arms, which a model regenerates from these coordinates. Publishing a free
      bending here would double count it.

    Moments are stored in the **calc's** sign convention (positive-magnitude
    beam integrals for ``mxx_free``/``mzz_free``), the same as
    :class:`~sloads.models.results.WingStationLoad`; the map to right-handed
    CID-0 body components is :func:`applied_body_moments`, which is the one
    place the ``Mzz -> -z`` asymmetry is applied.

    Values are LIMIT, Imperial (lb, lb-in, in) -- raw calc units, as everywhere
    else in this package; ``safety_factor`` is the case's own limit->ultimate
    factor, and each consumer scales at its own boundary.
    """

    case: str
    case_id: str
    label: str
    gid: Optional[int]
    x: float
    y: float
    z: float
    fx: float
    fy: float
    fz: float
    mxx_free: float
    myy_free: float
    mzz_free: float
    safety_factor: float
    torsion_axis: str
    #: Which component's set this row belongs to. Defaulted to ``"wing"`` so the
    #: field is additive to every existing construction site, and read by
    #: :func:`applied_body_moments` -- the whole reason it is on the row.
    component: str = "wing"
    #: Whether this row's moments are **already** right-handed about CID 0.
    #:
    #: False for every row a beam produces, which is the rule: moments are
    #: stored in the calc's own convention and mapped once, by component. The
    #: exception is the T-tail transfer node -- the one load on a fin deck that
    #: is not in the fin's frame at all, but the horizontal tail above it
    #: handing down a vertical force and a pitching moment about *its* span
    #: axis. Mapping that through the fin's rule would put the h-tail's pitching
    #: moment on the fin's torsion axis. The deck already treats it as its own
    #: case (``coordinates.ttail_transfer_to_airplane``); this is the same
    #: exception, declared on the row rather than left to a reader to infer.
    body_moments: bool = False


def applied_load_rows(arg: ResultsArg) -> List[AppliedLoad]:
    """The applied wing load set, one record per strip and per concentrated mass.

    The single owner of that row shape: the oracle report's Appendix B.1 table
    and :func:`applied_load_csv` are both views of this list, so the table a
    stress analyst reads and the file they load cannot disagree about what the
    applied set is.

    Sums back to the cumulative NETLOADS distributions exactly -- shear and
    drag by direct summation, bending and torsion once the model applies each
    force through the arm these coordinates state.
    """
    out: List[AppliedLoad] = []
    for result in _as_results(arg):
        sf = case_sf(result)
        # The field is typed on the result (M4-16: no getattr default here).
        case_id = result.case_ref.case_id if result.case_ref else ""
        for i, s in enumerate(result.stations):
            out.append(AppliedLoad(
                case=result.case, case_id=case_id, label=str(i + 1),
                gid=station_gid(i), x=s.x, y=s.y, z=s.z,
                fx=s.fx, fy=_NO_SPANWISE_STRIP_LOAD, fz=s.fz,
                mxx_free=_NO_FREE_BENDING, myy_free=s.myy_free,
                mzz_free=_NO_FREE_BENDING,
                safety_factor=sf, torsion_axis=result.torsion_axis))
        for mass in result.point_loads:
            out.append(_applied_point_load(result, mass, sf, case_id))
    return out


def _applied_point_load(result: WingLoadResult, mass: ConcentratedLoad,
                        sf: float, case_id: str) -> AppliedLoad:
    """One concentrated wing mass as its applied point load (zero free moment)."""
    return AppliedLoad(
        case=result.case, case_id=case_id, label=mass.name or "point mass",
        gid=None, x=mass.x, y=mass.y, z=mass.z,
        fx=mass.fx, fy=_NO_SPANWISE_STRIP_LOAD, fz=mass.fz,
        mxx_free=_NO_FREE_BENDING, myy_free=0.0,
        mzz_free=_NO_FREE_BENDING,
        safety_factor=sf, torsion_axis=result.torsion_axis)


def fuselage_applied_load_rows(arg, project: Optional[Project] = None
                               ) -> List[AppliedLoad]:
    """The applied fuselage load set, one record per station of the body beam.

    ``Fz`` is the whole of it: the body beam carries the station inertia, the
    balancing tail load and the wing carry-through reaction, all vertical. There
    is no producer for a fore-aft or lateral applied load on the beam and no
    free moment at a station, so five of the six components are structurally
    zero and are published as such (note 44 OR-140).

    The point is where the *structure* is, not where the mass is: the beam runs
    down the centre plane on the fuselage loads reference axis, so ``y`` is zero
    by construction and ``z`` is that axis's waterline at the station. ``project``
    supplies the axis; without it the waterline is unknown and is published as
    zero rather than guessed.
    """
    from ..derived_geometry import fuselage_lra

    lra = None
    if project is not None:
        try:
            lra = fuselage_lra(project)
        except Exception:           # an airplane with no body geometry entered
            lra = None
    out: List[AppliedLoad] = []
    for result in _body_results(arg):
        sf = case_sf(result)
        case_id = result.case_ref.case_id if result.case_ref else ""
        for gid, s in zip(body_station_gids(result), result.stations):
            out.append(AppliedLoad(
                case=result.case, case_id=case_id, label=str(gid), gid=gid,
                x=s.x, y=0.0, z=(lra.z_at(s.x) if lra is not None else 0.0),
                fx=_NO_BODY_AXIAL_LOAD, fy=_NO_BODY_LATERAL_LOAD, fz=s.fz,
                mxx_free=_NO_FREE_BENDING, myy_free=_NO_BODY_FREE_TORSION,
                mzz_free=_NO_FREE_BENDING,
                safety_factor=sf, torsion_axis=_BODY_TORSION_AXIS,
                component="fuselage"))
    return out


def tail_applied_load_rows(arg, component: str) -> List[AppliedLoad]:
    """The applied load set of one tail surface, in the deck's own terms.

    **Every load the spanwise deck emits for this surface, and nothing else**
    (note 44 OR-143). Until 2026-09-07 the report assembled this itself from the
    strip normal force alone, so the strip torsion and the fin's span-axis
    axial -- both on cards the deck writes -- were absent from an appendix that
    stated it was the same load. Three rows per case were missing entirely: the
    discrete control-surface nodes and the T-tail transfer.

    Each row's point comes from the same mapper the deck's ``GRID`` cards use,
    and each row's forces are already in airplane axes, because the maps that
    put them there are the surface's own and belong beside the geometry rather
    than at four call sites. The moments stay in the beam's convention and are
    mapped by :func:`applied_body_moments`, except the T-tail transfer, which
    says so on the row.
    """
    if component not in ("htail", "vtail"):
        raise ValueError(
            f"tail_applied_load_rows: component {component!r} is not "
            "'htail' or 'vtail'")
    out: List[AppliedLoad] = []
    for r in _tail_span_results(arg, component):
        sf = case_sf(r)
        case_id = r.case_ref.case_id if r.case_ref else ""
        stations = list(r.stations)
        for i, st in enumerate(stations):
            x, y, z = tail_station_to_airplane(st.x, st.y, component, st.z)
            # Normal and span-axis loads are two components of one applied
            # force -- the deck puts them on one card, and so does this row.
            nx, ny, nz = tail_force_to_airplane(st.fz, component)
            ax, ay, az = tail_axial_to_airplane(st.f_span, component)
            out.append(AppliedLoad(
                case=r.case, case_id=case_id, label=str(i + 1),
                gid=tail_span_gid(component, i), x=x, y=y, z=z,
                fx=nx + ax, fy=ny + ay, fz=nz + az,
                mxx_free=_NO_FREE_BENDING, myy_free=st.myy_free,
                mzz_free=_NO_FREE_BENDING,
                safety_factor=sf, torsion_axis=r.torsion_axis,
                component=component))
        for i, cp in enumerate(r.control_loads):
            x, y, z = tail_station_to_airplane(cp.x, cp.y, component, cp.z)
            fx, fy, fz = tail_force_to_airplane(cp.f_normal, component)
            out.append(AppliedLoad(
                case=r.case, case_id=case_id,
                label=f"control {i + 1}", gid=tail_control_gid(component, i),
                x=x, y=y, z=z, fx=fx, fy=fy, fz=fz,
                mxx_free=_NO_FREE_BENDING, myy_free=cp.m_torsion,
                mzz_free=_NO_FREE_BENDING,
                safety_factor=sf, torsion_axis=r.torsion_axis,
                component=component))
        transfer = r.tip_transfer
        if transfer is not None and stations:
            tip = stations[-1]
            x, y, z = tail_station_to_airplane(tip.x, tip.y, component, tip.z)
            fvec, mvec = ttail_transfer_to_airplane(transfer.fz, transfer.myy)
            out.append(AppliedLoad(
                case=r.case, case_id=case_id, label="T-tail transfer",
                gid=tail_span_gid(component, len(stations) - 1),
                x=x, y=y, z=z, fx=fvec[0], fy=fvec[1], fz=fvec[2],
                mxx_free=mvec[0], myy_free=mvec[1], mzz_free=mvec[2],
                safety_factor=sf, torsion_axis=r.torsion_axis,
                component=component, body_moments=True))
    return out


def gear_applied_load_rows(project: Project) -> List[AppliedLoad]:
    """The landing gear's applied load set: one row per case per loaded leg.

    **All 33 LANDLOAD cases** (note 44 OR-184/OR-188), against the assembled
    ground deck's 24. No critical-case down-select survives into this set: a
    ground case sizes a gear member through a load path the loads analysis cannot
    see -- a drag brace, a side brace, a trunnion -- so ranking 33 conditions on
    one scalar removes the case a reader needs. Cases 25-33 are the 23.499
    supplementary-nose family, which has no airplane in equilibrium to assemble;
    they are carried here and flagged in the document rather than dropped.

    **The point is not re-decided here.** Each row states the point
    :func:`sloads.gear_loads.application_point_of` names for its case -- the axle
    or the ground contact point, Appendix A's own printed point-of-load column
    (design note 39 AP-1/AP-2) -- and :attr:`~sloads.gear_loads.DeliveredLeg.
    point_name` names it in the row's label. That is what "the one that is
    applicable for the case" means operationally, and it has one owner.

    A wheel reaction is a **pure force**: the free moments are zero, and they are
    published as zeros rather than blanked, on the rule that a reader may not be
    left to decide whether an absent column is a zero or an omission. The
    *delivery* of that force to the gear reference point -- the second point, and
    the couple the lever arm makes there -- is :func:`gear_report_rows`, which is
    where a load applied at one point and received at another is one statement.

    A leg carrying nothing in a case is skipped, matching the free-body report
    beside it; which gears a family lifts clear is stated by the module's own
    condition values, where all three wheels appear and the unloaded ones are
    zero.
    """
    from ..gear_loads import delivered_gear_legs, gear_case_loads
    from ..safety_factors import table_for

    table = table_for(project)
    out: List[AppliedLoad] = []
    cases = gear_case_loads(project)
    legs_by_case = delivered_gear_legs(cases)
    for case in cases:
        sf = table.required_factor_for(case)
        case_id = case.case_ref.case_id if case.case_ref else ""
        for leg in legs_by_case.get(case.case, ()):
            if not leg.carries_load:
                continue
            x, y, z = leg.point
            fx, fy, fz = leg.force
            out.append(AppliedLoad(
                case=case.description, case_id=case_id,
                label=f"{leg.name} at {leg.point_name}",
                # No grid: the exported ground deck applies the reaction at the
                # gear reference node, not at the point it acts, so naming a
                # grid here would point a consumer at a node these coordinates
                # are not.
                gid=None,
                x=x, y=y, z=z, fx=fx, fy=fy, fz=fz,
                mxx_free=0.0, myy_free=0.0, mzz_free=0.0,
                safety_factor=sf, torsion_axis=_NO_TORSION_AXIS,
                component="landing_gear", body_moments=True))
    return out


def engine_applied_load_rows(project: Project) -> List[AppliedLoad]:
    """The engine mount's applied load set: six components at one point per case.

    The mount takes a point load, which is why it has no appendix of its own
    (note 44 OR-158) -- but it is still an element a reader sizes, so it gets its
    own file in the same shape as every other (OR-186). The rows are the engine
    module's own conditions read through :mod:`sloads.load_keys`, including the
    four sign combinations the 23.371(b) gyroscopic condition expands into, so
    this file and the load-case index cannot come to state different loads for
    the same case.

    Moments are already right-handed about CID 0 -- the mount reaction torque and
    the gyroscopic couple are stated in airplane axes at the combined engine and
    propeller CG -- so the row says so rather than being routed through a beam's
    convention it does not have.
    """
    from ..registry import get
    from ..report.render import point_load_records

    out: List[AppliedLoad] = []
    for rec in point_load_records(get("engine")(project).conditions):
        out.append(AppliedLoad(
            case=rec.description, case_id=rec.case_id, label=rec.label, gid=None,
            x=rec.x, y=rec.y, z=rec.z, fx=rec.fx, fy=rec.fy, fz=rec.fz,
            mxx_free=rec.mx, myy_free=rec.my, mzz_free=rec.mz,
            # A non-load condition prescribes no factor (#154); the applied row
            # needs a number, and 1.0 is the one that changes nothing.
            safety_factor=(1.0 if rec.safety_factor is None
                           else rec.safety_factor),
            torsion_axis=_NO_TORSION_AXIS,
            component="engine", body_moments=True))
    return out


def applied_loads(component: str, arg,
                  project: Optional[Project] = None) -> List[AppliedLoad]:
    """The applied load set of ``component`` -- the one entry point (OR-141).

    Every applied appendix and every applied CSV is a view of this call, so a
    table a stress analyst reads, a file they load and the deck they solve
    cannot disagree about what the applied set is. ``project`` is used by the
    fuselage alone, for the beam's waterline.
    """
    if component == "wing":
        return applied_load_rows(arg)
    if component == "fuselage":
        return fuselage_applied_load_rows(arg, project)
    if component in _POINT_LOAD_COMPONENTS:
        # A point-load set is built from the ``Project``, not from a results
        # argument: its producer is a module run, not a beam whose stations the
        # caller already holds. Refusing rather than defaulting, because a caller
        # that reached here without one asked for a set that cannot be built.
        if project is None:
            raise ValueError(
                f"applied_loads({component!r}) needs a project: a point-load set "
                "is built from the module run, not from a results argument")
        return (gear_applied_load_rows(project) if component == "landing_gear"
                else engine_applied_load_rows(project))
    return tail_applied_load_rows(arg, component)


def applied_body_moments(load: AppliedLoad) -> Vec3:
    """``load``'s free moments as a right-handed CID-0 vector (raw lb-in).

    The applied set stores its moments the way the calc does -- ``mxx``/``mzz``
    as positive-magnitude beam integrals -- and a body-axis consumer needs
    ``r x F`` components, which for ``Mzz`` is the negation
    (``CONVENTIONS.md`` §Wing torsion physical sense). That map has one owner,
    :func:`~sloads.export.coordinates.bending_moment_vector`, so this routes
    through it rather than restating the sign: both views of B.1 -- the report
    table and the CSV -- call this and neither carries sign logic of its own.

    **The map depends on the component**, which is why the row carries one. A
    surface's torsion is about its *span* axis: the wing's and the h-tail's span
    is ``y``, so their free torsion is the body ``My`` unchanged, and the body
    beam's bending is about ``y`` for the same reason. The **fin's span is
    ``z``** -- its torsion is ``Mz``, and negated. Returning ``(mx, myy_free,
    mz)`` for every component was right for three of the four and put 4,561
    lb-in of ``ga6_normal`` fin torsion on an axis a lateral force cannot make a
    moment about at all (note 44 OR-142).

    The fin's sign is not restated here: :func:`~sloads.export.coordinates.
    tail_torsion_to_airplane` derives it and the exported deck already calls it,
    so this routes through that owner rather than growing a second copy of the
    one asymmetry a fin deck can get silently backwards.

    Called with the raw-Imperial unit set, so the return is unscaled lb-in; each
    consumer applies its own safety factor and unit conversion afterwards.
    """
    if load.body_moments:
        return (load.mxx_free, load.myy_free, load.mzz_free)
    if load.component in ("htail", "vtail"):
        return tail_torsion_to_airplane(load.myy_free, load.component)
    mx, _zero, mz = bending_moment_vector(load.mxx_free, load.mzz_free)
    return (mx, load.myy_free, mz)


def _applied_csv_fields(u: DeliverableUnits,
                        table_sf: Optional[float] = None) -> List[str]:
    """Applied-load CSV header row for unit set ``u`` (D-21: units in-band)."""
    ln = u.length.label
    fo, mo = (load_label(u.force.label, table_sf),
              load_label(u.moment.label, table_sf))
    return [
        "Case", "Station", "GID", f"X ({ln})", f"Y ({ln})", f"Z ({ln})",
        # The whole applied vector, in body axes and in vector order, so a
        # consumer maps column to FORCE/MOMENT component without deciding
        # whether an absent column is a zero or an omission.
        f"Fx ({fo})", f"Fy ({fo})", f"Fz ({fo})",
        f"Mx ({mo})", f"My ({mo})", f"Mz ({mo})",
        "MyyAxis",                 # torsion reference axis (in-band, like SF)
        "SF",                      # the case's limit -> ultimate factor
    ]


#: The applied-load CSV each component is delivered as (note 44 OR-141a).
#:
#: One file per surface rather than one airframe file with a component column: a
#: consumer loads the surface they are sizing, and a single file would have to be
#: filtered before it could be used -- the retyping OR-64 exists to prevent, one
#: step further on.
APPLIED_CSV_NAMES = {
    "wing": "wing_applied_loads.csv",
    "fuselage": "fuselage_applied_loads.csv",
    "htail": "htail_applied_loads.csv",
    "vtail": "vtail_applied_loads.csv",
    "landing_gear": "landing_gear_applied_loads.csv",
    "engine": "engine_applied_loads.csv",
}


def applied_load_csv(arg: ResultsArg, header_comment: str = "", *,
                     system: UnitSystem = UnitSystem.IMPERIAL,
                     component: str = "wing",
                     project: Optional[Project] = None) -> str:
    """One component's applied load set as a CSV -- its appendix, as a file.

    For the wing: one row per strip and one per concentrated wing mass, root to
    tip. For the fuselage: one per beam station. For either tail: one per strip,
    plus the discrete control-surface nodes and the T-tail transfer. LIMIT
    throughout (the case's ``SF`` is stated in the last column and applied
    nowhere). This is the file a structures model is built from: every row is a
    load to apply at the point the row states, and nothing in it is a running
    total.

    The rows are :func:`applied_loads`, which is also what the appendix prints,
    so the table and the file cannot disagree; **G-OR-90** holds both to the
    cards the deck writes.

    Written in the solver unit channel, like the deck and the span-load CSV
    beside it -- a set of applied loads is a deck companion, not a
    human-readable deliverable.
    """
    u = solver_units(system)
    rows = list(applied_loads(component, arg, project))
    fields = _applied_csv_fields(u, shared_basis_factor(rows))
    x_h, y_h, z_h, fx_h, fy_h, fz_h, mx_h, my_h, mz_h = fields[3:12]
    buf = _io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    for load in rows:
        sf = load.safety_factor
        gx, gy, gz = to_grid(load.x, load.y, load.z, u)
        fx, fy, fz = to_force(load.fx, load.fy, load.fz, u)
        # The record is in the calc's moment convention; the body-axis map has
        # one owner and this is it.
        bmx, bmy, bmz = applied_body_moments(load)
        mx, my, mz = to_moment(bmx, bmy, bmz, u)
        writer.writerow({
            "Case": load.case, "Station": load.label,
            # Blank, not a placeholder id: a concentrated mass has no grid in
            # the exported deck, and inventing one here would read as a node a
            # consumer could reference.
            "GID": "" if load.gid is None else load.gid,
            x_h: f"{gx:.3f}", y_h: f"{gy:.3f}", z_h: f"{gz:.3f}",
            fx_h: f"{fx:.1f}", fy_h: f"{fy:.1f}", fz_h: f"{fz:.1f}",
            mx_h: f"{mx:.0f}", my_h: f"{my:.0f}", mz_h: f"{mz:.0f}",
            "MyyAxis": load.torsion_axis,
            "SF": sf_str(sf),
        })
    return header_comment + _APPLIED_CSV_NOTES[component] + buf.getvalue()


def write_applied_load_csv(arg: ResultsArg, path: str, *,
                           header_comment: str = "",
                           system: UnitSystem = UnitSystem.IMPERIAL,
                           component: str = "wing",
                           project: Optional[Project] = None) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(applied_load_csv(arg, header_comment, system=system,
                                  component=component, project=project))


















# --------------------------------------------------------------------------- #
# Side-of-body internal loads (step 13, note 24 R-3)
# --------------------------------------------------------------------------- #
#: A station this close (in) to the side of body is *at* it -- the existing node
#: becomes the SOB reporting node instead of a coincident duplicate.
_SOB_COINCIDENT_TOL = 1e-9


@dataclass
class SobInternalLoads:
    """The wing internal load at the side-of-body cut, in the calc's columns.

    The **wing root design load** (step 13): shear / bending / torsion carried
    across the wing-to-fuselage joint at butt line ``y`` -- distinct from the
    half-span totals, which include the centre-box strip loads inboard of the
    joint and overstate root bending by ~23 % on the reference GA wing (plan 10
    §1.1). Columns and signs are the span CSV's cumulative set (``Sz``/``Sx``/
    ``Mxx``/``Myy``/``Mzz``), torsion about the case's stated axis; magnitudes
    are LIMIT like every load sloads delivers (OR-116)."""
    y: float
    sz: float
    sx: float
    mxx: float
    myy: float
    mzz: float


def sob_internal_loads(result: WingLoadResult, sob_y: float) -> SobInternalLoads:
    """Closed-form SOB internal load: the applied nodal loads outboard, summed.

    One of the **two ways** the side-of-body load is stated (note 24 R-3), and
    the reference the other -- the solver's CBAR end force in the first element
    outboard of the SOB node -- is gated against in the round-trip harness.
    Each exported nodal load at ``p`` contributes its force plus the lever-arm
    couple about the cut (``fz*(y - sob_y)`` and the concentrated-mass offset
    couples ``mx``/``mz``, which restore lever arms the station table cannot
    carry), so the sum is exactly the static resultant of everything the deck
    applies outboard of the cut. A station coincident with the cut counts as
    outboard: the joint carries the loads applied *at* it.

    The general transfer rule this instantiates -- a load at ``p`` moved to
    node ``n`` carries the couple ``(p - n) x F`` -- has its single owner in
    :func:`sloads.export.coordinates.transfer_couple` (note 24 R-11, shipped
    with the step 12 LRA exporter).
    """
    loads = wing_nodal_loads(result)
    x_cut, _y, z_cut = sob_reference_point(result, sob_y)
    sz = sx = mxx = myy = mzz = 0.0
    for nl in loads:
        if nl.y < sob_y - _SOB_COINCIDENT_TOL:
            continue
        arm = nl.y - sob_y
        sz += nl.fz
        sx += nl.fx
        mxx += nl.fz * arm + nl.mx
        mzz += nl.fx * arm + nl.mz
        # Torsion is a genuine transfer now that the cards carry free moments:
        # the chordwise and vertical arms to the cut, plus the free moment
        # itself. Under the old differenced cards ``my`` already held the
        # transfer and this term would have doubled it (note 46 OR-67).
        myy += (nl.z - z_cut) * nl.fx - (nl.x - x_cut) * nl.fz + nl.my
    return SobInternalLoads(sob_y, sz, sx, mxx, myy, mzz)


def sob_reference_point(result: WingLoadResult,
                        sob_y: float) -> Tuple[float, float, float]:
    """The point the side-of-body loads are stated about: the LRA at ``sob_y``.

    One owner, because a torsion is only defined about a point and the two
    halves of the side-of-body statement -- :func:`sob_internal_loads` outboard
    and :func:`sob_collapsed_load` inboard -- must be about the *same* one or
    their sum is not the half-span total. Before the cards carried free torsion
    the question did not arise: the summed ``my`` had no chordwise dependence,
    so any reference gave the same answer and a caller could pass a placeholder.
    Now it cannot (note 46 OR-67).
    """
    x, z = _lra_point_at(wing_nodal_loads(result), sob_y)
    return (x, sob_y, z)


def _lra_point_at(loads: List[NodalLoad], y: float) -> Tuple[float, float]:
    """The ``(x, z)`` of the loads reference axis at span station ``y``.

    The deck's nodes lie on the LRA, so the axis between them is the straight
    line this interpolates; outside the loaded span it is held at the end node.
    A torsion is only defined about a point, and the side-of-body cut needs one
    that is on the same axis as the stations it is compared against.
    """
    if not loads:
        return (0.0, 0.0)
    if y <= loads[0].y:
        return (loads[0].x, loads[0].z)
    for a, b in zip(loads, loads[1:]):
        if y <= b.y:
            span = b.y - a.y
            f = (y - a.y) / span if span else 0.0
            return (a.x + f * (b.x - a.x), a.z + f * (b.z - a.z))
    return (loads[-1].x, loads[-1].z)












# --------------------------------------------------------------------------- #
# Body (fuselage) station GIDs
# --------------------------------------------------------------------------- #
# The fuselage net distribution (Ch 15) is a longitudinal beam: each station
# carries an applied vertical force (inertia + tail air load + wing reaction)
# that sums to zero in equilibrium. Note 56 D-56.2 deleted the per-component
# deck that wrote those as cards; what stays is the **numbering**, because the
# fuselage applied-load set and the CONM2 mass export both state which station
# they are at, and they have to agree.
#
# GIDs are keyed off each station's provenance (``BodyStationLoad.source``), not
# its index in the merged table: the wing carry-through reaction (M4-1) inserts
# extra nodes into the middle of the beam, and an index-based GID would have
# renumbered every mass station aft of the wing whenever the spar stations
# changed. Mass/tail stations therefore keep the historical ``1001 + i`` in
# nose->tail order and the reaction nodes take a disjoint block at ``1501 +``.
_BODY_MASS_BAND = band("body-mass")          # 1001-1500
_BODY_CARRY_BAND = band("body-reaction")     # 1501-2000

#: ``BodyStationLoad.source`` values that belong to the reaction-node GID block.
_BODY_REACTION_SOURCES = ("carry", "correction")


def beam_station_gid(index: int) -> int:
    """GID of the ``index``-th **fuselage mass station**, nose->tail.

    The station table is the mass SSOT's
    (:func:`sloads.mass_distribution.fuselage_beam_stations`), and its stations
    all enter :func:`body_station_gids` with ``source="mass"`` -- so they take
    the ``1001+`` block in order. Exposed so the CONM2 mass export attaches to
    the same nodes the fuselage applied-load set states, rather than re-deriving
    the numbering (``CLAUDE.md`` practice 3).
    """
    return _BODY_MASS_BAND.allocate(index)


def body_station_gids(result: BodyLoadResult) -> List[int]:
    """Stable sbeam GIDs for one body result's stations, in table order.

    Fuselage mass stations and the tail air-load station number from the
    ``body-mass`` band in nose->tail order; the wing carry-through reaction
    nodes (or the fallback correction nodes) from ``body-reaction``. Keying on
    ``source`` keeps a mass station's GID
    fixed no matter how many reaction nodes are inserted around it."""
    gids: List[int] = []
    n_mass = 0
    n_reaction = 0
    try:
        for s in result.stations:
            if s.source in _BODY_REACTION_SOURCES:
                gids.append(_BODY_CARRY_BAND.allocate(n_reaction))
                n_reaction += 1
            else:
                gids.append(_BODY_MASS_BAND.allocate(n_mass))
                n_mass += 1
    except ValueError as exc:
        raise ValueError(
            f"body export: {n_mass} mass and {n_reaction} reaction stations "
            f"exceed their GID band (would collide with the next band) -- {exc}"
        ) from None
    return gids




def _body_results(arg: "Union[Project, BodyLoadResult, Sequence[BodyLoadResult]]") -> List[BodyLoadResult]:
    if isinstance(arg, Project):
        if arg.loads is None or not arg.loads.body_net:
            raise ValueError(
                "Project has no net body loads to export -- run the 'body_loads' "
                "module (build_body_loads) first so Project.loads.body_net is set."
            )
        return list(arg.loads.body_net)
    if isinstance(arg, BodyLoadResult):
        return [arg]
    results = list(arg)
    if not results:
        raise ValueError("no body-load results to export")
    return results




































# --------------------------------------------------------------------------- #
# Spanwise empennage station GIDs (plan 09 T4)
# --------------------------------------------------------------------------- #
# Note 56 D-56.2 deleted the spanwise tail decks; the **numbering** stays,
# because the h-tail and fin applied-load sets state which station each row is
# at, and the LRA model ties its own chains to the same named points. The two
# surfaces do not share an axis map -- the h-tail spans ``y`` and loads ``fz``,
# the fin spans ``z`` and loads ``fy`` -- but that mapping is **not** written
# here: it comes from ``coordinates.py``, the single owner, which is also where
# the fin's torsion sign is derived (plan 09 §2 axes note).
_TAIL_SPAN_BANDS = {"htail": band("tail-span-htail"),
                    "vtail": band("tail-span-vtail")}


def tail_span_gid(component: str, i: int) -> int:
    """GID of spanwise station ``i`` of ``component``.

    Its own band per surface, registered in :mod:`sloads.export.bands` and
    proved disjoint from every other family there -- so an assembled airframe
    can carry both surfaces at once. The claim used to live in this docstring
    alone, and was false for two months against the balanced deck (review F-C1).
    """
    gid_band = _TAIL_SPAN_BANDS.get(component)
    if gid_band is None:
        raise ValueError(
            f"tail span export: unknown component {component!r} -- expected "
            "'htail' or 'vtail'; it has no GID block")
    return gid_band.allocate(i)


_TAIL_CONTROL_BANDS = {"htail": band("tail-control-htail"),
                       "vtail": band("tail-control-vtail")}


def tail_control_gid(component: str, i: int) -> int:
    """GID of hinge/actuator node ``i`` of ``component``'s control surface (T6).

    Its own band per surface, for the reason the registry states: a hinge station
    is not a strip midpoint, so it is a different point, and a load set that
    gained hinges must not renumber the strips beside them.
    """
    gid_band = _TAIL_CONTROL_BANDS.get(component)
    if gid_band is None:
        raise ValueError(
            f"tail control export: unknown component {component!r} -- expected "
            "'htail' or 'vtail'; it has no GID block")
    return gid_band.allocate(i)


def _tail_span_results(arg, component: str) -> List:
    """The spanwise results to state an applied load set for, one surface."""
    if isinstance(arg, Project):
        loads = arg.loads
        # An explicit map, not an attribute probe: an unknown component is a
        # caller error and says so, instead of reading as "no loads" (CH-2).
        slices = ({"htail": loads.htail_span, "vtail": loads.vtail_span}
                  if loads else {"htail": [], "vtail": []})
        if component not in slices:
            raise ValueError(
                f"tail span export: unknown component {component!r} -- expected "
                "'htail' or 'vtail'")
        slice_ = slices[component]
        if not slice_:
            raise ValueError(
                f"Project has no spanwise {component} loads to export -- run the "
                f"'tail_span' module (build_tail_span) first so "
                f"Project.loads.{component}_span is set.")
        return list(slice_)
    results = [arg] if isinstance(arg, TailSpanResult) else list(arg)
    if not results:
        raise ValueError(f"no spanwise {component} results to export")
    return results


























