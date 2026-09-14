"""A number typed into a page reaches the project in Imperial — in both systems.

This is the M4-11 acceptance test the plan calls "the real one"
(``docs/25_notes/07_m4_maintainability_sequence_plan.md`` §4 step 3). A
``unit_number_input`` that converted twice, or in the wrong direction, would
render perfectly and silently corrupt every input on every page.
``test_app_components.py`` pins the helper in isolation; this file pins it
**through a real page**, driven headlessly via ``AppTest`` — the widget, the
form, the Apply handler and the persist path together.

The shape of every case below: run the page in a unit system, type a number into
a field *in that system's display units*, then assert
``st.session_state["project"]`` holds the **Imperial** equivalent. Imperial and
SI runs assert the *same* stored Imperial value from different typed numbers,
which is exactly the property a conversion bug breaks.

**Six per-view cases were deleted at #270** with the front-end they drove: they
covered the same boundary through ``app/views/``' hand-written forms, where each
page converted its own fields and the risk was therefore per page. The surviving
GUI has one generic renderer, so the risk is per *widget kind* and the three
cases below are the whole of it.
"""

import math
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.dirname(os.path.abspath(__file__))):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import logging  # noqa: E402

logging.disable(logging.CRITICAL)  # silence Streamlit's bare-mode warnings

from sloads import UnitSystem  # noqa: E402
from sloads.units import UNIT_LABELS, to_display  # noqa: E402

pytest.importorskip("streamlit.testing.v1")

from helpers import widget_editing  # noqa: E402

_GA6 = os.path.join(_ROOT, "examples", "ga6_normal.project.json")

_SYSTEMS = [UnitSystem.IMPERIAL, UnitSystem.SI]


# --------------------------------------------------------------------------- #
# The same contract through the second GUI (design note 32, OG-F)
# --------------------------------------------------------------------------- #
# The oracle GUI puts all 230 of its fields through the same
# ``unit_number_input`` boundary, from one generic renderer -- so the cases here
# are per *widget kind* rather than per page: a scalar, a member of a composite,
# and a cell of an editable table are the three paths a number can take into the
# project, and each is written once in ``oracle_app/form.py``. A conversion bug
# in any of them is a bug on every page at once, which is the reverse of the
# per-view risk above and needs the reverse of a per-view test.
_ORACLE_SCRIPT = "from oracle_app.form import render_step\nrender_step({key!r})\n"


def _run_oracle(key: str, system: UnitSystem, project):
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string(_ORACLE_SCRIPT.format(key=key), default_timeout=90)
    project.unit_system = system.value
    at.session_state["project"] = project
    at.session_state["unit_system"] = system
    at.run()
    assert not at.exception, [e.message for e in at.exception]
    return at


def _oracle_number(at, path: str):
    """The oracle GUI's number widget for a registry ``path`` (shared helper)."""
    return widget_editing(at, path)


@pytest.mark.parametrize("system", _SYSTEMS, ids=[s.value for s in _SYSTEMS])
def test_an_oracle_scalar_is_stored_imperial_from_either_system(system):
    """A plain number: type 100 in, get 100 in; type 2540 mm, get the same 100 in.

    Driven on the wing area's **owner**. It used to type into
    ``speeds.wing_area_sqft``, which #36 established is display-only — STRSPEED
    resolves the planform and ignores that field — so it now renders disabled and
    a test that typed into it was asserting a conversion no user can perform.
    """
    from sloads import io

    project = io.load_project(_GA6)
    at = _run_oracle("configuration_layout", system, project)
    field = _oracle_number(at, "geometry.parametric.wing_area_sqft")
    assert (UNIT_LABELS[system]["area_sqft"] in (field.label or "")), (
        f"{system.value}: {field.label!r} does not state the active area unit")

    typed = to_display(150.0, "area_sqft", system)
    field.set_value(typed).run()
    stored = at.session_state["project"].geometry.parametric.wing_area_sqft
    assert math.isclose(stored, 150.0, rel_tol=1e-9), (
        f"{system.value}: typed {typed} and stored {stored}, expected 150.0 sq ft")


@pytest.mark.parametrize("system", _SYSTEMS, ids=[s.value for s in _SYSTEMS])
def test_an_oracle_composite_member_is_stored_imperial_from_either_system(system):
    """A member of a ``Tuple[float, float]`` -- the gear axle's (X, Z) station,
    which has no unit suffix in its own name and gets one from the registry.

    Read on **Configuration & Layout**, not Landing Loads: note 33 (DS-1) removed
    the ``landing.main_gear`` copy, so the axle is edited once, where it is stored.
    """
    from sloads import io

    project = io.load_project(_GA6)
    at = _run_oracle("configuration_layout", system, project)
    field = _oracle_number(at, "geometry.landing_gear.main_gear.axle_static.0")

    typed = to_display(120.0, "length", system)
    field.set_value(typed).run()
    stored = (at.session_state["project"]
              .geometry.landing_gear.main_gear.axle_static[0])
    assert math.isclose(stored, 120.0, rel_tol=1e-9), (
        f"{system.value}: typed {typed} and stored {stored}, expected 120.0 in")


def _oracle_keys():
    from sloads import workflow as wf

    return sorted(wf.oracle_step_keys())


@pytest.mark.parametrize("key", _oracle_keys())
def test_an_untouched_oracle_page_stores_exactly_what_it_loaded_in_si(key):
    """The rounding trap, in the GUI that renders every field live.

    ``app/`` gets one shot at this per Apply; the oracle GUI writes on every
    rerun, so a value converted out to SI and straight back would walk the
    project a hair at a time, on every keystroke anywhere on the page. It did:
    ``116 in`` came back as ``115.99999999999999``, on untouched geometry, for
    every SI user. Nothing is typed here at all.

    Every page, and SI only: ``tests/test_dirty_flag.py`` runs the Imperial
    direction over every page and example, and Imperial cannot drift -- its
    conversion is the identity. This is the direction with a factor in it.
    """
    from sloads import io

    project = io.load_project(_GA6)
    project.unit_system = UnitSystem.SI.value  # the selection is itself an edit (D-22)
    before = io.project_to_dict(project)
    at = _run_oracle(key, UnitSystem.SI, project)
    assert io.project_to_dict(at.session_state["project"]) == before, (
        f"rendering {key} in SI changed the project")


if __name__ == "__main__":  # pragma: no cover - needs pytest for parametrize
    raise SystemExit(pytest.main([__file__, "-q"]))
