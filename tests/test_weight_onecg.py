"""Validate WTONECG against the FAR 23 LOADS manual, Appendix A.

The worked example is the 6-place single's *aft gross weight* loading, whose
weight/CG/inertia report is printed in Appendix A p136. The itemized weight data
base is carried in ``examples/ga6_normal.project.json`` (the same file the engine
example uses), so this test exercises the JSON load path as well as the calc.

Per Decision 3 ("modernize the math", g kept at 32.174) the slug-ft^2 figures are
matched within ±0.1% of the manual's printed numbers; the lb-in^2 accumulator and
the weight are g-independent.
"""

import glob
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from helpers import value_of

from sloads import MassResult, Project, WeightInput, io
from sloads.modules import weight_onecg as calc

TOL = 1e-3  # ±0.1% relative

_EXAMPLE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "examples",
    "ga6_normal.project.json",
)


def aft_gross_result():
    project = io.load_project(_EXAMPLE)
    return calc.weights_and_inertia(project.weight.items)


def test_weight_and_cg_match_manual():
    # Appendix A p136 (aft gross weight CG): WEIGHT 3400, XBAR 84.99936,
    # ZBAR 92.57932.
    r = aft_gross_result()
    assert value_of(r, "weight") == 3400
    assert math.isclose(value_of(r, "xbar_fus_station"), 84.99936, rel_tol=TOL)
    assert math.isclose(value_of(r, "zbar_waterline"), 92.57932, rel_tol=TOL)


def test_inertias_airplane_axes_match_manual():
    # Appendix A p136, slug-ft^2: IXX 1201.527, IYY 2058.209, IZZ 3022.766,
    # IXZ 134.4063.
    r = aft_gross_result()
    assert math.isclose(value_of(r, "ixx"), 1201.527, rel_tol=TOL)
    assert math.isclose(value_of(r, "iyy"), 2058.209, rel_tol=TOL)
    assert math.isclose(value_of(r, "izz"), 3022.766, rel_tol=TOL)
    assert math.isclose(value_of(r, "ixz"), 134.4063, rel_tol=TOL)


def test_inertias_lb_in2_match_manual():
    # Appendix A p136, lb-in^2: IXX 5566051, IYY 9534613, IZZ 14002901, IXZ 622634.
    r = aft_gross_result()
    assert math.isclose(value_of(r, "ixx_lb_in_2"), 5566051, rel_tol=TOL)
    assert math.isclose(value_of(r, "iyy_lb_in_2"), 9534613, rel_tol=TOL)
    assert math.isclose(value_of(r, "izz_lb_in_2"), 14002901, rel_tol=TOL)
    assert math.isclose(value_of(r, "ixz_lb_in_2"), 622634, rel_tol=TOL)


def test_principal_axes_match_manual():
    # Appendix A p136: IX(P) 1191.662, IY(P) 2058.209, IZ(P) 3032.632,
    # theta 4.198392 deg.
    r = aft_gross_result()
    assert math.isclose(value_of(r, "ix_p_principal"), 1191.662, rel_tol=TOL)
    assert math.isclose(value_of(r, "iy_p_principal"), 2058.209, rel_tol=TOL)
    assert math.isclose(value_of(r, "iz_p_principal"), 3032.632, rel_tol=TOL)
    assert math.isclose(value_of(r, "principal_axis_angle_theta"), 4.198392, rel_tol=2e-3)


def test_wtonecg_states_the_share_each_inertia_takes_from_the_rows_own():
    """#385 (review A5): the ga6 oracle depends on its rows' own inertias;
    an airplane whose rows carry none is a transfer-only answer, and the
    module says which. The share is stated per axis, in percent."""
    r = aft_gross_result()
    own = {axis: value_of(r, f"{axis}_own_inertia_share") for axis in ("ixx", "iyy", "izz")}
    assert all(0.0 < s < 100.0 for s in own.values()), own
    project = io.load_project(_EXAMPLE)
    rows = project.weight.items
    expected = math.fsum(it.ixx for it in rows) / value_of(r, "ixx_lb_in_2") * 100.0
    assert math.isclose(own["ixx"], expected, rel_tol=1e-9)
    for it in rows:
        it.ixx = it.iyy = it.izz = 0.0
    bare = calc.weights_and_inertia(rows)
    assert all(value_of(bare, f"{axis}_own_inertia_share") == 0.0 for axis in ("ixx", "iyy", "izz"))
    # The share is a diagnostic, never a load: no factor, no -ULT marker.
    assert all(v.quantity == "diagnostic" for v in r.values if v.key.endswith("_own_inertia_share"))


def test_run_requires_items():
    raised = False
    try:
        calc.run(Project(name="no items", weight=WeightInput()))
    except ValueError:
        raised = True
    assert raised


