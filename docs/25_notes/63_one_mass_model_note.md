# One mass model: the case's loading is the mass state of every inertia load (design note 63)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-17** (owner, in session, under the solo profile —
`DEVELOPMENT_PROCESS.md` §0; rule 1's working-alone branch; PROPOSED,
reviewed and flipped the same day — the critical-advocate review's three
findings are **ruled** in §9 and their rulings are written into D-63.2,
D-63.7, D-63.8, D-63.10, D-63.11, gate 1, G-63.3a and G-63.4; R-63.4's
scope split is left to the owner at implementation). This is the
note design note 62 §6 promised: the wing mass states in the Wing Loads
step. The discussion that shaped it (2026-09-17) widened it from "a state
list on `WingMassInput`" to the ruling in §2: **the suite keeps one mass
model**, the item database and the case's D-25 loading, and every inertia
load — wing, fuselage and the assembled deck — reads its mass state from
the case. Filed as **#289** (band B7, 0.8.6, after #288); D-63.9, the loading editor, is **#290** (tier M, directly after #289).

**Tier L.** A schema change (fields leave `WingMassInput`, a design weight
and a carriage tag arrive), a new read in WINGINER and `body_loads`, and a
new case family in the Wing Loads step (the per-loading variants of each
SELECT slot). No oracle moves (§4 gate 1): on `ga6_normal` the derived
panel equals the entered one to the pound and the fixture carries no point
mass, so WINGINER's Appendix A figures are reproduced bit-for-bit.

**Conventions:** `CONVENTIONS.md` (mass is not a load quantity, no factor
touches it; §7 SSOT table — the mass partition has one owner,
`sloads/mass_distribution.py`, plan 11 B-2; case identity §case identity).
**Theory:** Ref 1 Ch 13 p93 (WINGINER: panel taper + concentrated masses,
per side, WINGINER.BAS 690–880 and 1180–1270), Ch 15 p103 (the body beam
carries what the wing does not), UG Table 2.2 (WTONECG feeds WINGINER).
Related and not repeated: note 25 (D-25, the entered loading), note 31
(`wing_fraction`, the row split in space), note 39 (OV-1, blank derives and
typed overrides), note 50 (the fuselage station table derived from the
items), note 32 (CONM2 per-row cards), note 62 (the **ten** SELECT slots this
note's variants multiply — six `.BAS`, NHAA/NLAA, and the load-factor pair
PNZ/NNZ of D-62.8, which already delivers the nz extremes so D-63.7 is a
question of mass state only).

---

## 1. Measurements (2026-09-17, at `dev/v0.8.6` 58d0900)

### 1.1 Three inertia paths, three readings of the mass state

| Path | Weight/CG it uses | Wing mass it distributes | Follows the case? |
|---|---|---|---|
| FLTLOADS / SELECT | the FLIGHT case's `weight_lb`, `xcg` | none needed | weight only |
| WINGINER / NETLOADS (`wing_inertia.py`, `net_loads.py`) | the case weight, **in the case label only** (`_case_weight`) | `wing_mass.panel_weight_lb` + `wing_mass.concentrated`, one list for the project | **no** |
| Balanced deck / LRA / CONM2 (`balance/applied.py`, `mass_cards.py`) | the winning V-n point's CG case; loading entered (D-25) or **searched** (`derive_case_loadings`) | WINGINER's panel **shape**, scaled onto the loading's WING-tagged parts (`_wing_inertia_scale`); body items at their own stations | yes, one loading per condition |
| `body_loads` (Ch 15 beam) | — | station table derived from the **whole** item database (`fuselage_beam_stations`), or the override table | **no** |

Two consequences, both on `atr42_100`:

- The net wing loads carry 1,900 lb of wing fuel per side at **every** case,
  the −1.00 g STALL −N pick at minimum weight included, while the LRA deck
  for the same condition carries **none**: the fuel row is tagged
  `fuselage` (its `wing_fraction` 0.41 puts 3,800 lb on the wing, against a
  real wing tankage of the order of 10,000 lb). This is the #257
  reconciliation statement, stated in the issued document and closed by
  nothing.
- The mass state behind each corner point is an accident of the search:
  least ballast wins, so whether "aft gross" flies with full fuel and fewer
  passengers or no fuel and a ballast row is decided by the numbers, not
  entered. `loading` is `None` on **every FLIGHT case of every fixture**;
  only `baron_58`'s three GROUND cases and `concept_heavy`'s one case carry
  one.

### 1.2 What the fixtures carry

