"""Net fuselage loads (Step C6, R6): the Ch 15 body distribution as two cantilevers.

Ch 15 ("Net Fuselage Loads") ships no program and no printed station table, so
the fuselage net distribution is a modern calc validated by **equilibrium
closure** (design note 64 gate 4): the wing reacts the body at one station --
force and couple, what the beam model's wing post carries (D-64.5) -- the
forward body is integrated nose -> front spar and the aft body tail -> rear spar
(D-64.2), shear and bending positive for an up load in either body (D-64.4),
and the two terminals, the box's applied rows and the reaction sum to zero
force and zero moment. The spar fitting pair is the static equivalent of the one
reaction (gate 6). A project that cannot place the wing post is refused by name
(§8 ruling 1) -- the whole-body "closure artifact" fallback is gone.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from sloads import io
from sloads.derived_geometry import carry_through
from sloads.joints import wing_station
from sloads.models import FuselageMassInput, FuselageStation, MissingInputError, TailLoadsInput
from sloads.modules import body_loads
from sloads.report import applied

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")


def _project():
    p = io.load_project(_GA)  # the Appendix A altitude set is the fixture's own since #164
    p.fuselage_mass = FuselageMassInput(stations=[
        FuselageStation(x=x, weight_lb=w) for x, w in
        [(30, 200), (60, 400), (90, 600), (140, 500), (200, 300), (250, 150)]
    ])
    p.tail_loads = TailLoadsInput(xt25=261.027)
    return p


def _with_spars(front: float, rear: float):
    """The fixture with its spar stations entered as given."""
    from dataclasses import replace

    p = _project()
    p.geometry.surfaces = [
        replace(s, front_spar_x_in=front, rear_spar_x_in=rear) if s.name == "wing" else s
        for s in p.geometry.surfaces
    ]
    return p


def _regions(r):
    fwd = [s for s in r.stations if s.region == body_loads.FORWARD]
    box = [s for s in r.stations if s.region == body_loads.BOX]
    aft = [s for s in r.stations if s.region == body_loads.AFT]
    return fwd, box, aft


def test_body_distribution_for_each_fuselage_condition():
    res = body_loads.build_body_loads(_project())
    # One distribution per critical fuselage condition (SELECT R5).
    assert {r.case for r in res} == {
        "MAX DOWN LOAD ON WING", "AFT DOWN BENDING", "AFT UP BENDING", "GREATEST NZ"}


def test_the_two_cantilevers_and_the_box_close_the_free_body():
    """Note 64 gate 4, the closure lock: the forward table's terminal ``(V, M)``
    at the front spar is the forward set's resultant and moment, the aft
    table's at the rear spar likewise, and the two terminals, the box's
    applied rows and the wing reaction sum to zero force and zero moment
    about the wing station.
    """
    results = body_loads.build_body_loads(_project())
    assert results
    for r in results:
        fwd, box, aft = _regions(r)
        assert fwd[-1].source == "root" and aft[0].source == "root"
        assert fwd[-1].x == r.x_front and aft[0].x == r.x_rear
        # Each terminal is its own cantilever's resultant and moment about the spar.
        assert math.isclose(fwd[-1].sz, sum(s.fz for s in fwd), rel_tol=1e-12, abs_tol=1e-9)
        assert math.isclose(fwd[-1].myy, sum(s.fz * (r.x_front - s.x) for s in fwd),
                            rel_tol=1e-12, abs_tol=1e-6)
        assert math.isclose(aft[0].sz, sum(s.fz for s in aft), rel_tol=1e-12, abs_tol=1e-9)
        assert math.isclose(aft[0].myy, sum(s.fz * (s.x - r.x_rear) for s in aft),
                            rel_tol=1e-12, abs_tol=1e-6)
        # ...and the whole free body closes.
        scale_f = sum(abs(s.fz) for s in r.stations)
        scale_m = max(abs(s.myy) for s in r.stations)
        force, moment = body_loads.closure_residuals(r)
        assert abs(force) < 1e-9 * scale_f, (r.case, force)
        assert abs(moment) < 1e-9 * scale_m, (r.case, moment)
        # The box rows carry no running load, by construction (D-64.2).
        assert box and all(s.sz == 0.0 and s.myy == 0.0 for s in box)
        assert all(r.x_front <= s.x <= r.x_rear for s in box)
        assert all(s.x < r.x_front for s in fwd[:-1]) and all(s.x > r.x_rear for s in aft[1:])


def test_a_positive_load_factor_bends_both_bodies_down():
    """Note 64 gate 5 / D-64.4 -- the owner's sign convention as a test: a
    pure-inertia positive-``nz`` set has negative shear and negative bending at
    every interior station of **both** bodies, and a negative ``nz`` the
    reverse. This is the sentence CONVENTIONS.md §7 cites for the sign."""
    p = _project()
    carry = carry_through(p)
    station = wing_station(p)
    # The post takes the side of body's own grade (ga6_normal's is the
    # fuselage-width fallback, assumed); a note is carried only by the
    # centreline fallback of §7b amendment 2.
    assert station.refused is None and station.note == ""
    x_w = station.x
    stations = [(s.x, s.weight_lb) for s in p.fuselage_mass.stations]
    for nz, sense in ((2.5, -1.0), (-1.0, 1.0)):
        rows, _info = body_loads.body_distribution(stations, nz, 0.0, 261.027, x_w, carry)
        fwd = [s for s in rows if s.region == body_loads.FORWARD]
        aft = [s for s in rows if s.region == body_loads.AFT]
        assert fwd and aft
        # The shear has the load's sense from the first loaded station in; the
        # moment accumulates one bay later (zero at the free end, and zero at a
        # station whose only outboard neighbour is the unloaded tail row).
        loaded = [s for s in fwd + aft if s.source != "tail"]
        assert all(sense * s.sz > 0.0 for s in loaded), [s.sz for s in loaded]
        assert all(sense * s.myy >= 0.0 for s in fwd + aft), [s.myy for s in fwd + aft]
        assert sense * fwd[-1].myy > 0.0 and sense * aft[0].myy > 0.0   # both roots
    assert body_loads.cantilever_sign(aft=False) == 1.0
    assert body_loads.cantilever_sign(aft=True) == -1.0


def test_the_wing_reaction_closes_the_applied_set_at_the_wing_station():
    """D-64.5: one row, at the wing station, carrying ``R = -sum(fz)`` and the
    couple that zeroes the whole set's moment about that station (right-handed
    about +y). It is a box row, and it is the only row with a couple."""
    p = _project()
    x_w = wing_station(p).x
    for r in body_loads.build_body_loads(p):
        assert r.wing_station_note == ""          # the side of body's own station
        loads = [s for s in r.stations if s.source in ("mass", "tail")]
        assert r.x_wing == x_w
        assert math.isclose(r.r_wing, -sum(s.fz for s in loads), rel_tol=1e-12)
        assert math.isclose(r.m_wing, sum((s.x - x_w) * s.fz for s in loads),
                            rel_tol=1e-12, abs_tol=1e-6)
        reaction = [s for s in r.stations if s.source == "reaction"]
        assert len(reaction) == 1 and reaction[0].region == body_loads.BOX
        assert reaction[0].x == x_w and reaction[0].fz == r.r_wing
        assert reaction[0].couple == r.m_wing
        assert all(s.couple == 0.0 for s in r.stations if s.source != "reaction")


def test_spar_reactions_are_the_static_equivalent_of_the_one_reaction():
    """Note 64 gate 6: ``R_f + R_r = R`` and the pair's right-handed moment
    about the wing station recovers the couple -- p103's 2x2, reported for the
    fittings and applied nowhere."""
    p = _project()
    carry = carry_through(p)
    assert carry is not None
    for r in body_loads.build_body_loads(p):
        assert math.isclose(r.r_front + r.r_rear, r.r_wing, rel_tol=1e-9)
        moment = (r.x_wing - r.x_front) * r.r_front - (r.x_rear - r.x_wing) * r.r_rear
        assert math.isclose(moment, r.m_wing, rel_tol=1e-9, abs_tol=1e-6)
        assert (r.x_front, r.x_rear) == (carry.x_f, carry.x_r)
        assert r.m_unbalanced != 0.0            # p103's pass-1 moment is still reported
    rows = body_loads.fitting_load_rows(body_loads.build_body_loads(p))
    assert rows and {"R front", "R rear", "R wing", "M wing", "X wing"} <= set(rows[0])


def test_a_station_at_a_spar_is_the_boxs():
    """Note 64 §8 ruling 2: a mass station exactly at a spar is a box row and
    enters neither cantilever."""
    p = _project()
    carry = carry_through(p)
    x_w = wing_station(p).x
    stations = [(30.0, 200.0), (carry.x_f, 100.0), (carry.x_r, 100.0), (250.0, 150.0)]
    rows, _ = body_loads.body_distribution(stations, 2.0, 0.0, 261.027, x_w, carry)
    at_spar = [s for s in rows if s.source == "mass" and s.x in (carry.x_f, carry.x_r)]
    assert len(at_spar) == 2 and all(s.region == body_loads.BOX for s in at_spar)
    fwd = [s for s in rows if s.region == body_loads.FORWARD]
    assert [s.source for s in fwd] == ["mass", "root"]     # only FS 30, then the spar row
    assert math.isclose(fwd[-1].sz, -2.0 * 200.0)


def test_an_unplaceable_wing_post_is_refused_by_name():
    """Note 64 §8 ruling 1 / gate 9: no carry-through, or a wing station
    outside the spars, refuses with the register's own sentence -- the
    whole-body closure artifact that used to close such a beam is gone.

    An out-of-order spar pair is what ``carry_through`` refuses (rear ahead of
    front); a pair that does not bracket the side of body's station is what
    the register refuses (D-64.3), naming all three stations.
    """
    with pytest.raises(MissingInputError, match="carry-through"):
        body_loads.build_body_loads(_with_spars(180.0, 60.0))
    x_w = wing_station(_project()).x
    with pytest.raises(MissingInputError) as err:
        body_loads.build_body_loads(_with_spars(x_w + 10.0, x_w + 40.0))
    text = str(err.value)
    assert "not between" in text and f"FS {x_w:.1f}" in text
    assert f"FS {x_w + 10.0:.1f}" in text and f"FS {x_w + 40.0:.1f}" in text
    assert not hasattr(body_loads, "CLOSURE_ARTIFACT_CAVEAT")


def test_a_project_with_no_side_of_body_reacts_the_wing_at_an_assumed_station():
    """Note 64 §7b amendment 2: a full planform with no body datum -- no
    ``sob_y_in`` and no fuselage width, ``concept_heavy`` -- keeps its body
    loads on a wing station **assumed** at the wing LRA's centreline point,
    with the register's sentence carried on every result; the LRA model still
    refuses such a project, since it has no SOB joint to start the wing at."""
    from sloads.export.lra_model import LraRefusal, build_lra_model
    from sloads.joints import WING_STATION_CENTRELINE, JointName, joints, wing_lra_point

    p = io.load_project(os.path.join(_EXAMPLES, "concept_heavy.project.json"))
    station = wing_station(p)
    assert station.refused is None and station.assumed
    assert station.x == pytest.approx(wing_lra_point(p, 0.0)[0])
    post = joints(p).one(JointName.WING_POST)
    assert post.basis == WING_STATION_CENTRELINE and post.note == station.note
    assert "wing station ASSUMED" in station.note and "sob_y_in" in station.note
    results = body_loads.build_body_loads(p)
    assert results and all(r.wing_station_note == station.note for r in results)
    assert all(r.x_wing == station.x for r in results)
    with pytest.raises(LraRefusal, match="side of body"):
        build_lra_model(p)


def test_body_load_rows_shape():
    rows = body_loads.body_load_rows(body_loads.build_body_loads(_project()))
    assert rows and set(rows[0]) == {"Case", "X", "Fz", "My_free", "Sz", "Myy", "Region", "Basis"}
    # The basis travels in-band with every row (defect M4-15).
    assert all(r["Basis"] == "LIMIT" for r in rows)
    # A box row prints no running load (D-64.2); every other row prints both.
    box = [r for r in rows if r["Region"] == body_loads.BOX]
    assert box and all(r["Sz"] == "" and r["Myy"] == "" for r in box)
    assert all(r["Sz"] and r["Myy"] for r in rows if r["Region"] != body_loads.BOX)


def test_body_gids_are_stable_when_the_spar_stations_move():
    """GIDs key off ``BodyStationLoad.source``, not the station's index in the
    merged table: the reaction and the two spar rows sit in the *middle* of
    the beam, and index-based GIDs would have silently renumbered every mass
    station aft of the wing whenever a spar station changed."""
    p = _project()
    r = body_loads.build_body_loads(p)[0]
    mass_gids = {s.x: g for s, g in zip(r.stations, applied.body_station_gids(r))
                 if s.source in ("mass", "tail")}
    # The reaction and spar rows land between mass stations, so the
    # interleaving is real.
    gids = applied.body_station_gids(r)
    assert any(a > b for a, b in zip(gids, gids[1:]))

    wing = p.geometry.by_name("wing")
    wing.front_spar_x_in, wing.rear_spar_x_in = 65.0, 120.0
    r2 = body_loads.build_body_loads(p)[0]
    moved = {s.x: g for s, g in zip(r2.stations, applied.body_station_gids(r2))
             if s.source in ("mass", "tail")}
    assert moved == mass_gids
    assert not r2.spars_assumed and r.spars_assumed


def test_body_gid_blocks_are_disjoint():
    """Mass/tail stations keep the historical 1001+ numbering; the reaction
    and spar rows take their own 1501+ block, below the tail family's 2001."""
    r = body_loads.build_body_loads(_project())[0]
    for s, gid in zip(r.stations, applied.body_station_gids(r)):
        if s.source in ("reaction", "root"):
            assert 1501 <= gid < 2001
        else:
            assert 1001 <= gid < 1501
    assert len(set(applied.body_station_gids(r))) == len(r.stations)
    # The spar rows apply nothing and are not rows of the applied set.
    rows = applied.fuselage_applied_load_rows([r])
    assert len(rows) == len([s for s in r.stations if s.source != "root"])
    reaction = [row for row in rows if row.myy_free != 0.0]
    assert len(reaction) == 1 and reaction[0].x == r.x_wing


