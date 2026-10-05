- **Every case-id band has a stated top edge, and a band that fills is refused by name instead of minting the next band's ids (#366, tier S, 2026-10-04).**
  `tail_span` minted `HT-{20+k}` per T-tail induced-roll carrier (#334) with
  `k` unbounded, so a 31st carrier would have minted `HT-50`, the tab band's
  first id, and corrupted the case index and the deck's subcase numbering
  without a word. The same shape was in `wing_inertia`'s hand-authored extra
  band, and every allocator band was open at the top. `case_ids.BAND_LAST` is
  now the one owner of each band's edge: a band ends where the next starts,
  and the last ends at the 100-wide subcase block. Both the allocator and the
  new `band_case_id` read it. A drift guard refuses an id formatted by hand
  from `COMPONENT_PREFIX` outside `case_ids`. The fullest band in any shipped
  example reaches 33 of its 99. No shipped fixture or delivered load moves.
