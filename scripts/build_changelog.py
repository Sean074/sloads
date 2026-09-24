#!/usr/bin/env python
"""Assemble ``changes/*.md`` fragments into ``CHANGELOG.md`` and the history file.

Design notes 26 (changelog fragments, 2026-08-16) and 28 MD-4 (history
fragments, 2026-08-16). Fragment contract: ``changes/README.md``. Run at
release cut only (``RELEASE_PROCESS.md`` §4); ``--dry-run`` previews without
writing.

Two destinations, one mechanism: ``<slug>.<breaking|added|changed|fixed|removed>.md``
becomes a bullet in the release's ``CHANGELOG.md`` section; ``<slug>.history.md``
(tier M paragraph or tier L step) is inserted, newest first, at the top of
``docs/90_record/00_completed_development.md``.

Design note 61 CV-2: a tier-M/L closure writes **one** fragment. A
``<slug>.history[-<type>].md`` with no companion ``<slug>.<type>.md`` also
*derives* its changelog bullet, from the bold lead phrase the history entry
already opens with (``derive_bullet``) — the same prose written once instead of
twice, with the changelog becoming a generated index of the record. ``-<type>``
names the subsection; plain ``.history.md`` derives into ``Changed``.

Pure functions (``parse_fragments``, ``derive_bullet``, ``merge_section``,
``cut_release``, ``roll_history``, ``roll_changelog``) do all the work on
strings so ``tests/test_changelog_fragments.py`` can exercise them without
touching the repo files; ``main`` is the only I/O.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGES_DIR = os.path.join(ROOT, "changes")
#: The record corpus (design note 61 CV-4): out of the default search path.
RECORD_DIR = os.path.join(ROOT, "docs", "90_record")
CHANGELOG = os.path.join(RECORD_DIR, "CHANGELOG.md")
HISTORY = os.path.join(RECORD_DIR, "00_completed_development.md")

#: Subsection order in a release block. ``type`` in the fragment name maps to
#: the heading; anything else is a naming error, not a new subsection.
TYPES: Tuple[Tuple[str, str], ...] = (
    ("breaking", "Breaking"),
    ("added", "Added"),
    ("changed", "Changed"),
    ("fixed", "Fixed"),
    ("removed", "Removed"),
)
TYPE_TO_HEADING = dict(TYPES)
#: The history destination (design note 28 MD-4): not a changelog subsection.
HISTORY_TYPE = "history"
#: Subsection a plain ``.history.md`` derives its bullet into (note 61 CV-2).
DEFAULT_DERIVED_TYPE = "changed"
FRAGMENT_NAME = re.compile(
    r"^(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.(?P<type>history-[a-z]+|[a-z]+)\.md$")
UNRELEASED = re.compile(r"^## \[Unreleased\]\s*$", re.M)
RELEASE_HEADING = re.compile(r"^## \[", re.M)
SUBSECTION = re.compile(r"^### (\w+)\s*$", re.M)


class FragmentError(ValueError):
    """A fragment that violates ``changes/README.md``; the file name is in the message."""


def split_history_type(kind: str) -> Optional[str]:
    """``history`` / ``history-<type>`` → the subsection its bullet derives into.

    ``None`` for a kind that is not a history fragment (note 61 CV-2).
    """
    if kind == HISTORY_TYPE:
        return DEFAULT_DERIVED_TYPE
    if kind.startswith(HISTORY_TYPE + "-"):
        return kind[len(HISTORY_TYPE) + 1 :]
    return None


def validate_fragment(name: str, body: str) -> str:
    """Return the fragment's type, or raise :class:`FragmentError` naming the fault."""
    m = FRAGMENT_NAME.match(name)
    if not m:
        raise FragmentError(f"{name}: not '<slug>.<type>.md' (kebab-case slug, lower-case type)")
    kind = m.group("type")
    derived = split_history_type(kind)
    if derived is not None:
        if derived not in TYPE_TO_HEADING:
            raise FragmentError(
                f"{name}: derived type '{derived}' not in {sorted(TYPE_TO_HEADING)}")
        if not body.strip():
            raise FragmentError(f"{name}: history fragment is empty")
        # A tier-M paragraph is a bullet: the history file lists them as
        # bullets, and six 0.8.6 fragments opened with a bare '**' and would
        # have rolled in un-bulleted (#299). The bare form survives only for
        # the tier-L step heading the README also allows ('**Step N — …**').
        if not body.lstrip().startswith(("- **", "**Step", "## ")):
            raise FragmentError(
                f"{name}: history fragment must be a tier-M bullet ('- **') "
                "or a tier-L step ('## Step' / '**Step')")
        derive_bullet(name, body)  # a fragment with no derivable lead is a fault now, not at cut
        return kind
    if kind not in TYPE_TO_HEADING:
        raise FragmentError(f"{name}: type '{kind}' not in {sorted(TYPE_TO_HEADING) + [HISTORY_TYPE]}")
    if not body.lstrip().startswith("- "):
        raise FragmentError(f"{name}: body must be Markdown bullet(s) starting with '- '")
    return kind


