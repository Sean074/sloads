"""A documented git/CI setting cannot differ from the live one in silence.

**The defect class (2026-08-25, backlog row 6 / issue #46, review CR-D-4).** Two
instances in one day, the same shape both times: a doc stated one thing, the
live setting another, and nothing compared them.

* `RELEASE_PROCESS.md` §4, `DEVELOPMENT_PROCESS.md` §0 (two rows) and
  `WORKFLOW_COMMANDS.txt` all said "linear history off, merge commits allowed".
  `main` enforces linear history; it refused the 0.7.2 milestone PR with "This
  branch must not contain merge commits" — at the cut, which is the worst moment
  to find it. Worse, the documented hotfix recovery told you to `git merge main`
  onto the milestone branch: the exact act that makes the milestone PR
  unmergeable, invisible until the cut.
* `DEVELOPMENT_PROCESS.md` §2 listed six required checks — `test (3.9)`,
  `test (3.11)`, `sbeam-roundtrip (3.11)` among them — three of which `ci.yml`
  never produces on a pull request at all. A required check that never reports
  blocks its PR forever; the live setting was (correctly) the fast-gate three,
  and §2 contradicted its own §0 table on the same page.

**Why the comparison is two hops.** CI has no `gh` credential, so a test cannot
read GitHub. Hop 1 is here and always runs: `.github/branch-protection.json` (a
checked-in snapshot of the live settings) is asserted against the prose, and
against what `ci.yml` actually reports on a pull request. Hop 2 is
`scripts/branch_protection_snapshot.py --check`, which the owner runs — it needs
auth, and a gate that needs a credential CI lacks is a gate that silently skips,
which is the failure mode this file exists to end.
"""

from __future__ import annotations

import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CI = os.path.join(_ROOT, ".github", "workflows", "ci.yml")
_SNAPSHOT = os.path.join(_ROOT, ".github", "branch-protection.json")
_STD = os.path.join(_ROOT, "docs", "10_standard")

_DEV_PROCESS = os.path.join(_STD, "DEVELOPMENT_PROCESS.md")
_RELEASE = os.path.join(_STD, "RELEASE_PROCESS.md")
_COMMANDS = os.path.join(_STD, "WORKFLOW_COMMANDS.txt")
_SMOKE = os.path.join(_ROOT, "scripts", "smoke_test.sh")



def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# --- what ci.yml actually reports ------------------------------------------

#: `python-version: ${{ <push-to-main cond> && fromJSON('[..full..]') || fromJSON('[..fast..]') }}`
_MATRIX = re.compile(
    r"python-version:\s*\$\{\{.*?fromJSON\('(?P<full>\[[^']*\])'\).*?fromJSON\('(?P<fast>\[[^']*\])'\)",
    re.S,
)
#: `python-version: ["3.12"]` -- one list, the same on a PR and on the push to
#: main (#327). The conditional form above stays readable so a reintroduced
#: split is parsed, and then refused by the parity test below.
_PLAIN_MATRIX = re.compile(r"^\s+python-version:\s*(?P<list>\[[^\]]*\])\s*$", re.M)
_JOB = re.compile(r"^  (?P<name>[a-z][a-z0-9-]*):\s*$", re.M)


