- **The oracle report states the horizontal tail's loads (#151 iteration 5,
  design note 44 §17, tier L, 2026-09-06).** Section 5, in four subsections and
  Appendix D, built from the `tail_loads` step (`TAILDIST`, Reference 1 Ch 10):
  5.1 the design conditions and the search that produced them, 5.2 the critical
  loads with the aerodynamic state each was computed at, 5.3 the chordwise
  pressure distribution and its figure, 5.4 the spanwise loads on the beam.
  Appendix D carries every condition at every station, as a view of
  `sbeam_bridge.tail_span_csv`'s own rows rather than a second assembler. Every
  load is LIMIT, states the factor 14 CFR 23.303 prescribes for its condition,
  and is multiplied by nothing.

- **The tail is two sections, and G-OR-2 becomes a partition (design note 44 §17
  OR-128/OR-129, tier L, 2026-09-06).** An analyst reads by surface, so the
  horizontal tail is section 5 and the vertical tail section 6, and everything
  below them renumbers — free, because `section_number` derives from position
  and no cross-reference is written as a literal. One step across two sections
  breaks the old one-step-one-section rule, so the rule becomes *one step, one
  declared partition*, keyed on `component`: **every published condition lands
  in exactly one section**, asserted in both directions, which is a stronger
  gate than the counting one it replaces.

- **Every critical tail condition states the load its control surface carries
  (design note 44 §17 OR-132, tier L, 2026-09-06).** `elevator_load` was
  published on 2 of 9 horizontal-tail conditions and `load_on_rudder` on 2 of 4
  vertical-tail ones, so section 5.2's table would have had a blank
  control-surface column on seven rows for no reason the analysis could give:
  both are pure functions of the 25 %/50 % split every one of those conditions
  already carries. Published in `_htail_condition`, the one constructor they all
  pass through, rather than at nine call sites. Second **OR-15 admission** over
  frozen `sloads/modules/select.py`; additive, and the one insertion that would
  have moved an existing CSV column was rewritten to append instead.
