- **An SI artifact states every number in SI, its prose included: provenance notes carry their quantities live and render in the channel written to, a persisted record keeps its numbers in values, and case names stay identifiers (#338, tier M, 2026-09-30)** —
  #312's SI check came first, as its row asked, and found the defect. `units.convert_results` converts values and never text, so a number a calc builder formatted into a string stayed in inches and pounds in an SI artifact. Measured on the five fixtures:
  - the SI LRA deck said "side of body ASSUMED at BL 23.00 in" beside GRIDs in mm (8–13 `$` lines per fixture);
  - both SI mass decks captioned every MASSSET in lb and in;
  - `concept_heavy`'s SI document placed its wing station "at FS 236.0 in";
  - Baron's SI WTENV table had "station -105 in" inside a label.

  Each named its unit, so nothing was mislabelled; the artifacts mixed units.
  **The owner (D1).** `units.UnitText` (built with `unit_text`/`Quantity`) is a sentence whose numbers stay Imperial values until a writer calls `render(system)`. It converts them through the tables a `LoadValue` goes through and prints them through `format_value`, which moved into `units.py` for it (`report/render.py` re-exports it). It has no implicit `str()`. These provenance records carry it:
  - `SobStation`, `FuselageCentreline`, `FuselageLra`, `VtailRoot`, `HTailWaterline`, `HTailAttachment`;
  - the planform notes;
  - `Joint.note`;
  - the LRA model's `assumed_notes`, including its gear-carrier and engine-mount sentences.

  The LRA deck renders them in its own system, and both mass decks' captions render in theirs. `BodyDragWaterline` keeps a plain `str`: its notes state no quantity.
  **Persisted records keep the number in a value (D2).**
  - The body result's `wing_station_note` is now a clause with no number in it (`joints.WING_STATION_CENTRELINE_REASON`), and §8 states the station from the result's `x_wing`.
  - WTENV's `(none -- ...)` ballast marker names no station. The moment-balance station and the fuselage nose and tail stations are value rows of their own.
  - The derived loading notes drop their ballast weight, which the loading carries.
  - A result's persisted `notes` render in Imperial (`tail_span.imperial_notes`); the rest of that class is #312's and #339's.

  **Case names are identifiers (D3).** A re-weighted ground case keeps "at 36,817 lb" in every system, and the SI LRA deck says so once above its case map.
  **Gate** (`tests/test_si_artifacts.py`):
  - SA-1, the rule;
  - SA-2, every provenance record a deck reads types `note` as `UnitText`;
  - SA-3, no Imperial-unit number in the SI LRA and mass decks of any fixture, or (slow lane) in the SI document and its `data/`, once identifiers are removed. The scan names the words that make `in` a preposition, so "-105 in is outside" counts as a station and is caught.

  **Delivered effect.** No load, card or GRID moves. Text moves in Imperial as well, because the notes now print at their units' precision (note 65): "BL 23.00 in" becomes "BL 23.0 in", and the spar fractions print through `format_value`. Imperial digests moved on 15 channels:
  - every fixture's `sbeam/mass_model` and `sbeam/mass_check` (caption text only);
  - the `sbeam/lra_model` of `ga6_normal`, `baron_58` and `concept_regional_jet` (`ASSUMED:` text only; the ATR's notes state no quantity);
  - Baron's `csv/weight_envelope` and `txt/weight_envelope` (the forward-regardless and aft-gross markers lose their stations and gain the station rows).

  No load-case channel moved.
