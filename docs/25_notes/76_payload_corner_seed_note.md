# Payload corners seeded to the note 75 rule, and a fuel vector per case on the Weight/CG grid (design note 76; #422, #423)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-11-03** (#422, #423; one `changes/` fragment, no history entry). AGREED 2026-11-03 — no code. The owner ruled in session, under the solo profile
(rule 1's working-alone branch): Q1 (a), Q2 yes, Q3 proportional, Q4 parked. PROPOSED the same day.

**Scope.** Note 75 §2 is the owner's payload-case rule. #337 entered the Baron to it by
hand; the seeder (`cg_cases.seed_flight_cases` / `seed_landing_cases`,
`mass_distribution.seed_loading_search`) does not build to it. Its objective is
"the heaviest loading inside the limits" with one row trimmed. This note does three things:
- gives the seeder one corner solver for the rule;
- uses that solver to choose a loading for each envelope limit point;
- draws each case's **fuel vector** (#423, review C5): the CG path from the case's zero-fuel
  loading to the case.

It also re-enters the ATR, the ATR seed and the regional jet, and retires #424's
`_HELD_UNTIL_422` exemption.

Out of scope:
- a tank burn order (Q3);
- seat-row payload databases (Q4);
- the Part 25 landing variant (#411).

`ga6_normal` and `concept_heavy` state no MZFW, so their seeds are untouched and so is the
Appendix A oracle.

Conventions: [`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §3. Every load stays LIMIT,
and no factor moves. The mass SSOT is the item database (plan 11 B1); a loading is an
entered `LoadingDefinition` (D-25), and no ballast is ever solved into a corner.

**Sources** (in `theory_sources.md` at closure):
- 14 CFR 25.321(b)(3): loads "for any practicable distribution of disposable load within
  the operating limitations".
- Lomax (1996):
  - §14.1 p233 (MZFW: zero usable fuel) and Eq 14.1 p234 (payload = MZFW − OEW);
  - §11.4 pp199–202 (MZFW at the forward CG, payload end-loaded);
  - §10.11 p183 and Fig 10.21 p184 (fuel usage drives wing bending).
- Note 75 §2 and §5.

## 1. Measured (prototype solver, 2026-11-03, fixtures at #424)

Each corner either sits on its limit or is at the rows' extreme. The extreme is the
linear-programming fill, aft-most or forward-most rows first. The gap to the limit is in
inches.

| Corner | Baron | ATR 42-100 | ATR 42-300 seed | RJ |
|---|---|---|---|---|
| full fuel fwd (MTOW) | on limit 78.30 | extreme, 3.60 | on limit | on limit |
| full fuel aft (MTOW) | extreme, 0.63 | extreme, 0.64 | on limit | extreme, 0.71 |
| mzfw fwd | extreme 79.61, 2.08 | extreme, 17.97 (33,434 lb, rows 76 lb short) | extreme, 4.67 | extreme, 8.61 |
| mzfw aft | on limit 86.0 | extreme, 5.29 (33,434 lb) | extreme, 8.97 | extreme, 7.64 |
| MZFW payload + fuel at MTOW, fwd / aft | 1.41 / on | 17.83 / 5.43 | 5.73 / 8.78 | 7.72 / 7.55 |
| MZFW payload + fuel at MLW, fwd / aft | 1.70 / on | 17.86 / 5.40 | 5.53 / 8.81 | 8.25 / 7.60 |

The MZFW payload is 93–97 % of every seat and hold on the two types, so it leaves no
freedom to move the CG. These airplanes reach their certified limits only with partial
payloads, which is true of the types and not a defect of the solver. On the Baron the
solver reproduces #337's hand-entered corners to 0.01 in.

## 2. Decisions

| # | Decision | Rationale |
|---|---|---|
| **D-76.1** | **One corner solver**, `mass_distribution.payload_corner(project, weight_lb, fuel_lb, edge)`. Fuel is spread over the consumable usable-fuel rows in proportion (the G-5 rule). The payload is `weight − OEW − fuel`, placed with **at most two discretionary rows part-filled**, mirrored pairs kept whole, so the CG sits on the edge's limit at that weight. When no such placement exists, the CG is the rows' extreme at that weight, and the gap is stated in `trimmed`. When the payload exceeds the rows, the weight is the rows' total, stated. Never ballast. | Note 75 §2. Two equations (weight and moment) need two free rows. Over that set the extreme is the LP vertex, so the test can compute it independently. |
| **D-76.2** | **The corner cases**, written when an MZFW is entered (D-63.5's skip rule kept): `full fuel fwd` (new), `full fuel aft`, `mzfw fwd` and `mzfw aft`, each from D-76.1. "Full fuel" is the tanks' capacity, or `MTOW − OEW` when that is less. | Note 75 §2's four corners. `full fuel fwd` was missing. |
| **D-76.3** | **The envelope limit points keep their weight and station**: the D-27 flight points and the three roled GROUND cases (FLTLOADS' and LANDLOAD's corners, note 75 §2). What changes is the **loading** each one carries. It is the first of these that lands on the point within `_CG_MATCH_TOL`: (1) the MZFW payload plus fuel to the point's weight; (2) full fuel plus the least payload; (3) the D-27 search with its ballast, flagged as today. | 25.321(b)(3): a real loading where one exists. The point stays where certification puts it (Q1). On the RJ this replaces the three gross cases' ballast loadings with no-ballast ones. |
| **D-76.4** | **Fuel vector**, `mass_distribution.fuel_vector(project, case) -> List[(weight_lb, x)]`. It starts at the case's own loading with every usable-fuel row off, then scales those rows together from 0 to the case's fractions in 10 steps (11 points). A case with no usable fuel aboard returns one point. | The path a refuelling or a burn draws on the envelope. It shows the zero-fuel end of every case (note 75 §5) next to the case. |
| **D-76.5** | **Drawn once**: `report/content.weight_cg_plot_data` adds one dotted series per case that carries fuel. The GUI's pre-run figure and both reports read that owner (`report/figures.py`), so they gain the vectors together. | OR-7: one producer per figure. |
| **D-76.6** | **Re-entered to the rule**: `atr42_100`, `atr42_300_seed`, `concept_regional_jet`. `_HELD_UNTIL_422` is deleted. The Baron's corners are re-seeded and must come out as entered (G-76.1). Its `fwd max landing` moves onto the limit (Q1 (a)). | #422. One digest wave. |

## 3. Gates

| Gate | Statement | Expected numbers |
|---|---|---|
| **G-76.1** | The solver reproduces the Baron's #337 corners. | `mzfw fwd` 5,270 @ 79.61; `mzfw aft` 5,270 @ 86.00; `full fuel aft` 5,500 @ 85.37; full fuel fwd 5,500 @ 78.30; all ±0.01 in. |
| **G-76.2** | Every corner case on every MZFW fixture: no ballast row, no usable fuel at `mzfw`, at most two part-filled rows. Its CG is either within `_CG_MATCH_TOL` of the limit or equal (±0.01 in) to the LP extreme, which the test computes on its own. | §1 table. |
| **G-76.3** | Every limit point keeps its entered weight and station. Its loading is the first match of D-76.3 (1)–(3), named in the case's note. | RJ `fwd gross` takes (2); no RJ gross case carries ballast. |
| **G-76.4** | The clamped-case residual ratchet (1.65 %) holds on the re-entered RJ, with no exemption. | NHAA ≤ 1.65 % (1.88 % on the #424 re-seed). |
| **G-76.5** | Fixtures with no MZFW are unchanged. | ga6 and `concept_heavy` seeds byte-identical; every Appendix A oracle green. |
| **G-76.6** | A fuel vector ends on its case (`case_loading_checks` tolerance) and starts at the zero-fuel loading. Weight is monotone along it. A case with no fuel aboard gives a single point. | Baron `aft gross`: 5,270 → 5,500 lb. |
| **G-76.7** | `weight_cg_plot_data` carries one vector per fuelled case, in both unit systems. The GUI figure and the report figure are the same `PlotData`. | ATR 42-100: every fuelled case. |

**Measured at closure:**
- **Corners:** as §1. `atr42_100`'s two zero-fuel corners are one point, so `mzfw fwd` is not written. The ATR seed's and RJ's `mzfw fwd` hold MZFW at the rows' extreme.
- **In-memory ga6 with an MZFW of 2,913 lb:** writes no corner. Every zero-fuel loading lies aft of the aft line (85.36 against 85.09).
- **Baron `fwd max landing`:** 79.67 → 77.96 on the limit (full fuel + least payload). VNP 6,383 → 6,667 lb and DNP 2,402 → 2,508 lb (+4.4 %); the main peaks hold.
- **RJ:** `fwd gross` takes full fuel, no ballast. NHAA's tie moves to sea level (case 28, past the 20° stop) with a clamped residual of 1.877 %. The owner ruled the per-case ceiling re-measured, as recorded, under the 2.5 % hard ceiling.
- **ATR seed:** NHAA moves to `mzfw fwd` (0.190 % / 1.46 %). PHAA and NHAA there run the elevator past both stops, flagged (note 73).
- **Fin cases:** fin loads and Ny hold on every fixture; the angular accelerations move with the loadings.

## 4. Questions

| # | Question | Recommendation |
|---|---|---|
| **Q1** — ruled **(a)** | Do the landing and gross cases stay **on the envelope limits** with a loading chosen per D-76.3, or **follow the MZFW payload plus fuel** wherever that puts them, as #337 entered the Baron's landing cases? | **(a) Stay on the limits.** Measured above, following the payload puts the ATR and RJ landing cases 5–18 in inside the forward limit. That lightens the nose gear against today's seed, which is unconservative. MZFW payload + fuel is still each point's first-choice loading, and the fuel vector shows its path. The Baron's `fwd max landing` moves 79.67 → 77.96 in (on the limit). |
| **Q2** — ruled **yes** | The loading order at a limit point: MZFW + fuel, then full fuel, then the ballasted search? | **Yes.** MZFW + fuel has the least wing-fuel relief (Lomax Fig 10.21), so it is the wing-bending side; full fuel is the next real loading; ballast comes last and is flagged. |
| **Q3** — ruled **proportional** | Spread fuel over the tanks in proportion, or add a per-tank burn order (a schema field)? | **Proportional now.** It is the G-5 rule the GROUND burn-down already uses. Filed as #425 (Lomax §10.11): every shipped twin has one tank per side, so a burn order moves nothing on them. |
| **Q4** — **parked** | Split the fixtures' 24-seat cabin rows into seat rows so the corners can reach their limits? | **No, parked.** Splitting into 4-abreast rows at 30 in pitch moves the MZFW corners by at most 0.45 in (ATR seed `mzfw fwd` 4.67 → 4.22; ATR 42-100 and RJ 0). It gives `full fuel aft` the limit on the ATR and RJ (0.6–0.7 in). Both are below the rows' own placement uncertainty. |
