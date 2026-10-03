"""The override cross-check: one comparison, one printing (#243).

The 2026-09-08 GUI review (G6) found the override warnings firing below their
own display precision and printing one number twice -- "This is 0.4356 but the
paired planform's tip/centreline chord says 0.4356" -- and a 0.02 % aspect-ratio
rounding flagged with the weight of a real data error. `sloads.cross_check`
owns the comparison and the printing; this file pins both and refuses a bare
near-zero comparison feeding a warning where the cross-checks live.
"""

import ast
import os

import pytest

from sloads import io, validation
from sloads.cross_check import CROSS_CHECK_REL, cross_check_disagrees, shown_apart
from sloads.units import format_value

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _four_sig(v):
    """The GUI caption's echo (`oracle_app.form._shown` without a unit)."""
    return f"{v:,.4g}"


# --------------------------------------------------------------------------- #
# 1. The comparison
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("typed, owner", [
    (0.43561, 0.43559),   # G6: the tip/centreline chord ratio, equal as printed
    (6.095, 6.094),       # G6: AR, 0.02 % apart
    (4.605, 4.604),       # G6: the second AR pair
])
def test_the_review_s_rounding_pairs_do_not_warn(typed, owner):
    assert not cross_check_disagrees(typed, owner, _four_sig)


def test_a_disagreement_past_the_band_warns():
    """The elevator's 16.4 vs 16.43 sq ft (0.18 %) is the review's real case."""
    assert cross_check_disagrees(16.4, 16.43, _four_sig)


def test_a_warning_never_prints_one_number_twice():
    """Past the band but equal at the printed row (a pound row, 0.1 % of 2 lb):
    the printing decides, so the sentence cannot show two identical numbers."""
    pound = lambda v: format_value(v, "lb")  # noqa: E731
    assert abs(2.4 - 2.403) > CROSS_CHECK_REL * 2.403 and pound(2.4) == pound(2.403)
    assert not cross_check_disagrees(2.4, 2.403, pound)


def test_zero_against_zero_agrees_and_zero_against_a_value_does_not():
    assert not cross_check_disagrees(0.0, 0.0, _four_sig)
    assert cross_check_disagrees(0.0, 1.0, _four_sig)


# --------------------------------------------------------------------------- #
# 2. Exact-equality checks print their numbers apart
# --------------------------------------------------------------------------- #
def test_a_sub_row_drift_prints_apart_at_one_decimal_count():
    assert shown_apart([5000.0, 4999.6], "lb") == ["5000.0", "4999.6"]
    assert shown_apart([5000.0, 5000.0, 4999.96], "lb") == ["5000.00", "5000.00", "4999.96"]


def test_values_that_already_print_apart_stay_at_their_row():
    assert shown_apart([5000.0, 4990.0], "lb") == [format_value(5000.0, "lb"),
                                                   format_value(4990.0, "lb")]


def test_the_mtow_drift_warning_states_a_sub_pound_drift():
    project = io.load_project(os.path.join(_ROOT, "examples", "ga6_normal.project.json"))
    mtow = project.weight.max_takeoff_weight_lb
    project.speeds.weight_lb = mtow - 0.4
    warning = next(w for w in validation.consistency_warnings(project)
                   if w.code == "mtow_representation_drift")
    assert f"{mtow:.1f} lb" in warning.message
    assert f"{mtow - 0.4:.1f} lb" in warning.message


# --------------------------------------------------------------------------- #
# 3. The guard: no bare near-zero comparison feeds a warning
# --------------------------------------------------------------------------- #
_CROSS_CHECK_SITES = ("sloads/validation.py", "oracle_app/form.py")


def _bare_drift_tests(tree):
    """``abs(a - b) > c`` with ``c`` inside the band, per enclosing function."""
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Compare) and len(node.ops) == 1
                    and isinstance(node.ops[0], ast.Gt)):
                continue
            left, right = node.left, node.comparators[0]
            if (isinstance(left, ast.Call) and isinstance(left.func, ast.Name)
                    and left.func.id == "abs" and left.args
                    and isinstance(left.args[0], ast.BinOp)
                    and isinstance(left.args[0].op, ast.Sub)
                    and isinstance(right, ast.Constant)
                    and isinstance(right.value, float)
                    and right.value < CROSS_CHECK_REL):
                yield fn, node


def test_no_cross_check_compares_below_the_band_on_its_own():
    """A new cross-check calls ``cross_check_disagrees``. One whose contract is
    exact equality may test any difference, but then prints through
    ``shown_apart`` in the same function, so the drift it found is visible."""
    offenders, seen = [], 0
    for rel in _CROSS_CHECK_SITES:
        with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for fn, node in _bare_drift_tests(tree):
            seen += 1
            prints_apart = any(isinstance(n, ast.Name) and n.id == "shown_apart"
                               for n in ast.walk(fn))
            if not prints_apart:
                offenders.append(f"{rel}:{node.lineno} ({fn.name})")
    assert seen, "no exact-equality check found -- the walk would pass vacuously"
    assert not offenders, (
        "a cross-check warns on a difference below the band without printing it "
        f"apart; call sloads.cross_check.cross_check_disagrees: {offenders}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
