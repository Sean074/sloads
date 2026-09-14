"""The fleet comparison's **shared rendering** -- readout, figures, fleet table.

Design note 57 D-57.5 ported the Aircraft Comparison page to the surviving GUI.
It was written as shared rendering because both front-ends carried the page
until ``app/views/`` retired at #270: everything a page shows is rendered here
and the page supplies only its own framing, which is why the port cost no
duplication. One page frames it now, marking it an sloads extension.

It follows note 60 D-60.1 exactly as the step figures do: it is handed
``Figure`` objects by :mod:`sloads.report.fleet_figures` and ``FleetStats`` by
:mod:`sloads.fleet`, and derives nothing. The tab labels below are the one
judgement it makes, and they are about the width of a tab row.

**Imperial throughout.** The reference fleet is nominal published
specifications, never a FAR input, and is never converted: the unit toggle
governs what the analysis reports, and a published specification is not
something this program computed. Each page says so in its own caption.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import pandas as pd
import streamlit as st

from app_shell.plots import render_figure
from sloads.fleet import FleetPoint, Subject, fleet_stats
from sloads.report.content import Figure

#: The tab each figure is shown under, keyed by ``Figure.key``. Short labels,
#: because six tab titles have to fit on one row; the renderer prints the
#: figure's own title above the axes, so nothing is lost by shortening.
TAB_LABELS: Dict[str, str] = {
    "fleet_wing_vs_power": "W/S vs W/P",
    "fleet_mtow_vs_empty": "MTOW vs empty",
    "fleet_span_vs_mtow": "Span vs MTOW",
    "fleet_area_vs_mtow": "Area vs MTOW",
    "fleet_aspect_vs_mtow": "AR vs MTOW",
    "fleet_seats_vs_mtow": "Seats vs MTOW",
}


def _fmt(value: Optional[float], digits: int = 0) -> Optional[float]:
    """Round for the table, or ``None`` -- rendered blank -- when absent."""
    return None if value is None else round(value, digits)


def _row(name: str, mtow: Optional[float], oew: Optional[float],
         power: Optional[float], w_s: Optional[float], w_p: Optional[float],
         span: Optional[float], area: Optional[float], ar: Optional[float],
         seats: int) -> Dict[str, object]:
    return {
        "Aircraft": name,
        "MTOW (lb)": _fmt(mtow),
        "Empty weight (lb)": _fmt(oew),
        "Power (hp)": _fmt(power),
        "W/S (lb/ft²)": _fmt(w_s, 1),
        "W/P (lb/hp)": _fmt(w_p, 1),
        "Wingspan (ft)": _fmt(span, 1),
        "Wing area (ft²)": _fmt(area),
        "Aspect ratio": _fmt(ar, 2),
        "Seats": seats or None,
    }


def subject_row(subject: Subject) -> Dict[str, object]:
    """One parameter-table row for the airplane being placed."""
    return _row(subject.name, subject.mtow_lb, subject.oew_lb, subject.power_hp,
                subject.w_s, subject.w_p, subject.span, subject.wing_area_ft2,
                subject.aspect_ratio_effective, subject.seats)


def point_row(point: FleetPoint) -> Dict[str, object]:
    """One parameter-table row for a reference aircraft."""
    return _row(point.name, point.mtow_lb, point.oew_lb, point.max_hp,
                point.w_s, point.w_p, point.span, point.wing_area_ft2,
                point.aspect_ratio_effective, point.seats)


def render_readout(subject: Subject, fleet: Sequence[FleetPoint]) -> None:
    """The quantitative placement: the two loading metrics, then the nearest-N.

    A metric the subject cannot supply renders as an em dash with the entry that
    would fill it named in the tooltip -- never as a zero, which would place the
    airplane at the bottom of the fleet on a quantity nobody entered.
    """
    stats = fleet_stats(subject, list(fleet))

    left, right = st.columns(2)
    if subject.w_s is not None and stats.ws_percentile is not None and stats.ws_band:
        left.metric("Wing loading W/S (lb/ft²)", f"{subject.w_s:.1f}",
                    help=(f"{stats.ws_percentile:.0f}th percentile of the fleet; "
                          f"p10–p90 band {stats.ws_band[0]:.1f}–{stats.ws_band[1]:.1f}."))
    else:
        left.metric("Wing loading W/S (lb/ft²)", "—",
                    help="Enter the wing area and the design weight to compute W/S.")
    if subject.w_p is not None and stats.wp_percentile is not None and stats.wp_band:
        right.metric("Power loading W/P (lb/hp)", f"{subject.w_p:.1f}",
                     help=(f"{stats.wp_percentile:.0f}th percentile of the fleet; "
                           f"p10–p90 band {stats.wp_band[0]:.1f}–{stats.wp_band[1]:.1f}."))
    else:
        right.metric("Power loading W/P (lb/hp)", "—",
                     help="Enter the installed power and the design weight to compute W/P.")

    if stats.outliers:
        st.warning("Outside the fleet p10–p90 band for: **"
                   + ", ".join(stats.outliers)
                   + "** — a distinctive design point, worth checking against "
                     "the figures below.")
    else:
        st.caption("Within the fleet p10–p90 band on every computed loading.")

    st.caption("**Parameter table** — this airplane, then the nearest reference "
               "aircraft (normalized distance over MTOW / W/S / W/P):")
    rows: List[Dict[str, object]] = [{"": "→", **subject_row(subject)}]
    rows += [{"": "", **point_row(point)} for point, _distance in stats.nearest]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def render_figures(figures: Sequence[Figure], *, key_prefix: str) -> None:
    """The six scatters, one per tab, exactly as the producer returned them.

    Every figure gets a tab whether or not it could be built: a missing one
    renders the producer's ``absent_reason`` inside its tab, so the tab row is
    the same set of comparisons on every project rather than a list that grows
    and shrinks with the data.
    """
    tabs = st.tabs([TAB_LABELS.get(f.key, f.title) for f in figures])
    for tab, figure in zip(tabs, figures):
        with tab:
            render_figure(figure, key=f"{key_prefix}.{figure.key}")


def render_fleet_table(fleet: Sequence[FleetPoint]) -> None:
    """The whole reference fleet, folded away under the figures."""
    with st.expander("Reference fleet data"):
        st.dataframe(pd.DataFrame([point_row(p) for p in fleet]),
                     hide_index=True, width="stretch")


__all__ = ["TAB_LABELS", "point_row", "render_figures", "render_fleet_table",
           "render_readout", "subject_row"]
