# The T-tail fin carries the horizontal tail's asymmetry (design note 51)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-06 (owner) — no code.** D-51.3's theory source is
FAA **AC 23-9** (2026-09-06 review); **D-51.3a decided (owner: net β)**;
**D-51.6 decided (owner: yaw parked with the numbers)**.

**Tier L** (new load case, new physics on the fin deck). The T-tail transfer sits in
the review-§3 frozen list; this note is the owner's explicit admission reopening
*distributed empennage loads / T-tail transfer* for exactly this scope and nothing
else.

## 1. What the code does today, and what is missing

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

| # | Decision | Alternative rejected |
|---|----------|----------------------|
| D-51.1 | **`TipTransfer` grows `mxx` (roll at the fin tip, airplane axes, default 0.0)** — additive schema change, no migration hop. T-16 is *narrowed*, not repealed: roll is zero **for a symmetric pairing** and carries the paired set's net rolling moment otherwise; the docstring states both | Keeping T-16 absolute — it was a statement about the T-5 balancing pairing, and both new producers (D-51.2, D-51.3) are asymmetric by construction |
| D-51.2 | **New fin critical condition `HTAIL UNSYM` (23.427(c)/(a))**: the h-tail's selected 23.427(a) case reacted through the fin — tip set = that case's `Fz`, `Myy` and net rolling moment `Mxx`; the fin's own airload in this condition is zero ("taken separately"). Expected RJ numbers: `Mxx = +72,547 lb-in`, `Fz`/`Myy` from the case-34 set (`lt25` 3,840.9, `lt50` 8,312.8 lb) | Superposing the roll moment onto the four existing fin cases — pairs loads the airplane never sees together; (c) says *each prescribed condition taken separately*, and the T-5 rational-pairing policy stands (plan 09 §8's conservative option stays parked) |
| D-51.3 | **Induced rolling moment in the four fin conditions per AC 23-9 ¶5a:** `M_r = 0.3·q·S_H·b_H·β`, delivered as a tip `Mxx` in the widened transfer, with an antisymmetric zero-net-lift h-tail span distribution carrying it on the h-tail's own deck. β per condition: SUDDEN RUDDER `RD·EFV·EFFECTV` (the AC's "dependent on rudder geometry" — sloads' own rudder-effectiveness machinery, one owner); YAW TO SIDESLIP 19.5°; YAW 15 NEUTRAL 15°; SIDE GUST `1.2·U/V`. RJ expected values in §4. **D-51.3a (owner, 2026-09-06):** YAW TO SIDESLIP's β is the **net** effective angle — 19.5° *minus* the held-rudder equivalent — because at the overswing the rudder still opposes the sideslip, lowering the effective β; the 19.5°-alone approximation is conservative (past experience) and is not used. This parallels SELECT's own superposition of the two fin-load terms in that condition (−10,456 + 6,908 lb on the RJ) | A carryover model derived from the fin load (DATCOM/ESDU interference factors) — rational and pre-scoped as the upgrade path, but the AC formula is the FAA's own published floor, needs only inputs sloads already holds, and self-checks against the AC's 4–6× band. Also rejected: the 23.427(b) split applied to the concurrent balancing load — produces ~0 on the RJ (+6.3 lb balancing load) exactly where the physics is largest, and the AC's 4–6× statement is the authority that the split is not a substitute |
| D-51.4 | **Export plumbing:** `ttail_transfer_to_airplane` widens to `(fz, myy, mxx)`; `mxx` maps to airplane `mx` — the only `Mx` card a fin deck carries, so its closure gate is an identity (§4). One `FORCE` + one `MOMENT` card as today | A separate roll card at its own GID band — the transfer is one physical set at one node |
| D-51.5 | **The balanced free-free deck is untouched.** The h-tail's unsymmetrical strips already sit at the fin-tip waterline with the correct roll arm; the fin-path is a per-component structural view. D-51.3's induced load, once pinned, is *also* added to the lateral balanced cases' h-tail strips (same producer, one owner) — a second implementation step under the same note | Routing D-51.2's lumped set into the balanced deck — double-counts the strips (the same reason T7 was excluded there, plan 11 §4) |
| D-51.6 | **Yaw transfer stays zero — parked with the numbers** (owner, 2026-09-06). The only physical producer is chordwise (drag) asymmetry on the h-tail: differing left/right induced drag makes a couple about the fin's vertical axis, landing in the fin **torsion** channel (shared `mz` component and sign convention with strip torsion, `coordinates.tail_torsion_to_airplane`). Sized on the RJ: (i) worst case is the 23.427(a) split (RH 5,816 / LH 4,600 lb at 187 KEAS) → ΔD ≈ 158 lb at the 59.7 in side centroid → **9,399 lb-in**, 1.83 % of governing fin bending and 5–24 % of the fin's *own-case* torsion (40–185 k lb-in) — but that producer exists only in the D-51.2 condition, where the fin carries no own aero, so 9.4 k lb-in can never govern the torsion envelope its own cases set; (ii) in the four fin conditions the D-51.3 induced set is antisymmetric about a ~zero balancing CL (+6 lb on the RJ), and induced drag is quadratic in CL, so its left/right drag difference cancels to second order — no producer. AC 23-9's method itself prescribes **only** the rolling moment (¶5a) | Adding an `mzz` field "for symmetry" — a number with no producer, the exact failure T-16 guarded against; or gating a 1.8 %-of-bending term the base method cannot resolve (±5–10 % band, rule 6) |

## 4. Gates (the closure targets, with expected numbers)

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
  `coordinates.py` and `sbeam_bridge.py` comment blocks updated together.
- **Note 21 §5** — "(b)" → "(c)", stale backlog-step-9 pointer replaced.
- `docs/30_future/21_power_effects_wing_note.md` G6-6 cites "(b)'s ratios" —
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
