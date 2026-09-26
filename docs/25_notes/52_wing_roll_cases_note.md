# The wing's rolling cases arrive complete (design note 52)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-09-25 (#306, 0.8.7 band B8) — §9 records the build
against the gates.** AGREED 2026-09-07 (owner); amended and re-agreed
2026-09-22 (owner, in session): D-52.10–D-52.13 added, the gates re-pinned,
filed to 0.8.7 (band B8). The three open decisions were resolved in the
2026-09-07 review: **D-52.5 decided (owner: implement the cm increment,
blank-reduces-to-oracle)**, **D-52.7 decided (owner: flagged error)**,
**D-52.8 decided (owner: design maximum weight)**. The 2026-09-22 amendment
follows the #294 review of the ACRL chain against Reference 1: note 63 moved
delivery onto the variant table after this note was agreed, and the table
carries the roll point's own lift, not condition A's (D-52.10); the manual's
70→75 % other-side rule is the pre-1996 wording of 23.349(a)(2), which
Amendment 23-48 made 75 % flat (D-52.11); the Appendix A case 160 lock moves
into a test-built case so the shipped fixture can follow the amended rule
(D-52.12); and the acrobatic gap reaches FLTLOADS, where no category branch
exists (D-52.13). #295 and #258 fold into this step.

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
  the `balance/air.py` `unbalanced_rolling_moment` docstring, and the report
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
- **The delivered ACRL semispan carries the wrong lift** *(found 2026-09-22)*.
  Since note 63 (#292) the wing set that reaches the deck is the variant
  table's governing run, and `wing_variants.wing_variant_table` builds every
  row's air load from the V-n point's own `cl`/`v_eas_kt`. For ACRL that point
  is the AC ROLL corner, balanced at the *airplane-average* load factor
  `(100 + p)/200 · n₁`, so its lift is the average of the two sides — on the
  GA6, CL 1.328 against condition A's 1.55. The manual's governing side is
  condition A in full (§2); the entered GA6 case says so (`cl: 1.55`), but
  the delivered variant does not. Root air bending on the delivered side is
  ≈ 440,000 lb-in against the printed 514,475, and with the relief the net is
  ≈ 316,000 against 390,380 — **19 % low on the case the manual calls
  critical for centre-section shear and concentrated-weight attachment**. D-29
  accepted the derived-route divergence on the premise that every fixture
  enters its cases explicitly and explicit wins; note 63 removed that premise
  for the delivered path.
- **The variant table ranks ACRL on a load it does not deliver** (#295): the
  rows are built with the couple at zero, so the governing run is chosen on
  the balanced part alone while the delivered case carries `unbal_moment`.
  Deriving the moment (D-52.2) on every row closes it.

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

*(the manual's rule — superseded by D-52.11: 14 CFR 23.349(a)(2) as amended by
Amdt 23-48, 61 FR 5144, 1996-02-09, reads "assume that 100 percent of the
semispan wing airload acts on one side of the airplane and **75 percent** of
this load acts on the other side" for normal, utility and commuter; the linear
70→75 % rule is the pre-1996 wording the 1996 manual still carried. Paragraph
(a)(1), acrobatic, keeps 60 % and adds **condition F**. Paragraph (a) opens
"unless the following values result in unrealistic loads", so the percentage
method is the permitted construction, not the requirement itself.)*

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
| D-52.1 | **One owner for the other-side percentage**: `other_side_percent(weight_lb, category)` — the rule it implements is D-52.11's (75 % flat), the weight argument kept for the category flag and the record — single source + drift-guard test (CLAUDE.md rule 3), placed beside the tail unsymmetric-percent precedent (`select.py:862-907`) or in `constants.py` — final home at implementation. **FLTLOADS reads the same owner**: the AC ROLL load factor `(100 + p)/200 · n₁` in `flight_envelope._config_points` is the only other place the percentage lives, and it is not a second literal | A literal in the UNB derivation — cross-cutting percentage with a regulatory basis; prose-only rules are how the units history happened |
| D-52.2 | **UNB is derived, not entered**: `accel_roll_unbalanced_moment(project)` = (1 − p/100) × (ACRL airloads root Mxx); `resolve_wing_cases` fills it on *derived* ACRL cases. An **entered** case keeps its entered value (existing projects unchanged); the limitation text at `wing_inertia.py:410` is deleted | Requiring hand entry forever — the documented gap this note exists to close |
| D-52.3 | **Both readers read one owner**: `balance/air.py`'s `unbalanced_rolling_moment` returns the resolved (entered-else-derived) value, so the balanced deck and the wing chain can never disagree | Leaving `balance.py` entered-only — two provenance paths for one physical quantity |
| D-52.4 | **The derivation is published**: UNB, p, the condition-A root moment it came from, θ̈, and the deflection schedule (δ at VA/VC/VD from `resolved_full_down_aileron_deg` and the speeds) surface as `LoadValue`s on the rolling wing cases — folding in the standing tier-M backlog finding "the deflection schedule is computed but not published" without touching `aileron.py` | Publishing from the aileron module — wrong owner (§2), and it would need an OR-15 admission for no reason |
| D-52.5 | **The TORS cm increment is implemented, blank-reduces-to-oracle** *(decided 2026-09-07)*: two additive optional schema fields, aileron inboard/outboard butt lines, on the aileron input slice; when present, the TORS case's airloads apply Δcm = −0.01·δ_case over that extent via the same double-station step the flap case uses, on the existing per-station `section_cm` mechanism (`airloads.py:394`). δ_case is SELECT's own schedule value — selection proxy and applied load use the same δ. **Blank fields → uniform cm → exactly the printed Appendix A path**; `ga6_normal` is not touched (the note-45 no-baggage precedent), so every existing lock holds | (a) Replicating only the printed run — underpredicts outboard torsion 2.4× against the manual's own stated method (§5); (b) always-on increment — breaks the oracle lock and forces geometry on every project |
| D-52.6 | **Report Section 3 gains a rolling-conditions subsection** (between the current 3.2 and 3.3): the 23.349(a)/(b) method, the percentages, the UNB derivation with its numbers, θ̈, the deflection schedule, and the statement that the printed distributions are the governing (100 %) side of an unsymmetrical condition. §3.4's five distribution figures and Appendix B pick the cases up automatically through `_wing_net`; the G-OR-26 case-order gate extends over them | A separate roll section outside §3 — the cases are wing cases; the oracle prints them inside the wing loads run |
| D-52.7 | **Acrobatic category is a flagged error** *(decided 2026-09-07)*: `other_side_percent` raises/flags on `acrobatic` rather than silently applying 60 % — matching the governing safety-factor-table rule that an unclassifiable case is flagged, never defaulted. The 60 % branch ships when an acrobatic project exists to verify it | Implementing 60 % untested — a constant with no fixture behind it |
| D-52.8 | **p uses the design maximum weight** *(decided 2026-09-07)*: the regulation and the manual say "design weight"; the GA6 example used 3400 lb (design gross) regardless of the case's loading. Conservative in the delivered direction: higher W → higher p → smaller UNB → smaller θ̈ → less inertia relief → higher net load on the delivered 100 % side, whose airload does not depend on p. p is a fixed airplane property, printed once in the D-52.6 subsection | The case's loading weight — per-case p the regulation does not describe, and anti-conservative at light loadings |
| D-52.9 | **Provenance sweep (rule 4)**: the three "UNB comes from AILERON" statements (`wing_inertia.py:410`, the `balance` package docstring, `oracle_sections.py:1880`) are corrected to the condition-A derivation in the same change | Fixing only the one the implementation touches |
| D-52.10 *(2026-09-22)* | **The delivered ACRL air load is condition A's.** One owner, `acrl_air_point(project, vn, pick)` (name final at implementation), resolves the condition A point — the STALL +N corner at the picked AC ROLL point's weight, altitude, CG and configuration — and the variant table builds the ACRL row's air load at that point's `cl`/`v_eas_kt`, with the AC ROLL point's own `nz`/`dx` for the inertia (the airplane-average factor is the inertia the airplane feels; the 100 % side is the air load it carries). The same owner feeds a derived `WingLoadCase` its `cl`/`v_eas_kt`, so the derived and delivered routes agree; an **entered** `cl`/`v_eas_kt` still wins (the 2026-08-13 ruling). **D-29 is superseded for every path that reaches a deliverable**; it survives only as the record of why the divergence was once accepted. Drift guard: on every fixture the delivered ACRL variant's `air_root_mxx` equals the condition A air distribution's root `mxx` (G-52.10) | Leaving the variant on the roll point's lift — 19 % low on the governing side (§5); or scaling the roll point's distribution by `200/(100 + p)` — the same number on the GA6 but a second producer of condition A's lift |
| D-52.11 *(2026-09-22)* | **The other-side percentage is 23.349(a)(2) as amended — 75 % flat** for normal, utility and commuter; 60 % acrobatic stays behind D-52.7. The manual's 70→75 % linear rule is retired and recorded in `02_approved_corrections.md` as the pre-Amdt 23-48 wording, with the moved figures (§4). The AC ROLL load factor becomes `0.875 · n₁` at every weight (the `w ≤ 1000` branch goes with the rule). Conservative in the couple's direction on nothing and in the load factor's direction on everything: UNB falls (149,043 → 128,619 on the GA6), the averaged factor rises (3.25 → 3.325), the 100 % side's air load is unchanged, and the net governing-side root bending rises ≈ 2 % | Keeping the manual's rule as the default with the amendment selectable — two rules for one regulatory quantity, and the oracle-lock policy already has the register for exactly this case (the 23.361 entries) |
| D-52.12 *(2026-09-22)* | **The Appendix A case 160 lock lives in a test-built case, the fixture follows the amended rule.** The WINGINER/NETLOADS oracle tests construct the case 160 entry themselves (nz −3.25, nx +0.4009, UNB −149,043, CL 1.55 at 116 kt) and hold the printed rows bit-for-bit, so the `.BAS` math stays oracle-locked whatever the rule; `ga6_normal`'s entered ACRL row is retired to derived (`case`/`nz`/`nx`/`unbal_moment`/`cl`/`v_eas_kt` null), so the shipped fixture exercises the derivation and the SELECT pin, the digests and the report move to the amended figures under the register entry | Keeping the entered row — the fixture would then disagree with its own derived value, and D-52.2's "entered wins" would hide the derivation on the one fixture with a printed oracle |
| D-52.13 *(2026-09-22)* | **The acrobatic gap is flagged where the roll points are made.** `flight_envelope._config_points` has no category branch: an acrobatic project today gets the normal percentage silently and no roll point from condition F (23.349(a)(1)). D-52.7's flag is raised by the percentage owner, which FLTLOADS now calls (D-52.1), so the AC ROLL point is refused on an acrobatic project with the same flagged error; the condition F point and the 60 % branch ship together when an acrobatic fixture exists (§8) | A silent normal-rule default — the 20-day shadow of #160's kind |

GUI: no structural change — `app/views/wing_loads.py` receives the cases
complete from `resolve_wing_cases`; it gains only a per-case caption showing
UNB/θ̈ when nonzero.

## 4. Gates (the closure targets, with expected numbers)

All oracle pins ±0.1 % (`math.isclose(rel_tol=1e-3)`), page-cited in the test,
GA6 (`ga6_normal` untouched — the D-52.5 fixture is separate).

| Gate | Statement | Expected | Source |
|------|-----------|----------|--------|
| G-52.1 | Derived UNB for the GA6 ACRL case | **128,619 lb-in** from (1 − 0.75)·514,475 *(amended 2026-09-22; the manual's 149,043 from 71.03 % is the register's recorded original)* | pp. 96, 212, 219; `02_approved_corrections.md` |
| G-52.2 | Percent owner, normal/utility/commuter at any weight | **75 %** *(manual: 71.04 % at 3400 lb, formula 71.0435)*; acrobatic → flagged error (D-52.7/D-52.13) | 23.349(a)(2) Amdt 23-48; pp. 92, 96 |
| G-52.3 | WINGINER case 160 with the derived UNB: θ̈ and root row | θ̈ ≈ −11.47 deg/s² (128,619·386/4,330,081); root Sz ≈ −1058, Mxx ≈ −115,500 — the exact values are computed at implementation and stated in the test beside the printed −13.287 / −1126 / −124,095, which G-52.12 holds | p. 219 |
| G-52.4 | Net case 160 root (100 % side), **asserted on the delivered variant** (D-52.10), air at condition A | Sz ≈ +5378, MX ≈ +399,000 (514,475 − G-52.3's Mxx); the printed +5310 / +390,380 is G-52.12's | p. 225 |
| G-52.5 | Net case 138 root, blank aileron BLs | Sz +3823, MX +282,393, MY −46,283 (unchanged — TORS carries no percentage) | p. 226 |
| G-52.6 | Station-sum identity (air + inertia = net) holds on both rolling cases, on the delivered variants; knit checks 514,475 − G-52.3 = G-52.4 (MX), and on the test-built case 514,475 − 124,095 = 390,380 (MX), −78,716 + 30,410 = −48,306 (MY), −57,444 + 11,161 = −46,283 (138 MY) | exact | pp. 212, 217, 219, 225, 226 |
| G-52.10 | Delivered lift is condition A's: on every fixture the ACRL variant's `air_root_mxx` equals the condition A air distribution's root `mxx`, and the variant's `cl`/`v_eas_kt` are the STALL +N point's at the picked case's weight/altitude/CG (GA6: CL 1.55, 116 kt, root 514,475) | identity, `rel_tol = 1e-9`; GA6 root ±0.1 % | p. 212 |
| G-52.11 | One percentage: the AC ROLL load factor in FLTLOADS is `(100 + p)/200 · n₁` read from the D-52.1 owner (GA6: 3.325), and SELECT's ACRL pick re-pins at that point (CL ≈ 1.36 at 116 kt, CG2, 12,000 ft — exact value stated in the test beside the printed 1.328) | identity; pin ±0.5 % | p. 68; Appendix A "Critical Wing Loads" |
| G-52.12 | The oracle lock: a test-built case 160 (nz −3.25, nx +0.4009, UNB −149,043, CL 1.55 at 116 kt) reproduces the printed WINGINER and NETLOADS rows — θ̈ −13.287, root Sz −1126 / Mxx −124,095 / Myy +30,410; net Sz +5310 / MX +390,380 / MY −48,306 / MZ −87,026 | ±0.1 % | pp. 219, 225 |
| G-52.13 | An acrobatic project: FLTLOADS refuses the AC ROLL point with the D-52.7 flagged error, never the normal percentage silently; no condition F point is emitted until §8's item ships | flagged | 23.349(a)(1) |
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
- **The delivered lift (D-52.10) is 19 % of the net governing-side root
  bending** on the GA6 (≈ 316,000 delivered against 390,380 printed): the roll
  point's lift is `(100 + p)/200` of condition A's, 85.5 % under the manual's
  rule, 87.5 % under the amended one. First-order on the one deck that ships;
  the largest single number in this note.
- **The amendment (D-52.11) moves the net governing-side root bending ≈ +2 %**
  on the GA6 (390,380 → ≈ 399,000): UNB −14 %, the averaged load factor
  +2.3 %, the 100 % side's air load unchanged. Outside the ±0.1 % oracle band,
  inside the base-method band — recorded in the register because it is a
  deliberate deviation, not because it is large.
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
- *(2026-09-22)* **D-29** (`03_resolved_decisions.md`) for every path that
  reaches a deliverable — superseded by D-52.10; the row gains the dated
  pointer. **The manual's 70→75 % rule** — superseded by D-52.11, recorded in
  `02_approved_corrections.md`. **#295** (the variant table ranks ACRL without
  the couple) and **#258** (a derived ACRL states nothing in band about its
  zero couple) — folded: D-52.2 derives the couple on every row and D-52.4
  publishes it, so both close with this step and their rows leave the backlog
  at the amendment. The `wing_inertia.resolve_wing_cases` limitation paragraph
  and `test_the_acrl_divergence_is_the_documented_one` go with D-29.

## 7. Closure obligations (tier L)

- `PROGRAM_SPEC.md`: wing-inertia and select sections (derived ACRL is
  complete; the D-52.5 fields); the rolling-conditions limitation paragraph
  rewritten.
- `theory_sources.md`: Ch 12/13 page citations for the derivation and the
  schedule; the §2 worked-example inconsistency recorded.
- `DATA_DICTIONARY.md` regenerated (via the generator) for the two new fields.
- `changes/` fragments + history fragment in full step format; backlog
  removals per §6.
- `CONVENTIONS.md` §7 SSOT table: three new rows (percent owner, UNB
  derivation, the condition A air point) with their drift guards.
- *(2026-09-22)* `02_approved_corrections.md`: the 23.349(a)(2) entry (written
  at the amendment; the implementation adds the test names). `ch04_wing_loads.md`
  §"The rolling conditions": written at the amendment, its "until this note
  ships" sentence removed at closure. `examples/ga6_normal.project.json`: the
  ACRL row retired to derived (D-52.12); one Imperial digest wave on the GA6
  (SELECT, WINGINER, NETLOADS, the report and the deck all move), stated in
  the history fragment. `03_resolved_decisions.md` D-29: the dated pointer.
  GitHub: #295 and #258 closed by the step's PR with the fold stated.

## 8. Deferred (parked with the numbers, owner ruling 2026-09-07)

- **Full-span left/right paired wing cases and a reported total** — dropped to
  stay faithful to the original oracle, which prints the governing side only
  and carries balance implicitly in the θ̈/UNB inertia terms. The full-span
  free-free representation already exists where it belongs: the balanced deck
  (`balance/air.py` + `balance/closure.py`, `aileron-roll` couple + `closure-roll` inertia, G-OR-72).
- **The other-side (p %) distribution as a delivered table** — the oracle
  prints only the 100 % side (p. 225 "100 PERCENT SIDE"); the p % side is the
  same rows scaled, and ships only if a consumer asks for it.
- **The aileron's own spanwise lift increment (#14)** — distinct from the
  D-52.5 *pitching-moment* increment; stays parked on its existing trigger
  ("a consumer sizes to ACRL" with distributed aileron lift).
- **The acrobatic 60 % branch and the condition F roll point** — parked behind
  D-52.7/D-52.13 until an acrobatic fixture exists. 23.349(a)(1) constructs the
  acrobatic roll from conditions A **and F** (the negative stall corner,
  STALL −N) at 60 %; FLTLOADS emits no F-based roll point today and, after
  D-52.13, refuses the A-based one on an acrobatic project rather than
  mis-scaling it. Both ship together, with the F point's SELECT family
  (a negative-lift accelerated roll, no slot today) decided in the note that
  brings the fixture.

## 9. As implemented (#306, 2026-09-25)

Owners: `constants.other_side_percent` / `ROLL_OTHER_SIDE_PERCENT` (D-52.1,
D-52.11; `UnsupportedCategoryError` for D-52.7/D-52.13) and the new
`modules/rolling.py` (`condition_a_point`, `condition_a_root_mxx`,
`accel_roll_unbalanced_moment`, `roll_acceleration`, `derive_accel_roll`,
`complete_rolling_case`, `steady_roll_schedule`/`steady_roll_deflection`,
`steady_roll_aero`, `aileron_cm_increment`). Gates: `tests/test_rolling_conditions.py`
(G-52.1–G-52.13), plus the FLTLOADS case 20 pair in `tests/test_flight_envelope.py`.
Schema v69 (`_hop_68`): `WingLoadCase.unbal_moment` is `Optional`, blank
derived; every stored `0` migrates to `null`.

Where the build departs from what §3/§4 predicted — each measured and stated
in the tests:

1. **The GA6's ACRL pick moved altitude.** At `0.875·n₁` the CG2 `AC ROLL`
   points' LZW (SELECT's criterion) tie across altitude to 0.13 %, inside the
   balance's 0.5 %, and sea level (V-n case 40, CL 1.326 at 117.45 kt) wins
   over the printed 12,000 ft point (CL 1.361 there — G-52.11's "≈ 1.36" is
   that point, not the pick). Condition A is then the case 22 air (CL 1.519,
   root 516,566): UNB −129,142, θ̈ −11.515, net root MX **+400,817** (+2.7 %
   on the print; G-52.4 predicted +399,000 at 12,000 ft). G-52.1/G-52.3 are
   asserted at the printed condition A (CL 1.55, 116 kt): UNB 128,619, θ̈
   −11.468, WINGINER root Sz −1046.3 / Mxx −114,286 (the §4 −1058 / −115,500
   were hand estimates). **Open for the owner:** whether a 0.13 % LZW tie
   should keep SELECT's printed altitude (a tie band on the ACRL pick) — not
   decided here; the build follows SELECT's criterion as it stands.
