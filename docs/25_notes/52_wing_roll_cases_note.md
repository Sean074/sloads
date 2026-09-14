# The wing's rolling cases arrive complete (design note 52)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-07 (owner) — no code.** The three open decisions were
resolved in the 2026-09-07 review: **D-52.5 decided (owner: implement the cm
increment, blank-reduces-to-oracle)**, **D-52.7 decided (owner: flagged
error)**, **D-52.8 decided (owner: design maximum weight)**.

**Tier L** (new physics derivation, new published quantities, additive schema
change). Lands in 0.8.2 after the freeze lifts with the drafting of the three
remaining report sections. Scope ruling by the owner (2026-09-07): **semispan,
governing (100 %) side only** — the full-span left/right pairing and reported
total-load ideas raised in the same review were explicitly dropped to keep
sloads close to the original oracle; they are parked in §8.

## 1. What the code does today, and what is missing

The roll physics already exists and is verified applied. `wing_inertia` builds
WINGINER's unit-roll distribution — `Fz = W·Y·100000/Iwxx`, `Iwxx = 2·ΣW·y²`
including concentrated masses (`sloads/modules/wing_inertia.py:200-203`) — and
`wing_inertia_distribution` scales it by `unbal_moment/100000` into
fz/sz/mxx/myy with the 50 %→25 % chord free-moment term and the point masses
(`:270-288`). `net_loads` sums air + inertia station by station. SELECT emits
`ACRL` (23.349(a)) and `TORS` (23.349(b)) among the six wing conditions, with
the steady-roll torsion proxy `(CM − 0.01·δ)·G·V²` and the CAM 3.222 deflection
schedule already implemented (`sloads/modules/select.py:225-253`).

What is missing is delivery, and one wrong provenance statement:

- **A derived `ACRL` case carries `unbal_moment = 0`** — the documented
  limitation at `wing_inertia.py:410`. The moment must be hand-entered, so in
  practice the rolling cases never reach the GUI wing-loads page, report
  Section 3, or Appendix B.
- **Three places state the moment "comes from AILERON"** (`wing_inertia.py:410`,
  the `balance.py` `unbalanced_rolling_moment` docstring, and the report
  provenance sentence at `oracle_sections.py:1880`). Per the manual (§2 below)
  that is wrong: the unbalanced rolling moment is derived from the condition-A
  airloads root bending moment and the 23.349(a) other-side percentage. No
  aileron geometry is involved. `modules/aileron.py` is **not touched** by this
  note.
- **The TORS distribution omits the 23.349(b) cm increment.** The manual's own
  worked example omitted it too (§2), but the effect is first-order for the
  case that exists to size torsion (§5), so it is implemented behind an
  additive input that reduces exactly to the printed oracle when blank.
- No report subsection states the rolling-condition method, and the published
  quantities (UNB, the percentage, θ̈, the deflection schedule) exist nowhere.

## 2. Governing basis

14 CFR 23.349 (rolling conditions), 23.455 (aileron deflections/speeds),
CAM 3.222 (the 0.5 factor at VD). Method source: `reference/FAR23Loads_Code.pdf`
Ch 12 pp. 91–93 (Wing Airloads — Critical Accelerated Rolling Condition;
Critical Steady Rolling Condition) and Ch 13 pp. 95–96 (Wing Inertia —
Unsymmetrical Rolling Conditions). Printed oracle: Appendix A pp. 203–228.

**ACRL (23.349(a)):** modify symmetric condition A (stall-line ∩ limit-nz on
the 23.333(d) envelope — *not* the point at VA) — 100 % of the condition-A
airload on one side, p % on the other, with

> p = 70 + 5·(W − 1000)/11500   (clamped 70–75 %, normal/utility;
> 60 % acrobatic regardless of weight)

and the unbalanced rolling moment accelerating the roll

> **UNB = (1 − p/100) × condition-A root bending moment.**

GA6: p = 71.03 %, root Mxx = 514,475 lb-in (p. 212) → UNB = 149,043 lb-in
(pp. 96, 219). The ACRL airloads run *is* the condition-A distribution at the
same weight/altitude/CG (case 142 Pt. A ↔ case 160, p. 208), so UNB is
self-derived from the ACRL case's own airloads root moment. WINGINER reacts it
through the unit-roll distribution (θ̈ = −13.287, p. 219). The manual rounds p
inconsistently (71.04 %/148,992 on p. 92; 71.03 %/149,043 on p. 96 and in
Appendix A); the exact formula gives 148,975 — all inside the ±0.1 % band of
the Appendix A value, which is the lock.

**TORS (23.349(b)):** the symmetric distribution at ⅔·n₁ at the ST ROL speed,
with the section pitching-moment coefficient over the aileron portion modified
by **Δcm = −0.01·δ**, δ the down deflection at the case's speed per the CAM
3.222 schedule (GA6 case 138: δ = 15·(121.3/170) = 10.703°, cm = −0.137 over
the aileron area — p. 93). Steady roll: no unbalanced moment.

