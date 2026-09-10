- **A raked fin root no longer kinks the loads reference axis (#219, design
  note 54 D-54.3, tier M, 2026-09-09).** Where a surface's edge polylines do
  not cover the same span, the chord keeps the closed-polygon clamp
  (`wing_geometry.planform_boundary` — the 8 % GA6 area over-read stands
  fixed), but a chord-fraction *line* — the LRA, the 25/50 % load points, the
  hinge — is now evaluated on the edges' own slopes (`TailPlanform.x_at`)
  instead of pointwise on the collapsing closure chord, which swung the GA6
  fin's LRA 33.5 in aft onto the trailing-edge root point over the last 5.5 in
  of span (Figure 24's kink). The GA6 fin axis is now one straight line root
  to tip (gate: slope constant to 1e-9); surfaces whose edges cover the same
  span are byte-unchanged. **Delivered numbers move on `ga6_normal` only**
  (the one raked fixture): the fin's load application stations in the raked
  region shift forward, so the lateral cases' yaw acceleration falls 0.6–2.9 %
  (p_dot ~0.1 % through the Ixz coupling) — fin loads and Ny bit-identical,
  the lever-arm-moved diagnostic — and the GA6 tail/balance CSVs and decks
  re-baseline with it. Rule-4 ride-alongs: `interp_x` extrapolates the
  *nearest* segment below range as its docstring always promised (it used the
  last segment's slope — the wrong end of the surface), and the dead clamped
  copy `tail_geometry._interp` is removed.