| Fixture | `panel_weight_lb` (per side) | `concentrated` (per side) | fuel rows | FLIGHT loadings |
|---|---|---|---|---|
| `ga6_normal` | 165 (= ½ × "Wing, outboard" 330) | none | "Fuel to gross wt" 409, fuselage | 0 of 4 |
| `baron_58` | 280 | engine+prop+nacelle 575.5, main gear 75, fuel 360, systems 180 | "Fuel, left/right wing" 360 each, **component wing, consumable** | 0 of 3 (3 GROUND) |
| `atr42_100` | 1,325 | engine+nacelle 1,190, wing fuel 1,900 | "Fuel to gross" 9,174, fuselage, `wing_fraction` 0.41 | 0 of 5 |
| `concept_regional_jet` | 2,100 | none | "Mission fuel" 3,440, fuselage | 0 of 5 |
| `concept_heavy` | 900 | fuel 600 | "Fuel to gross" 5,500, fuselage, `wing_fraction` 0.22 | 1 of 1 |

`baron_58` is already the shape this note asks for on the item side:
per-side wing rows, fuel as its own consumable row on the wing. It still
duplicates them in `concentrated`, which is the defect. `wing_mass_tie`
names the gap on every fixture that has one; `unmodelled_wing_mass` names
the single cause (the fuel). The fuselage side went through this once:
note 50 derived the station table from the items and left
`fuselage_mass.stations` as an OV-1 override (`stations_are_override`),
and every shipped fixture runs on the derived table.

### 1.3 What the schema already has, unused

- `CgCase.loading` (D-25): `aboard`, `fractions` on consumable rows,
  `ballast`. Authoritative when present; the case's numbers become a
  checked echo. **No GUI page edits it** (no `aboard` widget exists in
  `oracle_app/form.py` or `app_shell/`); it is entered in the file.
- `MassItem.consumable` (G-5) and `wing_fraction` (note 31, WF-3), the
  time and space axes of one row. `reacted_parts` is the one place a row
  becomes the parts the beams react.
- Design weights `max_takeoff_weight_lb` (G-14) and
  `max_landing_weight_lb` (G-4) as SSOT scalars. **No zero-fuel weight**
  anywhere (`04_far25_gap_analysis.md` 25.321/25.343, disposition N;
  parked as F25-1).

### 1.4 Why SELECT cannot carry the variants

Two cases at one envelope point balance to the same air loads, and SELECT
picks per family on air load (note 62 §1.1), so a second loading at the
same weight and CG never wins a slot. Inertia relief is invisible to the
pick by construction. That is the mechanical reason the owner's ruling
(note 62 §2, "handled in the Wing Loads step") is the only place it can be
applied.

## 2. Owner rulings (2026-09-17, in chat)

1. **Mass data lives on the Weight & Mass Properties page.** The wing's
   mass fields (`panel_weight_lb`, `concentrated[]`) move off the Wing
   Loads page into the item database and the case loading, the way the
   fuselage stations already did. The Wing Loads page keeps the panel
   *shape* and the load-case list, which are modelling, not mass.
2. **The payload cases are the mass states.** The corners of the weight/CG
   envelope are reached by more than one fuel/payload combination; each
   combination that matters is a case with an entered loading. Zero fuel
   and full fuel, and the payload that goes with each, are cases. Max
   zero-fuel weight at the forward and aft limits, then fuel out to the
   envelope, is the set an ATR-class airplane enters.
3. **Inertia-relief variants are the Wing Loads step's** (note 62 §2 carried
   forward): each SELECT slot runs at every FLIGHT mass state; SELECT's pick
   is untouched.

## 3. Decisions

