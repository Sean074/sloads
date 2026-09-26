- **The balanced deck no longer rebuilds the V-n matrix and SELECT's set for every case it assembles (design note 66 follow-up, tier S, 2026-09-26).**
  Each case's wing set asked for the wing case list, and each ask rebuilt the
  envelope and the critical set from scratch; the engine-mount and
  one-engine-out families (#286, #285) doubled the asks, to 46 envelope builds
  for the ATR's deck. `build_balanced_cases` now threads the envelope and
  critical set it already resolved, and each engine-mount parent is assembled
  once per V-n point: the ATR's deck builds in 2.9 s against about 20 s, and
  every delivered byte is unchanged (the frozen Imperial baseline, 258
  channels).
