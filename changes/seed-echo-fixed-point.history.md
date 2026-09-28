- **A seeded case's waterline is a fixed point: with no waterline target the search puts a solved ballast on the candidate loading's own waterline, so the placeholder no longer chooses the loading and re-seeding returns the same `zcg` (#314, tier M, 2026-09-27)** —
  Both seeds search for the loading that closes each case on a placeholder
  waterline and write the found loading's waterline back (D-26a, #300).
  `match_waterline=False` dropped the waterline from the match test but
  still solved the ballast's waterline from the placeholder and rejected
  any ballast that fell outside the airframe, so the placeholder decided
  which candidates survived. ATR's `aft max landing` searched on WTONECG's
  137.93, lost its least-ballast loading to that filter, and seeded 141.56;
  the flown search at 141.56 then chose the least-ballast loading after all
  and closed it with 1,007 lb of ballast at waterline 163.4, 22.5 in above
  the rest of a loading at 140.93. `case_loading_checks` could not see it,
  because the ballast made the totals match. The ballast now sits at the
  candidate's own waterline when there is no target, so the seed's choice
  is independent of the placeholder and the flown search keeps it. Measured
  on every seeded case of every fixture, ATR's `aft max landing` is the only
  one that moves: its fixture `zcg` is 140.93 (amending the #300 ruling's
  141.56) with the same loading and ballast weight, the ballast at 140.8.
  The Imperial baseline moves for ATR only, and only on that case: the gear
  loads read the CG height, so its landing moments and gear reactions shift
  by 0.1-0.6 % (landing and balance CSV/TXT, gear report, applied gear CSV),
  and the balanced and LRA decks carry the ballast at 140.8 instead of
  163.4; the digest is regenerated. A guard in `tests/test_cg_cases.py` holds every
  seed of every fixture to its own re-echo and every solved ballast to its
  loading's waterline within the 0.5 in match band.
