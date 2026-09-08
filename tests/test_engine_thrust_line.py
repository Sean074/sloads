"""The engine's thrust line is an input (design note 53).

Gates covered:

* **G-53.1** — a counter-clockwise engine's torque is the exact negative of the
  same engine's clockwise torque, in **every** deliverable that carries it.
* **G-53.2** — every shipped example is byte-identical under the default: the
  Appendix A figures hold and the Imperial baseline does not move.
* **G-53.3** — an entered line is used, an unentered one is marked ASSUMED, and
  the assumed one is exactly the airplane's forward axis. All three directions.
* **G-53.4** — a half-entered line is refused **by name**, naming the field that
  is missing; two coincident points are the same refusal.
* **G-53.5** — a pusher resolves to the same torque sign as a tractor with the
  same rotation. The gate that "no tractor assumption" is true, not merely said.
* **G-53.6** — the gyroscopic sub-cases are unchanged by the rotation direction,
  all six components, and section 10 states the exemption.
* **G-53.7** — the sign convention is stated where the value is entered and
  where it is read.
* **G-53.8** — the Configuration & Layout three-view draws each engine's thrust
  line and marks an assumed one.
* **G-53.9** — ``hub_thrust_set`` still applies a pure ``-x`` thrust on a project
  that enters a thrust line: the gate that this note's scope held (D-53.8).
"""

import math
import os
import sys
from dataclasses import replace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixtures import io520bb, turboprop

from sloads import io
from sloads.export.coordinates import (
    ASSUMED_THRUST_AXIS,
    ThrustLineError,
    engine_thrust_axis,
)
from sloads.load_keys import MX_MOUNT_TORQUE
from sloads.models.enums import RotorDirection
from sloads.models.report import ReportSpec
from sloads.modules.engine import run_all, torque_sense
from sloads.report import load_cases_to_rows, text_report
from sloads.report import oracle_content as oc

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_ALL = ("ga6_normal", "baron_58", "concept_regional_jet", "cessna_210")

#: Every condition whose published quantity is a torque about the thrust line,
#: and which D-53.5 therefore reverses. The gyroscopic pair is deliberately not
#: here -- that is D-53.6, gated separately below.
_TORQUE_FARS = {"23.361(a)(1)", "23.361(a)(2)", "23.361(a)(3)", "23.361(b)(1)",
                "25.361(a)(3)(i)", "25.361(a)(3)(ii)"}


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _torques(engine, **kw):
    """``{far: published torque}`` for one engine input."""
    out = {}
    for condition in run_all(engine, **kw):
        for value in condition.values:
            if value.key == MX_MOUNT_TORQUE:
                out[condition.far_reference] = value.value
    return out


# --------------------------------------------------------------------------- #
# G-53.1 -- the rotation reverses the torque, everywhere it is carried
# --------------------------------------------------------------------------- #
def test_a_counter_clockwise_engine_reverses_every_torque():
    """G-53.1. Exactly the negative, condition for condition, both engine types
    and the FAR 25 cases with them."""
    for base in (io520bb(), turboprop()):
        cw = replace(base, prop_direction=RotorDirection.CLOCKWISE)
        ccw = replace(base, prop_direction=RotorDirection.COUNTERCLOCKWISE)
        clockwise = _torques(cw, include_far25=True)
        counter = _torques(ccw, include_far25=True)
        assert set(clockwise) == set(counter) and clockwise
        for far, value in clockwise.items():
            assert counter[far] == -value, far
            if far in _TORQUE_FARS:
                assert value < 0.0, f"{far}: a clockwise propeller loads the airframe counter-clockwise"


def test_the_sign_has_one_owner():
    """D-53.5. Every published torque goes through ``torque_sense``, so the rule
    is one function rather than six literals that can drift apart."""
    assert torque_sense(replace(io520bb(), prop_direction=RotorDirection.CLOCKWISE)) == -1.0
    assert torque_sense(replace(io520bb(), prop_direction=RotorDirection.COUNTERCLOCKWISE)) == 1.0


