"""The solo loop's scripts, CI triggers and docs stay in step (DEVELOPMENT_PROCESS.md §0).

`scripts/solo_start.sh` / `scripts/solo_close.sh` need `git` and `gh` against
the live repository, so the loop itself is not a test. What can be asserted
offline: both scripts parse (`bash -n`), answer `--help` with their usage, and
`--dry-run` prints the full step sequence without executing anything — the
sequence is what §0 promises, so the dry-run text is checked for each step's
signature command.

Since 2026-08-22 the loop is **milestone-branch shaped**: one `dev/vX.Y.Z`
branch per release, every item committed directly onto it, and `main` reached
only by that milestone's single pull request. Two things follow that this file
also guards, because they are the same rule written in three places (rule 3):
`ci.yml` must run the fast gate on `dev/**` and the full matrix *only* on the
push to `main`, and the prose in §0 and the crib sheet must not still describe
the retired per-item branch → PR → squash-merge path.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_START = os.path.join(_ROOT, "scripts", "solo_start.sh")
_CLOSE = os.path.join(_ROOT, "scripts", "solo_close.sh")
_CI = os.path.join(_ROOT, ".github", "workflows", "ci.yml")
_PROCESS = os.path.join(_ROOT, "docs", "10_standard", "DEVELOPMENT_PROCESS.md")
_CRIB = os.path.join(_ROOT, "docs", "10_standard", "WORKFLOW_COMMANDS.txt")
_CI_STATE = os.path.join(_ROOT, "scripts", "ci_state.py")

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash not on PATH")


def _bash(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", *args], capture_output=True, text=True, timeout=30)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


@pytest.mark.parametrize("script", [_START, _CLOSE])
def test_scripts_parse_and_answer_help(script):
    assert _bash("-n", script).returncode == 0
    res = _bash(script, "--help")
    assert res.returncode == 0
    assert "Usage:" in res.stdout and "DEVELOPMENT_PROCESS.md" in res.stdout


# --- step 1: the milestone branch -------------------------------------------


def test_start_dry_run_opens_the_milestone_branch_and_pushes_it():
    res = _bash(_START, "--dry-run", "dev/v0.7.0")
    assert res.returncode == 0, res.stderr
    for sig in (
        "git pull --ff-only",
        "git checkout -b dev/v0.7.0",
        "git push -u origin dev/v0.7.0",
        "scripts/solo_close.sh --slug",
    ):
        assert sig in res.stdout, sig


def test_start_refuses_a_per_item_branch_and_says_what_replaced_it():
    """The old `<type>/<slug>` call is now a mistake, so the refusal has to
    teach the model rather than quote a regex — a per-item branch is exactly
    what the milestone branch exists to remove."""
    bad = _bash(_START, "--dry-run", "fix/38-select-keyed-pick")
    assert bad.returncode != 0
    assert "dev/vX.Y.Z" in bad.stderr
    assert "solo_close.sh" in bad.stderr
    # and a bare slug, or a dev branch without a version, are equally refused
    assert _bash(_START, "--dry-run", "some-slug").returncode != 0
    assert _bash(_START, "--dry-run", "dev/next").returncode != 0


def test_start_never_calls_gh():
    """Milestone scoping opens the issues; branching does not read them."""
    res = _bash(_START, "--dry-run", "dev/v0.7.0")
    assert "gh " not in res.stdout, res.stdout


# --- steps 3-7: closing one item, in place on the milestone branch -----------


def test_close_dry_run_lists_steps_3_to_7_in_order():
    res = _bash(_CLOSE, "--dry-run", "--slug", "some-slug", "27", "Subject")
    assert res.returncode == 0, res.stderr
    signatures = [
        "ruff check sloads/ cli.py oracle.py app_shell/ oracle_app/ scripts/",
        "mypy",
        "pytest -q -p no:cacheprovider",
        "git add -A",
        "git commit -m",
        "git push origin",
        "gh issue close 27 --reason completed",
        "backlog_issues.py check",
        "gh run list --branch <branch> --limit 1",
    ]
    positions = [res.stdout.find(s) for s in signatures]
    assert all(p >= 0 for p in positions), dict(zip(signatures, positions))
    assert positions == sorted(positions), "steps 3–7 are out of order in the dry-run"


def test_close_no_longer_touches_main_or_deletes_a_branch():
    """The retired half of the old script. Nothing lands on `main` except the
    milestone pull request, so a close that checked out main, fast-forwarded it
    or deleted the branch would be closing the item twice."""
    res = _bash(_CLOSE, "--dry-run", "--slug", "some-slug", "27", "Subject")
    assert res.returncode == 0, res.stderr
    for retired in ("git checkout -q main", "git merge --ff-only", "git branch -d",
                    "git push origin main"):
        assert retired not in res.stdout, retired
    src = _read(_CLOSE)
    assert "git merge --ff-only" not in src
    assert "git branch -d" not in src


def test_close_requires_a_slug_because_the_branch_names_the_milestone():
    assert _bash(_CLOSE, "--dry-run", "27", "Subject").returncode == 1
    assert "--slug" in _bash(_CLOSE, "--dry-run", "27", "Subject").stderr
    res = _bash(_CLOSE, "--help")
    assert res.returncode == 0 and "REQUIRED" in res.stdout


def test_close_rejects_missing_or_empty_arguments():
    assert _bash(_CLOSE, "--dry-run").returncode == 2
    assert _bash(_CLOSE, "--dry-run", "--slug", "s", "x", "Subject").returncode == 1


# --- the issue number is optional under the solo profile (§0) ---------------


#: The `gh` work an issue number costs, per item. Omitting the issue must drop
#: every one of them; the trailing `gh run list` CI peek is not in this set —
#: it is a courtesy, guarded on `gh auth status` succeeding at the time.
_ISSUE_GH_CALLS = ("gh auth status", "gh issue view", "gh issue close", "backlog_issues.py check")


@pytest.mark.parametrize(
    "argv, with_issue",
    [
        ([_CLOSE, "--dry-run", "--slug", "some-slug", "27", "Subject"], True),
        ([_CLOSE, "--dry-run", "--slug", "some-slug", "Subject"], False),
    ],
)
def test_the_issue_number_is_optional_and_omitting_it_drops_every_gh_call(argv, with_issue):
    res = _bash(*argv)
    assert res.returncode == 0, res.stderr
    present = [c for c in _ISSUE_GH_CALLS if c in res.stdout]
    if with_issue:
        assert present, res.stdout
    else:
        assert present == [], f"{present} survived without an issue number:\n{res.stdout}"


def test_close_without_an_issue_still_lists_the_gate_commit_and_push_steps():
    res = _bash(_CLOSE, "--dry-run", "--slug", "some-slug", "Subject")
    assert res.returncode == 0, res.stderr
    signatures = [
        "ruff check sloads/ cli.py oracle.py app_shell/ oracle_app/ scripts/",
        "mypy",
        "pytest -q -p no:cacheprovider",
        "git add -A",
        "git commit -m",
        "git push origin",
    ]
    positions = [res.stdout.find(s) for s in signatures]
    assert all(p >= 0 for p in positions), dict(zip(signatures, positions))
    assert positions == sorted(positions)


# --- the gate scales to the change set (§0) ---------------------------------


def test_the_dry_run_names_the_docs_only_guard_set():
    """The docs-only gate is §0's own five guard files, not a second list."""
    res = _bash(_CLOSE, "--dry-run", "--slug", "some-slug", "27", "Subject")
    assert res.returncode == 0, res.stderr
    for guard in (
        "tests/test_doc_currency.py",
        "tests/test_changelog_fragments.py",
        "tests/test_backlog_issues.py",
        "tests/test_schema_guards.py",
        "tests/test_workflow.py",
    ):
        assert guard in res.stdout, guard


