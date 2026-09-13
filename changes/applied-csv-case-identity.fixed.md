- **Every applied-load CSV row now states which case it is (#241, tier M,
  2026-09-13).** The files led with a `Case` column holding the case's
  *description*, which is prose and is not an identity: LANDLOAD's 33 ground
  conditions collapsed onto the eight descriptions they share, so a reader
  loading `landing_gear_applied_loads.csv` could not tell the aft-max-landing
  3-wheel case from the forward-light one, and a twin's two engine mounts shared
  all three of theirs. The minted `case_id` was populated on every row and
  emitted on none. All six files now lead with `Case ID`, `Case` and `Loading` —
  the id the load-case index is keyed by, the description, and the named CG the
  case was computed at — so a delivered row joins to the condition, CG, speed,
  altitude and FAR paragraph the index states for it. Both strings are copied
  off the case's own `CaseRef` by one owner (`report/applied.case_identity`),
  and the file's header block says what each column is.

- **A twin's two engine mounts are told apart, in the index as well as the file
  (#241).** The Baron fits two `CONTINENTAL IO-550-C`, and the per-engine tag on
  each condition title was the designation alone, so `EM-01` and `EM-04` carried
  identical descriptions and the load-case index described them identically.
  `modules/engine.engine_tags` now qualifies a shared designation with the
  engine's side, read off its own butt line, and the tag is applied **before**
  the `CaseRef` is minted. An installation whose engines already differ is
  untouched, so no shipped single-engine title moves.

- **`case_ids.index_case_id` (#241)** — the one owner of which suffixes a
  delivered case id may carry over the id the case index lists: a handed twin
  (`W-05R`), and the 23.371(b) gyro condition's four sign combinations
  (`EM-06a…d`), which one `ConditionResult` cannot carry four `CaseRef`s for.
  `report/render`'s sub-case minter now reads the same suffix alphabet it strips.

- **The Imperial baseline pins the gear and engine applied sets (#241).** Four of
  the six applied channels were digested and two were not, so the bytes of the
  file with the most cases in it moved unguarded.
