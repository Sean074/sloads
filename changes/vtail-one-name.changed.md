- **One surface, one name: `fin_*` identifiers retired for `vtail_*` (#223,
  tier S, 2026-09-09).** The mechanical sweep of the 2026-09-06 ruling
  (`CONVENTIONS.md` §7.2): every production identifier spelling the vertical
  tail "fin" — `fin_root`, `fin_root_waterline`, `FinRoot`, `FinCase`,
  `fin_sets`, `fin_load`, `ATTACH_FIN_TIP` and their kin — renamed to the
  `vtail` token across `sloads/`, the front-ends and the tests, first in the
  tail-geometry cluster so #219/#220/#54-series edits land on the agreed
  names. Serialized names are deliberately kept (`cy_beta_fin`/`cn_beta_fin`
  schema fields; the `balanced_fin_load`/`fin_angle_of_attack` LoadValue keys
  — renaming those is a schema/baseline change, not a spelling fix), prose may
  still say "fin", and the guard
  `tests/test_tail_geometry.py::test_no_fin_identifier_survives_or_returns`
  walks every production identifier so the seam cannot reopen. No load, deck
  byte, or delivered file changes.
