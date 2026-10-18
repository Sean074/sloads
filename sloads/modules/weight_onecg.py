"""Weight, centre of gravity and inertia for one loading -- WTONECG.BAS.

Given the itemized weight data base (each component's weight and station, plus
its own moments of inertia), WTONECG returns the loading's total weight, CG and
the airplane moments of inertia about both the airplane axes and the principal
axes, in slug-ft^2 and lb-in^2. These mass/inertia properties feed the flight,
landing and one-engine-out load modules in later phases.

The inertias are the parallel-axis (transfer) sum of each item about the
airplane CG; W*d^2 accumulates in lb-in^2 and is divided by 144*g to report
slug-ft^2 (WTONECG.BAS lines 780-860). Y is carried but is zero for a laterally
symmetric airplane.

**Which loading (design note 70, #382).** WTONECG.BAS reports *one* loading --
the operator keys in which rows are aboard. The port's one output was the sum
of every database row, which on every bundled airplane but the Appendix A one
is the database ceiling (G-14), not a loading: 43,308 lb against an MTOW of
36,817 on ``atr42_100``. Since note 70 the module reports every CG case's
loading of record (:func:`case_mass_properties`) and keeps the all-rows sum as
the labelled :data:`CEILING_TITLE` row, last. The equations are untouched.

Reference: WTONECG.BAS, Appendix C p377-381; worked example Appendix A p136.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Optional, Tuple

from ..constants import LBIN2_PER_SLUGFT2
from ..models import (
    CgCase,
    ConditionResult,
    LoadValue,
    MassCase,
    MassItem,
    MassResult,
    MissingInputError,
    ModuleResult,
    Project,
)
from ..picks import TIE_REL
from ..registry import register

if TYPE_CHECKING:
    from ..mass_distribution import CaseLoading

# 23.23 load-distribution limits (the CG/loading basis) + 23.29 empty weight and
# corresponding CG -- the quantities WTONECG actually computes (User's Guide S4.3).
_FAR = "23.23/23.29"
_SLUGFT2 = "slug-ft^2"
_LBIN2 = "lb-in^2"


def weights_and_inertia(items: List[MassItem]) -> ConditionResult:
    """Total weight, CG and moments of inertia for the given loading."""
    loaded = [it for it in items if it.weight_lb != 0]
    if not loaded:
        raise MissingInputError("WTONECG needs at least one non-zero weight item")

    # Weight and CG (WTONECG.BAS lines 657-750).
    total = math.fsum(it.weight_lb for it in loaded)
    xbar = math.fsum(it.weight_lb * it.x for it in loaded) / total
    zbar = math.fsum(it.weight_lb * it.z for it in loaded) / total

    # Moments of inertia about airplane coordinates, lb-in^2 (lines 780-860):
    # the parallel-axis transfer of each item plus the item's own inertia.
    ixx = (math.fsum(it.weight_lb * (it.y ** 2 + (it.z - zbar) ** 2) for it in loaded)
           + math.fsum(it.ixx for it in loaded))
    iyy = (math.fsum(it.weight_lb * ((it.x - xbar) ** 2 + (it.z - zbar) ** 2) for it in loaded)
           + math.fsum(it.iyy for it in loaded))
    izz = (math.fsum(it.weight_lb * (it.y ** 2 + (it.x - xbar) ** 2) for it in loaded)
           + math.fsum(it.izz for it in loaded))
    ixz = math.fsum(it.weight_lb * (it.x - xbar) * (it.z - zbar) for it in loaded)

    # The share of each inertia the rows' *own* inertias supply (#385, review
    # A5): the rest is the parallel-axis transfer alone. Appendix A's IXX
    # 1201.527 needs the ga6 rows' own terms; an airplane whose rows carry
    # none is a transfer-only answer, and the page says so.
    own_ixx = math.fsum(it.ixx for it in loaded)
    own_iyy = math.fsum(it.iyy for it in loaded)
    own_izz = math.fsum(it.izz for it in loaded)

    # Convert lb-in^2 -> slug-ft^2.
    ixx_s = ixx / LBIN2_PER_SLUGFT2
    iyy_s = iyy / LBIN2_PER_SLUGFT2
    izz_s = izz / LBIN2_PER_SLUGFT2
    ixz_s = ixz / LBIN2_PER_SLUGFT2

    # Principal axes (lines 865-910): rotate in the x-z plane to null the IXZ
    # product of inertia.
    two_theta = math.pi / 2 if izz_s == ixx_s else math.atan(2 * ixz_s / (izz_s - ixx_s))
    theta = 0.5 * two_theta
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    sin_2t = math.sin(2 * theta)
    pxi = ixx_s * cos_t ** 2 + izz_s * sin_t ** 2 - ixz_s * sin_2t
    pyi = iyy_s
    pzi = ixx_s * sin_t ** 2 + izz_s * cos_t ** 2 + ixz_s * sin_2t

    return ConditionResult(
        title="Weight, centre of gravity and inertia for one loading",
        far_reference=_FAR,
        values=[
            LoadValue("Weight", total, "lb", quantity="mass", key="weight"),
            LoadValue("XBAR (fus station)", xbar, "in", key="xbar_fus_station"),
            LoadValue("ZBAR (waterline)", zbar, "in", key="zbar_waterline"),
            LoadValue("IXX", ixx_s, _SLUGFT2, key="ixx"),
            LoadValue("IYY", iyy_s, _SLUGFT2, key="iyy"),
            LoadValue("IZZ", izz_s, _SLUGFT2, key="izz"),
            LoadValue("IXZ", ixz_s, _SLUGFT2, key="ixz"),
            LoadValue("IXX (lb-in^2)", ixx, _LBIN2, key="ixx_lb_in_2"),
            LoadValue("IYY (lb-in^2)", iyy, _LBIN2, key="iyy_lb_in_2"),
            LoadValue("IZZ (lb-in^2)", izz, _LBIN2, key="izz_lb_in_2"),
            LoadValue("IXZ (lb-in^2)", ixz, _LBIN2, key="ixz_lb_in_2"),
            LoadValue("IX(P) principal", pxi, _SLUGFT2, key="ix_p_principal"),
            LoadValue("IY(P) principal", pyi, _SLUGFT2, key="iy_p_principal"),
            LoadValue("IZ(P) principal", pzi, _SLUGFT2, key="iz_p_principal"),
            LoadValue("Principal-axis angle theta", math.degrees(theta), "deg", key="principal_axis_angle_theta"),
            LoadValue("IXX share from item own inertia", 100.0 * own_ixx / ixx if ixx else 0.0, "%",
                      quantity="diagnostic", key="ixx_own_inertia_share"),
            LoadValue("IYY share from item own inertia", 100.0 * own_iyy / iyy if iyy else 0.0, "%",
                      quantity="diagnostic", key="iyy_own_inertia_share"),
            LoadValue("IZZ share from item own inertia", 100.0 * own_izz / izz if izz else 0.0, "%",
                      quantity="diagnostic", key="izz_own_inertia_share"),
        ],
        note="Theta measured up from the waterline and aft from the CG.",
    )


#: The title of the one condition (and the one :class:`MassCase`) that is not a
#: loading: every database row aboard at once (design note 70 D-70.1; G-14
#: names the number the database *ceiling*). Appendix A p136 prints exactly
#: this on the ga6 database, whose rows sum to its aft-gross loading -- the
#: oracle row (G-70.1).
CEILING_TITLE = "Database ceiling (every row aboard)"

_TITLE_PREFIX = "Mass properties -- "


class CaseMassProperties(NamedTuple):
    """What WTONECG has to say about a project, computed once (D-70.2).

    ``rows`` are the persisted :class:`MassCase` rows -- one per CG case whose
    loading of record derives, in case order, then the ceiling row last;
    ``conditions`` are the same rows as the module's ``ConditionResult`` set
    (one per row, same order); ``skipped`` names each CG case that got no row
    and why, so a reader sees the absence rather than inferring it.
    """

    rows: List[MassCase]
    conditions: List[ConditionResult]
    skipped: List[Tuple[str, str]]


def _mass_case(condition: ConditionResult, name: str, *, ceiling: bool) -> MassCase:
    v = {lv.key: lv.value for lv in condition.values}
    return MassCase(
        name=name, weight_lb=v["weight"], cg_x=v["xbar_fus_station"], cg_y=0.0,
        cg_z=v["zbar_waterline"], ixx=v["ixx_lb_in_2"], iyy=v["iyy_lb_in_2"],
        izz=v["izz_lb_in_2"], ixz=v["ixz_lb_in_2"], gear_down=True, ceiling=ceiling)


def case_mass_properties(project: Project) -> CaseMassProperties:
    """The mass properties of every loading of record, and of the ceiling.

    **The one owner** of "the weight, CG and inertia of case X" (design note
    70 D-70.2): :func:`run`, :func:`build_mass` and ONENGOUT's mass state all
    read this. Each ``weight.cg_cases[]`` entry -- FLIGHT and GROUND alike
    (Q1) -- is resolved to its loading of record by
    :func:`sloads.mass_distribution.derive_case_loadings` (entered on the case,
    note 63 D-25, or searched), and :func:`weights_and_inertia` is applied to
    *that loading's* items. A case whose loading the database cannot produce
    gets no row and one stated reason (``baron_58``'s ``fwd regardless``);
    nothing is invented. The all-rows sum closes the list as the labelled
    ceiling, never first: until this note it was the module's *only* output,
    18 % over MTOW on ``atr42_100`` with an Ixx that belongs to no case
    (160,600 slug-ft^2 with the wing fuel aboard, 34,600 without).

    ``gear_down`` is ``True`` on every row: the database carries no gear-up
    position (D-70.3, Q4).
    """
    weight = project.weight
    if weight is None or not weight.items:
        raise MissingInputError("Project has no 'weight.items' data base for the mass slice")
    from ..mass_distribution import derive_case_loadings

    rows: List[MassCase] = []
    conditions: List[ConditionResult] = []
    skipped: List[Tuple[str, str]] = []
    cases = list(weight.cg_cases or [])
    loadings = {}
    if cases:
        try:
            loadings = {ld.name: ld for ld in derive_case_loadings(project, cases)}
        # refusal: an invalid case list derives no loading for any case; each
        # case is then stated as skipped for that one reason below
        except ValueError as exc:
            skipped.extend((c.name, str(exc)) for c in cases)
            cases = []
    for case in cases:
        ld = loadings.get(case.name)
        if ld is None or not ld.derivable:
            skipped.append((case.name, ld.note if ld is not None and ld.note
                            else "no loading of record derives from the weight data base"))
            continue
        try:
            condition = weights_and_inertia(list(ld.items))
        # refusal: a loading with no non-zero row has no mass properties
        except MissingInputError as exc:
            skipped.append((case.name, str(exc)))
            continue
        condition = replace(
            condition, title=f"{_TITLE_PREFIX}{case.name}",
            note=(f"The loading of record for CG case '{case.name}' "
                  f"({'entered on the case' if ld.entered else 'searched from the data base'}; "
                  f"{len(ld.items)} rows aboard). " + condition.note))
        conditions.append(condition)
        rows.append(_mass_case(condition, case.name, ceiling=False))
    ceiling = replace(
        weights_and_inertia(weight.items), title=CEILING_TITLE,
        note=("Every row of the weight data base aboard at once -- the ceiling of "
              "OEW <= MLW <= MTOW <= the item total, not a loading the airplane flies "
              "unless its data base sums to one. The Appendix A p136 figures are "
              "this row. " + weights_and_inertia(weight.items).note))
    conditions.append(ceiling)
    rows.append(_mass_case(ceiling, CEILING_TITLE, ceiling=True))
    return CaseMassProperties(rows, conditions, skipped)


def mass_basis(project: Project,
               loadings: Optional[Dict[str, "CaseLoading"]] = None,
               ) -> Optional[Tuple[CgCase, "CaseLoading"]]:
    """The airplane state a whole-airplane dynamic case is sized at (#333
    ruling 4; design note 70 D-70.5).

    The heaviest FLIGHT weight/CG case whose loading the weight database can
    produce, and the aft-most of those that tie on weight -- the shorter fin
    arm, so the larger fin load for one yawing moment. **One owner**: ONENGOUT's
    march takes its IZZ and CG from this loading and the balanced deck assembles
    the case on this CG case's 1 g point (D-66.11); the landing seed's waterline
    placeholder and the Geometry page's CG label read the same pick, so "the
    representative loading" has one meaning. Until #333 the march read the
    all-items loading instead, 17.6 % above MTOW on the ATR.

    ``loadings`` is the caller's ``{name: CaseLoading}`` when it has them;
    ``None`` when no derivable FLIGHT case exists.
    """
    from ..cg_cases import flight_cases
    from ..mass_distribution import derive_case_loadings
    from ..picks import extreme

    cases = flight_cases(project)
    if loadings is None:
        loadings = {ld.name: ld for ld in derive_case_loadings(project, cases)}
    usable = [(c, loadings[c.name]) for c in cases
              if loadings.get(c.name) is not None and loadings[c.name].derivable]
    if not usable:
        return None
    heaviest = max(ld.weight_lb for _, ld in usable)
    tied = [u for u in usable if u[1].weight_lb >= heaviest - TIE_REL * abs(heaviest)]
    return extreme(tied, lambda u: u[1].cg_x)


def basis_row(mass: Optional[MassResult], project: Project) -> Optional[MassCase]:
    """The persisted row of the :func:`mass_basis` case, else the first
    non-ceiling row, else the ceiling row, else ``None`` (D-70.4's fallback
    order for every reader that wants *one* representative loading)."""
    if mass is None or not mass.cases:
        return None
    by_name = {c.name: c for c in mass.cases if not c.ceiling}
    if by_name:
        try:
            basis = mass_basis(project)
        # refusal: an invalid case list has no basis; the first row stands in
        except ValueError:
            basis = None
        if basis is not None and basis[0].name in by_name:
            return by_name[basis[0].name]
        return next(iter(by_name.values()))
    return mass.cases[0]


def build_mass(project: Project) -> MassResult:
    """The persisted mass-properties slice (``Project.mass``): one
    :class:`MassCase` per CG case with a loading of record, then the ceiling
    row last (:func:`case_mass_properties`, design note 70 D-70.1)."""
    return MassResult(cases=case_mass_properties(project).rows)


def refresh_mass(project: Project) -> bool:
    """Make ``project.mass`` the slice ``weight.items`` and ``weight.cg_cases``
    derive; say whether it moved.

    The one writer of ``Project.mass`` (#62, PB-1). The GUI calls it whenever
    the item data base or the CG cases are persisted, and gate G5's reduction
    calls it after dropping the stored slice, so "the mass slice" has exactly
    one meaning: :func:`build_mass` over the project as it stands. No items, or
    none with a weight, derive nothing and the slice is ``None`` -- the
    ``weight_mass`` step's ✅ goes out with them rather than lingering on a
    loading that no longer exists. Idempotent by value: a project whose stored
    slice already equals the derivation is left untouched, which is what lets
    a render pass call this without dirtying the project
    (``tests/test_dirty_flag.py``).
    """
    fresh: Optional[MassResult]
    try:
        fresh = build_mass(project)
    except MissingInputError:
        fresh = None
    if fresh == project.mass:
        return False
    project.mass = fresh
    return True


# --------------------------------------------------------------------------- #
# Project entry point + registration
# --------------------------------------------------------------------------- #
MODULE_NAME = "weight_onecg"


def run(project: Project) -> ModuleResult:
    """Run WTONECG against a :class:`Project`: one condition per CG case with a
    loading of record, then the database ceiling (design note 70 D-70.1). A
    case that derives no loading is stated in the ceiling condition's note."""
    if project.weight is None or not project.weight.items:
        raise MissingInputError("Project has no 'weight.items' data base for the weight_onecg module")
    props = case_mass_properties(project)
    conditions = list(props.conditions)
    if props.skipped:
        stated = "; ".join(f"'{name}': {why}" for name, why in props.skipped)
        conditions[-1] = replace(
            conditions[-1],
            note=conditions[-1].note + f" No row for {len(props.skipped)} CG case(s) -- {stated}.")
    return ModuleResult(module=MODULE_NAME, conditions=conditions)


register(MODULE_NAME, run)
