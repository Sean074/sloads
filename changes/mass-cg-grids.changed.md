- **Every `CONM2` sits on its own `GRID` at its own item's CG (note 56 D-56.6,
  tier M, 2026-09-12).** A mass card used to hang on the nearest fuselage beam
  station and carry `x1/x2/x3` back to the item's true position. It now has a
  grid of its own, at that position, with a **zero** offset — so the mass model
  is self-contained and states no attachment it does not have. The wing-item
  limitation retires with it: a wing mass is at the wing mass's position, not on
  a fuselage node with a caption explaining why.
- **The grids are unconnected by design, and the deck says so.** sloads ships no
  tie, so a stiffness solve over the mass model is singular. The header names the
  condition, the reason, and the remedy (an `RBE2` per grid) rather than letting
  a reader discover it by running one. The placeholder massless beam and its
  `SPC1` are deleted — nothing is left for them to support.
- **The mass model is checked by a grid-point weight recovery, not by a solve**
  (D-56.7). `inertia_only_cards`, `case_station_weights` and
  `roundtrip.flatten_mass_case` are retired: they cross-checked sloads' reduction
  of a mass to a beam station, and there is no reduction left. sbeam's GPWG reads
  mass and CG off the deck **as shipped**, per payload case, in both unit
  systems. `--export-conm2` and the bundle now write two files, not three.
