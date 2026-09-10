"""Coordinate / units map: SLOADS airplane axes -> sbeam global frame (CID 0).

The whole suite works in the original program's Imperial airplane axes, all in
**inches** (SLOADS station/butt/waterline):

* ``x`` -- fuselage station, **positive aft**
* ``y`` -- butt line, **positive right** (out the starboard wing)
* ``z`` -- waterline, **positive up**

Forces follow the same axes: ``fz`` is lift (+up), ``fx`` is drag (+aft); the
wing torsion ``myy`` is the moment about the spanwise ``y`` axis.

sbeam runs in a single basic coordinate system (NASTRAN ``CID 0``), right-handed,
in whatever consistent unit set the user's model uses. SLOADS already uses a
right-handed inch frame that matches that convention, so the transform is the
**identity** -- the export emits inches into ``CID 0`` directly.

This module is the *single editable point* for that mapping: if a downstream
sbeam model ever needs a sign flip, an axis swap, or an inch->other-unit scale,
change it here and every exported GRID / FORCE / MOMENT follows.

**The unit scale (M4-20 step 4).** That "other-unit scale" is now real: a deck
may be written in the SI solver set (N / mm / N*mm / MPa) instead of the Imperial
one. Each function takes a :class:`~sloads.units.DeliverableUnits` and applies
its factor, so this module is the *only* place in the export channel where a load
or a coordinate is multiplied by anything. Nothing in ``sbeam_bridge`` scales:
its arithmetic is unchanged and unit-free, and it routes every dimensional value
it emits -- cards *and* CSV cells -- through these three functions, so a file's
numbers cannot disagree with the cards beside it.

Imperial is the all-1.0 identity set, so an Imperial deck takes the same code
path and cannot drift.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Tuple

from ..gear_loads import transfer_couple as _transfer_couple
from ..tail_geometry import SurfacePlane, surface_plane
from ..units import Channel, DeliverableUnits, UnitSystem, deliverable_units

if TYPE_CHECKING:  # pragma: no cover - typing only, and a cycle at runtime
    from ..models.inputs import EngineInput

Vec3 = Tuple[float, float, float]

# The NASTRAN coordinate-system id the bridge emits into. CID 0 is the basic
# (global) frame; GRID/FORCE/MOMENT cards stamp this in their CP/CID field.
SBEAM_CID = 0

#: The default unit set: the Imperial identity, so an un-parameterised call
#: behaves exactly as it did before the unit scale existed.
IMPERIAL = deliverable_units(UnitSystem.IMPERIAL, Channel.SOLVER)


def _checked(units: DeliverableUnits) -> DeliverableUnits:
    """Reject a unit set that is not dimensionally consistent (D-19).

    A solver deck's correctness rests on ``moment == force x length`` and
    ``pressure == force / length^2``. The human-readable set breaks both in SI
    (N*m and kPa against a mm length) and is a plausible thing to pass by
    mistake, since it is what every *report* is written in -- so refuse it here,
    at the one point every card and cell passes through, rather than emit a deck
    that parses cleanly and sizes structure to a 1000x-wrong torsion.
    """
    if not units.is_consistent:
        raise ValueError(
            f"{units.channel.value} unit set ({units.force.label}, "
            f"{units.length.label}, {units.moment.label}, {units.pressure.label}) "
            "is not dimensionally consistent and must not be written to an sbeam "
            "deck -- resolve it with deliverable_units(system, Channel.SOLVER)"
        )
    return units


def to_grid(x: float, y: float, z: float,
            units: DeliverableUnits = IMPERIAL) -> Vec3:
    """Map a SLOADS station point (in) to an sbeam GRID location (CID 0)."""
    k = _checked(units).length.factor
    return (x * k, y * k, z * k)


def to_force(fx: float, fy: float, fz: float,
             units: DeliverableUnits = IMPERIAL) -> Vec3:
    """Map a SLOADS force vector (lb) to sbeam global components (CID 0)."""
    k = _checked(units).force.factor
    return (fx * k, fy * k, fz * k)


def to_moment(mx: float, my: float, mz: float,
              units: DeliverableUnits = IMPERIAL) -> Vec3:
    """Map a SLOADS moment vector (lb-in) to sbeam global components (CID 0)."""
    k = _checked(units).moment.factor
    return (mx * k, my * k, mz * k)


def bending_moment_vector(mxx: float, mzz: float,
                          units: DeliverableUnits = IMPERIAL) -> Vec3:
    """Map a SLOADS spanwise **bending** pair to a CID-0 moment vector.

    ``mxx`` (out-of-plane, from ``fz``) and ``mzz`` (in-plane, from ``fx``) are
    beam bending moments, both stored by the calc as *positive-magnitude*
    integrals of ``load x (y - y_ref)``. Against the right-handed ``r x F``
    vector that a solver recovers from the cards, the two do **not** carry the
    same sign:

    * ``Mxx`` -> ``+x``.   ``(r x F)_x = dy*fz``, so the calc's sign is the
      vector's.
    * ``Mzz`` -> ``-z``.   ``(r x F)_z = -dy*fx``, so the calc's ``mzz`` is the
      *negation* of the vector component.

    Measured, not assumed: on ``ga6_normal`` the exported deck's resultant about
    the root reproduces ``mxx`` at a ratio of ``+1.0000`` and ``mzz`` at
    ``-1.0000`` on every case (both unit systems).

    This asymmetry is a sign convention, so it lives here -- the single editable
    point for the axis map -- rather than being spelled out at the card writer
    and copied again at its gate (``CLAUDE.md`` required practice 3). Callers
    needing an applied-couple card, or a moment gate, take it from this function.
    """
    k = _checked(units).moment.factor
    # ``+ 0.0`` normalises IEEE negative zero: the negation turns a zero ``mzz``
    # into ``-0.0``, which formats as ``-0.000000E+00`` and would rewrite the
    # MOMENT card of every wing that carries no concentrated mass -- a byte
    # change with no number behind it.
    return (mxx * k, 0.0, -mzz * k + 0.0)


def to_pressure(psi: float, units: DeliverableUnits = IMPERIAL) -> float:
    """Map a SLOADS load intensity (lb/in^2) to the deck's stress unit."""
    return psi * _checked(units).pressure.factor


