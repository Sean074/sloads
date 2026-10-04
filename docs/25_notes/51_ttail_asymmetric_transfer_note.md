# The T-tail fin carries the horizontal tail's asymmetry (design note 51)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-09-29 (#328), as amended by §9, which was AGREED
2026-09-29 (owner, in session).** First AGREED 2026-09-06, with no code. §9
re-scopes the note against the LRA deck that replaced the fin deck §1
describes (note 56). It holds the measurements, the owner's rulings of
2026-09-28 and 2026-09-29, and the decisions and gates the code is built to;
where §9 and §1–§8 differ, §9 governs. D-51.3a (net β) and D-51.6 (yaw
parked) stand. **D-51.9 closed 2026-10-04 (#336):** the ATR's tailplane
dihedral is 0°, owner-supplied (§9.7). **§10 AGREED 2026-10-04 (#334,
#335):** the horizontal tail carries `M_r`; D-51.4a, D-51.7 and D-51.10 are
amended there, and §10 governs where it differs.

**Tier L** (new load case, new physics on the fin deck). The T-tail transfer sits in
the review-§3 frozen list; this note is the owner's explicit admission reopening
*distributed empennage loads / T-tail transfer* for exactly this scope and nothing
else.

## 1. What the code does today, and what is missing

*Superseded by §9.1: this section describes the per-component fin deck note 56 deleted.*


Step T7 (plan 09, shipped 2026-08-13) transfers the horizontal tail's concurrent
set to the fin tip for every vertical-tail critical condition:
`ttail_transfer` (`sloads/modules/tail_span.py`) pairs each fin case with the
**balancing** tail load at that case's own V-n point plus the h-tail inertia at its
load factor (T-5), and emits `Fz` + `Myy` only — roll and yaw are identically zero
by T-16, on the rationale that a balancing condition is symmetric. The set rides
the last fin `GRID` via `coordinates.ttail_transfer_to_airplane`, is
equilibrium-gated (`tests/test_export_equilibrium.py::test_vtail_span_deck_resultants`),
and never enters the balanced free-free deck (correct — there the h-tail's own
distributed strips sit at the fin-tip waterline, and the LRA model reacts them
through the six-DOF fin-tip RBE2; a lumped transfer would double-count).

Two load paths are missing, both consequences of the same fact: **on a T-tail the
fin is the "supporting structure" of 14 CFR 23.427(a), and every asymmetric
horizontal-tail load reaches the airplane as a rolling moment at the fin tip.**

- **Gap 1 — the h-tail's own unsymmetrical case is never reacted through the
  fin.** The 23.427(a) case (D-R8, note 21) exists on the h-tail and in the
  balanced deck, but no fin critical condition carries its rolling moment. On
  `concept_regional_jet` the case's net roll about the centreline is
  **+72,547 lb-in** (air; the inertia half is symmetric and contributes none) —
  applied at the fin tip it is a *constant* `Mx` along the whole fin span, equal
  to **14.2 %** of the governing fin case's own root bending (YAW 15 NEUTRAL,
  −512,444 lb-in). Above the ±5–10 % base-method band
  (`theory_sources.md` §Base-method uncertainty), and a first-order omission in
  shipped fin-deck content, which outranks every fidelity item (CLAUDE.md rule 6).

- **Gap 2 — no sideslip/rudder-induced asymmetric load on the horizontal.** In
  the four fin conditions (23.441(a)(1–3), 23.443(b)) the flow over the
  horizontal is not symmetric: the fin's lift carries over onto the tailplane
  (endplate effect), an antisymmetric loading scaled by the **fin side load**
  (6,908 to −8,043 lb on the RJ), not by the concurrent balancing load (+6.3 lb
  at V-n case 14 — which is why any split-percentage approach applied to the
  T-5 pairing produces zero and is not a model). Today T7 transfers a symmetric
  h-tail set in exactly the cases where the horizontal is loaded asymmetrically,
  and the h-tail deck itself never sees the induced antisymmetric distribution.

## 2. Governing basis

14 CFR 23.427 (Amdt 23-42):

- **(a)** horizontal surfaces *and their supporting structure* designed for
  unsymmetrical loads arising from yawing and slipstream, combined with the
  23.421–23.425 conditions;
- **(b)** the conventional-layout default split, 100 % / (100 − 10(n−1)) % ≤ 80 %
  — already implemented (D-R8 / plan 09 T-10);
- **(c)** for horizontal surfaces "supported by the vertical tail surfaces", the
  surfaces and supporting structures designed for **combined vertical and
  horizontal surface loads resulting from each prescribed flight condition taken
  separately**.

(c) is the operative paragraph for both gaps. The oracle does not cover T-tails
(AC 23-9 ¶3 confirms Appendix A of Part 23 applies to conventional empennages
only), so per CLAUDE.md rule 2 the definition of done is a **stated
physics-closure / identity gate in CI**, not an oracle pin (§4).

**Method source: FAA AC 23-9,** *Evaluation of Flight Loads on Small Airplanes
with T, V, +, or Y Empennage Configurations* (1/27/88, ACE-100) —
`reference/AC23-9_Empennage_Flight_Loads.pdf`. It is the FAA's acceptable means
of compliance for 23.427(c) specifically. The parts this note adopts:

- **¶5a (p3), the in-lieu-of-rational-analysis formula:** the limit induced
  rolling moment at the horizontal/vertical intersection,

  `M_r = 0.3 · q · S_H · b_H · β`   (lb-ft; q lb/ft², S_H ft², b_H ft, β rad)

  with β the **effective vertical-tail sideslip angle**: rudder-geometry-derived
  for rudder deflection, the condition's own yaw angle for sideslip, and
  `β = 1.2·U/V` for the lateral gust (U gust fps, V airspeed fps, both EAS).
- **¶5a (p4), the combination rule:** M_r "shall be combined, as required by
  §23.427(c), with the vertical tail surface loads specified in §§23.441 and
  23.443" — i.e. it lands in the four existing fin conditions, exactly where
  D-51.3 puts it.
- **¶5d (p5), the pairing:** the lateral conditions' loads are "combined with
  the appropriate horizontal stabilizer balancing load for one-g level flight" —
  which is what the T-5 pairing already delivers (`point.lt` at the fin case's
  own V-n point), so **T-5 survives this note unchanged and gains an FAA
  citation**.
- **¶5d (p5), the magnitude cross-check:** "for a T-tail configuration, the
  rolling moment is in the range of **4 to 6 times** the value produced by a
  100–80 percent distribution of the conventional stabilizer design load" —
  a stated sanity band the gates use (§4), and the AC's own confirmation that
  the conventional 23.427(b) split is *not* a substitute for the induced moment.
- **¶5d (p5):** the symmetric conditions (23.331/421/423/425) generate no net
  lateral fin load and hence no induced moment — the four fin conditions (plus
  the lateral families of §8) are the complete producer set.

**Stated limits of the method (¶5a p4, carried into the deck notes):** no
compressibility (the RJ's SIDE GUST point is 310 KEAS at 20,000 ft — flag when
`mach_limit` bites); no dihedral effect (a 6° stabilizer dihedral can raise the
moment 50 % — guard: refuse or warn when a T-tail horizontal is entered with
appreciable dihedral, consistent with the AC ¶4b definition "little or no
dihedral"); static strength only, never flutter input.

**Lettering correction (S-tier rider):** note 21 §5's known limitation names this
paragraph "23.427(b)"; in the regulation the fin-with-horizontal case is **(c)**
and (b) is the split formula. Note 21 §5 is corrected, and its stale
"backlog step 9" pointer (T6/T7 shipped 2026-08-13) is replaced by a pointer here.

## 3. Decisions proposed

*D-51.2, D-51.3, D-51.4 and D-51.5 are amended by §9.3; D-51.1, D-51.3a and D-51.6 stand.*


| # | Decision | Alternative rejected |
|---|----------|----------------------|
| D-51.1 | **`TipTransfer` grows `mxx` (roll at the fin tip, airplane axes, default 0.0)** — additive schema change, no migration hop. T-16 is *narrowed*, not repealed: roll is zero **for a symmetric pairing** and carries the paired set's net rolling moment otherwise; the docstring states both | Keeping T-16 absolute — it was a statement about the T-5 balancing pairing, and both new producers (D-51.2, D-51.3) are asymmetric by construction |
| D-51.2 | **New fin critical condition `HTAIL UNSYM` (23.427(c)/(a))**: the h-tail's selected 23.427(a) case reacted through the fin — tip set = that case's `Fz`, `Myy` and net rolling moment `Mxx`; the fin's own airload in this condition is zero ("taken separately"). Expected RJ numbers: `Mxx = +72,547 lb-in`, `Fz`/`Myy` from the case-34 set (`lt25` 3,840.9, `lt50` 8,312.8 lb) | Superposing the roll moment onto the four existing fin cases — pairs loads the airplane never sees together; (c) says *each prescribed condition taken separately*, and the T-5 rational-pairing policy stands (plan 09 §8's conservative option stays parked) |
| D-51.3 | **Induced rolling moment in the four fin conditions per AC 23-9 ¶5a:** `M_r = 0.3·q·S_H·b_H·β`, delivered as a tip `Mxx` in the widened transfer, with an antisymmetric zero-net-lift h-tail span distribution carrying it on the h-tail's own deck. β per condition: SUDDEN RUDDER `RD·EFV·EFFECTV` (the AC's "dependent on rudder geometry" — sloads' own rudder-effectiveness machinery, one owner); YAW TO SIDESLIP 19.5°; YAW 15 NEUTRAL 15°; SIDE GUST `1.2·U/V`. RJ expected values in §4. **D-51.3a (owner, 2026-09-06):** YAW TO SIDESLIP's β is the **net** effective angle — 19.5° *minus* the held-rudder equivalent — because at the overswing the rudder still opposes the sideslip, lowering the effective β; the 19.5°-alone approximation is conservative (past experience) and is not used. This parallels SELECT's own superposition of the two fin-load terms in that condition (−10,456 + 6,908 lb on the RJ) | A carryover model derived from the fin load (DATCOM/ESDU interference factors) — rational and pre-scoped as the upgrade path, but the AC formula is the FAA's own published floor, needs only inputs sloads already holds, and self-checks against the AC's 4–6× band. Also rejected: the 23.427(b) split applied to the concurrent balancing load — produces ~0 on the RJ (+6.3 lb balancing load) exactly where the physics is largest, and the AC's 4–6× statement is the authority that the split is not a substitute |
| D-51.4 | **Export plumbing:** `ttail_transfer_to_airplane` widens to `(fz, myy, mxx)`; `mxx` maps to airplane `mx` — the only `Mx` card a fin deck carries, so its closure gate is an identity (§4). One `FORCE` + one `MOMENT` card as today | A separate roll card at its own GID band — the transfer is one physical set at one node |
| D-51.5 | **The balanced free-free deck is untouched.** The h-tail's unsymmetrical strips already sit at the fin-tip waterline with the correct roll arm; the fin-path is a per-component structural view. D-51.3's induced load, once pinned, is *also* added to the lateral balanced cases' h-tail strips (same producer, one owner) — a second implementation step under the same note | Routing D-51.2's lumped set into the balanced deck — double-counts the strips (the same reason T7 was excluded there, plan 11 §4) |
| D-51.6 | **Yaw transfer stays zero — parked with the numbers** (owner, 2026-09-06). The only physical producer is chordwise (drag) asymmetry on the h-tail: differing left/right induced drag makes a couple about the fin's vertical axis, landing in the fin **torsion** channel (shared `mz` component and sign convention with strip torsion, `coordinates.tail_torsion_to_airplane`). Sized on the RJ: (i) worst case is the 23.427(a) split (RH 5,816 / LH 4,600 lb at 187 KEAS) → ΔD ≈ 158 lb at the 59.7 in side centroid → **9,399 lb-in**, 1.83 % of governing fin bending and 5–24 % of the fin's *own-case* torsion (40–185 k lb-in) — but that producer exists only in the D-51.2 condition, where the fin carries no own aero, so 9.4 k lb-in can never govern the torsion envelope its own cases set; (ii) in the four fin conditions the D-51.3 induced set is antisymmetric about a ~zero balancing CL (+6 lb on the RJ), and induced drag is quadratic in CL, so its left/right drag difference cancels to second order — no producer. AC 23-9's method itself prescribes **only** the rolling moment (¶5a) | Adding an `mzz` field "for symmetry" — a number with no producer, the exact failure T-16 guarded against; or gating a 1.8 %-of-bending term the base method cannot resolve (±5–10 % band, rule 6) |

## 4. Gates (the closure targets, with expected numbers)

*Superseded by §9.4, which gates the LRA deck and the fin view.*


No printed oracle exists for any of this (Appendix A has no T-tail); every gate is
an identity or closure per CLAUDE.md rule 2.

1. **Roll-transfer identity (D-51.2):** the `HTAIL UNSYM` fin deck's single `Mx`
   card equals the h-tail 23.427(a) span table's `Σ fz·y` exactly
   (`rel_tol=1e-9`, same-producer identity). RJ expected: **72,547 lb-in**.
2. **`test_vtail_span_deck_resultants` extended:** deck `Mx` card sum equals
   `transfer.mxx`; the free-body statement gains the roll row; the existing
   "only `Myy` is the transfer's" assertion becomes "only `Myy`/`Mx`". The four
   T-5-paired cases still assert `mxx == 0.0` until D-51.3 lands (the identity
   that today's behavior is the symmetric special case).
3. **Balanced-deck no-double-count:** G-OR-72 unchanged; a new assertion that the
   balanced deck contains no `Mx` card at the fin tip GID band (the strips carry
   the roll arm, the lumped set never enters).
4. **Conventional isolation:** `test_a_conventional_fin_deck_is_unchanged_by_the_t_tail_code`
   re-run as-is — flipping `tail_type` removes every new card.
5. **D-51.3 closure (AC 23-9 ¶5a, page cited in the test):** the induced
   antisymmetric set has zero net lift (`Σ fz = 0` to 1e-12) and its `Mx`
   equals `0.3·q·S_H·b_H·β` exactly (`rel_tol=1e-9`, identity — the formula is
   the definition). RJ expected values (S_H = 120 ft², b_H = 23.17 ft):

   | Fin condition | q (psf) | β | M_r (lb-in) |
   |---|---|---|---|
   | SUDDEN RUDDER 23.441(a)(1), 187.07 KEAS | 118.5 | 12.88° (`25°·1.0·EFFECTV 0.5153`) | **266,611** |
   | YAW TO SIDESLIP 23.441(a)(2), 187.07 KEAS | 118.5 | 6.62° (net: 19.5° − 12.88°, D-51.3a) | **136,954** |
   | YAW 15 NEUTRAL 23.441(a)(3), 187.07 KEAS | 118.5 | 15.00° | **310,435** |
   | SIDE GUST 23.443(b), 310 KEAS / 20,000 ft | 325.4 | 6.57° (`1.2·50/V`) | **373,407** |

6. **The AC's own sanity band (¶5d):** M_r within 4–6× the 23.427(b) split roll
   moment (4–6 × 72,547 = 290–435 k lb-in). The gate asserts the band on the
   two pure-attitude cases — YAW 15 NEUTRAL **4.28×**, SIDE GUST **5.15×** —
   and *states* the two rudder-affected ratios rather than gating them
   (SUDDEN RUDDER 3.67×, YAW TO SIDESLIP 1.89×: EFFECTV and the D-51.3a net-β
   pull them below the AC's rough band by construction, which is the intended
   physics, not a failure).
7. Doc-currency and schema guards as usual (additive v-next `TipTransfer` field).

## 5. Effect vs error bar (rule 6)

| Item | Effect on a delivered load | Band | Verdict |
|---|---|---|---|
| Gap 1 / D-51.2 | 14.2 % of governing fin root bending (72.5 k / 512.4 k lb-in, RJ) | ±5–10 % | **Ranks** — and is defect-class (supporting-structure omission in shipped fin deck) |
| Gap 2 / D-51.3 | **27–73 % of governing fin root bending** (M_r 137–373 k vs 512.4 k lb-in own-load bending, RJ; D-51.3a net β) — AC 23-9 ¶5d calls this "the key loading component" for T-tails, and the numbers agree | ±5–10 % | **Ranks decisively** — on the RJ the induced moment is the dominant single contributor to fin bending after the fin's own load |
| Yaw / D-51.6 | Worst producer (the 23.427(a) case's induced-drag asymmetry): **9,399 lb-in**, **1.83 %** of governing fin root bending; in the four fin conditions the induced set is zero-net-lift about ~zero balancing CL, so its drag asymmetry vanishes to second order | ±5–10 % | **Parked with these numbers** (D-51.6, owner 2026-09-06; entry in `02_parked.md` travels with the implementing PR) |

## 6. What this supersedes / corrects

- **T-16** narrowed (roll zero *for symmetric pairings*) — `results.py`,
  `coordinates.py` and `report/applied.py` comment blocks updated together
  (`sbeam_bridge.py` when this was written; note 56 D-56.1 dissolved it).
- **Note 21 §5** — "(b)" → "(c)", stale backlog-step-9 pointer replaced.
- `docs/25_notes/21_power_effects_wing_note.md` G6-6 cites "(b)'s ratios" —
  verified **correct** (the split formula is (b)); no change.
- The frozen-list entry for the T-tail transfer gains a pointer to this note as
  the scoped reopening.

## 7. Closure obligations (tier L)

`theory_sources.md`: a 23.427 row stating (a)/(b)/(c) lettering and the D-51.3
source (**AC 23-9 ¶5a, p3–4**, `reference/AC23-9_Empennage_Flight_Loads.pdf`);
`PROGRAM_SPEC.md` tail-span/export sections; `CONVENTIONS.md` transfer-set row
updated; history fragment in full step format; changes fragments; the S-tier
note-21 rider travels in the same PR.

## 8. Deferred (AC 23-9's wider producer list, each parked with its trigger)

*The one-engine-out item is promoted by §9.3 (D-51.3b): its trigger is met on the ATR.
Its low-speed end is #333: there is no VMC input, VS stands in and is below the
ATR's VMC, and the unrecovered case reaches no output. `M_r` scales with the fin
load, so that case's induced moment is the smallest of the three (ATR VS
130,829 against VD 458,984 lb-in), and #328 does not wait for #333.*


AC 23-9 ¶5d names the unsymmetric producers as 23.351, **23.367**, 23.441 and
23.443, plus 23.455 rolling velocities. This note takes the 23.441/23.443 four;
the rest are deferred with the condition that promotes them:

- **One-engine-out (23.367):** `one_engine_out` already computes a net lateral
  fin load, so its case induces an M_r by the same formula — promote when the
  OEO fin load exceeds the 23.441 set's on any T-tail fixture (on the RJ it
  does not govern today).
- **23.455 rolling velocities / 23.351:** no producer module yet; files with
  the condition, not before.
- **Vectorial vertical+horizontal gust combination (¶5d):** park until a
  T-tail fixture's gust cases govern the empennage.
- **V- and Y-tail unit-load factors (¶Figure-1 section, 1/cosθ, 1/sinθ) and the
  ±50 fps normal-to-panel supplementary gust:** out of this note's T-tail
  scope; a candidate row when the Baron/V-tail pass (OR-11) reopens.
- Slipstream asymmetry on the horizontal (23.427(a)'s other producer; AC ¶5d
  recommends evaluating it under 23.301) — park with a number when a powered
  T-tail fixture exists.
- The plan 09 §8 conservative superposed-critical pairing — still parked, still
  un-filed; filing it as a backlog row is part of this note's S-tier rider.
  Note the AC's ¶5d pairing language ("one-g level flight balancing load") is
  an FAA citation *for* the rational T-5 policy.

## 9. Amendment — against the LRA deck (#328, PROPOSED 2026-09-29)

**Owner rulings.** On the issue, 2026-09-28:

- Q4: 23.427(a) is met by the (b) 100/80 split on every tail, and on a T-tail
  by (c) as well, through AC 23-9 ¶5a. `M_r` is sized for the fin, on the
  owner's assumption that it is not critical for the horizontal tail.
- Q5: that assumption is stated and checked on every T-tail. `M_r/2` per side
  is compared with the stabiliser's governing root bending: a warning above
  100 %, never a refusal, and the margin is stated below it.

In session, 2026-09-29, after §9.1's measurements:

- Q1 (a): the one-engine-out fin cases are a fifth producer.
- Q2 (a): Mach is stated on every `M_r` subcase, with a warning above 0.6.
- Q3 (a): the ATR's tailplane dihedral is entered from a cited source.

**Conventions:** `CONVENTIONS.md` §3 (LIMIT, SF stated per case and applied
nowhere), §4 (case identity), §7 (one owner per quantity), §7.1 (handedness).

### 9.1 What the tree does today (measured at `dev/v0.8.8`, 2026-09-29)

Note 56 deleted the per-component fin deck §1 was written against. The
deliverable is the LRA free-free deck, with the fin view (`build_tail_span`,
the fin's applied-load CSV in `report/applied.py`, and the report) beside it.
The balanced deck assembles the four fin conditions and, on a twin, the
one-engine-out cases as handed lateral cases. The 23.427(a) case is a handed
h-tail case. On a T-tail the h-tail's centreline is rigid to the fin tip
(`JointName.VTAIL_TIP_HTAIL`).

**Gap 1 is closed in the deck and open in the fin view.** The fin-root rolling
moment of the loads on the h-tail and fin members of the deck's 23.427(a)
case equals the h-tail span table's `Σ fz·y` exactly, in both hands:

| | RJ | ATR |
|---|---|---|
| 23.427(a) case picked | UNCHECKED MAN UP (V-n 34) | GUST DN RETRACTED |
| `Σ fz·y` | +72,547 lb-in | −30,622 lb-in |
| Deck fin root `Mx`, R / L | +72,547 / −72,547 | −30,622 / +30,622 |
| Share of governing fin root bending | 14.2 % (of 512,444) | 12.5 % of the four fin conditions (245,278); 3.4 % of the governing one-engine-out case (889,475) |

No gate asserts this, and the fin view carries no such condition. The oracle
report's 6.5 says so ("never reacted through the vertical tail").

**Gap 2 is open everywhere.** No producer of `M_r` exists. `M_r = 0.3·q·S_H·b_H·β`
(AC 23-9 ¶5a p3), with β per §9.3 D-51.3a:

| Condition | RJ q / β / Mach | RJ `M_r` (lb-in) | ATR q / β / Mach | ATR `M_r` (lb-in) |
|---|---|---|---|---|
| SUDDEN RUDDER 23.441(a)(1) | 118.5 / 12.88° / 0.283 | 266,727 | 87.2 / 13.19° / 0.243 | 112,543 |
| YAW TO SIDESLIP 23.441(a)(2) | 118.5 / 6.62° / 0.283 | 137,013 | 87.2 / 6.31° / 0.243 | 53,894 |
| YAW 15 NEUTRAL 23.441(a)(3) | 118.5 / 15.00° / 0.283 | 310,569 | 87.2 / 15.00° / 0.243 | 128,028 |
| SIDE GUST 23.443(b) | 325.5 / 6.57° / **0.692** | 373,565 | 195.1 / 8.49° / 0.455 | 162,118 |
| ONE ENGINE OUT VC 23.367(a)(2), ULT | — | — | 195.1 / 17.21° / 0.455 | 328,765 |
| ONE ENGINE OUT VD 23.367(a)(1) | — | — | 304.8 / 15.38° / 0.569 | 458,984 |

The inputs are S_H = 120.00 ft² and b_H = 23.167 ft on the RJ, and
S_H = 85.00 ft² and b_H = 18.333 ft on the ATR. The RJ reproduces §4's
figures to within 0.05 %.

`M_r` is 27–73 % of the RJ's governing fin root bending. On the ATR it is
22–66 % of the four fin conditions' root bending, but the ATR's fin is
governed by the one-engine-out VD case (889,475 lb-in, 3.6× the four). §8's
trigger for promoting 23.367 is therefore met, and AC 23-9 ¶5d names 23.367
among the producers.

**The horizontal-tail assumption holds everywhere except one case.**
`M_r/2` against the governing per-side h-tail root bending (RJ 349,920,
ATR 161,404 lb-in, both LIMIT):

- RJ: at most 53.4 % (side gust).
- ATR, the four fin conditions: at most 50.2 %.
- ATR one-engine-out VC (ultimate, SF 1.0): 67.9 % on a common basis.
- **ATR one-engine-out VD: 142.2 %.**

**AC limits.**
- Mach: the RJ's side gust is at 0.692.
- Dihedral: every fixture enters `htail_dihedral_deg = 0`, including the ATR,
  whose 0 is owner-supplied (D-51.9, closed at #336). The guard therefore has
  nothing to fire on in a fixture.

### 9.2 Governing basis, added to §2

- **The sense of `M_r`** (AC 23-9 ¶5d, p5–6 and Figure 1): "For the T-tail,
  the moment due to the horizontal surface **adds** to the moment due to the
  vertical tail load." `M_r` takes the sign of the fin's own root rolling
  moment in the same condition.
- **The producer set** (¶5d p5): 23.351, **23.367**, 23.441 and 23.443
  "generate a net lateral aerodynamic load on the vertical stabilizer and
  induce a rolling moment on the horizontal stabilizer". This amendment takes
  23.367, 23.441 and 23.443. 23.351 and the 23.455 rolling velocities stay in
  §8.
- **The combination** (¶5d p5): each producer is combined with the
  appropriate one-g balancing load. The deck's lateral and one-engine-out
  cases already ride their V-n point's trim tail load, and the fin view's
  four conditions carry T-5's pairing. A one-engine-out fin condition is not
  a point of the V-n matrix, but it runs at defined speeds (VC, VD, and VS in
  place of VMC, Ch 11 p87). The deck already pairs each one with a parent
  point; the fin view takes the same parent (D-51.1a).

### 9.3 Decisions, as amended

| # | Decision | Alternative rejected |
|---|---|---|
| D-51.1 *(stands)* | `TipTransfer.mxx`, the rolling moment at the fin tip in airplane axes, default 0.0. It is a result field, not an input, so there is no schema hop. T-16 is narrowed: the roll is zero for a symmetric pairing | — |
| D-51.1a *(revised 2026-09-29, owner)* | **A one-engine-out fin result is paired with the deck's own parent point.** A 23.367 condition is a transient, not a point of the V-n matrix, so `cond.case` is `None` and today its `tip_transfer` is `None`. The deck already resolves a parent for each one: `OEI_PARENT` (VC → `BAL C`, VD → `BAL D`, VS → `STALL 1G`), taken at the heaviest derivable FLIGHT loading and at the balanced altitude nearest the case's own (`engine_out_cases._heaviest_derivable`, `_nearest_altitude`). That resolution moves to **one owner**, `balance.engine_out_cases.oei_parent_point(project, cond)`, returning `None` with the reason when no parent resolves. The deck and `tail_span.ttail_transfer` both call it. On a T-tail the fin result's transfer is T-5's set at that parent point (the parent's balancing tail load and the h-tail inertia at its load factor), plus `mxx = M_r`. This is AC ¶5d's "appropriate horizontal stabilizer balancing load for one-g level flight". If no parent resolves, the transfer carries `mxx = M_r` alone and says why, the same record the deck's `no-parent` skip writes | `M_r` alone with no pairing (the fin view would lack the balancing load ¶5d asks for, which the deck carries); a second parent rule in `tail_span` (two owners of one pairing, which can disagree) |
| D-51.2a | **`HTAIL UNSYM` is a fin condition in the fin view only.** A fin result with zero fin air load carries the 23.427(a) h-tail case at its tip: `fz` = that table's `Σ fz` (air + inertia, as T7), `myy` by T7's own arm rule, and `mxx = Σ fz·y`. It takes the h-tail case's SF, and its id comes from a new band, `VTAIL_BAND_TTAIL = 20` (**VT-20**…VT-29), beside ONENGOUT's. It reaches the fin's applied-load CSV, the case index and the report. **The deck is not changed**, because its handed 23.427(a) case already carries the roll at the fin root exactly (§9.1); a gate asserts it (G-51.1) | Adding a lumped set to the deck (double-counts the strips, as D-51.5 said); leaving the fin view without it (the report's 6.5 states the omission today) |
| D-51.3a *(amended)* | **One owner, one β rule.** `tail_span.induced_roll_moment(project, cond)` returns `M_r`, its β, q, Mach and basis. **β is the fin's own side load expressed as an angle** on SELECT's slope: `β = \|LT25 + LT50\| / (AVT/57.3 · q · S_V)`. For SUDDEN RUDDER this is exactly `RD·EFV·EFFECTV`, for YAW TO SIDESLIP exactly D-51.3a's net β (19.5° − the rudder's), and for YAW 15 NEUTRAL exactly 15°. The ruled net β therefore falls out of the one formula with no special case. **SIDE GUST is the one exception**, AC ¶5a's `1.2·U/V` (U and V as EAS, fps), as agreed; SELECT's own gust angle includes the alleviation factor (RJ 4.81°, ATR 6.22°) and is not the AC's. q is at the condition's EAS. The sign is the fin's root rolling moment's (§9.2). `M_r` carries the fin condition's own SF, so the one-engine-out VC case stays `ULT SF=1.0` | Per-condition β formulas (four spellings of one quantity, and the net-β rule restated); SELECT's alleviated gust β (not the AC's method) |
| D-51.3b | **The one-engine-out fin conditions are a fifth producer** (Q1 (a)). Same owner and same β rule, at the case's speed and ONENGOUT's own altitude (entered, else the shoulder altitude). ATR: 328,765 lb-in (VC, ULT) and 458,984 lb-in (VD) | Parking it with the number (the ATR's largest induced moment, and the only case that fails the h-tail check) |
| D-51.4a *(replaces D-51.4)* | **The deck carries `M_r` as a free couple at the fin tip.** Each lateral and one-engine-out balanced case on a T-tail gains one `BalancedLoad` with `mx = M_r` at the `VTAIL_TIP_HTAIL` joint location, `source = "vtail-induced-roll"`. It routes to the fin member, and the tip node is the nearest. It is applied before the residual is summed, so the closure's roll degree of freedom reacts it: `ṗ` moves and the inertia field with it. This is the aileron couple's precedent (`air.py`, `aileron-roll`). The port twin reflects it through `reflect_load`. `is_lateral` and `vtail_load` still read `vtail-air` alone, so the fin side load reported does not change. In the fin view, `ttail_transfer_to_airplane` widens to `(fz, myy, mxx)`, as D-51.4 said | An antisymmetric h-tail strip set (Q4: sized for the fin, the h-tail checked instead — see §9.5); a couple at the fin root (misses the fin's own bending path) |
| D-51.5a *(replaces D-51.5)* | **No second (b) path in the deck.** D-51.2a's lumped set never enters it (G-51.3). `M_r` enters once, as D-51.4a says | — |
| D-51.6 *(stands)* | Yaw transfer zero, parked with its numbers | — |
| D-51.7 | **The h-tail assumption, checked** (Q5). For every `M_r` on a T-tail, the check is `(M_r/2 · SF_case) / (M_h · SF_h)`, where `M_h` is the governing per-side h-tail root bending over the h-tail's conditions, and `SF_case`/`SF_h` bring both to one basis. Above 100 %: a validation warning and an in-band statement on the case and in the report, never a refusal. At or below: the margin is stated. Shipped consequence: **the ATR warns on its one-engine-out VD case (142.2 %)** | Refusing (the owner ruled warn); `M_r/2` against a limit figure while the case is ultimate (compares unlike bases) |
| D-51.8 | **The AC's limits, stated and guarded.** (i) **Mach** at the condition's speed and altitude is stated on every `M_r` subcase; a warning above `AC23_9_MACH_WARN = 0.6`, an engineering threshold the AC does not give (owner, Q2). The RJ's side gust (0.692) fires it. (ii) **Dihedral:** the entered `htail_dihedral_deg` is stated on every `M_r` subcase, with a warning when it is above 0: AC ¶5a p4, "6° dihedral can increase the stabilizer rolling moment by 50 %". `M_r` is not scaled, because the AC gives no method. (iii) **Static only:** the deck header and the report say `M_r` is not a flutter input (¶5a p4) | Scaling `M_r` by dihedral (no source method); a Mach refusal |
| D-51.9 | **The ATR's tailplane dihedral is entered from a cited source** (Q3 (a)): Jane's [C] if it states a value, else measured off the [A] three-view's front elevation and tagged [E] in `atr42_100.sources.md`. No load reads the field, so only statements move. **Closed 2026-10-04 (#336):** no published value was found; the owner supplied 0°, cross-checked against ATR's 42-300/-320 front elevation (`atr42_100.sources.md` [F]), which draws none. G-51.10's constructed project is the guard's gate | Leaving 0.0 with a stated gap |
| D-51.10 | **The fin view states its root bending with the tip set.** Station columns stay the fin's own loads (T7's split, unchanged). Each T-tail fin result publishes one more value, the root rolling moment including the transfer's `mxx`, so a reader of the fin view sees the number the deck's fin root carries | Adding the transfer into every station column (moves the T7 split for every existing reader) |
| D-51.11 | **The report's 6.5 is rewritten for a T-tail.** With both paths carried, the statement "never reacted through the vertical tail" is false on a `T_TAIL`, and the OR-133 withholding of the fin's spanwise loads rests on nothing on that arrangement. It lifts for `T_TAIL` only, read off `is_t_tail`. V-tail and cruciform keep it | Keeping the withholding (states an omission the code no longer has) |

### 9.4 Gates (closure targets; no printed oracle — rule 2's second branch)

| Gate | What is asserted | Expected (RJ / ATR) | Tolerance |
|---|---|---|---|
| G-51.1 | In each handed 23.427(a) balanced case, the fin-root `Mx` of the h-tail and fin members' loads equals ± the h-tail table's `Σ fz·y` (Gap 1 in the deck) | ±72,547 / ±30,622 | 1e-9 |
| G-51.1a | Each one-engine-out fin result's transfer is paired with the same V-n point as the deck's case for it (one owner, `oei_parent_point`), and its `fz`/`myy` equal T-5's set at that point | — | exact |
| G-51.2 | `HTAIL UNSYM`'s `TipTransfer.mxx` equals `Σ fz·y`, and its applied-load row's `mx` equals `mxx` | +72,547 / −30,622 | 1e-9 |
| G-51.3 | The balanced deck carries no `HTAIL UNSYM` set, and exactly one `vtail-induced-roll` load per T-tail lateral or one-engine-out case | — | exact |
| G-51.4 | `M_r = 0.3·q·S_H·b_H·β` (AC ¶5a p3, page cited); β identities: SUDDEN RUDDER = `RD·EFV·EFFECTV`, YAW TO SIDESLIP = 19.5° − that, YAW 15 = 15°, SIDE GUST = `1.2·U/V` | §9.1 table | 1e-9 (identity); ±0.1 % (figures) |
| G-51.5 | Sense: `M_r` has the sign of the fin's air root rolling moment in every case (AC p5–6) | — | exact |
| G-51.6 | The deck's fin-root `Mx` in each lateral and one-engine-out case equals its value without the couple plus `M_r`. The case's 1 g half still closes inside `RESIDUAL_GATE`; the roll is reacted by `ṗ`, the lateral cases' existing standing | — | 1e-9 |
| G-51.7 | Fin-view root rolling moment with the tip set (D-51.10), airplane axes | RJ: SR −706,830, YTS +363,087, Y15 +823,013, SG −824,818 · ATR: SR −328,155, YTS +157,144, Y15 +373,307, SG −389,728, OEI VC ±965,886, OEI VD ±1,348,459 | ±0.1 % |
| G-51.8 | AC ¶5d band: 4–6× the (b) roll on the two pure-attitude cases; the rudder-affected and one-engine-out ratios are stated, not gated | RJ 4.28× / 5.15× · ATR 4.18× / 5.29× | band |
| G-51.9 | D-51.7: the ATR's one-engine-out VD warns (142.2 %); no other case on either fixture warns; the ratios are stated | RJ max 53.4 % · ATR VC 67.9 % | ±0.1 % |
| G-51.10 | D-51.8: the RJ side gust's Mach warning fires (0.692) and nothing else does; the ATR enters 0 (D-51.9, owner-supplied), so the dihedral warning is gated on the constructed project | — | exact |
| G-51.11 | Conventional isolation: flipping `tail_type` removes every new load, row, value and warning (the existing isolation test, extended) | — | exact |

### 9.5 Effect vs error bar (rule 6), and what moves

| Item | Effect on a delivered load | Verdict |
|---|---|---|
| Gap 1, fin view | RJ 14.2 %, ATR 12.5 % (3.4 % of its governing one-engine-out case) | Ranks on the RJ; the ATR is carried by the same rule |
| Gap 2 | Governing fin root bending: RJ 512,444 → 824,818 (+61 %); ATR 889,475 → 1,348,459 (+52 %) | Ranks decisively |
| h-tail under `M_r` | ATR one-engine-out VD 142.2 % of the h-tail's governing root bending | **Warned, not carried** (D-51.7, Q5). The antisymmetric h-tail case that would carry it is deferred to §8, with this number as its trigger; its trigger is met on the ATR as shipped (see below) |

**What moves.** On the RJ and the ATR:
- the fin view: the four fin conditions' transfers, the new VT-20 row and the
  ATR's one-engine-out transfers;
- the case index;
- every T-tail lateral and one-engine-out balanced case, through the couple
  and its `ṗ` (the Imperial digest and the LRA deck digests);
- the report's 6.5;
- on the ATR only, the fixture's dihedral (statements).

ga6, the Baron and concept_heavy are conventional and do not move (G-51.11).

**Deferred with its trigger met.** The ATR's one-engine-out VD case puts
`M_r/2` at 142 % of the horizontal tail's governing root bending. By the
owner's ruling that is warned, not carried: the h-tail's own deck and CSV do
not see an antisymmetric set. §8 gains the row "antisymmetric h-tail case
under `M_r` (the zero-net-lift set of the original D-51.3)". Its trigger is
D-51.7's check above 100 % on a shipped fixture, and it is met at ship.
Filing it as a backlog issue is part of this step's closure (rule 5).

### 9.6 Closure obligations (tier L), in addition to §7

- `theory_sources.md`: the 23.427 row cites AC 23-9 ¶5a p3–4 and ¶5d p5–6
  (sense and producers), the β rule, the Mach threshold's basis and the
  23.367 producer.
- `PROGRAM_SPEC.md`: the tail-span, balance and export sections.
- `CONVENTIONS.md` §7: rows for `induced_roll_moment` and
  `VTAIL_BAND_TTAIL`.
- `case_ids.py`'s band table.
- `atr42_100.sources.md`: the dihedral row.
- The report's 6.5 and OR-133 text.
- The §6 riders: note 21 §5's lettering fix, and filing the plan 09 §8
  pairing row.
- The Imperial and deck digests regenerated.
- One history fragment in full step format.

### 9.7 Implementation record (#328, 2026-09-29)

- **Owners.**
  - `tail_span.induced_roll_moment` returns an `InducedRoll` record (the
    moment, β, q, Mach, altitude, basis, dihedral, and the h-tail ratio).
  - `tail_span.vtail_root_roll` and `vtail_root_roll_with_tip` (D-51.10).
  - `tail_span.check_htail_under_induced_roll` (D-51.7), which also states
    the ratio on each fin result.
  - `engine_out_cases.oei_parent_point`: the deck's parent lookup, moved to
    one owner and called by both the deck and the fin view (D-51.1a).
  - `one_engine_out.case_altitude_ft`: the march's altitude, which the Mach
    of a one-engine-out `M_r` reads.
  - The constants `AC23_9_ROLL_COEFF`, `AC23_9_GUST_BETA_FACTOR` and
    `AC23_9_MACH_WARN`.
  - `case_ids.VTAIL_BAND_TTAIL` = 20.
- **The deck.** `balance.applied.vtail_sets` appends the couple from the
  transfer's `induced` record, source `vtail-induced-roll`, never `mxx`
  (D-51.5a). Each case that carries it states `INDUCED_ROLL_NOTE` in band.
- **Warnings.** `validation._check_ttail_induced_roll` raises
  `ttail_induced_roll_sizes_htail`, `ttail_induced_roll_mach` and
  `ttail_htail_dihedral`, all on the Tail Loads page.
- **The report.** `_vtail_withheld` no longer withholds a T-tail.
  `_ttail_vtail_paragraphs` states the three tip sets and each condition's
  numbers. Section 5's pointer names the T-tail. The dead T-tail branches of
  the withholding statement are removed.
- **Rider (rule 4).** The 23.333(c) gust velocity had four copies:
  `flight_envelope._gust_ude`, `vn_diagram._gust_ude`, and SELECT's lateral
  and h-tail gusts. They are now one owner, `constants.gust_ude_fps`, with an
  AST guard. No digest moved on any conventional fixture.
- **What moved.** The Imperial digest moved 8 channels each on the RJ and
  the ATR: the case index, the balance CSV and text, the tail-span CSV and
  text, the balanced deck, the LRA deck, and the fin's applied deck. The
  other three fixtures did not move. The lateral pins changed: roll
  acceleration ṗ rose 27–42 % (ATR) and 62–83 % (RJ), and yaw acceleration ṙ
  moved less than 4 %. Fin loads and Ny are unchanged.
- **D-51.1 corrected: v72 with an identity hop.** D-51.1 said "no
  migration hop" because `TipTransfer` is a result type. It is also
  persisted, so the persisted-shape guard (`test_schema_guards`) requires a
  bump. The new fields are `mxx`, `paired_case` and `induced`; the record
  type `InducedRoll` is new. Since 0.8.7 released v70 (#310), a bump gets a
  registered hop: v72, with an identity `_hop_71`.
- **D-51.9 was not done at ship; closed 2026-10-04 (#336).** Neither Jane's
  [C] nor a measurable [A] three-view was available at ship. At #336 the owner
  supplied 0°, and ATR's 42-300/-320 brochure front elevation, measured as a
  cross-check, draws no tailplane dihedral. The dihedral guard stays gated on
  a constructed project (G-51.10).


## 10. Amendment — the horizontal tail carries `M_r` (#334, #335, AGREED 2026-10-04)

**Owner rulings, in session 2026-10-04.** The owner's Q4/Q5 assumption of
§9 (that `M_r` sizes the fin and not the horizontal tail) does not hold on
the ATR, so the horizontal tail carries every induced moment, at the trim
solution of its fin condition:

- Q1: `M_r` is spread chord-proportionally, the 23.427(a) case's own shape.
- Q2: every T-tail fin condition carrying `M_r` gets its horizontal-tail
  condition, both engines' one-engine-out cases included.
- Q3: the D-51.7 check, its warning and `InducedRoll.htail_ratio` retire.
- Q4: the one-engine-out march reads an entered windmill drag coefficient
  (note 66 §13); the ATR keeps the Glauert bound (no cited value).
- #335: (a) — T-5 stays the only pairing policy.

**Conventions:** `CONVENTIONS.md` §3 (LIMIT, SF stated per case and applied
nowhere), §4 (case identity), §7 (one owner per quantity), §7.1 (handedness).

### 10.1 What the tree does today (measured at `dev/v0.8.9`, 2026-10-04)

The fin carries `M_r` (D-51.4a); the horizontal tail does not, and D-51.7
warns. With the proposed condition built (the fin condition's T-5 trim load
at its published CP, the tail's inertia at the pair's load factor, plus the
antisymmetric `M_r` set of D-51.12), the per-side root bending is:

| Fin condition | SF | Pair (V-n) | Trim load (lb) | `M_r` (lb-in) | Per-side root bending, larger side (lb-in) | Of today's governing |
|---|---|---|---|---|---|---|
| **ATR** — today's governing: GUST DN RETRACTED **161,404** (SF 1.5) ||||||
| SUDDEN RUDDER | 1.5 | 14 | +777.0 | −112,543 | 66,980 | 41.5 % |
| YAW TO SIDESLIP | 1.5 | 14 | +777.0 | +53,894 | 37,655 | 23.3 % |
| YAW 15 NEUTRAL | 1.5 | 14 | +777.0 | +128,028 | 74,723 | 46.3 % |
| SIDE GUST | 1.5 | 195 | −871.5 | −162,118 | 110,703 | 68.6 % |
| ONE ENGINE OUT VC, each engine | **1.0** | 175 | +703.0 | ±329,944 | 173,864 | 71.8 % on one basis (107.7 % raw) |
| **ONE ENGINE OUT VD, each engine** | 1.5 | 176 | +459.3 | ±460,327 | **233,122** | **144.4 %** |
| **RJ** — today's governing: GUST DN RETRACTED **349,920** (SF 1.5) ||||||
| SUDDEN RUDDER | 1.5 | 14 | +6.3 | −266,727 | 148,657 | 42.5 % |
| YAW TO SIDESLIP | 1.5 | 14 | +6.3 | +137,013 | 83,801 | 23.9 % |
| YAW 15 NEUTRAL | 1.5 | 14 | +6.3 | +310,569 | 170,579 | 48.7 % |
| SIDE GUST | 1.5 | 175 | −2,973.0 | −373,565 | 291,033 | 83.2 % |

The ATR's governing horizontal-tail root bending moves to the one-engine-out
VD condition, 161,404 → 233,122 lb-in (+44.4 %, LIMIT). The RJ's does not
move. "One basis" is `safety_factors.ultimate_basis`, the comparison key and
never a delivered value.

**Why the one-engine-out case dominates.** On the ATR its fin load is about
3.6× the rudder conditions', and about two thirds of it is the Glauert
windmill-drag bound, which assumes no propeller drag limiting at all.
23.367(a) asks for "a single malfunction of the propeller drag limiting
system" and (a)(3) for drag "substantiated by test or other data". Measured
at ATR VD, failed engine 1: the peak fin load is 16,040 lb on the bound,
11,196 lb at `C_D,disc` 0.25 and 8,314 lb at 0.10. The power level is under
1 % (max-continuous 15,984 lb, and 15,669 lb with no thrust). The march
cannot read a cited coefficient today (note 66 D-66.12a ruling (a′)), so
note 66 §13 changes that. The ATR keeps the bound until a source exists.

### 10.2 Decisions

| # | Decision | Alternative rejected |
|---|---|---|
| D-51.12 | **One horizontal-tail condition per T-tail fin condition carrying `M_r`.** That covers the four 23.441/23.443 conditions and every delivered one-engine-out case, each engine. Its stations are (i) the fin condition's T-5 trim load, read from the owner the fin transfer reads (`ttail_transfer`'s pair: `point.lt` at its published CP `_tail_cp_station`, split into `lt25`/`lt50` so the CP is exact); (ii) the tail's inertia at the pair's load factor; and (iii) the induced set: `distribute(h, k, 0, rh_scale=+1, lh_scale=−1)` with `k` such that `Σ fz·y = M_r`. That is chord-proportional, at 25 % chord, zero net lift, and `M_r/2` at each root. The SF is the fin condition's own (one-engine-out VC stays `ULT SF=1.0`). The label is `INDUCED ROLL — <fin condition>`, FAR `23.427(c)`, and the ID comes from a new band, `HTAIL_BAND_TTAIL = 20` (**HT-20**…HT-49). It reaches the h-tail CSV, the case index and the report. This is HTAIL UNSYM's mirror (D-51.2a) | One governing condition only (each side needs its own envelope, and the engines load opposite sides); a linear antisymmetric shape (a second shape owner, where 23.427(a)'s chord shape already exists); pairing with the critical h-tail load (#335 (b), below) |
| D-51.4b *(replaces D-51.4a)* | **The deck carries `M_r` on the horizontal tail, not at the fin tip.** Each T-tail lateral and one-engine-out balanced case swaps the `vtail-induced-roll` couple for D-51.12's induced strips (iii) only, `source = "htail-induced-roll"`, `side` R/L, routed to the h-tail member. The case already carries the trim tail load lumped, so (i)–(ii) are not added again. The set has `Σ fz = 0`, `Σ fz·y = M_r` and `Σ fz·x = 0` (`x` is symmetric about the centreline), so the closure is unchanged: `ṗ`, `ṙ`, `q̇` and the inertia field are identical. The h-tail centreline is rigid to the fin tip, so the fin root `Mx` is unchanged. The port twin reflects it through `reflect_load` | Keeping the couple and adding the strips (double-counts the roll); the strips on the h-tail view only (the deck would still not size the stabiliser) |
| D-51.7a *(retires D-51.7)* | **The check retires.** With the load carried, `M_r/2` against a governing it can itself become is circular. `check_htail_under_induced_roll`, `ttail_induced_roll_sizes_htail` and `InducedRoll.htail_ratio` go. Schema **v76**, with `_hop_75` dropping the field | Keeping the ratio as a statement (a number with no consumer — the consolidation ruling) |
| D-51.13 | **#335 ruled (a): T-5 is the only pairing policy.** AC 23-9 ¶5d p5 names the pairing ("combined with the applicable level flight balancing load"). Plan 09 §8's superposed-critical option closes on that citation, and §8's parked row with it | (b) a selectable superposed policy (pairs loads the airplane never sees together; the AC prescribes the rational pairing) |
| D-51.10a *(amends D-51.10)* | The fin view is unchanged: the tip transfer still carries `mxx = M_r`, and the root rolling moment with the tip set (G-51.7) does not move | — |

### 10.3 Gates (no printed oracle — rule 2's second branch)

| Gate | What is asserted | Expected (RJ / ATR) | Tolerance |
|---|---|---|---|
| G-51.12 | Each induced set: `Σ fz = 0`, `Σ fz·y = M_r`, and each root carries `±M_r/2` | — | 1e-9 |
| G-51.13 | Each D-51.12 condition's per-side root bending | §10.1 table | ±0.1 % |
| G-51.14 | The ATR's governing h-tail root bending is ONE ENGINE OUT VD; the RJ's is unchanged | ATR 233,122 · RJ 349,920 | ±0.1 % |
| G-51.15 | In every T-tail lateral and one-engine-out balanced case, `ṗ`, `ṙ`, `q̇` and the fin root `Mx` equal their pre-change values; no `vtail-induced-roll` load remains; exactly one induced set per case | — | 1e-9 |
| G-51.16 | The D-51.12 condition's trim part equals the fin transfer's `fz`/`myy` about the tip (one pairing owner) | — | 1e-9 |
| G-51.9 *(retired)* | Replaced by G-51.14 | — | — |
| G-51.11 *(extended)* | Conventional isolation: no `INDUCED ROLL` condition and no `htail-induced-roll` load off a T-tail; ga6, the Baron and concept_heavy are digest-identical | — | exact |

### 10.4 Effect vs error bar (rule 6)

ATR horizontal-tail governing root bending +44.4 % (LIMIT), against the base
method's ±5–10 %: it ranks. The RJ does not move. The fin does not move on
either fixture.

### 10.5 Closure obligations (tier L)

`PROGRAM_SPEC.md` (tail-span, balance, export); `CONVENTIONS.md` §7 (the
D-51.12 owner; the check row removed); `case_ids.py` (`HTAIL_BAND_TTAIL`);
`theory_sources.md` (the 23.427 row: the h-tail carries ¶5a's moment, ¶5d's
pairing); the report's 6.5 and the h-tail sections; `INDUCED_ROLL_NOTE`
rewritten; schema v76 and its hop; the digests regenerated (RJ and ATR only);
plan 09 §8 closed; note 66 §13; one history fragment in full step format.