| # | Decision | Why |
|---|---|---|
| **D-63.1** | **The mass state of a case is its D-25 loading, and every inertia consumer reads it.** WINGINER, NETLOADS, `body_loads` and the balanced deck take their masses from `reacted_parts(loading.items)` for the case they run. A case without a loading keeps today's search fallback (`derive_case_loadings`), bit-for-bit, so `ga6_normal` and every pre-existing file run unchanged; concept-mode validation warns (`case_loading_missing`) on a FLIGHT case with no loading — **the warning ships with the editor (D-63.9), not with the physics**, so no GUI user sees a warning the GUI cannot clear. | One model, one reading. The search stays a fallback, never the state of record. |
| **D-63.2** *(amended 2026-09-17, R-63.3)* | **`WingMassInput` loses its mass.** `concentrated[]` is removed. **The v67 migration drops, stamps and reports; it does not convert a mass the items already carry.** Measured: the wing tie closes on every shipped fixture, so every fixture's items already hold the concentrated mass — per-side rows on the Baron, `wing_fraction` slices of a fuselage fuel row on the ATR and concept_heavy — and converting each entry to a new row would double-count 2,381 lb on the Baron and 3,800 lb on the ATR, with no robust row match (the Baron's lumped 575.5 lb engine is three item rows at three stations; its 180 lb "systems" entry has no counterpart). So: on a file whose tie closes, `concentrated` is **dropped** and the dropped entries are named once in a validation note; on a file whose tie is open by the entries' amount, they are converted to per-side WING items (kind EMPTY, carriage POINT) because there the mass really is missing. In both cases the migration **stamps `carriage = POINT` on every WING row with a non-zero butt line** and leaves centreline WING rows PANEL — a one-time default for rows that exist, after which every row is typed (this is not the classification heuristic D-63.3 rejects). The three fixtures are then **hand-corrected in the PR** per D-63.4: ATR and concept_heavy fuel to per-side wing tank rows with the fuselage row's `wing_fraction` zeroed, ATR engines and nacelles per side. `panel_weight_lb` becomes a derived read: half the WING-tagged PANEL items, override allowed (`panel_weight_override_lb: Optional[float]`, OV-1 shape); the migration writes the override only where the derived value differs from the entered one by more than the tie tolerance. `tip_root_density_ratio`, `inboard_rib_y`, `surface`, `cases[]` stay. | The fuselage precedent (note 50). `wing_mass_tie` reduces to *derived panel vs override* and `unmodelled_wing_mass` is deleted — there is nothing left to disagree with. |
| **D-63.3** | **`MassItem.carriage: WingCarriage = PANEL`** (`PANEL` \| `POINT`), read on WING-reacted parts only. PANEL mass is spread by WINGINER's taper; POINT mass is a WINGINER concentrated mass at the part's own `x`/`y`/`z` (Ch 13 p93, lines 1180–1270). Default PANEL reproduces today's balanced-deck scaling on every row that exists. | The taper cannot tell an engine from a spar by inspection: `atr42_100` carries "Engines (2)" as one row at the centreline. A typed tag is the OV-1 answer, not a butt-line heuristic. |
| **D-63.4** | **Fuel is entered per tank as a WING (or fuselage) consumable row, carriage POINT, at the tank centroid**; `wing_fraction` remains for a row that genuinely spans both beams. A loading names the fuel rows aboard and their fractions. A tank modelled as a point is the `.BAS`'s own idealisation; a spanwise tank extent is parked (§6). | `baron_58` already does this. It removes the second fuel opinion the ATR carries today. |
| **D-63.5** | **`weight.max_zero_fuel_weight_lb`** (MZFW) joins MTOW and MLW as an SSOT design weight (G-4/G-14 shape: `0` = not entered; nothing derives it silently; the page offers OEW + max payload as the estimate). `seed_flight_cases` grows by three named cases when MZFW is entered — `"mzfw aft"`, `"mzfw fwd"`, `"full fuel aft"` — each written **with** its loading (all discretionary payload rows, no fuel rows / fuel rows to 1.0 with payload trimmed to MTOW); the five existing seed names and their derived loadings are unchanged. | Ruling 2. Part 25 requires MZFW as a design weight (25.321); on a wing-fuel airplane it is the up-bending critical state and today no case reaches it. |
| **D-63.6** | **WINGINER and NETLOADS run each wing case at a named mass state.** `WingLoadCase` gains `cg: Optional[str]` (a FLIGHT case name). Resolution: explicit `cg` wins; else the V-n point's own CG case (today's implicit state, now stated); else the search fallback. The point-mass list and the panel scale are built **per case** from that loading's WING parts; `inertia_units` (the shape) is built once. Every `WingLoadResult`/`CaseRef` names the mass state it ran at. | Today the case weight reaches the label and nothing else. |
| **D-63.7** *(amended 2026-09-17, R-63.2)* | **Each SELECT wing slot runs at every FLIGHT mass state, and the net-governing variant is the delivered case.** The Wing Loads step expands the ten slots (note 62) × the FLIGHT cases **regardless of `wing_mass.cases`** — an entered table is a *filter* on which slots run, never a second source of points (this narrows M4-2 decision 2's "explicit entries always win" to the slot list). For slot *s* and case *k*, the air load is that family's own winning V-n point balanced at *k* (SELECT's per-family criterion applied within case *k*), the inertia is *k*'s loading. Each variant is an existing V-n point — a **run** with its own identity (D-63.11). The governing variant is the one with the extreme **signed root `Mxx` at the loads reference axis** — largest for the positive slots, most negative for the negative ones (not "resultant": root bending is a signed moment). **The slot is a role the down-select assigns to one run:** SELECT's delivered `CriticalCondition` for the slot *is* the governing run — SELECT's air pick per family stays a queryable intermediate (`select.air_picks`, what the Appendix A test asserts) and an assessed row in the variant table without a W id, and the slot's condition is re-pointed to the governing run before anything downstream (index, deck, report) reads it. The W-nn id is the slot's (W-01…W-10, note 62 D-62.3) and the deck subcase number derives from it as today; the run key (D-63.11) names the point. The report's wing table lists every variant with the governing one marked; the balanced deck's mass set for the subcase is the governing run's loading, so the deck and the net table describe one state. | Ruling 3, and the only way an MZFW case can govern a slot the air pick gave to MTOW. One id per physical condition (M4-2 decision 1) holds because the slot id and the run key are two different things (D-63.11): SELECT's air pick and the governing variant are two runs with two run keys, and only one carries the slot. The count is 10 × 5–8, cheap. |
| **D-63.11** *(owner, R-63.2, 2026-09-17)* | **`CaseRef` carries the run key beside the slot id.** The run key is the composite that names a balanced point without reference to its position in the matrix: **manoeuvre label, CG case name, altitude, configuration** — the tuple G-62.2 already uses to survive the #164 renumber. `CaseRef` gains `run: str` (the manoeuvre label, e.g. `"GUST +C"`) and `config: str`; `cg`, `speed_kt`, `altitude_ft` already exist. The V-n `case` integer stays as a convenience and is never identity. **The slot id is the deliverable's number, the run key is the condition's name:** the case index keys its rows on the run key with the slot as a column, every deck subcase's `$` header states both (`SUBCASE 5101  W-01 PHAA  —  STALL +N, CG2, 0 ft, clean`), and `subcase_id`/`balanced_subcase_id` stay pure functions of the slot id so persisted `selected_case_ids` and exported decks do not move. `CONVENTIONS.md` §4 (case identity) and note 22 gain the one paragraph that says this. | The user's model (2026-09-17): every run of payload case × manoeuvre × speed/altitude × variation gets its own identifier at generation, the down-select picks the critical ones, and *their names stay*. FLTLOADS already generates that matrix; the missing piece was a run identity that does not float with the matrix size and is not confused with the slot. Nastran/sbeam need a small stable integer per subcase, which is what the slot band gives and a run-derived number could not. |
| **D-63.8** | **`body_loads` reads the case's loading**: `fuselage_beam_stations(project, loading)` lumps that loading's body parts — the entered loading, else the search fallback of D-63.1. The override table stays one per project (an override is one table, not one per state) and validation warns when an override is set on a project whose FLIGHT loadings differ in body mass by more than the tie tolerance. **This is a stated correction, not an oracle-locked read (owner, R-63.1, 2026-09-17):** today the Ch 15 beam integrates the *whole* item database at every fuselage condition — on `ga6_normal` 3,070 lb of body mass at the GREATEST NZ condition, whose CG4 airplane weighs 2,063 lb and carries 1,733 lb of body mass; AFT DOWN BENDING at CG3 integrates 3,070 against 2,470; MAX DOWN LOAD ON WING at CG2 keeps its total but moves the sixth occupant out and 248 lb of ballast in; AFT UP BENDING at CG1 is unchanged. Ch 15 prints no station table, so the body distributions are closure-locked, not oracle-locked, and the closure holds per condition either way. | Note 50's derivation was whole-database because there was no per-case read; there is now. A whole-database fallback would keep the defect on every fixture until #290 and leave the body reading a different mass state from the deck's. |
| **D-63.9** *(split to its own tier M issue **#290**, owner 2026-09-17; lands directly after #289)* | **The Payload Cases tab gains the loading editor**: per case, the discretionary rows aboard (checkboxes), a fraction on each consumable row aboard, an optional ballast row, and the echo check beside the entered weight/CG (D-25a). The Wing Loads page loses its mass table and shows the per-case WING parts read-only. | Ruling 1. D-25 shipped without a GUI; a state that can only be typed in JSON is not entered. |
| **D-63.10** *(amended 2026-09-17, R-63.1/R-63.3)* | **Oracle unchanged, twin movements stated.** `ga6_normal`: derived panel 165 = entered; no POINT rows; no loading → search fallback → WINGINER, NETLOADS, the deck's wing sets and CONM2 bit-for-bit; `body_loads` moves as gate 1 states (R-63.1). `baron_58` closure figures move by two stated causes: the `concentrated` duplicate goes and the lumped engine at x 48 becomes the item rows at x 30/50/55 (BL 66 kept through the POINT stamp), so PHAA/TORS torsion moves by the station change; the ATR and concept_heavy wing distributions move by the fuel re-slicing of D-63.4. Every moved figure is measured in the PR and stated in the fragment. | Rule 2 and CLAUDE.md's oracle lock. |

## 4. Gates (benchmark-first)

1. **Oracle unchanged, body loads corrected.** Every Appendix A WINGINER
   assertion and every Ch 15 closure assertion passes without edit;
   `ga6_normal` digests for `wing_inertia`, `net_loads`, the deck's wing
   sets and CONM2 are byte-identical. **`body_loads` moves** (D-63.8,
   R-63.1): on `ga6_normal` the CG1 condition is unchanged and the CG2,
   CG3 and CG4 conditions integrate the case's own body mass (3,070 lb
   redistributed, 2,470 and 1,733 lb against 3,070 today); the history
   fragment states the per-condition movement on every fixture and the
   `body_loads` digest is re-baselined in the same wave.
2. **G-63.1 one model.** For every fixture and every FLIGHT case: Σ WING
   parts of the case's loading = 2 × (panel used + Σ point masses used) by
   WINGINER for that case, to `RECONCILE_REL_TOL`. `mass_wing_tie` becomes
   this per-case check; the #257 statement in the report reads "0 lb" on
   every fixture or the gate fails.
3. **G-63.2 relief has the right sign.** On `atr42_100` and `baron_58`,
   for the PHAA slot, net root bending at the zero-fuel state exceeds net
   root bending at the full-fuel state at equal air load; on the NHAA slot
   the inequality reverses.
4. **G-63.3 the variant table is complete.** Slots × FLIGHT cases rows,
   exactly one marked governing per slot, the deck subcase's `$` header
   names the same run key as the marked row, and the CONM2 mass set the
   subcase references is that case's. **G-63.3a identity:** across a full
   run no two `CaseRef`s share a run key with different loads, no W id is
   carried by more than one run, and on `ga6_normal` the governing run of
   every slot has the run key of SELECT's air pick (the Appendix A set
   reproduced, gate 1 in one line). `select.air_picks` on the GA6 asserts
   the six Appendix A points unchanged.
5. **G-63.4 migration.** On every shipped fixture the v67 migration drops
   `concentrated` (the tie closes on all five) and the WING item weight
   the migrated file carries equals the pre-migration weight to the pound
   — nothing double-counted, nothing lost; every WING row at non-zero
   butt line is `POINT`, every centreline WING row `PANEL`. A synthetic
   file with an open tie converts its entries and closes the tie.
   `panel_weight_override_lb` is `None` on every fixture after the item
   databases are corrected (the corrections are part of the PR: ATR wing
   tankage as per-side rows, engines and nacelles per side, concept_heavy
   fuel per side). The Baron's WINGINER point-mass list after migration
   holds the same total per side as today's `concentrated` (1,190.5 lb),
   at the item rows' own stations.
6. **G-63.5 body per case.** `body_loads` on `baron_58` "fwd light"
   integrates the loading's body weight, not the database's.
7. **G-63.6 schema/GUI.** Data dictionary regenerated; field registry
   totality gate passes with the loading editor's widgets; `ci.yml`
   unchanged.

## 5. Rules applied

- Rule 1: this note before code. Rule 2: no printed oracle for a mass
  state; gates 2–6 are the invariant substitute, with the oracle lock in
  gate 1. Rule 3: the mass partition keeps its one owner
  (`mass_distribution.py`); `carriage` and the per-case read are owned there
  and drift-guarded by G-63.1. Rule 4: the same defect (a second mass list
  beside the items) is removed on the wing **and** checked on the fuselage
  override in one change. Rule 6: the effect is first-order on a delivered
  load — on `atr42_100` the wing fuel relief WINGINER applies to the
  minimum-weight case is 1,900 lb per side against a panel of 1,325.

## 6. What this supersedes / touches, and what it leaves

- Supersedes note 62 §6's sketch ("named disposable-mass states on
  `WingMassInput`") with D-63.1/D-63.6: the states are the cases.
- Touches note 31 (a fuel row per tank is now the preferred entry;
  `wing_fraction` kept), note 50 (per-case derivation, D-63.8), note 32
  (CONM2 cards stay one per row; the subcase's mass set follows D-63.7),
  #257 (the reconciliation family closes by construction, G-63.1), #260
  (its case-set shape follows D-63.7), F25-1 (MZFW leaves the parked pack,
  D-63.5; the 25.341 gust schedule stays parked).
- **Un-parks with a number** note 62's "pick on net root bending": D-63.7
  is that pick, applied to the variants, with the air pick per slot kept as
  SELECT's.
- **Leaves parked:** a spanwise tank extent (a fuel mass as a strip rather
  than a point) — measure the root-bending difference on the ATR once the
  per-tank rows exist and file it with the number; CG-dependent MTOW
  (already parked, G-14); the GROUND cases' burn-down interaction with an
  entered loading (G-5 already covers it).

## 7. Closure obligations (tier L)

`PROGRAM_SPEC.md` WTONECG/payload_cases, WINGINER, NETLOADS and Ch 15
sections; `ch04_wing_loads.md` (the variant table); `theory_sources.md`
WINGINER row citing this note; `CONVENTIONS.md` §7 SSOT table (the mass
state's owner) and §4 case identity (the slot id / run key split, D-63.11,
with note 22 amended the same way); `DATA_DICTIONARY.md` regenerated (v67); one
`changes/<slug>.history.md` fragment in full step format with the measured
twin/concept movements; one Imperial digest wave (`wing_inertia`,
`net_loads`, `body_loads`, balance, deck, CONM2, report); this note's status
to SHIPPED with the measurements; `04_far25_gap_analysis.md` 25.321 row to
**A**.

## 8. Worked sample: `ga6_normal` (measured 2026-09-17)

The Appendix A airplane's fuel is a fuselage tank at station 70, forward of
the CG, so its zero-fuel and full-fuel states move weight and CG and **not**
the wing inertia relief. The item database gives empty 1,822 lb at 73.0 in,
empty + pilot + 30-minute fuel 2,063 lb at 73.1 in, everything aboard
3,400 lb at 85.0 in; the aft limit is 85.1 in.

### 8.1 The mass cases and their loadings

| Case | W (lb) | xcg (in) | Loading (D-25) | Origin |
|---|---|---|---|---|
| CG1 aft gross | 3,400 | 85.1 | copilot, 3rd–6th person, fuel to gross 409, ballast row 78 | existing; echo 85.0 vs 85.1 entered |
| CG2 fwd gross | 3,400 | 77.49 | copilot, 3rd–5th person, fuel to gross, ballast 248 lb solved | existing; a stress-ballast case |
| CG3 fwd regardless | 2,800 | 72.64 | copilot, fuel to gross, ballast 158 lb solved | existing |
| CG4 min weight | 2,063 | 73.09 | nothing discretionary | existing; exact |
| mzfw aft | 2,743 | 82.7 | copilot, 3rd–5th person, 30-minute fuel only | D-63.5 seed |
| mzfw fwd | 2,233 | 73.2 | copilot only, 30-minute fuel only | D-63.5 seed |
| full fuel aft | — | — | duplicates CG1 | seed skips it |

**Two amendments to D-63.5 the sample forces.** Six people with no fuel to
gross is 2,913 lb at 86.6 in, aft of the limit: the zero-fuel seed searches
for the **heaviest zero-fuel loading inside the envelope**, it does not
simply drop the fuel rows. And a seeded case that coincides with an
existing case (weight and CG within the echo tolerance) is **not written**.

### 8.2 The variant table the Wing Loads step assesses

Eight slots × six FLIGHT cases = 48 variants; the air resultant (lb) of each
family's best V-n point per case, the four existing cases:

| Slot | CG1 | CG2 | CG3 | CG4 | Governs |
|---|---|---|---|---|---|
| PHAA (STALL +N, 3.8 g) | 12,547 | **13,132** | 11,122 | 8,172 | CG2, case 22 |
| PLAA (MAN D, 3.8 g) | 12,756 | **13,318** | 11,344 | 8,475 | CG2, case 25 |
| PMAA (GUST +C) | 13,137 @ 3.97 g | **13,701 @ 3.96 g** | 12,990 @ 4.43 g | 11,335 @ 5.25 g | CG2, case 30 |
| NHAA (STALL −N, −1.52 g) | 4,901 | **5,105** | 4,341 | 3,182 | CG2, case 28 |
| NMAA (GUST −C) | 6,168 | 6,449 | **6,772 @ −2.43 g** | 6,644 @ −3.25 g | CG3, case 53 |
| NLAA (GUST −D) | 2,535 | 2,681 | 3,043 | **3,226 @ −1.69 g** | CG4, case 72 |
| ACRL, TORS | same rule on the roll families | | | | CG2 case 40, CG1 case 18 |

On `ga6_normal` the net-governing variant is SELECT's air pick in every
slot: the wing inertia is the 165 lb panel per side at every case with no
point masses, so within a family at constant *nz* the net root bending
orders as the air load; in the gust families *nz* rises as weight falls,
adding relief to the light case, which already loses on air. **48 variants
assessed, 8 delivered, all 8 the Appendix A points** — gate 1 in numbers.
On `atr42_100` the table does not collapse: the zero-fuel case removes
wing-fuel relief of the order of 5,000 lb per side from the up-bending
slots and adds it to the down-bending ones.

### 8.3 Worked sample: `atr42_100`, a wing-fuel airplane (measured 2026-09-17)

The item database per D-63.3/D-63.4: the fuel to gross (9,174 lb) and the
reserve (700 lb) become per-side wing tank rows at the fixture's tank
station (x 395, ±175 in); engines and nacelles per side at ±161 in. MAC
74.1 in, leading edge 376.1 in; limits 15–35 % MAC at gross, 10 %
regardless. The V-n matrix was rebalanced at the seven cases below and each
slot's family pick per case run through WINGINER with **that case's** fuel
as the point mass (`nx` = 0; root Mxx is the comparison).

| Case | W (lb) | % MAC | Loading | Wing fuel (lb) |
|---|---|---|---|---|
| MTOW aft | 36,817 | 34.3 | all passengers, both holds, fuel to gross × 0.895 | 8,910 |
| MTOW fwd | 36,817 | 15.0 | fwd cabin, fwd hold, full fuel, **4,166 lb solved ballast** | 9,874 |
| MZFW aft | 28,410 | 35.0 | all passengers, fwd hold, aft hold trimmed to 853 lb, no fuel to gross | 700 |
| MZFW fwd | 23,477 | 7.0 | fwd cabin, fwd hold, no fuel to gross | 700 |
| full fuel aft | 36,817 | 36.3 | full fuel, aft cabin, aft hold, fwd cabin × 0.51 | 9,874 |
| fwd regardless | 30,000 | 11.1 | fwd cabin, fwd hold, fuel × 0.71 | 7,223 |
| min weight | 19,247 | 17.0 | crew and reserve only | 700 |

Three of the seven fall outside the entered envelope: the database cannot
reach 15 % MAC at gross without ballast, max payload at zero fuel sits at
36.8 % until the aft hold is trimmed, and the zero-fuel forward loading is
at 7 %. The fuel sits at 25 % MAC, so burning it moves the CG toward the
payload. **D-63.5's seed clips to the envelope on both edges** (the second
amendment of §8.1 generalised): a seeded zero-fuel or full-fuel case is the
heaviest loading of its kind inside the limits, and the note names the
trimmed row.

### 8.4 The ATR variant table, root Mxx (10³ in-lb), each case at its own fuel

Bracketed: what today's model delivers, 1,900 lb per side fixed at every case.

| Slot | MTOW fwd | MZFW aft | MZFW fwd | min weight | Governs |
|---|---|---|---|---|---|
| PHAA | **5,923** [7,162] | 5,500 [4,868] | 4,593 [3,960] | 3,444 [2,813] | MTOW fwd |
| PLAA | **5,771** [7,007] | 5,308 [4,676] | 4,231 [3,600] | 3,083 [2,451] | MTOW fwd |
| PMAA | **5,850** [7,086] | 5,750 [5,066] | 5,376 [4,610] | 4,535 [3,666] | MTOW fwd |
| NHAA | **−2,500** [−2,996] | −2,271 [−2,018] | −1,910 [−1,656] | −1,439 [−1,185] | MTOW fwd |
| NMAA | **−2,511** [−3,005] | −2,333 [−2,080] | −2,161 [−1,898] | −2,233 [−1,869] | MTOW fwd |
| NLAA | no negative-lift point (D-62.2) | −720 | −1,072 | **−1,268** [−1,108] | min weight |

Three readings:

- **The air pick still governs every slot, by 2 % on PMAA.** The MZFW aft
  variant is 5,750 against 5,850. A larger tankage or a tank further
  outboard than the fixture's 175 in flips it; D-63.7 is the check that
  decides on a wing-fuel airplane, not a table for the record.
- **Today's delivered wing loads are wrong in both directions.** The
  governing MTOW case is **overstated by 21 %** (relief of 1,900 lb per side
  applied against 4,937 lb aboard); every zero-fuel case is **understated
  by 11–18 %** (relief applied that is not there). The shipped ATR wing
  envelope is a 7,162 that should be 5,923 — rule 6's first-order effect,
  and the number that ranks this note.
- **NLAA at minimum weight** is the one slot the light case wins on air
  alone, and only because D-62.2 excludes the positive-lift GUST −D points
  the MTOW cases produce.

## 9. Review findings open at AGREED (critical-advocate review, 2026-09-17)

Recorded with the reviewer's recommendation; each is ruled by the owner
before its decision is coded, and the ruling amends the decision above.

- **R-63.1 — RULED 2026-09-17 (option 1: state it as a correction; D-63.8
  and gate 1 amended in place).** Original finding: gate 1 was not true for
  `body_loads` on `ga6_normal`. Today
  the Ch 15 beam integrates the **whole** item database (3,070 lb of body
  mass) for every fuselage condition; the four GA6 fuselage conditions sit
  at CG2, CG3, CG1 and CG4, and CG4 weighs 2,063 lb. D-63.8 reading the
  case's loading moves three of the four GA6 body distributions, so the
  `body_loads` digest cannot be byte-identical. There is no printed Ch 15
  station oracle, only the closure gate. *Recommendation:* state the GA6
  body movement as a **correction** (a 2,063 lb airplane's body inertia is
  integrated at 3,070 lb today), measure it in the PR, and amend gate 1 to
  "byte-identical for WINGINER, NETLOADS, the deck's wing sets and CONM2;
  `body_loads` moves by the stated amount". The alternative — a
  whole-database fallback when no loading is entered — keeps the defect.
- **R-63.2 — RULED 2026-09-17 (option 1 with the identity split: D-63.7
  amended, D-63.11 added).** Original finding: D-63.7 collided with case
  identity. M4-2 decision 1 gives one
  id per physical condition and the case index dedupes on it. If W-01's
  net-governing variant is a different V-n point from SELECT's PHAA
  condition, two conditions share one id and the index collapses them.
  Also, §8.4 runs all slots on the ATR while D-62.7 keeps the fixtures'
  explicit `wing_mass.cases` and `resolve_wing_cases` gives explicit entries
  precedence. *Recommendation:* rule that (a) the variant expansion runs
  over SELECT's slot set **regardless** of `wing_mass.cases` (the entered
  table becomes a filter, not a source), and (b) SELECT's delivered
  condition **is** the governing variant — the SELECT pick is re-pointed
  after the Wing Loads step decides, so one id, one point. State the
  governing quantity precisely: signed root `Mxx` per slot (largest for the
  positive slots, most negative for the negative ones), not "resultant".
