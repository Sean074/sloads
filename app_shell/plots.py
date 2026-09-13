"""The **screen renderer** of a report figure -- Plotly over ``PlotData``.

Design note 60 D-60.1: ``sloads.report.content.PlotData`` is the single owner of
what a figure *is*, and :mod:`sloads.report.plots_tex` (LaTeX/TikZ) and this
module (Plotly) are **peers over it**. Neither derives figure data; both are
given it. That is what makes "every figure the oracle report carries also appears
in the GUI" a property of the code rather than a promise, and it is why D-57.4's
*written fresh from the result slices* was withdrawn: a second derivation is a
second owner, and two owners of one picture is #239's drift class.

**What this module may and may not do.** It may decide how a line looks on a
screen. It may not decide what is plotted, what the axes mean, what a series is
called, or where a marker goes -- all of that arrived in the ``PlotData`` and is
rendered as given. There is no ``Project`` here and no calc import; the figure
is data by the time it reaches this file.

**Style, and why the screen is not greyscale.** ``SUMMARY_REPORT.md`` §4.3
requires a printed figure to stay legible in greyscale, so every producer states
a *line style* and never a colour. A screen has no such constraint and a
colour-coded legend is read faster than a dash-coded one, so traces are coloured
here -- **and the producer's stated style is honoured as well**, dash pattern and
weight both. A reader who has the PDF open beside the page sees the same dashed
curve in the same place; the colour is added information, not a substitute for
the encoding the report relies on.

**Regions.** ``Series.closed`` says the polyline bounds a region -- a planform
outline, a control surface -- rather than tracing a curve. A closed series is
closed back to its first vertex and filled where its style asks for a fill, and
the axes are then drawn to scale, because a planform stretched to fill a widget
is a drawing of a different airplane.

Pure except for the two ``st`` calls in :func:`render_figure`: :func:`plot` takes
data and returns a Plotly figure, so a test can assert on the traces without a
Streamlit runtime.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import plotly.graph_objects as go
import streamlit as st

from sloads.report.content import Figure, PlotData, Series

#: How a pgfplots style token maps to a Plotly dash pattern.
#:
#: The producers write pgfplots because that is the renderer they were written
#: for; translating here rather than changing them is the point of D-60.1 -- the
#: data stays what the LaTeX emitter reads, and each renderer interprets it.
_DASH = {
    "solid": "solid",
    "dashed": "dash",
    "densely dashed": "dash",
    "dotted": "dot",
    "densely dotted": "dot",
    "dashdotted": "dashdot",
}

#: How a weight token maps to a line width, in pixels.
_WIDTH = {"thick": 2.4, "very thick": 3.2}

#: The trace colours, in order of first use. Plotly's own qualitative set,
#: pinned here so a library default cannot renumber a figure's legend between
#: releases; the first entry is the one a single-series figure gets.
_COLOURS: Tuple[str, ...] = (
    "#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e",
    "#8c564b", "#17becf", "#bcbd22", "#e377c2", "#7f7f7f",
)

#: The marker colour of :attr:`PlotData.points`, and the colour of a reference
#: line. Both are annotations on the plotted data rather than data of their own,
#: so both are grey and neither takes a colour out of the series sequence.
_ANNOTATION = "#555555"

#: How a pgfplots ``mark=`` token maps to a Plotly marker symbol. A producer
#: states a shape when one figure carries more than one cloud of points, so the
#: printed figure reads in greyscale (``SUMMARY_REPORT.md`` §4.3); the screen
#: honours the shape as well as colouring the series, for the same reason the
#: line styles are honoured beside the colours.
_MARKS = {
    "*": "circle", "o": "circle-open", "square*": "square",
    "square": "square-open", "triangle*": "triangle-up",
    "triangle": "triangle-up-open", "diamond*": "diamond",
    "diamond": "diamond-open",
}


def _symbol(style: str) -> str:
    """The marker symbol a series' style asks for; a filled circle by default."""
    for token in (t.strip() for t in style.split(",")):
        if token.startswith("mark="):
            return _MARKS.get(token.split("=", 1)[1].strip(), "circle")
    return "circle"


def _line(style: str, colour: str) -> dict:
    """One series' line, from the pgfplots style string it was stated in."""
    tokens = [t.strip() for t in style.split(",") if t.strip()]
    dash = "solid"
    width = 1.8
    for token in tokens:
        if token in _DASH:
            dash = _DASH[token]
        if token in _WIDTH:
            width = _WIDTH[token]
    # ``very thick, dashed`` is one style carrying both, which is why the loop
    # reads every token rather than looking the whole string up.
    joined = " ".join(tokens)
    for name, value in _DASH.items():
        if " " in name and name in joined:
            dash = value
    return {"color": colour, "dash": dash, "width": width}


