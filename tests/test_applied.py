"""sbeam export bridge (Step C4): span-load CSV + FORCE/MOMENT cards + stick model.

Concept mode has no printed oracle, so the bridge is validated by *closure*: the
exported FORCE set sums to the NETLOADS root shear, the MOMENT(My) set to the
root torsion, and the FORCE moments about the root reproduce the root bending --
all by the increment construction in ``report.applied``. The cards are re-parsed by
a self-contained free-field reader (no sbeam dependency) and re-summed. Stick-deck
structure (one root clamp, a CBAR chain, one load set per case) is checked too.

The "deck parses and solves in sbeam" deliverable is verified manually against
the real sbeam parser/solver and recorded in the C4 history entry.

Reference: card style sbeam/results/load_export.py; NASTRAN FORCE/MOMENT/GRID/
CBAR/PBAR/MAT1/SPC1 cards.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.report import applied as ap
from sloads.report import tables as rt
from sloads.export.equilibrium import card_totals, closes, parse_cards
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.net_loads import build_net_loads

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")
_CONCEPT = os.path.join(_EXAMPLES, "concept_heavy.project.json")


def _wing_net(path):
    p = io.load_project(path)
    if p.envelope is None:
        p.envelope = build_envelope(p)
    return build_net_loads(p).wing_net


# --------------------------------------------------------------------------- #
# Nodal-load closure (the core guarantee)
# --------------------------------------------------------------------------- #
# The bridge exports ULTIMATE loads (limit x SF); closure holds against SF x root.
from sloads.export.deck_format import SUITE_SF as _SF  # noqa: E402


def _nodal_torsion_about_root(nodes):
    """The deck's rigid-body torsion about its root node: Σ my + Σ (p - root) x F.

    The cards carry each strip's **free** torsion, so the root torsion is only
    recovered once the arms are applied -- which is what a solver does and what
    the deck now claims (note 46 OR-67/OR-68). Summing ``my`` bare would give
    the free-torsion total, a different and much smaller number.
    """
    x0, z0 = nodes[0].x, nodes[0].z
    return sum(n.my + (n.z - z0) * n.fx - (n.x - x0) * n.fz for n in nodes)


def test_nodal_loads_sum_to_root_totals():
    for r in _wing_net(_GA):
        nodes = ap.wing_nodal_loads(r)
        root = r.stations[0]
        y0 = nodes[0].y
        assert math.isclose(sum(n.fz for n in nodes), root.sz, rel_tol=1e-9, abs_tol=1e-6)
        assert math.isclose(sum(n.fx for n in nodes), root.sx, rel_tol=1e-9, abs_tol=1e-6)
        assert math.isclose(_nodal_torsion_about_root(nodes), root.myy,
                            rel_tol=1e-9, abs_tol=1e-3)
        # Bending = FORCE moments about the root strip (exact under the WINGINER quadrature).
        assert math.isclose(sum(n.fz * (n.y - y0) for n in nodes), root.mxx, rel_tol=1e-6, abs_tol=1.0)
        assert math.isclose(sum(n.fx * (n.y - y0) for n in nodes), root.mzz, rel_tol=1e-6, abs_tol=1.0)


def test_concept_closure():
    results = _wing_net(_CONCEPT)
    assert results
    for r in results:
        nodes = ap.wing_nodal_loads(r)
        assert math.isclose(sum(n.fz for n in nodes), r.stations[0].sz, rel_tol=1e-9, abs_tol=1e-6)
        assert math.isclose(_nodal_torsion_about_root(nodes),
                            r.stations[0].myy, rel_tol=1e-9, abs_tol=1e-3)










def test_a_filtered_export_does_not_renumber_the_surviving_subcases():
    """M4-2 decision 8: the deck ``SUBCASE``/``SID`` is a property of the case, so
    dropping a case from the export leaves the others' numbers exactly where they
    were. Before M4-2 the number was the case's *position*, so deselecting one
    case shifted every case after it -- ``SUBCASE 2`` meant a different condition
    in two exports of the same project, with nothing in either deck saying so."""
    results = _wing_net(_GA)
    assert len(results) >= 3
    full = {r.case_ref.case_id: ap._sid(1, i, r) for i, r in enumerate(results)}

    keep = [r for r in results if r.case_ref.case_id != results[0].case_ref.case_id]
    kept_ids = [r.case_ref.case_id for r in keep]
    assert rt.filter_by_selected_case_ids(results, kept_ids) == keep
    filtered = {r.case_ref.case_id: ap._sid(1, i, r) for i, r in enumerate(keep)}
    assert filtered == {cid: full[cid] for cid in kept_ids}

    # ... and the map block a deck carries names the surviving cases under those
    # same numbers. It read the wing stick deck's text until note 56 D-56.2
    # deleted it; `subcase_map_block` is the owner both it and every surviving
    # deck render from, so the property is asserted at the owner.
    lines = "\n".join(ap.subcase_map_block(keep))
    for cid in kept_ids:
        assert f"$ SUBCASE {full[cid]} = {cid} -- " in lines
    dropped = results[0].case_ref.case_id
    assert f"$ SUBCASE {full[dropped]} = " not in lines


def test_subcase_map_names_the_governing_condition():
    """Decision 10: a deck consumer can trace a subcase back to its condition
    from the deck alone -- id, condition and FAR reference, on one line."""
    results = _wing_net(_GA)
    lines = ap.subcase_map_block(results)
    assert lines and lines[0].startswith("$ ")
    body = [ln for ln in lines if ln.startswith("$ SUBCASE ")]
    assert len(body) == len(results)
    for r, ln in zip(results, body):
        ref = r.case_ref
        assert f"= {ref.case_id} -- {ref.condition}" in ln
        assert f"FAR {ref.far_reference}" in ln






# --------------------------------------------------------------------------- #
# Inputs & file writers
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# The applied load set (the structures deliverable, oracle report Appendix B.1)
# --------------------------------------------------------------------------- #
_BARON = os.path.join(_EXAMPLES, "baron_58.project.json")


def _lra_net(path):
    """Net wing loads transferred to the wing's loads reference axis."""
    from sloads.modules.net_loads import loads_ref_axis_results

    p = io.load_project(path)
    if p.envelope is None:
        p.envelope = build_envelope(p)
    return loads_ref_axis_results(p, list(build_net_loads(p).wing_net))


