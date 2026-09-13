- **The fleet comparison ports to the surviving GUI (#268, design note 57
  D-57.5, tier M, 2026-09-13)** — the Phase-C *assess against similar airplanes*
  requirement lands in `oracle_app/` as a marked **✦** extension page, on the
  navigation only and never in the derived step set, at the url path `fleet`
  because `aircraft_comparison` is a workflow step key and a non-step reachable
  at a step's URL is what gate G2 exists to prevent. The port's real content is
  what it stopped owning. The bundled reference fleet moved from `app/data/`
  into `sloads/data/` and is read by `sloads.fleet.reference_fleet`; the
  subject's priority chain moved out of the page as
  `sloads.fleet.subject_from_project`; the six scatters became `PlotData`
  producers in `sloads/report/fleet_figures.py`; and the readout, tabs and fleet
  table became `app_shell/fleet_view.py`, which the retiring page now calls
  unchanged — two pages, one implementation, for the milestone in which both
  exist. D-57.5's *rewritten, not imported* was not followed; the amendment
  was **ratified by the owner in session, 2026-09-13**: note 60 D-60.1
  withdrew exactly that rule for figures
  on the ground that a second derivation is a second owner, the subject chain is
  the same class of thing, and it carries the 2026-08-15 fix that had stopped a
  regional jet being plotted 1,800 lb above any weight its loadings can reach —
  a rewrite would have been a rewrite of that fix. The move paid for itself
  immediately: gate DG-3 forbids anything in `sloads/` from integrating the wing
  planform itself, the page had been doing exactly that since M2-5 and was
  invisible to the guard while it lived in `app/`, and the subject now reads
  area, aspect ratio and span through `derived_geometry`'s resolvers — the
  single owner of what area the analysis actually uses (#70) — with the
  placement unchanged to the last ulp on every bundled example. Making the figures
  producer-owned needed three additions to the figure model, which could not
  express a scatter at all: `Series.marker`, `Series.labels` and
  `PlotData.log_x`/`log_y`, honoured by the Plotly renderer and — bar the
  per-point labels, which are a hover and not a printed node — by `plots_tex`,
  so the set can be printed the day a document asks for it. The figures are
  deliberately **not** in `sloads/report/figures.py`'s step catalogue and not in
  the oracle report: every family in that catalogue is drawn on the page whose
  programs produce it and is held against the built document by gate 10, and the
  fleet comparison runs no program. Guarded by `tests/test_fleet_figures.py` —
  the six figures build for every bundled example, the CSV has exactly one
  reader in the whole tree, neither front-end defines a derivation of its own,
  and both renderers honour the marker and the log axes.
