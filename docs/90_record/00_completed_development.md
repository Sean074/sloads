# Completed Development

The authoritative record of what has shipped: completed modules/phases, key
decisions, and resolved defects. Items move here from
[`../30_future/00_backlog.md`](../30_future/00_backlog.md) the moment they close,
with a matching `CHANGELOG.md` entry.

Each entry uses the step format: **Objective**, **Deliverables**, **Test /
Acceptance**, **Key decisions**.

**Live cycle only.** This file holds the current release cycle plus the previous
release cut. Older blocks roll into frozen, do-not-edit archives at each release
(`RELEASE_PROCESS.md` §4): the 0.8.2 cycle and the 0.8.1 cut are in
[`59_completed_development_to_0.8.2.md`](59_completed_development_to_0.8.2.md),
the 0.8.1 cycle and the 0.8.0 cut in
[`51_completed_development_to_0.8.1.md`](51_completed_development_to_0.8.1.md),
the 0.7.1 and 0.7.2 release cuts in
[`41_completed_development_to_0.8.0.md`](41_completed_development_to_0.8.0.md),
the 0.7.0 cycle and the 0.7.0 cut in
[`37_completed_development_to_0.7.1.md`](37_completed_development_to_0.7.1.md),
the 0.6.0 cycle and the 0.5.0 cut in
[`35_completed_development_to_0.6.0.md`](35_completed_development_to_0.6.0.md),
everything before 0.5.0 in
[`11_completed_development_to_0.5.0.md`](11_completed_development_to_0.5.0.md).
Tier S closures do not write here (a `changes/` fragment is their record); tier M
writes one paragraph, tier L the full step format — **as a `changes/<slug>.history.md`
fragment** (design note 28 MD-4), rolled to the top of this file at release cut, so
concurrent PRs never edit the same line here. Only the release-cut block itself is
written directly, by the release manager.

---

## Release cut: **sloads 0.8.3** (the empennage geometry model, and the export package closing on one solver artifact), tag `v0.8.3`, 2026-09-13

