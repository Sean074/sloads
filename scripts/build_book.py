#!/usr/bin/env python
"""Stage the user's book: the documentation a *user* of sloads reads (#427).

The repository's documentation is written for two readers. A developer needs
all of it; a user needs the theory, the guides, the input-file reference and
the validation rationale, with navigation and search. This script is the single
owner of **which pages those are and in what order** (:data:`BOOK`), and it
stages them as a self-contained source tree that a static-site generator
builds without knowing anything about this repository:

    python scripts/build_book.py            # stage into build/book/
    python scripts/build_book.py --check    # stage into a temp dir; exit 1 on a problem
    python scripts/build_book.py --ref v0.10.0   # GitHub links at a tag, not `main`

    (cd build/book && zensical build --strict)   # -> build/book/site/

Nothing under ``docs/`` moves or changes. A staged page keeps its
``docs/``-relative path, so a link between two book pages is valid untouched;
every other link is rewritten here, because the generator has no hook to do it:

* target is another staged file  -> a relative link inside the staged tree;
* target exists in the repository but is not in the book (a design note, an
  example, a test) -> its GitHub URL at ``--ref``;
* target does not exist -> an error naming the page and the link.

``tests/test_book.py`` stages the book on every run of the suite, so a renamed
chapter or a dead link fails the gate, not the deploy. The staging needs no
third-party package; only the final build needs the generator (the ``docs``
extra in ``pyproject.toml``).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import sys
import tempfile
from typing import Dict, List, Optional, Tuple

from sloads._urls import BOOK_URL, REPO_URL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(ROOT, "build", "book")

SITE_NAME = "sloads"
SITE_DESCRIPTION = "FAR 23 structural design loads: user guide, theory and validation"
DEFAULT_REF = "main"

#: The guide files that share the ``NN_`` prefix space with the chapters
#: without being one (``tests/test_guide.py`` owns the rule; ``tests/
#: test_book.py`` asserts this copy against it).
GUIDE_FRONT_MATTER = (
    "00_index.md",
    "01_getting_started.md",
    "02_before_you_start.md",
    "03_conventions.md",
)

#: A page: (repository-relative source, nav title or None for the page's own H1).
Page = Tuple[str, Optional[str]]


def _guide_chapters() -> List[Page]:
    """The oracle GUI chapters, in workflow order.

    The numbered guide files that are not front matter: G-UG-1 holds that set
    equal to ``sloads.workflow.oracle_steps()`` in order, so a glob here is the
    workflow's own list without importing the package into a docs build.
    """
    names = sorted(
        n for n in os.listdir(os.path.join(DOCS, "60_guide"))
        if re.match(r"^\d{2}_.+\.md$", n) and n not in GUIDE_FRONT_MATTER
    )
    return [(f"docs/60_guide/{n}", None) for n in names]


def _theory_chapters() -> List[Page]:
    paths = sorted(glob.glob(os.path.join(DOCS, "20_theory", "ch[0-9][0-9]_*.md")))
    return [(os.path.relpath(p, ROOT).replace(os.sep, "/"), None) for p in paths]


def book() -> List[Tuple[str, List[Page]]]:
    """The book: ordered sections of pages. The only statement of its contents."""
    return [
        ("Home", [
            ("README.md", "Overview"),
            ("CAPABILITIES.md", "Capabilities"),
            ("docs/20_theory/04_scope_and_applicability.md", "Scope and limits"),
        ]),
        ("Getting started", [
            ("docs/60_guide/00_index.md", "About the guide"),
            ("docs/60_guide/01_getting_started.md", None),
            ("docs/60_guide/02_before_you_start.md", None),
            ("docs/60_guide/03_conventions.md", None),
        ]),
        ("Oracle GUI guide", _guide_chapters()),
        ("Worked examples", [
            ("docs/60_guide/A_worked_single.md", None),
            ("docs/60_guide/B_worked_twin.md", None),
            ("docs/60_guide/E_worked_concept.md", None),
        ]),
        ("GUI user guide", [
            ("docs/10_standard/GUI_USER_GUIDE.md", None),
        ]),
        ("Theory", _theory_chapters() + [
            ("docs/20_theory/00_theory_sources.md", None),
            ("docs/20_theory/02_approved_corrections.md", None),
        ]),
        # The generated per-module matrix (#413) joins this section when it
        # lands: tests/test_book.py refuses a 20_theory file that is not listed.
        ("Validation", [
            ("docs/20_theory/03_validation_rationale.md", None),
        ]),
        ("Input-file reference", [
            ("docs/10_standard/DATA_DICTIONARY.md", None),
            ("docs/10_standard/PROJECT_GUIDE.md", None),
            ("docs/10_standard/CONVENTIONS.md", None),
        ]),
        ("Troubleshooting", [
            ("docs/60_guide/F_typical_questions.md", None),
            ("docs/60_guide/C_troubleshooting.md", None),
            ("docs/60_guide/D_where_next.md", None),
        ]),
    ]


#: Pages staged without a nav entry: reached by a link from a book page (the
#: guide's generated field tables and chapter list).
UNLISTED_DIRS = ("docs/60_guide/_generated",)

#: Source files staged under another name: the two front-door files live at the
#: repository root, and ``index.md`` is the site's landing page.
_RENAMED = {"README.md": "index.md", "CAPABILITIES.md": "capabilities.md"}

#: Trees that exist only on a developer's machine (``tests/test_doc_links.py``):
#: a link into one has no public target, so its text is kept and the link dropped.
_LOCAL_ONLY = ("reference/",)

_EXTERNAL = ("http://", "https://", "mailto:")
#: ``[text](target "title")`` or ``![alt](target)``; one level of nested
#: brackets in the text, as in ``[`[x]`](y)``.
_LINK = re.compile(
    r"(?P<bang>!?)\[(?P<text>(?:[^\[\]]|\[[^\]]*\])*)\]"
    r"\((?P<target>[^)\s]+)(?P<title>\s+\"[^\"]*\")?\)"
)
_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"(`+[^`]*`+)")


class BookError(Exception):
    """The book cannot be staged as declared."""


def staged_path(source: str) -> str:
    """Where a repository file lands in the staged ``docs/`` tree."""
    if source in _RENAMED:
        return _RENAMED[source]
    if source.startswith("docs/"):
        return source[len("docs/"):]
    raise BookError(f"{source}: only docs/ files and {sorted(_RENAMED)} can be staged")


def page_sources() -> List[str]:
    """Every Markdown page of the book, nav pages first, then the unlisted ones."""
    listed = [src for _, pages in book() for src, _ in pages]
    unlisted = []
    for d in UNLISTED_DIRS:
        for name in sorted(os.listdir(os.path.join(ROOT, d))):
            if name.endswith(".md"):
                unlisted.append(f"{d}/{name}")
    return listed + unlisted


def _resolve(source: str, target: str) -> str:
    """The repository-relative path a link ``target`` in ``source`` points at."""
    base = os.path.dirname(source)
    return os.path.normpath(os.path.join(base, target)).replace(os.sep, "/")


def _rewrite_page(source: str, text: str, pages: Dict[str, str], ref: str,
                  assets: Dict[str, str], errors: List[str]) -> str:
    """``text`` of ``source`` with every link valid from its staged location."""
    here = os.path.dirname(pages[source])

    def link(m: "re.Match[str]") -> str:
        target = m.group("target")
        if target.startswith(_EXTERNAL):
            return m.group(0)
        path, _, anchor = target.partition("#")
        if not path:
            fixed = _anchor_map(source).get(anchor, anchor)
            return m.group(0).replace(f"(#{anchor}", f"(#{fixed}", 1)
        repo_rel = _resolve(source, path)
        on_disk = os.path.join(ROOT, repo_rel)
        if repo_rel.startswith("../"):
            errors.append(f"{source}: link leaves the repository: {target}")
            return m.group(0)
        if any((repo_rel + "/").startswith(t) for t in _LOCAL_ONLY):
            return m.group("text")  # no public target: keep the words
        if not os.path.exists(on_disk):
            errors.append(f"{source}: broken link: {target}")
            return m.group(0)
        if repo_rel in pages:
            dest = pages[repo_rel]
            anchor = _anchor_map(repo_rel).get(anchor, anchor)
        elif repo_rel.startswith("docs/") and os.path.isfile(on_disk) and not repo_rel.endswith(".md"):
            # A figure or screenshot a book page shows: staged beside it.
            dest = assets.setdefault(repo_rel, staged_path(repo_rel))
        else:
            if m.group("bang"):
                errors.append(f"{source}: image outside docs/ cannot be staged: {target}")
                return m.group(0)
            kind = "tree" if os.path.isdir(on_disk) else "blob"
            url = f"{REPO_URL}/{kind}/{ref}/{repo_rel.rstrip('/')}"
            return f"[{m.group('text')}]({url}{'#' + anchor if anchor else ''}{m.group('title') or ''})"
        rel = os.path.relpath(dest, here or ".").replace(os.sep, "/")
        return (f"{m.group('bang')}[{m.group('text')}]"
                f"({rel}{'#' + anchor if anchor else ''}{m.group('title') or ''})")

    protected = _protected_spans(text)

    def outside(m: "re.Match[str]") -> str:
        # A link that *starts* inside code is an example of syntax, not a link.
        # One whose text holds a code span -- [`X.md`](X.md), the house style --
        # starts outside it and is rewritten.
        if any(a <= m.start() < b for a, b in protected):
            return m.group(0)
        return link(m)

    # Over the whole text, not line by line: a link's text may wrap.
    return _LINK.sub(outside, text)


def _protected_spans(text: str) -> List[Tuple[int, int]]:
    """Character ranges that are code: fenced blocks and inline code spans."""
    spans: List[Tuple[int, int]] = []
    pos, fence_start = 0, None
    for line in text.split("\n"):
        end = pos + len(line)
        if _FENCE.match(line):
            if fence_start is None:
                fence_start = pos
            else:
                spans.append((fence_start, end))
                fence_start = None
        elif fence_start is None:
            spans.extend((pos + m.start(), pos + m.end()) for m in _CODE_SPAN.finditer(line))
        pos = end + 1
    if fence_start is not None:
        spans.append((fence_start, len(text)))
    return spans


_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
_INLINE_MARKUP = re.compile(r"<[^>]+>|[`*_]|\[([^\]]*)\]\([^)]*\)")


def _anchor_map(source: str) -> Dict[str, str]:
    """``{GitHub heading anchor: the built site's anchor}`` where the two differ.

    The documents are written against GitHub's anchors, which keep a doubled
    hyphen where a heading drops a character (``a — b`` -> ``a--b``); the site
    generator collapses it. An explicit ``<a id=...>`` is the same on both.
    """
    out: Dict[str, str] = {}
    with open(os.path.join(ROOT, source), encoding="utf-8") as fh:
        text = fh.read()
    protected = _protected_spans(text)
    pos = 0
    for line in text.split("\n"):
        m = _HEADING.match(line)
        if m and not any(a <= pos < b for a, b in protected):
            plain = _INLINE_MARKUP.sub(lambda k: k.group(1) or "", m.group(1)).strip().lower()
            github = re.sub(r"[^\w\- ]", "", plain).replace(" ", "-")
            site = re.sub(r"[-\s]+", "-", re.sub(r"[^\w\s-]", "", plain)).strip("-")
            if github != site:
                out.setdefault(github, site)
        pos += len(line) + 1
    return out


def _yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def render_config(ref: str = DEFAULT_REF) -> str:
    """The generator's ``mkdocs.yml``: the nav is :func:`book`, stated once."""
    lines = [
        "# Generated by scripts/build_book.py -- DO NOT EDIT; edit the script.",
        f"site_name: {_yaml_str(SITE_NAME)}",
        f"site_description: {_yaml_str(SITE_DESCRIPTION)}",
        f"site_url: {_yaml_str(BOOK_URL)}",
        f"repo_url: {_yaml_str(REPO_URL)}",
        f"edit_uri: {_yaml_str(f'blob/{ref}/docs/')}",
        "docs_dir: docs",
        "site_dir: site",
        "strict: true",
        "theme:",
        "  name: material",
        "  features:",
        "    - navigation.sections",
        "    - navigation.top",
        "    - navigation.footer",
        "    - search.highlight",
        "    - content.code.copy",
        "  palette:",
        "    - media: \"(prefers-color-scheme: light)\"",
        "      scheme: default",
        "      toggle: {icon: material/weather-night, name: Dark mode}",
        "    - media: \"(prefers-color-scheme: dark)\"",
        "      scheme: slate",
        "      toggle: {icon: material/weather-sunny, name: Light mode}",
        "markdown_extensions:",
        "  - tables",
        "  - attr_list",
        "  - toc:",
        "      permalink: true",
        "  - pymdownx.highlight",
        "  - pymdownx.superfences",
        "nav:",
    ]
    for section, pages in book():
        lines.append(f"  - {_yaml_str(section)}:")
        for src, title in pages:
            dest = staged_path(src)
            lines.append(f"      - {_yaml_str(title)}: {_yaml_str(dest)}" if title
                         else f"      - {_yaml_str(dest)}")
    return "\n".join(lines) + "\n"


def stage(out: str = OUT, ref: str = DEFAULT_REF) -> List[str]:
    """Write the staged book under ``out``; return the problems found (empty = good).

    ``out`` is replaced whole, so a page dropped from :func:`book` cannot
    survive in a stale tree.
    """
    errors: List[str] = []
    sources = page_sources()
    missing = [s for s in sources if not os.path.isfile(os.path.join(ROOT, s))]
    if missing:
        return [f"book page does not exist: {s}" for s in missing]
    pages = {s: staged_path(s) for s in sources}
    clash = sorted({d for d in pages.values() if list(pages.values()).count(d) > 1})
    if clash:
        return [f"two book pages stage to the same path: {d}" for d in clash]

    if os.path.isdir(out):
        shutil.rmtree(out)
    docs_out = os.path.join(out, "docs")
    assets: Dict[str, str] = {}
    for src, dest in pages.items():
        with open(os.path.join(ROOT, src), encoding="utf-8") as fh:
            text = _rewrite_page(src, fh.read(), pages, ref, assets, errors)
        path = os.path.join(docs_out, dest)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    for src, dest in assets.items():
        path = os.path.join(docs_out, dest)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, src), path)
    with open(os.path.join(out, "mkdocs.yml"), "w", encoding="utf-8") as fh:
        fh.write(render_config(ref))
    return errors


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="stage into a temporary directory and report; write nothing here")
    ap.add_argument("--ref", default=DEFAULT_REF,
                    help=f"the git ref out-of-book links point at (default: {DEFAULT_REF})")
    ap.add_argument("-o", "--out", default=OUT, help="staging directory (default: build/book)")
    args = ap.parse_args(argv)

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            errors = stage(os.path.join(tmp, "book"), args.ref)
    else:
        errors = stage(args.out, args.ref)
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        return 1
    n = len(page_sources())
    print(f"book: {n} pages {'check out' if args.check else 'staged in ' + os.path.relpath(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
