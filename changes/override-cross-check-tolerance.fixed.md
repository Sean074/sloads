- **An override cross-check warns only on a difference it can show: one owner judges the disagreement at the ±0.1 % band and the printed digits, and an exact-equality check prints its drift apart (#243, tier S, 2026-10-02).**
  The 2026-09-08 GUI review (G6) found the form's override warnings firing on
  any difference above `1e-9` and printing both numbers at four significant
  figures -- "This is 0.4356 but the paired planform's tip/centreline chord
  says 0.4356" -- and a 0.02 % aspect-ratio rounding flagged with the weight
  of a real data error. The new `sloads/cross_check.py` owns the comparison:
  `cross_check_disagrees` warns only past `CROSS_CHECK_REL` (0.1 %, the
  oracle band) **and** when the warning's own formatter prints the two
  differently. Both `oracle_app/form.py` warnings call it, and so, sweeping
  the class, do `validation`'s `aileron_deflection_mismatch` and
  `engine_mass_row_mismatch`, which compared at `1e-6` and printed at the
  unit's row. The two exact-equality checks, `landing_case_weight_is_mlw`
  (G-4) and `mtow_representation_drift` (G-14), still warn on any
  difference, but print through `shown_apart`, so a 0.4 lb drift reads
  `5000.0 lb ... 4999.6 lb` rather than `5000 lb ... 5000 lb`. The wing-area
  (5 %) and hinge-halves (1 %) checks keep their stated bands.
  `tests/test_cross_check.py` pins the review's pairs and walks both files'
  ASTs, refusing a near-zero `abs(a - b) >` test unless its function prints
  through `shown_apart`; `CONVENTIONS.md` §7 gains the owner's row. No
  delivered load moves.
