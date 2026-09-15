"""Benchmark-first has a presence guard: every registered module carries a gate.

`CLAUDE.md` rule 2 — an oracle test (±0.1 %, page-cited) where a printed oracle
exists, otherwise a stated physics-closure gate in CI — was **prose only** until
#186. Nothing asserted that a registered module had either, so a module could
register, run in both front ends and ship with no gate at all while the suite
stayed green. The 2026-09-04 project review (R-16) found the coverage complete by
inspection and filed exactly that objection: inspection is not a guard, and the
module that needs one is the module nobody inspects.

This is the structural half practice 3 requires — the manifest is
``tests/module_gates.py``, and these tests make the registry and the manifest
answer to each other in both directions.
"""

from __future__ import annotations

import ast
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from module_gates import CLOSURE, GATES, ORACLE

import sloads.modules  # noqa: F401  (importing populates the registry)
from sloads import registry

_TESTS = os.path.dirname(os.path.abspath(__file__))

#: A page of Reference 1. A hyphenated range ("p217-221") yields only its leading
#: page, which is the intent: the range is prose for the reader, and the one page
#: the test must actually name is where its figures start.
_PAGE = re.compile(r"\bp\d{2,3}\b")

#: The coarser citations, used when a gate names no page at all. ``Ch N`` is here
#: because Reference 1's chapter hand-calcs are printed figures too -- BALLOADS'
#: only oracle is the Ch 9 case-202 worked example, and a page-only rule would
#: have forced it to call itself a closure and lose the distinction this manifest
#: exists to record.
_SOURCE = re.compile(r"Appendix\s+[AB]\b|\bCh\s+\d+\b")


