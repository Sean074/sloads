# Backlog state narrative & superseded re-cut preambles, to 2026-08-29

Rolled out of [`00_backlog.md`](../30_future/00_backlog.md) at the 0.8.2 cut
(issue #190, 2026-09-08), per the file's own precedent
([`10_backlog_state_narrative_to_2026-08-16.md`](10_backlog_state_narrative_to_2026-08-16.md)).
The backlog keeps the mission, the **current** re-cut (2026-08-29, second) with
its priority table, the open-defects index and the open design decisions; this
file holds the "Where things stand" narrative and the five superseded stacked
re-cut preambles exactly as they stood. Every re-cut below was superseded by
the one above it; the decisions they record remain of record.

---

**Where things stand (2026-08-29):** **0.8.2 (band B3, the oracle technical
report — design note 44, AGREED 2026-08-29) is the milestone in flight**,
inserted deliberately ahead of 0.9.0: the oracle report is developed and agreed
section by section first, then becomes the starting point for B2's main-report
rebuild. **0.9.0 (band B2, main-GUI development, anchored by #29) follows.** Before it: **0.8.1 is cut** —
`v0.8.1`, 2026-08-29, schema v59 (release-cut block in
[`../40_history/00_completed_development.md`](../40_history/00_completed_development.md)).
The released-defect-correction milestone: a
patch band (**B1**) opened 2026-08-28 against defects the 0.8.0 cut shipped
(re-cut below): the attitude-1 airplane-datum sign error and the dual-frame
landing output that makes it visible (#133/#134, design note 38 AGREED
2026-08-28 — **both closed 2026-08-29**, along with #139, the application-point
defect that opening #134 uncovered, [note 39](../40_history/43_application_point_note.md)),
the blank-derive crash pair (#121/#122, **both closed 2026-08-29** — the loader
refuses a `null` where `None` is not a value, which is where #121's `float(None)`
came from), and **#132** — the
released distribution claims Python 3.9 while its own dependency floor refuses
to resolve there, which is why `main`'s full-matrix run is red at the tag —
closed on the milestone branch 2026-08-28, before the band was named; the branch
is renamed `dev/v0.8.1` rather than re-cut, so the fix reaches users at 0.8.1
instead of waiting for 0.9.0. Band B1 also carries the three documentation
items the 2026-08-29 independent review of `dev/v0.8.1` raised — **#141** (the
delivered CSV states neither the frame nor the application point — **closed
2026-08-29**: both words ride on the value, as `LoadValue.point` beside
`LoadValue.frame`, and the CSV states them in a `Frame` and an `Applied at`
column; schema v58 → v59, an additive identity hop), **#140** (the guide's
landing chapter still described the pre-0.8.1 output — **closed 2026-08-29**:
chapter 14 describes the shipped two-frame, three-wheel deliverable with its
application point, and `03_conventions.md` carries the frame statement it
leans on) and **#142** (the docs-hygiene pass — **closed 2026-08-29**: the
standard and theory docs state what is rather than how it got there, every
measured effect kept in the present tense as the evidence for its rule, and the
superseded `BETA(2)` register entry no longer contradicts its own banner) —
folded in from the 0.8.2 band they were first tabled as
(re-cut 2026-08-29), and, ahead of them, the two defects found the same day
diagnosing the GA6 V-n failure: **#143** (the oracle GUI attaches a phantom
zero-coefficient LANDING set on one stray touch and saves it into the project
file) and **#144** (the calc side launders a zero lift polynomial into a 400-trip
`SolverFailure` instead of refusing it by name), one defect class in two fix
sites — **both closed 2026-08-29**: the set refuses by name at the consumer, and
an Optional record block is created and removed by a named gesture rather than
attached by a stray touch. **#145 closed 2026-08-29** — the GUI release gate
proved boot, not use; the whole-GUI journey walk it adds found the same
attachment class live in `app/views/` (the #143 fix had reached `oracle_app/`
only) crashing Results Review and Export on three of the seven bundled
examples, and swept it, with the residue filed as a B2 row. **#146 closed
2026-08-29** — an oracle cell states its provenance and no gate re-derives the
rule it checks (P-1/P-2), with the bounded sweep naming `one_engine_out` as the
one load family whose gate reads the listing its port was written from.
**Band B1 retired with the 0.8.1 cut; cut 0.9.0 when band B2 is empty.**
Before it: **0.8.0 is cut** — `v0.8.0`, 2026-08-28,
schema v57 (release-cut block in
[`../40_history/00_completed_development.md`](../40_history/00_completed_development.md)).
The oracle-GUI development milestone, 27 issues: the derive-by-default override
mechanism and its `derived_from` registry links (#97/#98/#95, note 36), the
oracle user guide with both worked-example appendices (#96, note 34), the
landing load factor entered as N (#123, note 37) with its HP-precedence sweep
finding (#124), and the four cut blockers of the
[production-release review](../50_reviews/2026-08-27_oracle_gui_production_review.md)
closed in-band (#126 the Tools station unit boundary, #127 the smoke gate boots
both front-ends, #128 a design note cannot claim unbuilt work, #129 the
container-width migration taken whole with the dependency ceiling policy
stated); the release states its maturity once (`4 - Beta`;
`app_shell.components.RELEASE_STATE`). **Band B retired with the cut; band B2
became the milestone in flight until the 0.8.1 patch band opened ahead of it
2026-08-28** (B2's anchor is still the main-GUI review #29, whose findings
drive the re-cut that owns the table).
Before it: **0.7.2 cut 2026-08-25** (`v0.7.2`, schema v55 unchanged) —
defect-only by construction: the seven `b`-class items of the C210 build review
(#76/#81/#82/#83/#84/#85/#86), closed 2026-08-24, plus the two first-order
defects the code review of the oracle GUI found inside eight lines of one
function (#88 — the row counter that deleted entered rows with no confirmation
and attached a blank CG case that stopped the flight envelope) and the **narrow
half of #71** with it (`ZeroDivisionError` out of the not-ready catch, which is
what hid it). The cut carried the re-cut of this table for the two GUI
milestones that follow
([code review 2026-08-24](../50_reviews/2026-08-24_oracle_gui_code_review.md)).
**Band A retired with the cut; band B is the milestone in flight — cut 0.8.0
when band B is empty.** Before it: **0.7.1 cut 2026-08-23** (`v0.7.1`, schema
v55 unchanged) — the 0.7.0 beta tested by building a Cessna 210 from blank in the
oracle GUI ([build review](../50_reviews/2026-08-23_c210_oracle_gui_build_review.md)):
51 findings, the two `a`'s fixed in-cycle (**none surviving**, so 0.8.0 keeps its
planned content), the whole-project results zip shipped, and seven `b`'s
(#76/#81/#82/#83/#84/#85/#86) carried to **0.7.2**. Before it: **0.7.0 cut 2026-08-23** (`v0.7.0`,
schema v55; release-cut block and delta baseline in
[`../40_history/00_completed_development.md`](../40_history/00_completed_development.md) /
[`../40_history/36_verification_baseline_0.7.0.md`](../40_history/36_verification_baseline_0.7.0.md))
— the oracle GUI beta, L-7, the hub thrust, the fixture-data pass, the
derived-scalar consolidation and the 2026-08-20 review's MAJORs; band B
(the main-GUI review #29, the docs/CI sweep #46, the beta's known issues
#67–#74) is the 0.8.0 plan, awaiting its re-cut. Before it: **0.6.0 cut 2026-08-17** (`v0.6.0`,
schema v53) — the ground/landing families, the governing SF table, discrete
control surfaces, the LRA beam model, the `CgCase` loading, wing-tank fuel
separability and one owner for every constant; every shipped fixture assembles
balanced flight and ground cases and the lateral cases carry fin-only aero.
The fixture-data pass (#9, Pri 1) shipped in full on 2026-08-17
(`changes/fixture-data-pass.*`, `changes/fixture-cg-datum-reconciliation.*`, D-27):
entered tail planforms, the ga6 fin-root pin and body outline, and the fixture CG
datum reconciled with the flight cases pinned to the WTENV limits; note 19 §10.2
(i)–(ii) are done. **L-7 shipped 2026-08-17** (`changes/l7-lateral-body-aero.*`): the lateral cases can carry the wing-body sideslip term, off by default, and state it either way. **The oracle GUI shipped OG-A…OG-F 2026-08-18/20** (note 32, `changes/oracle-gui-*`): a second
Streamlit front-end over the same calc, gates G1–G8. **The 2026-08-20 four-pass
critical review**
([`../50_reviews/2026-08-20_critical_review.md`](../50_reviews/2026-08-20_critical_review.md))
found no CRITICALs and ten MAJORs; band A of the table below is the **0.7.0**
scope (re-cut 2026-08-20).

---

# Previously re-cut 2026-08-29 (the band B3 fold)

**Re-cut 2026-08-29 (owner, in session).** The three documentation items the
2026-08-29 independent review of `dev/v0.8.1` raised — filed the same day as
**#141**, **#140** and **#142**, and tabled that day as a separate **band B3
(0.8.2)** — **join band B1 and ship in the 0.8.1 cut**. Band B3 is dissolved and
the table is renumbered densely (a re-cut owns the table); nothing is added and
nothing is dropped. Two rulings:

1. **The band that corrects a released defect carries the documentation of that
   correction.** #133/#134/#139 changed the shipped landing output — a load
   change, a second frame, and a stated application point — and #141 (the CSV
   names neither the frame nor the point the force acts at) and #140 (the guide
   chapter still describes the primed-only output) are that change reaching the
   reader. Cutting 0.8.1 without them ships corrected numbers behind an output
   and a guide that describe the numbers they replace — which is the failure
   ruling 3 of the 2026-08-28 re-cut pulled #134 into the band to prevent.
   **#142** rides with them as one pass over the same documents (rule 4), not as
   a third errand.
2. **#141 is a tier-M row inside a patch band, and that is the 2026-08-28
   ruling 3 applied a second time, deliberately.** It emits no new load and no
   new quantity — only the frame and application-point words for values 0.8.1
   already ships — and its channel (a landing methods-preamble line, which the
   CSV already has, and/or an emitted point-name row) is decided in the issue.
   #140 and #142 are tier S and prose-only. **The `app/views/` freeze is
   untouched by all three**, so ruling 4 below stands unchanged.

**Cut 0.8.1 when band B1 is empty, then 0.9.0 when band B2 is.** There is no
0.8.2 band and no 0.8.2 milestone: the milestone list is 0.8.1 → 0.9.0 → 1.0.0,
which is what GitHub carries.

# Previously re-cut 2026-08-28

**Re-cut 2026-08-28 (owner, in session).** A **0.8.1 patch band (B1)** is opened
ahead of the 0.9.0 work and the table is renumbered densely (a re-cut owns the
table). Nothing is added and nothing is dropped: four rows move up out of B2 and
D. The band exists because 0.8.0 shipped defects, and
[`../10_standard/RELEASE_PROCESS.md`](../10_standard/RELEASE_PROCESS.md) §2 makes
a verified fidelity fix its own release signal. Four rulings:

1. **The band is the 2026-08-24 ruling 1 applied to a released version** —
   defects with a first-order effect on shipped output, at any size. **#133**
   (the attitude-1 airplane-datum resolution: +14 % / −19 % on exported ground
   `FORCE` cards) is the band's reason for existing and its own row already
   named this pull as the owner's option. **#121** and **#122** join it as one
   defect class, not two rows: both are a blank registry sentinel escaping as a
   raw `TypeError` out of a derive chain, both found the same day building the
   guide's baron_58, and rule 4 does not permit fixing one and leaving the
   other. Neither has an oracle consequence; both are unhandled crashes on a
   documented, meaningful input state in a shipped GUI.
2. **#132 is a 0.8.1 row, and was already built as one.** The 0.8.0
   distribution claims Python 3.9 while its own dependency floor refuses to
   resolve there — a defect *in the released artifact*, and the reason `main`'s
   full-matrix run is red at the tag. It closed on the milestone branch before
   this band was named; the branch is renamed rather than re-cut, so the fix
   reaches users at 0.8.1 instead of waiting for 0.9.0. It carries no row here
   (it is closed) and no history is rewritten.
3. **#134 rode the patch band, and that was a stretch taken deliberately.**
   §1's table calls a new emitted quantity MINOR, and #134 emitted three (both
   frames, the fuselage-axis angle, NR/NV/ND). Design note 38 GF-6 permits
   "with or after", so the split was available and was declined: shipping the
   corrected sign without the p232 tables would deliver a load change no output
   lets the reader see. Recorded here as an owner ruling so the release-cut
   block can restate it, not as an oversight. *(Closed 2026-08-29; it grew a
   fourth emitted quantity — p233's datum moments — because the primed set
   could not leave the CSV without them, and a schema hop, v57→v58, for the
   frame the value now names.)*
4. **The `app/views/` freeze does not lift for this band.** #121 moves ahead of
   #29 with its scope cut at the seam its own body already describes — the
   *survives it* half plus the rule-4 sweep — and the layout half stays with
   the review. **#29 remains the anchor of 0.9.0**; its dependency simply
   becomes the 0.8.1 cut. Cut 0.8.1 when band B1 is empty, then 0.9.0 when
   band B2 is. (The 2026-08-29 independent review's documentation rows joined
   band B1 rather than opening a 0.8.2 band — the issues carry the 0.8.1
   milestone.)

# Previously re-cut 2026-08-26

**Re-cut 2026-08-26 (owner, in session).** Band B is unchanged in content;
this re-cut sets its **closure order** and renumbers the whole table densely
(a re-cut owns the table). Three rulings:

1. **The 0.8.0 order is dependency-driven:** #99 first (small,
   self-contained), then #97 (the collapsed-override widget, the registry
   `derived_from` link and its drift guard — the shared mechanism #95
   consumes), then #98 (its C210-29 seed half now lives at #97, so it follows
   rather than re-touch the same pages), then #95 (needs #97's `derived_from`;
   its re-shaped table is where C210-26's caption lands), then #100's
   implementation, then #94 (the text-only residue, written against the
   shipped mechanisms so no caption describes a page that then changes), and
   **#96 last** — the guide's screenshots and generated field tables capture
   finished pages (owner ruling, this session). **#100's design note is the
   band's first act** (rule 1: AGREED before code), drafted while #99/#97 are
   worked, so the tier-L row is never the long pole.
