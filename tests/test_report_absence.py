"""A stated absence says why, and nothing is absent silently (#316).

G-OR-7 keeps a half-filled project building a complete document and package.
Before #316 about twenty handlers in the report and package paths caught
``Exception``, and ``NonFiniteValue`` was a ``ValueError``, so a NaN on its way
into a delivered cell, or a calc defect, shipped as a short document or a
package missing one file, with no message anywhere. Now:

* a report or package path reads only ``sloads.models.REFUSALS`` as an absence:
  ``MissingInputError`` (the inputs are not there) and a plain ``ValueError``
  (they are there and the calc refused them -- a curve half entered, #71);
* a section absent by a ``ValueError`` states the module's own message, never
  "the inputs are not present";
* anything else, ``NonFiniteValue`` included, stops the build by name.

Two gates. **Static:** no handler under ``sloads/report/`` or ``sloads/export/``
can catch ``NonFiniteValue`` -- no bare ``except``, no ``Exception`` or
``BaseException``, and ``NonFiniteValue`` named only to re-raise it with the
file it was bound for. **Dynamic:** the three rules above, each injected.
"""

from __future__ import annotations

import ast
import math
import os
import re
import sys

import pytest

from sloads.models import REFUSALS
from sloads.report.render import NonFiniteValue, format_value

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCOPE = ("sloads",)
_BROAD = {"Exception", "BaseException"}
#: The on-line exemption a broad handler must carry, followed by its reason
#: (#330): the registry's run-all, which returns each failure with the module's
#: name, and typing introspection, where no calc runs.
_EXEMPT = re.compile(r"#\s*broad-except:\s*\S")


def _names(node: ast.expr | None) -> list[str]:
    """The exception class names a handler's type expression lists."""
    if node is None:
        return []
    items = node.elts if isinstance(node, ast.Tuple) else [node]
    return [i.id if isinstance(i, ast.Name) else i.attr if isinstance(i, ast.Attribute) else ""
            for i in items]


def _reraises(handler: ast.ExceptHandler) -> bool:
    return len(handler.body) == 1 and isinstance(handler.body[0], ast.Raise)


def _offenders() -> list[str]:
    out = []
    for scope in _SCOPE:
        for root, _dirs, files in os.walk(os.path.join(_REPO, scope)):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as fh:
                    source = fh.read()
                lines = source.splitlines()
                tree = ast.parse(source, path)
                rel = os.path.relpath(path, _REPO)
                for node in ast.walk(tree):
                    if not isinstance(node, ast.ExceptHandler):
                        continue
                    names = _names(node.type)
                    if node.type is None:
                        out.append(f"{rel}:{node.lineno}: bare except")
                    elif _BROAD & set(names) and not _EXEMPT.search(lines[node.lineno - 1]):
                        out.append(f"{rel}:{node.lineno}: except {'/'.join(sorted(_BROAD & set(names)))}")
                    elif "NonFiniteValue" in names and not _reraises(node):
                        out.append(f"{rel}:{node.lineno}: NonFiniteValue caught and not re-raised")
    return out


def test_no_handler_in_sloads_can_swallow_a_calc_defect():
    """The static half: every handler in ``sloads/`` is narrower than
    ``Exception`` (#316 for the report and export paths, #330 for the rest),
    unless it carries a ``# broad-except: <reason>`` on its line."""
    offenders = _offenders()
    assert not offenders, (
        "a handler in sloads/ can swallow a NaN or a calc defect (#316, #330); catch "
        "MissingInputError (a stated absence) or the specific refusal instead:\n  "
        + "\n  ".join(offenders))


def test_non_finite_value_is_not_a_value_error():
    """The ~30 handlers that catch ``ValueError`` for a declined geometry must
    not catch a NaN; the class hierarchy is what guarantees it, not each site."""
    assert not issubclass(NonFiniteValue, ValueError)
    assert not issubclass(NonFiniteValue, REFUSALS)
    with pytest.raises(NonFiniteValue):
        try:
            format_value(math.nan, "lb")
        except ValueError:          # the shape of every narrowed handler
            pytest.fail("a ValueError handler caught a NonFiniteValue")


@pytest.fixture(scope="module")
def _ga6_doc():
    from sloads.io import load_project
    from sloads.models.report import ReportSpec
    from sloads.report import oracle_content as oc

    project = load_project(os.path.join(_REPO, "examples", "ga6_normal.project.json"))
    return oc.build_oracle_document(project, ReportSpec())


