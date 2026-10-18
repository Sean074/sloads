# Weight & Mass Properties page — critical review (2026-10-17)

**Scope.** The oracle GUI's `weight_mass` step (WTESTIMA + WTONECG + WTENV) as
rendered on `dev/v0.9.0` at 6105658, walked on `atr42_100` with the other four
fixtures checked in code. Part 1 is the open-issue inventory the owner asked
for; part 2 is the review proper: data, interface, capability, and the mass
data that lives on other pages. Findings are numbered for filing (CLAUDE.md
rule 5); nothing here is filed yet.

**Method.** Page walked in the browser (every group, the two figures, the three
result blocks); `field_registry` rows for the page and every mass row on any
other page listed; the five fixtures' weight databases compared with the
engine, gear and fuselage mass typed elsewhere; the WTONECG, WTENV and WTESTIMA
outputs dumped; `validation.consistency_warnings` and the
`mass_distribution` checks run on all five.

---

## Part 1 — open issues that touch the page

Direct (the page's own data or widgets):

| Issue | Tier / band | What it is, for this page |
|---|---|---|
| #337 | S, tag E, unbanded | `baron_58` has no `MINIMUM` crew row: minimum flight weight and `aft max landing` fly with nobody at the controls. Proposes a split row and a "no crew in MINIMUM" guard. Fixture data entered on this page's Items grid. |
| #111 | L, band C, 1.0.0 | Wing fuel is a WINGINER point mass. The fix the backlog names (row 24) is a spanwise extent on the **item row** (`y_span` beside `carriage`), i.e. a new Items-grid column. The park condition (point-vs-band measured on the ATR) was never met. |
| #339 | M, 0.9.0 | Validation warnings ignore the SI toggle. This page's `envelope_point_unreachable`, `case_loading_search_missed` and `cg_case_loading_echo` all print lb and in. |
| #29 | S, band B2, 0.9.0 | The GUI review umbrella. This document is its Weight & Mass chapter. |
| #246 | M, band B2, 0.9.0 | Item 1: WTESTIMA's whole output has no home in the report and no registered exclusion. The page runs it and shows it; the report does not. Item 4: WINGINER's root/tip densities. |
| #362 | unbanded | Overturn guideline 55°, not 63°. The tip-back / overturn figures are computed from `Project.mass.cases[0]` (finding A1 below) and the 2026-08-16 review ruled they belong on this page (GR-GEAR-16/17). |

Indirect:

| Issue | Relevance |
|---|---|
| #218 | A fore-aft inertia term at Nx would read the mass distribution this page owns. |
| #348 / #355 | Every field classified in a published schema: the 14 Items columns and 22 CG-case fields are the largest single block. |
| #359 | Slimming the backlog file; the mass rows there (row 24) move to issue bodies. |

Parked (`02_parked.md`), relevant and still correct to park:

- **M4-4 — per-CG precise inertia in SELECT.** The rod estimate exceeds the
  database Iyy by +32 % on the ga6. Finding A1 is the prerequisite it waits on.
- **CG-dependent MTOW** (non-flat envelope top edge). Needs an input-form
  decision; nothing below depends on it.

**Nothing open covers**: a mass three-view, per-loading-case mass properties,
the engine/gear weight duplication across pages, or the missing CG-case seed
in this GUI. Those are the new findings.

---

## Part 2 — the review

### 2.0 What the page is today

One flat scroll, seven registry groups in registry order, then figures, then
results:

1. **Weight** — MTOW, MLW, ✦MZFW.
2. **Estimation** — the ten WTESTIMA fields (engine count and horsepower
   marked as also held elsewhere).
3. **Items** — the weight database, a `st.data_editor` grid of 14 columns
   (name, weight, x, y, z, ixx, iyy, izz, kind, component, ✦consumable,
   ✦usable_fuel, ✦wing_fraction, ✦carriage) with a row counter and the
   "Seed N rows from the estimate" button.
4. **Envelope** — the ten WTENV fields (gross weight, MAC, XLEMAC, nose and
   tail station all blank-derives with the live value shown).
5. **CG Cases** — one expander per case (11 on the ATR) holding the six case
   scalars, the nested **Loading** (aboard multiselect, a fraction widget per
   consumable or discretionary row, the D-25a echo sentence) and the nested
   **Ballast** record (14 editable fields), followed by the read-only
   **Mass cases** table.
6. **Wing weight (SELECT fuselage conditions)** — the 0.09 × MTOW stand-in
   override.
7. **Tail Mass** — rows for the empennage surface-mass override and the
   control-load bridge fields.

Figures (pre-run): the weight / CG envelope (both loading edges, the limit
polygon, every case marked) and item weight against station. Results:
WTONECG (one condition, 15 values), WTESTIMA (four groups, with the
"nothing reads these figures" advisory and the estimate-vs-entered comparison),
WTENV (five conditions).

What works well and should be kept: the OV-1 blank-derives captions with the
live value; the Mass cases table (one row per case, source stated); the
loading echo sentence; the seed-from-estimate contract (adds, never deletes);
the two figures sharing their owners with the report.

### 2.1 Data and correctness findings

**A1 — The page's only mass-properties result is for a loading that cannot
fly.** `weight_onecg.run` emits one condition, "Weight, centre of gravity and
inertia for one loading", over **every** item in the database. On the ATR that
is 43,308 lb against an MTOW of 36,817 lb: full fuel and full payload at once,
6,491 lb over the design weight, which G-14 already calls the database
*ceiling* and not a loading. The Ixx / Iyy / Izz / Ixz printed on the page and
in the report §2.2 therefore belong to no case. The same single row is
`Project.mass.cases[0]`, and it is read by:

- `configuration.cg_estimate` → tip-back, overturn and static margin on the
  Geometry page (at the 43,308 lb CG);
- `cg_cases.seed_landing_cases` (waterline placeholder only, D-26a);
- the report's mass-properties table.

SELECT's 23.443 Izz does **not** read it (blank `vtail.izz_slugft2` falls to
the rod estimate, +49 % on the C210 per C210-25), and ONENGOUT reads the
mass-basis FLIGHT loading instead (#333) — so one module already does what the
page should. Every CG case has a loading of record (entered or searched, the
Mass cases table lists it), and `mass_distribution.loading_mass_state` plus
`weight_onecg.weights_and_inertia` over that loading's items is the per-case
answer. **Recommendation (tier L, design note):** WTONECG emits one condition
per CG case, gear down, with the itemized total kept and labelled *database
ceiling*; `MassResult.cases` carries the per-case rows (its docstring already
calls this "a later refinement"); `cg_estimate` reads a named case; SELECT's
Izz and the vtail `izz_slugft2` default read the case's inertia (closes
M4-4's prerequisite). Oracle lock: the ga6 p136 figures are the itemized total
and stay as the ceiling row.

**A2 — Engine and propeller mass is typed twice and the link that reconciles
them is unused on every fixture.** `engines[].engine_weight_lb` /
`prop_weight_lb` are entered on Engine Mount Loads; the database carries the
same masses as rows; the `engine_mass_item` / `prop_mass_item` selectors
(note 36 OV-7) are blank on all four fixtures that have engines, so
`engine_mass_row_mismatch` can never fire. Measured:

| Fixture | Typed per engine | Database rows | Gap |
|---|---|---|---|
| ga6_normal | 505 / 74 | Engine install 505, Propeller 74 | none |
| atr42_100 | 890 / 310 | Engine L/R 890, Propeller L/R 310 | none |
| baron_58 | 433 / 82.5 | Engine L/R 433, Propeller L/R 82.5 | none (accessories 60 + 40 per side outside both) |
| concept_regional_jet | 1,550 / 0 | "Engines installed (2)" 3,400 at **y = 0** | 150 lb per engine, undetected; and a rear-fuselage twin's engines on the centreline, so Ixx carries no engine term |

The 2026-08-16 user review found this class (N1 instance 5, 300 lb apart then)
and ruled "engine mass → weight DB, L, note first"; the selector shipped, the
move did not. **Recommendation:** fixtures set the selectors (tier S, data);
a validation warning when an engine's selector is blank and a database row
name contains the engine label (tier S); the move itself is a design-note
item (see 2.4).

**A3 — Gear leg weight is typed on Geometry with no link to the database and
no check.** `geometry.landing_gear.{main,nose}_gear.weight_lb` feeds the gear
free body's inertia term. Against the database rows:

| Fixture | Typed main leg | Database main gear | Reading |
|---|---|---|---|
| ga6_normal | 77.5 | 45 + 110 = 155 | per leg, consistent |
| atr42_100 | 525 | 1,250 | per leg would be 625: **100 lb apart** |
| baron_58 | 150 | 75 L + 75 R | typed value is **both legs**, convention inverted |
| concept_regional_jet | 575 | 1,150 | per leg, consistent |

Nothing can see this today. **Recommendation:** a `gear_mass_item` selector
per leg on the OV-7 pattern, or derive the leg weight from gear-tagged rows
with the typed value as the override; and a reconciliation warning either way
(tier M; the inconsistent fixtures fixed in the same change, rule 4).

**A4 — Three fixtures carry stale entered fuselage station tables.**
`fuselage_mass.stations[]` is not marked override on any fixture, so the
derived table governs and the entered one is inert, but it sits in the file
and on the Fuselage Loads page looking like data: ga6 −492 lb, Baron
−1,089 lb, RJ −12,600 lb short of the non-wing items (`mass_fuselage_reconcile`
fails on all three). The warning renders on the Fuselage page, not here.
**Recommendation:** delete the stale tables from the fixtures (tier S) and show
the reconciliation on this page (B3).

**A5 — Item own-inertia is mostly absent and nothing says so.** Rows with any
ixx/iyy/izz: ga6 11 of 24, Baron 3 of 36, ATR 0 of 26, RJ 0 of 15,
concept_heavy 0 of 14. The ga6 oracle *depends* on these (IXX 1201.527 needs
them, registry note), so an airplane whose Ixx is transfer-only is a different
quality of answer. **Recommendation:** WTONECG states the own-inertia share
(Σ own / total, per axis) as a value, and the page caption names
"transfer-only" when it is zero (tier S).

**A6 — Butt lines are zero on every row of two fixtures.** ga6 (a single: fine)
and the RJ (a twin with wing-mounted gear: not fine). Together with A2's
centreline engines the RJ's Ixx is understated. Data; rides A2.

**A7 — #337** (Baron crew row) stands as filed.

**A8 — Engine count held twice by hand.** `weight.estimation.engine_count`
beside `len(Project.engines)`; the page says "the two must be kept in step".
The registry already marks it `governs`; the `concept_heavy` 2-vs-0 instance
is the precedent. **Recommendation:** derive it, typed value as override
(OV-1), tier S.

**A9 — WTENV's "Maximum loading weight" row is the ceiling labelled as a
loading.** Same number as A1 (43,308 lb). Rename the value "Database ceiling
(every row aboard)" in the summary condition (tier S, digest re-pin).

### 2.2 Interface findings

**B1 — The Items grid has no totals.** Fourteen columns, horizontal scroll,
five orthogonal tags per row, and the only sums are WTENV's results three
screens below. **Recommendation:** a totals strip directly under the grid —
empty / minimum / discretionary / ceiling weight with each CG, row counts per
kind, and the MTOW, MLW, MZFW chain check beside them — read from
`WeightInput.database_totals` and the ordering check in `validation` (tier S).

**B2 — The per-component partition is computed and shown nowhere.**
`mass_distribution.component_summary` (wing / fuselage / htail / vtail: items,
weight, % of W, X and Z CG) has a test and no GUI caller since the front-end
retired at #270. **Recommendation:** render it under the Items grid as a
`GROUP_TABLES` entry (tier S).

**B3 — The mass-model checks render on the pages that read the mass, not the
page that edits it.** `wing_mass_tie`, `fuselage_reconciliation`,
`tail_reconciliation`, `untagged_tail_surfaces`, `unplaced_items` are shown on
the Fuselage and Wing Loads pages. **Recommendation:** one "Mass model checks"
block on this page listing every check with its state (tier S; B2 and B3 are
one change).

**B4 — The CG-case editor is heavy.** Eleven expanders on the ATR, each with
the aboard multiselect, a fraction widget for every consumable *and* every
discretionary row whether aboard or not (six on the ATR; the Baron's database
would show more), and a 14-field Ballast record of which ten are fixed by
D-25's semantics (kind must be discretionary, component fuselage, not
consumable, not usable fuel, no wing fraction, panel carriage) yet render as
editable. The Mass cases summary comes *after* the eleven expanders.
**Recommendation (tier M):** Mass cases table first; fraction widgets only for
rows aboard; the Ballast record shows name, weight, x, y, z and inertia with
the fixed tags stated in the caption rather than offered.

