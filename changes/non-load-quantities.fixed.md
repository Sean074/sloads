- **A machine rating in load units is no longer a load (#170, review R-8, tier M, 2026-09-09).**
  `units.is_load_unit` decided what a safety factor may be stated for by testing the
  **unit string alone**, so an engine's own torque rating read as a structural load:
  ENGLOADS published GA-6's mean takeoff torque as 554.4 ft-lb and the ULTIMATE channel
  stated it as 831.6, a number with no meaning — 14 CFR 23.303's factor belongs to the
  *design* torque the same condition publishes beside it, not to a powerplant rating.
  `units.NON_LOAD_QUANTITIES` is now the owner of that distinction, and the producer has
  the last word: `"mass"` (unchanged), plus `"characteristic"` for an engine rating and
  `"diagnostic"` for `balance`'s pre-closure residual. Five quantities across two modules
  leave the class — `mean_takeoff_torque` (23.361(a)(1) and the turboprop (a)(3)),
  `max_continuous_torque` (23.361(a)(2)), `max_accelerating_torque` (25.361(a)(3)(ii)),
  `balanced_residual_fz` and `balanced_residual_my` — each losing its `SF` cell and its
  `-ULT` eligibility while the `mx_mount_torque`, the gyroscopic couples and the applied
  loads of the same conditions keep both. The class was swept, not the filed row: review
  R-8 found it three rows wide on the engine side and two more in the balance residuals.
  No load value changes anywhere. `CONVENTIONS.md`'s "Loads only" rule names the
  vocabulary; guards in `tests/test_safety_factors.py` pin the discrimination both ways on
  every fixture, assert every key of the class is actually reached, reject a `quantity`
  hint outside the owner's vocabulary, and check the delivered row itself — the rating's
  `SF` cell empty, the mount torque's filled, in one condition.
  The frozen Imperial baseline was regenerated deliberately and moved in **6 of 330**
  digests — `csv/balance` on each example, the 176 pre-closure residual rows whose `SF`
  cell is now blank like the percentage rows beside them; the 104 applied-load rows of the
  same files keep `1.5`, and no deck, report or load-case CSV byte moved.
