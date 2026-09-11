- **The load-output contract's statements get one owner, and eight copies of the
  solver unit set collapse to it (note 56 D-56.1, tier M, 2026-09-10).**
  `export/deck_format.py` — the card-writing primitives module #15 created for
  exactly this defect class — now also owns *what a load is stated to be*:
  `solver_units`, `basis_sentence`, `load_label`, `ult_label`, `case_sf` and
  `SUITE_SF`, promoted out of `sbeam_bridge`'s underscore namespace under the
  names the writers actually mean. The authority for *which* factor a case
  carries is unchanged — `safety_factors.py` (M4-8 / G-11) decides, these only
  render it.

  `deliverable_units(system, Channel.SOLVER)` — the choice of which unit set a
  deck may be written in — had been copied into a private `_units` helper in
  **four** export modules (`sbeam_bridge`, `balanced_deck`, `roundtrip`,
  `lra_model`) and written inline in **four** more (`mass_cards` ×4,
  `lra_import`, `workbook`, `coordinates`). All eight now read one owner, and
  `tests/test_deliverable_units.py::test_only_deck_format_resolves_the_solver_channel_in_the_export_package`
  fails the day a ninth appears (rule 3: the owner *and* the drift guard).

  **Found while doing it: the rename would have silently blinded G-OR-71.**
  `tests/test_limit_channel.py` scans the whole tree for a surviving
  limit→ultimate multiply, and its pattern matched `* _sf(` and `\bsf\b` — but
  `\bsf\b` does **not** match inside `case_sf`, because `_` is a word character
  and there is no boundary before `sf`. A text guard that matches nothing still
  passes, so nothing in the suite would have gone red. The pattern now names
  `case_sf` explicitly, including its dotted form, with three teeth assertions
  and the reason recorded in the source.

  No delivered byte changes: the Imperial digest's 330 channels are identical,
  and the whole suite is green.
