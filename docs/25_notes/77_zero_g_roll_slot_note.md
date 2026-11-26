# The 25.349(a) zero-g rolling condition: its own wing slot, released through SELECT (design note 77; #437)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-11-25 — no code.** The owner ruled in session, under the solo profile
(rule 1's working-alone branch): every recommendation in §4 is agreed as written. PROPOSED
the same day, drafted from #437 and its SELECT comment. Built after #410 (Q4).

**Scope.** 14 CFR 25.349(a) asks for the rolling manoeuvre "in combination with an airplane
load factor of zero and of two-thirds of the positive maneuvering factor used in design".
sloads balances, selects and releases only the two-thirds state (`ST ROL A/C/D` → TORS),
which is all 23.349(b) names. This note adds the zero-g state on the Part 25 basis: three
balanced points per CG and altitude, one new wing slot, and the guards that stop a condition
being run and then dropped before the released wing cases.

Out of scope:
- the Part 25 basis switch itself (#410 owns it; this note reads it);
- the roll-acceleration condition of 25.349(a)(1) for outboard masses (Q5, #412);
- the up-going aileron side (Q3, #438);
- 25.349(b), the 100/80 unsymmetrical gust (#412);
- 25.301(b) aileron deflection with wing torsional flexibility (rigid basis,
  `theory_sources.md` §Base-method uncertainty);
- any change to the Part 23 matrix, the six `SELECT.BAS` picks or an Appendix A oracle.

Conventions: [`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §1 (wing torsion is `Myy`
about the LRA, named as % chord; envelopes two-sided; a cumulative torsion is not a free
moment), §1.1 (aileron sense stated per side, never a global sign), §3 (every load LIMIT,
the factor stated and applied nowhere), §4 (fixed case ids, bands). Negative `Myy` is
nose-down.

**Sources** (in `theory_sources.md` at closure):
- 14 CFR 25.349(a), (a)(1)–(4), as amended through Amdt. 25-94. Read 2026-11-25 from Cornell
  LII; the verbatim text is captured to `reference/` as G-77.0 before any code.
- Reference 1 Ch 9 p. 68 "Steady Roll" (the torsion search) and Ch 12 p. 93 (`Δcm = −0.01·δ`).
- Note 52 D-52.5 (the TORS `Δcm` increment), note 62 (slots above `SELECT.BAS`), note 63
  D-63.7 (net-governing re-pointing).

## 1. Measured (prototype, 2026-11-25; not in the tree)

Net (air + inertia) wing torsion about the LRA at 40 % chord, LIMIT, lb-in, down-aileron
wing. `Δcm` is applied over the drawn aileron span. The zero-g points are balanced with
`flight_envelope._balance`. "Symmetric minimum" is the most negative torsion over every
flaps-up power-off V-n point of the same CG and altitude, uniform `cm`.

**`atr42_100`**, aft gross 36,817 lb, 12,000 ft, aileron BL 355–470, VA/VC/VD 160.4/240/300 kt:

| Condition | δ down | BL 12 | BL 157 | BL 278 | BL 375 | BL 423 |
|---|---|---|---|---|---|---|
| two-thirds n₁, VC (today's TORS) | 10.03° | −50,540 | −153,907 | −26,989 | −46,717 | −20,867 |
| two-thirds n₁, VD | 4.01° | −104,998 | −180,063 | −37,046 | −40,558 | −20,210 |
| zero g, VA | 15.00° | −111,631 | −86,571 | −70,242 | −56,502 | −27,440 |
| zero g, VC | 10.03° | −217,280 | −162,312 | −125,215 | **−94,819** | **−46,967** |
| zero g, VD (CAM schedule) | 4.01° | **−280,942** | **−194,578** | **−136,770** | −89,127 | −46,498 |
| zero g, VD (one-third roll rate) | 2.67° | −267,793 | −181,429 | −123,621 | −75,978 | −40,506 |
| symmetric minimum | — | −275,575 | −156,190 | −123,561 | −61,128 | −34,012 |
| zero-g roll ÷ symmetric minimum | — | 1.02 | 1.25 | 1.11 | **1.55** | 1.38 |

- The zero-g roll exceeds the symmetric envelope by 11–55 % from BL 157 to BL 423. That is
  above the 5–10 % base-method band, so the item **ranks** (rule 6).
- It is 2 % over at the root, inside the band.
- It is 1.1 to 3.7 times today's TORS at every station shown.

**`ga6_normal`** (Part 23; shown only as the oracle fixture), CG1 3,400 lb, 12,000 ft, BL 109–190:
the zero-g roll is 0.65–0.88 of the symmetric minimum (`GUST -C`) inboard of the aileron
and 1.17–1.24 of it across the aileron span. It does not move under this note (D-77.1).

## 2. Decisions

| # | Decision | Rationale |
|---|---|---|
| **D-77.1** | **Part 25 basis only.** `flight_envelope._config_points` adds the zero-g points only when #410's basis switch says Part 25. On a Part 23 basis no label, case number, pick or id changes. | 23.349(b) names two-thirds alone. The Appendix A V-n matrix is numbered by position, so an unconditional add would renumber it. |
| **D-77.2** | **Three labels: `ST RL0 A`, `ST RL0 C`, `ST RL0 D`**, balanced at `n = 0` at VA, VC and VD with the same Mach caps as their `ST ROL` twins. They are appended after the existing points of each configuration. | 25.349(a): zero load factor at each of the three speeds. Appending keeps existing case numbers on a Part 25 project as stable as the basis switch allows. |
| **D-77.3** | **One new wing slot, `ZROL`, id `W-11`**, with its own pool `_ZROLL`. The zero-g labels are **not** added to `_STROLL`. | The TORS proxy has no load-factor term, so a zero-g point ties its two-thirds twin and the first found wins (#437 comment). §1 shows the two differ by up to 3.7 times. |
| **D-77.4** | **The slot's criterion is the TORS proxy**, `(cm − 0.01·δ)·G·V²`, most negative, searched over `_ZROLL` only. | Within the pool every point is at zero g, so the proxy's blindness to lift costs nothing. On `atr42_100` it picks VC (−7,790 against −6,760 at VD, `cm` −0.035), the condition that governs the aileron span in §1. |
| **D-77.5** | **`ZROL` is an air-pick slot and a steady-roll slot, with no power-on twin (Q1)**: a row in `select.AIR_PICK_SLOTS` and in `rolling.STEADY_ROLL_SLOTS`; `SLOT_LIFT_SIGN` carries no sign test for it. | Its criterion is torsion, so D-63.7's net-bending pass must not re-point it. Without the steady-roll row the wing chain builds it with uniform `cm`. At zero g the wing lift is near zero and of either sign, so a lift-sign test would empty the slot at random. |
| **D-77.6** | **The aileron span is derived from the drawn aileron surface when `aileron_loads.inboard_y_in/outboard_y_in` are blank, on the Part 25 basis.** Entered values win. On a Part 23 basis blank still means no increment. | Both ATR fixtures leave them blank, so their delivered TORS carries no `Δcm` today and `ZROL` would be a symmetric zero-g case. D-52.5's blank-reduces-to-oracle rule stays for `ga6_normal`. |
| **D-77.7** | **The deflection at VD follows 25.349(a)(4) on the Part 25 basis**: `δ_D = δ_A·VA/(3·VD)`. VC keeps `δ_A·VA/VC`. `rolling.steady_roll_schedule` takes the basis; TORS and `ZROL` read the same schedule. | (a)(3) asks for the VA roll rate at VC and (a)(4) for one third of it at VD. With steady roll rate proportional to `δ·V` (the relation CAM 3.222's own schedule uses), that is one third where CAM gives one half. §1: −5 % at the root. See Q2. |
| **D-77.8** | **An entered `wing_mass.cases` list that omits a slot SELECT delivered is stated in band**: `resolve_wing_cases` returns the omitted slot names and the wing page, case index and reports print them. No fixture list is edited. | This is the stage that drops a case without a message (#437 stage 5). The list is a deliberate filter on `ga6_normal`, so it is stated, not removed. |
| **D-77.9** | **`ZROL` enters the deliverables as TORS does**: case index, both reports, the wing CSVs, and the balanced deck as the symmetric trim case with no antisymmetric increment. | Note 52 D-52.5 and note 66 already rule this for TORS. A rolling deck case is its own item. |
| **D-77.10** | **Only the down-going aileron side is delivered.** | Same as TORS today. The up side is #438 (Q3). |

## 3. Gates

| Gate | Statement | Expected numbers |
|---|---|---|
| **G-77.0** | `reference/14CFR_25_349_rolling_conditions.md` holds 25.349 verbatim with its amendment history, and the test cites it. | Present before the first code commit. |
| **G-77.1** | **Part 23 unchanged.** `ga6_normal` and `baron_58`: V-n matrix, picks, case ids and digests are identical to the parent commit; every Appendix A oracle is green; no `ST RL0` label and no `W-11` appear. | Byte-identical. |
| **G-77.2** | **Balance.** Every `ST RL0` point closes: `nz` = 0 ± 0.01, and wing lift plus tail load equals `nz·W` to the FLTLOADS balance tolerance. | `atr42_100` aft gross, 12,000 ft: wing CL 0.004–0.007. |
| **G-77.3** | **Label reach (class guard).** Every label `_config_points` can emit is in a SELECT wing pool or on one stated not-searched list, on every basis. | Fails today if a label is added to FLTLOADS alone. |
| **G-77.4** | **Slot tables (class guard).** Every key of `WING_SLOTS` is classified in `SLOT_LIFT_SIGN`; every slot whose pool holds a steady-roll label is in `STEADY_ROLL_SLOTS`; every id `wing_case_id` can mint lies inside its band. | Fails today for a slot 11 power twin (`W-50`, the AILERON band): see Q1. |
| **G-77.5** | **Release (class guard).** On every shipped fixture, every slot `select_wing` delivers is in `build_net_loads().wing_net` or named in the stated omission list of D-77.8. | `ga6_normal`: seven slots named as omitted. ATR fixtures: none. |
| **G-77.6** | **End to end, `atr42_100` on the Part 25 basis.** The `ZROL` pick is an `ST RL0` point; `W-11` is in `select_wing`, in `wing_net` with the increment applied, in the case index, the wing CSV and the deck. | Pick `ST RL0 C`. Net LRA torsion at BL 375 ≈ −94,800 lb-in and at BL 12 ≈ −217,300 lb-in (§1, ±2 % against the prototype; exact values stated in the test). |
| **G-77.7** | **Physics closure.** For the `ZROL` case: root net shear and bending equal the balanced point's wing lift and its moment (±0.1 %); root torsion equals the uniform-`cm` torsion plus `−0.01·δ·q·∫c²dy` over the aileron span (±0.1 %). | The integral computed independently in the test, as G-52.7 does. |
| **G-77.8** | **Ranking holds.** On `atr42_100`, `ZROL` exceeds the two-sided envelope of the other released wing cases at one station or more. | ≥ 1.10 at BL 375 (§1: 1.55 against the symmetric points). |

## 4. Questions

| # | Question | Recommendation |
|---|---|---|
| **Q1** — ruled **no twin** | **The power-on twin has no id.** `wing_case_id` puts slot 11's twin at `W-50`, which is AILERON's down case. The power band `W-40`…`W-49` is full with ten slots. | **No power-on twin for `ZROL`**, stated in band, with G-77.4 refusing any id outside its band. Thrust enters a zero-g balance through the tail load only. Widening the band moves `W-50` and every persisted aileron id. |
| **Q2** — ruled **both** | **Does TORS also move to the one-third schedule at VD on the Part 25 basis** (D-77.7), or does only `ZROL` use it? | **Both.** One schedule per basis; two schedules for one manoeuvre is the duplication rule 3 forbids. It changes the ATR TORS `Δcm` at VD only (TORS picks VC on `atr42_100`). |
| **Q3** — ruled **own issue, #438** | **The up-going aileron side.** On the LRA the nose-up extreme is the two-thirds roll at VA with the up aileron (`ga6_normal`: +24,090 against +15,920 with uniform `cm`). Neither slot delivers it. | **Its own issue**, filed at agreement as #438. It doubles the roll cases and needs the up-side deflection ratio per basis. Measured for #438 on `atr42_100`: 1.11–2.48 times the symmetric nose-up envelope, so it ranks. |
| **Q4** — ruled **wait** | **Does this wait for #410's basis switch, or key on `category` meanwhile?** No Part 25 switch exists in the schema today; both ATR fixtures carry category `C`. | **Wait for #410.** A temporary key would be a second owner of the basis. The note can be agreed now and built after. |
| **Q5** — ruled **#412** | **25.349(a)(1) roll acceleration** for airplanes with engines outboard of the fuselage. The ATR is one; the 100/75 `ACRL` rule is Part 23's. | **Ranked under #412**, not here. It needs a roll inertia and an unbalanced-moment reaction, which is a different mechanism from a torsion slot. |
| **Q6** — ruled **accept** | **§1's symmetric minimum is one CG and altitude block**, with that block's mass state. A heavier or forward block could raise the envelope and lower the 1.55. | **Accept for agreement; G-77.8 measures the real envelope** over the released cases. If it falls below 1.10 the item is parked with that number. |
