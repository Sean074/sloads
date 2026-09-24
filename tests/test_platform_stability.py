"""Platform-stable deliverable bytes (``CONVENTIONS.md`` §7, 2026-08-16).

A byte in a deck or report must not depend on the libm build, FMA, or the
interpreter's ``sum()``. Three owners, three guards:

* ``picks.extreme`` -- keyed picks are first-in-order inside a relative tie
  band, and **this file** walks the package's AST so no builtin ``min``/``max``
  with a ``key=`` can re-appear anywhere in ``sloads/``. The owner was
  ``select._extreme``, private to one module, until review 2026-08-20 CR-B-1
  found a live keyed pick in ``select`` itself that the old substring grep could
  not see (``(min if want_min else max)(...)`` contains neither ``max(`` nor
  ``min(`` next to ``key=``) plus the same defect class in five other modules
  and in the exporters;
* ``deck_format.fmt3`` -- vector-card components snap dust and ``-0`` to
  ``0.000000E+00`` (``tests/test_applied.py``);
* **this file** -- every float summation in ``sloads/`` is ``math.fsum``, which
  is exactly rounded and therefore identical on every platform and Python
  version. Python 3.12 changed the built-in ``sum()`` of floats to compensated
  (Neumaier) summation, so ``sum(ld.fz for ld in loads)`` on 3.12 landed a few
  ulp from 3.9/3.11 and the developer's Mac; where a value sat on a print
  boundary (an integer-valued residual, a 7th-digit tie in a FORCE card) the
  frozen Imperial digest failed on the 3.12 leg only. ``fsum`` closes the class
  rather than chasing the next knife-edge; the digest was regenerated once,
  deliberately, when the sweep landed (20 lines, all last-digit).

The only built-in ``sum`` left is the counting idiom ``sum(1 for ...)``, which
is integer arithmetic and exact everywhere.
"""

import ast
import glob
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import sloads
from sloads.picks import extreme

_PKG = os.path.dirname(os.path.abspath(sloads.__file__))

#: A built-in ``sum(`` call -- not ``fsum(``, not ``.sum(``, not the ``sum(1 for``
#: counting idiom.
_BARE_SUM = re.compile(r"(?<![\w.])sum\((?!1 for\b)")


def _code_lines(path):
    """(lineno, text) for the lines of ``path`` that are code -- docstrings and
    comment lines dropped, trailing comments stripped -- so prose that *mentions*
    ``sum(items)`` does not trip the guard."""
    out = []
    in_doc = False
    with open(path, encoding="utf-8") as fh:
        for n, ln in enumerate(fh, 1):
            stripped = ln.strip()
            if in_doc:
                if stripped.count('"""') % 2 == 1:
                    in_doc = False
                continue
            if stripped.count('"""') % 2 == 1:
                in_doc = True
                continue
            if stripped.startswith("#"):
                continue
            out.append((n, ln.partition("  #")[0]))
    return out


def test_every_float_summation_in_sloads_is_fsum():
    hits = []
    for root, _dirs, files in os.walk(_PKG):
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            for n, text in _code_lines(path):
                if _BARE_SUM.search(text):
                    hits.append(f"{os.path.relpath(path, _PKG)}:{n}: {text.strip()}")
    assert not hits, (
        "built-in sum() over floats is not platform-stable (Python 3.12 compensates "
        "it, 3.10/3.11 do not) -- use math.fsum, or `sum(1 for ...)` for a count:\n  "
        + "\n  ".join(hits))


def _keyed_picks(source, label):
    """``[(lineno, dump)]`` for every builtin ``min``/``max`` call in ``source``
    that carries a ``key=`` keyword.

    An AST walk, not a grep: CR-B-1's live bypass was
    ``(min if want_min else max)(bal_a, key=...)``, which contains neither
    ``min(`` nor ``max(``. Matched on the *callee expression*, so the
    conditional form, an aliased ``builtins.max``, and a call spread over
    several lines all read the same to the guard.

    What it deliberately does not see: a pick written as an accumulation loop
    (``if v > best: best = v``), which no static walk can distinguish from
    ordinary arithmetic. §7's wording is scoped to match this guard exactly --
    the shape it names is the shape it enforces.
    """
    def is_builtin_min_max(node):
        if isinstance(node, ast.Name):
            return node.id in ("min", "max")
        if isinstance(node, ast.IfExp):  # (min if c else max)(...)
            return is_builtin_min_max(node.body) or is_builtin_min_max(node.orelse)
        return False

    hits = []
    for node in ast.walk(ast.parse(source, filename=label)):
        if not isinstance(node, ast.Call) or not is_builtin_min_max(node.func):
            continue
        if any(kw.arg == "key" for kw in node.keywords):
            hits.append((node.lineno, ast.dump(node.func)))
    return hits