def _csv_rows(text):
    import csv as _csv

    from sloads.report.methods import strip_comment_lines

    return list(_csv.DictReader(strip_comment_lines(text).splitlines()))


def test_the_applied_set_carries_every_strip_and_every_concentrated_mass():
    """One row per strip plus one per wing mass -- the whole applied set."""
    net = _lra_net(_BARON)
    one = net[0]
    rows = ap.applied_load_rows([one])
    assert len(rows) == len(one.stations) + len(one.point_loads)
    assert len(one.point_loads) == 4, "the Baron enters four concentrated wing masses"
    named = [r.label for r in rows if r.gid is None]
    assert named == [m.name for m in one.point_loads]


def test_a_concentrated_mass_has_no_grid_and_no_free_moment():
    """A point mass is a pure force: every moment it makes is force x arm."""
    rows = ap.applied_load_rows(_lra_net(_BARON)[:1])
    masses = [r for r in rows if r.gid is None]
    assert masses, "the Baron has concentrated wing masses"
    for m in masses:
        assert m.myy_free == 0.0
        assert m.fz != 0.0


def _resultant(rows, about, outboard_of):
    """The applied set's six-component resultant about ``about``, tip-inboard.

    ``rows`` are :class:`~sloads.report.applied.AppliedLoad` records; only
    those at or outboard of ``outboard_of`` (a span station, in) contribute --
    which is exactly the population the cumulative table at that station holds.
    Moments are right-handed ``r x F`` plus the record's own free moments,
    taken through ``applied_body_moments`` so the sign map has one owner.
    """
    sx = sz = mx = my = mz = 0.0
    for r in rows:
        if r.y < outboard_of:
            continue
        dx, dy, dz = r.x - about[0], r.y - about[1], r.z - about[2]
        bmx, bmy, bmz = ap.applied_body_moments(r)
        sx += r.fx
        sz += r.fz
        mx += dy * r.fz - dz * r.fy + bmx
        my += dz * r.fx - dx * r.fz + bmy
        mz += dx * r.fy - dy * r.fx + bmz
    return sx, sz, mx, my, mz