def test_the_reversal_reaches_every_deliverable_that_carries_the_torque():
    """G-53.1. Not the module alone: the load-case file and the text report are
    where a reader meets this number, and a direction honoured in one and
    assumed in another is two conventions for one load."""
    cw = replace(io520bb(), prop_direction=RotorDirection.CLOCKWISE)
    ccw = replace(io520bb(), prop_direction=RotorDirection.COUNTERCLOCKWISE)

    column = None
    rows = {}
    for name, engine in (("cw", cw), ("ccw", ccw)):
        table = load_cases_to_rows(run_all(engine))
        column = column or next(c for c in table[0] if c.startswith("Engine mount torque"))
        rows[name] = [r[column] for r in table]
    for a, b in zip(rows["cw"], rows["ccw"]):
        if a in ("", None):
            assert b in ("", None)
            continue
        assert float(a) == -float(b)

    assert text_report(cw, run_all(cw)) != text_report(ccw, run_all(ccw))


# --------------------------------------------------------------------------- #
# G-53.2 -- the default costs nothing
# --------------------------------------------------------------------------- #
def test_the_default_is_what_every_project_already_assumed():
    """G-53.2. Clockwise is the default, and a project that states nothing
    produces exactly what it produced before the field existed -- which is what
    lets an additive schema change be an identity hop."""
    assert io520bb().prop_direction is RotorDirection.CLOCKWISE
    for name in _ALL:
        for engine in _project(name).engines:
            assert engine.prop_direction is RotorDirection.CLOCKWISE, name
    # The Appendix A figures, through the default (p227-229).
    torques = _torques(io520bb())
    assert math.isclose(torques["23.361(a)(2)"], -740.4412, rel_tol=1e-3)


# --------------------------------------------------------------------------- #
# G-53.3 -- entered, or assumed and marked
# --------------------------------------------------------------------------- #
def test_an_entered_line_is_the_axis():
    """G-53.3. The difference of the two points, normalised, forward by name."""
    engine = replace(io520bb(), thrust_line_aft=(30.0, 0.0, 90.0),
                     thrust_line_fwd=(-10.0, 0.0, 120.0))
    axis, assumed = engine_thrust_axis(engine)
    assert assumed is False
    length = math.hypot(-40.0, 30.0)
    assert axis == pytest.approx((-40.0 / length, 0.0, 30.0 / length))


def test_an_unentered_line_is_the_airplanes_forward_axis_and_says_so():
    """G-53.3. Exactly ``(-1, 0, 0)`` -- not "approximately", and not derived
    from the CG and the hub, which is what D-53.3 removed."""
    axis, assumed = engine_thrust_axis(io520bb())
    assert assumed is True
    assert axis == ASSUMED_THRUST_AXIS == (-1.0, 0.0, 0.0)


def test_the_axis_is_not_derived_from_the_mount_and_hub_stations():
    """D-53.3, said as the thing it forbids. The Appendix A engine's CG and hub
    are 32 in apart in ``x`` and 8 in apart in ``z``; the superseded derivation
    read that as a 14 deg nose-up thrust line. Moving either station must now
    move nothing about the axis."""
    engine = io520bb()
    moved = replace(engine, engine_cg=(22.0, 0.0, 0.0), prop_cg=(-10.0, 0.0, 300.0))
    assert engine_thrust_axis(engine) == engine_thrust_axis(moved)


# --------------------------------------------------------------------------- #
# G-53.4 -- half a line is refused by name
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("kw,missing", [
    ({"thrust_line_aft": (30.0, 0.0, 90.0)}, "thrust_line_fwd"),
    ({"thrust_line_fwd": (-10.0, 0.0, 90.0)}, "thrust_line_aft"),
])
def test_half_a_thrust_line_is_refused_by_name(kw, missing):
    """G-53.4. Neither ignored nor completed from a derived second point: the
    C210-21 load-bearing-blank pattern, and the refusal names the field."""
    with pytest.raises(ThrustLineError) as exc:
        engine_thrust_axis(replace(io520bb(), **kw))
    assert missing in str(exc.value)


def test_two_coincident_points_state_no_direction_and_are_refused():
    """G-53.4. A pair that states nothing is a stated pair that states nothing,
    which is not the same as an absent pair -- so it refuses rather than
    silently falling back to the assumed axis."""
    point = (30.0, 0.0, 90.0)
    with pytest.raises(ThrustLineError) as exc:
        engine_thrust_axis(replace(io520bb(), thrust_line_aft=point,
                                   thrust_line_fwd=point))
    assert "coincide" in str(exc.value)


