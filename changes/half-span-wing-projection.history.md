- **The half-span wing models are fed through one projection, `mass_distribution.half_span`, which refuses a wing mass state whose off-centreline parts are not mirrored pairs instead of running it as one side doubled (#301, tier M, 2026-09-26)** —
  The item database is full span (every row at its own butt line), but
  WINGINER (whose BASIC hangs every concentrated weight at a positive butt
  line), the balanced deck's wing set (the starboard half, mirrored) and the
  per-case tie are half-span models. The symmetry they depend on was checked
  in three places over three different sets of rows. The subset search and
  the seed search tested the discretionary subset alone, never the empty and
  minimum rows under it. Only POINT rows were counted, and by weight sum. The
  deck built its own starboard point set with its own copy of the centreline
  half-weight rule. Measured on `ga6_normal` with one 50 lb `EMPTY` wing row
  at y = ±100: a starboard POINT row reached the half-span models doubled
  (100 lb) and a port one was dropped (0 lb), each behind a warning while the
  search still called the loading valid. A one-sided PANEL row was halved
  onto both wings with no finding at all. Owner ruling (in session): build the
  projection now rather than a per-side deck (tier L, parked while no
  delivered load comes from an asymmetric mass state), and **refuse**, which
  amends design note 63 D-63.3's "an asymmetric entered state is named". The
  projection is the one place the rule lives: every off-centreline `WING`
  part, PANEL or POINT, must have a mirror image (same weight, x and z,
  opposite y, within `RECONCILE_REL_TOL` and 0.5 in). This is a pairing, not
  a weight sum, and a state that fails raises `WingAsymmetric` naming the
  parts. The search and seed search test base and subset together through
  `wing_symmetric`, and the seed search no longer trims one row of a mirrored
  pair. An asymmetric entered loading is not derivable, so the deck, WINGINER
  and the body beam refuse it by the route they already take for an
  unreachable case, with the parts in the reason. `validation`'s
  `wing_mass_asymmetric` now names a database that fails; the deck's point set
  and `WingMassState` read the projection (`port_point_weight_lb` and
  `_wing_points_symmetric` are gone). Every shipped fixture's database and
  every loading already pair exactly, so no output, digest or baseline moves.
  Guards: every shipped mass state is an exact half span; a one-sided POINT
  (either side) or PANEL row is refused by name at the projection, the mass
  state and the validator; the search refuses an asymmetric base; and a
  weight-balanced pair at unmirrored stations is refused. The SSOT row is in
  `CONVENTIONS.md` §7.
