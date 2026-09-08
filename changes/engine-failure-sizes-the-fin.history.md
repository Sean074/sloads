## Step 164 — The engine that fails is the one that sizes the fin (design note 44 §21, tier L, 2026-09-07)

**Objective.** Build Section 11, One Engine Inoperative — the eleventh section of
the oracle report and the only one whose subject is an *event* rather than a
state of the airplane. The section was scoped, and the scoping turned it into
something larger: measuring its loads against Section 6's showed it could not be
a report section alone.

**Agreed first.** Design note 44 **§21** (**OR-171 … OR-182**, gates **G-OR-113 …
G-OR-122**), settled with the owner in session before any code, from eleven
answered questions across two rounds. The note carries **two OR-15 admissions**
(**OR-181**), both narrow and both granted after a prototype had established
exactly what they needed to cover: `modules/one_engine_out.py` for four named
changes with `simulate` and `_moment` untouched, and `modules/select.py` for one
insertion point. Explicitly not admitted and not touched: `tail_span.py` and
`taildist.py` — the prototype proved they needed nothing.

**The measurement that reorganised the step.** LIMIT against LIMIT, total fin
load:

| Airplane | Largest SELECT fin case | 23.367 at VD | Ratio |
|---|---|---|---|
| `baron_58` | 1357.2 lb (YAW 15 NEUTRAL) | **2155.8 lb** | 1.6x |
| `atr42_100` | 4878.1 lb (YAW 15 NEUTRAL) | **12 829.3 lb** | 2.6x |
| `dhc8_dash8` | 4527.1 lb (SIDE GUST) | **14 780.8 lb** | 3.3x |

On every twin in the fixture set the one-engine-out case is the **governing** fin
load, by up to 3.3x, and the fin was sized without it: 23.367 was in no critical
set, no distribution, no appendix and no deck. Under rule 6 a defect with
first-order effect on shipped content outranks the iteration that found it, so
the section and the admission landed together. A document that printed a
governing load in Section 11 while Section 6 five pages earlier called a smaller
one critical would have published the contradiction rather than fixed it.

**Deliverables.**
- `modules/one_engine_out.py` — `fin_conditions` publishes the recovered cases as
  fin design conditions; `_fin_cases` is the one enumeration the section and the
  envelope both walk, so the printed cases and the admitted ones cannot come from
  two sets. Every entered engine is failed in turn, signed by its butt line.
- `modules/select.py` — `_with_engine_failure`, one insertion point in
  `default_critical`, idempotent because that function serves a persisted set as
  readily as a computed one.
- `report/oracle_content.py` — `SectionState.NOT_APPLICABLE`, ranked above
  `ABSENT`, its reason read from `applicability.step_not_applicable`.
- `report/oracle_sections.py` — the section, in three subsections, with the load
  table, the transient-response table and six figures.
- `safety_factors.shared_basis_factor` — the OR-118a per-table basis rule, given
  one owner and read by both the document and the export.
- `docs/10_standard/PROGRAM_SPEC.md` ONENGOUT, `docs/20_theory/00_theory_sources.md`
  C9, and the backlog row for the 0.9.x ultimate down-select.

**Test.** **G-OR-113** is the one that matters: Section 6 and Section 11 must
name the same critical fin case, which is the whole argument for OR-172 written
as an assertion. Beside it: every admitted case reaches the chordwise
distribution, the spanwise distribution, the appendix and the deck, asserted by
case ID through all four; a non-recovering case reaches **none** of them, checked
in both directions on `atr42_100`, whose VS case does not recover while its VC
and VD cases from the same run do; the published aero state reconstructs the
split it came from, each method through its own large-deflection factor; and a
mixed-basis file keeps a plain header while an all-ultimate one is marked. Suite
green — 3720 passed — ruff and mypy clean.

**Key decisions.** OR-172 is the step: the 23.367 cases are fin design conditions
and travel with them, which cost nothing downstream because ONENGOUT already
published the `LT25`/`LT50` split at the stations `taildist` and `tail_span`
distribute from. OR-174 is its necessary limit — a load at the simulation bound
is not a design load, and an envelope that absorbed one would have accepted a
number nobody has; such a case is printed in full, referred to stability and
control, and excluded. OR-178 was found rather than planned: implementing the
section would have dropped `ga6_normal` from "not yet implemented" to *"Not
analysed — the inputs this section needs are not present"*, which is false about
a single-engine airplane, so "not applicable" became a state of its own with the
predicate that already existed as its owner. OR-173 refuses to mirror: one engine
gives the fin one sense, and asserting the other would be the report minting a
case the analysis did not run.

**What this step states rather than solves.** Two consequences of a transient
having no V-n point are carried in the results' own notes and left there. The
fin's lateral inertia relief is switched off on exactly the cases that govern —
safe, because the relief is unconservative and worth 0.7-1.8 %. On a **T-tail**
the concurrent horizontal-tail tip transfer cannot be resolved for the same
reason, which on a T-tail twin means the case that sizes the fin is the case
whose tip load is missing; that is design note 51's, with the rest of the T-tail,
and it is why `atr42_100` does not join the shipped report set until note 51
lands (OR-182).
