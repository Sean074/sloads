- **The fuselage beam states where its mass is and where the beam runs (schema
  v62, tier L, 2026-09-07).** `FuselageStation` gains `y`/`z`, the butt line and
  waterline the lumped mass acts at, blank-deriving from the weight-weighted
  centroid of the item-database masses lumped at that station. They are a
  different statement from `FuselageMassInput.ref_waterline`, which is where the
  *beam* runs: on `ga6_normal` the body mass spans waterline 52 to 105 about a
  beam at 87.7. Chapter 15 solves the body as a symmetric-flight vertical beam
  and reads neither coordinate — only the station enters its shear and bending —
  so no delivered fuselage load moves across the hop, which is additive and
  loads a v61 file bit-identical.

- **Section 4.1 draws the airplane in side view (tier L, 2026-09-07).** A station
  table answers *how much, where along the body*; it cannot answer *does this
  look like the airplane*. The figure is in the X–Z plane — the plane Chapter 15
  solves in — and carries the three things a reader checks a beam against: each
  station's mass at the waterline it acts at, labelled with that mass; the beam
  those masses are carried on; and the stations the load enters and leaves at,
  the wing carry-through's two spars and the horizontal tail's balancing load.
  Table 21 gains Y and Z beside the weight, and says which of them the analysis
  reads.

- **The case reference is the identity in every fuselage and tail table (tier M,
  2026-09-07).** The pull-up, wing-attach and tail tables drop their
  condition-name columns: `F-01` and `HT-01` are the machine identity (M4-9), and
  the name and its regulation are stated once in each section's register rather
  than repeated in four tables. The tail register gains the safety factor, so the
  factor is stated wherever a case is named.

- **Appendix C places every station on the airplane (tier M, 2026-09-07).** `X`,
  `Y` and `Z` on every row: the body beam runs down the centre plane on the
  fuselage loads reference axis, so `Y` is zero by construction and `Z` is that
  axis's waterline — the position of the structure, not of the mass it carries,
  which the beam table states separately.