# --------------------------------------------------------------------------- #
# The load-transfer rule (note 24 R-11 / implementation note 25 LM-1)
# --------------------------------------------------------------------------- #
#: **The transfer rule** (note 24 R-11), re-exported from its implementation in
#: :func:`sloads.gear_loads.transfer_couple`. A load ``(F, M)`` at ``p`` moved to
#: ``n`` becomes ``(F, M + (p - n) x F)`` -- the exact static equivalent, so any
#: set transferred this way has the identical resultant it had before, which is
#: what the plan-07 invariant on the LRA model's transferred set asserts. Every
#: mover in the export channel is an instance of it: the gear point->trunnion
#: transfer, the concentrated-mass offset couples, the step-13
#: ``sob_collapsed_load``, the LRA model's nearest-node routing (LM-7).
#:
#: R-11 asked for **one** cross product rather than one hand-rolled per call
#: site, and it was written twice -- identically, here and in ``gear_loads``, each
#: docstring claiming to be the owner. Consolidated 2026-08-29 (#139) onto the
#: lower layer, since the calc side cannot import the export side: the name stays
#: here so no export call site moves, but there is one implementation.
transfer_couple = _transfer_couple


# --------------------------------------------------------------------------- #
# Reflection about the airplane centreline plane (plan 11 decision B-6)
# --------------------------------------------------------------------------- #
# Every asymmetric load case has an opposite-hand twin -- +beta yaw implies the
# -beta case, an aileron roll right implies roll left, an engine-out on the left
# implies the right. They are derived by **reflecting** the computed case rather
# than recomputing it, which is what keeps the oracle-locked FAR 23 path out of
# the handedness question entirely: SELECT, WINGINER and the V-n core never see
# it, because the mirroring happens at assembly.
#
# One owner, here, beside the axis maps, plus a drift guard in
# ``tests/test_balance.py`` -- ``CLAUDE.md`` required practice 3. A sign
# convention copied to a second call site is exactly the class of error that
# produces a deck which parses, solves, and sizes structure to a load the
# airplane never sees.

def reflect_point(x: float, y: float, z: float) -> Vec3:
    """Mirror a position through the centreline plane: ``y -> -y``."""
    return (x, -y, z)


