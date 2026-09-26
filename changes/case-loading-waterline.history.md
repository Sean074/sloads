- **A case's waterline is its loading's: a loading with no ballast counts as its case only within 0.5 in on station and waterline both, both seeds write back the waterline of the loading that closes each case, and `case_loading_checks` holds every case to that and is stated under the oracle report's 2.2 case table (#300, tier M, 2026-09-26)** —
  The subset search accepted a no-ballast loading (a subset that already
  weighs the case, or a ground case's fuel burn-down) on its station alone, so
  a loading could sit anywhere in waterline under a case whose `zcg` every
  balance, trim and gear module reads. The check meant to see that was wrong
  and unrouted: it held a no-ballast loading to 1e-9 — false failures on
  `ga6_normal`'s CG4 (0.0024 in, the very precedent the 0.5 in tolerance was
  written for) and `baron_58`'s `aft gross` xcg (0.35 in) — read flight cases
  only, and sat on `_UNSTATED_CHECKS` with no consumer. The search now tests
  both coordinates (`mass_distribution._cg_matches`); the check applies that
  band, covers ground cases, and is stated in the 2.2 case-table note, naming
  any case whose loading is not the case; `_UNSTATED_CHECKS` is empty. The
  sweep found the class three times. `baron_58` `aft gross` flew at 95.88
  against a stated 100.0 (4.12 in) and `concept_regional_jet` `fwd max
  landing` at 64.82 against 62.66 (2.16 in). And `cg_cases.seed_landing_cases`
  wrote every ground case's `zcg` as the whole database's waterline and never
  re-echoed it (D-26a), so the search solved ballast to reach that
  placeholder: 1,607 lb at the lowest item of `atr42_100` (z 60) under both
  max-landing cases, 1,946 lb near its top (z 218.7) under `fwd light`. Both
  seeds now share `cg_cases._echo_loading_waterlines` (search on station, write
  the found loading's waterline back); `derive_case_loadings(...,
  match_waterline=False)` exists for that step alone. Owner rulings: each case
  takes its loading's own waterline rather than a solved ballast the airplane
  does not carry — Baron `aft gross` 95.88, RJ ground 61.96 / 64.82 / 63.08,
  ATR ground 141.56 / 141.56 / 132.33; ATR's `aft max landing` ballast falls to
  1,007 lb at z 163.4 and the others move onto their loading's line. Delivered
  effect, three fixtures (`ga6_normal` and `concept_heavy` are byte-identical):
  Baron's governing horizontal-tail up-gust root bending 36,248 → 36,543 lb-in
  (+0.8 %), CHECKED MAN UP 13,398 → 12,926 (−3.5 %), the non-governing BAL UP
  RETRACTED 3,889 → 3,133; its one-engine-out pre-closure My residuals mostly
  fall now that the reference is the mass centre (VD −11,102 → 1,697, VC
  −7,055 → 95 lb-in) while VS rises to 0.7 % of n·W·MAC (−762 → −2,542). The
  critical nose-gear reactions rise 1.5 % on ATR (level landing Fz 21,918 →
  22,248 lb) and 1.2 % on the RJ (braked roll 8,752 → 8,859 lb); no flight,
  net or body load moves on either. The Imperial baseline was regenerated for
  those three (Baron 24 channels, ATR 8, RJ 8). Not in scope and unchanged:
  Baron's `fwd gross` and `fwd regardless` need 720 lb (13 %) of ballast, past
  the credibility gate, and reach no deck (filed as #309).
