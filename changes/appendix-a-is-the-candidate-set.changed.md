- **The reserved "Input echo" appendix is retired, not relettered (design note 44 OR-194, tier L, 2026-09-07).**
  A project
  file is already an exact, machine-readable echo of the inputs; a table
  transcribing it is a second copy that can disagree with the first, so the
  document names the file instead. Slot A was *filled* rather than vacated, so
  Appendices B through F did not move — which is the outcome the reservation
  (note 44 OR-50) existed to protect.
- **`VnPoint.case_ref` becomes `VnPoint.case_refs`, a list** (schema 63 → 64,
  identity hop). A V-n point is routinely selected as the source of more than one
  critical condition and the single slot kept only the last write.
- **`aero_curves.inertia_drag_factor` is the one owner of `NX = −DX/W`**,
  replacing the two spellings in `modules/select.py` and
  `modules/wing_inertia.py`. No delivered number moves.
- **One OR-15 admission** (note 44 OR-203, granted 2026-09-07), scoped to
  `modules/select.py` (two lines, one import) and `modules/wing_inertia.py` (one
  line, one import). No arithmetic is touched and no delivered number moves — the
  frozen Imperial digests are unchanged, which is the measurement that says so.
  Both files are re-pinned with the scope recorded beside the hash.