def reflect_force(fx: float, fy: float, fz: float) -> Vec3:
    """Mirror a force. A force is a **true vector**: only its ``y`` component,
    the one along the mirror normal, changes sign."""
    return (fx, -fy, fz)


def reflect_moment(mx: float, my: float, mz: float) -> Vec3:
    """Mirror a moment. A moment is an **axial** (pseudo) vector, so it
    transforms the other way round: the two components *in* the mirror plane
    flip and the normal one does not.

    Physically this is the whole point of the operator. Roll (``mx``) and yaw
    (``mz``) reverse -- a roll to starboard mirrors into a roll to port -- while
    pitch (``my``) is unchanged, because pitching is symmetric about the
    centreline. Applying the force rule to a moment would mirror a rolling case
    into itself and negate its pitch, which balances and means nothing.
    """
    return (-mx, my, -mz)


def reflect_side(side: str) -> str:
    """The mirrored side tag: ``"R" <-> "L"``, centreline unchanged."""
    return {"R": "L", "L": "R"}.get(side, side)


# --------------------------------------------------------------------------- #
# Empennage local frame -> airplane axes (plan 09 §2 axes note)
# --------------------------------------------------------------------------- #
# A spanwise tail strip is computed in the surface's own **(span, chord)** frame,
# which is what lets one integrator serve both surfaces. Mapping that frame onto
# airplane axes is where the two surfaces stop being alike, and it has one owner
# -- here -- with a drift guard, because it is a sign/axis convention and those
# are exactly what CONVENTIONS.md §7 says must never be hand-rolled per call site.
#
# *Which* plane a surface spans is not decided here: the four maps below ask
# ``tail_geometry.surface_plane`` (design note 54, D-54.2 / #220), the one
# authority, instead of each testing the component name themselves.
#
#   horizontal tail: span -> y, normal force -> fz, torsion -> myy  (the wing's map)
#   vertical tail:   span -> z, normal force -> fy, torsion -> myy
#
# The fin's normal force is a **side** force. Emitting it as ``fz`` -- the obvious
# copy-paste from the h-tail writer -- produces a deck that parses, solves, and
# loads the fin in the one direction it is not designed for.

def tail_station_to_airplane(x: float, span: float, component: str,
                             root_z: float = 0.0) -> Vec3:
    """Map a tail station's local ``(x, span)`` to an airplane ``(x, y, z)`` point."""
    if surface_plane(component) is SurfacePlane.WATERLINE:
        return (x, 0.0, root_z + span)
    return (x, span, root_z)


def tail_force_to_airplane(normal: float, component: str) -> Vec3:
    """Map a tail strip's normal force to airplane force components.

    The horizontal tail's normal force is vertical (``fz``); the vertical tail's
    is lateral (``fy``).
    """
    if surface_plane(component) is SurfacePlane.WATERLINE:
        return (0.0, normal, 0.0)
    return (0.0, 0.0, normal)


def tail_axial_to_airplane(axial: float, component: str) -> Vec3:
    """Map a tail strip's **span-axis** (axial) force to airplane components.

    A load along the member's own span: it compresses or stretches the beam and
    bends nothing. The h-tail spans in ``y`` and the fin in ``z``, so the same
    local number lands on different airplane axes -- which is the entire reason
    this is here and not a literal at the call site.

    Only the fin has a producer for it (``-n_z*W_vt``: the vertical acceleration
    runs along a fin's span). The h-tail's mapping is written anyway, because the
    day a spanwise ``n_y`` reaches the horizontal tail the axis must already be
    right, not invented then.
    """
    if surface_plane(component) is SurfacePlane.WATERLINE:
        return (0.0, 0.0, axial)
    return (0.0, axial, 0.0)


def ttail_transfer_to_airplane(fz: float, myy: float) -> Tuple[Vec3, Vec3]:
    """Map a T-tail's transferred tip set to airplane force/moment components.

    The one load on a fin deck that is **not** in the fin's local frame. Every
    other card there is a side load or a torsion about the fin's own span axis;
    this is the horizontal tail sitting on top of the fin, and what it hands down
    is a *vertical* force (airplane ``z``, axial to the fin) with the pitching
    moment ``myy`` its fore-aft offset makes about the tip node (airplane ``y``,
    the h-tail's span axis, not the fin's).

    So the map is the identity, and it is written here anyway -- as a named
    function rather than a literal at the writer -- because the identity is the
    claim being made. The plausible error is to route this force through
    :func:`tail_force_to_airplane` like everything else in the deck, which would
    emit the horizontal tail's lift as a *side* load on the fin: a deck that
    parses, solves, and bends the fin sideways with a pull-up.

    Roll and yaw are zero by construction (plan 09 decision T-16): the concurrent
    pairing is a balancing condition, which is symmetric, so the h-tail's two
    halves cancel about the centreline.
    """
    return (0.0, 0.0, fz), (0.0, myy, 0.0)


