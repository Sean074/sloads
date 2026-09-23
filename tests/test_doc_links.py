"""Every in-repo documentation link and cited doc path resolves (design note 61 CV-6).

Design note 61 moved 72 files in one change: 54 design notes to `docs/25_notes/`
(CV-3) and 18 record files, `CHANGELOG.md` among them, to `docs/90_record/`
(CV-4). 179 references pointed at the old locations, 11 of them from `tests/`
where a note is the standing authority for a physics figure.

A move like that is mechanical, and mechanical is exactly the failure mode a
prose rule cannot catch: nothing in the suite noticed a `docs/` link that had
stopped resolving, so a rewrite could have silently orphaned a citation and CI
would have stayed green. `CLAUDE.md` rule 3 -- a cross-cutting convention gets
a code owner plus a drift guard, never a prose rule alone -- makes the guard
part of the move rather than a follow-up, and it protects every future move as
well as this one.

Two link populations, one rule:

* Markdown links `[text](path)` in any tracked `.md`, resolved relative to the
  file that carries them.
* `docs/...` paths cited from `tests/`, `scripts/` and the packages, where a
  citation is a reference to an authority rather than a hyperlink.

External links (`http`), in-page anchors (`#section`) and `mailto:` are out of
scope: this guard is about the repository's own tree.

**`docs/90_record/` is exempt.** Design note 26 DV-1 made an archive a record
and not a document -- "do not edit" -- and a frozen block's links describe the
tree as it stood when it was written; six of them already pointed at note
numbers that a later renumbering retired. Holding a record to the live tree's
shape would mean editing the record to keep a test green, which is the wrong
way round. The live corpus is what must resolve.
"""

from __future__ import annotations

import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS = os.path.join(_ROOT, "docs")

#: Directories walked for markdown files. `.venv` and caches are not ours.
_SKIP_DIRS = {".git", ".venv", ".claude", "__pycache__", "node_modules", ".mypy_cache",
              ".pytest_cache", ".ruff_cache", "htmlcov", "build", "dist"}
#: Trees whose source files cite documentation paths in prose.
_CITING_TREES = ("tests", "scripts", "sloads", "app", "app_shell", "oracle_app")

#: `[text](target)` -- target up to the closing paren, no nested parens.
_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
#: A `docs/...` path cited anywhere in prose or a comment.
_DOC_PATH = re.compile(r"\bdocs/(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.(?:md|docx|py)\b")
_EXTERNAL = ("http://", "https://", "mailto:", "#")
#: The frozen record: a do-not-edit archive is held to the tree it was written
#: against, not to today's (see the module docstring).
_EXEMPT_TREES = (os.path.join(_DOCS, "90_record"),)

#: Trees that exist only on a developer's machine. ``reference/`` is gitignored
#: whole -- McMaster's manuals and the FAA circulars are copyright material kept
#: local (CLAUDE.md) -- so a link into it can be right and still resolve to
#: nothing on CI, which is how note 61's own closure commit went red on the
#: guard it shipped (2026-09-14). A link into a local-only tree is accepted, not
#: checked; the tree's absence is not a broken link.
_LOCAL_ONLY_TREES = (os.path.join(_ROOT, "reference"),)

#: Links that are already dead for a reason this guard must not paper over, and
#: must not guess a target for either. The `app/` Streamlit front end was
#: retired wholesale (note 60 D-60.12, #270); these two citations in a shipped
#: note point into it. Repointing them at a surviving owner is a content
#: decision for whoever knows the replacement -- tracked, not invented here.
_KNOWN_DEAD = {
    ("docs/25_notes/40_landing_load_factor_note.md", "../../app/views/landing_loads.py"),
    ("docs/25_notes/40_landing_load_factor_note.md", "../../app/views/weight_mass.py"),
}


def _markdown_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(_ROOT):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if any(dirpath.startswith(tree) for tree in _EXEMPT_TREES):
            continue
        for name in filenames:
            if name.endswith(".md"):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def _source_files():
    out = []
    for tree in _CITING_TREES:
        base = os.path.join(_ROOT, tree)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for name in filenames:
                if name.endswith(".py"):
                    out.append(os.path.join(dirpath, name))
    return sorted(out)


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def test_every_markdown_link_resolves():
    """A relative link in any `.md` points at a file that exists."""
    dangling = []
    for path in _markdown_files():
        rel_file = os.path.relpath(path, _ROOT)
        for target in _MD_LINK.findall(_read(path)):
            if target.startswith(_EXTERNAL):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            if (rel_file, clean) in _KNOWN_DEAD:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), clean))
            if any(resolved == tree or resolved.startswith(tree + os.sep)
                   for tree in _LOCAL_ONLY_TREES):
                continue
            if not os.path.exists(resolved):
                dangling.append(f"{rel_file} -> {target}")
    assert not dangling, (
        "markdown links that resolve to nothing (design note 61 CV-6) -- a move "
        "rewrote the file but not every reference to it:\n  " + "\n  ".join(dangling))


def test_every_docs_path_cited_from_source_resolves():
    """A `docs/...` path named in a test or module is a citation, and must resolve."""
    dangling = []
    for path in _source_files():
        rel_file = os.path.relpath(path, _ROOT)
        for cited in sorted(set(_DOC_PATH.findall(_read(path)))):
            if not os.path.exists(os.path.join(_ROOT, cited)):
                dangling.append(f"{rel_file} -> {cited}")
    assert not dangling, (
        "documentation paths cited from source that resolve to nothing "
        "(design note 61 CV-6):\n  " + "\n  ".join(dangling))


def test_the_two_corpora_exist_and_are_not_empty():
    """CV-3/CV-4 filed the tree by function; the guard states the shape it left."""
    for corpus in ("25_notes", "90_record"):
        base = os.path.join(_DOCS, corpus)
        assert os.path.isdir(base), f"docs/{corpus}/ is missing (design note 61)"
        assert os.listdir(base), f"docs/{corpus}/ is empty (design note 61)"
    assert not os.path.exists(os.path.join(_DOCS, "40_history")), (
        "docs/40_history/ is back -- design note 61 CV-3 split it by function: "
        "design notes to 25_notes/, the narrative record to 90_record/")


@pytest.mark.parametrize("stray", ["CHANGELOG.md"])
def test_the_record_does_not_creep_back_to_the_repository_root(stray):
    """CV-4 put the changelog in the record corpus; a root copy would be a second one."""
    assert not os.path.exists(os.path.join(_ROOT, stray)), (
        f"{stray} is at the repository root again -- design note 61 CV-4 keeps it "
        "at docs/90_record/ so it stays out of the default search path")


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-q"]))
