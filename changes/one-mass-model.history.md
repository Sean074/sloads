## Step — One mass model: the case's loading is the mass state of every inertia load (#289, design note 63 D-63.1…D-63.4, D-63.6, D-63.8, D-63.10, D-63.11, tier L, 2026-09-17)

**Objective.** Close the defect design note 63 measured: WINGINER and
NETLOADS distributed a second, project-wide mass list
(`wing_mass.panel_weight_lb` + `concentrated[]`) that ignored the case, the
balanced deck read a searched loading, and `body_loads` lumped the whole
item database at every condition — three readings of the mass state that
nothing reconciled. On `atr42_100` the −1.00 g minimum-weight pick carried
1,900 lb of wing fuel per side in the net loads and none in the deck; on
`ga6_normal` the GREATEST NZ condition's beam integrated 3,070 lb of body
mass under a 2,063 lb airplane. This is the one-model step of the R-63.4
scope split (ruled 2026-09-17); the variants step is #292 and the loading
editor #290.

**Deliverables.** **Schema v67.** `MassItem.carriage` (`WingCarriage`:
`PANEL` | `POINT`, D-63.3) says how the wing reacts a WING-carried part;
`WingMassInput` loses `panel_weight_lb` and `concentrated[]` — the panel is
derived (half the WING-tagged PANEL items, `mass_distribution.panel_weight`,
with `panel_weight_override_lb` the OV-1 override) and the concentrated
masses are the POINT rows of the case's loading; `WingLoadCase.cg` names
the mass state (D-63.6); `weight.max_zero_fuel_weight_lb` is stored beside
MTOW and MLW and seeds nothing until #292 (D-63.5); `CaseRef.run`/`config`
carry the run key beside the slot id (D-63.11) and `WingLoadResult` /
`BodyLoadResult` state their `mass_state`. **The read.**
`mass_distribution.wing_mass_state` resolves a CG case to its loading
(entered, else the search, bit-for-bit the pre-v67 fallback) and to the
panel and per-side POINT masses WINGINER hangs; `wing_inertia.panel_shape`
iterates the taper once at the project panel and `fold_units` scales it
and folds the case's point list per case, so WINGINER and NETLOADS carry
the relief a case flies with; `body_loads` derives each condition's
station table from that condition's loading (D-63.8); the balanced deck
scales its strips to the loading's PANEL parts and places its POINT parts
at their own stations. A loading the search cannot produce falls back to
the whole database **with the reason in the result** and a validation
warning; a searched loading is laterally symmetric by construction (one
tank of a pair is never a candidate) and an asymmetric entered one is
named. **The migration** (`_hop_66`, not an identity) drops
`concentrated[]` where the wing tie closes — every shipped fixture — and
names the entries once on the transient `Project.migration_notes`,
converts them to per-side POINT rows where it is open, stamps POINT on
every off-centreline WING row and PANEL elsewhere, and keeps the entered
panel as the override only where the derived value differs. **The
fixtures** are hand-corrected per D-63.2/D-63.4 and re-stamped: the
Baron's centreline fuel-system row per side; the ATR's engines and
nacelles per side and its 9,174 lb fuel-to-gross and 700 lb reserve rows
into per-side wing tank rows; the heavy's 5,500 lb fuel row likewise — so
`panel_weight_override_lb` is `None` on all five. The case index gains
`Run`/`Config` columns and every deck's `$` case map states the run key
after the id. The report's wing section names each case's mass state and
states the per-case tie ("0 lb apart" on every case). `PROGRAM_SPEC.md`
(payload_cases, WINGINER, NETLOADS, body_loads, the ownership table),
`CONVENTIONS.md` §1, §4 and §7, note 22 §2a, `theory_sources.md`'s
WINGINER row, `ch04`/`ch10` and the data dictionary state it.

