# OEI basis for feathering turboprops: feather credit, a distinct 23.367(a)(2) and a VMC–V speed sweep (design note 74; #405)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-11-02** (#405; one `changes/` fragment, no history entry). AGREED 2026-11-02 — no code (owner, in session, under the solo profile — rule 1's working-alone branch); Q1 ruled (a), Q3 ruled 1.0 s [E]. PROPOSED the same day. The owner ruled the shape in session the same day
(the feathered drag, the (a)(2) decay). Revised the same day:
- the autofeather is a take-off system (Dash 8; ATR 72 POH: armed only with PWR MGT at
  TO, activated 2.15 s after the failure), so it is recorded and not modelled (D-74.4);
- **the pilot initiates the feather at 2 s** (23.367(b), Lomax p. 42), stated as an
  owner assumption on every credited case. The drag holds until then and ramps to G-83
  over an [E] blade travel time (D-74.3).


Drafted for review findings **A-3** and **P-3** of
[`2026-11-01_critical_review_physics_atr42_docs.md`](../50_reviews/2026-11-01_critical_review_physics_atr42_docs.md).
- **A-3:** the failed hub's drag is ONENGOUT's Glauert fixed-pitch disc (C_D,disc 0.502).
  On `atr42_100` it is 20,319 lb at VD, 13× the live engine's 1,537 lb, and it makes
  OEI the governing fin case. No feathering is credited.
- **P-3:** the 23.367(a)(2) case reuses (a)(1)'s fuel-flow decay, so it adds no distinct
  coverage. Each case is run only at the top of its range.

**Scope.** This note adds three things to `one_engine_out`:
- the feathered-propeller drag and a pilot feather at 2 s;
- a distinct (a)(2) thrust decay;
- a speed sweep over each case's range.

Out of scope:
- the engine's own windmilling drag (G-80/G-82, D-74.8);
- a jammed engine's extra drag (Lomax p151, D-74.8);
- the map from Lomax's EO I/II/III onto ONENGOUT's instant (D-74.9).

