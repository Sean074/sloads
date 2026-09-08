- **Section 11, One Engine Inoperative (design note 44 §21, tier L, 2026-09-07).**
  The oracle report's eleventh section, in three subsections: 11.1 Input Data,
  11.2 Critical Cases and 11.3 Yaw Transient. The third exists because this is
  the suite's only time-marching analysis — every other condition is a state of
  the airplane, this one is an event — and a peak load stated without the march
  that produced it is a number a reader cannot check. 11.3 carries one pair of
  figures per case, the yaw response and the fin load that recovered it, each
  marking 23.367(b)'s two-second limit on corrective action and the instant of
  peak total load; a symmetric installation's second engine is not re-plotted,
  and the section says so.
- **The 23.367 engine-failure cases are fin design conditions (note 44 OR-172,
  tier L, 2026-09-07).** Every recovered case now joins the vertical tail's
  critical set and travels with it: Section 6, the chordwise and spanwise
  distributions, the applied-load appendix and the exported v-tail deck.
  `one_engine_out.fin_conditions` publishes them and `select.default_critical`
  admits them at one insertion point.
- **A `NOT_APPLICABLE` section state (note 44 OR-178).** The airplane has no such
  condition — distinct from the tool not producing it and from the inputs being
  missing. Its reason is read from `applicability.step_not_applicable`, the
  predicate the module refuses on and the coverage table cites.
