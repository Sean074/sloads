"""The applied-load appendices, as one deck in one frame (note 44 §18).

Appendices B.1, C.1, D and E give the same thing: the case, the point the load
acts at, all six body-axis components and the factor. This file owns what is
true of all four at once. What is true of one -- Appendix E's withholding,
Appendix B's concentrated masses -- stays in that section's own file.

The gate that matters most here is **G-OR-90**: an appendix row and the card the
deck writes for that grid are the same load. Everything else in §18 follows a
format ruling; that one is a defect gate. Until 2026-09-07 the tail appendices
printed the strip normal force and nothing else, while the deck wrote a MOMENT
card for the strip torsion and folded the fin's span-axis axial into the FORCE
card -- 232,139 lb-in of applied torsion missing from one appendix of one
example, under a sentence saying the row and the card were the same load.

Gates covered:

* **G-OR-89** -- one column set, in one order, across all four appendices.
* **G-OR-90** -- every row is the deck's card for that GID: same components,
  same sign, same point.
* **G-OR-91** -- the fin's torsion is Mz and negated; the h-tail's is My.
* **G-OR-92** -- a column printed as zero is named in the note; a component
  that is non-zero anywhere is not describable as absent.
* **G-OR-93** -- Appendix C is two lettered subsections sharing no load column.
* **G-OR-94** -- no ``Myy`` heading in section 6 or Appendix E, no ``Mzz`` in
  section 5 or Appendix D.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from sloads import io  # noqa: E402
from sloads.export import sbeam_bridge as sb  # noqa: E402
from sloads.field_registry import reduce_to_oracle_inputs  # noqa: E402
from sloads.models.report import ReportSpec  # noqa: E402
from sloads.report import oracle_content as oc  # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = os.path.join(_ROOT, "examples")
#: The three the report is shipped against. `concept_regional_jet` is here for a
#: reason and not for coverage: it is the T-tail, so it is the only one of the
#: three that exercises the transfer node and the largest applied torsion in the
#: suite (232,139 lb-in on the h-tail).
_SHIPPED = ("ga6_normal", "baron_58", "concept_regional_jet")

#: OR-139's column set, in order. One list, because the ruling is that there is
#: one -- a per-appendix copy of this would be the drift the gate exists to stop.
APPLIED_COLUMNS = ["Case", "Station", "GID", "X", "Y", "Z",
                   "Fx", "Fy", "Fz", "Mx", "My", "Mz", "SF"]


def _spec():
    return ReportSpec(title="FAR 23 Structural Design Loads",
                      report_number="LR-0142", revision="B",
                      abstract="An abstract.")


def _project(name):
    return reduce_to_oracle_inputs(
        io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json")))


def _doc(name):
    return oc.build_oracle_document(_project(name), _spec())


def _flat(sections):
    for section in sections:
        yield section
        yield from _flat(section.subsections)


def _applied_tables(doc):
    """Every applied-load appendix table of ``doc``, by its title."""
    return {t.title: t for s in _flat(doc.sections) for t in s.tables
            if t.title.startswith("Applied ") and " by station" in t.title}


# --------------------------------------------------------------------------- #
# G-OR-89 -- one column set
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", _SHIPPED)
def test_every_applied_appendix_prints_the_same_columns(name):
    """OR-139. A reader who has learnt one applied appendix has learnt all four.

    Both directions: every applied table has exactly these headings in this
    order, and there are as many applied tables as the airplane has components
    with loads -- so an appendix cannot satisfy the gate by not existing.
    """
    tables = _applied_tables(_doc(name))
    assert tables, name
    for title, table in tables.items():
        got = [c.split(" (")[0] for c in table.columns]
        assert got == APPLIED_COLUMNS, (name, title, got)
        assert table.rows, (name, title)


def test_all_four_components_reach_the_document():
    """The wing, the fuselage and both tails, on the airplane that has them."""
    titles = set(_applied_tables(_doc("ga6_normal")))
    assert titles == {
        "Applied wing loads by station (LIMIT)",
        "Applied fuselage loads by station (LIMIT)",
        "Applied horizontal tail loads by station (LIMIT)",
        "Applied vertical tail loads by station (LIMIT)",
    }, sorted(titles)


# --------------------------------------------------------------------------- #
# G-OR-90 -- the row and the card are the same load
# --------------------------------------------------------------------------- #
def _cards(text):
    """``{(kind, sid, gid): (c1, c2, c3)}`` from a FORCE/MOMENT deck.

    Components are **summed**, not replaced. A grid can legitimately carry two
    cards of one kind in one subcase -- on a T-tail the fin's tip node takes
    both the last strip and the transferred horizontal-tail load -- and a
    solver superposes them. Overwriting drops one of the two, which reads as
    the appendix carrying a load the deck does not.
    """
    out = {}
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if parts and parts[0] in ("FORCE", "MOMENT"):
            key = (parts[0], int(parts[1]), int(parts[2]))
            values = tuple(float(v) for v in parts[5:8])
            prev = out.get(key, (0.0, 0.0, 0.0))
            out[key] = tuple(a + b for a, b in zip(prev, values))
    return out


@pytest.mark.parametrize("name", _SHIPPED)
@pytest.mark.parametrize("component", ("htail", "vtail"))
def test_every_tail_appendix_row_is_the_card_the_deck_writes(name, component):
    """G-OR-90, the half that failed. Row for card, component for component.

    The deck is the authority: it is what a solver is actually given. Any load
    it emits at a grid and the appendix does not print at that grid is a load a
    reader building a model from the appendix leaves out, under a sentence
    saying the two are the same. That is what this asserts, in the direction
    that catches it -- every card is found, not merely every row is valid.
    """
    from sloads.modules.tail_span import build_tail_span

    project = _project(name)
    results = build_tail_span(project).get(component, [])
    if not results:
        pytest.skip(f"{name} has no {component} spanwise loads")

    seen = total_rows = 0
    # One case at a time: a GID repeats in every case's block, so a deck read
    # whole would compare one grid's card against the sum of its rows in every
    # condition -- which passes for a single-case airplane and hides everything
    # else. The case is the unit the deck itself is written in (one SID each).
    for result in results:
        rows = sb.applied_loads(component, [result])
        assert rows, (name, component, result.case)
        total_rows += len(rows)
        deck = _cards(sb.tail_span_force_moment_cards([result], component))
        assert deck, (name, component, result.case)
        by_gid = {}
        for row in rows:
            forces = (row.fx, row.fy, row.fz)
            moments = sb.applied_body_moments(row)
            prev = by_gid.get(row.gid, ((0.0,) * 3, (0.0,) * 3))
            by_gid[row.gid] = (tuple(a + b for a, b in zip(prev[0], forces)),
                               tuple(a + b for a, b in zip(prev[1], moments)))
        for (kind, _sid, gid), card in deck.items():
            if gid not in by_gid:
                continue      # a chord-station or control grid this set omits
            want = by_gid[gid][0 if kind == "FORCE" else 1]
            scale = max(max(abs(v) for v in card), 1.0)
            for got, expected in zip(card, want):
                assert math.isclose(got, expected, rel_tol=1e-5,
                                    abs_tol=1e-5 * scale), (
                    name, component, result.case, kind, gid, card, want)
            seen += 1
    # Every row is a card and then some: a strip contributes a FORCE and, where
    # its torsion is non-zero, a MOMENT, so the matched-card count is at least
    # the row count. A number below it means rows the deck does not write --
    # or, as before 2026-09-07, cards the appendix does not carry.
    assert seen >= total_rows, (
        f"{name} {component}: {seen} cards matched against {total_rows} applied "
        "rows -- the appendix is not the deck")


@pytest.mark.parametrize("name", _SHIPPED)
def test_the_tail_appendices_carry_the_torsion_the_deck_emits(name):
    """The specific defect, pinned with the specific number (OR-143).

    An assertion that the applied torsion column is non-zero somewhere. The
    appendices printed one force column and no moment at all until 2026-09-07;
    this fails outright against that document rather than merely differing from
    it, which is what a defect gate has to do.
    """
    from sloads.modules.tail_span import build_tail_span

    spans = build_tail_span(_project(name))
    for component in ("htail", "vtail"):
        if not spans.get(component):
            continue
        rows = sb.applied_loads(component, spans[component])
        torsion = math.fsum(abs(sb.applied_body_moments(r)[2 if component == "vtail" else 1])
                            for r in rows)
        assert torsion > 1.0, (name, component, torsion)
    # ...and the fin's span-axis axial, the other half of what was missing: a
    # fin's span is vertical, so its own mass under vertical acceleration is an
    # axial column load, which Appendix E called absent by construction.
    if spans.get("vtail"):
        axial = math.fsum(abs(r.fz)
                          for r in sb.applied_loads("vtail", spans["vtail"]))
        assert axial > 1.0, (name, axial)


# --------------------------------------------------------------------------- #
# G-OR-91 -- the torsion is on the surface's own span axis
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", _SHIPPED)
def test_the_fin_torsion_is_mz_and_the_htail_torsion_is_my(name):
    """OR-142. A surface's torsion is about its span axis, and a fin spans z.

    Asserted through ``applied_body_moments`` rather than on a column, so a
    component added later cannot inherit the wing's map by defaulting into it.
    The fin's ``My`` is not merely unused: a lateral load can make no moment
    about the y axis at all, so a non-zero one there is a wrong axis, never a
    small term.
    """
    from sloads.modules.tail_span import build_tail_span

    spans = build_tail_span(_project(name))
    for component, (zero, carries), sign in (
            ("htail", (2, 1), +1), ("vtail", (1, 2), -1)):
        if not spans.get(component):
            continue
        for row in sb.applied_loads(component, spans[component]):
            if row.body_moments:
                continue      # the T-tail transfer: the h-tail's axis, on the fin
            moments = sb.applied_body_moments(row)
            assert moments[0] == 0.0, (name, component, "Mx", moments)
            assert moments[zero] == 0.0, (name, component, "wrong axis", moments)
            assert math.isclose(moments[carries], sign * row.myy_free,
                                rel_tol=1e-12, abs_tol=1e-9), (
                name, component, moments, row.myy_free)


# --------------------------------------------------------------------------- #
# G-OR-92 -- a zero column is named, and an absence has to be true
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", _SHIPPED)
def test_no_applied_appendix_calls_a_live_component_absent(name):
    """OR-140's other half, and the sentence that made OR-143 hard to see.

    Appendix E stated that the two components beside its normal load were "not
    zero by measurement but absent by construction". One of them was the fin's
    axial, which the deck had been emitting all along. A note may say a column
    is zero only where the column is zero.
    """
    doc = _doc(name)
    for title, table in _applied_tables(doc).items():
        note = table.note or ""
        assert "absent by construction" not in note, (name, title)
        columns = {c.split(" (")[0]: i for i, c in enumerate(table.columns)}
        for symbol in ("Fx", "Fy", "Fz", "Mx", "My", "Mz"):
            values = [float(r[columns[symbol]].replace(",", ""))
                      for r in table.rows]
            live = any(v != 0.0 for v in values)
            claimed_zero = f"{symbol} " in note and "zero" in note
            if live:
                assert not (claimed_zero and f"{symbol} is zero" in note), (
                    name, title, symbol, "printed non-zero but called zero")


@pytest.mark.parametrize("name", _SHIPPED)
def test_every_applied_appendix_says_why_its_zero_columns_are_zero(name):
    """A zero column without a reason is a measured zero to the reader (OR-61).

    OR-140 keeps the column and moves the remedy into the note, so the note has
    to carry it: every appendix that prints an all-zero column names that
    column in its own note.
    """
    for title, table in _applied_tables(_doc(name)).items():
        note = table.note or ""
        columns = {c.split(" (")[0]: i for i, c in enumerate(table.columns)}
        for symbol in ("Fx", "Fy", "Fz", "Mx", "My", "Mz"):
            values = [float(r[columns[symbol]].replace(",", ""))
                      for r in table.rows]
            if all(v == 0.0 for v in values):
                assert symbol in note, (name, title, symbol,
                                        "an all-zero column with no reason")


# --------------------------------------------------------------------------- #
# G-OR-93 / G-OR-94
# --------------------------------------------------------------------------- #
def test_appendix_c_is_two_subsections_sharing_no_load_column():
    """OR-144, on OR-59's reasoning: applied and carried are not one table."""
    doc = _doc("ga6_normal")
    appendix = next(s for s in doc.sections
                    if s.title == oc.appendix_heading(oc.BODY_LOAD_STATIONS))
    titles = [s.title for s in appendix.subsections]
    assert titles == ["C.1 Applied loads", "C.2 Cumulative loads"], titles
    applied, carried = (s.tables[0] for s in appendix.subsections)
    loads = {"Fx", "Fy", "Fz", "Mx", "My", "Mz", "Sz", "Myy", "Sx", "Mxx", "Mzz"}
    a = {c.split(" (")[0] for c in applied.columns} & loads
    b = {c.split(" (")[0] for c in carried.columns} & loads
    assert a and b and not (a & b), (sorted(a), sorted(b))