def _test_path(module: str) -> str:
    return os.path.join(_TESTS, f"test_{module}.py")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _defined_test_names(path: str) -> set:
    tree = ast.parse(_read(path))
    return {n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def test_every_registered_module_has_a_gate_and_every_gate_a_module():
    """**The presence guard itself** — the two sets are equal, both directions.

    A module that registers without a manifest row fails at the commit that adds
    it, which is the whole point: the alternative is finding out at the next
    review, or not at all. A row whose module stopped registering fails too — a
    manifest that outlives its subject is how a statement and its code come
    apart, and this file is a statement about the code.
    """
    registered = set(registry.available())
    claimed = set(GATES)
    assert registered, "the registry is empty; sloads.modules did not import"
    assert registered - claimed == set(), (
        "registered modules with no benchmark-first gate declared in "
        f"tests/module_gates.py: {sorted(registered - claimed)} — CLAUDE.md rule 2 "
        "requires an oracle test or a stated closure gate for every module")
    assert claimed - registered == set(), (
        "tests/module_gates.py declares gates for modules that no longer "
        f"register: {sorted(claimed - registered)}")


def test_every_gate_names_tests_that_exist():
    """A named gate that does not exist is worse than no manifest.

    Asserted against the test file's own AST rather than by importing it: a
    renamed or deleted gate test must fail *here*, naming the module, instead of
    surfacing as a collection error somewhere else in the suite.
    """
    for module, gate in sorted(GATES.items()):
        path = _test_path(module)
        assert os.path.isfile(path), f"{module}: no {os.path.relpath(path, _TESTS)}"
        assert gate.tests, f"{module}: gate names no test"
        defined = _defined_test_names(path)
        missing = [t for t in gate.tests if t not in defined]
        assert not missing, (
            f"{module}: tests/module_gates.py names gate tests that "
            f"tests/test_{module}.py does not define: {missing}")


def test_every_oracle_gate_keeps_its_citation_in_the_test_file():
    """**The drift half**: the printed number and its page live in the test.

    `CLAUDE.md`'s math-fidelity rule puts the citation in the test, not only in a
    doc — so the manifest may not be the only place a page number survives. If a
    refactor drops `p231` from ``tests/test_landing.py``, that is the citation
    gone from the evidence, and it fails here.

    Only the token has to match, not the sentence: the manifest describes what
    the page prints and the test asserts it, and requiring the two prose forms to
    agree would make every reworded comment a failure.

    **Every** cited page must appear, not merely one of them. An "any" rule has
    no teeth where a citation also names its appendix: `Appendix A p999` would
    pass on the strength of the `Appendix A` half, which is the one part of a
    citation that is true of nearly every test file in the suite. The coarser
    token is accepted only when a gate names no page at all — `select` and
    `structural_speeds` match printed summaries the manual does not paginate as a
    table, and BALLOADS' oracle is a chapter hand-calc.
    """
    for module, gate in sorted(GATES.items()):
        if gate.kind != ORACLE:
            continue
        text = _read(_test_path(module))
        pages = _PAGE.findall(gate.cites)
        if pages:
            missing = [p for p in pages if p not in text]
            assert not missing, (
                f"{module}: cited page(s) {missing} appear nowhere in "
                f"tests/test_{module}.py — the citation left the evidence")
            continue
        coarse = _SOURCE.findall(gate.cites)
        assert coarse, (
            f"{module}: an ORACLE gate must cite a printed source (a page, an "
            f"appendix or a chapter); got {gate.cites!r}")
        assert any(tok in text for tok in coarse), (
            f"{module}: none of the cited sources {coarse} appears in "
            f"tests/test_{module}.py — the citation left the evidence")


def test_every_closure_gate_states_its_invariant_and_why_no_oracle_exists():
    """A closure states *what closes* — and its test file says why it must.

    Rule 2 allows a closure gate only where no printed oracle exists, so the
    absence is part of the evidence and belongs with it. Each of these files
    already opens by saying so in its own words ("no printed oracle exists for a
    spanwise tail distribution"; "ships no program and no printed station
    table"; Appendix B "is **absent** from the bundled references"), and this
    keeps that sentence there: a closure test file that stops explaining itself
    reads, to the next author, as a module that simply never got its oracle.

    Deliberately *not* asserted: that the manifest's prose avoids naming an
    appendix. The honest explanation usually must name one — "Appendix A stops
    at the totals" is the reason ``tail_span`` closes rather than matches — so a
    guard banning the token would fire on exactly the rows that explain
    themselves best, and would need a per-row exception list to stay green. A
    guard maintained by exceptions is not a guard.
    """
    absence = re.compile(r"no oracle|no printed|is \*\*absent\*\*|absent from", re.I)
    for module, gate in sorted(GATES.items()):
        if gate.kind != CLOSURE:
            continue
        assert len(gate.cites) > 60, (
            f"{module}: a closure gate must state the invariant it closes on, "
            f"not merely assert that one exists; got {gate.cites!r}")
        text = _read(_test_path(module))
        assert absence.search(text), (
            f"{module}: tests/test_{module}.py no longer states that no printed "
            "oracle exists for it — rule 2 permits a closure gate only in that "
            "case, so the statement is part of the evidence (#186)")


def test_every_gate_declares_a_known_kind():
    for module, gate in sorted(GATES.items()):
        assert gate.kind in (ORACLE, CLOSURE), f"{module}: unknown kind {gate.kind!r}"


def test_the_oracle_status_section_points_at_this_manifest():
    """The canonical prose names its machine-readable half, and does not restate it.

    ``00_theory_sources.md`` § Oracle status calls itself "the single
    authoritative statement of how each module is validated". It stays normative
    — it carries the *reasoning* (why Appendix B yields no twin oracle, why an
    unextractable page is not an unreadable one). What it must not do is leave
    the per-module mapping discoverable only by reading 23 test files, which is
    the state R-16 found.
    """
    path = os.path.join(os.path.dirname(_TESTS), "docs", "20_theory",
                        "00_theory_sources.md")
    text = _read(path)
    assert "tests/module_gates.py" in text, (
        "docs/20_theory/00_theory_sources.md no longer points at "
        "tests/module_gates.py — the canonical Oracle-status section and its "
        "machine-readable half have come apart (#186)")


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
