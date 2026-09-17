# Changelog archive — releases up to and including 0.8.3

**Frozen record — do not edit.** Rolled off `CHANGELOG.md` at a release
cut per design note 61 CV-5 (the rule design note 26 DV-1 gave the history
file). Verbatim; the live changelog holds the current cycle and the
previous release block.

---

## [0.8.3] — 2026-09-13

### Added

- **The LRA beam model gets a three-view renderer (`scripts/plot_lra_model.py`, tier S, 2026-09-10).**
  A display-only analyst tool over the public exporter API: project JSON in, one
  4-panel PNG out (isometric + plan + side + front) of the step-12 skeleton --
  CBAR chains by section family, RBE2 ties, BM-5 tagged nodes, the SPC support
  -- with the planform/body outlines overlaid from the same geometry owners the
  exporter reads (`--no-outlines` to omit; wing/h-tail edges are draped at the
  beam chain's waterline, a stated picture convention). The exporter's refusal
  contract is kept verbatim: an `LraRefusal` prints its named datum and exits 2,
  never defaulting it. matplotlib joins the `dev` extra; smoke-tested on the
  conventional, T-tail and twin example projects (`tests/test_plot_lra_model.py`).

- **The oracle report states what the beam grids cost the distribution (note 56
  D-56.10, tier L, 2026-09-12).** New **Appendix G**: one table of the widest
  gap in each internal-load channel of each member, over every case, and four
  figures — wing, fuselage, horizontal tail, fin — plotting that gap along the
  span for the case that bends the member hardest. It is the counterpart to
  D-56.9, which sums the applied set onto the beam's grids: the set's
  **resultant** is preserved exactly and gated, and this is where the
  **distribution** it moves is stated instead of left to be discovered.
- **New owner `sloads/report/lumping.py`.** The internal load at a cut is the
  static resultant of everything outboard of it, transferred to the cut through
  the same LM-1 owner the aggregation uses — one rule for shear, bending and
  torsion on all four members — evaluated twice about the same cuts, once from
  the load stations and once from the delivered set. **No solver is in the
  loop**, so the figure is a discretization comparison and not an idealisation
  one, and it is reproducible in CI. Cross-checked against
  `sob_internal_loads`, the single-cut instance it generalises, at the wing root
  of every case of four fixtures.
- **There is no acceptance tolerance, and the appendix says so.** The size of
  the difference is a function of the grid counts the project sets, so a fixed
  limit would fail a coarse mesh behaving exactly as specified.

### Changed

- **The applied load set gets its right address and `sbeam_bridge.py` ceases to
  exist (note 56 D-56.1, tier M, 2026-09-11).** `AppliedLoad`,
  `applied_loads` and its five component row builders, `applied_body_moments`,
  `applied_load_csv`, the side-of-body internal loads and the station numbering
  they state all live there now. It was never a bridge to sbeam: it is the record
  of what is applied and where, which the oracle report's applied appendices are
  built from directly.
- **Import from `sloads.report.applied`.** No shim is left at the old address and
  the export package no longer re-exports any of it — a guard refuses both.
- **Nothing delivered changed.** Module views, the case index, both reports,
  every CSV and every deck are byte-identical across the move.

- **The applied load set is stated at the LRA grids (note 56 D-56.9, tier L,
  2026-09-12).** `applied_loads` returns one row per (case, grid): every
  aerodynamic station and every concentrated mass is summed onto the nearest
  node of the member that carries it, with the exact lever-arm couple. The two
  grid sets do not align — the beam mesh is decided from geometry alone — so
  several stations generally land on one grid. The appendix row, the
  `*_applied_loads.csv` row and the `FORCE`/`MOMENT` card are now one object at
  one point.
- **`station_applied_loads` is the set before it is lumped**, and stays public:
  the calc's own distribution at the load-integration stations, which is both
  the aggregation's input and the reference curve of the VMT comparison.
- **`project` is now required** by `applied_loads` and `applied_load_csv` — the
  beam is built from it, and a caller without one cannot be handed the delivered
  set. Ask for `station_applied_loads` by name when that is what you want.
- **The resultant is unchanged and gated; the distribution is not.** LM-1
  preserves each load's resultant about every reference exactly, per component
  and per case. What moves is where the set says a load is carried — a real
  discretization difference, which the report will state as a VMT comparison.
  One consequence is visible today: a moment component that is zero at a station
  is generally **not** zero at a grid, because moving a force across an offset
  makes a couple. The applied appendices say so.

- **The assembled full-span deck stops being a shipped artifact (note 56 D-56.8,
  tier L, 2026-09-12).** Four surfaces retire in one change: the Balanced Cases
  page's stamped download, the Export & Report page's row, the `.bdf` inside the
  bundle `.zip`, and `cli.py --export-target balanced`. The report's Appendix A
  manifest loses its row with them — a controlling document naming a file the
  reader was never given is review F-D2's defect pointing the other way.
  `EXPORT_TARGETS` goes 4 → **3**: `gear` stays because D-56.1 reclassified the
  gear interface report as a *document* and this is its only headless route.
- **What ships in its place already did.** The **LRA beam model** carries the
  same assembled cases, transferred onto the beam's own grids, free-free, one
  `SUBCASE` per case — so nothing left the deliverable, one of two files
  carrying the same load sets did.
  `tests/test_cli.py::test_the_beam_deck_is_reachable_headless` is review F-D1's
  gate moved to follow the artifact rather than retired with the file it was
  first written about.
- **One stale manifest description swept with it (rule 4).** The mass model's
  row still said "for splicing into a model that already has nodes" — untrue
  since D-56.6 gave every `CONM2` its own `GRID` at its own CG. It now states
  what the file is and what splicing it costs: an `RBE2` per mass.
- **`balanced_deck` stays, as a genuine internal producer.** Its text is the
  un-aggregated load set at each load's true position, and its resultant is what
  the transferred set is gated against (`test_the_transferred_set_has_the_
  balanced_decks_resultant`). Deleting it would have deleted the reference the
  deliverable is checked against.

- **The boundary-derived seam is marked in the tail input blocks (#25 step 1,
  note 54 D-54.1, tier M, 2026-09-10).** The planform-geometry scalars the
  boundary-line model will derive — every area, span, MAC, MAC station and
  aspect ratio (9 of the h-tail block's 17 fields, 10 of the v-tail's 15, the
  wing-sourced `ARW` and `B` included) — are named in the new machine-readable
  maps `models.inputs.HTAIL_BOUNDARY_DERIVED` / `VTAIL_BOUNDARY_DERIVED`
  (`{field: deriving surface}`), which step 2's derivation consumes, and each
  carries a `[D]` mark that travels into the generated `DATA_DICTIONARY.md`;
  the aero, control-setting and mass/inertia fields are the stated remainder,
  and `vtail_root_waterline_z` is called out as placement (the L-1 owner's
  field), not planform. Field order is untouched — it is a persisted shape
  (`test_schema_guards.fields_hash`), so the physical regrouping rides step
  2's own schema bump rather than spending a version hop on cosmetics. No
  behavior change: every scalar stays entered and oracle-authoritative until
  step 2. Guard: `tests/test_empennage.py::
  test_the_boundary_derived_marking_partitions_the_tail_blocks` — every field
  of both blocks must declare its side of the seam.

- **The boundary-line model: entered lines derive the tail scalars (#25 step 2,
  note 54 D-54.1/D-54.8, tier L, schema v65, 2026-09-10).** The tail group's
  geometry is now entered as its **five boundary lines** — tail LE, tail TE and
  control LE (the `geometry.surfaces` polylines), the control's new
  `hinge_line` (v65), and the control's TE, which **is the parent's** along the
  interior of its span and therefore derives instead of being entered a second
  time (`tail_geometry.derived_control_trailing_edge`; an entered copy is held
  on the parent's line by `validate_control_trailing_edge`, hard on the tail
  groups — the wing controls join at the #260/D-54.6 fixture wave, whose
  estimated aileron polylines sit up to 9.4 in off their wing TE today). Every
  `[D]`-marked scalar of the two tail blocks (`HTAIL_BOUNDARY_DERIVED` /
  `VTAIL_BOUNDARY_DERIVED`, the #25 step 1 seam) **blank-derives** from the
  lines through `tail_geometry.boundary_derived_scalars`, consumed by
  `select.effective_tail_inputs`/`effective_vtail_inputs` and by
  `resolve_tail_planform` (note 36 OV-1: typed overrides, blank derives); the
  hinge halves SEFWDHL/SEAFTHL and SRFWDHL/SRAFTHL derive from the hinge
  line's area split (`control_hinge_areas`). A typed scalar stays
  authoritative — every Appendix A pin is untouched, `ga6_normal`'s
  elevator/rudder TEs are removed from the fixture because the derivation
  reproduces the printed tables byte-for-byte, and the Imperial digests did
  not move. Appendix A's printed h-tail/elevator/rudder figures are now
  **±0.1 % predictions** of the model (page-cited gate in
  `tests/test_tail_geometry.py`), and `validate_tail_planform` compares
  entered scalars only, retiring field-by-field as they stop being typed.
  `LayoutInput.htail_dihedral_deg` (D-54.8) is **declared, not modelled**: no
  load reads it (guarded) until note 51's dihedral guard and method spend it.
  The two tail input blocks are physically regrouped into the seam order with
  this bump — the regrouping step 1 deferred to the change that earned the
  version hop; the 64→65 migration is an identity.

- **The certification-basis / case-coverage matrix leaves the ranked backlog
  (#47 closed not-planned, tier S, 2026-09-11).** Owner ruling from the
  2026-09-10 scope-reduction review: the matrix is a DER-package feature off
  the mission bar (loads → sbeam + oracle report), so band C's row moves to
  `02_parked.md` as off-mission with its body preserved on the closed issue.
  Activation is stated — the methods-manual/DER-package direction, or before
  the next FAR 25 case build, design note first. Decided, not built.

- **The load-output contract's statements get one owner, and eight copies of the
  solver unit set collapse to it (note 56 D-56.1, tier M, 2026-09-10).**
  `export/deck_format.py` — the card-writing primitives module #15 created for
  exactly this defect class — now also owns *what a load is stated to be*:
  `solver_units`, `basis_sentence`, `load_label`, `ult_label`, `case_sf` and
  `SUITE_SF`, promoted out of `sbeam_bridge`'s underscore namespace under the
  names the writers actually mean. The authority for *which* factor a case
  carries is unchanged — `safety_factors.py` (M4-8 / G-11) decides, these only
  render it.

  `deliverable_units(system, Channel.SOLVER)` — the choice of which unit set a
  deck may be written in — had been copied into a private `_units` helper in
  **four** export modules (`sbeam_bridge`, `balanced_deck`, `roundtrip`,
  `lra_model`) and written inline in **four** more (`mass_cards` ×4,
  `lra_import`, `workbook`, `coordinates`). All eight now read one owner, and
  `tests/test_deliverable_units.py::test_only_deck_format_resolves_the_solver_channel_in_the_export_package`
  fails the day a ninth appears (rule 3: the owner *and* the drift guard).

  **Found while doing it: the rename would have silently blinded G-OR-71.**
  `tests/test_limit_channel.py` scans the whole tree for a surviving
  limit→ultimate multiply, and its pattern matched `* _sf(` and `\bsf\b` — but
  `\bsf\b` does **not** match inside `case_sf`, because `_` is a word character
  and there is no boundary before `sf`. A text guard that matches nothing still
  passes, so nothing in the suite would have gone red. The pattern now names
  `case_sf` explicitly, including its dotted form, with three teeth assertions
  and the reason recorded in the source.

  No delivered byte changes: the Imperial digest's 330 channels are identical,
  and the whole suite is green.

- **The deck-writing primitives get their own module (CH-4, #15, tier S, 2026-09-09).**
  `sloads/export/deck_format.py` is now the single owner of *how a bulk-data card is
  written* — the NASTRAN number format (`fmt`), the vector-card triple with its dust
  snapping (`fmt3`, `snap_zero`, `CARD_TOL`), the `SF` spelling (`sf_str`), the 72-column
  `$` comment wrap (`comment`), the `$`-block stamp (`stamped`) and the placeholder
  `MAT1`/`PBAR` section properties a determinate stick model needs to be solvable. Five
  sibling writers — `mass_cards`, `balanced_deck`, `lra_model`, `lra_import`, `roundtrip`
  — reached across the package for these through `sbeam_bridge`'s underscore; a private
  imported from another module is not private, it is an undeclared API whose every rename
  is a silent breakage. The names are public at their new owner and the cross-imports are
  gone. Pure move: no deck byte, CSV cell or printed figure changes, and the oracle,
  closure and frozen-Imperial-digest suites are unmoved. `CONVENTIONS.md` §7's
  platform-stable-bytes row and `PROJECT_GUIDE.md` §4 name the new owner.
  `test_platform_stability.py`'s emitted-value sweep now patches the formatter at **every**
  binding rather than at one module's — with the primitive outside `sbeam_bridge`, the old
  single patch would have shrunk a 159,407-value population sweep to one file's cards
  without failing.

- **The export package closes on one solver artifact (design note 56, #263, tier L, 2026-09-12).**
  The tier-L closure of a ten-slice change. `sloads/export/` goes from **8,603
  lines across 15 modules to 5,307**; four parallel model concepts become two;
  `cli.EXPORT_TARGETS` goes from ten targets to three (`lra`, `gear`, `mass`).
  What ships to a solver is the **LRA beam model** of the whole free-free
  airplane, plus the **CONM2 mass model**. The five per-component decks are
  deleted, the elementless assembled deck no longer leaves the tool, and
  `sbeam_bridge.py` — which the oracle report reached into at seven sites — no
  longer exists: the applied-load model and the deliverable tables that were
  never decks are `report/applied.py` and `report/tables.py`.

  This entry closes the sweep rather than the code. `CONVENTIONS.md` §7 gains a
  row for D-56.3 (every `GRID` in a deliverable comes from one contiguous band
  that deliverable owns) and re-cuts the joint-register and
  skeleton-solvability rows — the latter named `JOINT_MERGE_FRACTION`, retired
  at D-56.4, and the floor that replaced it guards a different thing. Two §1
  conventions are **retired in place**, struck and explained rather than
  deleted: "a load that a free-body cut introduces is never applied in the
  assembled model" and E-2's per-component moment reference, both of which
  argued about artifacts that no longer exist. `PROGRAM_SPEC.md`'s artifact
  statement and its D-R5 bullet are re-cut — D-R5 named a guard deleted with
  the wing deck, and the rule it protected now holds by construction, one
  producer with every consumer a view of it. `PROJECT_GUIDE.md`'s
  frozen-baseline paragraph loses four wrong facts in one clause and gains one
  that was never stated: the Imperial baseline digests one **non**-deliverable,
  the assembled deck, because gate 13 checks the beam model's re-aggregated
  load set against its resultant. `docs/20_theory/ch11_export_sbeam.md` is
  swept under rule 4 — its two validation tables are kept as the record of
  gates written against retired artifacts, each saying what it now applies to.

- **The LRA beam gets its own mesh, decided from geometry (note 56 D-56.4,
  tier L, 2026-09-11).** The beam *was* the load mesh: the wing chain was the
  WINGGEOM strips outboard of the side of body and the tail chains were the
  spanwise load stations. So the spanwise half of the LM-1 transfer was an
  **identity on every CI fixture**, and the arbitrary-grid routing a real user
  hits first was the least-covered path in the package — a degenerate special
  case hiding the general one. It also made one mesh serve two contracts: the
  strip count the replication oracle freezes at 20 was also, silently, the
  structural model.

  Each member's node set is now its own two **ends**, the joint register's
  owned locations on it, and `n` grids laid at equal spacing *between*
  consecutive owned points. `n` is per component and settable —
  `Project.lra_mesh` (**schema v66**, identity hop from v65) — defaulting to
  **wing 20 per side, fuselage 12 per cantilever, h-tail 12 per side, fin 10**.
  Blank means the default and every bundled example is blank. The WINGGEOM
  strips stay oracle-locked at 20 and simply stop being the beam.

  **A member runs to its own tip.** The wing chain used to stop at the
  outermost strip *midpoint* — 5.0 in inboard of the tip on `ga6_normal`
  (2.5 % of semispan), 12.1 in on `atr42_100`. That is the omission design note
  54 D-54.5 fixed for the fin, where it only got fixed because the T-tail tie
  made the tip a joint; with no tie to force the issue on the wing it survived.

  **The sliver class dies structurally.** Nothing is inserted any more, so a
  joint cannot land a percent of a strip from a station: the owned points come
  first and the grids are strictly interior to the segments between them.
  `JOINT_MERGE_FRACTION` retires. What replaces it is narrower and means
  something different — `_MIN_ELEMENT_FRACTION`, 1:200 of a member's target
  element length, catching two **owned** locations genuinely that close in the
  entered geometry, which is a data condition and gets a message that names the
  two points rather than asking for a bug report.

  Three gates land: no member can carry a sliver (by construction, on every
  member rather than the two tail chains the merge band covered); **the mesh is
  load-blind** — no chain node sits on a load station, and changing a grid
  count moves no delivered resultant; and a count below 2 is refused by name.
  Only `sbeam/lra_model` re-stamps — four channels. Every other deliverable is
  byte-identical and the round-trip solve gate passes unchanged.

- **The LRA model owns every grid it writes (note 56 D-56.3, tier M,
  2026-09-11).** The one shipped solver artifact took its right-wing station
  ids from the deleted wing stick deck's band, its two tail chains from the
  deleted spanwise decks', its hinge and actuator nodes from the deleted
  chordwise decks' and its gear nodes from the balanced deck's — four artifacts
  numbering the grids of the one that ships, three of them not deliverables and
  two of them gone. The model now allocates from **its own contiguous run,
  `20001–30999`**, one 999-wide sub-band per node family in a fixed order, so
  `gid // 1000 - 20` is the family index and a grid id read off a deck or a
  solver echo says what kind of point it is without a lookup. `sob_gid` moves
  to `lra_model` with it — one consumer, and this was it.

  Eleven bands replace six; the old `7001–7880` run and the borrowed ranges are
  left **unregistered rather than reused**, as D-56.2's retirements were. The
  bands still registered below the retirement line belong to the **applied-load
  model**, which keeps its own station numbering until D-56.9 re-states it at
  the LRA grids — so `bands.py`'s collapse to ~8 completes there, not here.

  Two gates land with it: **every LRA grid comes from the LRA's own band**,
  asserted from the emitted deck text on four fixtures (note 56 gate 4), and
  **no GID is defined at two positions across the shipped decks** (gate 3). One
  latent alias goes with the renumber: the fin tip and the h-tail's left
  attachment shared attachment index 2, safe only because a T-tail has no left
  attachment.

  Only `sbeam/lra_model` re-stamps — four digest channels, one per fixture with
  an LRA deck. Every applied-load CSV, the balanced deck, the mass deck and
  both reports are byte-identical, and the round-trip solve gate passes with
  its two known SI xfails unchanged.

- **Every `CONM2` sits on its own `GRID` at its own item's CG (note 56 D-56.6,
  tier M, 2026-09-12).** A mass card used to hang on the nearest fuselage beam
  station and carry `x1/x2/x3` back to the item's true position. It now has a
  grid of its own, at that position, with a **zero** offset — so the mass model
  is self-contained and states no attachment it does not have. The wing-item
  limitation retires with it: a wing mass is at the wing mass's position, not on
  a fuselage node with a caption explaining why.
- **The grids are unconnected by design, and the deck says so.** sloads ships no
  tie, so a stiffness solve over the mass model is singular. The header names the
  condition, the reason, and the remedy (an `RBE2` per grid) rather than letting
  a reader discover it by running one. The placeholder massless beam and its
  `SPC1` are deleted — nothing is left for them to support.
- **The mass model is checked by a grid-point weight recovery, not by a solve**
  (D-56.7). `inertia_only_cards`, `case_station_weights` and
  `roundtrip.flatten_mass_case` are retired: they cross-checked sloads' reduction
  of a mass to a beam station, and there is no reduction left. sbeam's GPWG reads
  mass and CG off the deck **as shipped**, per payload case, in both unit
  systems. `--export-conm2` and the bundle now write two files, not three.

- **The development plan re-cuts into three milestones: 0.8.3 closes the export
  contract, 0.8.4 converges the front-ends, 0.8.5 cleans up (backlog re-cut,
  tier S, 2026-09-11).** 0.8.3's named deliverable — the T-tail empennage
  geometry model — shipped with #25, leaving one L-tier note in flight (#263,
  note 56) behind a 21-row defect-and-polish tail, while note 57 sat **AGREED**
  and gated on "the 0.8.3 cut". Band **B4** is now #263 plus the rows that close
  with it (#173, #176) and #16 as note 56's pre-clean; band **B5** keeps note
  57's D-57.8 sequence with **#241, #242 and #245 inserted before #270** —
  #245's `data/` is the successor channel note 57 §1.3 names for
  `export_report`, so the retirement cannot precede it — and #255 closing
  superseded at #270; new band **B6** (milestone **0.8.5**) carries the
  remaining eighteen, landed once against one front-end. Band **B2** is
  re-chartered to calc, report and process work: the "main sloads GUI
  development" it was named for retires with #270. The whole table is
  renumbered densely (Pri 1–57) and the superseded preambles roll to
  `90_record/44_backlog_state_narrative_to_2026-08-29.md`.

  Two costs are booked rather than discovered: the baseline wave splits
  (#241/#242 move to 0.8.4, so digests regenerate twice — both are column
  additions to files the wave already rewrites), and **#179/#180 are deferred
  as latent**, not as polish — #179's first-match hole has no current producer
  and #180's `getattr` fallbacks are dead defaults, so rule 6 permits the
  deferral, and it is named here so it is a decision. The efficiency claim is
  stated narrowly because it was measured: the convergence avoids **one**
  tier-S row of duplicated effort (#255); `format_value` has zero `app/` call
  sites, #243/#177/#239 are on the survivor, and D-56.2's seven `app/views/`
  consumers were already paid.

- **The backlog is re-scoped onto the package note 56 left behind (tier S, 2026-09-12).**
  Seven surviving rows carried note 56 as a *forecast*; each now states what
  landed. #241's `AppliedLoad` fix has an address (`report/applied.py`) and the
  six `*_applied_loads.csv` files are the only applied-load CSVs left; #242
  narrows to the report's own files, with the control-surface `Fz` question
  surviving as rows *inside* the h-tail and fin files rather than as a file;
  #209's case index landed at `report/tables.py`, so its decision now touches
  three owners (`load_cases_to_rows`, `load_cases_csv`, the index itself);
  #191 loses the `sbeam_bridge.py` half and re-measures its candidates
  (`balance.py` 2,842, `report/content.py` 2,625, the new `report/applied.py`
  1,561); #254 and #245 restate their narrowings as landed. **#17's forecast was
  wrong in one half and says so**: `_export_sbeam` was not deleted with the
  per-component targets — it lost its branches and stands at 53, off the list —
  and `_manifest_rows` measures 131, not the 155 the row carried.

- **Three findings owed since note 56 are filed, and band B4 re-opens for one of
  them (tier S, 2026-09-12).** #274: the oracle report's balanced-cases
  paragraph and the Balanced Cases page still call the assembled model the
  primary deliverable and the per-component decks its analysis views, and the
  wing-root note attributes the `lra-sob` reporting node to the deleted wing
  stick deck — three false statements in shipped content, which the ordering
  rules put above every [V] item, so 0.8.3 does not cut over them. #275: the LRA
  mesh guarantees no fuselage owned point at the spar carry-through, and
  Appendix G measures the cost (fuselage shear 82–197 % of the channel's own
  peak; a ~107,000 lb reaction one bay from where it acts on
  `concept_regional_jet`). #276: `WeightEstimationInput.engines` is a count
  where `Project.engines` is a list, invisible to the units walker's totality
  gate and pinned meanwhile in `_KNOWN_AMBIGUOUS`.

- **The deliverable tables that are not decks move to `report/` (note 56 D-56.1,
  tier M, 2026-09-10).** The case index, the governing safety-factor table, the
  gear interface report and the export-scope filter they share are now
  `sloads/report/tables.py` (409 lines). None of them emits bulk data or knows
  what a GRID is — they are documents, and `report/` is where documents are
  assembled, which is why `report/content.py` and the oracle sections were
  already reaching back across the package to import them.

  Every row, column, header and byte is unchanged; the frozen Imperial digest is
  the proof. `sbeam_bridge.py` drops 3,013 → **2,639** lines.

  **The export package no longer re-exports them**, and a guard asserts it does
  not: a re-export would leave one name at two addresses, which is the condition
  D-56.1 exists to end. `sloads.export.__init__`'s docstring says where they went
  instead. Consumers re-pointed: `report/content.py`, `cli.py`, the Export page
  and the Landing-loads page.

  Two allowlists keyed on the old path were corrected — `test_envelope_owner`'s
  `_ALLOWED` (the reason belongs to the table, not to the bridge) and
  `test_ultimate_contract`'s `_ULT_CHANNEL`, which reads download-call text and
  would have passed silently on a page whose call had moved to a new alias. That
  is the second text guard this note has caught keyed to a name it was about to
  lose, after G-OR-71 in the previous slice.

- **The plane a surface is defined in has one owner (#220, tier S,
  2026-09-09).** Design note 54 D-54.2: whether a surface's span coordinate is
  a butt line (wing, h-tail, their controls) or a waterline (fin, rudder) is
  now answered once, by `sloads.tail_geometry.surface_plane` returning
  `SurfacePlane`, replacing the five per-call-site name tests — the four
  local→airplane maps in `export/coordinates.py` and the three-view's
  mirror/view branch in `modules/configuration.py` (its private
  `_WATERLINE_SPAN_SURFACES` tuple removed). Docstrings that claimed the
  second polyline coordinate is a butt line (`XYPoint`, `SurfaceInput`,
  `wing_geometry.interp_x`) corrected. New guards tie the coordinate maps and
  the report's declared frame/span-axis data back to the owner; `CONVENTIONS.md`
  §7 gains the SSOT row. No user-selected plane field yet (deferred with
  V-tail/cruciform support, note 54 §8). No load, deck byte, or delivered
  file changes.

- **The theory documentation becomes a chaptered manual (tier S, 2026-09-10).**
  `docs/20_theory/` is restructured for an engineer reader: eleven `chNN_`
  chapters on one template (scope, cases analyzed, method, assumptions &
  limitations, worked example, validation, sources) beside the slimmed hub
  `00_theory_sources.md` (sources, oracle status, citation rules, provenance
  policy, per-module citations, chapter map). New chapters: introduction
  (ch01, incl. the two front-ends and the no-physics-in-front-ends
  invariant), illustrated conventions (ch02, four script-generated SVG
  figures — `scripts/render_theory_figures.py`, new), wing (ch04), empennage
  incl. one-engine-out (ch05), fuselage (ch06), ground (ch08) and mass model
  (ch10) — the last four as stubs with assumptions and validation populated
  first. Renames: `design_airspeeds.md` → `ch03_airspeeds_envelope.md`
  (+ a new V-n envelope / case-inventory section), `engine_loads.md` →
  `ch07_engine_loads.md`, `balanced_cases.md` → `ch09_balanced_airplane.md`
  (+ §11, the closure-gate record). The hub's concept-mode closure
  narratives moved into the chapters' validation sections with a pointer map
  left behind; `01_far25_gap_analysis.md` relocated to
  `docs/30_future/04_far25_gap_analysis.md` (a plan, not theory). Link sweep
  across `PROGRAM_SPEC.md`, the corrections register, `30_future/` notes,
  two test comments and `00_INDEX.md`; historic documents (`40_history/`,
  `50_reviews/`, `CHANGELOG.md`) keep the names of their day.

- **Down-select on the ultimate basis; deliver LIMIT (#193, note 58, tier M,
  2026-09-11).** Comparisons *between* load cases — governing-case picks and
  cross-case envelopes — now key on `safety_factors.ultimate_basis`
  (`|value| × prescribed SF`, the quantity structure is sized to), while every
  delivered load stays LIMIT with the factor stated and applied nowhere: note
  49 OR-116 is confirmed by explicit ruling and #193's deliver-at-ULTIMATE
  half closes **decided, not done**. A full sweep found exactly one
  mixed-factor reduction in the suite — the Loads Plots pointwise envelope
  over the fin's chordwise set, SF 1.0 OEI curves against SF 1.5 SELECT
  curves on raw LIMIT magnitude — and `report.envelope_extremes` now takes
  the per-series factors and **refuses a mixed selection by name**
  (`safety_factors.uniform_factor` owns "same basis"); the page draws the
  per-case curves and states the withholding in band. G-OR-113 re-keys to the
  ultimate basis with the pin that no shipped pick flips (the governing VD
  case leads by ~2.2× on both twins). No delivered byte moves; `CONVENTIONS.md`
  §7 carries the owner row. The set-membership defect the sweep found (the
  summary report's v-tail governing table omits the OEI rows its chordwise
  table carries) is filed as #272, not folded in.

- **One surface, one name: `fin_*` identifiers retired for `vtail_*` (#223,
  tier S, 2026-09-09).** The mechanical sweep of the 2026-09-06 ruling
  (`CONVENTIONS.md` §7.2): every production identifier spelling the vertical
  tail "fin" — `fin_root`, `fin_root_waterline`, `FinRoot`, `FinCase`,
  `fin_sets`, `fin_load`, `ATTACH_FIN_TIP` and their kin — renamed to the
  `vtail` token across `sloads/`, the front-ends and the tests, first in the
  tail-geometry cluster so #219/#220/#54-series edits land on the agreed
  names. Serialized names are deliberately kept (`cy_beta_fin`/`cn_beta_fin`
  schema fields; the `balanced_fin_load`/`fin_angle_of_attack` LoadValue keys
  — renaming those is a schema/baseline change, not a spelling fix), prose may
  still say "fin", and the guard
  `tests/test_tail_geometry.py::test_no_fin_identifier_survives_or_returns`
  walks every production identifier so the seam cannot reopen. No load, deck
  byte, or delivered file changes.

### Fixed

- **#273 takes its row and the priority table is dense again (backlog hygiene,
  tier S, 2026-09-11).** The #16 sweep's residue was filed against milestone
  0.8.5 with a `band:` label and no row, which `scripts/backlog_issues.py check`
  refuses — and rightly: a banded issue outside the table is work with no place
  in the single order. It enters **band B6** at the hygiene front, where its two
  halves belong together: `io.py` and `report/oracle_package.py` each declare
  their own constants for `report.json` and `build.json` (two owners for one
  filename, the class practice 3 exists to prevent), and
  `gear_loads.LEG_WEIGHT_UNSET_NOTE` is public, in `__all__` and read by nothing,
  so a leg with no entered weight shows an OPEN free body with the explanation
  written and unrendered. The table renumbers densely 1–57, closing the gap the
  2026-09-11 re-cut left at Pri 4 when #16 closed. One stale ordinal goes with
  it: #191's `after #15 (Pri 14)` — a doubled reference that survived the re-cut
  pointing at neither the issue nor the row it meant — now reads `after #186 at
  the hygiene front`, named by issue so the next re-cut cannot strand it.

- **The open-defects index loses two wrong issue numbers, a deleted body and
  three closed entries (backlog hygiene, tier S, 2026-09-11).** The 2026-09-08
  index tidy (`07b24e2`) collapsed the *Open defects* bodies to one-line
  `#N — title` stubs and assigned the numbers positionally, which mis-stapled
  two: **"No engine-mount case reaches the LRA deck"** — an unfiled 2026-09-07
  finding with a full body — became `#209`, which is the load-case index's
  blank-load-columns defect, and its body was deleted; **"Review 2026-09-04
  small items"** became `#16`, which is Dead code (CH-5), now a 0.8.3 row. The
  engine-mount body is restored verbatim with the number struck and the gap
  re-verified live (the `lra-engine` band still allocates grids at
  `bands.py:274`; `transferred_case_loads` still takes a `BalancedCaseResult`,
  so no 23.361/23.363/23.371(b) condition reaches the deck); the small-items
  entry is deleted as redundant — all six are rowed (#175, #176, #179, #180,
  #188) or closed (#178). Three closed entries leave under the removal rule:
  **#170** (with the stale `Pri 49` ordinal the rows-never-cite-ordinals rule
  bars), **#181** and **#182**, whose "close on GitHub" instruction is
  discharged. Notes 56 and 57 lose their stale band/ordinal citations
  (`band B4 Pri 29` → `band B4`; `#255 in band B4` → band B5).

- **`baron_58` joins the Imperial output baseline — and every EXAMPLES-driven
  sweep — and the baseline's example list becomes structural (#271, tier S,
  2026-09-11).** The D-21 guard's hand-kept `EXAMPLES` tuple claimed "every
  shipped example" but was never extended when `baron_58` shipped, so the
  closure-locked twin's delivered bytes — 54 channels, more than any pinned
  fixture — had no byte-level drift guard; and since six other suites use
  `EXAMPLES` as *the* fixture walk, baron was also absent from the pinned
  assembly, ground-case, lateral, Izz, dCD, payload-derivability, couple-node
  and tail-coverage sweeps. All are now pinned from measurement (its SIDE
  GUST and wing families drop on non-derivable loadings, recorded per F-C7;
  the lateral pin's full-set assert relaxes to legality with the exact set
  per fixture), the digest fixture is regenerated additively (every existing
  digest byte-identical), and the prose claim gets its rule-3 drift guard:
  `test_deliverable_units.py::test_the_baseline_pins_every_bundled_example`
  ties `EXAMPLES` to the `examples/` directory, so a fixture added or removed
  without a deliberate regeneration fails loudly. Found while retiring two
  fixtures at #264.

- **The conventional h-tail no longer sits on the wing-root waterline (#261,
  design note 54 D-54.4, tier M, 2026-09-10).** `tail_geometry.h_tail_waterline`
  is completed: a conventional tail with no entered `h_tail_z` now takes the
  h-tail **mass items' weight-weighted `z`** (ASSUMED, basis `mass-item`)
  before falling back to the wing-root plane, now loud and last — an entered
  statement of where the surface's mass sits beats a placeholder printed as an
  airplane coordinate. And the **two-spellings rule**: a declared T-tail whose
  entered `h_tail_z` contradicts the fin tip by more than `PLANFORM_TOLERANCE`
  of the fin span gets the fin tip *and an in-band note naming the entered
  value NOT USED* (the #260 E5 pattern made loud). Swept per rule 4: the
  three-view sketch (`configuration.tail_planform`) now reads the owner with
  the project in hand instead of its own entered-else-wing-root copy, and the
  report's provenance sentences gain the mass-item and NOT-USED branches.
  **Delivered coordinates move**: `cessna_210`'s h-tail rises 86.0 → 100.0 in
  and `concept_heavy`'s drops 100.0 → 90.0 in (station points and exported
  `GRID`s only — the h-tail loads in `fz`, so no load moves); the Imperial
  baseline re-froze `cessna_210`'s three deck channels. Both moves are the
  note 54 gate-3 fixes, pinned in `tests/test_tail_geometry.py`.

- **The joint register: a joint is an owned location, a stated arm, a DOF set
  and a basis (#262, note 54 D-54.5/D-54.7, tier L, 2026-09-10).** Every
  inter-component tie in the LRA beam model now has its nodes placed by one
  owner, `sloads/joints.py` — the fin root→fuselage tie, the T-tail
  fin-tip↔h-tail-centreline pair, the conventional attachment pair, the wing
  side of body and the two spar posts. `joints(project)` resolves nothing
  itself: it reads the owners that already resolve each position
  (`tail_geometry`'s fin root and `h_tail_waterline`, `tail_span.htail_attachment`,
  `derived_geometry`'s `sob_station`/`carry_through`/`fuselage_lra`) and copies
  their location, ASSUMED/entered grade, basis and in-band note **verbatim**;
  `export/lra_model` places its nodes and raises its refusals by reading the
  register, so the two ends of a rigid tie can no longer be two spellings of one
  formula. **This corrects real geometry.** The R-6 tie hung the horizontal tail
  off the outermost fin *strip midpoint* rather than the fin tip: measured
  against the planform owners it spanned −23.228/−23.753/−20.876 in of x where
  the surfaces state −25.600/−26.100/−26.680 (5.80 in, −22 %, on
  `concept_regional_jet`), plus 6.25/6.5/6.9 in of `z` the airplane does not
  have — the arms note 51's D-51.2/D-51.3 transfer moments are computed across.
  The fin chain now runs **root → strips → tip** (`lra-fin-tip`), and the h-tail
  centreline and conventional attachment nodes are placed at their own LRA
  stations instead of being interpolated off the strip polyline (which put
  `ga6_normal`'s attachment pair 0.356 in off the body station it reacts
  against). D-54.7's drift guard (`tests/test_joints.py`) walks every joint of
  every fixture out of the **emitted deck text** and asserts the node is where
  the register put it, that a tie exists, that it constrains the stated DOF set,
  and that it spans the stated arm. No delivered load moves: of 330 baseline
  channels only `sbeam/lra_model` changed, on five of six fixtures, and the
  per-subcase deck resultant is unchanged (LM-1 preserves it wherever the nodes
  sit). Alongside it, `wing_geometry.chord_fraction_x` becomes the single owner
  of the chord-fraction line, which `TailPlanform.x_at` and
  `net_loads.to_loads_ref_axis` had each spelled out separately.

- **Every exported LRA deck solves, and the solve gate covers every fixture
  (#172, design note 55 D-55.1…D-55.6, tier L, 2026-09-10).** The mission claim
  is that the exported deck solves in sbeam with verified global equilibrium;
  it was demonstrated on two of six shipped fixtures, and the CLI exported the
  other four without a word. Three defects, all in **how a joint node joins the
  structure** — the sibling of note 54's *where a joint node sits*:
  **(1)** a body tie could parent on a node that was already an `RBE2`
  dependent, so `ga6_normal` stated `gear → rear-spar post → hub` as a chain of
  rigid elements, which sbeam refuses outright; the tie parent now takes the
  same not-already-a-dependent rule the support picker had carried since the
  model shipped. **(2)** A joint inserted near an existing strip station left a
  **sliver element** — `cessna_210`'s h-tail attachment landed 0.0769 in from a
  station (1.07 % of that chain's `ds`) for a 1638:1 element-length ratio and
  the singular solve the issue reported, with `baron_58` next at 0.1266 in /
  1.33 % and in no gate to say so. A station that close is now absorbed
  **into** the joint, which keeps the register's owned location (note 54
  D-54.5 is not negotiable) while the merged node keeps the station's `GID`, so
  its load routes there unchanged under LM-1. The governing tolerance is
  `JOINT_MERGE_FRACTION` — a fraction of the chain's own strip width, because
  "is this the same station" is a geometric question and had been answered by a
  1e-6 float-equality epsilon. **(3)** The support picker excluded `RBE2`
  dependents but not independents, although `roundtrip._supportable` applies
  both and documents why: `recover_reactions` never subtracts a load a rigid
  element transfers *onto* a constrained node, so it returns as reaction —
  measured at **569.49 lb** of Fx on `ga6_normal` against an applied set closing
  to 0.0002 lb. All three are now gated invariants, and a skeleton that still
  violates one is an `LraRefusal` naming it rather than a deck that dies in the
  user's solver. The solve gate widens from the two fixtures that passed to
  **every CLI-exportable fixture**: all six now solve in Imperial, with
  `concept_regional_jet` and `ga6_normal` remaining strict `xfail` in SI only on
  sbeam's pre-existing dense-path condition heuristic. No delivered load moves;
  `sbeam/lra_model` bytes move on `ga6_normal`, `baron_58` and `cessna_210`.

- **A machine rating in load units is no longer a load (#170, review R-8, tier M, 2026-09-09).**
  `units.is_load_unit` decided what a safety factor may be stated for by testing the
  **unit string alone**, so an engine's own torque rating read as a structural load:
  ENGLOADS published GA-6's mean takeoff torque as 554.4 ft-lb and the ULTIMATE channel
  stated it as 831.6, a number with no meaning — 14 CFR 23.303's factor belongs to the
  *design* torque the same condition publishes beside it, not to a powerplant rating.
  `units.NON_LOAD_QUANTITIES` is now the owner of that distinction, and the producer has
  the last word: `"mass"` (unchanged), plus `"characteristic"` for an engine rating and
  `"diagnostic"` for `balance`'s pre-closure residual. Five quantities across two modules
  leave the class — `mean_takeoff_torque` (23.361(a)(1) and the turboprop (a)(3)),
  `max_continuous_torque` (23.361(a)(2)), `max_accelerating_torque` (25.361(a)(3)(ii)),
  `balanced_residual_fz` and `balanced_residual_my` — each losing its `SF` cell and its
  `-ULT` eligibility while the `mx_mount_torque`, the gyroscopic couples and the applied
  loads of the same conditions keep both. The class was swept, not the filed row: review
  R-8 found it three rows wide on the engine side and two more in the balance residuals.
  No load value changes anywhere. `CONVENTIONS.md`'s "Loads only" rule names the
  vocabulary; guards in `tests/test_safety_factors.py` pin the discrimination both ways on
  every fixture, assert every key of the class is actually reached, reject a `quantity`
  hint outside the owner's vocabulary, and check the delivered row itself — the rating's
  `SF` cell empty, the mount torque's filled, in one condition.
  The frozen Imperial baseline was regenerated deliberately and moved in **6 of 330**
  digests — `csv/balance` on each example, the 176 pre-closure residual rows whose `SF`
  cell is now blank like the percentage rows beside them; the 104 applied-load rows of the
  same files keep `1.5`, and no deck, report or load-case CSV byte moved.

- **A raked fin root no longer kinks the loads reference axis (#219, design
  note 54 D-54.3, tier M, 2026-09-09).** Where a surface's edge polylines do
  not cover the same span, the chord keeps the closed-polygon clamp
  (`wing_geometry.planform_boundary` — the 8 % GA6 area over-read stands
  fixed), but a chord-fraction *line* — the LRA, the 25/50 % load points, the
  hinge — is now evaluated on the edges' own slopes (`TailPlanform.x_at`)
  instead of pointwise on the collapsing closure chord, which swung the GA6
  fin's LRA 33.5 in aft onto the trailing-edge root point over the last 5.5 in
  of span (Figure 24's kink). The GA6 fin axis is now one straight line root
  to tip (gate: slope constant to 1e-9); surfaces whose edges cover the same
  span are byte-unchanged. **Delivered numbers move on `ga6_normal` only**
  (the one raked fixture): the fin's load application stations in the raked
  region shift forward, so the lateral cases' yaw acceleration falls 0.6–2.9 %
  (p_dot ~0.1 % through the Ixz coupling) — fin loads and Ny bit-identical,
  the lever-arm-moved diagnostic — and the GA6 tail/balance CSVs and decks
  re-baseline with it. Rule-4 ride-alongs: `interp_x` extrapolates the
  *nearest* segment below range as its docstring always promised (it used the
  last segment's slope — the wrong end of the surface), and the dead clamped
  copy `tail_geometry._interp` is removed.

- **The shipped text stops naming the export package note 56 deleted (#274, tier
  S, 2026-09-12).** D-56.2 deleted the five per-component decks and D-56.8
  unshipped the assembled one, and the sweep that closed note 56 reached the
  standard docs but stopped short of the rendered strings — so the actively-used
  deliverable went on describing artifacts the package no longer builds. Seven
  statements a reader actually sees were false: the oracle report's §7 paragraph
  called the assembled model *"this deliverable's primary load output"* and the
  per-component decks *"analysis views cut out of this model"*; its wing-root
  note attributed the `lra-sob` tagged reporting node to *"the wing stick deck"*
  when `export/lra_model.py` writes that tag at GID 25001; its gear section and
  the Landing Loads page both sourced the reference-point reaction to *"the
  assembled deck"*; the Balanced Cases page repeated the first two claims in its
  caption; the Export page offered *"FORCE/MOMENT cards (and the wing stick
  model)"* and pointed the `MyyAxis` column at a span CSV that is gone; and the
  Configuration & Layout side-of-body help named the stick deck as the reporting
  node's consumer. Each is re-cut onto what the bundle carries — the LRA beam
  model as the solver artifact, the assembled set as the internal reference
  resultant its transfer is gated against — with the free-free equilibrium
  argument (G-OR-72) unchanged: it was always a claim about the model, never
  about which file it shipped in.

- **The same sweep runs through the deck's own header and the docstrings behind
  it (#274, tier S, 2026-09-12).** The LRA model's `$` header told its reader
  that *"the assembled balanced deck remains the equilibrium proof and the
  per-component decks the oracle views"* — text inside the one deck that ships —
  and its per-case and constraint comments sourced the residual to a deck no one
  receives; all three now name the model that carries them. Present-tense
  docstrings naming the deleted decks are corrected in `export/lra_model.py`,
  `export/bands.py`, `report/applied.py`, `report/tables.py`, `report/render.py`,
  `report/oracle_sections.py`, `modules/balance.py` (whose copy of the
  free-body-cut rule now points at `CONVENTIONS.md`, which retired it in place)
  and `app/views/loads_plots.py`. Only `sbeam/lra_model` moves in the Imperial
  baseline, on the four fixtures that build one, and only in `$` lines: every
  edit sits inside a `comment()` argument, which emits nothing else. **One thing
  is deliberately not fixed:** the case index still ships the headers
  `LOAD/SUBCASE (component)` and `LOAD/SUBCASE (assembled)`, naming two decks
  that no longer exist. Renaming them moves a shipped CSV header across three
  owners and is **#209**'s decision, not this sweep's, so `report/tables.py`
  states the mismatch where the columns are defined rather than leaving the next
  reader to infer it.

### Removed

- **Six dead public names leave `sloads/`, and a gate keeps the seventh from
  arriving (#16 / CH-5, tier S, 2026-09-11).** `balanced_deck.write_balanced_deck`,
  `mass_cards.write_conm2_fragment`, `mass_cards.write_mass_check_deck` and
  `mass_distribution.all_checks` — the four the 2026-08-16 scope review named,
  re-verified on this tree as definition-plus-`__all__` and nothing else — are
  deleted. Under rule 4 the sweep took the same class across the tree and found
  two more with no consumer *anywhere*: `report.tables.write_safety_factors_csv`,
  a fifth instance of the identical `write_X(project, path)`-wrapping-`X(project)`
  shape, orphaned when note 56 D-56.1 moved the report tables out of the export
  bridge, and `field_registry.paths_for_page`. New guard
  `tests/test_no_orphan_writers.py` fails when any `write_*` in `sloads/` has no
  caller in the calc package, either shell, the scripts, the CLI entry points or
  the suite — proven against a reintroduced orphan before it was removed.

  **The "demote the ~12 no-consumer public names" half does not ship, and the
  number is why.** Re-measured on this tree, `sloads/` carries **200** public
  top-level names with no consumer outside their own module, not twelve — and
  the review's own two examples have both evaporated: `gear_loads.contact_patch`
  gained an external consumer since 2026-08-16, and `sbeam_bridge.subcase_map`
  sits in the file note 56 D-56.1 dissolves, so demoting it is churn on a
  deletion. The 200 are dominated by module result dataclasses (`DesignSpeeds`,
  `MassCheck`, `Joint`) and single-source constant families whose members are
  public by declaration — the `MASS_EID_*` id bands, `WING_BAND_*`, and the
  encoded-but-dormant commuter tier that `GUI_design.md` documents as dormant
  and a blind sweep would have deleted. Demoting those would fight rule 3, not
  serve it. The mechanical part of the row shipped with a gate; the judgment
  part is closed **decided, not done**, with the measurement above as the record.

- **`cessna_210` and `dhc8_dash8` retire from the bundled example set (#264,
  tier M, 2026-09-11).** Owner ruling from the 2026-09-10 scope-reduction
  review: GA-single (`ga6_normal`), closure-locked-twin (`baron_58`) and
  ATR42-class (`atr42_100`) coverage is sufficient, with the two concept
  configurations kept; the two fixtures move to unmaintained parking outside
  the repository (recoverable from history at the `v0.8.2` tag). Full retire:
  both leave every CI matrix, parametrized fixture list, pinned baseline and
  sbeam digest (the Imperial baseline drops from six fixtures to four with
  **every surviving digest byte-identical**); fixture-specific tests re-pin to
  a surviving fixture or to a constructed case (the below-energy landing
  caution, the gear-carrier mistag guard, the no-balanced-case deck refusal);
  the GUI example listings, `README.md`, `GUI_USER_GUIDE.md`,
  `PROJECT_GUIDE.md` and `PROGRAM_SPEC.md` state the surviving five. The
  unfixable `cessna_210` engine/prop CG waterline defect (filed 2026-09-07,
  no printed page to correct it from) closes parked-with-fixture, and #216's
  `cessna_210` half goes with it.

- **The five per-component solver decks are deleted (note 56 D-56.2, tier L,
  2026-09-11).** The wing stick BDF and its span-load CSV, the fuselage FORCE
  deck with its span-load and fitting CSVs, the chordwise tail deck and CSV, the
  two spanwise empennage decks and CSVs, and the control-surface deck and CSV —
  every per-component structural model sloads shipped. They were four parallel
  model concepts sharing one ID space with the deliverable, none of them the
  deliverable, and the deliverable was borrowing its GIDs from them.

  **What ships is unchanged**: the full-span balanced free-free airplane deck,
  the LRA beam model, the CONM2 mass model, the gear interface report, the
  oracle report and the per-component **applied load sets** — the record of what
  is applied, where, for which case, at what factor, which is what every deleted
  deck was written from. `sbeam_bridge.py` 2,639 → **1,413** lines; `sloads/`
  and `tests/` together lose ~3,800.

  `EXPORT_TARGETS` goes **ten to four** — `balanced`, `gear`, `lra`, `mass` —
  and there is no default target any more (`wing` was the default because it was
  the first thing the bridge could write). The note's summary says two; `gear`
  survives because D-56.1 reclassified the gear report as a *document*, and
  `balanced` because demoting the balanced deck turns on whether `roundtrip.py`
  collapses, which is still open (note 56 §8). Dropping either on a count would
  remove a live deliverable ahead of its replacement.

  **Three standing limitations retire** rather than reword: `centerline-clamp`,
  `flight-only-body-deck` and `export-case-filter`. Each described a limitation
  of a per-component view and pointed the reader at the assembled deck, which is
  now the only view there is. Retiring a caveat is the one edit that can quietly
  widen a claim, so all three go in the same commit as the deletion, against the
  pinned key set in `tests/test_methods_stamp.py`.

  The GUI loses the per-page deck downloads on the wing, fuselage, aileron, flap
  and tab pages and ten rows from the Export page and the bundle manifest. The
  band registry retires `tail-chord-htail`, `tail-chord-vtail`,
  `control-surface` and the `stick-element` EID block, leaving their ranges
  **unregistered rather than reused** — a published map said what lived there,
  and D-56.3's renumber is where the holes close.

- **The round-trip stick-model wrapper retires with the last elementless deck
  (note 56 §8, tier L, 2026-09-12).** `sloads/export/roundtrip.py` 529 → **186**
  lines. `wrap_as_stick_model` read a deck's `GRID` cards and **invented** a tree
  of `CBAR`s, a `MAT1`/`PBAR` section, a determinate support and a case control,
  so that a load set on a node cloud could be handed to a linear static solve at
  all. D-56.2 deleted the per-component decks and D-56.8 unshipped the assembled
  one; the LRA beam model writes its own elements and its own support, so it goes
  to the solver exactly as it ships. Retired with the wrapper: `Support`,
  `Topology`, the property / element / constraint / case-control builders, the
  coincident-node collapse, the `roundtrip-rbe2` EID band and three wrapper unit
  tests. What is left is what was always the point — hand a deck to sbeam and
  read back what it says.
- **Two names moved to the owner that allocates them.** `_orientation` becomes
  `deck_format.orientation_vector`: `lra_model`, the one deck writer left, was
  importing a private name out of a test harness to build its bars. `SPC_SID`
  becomes `deck_format.SPC_SID` and both writers now read it — the harness held
  the constant while the two writers each spelled `1` into an f-string, so the
  band registry's declared owner was not the code that allocates the id.
