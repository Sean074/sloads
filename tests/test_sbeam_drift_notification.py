"""A notification nobody receives is not one (#188, review R-18).

`.github/workflows/sbeam-drift.yml` runs the round-trip gate against sbeam
`main` once a week, `continue-on-error` throughout, so its failure is advice
about the pin rather than a merge block. For ten months that advice was
delivered only as a red square on the Actions page, which nothing requires
anyone to open: the 2026-09-04 project review filed exactly that (R-18). The
workflow now files, updates and closes one pinned issue instead, so drift
arrives where work is planned.

**Why this needs a guard and not just a step.** The notifier is wired through
two YAML details that look like noise and delete cleanly:

* the gate step's **step-level** ``continue-on-error``. Without it a red gate
  skips every later step, so the step whose only job is to report the failure
  is the one the failure suppresses -- silently, and only ever on the week it
  matters. The job-level ``continue-on-error`` does *not* substitute: it decides
  how the run is scored, not whether later steps execute.
* the gate step's ``id``, and the ``steps.<id>.outcome`` the notifier reads.
  ``failure()`` cannot be used here, because a step that continues on error has
  ``conclusion: success`` -- an author reaching for the obvious spelling gets a
  notifier that never fires.

and through one literal that must be spelled the same way twice: the issue
title. It is both the search key and the created title, so a drift between the
two turns "update the open issue" into "open a new issue every Monday", which
is the failure mode that makes an auto-filer worse than no auto-filer.

`CLAUDE.md` practice 3: a convention that matters gets a drift-guard test, not
a comment asking the next author to be careful.
"""

from __future__ import annotations

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DRIFT = os.path.join(_ROOT, ".github", "workflows", "sbeam-drift.yml")
_GUIDE = os.path.join(_ROOT, "docs", "10_standard", "PROJECT_GUIDE.md")

#: Steps are list items at a fixed indent under ``jobs.drift.steps``. Parsed by
#: regex rather than with PyYAML deliberately: PyYAML is not a declared
#: dependency of this project (it arrives transitively through ``pre-commit``),
#: and `tests/test_ci_conformance.py` reads the other workflow the same way.
_STEP = re.compile(r"^      - ", re.M)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _steps(text: str) -> list:
    starts = [m.start() for m in _STEP.finditer(text)]
    assert starts, f"no steps parsed out of {os.path.basename(_DRIFT)}"
    bounds = starts + [len(text)]
    return [text[bounds[i]:bounds[i + 1]] for i in range(len(starts))]


def _step_named(text: str, fragment: str) -> str:
    hits = [s for s in _steps(text) if fragment in s.split("\n", 1)[0]]
    assert len(hits) == 1, (
        f"expected exactly one step whose name contains {fragment!r}; got {len(hits)}")
    return hits[0]


def _gate(text: str) -> str:
    return _step_named(text, "Round-trip gate")


def _notifier(text: str) -> str:
    return _step_named(text, "drift issue")


def test_the_workflow_is_parsed_at_all():
    """Guard the guard. Every assertion below is vacuous against a rewritten
    workflow whose step names moved, and a vacuous conformance test is worse
    than none: it reports the class as covered."""
    text = _read(_DRIFT)
    assert len(_steps(text)) >= 2
    assert _gate(text) is not _notifier(text)


def test_the_gate_step_continues_on_error_so_the_notifier_can_run():
    """The suppression trap, asserted. `continue-on-error` at the *step* is what
    lets a later step run at all after a red gate; the job-level one only scores
    the run. Delete it and the notification disappears on precisely the weeks
    there is something to notify."""
    gate = _gate(_read(_DRIFT))
    assert re.search(r"^        continue-on-error:\s*true\s*$", gate, re.M), (
        "the round-trip gate step no longer sets `continue-on-error: true`. A "
        "failing step without it skips every later step, so the drift issue "
        "would never be filed on the runs that fail (#188)")
    assert re.search(r"^        id:\s*\S", gate, re.M), (
        "the round-trip gate step lost its `id`; the notifier identifies the "
        "gate's outcome by that id (#188)")


