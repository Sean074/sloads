"""Render the theory-manual convention figures as SVGs.

Draws the schematic figures ``docs/20_theory/ch02_conventions.md`` and
``ch03_airspeeds_envelope.md`` embed: the airplane axes and positive-sense
diagram, the wing planform with the LRA and the chordwise stations, the
handedness reflection rule, and a representative V-n envelope with the case
inventory labelled. Every figure is a **schematic drawn from the conventions
charter** (`docs/10_standard/CONVENTIONS.md` §1/§7.1), not from any fixture:
no project file is read, so the figures cannot drift when example data does.
The one drawn from equations (the V-n sketch) uses round illustrative numbers
labelled as such in the chapter, not Appendix A's.

Usage::

    .venv/bin/python scripts/render_theory_figures.py            # write all
    .venv/bin/python scripts/render_theory_figures.py --only vn  # one figure

Requires matplotlib (declared in the ``dev`` extra). Output:
``docs/20_theory/figures/*.svg`` (checked in; re-run after editing).
"""

from __future__ import annotations

import argparse
import math
import os
from typing import Callable, Dict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs",
    "20_theory",
    "figures",
)

AX_KW = dict(color="0.15", lw=1.6)


def _arrow(ax, x0, y0, dx, dy, label, *, color="0.15", lw=1.6, ls="-", pad=0.35):
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0),
            (x0 + dx, y0 + dy),
            arrowstyle="-|>",
            mutation_scale=16,
            color=color,
            lw=lw,
            linestyle=ls,
        )
    )
    norm = math.hypot(dx, dy) or 1.0
    ax.text(
        x0 + dx + pad * dx / norm,
        y0 + dy + pad * dy / norm,
        label,
        ha="center",
        va="center",
        fontsize=11,
        color=color,
    )


def _curl(ax, cx, cy, r, label, *, color="0.35", start=210, end=-30):
    """A curved 'positive rotation' arrow about a point, right-handed on the page."""
    ax.add_patch(
        FancyArrowPatch(
            (cx + r * math.cos(math.radians(start)), cy + r * math.sin(math.radians(start))),
            (cx + r * math.cos(math.radians(end)), cy + r * math.sin(math.radians(end))),
            connectionstyle=f"arc3,rad={0.8}",
            arrowstyle="-|>",
            mutation_scale=12,
            color=color,
            lw=1.3,
        )
    )
    ax.text(cx, cy - r - 0.45, label, ha="center", va="top", fontsize=9.5, color=color)


