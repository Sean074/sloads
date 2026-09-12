- **The applied load set gets its right address, and the export bridge ceases to
  exist (note 56 D-56.1, tier M, 2026-09-11).** `sbeam_bridge.py` — 1,404 lines by this
  point, 3,091 when the note was written — moved whole to
  `sloads/report/applied.py`. The note described D-56.1 as a three-way split, and
  by the time it ran two of the three ways were already done: slice 1 took the
  load-output contract statements to `deck_format`, slice 2 took the report
  tables to `report/tables.py`, and slice 3 deleted the five per-component decks.
  What remained was one group — the applied-load model, its station numbering and
  the side-of-body internal loads — and the file's own docstring had said so
  since slice 3. So it moved under its right name rather than being split at a
  boundary that no longer existed. `sloads/export/` is **5,769 lines across 14
  modules**, from 8,603 across 15 when the note opened.
- **No shim, and two guards that keep it that way.**
  `test_no_module_named_sbeam_bridge_survives_the_move` refuses an importable
  `sbeam_bridge` at either package. `test_the_applied_load_set_has_one_address_and_the_export_package_is_not_it`
  is the slice-2 guard inverted: every name resolves from `report.applied` and
  none is reachable from `sloads.export`. An alias would have put one name at two
  addresses, which is the condition note 56 exists to remove — and it is exactly
  what let the per-component deck writers keep a public surface for two
  milestones after the decks stopped being deliverables.
- **Two sweeps followed the code rather than the directory.** The band registry's
  base-constant sweep walked `sloads.export` only, so on the day the numbering
  moved it would have gone quiet on **seven of the registry's own bands** —
  `wing-stick`, the two body runs and the four tail runs. That is precisely the
  blind spot `bands.py` exists to close, and it would have opened silently. It
  now walks the export package plus `report.applied`. The CH-2 no-silent-defaults
  AST sweep moved the same way, and stays a *named* file set rather than a second
  package walk: the rest of `report/` renders whatever a project happens to carry
  and reads optional slices with defaults by design, so extending the rule to the
  whole directory would have been a different decision wearing this one's
  clothes. `CONVENTIONS.md` §7's row is re-cut to state both halves.
- **One import points the wrong way, deliberately and for one slice.**
  `export/mass_cards.py` reads `beam_station_gid` from `report.applied` at module
  level — an `export → report` dependency, which is backwards. It is left visible
  rather than hidden behind a function-level import because **D-56.6 deletes
  it**: with each `CONM2` on a `GRID` at its own item's CG, no mass card states a
  beam station at all. A lazy import would have made a one-slice fact look
  permanent. There is no cycle either way.
- **Five stale citations swept with it (rule 4).** The class is a citation that
  outlived the code it named: `equilibrium.CardTotals` justified itself by two
  decks D-56.2 had deleted; `mass_cards` and `balanced_deck` both cited
  `sbeam_bridge.stamped`, which slice 1 had moved to `deck_format`;
  `PROGRAM_SPEC.md` cited `gear_report_csv` and `filter_by_selected_case_ids` at
  their pre-slice-2 addresses, and `CONVENTIONS.md` cited `LOAD_ID_COLUMN` at
  its. All five now name where the code is.
- **What did not happen here.** D-56.9 is a separate slice: `AppliedLoad.gid` is
  still allocated from the applied-load model's own bands, so the `wing-stick`
  `GID 1` hole stays open and the registry has not collapsed to its final count.
