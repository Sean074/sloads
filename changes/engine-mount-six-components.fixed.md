- **`ga6_normal`'s engine and propeller CG waterlines are corrected against
  Appendix A p227 (note 44 §20 OR-170, tier L, 2026-09-07).** The fixture entered
  `engine_cg = (22, 0, −10)` and `prop_cg = (−10, 0, 93.022)`, putting the worked
  example's engine at waterline −10 and its combined CG at **3.166** where the
  page prints **93.022**. Reading the page's input block back gives
  `ENGINE CG 22, 0, 92` and `PROPELLER CG −10, 0, 100`, which reproduce the
  printed combined CG exactly — the propeller's `x` had been pasted into the
  engine's `z`, and the printed *combined* `z` into the propeller's. The fixture
  comment recorded that only `x` was ever checked, and no test asserted `zpp`;
  one does now. The deck's `lra-engine-mount` and `lra-engine-hub` nodes move
  with it, so the Imperial baseline digests are regenerated.

- **A FAR 25 gyroscopic condition no longer loses its four sign combinations.**
  `report.render.load_cases_to_rows` fanned out a gyroscopic condition by
  matching its FAR **reference** against `23.371(b)`, so `25.371` — which packs
  the same four sub-cases under a different reference — printed a single row with
  no moments in it at all, on the Engine Mount page's load-case file. The
  question "does this condition fan out?" is now asked of the **keys** the
  sub-cases are carried in, which is what identifies them.

- **A report section that discovers its own absence renders it.** A builder that
  returned a stated absence — because a module declined to produce a result from
  slices the plan had found populated — had that sentence dropped, leaving a
  numbered heading with nothing under it. It now renders through the ABSENT
  state's own lead, so a builder cannot word absence a second way. The hole was
  under every builder that returns one, sections 7, 8 and 9 included.
