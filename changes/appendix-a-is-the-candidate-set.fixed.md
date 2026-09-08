- **A V-n point selected by more than one condition kept only the last case id (design note 44 OR-200, tier L, 2026-09-07).**
  `select._stamp_case_refs` assigned `p.case_ref` per condition, so a point that
  is the source of several lost all but one: on `ga6_normal` V-n case 14 is
  `VT-01`, `VT-02` **and** `VT-03`, case 74 is `HT-03` and `HT-09`, case 30 is
  `W-03` and `F-01` — 4, 5 and 4 multiply-selected points on the three shipped
  examples. Nothing shipped was wrong, because the field had one writer and no
  reader outside serialisation; it is fixed at its first reader rather than
  ranked against the fidelity backlog. The stamp now appends, and clears first,
  so stamping one envelope twice is the same as stamping it once.
- **The register of decisions was missing a decision that shipped code cites.**
  `report/render.py`, the step-165 history fragment and backlog row 38 all cite
  "note 44 OR-193", but design note 44 defined only OR-183 … OR-192. OR-193 is
  now in the register, and **G-OR-137** sweeps every `OR-n`/`G-OR-n` cited
  anywhere under `sloads/`, `tests/`, `docs/` or `changes/` and requires each to
  be defined in a design note — the gate that would have caught it.
- **OR-193's own gate was a frozen digest, not a stated property.** Its docstring
  claimed the fix was gated; the only thing holding it was the Imperial baseline,
  which fails as a *changed number*, so a change that moved the engine locations
  and regenerated the baseline would have passed. **G-OR-138** asserts the
  property instead: every condition an engine emits sits at one point, and no two
  engines share it — verified to fail against the defect it names.
