# Oracle technical report — scope, shape and development protocol

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6: the owner of what a note touches reviews it as a PR)*

**Status: AGREED 2026-08-29 (owner, in session — `CLAUDE.md` rule 1's
working-alone path); SHIPPED — every agreed iteration through §23 (Appendix A,
step 166, 2026-09-07) shipped on `dev/v0.8.2`, and the 2026-09-08 review's
0.8.2 fix set (#227–#238) is closed. Milestone 0.8.2 (#151); archived at the
0.8.2 cut, 2026-09-08 — the plan of record for the milestone.** The three §5 open
questions were answered the same day and are recorded as OR-10 … OR-12 (§5),
on the same footing as OR-1 … OR-9. §6 (2026-08-30) adds the milestone's
development constraints (OR-13 … OR-15) and §7 (2026-08-30) settles the report
file and the report page (OR-16 … OR-21) ahead of iteration 1, and §8
(2026-08-30) settles the issue package the build produces (OR-22 … OR-27); §9 (2026-08-30)
settles iteration 1 and supersedes OR-24 (OR-28 … OR-37). This note settles the shape of an
**automatic technical report generated from the oracle GUI's analysis** — what
document it is, where its content comes from, where it is triggered, and the
unusual development protocol (one section at a time, each agreed by the owner
before the next is built) — so that writing the sections is mechanical rather
than a fresh judgement call per section.

**Scope.** A formal technical report limited to the **oracle GUI capability**
(`oracle_app/`, design note 32): the analysis the original McMaster FAR 23
LOADS suite performs, and nothing this replication added. It is a **clean,
modern formal document that covers the same capability** — it does not imitate
the original programs' printouts (owner ruling 2026-08-29, consistent with the
C210-15 fidelity ruling: the contract is the analysis, not the presentation).
It is **not** the consolidated loads summary report
(`10_standard/SUMMARY_REPORT.md`, the export-bundle deliverable) and not the
user guide (`docs/60_guide/`, note 34): the summary report tells a structural
analyst *what to size to*; this report tells a reviewer *what analysis was
performed, by what method, on what inputs, with what results* — module by
module, with figures.

**Strategic intent.** The existing summary report needs substantial further
development. The plan of record is: the oracle report is developed first and
agreed section by section; once agreed, it becomes the **starting point and
reference implementation for the rebuilt main-GUI report**. Decisions taken
here are therefore taken as future main-report decisions unless explicitly
marked oracle-only.

Sources reviewed: `CLAUDE.md`, `docs/10_standard/SUMMARY_REPORT.md`,
`docs/10_standard/CONVENTIONS.md`, `docs/40_history/32_oracle_gui_note.md`,
`docs/40_history/34_oracle_user_guide_note.md`, `sloads/report/*.py`,
`sloads/workflow.py`, `oracle_app/*.py`, `app/views/export_report.py`.

---

## 1. Decisions (OR-1 … OR-9)

| # | Decision | Rationale |
|---|---|---|
| **OR-1** | The report is built **inside `sloads/report/`**, sharing the existing infrastructure: the `Section`/`Table`/`Figure`/`ReportDocument` content model, the `latex.py` renderer, the `Units` limit→ultimate boundary, and the pgfplots figure machinery. A new content builder (`sloads/report/oracle_content.py`) answers *what this report says*; nothing about *how it looks* is duplicated. | One renderer, one ULT boundary, one figure engine — the consolidation rule. A parallel generator would fork the exact machinery the main-report rebuild is meant to inherit. |
| **OR-2** | **The section set is derived, not listed**: one numbered analysis section per step in `sloads.workflow.oracle_steps()`, in workflow order, bracketed by fixed front sections (identity, introduction & scope, conventions, input data) and back sections (governing summary, references, input-echo appendix). Adding a `bas` to a workflow step adds a report section with **no report-code edit**. | Inherits note 32 gate G2 exactly as the user guide did (UG-7). A hand-maintained section list is the page-list defect wearing a third hat. |
| **OR-3** | The trigger is a **new page in `oracle_app`**, appended after the derived analysis pages. This **amends note 32's "deliberately does not have" list**: the LaTeX *summary* report remains `app/`-only; the *oracle technical report* is oracle capability reporting on itself and belongs where the analysis runs. Note 32's docstring statement in `oracle_app/Oracle.py` is updated in the same change. | The report's whole scope rule is "what the oracle GUI can do"; generating it from `app/` would put the document's home outside its own scope boundary. The amendment is recorded here and cross-linked from note 32. |
| **OR-4** | **Format: LaTeX → PDF.** The `.tex` is the primary artifact (downloadable always); the PDF is compiled when a TeX engine is available, exactly as the summary report does it. Self-contained: standard-distribution packages only, figures as pgfplots/TikZ source, no external image files. | Matches `SUMMARY_REPORT.md` §2 verbatim, keeps the two documents compilable by one toolchain, and hands the main-report rebuild a format it already speaks. Word/Markdown would create a migration at the exact moment of reuse. |
| **OR-5** | `SUMMARY_REPORT.md` **§2 (identity) and §3 (whole-document content rules) apply verbatim**: determinism (byte-identical renders at the same unit selection, caller-supplied timestamp), every load ULTIMATE with the `-ULT` marker and a stated SF per case, non-loads never scaled, traceable case IDs, absence-is-content (a section whose inputs are missing renders with its `absent_reason`, never disappears). | These rules are the document standard, not a summary-report peculiarity. Restating them per document is the drift the SSOT rule exists to prevent. |
| **OR-6** | **Nothing is recomputed.** Every figure and table value comes from the same pure builders the GUI pages consume (`run_all_modules` and the per-module `ModuleResult` slices, the plot builders behind `plots_tex.py`). The report is a *view* of the analysis, with a guard test asserting table values equal `ModuleResult` values. | `content.py`'s first rule, inherited. A report that computes its own numbers eventually disagrees with the pages it documents. |
| **OR-7** | **Graphics are computed plots from oracle data** — V–n envelope, spanwise/chordwise distributions, and per-module figures — generated through the owners behind `plots_tex.py` and the `app/` plot pages. One plot owner per figure, shared between GUI display and report; the report never grows a parallel plotting path. The oracle GUI's own pages remain plot-free (note 32 unchanged on that point): the plots exist in the *document*, not on the pages. | Consolidation rule again; and it keeps the oracle GUI's original-suite fidelity intact while the formal document gets the figures a formal document needs. |
| **OR-8** | **Development protocol: one section at a time, agreed before the next.** Each iteration: (1) a content spec for one section — its tables, figures, `ModuleResult` fields, and sample values from `examples/ga6_normal.project.json`; (2) owner agreement on the spec; (3) implementation + rendered sample PDF; (4) owner approval of the rendered section; (5) next section. The first iteration is the document skeleton + front matter, which fixes the visual and formal register everything else follows. | The owner's explicit working requirement for this feature. Encoding it here makes "agreed" a recorded state per section, not a memory. |
| **OR-9** | The report's own content standard (the per-section SHALL list, as it is agreed section by section) accrues in a **new standard doc, `docs/10_standard/ORACLE_REPORT.md`**, created with the first section and grown with each agreement. It cites `SUMMARY_REPORT.md` §2–§3 rather than restating them (OR-5). When the main report is rebuilt, the shared rules migrate up rather than being copied. | The section-at-a-time protocol needs somewhere durable for each agreement to land; chat is not a register. A standard doc per document matches the existing pattern. |

---

## 2. Document skeleton

Fixed front and back matter; the analysis body is derived (OR-2). Numbering
comes from a `SECTIONS`-style single source in `oracle_content.py`, exactly as
`content.py` owns the summary report's numbering (its F-R2 lesson).

### Front matter (fixed)

| § | Section | Contents |
|---|---|---|
| — | Title page | Project identity, aircraft, date (caller-supplied), code version, `SCHEMA_VERSION`, unit system, the load-basis statement in words (`SUMMARY_REPORT.md` §3.1). |
| 1 | Introduction & scope | What analysis this report documents: FAR Part 23 Subpart C structural design loads per the McMaster suite capability; what it excludes (concept mode, sbeam decks, everything sloads-only); references — `FAR23Loads_Code.pdf`, DOT/FAA/AR-96/46, `14 CFR 23` Subpart C. |
| 2 | Axes, sign conventions and units | Cites `CONVENTIONS.md` via the existing `conventions_tex.py` owner; the LIMIT→ULTIMATE contract stated once. |
| 3 | Input data | The airplane as analysed: configuration, geometry, weights, aero data, speeds — the traceability section, from the `Project` slices the oracle pages populate. |

### Analysis body (derived — one section per `oracle_steps()` step, workflow order)

Illustratively today (the report derives this; the note does not own it):
structural speeds; flight envelope (V–n); wing loads; fuselage loads; tail
loads; aileron loads; flap loads; tab loads; engine mount; one engine out;
landing loads — each section following one template (§3 below). Input-only
steps (geometry, weight & mass, aero data) appear in §3 Input data rather than
as analysis sections; the derivation rule is *steps with a `bas` that produce
results* — settled precisely in the first OR-8 iteration.

### Back matter (fixed)

| § | Section | Contents |
|---|---|---|
| n−1 | Summary of governing loads | The governing cases across the analysis body, ULT-marked, SF stated, located. |
| n | Methods and limitations | What the analysis does not cover and how much to trust it, scoped to the oracle capability; base-method uncertainty per `theory_sources.md`. |
| A | Input echo | Complete input listing from the project file — the reproducibility appendix. |

### Per-section template (analysis body)

1. **Condition and requirement** — the FAR paragraph(s) and original program(s), one paragraph.
2. **Method** — one paragraph naming the method with its `theory_sources.md` citation; never a re-derivation.
3. **Inputs used** — the slice values this module consumed (from the `Project`, not retyped).
4. **Results** — tables from the module's `ConditionResult`s: ULTIMATE, `-ULT` marked, SF stated, located.
5. **Figures** — the section's computed plot(s) (OR-7), where the module has one.

The template is finalised — possibly amended — when the first analysis-body
section goes through OR-8; after that it is fixed and a guard test holds every
section to it.

---

## 3. Acceptance gates

| Gate | Statement |
|---|---|
| **G-OR-1** | The report builds from `examples/ga6_normal.project.json` in CI without error, and the `.tex` compiles to PDF where a TeX engine is present. Extends the existing report build test rather than duplicating it. |
| **G-OR-2** | Every result-producing step in `sloads.workflow.oracle_steps()` has exactly one analysis section, and every analysis section maps to a step. Guard test (the G2 inheritance, OR-2). |
| **G-OR-3** | Every load table value equals the corresponding `ModuleResult` value × its case's SF — asserted through the content model, never by matching LaTeX strings (OR-6). |
| **G-OR-4** | Every load carries `-ULT` and a stated SF; no non-load quantity is scaled or marked. Reuses the summary report's marking checks (OR-5). |
| **G-OR-5** | Two builds of the same project at the same unit selection are byte-identical (OR-5). **Amended 2026-08-30 (§7, OR-20):** the unit selection is a `ReportSpec` field, so the statement is *two builds of the same project **and the same report spec** are byte-identical* — the spec plus the project is the complete recipe. **Extended 2026-08-30 (§8, OR-26):** G-OR-16 carries the same statement to every file of the issue package, not the `.tex` alone. |
| **G-OR-6** | The report contains no concept-mode or sloads-only content: building from a project with concept fields populated yields the same oracle-scope document as the same project with them absent. Guard test — this is the scope rule made structural. |
| **G-OR-7** | A half-filled project yields a complete document with `absent_reason` sections, never a traceback and never a silently missing section (OR-5, absence-is-content). |
| **G-OR-8** | Each agreed section's SHALL list in `ORACLE_REPORT.md` (OR-9) has a corresponding assertion in the report tests — an agreement without a guard is prose, not a gate. Checked at each section's closure. |

---

## 4. Closure tier and delivery

**Tier L** — a new capability, a note-32 scope amendment, and a new standard
doc. Design note agreed first (this note); `theory_sources.md` is cited via the
per-section method citations rather than gaining new equations (the report adds
no physics).

