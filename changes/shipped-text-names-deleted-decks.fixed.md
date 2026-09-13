- **The shipped text stops naming the export package note 56 deleted (#274, tier
  S, 2026-09-12).** D-56.2 deleted the five per-component decks and D-56.8
  unshipped the assembled one, and the sweep that closed note 56 reached the
  standard docs but stopped short of the rendered strings — so the actively-used
  deliverable went on describing artifacts the package no longer builds. Seven
  statements a reader actually sees were false: the oracle report's §7 paragraph
  called the assembled model *"this deliverable's primary load output"* and the
  per-component decks *"analysis views cut out of this model"*; its wing-root
  note attributed the `lra-sob` tagged reporting node to *"the wing stick deck"*
  when `export/lra_model.py` writes that tag at GID 25001; its gear section and
  the Landing Loads page both sourced the reference-point reaction to *"the
  assembled deck"*; the Balanced Cases page repeated the first two claims in its
  caption; the Export page offered *"FORCE/MOMENT cards (and the wing stick
  model)"* and pointed the `MyyAxis` column at a span CSV that is gone; and the
  Configuration & Layout side-of-body help named the stick deck as the reporting
  node's consumer. Each is re-cut onto what the bundle carries — the LRA beam
  model as the solver artifact, the assembled set as the internal reference
  resultant its transfer is gated against — with the free-free equilibrium
  argument (G-OR-72) unchanged: it was always a claim about the model, never
  about which file it shipped in.

- **The same sweep runs through the deck's own header and the docstrings behind
  it (#274, tier S, 2026-09-12).** The LRA model's `$` header told its reader
  that *"the assembled balanced deck remains the equilibrium proof and the
  per-component decks the oracle views"* — text inside the one deck that ships —
  and its per-case and constraint comments sourced the residual to a deck no one
  receives; all three now name the model that carries them. Present-tense
  docstrings naming the deleted decks are corrected in `export/lra_model.py`,
  `export/bands.py`, `report/applied.py`, `report/tables.py`, `report/render.py`,
  `report/oracle_sections.py`, `modules/balance.py` (whose copy of the
  free-body-cut rule now points at `CONVENTIONS.md`, which retired it in place)
  and `app/views/loads_plots.py`. Only `sbeam/lra_model` moves in the Imperial
  baseline, on the four fixtures that build one, and only in `$` lines: every
  edit sits inside a `comment()` argument, which emits nothing else. **One thing
  is deliberately not fixed:** the case index still ships the headers
  `LOAD/SUBCASE (component)` and `LOAD/SUBCASE (assembled)`, naming two decks
  that no longer exist. Renaming them moves a shipped CSV header across three
  owners and is **#209**'s decision, not this sweep's, so `report/tables.py`
  states the mismatch where the columns are defined rather than leaving the next
  reader to infer it.
