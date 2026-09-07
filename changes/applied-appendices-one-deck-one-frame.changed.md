- **One column set for every applied appendix (note 44 §18 OR-139/OR-140/OR-141, tier L,
  2026-09-07).** B.1 (wing), C.1 (fuselage), D (horizontal tail) and E (vertical tail)
  print `Case | Station | GID | X | Y | Z | Fx | Fy | Fz | Mx | My | Mz | SF`, in
  airplane axes, right-handed about CID 0. A reader who has learnt one applied appendix
  has learnt all four, and a heading cannot drift between them because there is one
  place it is written. `AppliedLoad` gains a `component` and `applied_loads` becomes the
  one entry point with a producer per component, so the appendix, the CSV and the deck
  are three views of one list — four assemblers of one load set is what let D and E
  diverge from the deck unnoticed.

- **The structural zeros are printed, and the note names the producer each one lacks
  (note 44 §18 OR-140, tier L, 2026-09-07).** This supersedes OR-61, which omitted `Fy`
  from B.1 because "a column of zeros in a deck reads as a measured zero". The reasoning
  stands everywhere else and keeps its reach over the results tables; the remedy was
  wrong for an appendix that is a deck, whose reader is writing FORCE/MOMENT cards and
  cannot tell an omitted column from a zero one. The export channel had already ruled
  this way for the same data. Until now B.1 printed six components and explained the
  zeros while D and E omitted them and explained the omission: two policies for one
  question, one chapter apart.
