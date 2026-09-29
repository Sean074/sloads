#!/usr/bin/env python3
"""The verdict on a milestone branch's CI, for the commit that was pushed (#329).

**Why this exists.** ``solo_close.sh`` pushes each item onto the milestone
branch and ``ci.yml`` runs the fast gate there, but until #329 nothing read the
result before the next close: the 0.8.7 milestone was red on ``dev/v0.8.7``
from #286 to the release cut (#324, a Linux-vs-macOS byte every local gate
passed), and the first anyone saw of it was the cut's pull request. #327 made
the developer's interpreter CI's; this closes the rest of the gap by reading
CI before the gate.

**Which run.** ``ci.yml`` cancels a branch's in-progress run when a newer push
arrives, so "the newest run" can be a run of a commit that was superseded. The
run judged is the one whose ``headSha`` is the pushed tip of the branch
(``origin/<branch>``); none listed yet is its own answer.

**The verdict** (owner ruling 1a, 2026-09-28):

* ``success`` -- green, exit 0;
* ``failure``, ``timed_out``, ``startup_failure`` -- red, exit 1: the close
  refuses unless ``--ci-red-ok "<reason>"`` says why this change goes in anyway
  (typically: it is the fix);
* anything else -- still running, queued, no run for the tip yet, ``cancelled``
  (the tip's own run can only be cancelled by hand), or input that is not the
  JSON expected -- warns, exit 2, and the close carries on.

Usage (what ``solo_close.sh`` runs; ``gh`` is the caller's, so the verdict is
testable from JSON alone)::

    gh run list --branch <b> --workflow ci.yml --limit 20 \\
        --json status,conclusion,headSha,url | scripts/ci_state.py --tip <sha>
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, List, Tuple

#: The conclusions that refuse a close. Everything else that is not
#: ``success`` warns (ruling 1a).
RED = frozenset({"failure", "timed_out", "startup_failure"})

GREEN, RED_EXIT, WARN = 0, 1, 2


def verdict(runs: List[Any], tip: str) -> Tuple[int, str]:
    """``(exit code, one-line message)`` for the run of ``tip`` among ``runs``."""
    short = tip[:7]
    run = next((r for r in runs if isinstance(r, dict) and r.get("headSha") == tip), None)
    if run is None:
        return WARN, f"no CI run listed for the pushed tip {short} yet -- check it with: gh run watch"
    url = run.get("url", "")
    status = run.get("status", "")
    if status != "completed":
        return WARN, f"CI is {status or 'not started'} on {short} -- not waited for: {url}"
    conclusion = run.get("conclusion", "")
    if conclusion == "success":
        return GREEN, f"CI green on {short}: {url}"
    if conclusion in RED:
        return RED_EXIT, f"CI is red on {short} ({conclusion}): {url}"
    return WARN, f"CI ended {conclusion or 'without a conclusion'} on {short}: {url}"


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--tip", required=True, help="the pushed commit (origin/<branch>)")
    args = parser.parse_args(argv)
    try:
        runs = json.loads(sys.stdin.read() or "null")
    except json.JSONDecodeError:
        runs = None
    if not isinstance(runs, list):
        print("CI unread -- gh returned no run list; check it yourself")
        return WARN
    code, message = verdict(runs, args.tip)
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