def fig_axes_signs() -> None:
    """Airplane axes (+aft/+right/+up) and the positive moment senses, plan + side."""
    fig, (axp, axs) = plt.subplots(1, 2, figsize=(10.5, 5.0))

    # --- plan view: x aft (down the page), y right ---
    axp.set_title("Plan view (from above)", fontsize=11)
    body = Polygon(
        [(-0.35, 3.2), (0.35, 3.2), (0.55, -0.5), (0.25, -3.4), (-0.25, -3.4), (-0.55, -0.5)],
        closed=True,
        facecolor="0.92",
        edgecolor="0.55",
    )
    axp.add_patch(body)
    wing = Polygon(
        [(-3.6, 0.4), (3.6, 0.4), (3.6, -0.7), (-3.6, -0.7)],
        closed=True,
        facecolor="0.85",
        edgecolor="0.55",
    )
    axp.add_patch(wing)
    tail = Polygon(
        [(-1.5, -3.35), (1.5, -3.35), (1.5, -2.75), (-1.5, -2.75)],
        closed=True,
        facecolor="0.85",
        edgecolor="0.55",
    )
    axp.add_patch(tail)
    # +x aft is *down* the page in this plan view; +y right.
    _arrow(axp, 0, 0, 0, -1.7, "", **AX_KW)
    axp.text(1.15, -2.05, "+x (aft,\nfuselage station)", fontsize=11, color="0.15")
    _arrow(axp, 0, 0, 2.6, 0, "+y (right,\nbutt line)", **AX_KW)
    axp.plot(0, 0, "o", color="0.15", ms=4)
    axp.text(-0.25, 0.35, "origin:\ndatum", fontsize=8.5, ha="right", color="0.35")
    _curl(axp, 0, -4.3, 0.55, "+mz = nose to port (yaw left)")
    axp.set_xlim(-5, 5)
    axp.set_ylim(-5.6, 4.2)

    # --- side view: x aft (right on page), z up ---
    axs.set_title("Side view (from starboard)", fontsize=11)
    fus = Polygon(
        [(-3.4, 0.15), (-2.3, 0.75), (2.2, 0.75), (3.3, 0.35), (3.3, -0.25), (-2.3, -0.55), (-3.4, -0.15)],
        closed=True,
        facecolor="0.92",
        edgecolor="0.55",
    )
    axs.add_patch(fus)
    vtail = Polygon(
        [(2.35, 0.65), (3.15, 2.3), (3.55, 2.3), (3.3, 0.5)],
        closed=True,
        facecolor="0.85",
        edgecolor="0.55",
    )
    axs.add_patch(vtail)
    _arrow(axs, 0, 0, 2.6, 0, "+x (aft)", **AX_KW)
    _arrow(axs, 0, 0, 0, 2.2, "+z (up,\nwaterline)", **AX_KW)
    _arrow(axs, -1.0, 1.6, 0, 1.1, "+fz = lift", color="C0")
    _arrow(axs, -0.4, -1.35, 1.1, 0, "+fx = drag", color="C0")
    _curl(axs, 0, -1.5, 0.55, "+my = nose-up pitch")
    axs.text(
        0,
        -3.35,
        "+mx = starboard wing up (roll to port)\nright-handed triad: x aft, y right, z up",
        ha="center",
        fontsize=9.5,
        color="0.35",
    )
    axs.set_xlim(-4.6, 5.4)
    axs.set_ylim(-4.0, 3.4)

    for ax in (axp, axs):
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("sloads airplane axes and positive senses (CONVENTIONS.md §1)", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "axes_and_signs.svg"))
    plt.close(fig)


