- **Both failed engines printed at the same butt line, and "Engine 1" meant a different engine per page (#231, 2026-09-08 review R7, tier S, 2026-09-08).**
  §11's input table printed `bleng` — the march's magnitude — so the Baron's
  two rows both said +1676 mm while the section's own footnote explains that
  which side failed sets the fin-load sign; the signed butt line is now
  recovered through the module's own side owner (`-sense × bleng`) and the
  note states the convention. The identity flip — §10 "Engine 1/Engine 2",
  §11 "engine 0/engine 1" — is settled 1-based with one owner per layer:
  `_engine_label` in `one_engine_out.py` now mints " (engine 1)" into the
  case names, and the published condition note's "Failed engine #0 at butt
  line 66 in" — 0-based and unsigned in one breath — states the 1-based
  number and the signed butt line (OR-15 admission granted 2026-09-08,
  scoped to those two sites),
  and §11's tables, figure titles and exclusion prose print through a single
  `_oei_engine_number` owner. Guards: the input table's butt lines equal the
  side owner's signed values on the Baron, §10 and §11 name the same engine
  by the same number with the same designation, the case names carry
  "(engine 1)/(engine 2)", and "engine 0" appears nowhere in the rendered
  document. The OR-13 manifest records the admission against the new hash,
  and the Imperial baseline is regenerated for the label-only drift in the
  twins' case names.
