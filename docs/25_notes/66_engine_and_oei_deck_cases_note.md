# The deck carries the engine: mount cases and the one-engine-out fin (design note 66)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-25 (owner, in session) — no code.** PROPOSED the same
day; the owner ruled Q1–Q7 of §2 **as recommended**, so D-66.1…D-66.16 stand as
written (§9). Drafted for one design pass over two band-B8 rows the 2026-09-22
re-charter paired ("#286 and #285 move B2 → B8 (one design pass)"): **#286**,
no engine-mount case reaches the LRA deck, and **#285**, the one-engine-out fin
conditions reach no shipped deck. Implementation: #286 first, then #285, each
a tier-L step on `dev/v0.8.7`.

**Tier L, twice** (#286 and #285 ship as two steps against this note): new
balanced-case families in the one shipped solver deck, new applied-load
producers, a new deck statement, no new physics. **No schema change is
proposed** (every input the two families need is already entered), so #276's
rename does not ride this note — see §6.

**Conventions:** `CONVENTIONS.md` §3 (every delivered load LIMIT, SF stated per
case and applied nowhere — the `ULT SF=1.0` cases state 1.0), §4 (case
identity: one id per physical condition; minted twins vs a twin with its own
id), §7 (single owners; this note adds rows for the engine increment, the OEI
parent point and the balanced-case SF stamp), §7.1 (handedness). **Theory:**
`ch07_engine_loads.md` (23.361/23.363/23.371), `ch05_empennage_loads.md`
§"One engine out (23.367)", `ch09_balanced_airplane.md` §7 and §11.
**Precedent:** note 21 §2.2 / §4 (the power-effects "Kind I" cases — agreed
2026-08-15 and parked; **this note discharges its Kind I half**), note 24 R-9
and note 27 LM-5 (the engine mount/hub nodes and their one RBE2), note 53
(the thrust line, `prop_direction`), note 56 D-56.2/D-56.8 (the per-component
decks deleted; the LRA deck is the one solver deck), plan 13 (file
`18_b8a_lateral_closure_plan.md`) §4 and §7 G1, note 33 (L-7), the ground
families (G-1: appended families, `_GroundCondition` as a non-SELECT source,
`LG-19`/`LG-20` as a twin with its own id), #284 (the deck states its
absences), #210 (every EM condition states its own point).

## 1. Measurements (2026-09-25, at `dev/v0.8.7` after #306)

### 1.1 The engine (#286)

- **ENGLOADS produces** (`modules/engine.py` `run_all`, line 811), per engine:
  23.361(a)(1) and (a)(2) and 23.363 always; on a turboprop also 23.361(a)(3),
  23.361(b)(1) and 23.371(b) (four gyro sign sub-cases); with `include_far25`,
  25.361(a)(3)(i)/(ii) and 25.371. Ids are `EM-nn` from one allocator across
  the installation: ga6 EM-01..03; baron EM-01..06 (3 per side); atr
  EM-01..12 (6 per side, EM-06/EM-12 gyro); RJ EM-01..18. `concept_heavy`
  has no engine.
- **Every EM condition is LIMIT, SF 1.5** (`safety_factors._RANGES` 23.321–23.371
  → family `flight`); none is ultimate.
