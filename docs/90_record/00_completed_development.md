# Completed Development

The authoritative record of what has shipped: completed modules/phases, key
decisions, and resolved defects. Items move here from
[`../30_future/00_backlog.md`](../30_future/00_backlog.md) the moment they close,
with a matching `CHANGELOG.md` entry.

Each entry uses the step format: **Objective**, **Deliverables**, **Test /
Acceptance**, **Key decisions**.

**Live cycle only.** This file holds the current release cycle plus the previous
release cut. Older blocks roll into frozen, do-not-edit archives at each release
(`RELEASE_PROCESS.md` §4): the 0.8.6, 0.8.5 and 0.8.4 cycles with the 0.8.5,
0.8.4 and 0.8.3 cuts are in
[`67_completed_development_to_0.8.6.md`](67_completed_development_to_0.8.6.md),
the 0.8.3 cycle and the 0.8.2 cut in
[`62_completed_development_to_0.8.3.md`](62_completed_development_to_0.8.3.md),
the 0.8.2 cycle and the 0.8.1 cut in
[`59_completed_development_to_0.8.2.md`](59_completed_development_to_0.8.2.md),
the 0.8.1 cycle and the 0.8.0 cut in
[`51_completed_development_to_0.8.1.md`](51_completed_development_to_0.8.1.md),
the 0.7.1 and 0.7.2 release cuts in
[`41_completed_development_to_0.8.0.md`](41_completed_development_to_0.8.0.md),
the 0.7.0 cycle and the 0.7.0 cut in
[`37_completed_development_to_0.7.1.md`](37_completed_development_to_0.7.1.md),
the 0.6.0 cycle and the 0.5.0 cut in
[`35_completed_development_to_0.6.0.md`](35_completed_development_to_0.6.0.md),
everything before 0.5.0 in
[`11_completed_development_to_0.5.0.md`](11_completed_development_to_0.5.0.md).
Tier S closures do not write here (a `changes/` fragment is their record); tier M
writes one paragraph, tier L the full step format — **as a `changes/<slug>.history.md`
fragment** (design note 28 MD-4), rolled to the top of this file at release cut, so
concurrent PRs never edit the same line here. Only the release-cut block itself is
written directly, by the release manager.

---

## Release cut: **sloads 0.8.7** (the deck carries what the airplane carries — the engine, the one-engine-out fin, the complete rolling conditions), tag `v0.8.7`, 2026-09-27

