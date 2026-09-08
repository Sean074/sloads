- **ONENGOUT fails every engine, not the selected one (note 44 OR-173, tier L,
  2026-09-07).** One engine's failure loads the fin in one sense; a fin is sized
  for both. Each entered engine whose failure produces a yawing moment is now
  marched in turn and carries its own case ID and its own sign. No case is a
  mirror of another — on an asymmetric installation the marches genuinely
  differ. `failed_engine_index` remains the selector for the single-case views.
- **An uncontrollable case is printed and excluded from the envelope (OR-174).**
  Where the march reaches its 60 s bound without recovering, the case is
  reported in full with the uncontrollability statement and a referral to the
  stability-and-control discipline, and it reaches no critical set, no
  distribution, no appendix and no deck. A load at the simulation bound is where
  the integration stopped, not a design load. On `atr42_100` and `dhc8_dash8`
  that is the VS case on both engines.
- **The already-ultimate basis rule gets one owner (`safety_factors.shared_basis_factor`).**
  Admitting 23.367(a)(2) — which the regulation prescribes ULTIMATE at SF 1.0 —
  to the fin's set makes the v-tail files *mixed*: one ultimate row among limit
  ones. A mixed file keeps plain load columns and states the basis per row in
  its `SF` cell; only an all-ultimate file carries `-ULT` (note 49 OR-118a). The
  rule was written in `report.render` and merely *assumed* in
  `export.sbeam_bridge`; both now read the one owner, and the methods stamp
  states the mixed-file case in as many words.
