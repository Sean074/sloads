- **The oracle reduction keeps each case's mass state: the `consumable` flag and an entered `loading` survive it, so the oracle report names the loading the analysis flew and a loading edit moves its fingerprint (#221, tier M, 2026-09-26)** —
  `field_registry.reduce_to_oracle_inputs`, which the oracle document and its
  fingerprint are built from, reset every field outside the oracle input set,
  and the loading model is sloads-only: every tank read as payload and every
  entered loading was replaced by a search. Measured on `atr42_100` before the
  fix: fuel 9,874 → 0 lb at MTOW and 700 → 0 at MZFW on all eleven cases,
  eight entered loadings searched instead, and the search adding up to
  1,669 lb of ballast the airplane does not carry; all five fixtures moved.
  Wing loads did not (total weight, CG and wing mass are unchanged) — the
  defect was in what the document states. The fix is a new registry
  declaration, `KEPT_BY_REDUCTION`, each entry with its reason, which the
  reduction honours and the GUI tiers and the supplied-set dial do not see
  (`supplied` was rejected: it would render the fields as original-suite
  inputs, and no Appendix A oracle depends on them). One reduction serves G5
  and the document alike. The G5 module comparison could not see the defect
  (fuel reclassified as payload moves no oracle-page value), so the guard
  compares the mass state itself — `mass_case_summary` equal on the full and
  reduced project for every shipped example — and the test that asserted the
  loading was dropped now asserts it is kept. The backlog row's `carriage` was
  already `supplied` (design note 63). MZFW and crew were swept and stay
  plain: they seed and check cases, and state no case's mass.
