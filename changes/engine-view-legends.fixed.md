- **The engine-installation views name each thrust line by its engine's number, state each designation once, keep the legend inside the text, and mark coincident application points once (#256, tier S, 2026-10-02).**
  Found building the ATR-42 issue package (2026-09-09 review §3 A3). Each
  thrust line's legend entry carried the engine designation -- "PRATT &
  WHITNEY CANADA PW120 (LH) thrust line (ASSUMED)" -- and two of them side by
  side were a 167 pt overfull box on all three views; on the Baron and the
  regional jet, whose engines share a designation, the two rows were
  identical and named neither arrow. `derived_geometry.engine_thrust_segments`
  now labels each "Engine N thrust line", matching its numbered marker, and
  the caption states "Engine N is the <designation>" once per engine. Both
  engines sit at one (x, z) in side view, so marker "2" printed over "1":
  `PlotData.marked_points` merges points within `COINCIDENT_REL` of the
  figure's span into one marker labelled "1 / 2", and both renderers --
  `plots_tex.plot_tex` and `app_shell.plots.plot` -- draw it, so the screen
  and the page agree. The weight/CG envelope's own copy of the merge
  ("CG3 / fwd light") is retired into it, keeping its separator. Sweeping the class, `plot_tex` drops any legend to one
  column when its longest entry cannot share a row
  (`_LEGEND_TWO_COLUMN_CHARS`). No delivered load moves.
