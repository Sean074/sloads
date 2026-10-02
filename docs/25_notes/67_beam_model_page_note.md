# The beam model reaches the GUI: the LRA drawn, the deck and the OEW mass set written (design note 67)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-10-01 — #283 with #244 riding (§11).** AGREED 2026-10-01 (owner, in session, under the solo profile — rule 1's working-alone branch). PROPOSED the same day; the owner ruled Q1–Q3 of §2.2 **as recommended**, so D-67.1…D-67.12 stand as written (§9). Drafted for band B9 row 9, **#283** (the
beam-model page), with row 10, **#244** (the grid row-counter), riding it as the
owner placed it on 2026-09-28. The six design questions of the 2026-10-01 review
were **ruled in session before drafting** (§2); this note writes them down as
decisions and asks only the residue (§2.2). Implementation is one tier-L step on
`dev/v0.8.8`, after this note is AGREED.

**Tier L.** A GUI page is added, a schema field is added (`MassItem.usable_fuel`,
v72 → v73), a new export target is added (`oew`), and note 57 D-57.6 is reopened.
**No delivered load moves.** No calc module, no load set and no shipped solver
digest changes. The one new artifact, the OEW mass set, is new bytes, not moved
bytes.

**Conventions:** `CONVENTIONS.md` §2 (the airplane axes the views are drawn in),
§3 (the deck is LIMIT, SF stated per case, applied nowhere; the stamp says so),
§7 (single owners: this note moves three owners out of the files that hold them
privately, the stamp, the picker and the drawing, and adds one, the OEW
partition). **Precedent:** note 24 R-1/R-7c/R-12 (the LRA model and its refusal
contract), note 27 LM-4 (refuse, never guess), note 44 OR-16/OR-22 (the Report
page is a non-step and the GUI's server is the user's own machine), note 56
D-56.4/D-56.6 and rulings 4/9/16 (the mesh is a settable input, the mass model
is unconnected and checked by GPWG), note 57 D-57.1/D-57.6 (the page set is
derived plus declared, and the export page retired without a port), note 60
D-60.1/D-60.4 (a figure is drawn on the page that produces it, and pre-run is
said), note 63 OV-1 (a row's meaning is a typed tag, never a name match).

## 1. Measurements (2026-10-01, at `dev/v0.8.8` after #312)

### 1.1 What reaches the deliverable today

- **The deck has one writer and one route.** `lra_model.write_lra_model_bdf`
  (`lra_model.py:1412`) is called only by `cli.py --export-sbeam <prefix> lra`
  (`cli.py:241`), which names the file `<prefix>.lra_model.bdf` and stamps it
  with `cli._stamps` (`cli.py:118`). The GUI has no route to it. Note 57
  D-57.6 retired `export_report` "without port", which took the only page that
  had one.
- **The stamp is CLI-private.** `_stamps` wraps
  `report.methods.bdf_comment_block` / `csv_comment_block` with the tool
  version and scope. A page that wrote the deck without it would mint a second
  stamp. A page that copied it would fork it. **Its docstring is stale:** "The
  BDF stamp is always ULTIMATE — a deck has no other basis" contradicts OR-116.
  The stamp text itself is LIMIT and is gated by G-OR-73. Only the prose is
  wrong.
- **The drawing has one owner, and it is outside the package.**
  `scripts/plot_lra_model.py` (301 lines) builds the model via
  `build_lra_model` and draws it in four matplotlib panels (iso, plan, side,
  front) with outlines draped at the chain waterlines (`collect_outlines`).
  It keeps a **private copy of the exporter's `_interp_chain`** (`_interp`,
  whose docstring admits it). It is tested by `tests/test_plot_lra_model.py`
  (4 tests). Note 64 §8 named #283 as its promotion.
