- **The mass tolerances are read through their owners, the FAR 23 exceedance line states its unit, §2.2 groups its checks by a field, and the one-engine-out yaw figure is signed like the fin load beside it (#321, tier S, 2026-10-01).**
  The remainder of the 0.8.7 review's calc-side minors; the engine items rode
  #319 and the rolling/select items #320. `validation` rebuilt the entered-loading
  weight band from `mass_distribution`'s two private halves and read its private
  `_CG_MATCH_TOL`, the owner did the same inside `case_loading_checks`, and the
  oracle report imported `_ECHO_WEIGHT_REL` to print "0.1 %": all now call
  `echo_weight_tolerance()`, `cg_match_tolerance()` and the new
  `echo_weight_rel()`, and `tests/test_mass_distribution.py` refuses any module
  outside the owner that reads one of the private names. The mirror-pair test
  has its own `_MIRROR_POSITION_TOL` (0.5 in, the hand-entry resolution, owner
  2026-10-01) instead of borrowing the CG search's band. `Exceedance` carries
  its `dim`, and `report.methods.exceedance_statement` is the one wording the
  methods block and the GUI banner print: an SI file's comment block said
  `20,000 exceeds the limit of 12,500` with no unit and now says
  `9071.8 kg exceeds the limit of 5669.9 kg`; both note 65 exemptions are gone.
  That unit exposed a defect it had been hiding: `package_data.data_header`
  built each `data/` file's methods block without the document's system, so
  every file of an SI issue package stated `UNITS: Imperial (lb, in, lb-in,
  lb/in^2) throughout` above its SI numbers. It now passes `doc.system`, and
  `tests/test_si_artifacts.py` checks each file's `UNITS:` line in both systems
  (the leak scan reads numbers with a unit after them and could not see it).
  `MassCheck.case` names the case a per-case check is about, so §2.2 no longer
  `rsplit`-parses the display string. The OEI yaw figure drew the march's
  magnitudes beside a fin load signed by the failed engine's side; yaw angle and
  rate now read nose to port positive (SELECT's β) and the rudder in the sense
  that loads the fin `+y`, stated in the caption (owner option (a)). BALANCE
  passes its resolved envelope to `default_critical`. No delivered load moves.
