- **A red sbeam-drift run files an issue, not just a red square (#188, review R-18, tier S, 2026-09-15).**
  The weekly `sbeam drift` workflow runs the round-trip gate against sbeam `main`
  rather than the pinned commit, `continue-on-error` throughout — but its result
  was delivered only on the Actions page, which nothing requires anyone to open,
  so drift could sit unread indefinitely. It now opens one **pinned drift issue**
  on the first red run, comments on it on every red run after that, and
  comments-then-closes it on the first run that is green again, so an open issue
  means *drifting now* and the signal leaves the board the same way it arrived. A
  gate that never ran (setup failed) moves nothing: closing a live drift report on
  the strength of a test that did not execute is the one wrong answer available.
  The wiring is guarded by `tests/test_sbeam_drift_notification.py`, which holds
  the three details that delete cleanly and fail silently — the gate step's
  *step-level* `continue-on-error` (without it a red gate skips the very step that
  reports it), the `steps.<id>.outcome` key (`failure()` can never be true for a
  step that continues on error), and the single spelling of the issue title that
  is both search key and created title, whose drift would open a fresh issue every
  Monday. `PROJECT_GUIDE.md`'s sbeam-pin procedure now says where the notice
  arrives.
