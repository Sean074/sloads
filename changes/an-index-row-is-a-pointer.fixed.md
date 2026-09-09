- **A live design note's INDEX row is a pointer again, not a second copy of
  the note (issue #187, tier S, 2026-09-08).** Note 44's `docs/00_INDEX.md`
  row had grown to ~600 words restating OR-13…OR-37 with its own copy of the
  status, and other rows mirrored the stale AGREED that #183 fixed in the
  notes — a second hand-maintained statement per note, the rule-3 drift
  class, already drifting. All ten `30_future/` rows are rewritten to one
  sentence plus the pointer with **no status**: the note's own Status line is
  the single owner. Guarded (`test_doc_currency.py`): a `30_future/` row over
  320 characters or carrying AGREED/SHIPPED/BUILT/PROPOSED fails CI.
  `40_history/` rows are exempt by decision — an archived note's status can
  never change again, so those rows are frozen record and the long
  descriptions there are the index's value as a finding aid for closed work.
  Proven both ways: adding "AGREED 2026-08-29" back to note 44's row fails
  the guard.