def test_every_keyed_pick_in_sloads_goes_through_picks_extreme():
    hits = []
    for root, _dirs, files in os.walk(_PKG):
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, _PKG)
            with open(path, encoding="utf-8") as fh:
                for lineno, _dump in _keyed_picks(fh.read(), rel):
                    hits.append(f"{rel}:{lineno}")
    assert not hits, (
        "a keyed built-in min()/max() is not platform-stable: candidates whose "
        "keys tie in exact arithmetic can land either side of the other by an ulp "
        "on a different libm or Python version, and the pick -- a case, a node, a "
        "pivot row -- flips with them. Route it through sloads.picks.extreme:\n  "
        + "\n  ".join(hits))


def test_extreme_pick_is_first_in_order_across_a_platform_ulp_tie():
    """The keyed pick is stable under last-ulp noise (CI vs local).

    ``BAL A`` at two altitudes carries the same VA and hence the same rudder load;
    on the developer's Mac the two keys are bit-identical and ``max`` returns the
    first, on the Linux CI runner one lands an ulp above the other and ``max``
    returned the *second* -- a different V-n case in the deck for a difference
    no printed digit shows. ``extreme`` picks the first candidate inside a
    ``TIE_REL`` relative band of the extreme, so both platforms agree; a
    genuinely larger candidate anywhere in the list still wins.
    """
    base = 4287.797363708473
    up = math.nextafter(base, math.inf)
    # bit-exact tie -> first (what max() did, so nothing moves locally)
    assert extreme(["a", "b"], {"a": base, "b": base}.__getitem__) == "a"
    # one-ulp tie either way -> still the first
    assert extreme(["a", "b"], {"a": base, "b": up}.__getitem__) == "a"
    assert extreme(["a", "b"], {"a": up, "b": base}.__getitem__) == "a"
    assert extreme(["a", "b"], {"a": -base, "b": -up}.__getitem__,
                   largest=False) == "a"
    # a real difference wins wherever it sits
    assert extreme(["a", "b"], {"a": base, "b": base * 1.001}.__getitem__) == "b"
    assert extreme(["a", "b"], {"a": base, "b": base * 0.999}.__getitem__,
                   largest=False) == "b"


def _ulp_neighbours(value, ulps=4):
    """``value`` shifted 1..``ulps`` steps each way, the last-ulp noise a
    different libm build (or a different summation) puts on the same number."""
    for direction in (math.inf, -math.inf):
        w = value
        for _ in range(ulps):
            w = math.nextafter(w, direction)
            yield w


def test_no_printed_deliverable_cell_hangs_on_the_last_ulp():
    """``format_value`` is continuous under last-ulp noise (#147).

    The formatter's two branches are far apart -- an integral value prints in
    full, everything else at four significant figures -- so on the raw double
    the choice between them was a *discontinuous* function of the last bit:
    ``-687258.0`` printed ``-687258`` and ``-687257.9999999999`` printed
    ``-6.873e+05``. Both reached one landing case's CSV, and which one a cell
    took moved with the libm build, so the frozen Imperial digest passed on the
    developer's Mac and failed on the Linux CI leg. Asserted on the values the
    deliverables actually carry, not on invented ones: every value of every
    condition of the trig-heaviest module of the example that failed.
    """
    from sloads import io, registry
    from sloads.report.render import format_value

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project = io.load_project(
        os.path.join(root, "examples", "concept_regional_jet.project.json"))
    landing = [m for m in registry.run_all_modules(project) if m.module == "landing"]
    assert landing, "the example must still produce landing results"

    checked = 0
    for condition in landing[0].conditions:
        for value in [v.value for v in condition.values] + [condition.safety_factor]:
            if not isinstance(value, float) or not math.isfinite(value) or value == 0.0:
                continue  # a relative ulp band around zero is not a band
            printed = format_value(value)
            checked += 1
            for neighbour in _ulp_neighbours(value):
                assert format_value(neighbour) == printed, (
                    condition.title, value, printed, neighbour,
                    format_value(neighbour))
    assert checked > 100, checked  # the sweep must not quietly empty out


