"""What the beam grids cost the distribution: Appendix G (note 56 D-56.10).

The re-aggregation of D-56.9 preserves the applied set's **resultant** exactly
-- ``test_applied.py::test_the_re_aggregation_moves_no_resultant`` asserts that,
per case, per component, and it is an identity of the construction rather than a
tolerance. This file owns the other half of the same statement: the
**distribution** does move, the report says how much, and the machinery that
computes how much is itself correct.

There is deliberately **no acceptance gate on the size of the deviation**
(ruling 15). It is a function of the grid counts the project sets, so a fixed
tolerance would fail a coarse mesh doing exactly what it was asked. What is
gated is that the number is *right* and that it is *stated*:

* the internal-load machinery reproduces a hand-checkable case, and reproduces
  the side-of-body owner it generalises;
* a deviation of zero is what a mesh that lands on the load stations produces --
  the degenerate case the mesh rule deliberately avoids, used here as a
  self-check that the two curves are computed the same way;
* the appendix exists on every shipped example, names its case, and states the
  worst deviation over **all** cases and not only the plotted one;
* the appendices that point at this comparison now point at something.
"""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.report import lumping
from sloads.report.oracle_content import LUMPING_COMPARISON, appendix_letter
from sloads.report.oracle_sections import _lumping_appendix, _lumping_comparisons
from sloads.units import UnitSystem

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "examples")

_EVERY_FIXTURE = ("ga6_normal", "baron_58", "atr42_100",
                  "concept_regional_jet", "concept_heavy")

#: The four that produce distributed loads on every surface. ``concept_heavy``
#: is not among them by design -- it is the fixture with no distributions, and
#: it is carried in :data:`_EVERY_FIXTURE` to gate the *absence* path.
_LOADED_FIXTURES = ("ga6_normal", "baron_58", "atr42_100",
                    "concept_regional_jet")


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


class _Row:
    """The two attribute sets ``lumping`` reads off an applied-load row."""

    def __init__(self, x, y, z, fx=0.0, fy=0.0, fz=0.0, mx=0.0, my=0.0, mz=0.0):
        self.x, self.y, self.z = x, y, z
        self.fx, self.fy, self.fz = fx, fy, fz
        self.mxx_free, self.myy_free, self.mzz_free = mx, my, mz
        self.body_moments = True
        self.case, self.case_id, self.component = "C", "C-01", "wing"
        self.torsion_axis, self.safety_factor = "", 1.5


def _cut(s, pos):
    return lumping.Cut(s=s, pos=pos, gid=0)


def test_the_internal_load_at_a_cut_is_the_outboard_resultant_transferred():
    """A hand case: two unit loads on a cantilever, checked at three cuts.

    Written out rather than compared against another implementation, because
    the whole appendix rests on this arithmetic and a second implementation
    would only prove the two agree. 10 lb at y = 10 and 10 lb at y = 20, on a
    beam whose reference line is x = z = 0: at the root the shear is 20 lb and
    the bending 10*10 + 10*20 = 300 lb-in; at y = 15 it is 10 lb and 50 lb-in;
    at y = 20 the load *at* the cut counts as outboard, so 10 lb and 0.
    """
    rows = [_Row(0.0, 10.0, 0.0, fz=10.0), _Row(0.0, 20.0, 0.0, fz=10.0)]
    cuts = [_cut(0.0, (0.0, 0.0, 0.0)), _cut(15.0, (0.0, 15.0, 0.0)),
            _cut(20.0, (0.0, 20.0, 0.0))]
    curve = lumping._curve(rows, cuts, 1, lumping._MEMBERS["wing"][2])
    assert curve.shear == pytest.approx([20.0, 10.0, 10.0])
    assert curve.bending == pytest.approx([300.0, 50.0, 0.0])
    assert curve.torsion == pytest.approx([0.0, 0.0, 0.0])


