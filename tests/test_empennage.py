"""Single-source empennage geometry (Step G6).

The horizontal-/vertical-tail + elevator/rudder geometry is entered once on the
Geometry page and stored in ``GeometryInput.empennage`` (``htail``/``vtail`` = the
analysis-native ``TailLoadsInput``/``VTailLoadsInput``). ``Project.tail_loads`` /
``.vtail_loads`` are properties proxying to it, so the SELECT/TAILDIST/BALLOADS/
ONENGOUT calc reads it unchanged. These tests lock in the single-source mechanics
(property proxy, serialization, pre-v27 migration) and that the derived slices keep
the Appendix A SELECT tail loads **bit-for-bit** (the calc is untouched).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import (
    Project,
    TailLoadsInput,
    VTailLoadsInput,
    io,
)
from sloads.models import SCHEMA_VERSION
from sloads.modules.select import build_critical

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")


def test_tail_loads_property_proxies_to_empennage():
    p = Project(name="t")
    assert p.tail_loads is None and p.vtail_loads is None   # no geometry yet
    ti = TailLoadsInput(htail_area_sqft=36.0, xt25=261.0)
    p.tail_loads = ti
    # The single stored home is geometry.empennage.htail; the property reads it back.
    assert p.geometry is not None and p.geometry.empennage is not None
    assert p.geometry.empennage.htail is ti
    assert p.tail_loads is ti
    p.vtail_loads = VTailLoadsInput(vtail_area_sqft=14.0)
    assert p.geometry.empennage.vtail is p.vtail_loads
    # Clearing goes back through the proxy.
    p.tail_loads = None
    assert p.tail_loads is None and p.geometry.empennage.htail is None


def test_empennage_round_trips_through_io():
    p = io.load_project(_GA)
    ti, vt = p.tail_loads, p.vtail_loads
    assert ti is not None and vt is not None
    p2 = io.project_from_dict(io.project_to_dict(p))
    # Every native field survives, and it is stored under geometry.empennage (not top-level).
    assert p2.tail_loads == ti
    assert p2.vtail_loads == vt
    assert p2.geometry.empennage.htail is p2.tail_loads
    d = io.project_to_dict(p)
    assert "tail_loads" not in d and "vtail_loads" not in d      # no top-level keys
    assert "htail" in d["geometry"]["empennage"] and "vtail" in d["geometry"]["empennage"]


def test_the_tail_slice_properties_read_the_empennage():
    """``Project.tail_loads``/``.vtail_loads`` are views onto
    ``geometry.empennage``, not slices of their own -- which is what made the
    pre-v27 top-level blocks re-homeable. That hop went out with #93; the
    single-owner reading it established is what this pins.
    """
    d = {
        "schema_version": SCHEMA_VERSION,
        "name": "empennage-owned",
        "geometry": {"empennage": {
            "htail": {"htail_area_sqft": 36.944, "xt25": 261.027,
                      "htail_semispan_in": 73.1},
            "vtail": {"vtail_area_sqft": 14.84, "vtail_span_in": 57.0},
        }},
    }
    p = io.project_from_dict(d)
    assert p.geometry is not None and p.geometry.empennage is not None
    assert p.tail_loads is p.geometry.empennage.htail
    assert p.vtail_loads is p.geometry.empennage.vtail
    assert math.isclose(p.tail_loads.htail_area_sqft, 36.944)
    assert math.isclose(p.vtail_loads.vtail_span_in, 57.0)


def test_select_tail_loads_survive_round_trip_bit_for_bit():
    """The empennage-derived slices feed SELECT losslessly: the governing
    horizontal-tail loads are byte-identical before and after a JSON round-trip
    (the single-source move does not perturb the oracle-locked calc). The exact
    Appendix A values are asserted in test_select.py."""
    def htail_loads(pr):
        return {c.label: {v.label: v.value for v in c.loads}
                for c in build_critical(pr).conditions if c.component == "htail"}
    p = io.load_project(_GA)
    before = htail_loads(p)
    after = htail_loads(io.project_from_dict(io.project_to_dict(p)))
    assert before and before == after


# --------------------------------------------------------------------------- #
# The boundary-derived seam (note 54 D-54.1 / #25 step 1)
# --------------------------------------------------------------------------- #
def test_the_boundary_derived_marking_partitions_the_tail_blocks():
    """Rule 3's drift guard on the D-54.1 seam.

    Every field of the two tail input blocks sits on exactly one side:
    planform geometry the boundary-line model derives (named, with the surface
    whose lines derive it), or aero/control/mass data that stays entered. A
    field added to either block without declaring its side fails here, and the
    memberships are pinned so the seam cannot drift before step 2 consumes it.
    """
    import dataclasses

    from sloads.models.inputs import (
        HTAIL_BOUNDARY_DERIVED,
        VTAIL_BOUNDARY_DERIVED,
    )

    stays_entered = {
        TailLoadsInput: {
            "tail_incidence_deg", "wing_zero_lift_cruise_deg",
            "wing_zero_lift_enroute_deg", "wing_zero_lift_landing_deg",
            "elevator_effectiveness", "elevator_te_up_deg",
            "elevator_te_down_deg", "wing_lift_slope_per_rad",
        },
        VTailLoadsInput: {
            "rudder_deflection_deg", "gross_weight_lb",
            "rudder_large_deflection_factor", "izz_slugft2",
            # Placement, not planform: the L-1 owner's field.
            "vtail_root_waterline_z",
        },
    }
    derived = {TailLoadsInput: HTAIL_BOUNDARY_DERIVED,
               VTailLoadsInput: VTAIL_BOUNDARY_DERIVED}
    surfaces = {"wing", "htail", "vtail", "elevator", "rudder"}
    for cls in (TailLoadsInput, VTailLoadsInput):
        fields = {f.name for f in dataclasses.fields(cls)}
        marked, entered = set(derived[cls]), stays_entered[cls]
        assert marked | entered == fields, cls.__name__
        assert not (marked & entered), cls.__name__
        assert set(derived[cls].values()) <= surfaces, cls.__name__
    # The counts of record (note 54 D-54.1's 9-of-17 plus the wing span the
    # v-tail block also carries):
    assert len(HTAIL_BOUNDARY_DERIVED) == 9
    assert len(VTAIL_BOUNDARY_DERIVED) == 10


if __name__ == "__main__":
    test_tail_loads_property_proxies_to_empennage()
    print("ok property proxy")
    test_empennage_round_trips_through_io()
    print("ok io round-trip")
    test_pre_v27_top_level_tail_slices_migrate_to_empennage()
    print("ok pre-v27 migration")
    test_select_tail_loads_survive_round_trip_bit_for_bit()
    print("ok SELECT bit-for-bit")
    print("all empennage tests passed")
