"""A refused input is stated as a refusal, not reported as something else (#361).

The #344 sweep made every silent ``ValueError`` catch say why silence is right.
It found four places where the silence was not right, because the refusal was
then reported as a *different* fact:

1. a present-but-unintegrable wing raised the absent wing's "add the surface"
   (``derived_geometry.require_wing_reference``);
2. FLAPLOAD's gust factor fell back to NG = 0 with no warning, although
   ``flap.resolved_ng`` promised one -- live on ``atr42_100``, which enters no
   NG and has no flaps-down coefficient set;
3. the tail, control-surface and Appendix A sections said "not entered" for
   inputs that were entered and refused;
4. two statements under the 2.2 case table vanished when their owner refused.
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import derived_geometry
from sloads.io import load_project
from sloads.models import MissingInputError
from sloads.modules import flap as flap_module
from sloads.modules import select as select_module
from sloads.modules import tail_span as tail_span_module
from sloads.modules import taildist as taildist_module
from sloads.report import oracle_sections as sections
from sloads.report.content import Units
from sloads.report.oracle_content import REFUSED_REASON
from sloads.units import UnitSystem
from sloads.validation import consistency_warnings

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PLANTED = "planted refusal for #361"


def _example(name):
    return load_project(os.path.join(_ROOT, "examples", f"{name}.project.json"))


class _Patched:
    """Swap one module attribute for a function that raises ``exc``, then restore."""

    def __init__(self, module, name, exc):
        self.module, self.name, self.exc = module, name, exc

    def __enter__(self):
        self.saved = getattr(self.module, self.name)

        def _raise(*_a, **_k):
            raise self.exc
        setattr(self.module, self.name, _raise)

    def __exit__(self, *_exc):
        setattr(self.module, self.name, self.saved)


# --- 1. a broken wing is not a missing one ----------------------------------

def test_an_unintegrable_wing_refuses_with_the_planforms_own_message():
    project = copy.deepcopy(_example("ga6_normal"))
    wing = project.geometry.by_name("wing")
    wing.leading_edge = wing.leading_edge[:1]
    try:
        derived_geometry.require_wing_reference(project)
    except MissingInputError as exc:
        raise AssertionError(f"a broken wing was reported as absent: {exc}") from exc
    except ValueError as exc:
        assert "LE and TE points" in str(exc)
        assert "add the surface" not in str(exc)
    else:
        raise AssertionError("an unintegrable wing was not refused")
    # The non-raising read keeps its contract: no reference.
    assert derived_geometry.wing_reference(project) is None


def test_an_absent_wing_is_still_missing():
    project = copy.deepcopy(_example("ga6_normal"))
    project.geometry.surfaces = [s for s in project.geometry.surfaces if s.name != "wing"]
    try:
        derived_geometry.require_wing_reference(project)
    except MissingInputError as exc:
        assert "add the surface" in str(exc)
    else:
        raise AssertionError("an absent wing was not refused")


# --- 2. the flap gust factor's fallback is stated ---------------------------

def test_the_atr_flap_ng_fallback_is_warned_and_stated_in_band():
    project = _example("atr42_100")
    reason = flap_module.ng_fallback_reason(project)
    assert reason is not None and "no flaps-down aerodynamic coefficient set" in reason
    warned = [w for w in consistency_warnings(project) if w.code == "flap_ng_fallback"]
    assert len(warned) == 1 and reason in warned[0].message
    note = flap_module.run(project).conditions[0].note
    assert reason in note


def test_a_typed_or_derived_ng_is_not_a_fallback():
    for name in ("ga6_normal", "baron_58", "concept_regional_jet"):
        project = _example(name)
        assert flap_module.ng_fallback_reason(project) is None, name
        assert not [w for w in consistency_warnings(project) if w.code == "flap_ng_fallback"], name
    project = copy.deepcopy(_example("atr42_100"))
    project.flap_loads.gust_load_factor = 1.6
    assert flap_module.ng_fallback_reason(project) is None


def test_the_atr_flap_load_does_not_move_with_the_fallback():
    """The measurement behind ruling (a): on the ATR the 2g condition at VF
    governs at NG = 0 and at the flaps-up-slope estimate alike, so the
    fallback is a statement, not a load."""
    key = "critical_flap_load_23_345_a"
    project = copy.deepcopy(_example("atr42_100"))
    at_zero = {v.key: v.value for v in flap_module.run(project).conditions[0].values}
    project.flap_loads.gust_load_factor = 1.6422
    at_est = {v.key: v.value for v in flap_module.run(project).conditions[0].values}
    assert at_zero[key] == at_est[key]


# --- 3. a refused section says so --------------------------------------------

def test_a_refused_tail_section_quotes_the_refusal():
    project = _example("ga6_normal")
    with _Patched(taildist_module, "build_tail_chordwise", ValueError(_PLANTED)):
        section = sections._tail_chordwise_section(project, "htail",
                                                   system=UnitSystem.IMPERIAL, plan=[])
    assert section.absent_reason.startswith(REFUSED_REASON)
    assert _PLANTED in section.absent_reason and "not entered" not in section.absent_reason
    with _Patched(tail_span_module, "build_tail_span", ValueError(_PLANTED)):
        for build in (sections._tail_span_section, sections._tail_station_appendix):
            section = build(project, "vtail", system=UnitSystem.IMPERIAL, plan=[])
            assert section.absent_reason.startswith(REFUSED_REASON), build.__name__
            assert _PLANTED in section.absent_reason, build.__name__


def test_an_absent_input_keeps_its_not_entered_wording():
    project = _example("ga6_normal")
    with _Patched(taildist_module, "build_tail_chordwise", MissingInputError(_PLANTED)):
        section = sections._tail_chordwise_section(project, "htail",
                                                   system=UnitSystem.IMPERIAL, plan=[])
    assert not section.absent_reason.startswith(REFUSED_REASON)
    assert "not entered" in section.absent_reason


def test_a_refused_control_section_quotes_the_refusal():
    project = _example("ga6_normal")
    with _Patched(flap_module, "build_flap", ValueError(_PLANTED)):
        section = sections._flap_loads(project, {}, system=UnitSystem.IMPERIAL, plan=[])
    assert section.absent_reason.startswith(REFUSED_REASON)
    assert _PLANTED in section.absent_reason


def test_appendix_a_names_the_selection_not_the_envelope():
    project = _example("ga6_normal")
    with _Patched(select_module, "default_critical", ValueError(_PLANTED)):
        section = sections._vn_appendix(project, system=UnitSystem.IMPERIAL, plan=[])
    assert section.absent_reason.startswith(REFUSED_REASON)
    assert "critical-condition selection" in section.absent_reason
    assert "flight envelope refused" not in section.absent_reason
    with _Patched(select_module, "default_envelope", ValueError(_PLANTED)):
        section = sections._vn_appendix(project, system=UnitSystem.IMPERIAL, plan=[])
    assert "the flight envelope refused its inputs" in section.absent_reason


# --- 4. a refused statement is replaced, not dropped ------------------------

def test_the_case_table_statements_state_a_refusal():
    from sloads import mass_distribution

    project = _example("ga6_normal")
    u = Units(UnitSystem.IMPERIAL)
    with _Patched(mass_distribution, "case_loading_checks", ValueError(_PLANTED)):
        text = sections._case_loading_statement(project, u)
    assert text.startswith("Whether each case is a loading") and _PLANTED in text
    with _Patched(mass_distribution, "envelope_point_reach", ValueError(_PLANTED)):
        text = sections._envelope_reach_statement(project, u)
    assert text.startswith("Whether each entered CG limit") and _PLANTED in text
    with _Patched(mass_distribution, "envelope_point_reach", MissingInputError(_PLANTED)):
        assert sections._envelope_reach_statement(project, u) == ""


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
