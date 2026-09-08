- **Appendix A is the balanced V-n condition register (design note 44 §23, tier L, 2026-09-07).**
  Every balanced flight condition the envelope produces — 80 rows on
  `ga6_normal`, 180 on `baron_58`, 200 on `concept_regional_jet` — reproducing
  Ref 1 Appendix A p179 (the mass cases) and p180-185 (the balanced-flight
  columns), with the manual's per-block `FOR CG1 FS= … WL= …` headings turned
  into CG, configuration and altitude columns so the table is flat. The document
  named 23 critical conditions and never showed the reader the 80, 180 or 200
  they were selected out of; a selection whose candidate set is not published is
  a claim, not a result. The four component columns mark which rows were
  selected, and as what: `W-03`, `F-01`, `VT-01, VT-02, VT-03`.
- **`<project>_vn_conditions.csv`** ships in the export bundle and the manifest —
  the appendix as a file, all nineteen columns in one flat row, built from the
  same rows the page prints.
- **Section 2.2 gains a `CG` column**, the positional id the conditions are
  indexed by, so a reader meeting `CG1` in Appendix A can find `fwd gross` in
  Section 2. One owner, `cg_cases.flight_case_ids`; the case *name* remains the
  identity everywhere else.
- **`NX` is printed beside `DX`** in the conditions table — the inertia drag
  factor `−DX/W` the drag leaves the balance as. The appendix states in one
  paragraph that thrust is not modelled and why the airplane is nonetheless in
  longitudinal equilibrium.
