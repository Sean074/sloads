- **The weight data base gains a seed button that adds rather than replaces
  (#269, design note 57 D-57.7, tier M, 2026-09-13).** WTESTIMA's component
  weights can now be copied into the itemized data base from the surviving GUI,
  which had no such action at all. Of D-57.7's three permitted answers — merge,
  refuse, or state the replacement before the click — the answer is **merge**:
  the seed matches on item name, adds only the components the data base does not
  already name, and never overwrites or deletes an entered row. Seeding twice is
  a no-op, so it is safe to press beside half-finished work. What the click will
  do is built as a plan and shown *above* the button
  (`weight_estimate.seed_plan` / `SEED_CONTRACT`), naming how many rows it adds
  and how many it leaves alone.

- **A seeded row says what it still owes, until it stops owing it (#269).**
  WTESTIMA supplies component weights and nothing else, so a seeded item arrives
  at station 0, untagged, with zero inertias — and `infer_component` then carries
  it on the fuselage beam at zero moment arm, moving the CG and the body shear
  while looking like entered data. `mass_distribution.unplaced_items` /
  `unplaced_warning` name exactly those rows, and both GUIs show the warning for
  as long as it is true rather than once in a success message. The predicate is
  general: a row counted into existence and left blank is the same row.

- **The main GUI's seed button stops being destructive (#269, closing #78).** It
  had replaced `Project.weight.items` wholesale — a data base positioned and
  tagged over an afternoon was one click from gone — and its caption said so
  after the fact. It now asks the same owner the new page asks, so the two
  cannot answer differently and the page that retires at #270 owns none of it.

- **`field_registry.TABLE_SEEDS` (#269)** — `RECORD_SEEDS`' analogue for a
  `…[]` list: a table whose rows a program the project has already run can
  propose, offered by the one registry-driven renderer and stated by the plan
  itself.
