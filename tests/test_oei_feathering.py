"""Design note 74 (#405): the one-engine-out feather basis, the distinct
23.367(a)(2) decay and the speed sweep -- gates G-74.1 to G-74.7.

References: Torenbeek, *Synthesis of Subsonic Airplane Design* (1982), App. G-8.2
Eq. G-83 p554 (the feathered propeller); Lomax, *Structural Loads Analysis for
Commercial Transport Aircraft* (1996) §4.3 p42 (23.367(b)'s 2 s) and §9.3.1 p151
(the 0.02-0.10 s mechanical failure). G-74.6 is G-66.9, unchanged, in
``tests/test_engine_out_cases.py``.
"""

import math
import os
from dataclasses import replace

import pytest

from sloads import io
from sloads.constants import (
    CORRECTIVE_DELAY_S,
    IN_PER_FT,
    MECH_FAILURE_DECAY_TIME_S,
    OEI_SWEEP_POINTS,
)
from sloads.models import MissingInputError
from sloads.modules import one_engine_out as oeo
from sloads.validation import consistency_warnings

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_TWINS = ("atr42_100", "atr42_300_seed", "baron_58")


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _unfeathered(project):
    project.engines = [replace(e, feather_travel_time_s=None) for e in project.engines]
    return project


def _case(project, prefix, engine=0):
    return next(fc for fc in oeo.vtail_cases(project)
                if fc.load_case.label.startswith(prefix) and fc.engine_index == engine)


# --- G-74.1: the feathered drag is Torenbeek G-83 ---------------------------- #
@pytest.mark.parametrize("blades", [2, 3, 4, 6])
def test_g83_on_the_disc_is_the_drag_area(blades):
    """G-74.1: ``feathered_drag_cd(B) * pi D^2 / 4 == 0.00125 B D^2`` (p554)."""
    d = 13.0
    assert oeo.feathered_drag_cd(blades) * math.pi * d ** 2 / 4.0 == pytest.approx(
        0.00125 * blades * d ** 2, rel=1e-12)


def test_the_atr_feathered_drag_area_is_a_percent_of_the_bound():
    """G-74.1 on the ATR: four blades on a 156 in disc, 0.845 ft^2 of drag area,
    1.27 % of the Glauert bound's 66.6 ft^2."""
    eng = _project("atr42_100").engines[0]
    d_ft = eng.prop_diameter_in / IN_PER_FT
    area = oeo.feathered_drag_cd(eng.prop_blades) * math.pi * d_ft ** 2 / 4.0
    bound = oeo.GLAUERT_DISC_CD_BOUND * math.pi * d_ft ** 2 / 4.0
    assert area == pytest.approx(0.845, rel=1e-3)
    assert area / bound == pytest.approx(0.0127, rel=1e-2)


# --- G-74.2: no feather, no change ------------------------------------------- #
@pytest.mark.parametrize("name", _TWINS)
def test_the_march_is_the_held_drag_until_the_feather_starts(name):
    """G-74.2: up to 2 s the credited march is the uncredited one, row for row
    and bit for bit; the drag only leaves the held peak once the pilot acts."""
    credited = _case(_project(name), "VD")
    held = _case(_unfeathered(_project(name)), "VD")
    assert credited.inputs.v_kt == held.inputs.v_kt
    start = oeo.feather_start_s(credited.inputs)
    before = [(a, b) for a, b in zip(oeo.simulate(credited.inputs)[0],
                                     oeo.simulate(held.inputs)[0]) if a.time < start]
    assert before and all(a == b for a, b in before)


@pytest.mark.parametrize("name", _TWINS)
def test_the_mechanical_failure_takes_no_feather(name):
    """G-74.2 / D-74.5: the 23.367(a)(2) march is the same with the feather
    entered or not -- it is never credited."""
    a = _case(_project(name), "VC")
    b = _case(_unfeathered(_project(name)), "VC")
    assert a.inputs.feather_travel_s is None
    assert a.summary == b.summary
    assert oeo.FEATHER_ASSUMPTION not in a.statements


