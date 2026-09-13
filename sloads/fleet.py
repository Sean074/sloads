"""Quantitative fleet comparison -- pure, unit-testable placement of one airplane
against a reference fleet.

A companion to the visual W/S-vs-W/P, MTOW-vs-empty-weight and geometric scatters on the
Aircraft Comparison page: those show *where* the design sits; this module reports it
numerically -- the nearest-N similar aircraft, the wing-loading / power-loading
percentile band, and outlier flags. It has no pandas and no Streamlit; the only
file it touches is the bundled reference fleet it owns
(:func:`reference_fleet`), and the readout and scatters are rendered by the GUI
page over what this module and :mod:`sloads.report.fleet_figures` return
(GUI_design §8.4).

**Amended at #268** (note 57 D-57.5), when the comparison ported to the
surviving GUI. Two things the retiring page owned move here, because neither was
ever presentation: :func:`subject_from_project` -- the priority chain that says
which slice each metric is read from -- and :func:`reference_fleet`, which reads
the bundled CSV. The statistics were always pure and still are; what this module
now also owns is *where the numbers come from*, which is the part that had a
defect history (the MTOW chain, corrected 2026-08-15) and which D-57.5 would
have had rewritten from scratch in the new front-end. The figures themselves are
:mod:`sloads.report.fleet_figures`; no front-end derives either.

The Aircraft Comparison page assembles the subject from whatever slices are
present, so a subject may supply any subset of the metrics -- the nearest-N distance
is computed over **whichever metrics the subject supplies** (always log-MTOW; add
W/S and W/P when available), each normalized against the fleet spread so the axes are
commensurate. Jets (no shaft power) carry no W/P and are excluded from W/P distance
and the W/P percentile only, never from the comparator pool.
"""

from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from .constants import IN_PER_FT

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .models import Project

#: The bundled reference fleet: nominal published specifications, never a FAR
#: input. It lives beside the code that reads it (``sloads/data/``) rather than
#: in a front-end's directory, which is where it sat until #268 -- an installed
#: ``sloads`` could not place an airplane against a fleet at all, because the
#: data shipped with a Streamlit app nothing imports.
REFERENCE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "data", "reference_aircraft.csv")

# Defaults (GUI_design §8.4, decisions D-E4-2 / D-E4-3, 2026-07-15).
DEFAULT_NEAREST_N = 3
DEFAULT_BAND = (10.0, 90.0)  # percentile band for the W/S and W/P outlier flags


@dataclass(frozen=True)
class FleetPoint:
    """One reference aircraft (nominal published specs; never a FAR input).

    ``wingspan_ft`` and ``aspect_ratio`` are optional geometry carried for the
    geometric comparison plots (span / area / AR vs. MTOW). They are not used by
    :func:`fleet_stats` -- the loading placement runs on MTOW / W/S / W/P only -- so
    older callers that omit them are unaffected.
    """
    name: str
    mtow_lb: float
    oew_lb: float
    max_hp: float
    wing_area_ft2: float
    seats: int = 0
    wingspan_ft: Optional[float] = None
    aspect_ratio: Optional[float] = None

    @property
    def w_s(self) -> Optional[float]:
        """Wing loading MTOW/S (lb/ft^2), or ``None`` when the area is unknown."""
        if self.wing_area_ft2 and self.wing_area_ft2 > 0:
            return self.mtow_lb / self.wing_area_ft2
        return None

    @property
    def w_p(self) -> Optional[float]:
        """Power loading MTOW/P (lb/hp), or ``None`` for a jet (max_hp == 0)."""
        if self.max_hp and self.max_hp > 0:
            return self.mtow_lb / self.max_hp
        return None

    @property
    def span(self) -> Optional[float]:
        """Wingspan (ft): the stored ``wingspan_ft`` if given, else derived from
        ``sqrt(aspect_ratio * wing_area_ft2)`` when both are present, else ``None``.
        Presentation-only geometry, matching :attr:`Subject.span`."""
        if self.wingspan_ft and self.wingspan_ft > 0:
            return self.wingspan_ft
        if (self.aspect_ratio and self.aspect_ratio > 0
                and self.wing_area_ft2 and self.wing_area_ft2 > 0):
            return math.sqrt(self.aspect_ratio * self.wing_area_ft2)
        return None

    @property
    def aspect_ratio_effective(self) -> Optional[float]:
        """Aspect ratio: the stored ``aspect_ratio`` if given, else derived from
        ``wingspan_ft**2 / wing_area_ft2`` when both are present, else ``None``.
        Presentation-only geometry, matching :attr:`Subject.aspect_ratio_effective`."""
        if self.aspect_ratio and self.aspect_ratio > 0:
            return self.aspect_ratio
        if (self.wingspan_ft and self.wingspan_ft > 0
                and self.wing_area_ft2 and self.wing_area_ft2 > 0):
            return self.wingspan_ft ** 2 / self.wing_area_ft2
        return None


