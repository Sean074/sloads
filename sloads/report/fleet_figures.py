"""The **fleet comparison's figures** -- one producer, rendered by either front-end.

Design note 57 D-57.5: the Aircraft Comparison page ports to the surviving GUI,
because placing a configuration against similar airplanes is the Phase-C charter
(``01_concept_loads_plan.md`` §1) and not a convenience of the front-end that
happened to carry it. Note 60 D-60.1 decides *how* a figure ports: the data of a
figure has one owner and the renderers are peers over it. This module is that
owner for the six scatters.

**Not in the figure catalogue, and why.** :mod:`sloads.report.figures` is keyed
by workflow step -- every family in it is drawn on the page whose programs
produce it, and the parity gate holds it against the built oracle report. The
fleet comparison is neither: it runs no ``.BAS`` program, it belongs to no step,
and the oracle report is the McMaster replication's document, which has no fleet
section and gains none here. So these figures live beside the catalogue rather
than in it. What does *not* change is the rule the catalogue exists to enforce:
the GUI is handed a ``Figure`` and renders it, and the sixth place a reader
could have found a second figure owner is closed by this file existing.

**Imperial, stated.** The reference fleet is nominal published specifications --
lb, ft, hp -- and is never a FAR input; nothing here is converted, and the page
says so. The unit toggle governs what the analysis reports, and a published
specification is not something this program computed.

**The scatter reached the model, not the renderer.** A fleet figure is a cloud
of points with a name on each and a weight axis spanning thirty times its own
low end. ``Series.marker``, ``Series.labels`` and ``PlotData.log_x``/``log_y``
were added at #268 for exactly that, so the shape is stated in the data both
renderers read rather than arranged by the one that happens to be drawing.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple

from ..fleet import FleetPoint, Subject
from .content import Figure, PlotData, Series

#: The legend names of the two series every fleet figure carries.
FLEET_SERIES = "Reference fleet"
SUBJECT_SERIES = "This airplane"

#: One reader per axis: what a fleet point contributes, and what the subject
#: does. Written as a pair rather than one accessor because ``FleetPoint`` and
#: ``Subject`` are deliberately different records -- a reference aircraft has a
#: published installed power, a subject has whatever its engines add up to --
#: and collapsing them into a common protocol would be inventing a third type
#: to serve six scatter axes.
_Axis = Tuple[str, Callable[[FleetPoint], Optional[float]],
              Callable[[Subject], Optional[float]]]

_MTOW: _Axis = ("MTOW (lb)", lambda p: p.mtow_lb, lambda s: s.mtow_lb)
_OEW: _Axis = ("Empty weight (lb)", lambda p: p.oew_lb or None,
               lambda s: s.oew_lb)
_WS: _Axis = ("Wing loading W/S (lb/ft²)", lambda p: p.w_s, lambda s: s.w_s)
_WP: _Axis = ("Power loading W/P (lb/hp)", lambda p: p.w_p, lambda s: s.w_p)
_SPAN: _Axis = ("Wingspan (ft)", lambda p: p.span, lambda s: s.span)
_AREA: _Axis = ("Wing area (ft²)", lambda p: p.wing_area_ft2 or None,
                lambda s: s.wing_area_ft2)
_AR: _Axis = ("Aspect ratio", lambda p: p.aspect_ratio_effective,
              lambda s: s.aspect_ratio_effective)
_SEATS: _Axis = ("Seats", lambda p: float(p.seats) or None,
                 lambda s: float(s.seats) or None)


def _scatter(fleet: Sequence[FleetPoint], subject: Optional[Subject],
             x: _Axis, y: _Axis, *, log_x: bool = False,
             log_y: bool = False) -> Optional[PlotData]:
    """The two series of one scatter, or ``None`` when neither has a point.

    A point is plotted only where **both** its coordinates exist: an aircraft
    with no published aspect ratio is absent from the aspect-ratio scatter and
    present in every other one, which is the behaviour the page had and the
    reason each axis is asked for its value rather than filtered once up front.
    """
    x_label, x_point, x_subject = x
    y_label, y_point, y_subject = y

    names: List[str] = []
    xs: List[float] = []
    ys: List[float] = []
    for point in fleet:
        px, py = x_point(point), y_point(point)
        if px is None or py is None:
            continue
        names.append(point.name)
        xs.append(float(px))
        ys.append(float(py))

    series: List[Series] = []
    if xs:
        series.append(Series(name=FLEET_SERIES, x=xs, y=ys, marker=True,
                             labels=names))
    if subject is not None:
        sx, sy = x_subject(subject), y_subject(subject)
        if sx is not None and sy is not None:
            series.append(Series(name=SUBJECT_SERIES, x=[float(sx)],
                                 y=[float(sy)], marker=True,
                                 labels=[subject.name]))
    if not series:
        return None
    return PlotData(x_label=x_label, y_label=y_label, series=series,
                    log_x=log_x, log_y=log_y)


def _figure(key: str, title: str, caption: str,
            data: Optional[PlotData]) -> Figure:
    if data is None:
        return Figure(key=key, title=title, absent_reason=(
            "neither this airplane nor the reference fleet supplies both of "
            "this figure's quantities."))
    return Figure(key=key, title=title, data=data, caption=caption)


def fleet_figures(subject: Optional[Subject],
                  fleet: Sequence[FleetPoint]) -> List[Figure]:
    """The six fleet scatters, in the order the page shows them.

    ``subject`` may be ``None`` -- a project with no design weight has no point
    to plot -- and the fleet is still drawn, because the comparators are worth
    seeing before the airplane exists. Every figure is returned either way, so a
    caller renders a fixed set and a missing one says why rather than vanishing.
    """
    return [
        _figure("fleet_wing_vs_power",
                "Wing loading against power loading",
                "Jets carry no shaft power and are absent from this figure.",
                _scatter(fleet, subject, _WS, _WP)),
        _figure("fleet_mtow_vs_empty",
                "Maximum take-off weight against empty weight",
                "Both axes are logarithmic: the fleet spans a factor of thirty "
                "in weight.",
                _scatter(fleet, subject, _OEW, _MTOW, log_x=True, log_y=True)),
        _figure("fleet_span_vs_mtow",
                "Wingspan against maximum take-off weight",
                "Span is the published figure where there is one, else "
                "sqrt(aspect ratio x area).",
                _scatter(fleet, subject, _MTOW, _SPAN, log_x=True)),
        _figure("fleet_area_vs_mtow",
                "Wing area against maximum take-off weight",
                "",
                _scatter(fleet, subject, _MTOW, _AREA, log_x=True)),
        _figure("fleet_aspect_vs_mtow",
                "Aspect ratio against maximum take-off weight",
                "Aircraft with no stored or derivable aspect ratio are absent.",
                _scatter(fleet, subject, _MTOW, _AR, log_x=True)),
        _figure("fleet_seats_vs_mtow",
                "Seats against maximum take-off weight",
                "",
                _scatter(fleet, subject, _MTOW, _SEATS, log_x=True)),
    ]


__all__ = ["FLEET_SERIES", "SUBJECT_SERIES", "fleet_figures"]
