"""Wing slot x FLIGHT mass-state variants -- design note 63, D-63.7.

Each SELECT wing slot (``case_ids.WING_SLOTS``, note 62) is assessed at
**every** FLIGHT weight/CG case: for slot *s* and case *k* the air load is
that family's own winning V-n point among the points balanced at *k*
(SELECT's per-family criterion applied within *k*), and the inertia is *k*'s
loading (:func:`sloads.mass_distribution.wing_mass_state`). Every variant is
an existing V-n point -- a **run** with its own identity (D-63.11) -- so no
point is re-balanced here; the matrix already holds each manoeuvre at each
CG case.

The governing variant of a slot is the one with the extreme **signed** root
``Mxx`` at the loads reference axis -- largest for the positive-lift slots,
most negative for the negative ones (``select.SLOT_LIFT_SIGN``); root bending
is a signed moment, not a resultant. SELECT re-points the slot's delivered
condition to that run (:func:`sloads.modules.select.select_wing`); the air
pick stays a queryable intermediate (:func:`sloads.modules.select.air_picks`)
and an assessed row here without a W id. Root ``Mxx`` is unchanged by the
25 %-chord to LRA transfer (``net_loads.to_loads_ref_axis`` moves torsion and
station only), so the comparison reads the computed root value directly.

Pure calc, no I/O, no registration: the table is an intermediate SELECT and
the report read (``oracle_sections`` §3.2), never a persisted result -- the
v67 schema carries the run key on every ``CaseRef`` and nothing else of this.
A project that cannot run the wing analysis at all (no ``wing_mass``, no
wing geometry or aero surface) has an empty table with the reason stated,
and SELECT then delivers its air picks unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from ..aero_curves import inertia_drag_factor
from ..cg_cases import flight_cases
from ..derived_geometry import require_integrable_planform, sync_geometry_derived, wing_plane
from ..mass_distribution import panel_weight, wing_mass_state
from ..models import (
    CriticalCondition,
    EnvelopeResult,
    MissingInputError,
    Project,
    VnPoint,
    WingLoadCase,
)
from ..picks import TIE_REL, extreme
from .airloads import air_load_distribution
from .wing_inertia import fold_units, panel_shape, wing_inertia_distribution

#: Two variants whose signed root ``Mxx`` agree to this are a tie and the air
#: pick keeps the slot. It is the FLTLOADS balance's own resolution: the
#: angle-of-attack iteration converges ``NZ`` to +-0.005 (``flight_envelope``),
#: so every point's CL -- and the root bending built from it -- carries ~0.5 %
#: of noise, and a smaller difference between two runs is not a finding
#: (``tests/test_select.py`` holds the Appendix A CLs to the same band).
#: ``picks.TIE_REL`` (1e-9) is the platform-stability tie, a different thing.
GOVERNING_TIE_REL = 5e-3

__all__ = ["GOVERNING_TIE_REL", "WingVariant", "WingVariantTable", "governing_points",
           "wing_variant_table"]


@dataclass(frozen=True)
class WingVariant:
    """One slot assessed at one FLIGHT case: the run and its net root bending."""
    slot: str                 # "PHAA" ... the note 62 slot the row is assessed for
    far_reference: str
    cg: str                   # the FLIGHT case: the point's CG case and the mass state
    case: int                 # V-n case number of the family's pick within ``cg``
    run: str                  # manoeuvre label (D-63.11)
    config: str
    altitude_ft: float
    v_eas_kt: float
    cl: float
    nz: float                 # WINGINER's sign: the negated flight load factor
    nx: float
    weight_lb: float
    air_root_mxx: float       # lb-in, 25 % chord == LRA for Mxx
    inertia_root_mxx: float
    root_mxx: float           # air + inertia, signed
    mass_state: str           # ``WingMassState.label``
    mass_state_case: str      # ``WingMassState.case`` ("" = database fallback)
    air_pick: bool = False    # SELECT's per-family air pick over the whole matrix
    governing: bool = False   # the variant the slot is delivered as (D-63.7)

    @property
    def run_key(self) -> str:
        """The D-63.11 run key, the same text ``CaseRef.run_key`` prints."""
        return f"{self.run}, {self.cg or '--'}, {self.altitude_ft:.0f} ft, {self.config or '--'}"


@dataclass
class WingVariantTable:
    """Every slot x FLIGHT-case variant, with the governing one marked per slot."""
    variants: List[WingVariant] = field(default_factory=list)
    #: Why the table is empty, when it is -- the wing analysis' own refusal.
    reason: str = ""

    def by_slot(self, slot: str) -> List[WingVariant]:
        return [v for v in self.variants if v.slot == slot]

    def governing(self) -> Dict[str, WingVariant]:
        """``{slot: governing variant}`` -- exactly one per assessed slot."""
        return {v.slot: v for v in self.variants if v.governing}

    @property
    def slots(self) -> List[str]:
        seen: List[str] = []
        for v in self.variants:
            if v.slot not in seen:
                seen.append(v.slot)
        return seen


def wing_variant_table(project: Project, envelope: Optional[EnvelopeResult] = None,
                       air_picks: Optional[Sequence[CriticalCondition]] = None,
                       ) -> WingVariantTable:
    """Assess every wing slot at every FLIGHT case (D-63.7).

    ``envelope`` is the caller's resolved V-n matrix (``select.default_envelope``
    when not given); ``air_picks`` SELECT's per-family picks over the whole
    matrix (``select.air_picks`` when not given) -- threaded in by
    ``select_wing`` so the search is not run twice and so this never asks
    ``default_critical`` for a set it is itself being built for.
    """
    # Imported here: ``select`` imports this module lazily from ``select_wing``,
    # and ``wing_inertia`` (imported above) imports ``select`` at module level.
    from . import select as _select

    env = envelope if envelope is not None else _select.default_envelope(project)
    picks = list(air_picks) if air_picks is not None else _select.air_picks(project, env)
    air_case = {c.label: c.case for c in picks if c.case is not None}
    sync_geometry_derived(project)
    wm = project.wing_mass
    if wm is None:
        return WingVariantTable(reason="the project has no 'wing_mass' inputs")
    geom = project.geometry.by_name(wm.surface) if project.geometry is not None else None
    aero = project.aero.by_name(wm.surface) if project.aero is not None else None
    if geom is None or aero is None:
        return WingVariantTable(reason=f"the project has no '{wm.surface}' geometry and aero surfaces")
    try:
        require_integrable_planform(geom)
    except MissingInputError as exc:
        return WingVariantTable(reason=str(exc))
    plane = wing_plane(project, wm.surface)
    shape = panel_shape(geom, wm, *plane, panel_weight(project))
    vn: List[VnPoint] = list(env.vn)
    variants: List[WingVariant] = []
    for k in flight_cases(project):
        vn_k = [p for p in vn if p.cg == k.name]
        if not vn_k:
            continue
        state = wing_mass_state(project, k.name)
        units = fold_units(shape, state.panel_weight_lb, state.point_masses)
        for label, far, p in _select.wing_slot_picks(project, vn_k, coincide=False):
            if p is None:
                continue
            nz = -p.nz
            nx = inertia_drag_factor(p.dx, k.weight_lb)
            inertia = wing_inertia_distribution(
                WingLoadCase(name=label, case=p.case, nz=nz, nx=nx), units)
            air = air_load_distribution(geom, aero, p.cl, p.v_eas_kt, *plane)
            a_mxx = air.stations[0].mxx
            i_mxx = inertia.stations[0].mxx
            variants.append(WingVariant(
                slot=label, far_reference=far, cg=k.name, case=p.case,
                run=p.condition, config=p.config, altitude_ft=p.altitude_ft,
                v_eas_kt=p.v_eas_kt, cl=p.cl, nz=nz, nx=nx, weight_lb=k.weight_lb,
                air_root_mxx=a_mxx, inertia_root_mxx=i_mxx, root_mxx=a_mxx + i_mxx,
                mass_state=state.label, mass_state_case=state.case,
                air_pick=(air_case.get(label) == p.case)))
    return WingVariantTable(variants=_mark_governing(variants))


def _mark_governing(variants: List[WingVariant]) -> List[WingVariant]:
    """Mark one governing variant per slot: the extreme signed root ``Mxx``.

    The air pick keeps the slot when it is within :data:`GOVERNING_TIE_REL`
    of the extreme (the balance's own noise), and always for the
    ``select.AIR_PICK_SLOTS`` -- the torsion and load-factor slots, whose
    criterion is not the bending. A slot whose air pick is not in the table
    (none on any shipped fixture) is governed by its extreme row alone.
    """
    from .select import AIR_PICK_SLOTS, SLOT_LIFT_SIGN

    out: List[WingVariant] = []
    slots = []
    for v in variants:
        if v.slot not in slots:
            slots.append(v.slot)
    winners: Dict[str, WingVariant] = {}
    for slot in slots:
        rows = [v for v in variants if v.slot == slot]
        sign = SLOT_LIFT_SIGN.get(slot, 1.0)
        def signed(v: WingVariant, s: float = sign) -> float:
            return s * v.root_mxx
        best = extreme(rows, signed)
        air = next((v for v in rows if v.air_pick), None)
        if air is not None:
            band = max(GOVERNING_TIE_REL, TIE_REL) * abs(best.root_mxx)
            if slot in AIR_PICK_SLOTS or sign * air.root_mxx >= sign * best.root_mxx - band:
                best = air
        winners[slot] = best
    for v in variants:
        out.append(WingVariant(**{**v.__dict__, "governing": winners[v.slot] is v}))
    return out


def governing_points(table: WingVariantTable) -> Dict[str, int]:
    """``{slot: V-n case number}`` of each slot's governing run."""
    return {slot: v.case for slot, v in table.governing().items()}
