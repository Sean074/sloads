- **The boundary-derived seam is marked in the tail input blocks (#25 step 1,
  note 54 D-54.1, tier M, 2026-09-10).** The planform-geometry scalars the
  boundary-line model will derive — every area, span, MAC, MAC station and
  aspect ratio (9 of the h-tail block's 17 fields, 10 of the v-tail's 15, the
  wing-sourced `ARW` and `B` included) — are named in the new machine-readable
  maps `models.inputs.HTAIL_BOUNDARY_DERIVED` / `VTAIL_BOUNDARY_DERIVED`
  (`{field: deriving surface}`), which step 2's derivation consumes, and each
  carries a `[D]` mark that travels into the generated `DATA_DICTIONARY.md`;
  the aero, control-setting and mass/inertia fields are the stated remainder,
  and `vtail_root_waterline_z` is called out as placement (the L-1 owner's
  field), not planform. Field order is untouched — it is a persisted shape
  (`test_schema_guards.fields_hash`), so the physical regrouping rides step
  2's own schema bump rather than spending a version hop on cosmetics. No
  behavior change: every scalar stays entered and oracle-authoritative until
  step 2. Guard: `tests/test_empennage.py::
  test_the_boundary_derived_marking_partitions_the_tail_blocks` — every field
  of both blocks must declare its side of the seam.
