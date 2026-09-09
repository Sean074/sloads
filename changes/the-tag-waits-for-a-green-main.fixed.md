- **The release tag now waits for the merge push's full-matrix run on `main`
  (issue #184, tier S, 2026-09-08).** The 3.10/3.11 compatibility legs and the
  coverage floor run only on the push to `main`, "fixed forward" — but
  `RELEASE_PROCESS.md` §4 step 4 tagged immediately after the merge with no
  requirement that that run was green, and 0.8.0 was tagged while it was red
  at install (#132; the classifier half was fixed then, this is the
  tag-on-red half). Step 4 now instructs
  `scripts/branch_protection_snapshot.py --check-main-run` before tagging —
  the new mode lives beside `--check` because both need the `gh` credential
  CI does not have (that script's founding constraint) — and it refuses a red
  **or still-in-progress** newest run on `main`, since tagging before the
  matrix finishes is the same hole with better luck.
  `tests/test_ci_conformance.py` gains the credential-free hop: §4 step 4
  must name `--check-main-run` and the script must offer it, so neither can
  be edited away without the other noticing. Proven both ways: removing the
  name from the doc fails the guard.