- **The GUI's figure system draws nothing itself.** `sloads.report.figures`
  owns the catalogue (`FigureFamily`: key, title, `step`, `Stage`, builder).
  Each figure is a renderer-agnostic `PlotData` of 2-D `Series`.
  `app_shell.plots` renders them in plotly and `report/plots_tex` in TikZ.
  `FigureFamily.step` is an `oracle_steps()` key. Whether a figure keeps its
  aspect ratio is derived, not declared: `plots.is_to_scale` is true when
  **every** series is `closed`.
- **The folder picker is page-private.** `oracle_app/report.py`
  `_browse_block` holds the OS dialog (`export.directory_dialog`) and the
  in-app fallback browser (`report_package.location_anchors` / `list_subdirs`
  / `create_subdir` / `is_writable`). The TCC warning is in the same block.
  Gate G1 (`tests/test_oracle_gui.py`) forbids a page importing `os`, so
  every path question is answered in `sloads.export`.

### 1.2 The axis and the mesh: already editable

The backlog row's "no editor for `lra_mesh` or `ref_axis_pct` beyond raw JSON"
was true when it was written on 2026-09-14. It no longer is:

| Field | Page | Tier | Consumers |
|---|---|---|---|
| `geometry.surfaces[].ref_axis_pct` | `configuration_layout` | SUITE (`supplied=True`) | `net_loads` and `tail_span` torsion, `joints`, `lra_model` (refuses when unset, R-7c) |
| `lra_mesh.{wing,fuselage,htail,vtail}_grids` | `configuration_layout` | EXTENSION | `lra_model` only (D-56.4: it moves no resultant) |

`tests/test_field_registry.py::test_every_page_is_a_real_workflow_step` holds
every registry `page` to `wf.BY_KEY`, so a field cannot sit on a non-step page
today.

### 1.3 The mass model and "OEW"

- **`--export-conm2` writes the full mass model**
  (`mass_cards.conm2_fragment`). It has one `GRID` + `CONM2` per item at its
  own CG (D-56.6, unconnected by design). Its baseline is "always-aboard"
  (`kind != DISCRETIONARY`, i.e. EMPTY + MINIMUM). It also writes one
  `MASSSET` per derivable payload case, plus `mass_check_deck`.
- **"OEW" has no typed partition.** `WeightInput.database_totals` calls EMPTY
  the manufacturer's empty weight and says OEW "adds the MINIMUM crew". But
  MINIMUM is also where every fixture keeps its reserve fuel:

  | Fixture | MINIMUM rows (lb) | `consumable` |
  |---|---|---|
  | `ga6_normal` | Pilot 170; 30 min fuel 71 | all False |
  | `baron_58` | Unusable fuel & oil, left 45; right 45 | False |
  | `concept_heavy` | Pilot 200; Copilot 200; Reserve fuel 300 | all False |
  | `concept_regional_jet` | Crew (2) 400; Reserve fuel 1500 | all False |
  | `atr42_100` | Captain + First officer 400; Reserve fuel, left 350; right 350 | fuel True |

- **`consumable` cannot be the partition.** It marks what G-5 may *burn down*
  for a ground target, and its own docstring says G-4 must tell mission fuel
  from reserve. Reserve fuel is therefore deliberately non-consumable on four
  fixtures. Separating crew from fuel in MINIMUM today could only be done by
  matching row names, which OV-1 forbids.

### 1.4 The row counter (#244)

- **The counter is `oracle_app/form.py:1853`** (`render_table`): a bare
  `st.number_input(min_value=0, step=1)` with no upper bound and no
  confirmation. The backlog row's "the one `app_shell` owner" is wrong: the
  counter has never been in `app_shell`. Counting **down** already deletes
  nothing and asks for a named click. Counting **up** commits at once: one
  stray digit committed 4,501 rows (2026-09-08 GUI review G4).
