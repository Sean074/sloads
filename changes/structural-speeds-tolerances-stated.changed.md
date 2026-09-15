- **Every `test_structural_speeds` assertion holds at ±0.1 %, or says on its own
  line why it cannot (#175, review R-4, tier S, 2026-09-15).** Five assertions sat
  at 2e-3…1e-2 in a file headed "matched within ±0.1 % per Decision 3", with
  nothing recording whether the width was a rounding limit or an unexamined
  disagreement — a passing assertion keeps no margin, so the reason is not
  recoverable afterwards. Three were simply loose and now hold at `TOL`: the GA6
  wing loading (1.7e-4 — the manual's hand area 2·13257/144 = 184.125 against
  WINGGEOM's polygon 184.157), VC(min) 141.8 kt (3.9e-5) and the regional jet's
  Mach margin 0.09728 (9.7e-5). MC/MD at the 12 000 ft shoulder are genuinely
  rounding-limited — the manual prints three decimals, so ±0.0005 is ±0.15 % at
  MC 0.323 and ±0.1 % is finer than the oracle resolves — and are now asserted as
  agreement *to the printed precision* (`round(value, 3) == 0.323`), which is both
  tighter than the 3e-3 band it replaces and self-explaining. The file's docstring
  states the rule for the next assertion added to it.
