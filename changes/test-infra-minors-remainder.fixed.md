- **A test file's self-runner starts, every test file has one, CI cannot drop the slow lane in silence, a misspelt marker is an error, and a released file's values survive the read (#322, tier S, 2026-10-02).**
  The remainder of the 0.8.7 review's test-infrastructure minors; the
  ENGLOADS spelling and `test_rolling_conditions.py`'s items rode #318. The
  three memoised builders in `tests/test_deck_basis.py` handed out a shallow
  copy whose `ModuleResult`s every test in the worker shared; they now return
  `copy.deepcopy`, and a test edits one and reads the next caller's.
  `addopts` gains `--strict-markers`, and `tests/test_ci_conformance.py`
  refuses a `ci.yml` pytest step that deselects `slow` or selects any marker
  but the solver job's `roundtrip`. The shadowed first copy of
  `test_every_example_round_trips_unchanged` is deleted, so the file's section
  headers match its docstring. Five test files gained the `__main__` runner
  CLAUDE.md requires, and sweeping that class found the runners that existed
  broken: 26 passed `-p no:xdist`, which unloads the plugin that owns
  `addopts`' `-n auto`, so each failed at startup with "unrecognized
  arguments: -n". They pass `-n 0`, as `pyproject.toml` and
  `00_program_overview.md` now advise, and a guard requires a runner in
  every `tests/test_*.py` and refuses `no:xdist` in one. The frozen
  `release_<X.Y.Z>.json` test checked only that the file loads, which a hop
  missing a later rename passes because the reader drops unknown keys; a new
  test requires every scalar of the migrated file back at its path with its
  value. No delivered load moves.
