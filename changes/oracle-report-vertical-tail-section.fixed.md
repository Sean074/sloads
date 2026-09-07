- **Two entered fields the oracle document depends on were reset before it read them
  (note 44 OR-134a, tier L, 2026-09-07).** The document is a function of
  `reduce_to_oracle_inputs` (OR-43), so a field outside the oracle input set is
  silently replaced by its dataclass default between the project and the page — not
  absent, *different*. `geometry.parametric.tail_type` was reset to `CONVENTIONAL`, so
  every airplane read as a conventional tail and the withholding above fired on nothing;
  `geometry.surfaces[].ref_axis_pct` was reset to the 25 % default, so the document
  stated its torsion about the quarter chord while every other consumer used the entered
  40 % — `ga6_normal`'s horizontal-tail root torsion **60.8 → 34.5 lb-in**,
  `concept_regional_jet`'s **4141.7 → 3645.3**, and every Appendix D/E applied-load `X`
  **3–6 in** off the deck card the appendix states it is the same load as. All seven
  shipped examples enter the axis. Both fields are now `supplied` and render in the
  registry-driven oracle form; no frozen file was touched.

- **The wing torsion is stated about the axis OR-51 ruled it is stated about (tier L,
  2026-09-07).** Section 3's gate asserted `25% chord` and its docstring explained the
  reset above as a decision — *"the report cannot print a 40 % chord torsion"* — where
  OR-51 had ruled the opposite in as many words: *"`ga6_normal` enters `ref_axis: 0.4`,
  so its wing torsion is delivered about the LRA 40 % chord … the report must not print
  one and call it the other."* The gate now reads the axis from the project rather than
  pinning a literal.

- **Section 6 no longer borrows section 5's flaps-extended absence (note 44 OR-131,
  tier L, 2026-09-07).** The flaps-extended gust of 23.425(a)(2) is a *horizontal* tail
  requirement with no counterpart in 23.441 or 23.443; stating it under the vertical
  tail described an absence that is not that surface's. Caught by the OR-131 gate on the
  first build of the mirror.

- **The vertical tail's loads reference axis was drawn along its root, not up its
  span (owner, 2026-09-07).** `WingStationLoad` documented its coordinates as airplane
  axes, and for the wing and the horizontal tail they are. On the **fin** they are not:
  `y` is the span coordinate in the surface's own plane and `z` is the root waterline
  that span is measured from. Section 6.1 read the names at face value, so Figure 24
  drew the axis as a flat row of markers along the constant 111.5 root waterline
  instead of climbing 112.9 → 167.1 up the fin, and its station table labelled the
  height above the root a *butt line*. Both now resolve the point through
  `export.coordinates.tail_station_to_airplane` — the owner the exported deck and
  Appendices D and E already used, which is why those were right — so the figure, the
  table and the FORCE card place a station at one point by construction. The analysis,
  the decks and the CSVs were never affected.

- **The tail and wing loads-reference-axis figures legended their stations "Design CG
  cases" (tier M, 2026-09-07).** `PlotData.points_label` was left at the V-n figure's
  default, so three figures named a different figure entirely — the defect that field
  was added to prevent. They say "Load stations".

- **Table columns could print on top of one another (tier M, 2026-09-07).** The width
  solver documents a floor — a column is never narrower than its longest unbreakable
  token, because a `p` column wraps between words and never inside one — and its last
  fallback scaled every column past it. On `ga6_normal` the `14 CFR` column of Table 25
  needed 63pt for `23.423(a)(1)` and was given 26, so the regulation printed over the CG
  case as `23.423(a)(1)G4` and a reader could not tell which CG case the condition was
  run at. The floor is absolute now; a table that cannot be set upright at either size
  is turned onto a landscape page instead (owner, 2026-09-07).

- **Every landscape appendix was sized for a portrait page (tier M, 2026-09-07).**
  Column widths were computed against `TEXT_WIDTH_PT` regardless of orientation, so
  Appendices B, C, D and E were squeezed into two-thirds of the page they print on —
  and the Baron's applied-wing-load table fell below its own floor for want of space
  that was there all along. The landscape width is now measured (652.85pt of
  `\linewidth`, not the 719.9pt the paper size suggests: `includeheadfoot` takes the
  running head and footer out of the block), and a section's orientation is inherited by
  its subsections, where the appendix tables actually live.

- **`fancyhdr` warned once per page that the running head did not fit (tier S,
  2026-09-07).** 77 identical warnings on the report's own example, in both report
  renderers, because a `\small` head is taller than the 12pt default `\headheight`.
  Declared. Building `ga6_normal` now emits 4 overfull-box warnings, worst 0.79pt,
  against 33 overfull plus 77 `fancyhdr` before.
