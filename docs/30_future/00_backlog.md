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
(the precision row, closed at #161) has **zero** `app/` call sites — 164 in `sloads/report/`, three in
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
> **Pri 1–30**: B6 0 rows, B7 1 (0 L, 0 M, 1 S), B8 5, B9 1, B2 8, C 8 *(recounted 2026-09-21 at the #161 closure; superseded by the 2026-09-22 re-cut below)*.
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
> states in the Wing Loads step, so a selected case runs at every disposable-mass state — is design note 63,
> filed as **#289** behind #288 (same shared ordinal) and **shipped 2026-09-18** (`113c9cd`) as the one-model step and **#292** the variants step, **shipped 2026-09-18**: every slot runs at every FLIGHT mass state, the net-governing run is delivered, MZFW seeds the zero-fuel cases, and the fixtures' `wing_mass.cases` are filters (note 63 SHIPPED, §11).

> **Re-cut 2026-09-22 (owner, in session) — the 0.8.6 pre-cut critical review.**
> The band emptied with #210 (2026-09-22) and the review the cut rule requires
> (`CODE_REVIEW_PROCESS.md` §0; gate green — ruff, mypy, the full suite) found
> the cut not clean: **one CRITICAL** — `select_wing` applies the D-62.8
> coincidence rule to the *air* picks before the D-63.7 re-pointing, so when
> NMAA moves to another mass state the NNZ extreme it coincided with is
> delivered by nobody (`baron_58` V-n case 153 at −2.345 g, `concept_regional_jet`
> case 213 at −1.805 g — a 23.337/23.341 design condition silently absent from
> the one deck that ships) — and **ten MAJOR**, six of them inside the wave's
> own closures. Four rulings:
>
> 1. **B7 re-opens for the pre-cut fixes** — #294 (the SELECT cluster: the
>    coincidence stage, the dead 1e-9 `nz` tie band, the `AIR_PICK_SLOTS`
>    guard), #295 (the ACRL variant omits its couple), #296 (`_hop_66` stamps
>    a converted centreline point PANEL), #297 (the LRA wing post raises
>    `KeyError`, not the refusal), #298 (SI precision rows deliver one or two
>    figures) and #299 (the doc residues, note 65's `AGREED` among them). The
>    round trip the 0.8.3 cut also took, for the same reason: a release cannot
>    knowingly carry a wrong delivered load.
> 2. **B8 / 0.8.7 is re-chartered “the deck carries what the airplane
>    carries.”** #210 shipped and #284 stated the absences; the two cases the
>    statement names are the largest gaps in the primary deliverable and sat at
>    the bottom of B2 behind process rows, both citing dependencies that had
>    shipped. **#286 and #285 move B2 → B8** (one design pass); **#258 moves in**
>    as the deck-statement gap it is (#284's class, misfiled as polish);
>    **#221 is promoted** from *Open defects* — measured: the oracle reduction
>    resets `weight.items[].consumable`, so on `atr42_100` every case turns from
>    entered to searched and the fuel reads 0 lb on all eleven, and since notes
>    62/63 the fuel state *is* the wing case set; #300 (the Baron `aft gross`
>    loading 4.12 in from its echo and the uncalled check that hid it), #301 (the
>    search tests symmetry of the discretionary subset alone), #302 and #303
>    (the #161/#293 residues) are filed; #276 rides the first schema hop the band
>    forces. The polish rows #243, #240, #256 move to B9 behind #283, whose
>    “after #275” is cleared.
> 3. **Rule 6 is applied to its own rows.** #226 is re-cut from a ranked
>    tier-M physics row whose body said “parked without a rank” into a tier-S
>    *measurement* row absorbing #217 and #218 (one `nx`/thrust-line study);
>    #111's park condition — the ATR point-vs-band root-bending number — was
>    never measured after the per-tank rows landed, and root bending is zero by
>    construction for a band with the same centroid, so its row asks for the
>    mid-band station shear first and claims no number; **#32 parks with the
>    number zero** — after #260 no shipped fixture reaches the Mach-capped
>    clamped state ([`02_parked.md`](02_parked.md)); #14 is labelled
>    consumer-gated, not rule-6.
> 4. **Open defects are filed or marked.** #304 (R-4's tolerance class) and
>    #305 (the aileron deflection schedule, whose freeze reason lifted at the
>    0.8.2 cut) are issued; the hinge-moment entry is re-justified on scope
>    alone; the dependency-ceiling entry takes the option its body offered —
>    priced, not fixed — and is marked *unfiled by choice*.
>
> Renumbered densely, **Pri 1–34**: B7 6 (0 L, 1 M, 5 S), B8 9 (2 L, 4 M, 3 S),
> B9 4 (1 L, 0 M, 3 S), B2 7 (0 L, 3 M, 4 S), C 8 (4 L, 1 M, 3 S). **Cut 0.8.6
> when B7 is empty again**, 0.8.7 when B8 is, 0.8.8 when B9 is, then 0.9.0 when
> B2 is.