def _ci_jobs():
    """{job name: (versions on a PR, versions on the push to main)}.

    A job with no version matrix reports under its bare name, so it maps to
    ``([""], [""])`` and yields the check name ``"<job>"``.
    """
    text = _read(_CI)
    starts = [(m.group("name"), m.start()) for m in _JOB.finditer(text)]
    jobs = {}
    for i, (name, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        m = _MATRIX.search(text, start, end)
        plain = _PLAIN_MATRIX.search(text, start, end)
        if m:
            jobs[name] = (json.loads(m.group("fast")), json.loads(m.group("full")))
        elif plain:
            versions = json.loads(plain.group("list"))
            jobs[name] = (versions, versions)
        else:
            jobs[name] = ([""], [""])
    return jobs


def _check_names(index):
    """The check names GitHub reports; ``index`` 0 = on a PR, 1 = on push to main."""
    out = set()
    for name, versions in _ci_jobs().items():
        for v in versions[index]:
            out.add(f"{name} ({v})" if v else name)
    return out


def test_the_ci_matrix_is_parsed_at_all():
    """Guard the guard: every assertion below is vacuous if the regexes stop
    matching a rewritten ci.yml, and a vacuous conformance test is worse than
    none — it reports the drift class as covered."""
    jobs = _ci_jobs()
    assert {"test", "typecheck", "sbeam-roundtrip"} <= set(jobs), (
        f"ci.yml job names not recognised: {sorted(jobs)}"
    )
    assert jobs["test"][0] != [""], "ci.yml's `test` job has no python-version list parsed"


def test_a_pull_request_runs_every_interpreter_the_push_to_main_runs():
    """#327. The push to `main` used to add 3.10/3.11 legs no PR ran, so a
    3.11-only regex (#325) was found only after the milestone merge. One
    interpreter everywhere: whatever the merge push runs, a PR ran first. Only
    coverage stays merge-push-only (``ci.yml``'s ``include``), and it is not an
    interpreter."""
    split = {name: v for name, v in _ci_jobs().items() if v[0] != v[1]}
    assert not split, (
        f"ci.yml runs different interpreters on a PR and on the push to main: {split}. "
        "A leg that only the merge push runs is found after the merge (#325, #327)."
    )


def test_the_suite_runs_on_the_interpreter_ci_runs():
    """#327. The developer's `.venv` was 3.11 while CI ran 3.12, so a byte
    that differed between them (#324) passed every local gate and failed every
    CI run for two days. The gate is only CI's gate if it runs CI's
    interpreter: read from `ci.yml`, so moving to a new Python is one edit that
    fails here until the venv follows."""
    ci = {v for v in _ci_jobs()["test"][0] if v}
    here = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert here in ci, (
        f"this suite is running on Python {here}; ci.yml's `test` job runs {sorted(ci)}. "
        "Rebuild .venv on that interpreter (CONTRIBUTING.md) -- a gate on another "
        "interpreter is not the gate CI runs (#324, #327)."
    )


#: Every interpreter literal ``ci.yml`` states, in any form: a scalar
#: ``python-version: "3.12"`` (the `typecheck` job's, which `_ci_jobs` does not
#: parse: that job reports under its bare name), a list, or a ``fromJSON``
#: include row.
_CI_VERSION = re.compile(r'python-version["\']?\s*:\s*(?:\[[^\]]*\]|["\']?3\.\d+["\']?)')


def test_every_interpreter_ci_names_is_the_test_jobs():
    """#329, a rider from the #327 review: `typecheck` pins a scalar
    ``python-version: "3.12"`` that the matrix parser never sees, so moving the
    `test` job to a new Python would leave mypy checking the old one with every
    conformance test green. Every version literal in ``ci.yml`` is one the
    `test` job runs."""
    text = _read(_CI)
    found = {v for m in _CI_VERSION.finditer(text) for v in re.findall(r"3\.\d+", m.group(0))}
    assert found, "no python-version literal parsed out of ci.yml"
    assert any(re.search(r'python-version:\s*"3\.\d+"', line) for line in text.splitlines()), (
        "the typecheck job's scalar python-version is no longer parsed -- re-check this guard")
    test = {v for v in _ci_jobs()["test"][0] if v}
    assert found <= test, (
        f"ci.yml names {sorted(found - test)} outside the `test` job's {sorted(test)} (#329)")


#: Where the current truth lives (``CLAUDE.md`` "Where to look"): the standard
#: and theory trees and the three front-door files. ``docs/90_record/`` is the
#: record, and a dated line there may name any interpreter it was true of.
_CURRENT_TRUTH = ("CLAUDE.md", "README.md", "CONTRIBUTING.md",
                  os.path.join("docs", "10_standard"), os.path.join("docs", "20_theory"))

#: An interpreter named as one, and only in context -- so a section number
#: ("3.10 Section 10") and a matplotlib stamp ("v3.11.1") are not read as one.
_DOC_VERSION = re.compile(
    r"\bPython\s+(3\.\d+)\b"            # Python 3.12
    r"|\bpython(3\.\d+)\b"               # python3.12 -m venv
    r"|\bpy3(1\d)\b"                      # py312
    r"|\w \((3\.\d+)\)"                   # test (3.12)
    r"|\b(3\.\d+)(?=\s+legs?\b)"          # the 3.12 leg
    r"|\b(3\.1\d)(?=/3\.\d)"              # 3.10/3.11/...
    r"|(?<=/)(3\.1\d)\b")                  # .../3.12

#: The mentions of other interpreters that are current truth and not a claim of
#: support (owner ruling 3a, #329): ``(file, version): reason``. A new one fails
#: until it is reworded or added here with its reason.
_INTERPRETER_MENTIONS = {
    ("docs/10_standard/DEVELOPMENT_PROCESS.md", "3.10"):
        "§0's CI row records the retired 3.10/3.11 legs and why they went (#327)",
    ("docs/10_standard/DEVELOPMENT_PROCESS.md", "3.11"):
        "§0's CI row records the retired 3.10/3.11 legs and why they went (#327)",
    ("docs/10_standard/DEVELOPMENT_PROCESS.md", "3.14"):
        "branch coverage under sys.monitoring needs CPython 3.14 -- a fact about "
        "coverage, not an interpreter sloads claims",
}


def _doc_files():
    for entry in _CURRENT_TRUTH:
        path = os.path.join(_ROOT, entry)
        if os.path.isfile(path):
            yield path
            continue
        for dirpath, _dirs, files in os.walk(path):
            for name in sorted(files):
                if name.endswith((".md", ".txt")):
                    yield os.path.join(dirpath, name)


def test_no_standard_doc_names_an_interpreter_ci_does_not_run():
    """#329, the other #327-review rider: #327 retired the doc-wording check
    for the old three-version list along with the list, and left nothing to
    stop a doc claiming an interpreter again -- ``CONVENTIONS.md`` §7 still
    said "identical on 3.10/3.11/3.12". Every interpreter a current-truth doc
    names is one ``ci.yml``'s `test` job runs, or an allowlisted mention with
    its reason."""
    ci = {v for v in _ci_jobs()["test"][0] if v}
    stray, seen = [], set()
    for path in _doc_files():
        rel = os.path.relpath(path, _ROOT)
        for lineno, line in enumerate(_read(path).splitlines(), start=1):
            for m in _DOC_VERSION.finditer(line):
                raw = next(g for g in m.groups() if g)
                version = f"3.{raw}" if "." not in raw else raw
                if version in ci:
                    continue
                if (rel, version) in _INTERPRETER_MENTIONS:
                    seen.add((rel, version))
                    continue
                stray.append(f"{rel}:{lineno}: {version}")
    assert not stray, (
        f"a current-truth doc names an interpreter ci.yml does not run ({sorted(ci)}):\n  "
        + "\n  ".join(stray)
        + "\nReword it, or add it to _INTERPRETER_MENTIONS with its reason (#329).")
    stale = set(_INTERPRETER_MENTIONS) - seen
    assert not stale, f"allowlisted mentions no longer in the docs -- remove them: {sorted(stale)}"


# --- hop 1a: snapshot <-> ci.yml -------------------------------------------

def test_every_required_check_actually_runs_on_a_pull_request():
    """CR-D-4's second instance, made structural. A required status check that
    `ci.yml` does not produce on a pull request can never report, so the PR can
    never merge — which is why the required set is the fast gate and not the
    full matrix. This is the assertion that would have caught the six-check
    list `DEVELOPMENT_PROCESS.md` §2 carried."""
    required = set(json.load(open(_SNAPSHOT, encoding="utf-8"))["required_status_checks"])
    on_pr = _check_names(0)
    missing = sorted(required - on_pr)
    assert not missing, (
        f"required check(s) that never run on a PR: {missing}.\n"
        f"ci.yml reports {sorted(on_pr)} on a pull request. Either the protection "
        "setting is wrong (fix it on GitHub, then run "
        "`python scripts/branch_protection_snapshot.py --write`) or ci.yml stopped "
        "producing the check."
    )


# --- hop 1b: snapshot <-> the process docs ---------------------------------

def test_the_process_docs_name_the_snapshot_required_checks():
    """`DEVELOPMENT_PROCESS.md` states the required-check set twice — §0's solo
    table and §2's protection bullet. Both must name exactly what is required,
    and neither may name a check that is not."""
    snap = json.load(open(_SNAPSHOT, encoding="utf-8"))
    text = _read(_DEV_PROCESS)
    for check in snap["required_status_checks"]:
        assert text.count(f"`{check}`") >= 2, (
            f"required check {check!r} is named fewer than twice in "
            "DEVELOPMENT_PROCESS.md — §0's table and §2's protection bullet must both "
            "state the live required set."
        )
    stale = [
        c
        for c in ("test (3.9)", "test (3.10)", "test (3.11)", "sbeam-roundtrip (3.11)")
        if c not in snap["required_status_checks"] and f"required checks `{c}`" in text
    ]
    assert not stale, f"DEVELOPMENT_PROCESS.md still lists non-required check(s): {stale}"


#: A phrase that follows one of these, within a short window, is being retracted
#: rather than asserted ("**Rebase, not `git merge main`**").
_NEGATION = re.compile(r"(?:\bnot\b|\bnever\b|\bno longer\b|rather than|instead of)[^.]{0,40}$")


def _unquoted(text: str, phrase: str) -> list:
    """Line numbers where ``phrase`` is *asserted* rather than cited.

    These docs correct themselves in place — §0's protection row quotes the
    wording it retracts ("linear history off, merge commits allowed"), and
    `RELEASE_PROCESS.md` §6 names the banned command to forbid it ("**Rebase, not
    `git merge main`**"). A flat substring ban fires on both and would force the
    correction off the page, which is the opposite of what this row wants. Two
    forms count as citation: inside quotation marks, or immediately after a
    negation. Anything else is the page telling you to do it.
    """
    quoted = set()
    for m in re.finditer(r'"[^"]*"', text):
        if phrase in m.group(0):
            quoted.update(range(m.start(), m.end()))
    out = []
    for m in re.finditer(re.escape(phrase), text):
        if m.start() in quoted:
            continue
        line_start = text.rfind("\n", 0, m.start()) + 1
        if _NEGATION.search(text[line_start : m.start()]):
            continue
        out.append(text.count("\n", 0, m.start()) + 1)
    return out


def test_the_process_docs_agree_with_the_live_merge_method():
    """The 0.7.2 instance: `main` requires linear history, so the milestone PR is
    rebase-merged. No process doc may tell you to merge it any other way, and the
    hotfix recovery must not tell you to merge `main` *into* the milestone branch
    — that is what makes the PR unmergeable, and it is invisible until the cut."""
    snap = json.load(open(_SNAPSHOT, encoding="utf-8"))
    assert snap["required_linear_history"] is True and snap["milestone_pr_merge_method"] == "rebase", (
        "the snapshot no longer describes a linear-history/rebase repository; this "
        "test's assertions below are written for that setting and must be revisited."
    )
    for path in (_DEV_PROCESS, _RELEASE, _COMMANDS):
        text = _read(path)
        assert "--rebase" in text or "rebase-merge" in text, (
            f"{os.path.relpath(path, _ROOT)} describes the milestone merge but never "
            "says rebase, while `main` requires linear history."
        )
        for banned in ("merge commits allowed", "linear history off", "git merge main"):
            loose = _unquoted(text, banned)
            assert not loose, (
                f"{os.path.relpath(path, _ROOT)} asserts {banned!r} — contradicts the live "
                "linear-history setting recorded in .github/branch-protection.json. "
                "(Quoting the old wrong wording to correct it is fine; this fires only on "
                f"an occurrence outside quotation marks. Offending line(s): {loose})"
            )


def test_the_process_docs_agree_with_the_live_review_settings():
    """The 2026-08-26 instance, and CR-D-4's own class one field deeper. §2 promised
    an approving review from a non-author, Code Owners review and stale-approval
    dismissal against a branch that required none of them: `required_pull_request`
    was true the moment GitHub carried *any* review block, so no assertion here
    could see the difference. The snapshot now tracks the three settings
    themselves, and this test holds the prose to whichever way they are set —
    including back, when a second collaborator turns them on."""
    snap = json.load(open(_SNAPSHOT, encoding="utf-8"))
    text = _read(_DEV_PROCESS)

    # The one review setting that IS live, in both profiles.
    assert snap["required_conversation_resolution"] is True, (
        "`main` no longer requires conversation resolution; §2 still says it does."
    )
    assert "conversations resolved" in text, (
        "DEVELOPMENT_PROCESS.md §2 stopped naming conversation resolution, which is "
        "live on `main`."
    )

    solo = (
        snap["required_approving_review_count"] == 0
        and snap["required_code_owner_reviews"] is False
        and snap["dismiss_stale_reviews"] is False
    )
    caveat = "Review requirements are the multi-dev profile's, and are OFF under §0"
    if solo:
        assert caveat in text, (
            "no review requirement is live on `main` (approvals, Code Owners and "
            "stale dismissal are all off in .github/branch-protection.json), but "
            "DEVELOPMENT_PROCESS.md §2 does not carry the bullet saying so. Written "
            "as a live requirement, it is a promise the branch does not keep."
        )
    else:
        assert caveat not in text, (
            "a review requirement is now live on `main`, so §2's 'OFF under §0' "
            "bullet is stale — state the settings as live and move them out of the "
            "switch-over list."
        )


# --------------------------------------------------------------------------- #
# The §3.5 smoke gate and the front-ends it claims to boot (#127)
# --------------------------------------------------------------------------- #
# The same defect class as the rest of this file, in the release gate rather than
# in CI: §3.5 is a hard gate, and for the release whose headline deliverable is
# the oracle GUI it started `app/Home.py` and nothing else. A second front-end
# nothing boots under a real server is a front-end whose boot no gate covers.

#: Directories that hold no front-end. Everything else at the top level is
#: scanned, so a third GUI joins the comparison by existing rather than by
#: someone remembering to list it here.
_NOT_A_GUI = {"tests", "scripts", "docs", "reference", "sloads", "changes",
              "examples", "projects", "changes", "sloads.egg-info"}
#: A GUI entry point is the file that calls ``st.set_page_config`` -- exactly one
#: per front-end (``tests/test_app_shell.py`` owns that rule). Anchored at the
#: line start so prose *about* the call, in a test or a doc, is not a front-end.
_PAGE_CONFIG = re.compile(r"^\s*st\.set_page_config\(", re.M)


def _front_ends():
    found = []
    for gui in sorted(os.listdir(_ROOT)):
        path = os.path.join(_ROOT, gui)
        if gui.startswith(".") or gui in _NOT_A_GUI or not os.path.isdir(path):
            continue
        for name in sorted(os.listdir(path)):
            entry = os.path.join(path, name)
            if not name.endswith(".py") or not os.path.isfile(entry):
                continue
            if _PAGE_CONFIG.search(_read(entry)):
                found.append(f"{gui}/{name}")
    return found


def test_the_smoke_gate_boots_every_front_end_this_repo_has():
    """`st.set_page_config` marks a GUI entry point (one per front-end, guarded
    by tests/test_app_shell.py). Every one of them is booted by the §3.5 script."""
    script = _read(_SMOKE)
    declared = re.search(r"GUI_ENTRY_POINTS=\((?P<body>[^)]*)\)", script)
    assert declared, "smoke_test.sh no longer declares GUI_ENTRY_POINTS"
    booted = re.findall(r'"([^"]+\.py)"', declared.group("body"))
    front_ends = _front_ends()
    assert front_ends, "no front-end found -- the detector, not the gate, is broken"
    assert sorted(booted) == sorted(front_ends), (
        "scripts/smoke_test.sh boots {booted} but this repo's front-ends are "
        "{front}: a GUI the §3.5 gate never starts is a GUI no release gate "
        "starts (#127)".format(booted=sorted(booted), front=sorted(front_ends))
    )
    # Declaring them is not booting them: one smoke_gui call per front-end.
    calls = re.findall(r"^smoke_gui ", script, re.M)
    assert len(calls) == len(front_ends), (
        f"{len(front_ends)} front-end(s) declared, {len(calls)} booted")


def test_the_release_checklist_names_every_front_end_the_gate_boots():
    """§3.5 is the line a release manager reads. It names what the script does."""
    release = _read(_RELEASE)
    section = release[release.index("### 3.5"):]
    section = section[:section.index("---")]
    for entry in _front_ends():
        assert entry in section, (
            f"RELEASE_PROCESS.md §3.5 does not name {entry}, which the smoke "
            "gate boots -- the checklist and the script must say the same thing"
        )
    assert "sloads-oracle" in section, (
        "§3.5 must say the oracle GUI is launched through its console script: "
        "running the launcher is the half of #127 that path-checking missed"
    )


def test_the_smoke_gate_runs_the_oracle_launcher_rather_than_resolving_it():
    """`test_oracle_gui.test_the_launcher_points_at_the_entry_point` proves the
    path resolves; only this proves the console script `pyproject.toml` binds
    actually starts a server."""
    script = _read(_SMOKE)
    assert "sloads-oracle" in script, "the console script is never invoked"
    with open(os.path.join(_ROOT, "pyproject.toml"), encoding="utf-8") as fh:
        assert "sloads-oracle" in fh.read(), "the console script is not declared"


_CLASSIFIER = re.compile(r'"Programming Language :: Python :: (3\.\d+)"')
_REQ_PY = re.compile(r'requires-python\s*=\s*">=(3\.\d+)"')


def test_the_python_support_claim_is_one_claim_in_three_places():
    """The 0.8.0 cut shipped `requires-python >= 3.9` beside a streamlit floor
    whose own Requires-Python is >= 3.10 — the 3.9 leg failed at *install*, on
    the push to `main`, after the tag (#132). Three statements of the supported
    interpreters exist (`requires-python`, the trove classifiers, the ci.yml
    full matrix) and the classifier comment's mirror rule was prose. This makes
    it structural: the classifier set IS the full-matrix set, the floor is the
    smallest of them, and every leg satisfies the floor. The half a test cannot
    reach offline — whether the *dependencies'* Requires-Python admits the
    floor — is enforced by the full-matrix install on `main` being green, which
    is exactly where #132 surfaced."""
    with open(os.path.join(_ROOT, "pyproject.toml"), encoding="utf-8") as fh:
        pyproject = fh.read()
    floor = _REQ_PY.search(pyproject)
    assert floor, "pyproject.toml states no '>=' requires-python floor"
    floor_v = tuple(int(n) for n in floor.group(1).split("."))
    classifiers = {c for c in _CLASSIFIER.findall(pyproject) if c != "3"}

    full = {v for _, on_main in _ci_jobs().values() for v in on_main if v}
    assert full, "no python-version matrix list parsed out of ci.yml"

    assert classifiers == full, (
        f"the classifier set {sorted(classifiers)} is not the ci.yml full matrix "
        f"{sorted(full)} — the classifier list mirrors the matrix (pyproject's own "
        "comment); a classifier claiming an untested interpreter is #132's shape"
    )
    as_tuples = {tuple(int(n) for n in v.split(".")) for v in full}
    assert min(as_tuples) == floor_v, (
        f"requires-python >= {floor.group(1)} but the smallest tested leg is "
        f"{'.'.join(map(str, min(as_tuples)))} — the floor must be the smallest "
        "interpreter CI actually installs on"
    )


def test_the_dependency_ceiling_policy_rests_on_an_unpinned_install():
    """`pyproject.toml` states a runtime floor and deliberately **no** upper
    bound (#129). That decision is only safe because CI installs the runtime
    dependencies unpinned on every run, so an upstream release that removes a
    deprecated API -- `use_container_width` is documented for removal -- fails
    the GUI tests here before it reaches anyone's fresh install. A constraints
    file or a `streamlit==` in a workflow step would retire that early warning
    silently, leaving the "no ceiling" decision resting on nothing."""
    ci = _read(_CI)
    installs = [line.strip() for line in ci.splitlines()
                if "pip install" in line and "--upgrade pip" not in line
                and not line.lstrip().startswith("#")]
    assert installs, "no dependency install step found in ci.yml"
    for line in installs:
        assert re.search(r"-e '?\.", line), (
            f"ci.yml installs something other than this project: {line!r} -- the "
            "unpinned-install policy is stated in pyproject.toml's dependencies"
        )
        assert "-c " not in line and "--constraint" not in line, (
            f"ci.yml constrains the install ({line!r}); the ceiling policy in "
            "pyproject.toml assumes CI meets the newest releases first"
        )
    for pinned in ("streamlit==", "streamlit<", "pandas==", "plotly=="):
        assert pinned not in ci, (
            f"ci.yml pins {pinned!r}; a pinned CI is a CI that cannot warn about "
            "the upstream removal pyproject.toml's ceiling policy relies on it for"
        )


#: Reaches past Streamlit's public surface that the suite is **allowed** to
#: make, each with the reason it is not a defect. A reach not listed here is a
#: reach nobody decided to take.
#:
#: The cost of an unwritten one is measured: `AppTest.session_state` was the
#: internal `SafeSessionState` through 1.63, and one line of the GUI journey
#: read its private `filtered_state`. 1.64 wrapped that object in a documented
#: tester-facing one, and the reach began reporting as a missing *key*
#: (`filtered_state not found in session_state`) on all five fixtures -- a
#: state defect's error message for an API change, on a branch whose local
#: gate was green because the developer's venv was six releases behind.
_PRIVATE_STREAMLIT_REACHES = {
    ("test_gui_journey.py", "filtered_state"):
        "the <= 1.63 half of _carry()'s version straddle, reached only when the "
        "public to_dict() introduced in 1.64 is absent -- the compatibility "
        "fallback itself, not an unguarded reach; see that helper's docstring",
}

#: Spellings that leave the documented API. `session_state._foo` and
#: `AppTest._session_state` are private by name; `streamlit.runtime` is the
#: server internals, which a test driving `AppTest` has no business importing;
#: `filtered_state` is named outright because it is private without looking it.
_PRIVATE_SPELLINGS = (
    r"\.filtered_state\b",
    r"\bsession_state\._\w+",
    r"\._session_state\b",
    r"\bfrom streamlit\.runtime\b",
    r"\bimport streamlit\.runtime\b",
)


def _private_streamlit_hits():
    """Every private-Streamlit reach in `tests/`, as (file, spelling) pairs."""
    hits = set()
    tests_dir = os.path.join(_ROOT, "tests")
    # This file is skipped, and must be: it is where the forbidden spellings
    # are written down, so it matches every one of them by construction.
    owner = os.path.basename(__file__)
    for name in sorted(os.listdir(tests_dir)):
        if not name.endswith(".py") or name == owner:
            continue
        body = _read(os.path.join(tests_dir, name))
        for pattern in _PRIVATE_SPELLINGS:
            for match in re.findall(pattern, body):
                hits.add((name, match.lstrip(".").strip()))
    return hits


def test_the_gui_tests_reach_no_undeclared_streamlit_internal():
    """The unbounded dependency ceiling (above) makes CI meet each new Streamlit
    first **on purpose**. That early warning is only worth having if what it
    catches is an upstream change to the API this suite actually agreed to use
    -- a test reaching into internals turns the warning into noise, and worse,
    into noise whose message describes the wrong thing entirely.

    So every reach is declared with a reason, or it is a failure here. This is
    the same shape as the ceiling policy it protects: the decision is written
    down where the next author meets it, not left implicit in a line of code
    that happens to work on the version installed today.

    The claim is exactly *undeclared*, and no more: an entry admits a spelling
    in a file, so it cannot tell a version straddle's guarded fallback from a
    bare reach beside it. What keeps that honest is the reason string, which
    names the shape it is admitting -- a second, different reach in the same
    file would be a lie told in prose rather than an assertion evaded."""
    for name, spelling in sorted(_private_streamlit_hits()):
        assert (name, spelling) in _PRIVATE_STREAMLIT_REACHES, (
            f"{name} reaches Streamlit's private {spelling!r} with no entry in "
            "_PRIVATE_STREAMLIT_REACHES. Use the public API if one exists; if "
            "none does, declare the reach and say why -- an undeclared one "
            "fails on an upstream release with an error that names a key, not "
            "an API"
        )


def test_the_declared_streamlit_reaches_are_not_stale():
    """An exemption outlives its reason silently. When the floor rises past the
    version a straddle was written for, the entry here is what says so."""
    hits = _private_streamlit_hits()
    for key, reason in _PRIVATE_STREAMLIT_REACHES.items():
        assert key in hits, (
            f"_PRIVATE_STREAMLIT_REACHES still exempts {key} -- {reason} -- but "
            "no test makes that reach any more; delete the entry"
        )



# --------------------------------------------------------------------------- #
# The tag precondition and its script cannot drift apart (#184)
# --------------------------------------------------------------------------- #
def test_the_tag_step_names_the_green_main_check_and_the_script_offers_it():
    """§4 step 4 tags after the merge, but coverage runs only on that push to
    `main`, "fixed forward", and the rebased tree is not the PR's -- and 0.8.0
    was tagged while that run was red at install (#132). The precondition is a
    scripted check (`--check-main-run`), kept beside `--check` because both
    need the `gh` credential CI does not have; this test is the credential-free
    hop: the doc must name the check, and the script must actually offer it,
    so neither can be edited away without the other noticing (#184).
    """
    release = _read(_RELEASE)
    step4 = release[release.index("4. **Tag"):]
    step4 = step4[:step4.index("5. **")]
    assert "--check-main-run" in step4, (
        "RELEASE_PROCESS.md §4 step 4 no longer names the "
        "branch_protection_snapshot.py --check-main-run precondition -- the "
        "tag-on-red half of #132 is open again (#184)"
    )
    script = _read(os.path.join(_ROOT, "scripts", "branch_protection_snapshot.py"))
    assert "--check-main-run" in script and "def check_main_run" in script, (
        "scripts/branch_protection_snapshot.py no longer offers "
        "--check-main-run, which RELEASE_PROCESS.md §4 step 4 instructs the "
        "release manager to run before tagging (#184)"
    )



def _ci_pytest_commands():
    """Every ``pytest`` invocation a ``run:`` step of ``ci.yml`` makes."""
    return [ln.split("run:", 1)[1].strip() for ln in _read(_CI).splitlines()
            if "run:" in ln and re.search(r"\bpytest\b", ln.split("run:", 1)[1])]


def test_ci_runs_the_slow_lane():
    """The per-item gate deselects ``slow`` (#308); CI is where those tests --
    the PDF compiles, the GUI journeys -- still run. A ``-m "not slow"`` added
    to a CI step would drop them from every check in silence (#322). The one
    marker CI selects is ``roundtrip``, the solver job's own subset."""
    commands = _ci_pytest_commands()
    assert commands, "no pytest step found in ci.yml -- the guard would pass vacuously"
    for cmd in commands:
        assert "slow" not in cmd, f"ci.yml deselects the slow lane: {cmd!r}"
        for selected in re.findall(r"-m\s+(\S+)", cmd):
            assert selected.strip("'\"") == "roundtrip", (
                f"ci.yml selects marker {selected} -- only the roundtrip job "
                f"selects a subset; the test job runs everything: {cmd!r}")


def test_a_misspelt_marker_is_an_error():
    """``--strict-markers`` (#322): without it ``@pytest.mark.slwo`` is a
    warning, and the test it was meant to move out of the fast lane stays in."""
    import tomllib
    with open(os.path.join(_ROOT, "pyproject.toml"), "rb") as fh:
        addopts = tomllib.load(fh)["tool"]["pytest"]["ini_options"]["addopts"]
    assert "--strict-markers" in addopts.split(), addopts


def _test_files():
    tests_dir = os.path.join(_ROOT, "tests")
    return [os.path.join(tests_dir, n) for n in sorted(os.listdir(tests_dir))
            if n.startswith("test_") and n.endswith(".py")]


def test_every_test_file_runs_on_its_own():
    """Each test file has a ``__main__`` self-runner (CLAUDE.md), and that
    runner starts: ``-p no:xdist`` unloads the plugin that owns ``addopts``'
    ``-n auto``, so 26 runners failed at startup with "unrecognized arguments:
    -n" before #322 moved them to ``-n 0``."""
    import ast
    missing, broken = [], []
    for path in _test_files():
        text = _read(path)
        tree = ast.parse(text)
        if not any(isinstance(node, ast.If)
                   and ast.unparse(node.test) in ("__name__ == '__main__'",
                                                  "'__main__' == __name__")
                   for node in tree.body):
            missing.append(os.path.basename(path))
        if re.search(r"pytest\.main\([^)]*no:xdist", text):
            broken.append(os.path.basename(path))
    assert len(_test_files()) > 100, "the walk found too few test files"
    assert not missing, f"test files with no __main__ self-runner: {missing}"
    assert not broken, f"self-runners passing -p no:xdist (use -n 0): {broken}"

if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-n", "0", "-q"]))
