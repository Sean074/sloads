- **`solo_close.sh` reads CI on the branch's pushed tip before its gate and refuses a close while it is red (#329, tier S, 2026-09-28).**
  The 0.8.7 milestone was red on `dev/v0.8.7` from #286 to the release cut
  (#324, a byte every local gate passed) because nothing read the branch's CI
  between closes. #327 made the developer's interpreter CI's; this closes the
  rest of the gap. In preflight, before the gate, the script lists the
  branch's `ci.yml` runs and `scripts/ci_state.py` judges the one for
  `origin/<branch>`. Only that run counts, because `ci.yml` cancels a
  superseded commit's run. A `failure`, `timed_out` or `startup_failure`
  refuses unless `--ci-red-ok "<reason>"` is given, and the reason goes into
  the commit body; that is how the close that fixes the red goes in. A run
  still going, no run yet, `cancelled`, or an unreadable answer warns and
  carries on. The check runs whenever `gh` is authenticated, with or without
  an issue number, and says "CI unread" when `gh` is not. Riders from the #327
  review in `tests/test_ci_conformance.py`:
  - every interpreter `ci.yml` names, the `typecheck` job's scalar
    `python-version` included, is one the `test` job runs;
  - no current-truth doc names another, except an allowlisted mention with its
    reason: the retired 3.10/3.11 legs and branch coverage's CPython 3.14 in
    §0.

  `CONVENTIONS.md` §7's `math.fsum` rationale no longer lists interpreters.
  The verdicts are tested from JSON alone in `tests/test_solo_scripts.py`,
  with no credentials.
