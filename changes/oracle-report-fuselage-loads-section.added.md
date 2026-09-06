- **The oracle report states the fuselage loads (#151 iteration 4, design note 44
  §13/§15, tier L, 2026-09-06).** Section 4, in five subsections and Appendix C,
  built from the `fuselage_loads` step (`NETLOADS`, Reference 1 Ch 15 p103):
  4.1 the fuselage beam and where its mass came from, 4.2 the run register and
  the notation, 4.3 the manual's own **CRITICAL FUSELAGE LOADS** summary
  (Appendix A p198, all seven blocks), 4.4 the closure of the beam and the
  wing-attach fitting loads, 4.5 the distributions. Appendix C carries every case
  at every station, as a view of `sbeam_bridge.body_span_load_csv`'s own rows
  rather than a second assembler. Every load is LIMIT, states the factor
  14 CFR 23.303 prescribes for its case, and is multiplied by nothing.

- **`body_loads` publishes the four critical fuselage conditions it had been
  discarding (design note 44 §15 OR-108, tier L, 2026-09-06).**
  `select_fuselage` had always computed blocks 1, 2, 3 and 7 of p198;
  `run()` returned `ModuleResult(conditions=[])` and threw them away, so the
  oracle GUI's Fuselage Loads page printed *"Body Loads produced no
  conditions."* beside a full station table where the manual prints its summary,
  and every other component page showed its critical cases. One `ModuleResult`
  now feeds the GUIs, the CLI, `load_cases_csv` and report section 4 through
  renderers that were already generic.

- **SELECT publishes the unbalanced pitching moment about the CG (design note 44
  §15 OR-111, tier L, 2026-09-06).** The one field of p198 with no owner in this
  project, and not reconstructible from the printed page by inspection — the arm
  closes against neither the 25 % nor the 50 % MAC until the balanced elevator
  load is subtracted. Recovered from `SELECT.BAS` 5210/5262/5410/5560, cited in
  `docs/20_theory/00_theory_sources.md`, and verified against the printed page on
  both cases (+243,203.9 against a printed 243203.5; −43,169.9 against
  −43170.23). The sign asymmetry between the unchecked and checked forms is the
  original's and is ported as found.

- **The methods statement declares the p198 tail-station deviation (G-OR-70,
  tier M, 2026-09-06).** `report/methods.APPROVED_CORRECTIONS` gains the OR-112
  entry, so every stamped CSV, deck and report states it in band. The register is
  the authority and the guard reads the register, which is what caught the
  omission the moment the entry was approved.
