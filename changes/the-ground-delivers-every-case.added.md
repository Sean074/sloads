- **Section 12, Landing Gear Loads — the analysis body is complete (design note 44 §22, tier L, 2026-09-07).**
  The oracle report's last derived section, and the first since Section 2 that all
  three shipped reports carry. Three subsections: the gear geometry with the
  manual's own `K` / `GAMMA` / ground-angle / `AP`-`BP`-`DP`-`CP` lever-arm table
  (Appendix A p230, reproduced to the printed figures), the LGFACTOR load factor
  with the drop-test estimate printed beside the pair the reactions ran at, and
  every one of the 33 FAR Part 23 ground conditions. `IMPLEMENTED` now covers the
  whole of `analysis_steps()`.
- **Appendix F — landing gear loads by case (OR-188).** The gear's applied set:
  one row per case per loaded leg, all 33 conditions, at the point that case's
  reaction acts at — the axle or the ground contact point, per design note 39's
  own owner. The first appendix indexed by case rather than by station.
- **Three ground-attitude figures (OR-189).** Appendix A prints two (p234's
  three-wheel level landing, p235's braked roll); sloads computes three
  attitudes, so the third is drawn. Each carries its ground angle, its axle
  state, the wheels at their contact patches and the CG the lever arms are taken
  about — and, which the manual leaves to the reader, the LANDLOAD cases that use
  that geometry: 1-6 and 10-12 level, 7-9 tail-down, 13-33 ground roll.
- **An applied-load CSV for every structural element (OR-186).** The landing gear
  and the engine mount join the wing, fuselage and both tails: `case`, load
  application point, all six components in the global frame, and `SF`, each file
  free to carry the columns its element needs beside the common spine.
