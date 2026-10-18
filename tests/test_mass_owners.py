"""Design note 71 (#383): one owner per mass quantity -- the closure gates.

G-71.1 (no delivered load moves) is the frozen Imperial digests; G-71.4 (the
six moved rows render on the pages the note names) is held here beside
``tests/test_field_registry.py``'s page pins; G-71.7 (the control-load fields
on the surface rows) is exercised by ``tests/test_tail_span.py``'s discrete
cases, which set them there. Every file has a zero-dependency self-runner.
"""

import glob
import math
import os
import sys
from dataclasses import replace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import field_registry as fr
from sloads import io
from sloads.cg_cases import max_takeoff_weight
from sloads.migrations import applied_hops, migrate
from sloads.models import SCHEMA_VERSION

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = sorted(glob.glob(os.path.join(_ROOT, "examples", "*.project.json")))


def _project(path):
    return io.load_project(path)


# --------------------------------------------------------------------------- #
# G-71.2 -- the speeds weight is a collapsed override of MTOW
# --------------------------------------------------------------------------- #
def test_a_blank_speeds_weight_derives_mtow_exactly_and_a_typed_one_governs():
    from sloads.modules.structural_speeds import design_speed_values, design_weight_lb
    from sloads.validation import consistency_warnings

    p = _project(os.path.join(_ROOT, "examples", "ga6_normal.project.json"))
    mtow = max_takeoff_weight(p)
    assert p.speeds.weight_lb == 0.0
    assert design_weight_lb(p, p.speeds) == mtow
    assert fr.external_value("speeds.weight_lb", p) == mtow
    assert "speeds.weight_lb" in fr.COLLAPSED_OVERRIDES
    blank = design_speed_values(p, p.speeds)
    assert blank == design_speed_values(p, replace(p.speeds, weight_lb=mtow))
    p.speeds.weight_lb = mtow + 100.0
    assert design_weight_lb(p, p.speeds) == mtow + 100.0
    assert design_speed_values(p, p.speeds) != blank
    assert "mtow_representation_drift" in {w.code for w in consistency_warnings(p)}
    # The MTOW owner no longer reads the copy back (no circle).
    p.weight.max_takeoff_weight_lb = 0.0
    p.weight.envelope = None
    p.weight.cg_cases = []
    assert max_takeoff_weight(p, required=False) == 0.0


# --------------------------------------------------------------------------- #
# G-71.3 -- the v79 -> v80 hop: one delete, two moves, the notes
# --------------------------------------------------------------------------- #
def _v79(**over):
    d = {
        "schema_version": 79,
        "weight": {"max_takeoff_weight_lb": 3400.0, "items": [], "cg_cases": []},
        "geometry": {
            "surfaces": [{"name": "htail", "leading_edge": [[0, 0], [1, 1]], "trailing_edge": [[2, 0], [3, 1]]},
                         {"name": "elevator", "leading_edge": [[0, 0], [1, 1]], "trailing_edge": [[2, 0], [3, 1]]}],
            "empennage": {"vtail": {"wing_span_in": 400.0, "gross_weight_lb": 3400.0, "izz_slugft2": 0.0}},
            "fuselage": {"sections": [], "body_drag_waterline_z": 0.0, "airplane_length_in": 0.0},
        },
        "fuselage_mass": {"stations": [], "ref_waterline": 87.7, "stations_are_override": False},
        "tail_mass": [{"surface": "htail", "panel_weight_lb": 60.0, "weight_is_override": True,
                       "control_load_mode": "discrete", "hinges_span_in": [30.0, 90.0],
                       "actuator_span_in": 55.0},
                      {"surface": "vtail", "panel_weight_lb": 40.0, "weight_is_override": True,
                       "control_load_mode": "discrete", "hinges_span_in": [20.0, 50.0],
                       "actuator_span_in": 35.0}],
    }
    d.update(over)
    return d


def test_the_v79_hop_deletes_the_fin_weight_and_moves_the_waterline_and_the_control_fields():
    assert applied_hops(79) == [79]
    out = migrate(_v79())
    assert out["schema_version"] == SCHEMA_VERSION
    vtail = out["geometry"]["empennage"]["vtail"]
    assert "gross_weight_lb" not in vtail and vtail["izz_slugft2"] == 0.0
    assert "ref_waterline" not in out["fuselage_mass"]
    assert out["geometry"]["fuselage"]["beam_waterline_z"] == 87.7
    elevator = next(s for s in out["geometry"]["surfaces"] if s["name"] == "elevator")
    assert elevator["control_load_mode"] == "discrete"
    assert elevator["hinges_span_in"] == [30.0, 90.0] and elevator["actuator_span_in"] == 55.0
    for row in out["tail_mass"]:
        assert "control_load_mode" not in row and "hinges_span_in" not in row
        assert row["weight_is_override"] is True
    # A fin weight equal to MTOW is dropped silently; the rudder's values had no
    # rudder row to land on and are stated once.
    notes = " ".join(out.get("migration_notes", []))
    assert "gross_weight_lb" not in notes
    assert "tail_mass[vtail]" in notes and "hinges_span_in" in notes
    # The migrated dict loads, and the moved values are where their readers look.
    project = io.project_from_dict(out)
    assert project.geometry.fuselage.beam_waterline_z == 87.7
    assert project.geometry.by_name("elevator").hinges_span_in == [30.0, 90.0]


