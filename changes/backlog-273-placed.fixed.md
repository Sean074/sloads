- **#273 takes its row and the priority table is dense again (backlog hygiene,
  tier S, 2026-09-11).** The #16 sweep's residue was filed against milestone
  0.8.5 with a `band:` label and no row, which `scripts/backlog_issues.py check`
  refuses — and rightly: a banded issue outside the table is work with no place
  in the single order. It enters **band B6** at the hygiene front, where its two
  halves belong together: `io.py` and `report/oracle_package.py` each declare
  their own constants for `report.json` and `build.json` (two owners for one
  filename, the class practice 3 exists to prevent), and
  `gear_loads.LEG_WEIGHT_UNSET_NOTE` is public, in `__all__` and read by nothing,
  so a leg with no entered weight shows an OPEN free body with the explanation
  written and unrendered. The table renumbers densely 1–57, closing the gap the
  2026-09-11 re-cut left at Pri 4 when #16 closed. One stale ordinal goes with
  it: #191's `after #15 (Pri 14)` — a doubled reference that survived the re-cut
  pointing at neither the issue nor the row it meant — now reads `after #186 at
  the hygiene front`, named by issue so the next re-cut cannot strand it.
