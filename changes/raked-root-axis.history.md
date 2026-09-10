- **The raked-root ruling (#219, design note 54 D-54.3, tier M, 2026-09-09)** —
  `resolve_tail_planform` rebased GA6's raked fin root onto one waterline and
  the LRA swung 33.5 in aft at the root (found 2026-09-07, Figure 24). The
  decision, made explicit per D-54.3: below (and above) the span both edges
  cover, the *chord* stays on the closed-polygon clamp that fixed the 8 % area
  over-read, and the *axis* — every chord-fraction line `TailPlanform.x_at`
  evaluates: LRA, 25/50 % load points, hinge — continues on the edges' own
  slopes, because the kink was an artifact of pointwise evaluation on the
  collapsing closure chord, not of the surface. The GA6 fin axis is now
  straight root to tip (slope constant to 1e-9, gated); square-root fins are
  byte-unchanged, asserted. Delivered numbers move on `ga6_normal` only, the
  one raked fixture: yaw acceleration −0.6 to −2.9 % across the four lateral
  cases (fin loads and Ny bit-identical — a lever arm moved, not the
  aerodynamics), lateral pins re-stated and the Imperial baseline
  regenerated. Rule-4 sweep: `wing_geometry.interp_x` now
  extrapolates the nearest segment below range as documented, and the dead
  `tail_geometry._interp` clamp is removed. Spec: PROGRAM_SPEC `tail_span`
  section; the fixture-side follow-through (fin span/geometry reconciliation)
  rides D-54.6 with #260.