# --- G-74.3: the credited schedule ------------------------------------------- #
@pytest.mark.parametrize("name", _TWINS)
def test_the_drag_ramps_from_its_2s_value_to_g83(name):
    """G-74.3: the failed hub's drag is its 2 s value at 2 s, the G-83 drag at
    2 s + travel and after, and the march's moment carries the same ramp."""
    for prefix in ("VD", "VS"):
        c = _case(_project(name), prefix).inputs
        start, travel = oeo.feather_start_s(c), c.feather_travel_s
        assert start == CORRECTIVE_DELAY_S
        full = oeo.windmill_drag(c)
        g83 = oeo.feathered_drag(c)
        assert oeo.engine_forces_at(start, c)[2] == pytest.approx(
            oeo._build_up(start, c, full), rel=1e-12)
        assert oeo.engine_forces_at(start + travel, c)[2] == pytest.approx(g83, rel=1e-9)
        assert oeo.engine_forces_at(start + 3.0 * travel, c)[2] == pytest.approx(g83, rel=1e-9)
        mid = start + 0.5 * travel
        thrust, remaining, drag = oeo.engine_forces_at(mid, c)
        assert oeo._moment(mid, c, thrust * c.bleng, full * c.bleng, 0.0, 0.0) == pytest.approx(
            (thrust - remaining + drag) * c.bleng, rel=1e-12)


@pytest.mark.parametrize("name", _TWINS)
def test_the_feather_never_raises_the_fin_load_and_says_so(name):
    """G-74.3: the credited peak is no larger than the held one, and every
    credited case states the owner's assumption."""
    for prefix in ("VD", "VS"):
        credited = _case(_project(name), prefix)
        held = _case(_unfeathered(_project(name)), prefix)
        assert credited.summary.max_tail_load_lb <= held.summary.max_tail_load_lb
        assert oeo.FEATHER_ASSUMPTION in credited.statements
        assert oeo.FEATHER_ASSUMPTION not in held.statements
        title = credited.title
        note = next(c.note for c in oeo.run(_project(name)).conditions if c.title == title)
        assert oeo.FEATHER_ASSUMPTION in note


def test_the_atr_vd_feathered_drag():
    """G-74.3's ATR figure: at VD (q about 305 psf) the peak 20,319 lb comes
    down to the feathered 258 lb."""
    c = _case(_project("atr42_100"), "VD").inputs
    assert oeo.windmill_drag(c) == pytest.approx(20_319.0, rel=1e-3)
    assert oeo.feathered_drag(c) == pytest.approx(258.0, rel=5e-3)


def test_a_bad_feather_entry_is_refused_by_name():
    """D-74.3: a travel time that is not positive, or a feather with no blade
    count for G-83, is refused rather than run."""
    project = _project("atr42_100")
    project.engines = [replace(e, feather_travel_time_s=0.0) for e in project.engines]
    with pytest.raises(ValueError, match="feather_travel_time_s"):
        oeo.vtail_cases(project)
    project = _project("atr42_100")
    project.engines = [replace(e, prop_blades=0) for e in project.engines]
    with pytest.raises(MissingInputError, match="prop_blades"):
        oeo.vtail_cases(project)


# --- G-74.4: the distinct 23.367(a)(2) --------------------------------------- #
@pytest.mark.parametrize("name", _TWINS)
def test_the_mechanical_failure_decays_in_its_own_time(name):
    """G-74.4: the (a)(2) thrust is gone by 0.02 s (Lomax p151), marched at a
    step that resolves it; (a)(1) keeps the fuel-flow decay."""
    vc = _case(_project(name), "VC").inputs
    vd = _case(_project(name), "VD").inputs
    project = _project(name)
    assert vc.time2decay == MECH_FAILURE_DECAY_TIME_S
    assert vc.dt <= vc.time2decay / 2.0
    assert oeo.engine_forces_at(MECH_FAILURE_DECAY_TIME_S, vc)[1] == 0.0
    assert vd.time2decay == project.one_engine_out.thrust_decay_time_s
    assert vd.dt == project.one_engine_out.time_step_s