#: A tier-M entry opens ``- **Title (#123, tier M, date)** — …``; a tier-L step
#: opens ``## Step N — …``. Either way the lead phrase *is* the changelog bullet.
LEAD_BOLD = re.compile(r"\*\*(?P<lead>.+?)\*\*", re.S)
LEAD_STEP = re.compile(r"^##\s+(?P<lead>.+?)\s*$", re.M)


def derive_bullet(name: str, body: str) -> str:
    """The ``CHANGELOG.md`` bullet a history fragment implies (note 61 CV-2).

    The lead phrase the entry already opens with, verbatim, as a one-line
    bullet — no second telling, and nothing a human has to keep in step.
    """
    text = body.lstrip()
    m = LEAD_STEP.match(text) if text.startswith("## ") else LEAD_BOLD.search(text)
    if not m:
        raise FragmentError(
            f"{name}: no lead phrase to derive a changelog bullet from "
            "(open with '- **Title (…)**' or '## Step N — …')")
    lead = " ".join(m.group("lead").split())
    return f"- **{lead}**\n"


def fragment_slug(name: str) -> str:
    """The ``<slug>`` of a validated fragment file name."""
    m = FRAGMENT_NAME.match(name)
    if not m:  # pragma: no cover - validate_fragment has already refused it
        raise FragmentError(f"{name}: not '<slug>.<type>.md'")
    return m.group("slug")


def parse_fragments(files: Dict[str, str]) -> Dict[str, List[str]]:
    """``{filename: body}`` → ``{type: [blocks…]}`` in filename order.

    Changelog types map to their subsection; :data:`HISTORY_TYPE` collects the
    history entries under their own key. A history fragment whose slug has no
    hand-written changelog fragment also contributes a *derived* bullet to its
    subsection (note 61 CV-2), so a tier-M/L closure writes one file, not two.
    """
    kinds = {name: validate_fragment(name, files[name]) for name in sorted(files)}
    hand_written = {
        fragment_slug(name) for name, kind in kinds.items() if split_history_type(kind) is None
    }
    out: Dict[str, List[str]] = {}
    for name, kind in kinds.items():
        body = files[name].strip("\n") + "\n"
        derived = split_history_type(kind)
        if derived is None:
            out.setdefault(kind, []).append(body)
            continue
        out.setdefault(HISTORY_TYPE, []).append(body)
        if fragment_slug(name) not in hand_written:
            out.setdefault(derived, []).append(derive_bullet(name, body))
    return out


HISTORY_RULE = re.compile(r"^---[ \t]*$", re.M)


def roll_history(history: str, entries: List[str]) -> str:
    """Insert ``entries`` (newest first is the file's order; the entries keep
    their filename order) directly after the header's first ``---`` rule.

    Everything below that point -- the live cycle -- is byte-identical.
    """
    if not entries:
        return history
    m = HISTORY_RULE.search(history)
    if not m:
        raise ValueError("history file has no '---' rule after its header")
    block = "\n".join(e.rstrip("\n") + "\n" for e in entries)
    return history[: m.end()] + "\n\n" + block + "\n" + history[m.end():].lstrip("\n")


