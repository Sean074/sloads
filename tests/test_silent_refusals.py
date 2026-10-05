"""No silent refusal without a stated reason (#344, CLAUDE.md rule 3).

Under the error contract a ``ValueError`` is a present-but-invalid input
refused by name. An ``except`` that catches it and hands back nothing -- an
empty list, ``None``, ``""``, a ``continue`` -- turns that refusal into
silence, and #344 found three that silently switched off the T-tail warnings
or emptied a whole deck family. Most such catches are honest ("a string that
is not a number is not a station"), so the rule is not *never*: it is that
each one states, on its ``except`` line or the line above it, why silence is
right there -- ``# refusal: <why>``. A new silent catch cannot land unstated.
"""

import ast
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = pathlib.Path(__file__).resolve().parents[1] / "sloads"
_MARKER = "# refusal:"
#: What a handler hands back that says nothing.
_EMPTY = {"[]", "None", "''", '""', "{}", "()", "0", "0.0"}


def _catches_value_error(node: ast.ExceptHandler) -> bool:
    types = node.type.elts if isinstance(node.type, ast.Tuple) else [node.type]
    return any(isinstance(t, ast.Name) and t.id == "ValueError" for t in types)


def _says_nothing(stmt) -> bool:
    if isinstance(stmt, (ast.Pass, ast.Continue, ast.Break)):
        return True
    if isinstance(stmt, ast.Return):
        return stmt.value is None or ast.unparse(stmt.value) in _EMPTY
    if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
        return stmt.value is not None and ast.unparse(stmt.value) in _EMPTY
    return False


def _is_silent(body) -> bool:
    """Every statement of the handler says nothing -- however many there are.
    Until #367 only a one-statement body was scanned, so ``x = []`` then
    ``continue`` was a silent catch the guard could not see. A body that
    raises, calls anything (a record, a warning) or computes a value is not
    silent; the reason is then the code's own."""
    return all(_says_nothing(stmt) for stmt in body)


def silent_value_error_catches():
    """``[(path, line, stated)]`` for every silent ``ValueError`` catch in sloads/."""
    out = []
    for path in sorted(_ROOT.rglob("*.py")):
        source = path.read_text()
        lines = source.splitlines()
        for node in ast.walk(ast.parse(source)):
            if (isinstance(node, ast.ExceptHandler) and node.type is not None
                    and _catches_value_error(node) and _is_silent(node.body)):
                here = lines[node.lineno - 1]
                above = lines[node.lineno - 2] if node.lineno > 1 else ""
                out.append((path.relative_to(_ROOT.parent), node.lineno,
                            _MARKER in here or above.strip().startswith(_MARKER)))
    return out


def test_every_silent_value_error_catch_states_why():
    unstated = [f"{p}:{n}" for p, n, stated in silent_value_error_catches() if not stated]
    assert not unstated, ("a silent ValueError catch must say why silence is right "
                          f"('{_MARKER} <why>' on or above the except line): {unstated}")


def test_the_guard_sees_the_catches_it_exists_for():
    """The scan is not vacuous: it finds the sites #344 annotated, among them
    SELECT's one-engine-out step. A handler catching ``MissingInputError``
    alone is not scanned -- the chain does not exist, and silence is the
    contract (``00_program_overview.md`` §error contract)."""
    found = [(str(p), stated) for p, _, stated in silent_value_error_catches()]
    assert len(found) > 40
    assert ("sloads/modules/select.py", True) in found
    assert ("sloads/validation.py", True) in found


def test_a_multi_statement_silent_body_is_seen():
    """#367: the two-statement blind spot, probed so it stays closed (the
    #345 class -- a structural gate is only as good as its probed edges)."""
    source = ("for v in values:\n"
              "    try:\n"
              "        f(v)\n"
              "    except ValueError:\n"
              "        out = []\n"
              "        continue\n")
    handler = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.ExceptHandler))
    assert _is_silent(handler.body)
    recorded = ast.parse("try:\n    f()\nexcept ValueError as exc:\n    out = []\n"
                         "    record.append(exc)\n")
    handler = next(n for n in ast.walk(recorded) if isinstance(n, ast.ExceptHandler))
    assert not _is_silent(handler.body)


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
