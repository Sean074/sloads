"""Documentation-currency guards: no volatile literals in the standard docs, and
`docs/00_INDEX.md` ↔ the docs tree, both ways.

Two documentation defect classes kept shipping past the structural guards
(2026-08-15 review R6-D1…D8; `00_program_overview.md` said "schema currently 15"
while the constant was 52): a **number in prose that describes the code's
current state** (schema version, test count, coverage, "currently N"), and a
**doc file with no `00_INDEX.md` row** (or a row whose file is gone). Prose
cannot hold either current, so this asserts both — the same posture
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

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS = os.path.join(_ROOT, "docs")
_INDEX = os.path.join(_DOCS, "00_INDEX.md")

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


# --- INDEX ↔ tree ---------------------------------------------------------

_INDEX_LINK = re.compile(r"\]\(((?:[0-9]{2}_[a-z_]+|\.\.)/[^)#]+\.md)\)")


def _docs_tree():
    out = set()
    for sub in sorted(os.listdir(_DOCS)):
        d = os.path.join(_DOCS, sub)
        if not os.path.isdir(d) or sub.startswith("__"):
            continue
        for f in os.listdir(d):
            if f.endswith(".md"):
                out.add(f"{sub}/{f}")
    return out


def _index_links():
    with open(_INDEX, encoding="utf-8") as fh:
        return set(_INDEX_LINK.findall(fh.read()))


def test_every_doc_has_an_index_row():
    missing = sorted(_docs_tree() - _index_links())
    assert not missing, f"docs/ files with no row in docs/00_INDEX.md: {missing}"


def test_every_index_row_points_at_a_file():
    dangling = sorted(
        link for link in _index_links() if not os.path.exists(os.path.normpath(os.path.join(_DOCS, link)))
    )
    assert not dangling, f"docs/00_INDEX.md rows whose file does not exist: {dangling}"


# --------------------------------------------------------------------------- #
# A live note's INDEX row is a pointer, not a second copy of the note (#187)
# --------------------------------------------------------------------------- #
# Note 44's row grew to ~600 words restating OR-13..OR-37 with its own copy of
# the status, and the 46/47 rows mirrored the stale AGREED that #183 fixed in
# the notes themselves -- a second hand-maintained statement per note, the
# rule-3 drift class. A `30_future/` row is one sentence plus the pointer and
# carries **no status**: the note's own Status line is the single owner.
# `40_history/` rows are exempt -- an archived note's status can never change
# again, so those rows are frozen record, not a drift surface.
_LIVE_ROW_CAP = 320
_STATUS_WORD = re.compile(r"\b(AGREED|SHIPPED|BUILT|PROPOSED)\b")


def test_a_live_note_index_row_is_one_line_and_states_no_status():
    offenders = []
    with open(_INDEX, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("| [`") or "](30_future/" not in line:
                continue
            name = line.split("[`", 1)[1].split("`]", 1)[0]
            if len(line.rstrip()) > _LIVE_ROW_CAP:
                offenders.append(f"{name}: {len(line.rstrip())} chars (cap {_LIVE_ROW_CAP})")
            claim = _STATUS_WORD.search(line)
            if claim:
                offenders.append(f"{name}: states a status ({claim.group(0)}) -- "
                                 "the note's own Status line is the single owner")
    assert not offenders, (
        "docs/00_INDEX.md rows for live 30_future/ files must be one sentence "
        "plus the pointer, no status (#187):\n  " + "\n  ".join(offenders))


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
        f"to docs/40_history/ or convert to markdown: {binaries}")


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
    """`README.md`, `CAPABILITIES.md` and both GUIs' About panel say the same
    thing about what this release is, because they all trace to one string.

    The claim is mixed by nature -- an oracle GUI that is finished beside an
    `app/` that is not -- and `Development Status` takes a single trove value,
    so `pyproject.toml` carries `4 - Beta` and the sentence carries the rest.
    Four hand-written copies of that sentence would disagree by the second cut,
    which is the documentation-currency failure this whole file exists for; the
    two markdown files cannot import the constant, so their copies are pinned
    to it here instead.
    """
    from app_shell.components import RELEASE_STATE

    for rel in _RELEASE_STATE_DOCS:
        with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
            assert RELEASE_STATE in fh.read(), (
                f"{rel} does not carry app_shell.components.RELEASE_STATE verbatim -- "
                "update the document in the same change as the constant")

    # The About panel consumes the symbol rather than re-typing the sentence, so
    # a user in the beta front-end is told so by the same owner (#129's sibling
    # concern: the classifier is read by pip, not by them).
    with open(os.path.join(_ROOT, "app_shell", "sidebar.py"), encoding="utf-8") as fh:
        assert "RELEASE_STATE" in fh.read(), "the About panel must consume the owner"


def test_no_second_spelling_of_the_release_state():
    """A literal copy anywhere outside the owner and the two documents it pins.

    The `LANDING_L_FAR_CAPTION` posture (`tests/test_landing.py`): stating the
    string once is only half of one owner -- the other half is that nobody
    spells it again somewhere the guard above would never look.
    """
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
                   {".git", ".venv", "__pycache__", ".pytest_cache", "reference",
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
# A design note cannot claim work is unbuilt after it has shipped (#128)
# --------------------------------------------------------------------------- #
# It blocks a release rather than trailing it: `RELEASE_PROCESS.md` §4 step 3
# rolls the notes into `docs/40_history/` at the cut, so an "unbuilt" claim
# enters the permanent record of the release that built it. Two instances found
# together (production-release review 2026-08-27 §3.3): note 32 said "everything
# else is unbuilt" of the oracle GUI whose every step had shipped, note 35 said
# "Nothing below is built yet" of work that shipped as #100.
#
# The evidence is deliberately **in-repo**. Whether an issue is closed lives on
# GitHub, which CI has no credential to read (the same constraint
# `tests/test_ci_conformance.py` is built around) -- but a closed item leaves a
# `changes/` fragment behind by the tiered-closure rule, and that fragment cites
# the note. So the fragment is the proxy, and it is a faithful one: it exists
# because something closed.
_NOTES_DIR = os.path.join("docs", "30_future")
_CHANGES = os.path.join(_ROOT, "changes")
#: Claims that work in this note has not been done. Kept literal rather than
#: clever -- a guard that guesses at prose fails on innocent sentences, and the
#: two spellings this file exists for are the two the review found.
_UNBUILT_CLAIM = re.compile(
    r"(everything else is unbuilt"
    r"|\bis unbuilt\b"
    r"|nothing (?:below|here)[^.]{0,40}\bbuilt\b"
    r"|not built yet"
    r"|no code has been written)", re.I)
#: A note's own record that some of it shipped.
_SHIPPED_MARK = re.compile(r"(✅|\bSHIPPED\b|\bBUILT\b)")


def _design_notes():
    directory = os.path.join(_ROOT, _NOTES_DIR)
    return sorted(n for n in os.listdir(directory) if n.endswith("_note.md"))


def _fragments_citing(note_name):
    """Closure fragments that name this note (``note 35``), i.e. it shipped."""
    number = note_name.split("_", 1)[0].lstrip("0")
    cite = re.compile(rf"\bnote {number}\b", re.I)
    if not os.path.isdir(_CHANGES):
        return []
    out = []
    for name in sorted(os.listdir(_CHANGES)):
        if not name.endswith(".md") or name == "README.md":
            continue
        with open(os.path.join(_CHANGES, name), encoding="utf-8") as fh:
            if cite.search(fh.read()):
                out.append(name)
    return out


@pytest.mark.parametrize("note", _design_notes())
def test_a_design_note_does_not_claim_unbuilt_work_it_has_shipped(note):
    text = "\n".join(_lines(os.path.join(_NOTES_DIR, note)))
    claims = [m.group(0) for m in _UNBUILT_CLAIM.finditer(text)]
    if not claims:
        return
    evidence = []
    if _SHIPPED_MARK.search(text):
        evidence.append("the note itself marks work SHIPPED/BUILT/✅")
    fragments = _fragments_citing(note)
    if fragments:
        evidence.append("closure fragment(s) cite it: " + ", ".join(fragments))
    assert not evidence, (
        f"{note} still claims unbuilt work ({claims}) while {'; '.join(evidence)}. "
        "Restate the Status line for what shipped -- notes 36/37 (SHIPPED) and 34 "
        "(AGREED …; BUILT …) are the model. RELEASE_PROCESS.md §4 step 3 rolls "
        "this note into docs/40_history/ at the cut, so the claim would enter the "
        "permanent record of the release that built it (#128)."
    )


# --------------------------------------------------------------------------- #
# A note a history fragment closed against must say SHIPPED/BUILT (#183)
# --------------------------------------------------------------------------- #
# The #128 guard above fires only on explicit "unbuilt" phrasing, so a header
# left at plain AGREED after the work landed passes CI -- three of the last
# four tier-L closures did exactly that (notes 46/47/48, review R-13), and the
# 0.8.2 hygiene pass found two more the issue did not know about (50, 53). It
# matters because `RELEASE_PROCESS.md` §4 step 3 rolls notes to
# `docs/40_history/` BY STATUS HEADER: an unflipped note is skipped by the roll
# and a wrong status enters the permanent record. The evidence is the same
# in-repo proxy #128 uses, narrowed to where it is unambiguous: a
# `changes/*.history.md` fragment's own `## Step` heading names the note it
# ships (``(design note 53, tier L``); a prose mention in a fragment body
# ("until note 51 lands") is exactly what this must NOT count.
_STEP_NOTE_CITE = re.compile(r"^## Step[^(]*\((?:design )?note (\d+)\b", re.M)
#: The note's Status paragraph: from the ``**Status`` line to the first blank.
_STATUS_PARA = re.compile(r"^\*\*Status[^\n]*(?:\n(?!\n)[^\n]*)*", re.M)


def _history_shipped_notes():
    """Note numbers named in a ``## Step`` heading of a history fragment."""
    shipped = {}
    if not os.path.isdir(_CHANGES):
        return shipped
    for name in sorted(os.listdir(_CHANGES)):
        if not name.endswith(".history.md"):
            continue
        with open(os.path.join(_CHANGES, name), encoding="utf-8") as fh:
            for number in _STEP_NOTE_CITE.findall(fh.read()):
                shipped.setdefault(number, name)
    return shipped


