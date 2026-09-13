# The export package reduces to one solver artifact (design note 56)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-09-12** — ten slices (1, 2, 3, 4, 5, 6a, 7, 6b-i,
6b-ii, 8) and the tier-L §7 closure, all on `dev/v0.8.3`; §7b is the record of
what landed and §7c of what the closure swept. **AGREED 2026-09-10** (owner, in
chat, under the solo profile — `DEVELOPMENT_PROCESS.md` §0; rule 1's
working-alone branch). The **twelve**
rulings in §2.2 are the owner's, taken in session on 2026-09-10 (7–9 on review,
10–12 during implementation); the decisions D-56.1…D-56.9 follow from them.
Raised as
[#263](https://github.com/Sean074/sloads/issues/263), band B4 — the slot
note 55 (#172) vacated at close, which is fitting: this note is its direct
successor and closes the question note 55 could only mitigate.

**Tier L.** A contract change to a published artifact set: four shipped solver
artifacts become two, and every exported id moves. No delivered load changes.

Measurements in §1 are taken at `dev/v0.8.3` after #262 and #172, i.e. with the
joint register (note 54 D-54.5) and the solvability fixes (note 55) in place.

**Amended 2026-09-10, before implementation** (owner flagged, note-55 D-55.6
precedent): D-56.2's consumer count was measured on `export_report.py` alone
and said "the GUI Export page". There are **seven** `app/views/` consumers;
the decision is unchanged, its blast radius in the main GUI is not. No
decision text other than that sentence moved.

**Amended again 2026-09-10, during implementation** (rulings 10–12 below, owner,
in session). The applied-load family could not be rehomed without settling what
its `gid` column means once the per-component decks are gone, and the answer —
*the LRA grids are where the loads and moments are calculated* — is a stronger
statement than this note originally made. It adds **D-56.9**, gives **D-56.4**
its mesh rule, and **reverses two things this note asserted**: §5's acceptance
of a coarser wing distribution is withdrawn, and §7's "no schema change" is
wrong — settable per-component grid counts are persisted input, so
`SCHEMA_VERSION` bumps with a migration hop. Both corrections are marked in
place rather than edited away.

---

## 1. What the code does today, and what is missing

### 1.1 Four model concepts, one id space

`sloads/export/` is **8,603 lines** across 15 modules; `sbeam_bridge.py` alone is
**3,091**. It ships four parallel model concepts:

| # | artifact | grids | elements | claim |
|---|---|---|---|---|
| 1 | per-component decks — wing stick, body, tail chord, tail span, control | 1–5600 | wing stick only | free-body **views** |
| 2 | balanced deck | 6001–7000, 10001+ | none | equilibrium **proof** |
| 3 | **LRA beam model** | 1–1000, 4001–5600, 7001–7880 | CBAR 11001+, RBE2 12001+ | the **deliverable** |
| 4 | CONM2 mass model | EID 9001+ | — | mass cross-check |

### 1.2 The deliverable does not own its grids

`lra_model.py:118-124` imports `station_gid`, `tail_span_gid`, `tail_control_gid`
and `sob_gid` from `sbeam_bridge`. At `lra_model.py:488` the right wing chain
takes its GIDs **directly from the wing stick model's band**:

```python
right = [sob_r] + [LraNode(nl.gid, (nl.x, nl.y, nl.z)) for nl in outboard]
```

So GID 7 names one point in `wing_loads.bdf` and a different point in
`lra_model.bdf`. The LRA model mints its own numbering only for the left wing,
fuselage, hub, engine and attach nodes. `bands.py` (355 lines) and its drift
guard `tests/test_bands.py` (243) exist largely to police a namespace that is
this crowded *because* four model concepts share it — the registry's own
docstring records the 4001 collision that created it.

`mass_cards.py:77` has the same dependency: `beam_station_gid`, i.e. the **body
deck's** 1001+ band. The mass model's node line is owned by an artifact that is
not the deliverable.

### 1.3 The beam mesh is the load mesh, and the load mesh is oracle-locked

`build_lra_model` calls `build_net_loads(project)` and `build_tail_span(project)`,
so the beam's node line **is** the load integrator's strip midpoints. Measured:
the wing is **20 strips on every fixture** — WINGGEOM's discretization, part of
the replication contract, which cannot move without breaking Appendix A. The
models are small: 84–115 nodes and 9–10 `RBE2`s across the six fixtures.

This is the generator of note 55's sliver class. A joint must be *inserted* into
a mesh chosen for load-integration reasons: `cessna_210`'s h-tail attachment
landed 0.0769 in from a station (1.07 % of `ds`, a 1638:1 element-length ratio),
`baron_58` next at 1.33 %. Note 55 mitigated it with `JOINT_MERGE_FRACTION` at
5 % of `ds` — `baron_58` is inside that band today, absorbed rather than clear.
The class is alive; only its current instances are handled.

### 1.4 The degenerate routing path is the only one CI exercises

Two paths route loads onto beam nodes, and they already share one owner —
`transfer_couple`, called at `lra_import.py:259` and `lra_model.py:882`. But when
beam nodes *are* load stations, the spanwise half of `(p − n) × F` is identity.
Every CI fixture therefore exercises the degenerate case, while the general case
— arbitrary grids at arbitrary positions, which is what `lra_import` does and
what a user with their own beam model hits first — is the least covered.

### 1.5 `sbeam_bridge.py` is not mostly deletable

The naive reading of §1.1 is "delete the bridge". That would take the oracle
report — the one actively-used deliverable — with it. Seven production sites
reach in:

| caller | symbols |
|---|---|
| `report/oracle_sections.py` | `applied_loads(...)` ×4, `applied_body_moments`, `body_station_gids` |
| `report/content.py` | `sob_internal_loads`, `case_index_rows_from`, `LOAD_ID_COLUMN` |
| `report/methods.py` | `CENTERLINE_CLAMP_NOTE` |

`applied_loads` is the OR-141 single entry point — *"a table a stress analyst
reads, a file they load and the deck they solve cannot disagree about what the
applied set is."* The `AppliedLoad` family is **report infrastructure filed under
the wrong name**, not surplus. Every `sloads/modules/*` reference to the bridge
is docstring prose; there is no calc dependency.

### 1.6 Where the open work is going

Of the open 0.8.3 rows, roughly **two-thirds of export work is maintenance on
artifacts that are not the deliverable**: #241, #242, #245, #209, #191, #176,
#173, #16, #17's `_export_sbeam`, #254. Against that, the LRA/balanced chain
carries #173 (one paragraph) and #188.

---

## 2. Governing basis

### 2.1 What the mission actually asks

`CLAUDE.md`: *"the exported deck solves in sbeam with verified global equilibrium,
continuously in CI"*, with the FAR23 core oracle-locked. Nothing in the mission
asks for per-component solver decks; `PROJECT_GUIDE.md` already calls them
analysis views. Note 55 made the solve claim true on all six fixtures.

### 2.2 Owner rulings (2026-09-10, in session)

1. **Nothing downstream actively uses any sbeam analysis output.** No
   reproducibility obligation — decks, digests and GIDs are free to move, and the
   renumber happens once.
2. **Sizing belongs to the stress analyst, outside sloads.** Core sloads produces
   an LRA beam model with **arbitrary** beam properties plus the load cards on its
   grids, to prove the load cases solve in sbeam or NASTRAN. That is the whole job.
3. **`lra_import` stays in core**, with a thin CLI wrapper. *(Amends an earlier
   ruling in the same session that sent it to a script.)* The intended future is
   **user-defined LRA grids imported as a BDF**, with aero and inertia summing onto
   them — so import is a primary entry, not a downstream convenience.
4. **CONM2 stays a deliverable and stays in core**, gaining **its own GRIDs at each
   mass item's CG**. No tool script.
5. **The LRA beam gets its own mesh — joint-driven and minimal.** The generated
   model is a *minimal reference default*; it retires naturally if import becomes
   universal.
6. Oracle-GUI per-page output buttons retire in favour of the document build's
   `data/` channel. **This is already #245's scope**, not new work.

*Follow-up rulings, same session (2026-09-10), taken on review:*

7. **The default beam builder stays in sloads**, with generic (arbitrary)
   properties — confirming ruling 5 against the alternative of moving default
   beam construction into sbeam. sloads ships the full solvable BDF, not just
   grids and loads.
8. **Gear, engine and control-surface loads stay in the LRA export** as point
   loads at their joint nodes; "distributed" describes the four member chains
   (wing, fuselage, h-tail, v-tail), not the whole applied set. Nothing the
   balanced cases carry is dropped.
9. **The CONM2 deck is a standalone cross-check** to enable the end user's own
   checks. It is never combined with the load subcases — the distributed loads
   already contain the inertia, so combining would double-count (the
   `mass_cards.py` header's own warning). Attaching the CG grids to any
   stiffness model is the **user's** job, via RBE connections they create to
   whatever model they are assessing; this holds unchanged under an imported
   user LRA model. The "spliced into a load deck" capability retires with the
   offsets (see D-56.6).

*Further rulings, same session (2026-09-10), taken when the applied-load family
would not move:*

10. **The LRA builder creates the grids, and those grids are where the loads
    and moments are calculated.** Not a mesh that loads are transferred *onto*
    after the fact — the LRA grid is the point at which the component's applied
    load is stated. This is what makes D-56.9 possible and what keeps the
    appendix row and the deck card the same object.
11. **Grid placement is equal spacing along each member, plus every owned
    point** (the joint register's locations, member ends, gear/engine/hinge
    nodes). Equal spacing is load-blind by construction.
12. **The per-member grid counts are settable by component**, defaulting to a
    stated table; the **wing stays at 20 per side** — today's resolution, not
    reduced, because under ruling 10 this is the resolution of a *delivered*
    load set rather than of an internal check.

**Rulings 13–15 (2026-09-12, owner, in session — taken at slice 6b's design
fork).** Implementation reached D-56.9 and found that the decision as written
could not be built: the LRA deck sums every source onto each node, so a card has
no single station-level row to be matched against. The owner's answer went
further than any of the three options put up, and these three rulings are it.

13. **The LRA grids are the reporting grids, and the loads are summed to them.**
    Aerodynamic and inertial forces are summed *onto* the LRA grid — several
    aero stations and several mass items onto one grid where the sets do not
    align, which they generally do not. The applied set is re-aggregated, not
    relabelled.
14. **The difference this produces is shown, not absorbed.** "As these grid sets
    do not align that may mean multiple aerodynamic force grids are summed to an
    LRA grid, likewise with the inertial loads. This will result in some
    difference as they are different locations. In the report a VMT plot should
    be added to show this difference."
15. **Stated, not gated with a tolerance** — the resultant identity stays exact
    and gated; the distribution difference is plotted and quantified. Four
    figures (wing, fuselage, h-tail, fin) on **one shared critical case**, both
    curves computed, no solver in the loop; the per-strip view stays in section 4
    and the appendix follows the deck.

**Ruling 16 (2026-09-12, owner, in session — taken at slice 7's verification.)**
Verifying gate 6's precondition showed D-56.6 costs three solver legs, and the
owner accepted the trade: **GPWG replaces the solve.**

16. **The mass model is checked by GPWG, not by a stiffness solve.** Ruling 9
    makes the CG grids unconnected by design, so `SOL 101` cannot run on the mass
    deck at all — `test_the_mass_deck_accelerates_and_reproduces_sloads_inertia`'s
    three legs (M-a total, M-b card-for-card, M-c the cases differ) lose their
    load path. M-b goes by design, since it compares against `inertia_only_cards`
    which D-56.7 retires. **M-a and M-c are a real loss and are recorded as one**:
    sbeam's own mass-matrix assembly and the `GRAV` acceleration path stop being
    exercised, in both unit systems — and the SI leg is what caught the 25.4×
    `GRAV` slip in the 2026-08-10 review (C1/F-G2). Rejected alternative:
    *ship an optional `RBE2` tie so the check can still solve.* It re-creates
    exactly the coupling D-56.6 removes, and ruling 4 already rejected attaching
    the mass model to the LRA grids; a deck that exists only to be solved by its
    own test is the maintenance D-56.2 removed. **The compensation is real and
    was measured, not assumed:** GPWG honours `MASSSET` where `SOL 101` does not
    — on the shipped `ga6_normal` deck it returns each case's mass exactly
    (CG1/CG4 = 1.648 = 3400/2063, CG3/CG4 = 1.357 = 2800/2063) — so gate 6 reads
    **the deck as shipped**, per case, in both unit systems, where the solve legs
    had to flatten each case into a baseline deck to work around the pinned
    `MASSSET` gap. The SI channel is therefore still checked; it is checked
    without the acceleration path.

### 2.3 Two facts that close sub-questions without a decision

* **There is no "sbeam json".** sbeam's only input is NASTRAN bulk data
  (`sbeam/parser/bdf_reader.py`, `bdf_field.py`, `case_control.py`); not one file
  in the installed package mentions JSON. A converter reading one cannot be built,
  and the distributed weight data lives in sloads' own `project.weight.items`.
* **`read_lra_model` needs only `GRID` cards** — CBARs are optional; it raises
  only when there are none. A user-defined LRA *node line* is sufficient input,
  which is what makes ruling 3 cheap.

---

## 3. Decisions proposed

| # | Decision | Alternative rejected |
|---|---|---|
| **D-56.1** | **`sbeam_bridge.py` splits three ways and ceases to exist.** The applied-load model (`AppliedLoad`, `applied_loads` + its five row builders, `applied_body_moments`, `sob_internal_loads`, ~600 lines) and the report tables (case index, `safety_factors_csv`, `gear_report_csv`, `filter_by_selected_case_ids`, `LOAD_ID_COLUMN`, `CENTERLINE_CLAMP_NOTE`, ~370) **move to `report/`**; the per-component decks (~1,900) are **deleted**. | *Package-split it in place* (#191's plan). Rejected: it preserves the misfiling. Two of the three groups are report code that never belonged in an export bridge, and the third is being deleted — splitting first means moving the same lines twice. |
| **D-56.2** | **The per-component solver decks are deleted** — wing stick BDF + span CSV, body, tail chordwise, tail span, control surface, cards *and* companion CSVs. Their non-test consumers are **seven `app/views/` modules**, not one: `export_report.py` (17 symbols), `wing_loads.py` (`applied_load_csv`, `span_load_csv`), `fuselage_loads.py` (`body_span_load_csv`), `tab_loads.py`, `aileron_loads.py` and `flap_loads.py` (`control_surface_csv`, `control_surface_force_moment_cards`) and `landing_loads.py` (`gear_report_csv`). Of those, `applied_load_csv` and `gear_report_csv` are in D-56.1's **move** group, so their pages re-point at `report/`; the rest are in the delete group, so **those per-page download buttons go with the decks**. That is a consequence of this decision in the main GUI, not #245's oracle-GUI channel — ruling 6 does not cover it. `tail_span_force_moment_cards` has **zero** production consumers. | *Keep them as views.* Rejected under ruling 1: they are not used, they own five GID bands the deliverable borrows from, and they carry most of the milestone's open export work. |
| **D-56.3** | **The LRA model owns one contiguous grid band.** It stops importing `station_gid` / `tail_span_gid` / `tail_control_gid` / `sob_gid`. Every shipped artifact's grids come from exactly one band it owns, so no GID is defined at two positions anywhere in the set. `bands.py` collapses from 25+ bands to ~8. | *Keep the borrowing and just delete the borrowed-from decks.* Not viable: the bands would survive as orphans owned by deleted code, which is the blind spot the registry exists to close. |
| **D-56.4** | **The LRA beam gets its own mesh: equal spacing plus every owned point** (amended, rulings 10–12; it read "joint-driven, minimal" when this note was agreed). The node set of a member is the joint register's owned locations, the member's ends, its gear / engine / hinge / actuator nodes, and **`n` equally spaced grids along it**, `n` per component and settable, defaulting to a stated table with the **wing at 20 per side**. Equal spacing is the load-bearing half of the rule: it is decided from geometry alone, so it cannot coincide with the load stations, and the LM-1 transfer is therefore exercised for real on every fixture — which is the whole argument in §1.4. A count-matching rule would leave most strips on their own node and the transfer an identity again, reproducing the defect under a new name. Nodes are the joints and load-transfer points plus those intermediates; loads land by LM-1 `(p − n) × F`, already the shared owner. Joints become mesh points **by construction**, so note 55's sliver class dies structurally and `JOINT_MERGE_FRACTION` and the sliver leg of `_refuse_unsolvable_skeleton` retire. The wing load mesh stays oracle-locked at 20 strips; it simply stops being the beam. | *Keep it welded* (note 55's posture). Rejected on §1.4: a welded mesh is a degenerate special case that hides the general one, so the arbitrary-grid path a real user hits first stays the least tested. *Formalise the merge rule instead.* Rejected: it maintains the class rather than removing it. |
| **D-56.5** | **`lra_import` stays in core; the "script" is a thin CLI entry point over it.** Importing an unsized LRA definition as the load target and putting loads on an already-sized model are the same code at different vintages. The `LRA_IMPORT_TOL_IN` validation against the project's own geometry stays with it. | *Move it to `scripts/`.* Rejected after ruling 3: the geometry validation needs core, and a second copy of the LM-1 transfer would become likely — forking the one rule this note exists to unify. |
| **D-56.6** | **CONM2 creates its own `GRID` at each mass item's CG**, with a zero-offset `CONM2` on it. `_attach_gid` and its CR-B-1 nearest-station tie rule, the offset arithmetic and the `beam_station_gid` import all go. `conm2_fragment` becomes self-contained and converges with `mass_check_deck`, which keeps only its case control and `GRAV`. The wing-item limitation `_attach_gid` documents **retires** — it was waiting on plan 11 B5, which shipped. The CG grids are **unconnected by design** (ruling 9): sloads ships no tie, and a CONM2 on an unconnected grid is singular in any stiffness solve — so the "spliced into a load deck" capability the `mass_cards.py` band comment documents retires with the offsets, and that prose is re-cut. The user RBEs the CG grids to whatever model they assess. | *Attach to the LRA model's grids.* Rejected by ruling 4: it re-creates the coupling this note removes, and ties the mass model's validity to a beam mesh that is explicitly a minimal default. *Keep a mass-only fuselage station line.* Rejected: it keeps the wing-item limitation alive permanently. |
| **D-56.7** | **`inertia_only_cards` retires.** It exists to compare sloads' reduction of a mass to a beam station against sbeam's GPWG recovery. With each mass at its own CG there is no reduction left to check. | *Keep it as a regression check.* Rejected: it would compare two identities. |
| **D-56.8** | **`balanced_deck` demotes to an internal producer.** Its cases feed the LRA transfer and the report's `balanced_case_rows`; no `.bdf` ships. A table is in the issue package **iff the document draws it** — the rule `data/<step_key>.csv` already states. Deck-companion CSVs nothing draws are deleted with their decks. | *Keep shipping it as the equilibrium proof.* Rejected: the proof is a CI gate, not a deliverable, and the LRA deck carries the same resultant. This also makes #173 moot rather than fixed. |
| **D-56.9** *(added by amendment, ruling 10; **rewritten by amendment 2026-09-12, ruling 13** — the original text is quoted in §6)* | **The applied load set is re-aggregated onto the LRA grids.** Not relabelled: *summed*. A component's applied set stops being one row per load-integration station and becomes **one row per (case, LRA grid)**, with every aerodynamic and inertial contribution that routes to that grid summed into it through LM-1 (`coordinates.transfer_couple`, the existing owner — the same rule `lra_model.transferred_case_loads` already applies, so there is one routing rule and not a second one written for the report). Several aero stations and several mass items therefore land on one grid, which is the point: the appendix row, the `*_applied_loads.csv` row and the `FORCE`/`MOMENT` card are then **one object at one point**, which is what the row-for-card claim always meant and what the per-component decks happened to provide. `AppliedLoad.gid` is an LRA grid and stops being `Optional` — a concentrated mass gets a grid like anything else. The seven bands the applied model allocated from (`wing-stick`, `body-mass`, `body-reaction`, the two `tail-span` and the two `tail-control` runs) retire, and `wing-stick`'s `GID 1` hole closes with them. **G-OR-90 keeps its form and changes its authority**: it reads the LRA deck, still card-first, still one case at a time — and the form is now *true*, because with one aggregation rule a component's rows at a grid and the card at that grid cannot disagree. | *Relabel the rows with the nearest LRA grid and leave the station-level decomposition intact* (what this decision said before the rewrite). Rejected on measurement, not taste: the LRA deck emits one `SUBCASE` per **balanced** case and `transferred_case_loads` sums every source onto each node, so a card at a grid has contributions from several components and matches no single station-level row. Card-first row-matching cannot hold against a summing deck — the gate would have had to weaken to a resultant identity, and the appendix would have kept describing a decomposition the delivered artifact does not have. *Make the applied set the literal card writer, replacing `transferred_case_loads`.* Rejected as a different change: the component sets do not carry the balanced case's inertia relief, so this would move G-OR-72's `nz × W` closure onto new machinery in a slice that is about addressing, not about what the deck is. |
| **D-56.10** *(added by amendment 2026-09-12, ruling 14)* | **The report states what the re-aggregation costs, as a VMT comparison.** LM-1 preserves each load's resultant about the node it lands on **exactly**, so the total resultant is unchanged and already gated. What moves is the **distribution**: a load that crosses a cut on its way to its assigned node takes its contribution to the internal V/M/T at that cut with it. That is a real discretization difference, it is a direct consequence of the mesh being load-blind by design (D-56.4), and the report states it rather than leaving a reader to discover it. A new section carries **four figures — wing, fuselage, h-tail, fin — for one shared critical case**, each plotting the calc's own distributed VMT against the VMT re-derived from the LRA-lumped applied set, with the worst deviation over **all** cases stated numerically beside them. **Amended 2026-09-12, at implementation, on two points of the sentence before this one — the ruling is unchanged and both changes are recorded in §7b.** (i) *One shared case is not available.* The four components' condition registers are disjoint by construction — the wing runs `W-nn`, the fuselage `F-nn`, the h-tail `HT-nn`, the fin `VT-nn`, each surface's own FAR conditions — so no case is run by more than one of them and there is nothing to share. Each figure names its own case, and it is that member's **most heavily bent** one, which is what "critical" means to a reader; the worst *lumping* is a different question and the table answers it over every case. (ii) *The deviation is plotted, not the two curves.* Six curves — three channels in two versions — carry three dimensions and cannot share one y-axis, and normalising them to share one puts six colourless lines in a figure that must stay legible in greyscale (`ORACLE_REPORT.md` §4.3). Nothing is lost: **both sets are already printed in full**, the station set in the cumulative appendices (B.2, C.2) and the delivered set in the applied ones (B.1, C.1, D, E). The difference between them was the one thing missing, and it is what the figure now is. **No solver is in the loop**: both curves are computed, so the figure is a discretization comparison and not an idealisation comparison, and it is reproducible in CI. | *Compare against sbeam's solved internal loads.* Rejected: it puts the solver's own idealisation into the same plot as the lumping error and a reader cannot tell which they are looking at. *Gate the deviation with a hard tolerance.* Rejected **for now** (ruling 15, and see gate 12): the deviation is a legitimate function of a user-settable grid count, so a fixed tolerance would fail a coarse mesh that is behaving exactly as specified. The number would also have to come from a measurement nobody has taken. It is stated and plotted; the resultant identity beside it stays exact and gated. | 

**`EXPORT_TARGETS`** (`cli.py:89`) goes from ten to **`("lra", "mass")`**, plus
`--lra-import`.

**Incidental correction, swept with the implementation:** the docstring of
`transferred_case_loads` (`lra_model.py:873`) says "the limit→ultimate factor
is applied at emission" — stale prose contradicting its own signature line
(**LIMIT**) and OR-116. The code applies nothing (G-OR-71 guards the multiply);
the sentence is deleted.

---

## 4. Gates

1. **The oracle report is byte-identical across the move.** `tests/test_oracle_report*.py`
   and `tests/test_report_content.py` pass unchanged after D-56.1's relocation,
   **before** any deletion. This is the gate that makes the sequencing safe.
2. **Every CLI-exportable fixture still solves**, reaction equal to minus the
   applied resultant — note 55's widened gate, unchanged in scope.
3. **No GID is defined at two positions** across the shipped artifact set; a
   registry walk proves it, replacing the disjointness guard's current job.
4. **Every LRA node's GID is from the LRA's own band** — the D-56.3 identity,
   asserted from the emitted deck text.
5. **No sliver is possible.** Every joint is a mesh point by construction; the
   note-55 sliver gate becomes vacuous and is replaced by the construction
   assertion. Mutation-tested.
6. **CONM2 re-grid is mass-neutral**: GPWG total mass and CG unchanged by the
   move to CG grids — the masses did not move, only the nodes they sit on.
   **Precondition verified 2026-09-12** (it was the note's one open unknown):
   `sbeam.gpwg.compute_gpwg` walks `CONM2` cards and grid positions directly, with
   no stiffness matrix and no connectivity, so a deck of grids and masses with
   **no elements and no `SPC`** returns the hand-computed mass and CG exactly. It
   applies a `CONM2` offset identically, so a mass at a beam station with an
   offset and the same mass at its own CG grid with zero offset give the same
   answer. **The tolerance is the deck's own print precision, measured not
   guessed:** GPWG reads the *printed* cards, and `deck_format.fmt` writes seven
   significant figures, so agreement is bounded at ~1e-7 by the artifact itself
   (worst over five fixtures × two unit systems × every mass case: **1.3e-7**,
   on `concept_heavy` — `46.62142525735088` prints as `4.662143E+01`). The gate
   is `rel_tol=1e-6` with that reason stated; a tighter one would be asserting
   that a seven-figure field carries more than seven figures.
   **Amended the same day, ruling 16: the inertia clause is struck.**
   `GpwgResult` is `total_mass, cg_x, cg_y, cg_z, massset_sid, massset_label` —
   the pinned sbeam has no GPWG inertia producer, so that third of the gate named
   an output that does not exist and had no authority to check against. Struck
   with its reason rather than left standing as an unrunnable clause.
7. **`EXPORT_TARGETS == ("lra", "mass")`**, and `tests/test_cli.py` proves no
   retired target is reachable.
8. **The delivered loads do not move.** Module views, case index, both reports
   and the CSVs are byte-identical; only `sbeam/*` digest channels change, and 72
   of the 83 retire. **Amended:** the `*_applied_loads.csv` files are the one
   exception, and a stated one — D-56.9 re-points their `gid` column at the LRA
   grids, so their bytes change by construction. Every other channel holds, and
   the resultant of each applied set is unchanged, which is gate 9's job.
9. *(added by amendment)* **G-OR-90 keeps its teeth against the LRA deck.**
   `tests/test_oracle_report_applied.py` runs unchanged in form — card-first,
   one case at a time — with the LRA deck as its authority. Mutation-tested: the
   omission class it was written for (note 44 OR-139, a component's torsion
   absent from the appendix but present on the card) must still fail it.
10. *(added by amendment)* **The LRA mesh is load-blind.** No member's node
    positions depend on the load stations: asserted by construction on every
    fixture, and by the stronger property that changing a component's grid count
    changes no delivered resultant — only how finely it is distributed. This is
    the gate that keeps D-56.4's equal-spacing argument true rather than
    asserted, and it is what makes the LM-1 transfer non-identity in CI.
12. *(added by amendment 2026-09-12)* **Every applied row is at an LRA grid,
    and every card is accounted for.** No `AppliedLoad` carries a gid outside the
    LRA's own run; `gid` is not `Optional`; the seven retired bands are gone from
    the registry and nothing allocates from them. Card-first against the LRA
    deck, one case at a time: every `FORCE`/`MOMENT` card the deck writes is
    found in the applied set at that grid, and the components agree. Mutation-
    tested against the note 44 OR-139 omission class the gate was written for.
13. *(added by amendment 2026-09-12)* **The re-aggregation moves no resultant,
    and says how much it moves the distribution.** Per component and per case,
    the summed applied set's resultant about any point equals the un-aggregated
    set's — exactly, LM-1 being the only rule applied (this is the half that is
    gated). The distribution difference is *stated*, not bounded: the report's
    VMT comparison renders for every fixture and the worst deviation over all
    cases is printed. A guard asserts the statement exists and is non-empty, so
    the figure cannot silently stop being drawn — per ruling 15 it asserts no
    tolerance on the deviation itself.

11. *(added by amendment)* **The schema hop is complete.** `SCHEMA_VERSION` 65 →
    66; a project written at 65 loads and produces the D-56.4 default counts;
    `tests/test_schema_guards.py` and `tests/test_project_units.py` both pass,
    the latter meaning the new count fields are classified as dimensionless with
    a reason rather than left out of the total classification.

---

## 5. Effect vs error bar (rule 6)

Rule 6 ranks a **physics/fidelity** item by its effect on a delivered load
against the base method's uncertainty. **This note is not such an item and rule 6
does not gate it**: no delivered load changes, and gate 8 asserts that.

Its justification is maintenance cost and correctness of coverage, and both are
measured rather than asserted: ~4,000 lines deleted, four model concepts to two,
25+ id bands to ~8, 83 sbeam digest channels to ~11, and — the substantive one —
two load-routing paths to one, which moves the general case from least-tested to
always-tested.

**One honest consequence to state.** The LRA model's stated value is *the internal
loads a solver recovers at the named nodes* — the wing side of body, the spar
posts, the fin root, the h-tail attachments. Those are joints, and joints remain
mesh points under D-56.4, so those recoveries are preserved. What becomes coarser
is the wing's **spanwise internal load distribution** between joints. That is
accepted: ruling 2 makes the generated model a solvability proof with arbitrary
properties, not a sizing model, and ruling 3 makes a user's own mesh the path to
anything finer.

> **Withdrawn by the 2026-09-10 amendment (rulings 10–12).** The paragraph above
> is left standing because the reasoning that failed is worth keeping visible.
> It is sound only while the LRA grids are somewhere to *hang* a check. Ruling 10
> makes them the points at which the loads and moments are **calculated and
> stated**, so the grid count is the resolution of a delivered load set, and
> "coarser is accepted because this is only a solvability proof" no longer
> follows from ruling 2 — the model is a solvability proof *and* the thing that
> carries the loads. Hence ruling 12's wing at 20 per side: today's resolution,
> held rather than reduced. The narrower claim survives intact — the named-node
> recoveries are preserved because joints are mesh points by construction.

---

## 6. What this supersedes / corrects

* **#173** and **#176** become **moot**, not fixed — the balanced deck stops
  being a shipped artifact and the `balanced` export target goes. Closed as
  superseded, citing this note.
* **#191** loses its `sbeam_bridge` half (D-56.1 replaces a split with a
  dissolution) and reduces to `modules/balance.py`. Its line counts are stale:
  `sbeam_bridge` 2,701 → **3,091**, `balance.py` 2,832 → **2,842**. Its named
  future candidate `report/content.py` becomes *more* pressing — `report/` grows
  by ~970 lines here.
* **Note 55** is not withdrawn: D-55.1 (tie-parent filter), D-55.5 (the refusal
  backstop) and D-55.6 (the support picker) all stand. **D-55.2 and D-55.3 are
  superseded by D-56.4** — the merge tolerance and the split epsilon exist to
  survive joints landing near stations, which cannot happen once joints *are*
  stations. The note's §8 deferral of a dedicated support node beside the
  carry-through is **promoted into D-56.4's mesh rule**, which should place one.
* **#245 is not superseded.** Ruling 6 is already its stated scope (*"the
  per-module CSV/text buttons and the results zip retiring in the same change"*).
  This note tells #245 which tables no longer need a home and narrows its
  column-inventory pass; the two coordinate.
* **#241 is not superseded** — the `AppliedLoad` model moves, it does not die, so
  the missing case identity still needs fixing at its new address.
* **This note corrects itself at D-56.9** (2026-09-12, rulings 13–15). The
  decision as first written read: *"The applied load set is stated at the LRA
  grids, and `AppliedLoad.gid` is an LRA grid. The component appendices and the
  `*_applied_loads.csv` files quote the node the deck actually carries the load
  at."* Quoted rather than edited away, because the correction is the useful
  part. "Quote the node" is ambiguous between **relabelling** a station-level row
  with a nearby grid and **summing** the station-level rows onto that grid, and
  only the second is buildable: the LRA deck emits one `SUBCASE` per *balanced*
  case and sums every source onto each node, so a card at a grid corresponds to
  no single station-level row and card-first matching has nothing to match. The
  original wording also assumed the two grid sets could be put in correspondence
  at all, which D-56.4 had already made false on purpose — a load-blind mesh does
  not align with the load stations, and that is the property §1.4 wanted.
  **D-56.10 exists because of the same correction**: once the sets are summed
  rather than paired, there is a distribution difference to state, and the note
  had no place to state it.
* **#209 narrows again.** The case index's `LOAD/SUBCASE (component)` column
  named per-component decks that D-56.2 deleted; after D-56.9 the applied rows
  are addressed by LRA grid, so the column's remaining question — index or load
  table — is asked against one deck rather than five.

---

## 7. Closure obligations (tier L)

* `changes/<slug>.changed.md` + `changes/<slug>.history.md` in **full step
  format**.
* `docs/10_standard/CONVENTIONS.md` §7 — the joint-register and
  skeleton-solvability rows re-cut; a new row for "every shipped artifact's grids
  come from one band it owns".
* `docs/10_standard/PROGRAM_SPEC.md` — the export section re-cut to two targets.
* `docs/10_standard/PROJECT_GUIDE.md` — package tree; the "all five sbeam CSVs,
  all five decks" sentence in the frozen-baseline paragraph is now wrong and must
  be re-cut with the channel count.
* `docs/00_INDEX.md` — row for this note *(landed with the note)*.
* **The seven `app/views/` modules D-56.2 names.** Removing a download button whose backing writer no longer exists is a consequence of this note, not #29's GUI review, so the `app/views/` hold does not bar it and no OR-15 admission is sought. Nothing else on those pages is touched, and the fragment states which buttons went.
* **No `theory_sources.md` citation.** Stated explicitly rather than silently
  omitted: this note changes no equation and cites no oracle. Gate 8 is why.
* ~~**No schema change.** `SCHEMA_VERSION` stands; `DATA_DICTIONARY.md`
  regeneration is a no-op.~~ **Wrong, corrected by the 2026-09-10 amendment.**
  Ruling 12 makes the per-member grid counts settable by component, and they are
  *input*: the project file is the record from which a deliverable reproduces,
  so a count that lived only in a CLI flag or a GUI widget would make two runs of
  one project legitimately disagree. Persisted input means the documented
  procedure applies in full (`PROJECT_GUIDE.md`: *"When you change a persisted
  dataclass, bump `SCHEMA_VERSION` — not optional"*): **65 → 66**, a migration
  hop in `sloads/migrations.py` defaulting existing projects to the D-56.4 table,
  `DATA_DICTIONARY.md` regenerated through its generator, and the new fields
  classified in `units._PROJECT_FIELD_KIND` — they are **dimensionless counts**,
  which that classification must state with its reason rather than leave
  unclassified.
* One **bulk digest re-stamp**, at the end, as a single wave with the claim in
  the fragment (`DEVELOPMENT_PROCESS.md` §231: a PR carries at most one).
* *(added 2026-09-12, D-56.10)* `docs/10_standard/ORACLE_REPORT.md` — the VMT
  comparison's section, its four figures and the deviation statement, with the
  gates it carries; `docs/10_standard/PROGRAM_SPEC.md`'s report content list
  gains the section. The figure is new *content*, so it is specified where the
  report's content rules live and not only in this note.
* *(added 2026-09-12, D-56.9 rewrite)* `docs/20_theory/00_theory_sources.md` —
  **a citation after all**, reversing the "no citation" line above for this one
  decision. Re-aggregating a distributed load onto a coarser node set is a
  discretization choice with a stated consequence, so the lumping rule (LM-1, and
  what it does and does not preserve) is cited where the method's basis lives.
  Gate 13 is its closure gate; there is no printed oracle for it.

---

## 7b. Implementation record

Written as the slices land, so the note stays the account of what happened and
not only of what was intended.

| slice | what landed | date |
|---|---|---|
| 1 | **The load-output contract statements get one owner.** `deck_format` takes `solver_units`, `load_label`, `ult_label`, `SUITE_SF`, `case_sf`, `basis_sentence`; four private `_units` copies and four inline `Channel.SOLVER` resolutions collapse onto one. A drift guard pins `deck_format.py` as the only module in `export/` that resolves the solver channel. | 2026-09-10 |
| 2 | **The deliverable tables that are not decks move to `report/`.** The case index, the governing safety-factor table, the gear interface report and the export-scope filter become `sloads/report/tables.py`; the export package stops re-exporting them and a guard asserts their absence. Deliverables byte-identical. | 2026-09-10 |
| 3 | **The five per-component decks are deleted** (D-56.2). `sbeam_bridge.py` 2,639 → 1,413; `EXPORT_TARGETS` 10 → 4; band registry retires four blocks; three standing limitations retire; sbeam digest channels 83 → 33. | 2026-09-11 |
| 4 | **The LRA model owns every grid it writes** (D-56.3). One contiguous run, `20001-30999`, eleven 999-wide sub-bands on a 1000 stride so `gid // 1000 - 20` is the family index; `sob_gid` moves to `lra_model`; gates 3 and 4 land. Only `sbeam/lra_model` re-stamps. | 2026-09-11 |
| 5 | **The LRA beam gets its own mesh** (D-56.4). Ends + owned points + equally spaced grids *between* them; counts settable per component (`Project.lra_mesh`, schema 65 -> 66) at wing 20/side, fuselage 12/cantilever, h-tail 12/side, fin 10; members run to their tips; `JOINT_MERGE_FRACTION` retires; gates 5, 10 and 11 land. Only `sbeam/lra_model` re-stamps. | 2026-09-11 |
| 6a | **``sbeam_bridge.py`` ceases to exist** (D-56.1). The applied-load family, the station numbering and the side-of-body internal loads move whole to ``report/applied.py``; the export package stops re-exporting them and no shim is left. Two guards land: one address per name in both directions, and no importable ``sbeam_bridge``. Deliverables byte-identical. | 2026-09-11 |
| 7 | **CONM2 gets its own CG grids and the mass model is checked by GPWG** (D-56.6 + D-56.7). One `GRID` per card at the item's own CG in the new `mass-cg` band (`13001+`), zero offset; `_attach_gid`, the offset arithmetic, the placeholder massless beam and its `SPC1` all go, and the wing-item limitation retires with the header sentence that stated it. `inertia_only_cards`, `case_station_weights` and `roundtrip.flatten_mass_case` retire. Gate 6 lands as GPWG. The mass model enters the digest baseline for the first time (234 → 244 channels). | 2026-09-12 |
| 6b-i | **The applied load set is re-aggregated onto the LRA grids** (D-56.9). `applied_loads` returns one row per (case, grid), every aero station and concentrated mass summed onto the nearest node of its member through LM-1; the station-level set stays public as `station_applied_loads`, the aggregation's input and D-56.10's reference curve. `project` becomes required. Gates 12 and 13 land. Four digest channels re-stamp -- the `*_applied` ones, gate 8's stated exception -- and 52 hold. | 2026-09-12 |
| 6b-ii | **What the lumping costs is published** (D-56.10). New owner `report/lumping.py`: the internal load at a cut is the outboard resultant transferred to the cut, one rule for V/M/T on all four members, evaluated twice about the same cuts. New **Appendix G** -- one table of the widest gap per channel over every case, four deviation figures. Two amendments to D-56.10, both recorded in the row above it: no shared case exists, and the deviation is plotted rather than the two curves. | 2026-09-12 |
| 8 | **The assembled deck stops shipping and the round-trip wrapper collapses** (D-56.8 + §8). Four surfaces retire (the Balanced Cases download, the Export page row, the bundle `.bdf`, the CLI target); `EXPORT_TARGETS` 4 -> 3; the report's manifest loses its row. `roundtrip.py` 529 -> 186: `wrap_as_stick_model` and its whole supporting cast go, and every solve in the file now runs the deck as it ships. #173 and #176 close as superseded. | 2026-09-12 |

**Two departures from the note as written, both deliberate.**

1. **The order of steps 2 and 3 is inverted for the applied-load group.**
   Gate 1 ("the move must precede the delete") was reasoned on the *report
   tables*, which sit physically among the deck writers and which the oracle
   report reaches — slice 2 satisfied it. For the applied-load family an AST
   closure showed the coupling to the deck writers is **fourteen names, all of
   them GID allocators, bands or results-coercion helpers**, which is D-56.9's
   own statement in structural form. The delete keeps all fourteen, so moving
   first would have meant a transitional `report → export.sbeam_bridge` import
   and a second move of the same names one slice later.

2. **`EXPORT_TARGETS` is `("balanced", "gear", "lra", "mass")`, not
   `("lra", "mass")`.** `gear` survives because **D-56.1 — this note — reclassified
   the gear interface report as a document** and moved it to `report.tables`; it
   ships in the bundle and this is the only headless route to it. `balanced`
   survives because demoting the balanced deck to an internal producer turns on
   §8's first open item, which is still open. The "ten to two" line was a count,
   not a decision, and dropping a live deliverable to satisfy it would have been
   the wrong reading of the note against itself.

**One defect introduced and not closed.** The case index still publishes a
`LOAD/SUBCASE (component)` column and no artifact quotes those numbers any more.
`tests/test_case_ids.py` asserts the absence explicitly, so the gap fails loudly
if a component pairing reappears — but an index naming a deck that does not
exist is misleading content in a shipped deliverable. It narrows **#209** and
should be the next thing closed after the applied-load move.

**Slice 4's two departures, and a claim of this note's that did not survive
measurement.**

1. **The band registry does not collapse to ~8 here.** D-56.3's row promises it
   and slice 4 leaves **eleven** LRA GID bands where there were six. The
   families the model used to borrow are now its own and each keeps a
   registered owner, because `owner_of` has to keep answering "who put this id
   in my deck?". The count falls at **D-56.9**, when the applied-load model
   stops carrying its own station numbering — `wing-stick`, the two body runs
   and the four tail runs are all still allocated from, and they number nothing
   that ships. `wing-stick`'s `GID 1` hole stays open for the same reason:
   D-56.2's note said D-56.3 would close it, and closing it now would renumber
   every station twice.

2. **The sub-bands are sized for D-56.4, not for today.** 999 wide against a
   present maximum of 84 grids on the largest fixture. D-56.4 makes the mesh
   `n` equally spaced grids per member with `n` settable per component, so a
   band sized to the current node count would be the next thing to move, and
   ruling 1's "the renumber happens once" is the whole reason a wholesale move
   was cheaper than a partial one.

**§1.2's `GID 7` illustration does not reproduce.** This note says three times
— §1.2, the issue body and the backlog row — that `GID 7` named one point in
`wing_loads.bdf` and a different point in `lra_model.bdf`. Measured at slice 4:
it did not. The LRA took the wing stick band's ids for the stations it shares,
so the shared ids named the *same* point, and the gear ids it took from
`balanced-gear` were the same trunnion in both decks. The **borrowing** was
real and is what D-56.3 fixes — the deliverable's grids were defined by four
artifacts, three of them not deliverables — and gate 4 is what catches it. The
position collision was not, and the only one on record (the balanced deck into
the spanwise h-tail band, review F-C1) the registry closed two months ago.
Gate 3 is kept and its docstring says so: it pins a property that was true by
accident, which is what the next deck family would re-open. The decision is
unchanged; the sentence that motivated it was wrong.

**One gate lost, recorded here rather than in a test that no longer exists.**
`test_the_sob_internal_load_is_the_first_outboard_elements_end_force` solved the
wing stick deck and compared the recovered CBAR end force against
`sob_internal_loads`. The closed form is still gated against the cumulative
table (`test_sbeam_bridge`), but the **solver** cross-check has no host: it needs
a deck with a CBAR outboard of the tagged SOB node whose cards are that wing
case's, and the LRA deck's cases are balanced cases carrying inertia — a
different claim, not a rename. It belongs to D-56.4's mesh, where the LRA deck
becomes the authority for G-OR-90 as well.

---

**Slice 5's three decisions inside D-56.4, which the note left open.**

1. **Segment-based spacing, not uniform-then-merge.** "`n` equally spaced grids
   plus every owned point" does not on its own give the note's own sentence that
   joints are mesh points *by construction* -- a uniformly placed grid can still
   land 0.08 in from a joint, which is note 55's failure wearing new clothes.
   The owned points divide the member into segments and the grids are laid
   strictly inside them, so no grid can be near a joint. `n` becomes a target
   rather than an exact node count, which is what it costs.

2. **`JOINT_MERGE_FRACTION` retires but a floor does not.** The note says the
   sliver class dies structurally. It does, for the class it names: insertion.
   It does not for two **owned** locations genuinely close together on one
   member, where both must be nodes. `_MIN_ELEMENT_FRACTION` catches that, at
   1:200 of the member's target element length, and its refusal is a data
   message rather than a bug report. Measured, not chosen: the one observed
   singular solve was 1:1638 and the tightest legitimate element across four
   fixtures at three mesh settings is 1:38.

3. **Members run to their tips**, which is an extent change and not only a mesh
   change. The wing chain stopped 5.0 in inboard of the tip on `ga6_normal` and
   12.1 in on `atr42_100`: the same omission D-54.5 fixed for the fin, which
   only got fixed there because a T-tail tie made the tip a joint. Owner ruled
   2026-09-11.

**Gear and engine nodes are model nodes, not chain stations.** D-56.4 lists
them in the member node set; they are read here as nodes of the *model*, tied by
`RBE2` as they already were, with only the hinge and actuator fittings owned by
their chains (as they already were). Making a tie parent exact rather than
nearest changes a load path and is left separable.

---

**Slice 6a: the split had already happened, so the move was a move.**

The note describes D-56.1 as a three-way split. By the time it ran, two of the
three ways were done -- slice 1 took the contract statements to
``deck_format``, slice 2 took the report tables to ``report/tables.py``, and
slice 3 deleted the decks -- so what was left in the file was exactly one group:
the applied-load model, its station numbering and the side-of-body loads. The
file's own docstring had said so since slice 3. It therefore moved whole, under
its right name, rather than being split at a boundary that no longer existed.

**Three decisions inside it.**

1. **No shim, and a guard that says so.**
   ``test_no_module_named_sbeam_bridge_survives_the_move`` refuses an importable
   ``sbeam_bridge`` at either address. An alias would have been one name at two
   addresses, which is the condition this note exists to remove, and it is what
   let the deck writers keep a public surface for two milestones after the decks
   stopped being deliverables. The companion guard,
   ``test_the_applied_load_set_has_one_address_and_the_export_package_is_not_it``,
   is the slice-2 guard inverted: every name resolves from
   ``report.applied`` and **none** is reachable from ``sloads.export``.

2. **Two sweeps followed the code, not the directory.** The registry's
   base-constant sweep walked ``sloads.export`` only, so the day the numbering
   moved it would have gone quiet on **seven of the registry's own bands** --
   ``wing-stick``, the two body runs and the four tail runs -- which is precisely
   the blind spot ``bands.py`` exists to close. It now walks the export package
   plus ``report.applied``. The CH-2 no-silent-defaults sweep moved the same way,
   and is deliberately a *named* file set rather than a second package walk: the
   rest of ``report/`` renders whatever a project happens to carry and reads
   optional slices with defaults by design, so extending the rule to the
   directory would have been a different decision wearing this one's clothes.
   ``CONVENTIONS.md`` §7's row is re-cut to state both halves.

3. **One import points the wrong way, for one slice.** ``export/mass_cards.py``
   reads ``beam_station_gid`` from ``report.applied`` at module level -- an
   ``export -> report`` dependency, which is backwards. It is kept rather than
   hidden behind a function-level import because **D-56.6 deletes it**: with each
   ``CONM2`` on a ``GRID`` at its own item's CG, no mass card states a beam
   station at all. A lazy import would have made a one-slice fact look like a
   permanent arrangement. There is no cycle either way, and it is the only
   import from ``report/`` in the export package.

**Four stale addresses swept with it (rule 4).** The class is a citation that
survived the code it named. ``equilibrium.CardTotals`` justified itself by two
decks D-56.2 had deleted; ``mass_cards`` and ``balanced_deck`` both cited
``sbeam_bridge.stamped``, which slice 1 had moved to ``deck_format``;
``PROGRAM_SPEC.md`` cited ``gear_report_csv`` and ``filter_by_selected_case_ids``
at their pre-slice-2 addresses, and ``CONVENTIONS.md`` cited ``LOAD_ID_COLUMN``
at its. All five now name where the code is.

**Slice order changed 2026-09-12: D-56.6 goes before D-56.9.** The note calls
D-56.6 orderable anywhere and it is, but 6a left `export/mass_cards.py` importing
`beam_station_gid` from `report.applied`, and D-56.9 retires that band. Running
D-56.6 first deletes the consumer, so D-56.9 retires the band once instead of
keeping it alive for one slice and retiring it in the next. The remaining order is
**7 (D-56.6/D-56.7) → 6b-i (the re-aggregation and the grids) → 6b-ii (D-56.10's
figure) → 8 (D-56.8 + §8)**.

**D-56.9 is not in this slice.** ``AppliedLoad.gid`` is still allocated from the
applied-load model's own bands, so the ``wing-stick`` ``GID 1`` hole stays open
and the registry has not collapsed. That is 6b, and it is the last thing between
this note and its band count.

---

**Slice 7: the precondition held, and the band did not go where the note said.**

Gate 6's one open unknown resolved cleanly — `compute_gpwg` walks `CONM2` cards
and grid positions with no stiffness matrix, so a deck of grids and masses with
no elements and no `SPC` returns the hand-computed mass and CG. Four things
around it did not go to plan, and each is recorded rather than smoothed over.

1. **The band is at `13001`, not the `11001` §D-56.6 proposed.** `11001-11999`
   is the `lra-cbar` **EID** run. The `CONM2` EID bands declare `clear_of_gids`
   precisely so a spliced deck's every id names one owner by inspection, and
   that rule runs both ways — a GID band inside EID space breaks it from the
   other side. The registry's own overlap guard caught it on the first run,
   which is the guard working exactly as intended.

2. **Gate 6's inertia clause was struck (ruling 16).** `GpwgResult` carries
   `total_mass` and a CG and nothing else; the pinned sbeam has no GPWG inertia
   producer, so a third of the gate named an output that does not exist.

3. **The tolerance is the artifact's, and it is measured.** The note called this
   an exact identity after a three-mass probe. Across five fixtures × two unit
   systems × every payload case the worst disagreement is **1.3e-7**, and the
   cause is not summation noise: GPWG reads the *printed* deck and
   `deck_format.fmt` writes seven significant figures
   (`46.62142525735088` prints `4.662143E+01`). `rel_tol=1e-6`, stated.

4. **The mass model had no digest channel at all**, so the artifact could be
   rewritten end to end — every grid new, every offset gone, the beam deleted —
   and nothing would have moved. That is the hole `sbeam/balanced_deck` was added
   to close in B8a-2, one artifact over, and it is closed the same way: both
   forms are now rendered, 234 → **244** channels.

**What the retirement cost, counted rather than asserted.** Five roundtrip legs
went: the three-part M-a/M-b/M-c recovery, the `MASSSET`-gap pin, the two
`flatten_mass_case` legs and the C1 mutation. M-b went by design with
`inertia_only_cards`. **M-a and M-c are a real loss** — sbeam's mass-matrix
assembly and the `GRAV` acceleration path are no longer exercised. Three things
make it affordable and all three were checked, not assumed: GPWG honours
`MASSSET` where `SOL 101` does not, so the gate reads the deck **as shipped**
rather than a flattened transform of it; it still runs per case in both unit
systems; and the **C1 defect class did not leave with its mutation leg** — a
25.4× `GRAV` error is caught by card text against an independently written
constant at `rel=1e-12`, in both systems, in `tests/test_mass_cards.py`. A solve
was never the only thing that could see C1; it was only the thing that did.

**One defect prevented, from #173's own lesson.** Ruling 9 leaves the deck
carrying `SOL 101` over unconnected grids, which dies "singular stiffness
matrix" — #173's defect class exactly, arriving at a different file the same
week #173 was queued to close as superseded. The header names the condition, the
reason and the remedy (`RBE2` per grid), and
`test_the_mass_model_carries_no_structure_and_says_a_solve_is_singular` makes
that statement a gate rather than a courtesy.

**A guard that had to learn a new distinction.** Adding the mass channels to the
digest baseline made the mass deck visible to `test_case_ids`' deck-number
parser, which read `SUBCASE 9301 / LABEL = CG1` as a per-component load-case
pairing and fired D-56.2's "a component deck came back" assertion. It is neither:
a `MASSSET` subcase names a **payload** case, and `CG1` is not a case id and has
no index row. The parser now skips the mass channels by name and says why —
found only because the new digest channel put the artifact in front of it, which
is the argument for the channel restated as an event.

---

**Slice 6b-i: what summing the set actually cost, itemised.**

The re-aggregation itself is small -- one function, one routing map, LM-1 from
the existing owner. What it moved is not, and the note owes an account of it.

1. **A cross-case defect, caught by an unrelated guard.** The first version
   keyed the accumulator by ``gid``. ``applied_loads`` returns every case
   concatenated, so `W-01`'s load at a grid was being summed into `W-02`'s --
   one row per grid for the whole file, carrying an arbitrary case's label and
   factor. Nothing in the new gates saw it; the *mixed-basis safety-factor*
   guard did, on ``atr42_100``, because the merged row took one case's SF.
   Keyed by ``(case, gid)`` now. Worth recording as the reason gate 13 is
   asserted per case and not per component.

2. **The structural zeros are gone, and that is physics.** Moving a force across
   an offset makes a couple about the transverse axes -- which is exactly what
   keeps the resultant exact. Measured: ``Mx`` goes from identically zero at the
   stations to **839 lb-in** on ``baron_58``'s h-tail rows and 869 on its fin,
   and the fin picks up a small real ``My`` (1.2-4.8 lb-in) from its axial
   ``Fz`` moved fore-aft. G-OR-92 ("a component non-zero anywhere is not
   describable as absent") failed, correctly, and the appendix notes are re-cut:
   the zeros are properties of the **station-level** set and the notes now say
   which is which. ``LUMPED_SET_NOTE`` is one wording for all four appendices,
   because four paraphrases of one claim is how note 44 OR-139 happened.
   ``ORACLE_REPORT.md``'s B.1 rules are re-cut to match.

3. **A concentrated mass is no longer an appendix row of its own.** It is summed
   into its grid's row, so "Engine+prop+nacelle" is no longer a caption anywhere
   in B.1. That is a genuine loss of reader value and it is stated in the spec
   rather than absorbed: the item's identity and weight are in the weights
   tables, and B.1 promises the load a model is given. #166's actual
   requirement -- that the point-mass inertia relief is not silently missing,
   4,821.5 lb of a 5,004.1 lb root shear on ``baron_58`` -- is unchanged, and
   its gate is re-aimed at exactly that rather than at the caption.

4. **Two tests were comparing points, not values, and only now say so.** The SI
   root-closure gate took moments about ``mine[0]``'s point, which used to be
   the root station and is now the first grid; it is re-pointed at the root
   station's own coordinates and closes exactly, through a full CSV round trip,
   which is a stronger statement of LM-1 than the arithmetic test beside it. And
   the B.1-vs-CSV gate began failing by 4 lb-in on a 14,464 lb-in ``Mx``: both
   sides are one list, but the table renders four significant figures
   (``-1.446e+04``) and the CSV carries the full value. Invisible while ``Mx``
   was zero. The rendering is #161's row; the gate takes a relative tolerance
   with the reason stated.

5. **A refusal that was not a refusal.** ``build_lra_model`` raises
   ``LraRefusal`` for a named missing datum -- but ``require_integrable_planform``
   raises a plain ``ValueError``, and catching only the subclass turned
   ``oracle_report_vtail``'s deliberately inconsistent fixture from a rendered
   appendix into a crash. Every ``ValueError`` out of that builder means one
   thing to this caller: no beam, so the station-level set, with ``gid`` a
   station number as before D-56.9. ``concept_heavy`` is the shipped instance.

6. **The digest baseline is the record that this went as intended.** Exactly
   **four** channels moved -- ``sbeam/{wing,body,htail,vtail}_applied`` -- and
   **52** held byte-identical. That is gate 8 and its one stated exception, read
   off the artifact rather than argued.

~~**D-56.10 is not in this slice.**~~ **Landed as 6b-ii the same day**; the
sentence below is kept as the record of the gap it names. *The VMT comparison
has its reference curve now (``station_applied_loads`` is public and gated) and
nothing draws it yet, so the note's claim that the report states what the
lumping costs is **not yet true** -- the appendix notes point at a comparison
that does not exist. That is 6b-ii and it is the next thing, not a later one.*

**Slice 6b-ii: what the measurement found.**

1. **Two amendments to D-56.10 before code, per rule 1**, both recorded in the
   decision row itself. *(i) There is no shared critical case to draw.* The
   four components' condition registers are disjoint by construction --
   ``W-nn``, ``F-nn``, ``HT-nn``, ``VT-nn`` -- so no case is run by more than
   one of them, and "one case for all four" was a premise about the data that
   the data does not hold. Each figure names its own, and it is the case that
   bends that member hardest; the case where the *lumping* is worst is a
   different question, and the table answers it over every case. A guard pins
   the disjointness so the amendment cannot rot silently.
   *(ii) The figures plot the gap, not the two curves.* Three channels in two
   versions is six colourless lines carrying three dimensions; no y-axis holds
   that honestly and no greyscale reader separates it. Both sets are already
   printed in full -- the station set in B.2/C.2, the delivered set in
   B.1/C.1/D/E -- so the difference was the one thing missing.
2. **The generic computation is cross-checked against the owner it
   generalises.** ``sob_internal_loads`` states the wing's internal load at one
   cut and has been gated against the solver since step 13. The new
   ``_curve`` reproduces it -- shear, bending **and** torsion -- at the wing
   root of every case of four fixtures. That is what made it safe to write one
   function for four members instead of four integrations: an internal load is
   a resultant about a point, and the wing already had a trusted instance of
   that sentence.
3. **The numbers are larger than the note assumed, and the fuselage is the
   outlier.** Worst deviation as a share of the channel's own peak, over every
   case, on the four loaded fixtures: wing shear 19-35 %, wing bending 3-5 %,
   wing torsion 17-77 %; h-tail and fin bending under 1.1 %, their shear
   6-14 % and torsion 9-21 %; **fuselage shear 82-197 %** and fuselage bending
   14-19 %. The fuselage number is real and not an artifact: on
   ``concept_regional_jet`` a ~107,000 lb carry-through reaction lands on a
   node one bay from where it acts, against a peak station shear of 54,588 lb.
   It is stated, not gated (ruling 15) -- but it is also the strongest argument
   yet that the **fuselage's owned points should include the spar carry-through
   stations**, which D-56.4's mesh does not currently guarantee. **Not yet
   filed as an issue** -- it needs one, and the owner runs `gh`; recorded here
   so it cannot be lost. Not fixed here either: this slice's job is to measure,
   and changing the mesh to improve its own measurement in the same change
   would be marking its own paper.
4. **Bending is the channel that survives lumping best, everywhere.** Under 5 %
   on every member of every fixture, against tens of per cent in shear and
   torsion. That is the expected shape -- bending is an integral of the shear,
   so moving a load a short distance perturbs it by the load times that short
   distance, while the shear at a crossed cut moves by the whole load -- and it
   is worth a reader knowing, because bending is what most of the structure is
   sized by.
5. **Three guards outside this feature caught its defects**, which is the
   argument for having them: the platform-stability sweep refused three keyed
   ``min``/``max`` picks (routed through ``picks.extreme``), the rendered-LaTeX
   sweep refused markdown emphasis in the new appendix prose, and the
   package-layout guard refused the new module until ``PROJECT_GUIDE.md`` §4
   listed it.
6. **The fin's withheld case is honoured.** OR-133 withholds the fin's spanwise
   loads on a non-conventional layout, so Appendix G omits the fin comparison
   there rather than publishing sideways a set section 6 declined to publish.
   ``atr42_100`` and ``concept_regional_jet`` are T-tails, so the guard is live
   in both directions on the shipped fixture set.

---

**Slice 8: what unshipping a deck cost, and what it did not.**

1. **Four surfaces, not one.** The assembled deck had a download on the
   Balanced Cases page, a row on the Export page, a `.bdf` in the bundle zip
   and a CLI target — all four added by 0.5.0 row 1 / D-R2 against a review
   finding (F-D2) that the mission's primary deliverable was page-only. All
   four go. The finding they answered has not been undone: the primary
   deliverable is still reachable headless, stamped, bundled and named by the
   controlling document — it is the **beam deck** now, and
   `test_cli::test_the_beam_deck_is_reachable_headless` is F-D1's gate moved to
   follow the artifact rather than retired with the file it was first written
   about.
2. **`balanced_deck` is a real internal producer, not a courtesy survival.**
   D-56.8's own wording — "its cases feed the LRA transfer and the report's
   `balanced_case_rows`" — describes `build_balanced_cases` and
   `balanced_case_rows`, both of which live elsewhere, so on that reading the
   deck writer had no consumer at all and should have been deleted like the
   other five. It has one, and it is load-bearing: the deck text is the
   **un-aggregated load set at each load's true position**, and its resultant is
   what the transferred set is gated against
   (`test_lra_model::test_the_transferred_set_has_the_balanced_decks_resultant`,
   gate 13's anchor). Deleting it would have deleted the reference the
   deliverable is checked against.
3. **The gear leg would not move, and that is Appendix G's finding arriving
   from the other side.** `test_the_gear_node_carries_the_reports_reaction`
   (G-13) was pointed at the beam deck first and failed: the deck's nose-gear
   trunnion carries 3,334.8 lb on `concept_regional_jet` against the gear
   report's 3,597.8, because D-56.9 sums whatever else is nearest onto the same
   grid. That is the aggregation working as specified — Appendix G is where its
   size is published — and asserting the report's number at that grid would be
   asserting the lumping away. The leg stays on the assembled set, where a gear
   reference point is still a node of its own. It reads card text and never
   solved anything, so nothing is lost by its subject not being the shipped
   file.
4. **Three legs moved and are stronger for it.** The reversed-fin mutation, the
   displaced-`GRID` mutation and the subcase-routing check now run on the beam
   deck. The first two used to run through elements the harness made up; they
   now run through the structure that ships, and the fin mutation is applied to
   the case *before* the transfer, so it calibrates the delivery path as well
   as the solve. Their subject moved from `ga6_normal` to `atr42_100`, the
   fixture whose beam deck solves in both unit systems.
5. **Two narrowings, stated rather than absorbed.** (i) The free-free solve
   xfails on the SI decks of `ga6_normal` and `concept_regional_jet` — sbeam's
   dense-path condition heuristic, already pinned — so those two fixtures lose
   an SI free-free solve the wrapped assembled deck did carry. SI is still
   solved on `baron_58` and `atr42_100`, and both of those fixtures solve in
   Imperial, which is what says the decks are sound. (ii) "Every assembled case
   reaches the deck, and each lateral one carries real side load" was asserted
   *inside* that solve; it is a property of the card text, so it is now
   asserted on the card text, where no solver is needed.
6. **Three wrapper unit tests retired with their subject** (it refuses a deck
   with no `GRID`s, it refuses an ungrouped node, it keeps the deck's own
   support). They were good tests of a good harness and they have no subject
   left. What replaced them is not another unit test but a change of subject:
   every solve in the file runs the deck as it ships.
7. **`PROGRAM_SPEC.md`'s export prose was stale from D-56.2 and is re-cut
   here** (rule 4). Its validation bullet still described solving a wing stick
   deck and a fuselage deck through the test-only wrapper, and its CLI bullet
   still listed ten targets with `wing` as the default. Both named artifacts
   deleted a slice earlier. Fixed with the sentences this slice makes wrong
   rather than left for §7's sweep, because leaving demonstrably false prose in
   a spec while editing the paragraph above it is worse than the scope
   discipline that would justify it.

---

## 7c. The closure sweep (tier L, 2026-09-12)

What §7 asked for, and what each obligation turned out to be. Written because
half of these were not the edit the checklist predicted.

1. **`CONVENTIONS.md` §7 — three rows, and two rules retired outright.** The
   skeleton-solvability row still named `JOINT_MERGE_FRACTION`, which retired at
   D-56.4; it is `_MIN_ELEMENT_FRACTION` now, and the row says why the
   *replacement guards a different thing* — note 55's sliver came from inserting
   a joint into a load-fixed mesh, and nothing is inserted any more, so what the
   floor catches is two genuinely close **owned** locations, a statement about
   the airplane rather than an sloads defect. The joint-register row gains the
   consequence that makes that true: since D-56.4 every owned location is a mesh
   point by construction. A new row lands for D-56.3 — **whose grids a shipped
   deck writes** — with gates 3 and 4 as its guard.

   Two §1 rules were **retired rather than re-cut**, because D-56.2 removed
   their subject: "a load that a free-body cut introduces is never applied in
   the assembled model" (no cut model ships, so there is no cut reaction to
   double-apply) and E-2, the per-component moment reference (it argued that no
   single airplane-wide reference could serve *because* the decks were
   per-component; one assembled airframe ships, so it has one reference). Both
   are kept in place, struck and explained, rather than deleted: a convention
   that retires because the code changed shape is exactly the thing a reader
   needs to find when they propose it again.

2. **`PROGRAM_SPEC.md` — the artifact statement and D-R5.** The artifact
   statement said the assembled deck ships; it does not, and the re-cut states
   both what ships and what the assembled deck now is *inside* the package. D-R5
   ("CLI wing decks are stated about the loads reference axis") named a guard,
   `test_the_cli_wing_deck_is_stated_about_the_loads_reference_axis`, that no
   longer exists — it went with the wing deck at D-56.2. The rule survives in a
   stronger form and the bullet now says so: `report/applied.py` calls
   `loads_ref_axis_results` **once** and every consumer is a view of what it
   returns, so the property holds by construction instead of route by route.
   A spec bullet naming a deleted test is the failure mode this closure exists
   to catch.

3. **`PROJECT_GUIDE.md` — the frozen-baseline paragraph, and a decision it
   forced.** The sentence promised "all five sbeam CSVs, all five decks … for
   all six examples — 256 channels": four wrong facts in one clause. The re-cut
   names the channels, drops the count (`digests.json` is its only owner, per
   the documentation-currency rule) and states something the checklist did not
   anticipate: **the baseline digests one non-deliverable.** The assembled deck
   keeps its channel although it no longer ships, because gate 13 checks the
   LRA's re-aggregated set against its resultant, and an anchor that can move
   without anything noticing is not an anchor. That is the same argument that
   added the channel at B8a-2 when the deck did ship. `imperial_baseline.py`
   states it at the channel rather than leaving it to be discovered.

4. **`docs/20_theory/ch11_export_sbeam.md` — swept under rule 4, not listed in
   §7.** The export chapter described four deck families, the test-only wrapper
   and a per-component cut model as current fact. Its two validation tables are
   the *record* of gates written against artifacts that no longer exist, and
   they are kept as that, each with a paragraph saying what it now applies to —
   the identities were never properties of the files, so they survived the files.
   The `roundtrip._supportable` sentence is re-pointed at `lra_model`'s support
   picker, its sole owner since §8's collapse.

5. **`ORACLE_REPORT.md` and `00_theory_sources.md` were already done**, by the
   slices that owed them (6b-ii's Appendix G section and 6b-i's LM-1 lumping
   section). §7's two "added 2026-09-12" bullets were written *as* those slices
   landed and were satisfied on arrival, which is the closure-in-the-PR rule
   working.

6. **No digest re-stamp.** §7 budgeted one bulk wave at the end. There is
   nothing to stamp: slices 4, 5, 6b-i and 7 each re-stamped narrowly and stated
   what moved, and slice 8 moved no byte at all — `SPC_SID` is 1 either way.
   The wave is stated as not-needed rather than silently skipped, because
   "a regeneration is a claim" cuts both ways.

7. **`CLAUDE.md`'s mission paragraph.** It said the primary deliverable is the
   assembled balanced model and that "per-component decks remain analysis
   views". Neither is true. Corrected here rather than left, because the file
   that instructs every session is the worst place for a stale artifact list.

8. **Two numbers this note promised and did not deliver, stated rather than
   quietly dropped.** D-56.3's row says `bands.py` collapses "from 25+ bands to
   ~8" and §5's effect table repeats it. Measured at closure: **42 registered
   bands.** Slice 4's departure note already forecast half of this (the LRA's
   own families each keep a registered owner, eleven where six were borrowed)
   and said the fall would come at D-56.9, when the applied-load model stopped
   carrying its own station numbering. It did not stop. D-56.9 was amended
   during implementation to keep the station-level set **public**, as
   `station_applied_loads`, because it is the aggregation's own input and
   D-56.10's reference curve — so `wing-stick`, `body-mass`, `body-reaction` and
   the four tail runs still number something real, in `report/applied.py`, and
   an orphan band owned by deleted code is precisely what the registry exists to
   prevent. The registry is larger than forecast because the package kept a
   distinction the forecast assumed away. The same arithmetic applies to the
   sbeam digest channels: "83 → ~11" against **37** measured, for the same
   reason plus the mass model entering the baseline at D-56.7, which the
   forecast predated. `export/` itself came in at **5,307 lines** against
   ~5,400 forecast, and `EXPORT_TARGETS` at **three** against two, `gear` being
   a document under D-56.1.

---

## 8. Deferred

* ~~**Whether `roundtrip.py` (595 lines) collapses to the single LRA solve
  gate.**~~ **RESOLVED 2026-09-12, slice 8: it collapses.** 529 lines (the note
  said 595; that was the pre-D-56.7 count, before `flatten_mass_case` went) to
  **186**. The decision follows from D-56.8 rather than being a separate
  judgement: roughly two-thirds of the module was `wrap_as_stick_model`, which
  read a deck's `GRID` cards and **invented** a tree of `CBAR`s, a `MAT1`/`PBAR`
  section, a determinate support and a case control, so that an **elementless**
  deck could be handed to a linear static solve at all. D-56.2 deleted the
  per-component decks and D-56.8 unshipped the assembled one, so no elementless
  deck is left; the LRA model writes its own elements and its own support and is
  solved exactly as it ships. The wrapper's own guard said this before it was
  deleted — it *refused* a deck that already carried `CBAR`s, on the grounds that
  a wrapped copy is not the shipped artifact. Retired with it: `Support`,
  `Topology`, `SPC_SID`, the property/element/constraint/case-control builders
  and the coincident-node collapse. `_orientation` moved to
  `deck_format.orientation_vector`, because `lra_model` was importing a private
  name out of a test harness to build its bars, and `SPC_SID` moved there too —
  the harness held the constant while the two **writers** each spelled `1` into
  an f-string, so the band registry's declared owner was not the code that
  allocates the id.
* **Retiring the generated LRA model entirely** in favour of import-only. Ruling
  5 makes it a minimal reference default explicitly so this stays cheap later.
  Promoting condition: the import path carrying the CI solve gate against a
  fixture beam model.
* **Making import the primary CI path** (running gate 2 against an imported
  model rather than a generated one), which would make the general routing case
  the *tested* case rather than merely a tested case.
* **`modules/balance.py` (2,842 lines)** is untouched here. The mission chain's
  remaining complexity is in the calc, and #191 keeps it.
