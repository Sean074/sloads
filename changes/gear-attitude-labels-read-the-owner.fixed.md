- **Section 12's attitude labels were swapped between families, and its case-range claim overlapped (#227, 2026-09-08 review R1/R2, tier S, 2026-09-08).**
  The Ground load conditions table labelled the tail-down landings (cases
  13–24) "Ground roll and handling" and the ground-roll cases 7–9 "Tail-down
  landing": `_ground_cases` indexed `_GROUND_ATTITUDES` by tuple *position*
  with `attitude_of`'s ground-angle index, and that tuple is deliberately not
  in gra order — its gra-index lives in its own third element, which the
  (correct) figures read. The loads themselves were verified right; only the
  label picked the wrong geometry for the reader. The title is now matched on
  the gra-index element. The strut-state table's second defect: it printed
  each geometry's cases as `min-max`, so the level attitude's 1–6 and 10–12
  became "1-12", claiming 7–9 at two ground angles at once — it now prints
  the exact runs through `_case_range_words`. Two G-OR-128 extension gates
  read both printed columns back against `attitude_of` and the free body,
  case by case, on every shipped example (rule 3: the owner existed, the
  consumer bypassed it).
