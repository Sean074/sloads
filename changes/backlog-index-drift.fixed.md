- **The open-defects index loses two wrong issue numbers, a deleted body and
  three closed entries (backlog hygiene, tier S, 2026-09-11).** The 2026-09-08
  index tidy (`07b24e2`) collapsed the *Open defects* bodies to one-line
  `#N — title` stubs and assigned the numbers positionally, which mis-stapled
  two: **"No engine-mount case reaches the LRA deck"** — an unfiled 2026-09-07
  finding with a full body — became `#209`, which is the load-case index's
  blank-load-columns defect, and its body was deleted; **"Review 2026-09-04
  small items"** became `#16`, which is Dead code (CH-5), now a 0.8.3 row. The
  engine-mount body is restored verbatim with the number struck and the gap
  re-verified live (the `lra-engine` band still allocates grids at
  `bands.py:274`; `transferred_case_loads` still takes a `BalancedCaseResult`,
  so no 23.361/23.363/23.371(b) condition reaches the deck); the small-items
  entry is deleted as redundant — all six are rowed (#175, #176, #179, #180,
  #188) or closed (#178). Three closed entries leave under the removal rule:
  **#170** (with the stale `Pri 49` ordinal the rows-never-cite-ordinals rule
  bars), **#181** and **#182**, whose "close on GitHub" instruction is
  discharged. Notes 56 and 57 lose their stale band/ordinal citations
  (`band B4 Pri 29` → `band B4`; `#255 in band B4` → band B5).
