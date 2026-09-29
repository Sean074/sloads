"""A stated absence says why, and nothing is absent silently (#316).

G-OR-7 keeps a half-filled project building a complete document and package.
Before #316 about twenty handlers in the report and package paths caught
``Exception``, and ``NonFiniteValue`` was a ``ValueError``, so a NaN on its way
into a delivered cell, or a calc defect, shipped as a short document or a
package missing one file, with no message anywhere. Now:

* a report or package path reads only ``render.REFUSALS`` as an absence:
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
import sys

import pytest

from sloads.report.render import REFUSALS, NonFiniteValue, format_value

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCOPE = ("sloads/report", "sloads/export")
_BROAD = {"Exception", "BaseException"}


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
                    tree = ast.parse(fh.read(), path)
                rel = os.path.relpath(path, _REPO)
                for node in ast.walk(tree):
                    if not isinstance(node, ast.ExceptHandler):
                        continue
                    names = _names(node.type)
                    if node.type is None:
                        out.append(f"{rel}:{node.lineno}: bare except")
                    elif _BROAD & set(names):
                        out.append(f"{rel}:{node.lineno}: except {'/'.join(sorted(_BROAD & set(names)))}")
                    elif "NonFiniteValue" in names and not _reraises(node):
                        out.append(f"{rel}:{node.lineno}: NonFiniteValue caught and not re-raised")
    return out


def test_no_report_or_export_handler_can_swallow_a_non_finite_value():
    """The static half: every handler in scope is narrower than ``NonFiniteValue``."""
    offenders = _offenders()
    assert not offenders, (
        "a report/export handler can swallow a NaN or a calc defect (#316); catch "
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


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