@dataclass(frozen=True)
class Subject:
    """The airplane being placed against the fleet.

    ``mtow_lb`` is always required (the common comparison axis). ``oew_lb``,
    ``wing_area_ft2`` and ``power_hp`` are optional -- each present metric adds a
    dimension to the nearest-N distance and enables its percentile / outlier check.

    ``wingspan_ft``, ``aspect_ratio`` and ``seats`` are **presentation-only**
    geometry carried for the Aircraft Comparison page's parameter table and its
    geometric scatter plots (span / area / AR / seats vs. MTOW). They are *not* used
    by :func:`fleet_stats` -- the loading placement runs on MTOW / W/S / W/P only --
    so a subject that omits them ranks identically to one that supplies them.
    """
    name: str
    mtow_lb: float
    oew_lb: Optional[float] = None
    wing_area_ft2: Optional[float] = None
    power_hp: Optional[float] = None
    wingspan_ft: Optional[float] = None
    aspect_ratio: Optional[float] = None
    seats: int = 0

    @property
    def w_s(self) -> Optional[float]:
        if self.wing_area_ft2 and self.wing_area_ft2 > 0:
            return self.mtow_lb / self.wing_area_ft2
        return None

    @property
    def w_p(self) -> Optional[float]:
        if self.power_hp and self.power_hp > 0:
            return self.mtow_lb / self.power_hp
        return None

    @property
    def span(self) -> Optional[float]:
        """Wingspan (ft): the stored ``wingspan_ft`` if given, else derived from
        ``sqrt(aspect_ratio * wing_area_ft2)`` when both are present, else ``None``.

        Presentation-only (the geometric plots) -- never a distance term.
        """
        if self.wingspan_ft and self.wingspan_ft > 0:
            return self.wingspan_ft
        if (self.aspect_ratio and self.aspect_ratio > 0
                and self.wing_area_ft2 and self.wing_area_ft2 > 0):
            return math.sqrt(self.aspect_ratio * self.wing_area_ft2)
        return None

    @property
    def aspect_ratio_effective(self) -> Optional[float]:
        """Aspect ratio: the stored ``aspect_ratio`` if given, else derived from
        ``wingspan_ft**2 / wing_area_ft2`` when both are present, else ``None``.

        Presentation-only (the geometric plots) -- never a distance term.
        """
        if self.aspect_ratio and self.aspect_ratio > 0:
            return self.aspect_ratio
        if (self.wingspan_ft and self.wingspan_ft > 0
                and self.wing_area_ft2 and self.wing_area_ft2 > 0):
            return self.wingspan_ft ** 2 / self.wing_area_ft2
        return None


@dataclass(frozen=True)
class FleetStats:
    """The quantitative placement of a :class:`Subject` against a fleet.

    ``nearest`` is the closest-N ``(FleetPoint, distance)`` pairs (ascending
    distance; the normalized distance is dimensionless). ``ws_percentile`` /
    ``wp_percentile`` are the subject's percentile rank (0-100) within the fleet
    distribution, or ``None`` when the subject lacks that metric or the fleet has no
    comparators for it. ``ws_band`` / ``wp_band`` are the fleet ``(low, high)``
    percentile band values used for the outlier test. ``outliers`` names each metric
    ("W/S", "W/P") whose subject value falls outside that band.
    """
    nearest: List[Tuple[FleetPoint, float]]
    ws_percentile: Optional[float]
    wp_percentile: Optional[float]
    ws_band: Optional[Tuple[float, float]]
    wp_band: Optional[Tuple[float, float]]
    outliers: List[str]


