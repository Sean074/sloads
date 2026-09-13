- **The applied-load CSVs state their case identity (#241, 2026-09-08 review §4,
  tier M, 2026-09-13)** — the six delivered applied-load files named each row's
  case by its *description*, and a description is not an identity. LANDLOAD's 33
  ground conditions share eight of them — one description, three loadings, three
  different sets of wheel reactions — so the gear file delivered 33 cases a
  reader could separate into eight groups and no further, and the Baron's two
  `CONTINENTAL IO-550-C` mounts published six conditions under three strings. The
  id that would have settled it, `AppliedLoad.case_id`, was populated on every
  row by every producer and emitted by none; the report's own applied appendix
  printed it while the file beside it did not, so the page and the file were not
  in fact the same row. All six files now lead with `Case ID`, `Case` and
  `Loading`: the minted id the load-case index is keyed by, the description, and
  the named CG the case was computed at (blank where the case names none, never
  guessed). The two identity strings are read off the case's own `CaseRef` by one
  owner, `report/applied.case_identity`, rather than by each of the five
  producers spelling the read for itself, and the header block of every file says
  what the three columns are and that `Case` is not unique. The twin's half of
  the finding was not a file defect at all: the per-engine tag was the engine
  *designation*, which two engines of one model share, and it was applied to the
  title *after* the `CaseRef` was minted — so the index itself described `EM-01`
  and `EM-04` in the same words. `modules/engine.engine_tags` now mints one
  distinct label per installation — the designation where it already separates
  them, plus the side (off the engine's own butt line) where it does not, plus
  the engine's position in the rare case that still collides — and the tag goes
  on before the id is minted. Nothing renames on an installation whose engines
  differ, so no single-engine title in any shipped example moved. A delivered id
  the index lists under a shorter name now joins through one owner too,
  `case_ids.index_case_id`: a handed twin (`W-05R`) and the 23.371(b) gyro
  condition's four sign combinations (`EM-06a…d`, which one `ConditionResult`
  cannot carry four `CaseRef`s for, Step D1) are suffixes on an id that *is*
  listed, and `report/render`'s minter reads the same suffix alphabet that strip
  removes. Guarded by `tests/test_applied_case_identity.py`: the round trip —
  every delivered `Case ID`, on every bundled example and all six components, is
  an id the case index names, and every `Loading` cell is that index row's own
  `CG` — plus the two collapses asserted directly (33 ids under 8 descriptions;
  six mounts under six), the gyro suffix stated rather than tolerated, and an AST
  walk of `report/applied.py` that fails any `AppliedLoad` construction which
  does not state its identity, so a producer added later cannot half-fill the
  columns. The Imperial baseline gained the gear and engine applied channels in
  the same change: four of the six were digested and two were not, which is how
  the bytes of the file with the most cases in it came to move unguarded. Every
  digest that moved is one of those six files, the engine module's own CSV/text
  output on the three multi-engine examples, and their case index.
