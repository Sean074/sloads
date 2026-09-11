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