> **B8 amended 2026-09-22 (owner, in session) — note 52 re-agreed and filed.** The #294 review of the ACRL chain against Reference 1 found the delivered `ACRL` variant carrying the roll point's averaged lift rather than condition A's (≈ 19 % low on the governing side's net root bending), the percentage on the manual's pre-1996 rule, and #295/#258 to be two symptoms of the one missing derivation. Design note 52 is amended in place (D-52.10–D-52.13) and its implementation enters **B8** as one tier-L row at #258's place, folding **#295** (B7) and **#258**; the 23-48 percentage is registered in `02_approved_corrections.md` at the amendment. Ordinals keep the re-cut's numbering (no renumber): **33 rows** — B7 4 (0 L, 0 M, 4 S), B8 9 (3 L, 4 M, 2 S), B9 4, B2 7, C 8. Cut rule unchanged.

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
| **B7 — 0.8.6: the baseline wave — re-opened 2026-09-22 for the pre-cut review's fixes** ||||||
| 6 | **Pre-cut documentation residues from the 0.8.6 review** — note 65's status still `AGREED` after #161 shipped (§7b amends D-65.3 and the header does not say so; the `test_doc_currency` guard matches `## Step` headings only, so tier-M note-backed closures slip through); `theory_sources.md:376` still states the retired nose-to-tail body closure, the spar carry-through reaction and `closure_artifact`; `60_guide/06_wing_loads.md` and `07_fuselage_loads.md` still teach the entered panel, the concentrated list and the carry-through model; `04_far25_gap_analysis.md` 25.343 rests on "fuel is one item"; five tier-M fragments lack the `- ` prefix the README states and would roll into the record un-bulleted; `00_INDEX.md` note rows describe the AGREED scope (D-62.8/W-09–10, D-63.11, the one-figure floor) *(0.8.6 pre-cut review, 2026-09-22)* (#299) | Each statement corrected in place, the doc-currency guard extended to the tier-M bold lead, one fragment | V | S / S | — |
| **B8 — 0.8.7: the deck carries what the airplane carries (re-chartered 2026-09-22 — the report polish it was named for moves behind #283)** ||||||
| 7 | **No engine-mount case reaches the LRA deck** — `lra-engine-mount`/`lra-engine-hub` nodes exist since note 24 R-9 and nothing loads them for a 23.361/23.363/23.371 condition; `coordinates.engine_applied_load` already owns the six components and is reached only from the report's section 10, so a nacelle, mount or attachment sized from the deck sees no engine case *(stated in *Open defects* as unfiled-by-choice since 2026-09-07; promoted 2026-09-16 from the 0.8.6 review)* (#286) | An `EM` case family with its SF from the governing table, the six components applied at the mount node and the reaction closed on the free-free airplane, equilibrium-gated in the round-trip CI, and the deck header naming every engine condition it carries and does not | V | L / M | a design note at AGREED first (one design pass with #285); #210 shipped 2026-09-22 |
| 8 | **The one-engine-out fin conditions reach no shipped deck** — SELECT names four 23.367 fin conditions on every twin (two already ultimate) and the assembler skips all four as out-of-family, a deferral that rested on the per-component fin deck note 56 D-56.2 deleted; the OEI fin load exists in the report and in no deck, and on a wing-mounted twin it is the primary fin/aft-fuselage sizing case. Plan 13 §4's ruling that a transient is not a steady balanced case stands; the channel it deferred to does not *(2026-09-09 review §5 item 2; filed 2026-09-16 from the 0.8.6 review)* (#285) | The transient's governing instant assembled as a quasi-static lateral case on the B8a-3 rudder-case machinery, handed by reflection, `ULT SF=1.0` stated per subcase, closure-gated in the round-trip CI on both twin fixtures; the note decides the instant, the inertia set and the L-7 interaction | V | L / M | a design note at AGREED first (one design pass with #286); #284 shipped 2026-09-20 and states the absence meanwhile |
| 9 | **The rolling conditions arrive complete — design note 52 as amended 2026-09-22** — the unbalanced rolling moment is entered by hand and a derived ACRL carries zero (three places say it "comes from AILERON"; Ref 1 Ch 16 computes aileron surface loads only); the delivered ACRL variant is built at the `AC ROLL` point's averaged lift, not condition A's, so the governing side's net root bending is ≈ 19 % low against Appendix A p225 (D-52.10); the other-side percentage is the manual's pre-1996 70→75 % rule where 23.349(a)(2) Amdt 23-48 says 75 % flat (D-52.11, `02_approved_corrections.md`); the TORS `Δcm = −0.01·δ` increment is selected on but not delivered (D-52.5); FLTLOADS has no category branch, so an acrobatic project gets the normal percentage silently (D-52.13) *(note 52 AGREED 2026-09-07, amended 2026-09-22 from the #294 review of the ACRL chain; folds #295 — the variant table ranks ACRL on the balanced part alone — and #258 — a derived ACRL states nothing in band about its zero couple)* (#306) | D-52.1–D-52.13 with gates G-52.1–G-52.13: one percentage owner (75 %, acrobatic flagged, read by FLTLOADS too), derived UNB on every row, the condition A air point on the delivered variant with its drift guard, the TORS increment behind optional aileron butt lines (blank reduces to the printed run), the provenance sweep, `ga6_normal`'s ACRL row retired to derived with the case 160 lock test-built, report §3 rolling subsection, one GA6 digest wave | V | L / M | design note 52 (AGREED, amended); D-29 superseded for delivered paths |
| 10 | **The oracle reduction resets `weight.items[].consumable`, moving a load — and after notes 62/63 it erases the mass model** — `field_registry.reduce_to_oracle_inputs` zeroes `consumable` because `weight.items[].consumable` is not in `oracle_input_paths()`; measured 2026-09-22 on `atr42_100`: the four consumable rows go to 0, every one of the eleven cases turns from *entered* to *searched*, and `mass_case_summary.fuel_lb` reads 0.0 on every case (9,874 → 0 at MTOW, 700 → 0 at MZFW), so a reduced project has no zero-fuel state at all — the state that is the wing case set since #289/#292 *(Open defects since 2026-09-06; promoted 2026-09-22 from the 0.8.6 pre-cut review)* (#221) | `consumable` (and `carriage`, `loading`) classified in the field registry so the reduction keeps them; a guard that the reduced ATR carries the same fuel per case as the full one; the GUI's own path checked for the same hole | V | M / S | — |
| 11 | **`case_loading_checks` holds a zero-ballast loading to 1e-9 where its owner documents 0.5 in, reaches no consumer, and the one real disagreement it hides is `baron_58`'s `aft gross` loading at zcg 95.884 in against the 100.0 the case states (4.12 in)** — measured again 2026-09-22: the derived branch still reports `xcg 85.652 against 86.0` as a failure inside the documented tolerance, and `aft gross`, `fwd gross`, `fwd regardless` still run searched; a closure-locked twin's balanced subcases and fuselage conditions ride a loading that disagrees with its echo *(filed 2026-09-16 from the #257 closure; promoted 2026-09-22)* (#300) | The derived branch takes `_CG_MATCH_TOL` when the loading carries no ballast; the check joins the four §2.2 already states and `_UNSTATED_CHECKS` empties; the Baron zcg is an owner data ruling (enter the loading, or correct the case) | V | M / S | — |
| 12 | **The loading search tests lateral symmetry of the discretionary subset only; the base (empty + minimum) is never tested, so "a searched loading is laterally symmetric by construction" is false** — `mass_distribution.py:1060` (and `seed_loading_search` :1251/:1293) call `_wing_points_symmetric(sub)`; the validator asks the same predicate of base + sub; one EMPTY WING POINT row at y = 100 on `ga6_normal` is mirrored to double weight in the half-span models behind a warning only; `_wing_points_symmetric` (:1127) also ignores a one-sided PANEL row, which `derived_panel_weight` (:527) halves onto both sides *(0.8.6 pre-cut review, 2026-09-22)* (#301) | The symmetry test on base + subset (or an asymmetric base refused at `database_mass_state`); PANEL rows included in the test; a guard on a one-sided fixture | V | M / S | — |
| 13 | **Delivered precision has three surviving digit counts outside the owner and two gates that do not look where the note says** — the governing safety factor is hand-formatted `f"{r.factor:g}"` in `report/tables.py:255` and `report/methods.py:337` while `front_sections.py:181` prints `1.500` (two spellings of one factor in one bundle, the D-65.6 fault; the AST gate regex cannot see a bare `:g`); `app_shell/limit_csv.py:45–50,109–111` keeps its own `round()` digit counts, invisible to the AST scan; gate 4 scans `sloads/report/` only (note 65 names `oracle_app/` and `app_shell/` too) and gate 2 runs Imperial only; surviving GUI digit counts at `app_shell/fleet_view.py:92–101`, `app_shell/sidebar.py:347–369`, `oracle_app/form.py:317–319` *(0.8.6 pre-cut review, 2026-09-22)* (#302) | Every site routed through `format_value` or exempted on the line with a reason; the scan widened to the two shell packages and to a bare `:g`; gate 2 run in both channels | V | S / S | — |
| 14 | **Minor residues of #293 and #161 in one row** — a `closure-self` load whose host is a zero-weight item with entered inertia gets `carrier=""` and falls to the pre-#293 `"all"` routing silently, and is minted `side="C"` regardless of host so a wing-carried host routes to `"all"` (`balance/closure.py:197–201`, `export/lra_model.py:1112`); `format_value(nan)` now raises and `imperial_baseline._try` swallows `ValueError`, silently dropping a channel from the digest set (`render.py:95`); the precision floor is a magnitude threshold, not the stated "would print as 0" rule, so `[0.5, 1)` prints in two notations in one column (`render.py:84`, docstring :63 still says three figures); `_air_mxx` can print `nan lb-in` into a delivered note (`select.py:552`); `oracle_sections.py:2249` hides the §3.2 variant register behind `except Exception` with a new `type: ignore`; a second copy of the centreline half-weight rule at `balance/applied.py:249` with no drift guard; the joints ASSUMED sentences print raw inches into the SI deck *(0.8.6 pre-cut review, 2026-09-22)* (#303) | Each corrected or exempted with a reason; the half-weight rule given one owner and a guard | V | S / S | — |
| 15 | **One field name means a count in one dataclass and a list in another** — `WeightEstimationInput.engines` is an engine **count** while `Project.engines` is the list of `EngineInput`, and the units walker reaches the list first, so the count has never been asked whether it is classified: it is invisible to a gate whose whole claim is totality. Harmless today only because a count is dimensionless and unconverted is right by accident, and pinned meanwhile in `tests/test_project_units.py::_KNOWN_AMBIGUOUS` as a decision on the record rather than a silence *(deferred out of note 56 as a schema change of its own, 2026-09-12)* (#276) | The field renamed `engine_count` with its lenient migration, the published field-registry path `weight.estimation.engines` moved with it, and `_KNOWN_AMBIGUOUS` emptied — removing the name is how the rename closes | V | M / S | rides the first schema hop this band forces (#286/#285 or #221) — never opens a milestone; 0.8.6 took v67 and v68 and it rode neither |
| **B9 — 0.8.8: the beam-model page, with the report polish behind it** ||||||
| 16 | **Beam-model page: the LRA definition, the model drawn, and the sbeam deck written to a chosen directory** — the LRA free-free model is the primary deliverable and the GUI has no path to it: no step, no page, no editor for `lra_mesh` or `ref_axis_pct` beyond raw JSON, and `lra_model.bdf` is written only by the CLI; the schema has called it "step 12" since v52 and no step exists. The page shows the axis (default a chord percentage, user-definable), draws the model as `scripts/plot_lra_model.py` does (iso + three views, outlines overlaid, refusal shown verbatim) and writes the **sbeam input BDF** — one writer, `write_lra_model_bdf` with the CLI's stamp — to a user-selected directory through the Report page's native picker. **Reopens note 57 D-57.6**, which retired the export page without port: this is the missing step for the deliverable, not that page ported, and a design note must say so at AGREED first. The report package does **not** carry the deck (owner, 2026-09-14): this page is the one GUI channel for it *(owner's request, 2026-09-14; moved from B2 into B9 at the same day's split, paired with #275)* (#283) | The note AGREED; the page as a step or declared non-step in `workflow.py`; the script's drawing moved to one owner the page and the script both call; no second writer, picker, stamp or figure (the #239 class) | V | L / M | a design note at AGREED first; #275 shipped 2026-09-21 |
| 17 | **Override cross-check warnings fire below display precision and print two identical numbers** *(2026-09-08 review G6)* (#243) | One owner for the comparison tolerance (display precision or a stated rel-tol) so every cross-check warning behaves the same | V | S / S | — |
| 18 | **Report polish rollup from the 2026-09-08 review** — ten tier-S presentation items in one issue so none is lost *(R13–R23)* (#240) | The ten items closed or individually declined with a reason | V | S / S–M | — |
| 19 | **Engine-installation figure legends overflow the margin on long twin designations; coincident point labels overprint** — invisible on GA6, guaranteed on any real twin *(2026-09-09 review A3)* (#256) | Legend entries wrapped or stacked inside the text width; shared-coordinate labels offset or combined *(beside #240's polish)* | V | S / S | — |
| **B2 — 0.9.0: calc, report and process work (re-chartered 2026-09-11 — the “main-GUI development” it was named for retires with #270)** ||||||
| 20 | **GUI review resumption, on the converged surface** — the review the 0.8.0 pass left unswept (Flight, Other, Ground, Plotting, Export), now against the one front-end left by #270: the fourteen pages of the generic renderer, the figure blocks of #267, the Report page and the JSON editor; findings filed at close (rule 5); re-cut follows. It inherits the one open class the #270 closures left standing — **L-8d's mutation half**, a widget that goes stale while the project is *mutated* underneath it (a seed chain, a cross-page write), which no generation bump covers and which the 2026-08-24 review and the 0.8.4 closure review (the seed button's row counter) both showed is a live mechanism *(re-scoped 2026-09-14 — the `app/views/` rows #148, #247–#252 and #259 closed with the tree they named)* (#29) | The review body completed against the surviving GUI; a reviewed list of findings, not a rework | V | S (review) / M | 0.8.4 cut |
| 21 | **`solo_close.sh` verifies fragment existence, not tier content** — nothing checks a tier-M closure touched `PROGRAM_SPEC.md`, a tier-L closure cited `theory_sources.md`, or that a physics change had a note at AGREED; hand-git bypasses are degrading the commit-subject record. The checkable subset gets scripted; the rest is named as discipline in `DEVELOPMENT_PROCESS.md` *(review R-15)* (#185) | The preflight enforcing the checkable closure obligations and validating the subject it writes | V | M / M | — |
| 22 | **Whole-pipeline-per-assertion tests, re-aimed at the coverage leg** — *moved from band D 2026-09-04* *(CR-D-6, filed from #46; hygiene; ruled 2026-08-26 (owner): option (b) — the trip figure was the coverage-instrumented run; the row is re-aimed at the run that pays for it)* (#92) | The repeated-pipeline shape gone from the coverage leg's `--durations`; the local command stays the clause's datum. **No `slow` marker** — `00_program_overview.md` §Testing states why | V | S / S–M | — |
| 23 | **The oracle form reaches into a `field_registry` private** — `oracle_app/form.py:709` calls `fr._locate(paths[0])`, the only access to a `sloads` private from either shell package *(production-release review 2026-08-27 §3.7; moved from band D 2026-09-04 — the GUI milestone is when `field_registry` is next touched)* (#130) | `field_registry` exposes the lookup publicly and `row_class` calls it; the private stays private | V | S / S | when `field_registry` is next touched |
| 24 | **The load-case index carries no loads for 344 of 347 rows** — its six load columns are the engine-mount shape (`render.load_cases_to_rows`' own docstring: *"the load components an engine mount must react"*, `load_keys.LOAD_CASE_KEYS`), and four of the five producers cannot express themselves in it: a landing case has three legs at three points, a wing case a distribution. Measured 2026-09-07: **344/347** rows on `ga6_normal`, **543/555** on `baron_58`, **587/617** on `concept_regional_jet` carry a blank load. Note 44 OR-186 answered the *deliverable* half — each structural element now has an applied-load CSV shaped for its own loads — and left the index itself, because removing or reshaping those columns touches every producer and every consumer of `load_cases_csv`. Either it is an index, in which case the load columns invite a reader to conclude a case carries nothing, or it is a load table, in which case most of it is missing *(note 44 §21 filed, §22 measured)* (#209) | A decision on what the file is, then the columns to match it — the candidate being that it becomes an index in name as well as in fact, with the per-element files carrying the loads. **Unchanged in substance by note 56**, but D-56.1 moved the case index out of the export bridge into `report/tables.py` (`case_index_rows`, `case_index_csv`) — arguably where a decision about what a *report* table is always belonged; its six load columns still come from `report/render.py`'s `load_cases_to_rows` and the file itself from `io.py`'s `load_cases_csv`, so the decision now touches three owners | V | M / M | note 44 §22 shipped; a decision on the file's purpose |
| 25 | **Measurement: how far does a power-on balance, and a body `Fx`, move a delivered load?** — `flight_envelope._balance` writes no longitudinal equation, so every balanced point is thrust-off (consistent, stated by note 44 OR-198: the drag leaves as `NX = −DX/W`); note 53's `thrust_line_fwd`/`thrust_line_aft` carry the geometry a thrust term would need, and the same `nx` is what a body `Fx` per station would apply. Three findings are one study: this row, **#217** (the entered thrust line does not steer the thrust in the balanced cases) and **#218** (the fuselage applied set is `Fz` alone). **Re-cut 2026-09-22 from a ranked tier-M physics row whose body said “parked without a rank”**: under rule 6 the first piece of work is the number, and a contract change to an oracle-locked module is not scheduled before it exists *(owner's question 2026-09-07; note 44 §23)* (#226) | The number — on `baron_58` and `atr42_100`, the movement of each delivered wing, tail and body load under a power-on balance at the thrust line and under a station `Fx = nx·m_i`, against the base-method band in `theory_sources.md` §Base-method uncertainty; then either a design note for a thrust term in `_balance` (and #217/#218's fixes), or all three parked with the number | V | S / S | — |
| 26 | **R-4's tolerance class is suite-wide, not `test_structural_speeds`'s alone** — 92 `rel_tol` values looser than Decision 3's ±0.1 %, 68 in 19 files with no justification within three lines (`test_select.py` 24, `test_landing.py` 12, `test_flap.py` 8); a passing assertion records no margin, so nothing distinguishes a rounding-limited tolerance from a disagreement nobody has looked at since *(filed 2026-09-15 from the #175 closure; issued 2026-09-22)* (#304) | Each site read and tightened or justified on its line; then the structural half — a guard refusing a tolerance looser than the file's stated band without a reason on the line | V | M / M | — |
| **C — 1.0.0: additional analysis capability (consumer-gated; design notes first)** ||||||
| 27 | The aileron's own lift increment is not distributed *(consumer-gated, not a rule-6 park: no effect number is claimed; D-29's 19 % is the air-load divergence, not this increment)* (#14) | `ACRL` wing cards gain the aero half of the couple (~70 % span); the schema fields shipped v52 and wait for data and a consumer | V | L / M | only if a consumer sizes to `ACRL` |
| 28 | **Wing fuel (and any tank/store band) is a point mass in WINGINER** — faithful to WINGINER.BAS lines 1180–1270 (every concentrated mass is a spanwise step; only the structure panel is spread), but a wet wing's fuel occupies a span band, so the point model concentrates the inertia relief and puts a fictitious jump in mid-span shear/torsion (**owner, C210 build: "fuel should be spread through the wing not just at one point mass location"**, C210-50, build review 2026-08-23) (#111) | the per-side tank item row (note 63 D-63.4, `carriage` POINT) gains a spanwise extent (`y_span`) folded into the per-strip density `w[i]`, reducing exactly to today's point when the band collapses — **not** a `WingMassInput` field, which D-63.2 empties of mass; Appendix A oracle case (concentrated gear only) untouched, lock holds. Interim: N item rows across the tank span with the same centroid — root bending and total shear identical | V | L / M | #289 and #292 shipped 2026-09-18 with the per-tank rows; **the park condition note 63 §6 set was never met** — the ATR point-vs-band number was not measured, and the metric it named (root bending) is zero by construction for a band with the same centroid. First deliverable is the tier-S measurement: mid-tank-band station shear and bending on `atr42_100`, point vs band, against the Schrenk 5–10 % datum; then rank or park on that number; design note first (physics/L) |
| 29 | Ground-case fuselage station distribution — the ground family has no per-station view *(from the #11 closure, D-28)* (#31) | Per-station shear/bending/torsion for the ground family on the fuselage beam, its own envelope beside the flight one and never merged with it, each station naming its ground case | V | L / M | a frame-sizing consumer; design note first |
| 30 | Calc-side function size (CH-8) — *moved from band D 2026-09-04; re-cut with the review's numbers: `landing_reactions` now 276, plus `envelope` 195, `build_tail_span` 176, `_export_sbeam` 173, `_manifest_rows` 155 and the three `balance` assemblers (see the R-22 comment on the issue)* (#17) | Split when touched; **the view functions wait for the GUI review (#29)**. **Re-measured at note 56's close (2026-09-12), and the forecast was wrong in one half**: `_export_sbeam` was not deleted — it lost its per-component branches and stands at **53**, off this list; `_manifest_rows` is **131**, not the 155 this row carried; `landing_reactions` (276), `envelope` (195) and `build_tail_span` (176 — untouched, but its deck consumer is gone) stand, as do the three `balance` assemblers | V | S / S | — |
| 31 | Review 2026-08-10 unscheduled findings m3–m13, m15–m18 + NITs *(defect sweep; moved from band D 2026-09-04)* (#18) | Swept opportunistically (practice 4) or promoted individually | V | S / S–M | — |
| 32 | mypy strictness ratchet — stage 2 `export/`, stage 3 `modules/`, **plus `io.py` as its own stage** (95 `Any`-typed lines, the schema boundary — the R-25 comment on the issue) *(design note 27 ST-3; moved from band D 2026-09-04)* (#19) | `sloads.export.*`, `sloads.io`, then `sloads.modules.*` added to the `[[tool.mypy.overrides]]` list and narrowed to zero under ST-4; then `warn_return_any`/`disallow_any_generics` toward `--strict` | V | S / S per stage | — |
| 33 | **No inbound channel for an externally computed load distribution** — the survivor can write a distribution and cannot read one back, so a distribution from another model cannot be checked against this analysis. Design-note work before code: which columns, which stations, which units, and what a disagreement between the two is *said* to be. `sloads/report/lra_import.py` already reads an external GRID/CBAR **model**, so the pattern exists; #245's `data/` is the outbound direction and does not cover this *(note 60 §9, amended 2026-09-13 — the home of §1.1's figure 19, which is deferred with it rather than retiring at #270)* (#279) | An agreed import contract, the channel, and the imported-against-computed overlay as its first consumer | V | L / M | a design note at AGREED first |
| 34 | **The oracle prints an aileron deflection schedule the module does not publish** — Appendix A p200 prints the deflections at VA, VC and VD (15.00 / 10.68 / 4.26 deg and their up throws); `aileron.aileron_loads` computes them internally and returns only the governing loads, so report §7 states the schedule in words and prints no numbers (OR-6 forbids re-deriving them) *(filed 2026-09-07, held unfiled while the OR-13 freeze stood; the freeze lifted at the 0.8.2 cut, so issued 2026-09-22)* (#305) | One `LoadValue` per deflection on `AileronResult`, the p200 figures as the oracle (±0.1 %), §7 printing them | V | M / S | — |

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
  taken. **Unfiled by choice**: the scope question is the work, and it is not this
  milestone's — on scope alone since 2026-09-22; the OR-13 freeze this entry
  once also cited lifted at the 0.8.2 cut and is no reason. *(Re-verified 2026-09-15 at the #280 closure: no hinge moment is
  computed for an aileron, elevator or rudder — `tail_span`'s `hinge_moment` is
  the tail attachment chain's actuator couple — and
  `AileronLoadsInput.hinges_span_in` and `actuator_span_in` are still read by
  `io`, `units` and `field_registry` and by no calc.)*

- #305 — The oracle prints an aileron deflection schedule the module does not publish *(filed 2026-09-07; held on the OR-13 freeze, which lifted at the 0.8.2 cut; issued to band C on 2026-09-22, the body moved to the issue)*.

- #218 — The fuselage applied set is `Fz` alone — is that the model, or the airplane?

- #221 — The oracle reduction resets `weight.items[].consumable`, moving a load *(promoted to band B8 on 2026-09-22 — it erases the per-case fuel state notes 62/63 built; the body is on the issue)*.

- #304 — R-4's tolerance class is suite-wide, not `test_structural_speeds`'s alone *(filed 2026-09-15 from the #175 closure; issued to band B2 on 2026-09-22, the body moved to the issue)*.
- #300 — `case_loading_checks` holds a zero-ballast loading to 1e-9 where its owner documents 0.5 in, reaches no consumer, and hides `baron_58`'s `aft gross` zcg disagreement (4.12 in) *(filed 2026-09-16 from the #257 closure; re-measured unchanged 2026-09-22 and issued to band B8, the body moved to the issue)*.

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
  owner's, and "priced, not fixed" is a legitimate answer to it. **Taken
  2026-09-22 (re-cut): priced, not fixed — unfiled by choice**; this entry is
  the note that says the lag is known.

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
