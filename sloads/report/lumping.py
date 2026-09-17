"""What re-aggregating the applied set onto the beam costs the distribution.

Design note 56 **D-56.10**, ruling 14. ``report.applied.aggregate_to_lra``
sums every load station and every concentrated mass onto the nearest node of
its member (D-56.9, ruling 13), each with the exact lever-arm couple, so the
**resultant** of the set is unchanged -- per case, per component, to the last
bit, and gate 13 asserts it. What moves is the **distribution**: a load that
crosses a cut on its way to its assigned node takes its contribution to the
internal shear, bending and torsion at that cut with it.

That is a real discretization difference and it is not a defect. The beam mesh
is decided from geometry alone (D-56.4) precisely so that the generated model
is one instance of the contract an imported user model obeys, rather than a
degenerate special case welded to the load stations. The size of the difference
is therefore a legitimate function of a user-settable grid count
(``Project.lra_mesh``), which is why it is **stated and plotted and not gated
with a tolerance** (ruling 15). The identity beside it -- the resultant -- stays
exact and gated.

**No solver is in the loop.** Both curves are computed here, from the two load
sets, about the same cuts. That makes the comparison a *discretization*
comparison and not an *idealisation* one: a reader looking at the gap is
looking at the lumping and at nothing else, and it is reproducible in CI. The
rejected alternative -- compare against sbeam's solved internal loads -- puts
the solver's own idealisation into the same picture and leaves a reader unable
to tell which of the two they are seeing.

The internal load at a cut
--------------------------
One rule for both curves and for every component: the internal load at a cut is
the **static resultant of everything outboard of it, transferred to the cut
point** -- the same LM-1 transfer the aggregation itself uses
(:func:`sloads.gear_loads.transfer_couple`), the same rule
:func:`sloads.report.applied.sob_internal_loads` states at the single
side-of-body cut. Nothing here re-derives a beam integration: an internal load
*is* a resultant about a point, and writing it that way is what lets one
function serve a wing, a fuselage, a horizontal tail and a fin without a
per-component integration path to keep in step.

The cuts are the member's **own nodes**, and both curves are computed about the
same ones. A cut is at a point, so a torsion compared between two sets is only
meaningful if both are stated about that point.

"Outboard" is the member's own span coordinate increasing: butt line on the
wing and horizontal tail (right side; the left is its mirror), waterline on the
fin, fuselage station on the body. A load lying exactly at the cut counts as
outboard -- the cut carries what is applied at it -- which is
:func:`~sloads.report.applied.sob_internal_loads`' own rule and keeps the root
cut's value equal to the whole member's resultant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from ..models import Project
from ..picks import extreme

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ..export.lra_model import LraModel
    from .applied import AppliedLoad

Vec3 = Tuple[float, float, float]

#: A load at the cut counts as outboard of it, to within this much length.
_AT_THE_CUT = 1e-9


@dataclass(frozen=True)
class Channels:
    """Which airplane components are this member's shear, bending and torsion.

    A beam's three internal channels are the same three ideas everywhere and
    different airplane axes each time, so the mapping is data and not a branch
    per component. ``shear`` indexes ``(Fx, Fy, Fz)``; ``bending`` and
    ``torsion`` index ``(Mx, My, Mz)``. The symbols are the airplane-axis ones
    the applied appendices print, so a reader can follow a column from the
    appendix into this comparison without a second notation to learn.
    """

    shear: int
    bending: int
    torsion: int
    shear_symbol: str
    bending_symbol: str
    torsion_symbol: str


#: member key, the span coordinate's index in ``(x, y, z)``, the channels, and
#: whether the member's cuts are restricted to the non-negative side.
#:
#: The wing and the horizontal tail are drawn on the **right** side only: the
#: left is its mirror on every case the suite runs, and two curves that are one
#: curve reflected say nothing the one curve does not. The fin spans in z. The
#: fuselage is not a cantilever and does not need to be -- the resultant of
#: everything aft of a station, about that station, is the internal load there
#: whichever side of the carry-through it falls on.
_MEMBERS: Dict[str, Tuple[str, int, Channels, bool]] = {
    "wing": ("wing-R", 1,
             Channels(2, 0, 1, "Fz", "Mx", "My"), True),
    "htail": ("htail", 1,
              Channels(2, 0, 1, "Fz", "Mx", "My"), True),
    "vtail": ("vtail", 2,
              Channels(1, 0, 2, "Fy", "Mx", "Mz"), False),
    "fuselage": ("fuselage", 0,
                 Channels(2, 1, 0, "Fz", "My", "Mx"), False),
}

#: The components the comparison is drawn for, in the order the report draws
#: them. The point-load components (``landing_gear``, ``engine``) are absent
#: because they are not re-aggregated at all -- their rows pass through
#: untouched -- so there is nothing for them to cost.
COMPONENTS: Tuple[str, ...] = ("wing", "fuselage", "htail", "vtail")

#: What each channel is called in prose and in a legend.
CHANNEL_NAMES: Tuple[Tuple[str, str], ...] = (
    ("shear", "V"), ("bending", "M"), ("torsion", "T"))


@dataclass(frozen=True)
class Cut:
    """One station the internal load is stated at: where it is, and its point."""

    s: float
    pos: Vec3
    gid: int


@dataclass(frozen=True)
class Curve:
    """One load set's internal loads along one member, at the shared cuts."""

    s: List[float] = field(default_factory=list)
    shear: List[float] = field(default_factory=list)
    bending: List[float] = field(default_factory=list)
    torsion: List[float] = field(default_factory=list)

    def channel(self, name: str) -> List[float]:
        return {"shear": self.shear, "bending": self.bending,
                "torsion": self.torsion}[name]