def test_the_applied_set_reproduces_the_whole_vmt_at_every_station():
    """The closure gate: the applied vector rebuilds V, M and T along the span.

    This is what makes the set a deck. A model applying the six components at
    the stated points generates every sweep, dihedral and span transfer itself,
    so the applied moment must be the *free* moment only -- carrying the
    increment of the cumulative instead would double the transfer.

    Checked at **every** station, not only the root, and on all five components
    the wing chain publishes: a set that closed at the root alone could still
    put the load in the wrong bay. ``Mzz`` is compared negated because the calc
    stores spanwise bending as a positive-magnitude integral while the body-axis
    resultant is ``r x F`` (``coordinates.bending_moment_vector``).
    """
    for path in (_GA, _BARON):
        for result in _lra_net(path):
            rows = ap.applied_load_rows([result])
            for station in result.stations:
                about = (station.x, station.y, station.z)
                got = _resultant(rows, about, station.y)
                want = (station.sx, station.sz, station.mxx, station.myy,
                        -station.mzz)
                for name, g, w in zip(("Sx", "Sz", "Mxx", "Myy", "Mzz"),
                                      got, want):
                    assert closes(g, w, scale=abs(w)), (
                        f"{path} {result.case} y={station.y:.1f} {name}: "
                        f"applied set gives {g}, table has {w}")


def test_the_applied_set_states_all_six_components():
    """Fy, Mx and Mz are published as zero, not left out (the reader's benefit).

    Their being zero is a property of this load set -- no spanwise strip load
    and no lateral wing condition; no free bending under strip theory -- and a
    consumer building cards has to be able to tell that from an omission.
    """
    for path in (_GA, _BARON):
        rows = ap.applied_load_rows(_lra_net(path))
        assert rows
        for r in rows:
            assert r.fy == 0.0
            assert ap.applied_body_moments(r)[0] == 0.0
            assert ap.applied_body_moments(r)[2] == 0.0
        assert any(r.myy_free for r in rows), "My is not structurally zero"


def test_the_applied_moment_is_the_free_moment_not_the_increment():
    """Guards the whole point of the file against a differencing 'simplification'.

    ``Myy free`` and the increment of the cumulative ``Myy`` are different
    quantities -- on ``ga6_normal`` PHAA the inboard strips disagree in sign --
    so a set built by differencing cannot be applied at these coordinates.
    """
    result = _lra_net(_GA)[0]
    s = result.stations
    increments = [s[i].myy - (s[i + 1].myy if i + 1 < len(s) else 0.0)
                  for i in range(len(s))]
    rows = [r for r in ap.applied_load_rows([result]) if r.gid is not None]
    opposed = [i for i, (r, d) in enumerate(zip(rows, increments)) if r.myy_free * d < 0]
    assert opposed, ("the two quantities no longer differ in sign anywhere -- if "
                     "the physics moved, restate the case; if the export was "
                     "rewritten to difference the cumulative, that is the defect")


def test_the_applied_csv_states_its_units_axis_and_factor():
    """A distribution file is unusable without its units, axis and basis (D-21)."""
    net = _lra_net(_GA)
    from sloads.report.methods import strip_comment_lines

    text = ap.applied_load_csv(net)
    header = strip_comment_lines(text).splitlines()[0]
    assert header.split(",") == [
        "Case", "Station", "GID", "X (in)", "Y (in)", "Z (in)",
        "Fx (lb)", "Fy (lb)", "Fz (lb)",
        "Mx (lb-in)", "My (lb-in)", "Mz (lb-in)", "MyyAxis", "SF"]
    row = _csv_rows(text)[0]
    assert row["MyyAxis"] == net[0].torsion_axis
    assert row["SF"] == "1.5"




def test_the_applied_csv_leaves_a_point_masss_gid_blank():
    """No invented grid: the deck has no node at a concentrated mass (yet)."""
    rows = _csv_rows(ap.applied_load_csv(_lra_net(_BARON)[:1]))
    blank = [r for r in rows if r["GID"] == ""]
    assert len(blank) == 4
    assert all(r["My (lb-in)"] == "0" for r in blank)
    assert all(r["GID"].isdigit() for r in rows if r not in blank)


def test_the_applied_csv_is_ultimate():
    """LIMIT x the case's own SF, like every other deliverable in this channel."""
    net = _lra_net(_GA)[:1]
    rows = ap.applied_load_rows(net)
    csv_rows = _csv_rows(ap.applied_load_csv(net))
    for r, c in zip(rows, csv_rows):
        assert math.isclose(float(c["Fz (lb)"]), r.fz,
                            abs_tol=0.05)


