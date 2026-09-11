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