**Test.** Gate 1: every Appendix A WINGINER and NETLOADS assertion passes
without edit and the GA6's `wing_inertia`, `net_loads`, `wing_applied`,
`mass_model` and `mass_check` digests are byte-identical; its body applied
set moves by the stated correction. **G-63.1** (`test_one_mass_model.py`):
on every fixture every delivered wing case names its state, its published
point loads are that state's POINT rows, and Σ WING parts of the loading =
2 × (panel + Σ points); each FLIGHT case's wing and body parts partition
its loading exactly. **G-63.3a, identity half:** every V-n-sourced
condition carries the point's run key, within the wing family a run key
names one slot, and WINGINER/NETLOADS deliver each W id under SELECT's run
key. **G-63.4:** the v66 fixture hops with nothing dropped or overridden
and loads to the current airplane; a closed-tie file drops and names, an
open-tie file converts and closes; every fixture carries its wing mass in
the items alone, POINT off-centreline, PANEL on it, the Baron's per-side
point list summing to the 1,190.5 lb its four lumped entries did.
**G-63.5:** the Baron's entered "fwd light" loading derives a beam of its
own body weight, not the database's. Validators `wing_panel_override_open`,
`wing_mass_asymmetric`, `wing_case_loading_not_derivable`,
`wing_case_mass_state_unnamed`, `wing_panel_empty`,
`fuselage_override_varies_by_case` and `migration_note` are each
exercised; on the shipped fixtures only the Baron's two non-derivable
FLIGHT cases fire. One Imperial digest wave.

**Key decisions.**

- **The fallback is stated, never silent.** A wing case that names no mass
  state, or one whose loading the search cannot produce, runs on the whole
  database with every row aboard — the pre-v67 reading — and the result's
  `mass_state` says why; the Baron's hand-entered PHAA and TORS now name
  `cg: "aft gross"`, its one derivable FLIGHT case, and its fuselage
  conditions at "fwd gross"/"fwd regardless" fall back with the reason
  until #290 enters those loadings.
- **The shape is scaled, not re-iterated.** WINGINER.BAS's ±1 % density
  band makes a re-run at a different target a different band; the shape
  built once at the project panel and scaled per case is exact at the
  target (Appendix A) and linear away from it.
- **The half-span models run the starboard POINT set.** A centreline POINT
  part enters at half its weight; the port parts are checked to mirror,
  and the subset search refuses an asymmetric candidate so no searched
  state can be one the deck and WINGINER cannot carry.
- **The fixtures' fuel is where the airplane's is.** The ATR and the
  heavy carried a `wing_fraction` slice sized to match the old fixed
  `concentrated` entry (3,800 / 1,200 lb); the whole fuel row is now
  per-side wing tank rows at the row's own station, so WTONECG's weight
  and CG are unchanged and the wing relief is the fuel aboard. Measured
  movements: the ATR PHAA relief per side 1,900 → 6,127 lb (engine 890,
  nacelle 300, fuel 4,587, reserve 350) and its closure `Izz` −8 % / −8 %
  / −15 % on fwd gross / aft gross / min weight; the Baron's 2,381 lb per
  side of engines, gear, fuel and systems at BL 57–95 instead of smeared to
  the tip, closure `Izz` 12,195 → 7,369 slug·ft² and the yaw accelerations
  up by the reciprocal (SUDDEN RUDDER +114 → +189 deg/s²), the lumped
  engine at x 48 now the item rows at x 30/50/55; the heavy's fuel 600 →
  2,750 lb per side at BL 120, closure `Izz` 32,302 → 42,104, its body beam
  15,000 → 10,700 lb; the ATR's stale entered fuselage table now reads
  2,333 lb *over* the derived beam (28,951 → 22,877 lb of body items). The GA6 body masses per condition:
  CG1 3,070 (unchanged), CG2 3,070 (redistributed: the sixth occupant out,
  248 lb of ballast in), CG3 2,470, CG4 1,733 lb against 3,070 before.
  Every fin load and `Ny` is unchanged on every fixture.
- **`04_far25_gap_analysis.md` 25.321 stays N** until #292 seeds the
  zero-fuel cases; MZFW is stored, not yet read.
