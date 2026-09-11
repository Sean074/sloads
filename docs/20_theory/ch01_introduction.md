# Chapter 1 — Introduction: What sloads Computes, and How to Read This Manual

This manual is written for an engineer using sloads: what the suite computes,
by what method, under what assumptions, and where each method stops being
valid. It explains; it does not own. Every normative contract it describes has
a single authoritative source elsewhere — the conventions charter
([`../10_standard/CONVENTIONS.md`](../10_standard/CONVENTIONS.md)), the
per-module spec ([`../10_standard/PROGRAM_SPEC.md`](../10_standard/PROGRAM_SPEC.md)),
and the theory-sources hub ([`00_theory_sources.md`](00_theory_sources.md)) —
and where this manual and an owner disagree, the owner is right and the manual
has a defect.

## 1.1 What sloads is

sloads is a modern Python replication of the **FAR 23 LOADS** suite (Hal C.
McMaster, Aero Science Software): the programs that compute the structural
design loads a small airplane must sustain under 14 CFR Part 23 Subpart C.
Two modes share one code path:

- **The FAR 23 replication core** is *oracle-locked*: where the manual prints a
  figure (Appendix A, the 6-place GA single), the port reproduces it within
  ±0.1 %, page-cited in the test. The methods are the manual's — modernized in
  arithmetic (`math.pi`, clean equations), never in physics.
- **Concept mode** (`category="C"`) is a *superset* for configurations outside
  the FAR 23 caps (weight, seats, speeds). It adds no second method: on GA
  inputs it reduces exactly to the replication core, and above the calibration
  band — where no printed oracle can exist — it is validated by stated physics
  closures instead ([`00_theory_sources.md`](00_theory_sources.md) §Oracle
  status; chapters 9–11).

The primary deliverable is the **full-span balanced free-free airplane model**
(chapter 9): aero and inertia together, left and right cases, exported as
solver bulk data with a mass model. The per-component distributions (wing,
empennage, fuselage — chapters 4–6) are analysis views of the same physics.

## 1.2 The analysis pipeline

The suite is a set of pure calculation modules over one shared project bundle;
data flows one way:

1. **Design airspeeds and the V-n envelope** (chapter 3) — from weight,
   geometry and category to VS/VA/VC/VD/VF and the flight-envelope corner
   points and gust lines: the **case inventory**.
2. **Case selection** — the wing and fuselage paths prune that inventory to
   the critical conditions before analysis (SELECT, chapter 4 §"Cases
   analyzed"); the empennage and ground families instead derive their cases
   from their own FAR conditions and envelope the results *after* analysis
   (chapters 5 and 8).
3. **Component loads** — spanwise and chordwise distributions per component
   (chapters 4–7), each condition carrying its FAR reference and case
   identity.
4. **The balanced airplane** (chapter 9) — the applied set assembled on the
   mass model (chapter 10) and closed in six degrees of freedom by one
   rigid-body field.
5. **Export** (chapter 11) — `FORCE`/`MOMENT`/`CONM2` bulk data for the sbeam
   solver, with equilibrium re-verified from the emitted card text and by an
   independent solve.

Module-by-module inputs and outputs are `PROGRAM_SPEC.md`'s; the module names
map to the original `.BAS` programs there.

## 1.3 Reading the output: every load is LIMIT

**Every load sloads delivers is a LIMIT load.** The 14 CFR 23.303 factor of
safety (1.5) is **stated per case and applied nowhere** — the sizing analysis
applies it, not the loads program. The `-ULT` marker survives only on the two
families the regulation prescribes already ultimate (23.367(a)(2) sudden
engine stoppage, 23.561(b) emergency-landing inertia — `ULT SF=1.0`, apply
nothing further). A condition that is not a load case prescribes no factor and
renders `N/A`. The full contract, its single-source owner
(`sloads/safety_factors.py`) and its guards are `CONVENTIONS.md` §3; the
regulatory basis is [`00_theory_sources.md`](00_theory_sources.md) §Limit vs.
ultimate. If a number you read from any sloads artifact surprises you by a
factor of 1.5, read that section before anything else.

Internal calculation is Imperial (inches, pounds — the original programs'
units); SI is a presentation channel converted at the boundary, and solver
decks use the consistent N·mm/MPa channel. Every deliverable file states its
unit set in band (`CONVENTIONS.md` §2).

## 1.4 How each chapter is organized

The load chapters (3–11) follow one template:

- **Scope & regulatory basis** — what the chapter covers and the FAR sections
  that prescribe it.
- **Cases analyzed** — where this component's conditions come from: the
  envelope inventory via SELECT, or the family's own FAR conditions. Every
  case is traceable to one of the two.
- **Method & equations** — the analysis, with symbols, citing Reference 1
  chapter and page.
- **Assumptions & limitations** — stated, not implied: what the method cannot
  see, which direction an omission errs, and the recorded decisions behind
  each.
- **Worked example** — Appendix A's airplane where the manual prints one.
- **How it is validated** — the oracle (±0.1 %, page-cited) where a printed
  figure exists; otherwise the stated closure gate, in plain language, with
  the step/decision identifiers demoted to citations.
- **Sources** — the pages, regulations and design notes of record.

Chapters not yet written in full carry the template with their assumptions,
limitations and validation pointers populated first — those are the sections
an engineer needs before trusting a number.

## 1.5 The two front-ends (and the one calc package under them)

sloads ships two Streamlit front-ends plus a CLI, and **no physics lives in
any of them**: the calculation package is I/O-free, and the front-ends are
interchangeable shells over the same modules. Every equation, assumption and
limitation in this manual therefore applies identically regardless of which
surface produced the number.

- **The main app** (`app/Home.py`) is the workflow-driven front-end for doing
  loads work: project definition through balanced cases and export, ordered by
  the step graph.
- **The oracle GUI** (`oracle_app/Oracle.py`) is the replication and
  verification workbench: it mirrors the original FAR 23 LOADS program
  sequence so a user can walk the Appendix A airplane against the printed
  pages. Its fidelity target is the **analysis contract** — the consumed
  values and computed results — not the original's prompt-by-prompt interface
  (ruling C210-15, `docs/50_reviews/2026-08-23_c210_oracle_gui_build_review.md`).

A feature present in one front-end and not the other is a user-interface
difference, documented with the front-ends (`../10_standard/GUI_USER_GUIDE.md`),
never a difference in analysis.

## 1.6 The validation vocabulary used throughout

Three terms recur in every "How it is validated" section, defined once in
[`00_theory_sources.md`](00_theory_sources.md) §Oracle status and §Oracle
provenance:

- **Oracle-locked** — asserted against a printed Appendix A figure within
  ±0.1 %, page-cited.
- **Closure-locked** — no printed figure exists (Appendix B is not bundled;
  concept mode is above the printed airplane); the gate is sub-formula
  exactness against the `.BAS` source plus a stated physics closure or an
  independent producer.
- **Provenance** — every oracle cell states where its number came from
  (transcription / OCR / absent / back-solved), and no gate re-derives the
  rule it checks (rules P-1/P-2).

The per-module status table — which of these each module carries — is the hub's
§Oracle status, the single authoritative statement; this manual points at it
and never restates it.
