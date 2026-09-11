- **The joint register: a joint is an owned location, a stated arm, a DOF set
  and a basis (#262, note 54 D-54.5/D-54.7, tier L, 2026-09-10).** Every
  inter-component tie in the LRA beam model now has its nodes placed by one
  owner, `sloads/joints.py` — the fin root→fuselage tie, the T-tail
  fin-tip↔h-tail-centreline pair, the conventional attachment pair, the wing
  side of body and the two spar posts. `joints(project)` resolves nothing
  itself: it reads the owners that already resolve each position
  (`tail_geometry`'s fin root and `h_tail_waterline`, `tail_span.htail_attachment`,
  `derived_geometry`'s `sob_station`/`carry_through`/`fuselage_lra`) and copies
  their location, ASSUMED/entered grade, basis and in-band note **verbatim**;
  `export/lra_model` places its nodes and raises its refusals by reading the
  register, so the two ends of a rigid tie can no longer be two spellings of one
  formula. **This corrects real geometry.** The R-6 tie hung the horizontal tail
  off the outermost fin *strip midpoint* rather than the fin tip: measured
  against the planform owners it spanned −23.228/−23.753/−20.876 in of x where
  the surfaces state −25.600/−26.100/−26.680 (5.80 in, −22 %, on
  `concept_regional_jet`), plus 6.25/6.5/6.9 in of `z` the airplane does not
  have — the arms note 51's D-51.2/D-51.3 transfer moments are computed across.
  The fin chain now runs **root → strips → tip** (`lra-fin-tip`), and the h-tail
  centreline and conventional attachment nodes are placed at their own LRA
  stations instead of being interpolated off the strip polyline (which put
  `ga6_normal`'s attachment pair 0.356 in off the body station it reacts
  against). D-54.7's drift guard (`tests/test_joints.py`) walks every joint of
  every fixture out of the **emitted deck text** and asserts the node is where
  the register put it, that a tie exists, that it constrains the stated DOF set,
  and that it spans the stated arm. No delivered load moves: of 330 baseline
  channels only `sbeam/lra_model` changed, on five of six fixtures, and the
  per-subcase deck resultant is unchanged (LM-1 preserves it wherever the nodes
  sit). Alongside it, `wing_geometry.chord_fraction_x` becomes the single owner
  of the chord-fraction line, which `TailPlanform.x_at` and
  `net_loads.to_loads_ref_axis` had each spelled out separately.
