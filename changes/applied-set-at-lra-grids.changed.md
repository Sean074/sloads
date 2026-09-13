- **The applied load set is stated at the LRA grids (note 56 D-56.9, tier L,
  2026-09-12).** `applied_loads` returns one row per (case, grid): every
  aerodynamic station and every concentrated mass is summed onto the nearest
  node of the member that carries it, with the exact lever-arm couple. The two
  grid sets do not align — the beam mesh is decided from geometry alone — so
  several stations generally land on one grid. The appendix row, the
  `*_applied_loads.csv` row and the `FORCE`/`MOMENT` card are now one object at
  one point.
- **`station_applied_loads` is the set before it is lumped**, and stays public:
  the calc's own distribution at the load-integration stations, which is both
  the aggregation's input and the reference curve of the VMT comparison.
- **`project` is now required** by `applied_loads` and `applied_load_csv` — the
  beam is built from it, and a caller without one cannot be handed the delivered
  set. Ask for `station_applied_loads` by name when that is what you want.
- **The resultant is unchanged and gated; the distribution is not.** LM-1
  preserves each load's resultant about every reference exactly, per component
  and per case. What moves is where the set says a load is carried — a real
  discretization difference, which the report will state as a VMT comparison.
  One consequence is visible today: a moment component that is zero at a station
  is generally **not** zero at a grid, because moving a force across an offset
  makes a couple. The applied appendices say so.