def test_no_emitted_deck_value_hangs_on_the_last_ulp():
    """``deck_format.fmt`` is continuous under last-ulp noise -- the solver-channel half of #147.

    The report channel got this rule at #147; the deck channel did not, and the
    class recurred in the same place it was found the first time: the frozen
    Imperial digest passing on the developer's Mac and failing on the Linux CI
    leg, this time on ``sbeam/balanced_deck``. ``fmt`` prints **seven**
    significant digits, which is finer than a computed load reproduces across
    platforms, so a value sitting on the decimal rounding tie of its seventh
    digit takes round-half-even off the last bit: ``-341426.25`` in the regional
    jet's ``MOMENT`` cards printed ``-3.414262E+05`` here and ``-3.414263E+05``
    there, for one load.

    Asserted over the values the decks **actually emit**, every shipped example,
    by spying on the formatter rather than by re-deriving a candidate set --
    invented values would not have found this one. Before
    :func:`sloads.units.canonical` reached ``fmt``, 248 of the 159,407 emitted
    values moved under this band; the sweep is the whole population, so the next
    emitter that formats a solved scalar by hand fails here too.
    """
    import importlib
    import pkgutil

    import sloads.export as export_pkg
    from sloads.export import deck_format

    import imperial_baseline as baseline

    seen: "list[float]" = []
    original = deck_format.fmt

    def spy(value):
        seen.append(value)
        return original(value)

    # Patched at **every** binding, not only at its owner. The sibling writers do
    # ``from .deck_format import fmt``, so each holds its own reference, and
    # patching the owner alone would silently shrink this sweep from the whole
    # emitted population to one module's cards -- the claim the docstring makes.
    # (#15 moved the primitive out of what is now ``report.applied``, where one
    # patch sufficed.)
    patched = [deck_format]
    for info in pkgutil.iter_modules(export_pkg.__path__):
        module = importlib.import_module(f"sloads.export.{info.name}")
        if getattr(module, "fmt", None) is original:
            patched.append(module)
    assert len(patched) > 1, patched   # the binding sweep must not empty out

    checked = fragile = 0
    for module in patched:
        module.fmt = spy
    try:
        for example in baseline.EXAMPLES:
            seen.clear()
            baseline.artifacts(example)
            for value in seen:
                if (not isinstance(value, float) or not math.isfinite(value)
                        or value == 0.0):
                    continue  # a relative ulp band around zero is not a band
                printed = original(value)
                checked += 1
                for neighbour in _ulp_neighbours(value, ulps=3):
                    if original(neighbour) != printed:
                        fragile += 1
                        assert False, (
                            example, value, printed, neighbour,
                            original(neighbour))
    finally:
        for module in patched:
            module.fmt = original
    # 90,693 values at the #264 fixture set (was >100k over six fixtures).
    assert checked > 80_000, checked  # the sweep must not quietly empty out


def test_the_deck_formatter_still_prints_what_it_used_to():
    """Canonicalising is a fix for the tie, not a change of emitted precision.

    A value nowhere near the seventh-digit boundary prints exactly as it always
    did -- seven significant digits in NASTRAN scientific style. Only a value
    already sitting on the tie can move, and there the seventh digit carried no
    information to lose.
    """
    from sloads.export.deck_format import fmt

    for value, expected in (
        (1234.5678, "1.234568E+03"),
        (-7157.865, "-7.157865E+03"),
        (0.0, "0.000000E+00"),
        (1.0, "1.000000E+00"),
        (-341426.25, "-3.414262E+05"),   # the tie itself, resolved one way only
    ):
        assert fmt(value) == expected, (value, fmt(value), expected)