- **R-63.3 — RULED 2026-09-17 (option 1: drop where the tie closes, stamp
  POINT on off-centreline WING rows, hand-correct the three fixtures;
  D-63.2, D-63.10 and G-63.4 amended).** Original finding: the migration
  could not be mechanical. The wing tie closes
  on all five fixtures today, so every fixture's items already carry the
  `concentrated` mass in some form: per-side rows on the Baron,
  `wing_fraction` slices of a fuselage fuel row on the ATR and
  concept_heavy. Converting each entry into a new WING item double-counts
  2,381 lb on the Baron and 3,800 lb on the ATR, and no robust row match
  exists (the Baron's "Systems & unusable fuel" 180 lb/side has no item
  counterpart). Conversely D-63.3's default PANEL smears the Baron's
  engine, gear and fuel — WINGINER point masses at BL 66/57/95 today —
  until hand-tagged, so "PANEL reproduces today" holds for the deck and
  not for WINGINER on the Baron. *Recommendation:* the migration **drops**
  `concentrated` where the tie closes (recording what it dropped in a
  validation note), stamps `carriage = POINT` on every WING row at
  non-zero butt line, and the PR hand-corrects the ATR and concept_heavy
  fuel rows per D-63.4; twin movements measured and stated (D-63.10).
- **R-63.4 (minor).** D-63.5 adds a third search objective (heaviest
  zero-fuel loading inside the envelope) beside the exact-subset search and
  the ground burn-down; `cg_cases.FLIGHT_CASE_NAMES` pins the five seed
  names and its guard test moves. Five orthogonal tags now sit on one
  `MassItem` row (kind, component, consumable, wing_fraction, carriage) —
  the complexity cost of the OV-1 choice, to be stated in the data
  dictionary. *Scope:* the reviewer recommends splitting #289 — D-63.1 to
  D-63.4, D-63.6 and D-63.8 as the one-model step; D-63.5 and D-63.7 as the
  variants step with its own gates.