#: Live-file line budget shared by the history (note 26 DV-6) and, from note 61
#: CV-5, the changelog: crossing it triggers a roll, it is not a defect.
LIVE_LINE_THRESHOLD = 1500


def roll_changelog(changelog: str, keep: int = 2) -> Tuple[str, str]:
    """Split ``CHANGELOG.md`` into (live, archived) at a release boundary.

    The live file keeps its header, ``[Unreleased]`` and the newest ``keep``
    release blocks; everything older is returned verbatim for a frozen
    ``90_record/NN_changelog_to_<version>.md`` (note 61 CV-5, the rule note 26
    DV-1 gave the history and not the changelog). Byte-preserving: the two
    parts concatenate back to the input.
    """
    if keep < 1:
        raise ValueError("keep must be at least 1 release block")
    starts = [m.start() for m in RELEASE_HEADING.finditer(changelog)]
    # starts[0] is '[Unreleased]'; release blocks proper begin at starts[1].
    if len(starts) <= keep + 1:
        return changelog, ""
    cut = starts[keep + 1]
    return changelog[:cut].rstrip("\n") + "\n", changelog[cut:]


#: ``## [0.8.3] — 2026-09-13`` → the version. Names the archive after the newest
#: release it contains, as ``11_completed_development_to_0.5.0.md`` already is.
RELEASE_VERSION = re.compile(r"^## \[(?P<version>[^\]]+)\]", re.M)


def archive_name(archived: str) -> str:
    """File name for a rolled-off changelog block (note 61 CV-5)."""
    m = RELEASE_VERSION.search(archived)
    if not m:
        raise ValueError("rolled block has no release heading to name the archive after")
    return f"CHANGELOG_to_{m.group('version')}.md"


def archive_header(archived: str) -> str:
    """The do-not-edit header a frozen changelog archive opens with."""
    m = RELEASE_VERSION.search(archived)
    version = m.group("version") if m else "?"
    return (
        f"# Changelog archive — releases up to and including {version}\n\n"
        "**Frozen record — do not edit.** Rolled off `CHANGELOG.md` at a release\n"
        "cut per design note 61 CV-5 (the rule design note 26 DV-1 gave the history\n"
        "file). Verbatim; the live changelog holds the current cycle and the\n"
        "previous release block.\n\n---\n\n"
    )


def _split_subsections(body: str) -> Tuple[str, Dict[str, str]]:
    """Split an ``[Unreleased]`` body into (preamble, {heading: text})."""
    parts = SUBSECTION.split(body)
    preamble = parts[0]
    sections: Dict[str, str] = {}
    for i in range(1, len(parts), 2):
        sections[parts[i]] = parts[i + 1]
    return preamble, sections


def merge_section(unreleased_body: str, fragments: Dict[str, List[str]]) -> str:
    """Merge fragment bullets into an ``[Unreleased]`` body, subsection by subsection.

    Fragments lead each subsection, legacy hand-written text follows; empty
    subsections are dropped; subsection order is :data:`TYPES`, then any
    unknown legacy headings in their original order.
    """
    preamble, legacy = _split_subsections(unreleased_body)
    known = [h for _, h in TYPES]
    order = known + [h for h in legacy if h not in known]
    out = [preamble.rstrip("\n") + "\n" if preamble.strip() else ""]
    for heading in order:
        kind = next((k for k, h in TYPES if h == heading), None)
        new = "\n".join(fragments.get(kind, [])) if kind else ""
        old = legacy.get(heading, "").strip("\n")
        if not new.strip() and not old.strip():
            continue
        block = f"### {heading}\n\n"
        if new.strip():
            block += new.rstrip("\n") + "\n\n"
        if old.strip():
            block += old + "\n\n"
        out.append(block)
    return "".join(out).rstrip("\n") + "\n"