Conventions: [`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §2 (axes, signs) and §3
(every load LIMIT; (a)(2) states `ULT SF=1.0`, D-66.14, unchanged).

**Sources** (in `theory_sources.md` at closure):
- Torenbeek, *Synthesis of Subsonic Airplane Design*, 1982, App. G-8, pp. 553–555,
  Eqs. G-79 to G-85. Photographed: `Library/configuration/Design_Torenbeek/20261011_210600`–`210854`.
- Lomax, *Structural Loads Analysis for Commercial Transport Aircraft*, 1996:
  - §4.3, pp. 42–43: the 25.367 text and the limit/ultimate split;
  - §9.3, pp. 150–151: the EO conditions and the decay times.
- 14 CFR 23.367(a), (b); Ref 1 Ch 11 pp. 87–88 (ONENGOUT).

---

## 1. What the sources settle

| Source | Content | Use |
|---|---|---|
| Torenbeek G-83, p. 554 | Stopped, feathered propeller: Δ(C_D S)_prop = 0.00125 B_p D_p², B_p "the number of blades per propeller" (p. 555). Dimensionless coefficient. As a disc coefficient: **0.00159·B_p**. | The drag after feathering (D-74.1). |
| Torenbeek G-8, p. 553 | "The drag increment in **steady flight** following engine failure". The windmilling propeller is referred to Ref. G-100, not given. | G-83 is the end state, not the transient peak (D-74.2, Q1). |
| 23.367(a), quoted by Lomax p. 42 | Turboprops are designed for the failures "in combination with **a single malfunction of the propeller drag limiting system**"; (a)(3) the decay and drag history substantiated by data. | The autofeather is not credited; the regulated case keeps the windmill peak until the pilot acts (D-74.3, D-74.4). |
| 23.367(b), Lomax p. 42 | Pilot corrective action not earlier than 2 s after the failure. | The pilot starts the feather at 2 s, an owner assumption (D-74.3). |
| Lomax §9.3.1, p. 151 | Fuel-flow interruption: limit, "a linear variation of thrust for convenience of analysis". Mechanical failure: ultimate, "T/T₀ … may be assumed to be zero in **0.02–0.10 s**". A jammed engine "would produce significantly more drag than the windmilling case". | The (a)(1) ramp (unchanged, now cited) and the (a)(2) decay (D-74.5). |

## 2. Decisions (D-74.1 … D-74.11)

| # | Decision | Rationale |
|---|---|---|
| **D-74.1** | **Feathered drag** `feathered_drag_cd(blades) = 0.00125·B·4/π`, the G-83 drag area on the disc, so it rides `windmill_drag_from_cd` (`one_engine_out.py:299`) at the case's q. It needs `EngineInput.prop_blades > 0` and refuses by name without it. | One drag owner. G-83 is dimensionless, so it applies in any unit system. |
| **D-74.2** | **The peak is unchanged:** the entered `windmill_drag_cd` (D-66.12a, the (a)(3) history) or the Glauert bound. G-83 never replaces the peak. | G-83 is steady flight (p. 553). The transient peak, before the feather completes, is what loads the fin. |
| **D-74.3** | **The pilot feathers, starting at 2 s** (owner ruling 2026-11-02). The failed propeller's drag builds to the peak on ONENGOUT's ramp. At `CORRECTIVE_DELAY_S` (2.0 s after the failure, the 23.367(b) / Lomax p. 42 earliest pilot action, moved to `constants.py` from `one_engine_out._CORRECTIVE_DELAY_S`) the pilot starts the feather, and the drag ramps linearly from its value at 2.0 s to the G-83 drag over `EngineInput.feather_travel_time_s: Optional[float]` (the blade travel to feather, [E] unless the maker gives it), then holds. The credit applies to the (a)(1) and low-end cases at every swept speed. **(a)(2) never takes it** (D-74.5). Blank travel time: no feather, and the drag holds at the peak as today. Every credited case states the assumption verbatim (`FEATHER_ASSUMPTION` owner string): "the pilot initiates the feather 2 s after the failure (23.367(b), owner assumption), completed in the entered blade travel time". | The owner's ruling. 23.367(b) and Lomax set 2 s as the earliest corrective action; the clause speaks of the flight controls, so applying it to the engine controls is an owner assumption, and it is stated. It is the earliest the pilot may act, not a conservative estimate (23.367(a)(4)), and the case says so. |
| **D-74.4** | **No autofeather credit.** The autofeather is recorded, not modelled: on the ATR 72 (POH) it is armed only with PWR MGT at TO, the ATPCS pushbutton ON, both power levers above 49° and both torques above 46 % in flight, and it activates 2.15 s after the failure is detected; on the Dash 8 it is a take-off system too. The pilot's 2.0 s initiation (D-74.3) precedes the ATR's 2.15 s activation, so an autofeather would add no credit, and it is never armed at VC/VD. | The sequential schedule replaces the earlier 2 s gate and the blend (owner, A, 2026-11-02). One feather schedule, not two. |
| **D-74.5** | **A distinct (a)(2):** `OneEngineOutInput.mech_failure_decay_time_s: float = 0.02` (Lomax p151, the abrupt end of 0.02–0.10 s, which gives the largest yaw rate). The thrust decay ramp on the VC (ultimate) case uses it. Its drag is the peak, **never credited** (Lomax p151's jammed engine). It is marched at `min(time_step_s, decay/2)` so the decay is resolved. | P-3. A 0.02 s decay inside a 0.05 s step would otherwise be a step at t = 0. |
| **D-74.6** | **Speed sweep:** each failure case is marched at 11 equal speeds over `[v_lo, v_hi]` (the low end, then VC or VD), at the case's altitude. The case delivers the speed with the largest peak \|fin load\|, and its basis states that speed and the top-end value. The case's identity, label and SF are unchanged. An entered `speeds_kt` is not swept. | P-3. `_LoadCase` already records `v_lo`. The cost is 10 extra marches per case, without the I/O. |
| **D-74.7** | **The schedule has one owner,** `engine_forces_at` (thrust, remaining thrust, drag at t). `_moment` and the balanced case read it, so the feather ramp cannot drift between the march and the deck. | Rule 3. Today `_moment` restates the ramps (`one_engine_out.py:357`). |
| **D-74.8** | **Parked with their numbers:**<br>• The engine's windmilling drag: G-80 external, 0.1·(π/4)·D_i². At an assumed 1.5 ft inlet it is 0.18 ft², 0.13 % of the ATR's Glauert drag area (132.7 × 0.502 = 66.6 ft²), and there is no inlet field.<br>• The jammed engine: Lomax gives no number, so it is recorded as unquantified. | Rule 6. |
| **D-74.9** | **Lomax's EO I/II/III** (p. 150: maximum sideslip with zero rudder; maximum yaw rate or rudder at 2 s; zero sideslip with the rudder required) **are recorded, not re-mapped.** ONENGOUT delivers its own peak instant (D-66.10). | A follow-up issue if the owner wants EO I or III as separate cases. |
| **D-74.10** | **Uptrim is recorded, not modelled.** ATPCS uptrims the live engine in the take-off band. The low-end case already flies the live engine at `takeoff_hp`, and the case states that it should be the uptrimmed (reserve) rating where the installation uptrims. No new field. | The live engine's power is entered; no autofeather is modelled to trigger the uptrim. |
| **D-74.11** | The fixture decay and drag times are unsourced. Each fixture's `.sources.md` records them as such, citing Lomax p. 42 for the 1 s to several seconds range. They are not changed. | Rule 6: the time scale sets the yaw rate, so it is named rather than silently carried. |

## 3. Closure gates (G-74.1 … G-74.7)

| Gate | Statement | Target |
|---|---|---|
| **G-74.1** | G-83 sub-formula: `feathered_drag_cd(B)·πD²/4 == 0.00125·B·D²` (Torenbeek p. 554). The ATR, at B 4 and D 13 ft: 0.845 ft², 1.27 % of the Glauert area. | rel 1e-12 |
| **G-74.2** | No credit: an engine with no `feather_travel_time_s`, and every (a)(2) case whatever is entered, marches identically to today's cases (at the top-end speed, before the sweep). | rel 1e-12 (D-74.7 may reorder the arithmetic) |
| **G-74.3** | Credited case: the drag equals its 2.0 s value at 2.0 s and the G-83 drag at 2.0 s + travel, at the case's q, and the case states `FEATHER_ASSUMPTION`. The peak fin load is ≤ the uncredited case's. The ATR at VD (q ≈ 305 psf): 20,319 lb held until 2.0 s, then down to 258 lb. The fin load before and after is recorded at implementation. | rel 1e-9; ≤ |
| **G-74.4** | (a)(2): thrust is 0 by 0.02 s. The peak fin load converges between the step and half the step. It never takes credit, even when entered. | ≤ 1 % |
| **G-74.5** | Sweep: the delivered speed's peak is ≥ the top end's at every fixture. The governing speed of each case is recorded at implementation. | ≥ |
| **G-74.6** | The balanced OEI deck closes against the march at the delivered speed (G-66.9, unchanged gate). | as G-66.9 |
| **G-74.7** | ATR re-derivation: the governing fin and aft-body cases, before and after, recorded in the PR. With Q1 at (a), the VD peak stays 20,319 lb for the first 2 s; the feather (D-74.3) is what moves the VD fin load, if it moves at all. | recorded |

**Delivered numbers move:**
- (a)(2) on all three twins (`atr42_100`, `atr42_300_seed`, `baron_58`): the 0.02 s decay and the sweep;
- (a)(1) on any twin where the sweep finds an interior speed;
- the (a)(1) and low-end cases on any twin with a `feather_travel_time_s` entered (Q3).

One Imperial digest wave. No oracle: Ref 1 prints no ONENGOUT output, and the
ONENGOUT.BAS sub-formula tests stand unchanged.

## 4. The transient, and questions for the owner

**The thrust-to-drag transition is modelled, by prescription and not by inertia.** The
schedule (ONENGOUT, `engine_forces_at`) runs:
1. the failed propeller's thrust ramps linearly to zero over `thrust_decay_time_s`, as
   the engine runs down;
2. its drag then builds linearly to the peak over `windmill_drag_time_s`.

That is Lomax's "linear variation of thrust for convenience of analysis" (p. 151). The
rotational inertia of the engine and propeller enters only through the two entered
times, which 23.367(a)(3) wants substantiated. No run-down dynamics are modelled. The
times on all three twins are 0.5 s and 2.0 s with **no provenance in any
`.sources.md`**. Lomax's Fig. 4.5 decay takes about 1 s, and he gives "1 s to as long
as several seconds" (p. 42). Recorded as an input gap (D-74.11).

- **Q1 — the windmill peak. Ruled (a), 2026-11-02.** With the feather at 2 s (D-74.3), the peak acts for the
  first 2 s of every (a)(1) case and for the whole (a)(2) march. How much of A-3 the
  feather removes depends on when the fin load peaks, which is measured at
  implementation (G-74.3). The peak's value is still unsourced. Options:
  - (a) keep the Glauert bound as the blank default, stated. A turboprop with no entered
    `windmill_drag_cd` gets a `ConsistencyWarning` giving the bound's drag-to-thrust
    ratio, which is 13× on the ATR at VD.
  - (b) require `windmill_drag_cd` when 23.367(a) applies (turboprop), and refuse
    without it.
  - (c) a sourced default from Torenbeek's Ref. G-100. It is now an ESDU data item, not
    available in session.

  **Recommended: (a).** #405 then closes P-3 and the feather basis. Whatever A-3 leaves
  after the feather is carried to a new issue, "sourced windmilling-propeller drag at the fine-pitch limit
  (ESDU)", with the 20,319 lb (13× thrust) as its number.
- **Q2 — ruled 2026-11-02:** the pilot starts the feather at 2 s; the autofeather is not
  modelled (D-74.3, D-74.4).
- **Q3 — the fixtures' `feather_travel_time_s` [E]. Ruled 1.0 s [E] on the three twins, 2026-11-02.** No source in hand gives a blade
  travel time to feather for the PW120 / 14SF installation or the Baron's. It is
  needed for the two ATR fixtures and `baron_58`, or left blank there (no credit).

## 5. Implementation record (#405, 2026-11-02)

- **D-74.7 as built:** the feather ramp has one owner, `_feather_drag`, read by
  both `_moment` and `engine_forces_at`. The thrust and build-up arithmetic keeps
  ONENGOUT's own statement order in `_moment`, so a march with no feather is
  bit-identical to v81 (G-74.2 holds at equality, not 1e-12). The feather starts
  at `feather_start_s` = max(2 s, the decay time): a propeller still giving
  thrust is not being feathered.
- **G-74.7, the ATR (`atr42_100`), per engine, before → after:**
  - VD (a)(1): 19,568 → **19,079 lb** (−2.5 %);
  - VC (a)(2): 14,075 → **13,245 lb** (−5.9 %);
  - VS: 6,330 → **6,278 lb**.

  The fin load peaks at 2.15–2.5 s on every twin, just after the feather starts,
  so the feather trims it rather than removing it. The (a)(2) fall is the model's,
  not a defect: the abrupt failure yaws the airplane early (peak yaw rate by
  about 1 s), and it is already swinging back on its weathercock stiffness when
  the rudder goes in at 2 s. Halving the step moves it by 0.07 %.
- **The sweep:** the top end governs every swept case on all three twins.
- **The h-tail:** the governing ATR h-tail root bending is still the induced
  roll of ONE ENGINE OUT VD, 340,403 → 332,206 lb-in, now +6.8 % on
  UNSYMMETRICAL's 311,137.
- **Q1 (a):** `windmill_drag_bound` on the ATR's VD case gives 13.22× the live
  engine's thrust and 11.24× the rated power (the seed: 14.94× and 12.70×).
  A-3's remainder, a sourced windmilling drag at the fine-pitch limit (ESDU,
  Torenbeek Ref. G-100), is carried to its own issue.
- **The oracle reduction:** the feather is a sloads input the oracle GUI never
  asks for, so `test_oracle_inputs.PILOT_FEATHER` declares the one-engine-out
  and fin chordwise values it moves on `baron_58` and `atr42_100`. The precedent
  is the turbine-rotor model. `fixtures.unrecovered_turboprop` blanks the
  feather, because with it VS recovers at any rudder throw that keeps VC
  recovering.