**Objective.** Close band **B4**. The milestone opened on its named deliverable
— the **T-tail empennage geometry model** (#25) — and closed on the one that
grew out of it: `sloads/export/` shipped **four parallel model concepts** in one
ID space, three of which were not the deliverable, and the deliverable borrowed
GIDs from artifacts nobody consumed. Design note **56** reduced the package to
**one solver artifact plus the mass model**. The two are the same problem seen
twice — where a joint node *sits* (note 54) and how the model that carries it is
*built* (note 56) — which is why they landed in one milestone.

**Deliverables** (the `[0.8.3]` changelog section is the release note):
- **The empennage geometry model (#25, design note 54, tier L, schema v65).**
  The tail group's geometry is **entered once as boundary lines** and the
  scalars derive: the seam between fixed surface and control surface is marked
  in the input blocks (step 1), and the planform scalars each surface used to
  carry independently become reads of the entered polylines (step 2). Around it
  the cluster: the joint register — a joint is an **owned location, a stated arm
  and a DOF set** (#262, D-54.5/D-54.7, `sloads/joints.py`, importing three
  owners so it can live inside none of them); the conventional h-tail off the
  wing-root waterline (#261, D-54.4); a raked fin root that no longer kinks the
  loads reference axis (#219, D-54.3); one owner for the plane a surface is
  defined in (#220, D-54.2); one name per surface, `fin_*` retired for `vtail_*`
  (#223). **D-54.6 alone remains**, riding the baseline wave in 0.8.5, so note
  54 stays live.
- **The export package closes on one solver artifact (#263, design note 56,
  tier L, ten slices).** The five **per-component decks are deleted** (D-56.2);
  the assembled balanced deck is **unshipped**, demoted to an internal producer
  the LRA transfer and the report's tables consume (D-56.8); `sbeam_bridge.py`
  **ceases to exist** — the applied-load model and the report's deliverable
  tables were never a bridge to sbeam and move to `report/applied.py` and
  `report/tables.py` under their right names (D-56.1), with no shim and two
  guards refusing one. What ships is the **LRA beam model** and the CONM2 mass
  model: the LRA owns every grid it writes (D-56.3), takes a **joint-driven mesh
  decided from geometry** rather than one welded to the load stations (D-56.4),
  and carries the applied set summed onto its own grids with the exact
  lever-arm couple (D-56.9); every `CONM2` sits on its own `GRID` at its own
  item's CG (D-56.6). `EXPORT_TARGETS` 10 → **3**, `sloads/export/` 8,603 lines
  across 15 modules → **5,316 across 14**.
- **What the beam grids cost the distribution is published, not discovered
  (D-56.10).** New **Appendix G** and the new owner `report/lumping.py`: the
  widest gap in each internal-load channel of each member over every case, plus
  four figures along the span. The **resultant** is preserved exactly and gated
  by LM-1; the **distribution** it moves is a real discretization difference, so
  it is stated. No solver is in the loop and there is no acceptance tolerance —
  the size of the difference is a function of the grid counts the project sets.
- **Every exported LRA deck solves (#172, design note 55, tier L).** Three
  defects in *how a joint node joins the structure*: a body tie parenting on a
  node already an `RBE2` dependent (a rigid chain sbeam refuses outright), a
  joint inserted beside an existing station leaving a **sliver element**
  (`cessna_210` at 1.07 % of `ds`, 1638:1), and a support picker that excluded
  rigid dependents but not independents — **569.49 lb** of recovered reaction
  against an applied set closing to 0.0002 lb. All three are gated invariants,
  a skeleton that violates one is an `LraRefusal` naming it, and the solve gate
  widens from the two fixtures that passed to **every CLI-exportable fixture**.
  This is the milestone's mission claim made true rather than asserted.
- **The load-output contract consolidated (#193, note 58, tier M; #170; #175).**
  Governing-case comparisons key on **|value| × SF** so a 2,000 lb case at 1.5
  is not out-ranked by a 2,500 lb case at 1.0, and a mixed-factor envelope
  refuses by name; no delivered load value moves on any fixture. The contract's
  statements get **one owner** and eight copies collapse onto it; a machine
  rating in load units stops being a load (#170).
- **The plan re-cuts into three milestones (tier S, 2026-09-11).** 0.8.3 closes
  the export contract, **0.8.4** converges the two front-ends on one (note 57,
  AGREED), **0.8.5** takes the defect-and-polish tail on the converged surface —
  because note 57 sat AGREED, filed and sequenced, gated on a 21-row tail with
  no relation to this milestone's charter. Bands B5 and B6 carry them.
- **Hygiene as its own items:** the deck-writing primitives get their own module
  (#15, CH-4); six dead public names leave `sloads/` with a gate keeping the
  seventh from arriving (#16, CH-5); the round-trip stick-model wrapper retires
  with the last elementless deck, 529 → **186** lines; `cessna_210` and
  `dhc8_dash8` retire from the bundled examples (#264) while `baron_58` joins
  the Imperial output baseline and the example list becomes structural (#271);
  the theory documentation becomes a chaptered manual; the certification-basis
  matrix leaves the ranked backlog under rule 6 (#47, closed not-planned); the
  backlog is re-scoped onto the package note 56 left behind, and its open-defects
  index loses two wrong issue numbers, a deleted body and three closed entries.
- **The band re-opened once, and drained before the cut (#274).** The
  issue-bookkeeping pass that followed #263 found **seven** rendered statements
  — the oracle report's §7 and gear sections, four GUI captions and a help
  string — plus the `$` header inside the one deck that ships, all describing
  the export package the note had just deleted. A defect with first-order effect
  on shipped content outranks every [V] item, and 0.8.3 could not knowingly cut
  a report naming artifacts it does not build. Filed, fixed and closed the same
  day; the deliberate carve-out is the case index's `LOAD/SUBCASE (component)` /
  `(assembled)` headers, which move a shipped CSV header across three owners and
  are **#209**'s decision, stated at `LOAD_ID_COLUMN` rather than left to be
  inferred.
- **Found at the cut and fixed pre-cut (the §3.5 walk):** three more shipped
  statements of #274's class that its sweep had not reached — the Wing Loads
  caption offering "all three files" and describing the span-load file beside
  them, the Fuselage Loads caption offering "both files" and naming the body
  span CSV, and the SI methods stamp's "the sbeam solver decks **and their span
  CSVs**" — all naming companion files D-56.2 deleted. With them the last
  `*_ULT.csv` filename in the tree, `wing_applied_loads_ULT.csv`, which note 49
  **OR-81** had held for exactly this milestone: the file is LIMIT like every
  other, and a name asserting otherwise is the one statement a reader cannot
  check against the content.
- **Version** `0.8.2` → **`0.8.3`**. Schema **v61 → v66** across the cycle
  (the boundary-line model's v65 among them); `io.py` still loads older saves.
- **Changelog cut** — `scripts/build_changelog.py 0.8.3 --date 2026-09-13`:
  **34 fragments** consumed into `## [0.8.3]`, **20 history entries** rolled to
  the top of this file, a fresh empty `[Unreleased]` opened.
- **History roll** (`RELEASE_PROCESS.md` §4.3): notes **55** and **56** move to
  `40_history/` keeping their numbers; note **54** stays live on D-54.6 alone
  and note **58** on D-58.1 (decided, not done) — the mechanical rule rolls a
  note whole when its status reads shipped, never by halves; notes 21/49/51/52/57
  stay with their open milestones. The live file passed the **1,500-line
  threshold**, so everything below the 0.8.2 cut block froze verbatim into
  [`59_completed_development_to_0.8.2.md`](59_completed_development_to_0.8.2.md).
- **Gates at cut:** `pytest` **3,422 passed / 17 skipped / 2 xfailed / 0 failed**, `ruff` clean, `mypy` clean
  (`sloads/`, 98 source files), `scripts/smoke_test.sh` **PASS** (both front-ends boot, CLI CSV checked),
  `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on 7 tracked keys,
  the §3.5 by-hand walk done by the owner, no open CRITICAL/MAJOR review
  findings. The four statements above came out of a read of the pages that
  precedes that walk, not out of it.

**Key decisions.** *A deliverable is what a consumer holds, and everything else
is scaffolding that has to justify itself.* The package had grown four model
concepts because each was easier to add than to reconcile, and the cost was not
maintenance time but **truth**: the shipped model borrowed GIDs from decks that
were not deliverables, and the report described a package the bundle did not
carry. Two rulings made the reduction cheap enough to take. Nothing downstream
reproduces an sbeam output, so decks, digests and GIDs were free to move and the
renumber happened once. And sizing belongs to the stress analyst, outside
sloads: core sloads produces an LRA beam model with arbitrary beam properties
plus the load cards on its grids, to prove the cases solve — that is the whole
job, and it is what let ~4,000 lines go without withdrawing a claim.

*The mesh was the tell.* A beam welded to the load stations is a **degenerate
special case that hides the general one**: when beam nodes *are* load stations
the spanwise half of the transfer is identity, so every CI fixture exercised the
degenerate path while arbitrary-grid routing — what a real user meets first —
was least covered. Cutting the mesh loose made the generated model *one instance
of the contract the imported model obeys*, and note 55's sliver class died
structurally rather than by tolerance.

*Publish the cost of your own discretization.* D-56.9 sums the applied set onto
grids the mesh chose from geometry, so a moment that is zero at a station is
generally not zero at a grid. The resultant is gated; the distribution moves.
Appendix G exists because the honest response to "this changed something we
cannot bound" is to measure and print it, not to pick a tolerance that would
fail a coarse mesh behaving exactly as specified.

**Band B4 retired with the cut; band B5 (0.8.4 — the two front-ends converge on
one, design note 57) is the milestone in flight.**

- **The applied load set gets its right address, and the export bridge ceases to
  exist (note 56 D-56.1, tier M, 2026-09-11).** `sbeam_bridge.py` — 1,404 lines by this
  point, 3,091 when the note was written — moved whole to
  `sloads/report/applied.py`. The note described D-56.1 as a three-way split, and
  by the time it ran two of the three ways were already done: slice 1 took the
  load-output contract statements to `deck_format`, slice 2 took the report
  tables to `report/tables.py`, and slice 3 deleted the five per-component decks.
  What remained was one group — the applied-load model, its station numbering and
  the side-of-body internal loads — and the file's own docstring had said so
  since slice 3. So it moved under its right name rather than being split at a
  boundary that no longer existed. `sloads/export/` is **5,769 lines across 14
  modules**, from 8,603 across 15 when the note opened.
- **No shim, and two guards that keep it that way.**
  `test_no_module_named_sbeam_bridge_survives_the_move` refuses an importable
  `sbeam_bridge` at either package. `test_the_applied_load_set_has_one_address_and_the_export_package_is_not_it`
  is the slice-2 guard inverted: every name resolves from `report.applied` and
  none is reachable from `sloads.export`. An alias would have put one name at two
  addresses, which is the condition note 56 exists to remove — and it is exactly
  what let the per-component deck writers keep a public surface for two
  milestones after the decks stopped being deliverables.
- **Two sweeps followed the code rather than the directory.** The band registry's
  base-constant sweep walked `sloads.export` only, so on the day the numbering
  moved it would have gone quiet on **seven of the registry's own bands** —
  `wing-stick`, the two body runs and the four tail runs. That is precisely the
  blind spot `bands.py` exists to close, and it would have opened silently. It
  now walks the export package plus `report.applied`. The CH-2 no-silent-defaults
  AST sweep moved the same way, and stays a *named* file set rather than a second
  package walk: the rest of `report/` renders whatever a project happens to carry
  and reads optional slices with defaults by design, so extending the rule to the
  whole directory would have been a different decision wearing this one's
  clothes. `CONVENTIONS.md` §7's row is re-cut to state both halves.
- **One import points the wrong way, deliberately and for one slice.**
  `export/mass_cards.py` reads `beam_station_gid` from `report.applied` at module
  level — an `export → report` dependency, which is backwards. It is left visible
  rather than hidden behind a function-level import because **D-56.6 deletes
  it**: with each `CONM2` on a `GRID` at its own item's CG, no mass card states a
  beam station at all. A lazy import would have made a one-slice fact look
  permanent. There is no cycle either way.
- **Five stale citations swept with it (rule 4).** The class is a citation that
  outlived the code it named: `equilibrium.CardTotals` justified itself by two
  decks D-56.2 had deleted; `mass_cards` and `balanced_deck` both cited
  `sbeam_bridge.stamped`, which slice 1 had moved to `deck_format`;
  `PROGRAM_SPEC.md` cited `gear_report_csv` and `filter_by_selected_case_ids` at
  their pre-slice-2 addresses, and `CONVENTIONS.md` cited `LOAD_ID_COLUMN` at
  its. All five now name where the code is.
- **What did not happen here.** D-56.9 is a separate slice: `AppliedLoad.gid` is
  still allocated from the applied-load model's own bands, so the `wing-stick`
  `GID 1` hole stays open and the registry has not collapsed to its final count.

- **The applied load set is re-aggregated onto the LRA grids (note 56 D-56.9,
  tier L, 2026-09-12).** The eighth slice of note 56, and the one the decision
  had to be rewritten for. Implementation reached D-56.9 as written — *"the
  appendices quote the node the deck carries the load at"* — and found it
  unbuildable: the LRA deck emits one `SUBCASE` per **balanced** case and sums
  every source onto each node, so a card at a grid corresponds to no single
  station-level row and the card-first gate had nothing to match. The owner's
  answer (rulings 13–15, 2026-09-12) went further than the options put up: the
  loads are **summed** to the LRA grids, not relabelled with them, and the
  report states the difference that produces. `applied_loads` now returns one
  row per (case, grid) through LM-1 — `gear_loads.transfer_couple`, the same
  owner `lra_model.transferred_case_loads` uses, so there is one routing rule
  and not a second written for the report. `station_applied_loads` keeps the
  un-lumped set under its own name; `project` becomes required.
- **A cross-case defect, caught by a guard that was not looking for it.** The
  first version keyed the accumulator by `gid` alone. `applied_loads` returns
  every case concatenated, so `W-01`'s load at a grid was summed into `W-02`'s,
  collapsing the file to one row per grid under an arbitrary case's label and
  factor. None of the new gates saw it — the *mixed-basis safety-factor* guard
  did, on `atr42_100`, because the merged row took one case's SF into a file
  that should have carried two. Keyed by `(case, gid)`, and gate 13 is asserted
  per case for the same reason.
- **The structural zeros are gone, and that is the physics working.** Moving a
  force across an offset makes a couple about the transverse axes — which is
  precisely what keeps the resultant exact. `Mx` goes from identically zero at
  the stations to **839 lb-in** on `baron_58`'s h-tail rows and 869 on its fin,
  and the fin gains a small real `My` (1.2–4.8 lb-in) from its axial `Fz` moved
  fore-aft. G-OR-92 failed, correctly. The appendix notes are re-cut through one
  shared wording, `LUMPED_SET_NOTE`, because four paraphrases of one claim is
  how note 44 OR-139 happened; `ORACLE_REPORT.md`'s B.1 rules are re-cut to
  match, distinguishing what is zero at a station from what is zero in the
  delivered set.
- **A concentrated mass stops being an appendix row of its own.** It is summed
  into its grid's row, so "Engine+prop+nacelle" is no longer a caption anywhere
  in B.1. A real loss of reader value, stated in the spec rather than absorbed:
  the item's identity and weight live in the weights tables, and B.1 promises
  the load a model is given. #166's actual requirement — that the point-mass
  inertia relief is not silently missing, 4,821.5 lb of a 5,004.1 lb root shear
  on `baron_58` — is unchanged, and its gate is re-aimed at that rather than at
  the caption it used to be checked through.
- **Two gates were comparing points and only now had to say so.** The SI
  root-closure gate took moments about the first row's point, which used to be
  the root station and is now the first grid; re-pointed at the root station's
  own coordinates it closes exactly through a full CSV round trip, which states
  LM-1 more strongly than the arithmetic test beside it. The B.1-vs-CSV gate
  began failing by 4 lb-in on a 14,464 lb-in `Mx` — both sides are one list, but
  the table renders four significant figures (`-1.446e+04`) and the CSV carries
  the full value. Invisible while `Mx` was zero everywhere. The rendering is
  #161's row; the gate takes a relative tolerance with the reason recorded.
- **A refusal that was not the refusal.** `build_lra_model` raises `LraRefusal`
  for a named missing datum, but `require_integrable_planform` raises a plain
  `ValueError` — so catching only the subclass turned `oracle_report_vtail`'s
  deliberately inconsistent fixture from a rendered appendix into a crash. Every
  `ValueError` from that builder means one thing here: no beam, so the
  station-level set, with `gid` a station number as it was before D-56.9.
- **The digest baseline is the evidence this went as intended.** Exactly four
  channels moved — `sbeam/{wing,body,htail,vtail}_applied` — and 52 held
  byte-identical. That is gate 8 with its one stated exception, read off the
  artifacts rather than argued.
- **What is not done.** D-56.10's VMT comparison has its reference curve
  (`station_applied_loads`, public and gated) and nothing draws it, so the
  appendix notes point at a comparison that does not exist yet. That is the next
  slice, not a later one.

- **The package delivers one solver artifact (note 56 D-56.8 + §8, tier L,
  2026-09-12).** The tenth slice of note 56 and the last of its implementation.
  The assembled full-span free-free deck stops being a shipped artifact: four
  surfaces retire in one change — the Balanced Cases page's stamped download,
  the Export & Report page's row, the `.bdf` inside the bundle `.zip`, and
  `cli.py --export-target balanced` — and the report's Appendix A manifest
  loses its row with them, because a controlling document naming a file the
  reader was never given is review F-D2's defect pointing the other way.
  `EXPORT_TARGETS` goes 4 → **3**, not the note's 2: D-56.1 reclassified the
  gear interface report as a *document* and this is still its only headless
  route.
- **Review F-D2's finding is honoured, not undone.** All four retired surfaces
  were added by 0.5.0 row 1 / D-R2 against a finding that the mission's primary
  deliverable was page-only, unstamped and unnamed by the controlling document.
  It is still reachable headless, stamped, bundled and named — it is the **LRA
  beam model** now, which carries the same assembled cases transferred onto the
  beam's own grids. Nothing left the deliverable; one of two files carrying the
  same load sets did. F-D1's reachability gate moved to follow the artifact
  rather than retiring with the file it was first written about.
- **`balanced_deck` survives, and not as a courtesy.** D-56.8's own wording —
  "its cases feed the LRA transfer and the report's `balanced_case_rows`" —
  names `build_balanced_cases` and `balanced_case_rows`, both of which live
  elsewhere; read literally, the deck writer had no consumer and should have
  been deleted like the other five. It has one and it is load-bearing: the deck
  text is the **un-aggregated load set at each load's true position**, and its
  resultant is what the transferred set is gated against (gate 13's anchor,
  `test_the_transferred_set_has_the_balanced_decks_resultant`). Deleting it
  would have deleted the reference the deliverable is checked against.
- **§8 resolved: the round-trip wrapper collapses.** `sloads/export/roundtrip.py`
  529 → **186** lines. Roughly two-thirds of it was `wrap_as_stick_model`, which
  read a deck's `GRID` cards and *invented* a tree of `CBAR`s, a `MAT1`/`PBAR`
  section, a determinate support and a case control, so that an **elementless**
  deck — a load set on a node cloud — could be handed to a linear static solve
  at all. D-56.2 deleted the per-component decks and D-56.8 unshipped the
  assembled one, so none is left; the LRA model writes its own elements and its
  own support and goes to the solver exactly as it ships. The wrapper's own
  guard had said this before it was deleted: it *refused* a deck that already
  carried `CBAR`s, because a wrapped copy is not the shipped artifact. Retired
  with it: `Support`, `Topology`, the property / element / constraint /
  case-control builders, the coincident-node collapse, the `roundtrip-rbe2` EID
  band and three wrapper unit tests.
- **Two names moved to the code that allocates them.** `_orientation` →
  `deck_format.orientation_vector`, because `lra_model` — the one deck writer
  left — was importing a private name out of a test harness to build its bars.
  `SPC_SID` → `deck_format.SPC_SID`, read by both writers: the harness held the
  constant while the two writers each spelled `1` into an f-string, so the band
  registry's declared owner was not the code that allocates the id.
- **Three solver legs moved onto the shipped deck and are stronger there** — the
  reversed-fin mutation, the displaced-`GRID` mutation and the subcase-routing
  check. The first two used to run through elements the harness made up; they
  now run through the structure that ships, and the fin mutation is applied to
  the case *before* the transfer, so it calibrates the delivery path as well as
  the solve. Their subject moved from `ga6_normal` to `atr42_100`, the fixture
  whose beam deck solves in both unit systems.
  `test_assembled_deck_reacts_to_zero` retires into
  `test_the_lra_model_solves_and_reacts_only_the_residual`, which makes the same
  free-free claim about the deck a reader is handed, over four fixtures rather
  than two.
- **The gear leg would not move, and that is Appendix G's finding arriving from
  the other side.** G-13's assertion was pointed at the beam deck first and
  failed: the deck's nose-gear trunnion carries 3,334.8 lb on
  `concept_regional_jet` against the gear report's 3,597.8, because D-56.9 sums
  whatever is nearest onto the same grid. That is the aggregation working as
  specified — Appendix G is where its size is published — and asserting the
  report's number at that grid would be asserting the lumping away. The leg
  stays on the assembled set, where a gear reference point is still a node of
  its own; it reads card text and never solved anything, so nothing is lost by
  its subject not being the shipped file.
- **Two narrowings, stated rather than absorbed.** The free-free solve xfails on
  the SI decks of `ga6_normal` and `concept_regional_jet` — sbeam's dense-path
  condition heuristic, already pinned — so those two fixtures lose an SI
  free-free solve the wrapped deck did carry; SI still runs on `baron_58` and
  `atr42_100`, and both of the xfailing fixtures solve in Imperial, which is
  what says their decks are sound. And "every assembled case reaches the deck,
  and each lateral one carries real side load", asserted *inside* the retired
  solve, becomes an assertion on the deck's card text, which is where it is
  observable.
- **`PROGRAM_SPEC.md`'s export prose was stale from D-56.2 and is re-cut here**
  (rule 4). Its validation bullet still described solving a wing stick deck and
  a fuselage deck through the test-only wrapper, and its CLI bullet still listed
  ten targets with `wing` as the default — artifacts deleted a slice earlier.
  Leaving demonstrably false prose in a spec while editing the paragraph above
  it is worse than the scope discipline that would defer it to §7's sweep.
  `PROJECT_GUIDE.md` §4's two tree lines and `CONVENTIONS.md` §7's skeleton row
  follow the code. **#173 and #176 close as superseded, not fixed:** both are
  defects in an artifact that no longer ships.

- **#25 step 1 — the boundary-derived seam marked (note 54 D-54.1, tier M,
  2026-09-10)** — the first half of the 0.8.3 headline: before the boundary-line
  model can derive the empennage scalars, the seam it replaces must be a
  stated, guarded set rather than a prose count. The derivable membership of
  the two tail input blocks is machine-readable — `HTAIL_BOUNDARY_DERIVED` /
  `VTAIL_BOUNDARY_DERIVED` map each field to the surface whose boundary lines
  derive it (`htail`/`vtail`/`elevator`/`rudder`, plus `wing` for `ARW` and
  `B`, extending the note 36 derive-by-default contract those two already
  honour) — with a `[D]` mark per field that travels into the generated data
  dictionary, and a partition guard pinning both maps against the dataclasses
  so a field added to either block must declare its side. Field order is
  deliberately untouched: it is a persisted shape under
  `test_schema_guards.fields_hash`, so the physical regrouping lands with
  step 2's schema bump (the boundary model proper, tier L, D-54.1) instead of
  spending a version hop on cosmetics. No load, deck byte, or delivered value
  moves; `DATA_DICTIONARY.md` regenerated.

## Step — The boundary lines are entered once, and the scalars derive (#25 step 2, design note 54 D-54.1/D-54.8, tier L, 2026-09-10)

**Objective.** Close the 0.8.3 headline's schema half: boundaries that are
physically one line were entered several times with nothing checking the copies
agree — `ga6_normal`'s elevator TE was byte-identical to its h-tail TE, its
rudder TE was the fin TE plus a closure point, and the nine h-tail and ten
v-tail planform scalars were hand-typed readings of surfaces the project
already carried as polylines. After this step one tail group is **five entered
lines** — tail LE, tail TE, control LE, control hinge line, and the control TE
*derived* from the parent's — and every `[D]`-marked scalar of the step-1 seam
derives from them wherever it is blank.

**Agreed first.** Design note 54 (AGREED 2026-09-09, owner), D-54.1 for the
boundary-line model and D-54.8 for the declared dihedral field; #25 step 1
(the marked seam, tier M, 2026-09-10) landed the machine-readable membership
this step consumes.

**Deliverables.** Schema v65 (`SurfaceInput.hinge_line`, control
`trailing_edge` allowed empty, `LayoutInput.htail_dihedral_deg`, the two tail
blocks physically regrouped into the seam order; identity hop, examples
re-stamped). The resolution owners in `sloads/tail_geometry.py`:
`CONTROL_PARENT`/`TAIL_CONTROL`, `derived_control_trailing_edge` (parent TE
over the control's span, end-closure to the control's own LE endpoint where it
departs), `validate_control_trailing_edge` (the copies-agree guard, hard on
the tail groups), `resolved_control_surface`/`resolved_surfaces` (the read
every control-polyline consumer goes through: the WINGGEOM integrator,
AIRLOADS' Schrenk pass, the report's planform figures),
`control_hinge_areas` (the hinge split, integrated by the one planform owner
so the halves and the whole cannot drift), and `boundary_derived_scalars`
(the `{field: value}` set `effective_tail_inputs`/`effective_vtail_inputs`
and `resolve_tail_planform` take for blank fields only). `ga6_normal` sheds
its elevator and rudder trailing edges — the derivation reproduces Appendix
A's printed coordinate tables (p153, p149) byte-for-byte, pinned in the test
that replaced them.

**Test.** Note 54 gate 7: every derived scalar the GA6 boundary lines supply
lands on its printed Appendix A figure within ±0.1 % (h-tail p151, elevator
p153, rudder p149; the fin against the printed-planform scalars) —
`test_the_boundary_model_predicts_the_printed_appendix_a_figures` — so the
transcriptions became checked predictions. Gate 8: the frozen Imperial
digests are **byte-identical** across the whole step, re-stamp included.
Mechanism gates: derived-TE byte-identity, the +1.00 % aileron end-closure
number from #25's own row (why an entered control TE survives), the
off-parent refusal, the analytic hinge split and its two refusals, the
whole-seam blank-derive walk, the v65 round-trip, and D-54.8's boundary — a
6° declared dihedral moves nothing any module renders.

**Key decisions.** (1) *Blank derives, typed overrides* — the oracle fixtures
keep their Appendix A transcriptions, so the model lands with zero movement in
any delivered load; the derivation is proven against the print, not by
re-baselining onto itself. (2) The copies-agree guard is **hard on the tail
groups only**: three shipped fixtures' estimated aileron polylines sit
0.04–9.4 in off their wing TE, and reconciling that data is the #260/D-54.6
fixture wave's deliberate, baseline-moving work — a guard that fired today
would have forced silent fixture edits inside a no-movement step. (3) The
fixed-surface TE line of D-54.1's five is carried by the parent TE + control
LE pair wherever the two coincide; a separately-entered stabilizer TE
(shroud/overlap geometry) has no consumer and no printed oracle yet
(Appendix A p152 prints the h-stabilizer run the future gate would use), so
it waits for its consumer rather than shipping as an unread field. (4) The
tail blocks' physical regrouping rode this bump exactly as step 1's fragment
promised — field order is a persisted shape, and the reorder spent the
version hop the boundary model was already paying for.

- **The load-output contract's statements get one owner (note 56 D-56.1, tier M,
  2026-09-10)** — The first slice of note 56's export reduction, and a
  precondition for the rest of it: D-56.1 splits `sbeam_bridge.py` three ways,
  and the helpers both halves need had to have a home before either half could
  move, or the split would have manufactured a copy rather than removed one.
  `deck_format.py` was already that home by its own charter — created at #15
  (CH-4) because five sibling writers were reaching across the package to import
  its format helpers *through the underscore* — and its docstring explicitly
  deferred the contract statements to `sbeam_bridge` "where the load-output
  contract lives". That sentence is what changed: `solver_units`,
  `basis_sentence`, `load_label`, `ult_label`, `case_sf` and `SUITE_SF` moved,
  and the same reasoning that justified the module now covers them.
  `safety_factors.py` remains the authority for the factor itself; these render
  what it decides. The measured duplication was worse than the note recorded:
  the solver-channel resolution existed in **eight** places — four private
  `_units` helpers that agreed only because nobody had yet edited one of them,
  and four inline calls in `mass_cards`, `lra_import`, `workbook` and
  `coordinates` — all swept in the same change under rule 4, with a drift guard
  scoped to `sloads/export/` (`report/` names the channel legitimately, where it
  *compares* the human and solver sets rather than picking one). The finding
  that mattered was not the duplication but a guard: **G-OR-71**, the whole-tree
  scan for a surviving limit→ultimate multiply, keys on source text, and
  renaming `_sf` to `case_sf` would have slipped straight past its `\bsf\b`
  alternative — `_` is a word character, so there is no boundary before `sf` —
  leaving the scan passing and toothless against the exact spelling it now had
  to catch. It is fixed with its teeth extended and the reason written into the
  test, and it is a standing caution for the rest of note 56, which renames and
  relocates a great deal more: a text guard does not fail when it is bypassed,
  so every one it passes over must be re-read against the new spelling rather
  than trusted to go red. Deliverables are byte-identical — the Imperial
  digest's 330 channels, the two reports and every CSV — which is note 56's
  gate 8 asserted at the first opportunity rather than at the end.

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

- **The bundled example set reduces to five (#264, tier M, 2026-09-11)** — the
  2026-09-10 scope-reduction review's first ruling landed: `cessna_210` and
  `dhc8_dash8` retire to unmaintained parking outside the repository
  (recoverable at the `v0.8.2` tag), since `ga6_normal`, `baron_58`,
  `atr42_100` and the two concept configurations carry every coverage class
  the mission names (GA single, closure-locked FAR 23 twin, ATR42-class
  turboprop, >12.5k concept, T-tail jet). The retire is full — CI matrices,
  parametrized lists, pinned baselines and sbeam digests all shrink to the
  surviving set, and the Imperial baseline regeneration proved every surviving
  digest byte-identical, so no delivered load moved. Where a retired fixture
  was a role's only exerciser the test re-pinned to a surviving fixture or a
  constructed case (below-energy landing caution from `ga6_normal` at N=2.90;
  gear-carrier mistag from `atr42_100` with a wing-carried leg; the
  VD-governed-by-`K_d·VCmin` branch is recorded as unexercised on shipped
  data). Sequenced deliberately ahead of the #164 baseline-regeneration wave
  so that wave regenerates four fixtures, not six. The `cessna_210` engine/prop
  CG waterline defect (2026-09-07, unfixable without the airplane's own data)
  closes parked-with-fixture; #216 narrows to its `baron_58`/RJ halves.

- **The h-tail waterline owner is completed (#261, design note 54 D-54.4,
  tier M, 2026-09-10)** — the #236 owner's conventional leg had one branch
  between "entered" and the wing-root placeholder review R12 filed (32.5 in
  low on the reviewed GA-6, 14 in on `cessna_210`, printed as an airplane
  coordinate in Appendix D and the deck `GRID`s). Per D-54.4, decided
  2026-09-09: entered `h_tail_z` → the h-tail **mass items' weight-weighted
  `z`** (ASSUMED, basis `mass-item` — an entered statement of the surface's
  height that is not a surface definition, and says so) → the wing-root plane,
  loud and last. The T-tail and cruciform branches stand, with the
  **two-spellings rule** added: an entered `h_tail_z` contradicting a declared
  T-tail's fin tip past `PLANFORM_TOLERANCE` of the fin span is named NOT
  USED in-band rather than silently outranked (#260 E5's class). Rule-4
  sweep: the three-view reads the owner (its private copy removed), the
  report's provenance sentences cover both new branches, and `CONVENTIONS.md`
  §7 gains the SSOT row. `cessna_210` moves 86.0 → 100.0 in and
  `concept_heavy` 100.0 → 90.0 in — stations and `GRID`s only, no load —
  pinned as note 54's gate 3; Imperial baseline re-frozen. This is phase 3's
  minimum geometry prerequisite (correct arms for note 51's transfer moments)
  alongside the #260 fixture pass.

## Step — The joints between components get an owner (#262, design note 54 D-54.5/D-54.7, tier L, 2026-09-10)

**Objective.** Close note 54's remaining decision pair. Every inter-component
transfer in the LRA beam model is an `RBE2`, and a rigid tie across a real
offset carries the exact lever-arm couple — so the *mechanism* was always
statically exact. What had no owner was the **node positions**: each end of each
tie was resolved independently, from separately entered data, by whichever
expression was nearest to hand, and nothing compared the two. Note 54 §1 states
the covering rule — *a joint between two components must be a first-class
geometric entity: an owned location, stated offset arms, a DOF set and a basis,
not an emergent coincidence of separately-entered surfaces.*

**Agreed first.** Design note 54 (AGREED 2026-09-09, owner), D-54.5 for the
register and D-54.7 for its drift guard. The note left the register's home open
("`sloads/joints.py`, or a `geometry` submodule — final home decided at
AGREED"); decided at implementation as `sloads/joints.py`, because the register
must import `tail_geometry`, `derived_geometry` **and** `modules/tail_span` and
so can live inside none of them, `modules/` is reserved for
`run(project) -> ModuleResult` producers, and calc may not import `export/` —
`lra_model` importing `joints` is the correct direction.

**What the register found.** Three of the five joint kinds already agreed with
their owners at `rel_tol=1e-9` (fin root, wing SOB, spar posts — the fin-root
waterlines reproduce note 54 gate 1's table exactly: 111.5 / 110.0 / 100.2 /
191.2 / 203.5 / 87.0). Two did not:

| fixture | R-6 tie as exported | the owners' arm | error |
|---|---|---|---|
| `atr42_100` | dx −23.228, dz +6.250 | dx −25.600, dz 0 | 2.37 in x, 6.25 in z |
| `dhc8_dash8` | dx −23.753, dz +6.500 | dx −26.100, dz 0 | 2.35 in x, 6.50 in z |
| `concept_regional_jet` | dx −20.876, dz +6.900 | dx −26.680, dz 0 | **5.80 in x (−22 %)**, 6.90 in z |

`vtail_chain[-1]` was the outermost fin **strip midpoint**, half a strip below
the surface's own top — the whole of the spurious `z` — and the h-tail
centreline node was interpolated off the strip-station polyline at `y = 0`,
which on a swept surface answers with the innermost strip's station rather than
the centreline's. The conventional attachment pair carried the same defect in
miniature: the node interpolated off the chain while the body station it reacts
against came from the planform owner, 0.356 in apart on `ga6_normal` and 0.010
on `baron_58`. These are the arms note 51's D-51.2/D-51.3 transfer moments are
computed across, which is why note 54 §5 ranks this as note 51's enabling gate.

**Deliverables.** `sloads/joints.py`: `JointName`, a frozen `Joint` (name, side,
`location`, `arm`, `to`, `node_family`, `dof`, `basis`, `assumed`, `note`),
`Refusal`, `JointRegister` and `joints(project)`. One uniform `Joint` with a
**pair modelled as two rows** rather than a per-kind type union — the h-tail
attachments, the SOB nodes and the spar posts are each two physical points with
two GIDs already, and flattening them is what lets the drift guard walk the
register with no per-kind branch. `location` is always a full airplane point,
never a station scalar: the two joints that were wrong were wrong in a
coordinate a scalar form would have dropped. `export/lra_model` reads the
register for the SOB pair and hub, the posts, the fin root, the new
`lra-fin-tip` node, the h-tail centreline and the attachment pair, and raises
`LraRefusal` from the register's refusal reasons; `_insert_on_chain` gains an
optional owned `pos`. `wing_geometry.chord_fraction_x` is extracted as the
single owner of the chord-fraction line, replacing the copies in
`TailPlanform.x_at` and `net_loads.to_loads_ref_axis`. `CONVENTIONS.md` §7 gains
the joint-register and chord-fraction rows; `PROGRAM_SPEC.md`'s LRA section and
`PROJECT_GUIDE.md`'s package tree follow. **No schema change — v65 stands**, so
`DATA_DICTIONARY.md` regeneration is a no-op, and note 54 §7 rules that no
`theory_sources.md` row is owed (this places geometry; it adopts no method).

**Test.** `tests/test_joints.py`, four guards in the shapes the suite already
uses. The D-54.7 walk parses the **emitted deck text** — `GRID` cards, their
`$ SLOADS-NODE` tags and the `RBE2`s — rather than the `LraModel` object, since
once `lra_model` reads the register an in-memory comparison would be very nearly
tautological; the 1e-9 copy identity is asserted against the built model and the
deck is then held to the writer's own precision (1e-3 in, an order of magnitude
below the smallest defect this guard chases, `baron_58`'s 0.010 in). It walks
whatever the register produced and has no fixture list of its own, so a joint
added is guarded the day it exists; `test_the_joint_set_partitions_by_layout` is
its guard-on-the-guard, pinning every fixture to a non-empty, layout-correct set
and failing on any `JointName` with no producer. `test_the_walk_would_have_caught_the_tip_joint_arm`
restores the pre-register construction and states what it cost. Gate 4 is
written data-driven against `carry_through(project).assumed` — with the entered
direction on a constructed project, since no shipped fixture enters its spar
stations — so #260 flipping any fixture needs no edit here. The walk was
mutation-tested: reintroducing the old tip placement fails it on exactly the
three T-tails.

**Key decisions.** (1) *Placement rewired now, not in phase 2.* D-54.7's own
wording — "positions are copies of one owner, not measurements" — forecloses
the softer reading: two independent computations compared at 1e-9 is a
measurement, and a register that disagreed with the deck on three of six
fixtures would be a *sixth* independent copy, the thing note 54 §1 exists to
stop. (2) *Gate 8 re-scoped, with the numbers* (owner, 2026-09-10; recorded in
the note). Byte-identical `GRID`s and "the register owns placement" are
incompatible. What holds: every **delivered load** is byte-identical on all six
fixtures — of 330 baseline channels exactly one moved, `sbeam/lra_model`, on
five (`cessna_210` is byte-identical) — and equilibrium is preserved exactly,
the per-subcase deck resultant unchanged to four significant figures with the
largest change 5.2e-8 of the largest applied card, because `transferred_case_loads`
holds the balanced resultant under LM-1 wherever the nodes sit. (3) *Refusals
are carried as grades, not raised.* The register is calc-side and will be read
by consumers that must not refuse (the report's provenance sentences today,
`body_loads`' T-tail entry point in phase 2); whether a missing joint is fatal
is the exporter's policy (BM-3), so `lra_model` keeps raising `LraRefusal` — but
reads its reason from the register, so the two cannot drift. (4) *T7's `x_tip`
was investigated and dismissed, not filed.* `tail_span.py:1159` feeds the same
outermost-strip station into `ttail_transfer`, which looks like the same defect;
it is not. `sbeam_bridge` applies the transfer's force **and** its free moment
at that same node, so `(F at P, M about P)` is a statically exact decomposition
and the resultant about any reference is independent of `x_tip` —
`tail_span.py:1155` says so deliberately. Moving it would only be correct if the
application node moved too, and that node is a strip midpoint from the aero
integration, so it would reopen the strip scheme and its oracle for no change in
any delivered load. Left alone. (5) *The chord-fraction owner was extracted
first.* The expression existed twice and the register would have made it three;
per rule 3 the formula got an owner before the register read it, which is also
what makes the tip arm's `z` member zero **by construction** — `h_tail_waterline`'s
fin-tip branch *is* `root_z + span`, so note 54 gate 2's first clause is proved
rather than asserted. (6) The fin chain gains one `CBAR`, shifting `lra-cbar`
EIDs on the three T-tail decks: numbering, not posture. The scoped reopening
note 54 §6 grants is node *placement* only — the same four tie kinds, the same
`123456` DOF, the same `SPC1` support rule, all untouched.

## Step — Every exported LRA deck solves, or the export refuses (#172, design note 55, tier L, 2026-09-10)

**Objective.** Make the Phase-C mission claim true per fixture. *"The exported
deck solves in sbeam with verified global equilibrium, continuously in CI"* was
demonstrated on `concept_regional_jet` and `atr42_100`; `ga6_normal` and
`cessna_210` did not solve, `baron_58` and `dhc8_dash8` were never asked, and
the CLI exported all four without a refusal or a caveat. The roundtrip LRA leg's
matrix was the set of fixtures that passed it, so the claim was tested against
its own survivors.

**Agreed first.** Design note 55 (AGREED 2026-09-10, owner), D-55.1…D-55.5, with
D-55.2's tolerance decided at 5 % of `ds` and D-55.5's posture as a hard
refusal. **D-55.6 was added during implementation and the note amended** — see
the key decisions below.

**What the diagnosis found.** The two reported failures had different symptoms
and one cause: *how a joint node joins the chain it lands on* — the sibling of
note 54 D-54.5's *where a joint node sits*, and the phase-2 half that row
forecast.

* `ga6_normal`: `GRID 7605`, the rear-spar post, was **dependent** in the hub tie
  (BM-2) and **independent** in both main-gear ties, because the nearest body
  station to the trunnions is the post. That states `gear → post → hub` in rigid
  links, which sbeam refuses. It was the only such conflict across all six
  fixtures — and the rule that prevents it existed twice already, in the engine
  path's *"one RBE2, hub folded in — sbeam refuses chained rigid elements"* and
  in the support picker's `n.gid not in dependents`.
* `cessna_210`: **not** a topology error. All six fixtures are singly connected
  with no zero-length element, no duplicate node and a worst `CBAR` orientation
  conditioning of 0.28. The h-tail attachment landed **0.0769 in** from a strip
  station — 1.07 % of that chain's `ds` — for a **1638:1** element-length ratio
  on a deck the module's own comment records as running within ~4× of sbeam's
  1e15 refusal. `baron_58` was next at 0.1266 in / 1.33 %; `ga6_normal`'s
  equivalent neighbour is a legitimate 33.66 %, so the two populations separate
  by a factor of 25.

**Deliverables.** In `export/lra_model.py`: the body-tie parent picker gains the
not-already-a-dependent filter (D-55.1); `_insert_on_chain` gains `merge_tol`
and the absorb-into-the-joint semantics (D-55.2), swept per rule 4 to the
hinge/actuator parents on the same chains; `_COINCIDENT_TOL` is documented as
float equality only and `JOINT_MERGE_FRACTION` becomes the geometric owner
(D-55.3); `_refuse_unsolvable_skeleton` is the LM-4 backstop (D-55.5); the
support picker excludes both ends of every `RBE2` (D-55.6).
`tests/test_sbeam_roundtrip.py` gains `LRA_SOLVE_MATRIX` — every CLI-exportable
fixture (D-55.4) — beside `SOB_MATRIX`, which keeps its two SOB-specific
assertions and loses a stale comment about `ga6_normal` having no body data.
`CONVENTIONS.md` §7 gains the skeleton-solvability row; `PROGRAM_SPEC.md`'s LRA
section states the three invariants and the widened gate.

**Test.** Gates 1–3 and D-55.6's precondition are four parametrized guards in
`tests/test_lra_model.py`, each **mutation-tested**: reverting the fixes fails
them on exactly the fixtures the issue named — gate 1 on `ga6_normal`, gate 2 on
`cessna_210` and `baron_58`. Gate 5 is the widened solve gate, run against the
locally installed sbeam: **all six fixtures solve in Imperial**, with the
reaction equal to minus the applied resultant. Gate 6: every delivered load
byte-identical on all six; of 330 baseline channels only `sbeam/lra_model`
moved, on three fixtures, and the per-subcase deck resultant is unchanged
(worst 2.5e-9 of the largest applied card). A regression test covers a project
with no vertical tail, which is the shape no fixture is and which the D-55.2
work briefly broke.

**Key decisions.** (1) *Fix the skeleton, do not refuse.* #172 offered
refuse-with-stated-absence **or** fix; both defects had a correct, cheap fix and
a written precedent in the same file, so refusing four of six fixtures would
have withdrawn the mission claim rather than met it. D-55.5's refusal stays as
the backstop and fires on nothing shipped. (2) *The station is absorbed into the
joint, never the reverse.* Snapping the joint onto the nearby station is the
obvious sliver fix and is note 54 D-54.5 inverted — it would place an owned
location by the mesh. Gate 4 asserts `tests/test_joints.py` still passes
unchanged, so this note cannot undo the last one. (3) *The gear re-parents, it
does not re-route.* Folding it into the hub tie as the engine path folds its hub
would state a load path the project did not enter: `ga6_normal` enters
`carrier BODY`, so its gear still reaches a fuselage node, one station off the
post. (4) **D-55.6 was found by fixing D-55.1 and is recorded as its own
decision.** Re-parenting the gear ties moved them onto the very node the support
picker had clamped, and `ga6_normal` went from *will not factor* to *solves with
a 569.49 lb reaction against a ~0 applied set* — strictly worse. The preventing
rule was already written and explained in `roundtrip._supportable`; `lra_model`
carried half of it. Folding it silently into D-55.1 would have hidden a change
to the support node on two fixtures, so the note was amended and the owner
flagged. (5) *The positional support ordering is kept.* A
nearest-the-carry-through variant was implemented and measured: it changes only
`cessna_210`'s clamp and no gate outcome, so the smaller diff and the shipped
idiom win; D-55.6 changes which nodes are eligible, not the order. (6)
*`ga6_normal`'s SI deck joins the regional jet's existing strict `xfail`.* It is
the same pre-existing sbeam limitation — a dense-path 1e15 condition heuristic
reading a units artifact of the mm frame, where the Imperial twin of the
identical model solves exactly. The fixture sits on that edge because it has
only two untied fuselage nodes, both far from the wing; a dedicated support node
beside the carry-through would move it off permanently and is deferred in §8
with its promoting condition rather than guessed at here.

- **The LRA beam gets its own mesh (note 56 D-56.4, tier L, 2026-09-11)** —
  The fifth slice of note 56, and the one that separates the structural
  model from the replication contract's strip count.

  **Objective.** Cut the LRA beam model loose from the load stations, so the
  structural mesh is decided by geometry and a node count rather than by the
  replication contract's strip count — and so the general load-routing case is
  the one CI exercises.

  **Why it mattered.** The beam *was* the load mesh. The wing chain was the
  WINGGEOM strips outboard of the side of body; the two tail chains were the
  spanwise load stations. Beam nodes therefore *were* load stations, the spanwise
  half of the LM-1 transfer `(F, M)@p → (F, M + (p − n) × F)@n` was an identity
  on every fixture in CI, and the arbitrary-grid path — what a user with their own
  beam model hits first, and the path `lra_import` exists to serve — was the least
  covered code in the package. It also welded two unrelated contracts together:
  the 20 strips the printed oracle freezes were also, unstated, the structural
  idealization. And it is what made a joint an *insertion* into someone else's
  mesh, which is the whole of note 55: `cessna_210`'s h-tail attachment landed
  0.0769 in from a station, 1.07 % of a strip, a 1638:1 element-length ratio and
  the singular solve #172 reported.

  **Deliverables.**

  * **The mesh rule.** A member's node set is its own two ends, the joint
  register's owned locations on it, and `n` grids laid at equal spacing
  **between** consecutive owned points. Segment-based rather than
  uniform-then-merge, and that is the load-bearing choice: grids exist only
  strictly inside segments, so a grid can never land beside a joint. It is what
  makes "joints are mesh points by construction" true rather than asserted.
  `n` is a target, not the node count — a member whose owned points are unevenly
  spread rounds segment by segment — and trading the exact count for the sliver
  is the right way round: one is a number in a form, the other is a singular
  stiffness matrix.
  * **The counts are persisted input.** `Project.lra_mesh` (`LraMeshInput`,
  **schema v65 → v66**, identity hop, five examples re-stamped): four
  `Optional[int]` counts, `None` = the default, defaults **wing 20 per side,
  fuselage 12 per cantilever, h-tail 12 per side, fin 10** (owner ruling
  2026-09-11). Persisted rather than a flag because the count decides which
  grids a delivered deck carries, so a project exported at 20 a side must
  reopen at 20. Classified dimensionless with a reason; four field-registry
  rows on the geometry page; `DATA_DICTIONARY` regenerated.
  * **A member runs to its own end.** The wing chain stopped at the outermost
  strip *midpoint* — 5.0 in inboard of the tip on `ga6_normal` (2.5 % of
  semispan), 12.1 in on `atr42_100`. That is exactly the omission D-54.5 fixed
  for the fin, and the reason it survived on the wing is instructive: the fin's
  got fixed because a T-tail tie made the tip a *joint*, so something forced the
  issue. Nothing forced it here. D-56.4's "the member's ends" is the general
  form of that fix.
  * **One owner for where the wing beam is.** `joints.wing_lra_point` was already
  the register's private resolver; it is public now, over
  `wing_geometry.chord_fraction_x`, so the exporter meshes from the same
  construction the register places joints on instead of growing a fifth
  spelling of the chord-fraction line. Verified against the delivered load
  stations on all four fixtures: agreement to 1.4e-14 in.
  * **`JOINT_MERGE_FRACTION` retires**, and what replaces it is a different
  question. Nothing is inserted, so an insertion-induced sliver cannot arise.
  What *can* still arise is two **owned** locations genuinely close together on
  one member — two joints, a joint and a trunnion — where both must be nodes
  because dropping either drops a load path. `_MIN_ELEMENT_FRACTION` catches
  that, its message names the two points and asks for the geometry rather than
  for a bug report, and the threshold is measured rather than chosen: the one
  observed singular solve was 1:1638, the tightest legitimate element across
  four fixtures at three mesh settings is 1:38, and the floor sits at 1:200.
  Note 55's 5 % is **not** the precedent — that number decided whether to merge
  a station, a question about strip scale; this one decides whether to refuse a
  solve, a question about stiffness contrast.

  **Test.** Note 56 gates 5, 10 and 11. Gate 5 (no member can carry a sliver) is
  asserted on every member rather than the two tail chains the merge band covered.
  Gate 10 is the note's own argument in one test, in two halves because either
  alone is weak: **position** — no wing chain node sits on a load station, the
  side of body excepted, since a station coinciding with an owned joint is a fact
  about the airplane; and **resultant** — meshing the same project fine
  (31/17/15/19) and coarse (7/5/4/5) moves no case's six-component resultant,
  which is what says the mesh is free to move at all. Gate 11 is the schema hop.
  The round-trip solve gate passes on every CLI-exportable fixture with its two
  known SI xfails (sbeam's dense-path condition heuristic) unchanged — evidence
  that the renumber and re-mesh moved grids and nothing else, since the transfer
  routes by position and never by id.

  **Key decisions.**

  1. **Segment-based spacing over uniform-then-merge.** Uniform placement plus a
   merge band would have been the smaller change and would still have improved
   on note 55 — what gets absorbed would be an anonymous grid rather than a load
   station carrying a gid and a load. It was rejected because it keeps a
   tolerance constant and therefore keeps the class: the note's sentence that
   the sliver dies structurally would have been false. Segment-based is the only
   reading that makes it true.
  2. **Gear and engine nodes are model nodes, not chain stations.** D-56.4 lists
   "its gear / engine / hinge / actuator nodes" in the member's node set. The
   hinge and actuator fittings are chain-owned points here, because they already
   were; the gear trunnions and the engine mount/hub stay their own nodes tied
   by `RBE2` to the nearest chain node, which is the topology that already
   shipped. Making a tie parent exact rather than nearest is a real improvement
   and a separable one — it changes a load path, and this step changes enough.
  3. **The fuselage is meshed too, though it was never the degenerate case.** Its
   stations were the *outline's* section stations, not load stations, so the
   note's §1.4 argument never applied to it. It moves anyway, because the
   alternative is that how finely the beam is analysed remains a consequence of
   how finely someone drew the body — a different quantity wearing the same
   number.

- **The LRA model owns every grid it writes (note 56 D-56.3, tier M,
  2026-09-11)** — The fourth slice of note 56, and the one that makes the
  deliverable self-contained. `lra_model.py` imported `sob_gid`,
  `tail_span_gid` and `tail_control_gid` from `sbeam_bridge` and took
  `band("balanced-gear")` directly; its right wing chain carried the wing load
  stations' own `gid` values. So the grids of the one artifact sloads ships
  were numbered by four artifacts, three of which were not deliverables and two
  of which D-56.2 deleted a day earlier. The model now allocates every node
  from a contiguous run it owns, `20001–30999`, in 999-wide sub-bands on a
  1000 stride so `gid // 1000 - 20` is the family index — a property a test
  pins, because a band widened to 1000 would put its last id in the next
  family's thousand and the readability would fail silently.

  **The renumber is once, and the scope of "once" is the whole model.**
  Ruling 1 (nothing downstream reproduces any sbeam output) is what makes a
  wholesale move cheaper than a partial one, so the sub-bands are sized for
  D-56.4's settable per-component grid counts rather than for today's node
  count: the next slice changes where nodes sit and how many there are without
  touching numbering. `sob_gid` moved to `lra_model` in the same pass — it had
  exactly one production consumer and this was it.

  **The band registry does not collapse here, and the note's "25+ → ~8" is
  still owed by a later slice.** Eleven LRA bands replace six, because the
  families the model borrowed are now its own and each keeps a registered
  owner: `owner_of` must still answer "who put this id in my deck?". The bands
  the LRA vacated are left unregistered rather than reused, as D-56.2's were,
  and the ones still registered below that line — `wing-stick`, the two body
  runs, the two spanwise and two chordwise tail runs — belong to the
  **applied-load model**, which numbers nothing that ships and retires with it
  at D-56.9. `wing-stick`'s `GID 1` hole stays open for the same reason:
  closing it now would renumber every station twice.

  **Gates 3 and 4 land, and gate 3's stated motivation did not survive
  measurement.** Gate 4 — every grid in the emitted LRA deck comes from the
  LRA's own band, on four fixtures — is the gate this slice exists for, and it
  is asserted from deck text rather than from the builder because an id that
  reaches a file is what a solver splices on. Gate 3 — no GID defined at two
  positions across the shipped decks — passes by construction, and note 56
  §1.2's illustration for it does **not** reproduce: `GID 7` did not name one
  point in `wing_loads.bdf` and another in `lra_model.bdf`. The LRA took the
  wing stick band's ids for the stations it shares, so the shared ids named the
  same point, and the gear ids shared with the balanced deck were the same
  trunnion in both. The **borrowing** was real — provenance, which gate 4
  catches — and the only position collision on record (the balanced deck into
  the spanwise h-tail band, review F-C1) the registry closed two months ago.
  The gate is kept and its docstring states this: it guards a property that was
  true by accident, which is what the next deck family would re-open.

  **One latent alias removed while the ids were moving.** The fin tip and the
  h-tail's left attachment both allocated attachment index 2, safe only because
  a T-tail layout has no left attachment — a mutual exclusion holding an id
  apart, which is the class the registry exists to make impossible. The fin tip
  takes index 3 and the inserted control-node parents shift past it. The stale
  `transferred_case_loads` docstring sentence claiming the limit→ultimate
  factor is applied at emission — the incidental correction note 56 §3 names —
  is deleted in the same pass; the code applies nothing and G-OR-71 guards it.

  **The delivered loads do not move.** Only `sbeam/lra_model` re-stamps, four
  channels, one per fixture with an LRA deck. Every applied-load CSV, the
  balanced deck, the mass deck and both reports are byte-identical, and the
  round-trip solve gate passes on every fixture with its two known SI xfails
  (sbeam's dense-path condition heuristic) unchanged — which is the evidence
  that the renumber moved ids and nothing else, since the transfer routes by
  position (`nearest_node`) and never by id.

- **What the beam grids cost the distribution is published (note 56 D-56.10,
  tier L, 2026-09-12).** The ninth slice of note 56, and the one D-56.9 owed the
  same day it landed: the applied appendices had begun saying *"what the lumping
  costs the distribution is stated in the VMT comparison"* and no such
  comparison existed. It does now, as **Appendix G** — one table of the widest
  gap per internal-load channel per member over every case, and four figures
  drawing that gap along the span. The owner is the new
  `sloads/report/lumping.py`, and the whole appendix rests on one sentence: an
  internal load at a cut is the static resultant of everything outboard of it,
  transferred to the cut. Written that way it serves a wing, a fuselage, a
  horizontal tail and a fin from one function, with no per-component
  integration path to keep in step, and it reuses the LM-1 owner the
  aggregation itself routes through.
- **D-56.10 was amended twice before any code, per rule 1.** *(i) There is no
  shared critical case to draw.* The decision called for four figures on one
  case so they could be read together; the four components' condition registers
  are disjoint by construction — `W-nn`, `F-nn`, `HT-nn`, `VT-nn`, each
  surface's own FAR conditions — so no case is run by more than one of them and
  the premise was simply false about the data. Each figure now names its own,
  and it is the case that bends that member hardest; the case where the
  *lumping* is worst is a different question and the table answers it over every
  case. A guard pins the disjointness so the amendment cannot outlive its
  reason silently. *(ii) The figures plot the gap, not the two curves.* Three
  channels in two versions is six colourless lines carrying three different
  dimensions; no single y-axis holds that honestly and no greyscale reader
  separates it. Nothing is lost, because both sets are already printed in full —
  the station set in B.2 and C.2, the delivered set in B.1, C.1, D and E — so
  the difference was the one thing the report did not carry.
- **The generic computation is cross-checked against the owner it
  generalises.** `report.applied.sob_internal_loads` states the wing's internal
  load at the side-of-body cut and has been gated against the solver's own CBAR
  end force since step 13. The new curve reproduces it — shear, bending **and**
  torsion — at the wing root of every case of four fixtures. That check is what
  made it safe to write one function for four members rather than four
  integrations; without it the appendix would rest on arithmetic nothing else
  had ever agreed with.
- **The numbers are larger than the decision assumed, and the fuselage is the
  outlier.** Worst deviation as a share of the channel's own peak, over every
  case, on the four loaded fixtures: wing shear 19–35 %, wing bending 3–5 %,
  wing torsion 17–77 %; both tails under 1.1 % in bending, 6–14 % in shear,
  9–21 % in torsion; **fuselage shear 82–197 %** and fuselage bending 14–19 %.
  The fuselage number is real rather than an artifact — on
  `concept_regional_jet` a ~107,000 lb spar carry-through reaction lands on a
  node one bay from where it acts, against a peak station shear of 54,588 lb.
  Ruling 15 says state it and do not gate it, and it is stated; it is also the
  strongest argument yet that the fuselage's owned mesh points should include
  the carry-through stations, which D-56.4's mesh does not currently guarantee.
  That is recorded in the note and owed an issue of its own; it is not fixed
  here, because this slice's job is to measure and changing the mesh to improve
  its own measurement in the same change would be marking its own paper.
- **Bending survives lumping best on every member of every fixture** — under
  5 %, against tens of per cent in shear and torsion. That is the expected
  shape, because bending is an integral of the shear: moving a load a short
  distance perturbs it by the load times that distance, while the shear at a
  crossed cut moves by the whole load. It is worth a reader knowing, since
  bending is what most of the structure is sized by, and the appendix's prose
  says so rather than leaving four figures to imply it.
- **Three guards outside the feature caught its defects**, which is the argument
  for having them at all: the platform-stability sweep refused three keyed
  `min`/`max` picks and sent them through `picks.extreme`; the rendered-LaTeX
  sweep refused markdown emphasis in the new appendix prose; and the
  package-layout guard refused the new module until `PROJECT_GUIDE.md` §4 listed
  it. None of the three is about lumping, and all three were right.
- **The fin's withholding is honoured.** OR-133 withholds the fin's spanwise
  loads on a non-conventional layout, so Appendix G omits the fin comparison
  there rather than publishing sideways a set section 6 declined to publish.
  `atr42_100` and `concept_regional_jet` are T-tails, so the guard is live in
  both directions on the shipped fixture set. A channel with no producer — the
  fuselage carries no torsion in this analysis — is left out of its figure
  rather than drawn flat, so no legend entry invites a reader to hunt for a line
  hidden under the axis.
- **Docs and gates.** `ORACLE_REPORT.md` §3.14 and a section-register row;
  `PROGRAM_SPEC.md`'s applied-set entry; `PROJECT_GUIDE.md` §4; and — reversing
  the note's own "no citation" line for this one decision —
  `docs/20_theory/00_theory_sources.md` gains the lumping rule: what LM-1
  preserves exactly, what it does not, and why there is no printed oracle and no
  tolerance for the second half. Ten tests in `tests/test_lumping.py`,
  including a hand-computed cantilever whose numbers are written out rather than
  compared against a second implementation.

- **CONM2 gets its own CG grids, and the mass model is checked by GPWG (note 56
  D-56.6 + D-56.7, tier M, 2026-09-12).** The seventh slice of note 56, taken
  **before** D-56.9 rather than after: 6a left `export/mass_cards.py` importing
  `beam_station_gid` from `report.applied`, and D-56.9 retires that band, so
  running this first deletes the consumer and the band retires once instead of
  being kept alive for a slice. One `GRID` per card at the item's own centre of
  gravity, in a new `mass-cg` band, with a zero `CONM2` offset; `_attach_gid`,
  its CR-B-1 tie rule and the offset arithmetic all go, and so does the standing
  limitation that wing items hung on a fuselage node — with the header sentence
  that stated it.
- **The precondition the note had left open held.** Gate 6 rested on sbeam's GPWG
  accepting unconnected grids and nobody had checked. `compute_gpwg` walks
  `CONM2` cards and grid positions with no stiffness matrix, so a deck of grids
  and masses with **no elements and no `SPC`** returns the hand-computed mass and
  CG, and applies an offset identically — which is what makes "the masses did not
  move, only the nodes they sit on" checkable rather than merely stated.
- **The band went to `13001`, not the `11001` the note proposed.**
  `11001-11999` is the `lra-cbar` **EID** run. The `CONM2` EID bands declare
  `clear_of_gids` so that every id in a spliced deck names one owner by
  inspection, and that rule runs both ways: a GID band inside EID space breaks it
  from the other side. The registry's overlap guard caught it on the first run.
- **Gate 6 lost a third and gained a measured tolerance.** Its inertia clause is
  struck (ruling 16): `GpwgResult` carries a total mass and a CG and nothing
  else, so that clause named an output the pinned sbeam does not produce. And the
  agreement is not exact — across five fixtures × two unit systems × every
  payload case the worst disagreement is **1.3e-7**, because GPWG reads the
  *printed* deck and `deck_format.fmt` writes seven significant figures
  (`46.62142525735088` prints as `4.662143E+01`). The gate is `rel_tol=1e-6` with
  that reason, rather than a tighter number asserting that a seven-figure field
  carries more than seven figures.
- **Five roundtrip legs were retired and the loss is counted, not asserted.**
  M-b went by design with `inertia_only_cards`; the `MASSSET`-gap pin and the two
  `flatten_mass_case` legs went with the workaround they served. **M-a and M-c
  are a real loss** — sbeam's own mass-matrix assembly and the `GRAV`
  acceleration path are no longer exercised. Three things make that affordable,
  each checked rather than assumed: **GPWG honours `MASSSET` where `SOL 101` does
  not**, so the surviving gate reads the deck as shipped instead of a flattened
  transform of it — strictly better on that axis; it still runs per case in both
  unit systems; and the **C1 defect class did not leave with its mutation leg**.
  A 25.4× SI `GRAV` error is caught by card text against an independently written
  constant at `rel=1e-12` in both systems. A solve was never the only thing that
  could see C1 — it was only the thing that did.
- **A defect prevented, from #173's own lesson.** The deck still carries `SOL 101`
  over what are now unconnected grids, which dies "singular stiffness matrix" —
  #173's defect class exactly, arriving at a different file in the same milestone
  #173 closes as superseded. `test_the_mass_model_carries_no_structure_and_says_a_solve_is_singular`
  makes the header's statement a gate rather than a courtesy.
- **The mass model entered the digest baseline for the first time**, 234 → **244**
  channels. It had none, so this slice could rewrite the artifact end to end —
  every grid new, every offset gone, the beam deleted — and no digest would have
  moved. That is the hole `sbeam/balanced_deck` was added to close in B8a-2, one
  artifact over, closed the same way. It paid for itself immediately: the new
  channel put the deck in front of `test_case_ids`' deck-number parser, which
  read `SUBCASE 9301 / LABEL = CG1` as a per-component load-case pairing. It is
  neither — a `MASSSET` subcase names a **payload** case, and `CG1` is not a case
  id and has no index row. The parser now skips the mass channels by name.

- **What a load is became a producer's declaration, not a unit lookup (#170, review R-8, tier M, 2026-09-09)** — `units.is_load_unit` had one input that mattered, the unit string, and `ft-lb` is the unit of a torque whether that torque is something the structure must sustain or something the engine is rated at. ENGLOADS publishes both in one condition: 23.361(a)(1) states GA-6's mean takeoff torque (554.4 ft-lb) as the input and the mount torque derived from it (−737.3 ft-lb, the rating × the 1.33 mean-torque factor) as the load. The predicate could not tell them apart, so the channel stated 23.303's 1.5 for both and the ULTIMATE surfaces printed 831.6 ft-lb of mean takeoff torque. Note 48 found it while reviewing #154, filed it and deliberately did not fix it there (§1.2, §2.4) on the grounds that it is a question about what a load *is* rather than about which channel renders it — answering it inside a channel change would have hidden it. `units.NON_LOAD_QUANTITIES` is the answer and the owner: a frozenset of `LoadValue.quantity` hints that override the unit string, joined by `"characteristic"` (a machine rating) and `"diagnostic"` (an equilibrium-quality number) beside the `"mass"` that was already there for the `lb` ambiguity. The field now answers two questions — SI dimension and load-ness — and the code says so in both directions, because `report.content._load_dimension` must keep testing `"mass"` alone: a characteristic is not a load but still has a dimension, and routing it through the load-ness set would leave an engine rating stated in Imperial inside an SI document. The class was swept rather than the filed row, per rule 4 and the 2026-09-04 review's R-8: three engine ratings (`mean_takeoff_torque` on both the reciprocating 23.361(a)(1) and the turboprop path, `max_continuous_torque`, `max_accelerating_torque`) and the two `balance` pre-closure residuals, which were factored and `-ULT`-marked beside the applied loads of the case whose closure quality they describe — while their percentage forms, never in load units, were not, so one pair of numbers was marked two ways. Five quantities lose an `SF` cell; no load value moves, and the oracle and closure suites are unmoved. Four guards in `tests/test_safety_factors.py` hold it: the predicate's own truth table at the owner; the per-value discrimination across every fixture in **both** directions (a blanket exclusion of `ft-lb` in ENGLOADS would pass the forward half while silently dropping the factor from the mount torque, the gyroscopic couples and the stoppage torque); a reached-every-key assertion so the class cannot be sampled instead of swept; and a vocabulary drift guard refusing any published `quantity` hint that has no row at an owner.

- **The five per-component solver decks are deleted (note 56 D-56.2, tier L,
  2026-09-11)** — The third slice of note 56, and the one the note is named for.
  `sbeam_bridge.py` shipped the suite's loads as five families of per-component
  deck: a wing CBAR stick model, a fuselage FORCE deck, a chordwise tail deck,
  two spanwise empennage decks and a control-surface deck, each with a CSV
  companion. All ten files are gone. They were separate structural models of one
  piece of the airplane apiece, sharing an ID space with the deliverable — the
  full-span balanced free-free model, which is the whole airplane with aero and
  inertia together — and the deliverable was borrowing GIDs *from* them, so
  `GID 7` named one point in `wing_loads.bdf` and another in `lra_model.bdf`.
  Roughly two-thirds of the milestone's open export work was maintenance on
  concepts that were not what ships.

  **The sequencing is the note's, inverted for this group, and the inversion was
  checked before it was taken.** Note 56 ordered the move of the applied-load
  family before this deletion, on gate 1: deleting the decks before rehoming
  what they sit beside would take the oracle report with them. That reasoning
  belonged to the *report tables* group, which moved in the previous slice. For
  the applied-load family an AST closure settled it the other way: the family's
  entire coupling to the deck writers is **fourteen names, every one a GID
  allocator, a band or a results-coercion helper** — which is the structural
  form of D-56.9's own statement that `AppliedLoad.gid` is a per-component
  deck's GID. Deleting first keeps all fourteen and removes 1,400 lines that
  touch none of them; moving first would have meant writing a
  `report → export.sbeam_bridge` import for those fourteen and then moving them
  again one slice later. Note 56 §8's confirm-before-delete resolved clean in
  the same pass: the oracle report draws **no** per-component deck table, so
  nothing needed rehoming.

  **Three standing limitations were retired, not reworded.** `centerline-clamp`
  (the wing stick model's SPC at BL 0, and the 23 % by which its reaction
  overstated a root load), `flight-only-body-deck` and `export-case-filter` each
  described a limitation of a per-component view and each pointed the reader
  toward the assembled deck. With the views gone the sentences have no subject,
  and keeping them would describe the deliverable as having a limitation it
  cannot have. Retiring a caveat is the one edit that can quietly widen a claim,
  so the owner was asked before the slice began and the three go in this commit
  against `test_methods_stamp`'s pinned key set — which is what that contract
  exists for.

  **Five gates changed authority and kept their form; two narrowed and say so.**
  G-OR-59 and Appendix D's one-load-set gate now read
  `applied_loads(…)` instead of the deleted span CSVs — the row set both were
  always built from, which is why the appendices are unchanged by the deletion.
  G-OR-37, the gate that the delivered loads are the applied set and not a
  differenced cumulative column, is summed from the applied set itself rather
  than re-derived from deck text. The free-free geometry mutation and the
  deck-comment width sweep moved to the assembled and LRA decks, which is where
  they belong: those are the decks that ship. The two that narrowed are stated
  in place. **G-OR-73** lost its "deck and document agree" comparison, because
  the surviving decks have no CSV companion and the surviving CSVs have no deck;
  both halves were always compared to the case's own `safety_factor` rather than
  to each other — that was the assertion carrying the force, and it is
  untouched. **The swapped-subcase mutation** became a deck-text check: every
  balanced free-free case has a zero resultant by construction, so swapping two
  subcases' load sets leaves all six reactions at zero and no reaction-based
  gate can see it. Writing a solve that proves nothing would have been worse
  than asserting the property where it is observable.

  **Two gates were lost outright, and neither is disguised.** The wing stick
  deck's solve gate took `test_the_sob_internal_load_is_the_first_outboard_
  elements_end_force` with it: the closed-form side-of-body load is still gated
  against the cumulative table, but the solver cross-check needs a deck with a
  CBAR outboard of the SOB node whose cards are that wing case's, and the LRA
  deck's cases are balanced cases — a different claim, not a rename, and it
  belongs to D-56.4's mesh. G-OR-90 lost its deck-comparison leg for a better
  reason: it compared `applied_loads` against `tail_span_force_moment_cards`,
  two renderings of one load set, which is a real check only while two writers
  can disagree. D-56.9 makes the applied set *the* authority the delivered cards
  are written from, so that comparison is now tautological; the leg that carries
  the OR-143 defect never read a deck and is untouched.

  **One defect this slice creates and does not close**: the case index still
  publishes a `LOAD/SUBCASE (component)` column, and no artifact quotes those
  numbers any more. `test_case_ids` asserts the absence explicitly — it fails if
  a component pairing reappears — so the gap is recorded rather than silent, but
  a shipped index naming a deck that does not exist is misleading content and
  belongs to #209. The Imperial digest re-stamps deliberately: 330 channels →
  280, of which sbeam goes **83 → 33**, the note's own measure of the reduction.

- **The raked-root ruling (#219, design note 54 D-54.3, tier M, 2026-09-09)** —
  `resolve_tail_planform` rebased GA6's raked fin root onto one waterline and
  the LRA swung 33.5 in aft at the root (found 2026-09-07, Figure 24). The
  decision, made explicit per D-54.3: below (and above) the span both edges
  cover, the *chord* stays on the closed-polygon clamp that fixed the 8 % area
  over-read, and the *axis* — every chord-fraction line `TailPlanform.x_at`
  evaluates: LRA, 25/50 % load points, hinge — continues on the edges' own
  slopes, because the kink was an artifact of pointwise evaluation on the
  collapsing closure chord, not of the surface. The GA6 fin axis is now
  straight root to tip (slope constant to 1e-9, gated); square-root fins are
  byte-unchanged, asserted. Delivered numbers move on `ga6_normal` only, the
  one raked fixture: yaw acceleration −0.6 to −2.9 % across the four lateral
  cases (fin loads and Ny bit-identical — a lever arm moved, not the
  aerodynamics), lateral pins re-stated and the Imperial baseline
  regenerated. Rule-4 sweep: `wing_geometry.interp_x` now
  extrapolates the nearest segment below range as documented, and the dead
  `tail_geometry._interp` clamp is removed. Spec: PROGRAM_SPEC `tail_span`
  section; the fixture-side follow-through (fin span/geometry reconciliation)
  rides D-54.6 with #260.

- **The deliverable tables that are not decks move to `report/` (note 56 D-56.1,
  tier M, 2026-09-10)** — The second slice of note 56, and the safe half of
  D-56.1's three-way split. The case index, the governing safety-factor table,
  the gear interface report and the export-scope filter had lived in
  `export/sbeam_bridge.py` since the first consumer happened to be there, and
  stayed through five milestones; none of them emits a card. The move was
  chosen to go first because gate 1 makes it the thing that stops the later
  deletions taking the oracle report with them — `report/content.py`,
  `report/oracle_sections.py` and `report/methods.py` reach into the bridge at
  ten sites, so deleting the per-component decks (D-56.2) before rehoming what
  they sit beside would have removed the one actively-used deliverable along
  with four unused ones. A dependency scan settled the order: this group's
  closure needs **nothing** from the code that stays and **nothing** reaches
  back into it, so it moves whole, while the applied-load family does not (see
  below). 409 lines out; `sbeam_bridge.py` 3,013 → 2,639. The export package
  stops re-exporting the moved names rather than keeping a shim, and a guard
  asserts their absence — under ruling 1 nothing downstream reproduces, so a
  compatibility alias would buy nothing and would leave one name at two
  addresses, which is the condition D-56.1 exists to end. Deliverables are
  byte-identical across the move (gate 8, gate 1). **Two allowlists keyed on the
  old path had to be corrected, and one of them mattered:**
  `test_ultimate_contract`'s `_ULT_CHANNEL` matches the *call text* at each GUI
  download site to decide whether a CSV is ultimate by construction, so a page
  whose call had moved to a new module alias would have gone on passing while
  the guard no longer recognised it. That is the second text guard this note has
  caught keyed to a name it was about to lose, after G-OR-71 in the first slice,
  and it confirms the standing caution recorded there. **What it did not move,
  and why:** `sob_internal_loads` and `CENTERLINE_CLAMP_NOTE` are report-only in
  their consumers but are still referenced by deck writers that D-56.2 deletes,
  so moving them now would have required either a reversed `export → report`
  import or a deferred one to break the cycle; both are worse than waiting one
  step. The applied-load family stayed for a substantive reason rather than a
  mechanical one: `AppliedLoad.gid` is a **per-component deck's** GID, and
  G-OR-90 — the gate asserting every card the deck writes at a GID is the
  appendix's row at that GID — reads `tail_span_force_moment_cards`, which
  D-56.2 deletes on the grounds that it has no production consumer. True, but it
  is the authority for that gate, so deleting it removes the gate rather than a
  deck. What the appendix's `gid` column means once the per-component decks are
  gone was a decision note 56 had not recorded; raising it produced **rulings
  10–12 and D-56.9** in the same session, and the note is amended with them here
  — the LRA grids are where the loads and moments are *calculated*, so the
  appendix row and the card are one object at one point again and G-OR-90 keeps
  its row-for-card form against a different authority. Two of the note's own
  statements are reversed by that amendment and marked in place rather than
  edited away: §5's acceptance of a coarser wing distribution (which held only
  while the grids were somewhere to hang a check) and §7's "no schema change"
  (settable per-component grid counts are persisted input, so `SCHEMA_VERSION`
  bumps 65 → 66 with a migration hop). Neither affects this slice's code; both
  had to be recorded before the next one starts.

- **The comparison basis gets one owner, and the LIMIT contract stands by
  ruling (#193, design note 58, tier M, 2026-09-11)** — the standing proposal
  to deliver ultimate loads (owner, 2026-09-07) resolved the other way by the
  same owner: delivered output stays LIMIT permanently, aligned with the
  oracle GUI's stated-never-applied posture, and what moves to the ultimate
  basis is the *comparison* — `safety_factors.ultimate_basis` keys every
  governing-case pick across cases whose prescribed factors differ, which is
  exactly one family (23.367(a)(2), ULTIMATE SF 1.0 amid LIMIT 1.5 since note
  44 OR-172's admission). A complete ranking-site sweep found one production
  mixed-factor reduction — the Loads Plots pointwise envelope — and
  `envelope_extremes` now requires the per-series factors and refuses a mixed
  set by name rather than publishing a value on either wrong basis (no
  factored value is ever delivered; the G-OR-71 class stays dead). Measured
  before deciding: no shipped pick flips (the governing fin case leads the
  ULTIMATE case ~2.2× on both twins, pinned in the re-keyed G-OR-113), so the
  change moved no delivered byte and bought the rule while it was free. The
  sweep's by-catch — the summary report's v-tail governing table reading
  `build_critical` while its chordwise table reads `default_critical` — is
  filed as #272.

## Release cut: **sloads 0.8.2** (the oracle technical report, LIMIT with the factor stated), tag `v0.8.2`, 2026-09-08

**Objective.** Close band **B3** — the oracle technical report (design note 44,
milestone row #151): a clean, modern formal LaTeX report of the oracle GUI's
analysis, generated from a new `oracle_app` page, built one owner-agreed
iteration at a time under the OR-13 freeze (solver and existing oracle GUI
frozen additive-only, a hashed manifest, defects in frozen code filed not
fixed, OR-15 the sole admission mechanism).

**Deliverables** (the `[0.8.2]` changelog section is the release note):
- **The report, whole:** iterations 1–10 all shipped — front matter and the
  issue-package build (`ReportSpec`, fingerprint provenance, `MANIFEST.txt`);
  §2 Loads Configuration with the planform, weight-envelope and V-n figures;
  §3 Wing Loads + Appendix B (applied split from carried); §4 Fuselage Loads +
  Appendix C (the p198 conditions published, the carry-through entered as a
  station, notes 46/47/48/50); §5/§6 the two tail sections + Appendices D/E;
  §7–§9 aileron, flap and tab as pressure sections with no appendix by gate;
  §10 engine mount, §11 OEI, §12 landing; and Appendix A as the balanced V-n
  condition register — the candidate set every selection is made from,
  published as a page and as `<project>_vn_conditions.csv`. Byte-deterministic
  from `ga6_normal` and `baron_58` in CI, concept-content-free by guard.
- **The load-output contract inverted (note 49, OR-116/OR-117):** every load
  sloads delivers is **LIMIT with the safety factor stated per case and
  applied nowhere** — module views, both reports, the CSVs and the sbeam deck
  — gated tree-wide (G-OR-71…G-OR-74), with the two prescribed-ultimate
  families (23.367(a)(2), 23.561(b)) the stated exception at SF 1.0. The GUI's
  21 stale ULTIMATE claims swept by an AST gate (#192).
- **The review that would not let Rev A leave DRAFT:** the owner-commissioned
  2026-09-08 GUI/report/CSV review filed **#227–#246** in-session (rule 5);
  the 0.8.2 subset **#227–#238** all fixed — ground-attitude labels read the
  owner not the tuple order, every cross-reference resolves, gyro prose
  follows the printed case set, SF columns and SI conversion completed.
- **Cut hygiene as its own items:** #190 (ten shipped notes archived keeping
  their numbers, the backlog re-cut, parked rows promoted to #247–#252) and
  the review quartet — #183 (a note closed by a history fragment says SHIPPED,
  guarded), #184 (the tag waits for a green `main`: `--check-main-run`),
  #187 (a live note's INDEX row is a pointer, capped and status-free by
  guard), #189 (process docs describe the process that exists;
  `GIT_FLOW_GUIDE.docx` demoted, the standard tree guardable-formats-only by
  guard). Found at the §3.5 walk and fixed pre-cut: the three-view drew the
  fin's loads reference axis in the top view (`lra_overlays`, the last OR-15
  admission of the milestone).
- **Version** `0.8.1` → **`0.8.2`** (a new GUI capability — the report page —
  and no schema break: the v60 → v61 hop converts the spar-station entry by
  the airplane's own polylines, old saves migrating).
- **Changelog cut** — `scripts/build_changelog.py 0.8.2 --date 2026-09-08`:
  **91 fragments** consumed into `## [0.8.2]`, **39 history entries** rolled
  to the top of this file, a fresh empty `[Unreleased]` opened.
- **History roll** (`RELEASE_PROCESS.md` §4.3): notes **44** (the report — the
  milestone's plan of record) and **53** (thrust line) move to `40_history/`;
  note **49** stays live — its header states an unshipped 0.8.3 half (OR-81's
  marker sweep, OR-90…OR-92), and the mechanical rule rolls a note whole when
  its status reads shipped, not by halves; notes 21/51/52 stay with their open
  milestones.
  The live file passed the **1,500-line threshold**, so everything below the
  0.8.1 cut block froze verbatim into
  [`51_completed_development_to_0.8.1.md`](51_completed_development_to_0.8.1.md).
  `tests/test_frozen_set.py` is deleted — the OR-13 freeze is milestone-scoped
  and lapses with this cut, which is also what admits 0.8.3's #25 (empennage
  geometry) and the frozen-code defect queue (#177, #210, the `tail_span.py`/
  `balance.py` docstrings citing archived notes' old paths).
- **Gates at cut:** `pytest` **3809 passed / 32 skipped / 1 xfailed / 0
  failed**, `ruff` clean, `mypy` clean (`sloads/`), `scripts/smoke_test.sh`
  **PASS** (both front-ends boot, CLI CSV checked),
  `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on 7 tracked keys,
  the §3.5 by-hand walk done (it found the fin LRA defect above), no open
  CRITICAL/MAJOR review findings.

**Key decisions.** *A report is a view, and building a view is not an occasion
to adjust what is viewed:* the OR-13 freeze held for the whole milestone as a
hashed manifest, and every one of its admissions is a scoped OR-15 comment on
the hash it moved — the freeze ends by deletion at the cut, not by erosion.
*The factor is stated, never applied* (note 49): the milestone that documented
the analysis is also the one that made every delivered load say what has not
been done to it. The review's findings became milestoned issues in-session,
and the ones that could not ship in 0.8.2 are 0.8.3/0.9.0 rows, not prose.
**Band B3 retired with the cut; band B4 (0.8.3 — the empennage geometry model,
unblocked by this cut's freeze lift) is the milestone in flight.**