**Objective.** Close band **B8**, re-chartered on 2026-09-22 as *the deck
carries what the airplane carries*: the report polish the band was first named
for moved behind #283, and the rows that left a load the airplane flies out of
the one deck that ships moved in. Three were the milestone: the engine-mount
conditions (#286) and the one-engine-out fin (#285), designed in one pass as
design note 66, and the accelerated roll derived as the regulation states it
(#306, note 52 re-agreed). The rest were the mass-state residues note 63 left
(#221, #300, #301) and the precision residues of note 65 (#302, #303). The
band emptied on 2026-09-27 with #310, #276 and #311; the pre-cut release
review (#313–#322) found the cut not clean — one CRITICAL, five MAJOR — and
the owner banded the four that block it back into B8 (#313–#315, #317), the
third milestone running to take that round trip.

**Deliverables** (the `[0.8.7]` changelog section is the release note):
- **The rolling conditions arrive complete (#306, note 52, tier L).** The
  delivered `ACRL` side carries condition A's lift, not the roll point's
  average; the other side is the Amdt 23-48 75 % at every weight (registered
  in `02_approved_corrections.md`); the unbalanced moment derives from the
  pair and the TORS case carries its aileron increment. #315 made the couple
  SELECT and report 3.3 publish the one the chain flies when a user enters it.
- **The deck carries the engine (#286, #285, note 66, tier L each).** Every
  23.361/23.371 mount condition that pairs with a flight state is an assembled
  free-free case at the engine's own nodes; ONENGOUT's peak instant is an
  assembled lateral case on a 1 g parent with the engine pair beside the fin,
  and the fin load now resists its engine's yaw — the sign OR-173 was
  implemented with is reversed, approved by the owner in session on
  2026-09-26 after the fix had shipped (note 44, note 66 §11). #313 made a
  condition that prescribes an engine's thrust replace the entered one, so no
  hub carries two.
- **The mass state holds (#221, #300, #301, #314, tier M each).** The oracle
  reduction keeps each case's loading; a case's waterline is its loading's,
  checked to 0.5 in on station and waterline both, and re-seeding is a fixed
  point; the half-span wing models are fed through one projection that
  refuses an unmirrored wing mass state.
- **Files a release wrote stay readable (#310, #276, tier M/S).** From this
  release on every release's schema is recorded in `RELEASED_SCHEMAS` with a
  frozen fixture, and the hop chain must reach it without a gap; the v55–v69
  hops and the readers' legacy branches are gone.
- **Precision and tooling (#302, #303, #308, #311, note 66 follow-up, tier S).**
  Every delivered and on-screen number takes its digits from its unit; a
  non-finite value is refused; the balanced deck resolves the envelope once;
  the suite's shared bundles build once per worker behind a `slow` lane; the
  oracle journey converges on `atr42_100` again.
- **A zero prints unsigned whatever the Python version (#324, tier S).** The
  release PR's CI (#323) failed on the regional jet's balanced-deck digest,
  and so had every `dev/v0.8.7` push since #286: the gyroscopic engine-mount
  headers printed a zero-by-construction closure load factor with the sign of
  its solve residue, `+0.00000` on Python 3.11 and `-0.00000` on 3.12. Both
  print sites now read one snapped owner; the ATR 42's eight such headers move
  to `+0.00000` and its deck digest is regenerated, and no load card moves.
- **A test regex that loads on Python 3.10 (#325, tier S).** `main`'s full
  CI run after the merge failed on the 3.10 leg alone: #303's unit guard in
  `tests/test_joints.py` used a 3.11-only atomic group. It now uses the
  lookahead-and-backreference spelling, and the tag waited for the fix.
- **The release review's closure debt (#317, tier S).** Note 66 gained its
  theory citation and gate rows, note 63 records the symmetric wing mass rule,
  and no fragment describes the deleted hop.
- **Docs-only commits on the branch:** design note 66 PROPOSED and AGREED
  (Q1–Q7 as recommended), note 44 OR-173 amended, and the owner's bandings of
  #312/#309 into B9 and #313–#315/#317 into B8.
- **Version** `0.8.6` → **`0.8.7`**. Schema **v68 → v70**: v69 at #306
  (`WingLoadCase.unbal_moment` optional) and v70 at #276 (`engine_count`),
  both with no hop, since #310 made the first released schema the floor and
  neither was released. **`RELEASED_SCHEMAS` gains its first row,
  `"0.8.7": 70`**, frozen as `tests/fixtures_schema/release_0.8.7.json`
  (a copy of `examples/ga6_normal.project.json`).
- **Changelog cut** — `scripts/build_changelog.py 0.8.7 --date 2026-09-27`:
  **17 fragments** consumed — 7 into `## [0.8.7]` directly and **10 history
  entries** rolled to the top of this file, their changelog bullets derived
  from their leads — and a fresh empty `[Unreleased]` opened. #324's bullet
  was written into `## [0.8.7]` by hand afterwards: the release PR's CI found
  it after the cut (below).
- **Record roll** (`RELEASE_PROCESS.md` §4 step 3): no note moves (note 61
  CV-3). This file stood at 1,461 lines before the cut and 1,803 after
  the fragments, over 1,500, so everything below the 0.8.6 release-cut block
  (the 0.8.6 cycle and the 0.8.5, 0.8.4 and 0.8.3 cuts) moved verbatim to
  [`67_completed_development_to_0.8.6.md`](67_completed_development_to_0.8.6.md);
  587 lines remain. The changelog stood at 967 and 1,110; it did not
  roll.
- **Verification baseline** (§4 step 5): unchanged from
  [`36_verification_baseline_0.7.0.md`](36_verification_baseline_0.7.0.md)
  but for the one registered correction: the 23.349(a)(2) 75 % moves the
  Appendix A airplane's derived unbalanced rolling moment from the printed
  149,043 to 128,619 lb-in and the `AC ROLL` load factor to `0.875·n₁`, each
  figure stated in `02_approved_corrections.md` and asserted in
  `tests/test_rolling_conditions.py`. Every other Appendix A assertion is the
  same test on the same printed number.
- **Gates at cut:** `pytest` **3,901 passed / 11 skipped / 2 xfailed / 0
  failed** (3,742 passed / 9 skipped / 2 xfailed at the 0.8.6 cut) on
  `28b72d4`, the tip before the cut commits, with the cut's own guards
  (migrations, doc currency, links, fragments, backlog) re-run green after
  them; `ruff` clean, `mypy` clean (`sloads/`, 112 source files),
  `scripts/smoke_test.sh` **PASS**, `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on
  7 tracked keys, the §3.5 by-hand walk done by the owner
  (2026-09-28). Of the 2026-09-27 review's CRITICAL/MAJOR findings,
  #313–#315 and #317 closed on the branch;
  **two MAJOR stay open by the owner's banding ruling of 2026-09-27**, which
  named the four above as the cut's blockers and left the rest unbanded: #316
  (a NaN still swallowed by `package_data` and the report's broad
  `except Exception` sites — #303's rule not yet swept) and #318 (note 66 and
  52 gates that re-derive what they check). #319–#322 are decisions and
  minors.

**Key decisions.** *A load the airplane carries is not delivered until the
deck carries it.* The band was re-chartered on that sentence, and each of its
three large rows found a quantity the report printed and the one shipped deck
did not hold — the engine, the one-engine-out fin, condition A's lift on the
rolling side. The second decision repeats 0.8.6's: an emptied band is not a
release until a critical read of the whole branch says so. This one found a
thrust counted twice on a gyroscopic case and a published couple that was not
the one flown; the round trip cost a day and four rows. The third is recorded
where it was made late: #285 reversed the fin-load sign OR-173 was
implemented with before the owner saw it, and the approval stands in three
places that now say the same thing. The last was learned at the merge: the
fast gate on `dev/v0.8.7` was red on every push from #286 to the cut, on one
Python-version byte (#324), and no close stopped on it because
`solo_close.sh` gates locally and reads CI after the push. The release PR was
the first place anyone read it; a close that waits for CI is left to the owner.
The merge then found the other half of the same gap: 3.10 and 3.11 run only on
the push to `main`, so a 3.11-only regex in a test (#325) surfaced after the
milestone PR had merged, and the tag waited on a second PR.

- **The accelerated roll's published couple is the one flown: the variant table resolves ACRL through the same owner as the wing chain and the balanced deck, so an entered unbalanced rolling moment reaches SELECT, report 3.3 and the Wing Loads caption (#315, tier M, 2026-09-27)** —
  The wing chain and the balanced deck resolve the ACRL case through
  `rolling.complete_rolling_case`, where an entered `unbal_moment`, `cl` or
  `v_eas_kt` wins over the condition A derivation (design note 52). The
  `wing_variants` table derived all three regardless, and SELECT publishes
  the governing row, so the regional jet flew its entered -600,000 lb-in
  while SELECT and report 3.3 published the derived -1,614,422 lb-in and a
  roll acceleration built from it. The table now resolves each ACRL row
  through `complete_rolling_case`, with the entered case named by the new
  `rolling.entered_rolling_case`. The row records which fields were entered
  and keeps condition A's CL, speed and root bending as separate fields.
  SELECT labels an entered couple *(entered)* and publishes an entered air
  point beside condition A's. Report 3.3 names the entered value and states
  the derivation for comparison, and the GUI caption decides entered versus
  derived from the input instead of comparing numbers. On the regional jet
  every ACRL row's net root bending rises by about 480,000 lb-in (less roll
  relief), the governing row is unchanged (fwd gross, case 180), and so is
  every delivered wing and deck load; the other four fixtures enter no
  couple and do not move. The Imperial baseline moves on the regional jet's
  SELECT CSV and text report alone, and the digest is regenerated. A gate
  in `tests/test_rolling_conditions.py` holds SELECT's published couple to
  the wing chain's and the balanced deck's on every fixture.

- **A case's waterline is its loading's: a loading with no ballast counts as its case only within 0.5 in on station and waterline both, both seeds write back the waterline of the loading that closes each case, and `case_loading_checks` holds every case to that and is stated under the oracle report's 2.2 case table (#300, tier M, 2026-09-26)** —
  The subset search accepted a no-ballast loading (a subset that already
  weighs the case, or a ground case's fuel burn-down) on its station alone, so
  a loading could sit anywhere in waterline under a case whose `zcg` every
  balance, trim and gear module reads. The check meant to see that was wrong
  and unrouted: it held a no-ballast loading to 1e-9 — false failures on
  `ga6_normal`'s CG4 (0.0024 in, the very precedent the 0.5 in tolerance was
  written for) and `baron_58`'s `aft gross` xcg (0.35 in) — read flight cases
  only, and sat on `_UNSTATED_CHECKS` with no consumer. The search now tests
  both coordinates (`mass_distribution._cg_matches`); the check applies that
  band, covers ground cases, and is stated in the 2.2 case-table note, naming
  any case whose loading is not the case; `_UNSTATED_CHECKS` is empty. The
  sweep found the class three times. `baron_58` `aft gross` flew at 95.88
  against a stated 100.0 (4.12 in) and `concept_regional_jet` `fwd max
  landing` at 64.82 against 62.66 (2.16 in). And `cg_cases.seed_landing_cases`
  wrote every ground case's `zcg` as the whole database's waterline and never
  re-echoed it (D-26a), so the search solved ballast to reach that
  placeholder: 1,607 lb at the lowest item of `atr42_100` (z 60) under both
  max-landing cases, 1,946 lb near its top (z 218.7) under `fwd light`. Both
  seeds now share `cg_cases._echo_loading_waterlines` (search on station, write
  the found loading's waterline back); `derive_case_loadings(...,
  match_waterline=False)` exists for that step alone. Owner rulings: each case
  takes its loading's own waterline rather than a solved ballast the airplane
  does not carry — Baron `aft gross` 95.88, RJ ground 61.96 / 64.82 / 63.08,
  ATR ground 141.56 / 141.56 / 132.33; ATR's `aft max landing` ballast falls to
  1,007 lb at z 163.4 and the others move onto their loading's line. Delivered
  effect, three fixtures (`ga6_normal` and `concept_heavy` are byte-identical):
  Baron's governing horizontal-tail up-gust root bending 36,248 → 36,543 lb-in
  (+0.8 %), CHECKED MAN UP 13,398 → 12,926 (−3.5 %), the non-governing BAL UP
  RETRACTED 3,889 → 3,133; its one-engine-out pre-closure My residuals mostly
  fall now that the reference is the mass centre (VD −11,102 → 1,697, VC
  −7,055 → 95 lb-in) while VS rises to 0.7 % of n·W·MAC (−762 → −2,542). The
  critical nose-gear reactions rise 1.5 % on ATR (level landing Fz 21,918 →
  22,248 lb) and 1.2 % on the RJ (braked roll 8,752 → 8,859 lb); no flight,
  net or body load moves on either. The Imperial baseline was regenerated for
  those three (Baron 24 channels, ATR 8, RJ 8). Not in scope and unchanged:
  Baron's `fwd gross` and `fwd regardless` need 720 lb (13 %) of ballast, past
  the credibility gate, and reach no deck (filed as #309).

- **A condition that prescribes an engine's thrust replaces the entered one: the 23.371(b)/25.371 gyroscopic case's engine carries ENGLOADS's max-continuous thrust alone and a one-engine-out case ONENGOUT's pair alone (#313, design note 66, tier M, 2026-09-27)** —
  An entered `thrust_lb` (#10) is applied at every engine's hub in every
  flight case, and the engine-mount builder keeps it unscaled on purpose; the
  gyroscopic increment then added ENGLOADS's thrust at the same hub, and the
  one-engine-out case added ONENGOUT's live-thrust / windmill-drag pair beside
  the entered thrust on both engines. On an `atr42_100` copy with 4,000 lb
  entered per engine the left engine's gyroscopic case carried 14,865 lb
  (10,865 + 4,000), and the one-engine-out case gave the failed engine 4,000
  lb of thrust beside its 13,004 lb windmill drag and the live engine 5,921 lb
  (1,921 + 4,000). `hub_thrust_set` now tags each hub force with its engine
  (`carrier = engine-<i>`, the D-66.6 rule, so an entered thrust also routes
  to its own engine's LRA member) and leaves out the engines a condition names
  as `replaced`, saying so in band: a gyroscopic case's parent is assembled
  without its own engine's entered thrust, the other engines keep theirs, a
  torque case keeps all, and an engine-out case — ONENGOUT models a twin, so
  its pair is the whole thrust state — carries none. The "Applied engine
  thrust" row and `is_powered` read the entered thrust only, as they did; the
  engine-mount docstring's claim that ENGLOADS's thrust made a case powered is
  corrected (the family's gate exemption is `is_engine_mount`). Latent: no
  shipped fixture enters thrust, so no delivered load, card or case moves.
  Gate G-12 in `tests/test_hub_thrust.py` — no hub in any case of a powered
  build carries two thrusts; the gyroscopic engine's thrust is the unpowered
  build's; the engine-out pair is the unpowered build's.

## Step — The deck carries the engine: every 23.361/23.371 mount condition that pairs with a flight state is an assembled free-free case at the engine's own nodes, and every balanced case states its own safety factor (#286, design note 66 D-66.1…D-66.9, tier L, 2026-09-26)

**Objective.** Close #286: ENGLOADS computed every engine-mount condition and
the LRA deck had a mount and a hub node per engine since note 24 R-9, yet no
engine condition reached the deck — a nacelle, mount or attachment sized from
it saw no engine case, and the deck said nothing about the absence. The owner
agreed design note 66 the same day (Q1–Q7 as recommended).

**Deliverables.** A new balanced family, `balance/engine_cases.py`, appended
after the ground families: per engine, never mirrored, ids ENGLOADS's own
`EM-nn`. Each case is an assembled flight case in SELECT's delivered PHAA block
(PHAA's point for 23.361(a)(1)/(a)(2), `BAL C` for (a)(3) and FAR
25.361(a)(3)(i)/(ii), `MAN A` for 23.371(b)/25.371) scaled by one constant to
the load factor ENGLOADS states for the engine, plus the engine's own torque,
gyroscopic couples and thrust through `coordinates.engine_applied_load`, at the
mount and hub nodes of that engine. ENGLOADS's vertical is never re-applied —
the engine's mass is in the parent's inertia at that `n`. The torque is trimmed
by an equal and opposite `aileron-trim` couple (note 21 P-9); the gyro couples
and thrust are closed by the rigid-body relief. 23.363 and 23.361(b)(1) are
mount-local and named in the deck's not-assembled block with their reason. The
LRA model gains a member per engine and routes an EM load by its `carrier`.
Every balanced case now stamps its own safety factor from the governing table
(`safety_factors.stamp`), so the deck's basis sentence states the case's factor
rather than the field's default — 1.5 everywhere today. Each gyroscopic sign
combination is now a condition with its own `EM` id (`engine.split_gyro`,
`mount_conditions`; the render-time `a`–`d` suffix retired), and 25.371's A2
vertical is read wherever the 2.5 g one was (`load_keys.FZ_VERTICAL_A2`).
One Imperial digest wave, 26 channels: the balanced and LRA decks, the balance module's CSV and text and the case index move on the four engine fixtures (the EM subcases, the not-assembled engine lines); the engine CSV, text and applied-load file move on the two turboprops (the gyro split's ids; the RJ's 25.371 vertical, 0 before). `concept_heavy` has no engine and did not move.

**Test.** `tests/test_engine_mount_cases.py`: the deck carries exactly the
ruled set per fixture (G-66.2); every case's SF is the table's (G-66.1); each
EM case flies at ENGLOADS's `n` with no re-applied vertical, and the itemised
engine weighs ENGLOADS's `PPWT` to the pound where the database itemises it
(G-66.3); the increment is `engine_applied_load` of ENGLOADS's scalars and
lands on its own engine's nodes (G-66.4); every case closes in six DOF (G-66.5);
the torque nets no roll and no EM case is handed (G-66.7); the RJ's 25.371
rows carry their vertical (G-66.12). The round-trip solve gate passes on every
engine fixture with the new subcases (G-66.6).

**Key decisions.** (1) The regional jet's database lumps both engines as one
3,400 lb centreline row against ENGLOADS's 2 × 1,550 lb: its EM cases are
correct for the airplane as entered, and the discrepancy is recorded in note
66 §10, not fixed. (2) The family is exempt from the flight trim gate — the
case it scales is gated as itself — and is judged by G-66.x. (3) The gyro split
renumbers the turboprops' later EM ids (the ATR's right engine moves from
EM-07… to EM-10…).

## Step — The one-engine-out fin reaches the deck: ONENGOUT's peak instant is an assembled lateral case on a 1 g parent with the engine pair beside the fin, and the fin load it publishes now resists its engine's yaw (#285, design note 66 D-66.10…D-66.16, tier L, 2026-09-26)

**Objective.** Close #285: SELECT names ONENGOUT's 23.367 fin conditions on
every twin — on the ATR 3.6x its largest static fin case, the fin and aft
fuselage's sizing load — and the assembler skipped all of them as out of
family, on a deferral to a per-component fin deck that note 56 deleted.

**Deliverables.** A new balanced family, `balance/engine_out_cases.py`,
appended after the engine-mount family: each recovered ONENGOUT condition at
its instant of peak total fin load, assembled on FLTLOADS's 1 g point for the
speed (`BAL C` / `BAL D` / `STALL 1G`) at the heaviest derivable FLIGHT CG case
and the V-n altitude nearest ONENGOUT's, carrying the fin distribution
`tail_span` builds and the engine pair at that instant — the live engine's
thrust at the mirror of the failed hub and the failed engine's remaining
thrust and windmill drag at its hub, from `one_engine_out.engine_forces_at`,
the march's own schedule. One engine's failure is computed per speed; the
mirrored engine's is its reflected twin under its own VT id. No L-7 term, said
in band; unrecovered marches recorded (`not-recovered`). The 23.367(a)(2) cases
state `ULT SF=1.0` through #286's stamp. **The published fin sign is
corrected**: ONENGOUT gave every fin load (and δ, α_tail) the sense that adds
to its own engine's yaw while its β carried the nose's; the fin now resists
(`+y` engine → `+y` fin load, SELECT's static convention) and β keeps the
nose's sense. Magnitudes and the fin envelope are unchanged; which engine's
case carries which sign flips. One Imperial digest wave, 32 channels: on the two twins the balanced and LRA decks, the balance output and the case index gain the family, and the one-engine-out, tail-span, chordwise and v-tail applied outputs move with the sign correction (12 each); on the other three fixtures only the deck headers and the balance text move, for the reworded out-of-family sentence.

**Test.** `tests/test_engine_out_cases.py`: one computed case and its twin per
recovered speed (G-66.8); the closure's yaw is ONENGOUT's ψ̈ after the Izz ratio
to 2–3 % (G-66.9, gated at 5 %); the fin opposes the engine pair, and a
positive β carries a negative fin load; each twin carries the other engine's
own fin load (G-66.10); the ATR's unrecovered VS is recorded (G-66.11); SF 1.0
on 23.367(a)(2) (G-66.14); no L-7 load and the statement in band (G-66.15);
the 1 g half closes inside 1 % (G-66.16); `engine_forces_at` reproduces the
march's engine moment at every instant.

**Key decisions.** (1) The sign correction reverses the fin-load sign note
44 OR-173 was implemented with (its one-case-per-engine rule stands) — found
because the balanced case is the first place the fin and the engine met;
recorded in note 66 §11 and approved by the owner in session, 2026-09-26
(after the fact: the fix shipped in 60c90ab before the owner reviewed it).
(2) The family is exempt from the trim gate for the engine pair's pitch couple (6.4 % of n·W·MAC on the
ATR's VC case — the pair's axial force at the hub waterline), the powered
cases' standing; the 1 g half is gated instead.

- **The half-span wing models are fed through one projection, `mass_distribution.half_span`, which refuses a wing mass state whose off-centreline parts are not mirrored pairs instead of running it as one side doubled (#301, tier M, 2026-09-26)** —
  The item database is full span (every row at its own butt line), but
  WINGINER (whose BASIC hangs every concentrated weight at a positive butt
  line), the balanced deck's wing set (the starboard half, mirrored) and the
  per-case tie are half-span models. The symmetry they depend on was checked
  in three places over three different sets of rows. The subset search and
  the seed search tested the discretionary subset alone, never the empty and
  minimum rows under it. Only POINT rows were counted, and by weight sum. The
  deck built its own starboard point set with its own copy of the centreline
  half-weight rule. Measured on `ga6_normal` with one 50 lb `EMPTY` wing row
  at y = ±100: a starboard POINT row reached the half-span models doubled
  (100 lb) and a port one was dropped (0 lb), each behind a warning while the
  search still called the loading valid. A one-sided PANEL row was halved
  onto both wings with no finding at all. Owner ruling (in session): build the
  projection now rather than a per-side deck (tier L, parked while no
  delivered load comes from an asymmetric mass state), and **refuse**; design
  note 63 §13 records the rule and supersedes its §10 amendment (a). The
  projection is the one place the rule lives: every off-centreline `WING`
  part, PANEL or POINT, must have a mirror image (same weight, x and z,
  opposite y, within `RECONCILE_REL_TOL` and 0.5 in). This is a pairing, not
  a weight sum, and a state that fails raises `WingAsymmetric` naming the
  parts. The search and seed search test base and subset together through
  `wing_symmetric`, and the seed search no longer trims one row of a mirrored
  pair. An asymmetric entered loading is not derivable, so the deck, WINGINER
  and the body beam refuse it by the route they already take for an
  unreachable case, with the parts in the reason. `validation`'s
  `wing_mass_asymmetric` now names a database that fails; the deck's point set
  and `WingMassState` read the projection (`port_point_weight_lb` and
  `_wing_points_symmetric` are gone). Every shipped fixture's database and
  every loading already pair exactly, so no output, digest or baseline moves.
  Guards: every shipped mass state is an exact half span; a one-sided POINT
  (either side) or PANEL row is refused by name at the projection, the mass
  state and the validator; the search refuses an asymmetric base; and a
  weight-balanced pair at unmirrored stations is refused. The SSOT row is in
  `CONVENTIONS.md` §7.

- **The oracle reduction keeps each case's mass state: the `consumable` flag and an entered `loading` survive it, so the oracle report names the loading the analysis flew and a loading edit moves its fingerprint (#221, tier M, 2026-09-26)** —
  `field_registry.reduce_to_oracle_inputs`, which the oracle document and its
  fingerprint are built from, reset every field outside the oracle input set,
  and the loading model is sloads-only: every tank read as payload and every
  entered loading was replaced by a search. Measured on `atr42_100` before the
  fix: fuel 9,874 → 0 lb at MTOW and 700 → 0 at MZFW on all eleven cases,
  eight entered loadings searched instead, and the search adding up to
  1,669 lb of ballast the airplane does not carry; all five fixtures moved.
  Wing loads did not (total weight, CG and wing mass are unchanged) — the
  defect was in what the document states. The fix is a new registry
  declaration, `KEPT_BY_REDUCTION`, each entry with its reason, which the
  reduction honours and the GUI tiers and the supplied-set dial do not see
  (`supplied` was rejected: it would render the fields as original-suite
  inputs, and no Appendix A oracle depends on them). One reduction serves G5
  and the document alike. The G5 module comparison could not see the defect
  (fuel reclassified as payload moves no oracle-page value), so the guard
  compares the mass state itself — `mass_case_summary` equal on the full and
  reduced project for every shipped example — and the test that asserted the
  loading was dropped now asserts it is kept. The backlog row's `carriage` was
  already `supplied` (design note 63). MZFW and crew were swept and stay
  plain: they seed and check cases, and state no case's mass.

- **A project file is readable if a release wrote it: from 0.8.7 on every release's schema is recorded and frozen, and the hop chain must reach it without a gap; the v55–v69 hops, their fixtures and the readers' legacy branches are gone (#310, tier M, 2026-09-26)** —
  Owner ruling (in session): compatibility is kept at release level, starting
  at 0.8.7. A file any release from 0.8.7 on wrote stays readable by every
  later release; a schema version that lived only on a development branch is
  never promised. Before this the gate read v55 onward through fourteen hops
  that carried files no one holds (the project is pre-production and the owner
  keeps no project files outside `examples/`), and #276 was waiting for a
  schema hop to ride. `sloads.migrations` now keeps the gate and the machinery
  (`migrate`, the `MIGRATIONS` chain, `migration_notes`) and adds
  `RELEASED_SCHEMAS`, empty until the 0.8.7 cut. `SUPPORTED_FLOOR` is the
  oldest released schema, or the current one while none is recorded. The rule
  is held by `tests/test_migrations.py`. Every release the changelog names from
  0.8.7 on must have a row, so the cut's new header turns the suite red until
  it does. Every row's frozen `tests/fixtures_schema/release_<X.Y.Z>.json` must
  load. And the chain must run from the floor to the current version without a
  gap, since the reader drops unknown keys and a bump with no hop would misread
  a stale file rather than refuse it. The step is in `RELEASE_PROCESS.md` §4.
  With no hop left to reach them, the readers' legacy branches went too: the
  singular `engine` key, a V-n point's singular `case_ref`, the retired
  stall-speed and `units` keys, the gear built from retired layout fields, and
  the fuselage outline built from the parametric length/width/height (with
  `default_fuselage_outline`, now unused). The reader no longer takes those
  three scalars at all, since they are never written. One of the branches was
  a live defect: a surface's `ref_axis_pct` entered as 0.25 read back as "not
  entered", a rule written for files the pre-v52 writer saved. An entered 0.25
  now stays entered. No shipped example carried any of these shapes, and no
  load, deck or digest moves.

## Step — The rolling conditions arrive complete: condition A's lift on the delivered ACRL side, the Amdt 23-48 75 %, a derived unbalanced moment and the TORS aileron increment (#306, design note 52 D-52.1…D-52.13, tier L, 2026-09-25)

**Objective.** Deliver FAR 23.349's two rolling cases whole. SELECT always
picked `ACRL` and `TORS`, and WINGINER always had the unit-roll physics, but
the unbalanced rolling moment had to be typed by hand (a derived `ACRL`
carried zero, #258), the delivered `ACRL` variant flew the `AC ROLL` point's
airplane-average lift rather than condition A's (≈ 19 % low on the governing
side's net root bending), the other-side percentage was the manual's
pre-1996 70→75 % rule where 23.349(a)(2) as amended by Amdt 23-48 says 75 %
flat, the TORS `Δcm = −0.01·δ` increment was selected on but never applied,
the variant table ranked `ACRL` without its couple (#295), and an acrobatic
project got the normal percentage silently.

**Deliverables.** `constants.other_side_percent` (75 %, acrobatic refused
with `UnsupportedCategoryError`) is the one percentage owner, read by
FLTLOADS's `AC ROLL` factor `(100 + p)/200 · n₁` (3.25 → 3.325 on the GA6).
A new `modules/rolling.py` owns condition A's point and root bending, the
derived `UNB = −(1 − p/100) · M_root(A)`, the roll acceleration, the CAM 3.222
steady-roll schedule SELECT's torsion proxy now reads, and the TORS `Δcm`
table built on the existing v52 aileron butt lines. `resolve_wing_cases`
completes every `ACRL` case from those owners (entered values win); the
variant table builds `ACRL` rows at condition A's air with the derived couple
in the inertia; the balanced deck reads the same resolved couple, deriving it
at the balanced case's own point where an entered filter list omits `ACRL`.
The delivered wing conditions publish the derivation (percentage, condition
A's CL/V/root, UNB, θ̈ on `ACRL`; the deflection schedule on `TORS`). Schema
v69: `WingLoadCase.unbal_moment` is optional, blank derived; no hop (v69
was never released, #310). `ga6_normal`'s `ACRL` row is retired to
derived. The three "UNB comes from AILERON" statements are corrected.
`CONVENTIONS.md` §7 gains three owner rows; the approved-corrections entry,
ch04, ch09, `theory_sources.md`, `PROGRAM_SPEC.md` and D-29 carry the
shipped statement. One Imperial digest wave, 66 channels: FLTLOADS, SELECT, BALLOADS and the balanced and LRA decks moved on every fixture (the `AC ROLL` factor, the published derivation, every `ACRL` now a handed pair with its couple); NETLOADS, WINGINER and the wing applied deck on the GA6, the ATR and the RJ, whose wing lists run `ACRL`; the case index on all but the RJ. AIRLOADS, AILERON, the body, gear and tail channels did not move. Report §3 gains 3.3 *Rolling conditions* (the method, the percentage, the UNB derivation table and the deflection schedule; the two subsections after it renumber through the owner) and the Wing Loads page a caption stating the couple.

**Test.** `tests/test_rolling_conditions.py` holds G-52.1–G-52.13: the
Appendix A case 160 as a **test-built case** at its printed inputs reproduces
WINGINER p. 219 (θ̈ −13.287, root Sz −1126, Mxx −124,095, Myy +30,410) and
NETLOADS p. 225, so the `.BAS` math stays locked under the amended rule; the
derived UNB at the printed condition A is 128,619; the delivered `ACRL` air
equals condition A's to the identity on every variant; TORS with blank butt
lines is p. 226, with BL 109.28–201 its root ΔMyy is −18,667; drift guards
forbid the retired rule's literals and a second producer of the couple.
FLTLOADS case 20 is held at the manual's factor and asserted at the amended
one. D-29's divergence pin is replaced by the condition A equality.

**Key decisions.** (1) SELECT's `ACRL` pick on the GA6 moved from 12,000 ft
to sea level (V-n case 40): at the amended factor the CG2 roll points' LZW
tie across altitude to 0.13 %, inside the balance's 0.5 %; the build follows
SELECT's criterion and note 52 §9 leaves a tie band to the owner. The GA6
delivers UNB −129,142 and a net root MX of +400,817 (+2.7 % on the print).
(2) θ̈ is published in rad/s² — WINGINER prints it unlabelled and
`UNB·g/I_wxx` is 1/s². (3) Every fixture's `ACRL` is now a handed pair: the
ATR, the Baron and `concept_heavy` assembled a symmetric `ACRL` with no couple
before. (4) The TORS increment is wing-chain only; the balanced TORS stays the
symmetric trim case.

- **A seeded case's waterline is a fixed point: with no waterline target the search puts a solved ballast on the candidate loading's own waterline, so the placeholder no longer chooses the loading and re-seeding returns the same `zcg` (#314, tier M, 2026-09-27)** —
  Both seeds search for the loading that closes each case on a placeholder
  waterline and write the found loading's waterline back (D-26a, #300).
  `match_waterline=False` dropped the waterline from the match test but
  still solved the ballast's waterline from the placeholder and rejected
  any ballast that fell outside the airframe, so the placeholder decided
  which candidates survived. ATR's `aft max landing` searched on WTONECG's
  137.93, lost its least-ballast loading to that filter, and seeded 141.56;
  the flown search at 141.56 then chose the least-ballast loading after all
  and closed it with 1,007 lb of ballast at waterline 163.4, 22.5 in above
  the rest of a loading at 140.93. `case_loading_checks` could not see it,
  because the ballast made the totals match. The ballast now sits at the
  candidate's own waterline when there is no target, so the seed's choice
  is independent of the placeholder and the flown search keeps it. Measured
  on every seeded case of every fixture, ATR's `aft max landing` is the only
  one that moves: its fixture `zcg` is 140.93 (amending the #300 ruling's
  141.56) with the same loading and ballast weight, the ballast at 140.8.
  The Imperial baseline moves for ATR only, and only on that case: the gear
  loads read the CG height, so its landing moments and gear reactions shift
  by 0.1-0.6 % (landing and balance CSV/TXT, gear report, applied gear CSV),
  and the balanced and LRA decks carry the ballast at 140.8 instead of
  163.4; the digest is regenerated. A guard in `tests/test_cg_cases.py` holds every
  seed of every fixture to its own re-echo and every solved ballast to its
  loading's waterline within the 0.5 in match band.

## Release cut: **sloads 0.8.6** (the baseline wave — one mass model, the negative wing slots, the wing-body joint, delivered precision), tag `v0.8.6`, 2026-09-23

**Objective.** Close band **B7** — the rows that move delivered numbers and
regenerate the digests, sequenced after 0.8.5 so the regeneration is paid
once, and gated on one decision: #164's case-set shape. Taking that decision
opened the band wider than its five rows. Design note 62 (the negative
angle-of-attack wing slots) answered the case-set question; note 63 (one mass
model) answered what mass each case carries; note 64 (the wing-body joint)
answered where the body reacts the wing; note 65 (delivered precision)
answered how a number becomes text. The band emptied on 2026-09-22, the
pre-cut critical review found the cut not clean — one CRITICAL, ten MAJOR —
and it re-opened for six fixes (#294–#299, #295 folded into #306), the round
trip the 0.8.3 cut also took: a release cannot knowingly carry a wrong
delivered load.

**Deliverables** (the `[0.8.6]` changelog section is the release note):
- **The wing case set is complete on both sides (#288, note 62, tier L).**
  SELECT.BAS carried three positive angle-of-attack slots and one negative;
  NHAA (W-07) and NLAA (W-08) are added, NMAA narrowed to the VC pair, a
  negative slot admits negative lift only, and the load-factor-extreme pair
  PNZ (W-09) and NNZ (W-10) delivers the point that sizes the wing-mounted
  masses whatever weight it occurs at. The six Appendix A picks are locked and
  the new slots closure-gated on every fixture's frozen pick.
- **One mass model (#289, #292, #290, note 63, tier L/L/M).** The case's D-25
  loading is the mass state of every inertia load: `WingMassInput` loses its
  mass (schema **v67**), the panel is derived from the `PANEL` rows and the
  concentrated masses are the loading's `POINT` rows, fuel is entered per tank,
  MZFW is a design weight that seeds the zero-fuel and full-fuel cases, every
  SELECT wing slot runs at every FLIGHT mass state with the net-governing run
  delivered, `CaseRef` carries the run key beside the slot id, and the Payload
  Cases group edits the loading the distributions read.
- **The wing-to-body joint (#275, note 64, tier L).** One vertical post at the
  wing station, the fuselage beam through the box with grids at both spars,
  the body integrated as two cantilevers positive-up, the box's loads applied
  and never integrated, M4-1's linear smear and the whole-body closure
  correction retired; a project that cannot place the wing post is refused by
  name (schema **v68**).
- **The baseline wave proper (#164, #222, #260, #293, #161, tier M each).**
  The GA6 fixture balances at Appendix A's three altitudes; the fuselage
  critical set publishes one key per quantity; the ATR 42 fixture is
  reconciled end to end from the published 42-300 data; a closure load lands
  on the member that carries its mass; and every delivered cell prints at the
  precision its unit prescribes (note 65) — no exponent form on the human
  channel, one owner for the digit count, the solver channel untouched.
- **The deck says what it does not carry (#284, #210, #291, tier S).** The LRA
  deck states the SELECT conditions it does not assemble; every engine-mount
  condition states its own point of application; the heavy's drag polar has
  its minimum at the wing's zero-alpha lift coefficient.
- **The pre-cut review's fixes (#294, tier M; #296, #297, #298, #299, tier S).**
  D-62.8's coincidence rule runs once, on the delivered wing set, so the NNZ
  extreme is delivered by somebody whatever mass state NMAA moves to (the
  CRITICAL: `baron_58` case 153 at −2.345 g and the RJ's case 213 were absent
  from the one deck that ships); the v67 migration keeps a converted
  centreline wing mass a point mass; the LRA exporter refuses an unbracketed
  wing station by name instead of a `KeyError`; an SI cell resolves no
  coarser than the Imperial cell it converted from (a 31.2 ft² tail printed
  `3` m²); the live corpus states shipped 0.8.6 and a tier-M closure can no
  longer leave its note at AGREED.
- **Docs-only commits on the branch:** the 2026-09-22 re-cut (B8 re-chartered
  "the deck carries what the airplane carries", #300–#305 filed, rule 6
  applied to #226, #111 and #32) and design note 52 amended and re-agreed
  (D-52.10–D-52.13; the 23.349(a)(2) 75 % correction registered ahead of its
  implementation, #306, with the register's `ships with` marker).
- **Version** `0.8.5` → **`0.8.6`**. Schema **v66 → v68**: v67 at #289 (the
  hop drops `wing_mass.concentrated`, stamps carriage and reports what it
  converted; #296 fixed its stamp order), v68 at #275 (an identity hop on the
  input model — two result dataclasses changed shape).
- **Changelog cut** — `scripts/build_changelog.py 0.8.6 --date 2026-09-23`:
  **19 fragments** consumed — 8 into `## [0.8.6]` directly and **11 history
  entries** rolled to the top of this file, their changelog bullets derived
  from their leads — and a fresh empty `[Unreleased]` opened.
- **Record roll** (`RELEASE_PROCESS.md` §4 step 3): no note moves (note 61
  CV-3). This file stood at 966 lines before the cut and 1,461
  after it; the changelog at 870 and 967. Neither crossed
  1,500, so nothing rolled.
- **Verification baseline** (§4 step 5): unchanged from
  [`36_verification_baseline_0.7.0.md`](36_verification_baseline_0.7.0.md).
  No FAR 23 oracle figure moved: the Appendix A assertions are the same tests
  on the same printed numbers (note 62 G-62.2 locks the six Appendix A wing
  picks by name, #164 re-pins the GA6 conditions at the altitudes the manual
  states). What moved is the delivered set above the oracle — the new slots,
  the per-case mass states, the two-cantilever body, the ATR and heavy
  fixtures, every human-channel digit — each pinned by its own closure gate
  in the notes' §4 tables and regenerated digests, and each recorded in its
  history entry below. A new baseline document would restate 0.7.0's numbers
  verbatim.
- **Gates at cut:** `pytest` **3,742 passed / 9 skipped / 2 xfailed / 0 failed** (3,591 passed / 7 skipped /
  2 xfailed at the 0.8.5 cut), `ruff` clean, `mypy` clean (`sloads/`, 109
  source files), `scripts/smoke_test.sh` **PASS**, `scripts/backlog_issues.py
  check` clean, `scripts/branch_protection_snapshot.py --check`
  matches on 7 tracked keys, the §3.5 by-hand walk done by the owner (2026-09-24), no open CRITICAL/MAJOR review
  findings (the 2026-09-22 review's eleven closed in #294–#299 and #306's
  charter). The **9 skips are fixture-conditional** (§3.3): a parametrized check that a bundled example carries no input for — an entered station table, a WTENV envelope, a fuselage outline, a geometry slice to half-enter — states so and skips, and the three `concept_heavy` LRA skips state the exporter's refusal on a fixture where no side of body resolves (note 64); the set grew by two since 0.8.5 within those. The **2 xfails are the same pair as at 0.8.4 and 0.8.5**: the SI-frame LRA round trips on `concept_regional_jet` and `ga6_normal`, refused by sbeam's dense-path condition heuristic and solving exactly in Imperial (note 55 §8).

**Key decisions.** *A case set is not complete until both sides of it are.*
The band opened on one question — what shape the case set takes — and the
honest answer was three notes deep: a slot for the negative side needs a mass
state to run at, a mass state needs one model that every consumer reads, and
a body that reacts the wing needs a station the beam model actually has. Each
note was PROPOSED and AGREED in session under the solo profile and shipped
within days, with the shipping measurements recorded in the note itself (§8
of note 62, §10–§12 of note 63, §7b of notes 64 and 65) so a decision and its
amendment sit on one page. The second decision was the review's: a band that
has emptied is not a release until a critical read of the whole branch says
so, and this one did not — the coincidence rule on the wrong set would have
shipped a 23.337 design condition to nobody. The round trip cost a day and
six tier-S rows; the alternative was a known-wrong deck under a release tag.