def percentile_rank(value: float, population: Sequence[float]) -> Optional[float]:
    """Percentile rank (0-100) of ``value`` within ``population``.

    The fraction of the population at or below ``value``, times 100 -- the standard
    "weak" rank. ``None`` for an empty population.
    """
    pop = [p for p in population if p is not None]
    if not pop:
        return None
    at_or_below = sum(1 for p in pop if p <= value)
    return 100.0 * at_or_below / len(pop)


def percentile(population: Sequence[float], pct: float) -> Optional[float]:
    """The ``pct`` (0-100) percentile of ``population`` by linear interpolation.

    ``None`` for an empty population. Mirrors numpy's default ("linear") method so
    the band is the conventional one, without adding a numpy dependency.
    """
    pop = sorted(p for p in population if p is not None)
    if not pop:
        return None
    if len(pop) == 1:
        return float(pop[0])
    rank = (pct / 100.0) * (len(pop) - 1)
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return float(pop[lo])
    frac = rank - lo
    return float(pop[lo] + (pop[hi] - pop[lo]) * frac)


def _band(population: Sequence[float], band: Tuple[float, float]) -> Optional[Tuple[float, float]]:
    lo = percentile(population, band[0])
    hi = percentile(population, band[1])
    if lo is None or hi is None:
        return None
    return (lo, hi)


def _spread(values: Sequence[float]) -> float:
    """A positive normalizing scale for a metric: its (max - min) over the fleet.

    Falls back to ``|mean|`` then ``1.0`` so a degenerate (all-equal or zero) metric
    never divides by zero -- it simply contributes ~no distance.
    """
    vals = [v for v in values if v is not None]
    if not vals:
        return 1.0
    spread = max(vals) - min(vals)
    if spread > 0:
        return spread
    mean = math.fsum(vals) / len(vals)
    return abs(mean) if mean else 1.0


def fleet_stats(
    subject: Subject,
    fleet: Sequence[FleetPoint],
    *,
    n: int = DEFAULT_NEAREST_N,
    band: Tuple[float, float] = DEFAULT_BAND,
) -> FleetStats:
    """Place ``subject`` against ``fleet``: nearest-N, percentile band, outliers.

    Distance is a normalized Euclidean metric over the axes the subject supplies:
    always ``log10(MTOW)`` (weight spans orders of magnitude across the fleet), plus
    W/S and W/P when the subject has them. Each axis is divided by the fleet spread
    on that axis so the axes are commensurate. A fleet point missing an axis the
    subject has (e.g. a jet's W/P) simply contributes no term for that axis, so it
    can still rank as a neighbour on the remaining axes.
    """
    fleet = list(fleet)

    # Per-axis normalizing scales from the fleet spread (subject included so an
    # off-fleet concept still yields a finite, comparable distance).
    log_mtows = [math.log10(p.mtow_lb) for p in fleet if p.mtow_lb > 0]
    log_mtows.append(math.log10(subject.mtow_lb) if subject.mtow_lb > 0 else 0.0)
    s_mtow = _spread(log_mtows)
    ws_pop = [p.w_s for p in fleet if p.w_s is not None]
    wp_pop = [p.w_p for p in fleet if p.w_p is not None]
    s_ws = _spread(ws_pop + ([subject.w_s] if subject.w_s is not None else []))
    s_wp = _spread(wp_pop + ([subject.w_p] if subject.w_p is not None else []))

    subj_log_mtow = math.log10(subject.mtow_lb) if subject.mtow_lb > 0 else None

    def _distance(p: FleetPoint) -> float:
        sq = 0.0
        if subj_log_mtow is not None and p.mtow_lb > 0:
            sq += ((subj_log_mtow - math.log10(p.mtow_lb)) / s_mtow) ** 2
        if subject.w_s is not None and p.w_s is not None:
            sq += ((subject.w_s - p.w_s) / s_ws) ** 2
        if subject.w_p is not None and p.w_p is not None:
            sq += ((subject.w_p - p.w_p) / s_wp) ** 2
        return math.sqrt(sq)

    ranked = sorted(((p, _distance(p)) for p in fleet), key=lambda pd: pd[1])
    nearest = ranked[: max(0, n)]

    # Percentile band + outlier flags on the metrics the subject supplies.
    ws_percentile = percentile_rank(subject.w_s, ws_pop) if subject.w_s is not None else None
    wp_percentile = percentile_rank(subject.w_p, wp_pop) if subject.w_p is not None else None
    ws_band = _band(ws_pop, band) if subject.w_s is not None else None
    wp_band = _band(wp_pop, band) if subject.w_p is not None else None

    outliers: List[str] = []
    if subject.w_s is not None and ws_band is not None and not (ws_band[0] <= subject.w_s <= ws_band[1]):
        outliers.append("W/S")
    if subject.w_p is not None and wp_band is not None and not (wp_band[0] <= subject.w_p <= wp_band[1]):
        outliers.append("W/P")

    return FleetStats(
        nearest=nearest,
        ws_percentile=ws_percentile,
        wp_percentile=wp_percentile,
        ws_band=ws_band,
        wp_band=wp_band,
        outliers=outliers,
    )


