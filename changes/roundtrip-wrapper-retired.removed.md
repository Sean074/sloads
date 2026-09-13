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
