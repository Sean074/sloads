#!/usr/bin/env python
"""Generate ``docs/00_INDEX.md`` from the docs tree (2026-11-01, #359).

One row per file, its title read from the file's own H1, so the index can
never say something about a document that the document does not say about
itself. The section order, headings, intro paragraphs and the root-docs
footer are the only prose, and they live here.

    python scripts/build_index.py            # print the index
    python scripts/build_index.py --write    # rewrite docs/00_INDEX.md
    python scripts/build_index.py --check    # exit 1 when the committed file differs

``tests/test_doc_currency.py`` asserts the committed file equals ``render()``.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
INDEX = os.path.join(DOCS, "00_INDEX.md")

#: (directory, heading, intro paragraph or None, newest-first). An unknown
#: directory under docs/ is an error: a new section is a decision, not a glob.
SECTIONS: Tuple[Tuple[str, str, Optional[str], bool], ...] = (
    ("10_standard", "10_standard — Code standard", None, False),
    ("20_theory", "20_theory — Theory & equation sources (the theory manual)",
     "The hub plus the chaptered theory manual: each `chNN_` chapter follows one\n"
     "template (scope, cases analyzed, method, **assumptions & limitations**, worked\n"
     "example, validation, sources); stub chapters ship the template with\n"
     "assumptions and validation populated first.", False),
    ("25_notes", "25_notes — Design notes",
     "Every design note and plan, whatever its status. A note that has shipped is\n"
     "still the authority for what it decided, so it is filed by what it *is* and not\n"
     "by whether its work is done (design note 61 CV-3). The note's own **Status**\n"
     "line is the single owner of that question; a row here never repeats it (#187).", False),
    ("30_future", "30_future — Future development", None, False),
    ("90_record", "90_record — The record (out of the default search path)", None, False),
    ("50_reviews", "50_reviews — Process reviews", None, True),
    ("60_guide", "60_guide — Oracle GUI user guide",
     "Structure per design note 34 ([`25_notes/34_oracle_user_guide_note.md`](25_notes/34_oracle_user_guide_note.md), "
     "decisions UG-1…UG-12): chapters follow `sloads.workflow.oracle_steps()` order; per-page field tables and the "
     "chapter list live under `60_guide/_generated/` (written by `docs/generate_data_dict.py`, never hand-edited); "
     "screenshots in `60_guide/img/` come from `scripts/capture_guide_shots.py`. Gates G-UG-1…G-UG-6: "
     "`tests/test_guide.py`.", False),
)

#: The section table: (directory, type, contents). Rendered as the preamble's table.
_SECTION_TABLE: Tuple[Tuple[str, str, str], ...] = (
    ("10_standard/", "**Code standard**",
     "The authoritative description of how the suite works *today* — architecture, the per-module spec, "
     "the conventions charter, and the process guides. Update these whenever code changes."),
    ("20_theory/", "**Theory & equation sources**",
     "Where each module's equations and regression oracles come from (the `reference/` PDFs), plus "
     "per-module page citations as modules are ported."),
    ("25_notes/", "**Design notes**",
     "Every design note and plan, **whatever its status** — the agreed rationale behind the physics, the "
     "conventions and the process, and the standing citation target for the tests that assert them. Filed "
     "by function, not by date (design note 61 CV-3): a note that has shipped is still the authority for "
     "what it decided."),
    ("30_future/", "**Future development**",
     "The mission-tagged backlog, the parked-items file, and the plan-of-record documents. Design notes "
     "live in `25_notes/` from the day they are written."),
    ("90_record/", "**The record** (out of the default search path)",
     "What happened and when: the frozen completed-development archives, the changelog and its archives, "
     "the per-release verification baselines. Consulted when the question is explicitly *when* or *why did "
     "this change*; it is not where current truth lives (design note 61 CV-4)."),
    ("50_reviews/", "**Process reviews**",
     "Periodic development-process assessments and the recommendations driving process changes."),
    ("60_guide/", "**Oracle GUI user guide**",
     "Page-by-page illustrated guide to the oracle GUI (design note 34): front matter, one "
     "generated-and-authored chapter per oracle page in workflow order, worked-example appendices. Field "
     "tables and the chapter list are generated (`docs/generate_data_dict.py`); screenshots by "
     "`scripts/capture_guide_shots.py`."),
)

PREAMBLE = (
    "# sloads Documentation — Index\n\n"
    "This directory is organised into seven numbered sections by **document type**.\n"
    "Lower numbers are the day-to-day references; higher numbers are planning, and\n"
    "`90_record/` is the record — what happened and when, deliberately out of the\n"
    "way of a search for what is true now (design note 61). **This file is\n"
    "generated** by `scripts/build_index.py` from each document's own title; edit\n"
    "the document, then regenerate.\n\n"
    "| Section | Type | Contents |\n|---------|------|----------|\n"
    + "".join(f"| `{d}` | {t} | {c} |\n" for d, t, c in _SECTION_TABLE)
    + "\n---\n"
)

FOOTER = """---

