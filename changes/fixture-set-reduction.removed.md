- **`cessna_210` and `dhc8_dash8` retire from the bundled example set (#264,
  tier M, 2026-09-11).** Owner ruling from the 2026-09-10 scope-reduction
  review: GA-single (`ga6_normal`), closure-locked-twin (`baron_58`) and
  ATR42-class (`atr42_100`) coverage is sufficient, with the two concept
  configurations kept; the two fixtures move to unmaintained parking outside
  the repository (recoverable from history at the `v0.8.2` tag). Full retire:
  both leave every CI matrix, parametrized fixture list, pinned baseline and
  sbeam digest (the Imperial baseline drops from six fixtures to four with
  **every surviving digest byte-identical**); fixture-specific tests re-pin to
  a surviving fixture or to a constructed case (the below-energy landing
  caution, the gear-carrier mistag guard, the no-balanced-case deck refusal);
  the GUI example listings, `README.md`, `GUI_USER_GUIDE.md`,
  `PROJECT_GUIDE.md` and `PROGRAM_SPEC.md` state the surviving five. The
  unfixable `cessna_210` engine/prop CG waterline defect (filed 2026-09-07,
  no printed page to correct it from) closes parked-with-fixture, and #216's
  `cessna_210` half goes with it.