2. **#92 is ruled (b) — re-aimed at the coverage leg.** The clause's
   thresholds are written against the local command, which the 2026-08-26
   re-measurement shows already passes them; the cost is real only under CI's
   `--cov` leg on the push to `main`. The row stays band D with its
   done-condition rewritten against that leg — not closed as no-longer-tripped,
   because the whole-pipeline-per-assertion shape is confirmed and the
   refactor is small.
3. **#78 and #29 stay B2/0.9.0 with their `band:B` labels** — the milestone,
   not the label, is what separates B from B2 (#29 carries `band:B` the same
   way), so no label move is made.

# Previously re-cut 2026-08-24

**Re-cut 2026-08-24 (owner, from
[`../50_reviews/2026-08-24_oracle_gui_code_review.md`](../50_reviews/2026-08-24_oracle_gui_code_review.md)).**
The release themes are re-set by the owner: **0.8.0 — oracle-GUI development**
(it was "the main-GUI review completed"), and a new **0.9.0 — main-GUI
development and bug correction**, which is where #29 and its findings now land.
1.0.0 is unchanged. Four rulings govern the placement:

1. **0.7.2 admits defects with a first-order effect on shipped output, at any
   size** — presentation, UX and capability wait. One row qualified (the row
   counter); the narrow half of #71 came with it because it is what made the
   defect invisible.
