- **The fleet comparison ports to the surviving GUI, and stops owning anything
  (#268, design note 57 D-57.5, tier M, 2026-09-13).** The Phase-C *assess
  against similar airplanes* requirement is now a page of the oracle GUI —
  `oracle_app/fleet.py`, marked **✦** as an sloads extension because the
  original suite has no such program, registered on the navigation only and
  never in the derived step set (gate G2). The airplane is placed against the bundled
  reference fleet by wing loading, power loading, weight and geometry, with the
  nearest comparators named, the p10–p90 band flagged, and six scatter tabs.
  The reference figures are nominal published specifications in Imperial units
  and never enter a computation.

- **The reference fleet moves into the package it belongs to (#268).**
  `app/data/reference_aircraft.csv` → `sloads/data/reference_aircraft.csv`, read
  by `sloads.fleet.reference_fleet` and shipped as package data. It had been
  sitting inside a Streamlit app nothing imports, so a `pip install sloads`
  carried no fleet to compare against; the front-end that carried it retires at
  #270.

- **`sloads.fleet` gains the subject's priority chain (#268).**
  `subject_from_project` — MTOW from `cg_cases.max_takeoff_weight` then
  WTESTIMA, empty weight from the item database then WTESTIMA, area / aspect
  ratio / span from the parametric layout then the WINGGEOM wing surface — moves
  out of the retiring page unchanged. D-57.5 asked for it to be *rewritten, not
  imported*; note 60 D-60.1 had already withdrawn that rule for figures on the
  ground that a second derivation is a second owner, and this chain carries the
  2026-08-15 fix that stopped a regional jet being plotted 1,800 lb heavy.

- **Moving the chain into `sloads/` put it under a guard that caught it
  (#268).** Gate DG-3 (`tests/test_derived_geometry.py`) forbids a module in
  `sloads/` from integrating the wing planform itself — the defect #70 found
  after four numbers for one wing turned up in the tree. The comparison page had
  been a fifth, invisible to the guard because it lived in `app/`. The subject
  now reads area, aspect ratio and span through `derived_geometry`'s resolvers,
  which is *what the analysis actually uses*; the placement is unchanged to the
  last ulp on every bundled example.

- **A scatter is now something the figure model can say (#268).**
  `Series.marker` (points, not a polyline), `Series.labels` (which airplane each
  point is, shown on hover) and `PlotData.log_x` / `log_y` (a fleet spanning a
  factor of thirty in weight). The six figures are built by
  `sloads/report/fleet_figures.py` and drawn by `app_shell/plots.py`, with
  `plots_tex` honouring the marker and the log axes too — so the port adds no
  second figure owner, and both front-ends render one implementation
  (`app_shell/fleet_view.py`) until `app/views/` retires.
