- **The plane a surface is defined in has one owner (#220, tier S,
  2026-09-09).** Design note 54 D-54.2: whether a surface's span coordinate is
  a butt line (wing, h-tail, their controls) or a waterline (fin, rudder) is
  now answered once, by `sloads.tail_geometry.surface_plane` returning
  `SurfacePlane`, replacing the five per-call-site name tests — the four
  local→airplane maps in `export/coordinates.py` and the three-view's
  mirror/view branch in `modules/configuration.py` (its private
  `_WATERLINE_SPAN_SURFACES` tuple removed). Docstrings that claimed the
  second polyline coordinate is a butt line (`XYPoint`, `SurfaceInput`,
  `wing_geometry.interp_x`) corrected. New guards tie the coordinate maps and
  the report's declared frame/span-axis data back to the owner; `CONVENTIONS.md`
  §7 gains the SSOT row. No user-selected plane field yet (deferred with
  V-tail/cruciform support, note 54 §8). No load, deck byte, or delivered
  file changes.