def test_applied_load_writer(tmp_path=None):
    import tempfile

    d = str(tmp_path) if tmp_path else tempfile.mkdtemp()
    path = os.path.join(d, "applied.csv")
    ap.write_applied_load_csv(_lra_net(_GA), path, header_comment="# ULTIMATE\n")
    text = open(path, encoding="utf-8").read()
    assert text.startswith("# ULTIMATE")
    assert "My (lb-in)" in text


def test_accepts_project_and_requires_loads():
    p = io.load_project(_GA)
    try:
        ap.applied_load_csv(p)  # no Project.loads set yet
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError when Project.loads is missing")
    p.loads = build_net_loads(p)
    rows = _csv_rows(ap.applied_load_csv(p))
    assert rows and "GID" in rows[0]


def test_project_export_transfers_to_loads_ref_axis():
    """The Project path states wing torsion about the surface's LRA, labelled in-band."""
    from sloads.modules.wing_geometry import interp_x

    p = io.load_project(_GA)
    p.loads = build_net_loads(p)
    wing = p.geometry.by_name(p.wing_mass.surface)
    wing.ref_axis_pct = 0.40
    rows = _csv_rows(ap.applied_load_csv(p))
    assert rows and all(r["MyyAxis"] == "LRA 40% chord" for r in rows)
    # The applied station X is the LRA point, not the 25% chord it was computed
    # about: the transfer moved the point the load is stated at.
    raw = p.loads.wing_net[0].stations[0]
    x_le = interp_x(wing.leading_edge, raw.y)
    x_te = interp_x(wing.trailing_edge, raw.y)
    x_lra = x_le + 0.40 * (x_te - x_le)
    assert math.isclose(float(rows[0]["X (in)"]), x_lra, rel_tol=1e-3, abs_tol=0.01)


def test_writers(tmp_path=None):
    import tempfile

    results = _lra_net(_GA)
    d = tmp_path or tempfile.mkdtemp()
    csv_p = os.path.join(str(d), "w.applied_loads.csv")
    ap.write_applied_load_csv(results, csv_p)
    assert os.path.getsize(csv_p) > 0










# --------------------------------------------------------------------------- #
# Export-scope filter (Step D8.3)
# --------------------------------------------------------------------------- #
def test_filter_by_selected_case_ids_none_is_unfiltered():
    results = _wing_net(_GA)
    assert rt.filter_by_selected_case_ids(results, None) == results


def test_filter_by_selected_case_ids_keeps_only_selected():
    results = _wing_net(_GA)
    ids = {results[0].case_ref.case_id}
    filtered = rt.filter_by_selected_case_ids(results, ids)
    assert len(filtered) == 1
    assert filtered[0].case_ref.case_id == results[0].case_ref.case_id


def test_filter_by_selected_case_ids_empty_selection_drops_all_tagged():
    results = _wing_net(_GA)
    assert rt.filter_by_selected_case_ids(results, set()) == []


def test_the_applied_load_set_has_one_address_and_the_export_package_is_not_it():
    """Note 56 D-56.1: the applied-load model lives in ``report/``, and only there.

    Step P1-4 asserted that all four *component deck* families were reachable
    from ``sloads.export``. D-56.2 deleted all of them, and D-56.1 then took the
    surface that had replaced them -- the applied load set, the station
    numbering and the side-of-body loads -- out of the package too, because none
    of it is a bridge to sbeam: it is the record of what is applied and where,
    which the report is built from.

    So this pins one address per name, in both directions. Every name resolves
    from :mod:`sloads.report.applied`; **none** of them is re-exported by
    ``sloads.export``. A compatibility alias would put one name at two
    addresses, which is the condition note 56 exists to remove -- and it is the
    condition that let the deck writers keep a public surface after the decks
    themselves stopped being deliverables. The deleted writers are listed beside
    them so a name cannot come back without an artifact.
    """
    import sloads.export as export_pkg
    from sloads.report.applied import (  # noqa: F401
        AppliedLoad,
        applied_load_csv,
        applied_loads,
        beam_station_gid,
        body_station_gids,
        sob_internal_loads,
        station_gid,
        wing_nodal_loads,
        write_applied_load_csv,
    )
    from sloads.report.tables import (  # noqa: F401
        case_index_csv,
        filter_by_selected_case_ids,
        write_case_index_csv,
    )

    for name in ("applied_loads", "applied_load_csv", "write_applied_load_csv",
                 "station_gid", "beam_station_gid", "body_station_gids",
                 "wing_nodal_loads", "AppliedLoad", "sob_internal_loads"):
        assert hasattr(ap, name), f"{name} missing from report.applied"
        assert not hasattr(export_pkg, name), (
            f"{name} is the applied-load model (note 56 D-56.1); it moved to "
            "sloads.report.applied and the export package must not re-export it")
        assert name not in export_pkg.__all__, f"{name} still in export __all__"

    for name in ("case_index_csv", "write_case_index_csv",
                 "filter_by_selected_case_ids", "safety_factors_csv",
                 "gear_report_csv"):
        assert not hasattr(export_pkg, name), (
            f"{name} is a report table (note 56 D-56.1); the export package "
            "must not re-export it")

    for name in ("span_load_csv", "force_moment_cards", "stick_model_bdf",
                 "body_span_load_csv", "body_force_moment_cards",
                 "body_fitting_load_csv", "tail_chordwise_csv",
                 "tail_force_moment_cards", "tail_span_csv",
                 "tail_span_force_moment_cards", "control_surface_csv",
                 "control_surface_force_moment_cards"):
        assert not hasattr(export_pkg, name), (
            f"{name} is a per-component deck writer (note 56 D-56.2); it was "
            "deleted, and an alias here would resurrect the name without the "
            "artifact")
        assert not hasattr(ap, name), f"{name} still exists in report.applied"


