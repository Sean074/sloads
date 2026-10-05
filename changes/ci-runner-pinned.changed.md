- **CI runs on a pinned `ubuntu-24.04` image and on the Node 24 action majors (`actions/checkout@v5`, `actions/setup-python@v6`) in both workflows, and a guard refuses a floating runner or a Node 20 action (#363, tier S, 2026-10-04).**
  `ubuntu-latest` moves to Ubuntu 26 on 2026-10-19 with no commit in this
  repository to point at, so a red after that date could not be told from a
  code regression, and the first run on the new image would have been the
  0.8.9 release cut's push to `main`. The Node 20 runtime of `checkout@v4` and
  `setup-python@v5` is deprecated, and every run since the 0.8.8 cut carried
  the annotation. Moving the image is now a deliberate edit.
  `tests/test_ci_conformance.py` checks every workflow: every `runs-on` must
  be a pinned `ubuntu-NN.04`, and every action must be at or above its floor in
  a total per-action table, so an action added later has to be decided there.
  No calc or delivered output changes.
