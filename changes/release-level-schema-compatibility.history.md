- **A project file is readable if a release wrote it: from 0.8.7 on every release's schema is recorded and frozen, and the hop chain must reach it without a gap; the v55–v69 hops, their fixtures and the readers' legacy branches are gone (#310, tier M, 2026-09-26)** —
  Owner ruling (in session): compatibility is kept at release level, starting
  at 0.8.7. A file any release from 0.8.7 on wrote stays readable by every
  later release; a schema version that lived only on a development branch is
  never promised. Before this the gate read v55 onward through fourteen hops
  that carried files no one holds (the project is pre-production and the owner
  keeps no project files outside `examples/`), and #276 was waiting for a
  schema hop to ride. `sloads.migrations` now keeps the gate and the machinery
  (`migrate`, the `MIGRATIONS` chain, `migration_notes`) and adds
  `RELEASED_SCHEMAS`, empty until the 0.8.7 cut. `SUPPORTED_FLOOR` is the
  oldest released schema, or the current one while none is recorded. The rule
  is held by `tests/test_migrations.py`. Every release the changelog names from
  0.8.7 on must have a row, so the cut's new header turns the suite red until
  it does. Every row's frozen `tests/fixtures_schema/release_<X.Y.Z>.json` must
  load. And the chain must run from the floor to the current version without a
  gap, since the reader drops unknown keys and a bump with no hop would misread
  a stale file rather than refuse it. The step is in `RELEASE_PROCESS.md` §4.
  With no hop left to reach them, the readers' legacy branches went too: the
  singular `engine` key, a V-n point's singular `case_ref`, the retired
  stall-speed and `units` keys, the gear built from retired layout fields, and
  the fuselage outline built from the parametric length/width/height (with
  `default_fuselage_outline`, now unused). The reader no longer takes those
  three scalars at all, since they are never written. One of the branches was
  a live defect: a surface's `ref_axis_pct` entered as 0.25 read back as "not
  entered", a rule written for files the pre-v52 writer saved. An entered 0.25
  now stays entered. No shipped example carried any of these shapes, and no
  load, deck or digest moves.
