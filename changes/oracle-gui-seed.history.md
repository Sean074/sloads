- **The weight-estimate seed is built fresh, and built merging (#269, design
  note 57 D-57.7, tier M, 2026-09-13)** — the surviving GUI had no way to copy
  WTESTIMA's component weights into the itemized data base WTONECG and WTENV
  actually read, and the retiring GUI had one that replaced every entered item
  and captioned the replacement underneath the button that had already done it
  (#78, C210-9). D-57.7 refused to port the defect into its new home and fix it
  later, so both halves land in the first version. Of *merge, refuse or
  replace*, the answer is **merge**, chosen because it is the only one of the
  three that is idempotent: the seed matches on item name, adds only what the
  data base does not already name, never overwrites and never deletes, so
  pressing it a second time after positioning half the rows picks up the other
  half and disturbs nothing. The plan is built before the click and states
  itself above the button — how many rows it adds, how many it leaves alone,
  and that nothing is replaced. The second half is the one the numbers care
  about: WTESTIMA gives weights and nothing else, so a seeded row arrives at
  station 0 untagged, where `infer_component` carries it on the fuselage beam
  at zero moment arm and it moves the CG and the body shear while looking like
  data the user entered. Both GUIs now show `mass_distribution.unplaced_warning`
  as a warning that persists until each row has an `x` station and a
  `component` tag, and the predicate is written generally — a row counted into
  existence and left blank is the same row. Every part of that is owned in
  `sloads/` (`weight_estimate.SEED_CONTRACT`/`SeedPlan`/`seed_plan`/`seeded_items`
  and `mass_distribution.unplaced_items`/`unplaced_warning`), reached from the
  oracle form through the new `field_registry.TABLE_SEEDS` — `RECORD_SEEDS`'
  analogue for a `…[]` table — which is what let the retiring `app/` page be
  pointed at the same owner instead of being left holding a live destructive
  button for the rest of the milestone. Nothing moved out of `app/`, so this is
  not the port D-57.7 rejected; it does mean #270 deletes a page that owns none
  of it, and it closes **#78** superseded. Guarded by
  `tests/test_weight_seed.py`: an entered row survives a seed unchanged in
  weight, station and tag; a second seed offers nothing; a name already present
  is matched regardless of case or spacing; a project with no mission inputs is
  told why rather than crashing; a seeded row is named as unplaced until it is
  both positioned and tagged, while a zero-weight blank is not; and
  `estimate_to_mass_items` has exactly one caller in the whole tree.
