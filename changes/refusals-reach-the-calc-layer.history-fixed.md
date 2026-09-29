- **A half-entered h-tail, landing gear or negative stall CL is refused by name instead of stopping the report with a bare ZeroDivisionError, and no handler in `sloads/` swallows a calc defect (#330, tier M, 2026-09-28)** —
  #316 narrowed the report's handlers to the two refusals, `MissingInputError`
  and a plain `ValueError`, and left two catch-alls outside its scope:
  `fleet._wtestima_value`, which turned any WTESTIMA failure into a quiet change
  of source on the fleet chart, and `validation`'s mass-state check, which
  dropped its warning on any exception. Measuring what the second one caught
  over the whole suite found two `ZeroDivisionError`s, and building the report
  over every Optional record the GUI can add, at its blank defaults, on all five
  examples found the rest: three divisors an input can zero, each raising a bare
  `ZeroDivisionError` — SELECT's rational h-tail balance on a freshly added
  h-tail record (elevator effectiveness 0), LANDLOAD's ground angle on a freshly
  added gear record (main and nose axles both at the datum), and the flight
  envelope's STALL −N / STALL −1G on a flaps-up set with no negative stall CL.
  Since #316 each stopped the whole report with a message that named nothing,
  where before it printed as an absent section. Each is now refused where it
  divides, by `MissingInputError` naming the field (`select.htail_balance`,
  `landing.ground_angles`, `flight_envelope.balance_configs`); no number moves
  on a valid project. `REFUSALS` moved from `report/render.py` to
  `sloads.models`, beside `MissingInputError`, because the calc layer never
  imports `report`; the two handlers catch it and nothing wider, and a defect in
  either now raises. `tests/test_report_absence.py`'s scan covers all of
  `sloads/`, with the registry's run-all and the three typing-introspection
  handlers exempted on their lines by `# broad-except: <reason>`, and a slow-lane
  sweep builds the document and package over every blank record. The rule — a
  divisor an input can zero is refused by name where it divides — is a row of
  `00_program_overview.md` §Error handling; the three refusals are stated in
  `PROGRAM_SPEC.md` under FLTLOADS, SELECT and LANDLOAD.
