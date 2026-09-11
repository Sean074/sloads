- **The LRA beam gets its own mesh (note 56 D-56.4, tier L, 2026-09-11)** —
  The fifth slice of note 56, and the one that separates the structural
  model from the replication contract's strip count.

  **Objective.** Cut the LRA beam model loose from the load stations, so the
  structural mesh is decided by geometry and a node count rather than by the
  replication contract's strip count — and so the general load-routing case is
  the one CI exercises.

  **Why it mattered.** The beam *was* the load mesh. The wing chain was the
  WINGGEOM strips outboard of the side of body; the two tail chains were the
  spanwise load stations. Beam nodes therefore *were* load stations, the spanwise
  half of the LM-1 transfer `(F, M)@p → (F, M + (p − n) × F)@n` was an identity
  on every fixture in CI, and the arbitrary-grid path — what a user with their own
  beam model hits first, and the path `lra_import` exists to serve — was the least
  covered code in the package. It also welded two unrelated contracts together:
  the 20 strips the printed oracle freezes were also, unstated, the structural
  idealization. And it is what made a joint an *insertion* into someone else's
  mesh, which is the whole of note 55: `cessna_210`'s h-tail attachment landed
  0.0769 in from a station, 1.07 % of a strip, a 1638:1 element-length ratio and
  the singular solve #172 reported.

  **Deliverables.**

  * **The mesh rule.** A member's node set is its own two ends, the joint
  register's owned locations on it, and `n` grids laid at equal spacing
  **between** consecutive owned points. Segment-based rather than
  uniform-then-merge, and that is the load-bearing choice: grids exist only
  strictly inside segments, so a grid can never land beside a joint. It is what
  makes "joints are mesh points by construction" true rather than asserted.
  `n` is a target, not the node count — a member whose owned points are unevenly
  spread rounds segment by segment — and trading the exact count for the sliver
  is the right way round: one is a number in a form, the other is a singular
  stiffness matrix.
  * **The counts are persisted input.** `Project.lra_mesh` (`LraMeshInput`,
  **schema v65 → v66**, identity hop, five examples re-stamped): four
  `Optional[int]` counts, `None` = the default, defaults **wing 20 per side,
  fuselage 12 per cantilever, h-tail 12 per side, fin 10** (owner ruling
  2026-09-11). Persisted rather than a flag because the count decides which
  grids a delivered deck carries, so a project exported at 20 a side must
  reopen at 20. Classified dimensionless with a reason; four field-registry
  rows on the geometry page; `DATA_DICTIONARY` regenerated.
  * **A member runs to its own end.** The wing chain stopped at the outermost
  strip *midpoint* — 5.0 in inboard of the tip on `ga6_normal` (2.5 % of
  semispan), 12.1 in on `atr42_100`. That is exactly the omission D-54.5 fixed
  for the fin, and the reason it survived on the wing is instructive: the fin's
  got fixed because a T-tail tie made the tip a *joint*, so something forced the
  issue. Nothing forced it here. D-56.4's "the member's ends" is the general
  form of that fix.
  * **One owner for where the wing beam is.** `joints.wing_lra_point` was already
  the register's private resolver; it is public now, over
  `wing_geometry.chord_fraction_x`, so the exporter meshes from the same
  construction the register places joints on instead of growing a fifth
  spelling of the chord-fraction line. Verified against the delivered load
  stations on all four fixtures: agreement to 1.4e-14 in.
  * **`JOINT_MERGE_FRACTION` retires**, and what replaces it is a different
  question. Nothing is inserted, so an insertion-induced sliver cannot arise.
  What *can* still arise is two **owned** locations genuinely close together on
  one member — two joints, a joint and a trunnion — where both must be nodes
  because dropping either drops a load path. `_MIN_ELEMENT_FRACTION` catches
  that, its message names the two points and asks for the geometry rather than
  for a bug report, and the threshold is measured rather than chosen: the one
  observed singular solve was 1:1638, the tightest legitimate element across
  four fixtures at three mesh settings is 1:38, and the floor sits at 1:200.
  Note 55's 5 % is **not** the precedent — that number decided whether to merge
  a station, a question about strip scale; this one decides whether to refuse a
  solve, a question about stiffness contrast.

  **Test.** Note 56 gates 5, 10 and 11. Gate 5 (no member can carry a sliver) is
  asserted on every member rather than the two tail chains the merge band covered.
  Gate 10 is the note's own argument in one test, in two halves because either
  alone is weak: **position** — no wing chain node sits on a load station, the
  side of body excepted, since a station coinciding with an owned joint is a fact
  about the airplane; and **resultant** — meshing the same project fine
  (31/17/15/19) and coarse (7/5/4/5) moves no case's six-component resultant,
  which is what says the mesh is free to move at all. Gate 11 is the schema hop.
  The round-trip solve gate passes on every CLI-exportable fixture with its two
  known SI xfails (sbeam's dense-path condition heuristic) unchanged — evidence
  that the renumber and re-mesh moved grids and nothing else, since the transfer
  routes by position and never by id.

  **Key decisions.**

  1. **Segment-based spacing over uniform-then-merge.** Uniform placement plus a
   merge band would have been the smaller change and would still have improved
   on note 55 — what gets absorbed would be an anonymous grid rather than a load
   station carrying a gid and a load. It was rejected because it keeps a
   tolerance constant and therefore keeps the class: the note's sentence that
   the sliver dies structurally would have been false. Segment-based is the only
   reading that makes it true.
  2. **Gear and engine nodes are model nodes, not chain stations.** D-56.4 lists
   "its gear / engine / hinge / actuator nodes" in the member's node set. The
   hinge and actuator fittings are chain-owned points here, because they already
   were; the gear trunnions and the engine mount/hub stay their own nodes tied
   by `RBE2` to the nearest chain node, which is the topology that already
   shipped. Making a tie parent exact rather than nearest is a real improvement
   and a separable one — it changes a load path, and this step changes enough.
  3. **The fuselage is meshed too, though it was never the degenerate case.** Its
   stations were the *outline's* section stations, not load stations, so the
   note's §1.4 argument never applied to it. It moves anyway, because the
   alternative is that how finely the beam is analysed remains a consequence of
   how finely someone drew the body — a different quantity wearing the same
   number.
