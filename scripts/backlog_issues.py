#!/usr/bin/env python
"""The backlog ↔ GitHub Issues bridge (design note 28 MD-5; slimmed 2026-11-01, #359).

Issues are the system of record for open work; ``docs/30_future/00_backlog.md``
keeps the plan (mission, ordering rules, the priority table with bands). The
table is a **view of the issues**: a row is one line, ``| Pri | **title** (#N) |
what ships | tag | tier / effort | depends |``, and the body lives in the issue.

    check    every priority-table row names an open issue, every open issue
             labelled ``band:*`` appears in the table, and every row's issue sits
             on the milestone its **band header** names — never on one already
             cut in CHANGELOG.md (needs gh; exit 1 on drift)
    render   drop every row whose issue is CLOSED; nothing else moves. Run by
             ``scripts/solo_close.sh`` in preflight with ``--closing N`` (the
             issue it is about to close counts as closed), so the row leaves in
             the closing commit and nobody hand-edits the table. ``--dry-run``
             prints the rows it would drop and writes nothing.

Pure functions (``parse_backlog``, ``render_backlog``, ``band_milestones``,
``row_bands``) work on strings so ``tests/test_backlog_issues.py`` runs them on
the live file without ``gh``; only ``check`` and ``render`` shell out.
Owner-run; never from CI.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG = os.path.join(ROOT, "docs", "30_future", "00_backlog.md")

# Band identifiers are not all a single letter (B2, B10, B12): matching `[A-Z]`
# alone silently skipped those header rows, so every row beneath inherited the
# previous band -- and the band an issue is filed under is exactly what the
# milestone check compares.
BAND_ROW = re.compile(r"^\|\s*\*\*([A-Z]\d{0,2})\s+[—-]\s*(.*?)\*\*\s*\|")
ITEM_ROW = re.compile(r"^\|\s*(\d+)\s*\|")
ISSUE_REF = re.compile(r"\(#(\d+)\)")


@dataclass
class Item:
    kind: str                       # always "row"
    title: str
    labels: List[str] = field(default_factory=list)
    band: str = ""
    pri: Optional[int] = None
    line: int = 0                   # 1-based line in the backlog
    existing: Optional[int] = None  # the ``(#N)`` the row carries


def _plain(md: str) -> str:
    """A title with markdown stripped, one line, <= 120 chars."""
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    t = re.sub(r"[`*]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:117] + "…" if len(t) > 120 else t


def parse_backlog(text: str) -> List[Item]:
    """The priority-table rows, each with the labels its cells imply."""
    items: List[Item] = []
    band = ""
    for i, line in enumerate(text.splitlines()):
        m = BAND_ROW.match(line)
        if m:
            band = m.group(1)
            continue
        if not (ITEM_ROW.match(line) and band):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # | Pri | Item | What ships | Tag | Tier / effort | Depends on |
        if len(cells) < 6:
            continue
        pri, title, tag, tier = int(cells[0]), cells[1], cells[3], cells[4]
        tier_letter = tier.strip().split("/")[0].strip()[:1].upper() or "M"
        labels = [f"band:{band}", f"tier:{tier_letter}", f"tag:{tag.strip()[:1].upper()}"]
        labels.append("kind:defect" if "defect" in title.lower() else "kind:step")
        if "hygiene" in title.lower() or "CH-" in title:
            labels[-1] = "kind:hygiene"
        refs = ISSUE_REF.findall(title)
        items.append(Item("row", _plain(ISSUE_REF.sub("", title)), labels, band, pri,
                          line=i + 1, existing=int(refs[0]) if refs else None))
    return items


def row_ref(line: str) -> Optional[int]:
    """The issue a priority-table row *is*, or ``None``.

    Only the **Item** cell is read: other cells cite other issues in prose
    ("waits for the GUI review (#29)"), and a scan of the whole line reads that
    cross-reference as the row's own identity (found 2026-08-25, #46).
    """
    if not ITEM_ROW.match(line):
        return None
    cells = line.strip().strip("|").split("|")
    if len(cells) < 2:
        return None
    m = ISSUE_REF.search(cells[1])
    return int(m.group(1)) if m else None


def table_refs(text: str) -> List[int]:
    return [n for line in text.splitlines() if (n := row_ref(line)) is not None]


# --- render: the table as a view of the issues -------------------------------


def render_backlog(text: str, states: Dict[int, str]) -> str:
    """``text`` with every item row whose issue is CLOSED dropped.

    A row is owned by the ``(#N)`` in its Item cell; a later ``(#N)`` in the
    line is a cross-reference and never drops the row. An issue ``states`` does
    not know leaves its row alone. Nothing outside the item rows moves.
    """
    out: List[str] = []
    for line in text.splitlines():
        n = row_ref(line)
        if n is not None and states.get(n, "").upper() == "CLOSED":
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def fetch_states() -> Dict[int, str]:
    """``{number: state}`` for every issue, open or closed (needs gh)."""
    raw = json.loads(_gh("issue", "list", "--state", "all", "--limit", "1000",
                         "--json", "number,state"))
    return {int(it["number"]): it["state"] for it in raw}


# --- gh ----------------------------------------------------------------------


def _gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


#: The record corpus, out of the default search path (design note 61 CV-4).
CHANGELOG = os.path.join(ROOT, "docs", "90_record", "CHANGELOG.md")
#: `## [0.7.2] — 2026-08-25` — a released section. `[Unreleased]` is not one.
CUT_SECTION = re.compile(r"^##\s*\[(\d+\.\d+\.\d+)\]", re.M)
#: The release a band header names: `**B — 0.8.0: oracle-GUI development**`.
BAND_MILESTONE = re.compile(r"(\d+\.\d+\.\d+)")


def band_milestones(text: str) -> Dict[str, Optional[str]]:
    """{band: the release its header names}, ``None`` where it names none.

    Read from the header row rather than hardcoded: the letters move at every
    re-cut, and a hardcoded map is the drift this check exists to catch. A
    maintenance band ("when the module is next touched") names no release by
    design, so its issues carry no milestone.
    """
    out: Dict[str, Optional[str]] = {}
    for line in text.splitlines():
        m = BAND_ROW.match(line)
        if m:
            v = BAND_MILESTONE.search(m.group(2))
            out[m.group(1)] = v.group(1) if v else None
    return out


def row_bands(text: str) -> Dict[int, str]:
    """{issue number: the band whose header it sits under}."""
    out: Dict[int, str] = {}
    band = ""
    for line in text.splitlines():
        m = BAND_ROW.match(line)
        if m:
            band = m.group(1)
            continue
        if band:
            n = row_ref(line)
            if n is not None:
                out[n] = band
    return out


def cut_milestones() -> set:
    """Releases that already have a section in ``CHANGELOG.md`` — i.e. are cut.

    GitHub milestone *state* is not usable for this: cut milestones stay open
    on GitHub.
    """
    with open(CHANGELOG, encoding="utf-8") as fh:
        return set(CUT_SECTION.findall(fh.read()))


def check(text: str) -> Tuple[List[int], List[Tuple[int, str]], List[str]]:
    """(table refs with no open issue, open band:* issues not in the table,
    band-vs-milestone faults).

    Two faults are reported in the third list (issue #46): an issue whose
    milestone is not the one its band names, and an issue parked on a
    milestone `CHANGELOG.md` shows as already cut, which can never ship.
    """
    refs = set(table_refs(text))
    raw = _gh("issue", "list", "--state", "open", "--limit", "1000",
              "--json", "number,title,labels,milestone")
    open_issues = json.loads(raw)
    open_nums = {it["number"] for it in open_issues}
    banded = [(it["number"], it["title"]) for it in open_issues
              if any(lb["name"].startswith("band:") for lb in it["labels"])]

    wanted = band_milestones(text)
    bands = row_bands(text)
    cut = cut_milestones()
    faults: List[str] = []
    for it in open_issues:
        n = it["number"]
        if n not in bands:
            continue
        band = bands[n]
        have = (it.get("milestone") or {}).get("title")
        want = wanted.get(band)
        if have != want:
            faults.append(
                f"#{n} is a band-{band} row (names {want or 'no milestone'}) "
                f"but its milestone is {have or 'unset'}: {it['title'][:60]}"
            )
        elif have in cut:
            faults.append(
                f"#{n} is open on milestone {have}, which CHANGELOG.md shows as already "
                f"cut — it can never ship there: {it['title'][:60]}"
            )
    return sorted(refs - open_nums), [(n, t) for n, t in banded if n not in refs], faults


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["check", "render"])
    ap.add_argument("--closing", type=int, metavar="N",
                    help="render: treat issue N as CLOSED (solo_close.sh preflight, before gh closes it)")
    ap.add_argument("--dry-run", action="store_true",
                    help="render: print the rows that would be dropped; write nothing")
    args = ap.parse_args(argv)
    with open(BACKLOG, encoding="utf-8") as fh:
        text = fh.read()

    if args.command == "render":
        states = fetch_states()
        if args.closing is not None:
            states[args.closing] = "CLOSED"
        rendered = render_backlog(text, states)
        if rendered == text:
            print("priority table already matches the issues")
            return 0
        dropped = [ln for ln in text.splitlines() if ln not in rendered.splitlines()]
        for ln in dropped:
            print(f"drop: {ln[:100]}")
        if args.dry_run:
            print(f"[{len(dropped)} row(s) would leave; nothing written]")
            return 0
        with open(BACKLOG, "w", encoding="utf-8") as fh:
            fh.write(rendered)
        print(f"rendered {os.path.relpath(BACKLOG, ROOT)} from the issues: {len(dropped)} row(s) left")
        return 0

    dangling, missing, faults = check(text)
    for n in dangling:
        print(f"table row references #{n} but no such open issue")
    for n, t in missing:
        print(f"open band:* issue #{n} is not in the priority table: {t}")
    for f in faults:
        print(f"band/milestone: {f}")
    return 1 if (dangling or missing or faults) else 0


if __name__ == "__main__":
    sys.exit(main())