@pytest.mark.parametrize("note", _design_notes())
def test_a_note_closed_by_a_history_fragment_says_shipped(note):
    number = note.split("_", 1)[0].lstrip("0")
    fragment = _history_shipped_notes().get(number)
    if fragment is None:
        return
    text = "\n".join(_lines(os.path.join(_NOTES_DIR, note)))
    status = _STATUS_PARA.search(text)
    assert status, f"{note} has no **Status** line to carry its shipped state"
    assert _SHIPPED_MARK.search(status.group(0)), (
        f"{note} is the design basis of changes/{fragment} (its step heading "
        f"names note {number}) but its Status paragraph carries no "
        "SHIPPED/BUILT/✅ mark. Flip the header -- RELEASE_PROCESS.md §4 "
        "step 3 rolls notes by status, so a stale AGREED skips the roll and "
        "enters the record wrong (#183)."
    )


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
    named ``test_every_load_the_wing_section_prints_is_marked_ultimate`` and
    ``test_the_wing_root_loads_are_the_limit_result_times_the_case_factor`` after
    note 49 OR-116 renamed both -- so two rows claiming the report's load basis
    was gated pointed at nothing at all. A conformance table is a promise that
    something checks the row; a dead name is that promise silently withdrawn,
    and renaming a test is exactly when it happens.

    Only the two citation forms the tables use are matched, and a name that is
    not a test is not a citation -- so this cannot be satisfied or broken by
    prose that merely mentions a function.
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
        # which is the right strictness: it is shorthand for "another test in the
        # group above", and pinning it to a file would break on a legitimate move.
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


