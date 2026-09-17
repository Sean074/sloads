# Backlog — Open Work & Development Plan

The authoritative list of **open** items, mission-tagged, in one order — the
**priority table** below; item bodies follow it. Rules of the road (closure
tiers, definition of done, the removal rule, naming) are in
[`../../CLAUDE.md`](../../CLAUDE.md) and restated once above the table; they
are not repeated here. Off-mission items live in [`02_parked.md`](02_parked.md);
completed work in [`../90_record/00_completed_development.md`](../90_record/00_completed_development.md)
and [`../../CHANGELOG.md`](../90_record/CHANGELOG.md); the pre-2026-08-16 running
"current state" narrative is archived in
[`../90_record/10_backlog_state_narrative_to_2026-08-16.md`](../90_record/10_backlog_state_narrative_to_2026-08-16.md).
Narratives and plans: [`01_concept_loads_plan.md`](01_concept_loads_plan.md)
(concept mode), [`03_gui_rework_plan.md`](03_gui_rework_plan.md) (GUI),
design notes per step ([`../00_INDEX.md`](../00_INDEX.md) is the guarded index
of the live set — no list is kept here; every note, whatever its status,
lives in [`../25_notes/`](../00_INDEX.md) and keeps its number (note 61 CV-3;
the status-driven move at each cut is retired); the pre-2026-08-29 "where
things stand" narrative and superseded re-cut preambles are in
[`../90_record/44_backlog_state_narrative_to_2026-08-29.md`](../90_record/44_backlog_state_narrative_to_2026-08-29.md)); architecture
[`../10_standard/PROJECT_GUIDE.md §7`](../10_standard/PROJECT_GUIDE.md); per-module
spec [`PROGRAM_SPEC.md`](../10_standard/PROGRAM_SPEC.md).

> **Invariant:** no calc-math change to the FAR23 path — Appendix A oracles pass
> throughout; concept mode reduces exactly to FAR23 on GA inputs; ultimate-load
> output rules hold; `workflow.py` stays the single source of navigation truth.

## Mission

**A demonstrated concept-loads → sbeam sizing loop** (2026-08-05): a concept
configuration goes in, distributed **LIMIT** loads come out as `FORCE`/`MOMENT`
cards (the 23.303 factor stated per subcase and applied nowhere — note 49
OR-116, confirmed by note 58 D-58.1: delivery stays LIMIT permanently, and
comparisons between cases are made on the ultimate basis), and the exported deck solves in sbeam with verified global equilibrium,
continuously in CI; the FAR23 core stays oracle-locked. **Primary deliverable
(2026-08-08):** the **full-span balanced free-free airplane model** — mass
model exported (CONM2), wing/fuselage/empennage/landing cases carrying aero +
inertia, left/right twins by reflection, and an LRA beam model exported and
importable — decisions of record plan 11 §2 (B-1…B-8), plan 12 (C-1…C-6),
note 24 (BM-1…BM-5). **Order of work (2026-08-09):** the sbeam
`FORCE`/`MOMENT` cards for the wing, body and tail cases. Items are tagged
**[E]** (essential to the loop) or **[V]** (valuable, not blocking).
**Definition of done** for a calc step: module merged and self-registered;
`tests/test_<module>.py` passing (±0.1 % oracle where printed, else a stated
closure gate in CI, benchmark-first); a page in `workflow.py`; the `Project`
schema round-trips with `SCHEMA_VERSION` bumped and older files loading; docs
synced per the closure tier.

Reference-authority hierarchy: (1) `.BAS` listings + Appendix A printed output,
(2) User's Guide CFR quotes (Jan-1994), (3) Code-manual 1990 prose.

---

# Priority table (re-cut 2026-09-11 — the single order of work)