def test_the_v79_hop_states_a_fin_weight_that_differed_from_mtow():
    out = migrate(_v79(geometry={
        "surfaces": [], "empennage": {"vtail": {"gross_weight_lb": 3000.0}}}))
    notes = " ".join(out.get("migration_notes", []))
    assert "gross_weight_lb=3000.0" in notes and "3400" in notes
    # No fuselage outline and no waterline: none is created.
    out = migrate(_v79(fuselage_mass={"stations": [], "ref_waterline": 0.0}, geometry={"surfaces": []}))
    assert "fuselage" not in out["geometry"] or "beam_waterline_z" not in out["geometry"].get("fuselage", {})


# --------------------------------------------------------------------------- #
# G-71.4 -- the moved rows render where the note says, and the deleted one is gone
# --------------------------------------------------------------------------- #
def test_the_moved_rows_render_on_the_pages_the_note_names():
    pages = {
        "geometry.empennage.vtail.izz_slugft2": "weight_mass",
        "wing_mass.panel_weight_override_lb": "weight_mass",
        "wing_mass.tip_root_density_ratio": "weight_mass",
        "wing_mass.inboard_rib_y": "weight_mass",
        "fuselage_mass.stations[].x": "weight_mass",
        "fuselage_mass.stations_are_override": "weight_mass",
        "geometry.fuselage.beam_waterline_z": "configuration_layout",
        "geometry.surfaces[].control_load_mode": "configuration_layout",
        "geometry.surfaces[].hinges_span_in": "configuration_layout",
        "geometry.surfaces[].actuator_span_in": "configuration_layout",
        "engines[].engine_mass_item": "configuration_layout",
        "engines[].prop_mass_item": "configuration_layout",
        "wing_mass.cases[].name": "wing_loads",
        "speeds.weight_lb": "structural_speeds",
    }
    for path, page in pages.items():
        assert fr.entry(path).page == page, path
    for gone in ("geometry.empennage.vtail.gross_weight_lb", "fuselage_mass.ref_waterline",
                 "tail_mass[].control_load_mode", "tail_mass[].hinges_span_in",
                 "tail_mass[].actuator_span_in"):
        assert gone not in fr.BY_PATH, gone
    assert fr.entry("engines[].engine_mass_item").supplied, "load-bearing since D-71.3 (G5)"


# --------------------------------------------------------------------------- #
# G-71.5 -- the fuselage beam waterline reads the moved field
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("path", _EXAMPLES, ids=os.path.basename)
def test_the_fuselage_lra_reads_the_moved_waterline(path):
    from sloads.derived_geometry import fuselage_lra

    project = _project(path)
    outline = project.geometry.fuselage if project.geometry is not None else None
    entered = outline.beam_waterline_z if outline is not None else 0.0
    lra = fuselage_lra(project)
    if entered:
        assert lra.basis == "entered" and lra.z_at(0.0) == pytest.approx(entered)
    else:
        assert lra.basis != "entered"


# --------------------------------------------------------------------------- #
# G-71.6 -- no fixture types a mass quantity apart from its owner
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("path", _EXAMPLES, ids=os.path.basename)
def test_no_fixture_types_a_mass_quantity_apart_from_its_owner(path):
    from sloads.modules.engine import resolved_engines

    project = _project(path)
    if project.speeds is not None:
        assert project.speeds.weight_lb == 0.0, "STRSPEED W derives MTOW"
    lg = project.geometry.landing_gear if project.geometry is not None else None
    if lg is not None and lg.main_gear.weight_lb is not None:
        assert lg.main_gear.weight_lb == 0.0 and lg.nose_gear.weight_lb == 0.0
    for raw, resolved in zip(project.engines, resolved_engines(project)):
        if raw.engine_mass_item:
            assert raw.engine_weight_lb == 0.0 and resolved.engine_weight_lb > 0.0
        if raw.prop_mass_item:
            assert raw.prop_weight_lb == 0.0 and resolved.prop_weight_lb > 0.0
    vt = project.geometry.empennage.vtail if project.geometry and project.geometry.empennage else None
    assert vt is None or not hasattr(vt, "gross_weight_lb")


# --------------------------------------------------------------------------- #
# G-71.8 -- the wing spanwise mass figure
# --------------------------------------------------------------------------- #
def test_the_wing_mass_span_figure_is_catalogued_and_integrates_to_the_panel():
    from sloads.derived_geometry import wing_plane
    from sloads.mass_distribution import wing_mass_state
    from sloads.modules.wing_inertia import inertia_units
    from sloads.report import figures as fx
    from sloads.units import UnitSystem

    rows = {f.key: f for f in fx.families_for_step("wing_loads")}
    assert "wing_mass_span" in rows and rows["wing_mass_span"].stage is fx.Stage.PRE_RUN
    for path in _EXAMPLES:
        project = _project(path)
        built = {figure.key: figure for _family, figure in
                 fx.build_step_figures("wing_loads", project, system=UnitSystem.IMPERIAL, results=None)}
        figure = built["wing_mass_span"]
        assert figure.data is not None or figure.absent_reason, path
        if figure.data is None:
            continue
        curves = [s for s in figure.data.series if not s.marker]
        assert curves, path
        name = project.wing_mass.surface
        surface = project.geometry.by_name(name)
        state = wing_mass_state(project, None)
        units = inertia_units(surface, project.wing_mass, *wing_plane(project, name),
                              panel_weight_lb=state.panel_weight_lb,
                              point_masses=state.point_masses)
        # The density curve integrates back to the strip masses it was drawn from.
        for curve in curves:
            ye = list(units.ye)
            widths = [abs(b - a) for a, b in zip(ye, ye[1:])] + [abs(ye[-1] - ye[-2])]
            total = math.fsum(d * w for d, w in zip(curve.y, widths))
            assert total > 0.0
        points = [s for s in figure.data.series if s.marker]
        if state.point_masses:
            assert points and points[0].sizes and len(points[0].sizes) >= len(state.point_masses)
        assert "Not a load" in figure.caption


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
