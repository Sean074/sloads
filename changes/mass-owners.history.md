## Step — One owner per mass quantity: the fin's typed design weight deleted, STRSPEED's weight a collapsed override of MTOW, the engine masses derived from their rows on every fixture, the yaw-inertia, wing-mass and fuselage-station overrides on the weight page, the beam waterline and the control-load geometry on the Geometry page, and a wing spanwise-mass figure (#383, design note 71, tier L, 2026-10-18)

**Objective.** Note 69 gave the Geometry page one owner per geometry quantity;
this is the mass side. After #384 and #385 no mass quantity was typed apart
from its owner on any fixture, so what remained was placement — a quantity
edited on a page that is not its owner's — and one unguarded copy,
`speeds.weight_lb`, held in line only by a drift warning. Design note 71 sets
the rule (D-71.1: a quantity the weight data base or a design weight owns has
one owner; a copy elsewhere is a collapsed override rendered beside its owner,
a non-mass field renders on the page whose quantity it is, and a copy no
program reads differently is deleted) and the owner ruled its six questions in
session.

**Deliverables.**
- **Schema v79 → v80, one hop** (`_hop_79`, D-71.4/D-71.7/D-71.9, Q6):
  `geometry.empennage.vtail.gross_weight_lb` deleted (every fixture typed it at
  MTOW; a differing value is stated once in the migration notes);
  `fuselage_mass.ref_waterline` moved to `geometry.fuselage.beam_waterline_z`
  (87.7 / 102.6 / 110.2 / 53.3 in on the four fixtures that enter it);
  `tail_mass[].control_load_mode` / `hinges_span_in` / `actuator_span_in` moved
  to the tail's control surface row in `geometry.surfaces[]` (htail → elevator,
  vtail → rudder; a tail row with no such surface has its values stated once).
  `EXPECTED_FIELDS_HASH` re-pinned; the five examples re-stamped.
- **`speeds.weight_lb` is a collapsed override of MTOW** (D-71.2, Q3):
  `structural_speeds.design_weight_lb` is the one owner — the typed value, else
  MTOW — read by STRSPEED, by the flap module's 23.345 cases and by the V-n
  balance (the flap and the balance read the field directly until this step,
  which is how a blanked fixture moved the flap digests before the owner
  existed); `cg_cases.max_takeoff_weight` no longer falls back to the copy;
  every fixture derives.
- **The engine and propeller weights derive from their rows on every fixture**
  (D-71.3, Q2): the typed copies blanked, the OV-7 selectors render in the
  Geometry page's Engines section and are marked load-bearing (G5) since
  without the link ENGLOADS has no engine mass; the supplied-set dial moves to
  19 % with that reason.
- **Page moves**: the fin yaw-inertia override (D-71.5), the wing-panel
  override with the tip/root density ratio and the inboard rib (D-71.8, Q4,
  overruling the draft) and the fuselage station table with its override switch
  (D-71.6) render on the Weight & Mass Properties page in titled groups; the
  beam waterline and the three control-load fields render on Geometry (D-71.7,
  D-71.9, Q5, overruling the draft: "they define geometry that is to be used in
  the beam model"). `tail_span.control_surface_row` reads the control surface's
  row; the Tail Mass table is mass only.
- **`wing_mass_span`** (D-71.10, Q4): a pre-run figure on the Wing Loads page
  and in report §3.1 beside the span loads — the panel mass density WINGINER
  spreads per strip, one curve per distinct FLIGHT mass state (cases sharing a
  panel share a curve and are named on it), the point masses marked at their
  butt lines and sized by weight (`Series.sizes`), read through the module's
  own `inertia_units` so the drawing and the inertia loads come from one sweep.
- **Docs**: PROGRAM_SPEC §STRSPEED, §WINGINER, §BODYLOAD's waterline paragraph,
  the T6 paragraph and the slice table; GUI_design.md's two mentions;
  CONVENTIONS.md §7's LRA-waterline row, the OV-1 row and §2's beam paragraph;
  `theory_sources.md`'s STRSPEED row; DATA_DICTIONARY and the guide regenerated.

**Test.** `tests/test_mass_owners.py`: a blank speeds weight derives MTOW
exactly, a typed one governs and warns, and the owner no longer reads the copy
(G-71.2); the hop deletes, moves and states on a synthetic v79 dict and the
result loads with the values where their readers look (G-71.3); the fourteen
moved and kept rows render on the pages the note names and the five deleted
paths are gone (G-71.4); `fuselage_lra` reads the moved waterline on every
fixture (G-71.5); no fixture types a mass quantity apart from its owner
(G-71.6); the wing-mass figure is catalogued pre-run, builds on every fixture
and its density integrates to a positive panel on each curve (G-71.8).
`tests/test_tail_span.py` and `tests/test_lra_model.py` set the discrete
control-load geometry on the elevator's and rudder's rows (G-71.7) and every
delivered tail load reproduces. **G-71.1 holds: every Imperial digest is
unchanged on every fixture**, including the flap channels once the design
weight had its owner. Gates: ruff, mypy and the whole suite green.

**Key decisions.** Q1–Q6 of note 71 §3, ruled 2026-10-18 (owner, in session):
delete the fin's typed design weight; blank the fixtures' engine and propeller
weights so the rows govern; STRSPEED's weight as a collapsed override rather
than deleted; the wing mass shape to the weight page **with** a spanwise mass
plot on the Wing Loads page (overruling the draft's "stays"); the control-load
fields to the Geometry page as beam-model geometry (overruling the draft's
"rename in place"); one migration hop for all three schema changes.