def test_the_keyed_pick_guard_recognises_the_shapes_it_must():
    # the plain forms, and the CR-B-1 bypass the substring grep could not see
    assert _keyed_picks("p = max(cands, key=f)", "t") == [(1, "Name(id='max', ctx=Load())")]
    assert len(_keyed_picks("p = min(cands, key=f)", "t")) == 1
    assert len(_keyed_picks("p = (min if want_min else max)(cands, key=f)", "t")) == 1
    assert len(_keyed_picks("p = max(\n    cands,\n    key=f,\n)", "t")) == 1
    # and what it must not flag
    assert _keyed_picks("p = extreme(cands, f, largest=False)", "t") == []
    assert _keyed_picks("s = max(abs(v) for v in row)", "t") == []
    assert _keyed_picks("b = max(keys) if largest else min(keys)", "t") == []
    assert _keyed_picks("d = frame.max(key='x')", "t") == []       # attribute, not builtin


def test_the_guard_recognises_the_shapes_it_must():
    assert _BARE_SUM.search("x = sum(a for a in b)")
    assert _BARE_SUM.search("total = sum(raw)")
    assert not _BARE_SUM.search("n = sum(1 for r in rows if r.ok)")
    assert not _BARE_SUM.search("x = math.fsum(a for a in b)")
    assert not _BARE_SUM.search("y = fsum(vals)")
    assert not _BARE_SUM.search("z = arr.sum(axis=0)")


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"ok   {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)


# --------------------------------------------------------------------------- #
# Design note 65: every delivered cell prints at the precision its unit
# prescribes (#161). Four gates: the rule by example in both channels, no
# exponent form on any human channel, every emitted unit string rowed, and no
# renderer in ``sloads/report/`` writing a digit count of its own.
# --------------------------------------------------------------------------- #
_EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sloads.__file__))), "examples")
_REPORT_SOURCES = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(sloads.__file__)), "report", "*.py")))


