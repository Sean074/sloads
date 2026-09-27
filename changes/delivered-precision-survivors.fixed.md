- **Every delivered and on-screen number takes its digits from its unit, and note 65's gates look where the note says (#302, tier S, 2026-09-26).**
  The safety factor printed `1.5` in `safety_factors.csv` and the overrides
  statement, through a bare `:g` the gate could not see, and `1.500` in the
  report beside them; both now read `format_value`. The GUI station tables
  held digit counts at two levels: the row builders (`wing_load_rows`,
  `body_load_rows`, `fitting_load_rows`) returned strings at their own
  decimals, and `app_shell/limit_csv.py` re-rounded them from its own table.
  The builders now return the calc's floats, and each cell is read back from
  `format_value` under its header's label, so it stays a number and a column
  still sorts; on screen a station shows 0.1 in rather than 0.001 in and a
  force the whole pound. The fleet view, the sidebar's airspeed and %MAC tools,
  the landing page's energy N and the results page's estimate delta and
  inertia sentences route through the owner too. `lbf`, `psi` and `sqft` (the
  scalar converter's spellings) and `lb/hp` (the fleet view's power loading)
  gained rows, since a unit with no row falls to the fallback. What remains is
  exempt on its statement with a reason: prose tolerances and shares,
  percentile ranks, dictionary keys, the entered-value echo, the owner
  itself. Gate 4 scans `sloads/report/`, `app_shell/` and `oracle_app/`, and
  catches any float presentation type (a bare `:g` included) and any `round`
  to a digit count. Gate 2 runs in SI as well: the load-case CSVs in the fast
  lane; the SI document and its `data/` in the slow lane (all five fixtures
  clean, the gear report excepted as the solver channel's companion). Gate 3
  holds the scalar converter's keys to a row. No Imperial baseline digest
  moves.
