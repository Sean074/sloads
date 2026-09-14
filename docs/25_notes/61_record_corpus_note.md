# Design note 61 — the record corpus: split by function, quarantine, one telling

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6: the owner of what a
note touches reviews it as a PR)*

**Status:** AGREED 2026-09-13 (owner, in session: all six decisions, `25_notes/`
as the note corpus, every stage in 0.8.4) — ✅ **SHIPPED 2026-09-14** in 0.8.4,
except the first changelog roll, which is a release-cut action (CV-5, §5).
Amends design note 26 (`28_doc_volume_reduction_note.md`, AGREED 2026-08-16):
DV-1, DV-2 and DV-6 stand; **DV-4 is superseded by CV-2** and **DV-5's
status-driven note move is retired by CV-3**. Tier M closure.

## 1. The problem

Note 26 measured *volume* and fixed the shape of a closure: fragments instead of
edits to a 5k-line file, an era archive for the history, no history entry at
tier S. All three hold. The defect this note addresses is a different one, and
note 26's own instrument would not have found it: the cost is not the size of
the record but that **the record outnumbers the authority in the search path**,
and that the two are no longer cleanly separable.

Measured 2026-09-13:

| corpus | lines | reader |
|---|---|---|
| `10_standard` + `20_theory` — current truth | **12,489** | the owner; the AI; a new author |
| `40_history/` design notes (52 files) | **19,174** | **cited by 18 files under `tests/`** |
| `40_history/` narrative + era archives | 16,679 | nothing |
| `CHANGELOG.md` | 11,249 | nothing |

**Pure record — 27,928 lines, 2.2× the whole current-truth corpus, with no
reader.** For comparison: 79,118 lines of code, 60,280 of tests, 62,568 of docs.

Three findings, in order of weight:

1. **The search space is poisoned, and worsens by construction.** Grepping terms
   a maintainer or the AI would actually search returns 2–3× more hits from the
   record than from the authority — `safety factor` 19 record files against 9
   authoritative, `LRA` 34 against 14, `envelope` 42 against 19, `PlotData` 11
   against 3, `ground-line` 15 against 5. Every record hit is a snapshot of what
   was true on a past date. The ratio degrades every cycle: the record grows
   with time, the truth corpus grows with the code.

2. **`40_history/` is two corpora fused under one name.** 52 of its 61 files are
   design notes, and they are live reference, not history: 18 files under
   `tests/` reference the directory, citing 11 distinct notes plus the live
   history file as the standing authority for physics
   (`24_lra_beam_model_review_note.md`, `33_l7_lateral_body_aero_note.md`,
   `38_taildist_aero_state_note.md`, …). 127 links point into the directory from
   live docs. The record therefore *cannot* be pushed out of the search path as
   it stands — quarantining `40_history/` today would exile the physics
   authority. Worse, those notes are written in the past-tense register of an
   archive, so a reader who finds one cannot tell from its filing whether it
   states current truth.

3. **Tier M still tells each item twice, at length.** Note 26's DV-4 removed the
   duplication at tier S on the split *"history records decisions and behaviour
   changes; the changelog records everything"*. That split has not held. The
   current cycle: 12 items, **9,418 words** — 5,211 changelog + 4,207 history —
   about **780 words per closed item**. Today's `oracle-package-data-channel`
   pair is 797 words in seven bullets and 398 words in one paragraph carrying
   the same seven findings, the same causes, the same rejected alternatives; the
   history fragment is a re-flowed compression of the changelog fragment, not a
   different question answered. `delivered-csv-axis-statement` is 688/601;
   `oracle-gui-fleet` 427/443. Commit messages are ~20 words and contribute
   nothing to the volume — the duplication is entirely between the two
   fragments.

Note 26 answered "how does a closure get written". The unanswered question is
**where durable understanding lands**. Absent a rule, it lands in the narrative,
which is how the narrative became load-bearing and how the search path filled
with dated prose.

## 2. Decisions

Ordered as they should ship: the rule that stops the leak, the generator that
halves the writing, the split that makes quarantine safe, the quarantine, the
roll.

