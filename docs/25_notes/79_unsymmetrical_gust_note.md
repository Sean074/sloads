# The 25.349(b) unsymmetrical gust, 100/80, and the per-side wing air load on the full airplane (design note 79; #439, #440)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-11-26 — no code.** The owner ruled every question in session, under
the solo profile (rule 1's working-alone branch), one at a time; each ruling is recorded in
place in §4. PROPOSED 2026-11-25. The owner also stated the case's purpose: the 100/80 gust
is a **wing-to-fuselage interface** case and is not meant to be critical in the wing.

**Two steps.** **Step 1, #440:** the per-side mechanism, the whole-airplane roll
acceleration, the solved load factor and the interface table, on the accelerated roll,
every basis; it does not depend on #410. **Step 2, #439:** the 100/80 gust points and slots
on the Part 25 basis, after #410 and step 1.

**Scope.** 25.349(b) puts 100 % of the gust wing air load on one side of the airplane and
80 % on the other. sloads has no such case. This note adds it for the positive and the
negative gust. Its purpose is the design of the wing-to-fuselage interface: the two wing
roots deliver different loads to the body, and the body takes a rolling moment that no
symmetric case gives it. The deliverable is therefore the full-airplane balanced case in
both hands and the interface loads read from it. A wing slot exists only to carry the case
through SELECT to that assembly and into the released set. It also changes how a left/right wing difference is carried on the
full airplane: as different air loads on the two wings, strip for strip, with the rolling
moment reacted by every mass item (25.301(b)). The accelerated roll (23.349(a)(2), 100/75)
moves to that form with it.

Out of scope:
- empennage aerodynamics in the roll (owner ruling: neglected; the tail enters as mass and
  as the symmetric trim load);
- the gust itself (25.341 and VB are #410's; this note reads whatever gust points exist);
- 25.349(a)(1) roll acceleration for outboard masses (#412);
- the 100/80 gust on a Part 23 basis (Q7, ruled: 23.349(a)(2) covers it).

Conventions: [`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §1 (axes; a residual the
airplane is not meant to balance is reported, never gated: `residual_mx` on a rolling
case), §3 (every load LIMIT, the factor stated and applied nowhere), §4 (case ids, bands),
§7.1 (the opposite-hand twin is derived by reflection; the hand is a suffix `L`/`R`).

**Sources** (in `theory_sources.md` at closure):
- 14 CFR 25.349(b) (`reference/14CFR_25_349_rolling_conditions.md`).
- 14 CFR 25.301(b): the air loads "must be placed in equilibrium with inertia forces,
  considering each item of mass in the airplane" (supplied by the owner 2026-11-25; captured
  to `reference/` as G-79.0).
- Reference 1 Ch 12 pp. 90–91 (23.349(a): the 100 % side, the other-side percentage, the
  unbalanced moment and WINGINER's reaction); Appendix A p. 219 (`UNB −149,043`, `θ̈ −13.287`).
- Note 52 (D-52.1 to D-52.3, D-52.10, D-52.12), note 77 (G-77.3 to G-77.5, Q1).

## 1. Measured (prototype, 2026-11-25; not in the tree)

`atr42_100`. The 100 % side carries the gust point's own air load. The airplane load
factor is the gust factor times (100 + 80)/200, balanced with `flight_envelope._balance`.
The unbalanced moment is 20 % of the air root bending. The whole-airplane roll
acceleration is `p_dot` from `balance.assemble` at the gust point's loading. Net = air +
inertia, LIMIT.

| | Positive gust | Negative gust | Accelerated roll (delivered) |
|---|---|---|---|
| V-n point | case 190 `GUST +C`, fwd gross 36,817 lb, 12,000 ft, 240 kt | case 233 `GUST -C`, min weight 22,674 lb, 12,000 ft, 240 kt | case 120 `AC ROLL` |
| Parent / averaged load factor | 2.596 / 2.334 | −1.470 / −1.328 | — |
| Unbalanced moment, lb-in | 1,892,343 | 720,764 | 2,043,682 |
| Roll acceleration, wing inertia alone, rad/s² | 0.765 | 0.823 | 2.334 |
| Roll acceleration, whole airplane, rad/s² | 0.727 | 0.747 | 2.097 |
| Whole airplane ÷ wing alone | 0.95 | 0.91 | 0.90 |
| 100 % side net root bending ÷ symmetric gust | 0.92 | 0.92 | — |
| Same ratio along the span, bending / shear | 0.91–0.97 / 0.84–0.98 | 0.90–0.93 / 0.89–0.94 | — |
| **At the interface (wing root, BL 12):** | | | |
| Net root shear, 100 % side / 80 % side, lb | 26,061 / 23,480 | −10,557 / −9,913 | — |
| Sum of the two root shears ÷ symmetric gust | 0.90 | 0.90 | — |
| Root shear difference, 100 % − 80 % side, lb | 2,581 | −644 | 0 on every symmetric case |
| Antisymmetric net root bending, half the difference, lb-in | 90,058 | −49,134 | 0 on every symmetric case |
| Rolling moment into the body about the centreline, lb-in | ≈ 211,000 | ≈ −106,000 | 0 on every symmetric case |

- **The 100 % wing is not governed by this case** (rule 6): its net loads are 84–98 % of
  the symmetric gust at the same point, for both signs. The roll relief outweighs the lower
  load factor. The symmetric gust is already released.
- **The whole-airplane ruling moves the wing 1 %**: the wing with its fuel and nacelles is
  91–95 % of the airplane's roll inertia on this type.
- **At the interface the case adds a load of a kind the symmetric cases do not have**:
  a rolling moment into the body of about 0.2 × 10⁶ lb-in (positive) and 0.1 × 10⁶
  (negative), with unequal left and right root shears, at 90 % of the symmetric vertical
  load. The body's share is 11–15 % of the unbalanced moment; the wing's own roll inertia
  reacts the rest. Only the accelerated roll delivers such a moment today, and only in the
  positive sense.
- The interface figures are from the wing chain's root station and are indicative; the
  assembled case is the authority (G-79.11).

**The oracle's treatment (Reference 1).** Ch 12 p. 91: the condition A air load "is the air
load for the 100 percent wing", and "to calculate the air loads on the other wing multiply
the air loads on the 100 percent wing by the percentage". The program models one wing and
leaves the other to the user. Ch 12 p. 92: the condition "is critical for shear across the
wing center section and for attachment of concentrated weight components in the wing".
WINGINER reacts the couple with the wing's own roll inertia (pp. 95–96, Appendix A p. 219).

**Step 1 measured**, the delivered accelerated-roll 100 % side with the whole-airplane roll
acceleration:

| | `θ̈` vs today | Net bending, root to tip | Net shear | Roll increment on wing-mounted masses |
|---|---|---|---|---|
| `ga6_normal` | 0.80 | +3.0 % to +7.2 % | +1.8 % to +5.8 % | −20 % |
| `atr42_100` | 0.90 | +1.7 % to +2.4 % | +1.4 % to +2.4 % | 0.97 g → 0.87 g at BL 161 |

Unlike the gust case, the accelerated roll does set parts of the delivered wing envelope,
so these are moved deliverables. Solving its load factor for lift (D-79.3) moves it from
3.3250 to ≈ 3.3185 on `ga6_normal` (0.8729 of n₁) and from 2.1873 to ≈ 2.1962 on
`atr42_100` (0.8798 of n₁).

## 2. Decisions

| # | Decision | Rationale |
|---|---|---|
| **D-79.1** | **Part 25 basis only**, read from #410's switch. On a Part 23 basis no gust-roll point, slot or id appears. | Owner ruling (Q7): on a Part 23 basis 23.349(a)(2)'s 100/75 in condition A covers the unsymmetrical wing load. |
| **D-79.2** | **One percentage owner.** `constants.unsymmetrical_gust_percent()` returns 80, beside `other_side_percent`. Both are read through one function that takes the condition family, so no second literal exists. | Note 52 D-52.1's rule for the 75. |
| **D-79.3** — owner ruling (Q6) | **Companion balanced points, solved for lift.** FLTLOADS adds `UG +C`, `UG -C`, `UG +D`, `UG -D` in each CG and altitude block, at the gust's speed. Each is balanced at the load factor whose wing lift equals `(100 + p)/200` of its parent gust point's wing lift; the solved factor is stated. **The `AC ROLL` point is built the same way** against condition A, replacing the fixed `0.875·n₁`. | The rule fixes the air load on each wing; the load factor follows. The tail load does not scale with the wing, so a fixed fraction of the load factor leaves a lift mismatch (measured: +0.19 % of `n·W` on `ga6_normal`, −0.41 % on `atr42_100`). One definition on every fixture. |
| **D-79.4** | **Two wing slots: `UGSP` (`W-13`) and `UGSN` (`W-14`).** `UGSP` takes the `UG +` point whose parent gust has the largest wing lift; `UGSN` the `UG -` point whose parent has the most negative. The delivered wing is the 100 % side: air at the parent's `cl` and speed, inertia at the companion's `nz` and `dx`. | "Wing maximum airload", read as wing lift (owner ruling, Q4), each sign (owner: positive and negative assessed). The slot is the carrier into the balanced set and the released list, not a wing-critical case (§1), and the report says so. One owner, `gust_roll_parent(vn, pick)`, resolves the parent as `condition_a_point` does. |
| **D-79.5** | **The unbalanced moment is `−(1 − p/100)` × the parent's air root bending**, from `accel_roll_unbalanced_moment`, unchanged. | One producer of a derived `unbal_moment` (G-52.9). |
| **D-79.6** — owner ruling (Q1) | **The roll acceleration is the whole airplane's.** For a derived rolling case the wing chain's `θ̈` is the rolling moment over the roll inertia of every mass item of the case's loading, from the inertia-tensor owner the balance closure uses. The wing's own masses (structure, fuel, nacelles) then react `θ̈` at their own butt lines. | 25.301(b): each item of mass. WINGINER reacts the couple with the wing alone, which over-relieves the 100 % side by 5–10 % of the roll term (§1). See Q5 for the Appendix A path. |
| **D-79.7** — owner ruling (Q2) | **A left/right wing difference is carried as two different air loads.** `balance.wing_sets` takes a per-side factor: starboard strips at 1.0 and port strips at `p/100`, at the parent point's `cl`. The lumped rolling couple at the wing centre, its `aileron-roll` source and `AILERON_COUPLE_NOTE` are deleted. The accelerated roll uses the same path with `p` = 75. | The rule states the load on each wing. A lumped couple rolls the airplane correctly but leaves both wings of the deck carrying the same load. One mechanism, not two (the owner's consolidation rule). |
| **D-79.8** | **The closure reacts the roll over every mass**, as it does today: one rigid-body field on the assembled inertia tensor. No tail or fin air load is added for the roll. | 25.301(b); the owner's ruling on empennage aerodynamics. |
| **D-79.9** | **Both hands are released.** The assembled case is the `R` case (100 % on the starboard wing); `handed_twin` reflects it into the `L` case. Each gust sign therefore gives two full-airplane cases: `W-13R`, `W-13L`, `W-14R`, `W-14L`. | CONVENTIONS §7.1. The owner asked for one left and one right. On a symmetric airplane the pair mirror each other and both are still listed. |
| **D-79.10** | **Released and documented.** The slots pass note 77's guards; they appear in the case index, the wing CSVs, the deck and both reports. The report's rolling-conditions subsection (D-52.6) gains, per case: the rule, the percentage, the parent point, the averaged load factor, the unbalanced moment, the whole-airplane `θ̈`, and which wing carries 100 %. | A case that is run and not stated is the defect #437 named. |
| **D-79.12** | **The interface loads are stated per case and per hand**: left and right net wing-root shear, bending and torsion (LRA), their sum and difference, and the rolling moment into the body about the centreline. One owner computes them from the assembled balanced case; the report subsection and the case index read it. | The owner's purpose for the case (2026-11-26). The symmetric cases have these at zero difference, so the table is where the case's content is visible. See Q8. |
| **D-79.13** | **The report states both consequences of D-79.6** beside the accelerated roll: the 100 % side's wing loads rise, and the roll increment on masses mounted in the wing falls, against the manual's wing-only method. The deviation is entered in `02_approved_corrections.md` with the moved figures per fixture. | The manual names concentrated-weight attachments as what the case is critical for; a lower number there must not be silent. |
| **D-79.11** | **No power-on twin ids.** The pools of `UGSP` and `UGSN` hold the power-on `UG` labels too, and the pick states its power state. | The twin band `W-40`…`W-49` is full (note 77 Q1). See Q4. |

## 3. Gates

| Gate | Statement | Expected numbers |
|---|---|---|
| **G-79.0** | `reference/14CFR_25_301_loads.md` holds 25.301(b) verbatim. | Captured 2026-11-26 (`reference/` is local-only). |
| **G-79.1** | **Part 23, gust side unchanged.** `ga6_normal` and `baron_58`: no `UG` label, no `W-13`/`W-14`; V-n matrix and SELECT picks identical to the parent commit. | Byte-identical picks. |
| **G-79.2** | **Per-side factor.** In every assembled rolling case the port wing-air strip equals `p/100` of its starboard mirror in `fx`, `fz` and `my`, and no load has the source `aileron-roll`. | Exact; 0.80 gust, 0.75 accelerated roll. |
| **G-79.3** | **Rolling moment.** The wing-air strips' moment about the centreline equals `(1 − p/100)` × the starboard strips' `Σ y·fz` (±0.1 %), and agrees with the wing chain's `unbal_moment` to the root-station offset the test states. | `atr42_100`: ≈ 1.89 × 10⁶ and 0.72 × 10⁶ lb-in. |
| **G-79.4** | **One roll acceleration.** The wing chain's `θ̈` for a derived rolling case equals the balanced case's `p_dot` (±1 %). | `atr42_100`: 0.727, 0.747 and 2.097 rad/s². |
| **G-79.5** | **Lift equality.** For every `UG` point and every `AC ROLL` point, the balanced wing lift equals `(100 + p)/200` of its parent's (±0.01 %), and the assembled case's vertical and pitch residuals meet the existing 1 % gate before closure; `residual_mx` is reported, not gated. | `ga6_normal` `AC ROLL` nz ≈ 3.3185; `atr42_100` ≈ 2.1962 (linear estimate; exact values stated in the test). The moved V-n rows are entered in `02_approved_corrections.md`. |
| **G-79.6** | **Both hands.** For each of `UGSP`, `UGSN` and ACRL the balanced set holds exactly one `R` and one `L` case, and the `L` case is the reflection of the `R` case load for load. | Four gust-roll cases on `atr42_100`. |
| **G-79.7** | **End to end, `atr42_100` on the Part 25 basis.** Each slot is in `select_wing`, `wing_net`, the balanced set (both hands), the case index, the wing CSV, the deck and the report subsection. | 100 % side net root bending ≈ 4.39 × 10⁶ (positive) and −2.46 × 10⁶ lb-in (negative), ±2 % against the prototype. |
| **G-79.8** | **Accelerated roll, same airplane motion.** After D-79.7 the ACRL balanced case's `p_dot` is within 1 % of its value at the parent commit on every fixture, and its port wing now carries 75 % of the starboard air load. | `atr42_100` 2.097 rad/s². Deck digests move; recorded per fixture. |
| **G-79.9** | **Appendix A holds.** The test-built case 160 (D-52.12) reproduces p. 219 bit for bit. | `UNB −149,043`, `θ̈ −13.287`. |
| **G-79.11** | **Interface loads.** For each gust-roll case and hand, the stated left and right root loads sum to the body's reaction (`ΣFz` of everything not on the wing, ±0.1 %), their rolling moment about the centreline equals the body's roll inertia reaction (±0.1 %), and the `L` case's table is the `R` case's with the sides exchanged. The gate also reports the rolling moment into the body for every `UG` point of each sign and names any that exceeds the delivered pick's (Q3). | `atr42_100`: rolling moment into the body ≈ 0.21 × 10⁶ and 0.11 × 10⁶ lb-in; shear sum 0.90 of the symmetric gust (prototype, ±5 %; exact values stated in the test). |
| **G-79.10** | Note 77's class guards pass with the labels and slots added (G-77.3 to G-77.5). | — |

## 4. Questions

| # | Question | Recommendation |
|---|---|---|
| **Q1** — ruled **whole airplane** | Whose roll inertia relieves the wing-chain case? | Ruled: the roll acceleration is the whole airplane's; the wing's masses, fuel and nacelles included, react it (D-79.6). |
| **Q2** — ruled **yes** | Does the accelerated roll move to the per-side distribution? | Ruled: yes; the lumped couple is retired (D-79.7). |
| **Q3** — ruled **one per sign, with the report** (2026-11-26) | **Which gust points?** | Ruled: the largest wing lift of each sign over the whole matrix (D-79.4). The interface moment scales with the air root bending, but the body's share varies with the loading (11 % at forward gross, 15 % at minimum weight), so G-79.11 also reports the rolling moment into the body for every gust point and names any that exceeds the pick's. |
| **Q4** — ruled **fold in** (2026-11-26) | **Power-on:** fold into the two slots, or deliver nothing power-on? | Ruled: each slot searches both power states and delivers the point with the largest wing lift, stating its power state (D-79.11). The owner reads the rule's "wing maximum airload" as wing lift. |
| **Q5** — ruled **yes** (2026-11-26) | **Does D-79.6 reach the Part 23 accelerated roll in the wing chain?** | Ruled: yes, for derived cases on every basis, as step 1 (#440). The oracle models one wing and leaves the case to the user, so the same logic as the Part 25 case applies. An entered `unbal_moment` keeps WINGINER's wing-only reaction, so the test-built case 160 stays the oracle (G-79.9). D-79.13 states the consequences. |
| **Q6** — ruled **solve for lift, both cases** (2026-11-26) | **How is the averaged load factor set?** | Ruled: the companion's load factor is solved so its wing lift equals `(100 + p)/200` of the parent's, for the gust-roll points and for `AC ROLL` alike (D-79.3). No fall-back rule. |
| **Q8** — ruled **yes** (2026-11-26) | **Is the interface table (D-79.12) also printed for the accelerated roll**, with a symmetric reference? | Ruled: yes for the accelerated roll (step 1); one symmetric reference row beside each rolling case (condition A, or the parent gust). A full interface envelope over every case is not opened here. |
| **Q7** — ruled **no** (2026-11-26) | **The 100/80 gust on a Part 23 basis?** | Ruled: not needed. 23.349(a)(2) covers the unsymmetrical wing load on that basis: "For normal, utility, and commuter categories, in Condition A, assume that 100 percent of the semispan wing airload acts on one side of the airplane and 75 percent of this load acts on the other side" (as supplied by the owner). D-79.7 gives that case its per-side form. |
