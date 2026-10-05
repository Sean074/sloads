- **The speed derivation is proved to refuse only by name, so the one-engine-out family cannot crash on a zero wing area (#365, tier S, 2026-10-04).**
  The 0.8.9 pre-release review asked whether the #344 narrowing of ONENGOUT's
  VS read to `MissingInputError` let a `ZeroDivisionError` escape to the deck
  build. It cannot: `design_speed_values` refuses a non-positive weight, the
  WINGGEOM integral refuses a degenerate or zero-area planform before it
  divides, `stall_speed_kt` refuses a negative typed area, and the atmosphere
  is positive at every altitude. The contract is stated on the function, the
  three dead `ZeroDivisionError` catches around it in `validation.py` are
  removed, and a guard test drives each degenerate area to its named refusal.
  No shipped fixture or delivered load moves.