def tail_torsion_to_airplane(torsion: float, component: str) -> Vec3:
    """Map a tail strip's torsion about its LRA to airplane moment components.

    A surface's torsion is about its **span** axis, and that is where the two
    empennage surfaces part company: the h-tail's span is ``y``, so its torsion is
    ``myy``; the fin's span is ``z``, so **its torsion is** ``mzz``, not ``myy``.

    Sign, derived rather than asserted. The stored strip torsion is
    ``(x_lra - x_load) * normal``. For the h-tail, ``r x F`` with
    ``r = (x_load - x_lra, 0, 0)`` and ``F = (0, 0, fz)`` gives
    ``my = (x_lra - x_load)*fz`` -- the stored value unchanged. For the fin,
    ``F = (0, fy, 0)`` gives ``mz = (x_load - x_lra)*fy`` -- the stored value
    **negated**.

    That sign is the whole reason this function exists rather than a literal at
    the call site: a fin torsion emitted with the h-tail's sign is a deck that
    parses, solves, and twists the fin the wrong way.
    """
    if surface_plane(component) is SurfacePlane.WATERLINE:
        return (0.0, 0.0, -torsion)
    return (0.0, torsion, 0.0)


# --------------------------------------------------------------------------- #
# Engine mount: the thrust line, and the load an engine applies to the airframe
# --------------------------------------------------------------------------- #
#: The thrust axis used where an installation does not state its own thrust
#: line: airplane **forward**, which is ``-x`` because ``x`` is positive aft.
ASSUMED_THRUST_AXIS: Vec3 = (-1.0, 0.0, 0.0)


class ThrustLineError(ValueError):
    """A thrust line entered as one point of two (design note 53, D-53.1)."""


def engine_thrust_axis(engine: "EngineInput") -> Tuple[Vec3, bool]:
    """``(unit vector along the thrust line, whether it was assumed)``.

    **The thrust line is an input** (design note 53, D-53.1): two entered
    points, ``thrust_line_aft`` and ``thrust_line_fwd``, whose difference is the
    axis. ``thrust_line_fwd`` is the forward one **by name** -- nothing infers
    it from the smaller fuselage station -- which is what lets a pusher
    installation be stated without a special case: the torque's sense is about
    which way the shaft turns as the pilot sees it, not about which end of the
    engine the propeller is on.

    Both points left at the origin means **not entered** -- the sentinel
    ``LandingGearInput.attach`` already uses for an optional station, and a
    point at the nose datum on the centreline at waterline zero is not a thrust
    line anybody means. The axis is then the airplane's forward direction and
    the ``True`` flag says so, for every deliverable to mark -- the same
    explicit-with-flagged-inference shape as ``EngineInput.mounted_on`` (BM-4)
    and ``derived_geometry.fuselage_centreline``. **Two grades of provenance,
    not three.** Until D-53.3 this function derived a middle grade, the
    direction from the engine CG to the hub (note 44 OR-161, now superseded).
    That is a line between two *mass* stations, not the shaft, and it inherits
    every error in either: measured 14.0 deg off ``x`` on ``ga6_normal`` --
    which put an ``mz`` of -178.8 ft-lb into a section 10 for an airplane that
    has no such moment -- and 71.6 deg, very nearly straight up, on
    ``cessna_210``, whose engine CG waterline is a filed defect. A derivation
    that turns a station error into an orientation is worse than an assumption
    that says it is one.

    One point of the two raises :class:`ThrustLineError`, by name: a
    half-entered line is neither ignored nor completed from a derived second
    point (the C210-21 load-bearing-blank pattern). Two coincident points are
    the same refusal -- they state no direction.

    This is here rather than at a call site because it is an *axis resolution*,
    and ``CONVENTIONS.md`` §1 makes this module the single edit point for those.
    """
    aft, fwd = engine.thrust_line_aft, engine.thrust_line_fwd
    stated_aft, stated_fwd = any(aft), any(fwd)
    if not stated_aft and not stated_fwd:
        return ASSUMED_THRUST_AXIS, True
    if not (stated_aft and stated_fwd):
        missing = "thrust_line_aft" if not stated_aft else "thrust_line_fwd"
        raise ThrustLineError(
            f"engine {engine.engine_designation or '(unnamed)'} states half a "
            f"thrust line: {missing} is left at the origin, which is this "
            f"schema's 'not entered'. Enter both points or neither -- a single "
            f"point states no direction, and the missing one is not derived.")
    dx, dy, dz = (float(f) - float(a) for f, a in zip(fwd, aft))
    magnitude = math.sqrt(dx * dx + dy * dy + dz * dz)
    if magnitude <= 0.0:
        raise ThrustLineError(
            f"engine {engine.engine_designation or '(unnamed)'} states a "
            f"thrust line whose two points coincide, so it states no "
            f"direction. Move one of them, or clear both to use the "
            f"airplane's forward axis.")
    return (dx / magnitude, dy / magnitude, dz / magnitude), False


