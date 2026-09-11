# The export package reduces to one solver artifact (design note 56)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-10** (owner, in chat, under the solo profile —
`DEVELOPMENT_PROCESS.md` §0; rule 1's working-alone branch). The **twelve**
rulings in §2.2 are the owner's, taken in session on 2026-09-10 (7–9 on review,
10–12 during implementation); the decisions D-56.1…D-56.9 follow from them.
Raised as
[#263](https://github.com/Sean074/sloads/issues/263), band B4 Pri 29 — the slot
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
| **D-56.9** *(added by amendment, ruling 10)* | **The applied load set is stated at the LRA grids, and `AppliedLoad.gid` is an LRA grid.** The component appendices and the `*_applied_loads.csv` files quote the node the deck actually carries the load at, so the appendix row and the FORCE/MOMENT card are **one object at one point** — which is what the row-for-card claim always meant and what the per-component decks happened to provide. A concentrated mass gets a grid like anything else, so `gid` stops being `Optional`. **G-OR-90 keeps its form and changes its authority**: it reads the LRA deck instead of `tail_span_force_moment_cards`, still card-first (every card is found, not merely every row is valid), still one case at a time. | *Let `gid` become `None` and gate on position.* Rejected: it drops the identity the tags (BM-5) exist to provide and makes the appendix describe no artifact. *Keep one per-component card writer alive as the gate's reference.* Rejected: a deck kept in the tree only to be compared against is exactly the maintenance D-56.2 removes — and it would gate the appendix against an artifact nobody receives, which is how the omission in note 44 OR-139 survived review in the first place. |

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
6. **CONM2 re-grid is mass-neutral**: GPWG total mass, CG and inertia unchanged
   by the move to CG grids — the masses did not move, only the nodes they sit on.
   *Precondition to verify first: sbeam's GPWG accepts unconnected grids.*
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

---

## 8. Deferred

* **Whether `roundtrip.py` (595 lines) collapses to the single LRA solve gate.**
  Decide during implementation once the gate set is known; it is test
  scaffolding, so it carries no deliverable risk either way.
* **Retiring the generated LRA model entirely** in favour of import-only. Ruling
  5 makes it a minimal reference default explicitly so this stays cheap later.
  Promoting condition: the import path carrying the CI solve gate against a
  fixture beam model.
* **Making import the primary CI path** (running gate 2 against an imported
  model rather than a generated one), which would make the general routing case
  the *tested* case rather than merely a tested case.
* **`modules/balance.py` (2,842 lines)** is untouched here. The mission chain's
  remaining complexity is in the calc, and #191 keeps it.