| ID | Decision | Rationale |
|---|---|---|
| **CV-1** | **The closure tier table gains one question:** *does a reader of the code today need this, or only a reader asking what happened?* Content a reader needs **today** goes to `10_standard`/`20_theory` in the present tense; only the dated remainder goes to the record. Applies at every tier that writes a history fragment. | The only decision here that stops the defect regenerating. Without it the split (CV-3) has to be redone: durable understanding keeps leaking into the narrative, and a narrative with understanding in it is one nobody can safely ignore. Also the direct answer to who a new author is served by — the owner's ruling is `10_standard` and `20_theory`, not the record. |
| **CV-2** | **Tier M/L writes one fragment, not two.** The `*.history.md` fragment is the single hand-written telling; `scripts/build_changelog.py` **derives** the `CHANGELOG.md` bullet from its bold lead phrase and issue reference at release cut. Hand-written `<slug>.<type>.md` fragments remain valid and remain the tier S form; at tier M/L they become optional, for the case where the consumer-facing bullet genuinely differs from the lead. Supersedes note 26 DV-4, extending its logic upward. | Halves the per-item writing and halves the duplicate grep hits **with no cap and no content lost** — the owner's constraint. A word limit would risk losing something that turns out to be needed; generation does not: the same prose is written once instead of twice, and the changelog becomes a generated index of the record rather than a second narrative of it. DV-4's premise (the two files answer different questions) is falsified above at tier M; its remedy is correct and simply needs applying one tier higher. |
| **CV-3** | **`40_history/` splits by function, not by date.** The 52 design notes move to **`docs/25_notes/`** — beside the theory, which is where the owner looks first and where CV-1 sends a new author. What remains in `40_history/` is the narrative record: the live `00_completed_development.md`, the era archives, the backlog-state narratives. Verbatim moves; **no file body is edited**. The 11 test citations, the 127 inbound links and `docs/00_INDEX.md` are rewritten in the same change. | The single largest reduction in what must be waded through, and the precondition for CV-4. A design note cited by a physics test is reference; filing it under *history* misstates its standing to every reader and is why the record cannot currently be separated from the authority. Moving rather than rewriting keeps information loss at zero and keeps the change mechanical. |
| **CV-4** | **After CV-3, the pure record is quarantined out of the default search path**: `40_history/` and `CHANGELOG.md` move under one marked root **`docs/90_record/`**, and `CLAUDE.md` states that current truth is `10_standard` + `20_theory` + `25_notes`, and that `90_record/` is consulted only when the question is explicitly *when* or *why did this change*. | ~28k lines with no reader stop competing with 12k lines that have three. Near-zero effort once CV-3 has made it safe, and it deletes nothing — the record stays complete and reachable, it simply stops being the majority of every search result. **Correct only after CV-3**; applied today it would exile the physics authority, which is a defect, not a fix. |
| **CV-5** | **`CHANGELOG.md` gains DV-1's archive rule.** At each release cut, everything below the previous release rolls into a frozen `90_record/NN_changelog_to_<version>.md`; the live file holds the current cycle plus the previous release block, same 1,500-line threshold and warn-not-fail guard as DV-6 applies to the history. | The asymmetry note 26 left: the history file is rolled and sits at 1,388 lines, the changelog was given no equivalent rule and is now 11,249 — 8× the file DV-1 was written to rescue, and growing ~800–2,000 lines per release (0.8.2 alone added 1,967). Not subsumed by CV-4: quarantining an 11k-line file still leaves an 11k-line file to read when the record is legitimately consulted. |
| **CV-6** | **A link-resolution guard ships with CV-3**: a test that every in-repo Markdown link and every doc path cited from `tests/` resolves to an existing file. | `CLAUDE.md` rule 3 — a cross-cutting convention gets a code owner plus a drift guard, never prose alone. CV-3 moves 179 link targets and 11 test citations; without a guard the move can rot silently, and the same guard then protects CV-4's second move and every future one. That no such guard exists today is a finding of this note in its own right. |

## 3. What ships

Staged; each stage is independently closable.

