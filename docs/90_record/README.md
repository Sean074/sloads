# `90_record/` — the record

**This directory is not where current truth lives.** Every line in it states
what was true on a date. It is here to be kept, not to be searched.

Consult it when the question is explicitly **when did this change** or **why did
it change**. For **how does this work**, go to `10_standard/` (the code
standard), `20_theory/` (equations and oracles) or `25_notes/` (the agreed
rationale, and what the tests cite).

## Why it is filed apart

Design note 61 measured the search cost. Terms a maintainer actually looks up
returned two to three times more hits from the record than from the authority —
`LRA` 34 record files against 14 authoritative, `envelope` 42 against 19 — and
every record hit is a dated snapshot. The ratio worsened by construction: the
record grows with time, the live corpus grows with the code. CV-4 moved the
record out of the default search path; CV-3 first rescued the 52 design notes
that were filed in here by date and are cited by the physics tests as standing
authority.

## What is in here

| Kind | Files |
|------|-------|
| The changelog | `CHANGELOG.md` (live: current cycle + previous release block) and `CHANGELOG_to_<version>.md` archives (note 61 CV-5) |
| Completed development | `00_completed_development.md` (live) and the `NN_completed_development_to_<version>.md` era archives (note 26 DV-1) |
| Verification baselines | `NN_verification_baseline_<version>.md` — the per-release regression record (`RELEASE_PROCESS.md` §4.5) |
| Backlog-state narratives | point-in-time snapshots of the backlog |
| Executed runbooks | e.g. the M3-1 rename procedure — how a completed one-off was carried out |

## Rules

- **Archives are frozen: do not edit them.** A file named `…_to_<version>.md`
  is a record, not a document (note 26 DV-1). Its links point at the tree as it
  stood when it was written, which is why `tests/test_doc_links.py` exempts this
  directory.
- **The two live files are never hand-edited** at the top: closure writes a
  `changes/` fragment and `scripts/build_changelog.py` assembles both at the
  release cut (`RELEASE_PROCESS.md` §4).
- **Both live files roll at 1,500 lines** — a threshold, not a defect;
  `tests/test_changelog_fragments.py` warns and the release cut does the roll.
