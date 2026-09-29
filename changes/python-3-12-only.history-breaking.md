- **sloads requires Python 3.12, and the developer's gate, every pull request and the push to `main` run that one interpreter (#327, tier M, 2026-09-28)** —
  The package declared `>=3.10`, a floor taken from streamlit (#132) rather
  than from anything the code needs, and CI carried 3.10/3.11 legs that ran
  only on the push to `main`, while the developer's `.venv` was 3.11 and every
  pull request and `dev/**` push ran 3.12. 0.8.7 paid for that split twice: a
  deck byte that differed between 3.11 and 3.12 kept `dev/v0.8.7`'s CI red
  from #286 to the cut while every local gate passed (#324), and a 3.11-only
  regex failed the 3.10 leg after the milestone had merged (#325). Now
  `requires-python` is `>=3.12`, the 3.10/3.11 classifiers are gone, and the
  `test` and `sbeam-roundtrip` jobs run `["3.12"]` on every event, so the push
  to `main` adds only the coverage measurement. `tests/test_ci_conformance.py`
  holds two new rules: a pull request runs every interpreter the push to `main`
  runs, and the suite fails when it runs on an interpreter the `ci.yml` `test`
  job does not, which makes a stale `.venv` one named failure instead of a
  gate that silently differs from CI. The asymmetry guard it replaces and the
  doc-wording check for the three-version list retire with the matrix. ruff's
  py312 target raises no new finding. Installing on 3.10 or 3.11 is refused
  from 0.8.8. `CLAUDE.md`, `README.md`, `CONTRIBUTING.md` (the venv command),
  `00_program_overview.md`, `DEVELOPMENT_PROCESS.md` §0/§2, `RELEASE_PROCESS.md`
  §4 and `WORKFLOW_COMMANDS.txt` state the one interpreter.