- **Stage 1 (CV-1, CV-2)** — forward-only, no file moves.
  `CLAUDE.md` tier table (the CV-1 question); `changes/README.md` (one telling at
  tier M/L, the derivation rule); `scripts/build_changelog.py` (derive the
  changelog bullet from a history fragment's lead); `tests/test_changelog_fragments.py`
  (derivation asserted on strings; a tier-M/L pair is no longer required).
- **Stage 2 (CV-3, CV-6)** — the move.
  52 files `40_history/` → `docs/25_notes/`, verbatim; 11 test citations, 127
  inbound links, `docs/00_INDEX.md`; new `tests/test_doc_links.py`.
- **Stage 3 (CV-4)** — `40_history/` and `CHANGELOG.md` → `docs/90_record/`;
  `CLAUDE.md` search-path rule; `docs/00_INDEX.md`; link guard re-run.
- **Stage 4 (CV-5)** — `RELEASE_PROCESS.md` §4 changelog-roll step;
  `scripts/build_changelog.py` roll function; threshold guard in
  `tests/test_changelog_fragments.py`. First roll at the 0.8.4 cut.

## 4. Not done, on purpose

- **No word caps on any fragment.** Considered and rejected by the owner: a cap
  risks losing content that later proves needed, and the volume problem is
  addressed by writing each telling once (CV-2) and by filing it out of the
  search path (CV-4), neither of which discards a sentence.
- **No rewriting of any existing fragment, changelog entry or history block.**
  CV-3 and CV-4 are file moves; every body is byte-identical after the change.
  The existing record is filed, not re-litigated.
- **The 52 notes are not re-registered or re-dated on the move.** A note's status
  line already says whether it shipped; CV-3 changes where a note lives, not what
  it claims.
- **`docs/50_reviews/` (6,950 lines) is untouched.** It is neither authority nor
  narrative and no measurement here implicates it; if it proves to be search
  noise it is a separate finding with its own number.
- **No CI job beyond the guard tests.** The release cut stays a human step with
  `--dry-run` as its preview, per note 26.

## 5. Acceptance

- **CV-1/CV-2:** a tier-M closure writes one fragment; `build_changelog.py
  --dry-run` produces the same `CHANGELOG.md` bullet from the history fragment
  alone that the hand-written pair produced. Per-item words fall from ~780 to
  the history fragment alone (~350 on this cycle's mean) with no sentence
  dropped.
- **CV-3:** `pytest` green with zero edits to any moved file's body; `git log
  --follow` resolves across the move; the 11 test citations and 127 links all
  resolve.
- **CV-4:** grep of the five sample terms against the default search path
  (`10_standard` + `20_theory` + `25_notes`) returns the authoritative files and
  no dated narrative; record hits are reachable only by naming `90_record/`.
- **CV-5:** live `CHANGELOG.md` ≤ 1,500 lines after the 0.8.4 cut; archive line
  count + live line count = the original 11,249 + header lines added.
- **CV-6:** `tests/test_doc_links.py` fails on a deliberately broken link and on
  a deliberately broken test citation.
- `ruff` clean, `mypy` clean, full suite passing at every stage boundary.

## 6. Owner rulings (2026-09-13)

1. **Note number 61** confirmed.
2. **`docs/25_notes/`** is the note corpus — `20_theory/` stays pure theory.
3. **All four stages ship in 0.8.4.** (Asked as "0.8.3"; 0.8.3 was cut the same
   day and its changelog section is closed, so the open milestone is 0.8.4.)

## 7. What the change actually moved (2026-09-14)

72 files, no body edited: 54 to `25_notes/` (44 from `40_history/`, nine live
notes from `30_future/`, this note), 18 to `90_record/` (`CHANGELOG.md`, the
completed-development live file and its five era archives, six verification
baselines, two backlog-state narratives, the executed M3-1 runbook, the git-flow
`.docx`). `40_history/` is gone; `30_future/` keeps the five plan-of-record
documents. 114 files had references rewritten.

Three things the move surfaced that the plan did not predict:

- **The link guard found rot that pre-dated it.** Twelve live links resolved to
  nothing *before* CV-3 — notes renumbered without their inbound links being
  fixed (`39_application_point_note.md` → `43_…`), a theory chapter renamed
  (`balanced_cases.md` → `ch09_balanced_airplane.md`), the FAR 25 gap analysis
  cited under `20_theory/`. All fixed here. This is CV-6 earning its place on
  the day it shipped rather than at some future move.
- **`90_record/` had to be exempted from the guard.** Its frozen archives link
  to a tree that has been renumbered repeatedly since they were written; holding
  a do-not-edit record to today's shape would mean editing the record to keep a
  test green (note 26 DV-1 forbids the edit, and rightly).
- **Two dead links are left standing, deliberately.** Note 40 cites
  `app/views/landing_loads.py` and `app/views/weight_mass.py`; the `app/`
  front end was deleted wholesale at #270 / note 60 D-60.12. Repointing them at
  a surviving owner is a content decision for whoever knows the replacement, so
  they are named in the guard's `_KNOWN_DEAD` rather than guessed at. **37 live
  documents still reference `app/`**, seven of them in `10_standard/` and
  `CLAUDE.md` — a documentation-currency defect of the GUI retirement, not of
  this note, and one that wants its own item. One instance had actually broken:
  `CONTRIBUTING.md`'s printed lint command still named `app/` (and omitted
  `oracle.py`/`oracle_app/`), so it exits 1 as written; fixed here under
  practice 4. The rest are prose mentions that are stale but not wrong to read.

One decision deferred inside CV-3's blast radius: #187's INDEX-row rule has two
halves, and only the **status** half was widened to the 54 note rows (20 rows
cleaned). The **length** cap still covers `30_future/` only, because 44 note
rows exceed it and trimming a row to one sentence is a content edit per note,
not a consequence of re-filing. `tests/test_doc_currency.py` states this at
`_LEN_ROW_DIRS`.