def test_moment_closure_fields_round_trip_through_io():
    """The ``BodyLoadResult`` closure fields (and the station ``source``,
    ``region`` and ``couple`` the export and the tables key off) survive
    save/load."""
    import tempfile

    from sloads.models import LoadsResult

    p = _project()
    results = body_loads.build_body_loads(p)
    p.loads = LoadsResult(body_net=results)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "p.json")
        io.save_project(p, path)
        back = io.load_project(path)
    got, want = back.loads.body_net[0], results[0]
    for f in ("m_unbalanced", "r_front", "r_rear", "x_front", "x_rear",
              "x_wing", "r_wing", "m_wing"):
        assert math.isclose(getattr(got, f), getattr(want, f), rel_tol=1e-9), f
    assert got.spars_assumed == want.spars_assumed
    for f in ("source", "region", "couple"):
        assert [getattr(s, f) for s in got.stations] == [getattr(s, f) for s in want.stations]


def test_run_requires_a_beam_from_either_source():
    """The guard is now "no station table from *either* source" (step B1).

    Since B1 the beam is derived from ``weight.items`` (the mass SSOT), so
    clearing ``fuselage_mass`` alone no longer starves the module — the item data
    base still supplies a table, which is the whole point. Both have to be gone.
    """
    project = io.load_project(_GA)
    project.fuselage_mass = None
    project.weight = None
    raised = False
    try:
        body_loads.run(project)
    except ValueError:
        raised = True
    assert raised


def test_the_beam_is_derived_from_the_mass_ssot_without_a_station_table():
    """Clearing ``fuselage_mass`` leaves the beam intact and unchanged.

    Before B1 the entered table was the only source; now it is the *override* and
    the itemized data base is authoritative, so dropping it changes nothing. That
    is the SSOT working: one mass model, two ways in."""
    project = io.load_project(_GA)
    with_table = body_loads.build_body_loads(project)
    project.fuselage_mass = None
    without = body_loads.build_body_loads(project)
    assert [s.x for s in without[0].stations] == [s.x for s in with_table[0].stations]
    assert [s.fz for s in without[0].stations] == [s.fz for s in with_table[0].stations]


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
