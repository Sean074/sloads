- **Two cross-references pointed at plan keys that cannot exist (#230, 2026-09-08 review R6, tier S, 2026-09-08).**
  `NOT_CARRIED` was written for genuinely deselected or unbuilt targets, but
  §2.4 passed `"flight_envelope_cases"` — a key the plan has never had — and
  §4.3 with Table 25's footnote passed `"tail_loads"`, retired as a section
  key by the OR-129 htail/vtail partition, so every issue of every report
  told the reader its design-case tabulation and its pull-up derivation were
  *"in a section this issue does not carry"* while carrying both. §2.4 now
  points at Appendix A (the candidate register) and the component case
  registers; §4.3 points at the horizontal-tail section through the existing
  `_tail_section_key` composer. Two guards make it structural: a static
  sweep resolves every key passed to `section_ref`/`subsection_ref` —
  literals, module constants, the declared composer — and fails on a key
  the full plan does not carry *or* an argument it cannot resolve, and a
  runtime gate asserts a full build of both shipped examples never prints
  `NOT_CARRIED` anywhere. G-OR-68's own test was complicit — it looked up
  `"tail_loads"` too, degraded in lockstep and asserted the broken sentence —
  and now demands a resolved section number on both references.