2. **Rows are placed by fix site.** Work whose implementation is in the shared
   `app_shell/` lands in 0.8.0 with the oracle work even where the main GUI
   benefits — so **#80** (sidebar Tools, one shared implementation) and **#70**
   (the shell's unit radio) are 0.8.0 rows, not 0.9.0 ones. **#79**
   (flutter-clearance removal) and **#46** (docs/CI sweep) are neither GUI; both
   stay in 0.8.0 rather than slip two milestones.
3. **A row that genuinely has two halves is split at the seam**, not deferred
   whole: **#78** and **#21** each keep an oracle half in 0.8.0 and a main-GUI
   half in 0.9.0, as their bodies already describe.
4. **The mission stays at 1.0.0**, behind both GUI milestones. Recorded as a
   choice, not a drift: the full-span balanced free-free airplane model and the
   concept-loads → sbeam loop — the deliverable §Mission above names first — are
   now two GUI releases away. The alternative (re-ranking mission rows against
   the GUI rows on merit) was offered and declined
   (review §5.4).

The parked rows the 0.9.0 theme promotes at #29's re-cut are named in its row
below rather than moved here early, so `02_parked.md` keeps their bodies until
the review that scopes them.

# Previously re-cut 2026-08-22 for the 0.7.0 beta

**Re-cut 2026-08-22 (user, from
[`../50_reviews/2026-08-22_backlog_review_0_7_0_beta.md`](../50_reviews/2026-08-22_backlog_review_0_7_0_beta.md),
BB-1…BB-10).** The 2026-08-20 band A emptied on 2026-08-22; before cutting,
the user re-scoped **0.7.0 as a beta release of the oracle GUI** — everything
that supports a *usable* oracle GUI is in. Band A is repopulated with four
rows: **#51** (the unkeyed half of `app/views/` — reproduced data loss on a
shipped example; the reopen comment of 2026-08-22 is the scope of record) with
**#44** pulled forward to land as the same pass (the fixes share their call
sites; `unit_number_input` stamps for its callers); **#45** promoted on a
measurement — 2 of the 14 oracle pages give a fresh project wrong "run the
pages before this one first" guidance for a slice their own form enters; and
**#52** pulled forward because both duplicate fields render side by side on
one oracle page each. Two amendments to the 2026-08-20 preamble: the
`app/views/` freeze lifts **for exactly #51/#44's call sites** (`key=` + the
boundary helper; layout/behaviour stays frozen pending #29), and the schema
freeze is lifted **for exactly one hop** — #52's v55 duplicate retirement with
its reconciling migration (ordering rule below). #50 closed as a duplicate of
#51. Nothing promoted from `02_parked.md` (BB-9: the L-8 GUI rows are
`app/views/`-only or below the criterion, with the numbers). A fifth row was
added at the user's direction after the review: a **pre-cut beta review** of
the oracle GUI's function end-to-end (the 2026-08-15 candidate-review
pattern), last, so the cut signal includes it by construction. Cut **0.7.0
when band A is empty**.

