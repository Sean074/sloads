- **The closures 0.8.7 left short are completed: note 66 has its theory citation and gate rows, note 63 records #301's symmetry rule, and no fragment describes the deleted `_hop_68` (#317, tier S, 2026-09-27).**
  Found by the 0.8.7 release review. `00_theory_sources.md` gains the design
  note 66 row for the engine-mount and one-engine-out deck families, and
  chapter 7's header says the deck carries them. `PROGRAM_SPEC.md` points at
  `safety_factors.py` in place of "1.5 on every family shipped to date",
  which #285's already-ultimate cases made wrong. It states the one-engine-out
  fin's published sense, and its FLTLOADS, SELECT and WINGINER sections point
  at the accelerated-roll paragraph. Note 66 amends D-66.16 with the trim-gate
  exemption, corrects D-66.13's engine 1 to hand L and defines G-66.14 to
  G-66.16. The OR-173 sign reversal is recorded the same way in note 44,
  note 66 §11 and the #285 fragment: the implemented sign was reversed, the
  one-case-per-engine rule stands, and the owner approved it in session on
  2026-09-26, after the fix had shipped. Note 63 gains §13, the laterally
  symmetric wing mass rule, which the #301 fragment, the code and the tests
  now cite in place of D-63.3.
  The `_hop_68` statements in the roll-conditions fragment, `project.py` and
  the schema guard now say no hop (v69 was never released, #310), and the
  fast-lane fragment drops its slow-test count. The #286 and #285 index rows
  leave the backlog. No output moves.
