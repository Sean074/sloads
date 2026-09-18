## Step — The negative angle-of-attack wing slots and the load-factor-extreme pair, above SELECT.BAS (#288, design note 62 D-62.1…D-62.8, tier L, 2026-09-17)

**Objective.** Close the coverage gap note 62 measured: `SELECT.BAS` searches
three positive angle-of-attack slots and **one** negative, so whichever
negative point has the largest resultant is delivered and the other spar's
down-load case is discarded with nothing said, and because every slot picks
on air load the largest-magnitude load-factor points in the matrix (GA6
+5.25 g and −3.25 g at CG4, the case that sizes every wing-mounted mass)
reach no deliverable either. This is the #164 case-set ruling, taken in the
owner's rulings of note 62 §2 and its critical-advocate review the same day.

**Deliverables.** `select_wing` gains four slots after TORS: **NHAA**
(largest resultant among STALL −N / STALL −1G), **NLAA** (MAN −D / GUST −D),
**PNZ** (largest `nz` over every positive-family label, tie-break largest
resultant) and **NNZ** (most negative `nz` over every negative-family label);
**NMAA** is narrowed to the VC pair MAN −C / GUST −C. A negative slot admits a
point only when the **wing's** lift is negative (`LZW < 0`) and PNZ only when
it is positive — the sign tested is the wing's, not the airplane's load factor
(D-62.2) — and a slot with no eligible point is **empty**, a gap in the W-
band; a PNZ/NNZ point another slot already delivers is not delivered twice
(D-62.8's coincidence rule, `case_ids` M4-2 decision 1). `WING_SLOTS` mints
W-07…W-10 for the four and nothing moves below them; all four join
`SYMMETRIC_WING_CONDITIONS`, so the LRA deck gains up to four symmetric
subcases; a slot on a non-derivable CG case is a `loading-not-derivable` skip
like the six before it (`baron_58` W-07/W-08/W-09, until #290 enters those
loadings). `PROGRAM_SPEC.md`'s SELECT section and case-id rule,
`ch04_wing_loads.md`'s table and `theory_sources.md`'s SELECT row state the
four; `CONVENTIONS.md` states the residual scale's 1 g floor (below). One
Imperial digest wave: `select`, `balance`, the balanced and LRA decks and the
case index moved on every fixture; `net_loads`, `wing_inertia` and `airloads`
moved on none, because every fixture enters `wing_mass.cases` by hand
(D-62.7).

**Test.** Gate 1: the six Appendix A picks are the same points on the same
figures (`test_critical_wing_conditions_match_appendix_a`, unchanged
tolerances). **G-62.1** asserts the invariants on every fixture — membership,
wing-lift sign, largest resultant among the eligible, empty-when-ineligible,
the load-factor extremes, the coincidence rule, one V-n case under one wing id.
**G-62.2** freezes every fixture's pick by name (label, load factor, speed,
CG case, altitude, resultant), so #164's V-n renumber cannot move it.
**G-62.3** (`test_balance.py`) asserts each non-empty slot is assembled
symmetric and unhanded or is in the skip record as `loading-not-derivable`,
and names the Baron's three. **G-62.4** pins W-07…W-10 and the gaps. The
report's per-label run register is extended to the ten GA6 slots.

**Key decisions.**

- **NMAA moves on the heavy as well as the ATR.** The AGREED text said the
  narrowing returns the same point on every fixture but the ATR; on
  `concept_heavy` the `.BAS`'s NMAA was the STALL −N point too (case 8, R
  32,463 against MAN −C's 32,367), which is NHAA's now. Note 62 §8 corrects
  gate 1 and G-62.2's heavy PNZ cell (it coincides with PHAA, not PMAA: the
  three 4.0 g manoeuvre points tie on `nz` and MAN A has the largest
  resultant).
- **The residual gate's scale floors at 1 g** (`BalancedCaseResult.gate_load_factor`).
  The heavy's NLAA is a −0.024 g VD gust; its pre-closure residual against
  `n·W` read 31 % force / 13 % pitch, and 0.75 % / 0.32 % against the
  airplane's weight — the loads the case actually carries, since a near-0 g
  case still balances a weight of lift against a weight of inertia and the
  *net* is what is near zero. Every case above 1 g is unchanged; the relief
  fraction reads the same owner.
- **A fixture defect is recorded, not excused.** The heavy's new NMAA sits at
  alpha −9.8°, 0.2° inside the polar's trusted window, with a forward
  non-wing axial force (dCD +0.0169) — the point the old NMAA occupied was
  outside the window and clamped. The sign gate is right to call it a
  fixture aero-data defect in the heavy's crude polar; it is recorded with
  its number in `_DELTA_CD_FORWARD_INSIDE_WINDOW`, asserted both ways, and
  the fixture's polar is the fix (#291).
- **Ratchets and clamps re-pinned with the cause stated.** NHAA clamps on
  the ATR, the RJ and the heavy (stall-line alpha −12.8 / −18.7 / −14.3°);
  the ATR's new NMAA at 25,000 ft still clamps; NLAA's force residual is the
  largest symmetric one on the GA6 (1.15 %) and the RJ (1.16 %), a VD gust
  at small negative load factor where the tail load is a larger share of the
  balance, inside the 2.5 % acceptance with pitch at a tenth of its gate;
  the ATR's "min weight" case assembles for the first time and its closure
  Izz is pinned.
