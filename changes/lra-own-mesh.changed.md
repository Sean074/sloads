- **The LRA beam gets its own mesh, decided from geometry (note 56 D-56.4,
  tier L, 2026-09-11).** The beam *was* the load mesh: the wing chain was the
  WINGGEOM strips outboard of the side of body and the tail chains were the
  spanwise load stations. So the spanwise half of the LM-1 transfer was an
  **identity on every CI fixture**, and the arbitrary-grid routing a real user
  hits first was the least-covered path in the package — a degenerate special
  case hiding the general one. It also made one mesh serve two contracts: the
  strip count the replication oracle freezes at 20 was also, silently, the
  structural model.

  Each member's node set is now its own two **ends**, the joint register's
  owned locations on it, and `n` grids laid at equal spacing *between*
  consecutive owned points. `n` is per component and settable —
  `Project.lra_mesh` (**schema v66**, identity hop from v65) — defaulting to
  **wing 20 per side, fuselage 12 per cantilever, h-tail 12 per side, fin 10**.
  Blank means the default and every bundled example is blank. The WINGGEOM
  strips stay oracle-locked at 20 and simply stop being the beam.

  **A member runs to its own tip.** The wing chain used to stop at the
  outermost strip *midpoint* — 5.0 in inboard of the tip on `ga6_normal`
  (2.5 % of semispan), 12.1 in on `atr42_100`. That is the omission design note
  54 D-54.5 fixed for the fin, where it only got fixed because the T-tail tie
  made the tip a joint; with no tie to force the issue on the wing it survived.

  **The sliver class dies structurally.** Nothing is inserted any more, so a
  joint cannot land a percent of a strip from a station: the owned points come
  first and the grids are strictly interior to the segments between them.
  `JOINT_MERGE_FRACTION` retires. What replaces it is narrower and means
  something different — `_MIN_ELEMENT_FRACTION`, 1:200 of a member's target
  element length, catching two **owned** locations genuinely that close in the
  entered geometry, which is a data condition and gets a message that names the
  two points rather than asking for a bug report.

  Three gates land: no member can carry a sliver (by construction, on every
  member rather than the two tail chains the merge band covered); **the mesh is
  load-blind** — no chain node sits on a load station, and changing a grid
  count moves no delivered resultant; and a count below 2 is refused by name.
  Only `sbeam/lra_model` re-stamps — four channels. Every other deliverable is
  byte-identical and the round-trip solve gate passes unchanged.