def test_no_module_named_sbeam_bridge_survives_the_move():
    """D-56.1's other half: the file is gone, not emptied or aliased.

    ``sbeam_bridge`` named a bridge to sbeam that had not existed in the file
    for two milestones. Leaving an importable shim would keep the name -- and
    the misfiling it records -- alive in every citation that has not been
    re-pointed yet.
    """
    import importlib

    for name in ("sloads.export.sbeam_bridge", "sloads.report.sbeam_bridge"):
        try:
            importlib.import_module(name)
        except ImportError:
            continue
        raise AssertionError(
            f"{name} is importable; note 56 D-56.1 dissolved it into "
            "sloads.report.applied and left no shim")


# --------------------------------------------------------------------------- #
# Per-case safety factor (defect M4-7)
#
# The bridge used to hardcode a flat x1.5 and ignore the case's own factor, so a
# case whose values are already ultimate (safety_factor = 1.0, per the CLAUDE.md
# ultimate-load contract) would have been multiplied by 1.5 a second time. These
# lock the factor to the *result*, not to a suite-wide constant.
# --------------------------------------------------------------------------- #
def _wing_net_with_sf(sf):
    """The GA wing net loads with every case's safety factor forced to ``sf``."""
    results = _wing_net(_GA)
    for r in results:
        r.safety_factor = sf
    return results


def test_wing_export_honours_per_case_safety_factor():
    """Closure holds against *that case's* factor -- SF=1.0 exports unscaled."""
    for sf in (1.0, 1.25, _SF):
        for r in _wing_net_with_sf(sf):
            nodes = ap.wing_nodal_loads(r)
            root = r.stations[0]
            assert math.isclose(sum(n.fz for n in nodes), root.sz,
                                rel_tol=1e-9, abs_tol=1e-6), sf
            assert math.isclose(_nodal_torsion_about_root(nodes), root.myy,
                                rel_tol=1e-9, abs_tol=1e-3), sf


def test_wing_export_mixes_factors_across_cases():
    """Two cases, two factors: each load set scales by its own, not by the first."""
    results = _wing_net(_GA)
    assert len(results) >= 2
    results[0].safety_factor = 1.0
    results[1].safety_factor = 1.5
    for r in results[:2]:
        nodes = ap.wing_nodal_loads(r)
        assert math.isclose(sum(n.fz for n in nodes), r.stations[0].sz,
                            rel_tol=1e-9, abs_tol=1e-6), r.case








def test_taildist_and_body_copy_the_condition_factor():
    """The producers carry the owning CriticalCondition's factor into the slice."""
    from sloads.modules.body_loads import build_body_loads
    from sloads.modules.select import build_critical
    from sloads.modules.taildist import build_tail_chordwise

    p = io.load_project(_GA)
    if p.envelope is None:
        p.envelope = build_envelope(p)
    # Persist the critical set so both producers read the *same* (mutated) conditions.
    p.envelope.critical = build_critical(p)
    for cond in p.envelope.critical.conditions:
        cond.safety_factor = 1.25

    derived = build_body_loads(p) + build_tail_chordwise(p)
    assert derived
    for r in derived:
        assert r.safety_factor == 1.25, r.case


