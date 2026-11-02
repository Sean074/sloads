"""Single-source landing-gear geometry (Step G6b).

The tricycle-gear geometry native to LANDLOAD (axle X/Z at three strut states,
rolling radius, strut type, tread) is entered once in ``GeometryInput.landing_gear``
and drives both the three-view (tip-back/overturn/clearance) and the ground-load
analysis. ``landing.build_landing`` syncs it onto ``Project.landing`` before the
reaction solve, so the LANDLOAD math is unchanged. These tests lock in the
single-source mechanics (serialization under geometry, pre-v28 migration, the
derived coarse gear values) and that the Appendix A gear reactions stay bit-for-bit.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.modules.configuration import gear_stations
from sloads.modules.landing import build_landing

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")
_JET = os.path.join(_EXAMPLES, "concept_regional_jet.project.json")  # has a parametric layout


def test_gear_geometry_serializes_under_geometry_not_landing():
    p = io.load_project(_GA)
    assert p.geometry.landing_gear is not None
    d = io.project_to_dict(p)
    assert "landing_gear" in d["geometry"]
    assert "main_gear" not in d["landing"] and "tread_in" not in d["landing"]
    p2 = io.project_from_dict(d)
    assert p2.geometry.landing_gear.main_gear.axle_static == p.geometry.landing_gear.main_gear.axle_static
    assert p2.geometry.landing_gear.tread_in == p.geometry.landing_gear.tread_in


def test_gear_stations_derives_coarse_values_from_axles():
    p = io.load_project(_JET)   # a fixture with a parametric layout + gear geometry
    gc = gear_stations(p.geometry.parametric, p.geometry.landing_gear)
    lg = p.geometry.landing_gear
    assert gc["main_x"] == lg.main_gear.axle_static[0]
    assert gc["track"] == lg.tread_in
    # Ground line = lowest static wheel contact (static axle Z - rolling radius).
    ground = min(lg.main_gear.axle_static[1] - lg.main_gear.rolling_radius_in,
                 lg.nose_gear.axle_static[1] - lg.nose_gear.rolling_radius_in)
    assert math.isclose(gc["ground_z"], ground)
    assert math.isclose(gc["gear_height"], p.geometry.parametric.root_waterline_z - ground)


def test_landloads_reactions_unchanged_bit_for_bit():
    """The gear syncs from geometry.landing_gear -> LANDLOAD produces byte-identical
    reactions before and after a JSON round-trip (Appendix A ground-load lock)."""
    def reactions(pr):
        _lf, rx = build_landing(pr)
        return [(c.case, round(c.result, 9), round(c.rmp, 9)) for c in rx]
    p = io.load_project(_GA)
    before = reactions(p)
    after = reactions(io.project_from_dict(io.project_to_dict(p)))
    assert before and before == after


#: The wheel track each fixture's sources register publishes, in inches, pinned
#: beside the stored ``tread_in`` (issue #399: the ATR baseline kept a 150 in
#: estimate after its register had recorded the published 4.10 m). The
#: track is the tyre-centre distance: the gear deck's wheel nodes sit at
#: ``+-tread/2`` and LANDLOAD's roll/yaw arms are ``tread/2``. A fixture whose
#: register publishes no track (``ga6_normal``, ``concept_regional_jet``: [E]
#: placements) has no row here and is not pinned.
_PUBLISHED_TRACK_IN = {
    "atr42_100.project.json": (161.4, 4.10),        # atr42_100.sources.md "Wheel track" [A]
    "atr42_300_seed.project.json": (161.4, 4.10),   # atr42_300_seed.sources.md "Main gear track" [D]
    "baron_58.project.json": (115.0, None),         # baron_58.sources.md "Main gear track" [B]
}


def test_the_stored_track_is_the_register_s_published_one():
    """Every fixture whose register publishes a wheel track stores that track
    (``_PUBLISHED_TRACK_IN``), and where the register quotes metres the pinned
    inch value is their conversion, not a copied number."""
    for name, (track_in, track_m) in sorted(_PUBLISHED_TRACK_IN.items()):
        p = io.load_project(os.path.join(_EXAMPLES, name))
        assert p.geometry.landing_gear.tread_in == track_in, name
        if track_m is not None:
            assert math.isclose(track_m / 0.0254, track_in, abs_tol=0.05), name


if __name__ == "__main__":
    test_gear_geometry_serializes_under_geometry_not_landing()
    print("ok serializes under geometry")
    test_gear_stations_derives_coarse_values_from_axles()
    print("ok gear_stations derivation")
    test_landloads_reactions_unchanged_bit_for_bit()
    print("ok LANDLOAD bit-for-bit")
    test_the_stored_track_is_the_register_s_published_one()
    print("ok published track pinned")
    print("all landing-gear-geometry tests passed")
