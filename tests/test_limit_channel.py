"""The one load basis: what a render states, and that nothing can ask for another.

Design note 48 built ``report.LoadChannel`` as a *switch* -- an ULTIMATE channel
(case selection, the export deck, the case index, the oracle technical report)
and a LIMIT channel (the CLI and the GUI's per-module analysis surfaces). Note 49
**OR-116** removed the choice: every load sloads delivers is LIMIT, on every
surface, with its factor stated and applied nowhere. The enum kept a single
member until the front-end that named it retired (#270), and the parameter
itself went at #29 (2026-10-18): no renderer, CSV writer or stamp takes a basis
argument, and the name ``LoadChannel`` appears in no shipped source.

Gates here:

* **G-OR-44** -- there is no basis to choose: no renderer takes a ``channel``
  argument and no shipped source names one. A page or a writer cannot ask for
  ULTIMATE because there is nothing to ask; the hazard the switch's default
  used to guard against (a caller forgetting the argument) is closed by
  construction.
* **G-OR-47** -- a LIMIT render applies no factor, emits no ``-ULT`` marker
  except on the two already-ultimate families (OR-118), and states its basis
  with the instruction to apply the factor in the sizing analysis.
* **G-OR-71** -- no path in ``sloads/`` multiplies a load by a safety factor.
  The structural form of "stated, never applied"; see the scan at the foot of
  this file, and ``tests/test_deck_basis.py`` for the deck-side half (G-OR-73).
* the ``N/A`` half of **OR-82**: a condition prescribing no factor never prints
  one.
"""

import glob
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sloads.modules  # noqa: F401
from sloads import io
from sloads.registry import run_all_modules
from sloads.report import (
    critical_rows,
    format_value,
    load_cases_to_rows,
    module_text_report,
    results_to_rows,
    summary_rows,
    text_report,
)
from sloads.report.methods import bundle_stamps, csv_comment_block, methods_statement
from sloads.safety_factors import prescribes_factor
from sloads.units import is_load_unit

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = sorted(glob.glob(os.path.join(_ROOT, "examples", "*.project.json")))
_GA = os.path.join(_ROOT, "examples", "ga6_normal.project.json")


def _modules(path):
    return run_all_modules(io.load_project(path))


# --------------------------------------------------------------------------- #
# G-OR-44 -- there is no basis to choose
# --------------------------------------------------------------------------- #
#: Every renderer, writer and stamp that used to take the switch.
_ONE_BASIS_SURFACES = (
    module_text_report, text_report, summary_rows, results_to_rows,
    critical_rows, load_cases_to_rows, io.load_cases_csv, io.write_load_cases_csv,
    methods_statement, csv_comment_block, bundle_stamps,
)


def test_no_renderer_takes_a_basis_argument():
    """The parameter is gone, not defaulted (#29, 2026-10-18).

    Note 48 built ``channel=`` into every surface and note 49 OR-116 left it
    with one legal value; a parameter with one legal value is a question with
    one answer, and a reader who sees it asks what the other answer is. None of
    these signatures names a channel now, and ``sloads.report`` exports no
    ``LoadChannel``.
    """
    import inspect

    import sloads.report

    for fn in _ONE_BASIS_SURFACES:
        names = set(inspect.signature(fn).parameters)
        assert not {n for n in names if "channel" in n}, (fn.__qualname__, names)
    assert not hasattr(sloads.report, "LoadChannel")


def test_no_shipped_source_names_a_load_channel():
    """The structural half: the switch cannot come back under its old name.

    Scans the code lines (comments stripped) of every shipped Python file --
    ``sloads/``, ``oracle_app/``, ``app_shell/``, ``scripts/``, ``cli.py``,
    ``oracle.py`` -- for ``LoadChannel``. A render that wanted two bases again
    would have to build the switch from nothing and say so in a design note.
    """
    offenders = []
    roots = [os.path.join(_ROOT, d) for d in ("sloads", "oracle_app", "app_shell", "scripts")]
    files = [os.path.join(_ROOT, "cli.py"), os.path.join(_ROOT, "oracle.py")]
    for root in roots:
        for dirpath, _dirs, names in os.walk(root):
            files += [os.path.join(dirpath, n) for n in names if n.endswith(".py")]
    for path in sorted(files):
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if "LoadChannel" in line.split("#", 1)[0]:
                    offenders.append(f"{os.path.relpath(path, _ROOT)}:{n}")
    assert not offenders, offenders


