- **The LRA deck states the SELECT conditions it does not assemble (#284, tier S, 2026-09-20).**
  The assembler records every condition it drops through one owner, but the block
  that rendered the record lived in the assembled deck note 56 D-56.8 stopped
  shipping, and the LRA deck -- the one solver deck that ships -- wrote none: a
  sizing loop reading it was never told that a quarter of SELECT's set is absent
  (ATR 47 assembled / 28 recorded). The `$ CONDITIONS NOT ASSEMBLED` block now
  renders under the LRA deck's case map from the wording owner
  (`balance.skipped_block`, moved beside `SKIP_REASONS` so the shipping deck does
  not import it from the internal producer), derived when the caller supplies no
  record. The `out-of-family` reason no longer sends the reader to the
  per-component analyses D-56.2 deleted: it names the report and case index that
  carry the fuselage conditions, the report alone for the one-engine-out fin
  conditions, and states that none reaches a solver deck (#285 is the fin's
  return). Guard: `tests/test_lra_model.py::test_the_lra_deck_states_what_it_does_not_cover`
  holds deck block == record on every CLI-exportable fixture, on the derived,
  supplied and written paths. Statement only -- no load moved; the fourteen digest
  channels that carry the wording (balance txt, balanced_deck, lra_model)
  regenerated.
