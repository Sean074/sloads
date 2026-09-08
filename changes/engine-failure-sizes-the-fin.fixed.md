- **The 23.367 cases reached the load-case index carrying no load at all (note 44
  OR-180, tier L, 2026-09-07).** The module published its headline load under the
  key `max_tail_load`; `render.load_cases_to_rows` maps `fy_side`. Every 23.367
  row in the published case file therefore had an ID, a regulation, a speed and a
  factor, and no load. The fin load is a side load and is keyed as one.
- **An SI deliverable could head a column in `ft-lb` or `in`.**
  `render._detect_moment_unit` fell back to the Imperial `ft-lb`, and the
  location fallback to `in`, whatever system the set was rendered in. Nothing
  exercised it while every result set with a case index also carried a moment and
  a location; the one-engine-out set carries neither. Both fallbacks now read the
  set's own force unit for their system.
- **Deck subcase comments overran the 72-column card width.**
  `subcase_map_block` and three per-case `$` headers built their own lines
  instead of going through `sbeam_bridge._comment`, so they carried their own
  width assumption — fine while every condition name was as short as `PHAA`, and
  an overrun on the four turboprop tail decks the moment one was not. The width
  is the emitter's property now, which is the rule the wing decks were already
  moved to.
- **A negative zero in the tail deck's inertia statement.** The fin's lateral
  factor is exactly zero on a condition naming no V-n point, so the inertia total
  printed `-0.0 lb` — which reads as a small negative load rather than as none.