- **The mesh counts are the same class in a different widget.** They are
  scalar `number_input`s through the registry, not row counters. A stray
  digit puts 4,501 grids on a wing, and the deck grows with it. Nothing
  bounds them (`lra_model` reads `project.lra_mesh or LraMeshInput()` and
  meshes what it is given).
- **Largest shipped list today:** 36 weight items (`baron_58`), 11 CG cases
  (`atr42_100`).

## 2. Owner rulings

### 2.1 Taken in session, 2026-10-01, before drafting

| Q | Question | Ruling |
|---|---|---|
| D1 | Step or non-step? | **A non-step page**, `NON_STEP_PAGES` row `beam_model` (option b). |
| D2 | Where the axis and mesh are edited | **(a)** `ref_axis_pct` stays on Geometry and is shown read-only, drawn and linked from the beam page. The `lra_mesh` counts **move** to the beam page. |
| D3 | The axis definition | **As it is:** a chord fraction per surface. No new axis form. |
| D4 | The drawing | **One `PlotData` owner in `sloads.report.figures`. The script retires.** |
| D5 | The mass model the page writes | **The OEW mass set: no payload and no fuel.** The fuel partition is a **typed tag** (option a of the follow-up). |
| D6 | #244 | **A cap, a confirmation on a large jump, and a re-seed from state**, in one owner, covering the row counter and the mesh counts. |

### 2.2 Asked at PROPOSED (all ruled as recommended 2026-10-01 — §9)

| Q | Question | Recommendation |
|---|---|---|
| Q1 | The tag's name and meaning | **`usable_fuel`, not `fuel`.** Unusable fuel and oil is part of the operating airplane and stays in OEW. A field named `fuel` that is False on a row called "Unusable fuel" says two things at once. `usable_fuel` says exactly what OEW excludes. |
| Q2 | #244's numbers | **Confirm any increase of more than 10 at once. Cap a list at 500 rows and a mesh count at 200 per member, with a floor of 2.** 10 is above every seed batch a user types by hand. 500 is 14× the largest shipped table. 200 is 10× the wing default and above any count the LM-1 transfer gains from. |
| Q3 | Does the CLI's `oew` target also write a GPWG check deck? | **No.** The OEW set is one mass state with no `MASSSET`. `mass_check_deck` covers the full model and gate 6 already reads it. The OEW set's own check is gate 7 below, an exact sum. |

## 3. Decisions

### The page

- **D-67.1 — The beam model is a non-step page.** A
  `NON_STEP_PAGES` row: `GuiPage("beam_model", "Beam Model", reason=…)`.
  - **The reason:** it is the deliverable built from the analysis, not a
    step of it. It runs no `.BAS` program and fills no slice the analysis
    reads.
  - **Position:** after Fleet and before Report, so the navigation reads
    analysis → deliverable → document.
  - **Renderer:** `oracle_app/beam_model.py`, added to `Oracle.py`'s
    `_RENDERERS`/`_TITLES`. That mapping is the drift the file is allowed to
    have.
  - **D-57.6 is reopened, not reversed.** The pages it retired stay retired.
    This is the missing route to the primary deliverable. D-57.6 had no such
    route to retire, because the retired export page wrote the per-component
    decks note 56 deleted.
  - **The schema's stale label is corrected.** The "step 12" comment
    (`project.py:243`) and the plot script's word for it are the last uses
    of that name.