**The manual's internal inconsistency (recorded in `theory_sources.md` by this
note):** the printed case-138 run entered uniform cm = −0.03 (p. 216) — the
worked example skipped its own Ch 12 instruction — and the net table p. 226
follows it. The flap case (pp. 165–166 of the print, PDF pp. 170–171) proves
the intended input pattern: cm entered per station with a double-station step
at the discontinuity (−.45 at BL 0/109.279, −.03 at 109.280/201). The aileron
portion of the GA6 wing is the same boundary from the other end: BL 109.28–201.

Cross-references: `CONVENTIONS.md` §1 (frames/axes — all quantities on the wing
reference plane along the quarter chord, airplane coordinates), §3 (every
delivered load LIMIT, SF stated per case and applied nowhere — unchanged by
this note), §4 (case identity — ACRL/TORS keep their existing unhanded ids;
no handed pairs, per the §8 parking), §7 (the two new owners of D-52.1/D-52.2
join the single-source table with drift guards).

## 3. Decisions

| # | Decision | Alternative rejected |
|---|----------|----------------------|
| D-52.1 | **One owner for the other-side percentage**: `other_side_percent(weight_lb, category)` implementing the 70→75 % linear rule, single source + drift-guard test (CLAUDE.md rule 3), placed beside the tail unsymmetric-percent precedent (`select.py:862-907`) or in `constants.py` — final home at implementation | A literal in the UNB derivation — cross-cutting percentage with a regulatory basis; prose-only rules are how the units history happened |
| D-52.2 | **UNB is derived, not entered**: `accel_roll_unbalanced_moment(project)` = (1 − p/100) × (ACRL airloads root Mxx); `resolve_wing_cases` fills it on *derived* ACRL cases. An **entered** case keeps its entered value (existing projects unchanged); the limitation text at `wing_inertia.py:410` is deleted | Requiring hand entry forever — the documented gap this note exists to close |
| D-52.3 | **Both readers read one owner**: `balance.py.unbalanced_rolling_moment` returns the resolved (entered-else-derived) value, so the balanced deck and the wing chain can never disagree | Leaving `balance.py` entered-only — two provenance paths for one physical quantity |
| D-52.4 | **The derivation is published**: UNB, p, the condition-A root moment it came from, θ̈, and the deflection schedule (δ at VA/VC/VD from `resolved_full_down_aileron_deg` and the speeds) surface as `LoadValue`s on the rolling wing cases — folding in the standing tier-M backlog finding "the deflection schedule is computed but not published" without touching `aileron.py` | Publishing from the aileron module — wrong owner (§2), and it would need an OR-15 admission for no reason |
| D-52.5 | **The TORS cm increment is implemented, blank-reduces-to-oracle** *(decided 2026-09-07)*: two additive optional schema fields, aileron inboard/outboard butt lines, on the aileron input slice; when present, the TORS case's airloads apply Δcm = −0.01·δ_case over that extent via the same double-station step the flap case uses, on the existing per-station `section_cm` mechanism (`airloads.py:394`). δ_case is SELECT's own schedule value — selection proxy and applied load use the same δ. **Blank fields → uniform cm → exactly the printed Appendix A path**; `ga6_normal` is not touched (the note-45 no-baggage precedent), so every existing lock holds | (a) Replicating only the printed run — underpredicts outboard torsion 2.4× against the manual's own stated method (§5); (b) always-on increment — breaks the oracle lock and forces geometry on every project |
| D-52.6 | **Report Section 3 gains a rolling-conditions subsection** (between the current 3.2 and 3.3): the 23.349(a)/(b) method, the percentages, the UNB derivation with its numbers, θ̈, the deflection schedule, and the statement that the printed distributions are the governing (100 %) side of an unsymmetrical condition. §3.4's five distribution figures and Appendix B pick the cases up automatically through `_wing_net`; the G-OR-26 case-order gate extends over them | A separate roll section outside §3 — the cases are wing cases; the oracle prints them inside the wing loads run |
| D-52.7 | **Acrobatic category is a flagged error** *(decided 2026-09-07)*: `other_side_percent` raises/flags on `acrobatic` rather than silently applying 60 % — matching the governing safety-factor-table rule that an unclassifiable case is flagged, never defaulted. The 60 % branch ships when an acrobatic project exists to verify it | Implementing 60 % untested — a constant with no fixture behind it |
| D-52.8 | **p uses the design maximum weight** *(decided 2026-09-07)*: the regulation and the manual say "design weight"; the GA6 example used 3400 lb (design gross) regardless of the case's loading. Conservative in the delivered direction: higher W → higher p → smaller UNB → smaller θ̈ → less inertia relief → higher net load on the delivered 100 % side, whose airload does not depend on p. p is a fixed airplane property, printed once in the D-52.6 subsection | The case's loading weight — per-case p the regulation does not describe, and anti-conservative at light loadings |
| D-52.9 | **Provenance sweep (rule 4)**: the three "UNB comes from AILERON" statements (`wing_inertia.py:410`, `balance.py` docstring, `oracle_sections.py:1880`) are corrected to the condition-A derivation in the same change | Fixing only the one the implementation touches |

GUI: no structural change — `app/views/wing_loads.py` receives the cases
complete from `resolve_wing_cases`; it gains only a per-case caption showing
UNB/θ̈ when nonzero.

