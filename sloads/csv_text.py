"""What a delivered CSV's *text* looks like — the one owner of its line ending.

Every CSV sloads delivers is a stamped file: a ``#``-prefixed methods block and
per-file conventions block, then a header row and the data. The prose half is
built by string joins on ``"\\n"``; the data half was built by :mod:`csv`, whose
default ``lineterminator`` is ``"\\r\\n"``. So every delivered file mixed the two
within itself (2026-09-08 review C4, #242) — an editor, a ``git diff`` and a
strict reader each have to decide what that means, and none of them should have
to.

**LF, everywhere.** RFC 4180 names CRLF, and every reader that matters — Excel
included — accepts LF; nothing else sloads writes is CRLF (the NASTRAN decks, the
``.tex`` sources, ``METHODS.txt`` and the comment blocks above these very rows
are all LF), so LF is the choice that makes one file, and the whole bundle, read
one way.

The rule is worth an owner rather than a ``lineterminator=`` argument repeated at
seven call sites, because the failure is invisible: a writer added later without
the argument produces a file that *looks* right in every viewer and is mixed on
disk. :func:`writer` and :func:`dict_writer` are the two constructions the
package makes, and ``tests/test_csv_text.py`` reads every delivered channel back
to check that no byte of ``\\r`` reached any of them.
"""

from __future__ import annotations

import csv
from typing import Any, Sequence, TextIO

#: The line ending of every CSV sloads delivers. See the module docstring for
#: why it is not the :mod:`csv` default.
CSV_LINE_TERMINATOR = "\n"


def writer(buf: TextIO) -> Any:
    """A :func:`csv.writer` that ends its lines the way this package does."""
    return csv.writer(buf, lineterminator=CSV_LINE_TERMINATOR)


def dict_writer(buf: TextIO, fieldnames: Sequence[str]) -> Any:
    """A :class:`csv.DictWriter` that ends its lines the way this package does."""
    return csv.DictWriter(buf, fieldnames=list(fieldnames),
                          lineterminator=CSV_LINE_TERMINATOR)
