- **Design note 60 amends the convergence plan: twenty figures, one owner, and one report (note 60 AGREED 2026-09-13, band B5 re-cut, tier S).**
  The critical review of band B5, taken immediately after the 0.8.3 cut, found
  two measurements design note 57 did not make. **The front-end carries twenty
  figures, not the four D-57.4 names** — thirteen of the 22 `app/views/` pages
  chart at twenty call sites, and **nine of those pages are shared analysis
  steps** the survivor renders today with no figure, which a page-level audit
  cannot see going. And **`app/views/export_report.py` is the only production
  consumer of `content.build_report`**, so D-57.6 retires the 2,632-line
  summary report without naming it — taking the only statement of the axis
  system and sign conventions either front-end makes (`conventions_tex.py`,
  276 lines, sole consumer, three static TikZ diagrams) and the only FAR 23
  Subpart C coverage matrix (`coverage.py`, 241 lines, sole consumer).

  **Block A (D-60.1…D-60.6)** withdraws D-57.4's *written fresh* ruling:
  `content.PlotData` — already frozen, renderer-agnostic and already shared by
  both documents — stays the single owner of what a figure is, `plots_tex`
  emits LaTeX and a new `app_shell/plots.py` emits Plotly, and a both-ways
  parity guard holds them together, so *"every report figure appears in the
  GUI"* is structural rather than diligent (practice 3). Producers become
  callable per figure from a `Project` (pre-run) or from the module results
  (post-run), classified as one; #267 is re-tiered **M → L** and gains the
  figure gate it shipped without (practice 2).

  **Block B (D-60.7…D-60.12)** merges four cross-cutting sections into the
  oracle report — axes and sign conventions, the FAR coverage matrix, the
  governing safety-factor table and the bundle manifest — as a front-matter
  group after the Introduction via `oracle_content.FRONT_SECTIONS`, so the
  section plan stays **derived** and G-OR-2 survives re-cut on the OR-16
  pattern. Every other `content.SECTIONS` key is declared superseded with its
  successor or its reason in an audit table a guard reads, and `build_report`
  is deleted at #270 only after the merge has landed. #245 is confirmed and
  widened: the per-module CSV and text buttons retire with the results zip and
  `data/` is the single tabular channel.

  Band **B5 gains two rows** — **#239** pulled forward from B6, because note
  57's gates 4 and 5 are enforced by `tests/test_basis_statements.py` whose
  `_GUI_TREES` excludes `oracle_app` and including it *is* that row, and the
  **report-merge** row filed new — and re-tiers **#267**. Note 57's gates 4 and
  5 move from #270 to #266 and gate 7 is asserted after #266, since that row
  adds 79 fields to the survivor's renderer and could re-import the no-op-Apply
  class. Note 57's D-57.8 rule is unchanged and is what the additions serve:
  the surviving GUI is complete before anything is removed. The priority table
  is renumbered densely with the re-cut (**Pri 1–57**).
