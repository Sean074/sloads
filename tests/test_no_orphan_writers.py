"""A ``write_*`` deliverable wrapper in ``sloads/`` cannot lose its last caller
in silence.

**The defect class (#16 / CH-5).** The 2026-08-16 scope review found four public
names that were never called anywhere -- definition plus ``__all__`` and nothing
else -- and three of the four were the same shape: a two-line
``write_X(project, path, ...)`` wrapper around an ``X(project, ...)`` builder,
left behind when the caller that wrote the file went away. Nothing noticed,
because a wrapper with no caller still imports, still type-checks and still
lints clean; only a whole-tree grep finds it, and nobody greps on a schedule.

By the time the row was worked (2026-09-11) a **fifth** had appeared the same
way -- ``report.tables.write_safety_factors_csv``, orphaned when note 56 D-56.1
moved the report tables out of the export bridge. That is the rule-4 test: the
class recurred, so the sweep gets a gate rather than a second manual pass.

**What this asserts, and what it deliberately does not.** Only ``write_*``
functions, because the pattern is specific: they exist to put a deliverable on
disk, so a caller is the whole point of one and its absence means the deliverable
is no longer produced. A no-consumer dataclass or constant is *not* in scope --
``sloads/`` has ~200 public names with no consumer outside their own module, and
the great majority are module result types and single-source constant families
(the ``MASS_EID_*`` id bands, ``WING_BAND_*``, the encoded-but-dormant commuter
tier) that are public on purpose. Sweeping those is the judgment call #16 left
open; this gate takes only the part that is mechanical.
"""

from __future__ import annotations

import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CALC = os.path.join(_ROOT, "sloads")
#: Every tree that may hold a caller: the calc package, both shells, the CLI
#: entry points, the scripts and the suite itself.
_SEARCHED = ["sloads", "app", "app_shell", "oracle_app", "scripts", "tests",
             "cli.py", "oracle.py"]

_DEF = re.compile(r"^def (write_[a-z0-9_]+)\(", re.M)


def _py_files(*roots: str):
    for r in roots:
        p = os.path.join(_ROOT, r)
        if os.path.isfile(p):
            yield p
            continue
        for dirpath, _, names in os.walk(p):
            if "__pycache__" in dirpath:
                continue
            for n in names:
                if n.endswith(".py"):
                    yield os.path.join(dirpath, n)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_every_write_wrapper_in_sloads_has_a_caller() -> None:
    """No ``sloads/`` deliverable writer is left without a consumer.

    A reference inside the defining module counts -- a writer called by its own
    package's builder is consumed -- but the definition line and the module's
    ``__all__`` entry do not, since those are exactly what a dead symbol keeps.
    """
    sources = {f: _read(f) for f in _py_files(*_SEARCHED)}
    orphans = []
    for path, text in sorted(sources.items()):
        if not path.startswith(_CALC + os.sep):
            continue
        for name in _DEF.findall(text):
            pattern = re.compile(r"\b%s\b" % re.escape(name))
            hits = 0
            for other, body in sources.items():
                for i, line in enumerate(body.splitlines()):
                    if not pattern.search(line):
                        continue
                    same_file = other == path
                    if same_file and line.startswith("def %s(" % name):
                        continue          # the definition itself
                    if line.strip() in ('"%s",' % name, "'%s'," % name):
                        continue          # an __all__ entry
                    hits += 1
            if not hits:
                orphans.append("%s:%s" % (os.path.relpath(path, _ROOT), name))
    assert not orphans, (
        "these sloads/ deliverable writers have no caller anywhere -- either a "
        "consumer was removed without them (the #16 / CH-5 class: four found in "
        "2026-08-16, a fifth by 2026-09-11) or the deliverable is genuinely "
        "retired and the writer should go with it:\n  " + "\n  ".join(orphans)
    )


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