def test_the_default_render_applies_no_factor_and_states_it():
    """The endpoint of OR-86, asserted on the default path (note 49 OR-116).

    Replaces ``test_the_ultimate_channel_still_applies_the_factor``. The engine
    module is the right witness twice over: its 23.367(a)(2) cases are computed
    already ultimate at SF = 1.0, so this also pins OR-118 -- the ``-ULT``
    marker survives exactly there.
    """
    mr = [m for m in _modules(_GA) if m.module == "engine"][0]
    text = module_text_report("Engine", mr.conditions)
    assert "Loads are LIMIT" in text
    condition = next(c for c in mr.conditions
                     if any(is_load_unit(v.units, v.quantity or "")
                            for v in c.values))
    load = next(v for v in condition.values
                if is_load_unit(v.units, v.quantity or ""))
    assert condition.safety_factor is not None
    # the calc's own number, unscaled -- and the factor still stated
    assert format_value(load.value, load.units) in text
    assert format_value(condition.safety_factor) in text


# --------------------------------------------------------------------------- #
# G-OR-47 -- what a LIMIT render says, and does not say
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_a_limit_render_never_marks_a_value_ultimate(path):
    for mr in _modules(path):
        text = module_text_report(mr.module, mr.conditions)
        assert "[ULTIMATE" not in text, f"{path}/{mr.module}"
        # OR-118: ``-ULT`` survives on the two families computed already
        # ultimate and nowhere else, so its presence is checked against the
        # cases rather than forbidden outright.
        already = [c for c in mr.conditions if c.safety_factor == 1.0]
        # Data lines only: the basis header *explains* the ``-ULT`` marker in
        # prose ("a load marked -ULT is already ultimate"), so a whole-text grep
        # would be satisfied by the explanation rather than by a value.
        values = "\n".join(ln for ln in text.splitlines() if ln.startswith("    "))
        if not already:
            assert "-ULT" not in values, f"{path}/{mr.module}"
            for row in summary_rows(mr.module, mr.conditions):
                for key, cell in row.items():
                    assert "-ULT" not in str(key), f"{path}/{mr.module}: {key}"


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_a_limit_render_states_its_basis_and_points_at_the_deliverable(path):
    """``CONVENTIONS.md`` §3: the basis *and* who applies the factor, in band.

    Note 49 OR-116/OR-117: there is no longer an ULTIMATE deliverable to point
    at, so the pointer becomes an instruction -- apply it in the sizing
    analysis."""
    for mr in _modules(path):
        text = module_text_report(mr.module, mr.conditions)
        assert "Loads are LIMIT" in text
        assert "applied nowhere" in text
        assert "sizing analysis" in text


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_a_limit_render_reports_the_calc_value_unscaled(path):
    """The whole point: the number is the calc's own, whatever the factor is."""
    for mr in _modules(path):
        text = module_text_report(mr.module, mr.conditions).replace(",", "")
        for c in mr.conditions:
            if c.safety_factor in (None, 1.0):
                continue        # nothing to distinguish scaled from unscaled
            for v in c.values:
                if not is_load_unit(v.units, v.quantity or "") or not v.value:
                    continue
                assert format_value(v.value, v.units) in text, (
                    f"{path}/{mr.module}: {v.label} is not at its LIMIT value")


# --------------------------------------------------------------------------- #
# OR-82 -- a condition that prescribes no factor never prints one
# --------------------------------------------------------------------------- #
def test_a_factorless_condition_prints_no_factor():
    for mr in _modules(_GA):
        factorless = [c for c in mr.conditions if not prescribes_factor(c)]
        if not factorless:
            continue
        text = module_text_report(mr.module, factorless)
        assert "SF=1.5" not in text, f"{mr.module} claims a factor it lacks"
        for row in summary_rows(mr.module, factorless):
            assert row.get("SF", "") in ("", "N/A"), (mr.module, row.get("SF"))


if __name__ == "__main__":
    import traceback

    failed = 0
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for name, fn in tests:
        marks = getattr(fn, "pytestmark", [])
        args = [a for m in marks for a in (m.args[1] if m.name == "parametrize"
                                           else [])]
        try:
            if args:
                for a in args:
                    fn(a)
            else:
                fn()
            print(f"PASS {name}")
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)


# --------------------------------------------------------------------------- #
# G-OR-71 -- no path in sloads/ multiplies a load by a safety factor
# --------------------------------------------------------------------------- #
#: The one place a ``* sf`` is not a safety factor. ``FLAPLOAD.BAS`` names the
#: flap area of one side ``SF``, and the port keeps the manual's variable names
#: so the code reads against the listing. Stated here with its reason rather
#: than filtered out silently: an exception nobody can see is how a scan like
#: this rots into a formality.
_NOT_A_SAFETY_FACTOR = {
    "sloads/modules/flap.py": "`sf` is the flap area of one side (sq ft), "
                              "FLAPLOAD.BAS's own name for it",
    "sloads/safety_factors.py": "`ultimate_basis` IS |value| x SF -- the "
                                "comparison key every governing-case pick "
                                "ranks on (note 58 D-58.2), a basis and "
                                "never a delivered value; the scope test "
                                "below pins it as the file's only multiply",
}