def test_build_mass_persists_properties_and_round_trips():
    # build_mass emits the persisted Project.mass slice (R7): weight/CG/inertia in
    # lb-in^2, matching the WTONECG result and surviving the io round-trip. The
    # Appendix A row is the ceiling row, last (design note 70 D-70.1/D-70.9).
    project = io.load_project(_EXAMPLE)
    mass = calc.build_mass(project)
    assert len(mass.cases) == len(project.weight.cg_cases) + 1
    c = mass.cases[-1]
    assert c.ceiling and c.name == calc.CEILING_TITLE
    assert c.weight_lb == 3400
    assert math.isclose(c.cg_x, 84.99936, rel_tol=TOL)
    assert math.isclose(c.iyy, 9534613, rel_tol=TOL)
    assert math.isclose(c.izz, 14002901, rel_tol=TOL)

    project.mass = mass
    rebuilt = io.project_from_dict(io.project_to_dict(project))
    assert rebuilt.mass is not None
    assert math.isclose(rebuilt.mass.cases[-1].iyy, c.iyy, rel_tol=1e-9)
    assert rebuilt.mass.cases[-1].ceiling and not rebuilt.mass.cases[0].ceiling


# --------------------------------------------------------------------------- #
# Design note 70: one row per CG case, the ceiling last
# --------------------------------------------------------------------------- #
_EXAMPLES = sorted(glob.glob(os.path.join(os.path.dirname(_EXAMPLE), "*.project.json")))


def test_the_ceiling_row_run_emits_is_the_appendix_a_oracle():
    """G-70.1: the p136 figures are the all-items sum, and that sum is the one
    condition titled as the ceiling -- last, never first."""
    project = io.load_project(_EXAMPLE)
    conditions = calc.run(project).conditions
    assert conditions[-1].title == calc.CEILING_TITLE
    assert sum(c.title == calc.CEILING_TITLE for c in conditions) == 1
    oracle = {v.key: v.value for v in aft_gross_result().values}
    got = {v.key: v.value for v in conditions[-1].values}
    for key in ("weight", "xbar_fus_station", "zbar_waterline", "ixx", "iyy", "izz", "ixz"):
        assert got[key] == oracle[key], key
    assert math.isclose(got["ixx"], 1201.527, rel_tol=TOL)


@pytest.mark.parametrize("path", _EXAMPLES, ids=os.path.basename)
def test_every_case_row_is_wtonecg_over_that_cases_loading_of_record(path):
    """G-70.2 (identity, not closeness): each row's weight and CG are the
    ``CaseLoading``'s own, its inertias are ``weights_and_inertia`` over that
    loading's items, in case order; G-70.4: the ceiling is last and heaviest,
    and a case that derives no loading is stated, never invented."""
    from sloads.mass_distribution import derive_case_loadings

    project = io.load_project(path)
    props = calc.case_mass_properties(project)
    rows, conditions = props.rows, props.conditions
    assert len(rows) == len(conditions)
    assert rows[-1].ceiling and conditions[-1].title == calc.CEILING_TITLE
    assert all(not r.ceiling for r in rows[:-1])
    assert all(rows[-1].weight_lb >= r.weight_lb for r in rows)
    cases = list(project.weight.cg_cases)
    loadings = {ld.name: ld for ld in derive_case_loadings(project, cases)}
    expected = [c.name for c in cases if loadings[c.name].derivable]
    assert [r.name for r in rows[:-1]] == expected
    skipped = dict(props.skipped)
    assert set(skipped) == {c.name for c in cases if not loadings[c.name].derivable}
    assert all(why for why in skipped.values())
    for row, cond in zip(rows[:-1], conditions[:-1]):
        ld = loadings[row.name]
        v = {x.key: x.value for x in calc.weights_and_inertia(list(ld.items)).values}
        assert cond.title == f"Mass properties -- {row.name}"
        assert row.weight_lb == v["weight"] and row.cg_x == v["xbar_fus_station"]
        assert math.isclose(row.weight_lb, ld.weight_lb, rel_tol=1e-9)
        assert math.isclose(row.cg_x, ld.cg_x, rel_tol=1e-9)
        assert math.isclose(row.cg_z, ld.cg_z, rel_tol=1e-9)
        assert (row.ixx, row.iyy, row.izz, row.ixz) == (
            v["ixx_lb_in_2"], v["iyy_lb_in_2"], v["izz_lb_in_2"], v["ixz_lb_in_2"])
        assert row.gear_down is True
    if skipped:
        note = calc.run(project).conditions[-1].note
        for name in skipped:
            assert f"'{name}'" in note


def test_the_baron_fwd_regardless_case_derives_no_row_and_says_why():
    """G-70.4 on the fixture that has the case: ``baron_58``'s ``fwd
    regardless`` loading cannot be produced from its data base."""
    project = io.load_project(os.path.join(os.path.dirname(_EXAMPLE), "baron_58.project.json"))
    props = calc.case_mass_properties(project)
    assert "fwd regardless" not in {r.name for r in props.rows}
    assert "fwd regardless" in dict(props.skipped)
    assert "not a loading this weight database can produce" in dict(props.skipped)["fwd regardless"]


def test_the_basis_row_is_the_mass_basis_flight_case_then_a_case_then_the_ceiling():
    """D-70.4/D-70.5: the one representative row every single-CG reader takes."""
    project = io.load_project(os.path.join(os.path.dirname(_EXAMPLE), "atr42_100.project.json"))
    mass = calc.build_mass(project)
    row = calc.basis_row(mass, project)
    assert row is not None and row.name == "aft gross" and not row.ceiling
    only_ceiling = MassResult(cases=[c for c in mass.cases if c.ceiling])
    assert calc.basis_row(only_ceiling, project).ceiling
    assert calc.basis_row(None, project) is None
    assert calc.basis_row(MassResult(cases=[]), project) is None


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
