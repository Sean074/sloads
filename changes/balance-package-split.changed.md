- **`modules/balance.py` is the `modules/balance/` package: eight files on the
  banners the single file already carried (#191, review R-23, tier S,
  2026-09-15).** 2,845 lines — the file where every full-airplane change lands —
  split by pure moves along its own section boundaries: `constants.py` (which
  conditions assemble, the two residual acceptances, the stated notes),
  `lateral.py` (the L-7 wing-body sideslip terms, owner of the `body-aero`
  source), `skipped.py` (the F-C7 record), `applied.py` (the applied sets),
  `queries.py` (what a case *is* — handedness, the residual-gate family,
  lateral/ground/powered), `closure.py` (resultants and the six-DOF closure),
  `air.py` (assembly, the handed twin, the case set) and `ground.py` (the ground
  families). The subsystem's own explanation — the three things that had to be
  got right, the seam rule, the lateral and unsymmetrical-tail sections — stays
  whole as the package docstring. No behavior moved with the code: the existing
  oracle and closure gates are the guard, and `build_balanced_cases` returns the
  same cases in the same order, so no deck's subcase sequence changes.
  **The split is invisible to consumers.** 42 names are imported from
  `sloads.modules.balance` across `sloads/`, `tests/` and `export/`, and 11 more
  are reached as `balance.X`; `__init__.py` re-exports every one of them, so not
  a single import line elsewhere changed. `air` and `ground` import each other —
  one assembly machinery, two sources of case — and the cycle is deferred at the
  single call in `build_balanced_cases` rather than broken by moving the twins
  somewhere neither family owns. `skipped_conditions`, a facade that re-runs
  assembly, sits with `run()` in `__init__.py` so the record type does not point
  at the assembly that produces it.
  **The prose that named the file was swept with it** (practice 4): eight SSOT
  owner cells in `CONVENTIONS.md` §7 now name the file inside the package that
  owns the convention, `PROJECT_GUIDE.md` §4's tree lists all eight (its guard
  fails both ways), and `PROGRAM_SPEC.md`, `ch09_balanced_airplane.md`,
  `02_approved_corrections.md` and fourteen design notes were re-pointed —
  including three markdown links into `sloads/modules/balance.py` that would
  have failed `test_doc_links.py`. Twelve `balance.py:NNN` citations lost their
  line numbers rather than gaining new ones: a line number into a 2,845-line
  file was never stable, and three of the twelve had already drifted off the
  statement they cited.
  **Three tools assumed a module was one file, and the sweep fixed all three**
  (practice 4): `test_workflow.py`'s slice sweep read `modules/<name>.py` and so
  saw a split module read nothing at all, `docs/generate_data_dict.py` attributed
  consumers by globbing `modules/*.py`, and `test_deliverable_units.py`'s
  conversion-at-the-boundary guard listed that directory flat — the first two
  failed loudly, the third would have gone on passing while silently no longer
  covering the largest module in the tree. Each now resolves a module to its file
  *or* its package.
