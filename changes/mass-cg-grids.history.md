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
