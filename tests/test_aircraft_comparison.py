"""Unit test for the comparison **subject**'s priority chain.

The Aircraft Comparison page builds its :class:`~sloads.fleet.Subject` from
whichever project slices are present, with a documented priority per metric
(backlog F2 step 2). The chain moved out of the page and into its owner at
**#268** (note 57 D-57.5): it is not presentation, it has a defect history of
its own, and D-57.5's *rewritten, not imported* would have rewritten the fix
with it. These tests are unchanged in what they assert and now call the owner
directly -- no Streamlit import, no view module executed in bare mode.

The figures and the pages that draw them are ``tests/test_fleet_figures.py``.
"""

import os

import pytest

from sloads.fleet import subject_from_project

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLE = os.path.join(_ROOT, "examples", "ga6_normal.project.json")


def test_subject_from_example_project():
    # The GA-6 example carries a design weight (speeds) + installed power (engines)
    # and no parametric layout, but it *does* carry a WINGGEOM wing surface -- so the
    # geometric axes (area/AR/span) resolve from the surface fallback (M2-5), and the
    # subject is fully placed.
    from sloads import io
    subject = subject_from_project(io.load_project(_EXAMPLE))
    assert subject is not None
    assert subject.mtow_lb > 0
    assert subject.power_hp and subject.power_hp > 0


def test_subject_geometric_axes_from_wing_surface():
    # M2-5: a project with geometry.surfaces (WINGGEOM planform) but no parametric
    # layout resolves wing area, aspect ratio and span from the wing surface. The GA-6
    # example carries no speeds.wing_area_sqft, so W/S is *only* computable via this
    # fallback. The recovered AR/span match the Appendix A wing (AR 6.095, span 33.5 ft).
    import math

    from sloads import io
    subject = subject_from_project(io.load_project(_EXAMPLE))
    assert subject.wing_area_ft2 and subject.wing_area_ft2 > 0
    assert subject.w_s and subject.w_s > 0
    assert math.isclose(subject.aspect_ratio_effective, 6.095, rel_tol=1e-3)
    assert subject.span is not None and math.isclose(subject.span, 33.5, rel_tol=1e-2)


def test_area_priority_surface_over_speeds():
    # M2-5 priority: parametric -> surface -> speeds. When a project has both a
    # WINGGEOM wing surface and a scalar speeds.wing_area_sqft (and no parametric),
    # the computed planform wins.
    from sloads import io
    project = io.load_project(os.path.join(_ROOT, "examples", "atr42_100.project.json"))
    assert project.speeds.wing_area_sqft  # the fixture carries a scalar area
    # Since #268 the planform is read through ``derived_geometry``'s resolvers
    # -- the single owner of *what area the analysis actually uses* (#70) --
    # rather than off ``surface_properties`` here, so the comparison is against
    # that owner and the page is no longer a fifth place holding a wing area.
    from sloads.derived_geometry import planform_area_sqft
    resolved = planform_area_sqft(project)
    assert resolved
    subject = subject_from_project(project)
    # ``approx``, not ``==``: the two reach the same area by different arithmetic
    # and closed-form planform integration (2026-08-30) put a last-ulp gap
    # between them. Exact float equality across two code paths was never the
    # property under test -- that the subject reads the planform and not the
    # scalar is, and the line below is what says so.
    assert subject.wing_area_ft2 == pytest.approx(resolved, rel=1e-12)
    assert subject.wing_area_ft2 != project.speeds.wing_area_sqft


def test_subject_geometric_axes_from_configuration():
    # A project with a configuration slice resolves wing area + AR, and the subject's
    # span derives from sqrt(AR * S) even with no explicitly stored span.
    from sloads import (
        EngineInput,
        GeometryInput,
        LayoutInput,
        Project,
        StructuralSpeedsInput,
    )
    project = Project(
        name="Synthetic",
        geometry=GeometryInput(parametric=LayoutInput(wing_area_sqft=180.0, aspect_ratio=7.5)),
        speeds=StructuralSpeedsInput(weight_lb=2450.0),
        engines=[EngineInput(max_cont_hp=180.0)],
    )
    subject = subject_from_project(project)
    assert subject is not None
    assert subject.mtow_lb == 2450.0
    assert subject.wing_area_ft2 == 180.0
    assert subject.power_hp == 180.0
    assert subject.aspect_ratio_effective == 7.5
    assert subject.span is not None and abs(subject.span - (7.5 * 180.0) ** 0.5) < 1e-9


def test_subject_is_none_without_mtow():
    from sloads import Project
    assert subject_from_project(Project(name="")) is None


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
    raise SystemExit(1 if failed else 0)
