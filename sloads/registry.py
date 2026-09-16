"""Module registry: map a module name to its ``run(project)`` function.

Each suite module calls :func:`register` at import time, so importing
``sloads.modules`` populates the registry. The CLI, GUI "run all" and tests
look modules up here by name instead of importing each one directly -- adding
program #2..#22 is then just a new module file that registers itself.

**Every runner this registry hands out stamps** (#177). A module mints its
conditions' ``safety_factor`` from its own reading of the case; the *governing*
factor is the project's safety-factor table (M4-8 / G-11), and until #177 that
table was applied by the two "run everything" helpers below and nowhere else.
Five callers ran a module without them -- the GUI's per-module blocks, the
oracle report's own run point, the step figures, the engine rows behind the
deck, the fleet view -- so on those surfaces a project override was silently
ignored and a condition that prescribes no factor kept the dataclass 1.5
instead of the stamped ``None`` (#154 surviving one surface at a time). Rather
than stamp at five call sites and wait for a sixth, :func:`register` wraps the
runner: the factor is applied where the runner is *handed out*, so an unstamped
render is not something a caller can choose. Guard:
``tests/test_safety_factors.py::test_no_module_runner_is_reachable_unstamped``.
"""

from __future__ import annotations

from functools import wraps
from typing import Callable, Dict, List, Tuple

from .models import MissingInputError, ModuleResult, Project

RunFn = Callable[[Project], ModuleResult]

_REGISTRY: Dict[str, RunFn] = {}


def _stamping(fn: RunFn) -> RunFn:
    """``fn``, with the project's governing table written onto what it returns.

    The wrapper is thin on purpose: it neither classifies nor renders, it only
    makes sure the one owner of the policy has been past the result before any
    caller sees it. Stamping is idempotent -- the table is a pure function of
    the project -- so a caller that stamps again (``report.content`` stamps its
    own assembled groups) is not fighting this.
    """

    @wraps(fn)
    def run(project: Project) -> ModuleResult:
        from .safety_factors import stamp

        result = fn(project)
        stamp(project, result.conditions)
        return result

    return run


def register(name: str, fn: RunFn) -> None:
    """Register ``fn`` as the runner for module ``name`` (last registration wins).

    What is stored is ``fn`` **wrapped to stamp** (#177), so there is no lookup
    path -- :func:`get`, :func:`run_all_modules`, a direct ``_REGISTRY`` read --
    that yields a runner whose results have not been past the governing table.
    """
    _REGISTRY[name] = _stamping(fn)


def get(name: str) -> RunFn:
    """Return the runner for ``name`` or raise ``KeyError`` listing what's available."""
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"Unknown module {name!r}; registered: {', '.join(available()) or '(none)'}"
        ) from None


def available() -> List[str]:
    """Names of all registered modules, in registration order."""
    return list(_REGISTRY)


def run_all_modules(project: Project) -> List[ModuleResult]:
    """Run every registered module that has the input slice it needs.

    A module raises :class:`~sloads.models.MissingInputError` when a required
    project slice is absent; those are skipped here so "run all" works on a
    partially-filled project. A plain :class:`ValueError` (an invalid domain input
    or a genuine calc defect) is **not** caught -- it propagates so the failure is
    visible in run-all/export rather than silently vanishing (M2R-8).
    """
    # Every module's conditions take their factor from the project's governing
    # safety-factor table (M4-8 / decision G-11). Since #177 that happens inside
    # the registered runner, so this loop states no policy of its own -- and the
    # four other callers that never reached this function are covered by the
    # same rule.
    results: List[ModuleResult] = []
    for name in available():
        try:
            results.append(_REGISTRY[name](project))
        except MissingInputError:
            continue
    return results


def run_all_modules_reporting(project: Project) -> Tuple[List[ModuleResult],
                                                         List[Tuple[str, Exception]]]:
    """:func:`run_all_modules`, with the invalid-input failures handed back.

    ``run_all_modules`` lets a plain :class:`ValueError` propagate on purpose
    (M2R-8): an invalid domain input and an absent one are different answers, and
    the invalid one must not vanish. That is right for the CLI and the export,
    which should fail the run — but a *page* that renders every module's results
    then dies whole on one bad slice, showing a traceback instead of the twenty
    modules that are fine. Three of the seven bundled examples carry an aileron
    or flap slice with no area, and both the Results Review and Export pages were
    dead on all three (#145).

    So the failure is neither swallowed nor fatal here: each module that raises is
    returned with its exception, for the caller to show by name beside the results
    that did compute. ``MissingInputError`` is still simply skipped — that is
    "not my turn", not a failure.
    """
    results: List[ModuleResult] = []
    failures: List[Tuple[str, Exception]] = []
    for name in available():
        try:
            results.append(_REGISTRY[name](project))
        except MissingInputError:
            continue
        except Exception as exc:  # reported, by name, to the caller
            failures.append((name, exc))
    return results, failures