**Re-cut 2026-09-11 (owner, in session) — three milestones where there were
two, and the whole table renumbered densely.** The 0.8.3 milestone's **named
deliverable shipped with #25** (the T-tail empennage geometry model); what
remained on it was one L-tier design note in flight (#263, note 56) plus a
21-row defect-and-polish tail with no relation to the milestone's charter —
while **note 57 sat AGREED, filed and sequenced, gated on "the 0.8.3 cut"**,
i.e. gated on those 21 rows. The table is re-cut into three bands:

* **B4 / 0.8.3 — the export contract closes.** #263's remaining slices
  (D-56.9 + D-56.1, D-56.6, D-56.8 + §8), the two rows that close superseded
  with it (#173, #176), and #16 pulled in from 0.9.0 as the pre-clean note 56
  absorbs either way. Four rows, one work package.
* **B5 / 0.8.4 — the two front-ends converge.** Note 57's D-57.8 sequence
  unchanged (#265 → #266 → #267/#268/#269 → #270), with **#241, #242 and #245
  inserted before #270** and **#255 closing superseded at it**.
* **B6 / 0.8.5 — the defect and polish cleanup, on the converged surface.**
  The remaining eighteen, in the 2026-09-09 working sequence: the hygiene
  front, the safety-factor cluster, the tail-geometry cluster, the baseline
  wave, then polish.

Four rulings, and the costs they book:

1. **#245 moves *forward*, not back — 0.8.3 → 0.8.4.** Its title is the
   convergence problem verbatim (*"the files ship only from `app/`'s export
   page"*), and note 57 §1.3 names its `data/` as `export_report`'s successor
   channel, so **#270 cannot retire that page until #245 lands**. #241 and
   #242 follow it into the band so `data/` is born corrected rather than
   corrected after shipping.
2. **The baseline wave splits, and that is the price.** It was sequenced
   #164 → #222 → #241 → #242 → #161 so digests and report baselines
   regenerate once; with #241/#242 in 0.8.4 it regenerates twice. Both are
   column *additions* to files the wave already rewrites, so the second pass
   is scripted regeneration, not rework — booked here rather than discovered
   later. The wave that stays in B6 is **#164 → #222 → #260 → #161**.
3. **The SF cluster — #179, #180, #177 — was correctness, not polish, and it is
   closed.**
   Rule 6 puts a defect with first-order effect on shipped content ahead of
   everything; both were **latent** — #179's silently-first-match hole had no
   current producer emitting the string, #180's `getattr` fallbacks were dead
   defaults that would only resurrect a flat 1.5 under a future attribute
   rename. Latent, so the deferral was lawful; named here so it was a decision
   and not a drift. **#179 closed 2026-09-15**, and its practice-4 sweep found a
   second latent misreading in the same classifier (a four-digit Subpart G
   section read as a three-digit Subpart C one). **#180 closed 2026-09-15**, and
   its sweep found the class far larger than the finding named: fifteen defaulting
   reads on the delivery side, not two — one able to print an SF of zero, four
   turning "this condition prescribes no factor" into a printed 1.5. Twice
   in one day the deferred item's own neighbourhood held more than the item —
   which is the standing argument against letting a latent defect sit: the
   deferral is lawful, the company it keeps is never inspected. **#177 closed
   2026-09-15** and made that three times: R-6 named one GUI surface, and the
   sweep found five callers running modules unstamped — the oracle report's own
   run point among them, so the shipped document printed the dataclass 1.5 on
   every condition the governing table says prescribes no factor. The fix put
   the stamp where the runner is handed out rather than at five call sites, and
   the sweep turned up a producer whose stated reference and stated factor
   contradicted each other on two shipped fixtures. The cluster's common shape,
   across all three: the *policy* had an owner from M4-8 onward, and every
   defect in it was a caller who never asked the owner.
4. **Band B2 is re-chartered, not re-ordered.** It was named "main-GUI
   development and bug correction" for a front-end #270 deletes. Its rows keep
   their order; nine of them (#29, #148, #247–#252, and #78's re-scope) close
   or re-scope at #270 under R-57.4, and #259 closes with the dashboard. What
   survives is calc, report and process work, which is what the header now
   says.

The efficiency claim is stated narrowly, because it was measured: the
convergence saves **one** tier-S row of duplicated effort (#255). `format_value`
(#161) has **zero** `app/` call sites — 164 in `sloads/report/`, three in
`oracle_app/` — the override cross-check (#243) lives at `oracle_app/form.py`,
#177 and #239 are on the survivor, and D-56.2's seven `app/views/` consumers
were already paid on 2026-09-10/11. The gain is not avoided rework: it is that
an AGREED note stops waiting on unrelated polish, each milestone carries one
charter, and the tail is triaged once against one front-end.

**Cut 0.8.3 when band B4 is empty, 0.8.4 when B5 is, 0.8.5 when B6 is, then
0.9.0 when B2 is** — superseding the 2026-08-29 "then 0.9.0 when band B2 is"
clause, which knew of no milestone between.

> **B4 is retired: 0.8.3 was cut on 2026-09-13** (tag `v0.8.3`; the release-cut
> block in
> [`../90_record/00_completed_development.md`](../90_record/00_completed_development.md)
> is the record). The band emptied, re-opened the same day and emptied again:
> #263 (design note 56) closed with #173 and #176, taking the band's last three
> rows, and the issue-bookkeeping pass that followed found statements in shipped
> content — in the oracle report, on four GUI captions, and inside the one deck
> that ships — describing the export package the note deleted. A defect with
> first-order effect on shipped content is exactly what the ordering rules put
> above every [V] item, and 0.8.3 could not knowingly cut a report that names
> artifacts it does not build, so the band took one row for #274 rather than the
> release carrying the statement. The round trip is the cut rule working, not
> drift: the band is the pre-cut queue, something entered it, and the queue
> drained before the cut instead of after it. **Band B5 (0.8.4 — the two
> front-ends converge on one, design note 57) is the milestone in flight.**

> **Band B5 re-cut 2026-09-13 (owner, in session) — design note 60.** The
> band's critical review, taken immediately after the 0.8.3 cut, found two
> things note 57 did not measure. The front-end carries **twenty** figures, not
> the four D-57.4 names — and **nine of the thirteen** plot-carrying pages are
> *shared* analysis steps, which a page-level audit cannot see going. And
> `app/views/export_report.py` is the only production consumer of
> `content.build_report`, so D-57.6 retires the **summary report** without
> naming it, taking the only statement of the axis system either front-end
> makes and the only FAR 23 Subpart C coverage matrix. The band gains two rows
> — **#239** pulled forward from B6 (note 57's gates 4 and 5 assert through it,
> so the band that depends on it cannot follow it) and the **report-merge**
> row, filed new — and re-tiers one, **#267 M → L**. Note 57's D-57.8 rule is
> unchanged and is exactly what the additions serve: the surviving GUI is
> complete before anything is removed. The table is renumbered densely with
> the re-cut, which owns it — **Pri 1–57**.

> **B5 emptied 2026-09-13 with #270.** The band's last two rows closed together:
> `app/views/` and `app/Home.py` were deleted — 22 pages, 8,461 lines — with
> `content.build_report`, the summary report's LaTeX path, `report/bundle.py`
> and the `.xlsx` workbook, and **#255** closed superseded because its fix site
> was one of the deleted files. The page set is now `workflow.gui_pages()`: the
> derived analysis steps plus the three declared non-step pages. The band's
> charter is met — there is one front-end — and note 57 §6/§8's end-of-milestone
> work is done (2026-09-13): the `app_shell/` slimming swept the five names the
> deletion left unreachable, every statement in the code that still described two
> front-ends is re-cut, and the release-state sentence stops naming a GUI that
> does not exist. R-57.5's rename **executes as nothing** — the ruling took the
> branch where the name and entry point stand, and the milestone changed the
> argument for a rename, not the decision; if it is ever taken up it is its own
> row with its own deprecation of the console script. What is left for the cut
> itself is step 3 of `RELEASE_PROCESS.md` §4 (the record roll, note 61) and
> not a row.
> **B5 is retired: 0.8.4 was cut on 2026-09-14** (tag `v0.8.4`; the release-cut
> block in
> [`../90_record/00_completed_development.md`](../90_record/00_completed_development.md)
> is the record). The band emptied once and stayed empty — the pre-cut queue took
> nothing back, which is what the 0.8.3 round trip was the exception to.
> **Band B6 (0.8.5 — correctness and tooling on the converged surface) is the
> milestone in flight**; B7, B8 and B9 (0.8.6–0.8.8) follow it in order.

> **B6 re-cut 2026-09-14 (owner, in session) — the band opened against its own
> rules.** The milestone's first read asked one question of band B2: is any row
> there 0.8.5 work by rule 6 or by B6's charter? Four are, and they move.
> **#272** — the row said to check whether #270 retired its consumer surface; it
> did not (the oracle report still enumerates the v-tail set twice), and the
> omitted case is the governing one on every shipped twin, which is first-order
> effect on shipped content. **#257** — the deck and report ride a mass model
> short of the item table with no statement a reader can see: the class #258
> and #254 are already in the band for, landing in the header #275 reworks.
> **#280** — the backlog tool has corrupted an unfiled defect's body three
> times, and this milestone runs `check` at every closure; it goes to the
> hygiene front so the fourth time is not scheduled. **#210** — stranded on
> "the OR-13 freeze lifting", which happened at the 0.8.2 cut. Two drifts
> found in the same read are corrected here: **#282** was filed to the
> milestone after the 0.8.4 cut with no band label and no row (both added),
> and #191 carried a band label and nothing else. **#283** is filed new to B2
> — the beam-model page the owner asked for — with the ruling that the report
> package does not carry the deck. Left in B2 deliberately: #29 (a review
> produces rows, and a band does not grow mid-flight), #209 (a decision first),
> #226 (a measurement first). The table is renumbered densely with the re-cut,
> which owns it — **Pri 1–40**; the band is twenty-five rows, 1 L, 8 M, 16 S.

> **B6 split four ways, 2026-09-14 (owner, in session) — the same twenty-five
> rows, cut by what each touches.** One twenty-five-row band sat every row
> behind the two decisions the owner still owes (#164's case-set shape, #275's
> D-56.4 amendment) and held the wrong shipped statements on the dev branch for
> the whole run. The record prices a cut at two commits and a baseline verify,
> so the band is cut where the work changes kind, and each cut's baseline
> regeneration is paid once. **B6 (0.8.5)** keeps the fourteen rows that need
> no decision and move no delivered number: the hygiene front, the SF cluster,
> the statement fixes and #216 — which cost the band's one exception, an
> Imperial digest regeneration on 2026-09-16 for the two aileron planforms
> WING_GEOMETRY publishes, no load or deck row among them. **B7 (0.8.6)** is
> the baseline wave
> (#164 → #222 → #260 → #161) with #210, the rows that move numbers and
> regenerate digests, gated on the #164 decision alone. **B8 (0.8.7)** is the
> polish tail (#243, #240, #256, #258, #276) — deferrable as a unit behind
> 0.9.0 if the calendar says so. **B9 (0.8.8)** pairs **#275** with **#283**,
> pulled forward from B2: the mesh-rule amendment and the beam-model page are
> one subject (what the LRA mesh is, and how the user sees and exports it), the
> page depends on the amendment, and both need a note at AGREED, so the two
> notes are written as one design pass. The one row that could have gone
> either way is #177, a display change to the SF band that stays in B6 — if it
> moves a printed value, B7 regenerates what B6 regenerated, which is accepted.
> Renumbered densely, **Pri 1–40**: B6 14 rows (2 M, 12 S), B7 5 (1 L, 3 M,
> 1 S), B8 5 (1 M, 4 S), B9 2 (1 L, 1 M). **Cut 0.8.5 when B6 is empty, 0.8.6
> when B7 is, 0.8.7 when B8 is, 0.8.8 when B9 is, then 0.9.0 when B2 is** —
> superseding the 2026-09-11 cut clause above, which knew one band where there
> are now four.

> **B7 re-cut 2026-09-16 (owner, in session) — the 0.8.6 review against an
> ATR-class aircraft sized from the LRA deck.** The review asked one question
> of the band: does a new ATR-class project, its own data entered and the LRA
> free-free deck as the deliverable, get what it needs from these five rows?
> It does not, and the gaps were measured on the current tree rather than
> quoted from the 2026-09-09 review. Two of the five rows touch the deck and
> neither moves a deck load. Three things do. **#284** is filed to B7: the one
> deck that ships states nothing about the 28 SELECT conditions it does not
> assemble, and the reason it would give names the per-component decks note
> 56 deleted — a first-order statement gap in shipped content, tier S. **#275**
> moves B9 → B7: the carry-through mesh defect is largest on exactly the
> high-wing fuselage the review was run against, and a deck row outranks the
> two report rows it now precedes. **#285** and **#286** are filed to B2 as the
> two primary twin cases the deck does not carry — the OEI fin transient, whose
> deferral to a per-component deck became an absence at note 56, and the
> engine-mount set, promoted from nine days in *Open defects* without a number.
> One correction the review makes to itself: the deck's wing set comes from
> SELECT, so the ATR's single entered wing case (now #260's E6) reaches the
> WINGINER distributions and the report, not the deck. Renumbered densely,
> **Pri 1–29**: B6 0 rows, B7 7 (1 L, 4 M, 2 S), B8 5, B9 1, B2 8, C 8.
> Cut clause unchanged.

> **B6 is retired: 0.8.5 was cut on 2026-09-16** (tag `v0.8.5`; the release-cut
> block in
> [`../90_record/00_completed_development.md`](../90_record/00_completed_development.md)
> is the record). The band emptied on 2026-09-16 with #216 and stayed empty:
> the pre-cut review that followed found three tier-S residues and closed them
> in one commit rather than re-opening a row, and the B7 re-cut landed on the
> same branch before the cut. **Band B7 (0.8.6 — the baseline wave) is the
> milestone in flight**; B8 and B9 (0.8.7, 0.8.8) follow it in order.

> **B7 amended 2026-09-17 (owner, in session) — the #164 case-set ruling is taken.** The 0.8.6 review of
> SELECT's wing search against an ATR-class airplane found the negative side carries one slot where the
> positive side carries three, and design note 62 records the ruling: two slots added (NHAA, NLAA), NMAA
> narrowed, filed as **#288** at the head of the band ahead of #164, whose V-n renumber would move the case
> numbers the note's gates name. #288 shares ordinal 1 with #164 until the next re-cut (gaps and shared
> ordinals are the rule between re-cuts; the row order is the order). The companion change — wing mass
> states in the Wing Loads step, so a selected case runs at every disposable-mass state — is the next note,
> not yet a row; #260's E6 and the fixtures' hand-entered `wing_mass.cases` wait on it.

**System of record (design note 28 MD-5, 2026-08-16):** open work is **GitHub
Issues** (labels `tier:*`, `tag:*`, `band:*`, `kind:*`; a milestone per release;
the Project board is the view). This file keeps the **plan** — mission,
definition of done, the reference hierarchy, and this table — and each row names
its issue as `(#N)` once `scripts/backlog_issues.py create` + `rewrite` have run
(owner, once); item bodies then live in the issues, a PR says `Closes #N`, and
`scripts/backlog_issues.py check` holds table ↔ open issues both ways. Until the
migration runs, bodies stay where they are — a defect promoted into the table
keeps its body in *Open defects*, and the [E]/[V] detail sections hold the rest.

**Ordering rules (cumulative):**

- *2026-08-09:* wrong cards outrank missing cards; [V] items are ranked, not
  opportunistic.
- *2026-08-16 — effect-vs-error-bar rule* — promoted to **`CLAUDE.md` rule 6**
  (the datum it measures against is
  [`../20_theory/00_theory_sources.md` §Base-method uncertainty](../20_theory/00_theory_sources.md#base-method-uncertainty)):
  a [V] item is ranked only if its stated effect exceeds that; below it, parked
  with the number. Defects with first-order effect on shipped content outrank
  every [V] item.
- *2026-08-16 — schema freeze through 0.6.0* (held: one hop, v53). *2026-08-17
  — 0.7.0:* lifted for exactly **one additive hop**, L-7's lateral inputs
  (off by default, note 19 L-7.3); any other field change in 0.7.0 rides that hop
  or waits for 0.8. v47 → v52 in nine days is the churn the rule answers.
  *2026-08-22 — 0.7.0 beta:* lifted for exactly **one hop**, #52's retirement
  of the two duplicate entries (v55) with a migration that takes the owner's
  value and warns on disagreement; anything else rides that hop or waits.

> **Removal rule (hard requirement, restating the lifecycle rule).** Once a
> step is complete it **SHALL be removed** from this table and this file in the
> same session, with its tiered closure trail. A closing change deletes **its
> own row and touches nothing else** — no renumbering (gaps in **Pri** are
> fine: it is the order at the last re-cut, not an ID; dense numbering returns
> only at a re-cut, which owns the whole table) — and rows never cite another
> row's ordinal (dependencies name the band or the `#N`), so two in-flight
> changes cannot conflict on this table (`DEVELOPMENT_PROCESS.md` §0).


| Pri | Item (detail below / in its plan) | What ships | Tag | Tier / effort | Depends on |
|---|---|---|---|---|---|
| **B7 — 0.8.6: the baseline wave** ||||||
| 1 | **SELECT gains the negative angle-of-attack wing slots NHAA and NLAA, NMAA narrowed to the VC pair** — SELECT.BAS searches three positive angle-of-attack slots and **one** negative, so whichever negative point has the largest resultant is delivered and the other spar's down-load case is discarded with nothing said; on `atr42_100` the pick between STALL −N and MAN −C is decided by the drag term and the −1.44 g VC gust at minimum weight reaches no deliverable, on `ga6_normal` the forward-CP stall point is dropped. Design note 62 (PROPOSED 2026-09-17) adds NHAA (W-07) and NLAA (W-08), narrows NMAA to MAN −C / GUST −C, requires negative lift of a negative slot, and carries both in the LRA deck. **This is the #164 case-set ruling.** Every fixture enters `wing_mass.cases` by hand, so no new slot reaches WINGINER/NETLOADS here and the Appendix A oracles do not move *(measured 2026-09-17)* (#288) | `select_wing` with the three-slot negative triad, W-07/W-08 in `WING_SLOTS`, both in `SYMMETRIC_WING_CONDITIONS`, the six Appendix A picks locked and the two slots closure-gated on every fixture's frozen pick (G-62.1…G-62.4); `PROGRAM_SPEC` / `ch04` / `theory_sources` updated; one digest wave (`select`, deck, report register) | V | L / M | note 62 at AGREED; lands **before #164**, whose V-n renumber moves the case numbers the note names |
| 1 | **GA6 fixture: altitude identity + wing-case envelope, one package** — every delivered case states 0 ft where Appendix A names its critical wing conditions at 12,000 ft, and the wing export ships three cases with no negative-g, so the delivered distributions do not envelop the wing; each fix renumbers the V-n indices the other depends on, so this row is #164 **and #165 merged** — the renumber is paid once *(review R-26)* (#164) | Stated condition identities correct and the wing enveloped; the three oracle cases kept; oracle-locked fixtures renumbered in one pass | V | L / M | #288 (the case-set ruling, note 62) ships first; the wing-case envelope half then reads SELECT's eight slots |
| 2 | **The LRA deck states nothing about the SELECT conditions it does not assemble, and the `out-of-family` reason names decks note 56 deleted** — the assembler records every skip through one owner, but the block that rendered it lived in the assembled deck D-56.8 stopped shipping, and `write_lra_model_bdf` writes none; the reason for the largest class still says the fuselage and one-engine-out conditions are "covered by the per-component analyses", which D-56.2 deleted. A sizing loop reading the one deck that ships is not told that a quarter of SELECT's set is absent, and on a wing-mounted twin the absent quarter holds the primary fin/aft-fuselage case *(measured 2026-09-16: ATR deck 43 SUBCASEs, 28 unassembled, 0 stated; GA6 44 / 24 / 0)* (#284) | The skip record rendered in the LRA deck header from `skipped_conditions(project)`, the reason text reworded to name surviving artifacts, every reason that names a deleted artifact swept, and a G-OR-73-class guard holding deck ↔ record equal on every fixture | V | S / S | — |
| 3 | **The LRA mesh does not guarantee a fuselage owned point at the spar carry-through, and Appendix G now measures what that costs** — worst fuselage shear deviation **82–197 %** of the channel's own peak across the four loaded fixtures, against **under 5 %** for bending everywhere; on `concept_regional_jet` a ~107,000 lb carry-through reaction lands on a node one bay from where it acts, against a peak station shear of 54,588 lb. Stated and not gated under note 56 ruling 15, and deliberately not fixed in the slice that measured it — changing the mesh to improve its own measurement would be marking its own paper *(note 56 §7b finding 3, measured 2026-09-12; **pulled forward from B9 2026-09-16** — first-order on an ATR-class high-wing fuselage, which the 0.8.6 review put ahead of the two rows below it)* (#275) | D-56.4's mesh rule amended so the fuselage's owned points include the spar carry-through stations; Appendix G re-measured over the same four fixtures with the fuselage shear row expected to fall by the bay length it currently mis-places | V | M / M | an amendment to note 56 D-56.4 (#263 shipped) |
| 4 | **One fuselage quantity is published under two `LoadValue` keys** — `select_fuselage`'s down/up blocks split one quantity across two keys; the report's §4.3 fold is the workaround *(found 2026-09-06, OR-14)* (#222) | Keys converge, labels survive as display text; rides the baseline wave (CSV columns move) | V | M / S | the baseline wave (#164 first) |
| 5 | **`atr42_100` is internally inconsistent** — planform 18 % under the type's area with the true value stored-but-ignored, wing items 3.4x the panel integration, fuselage stations 3,741 lb short, five override warnings on load, no control-surface slices, **and one entered wing case** — `wing_mass.cases` holds PHAA alone with a zero couple, so the WINGINER distributions and the report's wing section run no negative-g, TORS or ACRL case on the ATR while the deck's six come from SELECT unaffected *(2026-09-09 review §4; E6 added 2026-09-16 from the 0.8.6 review)* (#260) | The fixture reconciled end-to-end from published ATR 42-300 data, its wing-case set shaped by the #164 ruling; in the CI matrices, so baselines move *(the baseline wave; #261 shipped 2026-09-10)* | V | M / M | the baseline wave, now **#164 → #222 → #161** — #241/#242 left it for 0.8.4 at the 2026-09-11 re-cut; the case-set shape follows note 62 (#288) and the wing-mass-state note that follows it |
| 6 | **`format_value` prints inconsistent precision and flips notation on integral values** — `%g` strips significant zeros and switches notation at 1e5; ~84 call sites, every delivered table cell *(owner's PDF review 2026-09-01, OR-14)* (#161) | Consistent fixed-significant-figure rendering, design note first; lands **last** in the baseline wave since it reformats what the others produce | V | M / M | design note; the baseline wave |
| 7 | **Two engine-mount conditions per engine state no point of application** — the 23.361(b)(1) sudden-stoppage torque and the 23.371(b) gyroscopic condition carry no `loc_*` values while the four beside them for the same engine do. Until 2026-09-07 the index filled the gap with the *first* location in the set, publishing the right-hand engine's stoppage torque and its four gyroscopic sub-cases at the **left-hand** engine's butt line — ten rows on `atr42_100` and `dhc8_dash8`, fifteen on `concept_regional_jet`. Note 44 OR-193 carried the fix at the render boundary (a condition with no point takes the point of the condition it follows, which is that engine's, gated on every fixture); the **producer** stating the point on every condition it emits is the proper repair, and `modules/engine.py` is frozen for 0.8.2 *(note 44 §22, OR-193)* (#210) | `modules/engine.py` emitting `loc_x`/`loc_y`/`loc_z` on all six conditions, and `_running_locations` reduced to the identity it should be | V | S / S | — *(the OR-13 freeze lifted at the 0.8.2 cut; the row was stranded on a satisfied dependency until the 2026-09-14 re-cut)* |
| **B8 — 0.8.7: report polish** ||||||
| 8 | **Override cross-check warnings fire below display precision and print two identical numbers** *(2026-09-08 review G6)* (#243) | One owner for the comparison tolerance (display precision or a stated rel-tol) so every cross-check warning behaves the same | V | S / S | — |
| 9 | **Report polish rollup from the 2026-09-08 review** — ten tier-S presentation items in one issue so none is lost *(R13–R23)* (#240) | The ten items closed or individually declined with a reason | V | S / S–M | — |
| 10 | **Engine-installation figure legends overflow the margin on long twin designations; coincident point labels overprint** — invisible on GA6, guaranteed on any real twin *(2026-09-09 review A3)* (#256) | Legend entries wrapped or stacked inside the text width; shared-coordinate labels offset or combined *(beside #240's polish)* | V | S / S | — |
| 11 | **A derived ACRL assembles with a zero aileron couple and the deck states nothing in band** — a reader cannot tell couple-free physics from couldn't-compute-the-couple *(2026-09-09 review A5)* (#258) | The zero-by-derivation stated in the case's notes, deck header and UI, like the ASSUMED thrust line; one guard test | V | S / S | — |
| 12 | **One field name means a count in one dataclass and a list in another** — `WeightEstimationInput.engines` is an engine **count** while `Project.engines` is the list of `EngineInput`, and the units walker reaches the list first, so the count has never been asked whether it is classified: it is invisible to a gate whose whole claim is totality. Harmless today only because a count is dimensionless and unconverted is right by accident, and pinned meanwhile in `tests/test_project_units.py::_KNOWN_AMBIGUOUS` as a decision on the record rather than a silence *(deferred out of note 56 as a schema change of its own, 2026-09-12)* (#276) | The field renamed `engine_count` with its lenient migration, the published field-registry path `weight.estimation.engines` moved with it, and `_KNOWN_AMBIGUOUS` emptied — removing the name is how the rename closes | V | M / S | a schema hop (the registry path is published) |
| **B9 — 0.8.8: the beam-model page (its mesh-rule amendment, #275, moved to B7 on 2026-09-16)** ||||||
| 13 | **Beam-model page: the LRA definition, the model drawn, and the sbeam deck written to a chosen directory** — the LRA free-free model is the primary deliverable and the GUI has no path to it: no step, no page, no editor for `lra_mesh` or `ref_axis_pct` beyond raw JSON, and `lra_model.bdf` is written only by the CLI; the schema has called it "step 12" since v52 and no step exists. The page shows the axis (default a chord percentage, user-definable), draws the model as `scripts/plot_lra_model.py` does (iso + three views, outlines overlaid, refusal shown verbatim) and writes the **sbeam input BDF** — one writer, `write_lra_model_bdf` with the CLI's stamp — to a user-selected directory through the Report page's native picker. **Reopens note 57 D-57.6**, which retired the export page without port: this is the missing step for the deliverable, not that page ported, and a design note must say so at AGREED first. The report package does **not** carry the deck (owner, 2026-09-14): this page is the one GUI channel for it *(owner's request, 2026-09-14; moved from B2 into B9 at the same day's split, paired with #275)* (#283) | The note AGREED; the page as a step or declared non-step in `workflow.py`; the script's drawing moved to one owner the page and the script both call; no second writer, picker, stamp or figure (the #239 class) | V | L / M | a design note at AGREED first; **after #275** (it draws the mesh #275 amends) |
| **B2 — 0.9.0: calc, report and process work (re-chartered 2026-09-11 — the “main-GUI development” it was named for retires with #270)** ||||||
| 14 | **GUI review resumption, on the converged surface** — the review the 0.8.0 pass left unswept (Flight, Other, Ground, Plotting, Export), now against the one front-end left by #270: the fourteen pages of the generic renderer, the figure blocks of #267, the Report page and the JSON editor; findings filed at close (rule 5); re-cut follows. It inherits the one open class the #270 closures left standing — **L-8d's mutation half**, a widget that goes stale while the project is *mutated* underneath it (a seed chain, a cross-page write), which no generation bump covers and which the 2026-08-24 review and the 0.8.4 closure review (the seed button's row counter) both showed is a live mechanism *(re-scoped 2026-09-14 — the `app/views/` rows #148, #247–#252 and #259 closed with the tree they named)* (#29) | The review body completed against the surviving GUI; a reviewed list of findings, not a rework | V | S (review) / M | 0.8.4 cut |
| 15 | **`solo_close.sh` verifies fragment existence, not tier content** — nothing checks a tier-M closure touched `PROGRAM_SPEC.md`, a tier-L closure cited `theory_sources.md`, or that a physics change had a note at AGREED; hand-git bypasses are degrading the commit-subject record. The checkable subset gets scripted; the rest is named as discipline in `DEVELOPMENT_PROCESS.md` *(review R-15)* (#185) | The preflight enforcing the checkable closure obligations and validating the subject it writes | V | M / M | — |
| 16 | **Whole-pipeline-per-assertion tests, re-aimed at the coverage leg** — *moved from band D 2026-09-04* *(CR-D-6, filed from #46; hygiene; ruled 2026-08-26 (owner): option (b) — the trip figure was the coverage-instrumented run; the row is re-aimed at the run that pays for it)* (#92) | The repeated-pipeline shape gone from the coverage leg's `--durations`; the local command stays the clause's datum. **No `slow` marker** — `00_program_overview.md` §Testing states why | V | S / S–M | — |
| 17 | **The oracle form reaches into a `field_registry` private** — `oracle_app/form.py:709` calls `fr._locate(paths[0])`, the only access to a `sloads` private from either shell package *(production-release review 2026-08-27 §3.7; moved from band D 2026-09-04 — the GUI milestone is when `field_registry` is next touched)* (#130) | `field_registry` exposes the lookup publicly and `row_class` calls it; the private stays private | V | S / S | when `field_registry` is next touched |
| 18 | **The load-case index carries no loads for 344 of 347 rows** — its six load columns are the engine-mount shape (`render.load_cases_to_rows`' own docstring: *"the load components an engine mount must react"*, `load_keys.LOAD_CASE_KEYS`), and four of the five producers cannot express themselves in it: a landing case has three legs at three points, a wing case a distribution. Measured 2026-09-07: **344/347** rows on `ga6_normal`, **543/555** on `baron_58`, **587/617** on `concept_regional_jet` carry a blank load. Note 44 OR-186 answered the *deliverable* half — each structural element now has an applied-load CSV shaped for its own loads — and left the index itself, because removing or reshaping those columns touches every producer and every consumer of `load_cases_csv`. Either it is an index, in which case the load columns invite a reader to conclude a case carries nothing, or it is a load table, in which case most of it is missing *(note 44 §21 filed, §22 measured)* (#209) | A decision on what the file is, then the columns to match it — the candidate being that it becomes an index in name as well as in fact, with the per-element files carrying the loads. **Unchanged in substance by note 56**, but D-56.1 moved the case index out of the export bridge into `report/tables.py` (`case_index_rows`, `case_index_csv`) — arguably where a decision about what a *report* table is always belonged; its six load columns still come from `report/render.py`'s `load_cases_to_rows` and the file itself from `io.py`'s `load_cases_csv`, so the decision now touches three owners | V | M / M | note 44 §22 shipped; a decision on the file's purpose |
| 19 | **The flight balance models no thrust** — `flight_envelope._balance` solves the normal force and the pitching moment about the CG and writes **no** longitudinal force equation, so every balanced V-n point is thrust-off. That is consistent rather than absent: the drag leaves the balance as `NX = -DX/W` (`aero_curves.inertia_drag_factor`) and WINGINER applies it to the mass distribution, so the airplane is in longitudinal equilibrium as a decelerating body, and note 44 OR-198 makes Appendix A state it. Modelling power would reduce NX and add a thrust-line pitching moment about the CG — design note 53's `thrust_line_fwd`/`thrust_line_aft` already carry the geometry — and would move **every** balanced point, hence every selected condition and every delivered load. **Parked without a rank under rule 6:** its effect on a delivered load is unmeasured, so the first piece of work is the measurement, not the implementation; a power-on balance whose effect is below the base method's own uncertainty is not worth a contract change to an oracle-locked module *(owner's question, 2026-09-07: "we don't have any cases defined as thrust on or off, are all assumed off?"; note 44 §23, OR-198)* (#226) | The measurement first — how far a power-on balance moves a delivered load on a shipped fixture — and then, only if it clears the base-method error bar, a design note for a thrust term in `_balance` | V | M / L | a measurement; then a design note (oracle-locked module) |
| 20 | **The one-engine-out fin conditions reach no shipped deck** — SELECT names four 23.367 fin conditions on every twin (two already ultimate) and the assembler skips all four as out-of-family, a deferral that rested on the per-component fin deck note 56 D-56.2 deleted; the OEI fin load exists in the report and in no deck, and on a wing-mounted twin it is the primary fin/aft-fuselage sizing case. Plan 13 §4's ruling that a transient is not a steady balanced case stands; the channel it deferred to does not *(2026-09-09 review §5 item 2; filed 2026-09-16 from the 0.8.6 review)* (#285) | The transient's governing instant assembled as a quasi-static lateral case on the B8a-3 rudder-case machinery, handed by reflection, `ULT SF=1.0` stated per subcase, closure-gated in the round-trip CI on both twin fixtures; the note decides the instant, the inertia set and the L-7 interaction | V | L / M | a design note at AGREED first; #284 states the absence meanwhile |
| 21 | **No engine-mount case reaches the LRA deck** — `lra-engine-mount`/`lra-engine-hub` nodes exist since note 24 R-9 and nothing loads them for a 23.361/23.363/23.371 condition; `coordinates.engine_applied_load` already owns the six components and is reached only from the report's section 10, so a nacelle, mount or attachment sized from the deck sees no engine case *(stated in *Open defects* as unfiled-by-choice since 2026-09-07; promoted 2026-09-16 from the 0.8.6 review)* (#286) | An `EM` case family with its SF from the governing table, the six components applied at the mount node and the reaction closed on the free-free airplane, equilibrium-gated in the round-trip CI, and the deck header naming every engine condition it carries and does not | V | L / M | a design note at AGREED first; **after #210** |
| **C — 1.0.0: additional analysis capability (consumer-gated; design notes first)** ||||||
| 22 | The aileron's own lift increment is not distributed (#14) | `ACRL` wing cards gain the aero half of the couple (~70 % span); the schema fields shipped v52 and wait for data and a consumer | V | L / M | only if a consumer sizes to `ACRL` |
| 23 | **Wing fuel (and any tank/store band) is a point mass in WINGINER** — faithful to WINGINER.BAS lines 1180–1270 (every concentrated mass is a spanwise step; only the structure panel is spread), but a wet wing's fuel occupies a span band, so the point model concentrates the inertia relief and puts a fictitious jump in mid-span shear/torsion (**owner, C210 build: "fuel should be spread through the wing not just at one point mass location"**, C210-50, build review 2026-08-23) (#111) | `WingMassInput` gains a distributed-mass band (y_start, y_end, weight, chordwise CG) folded into the per-strip density `w[i]`, reducing exactly to today's point when the band collapses; Appendix A oracle case (concentrated gear only) untouched, lock holds. Interim (documented in the review): split the fuel into N concentrated rows across the tank span with the same centroid — root bending and total shear identical | V | L / M | design note first (physics/L) |
| 24 | Ground-case fuselage station distribution — the ground family has no per-station view *(from the #11 closure, D-28)* (#31) | Per-station shear/bending/torsion for the ground family on the fuselage beam, its own envelope beside the flight one and never merged with it, each station naming its ground case | V | L / M | a frame-sizing consumer; design note first |
| 25 | Mach-capped balanced points are published with their coefficients extrapolated past the fitted stall alpha, and nothing says so *(from the #13 closure, D-30)* (#32) | A derived past-fit marker wherever a per-point quantity is published (BALLOADS' 300 rows first); rows stay published and marked, never withheld; no schema field — the marker reads `EnvelopeResult.is_clamped`, the owner #33 left (2026-08-22), rather than re-deriving the point's CL against its Mach-adjusted stall CL; the two are pinned to name the same rows | V | M / S–M | — |
| 26 | Calc-side function size (CH-8) — *moved from band D 2026-09-04; re-cut with the review's numbers: `landing_reactions` now 276, plus `envelope` 195, `build_tail_span` 176, `_export_sbeam` 173, `_manifest_rows` 155 and the three `balance` assemblers (see the R-22 comment on the issue)* (#17) | Split when touched; **the view functions wait for the GUI review (#29)**. **Re-measured at note 56's close (2026-09-12), and the forecast was wrong in one half**: `_export_sbeam` was not deleted — it lost its per-component branches and stands at **53**, off this list; `_manifest_rows` is **131**, not the 155 this row carried; `landing_reactions` (276), `envelope` (195) and `build_tail_span` (176 — untouched, but its deck consumer is gone) stand, as do the three `balance` assemblers | V | S / S | — |
| 27 | Review 2026-08-10 unscheduled findings m3–m13, m15–m18 + NITs *(defect sweep; moved from band D 2026-09-04)* (#18) | Swept opportunistically (practice 4) or promoted individually | V | S / S–M | — |
| 28 | mypy strictness ratchet — stage 2 `export/`, stage 3 `modules/`, **plus `io.py` as its own stage** (95 `Any`-typed lines, the schema boundary — the R-25 comment on the issue) *(design note 27 ST-3; moved from band D 2026-09-04)* (#19) | `sloads.export.*`, `sloads.io`, then `sloads.modules.*` added to the `[[tool.mypy.overrides]]` list and narrowed to zero under ST-4; then `warn_return_any`/`disallow_any_generics` toward `--strict` | V | S / S per stage | — |
| 29 | **No inbound channel for an externally computed load distribution** — the survivor can write a distribution and cannot read one back, so a distribution from another model cannot be checked against this analysis. Design-note work before code: which columns, which stations, which units, and what a disagreement between the two is *said* to be. `sloads/report/lra_import.py` already reads an external GRID/CBAR **model**, so the pattern exists; #245's `data/` is the outbound direction and does not cover this *(note 60 §9, amended 2026-09-13 — the home of §1.1's figure 19, which is deferred with it rather than retiring at #270)* (#279) | An agreed import contract, the channel, and the imported-against-computed overlay as its first consumer | V | L / M | a design note at AGREED first |

**Frozen (review §3) — no further investment; tests and gates kept; touched
for defects only:** the FAR 23 core; the balanced assembler + handedness;
CONM2/MASSSET export; the sbeam round-trip harness; the ground/landing
families + gear report; the governing safety-factor table (Layer 2 parked);
distributed empennage loads, control surfaces, hinge moment, T-tail transfer;
the **LRA beam model at its determinate paths**; the summary report, PDF,
workbook, manifest and methods stamp; the GUI — `oracle_app/` + `app_shell/`, the one front-end since #270 —
pending the GUI review (#29), whose findings decide what re-opens (the CLI is
the delivery path; the `app/views/`-only rows M4-11b and L-8b/c/e/f closed with
that tree on 2026-09-14; parked **L-8d**'s keyed data-loss half shipped 2026-08-21 as #51 —
`app_shell/widget_keys.py` — and its unkeyed half shipped 2026-08-22, closing
#51's reopen as one pass with #44's unit-boundary rollout: that pass consumed
**the one carve-out from this freeze** — `key=` plus the boundary helper at
exactly those call sites, no layout/behaviour rework — so the freeze is whole
again; L-8d's mutation case stays parked); F25-2.

---

## Open defects (index)

A bullet whose body says **unfiled by choice** is a finding stated here on
purpose and not scheduled: `scripts/backlog_issues.py` lists it under `plan`,
never files it under `create` and never collapses it under `rewrite`. The phrase
is the marker the tool reads — before #280 nothing in the tool knew the state
existed, and what kept two of these unfiled was a regex that could not see a
bold heading wrapping onto a second line.

- #18 — Review 2026-08-10 unscheduled findings [Minor/NIT].
- #217 — An entered thrust line does not steer the thrust in the balanced cases.

- #286 — No engine-mount case reaches the LRA deck *(held here without a number
  from 2026-09-07; promoted to band B2 on 2026-09-16, the body moved to the issue)*.
- #285 — The one-engine-out fin conditions reach no shipped deck.
- #284 — The LRA deck states nothing about the SELECT conditions it does not
  assemble.

- **No control-surface hinge moment is computed anywhere — in sloads or in the
  suite it replicates.** Checked against the source 2026-09-07: `AILERON.BAS`,
  `FLAPLOAD.BAS` and `TABLOADS.BAS` each end after printing their loads and
  chordwise pressures; chapter 16 (p105–106) claims only the constant pressure
  forward of the hinge line; and the words *hinge moment* occur once in the
  whole manual, in the quoted CAM 3.224-1(a) tab-deflection limit, which
  chapter 18 (p113) then declines to apply — *"the computer program for surface
  loads for the aileron, elevator and rudder are not limited to pilot effort."*
  So this is **not a replication gap**: note 44 §19 OR-154 states the *sense* of
  the moment as the sign convention and derives no magnitude. Whether sloads
  should produce one as a modern addition — it is what a control-surface
  attachment and its actuator are sized to, and `AileronLoadsInput.hinges_span_in`
  and `actuator_span_in` are already entered-never-invented and unconsumed — is a
  **scope question for a later milestone**, and one that needs a method the
  oracle cannot supply (a chordwise centre of pressure per throw, and a hinge
  line the schema does not carry as geometry). **Filed 2026-09-07.** Tier L if
  taken, and it would reach `modules/aileron.py`, frozen for 0.8.2 under OR-13.
  **Unfiled by choice**: the scope question is the work, and it is not this
  milestone's. *(Re-verified 2026-09-15 at the #280 closure: no hinge moment is
  computed for an aileron, elevator or rudder — `tail_span`'s `hinge_moment` is
  the tail attachment chain's actuator couple — and
  `AileronLoadsInput.hinges_span_in` and `actuator_span_in` are still read by
  `io`, `units` and `field_registry` and by no calc.)*

- **The oracle prints an aileron deflection schedule the module does not
  publish.** Appendix A p200 prints the deflections at VA, VC and VD (15.00 /
  10.68 / 4.26 deg and their up throws) that the pick is made from;
  `aileron.aileron_loads` computes them internally and returns only the
  governing loads and speeds, so section 7 states the schedule as a rule in
  words and prints no numbers for it — the report may not re-derive what a
  module did not return (OR-6). Publishing them is additive, one `LoadValue`
  each. **Filed 2026-09-07.** Tier M, and it touches frozen `modules/aileron.py`
  (OR-13). **Unfiled by choice** while that freeze stands. *(Re-verified
  2026-09-15 at the #280 closure: `aileron_loads` still computes `cdeg`/`ddeg`
  and their up throws internally, and `AileronResult` still returns no
  deflection field.)*

- #218 — The fuselage applied set is `Fz` alone — is that the model, or the airplane?

- #221 — The oracle reduction resets `weight.items[].consumable`, moving a load.

- #222 — One fuselage quantity is published under two `LoadValue` keys.

- **R-4's tolerance class is suite-wide, not `test_structural_speeds`'s alone.**
  Closing #175 swept the file the review named; the same sweep, run across
  `tests/`, finds **92** `rel_tol` values looser than the ±0.1 % of Decision 3,
  of which **68 in 19 files** carry no justification within three lines — the
  heuristic is crude (it accepts any nearby comment mentioning a percentage,
  rounding or precision), so the true figure is the ceiling, not the count.
  Concentration: `test_select.py` 24, `test_landing.py` 12, `test_flap.py` 8.
  Each one is individually plausible — a printed three-figure oracle, a
  curve-fit band, an accepted method difference — and that is exactly the
  problem: nothing distinguishes the rounding-limited ones from a disagreement
  nobody has looked at since, because a passing assertion records no margin.
  The structural half (practice 3) is a guard that refuses a tolerance looser
  than the file's own stated band without a reason on its line; it cannot land
  until the 68 are read, which is the work. **Filed 2026-09-15, from the #175
  closure.** Tier M, effort M — a read per site, not a `sed`; the fix for most
  will be to tighten, as it was for three of #175's five.
- **`case_loading_checks` holds a zero-ballast loading to 1e-9 where its own
  owner documents 0.5 in, and reaches no consumer at all.** Found by the #257
  sweep, which routed every *other* mass reconciliation to the issued document.
  `mass_distribution.case_loading_checks` compares each derived payload loading
  against the flight case's entered weight/CG echo. A **derived** loading takes
  the `_close(got, want, 1e-9)` branch — exact by construction, because the
  ballast row is *solved* from the target — but the same module's `CaseLoading`
  docstring states that a loading which already weighs the case weight has no
  ballast to move it and matches "only within `_CG_MATCH_TOL`" (0.5 in), and
  names ga6's CG4 as the precedent. The check does not use that tolerance, so it
  reports a failure on **four of the five shipped fixtures** that is not one
  (ga6 CG4 0.0024 in, atr42 0.0034 in, the RJ 0.0040 in, concept_heavy
  0.0044 in). Underneath the noise is **one real disagreement**: `baron_58`'s
  `aft gross` loading sits at zcg 95.884 in against the 100.0 the case states —
  **4.12 in, past the 0.5 in tolerance** — and xcg 85.652 against 86.0. That is a
  closure-locked twin, and its balanced cases run on the loading, not the echo.
  Both halves were invisible for the same reason: the function has **no caller**
  outside its own tests, so nothing ever printed what it found. The fix is two
  things in order — the derived branch takes `_CG_MATCH_TOL` when the loading
  carries no ballast (so the check means what its owner says it means), and then
  the check joins the four §2.2 already states, which is what
  `tests/test_mass_distribution.py::_UNSTATED_CHECKS` exempts it from until
  then. **Filed 2026-09-16, from the #257 closure.** Tier M, effort S for the
  tolerance and the routing; the baron_58 number is a data question for the
  owner and may be neither.

- **The unbounded dependency ceiling's early warning arrives after the push, and
  nothing tells a developer their venv has drifted.** `pyproject.toml` states a
  runtime floor with no upper bound and the decision is deliberate: CI installs
  unpinned on every run, so an upstream removal fails the GUI tests here before
  it reaches a user's fresh install (guard:
  `tests/test_ci_conformance.py::test_the_dependency_ceiling_policy_rests_on_an_unpinned_install`).
  What the policy does not say is where that failure lands. A developer's venv
  holds whatever was current the day it was made — this one sat at Streamlit
  **1.58.0 against CI's 1.64.0, six releases** — so `pytest` is green locally
  and red on the branch, *after* the push, and on 2026-09-16 that meant two
  consecutive red CI runs across two closures before anyone read the log. The
  local gate cannot answer the question by itself: asking PyPI what is newest
  needs a network the gate must not depend on. Options, cheapest first: the
  fast gate reports the installed runtime versions in its log, so a red is read
  against them without a second command; `solo_start.sh` refreshes the runtime
  dependencies when it opens a milestone branch, which is the one moment the
  cost is already being paid; or nothing changes and this entry is the note
  that says the lag is known and priced. **Filed 2026-09-16, from the
  1.64 `AppTest.session_state` break.** Tier S, effort S — but the choice is the
  owner's, and "priced, not fixed" is a legitimate answer to it.

Two long-standing entries left this list on 2026-08-18 at the issue #13 closure —
**decided, not fixed**, which is why neither survives here under the removal
rule. Both keep their pins; the decisions carry what the bodies used to:

- The **derived `ACRL` air-load divergence** is **D-29**: SELECT's own
  23.349(a)(2) pick is what the derived case names, the ~19 % difference against
  the worked example is accepted and stated, and an `ACRL` case used for sizing is
  **entered, never derived**. Pin:
  `tests/test_wing_case_derivation.py::test_the_acrl_divergence_is_the_documented_one`.
- The **ATR-42 Mach-capped stall exceedance** is **D-30**: nine of 300 points at
  25,000 ft are ordinary stall/Mach-limited flight, not a defect — `nz = n` and
  `n·W` are exact and the fixture is not edited to hide the corner. What is real
  is that CM/CD are evaluated 0.9–3.1 deg past their fit there, moving the
  published tail split by 3.3–44 % with **0 of the 9 SELECTed**, so no sizing load
  moves: filed as **#32** (mark the rows, band B) and **#33** (the solver's own
  silence — **closed 2026-08-22**: the nine are reported *clamped*, and #32's
  marker reads that owner). Pin:
  `tests/test_aero_curves.py::test_the_atr42_stall_exceedance_is_the_documented_mach_capped_one`.
  The GA oracle and both concept fixtures close cleanly.

---

## Open design decisions requiring user input

- [ ] **D-5 — Appendix B twin fixture (blocks parked L-9).** The swept (C7) and
  ONENGOUT (C9) printed oracles want the 10-place twin turboprop as a fixture,
  but Appendix B is **not in the bundled PDF**. *Can the user supply a legible
  Appendix B or the original `.INP`/`.OUT` files?* Until then
  `examples/twin_turboprop.project.json` can't be built and these oracles stay
  blocked. **(Reviewed 2026-07-20: keep blocked as-is.)**

D-1 … D-18 (all but D-5) are answered and recorded in
[`../25_notes/03_resolved_decisions.md`](../25_notes/03_resolved_decisions.md).