def engine_applied_load(axis: Vec3, *, torque: float = 0.0,
                        thrust: float = 0.0, vertical_down: float = 0.0,
                        side: float = 0.0, myy: float = 0.0, mzz: float = 0.0,
                        ) -> Tuple[Vec3, Vec3]:
    """The six airplane-axis components an engine applies to its mount.

    ``(fx, fy, fz), (mx, my, mz)`` at the engine's combined CG, from the
    quantities ``sloads.modules.engine`` publishes per condition. Unit-agnostic:
    forces come out in whatever ``thrust``/``vertical_down``/``side`` are in and
    moments in whatever ``torque_reaction``/``myy``/``mzz`` are in (the module's
    lb and ft-lb), because nothing here scales -- this is a rotation, and the
    unit channel is :func:`to_force`/:func:`to_moment`'s to apply.

    Three sign facts, each **derived** rather than asserted (note 44 §20, OR-160
    and OR-162):

    * **The torque acts about the thrust line**, not about ``x``, and "clockwise
      from the pilot's view is positive" *is* the right-hand sense about that
      line. The pilot looks along ``axis``; an observer looking along a vector
      sees a right-hand-positive rotation as clockwise. So no flip is applied to
      the scalar -- it is rotated, and nothing else.
    * **``torque`` is already what the engine applies to the airframe**, despite
      being printed under the word *reaction*. Third law, twice: a propeller
      turning clockwise from the pilot's seat is driven by ``+Q`` from the
      engine, so it returns ``-Q`` to the engine; the mount holds the engine
      against that with ``+Q``; and the engine therefore delivers ``-Q`` to the
      airframe. ``-Q`` is exactly what ``mx_mount_torque`` carries and what the
      oracle prints as a negative ``ENG MOUNT TORQUE``. Nothing here negates it.
    * **The airplane rolls left, and the resolution says so.** With ``axis`` the
      forward direction ``(-1, 0, 0)``, ``-Q`` about it becomes ``mx = +Q``, and
      a positive moment about the aft-positive ``x`` axis carries starboard up --
      the left roll a clockwise propeller's torque produces. That the two
      independent readings agree is what makes the sign derived rather than
      chosen, and it is why the printed scalar and the printed ``mx`` carry
      opposite signs on a conventional installation.
    * **Thrust runs along the same axis**, so it is resolved with it; a nose-up
      thrust line lands part of its load on ``fz``, which is exactly the effect
      that resolving it makes visible.

    ``vertical_down`` is the module's positive-downward vertical load, so it
    lands on ``fz`` negated (``z`` is positive up). ``myy``/``mzz`` are the
    23.371(b) gyroscopic moments, which the module already publishes about the
    airplane's ``y`` and ``z`` axes and which are therefore added unrotated.
    """
    applied_torque = float(torque)
    ax, ay, az = axis
    force = (thrust * ax, thrust * ay + float(side), thrust * az - float(vertical_down))
    moment = (applied_torque * ax,
              applied_torque * ay + float(myy),
              applied_torque * az + float(mzz))
    return force, moment