**B5 — There is no way to seed the CG cases in this GUI.** `cg_cases.
seed_flight_cases` and `seed_landing_cases` (the WTENV corner cases plus the
MZFW trio; the three roled landing cases) have **no caller** in `sloads/`,
`app_shell/`, `oracle_app/`, `scripts/` or `cli.py`. PROGRAM_SPEC §LANDLOAD
says the seed is "offered on that tab as a button" — that was the retired
front-end. A new project's user types every case and every loading by hand.
**Recommendation:** a `TABLE_SEEDS` entry for `weight.cg_cases[]` on the
existing items-seed contract (adds, never deletes, plan caption first), tier S
to M; the spec sentence corrected in the same change.

**B6 — Figures.** The envelope has a station axis only although every limit
is entered in % MAC; a second axis or % MAC tick labels would let a reader
check the entered limits against the drawing. Case markers overlap at the
corners (fwd regardless / fwd light share a point by design, mzfw fwd sits on
fwd gross's weight). The item-station figure is one-dimensional (x only); C1
replaces it.

**B7 — The cross-page caption is stale.** The page says "These numbers also
read engines (entered on Engine Mount Loads)". The `engines[]` rows are entered
on Geometry since note 69 D-69.14; the caption resolves `reads=("engines",)`
through Engine Mount's `edits=("engines",)`. Tier S, workflow declaration.

**B8 — The standard doc describes a page that no longer exists.**
GUI_design.md §3 gives this page "tabs: Estimate · Weight, CG & Inertia ·
Payload Cases · Weight / CG Envelope"; PROGRAM_SPEC §WTONECG says `mass` is
produced by "the Weight, CG & Inertia tab's Apply weight items handler
(M4-17a)". The oracle GUI renders one flat scroll and `refresh_mass` runs on
every render. Tier S, docs.

**B9 — The SELECT wing-weight stand-in ignores the database.** 0.09 × MTOW
(3,314 lb on the ATR) while the wing-tagged rows sum to 3,500 lb. OV-1: derive
from the `WING` rows, stand-in as the fallback when none are tagged, typed
value as override (tier S to M; SELECT fuselage digests move).

**B10 — Tail Mass shows nothing until a row exists.** The derived
`derived_tail_surface_weight` per surface is the number a user wants to see
before deciding to override it. Show it in the empty-table note (tier S).

**B11 — SI** is #339.

### 2.3 Capabilities to add

**C1 — A mass three-view ("bubble" view).** The retired front-end overlaid a
marker per `weight.items` row on the Configuration three-view (D4.6, changelog
to 0.8.2); it went with the front-end at #270, and note 69's new airplane
three-view (D-69.15) deliberately draws airframe, controls, engines and gear
only. There is no picture anywhere of **where the mass is** in y or z, which
is exactly what A2/A3/A6 would have shown at a glance. **Proposal (tier M, no
physics):** a figure family `mass_three_view` (plan, side, front) on
`weight_mass`, stage PRE_RUN, built on `oracle_sections.airplane_view_figures`'s
airframe series, adding:

- one circle per item, area proportional to weight, marker shape by `kind`
  (the item-station figure's rule) and colour by `component`, name on hover;
- the itemized CG and every CG case's CG as distinct markers (side and plan);
- the structural CG limits as a station band (side and plan);
- the fuselage outline extent, so `mass_item_outside_body` is a thing a
  reader sees.

`PlotData.Series` carries `marker` and `labels` but no per-point size: a
`sizes` member is the one model addition, with the Plotly and TikZ renderers
reading it. Report §2.2 prints the same three frames after the envelope.

**C2 — Per-case mass properties table** — finding A1, the table a mass
engineer expects: W, Xcg, Zcg, Ixx, Iyy, Izz, Ixz, principal axis, per CG
case, with the ceiling row last.

**C3 — Gear-geometry figures per CG case here.** Tip-back, overturn and static
margin at each case (GR-GEAR-16/17 and GR-GEOM-7 decided this on 2026-08-16;
blocked on A1). #362's guideline correction rides it.

**C4 — Reachability drawn.** `envelope_point_reach` already computes the CG
interval the database can produce at each weight; draw it as a band under the
limit polygon so an unreachable limit is seen, not only warned (tier S once
B6's axis work is done).

**C5 — Burn-down path per case** on the envelope: the G-5 proportional
fuel-burn trajectory from a case's take-off loading to its zero-fuel state.
Optional; tier M.

### 2.4 Mass data on other pages that belongs here

Owner rulings already on record: GR-INPUT-2 ("all airplane-specific input on
the definition pages; analysis assumptions on the analysis page"),
GR-VTAIL-13 ("move yaw inertia, gross weight to mass properties"), and the
2026-08-16 review's own list "→ Weight & Mass Properties: engine_weight_lb,
prop_weight_lb, hub_weight_lb, prop_inertia — not a plain widget move".

| Path | Page now | Read by | Recommendation |
|---|---|---|---|
| `engines[].engine_weight_lb`, `prop_weight_lb`, `hub_weight_lb` | Engine Mount | ENGLOADS | **Move:** database rows are the owner; the selector (OV-7) becomes the only link and is required when a row matches. Design note first (changes which weight sizes the mount). |
| `engines[].prop_inertia`, `rotors[].weight_lb / inertia / diameter_in` | Engine Mount (rotors JSON-only) | ENGLOADS, OEI | Rotating inertia: **stays** on the engine page, but the rotor weight derives from the selected row. |
| `geometry.landing_gear.*.weight_lb` | Geometry | gear free body | **Link or derive** (A3). The axle geometry stays on Geometry. |
| `geometry.empennage.vtail.gross_weight_lb` | Geometry | SELECT 23.443 | Already derives from MTOW (governs); the typed override, if kept at all, belongs here. |
| `geometry.empennage.vtail.izz_slugft2` | Geometry | SELECT 23.443 | **Move** and derive from the per-case inertia (A1); the rod estimate stays as the fallback, disclosed. |
| `speeds.weight_lb` | Structural Speeds | STRSPEED | Duplicate of MTOW with a drift warning (DS-6). Derive; typed as override. |
| `one_engine_out.izz_slugft2`, `xcg_in` | One Engine Out | ONENGOUT | Overrides of A1's per-case values; keep as analysis overrides, label them as such. |
| `wing_mass.panel_weight_override_lb` | Wing Loads | WINGINER | **Move** beside `tail_mass[]`'s override, the same contract for the same quantity. |
| `wing_mass.tip_root_density_ratio`, `inboard_rib_y` | Wing Loads | WINGINER | The mass *shape*; arguably here with the panel override. Owner call. |
| `fuselage_mass.stations[]`, `stations_are_override` | Fuselage Loads | body_loads | **Move:** a mass-distribution override; the Fuselage page keeps a read-only view as Landing keeps the roled cases. |
| `fuselage_mass.ref_waterline` | Fuselage Loads | beam model | Not mass: the fuselage LRA waterline. Belongs on Geometry with the other LRAs. |

And the converse — on this page but not mass: `tail_mass[].control_load_mode`,
`hinges_span_in`, `actuator_span_in` are control-surface load-path geometry
(note 56's bridge). They belong with the elevator and rudder on Geometry or on
Tail Loads.

### 2.5 Filed (2026-10-17, unbanded — owner to band)

| Issue | Tier | Findings |
|---|---|---|
| #382 | L, note first | A1 per-case mass properties + C2 table + C3 gear figures per case, vtail Izz default, M4-4's prerequisite; #362 rides it |
| #383 | L, note first | §2.4 move table + A2's engine-mass move; the `wing_mass` / `fuselage_mass` override moves may ship ahead as tier M |
| #384 | M, defect | A2 selectors + blank-selector warning, A3 gear link, A4 stale tables, A6 butt lines |
| #385 | S, defect | A5 own-inertia share, A8 engine count, A9 ceiling label, B9 wing-weight stand-in |
| #386 | S | B1 totals, B2 + B3 checks block, B6 axis + C4 reach band, B7 caption, B8 docs, B10 |
| #387 | M | B4 editor slimming + B5 CG-case seed |
| #388 | M | C1 mass three-view (`Series.sizes`); the `item_station` figure retired with it; C5 noted as an unfiled option |

A7 is #337 and B11 is #339, both already open.

Sequence: A1 is the keystone — C2, C3, M4-4 and the vtail Izz all read its
output — and the three-view (C1) is the cheapest way to make A2/A3/A6-class
data errors visible before the next fixture is entered.
