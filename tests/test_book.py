"""The user's book stages whole, and every link in it lands somewhere (#427).

`scripts/build_book.py` selects the documentation a *user* reads, stages it as
a self-contained tree and rewrites every link that would otherwise leave it.
The published site is built from that tree on the push to `main` -- which is the
worst moment to learn that a chapter was renamed or a link went dead. These
guards stage the book on every run of the suite, with no site generator
installed, so the failure is the developer's and not the deploy's.

What is checked is the *staged output*, read back independently of the code
that wrote it: the first draft of the script skipped every link whose text was
in backticks, reported success, and only the generator's strict build noticed.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS = os.path.join(_ROOT, "docs")

#: Any `](target)` at all -- deliberately looser than the script's own pattern,
#: so a link the script failed to recognise is still read here.
_TARGET = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_FENCE = re.compile(r"^\s*(```|~~~)")
_NOT_A_FILE = ("http://", "https://", "mailto:", "#")
#: The developer-facing trees: linked from the book by URL, never staged into it.
_NOT_IN_THE_BOOK = ("25_notes", "30_future", "50_reviews", "90_record")


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def bb():
    return _load(os.path.join("scripts", "build_book.py"), "build_book")


@pytest.fixture(scope="module")
def staged(bb, tmp_path_factory):
    out = str(tmp_path_factory.mktemp("book"))
    errors = bb.stage(out)
    assert not errors, "the book does not stage:\n  " + "\n  ".join(errors)
    return out


def _staged_markdown(staged):
    docs = os.path.join(staged, "docs")
    for dirpath, _, names in os.walk(docs):
        for name in names:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def _file_targets(path):
    """Every link target in a staged page that names a file, outside fenced code."""
    fenced = False
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if _FENCE.match(line):
                fenced = not fenced
            if fenced:
                continue
            line = re.sub(r"`[^`]*\]\([^`]*`", "", line)  # `[a](b)` shown as syntax
            for m in _TARGET.finditer(line):
                if not m.group(1).startswith(_NOT_A_FILE):
                    yield m.group(1).partition("#")[0]


def test_every_link_in_the_staged_book_resolves_inside_it(staged):
    docs = os.path.realpath(os.path.join(staged, "docs"))
    bad = []
    for page in _staged_markdown(staged):
        for target in _file_targets(page):
            dest = os.path.realpath(os.path.join(os.path.dirname(page), target))
            if not dest.startswith(docs + os.sep) or not os.path.exists(dest):
                bad.append(f"{os.path.relpath(page, docs)}: {target}")
    assert not bad, (
        "links in the staged book that resolve to nothing inside it -- "
        "scripts/build_book.py left them unrewritten:\n  " + "\n  ".join(bad))


def test_every_nav_entry_is_a_staged_page(bb, staged):
    config = open(os.path.join(staged, "mkdocs.yml"), encoding="utf-8").read()
    named = re.findall(r'"([^"]+\.md)"\s*$', config, re.M)
    assert named, "no nav entry parsed out of the staged mkdocs.yml -- re-check this guard"
    missing = [n for n in named if not os.path.isfile(os.path.join(staged, "docs", n))]
    assert not missing, f"nav entries with no staged page: {missing}"
    assert "index.md" in named, "the book has no landing page"
    listed = [src for _, pages in bb.book() for src, _ in pages]
    assert len(listed) == len(set(listed)) == len(named), "a page is in the nav twice"


def test_every_guide_chapter_is_in_the_book(bb):
    """The chapter list is the workflow's (G-UG-1), and the script's copy of the
    guide's front-matter set is `tests/test_guide.py`'s: a chapter added to the
    workflow, or a front-matter file added to the guide, cannot be left out."""
    guide = _load(os.path.join("tests", "test_guide.py"), "test_guide_for_book")
    assert set(bb.GUIDE_FRONT_MATTER) == guide._FRONT_MATTER
    listed = {src for _, pages in bb.book() for src, _ in pages}
    chapters = {f"docs/60_guide/{name}" for name in guide._chapter_files()}
    assert chapters <= listed, f"oracle chapters missing from the book: {sorted(chapters - listed)}"
    lettered = {f"docs/60_guide/{n}" for n in os.listdir(os.path.join(_DOCS, "60_guide"))
                if n.endswith(".md")}
    assert lettered <= listed, f"guide files missing from the book: {sorted(lettered - listed)}"


def test_every_theory_file_is_in_the_book(bb):
    listed = {src for _, pages in bb.book() for src, _ in pages}
    theory = {f"docs/20_theory/{n}" for n in os.listdir(os.path.join(_DOCS, "20_theory"))
              if n.endswith(".md")}
    assert theory <= listed, (
        f"20_theory files missing from the book: {sorted(theory - listed)} -- a user "
        "reads the whole theory tree; add the file to scripts/build_book.py's book()")


def test_no_developer_tree_is_staged(staged):
    docs = os.path.join(staged, "docs")
    present = [d for d in _NOT_IN_THE_BOOK if os.path.exists(os.path.join(docs, d))]
    assert not present, f"developer-facing trees staged into the user's book: {present}"


def test_out_of_book_links_point_at_the_ref(bb, tmp_path):
    out = str(tmp_path / "book")
    assert not bb.stage(out, ref="v9.9.9")
    text = "".join(open(p, encoding="utf-8").read() for p in _staged_markdown(out))
    urls = re.findall(re.escape(bb.REPO_URL) + r"/(?:blob|tree)/([^/]+)/", text)
    assert urls, "no out-of-book link was rewritten to a repository URL -- re-check this guard"
    assert set(urls) == {"v9.9.9"}, f"repository links at a ref other than the one asked for: {set(urls)}"


def test_the_guard_would_catch_a_broken_and_an_unrewritten_link(bb, tmp_path, monkeypatch):
    """Both halves: the script reports a link to nothing, and the read-back
    above reports a link the script passed through without rewriting."""
    # A scratch tree, its paths assembled so that no line of this file reads
    # as a citation of a real document (tests/test_doc_links.py scans for them).
    root, d = tmp_path / "repo", "docs"
    (root / d / "60_guide" / "_generated").mkdir(parents=True)
    (root / d / "25_notes").mkdir()
    (root / d / "25_notes" / "n.md").write_text("# N\n", encoding="utf-8")
    (root / d / "a.md").write_text(
        "# A\n[gone](nowhere.md) [`note`](25_notes/n.md) [wrapped\nnote](25_notes/n.md)\n"
        "`[syntax](nowhere.md)`\n", encoding="utf-8")
    monkeypatch.setattr(bb, "ROOT", str(root))
    monkeypatch.setattr(bb, "DOCS", str(root / d))
    monkeypatch.setattr(bb, "book", lambda: [("S", [(f"{d}/a.md", None)])])
    out = str(tmp_path / "out")
    errors = bb.stage(out)
    assert errors == [f"{d}/a.md: broken link: nowhere.md"], errors
    page = os.path.join(out, d, "a.md")
    staged_text = open(page, encoding="utf-8").read()
    assert staged_text.count(f"{bb.REPO_URL}/blob/main/{d}/25_notes/n.md") == 2, staged_text
    assert "`[syntax](nowhere.md)`" in staged_text
    assert list(_file_targets(page)) == ["nowhere.md"]


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-n", "0", "-q"]))
