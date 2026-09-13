- **The assembled full-span deck stops being a shipped artifact (note 56 D-56.8,
  tier L, 2026-09-12).** Four surfaces retire in one change: the Balanced Cases
  page's stamped download, the Export & Report page's row, the `.bdf` inside the
  bundle `.zip`, and `cli.py --export-target balanced`. The report's Appendix A
  manifest loses its row with them — a controlling document naming a file the
  reader was never given is review F-D2's defect pointing the other way.
  `EXPORT_TARGETS` goes 4 → **3**: `gear` stays because D-56.1 reclassified the
  gear interface report as a *document* and this is its only headless route.
- **What ships in its place already did.** The **LRA beam model** carries the
  same assembled cases, transferred onto the beam's own grids, free-free, one
  `SUBCASE` per case — so nothing left the deliverable, one of two files
  carrying the same load sets did.
  `tests/test_cli.py::test_the_beam_deck_is_reachable_headless` is review F-D1's
  gate moved to follow the artifact rather than retired with the file it was
  first written about.
- **One stale manifest description swept with it (rule 4).** The mass model's
  row still said "for splicing into a model that already has nodes" — untrue
  since D-56.6 gave every `CONM2` its own `GRID` at its own CG. It now states
  what the file is and what splicing it costs: an `RBE2` per mass.
- **`balanced_deck` stays, as a genuine internal producer.** Its text is the
  un-aggregated load set at each load's true position, and its resultant is what
  the transferred set is gated against (`test_the_transferred_set_has_the_
  balanced_decks_resultant`). Deleting it would have deleted the reference the
  deliverable is checked against.