def test_a_nan_in_a_named_file_stops_the_package_naming_the_file(_ga6_doc, monkeypatch):
    """``package_data.add`` used to drop the file silently."""
    from sloads.report import oracle_sections, package_data

    def poisoned(_project, header, **_kw):
        return header + "\n" + format_value(math.nan, "lb") + "\n"

    monkeypatch.setattr(oracle_sections, "vn_conditions_csv", poisoned)
    with pytest.raises(NonFiniteValue, match=r"data/.*: a delivered lb cell is nan"):
        package_data.data_files(_ga6_doc)


def test_a_nan_in_a_module_result_stops_the_package_naming_the_file(_ga6_doc, monkeypatch):
    """The per-module load-case files: the loop that skipped a failing file."""
    from sloads.report import package_data

    value = _ga6_doc.results["flight_envelope"].conditions[0].values[0]
    monkeypatch.setattr(value, "value", math.nan)
    with pytest.raises(NonFiniteValue, match=r"data/load_cases/flight_envelope\.csv"):
        package_data.data_files(_ga6_doc)


def test_a_producer_defect_is_not_an_absent_file(_ga6_doc, monkeypatch):
    """An exception outside ``REFUSALS`` is a defect, never an absent file: it
    propagates out of the package build."""
    from sloads.report import oracle_sections, package_data

    def broken(_project, _header, **_kw):
        raise KeyError("a calc defect")

    monkeypatch.setattr(oracle_sections, "vn_conditions_csv", broken)
    with pytest.raises(KeyError, match="a calc defect"):
        package_data.data_files(_ga6_doc)


def _run_with(monkeypatch, exc: BaseException):
    """``run_sections`` on ga6_normal with ``flight_envelope`` raising ``exc``."""
    from sloads import registry
    from sloads.io import load_project
    from sloads.models.report import ReportSpec
    from sloads.report import oracle_content as oc

    real = registry.get

    def get(name):
        if name == "flight_envelope":
            def broken(_project):
                raise exc
            return broken
        return real(name)

    monkeypatch.setattr(registry, "get", get)
    project = load_project(os.path.join(_REPO, "examples", "ga6_normal.project.json"))
    spec = ReportSpec()
    results = oc.run_sections(project, spec)
    return oc.section_plan(project, spec, results=results)


def test_a_refused_input_is_an_absent_section_that_says_so(monkeypatch):
    """A plain ``ValueError`` is present input the module refused: the section
    is ``ABSENT`` (a report built mid-entry still builds) and its reason is the
    module's message -- never "the inputs are not present", which is false."""
    from sloads.report import oracle_content as oc

    plan = _run_with(monkeypatch, ValueError("aileron area must be positive"))
    entry = next(e for e in plan if e.step_key == "flight_envelope")
    assert entry.state is oc.SectionState.ABSENT
    assert entry.reason == (f"{oc.REFUSED_REASON} aileron area must be positive.")
    assert oc.STATE_REASON[oc.SectionState.ABSENT] not in entry.reason


@pytest.mark.parametrize("exc", [KeyError("a calc defect"), ZeroDivisionError("a calc defect"),
                                 NonFiniteValue("a delivered lb cell is nan")],
                         ids=["KeyError", "ZeroDivisionError", "NonFiniteValue"])
def test_a_module_defect_is_not_an_absent_section(monkeypatch, exc):
    """Anything that is not one of the two refusals stops the build by name."""
    with pytest.raises(type(exc)):
        _run_with(monkeypatch, exc)


# --------------------------------------------------------------------------- #
# #330 -- a divisor an input can zero is refused by name where it divides
# --------------------------------------------------------------------------- #
def _ga6():
    from sloads.io import load_project

    return load_project(os.path.join(_REPO, "examples", "ga6_normal.project.json"))


def _blank_htail(project):
    project.geometry.empennage.htail = type(project.geometry.empennage.htail)()


def _blank_gear(project):
    project.geometry.landing_gear = type(project.geometry.landing_gear)()


def _no_negative_stall(project):
    project.aero_coeffs.cruise.neg_stall_cl = 0.0