def test_every_delivered_cell_prints_at_its_units_precision():
    """Design note 65 D-65.2 .. D-65.6, one example per row of the table.

    The unit string names the row: a load to the pound, a station to 0.1 in,
    an angle to 0.01 deg, a coefficient at four significant figures with its
    zeros kept -- and no exponent form inside the delivered window, whatever
    the magnitude. A non-zero cell that would print as ``0`` at its row's
    decimals falls to four figures (the floor, D-65.3, one significant
    figure as amended at implementation). An ``int`` with a fixed-decimal row
    prints at the row (a typed 170 kt is the loaded 170.0); one with none is a
    count and prints as itself. The safety factor is a dimensionless
    number like any other (§8 Q1). #147's near-integer pair still prints one
    string, because the twelve-figure quantization stayed.
    """
    from sloads.report.content import Units
    from sloads.report.render import format_value
    from sloads.units import HUMAN_SI, UnitSystem

    cases = [
        # loads, moments, areas, inertias: the whole unit
        (13360.4, "lb", "13360"), (243800.2, "lb-in", "243800"), (-10937.6, "ft-lb", "-10938"),
        (13259.29, "in^2", "13259"), (5566065.78, "lb-in^2", "5566066"),
        (232252.63, "slug-ft^2", "232253"), (586.6, "ft^2", "587"), (1.4, "lb", "1"),
        # lengths and altitude: one decimal (§8 Q2)
        (112.46, "in", "112.5"), (-99636.97, "in", "-99637.0"), (12000.0, "ft", "12000.0"),
        # speeds
        (170.0, "kt(EAS)", "170.0"), (160.42529, "kt(EAS)", "160.4"), (10.0, "ft/s", "10.0"),
        # angles, rates, pressures, percentages (ruling 3), load factors
        (0.5263, "deg", "0.53"), (3.98815, "deg", "3.99"), (4.078, "deg/s", "4.08"),
        (636.6952, "deg/s^2", "636.70"), (3.12, "lb/in^2", "3.12"), (152.949, "lb/ft^2", "152.95"),
        (25.3, "%MAC", "25.30"), (72.0, "%", "72.00"), (6.49997, "% tail MAC", "6.50"),
        (3.8016, "g", "3.80"), (-1.52, "g", "-1.52"),
        # dimensionless: four significant figures, zeros kept, no exponent switch
        (0.4718, "", "0.4718"), (4.93, "", "4.930"), (0.107, "1/deg", "0.1070"),
        (4.4297, "/rad", "4.430"), (2.35, "s", "2.350"), (1.5, "", "1.500"), (1.0, "", "1.000"),
        (24000.4, "", "24000"), (0.004128, "", "0.004128"), (1.0 / 3, "", "0.3333"),
        (9.9995, "", "9.999"), (0.00099995, "", "0.001000"),
        # the floor: a non-zero cell that would print as 0 keeps four figures
        (0.3, "lb-in", "0.3000"), (0.004239, "in", "0.004239"), (0.004, "deg", "0.004000"),
        # zero at the row's decimals; an int as itself
        (0.0, "lb", "0"), (0.0, "in", "0.0"), (0.0, "deg", "0.00"), (0.0, "", "0"),
        (10, "", "10"), (7, "lb", "7"), (170, "kt(EAS)", "170.0"), (12000, "ft", "12000.0"),
        # the exponent window's edges
        (-5.067e-05, "g", "-5.067e-05"), (1.2e9, "", "1.200e+09"),
        # a unit with no row prints at four figures (the gate below is what fails)
        (1234.5678, "furlong", "1235"),
        # the SI labels a converted LoadValue carries resolve no coarser than the
        # Imperial cell they converted from (D-65.5 as amended at #298): the
        # Imperial row plus a decimal per decade the factor divides by
        (59412.3, "N", "59412"), (1542.21, "kg", "1542.2"), (27547.4, "N·m", "27547.4"),
        (2857.46, "mm", "2857.5"), (35.923, "kPa", "35.92"), (7.32, "kN/m²", "7.3200"),
        (48.94, "m/s", "48.94"), (0.5, "kg·m²", "0.5000"), (54.6, "m^2", "54.6000"),
        (3.1, "kg*m^2", "3.1000"), (2.899, "m^2", "2.8990"),    # #298's 31.2 ft² tail, not "3"
        (8.55437, "m²", "8.5544"),                              # the wing geometry's 13259 in²
        (1628.66, "kg·m²", "1628.6600"), (74.57, "kW", "74.6"),
    ]
    for value, units, expected in cases:
        got = format_value(value, units)
        assert got == expected, (value, units, got, expected)
    assert format_value(-687258.0, "lb") == format_value(-687257.9999999999, "lb") == "-687258"
    assert format_value(1.6685) == format_value(1.6684999999999999) == "1.669"
    # The document's Units passes the label of the system it prints in, so an
    # SI cell has the SI row's decimals, an Imperial cell the Imperial row's.
    si, imp = Units(UnitSystem.SI), Units(UnitSystem.IMPERIAL)
    for value, dim, unit, si_dim, si_unit in [
        (3400.0, "mass", "lb", "mass", "kg"), (100.0, "length", "in", "length_in", "mm"),
        (5.2, "pressure", "lb/in^2", "pressure", "kPa"), (31.2, "area", "ft^2", "area_sqft", "m^2"),
    ]:
        assert imp.plain(value, dim) == format_value(value, unit)
        assert si.plain(value, dim) == format_value(value * HUMAN_SI[si_dim].factor, si_unit)
    assert si.plain(31.2, "area") == "2.8986" and si.plain(3400.0, "mass") == "1542.2"
    assert imp.load(13360.4, "force", 1.5) == "13360"
    assert si.load(13360.4, "force", 1.5) == format_value(13360.4 * HUMAN_SI["force"].factor, "N")
    assert si.load(13360.4, "force", 1.5).isdigit()


def _delivered_units_of(project, mass_units=None):
    """Every unit string a LoadValue of every module of ``project`` carries;
    the strings a ``quantity="mass"`` value carries are also added to
    ``mass_units`` when a set is passed (a ``lb`` of mass converts to kg, not N)."""
    from dataclasses import fields, is_dataclass

    from sloads import registry
    from sloads.models import LoadValue

    seen = set()

    def walk(o, depth=0):
        if isinstance(o, LoadValue):
            seen.add(o.units)
            if mass_units is not None and o.quantity == "mass":
                mass_units.add(o.units)
        elif isinstance(o, (list, tuple)):
            for x in o:
                walk(x, depth + 1)
        elif isinstance(o, dict):
            for x in o.values():
                walk(x, depth + 1)
        elif is_dataclass(o) and depth < 6:
            for f in fields(o):
                walk(getattr(o, f.name), depth + 1)
    for result in registry.run_all_modules(project):
        walk(result)
    return seen


