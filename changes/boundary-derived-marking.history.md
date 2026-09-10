- **#25 step 1 — the boundary-derived seam marked (note 54 D-54.1, tier M,
  2026-09-10)** — the first half of the 0.8.3 headline: before the boundary-line
  model can derive the empennage scalars, the seam it replaces must be a
  stated, guarded set rather than a prose count. The derivable membership of
  the two tail input blocks is machine-readable — `HTAIL_BOUNDARY_DERIVED` /
  `VTAIL_BOUNDARY_DERIVED` map each field to the surface whose boundary lines
  derive it (`htail`/`vtail`/`elevator`/`rudder`, plus `wing` for `ARW` and
  `B`, extending the note 36 derive-by-default contract those two already
  honour) — with a `[D]` mark per field that travels into the generated data
  dictionary, and a partition guard pinning both maps against the dataclasses
  so a field added to either block must declare its side. Field order is
  deliberately untouched: it is a persisted shape under
  `test_schema_guards.fields_hash`, so the physical regrouping lands with
  step 2's schema bump (the boundary model proper, tier L, D-54.1) instead of
  spending a version hop on cosmetics. No load, deck byte, or delivered value
  moves; `DATA_DICTIONARY.md` regenerated.
