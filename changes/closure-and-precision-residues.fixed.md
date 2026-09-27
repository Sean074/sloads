- **The residues of #293 and #161: a self-inertia relief names its own carrier, a NaN or an infinity is refused rather than printed or swallowed, the precision floor is stated as it works, and the SI deck's ASSUMED coordinates carry their unit (#303, tier S, 2026-09-26).**
  A `closure-self` relief found its carrier by matching its station against
  the mass loads, so an item entered with an inertia and no weight matched
  nothing and landed on the nearest grid of the whole skeleton;
  `point_mass_self_inertia` now hands over each item's carrier and side (the
  body-inertia load's, one constant `BODY_INERTIA_SOURCE` for both). No shipped
  fixture had such an item: `ga6_normal`'s 406 reliefs all reached the
  fuselage before and after. `format_value` raises `NonFiniteValue` for a
  NaN or an infinity, where a NaN failed inside the quantization and an
  infinity printed `inf`. The baseline's `_try` skips only a missing input
  slice or an LRA refusal, the only two it met, instead of any `ValueError`,
  so a NaN can no longer drop a channel from the digest without a word.
  `select._air_mxx` raises on a miss instead of returning a NaN into the
  net-governing note. The floor's words said "a cell that would print as
  `0`"; the code tests the magnitude against one unit of the row's last
  decimal, so a 0.7 lb cell prints `0.7000`. The words were corrected in
  `units.py`, `format_value`'s docstring (which still said three figures),
  note 65 §7b and `CONVENTIONS.md`. Changing the code instead would have
  rounded ~70 cells across all five fixtures to a figure they do not have (a
  0.5682 slug-ft² rotor inertia as `1`). 3.2's variant register and wing mass
  sentence no longer sit behind `except Exception`: the register prints the
  variant table's own reason when it is empty (its `type: ignore` went with a
  typed `envelope`), and the mass sentence states a `WingAsymmetric` or
  missing-input refusal by name. The side-of-body, fuselage centre line, wing
  station and spar-station ASSUMED sentences state `in`, which the mm deck
  printed bare. The Imperial baseline moved on `sbeam/lra_model` for
  `baron_58`, `ga6_normal` and `concept_regional_jet`, in comment lines only,
  and was regenerated. The centreline half-weight copy this row also named
  was removed at #301.