def test_every_unit_string_a_fixture_emits_has_a_precision_row():
    """D-65.4's last row is a fallback, never a destination: every unit string
    an example emits, every key the SI converter reads, every SI label it
    writes and every ASCII label the report prints has a row -- and the SI row
    of a label is exactly what the Imperial units that convert to it need to
    print no coarser than their source (D-65.5 as amended at #298; until then
    the row *copied* the Imperial count, and a 31.2 ft² tail printed as ``3``
    m²). The sources are the unit strings a shipped fixture emits, the mass
    strings among them (a ``lb`` of mass converts to kg, not N), and the
    dimensions the report prints itself; a converter row no producer emits
    would not set a row. ``m²`` takes four decimals because the wing geometry
    emits its areas to the square inch, and 0.0001 m² is the nearest decimal
    not coarser than that."""
    import imperial_baseline as baseline
    from sloads import io
    from sloads.report.content import _EXTRA_DIMENSIONS, _IMPERIAL_HUMAN
    from sloads.units import (
        DELIVERED_PRECISION,
        DELIVERED_PRECISION_SI,
        HUMAN_SI,
        UNIT_LABELS,
        Channel,
        UnitSystem,
        _INPUT_KIND,
        _RESULT_TO_SI,
        deliverable_units,
        si_decimals,
    )

    emitted, mass_units = set(), set()
    for example in baseline.EXAMPLES:
        emitted |= _delivered_units_of(io.load_project(os.path.join(_EXAMPLES_DIR, example)), mass_units)
    assert emitted, "the walk must not quietly empty out"
    assert emitted <= set(DELIVERED_PRECISION), sorted(emitted - set(DELIVERED_PRECISION))
    assert set(_RESULT_TO_SI) <= set(DELIVERED_PRECISION), sorted(set(_RESULT_TO_SI) - set(DELIVERED_PRECISION))
    si_labels = {d.label for d in HUMAN_SI.values()} | {si for _f, _i, si in _EXTRA_DIMENSIONS.values()}
    assert si_labels <= set(DELIVERED_PRECISION_SI), sorted(si_labels - set(DELIVERED_PRECISION_SI))

    needed = {}                       # SI label -> the most decimals any source needs

    def source(imperial, factor, label):
        d = si_decimals(imperial, factor)
        assert d is not None, (imperial, label)
        needed[label] = max(needed.get(label, 0), d)

    for unit, (factor, label) in _RESULT_TO_SI.items():
        if unit in emitted:
            source(unit, factor, label)
    for unit in mass_units:
        source(unit, HUMAN_SI["mass"].factor, HUMAN_SI["mass"].label)
    si_human = deliverable_units(UnitSystem.SI, Channel.HUMAN)
    for dim in ("force", "length", "moment", "torque", "pressure", "mass", "mass_inertia"):
        source(getattr(_IMPERIAL_HUMAN, dim).label, getattr(si_human, dim).factor, getattr(si_human, dim).label)
    for factor, imperial, si in _EXTRA_DIMENSIONS.values():
        source(imperial, factor, si)
    for kind, imperial in UNIT_LABELS[UnitSystem.IMPERIAL].items():
        if imperial in DELIVERED_PRECISION:          # the engine record's hp -> kW
            source(imperial, HUMAN_SI[_INPUT_KIND[kind]].factor, UNIT_LABELS[UnitSystem.SI][kind])
    # The report's ASCII spelling of a label is the same unit as the owner's
    # (``m^2`` is ``m²``) and takes the same row: one document prints both.
    for dim, owner in {"mass": "mass", "area": "area_sqft", "inertia": "inertia_slugft2",
                       "inertia_lbin2": "inertia_lbin2"}.items():
        ascii_label, owner_label = _EXTRA_DIMENSIONS[dim][2], HUMAN_SI[owner].label
        needed[ascii_label] = needed[owner_label] = max(needed[ascii_label], needed[owner_label])
    assert {"kg", "N·m", "m²", "m^2", "kg·m²", "kg*m^2", "kW", "kN/m²"} <= set(needed), sorted(needed)
    for label, decimals in needed.items():
        assert DELIVERED_PRECISION_SI[label] == decimals, (label, DELIVERED_PRECISION_SI[label], decimals)
    assert si_decimals("ft^2", HUMAN_SI["area_sqft"].factor) == 2      # 1 ft² = 0.093 m²: two decimals
    assert si_decimals("in^2", HUMAN_SI["area_sqin"].factor) == 4      # 1 in² = 6.5e-4 m²: the label's row
    assert si_decimals("lb-in^2", HUMAN_SI["inertia_lbin2"].factor) == 4
    assert si_decimals("in", HUMAN_SI["length_in"].factor) == 1        # 0.1 in = 2.54 mm: the row stays
    assert si_decimals("", 1.0) is None


