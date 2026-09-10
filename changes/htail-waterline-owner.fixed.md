- **The conventional h-tail no longer sits on the wing-root waterline (#261,
  design note 54 D-54.4, tier M, 2026-09-10).** `tail_geometry.h_tail_waterline`
  is completed: a conventional tail with no entered `h_tail_z` now takes the
  h-tail **mass items' weight-weighted `z`** (ASSUMED, basis `mass-item`)
  before falling back to the wing-root plane, now loud and last — an entered
  statement of where the surface's mass sits beats a placeholder printed as an
  airplane coordinate. And the **two-spellings rule**: a declared T-tail whose
  entered `h_tail_z` contradicts the fin tip by more than `PLANFORM_TOLERANCE`
  of the fin span gets the fin tip *and an in-band note naming the entered
  value NOT USED* (the #260 E5 pattern made loud). Swept per rule 4: the
  three-view sketch (`configuration.tail_planform`) now reads the owner with
  the project in hand instead of its own entered-else-wing-root copy, and the
  report's provenance sentences gain the mass-item and NOT-USED branches.
  **Delivered coordinates move**: `cessna_210`'s h-tail rises 86.0 → 100.0 in
  and `concept_heavy`'s drops 100.0 → 90.0 in (station points and exported
  `GRID`s only — the h-tail loads in `fz`, so no load moves); the Imperial
  baseline re-froze `cessna_210`'s three deck channels. Both moves are the
  note 54 gate-3 fixes, pinned in `tests/test_tail_geometry.py`.
