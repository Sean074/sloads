## Step 155 — The oracle report states the fuselage loads (tier L, 2026-09-06)

**Objective.** Give the oracle technical report its second load-bearing section: the
fuselage loads, as five subsections and a lettered appendix, built from the
`fuselage_loads` step (`NETLOADS`, Reference 1 Ch 15 p103) without the report computing
anything of its own.

**Agreed first.** Design note 44 §13 (**OR-94 … OR-102**), §15 (**OR-108 … OR-113**) and
§16 (**OR-114/OR-115**), with the carry-through half answered by design note 50 — all
settled with the owner in session on 2026-09-05, before any code. Gates **G-OR-53 …
G-OR-59** and **G-OR-64 … G-OR-68**.

**Deliverables.**
- `report/oracle_sections.py` — 4.1 the fuselage beam, 4.2 the run register and notation,
  4.3 the critical fuselage loads, 4.4 the beam closure and the wing-attach fitting loads,
  4.5 the distributions, and Appendix C's station table. The subsections are titled here
  and numbered by `subsection_number`, the one numbering owner.
- `report/oracle_content.py` — `BODY_LOAD_STATIONS` in third appendix position, and
  `"fuselage_loads"` in `IMPLEMENTED`, which is the whole of the switch: the OR-32
  placeholder that had been holding the slot becomes a section.
- `modules/body_loads.py` — `run()` publishes the p198 conditions; `critical_fuselage_conditions`
  and `case_list_source` publish the case identity and the provenance a consumer needs
  without a second call to SELECT.
- `modules/select.py` — the unbalanced pitching moment about the CG on the four maneuver
  conditions.

**Key decisions.**
- **Five subsections rather than section 3's four.** §15 gave the section a summary an
  analyst turns to first, and folding the manual's own summary into a subsection about
  closure machinery would have made it a footnote to the machinery.
- **The section projects the published `ModuleResult`; the builder is read for the station
  table only.** This is OR-95 rewritten rather than withdrawn, because it turned over: the
  original ruling had section 4 read `build_body_loads` throughout, on the grounds that
  there was no result to project. There was no result because the module was discarding
  one, which is the defect below.
- **`body_loads.run()` returns the four conditions it already builds (OR-108).**
  `select_fuselage` computes blocks 1, 2, 3 and 7 of p198 — labels, FAR references, V-n
  case numbers and three quantities each — and `run()` returned an empty `ModuleResult`,
  so the oracle GUI's Fuselage Loads page said *"Body Loads produced no conditions."*
  beside a 92-row station table. One owner, not four: the same result now feeds both GUIs,
  the CLI, `load_cases_csv` and the report, through renderers that needed no edit. The
  alternative — each surface calling `select_fuselage` for itself — is rule 3's failure
  mode with a deliverable on the end of it. **Admitted under OR-15** by the owner on
  2026-09-05; additive, no value changes, and the frozen manifest is updated in the same
  commit per G-OR-9.
- **The unbalanced pitching moment is published from SELECT with its equation recovered
  and cited (OR-111).** It was the one field of p198 this project could not state, and it
  is *not* reconstructible from the printed page by inspection: the arm closes against
  neither the 25 % nor the 50 % MAC until the balanced elevator load is subtracted. From
  Appendix C, `SELECT.BAS` 5210: `PITCHMOMH5CASE = -(LT50UPTEUNCK - LT50) * (XT50 -
  XXCG(H5CASE))`, and 5410 for the checked pair. The increment is measured from the
  balanced 50 %-chord load and the arm runs from the CG to the 50 % tail MAC; verified
  against the printed page on both, `-(-1346.496 - (-113.6319)) × (270.357 - 73.09) =
  +243,203.9` against a printed `243203.5` and `-218.3436 × (270.357 - 72.64) = -43,169.9`
  against `-43170.23`. **The sign asymmetry is the original's** — the unchecked expression
  negates and the checked one does not — and is ported as found, not tidied. Second
  **OR-15 admission**, over `sloads/modules/select.py`.
