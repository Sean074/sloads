"""The report's content model: :class:`Section`, :class:`Table`, :class:`Figure`.

Step G8.4. This module answers *what a report says*; :mod:`sloads.report.latex`
answers *how it looks*. Keeping the two apart is what lets a test assert
``doc.section("Wing Loads").table.rows`` instead of matching LaTeX strings, and
lets the renderer stay a dumb, fully-covered string function.

**What is left here, and what was.** This module built the *summary report* --
``build_report``, its nine sections, its bundle manifest -- as well as owning the
model those sections were made of. The summary report's only production consumer
was ``app/views/export_report.py``, which retired with the rest of that front-end
at #270 (note 57 D-57.6, note 60 D-60.11), so the document and its sections were
deleted with it and what remains is the model plus the three plot-data producers
both the documents and the GUI draw from. The four cross-cutting sections that
existed nowhere else -- axes and sign conventions, the governing safety factors,
the FAR 23 Subpart C coverage matrix and the package file list -- were merged
into the surviving document first, at #278, and live in
:mod:`sloads.report.front_sections`. The surviving document is
:mod:`sloads.report.oracle_content`, whose rules are
``docs/10_standard/ORACLE_REPORT.md``.

Three rules still govern everything built from this model:

* **Nothing is recomputed here.** Every figure comes from the same pure builder
  the GUI pages and the sbeam bridge use. A report that computed its own values
  would eventually disagree with the exports it accompanies.
* **Every load is LIMIT, stated, and located.** Loads are the calc's own values
  (note 49 OR-116): nothing here is scaled, each row states the
  ``safety_factor`` a sizing analysis must apply, and each names the
  station/case it occurs at. The ``-ULT`` marker survives only on the two
  families the regulation prescribes already ultimate (OR-118). Envelopes are
  two-sided. Non-load quantities (weights, geometry, speeds, load factors) take
  no factor at all.
* **Absence is content.** A section whose inputs are missing carries an
  ``absent_reason`` and is still rendered, with that reason. It is never silently
  dropped and never rendered as an empty table (ORACLE_REPORT.md §3.4).

Pure: no filesystem, no subprocess, no Streamlit, no clock. ``generated`` is a
caller-supplied string, so two builds of the same project are identical.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..models import Project
from ..units import (
    HUMAN_SI,
    Channel,
    DeliverableUnits,
    UnitSystem,
    deliverable_units,
)
from .render import format_value, ultimate_units

#: Errors a defensive build step tolerates. Same set the Export page catches: a
#: half-filled project must yield a report with "not analysed" sections, never a
#: traceback -- the report is how an engineer *finds* the gaps.
_CALC_ERRORS = (ValueError, ZeroDivisionError, KeyError, IndexError, TypeError)

# --------------------------------------------------------------------------- #
# The content model
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Table:
    """One rendered table: a caption, column headers and pre-formatted cells.

    Cells are **strings**: the content layer owns formatting (and therefore the
    unit conversion and the limit->ultimate scaling), so the renderer cannot
    accidentally reformat a load. ``units`` belong in the column header, never in
    the cell (§3.5).

    ``status_column`` names a column whose value classifies the row (the coverage
    matrix's ``Status``); the renderer uses it to make "not analysed" rows
    visually distinct, which §4.4 requires.
    """

    title: str
    columns: List[str]
    rows: List[List[str]]
    note: str = ""
    small: bool = False
    status_column: str = ""
    #: Relative path of a generated ``.tex`` fragment holding this table's body,
    #: for a report delivered as a **package** (design note 44 OR-23). Empty --
    #: the default, and what every summary-report table uses -- means the rows
    #: are written inline, which is what ``SUMMARY_REPORT.md`` §2 requires of a
    #: standalone ``.tex``. Carrying the mode on the table rather than on the
    #: document is deliberate: a packaged report still writes its title-block and
    #: control tables inline, so "external" is a property of one table's data,
    #: never of the document.
    data_ref: str = ""
    #: The ``data/`` file of the issue package that already carries this table's
    #: numbers, or empty (#245).
    #:
    #: Set by the producer where a **named** deliverable covers the table --
    #: ``wing_applied_loads.csv`` covers Appendix B.1, ``vn_conditions.csv``
    #: covers Appendix A's two condition tables. The package's data emitter reads
    #: it as "do not write this table again": a generically emitted copy of a
    #: table a named file already carries would be a second file of the same
    #: numbers under a name nothing cites, which is the duplication ``data/``
    #: exists to end.
    #:
    #: Distinct from :attr:`data_ref`, which is a *typeset* ``.tex`` fragment the
    #: document ``\input``s. This names a CSV the reader opens; the two answer
    #: different questions and a table can set either, both, or neither.
    data_file: str = ""


@dataclass(frozen=True)
class Series:
    """One named polyline of a figure. ``style`` is a line style, never a colour --
    figures must stay legible in greyscale (§4.3).

    ``closed`` says the polyline bounds a **region** -- a planform outline, a
    control surface -- rather than tracing a line through the figure. An emitter
    that fills or closes a path reads it; the default is an ordinary open
    polyline, which is what every plotted curve is. It exists because a planform
    figure carries both kinds at once: the wing outline is a closed region and
    the loads reference axis drawn on it is not, and closing the axis would cut
    a chord from tip back to root that no part of the airplane follows.
    """

    name: str
    x: List[float]
    y: List[float]
    style: str = "solid"
    closed: bool = False
    #: The series is a **cloud of points**, not a polyline: an emitter draws a
    #: mark at each vertex and no connecting line.
    #:
    #: Added at #268, when the fleet comparison became the first figure in the
    #: model that is a scatter rather than a curve. Carried on the series rather
    #: than inferred (from an unsorted ``x``, say) because whether a set of
    #: points is a line is the producer's statement about its own data: an
    #: airplane placed against thirty-eight others is a scatter even when the
    #: points happen to arrive in order, and a load distribution is a line even
    #: where two stations share a station value.
    marker: bool = False
    #: Per-vertex identity, parallel to :attr:`x` and :attr:`y`, or empty.
    #:
    #: What each point *is* -- an aircraft name on a fleet scatter -- as opposed
    #: to what the series is called. A screen renderer shows it on demand
    #: (hover), which is the whole use: the question a scatter provokes is
    #: "which one is that?". A printed emitter ignores it, deliberately --
    #: a node label on every point of a cloud is not a figure -- so this is the
    #: one member of the model the two renderers do not both honour, and it is
    #: allowed to be because it carries no data the figure's geometry needs.
    labels: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class PlotData:
    """The data of one figure, in the renderer-agnostic form ``plots_tex`` consumes."""

    x_label: str
    y_label: str
    series: List[Series] = field(default_factory=list)
    #: Labelled point markers (e.g. the design CG cases).
    points: List[Tuple[str, float, float]] = field(default_factory=list)
    #: Labelled vertical reference lines (e.g. the fwd/aft CG limits).
    vlines: List[Tuple[str, float]] = field(default_factory=list)
    #: Whether the axis is logarithmic. Stated by the producer, because it is a
    #: property of the quantity and not of the renderer: a fleet spanning 1,300
    #: to 41,000 lb has its whole general-aviation half in the first inch of a
    #: linear axis, and both renderers must make the same choice about it or the
    #: printed figure and the screen figure stop being the same picture.
    log_x: bool = False
    log_y: bool = False
    #: The legend entry :attr:`points` are drawn under.
    #:
    #: Defaulted to the weight/CG figure's wording, which was the only user when
    #: the marker series was written and which had it hard-coded in the emitter.
    #: The oracle report's V-n diagrams mark gust design points with the same
    #: mechanism, and inheriting a legend that named somebody else's figure was
    #: how that showed up (GUI review, 2026-08-30).
    points_label: str = "Design CG cases"


@dataclass(frozen=True)
class Figure:
    """A figure plus the corner-point table §4.3 requires beside it.

    ``data is None`` means the figure could not be built; ``absent_reason`` then
    says why, and the section renders that sentence instead of an empty axis.

    There is deliberately no ``data_ref`` here yet, though :attr:`Table.data_ref`
    exists: an axis that reads a shipped CSV has to name the *columns* it plots,
    and that schema is defined by the emitter that writes the first plotted
    section's data. Adding the field before the schema exists would be guessing
    at it in the one place a wrong guess is expensive to undo.
    """

    key: str
    title: str
    data: Optional[PlotData] = None
    caption: str = ""
    absent_reason: str = ""
    #: Which **figure family** this instance belongs to (note 60 D-60.2/D-60.4).
    #:
    #: A key identifies one drawing; a family identifies the *kind* of drawing,
    #: and the two differ wherever a producer emits a run of instances -- ``vn_0
    #: ... vn_14`` is one family at fifteen keys, and so are the per-tab
    #: pressures, the per-case attitudes and the OEI histories. The figure
    #: catalogue (:mod:`sloads.report.figures`) is keyed by family, because what
    #: a GUI page offers is the kind of figure, not an instance number that
    #: depends on how many CG cases a project happens to carry.
    #:
    #: Defaulted to :attr:`key` below, so a single-instance producer states
    #: nothing and a multi-instance one must: the common case costs no edit and
    #: the case that can drift is the one required to declare itself. Carried as
    #: data rather than pattern-matched out of the key by the guard -- a guard
    #: that parses ``vn_0`` into ``vn`` is guessing at a convention nothing
    #: enforces, and it would be the guard, not the producer, that decided what
    #: a family is.
    family: str = ""

    def __post_init__(self) -> None:
        if not self.family:
            object.__setattr__(self, "family", self.key)


@dataclass
class Section:
    """One numbered section: prose paragraphs, tables, figures, subsections."""

    title: str
    body: List[str] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    figures: List[Figure] = field(default_factory=list)
    subsections: List["Section"] = field(default_factory=list)
    absent_reason: str = ""
    #: The bold lead the renderer puts in front of ``absent_reason``.
    #:
    #: Defaults to the summary report's single reason for a missing section --
    #: it was not analysed. The oracle report has *four* section states (design
    #: note 44 OR-32) that must not borrow each other's wording, because each
    #: names a different party's decision: leading a not-yet-implemented section
    #: with "Not analysed" tells the reader their data was incomplete when it was
    #: the tool that was.
    absent_lead: str = "Not analysed"
    #: Start this section on a fresh page. Back matter is reference material a
    #: reader turns to rather than reads through, so an appendix that begins
    #: halfway down the last page of the section before it reads as a
    #: continuation of it. Set by the appendix builder, not by section content.
    page_break: bool = False
    #: Render this section rotated. A station-by-station applied-load table is
    #: wide because a load needs its point as well as its components, and
    #: shrinking the type to fit is the wrong trade for a table meant to be read
    #: number by number. Applies to the whole section, so one appendix has one
    #: orientation throughout.
    landscape: bool = False

    @property
    def table(self) -> Optional[Table]:
        """The section's first table (the common case), or ``None``."""
        return self.tables[0] if self.tables else None

    def subsection(self, title: str) -> Optional["Section"]:
        """The direct subsection whose title matches ``title`` (case-insensitive)."""
        for s in self.subsections:
            if s.title.lower() == title.lower():
                return s
        return None


# --------------------------------------------------------------------------- #
# Unit helpers -- one resolved set per document (M4-20)
# --------------------------------------------------------------------------- #
#: Dimensions the deliverable unit set does not carry, because they are not load
#: dimensions: (Imperial->SI factor, Imperial label, SI label). The factors are
#: ``units.HUMAN_SI``'s (the one owner, CH-7); only the ASCII labels a report
#: prints live here.
_EXTRA_DIMENSIONS = {
    "mass": (HUMAN_SI["mass"].factor, "lb", "kg"),
    "area": (HUMAN_SI["area_sqft"].factor, "ft^2", "m^2"),
    "inertia": (HUMAN_SI["inertia_slugft2"].factor, "slug-ft^2", "kg*m^2"),
    "inertia_lbin2": (HUMAN_SI["inertia_lbin2"].factor, "lb-in^2", "kg*m^2"),
}

_IMPERIAL_HUMAN: DeliverableUnits = deliverable_units(UnitSystem.IMPERIAL, Channel.HUMAN)


class Units:
    """The document's resolved unit set, plus the conversions the tables need.

    One instance per document, built from ``deliverable_units(system,
    Channel.HUMAN)`` -- the report is a human-readable deliverable, so it reports
    moments in N*m and pressures in kPa, never the solver deck's N*mm/MPa (D-19).
    Imperial is the all-1.0 identity, so an Imperial report is byte-for-byte what
    it was before M4-20.
    """

    def __init__(self, system: UnitSystem) -> None:
        self.system = system
        self.d: DeliverableUnits = deliverable_units(system, Channel.HUMAN)

    # -- plain (non-load) quantities: converted, never scaled, never marked --- #
    def plain(self, value: Any, dim: str) -> str:
        """A non-load quantity formatted in the document's units (no ``-ULT``).

        ``value`` is typed loosely because an absent quantity reaches here as
        ``None`` *or* as the empty string the result types use for "this
        component does not apply"; both render as an empty cell rather than a
        zero, which would read as a measurement.
        """
        if value is None or value == "":
            return ""
        return format_value(value * self._factor(dim), self.precision_key(dim))

    def precision_key(self, dim: str) -> str:
        """The unit string of ``dim`` in the document's own system -- the key a
        cell's delivered precision is read by. An SI cell reads the SI row,
        which resolves no coarser than the Imperial cell it converted from
        (note 65 D-65.5 as amended at #298); until then this returned the
        Imperial label whatever the system, and a 31.2 ft² tail printed as
        ``3`` m²."""
        return self.label(dim)

    def label(self, dim: str) -> str:
        """The plain unit label for ``dim`` (``"in"``/``"mm"``, ``"lb"``/``"kg"``...)."""
        if dim in _EXTRA_DIMENSIONS:
            _, imperial, si = _EXTRA_DIMENSIONS[dim]
            return imperial if self.system == UnitSystem.IMPERIAL else si
        return getattr(self.d, dim).label

    def ult_label(self, dim: str, sf: float = 0.0) -> str:
        """The unit label for a load dimension.

        LIMIT is the project's only basis (note 49 OR-116), so a load's label is
        plain and its factor is stated in the row's ``SF`` cell. A load computed
        **already ultimate** (``sf == 1.0``) keeps the ``-ULT`` marker, which is
        now rare enough to be conspicuous (OR-118).
        """
        label = getattr(self.d, dim).label
        return ultimate_units(label) if sf == 1.0 else label

    def load(self, value: Any, dim: str, sf: Optional[float]) -> str:
        """A LIMIT load, converted only -- ``sf`` is stated, not applied (OR-116).

        Same loose typing as :meth:`plain`, for the same reason. ``sf`` is
        ``Optional`` for a plainer one: the factor is never applied here, so a
        condition that prescribes none (``None``, #154) is a legal caller and
        need not invent a number to get through the boundary (#180).
        """
        if value is None or value == "":
            return ""
        return format_value(self.load_value(value, dim, sf), self.precision_key(dim))

    # -- the same two conversions as numbers, for a figure's axis ------------ #
    #
    # A plotted load goes through the boundary exactly as a tabulated one does:
    # the figure and the table beside it are then the same number drawn two
    # ways, and neither can be the one that forgot to scale.
    def load_value(self, value: float, dim: str, sf: Optional[float]) -> float:
        """A LIMIT load in the document's units.

        ``sf`` is retained in the signature because every caller has it and the
        row states it; it is **not** applied (note 49 OR-116).
        """
        del sf  # stated by the caller's SF cell, never applied
        return value * getattr(self.d, dim).factor

    def plain_value(self, value: float, dim: str) -> float:
        """A non-load quantity as a number in the document's units."""
        return value * self._factor(dim)

    def _factor(self, dim: str) -> float:
        if dim in _EXTRA_DIMENSIONS:
            return 1.0 if self.system == UnitSystem.IMPERIAL else _EXTRA_DIMENSIONS[dim][0]
        return getattr(self.d, dim).factor


# --------------------------------------------------------------------------- #
# Component loads -- the live recompute the report and the bundle share
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ComponentLoads:
    """The four distributed-load families, recomputed from the current inputs.

    The Export page and the report build these the same way, through this one
    function, so a bundle's report can never describe different numbers from the
    CSV/BDF files beside it. Wing results are already transferred to the wing's
    loads reference axis (LRA) -- every reported wing torsion is about that axis.
    """

    wing: List[Any] = field(default_factory=list)
    body: List[Any] = field(default_factory=list)
    tail: List[Any] = field(default_factory=list)
    control: List[Any] = field(default_factory=list)
    #: SELECT's governing conditions, through the owner
    #: (``select.default_critical``): the persisted ``Project.envelope.critical``
    #: when the project carries one, else SELECT's own search run fresh -- which
    #: covers the project loaded from JSON that carries no envelope at all.
    #: Re-pointed at #272. It read ``build_critical`` directly until then, to
    #: recompute live "exactly as the Critical Loads and Results Review pages
    #: do"; those pages went with ``app/`` at #270, and the bypass outlived the
    #: reason for it. The owner is what carries note 44 OR-172's admission, so
    #: a consumer that skips it gets a fin set short its governing case.
    critical: List[Any] = field(default_factory=list)


def _try(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except _CALC_ERRORS:
        return None


def component_loads(project: Project) -> ComponentLoads:
    """Recompute the wing / fuselage / tail / control-surface distributed loads.

    Defensive by design: a component whose inputs are absent yields an empty list
    rather than an exception, so a partially-filled project still reports on the
    components it *can* cover.
    """
    from ..modules.aileron import build_aileron
    from ..modules.body_loads import build_body_loads
    from ..modules.flap import build_flap
    from ..modules.net_loads import build_net_loads, loads_ref_axis_results
    from ..modules.select import default_critical
    from ..modules.tab import build_tabs
    from ..modules.taildist import build_tail_chordwise
    from ..safety_factors import stamp

    critical = _try(default_critical, project)
    net = _try(build_net_loads, project)
    wing = loads_ref_axis_results(project, net.wing_net) if net is not None else None
    control: List[Any] = []
    for fn in (build_aileron, build_flap, build_tabs):
        control += _try(fn, project) or []
    out = ComponentLoads(
        wing=wing or [],
        body=_try(build_body_loads, project) or [],
        tail=_try(build_tail_chordwise, project) or [],
        control=control,
        critical=list(critical.conditions) if critical is not None else [],
    )
    # The governing safety-factor table is written onto the carrier here, at the
    # one boundary every front-end shares (M4-8 / G-11). Without this a project
    # override would move the report's SF column and leave the deck's SF= marker
    # and its scaled cards behind it -- the defect class review finding F-R1
    # closed. With no override (every shipped fixture) it is a no-op that writes
    # back exactly the factor the producer minted.
    stamp(project, out.wing, out.body, out.tail, out.control, out.critical)
    return out


#: The structural-limit corners, in the order they close the polygon.
#:
#: The forward limit is **piecewise**: constant at the forward-regardless station
#: below the reduced weight, then linear in weight up to the forward-gross
#: station at gross (`PROGRAM_SPEC` WTENV / M4-17c, the same relation
#: ``validation.wtenv_fwd_cg_limit_at_weight`` evaluates). Joining the anchors
#: with a straight segment *is* that interpolation, so the polygon is five WTENV
#: outputs connected, not a sixth quantity computed here.
_LIMIT_CORNERS = (
    ("forward_regardless_station", None),
    ("forward_regardless_station", "forward_regardless_point_weight"),
    ("forward_gross_station", "aft_gross_point_weight"),
    ("aft_gross_station", "aft_gross_point_weight"),
    ("aft_gross_station", None),
)


def _limit_polygon(values: Dict[str, float], floor: float,
                   len_f: float, mass_f: float) -> Optional[Series]:
    """The closed structural-limit envelope, or ``None`` if a corner is missing.

    ``floor`` is the minimum flight weight -- the bottom edge. A limit the
    airplane has no entry for leaves the polygon undrawn rather than half drawn:
    a limit envelope missing a side reads as permission, which is the one way
    this figure could mislead.
    """
    try:
        corners = [(values[x], floor if w is None else values[w])
                   for x, w in _LIMIT_CORNERS]
    except KeyError:
        return None
    if any(w <= 0 for _x, w in corners):
        return None
    corners.append(corners[0])          # close it
    return Series("Structural limits", [x * len_f for x, _w in corners],
                  [w * mass_f for _x, w in corners], style="densely dotted")


#: The Mach-limited boundaries drawn, by MACHLIM's own value keys.
#:
#: Declared as data and guarded against those keys, so a renamed key empties the
#: figure in the suite rather than on the page. Styles, never colours (SS 4.3).
_SPEED_ALTITUDE_LINES: Tuple[Tuple[str, str, str], ...] = (
    ("V(MC) cruise", "v_mc", "solid"),
    ("V(MNE) never-exceed", "v_mne", "dashed"),
    ("V(MD) dive", "v_md", "dotted"),
)


def speed_altitude_plot_data(project: Project) -> Optional[PlotData]:
    """The speed/altitude envelope figure's data -- the one owner (OR-7).

    Sea level to the maximum operating altitude, which is the whole operating
    envelope rather than its Mach-limited top: each boundary is **constant in
    EAS below the shoulder altitude and Mach-limited above it**, and the kink
    between the two is the point of the figure. The sub-shoulder segment adds no
    arithmetic -- it is the shoulder row's own speed held constant down to sea
    level, which is what "the shoulder altitude" means -- so every speed drawn
    is a value MACHLIM returned.

    ``Vh`` is marked, not drawn as a line: ``speeds.vh_kt`` is the maximum level
    flight speed **at sea level** and the analysis carries no altitude variation
    of it, so a full-height line would assert a boundary nothing computed. As a
    sea-level marker it still shows the thing worth seeing -- where Vh sits
    against VC, whose FAR floor is capped at 0.9 Vh (14 CFR 23.335(a)).

    Speeds are KEAS and altitudes feet in every unit system: the aviation
    channel is not converted (see :data:`AVIATION_UNITS_NOTE`). ``None`` when
    the airplane has no Mach-limited boundary to draw.
    """
    from ..modules.mach_limit import mach_limit_lines
    from ..modules.structural_speeds import design_speed_values

    speeds = project.speeds
    ml = speeds.mach_limit if speeds is not None else None
    if speeds is None or ml is None:
        return None
    # MC/MD come from STRSPEED, the single producer (F25-2) -- not from ``ml``.
    ds = _try(design_speed_values, project, speeds)
    results = (_try(mach_limit_lines, ml, ds.mc, ds.md, speeds.shoulder_altitude_ft)
               if ds is not None else None)
    if not results:
        return None

    rows = [{v.key: v.value for v in r.values} for r in results[1:]]
    if not rows:
        return None
    shoulder = float(speeds.shoulder_altitude_ft)

    series = []
    for name, key, style in _SPEED_ALTITUDE_LINES:
        vs = [row[key] for row in rows if key in row]
        alts = [row["altitude"] for row in rows if key in row]
        if not vs:
            continue
        if shoulder > 0:
            # Constant EAS below the shoulder: the first row's speed, held down
            # to sea level. Not a second computation of it.
            vs.insert(0, vs[0])
            alts.insert(0, 0.0)
        series.append(Series(name, vs, alts, style))
    if not series:
        return None

    points = ([("Vh", float(speeds.vh_kt), 0.0)] if speeds.vh_kt else [])
    return PlotData("V (KEAS)", "Altitude (ft)", series, points=points,
                    points_label="Maximum level-flight speed Vh (sea level)")


def weight_cg_plot_data(project: Project, u: Units) -> Optional[PlotData]:
    """The weight/CG envelope figure's data -- the one owner (OR-7).

    Both loading edges (note 45: ``WTENV.BAS`` sweeps its discretionary items
    ascending *and* descending), the closed structural-limit polygon, and every
    entered CG case as a labelled marker. Shared by the summary report and the
    oracle technical report so the two documents cannot draw the same airplane
    two ways. ``None`` when there is no weight data base to sweep.

    Drawing only the forward edge -- which is what this figure did until note 45
    -- shows the half that approaches no limit and hides the half that can
    exceed one, so the containment reading a reader takes from it would be wrong
    rather than merely partial.
    """
    from ..modules.weight_envelope import envelope as weight_envelope
    from ..modules.weight_envelope import loading_envelope

    weight = project.weight
    env_in = weight.envelope if weight is not None else None
    forward = _try(loading_envelope, project) or []
    if not forward:
        return None
    aft = _try(loading_envelope, project, aft=True) or []

    L, W = u.label("length"), u.label("mass")
    len_f = u.d.length.factor
    mass_f = 1.0 if u.system == UnitSystem.IMPERIAL else _EXTRA_DIMENSIONS["mass"][0]

    def edge(name: str, vertices, style: str) -> Series:
        return Series(name, [v.station * len_f for v in vertices],
                      [v.weight * mass_f for v in vertices], style=style)

    series = [edge("Forward loading envelope", forward, "solid")]
    if aft:
        series.append(edge("Aft loading envelope", aft, "dashed"))

    values: Dict[str, float] = {}
    if env_in is not None:
        for r in _try(weight_envelope, project, env_in) or []:
            for v in r.values:
                values.setdefault(v.key, v.value)
    polygon = _limit_polygon(values, forward[0].weight, len_f, mass_f)
    if polygon is not None:
        series.append(polygon)

    # Cases sharing a point are one marker with both names: on the GA6 the
    # forward-light landing case and CG3 are the same loading, and two labels
    # stacked on one diamond is a smudge, not information.
    marked: Dict[Tuple[float, float], List[str]] = {}
    for c in (weight.cg_cases if weight is not None else []):
        marked.setdefault((c.xcg * len_f, c.weight_lb * mass_f), []).append(c.name)
    points_marked = [(" / ".join(names), x, y)
                     for (x, y), names in marked.items()]

    return PlotData(f"Fuselage station ({L})", f"Weight ({W})", series,
                    points=points_marked)


#: The marker shape each loading kind is drawn with, and the order the legend
#: lists them in. Shape rather than colour, for §4.3's greyscale rule: three
#: clouds of identical dots would be one cloud on a printed page.
_ITEM_KINDS: Tuple[Tuple[str, str, str], ...] = (
    ("empty", "Empty weight", "mark=*"),
    ("minimum", "Minimum flight weight", "mark=square*"),
    ("discretionary", "Discretionary useful load", "mark=triangle*"),
)


def item_station_plot_data(project: Project, u: Units) -> Optional[PlotData]:
    """Each mass item's weight against its fuselage station, by loading kind.

    The figure note 60 §1.1 counted as #6 and #267 could not port, the model
    having had no way to say "a cloud of named points" until #268 added one.
    It is the weight data base drawn: where the mass sits along the body, which
    is how an item entered at the wrong station is seen rather than computed
    around. Split by :class:`~sloads.models.enums.MassItemKind` because *when*
    an item is aboard is the first question a reader has about a mass at an
    extreme station -- a heavy nose item that is discretionary is a loading, a
    heavy nose item that is empty weight is the airplane.

    ``None`` when the data base is empty: there is nothing to draw, and the
    caller says so rather than printing an empty axis.

    The item names ride on :attr:`Series.labels`, so the screen names each point
    on hover and the printed figure does not try to. A stem plot -- the shape
    the retiring GUI drew -- would need a member of its own; a labelled point at
    the same coordinates carries the same reading, which is why this ports now
    and did not at #267.
    """
    weight = project.weight
    items = list(weight.items) if weight is not None else []
    if not items:
        return None

    L, W = u.label("length"), u.label("mass")
    len_f = u.d.length.factor
    mass_f = 1.0 if u.system == UnitSystem.IMPERIAL else _EXTRA_DIMENSIONS["mass"][0]

    series = []
    for value, name, style in _ITEM_KINDS:
        rows = [i for i in items if str(getattr(i.kind, "value", i.kind)) == value]
        if not rows:
            continue
        series.append(Series(
            name, [i.x * len_f for i in rows], [i.weight_lb * mass_f for i in rows],
            style=style, marker=True, labels=[i.name for i in rows]))
    if not series:
        return None
    return PlotData(f"Fuselage station ({L})", f"Item weight ({W})", series)


__all__ = [
    "ComponentLoads",
    "Figure",
    "PlotData",
    "Section",
    "Series",
    "Table",
    "Units",
    "component_loads",
    "item_station_plot_data",
    "speed_altitude_plot_data",
    "weight_cg_plot_data",
]