# --------------------------------------------------------------------------- #
# Per-case safety factor, wing + control surfaces (defect M4-13)
#
# These four modules own their conditions (no upstream CriticalCondition to copy
# from), so the factor is minted once in build_* and run()'s ConditionResult must
# copy it from the built result -- never re-default it independently.
# --------------------------------------------------------------------------- #
def _ga_project():
    p = io.load_project(_GA)
    if p.envelope is None:
        p.envelope = build_envelope(p)
    return p


def test_wing_and_control_results_agree_with_their_conditions():
    """Each producer's result slice and rendered ConditionResult carry one factor."""
    from sloads.modules import aileron, flap, net_loads, tab

    p = _ga_project()

    loads = net_loads.build_net_loads(p)
    conds = {c.case_ref.case_id: c for c in net_loads.run(p).conditions}
    for r in loads.wing_air + loads.wing_inertia + loads.wing_net:
        assert r.safety_factor == conds[r.case_ref.case_id].safety_factor, r.case

    down, up = aileron.build_aileron(p)
    assert down.safety_factor == up.safety_factor
    assert aileron.run(p).conditions[0].safety_factor == down.safety_factor

    built = flap.build_flap(p)[0]
    assert flap.run(p).conditions[0].safety_factor == built.safety_factor

    for r, c in zip(tab.build_tabs(p), tab.run(p).conditions):
        assert r.safety_factor == c.safety_factor, r.case


def test_run_copies_the_built_results_factor():
    """run() reads the mint in build_* rather than defaulting a second source of
    truth -- a non-default factor must reach the rendered ConditionResult."""
    from sloads.modules import aileron, flap, net_loads, tab

    p = _ga_project()

    def force_sf(results):
        for r in results:
            r.safety_factor = 1.25
        return results

    # build_net_loads returns a LoadsResult; the control-surface builders a list.
    patches = [
        (net_loads, "build_net_loads", lambda built: force_sf(built.wing_net)),
        (aileron, "build_aileron", force_sf),
        (flap, "build_flap", force_sf),
        (tab, "build_tabs", force_sf),
    ]
    for module, attr, mutate in patches:
        real = getattr(module, attr)

        def patched(proj, real=real, mutate=mutate):
            built = real(proj)
            mutate(built)
            return built

        setattr(module, attr, patched)
        try:
            for cond in module.run(p).conditions:
                assert cond.safety_factor == 1.25, (module.MODULE_NAME, cond.title)
        finally:
            setattr(module, attr, real)


# --------------------------------------------------------------------------- #
# Side-of-body node + internal loads (step 13, note 24 R-3)
# --------------------------------------------------------------------------- #
_RJ = os.path.join(_EXAMPLES, "concept_regional_jet.project.json")
_ATR = os.path.join(_EXAMPLES, "atr42_100.project.json")


def _project_and_wing(path):
    from sloads.modules.net_loads import loads_ref_axis_results

    p = io.load_project(path)
    if p.envelope is None:
        p.envelope = build_envelope(p)
    return p, loads_ref_axis_results(p, build_net_loads(p).wing_net)


def test_sob_internal_loads_match_the_cumulative_table_at_a_cut():
    """Way one of two: the outboard sum reproduces NETLOADS' own cumulative table.

    On the mass-free Appendix A wing the closed-form sum of applied nodal loads
    outboard of a cut equals the cumulative shear/torsion at the next station
    plus the bending carried back over the remaining arm -- computed by
    different code (WINGINER quadrature) than the card increments being summed.
    """
    for r in _wing_net(_GA):
        s, sf = r.stations, r.safety_factor
        for k in (0, 2, len(s) - 2):
            y_cut = 0.5 * (s[k].y + s[k + 1].y)
            si = ap.sob_internal_loads(r, y_cut)
            nxt = s[k + 1]
            assert math.isclose(si.sz, nxt.sz, rel_tol=1e-9, abs_tol=1e-6)
            assert math.isclose(si.sx, nxt.sx, rel_tol=1e-9, abs_tol=1e-6)
            # Torsion at the cut is the next station's value transferred to the
            # cut's own point on the LRA -- the cut is half a strip inboard, and
            # a swept, dihedralled axis makes that a real difference (19 % at
            # the root strip of ga6_normal). Under the old differenced cards the
            # transfer was already inside ``my`` and this read as nxt.myy flat.
            x_cut = 0.5 * (s[k].x + s[k + 1].x)
            z_cut = 0.5 * (s[k].z + s[k + 1].z)
            want_myy = (nxt.myy - nxt.sz * (nxt.x - x_cut)
                        + nxt.sx * (nxt.z - z_cut))
            assert math.isclose(si.myy, want_myy, rel_tol=1e-9, abs_tol=1e-3)
            assert math.isclose(si.mxx, (nxt.mxx + nxt.sz * (nxt.y - y_cut)),
                                rel_tol=1e-6, abs_tol=1.0)
            assert math.isclose(si.mzz, (nxt.mzz + nxt.sx * (nxt.y - y_cut)),
                                rel_tol=1e-6, abs_tol=1.0)










