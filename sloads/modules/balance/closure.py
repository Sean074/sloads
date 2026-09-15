"""Resultants, and the six-DOF closure that leaves the case free-free.

Part of :mod:`sloads.modules.balance` (#191); the subsystem docstring is the
package's. What is left over after the applied sets are summed is distributed as
rigid-body relief -- :mod:`sloads.rigid_body` owns the mechanics; this is where a
case uses them, and the pre-closure residual it reports is the diagnostic the
gates in :mod:`~sloads.modules.balance.queries` judge.
"""

from __future__ import annotations

import math
from typing import List, Sequence, Tuple

from ...models import BalancedLoad, CgCase
from ...rigid_body import InertiaTensor, PointMass, SelfInertia, inertia_tensor, relief_force, relief_moment


def resultant(loads: Sequence[BalancedLoad],
              ref: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """``(Fx, Fz, My)`` of ``loads`` about ``ref`` -- free moments plus lever arms.

    The symmetric three. :func:`resultant6` is the full rigid-body resultant;
    this stays as the in-plane view every symmetric caller wants.
    """
    fx, _, fz, _, my, _ = resultant6(loads, ref)
    return fx, fz, my


def resultant6(loads: Sequence[BalancedLoad],
               ref: Tuple[float, float, float]) -> Tuple[float, float, float,
                                                         float, float, float]:
    """``(Fx, Fy, Fz, Mx, My, Mz)`` of ``loads`` about ``ref``.

    All six, from B7 on, because an antisymmetric case is out of balance in a
    degree of freedom the symmetric three cannot see: ``ACRL`` assembled without
    a roll term closes ``Fx``/``Fz``/``My`` to 1e-11 and carries a whole
    unbalanced rolling moment, which is precisely the case reading as balanced
    while meaning nothing.

    ``Fy`` and ``Mz`` are identically zero for every family shipped today -- no
    load in the suite has a side component yet -- and are computed rather than
    assumed so B8a's lateral cases inherit a resultant that already covers them,
    and so :func:`test_lateral_dof_are_untouched` can pin the fact.
    """
    fx = math.fsum(ld.fx for ld in loads)
    fy = math.fsum(ld.fy for ld in loads)
    fz = math.fsum(ld.fz for ld in loads)
    mx = math.fsum(ld.mx + (ld.y - ref[1]) * ld.fz - (ld.z - ref[2]) * ld.fy
             for ld in loads)
    my = math.fsum(ld.my + (ld.z - ref[2]) * ld.fx - (ld.x - ref[0]) * ld.fz
             for ld in loads)
    mz = math.fsum(ld.mz + (ld.x - ref[0]) * ld.fy - (ld.y - ref[1]) * ld.fx
             for ld in loads)
    return fx, fy, fz, mx, my, mz


#: One ``closure-*`` source per degree of freedom, and the axis of
#: ``omega_dot`` each rotational one carries. Split rather than emitted as a
#: single ``closure-rot`` load because the split is what makes the field
#: *attributable*: the B7 gate isolates the roll strips and compares them with
#: WINGINER's unit-roll set, and a deck reader can see which acceleration put a
#: given card there. The sum of the three is the full field either way.
_ROTATIONAL_SOURCES = (("closure-roll", 0), ("closure-pitch", 1),
                       ("closure-yaw", 2))


def _closure(loads: List[BalancedLoad], cg: CgCase,
             residual: Tuple[float, float, float, float, float, float],
             self_inertia: Sequence[Tuple[Tuple[float, float, float],
                                          SelfInertia]] = (),
             ) -> Tuple[Tuple[float, float, float],
                        Tuple[float, float, float], InertiaTensor]:
    """Close the residual as rigid-body relief; return ``(n, omega_dot, tensor)``.

    **Six** degrees of freedom from B8a-2 (plan 13 decisions L-2/L-3), not the
    four B7 carried and not the two plan 11 B-3 anticipated, and -- more to the
    point -- **one field** rather than four hand-rolled slices of one. The
    relief is ``f_i = -w_i (n + omega_dot x r_i)``, written once in
    :mod:`sloads.rigid_body`; this function decides *what* it is applied to and
    with which accelerations.

    The three translational DOF stay decoupled ratios ``n = F/W`` **because the
    field is referred to the mass set's own centroid**, where ``Sum w_i r_i`` is
    zero by definition: a uniform load factor then produces no moment, and an
    angular acceleration produces no net force. That reference is the loading's
    CG to the last digit on nearly every case (step C1 solves the ballast from
    it), and it is computed here rather than assumed to be, because "nearly"
    is not a closure. ``ga6_normal``'s ``CG4`` loading sits 0.0024 in forward and
    0.0052 in below its own entered CG -- nothing at all until an acceleration
    multiplies it, and the 23.427(a) case's ``q_dot`` of 637 deg/s^2 is what
    multiplies it: referred to the entered CG the same field leaves **0.31 lb**
    of ``Fx`` unclosed (D-R8). The residual reported on the case is still stated
    about the CG, which is what a reader expects; only the relief is solved
    where it is exact.

    The three rotational DOF are **one coupled 3x3 solve** on the assembled
    inertia tensor about that same centroid: the field
    an angular acceleration applies produces the moment ``-[I]{omega_dot}``
    exactly, and ``[I]``'s off-diagonal ``Ixz`` is 8.4 % of the ga6's pitch
    inertia and larger on the regional jet (plan 13 §3.5), so roll and yaw are
    genuinely coupled and three independent ratios would be wrong rather than
    approximate.

    What changed at B8a-2, and what it moved
    ----------------------------------------
    Each acceleration now applies **both** its force components rather than the
    one the vertical-only ancestors carried. That is the difference between
    ``Sum w*d^2`` and a moment of inertia, and it is not uniformly small:

    * pitch gained ``fx = -w*q_dot*dz``. The companion itself is negligible
      (<= 0.08 % of a node load) but the *acceleration* moved, because the pitch
      inertia stopped being ``Sum w*dx^2``: ``q_dot`` fell 18-22 % on
      ``ga6_normal``, 3-4 % on the regional jet;
    * roll gained ``fy = +w*p_dot*dz``, worth 94-518 lb at a peak node -- larger
      than the roll term already in the deck, because ``fz = -w*p_dot*dy``
      touches only the wing strips (every database item sits at ``y = 0``) while
      the companion touches every mass off the roll axis. ``p_dot`` fell 20.7 %
      / 23.2 % accordingly, and the B7 gate reads the *shape* it preserves
      exactly plus that ratio, pinned;
    * yaw is new, and would have been 55 % wrong had it copied the pitch DOF's
      one-component pattern.

    Self-inertia (L-3) rides along as a **free moment** ``-[I_self]{omega_dot}``
    at each node whose mass the assembly carries as a point. It is 13.3 % of
    ``ga6_normal``'s ``Izz``; the regional jet's database enters none.

    The x degree of freedom is not optional: **nothing else in the assembled
    model reacts drag.** The suite has no distributed thrust, and FAR 23's
    longitudinal load factor ``nx`` is exactly this quantity. On ``ga6_normal``
    PHAA the closure gives 0.661 g against the trim's own drag of 0.610. Leaving
    it open would put 17-26 % of ``n*W`` into the support reaction and make
    "reactions ~ 0" untrue in a file that still solved.

    That 0.05 g difference is **not** quadrature (an earlier reading here called
    it "the same strip-quadrature-versus-closed-form gap"; corrected 2026-08-15).
    ``residual_fx`` equals the wing strips' ``Sum fx`` exactly -- nothing in the
    assembled model carries the airplane's **non-wing** drag -- and the gap is
    element-independent: -191.5 lb at 5 elements, -173.4 lb converged at 640. It
    is a missing load, not an integration error, and the same missing load is the
    whole of the pitch residual through its ``(zw - zcg)`` arm. Filed on the
    backlog as "non-wing drag has no carrier in the assembled model".

    The relief is spread over **the inertia loads already in the model**, not
    over the raw item list. Those are the same masses, but at the places the
    assembled model actually carries them -- wing mass out along the span rather
    than on the centreline where the database enters it -- so the deck's internal
    load path stays physical and no relief lands on a node the airplane has no
    mass at.
    """
    zero = (0.0, 0.0, 0.0)
    masses = [(ld, ld.weight_lb) for ld in loads if ld.weight_lb]
    w_total = math.fsum(w for _, w in masses)
    if not w_total:
        return zero, zero, InertiaTensor()

    # The centroid of the masses the model actually carries -- the one point the
    # relief field is exact about (see the docstring).
    cx = math.fsum(ld.x * w for ld, w in masses) / w_total
    cy = math.fsum(ld.y * w for ld, w in masses) / w_total
    cz = math.fsum(ld.z * w for ld, w in masses) / w_total
    points = [PointMass(w, ld.x - cx, ld.y - cy, ld.z - cz) for ld, w in masses]
    tensor = inertia_tensor(points, [si for _, si in self_inertia])
    fx, fy, fz, mx, my, mz = residual
    n = (fx / w_total, fy / w_total, fz / w_total)
    # The residual arrives about the CG; transfer it to the centroid,
    # ``M_c = M_ref + (ref - c) x F``, before solving for the accelerations.
    dx, dy, dz = cg.xcg - cx, 0.0 - cy, cg.zcg - cz
    omega_dot = tensor.solve((mx + dy * fz - dz * fy,
                              my + dz * fx - dx * fz,
                              mz + dx * fy - dy * fx))

    for (ld, w), pm in zip(masses, points):
        r = (pm.dx, pm.dy, pm.dz)
        f = relief_force(w, r, n, zero)
        loads.append(BalancedLoad(x=ld.x, y=ld.y, z=ld.z,
                                  fx=f[0], fy=f[1], fz=f[2],
                                  source="closure-n", side=ld.side))
        for source, axis in _ROTATIONAL_SOURCES:
            if not omega_dot[axis]:
                continue
            only = (omega_dot[0] if axis == 0 else 0.0,
                    omega_dot[1] if axis == 1 else 0.0,
                    omega_dot[2] if axis == 2 else 0.0)
            f = relief_force(w, r, zero, only)
            loads.append(BalancedLoad(x=ld.x, y=ld.y, z=ld.z,
                                      fx=f[0], fy=f[1], fz=f[2],
                                      source=source, side=ld.side))

    for (x, y, z), si in self_inertia:
        m = relief_moment(si, omega_dot)
        if any(m):
            loads.append(BalancedLoad(x=x, y=y, z=z, mx=m[0], my=m[1], mz=m[2],
                                      source="closure-self", side="C"))
    return n, omega_dot, tensor
