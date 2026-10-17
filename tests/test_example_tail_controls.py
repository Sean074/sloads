"""Design note 69 D-69.17 / gate G-69.11: the elevator and rudder entered on
three examples, their SELECT scalars blank and derived.

``atr42_100``, ``baron_58`` and ``concept_regional_jet`` enter ``elevator`` and
``rudder`` surfaces with a ``hinge_line``, constructed to integrate to the
scalars the files used to type (``examples/*.sources.md``), and the six SELECT
scalars are blank. Two things follow and are held here:

* the **derived** scalars land on the former typed values within 0.1 % and the
  mismatch warnings stay silent;
* every tail load is the one the typed scalars produced, within 0.1 % -- the
  gate that found ``taildist.surface_geom`` reading the raw slice, which sized
  the ATR's elevator aft area at 0 the day its scalar went blank.
"""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io, registry
from sloads.modules.select import effective_tail_inputs, effective_vtail_inputs
from sloads.validation import consistency_warnings

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

#: The scalars each file typed until D-69.17 (both-sides SE halves, the fin's
#: SR halves), from its sources register.
FORMER = {
    "atr42_100": {"elevator_fwd_hinge_sqft": 3.0, "elevator_aft_hinge_sqft": 23.0,
                  "rudder_fwd_hinge_sqft": 2.5, "rudder_aft_hinge_sqft": 19.5},
    "baron_58": {"elevator_fwd_hinge_sqft": 2.1, "elevator_aft_hinge_sqft": 18.9,
                 "rudder_fwd_hinge_sqft": 0.9, "rudder_aft_hinge_sqft": 8.1},
    "concept_regional_jet": {"elevator_fwd_hinge_sqft": 4.0, "elevator_aft_hinge_sqft": 30.0,
                             "rudder_fwd_hinge_sqft": 4.0, "rudder_aft_hinge_sqft": 29.0},
}
_SCALARS = ("elevator_fwd_hinge_sqft", "elevator_aft_hinge_sqft", "elevator_area_sqft",
            "rudder_fwd_hinge_sqft", "rudder_aft_hinge_sqft", "rudder_area_sqft")
_TAIL_MODULES = ("select", "taildist", "tail_span", "balloads")


def _load(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _retyped(name):
    """The same project with the former scalars typed back in."""
    project = _load(name)
    ht, vt = project.geometry.empennage.htail, project.geometry.empennage.vtail
    former = FORMER[name]
    ht.elevator_fwd_hinge_sqft = former["elevator_fwd_hinge_sqft"]
    ht.elevator_aft_hinge_sqft = former["elevator_aft_hinge_sqft"]
    ht.elevator_area_sqft = former["elevator_fwd_hinge_sqft"] + former["elevator_aft_hinge_sqft"]
    vt.rudder_fwd_hinge_sqft = former["rudder_fwd_hinge_sqft"]
    vt.rudder_aft_hinge_sqft = former["rudder_aft_hinge_sqft"]
    vt.rudder_area_sqft = former["rudder_fwd_hinge_sqft"] + former["rudder_aft_hinge_sqft"]
    return project


def _tail_values(project):
    out = {}
    for module in _TAIL_MODULES:
        for cond in registry.get(module)(project).conditions:
            for v in cond.values:
                if isinstance(v.value, (int, float)) and not isinstance(v.value, bool):
                    out[(module, cond.title, v.label)] = float(v.value)
    return out


@pytest.mark.parametrize("name", sorted(FORMER))
def test_the_six_scalars_are_blank_and_derive_the_former_values(name):
    project = _load(name)
    ht, vt = project.geometry.empennage.htail, project.geometry.empennage.vtail
    for attr in _SCALARS:
        assert getattr(ht if attr.startswith("elevator") else vt, attr) == 0.0, attr
    for control in ("elevator", "rudder"):
        surface = project.geometry.by_name(control)
        assert surface is not None and len(surface.hinge_line) >= 2 and not surface.trailing_edge
    eti, evt = effective_tail_inputs(project), effective_vtail_inputs(project)
    former = FORMER[name]
    for attr, want in former.items():
        got = getattr(eti if attr.startswith("elevator") else evt, attr)
        assert math.isclose(got, want, rel_tol=1e-3), (attr, got, want)
    assert math.isclose(eti.elevator_area_sqft,
                        former["elevator_fwd_hinge_sqft"] + former["elevator_aft_hinge_sqft"], rel_tol=1e-3)
    assert math.isclose(evt.rudder_area_sqft,
                        former["rudder_fwd_hinge_sqft"] + former["rudder_aft_hinge_sqft"], rel_tol=1e-3)
    codes = {w.code for w in consistency_warnings(project)}
    assert not codes & {"elevator_area_mismatch", "rudder_area_mismatch"}


@pytest.mark.parametrize("name", sorted(FORMER))
def test_every_tail_load_is_the_typed_scalars_within_the_band(name):
    """G-69.11: SELECT, TAILDIST, the spanwise tail set and BALLOADS read the
    resolved scalars, so blanking them moves no tail load past the construction
    residual. A module that reads the raw slice fails this by a factor, not a
    percent."""
    derived, typed = _tail_values(_load(name)), _tail_values(_retyped(name))
    assert set(derived) == set(typed)
    apart = [(key, typed[key], derived[key]) for key in typed
             if not math.isclose(derived[key], typed[key], rel_tol=1e-3, abs_tol=1e-6)]
    assert not apart, apart[:10]


if __name__ == "__main__":                       # zero-dependency self-runner
    import traceback
    failures = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            for example in sorted(FORMER):
                try:
                    _fn(example)
                    print(f"PASS {_name}[{example}]")
                except Exception:
                    failures += 1
                    print(f"FAIL {_name}[{example}]")
                    traceback.print_exc()
    raise SystemExit(1 if failures else 0)