# --------------------------------------------------------------------------- #
# Where the numbers come from (#268, note 57 D-57.5)
# --------------------------------------------------------------------------- #


def reference_fleet(path: Optional[str] = None) -> List[FleetPoint]:
    """The bundled reference aircraft as :class:`FleetPoint` records.

    ``path`` defaults to :data:`REFERENCE_CSV`. The file carries a leading
    ``#`` comment block stating what the data is and is not; the reader skips
    it, and ``tests/test_reference_aircraft.py`` guards the shape of the rows.

    Returns ``[]`` for a missing file rather than raising: the fleet comparison
    is an assessment beside the analysis, and a caller that cannot find the
    reference data should say so on its page, not fail the page it is on.
    """
    target = path or REFERENCE_CSV
    if not os.path.exists(target):
        return []

    def _opt(row: Dict[str, str], key: str) -> Optional[float]:
        raw = (row.get(key) or "").strip()
        try:
            return float(raw) if raw else None
        except ValueError:
            return None

    def _req(row: Dict[str, str], key: str) -> float:
        return _opt(row, key) or 0.0

    with open(target, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(line for line in fh
                                   if not line.startswith("#")))
    points: List[FleetPoint] = []
    for row in rows:
        name = (row.get("aircraft") or "").strip()
        if not name:
            continue
        seats = _opt(row, "seats")
        points.append(FleetPoint(
            name=name,
            mtow_lb=_req(row, "mtow_lb"),
            oew_lb=_req(row, "oew_lb"),
            max_hp=_req(row, "max_hp"),
            wing_area_ft2=_req(row, "wing_area_ft2"),
            seats=int(seats) if seats else 0,
            wingspan_ft=_opt(row, "wingspan_ft"),
            aspect_ratio=_opt(row, "aspect_ratio"),
        ))
    return points


def _wtestima_value(project: "Project", key: str) -> Optional[float]:
    """One figure out of a live WTESTIMA estimate, by ``LoadValue.key``, or ``None``.

    Runs the registered ``weight_estimate`` module (needs ``weight.estimation``);
    any failure (missing slice, ValueError) yields ``None`` so the caller falls
    back to a lower-priority source.
    """
    from . import registry

    if not (project.weight and project.weight.estimation):
        return None
    try:
        result = registry.get("weight_estimate")(project)
    except Exception:
        return None
    for cond in result.conditions:
        for value in cond.values:
            if value.key == key:
                return float(value.value)
    return None


def _planform(project: "Project") -> Dict[str, Optional[float]]:
    """The wing planform's area (ft²), aspect ratio and full span (in), or ``{}``.

    Read through ``derived_geometry``'s resolvers rather than off
    ``wing_geometry.surface_properties`` directly: #70 made those the single
    owner of *what area the analysis actually uses*, after four numbers for one
    wing were found in the tree. A comparison page is the fifth place that could
    have grown one, and it did not have to -- the resolvers answer exactly the
    three quantities the subject needs.

    ``planform_area_sqft`` raises on a half-entered planform, which its own
    docstring leaves to callers that only want to display something. This is
    one: a fleet scatter with no point on it beats a page that will not open.
    """
    from .derived_geometry import planform_area_sqft, wing_aspect_ratio, wing_span_in

    if project.geometry is None or project.geometry.by_name("wing") is None:
        return {}
    try:
        area = planform_area_sqft(project)
    except (ValueError, ZeroDivisionError):
        return {}
    return {"area_sqft": area,
            "aspect_ratio": wing_aspect_ratio(project),
            "span_in": wing_span_in(project)}