def cut_release(changelog: str, fragments: Dict[str, List[str]], version: str, date: str) -> str:
    """Return the new ``CHANGELOG.md`` text with ``[Unreleased]`` cut as ``version``.

    Only the ``[Unreleased]`` block changes; every released section below it
    is byte-identical.
    """
    m = UNRELEASED.search(changelog)
    if not m:
        raise ValueError("CHANGELOG.md has no '## [Unreleased]' heading")
    start = m.end()
    nxt = RELEASE_HEADING.search(changelog, start)
    end = nxt.start() if nxt else len(changelog)
    body = merge_section(changelog[start:end], fragments)
    new_block = f"## [Unreleased]\n\n## [{version}] — {date}\n\n{body}\n"
    return changelog[: m.start()] + new_block + changelog[end:]


def preview(changelog: str, fragments: Dict[str, List[str]]) -> str:
    """The merged ``[Unreleased]`` body as it would be cut — for ``--dry-run``."""
    m = UNRELEASED.search(changelog)
    if not m:
        raise ValueError("CHANGELOG.md has no '## [Unreleased]' heading")
    nxt = RELEASE_HEADING.search(changelog, m.end())
    end = nxt.start() if nxt else len(changelog)
    return merge_section(changelog[m.end() : end], fragments)


def load_fragments(changes_dir: str = CHANGES_DIR) -> Dict[str, str]:
    files: Dict[str, str] = {}
    for name in os.listdir(changes_dir):
        if name == "README.md" or name.startswith("."):
            continue
        with open(os.path.join(changes_dir, name), encoding="utf-8") as fh:
            files[name] = fh.read()
    return files


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("version", nargs="?", help="X.Y.Z (required unless --dry-run)")
    ap.add_argument("--date", help="YYYY-MM-DD release date (required unless --dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="print the merged section; write nothing")
    ap.add_argument("--roll", action="store_true",
                    help="after the cut, roll release blocks older than the previous one into a frozen "
                         "90_record/ archive (note 61 CV-5)")
    ap.add_argument("--keep", type=int, default=2, metavar="N",
                    help="release blocks the live changelog keeps when --roll is given (default 2)")
    args = ap.parse_args(argv)

    files = load_fragments()
    fragments = parse_fragments(files)
    with open(CHANGELOG, encoding="utf-8") as fh:
        changelog = fh.read()

    history_entries = fragments.pop(HISTORY_TYPE, [])
    with open(HISTORY, encoding="utf-8") as fh:
        history = fh.read()

    if args.dry_run:
        sys.stdout.write(preview(changelog, fragments))
        if history_entries:
            sys.stdout.write("\n---- history entries (rolled to the top of the history file) ----\n\n")
            sys.stdout.write("\n".join(history_entries))
        sys.stdout.write(f"\n[{len(files)} fragment(s): {len(files) - len(history_entries)} changelog, "
                         f"{len(history_entries)} history; nothing written]\n")
        return 0
    if not args.version or not args.date:
        ap.error("version and --date are required unless --dry-run")
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        ap.error("version must be X.Y.Z")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        ap.error("--date must be YYYY-MM-DD")

    cut = cut_release(changelog, fragments, args.version, args.date)
    rolled = ""
    if args.roll:
        cut, archived = roll_changelog(cut, keep=args.keep)
        if archived:
            rolled = os.path.join(RECORD_DIR, archive_name(archived))
            with open(rolled, "w", encoding="utf-8") as fh:
                fh.write(archive_header(archived) + archived)
    with open(CHANGELOG, "w", encoding="utf-8") as fh:
        fh.write(cut)
    if history_entries:
        with open(HISTORY, "w", encoding="utf-8") as fh:
            fh.write(roll_history(history, history_entries))
    for name in files:
        os.remove(os.path.join(CHANGES_DIR, name))
    print(f"CHANGELOG.md: cut [{args.version}] — {args.date}; {len(files) - len(history_entries)} changelog "
          f"fragment(s) consumed; {len(history_entries)} history entr(y/ies) rolled into the history file")
    if rolled:
        print(f"changelog rolled: older release blocks frozen into {os.path.relpath(rolled, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
