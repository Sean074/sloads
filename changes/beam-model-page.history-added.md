## Step — The beam model reaches the GUI: a Beam Model page shows its axes, owns its mesh, draws it and writes the deck with the operating empty weight's mass set beside it, every drawing is drawn to scale, and a stray keystroke can no longer commit 4,501 rows (#283 with #244 riding, design note 67 D-67.1–D-67.12, tier L, 2026-10-01)

**Objective.** Close #283 and #244. The LRA free-free beam model is the primary deliverable, and the GUI had no route to it:

- the deck was written only by `cli.py --export-target lra`;
- the model was drawn only by `scripts/plot_lra_model.py`;
- note 57 D-57.6 had retired the export page without a port.

Measured first (note 67 §1):

- **The stamp was CLI-private.** It read the tool version from `importlib.metadata`, the install-time snapshot `sloads/_version.py` exists to replace.
- **The folder picker was private to the Report page.**
- **The axis and the mesh were already editable on Geometry.** The backlog row said otherwise.
- **"OEW" had no typed partition.** Four of five fixtures keep reserve fuel in `MINIMUM` with `consumable` False, by G-4's design.
- **#244's counter lived in `oracle_app/form.py`,** not in `app_shell`. Nothing bounded the mesh counts either.

**Deliverables.**
- **One owner each for the stamp, the names and the picker (D-67.6–D-67.8).**
  - `report.bundle_stamps` reads the version from `_version`.
  - `export/deliverables` holds the file names and the one render-then-write both routes take. `render_set` renders a whole set before `write_set` opens a file, and `write_lra_model_bdf` retires.
  - `app_shell/folder_picker.folder_picker` keeps one session key per page.
  - The stale "the BDF stamp is always ULTIMATE" prose in `cli.py` and `report.methods` is corrected.
- **The OEW mass set (D-67.9–D-67.11).**
  - `MassItem.usable_fuel` (schema v73, identity `_hop_72`). Mission and reserve fuel are usable; unusable fuel and oil are not, per 14 CFR 23.29(a).
  - `mass_distribution.oew_items`: `EMPTY` + `MINIMUM` less usable fuel.
  - `mass_cards.oew_fragment`: GRID + CONM2, no MASSSET. Its header names every `MINIMUM` row it kept and every fuel row it left out.
  - The CLI gains `--export-target oew`.
  - The five fixtures tag 13 rows. The ATR's OEW is 22,674 lb with both reserve tanks left out.
- **The drawing (D-67.4/D-67.5, amended in §10).**
  - `oracle_sections.beam_model_figures`: four views (iso, plan, side, front), drawn from `build_lra_model`, the deck's own builder.
  - The orthographic outlines come from `_airframe_series`, the engine views' owner. A refusal is stated verbatim in each view.
  - Catalogued on the `beam_model` page, and printed at the head of the oracle report's Appendix G, so note 60's parity holds.
  - The script, its test and `examples/*_lra_views.png` are deleted.
- **Drawings to scale (§10, owner-confirmed).**
  - `PlotData.to_scale` is stated by the producer, and both renderers read it.
  - Before, the screen derived it from "every series closed", and print never set it outside the four planform keys. The engine views, ground attitudes, tail LRA planforms and fuselage side view were drawn on free axes under captions saying "to scale on equal axes".
  - Seven producers set the flag.
  - A drawing's printed legend is offset in baselines, so a thin drawing's legend clears its axis label.
  - Unnamed series take no legend row on screen, as in print.
- **The page (D-67.1–D-67.3).**
  - `NON_STEP_PAGES` gains `beam_model`.
  - The axes are shown read-only by `lra_model.reference_axis_rows`, over the same `LRA_SURFACES` the exporter refuses on.
  - The four `lra_mesh` rows move from Geometry, rendered through `form.render_page_inputs`, which shares `render_step`'s group loop.
  - The write needs a named confirmation before replacing a file. The page catches the deck's own `ValueError`, not only `LraRefusal`.
  - The registry and figure-family guards widen from analysis steps to GUI pages.
