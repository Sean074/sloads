- **A refused input is now stated as a refusal: a broken wing is no longer reported as a missing one, the flap gust factor's fallback to NG = 0 is warned and stated, and the report says when entered inputs were refused (#361, tier S, 2026-10-04).**
  The #344 sweep found four places where a refusal was reported as a different
  fact. `derived_geometry.require_wing_reference` now re-raises an
  unintegrable planform's own `ValueError`, so the user sees "needs >= 2 LE and
  TE points", not "add the surface". It raises `MissingInputError` only for a
  wing that is not there. A blank flap `gust_load_factor` that the flight
  envelope cannot derive still stands at 0. That makes the 23.345 gust at VF
  condition non-critical, and it is now stated: `flap.ng_fallback_reason`
  names why (from `flight_envelope.gust_at_vf_absence`, the same walk as the
  derivation), the flap result's note says so, and `validation` warns
  `flap_ng_fallback`. Only `atr42_100` falls back, and only its flap note text
  changes. Its 2g condition at VF governs the critical flap load at NG = 0 and
  at the 1.64 estimated from its flaps-up slope alike, so no delivered load
  moves (owner ruling (a): state the fallback, change no data). Three groups of
  report sections now quote a refusal in the #316 `REFUSED_REASON` shape, in
  place of a false "not entered": the tail chordwise, spanwise and station
  appendix; the aileron, flap and tab sections; and Appendix A. Appendix A
  also says whether the flight envelope refused or only the critical-condition
  selection did. The 2.2 case-loading and envelope-reach statements state a
  refusal instead of vanishing. Gate: `tests/test_refusals_stated.py`. The
  Imperial baseline moves on one channel, `atr42_100` `txt/flap`.
