#!/usr/bin/env python3
"""Print one release's section of ``docs/90_record/CHANGELOG.md`` -- the body
the GitHub release carries (RELEASE_PROCESS.md §4 step 4; #396).

    .venv/bin/python scripts/release_notes.py 0.9.0          # the block under ``## [0.9.0]``
    .venv/bin/python scripts/release_notes.py v0.9.0         # a tag spelling is accepted

The block runs from the ``## [X.Y.Z] -- date`` heading (excluded) to the next
``## [`` heading or the end of the file, trimmed. A version the changelog does
not carry exits 1 with the versions it does, so the release workflow fails
before it creates an empty release.
"""
from __future__ import annotations

import os
import re
import sys
from typing import List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(ROOT, "docs", "90_record", "CHANGELOG.md")

HEADING = re.compile(r"^## \[(?P<version>[^\]]+)\][^\n]*$", re.M)


def release_notes(changelog: str, version: str) -> Optional[str]:
    """The text under ``## [version]`` up to the next release heading, or
    ``None`` when the changelog has no such heading."""
    heads = list(HEADING.finditer(changelog))
    for i, m in enumerate(heads):
        if m.group("version") == version:
            end = heads[i + 1].start() if i + 1 < len(heads) else len(changelog)
            return changelog[m.end():end].strip() + "\n"
    return None


def versions(changelog: str) -> List[str]:
    return [m.group("version") for m in HEADING.finditer(changelog)]


def main(argv: Optional[List[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: release_notes.py X.Y.Z | vX.Y.Z", file=sys.stderr)
        return 2
    version = args[0][1:] if args[0].startswith("v") else args[0]
    with open(CHANGELOG, encoding="utf-8") as fh:
        text = fh.read()
    notes = release_notes(text, version)
    if notes is None:
        print(f"release_notes: no '## [{version}]' heading in {os.path.relpath(CHANGELOG, ROOT)}; "
              f"it has: {', '.join(versions(text))}", file=sys.stderr)
        return 1
    sys.stdout.write(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
