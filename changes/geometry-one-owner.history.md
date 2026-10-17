## Step — One owner per geometry quantity on the Geometry page: the parametric wing scalars and fuselage summaries deleted, LF and the drag waterline moved to the outline, the control areas derived from the drawn surfaces, an Engines section and a pre-run airplane three-view (#378, design note 69, tier L, 2026-10-16; closes #377, #379, #380, #381)

**Objective.** The Geometry page asked for quantities the geometry entered on
the same page already determined, stored both, and tied them together loosely
or not at all: five parametric wing scalars that drifted from the planform (ga6
XLEMAC 56.73 against the planform's 63.62), three fuselage summaries copied onto
`LayoutInput` on every run, SELECT's LF typed beside an outline that knew it,
the aileron and flap areas typed beside their polylines, the engine arrangement
under a "Project" heading on one page and the engine locations on another, and
no drawing of the airplane as a whole. Design note 69 sets one rule (D-69.1: a
quantity the entered geometry determines has one owner; a stored copy is a
collapsed override where an original-suite program reads it, and deleted
otherwise) and applies it field by field.

**Deliverables.**
- **Schema v76 → v77** (`_hop_76`, D-69.12): `geometry.parametric` loses
  `wing_area_sqft`, `aspect_ratio`, `taper_ratio`, `le_sweep_deg`, `le_root_x`
  and the three fuselage summaries; `geometry.fuselage` gains
  `body_drag_waterline_z` (moved, unchanged meaning) and `airplane_length_in`
  (SELECT LF, moved from the empennage record, now a collapsed override of the
  outline's length). The hop moves the two values, drops the five keys and
  states a non-zero dropped value once. The dropped values: `ga6_normal`
  184.12 / 6.095 / 0.436 / 7.65° / 45; `baron_58` 199.2 / 7.186 / 0.5 / 2.65° /
  62; `concept_regional_jet` 500.0 / 8.712 / 0.25 / 27.2° / 480; `atr42_100`
  586.6 / 11.08 / 0.594 / 3.28° / 365; `concept_heavy` 282.2 / 8.92 / 0.5 /
  7.57° / 200. Nothing read them for a load.
- **`configuration` integrates the stored `wing` surface** (D-69.2): the
  condition is "Wing planform (WINGGEOM)" with S, span, the polylines' root and
  tip chords, MAC, XLEMAC, YMAC and AR; the stability estimate takes the same
  MAC frame; `component_stations(project)` reads the planform and the outline.
  `wing_planform`, `wing_polylines`, `wing_surface`, `wing_layout_from_surface`,
  `parametric_wing_seed`, `RECORD_SEEDS`, the seed button (#376's fix with it),
  `validation._check_area_mismatch` and the parametric branches of the taper and
  area checks are retired. `fleet` reads the planform only.
- **The fuselage summaries are gone** (D-69.3): `sob_station`,
  `vtail_root_waterline`'s no-outline fallback (now the wing root alone, stated)
  and `component_stations` call `fuselage_summary`; `sync_geometry_derived` and
  its eleven call sites are deleted.
- **Collapsed overrides with their own band** (D-69.4/7/8/10): a blank LF
  derives the outline length (`derived_geometry.airplane_length_in`); a blank
  SAFWD/SAAFT derives from the `aileron` surface's hinge split, only where it
  carries a `hinge_line` (`aileron.aileron_hinge_areas`); a blank SF derives
  from the `flap` surface's one-side area (`flap.flap_area_one_side_sqft`); all
  through the one integrator `tail_geometry.control_surface_areas` (D-69.6),
  which `boundary_derived_scalars` now calls too. `FieldEntry.band` lets a row
  state its disagreement band (`cross_check_disagrees(..., rel=)`): the control
  areas take 1 %, everything else the oracle's 0.1 %. `aileron_area_mismatch`
  and `flap_area_mismatch` warn on the Geometry page. Flap E is **parked** with
  its number (D-69.9, `02_parked.md`: 0.245–0.252 against the printed 0.27).
- **The page** (D-69.5/13/14/18, #380): Surfaces, Fuselage, Engines,
  Parametric, Empennage, aileron, flap, gear, in registry order. The Fuselage
  and Engines sections each span two record prefixes under one heading
  (`_render_groups` merges adjacent groups sharing a `DISPLAY_GROUPS` title).
  The Engines section holds `engine_layout` and, per engine, `mounted_on`,
  `engine_cg`, `prop_cg`, the thrust line and `prop_diameter_in`; Geometry owns
  the `engines[]` rows (`LIST_ROW_OWNER`) and the Engine Mount page renders the
  rows it edits with no add or delete control; the "Project" heading is gone and
  `include_far25` is titled "FAR 25 supplement". `entering_step(slice, after=)`
  lets the Flap page's later-page mark name Engine Mount for a slice now split
  across two pages.
- **The airplane three-view** (D-69.15/16, #381): three pre-run figure
  families on Geometry and in the report's §2.1 — plan, side and front, to scale
  — drawn from the owners Section 2 and Section 10 already read: the outline and
  its entered centre line, the wing and tails from their polylines, the four
  controls shaded with their hinge lines where entered, each engine's thrust
  line and a propeller disc of `prop_diameter_in`, and each gear leg with its
  wheel (main wheels at ±tread/2, owner ruling Q7). What is not entered is
  named, never sketched. The planform figures draw an entered `hinge_line`; the
  caption that said the analysis carries "no hinge geometry" is corrected and
  guarded (G-69.12).
- **Example data** (D-69.17, #381 step 4): `atr42_100`, `baron_58` and
  `concept_regional_jet` enter `elevator` and `rudder` surfaces with a hinge
  line, constructed to integrate to the former typed SELECT scalars within
  0.02 % (ATR SE 3.0/23.0, SR 2.5/19.5; Baron 2.1/18.9, 0.9/8.1; RJ 4.0/30.0,
  4.0/29.0), and the six scalars are blanked so they derive (D-54.1). Every
  example is rewritten at v77. **Found by G-69.11 and fixed in the same step
  (rule 4):** `taildist.surface_geom`, `tail_span`'s hinge-moment split and
  the `configuration` tail sketch read the raw slice's hinge halves rather than
  the resolved inputs SELECT loads with, so the first blank scalar sized the
  ATR's elevator aft area at 0 and moved its chordwise pressures by a factor of
  100; every reader now goes through `select.effective_tail_inputs` /
  `effective_vtail_inputs`, and `tests/test_example_tail_controls.py` holds
  every tail load of the three examples to the typed scalars' within 0.1 %.

**Test.** G-69.1–G-69.12 (`docs/25_notes/69_geometry_duplicates_note.md` §4,
§5.4): the Appendix A oracle and the twin closures unchanged; `ga6_normal` and
`concept_heavy` bit-identical on every delivered load (their only moved digest
channels are `configuration`'s retitled condition); the Imperial digests
regenerated deliberately for the three examples whose tail data changed
(D-69.17): `wing_geometry` and `airloads` gain the two new surfaces' rows,
`select`/`balloads`/`tail_span`/`taildist` move by the construction residual
(no module value moves past 0.1 %), and the Baron's and RJ's `balance`, balanced
deck and LRA model follow their tail loads; the v77 hop on a v76 dict and every released fixture; the
page order and one-heading rule, the rows-only engine table, the three-view
on every bundled example and on a wing-only project; the control-area band read
from the registry.

**Key decisions.** Delete, not derive-and-mark, for the five wing scalars
(Q1): the only thing they fed that was not a copy of the planform was a
different MAC frame from the analysis's. LF moves to the outline (Q2). One
heading over two prefixes, guarded (Q3). Flap E parked with its number (Q4).
Geometry owns the engine rows (Q5). The elevator and rudder polylines are
constructed to the former typed estimate, not traced (Q6). The gear wheel at the
tread, the strut from the attach (Q7).
