- **The delivered files start saying which way their axes point, and stop
  stating zeros their own rows fill (#242, 2026-09-08 review C2+C3+C4, tier M,
  2026-09-13)** — the review checked the CSVs against the requirement they exist
  to serve, found the *data* airplane-global and frame-correct throughout, and
  found the *self-description* missing the one sentence a forwarded file cannot
  do without: nothing anywhere said that `x` is the fuselage station positive
  aft. Note 56 narrowed the finding on its way here — the deck-companion span,
  chordwise and fitting CSVs it also covered went with their decks, and with
  them `tail_chordwise.csv`'s second meaning of `Axis` and
  `control_surface_loads.csv`'s `Fz`-on-a-lateral-normal — so what was left was
  the report's own set and the two halves of C3 that had survived into it. The
  fix is one stanza in the methods stamp, because the stamp is the single
  statement every channel already wraps (G8-3), and the axis words live in
  `export/coordinates` rather than in the stamp, because `CONVENTIONS.md` §1
  already names that module the single edit-point for the map and a sentence
  that is not beside the thing it describes is a sentence that outlives it. Two
  exceptions are declared rather than papered over: the gear report carries the
  manual's ground-line frame in three of its columns and airplane axes in every
  other, and says so in its own block; and the applied files' torsion-axis
  column was renamed `TorsionAxis` because the fin's torsion is `Mz` and a
  column asserting `Myy` was, on one of six files, exactly the class of claim
  the issue was filed about. Working the file set turned up the same defect from
  the direction prose cannot defend itself in: note 56 D-56.9 had re-aggregated
  the delivered rows onto the LRA grids, where each load carries the lever-arm
  couple of its own offset, and the hand-written structural-zero blocks — the
  numbers having moved and the sentences not — were declaring `Mx`, `My` or `Mz`
  zero "throughout" on four of the six files while the rows beside them were
  filled. So OR-140's apparatus was split: whether a column is zero is now
  **measured** from the rows being written, the prose supplies only the reason,
  a zero that belongs to this configuration rather than to the model is stated
  as that, and a file at grids says it is at grids. C4's riders were taken where
  they were the same defect class — the V-n file now carries the two table notes
  that define five of its nineteen columns, read off the `Table` objects the
  appendix renders so the two cannot drift, and `sloads/csv_text.py` owns the
  line terminator that every stamped file used to mix — and left where they were
  not: the `lbf`/`psi` display vocabulary lives entirely in `app/views/`, which
  #270 deletes, and the `N·m` middot is an encoding decision (a UTF-8 BOM, or an
  ASCII-ised SI vocabulary) that moves the whole SI channel and wants an owner
  ruling rather than a rider on an axis stanza. Guarded by
  `tests/test_delivered_frame_statement.py`: every stamped channel states all
  three axes and their senses; the axis words appear in no second place under
  `sloads/`; the stanza is identical on two different airplanes; the gear
  report places every one of its frame-bearing columns on one side of the split,
  checked against the field list so a column added later fails rather than
  passes; no applied file claims a zero its own rows fill and no reason outlives
  its column, over every bundled example and all six components; a file at grids
  says so and one that is not does not; and no delivered channel, decks
  included, contains a carriage return.
