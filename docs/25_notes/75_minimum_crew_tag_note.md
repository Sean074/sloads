# Crew is in the zero-fuel weight, and payload cases are built to MZFW and full fuel at both limits (design note 75; #337)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-11-02** (#337; addendum §5 SHIPPED 2026-11-03, #424; closure under the #359 rules, so one
`changes/` fragment and no history entry). AGREED 2026-11-02, no code. The owner ruled in session,
under the solo profile (rule 1's working-alone branch), on the payload-case
rule (§2) and approved the plan. That ruled Q1–Q4 of the first draft:
- the crew tag is a boolean on the row;
- the schema hop infers nothing;
- payload cases are built to the owner's rule;
- the Baron's half-hour reserve fuel goes to its own issue.

**Scope.** `baron_58` is the only shipped fixture whose weight database carries no
crew in its `MINIMUM` rows. Its pilot sits inside the discretionary row
`Pilot & front passenger` (340 lb at +75). As a result:
- its minimum flight weight, which is also WTENV's minimum point and the start of
  both envelope edges, is the empty airplane plus unusable fuel (4,100 lb at
  78.36), with nobody at the controls;
- the GROUND case `aft max landing` flies without a pilot.

This note puts the crew in the zero-fuel weight with a typed tag and a guard. It
also states how payload cases are built, and rebuilds the Baron's cases to that
rule.

Out of scope here, filed as issues:
- **#422** the seed (`cg_cases.seed_flight_cases` / `seed_landing_cases`) builds
  to the rule, and the other fixtures are re-entered;
- **#423** a fuel vector for each payload case on the Weight/CG grid (review C5);
- **#424** the Baron's 23.25(b)(3) half-hour fuel.

## 1. Sources

- **14 CFR 23.25(b)**, as quoted in the User's Guide (DOT/FAA/AR-96/46 §4.3.1.2,
  p4-3). The minimum weight is not more than empty weight + "the weight of the
  required minimum crew (assuming a weight of 170 pounds for each crewmember)" +
  half an hour of fuel at maximum continuous power. UG §4.3 p4-2 says the minimum
  crew is "usually the pilot".
- **Lomax** (1996):
  - §14.1 p233: MZFW is "the maximum weight at which the airplane may be loaded
    with zero usable fuel".
  - Eq 14.1 p234: maximum design payload = MZFW − OEW.
  - §11.4 pp199–202: the rational payload loading is MZFW at the forward flight
    CG with the payload end-loaded, plus the reverse loading.
  - Lomax gives no crew rule; 23.25(b)(2) supplies it.

## 2. The payload-case rule (owner, 2026-11-02)

Payloads are built so the case set holds these combinations:

| Corner | Weight | Fuel | Payload | CG |
|---|---|---|---|---|
| **Full fuel fwd / aft** | gross (MTOW) | maximum | the minimum that reaches gross | forward / aft limit |
| **MZFW fwd / aft** | MZFW | none | MZFW − OEW (Eq 14.1) | forward / aft limit |
| **MZFW + fuel** | to MLW (landing), to gross | as required | the MZFW payload | follows the payload |

Where the database's own rows cannot reach a limit, the corner is the **extreme
the rows reach**, and the gap is stated. The corner is never dropped and never
ballasted. WTENV's D-27 structural-limit points (aft gross, fwd gross,
fwd regardless, min weight) stay as they are: they are the certification corners
FLTLOADS reads.

## 3. Decisions