def fig_planform_lra() -> None:
    """A tapered swept half-wing: LRA at ref_axis_pct chord, 25/50% stations, strip loads.

    Drawn root-at-left with the span horizontal; +x (aft) points down the page,
    so the leading edge is the upper boundary.
    """
    fig, ax = plt.subplots(figsize=(10.0, 5.6))
    span, cr, ct, sweep_le = 10.0, 3.0, 1.4, 0.25

    def chord(y: float) -> float:
        return cr + (ct - cr) * y / span

    def x_le(y: float) -> float:
        return sweep_le * y

    # planform: horizontal axis = y (span), vertical = -x so +x aft is down
    ax.add_patch(
        Polygon(
            [(0, -x_le(0)), (span, -x_le(span)), (span, -(x_le(span) + ct)), (0, -cr)],
            closed=True,
            facecolor="0.93",
            edgecolor="0.5",
        )
    )
    for frac, style, label in (
        (0.25, dict(color="C0", lw=1.2, ls="--"), "25% chord"),
        (0.40, dict(color="C3", lw=2.0, ls="-"), "LRA (ref_axis_pct — the assumed elastic axis)"),
        (0.50, dict(color="C0", lw=1.2, ls=":"), "50% chord"),
    ):
        xs = [-(x_le(y) + frac * chord(y)) for y in (0.0, span)]
        ax.plot([0, span], xs, **style)
        y_lab = {0.25: xs[1] + 1.0, 0.40: xs[1], 0.50: xs[1] - 1.0}[frac]
        ax.plot([span, span + 0.5], [xs[1], y_lab], color=style["color"], lw=0.7)
        ax.text(span + 0.65, y_lab, label, fontsize=9.5, color=style["color"], va="center")

    # a strip with its load and torsion arm
    y0 = 5.4
    c = chord(y0)
    ax.add_patch(
        Polygon(
            [
                (y0 - 0.25, -x_le(y0)),
                (y0 + 0.25, -x_le(y0)),
                (y0 + 0.25, -(x_le(y0) + c)),
                (y0 - 0.25, -(x_le(y0) + c)),
            ],
            closed=True,
            facecolor="C0",
            alpha=0.15,
            edgecolor="C0",
        )
    )
    x_cp = x_le(y0) + 0.30 * c
    x_lra = x_le(y0) + 0.40 * c
    ax.plot(y0, -x_cp, "o", color="C0", ms=5)
    ax.annotate(
        "strip lift fz at the strip\ncentre of pressure",
        (y0, -x_cp),
        xytext=(y0 - 0.7, -x_cp + 2.0),
        fontsize=9,
        color="C0",
        ha="center",
        arrowprops=dict(arrowstyle="->", color="C0", lw=0.9),
    )
    ax.annotate(
        "",
        (y0, -x_lra),
        (y0, -x_cp),
        arrowprops=dict(arrowstyle="-|>", color="C3", lw=1.6),
    )
    ax.annotate(
        "chordwise arm → torsion myy\nabout the LRA (+myy = LE up)",
        (y0, -x_lra),
        xytext=(y0 + 0.5, -x_lra - 2.1),
        fontsize=9,
        color="C3",
        arrowprops=dict(arrowstyle="->", color="C3", lw=0.9),
    )
    ax.annotate(
        "root (y = 0): Sz, Mxx, Myy, −Mzz stated here",
        (0.05, -cr * 0.5),
        xytext=(0.4, -cr - 1.6),
        fontsize=9,
        color="0.3",
        arrowprops=dict(arrowstyle="->", color="0.5"),
    )
    ax.text(1.2, -x_le(1.2) + 0.35, "leading edge", fontsize=8.5, color="0.45")
    _arrow(ax, -0.8, 0.6, 2.2, 0.0, "", **AX_KW)
    ax.text(2.05, 0.95, "+y (butt line)", fontsize=11, color="0.15")
    _arrow(ax, -0.8, 0.6, 0.0, -2.0, "+x (aft)", **AX_KW)
    ax.set_xlim(-1.8, span + 4.6)
    ax.set_ylim(-cr - 2.6, 2.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        "Wing planform (from above, root at left), the load reference axis and the chordwise stations\n"
        "(CONVENTIONS.md §1: torsion is about the LRA and names its axis)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "planform_lra.svg"))
    plt.close(fig)


def fig_handedness() -> None:
    """The reflection rule: y -> -y flips fy (true vector) and mx/mz (axial), not fz/my."""
    fig, (axr, axl) = plt.subplots(1, 2, figsize=(10.5, 4.6))
    for ax, hand, sgn in ((axr, "starboard case (…R)", +1), (axl, "port twin (…L) — derived by reflection", -1)):
        ax.set_title(hand, fontsize=11)
        ax.add_patch(
            Polygon(
                [(-0.3, 2.6), (0.3, 2.6), (0.45, -0.4), (0.2, -2.8), (-0.2, -2.8), (-0.45, -0.4)],
                closed=True,
                facecolor="0.92",
                edgecolor="0.55",
            )
        )
        ax.add_patch(
            Polygon(
                [(-3.0, 0.3), (3.0, 0.3), (3.0, -0.55), (-3.0, -0.55)],
                closed=True,
                facecolor="0.85",
                edgecolor="0.55",
            )
        )
        _arrow(ax, 0.0, -2.3, sgn * 1.7, 0.0, "fin side load fy\n(sign flips)", color="C3")
        _arrow(ax, 0.0, 1.6, 0.0, 1.2, "fz, my\nunchanged", color="C0")
        _curl(ax, 0, -4.0, 0.5, f"mx, mz reverse ({'+' if sgn > 0 else '−'})")
        ax.set_xlim(-4.6, 4.6)
        ax.set_ylim(-5.4, 3.6)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle(
        "Handedness: the opposite-hand twin is reflection y → −y at assembly\n"
        "forces are true vectors (only fy flips); moments are axial vectors "
        "(mx, mz flip, my does not) — CONVENTIONS.md §7.1",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(os.path.join(OUT_DIR, "handedness.svg"))
    plt.close(fig)


def fig_vn_envelope() -> None:
    """A representative V-n envelope with the corner-point case inventory labelled."""
    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    n_pos, n_neg = 3.8, -1.52
    vs, vc, vd = 60.0, 160.0, 210.0
    va = vs * math.sqrt(n_pos)
    vs_inv = vs * math.sqrt(abs(n_neg))

    v_stall = list(range(0, int(va) + 1))
    ax.plot(v_stall, [(v / vs) ** 2 for v in v_stall], color="0.2", lw=1.6)
    v_stall_n = list(range(0, int(vs_inv) + 1))
    ax.plot(v_stall_n, [-((v / vs) ** 2) * (abs(n_neg) / ((vs_inv / vs) ** 2)) for v in v_stall_n], color="0.2", lw=1.6)
    # manoeuvre boundary
    ax.plot([va, vd, vd, vc, vs_inv], [n_pos, n_pos, 0, n_neg, n_neg], color="0.2", lw=1.6)
    ax.axhline(0, color="0.75", lw=0.8)

    # gust lines from (0, 1)
    for v_ref, slope_scale, ls in ((vc, 1.0, "--"), (vd, 0.5, ":")):
        for sgn in (+1, -1):
            ax.plot([0, v_ref], [1, 1 + sgn * slope_scale * 0.0155 * v_ref], color="C0", lw=1.1, ls=ls)
    ax.plot([0], [1], "o", color="C0", ms=4)

    pts = {
        "PHAA": (va, n_pos, (-28, 10)),
        "PLAA": (vd, n_pos, (6, 10)),
        "NHAA": (vs_inv, n_neg, (-34, -16)),
        "NLAA": (vc, n_neg, (6, -16)),
        "dive": (vd, 0.0, (8, -4)),
    }
    for name, (x, y, off) in pts.items():
        ax.plot(x, y, "s", color="C3", ms=6)
        ax.annotate(name, (x, y), xytext=off, textcoords="offset points", fontsize=10, color="C3")

    for x, lab in ((vs, "VS"), (va, "VA"), (vc, "VC"), (vd, "VD")):
        ax.axvline(x, color="0.85", lw=0.8, zorder=0)
        ax.text(x, -2.35, lab, ha="center", fontsize=10, color="0.35")

    ax.text(6, 3.9, "gust lines at VC (dashed) and VD (dotted), ± from n = 1", fontsize=9.5, color="C0")
    ax.text(va * 0.62, 1.05, "stall boundary\nn = (V/VS)²", fontsize=9.5, color="0.35", ha="center")
    ax.set_xlim(0, vd * 1.13)
    ax.set_ylim(-2.6, 4.6)
    ax.set_xlabel("equivalent airspeed (KEAS)")
    ax.set_ylabel("load factor n")
    ax.set_title(
        "A representative V-n envelope and its case inventory (illustrative numbers, not Appendix A)\n"
        "corner points + gust intersections are the candidate conditions handed downstream",
        fontsize=11,
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "vn_envelope.svg"))
    plt.close(fig)


FIGURES: Dict[str, Callable[[], None]] = {
    "axes": fig_axes_signs,
    "planform": fig_planform_lra,
    "handedness": fig_handedness,
    "vn": fig_vn_envelope,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", choices=sorted(FIGURES), help="render one figure")
    args = parser.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    names = [args.only] if args.only else sorted(FIGURES)
    for name in names:
        FIGURES[name]()
        print(f"rendered figure {name!r} into {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