@dataclass(frozen=True)
class CaseComparison:
    """The two curves for one case of one component, and their difference."""

    case: str
    station: Curve
    lumped: Curve
    #: The factor 14 CFR 23.303 prescribes for this case -- **stated, applied to
    #: nothing** (OR-116), exactly as every other row of every other table
    #: states it. A deviation is a difference of two LIMIT loads and is
    #: therefore LIMIT itself. No default: the one caller reads it off the
    #: applied rows, and a default of 0.0 would print an SF no regulation
    #: prescribes if that read were ever skipped (#180 residue, 0.8.5 review).
    safety_factor: float

    def deviation(self, channel: str) -> List[float]:
        """``lumped - station``, cut by cut, in the raw Imperial channel."""
        return [lump - stn for lump, stn
                in zip(self.lumped.channel(channel),
                       self.station.channel(channel))]

    def worst(self, channel: str) -> Tuple[float, float, float]:
        """``(deviation, s, reference)`` at the cut where the gap is widest.

        ``reference`` is the station curve's own peak magnitude along the
        member, not its value at that cut: a deviation is read against what the
        member carries, and dividing by a value that is near zero at the tip
        would report a hundred per cent of nothing.
        """
        station = self.station.channel(channel)
        reference = max((abs(v) for v in station), default=0.0)
        pairs = list(zip(self.deviation(channel), self.station.s))
        if not pairs:
            return (0.0, 0.0, reference)
        gap, s = extreme(pairs, lambda p: abs(p[0]))
        return (gap, s, reference)


@dataclass(frozen=True)
class ComponentComparison:
    """Every case of one component, plus the member the cuts were taken on."""

    component: str
    member: str
    channels: Channels
    cases: List[CaseComparison] = field(default_factory=list)

    def case(self, case_id: str) -> Optional[CaseComparison]:
        return next((c for c in self.cases if c.case == case_id), None)

    def worst(self, channel: str) -> Tuple[str, float, float, float]:
        """``(case, deviation, s, reference)`` -- the widest gap over **all** cases.

        The figures are drawn for one case so that four components can be read
        together (D-56.10); the number beside them is over every case, because a
        reader asking "how much does this cost me" is not asking about the case
        that happened to be plotted.
        """
        if not self.cases:
            return ("", 0.0, 0.0, 0.0)
        ranked = [(c.case,) + c.worst(channel) for c in self.cases]
        return extreme(ranked, lambda r: abs(r[1]))


def _cuts(model: "LraModel", component: str) -> List[Cut]:
    """The member's own nodes, ordered along its span coordinate."""
    key, axis, _channels, right_only = _MEMBERS[component]
    nodes = model.members.get(key) or []
    picked = [n for n in nodes if not right_only or n.pos[axis] >= 0.0]
    out = [Cut(s=n.pos[axis], pos=n.pos, gid=n.gid) for n in picked]
    return sorted(out, key=lambda c: c.s)


def _curve(rows: Sequence[object], cuts: Sequence[Cut], axis: int,
           channels: Channels) -> Curve:
    """``rows``' internal loads at ``cuts``: the outboard resultant, transferred."""
    from ..gear_loads import transfer_couple
    from .applied import applied_body_moments

    loads: List[Tuple[float, Vec3, Vec3, Vec3]] = []
    for row in rows:
        p = (row.x, row.y, row.z)          # type: ignore[attr-defined]
        f = (row.fx, row.fy, row.fz)       # type: ignore[attr-defined]
        loads.append((p[axis], p, f, applied_body_moments(row)))  # type: ignore[arg-type]

    curve = Curve()
    for cut in cuts:
        force = [0.0, 0.0, 0.0]
        moment = [0.0, 0.0, 0.0]
        for s, p, f, m in loads:
            if s < cut.s - _AT_THE_CUT:
                continue
            couple = transfer_couple(p, cut.pos, f)
            for i in range(3):
                force[i] += f[i]
                moment[i] += m[i] + couple[i]
        curve.s.append(cut.s)
        curve.shear.append(force[channels.shear])
        curve.bending.append(moment[channels.bending])
        curve.torsion.append(moment[channels.torsion])
    return curve


