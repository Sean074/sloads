# Critical review — physics, ATR 42 capability, user documentation, issue priority

**Date:** 2026-11-01 · **Baseline:** `dev/v0.10.0` @ `a9bdf9d` (+ untracked
`examples/atr42_300_seed.*`) · **Reviewer:** Claude (Opus 5.5), read-only review.
No code was changed. Every module was run through the CLI on `atr42_100` and
`atr42_300_seed`, the LRA deck was exported for the seed, and the full suite was
run once.

**Scope:**
1. Physics accuracy.
2. Capability for an ATR 42-class analysis.
3. User documentation: how the program works, the methods, their assumptions and limitations, and the validation cases.
4. The open issue list and its priority.

Findings are marked **VERIFIED** (code read, numbers reproduced) or
**SUSPECTED** (a reading that the owner needs to confirm against the regulation
text or the manual). `reference/` is not in the checkout, so manual page
checks were not possible. Every regulation figure below must be confirmed
against the CFR text before code changes (the `04_far25_gap_analysis.md` rule).

---

## 0 · Executive summary

| # | Finding | Severity | Status |
|---|---|---|---|
| P-1 | LGFACTOR energy equation counts wing lift twice. The energy ratio is the **gear** factor, but the code labels it the airplane N and then subtracts L. This is unconservative: about 25 % on gear reactions wherever the energy value governs (`baron_58`). It also makes the entered `N = 2.67` on the ATR fixtures about 12 % low against the energy value | **Critical** | VERIFIED (code + numbers); faithful to LGFACTOR.BAS, so it needs an oracle-deviation ruling |
| A-1 | Every ATR 42 load is a Part 23 (pre-Amdt-64) static analysis. The Part 25 packages F25-1 (gust/VB/U_ref, 25.337 floor) and F25-4 (25.473 landing) are parked and **have no GitHub issue**, while milestone 0.10.0 is titled "the ATR-class analysis" | **Critical (scope)** | VERIFIED |
| A-2 | Balanced cases run past the elevator stop with no flag (ATR seed HT-02: −34.6° against a 25° stop; `atr42_100`: −32.4°) | **Major** | VERIFIED |
| A-3 | OEI windmill drag defaults to a GA fixed-pitch Glauert disc (C_D ≈ 0.50 on the disc). On the ATR this gives 20.3 klb of drag at VD, 13× the engine's thrust, and makes OEI the governing fin case (20.1 klb, 2.6× the manoeuvre cases). There is no feather/autofeather credit and no VMC–VD sweep | **Major** (conservative, but it distorts what governs) | VERIFIED |
| A-4 | ATR seed input errors: forward CG at 1.0 % MAC, VC 240 below VMO 250, chosen n 2.5 below the 25.337(b) value of 2.61, T-tail height inconsistent, `include_far25` off | **Major** (fixture) | VERIFIED |
| D-1 | GUI_USER_GUIDE §5 still teaches the retired "exported = ultimate" model. A user could skip the 1.5 factor | **Major** (unconservative misuse) | VERIFIED |
| D-2 | No current verification record (last baseline 0.7.0), and no readable validation matrix | **Major** | VERIFIED |
| D-3 | No single scope and applicability statement. Five of eleven theory chapters are stubs, including ch11 (the primary deliverable, the LRA deck) | **Major** | VERIFIED |
| T-1 | Suite not green on this working tree: 35 failures, all caused by the untracked `atr42_300_seed`. Some are fixture-count guards; the rest are real failures where the GUI round trip does not leave the project unchanged (§4) | **Major (gate)** | VERIFIED |
| I-1 | The 0.10.0 band is about 75 % process, schema and hygiene work. The four ATR-relevant physics gaps above have no issue, and the validation-citation defects (#371, #373) have no milestone | **Major (planning)** | — |

The FAR 23 replication core holds up well: the gust formula, design speeds,
manoeuvre factors, rolling split, engine torque and gyro, ground-load
combination factors, units and the export equilibrium were all checked and
found correct (§1.3). The weak points are elsewhere:
- one physics error inherited from the source;
- a regulation basis that does not match the ATR 42;
- user documentation that is good where it exists (`docs/60_guide/`) but missing or contradictory where a certifying reader would look first.

---

## 1 · Physics accuracy

### 1.1 Defects

**P-1 — Critical — LGFACTOR double-counts wing lift (`sloads/modules/landing.py:104-130`).** VERIFIED.

The code sets up the energy balance over the stroke:

```
½(W/g)V² + W(1−L)(s+d) = F_gear,max · (η_t·d + η_s·s)
n = numerator / denominator          # = F_gear,max / W
```

The right-hand side is the work done by the **gear** force. The ratio is
therefore the gear reaction factor n_j, and the lift is already accounted for
in the `(1−L)` term. The code labels the ratio as the airplane inertia factor
N and returns `NLG = N − L`, so it subtracts L a second time.

The correct pair is `NLG = n`, `N = n + L`. This is the form of the
23.473(g) floors, which differ by exactly 0.667 (2.67 against 2.0), and of
23.725's `n = n_j·(We/W) + L`. LANDLOAD's own inertia factor at
`landing.py:577` (`nvp = (2·vmp + vnp + lf·wl)/wl`) also uses N = gear + L. So
the module disagrees with itself.

Delivered effect on the fixtures:

| Fixture | Code | Corrected | Effect on gear reactions |
|---|---|---|---|
| `baron_58` (N blank, energy governs) | N 3.364, NLG 2.697 | NLG 3.364, N 4.031 | about **25 % low** |
| `atr42_100` / seed (N entered 2.67) | energy ratio printed as "N 2.375, NLG 1.708" | NLG 2.375, N 3.04 | entered N 2.67 gives NLG 2.003, about **16 % low** |
| `ga6_normal` (N entered 3.167) | — | — | delivered loads unaffected; the p236 oracle locks McMaster's arithmetic, not the physics |

On the ATR fixtures, the entered 2.67 floor was chosen against a value that
is itself under-computed.

*Action:*
1. Owner ruling plus a `02_approved_corrections.md` entry, keeping the p236
   figures as the "printed" column. This follows the #133/#134 pattern.
2. Fix to `NLG = E/(W·Σηδ)`, `N = NLG + L`.
3. Add an independent closed-form energy-balance closure test.
4. Re-derive the ATR fixtures' N.
5. Sweep for the same class (rule 4): any other place where a printed figure
   is the only check on an energy or work balance.

Rule 6 puts this ahead of every [V] row.

**P-2 — Minor (conservative) — checked-manoeuvre pitch acceleration uses +39 for both directions (`select.py:1155-1186`).** SUSPECTED regulation reading.

The pre-Amdt-64 23.423 / 25.331(c)(2) lineage uses:
- **+39/V·n(n−1.5)** for the nose-up check;
- **−26/V·n(n−1.5)** for the nose-down check.

`test_select.py:505` pins McMaster's 787.8. If the reading is confirmed, the
CHECKED MAN UP increment is 1.5× high.

*Action:* confirm the text, then register the value as kept-conservative or
correct it as an approved deviation.

**P-3 — Minor-to-Major on a turboprop — 23.367(a)(2) is the (a)(1) simulation at a different speed (`one_engine_out.py:495-510`).**

The ultimate turbine case uses the (a)(1) fuel-flow-interruption thrust-decay
and windmill schedule. Because of that, the (a)(2) row is almost always
dominated by (a)(1) × 1.5 at VD and adds no independent coverage. Each case is
also evaluated only at the top speed of its range, and nothing checks that
the load is monotonic in speed.

*Action:*
- an (a)(2) drag-time schedule input (blade loss or seizure), or a caption
  stating that it is not distinctly modelled;
- a speed sweep across the range;
- with A-3, the feather and autofeather basis.

**P-4 — Minor — compressibility.**
- `flight_envelope.py:282` scales the whole-airplane 3D slope by
  1/√(1−M²). The finite-wing (Helmbold/DATCOM) form rises less. At AR 12 and
  M 0.5 (ATR) the gust Δn is about 3–5 % high, which is conservative.
- In `select.py:1206-1213`:
  - the tail slope and the downwash wing slope carry **no** Mach correction while the wing gust does, which is inconsistent above about M 0.4;
  - the downwash constant is 36 against 2·57.3/π = 36.48.
- *Action:* use one Mach-correction owner (rule 3) applied to wing and tail
  alike, in the finite-wing form.

**P-5 — Minor — standard atmosphere (`constants.py:357`).** The tropopause is at 35,332 ft (ISA: 36,089 ft) and the isothermal decay is 4.778e-5/ft (ISA: 4.806e-5). The effect is below 0.5 % on the speed of sound above FL350, so not relevant to the ATR (ceiling 25,000 ft).

*Action:* align with ISA / sstandards in passing.

**P-6 — Minor — gyroscopic thrust basis (`engine.py:639`).**
- The value is labelled "max continuous thrust" but is computed from the **takeoff** torque, at VSF, at 100 % efficiency.
- On the ATR this gives 10.9 klb per engine, above the ideal static thrust of the 13 ft disc (about 9.1 klb).
- The gyroscopic rates are Part 23's fixed 2.5 / 1.0 rad/s.
- *Action:* compute thrust from a maximum-continuous power input with a propeller efficiency (or the ideal-disc cap), and fix the label.

### 1.2 Validation strength (physics view)

- The oracle tests pin **McMaster's printed arithmetic**. They catch porting
  errors but not source errors, which is how P-1 survived 30 years and the
  whole port. *Action:* for each oracle-locked module, add at least one
  independent closed-form physics check (energy balance, ΣF = nW, the θ̈
  definition, ideal-disc thrust) beside the printed figure.
- "±0.1 %" is the stated tolerance, but the suite carries 38 asserts at 2e-3,
  20 at 3e-3, 18 at 5e-3 and 4 at 1e-2. Examples are the SELECT h-tail locks
  at 0.5 % (`test_select.py:497-505`) and landing N at 0.2 %
  (`test_landing.py:625`). This is #304. The documentation should state the
  real band per assertion.
- ONENGOUT and the swept-wing path, which are the twin-turboprop features
  most relevant to the ATR, have **no printed oracle**. Appendix B is missing
  (#20), so they are closure-locked only.

### 1.3 Checked and found correct

- **Gust (23.341):** Pratt mass ratio with ρ at altitude, Kg = 0.88μ/(5.3+μ), the 498 divisor (KEAS), U_de 50/25 fps with the altitude taper, 25 fps at VF.
- **Lateral gust (23.443):** includes the (K/l_t)² term.
- **Design speeds:** VC/VD minima and their taper, the VD ≥ 1.25 VC floor, VA = VS√n, VF.
- **Manoeuvre factors (23.337):** all categories.
- **Rolling:** 2/3 n, the 100/75 split per Amdt 23-48, and the 23.455 aileron schedule.
- **Engine torque factors** (turboprop 1.25; the piston factors by cylinder count) and the AC 23-19A corrections.
- **Engine mount and gyro:** 23.363 side load and the 23.371 gyro combinations.
- **Ground loads:**
  - sink rate 4.4(W/S)^¼ clamped to 7–10 fps;
  - spin-up drag K;
  - side loads 1.33 / 0.5 / 0.33;
  - braked roll 0.8;
  - nose gear 2.25 / 0.8 / 0.4 / 0.7.
- **Engine-failure factor table:** (a)(2) carries ULT SF 1.0.
- **V-tail:** 19.5° / 15° sideslip.
- **Units and mass:**
  - unit factors exact;
  - CONM2 carries mass, not weight;
  - a single owner for d'Alembert relief.
- **Export:** deck equilibrium is re-derived from the emitted card text.
- **Span loading:** Schrenk span loading with the basic-loading term, and the swept branch above 15°.
- **ATR seed deck:** 68 subcases; closure residuals 0.09–2.31 % of n·W.

---

## 2 · Capability for an ATR 42-class aircraft

**Basis mismatch, stated plainly.** The ATR 42 is a transport-category
airplane: original basis FAR/JAR 25 at the mid-1980s amendment level, MTOW
16.7 t (-300) to 18.6 t (-500/-600). sloads runs every case under Part 23
rules. "Category C" means that only the load factors are the user's. The
output files cite 23.333–23.499 throughout, and 25.303 appears only in
methods prose.

There is one fortunate historical point. The pre-Amdt-25-86 Part 25 gust rule
used the same Pratt static method, with U_de **66 / 50 / 25 fps at
VB / VC / VD**. So the original ATR 42 basis is reachable as a static
surrogate. But the 66 fps VB line, which is also 23.333(c)'s commuter line, is
**not implemented**, and VB is not computed.

**Seed fixture vs sources** (`atr42_300_seed.project.json`; VERIFIED):

| Item | In file | Expected | Effect |
|---|---|---|---|
| Forward CG | `fwd_gross_pct_mac` 6.0, `fwd_regardless_pct_mac` **1.0** | sources 6.1–32.9 % (1.0 not sourced) | needs 1.4–1.7 klb of ballast to reach; overstated tail-down loads |
| VC | 240 KEAS | ≥ VMO 250 (25.1505) | gust Δn about 4 % low |
| chosen_n | 2.5 | 2.1 + 24000/(W+10000) = **2.61** at 36,817 lb | manoeuvre loads about 4 % low; output prints the user's 2.5 as "minimum required" |
| T-tail height | h-tail at WL 316 | fin tip about WL 328; h-tail mass item at z 301.65 | three inconsistent heights |
| `include_far25` | absent (off) | on for a turboprop transport | 25.361/25.371 not run |
| VD | 300, printed beside "VD(min) 327.5" | — | no explanation shown |
| Misc | description duplicated; `estimation.crew` 1; `engine_count` 0 | — | — |

Correct in the seed:
- area 586.6 ft², MAC, span, h-tail, track 161.4 in (#399 is still open on `atr42_100`);
- MZFW, MLW, fuel;
- propeller, and takeoff torque 8,750 ft-lb.

**Plausibility.** Governing wing root bending is 6.68e6 lb·in, about
0.75 MN·m limit (GUST +C, 2.92 g, `mzfw fwd`, 12,000 ft). A hand check gives
about 7.1e6, so the number is self-consistent. Root shear is 34.6 klb.

**Gap table**

| ATR requirement | State | Impact | Issue |
|---|---|---|---|
| 25.337 n₁ (2.61) and its check | Partial: a user value, not checked | about −4 % manoeuvre | **none**: file as F25-1 |
| 25.341 gust: VB, 66 fps line (old basis) or U_ref/F_g (current) | **Missing** (Pratt 50/25 only) | the governing wing case is missing its VB line | **none**: file as F25-1 |
| 25.341(b) continuous turbulence, tuned-gust dynamics | Out of scope, documented | — | — |
| 25.473 landing: L = 1.0 path, 6 fps at MTOW, LDW/MTOW pairing | Partial (L is free; no 6 fps case) | with P-1, N about 3.0–3.4 against 2.67 delivered | **none**: file as F25-4 |
| Sponson / twin-wheel main gear (per-wheel loads) | Partial (single leg) | per-wheel and axle loads not delivered | none |
| 25.367 OEI: VMC–VD sweep, feather/autofeather drag, (a)(2) distinct | Partial / suspect (A-3, P-3) | fin and aft body possibly 2× over-loaded; governing case misidentified | #353 related; **new** |
| Balance feasibility (elevator stop, tail α, fin stall) | **Missing** (A-2) | unflyable cases delivered silently | #353 partial; **new** |
| Flaps-down V-n (25.345), VF per 25.335(e), flaps-down span load | Missing (seed has no flap coefficient set; VF 145.9 kt is the Part 23 minimum) | flap, h-tail and wing-flap loads absent | #163 plus a new fixture issue |
| 25.351 yaw overswing | Missing (F25-3 parked) | fin manoeuvre load low by about 1.3–1.5 on that phase | none |
| T-tail asymmetric (25.427) | Present as a surrogate | — | the deck prose says "conventional layout" on a T-tail (#255 class) |
| Thrust in the balance | Missing; measured +10.7 % on the ATR tail load | above the method's own error band | #226 (L) |
| Lateral body aero (large fuselage) | Off by default | n_y understated | #390 |
| Distributed wing fuel; 25.343(b) reserve fuel | Point mass; reserve case missing | coarse inertia-relief distribution | #111; reserve: none |
| 25.365 pressurisation | Excluded permanently (D-24) | body skin and frames cannot be sized from the deck alone | by design; state it in the scope page |
| Ground-case fuselage distribution | Missing | sponson gear into the fuselage | #31 |
| Flutter MFC basis for transports (1.2·MD) | GA formula | MFC nonsensical for transports | parked, no issue |
| Altitude, Mach caps, MZFW design weight | **Present** | — | — |

**Verdict:** sloads delivers a credible **Part-23-style static loads set** for
an ATR 42-sized airplane, with good equilibrium in the exported free-free beam
model. It does **not** deliver a Part 25 loads set. Its known deviations go
both ways:
- **unconservative:** landing (P-1), the missing VB gust line, n₁ 2.5 against 2.61, VC below VMO;
- **conservative:** OEI drag, the checked manoeuvre.

---

## 3 · User documentation

**Good:**
- `docs/60_guide/` is written for a structures engineer: a consistent page template, generated field tables, screenshots, two worked airplanes and troubleshooting.
- The LIMIT contract is stated consistently.
- The exported CSVs carry a self-describing METHODS AND LIMITATIONS header that a DER can read on its own.
- `02_approved_corrections.md` is a real register.
- `tests/module_gates.py` maps every module to its gate.

| # | Finding | Severity | Action |
|---|---|---|---|
| D-1 | `GUI_USER_GUIDE.md:263-277` (§5) says to check for `-ULT` and "do not export those numbers", and that SF=1.0 is "still an ultimate deliverable". This is the pre-note-49 model and contradicts §1 of the same file | Major | rewrite §5 to the LIMIT contract |
| D-2 | No validation matrix a user can read. The last verification baseline is 0.7.0 (RELEASE_PROCESS §4 step 5 not followed for 0.7.1–0.9.0). GUI guide §6/§9 points at the **0.2.0** baseline | Major | generate `20_theory/VALIDATION.md` from `module_gates.py`: module × source/page × printed × computed × tolerance × reason; give one command to reproduce it; restore the baseline step |
| D-3 | No single scope and applicability page. The limits are scattered: tricycle gear only (`landing.py:40`); propeller-only OEI; no tail compressibility above M 0.6; rigid airplane with Schrenk; Part 23 discrete gust only; engine layouts 1N/2W/4W; pressurisation excluded; the Part 25 gaps | Major | write one page: supported configurations, speed/Mach/weight range, what is not modelled, **and which way each omission errs**; link it from README and CAPABILITIES |
| D-4 | Theory chapters ch04, ch05, ch08, ch10 and ch11 are stubs. ch11 (the LRA deck, the primary deliverable) has no deck walk-through: subcases, the LABEL ↔ case-ID join, where the SF is stated, how to apply 1.5 in sbeam. There is no chapter on control surfaces (aileron, flap, tab) or on the weight methods | Major | finish ch11 first, with an annotated deck excerpt; then ch08 (with P-1) and a control-surface chapter |
| D-5 | `CAPABILITIES.md` §2 still advertises the workbook, the dashboard and the Results Review / Export page, all retired at #270 | Major | resync to the outputs that actually ship |
| D-6 | `DATA_DICTIONARY.md` is broken: two field tables, most types `?`. Cause: `docs/generate_data_dict.py:103-108` swallows its exception, and `models.py` is now a package. GUI guide §4 sends users there | Major | fix the generator; add a test that every input dataclass gets a table |
| D-7 | `reference/` is gitignored, so a reviewer cannot check a single page citation. Combined with #371 (six wrong page citations) and #373 (the Ref 1 citation is incomplete), validation traceability is weak | Major | a "How to obtain the references" section (DOT/FAA/AR-96/46 is public; give the full citation for McMaster 1996); ship the `.md` CFR transcriptions |
| D-8 | The README has no route to the user docs, mentions a CI badge that does not exist, and names a root `CHANGELOG.md` that is not there | Minor | a Documentation section (#394 should absorb this) |
| D-9 | `B_worked_twin.md` has no checkpoint table, so the twin (closure-locked) path cannot be checked by a user | Minor | add one |
| D-10 | Developer jargon (note, G-OR, D-xx IDs) and dated narrative in ch09–ch11 go against CV-4 | Minor | move IDs to Sources; move the narrative to `90_record` |
| D-11 | Changelog entries are 300–500-word paragraphs, so changes that move delivered loads cannot be found | Minor | a "results-affecting changes" list per release |
| D-12 | The corrections register has no magnitude column | Minor | add the delivered-load effect of each deviation |
| D-13 | `concept_regional_jet` and `concept_heavy` have no `.sources.md`; the ATR seed is untracked | Minor | provenance, or mark them synthetic |

---

## 4 · Build state

Running `pytest` on this working tree gives **35 failed, 4452 passed, 48 skipped**.
Every failure is caused by the untracked `examples/atr42_300_seed.project.json`.
`main` is unaffected. The failures fall into two kinds.

**1. Fixture-registry guards.** These expect five shipped examples and find six:
- `test_cg_cases` ground coverage;
- `test_deliverable_units` (two tests);
- `test_oracle_inputs::test_every_shipped_example_is_classified`;
- `test_validation`'s warning census.

These are expected for a new fixture and are cleared by registering it.

**2. Round-trip failures.** These are substantive:
- `test_derived::test_every_example_stores_the_mass_it_derives`: the seed's stored mass disagrees with what it derives;
- `test_dirty_flag` (oracle page render changes the project);
- `test_widget_freshness` (stale widget state overwrites the loaded project).

The `test_dirty_flag` and `test_widget_freshness` failures occur on most
pages. Either the seed (sconfig-exported) is not round-trip-clean, or it
exposes a GUI defect that the curated fixtures do not.

*Action:* diagnose kind 2 before committing the seed. This belongs with the
A-4 corrections, and it is also evidence for the sconfig schema work
(#348/#355): an exported seed should load clean by construction. Do not fix it
by excluding the file from the glob.

---

## 5 · Issue list and priority review

**State:** 30 open issues. Band B11 (0.10.0, chartered "the ATR-class
analysis, measured") holds 26 rows. Of these:
- about **6 touch delivered loads** (#226, #337, #390, #399, and #217/#218 riding #226);
- about **20 are process, schema, packaging or test hygiene**.

None of the physics or capability gaps in §1–§2 has an issue.

### 5.1 Issues to file (with bodies, rule 5)

| Proposed | Tier | Rank |
|---|---|---|
| **LGFACTOR double-counts L (P-1)**: an oracle deviation, plus the fix and the energy-closure gate | L (oracle deviation, physics) | **B11 head**: a first-order defect on shipped content, unconservative |
| **Balance feasibility flags**: elevator stop, tail α, fin stall (absorbs #353, rule 4) | M | B11, after P-1 |
| **OEI basis for feathering turboprops**: windmill C_D default / feather time, VMC–VD sweep, distinct (a)(2) (A-3, P-3) | L | B11 |
| **ATR seed fixture corrections** (A-4) plus the widget-freshness failure (§4) | S | B11, before the seed is committed |
| **F25-1 transport envelope**: 25.337 n₁ check, VB computed, 66 fps VB line (old-basis surrogate) and/or U_ref/F_g | L | 0.10.0 if the ATR is the target; otherwise state in the milestone title that it is not |
| **F25-4 landing variant**: L = 1.0, 6 fps at MTOW, LDW/MTOW pairing | M | with F25-1 |
| Gyro thrust basis (P-6) | S | B11 tail |
| Mach correction, one owner for wing and tail (P-4) | M | C |
| Validation matrix plus restored baselines (D-2); scope page (D-3); GUI guide §5 (D-1); CAPABILITIES resync (D-5); DATA_DICTIONARY generator (D-6) | S–M each | D-1 and D-5 in B11 with #394; D-2 and D-3 before 1.0.0 |
| Multi-wheel / sponson gear per-wheel loads; 25.343(b) reserve fuel; transport MFC | M | C |

### 5.2 Re-ranking the existing issues

| Issue | Current | Recommendation | Reason |
|---|---|---|---|
| #394, #395, #396, #397 | B11 Pri 1–4 | **keep at the head**, but make #394 absorb D-8 and route to the docs | cheap, and they gate whether a colleague can use the program at all |
| #399, #337 | Pri 5–6 | keep | fixture data defects; #399 is fixed in the seed but not in `atr42_100` |
| #400 sbeam drift | Pri 7 | keep; consider raising it | the CI loop is the mission's own claim |
| #226 thrust in the balance | Pri 8, L | keep, **after P-1** | measured at +10.7 %, above the method's error band |
| #371, #373 citation defects | **unbanded** | **move into B11** | they are the validation traceability a DER checks first; S-tier |
| #304 tolerance class | Pri 22 | **raise** to beside the validation matrix | the "±0.1 %" claim is not true suite-wide; documentation and tests must agree |
| #353 fin stall | parked | **un-park** into the feasibility-flag issue | the same class as the ATR elevator-stop finding |
| #163 flaps-down span load | C | **raise** for the ATR | 25.345 flap cases are absent entirely |
| #111 wing fuel band | C | do the S-tier measurement now (it was promised and never run) | a wet-wing transport is exactly the case it was deferred for |
| #20 Appendix B | open decision | **actively pursue a legible Appendix B** (the original McMaster manual / NTIS) | it is the only printed twin-turboprop oracle: OEI and swept wing, the ATR-relevant paths |
| #390 directional stability | Pri 9 | keep | — |
| #348, #355, #351, #356 (sconfig schema) | Pri 11–14 | **merge into one or two issues** | four rows for one deliverable (a generated JSON Schema plus its document) |
| #359 slim backlog | Pri 17 | **raise** | the 684-line backlog, re-cut narratives and double booking are a large share of the cost of every closure; this review needed a file read to find what 0.10.0 contains |
| #357, #358, #185, #92, #130, #209, #246, #340, #345, #346 | Pri 15–26 | keep in B11 or move to 1.0.0 | hygiene; no delivered load moves |
| #217, #218 | no tier | tier them or close them into #226 | each row should carry a tier |
| #375, #14, #305, #279, #31, #17, #18, #19, #32, #398 | C / 1.0.0 | keep | #31 (ground body distribution) matters for sponson gear into the fuselage; flag it for ATR body sizing |

### 5.3 Process observations

- The governance machinery (tiers, gates, note numbering, re-cut narratives)
  is unusually rigorous and has demonstrably caught defect classes; the
  2026-09-15 safety-factor sweeps are examples. But the effort ratio is now
  inverted. 0.10.0 carries more rows about how work is recorded than about
  the loads the milestone is named for, and the theory chapters that a user
  needs are stubs, while 64 design notes and 28k lines of record exist.
- Rule 6 (effect against error bar) is sound. Applying it requires that
  *source* errors be findable. Because the oracle validates against the
  source, P-1 class defects are invisible to the current gates. Independent
  physics closures (§1.2) are what close that hole.

---

## 6 · Recommended actions, in order

1. **P-1:** owner ruling, oracle-deviation entry, fix, energy-closure gate,
   re-derive the fixtures' landing N. Unconservative, first-order.
2. **D-1:** fix GUI_USER_GUIDE §5. The documentation can lead to
   unconservative use.
3. **§4 / A-4:** fix the ATR seed (CG, VC ≥ VMO, n₁ 2.61, T-tail height,
   `include_far25`) and resolve the widget-freshness failures before
   committing it.
4. **A-2:** add the balance feasibility flags (elevator stop, tail α, fin
   stall; absorbs #353).
5. **Decide what "ATR-class analysis" means for 0.10.0.** Either file and
   rank F25-1 and F25-4 (VB with the 66 fps line, the n₁ check, the Part 25
   landing pairing), or retitle the milestone to "Part-23-method surrogate
   for ATR-sized airplanes" and state that in the scope page.
6. **A-3 / P-3:** the OEI basis for feathering turboprops.
7. **#226:** the thrust term (already measured).
8. **Documentation for a reviewer:**
   - the validation matrix and restored baselines (D-2, #304, #371, #373);
   - the scope and applicability page (D-3);
   - the ch11 deck walk-through (D-4);
   - CAPABILITIES and DATA_DICTIONARY repairs (D-5, D-6);
   - the reference-access section (D-7).
9. **Independent physics closures** beside each printed oracle (§1.2).
10. **Slim the backlog (#359)** and consolidate the schema rows, so the next
    milestone's rows are about loads.