def subject_from_project(project: "Project") -> Optional[Subject]:
    """Assemble the comparison :class:`Subject` from the best-available slices.

    Priority per metric (backlog F2 step 2; surface fallback added in M2-5):
      MTOW  -- cg_cases.max_takeoff_weight (G-14 SSOT + chain) -> WTESTIMA
      Empty weight -- weight.database_totals()[1] (EMPTY rows; #94, C210-12) -> WTESTIMA
      area  -- parametric.wing_area_sqft -> WINGGEOM planform -> speeds.wing_area_sqft
      power -- Sum engines[].max_cont_hp -> weight.estimation.max_continuous_hp
      AR    -- parametric.aspect_ratio -> WINGGEOM planform
      span  -- WINGGEOM planform (else back-derived from AR*area by Subject.span)
      seats -- speeds.occupants -> weight.estimation.seats

    Returns ``None`` only when no MTOW can be found (the common comparison
    axis); a missing secondary metric leaves its field ``None`` -- rendered
    "--" -- rather than dropping the subject silently.

    Moved here from ``app/views/aircraft_comparison.py`` at #268 (see the module
    docstring). Behaviour is unchanged, deliberately: the chain is the part of
    this page with a defect history, and a port that re-derived it would be
    re-deriving the fix with it.
    """
    from . import cg_cases

    speeds = project.speeds
    weight = project.weight
    config = project.geometry.parametric if project.geometry is not None else None
    planform = _planform(project)

    direct = weight.database_totals() if (weight and weight.items) else None

    # MTOW from its single owner (decision G-14: the SSOT field, else the
    # documented speeds/envelope/heaviest-case fallback chain), then WTESTIMA.
    # The item-database total sat in this chain until 2026-08-15, which plotted
    # this airplane against the reference fleet at a weight no loading can
    # reach -- 1,800 lb high on a regional jet.
    mtow: Optional[float] = cg_cases.max_takeoff_weight(project, required=False) or None
    if not mtow:
        mtow = _wtestima_value(project, "max_take_off_weight")
    if not mtow:
        return None

    oew: Optional[float] = (float(direct[1]) if direct and direct[1]
                            else _wtestima_value(project, "empty_weight"))

    wing_area: Optional[float] = None
    if config and config.wing_area_sqft:
        wing_area = float(config.wing_area_sqft)
    elif planform.get("area_sqft"):
        wing_area = float(planform["area_sqft"] or 0.0)
    elif speeds and speeds.wing_area_sqft:
        wing_area = float(speeds.wing_area_sqft)

    power: Optional[float] = None
    if project.engines:
        power = math.fsum(e.max_cont_hp or 0.0 for e in project.engines) or None
    if power is None and weight and weight.estimation and weight.estimation.max_continuous_hp:
        power = float(weight.estimation.max_continuous_hp)

    aspect_ratio: Optional[float] = None
    if config and config.aspect_ratio:
        aspect_ratio = float(config.aspect_ratio)
    elif planform.get("aspect_ratio"):
        aspect_ratio = float(planform["aspect_ratio"] or 0.0)

    # Span from the surface planform (full span, inches) when available;
    # otherwise Subject.span back-derives it from sqrt(AR * area).
    wingspan_ft: Optional[float] = None
    if planform.get("span_in"):
        wingspan_ft = float(planform["span_in"] or 0.0) / IN_PER_FT

    seats = 0
    if speeds and speeds.occupants:
        seats = int(speeds.occupants)
    elif weight and weight.estimation and weight.estimation.seats:
        seats = int(weight.estimation.seats)

    return Subject(
        name=project.name or "This airplane",
        mtow_lb=mtow,
        oew_lb=oew,
        wing_area_ft2=wing_area,
        power_hp=power,
        wingspan_ft=wingspan_ft,
        aspect_ratio=aspect_ratio,
        seats=seats,
    )