def _by_case(rows: Sequence["AppliedLoad"]) -> Dict[str, List["AppliedLoad"]]:
    out: Dict[str, List["AppliedLoad"]] = {}
    for row in rows:
        key = row.case_id or row.case
        out.setdefault(key, []).append(row)
    return out


def compare(project: Project, component: str,
            results: object) -> Optional[ComponentComparison]:
    """The lumping comparison for one component, or ``None`` when there is none.

    ``None`` -- rather than an empty comparison -- whenever the question cannot
    be asked: no results, no beam (the project is missing a datum the model must
    not guess), or a member the mesh did not build. A report section turns that
    into a stated absence; it is not an error, and G-OR-7 keeps a half-filled
    project building a complete document.
    """
    from ..export.lra_model import build_lra_model
    from .applied import aggregate_to_lra, station_applied_loads

    if component not in _MEMBERS:
        raise ValueError(f"no beam member is defined for {component!r}")
    if not results:
        # Asked before the producer ran, or of a project that produced nothing
        # for this surface. The producers refuse an empty argument by raising
        # (``no spanwise htail results to export``), which is right for an
        # export and wrong here: a document section asking "what did the
        # lumping cost?" of a component with no loads has its answer, and it is
        # not an exception.
        return None
    station_rows = station_applied_loads(component, results, project)
    if not station_rows:
        return None
    try:
        model = build_lra_model(project)
    except ValueError:
        # The same refusal ``applied_loads`` absorbs: with no beam there are no
        # grids, the delivered set is the station set, and the lumping costs
        # nothing because no lumping happened.
        return None
    cuts = _cuts(model, component)
    if len(cuts) < 2:
        return None
    lumped_rows = aggregate_to_lra(station_rows, model, component)
    _member, axis, channels, _right_only = _MEMBERS[component]

    station_cases = _by_case(station_rows)
    lumped_cases = _by_case(lumped_rows)
    cases = [
        CaseComparison(case=case,
                       station=_curve(rows, cuts, axis, channels),
                       lumped=_curve(lumped_cases.get(case, []), cuts, axis,
                                     channels),
                       # Read off the row, not defaulted: every AppliedLoad
                       # mints the field (M4-13/M4-16), and a fallback here
                       # would print SF 0 -- a factor no regulation prescribes
                       # -- if the field were ever renamed (#180).
                       safety_factor=rows[0].safety_factor)
        for case, rows in station_cases.items()]
    return ComponentComparison(component=component, member=_MEMBERS[component][0],
                               channels=channels, cases=cases)


def critical_case(comparison: ComponentComparison) -> str:
    """The case a component's figure is drawn for: its most heavily bent one.

    **This is one case per component, not one case for the four**, which amends
    D-56.10 as first written. The intent there -- four figures a reader takes in
    together, all showing the same instant of flight -- cannot be honoured,
    because the four components' condition registers are disjoint by
    construction: the wing runs ``W-nn``, the fuselage ``F-nn``, the horizontal
    tail ``HT-nn`` and the fin ``VT-nn``, each surface's own FAR conditions, and
    no case is run by more than one of them. There is no case to share. Drawing
    a common one would mean inventing a correspondence between conditions the
    analysis does not claim.

    So each figure names its own, and it is the **critical** one in the sense a
    reader means -- the case that bends the member hardest -- rather than the
    case where the lumping happens to be worst. The worst lumping is a separate
    question and gets a separate answer: the deviation table beside the figures
    states it, per channel, over **every** case, and names the case it came
    from. Choosing the plotted case by the quantity being measured would make
    the figure flatter than the airplane whenever the two disagree.

    The candidates are ordered by case id before the pick, and the pick goes
    through :func:`sloads.picks.extreme`, so a project whose two hardest cases
    tie draws the same figure on every platform (CR-B-1).
    """
    if not comparison.cases:
        return ""
    by_id = sorted(comparison.cases, key=lambda c: c.case)
    return extreme(by_id,
                   lambda c: max((abs(v) for v in c.station.bending),
                                 default=0.0)).case


__all__ = [
    "CHANNEL_NAMES",
    "COMPONENTS",
    "CaseComparison",
    "Channels",
    "ComponentComparison",
    "Curve",
    "Cut",
    "compare",
    "critical_case",
]
