"""The empennage planform the spanwise strip integrator runs on (plan 09 T1).

Design note: ``docs/40_history/09_distributed_empennage_loads_plan.md`` decisions
**T-1** (reuse ``SurfaceInput``) and **T-8** (full-span h-tail bookkeeping).
Conventions: ``docs/10_standard/CONVENTIONS.md`` §1 (axes), §7 (single-source
owners).

Two representations of the same surface
---------------------------------------
The empennage has carried its geometry as **scalars** since the suite was ported
-- ``htail_area_sqft``/``htail_semispan_in`` on :class:`TailLoadsInput`,
``vtail_area_sqft``/``vtail_span_in`` on :class:`VTailLoadsInput` -- because that
is all SELECT, TAILDIST and BALLOADS ever needed. A **typed** scalar is
authoritative and this module never overrides it.

A spanwise distribution needs more: a chord at every station. Decision T-1 gets
it by reusing the wing's ``SurfaceInput`` -- an ``"htail"`` / ``"vtail"`` entry in
``geometry.surfaces``, with the same LE/TE polylines, the same user-set
``elements`` station count and the same ``ref_axis_pct`` loads reference axis.
Where such an entry exists it is authoritative **for strips**, and the 1 %
validator below is the drift guard that keeps the two representations describing
one airplane.

The boundary-line model (design note 54 D-54.1, #25 step 2)
-----------------------------------------------------------
Since v65 the polylines are the tail group's **five entered boundary lines** --
tail LE, tail TE, control LE, the control's ``hinge_line``, and the control's
TE, which is the *parent's* along the interior of its span and therefore
derives instead of being entered a second time
(:func:`derived_control_trailing_edge`; an entered copy is held on the
parent's line by :func:`validate_control_trailing_edge`). Every ``[D]``-marked
scalar of the two tail blocks **blank-derives** from them
(:func:`boundary_derived_scalars`, the note 36 OV-1 contract), which is what
turns Appendix A's printed tail figures from transcriptions into ±0.1 %
predictions -- the shipped oracle fixtures keep their typed scalars, so no
delivered number moved when the model landed.

The derived planform, and why it is marked rather than hidden
--------------------------------------------------------------
Where no tail entry exists (a scalars-only project) this module **derives** a
rectangular planform from the authoritative scalars -- constant chord ``S/b``,
leading edge a quarter-chord ahead of the 25 %-MAC station -- which is
precisely the first-order derivation ``configuration.tail_planform`` has
always used for the three-view, and which that function's own docstring is
careful to call "not a structural surface definition".

It is not one here either, and the result says so: every derived planform sets
``assumed=True``, which travels into :class:`TailSpanResult`, the page, the CSV
and the deck ``$`` header. This is the established pattern for a value the tool
had to supply rather than read (``body_loads``' ``spars_assumed``,
``wing_geometry``'s assumed spar fractions) -- a first-order answer, delivered,
and never reported as input.

**What "assumed" costs, quantitatively.** The bending closure integrates the
half-planform area centroid, ``ybar = (b/3)(c_r + 2c_t)/(c_r + c_t)``: ``b/2``
for the rectangle assumed here, falling to ``b/3`` for a fully-tapered surface.
A real tapered tail therefore carries its load further inboard than this
assumption, so a derived planform is **conservative in root bending** -- but the
station-by-station distribution it delivers is not the surface's own. Enter the
polylines when the tail geometry is known.

Half and full, stated once (plan 09 §3.1)
------------------------------------------
``SurfaceInput`` polylines are defined on **one side** of a ``symmetric=True``
surface. The horizontal tail is symmetric, so ``2 x polyline_area`` compares
against ``htail_area_sqft`` and ``polyline_semispan`` against
``htail_semispan_in``. The vertical tail is a single surface: ``polyline_area``
compares against ``vtail_area_sqft`` and ``polyline_span`` against
``vtail_span_in``, with no factor anywhere. Getting this backwards is a factor of
two in every strip, which is why it is written down once, here, and used from
here.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .constants import IN2_PER_FT2
from .derived_geometry import FuselageCentreline, fuselage_centreline, fuselage_height_at, require_integrable_planform
from .models import LayoutInput, Project, SurfaceInput, TailType
from .picks import extreme

#: Component names, which are also the ``geometry.surfaces`` entry names (T-1).
HTAIL = "htail"
VTAIL = "vtail"
TAIL_COMPONENTS = (HTAIL, VTAIL)


class SurfacePlane(Enum):
    """The plane a surface's polylines are defined in (design note 54, D-54.2).

    Every ``SurfaceInput`` polyline point is ``(fuselage station X, span
    coordinate)`` -- and what that second coordinate *is* differs by surface. A
    wing or horizontal tail (and its controls) spans **outboard**, so its span
    coordinate is a butt line; a vertical tail and its rudder span **upward**,
    so theirs is a waterline -- the GA6 fin root is ``(240.912, 117.0)``,
    station 240.912 at *waterline* 117.0. The values are the reader's nouns,
    which is what the report's span-axis labels print.
    """

    BUTT_LINE = "butt line"
    WATERLINE = "waterline"


#: Surface-entry names (prefix match) whose span coordinate is a waterline.
_WATERLINE_SPAN_PREFIXES = ("vtail", "rudder")


def surface_plane(name: str) -> SurfacePlane:
    """The plane the named surface is defined in -- the one authority (#220).

    Before this owner, five call sites decided the question with their own
    name test -- the four local->airplane maps in ``export/coordinates.py``
    and the three-view's mirror/view branch in ``modules/configuration.py`` --
    which is exactly the per-call-site convention drift ``CONVENTIONS.md`` §7
    exists to end. The plane is a property of the surface, stated once, here.

    Two facts the owner carries with it:

    * **The frame decides mirroring, never ``SurfaceInput.symmetric``**:
      ``examples/baron_58.project.json`` sets ``symmetric=True`` on its fin,
      and mirroring a waterline-span surface about ``y = 0`` would draw a
      second fin hanging below the airplane.
    * **No user-selected plane field yet** (D-54.2's own ruling): a declared
      plane input belongs with V-tail/cruciform support, deferred to note 54
      §8. Until then the name prefix is the declaration.
    """
    return (SurfacePlane.WATERLINE
            if name.startswith(_WATERLINE_SPAN_PREFIXES)
            else SurfacePlane.BUTT_LINE)

#: Fractional agreement required between an entered planform and the
#: oracle-authoritative scalars (plan 09 §3.1). Loud, not a silent preference:
#: two representations of one surface that disagree by more than this are a data
#: defect, and every downstream number would be quietly wrong by that much.
PLANFORM_TOLERANCE = 0.01



@dataclass
class TailPlanform:
    """The resolved planform of one empennage surface, in its **local** frame.

    ``span`` runs from the surface root (``0``) outboard; for the horizontal tail
    that is the semispan (the full-span station set is built by mirroring, T-8)
    and for the vertical tail the whole fin. ``le``/``te`` are ``(x, s)`` polyline
    points -- chordwise station against span coordinate -- so a single strip
    integrator serves both surfaces and the local->airplane mapping stays in
    ``export/coordinates.py`` where it has one owner.

    ``area`` is the **whole surface** (both sides for the h-tail), matching every
    other tail quantity in the suite. ``assumed`` records that the planform was
    derived from the scalars rather than entered.
    """

    component: str
    le: List[Tuple[float, float]]
    te: List[Tuple[float, float]]
    span: float                     # semispan (htail) / full fin span (vtail), in
    area: float                     # whole surface, in^2
    elements: int = 10
    ref_axis_pct: float = 0.25
    assumed: bool = False
    root_z: float = 0.0             # v-tail only: waterline of the fin root
    root_z_assumed: bool = False    # v-tail only: was root_z derived? (L-1)
    root_z_basis: str = ""          # v-tail only: which branch supplied it
    notes: List[str] = field(default_factory=list)

    @property
    def symmetric(self) -> bool:
        """True for the h-tail: the local semispan planform mirrors to full span."""
        return self.component == HTAIL

    def chord(self, s: float) -> float:
        """Local chord at span station ``s`` (in).

        Through the one closure owner (``wing_geometry.planform_boundary``): a
        surface whose edges do not cover the same span is bounded by its root and
        tip chords there, not by an extrapolated edge. The GA6 fin's trailing
        edge reaches 5.5 in below its leading edge, and extrapolating instead
        over-read its area by 8 %.
        """
        from .modules.wing_geometry import planform_boundary

        left, right, _lo, _hi, _breaks = planform_boundary(self.le, self.te)
        return right(s) - left(s)

    def x_le(self, s: float) -> float:
        from .modules.wing_geometry import planform_boundary

        left, _right, _lo, _hi, _breaks = planform_boundary(self.le, self.te)
        return left(s)

    def x_at(self, s: float, pct: float) -> float:
        """Chordwise station of ``pct`` of the local chord at span ``s``.

        **The raked-root ruling (design note 54 D-54.3, #219).** Where the two
        edges do not cover the same span -- the GA6 fin's trailing edge starts
        5.5 in below its leading edge, and its leading edge tops out 1.7 in
        above its trailing edge -- the *chord* keeps the closed-polygon clamp
        (:meth:`chord`; the 8 % area over-read justified it), but a
        chord-fraction **line** -- the loads reference axis, the 25/50 % load
        points, the hinge -- is evaluated on the **edges' own slopes**
        (``interp_x`` extrapolates the nearest segment) rather than on the
        closing chord. Re-evaluating the fraction pointwise on the collapsing
        closure chord swung the GA6 fin's LRA onto the trailing-edge root
        point (Figure 24's kink): an artifact of pointwise evaluation, not of
        the surface. Inside the span both edges cover, the two formulations
        are identical, so a square-root fin is byte-unchanged.
        """
        from .modules.wing_geometry import interp_x

        x_le = interp_x(self.le, s)
        return x_le + pct * (interp_x(self.te, s) - x_le)

    def strip_area(self) -> float:
        """The whole-surface area **as the strip quadrature sees it** (in^2):
        ``sum(chord * ds)`` over the ``elements`` mid-strip stations, doubled for
        the symmetric h-tail.

        This -- not :attr:`area` -- is the ``S`` the spanwise distribution
        normalises by, so that ``sum(frac) == 1`` and SELECT's total is conserved
        end-to-end **for every planform**. For the derived rectangle the two are
        the same number; for an entered polyline they differ by up to the
        ``PLANFORM_TOLERANCE`` the validator allows, and normalising by the
        scalar there put that same fraction onto the deck total (backlog Pri 1,
        the first entered tail polylines).
        """
        h = max(2, self.elements)
        ds = self.span / h
        total = 0.0
        for j in range(h):
            total += self.chord(ds / 2.0 + j * ds) * ds
        return 2.0 * total if self.symmetric else total


# --------------------------------------------------------------------------- #
# Validation -- the drift guard between the two representations
# --------------------------------------------------------------------------- #
def _polyline_area_and_span(surf: SurfaceInput) -> Tuple[float, float]:
    """``(area_one_side_in2, span_in)`` of an entered planform.

    **Asked of the one owner**, :func:`sloads.modules.wing_geometry.surface_properties`,
    rather than integrated again here. Until 2026-08-30 this module carried its
    own strip sweep "integrated the same way" -- and when the owner went to
    closed-form integration over the closed planform, the copy did not, so the
    two disagreed by 5.8 % on area and 9.7 % on span for the GA6 fin and
    :func:`validate_tail_planform` refused a planform that was in fact correct.
    A second implementation that has to be kept in step is the defect; there is
    now one (CLAUDE.md rule 3).

    ``span`` is the surface's own, root to tip across **both** edges, so a fin
    whose trailing edge reaches below its leading edge measures the full height.
    ``area`` stays one-sided; the half/full bookkeeping is
    :func:`validate_tail_planform`'s and is applied there and nowhere else.
    """
    from .modules.wing_geometry import surface_properties

    require_integrable_planform(surf)
    values = {v.key: v.value for v in surface_properties(surf).values}
    span = values["span"] / 2.0 if surf.symmetric else values["span"]
    return values["area_per_side"], span


def _polyline_mac_and_x25(surf: SurfaceInput) -> Tuple[float, float]:
    """``(mac_in, x_25_mac_in)`` of an entered planform -- the mean aerodynamic
    chord and the fuselage station of its quarter-chord point.

    From the same owner as :func:`_polyline_area_and_span`, for the same reason.
    ``XLE(MAC)`` is what ``surface_properties`` reports, and the quarter-chord
    point is a quarter of the MAC aft of it.
    """
    from .modules.wing_geometry import surface_properties

    require_integrable_planform(surf)
    values = {v.key: v.value for v in surface_properties(surf).values}
    mac = values["mac"]
    return mac, values["xle_mac_station_of_mac_le"] + 0.25 * mac


def validate_tail_planform(surf: SurfaceInput, component: str,
                           area_sqft: float, span_in: float,
                           x25_in: float = 0.0) -> None:
    """Raise if an entered planform disagrees with the authoritative scalars.

    ``area_sqft``/``span_in`` are the surface's scalar values: ``htail_area_sqft``
    with ``htail_semispan_in``, or ``vtail_area_sqft`` with ``vtail_span_in``.
    The half/full bookkeeping is applied here and nowhere else (§3.1): the h-tail
    doubles its one-sided polyline area and compares span as a **semispan**; the
    v-tail compares both directly.

    ``x25_in`` is the scalar 25 %-MAC fuselage station (``xt25`` / ``xv25``) --
    the point every chordwise pressure and every SELECT tail arm is stated at.
    When given (non-zero) the polyline's own quarter-MAC station must land on
    it within ``PLANFORM_TOLERANCE`` of the MAC (backlog Pri 1, the fixture-data
    pass): a planform whose strips sit fore or aft of the station its loads are
    computed at would put the deck's tail load on a different lever arm from
    the balance's.

    Loud, per T-1: silently preferring one representation would leave the whole
    tail path -- chordwise pressures from the scalars, spanwise strips from the
    polylines -- describing two different airplanes.
    """
    if area_sqft <= 0 or span_in <= 0:
        return
    poly_area, poly_span = _polyline_area_and_span(surf)
    want_area = area_sqft * IN2_PER_FT2
    got_area = 2.0 * poly_area if component == HTAIL else poly_area
    scalar_names = ('htail_area_sqft/htail_semispan_in' if component == HTAIL
                    else 'vtail_area_sqft/vtail_span_in')
    for what, got, want in (("area", got_area, want_area),
                            ("span", poly_span, span_in)):
        if want and abs(got - want) / abs(want) > PLANFORM_TOLERANCE:
            raise ValueError(
                f"{component} planform disagrees with its scalar geometry: "
                f"{what} {got:.1f} from the geometry.surfaces polyline against "
                f"{want:.1f} from {scalar_names}"
                f" ({abs(got - want) / abs(want) * 100:.1f} % apart, limit "
                f"{PLANFORM_TOLERANCE * 100:.0f} %). The scalars are "
                "oracle-authoritative; correct the polyline or the scalar, do not "
                "leave the surface described twice, differently."
            )
    if x25_in:
        mac, got_x25 = _polyline_mac_and_x25(surf)
        if mac > 0 and abs(got_x25 - x25_in) > PLANFORM_TOLERANCE * mac:
            raise ValueError(
                f"{component} planform disagrees with its scalar geometry: the "
                f"polyline's 25 %-MAC station is FS {got_x25:.1f} against "
                f"{'xt25' if component == HTAIL else 'xv25'} = {x25_in:.1f} "
                f"({abs(got_x25 - x25_in):.1f} in apart, limit "
                f"{PLANFORM_TOLERANCE * 100:.0f} % of the {mac:.1f} in MAC). The "
                "scalar station is where the balance states the tail load; move "
                "the polyline (or correct the scalar), do not leave the load on "
                "two lever arms."
            )


# --------------------------------------------------------------------------- #
# The boundary-line model (design note 54 D-54.1, #25 step 2)
# --------------------------------------------------------------------------- #
#: Control surface -> the parent surface whose trailing edge it shares. The
#: physical fact #25 was filed on: a control's trailing edge *is* its parent's
#: trailing edge along the interior of its span, and entering it a second time
#: is how one line gets described twice, differently. With this map the copy
#: either derives (:func:`derived_control_trailing_edge`, a blank control TE)
#: or is validated to lie on the parent
#: (:func:`validate_control_trailing_edge`, an entered one).
CONTROL_PARENT: Dict[str, str] = {
    "elevator": HTAIL,
    "rudder": VTAIL,
    "aileron": "wing",
    "flap": "wing",
}

#: Tail parent -> its control surface, for the tail groups the D-54.1 scalar
#: derivation covers (the wing controls' areas are entered on their own load
#: slices and are not part of the seam).
TAIL_CONTROL: Dict[str, str] = {
    parent: control for control, parent in CONTROL_PARENT.items()
    if parent in TAIL_COMPONENTS
}


def derived_control_trailing_edge(parent: SurfaceInput,
                                  control: SurfaceInput) -> List[Tuple[float, float]]:
    """The control's trailing edge, derived from its parent's (D-54.1).

    The parent's trailing-edge points over the interior of the control's span
    (taken from its own leading-edge polyline's span extremes), with the ends
    resolved by where the control sits against the parent's edge:

    * the control's end lands **inside** the parent TE's span -- an
      interpolated point on the parent TE at that station (the aileron root,
      where the surface starts mid-span);
    * the control's end **coincides** with the parent TE's end -- the parent's
      own vertex, verbatim (the GA6 elevator, whose derived TE is therefore
      byte-identical to the ``htail`` entry's);
    * the control extends **past** the parent TE's span -- the control's own
      leading-edge endpoint closes the boundary (the GA6 rudder, whose tip at
      ``(282.0, 168.0)`` reaches 1.2 in above the fin TE).

    Where the true closure departs from this construction -- the GA6 aileron's
    root closure meets the wing TE at BL 110.401, not at its own root BL 109,
    and clipping to the LE span costs +1.00 % of its area (#25) -- the control
    keeps an **entered** TE, which :func:`validate_control_trailing_edge` then
    holds against the parent instead.
    """
    from .modules.wing_geometry import interp_x

    spans = [p[1] for p in control.leading_edge]
    s_lo, s_hi = min(spans), max(spans)
    te = parent.trailing_edge
    p_lo, p_hi = te[0][1], te[-1][1]
    out: List[Tuple[float, float]] = []
    if s_lo < p_lo:
        out.append(extreme(control.leading_edge, key=lambda p: p[1],
                           largest=False))
    elif s_lo == p_lo:
        out.append((te[0][0], te[0][1]))
    else:
        out.append((interp_x(te, s_lo), s_lo))
    out.extend((p[0], p[1]) for p in te if s_lo < p[1] < s_hi)
    if s_hi > p_hi:
        out.append(extreme(control.leading_edge, key=lambda p: p[1]))
    elif s_hi == p_hi:
        out.append((te[-1][0], te[-1][1]))
    else:
        out.append((interp_x(te, s_hi), s_hi))
    return out


def validate_control_trailing_edge(parent: SurfaceInput,
                                   control: SurfaceInput) -> None:
    """Raise if an entered control TE leaves its parent's trailing edge.

    The #25 "nothing checking the copies agree" guard for the polyline layer,
    the same standing :func:`validate_tail_planform` has for the scalars: a
    control whose entered TE is off the parent's is one physical line described
    twice, differently, and every area split between the two surfaces is
    quietly wrong by the gap. Each entered TE point must lie on the parent's
    trailing edge (within :data:`PLANFORM_TOLERANCE` of the parent's root
    chord) -- except a point that *is* one of the control's own leading-edge
    vertices, which is an end-closure: the control's boundary meeting the
    trailing edge, entered once on the LE and repeated to close the polygon
    (the GA6 aileron root, the GA6 rudder tip).
    """
    if not control.trailing_edge:
        return
    from .modules.wing_geometry import interp_x

    s_root = parent.trailing_edge[0][1]
    root_chord = abs(interp_x(parent.trailing_edge, s_root)
                     - interp_x(parent.leading_edge, s_root))
    tol = PLANFORM_TOLERANCE * max(root_chord, 1.0)
    for x, s in control.trailing_edge:
        if any(abs(x - lx) <= 1e-9 and abs(s - ls) <= 1e-9
               for lx, ls in control.leading_edge):
            continue   # an end-closure vertex shared with the control's own LE
        want = interp_x(parent.trailing_edge, s)
        if abs(x - want) > tol:
            raise ValueError(
                f"{control.name} trailing edge disagrees with its parent "
                f"{parent.name}: the entered TE point ({x:.3f}, {s:.3f}) is "
                f"{abs(x - want):.2f} in off the {parent.name} trailing edge "
                f"({want:.3f} at span {s:.3f}; limit {tol:.2f} in). A "
                "control's trailing edge IS its parent's (design note 54 "
                "D-54.1): correct the point, or leave the control's "
                "trailing_edge empty to derive it.")


def resolved_control_surface(geometry, name: str) -> Optional[SurfaceInput]:
    """The named surface with its trailing edge resolved (D-54.1).

    For a control surface (:data:`CONTROL_PARENT`) whose parent is entered:
    a blank ``trailing_edge`` derives from the parent
    (:func:`derived_control_trailing_edge`); an entered one is validated
    against it (:func:`validate_control_trailing_edge`) and used as given.
    Every other surface -- and a control whose parent is absent -- is returned
    verbatim. This is the read every consumer of a control polyline goes
    through (the WINGGEOM integrator, the report's planform figures), so a
    TE-less control integrates and draws exactly as its parent-derived shape.
    """
    surf = geometry.by_name(name) if geometry is not None else None
    if surf is None:
        return None
    parent_name = CONTROL_PARENT.get(surf.name)
    if parent_name is None:
        return surf
    parent = geometry.by_name(parent_name)
    if (parent is None or len(parent.trailing_edge) < 2
            or len(parent.leading_edge) < 2 or len(surf.leading_edge) < 2):
        return surf
    # The shared mid-entry precondition (#71, PB-21) before any interpolation
    # along the parent's edges: a degenerate parent planform (a repeated span
    # station mid-typing) must come out as the named ValueError refusal, never
    # as interp_x's bare ZeroDivisionError.
    require_integrable_planform(parent)
    if surf.trailing_edge:
        # The copies-agree guard is hard on the **tail groups** -- D-54.1's
        # stated scope. The wing controls carry it too in principle, but three
        # shipped fixtures' estimated aileron polylines sit 0.04-9.4 in off
        # their wing TE (measured 2026-09-10), and reconciling that data moves
        # delivered baselines -- which is the #260/D-54.6 fixture wave's
        # deliberate work, not this step's. The hard guard extends to
        # aileron/flap when that wave enters their geometry.
        if parent_name in TAIL_COMPONENTS:
            validate_control_trailing_edge(parent, surf)
        return surf
    return replace(surf, trailing_edge=derived_control_trailing_edge(parent, surf))


def resolved_surfaces(geometry) -> List[SurfaceInput]:
    """Every entered surface with control trailing edges resolved (D-54.1)."""
    if geometry is None:
        return []
    return [resolved_control_surface(geometry, s.name) or s
            for s in geometry.surfaces]


def control_hinge_areas(control: SurfaceInput) -> Optional[Tuple[float, float]]:
    """``(fwd_in2, aft_in2)`` one-sided areas split at the entered hinge line.

    The hinge line (``SurfaceInput.hinge_line``, the aerodynamic hinge axis as
    an ``(X, span)`` polyline) divides the control into the area forward of
    the hinge (the balance/horn, SELECT's ``SEFWDHL``/``SRFWDHL``) and aft of
    it (``SEAFTHL``/``SRAFTHL``). Both halves are integrated by the one
    planform owner (``wing_geometry.surface_properties``) over constructed
    LE/hinge and hinge/TE surfaces, so the split and the whole cannot drift
    apart. ``None`` when no hinge line (or no resolvable planform) is entered.

    Refused loudly when the hinge line does not span the control (the clamp
    would silently invent closure chords) or leaves the chord at any strip
    station (a hinge forward of the LE or aft of the TE is not a split, it is
    a different surface).
    """
    if (len(control.hinge_line) < 2 or len(control.leading_edge) < 2
            or len(control.trailing_edge) < 2):
        return None
    # The shared mid-entry precondition (#71) before the interp sweep below.
    require_integrable_planform(control)
    from .modules.wing_geometry import interp_x, surface_properties

    spans = ([p[1] for p in control.leading_edge]
             + [p[1] for p in control.trailing_edge])
    s_lo, s_hi = min(spans), max(spans)
    span = s_hi - s_lo
    h_spans = [p[1] for p in control.hinge_line]
    if (min(h_spans) > s_lo + PLANFORM_TOLERANCE * span
            or max(h_spans) < s_hi - PLANFORM_TOLERANCE * span):
        raise ValueError(
            f"{control.name} hinge_line spans {min(h_spans):.1f}.."
            f"{max(h_spans):.1f} in against the control's {s_lo:.1f}.."
            f"{s_hi:.1f} in -- the hinge line must cover the control's span "
            f"(within {PLANFORM_TOLERANCE * 100:.0f} %), or the area split "
            "would be closed by invented chords.")
    h = max(2, control.elements)
    for j in range(h):
        s = s_lo + (j + 0.5) * span / h
        x_le = interp_x(control.leading_edge, s)
        x_te = interp_x(control.trailing_edge, s)
        x_h = interp_x(control.hinge_line, s)
        tol = PLANFORM_TOLERANCE * max(abs(x_te - x_le), 1.0)
        if not (min(x_le, x_te) - tol <= x_h <= max(x_le, x_te) + tol):
            raise ValueError(
                f"{control.name} hinge_line leaves the control chord at span "
                f"{s:.1f} in: hinge {x_h:.2f} against LE {x_le:.2f} / TE "
                f"{x_te:.2f}. The hinge line splits the control's own area; "
                "correct the polyline that puts it outside the surface.")
    fwd = replace(control, trailing_edge=[(p[0], p[1]) for p in control.hinge_line])
    aft = replace(control, leading_edge=[(p[0], p[1]) for p in control.hinge_line])

    def _area(s_: SurfaceInput) -> float:
        return float(next(v.value for v in surface_properties(s_).values
                          if v.key == "area_per_side"))

    return _area(fwd), _area(aft)


def boundary_derived_scalars(project: Project, component: str) -> Dict[str, float]:
    """The boundary-line model's values for the marked scalars (D-54.1).

    ``{field name: derived value}`` for the :data:`~sloads.models.inputs
    .HTAIL_BOUNDARY_DERIVED` / ``VTAIL_BOUNDARY_DERIVED`` fields of one tail
    group that the entered boundary lines can supply: the parent surface's
    area/span/AR/MAC and 25/50 %-MAC stations from the WINGGEOM strip
    integrator, the control's area from its resolved planform (its TE derived
    from the parent where not entered), and the hinge-split areas where a
    ``hinge_line`` is entered. Fields whose lines are absent are simply not in
    the dict -- the consumer (``select.effective_tail_inputs`` /
    ``effective_vtail_inputs``, and :func:`resolve_tail_planform`'s scalar
    read) takes them only for a **blank** entered scalar, the note 36 OV-1
    contract: typed overrides, blank derives. The two wing-sourced fields of
    the maps (``aspect_ratio_wing``, ``wing_span_in``) are not produced here;
    their owners (``derived_geometry.wing_aspect_ratio`` / ``wing_span_in``)
    predate this model and are consumed in the same functions.

    The half/full bookkeeping is §3.1's, stated once there and applied the
    same way here: h-tail group areas are **both sides** (the surface is
    symmetric; ``htail_semispan_in`` is the semispan), v-tail group areas are
    the single fin's.
    """
    geometry = project.geometry
    if geometry is None or component not in TAIL_COMPONENTS:
        return {}
    from .modules.wing_geometry import surface_properties

    out: Dict[str, float] = {}
    surf = geometry.by_name(component)
    if surf is not None and len(surf.leading_edge) >= 2 and len(surf.trailing_edge) >= 2:
        try:
            vals = {v.key: v.value for v in surface_properties(surf).values}
        except (ValueError, ZeroDivisionError):
            vals = {}
        if vals:
            aps, span, mac = vals["area_per_side"], vals["span"], vals["mac"]
            x25 = vals["xle_mac_station_of_mac_le"] + 0.25 * mac
            x50 = vals["xle_mac_station_of_mac_le"] + 0.50 * mac
            if component == HTAIL:
                out.update({
                    "htail_area_sqft": 2.0 * aps / IN2_PER_FT2,
                    "htail_semispan_in": span / 2.0,
                    "aspect_ratio_htail": vals["aspect_ratio"],
                    "xt25": x25,
                    "xt50": x50,
                })
            else:
                out.update({
                    "vtail_area_sqft": aps / IN2_PER_FT2,
                    "vtail_span_in": span,
                    "vtail_mac_in": mac,
                    "aspect_ratio_vtail": vals["aspect_ratio"],
                    "xv25": x25,
                    "xv50": x50,
                })
    control = resolved_control_surface(geometry, TAIL_CONTROL[component])
    if (control is not None and len(control.leading_edge) >= 2
            and len(control.trailing_edge) >= 2):
        try:
            c_aps = float(next(v.value for v in surface_properties(control).values
                               if v.key == "area_per_side"))
        except (ValueError, ZeroDivisionError, StopIteration):
            c_aps = 0.0
        both = 2.0 if component == HTAIL else 1.0
        if c_aps > 0.0:
            key = "elevator_area_sqft" if component == HTAIL else "rudder_area_sqft"
            out[key] = both * c_aps / IN2_PER_FT2
        halves = control_hinge_areas(control)
        if halves is not None:
            fwd, aft = halves
            if component == HTAIL:
                out["elevator_fwd_hinge_sqft"] = both * fwd / IN2_PER_FT2
                out["elevator_aft_hinge_sqft"] = both * aft / IN2_PER_FT2
            else:
                out["rudder_fwd_hinge_sqft"] = fwd / IN2_PER_FT2
                out["rudder_aft_hinge_sqft"] = aft / IN2_PER_FT2
    return out


# --------------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------------- #
def _scalars(project: Project, component: str) -> Optional[Tuple[float, float, float]]:
    """``(area_sqft, span_in, x25)`` -- **entered** scalars only, ``0.0`` blank.

    ``span_in`` is the **semispan** for the h-tail and the full span for the
    v-tail, i.e. exactly the local span each planform is defined over.
    ``None`` when the slice itself is absent. The blank-derives leg (D-54.1)
    is :func:`resolve_tail_planform`'s, so this stays the honest record of
    what was typed -- which is also what :func:`validate_tail_planform` must
    compare against (a derived scalar validated against the polyline it was
    derived from proves nothing).
    """
    if component == HTAIL:
        ti = project.tail_loads
        if ti is None:
            return None
        return ti.htail_area_sqft, ti.htail_semispan_in, ti.xt25
    vt = project.vtail_loads
    if vt is None:
        return None
    return vt.vtail_area_sqft, vt.vtail_span_in, vt.xv25


@dataclass(frozen=True)
class VtailRoot:
    """Where the vertical tail's root sits, and on whose authority.

    ``assumed`` is False only for an entered value; ``basis`` names the branch of
    :func:`vtail_root_waterline` that produced it, and ``note`` is the in-band
    sentence a derived value owes its consumer.
    """

    z: float
    assumed: bool
    basis: str
    note: str = ""


def vtail_root_waterline(layout: Optional["LayoutInput"], vtail_span_in: float = 0.0,
                       explicit: float = 0.0,
                       centreline: Optional[FuselageCentreline] = None,
                       outline=None, x_vtail: float = 0.0,
                       entered_geometry: float = 0.0) -> VtailRoot:
    """Waterline of the vertical-tail root (in) -- **the single owner** (L-1).

    Design note: ``docs/40_history/18_b8a_lateral_closure_plan.md`` §5.1, decision
    L-1. Read by :func:`resolve_tail_planform` for the load path and by
    ``configuration.tail_planform`` for the three-view, so the sketch and the deck
    cannot put the same fin in two places (``CONVENTIONS.md`` §7 rule 2).

    **Why this is worth an owner at all.** The fin's height above the CG is the
    lever arm of the roll moment a side load makes, and that is a first-order
    design load in every lateral case. Before this existed the load path used
    ``0`` -- placing ``ga6_normal``'s fin *64.5 in below* its own CG and reversing
    the sign of that moment.

    Resolution order::

        entered vtail polyline   -> its own root waterline             (assumed False)
        explicit input           -> use it                            (assumed False)
        T-tail with h_tail_z set -> root_waterline_z + h_tail_z - span (assumed True)
        fuselage outline present -> z_centre(x_vtail) + height(x_vtail)/2
        otherwise                -> root_waterline_z + fuselage_height/2
        no layout / no data      -> 0.0, with a loud note

    **The polyline leads (2026-09-06).** ``entered_geometry`` is the lowest point
    of either edge of the ``vtail`` entry in ``geometry.surfaces`` -- the airplane's
    own statement of where its vertical tail is, in the waterline datum the rest of
    the geometry is entered in. Every other branch *reconstructs* that placement
    from something else (a scalar typed on another page, the T-tail relation, the
    body's top at the fin station), so where the surface itself states it, asking
    anything else is asking a second opinion of a fact already on file. It ranks
    above ``explicit`` because the two are not blank-derives-typed-overrides
    (note 36 OV-1) alternatives: they are two spellings of one measurement, and
    a disagreement between them is refused below rather than resolved by
    precedence.

    ``0.0`` reads as *not stated*, the same convention ``explicit`` carries
    (``DATA_DICTIONARY``: ``0 -> derived, marked assumed``), so a fin entered
    root-relative still falls through to the branches that place it.

    **Two spellings, one fin.** When the polyline and ``explicit`` are both stated
    and disagree by more than ``PLANFORM_TOLERANCE`` of the fin span, the polyline
    is used and the returned ``note`` says so *and* names the value it did not
    use. :func:`validate_tail_planform` raises on the same duplication class one
    level down, and the difference is deliberate: area against span is an
    unresolvable conflict -- two representations of one surface with no rule to
    pick between them -- while this one has a stated precedence, so the honest
    outcome is a resolution stated in band rather than a refusal. Raising here
    would also make ``vtail_root_waterline_z`` un-typable on any project with an
    entered fin, which is a shipped input field.

    The defect it was written against is on the record: ``ga6_normal`` carried an
    ``explicit`` 78.5 -- its *wing* root waterline, pinned as attribution
    scaffolding by note 19 §10.2 step (i) on 2026-08-17 and never removed --
    against a polyline stating 111.5, and being first in the order it shadowed
    both the polyline and the body outline that the same pass entered to
    supersede it. Nothing said so for 20 days.

    The T-tail branch is the **inverse of the three-view's own default**, which
    places a T-tail's horizontal surface at ``fuselage_height/2 + v_span`` above
    the wing root waterline -- i.e. at the fin tip. Where ``h_tail_z`` is entered
    instead of defaulted, solving that relation for the root is what keeps the fin
    tip and the horizontal tail in contact; the fuselage-top formula does not
    (on ``concept_regional_jet`` it leaves them 18 in apart).

    The outline branch is the fuselage-top formula with a real body datum
    (backlog Pri 1, from T-8a): the section-centre line
    (:func:`~sloads.derived_geometry.fuselage_centreline`, note 24 R-4) plus half
    the **local** body height at the fin station, both evaluated at ``x_vtail``
    (the fin's 25 %-MAC station ``xv25``). It fires only when the local height is
    non-zero -- a pointed tail cone at ``x_vtail`` states no top to sit on.

    The layout fallback is the branch the outline datum replaces, retained for a
    project with no fuselage outline: ``fuselage_height / 2`` above
    ``root_waterline_z``, which reads the **wing** root as the body centreline --
    the substitution ``CONVENTIONS.md``'s body-drag row refuses for D-1, and on a
    high-wing airplane it stacks half a body above the real top. Its note says
    so.
    """
    if entered_geometry:
        note = ""
        limit = PLANFORM_TOLERANCE * vtail_span_in if vtail_span_in > 0 else 0.0
        if explicit and limit and abs(entered_geometry - explicit) > limit:
            note = (
                f"vtail root waterline {entered_geometry:.1f} in from the "
                f"geometry.surfaces 'vtail' polyline; the entered "
                f"vtail_root_waterline_z of {explicit:.1f} in disagrees by "
                f"{abs(entered_geometry - explicit):.1f} in and is NOT USED. "
                "The fin's height above the CG is the roll arm of every side "
                "load it carries, so the surface is placed twice, differently: "
                "correct the polyline or clear the scalar.")
        return VtailRoot(entered_geometry, False, "geometry", note)
    if explicit:
        return VtailRoot(explicit, False, "entered")
    if layout is None:
        return VtailRoot(0.0, True, "none", _VTAIL_ROOT_UNKNOWN)
    if (layout.tail_type == TailType.T_TAIL and layout.h_tail_z
            and vtail_span_in > 0):
        z = layout.root_waterline_z + layout.h_tail_z - vtail_span_in
        return VtailRoot(z, True, "t-tail", (
            f"vtail root waterline {z:.1f} in ASSUMED from the T-tail relation "
            f"(root_waterline_z {layout.root_waterline_z:.1f} + h_tail_z "
            f"{layout.h_tail_z:.1f} - fin span {vtail_span_in:.1f}), which puts "
            "the fin tip at the horizontal tail. Enter "
            "vtail_root_waterline_z to state it."))
    if centreline is not None:
        height = fuselage_height_at(outline, x_vtail)
        if height:
            z_c = centreline.z_at(x_vtail)
            z = z_c + height / 2.0
            note = (
                f"vtail root waterline {z:.1f} in ASSUMED as the local fuselage "
                f"top (z_centre {z_c:.1f} + height {height:.1f} / 2 at FS "
                f"{x_vtail:.1f}). Enter vtail_root_waterline_z to state it.")
            if centreline.assumed and centreline.note:
                note += " " + centreline.note
            return VtailRoot(z, True, "fuselage-top", note)
    if layout.root_waterline_z or layout.fuselage_height:
        z = layout.root_waterline_z + layout.fuselage_height / 2.0
        return VtailRoot(z, True, "fuselage-top", (
            f"vtail root waterline {z:.1f} in ASSUMED as the fuselage top "
            f"(root_waterline_z {layout.root_waterline_z:.1f} + fuselage_height "
            f"{layout.fuselage_height:.1f} / 2) -- with no fuselage outline the "
            "WING root stands in for the body centreline. Enter "
            "vtail_root_waterline_z or a fuselage outline to state it."))
    return VtailRoot(0.0, True, "none", _VTAIL_ROOT_UNKNOWN)


#: What a fin with no vertical placement at all owes its consumer. Loud, because
#: the consequence is not a small error: the roll moment of a fin side load about
#: the CG takes the *wrong sign* when the fin is modelled below it.
_VTAIL_ROOT_UNKNOWN = (
    "vtail root waterline is 0 -- no parametric fuselage and no "
    "vtail_root_waterline_z, so the fin is placed on the airplane centreline. "
    "Its roll arm about the CG is therefore wrong, and may be wrong in sign.")


def entered_vtail_root(project: Project) -> float:
    """The fin root waterline the ``vtail`` polyline states, or ``0.0``.

    The root is the lowest point of **either** edge, the same rule
    :func:`resolve_tail_planform` measures the fin's span with (owner,
    2026-08-30): a fin whose trailing edge reaches below its leading edge -- a
    dorsal fillet -- has its root at the fillet. ``ga6_normal`` is exactly that
    shape, LE root 117.0 against TE root 111.5, so its stated root is 111.5.
    """
    geometry = project.geometry
    surf = geometry.by_name(VTAIL) if geometry is not None else None
    if surf is None or not surf.leading_edge or not surf.trailing_edge:
        return 0.0
    return min(surf.leading_edge[0][1], surf.trailing_edge[0][1])


def vtail_root(project: Project) -> VtailRoot:
    """The fin root for this project, from the single owner above.

    The project-level entry point: resolves the outline datum (the section-centre
    line and the fin station ``xv25``) once, so :func:`resolve_tail_planform` and
    ``configuration.tail_planform`` cannot feed the owner different bodies.
    """
    geometry = project.geometry
    vt = project.vtail_loads
    return vtail_root_waterline(
        geometry.parametric if geometry is not None else None,
        vt.vtail_span_in if vt is not None else 0.0,
        vt.vtail_root_waterline_z if vt is not None else 0.0,
        centreline=fuselage_centreline(project),
        outline=geometry.fuselage if geometry is not None else None,
        x_vtail=vt.xv25 if vt is not None else 0.0,
        entered_geometry=entered_vtail_root(project))


@dataclass(frozen=True)
class HTailWaterline:
    """Where the horizontal tail sits, and on whose authority.

    Same contract as :class:`VtailRoot`: ``assumed`` is False only for an entered
    value, ``basis`` names the branch of :func:`h_tail_waterline` that produced
    it, and ``note`` is the in-band sentence a derived value owes its consumer.
    """

    z: float
    assumed: bool
    basis: str
    note: str = ""


def h_tail_waterline(project: Project,
                     vtail: Optional[TailPlanform] = None) -> HTailWaterline:
    """Waterline of the horizontal tail (in) -- **the single owner** (#236).

    Read by ``tail_span._h_tail_waterline`` for the load stations (so the report's
    station tables, Appendix D and the exported ``GRID``s all carry it) and echoed
    by the report's provenance sentences, so the document cannot state a
    provenance the resolution did not have. The three-view
    (``configuration.tail_planform``) resolves the same entered branch from the
    same fields, drift-guarded in ``tests/test_tail_geometry.py``.

    The h-tail loads in ``fz`` only, so this coordinate enters no delivered load
    -- it places stations and ``GRID``s, not forces (``z`` pairs with ``Fx`` in
    ``Myy`` and with ``Fy`` in ``Mxx``, and the surface carries neither). That is
    why the wing-root placeholder survived here for so long, and why the 2026-09-08
    review (R12) filed it anyway: the document printed the placeholder as an
    airplane coordinate, and an analyst importing Appendix D's points placed the
    GA-6's tail 32.5 in low.

    Resolution order (design note 54, D-54.4 completed the conventional leg)::

        T-tail with a resolved fin -> fin root + fin span (the fin tip);
                                      an entered h_tail_z that contradicts it
                                      is named NOT USED (the two-spellings rule)
        cruciform, h_tail_z blank  -> fin root + fin span / 2 (assumed True)
        h_tail_z entered           -> root_waterline_z + h_tail_z (assumed False)
        htail mass item(s) entered -> their weight-weighted z (assumed True,
                                      basis "mass-item")
        otherwise                  -> root_waterline_z, with a loud note
        no layout                  -> 0.0, same note

    The cruciform branch mirrors the three-view's own mid-fin default so the
    sketch and the deck place one surface once (``CONVENTIONS.md`` §7 rule 2) --
    before this owner the deck used the wing root there, 32+ in below the drawn
    surface on any real cruciform.

    **The two-spellings rule** (D-54.4, the #260 E5 pattern made loud): on a
    declared T-tail the surface sits on the fin, so the relation *is* the
    waterline -- but a project may also carry an entered ``h_tail_z`` spelling
    the same fact a second way. Where the entered spelling disagrees with the
    fin tip by more than :data:`PLANFORM_TOLERANCE` of the fin span, the fin
    tip wins **and the note names the entered value as NOT USED**, exactly as
    the fin-root owner treats its own two spellings. Silent precedence is what
    let ``atr42_100`` declare ``t_tail`` with ``h_tail_z = 0.0`` and be right
    only by branch order.

    **The mass-item branch** (D-54.4, decided 2026-09-09): before falling back
    to the wing-root plane, a conventional tail with no entered ``h_tail_z``
    takes the h-tail mass items' weight-weighted ``z`` -- an entered statement
    of where the surface's mass sits, which is a far better placement than the
    wing root (``cessna_210``'s item puts the surface at 100.0 in where the
    wing-root plane sat 14 in low at 86.0). ASSUMED, because a mass station is
    not a surface definition; the note says which item(s) spoke.
    """
    if vtail is None:
        vtail = resolve_tail_planform(project, VTAIL)
    geometry = project.geometry
    layout = geometry.parametric if geometry is not None else None
    if (layout is not None and vtail is not None and vtail.span > 0
            and layout.tail_type == TailType.T_TAIL):
        z = vtail.root_z + vtail.span
        note = (f"h-tail waterline {z:.1f} in is the fin tip the horizontal "
                "surface sits on (fin root + fin span, from the fin-root owner).")
        if layout.h_tail_z:
            entered = layout.root_waterline_z + layout.h_tail_z
            if abs(entered - z) > PLANFORM_TOLERANCE * vtail.span:
                note += (f" The entered h_tail_z implies waterline "
                         f"{entered:.1f} in and is NOT USED: a declared T-tail "
                         "sits on its fin, and the two spellings disagree by "
                         f"{abs(entered - z):.1f} in. Clear h_tail_z, or fix "
                         "the fin geometry it contradicts.")
        return HTailWaterline(z, vtail.root_z_assumed, "fin-tip", note)
    if (layout is not None and vtail is not None and vtail.span > 0
            and layout.tail_type == TailType.CRUCIFORM
            and not layout.h_tail_z):
        z = vtail.root_z + vtail.span / 2.0
        return HTailWaterline(z, True, "mid-fin", (
            f"h-tail waterline {z:.1f} in ASSUMED as the mid-fin point the "
            "three-view draws a defaulted cruciform at. Enter h_tail_z to "
            "state it."))
    if layout is not None and layout.h_tail_z:
        return HTailWaterline(
            layout.root_waterline_z + layout.h_tail_z, False, "entered")
    from .mass_distribution import distribution
    from .models import MassComponent

    dist = distribution(project)
    weight = dist.weight(MassComponent.HTAIL)
    if weight > 0.0:
        z = dist.cg("z", MassComponent.HTAIL)
        names = ", ".join(it.name for it in
                          dist.by_component.get(MassComponent.HTAIL, []))
        return HTailWaterline(z, True, "mass-item", (
            f"h-tail waterline {z:.1f} in ASSUMED as the h-tail mass items' "
            f"weight-weighted z ({names}) -- h_tail_z is not entered, and a "
            "mass station is not a surface definition. Enter h_tail_z to "
            "state it."))
    z = layout.root_waterline_z if layout is not None else 0.0
    return HTailWaterline(z, True, "wing-root", (
        f"h-tail waterline {z:.1f} in ASSUMED as the wing-root reference plane "
        "-- h_tail_z is not entered, so this is not the surface's true "
        "waterline. No delivered load depends on it (the h-tail loads in fz "
        "only); it places the load stations and the exported GRIDs. Enter "
        "h_tail_z to state it."))


def resolve_tail_planform(project: Project,
                          component: str) -> Optional[TailPlanform]:
    """The planform to run strips on, or ``None`` when the surface is not modelled.

    Entered polylines win and are validated; otherwise a rectangular planform is
    derived from the scalars and marked ``assumed``. See the module docstring for
    why the derivation exists and what it costs.

    **Blank scalars derive from the boundary lines** (D-54.1, #25 step 2): a
    surface whose area/span scalars are not typed but whose polylines are
    entered is modelled from :func:`boundary_derived_scalars` rather than
    refused -- the note 36 OV-1 contract, typed overrides and blank derives.
    The validator compares the polylines against the **entered** scalars only,
    so it retires field-by-field exactly as the scalars stop being typed.
    """
    if component not in TAIL_COMPONENTS:
        raise ValueError(f"unknown tail component {component!r}; expected one of "
                         f"{TAIL_COMPONENTS}")
    scalars = _scalars(project, component)
    if scalars is None:
        return None
    entered_area, entered_span, entered_x25 = scalars
    area_sqft, span_in, x25 = entered_area, entered_span, entered_x25
    if area_sqft <= 0 or span_in <= 0 or not x25:
        derived = boundary_derived_scalars(project, component)
        keys = (("htail_area_sqft", "htail_semispan_in", "xt25")
                if component == HTAIL else
                ("vtail_area_sqft", "vtail_span_in", "xv25"))
        area_sqft = area_sqft or derived.get(keys[0], 0.0)
        span_in = span_in or derived.get(keys[1], 0.0)
        x25 = x25 or derived.get(keys[2], 0.0)
    if area_sqft <= 0 or span_in <= 0:
        return None
    area_in2 = area_sqft * IN2_PER_FT2
    geometry = project.geometry
    surf = geometry.by_name(component) if geometry is not None else None
    # The fin root is a property of the *surface's placement*, not of how its
    # planform was obtained, so it is resolved once here and applies equally to an
    # entered polyline and a derived rectangle (L-1).
    root = vtail_root(project) if component == VTAIL else VtailRoot(0.0, False, "n/a")
    root_notes = [root.note] if root.note else []

    if surf is not None:
        validate_tail_planform(surf, component, entered_area, entered_span,
                               entered_x25)
        # The root is the lowest point of **either** edge and the tip the
        # highest, so a fin whose trailing edge reaches below its leading edge
        # measures its full height (owner, 2026-08-30). Every surface entered
        # before the GA6 empennage has matching edge ranges, for which this is
        # the value it always had.
        s_root = min(surf.leading_edge[0][1], surf.trailing_edge[0][1])
        s_tip = max(surf.leading_edge[-1][1], surf.trailing_edge[-1][1])
        return TailPlanform(
            component=component,
            le=[(x, s - s_root) for x, s in surf.leading_edge],
            te=[(x, s - s_root) for x, s in surf.trailing_edge],
            span=s_tip - s_root,
            area=area_in2,
            elements=surf.elements,
            ref_axis_pct=surf.ref_axis,
            assumed=False,
            root_z=root.z,
            root_z_assumed=root.assumed,
            root_z_basis=root.basis,
            notes=root_notes,
        )

    # Derived: constant chord = S/b, LE a quarter chord ahead of the 25 % MAC
    # station. For the h-tail the local span is the semispan and the area is
    # both-sides, so the chord is S/(2*semispan) -- the full-span average chord,
    # which is exactly TAILDIST's CAVE.
    full_span = 2.0 * span_in if component == HTAIL else span_in
    chord = area_in2 / full_span
    x_le = x25 - 0.25 * chord
    notes = [
        f"{component} planform DERIVED as a rectangle (chord {chord:.2f} in) from "
        f"the area/span scalars -- no '{component}' entry in geometry.surfaces. "
        "First-order: a tapered surface carries its load further inboard, so root "
        "bending here is conservative but the station distribution is not the "
        "surface's own."
    ]
    notes += root_notes
    return TailPlanform(
        component=component,
        le=[(x_le, 0.0), (x_le, span_in)],
        te=[(x_le + chord, 0.0), (x_le + chord, span_in)],
        span=span_in,
        area=area_in2,
        elements=_derived_elements(project),
        ref_axis_pct=_derived_ref_axis(project),
        assumed=True,
        root_z=root.z,
        root_z_assumed=root.assumed,
        root_z_basis=root.basis,
        notes=notes,
    )


def _derived_elements(project: Project) -> int:
    """Station count for a derived planform: the wing's, so one project reports
    every surface at a comparable resolution, floored at the T-6 minimum of 2."""
    geometry = project.geometry
    wing = geometry.by_name("wing") if geometry is not None else None
    return max(2, wing.elements // 2 if wing is not None else 10)


def _derived_ref_axis(project: Project) -> float:
    """LRA fraction for a derived planform: the wing's, so a project that has
    stated its beam axis once does not have to state it again per surface."""
    geometry = project.geometry
    wing = geometry.by_name("wing") if geometry is not None else None
    return wing.ref_axis if wing is not None else 0.25


def half_area_centroid(planform: TailPlanform) -> float:
    """Span centroid ``ybar`` of one half-planform (in) -- the bending target.

    Closed-form for a straight-tapered surface,
    ``ybar = (b/3)(c_r + 2c_t)/(c_r + c_t)``, and this integration reproduces it;
    the test states the analytic value and this function is what the module
    integrates, so the two are independent producers of the same number.
    """
    h = max(1, planform.elements)
    ds = planform.span / h
    area = moment = 0.0
    for el in range(h):
        s = ds / 2 + el * ds
        da = planform.chord(s) * ds
        area += da
        moment += da * s
    return moment / area if area else 0.0


def is_t_tail(project: Project) -> bool:
    """True when the layout says the h-tail sits on the fin (plan 09 T7's gate)."""
    geometry = project.geometry
    layout = geometry.parametric if geometry is not None else None
    return layout is not None and layout.tail_type == TailType.T_TAIL


def tail_layout(project: Project) -> Optional[TailType]:
    """The empennage arrangement this project declares, or ``None``.

    ``None`` is *undeclared*, not conventional. The difference is the whole of
    :func:`is_conventional_tail`'s docstring, and keeping the two apart here is
    what lets a consumer decide which way to read a silence instead of
    inheriting a decision this function made for it.
    """
    geometry = project.geometry
    layout = geometry.parametric if geometry is not None else None
    return layout.tail_type if layout is not None else None


def is_conventional_tail(project: Project) -> bool:
    """True when the empennage is the arrangement this analysis models (OR-134).

    A conventional tail is a horizontal and a vertical surface each carried by
    the fuselage and each loaded independently. **Every other value is not** --
    ``T_TAIL``, ``V_TAIL`` and ``CRUCIFORM`` alike (note 44 OR-134): a cruciform
    fin carries the same horizontal-tail reaction a T-tail's does, and a V-tail
    has no separable vertical surface for the analysis to be about. The report
    withholds the vertical tail's spanwise loads on any of them (OR-133).

    An **undeclared** layout reads as conventional, because that is the
    arrangement every other default in this package already assumes -- the
    planform resolver, the beam model and the balanced deck all place two
    fuselage-carried surfaces -- and a project that declares nothing gets the
    analysis it is actually being given. It is not a silent assumption: the
    layout is a Section 2 input and the document echoes it.
    """
    layout = tail_layout(project)
    return layout is None or layout == TailType.CONVENTIONAL


__all__ = [
    "CONTROL_PARENT",
    "HTAIL",
    "PLANFORM_TOLERANCE",
    "TAIL_COMPONENTS",
    "TAIL_CONTROL",
    "VTAIL",
    "HTailWaterline",
    "SurfacePlane",
    "TailPlanform",
    "VtailRoot",
    "boundary_derived_scalars",
    "control_hinge_areas",
    "derived_control_trailing_edge",
    "h_tail_waterline",
    "half_area_centroid",
    "is_conventional_tail",
    "is_t_tail",
    "resolve_tail_planform",
    "resolved_control_surface",
    "resolved_surfaces",
    "surface_plane",
    "tail_layout",
    "validate_control_trailing_edge",
    "validate_tail_planform",
    "vtail_root",
    "vtail_root_waterline",
]
