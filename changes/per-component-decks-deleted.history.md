- **The five per-component solver decks are deleted (note 56 D-56.2, tier L,
  2026-09-11)** — The third slice of note 56, and the one the note is named for.
  `sbeam_bridge.py` shipped the suite's loads as five families of per-component
  deck: a wing CBAR stick model, a fuselage FORCE deck, a chordwise tail deck,
  two spanwise empennage decks and a control-surface deck, each with a CSV
  companion. All ten files are gone. They were separate structural models of one
  piece of the airplane apiece, sharing an ID space with the deliverable — the
  full-span balanced free-free model, which is the whole airplane with aero and
  inertia together — and the deliverable was borrowing GIDs *from* them, so
  `GID 7` named one point in `wing_loads.bdf` and another in `lra_model.bdf`.
  Roughly two-thirds of the milestone's open export work was maintenance on
  concepts that were not what ships.

  **The sequencing is the note's, inverted for this group, and the inversion was
  checked before it was taken.** Note 56 ordered the move of the applied-load
  family before this deletion, on gate 1: deleting the decks before rehoming
  what they sit beside would take the oracle report with them. That reasoning
  belonged to the *report tables* group, which moved in the previous slice. For
  the applied-load family an AST closure settled it the other way: the family's
  entire coupling to the deck writers is **fourteen names, every one a GID
  allocator, a band or a results-coercion helper** — which is the structural
  form of D-56.9's own statement that `AppliedLoad.gid` is a per-component
  deck's GID. Deleting first keeps all fourteen and removes 1,400 lines that
  touch none of them; moving first would have meant writing a
  `report → export.sbeam_bridge` import for those fourteen and then moving them
  again one slice later. Note 56 §8's confirm-before-delete resolved clean in
  the same pass: the oracle report draws **no** per-component deck table, so
  nothing needed rehoming.

  **Three standing limitations were retired, not reworded.** `centerline-clamp`
  (the wing stick model's SPC at BL 0, and the 23 % by which its reaction
  overstated a root load), `flight-only-body-deck` and `export-case-filter` each
  described a limitation of a per-component view and each pointed the reader
  toward the assembled deck. With the views gone the sentences have no subject,
  and keeping them would describe the deliverable as having a limitation it
  cannot have. Retiring a caveat is the one edit that can quietly widen a claim,
  so the owner was asked before the slice began and the three go in this commit
  against `test_methods_stamp`'s pinned key set — which is what that contract
  exists for.

  **Five gates changed authority and kept their form; two narrowed and say so.**
  G-OR-59 and Appendix D's one-load-set gate now read
  `applied_loads(…)` instead of the deleted span CSVs — the row set both were
  always built from, which is why the appendices are unchanged by the deletion.
  G-OR-37, the gate that the delivered loads are the applied set and not a
  differenced cumulative column, is summed from the applied set itself rather
  than re-derived from deck text. The free-free geometry mutation and the
  deck-comment width sweep moved to the assembled and LRA decks, which is where
  they belong: those are the decks that ship. The two that narrowed are stated
  in place. **G-OR-73** lost its "deck and document agree" comparison, because
  the surviving decks have no CSV companion and the surviving CSVs have no deck;
  both halves were always compared to the case's own `safety_factor` rather than
  to each other — that was the assertion carrying the force, and it is
  untouched. **The swapped-subcase mutation** became a deck-text check: every
  balanced free-free case has a zero resultant by construction, so swapping two
  subcases' load sets leaves all six reactions at zero and no reaction-based
  gate can see it. Writing a solve that proves nothing would have been worse
  than asserting the property where it is observable.

  **Two gates were lost outright, and neither is disguised.** The wing stick
  deck's solve gate took `test_the_sob_internal_load_is_the_first_outboard_
  elements_end_force` with it: the closed-form side-of-body load is still gated
  against the cumulative table, but the solver cross-check needs a deck with a
  CBAR outboard of the SOB node whose cards are that wing case's, and the LRA
  deck's cases are balanced cases — a different claim, not a rename, and it
  belongs to D-56.4's mesh. G-OR-90 lost its deck-comparison leg for a better
  reason: it compared `applied_loads` against `tail_span_force_moment_cards`,
  two renderings of one load set, which is a real check only while two writers
  can disagree. D-56.9 makes the applied set *the* authority the delivered cards
  are written from, so that comparison is now tautological; the leg that carries
  the OR-143 defect never read a deck and is untouched.

  **One defect this slice creates and does not close**: the case index still
  publishes a `LOAD/SUBCASE (component)` column, and no artifact quotes those
  numbers any more. `test_case_ids` asserts the absence explicitly — it fails if
  a component pairing reappears — so the gap is recorded rather than silent, but
  a shipped index naming a deck that does not exist is misleading content and
  belongs to #209. The Imperial digest re-stamps deliberately: 330 channels →
  280, of which sbeam goes **83 → 33**, the note's own measure of the reduction.