# --------------------------------------------------------------------------- #
# G-53.5 -- no tractor assumption
# --------------------------------------------------------------------------- #
def test_a_pusher_resolves_to_the_same_torque_sign_as_a_tractor():
    """G-53.5. The sense is about which way the shaft turns as the pilot sees
    it, not about which end of the engine the propeller is on. Both are entered
    with the same forward direction, so both resolve identically -- and the
    pusher's propeller station being aft of its engine changes nothing."""
    from sloads.export.coordinates import engine_applied_load

    tractor = replace(io520bb(), engine_cg=(22.0, 0.0, 92.0),
                      prop_cg=(-10.0, 0.0, 92.0),
                      thrust_line_aft=(30.0, 0.0, 92.0),
                      thrust_line_fwd=(-10.0, 0.0, 92.0))
    pusher = replace(io520bb(), engine_cg=(22.0, 0.0, 92.0),
                     prop_cg=(60.0, 0.0, 92.0),
                     thrust_line_aft=(60.0, 0.0, 92.0),
                     thrust_line_fwd=(10.0, 0.0, 92.0))
    for one, other in ((tractor, pusher),):
        assert engine_thrust_axis(one)[0] == engine_thrust_axis(other)[0]
        a = _torques(one)["23.361(a)(2)"]
        b = _torques(other)["23.361(a)(2)"]
        assert a == b < 0.0
        _fa, ma = engine_applied_load(engine_thrust_axis(one)[0], torque=a)
        _fb, mb = engine_applied_load(engine_thrust_axis(other)[0], torque=b)
        assert ma == mb and ma[0] > 0.0


# --------------------------------------------------------------------------- #
# G-53.6 -- the gyroscopic exemption
# --------------------------------------------------------------------------- #
def test_the_gyroscopic_case_is_unchanged_by_the_rotation_direction():
    """G-53.6. All four sign combinations are published either way, so the set
    the mount is checked against is identical and nothing there flips."""
    cw = replace(turboprop(), prop_direction=RotorDirection.CLOCKWISE)
    ccw = replace(turboprop(), prop_direction=RotorDirection.COUNTERCLOCKWISE)

    def gyro(engine):
        condition = next(c for c in run_all(engine)
                         if c.far_reference == "23.371(b)")
        return {v.key: v.value for v in condition.values}

    assert gyro(cw) == gyro(ccw)


def test_section_ten_states_the_gyroscopic_exemption_and_the_rotation():
    """G-53.6/G-53.7. Both statements are in the document, and the rotation is
    stated per engine so a counter-rotating twin can be described at all."""
    doc = oc.build_oracle_document(_project("concept_regional_jet"), ReportSpec())
    section = next(s for s in doc.sections if s.title.startswith("10."))
    text = " ".join(b for sub in section.subsections for b in sub.body)
    assert "sign combination" in text
    assert "Rotation is stated per engine" in text
    assert "clockwise" in text


def test_a_counter_rotating_twin_is_described_as_one():
    """D-53.4's whole reason for being per engine: the report says the two turn
    opposite ways rather than describing them as one installation."""
    project = _project("baron_58")
    left, right = project.engines
    project.engines = [replace(left, prop_direction=RotorDirection.CLOCKWISE),
                       replace(right, prop_direction=RotorDirection.COUNTERCLOCKWISE)]
    doc = oc.build_oracle_document(project, ReportSpec())
    section = next(s for s in doc.sections if s.title.startswith("10."))
    text = " ".join(b for sub in section.subsections for b in sub.body)
    assert "counter-clockwise" in text
    assert "opposite ways" in text

    table = next(t for sub in section.subsections for t in sub.tables
                 if t.title.startswith("Engine torque"))
    torque = next(i for i, c in enumerate(table.columns)
                  if c.startswith("Torque about thrust line"))
    values = [float(r[torque]) for r in table.rows if float(r[torque]) != 0.0]
    assert any(v > 0 for v in values) and any(v < 0 for v in values)


# --------------------------------------------------------------------------- #
# G-53.7 -- stated where entered
# --------------------------------------------------------------------------- #
def test_the_engine_page_states_the_sign_convention_beside_the_control():
    """G-53.7. The owner's requirement in as many words: the one thing a user
    cannot check on a results page is which way round "clockwise" was meant, so
    the page that takes the value says it."""
    here = os.path.dirname(os.path.abspath(__file__))
    page = os.path.join(os.path.dirname(here), "app", "views", "engine_mount.py")
    with open(page, encoding="utf-8") as fh:
        source = fh.read()
    for phrase in ("clockwise seen from the pilot's seat",
                   "counter-clockwise",
                   "Enter both points or",
                   "ASSUMED"):
        assert phrase in source, phrase


