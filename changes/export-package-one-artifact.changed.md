- **The export package closes on one solver artifact (design note 56, #263, tier L, 2026-09-12).**
  The tier-L closure of a ten-slice change. `sloads/export/` goes from **8,603
  lines across 15 modules to 5,307**; four parallel model concepts become two;
  `cli.EXPORT_TARGETS` goes from ten targets to three (`lra`, `gear`, `mass`).
  What ships to a solver is the **LRA beam model** of the whole free-free
  airplane, plus the **CONM2 mass model**. The five per-component decks are
  deleted, the elementless assembled deck no longer leaves the tool, and
  `sbeam_bridge.py` — which the oracle report reached into at seven sites — no
  longer exists: the applied-load model and the deliverable tables that were
  never decks are `report/applied.py` and `report/tables.py`.

  This entry closes the sweep rather than the code. `CONVENTIONS.md` §7 gains a
  row for D-56.3 (every `GRID` in a deliverable comes from one contiguous band
  that deliverable owns) and re-cuts the joint-register and
  skeleton-solvability rows — the latter named `JOINT_MERGE_FRACTION`, retired
  at D-56.4, and the floor that replaced it guards a different thing. Two §1
  conventions are **retired in place**, struck and explained rather than
  deleted: "a load that a free-body cut introduces is never applied in the
  assembled model" and E-2's per-component moment reference, both of which
  argued about artifacts that no longer exist. `PROGRAM_SPEC.md`'s artifact
  statement and its D-R5 bullet are re-cut — D-R5 named a guard deleted with
  the wing deck, and the rule it protected now holds by construction, one
  producer with every consumer a view of it. `PROJECT_GUIDE.md`'s
  frozen-baseline paragraph loses four wrong facts in one clause and gains one
  that was never stated: the Imperial baseline digests one **non**-deliverable,
  the assembled deck, because gate 13 checks the beam model's re-aggregated
  load set against its resultant. `docs/20_theory/ch11_export_sbeam.md` is
  swept under rule 4 — its two validation tables are kept as the record of
  gates written against retired artifacts, each saying what it now applies to.
