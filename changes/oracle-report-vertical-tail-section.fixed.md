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