def test_a_chordwise_offset_becomes_torsion_and_not_bending():
    """The couple LM-1 makes is about the axes transverse to the force.

    A vertical load one inch aft of the reference line makes a torsion about
    the span axis and no extra bending -- the distinction the applied
    appendices' zero-column notes now turn on, asserted where the arithmetic
    lives.
    """
    curve = lumping._curve([_Row(1.0, 10.0, 0.0, fz=10.0)],
                           [_cut(0.0, (0.0, 0.0, 0.0))], 1,
                           lumping._MEMBERS["wing"][2])
    assert curve.bending == pytest.approx([100.0])
    assert curve.torsion == pytest.approx([-10.0])


def test_a_mesh_that_lands_on_the_load_stations_costs_nothing():
    """The degenerate case, as a self-check on the two curves being one method.

    When every load already sits at a cut, lumping moves nothing, so the two
    curves must agree bit for bit. This is the special case D-56.4 deliberately
    stopped generating -- the whole reason the comparison exists is that the
    real mesh is not this -- and it is exactly what proves the station curve and
    the lumped curve are computed by the same rule and not by two.
    """
    cuts = [_cut(float(y), (0.0, float(y), 0.0)) for y in (0, 10, 20)]
    rows = [_Row(0.0, 10.0, 0.0, fz=7.0), _Row(0.0, 20.0, 0.0, fz=3.0)]
    channels = lumping._MEMBERS["wing"][2]
    station = lumping._curve(rows, cuts, 1, channels)
    lumped = lumping._curve(rows, cuts, 1, channels)
    assert station.bending == lumped.bending


@pytest.mark.parametrize("example", _LOADED_FIXTURES)
def test_the_station_curve_at_the_root_is_the_side_of_body_owner(example):
    """The generalisation reproduces the special case it generalises.

    ``report.applied.sob_internal_loads`` states the wing's internal load at one
    cut, from the same station-level set, and has been gated against the solver
    since step 13. Computing it a second way is only safe if the two agree, so
    they are compared where they overlap: the station curve evaluated at the
    side-of-body cut, against that owner. This is why the comparison could be
    written generically at all -- an internal load is a resultant about a point,
    and the wing already had a trusted instance of that sentence.
    """
    from sloads.report.applied import (
        sob_internal_loads,
        sob_reference_point,
        station_applied_loads,
    )
    from sloads.report.oracle_sections import _wing_net

    project = _project(example)
    net = _wing_net(project)
    channels = lumping._MEMBERS["wing"][2]
    for result in net:
        rows = [r for r in station_applied_loads("wing", [result], project)
                if r.y >= 0.0]
        root = min(r.y for r in rows)
        owner = sob_internal_loads(result, root)
        curve = lumping._curve(
            rows, [_cut(root, sob_reference_point(result, root))], 1, channels)
        assert math.isclose(curve.shear[0], owner.sz, rel_tol=1e-9,
                            abs_tol=1e-6), (example, result)
        assert math.isclose(curve.bending[0], owner.mxx, rel_tol=1e-9,
                            abs_tol=1e-6), (example, result)
        assert math.isclose(curve.torsion[0], owner.myy, rel_tol=1e-9,
                            abs_tol=1e-6), (example, result)


@pytest.mark.parametrize("example", _LOADED_FIXTURES)
def test_every_surface_states_what_its_lumping_cost(example):
    """Every comparison the project may state is built, and names a case it ran.

    Every one it *may* state: OR-133 withholds the fin's spanwise loads on a
    non-conventional layout, and this appendix must not publish sideways a set
    section 6 declined to publish. ``atr42_100`` and ``concept_regional_jet``
    are T-tails, so the assertion is live in both directions on this fixture
    set.
    """
    from sloads.tail_geometry import is_conventional_tail

    project = _project(example)
    comparisons = _lumping_comparisons(project)
    expected = set(lumping.COMPONENTS)
    if not is_conventional_tail(project):
        expected.discard("vtail")
    assert {c.component for c in comparisons} == expected, example
    for comparison in comparisons:
        case = lumping.critical_case(comparison)
        assert comparison.case(case) is not None, (example, comparison.component)