def test_the_docs_only_predicate_admits_docs_and_rejects_everything_else():
    """The `case` arms in solo_close.sh decide the gate size — and, since the
    milestone-branch change, ONLY the gate size: where an item is closed no
    longer depends on what it touches."""
    src = _read(_CLOSE)
    assert "*.md|docs/*|changes/*)" in src, "the docs-only allowlist moved — re-check this guard"
    assert "DOCS_ONLY=0; break" in src


def test_close_honours_suffix_and_date_and_rejects_a_bad_date():
    res = _bash(_CLOSE, "--dry-run", "--slug", "s", "--suffix",
                "backlog Pri 9, tier S, 2026-08-17", "28", "X")
    assert res.returncode == 0 and 'git commit -m "X (backlog Pri 9, tier S, 2026-08-17)"' in res.stdout
    res = _bash(_CLOSE, "--dry-run", "--slug", "s", "--date", "2026-08-17", "28", "X")
    assert res.returncode == 0 and "2026-08-17)" in res.stdout
    bad = _bash(_CLOSE, "--dry-run", "--slug", "s", "--date", "2026-13-40", "28", "X")
    assert bad.returncode == 1 and "--date must be YYYY-MM-DD" in bad.stderr


# --- CI runs the advisory gate on dev/**, the full matrix only on main -------


def test_ci_runs_on_the_milestone_branch():
    ci = _read(_CI)
    assert '"dev/**"' in ci, "pushes to a milestone branch must trigger CI (§0)"


