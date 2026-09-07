- **An applied-load CSV per surface (note 44 §18 OR-141a, tier L, 2026-09-07).**
  `fuselage_applied_loads.csv`, `htail_applied_loads.csv` and
  `vtail_applied_loads.csv` join `wing_applied_loads.csv` in the export bundle and on
  the Export page, each carrying its component's whole applied set — the case, the
  point the load acts at, all six body-axis components and the factor. One file per
  surface rather than one airframe file with a component column: a consumer loads the
  surface they are sizing, and a single file would have to be filtered before it could
  be used. The file and its appendix are the same rows through the same owner, and
  **G-OR-90** holds both to the cards the deck writes.

- **Appendix C is split into C.1 applied and C.2 carried (note 44 §18 OR-144, tier L,
  2026-09-07).** On the reasoning that split Appendix B and was never the wing's alone:
  the load applied at a station and the load carried across it are different quantities,
  and a reader who takes one for the other builds the wrong model. They shared one
  table, with the distinction carried by a sentence in a note.