def test_the_unbuilt_guard_would_catch_the_two_it_was_written_for():
    """A guard whose pattern no longer matches its own founding instances is a
    guard that passes because it sees nothing. These are the exact sentences
    note 32 and note 35 carried on 2026-08-27."""
    for sentence in ("an independent tier-S fix; everything else is unbuilt.",
                     "state plus the existing load increment, nothing more. "
                     "Nothing below is built yet."):
        assert _UNBUILT_CLAIM.search(sentence), sentence


# --------------------------------------------------------------------------- #
# Every shipped oracle-report guard module has a row in the standard's register
# --------------------------------------------------------------------------- #

_ORACLE_REPORT_STD = os.path.join("docs", "10_standard", "ORACLE_REPORT.md")


def _report_guard_modules():
    """Every ``tests/test_oracle_report*.py`` file, by name.

    The glob is the source, not a hand list: the defect this guard exists for
    is a shipped guard module the standard never mentions, and a hand list
    would itself be a copy that goes stale the same way.
    """
    tests_dir = os.path.join(_ROOT, "tests")
    return sorted(n for n in os.listdir(tests_dir)
                  if n.startswith("test_oracle_report") and n.endswith(".py"))


def _uncited_report_modules(text):
    return [name for name in _report_guard_modules() if name not in text]


def test_every_oracle_report_guard_module_is_cited_by_the_standard():
    """A shipped guard module the register never names is an agreement held by
    prose alone -- G-OR-8's own defect, in the standard that states G-OR-8.

    Found by the 2026-09-08 review (#238): iterations 8, 9 and 10 shipped with
    their gates in ``test_oracle_report_oei.py``, ``_landing.py`` and
    ``_vn.py``, and `ORACLE_REPORT.md` cited none of them -- nor the earlier
    ``_vtail.py`` and ``_applied.py``. `test_every_test_a_standard_doc_cites_exists`
    checks the citations that are there; this is the other direction, which is
    the one that failed.
    """
    text = "\n".join(_lines(_ORACLE_REPORT_STD))
    uncited = _uncited_report_modules(text)
    assert not uncited, (
        f"ORACLE_REPORT.md never cites {uncited}. Every shipped oracle-report "
        f"guard module needs a row in the standard's §7 register (or a "
        f"conformance entry): an agreement without a named guard is prose "
        f"(G-OR-8, #238).")


def test_the_module_citation_guard_would_catch_an_unregistered_module():
    """The guard's teeth: the five modules #238 found missing, against a doc
    that cites only the base file -- which is what the register looked like."""
    modules = _report_guard_modules()
    doc_citing_only_the_base = "see `test_oracle_report.py::test_a_thing`"
    uncited = _uncited_report_modules(doc_citing_only_the_base)
    for name in ("test_oracle_report_oei.py", "test_oracle_report_landing.py",
                 "test_oracle_report_vn.py", "test_oracle_report_vtail.py",
                 "test_oracle_report_applied.py"):
        assert name in modules, name
        assert name in uncited, name
    assert "test_oracle_report.py" not in uncited


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
