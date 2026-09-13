## Step — The export package reduces to one solver artifact (#263, design note 56, tier L, 2026-09-12)

**Objective.** `sloads/export/` was 8,603 lines across 15 modules shipping
**four parallel model concepts** — five per-component decks, the assembled
balanced deck, the LRA beam model, the CONM2 mass model — each with its own GID
bands, and the one that is the mission's deliverable borrowed its grids from
three that were not. Roughly two-thirds of the milestone's open export work was
maintenance on the concepts nobody ships. The owner's ruling 1 removed the hard
part before it started: **nothing downstream consumes any sbeam analysis
output**, so there is no reproducibility obligation and the renumber happens
once. Rulings 2–12 settled the rest — sizing belongs to the stress analyst
outside sloads, so core sloads produces a beam model with arbitrary properties
whose whole job is to **prove the load cases solve** with verified equilibrium.

**Agreed first.** Design note 56, AGREED 2026-09-10, amended twice during
implementation (rulings 10–12 on the applied-load model's `gid` column,
13–15 on the re-aggregation) with both corrections marked in place. The note
reverses two of its own assertions and says so: §5's acceptance of a coarser
wing distribution is withdrawn, and its "no schema change" line was wrong.

**Deliverables — ten slices.** (1) The load-output contract statements get one
owner, `deck_format`; four private `_units` copies collapse. (2) The
deliverable tables that are not decks — the case index, the governing
safety-factor table, the gear interface report, the export-scope filter — move
to `report/tables.py`, byte-identical. (3) The five per-component decks are
**deleted** (D-56.2): `sbeam_bridge.py` 2,639 → 1,413, `EXPORT_TARGETS` 10 → 4,
four bands retired, three standing limitations retired. (4) The LRA model owns
every grid it writes (D-56.3): one contiguous run `20001-30999`, eleven
999-wide sub-bands on a 1000 stride so `gid // 1000 - 20` is the family index.
(5) The beam gets its **own mesh** (D-56.4) — ends, the joint register's owned
locations, and `n` equally spaced grids strictly *between* them, `n` settable
per component (`Project.lra_mesh`, schema **65 → 66** with a migration hop).
(6a) `sbeam_bridge.py` **ceases to exist** (D-56.1): the applied-load family,
the station numbering and the side-of-body internal loads move whole to
`report/applied.py`, no shim. (7) Every `CONM2` gets its own `GRID` at its own
CG with a zero offset (D-56.6/D-56.7), unconnected by design and saying so in
the deck header; `inertia_only_cards` and `case_station_weights` retire. (6b-i)
The applied set is **re-aggregated onto the LRA grids** (D-56.9), summed through
LM-1, with the station-level set kept public as `station_applied_loads`.
(6b-ii) What the lumping costs is **published** (D-56.10): `report/lumping.py`
and oracle-report **Appendix G**. (8) The assembled deck stops shipping
(D-56.8) and `roundtrip.py` collapses 529 → 186 as `wrap_as_stick_model` goes.

Net: `export/` **8,603 → 5,307**, four model concepts → two, ten CLI export
targets → three, one load-routing path where there were two.

**Test.** Thirteen gates, all stated with their slices and all in CI. The
load-bearing ones: the mesh is **load-blind** (`test_the_lra_mesh_is_load_blind`
— the beam is decided from geometry, which is what makes the LM-1 transfer a
real transfer rather than the identity every fixture used to exercise); every
LRA grid comes from the LRA's own band and no GID is defined at two positions
across the shipped set (gates 3 and 4); the re-aggregated set carries the
assembled deck's resultant, per case, all six components (**gate 13** — the
aggregation moves no resultant); sbeam's own GPWG recovers each payload case
from the shipped mass deck, both unit systems (**gate 6**); and the beam deck
solves free-free over four fixtures with three mutation legs proving the gate
bites. Appendix G is the honest complement: the aggregation moves no resultant
but it does move the internal load at a cut, and how much is published per
surface and per channel rather than assumed.

**Key decisions.** (1) *`balanced_deck` survives a decision that reads like it
deletes it.* D-56.8's wording named two functions that live elsewhere, so on a
literal reading the deck writer had no consumer. It has one and it is
load-bearing: the deck text is the un-aggregated load set at each load's true
position, and its resultant is gate 13's anchor. It keeps its frozen digest
channel for the same reason — an anchor that can move unnoticed is not an
anchor — which makes it the one non-deliverable the Imperial baseline renders,
stated at the channel rather than left to be found. (2) *The gear reaction leg
would not move to the beam deck, and that is Appendix G arriving from the other
side.* Pointed at the shipped deck it failed — 3,334.8 lb at the nose-gear
trunnion against the gear report's 3,597.8 on `concept_regional_jet` — because
D-56.9 sums whatever else is nearest onto the same grid. Asserting the report's
number there would be asserting the lumping away, so the leg stays on the
un-aggregated set. (3) *Steps 2 and 3 were inverted for the applied-load
family.* The "move before delete" gate was reasoned on the report tables; an
AST closure showed the applied family's coupling to the deck writers is
fourteen names, all GID allocators and bands, which the delete keeps — moving
first would have meant a transitional import and a second move one slice later.
(4) *Two forecast numbers were missed and are stated, not dropped.* The band
registry was to fall from "25+ to ~8"; it is **42**, because D-56.9 was amended
to keep the station-level set public, so the station bands still number
something real. The sbeam digest channels were to fall to ~11; they are **37**,
for the same reason plus the mass model entering the baseline. (5) *Two §1
conventions retire in place rather than being deleted* — the free-body-cut rule
and E-2's per-component moment reference. A convention that retires because the
code changed shape is exactly what a reader needs to find when they propose it
again. (6) *`§1.2`'s `GID 7` illustration does not reproduce* and the note says
so three places over: the **borrowing** was real and is what D-56.3 fixes, the
position collision was not.
