- **The bundled example set reduces to five (#264, tier M, 2026-09-11)** — the
  2026-09-10 scope-reduction review's first ruling landed: `cessna_210` and
  `dhc8_dash8` retire to unmaintained parking outside the repository
  (recoverable at the `v0.8.2` tag), since `ga6_normal`, `baron_58`,
  `atr42_100` and the two concept configurations carry every coverage class
  the mission names (GA single, closure-locked FAR 23 twin, ATR42-class
  turboprop, >12.5k concept, T-tail jet). The retire is full — CI matrices,
  parametrized lists, pinned baselines and sbeam digests all shrink to the
  surviving set, and the Imperial baseline regeneration proved every surviving
  digest byte-identical, so no delivered load moved. Where a retired fixture
  was a role's only exerciser the test re-pinned to a surviving fixture or a
  constructed case (below-energy landing caution from `ga6_normal` at N=2.90;
  gear-carrier mistag from `atr42_100` with a wing-carried leg; the
  VD-governed-by-`K_d·VCmin` branch is recorded as unexercised on shipped
  data). Sequenced deliberately ahead of the #164 baseline-regeneration wave
  so that wave regenerates four fixtures, not six. The `cessna_210` engine/prop
  CG waterline defect (2026-09-07, unfixable without the airplane's own data)
  closes parked-with-fixture; #216 narrows to its `baron_58`/RJ halves.