#: ``[\w.]*`` before each name is not decoration: the forms actually removed
#: from the tree were ``* c.safety_factor`` and ``* r.safety_factor``, and a
#: pattern anchored straight to the bare name matches neither. The teeth test
#: below found that gap; without it this scan would have shipped blind to the
#: exact spelling it exists to catch.
#: ``case_sf`` beside ``_sf``: note 56 D-56.1 promoted the per-case factor
#: reader out of what is now ``report.applied`` into ``deck_format`` under a
#: public name, and
#: ``\bsf\b`` does **not** match inside ``case_sf`` (``_`` is a word character,
#: so there is no boundary before ``sf``). Without this alternative the rename
#: alone would have blinded the scan to ``* case_sf(result)`` -- silently, since
#: a text guard that matches nothing still passes.
_MULTIPLY = re.compile(
    r"\*\s*[\w.]*(?:case_sf|_sf)\(|\*\s*[\w.]*\bsf\b|\bsf\s*\*"
    r"|\*\s*[\w.]*\bsafety_factor\b|\bsafety_factor\s*\*"
    r"|\*\s*[\w.]*\bULTIMATE_FACTOR\b|\bULTIMATE_FACTOR\s*\*")


def test_no_path_in_sloads_multiplies_a_load_by_a_safety_factor():
    """**G-OR-71** -- design note 49 OR-116, the whole-tree form.

    The factor is stated and applied nowhere: not on a module view, not in a
    report, not in the exported deck. This is the structural version of that
    sentence, because prose cannot hold it -- the multiply was removed from 81
    sites across 7 files, and a single one creeping back would be invisible to
    every other gate in the suite except ``G-OR-72``, which sees only the
    balanced deck.

    A text scan is crude on purpose. It cannot be fooled by a helper's name or
    by which module the arithmetic hides in, and its one false positive is
    named above with the reason it is not a safety factor.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    offenders = []
    for dirpath, _dirs, files in os.walk(os.path.join(root, "sloads")):
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            if rel in _NOT_A_SAFETY_FACTOR:
                continue
            with open(path, encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    code = line.split("#", 1)[0]
                    if _MULTIPLY.search(code):
                        offenders.append(f"{rel}:{n}: {line.strip()}")
    assert not offenders, (
        "a load is multiplied by a safety factor; the factor is stated and "
        "applied nowhere (note 49 OR-116):\n  " + "\n  ".join(offenders))


def test_the_g_or_71_scan_would_catch_a_multiply():
    """The scan's teeth, since a pattern that matches nothing proves nothing."""
    assert _MULTIPLY.search("out = value * sf")
    assert _MULTIPLY.search("row = v.value * c.safety_factor")
    assert _MULTIPLY.search("y = station.myy * r.safety_factor")
    assert _MULTIPLY.search("fz = load.fz * _sf(result)")
    assert _MULTIPLY.search("fz = load.fz * case_sf(result)")
    assert _MULTIPLY.search("fz = load.fz * deck_format.case_sf(result)")
    assert _MULTIPLY.search("x = ULTIMATE_FACTOR * limit")
    assert _MULTIPLY.search("x = limit * ULTIMATE_FACTOR")
    # ...and does not fire on reading or stating the factor, which is the whole
    # point: `case_sf` and `sf_str` survive OR-116, only the multiply goes.
    assert not _MULTIPLY.search("sf = case_sf(result)")
    assert not _MULTIPLY.search('"SF": sf_str(sf)')
    assert not _MULTIPLY.search("lf = [cl * q for cl, q in zip(clf, qs)]")


def test_the_safety_factors_exemption_covers_exactly_the_comparison_key():
    """The G-OR-71 exemption for ``safety_factors.py`` stays as narrow as its
    stated reason: the file's ONE matching line is ``ultimate_basis``'s own
    ``abs(value) * safety_factor`` (note 58 D-58.2 -- a ranking key, never a
    delivered value). A second multiply appearing anywhere in the file fails
    here, so the per-file exemption cannot quietly widen into a blind spot."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "sloads", "safety_factors.py")
    hits = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            code = line.split("#", 1)[0]
            if _MULTIPLY.search(code):
                hits.append((n, line.strip()))
    assert len(hits) == 1, hits
    assert hits[0][1] == "return abs(value) * safety_factor", hits