2. **θ̈ is rad/s².** WINGINER prints `THETADOT` unlabelled (pp. 214, 219);
   `UNB·g/I_wxx` is 1/s². §4's "deg/s²" was a labelling slip; published as
   `rad/s^2` (a `DELIVERED_PRECISION` row, three places as printed).
3. **D-52.5 needed no new field.** `AileronLoadsInput.inboard_y_in` /
   `outboard_y_in` exist since v52 (note 24 R-2); the increment reads them.
   G-52.7's root ΔMyy is −18,667 (δ 10.7065°), against the hand estimate
   −19,035. The increment is wing-chain only (NETLOADS, the variant table);
   the balanced deck's TORS stays the symmetric trim case — the increment is
   antisymmetric between the down- and up-going ailerons.
4. **The balanced deck derives where the wing list omits ACRL.** An entered
   list is a filter (D-63.7); on `baron_58` and `concept_heavy` it names no
   ACRL while SELECT does, so `balance.air.unbalanced_rolling_moment` derives
   the couple at the balanced case's own V-n point through the same owner.
   Consequence: **every fixture's ACRL is now a handed pair** — the ATR, the
   Baron and `concept_heavy` assembled a symmetric ACRL with no couple before
   (#258 across the fleet, not only on the derived route).
5. **The published derivation** (D-52.4) rides on the delivered wing
   `CriticalCondition`: `other_side_percent`, `condition_a_cl`,
   `condition_a_v_eas`, `condition_a_root_mxx`, `unbalanced_rolling_moment`,
   `roll_acceleration` on ACRL; `aileron_down_deflection` and the VA/VC/VD
   schedule on TORS.