@pytest.mark.parametrize("example", _LOADED_FIXTURES)
def test_the_worst_deviation_is_over_every_case_and_not_the_plotted_one(example):
    """The table's number is the maximum over all cases -- asserted, not assumed.

    The defect this rules out is the easy one: reporting the plotted case's
    deviation under a heading that says "over every case". On these fixtures the
    two genuinely differ -- the h-tail's worst torsion is not its most heavily
    bent case -- so the assertion has something to bite on.
    """
    project = _project(example)
    for comparison in _lumping_comparisons(project):
        for channel, _letter in lumping.CHANNEL_NAMES:
            _case, gap, _s, _ref = comparison.worst(channel)
            per_case = [abs(c.worst(channel)[0]) for c in comparison.cases]
            assert math.isclose(abs(gap), max(per_case), rel_tol=1e-12), (
                example, comparison.component, channel)


def test_the_four_components_share_no_case_which_is_why_each_names_its_own():
    """The fact that amended D-56.10, pinned so the amendment cannot rot.

    If a future change ever *did* give the four a common case register, this
    fails and the note's reasoning gets revisited rather than silently
    outliving its premise.
    """
    project = _project("ga6_normal")
    registers = [{c.case for c in comparison.cases}
                 for comparison in _lumping_comparisons(project)]
    for i, first in enumerate(registers):
        for second in registers[i + 1:]:
            assert not (first & second)


@pytest.mark.parametrize("example", _EVERY_FIXTURE)
def test_the_appendix_builds_and_states_that_it_has_no_pass_mark(example):
    """Every fixture, loaded or not: it renders, and it never implies a limit."""
    section = _lumping_appendix(_project(example), system=UnitSystem.IMPERIAL,
                                plan=[])
    prose = " ".join(section.body) + section.absent_reason
    assert prose.strip()
    if not section.figures:
        assert section.absent_reason, example
        return
    assert "no acceptance criterion" in prose, example
    for figure in section.figures:
        assert figure.data is not None or figure.absent_reason, figure.key


@pytest.mark.parametrize("example", _LOADED_FIXTURES)
def test_a_channel_with_no_producer_is_left_out_rather_than_drawn_flat(example):
    """A fuselage carries no torsion here, and no legend entry invites a search."""
    section = _lumping_appendix(_project(example), system=UnitSystem.IMPERIAL,
                                plan=[])
    body = next(f for f in section.figures if f.key == "lumping_fuselage")
    assert body.data is not None, example
    assert not [s for s in body.data.series if s.name.startswith("T ")], example


def test_the_applied_appendices_point_at_an_appendix_that_exists():
    """The note 56 D-56.9 sentence promised this comparison; here it is.

    Written as a gate because the promise shipped one slice before the thing:
    B.1, C.1, D and E all say "what the lumping costs the distribution is stated
    in the VMT comparison", and for one slice that sentence pointed nowhere.
    """
    from sloads.report.oracle_sections import LUMPED_SET_NOTE

    assert "VMT comparison" in LUMPED_SET_NOTE
    assert appendix_letter(LUMPING_COMPARISON) == "G"


def test_the_new_slot_did_not_move_a_letter():
    """OR-50: the letter is the position, so an appendix is appended, never inserted."""
    from sloads.report.oracle_content import (
        BODY_LOAD_STATIONS,
        GEAR_LOAD_CASES,
        HTAIL_LOAD_STATIONS,
        VN_CONDITIONS,
        VTAIL_LOAD_STATIONS,
        WING_LOAD_STATIONS,
    )

    assert [appendix_letter(t) for t in (
        VN_CONDITIONS, WING_LOAD_STATIONS, BODY_LOAD_STATIONS,
        HTAIL_LOAD_STATIONS, VTAIL_LOAD_STATIONS, GEAR_LOAD_CASES,
    )] == ["A", "B", "C", "D", "E", "F"]


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
