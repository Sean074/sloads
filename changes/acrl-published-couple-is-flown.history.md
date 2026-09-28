- **The accelerated roll's published couple is the one flown: the variant table resolves ACRL through the same owner as the wing chain and the balanced deck, so an entered unbalanced rolling moment reaches SELECT, report 3.3 and the Wing Loads caption (#315, tier M, 2026-09-27)** —
  The wing chain and the balanced deck resolve the ACRL case through
  `rolling.complete_rolling_case`, where an entered `unbal_moment`, `cl` or
  `v_eas_kt` wins over the condition A derivation (design note 52). The
  `wing_variants` table derived all three regardless, and SELECT publishes
  the governing row, so the regional jet flew its entered -600,000 lb-in
  while SELECT and report 3.3 published the derived -1,614,422 lb-in and a
  roll acceleration built from it. The table now resolves each ACRL row
  through `complete_rolling_case`, with the entered case named by the new
  `rolling.entered_rolling_case`. The row records which fields were entered
  and keeps condition A's CL, speed and root bending as separate fields.
  SELECT labels an entered couple *(entered)* and publishes an entered air
  point beside condition A's. Report 3.3 names the entered value and states
  the derivation for comparison, and the GUI caption decides entered versus
  derived from the input instead of comparing numbers. On the regional jet
  every ACRL row's net root bending rises by about 480,000 lb-in (less roll
  relief), the governing row is unchanged (fwd gross, case 180), and so is
  every delivered wing and deck load; the other four fixtures enter no
  couple and do not move. The Imperial baseline moves on the regional jet's
  SELECT CSV and text report alone, and the digest is regenerated. A gate
  in `tests/test_rolling_conditions.py` holds SELECT's published couple to
  the wing chain's and the balanced deck's on every fixture.
