- **The development plan re-cuts into three milestones: 0.8.3 closes the export
  contract, 0.8.4 converges the front-ends, 0.8.5 cleans up (backlog re-cut,
  tier S, 2026-09-11).** 0.8.3's named deliverable — the T-tail empennage
  geometry model — shipped with #25, leaving one L-tier note in flight (#263,
  note 56) behind a 21-row defect-and-polish tail, while note 57 sat **AGREED**
  and gated on "the 0.8.3 cut". Band **B4** is now #263 plus the rows that close
  with it (#173, #176) and #16 as note 56's pre-clean; band **B5** keeps note
  57's D-57.8 sequence with **#241, #242 and #245 inserted before #270** —
  #245's `data/` is the successor channel note 57 §1.3 names for
  `export_report`, so the retirement cannot precede it — and #255 closing
  superseded at #270; new band **B6** (milestone **0.8.5**) carries the
  remaining eighteen, landed once against one front-end. Band **B2** is
  re-chartered to calc, report and process work: the "main sloads GUI
  development" it was named for retires with #270. The whole table is
  renumbered densely (Pri 1–57) and the superseded preambles roll to
  `40_history/44_backlog_state_narrative_to_2026-08-29.md`.

  Two costs are booked rather than discovered: the baseline wave splits
  (#241/#242 move to 0.8.4, so digests regenerate twice — both are column
  additions to files the wave already rewrites), and **#179/#180 are deferred
  as latent**, not as polish — #179's first-match hole has no current producer
  and #180's `getattr` fallbacks are dead defaults, so rule 6 permits the
  deferral, and it is named here so it is a decision. The efficiency claim is
  stated narrowly because it was measured: the convergence avoids **one**
  tier-S row of duplicated effort (#255); `format_value` has zero `app/` call
  sites, #243/#177/#239 are on the survivor, and D-56.2's seven `app/views/`
  consumers were already paid.