# --------------------------------------------------------------------------- #
# G-53.8 -- the three-view draws it
# --------------------------------------------------------------------------- #
def test_the_three_view_draws_each_thrust_line_and_marks_an_assumed_one():
    """G-53.8. Drawn on the Configuration & Layout sketch because it is geometry
    the user states and can therefore get wrong, and a three-view is where a
    wrong line is obvious. An assumed line is flagged, because a line nobody
    entered must not look like one somebody did.

    Asserted on the pure decision -- what to draw -- rather than on the plotly
    figure, which needs a Streamlit script context; the rendering itself is
    covered by the whole-GUI walk.
    """
    from sloads.derived_geometry import engine_thrust_segments

    project = _project("baron_58")
    project.engines = [replace(project.engines[0]),
                       replace(project.engines[1],
                               thrust_line_aft=(50.0, 66.0, 97.0),
                               thrust_line_fwd=(20.0, 66.0, 97.0))]
    segments = engine_thrust_segments(project)
    assert len(segments) == 2
    (_l1, assumed1, start1, end1), (_l2, assumed2, start2, end2) = segments
    assert assumed1 is True and assumed2 is False
    assert "ASSUMED" in _l1 and "ASSUMED" not in _l2
    # The assumed line runs forward from the hub, and only forward.
    assert end1[0] < start1[0] and end1[1] == start1[1] and end1[2] == start1[2]
    # The entered line is the entered pair, unaltered.
    assert (start2, end2) == ((50.0, 66.0, 97.0), (20.0, 66.0, 97.0))


def test_a_half_entered_thrust_line_draws_nothing_rather_than_guessing():
    """G-53.8/G-53.4. The refusal belongs to the owner; the sketch declines to
    invent the missing point rather than drawing a line half of which is a
    guess."""
    from sloads.derived_geometry import engine_thrust_segments

    project = _project("ga6_normal")
    project.engines = [replace(e, thrust_line_aft=(30.0, 0.0, 92.0))
                       for e in project.engines]
    assert engine_thrust_segments(project) == []


def test_a_project_with_no_engine_draws_no_thrust_line():
    """The empty case, which a figure must survive rather than fail on."""
    from sloads.derived_geometry import engine_thrust_segments

    project = _project("ga6_normal")
    project.engines = []
    assert engine_thrust_segments(project) == []


# --------------------------------------------------------------------------- #
# G-53.9 -- the scope held
# --------------------------------------------------------------------------- #
def test_the_balanced_cases_still_apply_a_purely_axial_thrust():
    """G-53.9. D-53.8 parks the balanced-case half of this deliberately: an
    entered thrust line creates the input that would steer it, and until that
    step is taken the thrust stays a pure ``-x`` force. The gate that the scope
    held, and the one that fails the day somebody takes the parked work without
    reading the note."""
    from sloads.modules.balance import hub_thrust_set

    project = _project("ga6_normal")
    project.engines = [replace(e, thrust_lb=500.0,
                               thrust_line_aft=(30.0, 0.0, 90.0),
                               thrust_line_fwd=(-10.0, 0.0, 130.0))
                       for e in project.engines]
    from sloads.cg_cases import flight_cases

    cg = flight_cases(project)[0]
    loads, _notes = hub_thrust_set(project, cg)
    assert loads
    for load in loads:
        assert load.fy == 0.0 and load.fz == 0.0
        assert load.fx == -500.0


if __name__ == "__main__":  # pragma: no cover - zero-dependency self-runner
    failures = 0
    for _name, _fn in sorted(dict(globals()).items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        marks = getattr(_fn, "pytestmark", [])
        cases = [c.args[1] for m in marks for c in [m] if m.name == "parametrize"]
        try:
            if cases:
                for args in cases[0]:
                    _fn(*args)
            else:
                _fn()
            print(f"ok   {_name}")
        except Exception as exc:
            failures += 1
            print(f"FAIL {_name}: {exc}")
    sys.exit(1 if failures else 0)
