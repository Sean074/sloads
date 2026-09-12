- **The applied load set gets its right address and `sbeam_bridge.py` ceases to
  exist (note 56 D-56.1, tier M, 2026-09-11).** `AppliedLoad`,
  `applied_loads` and its five component row builders, `applied_body_moments`,
  `applied_load_csv`, the side-of-body internal loads and the station numbering
  they state all live there now. It was never a bridge to sbeam: it is the record
  of what is applied and where, which the oracle report's applied appendices are
  built from directly.
- **Import from `sloads.report.applied`.** No shim is left at the old address and
  the export package no longer re-exports any of it — a guard refuses both.
- **Nothing delivered changed.** Module views, the case index, both reports,
  every CSV and every deck are byte-identical across the move.