@pytest.mark.parametrize("example", __import__("imperial_baseline").EXAMPLES)
def test_no_delivered_cell_is_in_exponent_form(example):
    """Every human channel of every example -- the CSVs, the text views, the
    case index -- prints no cell in exponent form inside the delivered window
    (D-65.2: below 1e-4 or at 1e9 and above the plain spelling would be worse,
    and the match is asserted to be there). Outside the scan: the solver
    channel (``sbeam/*``, D-65.8) and the gear report, which is written by
    ``deck_format.fmt`` in the solver's consistent units on purpose
    (``report/tables.py``, ``solver_units``) and is that channel's companion."""
    import imperial_baseline as baseline

    human = {k: v for k, v in baseline.artifacts(example).items()
             if not k.startswith("sbeam/") and k != "gear_report"}
    assert human, example
    exponent = re.compile(r"(?<![\w.])-?\d+\.?\d*[eE][+-]\d+")
    inside = {}
    for channel, text in human.items():
        bad = [m for m in exponent.findall(text) if 1e-4 <= abs(float(m)) < 1e9]
        if bad:
            inside[channel] = bad[:3]
    assert not inside, inside


@pytest.mark.parametrize("path", _REPORT_SOURCES, ids=os.path.basename)
def test_no_report_renderer_writes_a_digit_count_of_its_own(path):
    """D-65.7: precision is the unit's, read through ``format_value``. An
    f-string precision spec or a ``%.Nf`` format in ``sloads/report/`` fails
    unless its line (or the line above) states ``note 65 exempt`` and why --
    a TikZ coordinate, a LaTeX length, the solver channel's companion CSV."""
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    lines = source.splitlines()
    spec = re.compile(r"\.\d+[fFeEgG]")
    percent = re.compile(r"%[0-9]*\.\d+[feg]")

    def exempt(stmt):
        # The marker anywhere on the statement's own lines (an f-string's
        # FormattedValue reports the enclosing string's line on 3.10/3.11).
        return any("note 65 exempt" in lines[i - 1]
                   for i in range(stmt.lineno, (stmt.end_lineno or stmt.lineno) + 1))

    offenders = []
    for stmt in ast.walk(ast.parse(source)):
        if not isinstance(stmt, ast.stmt) or exempt(stmt):
            continue
        for node in ast.iter_child_nodes(stmt):
            for sub in ast.walk(node):
                if isinstance(sub, ast.stmt):
                    continue        # a nested statement is judged on its own lines
                if isinstance(sub, ast.FormattedValue) and sub.format_spec is not None:
                    text = "".join(v.value for v in sub.format_spec.values
                                   if isinstance(v, ast.Constant) and isinstance(v.value, str))
                    if spec.search(text):
                        offenders.append((sub.lineno, text))
                elif (isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.Mod)
                      and isinstance(sub.left, ast.Constant) and isinstance(sub.left.value, str)
                      and percent.search(sub.left.value)):
                    offenders.append((sub.lineno, sub.left.value))
    assert not offenders, f"{os.path.basename(path)}: {offenders} -- call format_value(value, units)"
