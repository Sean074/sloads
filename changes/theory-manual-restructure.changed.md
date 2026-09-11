- **The theory documentation becomes a chaptered manual (tier S, 2026-09-10).**
  `docs/20_theory/` is restructured for an engineer reader: eleven `chNN_`
  chapters on one template (scope, cases analyzed, method, assumptions &
  limitations, worked example, validation, sources) beside the slimmed hub
  `00_theory_sources.md` (sources, oracle status, citation rules, provenance
  policy, per-module citations, chapter map). New chapters: introduction
  (ch01, incl. the two front-ends and the no-physics-in-front-ends
  invariant), illustrated conventions (ch02, four script-generated SVG
  figures — `scripts/render_theory_figures.py`, new), wing (ch04), empennage
  incl. one-engine-out (ch05), fuselage (ch06), ground (ch08) and mass model
  (ch10) — the last four as stubs with assumptions and validation populated
  first. Renames: `design_airspeeds.md` → `ch03_airspeeds_envelope.md`
  (+ a new V-n envelope / case-inventory section), `engine_loads.md` →
  `ch07_engine_loads.md`, `balanced_cases.md` → `ch09_balanced_airplane.md`
  (+ §11, the closure-gate record). The hub's concept-mode closure
  narratives moved into the chapters' validation sections with a pointer map
  left behind; `01_far25_gap_analysis.md` relocated to
  `docs/30_future/04_far25_gap_analysis.md` (a plan, not theory). Link sweep
  across `PROGRAM_SPEC.md`, the corrections register, `30_future/` notes,
  two test comments and `00_INDEX.md`; historic documents (`40_history/`,
  `50_reviews/`, `CHANGELOG.md`) keep the names of their day.
