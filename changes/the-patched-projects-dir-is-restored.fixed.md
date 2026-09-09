- **A test's monkeypatch of `io.default_projects_dir` leaked into later tests
  (tier S, 2026-09-08).** `tests/test_app_shell.py`'s `_NAMED_SCRIPT` (the
  #65/PB-6 save tests) replaced `sloads.io.default_projects_dir` with a lambda
  returning the test's `tmp_path` and never put it back — the same script's
  `try/finally` restored `st.download_button` but not this. Streamlit's
  `AppTest` runs the script in the test process, so the patch survived for the
  rest of the xdist worker's life, and whenever the scheduler later placed
  `test_io.py::test_default_projects_dir_is_repo_relative` on that worker it
  read the leaked temp dir: the CI failures on the #234/#235/#236 pushes
  (`assert 'test_open_re...' == 'projects'`), green locally only because the
  scheduling differs. The original is now captured before the patch and
  restored in the same `finally`. Proven by running the polluting and polluted
  tests in one process: fails without the restore, passes with it. The sweep
  found no other unrestored module-attribute patch in the test tree.
