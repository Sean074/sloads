# Steady roll, up-going aileron side: the nose-up wing torsion slot (design note 78; #438)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-11-25 — no code.** The owner ruled in session, under the solo profile
(rule 1's working-alone branch): every recommendation in §4 is agreed as written. PROPOSED
the same day, split out of note 77 by its Q3 ruling. Built after #437 (Q4).

**Scope.** In a steady roll one aileron is down and the other is up. sloads delivers the
down side only (TORS, and `ZROL` under note 77), which sets the nose-down torsion. The
up-going aileron adds a nose-up section moment to the nose-up torsion that positive lift
ahead of the LRA already gives, and no slot delivers that. This note adds one wing slot for
it, at two-thirds n₁, with the pass-through guards of note 77.

Out of scope:
- the zero-g state with the up aileron (§1: smaller than the two-thirds state at every
  station, so it is not searched);
- the rolling-moment balance and the lift the two sides trade in a roll (the manual's
  method keeps the symmetric lift distribution, Ch 12 p. 93; so does this note);
- the Part 23 basis (Q1);
- 25.349(a)(1) roll acceleration (#412) and 25.349(b) (#439);
- any change to the six `SELECT.BAS` picks or an Appendix A oracle.

Conventions: [`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §1 (wing torsion is `Myy`
about the LRA, named as % chord; envelopes two-sided), §1.1 (aileron sense stated per side,
"TE-up", never a global `δa` sign), §3 (every load LIMIT, the factor stated and applied
nowhere), §4 (fixed case ids, bands). Positive `Myy` is nose-up.

**Sources** (in `theory_sources.md` at closure):
- 14 CFR 25.349(a) and (a)(2)–(4): the rolling manoeuvre and its aileron deflections
  (`reference/14CFR_25_349_rolling_conditions.md`, note 77 G-77.0).
- Reference 1 Ch 12 p. 92: 23.349(b) as quoted, `Δcm = −0.01·δ` where "δ is the down aileron
  deflection in degrees"; p. 93, the increment added to the basic airfoil `cm` over the
  aileron span on the symmetric two-thirds lift distribution.
- Reference 1 Appendix A p. 200: the entered up travel (`AUPDEG`, −10.0° on GA6).
- Note 52 D-52.5, note 77 (D-77.5 to D-77.8, G-77.3 to G-77.5).

## 1. Measured (prototype, 2026-11-25; not in the tree)

Net (air + inertia) wing torsion about the LRA at 40 % chord, LIMIT, lb-in, positive
nose-up, up-aileron wing. `Δcm = +0.01·δ_up` over the drawn aileron span, CAM schedule
scaled to the entered up travel. "Delivered maximum" is the most nose-up torsion over the
wing cases the fixture releases today.

**`atr42_100`**, aft gross 36,817 lb, 12,000 ft, aileron BL 355–470, full up 20°:

| Condition | δ up | BL 12 | BL 109 | BL 206 | BL 278 | BL 326 | BL 375 | BL 423 |
|---|---|---|---|---|---|---|---|---|
| two-thirds n₁, VA | 20.00° | +125,463 | +41,688 | +84,430 | +124,233 | +106,824 | +89,988 | +43,761 |
| two-thirds n₁, VC | 13.37° | +96,727 | +27,588 | +82,369 | +120,277 | **+110,155** | **+100,550** | **+46,245** |
| two-thirds n₁, VD | 5.35° | −12,956 | −64,412 | +8,882 | +54,996 | +53,219 | +51,484 | +21,734 |
| zero g, VC | 13.37° | −70,013 | −35,110 | +1,652 | +22,052 | +37,818 | +52,447 | +20,144 |
| delivered maximum | — | +139,999 | +34,592 | +165,548 | +121,252 | +91,203 | +61,713 | +33,900 |
| delivered by | — | PHAA-P | PHAA | ACRL-P | ACRL-P | ACRL-P | ACRL-P | ACRL-P |
| up roll ÷ delivered maximum | — | 0.90 | 1.21 | 0.51 | 1.02 | 1.21 | **1.63** | 1.36 |

- From BL 326 outboard the up-aileron roll is 21–63 % above everything delivered today.
  That is above the 5–10 % base-method band, so the item **ranks** (rule 6).
- Inboard of BL 278 the delivered PHAA and ACRL cases already cover it, except a 21 %
  excess at BL 109 where both values are small.
- VC governs the aileron span and VA the inboard wing. The slot is for the aileron span.

**`ga6_normal`**, CG1 3,400 lb, 12,000 ft, BL 109–190, full up 10°: the up roll is 0.79–0.87
of the delivered maximum (ACRL) inboard and 0.87–1.02 across the aileron span. It does not
rank on this airplane.

**Note 77 cross-check, same method:** the zero-g down-aileron roll on `atr42_100` is 1.51
times the delivered minimum at BL 375 (−94,819 against −62,862, NLAA) and 1.17 at BL 157.
G-77.8's 1.10 floor holds against the delivered envelope, not only the one-block one.

## 2. Decisions

| # | Decision | Rationale |
|---|---|---|
| **D-78.1** | **One new wing slot, `TORU`, id `W-12`**, searched over the existing `ST ROL A/C/D` points. No new FLTLOADS label and no new balanced point. | The airplane state is the one TORS already uses (two-thirds n₁ at VA, VC, VD); only the side of the airplane differs. So nothing is "run" that could be dropped upstream of SELECT. |
| **D-78.2** | **Part 25 basis only** (Q1), read from #410's switch as note 77 does. | §1: it ranks on the ATR and not on GA6. 23.349(b) as quoted names the down aileron alone, so on Part 23 the case is beyond the rule's own simplified method. |
| **D-78.3** | **The section increment is `Δcm = +0.01·δ_up`**, `δ_up` the up deflection in degrees as a magnitude, over the same aileron span. `rolling.aileron_cm_increment` takes the signed deflection it already takes (TE-up negative), so one owner serves both sides. | The rule's increment is linear in deflection; this extends the same slope through zero to the up side. It is an **extension of the quoted rule, stated as such** in `theory_sources.md` (Q2). |
| **D-78.4** | **The up deflection schedule is the basis's steady-roll schedule scaled by the travel ratio**: `δ_up(V) = δ_down(V) · up_deflection_deg / full_down`. On the Part 25 basis that is full up at VA, `VA/VC` at VC and `VA/(3·VD)` at VD (D-77.7). | 25.349(a)(2)–(4) set the control deflection, and both ailerons move with it. `aileron_loads.up_deflection_deg` is the entered up travel (`AUPDEG`). |
| **D-78.5** | **Criterion: the most positive proxy** `(cm + 0.01·δ_up)·G·V²` over the pool. **Ties are broken by the largest wing lift `LZW`**, within `LZW_TIE_REL` of the best proxy. | Mirror of TORS (most negative). The proxy has no CG or load-factor term, so every CG at one speed and altitude ties; nose-up torsion on the LRA grows with lift, so the heaviest-lift point is the governing one. First-found is the defect #437 named. |
| **D-78.6** | **`TORU` is an air-pick slot and a steady-roll slot, with no power-on twin.** Rows in `AIR_PICK_SLOTS` and `STEADY_ROLL_SLOTS`; `SLOT_LIFT_SIGN` requires positive lift. `STEADY_ROLL_SLOTS` becomes a map from slot to aileron side, so the wing chain applies the right sign. | As D-77.5 and note 77 Q1 (the twin band `W-40`…`W-49` is full; slot 12's twin would be `W-51`, AILERON's up case). A tuple of names cannot say which side a slot is. |
| **D-78.7** | **A blank or zero `up_deflection_deg` leaves the slot empty**, stated in band as a slot with no eligible candidate. | No up travel entered means no up-aileron case can be built; a silent fall-back to the down travel would invent a number. |
| **D-78.8** | **Deliverables as TORS and `ZROL`**: case index, both reports, wing CSVs, and the balanced deck as the symmetric trim case with no antisymmetric increment. | Note 52 D-52.5 and D-77.9. |
| **D-78.9** | **The aileron span and the stated-omission list are note 77's** (D-77.6, D-77.8); this note adds no second owner. | One owner per convention (rule 3). |

## 3. Gates

| Gate | Statement | Expected numbers |
|---|---|---|
| **G-78.1** | **Part 23 unchanged.** `ga6_normal` and `baron_58`: picks, case ids and digests identical to the parent commit; every Appendix A oracle green; no `W-12`. | Byte-identical. |
| **G-78.2** | **Note 77's class guards pass with the slot added**: G-77.3 (labels), G-77.4 (slot tables and id bands), G-77.5 (release or stated omission). | `wing_case_id("TORU-P")` is refused. |
| **G-78.3** | **Selection, `atr42_100` on the Part 25 basis.** `TORU` picks an `ST ROL C` point; among the points tied on the proxy it is the one with the largest `LZW`. | Proxy at VC 5,690 against 4,250 at VA (`cm` −0.035, before `G`). |
| **G-78.4** | **End to end.** `W-12` is in `select_wing`, in `wing_net` with the up increment applied, in the case index, the wing CSV and the deck. | Net LRA torsion at BL 375 ≈ +100,500 lb-in for the aft-gross block of §1 (±2 % against the prototype; the picked block's exact value stated in the test). |
| **G-78.5** | **Physics closure.** For the `TORU` case: root net shear and bending equal those of the same point built with uniform `cm` (±0.1 %); root torsion equals the uniform-`cm` torsion plus `+0.01·δ_up·q·∫c²dy` over the aileron span (±0.1 %). | The integral computed independently in the test, as G-52.7 does. |
| **G-78.6** | **Sign symmetry.** `aileron_cm_increment` with `+δ` and `−δ` gives increments equal and opposite at every station. | Exact. |
| **G-78.7** | **Ranking holds.** On `atr42_100`, `TORU` exceeds the nose-up side of the envelope of every other released wing case at one station or more. | ≥ 1.10 at BL 375 (§1: 1.63). |
| **G-78.8** | **Empty slot.** A Part 25 project with `up_deflection_deg` blank delivers no `W-12` and states the empty slot. | In-memory `atr42_100` with the field cleared. |

## 4. Questions

| # | Question | Recommendation |
|---|---|---|
| **Q1** — ruled **Part 25 only** | **Part 25 basis only, or both bases?** On Part 23 it would add a case Appendix A does not print. | **Part 25 only.** GA6 measures 0.79–1.02 of the delivered envelope, inside the band; Part 23 is parked with that number. `baron_58` is not measured; if it ranks there, that is a new issue. |
| **Q2** — ruled **yes, as an extension** | **Is `+0.01` per degree acceptable for the up side?** The rule quotes the slope for the down aileron only; no source in the tree gives an up-side value. | **Yes, stated as an extension.** A plain-flap section moment is close to linear through zero deflection. An entered override is not added until a fixture has a sourced value. |
| **Q3** — ruled **`TORU` only** | **Tie-break on wing lift (D-78.5): apply it to TORS and `ZROL` too?** They have the same first-found tie across CGs. For TORS on GA6 it could move the Appendix A pick (case 138, CG1). | **`TORU` only here.** For the down side, lift relieves the nose-down torsion on the LRA, so the tie-break would be least lift, and it touches an oracle-locked pick. Filed as a finding on #437 for note 77's build to rule. |
| **Q4** — ruled **after #437** | **Does `TORU` wait for #437?** It reuses the basis switch, the schedule owner, the derived aileron span and the three class guards. | **Yes, built after #437**, as the backlog row states. |
| **Q5** — ruled **no second slot** | **Is the excess at BL 109 (1.21, on +41,688 against +34,592) a second governing region the VC pick misses?** VA governs there. | **No second slot.** The values are a quarter of the adjacent stations'; the envelope there is set by sign changes between PHAA and ACRL. G-78.7 reports the ratio at every station so a later fixture can reopen it. |
