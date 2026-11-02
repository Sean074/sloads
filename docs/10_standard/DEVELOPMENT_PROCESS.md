# sloads — Development Process (multi-developer)

The standard for **how work moves** from an idea to a released, oracle-locked
change when more than one person (and more than one person's AI) is working on
the repository. Design note 28 (MD-1…MD-12, agreed 2026-08-16) is the rationale;
this page is the rule. `CONTRIBUTING.md` at the repo root is the short human
on-ramp and links here; `CLAUDE.md` is the AI's operating contract and links here.
Nothing on this page changes *what* the standard requires (closure tiers,
benchmark-first, make-it-structural, review depth, release gate) — it re-homes
*where* each requirement is checked: **the session becomes the pull request.**
§0 states which of these mechanisms are switched off while the repository has a
single collaborator; §1–§9 apply in full from the day a second one is added.

---

## 0. Working alone — the solo profile (added 2026-08-17)

Note 28 buys its value from concurrency: a reviewer who is not the author,
counters that two branches can race on, an issue tracker two people can both
read. With **one collaborator** (the GitHub collaborator list is the test) those
mechanisms cost a CI round-trip and a bookkeeping channel per item and protect
nothing — the first week of the process on 0.6.0 (PR #25 / issue #1: template
placeholder left unfilled, the issue never closed, the backlog row-removal
conflicting with the next branch) is the evidence. While solo:

| Mechanism | Solo profile |
|---|---|
| Branch / PR per item (§1, §2) | **Retired — one milestone branch replaces both** (2026-08-22). `scripts/solo_start.sh dev/vX.Y.Z` opens **one** branch per release off `main`; every item of that milestone is worked and committed **directly on it** — no per-item branch, no per-item PR, **one commit per closed item** with the subject in the project style, so `git log` stays the step-per-commit record. The item's issue closes and its priority-table row leaves **in its own commit**, so the backlog is a live view of what is still open mid-milestone. Each push runs the fast gate on `dev/**` (see the CI row): **advisory** — the branch is unprotected, nothing waits on it, and it runs while the next item is already being worked. When the milestone is empty the release is cut **on this branch** (`RELEASE_PROCESS.md` §4 — there is no separate `release/x.y.z`), and it reaches `main` as **one pull request, rebase-merged** (`gh pr merge <N> --rebase`) — every per-item commit replayed onto `main` individually, and never squashed — whose push to `main` runs the full matrix. Rebase rather than a merge commit because `main` enforces linear history (corrected 2026-08-25 at the 0.7.2 cut, where the merge was refused: "This branch must not contain merge commits"); it satisfies the protection rule and keeps the step-per-commit record, at the cost of rewriting the branch's SHAs — so the milestone branch is deleted after the merge, not reused. **Why this replaced per-item PRs:** the defect class was two closing paths both claiming to close the item — #38 mixed a hand-made PR with `solo_close.sh`, and the PR body's `Closes #38` closed the issue before the script's own `gh issue close` ran; #53/#54 committed to a branch whose PR had already squash-merged (its commits then conflict with their own squashed copy on `main`, resolved by cherry-picking onto a fresh branch, never by hand-resolving the duplicate history); and the `--ff-only` push needed an admin bypass because `main` requires a PR. One path, one gate, and `main`'s protection stays fully on. |
| Non-author review, CODEOWNERS (§2, §7) | **Not applicable** — unsatisfiable with one person. Review depth (`CODE_REVIEW_PROCESS.md` §0) is still owed; it is the AI's review in the session, and its findings are filed with bodies (rule 5). |
| Issues as system of record (§4) | **Unchanged, and the table is a generated view (#359, 2026-11-01).** Every item is an issue; the priority table is regenerated from the issues by `backlog_issues.py render`, which `solo_close.sh` runs in preflight with `--closing N`, so the row leaves **in the closing commit** — on the milestone branch, at the moment the item is done — and nobody edits the table by hand. (No `Closes #N` in the milestone PR — it would re-close what is already closed, the #38 failure in a new place.) The issue argument to `solo_close.sh` is **optional**: omit it and the script makes no issue call — no read, no `gh issue close`, no `render`, no `check`. The one `gh` call left is the read-only CI check, made whenever `gh` is authenticated (#329). |
| Rebase before regenerating (§6) | **Unchanged.** The priority table is a generated view, not a counter: a close drops its own row and touches nothing else; rows never cite another row's ordinal (dependencies name the band or the `#N`). |
| Closure tiers, fragments, design-note-before-physics, rules 1–6, release gate (§3, §5, §8, §10) | **Unchanged.** These are the quality mechanisms; none of them needs a second person. A tier-L design note is agreed in chat and merged with the work (`CLAUDE.md` rule 1); §9's "agreed in chat is retired" resumes with the second collaborator. |
| Branch protection on `main` | **Stays fully on** (2026-08-22) — the milestone model needs no bypass, because the only thing that ever lands on `main` is the milestone PR. Owner-applied settings: PR required; required checks are the **fast gate** — `test (3.12)`, `typecheck`, `sbeam-roundtrip (3.12)`; **"Require linear history" ON**, so the milestone PR is **rebase-merged** and every per-item commit survives on `main` as its own linear commit. This row said the opposite until 2026-08-25 — "linear history off, merge commits allowed" — and the setting, not the doc, was the truth: the 0.7.2 PR was blocked with "This branch must not contain merge commits". Rebase satisfies both requirements at once, so no setting was changed to fit the doc. `dev/**` is deliberately **unprotected**: its CI is advisory. |
| CI shape (`ci.yml`) | **One interpreter everywhere; coverage only on the merge to `main`.** Every PR, every push to a `dev/**` milestone branch *and* the push to `main` run 3.12 (**uninstrumented**, mypy, solver round-trip on 3.12) — the interpreter the developer's `.venv` must also be, which `tests/test_ci_conformance.py` enforces (#327, 2026-09-28: the 3.10/3.11 compatibility legs that ran on `main` alone retired after they and a 3.11 `.venv` let #324 and #325 through every gate before the merge) — measured 7.3 min, of which pytest is 7.2 (2026-08-22: 4 xdist workers on the public-repo runner, ~1,700 CPU-seconds of tests spread broadly — the slowest-15 are only ~13 % of it, so no slow-test split moves this number; a suite-wide fixture reduction would, and is band B). The **coverage-instrumented 3.12 leg** runs on the push to `main` alone — i.e. on the milestone merge — and is fixed forward; it moved there 2026-08-22, when the instrumented PR leg passed 27 minutes. The instrumented leg measures line coverage under `COVERAGE_CORE=sysmon` (branch measurement under `sys.monitoring` needs Python 3.14; branch figures on demand locally with `--cov-branch`). The coverage conditional therefore keys on **push-to-`main`**, never on "is this a PR" — keyed the old way a `dev/**` push would take the other arm and run the 27-minute leg (guard: `tests/test_solo_scripts.py`). A re-push cancels the run in flight (`concurrency`), so a burst of item commits leaves only the last one verified — working one item at a time, that is the intended trade. A **docs-only closure** (the predicate of the local-gate row below) pushes with `[skip ci]` in its commit body, so no advisory run starts for a commit that could not change it; `--full-gate` runs it, the next code push covers the skipped tip, and `scripts/ci_state.py` reads "no run for the tip" as a warning, not a red (#416, 2026-11-01). |
| Local gate before merge/push | `ruff` · `mypy` (the pre-commit hook, ~10 s) and the suite **once**, on the whole tree, immediately before the push (the pre-push hook) — not after every edit. **This is now the gate that actually costs you time**, since CI on `dev/**` is advisory and runs behind you. **It scales to the change set:** a docs-only change set — every path either `*.md` or under `docs/` or `changes/` — runs `ruff` · `mypy` and the six guard files — `test_doc_currency`, `test_doc_links`, `test_changelog_fragments`, `test_schema_guards`, `test_backlog_issues`, `test_workflow` — in ~3 s instead of the suite's ~150 s; `solo_close.sh` decides from the paths and `--full-gate` overrides. Any other change set takes the suite **less its `slow` lane** (#308, 2026-09-26: the PDF compiles, the GUI journeys and the whole-analysis planform sweeps, marked `pytest.mark.slow`), which `--full-gate`, CI and the milestone merge still run; the shared fixture bundles (`imperial_baseline.artifacts` and the report/deck builders the slowest files repeated) are built once per test process. Since 2026-08-22 that predicate sizes the gate and **nothing else** — where an item is closed no longer depends on what it touches, because every item closes the same way on the milestone branch. While iterating run **the module's own test file**, and `test_deliverable_units.py` once before closing rather than per edit — it is where a physics change shows first (the Imperial digest) *and* now the slowest file in the suite, so per-edit it costs more than the whole suite did when this row was written (timings and the ~43 s parallel floor: `.pre-commit-config.yaml`, re-measured 2026-08-19). |

**The loop is scripted (issue #27, 2026-08-17; cycle-time revision 2026-08-19;
milestone-branch revision 2026-08-22):**

*Once per release* — `scripts/solo_start.sh dev/vX.Y.Z` opens the milestone
branch off `main` and pushes it (preflight: on `main`, clean tree, the branch
does not exist). It never calls `gh`: the issue set is opened when the
milestone is *scoped*, not when the branch is cut.

*Once per item, on that branch* — `scripts/solo_close.sh --slug <slug>
[<issue>] "<Subject>"` runs the closing half in order: gate (`ruff` · `mypy` ·
`pytest`, scaled to the change set), one commit with the project-style
parenthetical, push, `gh issue close` with the branch SHA, then
`backlog_issues.py check` / issue state / that branch's last CI run. It refuses
to start until the one fragment exists (≤ 60 words, lead naming the tier), or
when the commit subject exceeds 100 characters; when an issue is given it drops
that item's row itself (`backlog_issues.py render --closing N`) and warns when
a new design note in the change set exceeds ~150 lines. **It reads CI before
its gate** (#329): the `ci.yml` run of the branch's pushed tip, judged by
`scripts/ci_state.py` — red (`failure`, `timed_out`, `startup_failure`) refuses
unless `--ci-red-ok "<reason>"`, whose reason goes into the commit body (the
close that fixes the red); still running, no run yet or `cancelled` warns and
carries on. A red that every local gate passes (#324's Linux-vs-macOS byte) is
found at the next close, not at the milestone's pull request. It stops at the first
failure with the recovery printed (`--dry-run` shows the sequence; `--help` the
options). `--slug` is **required**: the branch names the milestone, not the
item, so there is no branch name to take it from. Two things it no longer does,
deliberately — it never checks out, fast-forwards or pushes `main`, and it
never deletes a branch. **What stays conditional:** the issue number is
optional and drops every `gh` call with it, and the gate shrinks to the guard
files for a docs-only change set.

*Once per milestone, at the end* — cut the release on the branch
(`RELEASE_PROCESS.md` §4), open one PR into `main`, rebase-merge it
(`gh pr merge <N> --rebase` — `main` enforces linear history), tag from `main`.

The step between start and close — the work and the closure artefacts — is the
developer's; the scripts encode nothing that this section does not already say
(rule 3: the sequence is structural, not a chat transcript), and
`tests/test_solo_scripts.py` holds the scripts, `ci.yml`'s triggers and this
prose in step.

**Switch-over is mechanical:** the day a second collaborator is added, any open
milestone branch is finished and merged first (it is the one mechanism here
that cannot simply be abandoned mid-flight), branch protection goes back to §2
— linear history on, squash-merge only — and this section stops applying.
Nothing done under the solo profile has to be redone.

---

## 1. The flow

```
issue (#N, labelled tier/tag/band)            <- the system of record for open work
   |
   |  tier L / physics: note/NN-slug PR  ->  design note merged at AGREED  (MD-6)
   v
branch  <type>/<slug>  off main               <- one item per branch, short-lived   (MD-1)
   |
   |  work; closure artefacts land IN the PR   (MD-3)
   |  rebase on main before you regenerate anything (schema, digest, bands)  (MD-7)
   v
PR -> CI (test x3, typecheck, sbeam-roundtrip) -> review at tier depth (>=1, != author; owner per CODEOWNERS)
   |
   |  squash-merge; PR title = commit subject; branch deleted   (MD-2)
   v
main (always releasable)  ->  release manager cuts release/x.y.z per RELEASE_PROCESS.md §4  (MD-11)
```

## 2. Branches and merging (MD-1, MD-2)

- **Trunk-based.** `main` is always releasable. Branch from `main`; rebase on
  `main` before merge; delete on merge. No long-lived integration branches. The
  only other branch kind is the hotfix branch of `RELEASE_PROCESS.md` §6 and the
  release manager's `release/x.y.z` (§8 below). **§0's `dev/vX.Y.Z` milestone
  branch is the one exception, and it belongs to the solo profile only** — it is
  safe there precisely because nothing races it; it retires, with the rest of
  §0, the day a second collaborator is added.
- **Names:** `<type>/<slug>` — `step/14-pbar-passthrough`, `fix/gear-csv-ult-marker`,
  `note/28-multi-dev`, `docs/…`, `chore/…`. The slug is the fragment slug.
- **`main` is protected** (settings, owner-applied): PRs only, the owner
  included; required checks are the **fast gate** — `test (3.12)`, `typecheck`,
  `sbeam-roundtrip (3.12)`; conversations resolved; **linear history —
  squash-merge only**. **The review requirements split by profile** — see the
  next-but-one bullet.
  - **Review requirements are the multi-dev profile's, and are OFF under §0
    (2026-08-26).** The multi-dev target is **one approving review from someone
    other than the author**, review from Code Owners (`.github/CODEOWNERS`) and
    **stale approvals dismissed on push**. Live `main` requires none of the
    three, and that is deliberate rather than neglect: GitHub does not let an
    author approve their own pull request, and `CODEOWNERS` names one person on
    every line, so under the solo profile either setting would block **every**
    merge — the milestone PR included — until a second collaborator exists.
    Turning all three on is part of the switch-over, beside restoring
    squash-merge. The snapshot tracks `required_approving_review_count`,
    `required_code_owner_reviews`, `dismiss_stale_reviews` and
    `required_conversation_resolution` individually, and
    `tests/test_ci_conformance.py` asserts this prose against them — CR-D-4's own
    class, one field deeper. A snapshot that tracked only `required_pull_request`
    could not see any of these three, because that field is true the moment a
    review block exists at all.
  - **Why these three, and why they are the same three under §0:** they are
    every check `ci.yml` reports on a pull request, and a required check that
    never reports blocks the PR forever (2026-08-20 review, CR-D-4, when §2
    listed six, three of them legs that ran only on `main`). Since #327 the
    push to `main` runs the same three and adds only coverage, a *fixed-forward*
    measurement on the merge push, not a gate.
  - **What §0 does change** is the merge *method* — squash here, **rebase** under
    the solo profile, so the milestone PR keeps one commit per item and still
    satisfies linear history. The protection settings and the required-check set
    are the same in both profiles. Restoring squash-merge is part of the
    switch-over. The live settings are snapshotted in
    [`../../.github/branch-protection.json`](../../.github/branch-protection.json)
    and this prose is asserted against that snapshot by
    `tests/test_ci_conformance.py`, so the two cannot drift apart in silence
    again.
- **Squash-merge, PR title = commit subject** in the project's existing style
  (`Step 14: PBAR/MAT1 pass-through (tier M, 2026-08-20)`), so `git log` stays
  the step-per-commit record it is today.
- **`self-merge-ok`:** a PR labelled so — tier S, docs/hygiene only, **no change
  under `sloads/`** — may be merged by its author once CI is green. Anything
  else waits for its reviewer.

## 3. Closure travels in the PR (MD-3, MD-4)

The Step Completion Requirement (`CLAUDE.md`) reads "same session"; with more
than one developer it means **same PR**. A PR that closes an item carries, at
its tier:

| Tier | In the PR |
|---|---|
| **S** | one `changes/<slug>.<type>.md` fragment — **one bullet, ≤ 60 words**; `Closes #N` in the body |
| **M** | S + the affected `PROGRAM_SPEC.md`/standard-doc sections |
| **L** | M + `theory_sources.md` citation + the design note (§5 template, ≤ ~150 lines) merged at AGREED first, flipped to *shipped* |

- **There is no history entry at any tier** (#359, 2026-11-01). `CHANGELOG.md`
  (built from the fragments at the cut), the design notes and `git log` are the
  record; `docs/90_record/00_completed_development.md` is frozen. The one
  question every closure asks (note 61 CV-1): *does a reader of the code today
  need this?* If yes it goes to `10_standard`/`20_theory` in the present tense;
  if not, the fragment's one sentence is all that is written.
- **The commit subject is ≤ 100 characters**, parenthetical included
  (`solo_close.sh` refuses a longer one). The subject is the change in a
  phrase; the fragment and the issue say the rest.
- **Backlog removal is `Closes #N`.** Merging the PR closes the issue; the
  row leaves the priority table at the next `backlog_issues.py render` (§4) —
  the PR itself does not edit the table. (Under §0 the close script runs
  `render` itself, so the row leaves in the closing commit.)
- "Closure in a follow-up" is a `[MAJOR]` review finding, exactly as before.
- The PR template is the tier table as a checklist; the reviewer's approval
  gate is `CODE_REVIEW_PROCESS.md` §Approval gate.

## 4. Issues are the record; `00_backlog.md` is the plan (MD-5)

- **Every open item is a GitHub issue** with labels `tier:S|M|L`, `tag:E|V`,
  `band:A|B|…`, `kind:defect|step|decision|hygiene` (the live label set is the
  authority — `gh label list`; there is no `kind:note`), plus `physics`,
  `needs-design-note`, `parked`, `self-merge-ok` as apply; a **milestone per
  release** (`0.6.0`); an assignee when someone is on it. The GitHub Project
  board is the view.
- **`docs/30_future/00_backlog.md` keeps the plan**: mission, the ordering
  rules, and the **priority table** with bands — each row
  `| Pri | **title** (#N) | what ships | tag | tier / effort | depends |`, and
  nothing below the table (guard: `tests/test_backlog_issues.py`). The body
  lives in the issue; the file carries no narrative. A re-cut's reasoning goes
  in the GitHub milestone description and the closing fragment, not here.
  `02_parked.md` holds the items parked with their rule-6 number.
- **The table is a generated view of the issues (#359).** Nobody edits a row
  by hand: `scripts/backlog_issues.py render` drops every row whose issue is
  closed and touches nothing else (`--closing N` counts an issue as closed
  before `gh` closes it; `--dry-run` previews). `solo_close.sh` runs it in
  preflight, so the row leaves in the closing commit; a re-cut adds or reorders
  rows in its own tier-S commit. Rows never cite another row's ordinal
  (dependencies name the band or `#N`).
- **Guard (both ways):** every priority-table row names an open issue, every
  open issue labelled `band:*` appears in the table, and every row's issue sits
  on the milestone its band header names (`scripts/backlog_issues.py check`;
  it needs `gh`, so it is a script, not a pytest; `solo_close.sh` runs it at
  every close with an issue).

## 5. Design notes and the shape of `30_future/` (MD-6)

- **Tier L and every physics change: a design note PR before code.** Open
  `note/NN-slug` with the note at `PROPOSED`; the owner of what it touches
  reviews (theory reference, `CONVENTIONS.md` citations, target numbers,
  tolerances — `CLAUDE.md` rule 1); merge at `AGREED — no code`. The
  implementing PR references it and flips it to `shipped <date>`.
- **Numbers are claimed by opening the note PR.** Gaps and out-of-order numbers
  are fine; `docs/00_INDEX.md` is generated from each note's title
  (`scripts/build_index.py`, guarded by `tests/test_doc_currency.py`).
- Every note carries `**Owner:** @handle` and `**Reviewers:** …` under its title.
- **The note is its tables, ≤ ~150 lines** (#359, 2026-11-01; `solo_close.sh`
  warns past that). Template:
  1. `**Status:**` line — PROPOSED / AGREED / SHIPPED, with dates and who ruled;
  2. **Scope** — one paragraph: the defect or capability, and what is out;
  3. **Decisions** — a table `| # | Decision | Rationale |` (`D-NN.k`);
  4. **Gates** — a table `| Gate | Statement | Expected numbers |` (`G-NN.k`);
  5. **Questions** — a table `| # | Question | Recommendation |`, ruled in place.
  No "sources reviewed" narration, no measured-fleet prose beyond the numbers
  the gates need, no second telling of the theory the test already cites.
- `25_notes/` holds **every** design note and plan, whatever its status: a note
  that has shipped is still the authority for what it decided (note 61 CV-3).
  Note 26 DV-5's status-driven move to `40_history/` is retired — nothing moves
  at release cut but the record itself.
- `30_future/` holds only `00_backlog.md`, `02_parked.md` and the
  plan-of-record documents (`01_concept_loads_plan.md`,
  `03_gui_rework_plan.md`, `04_far25_gap_analysis.md`) — nothing else.

## 6. The three shared counters — rebase before you regenerate (MD-7)

| Counter | Rule | Collision guard |
|---|---|---|
| `SCHEMA_VERSION` (`sloads/models/project.py`) | bump on the branch; **re-bump at rebase** if `main` moved past you, keeping the migration chain linear | `tests/test_migrations.py` contiguity check |
| Imperial digest (`tests/fixtures_imperial/digests.json`) | a PR carries **at most one** digest wave; regenerate *after* rebasing on `main`; the fragment names the wave; the reviewer confirms it (`PROJECT_GUIDE.md` §"Imperial output is frozen") | `test_imperial_output_matches_the_frozen_baseline` |
| Case-ID bands (`sloads/case_ids.py`) | claim a new band on the branch | `tests/test_case_ids.py` uniqueness |

Two PRs with digest waves serialize: the second rebases and regenerates. The
priority table is **not** a counter: it is a generated view (§4), so two closes
cannot collide on it.

## 7. Ownership and review (MD-8)

- `.github/CODEOWNERS` lists the single-source owners (`CLAUDE.md` rule 3 with a
  human attached): the calc SSOT files, the oracle register and digest fixtures,
  and the standard every developer's AI reads. **An oracle deviation is approved
  by the owner of `02_approved_corrections.md`, in the PR** — the "user approval"
  of `CLAUDE.md` now has a place where it is recorded.
- Review depth follows `CODE_REVIEW_PROCESS.md` §0 (tier S checklist, M scoped
  steps, L full process + design-note check). The reviewer is never the author.

## 8. Releases (MD-11)

- A **release manager** is named on the milestone and rotates. They cut per
  `RELEASE_PROCESS.md` §4 on a `release/x.y.z` branch — version bump, changelog
  build, baseline — as one PR reviewed like any other, then tag from `main`.

## 9. The AI with more than one developer (MD-9)

- **One `CLAUDE.md`** in the repo is every developer's AI contract; it is in
  CODEOWNERS and is reviewed like code. Per-developer settings live in
  `.claude/settings.local.json` (git-ignored); the shared allowlist is
  `.claude/settings.json`.
- **The AI never pushes, opens, or merges a PR.** The developer does and is the
  author of record (`CLAUDE.md` "Git that changes state is the user's to
  run"; read-only git/gh is the AI's to run).
- A PR whose diff is substantially AI-generated says so in the template's
  `AI-assisted:` line; the reviewer reads accordingly.
- "Agreed in chat" is retired: the AI's design-note check is "the note is
  merged at AGREED".

## 10. What did not change (MD-12)

The closure tiers, benchmark-first done, make-it-structural, generalize-on-first-find,
the review steps and severities, the release gate, the documentation-currency rule,
the fragment mechanism, and the AI's git rule.

## 11. Where to look, and where not to (note 61 CV-4)

Current truth is `10_standard/`, `20_theory/` and `25_notes/` — search those.
**`docs/90_record/` is the record**: the frozen completed-development archives,
the changelog and its archives, the per-release verification baselines. Nothing
in it states what is true now; every line of it states what was true on a date.
Read it only when the question is explicitly *when did this change* or *why did
it change*, and never to answer *how does this work*. It is more than twice the
size of the live corpus, so treating it as searchable makes every search worse.
Since 2026-11-01 (#359) nothing is appended to it but the changelog: the design
notes and `git log` carry the why.
