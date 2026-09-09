- **Every h-tail load station printed the wing-root waterline as an airplane
  coordinate (#236, 2026-09-08 review R12, tier M, 2026-09-08).**
  The GA-6 report printed WL 78.5 — the wing root — for every h-tail station in
  §5.1 and Appendix D under a note calling the point airplane axes, while the
  airplane's h-tail sits at WL 111; an analyst importing the points placed the
  tail 32.5 in low with no way to know. The number was `tail_span`'s documented
  placeholder (z enters no load for a surface that loads in fz only), and the
  filed 0.8.2 scope was a disclosure sentence — the owner widened it (option B,
  OR-15 admission over `sloads/modules/tail_span.py`): `LayoutInput.h_tail_z`,
  until now a three-view sketch offset, is a real analysis input read by the
  new single owner `tail_geometry.h_tail_waterline` (fin tip on a T-tail,
  mid-fin on a defaulted cruciform — the deck used the wing root there, below
  the drawn surface — `root_waterline_z + h_tail_z` where entered, the
  wing-root plane marked ASSUMED with a loud note otherwise).
  `tail_span._h_tail_waterline` is a thin reader of it, so §5.1's station
  table, Appendix D and the exported GRIDs all moved together; both tables now
  carry a provenance sentence built from the same owner
  (`oracle_sections._htail_waterline_sentence`), so the document cannot claim
  a placement the resolution did not make. `ga6_normal` enters 32.5 and
  `baron_58` 13.0 (their own h-tail mass items); `cessna_210`/`concept_heavy`
  stay blank and print the ASSUMED disclosure. No delivered load moved — z
  pairs with the force components the surface does not carry. Register rule
  added (ORACLE_REPORT.md §3.6). Guards, all bite-proven: the owner's entered/
  assumed/fin-tip branches, a three-view-vs-load-path drift guard (the fin's
  twin), and the report's two-direction guard — the GA-6 must print 111.0 with
  the entered sentence, and the GA-6 with `h_tail_z` blanked (the reviewed
  state) must print 78.5 with the ASSUMED not-the-true-waterline sentence in
  both tables.
