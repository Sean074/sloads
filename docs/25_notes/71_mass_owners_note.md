# One owner per mass quantity: the engine, gear, tail, wing-panel and fuselage masses typed on other pages, and the fuselage beam waterline (design note 71)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-10-18** (#383 closed in one tier-L step on `dev/v0.9.0`,
schema v80). AGREED the same day (owner, in session, under the solo profile —
rule 1's working-alone branch). PROPOSED the same day; the owner ruled Q1–Q3
and Q6 **as recommended** and **overruled Q4 and Q5** (§3): the wing mass
shape moves to the weight page with a spanwise wing-mass figure added to the
Wing Loads page (D-71.8, D-71.10), and the tail control-load fields move to
the control surfaces' rows on the Geometry page (D-71.9).
Drafted for **#383**, band B2 Pri 9, from the Weight & Mass Properties page
review (`docs/50_reviews/2026-10-17_weight_mass_page_review.md`, §2.4 and
finding A2's move clause). The geometry twin shipped as note 69 (#378); this
is the mass side, and it starts where #384 (the gear link), #385 (the engine
count and SELECT's wing weight) and #382 (per-case mass properties) left the
ground.

**Tier L.** Schema change (v79 → v80, one hop: one field deleted, one field
and three list fields move slice); six registry rows change page; one
STRSPEED input becomes a collapsed override; one figure family is added. **No delivered load moves** on a fully specified project
(G-71.1): every move keeps the governing number and every new derive
reproduces the typed value the fixtures carry today, which §1 measures
field by field.

**Conventions:** `CONVENTIONS.md` §7 (single owners: this note retires one
stored copy, moves one field to its owner's slice and adds one collapsed
override to the OV-1 row). **Theory:** no new physics. **Precedent:** note
39/36 OV-1/OV-7 (falsy derives, typed overrides, the selector link), note 69
D-69.1 (a quantity the entered data determines has one owner; a copy is a
collapsed override where an original-suite program reads it, deleted
otherwise), note 63 OV-1 (a meaning is a typed field), and the owner rulings
on record: **GR-INPUT-2** (2026-08-16: "all the airplane specific input
defined here [the definition pages] — geometry, weights, engine power; any
analysis-specific assumptions on the page for that analysis"),
**GR-VTAIL-13** ("move yaw inertia, gross weight to mass properties"), and the
same review's list "→ Weight & Mass Properties: engine_weight_lb,
prop_weight_lb, hub_weight_lb, prop_inertia — not a plain widget move".

---

## 1. Measurements (2026-10-18, `dev/v0.9.0` after #387)

Each row of the review's move table, re-measured after #384 and #385. "Typed"
is what every fixture carries; "owner" is the number the data base or MTOW
owner gives; a row whose typed value equals its owner on every fixture can
become a derive with no load moving.

| Path | Page | Read by | Typed on the fixtures | Owner's number | Gap |
|---|---|---|---|---|---|
| `engines[].engine_weight_lb` / `prop_weight_lb` | Engine Mount | ENGLOADS | ga6 505/74; ATR 890/310 ×2; Baron 433/82.5 ×2; RJ 1,700/0 ×2 | the selected rows (OV-7, linked on every fixture since #384) | none |
| `engines[].hub_weight_lb` | Engine Mount | ENGLOADS (prop inertia estimate; hub ≤ prop refused, #364) | ATR 120; others blank | no row carries a hub | — (no owner to derive from) |
| `engines[].prop_inertia`, `rotors[].weight_lb / inertia / diameter_in` | Engine Mount (rotors JSON-only) | ENGLOADS, OEI | blank / ATR and RJ one rotor each | rotating inertia is not a mass row | — |
| `geometry.landing_gear.*.weight_lb` | Geometry | gear free body | blank on all four (derive, #384) | the `gear`-tagged rows | closed at #384 |
| `geometry.empennage.vtail.gross_weight_lb` | Geometry | SELECT 23.443 (fin design weight) | = MTOW on all four | `weight.max_takeoff_weight_lb` (collapsed override already, `_mtow`) | none |
| `geometry.empennage.vtail.izz_slugft2` | Geometry | SELECT 23.443 (blank → rod estimate) | blank on all four | per-case Izz disclosed, rod default kept (D-70.7) | — |
| `speeds.weight_lb` | Structural Speeds | STRSPEED W; `cg_cases.max_takeoff_weight`'s fallback | = MTOW on all five | `weight.max_takeoff_weight_lb` (G-14) | none — a copy guarded only by `mtow_representation_drift` |
| `one_engine_out.izz_slugft2`, `xcg_in` | One Engine Out | ONENGOUT (blank → the mass-basis row) | blank | the mass-basis FLIGHT row (#333) | — (an analysis override, GR-INPUT-2's second clause) |
| `wing_mass.panel_weight_override_lb` | Wing Loads | WINGINER | blank on all five | half the WING PANEL rows (D-63.2) | — |
| `wing_mass.tip_root_density_ratio`, `inboard_rib_y` | Wing Loads | WINGINER | 0.9/53 ATR, 0.9/21 Baron, 0.95/23 ga6, 0.35/40 RJ, 0.9/30 heavy | no owner: the mass *shape*, WINGINER.BAS's own prompts | — |
| `fuselage_mass.stations[]`, `stations_are_override` | Fuselage Loads | body_loads (override only) | empty on all five since #384 | `derived_fuselage_stations` | — |
| `fuselage_mass.ref_waterline` | Fuselage Loads | the beam model's LRA (`derived_geometry.fuselage_lra`) | 87.7 ga6, 102.6 Baron, 110.2 ATR, 53.3 RJ; none on heavy | not mass at all: the body beam's waterline | — |
| `tail_mass[].control_load_mode`, `hinges_span_in`, `actuator_span_in` | Weight & Mass | `tail_span` (note 56's hinge/actuator bridge) | no rows on any fixture | not mass: control-surface load-path geometry | — |

Two facts the table settles. First, after #384 and #385 **no mass quantity is
typed apart from its owner on any fixture**: the remaining duplication is
*placement* (a quantity edited on a page that is not its owner's) and one
unguarded copy (`speeds.weight_lb`). Second, two fields on the weight page are
not mass and two fields on other pages are not analysis assumptions, which is
GR-INPUT-2's test for where they belong.

## 2. Decisions (D-71.1 … D-71.9)

**D-71.1 — The rule.** A quantity the weight data base or a design weight
owns has one owner. A field elsewhere that holds the same quantity is a
collapsed override (note 36 OV-1: blank derives, typed governs, the caption
shows the owner's number) rendered **beside its owner**; a field that is not
mass renders on the page whose quantity it is; a field that no program reads
differently from its owner is deleted.

**D-71.2 — `speeds.weight_lb` becomes a collapsed override of MTOW.** STRSPEED
reads `inp.weight_lb or max_takeoff_weight(project)`; the registry row gains
`governs=True` and the `_mtow` resolver; `cg_cases.max_takeoff_weight`'s
fallback to it is retired (its one remaining reader is this derive, the
other way round); `mtow_representation_drift` keeps watching a typed value.
The five fixtures blank it. Appendix A's STRSPEED oracle runs at 3,400 either
way (G-71.1).

**D-71.3 — The engine and propeller masses stay where ENGLOADS asks for them,
derived.** `engine_weight_lb` / `prop_weight_lb` are ENGLOADS prompts and
remain on Engine Mount as the OV-7 collapsed overrides they are; the five
fixtures **blank them** so the rows govern, which is the move the 2026-08-16
review asked for in substance ("not a plain widget move"). `hub_weight_lb`,
`prop_inertia` and the rotor fields are rotating-mass inputs with no row to
derive from and stay typed (GR-INPUT-2: an analysis input on its analysis
page). The `*_mass_item` selectors render in the Geometry page's Engines
section beside the engine's location — the link is part of the engine's
identity, not of the mount analysis — and `engine_mass_row_unlinked` (#384)
keeps a blank selector visible.

**D-71.4 — The fin's design weight is deleted.** `vtail.gross_weight_lb` is a
collapsed override of MTOW that every fixture types at MTOW and no shipped
case overrides; SELECT's 23.443 design weight *is* the airplane's MTOW (G-14).
Schema v80 drops the key; a v79 file whose value differs from its MTOW has
the difference stated once in the migration notes (note 69's D-69.2 pattern).
GR-VTAIL-13's "gross weight to mass properties" is met by the MTOW field that
already lives there.

**D-71.5 — The fin's yaw inertia override moves to the weight page.**
`vtail.izz_slugft2` keeps its slice and its semantics (D-70.7: blank is the
rod estimate, disclosed against the per-case Izz) and changes **page** to
Weight & Mass Properties, in a "Rotating and yaw inertia" group beside the
tail masses — GR-VTAIL-13's "yaw inertia to mass properties". A page change
is a registry edit; `tests/test_field_registry.py` pins the new page.

**D-71.6 — The wing-panel and fuselage-station overrides move to the weight
page.** `wing_mass.panel_weight_override_lb` renders beside `tail_mass[]`
(the same contract for the same quantity: a panel weight the rows derive,
typed to override); `fuselage_mass.stations[]` and `stations_are_override`
render on the weight page as a "Fuselage mass stations" group. Both are page
changes only; the slices and readers are untouched. The Fuselage Loads page
keeps its derived-station results and the `mass_fuselage_reconcile` warning,
and says where the override is entered (the `reads` caption).

**D-71.7 — The fuselage beam waterline moves to the geometry slice.**
`fuselage_mass.ref_waterline` is the body beam's load reference axis
waterline (`derived_geometry.fuselage_lra`, owner ruling 2026-09-07), not a
mass quantity: schema v80 moves it to `geometry.fuselage.beam_waterline_z`,
rendered in the Geometry page's Fuselage section beside the drag waterline,
with `fuselage_lra` reading the new field and the hop carrying the value
(87.7 / 102.6 / 110.2 / 53.3 on the four fixtures that enter it). The beam
model page and every deck are unchanged by value (G-71.1).

**D-71.8 — The wing mass shape moves to the weight page** (owner, Q4:
overruling the draft's "stays"). `tip_root_density_ratio` and `inboard_rib_y`
render beside the panel-weight override in a "Wing mass" group: the three
together state what the wing's mass is and how it is spread, which the owner
rules is mass data, not an analysis assumption. Page change only; the slice
and WINGINER are untouched.

**D-71.9 — The tail control-load geometry moves to the control surfaces'
rows on the Geometry page** (owner, Q5: "they define geometry that is to be
used in the beam model"). `control_load_mode`, `hinges_span_in` and
`actuator_span_in` leave `tail_mass[]` for the elevator's and rudder's
`SurfaceInput` rows (`geometry.surfaces[]`, where the hinge line already is
since note 69 D-69.16); the v80 hop carries each tail row's values to its
control surface (`tail_geometry.CONTROL_PARENT` inverted: htail → elevator,
vtail → rudder); `tail_span`'s bridge reads the control surface's row. The
Tail Mass table is then mass only.

**D-71.10 — A spanwise wing-mass figure on the Wing Loads page** (owner, Q4).
A figure family `wing_mass_span` beside the span-load figures: the panel
mass density WINGINER integrates per strip against span, for each FLIGHT
case's mass state, with the point masses marked at their butt lines and
sized by weight (`Series.sizes`, #388), built from the same `inertia_units`
the module runs on so the drawing and the loads cannot disagree. Where the
wing mass is entered (the weight page) is no longer where its distribution is
analysed, and the owner asks that the analysis page show what it spreads.

## 3. Questions for the owner (ruled 2026-10-18, in session)

| # | Question | Recommendation | Ruling |
|---|---|---|---|
| Q1 | Delete `vtail.gross_weight_lb` (D-71.4) or keep it as a collapsed override on the weight page? | **Delete**: MTOW is the one design weight, every fixture types it, and a fin sized at a different weight than the airplane's is not a case the suite has. | **Delete.** |
| Q2 | Blank the fixtures' typed engine and propeller weights so the rows govern (D-71.3)? | **Yes**: the typed values equal the rows on every fixture since #384, so nothing moves and the row becomes the one place the number is edited. | **Blank them.** |
| Q3 | `speeds.weight_lb` as a collapsed override (D-71.2) or deleted outright? | **Collapsed override**: STRSPEED is oracle-locked and its prompt is the design weight; a typed value is the owner's deliberate deviation, warned. | **Collapsed override.** |
| Q4 | Move `tip_root_density_ratio` / `inboard_rib_y` to the weight page beside the panel override? | No: they shape the panel's mass, they do not state a mass. | **Overruled: move them to the weight page**, and add a plot of the wing's spanwise weight distribution to the Wing Loads page, like the span-load plots (D-71.8, D-71.10). |
| Q5 | Move the three control-load fields off `tail_mass[]` onto the control surface rows? | Not in this note: rename in place; the schema move is note 56's to reopen. | **Overruled: they belong on the Geometry page** — they define geometry the beam model uses (D-71.9). |
| Q6 | Schema v80 as one hop (delete + move) or two? | **One hop** (`_hop_79`): one release, one migration note. | **One hop.** |

## 4. Closure gates (G-71.1 … G-71.6)

| Gate | Statement | Where |
|---|---|---|
| G-71.1 | **No delivered load moves**: every Imperial digest is unchanged on every fixture (the typed values the moves retire equal their owners); the beam model and every deck are byte-identical | `tests/imperial_baseline.py`'s frozen digests, `tests/test_sbeam_roundtrip.py` |
| G-71.2 | A blank `speeds.weight_lb` derives MTOW exactly, a typed one governs and warns; `max_takeoff_weight` no longer reads it | `tests/test_derive_override.py`, `tests/test_cg_cases.py` |
| G-71.3 | `vtail.gross_weight_lb` is gone from the registry, the schema and the dictionary; the v79 → v80 hop drops it and states a value that differed from MTOW; `ref_waterline` arrives at `geometry.fuselage.beam_waterline_z` with its value on all four fixtures | `tests/test_migrations.py`, `tests/test_schema_guards.py` |
| G-71.4 | The six moved rows render on the pages this note names and nowhere else, and every input field still lands on exactly one oracle page | `tests/test_field_registry.py` |
| G-71.5 | `fuselage_lra` reads the moved field: the beam waterline on every fixture equals its value before the move | `tests/test_derived_geometry.py` |
| G-71.6 | The five fixtures type no mass quantity apart from its owner: engine and prop weights, gear weights, `speeds.weight_lb` all blank; selectors set | `tests/test_derive_override.py` (a fixture sweep) |
| G-71.7 | The three control-load fields are gone from `tail_mass[]` and present on `geometry.surfaces[]`; a v79 tail row's values arrive on its control surface; `tail_span`'s bridge reads them there and every delivered tail load is unchanged | `tests/test_migrations.py`, `tests/test_tail_span.py` |
| G-71.8 | `wing_mass_span` is catalogued on the Wing Loads page, builds on every fixture, draws one density series per FLIGHT mass state from `inertia_units` and marks every point mass sized by weight; the per-strip density integrates to the state's panel weight | `tests/test_figures.py` |

## 5. Out of scope, stated

- The per-case mass properties (#382, shipped), the gear link (#384,
  shipped), the engine count and SELECT wing weight (#385, shipped).
- M4-4 (SELECT's precise inertia) stays parked; D-71.5 moves the override's
  page, not its default.
- A `Fuselage` read-only view of the station override on Fuselage Loads: the
  page states where it is entered; a second rendering is what this note
  removes elsewhere.
