- **`concept_heavy`'s drag polar re-entered with its minimum at the wing's zero-alpha lift coefficient (#291, tier S, 2026-09-20).**
  The fixture's `CD = 0.025 + 0.05·CL²` had its minimum at `CL = 0` on a wing whose
  lift fit reads `CL = 0.3` at zero alpha, so at negative CL the airplane-less-tail
  polar under-read the drag and the non-wing axial force came out forward inside the
  polar's trusted window on the NMAA case note 62 narrowed to the VC pair (dCD
  +0.0169, note 62 §8.3). Re-entered as `CD = 0.0295 − 0.03·CL + 0.05·CL²`, the same
  quadratic with its minimum moved, NMAA reads −0.0039 and every heavy case inside
  the window is negative, so `tests/test_balance.py::_DELTA_CD_FORWARD_INSIDE_WINDOW`
  is empty again; the heavy's dCD band, clamp ceilings and residual ratchets are
  re-pinned with the cause stated (symmetric force worst 1.99 % → 1.21 %, pitch
  0.84 % → 0.52 %; NHAA still clamps outside the window). Fixture data only, no
  physics or schema change; the heavy's sixteen digest channels regenerated.