> Root-level docs live outside `docs/`: [`../README.md`](../README.md) (user
> front page), [`../CONTRIBUTING.md`](../CONTRIBUTING.md) (the human on-ramp),
> [`90_record/CHANGELOG.md`](90_record/CHANGELOG.md) (release notes — `[Unreleased]`
> is generated from [`../changes/`](../changes/README.md) fragments at release cut), and
> [`../CLAUDE.md`](../CLAUDE.md) (guidance for Claude Code). The authoritative
> theory/oracle PDFs live in [`../reference/`](../reference/), alongside the
> **CFR/AC text extracts** cited by the calc and the F25 gap analysis —
> `14CFR_factor_of_safety.md`, `14CFR_operating_limitations.md`,
> `14CFR_MC_MD_speed_margin.md`, `14CFR_Part25_engine_torque.md`,
> `AC_23-19A_engine_torque.md`, `23_427_unsymmetrical_candidate_set.md`, and
> `fuselage_pitching_moment.md`.
"""

INDEXED_EXT = (".md", ".txt", ".docx")
_H1 = re.compile(r"^\s*#\s+(.+?)\s*$")


def title_of(path: str) -> str:
    """A file's own title: its first H1 (``.md``), first non-blank line (``.txt``),
    or its file name (anything else)."""
    name = os.path.basename(path)
    stem, ext = os.path.splitext(name)
    if ext == ".md":
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = _H1.match(line)
                if m:
                    return m.group(1).replace("|", "\\|")
        return stem
    if ext == ".txt":
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    return line.strip().lstrip("#").strip().replace("|", "\\|")
        return stem
    return stem


def _files(directory: str, newest_first: bool) -> List[str]:
    out = sorted(
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.endswith(INDEXED_EXT) and not f.startswith(".")
    )
    return out[::-1] if newest_first else out


def render(docs: str = DOCS) -> str:
    """The whole index as text."""
    known = {d for d, _, _, _ in SECTIONS}
    present = {d for d in os.listdir(docs) if os.path.isdir(os.path.join(docs, d)) and not d.startswith("__")}
    unknown = sorted(present - known)
    if unknown:
        raise SystemExit(f"docs/ directories with no section in build_index.SECTIONS: {unknown}")
    out = [PREAMBLE]
    for d, heading, intro, newest_first in SECTIONS:
        out.append(f"\n## {heading}\n\n")
        if intro:
            out.append(intro + "\n\n")
        out.append("| File | Title |\n|------|-------|\n")
        for f in _files(os.path.join(docs, d), newest_first):
            out.append(f"| [`{f}`]({d}/{f}) | {title_of(os.path.join(docs, d, f))} |\n")
    out.append("\n" + FOOTER)
    return "".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="rewrite docs/00_INDEX.md")
    ap.add_argument("--check", action="store_true", help="exit 1 when the committed index differs")
    args = ap.parse_args(argv)
    text = render()
    if args.check:
        with open(INDEX, encoding="utf-8") as fh:
            if fh.read() == text:
                print("docs/00_INDEX.md is current")
                return 0
        print("docs/00_INDEX.md differs from the generator: run scripts/build_index.py --write", file=sys.stderr)
        return 1
    if args.write:
        with open(INDEX, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {os.path.relpath(INDEX, ROOT)}")
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