- **The bounded count (D-67.12, #244).** `app_shell.components.count_input` covers every row counter and every `field_registry.COUNT_RULES` field:
  - rows are capped at 500, and mesh counts run 2–200 (`LRA_GRID_BOUNDS`, the exporter's own range);
  - an increase of more than 10 is held until its named button is pressed;
  - the widget re-seeds whenever the model moved underneath it;
  - a file carrying an out-of-range mesh count is refused by the exporter, naming the field.
- **Docs:**
  - `PROGRAM_SPEC.md`: the export menu (stale "default" and "Export page bundles" text removed), the Beam Model page, the `usable_fuel` consumer row, the mesh range.
  - `CONVENTIONS.md` §7: six owner rows.
  - `theory_sources.md`: the OEW definition.
  - `GUI_design.md` and `GUI_USER_GUIDE.md`.
  - The guide's getting-started, troubleshooting and where-next chapters.
  - `PROJECT_GUIDE.md` §4.
  - `DATA_DICTIONARY.md` and the guide's generated tables, regenerated.
- **Digests.** One new channel per example, `sbeam/oew_mass` (258 → 263). No existing channel moved. The oracle report has no digest channel.

**Test.**
- `tests/test_beam_model_page.py` (new):
  - gate 1: page and CLI byte-identical, four airplanes, both systems;
  - a refusal writes nothing and is stated verbatim on the page;
  - the file prefix rule and replace detection;
  - the page under AppTest: shipped airplane, blank project, write click;
  - one picker owner.
- `tests/test_bounded_count.py` (new), gate 9:
  - the cap, a held jump, a small step committing normally, the re-seed;
  - the mesh bounds equal the exporter's;
  - a blank mesh count's jump is measured from its default;
  - a file count of 1 or 4,501 is refused by name.
- `tests/test_figures.py`:
  - the beam model's plan view carries every CBAR, tie and owned node;
  - a refusal is stated verbatim;
  - both renderers honour `to_scale`, and a caption claiming "to scale" carries the flag;
  - G-FIG-1/3/6 walk GUI pages.
- `tests/test_mass_cards.py`: the fixture tags, the exact partition, one card per kept row, the header naming every `MINIMUM` row, an untagged reserve kept by name.
- `tests/test_sbeam_roundtrip.py`: GPWG recovers the OEW in both systems.
- `tests/test_migrations.py`: the v73 hop.
- `tests/test_cli.py`:
  - the `oew` target;
  - the CLI builds no stamp and spells no file name;
  - the stamp carries `_version`'s version.
- Re-cut:
  - `test_field_registry.py`: pages are GUI pages, and the mesh renders on the beam page alone.
  - `test_lra_model.py` and `test_deliverable_units.py`: the writer moved to `deliverables`.
  - `test_oracle_report.py`: picker keys.
  - `test_schema_guards.py`: the v73 hash.
  - `test_oracle_journey.py`: the harness clicks a held jump, as it clicks the #143 Add gestures.

**Key decisions.**
1. **A non-step page, not a fifth phase.** The model is the deliverable built from the analysis. Its page runs no `.BAS` program and fills no slice a computation reads, and `workflow.py` already said deliverables are not steps.
2. **The axis stays where its other consumer is.** `net_loads` and `tail_span` torsion read `ref_axis_pct`, so it is entered on Geometry and shown on the beam page. The mesh, which only the exporter reads, moved beside its own drawing.
3. **OEW is a typed partition, never a name match.** `consumable` already means "G-5 may burn it down", and reserve fuel is deliberately not consumable. Unusable fuel and oil stay in OEW on the regulation's own empty-weight definition.
4. **The report prints the beam model (owner ruling A).** This keeps note 60 D-60.1 whole, so the GUI shows no figure the document lacks, rather than carving out the first exemption.
5. **"To scale" is the producer's statement.** It is a property of what is drawn, like `log_x`, and both renderers must answer it alike. Deriving it from closed outlines was wrong in both directions on the shipped catalogue.
6. **A file's out-of-range mesh count is the exporter's refusal, not a validation warning.** Validation warnings target analysis-step pages only, and the refusal reaches both the CLI and the beam page verbatim.
