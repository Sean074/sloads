"""Documentation-currency guards: no volatile literals in the standard docs, the
retired ULTIMATE contract nowhere a user reads, the release state owned once,
`docs/00_INDEX.md` equal to its generator's output, and every test a standard
doc cites alive.

Two documentation defect classes kept shipping past the structural guards
(2026-08-15 review R6-D1…D8; `00_program_overview.md` said "schema currently 15"
while the constant was 52): a **number in prose that describes the code's
current state** (schema version, test count, coverage, "currently N"), and a
**doc file with no `00_INDEX.md` row** (or a row whose file is gone). Prose
cannot hold either current, so the first is asserted by pattern and the second
by generating the index (`scripts/build_index.py`, #359) — the same posture
`test_package_layout.py` takes for the package tree.

Scope is the *standard* — `README.md`, `CLAUDE.md`, `docs/00_INDEX.md`,
`docs/10_standard/`, `docs/20_theory/`. Plan notes, history and reviews are
dated statements and may carry any number; `DATA_DICTIONARY.md` is generated
and legitimately prints the schema version.

Stable facts are not volatile: `schema v46` as *provenance* ("added at v46")
never rots and is allowed; `SCHEMA_VERSION` next to a number is a claim about
*now* and is not. Rule text: `00_program_overview.md` §"Documentation currency".
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS = os.path.join(_ROOT, "docs")
_INDEX = os.path.join(_DOCS, "00_INDEX.md")
_INDEX_SCRIPT = os.path.join(_ROOT, "scripts", "build_index.py")


def _md_in(sub):
    return sorted(os.path.join("docs", sub, f) for f in os.listdir(os.path.join(_DOCS, sub)) if f.endswith(".md"))


#: Files whose prose must not state the code's current numbers.
_STANDARD_DOCS = (
    ["README.md", "CLAUDE.md", os.path.join("docs", "00_INDEX.md")] + _md_in("10_standard") + _md_in("20_theory")
)
_GENERATED = {os.path.join("docs", "10_standard", "DATA_DICTIONARY.md")}

#: (name, pattern) — each is a claim about the code's *current* state that a
#: constant, CI, or a generated file owns instead. Word-form numbers ("two
#: tests") and provenance citations ("schema v46") are deliberately not matched.
VOLATILE = [
    ("SCHEMA_VERSION with a number", re.compile(r"SCHEMA_VERSION\W{0,8}\d")),
    ("'currently' with a number", re.compile(r"\bcurrently\W{0,4}\d")),
    ("a test count", re.compile(r"\b\d[\d,]*\s+tests?\b")),
    ("a test-file count", re.compile(r"\b\d[\d,]*\s+test files\b")),
    ("a coverage percentage", re.compile(r"\bcoverage\W{0,20}\d+\s?%")),
    ("a version-is-now claim", re.compile(r"\bversion\W{0,4}(?:is|currently|now)\W{0,4}\d")),
    ("an item/commit count", re.compile(r"\b\d[\d,]*\s+(?:open |backlog )?(?:items|commits)\b")),
    # CR-D-5 (2026-08-20 review): `streamlit>=1.30` sat in the overview against a
    # real `>=1.36`. A version floor is `pyproject.toml`'s to state; a copy of one
    # is a claim about now, and this class was invisible to the patterns above.
    ("a dependency version specifier", re.compile(r"[A-Za-z][\w.-]*\s*[<>~!=]=\s*\d")),
]


def _lines(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read().splitlines()


@pytest.mark.parametrize("rel", [d for d in _STANDARD_DOCS if d not in _GENERATED])
def test_standard_doc_states_no_volatile_literal(rel):
    hits = []
    for n, line in enumerate(_lines(rel), 1):
        for name, pat in VOLATILE:
            if pat.search(line):
                hits.append(f"{rel}:{n}: {name} — {line.strip()[:100]}")
    assert not hits, (
        "volatile literal(s) in a standard doc — point at the owner (constant / CI / generated file) instead:\n  "
        + "\n  ".join(hits)
    )


# --- The retired ULTIMATE-deliverable contract -----------------------------

#: (name, pattern) — each is a sentence of the contract note 49 OR-116
#: *reversed*: every delivered load is LIMIT with the factor stated and applied
#: nowhere. These exact claims survived the OR-116 sweep in `CAPABILITIES.md`
#: and `SUMMARY_REPORT.md` for a year because no guard read them (found by the
#: 0.8.8 pre-release review) — a capability summary stating the old basis tells
#: an analyst *not* to apply the factor the deck did not apply. `90_record/` is
#: outside the scope on purpose: there the sentences state what was true on a
#: date.
RETIRED_CONTRACT = [
    ("the pre-OR-116 basis claim", re.compile(r"(?i)deliverable is ultimate")),
    ("ULTIMATE as what comes out", re.compile(r"(?i)ultimate\W{1,4}loads come out")),
    ("the factor applied at a render/export boundary",
     re.compile(r"(?i)factor is applied (?:once\s+)?at the")),
    ("governing loads called ultimate", re.compile(r"(?i)governing ultimate loads")),
    ("the retired ULTIMATE-twin pairing", re.compile(r"(?i)pairs? with an ultimate twin")),
    # #402 (review D-1): the five above are the *producer's* side of the claim.
    # `GUI_USER_GUIDE.md` §5 taught the same model from the *reader's* side --
    # "`-ULT` ... ultimate and ready for sizing", "do not export those numbers",
    # "still an ultimate deliverable" -- in lower case, and shipped past this
    # guard for a year. A reader who believes any of these skips the 1.5.
    ("a delivered number called ready for sizing", re.compile(r"(?i)ready for sizing")),
    ("limit numbers the reader is told not to export",
     re.compile(r"(?i)do not export (?:those|these|the) numbers")),
    ("SF=1.0 called still an ultimate deliverable", re.compile(r"(?i)still an ultimate")),
    ("exported as a synonym for ultimate",
     re.compile(r"(?i)export(?:ed|s)?\W{1,3}(?:=|is|are|means) ultimate")),
]

#: (name, pattern) -- an output the front-end that retired at #270 offered,
#: stated as if it still ships (#402, review D-5). `CAPABILITIES.md` §2 went on
#: advertising the workbook, the dashboard and the Results Review / Export phase
#: for two milestones after their deletion. Scoped to the documents a *user*
#: reads: `PROGRAM_SPEC.md` and `ORACLE_REPORT.md` record the same words as
#: history ("Workbook export bridge -- RETIRED") and stay outside on purpose.
RETIRED_OUTPUTS = [
    ("the workbook export (deleted at #270)", re.compile(r"(?i)\bworkbook export\b")),
    ("the Results Review / Export phase (deleted at #270)",
     re.compile(r"(?i)results review\s*/\s*export")),
    ("the dashboard (deleted at #270)", re.compile(r"(?i)\bdashboard with\b")),
    ("the Export page's downloads (deleted at #270)",
     re.compile(r"(?i)\bexport page'?s? (?:download|zip|bundle)")),
]

#: `CAPABILITIES.md` is where the class was found, and it sits outside
#: `_STANDARD_DOCS`' volatile-number scope; the contract scan reads it too.
#: `docs/60_guide/` joined at #402: it is the chapter that teaches the contract,
#: and G-OR-74's sweep of it (`test_basis_statements.py`) reads only the
#: upper-case ``ULTIMATE`` spellings.
_CONTRACT_DOCS = [d for d in _STANDARD_DOCS if d not in _GENERATED] + [
    "CAPABILITIES.md", "CONTRIBUTING.md",
] + _md_in("60_guide")

#: What a user reads first: the outputs scan is held to these.
_USER_DOCS = [
    "README.md", "CAPABILITIES.md", "CONTRIBUTING.md",
    os.path.join("docs", "10_standard", "GUI_USER_GUIDE.md"),
] + _md_in("60_guide")


def _paragraphs(rel):
    """``(first_line_number, text)`` per paragraph, whitespace collapsed.

    A claim wraps -- §5 wrote "it is still an / ultimate deliverable" across a
    line break -- so the retired-claim scans read paragraphs, not lines.
    """
    out, start, buf = [], None, []
    for n, line in enumerate(_lines(rel) + [""], 1):
        if line.strip():
            if start is None:
                start = n
            buf.append(line.strip())
        elif buf:
            out.append((start, " ".join(buf)))
            start, buf = None, []
    return out


def _retired_hits(rel, patterns):
    hits = []
    for n, text in _paragraphs(rel):
        for name, pat in patterns:
            m = pat.search(text)
            if m:
                hits.append(f"{rel}:{n}: {name} — …{text[max(0, m.start() - 40):m.end() + 40]}…")
    return hits


@pytest.mark.parametrize("rel", _CONTRACT_DOCS)
def test_no_current_truth_doc_states_the_retired_ultimate_contract(rel):
    hits = _retired_hits(rel, RETIRED_CONTRACT)
    assert not hits, (
        "the retired ULTIMATE-deliverable contract in a current-truth doc — every "
        "delivered load is LIMIT with the factor stated, never applied (note 49 "
        "OR-116; CLAUDE.md §Load-output contract):\n  " + "\n  ".join(hits)
    )


@pytest.mark.parametrize("rel", _USER_DOCS)
def test_no_user_doc_advertises_an_output_retired_at_270(rel):
    hits = _retired_hits(rel, RETIRED_OUTPUTS)
    assert not hits, (
        "a user-facing doc advertises an output the front-end retired at #270 "
        "(design note 57 D-57.1); what ships is `workflow.gui_pages()`, the report "
        "issue package and the CLI export targets:\n  " + "\n  ".join(hits)
    )


#: One real sentence per retired pattern, quoted from the document that
#: shipped it (#402). Kept as data so the meta-test can prove both directions:
#: every witness fails its scan, and every pattern catches some witness.
_RETIRED_WITNESSES = (
    "The deliverable is ULTIMATE.",
    "Ultimate loads come out of the export.",
    "The factor is applied once at the render/export boundary.",
    "the governing ultimate loads",
    "each limit case pairs with an ultimate twin",
    # GUI_USER_GUIDE.md §5, as shipped until #402 -- the line break is real
    "If it is there, the number is\n   ultimate and ready for sizing.",
    "confirm the page is a per-module *analysis* page — do not export those\n   numbers as-is.",
    "it is still an\n   ultimate deliverable, not a limit load.",
    "exported = ultimate",
)
_OUTPUT_WITNESSES = (
    "- **Workbook export** — a multi-sheet spreadsheet with per-sheet unit statements.",
    "- **Interactive GUI** — dashboard with workflow status and validation warnings",
    "selection**, and a Results Review / Export phase.",
    "the Export page's download row and its bundle `.zip`",
)


def test_the_retired_claim_guards_would_catch_each_spelling(tmp_path, monkeypatch):
    """The guards' teeth: each witness trips its scan, each pattern is exercised,
    and the true sentences beside them pass."""
    monkeypatch.setattr(sys.modules[__name__], "_ROOT", str(tmp_path))
    for witnesses, patterns in ((_RETIRED_WITNESSES, RETIRED_CONTRACT),
                                (_OUTPUT_WITNESSES, RETIRED_OUTPUTS)):
        for i, witness in enumerate(witnesses):
            rel = f"w{i}.md"
            (tmp_path / rel).write_text(witness, encoding="utf-8")
            assert _retired_hits(rel, patterns), f"no pattern caught {witness!r}"
        for name, pat in patterns:
            assert any(pat.search(" ".join(w.split())) for w in witnesses), (
                f"no witness exercises {name!r}")
    # the sentences that are true survive both scans
    for ok in (
        "`SF=1.0` | nothing to apply — the case is already ultimate",
        "Every load sloads delivers is LIMIT, and it is your sizing analysis that applies the factor.",
        "### Workbook export bridge — RETIRED (Step D8.2; deleted at #270)",
    ):
        (tmp_path / "ok.md").write_text(ok, encoding="utf-8")
        assert not _retired_hits("ok.md", RETIRED_CONTRACT), ok
    # ...but the historical heading is true only outside the user-doc scope
    assert "docs/10_standard/PROGRAM_SPEC.md" not in _USER_DOCS


# --- INDEX = the generator's output (#359) ---------------------------------


def test_the_index_is_the_generator_output():
    """`docs/00_INDEX.md` is generated from each document's own H1 by
    `scripts/build_index.py`: a file with no row, a row with no file, or a row
    that says something the document does not, all show up as one diff. Run
    `scripts/build_index.py --write` after adding, removing or retitling a doc."""
    spec = importlib.util.spec_from_file_location("build_index", _INDEX_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with open(_INDEX, encoding="utf-8") as fh:
        committed = fh.read()
    assert mod.render() == committed, (
        "docs/00_INDEX.md differs from scripts/build_index.py's output — run "
        "`.venv/bin/python scripts/build_index.py --write` and commit the result")


# --------------------------------------------------------------------------- #
# The standard tree holds only guardable text formats (#189)
# --------------------------------------------------------------------------- #
# GIT_FLOW_GUIDE.docx sat in 10_standard/ advertising the squash flow the
# process retired at the 0.7.2 cut -- a binary doc's currency rests on a prose
# promise no test can check (precedent: CR-D-4, two docs stating a dead
# setting). Standard docs must be formats the guards in this file can read.
_GUARDABLE_EXT = {".md", ".txt"}


def test_the_standard_tree_holds_only_guardable_text_formats():
    binaries = sorted(
        f for f in os.listdir(os.path.join(_DOCS, "10_standard"))
        if os.path.splitext(f)[1] not in _GUARDABLE_EXT
    )
    assert not binaries, (
        "docs/10_standard/ files no drift guard can read (#189) -- demote them "
        f"to docs/90_record/ or convert to markdown: {binaries}")


# --------------------------------------------------------------------------- #
# The release-state statement has one owner (owner ruling 2026-08-28,
# production-release review §3.5/§5.3)
# --------------------------------------------------------------------------- #
#: The documents that must carry the release-state sentence verbatim. Markdown
#: cannot import a symbol, so "one owner" is enforced the only way prose allows:
#: the owner's exact string has to appear, and a second spelling of it must not.
_RELEASE_STATE_DOCS = ("README.md", "CAPABILITIES.md")

#: Files allowed to hold the sentence *as a literal* -- the owner itself, this
#: guard, and the two documents above. Anywhere else is a second copy.
_RELEASE_STATE_OWNER = os.path.join("app_shell", "components.py")


def test_the_release_state_is_stated_by_one_owner():
    """`README.md`, `CAPABILITIES.md` and the GUI's About panel say the same
    thing about what this release is, because they all trace to one string.
    The two markdown files cannot import the constant, so their copies are
    pinned to it here."""
    from app_shell.components import RELEASE_STATE

    for rel in _RELEASE_STATE_DOCS:
        with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
            assert RELEASE_STATE in fh.read(), (
                f"{rel} does not carry app_shell.components.RELEASE_STATE verbatim -- "
                "update the document in the same change as the constant")

    with open(os.path.join(_ROOT, "app_shell", "sidebar.py"), encoding="utf-8") as fh:
        assert "RELEASE_STATE" in fh.read(), "the About panel must consume the owner"


def test_no_second_spelling_of_the_release_state():
    """A literal copy anywhere outside the owner and the two documents it pins."""
    from app_shell.components import RELEASE_STATE

    # A distinctive fragment rather than the whole sentence: a second copy that
    # drifted by a word is exactly the case this must still catch.
    fragment = RELEASE_STATE.split(";")[0].strip()
    allowed = {os.path.normpath(p) for p in
               (_RELEASE_STATE_OWNER, os.path.join("tests", "test_doc_currency.py"))
               } | {os.path.normpath(d) for d in _RELEASE_STATE_DOCS}
    offenders = []
    for base, dirs, files in os.walk(_ROOT):
        dirs[:] = [d for d in dirs if d not in
                   {".git", ".venv", ".claude", "__pycache__", ".pytest_cache", "reference",
                    "sloads.egg-info", "_to_delete", "_staging_tmp2", "projects"}]
        for name in files:
            if not name.endswith((".py", ".md", ".toml")):
                continue
            rel = os.path.normpath(os.path.relpath(os.path.join(base, name), _ROOT))
            if rel in allowed:
                continue
            with open(os.path.join(base, name), encoding="utf-8", errors="ignore") as fh:
                if fragment in fh.read():
                    offenders.append(rel)
    assert not offenders, (
        "the release-state sentence is spelled a second time in "
        f"{offenders} -- import app_shell.components.RELEASE_STATE instead")


# --------------------------------------------------------------------------- #
# A standard doc's conformance table must name tests that exist
# --------------------------------------------------------------------------- #
#: How a standard doc cites a test: ``file.py::test_name`` for the first of a
#: group and a bare ``::test_name`` for each one after it, which is the shorthand
#: the conformance tables actually use.
_TEST_CITE = re.compile(r"`(?:tests/)?(test_[a-z0-9_]+\.py)::(test_[a-z0-9_]+)`")
_TEST_CITE_SHORT = re.compile(r"`::(test_[a-z0-9_]+)`")


def _defined_tests():
    """``{file: {test names}}`` across ``tests/``, plus the flat union."""
    by_file, every = {}, set()
    tests_dir = os.path.join(_ROOT, "tests")
    for name in sorted(os.listdir(tests_dir)):
        if not (name.startswith("test_") and name.endswith(".py")):
            continue
        with open(os.path.join(tests_dir, name), encoding="utf-8") as fh:
            found = set(re.findall(r"^def (test_\w+)", fh.read(), re.M))
        by_file[name] = found
        every |= found
    return by_file, every


@pytest.mark.parametrize("rel", _STANDARD_DOCS)
def test_every_test_a_standard_doc_cites_exists(rel):
    """A conformance row that names a deleted test asserts nothing.

    Found by hand on 2026-09-05: `ORACLE_REPORT.md`'s conformance table still
    named two tests note 49 OR-116 had renamed, so two rows claiming the
    report's load basis was gated pointed at nothing. Only the two citation
    forms the tables use are matched, so prose that merely mentions a function
    cannot satisfy or break this.
    """
    by_file, every = _defined_tests()
    path = os.path.join(_ROOT, rel)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    dead = []
    for file_name, test in _TEST_CITE.findall(text):
        if file_name not in by_file:
            dead.append(f"{file_name}::{test} (no such test file)")
        elif test not in by_file[file_name]:
            dead.append(f"{file_name}::{test}")
    for test in _TEST_CITE_SHORT.findall(text):
        # The short form names no file, so it is satisfied by any test file --
        # shorthand for "another test in the group above".
        if test not in every:
            dead.append(f"::{test}")
    assert not dead, (
        f"{rel} cites test(s) that no longer exist: {dead}. A conformance row "
        f"naming a deleted test claims a gate that is not there.")


def test_the_citation_guard_would_catch_a_renamed_test():
    """The guard's teeth: the exact pair it was written for, and the two forms."""
    _by_file, every = _defined_tests()
    assert "test_no_load_the_wing_section_prints_is_marked_ultimate" in every
    assert "test_every_load_the_wing_section_prints_is_marked_ultimate" not in every
    assert _TEST_CITE.findall("see `test_oracle_report.py::test_a_thing`") == [
        ("test_oracle_report.py", "test_a_thing")]
    assert _TEST_CITE_SHORT.findall("and `::test_another_thing`") == [
        "test_another_thing"]
    # prose naming a non-test function is not a citation
    assert not _TEST_CITE_SHORT.findall("`::build_report`")


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-n", "0", "-q"]))