@pytest.mark.parametrize("name", _TWINS)
def test_the_mechanical_failure_converges_in_the_step(name):
    """G-74.4: halving the (a)(2) step moves its peak fin load by under 1 %."""
    c = _case(_project(name), "VC").inputs
    coarse = oeo.simulate(c)[1].max_tail_load_lb
    fine = oeo.simulate(replace(c, dt=c.dt / 2.0))[1].max_tail_load_lb
    assert fine == pytest.approx(coarse, rel=1e-2)


def test_a_bad_decay_is_refused_by_name():
    project = _project("atr42_100")
    project.one_engine_out = replace(project.one_engine_out, mech_failure_decay_time_s=0.0)
    with pytest.raises(ValueError, match="mech_failure_decay_time_s"):
        oeo.vtail_cases(project)


# --- G-74.5: the sweep ------------------------------------------------------- #
@pytest.mark.parametrize("name", _TWINS)
def test_the_sweep_delivers_the_largest_peak(name):
    """G-74.5: each swept case is marched at 11 speeds from the low end to its
    top, and the delivered speed's peak is at least the top end's. On every
    shipped twin today the top end governs, and the case says so."""
    project = _project(name)
    for fc in oeo.vtail_cases(project):
        speeds = oeo.sweep_speeds_kt(fc.load_case, project.one_engine_out)
        if fc.load_case.low_end:
            assert speeds == [fc.load_case.v_hi_kt] and fc.sweep_note == ""
            continue
        assert len(speeds) == OEI_SWEEP_POINTS
        assert speeds[0] == fc.load_case.v_lo_kt and speeds[-1] == fc.load_case.v_hi_kt
        top = oeo.simulate(replace(fc.inputs, v_kt=fc.load_case.v_hi_kt))[1]
        assert fc.summary.max_tail_load_lb >= top.max_tail_load_lb
        assert fc.inputs.v_kt == fc.load_case.v_hi_kt
        assert fc.sweep_note.endswith("the top end governs.")


def test_an_entered_speed_list_is_not_swept():
    project = _project("baron_58")
    project.one_engine_out = replace(project.one_engine_out, speeds_kt=[150.0])
    (fc, *_rest) = oeo.vtail_cases(project)
    assert fc.sweep_note == "" and fc.inputs.v_kt == 150.0


# --- G-74.7: the ATR re-derived ---------------------------------------------- #
@pytest.mark.parametrize("prefix, want, before", [
    ("VC", 13_245.0, 14_075.0),   # (a)(2): the abrupt decay lands the peak lower
    ("VD", 19_079.0, 19_568.0),   # (a)(1): the feather from 2 s
    ("VS", 6_278.0, 6_330.0),     # the low end: the feather from 2 s
])
def test_the_atr_fin_cases_re_derived(prefix, want, before):
    """G-74.7, measured 2026-11-02 (before: 2026-11-01, #420). The fin load
    peaks at 2.15-2.5 s on every twin, just after the feather starts, so the
    feather trims it rather than removing it. The (a)(2) case falls: the
    abrupt failure yaws the airplane early and it is already swinging back
    when the rudder goes in at 2 s."""
    fc = _case(_project("atr42_100"), prefix)
    assert fc.summary.max_tail_load_lb == pytest.approx(want, rel=1e-3)
    assert fc.summary.max_tail_load_lb < before


# --- Q1 (a): the bound is stated on a turboprop ------------------------------ #
def test_the_bound_is_warned_on_a_turboprop_with_its_ratios():
    """Q1 (a), review A-3: on the ATR the VD peak is 13.2 times the live
    engine's thrust and 11.2 times its rated power, and the warning says so;
    entering a coefficient silences it; the piston Baron is not warned."""
    def bound(project):
        return [w for w in consistency_warnings(project) if w.code == "windmill_drag_bound"]

    atr = bound(_project("atr42_100"))
    assert len(atr) == 2
    assert "13.22 times the live engine's thrust" in atr[0].message
    assert "11.24 times the engine's rated shaft power" in atr[0].message
    assert not bound(_project("baron_58"))
    entered = _project("atr42_100")
    entered.engines = [replace(e, windmill_drag_cd=0.25) for e in entered.engines]
    assert not bound(entered)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