@pytest.mark.parametrize("name", _SHIPPED)
def test_neither_tail_prints_the_others_torsion_symbol(name):
    """OR-146. The beam-frame symbol follows the surface's span axis.

    Section 6.5 printed ``Myy`` for the fin -- the letter of a component whose
    body-axis value is identically zero -- while section 3.2 maps the beam
    symbols onto body axes two chapters earlier. Both directions, both
    sections, so neither can drift back to the other's letter.
    """
    doc = _doc(name)
    for number, banned, wanted in (("5", "Mzz", "Myy"), ("6", "Myy", "Mzz")):
        section = next((s for s in doc.sections if s.title.startswith(f"{number}. ")),
                       None)
        if section is None:
            continue
        headings = [c.split(" (")[0]
                    for s in _flat([section]) for t in s.tables for c in t.columns]
        symbols = [r[0] for s in _flat([section]) for t in s.tables
                   if t.title == "Notation for the spanwise loads" for r in t.rows]
        assert banned not in headings + symbols, (name, number, banned)
        if any(h.startswith("Root ") for h in headings):
            assert wanted in headings + symbols, (name, number, wanted)


if __name__ == "__main__":       # zero-dependency self-runner
    failures = 0
    for _name, _fn in sorted(globals().items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        marks = getattr(_fn, "pytestmark", [])
        argsets = [()]
        for mark in marks:
            if mark.name == "parametrize":
                argsets = [a if isinstance(a, tuple) else (a,)
                           for a in mark.args[1]]
        for _args in argsets:
            try:
                _fn(*_args)
            except Exception as exc:                     # noqa: BLE001
                failures += 1
                print(f"FAIL {_name}{_args}: {exc}")
    print("ok" if not failures else f"{failures} failure(s)")
    sys.exit(1 if failures else 0)
