- **Appendices D and E did not carry every applied load the deck emits, and said they
  did (note 44 §18 OR-143, tier L, 2026-09-07).** Both stated that "a row here and the
  card that carries it are the same load". Per station the spanwise deck writes a
  `MOMENT` card from the strip torsion and folds the span-axis axial into the `FORCE`
  card; the appendix printed one force column and no moment at all. First case, summed
  over stations: horizontal-tail applied torsion **6,689 lb-in** on `ga6_normal` and
  **232,139** on `concept_regional_jet`; fin torsion **2,351** and **80,117**, with
  **23.1 lb** and **638.5 lb** of axial. Appendix E's note further stated that the two
  components beside its normal load were "not zero by measurement but absent by
  construction" — for the fin `Fz` is neither, and never was. Three shipped examples
  also carry a T-tail transfer node that neither appendix printed. A reader building a
  model from D or E got an under-loaded surface and was told the set was complete.
  **G-OR-90** now holds every appendix row to the card the deck writes at that grid,
  case by case, on all three shipped examples.

- **The fin's torsion was stated about an axis a lateral load cannot twist (note 44 §18
  OR-142/OR-146, tier L, 2026-09-07).** `applied_body_moments` returned
  `(mx, myy_free, mz)` for every row — right for the wing and the horizontal tail, whose
  span is `y`, and wrong for the fin, whose span is `z`: its torsion is `Mz`, and
  negated. Section 6.5 printed the same quantity as **`Myy` = 4,561 lb-in** at
  `ga6_normal`'s fin root, when the airplane's `My` on a fin is *identically zero*: a
  lateral force produces no moment about the `y` axis at all. Section 3.2 maps the beam
  symbols onto body axes two chapters earlier, so a reader carried that map into
  section 6 where it was wrong by ninety degrees. `coordinates.tail_torsion_to_airplane`
  had owned the right map, with the sign derived rather than asserted, since the deck was
  written; the report was the consumer that did not call it. Section 6.5 and Appendix E
  now print `Mzz`/`Mz`, and each notation table names the airplane axis rather than
  leaving the letter to carry it.

- **Appendix B.1 stated its safety factor somewhere else (note 44 §18 OR-139, tier L,
  2026-09-07).** Alone among the four applied appendices, and in the one a reader is
  likeliest to lift rows from. It also carried no `GID`, so a wing row was the only one
  that could not be tied to the card that carries it.

- **The single-owner constant guard read a glyph width as the dynamic-pressure divisor
  (tier S, 2026-09-07).** `\b295\b` treats a decimal point as a word boundary, so it
  matched the `295` inside `6.295`. Every literal in that guard now has to *start* a
  number rather than be a run of digits taken out of the middle of one.
