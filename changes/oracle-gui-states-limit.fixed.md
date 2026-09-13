- **The oracle GUI's results captions state LIMIT, and the GUI-source sweep has one owner (#239, note 60 §5, tier S, 2026-09-13).**
  `oracle_app/results.py` captioned every load-case table *"ULTIMATE loads (= limit x
  the case safety factor)"* over bytes that had been LIMIT since note 48 and were
  gated as LIMIT by G7 the whole time — the understrength direction, and the second
  front-end's half of #192. The caption is now the sentence `app/views/results_review.py`
  already carried: load columns LIMIT, the `SF` column stating the 14 CFR 23.303 factor
  the tool applies nowhere, and the `-ULT` marker only on a load the regulation already
  prescribes ultimate (23.367(a)(2), 23.561(b)).
- **The `ResultBlock` basis discriminator is retired with the claim it carried.**
  Since note 49 OR-116 there is one basis, so `ULTIMATE`/`LIMIT` are replaced by
  `CASE_TABLE`/`STATION_TABLE` — a block now selects its caption by the *shape* of its
  table (per-case `SF` column vs. station `Basis` column), which is the thing that
  actually still varies, and no value exists that could claim ULTIMATE again.
- **G-OR-74's screen sweep covers the oracle GUI.** `tests/test_basis_statements.py`
  excluded `oracle_app/` as a tree under note 44's OR-13 freeze, sweeping only
  `oracle_app/report.py` by name; the freeze lifted with 0.8.2 and the exclusion did
  not, which is why the false caption ran green beside the gate for a whole milestone.
  779 further literals are now in scope. Design note 57's gates 4 and 5 are asserted
  through this sweep, so #266 can depend on it.
- **`_GUI_TREES` converges on one owner** (`tests/helpers.GUI_TREES`, rule 4 / practice 3,
  note 60 §3). `test_basis_statements.py` and `test_app_shell.py` each kept a tuple of
  their own and disagreed about what "the GUI" is; a guard can no longer narrow its own
  scope without editing the owner every other guard reads. The shared tuple walks `app`
  whole rather than `app/views`, so `app/Home.py` is swept too.
