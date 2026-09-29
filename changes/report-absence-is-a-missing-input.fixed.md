- **A NaN or a calc defect no longer ships as an absent section or a missing package file, and a section the analysis refused says why instead of "not present" (#316, tier S, 2026-09-28).**
  Twenty-one handlers in `sloads/report/` caught `Exception` — `package_data.add()`
  and its two siblings, fourteen section helpers in `oracle_sections.py`,
  `run_sections` and the GUI's `figures.results_for_step` among them — and
  `NonFiniteValue` was a `ValueError`, so the ~30 handlers #303 had narrowed to
  `ValueError` could catch it too. A NaN bound for a delivered cell dropped its
  file from `data/` without a word, a calc defect printed as an absent section,
  and a section whose inputs were present but refused (a curve half entered, an
  area typed as zero) told its reader the inputs "are not present in the
  project". Now `report.render.REFUSALS` — `MissingInputError` and a plain
  `ValueError`, the two halves of the error contract — is the one owner of what
  a report or package path may read as an absence, and every one of the
  twenty-one catches it and nothing wider; a report built mid-entry keeps
  building (#71). A section absent by a `ValueError` states the module's own
  message after `oracle_content.REFUSED_REASON` (on `ga6_normal` with a
  one-point wing leading edge, sections 6.3, 7, 11, 12 and 16 now say so).
  `NonFiniteValue` derives from `Exception`, so no refusal handler can catch
  it, and the package build re-raises it naming the file; any other exception
  stops the build by name. The six "no … loads to export" raises in
  `report/applied.py` are `MissingInputError`, which is what they are, and
  `applied.py`'s guard around the total `fuselage_lra` is removed. Guard:
  `tests/test_report_absence.py` (no report or export handler can catch
  `NonFiniteValue`; a NaN stops the package naming the file; a refused input is
  stated; a `KeyError`, `ZeroDivisionError` or `NonFiniteValue` from a module is
  neither an absent file nor an absent section). No delivered byte moves on the
  shipped examples. The contract is stated in `00_program_overview.md` §Error
  handling.