@pytest.mark.parametrize("blank,build,names", [
    (_blank_htail, "select", "elevator_effectiveness"),
    (_blank_gear, "landing", "axle compressed"),
    (_no_negative_stall, "flight_envelope", "negative stall CL"),
], ids=["blank h-tail record", "blank landing-gear record", "no negative stall CL"])
def test_a_zeroed_divisor_is_refused_by_name(blank, build, names):
    """Each was a bare ``ZeroDivisionError`` -- a GUI "Add" of the h-tail or gear
    record, a cruise set with no negative stall CL -- which since #316 stopped
    the whole report with a message that named nothing."""
    from sloads.models import MissingInputError
    from sloads.modules.flight_envelope import build_envelope
    from sloads.modules.landing import ground_angles
    from sloads.modules.select import default_critical

    project = _ga6()
    blank(project)
    with pytest.raises(MissingInputError, match=names):
        if build == "select":
            default_critical(project)
        elif build == "landing":
            ground_angles(project.landing, project.geometry.landing_gear)
        else:
            build_envelope(project)


def test_the_weight_warnings_withhold_only_on_a_refusal(monkeypatch):
    """``validation``'s mass-state check reads a refusal as "nothing to name"
    (the module states it on its page); a defect raises (#330)."""
    from sloads import validation
    from sloads.modules import wing_inertia

    project = _ga6()
    _blank_htail(project)
    validation.consistency_warnings(project)          # a refusal: no raise

    def broken(*_a, **_kw):
        raise ZeroDivisionError("a calc defect")

    monkeypatch.setattr(wing_inertia, "resolve_mass_case", broken)
    project = _ga6()
    assert project.wing_mass and project.wing_mass.cases, "nothing to resolve: the test proves nothing"
    with pytest.raises(ZeroDivisionError, match="a calc defect"):
        validation.consistency_warnings(project)


@pytest.mark.parametrize("exc,raises", [("refusal", False), ("defect", True)])
def test_the_fleet_fallback_is_taken_only_on_a_refusal(monkeypatch, exc, raises):
    """``fleet._wtestima_value`` falls back on a refusal and raises on a
    defect, which it used to turn into a quiet change of source (#330)."""
    from sloads import fleet, registry
    from sloads.models import MissingInputError

    project = _ga6()
    assert project.weight and project.weight.estimation, "no WTESTIMA inputs: the test proves nothing"
    err = MissingInputError("not entered") if exc == "refusal" else KeyError("a calc defect")

    def broken(_project):
        raise err

    real = registry.get
    monkeypatch.setattr(registry, "get",
                        lambda name: broken if name == "weight_estimate" else real(name))
    if raises:
        with pytest.raises(KeyError, match="a calc defect"):
            fleet._wtestima_value(project, "max_take_off_weight")
    else:
        assert fleet._wtestima_value(project, "max_take_off_weight") is None


def _optional_blocks():
    """Every Optional record block the GUI can add, read as ``test_oracle_gui``
    reads it -- so a new one joins this sweep the day it is registered."""
    from oracle_app.form import optional_steps, page_groups
    from sloads import field_registry as fr
    from sloads import workflow as wf

    seen, out = set(), []
    for key in sorted(wf.oracle_step_keys()):
        for prefix, _paths in page_groups(key):
            if prefix.endswith(fr.LIST_MARKER) or prefix in seen:
                continue
            if optional_steps(prefix):
                seen.add(prefix)
                out.append(prefix)
    return out


@pytest.mark.slow
@pytest.mark.parametrize("prefix", _optional_blocks())
def test_a_freshly_added_record_leaves_the_report_building(prefix):
    """The GUI's "Add" of any Optional record puts it at its blank defaults;
    the document and the package still build over it (G-OR-7, #71), each gap a
    stated refusal (#330). Measured on all five examples at the close; run on
    ga6_normal here."""
    import typing

    from sloads.models.report import ReportSpec
    from sloads.report import oracle_content as oc
    from sloads.report import package_data

    project = _ga6()
    *head, attr = prefix.split(".")
    parent = project
    for part in head:
        parent = getattr(parent, part)
        if parent is None:
            pytest.skip(f"ga6_normal enters no {part}")
    hint = typing.get_type_hints(type(parent))[attr]
    cls = next((a for a in typing.get_args(hint) if a is not type(None)), hint)
    try:
        blank = cls()
    except TypeError:
        pytest.skip(f"{cls.__name__} has no blank default (required fields)")
    setattr(parent, attr, blank)
    package_data.data_files(oc.build_oracle_document(project, ReportSpec()))


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-n", "0", "-q"]))