def test_the_deck_and_applied_load_surface_takes_no_silent_defaults():
    """CH-2 (code-standard review item 9): the error contract -- "flagged,
    never silently defaulted" -- holds structurally across the export package
    and the applied-load model.

    ``getattr(obj, name, default)`` is the shape that hides a missing attribute
    behind a quiet fallback; every result the exporters read is a typed
    dataclass whose ``case_ref`` / ``case`` / ``hand`` / ``tip_transfer`` are
    declared fields, so they are read as attributes. The one dynamic lookup
    (the ``htail``/``vtail`` span slice) is an explicit map that refuses an
    unknown component. Two-argument ``getattr`` -- a *dynamic attribute name*
    on a typed object, no default -- is not this class and stays allowed."""
    import ast
    from pathlib import Path

    # The export package, plus this module -- and *only* this module out of
    # ``report/``. Note 56 D-56.1 moved the applied-load model here; the rule it
    # was written under travels with the code, not with the directory. The rest
    # of ``report/`` renders whatever a project happens to carry and reads
    # optional slices with defaults by design, which is why the sweep is a named
    # file set rather than a second package walk.
    import sloads.export as export_pkg

    paths = sorted(Path(export_pkg.__file__).parent.glob("*.py"))
    paths.append(Path(ap.__file__))
    hits = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "getattr" and len(node.args) >= 3):
                hits.append(f"{path.name}:{node.lineno}")
    assert not hits, (
        "getattr(..., default) in the export package or the applied-load "
        f"model: {hits}")


def test_tail_span_export_refuses_an_unknown_component():
    """The slice lookup is a map, so a bad component name is a stated error,
    not an empty export (CH-2).

    Asserted at ``applied_loads`` since note 56 D-56.2 deleted the spanwise
    deck writer: the map is the same one, and the public entry point is the
    better place to hold it.
    """
    project = io.load_project(_GA)
    for entry in (lambda: ap.applied_loads("canard", project),
                  lambda: ap._tail_span_results(project, "canard")):
        try:
            entry()
        except ValueError as exc:
            assert "'canard'" in str(exc), str(exc)
        else:
            raise AssertionError("an unknown component was accepted")


def test_card_components_snap_dust_and_negative_zero():
    """One card's three components: dust below ``CARD_TOL x`` the card's own scale
    prints as ``0.000000E+00`` -- never as its platform-dependent residue, and
    never as ``-0.000000E+00`` (both failed the frozen digest in CI while the
    same commit passed locally). A real small component is untouched."""
    from sloads.export.deck_format import fmt3
    assert fmt3(-912.811, 6.101335e-15, 3244.192) == \
        "-9.128110E+02, 0.000000E+00, 3.244192E+03"
    assert fmt3(-0.0, -0.0, 4384.268) == \
        "0.000000E+00, 0.000000E+00, 4.384268E+03"
    # relative floor: 1e-5 of a 1e3 load is above 1e-9 x scale -> kept
    assert fmt3(1000.0, 1e-5, 0.0) == "1.000000E+03, 1.000000E-05, 0.000000E+00"
    # absolute floor for an all-tiny card: 1e-8 stays, 1e-10 goes
    assert fmt3(1e-8, 1e-10, 0.0) == "1.000000E-08, 0.000000E+00, 0.000000E+00"
    # every FORCE/MOMENT triple in the exporters goes through it (rule 4 guard)
    import re
    from pathlib import Path
    root = Path(ap.__file__).parent
    triple = re.compile(r"\{fmt\(\w+\)\}, \{fmt\(\w+\)\}, \{fmt\(\w+\)\}")
    hits = [f"{f.name}: {ln.strip()}" for f in root.glob("*.py")
            for ln in f.read_text().splitlines()
            if triple.search(ln) and "PBAR" not in ln]   # PBAR's A, I1, I2 is not a vector
    assert not hits, f"vector cards formatted component-wise, bypassing fmt3: {hits}"


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


