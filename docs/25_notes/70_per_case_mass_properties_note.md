# Mass properties per CG case: WTONECG reports every loading of record, and the all-items total becomes the labelled database ceiling (design note 70)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-10-17** (#382 closed in one tier-L step on `dev/v0.9.0`,
schema v78). AGREED the same day (owner, in session, under the solo profile —
rule 1's working-alone branch). PROPOSED the same day; the owner ruled Q1–Q5
of §3 **as recommended**, so D-70.1…D-70.9 stand as written. Drafted for
**#382**, band B2 Pri 3, from the Weight & Mass Properties page review
(`docs/50_reviews/2026-10-17_weight_mass_page_review.md`, findings A1, C2,
C3).

**Tier L.** Schema change (v77 → v78: `MassCase` gains one field, §2 D-70.3);
WTONECG emits one condition per CG case instead of one; `Project.mass`
carries the per-case rows; two readers of `mass.cases[0]` change what they
read. **No delivered load moves** (G-70.6): no load module reads
`Project.mass` — SELECT's inertias are the rod estimates or the typed
override, ONENGOUT already computes its own per-case inertia (#333), LANDLOAD
and FLTLOADS read the CG cases. What moves is what the page, the report §2.2
table and the Geometry page's gear-geometry figures *say*, and the
`weight_onecg` txt/csv digests on every fixture plus `configuration`'s on the
four with gear geometry (one digest wave; neither is a load module).

**Conventions:** `CONVENTIONS.md` §2 (stations, butt lines, waterlines in
inches; inertias in lb-in² in the database, slug-ft² reported) and §7 (single
owners: this note adds one row, the mass-properties owner, §4). **Theory:**
no new physics — WTONECG.BAS lines 657–910 (Appendix C p377–381) applied to a
subset of the rows instead of all of them; the equations are untouched and
the Appendix A p136 oracle stays as the ceiling row (G-70.1).
**Precedent:**
- #333 ruling 4 (`one_engine_out.mass_basis` / `_mass_state`): the inertia a
  case is sized at comes from *that case's loading* through
  `weights_and_inertia`, "rather than to every database row"; falling back to
  the all-items loading "would size them above MTOW without saying so";
- G-14: `Σ items` is the database **ceiling**, not a design weight;
- note 63 D-25: every CG case has a loading of record — entered, or searched
  by `mass_distribution.derive_case_loadings`;
- `MassResult`'s own docstring: "Carries the weight/CG/inertia of each
  structural-limit loading (up to the four CG cases x gear up/down)" — the
  shape this note finally gives it; `build_mass`: "the full per-CG-loading set
  … is a later refinement"; `cg_estimate`: "once that lands this should pick
  the representative case rather than always the first".

---

## 1. Measurements (2026-10-17, `dev/v0.9.0` at 6105658)

### 1.1 What `Project.mass` holds today, against the design weight

`weight_onecg.build_mass` sums **every** `weight.items[]` row into one
`MassCase("itemized loading")`. `weight_onecg.run` emits the same sum as the
one condition "Weight, centre of gravity and inertia for one loading".

| Fixture | MTOW (lb) | `mass.cases[0]` weight (lb) | Over MTOW | Is it a loading? |
|---|---|---|---|---|
| ga6_normal | 3,400 | 3,400 | 0 | yes — Appendix A's own database sums to the aft-gross loading (p136) |
| baron_58 | 5,500 | 6,540 | +1,040 (+19 %) | no |
| atr42_100 | 36,817 | 43,308 | +6,491 (+18 %) | no — full fuel and full payload at once |
| concept_regional_jet | 33,000 | 34,800 | +1,800 (+5 %) | no |
| concept_heavy | 18,000 | 18,000 | 0 | yes (one case, every row aboard) |

The ga6 coincidence is why the oracle test passes and why nobody saw this:
on the Appendix A airplane the ceiling *is* a loading.

### 1.2 Who reads it

| Reader | What it reads | Effect today |
|---|---|---|
| `configuration.cg_estimate` (`configuration.py:555`) | `mass.cases[0].cg_x / cg_z`, label "Weight DB" | tip-back, overturn and static margin on the Geometry page and in the report are drawn at the 43,308 lb CG on the ATR, a CG no loading has |
| `cg_cases.seed_landing_cases` (`cg_cases.py:343`) | `mass.cases[0].cg_z` | the waterline placeholder the landing seed searches from (D-26a) |
| report §2.2 `oracle_sections._weights` | every `weight_mass` condition | one table titled "Mass properties" — the ceiling's Ixx/Iyy/Izz/Ixz with no case name |
| `oracle_app.results.select_inertia_advisory` | `max(mass.cases, key=weight)` | quotes "WTONECG's item-database inertias at the heaviest loading (itemized loading)" against the rod estimates |
| `landing.py:794`, `workflow.py:227`, `inputs.py:1898` | — | docstrings stating that LANDLOAD / the CG cases *no longer* read it |
| SELECT (`select.py:1507`) | **nothing** — `vt.izz_slugft2 or _default_izz(...)` | `PROGRAM_SPEC.md` §SELECT "Reads: `Project.mass` (WTONECG inertia)" is wrong today (§2 D-70.8) |
| ONENGOUT (`one_engine_out._mass_state`) | **nothing** — recomputes per case | the pattern this note generalizes |

### 1.3 Per-case mass properties, as `weights_and_inertia` over each case's loading of record

`derive_case_loadings(project, project.weight.cg_cases)` → `weights_and_inertia(loading.items)`;
slug-ft²; every fixture, FLIGHT and GROUND cases alike.

**atr42_100** (ceiling: W 43,308, X 401.2, Ixx 160,965, Iyy 85,431, Izz 224,883)

| Case | W (lb) | Xcg (in) | Ixx | Iyy | Izz |
|---|---|---|---|---|---|
| aft gross | 36,817 | 404.11 | 160,602 | 81,988 | 221,803 |
| fwd gross | 36,817 | 386.22 | 160,602 | 116,032 | 255,847 |
| mid gross | 36,817 | 395.17 | 160,602 | 85,610 | 225,425 |
| full fuel aft | 36,817 | 403.31 | 160,690 | 81,306 | 221,033 |
| mzfw aft | 33,510 | 403.69 | **34,855** | 81,115 | 99,163 |
| fwd regardless | 30,000 | 381.75 | 34,612 | 67,293 | 85,583 |
| mzfw fwd | 28,054 | 382.39 | 34,612 | 67,255 | 85,545 |
| min weight | 23,374 | 390.67 | 34,448 | 64,464 | 82,918 |
| aft max landing (GROUND) | 36,155 | — | 160,6xx | 83,108 | 222,923 |
| fwd max landing (GROUND) | 36,155 | — | 160,6xx | 127,541 | 267,526 |
| fwd light (GROUND) | 30,000 | — | 34,612 | 67,293 | 85,584 |

The number that matters: the ATR's **Ixx is 160,600 with wing fuel aboard and
34,600 without** — a factor of 4.6 — and the single ceiling row shows the
first for every case. Iyy spans 64,464 → 127,541 across cases (×2.0).

**baron_58** (ceiling: W 6,540, Ixx 4,812, Iyy 3,258, Izz 7,861)

| Case | W | Ixx | Iyy | Izz |
|---|---|---|---|---|
| aft gross | 5,500 | 4,809 | 2,566 | 7,172 |
| fwd gross | 5,500 | 4,809 | 2,333 | 6,939 |
| mzfw aft | 5,270 | 3,405 | 2,727 | 5,932 |
| mzfw fwd | 4,590 | 3,403 | 2,263 | 5,470 |
| aft / fwd max landing, fwd light (GROUND) | 5,400 / 5,400 / 4,440 | — | 2,566 / 2,381 / 2,138 | 6,977 / 6,501 / 5,345 |
| fwd regardless | — | **not derivable** ("no combination of discretionary items reaches this weight and CG") | | |

The ceiling's Iyy (3,258) is 27 % above the heaviest real loading's (2,566).

**concept_regional_jet** (ceiling: W 34,800, Iyy 214,874, Izz 209,381): seven
FLIGHT and three GROUND rows derive; Iyy spans 169,484 (min weight) →
271,837 (fwd regardless), and the ceiling sits *inside* the range — a reader
cannot even tell from it which way a case moves. **ga6_normal**: CG1–CG4 plus
the three landing cases derive; CG1 (3,400 lb, X 85.10, Ixx 1,205.3) is the
searched loading and differs from the all-rows oracle (X 84.999, Ixx 1,201.5)
by the search's own tolerance — the oracle row is the ceiling row and stays
pinned as it is (G-70.1). **concept_heavy**: the one case equals the ceiling.

### 1.4 The rod-estimate Izz SELECT uses, against the per-case value (for Q2)

| Fixture | `select.default_side_gust_izz` | aft-gross loading Izz | Rod over database |
|---|---|---|---|
| ga6_normal | 4,173 | 3,025 | +38 % |
| baron_58 | 8,555 | 7,172 | +19 % |
| atr42_100 | 335,527 | 221,803 | +51 % |
| concept_regional_jet | 384,316 | 224,185 | +71 % |

Same class as C210-25's +49 % and M4-4's +32 % / +123 % on Iyy. The side-gust
fin load's dependence on Izz is through the radius of gyration
`k = √(Izz / (W/g))` (`select._vt_side_gust_terms`), so the rod estimate is
conservative on every fixture, and the ga6 SELECT oracle is computed *with*
the rod value. Switching the default is an oracle deviation (M4-4's park
reason), which is why §2 does not switch it.

## 2. Decisions (D-70.1 … D-70.9)

**D-70.1 — One mass-properties row per CG case, FLIGHT and GROUND alike, plus
the ceiling.** `weight_onecg.run` emits one `ConditionResult` per
`weight.cg_cases[]` entry whose loading of record is derivable, titled by the
case name (`"Mass properties -- aft gross"`), computed by the unchanged
`weights_and_inertia` over `derive_case_loadings(project, cases).items`, in
case-entry order; then one final condition, the all-rows sum, titled
**"Database ceiling (every row aboard)"**. A case whose loading is not
derivable gets no row and one stated reason in the module's notes (the
`SkippedCondition` idiom; Baron's fwd regardless), never an invented row.
`build_mass` / `refresh_mass` persist the same set into `Project.mass.cases`
— the ceiling row **last**, so `cases[0]` is the first CG case, not the sum.

**D-70.2 — One owner for "the mass properties of case X".** A new
`weight_onecg.case_mass_properties(project) -> List[MassCase]` (the
per-case rows + the ceiling, same function `run` and `build_mass` call) is the
single owner; `one_engine_out._mass_state` reads its basis case's row through
it rather than calling `weights_and_inertia` itself (identity, G-70.3). The
derivation of the loading stays `mass_distribution.derive_case_loadings`
(note 63); this note adds no second loading search.

**D-70.3 — `MassCase.ceiling: bool = False`** (schema v77 → v78). The ceiling
row is identified by a typed field, never by its name (note 63 OV-1: a
meaning is a field, not a name match). Migration: a v77 `mass` block is
discarded and re-derived on load — `Project.mass` is derived data
(`derived.py`: "WTONECG over `weight.items` and nothing else"), so nothing is
lost; the five bundled examples are re-stamped. `gear_down` stays `True` on
every row: the database has no gear-up position, so the gear-up variant the
`MassResult` docstring promised is **parked** here as a stated limitation,
not an open promise (Q4).

**D-70.4 — `configuration.cg_estimate` reads a named case, and the
gear-geometry figures go per case (C3).** `_gear_condition` emits tip-back,
overturn and static margin **per FLIGHT and GROUND case** that has a row,
each value row naming its case, and two summary rows naming the governing
case: tip-back **minimum** (the aft-most CG) and overturn **maximum**. The
"Weight DB" fallback order becomes: the per-case rows → the ceiling row,
labelled "database ceiling" → the 25 %-MAC estimate. #362's 55° guideline
rides this (the overturn caption is rewritten anyway). The Geometry page's
figures show the governing case; the report prints the per-case table.

**D-70.5 — `seed_landing_cases` seeds its waterline from the heaviest FLIGHT
row** (the `one_engine_out.mass_basis` pick: heaviest, aft-most on a tie),
falling back to the ceiling row only when no FLIGHT row derives. The
placeholder is still a placeholder (D-26a); it just stops being a waterline
of a loading that cannot fly.

**D-70.6 — The page and report §2.2 print the per-case table (C2).** One
table, one row per case: W, Xcg, Zcg, % MAC, Ixx, Iyy, Izz, Ixz (slug-ft² or
kg·m²), principal Ix/Iz and θ, with the ceiling row last and marked. The
existing `_weights` loop already titles per condition when there are several;
the #232 one-channel-per-system filter applies to every condition. The
`oracle_app.results.select_inertia_advisory` comparison quotes the
**mass-basis FLIGHT row by name** instead of "the heaviest loading".

**D-70.7 — SELECT's Izz default does not switch in this note; the per-case
value is disclosed beside it.** The `geometry.empennage.vtail.izz_slugft2`
registry row's `derived_from` and `select_inertia_advisory` quote the
mass-basis FLIGHT case's Izz as "the database value for *case*", the rod
estimate stays the governing default (oracle lock, conservative sign — §1.4).
M4-4 stays parked with its number; **its prerequisite — a per-case precise
inertia to wire — is delivered by this note**, and the promotion is a
fidelity decision with an `02_approved_corrections.md` entry, not part of
#382 (Q2).

**D-70.8 — `PROGRAM_SPEC.md` tells the truth about who reads `Project.mass`.**
§WTONECG: reads become the CG cases' loadings; "Computed at the 4 CG
locations … so up to 8 loadings, not one" becomes "one row per CG case plus
the ceiling; gear-up parked". §SELECT "Reads: `Project.mass` (WTONECG
inertia)" is corrected to the rod estimate / typed override with the
database value disclosed. §LANDLOAD's `mass.cases[0].cg_z` sentence follows
D-70.5. The M4-17a "Apply weight items handler" sentence (review B8) is
corrected to `refresh_mass` on render in the same touch.

**D-70.9 — The ceiling row keeps the oracle.** `tests/test_weight_onecg.py`
pins Appendix A p136 against `weights_and_inertia(project.weight.items)` —
the ceiling — and is untouched; a new assertion pins that the ceiling row
`run` emits *is* that result (same object path, G-70.1).

## 3. Questions for the owner

| # | Question | Recommendation |
|---|---|---|
| Q1 | Rows for GROUND cases too, or FLIGHT only? | **Both** (D-70.1): the landing cases are loadings of record and the gear figures (D-70.4) are a ground question. |
| Q2 | Switch SELECT's blank-Izz default from the rod estimate to the per-case database value now? | **No** (D-70.7): it is M4-4's oracle deviation (ga6 +38 %, every fixture conservative); deliver the number, disclose it, leave the switch to M4-4 with an approved-corrections entry. |
| Q3 | Gear figures per case (D-70.4), or one figure at a chosen case? | **Per case** with the governing case named; one chosen case re-creates the "which loading is this?" problem. |
| Q4 | Gear-up rows (the `MassResult` docstring's promise)? | **Park, stated**: no gear-up position exists in the database; `gear_down=True` on every row and the docstring says so. |
| Q5 | Schema field `MassCase.ceiling` (v78) versus a reserved name? | **Field** (D-70.3), per note 63 OV-1. |

## 4. Closure gates (G-70.1 … G-70.8)

| Gate | Statement | Where |
|---|---|---|
| G-70.1 | The Appendix A p136 figures (W 3400, XBAR 84.99936, ZBAR 92.57932, IXX/IYY/IZZ/IXZ 1201.527/2058.209/3022.766/134.4063 slug-ft²) are the **ceiling row** `run` emits on `ga6_normal`, ±0.1 % | `tests/test_weight_onecg.py` (existing pins + the ceiling-row identity) |
| G-70.2 | For every fixture and every derivable CG case, the row's W/Xcg/Zcg equal the `CaseLoading`'s own `weight_lb/cg_x/cg_z` and its inertias equal `weights_and_inertia(loading.items)` (identity, rel 1e-9) | `tests/test_weight_onecg.py` |
| G-70.3 | `one_engine_out._mass_state` equals the `case_mass_properties` row of the same case on every fixture with a FLIGHT basis (one owner) | `tests/test_one_engine_out.py` |
| G-70.4 | The ceiling row is last, flagged `ceiling=True`, and its weight ≥ every other row's; a non-derivable case yields no row and a stated reason (baron_58 fwd regardless) | `tests/test_weight_onecg.py` |
| G-70.5 | `cg_estimate` never returns the ceiling CG while a case row exists; the Geometry gear condition names a case on every value row and the governing case on the two summary rows, on every fixture | `tests/test_configuration.py` |
| G-70.6 | **No delivered load moves:** every Imperial digest other than `weight_onecg`'s and `configuration`'s (`txt` and `csv`; neither is a load module — the second carries the per-case gear angles) is unchanged on every fixture; SELECT's Izz on every fixture is unchanged | `tests/imperial_baseline.py`'s frozen digests (one digest wave: 5 + 4 fixtures) + `tests/test_select.py` |
| G-70.7 | SI report §2.2 prints one inertia channel per condition for N conditions (the #232 filter generalizes) | `tests/test_report_si.py` |
| G-70.8 | `PROGRAM_SPEC.md` §SELECT no longer says SELECT reads `Project.mass`; the data dictionary regenerates with `MassCase.ceiling` | `tests/test_doc_currency.py` / `tests/test_data_dictionary.py` |

## 5. Out of scope, stated

- The engine / gear / vtail mass-owner moves — **#383** (note next).
- The mass three-view (**#388**), the CG-case editor and seed (**#387**), the
  page totals and checks block (**#386**): they read this note's rows but do
  not wait on them.
- M4-4 (SELECT's precise inertia) stays parked on its own number; D-70.7
  delivers only its prerequisite.
- Per-case *Iyy* for a checked-maneuver pitching condition: the consumer does
  not exist (parked M4-2's reasoning); the rows are there when it does.