def test_the_notifier_keys_on_the_gates_outcome_and_never_on_failure():
    """A step that continues on error reports `conclusion: success`, so
    `failure()` and `if: failure()` are both dead here — the outcome is the only
    spelling that sees the red gate. This asserts the live one and bans the
    plausible wrong one across the whole workflow."""
    text = _read(_DRIFT)
    gate_id = re.search(r"^        id:\s*(\S+)", _gate(text), re.M).group(1)
    notifier = _notifier(text)
    assert f"steps.{gate_id}.outcome" in notifier, (
        f"the notifier no longer reads `steps.{gate_id}.outcome`; without it "
        "nothing connects the report to the gate it reports on (#188)")
    assert "failure()" not in text, (
        "sbeam-drift.yml uses `failure()`, which can never be true in this "
        "workflow: the gate continues on error, so its conclusion is success. "
        "Key on `steps.<id>.outcome` instead (#188)")


def test_the_notifier_may_write_issues():
    """The permission is the whole capability. `GITHUB_TOKEN` is read-only for
    issues by default in a repository configured that way, and the step fails
    with a 403 the week it first matters."""
    text = _read(_DRIFT)
    assert re.search(r"^\s*issues:\s*write\s*$", text, re.M), (
        "sbeam-drift.yml no longer grants `issues: write`; the notifier cannot "
        "file or close anything without it (#188)")


def test_the_issue_is_found_and_created_under_one_title():
    """**The auto-filer's characteristic bug.** The title is both the search key
    and the created title. Let the two spellings drift and every Monday opens a
    fresh issue while last Monday's stays open — noise that gets the whole
    mechanism switched off, which is the outcome R-18 was trying to avoid."""
    notifier = _notifier(_read(_DRIFT))
    assign = re.search(r'export TITLE="([^"]+)"', notifier)
    assert assign, (
        "the notifier no longer binds the issue title to a single `TITLE` "
        "variable; find-or-create must not spell it twice (#188)")
    assert notifier.count(assign.group(1)) == 1, (
        "the drift issue's title appears literally more than once in the "
        f"notifier: {assign.group(1)!r}. Use \"$TITLE\" everywhere (#188)")
    for use in ('--search "$TITLE in:title"', '--title "$TITLE"'):
        assert use in notifier, (
            f"the notifier no longer uses {use!r}; the search key and the "
            "created title must be the same string (#188)")


def test_the_notifier_files_updates_and_clears():
    """All three verbs, because an issue that is only ever opened stops being a
    signal. The close arm is what keeps a pinned issue meaning "drifting now"
    rather than "drifted once"."""
    notifier = _notifier(_read(_DRIFT))
    for verb in ("gh issue create", "gh issue comment", "gh issue close"):
        assert verb in notifier, f"the notifier no longer runs `{verb}` (#188)"


def test_a_gate_that_did_not_run_moves_nothing():
    """Setup failures must not close a live drift report. If the install step
    dies the gate is `skipped`, and any branch that treats "not failure" as
    "green" would close the issue on the strength of a test that never ran."""
    notifier = _notifier(_read(_DRIFT))
    assert re.search(r"failure\|success\)", notifier), (
        "the notifier no longer restricts itself to the outcomes `failure` and "
        "`success`. A skipped gate (setup died) must leave the issue exactly "
        "where it is (#188)")


def test_the_pin_procedure_tells_the_reader_the_issue_exists():
    """Docs-vs-CI, the class `tests/test_ci_conformance.py` exists for. The
    bump procedure is where someone arrives holding a red drift result; if it
    still describes the Actions page as the only place drift appears, the
    notification exists and the person who needs it does not know."""
    guide = _read(_GUIDE)
    assert "sbeam-drift.yml" in guide and "drift issue" in guide, (
        "PROJECT_GUIDE.md's sbeam-pin section no longer tells the reader that a "
        "red weekly run files a drift issue (#188)")


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