- **D-67.2 — The page has four blocks, top to bottom.**
  1. **The axes.** Per surface: name, `ref_axis_pct` as a percentage, and
     whether it was entered. The fuselage LRA is shown as derived
     (`derived_geometry.fuselage_lra`). A link goes to Geometry. Nothing is
     editable here (D2).
  2. **The mesh.** The four `lra_mesh` counts through the form's own record
     renderer (`render_record`), so the Optional-record add/remove gesture
     (#143) and the EXTENSION mark come with them.
  3. **The drawing.** D-67.4.
  4. **Write.** D-67.6/D-67.7.

  An `LraRefusal` from `build_lra_model` replaces blocks 3 and 4 with its
  text, **verbatim**, in an `st.error`. Blocks 1 and 2 still render, because
  they are usually how the refusal gets fixed.
- **D-67.3 — The mesh counts move to the beam page, and the registry learns
  non-step pages.**
  - The four `lra_mesh.*` rows change `page` from `configuration_layout` to
    `beam_model`.
  - `test_every_page_is_a_real_workflow_step` becomes
    `test_every_page_is_a_gui_page`, read against `wf.gui_pages()`.
  - A non-step page that renders registry rows must say so in its `GuiPage`
    reason. Only `beam_model` does.
  - **D-56.4's placement reasoning is superseded on one point.** The mesh
    went to Geometry because the export page was retiring. The mesh is still
    "a discretisation of the airframe's own beam geometry". It now sits
    beside the drawing of that discretisation.
  - `ref_axis_pct` does **not** move. `net_loads` and `tail_span` torsion
    read it, and an analysis input stays with the analysis that consumes it.

### The drawing

- **D-67.4 — One figure family, four instances, in `sloads.report.figures`.**
  - **The family:** `lra_beam_model`, `Stage.PRE_RUN`. The model is entered
    geometry discretised, and no load has been computed to draw it.
  - **The instances:** `plan`, `side`, `front` and `iso`. Each is a `Figure`
    whose `PlotData` carries:
    - one open `Series` per CBAR chain family, `style="solid"`;
    - one dashed `Series` for the RBE2 ties;
    - closed outline `Series`, ported from `collect_outlines`;
    - `points` for the tagged nodes (SOB, posts, centre, fin root, h-tail
      attach, gear, engine mount and hub, hinge, actuator) and the SPC
      support.
  - **The iso view** is a fixed axonometric projection
    (elev 22°, azim −125°, the script's own) applied by the producer. That
    keeps it 2-D `PlotData` that both renderers already draw.
  - **The builder** is `build_lra_model` plus the outline owners the script
    reads (`resolve_tail_planform`, the fuselage sections, the wing edges).
    The draping helper calls the exporter's `_interp_chain`, renamed
    `interp_chain` and exported, instead of a copy.
  - **No colour carries meaning,** because §4.3 requires greyscale. The
    families are told apart by style and legend name, not by the script's
    palette.
  - **An outline that fails to resolve is dropped** with a caption sentence
    naming it. The beam still draws (the script's contract, kept).
- **D-67.4a — `FigureFamily.step` accepts a `gui_pages()` key.** The
  family's page is `beam_model`. Today's guard reads `oracle_steps()`; it
  widens exactly as D-67.3's does.
- **D-67.4b — `is_to_scale` becomes "any series is closed".** The beam views
  carry open chains beside closed outlines, so "every series closed" would
  draw an airframe out of scale. No existing figure changes answer: no load
  distribution carries a closed series, and every current to-scale figure
  has one. A beam view whose outlines all failed to resolve then loses the
  aspect lock. Its caption already says the outlines are missing.
- **D-67.5 — The script and its test retire.** `scripts/plot_lra_model.py`
  and `tests/test_plot_lra_model.py` are deleted. The test's three
  behaviours (renders every example, refusal verbatim, outline-free still
  renders) move to the family's test as gates 4–5. `matplotlib` stays in
  the dev extra, because `scripts/render_theory_figures.py` uses it, but its
  `pyproject.toml` comment loses the script's sentence. The report does
  **not** print the family. Whether it should is its own question, filed
  if asked.

### Writing

- **D-67.6 — One stamp owner.** `cli._stamps` moves to
  `sloads.report.methods.bundle_stamps(project, system, generated="",
  csv_channel=LoadChannel.LIMIT)` with an unchanged body. The CLI and the
  page both call it. Its stale "always ULTIMATE" sentence is corrected in
  the move.
  - **The page passes `generated=report_package.build_timestamp()`,** as the
    Report page does. The CLI passes its `--generated`.
  - **That stamp line is the only byte that may differ** (gate 1).
- **D-67.7 — One picker owner.** `_browse_block` moves to
  `app_shell/folder_picker.py` as `folder_picker(state_key, prompt)`, with
  the TCC warning. The Report page and the beam page call it, each under
  its own session-state key, so choosing a deck folder never moves the
  report folder.
- **D-67.8 — One file-name owner.** `sloads.export.deliverable_names(prefix)`
  maps target → file names. Its rows are `lra` → `<prefix>.lra_model.bdf`,
  `oew` → `<prefix>.oew_mass.bdf` and the existing `mass` names. `cli.py`
  stops spelling them.
  - **The page's prefix** is the project file's stem, or `sloads` for an
    unsaved project.
  - **An existing file is not overwritten silently.** The page lists the
    files that would be replaced and asks for one named confirmation.
  - **A refusal writes nothing:** the writers render before they open,
    which is already `write_lra_model_bdf`'s contract.
- **D-67.9 — The page writes two files: the LRA deck and the OEW mass set.**
  - The `oew` file is a self-contained `GRID` + `CONM2` fragment with no
    `MASSSET` and no case control, under D-56.6's unconnected-grid rule and
    header ("RBE2 each grid to your own model").
  - It is the deck's companion, not part of it. Ruling 4 and D-56.6 keep the
    mass model off the LRA grids, and this note changes neither.
  - The page does **not** write the full `MASSSET` model. `--export-conm2`
    keeps it.

### The OEW mass set

- **D-67.10 — `MassItem.usable_fuel: bool = False`** (schema v72 → v73;
  name per Q1).
  - **Meaning:** fuel that can be drawn by the engines, mission and reserve
    alike. Unusable fuel and oil is **not** usable fuel and stays in OEW.
  - **It is orthogonal to `consumable`.** Reserve fuel is
    `usable_fuel=True, consumable=False`. Mission fuel is True/True. A
    non-fuel expendable (water, stores) is False/True. No implication is
    enforced between them.
  - **This is the sixth typed row tag** (OV-1).
  - **The hop is additive and infers nothing,** so `_hop_72` is an identity
    and a migrated project's rows are all `False`. The five fixtures are
    tagged by hand (§1.3: ga6 "30 min fuel", concept_heavy and RJ "Reserve
    fuel", ATR's two reserve rows, and every DISCRETIONARY fuel row in all
    five).
  - **Read by the OEW partition only.** No load, G-5 burn-down or G-4
    estimate reads it in this step.
- **D-67.11 — One OEW partition owner.**
  `mass_distribution.oew_items(project)` returns the rows of
  `kind in (EMPTY, MINIMUM) and not usable_fuel`. `database_totals`' "OEW"
  prose points at it.
  - `mass_cards.oew_fragment(project, *, header_comment, system)` writes
    those rows through the existing `_conm2_line` and the `mass-cg` grid band.
    No second card writer exists.
  - **Its header names every MINIMUM row it includes, and every row it left
    out as usable fuel.** A migrated project whose reserve fuel is untagged
    therefore shows that fuel *by name* in the file and on the page, and is
    never silently in or out.
  - **The CLI gains `oew` in `EXPORT_TARGETS`,** so the page has no artifact
    the headless route cannot reproduce (gate 1).

### The counter (#244)

- **D-67.12 — One bounded-count owner in `app_shell`.**
  `app_shell.components.count_input(label, current, *, key, floor, cap,
  jump=10)` is used by `render_table`'s row counter and by the four mesh
  counts.
  - **Re-seeded from state.** The widget is re-seeded from `current`
    whenever the model's count differs from the widget's last committed
    value. A model that grew underneath it (the seed button, a project
    load) is shown as it is, never as a stale 1 beside 4,501 rows.
  - **Capped.** A value above `cap` is not committed. The control says the
    cap and why.
  - **A large jump waits for a click.** An increase of more than `jump` over
    `current` is held and needs a named confirmation ("Add 4,500 rows to
    Items"). Below `jump` it commits as today. Counting down is unchanged.
  - **The numbers are Q2's.** The registry carries a mesh count's bounds,
    and `count_input` reads them, so the widget and validation share one
    source.
  - **Validation refuses an out-of-range mesh count in a loaded file** with
    the same bounds, so a JSON edit cannot reach the exporter with 4,501.

## 4. Gates

| # | Gate | Test home |
|---|---|---|
| 1 | **Parity.** For every example, the page's write path and the CLI (`lra`, `oew`) produce byte-identical files given the same `generated`, in both unit systems. | `test_beam_model_page.py` |
| 2 | **One owner each.** `cli.py` defines no stamp, no file name and no deck writer. `oracle_app/report.py` defines no picker. No `_interp` copy survives. | `test_beam_model_page.py`, `test_platform_stability.py` |
| 3 | **G1 holds.** `oracle_app/beam_model.py` imports no `os`, no `pathlib` and no writer outside `sloads.export`. | existing `test_oracle_gui.py` |
| 4 | **Refusal.** An `LraRefusal` writes no file and shows the exception text verbatim, the script test's verbatim leg ported. | `test_beam_model_page.py` (AppTest) |
| 5 | **Figure.** The family builds four instances on every example. Every CBAR, RBE2 and tagged node of `build_lra_model` appears in the plan view. An outline failure degrades to a caption sentence. | `test_figures.py` |
| 6 | **Page set.** `gui_pages()` carries `beam_model`. Registry pages and figure-family pages are `gui_pages()` keys. The four `lra_mesh` rows render on the beam page and nowhere else. | `test_workflow.py`, `test_field_registry.py` |
| 7 | **OEW.** On every example, `oew_fragment`'s CONM2 masses sum **exactly** (`math.fsum`, then the mass factor) to Σ EMPTY + Σ MINIMUM − Σ usable-fuel MINIMUM, and sbeam's GPWG recovers that weight and CG to its existing gate-6 tolerance. No usable-fuel row and no DISCRETIONARY row has a card. | `test_mass_cards.py`, `test_sbeam_roundtrip.py` |
| 8 | **Schema.** The v72 → v73 hop round-trips. A v72 file loads with every `usable_fuel` False. The five fixtures carry the tags §1.3 lists. | `test_migrations.py` |
| 9 | **Counter (#244).** A jump past `jump` does not commit until confirmed. A value above `cap` never commits. The widget re-seeds when the model's count changes underneath it. An out-of-range mesh count in a loaded file is refused by validation. | `test_app_shell.py`, `test_validation.py` |
| 10 | **No load moves.** Appendix A oracles, the closure suites and every existing digest are byte-identical. The OEW set's digest is **new** and is the only digest added. | the existing suite |

## 5. Effect vs error bar (rule 6)

Not applicable: no delivered load changes. The defect this closes is
reachability: the primary deliverable could not be produced from the GUI. The
2026-09-28 re-charter ranked that inside B9 ("the user can reach them").

## 6. What this supersedes, touches and leaves

- **Supersedes:**
  - D-57.6's "without port" for the beam deck alone (D-67.1);
  - D-56.4's placement of the mesh counts (D-67.3);
  - `plots.is_to_scale`'s "every" (D-67.4b);
  - the backlog row's "no editor" sentence and #244's "app_shell owner"
    (§1.2, §1.4).
- **Touches:**
  - `workflow.py` (one `GuiPage`);
  - `field_registry.py` (four `page` tags, one new row for `usable_fuel`);
  - `models/inputs.py`, `models/project.py`, `io.py` (v73);
  - `mass_distribution.py`, `export/mass_cards.py`, `export/lra_model.py`
    (`interp_chain` exported);
  - `report/methods.py`, `report/figures.py`;
  - `app_shell/plots.py`, `app_shell/components.py`, `app_shell/folder_picker.py`
    (new);
  - `oracle_app/beam_model.py` (new), `oracle_app/report.py`, `oracle_app/form.py`,
    `oracle_app/Oracle.py`;
  - `cli.py`;
  - the five fixtures (tags only);
  - `DATA_DICTIONARY.md` (regenerated);
  - the user guide's page list.
- **Leaves:**
  - `--export-conm2` and its `MASSSET` model, unchanged;
  - `lra_import`, unchanged and CLI-only. Importing an LRA model from the GUI
    is not asked for;
  - G-4 and G-5's readings of `consumable`, unchanged. `usable_fuel` gives
    G-4 a typed reserve-fuel answer later, not here.

## 7. Closure obligations (tier L)

- This note merged at AGREED first.
- `PROGRAM_SPEC.md`: the export section (the `oew` target, the page) and
  WTONECG's database tags (`usable_fuel`).
- `CONVENTIONS.md` §7: rows for the stamp, picker, file-name, OEW partition
  and bounded-count owners.
- `theory_sources.md`: OEW's definition and its source.
- `GUI_design.md`: the page.
- One `changes/beam-model-page.history.md` in full step format, and the
  backlog rows 9 and 10 removed.
- #283 and #244 close through `solo_close.sh`.

## 8. Deferred

- The beam figure in the oracle report (D-67.5): file it if asked.
- An LRA import route in the GUI (§6).
- G-4's landing-weight estimate reading `usable_fuel` instead of its current
  rule.

## 9. Rulings taken at AGREED (owner, 2026-10-01, in session)

**Q1–Q3 as recommended.** The tag is `MassItem.usable_fuel` (D-67.10).
#244's bounded count confirms an increase of more than 10, caps a list at 500
rows and a mesh count at 200 per member, with a floor of 2 (D-67.12). The `oew`
target writes the fragment alone, with no GPWG check deck, and gate 7 is its
check. No decision changed at AGREED.

## 10. Amendments at implementation (2026-10-01)

**D-67.5 amended (owner ruling A, in session):** the oracle report **prints** the beam-model
family. Note 60 D-60.1's parity gate
(`test_figures.py::test_g_fig_5_every_gui_figure_has_a_report_producer`) holds
that no figure is shown in the GUI that the report does not print, and the
owner kept it whole rather than exempt the page. The four views open Appendix
G, the appendix that already states what the beam model's grids cost the
distribution, so the delivered model is drawn where it is described. The script's
three PNGs in `examples/` (`*_lra_views.png`, linked from nowhere) retire with
it.

**D-67.4b replaced: the producer states whether a figure is to scale** *(raised in session at step 3; the owner kept it in this item at closure, 2026-10-01)*.
"Any series closed" was measured against every figure the catalogue builds,
and it was not the rule either. `body_side_view` is captioned "to scale on equal
axes" and carries no closed series. The engine views, the ground attitudes and
the two tail LRA planforms carry open lines beside closed outlines, so the
GUI's "every series closed" drew them on free axes. In print, `plot_tex` never
set equal axes for any figure outside the four planform keys, so every one of
these printed to the wrong shape. The amendment: `PlotData.to_scale`,
stated by the producer on the same reasoning as `log_x` (a property of the
quantity, which both renderers must answer the same way). `app_shell.plots`
and `plot_tex` both read it. A guard holds the flag and any caption that says
"to scale" together. The printed engine views, attitudes, side view and
LRA planforms move as a result, and the history fragment says so.

**D-67.4 refined: outlines come from the report's own owner.** The three
orthographic views draw the airframe through `oracle_sections._airframe_series`,
the owner the engine views already use, instead of porting the script's
`collect_outlines`. That drawing therefore has one owner rather than two. The
iso view draws the beam, the ties, the owned nodes and the fuselage side
profile. It does not drape the planforms, which was the script's own "picture
convention, not geometry".

## 11. Implementation record — #283 and #244 (2026-10-01)

Built in six steps on `dev/v0.8.8`, the full suite green after each. Where the
build departed from §3, it is said here. The owner confirmed §10's to-scale
amendment at closure, kept in this item.

- **D-67.6–D-67.8 (owners first).** `report.bundle_stamps`,
  `app_shell/folder_picker.folder_picker` and `export/deliverables` moved the
  stamp, the picker and the file names out of `cli.py` and the Report page. The
  CLI's copy of the stamp read the version from `importlib.metadata`, the
  install-time snapshot `sloads/_version.py` replaced; the owner reads
  `_version`. **Departure:** `lra_model.write_lra_model_bdf` is retired rather
  than kept beside the new path. The CLI's `lra`/`oew` targets and the page
  render through `deliverables.render_set` and write through `write_set`, so a
  set is rendered whole before any file opens.
- **D-67.10/D-67.11.** Schema v73 and its identity hop. The five fixtures are
  tagged: 13 usable-fuel rows, reserve and mission. Unusable fuel, unusable
  fuel and oil, and the Baron's fuel system stay untagged. ATR OEW 22,674 lb
  with both reserve tanks left out. sbeam's GPWG recovers each OEW to about
  1e-7. One new digest channel per example (`sbeam/oew_mass`, 258 → 263); no
  existing channel moved.
- **D-67.4/D-67.5 (as amended in §10).**
  - `oracle_sections.beam_model_figures` builds the family from
    `build_lra_model`.
  - The orthographic outlines come from `_airframe_series`. The script, its
    test and its three PNGs are deleted.
  - `PlotData.to_scale` is set on seven existing drawing producers. Drawings
    place their legend in baselines, as the planform emitter does.
  - **Found at implementation:** an engine side view on equal axes is a thin
    strip, and the axis-relative legend offset then sat on its x label.
- **D-67.1–D-67.3 (the page).** **Departure:** `form.render_page_inputs`
  renders a non-step page's registry rows by sharing `render_step`'s group
  loop rather than copying it. **Found at implementation:** the deck itself
  raises a plain `ValueError` when no balanced case can be assembled. The page's
  write catches `ValueError` (an `LraRefusal` is one), or such a project would
  have crashed it.
- **D-67.12 (#244).** `app_shell.components.count_input`, with
  `field_registry.ROW_COUNT_CAP`, `COUNT_CONFIRM_JUMP`, `COUNT_RULES` and
  `models.inputs.LRA_GRID_BOUNDS`. **Departure:** a mesh count out of range in a
  loaded file is refused by the **exporter**, as an `LraRefusal` naming
  `lra_mesh.<member>_grids`, and not by `validation`. Validation's warnings
  target analysis-step pages only, and the Beam Model page already states
  refusals verbatim. `LraMeshInput.count` enforces the cap too.
  - The oracle journey's typing harness clicks the held-jump button, as it
    clicks the #143 Add gestures: typing a 24-row table from blank now asks
    once.
  - "LRA" joined the label spelling table (so the record reads "LRA Mesh"),
    since `DISPLAY_GROUPS` titles are reserved for original-suite fields.
- **Gates:**
  - `tests/test_beam_model_page.py`: gates 1, 2 and 4, the page under AppTest,
    and the one-picker guard.
  - `tests/test_figures.py`: gate 5 and the to-scale pair.
  - `tests/test_field_registry.py` and `tests/test_workflow.py`: gate 6.
  - `tests/test_mass_cards.py` and `tests/test_sbeam_roundtrip.py`: gate 7.
  - `tests/test_migrations.py`: gate 8.
  - `tests/test_bounded_count.py`: gate 9.
  - Gate 10 is the unchanged suite and digests.
