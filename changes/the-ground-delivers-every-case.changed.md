- **No critical-case down-select survives into the ground loads (design note 44 OR-184, tier L, 2026-09-07).**
  Section 12 and Appendix F carry every one of the 33 LANDLOAD conditions, and
  say so. A ground case sizes a gear member through a load path the loads
  analysis does not model — a drag brace, a side brace, a trunnion — so the case
  that governs one member is not the case that governs another, and ranking 33
  conditions on a single scalar answers a question nobody asked while removing
  the case a reader needs. The per-family largest reactions are still printed and
  are labelled a reading aid.
- **The entered landing load factor is stated beside the computed one (OR-187).**
  `ga6_normal` enters `N = 3.167` against LGFACTOR's energy estimate of 3.0970;
  `concept_regional_jet` enters 2.67 — exactly the 23.473(g) floor — against
  2.3755. The reactions run at the entered value, which is the user's decision to
  make; §12.2 prints both pairs and names which governed, because a section that
  presented an entered number as the output of the drop-test calculation would
  describe an analysis nobody ran.
- **`modules/landing.py` under the OR-15 admission of 2026-09-07 (OR-190).**
  `_geometry` becomes `landing_geometry` and `_critical` becomes
  `critical_reaction` with a gear argument. No arithmetic in either is touched.
