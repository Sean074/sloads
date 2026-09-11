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