## 4. Gates (the closure targets, with expected numbers)

All oracle pins ±0.1 % (`math.isclose(rel_tol=1e-3)`), page-cited in the test,
GA6 (`ga6_normal` untouched — the D-52.5 fixture is separate).

| Gate | Statement | Expected | Source |
|------|-----------|----------|--------|
| G-52.1 | Derived UNB for the GA6 ACRL case | 149,043 lb-in from (1 − p)·514,475 | pp. 96, 212, 219 |
| G-52.2 | Percent owner at W = 3400, normal | 71.04 % (formula 71.0435; manual prints 71.03/71.04) | pp. 92, 96 |
| G-52.3 | WINGINER case 160 with derived UNB: θ̈ and root row | θ̈ = −13.287; root Sz −1126, Mxx −124,095, Myy +30,410 | p. 219 |
| G-52.4 | Net case 160 root (100 % side) | Sz +5310, MX +390,380, MY −48,306, MZ −87,026 | p. 225 |
| G-52.5 | Net case 138 root, blank aileron BLs | Sz +3823, MX +282,393, MY −46,283 | p. 226 |
| G-52.6 | Station-sum identity (air + inertia = net) holds on both rolling cases; knit checks 514,475 − 124,095 = 390,380 (MX), −78,716 + 30,410 = −48,306 (MY), −57,444 + 11,161 = −46,283 (138 MY) | exact | pp. 212, 217, 219, 225, 226 |
| G-52.7 | D-52.5 fixture (BLs 109.28/201, δ = 10.703°): ΔMyy at the root vs the blank run | ≈ −19,035 lb-in nose-down (−0.10703·97.966·∫c²dy/144, ∫c²dy = 261,419 in³ for c 62.253→44 over 91.72 in; exact value computed and stated in the test) | Ch 12 p. 93 + planform pp. 203, 213 |
| G-52.8 | D-52.5 reduction: the fixture with blank BLs reproduces G-52.5 bit-for-bit | identical rows | — |
| G-52.9 | Drift guards: the percent owner is the only source of 70/75/12500/1000; the UNB derivation is the only producer of a derived case's `unbal_moment` | grep-style guard per rule 3 | — |

Report gates: the D-52.6 subsection carries the standing SF statement per case
(G-OR-73/74 pattern — LIMIT, stated, applied nowhere); G-OR-26 ordering extends
over the rolling cases in §3.2/3.3/3.4 and Appendix B.

## 5. Effect vs error bar (rule 6)

- **UNB relief is 24 % of the ACRL root bending** (−124,095 inertia vs 514,475
  air, p. 212/219): omitting the derivation doesn't perturb the case — it
  removes it. First-order on shipped content; this outranks fidelity items.
- **The cm increment**: net root MY −46,283 → ≈ −65,300 (**+41 %**); at
  BL 145.7, −7,198 → ≈ −17,100 (**2.4×**). Outboard torsion is the quantity
  TORS exists to deliver; far above the base-method ±5–10 % band, so per the
  owner's D-52.5 ruling it is implemented rather than parked.

## 6. What this supersedes / corrects

- The `wing_inertia.py:410` limitation and both other AILERON-provenance
  statements (D-52.9).
- The backlog finding "the aileron deflection schedule is computed but not
  published" (tier M, 2026-09-07) — folded into D-52.4 and removed from the
  backlog at closure.
- Untouched: the aileron hinge-moment scope finding (separate question, stays);
  `modules/aileron.py` (no OR-15 admission needed — nothing in it changes).

## 7. Closure obligations (tier L)

- `PROGRAM_SPEC.md`: wing-inertia and select sections (derived ACRL is
  complete; the D-52.5 fields); the rolling-conditions limitation paragraph
  rewritten.
- `theory_sources.md`: Ch 12/13 page citations for the derivation and the
  schedule; the §2 worked-example inconsistency recorded.
- `DATA_DICTIONARY.md` regenerated (via the generator) for the two new fields.
- `changes/` fragments + history fragment in full step format; backlog
  removals per §6.
- `CONVENTIONS.md` §7 SSOT table: two new rows (percent owner, UNB derivation)
  with their drift guards.

## 8. Deferred (parked with the numbers, owner ruling 2026-09-07)

- **Full-span left/right paired wing cases and a reported total** — dropped to
  stay faithful to the original oracle, which prints the governing side only
  and carries balance implicitly in the θ̈/UNB inertia terms. The full-span
  free-free representation already exists where it belongs: the balanced deck
  (`balance.py`, `aileron-roll` couple + `closure-roll` inertia, G-OR-72).
- **The other-side (p %) distribution as a delivered table** — the oracle
  prints only the 100 % side (p. 225 "100 PERCENT SIDE"); the p % side is the
  same rows scaled, and ships only if a consumer asks for it.
- **The aileron's own spanwise lift increment (#14)** — distinct from the
  D-52.5 *pitching-moment* increment; stays parked on its existing trigger
  ("a consumer sizes to ACRL" with distributed aileron lift).
- **The acrobatic 60 % branch** — parked behind D-52.7 until an acrobatic
  fixture exists.
