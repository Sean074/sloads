- **Benchmark-first gets its presence guard (#186, review R-16, tier S, 2026-09-15).**
  `CLAUDE.md` rule 2 makes an oracle test (±0.1 %, page-cited) or a stated
  physics-closure gate the definition of done for every module, and until now
  nothing asserted a registered module *had* one: a module could register, run in
  the front end and ship with no gate at all while the suite stayed green.
  `tests/module_gates.py` is the manifest — one row per registered module giving
  its kind (`ORACLE` / `CLOSURE`), its gate test functions and either the printed
  source or the invariant it closes on — and `tests/test_module_gates.py` walks
  `registry.available()` against it. Six ways to fail, each verified to bite: a
  module that registers without a row, a row whose module stopped registering, a
  gate naming a test that no longer exists, an oracle whose cited page appears
  nowhere in its test file, a closure that states no invariant or whose test file
  stops saying why no printed oracle exists, and an unknown kind. All 23 modules
  are covered — 18 oracle-locked against Appendix A (or Ch 9's hand-calc, which
  is BALLOADS' only printed figure), 5 closure-locked because no printed figure
  exists for them: `balance`, `body_loads`, `configuration`, `one_engine_out` and
  `tail_span`. `20_theory/00_theory_sources.md`'s Oracle-status section stays
  normative and now names its machine-readable half, which a guard holds in place.