**Pre-cut beta review 2026-08-22 (#61, from
[`../50_reviews/2026-08-22_pre_cut_beta_review.md`](../50_reviews/2026-08-22_pre_cut_beta_review.md),
PB-1…PB-24).** The fresh-project journey on all 14 oracle pages, the
`oracle_app/` + `app_shell/` delta and the G1–G8 rot check found the
mechanics sound and the cut **not ready**: eight BLOCKS-CUT findings enter
band A as five rows — the oracle GUI's project
is not the project gate G5 tests (`mass` never produced, items untagged,
rotors and station tables outside the reduction; **closed #62, 2026-08-23**), blank-seeded selector and
code fields that silently change loads (**closed #63, 2026-08-23**), the stale project download
(**closed #64, 2026-08-23**), no
project name (every save overwrites the last; **closed #65, 2026-08-23**), and an engine-layout state
that saves a file the loader refuses (**closed #66, 2026-08-23**; band A empty — cut 0.7.0). Sixteen KNOWN-ISSUE findings go to band
B as rows 11–18 (release notes for 0.7.0; fixed in 0.7.x/0.8.0). The cut
signal is unchanged in form: **0.7.0 when band A is empty**.

**Previously re-cut 2026-08-20 (user, from
[`../50_reviews/2026-08-20_critical_review.md`](../50_reviews/2026-08-20_critical_review.md)).**
The release themes are fixed by the user: **0.7.0 — the oracle GUI fully
functional**, plus the review's non-GUI MAJOR defect fixes (defects outrank
capability, rule 6); **0.8.0 — the main-GUI review (#29) completed and its
findings addressed** (#29 and every CR-D finding move wholesale out of the
0.7.0 band); **1.0.0 — additional analysis capability** (the former band-B
consumer-gated rows move there). Band A is ordered by fix dependency: the
shared shell first (both GUIs inherit CR-D-1), then the oracle form's persist
path, then one-owner-at-render (which closes the two top-ranked backlog items
riding it), then scope/nav polish, then the six non-GUI MAJORs grouped by
fix-site, with **#33 promoted from band C** per the review's §6 rank 2 (its
band-C placement under-ranked its blast radius). The review's MINOR/NIT
findings are one sweep row, worked with their modules (practice 4). **No
schema hop is needed anywhere in band A** — every fix is widget-, test-,
guard- or report-side; the schema freeze holds through 0.7.0. The Streamlit
freeze splits: `oracle_app/` + `app_shell/` are **open** for exactly the band-A
rows; `app/views/` stays frozen pending #29 (0.8.0). Cut **0.7.0 when band A
is empty**.

**Previously re-cut 2026-08-17 (user, from
[`../50_reviews/2026-08-17_backlog_review_0_7_0.md`](../50_reviews/2026-08-17_backlog_review_0_7_0.md),
BR-1…BR-13).** Band A is now the **0.7.0** scope: the fixture-data pass first
(it carries the `ga6_normal` body outline the headline needs and closes the
WTENV-envelope defect), then **L-7 lateral body aero as the headline** (**shipped 2026-08-17**, note 19 rev. 3, schema v54; `changes/l7-lateral-body-aero.*`) — then the hub thrust card (**shipped 2026-08-17**, issue #10, tier M; note 21's carve-out on L-7's v54 field, `changes/hub-thrust-force.*`), the combined station envelope (**closed
2026-08-18 as decided-against**, decision **D-28**, `changes/no-combined-station-envelope.*`:
flight and ground fuselage cases are assessed with different internal-pressure
companion cases, so no envelope over both is supportable from a tool that
excludes pressurization — the two families stay separate deliverables and the
ground family's own missing per-station view is filed as **#31**, band B),
the recorded decisions (**closed 2026-08-18**, decisions **D-29**/**D-30**/**D-31**,
`changes/recorded-decisions.*`: the derived `ACRL` point names SELECT's own pick;
the ATR-42's Mach-capped corner is ordinary stall-limited flight, with the real
finding — coefficients evaluated past their fit on nine published rows, no
governing load affected — filed as **#32**/**#33**; and the gust-shape study
**merged** in, reusing Schrenk being inside the Schrenk band by construction, so
a decision and not work; #12 closed into #13), and the **GUI review** (#29) the user asked for,
which re-opens the UI freeze to the extent its findings justify. Nothing was
promoted from `02_parked.md`; the aileron increment stays in band B; band C is
unchanged. Schema: the freeze is lifted for exactly L-7's additive hop; anything
else rides it or waits. Cut **0.7.0 when band A is empty**.

**Previously re-cut 2026-08-16 (user, from
[`../50_reviews/2026-08-16_scope_and_deficiency_review.md`](../50_reviews/2026-08-16_scope_and_deficiency_review.md)).**
The review sorted every row against the **base method's own error bar** rather
than by mission trace alone, and three things changed: (1) **band A is now the
whole of 0.6.0** — the first-order defects in shipped output, the units and
gate gaps, and the code-health items that make every later session cheaper;
the release is cut when band A is empty and **nothing in band B holds it**;
(2) **step 14 is descoped** from "real stiffness" to a `PBAR`/`MAT1`
pass-through (§2.3 of the review; shipped 2026-08-17 as consumer-*editable*
per-family cards, no input path) — the indeterminate-path half is parked;
(3) **fourteen rows are parked** to
[`02_parked.md`](02_parked.md) ("Parked 2026-08-16") — the band-E physics
that adds fidelity above the base analysis (power effects' seven-step plan,
Multhopp `Cm`, the pitching load factor, per-CG inertia), the whole band-H
Part 25 pack, and the fixture-only rows — with bodies kept in full. Two
standing rules were added to the ordering rules below: the
**effect-vs-error-bar rule** and a **schema freeze through 0.6.0**. Bands
A–C are a reading aid; the **Pri** column is the order.

Previously re-cut 2026-08-15 (post-0.6.0-headline: defects interleaved by
severity, band C from D-25), 2026-08-13 at the 0.5.0 tag, and 2026-08-10 from
the 0.5.0 code review
([`../50_reviews/2026-08-10_code_review_0_5_0.md`](../50_reviews/2026-08-10_code_review_0_5_0.md))
and its user-resolved decisions **D-R1…D-R8**
([`../40_history/03_resolved_decisions.md`](../40_history/03_resolved_decisions.md)).
The 0.5.0 scope and the 0.6.0-candidate review's rows
([`../50_reviews/2026-08-15_review_0_6_0_candidate.md`](../50_reviews/2026-08-15_review_0_6_0_candidate.md))
are gone from this table under the removal rule; what shipped is in
[`../../CHANGELOG.md`](../../CHANGELOG.md) and
[`../40_history/00_completed_development.md`](../40_history/00_completed_development.md).
Review finding IDs still cited per row (m\*, CH-\*) resolve in their review
document. Historic step numbers (steps 8–14) are kept inside item names for
traceability with plans 09/11/12/13; the **Pri** column is ordinal only.
