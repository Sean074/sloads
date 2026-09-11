- **The load-output contract's statements get one owner (note 56 D-56.1, tier M,
  2026-09-10)** — The first slice of note 56's export reduction, and a
  precondition for the rest of it: D-56.1 splits `sbeam_bridge.py` three ways,
  and the helpers both halves need had to have a home before either half could
  move, or the split would have manufactured a copy rather than removed one.
  `deck_format.py` was already that home by its own charter — created at #15
  (CH-4) because five sibling writers were reaching across the package to import
  its format helpers *through the underscore* — and its docstring explicitly
  deferred the contract statements to `sbeam_bridge` "where the load-output
  contract lives". That sentence is what changed: `solver_units`,
  `basis_sentence`, `load_label`, `ult_label`, `case_sf` and `SUITE_SF` moved,
  and the same reasoning that justified the module now covers them.
  `safety_factors.py` remains the authority for the factor itself; these render
  what it decides. The measured duplication was worse than the note recorded:
  the solver-channel resolution existed in **eight** places — four private
  `_units` helpers that agreed only because nobody had yet edited one of them,
  and four inline calls in `mass_cards`, `lra_import`, `workbook` and
  `coordinates` — all swept in the same change under rule 4, with a drift guard
  scoped to `sloads/export/` (`report/` names the channel legitimately, where it
  *compares* the human and solver sets rather than picking one). The finding
  that mattered was not the duplication but a guard: **G-OR-71**, the whole-tree
  scan for a surviving limit→ultimate multiply, keys on source text, and
  renaming `_sf` to `case_sf` would have slipped straight past its `\bsf\b`
  alternative — `_` is a word character, so there is no boundary before `sf` —
  leaving the scan passing and toothless against the exact spelling it now had
  to catch. It is fixed with its teeth extended and the reason written into the
  test, and it is a standing caution for the rest of note 56, which renames and
  relocates a great deal more: a text guard does not fail when it is bypassed,
  so every one it passes over must be re-read against the new spelling rather
  than trusted to go red. Deliverables are byte-identical — the Imperial
  digest's 330 channels, the two reports and every CSV — which is note 56's
  gate 8 asserted at the first opportunity rather than at the end.