- **The loads are stated at the combined engine+prop CG** (`_applied_at`,
  #210). `coordinates.engine_applied_load` (coordinates.py:434) turns the
  scalars into airplane-axis force and moment about the thrust line
  (`engine_thrust_axis`: the entered line, else `(-1,0,0)` flagged ASSUMED;
  every fixture is on the assumed axis). **Its only callers are report §10.**
  `engine_applied_loads.csv` uses a different sense by declaration
  (`CONVENTIONS.md`, note 44 OR-160); the deck must use the airplane-axis one.
- **The LRA deck has the nodes and no loads.** One `lra-engine-mount` node at
  `engine_cg` and one `lra-engine-hub` at `prop_cg` per engine (dropped when
  they coincide, as on the RJ), both dependents of one RBE2 to the wing chain
  or a body tie (note 27 LM-5). `_member_key` sends every `engine-*` load to
  one shared `engine` member and the nearest node of it — on a close pair,
  possibly the other engine's.
- **The engine's mass is already in every balanced case, off the engine
  nodes.** WING/POINT item rows (baron, atr) ride the wing chain as
  `wing-inertia`; FUSELAGE rows (ga6, RJ) ride the body as `body-inertia`.
  **Adding ENGLOADS's vertical `n·W` at the mount on top of a flight parent
  would count the engine's inertia twice.**
- **The concurrent flight load exists nowhere as a balanced state.** 23.361(a)(1)
  is torque "acting simultaneously with 75 percent of the limit loads from
  flight condition A", (a)(2) with 100 %, (a)(3) with "1 g level flight loads";
  23.363 "may be assumed to be independent of other flight conditions";
  23.371(b) is yaw 2.5 rad/s, pitch 1 rad/s, n = 2.5 and max-continuous thrust.
  ENGLOADS applies `n` to the engine+prop weight only.
- **Two defects found on the way** (fixed in this note's step, §3):
  `render._gyro_subcases` reads `fz_vertical_2_5g` only, so 25.371's
  `vertical_limit_load_a2_load` is dropped (RJ EM-09a..d print fz 0 against
  EM-06a..d's 3875); and `case_ids.subcase_id` raises on `EM-06a`, so the
  gyro sub-cases cannot be numbered as solver subcases today.
- **The deck says nothing about engines.** `skipped_block` states the SELECT
  and LANDLOAD absences (#284); no engine condition is named carried or not.

### 1.2 The one-engine-out fin (#285)

- **ONENGOUT** (`modules/one_engine_out.py`) is a single-DOF yaw time-march
  (ONENGOUT.BAS 203-410). Per failed engine (every engine off the centreline,
  OR-173) and per speed it emits a fin condition at the **peak total fin load**
  (OR-175): `VC (ultimate)` 23.367(a)(2) **SF 1.0**, `VD (limit)` 23.367(a)(1)
  SF 1.5, `VS` 23.367 SF 1.5; a case that does not recover in 60 s is
  dropped (OR-174). Ids VT-30…VT-49. `case=None`: no V-n point, "because it is
  a transient".
- **On the fixtures** (only the two twins carry `one_engine_out`):

  | | condition | LT (lb) | θ at peak | t peak | rudder |
  |---|---|---|---|---|---|
  | atr42_100 | VC (ult), eng 1 / 2 | ±11,455.6 | 9.07° | 2.30 s | 25° |
  | | VD (lim), eng 1 / 2 | ±15,993.0 | 7.22° | 2.30 s | 25° |
  | | VS | not recovered — absent | | | |
  | baron_58 | VC (ult) | ±1,491.8 | 3.83° | 2.20 s | 16.7° |
  | | VD (lim) | ±2,158.8 | 3.63° | 2.15 s | 12.5° |
  | | VS | ±676.5 | — | — | — |

  The ATR's VD case is **3.6×** its largest assembled fin case (YAW 15
  NEUTRAL, 4,461 lb); the Baron's 1.6× (1,357 lb). Four conditions on the ATR,
  six on the Baron.
- **The fin distribution is already built.** `build_tail_span` distributes
  every critical v-tail condition with `lt25/lt50`, the OEI rows included
  (atr: 10 strips, Σfy ±11,455.6 / ±15,993.0), and `_vtail_distributions`
  keys them by label. What stops them is the family gate
  (`BALANCED_VTAIL_CONDITIONS` omits them — "a transient, not a balanced
  steady case (plan 13 §4)") and then `no-vn-point` (`case=None`) and no CG
  case.
- **The fin is not the whole yaw balance at the instant.** ONENGOUT's own
  moment at the peak: atr VC net −2,475,389 lb-in = engine asymmetry (T+D)·y
  +2,402,979 − fin moment 4,878,368 (ψ̈ −52.6 deg/s²); the fin moment is about
  twice the engine moment, so the airplane is decelerating in yaw. A closure
  fed the fin alone would yaw at −fin/Izz, not −(fin − engine)/Izz.
- **A 1 g parent exists at every OEI speed.** FLTLOADS balances `BAL C` and
  `BAL D` at n = 1 at VC and VD, and `STALL 1G` at the 1 g stall speed, in
  every configuration/CG/altitude block (`flight_envelope._config_points`).
  ONENGOUT flies at the shoulder altitude (12,000 ft on both twins); the ATR's
  matrix has 12,000 ft, the Baron's 0 and 10,000.
- **The mass state differs.** ONENGOUT reads Izz from WTONECG's heaviest
  `project.mass` case (atr 224,883 slug-ft², 43,308 lb; baron 7,335); the
  closure reacts on the assembled tensor of the case's loading (plan 13 §3.4's
  three-Izz identity).
- **L-7** (`lateral_aero_terms`) reads `cond.beta_deg` and the fin `Cy_β/Cn_β`
  SELECT publishes; ONENGOUT publishes `beta_deg = sense·θ` (the **yaw angle**)
  and no fin derivatives. L-7 is off by default and off on both twins.

### 1.3 Shared

- **No balanced case states its own safety factor.** `BalancedCaseResult.
  safety_factor` defaults to `ULTIMATE_FACTOR` and nothing in
  `modules/balance/` sets it; the deck header prints
  `basis_sentence(case.safety_factor)`. Every assembled case says "SF 1.5"
  today — right by coincidence for every family so far, wrong the moment a
  `ULT SF=1.0` case joins.
- **The round-trip CI already solves every engine fixture.**
  `test_the_lra_model_solves_and_reacts_only_the_residual` runs ga6, baron,
  atr and the RJ (Imperial and SI); new subcases are solve-gated on arrival.
  `test_every_assembled_case_reaches_the_beam_deck_carrying_its_lateral_load`
  hard-codes `len(lateral) == 8` on ga6/RJ.

## 2. Owner rulings (asked at PROPOSED; all ruled as recommended 2026-09-25 — §9)

| # | Question | Recommended | Why it is the owner's |
|---|---|---|---|
| Q1 | **Which engine conditions become balanced cases?** | 23.361(a)(1), (a)(2), (a)(3), 23.371(b) (and the FAR 25 (a)(3)(i)/(ii), 25.371 on a `include_far25` project) — the ones the regulation pairs with a flight state. 23.363 and 23.361(b)(1) stay **mount-local**, named in the deck as not assembled with the reason. | Note 21 kept (a)(3) mount-local on "no flight loads"; the text says "1 g level flight loads", so this reverses a parked ruling. |
| Q2 | **What is condition A's parent case?** | The delivered **PHAA** run (W-01, note 63's net-governing point) at its own CG and loading, scaled 0.75 for (a)(1). 23.371(b)'s n = 2.5 parent is the delivered **MAN A** point scaled 2.5/n₁ (note 21 P-7 asked "at VA"). | Condition A has one point per CG case; PHAA's governing run is the one the deck already carries, but a per-CG family is the alternative. |
| Q3 | **How is the propeller torque reacted?** | Note 21 P-9: an `aileron-trim` free couple +ΣQ at the wing a.c. — a steady torque is trimmed by aileron, the case stays unhanded, a counter-rotating pair nets zero. | P-9 was agreed while parked; confirm it holds. |
| Q4 | **What is the OEI case's symmetric half?** | 1 g level flight at the case's speed: `BAL C` for VC, `BAL D` for VD, `STALL 1G` for VS — at the **heaviest derivable FLIGHT CG case** (ONENGOUT's own mass basis) and the V-n altitude nearest ONENGOUT's (12,000 → 12,000 ft on the ATR, 10,000 ft on the Baron). | One CG case per condition vs every CG case (×4 cases on the ATR) is a coverage/volume trade. |
| Q5 | **Does the OEI applied set carry the engine pair?** | **Yes**: the live engine's thrust and the failed engine's windmill drag at their hubs, at ONENGOUT's own values at the peak instant, so the closure's yaw reproduces ONENGOUT's ψ̈ (§4 G-66.9) rather than a fin-only yaw twice as large. | Plan 13 §4's "transient" ruling is being narrowed to "its governing instant, quasi-static" — the owner's to confirm. |
| Q6 | **L-7 on an OEI case?** | **Not applied**, stated in band: ONENGOUT's θ is a yaw angle, not a sideslip (the flight path turns), no fin derivatives are published, and L-7.4's net-moment check is rudder-neutral only. | L-7.3 is the owner's opt-in switch; the question is whether the switch reaches this family. |
| Q7 | **Gyro sub-case numbering.** | Mint **four real EM ids** per gyro condition in ENGLOADS (`EM-06`…`EM-09` on the ATR's left engine, renumbering what follows), retiring the render-time `a/b/c/d` suffix. | It renumbers shipped EM ids on the turboprops (one digest wave); the alternative is a suffix→SID offset rule in `case_ids`. |

## 3. Decisions

### Shared

| # | Decision | Alternative rejected |
|---|---|---|
| D-66.1 | **Every balanced case stamps its own safety factor** from its source condition (SELECT's `CriticalCondition.safety_factor`, the ENGLOADS/ONENGOUT `ConditionResult`'s, LANDLOAD's for ground), through `assemble`/`assemble_ground` and onto the reflected twin. The deck header's `basis_sentence` then reads the case's own factor, so a 23.367(a)(2) subcase prints `ALREADY ULTIMATE (SF=1.0)`. A drift guard: every assembled case's SF equals `safety_factors`' answer for its FAR reference. | Stamping only the new families — the defect is general, latent because every family so far is 1.5 |
| D-66.2 | **Both families are appended after the ground families**, EM then OEI, so every shipped deck's existing subcase sequence is untouched (the ground precedent, G-1). | Interleaving by FAR paragraph — renumbers every shipped deck |
| D-66.3 | **The deck states every engine and OEI condition it does not assemble**, with the reason, in the #284 `CONDITIONS NOT ASSEMBLED` block: a `_EngineCondition` adapter (the `_GroundCondition` precedent) feeds ENGLOADS's mount-local conditions and ONENGOUT's unrecovered speeds into `skipped_block`. The `out-of-family` wording that says the OEI conditions reach "the report alone" is rewritten. | A header paragraph in prose — the record is structured and gated (`test_every_condition_is_either_assembled_or_recorded`) |

### The engine-mount family (#286)

| # | Decision | Alternative rejected |
|---|---|---|
| D-66.4 | **The EM case is a scaled parent plus the engine increment.** Parent (Q2): the delivered condition A run for 23.361(a)(1)/(a)(2), scaled by 0.75/1.00; its 1 g `BAL` point for (a)(3); MAN A scaled to n = 2.5 for 23.371(b). A balanced set scaled by a constant stays balanced, so the parent's air, inertia and closure scale together and the engine increment is the only new content. | Re-balancing FLTLOADS at a new load factor — a second producer of condition A |
| D-66.5 | **The engine increment is the mount module's own numbers, never the vertical.** Per engine: `mx_mount_torque` about the thrust axis, and on 23.371 the gyro `myy`/`mzz` and `fx_thrust` at the hub, all through `coordinates.engine_applied_load` (airplane axes, one owner, note 21 §2.3). **ENGLOADS's `fz_vertical` is not applied**: the engine mass is already in the scaled parent's inertia at the same `n` — a gate (G-66.3) asserts that inertia equals ENGLOADS's vertical to the pound, which is the independent-producer check the double count would otherwise hide. | Applying `fz_vertical` at the mount — double-counts the engine's inertia |
| D-66.6 | **The loads land on their own engine's nodes.** The couple and the torque go to the `lra-engine-mount` node, thrust to the `lra-engine-hub`, moved from the combined CG with the transfer couple (resultant preserved); `_member_key` gains a per-engine member (`engine-<i>`) so a load cannot land on the other engine's nearest node. | Nearest node of one shared `engine` member — resultant exact, per-engine RBE2 recovery wrong on a close pair |
| D-66.7 | **Torque reaction by P-9** (Q3): an `aileron-trim` free couple +ΣQ at the wing a.c.; the gyro couples by the closure's q̇/ṙ with the My/Mz residual gate exempted for 23.371 (note 21 §4). **Engine loads are applied per engine, never mirrored**: `reflect_load` gains the rotation-fixed exclusion note 21 §4.4 requires (`engine-torque`, `engine-gyro`), so a twin of any case never reverses a propeller. | Closure ṗ for the torque — mints a spurious port twin (note 21) |
| D-66.8 | **Ids and subcases.** An EM case keeps ENGLOADS's `EM-nn` (one id per physical condition); per Q7 the gyro sub-cases become four real ids; `balanced_subcase_id` then maps them (EM-01 → 5501). The `_gyro_subcases` 25.371 vertical-key defect is fixed in the same step. | Deck-only ids — a second id for one condition |
| D-66.9 | **What the EM family states per case**: the parent run and its scale, the engine, the thrust axis (entered or ASSUMED), the propeller sense, and "the engine's inertia is the parent's, at the parent's n — the vertical is not re-applied". | — |

### The one-engine-out family (#285)

| # | Decision | Alternative rejected |
|---|---|---|
| D-66.10 | **The instant is ONENGOUT's own**: the peak total fin load (OR-175), the one SELECT already names. Plan 13 §4's ruling is narrowed, not reversed: the transient is not re-run in the balance; its governing instant is assembled quasi-statically, which is what every other fin condition already is. | Peak yaw rate, or the time history as several cases — a second criterion for one condition |
| D-66.11 | **The symmetric half is 1 g level flight at the case's speed** (Q4): `BAL C`/`BAL D`/`STALL 1G` at the heaviest derivable FLIGHT CG case, nearest altitude, stated. The fin distribution is `_vtail_distributions`' existing one; it replaces nothing (the trim tail load stays the parent's). | A synthetic 1 g state — FLTLOADS already balances one |
| D-66.12 | **The applied set carries the engine pair** (Q5): live-engine thrust `−T` and failed-engine windmill drag `+D` at their hubs, at ONENGOUT's values at the peak instant (its own thrust-decay and drag ramps). The yaw residual is then fin + engine, as ONENGOUT's moment is, and the closure's ṙ reproduces ψ̈ to plan 13's Izz identity (G-66.9). | The fin alone — ψ̈ about twice ONENGOUT's on the ATR |
| D-66.13 | **One computed case per speed, the other engine as its twin by reflection, under its own id** — engine 1's failure is computed (hand R), engine 2's is `handed_twin(case, case_ref=<engine 2's VT id>)` (the `LG-19`/`LG-20` precedent). Valid for a mirror-symmetric installation, which a gate asserts (engine 2's own march equals the reflection, G-66.10); an asymmetric installation computes each engine. | Computing both and minting twins of both — four cases for two conditions |
| D-66.14 | **`ULT SF=1.0` per subcase** on the 23.367(a)(2) cases through D-66.1; the VD/VS cases state 1.5. | — |
| D-66.15 | **L-7 is not applied** (Q6) and every OEI case carries the standing statement plus "the yaw angle of this transient is not a sideslip; the wing-body side force is not estimated for it". | Applying L-7 at β = θ — the wrong angle |
| D-66.16 | **Gates by family**: the symmetric half's residual gate applies (the 1 g parent closes as it does for the four static fin cases); the lateral residual is the fin + engine moment by construction and is reported, not gated. | — |

## 4. Gates

| Gate | Statement | Expected |
|---|---|---|
| G-66.1 | Every assembled case's SF equals `safety_factors`' answer for its FAR reference; the deck header states it | 1.5 on every existing case (no digest change from this alone); 1.0 on 23.367(a)(2) |
| G-66.2 | EM coverage: the deck carries exactly the Q1 set per engine per fixture, and the not-assembled block names the rest | ga6 2 + 1 named; baron 4 + 2; atr per Q1/Q7; RJ incl. FAR 25; `concept_heavy` none |
| G-66.3 | **No double count**: in an EM case, the engine items' inertia equals ENGLOADS's `fz_vertical` (0.75·n_A·W on (a)(1)) | identity, rel 1e-9 |
| G-66.4 | The applied engine increment equals `engine_applied_load` of the mount module's scalars, per engine, at its own mount/hub nodes | identity |
| G-66.5 | The EM case minus its engine increment equals the scaled parent, load for load | identity |
| G-66.6 | Round-trip CI: every new EM and OEI subcase solves free-free with reactions ≈ 0 (`test_the_lra_model_solves_and_reacts_only_the_residual`) | on ga6, baron, atr, RJ, both systems |
| G-66.7 | P-9: the torque couple nets the rolling moment to zero; a counter-rotating pair applies none; no EM case is handed by its torque | identity |
| G-66.8 | OEI coverage: atr 4 conditions → 2 computed + 2 twins; baron 6 → 3 + 3; SIDE GUST's existing skip unchanged | counts |
| G-66.9 | **The yaw identity**: each OEI case's closure ṙ equals ONENGOUT's ψ̈ at the peak after the plan 13 §3.4 Izz identity (assembled tensor vs WTONECG) | stated per fixture at implementation, beside ONENGOUT's −52.6 / −70.2 (atr) and −112.9 / −157.2 (baron) deg/s² |
| G-66.10 | The reflected twin equals engine 2's own ONENGOUT march (fin load, β, rudder) | rel 1e-9 on both twins |
| G-66.11 | The not-assembled block names the ATR's unrecovered VS | named |
| G-66.12 | The 25.371 vertical reaches the RJ's gyro cases | the FAR 25 gyro cases carry their own `vertical_limit_load_a2_load`, not 0 (today EM-09a..d print 0) |

## 5. Effect vs error bar (rule 6)

- **OEI is the largest fin load on both twins** — 3.6× the ATR's largest
  assembled fin case, 1.6× the Baron's — and today it reaches no solver deck.
  On a wing-mounted twin it sizes the fin and aft fuselage: first-order on
  the one deck that ships.
- **The engine cases** carry the mount's torque (737 ft-lb on the GA6 at
  23.361(a)(1), larger on the turboprops) and the gyro couples. Against the
  airplane they are small; against the nacelle, mount and attachment they are
  the design loads, and those items are sized from the deck.
- **D-66.1** moves no number today (every family is 1.5) and prevents a
  wrong one tomorrow.

## 6. What this supersedes / touches, and what it leaves

- **Note 21 §2.2 Kind I** — discharged by #286 (Q1 reverses its (a)(3)
  ruling if confirmed); its Kind II (the power-effects set: slipstream,
  P-factor, normal force) stays parked.
- **Plan 13 §4** — narrowed by D-66.10; `BALANCED_VTAIL_CONDITIONS`'s comment
  and `ch09` §11.2's stale "cannot execute on any fixture" caution are
  rewritten; `test_balance.py`'s "disjoint producers" comment likewise.
- **Report §11** already says every recovered case "is written into the
  exported deck" — true at #285's closure, false until then.
- **#276** (`engine_count`) said it rides the first schema hop this band
  forces; #306 forced v69 and this note forces none, so #276 takes its own
  hop.
- **#217/#226** (the thrust line into balance) stay where they are: D-66.5
  uses the thrust axis for the engine increment only.
- **Untouched:** ENGLOADS and ONENGOUT physics and their oracles; the four
  static fin conditions; the ground families.

## 7. Closure obligations (tier L, each step)

`PROGRAM_SPEC.md` (balance: the two families, the SF stamp; ENGLOADS ids per
Q7); `ch07`, `ch05`, `ch09` §7/§11; `CONVENTIONS.md` §7 rows (the engine
increment owner, the OEI parent owner, the SF stamp) and §7.1 (the
rotation-fixed exclusion); the LRA deck header wording; the `out-of-family`
reason; one Imperial digest wave per step (the balanced and LRA decks, the
case index; ENGLOADS on the turboprops under Q7); `changes/` history
fragments; backlog rows #286 and #285 removed at their closures.

## 8. Deferred

- **Note 21's Kind II** (slipstream, P-factor, propeller normal force) —
  parked on its own trigger.
- **23.363 and 23.361(b)(1) as balanced cases** — mount-local by Q1; they
  ship if a consumer asks for the airplane state around them.
- **The OEI time history as a case set** (several instants) — one instant
  per condition until a consumer needs the envelope.
- **L-7 on OEI** — if the owner wants it, it needs a sideslip from the
  transient, which ONENGOUT (single DOF) does not compute.

## 9. Rulings taken at AGREED (owner, 2026-09-25, in session)

"Agree Q1–Q7 as recommended." Each question of §2 is ruled in its
*Recommended* column, and the decisions that cite it stand unamended:

- **Q1** — the balanced EM set is 23.361(a)(1), (a)(2), (a)(3) and 23.371(b)
  (plus 25.361(a)(3)(i)/(ii) and 25.371 on an `include_far25` project);
  23.363 and 23.361(b)(1) stay mount-local and are named in the deck
  (D-66.3, D-66.4). **Note 21's ruling that 23.361(a)(3) stays mount-local is
  reversed** on the regulation's "1 g level flight loads".
- **Q2** — condition A's parent is the delivered PHAA run (×0.75 for
  (a)(1)); 23.371(b)'s is MAN A scaled to n = 2.5 (D-66.4).
- **Q3** — the torque is reacted by note 21 P-9's aileron-trim couple
  (D-66.7).
- **Q4** — the OEI symmetric half is `BAL C` / `BAL D` / `STALL 1G` at the
  heaviest derivable FLIGHT CG case and the nearest V-n altitude (D-66.11).
- **Q5** — the OEI applied set carries the live-engine thrust and the
  failed-engine windmill drag at the peak instant (D-66.12).
- **Q6** — L-7 is not applied to the OEI cases, stated in band (D-66.15).
- **Q7** — each gyro condition mints four real EM ids in ENGLOADS, retiring
  the render-time `a/b/c/d` suffix; the turboprops' later EM ids renumber in
  #286's digest wave (D-66.8).