def test_a_mixed_basis_csv_keeps_a_plain_header_and_an_all_ultimate_one_is_marked():
    """OR-118a's per-table rule, now that a mixed table exists (note 44 §21).

    Read against the v-tail's **applied load set** since note 56 D-56.2 deleted
    the chordwise CSV it used to read; the 23.367(a)(2) case sits in that file
    for the same reason it sat in the other one, so the rule keeps its live
    demonstration.

    This test used to assert the *fact* that no already-ultimate case reached a
    per-component CSV, and said in as many words that it was a fact about the
    result set rather than a law -- so that the day one arrived, the guard would
    fail rather than a plain column heading quietly under-stating the basis.
    OR-172 admitted 23.367 to the fin's critical set and that day came: the
    23.367(a)(2) case is ``engine_ultimate`` at SF 1.0 and now sits in the
    v-tail chordwise and spanwise files beside five LIMIT ones.

    What replaces it is the rule itself, in both directions. A **mixed** file
    keeps plain load columns and carries the distinction in its per-row ``SF``
    cell, because a heading that claimed ``-ULT`` would over-state every limit
    row and one that claimed LIMIT would invite a reader to factor a load that
    is already factored. An **all-ultimate** file is marked. The basis is
    :func:`sloads.safety_factors.shared_basis_factor`, which is the single owner
    both the document and the export read.
    """
    import dataclasses
    import glob
    import os

    from sloads.report.applied import applied_load_csv
    from sloads.io import load_project
    from sloads.modules.tail_span import build_tail_span
    from sloads.safety_factors import shared_basis_factor

    def _header_marked(text):
        return "-ULT" in [ln for ln in text.splitlines()
                          if not ln.startswith("#")][0]

    saw_mixed = False
    for path in sorted(glob.glob(os.path.join(_EXAMPLES, "*.project.json"))):
        project = load_project(path)
        try:
            results = build_tail_span(project).get("vtail") or []
        except Exception:
            continue
        if not results:
            continue
        factors = {r.safety_factor for r in results}
        text = applied_load_csv(results, component="vtail")
        if len(factors) > 1:
            saw_mixed = True
            assert not _header_marked(text), (
                f"{os.path.basename(path)}: a table mixing "
                f"{sorted(factors)} must keep a plain header (OR-118a)")
            assert shared_basis_factor(results) is None
            # ...and the distinction has to be somewhere, so it is in the rows.
            assert any(row.strip().endswith(",1.0")
                       for row in text.splitlines()
                       if not row.startswith("#")), (
                f"{os.path.basename(path)}: the already-ultimate row states no "
                f"SF of 1.0, so the mixed file states its basis nowhere")
        elif factors == {1.0}:
            assert _header_marked(text), (
                f"{os.path.basename(path)}: every row is already ultimate, so "
                f"the load columns must carry -ULT (OR-118)")

    assert saw_mixed, (
        "no shipped example produces a mixed-basis fin file any more. Either "
        "23.367 has left the fin's critical set (note 44 OR-172) or the "
        "fixtures have changed; this rule then has no live demonstration and "
        "the reason it exists has to be re-established, not deleted.")


def test_the_shared_basis_owner_is_asked_by_both_deliverables():
    """One owner for OR-118a, read by the document and by the export (rule 3).

    The rule was written twice -- once in ``report.render._table_sf``, once as
    an assumption in ``report.applied._load_label`` -- which is how a mixed
    table became expressible in one deliverable and unthinkable in the other.
    """
    from sloads.report.render import _table_sf
    from sloads.safety_factors import shared_basis_factor

    class _R:
        def __init__(self, sf):
            self.safety_factor = sf

    for case in ([], [_R(1.5)], [_R(1.0)], [_R(1.0), _R(1.5)], [_R(1.0), _R(1.0)]):
        assert _table_sf(case) == shared_basis_factor(case)
    assert shared_basis_factor([_R(1.0), _R(1.0)]) == 1.0
    assert shared_basis_factor([_R(1.0), _R(1.5)]) is None
    assert shared_basis_factor([]) is None
