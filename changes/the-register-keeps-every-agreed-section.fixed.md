- **ORACLE_REPORT.md's register had fallen three shipped iterations behind, and
  carried entries later decisions had inverted (#238, 2026-09-08 review, tier S,
  2026-09-08).** The standard had no section for Section 11 OEI (note 44 §21),
  Section 12 Landing Gear (§22) or Appendix A as the V-n condition register
  (§23) — all AGREED and shipped — and its §7 register and §8 conformance list
  cited none of their guard modules; §3.11–§3.13 are now written from the
  iterations' SHALLs, with register rows and conformance entries, and §3.4's two
  stray OR-194 bullets moved into §3.13. Three stale entries were corrected to
  the current rulings ("reserved, unreferable Appendix A" → the slot OR-194
  filled; "carries the `-ULT` marker" → LIMIT with the factor stated, per
  OR-116; the pre-OR-59 single-table Appendix B → B.2 beside B.1), and §3.6's
  `Fz`-only Appendix D column set now defers to §3.8's thirteen-column applied
  spine, which amended it. The rule-4 sweep caught the same classes elsewhere:
  §3.1's selection scope still offered the retired input echo, §5 still called
  the echo "the record of what was analysed" (now the packaged `project.json`),
  and `models/report.py` still claimed a deselected section is rendered with
  its exclusion stated. Guard: `test_doc_currency.py` now requires every
  shipped `test_oracle_report*.py` module to be cited by the standard — the
  direction the existing dead-citation guard did not check, and the one that
  failed (five modules were uncited: `_oei`, `_landing`, `_vn`, `_vtail`,
  `_applied`) — with a meta-test proving it bites.