**Milestone 0.8.2, one backlog row, solo profile.** The whole report is **one
backlog item** pointing at this note — **issue #151**, the row's owning issue —
worked on `dev/v0.8.2`. **#152 is this note's design-note PR** (`note/44-slug`,
merged at AGREED per `DEVELOPMENT_PROCESS.md` §5), **not an issue** — the two
numbers share a series on GitHub, so cite #151 for the work and #152 only for
the agreement that authorised it. The row is owned by #151, which carries the
band, tier, tag and milestone. Issues are not
opened per section (`DEVELOPMENT_PROCESS.md` §0: the backlog is the record;
OR-9's accruing standard doc is the per-section register). Delivery follows
OR-8 as **one commit per agreed iteration** — ordinary work commits, keeping
the step-per-commit `git log` record — with a single `solo_close.sh` closure
(fragments, history entry, row removal) when the final section is agreed.
0.8.2 slots ahead of 0.9.0 (band B2, main-GUI development) deliberately: this
report is B2's declared starting point.

| Commit | Contents |
|---|---|
| 1 | `oracle_content.py` skeleton + section derivation + the oracle_app report page + `ORACLE_REPORT.md` created + gates G-OR-1/2/5/6/7. **Amended 2026-08-30 (§7):** also `ReportSpec` + `REPORT_SCHEMA_VERSION` + the `io` load/save/fingerprint owners (OR-17, OR-21), `examples/ga6_normal.report.json`, and gates G-OR-10 … G-OR-13. **Amended 2026-08-30 (§8):** also the issue-package builder + `MANIFEST.txt` + the `data/` emitters (OR-22, OR-23) and gates G-OR-14 … G-OR-17 |
| 2 | Front matter (title, §1–§3) — the register-setting iteration |
| 3… | Analysis-body sections, one OR-8 iteration each, in workflow order; G-OR-3/4 land with the first results section |
| final | Governing summary, methods & limitations, input echo appendix, note-32 cross-link, tier-L closure |

---

## 5. Answers to the open questions (OR-10 … OR-12)

*Resolved by the owner 2026-08-29, in session. Decisions, on the same footing
as OR-1 … OR-9; §3's gates apply to them.*

### OR-10 — CI builds the `.tex`; the PDF compile is a local check

`ci.yml` carries no TeX engine today. G-OR-1's CI leg therefore asserts the
**`.tex` build** (the report builds from the example without error and the
source renders); compiling to PDF is checked **locally at each OR-8 iteration**
— the rendered sample PDF is what the owner approves, so every agreed section
has in fact compiled. This matches the summary report's existing practice: the
`.tex` is the primary artifact and is self-contained for any standard engine
(`tectonic`, `latexmk`, `pdflatex` — `SUMMARY_REPORT.md` §2). Adding a
`tectonic` compile job to CI is a candidate 0.9.0 improvement, not a
prerequisite here.

**Amended 2026-08-30 (§8, OR-22/OR-26):** the CI leg builds the **issue package** and asserts its manifest (G-OR-14), the `.tex` being one file of it; and self-containment is read at package level (OR-26), the `.tex` reading `data/` at compile time.

### OR-11 — Both examples build the report in CI

`examples/baron_58.project.json` already exists (note 34, UG-9). G-OR-1 runs
over **both** `ga6_normal` and `baron_58`: the single is the Appendix A oracle
case; the twin exercises the engine-mount and one-engine-out sections as
*present* rather than `absent_reason`, and (per UG-12) is the SI-channel case,
so the two builds together cover both unit selections of G-OR-5.

**Amended 2026-08-30 (owner):** the *machine* covers the twin every section —
G-OR-1 has built both packages on every push since iteration 1 — but the
**owner's read of the Baron report is one pass at the end of report
development**, not a second review per section. The GA6 is the review vehicle
throughout (it is the Appendix A oracle case, so a wrong number there is a
*known*-wrong number), and reviewing both per section doubles the reading for a
second opinion on the same renderer.

What that end pass is for is the half CI cannot assert: that the twin's report
*reads* correctly where it differs from the oracle case — the `absent_reason`
wording on sections the GA6 has and it does not (and the reverse), the DERIVED
planform provenance where the GA6 now says entered (Appendix B is not bundled,
so the Baron has no printed polylines), the SI channel's number formatting under
UG-12, and the engine-mount and one-engine-out sections appearing as *present*.
The deferral is safe because those are stated by guards rather than by eye —
`test_a_tail_table_states_where_its_planform_came_from` asserts the provenance
label in both directions, and the package manifest and determinism gates assert
the rest — so what is deferred is judgement, not detection. A GA6-shaped
assumption reaching the renderer fails CI on the twin the same day it lands.

### OR-12 — Iteration order is workflow order

The default stands: analysis-body sections are developed in
`oracle_steps()` order, matching the section numbering, so each iteration's
sample values are values the already-agreed sections produced (the note 34
UG-10 lesson — writing a downstream section first means inventing numbers the
tool later contradicts).

---

## 6. Development constraints for milestone 0.8.2 (OR-13 … OR-15)

*Owner ruling 2026-08-30, in session (`CLAUDE.md` rule 1's working-alone path).
Milestone-scoped: these constraints govern `dev/v0.8.2` only, and lapse at the
0.8.2 cut. They are decisions on the same footing as OR-1 … OR-12; §3's gate
discipline applies to them via G-OR-9.*

The report is a **view** of an analysis that is already oracle-locked and
already agreed (OR-6, OR-7). Building a view is therefore not an occasion to
adjust what is being viewed. These three rules make that structural rather than
a matter of restraint.

### OR-13 — The frozen set: solver and existing oracle GUI, additive-only

For the duration of 0.8.2 the following are **frozen** — no edit, including
refactors, renames, formatting and type-annotation churn:

| Frozen | Why |
|---|---|
| `sloads/modules/**` | The solver. Appendix A holds it to ±0.1 %, but an oracle test only catches a change that moves a printed number; the freeze also catches the ones that do not. |
| `oracle_app/Oracle.py`, `form.py`, `labels.py`, `results.py`, `__init__.py` | Every existing oracle GUI page and its input/output behaviour. The C210-15 fidelity ruling makes these the consumed-value contract the report reads from. |

**Permitted, and only these:**

1. **New files** — `sloads/report/oracle_content.py`, the new `oracle_app`
   report page, `docs/10_standard/ORACLE_REPORT.md`, new tests. Additive work in
   `oracle_app` is the milestone's own first commit (OR-3) and is not a change
   to the frozen set.
2. **The one OR-3 amendment** to `oracle_app/Oracle.py` — note 32's
   "deliberately does not have" statement, updated to record the amendment.
   **Widened 2026-08-30 (§7, OR-16):** the amendment is the docstring **and** the
   report page's registration in the page dict / `st.navigation`, since a derived
   page set has no other way to carry a non-step page. One commit, one manifest
   update, the authority named in the message.
3. **A blocking-defect fix admitted under OR-15**, which carries its issue
   number and updates the manifest in the same commit.

Shared code outside the frozen set (`sloads/report/*.py`, `sloads/workflow.py`)
stays open under the ordinary rules — but a change there that alters the
**summary report's** output is a behaviour change to a delivered capability
(tier M), not report plumbing, and is ticketed like any other.

### OR-14 — A defect found in frozen code is filed, not fixed

Reading the solver and the oracle GUI closely is the point of writing this
report, so it will surface defects. Every one is **written up as a GitHub issue
with a body** the session it is found (`CLAUDE.md` rule 5), and left in place.
Diagnosing a suspected defect far enough to file it accurately is expected; the
line is the edit, not the investigation. The report renders what the frozen code
actually produces — a document that quietly papers over a defect is worse than
one that exposes it, and the issue is the exposure.

This does not weaken `CLAUDE.md` rule 4 (generalize on first find): the sweep of
the defect class is part of the *ticketed* fix, wherever that fix lands.

### OR-15 — Triage of what is found

| Finding | Milestone |
|---|---|
| **Prevents progress** — the report cannot be built, or cannot be built truthfully, without the fix | **0.8.2**, admitted by explicit owner decision, with an issue number and a manifest update in the fixing commit |
| Concerns **oracle GUI output** — a value, label, unit, frame or presentation the report consumes — but the report can be written correctly around it | **0.8.3** |
| Anything else — solver fidelity, main GUI, concept mode, hygiene | **0.9.0** |

"Prevents progress" is deliberately narrow: a wrong number the report can state
accurately (because the report states what the analysis produced) does **not**
prevent progress — it is an 0.8.3 or 0.9.0 ticket and, where the error is
material, a `Methods and limitations` entry in the back matter until it is
fixed.

### G-OR-9 — the freeze is a test, not a promise

`tests/test_frozen_set.py` holds a SHA-256 manifest of every frozen path and
fails on any change to one. Updating the manifest is the deliberate act that
records an OR-13 exception: the commit that changes a frozen file updates the
manifest beside it and names its authority (OR-13 item 2, or an OR-15 issue
number) in the commit message. `CLAUDE.md` rule 3 — a cross-cutting convention
gets a code owner and a drift guard, never a prose rule alone.

---

## 7. The report file and the report page (OR-16 … OR-21)

*Owner rulings 2026-08-30, in session (`CLAUDE.md` rule 1's working-alone path),
settling the shape of the OR-3 page and the artifact it edits before iteration 1
is built. Decisions on the same footing as OR-1 … OR-15; §3's gate discipline
applies via G-OR-10 … G-OR-13.*

### OR-16 — The trigger page, and what OR-13 admits

The OR-3 page is a **new file, `oracle_app/report.py`**, appended after the
derived analysis pages (title *Report*, url_path `report`). Its blocks, top to
bottom: report file (load / download / new); document identity; abstract;
signatures; distribution and marking; content selection; preflight; generate and
download.

A derived page set has no way to carry a non-step page except through the entry
point, so registering it necessarily touches a frozen file. **OR-13 item 2 is
widened accordingly**: the admitted OR-3 amendment to `oracle_app/Oracle.py` is
the docstring statement **and** the page's registration in the page dict /
`st.navigation` — one commit, one manifest update, the authority named in the
message. Nothing else in that file moves.

### OR-17 — Report metadata is its own artifact, not a `Project` slice

A report is a **document instance**, not a property of the airplane: one project
yields many issues (different customers, revisions, scope selections). Metadata
therefore lives in a **new `ReportSpec` dataclass** with its own
`REPORT_SCHEMA_VERSION`, serialised to a **`report.json`** file mapped in
`sloads/io.py` (`load_report`, `save_report`) — **amended 2026-08-30 (§9,
OR-28): that file lives inside the issue package directory, not beside
`<stem>.project.json`** — — which stays the only dataclass↔JSON mapping. **`Project` and
`SCHEMA_VERSION` are not touched**, so note 32's OG-13/G6 promise (a project
saved by either GUI opens in the other unchanged) is untouched, and no migration
is owed.

The page holds one active spec at a time in session state; the user swaps files
to switch issues. The file widget is **page-local**, deliberately not in the
shared `app_shell` sidebar: that sidebar is shared with `app/`, and the report
file belongs to the report page. Editing the spec marks the session dirty by the
same rule the project file uses.

The artifact is also what makes a headless build expressible later
(`sloads oracle-report <project> --report <spec>`). Not iteration 1; the door is
open rather than walled.

### OR-18 — Title block, and DRAFT until signed off

`ReportSpec` carries: title, report number, revision/issue, issue date, issuing
organisation, customer/programme, abstract, revision history (rows of date /
revision / description / by), distribution statement, classification marking
(rendered in every page footer), and three signature rows — **prepared, checked,
approved**, each name / role / date.

**Any empty signature name makes the document a draft**: a DRAFT watermark and a
footer marking, still fully buildable and downloadable. All three names present
clears it. The document never silently presents itself as approved, and the page
never blocks the build to force the point.

### OR-19 — Section selection is stated exclusion, never omission

The user selects which analysis sections an issue carries. **Every derived
section always exists** — G-OR-2 stays literally true. A deselected section
renders its heading and *"not included in this issue — excluded by user
selection at report generation"*, and the title page lists the exclusions: this
is `SUMMARY_REPORT.md` §3.4's filtered-export rule applied at section level, and
an analyst never receives a reduced document without being told.

Selection is limited to **analysis-body sections and the Appendix A input echo**.
Front matter, the governing-loads summary and methods & limitations are never
selectable — they carry the load basis and traceability statements. Exclusions
are stored **by workflow step key**, never by section number, which moves as
steps are added.

**Absent is not excluded.** A step whose inputs are missing renders its
`absent_reason` (OR-5) whether or not it was selected; the two states are
distinct in the preflight table and in the document.

### OR-20 — The document's unit system is a `ReportSpec` field

`spec.unit_system` governs the document, so a report file plus a project is a
complete, reproducible recipe. The sidebar toggle continues to govern what the
**analysis pages display**; the report page carries its own control bound to the
spec field and states the split in a caption.

That is a second owner of a selection the sidebar otherwise owns alone, so it is
made structural rather than remembered (`CLAUDE.md` rule 3): **G-OR-12**. And
**G-OR-5 is reworded** to fold the qualifier in — *two builds of the same project
and the same report spec are byte-identical*.

### OR-21 — Provenance: identity, anchors, fingerprint — stamp and warn

The spec records what airplane definition it was written for, and the document
prints it. Two questions are answered by two different things, and the stamp
carries both:

| Question | Answered by |
|---|---|
| *Is this the same airplane?* | **Human identity** — project name, aircraft designation, and anchor values (MTOW, wing area, design speeds). This is what a reader of the PDF actually checks; a hex string tells them nothing. |
| *Has the definition changed since this issue was signed?* | **The fingerprint** — nothing else answers it cheaply. |

The fingerprint is a SHA-256 over a **canonical projection of the inputs the
oracle report consumes** — the slices behind `oracle_steps()`, sorted keys,
round-trip float repr — **not** over the project file. Hashing the whole file
would fire on a concept-mode field, an sloads-only field or a re-save with
different key ordering: a warning about a document none of them can affect, and a
warning that fires on noise is ignored on signal. The scope boundary is asserted,
not described: **G-OR-13**.

The stamp carries its own **`fingerprint_version`**. When a later milestone adds a
field to an oracle-consumed slice, every existing report's fingerprint goes stale;
on a version mismatch the page states *"cannot compare — stamped by an earlier
fingerprint definition"* rather than crying wolf, and the human anchors still
compare.

On load against a different project the page **warns and builds anyway** — a
banner naming both sides, and a note in the document's identity block. It never
refuses: a project is legitimately revised under the same report number, and
refusing would obstruct the normal case to police the rare one.

The fingerprint is **not a signature** — there is no key, so it detects accident,
not tampering. And it is not the record of what was analysed: the **Appendix A
input echo is** the definitive record; the fingerprint is the fast comparator that
says *go read Appendix A, something moved*.

### Gates added by this section

| Gate | Statement |
|---|---|
| **G-OR-10** | No `ReportSpec` field reaches any `ModuleResult` or any load value — document metadata cannot move a number. |
| **G-OR-11** | `ReportSpec` round-trips through `save_report`/`load_report` stably; a missing or unreadable report file yields a default unsigned draft, never a traceback. |
| **G-OR-12** | The report build path reads `spec.unit_system` and never `active_system()` — the document's unit owner asserted, not conventional. |
| **G-OR-13** | Mutating any oracle-consumed field changes the fingerprint; mutating any field outside the oracle scope does not (the OR-21 scope boundary, the same structural move as G-OR-6). |

---

## 8. The issue package (OR-22 … OR-27)

*Owner rulings 2026-08-30, in session, settling what the report page's build
button actually produces. A report issue is a **package**, not a file: the
document plus the data behind every table and plot plus the definition it was
built from, in one directory that can be archived, signed and re-opened years
later. Decisions on the same footing as OR-1 … OR-21; gates G-OR-14 … G-OR-17.*

### OR-22 — Build produces a directory, not a download

The page's build action writes an **issue package** — a real directory on the
local filesystem, since the oracle GUI is a locally-run tool (`sloads-oracle`)
and the user's machine is the server. The page carries an output-root control;
the directory name is derived from the report number and revision
(`LR-0142_RevB/`), never from the clock.

```
LR-0142_RevB/
  report.tex          the document (OR-4)
  report.json         the spec the page edits (OR-28; never machine-written)
  build.json          the as-built stamp: fingerprint, timestamp, generator (OR-30)
  project.json        a copy of the airplane definition it was built from
  MANIFEST.txt        a full SUMMARY_REPORT.md §4.7 manifest (OR-35)
  data/<step_key>.csv one file per table or plot the document draws (OR-23)
  report.pdf          present only after a local compile (OR-26)
```

`app/`'s export page delivers a zip through the browser instead
(`export_report.py`, "Download all"); that is the right shape for a page that
may be served remotely, and the wrong shape here. A zip of the same tree is a
candidate convenience later, built from the same builder — not iteration 1.

### OR-23 — The shipped data is the document's source, not a copy of it

Tables are generated `.tex` fragments the document `\input`s; plots are
pgfplots reading `data/<step_key>.csv` at compile time. **The document therefore
cannot disagree with the shipped data, because it is reading it** — the
architecture is the guarantee, so no drift-guard between two renderings is owed
(`CLAUDE.md` rule 3 is satisfied by removing the duplication rather than
policing it). It also makes OR-6 auditable from outside: a reviewer diffs the
CSV against the analysis page instead of trusting the sentence.

Files are named by **workflow step key**, never by section number, for OR-19's
reason. Each carries a comment header stating the **units string including the
`-ULT` marker, the safety factor and its basis, the step key, and the
fingerprint** — a data file lifted out of the folder and mailed onward is still
self-describing, which is what `SUMMARY_REPORT.md` §3.1 requires of every
load-bearing number. **G-OR-15**; no orphans in either direction, **G-OR-17**.

### OR-24 — The package's `report.json` is a snapshot; the working spec stays put

**Superseded 2026-08-30 by OR-28 (§9): the package directory is the spec's home,
and the as-built stamp moved to `build.json` (OR-30). The reasoning below is kept
because it is what OR-28 had to answer, not because it still governs.**

OR-17's placement stands: the **working** spec lives at `<stem>.report.json`
beside the project, and is what the page loads and edits. The build **copies it
into the package**, stamped with the OR-21 fingerprint and the build timestamp
supplied by the caller. The two copies have different jobs — one is the editable
recipe for the next issue, the other is the immutable record of this one — and
loading a package's `report.json` back into the page is reading history, not
resuming work.

`project.json` is copied in for the same reason: anyone holding the folder can
rebuild the document without hunting for the airplane file, and the fingerprint
has its subject present to compare against rather than merely named.

### OR-25 — Rebuild clobbers the revision; a new revision is a new directory

Building again into the same report number and revision **overwrites in place,
silently** — it is a build product, and the edit-build-read loop must not carry
friction. Bumping the revision in the spec produces a **new directory beside**
the old one, so an issued revision is never destroyed by continued work. The
package is disposable; the revision history in the spec (OR-18) is not.

### OR-26 — Self-containment is a property of the package

**Superseded by an amendment to the standard itself, 2026-08-30 (owner).** This
section first recorded a *reading* of `SUMMARY_REPORT.md` §2 — that a CSV is not
an image, so OR-23 was already permitted. A rule that says one thing and means
another leaves the next person to re-derive the reading from a design note, which
is the prose-rule-without-an-owner failure `CLAUDE.md` rule 3 exists to prevent.
So §2 was amended instead, tier M, and OR-26 is now a **citation** of it:

- The **image prohibition is unchanged and absolute** — figures are pgfplots/TikZ
  source, never `\includegraphics`. Every property that rule protects
  (deterministic, diffable, unit-testable as text, vector in the document's own
  fonts, no non-TeX toolchain) is untouched by reading a text data file.
- A new **§2 *Data reference*** clause permits a report **delivered as a package**
  to read plain-text data from inside it, on four conditions the issue package
  already meets: the file is in the manifest (G-OR-14), the path is relative and
  stays inside the package root, the file is self-describing to §3.1 (G-OR-15),
  and determinism holds for the whole package (G-OR-16).
- A report **delivered as a standalone `.tex`** — which `app/`'s summary report
  still is, via its own download button — **SHALL NOT** reference any external
  file, and now has the guard that says so
  (`test_report_latex.py::test_the_standalone_tex_references_no_external_file`).

The amendment is not a liberty taken for this milestone: §1.5, §4.7 and §5 already
require the report to travel with companion data files and to point the reader at
them. Reading them makes that reference **mechanical instead of editorial**, so the
document cannot misquote its own companion — §4.7's intent, finally with teeth.

The PDF (OR-10, local) is **compiled out of tree** and only the PDF copied back:
no `.aux`, `.log`, `.out` or engine cache ever enters the package, or the
determinism gate becomes a fight with the toolchain. **G-OR-14**.

Determinism now applies to the whole tree: **G-OR-16** extends G-OR-5 from the
`.tex` to every file in the package. CI's OR-10 leg builds the **package** and
asserts its manifest, not the `.tex` alone.

### OR-27 — The button is *Build*; DRAFT stays the unsigned state

OR-18 already gives DRAFT a meaning — the document is unsigned. The build action
is therefore called **Build issue package**, and it fires identically for signed
and unsigned specs: a signed report is built by the same button, and an unsigned
one is built with the watermark. Naming the button *Draft* would make the two
meanings collide on one page.

### Gates added by this section

| Gate | Statement |
|---|---|
| **G-OR-14** | The package contains exactly the files its `MANIFEST.txt` lists, with matching hashes — no engine aux files, no strays, nothing listed but absent. **Widened 2026-08-30 (§9, OR-35): the manifest also meets `SUMMARY_REPORT.md` §4.7.** |
| **G-OR-15** | Every shipped data file's header states its units string (with the `-ULT` marker), safety factor and basis, step key and fingerprint (`SUMMARY_REPORT.md` §3.1 applied to detached files). |
| **G-OR-16** | Two builds of the same project and the same report spec produce byte-identical **packages**, file for file — G-OR-5 extended from the document to the tree. |
| **G-OR-17** | Every file in `data/` is referenced by the `.tex`, and every table or plot in the `.tex` is backed by a file in `data/` — no orphans in either direction. |

---

## 9. Iteration 1 — amendments settled in planning (OR-28 … OR-37)

*Owner rulings 2026-08-30, in session, settling iteration 1 before it is built.
Several of these **override** §7 and §8 as written; where they conflict, §9 wins
and the superseded text says so. Decisions on the same footing as OR-1 … OR-27.*

### OR-28 — The package directory is the spec's home

**Supersedes OR-24, and amends OR-17 and OR-22.** The working `report.json`
lives **inside the package directory** and is what the page loads and edits.
There is no `<stem>.report.json` beside the project.

OR-24 split the spec in two — an editable recipe beside the project, an immutable
snapshot in the package — and gave them different jobs. In practice the split
costs more than it buys: a user with six issues of one report keeps six spec
files in the project folder with no directory to disambiguate them, and every
build has to answer *which* spec it came from. One issue, one directory, holding
everything about that issue, is the model the analyst already has in their head.

A real consequence, and a gain: `MANIFEST.txt` must match the tree (G-OR-14), and
`report.json` is now in the tree. A stale manifest hash for `report.json`
therefore means **the spec has been edited since the last build** — a
freshness signal that would otherwise have had to be invented, and that the
preflight block states rather than computing separately.

### OR-29 — Report root, and how a package is opened

Packages live under **`<project dir>/reports/`** by default, overridable by a
path field on the page. The page lists the report directories it finds there in a
selectbox, plus *New*.

Streamlit has no directory picker and the file uploader returns files, not
folders — so discovery plus a path override is not a compromise, it is the only
mechanism available to a locally-run app. It is also what makes the page testable
without a browser: a test points the root at `tmp_path`.

### OR-30 — The as-built stamp is `build.json`; `report.json` is never machine-written

**Amends OR-24's stamping.** The fingerprint, the caller-supplied build timestamp
and the generator version go in a **`build.json`** the builder owns. `report.json`
holds only what the user typed.

With OR-28 putting one `report.json` in the tree, stamping it in place would mean
the build writes the file the user edits — and G-OR-16 (byte-identical rebuilds)
would then need a by-name exclusion list for the stamped fields, maintained
forever as the spec grows. Separating the two files removes the carve-out instead
of maintaining it, and keeps `report.json` diffable as a record of human intent.

### OR-31 — Iteration 1 is the front matter, and the abstract is the spec's

Iteration 1 delivers: cover/title page, **abstract** (OR-18's free text), table of
contents, list of figures, list of tables, and **section 1 Introduction**.

The **governing-loads summary is not this iteration.** It is computed from
delivered loads and cannot honestly exist before the sections it summarises; OR-19
already rules it never-selectable for that reason. Naming both "the summary" is
what made this worth stating.

### OR-32 — Not-yet-built is a third state, distinct from excluded and absent

A derived analysis section that the generator does not yet build renders its
heading and *"not yet implemented in this revision of the report generator"*.

This is a **third state**, and the document and the preflight table both keep the
three apart:

| State | Means | Ruled by |
|---|---|---|
| **Excluded** | a user deselected it for this issue | OR-19 |
| **Absent** | the inputs it needs are missing | OR-5 |
| **Not yet implemented** | the tool cannot produce it yet | OR-32 |

Collapsing the third into either of the others would be a false statement about
whose decision produced the gap — the reader would be told a person chose to omit
a section, or that their data was incomplete, when neither is true. It also lets
**G-OR-2 hold from the first commit** rather than waiting for the last section:
every derived step has a section throughout, and the section says what it is.

### OR-33 — `REPORT_SCHEMA_VERSION` stays at 1 for the milestone

Sections will add spec fields as they are agreed. The version stays **1** until
the 0.8.2 cut: no report file has shipped, so there is nothing to migrate, and
bumping a version against no readership teaches the number to mean nothing. It
starts carrying information at the cut.

### OR-34 — The empty lists still render

`\listoffigures` and `\listoftables` are emitted from iteration 1, empty. A
document that silently drops its own front matter while incomplete is harder to
trust than one showing an empty list — and the empty list is itself accurate.

### OR-35 — `MANIFEST.txt` is a full `SUMMARY_REPORT.md` §4.7 manifest

**Widens OR-22 and G-OR-14.** OR-22 described `MANIFEST.txt` as every file with
its SHA-256. That is not enough: the §2 *Data reference* clause (OR-26) conditions
the packaged-report permission on the package "carrying a manifest (**§4.7**)",
so §4.7 binds — per-file contents, units, sign and axis conventions and the
section that summarises it, under an opening statement of the package's unit
system, with section references from the numbering owner and never a literal
`§N`, exhaustive **in both directions**.

Both of §4.7's SHALLs were written after real defects (CR-C-1, an artifact
shipped with no row; CR-C-3, a basis cell wrong through two reviews), so this is
not ceremony. The shape is already built: `content._section_manifest` renders
**File / Contents / Units / Conventions / Summarised in**, and
`tests/test_bundle_manifest.py` holds it in both directions. The issue package
reuses that shape rather than inventing a lighter one.

### OR-36 — The PDF compile is a later iteration

`sloads/export/pdf.py`'s `compile_pdf` takes the LaTeX **source string** and
compiles it in a temporary directory — which is exactly OR-26's out-of-tree
requirement, and exactly why it cannot compile this document: a `.tex` that
`\input`s `data/*.tex` and reads `data/*.csv` will not find them there.

Extending it to compile a package tree is its own change with its own gate, and
it is not on iteration 1's critical path: CI asserts the `.tex` build (OR-10), and
front matter is reviewable as source. G-OR-1's PDF leg lands with that change.

### OR-37 — No example report file

The note's §4 commit-1 row called for `examples/ga6_normal.report.json`. OR-28
leaves nowhere beside the project for it to live, and an example *package
directory* checked into `examples/` would be a build product in source control.
Tests construct a spec with `default_spec()` into `tmp_path` instead. The headless
build path (OR-17's `sloads oracle-report`) is unaffected — it will take a
package directory.

### Gates

| Gate | Statement |
|---|---|
| **G-OR-14** | **Widened by OR-35:** the package contains exactly the files `MANIFEST.txt` lists, with matching hashes, and the manifest meets `SUMMARY_REPORT.md` §4.7 — the five columns, the opening unit-system statement, section references from the numbering owner, exhaustive both ways. |
| **G-OR-18** | The three gap states (OR-32) are distinguishable in the rendered document and in the page's preflight: no state's wording can be produced by another's cause. |
| **G-OR-19** | `report.json` is byte-identical before and after a build — the builder never writes the user's spec (OR-30). |

**Note on vacuous gates.** G-OR-15 (data-file headers) and G-OR-17 (no orphans)
are written in iteration 1 but have no `data/` files to act on until the first
analysis section. Their tests say so in the docstring: a gate that passes because
there is nothing to check must not read as a gate that passed.

## 10. Iteration 2 — Section 2, Loads Configuration (OR-38 … OR-44)

*Agreed with the owner in session, 2026-08-30, during the live GUI review. Content
spec per OR-8; SHALL list in `ORACLE_REPORT.md` §3.3; decisions on the same
footing as OR-1 … OR-37.*

| # | Decision | Amends |
|---|---|---|
| **OR-38** | **Section 2 groups four steps as subsections** — geometry, weight and mass properties, structural design speeds, flight envelope — under one numbered section, "Loads Configuration". Subsections rather than a flat merge, so every step keeps exactly one home and **G-OR-2 is unchanged**. Grouping is declared as data (`SECTION_GROUPS`), and a group's members must be contiguous in workflow order. | OR-2 (extends) |
| **OR-39** | **The document owns its own section titles** (`DOCUMENT_TITLES`). A heading is never `WorkflowStep.title`: the workflow is our machinery, the reader of the PDF has no concept of it, and a nav rename must not retitle a signed report. Both directions guarded. | new |
| **OR-40** | **The V-n envelope is the polyline through FLTLOADS' produced design points**, one figure per loading/altitude block. `vn_diagram.build_vn_diagram` is not used: its own docstring calls it an approximate Structural-Speeds sanity plot whose stall boundary assumes constant CLmax. On the reference GA wing it predicts n = 3.51 at the STALL +N corner where the analysis computes 3.80 — **8% low**, because the real boundary follows CL rising 1.395 → 1.512 with α and the compressibility correction. Plotting it would put the report's own design points visibly off their own boundary. | OR-6 (applies) |
| **OR-41** | **The SELECT case list belongs to the load-case section**, not to 2.4. Section 2.4 carries the figures and the corner load factors; the case table is the next iteration. Same source, different projection — no number is tabulated twice. | new |
| **OR-42** | **Tables and plots render inline for now.** OR-23's `data/*.csv` externalisation becomes its own iteration, with **G-OR-15 and G-OR-17 landing there**; they stay vacuous until it. Deferral, not reversal: the manifest stays consistent because no `data/` files exist yet. | OR-23 (defers) |
| **OR-43** | **`build_oracle_document` reduces its project through `reduce_to_oracle_inputs` first.** The document is a function of the oracle projection, hashed by the same reducer the fingerprint uses — one guarantee, one owner. Found by G-OR-6 failing: section 2 quotes each module's certification basis, and on a concept project the speeds module takes the Part 25 Mach-margin route and says so, so a concept-only field reached the printed page through a module note. | OR-21, G-OR-6 (implements) |
| **OR-44** | **Section 2 states no load in force or moment units.** Nothing in it is scaled to ultimate or marked `-ULT`, and no table states a safety factor — but every value still passes through the `render` ultimate boundary rather than being hand-formatted, so the section never decides what a load is. **G-OR-4 holds by construction.** **Amended by the owner, 2026-08-30:** the first draft said "section 2 carries no loads" and put a note under every table saying geometry, mass, speeds and load factors *are not loads*. That is wrong — **n is a limit load factor, so a load factor is a load** — and the note was removed outright rather than reworded. What section 2 may state about them is that they are **LIMIT**, which the V-n captions and the corner table do at point of use. | OR-5, G-OR-4 |

### Section 2.1 and 2.2 extended (owner, in session 2026-08-30)

**OR-45 — 2.1 states every surface, one table each.** Wing planform, horizontal
tail and elevator, vertical tail and rudder, aileron, flap, and one table per
trim tab; each with its area, planform figures, tail arm stations where it has
them, and its control deflections.

**OR-46 — the report may echo a project input, and must label it.** These are the
first values section 2 reads from the project rather than from a `ModuleResult`:
no module returns a control-surface area or a throw. This does not weaken OR-6,
which forbids *re-deriving* a value and not *reporting* one, but the distinction
is the reader's to see, so 2.1 states once that the empennage and control-surface
values are the configuration as entered. The field lists are declared as data so
a renamed input fails the suite instead of silently emptying a row, and G-OR-3's
guard was widened from "every number came from a `ModuleResult`" to "every number
came from a result **or** from the project as entered, and none is invented".

**OR-47 — 2.2 states the weight and CG cases**: name, role, weight, Xcg, Zcg and
analysis, with a note explaining what role and analysis govern. `CgCase.analyses`
is a `set` by design (G-3), so the printed order is declared rather than taken
from iteration — set order is not a document property, and resting the
determinism gates on it is the kind of defect that passes locally and fails on
another interpreter.

### Findings recorded, not fixed

- **A condition holding no loads still carries `safety_factor = 1.5`** — the
  geometry, mass-properties and design-speed conditions. No value is affected
  (the boundary scales by units and quantity, not by the stamp) but the claim is
  false: a wing span has no safety factor.

  **Not an OR-14 finding, on inspection.** The first reading of this blamed the
  frozen modules. It is not theirs: `1.5` is the dataclass default on
  `ConditionResult.safety_factor` (`sloads/models/results.py`) and
  `safety_factors.GoverningTable.stamp` overwrites it from `registry`. None of
  those is in the frozen set, so the fix is ordinary work at its own owner rather
  than something the freeze defers.

  `flight_envelope` is **not** affected and was wrongly listed at first: its
  conditions carry M(W+F), LZW, LT and DX in lb and lb-in, so a factor is a true
  statement about them.

  **Owner's ruling, 2026-08-30:** non-loads do not have safety factors. A
  condition with no load value **SHALL** carry `None`, rendered "N/A", and a
  mixed condition keeps its factor while showing N/A against its non-load rows.
  Fixed at the data model, after section 2 closes — filed as **#154** with a body,
  backlog row below. Section 2 prints no safety factor at all, so nothing in the report
  states the false claim in the meantime.
- **The stall boundary is only sampled at its design points.** Drawing the true
  curve between them needs FLTLOADS to sample intermediate speeds, which is
  frozen-module work. Backlogged and **parked with the 8% number** that parks it
  (CLAUDE.md rule 6): below that, the polyline and the true boundary differ by
  less than the base method's own uncertainty at every plotted vertex, because
  the vertices are exact.

### #155 moved from OR-14 to OR-15 (owner, 2026-08-30)

**#155** — the modules describing WINGGEOM's geometry integral as a *strip
integrator* — was first recorded above as an OR-14 finding: filed, not fixed,
because `configuration.py` is frozen. The owner admitted it under **OR-15**
instead, on the reasoning that OR-14 defers defects the report merely *exposes*,
while this one the report's own correction *created*: the closed-form integration
landed in the same milestone and made the surrounding prose false in the same
commit. Leaving it would have shipped a report whose §2.1 reproduces, verbatim, a
description of a method the milestone removed.

Three frozen files carry the fix — `wing_geometry.py` (its module docstring still
taught the strip method its own `surface_properties` no longer uses),
`configuration.py` (the four sites #155 names, one of them the report-visible
note) and `airloads.py` (whose docstring credited its strips to WINGGEOM). The
sweep is CLAUDE.md rule 4: the same false statement was corrected everywhere it
appears, including `models/inputs.py`, three test headers, `PROGRAM_SPEC.md`,
`00_theory_sources.md` and `01_concept_loads_plan.md`. Statements about strips
that remain *true* — AIRLOADS' own span loop, the spanwise load stations,
`tail_geometry`, and every historical reference in the correction register — were
left standing.

Two consequences beyond the prose. The WINGGEOM table's `Integration elements`
row was renamed **`Load stations`** (key `integration_elements` → `load_stations`,
which nothing read): the value is the user's load-station count and had stopped
being an integration parameter. And the Appendix A **aileron oracle was tightened
from ±2 % to ±0.1 %** — it had been loosened only because the result depended on a
strip count the manual never tabulates, and closed-form integration reaches
0.037 %. No load number moves: the Imperial baseline drifts in the
`wing_geometry` and `configuration` channels only, and only in that row label and
that note.

### #153 moved from OR-14 to OR-15 (owner, 2026-08-30)

**#153** — the per-row delete removing the wrong row — was recorded above as an
OR-14 finding: a live defect in `oracle_app/form.py` that the report *exposed*
rather than caused, and therefore one the freeze defers. The owner lifted the
rule for it on 2026-08-30. The reasoning that carried it is the exposure, not the
defect: it was unreachable while every fixture held two surfaces, because
deleting row 2 of 2 removes the last row either way, and **this milestone made it
reachable** by giving `ga6_normal` seven surfaces. What it costs to leave is
silent data loss — the wrong surface goes, with no warning and no undo — on the
Geometry page the section 2 review is conducted from.

**The filed root cause was wrong, and the fix is not where it said.** The filing
blamed `_delete_row`'s `on_click` args binding a list detached by the next run,
so that `del rows[index]` never reached the project. Instrumented, the callback
receives the project's own attached list and the deletion lands every time. What
undid it was the *render* that followed: a row widget keys itself by row index,
Streamlit's retained state outvotes the `value=` seeded from the model, and every
row below the deleted one was renumbered onto its neighbour's state — so the tail
of the table was typed back over itself one place up and the row that visibly
disappeared was the last one. `_retire_renumbered_rows` retires the state of the
rows a deletion renumbers, and only those; a row above the deletion did not move
and keeps an edit typed in the same interaction as the click.

Swept as one class (CLAUDE.md rule 4) rather than fixed in the shape that showed
it. The flat grid is a single `st.data_editor` whose pending edits are an
index-keyed map, so it is renumbered by the same deletion — as are the cached
grid frames of a polyline sitting inside a renumbered row. Both tests now
snapshot whole rows instead of names: the shift moved *values* between rows, and
a name-only snapshot passes while the data has moved, which is how the flat
shape's test passed against a defect it shared. The contract is stated in
`GUI_design.md` beside the counter rule it belongs with.

`oracle_app/form.py` is hash-frozen by OR-13; the manifest hash is updated in the
same commit and the authority named in the commit message.

---

## 11. Iteration 3 — Section 3, Wing Loads (OR-48 … OR-58)

*Agreed with the owner in session, 2026-09-01. Section 3 is the first section that
states a load in force and moment units, so the rulings below are mostly about
which basis a number carries and where it comes from — not about layout.
Content spec per OR-8; SHALL list to `ORACLE_REPORT.md` §3.4; decisions on the
same footing as OR-1 … OR-47.*

| # | Decision | Amends |
|---|---|---|
| **OR-48** | **Section 3 is Wing Loads, built from the `wing_loads` step** (`AIRLOADS+WINGINER+NETLOADS`, primary module `net_loads`), in four subsections: 3.1 the wing input data the loads were run from, 3.2 the run register of cases and their FAR conditions, 3.3 the summary of load cases assessed, 3.4 the load distributions themselves. The per-station numbers go to an appendix, not into the body. | OR-8 (iteration) |
| **OR-49** | **Every load case in section 3 is stated ULTIMATE; input distributions are stated LIMIT; both carry the label.** The load-output contract is not relaxed for the report — a span loading at a target `CL` is an input to the analysis, not a delivered load, so it stays LIMIT and says so, while every shear, bending moment and torsion the section delivers is scaled at the render boundary and marked `-ULT` with its case's factor. **No number in section 3 is printed without a LIMIT or ULT label.** This is where G-OR-4 stops being vacuous: section 2 could hold by carrying no force or moment (OR-44); section 3 holds only by marking every one of them. | OR-44 (extends), G-OR-4 |
| **OR-50** | **The Appendix A input echo takes a reserved slot that renders as an OR-32 "not yet implemented" appendix page.** `APPENDICES` stops being empty. Appendix lettering is derived from position, so shipping Wing Loads into an empty tuple would print it as Appendix A today and silently move it to B when the echo lands — and a signed issue would then disagree with its own reissue. A reserved, stated slot makes **Wing Loads Appendix B from the first build**, and reuses the state machinery a section already has rather than inventing a second way to say "not yet". | OR-32 (applies), OR-35 |
| **OR-51** | **3.1 defines the loads reference axis, and for oracle loads the 25% chord *is* the LRA.** The suite computes about the 25% chord (AIRLOADS/WINGINER/NETLOADS, oracle-locked) and transfers to the surface's entered `ref_axis` at the render boundary; in sloads the LRA is user-defined, so 3.1 states which axis this project's loads are about rather than assuming. It carries **a table of the LRA point (X, Y, Z) against station** and **a planform figure with the LRA drawn on it**. Live in the report's own example: `ga6_normal` enters `ref_axis: 0.4`, so its wing torsion is delivered about the LRA 40% chord with the 25%-chord oracle value beside it — the report must not print one and call it the other. | `CONVENTIONS.md` §1, OR-6 |
| **OR-52** | **3.1's aero input data is the wing span loading and the airplane tail-off / tail-on data.** Span loading is `c*cl` — the span load, **not** the running load in lb/in — plotted at three wing lift coefficients, `CL = 0` (the basic distribution alone), `CL = 1.0`, and `CL = CLmax`, following the oracle's own three-case presentation. `CLmax` is `AeroCoeffSet.stall_cl`, an owner, never a typed constant. The three curves are obtained by **calling AIRLOADS' own `spanwise_distribution` with the target `CL` replaced**; the report never evaluates the additive/basic sum itself, which is what keeps OR-6 true of a figure with three curves the analysis did not run. Tail-off is the entered airplane-less-tail polynomial (`AeroCoeffSet.lift` / `moment`); tail-on is FLTLOADS' balanced per-case result (`wing_cl`, `lift_less_tail_lzw`, `balancing_tail_load_lt`) — the same values, one balanced and one not, which is what makes the tail load visible as a difference. | OR-6, OR-46 |
| **OR-53** | **The flaps-down set is stated absent, never quietly omitted.** The oracle prints two sets of span-load plots, clean and flaps-down. sloads can print the clean set only: `AeroCoefficientsInput.flaps_down` is optional and `ga6_normal` carries none, and AIRLOADS does not model the cosine fairing of the basic distribution across a deflected-flap lift discontinuity — its own documented limitation, since the Appendix A wing has no such discontinuity. So the flaps-down half renders as an ABSENT state with its reason, becoming present the moment a project carries the set, and **the missing span-load capability is filed rather than fixed here** (OR-14,
filed as #163). | OR-5, OR-14 |
| **OR-54** | **3.2 is the run register: what was run, at what condition, under which rule.** One row per selected wing case carrying the case ID, the condition, the FAR reference, the CG case and weight, the speed and altitude, and `Nz`/`Nx`. Every field of it already exists on `CaseRef` and the resolved case — this is a projection of case identity, not a new record of it, which is what OR-41 deferred to this iteration. 3.2 also states the coordinate and sign convention the section's loads are in, citing `CONVENTIONS.md` and naming the torsion axis of OR-51. | OR-41 (discharges) |
| **OR-55** | **SELECT's chosen subset *is* the critical set; 3.3 tabulates it and 3.4 plots all of it.** No second criticality rule is invented for the report — the wing cases the analysis ran are the wing cases the section shows. 3.3 gives root values per case; 3.4 gives one figure per quantity with every selected case on it: **vertical shear `Sz`, bending `Mxx`, torsion `Myy`, and drag shear `Sx`**. ~~Chord bending `Mzz` is omitted.~~ **That omission is SUPERSEDED by OR-72 (design note 47, 2026-09-03):** it rested on `Mzz` being a load nobody reads off a plot, and at the root it exceeds the torsion that does get a figure on four of the five example cases. 3.4 now carries five figures, one per column of B.2. The figures show the **net** loads only, and state that shear, bending and torsion are **summed from tip to root** — a cumulative quantity read as a running one is the misreading the caption exists to prevent. | OR-6 |
| **OR-57** | **The register states where its case list came from.** The suite has two paths to a wing case set: the critical-load selection's own search of the V-n matrix, and a case list entered on the project, which **wins when it is present** (`wing_inertia.resolve_wing_cases`). A section that presents an entered list as the outcome of a search describes an analysis nobody ran, so 3.2 **SHALL** say which it is, **SHALL** state what the matrix it was searched from enumerates — every combination of configuration, weight/CG case, altitude and flight condition, not the twenty conditions a V-n diagram shows — and, where a list is entered, **SHALL** tabulate every condition the selection names with whether it was run. Found in the owner's review of iteration 3, 2026-09-03: the shipped prose claimed selection while `ga6_normal` runs an entered three of the selection's six. An entered list is legitimate and sometimes necessary — an accelerated-roll case carries an unbalanced rolling moment the selection cannot name — but it is the project's list, and the difference is the reader's to see. | OR-46 (extends), OR-54, OR-55 |
| **OR-58** | **The register states the sign convention of its load factors, and says when the set holds no negative-load-factor case.** `Nz` in a wing case is the **inertia** load factor — the negative of the airplane's flight load factor, since the inertia opposes the air load (`wing_inertia._resolve_case`: `Nz = −NZ`) — so a +3.8 g manoeuvre prints as −3.8. Every load factor in the table is a negative number whichever kind of condition it is, so *which* kind cannot be read off the page: 3.2 **SHALL** state the convention, and **SHALL** state, from the analysed set rather than by assertion, whether it contains a negative-load-factor condition. A set of positive-g cases alone does not envelop the wing — 23.333(c)'s negative manoeuvre and negative gust reverse the bending — and a section that leaves that to be worked out from a column of minus signs is not stating what it analysed. Found in the owner's review, 2026-09-03, by misreading exactly this table. The analysis half — that `ga6_normal` runs no negative case at all — is **#165**. | OR-54 (extends) |
| **OR-56** | **Appendix B is the per-station table of the selected wing cases, carrying the increment total load at each station — not the running load.** One row per station per case: the station coordinates, the strip's own increment `Fz` and `Fx`, and the cumulative `Sz`, `Sx`, `Mxx`, `Myy` with its axis named. ULTIMATE per OR-49. `net_loads.wing_load_rows` is already the canonical shape of that row, so the appendix is a view of an existing owner rather than a second layout of the same data. | OR-6, OR-49 |

### Gates added by this section

| Gate | Statement |
|---|---|
| **G-OR-20** | Every load value section 3 or Appendix B prints carries a LIMIT or an ULT label; a value with neither fails the suite. |
| **G-OR-21** | Every delivered shear, bending moment and torsion in section 3 is the ULTIMATE value — the LIMIT value times that case's own stated safety factor — and no input distribution is scaled. |
| **G-OR-22** | Wing Loads is Appendix B in a document whose input echo is not yet built, and the reserved slot renders its state rather than a blank page. |
| **G-OR-23** | Every torsion printed in section 3 names its reference axis, and the axis named is the project's entered LRA. |
| **G-OR-24** | The three span-load curves come from AIRLOADS' own distribution function at three target `CL`s, and the `CLmax` curve's `CL` is the aero set's `stall_cl`. |
| **G-OR-25** | A project with no flaps-down aero set renders the flaps-down figure as ABSENT with a reason, and prints no clean-configuration curve in its place. |
| **G-OR-26** | The cases 3.2, 3.3, 3.4 and Appendix B each state are the same set, in the same order — the selected wing cases, no more and no fewer. |
| **G-OR-27** | 3.2 states which path produced its case list, counts the V-n matrix the selection searched by every dimension it enumerates, and marks each named condition run or not run. |
| **G-OR-28** | 3.2 states what the sign of a load factor means, and says from the analysed set whether it holds a negative-load-factor condition. |

### Amendments made building Section 6 (2026-09-07)

Both were settled with the owner in session before the code was written, on the
same OR-8 footing as the rulings above.

| # | Decision | Amends |
|---|---|---|
| **OR-133a** | **The condition register and the critical-load summary state that the set is short a condition, and name it.** *(Owner, 2026-09-07.)* OR-133's stated scope of the withholding was 6.4 and Appendix E. But OR-133 names **two** unmodelled paths and only one of them is about the loads: the other is about the *condition list*, and on a non-conventional tail 6.2 and 6.3 still render in full — four categories, a four-row summary, and nothing on either page saying a fifth condition is missing. That is OR-61's argument in a new place (a complete-looking table reads as a measured completeness), and it lands on the table an analyst actually stops at, as 5.2's own ordering note concedes. Both tables carry a one-line note **on non-conventional projects only**, pointing at 6.5 and **naming** the case — the horizontal tail's 23.427(a) unsymmetrical load reacted through the vertical tail. Named rather than counted: OR-133's own distinction is that this is an omitted condition and not an understated one, a note saying merely "a condition is missing" makes the reader do work the analysis has already done, and a named case is falsifiable — when note 51's D-51.1 ships there is a specific sentence to delete rather than a hedge to re-litigate. | **OR-133 (extends)**, OR-61 |
| **OR-134a** | **A field the document's content depends on is in the oracle input set, or the document is a function of something it cannot see.** *(Found in implementation, 2026-09-07.)* OR-134 required the `TailType` docstring and the `CONVENTIONS.md` §7 row. Necessary, not sufficient: the document is a function of `reduce_to_oracle_inputs` (**OR-43**), and `geometry.parametric.tail_type` was `SLOADS`-origin and not `supplied`, so the reduction reset it to `CONVENTIONAL` **before the report read it**. OR-133 therefore fired on nothing — every airplane read as a conventional tail, the three shipped T-tails included, and Appendix E printed 40 rows of the loads the ruling withholds on `atr42_100`. The field is `supplied` under `SUPPLIED_RULE`, and because the oracle form builds from the registry (`oracle_app/form.py` reads `oracle_input_paths()`), it renders without touching a frozen file. **Generalised in the same change (rule 4):** the sweep found `geometry.surfaces[].ref_axis_pct` reset the same way — all seven examples enter 40 % of chord, the document stated 25 %, `ga6_normal`'s h-tail root torsion moved **60.8 → 34.5 lb-in**, `concept_regional_jet`'s **4141.7 → 3645.3**, and every Appendix D/E applied-load X sat **3–6 in** off the deck card the appendix claims to be the same load as. That contradicted **OR-51** in as many words (*"the report must not print one and call it the other"*), and the gate written with Section 3 had pinned the defect and explained it in its docstring as a ruling. Both fields are `supplied`; the Section 3 gate reads the axis from the project; and the class gets a **drift guard**, not a prose rule: for every shipped example and both surfaces, the beam the document states its loads about is the beam the analysis ran. | **OR-43**, **OR-51 (restores)**, OR-134, `SUPPLIED_RULE` |

### Findings to file (OR-14 — file, do not fix here)

- **`weight.items[].consumable` is reset by the oracle reduction too.** The
  OR-134a sweep found it: on `concept_regional_jet` the reduction flips one
  item's `consumable` flag, moving the mass and CG and with them the balancing
  case — horizontal-tail root `Fz` **−175.6 → −214.5 lb**. Same class as
  `tail_type` and `ref_axis_pct`, different slice (weight, not geometry), and on
  a fixture the oracle report is not built for. `geometry.parametric
  .fuselage_width`/`.fuselage_height` are reset on the same project. Filed with
  the numbers rather than swept into a document-section change; the drift guard
  names it explicitly rather than exempting it silently.

- **`examples/ga6_normal.project.json` balances at sea level only.**
  `flight_loads.altitudes_ft` is `[0.0]`, so the V-n matrix is 80 points over
  four CG cases, twenty conditions and **one** altitude. Appendix A names five of
  its six critical wing conditions **at 12,000 ft** (`modules/select.py`'s own
  validation list: PLAA MAN D, PMAA GUST +C, NMAA GUST −C, ACRL, TORS). The
  loads still reproduce — these are equivalent-airspeed points and the module's
  oracle tests pass — but every case in the report's own register therefore reads
  `0 ft` where the manual reads 12,000, and the compressibility factor at those
  points is the sea-level one. Raised in the owner's review of iteration 3,
  2026-09-03; **filed as #164**, which also records why adding the altitude is
  not a free change (it renumbers every V-n case).

- **The GA6 wing case set holds no negative-load-factor condition.** The entered
  three (PHAA, TORS, ACRL) are all positive-g, and the selection's **NMAA**
  (23.333(c), V-n point 53, GUST −C at CG3) is one of the three the entered list
  overrides. So the wing distributions do not envelop the wing. A plain deletion
  of the entered list is not the fix: the entered three are the set Appendix A
  prints net loads for, and the entered ACRL carries an `unbal_moment` the
  selection cannot name — so the shape is additive. **Filed as #165**; the
  reporting half is OR-58 and is done.

- **No flaps-down span loading.** AIRLOADS does not fair the basic distribution
  across a deflected-flap lift discontinuity, so the oracle's second set of
  span-load plots cannot be produced for any project. Not a defect in what is
  built — a documented limitation of the ported method — but it is the gap OR-53
  renders as an absence, and the absence should point at a filed item rather than
  at nothing. **Filed 2026-09-01 as #163.**

---

## 12. Appendix B as a structures deck (OR-59 … OR-64)

*Owner rulings 2026-09-03, in session, in the review of iteration 3's Appendix B.
Same footing as OR-1 … OR-58. The ruling that starts them: **the aim of the
Appendix B table is to give the sectional loads to apply to a structures
model.** Everything below follows from taking that literally.*

| # | Decision | Amends |
|---|---|---|
| **OR-59** | **Appendix B is split: B.1 the applied loads, B.2 the loads carried.** They are different quantities and a reader who takes one for the other builds the wrong model, so the distinction is enforced by the table boundary and the heading rather than by a word in a note. B.1 gives, per row, the point the load acts at (`X`, `Y`, `Z`) and the load applied there (`Fz`, `Fx`, `Myy` free) — a deck, self-contained, with no coordinate to fetch from another section. B.2 gives `Sz`, `Sx`, `Mxx`, `Myy` against station: what a model built from B.1 should return. | **OR-56 (supersedes)** |
| **OR-60** | **The applied moment is the *free* moment, never a difference of the cumulative column.** `AIRLOADS` forms `myy = tyy + tvyy + trq`, of which only `trq` accumulates a strip increment; `tyy` and `tvyy` are position transfers of the outboard shear across the bay's sweep and dihedral, which a structural model generates for itself from the geometry. `ΔMyy` and the free moment are not close — at `ga6_normal` PHAA's outboard strip they are −5,313 and +5,917 lb·in, opposite in sign — so applying the difference double-counts the transfer, which is the 20 % error `balance._free_moments` was written to prevent. By the same argument **`Mxx` and `Mzz` have no applied increment at all**: a strip applies forces and a section moment and nothing else. | OR-6 |
| **OR-61** | **`Fy` is not a column, because the wing has no producer for it.** `WingStationLoad.f_span` is the fin's — a v-tail's span is airplane `Z`, so vertical acceleration is an axial column load in its deck — and is `0.0` at every wing station by construction, a wing carrying its spanwise inertia as `fz`. A column of zeros in a deck reads as a measured zero; the absence is stated in the derivation instead. | OR-32 |
| **OR-62** | **Section 3.2 owns the notation and the derivation.** It carries a symbol table — symbol, quantity, units, **and whether the quantity is an applied increment or a cumulative load** — and writes out the recurrences that build `Sz`, `Sx`, `Mxx`, `Myy` from the applied set, naming which terms are position transfers. A column heading anywhere in section 3 or Appendix B names a symbol from that table and nothing else. The prose form this replaces carried the same facts and let the ambiguity through, which is the argument for the table: increment-versus-cumulative is a property of each symbol, and prose that states it for ten symbols at once is prose nobody checks a heading against. | OR-54 (extends) |
| **OR-64** | **The applied set has one owner, in the export channel, and Appendix B.1 is a view of it.** The ruling that opened §12 — the appendix exists to give the sectional loads to a structures model — makes the appendix a *deliverable format*, not a report table, and a deliverable format that only the report can produce is one the analyst has to retype. So `export.sbeam_bridge` gains `applied_load_rows` (the row shape) and `applied_load_csv` (`wing_applied_loads.csv`, ULTIMATE, solver channel), offered on the **Wing Loads** page and in the Export bundle; B.1 consumes the same list and converts at the report's own boundary, exactly as §6 already does for `mass_case_rows` and `balanced_case_rows`. Two assemblers of one load set would be rule 3's failure mode with a deck on the end of it. **Not** extended to `wing_nodal_loads` at the time of writing — **superseded 2026-09-03**: design note 46 (OR-67) does extend it, in this milestone, after the defect was measured at 21–190 % of the root torsion and so outranked the "not inside a report milestone" judgement under `CLAUDE.md` rule 6. | OR-59 |
| **OR-63** | **Every appendix starts a fresh page; Appendix B is landscape throughout.** Back matter is reference material a reader turns to, and an appendix that begins halfway down the last page of the section before it reads as a continuation of it. One orientation per appendix rather than a per-table rule, so the orientation survives a column being added. `Section` gains `page_break` and `landscape`; `pdflscape` joins the shared preamble. | `SUMMARY_REPORT.md` §2 |

### Gates added by this ruling

| Gate | Statement |
|---|---|
| **G-OR-29** | The applied set closes onto the cumulative one: `Fz`, `Fx` and `myy_free` summed tip inboard, with each concentrated mass entering as a point force through the arms its own coordinates state, reproduce the published `Sz`, `Sx`, `Mxx` and `Myy` at every station of every case, on `ga6_normal` **and** on `baron_58`. |
| **G-OR-30** | Every symbol a section 3 or Appendix B column heading uses is defined in 3.2's notation table, with its sense stated. |
| **G-OR-31** | Appendix B renders as two lettered subsections, applied and cumulative, with no load column shared between them. |
| **G-OR-32** | Every concentrated wing mass is a row of B.1 at its own coordinates, carrying zero free moment; the row count is the station count plus the mass count. |
| **G-OR-34** | Appendix B.1's rows and `wing_applied_loads.csv` come from `applied_load_rows` and agree row for row, station label for station label. The applied moment is the free moment and not `ΔMyy`: the two still differ in sign somewhere on `ga6_normal` PHAA, and the free moments plus the applied forces' own arms reproduce the cumulative root `Myy` on both example airplanes. |
| **G-OR-33** | Every appendix sets `page_break`; Appendix B sets `landscape`, and the rendered document opens and closes the environment exactly once. |

### The OR-15 admission of 2026-09-03 (first: the concentrated wing mass)

**Finding.** `WINGINER` adds each concentrated wing mass to the cumulative
shears, bending and torsion of every station inboard of it and leaves the
per-strip `fx`/`fz` panel-only — stated outright at `wing_inertia.py:212-215`.
The mass is therefore published nowhere as an applied load, and an Appendix B
built from the strip table alone is short by the whole of it: on `baron_58` PHAA,
**4,821.5 lb of a 5,004.1 lb root shear**, exactly `nz × ΣW` over the four entered
masses. It is inertia relief, so a model built from the short deck is
unconservative in shear and, with the masses at `y = 57–95 in`, substantially so
in root bending. `ga6_normal` enters no concentrated wing mass, which is why the
closure was exact there and the defect invisible until the Baron ran.

**Why it prevents progress.** OR-15's first row is narrow by design — a wrong
number the report can state accurately is not blocking. This is not that. The
appendix's stated purpose is to be applied to a structures model; a table that
cannot be applied without silently losing most of the inertia relief cannot be
written truthfully around the gap.

**Admitted by the owner in session, 2026-09-03, filed as #166.** Frozen files changed:
`sloads/modules/wing_inertia.py` (publish each mass as a `ConcentratedLoad`),
`sloads/modules/airloads.py` and `sloads/modules/wing_inertia.py` (populate
`WingStationLoad.myy_free`, which the wing chain left `0.0`), and
`sloads/modules/net_loads.py` (sum and transfer both). The manifest is updated in
the same commit per G-OR-9.

**Why `myy_free` had to be published rather than recovered.**
`balance._free_moments` reverses the transfer recurrence from the cumulative
column, which is exact for an air load and **wrong** once a point mass steps the
shear: the step is not a transfer, so it lands in the recovered free moment as a
spurious term. The two owners are guarded against each other on the air loads,
where both are valid.

**No oracle moved.** Every change is additive — a new field, a field that was
`0.0`, a new list — and no cumulative value is touched. The oracle tests and the
Appendix A ±0.1 % gates are unchanged, which is asserted rather than assumed.
`SCHEMA_VERSION` does not bump: `WingLoadResult` is a result, `Project` holds no
field of that type, and nothing on disk has this shape (the `BalancedCaseResult`
precedent in `tests/test_schema_guards.py`).

### The OR-15 admission of 2026-09-03 (second: the notation symbol)

**Finding.** Section 3.3 prints the column heading "Root chord bending Mzz"
while 3.2's notation table defines no `Mzz` — against this standard's own SHALL
that a column heading anywhere in section 3 names a symbol from that table and
nothing else. The guard covered the two appendix tables only, so the rule was
unguarded exactly where it was broken.

**Why it prevents progress.** The document cannot be built truthfully while it
breaks a rule it prints about itself. The guard cannot be widened without the
fix: 3.3's headings are prose built from `LoadValue.label`, and the symbol
cannot be parsed back out of them — `"Root torsion Myy (25% chord)"` does not
end in its symbol, and two different labels carry the same one.

**Admitted by the owner in session, 2026-09-03 (design note 47, D-6).** Frozen
file changed: `sloads/modules/net_loads.py` — the six wing root `LoadValue`s
gain `symbol=`. The manifest is updated in the same commit per G-OR-9.

**No oracle moves.** A defaulted field on a result type and a keyword on six
constructor calls; no value, unit, key or label changes, and
`report.render.results_to_rows` builds its columns explicitly, so no CSV and no
Imperial digest is touched. Full reasoning and the decisions it carries
(OR-71 … OR-75) are in [design note 47](../40_history/47_appendix_b2_chord_bending_note.md).

---

## 13. Iteration 4 — Section 4, Fuselage Loads (OR-94 … OR-102)

**Status: AGREED 2026-09-05 (owner, in session) — SHIPPED 2026-09-06 (#151 iteration 4).** OR-8 agrees a section before
it is built, and iteration 3 is the argument for holding to that: three of its
rulings (OR-57, OR-58, OR-62) were retrofits after the owner read a shipped
section. Ruled in one pass after §14, §15 and §16 were settled, so the section
spec below already reflects them: **OR-94 re-cut to five subsections**, **OR-95
rewritten** under OR-108, **OR-97 amended** by OR-103, and **OR-102 governed** by
§16.
Content spec per OR-8; SHALL list to a new `ORACLE_REPORT.md` §3.5; decisions on
the same footing as OR-1 … OR-93.

*The measurements the recommendations rest on were taken 2026-09-05 against
`examples/ga6_normal.project.json` and `examples/baron_58.project.json` — the two
airplanes G-OR-1 builds — and are quoted where they carry a decision.*

| # | Decision | Amends |
|---|---|---|
| **OR-94** | **Section 4 is Fuselage Loads, built from the `fuselage_loads` step** (`NETLOADS`, Ref 1 Ch 15 p103, primary module `body_loads`), in **five** subsections: 4.1 the fuselage beam the loads were run on, 4.2 the run register of cases and their FAR conditions, 4.3 **Critical Fuselage Loads** — the seven blocks of printed p198 (§15), 4.4 the closure of the beam and the wing-attach fitting loads, 4.5 the distributions themselves. The per-station numbers go to **Appendix C**, not into the body. Five rather than §3's four because §15 gave the section a summary that an analyst turns to first, and folding the manual's own summary into a subsection about closure machinery would make it a footnote to the machinery (owner, 2026-09-05). Adding `"fuselage_loads"` to `oracle_content.IMPLEMENTED` is the switch; the OR-32 placeholder it replaces is the mechanism that has been holding the slot. | OR-8 (iteration) |
| **OR-94a** | **Section 4 delivers LIMIT loads, and OR-49 does not extend to it.** *(Added 2026-09-05, note 49 OR-116/OR-120.)* OR-49 made every §3 load ULTIMATE at the render boundary; that boundary is being removed project-wide, and §4 is new content, so it is built on the final basis rather than written twice. **Every load §4 and Appendix C print is LIMIT, marked as such, with its case's safety factor stated in an `SF` column and applied nowhere.** The two already-ultimate families keep `-ULT` under note 49 OR-118. G-OR-54 inverts with this. | **OR-49 (does not extend)**, note 49 OR-116 |
| **OR-95** | **§4 projects the published `ModuleResult`; the builder is read for the station table only.** *(Rewritten 2026-09-05 under OR-108, which makes `body_loads.run()` publish the four conditions it had been discarding. The original ruling — that §4 read `build_body_loads` throughout because there was no result to project — is superseded; it is rewritten rather than withdrawn so the record shows why it turned over.)* §4's cases, root values and register come from `body_loads`' own `ConditionResult`s, identical in mechanism to §3, which removes a special case from the report and makes the section and the GUI provably show one case set. The **station table and Appendix C still read `build_body_loads`**, because that is where stations live and no result type carries them. The alternative — report and GUI reaching the same case set by two routes — is the drift OR-108 was chosen to prevent. | **OR-108**, OR-6 |
| **OR-96** | **4.1 states the beam, and states where the beam's mass came from.** `fuselage_beam_stations` returns the **mass SSOT's derived** table (step B1) — derived from `weight.items` unless the project explicitly overrides it — and *not* `fuselage_mass.stations` as entered, which is what it read before B1 and which left every fixture's beam lighter than its airplane. A section that presents a derived table as entered input describes a table nobody typed, which is OR-57's finding in a second place. 4.1 **SHALL** state which of the two it is, tabulate station and weight, and print `ΣW` against the airplane's own weight so the reader can see the beam is whole. **In this document it is always the derived table:** `stations_are_override` is `Origin.SLOADS`, so `reduce_to_oracle_inputs` strips it and OR-43's projection forecloses the override branch before the section sees it — 4.1 states the derivation, not a choice between two. Measured on the projected inputs: `ga6_normal` 17 derived stations totalling 3,070.0 lb from 5 entered, `baron_58` 15 from 6. | OR-57 (extends), OR-43 |
| **OR-97** | **4.1 states the carry-through, and 4.4 states that its spar stations were *assumed*.** Measured, and this is the sharpest thing in the iteration: on **both** report fixtures **every** fuselage case runs with `spars_assumed=True` — neither airplane enters `front_spar_pct`/`rear_spar_pct`, so `DEFAULT_FRONT_SPAR_PCT`/`DEFAULT_REAR_SPAR_PCT` (0.15 / 0.65) are substituted, giving `ga6_normal` a carry-through of x = 60.15 → 110.65 in and `baron_58` 74.6 → 116.6 in. 4.3's fitting loads are the sizing loads for the wing-attach fittings, and on every example this report ships they are computed against **assumed** geometry. **And it is not a fixture-data gap — it is structural**: `front_spar_pct`/`rear_spar_pct` are `Origin.SLOADS`, so the oracle GUI never offers them (gate G5's reduced input set) *and* `reduce_to_oracle_inputs` strips them, which I verified by entering 20 %/60 % on `ga6_normal` and watching the projection return the carry-through to the 15 %/65 % default. **Every fuselage fitting load this document can ever print is derived from assumed spar stations**, whatever the project file carries. `CarryThrough.assumed` is already documented as "the provenance flag every deliverable states, so an assumed spar location is never reported as input"; §4 **SHALL** state it beside the fitting-load table itself, in the same visual field as the numbers, and **SHALL** state it as a fact about this airplane rather than about the tool. **Amended the same day by OR-103**: the structural half of this finding is fixed rather than filed — the spar pair becomes an oracle input, the field the reader would go looking for exists, and "assumed" recovers its plain meaning of *nobody entered one*. The measured 15 %/65 % figures above are the pre-OR-104 defaults and are kept as the record of what was found. | `CONVENTIONS.md`, OR-53, OR-43, OR-103 |
| **OR-98** | **A closure-artifact result is stated, never printed as a distribution.** With no carry-through resolvable, `body_distribution` keeps the single wing reaction and cancels the residual moment with a self-equilibrated whole-body correction — its own docstring: *"Closes the beam, invents the source."* `BodyLoadResult.closure_artifact` flags it. A section that prints that station table as a load distribution publishes a load with no physical source and no fitting loads to go with it. 4.5 **SHALL** render an artifact result under its own stated state, by OR-32's gap-state machinery rather than a fourth way of saying it, and **SHALL NOT** print its distribution. Neither report fixture takes that path, so the clause is written from the code rather than from the example — and is therefore guarded on a constructed project, not on `ga6_normal`. | OR-32 (applies), OR-53 |
| **OR-99** | **4.2's register carries OR-57 and OR-58 whole, because §4 has both of their conditions.** Two paths to a case list again: the persisted `envelope.critical` filtered to `component == "fuselage"`, or a fresh `select_fuselage(project)` — so 4.2 **SHALL** say which it was. And OR-58's obligations apply unchanged: the register **SHALL** state the sign convention of its load factors and **SHALL** state, from the analysed set rather than by assertion, whether it contains a negative-load-factor condition. Measured: both fixtures run four conditions — `MAX DOWN LOAD ON WING`, `AFT DOWN BENDING`, `AFT UP BENDING`, `GREATEST NZ`. Those names carry the sense in words, which is exactly the trap OR-58 was written from: a name is not the number, and a reader checking the envelope reads the column. | OR-57, OR-58 (extend) |
| **OR-100** | **The quantities §4 delivers are `Fz`, `Sz` and `Myy`, and the absences are stated in the derivation rather than printed as zero columns.** `BodyStationLoad` carries no lateral shear and no lateral bending: Ch 15 p103 is a symmetric-flight vertical beam solve, and the lateral body case is a different analysis with a different producer. By OR-61's argument — a column of zeros reads as a measured zero — the absence is written out in 4.2's notation and derivation, not tabulated. 4.2's symbol table and recurrences are §3.2's, restricted to the three symbols §4 uses, with `Myy`'s axis named. | OR-61 (applies), OR-62 |
| **OR-101** | **Appendix C is the per-station table, and it is a view of the export owner, not a second assembler.** OR-64's ruling stands unchanged one section over: `sbeam_bridge.body_span_load_csv` and `body_fitting_load_csv` already exist, are already offered by the CLI (`--export-sbeam`) and the Export bundle, and are already the ULTIMATE deliverable `body_load_rows`' own docstring points at. Appendix C consumes those rows and converts at the report's own boundary. `APPENDICES` gains `Appendix(BODY_LOAD_STATIONS, step_key="fuselage_loads", built=True)` in third position — the letter follows position, so Appendix A stays the reserved input echo and Appendix B stays the wing. | OR-64 (applies), OR-50 |
| **OR-102** | **4.4 states the factors it applies, and states that it applies no factor at all.** **Amended 2026-09-05 by note 49 OR-116/OR-120:** the fitting loads are **LIMIT**, like every other delivered load in the project, with the case's safety factor stated beside them and applied nowhere. The `-ULT` marker appears in §4 only if a fuselage case is `engine_ultimate` or `emergency` (note 49 OR-118), which none is. **Ruled by the owner 2026-09-05, and wider than this section: no sloads load carries a Subpart D special factor, ever** — see **§16 (OR-114/OR-115)**, which is the decision of record; 4.3 states its consequence and cites it. This closes review **R-11** as *decided, not fixed*. | OR-49, **§16 (governs)** |

### Gates added by this section

- **G-OR-53** — §4 renders its five subsections numbered by the numbering owner,
  and Fuselage Loads is **Appendix C** behind the reserved A and the wing's B.
- **G-OR-54** — *(inverted 2026-09-05, OR-94a)* every load §4 and Appendix C
  print is **LIMIT**, states its case's safety factor, and carries **no** `-ULT`
  marker — except a case of the two already-ultimate families, which carries it
  and states `SF=1.0`. Asserted in both directions, as note 49 G-OR-51 does
  project-wide.
- **G-OR-55** — 4.1 states the provenance of its beam and prints `ΣW`; a project
  with no beam stations says so and still builds.
- **G-OR-56** — the fitting-load table states `assumed` against `entered` spar
  stations, asserted on a project of each. **Live from OR-103**: the `entered`
  branch is reachable through the oracle GUI and through the projection, so it
  is asserted where the reader meets it rather than only at `carry_through`.
  G-OR-60 pins the projection half.
- **G-OR-57** — a `closure_artifact` result renders its stated state and no
  distribution (constructed project; no shipped fixture reaches this path).
- **G-OR-58** — 4.2 states which of the two paths its case list came from, states
  what the load-factor sign means, and says whether the set holds a
  negative-load-factor condition.
- **G-OR-59** — Appendix C's rows and the `body_span_load_csv` download are one
  load set and agree row for row.

### Findings to file (OR-14 — file, do not fix here)

- ~~**The wing-attach fitting loads in the oracle report are permanently derived
  from assumed spar stations.**~~ **Not filed — fixed, §14.** Found 2026-09-05 by
  entering 20 %/60 % on `ga6_normal` and watching OR-43's projection revert the
  carry-through to the default; put to the owner the same day and ruled fixed in
  this milestone (OR-103 … OR-107). The question it raised — whether a *sizing*
  deliverable may be reachable only from outside the oracle input set — is
  answered *no*, and answered structurally, by the `supplied` mark.
  Related but not the same: `select_input.wing_weight_lb` is `Origin.ORIGINAL`
  and *is* offered, defaulting to `0.09 × MTOW` when left at zero — already
  disclosed on the page (#95, C210-22).

---

## 14. The carry-through becomes an oracle input (OR-103 … OR-107)

> **SUPERSEDED 2026-09-05 by [design note 50](../40_history/50_fuselage_carry_through_note.md)**
> (OR-121 … OR-127), which answers OR-97 by making the carry-through an entered
> **fuselage station** rather than an entered chord fraction. OR-103 and OR-105
> are superseded/withdrawn, OR-104 survives re-cast as the estimator for a blank
> station, OR-106 survives restated, and **OR-107 stands** — the change touches
> no frozen file. Kept unedited below as the record of what was ruled and why it
> turned over.

**Status: AGREED 2026-09-05 (owner, in session) — superseded the same day, see above.** Raised by §13's OR-97 finding
and ruled the same day. Milestone **0.8.2**; closure tier **L** (schema hop, and
the oracle input set is a stated contract — gate G5).

*The owner's instruction: "the carry-through should be added to the geometry GUI
of the oracle. the default can 20%/60% but the user should be able to overwrite."
Four questions were put and ruled, then two of the rulings were superseded by
what the code turned out to already provide — recorded below as taken.*

| # | Decision | Amends |
|---|---|---|
| **OR-103** | **The spar fractions become an oracle input by `supplied=True`, not by reclassifying their origin.** `oracle_app/form.py` builds every page from the registry — *"no field on a page the registry does not put there"* — over `keep = fr.oracle_input_paths()`, which is `ORIGINAL │ supplied`; `reduce_to_oracle_inputs` reduces to the same set. So one mark makes the field render **and** survive OR-43's projection. The mark is earned on `SUPPLIED_RULE` route 2, *demonstrably load-bearing*: dropping the entered value changes a Fuselage Loads result on a shipped example, which is the demonstration G-OR-61 makes. **Origin stays `SLOADS`, and that is the true row** — Ch 15 ships no `.BAS` (the module docstring: "a *suggested procedure* rather than a ported `.BAS` program") and the distributed carry-through is this project's refinement of p103's two point reactions, so `ORIGINAL` would enter a false claim in the table gate G5 is measured against. The two marks are mutually exclusive by guard (`test_a_supplied_field_is_never_original`), so this is a choice, not an addition. **This supersedes the owner's first ruling of 2026-09-05** (`Origin.ORIGINAL`), which was taken against a question that did not offer the supplied route. | OR-97 (discharges) |
| **OR-104** | **The assumed carry-through becomes 20 % / 60 % of root chord**, from 15 % / 65 %. One owner, changed once: `constants.DEFAULT_FRONT_SPAR_PCT` / `DEFAULT_REAR_SPAR_PCT`, so `body_loads` and `export/lra_model` — its only two readers, through `carry_through` — move together and no front-end carries a second default. Measured on `ga6_normal`, front fitting load: `MAX DOWN LOAD ON WING` −1.5 %, `AFT DOWN BENDING` −11.6 %, `AFT UP BENDING` −10.6 %, `GREATEST NZ` −4.2 %; the carry-through moves from x = 60.15–110.65 in to 65.20–105.60 in. **No printed oracle moves** — Ch 15 ships none — so the acceptance is the equilibrium-closure gates the module has always been held to, re-run and stated, per `CLAUDE.md` practice 2. | `constants.py` |
| **OR-105** | **The spar fractions are stored as a percentage (0–100), not a fraction.** They were the only `_pct` leaves in the schema holding a fraction: `weight.envelope.aft_gross_pct_mac` and its siblings hold `30.0`, `front_spar_pct` held `0.15`, and `units._DIMENSIONLESS_RULES` classifies both off the same `_pct$` pattern. The oracle widget renders a stored number raw, so the moment OR-103 made the field visible the oracle GUI would have asked for `0.20` where the main GUI asks for `20` — **one quantity in two scales across two front-ends, and a spar at 2000 % of chord for anyone who typed the number the label implied**. Storing percent removes the trap rather than labelling it: `carry_through` divides by 100 at the one place it reads them, the main GUI's ×100 goes, and the suffix stops lying. Schema **v60 → v61**, `_hop_60` multiplying an entered value by 100. No shipped fixture data moves — all seven examples write both keys as `null`. | `units.py` §`_pct`, schema |
| **OR-106** | **`None` still means assumed, and the widget stays blank.** The provenance flag is `CarryThrough.assumed`, driven by the field being unset; a widget pre-filled with the default would make every deliverable claim its fitting loads were sized on entered geometry when the user only accepted a default. No new state and no schema field are needed for this: the oracle form already renders an unfilled `Optional` **empty**, not as a fake 0 (#35, CR-A-3), with a placeholder and a clear button, so accepting the default is not recorded as an entry. The default is disclosed in the field's registry `basis`, which is the widget's help text. | #35/CR-A-3 |
| **OR-107** | **No frozen file is edited, so OR-13's freeze is not engaged and OR-15 is not invoked.** The owner granted an OR-15 admission for this work on 2026-09-05; it turned out not to be needed, and is recorded as unused rather than quietly spent. The frozen set is `sloads/modules/**` and `oracle_app/`'s five pages; this change touches `field_registry.py`, `constants.py`, `derived_geometry.py`, `io.py`, `migrations.py`, `units.py` and `app/views/` — none of them frozen — and the oracle GUI gains the field **without an edit** because its pages are registry-built. `tests/test_frozen_set.py`'s manifest is therefore unchanged and G-OR-9 does not apply. **This supersedes the owner's fourth ruling of 2026-09-05.** | OR-13, OR-15 (neither engaged) |

### Gates added by this ruling

- **G-OR-60** — the spar pair is in `oracle_input_paths()` and survives
  `reduce_to_oracle_inputs`: a project entering 25 %/55 % reports 25 %/55 % in
  the oracle report, not the default. This is the assertion OR-97's finding
  turned on, run from the other side.
- **G-OR-61** — the **G5 demonstration** that earns the supplied mark: dropping
  the entered spar fractions changes a Fuselage Loads result on a shipped
  example. Without this the mark is speculative, which `SUPPLIED_RULE` forbids.
- **G-OR-62** — `CarryThrough.assumed` is True exactly when the field is unset,
  asserted **through the projection** as well as on the raw project, so a future
  reducer change cannot silently turn an entered station into an assumed one.
- **G-OR-63** — the percent hop: a v60 file carrying `0.15`/`0.65` loads as
  `15.0`/`65.0` and reproduces its pre-hop carry-through stations exactly, so
  the hop is a representation change and not a geometry change.

---

## 15. The critical fuselage summary (OR-108 … OR-113)

**Status: AGREED 2026-09-05 (owner, in session) — SHIPPED 2026-09-06 (#151 iteration 4).** Raised by the owner reading
printed **p198, `CRITICAL FUSELAGE LOADS`**, against the Fuselage Loads page.
Milestone **0.8.2**; closure tier **L**. Carries an **OR-15 admission** over two
frozen files.

**The finding.** The manual prints a seven-block critical-fuselage summary.
`select_fuselage` already computes four of those blocks — labels, FAR references,
V-n case numbers and the same three quantities each — and then
`body_loads.run()` returns `ModuleResult(conditions=[])`, so every one of them is
discarded. The oracle GUI's Fuselage Loads page renders, verbatim,
*"Body Loads produced no conditions."* beside a 92-row station table, where the
manual prints its summary. Every other component page shows its critical cases.

| p198 block | sloads today | After this note |
|---|---|---|
| 1 MAXIMUM TOTAL FUSELAGE LOAD ACTING DOWN ON WING | `MAX DOWN LOAD ON WING` (23.301) — computed, discarded | published |
| 2 MAXIMUM AFT FUSELAGE DOWN BENDING | `AFT DOWN BENDING` (23.331) — computed, discarded | published |
| 3 MAXIMUM AFT FUSELAGE UP BENDING | `AFT UP BENDING` (23.331) — computed, discarded | published |
| 4 UNCHECKED PULL UP MANEUVER | absent from the page | published, referred |
| 5 CHECKED PULL UP MANEUVER | absent from the page | published, referred |
| 6 LANDING CONDITIONS (advisory) | absent | stated |
| 7 GREATEST VERTICAL INERTIA FACTOR | `GREATEST NZ` — computed, discarded | published |

| # | Decision | Amends |
|---|---|---|
| **OR-108** | **`body_loads.run()` returns the four conditions it already builds.** One owner, not four: the same `ModuleResult` then feeds the oracle GUI, the main GUI, the CLI, `load_cases_csv` and report §4 through renderers that are already generic — `oracle_app/results.py` needs no edit to show them. The alternative considered and rejected was each surface calling `select_fuselage` for itself, which is rule 3's failure mode with a deliverable on the end of it. **OR-15 admission, granted by the owner 2026-09-05**, over `sloads/modules/body_loads.py`: additive, no value changes, nothing recomputed. Manifest updated in the same commit per G-OR-9. **This supersedes OR-95**, which recorded the empty result as "not a defect" — reading the builder for the *station table* stays right; discarding the *case summary* was the defect. | **OR-95 (supersedes)** |
| **OR-109** | **All seven blocks are reproduced, and a number that also appears elsewhere carries its reference.** The manual's own device — *"SEE HORIZONTAL TAIL LOADS FOR FURTHER DATA"* — is the answer to the two-pages-one-number objection: the reader gets the value where the fuselage question is asked, and is told where it is derived. Blocks 4 and 5 therefore print their tail-load quantities on the fuselage page **with a stated reference to the Tail Loads section**, and the values are **read from SELECT's own htail conditions**, never reassembled, so the two pages cannot drift. Owner ruling 2026-09-05. | OR-6 |
| **OR-110** | **Weight and CG are case identity, so blocks 4 and 5 state them by lookup, not by calculation.** `CaseRef.cg` names the case; `cg_cases` resolves it to `weight_lb` and `xcg`. This is OR-54's projection-of-case-identity argument one section over, and it is exact: `CG4 → 73.09 in` and `CG3 → 72.64 in` reproduce p198's printed `XCG` values to the digit. The case ID is stated alongside, so a reader who wants the rest of the case finds it in the SELECT output rather than having it re-tabulated. Owner ruling 2026-09-05: *"the weight and cg are part of the case … these could be repeated here or just the cases stated."* Both — repeated for the reader, with the case named. | OR-54 (extends) |
| **OR-111** | **The unbalanced moment about the CG is published from SELECT, with its equation recovered from the source and cited.** It was the one field of p198 with no owner and no derivation this project could state, and it is **not** reconstructible from the printed page by inspection — the arm closes against neither the 25 % nor the 50 % MAC until the balanced elevator load is subtracted. Recovered from Appendix C (`reference/code.txt` line 5210): `PITCHMOMH5CASE = -(LT50UPTEUNCK - LT50) * (XT50 - XXCG(H5CASE))`, and for the checked cases `PITCHMOMH7CASE = L5T * (XT50 - XXCG(I))`. **The increment is measured from the balanced 50 %-chord load, and the arm runs from the CG to the 50 % tail MAC.** Verified against the printed page on both: unchecked `-(-1346.496 - (-113.6319)) × (270.357 - 73.09) = +243,203.9` against a printed `243203.5`; checked `-218.3436 × (270.357 - 72.64) = -43,169.9` against a printed `-43170.23`. The **sign asymmetry is the original's** — the unchecked expression negates and the checked one does not — and is ported as found, not tidied. Cited in `theory_sources.md` with the line number. Second **OR-15 admission**, over `sloads/modules/select.py`. | `theory_sources.md` |
| **OR-112** | **`FS 50 PERCENT HORIZ TAIL` prints the real station, and the deviation is registered.** The manual prints `0` in both fuselage blocks while its own tail-loads input echo states `270.357`, and `tail_loads.xt50` holds `270.357`. OR-111's arithmetic settles it independently: the moment closes **only** with 270.357, so the original computed with the real station and printed zero — a defect in its print, not a modelling choice. sloads prints the real value and records the difference in `02_approved_corrections.md`, so an analyst comparing against the page finds it explained rather than discovering it. Owner ruling 2026-09-05. | `02_approved_corrections.md` |
| **OR-113a** | **The summary's loads are LIMIT, and each block states the factor it does not apply.** *(Added 2026-09-05, note 49 OR-116.)* p198's blocks are load quantities, so they follow the project basis. This also removes a trap the ULTIMATE basis would have created here: the manual's own p198 figures are **limit** loads, so a reader comparing our summary against the printed page would have been comparing 1.5x against 1x — exactly the defect note 49 E-c found in section 3's tables. | note 49 OR-116 |
| **OR-113** | **Block 7's pitching-acceleration advisory is carried, because it names a limitation this project still has.** The manual warns that *"pitching acceleration will add algebraically to vertical inertia at all fus stations"*. sloads models the linear half of p103's "linear and pitching load factors" and **not** the pitching half — that is **M4-21**, open, with `theta_ddot = 0` on the balanced trim cases these conditions come from. Reproducing the manual's advisory therefore states a true limitation of the delivered numbers rather than decorating them, which is the one good reason to carry advisory prose at all. Block 6's landing advisory is carried on the same footing, referring to Landing Gear Loads. | M4-21 |

### Gates added by this ruling

- **G-OR-64** — `body_loads.run()` publishes one condition per block 1/2/3/7, each
  carrying its FAR reference and its V-n case number, on both report fixtures.
- **G-OR-65** — the oracle GUI's Fuselage Loads page renders those conditions:
  the string *"produced no conditions"* never appears for `body_loads` on a
  project that has an envelope. The regression this closes, asserted by its
  symptom.
- **G-OR-66** — blocks 4 and 5 read their tail-load values from SELECT's htail
  conditions: the fuselage page and the tail page print the same number for the
  same quantity, asserted by comparison rather than by both matching a literal.
- **G-OR-67** — the unbalanced moment reproduces the printed page within the
  oracle tolerance on both the unchecked and the checked case (OR-111's two
  reconstructions are the test's cited numbers), and the 50 % tail MAC station it
  uses is the entered one, never zero.
- **G-OR-68** — every repeated quantity on the fuselage page carries its
  reference to the section that derives it (OR-109), and every stated advisory
  names the open item or the section behind it (OR-113).

---

## 16. Special factors are stress's, not loads' (OR-114 … OR-115)

**Status: AGREED 2026-09-05 (owner, in session).** Owner directive, verbatim:
*"the external loads report should NOT add fitting factors. this is applied by
stress. NO load in sloads should have the 23.625 fitting factor, or any of the
other special factors 23.619 such as bearing factor 23.623 and casting factor
23.621."* Raised settling §13's OR-102; ruled wider than the section that raised
it. Milestone **0.8.2**; closure tier **M**.

**This is not a change — it is a boundary being made structural before something
drifts across it.** Measured 2026-09-05: no path in `sloads/`, `app/`,
`oracle_app/` or `cli.py` mentions or applies a fitting, casting, bearing or
other special factor, and the governing table `sloads/safety_factors.py` carries
no Subpart D row. The 2026-09-04 review's R-11 says the same from the other side.
What is missing is not the behaviour but the **statement plus its guard**, which
is what `CLAUDE.md` practice 3 requires of any cross-cutting convention.

| # | Decision | Amends |
|---|---|---|
| **OR-114** | **sloads delivers external loads; the special factors of 14 CFR 23 Subpart D are applied by stress and by no part of this project.** Named and excluded: **23.619** special factors, **23.621** casting factor, **23.623** bearing factor, **23.625** fitting factors — and the class, not only the list, so a hinge or a seat-track factor arriving later is excluded by the same rule rather than needing a new one. The reason is a division of responsibility, not a tolerance: a special factor is a property of a *part* — its material, its process, its joint — and none of those is an input to a loads analysis. A loads program that applied one would be sizing, and would be doing it with information it does not have. The `-ULT` contract is unchanged: a delivered load is limit × the governing safety factor, and **nothing else**. | `CONVENTIONS.md` §3 |
| **OR-115** | **One owner, one statement, one guard.** The rule lives with the governing safety-factor table (`sloads/safety_factors.py`, the M4-8/G-11 owner), because that is the single source for what multiplies a load and this is a statement about what does not. `CONVENTIONS.md` §3 states the boundary; the shipped **methods statement** states it to the reader, which is where an analyst meets it — so it rides with **#174** (the methods-statement catch-up, already a 0.8.2 row) rather than being a second edit to the same sentence. Registered in `02_approved_corrections.md` **§Withdrawn from scope**, following the 23.629 flutter precedent exactly (#79, C210-19). | `safety_factors.py`, #174 |

### Gates added by this ruling

- **G-OR-69** — no shipped module, report or export path applies a Subpart D
  special factor, asserted as the flutter withdrawal is asserted
  (`test_no_shipped_module_computes_a_flutter_clearance_speed` is the pattern):
  a scan over the safety-factor owner's rows plus every applied factor,
  failing on any value that is not the governing table's own.
- **G-OR-70** — the shipped methods statement says so, checked against
  `02_approved_corrections.md` §Withdrawn from scope rather than against its own
  source tuple — the circularity #174 exists to fix, so the new clause is not
  added behind the same blind guard.

---

## 17. Iteration 5 — Sections 5 and 6, Tail Loads (OR-128 … OR-138)

**Status: AGREED 2026-09-06 (owner, in session).** Four of the rulings below were
settled with the owner in session on 2026-09-06 before this note was drafted
(**OR-128** the two-section split, **OR-132** the control-surface loads,
**OR-133**/**OR-134** the non-conventional tail, **OR-138** the naming); the rest are
put here for the same pass. OR-8 agrees a section before it is built.

*Measurements taken 2026-09-06 against `examples/ga6_normal.project.json` and
`examples/baron_58.project.json` — the two airplanes G-OR-1 builds — and quoted where
they carry a decision. Both fixtures run **nine** horizontal-tail conditions and
**four** vertical-tail conditions, with identical labels and FAR references on each.*

*One premise of the first draft was wrong and is corrected in place rather than
quietly: the tail is **one** oracle step, not two (OR-129, OR-130a). `tail_span_loads`
is a modern deliverable with no `.BAS`, outside `oracle_steps()` and outside the oracle
GUI's page set. The agreed section shape is unaffected; the spanwise loads enter as
appendix content on the Appendix B precedent instead of as a second derived step.*

| # | Decision | Amends |
|---|---|---|
| **OR-128** | **The tail is two sections, not one: Section 5 Horizontal Tail and Elevator Loads, Section 6 Vertical Tail and Rudder Loads.** *(Owner, 2026-09-06.)* The alternative — one grouped section with the two workflow steps as its subsections — forces **method-major** numbering (5.1 Chordwise, 5.2 Spanwise), because `oracle_content.section_plan` prints exactly one numbered subsection per member step. An analyst reads by surface: the h-tail's totals, its chordwise profile and its span loads are one story, and the fin's are another. Splitting by surface makes each section a whole story and needs no third heading level. Everything below renumbers — aileron 7, flap 8, tab 9, engine mount 10, one engine inoperative 11, landing gear 12 — which is free, because `section_number` derives from position and no cross-reference is ever written as a literal (OR-2). | OR-8 (iteration), OR-38 |
| **OR-129** | **G-OR-2 is amended: a result-producing step may fan out into sections by a declared partition.** OR-128 puts one step across two sections, so the existing one-step-one-section mapping cannot express it. The rule becomes: every result-producing step is covered by exactly one declared partition of sections, and every analysis section names the step and the component it is built from — guarded **totally in both directions**, so a published condition that lands in no section, or in two, fails the suite. That is a stronger gate than the positional one it replaces, which could only count. The partition key is `component`, already a field on `TailChordResult` and `TailSpanResult`; no new concept. **Corrected 2026-09-06, before implementation:** the drafted text said the partition ran over *two* steps, `tail_loads` and `tail_span_loads`. It does not. `tail_span_loads` carries `bas=None` and produces no slice a `.BAS` step requires, so `workflow.oracle_steps()` excludes it — it is not an oracle GUI page and it is not an analysis section. **The partition is over `tail_loads` alone.** The correction makes the amendment smaller, not larger, and the section shape OR-128/OR-130 agreed is unchanged; what it changes is where the spanwise loads come from, which is OR-130a. | **G-OR-2 (amended)**, OR-2 |
| **OR-130a** | **The spanwise tail loads are appendix content read from a non-step producer, exactly as the wing's are.** *(Added 2026-09-06 with OR-129's correction.)* Since `tail_span_loads` is not an oracle step, 5.4/6.4 cannot be a section derived from it. They do not need to be: the wing already has this shape. §3.2 owns the notation and the recurrences while the station-by-station numbers live in **Appendix B**, which OR-59 ruled is a *deliverable format* — "the sectional loads to apply to a structures model" — and OR-64 made a **view of the export owner** rather than a report table. 5.4 and 6.4 are the same: a short subsection owning the notation, the beam it is run on and the closure that stands in for the absent oracle, with the per-station table in Appendix D/E as a view of `sbeam_bridge`'s own rows. The builder reads `tail_span.build_tail_span` directly, which is OR-95's ruling one section over (§4 projects the published result and reads the builder for stations alone). **This is also why the oracle scope is not breached:** Section 5 is derived from `tail_loads`, and the modern spanwise deliverable enters as back matter on the Appendix B precedent, not as a derived section claiming a program that does not exist. | **OR-59/OR-64 (precedent)**, OR-95, OR-130 |
| **OR-130** | **Four subsections each, mirrored.** 5.1 / 6.1 the critical conditions and how they were selected; 5.2 / 6.2 the critical-case summary table; 5.3 / 6.3 the chordwise distribution and its figures; 5.4 / 6.4 the spanwise loads. Per-station numbers go to the appendices (OR-136), not the body. The mirror is deliberate: the two surfaces are analysed by the same machinery in the same order, and a reader who has read Section 5 knows where to look in Section 6. | OR-94 (shape precedent) |
| **OR-131** | **Each section states the selection method in its own terms, and neither cross-references the other for it.** The candidate pool for both is the entire balanced V-n matrix, filtered by condition label, with `extreme()` returning one governing case per category (`theory_sources.md` §`select`, C210-26); 23.333(b)'s "each combination" is discharged by FLTLOADS balancing the full matrix. But the **categories differ** — nine for the h-tail (balancing up/down 23.421, unchecked maneuver up/down 23.423(a)(1)/(2), checked up/down 23.423(b), gust up/down 23.425(a)(1), unsymmetrical 23.427(a)) against four for the fin (23.441(a)(1)/(2)/(3), 23.443(b)) — and a reader carrying one section's category list into the other reads a different airplane. This is OR-58's argument applied to a method rather than a sign convention. | OR-58 (extends) |
| **OR-132** | **Every tail condition states the load carried by its control surface (third OR-15 admission, over `sloads/modules/select.py`).** *(Owner, 2026-09-06.)* Measured: `elevator_load` is published on **2 of 9** h-tail conditions — the two unchecked maneuvers — and `load_on_rudder` on **2 of 4** fin conditions. 5.2's and 6.2's whole purpose is one table a reader reads across, and as it stands the control-surface column would be blank on **seven** h-tail rows and two fin rows for no reason the analysis can state: `select.elevator_load(lt50, lt25, ti)` and `select.rudder_load_parts(lrud, lyaw, vt)` are pure functions of the split every one of those conditions already carries. Publishing them is additive — one `LoadValue` per condition, no existing value moves — and the frozen manifest is updated in the same commit per G-OR-9. **`UNSYMMETRICAL` (23.427(a)) states one too, with the RH/LH split beside it** (owner, 2026-09-06). Its total is a scaled version of the governing case and the elevator share scales with it, so the value is real; the risk is that an elevator load quoted for an unsymmetrical case reads as one surface's load, when the case's whole content is that the two sides differ. Adjacency answers it — the split is what stops the number being read as a single surface's, so the two are printed together and never in separate tables. **No `select.py` change is needed for the split half:** the condition already publishes `rh_side_load`, `lh_side_load` and `other_side_percent` (measured `−700.29` / `−504.21` / `72 %` on `ga6_normal`), so OR-135's obligation there is a rendering one, satisfied by projection. Only the elevator load is published. | **OR-15** (admission), M4-9 |
| **OR-133** | **Non-conventional tail arrangements are not supported, the report says so, and it withholds the vertical tail's spanwise loads rather than printing them.** *(Owner, 2026-09-06.)* sloads analyses the empennage as a conventional tail: a horizontal and a vertical surface each carried by the fuselage and each loaded independently. In any other arrangement the vertical tail is additionally the *supporting structure* of the horizontal tail in the sense of 14 CFR **23.427(a)**, and two load paths that creates are not modelled — the h-tail's unsymmetrical case is never reacted through the fin, so the fin's critical-case set **omits a condition** rather than understating one; and the four fin conditions transfer a **symmetric** h-tail set in precisely the cases where sideslip and rudder deflection load the horizontal surface asymmetrically. Both are quantified in **design note 51** (AGREED 2026-09-06), whose D-51.3 measures the induced rolling moment at **27–73 %** of the governing fin case's own root bending on `concept_regional_jet`. **Scope of the withholding is the report only** (owner, 2026-09-06): 6.4 and Appendix E render the OR-32 stated state and no table, while the calc, the decks, the CLI and the GUI are untouched — `build_tail_span`'s v-tail results are what the balanced deck's lateral cases close `ΣFy = 0 → n_y = L_v/W` against, and withholding them there would stop the lateral cases assembling on all three T-tail fixtures, i.e. would break the mission deliverable to document a limitation in it. **What is *not* affected, stated positively:** the vertical tail's chordwise pressure distribution (6.3) is unaffected — it distributes the surface's own total across its chord and is indifferent to what the fin carries above it — and the horizontal tail's own loads and distributions (Section 5 entire) are unaffected. | OR-32 (mechanism), **note 51** |
| **OR-134** | **`TailType` stops being a layout-sketch distinction.** Its docstring says today: *"a layout sketch distinction only, not a structural classification."* OR-133 makes the field decide whether a deliverable is printed, so that sentence becomes false the moment OR-133 ships, and a field whose meaning has quietly changed is the defect class this milestone has now hit twice (the fin waterline, §160). The docstring and the `CONVENTIONS.md` §7 SSOT table **SHALL** be corrected in the same change, naming the report as a consumer. **Any value other than `CONVENTIONAL` triggers OR-133** (owner, 2026-09-06) — `T_TAIL`, `V_TAIL` and `CRUCIFORM` alike: a cruciform fin carries the same horizontal-tail reaction, and a V-tail has no separable vertical surface for the analysis to be about. Only `T_TAIL` is exercised by a fixture (`atr42_100`, `dhc8_dash8`, `concept_regional_jet`), so the other two are guarded on constructed projects. | `CONVENTIONS.md` §7 |
| **OR-135** | **A quantity whose provenance changes the number is stated beside it.** Three in this iteration, all following OR-97's ruling that provenance belongs in the same visual field as the value: 6.2's `SIDE GUST` row states whether its yaw inertia `IZZ` was **entered or rod-estimated** (C210-25 measured the rod estimate **+49 %** over WTONECG's database value on the C210, with nothing on the page saying an estimate was in play — `select.default_side_gust_izz` is the owner); 5.2's `UNSYMMETRICAL` row states its **RH/LH split**, because the case's own total is not a load anything is sized to; and 5.2's checked-maneuver pair states the **pitch inertia `Iyy`** it was computed with. | OR-97 (extends) |
| **OR-136** | **Two appendices, D and E, lettered by position.** Appendix D is the horizontal tail station by station, Appendix E the vertical tail, each **inheriting its section's state** by the OR-50 mechanism that already letters A–C. Two rather than one because OR-128 made two sections and an appendix that served both would have no section to inherit from — and because Appendix E is exactly what OR-133 withholds on a non-conventional tail, which a shared appendix could only express by going half empty. Both are views of `sbeam_bridge`'s own rows, not second assemblers (OR-64/OR-101 one section further on). | OR-50, OR-64, OR-101 |
| **OR-137** | **5.1 states the 23.427(a) oracle deviation where the case is introduced.** M1-4 (approved 2026-07-20): `SELECT.BAS` 6070–6175 includes the unchecked maneuvers in the unsymmetrical candidate array and the printed Appendix A sample output does not, so sloads selects the DN unchecked maneuver and prints **−1204.7** (RH −700.4, LH −504.3, 72 %) where the page prints −1111.8. The listing and the CFR are authoritative; the register carries it and the methods statement declares it. 5.1 states it in words at the point the case is introduced, so an analyst comparing against the page finds it explained rather than discovering it — OR-112's treatment one section over. | `02_approved_corrections.md` |
| **OR-138** | **The surface is the vertical tail; "fin" is retired.** *(Owner, 2026-09-06.)* "v-tail" where space requires, `vtail` as the code token — matching 23.441/23.443, the schema, the component key and what the reports already print. Stated in `CONVENTIONS.md` §7.2. Sections 5 and 6 take the agreed name from the first line; the identifier sweep (`fin_root`, `FinRoot`, `fin_tip`, `fin_load`, …) is filed for the 0.8.2 cut, since it reaches frozen `modules/tail_span.py`. | `CONVENTIONS.md` §7.2 |

### Gates added by this iteration

- **G-OR-80** — Sections 5 and 6 each render **five** subsections numbered by the
  numbering owner (*amended 2026-09-07*: OR-130 agreed four, and the owner's
  review added the input-data subsection to both; the mirror carried it into
  Section 6 at no cost, which is the argument for one builder demonstrated); the tail appendices are **D** and **E** behind A, B and C; and
  every section below the tail carries the number its position gives it.
- **G-OR-81** — *(OR-129, the partition gate)* every condition published by
  `taildist` and `tail_span` appears in **exactly one** section, and every tail
  section names the step and component it was built from. Asserted in both
  directions on both fixtures, so a dropped condition and a duplicated one each
  fail.
- **G-OR-82** — every load Sections 5 and 6 and Appendices D and E print is
  **LIMIT**, states its case's safety factor in an `SF` column, and carries no
  `-ULT` marker. Asserted in both directions (note 49 G-OR-51, as G-OR-54 does
  for §4).
- **G-OR-83** — the printed totals are the module's own unscaled values, matched
  through the content model rather than against a literal, against the Appendix A
  oracles: h-tail balancing **+519.85 / −613.92**, unchecked **−1397.8 / +1227.2**,
  checked **−671.5 / +787.8**, gust **+908.6 / −1292.8**, unsymmetrical **−1204.7**
  (OR-137); fin **+591** (rudder 167), **−92**, **−526**, **+604** (`IZZ` 4169.164).
  Tolerances are `test_select.py`'s own — the report cites them, it does not
  re-derive them.
- **G-OR-84** — 5.3 and 6.3 reproduce the chordwise oracle: p237 cond 1
  `LT25 +907.62 / LT50 −387.77 → 0.682 / 0.095 / 0 / 0.015 / −0.030` and p245
  cond 1 `LT50 679 → 0 / 0.370 / 0 / 0.462 / 0.462`, ±0.1 %; the component
  constants (`AHT`; `AVT` + `EFFECTV`) print **once per section** and are rendered
  as reference data, never as a load case.
- **G-OR-85** — every distributed case states its aero state or its fixed AS-4
  reason, never a blank (note 35 G-AS-3, carried into the document).
- **G-OR-86** — *(OR-132)* every h-tail condition states an elevator load and
  every vertical-tail condition a rudder load, so neither summary table has a
  blank in that column on either fixture.
- **G-OR-87** — *(OR-133/OR-134)* on a non-conventional tail, 6.4 and Appendix E
  render the stated state and no table, the limitation is stated in full in
  Section 6 and pointed at from Section 5, and **Section 5, 6.3 and Appendix D are
  unchanged** — asserted by building the same project as `CONVENTIONAL` and as
  `T_TAIL` and diffing. Run for `V_TAIL` and `CRUCIFORM` on constructed projects.
  Its companion: `build_tail_span` still returns the v-tail results, and the
  balanced deck still assembles its lateral cases, on all three T-tail fixtures —
  the gate that the withholding stayed inside the report.
- **G-OR-88** — 6.2 states whether `IZZ` was entered or estimated, and 5.2 states
  the RH/LH split and the checked pair's `Iyy` (OR-135). The unsymmetrical row's
  elevator load and its RH/LH split are asserted **adjacent** — same table, same
  row — because adjacency is the whole of OR-132's answer there, and a gate that
  only checked both were present somewhere would pass the arrangement the ruling
  rejects.

### Findings to file (OR-14 — file, do not fix here)

- **The T-tail transfer pairs the *balancing* tail load.** Note 51 §1 records that
  `ttail_transfer` pairs each fin case with the balancing h-tail load at that
  case's own V-n point — on `concept_regional_jet` a **+6 lb** load against a
  **7–8 klb** fin load. OR-133 states the consequence for the vertical tail;
  whether the same pairing assumption reaches Section 5's h-tail span subsection
  is **to be checked before 5.4 is written**, and filed rather than fixed if it
  does. Note 51's D-51.1 is the fix and it is a separate step.

## 18. The applied appendices are one deck in one frame (OR-139 … OR-146)

*Owner ruling 2026-09-07, in session, from the review of Appendices B, C, D and
E. The ruling that starts them: **every appendix that gives an applied load gives
the same thing in the same frame — the case, the point it acts at, all six
components, and the factor.** Everything below follows from taking that
literally, and §12's opening ruling (the appendix exists to give the sectional
loads to a structures model) is what makes it binding rather than tidy.*

Reviewing the proposal found that two of the four appendices are **wrong today**,
not merely inconsistent, so this section carries a defect (OR-143) as well as a
format. Under `CLAUDE.md` rule 6 the defect outranks the consistency work; the
owner's ruling is that they close as one step, because the single-owner change
(OR-141/OR-142) is the fix that stops the defect recurring.

| # | Decision | Amends |
|---|---|---|
| **OR-139** | **One column set for every applied appendix.** `Case`, `GID`, `X`, `Y`, `Z`, `Fx`, `Fy`, `Fz`, `Mx`, `My`, `Mz`, `SF` — the point in airplane axes, the load right-handed about CID 0 at that point, and the factor the case prescribes and nothing applies. B.1 (wing), C.1 (fuselage), D (h-tail) and E (v-tail) all print it. B.1 already prints eleven of the twelve and omits **`SF`**, alone among the four, in the one appendix a reader is likeliest to lift rows from; D and E omit `GID`'s companion columns entirely. A reader who has learnt one appendix has learnt all four. | OR-59, OR-61 |
| **OR-140** | **The structural zeros are printed, and the note names the producer each is missing.** OR-61 omitted `Fy` from B.1 because "a column of zeros in a deck reads as a measured zero". That reasoning is sound and its remedy was the wrong one for an appendix that is a deck: a consumer writing FORCE/MOMENT cards needs the whole vector, and the export channel already ruled the other way for the same data — `_APPLIED_CSV_CONVENTIONS` states the structural zeros "so a consumer writing cards cannot read a printed zero as an omission" (OR-65). Today B.1 prints six components and explains the zeros while D and E omit them and explain the omission: **two policies for one question, one chapter apart**. The report does not take a position its own deck contradicts. | **OR-61 (supersedes)**, OR-65 |
| **OR-141** | **The applied set has one row shape for the whole airframe.** `AppliedLoad` gains `component`, and `applied_load_rows` gains a producer per component — wing strips and concentrated masses (as now), fuselage stations, h-tail strips, v-tail strips, each surface's discrete control-surface nodes and the T-tail transfer node. Every appendix and every applied CSV is a view of that one list. OR-64 ruled this for the wing on the argument that a deliverable format only the report can produce is one the analyst has to retype; the same argument covers the other three, and the divergence OR-143 records is what happens when it is not extended. | OR-64 (extends) |
| **OR-142** | **The beam-frame → body-axis moment map is one function and it is component-aware.** `applied_body_moments` returns `(mx, myy_free, mz)` for every row. That is right for the wing and the h-tail, whose span is `y`, and **wrong for the fin**, whose span is `z`: its torsion is `Mz`, and negated. `export.coordinates.tail_torsion_to_airplane` already owns that map with the sign derived rather than asserted, and the exported deck already calls it — the report is the consumer that does not. One owner, every consumer. | OR-60 |
| **OR-143** | **Appendices D and E do not carry every applied load the deck emits, and say they do.** Both state "a row here and the card that carries it are the same load". Per station the deck writes a `MOMENT` card from the strip torsion and folds the span-axis axial into the `FORCE` card; the appendix prints one force column. First case, summed over stations: h-tail applied torsion **6,689 lb-in** on `ga6_normal` and **232,139** on `concept_regional_jet`; fin torsion **2,351** and **80,117**, with **23.1 lb** and **638.5 lb** of axial. Appendix E's note further states the other two force components are "not zero by measurement but absent by construction" — for the fin `Fz` is neither. Three shipped examples also carry a T-tail tip-transfer node the appendix omits. A reader building a model from D or E today gets an under-loaded surface and is told the set is complete. | OR-137 |
| **OR-144** | **Appendix C splits into C.1 applied and C.2 carried**, on OR-59's reasoning unchanged: `Fz` applied and `Sz`/`Myy` cumulative share one table today, and they are different quantities. | OR-59 (extends) |
| **OR-145** | **B.2 stays, and states that it is not a member of this family.** It is the beam's own cumulative quantities — what a model built from B.1 should *return*, not what it is given — and that is why the frame is different. C.2 inherits the same statement. | OR-59 |
| **OR-146** | **A beam-frame torsion symbol follows its surface's span axis.** §5.5 prints `Myy`; §6.5 prints `Mzz`. The wing and the h-tail span `y`, so their torsion is `Myy` and the letter is right by coincidence of the convention; the fin spans `z`. §6.5 currently prints **`Myy` = 4,561 lb-in** at `ga6_normal`'s fin root for a quantity whose body-axis `My` is **identically zero** — a lateral force can produce no moment about `Y` at all. §3.2's notation table maps the beam symbols onto body axes two chapters earlier ("`Mxx` and `Mx` share a sense while `Mzz` is the negation of a body-axis `Mz`"), so a reader carries that map into §6, where it is wrong by 90°. The deck has named this `mzz` since it was written. | OR-130a |

### OR-141a — A CSV per surface, not per report (owner, 2026-09-07)

*Amendment made on agreeing §18.* OR-141 makes every appendix a view of one
list; the owner's amendment states the other view explicitly: **each surface
gets its own applied-load CSV**, carrying the same twelve columns as its
appendix, offered on that surface's page and in the export bundle beside
`wing_applied_loads.csv`. `fuselage_applied_loads.csv`,
`htail_applied_loads.csv`, `vtail_applied_loads.csv`.

One file per surface rather than one airframe file with a component column: a
consumer loads the surface they are sizing, and a single file would have to be
filtered before it could be used — the retyping OR-64 exists to prevent, one
step further on. The appendix and the CSV are the same rows through the same
owner, so a reader who prefers the file to the page is reading the same load
set, and **G-OR-90** holds all of them to the deck.

### Gates added by this ruling

| Gate | Statement |
|---|---|
| **G-OR-89** | Every applied appendix — B.1, C.1, D, E — prints OR-139's twelve columns in that order, on every shipped example, and no two of them differ in a heading. |
| **G-OR-90** | Every applied appendix row and the card the deck writes for that `GID` place the same load at the same point: same six components, same sign, same coordinates, on `ga6_normal`, `baron_58` and `concept_regional_jet`. This is the gate OR-143 would have failed. |
| **G-OR-91** | The fin's applied `Mz` is the negation of its strip torsion and its `My` is zero, at every station of every case; the h-tail's `My` is its strip torsion and its `Mz` is zero. Asserted through `applied_body_moments`, so a component added later cannot inherit the wing's map by default. |
| **G-OR-92** | Every column an applied appendix prints as zero is named in that appendix's note with the producer it lacks; a component that is non-zero anywhere on any shipped example is not describable as absent by construction. |
| **G-OR-93** | Appendix C renders as two lettered subsections with no load column shared between them, and the applied and cumulative rows of both B and C close onto one another (G-OR-29 extended to the body beam). |
| **G-OR-94** | No `Myy` heading appears anywhere in section 6 or Appendix E, and no `Mzz` heading in section 5 or Appendix D; every symbol either section uses is defined in its own notation table with the axis named. |

### Findings to file (OR-14 — file, do not fix here)

- **The fuselage applied set is `Fz` alone.** Whether the body beam has an `Fx`
  producer at all (axial from thrust, drag or a fore-aft inertia term) is not
  settled here; OR-140 prints the column as a stated zero either way, and if a
  producer exists the column is where it will appear.

## 19. Iteration 6 — Sections 7, 8 and 9, control-surface pressures (OR-147 … OR-157)

**Status: AGREED 2026-09-07 (owner, in session).** Drafted from the owner's ruling
in session: *"These surfaces will be just pressure loads. So no appendix B, C, D
type distributed loads. The aileron and flap geometry is defined with the main
surface in Section 2, use this definition. The tab is defined with the elevator.
The purpose is to show how to apply the pressure load to the control surface …
There should be no appendix needed for these three surfaces. This is similar to
the elevator and rudder pressures. Note we have some spanwise distribution of
pressure that should also be defined (this is ambiguous in the Oracle)."*

*Measurements taken 2026-09-07 against `examples/ga6_normal.project.json`,
`examples/baron_58.project.json`, `examples/concept_regional_jet.project.json`
(the three G-OR-1 builds) and `examples/cessna_210.project.json`, and quoted
where they carry a decision.*

**The section shape is already agreed and is not re-opened here.** OR-128 lettered
these three as peer sections — *aileron 7, flap 8, tab 9* — when it split the
tail into two. Nothing below changes that.

| # | Decision | Amends |
|---|---|---|
| **OR-147** | **These three sections deliver a pressure and nothing else.** No appendix, no station table, no CSV, no deck rows are added by this iteration *(owner, 2026-09-07)*. The A–E pattern exists because a wing, a body and a tail deliver a **distributed** load that a structures model integrates station by station; an aileron delivers a pressure field over a surface whose planform §2 already carries, and the reader applies it themselves. The deliverable is therefore the pressure, its shape over the surface, and the sign convention that says which way it acts. §5.3 and §6.3 — the elevator's and the rudder's chordwise distributions — are the precedent, and these sections are written to read like them. | OR-59 (does **not** extend), OR-139 |
| **OR-148** | **The geometry is Section 2's and is referenced, never restated.** §2.1 already prints an *Aileron*, a *Flap* and a *Trim tab* input table, and its wing planform figure already draws the aileron and the flap to scale on the wing while its horizontal-tail planform draws the elevator. A section that reprinted a deflection limit or an area would be the same number in two places, which §3.3 forbids. Each section opens by pointing at 2.1 through the reference owner and prints only what its own analysis produced. | §3.3 ("a number is printed once") |
| **OR-149** | **The tab is drawn on the elevator, not on the horizontal tail** *(owner, 2026-09-07)*. `TabSpec.station_in` is the butt line (wing / h-tail host) or waterline (fin host) of the tab MAC, and the surface it is cut into is the control surface, not the fixed one. The locator is therefore drawn on §2.1's **elevator** outline for an h-tail tab, the **rudder** for a fin tab and the **aileron** for a wing tab — the same three outlines 2.1 already draws as regions. | OR-148 |
| **OR-150** | **One sign convention, stated once and shared by all three** *(owner's words, 2026-09-07)*. **Pressure is positive acting normal to the control-surface plane, in the sense a trailing-edge-down deflection produces.** A positive pressure gives a **nose-down** moment about the hinge line — leading edge down, trailing edge up — and a negative pressure, which is what a trailing-edge-up throw produces, gives a **trailing-edge-down** moment about the hinge line. The two statements are one rule read from both throws, and both are printed: the aileron is the only one of the three with a signed pair, and the down throw's `+0.484` and the up throw's `−0.323` psi on `ga6_normal` are the rule's own instances. The convention is stated in the same words §5.3 and §6.3 state the elevator's and the rudder's, and the airplane-axis reading of "normal" is named per host (wing- and h-tail-borne surfaces: airplane **+z**; a fin-borne surface: airplane **+y**), because the surface's own normal is what the pressure is about and the airplane axis is what a reader applies it in. | `CONVENTIONS.md` §7, OR-146 (frame precedent) |
| **OR-151** | **The spanwise distribution is uniform pressure; the chordwise profile is in fractions of the *local* surface chord.** This is the ambiguity the owner names, and it is not a new assumption — it is what each of the three oracle equations already does, recovered and stated. Every one divides a load by an **area** to get a pressure: the aileron's `W = LAIL/(SAFWD + ½·SAAFT)`, the flap's `LF = 0.75·p_LE·SF`, the tab's `W = LTAB/1.5/STAB`. A pressure that came from an area and is quoted as one number is uniform over that area by construction. Checked against Appendix A, exactly: flap `629/(10.7·144) = 0.4082`, `÷0.75 = 0.5443` against the printed **0.545 psi**; tab `84.618/226 = 0.3744`, `×4/3 = 0.4992` against the printed **0.4992 / 0.2496**; aileron `271.44/3.894/144 = 0.4841` against **0.484**. **Two consequences are stated in the section, not left to be inferred:** the load **per unit span** is proportional to the local surface chord, so a tapered aileron carries more load per inch at its inboard end at the same psi; and the chordwise breakpoint the aileron profile carries is an **area** fraction, `SAFWD/SA` (`0.2004` on `ga6_normal`), which equals a chord fraction only where the hinge-chord ratio is constant along the span. Where it is not, the ratio is the span-mean and the section says so. | `theory_sources.md` (aileron / flap / tab) |
| **OR-152** | **The pressure has one owner — the module — and a drawn outline is a locator, never a divisor.** The entered analysis area and the entered planform outline are two different numbers, and on three of four examples they disagree: aileron analysis-area against drawn outline — the drawn one stated as a percentage of the analysis one, which is the way the document prints it — **6.488 / 6.474 (−0.2 %)** on `ga6_normal`, **7.6 / 7.306 (−4 %)** on `baron_58`, **6.2 / 6.493 (+5 %)** on `cessna_210` and **15.0 / 8.458 (−44 %)** on `concept_regional_jet`; flap **10.7 / 10.72 (+0.2 %)** on `ga6_normal`, and no other example enters a flap outline at all. A figure that shaded the outline and computed its own psi would print a pressure **77 % high** on the regional jet for a load nothing had changed — the milestone's recurring defect exactly, an entered value shadowed by a derived stand-in with nothing saying so. So the printed pressure is the module's, the figure is annotated with the **entered area it was computed from**, and where both areas exist and disagree by more than **2 %** the section **states the discrepancy** rather than drawing a shape whose area contradicts the number beside it. *(Owner, 2026-09-07: 2 % stands — it fires on the Baron and the C210 as well as the jet, which is the point of it.)* The regional jet's 77 % is filed as a data finding below; it is not this iteration's to fix. | **OR-6**, rule 3 (one owner + drift guard) |
| **OR-153** | **Two figures per section, and the second is allowed to be absent.** *(a)* The **chordwise application diagram** — a section cut through the surface, leading edge left, hinge line and chord fractions marked, the pressure block drawn to scale with its values, the resultant arrow at the pressure centroid, and the sign convention on the drawing. It is built from the module's own `ControlSurfaceStation` profile and needs no geometry, so it is available on every project that runs the module. *(b)* The **planform locator** — §2's entered outline of the surface with the pressure region on it — which is available only where that outline is entered: the aileron on all four examples, the flap on **`ga6_normal` alone**, the elevator (and so the tab) on **`ga6_normal` alone**. Where it is not entered the figure renders the OR-32 stated absence, and the section is otherwise complete. Neither figure is decoration: (a) is *how to apply the load*, which is the owner's stated purpose, and (b) is *where*. | OR-32, §4.3 |
| **OR-154** | **No hinge moment is printed, and the absence is the method's, not the replication's.** *(Checked against the source 2026-09-07, after the owner asked.)* `AILERON.BAS` runs 9 → `END` and computes the two loads, the two speeds and the two pressures; its last statements are a load check, `LCHECK = W*SAFWD + .5*W*SAAFT` — the same closure **G-OR-97** now asserts — with its `LPRINT` commented out. `FLAPLOAD.BAS` and `TABLOADS.BAS` end the same way. Chapter 16 (p105–106) says only that *"the program calculates the constant pressure forward of the hinge line"*. The words *hinge moment* appear **once in the whole manual**, inside the quoted text of CAM 3.224-1(a) — a tab's deflection *need not exceed that which would produce a hinge moment on the main surface corresponding to maximum pilot effort* — and chapter 18 (p113) then declines even that use: *"The computer program for surface loads for the aileron, elevator and rudder are not limited to pilot effort."* So sloads reports no hinge moment because the suite it replicates computes none, and deriving one here would be the report producing a load quantity — OR-6 — in the section whose whole subject is where the load acts. The **sense** of the hinge moment is the sign convention (OR-150) and is stated in words; the magnitude is not stated at all. One sentence goes with it, because a reader who applies the pressure will meet it immediately: the balance area forward of the hinge line carries the same-signed pressure and contributes the **opposite** moment about the hinge, which is what that area is for. That sloads publishes no hinge moment is filed below as a finding, not fixed here. | **OR-6** |
| **OR-155** | **The tab's locator rectangle is drawn from its entered area and MAC, and is labelled as drawn** *(owner, 2026-09-07: rectangle, not marker)*. A tab has no entered outline anywhere in the schema; it is placed by `station_in`, sized by `mac_in` and `area_sqft`. The locator is therefore the rectangle of chord `MACTAB` and span `STAB/MACTAB` centred on the entered station — **30.2 in** on `ga6_normal`, 28.8 on `baron_58`, 64.3 on `concept_regional_jet` — drawn on the elevator per OR-149. This is a **drawing** convention, and the caption says so in as many words: *the tab planform is not entered; this rectangle is the entered area at the entered station.* The alternative, a marker at the station with no extent, tells a reader where but not how much of the elevator the pressure covers, which is the question the figure exists to answer. If the owner prefers the marker, the section loses nothing else. | OR-6 (the reason it is labelled) |
| **OR-156** | **The flap prints the four conditions it was chosen from, then the pick.** `23.345(a)`'s critical load is the largest of 1G stall, 2G stall, 2G at VF and the flaps-extended gust at VF, and a pick means nothing without the set — `ga6_normal` prints **212 / 424 / 629 / 624 lb**, and that the last two are within 1 % is the section's own content. The slipstream (`23.457(b)`) and the gust-combined load (`23.345(b)(1)`) follow in their own table. *(Corrected in implementation, 2026-09-07: the draft said "their own subsection". A subsection would make Section 8 the only one of the three with a second heading level, against the owner's "simple sections"; a titled table carries the same separation at one level. Nothing else in the ruling changes.)* **The known limitation is stated where it bites:** with no engine record carrying take-off power and propeller diameter, the slipstream case does not exist and the flap is sized on the gust-combined load alone — measured ~19 % low on the C210 (#69, #85). The section states that condition rather than printing a silently smaller number. | OR-135 (provenance beside the value) |
| **OR-157** | **One row per tab, one figure per tab.** `TabLoadsInput.tabs` is a list and each entry names its host, so the summary is a table with a row per tab — host, area, MAC, station, chord ratio E, load, LE and TE pressure — and the chordwise diagram is drawn per tab, because it is the figure that carries the pressures. Every shipped example enters exactly one tab, all on the horizontal tail, so the multi-tab path is exercised on a constructed project. The station column states **which** station it is: a butt line for a wing or h-tail tab, a waterline for a fin tab, never the bare number. | OR-146 (name the axis) |

### Gates added by this iteration

- **G-OR-95** — Sections 7, 8 and 9 add **no** appendix, no manifest row and no
  CSV: the appendix set stays A–E and the manifest is byte-identical to the same
  build without them. The gate that OR-147 stayed a report change.
- **G-OR-96** — every pressure and load these three sections print is the
  module's own unscaled value, matched through the content model, against the
  Appendix A oracles: aileron **+271.44 / −180.96 lb at 170.0 kt**, **+0.484 /
  −0.323 psi** (p200); flap **629 lb**, **0.545 psi**, the four candidates
  **212 / 424 / 629 / 624**, slipstream factor **1.407**, gust-combined
  **819 lb** (p201); tab **E 0.17735**, **84.618 lb**, **0.4992 / 0.2496 psi**
  (p202) — ±0.1 %, page-cited in the test.
- **G-OR-97** — *(OR-151)* the printed pressure profile **integrates back to the
  printed load** over the entered area, on every case of every shipped example:
  the chordwise mean of the profile times the entered area equals the module's
  load to within 0.1 %. This is the gate that the stated spanwise rule is the one
  the numbers were built with, and it fails if a future edit changes either the
  profile or the area without the other.
- **G-OR-98** — *(OR-152)* no figure, table or caption in these three sections
  computes a pressure from a drawn outline; the pressure appears in the document
  only by projection from `ControlSurfaceLoadResult`. Asserted by building
  `concept_regional_jet`, whose outline and entered area differ by 77 %, and
  reading the printed psi against the module's.
- **G-OR-99** — *(OR-152)* where both areas exist and differ by more than 2 %,
  the section prints the discrepancy statement; where they agree it does not.
  Asserted in both directions, so a statement that never fires and one that
  always fires both fail.
- **G-OR-100** — *(OR-150)* the sign convention is stated in every one of the
  three sections, in the same words, and names the airplane axis its host's
  normal is; the aileron section prints **both** throws with opposite signs and
  states the hinge-moment sense of each.
- **G-OR-101** — *(OR-153)* the chordwise diagram is built on every project that
  runs the module, and the planform locator renders either the outline or the
  OR-32 stated absence — never an empty axis. Asserted on all four examples,
  which between them cover outline-entered and outline-absent for each of the
  three surfaces.
- **G-OR-102** — *(OR-148)* no deflection limit, area, chord ratio or station
  these sections reference is **printed** by them: every such value appears once,
  in §2.1, and the sections reach it through the reference owner.
- **G-OR-103** — *(OR-156)* the flap section prints four candidate loads and
  names which is critical; with no engine record it states the slipstream
  condition's absence and does not print a slipstream subsection.

### Findings to file (OR-14 — file, do not fix here)

- **`concept_regional_jet` enters an aileron whose drawn outline is 44 % smaller
  than the area its loads were run on.** The analysis area is 15.0 sq ft and the
  entered outline encloses 8.458 — the same fact as "the analysis area is 77 %
  larger than the outline", and the document states it the first way because
  the analysis area is what the pressure was divided by. One of the two is
  wrong and it is a fixture-data question, not a report one; OR-152 makes the
  document state the disagreement rather than hide it either way. The same check
  finds `baron_58` at +4.0 % and `cessna_210` at −4.5 %, which are plausible as
  outline-vs-analysis differences and are recorded for the same review.
- **Three examples enter a flap they do not draw.** `baron_58`,
  `cessna_210` and `concept_regional_jet` carry a `flap_loads` slice and no
  `flap` surface, so their flap sections will carry a stated absence where
  `ga6_normal` carries a figure. Entering the outlines is fixture work.
- **sloads publishes no control-surface hinge moment.** OR-154 states the sense
  and prints no number. Whether the hinge moment is a deliverable this suite
  should produce — it is what a control-surface attachment is sized to — is a
  scope question for a later milestone, with `AileronLoadsInput.hinges_span_in`
  and `actuator_span_in` already entered-never-invented and unconsumed.

---

## 20. Iteration 7 — Section 10, Engine Mount Loads (OR-158 … OR-170)

**Status: AGREED 2026-09-07 (owner, in session).** Drafted from the owner's ruling
in session: *"10.1 Input Data, which will summarize the input and load cases
assessed including the definition of the location of the applied loads. 10.2
Critical Cases which will contain the loads similar to the oracle, but all 6 load
components in the global coordinate system"*, and from the seven answers that
followed — *"1. Use the same as the oracle. 2. Applied by engine to airframe,
ensure this note is explicit. 3. Resolve the thrust axis into the global. Add
another table that gives the engine torque as torque about the engine thrust line
per case and thrust. 4. ok. 5. Each combination as a separate case. 6. One line
per engine. 7. All three, add the wing and fuselage and tail outline if
available."*

*Measurements taken 2026-09-07 against `examples/ga6_normal.project.json`,
`examples/baron_58.project.json`, `examples/concept_regional_jet.project.json`
and `examples/cessna_210.project.json`, and quoted where they carry a decision.*

**What the module already produces, and what it does not.** `ENGLOADS.BAS` /
`sloads/modules/engine.py` returns six FAR 23 conditions — 23.361(a)(1),
23.361(a)(2), 23.363, and for a turbopropeller 23.361(a)(3), 23.361(b)(1) and
23.371(b) — plus three FAR 25 cases behind `Project.include_far25`. Every one
classifies **`flight`** in `sloads/safety_factors.py`, so Section 10 is uniformly
LIMIT at SF 1.5 with the factor stated and applied nowhere, and no `-ULT` marker
can appear in it. `render.load_cases_to_rows` already fans the conditions into one
row per case at the combined CG — that is the Engine Mount page's CSV, and it is
in the **oracle's** convention, which is the thing OR-160 has to be explicit about.

| # | Decision | Amends |
|---|---|---|
| **OR-158** | **Section 10 is two subsections: 10.1 Input Data and 10.2 Critical Cases** *(owner, 2026-09-07)*. 10.1 states what the analysis was run from — the engine and propeller data, the three stations, the thrust axis, the case list and the sign convention — and 10.2 states what came out. No third subsection: the conditions are enumerated by regulation, not selected from a sweep, so there is no "cases assessed" step of the kind §3.3 needs. | OR-48 (the §3 shape, not extended) |
| **OR-159** | **The application point is the oracle's: the combined engine + propeller CG** *(owner: "use the same as the oracle")*. `XPP, YPP, ZPP` — the weight-average of the engine and propeller CGs, truncated to three decimals exactly as the BASIC did — is the point every component in 10.2 acts at, and it is the point Appendix A prints as `APPLIED AT X,Y,Z`. **Three stations are in play and 10.1 prints all three**, because the deck already carries the other two: `lra-engine-mount` sits at the **engine** CG and `lra-engine-hub` at the **propeller** CG (`export/lra_model.py`), and a reader transferring this set to a mount plane needs to know which of the three the moments are quoted about. The loads are quoted about the combined CG and nothing else; the other two are printed as geometry. | OR-6, `CONVENTIONS.md` §1 |
| **OR-160** | **The published set is the load applied by the engine to the airframe, and the section says so in as many words** *(owner, 2026-09-07: "ensure this note is explicit")*. The oracle's `ENG MOUNT TORQUE` column is printed **negative** because it is the reaction the mount applies to the engine; so is `load_cases_to_rows`' `Engine mount torque` column on the Engine Mount page's CSV, and both stay as they are. Section 10.2 publishes the **opposite** sense — what the engine does to the structure — because that is what every other applied set in this document publishes (Appendices B–E, OR-141) and a reader who mixes the two sizes a mount backwards. The relationship is stated, not implied: 10.2 names the CSV column it is opposite to. **G-OR-105** holds the two to opposite signs — always, and to equal magnitudes where the thrust line *is* the airplane's own axis, which is the case the equality can be asserted on — so they cannot drift into agreement and a third convention cannot appear between them. | OR-141, OR-143 (the same class of defect) |
| **OR-161** | ~~**SUPERSEDED by design note 53 D-53.3 (owner, 2026-09-07)**~~ — the thrust line is now an *input*, two entered points, and an engine that states none is resolved about the airplane's forward axis and marked ASSUMED. The derived middle grade below is gone: it is a line between two **mass** stations, not the shaft, and it inherits every error in either — measured 14.0° off `x` on `ga6_normal` (which put `Mz = −178.8 ft-lb` into 10.2 for an airplane with no such moment) and 71.6°, very nearly straight up, on `cessna_210`, whose engine CG waterline is a filed defect. The caveat this decision shipped with, and the backlog entry filed beside it the same day, were the reasons. What survives unchanged: the owner is `export/coordinates.py`, the assumed grade is flagged on every deliverable, and 10.1 prints the direction cosines. *Original text:* **The thrust axis is derived from the entered stations, resolved into the global frame, and has one owner** *(owner: "resolve the thrust axis into the global")*. The axis is the unit vector from the engine CG to the propeller hub, `prop_cg − engine_cg` — forward by construction, since a hub is ahead of the engine that drives it. Where the two coincide, or either is unentered, the axis falls back to airplane **−x** (forward) and is **marked ASSUMED** in 10.1 — the same explicit-with-flagged-inference shape `mounted_on` (BM-4) and `fuselage_centreline` already use, and both branches are exercised by shipped data: `ga6_normal` (−32, 0, +8), `baron_58` (−20, 0, 0) and `cessna_210` (−32, 0, −4) derive it; `concept_regional_jet`, whose two engines enter `prop_cg == engine_cg`, assumes it. The owner is **`sloads/export/coordinates.py`** — `CONVENTIONS.md` §1 already names that module the single edit point for every axis resolution in the suite, and `tail_torsion_to_airplane` is the precedent for the report reading it rather than restating its signs (OR-146). Nothing is resolved inside the report. | `CONVENTIONS.md` §1, rule 3 |
| **OR-162** | **The torque's sense is derived, not asserted — and the draft got it wrong.** The module states "clockwise from the pilot's view is positive". The pilot looks **along** the thrust axis, so a right-hand-positive rotation about it is what the pilot sees as clockwise: the module's scalar is already the right-hand sense about the axis. *(Corrected in implementation, 2026-09-07.)* The draft added **a negation** here, to turn "the reaction" into "the applied load" — and that made Section 10.2's `Mx` **equal** the load-case file's `ENG MOUNT TORQUE`, the two conventions agreeing, which is the one outcome that means one of them has been lost. Third law, twice, settles it and no negation survives: a propeller turning clockwise from the seat is driven by `+Q` from the engine, returns `−Q` to the engine, is held by `+Q` from the mount, so **the engine delivers `−Q` to the airframe** — which is exactly what `mx_mount_torque` carries and what the oracle prints as a negative number. The scalar is *rotated*, not flipped: with `â ≈ (−1, 0, 0)`, `−Q` about it is `mx = +Q`, and a positive moment about the aft-positive `x` axis carries starboard up — the **left roll** a clockwise propeller produces. Two independent readings agreeing is what makes the sign derived. 10.1 prints the **direction cosines** of each engine's axis so this is checkable on the page rather than taken on trust. | `CONVENTIONS.md` §1 |
| **OR-163** | **10.2 carries two tables, and the second is the thrust-line pair** *(owner, 2026-09-07)*. **Table 1** is the six global components — `Fx Fy Fz Mx My Mz` at the OR-159 point — one row per case per engine, with the SF stated. **Table 2** is the same cases with the **torque about the engine thrust line** and the **thrust along it**: the two scalars Table 1 was resolved from. *(Corrected in implementation, 2026-09-07: neither table prints a **FAR** column. Eleven columns would not set upright at any size and the renderer turned the page; the regulation for each case is in 10.1's case list against the same case ID, so dropping it costs the reader a glance and saves them a rotated page. The condition's name stays, in a short form owned in one place — **G-OR-112** holds every reference the module can produce to an entry in it, so a condition added later cannot print a blank.)* It derives nothing Table 1 does not, and it exists for two reasons — an installation whose thrust line is not along `x` has its engineering numbers in the engine's own axis, where a mount is actually designed; and printing the pre-resolution pair beside the post-resolution set makes **G-OR-104** a check a reader can repeat rather than one only the suite can. | OR-135 (provenance beside the value) |
| **OR-164** | **Thrust is a component of the gyroscopic case and of no other** *(owner: "ok")*. 23.361 and 23.363 prescribe no thrust, and 23.371(b) prescribes max-continuous thrust explicitly. `Fx` therefore prints `0` in the 23.361/23.363 rows and is **not** filled from `EngineInput.thrust_lb`, which is a *flight* input `balance.hub_thrust_set` applies at the hub in the assembled balanced cases (#10) and is not a component of any engine-mount condition. 10.1 states that in one sentence, because a reader who has met `thrust_lb` on the Engine page will otherwise read the zero as an omission. | OR-140 (a zero column is printed and named) |
| **OR-165** | **Every gyroscopic sign combination is its own case** *(owner, 2026-09-07)*. 23.371(b)'s four combinations of `±Myy` and `±Mzz` fan out into four rows, each with the 2.5 g vertical and the max-continuous thrust that act in every one of them, carrying the **a/b/c/d** case IDs already minted by `render._gyro_subcase_id`. That existing owner is asked, not re-implemented: a second suffix scheme would be a second identity for the same case, and the case ID is what ties a row here to a row in the CSV. | `case_ids.py`, backlog Step D1 |
| **OR-166** | **One row per engine** *(owner, 2026-09-07)*. Every entry in `project.engines` prints its own rows at its own butt line, tagged with the designation the module already prefixes onto a multi-engine title. No critical engine is selected and no mirror is asserted: two mounts are two structures, `baron_58`'s pair sit at BL ∓66 with opposite `y`, and the saving from printing one would be four rows. | OR-6 |
| **OR-167** | **The side load prints one sense and states the other.** 23.363 prescribes a side load acting in **either** direction and the oracle prints a magnitude (`770.07 lb` at `ny = 1.33` on the Appendix A engine). The row prints it as `+Fy` and the section states that the mount is checked for both senses. It is **not** fanned into two cases the way the gyro combinations are, and the difference is the point: the gyro sub-cases exist because the module publishes four signed pairs, and a second side-load case would be the report minting a case the analysis did not run. Filed below as a finding, not resolved here. | **OR-6**, OR-165 (why the two differ) |
| **OR-168** | **Three figures — side, front and planform — and each draws whatever airframe outline the project entered** *(owner: "all three, add the wing and fuselage and tail outline if available")*. Side view in `X–Z`, front view in `Y–Z`, planform in `X–Y`; each carries the fuselage outline, the wing, the horizontal tail and the vertical tail wherever the project enters them, drawn through §2.1's own polyline owner so the shapes cannot disagree with Section 2's. On each, every engine's **mount node, hub node and application point** are marked, the thrust axis is drawn as the line between the first two, and the positive senses of the components lying in that view's plane are drawn on it — which is what makes the sign convention a picture rather than a paragraph. An outline that is not entered is simply not drawn and the caption names which were; a project with **no** entered outline still gets all three figures, because the engine stations are the subject and the airframe is context. The figure is absent only where there is no engine. | OR-153 (two figures; this section earns three), OR-32 |
| **OR-169** | **The fuselage outline gets one owner, here, because this is the first consumer that draws it.** `GeometryInput.fuselage` has carried a section table (`x`, `width`, `height`, `z_centre`) since the schema had a body, and **nothing draws it**: §2.1 draws surfaces, §4.1 draws the *beam*. `derived_geometry.fuselage_outline(project, frame)` becomes the one producer of the body's polyline in each of the three views — side from the centreline ± half-height, plan from ± half-width, front from the maximum section — reading `fuselage_centreline` for the side view's datum so the existing assumed-centreline note is the one that travels, rather than a second guess made in the report. Rule 3, at the first time of asking. | rule 3, `CONVENTIONS.md` §7 |
| **OR-170** | **`ga6_normal`'s engine and propeller CG waterlines are wrong, and this iteration fixes them.** *(Defect found 2026-09-07 while measuring for OR-159; page-cited.)* The fixture enters `engine_cg = (22, 0, −10)` and `prop_cg = (−10, 0, 93.022)`, which puts the worked example's engine at **waterline −10** and gives a combined CG of **(17.910, 0, 3.166)**. Appendix A p227 prints `APPLIED AT X,Y,Z  17.91, 0, 93.022`. Reading the page's input block back, the two entered triples are `ENGINE CG 22, 0, 92` and `PROPELLER CG −10, 0, 100`, and they reproduce the printed combined CG exactly: `(505·92 + 74·100)/579 = 93.0224…`, truncated to **93.022**. What is in the fixture is a transcription slip in both slots — the propeller's `x` (−10) pasted into the engine's `z`, and the printed **combined** `z` (93.022) pasted into the propeller's. The fixture comment, *"XPROP chosen so combined XPP = 17.91"*, records that only `x` was ever checked, and no test asserts `zpp`. It is corrected in `examples/ga6_normal.project.json` and `tests/fixtures.py`, **G-OR-106** asserts `zpp` against the printed figure so it cannot slip back, and the deck digests move with it because the LRA engine mount and hub nodes are placed from these stations. Under rule 6 a defect with first-order effect on shipped content outranks the iteration it was found in. `cessna_210` carries the same shape of error — `(20, 0, −8)` / `(−12, 0, 88)`, combined `z = 4.843` — with **no printed page to derive the right values from**; it is filed below with its number and is not guessed at here. | rule 4, rule 6, **OR-6** |

### Gates added by this iteration

- **G-OR-104** — *(OR-161/OR-162/OR-163)* the six global components printed in
  Table 1 are the resolution of the two scalars printed in Table 2, for every
  case of every engine of every shipped example:
  `(Mx, My, Mz) == T·â + (0, Myy, Mzz)` and
  `(Fx, Fy, Fz) == thrust·â + (0, Fy, −Fz_down)` to 1e-9. Asserted **through
  `coordinates.engine_applied_load`**, not against a column, so a component added
  later cannot inherit a literal at a call site — the OR-146 shape.
- **G-OR-105** — *(OR-160)* for the same case, §10.2's `Mx` and the Engine Mount
  page's CSV `Engine mount torque` are **exactly opposite** and neither is zero,
  on a conventional installation. The gate that the two conventions stay two, and
  stay related.
- **G-OR-106** — *(OR-159/OR-170)* the Appendix A reciprocating figures, ±0.1 %
  and page-cited: `n = 2.85`, vertical **1650.15 lb**, applied at
  **(17.91, 0, 93.022)**, mean take-off torque **554.3884 ft-lb** and the
  AC 23-19A corrected **737.34**; `n = 3.8`, **2200.2 lb**, max-continuous torque
  **556.7227**, mount torque **−740.4412**; side-load factor **1.33**, side load
  **770.07 lb** (p227–229).
- **G-OR-107** — *(OR-165)* a turbopropeller project prints the four gyroscopic
  combinations as four rows with the `a/b/c/d` IDs `render._gyro_subcase_id`
  mints, and no fifth row; the vertical and the thrust repeat unchanged across
  all four.
- **G-OR-108** — *(OR-166)* on `baron_58` every case appears once per engine, each
  at its own butt line, with both signs of `y` present and the designations
  distinguishing the rows.
- **G-OR-109** — *(OR-161)* an assumed thrust axis is marked and a derived one is
  not, asserted in **both** directions on shipped data:
  `concept_regional_jet` (hub at the engine CG) prints the ASSUMED statement,
  `ga6_normal` does not.
- **G-OR-110** — *(the load-output contract)* no load Section 10 prints is marked
  ultimate: every load column carries a LIMIT label, every row states its factor
  in an `SF` column, and the section's rendered text contains no `-ULT`.
- **G-OR-111** — *(OR-168/OR-169)* the three figures draw every outline the
  project enters and the caption names them; on a project that enters none they
  still draw the engines, and on a project with no engine all three render the
  OR-32 stated absence.
- **G-OR-112** — *(added in implementation)* every FAR reference the module can
  produce, FAR 25 cases included, has an entry in the short-name map a load
  table prints from. A load table's Condition column is a *second* name for a
  condition, so the map from the first must be total, or a condition added later
  prints its full sentence into a ten-column table — or, under a future edit,
  prints nothing.

### Findings filed, not fixed here

- **`cessna_210`'s engine and propeller CG waterlines** are `−8` and `88`, giving
  a combined CG at waterline **4.843** — the same class of slip as OR-170 with no
  printed page to correct it from. Needs the airplane's own data.
- **No side-load case is run for the negative sense** (OR-167). The mount is
  checked for both by the reader; the analysis publishes one signed value.
- **No engine-mount case reaches the sbeam deck.** The LRA model has carried
  `lra-engine-mount` and `lra-engine-hub` nodes since note 24 R-9, and nothing
  writes a `FORCE`/`MOMENT` at them for a 23.361 condition. Section 10 delivers
  the six components a deck would need, which is what makes this the point at
  which the gap is worth stating.

## 21. Iteration 8 — Section 11, One Engine Inoperative (OR-171 … OR-182)

**Status: AGREED 2026-09-07 (owner, in session).** Drafted from the owner's
answers to six questions — *"Q1 add the yaw transient section. Q2 all 6. Q3 this
is a good question, should these loads go in the v-tail section and be added to
the envelope for the v-tail? and the distributed load in the v-tail appendix? Q5
unrecoverable statement, these would then need to be checked with stability and
control team to assess if it correct. Q6 does the baron not provide sufficient
coverage? currently the t-tail configuration of the ATR is not fully implemented,
but when it is it should be added to the document full shipped set"* — and from
the five that followed: *"A. Let's keep it Section 11, can we add the distributed
tail loads to the same appendix? B. Mark the plot to indicate this case is SF 1.0.
(In a later milestone this is the reason I want to do all down select at ultimate
and convert all delivered loads to ultimate.) C. Uncontrollable cases DO NOT enter
the envelope. D. For single engine airplanes make a note 'These cases are not
applicable.' You can provide additional details of the regulations. E. So long as
it results in the peak total load this is acceptable."*

*Measurements taken 2026-09-07 against `examples/baron_58.project.json`,
`examples/atr42_100.project.json`, `examples/dhc8_dash8.project.json` and
`examples/ga6_normal.project.json`, and quoted where they carry a decision.*

**What the module already produces.** `ONENGOUT.BAS` / `modules/one_engine_out.py`
is the suite's only **time-marching** analysis: an Euler integration of the yaw
transient that follows an engine failure, from the failure through the 23.367(b)
two-second delay, the rudder ramp and the recovery. It returns one
`ConditionResult` per speed case — 23.367(a)(2) at VC classified **ULTIMATE**
(SF 1.0), 23.367(a)(1) at VD LIMIT, and the VS floor where VS is substituted for
VMC — each carrying engine thrust, windmill drag, maximum yawing velocity, the
**maximum tail load**, its 25 %/50 % MAC split at the peak, and the time to
recovery. The case IDs are `VT-30…`, ONENGOUT's own disjoint band (M4-2
decision 5).

**The finding that reorganised this iteration.** Section 11 was scoped as a report
section. Measuring its loads against Section 6's showed it could not be one.

| Airplane | Largest SELECT fin case (LIMIT) | 23.367 at VD (LIMIT) | Ratio |
|---|---|---|---|
| `baron_58` | 1357.2 lb (YAW 15 NEUTRAL) | **2155.8 lb** | 1.6× |
| `atr42_100` | 4878.1 lb (YAW 15 NEUTRAL) | **12 829.3 lb** | 2.6× |
| `dhc8_dash8` | 4527.1 lb (SIDE GUST) | **14 780.8 lb** | 3.3× |

On every twin in the fixture set the one-engine-out case is the **governing** fin
load, by up to 3.3×, and the fin is sized without it: 23.367 is not in Section 6's
critical set, not in the chordwise or spanwise distribution, not in Appendix E and
not in the exported deck. Under rule 6 a defect with first-order effect on shipped
content outranks the iteration that found it.

| # | Decision | Amends |
|---|---|---|
| **OR-171** | **Section 11 is three subsections: 11.1 Input Data, 11.2 Critical Cases and 11.3 Yaw Transient** *(owner: "add the yaw transient section")*. The third exists because this analysis is a *march*, not a condition: 11.1 and 11.2 alone would state a peak load with no account of the event that produced it, and the reader's first question about a transient is when the peak occurs relative to the pilot's input. 11.3 is where the histories, the recovery times and the 23.367(b) delay are stated. It is the first section in this document whose content is a time axis. | OR-158 (§10's two; this section earns three) |
| **OR-172** | **The 23.367 cases join the fin's critical set, and the whole v-tail chain picks them up** *(owner, 2026-09-07, answering their own question)*. The measured ratios above are the argument: a document that prints a governing load in Section 11 while Section 6 five pages earlier calls a smaller one critical has published a contradiction, and a deck built from the smaller one sizes a fin that the certification case breaks. ONENGOUT already publishes the `lt25`/`lt50` split at the same `xv25`/`xv50` stations SELECT uses, which is exactly what `taildist` and `tail_span` distribute from — so Section 6.2, 6.3, 6.4, 6.5, **Appendix E and the exported v-tail deck** take the cases with no change to any of them. Verified by prototype before the decision was taken: `baron_58`'s applied deck goes from 40 rows to 70 and the SF-1.0 case carries its own factor through. The owner's *"can we add the distributed tail loads to the same appendix"* is answered by doing nothing to stop it — one appendix per surface stays one appendix per surface (OR-141a). | OR-129, OR-136, OR-141a, **rule 6** |
| **OR-173** | **One case per engine, and no mirror asserted** *(decided in draft, owner reviewed)*. `failed_engine_index` selects one engine, which gives the fin **one** sense of load; SELECT's set carries both naturally (`−476.8` and `+1015.6` on `baron_58`). Each entered engine's failure is therefore run as its own case. The alternative — run one and mirror it — is correct only on a symmetric installation, which `baron_58` happens to be and a future asymmetric one will not; and a mirrored case is the report minting a case the analysis did not run, which is what OR-6 forbids. Section 10's OR-166 is the precedent, one section back: one row per engine, two mounts are two structures. `failed_engine_index` stays, as the selector for the single-case views that already read it. | **OR-6**, OR-166 |
| **OR-174** | **An uncontrollable case is printed in full and excluded from the envelope** *(owner: "uncontrollable cases DO NOT enter the envelope")*. Where the march reaches the 60 s bound without recovery — `atr42_100` and `dhc8_dash8` both do at VS — the section prints the case, its load at the simulation limit, and the statement that the airplane is uncontrollable at that speed, **with the referral the owner asked for: the case is for the stability-and-control discipline to assess, not for this analysis to rule on**. It does not reach the fin's critical set, the distribution, the appendix or the deck. A number at the simulation bound is not a design load, and an envelope that quietly absorbs one has accepted a load nobody has accepted. Printing it and excluding it are both required: suppressing it would hide that the case ran. | OR-6, **note 49 OR-116** |
| **OR-175** | **The chordwise split is taken at the instant of peak total load** *(owner: "so long as it results in the peak total load this is acceptable")*. `lt25` and `lt50` are read from the single history row where `lt25 + lt50` is greatest — on `baron_58` at VD that is `t = 2.15 s`, `θ = 3.609°`, rudder `12.50°`, `LT = 2155.82 lb`. Not each quantity's own maximum, which would combine two instants the airplane never occupies and produce a chordwise distribution of a load that never existed. The condition also publishes the peak instant's `θ` as its sideslip and the rudder angle as its deflection, so a fin case from this section carries the same aero state every other fin case does. | note 35 AS-1/AS-2, `CONVENTIONS.md` §1.1 |
| **OR-176** | **The ultimate-classified case is marked wherever it is plotted or tabulated** *(owner: "mark the plot to indicate this case is SF 1.0")*. 23.367(a)(2) is classified ULTIMATE by the regulation, so it carries SF 1.0 while every case beside it carries 1.5, and a fin envelope is therefore a maximum over cases whose prescribed factors differ. Every table row and **every plotted series** naming that case states its factor in band. This is the note 49 shape — the factor stated per subcase and applied nowhere — held at the point where it is easiest to lose, which is a chart. | note 49 **OR-116**, OR-136 |
| **OR-177** | **Six figures: every case, both quantities** *(owner: "all 6")*. Per case, one figure of `θ` and `θ̇` against time and one of `LT25`, `LT50` and their total — the two the GUI already draws, which is what makes the document and the screen the same analysis rather than two renderings of it. Three speed cases per engine. The 23.367(b) two-second delay, the instant corrective action begins and the peak are marked on each, because a transient plotted without its events is a curve rather than a result. | OR-32, OR-153 |
| **OR-178** | **"Not applicable" becomes a section state of its own, because implementing this section would otherwise print a falsehood** *(owner: "for single engine airplanes make a note 'These cases are not applicable'")*. `ga6_normal` renders Section 11 today as `NOT_IMPLEMENTED` — *"Nothing about this project or this issue is missing"* — which is true. The moment the builder exists it falls to `ABSENT`: *"Not analysed. The inputs this section needs are not present in the project."* That is **false**. A single-engine airplane is not missing inputs; it has no one-engine-inoperative condition, and telling a reader to go and enter something is the exact defect `STATE_TEXT`'s own docstring was written about. So: a fourth `SectionState`, `NOT_APPLICABLE`, ranked above `ABSENT`, whose reason is read from **`applicability.step_not_applicable`** — the predicate the module refuses on, the coverage table cites and the GUI withholds on, already written and already the single owner (#84, C210-43). No second copy of the rule, and the sentence names the regulation: 23.367(a) is the unsymmetrical-load condition of a **multi-engine** airplane, and losing the only engine leaves no asymmetric thrust and no yaw moment to react. **What the page prints, verbatim** *(owner, 2026-09-07: "for single engine airplanes make a note 'These cases are not applicable.' You can provide additional details of the regulations")*: the lead is **Not applicable**, and the sentence is the predicate's own — *"These cases are not applicable. FAR 23.367 does not apply — single/centreline engine: a single-engine airplane has no one-engine-inoperative condition. Losing the only engine leaves no asymmetric thrust and no yaw moment to react."* The regulation is named because the owner asked for it and because a reader checking a certification basis needs to see that the condition was considered and ruled out, not merely that nothing was printed. Rule 3 at the first time of asking; rule 4 sweeps it across every entry in `_STEP_NOT_APPLICABLE`, which is where the class lives. | **rule 3**, rule 4, OR-2 |
| **OR-179** | **The fin's inertia relief is absent on these cases, and the section says so.** `tail_span._case_weight` returns zero for a condition naming no V-n point — deliberately, *"switches the lateral inertia off rather than dividing by a guess"* — and a 23.367 condition names none, so `n_y = 0` on every one of them and the fin's own mass contributes no relief. Measured on the prototype. That relief is **unconservative** and worth 0.7–1.8 % by its owner's own docstring, so its absence is safe and nothing is changed to obtain it. It is stated in 11.2 and in Section 6.5's existing inertia sentence, because a reader comparing an OEI row against a SELECT row beside it will otherwise read the difference as an omission. | OR-140 (a zero is printed and named), L-7/L-8 |
| **OR-180** | **The 23.367 cases reach the load-case index with every load column blank, and this iteration fixes the instance.** *(Defect found 2026-09-07 while scoping OR-172.)* The module publishes its headline load under the key `max_tail_load`; `render.load_cases_to_rows` maps `fy_side`. So the case index — the file a reader takes to a stress group — carries three 23.367 rows with an ID, a regulation, a speed and a factor, and **no load at all**. Same class as OR-170 one iteration back: a published deliverable that is silently empty. The fin load is a side load and is keyed as one. The fin load is a side load and is keyed as one. **The rule-4 sweep was attempted and abandoned on measurement** — see G-OR-118: *every published condition reaches the index carrying a load* is false of the suite by design, so what would have been a class gate is a filed finding instead. Keying the instance correctly is a strict improvement either way, and the 23.367 rows now carry the load they always had. | rule 4, rule 6, **OR-6** |
| **OR-181** | **The OR-15 admission of 2026-09-07 (the frozen set), scoped to two files.** Granted by the owner in session after the prototype established what was needed. **`modules/one_engine_out.py`**: publish the fin `CriticalCondition`s from the peak instant (a new function — `simulate` and `_moment` untouched), key the headline load `fy_side` (OR-180), carry `recovered` out so OR-174 can exclude, and loop the entered engines (OR-173). **`modules/select.py`**: one insertion point in `default_critical` appending those conditions to the fin's set, with a function-local import — ONENGOUT already reads `select.effective_vtail_inputs`, and a module-level import would close a cycle. Explicitly **not** admitted and not touched: `tail_span.py`, `taildist.py`, and any refactor, rename or reformatting in either admitted file. Both re-pinned in the frozen manifest with the scope recorded beside the hash. Two consequences stated to the owner before the grant and accepted: the persisted `CriticalLoadSet` gains rows on every twin so **the deck digests move**, and Section 6 names a different governing fin case on all three twins. | OR-13, OR-15 |
| **OR-182** | **`baron_58` carries the section; the ATR joins the shipped set when its T-tail lands** *(owner, 2026-09-07)*. Of the three shipped reports only `baron_58` produces a Section 11 — `ga6_normal` is single-engine (OR-178) and `concept_regional_jet` is a turbofan, which the module **refuses** on `PROPELLER_ONLY_NOTE` grounds: thrust is shaft power over true airspeed and the windmill term collapses with the propeller diameter, so a fan installation's asymmetry would be understated rather than approximated. `baron_58` exercises every case, every figure and the whole OR-172 chain. What it does **not** reach is the uncontrollable branch — it recovers at all three speeds, and only `atr42_100` and `dhc8_dash8` hit the 60 s bound — so OR-174's statement is gated by tests and printed in no shipped document until then. `atr42_100` is a **T-tail** and design note 51 is AGREED but unimplemented; it is added to the shipped set when that lands, and this decision is the record of why the gap exists in the meantime. | OR-37, note 51 |

### Gates added by this iteration

- **G-OR-113** — *(OR-172)* on every shipped twin, the fin's critical set
  contains a 23.367 condition, and the largest fin load in Section 6 equals the
  largest in Section 11 where 23.367 governs. The gate that the two sections
  cannot name different critical cases.
- **G-OR-114** — *(OR-172)* every 23.367 condition admitted to the critical set
  reaches the chordwise distribution, the spanwise distribution, Appendix E and
  the exported v-tail deck, asserted by case ID through all four. A case in the
  envelope that stops short of the deck is the defect this gate exists for.
- **G-OR-115** — *(OR-173)* a twin runs one case per entered engine, both senses
  of fin load are present across the set, and no case is a mirror of another:
  each names its own engine and its own butt line.
- **G-OR-116** — *(OR-174)* a non-recovering case is printed in Section 11 with
  the uncontrollability statement **and** the stability-and-control referral, and
  its case ID appears in **no** critical set, no distribution, no appendix and no
  deck. Asserted on `atr42_100`, whose VS case does not recover, in both
  directions — the recovered cases from the same run *are* present.
- **G-OR-117** — *(OR-175)* the `lt25`/`lt50` a fin condition carries are the pair
  from the single history row of greatest total, asserted against a re-run of
  `simulate` rather than against a stored number, so the peak cannot drift from
  the march that produced it.
- **G-OR-118** — *(OR-180)* the 23.367 rows reach the published case file
  carrying a side load, and the key they publish it under is the one
  `load_cases_to_rows` maps. **Narrowed from the sweep this decision first
  claimed, on measurement**: the general form — *every published condition
  reaches the index carrying a load* — is **false of the suite by design**, and
  asserting it would have been a gate that had to be weakened until it meant
  nothing. Measured 2026-09-07: **100 of 118** `vtail`-tagged conditions across
  every shipped example carry a blank `Side load`, SELECT's own four among them.
  The case index is a register of case *identities* — id, regulation, speed,
  factor — and its six load columns are the engine-mount/balance shape, filled by
  the producers that speak it. That is a real question about what the file is
  for, and it is filed below rather than answered by a gate written to pass.
- **G-OR-119** — *(OR-176)* every table row and every plotted series naming
  23.367(a)(2) states SF 1.0 in band, and no load in Section 11 is marked
  ultimate: the section's rendered text contains no `-ULT`.
- **G-OR-120** — *(OR-178)* `ga6_normal`'s Section 11 renders the
  `NOT_APPLICABLE` lead and the regulation-citing reason, and **not** the
  `ABSENT` one; the reason string is `applicability.step_not_applicable`'s own,
  compared by identity so a second copy of the sentence cannot appear. Every key
  in `_STEP_NOT_APPLICABLE` is covered.
- **G-OR-121** — *(OR-177)* six figures on `baron_58`, each marking the 23.367(b)
  two-second delay, the onset of corrective action and the peak; a project whose
  march produces no history renders the OR-32 stated absence.
- **G-OR-122** — *(OR-179)* the fin inertia is zero on every 23.367 condition and
  non-zero on every SELECT condition beside it, and Section 11 states the reason.
  The gate that a silent zero stays a stated one.

### Filed, not fixed here

- **Down-select at ULTIMATE and deliver ultimate loads** *(owner, 2026-09-07:
  "in a later milestone this is the reason I want to do all down select at
  ultimate and convert all delivered loads to ultimate")*. OR-176 is the
  motivation in miniature: an envelope taken over cases whose prescribed factors
  differ is a maximum of quantities that are not comparable, and selecting the
  critical case at LIMIT can name the wrong one. This reverses note 49's OR-116
  for the delivered set and needs a design note of its own. Filed against 0.9.x.
- **The case index's load columns are sparsely populated, and it is not clear
  what the file is for.** Measured while attempting OR-180's rule-4 sweep: **100
  of 118** `vtail`-tagged conditions across the shipped examples carry a blank
  `Side load`, including all four of SELECT's own on every airplane. The six load
  columns are an engine-mount/balance shape and most producers do not speak it,
  so the file is a register of case identities for them and a load table for a
  few. Either it is an index — in which case the load columns invite a reader to
  conclude a case carries nothing — or it is a load table, in which case most of
  it is missing. Needs a decision before it is gated.
- **`atr42_100` and `dhc8_dash8` do not recover at VS.** Both reach the 60 s
  bound. Whether that is the model, the fixture's VS, or a real VMC finding is a
  stability-and-control question (OR-174) and is not settled here.

---

## 22. Iteration 9 — Section 12, Landing Gear Loads (OR-183 … OR-192)

**Status: AGREED 2026-09-07 (owner, in session).** Drafted from the owner's
answers to three findings and six questions — *"F1 all cases should be listed.
F2 add all conditions, no critical case downselect can be done without
considering the airplane loads. F3 the user can overwrite the computed, that is
the user's decision. Q1 fold 12.4 into 12.3. Q2 Ok. Q3 Nose and main. Q4 The csv
and the appendix should have the same style as the other wing, fuselage and
empennage sections, i.e. case, load application point, all 6 loads in global, and
SF. Q5 granted. Q6 can we replicate figures similar to those in the oracle
document pages 233 and 234 that explain the angles and identify which cases use
which geometry?"* — and from the five that followed: *"C1 b. C2 Use both points
but the one that is applicable for the case. C3 33, with 25–33 flagged as
carrying no airplane equilibrium — confirmed. C4 A separate CSV file for each
structural element, i.e. each appendix wing, h-tail, v-tail, fuselage, engine and
another for landing. Then they can be specifically shaped for the loads presented
in that csv. C5 three figures that cover all cases would be very helpful."*

*Measurements taken 2026-09-07 against `examples/ga6_normal.project.json`,
`examples/baron_58.project.json` and `examples/concept_regional_jet.project.json`
— the three shipped reports, and the first section since Section 2 that all three
produce — and quoted where they carry a decision.*

**This is the last analysis-body section.** With it the derived body is complete:
every `oracle_steps()` step with a `bas` that produces results has a built
section, and `IMPLEMENTED` stops being a subset of `analysis_steps()`.

**What the module already produces.** `LGFACTOR` + `LANDLOAD`
(`modules/landing.py`, Ref 1 Ch 20 p126-130) emit **40 conditions**: the
landing-load-factor condition, six per-FAR-family "critical reaction" summaries,
and the full **33-case reaction matrix**, each matrix case carrying ~48 values in
two frames — the airplane-datum delivered set for all three wheels (an unloaded
wheel at zero, never omitted) and the manual's primed ground-line set — plus the
unbalanced moments and the ground-line inertia factors. Cases 1-24 are already
assembled into balanced ground cases and exported; 25-33 are the 23.499
supplementary-nose family, gear-design conditions with no airplane in
equilibrium. Oracles: Appendix A p236 (`V 9.0048 / N 3.0951 / NLG 2.4281`) and
p230 (`K 0.324 / GAMMA 17.978` and the AP/BP/DP/CP lever-arm table).

### The three findings that reshaped the iteration

**F1 — every landing row reaches the load-case index with no load, and so does
almost everything else.** Measured 2026-09-07: **40 of 40** landing rows carry a
blank load on all three shipped examples. Sweeping the whole registry the figure
is **344 of 347** rows on `ga6_normal`, **543 of 555** on `baron_58` and **587 of
617** on `concept_regional_jet` — only the engine module's handful are filled.
This is not a landing defect. `render.load_cases_to_rows`' own docstring says its
columns are *"the load components an engine mount must react"*, and
`load_keys.LOAD_CASE_KEYS` is that shape: one force triple and one moment triple
at one point. A landing case has **three legs at three points** and cannot be
expressed in it at all. This is the question filed at the end of §21 — *is that
file an index or a load table?* — and Section 12 is where it stopped being
deferrable. **Answered by OR-186.**

**F2 — the family "critical reaction" summaries hide the case that sizes the nose
gear.** `landing._critical` returns **one** case per FAR reference, ranked on
`max(main-wheel resultant, nose-wheel resultant)`. On all three shipped examples
the 2-wheel level landing wins 23.479(a) on main-wheel load, so the **3-wheel
level landing never appears as a critical row** — although its nose reaction is
the largest of the family (`1786.8` / `4194.3` / `8178.8` lb) and it is the
condition **Section 4's own advisory forward-references by name**: *"the forward
fuselage is critical for up bending in the three-wheel level landing … those
conditions are analysed in §12."* Under §21's own precedent the document may not
forward-reference a condition the target section does not contain. **Answered by
OR-184 and OR-185.**

**F3 — two of the three shipped examples run at an entered load factor, not the
computed one.** `ga6_normal` enters `N = 3.167` against LGFACTOR's energy
estimate `3.0970`; `concept_regional_jet` enters `2.67` — exactly the 23.473(g)
floor — against `2.3755`. The reactions run at the entered value. The owner's
ruling is that this is the user's decision to make (*"the user can overwrite the
computed"*), so nothing refuses; **OR-187** states it instead.

| # | Decision | Amends |
|---|---|---|
| **OR-183** | **Section 12 is three subsections: 12.1 Input Data and Gear Geometry, 12.2 Landing Load Factor and 12.3 Ground Load Conditions** *(owner: "fold 12.4 into 12.3")*. The free body — where the reaction acts, at what strut state and ground angle, and what arrives at the gear reference point — is not a separate analysis from the reactions; it is the same reactions stated at their point. A fourth subsection would have split one statement across two headings, which is the defect OR-140 names in the small. 12.2 stands alone rather than folding into 12.1 because LGFACTOR is a **separate program** with its own oracle and its own regulation (23.473(d)-(g)), and its output is the input the whole of 12.3 runs at. | OR-171 (§11's three), OR-158 |
| **OR-184** | **No critical-case down-select survives into this section: all 33 conditions are delivered** *(owner: "add all conditions, no critical case down-select can be done without considering the airplane loads")*. A ground case sizes a gear leg through a load path the loads analysis cannot see — a drag brace, a side brace, a trunnion — and the case that governs one member is not the case that governs another. Ranking 33 conditions on a single scalar therefore answers a question nobody asked, and answers it in a way that **removes** the case a reader needs. So Section 12 and Appendix F carry **every** case; the summaries below are a reading aid and are labelled as one, never a selection. This is the same principle as OR-174 approached from the other side: there, a case the analysis cannot stand behind is excluded and said to be; here, no case may be excluded at all. | **OR-57**, OR-174, rule 6 |
| **OR-185** | **Where a family critical is named it is named twice — nose and main** *(owner: "nose and main")*. `_critical`'s `max(main, nose)` is not a tie-break, it is a comparison between two different gears: the winner sizes one and the loser's larger reaction on the other gear is discarded. F2 is that defect with a number on it. Each FAR family now yields **two** summary conditions, the largest main-wheel reaction and the largest nose-wheel reaction, each ranked on its own gear's full three-component magnitude, and a family whose nose reactions are all zero yields the main row only. The shipped condition set goes from **40 to 42**: only the 23.479(a) and 23.493 families load both gears, so the other four yield one row each, which is itself the measurement that the single-scalar rank was discarding a real condition rather than a duplicate. Fixed in the module rather than in the report *(owner: "C1 b")*, so that the CSV, Results Review, the GUI and the document are corrected together — fixing the PDF and leaving the CSV wrong is publishing two answers. | rule 3, rule 4, **rule 6** |
| **OR-186** | **Each structural element gets its own applied-load CSV, shaped for the loads it carries; the case index stays a register of identities and says so** *(owner: "a separate CSV file for each structural element … then they can be specifically shaped for the loads presented in that csv")*. F1's 344-of-347 is what a single flat row shape costs when four of the five producers do not speak it. The wing, fuselage and both tails already have theirs through `applied_load_csv`; this decision adds the **landing gear** and the **engine mount** and makes the rule general. The common spine is the owner's own list — *case, load application point, all six load components in the global frame, and SF* — and each file may carry the columns its element needs beside it. The case index is **not** reshaped here: it is a cross-module schema change touching every producer, and it is filed with its measurement. What changes is that Section 12 states plainly where the loads are, so a reader meeting a blank load column is not left to conclude the case carries nothing. | **rule 4**, OR-141, OR-180, note 38 GF-6 |
| **OR-187** | **The load factor the reactions ran at is stated beside the one LGFACTOR computed, and the difference is not treated as an error** *(owner: "the user can overwrite the computed, that is the user's decision")*. 12.2 prints both pairs — the drop-test energy `N`/`NLG` and the governing pair — names which governed, and where they differ says so in one sentence. `below_energy_caution`'s warning is printed where the module raises it (an entered `N` **below** the energy estimate, as `cessna_210` has), because a user's decision is still a decision a reader should see; it is a statement, not a refusal. This is OR-57's rule applied to a scalar instead of a case list: a section that presents an entered number as a computed one describes an analysis nobody ran. | **OR-57**, note 37 LF-6 |
| **OR-188** | **Appendix F is the gear's applied set, all 33 cases, at the point design note 39 names for each** *(owner: "Q2 Ok"; "C3 33, with 25-33 flagged"; "C2 use both points but the one that is applicable for the case")*. One row per case per **loaded** leg, in the `AppliedLoad` shape every other appendix uses, so B through F are one style. The application point is **not** re-decided here: `gear_loads.application_point_of` already owns Appendix A's own printed point-of-load column and answers `AXLE` or `GROUND_CONTACT` per case, which is exactly *"the one that is applicable"* — the row states that point and names it. A wheel reaction is a **pure force**, so `Mx`/`My`/`Mz` are structurally zero and are printed rather than blanked, on OR-140's rule. The delivery to the gear reference point — the second point, and the transfer moment it produces — stays in 12.3's free body, which is where a load applied at one point and delivered to another is one statement. Cases **25-33 are carried and flagged**: they are 23.499 gear-design conditions with no airplane in equilibrium, which is why the balanced deck carries 1-24, and omitting them from a set the owner asked to be complete would repeat F2 at the family level. | OR-141a, **design note 39 AP-1/AP-2**, OR-140 |
| **OR-189** | **Three attitude figures, drawn from the manual's own, each naming the cases that use it** *(owner: "three figures that cover all cases would be very helpful")*. Appendix A prints two — p234's `3 WHEEL LEVEL LANDING` and p235's `BRAKED ROLL` — and sloads computes **three** attitudes, so the third is drawn rather than left to prose. Each figure carries what the manual's carries: the fuselage station line, the ground line, the ground angle, the CG at its station, the wheel at its rolling radius and axle position, the resultant's direction, and `K` / `GAMMA` / `BETA` where the attitude has them. What is added is the owner's requirement that they *"identify which cases use which geometry"*, which the manual leaves to the reader: **level, compressed axle — cases 1-6 and 10-12; tail-down, compressed axle — cases 7-9; ground roll, static axle — cases 13-33**. That mapping is `landing.attitude_of`'s, read rather than restated. | OR-7, OR-32, rule 3 |
| **OR-190** | **The OR-15 admission of 2026-09-07 (the frozen set), scoped to `modules/landing.py` alone** *(owner: "Q5 granted"; "C1 b")*. Two changes and nothing else. **(1)** `_geometry` becomes public as `landing_geometry` so 12.1 can print the p230 oracle — `K`, `GAMMA`, the three ground angles, `BETA` and the AP/BP/DP/CP lever arms — which is a rename and a docstring, no arithmetic touched. **(2)** `_critical` becomes `critical_reaction`, gains a gear argument, and `run` emits the nose and main summaries of OR-185 — public because the report ranks the same set for its own reading-aid table, and a report reaching into a module's private name is a second owner wearing a disguise. Explicitly **not** admitted and not touched: `landing_reactions`, `landing_load_factor`, `_geometry`'s body, and any refactor, rename or reformatting elsewhere in the file. Re-pinned in the frozen manifest with the scope recorded beside the hash. The consequence stated and accepted: the shipped condition set grows from 40 to 42, so the landing CSV and every digest taken over it move. | OR-13, OR-15, OR-181 |
| **OR-191** | **Section 4's forward reference is now satisfied, and that is asserted rather than assumed.** `_body_advisories` tells the reader that the three-wheel level landing is analysed in Section 12. Before OR-185 it was not — the condition existed in the matrix but no summary named it, and the matrix was not in the document at all. A cross-reference is a promise the target keeps, so the gate holds Section 12 to containing, by name, every condition another section sends a reader to it for. | OR-113, rule 3 |
| **OR-192** | **All three shipped reports carry this section, and the concept one carries its own warning.** `ga6_normal`, `baron_58` and `concept_regional_jet` all produce Section 12 — the first section since Section 2 that every shipped report contains, and the reason this iteration needs no new fixture. `concept_regional_jet` is category C, so the module's concept note travels with the conditions: an unverified extrapolation past the FAR23 band, with 23.473(g) warn-only rather than refusing. Its entered `N` is **exactly** the 23.473(g) floor of 2.67 while its energy estimate is 2.3755, which is the sharpest illustration in the fixture set of why OR-187 prints both. A project with no `landing` slice — `concept_heavy` — renders the ABSENT state, which is correct: it is missing an input, not exempt from a regulation, so OR-178's `NOT_APPLICABLE` is **not** used here. | OR-37, OR-178, OR-182 |

### Gates added by this iteration

- **G-OR-123** — *(OR-184)* Section 12 and Appendix F contain **all 33** LANDLOAD
  cases on every shipped example, asserted by case number, and no case present in
  the module's result set is absent from the document. The gate that a
  down-select cannot creep back in.
- **G-OR-124** — *(OR-185)* every FAR ground family with a non-zero nose reaction
  yields two summary conditions; the nose row is ranked on the nose magnitude and
  the main row on the main magnitude; and on all three shipped examples the
  23.479(a) nose row is **case 2**, a three-wheel level landing (measured
  2026-09-07: case 2 on all five fixtures that carry gear geometry). Asserted against a
  re-rank of the full matrix rather than a stored number.
- **G-OR-125** — *(OR-186)* the landing and engine applied CSVs exist, carry the
  common spine (case, application point, six components, SF), and their rows are
  the same `applied_loads` records the appendix prints — so file and table cannot
  disagree. Extends G-OR-90 to the two new components.
- **G-OR-126** — *(OR-187)* where the governing load factor differs from the
  energy estimate, 12.2 prints both and names which governed; where
  `below_energy_caution` fires, its sentence appears. Asserted on `ga6_normal`
  (entered above) and on a project entered below.
- **G-OR-127** — *(OR-188)* every Appendix F row states a point that
  `application_point_of` names for its case, compared through that owner rather
  than against a literal; cases 25-33 are present and carry the
  no-airplane-equilibrium flag; every row's moments are zero.
- **G-OR-128** — *(OR-189)* three figures, each naming its attitude, its axle
  state, its ground angle and its case list, with the case lists partitioning
  1-33 exactly — asserted against `landing.attitude_of`, so a change to the
  attitude map fails here rather than printing a figure that claims cases it does
  not cover.
- **G-OR-129** — *(OR-191)* every condition another section forward-references by
  name appears in the section referenced. Written against Section 4's
  three-wheel-level-landing advisory, which is the instance, and swept across
  `_body_advisories`.
- **G-OR-130** — *(OR-183/OR-192)* Section 12 renders on all three shipped
  examples with its three subsections; a project with no `landing` slice renders
  ABSENT and **not** `NOT_APPLICABLE`; and `IMPLEMENTED` now covers every entry of
  `analysis_steps()`, which is the gate that the analysis body is complete.

### Filed, not fixed here

- **The load-case index carries no loads for 344 of 347 rows.** Measured above
  (F1). Its six load columns are the engine-mount shape and four of the five
  producers cannot express themselves in it. OR-186 answers the *deliverable*
  question — each element gets a file shaped for its own loads — but leaves the
  index itself unchanged, because reshaping it is a schema decision touching
  every producer and every consumer of `load_cases_csv`. The candidate answer is
  that it becomes an index in name as well as in fact, with the load columns
  removed and the per-element files carrying the loads. Filed against 0.9.x.
- **No gear kinematic model.** Section 12 delivers the reaction, its point, the
  attitude and what arrives at the reference point. It does **not** state drag
  brace, side brace, trunnion or axle bending, and 12.3 says so — the same
  sentence the GUI page already carries. This is a scope boundary, not a defect,
  and is recorded so that OR-184's "no down-select" is read as what it is: the
  loads analysis handing a complete set to a discipline that can rank it.
- **Tricycle gear only.** `UG Table 2.1`, and unchanged by this iteration. A
  tail-wheel airplane has no representation in the schema, so there is nothing to
  state per project; the limitation belongs to Methods and limitations.

## 23. Iteration 10 — Appendix A, the V-n condition register (OR-193 … OR-203)

**Status: AGREED 2026-09-07 (owner, in session).** Drafted from the owner's
instruction — *"I have decided to change the contents of the report's Appendix A.
It will now contain the tables that have each of the conditions identified in
V-n; this is the oracle document McMaster tables on page 179 (which has the
definition of each mass case: CG, WT, XCG, ZCG) and then pages 180 through 185
which have Case, Condition, V EAS kts, NZ, Alpha, G CORR, CL, M(W+F), LZW, LT,
DX. Add a column for CG (CG1 etc) and altitude. Also add columns to indicate if
this case is W, F, HT, VT, Engine, and that case id — example W-01."* — and from
the eight answers that followed: *"Q1 do not repeat information that is in other
sections except the mass case definition. Q2 drop it and just reference the json
file. Q3 engine drop. We don't have any cases defined as thrust on or off, are
all assumed off? Add configuration (flap position). Q4 landscape is fine. Q5
flat. Q6 CG case id; for the baron_58 and regional jet can we convert them to an
id, the CG table could add the expanded name. Is this too big a change? Q7 yes.
Q8 add config."*

*Measurements taken 2026-09-07 against the three shipped reports —
`ga6_normal`, `baron_58`, `concept_regional_jet` — and against `atr42_100` and
`concept_heavy` where a fourth and fifth shape was needed. Quoted where they
carry a decision.*

**This is the first appendix that is not a projection of a section.** B through F
each restate one section's loads at a finer grain, and their state follows that
section's (`Appendix.step_key`). Appendix A follows no section: it is the matrix
every section selected *from*, and its reason for existing is that the document
currently asserts 23 critical conditions without ever showing the reader the 80,
180 or 200 they were chosen out of. A selection whose candidate set is not
published is a claim, not a result.

### What the module already produces

`FLTLOADS` (`modules/flight_envelope.py`, Ref 1 Ch 6-8) balances every
(configuration x altitude x CG case x condition) point and returns a `VnPoint`
carrying **exactly** the manual's printed columns — `v_eas_kt`, `nz`,
`alpha_deg`, `g_corr`, `cl`, `m_wf`, `lzw`, `lt`, `dx` — plus the three the owner
asked to be added as columns, `config`, `cg` and `altitude_ft`, which are already
fields rather than block headings. **Nothing in this iteration recomputes a
load.** The arithmetic is untouched; what changes is that a matrix which has
always existed in memory is published.

Envelope sizes, measured: **80** points on `ga6_normal` (1 config x 1 altitude x
4 CG x 20 conditions), **180** on `baron_58` (3 altitudes x 3 CG), **200** on
`concept_regional_jet` (2 altitudes x 5 CG). McMaster's own example is 280.

### Three findings

**A1 — the critical set is 8 to 22 per cent of the matrix, and the rest is
invisible.** Of 80 / 180 / 200 balanced points, **18 / 17 / 17** are ever named
as a critical condition. Sections 3 through 6 print the survivors and the
document nowhere states what they survived. The appendix is the candidate set;
the component columns are the survivors marked *within* it, which is why they are
columns on the matrix rather than a second table beside it.

**A2 — the V-n-to-case-id stamp is lossy, and this appendix is its first
reader.** `select._stamp_case_refs` writes `p.case_ref = ref` onto the
originating point, but a point may be selected more than once: on `ga6_normal`
V-n case **14** is `VT-01`, `VT-02` **and** `VT-03`; case **74** is `HT-03` and
`HT-09`; case **30** is `W-03` and `F-01`. Last write wins and the rest are
dropped. Measured on all three: **4, 5 and 4** points are multiply selected.
Nothing shipped is wrong today — `VnPoint.case_ref` has one writer and, outside
serialisation, **no reader in `sloads/`** — so this is a latent defect whose first
consumer is the table being built here, which is why it is fixed here rather than
ranked against the fidelity backlog under rule 6.

**A3 — the register of decisions is missing a decision that shipped code
cites.** `report/render.py:683` documents `_running_locations` as *"a defect fix
(note 44 OR-193)"*, `changes/the-ground-delivers-every-case.history.md` announces
§22 as **OR-183 … OR-193**, and backlog row 38 cites OR-193 — but §22's heading
reads OR-183 … OR-192 and its decision table has no OR-193 row. The same
docstring claims the fix is *"gated"*; the only thing holding it is the frozen
imperial baseline, which fails as a **changed number** rather than as a **stated
property**, so a future change that moved the engine locations *and* regenerated
the baseline would pass. A register that a shipped citation can point outside of
is not a register.

### Decisions

| # | Decision | Amends |
|---|---|---|
| **OR-193** | **A condition that states no point of application takes the point of the condition it follows, not the first in the set.** *(Recorded here, in the register, for the fix that shipped in §22 on 2026-09-07 — A3.)* Two of the six engine-mount conditions carry no `loc_*` values while the four beside them for the same engine do; the old fallback reached for the first location in the whole set, so every multi-engine fixture printed the right-hand engine's sudden-stoppage torque and its four gyroscopic sub-cases at the **left-hand** engine's butt line — ten rows on `atr42_100` and `dhc8_dash8`, fifteen on `concept_regional_jet`. Producers emit one engine's conditions together, so the previous location is that engine's. Carried at the render boundary because `modules/engine.py` is frozen for 0.8.2; the producer stating the point on every condition it emits is the proper repair and is filed (backlog row 38, #210). | OR-140, rule 4 |
| **OR-194** | **Appendix A becomes the V-n condition register, and the input echo is retired rather than relettered** *(owner: "drop it and just reference the json file")*. OR-50 reserved slot A for an input echo and argued the reservation on lettering stability: an appendix that appears later must not push its neighbours along. That argument is spent — the slot is being **filled**, not vacated, so B through F do not move and no issued document disagrees with its reissue. The echo itself is dropped on the owner's ruling and the reason is good independent of the ruling: `project.json` **is** the input echo, exactly and machine-readably, and a table transcribing it is a second copy that can disagree with the first. The document names the file. `GROUP_PROSE`'s `{input_echo}` substitution and `INPUT_ECHO` go with it, since a formatter with nothing to format is the decoration rule 3's precedent warns about. | **OR-50**, OR-32 |
| **OR-195** | **Appendix A repeats nothing another section carries — except the mass cases, and that exception is the key its own CG column needs** *(owner: "do not repeat information that is in other sections except the mass case definition")*. p179 is headed *V-n Data* and holds five blocks: geometry, structural speeds, altitudes, aero coefficients, and the CG tables. Four of the five are Section 2's — §2.1 Geometry, §2.3 Structural Design Speeds, §2.4 Flight Envelope — and are **not** reproduced. The fifth crosses because the condition table's `CG` column is unreadable without it. Measured while deciding: §2.2 *already* prints `Case | Role | Weight | Xcg (in) | Xcg (% MAC) | Zcg | Analysis`, a strict superset of p179's four columns — so the exception the owner carved out is the one place the document already had covered. Appendix A therefore carries the **key**, not the copy: id, name, WT, XCG, ZCG, the five columns the condition rows resolve against. | OR-140, rule 3 |
| **OR-196** | **One flat table, landscape, ordered CG then configuration then altitude then case** *(owner: "Q4 landscape is fine", "Q5 flat")*. McMaster prints a block per (config, altitude, CG) under a `FOR CG1 FS= 85.1 WL= 93` heading; the owner's added CG, altitude and configuration columns make that heading redundant, and a block structure whose heading is also a column is the same fact stated twice. The row order **is** the manual's — the blocks flattened in place — so a reader holding p180 against the appendix reads the same sequence. Columns: `CG`, `Config`, `Altitude`, `Case`, `Condition`, `V (EAS)`, `NZ`, `Alpha`, `G corr`, `CL`, `M(W+F)`, `LZW`, `LT`, `DX`, `NX`, `W`, `F`, `HT`, `VT` — nineteen, so the section is landscape, which the owner granted rather than the table being trimmed to fit. | OR-140, OR-141a |
| **OR-197** | **Four component columns — W, F, HT, VT — and no engine column** *(owner: "Q3 engine drop")*. `modules/engine.py` mints `EM-` ids from engine geometry and the prescribed factors of 23.361 / 23.363 / 23.371; `modules/landing.py` mints `LG-` from ground attitudes. **Neither reads the V-n matrix**, so neither can ever appear in a V-n row: an engine column would be structurally empty on every project that could ever exist, and a permanently blank column reads as a data gap rather than as the fact that engine mount loads are not flight-envelope conditions. The section says so in one sentence instead, which is OR-140's rule — state the absence, do not print it as a hole. | OR-140, rule 3 |
| **OR-198** | **NX is printed beside DX, and the thrust assumption is stated** *(owner: "we don't have any cases defined as thrust on or off, are all assumed off?")*. Answered from `_balance` (`flight_envelope.py:152`): the balance solves **Z-force and pitch only** — no thrust term, and no X-equation. But the drag does not vanish. `select.py:343` and `wing_inertia.py:376` both take **`NX = -DX / W`** and hand it to WINGINER as a longitudinal inertia load factor, so the airplane *is* in X-equilibrium, by d'Alembert: the whole of DX is reacted as a deceleration. Thrust is therefore **off, consistently and by construction** — a modelled assumption, not an omission. NX is printed because it is the number that says where the drag went, because it is what the wing inertia actually consumes, and because DX alone invites a reader to conclude the airplane is unbalanced longitudinally. Adding power is a change to the balance — a reduced NX and a thrust-line pitching moment about the CG, for which design note 53's `thrust_line_fwd`/`thrust_line_aft` already supply the geometry — and is **filed, not done here**. | OR-57, **rule 6** |
| **OR-199** | **A CG case carries a derived positional id; its name remains its identity** *(owner: "CG case id … for the baron_58 and regional jet can we convert them to an id, the CG table could add the expanded name. Is this too big a change?")*. It is not: it is a display-only derived view with one owner, and nothing is renamed. `flight_cases(project)` already returns entry order, so `CG1..CGn` is that order indexed — and on `ga6_normal` the cases are *literally* named `CG1`-`CG4` in that order, so the derivation reproduces the manual exactly rather than merely resembling it. The condition table prints the id; Appendix A's mass-case table prints `id | name | WT | XCG | ZCG`; **§2.2 gains the id column** so the two agree and a reader meeting `CG1` in the appendix can find `fwd gross` in Section 2. `CgCase.name` stays the key everywhere else — `selected_case_ids`, `CaseRef.cg`, deck labels, validation and every example JSON are untouched. Stated in the appendix and gated: the ordinal is **positional**, so reordering the cases in the JSON renumbers the appendix in a reissue. That is the same property OR-50 defended for appendix letters, and it is acceptable here for the opposite reason — the id is display-only and carries no persisted reference. | OR-50, rule 3 |
| **OR-200** | **A V-n point carries every case it was selected for: `case_ref` becomes `case_refs`** (A2). A single slot cannot answer a question with four columns in it. The field is **replaced** rather than joined by a plural sibling, because it has no reader to preserve — one writer, no consumer outside `io.py` — and leaving a dead singular beside a live plural is the decoration this project removes rather than marks. `SCHEMA_VERSION` 63 -> 64, with the old singular key read into a one-element list so any persisted envelope loads unchanged. `_stamp_case_refs` appends; the emission order (wing, htail, vtail, fuselage) becomes the printed order, so `VT-01, VT-02, VT-03` reads as the selection made it. | rule 3, rule 4, M4-2 decision 1 |
| **OR-201** | **Appendix A ships `<project>_vn_conditions.csv`** *(owner: "Q7 yes")*. OR-186 made per-element applied-load files the general rule; this is the same rule one level up — the appendix's own rows, in the appendix's own shape, as a file, because a 200-row matrix is a thing a reader wants to sort rather than to page through. It is **not** an applied-load file and does not carry the `AppliedLoad` spine: a V-n point is a balanced flight state, not a load at a point, and forcing it into the six-component shape is the defect F1 measured from the other direction. Same rows, same order, same columns as the table, gated against it. | **OR-186**, OR-141 |
| **OR-202** | **Every `OR-n` cited anywhere in the tree has a row in the register** (A3). OR-193 is defined above, in this iteration's table and flagged as the fix that shipped in §22's step -- rather than by editing §22, whose heading and table are accurate for the decisions taken *there*; the citation now resolves, which is what a register owes. What stops the next one is structural rather than editorial. A citation is a promise the register keeps, in exactly the sense OR-191 made cross-section references a promise the target keeps, and the gate is the same shape: sweep the tree for `OR-n` and `G-OR-n`, and require each to be *defined* somewhere in `docs/30_future/`. OR-193 also gains the gate its own docstring already claimed, asserted as the **property** — a condition with no point takes the point of the condition it follows, and on a multi-engine airplane that is the same engine's — rather than as a frozen digest that a regenerated baseline would wave through. | **OR-191**, rule 3, rule 5 |
| **OR-203** | **The OR-15 admission of 2026-09-07 (the frozen set), scoped to `modules/select.py` and `modules/wing_inertia.py`** *(owner: "OR-15 granted")*. Three changes and nothing else. **(1)** `_stamp_case_refs` **appends** to `VnPoint.case_refs` instead of assigning `case_ref`, and clears the list first so stamping one envelope twice is the same as stamping it once — the OR-200 fix, at the one line that was losing the ids. **(2)** `select._condition`'s `nx = -p.dx / _cg_weight(weights, p)` and **(3)** `wing_inertia._case_from_vn`'s `nx = -vp.dx / weight if weight else 0.0` both become `inertia_drag_factor(...)` — the OR-198 owner, one import each. **No arithmetic is touched by any of the three**, and the zero-weight branch is preserved exactly: `_cg_weight` raises before it can be reached in `select`, and `wing_inertia`'s tolerant `0.0` is the function's own answer. Explicitly **not** admitted and not touched: every selection criterion, `htail_balance`, `elevator_load`, the v-tail subroutine, the wing slot table, and any refactor or rename elsewhere in either file. Re-pinned in the frozen manifest with the scope recorded beside each hash. The consequence stated and accepted: **none** — no delivered load moves, and the Imperial digests are unchanged, which is the measurement that says so. | OR-13, **OR-15**, OR-181, OR-190 |

### Gates added by this iteration

- **G-OR-131** — *(OR-194/OR-196)* Appendix A renders on all three shipped
  examples with **one row per V-n point** and no others — the count equal to the
  built envelope's, asserted against `default_envelope` rather than a stored
  number — in the agreed column order, in the manual's own row order, and the
  section is landscape. `INPUT_ECHO` and the `{input_echo}` substitution are gone,
  and no rendered document contains a dangling reference to them.
- **G-OR-132** — *(OR-195)* no table in Appendix A carries a column signature
  another section's table already carries, **except** the mass cases; swept across
  the whole document rather than asserted against a list, so a later section that
  starts duplicating the matrix fails here.
- **G-OR-133** — *(OR-197/OR-200)* every case id stamped on any critical condition
  appears in exactly one Appendix A row; every multiply-selected point shows **all**
  of its ids, asserted against a fresh `build_critical` rather than a literal, with
  `ga6_normal` case 14 carrying `VT-01`, `VT-02` and `VT-03` as the named instance;
  and no `EM-` or `LG-` id appears anywhere in the appendix.
- **G-OR-134** — *(OR-198)* every row's `NX` equals `-DX / W` for that row's CG
  case, compared through the same owner `select` and `wing_inertia` read, so a
  change to the inertia-drag convention fails here rather than printing two
  answers; and the thrust statement is present in the appendix body.
- **G-OR-135** — *(OR-199)* the id map is a bijection over `flight_cases` order;
  every CG printed in the condition table appears in the mass-case table **and** in
  §2.2's table under the same id; and on `ga6_normal` every derived id equals the
  case's own name, which is the manual's numbering reproduced rather than imitated.
- **G-OR-136** — *(OR-201)* the CSV's rows are the appendix's rows — same count,
  same order, same values — compared through the builder, so the file and the
  table cannot disagree. Extends G-OR-90's rule to a non-`AppliedLoad` shape.
- **G-OR-137** — *(OR-202)* every `OR-n` and `G-OR-n` cited anywhere under
  `sloads/`, `tests/`, `docs/` or `changes/` is defined in a design note under
  `docs/30_future/`. The gate that would have caught A3.
- **G-OR-138** — *(OR-193/OR-202)* a condition carrying no point of application
  takes the point of the condition it follows, and on every multi-engine fixture
  that point is **the same engine's** — asserted per engine against the emitted
  grouping on `atr42_100`, `dhc8_dash8` and `concept_regional_jet`, as a property
  rather than as a digest.

### Filed, not fixed here

- **No thrust in the balance (OR-198).** Answered rather than changed: thrust is
  off, and the drag is carried as `NX = -DX/W`. Modelling power would change every
  balanced point — a reduced NX and a thrust-line pitching moment about the CG —
  and is a physics change to an oracle-locked module, so it is a design note of
  its own, not a column. Its effect on a delivered load is unmeasured, so under
  rule 6 it is parked *without* a rank until someone measures it; the measurement
  is the first piece of work, not the last.
- **`modules/engine.py` still states no point on two of six conditions.** Backlog
  row 38 (#210), unchanged by this iteration. OR-193 is now in the register and
  OR-198's sibling gate holds the boundary fix; the producer repair still waits on
  the OR-13 freeze lifting.
- **The load-case index still carries no loads for 344 of 347 rows.** Backlog row
  37 (#209), unchanged. OR-201 adds a sixth per-element file and does not reshape
  the index.