| ID | Decision |
|----|----------|
| **D-75.1** | **`MassItem.required_crew: bool = False`** is the seventh typed tag (not `crew`, which is `WeightEstimationInput`'s numeric crew count). It marks required crew and is orthogonal to `kind`, as `usable_fuel` is. It is an input, never a name match (note 63 OV-1). |
| **D-75.2** | **Schema v83.** `_hop_82` is an identity, an additive field that infers nothing, as the v73 hop did. A migrated file is warned (D-75.3) until its crew row is tagged. |
| **D-75.3** | **`minimum_crew_missing`** (page `weight_mass`). A non-empty weight database with no row that is both `required_crew` and `MINIMUM` is warned, citing 23.25(b)(2). |
| **D-75.4** | **`crew_not_minimum`** (page `weight_mass`). A `required_crew` row whose kind is not `MINIMUM` is warned by name. As payload, a crew row can be left off a loading; as `EMPTY`, it moves the 23.29 empty weight. |
| **D-75.5** | **Every shipped fixture tags its crew:**<br>• `ga6_normal`: Pilot<br>• `atr42_100` and `atr42_300_seed`: Captain + First officer<br>• `concept_regional_jet`: Crew (2)<br>• `concept_heavy`: Pilot and Copilot<br>No weight moves on these five. |
| **D-75.6** | **`baron_58` splits the row:**<br>• `Pilot`: 170 lb at +75, `MINIMUM`, `required_crew`, graded [E] (23.25(b)(2); the arm is [A]).<br>• `Front passenger`: 170 lb at the same point, discretionary.<br>`fwd gross` and `fwd light` re-enter on `Front passenger`, with weight, moment and waterline unchanged. `fwd gross` already is the full-fuel forward corner: full fuel, 510 lb of payload, 5,500 lb at 78.30. |
| **D-75.7** | **The Baron's other corners, rebuilt to §2.** Each waterline comes from its own loading (D-26a). |

The D-75.7 corners:

| Case | Weight | CG | Loading | Note |
|---|---|---|---|---|
| `mzfw aft` | 5,270 | 86.00 (limit) | passengers full; nose 0.1688; rear 0.2484 | |
| `aft gross` (D-27 limit point, now entered) | 5,500 | 86.00 (limit) | the MZFW payload (every seat; nose 0.1458; rear 0.2656) plus 230 lb of fuel (tanks 0.3194) | until now it was searched, and the search closed it with no pilot aboard; with the pilot it needs 110 lb of ballast; z 95.88 → 96.56 |
| `mzfw fwd` | 5,270 | **79.61** | nose and front full, mid full, rear 0.475 | the rows' forward extreme; the limit is 77.54, a gap of **2.07 in** |
| `full fuel aft` (new FLIGHT case, appended) | 5,500 | **85.37** | full fuel; aft passengers full; rear 0.425 | the rows' aft extreme; the limit is 86.0, a gap of **0.63 in** |
| `aft max landing` | 5,400 | 85.90 | `mzfw aft` plus 130 lb of fuel (tanks 0.1806) | |
| `fwd max landing` | 5,400 | 79.67 | `mzfw fwd` plus the same fuel | |

## 4. Effect and gates

**What moves, all on the Baron:**
- The minimum flight weight goes from 4,100 / 78.36 to **4,270 / 78.22**.
- Three cases move to the rule (`mzfw aft`, `mzfw fwd` and the two landing
  cases), and one FLIGHT case is added, which appends V-n conditions after the
  existing ones.
- Landing reactions move with the landing CGs: aft 85.72 → 85.90, fwd 79.14 → 79.67.
  The main peaks do not move; the nose peaks fall to VNP 6,383 and DNP 2,402 lb
  (−1.2 %).
- **`aft gross`, measured at closure:** with the pilot aboard, its searched loading
  needed 110 lb of ballast, so it is entered as the MZFW payload plus 230 lb of
  fuel (it was 720 lb). Less wing fuel lowers its closure Izz from 7,369 to
  6,564 slug ft² (−11 %). The three VA lateral cases it governs keep their fin
  loads and Ny, while r_dot and p_dot rise 12 % (SUDDEN RUDDER 217.3 → 243.4
  deg/s²).
- PHAA and ACRL now close at `mzfw fwd`, where they closed at `mzfw aft`.
- The Baron's 39 Imperial digest channels move; no other fixture's do.
- `fwd regardless` sits below the new minimum weight. It is already flagged
  (#309).
- The Baron's Imperial digests and derived `mass` block are regenerated.

**Gates (`tests/test_minimum_crew.py`):**
- **G-75.1:** every shipped fixture is free of both warnings.
- **G-75.2:** a constructed database trips each warning by code.
- **G-75.3:** the Baron's minimum flight weight is 4,270 / 78.22 (`loading_kind_totals`).
- **G-75.4:** each Baron corner in D-75.7 holds its weight, and its CG is either the
  limit or the rows' extreme in that direction. That extreme is the station-order
  fill of the payload rows, computed in the test independently of the fixture.
- **G-75.5:** the v82 → v83 hop is an identity (`test_schema_guards`).
- The existing `case_loading_checks` keeps every entered loading matching its case.

## 5. Addendum (#424, owner 2026-11-03): no structural-reserve credit

**Ruling.** Standard weight definitions, and no reserve-fuel credit taken in the
loads. A `MINIMUM` row is aboard every loading, so the reserve rows the ATR, the
regional jet and `concept_heavy` carried rode inside every zero-fuel weight. That
is the credit 23.343(c) (61 FR 5144, 1996) and 25.343(a) allow but do not
require, and taking it owes a zero-wing-fuel case at 90 % n / +2.25 g and 85 %
gust (23.343(c)(1), 25.343(b)(1)). The minimum weight of 23.25(b) is a ceiling
("not more than"), and 25.25(b) leaves it to the applicant, so empty + crew
complies. It is also the lower weight, which raises the light-weight gust n.

| Quantity | 14 CFR | McMaster (oracle) | Lomax (1996) | sloads |
|---|---|---|---|---|
| Minimum weight | 23.25(b): ≤ empty + crew + ½ h fuel | items 51–60: pilot + "30 MIN FUEL" 71 lb = 2,063 lb (App. A p136, p139) | OEW_min, no usable fuel (§14.1 p233) | `EMPTY` + `MINIMUM`; ga6 keeps its 71 lb (oracle), the rest no fuel |
| ZFW / MZFW | 23.343(b) zero wing fuel | no zero-fuel condition | zero usable fuel (p233), payload = MZFW − OEW (Eq 14.1 p234) | zero usable fuel |
| Structural reserve | optional (23.343(c), 25.343(a)) | not addressed | the band OEW + SRF … MZFW + SRF (§14.1.1 p234) | not selected |

| ID | Decision |
|----|----------|
| **D-75.8** | The reserve rows fold into the tank rows at the same station (ATR 350 → wing fuel 4,937 a side; RJ 1,500 → mission fuel 4,940; heavy 300 → wing fuel 2,900 a side), so every fuelled case keeps its weight and CG. `min weight` and the `mzfw` cases are re-seeded (D-63.5) with no usable fuel. `atr42_100`'s payload rows reach 76 lb short of MZFW, so its `mzfw aft` is the rows' extreme, 33,434 lb. The RJ's gross, forward-regardless and `fwd light` cases keep their pre-#424 loadings: re-seeded, NHAA breaks the clamped-case residual ratchet (1.88 % against 1.65 %), so the D-27 guard checks their weight and station only until #422. The MZFW and MLW estimates (`cg_cases`) leave every usable-fuel row out. |
| **D-75.9** | **`minimum_fuel_in_zero_fuel_weight`** (page `weight_mass`) warns on a `MINIMUM` usable-fuel row when an MZFW is stated. |
| **D-75.10** | The code prose that called `MINIMUM` "pilot, reserve fuel" now says crew plus the optional 23.25(b)(3) fuel. |
| **D-75.11** | **`mass_distribution.fuel_basis`** states the minimum-weight rule, the reserve not taken, and the zero-fuel cases run. Where none is run, as on ga6, it says "not run; assumed not critical". The methods statement carries it, so it reaches every report, METHODS.txt and every CSV and deck stamp; WTENV's caption shows it on the Weight & Mass page. |

**Effect** (all LIMIT; the factor is unchanged):
- **Minimum weight:** −700 lb on each ATR, −1,500 lb on the RJ.
- **Gust n at `min weight`:** ATR NLAA −0.61 → −0.656, PNZ 3.41 → 3.471, NNZ −1.41 → −1.47; RJ NMAA/NNZ −1.80 → −1.991, NLAA −0.80 → −0.923, PNZ 3.80 → 3.996.
- **ATR ACRL** (closes at `mzfw aft`): the wing span reacts 0.696 of the aileron moment (was 0.622).
- **Not moved:** ga6's oracle and the Baron.

**Gates (`tests/test_reserve_fuel.py`):**
- **G-75.6:** only ga6 carries `MINIMUM` fuel.
- **G-75.7:** the guard fires by name.
- **G-75.8:** every `mzfw` case has no usable fuel and is ≤ MZFW.
- **G-75.9:** every artifact states the fuel basis, and ga6 states its rule and its assumption.