def test_coverage_is_reserved_for_the_push_to_main():
    """One conditional — the coverage `include` — must key on *push to main*, not
    on `pull_request`. Keyed the old way, a `dev/**` push would take the `||` arm
    and run the coverage-instrumented leg: the ~27-minute run that the
    2026-08-22 change moved off the fast gate in the first place. The two
    interpreter conditionals it used to share this rule with retired at #327:
    every run is 3.12, so only coverage differs between a PR and `main`
    (``tests/test_ci_conformance.py`` holds that parity)."""
    ci = _read(_CI)
    sentinel = "github.event_name == 'push' && github.ref == 'refs/heads/main'"
    assert ci.count(sentinel) == 1, (
        f"expected the push-to-main condition once (the coverage include), found "
        f"{ci.count(sentinel)}")
    assert "github.event_name == 'pull_request' &&" not in ci, (
        "a matrix still keys on 'is this a PR', which sends dev/** pushes to the full matrix")


# --- the prose says the same thing (rule 3) ---------------------------------


def test_the_process_and_crib_sheet_describe_the_milestone_branch():
    process, crib = _read(_PROCESS), _read(_CRIB)
    for name, text in (("DEVELOPMENT_PROCESS.md §0", process), ("WORKFLOW_COMMANDS.txt", crib)):
        assert "dev/v" in text, f"{name} does not name the milestone branch"
    # the retired per-item path must not still be prescribed by the crib sheet
    assert "gh pr merge --squash" not in crib, (
        "WORKFLOW_COMMANDS.txt still prescribes the per-item squash-merge")


# --- #329: the close reads CI on the pushed tip before its gate -------------


def _ci_state():
    spec = importlib.util.spec_from_file_location("ci_state", _CI_STATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_TIP = "0123456789abcdef0123456789abcdef01234567"


def _run(sha=_TIP, status="completed", conclusion="success"):
    return {"headSha": sha, "status": status, "conclusion": conclusion,
            "url": f"https://example.invalid/runs/{sha[:7]}"}


@pytest.mark.parametrize("runs, code", [
    ([_run()], 0),
    ([_run(conclusion="failure")], 1),
    ([_run(conclusion="timed_out")], 1),
    ([_run(conclusion="startup_failure")], 1),
    ([_run(status="in_progress", conclusion="")], 2),
    ([_run(status="queued", conclusion="")], 2),
    ([_run(conclusion="cancelled")], 2),
    ([_run(conclusion="action_required")], 2),
    ([], 2),
    # the newest run is a superseded commit's red; the tip's own run is green
    ([_run(sha="f" * 40, conclusion="failure"), _run()], 0),
    # ...and the other way round: only the tip's run is judged
    ([_run(sha="f" * 40), _run(conclusion="failure")], 1),
    # nothing listed for the tip yet: a newer push's run has not started
    ([_run(sha="f" * 40)], 2),
], ids=["green", "failure", "timed_out", "startup_failure", "in_progress", "queued",
        "cancelled", "action_required", "no_runs", "tip_green_under_a_red",
        "tip_red_under_a_green", "tip_not_listed"])
def test_the_ci_verdict_judges_the_pushed_tip_by_ruling_1a(runs, code):
    """Red refuses, green passes, everything else warns (owner ruling 1a,
    2026-09-28) -- and only the run of the pushed tip is judged, because
    ``ci.yml`` cancels a superseded commit's run. Credential-free: the verdict
    is the helper's, fed the JSON ``gh run list`` returns."""
    got, message = _ci_state().verdict(runs, _TIP)
    assert got == code, message
    if code == 1:
        assert "red" in message and "https://" in message


@pytest.mark.parametrize("stdin", ["", "not json", '{"a": 1}'])
def test_unreadable_ci_warns_rather_than_refusing(stdin):
    """``gh`` failed, or answered something else: CI is unread, which warns
    (ruling 2a) -- a network blip must not block a close, nor pass as green."""
    res = subprocess.run([sys.executable, _CI_STATE, "--tip", _TIP], input=stdin,
                         capture_output=True, text=True, timeout=30, check=False)
    assert res.returncode == 2, res.stdout + res.stderr
    assert "unread" in res.stdout


def test_the_close_reads_ci_in_preflight_before_the_gate():
    """The read is preflight: before the gate, so a red refuses with nothing
    changed -- with or without an issue number (ruling 2a)."""
    for argv in (["27", "Subject"], ["Subject"]):
        res = _bash(_CLOSE, "--dry-run", "--slug", "some-slug", *argv)
        assert res.returncode == 0, res.stderr
        read = res.stdout.find("--workflow ci.yml")
        assert 0 <= read < res.stdout.find("ruff check"), res.stdout
        assert "scripts/ci_state.py" in res.stdout and "--ci-red-ok" in res.stdout


def test_a_red_close_needs_a_reason_and_the_reason_is_recorded():
    """``--ci-red-ok`` takes a reason and the script puts it in the commit
    body; an empty one is refused before anything runs."""
    res = _bash(_CLOSE, "--dry-run", "--slug", "s", "--ci-red-ok", "", "27", "X")
    assert res.returncode == 1 and "reason" in res.stderr
    src = _read(_CLOSE)
    assert 'git commit -q -m "$MSG" -m "$CI_NOTE"' in src
    assert "scripts/ci_state.py --tip" in src


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