- **`FS 50 PERCENT HORIZ TAIL` prints the real station (OR-112).** The manual prints `0`
  in both fuselage blocks while its own tail-loads echo states `270.357`. OR-111's
  arithmetic settles it independently: the moment closes only with the real station, so
  the original computed with it and printed zero — a defect in its print, not a modelling
  choice. Registered in `docs/20_theory/02_approved_corrections.md`, so an analyst
  comparing against the page finds it explained rather than discovering it.
- **Blocks 4 and 5 are read from SELECT and carry their reference (OR-109/OR-110).** The
  manual's own device — *"SEE HORIZONTAL TAIL LOADS FOR FURTHER DATA"* — is the answer to
  the two-pages-one-number objection: the reader gets the value where the fuselage question
  is asked and is told where it is derived. Weight and CG are case identity and are stated
  by lookup from the case's CG name, which is why `CG4 → 73.09 in` and `CG3 → 72.64 in`
  reproduce p198's printed `XCG` to the digit.
- **The advisories are carried because each names something true (OR-113).** Block 7's
  pitching-acceleration warning states a limitation this analysis still has: Ch 15 resolves
  the fuselage inertia into a linear and a pitching load factor, and only the linear half
  is modelled (**M4-21**, `θ̈ = 0` on these balanced trim cases). Reproducing it therefore
  states a true property of the delivered numbers rather than decorating them, which is the
  one good reason to carry printed prose at all.
- **The section states what it does not deliver rather than tabulating zeros (OR-100).**
  Ch 15's beam is a symmetric-flight vertical solve, so there is no lateral shear and no
  lateral bending here; a column of zeros would read as a measured zero. The notation table
  names the three symbols the section uses and nothing else.
- **4.2 states its own load-factor sign convention, and states that it is not section 3's.**
  Section 3 prints the inertia load factor and section 4 the airplane's own, so a reader
  carrying one section's rule into the other reads every condition backwards. This is
  OR-58 applied to a section whose convention differs, and it is why the sentence is
  written out here rather than cross-referenced.
- **An assumed spar station is stated beside the numbers it sized (OR-97).** The
  wing-attach fitting loads are the sizing loads for the fittings, and on both report
  fixtures they are computed against a carry-through nobody entered. The provenance is a
  column of the fitting-load table, in the same visual field as the loads, and it is stated
  as a fact about the airplane rather than about the tool. The structural half of the
  finding was fixed rather than filed, by design note 50: the carry-through is an entered
  fuselage station, so the field a reader would go looking for exists.
- **No sloads load carries a Subpart D special factor (OR-114/OR-115).** 4.4 states the
  consequence where the fitting loads are printed — the casting, bearing, fitting and
  hinge factors of 23.619/621/623/625 qualify a material allowable or a fitting's strength
  at the stress analysis, not the external load a loads analysis delivers, and a fitting
  factor applied here would be applied twice.

**Test.** Twenty-one gates in a new `tests/test_oracle_report_fuselage.py`, one file for
one section's gate set. Among them: the five subsections are numbered by the numbering
owner and the appendix letters to C behind the reserved A and the wing's B; every load
column carries no `-ULT` **and** every load table carries an `SF` column, asserted in both
directions; the printed value is the module's own unscaled result; 4.1 states its beam
derived and prints its total; a project with no beam mass renders the `ABSENT` state in
both the section and its appendix and still builds a whole document; the fitting table
reads `assumed` on the shipped fixture and `entered` on a project that enters its spar
stations, through the projection; a constructed closure-artifact project states its state
and plots nothing; the register names its path, its sign convention and its one
negative-load-factor condition from the analysed set; Appendix C and
`body_span_load_csv` agree row for row on GID, station, load and factor; `body_loads`
publishes one condition per printed block on both fixtures, each with its FAR reference and
V-n point; blocks 4 and 5 equal SELECT's own values by comparison rather than by both
matching a literal; and OR-111's two reconstructions reproduce the printed page within the
oracle tolerance with the 50 % tail station entered and never zero.

Two existing wing gates were restated rather than relaxed, both position-dependent
assertions that a third appendix broke without saying anything untrue: the appendix
lettering test now slices from the first appendix instead of from the end of the document,
and the landscape test counts one balanced environment per landscape section instead of
exactly one. The frozen Imperial baseline moves on two channels only — `body_loads` and
`select`, in every example — which is the shape an additive publication should have.
