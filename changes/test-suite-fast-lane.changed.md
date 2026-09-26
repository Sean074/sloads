- **The test suite builds each fixture's shared bundle once per worker, and the per-item gate skips a marked slow lane (#308, tier S, 2026-09-26).**
  `imperial_baseline.artifacts` -- the whole Imperial bundle of one example,
  rebuilt from scratch in seven test files -- and the deck, document, package
  and report-figure builders `test_deck_basis` and `test_figures` repeated per
  test are memoised per test process and hand out copies; the frozen Imperial
  baseline shows no byte moved. A registered `slow` marker holds the 28
  irreducible tests (the PDF compiles, the GUI journeys, the whole-analysis
  planform sweeps); `solo_close.sh` runs `-m "not slow"` per item, and
  `--full-gate`, CI and the milestone merge run everything. Measured 2026-09-26 on the 8-core MacBook Air: the full suite 30 min 02 s -> 12 min 39 s, the per-item fast lane 11 min 49 s. The
  issue opened and closed inside this step, so it has no backlog row.