def _fill(style: str) -> Optional[str]:
    """The fill colour a ``fill=gray!NN`` style asks for, or ``None``.

    The grey level is read out of the style rather than assumed: a planform
    figure uses two of them to tell an outline from a region inside it, and
    collapsing both to one fill would lose the distinction the producer drew.
    """
    for token in (t.strip() for t in style.split(",")):
        if token.startswith("fill=gray!"):
            try:
                level = int(token.split("!", 1)[1])
            except ValueError:
                return None
            shade = int(255 * (100 - min(level, 100)) / 100)
            return f"rgba({shade},{shade},{shade},0.45)"
    return None


def _xy(series: Series) -> Tuple[List[float], List[float]]:
    """The polyline's points, closed back to the first where it bounds a region."""
    x, y = list(series.x), list(series.y)
    if series.closed and len(x) > 2 and (x[0], y[0]) != (x[-1], y[-1]):
        x.append(x[0])
        y.append(y[0])
    return x, y


def is_to_scale(data: PlotData) -> bool:
    """Whether this figure is a *drawing* and must keep its aspect ratio.

    True when every series bounds a region: that is what a planform, a side view
    and a control-surface locator have in common, and what a load distribution
    never has. Derived from the data rather than from a flag on the family --
    ``Series.closed`` already carries the fact, and a second declaration beside
    it would be free to disagree with it.
    """
    return bool(data.series) and all(s.closed for s in data.series)


def plot(data: PlotData, *, height: int = 420) -> go.Figure:
    """``data`` as a Plotly figure. No Streamlit, no project, no calc."""
    fig = go.Figure()
    colours = iter(_COLOURS * 4)
    for series in data.series:
        colour = next(colours)
        x, y = _xy(series)
        fill = _fill(series.style)
        if series.marker:
            # A scatter (#268). ``Series.labels`` is per-point identity and the
            # only place it is shown is the hover, which is the question a
            # scatter provokes -- which one is that? -- answered without
            # printing a name over every point of the cloud.
            labels = list(series.labels)
            fig.add_trace(go.Scatter(
                x=x, y=y, name=series.name, mode="markers",
                text=labels or None,
                marker={"size": 9, "color": colour,
                        "symbol": _symbol(series.style),
                        "line": {"width": 1, "color": colour}},
                hovertemplate=(("%{text}<br>" if labels else f"{series.name}<br>")
                               + "%{x}, %{y}<extra></extra>")))
            continue
        fig.add_trace(go.Scatter(
            x=x, y=y, name=series.name, mode="lines",
            line=_line(series.style, colour),
            fill="toself" if fill else None,
            fillcolor=fill,
            hovertemplate=f"{series.name}<br>%{{x}}, %{{y}}<extra></extra>"))
    if data.points:
        fig.add_trace(go.Scatter(
            x=[x for _label, x, _y in data.points],
            y=[y for _label, _x, y in data.points],
            text=[label for label, _x, _y in data.points],
            name=data.points_label, mode="markers+text",
            textposition="top center",
            textfont={"size": 10, "color": _ANNOTATION},
            marker={"size": 8, "color": _ANNOTATION, "symbol": "circle"},
            hovertemplate="%{text}<br>%{x}, %{y}<extra></extra>"))
    for label, x in data.vlines:
        # A reference line is drawn, not added as a series: it belongs to the
        # axes rather than to the data, and a legend entry per speed line would
        # bury the curves the figure is about.
        fig.add_vline(x=x, line={"color": _ANNOTATION, "dash": "dot", "width": 1},
                      annotation_text=label, annotation_position="top",
                      annotation_font={"size": 10, "color": _ANNOTATION})
    fig.update_layout(
        height=height,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        xaxis_title=data.x_label, yaxis_title=data.y_label,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02,
                "xanchor": "left", "x": 0},
        hovermode="closest")
    # The producer states the axis scale, so the screen figure and the printed
    # one are the same picture (#268).
    if data.log_x:
        fig.update_xaxes(type="log")
    if data.log_y:
        fig.update_yaxes(type="log")
    if is_to_scale(data):
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def render_figure(figure: Figure, *, key: str, height: int = 420) -> bool:
    """Render one report figure on the page. ``True`` if it had data to draw.

    A figure with no data renders its ``absent_reason`` -- the sentence the
    producer wrote for the document -- rather than an empty axis. The two
    front-ends therefore say the same thing about the same missing figure, which
    is the property ``Figure.absent_reason`` was added to the model for.
    """
    st.markdown(f"**{figure.title}**")
    if figure.data is None:
        st.caption(f"Not drawn — {figure.absent_reason}"
                   if figure.absent_reason else "Not drawn.")
        return False
    st.plotly_chart(plot(figure.data, height=height), width="stretch", key=key)
    if figure.caption:
        st.caption(figure.caption)
    return True


__all__ = ["is_to_scale", "plot", "render_figure"]
