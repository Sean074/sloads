"""Render a project's LRA beam model as an iso + three-view PNG.

A display-only analyst tool: it reads a ``*.project.json``, builds the step-12
LRA skeleton through the public exporter API
(:func:`sloads.export.lra_model.build_lra_model` -- geometry and topology, no
loads), and draws it as a 4-panel figure (isometric, plan, side, front) with
the planform/body outlines overlaid for context.

Nothing here feeds an analysis: the outlines come from the same geometry
owners the exporter reads (the entered surface polylines,
``resolve_tail_planform``, the fuselage outline sections), and the beam is
drawn exactly where ``build_lra_model`` put it. Two honesty notes:

* the wing/h-tail planform edges are ``(X, span)`` with no waterline, so the
  outline is **draped at the beam chain's own interpolated waterline** --
  correct in plan view; in the side/front views it inherits the LRA's
  dihedral rather than the true surface z. A picture convention, not geometry;
* the exporter's refusal contract is kept: a :class:`~sloads.export.lra_model
  .LraRefusal` (missing ``ref_axis_pct``, no side of body, ...) is printed
  verbatim and the script exits 2 -- it never defaults the missing datum. An
  *outline* that fails to resolve degrades to a stderr note and a skipped
  overlay; the beam plot itself still renders.

Usage::

    .venv/bin/python scripts/plot_lra_model.py examples/ga6_normal.project.json
    .venv/bin/python scripts/plot_lra_model.py p.project.json -o views.png --dpi 200 --no-outlines

Requires matplotlib (declared in the ``dev`` extra).
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from typing import Callable, List, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads.export.lra_model import LraModel, LraRefusal, build_lra_model
from sloads.io import load_project
from sloads.models import Project
from sloads.tail_geometry import HTAIL, VTAIL, resolve_tail_planform

Vec3 = Tuple[float, float, float]
Loop = List[Vec3]

#: CBAR chain colour per section family (display only).
FAMILY_COLOR = {"wing": "#1f77b4", "fuselage": "#2ca02c",
                "htail": "#d62728", "vtail": "#9467bd"}

#: Marker style + legend label per BM-5 node family tag.
MARKERS = {
    "lra-sob": ("o", "#1f77b4", "SOB node"),
    "lra-post": ("s", "#2ca02c", "spar post"),
    "lra-centre": ("D", "black", "centre hub"),
    "lra-fin-root": ("^", "#9467bd", "fin root"),
    "lra-attach": ("v", "#d62728", "h-tail attach"),
    "lra-gear": ("P", "#8c564b", "gear"),
    "lra-engine-mount": ("X", "#ff7f0e", "engine mount"),
    "lra-engine-hub": ("*", "#ff7f0e", "engine hub"),
    "lra-hinge": ("1", "gray", "hinge"),
    "lra-actuator": ("2", "gray", "actuator"),
}


def _interp(pairs: Sequence[Tuple[float, float]], k: float) -> float:
    """Linear interpolation on (key, value) pairs, end-segment extrapolation.

    A local, display-only mirror of the exporter's private ``_interp_chain``
    (kept separate deliberately: promoting that helper is a sloads change this
    script must not require).
    """
    pts = sorted(pairs)
    if len(pts) == 1:
        return pts[0][1]
    if k <= pts[0][0]:
        (ka, va), (kb, vb) = pts[0], pts[1]
    elif k >= pts[-1][0]:
        (ka, va), (kb, vb) = pts[-2], pts[-1]
    else:
        (ka, va), (kb, vb) = next((a, b) for a, b in zip(pts, pts[1:]) if a[0] <= k <= b[0])
    t = 0.0 if kb == ka else (k - ka) / (kb - ka)
    return va + t * (vb - va)


def _closed(loop: Loop) -> Loop:
    return loop + loop[:1]


def collect_outlines(project: Project, model: LraModel) -> List[Loop]:
    """The display outlines as closed 3D polylines -- resilient per surface.

    Each block reads the same owner the exporter reads and drapes the edges at
    the corresponding beam chain's waterline (see the module docstring). A
    surface whose outline cannot resolve is skipped with a stderr note; the
    beam plot never depends on this function succeeding.
    """
    outlines: List[Loop] = []
    geom = project.geometry
    if geom is None:
        return outlines

    # Wing: (X, BL) edges, mirrored, at the right-wing chain's z(|y|).
    wing = geom.by_name("wing")
    wing_chain = model.members.get("wing-R") or []
    if wing is not None and wing.leading_edge and wing.trailing_edge and wing_chain:
        wing_z = [(n.pos[1], n.pos[2]) for n in wing_chain]
        for sgn in (1.0, -1.0):
            loop = ([(x, sgn * s, _interp(wing_z, abs(s))) for x, s in wing.leading_edge]
                    + [(x, sgn * s, _interp(wing_z, abs(s))) for x, s in reversed(wing.trailing_edge)])
            outlines.append(_closed(loop))

    # H-tail: (x, BL) edges mirrored at the h-tail chain's waterline -- which
    # is the fin-tip waterline on a T-tail, because the chain already sits there.
    ht_chain = model.members.get("htail") or []
    if ht_chain:
        try:
            pf_h = resolve_tail_planform(project, HTAIL)
        except (ValueError, KeyError) as err:
            print(f"note: h-tail outline skipped ({err})", file=sys.stderr)
        else:
            z_ht = ht_chain[0].pos[2]
            for sgn in (1.0, -1.0):
                loop = ([(x, sgn * s, z_ht) for x, s in pf_h.le]
                        + [(x, sgn * s, z_ht) for x, s in reversed(pf_h.te)])
                outlines.append(_closed(loop))

    # Fin: (x, WL offset above root_z) edges on the centre plane.
    if model.members.get("vtail"):
        try:
            pf_v = resolve_tail_planform(project, VTAIL)
        except (ValueError, KeyError) as err:
            print(f"note: fin outline skipped ({err})", file=sys.stderr)
        else:
            loop = ([(x, 0.0, pf_v.root_z + s) for x, s in pf_v.le]
                    + [(x, 0.0, pf_v.root_z + s) for x, s in reversed(pf_v.te)])
            outlines.append(_closed(loop))

    # Fuselage: plan half-widths and side heights about the body chain's
    # waterline, plus the widest section as the front-view ellipse.
    fus_chain = model.members.get("fuselage") or []
    outline = geom.fuselage
    if outline is not None and outline.sections and fus_chain:
        fus_z = [(n.pos[0], n.pos[2]) for n in fus_chain]
        secs = sorted(outline.sections, key=lambda s: s.x)
        plan = ([(s.x, s.width / 2, _interp(fus_z, s.x)) for s in secs]
                + [(s.x, -s.width / 2, _interp(fus_z, s.x)) for s in reversed(secs)])
        outlines.append(_closed(plan))
        side = ([(s.x, 0.0, _interp(fus_z, s.x) + s.height / 2) for s in secs]
                + [(s.x, 0.0, _interp(fus_z, s.x) - s.height / 2) for s in reversed(secs)])
        outlines.append(_closed(side))
        wide = max(secs, key=lambda s: s.width)
        if wide.width > 0 and wide.height > 0:
            cz = _interp(fus_z, wide.x)
            outlines.append([(wide.x, wide.width / 2 * math.cos(t), cz + wide.height / 2 * math.sin(t))
                             for t in (i * math.tau / 72 for i in range(73))])
    return outlines


def render(model: LraModel, outlines: Sequence[Loop], title: str, out_path: str, dpi: int) -> None:
    """Draw the 4-panel figure and save it to ``out_path``."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    pos = {n.gid: n.pos for n in model.nodes}
    segs: dict = {}
    for (ga, gb), fam in zip(model.cbars, model.cbar_families):
        segs.setdefault(fam, []).append((pos[ga], pos[gb]))
    ties = [(pos[gn], pos[gm]) for gn, _cm, gms, _lbl in model.rbe2s for gm in gms]
    tagged: dict = {}
    for n in model.nodes:
        if n.family in MARKERS:
            tagged.setdefault(n.family, []).append(n.pos)
    support = pos[model.support_gid]
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    zs = [p[2] for p in pos.values()]

    def draw(ax, proj: Callable[[float, float, float], tuple]) -> None:
        is3d = len(proj(0.0, 0.0, 0.0)) == 3
        for loop in outlines:
            ax.plot(*zip(*[proj(*p) for p in loop]), color="0.65", lw=0.8, zorder=1)
        for fam, ss in segs.items():
            for a, b in ss:
                ax.plot(*zip(proj(*a), proj(*b)), color=FAMILY_COLOR[fam], lw=1.6, solid_capstyle="round")
        for a, b in ties:
            ax.plot(*zip(proj(*a), proj(*b)), color="0.55", lw=0.9, ls="--")
        for fam, pts in tagged.items():
            m, c, _lbl = MARKERS[fam]
            cc = list(zip(*[proj(*p) for p in pts]))
            if is3d:
                ax.scatter(*cc, marker=m, s=45, color=c, zorder=5, depthshade=False)
            else:
                ax.scatter(*cc, marker=m, s=45, color=c, zorder=5)
        sp = proj(*support)
        if is3d:
            ax.scatter(*[[v] for v in sp], marker="x", s=70, color="red", zorder=6, depthshade=False)
        else:
            ax.scatter(*sp, marker="x", s=70, color="red", zorder=6)

    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(f"{title} — LRA beam model (build_lra_model)\n"
                 "node lines on the loads reference axes; CBAR chains solid, RBE2 rigid ties dashed; "
                 "grey = planform/body outline; red x = SPC support", fontsize=12)

    ax3 = fig.add_subplot(2, 2, 1, projection="3d")
    draw(ax3, lambda x, y, z: (x, y, z))
    ax3.set_xlabel("FS x (in)")
    ax3.set_ylabel("BL y (in)")
    ax3.set_zlabel("WL z (in)")
    ax3.set_title("Isometric")
    ax3.view_init(elev=22, azim=-125)
    cx, cy, cz = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, (max(zs) + min(zs)) / 2
    r = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)) / 2 * 1.05
    ax3.set_xlim(cx - r, cx + r)
    ax3.set_ylim(cy - r, cy + r)
    ax3.set_zlim(cz - r, cz + r)
    ax3.set_box_aspect((1, 1, 1))

    flats = (
        (fig.add_subplot(2, 2, 2), lambda x, y, _z: (x, y), "Plan (top) view", "FS x (in)", "BL y (in)"),
        (fig.add_subplot(2, 2, 3), lambda x, _y, z: (x, z), "Side (profile) view — nose left",
         "FS x (in)", "WL z (in)"),
        (fig.add_subplot(2, 2, 4), lambda _x, y, z: (y, z), "Front view (looking aft)", "BL y (in)", "WL z (in)"),
    )
    for ax, proj, name, xl, yl in flats:
        draw(ax, proj)
        ax.set_title(name)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)

    handles = [Line2D([], [], color=c, lw=2, label=f) for f, c in FAMILY_COLOR.items()]
    handles.append(Line2D([], [], color="0.55", lw=1, ls="--", label="RBE2 rigid tie"))
    if outlines:
        handles.append(Line2D([], [], color="0.65", lw=0.8, label="planform/body outline"))
    for fam, (m, c, lbl) in MARKERS.items():
        if fam in tagged:
            handles.append(Line2D([], [], marker=m, color="none", markeredgecolor=c,
                                  markerfacecolor=c, markersize=8, label=lbl))
    handles.append(Line2D([], [], marker="x", color="none", markeredgecolor="red",
                          markersize=9, label="SPC support"))
    fig.legend(handles=handles, loc="lower center", ncol=7, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", help="path to the *.project.json to render")
    ap.add_argument("-o", "--output", default=None,
                    help="output PNG path (default: <project stem>_lra_views.png beside the input)")
    ap.add_argument("--dpi", type=int, default=150, help="raster resolution (default 150)")
    ap.add_argument("--no-outlines", action="store_true",
                    help="draw the beam skeleton only, no planform/body outlines")
    args = ap.parse_args(argv)

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("plot_lra_model.py needs matplotlib: .venv/bin/pip install -e '.[dev]' "
              "(or pip install matplotlib)", file=sys.stderr)
        return 3

    project = load_project(args.project)
    try:
        model = build_lra_model(project)
    except LraRefusal as err:
        print(f"LRA refusal: {err}", file=sys.stderr)
        return 2

    outlines: List[Loop] = [] if args.no_outlines else collect_outlines(project, model)

    out = args.output
    if out is None:
        stem = os.path.basename(args.project)
        for suffix in (".project.json", ".json"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        out = os.path.join(os.path.dirname(os.path.abspath(args.project)), f"{stem}_lra_views.png")

    title = project.name or os.path.basename(args.project)
    if len(title) > 80:
        title = title[:77] + "..."
    render(model, outlines, title, out, args.dpi)
    print(f"{out}: {len(model.nodes)} nodes, {len(model.cbars)} CBARs, "
          f"{len(model.rbe2s)} RBE2s, {len(outlines)} outline loops")
    return 0


if __name__ == "__main__":
    sys.exit(main())
