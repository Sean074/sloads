"""The F-C7 record: what the assembled deliverable does *not* cover.

Part of :mod:`sloads.modules.balance` (#191); the subsystem docstring is the
package's. A completeness statement is a deliverable in its own right, so the
reason codes, the record type and the wording every surface states it in have
one owner here. :func:`~sloads.modules.balance.skipped_conditions`, which
re-runs assembly to produce the record alone, is a package entry point and sits
with :func:`~sloads.modules.balance.run`.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from ...gear_loads import GearCaseLoads
from ...models import BalancedCaseResult
from .queries import source_case_name

#: Reason codes :func:`build_balanced_cases` records against a condition it did
#: not assemble. The code is the stable identity (tests and consumers key on it);
#: the sentence beside it is what the reader gets.
#:
#: ``out-of-family`` is a *deliberate* exclusion and the rest are gaps in the
#: project's inputs, but both are recorded: the deliverable's honesty statement
#: is "here is every condition SELECT named and what became of it", and a silent
#: exclusion reads exactly like a condition that was never named.
#:
#: The wording is **reader-facing prose, not diagnostics**: these sentences reach
#: the controlling document (report §4) as well as the deck, and the report's rule
#: is that its reader is an analyst rather than a maintainer -- so no input-slice
#: or constant names appear here.
SKIP_REASONS = {
    "out-of-family": (
        # Reworded at #284: the sentence used to send the reader to the
        # per-component decks note 56 D-56.2 deleted. It now names the artifacts
        # that survive, and states the deck absence as an absence.
        "not one of the balanced families this analysis assembles -- the "
        "fuselage conditions are delivered as net fuselage loads in the report "
        "and the case index, and the one-engine-out fin conditions in the "
        "report alone; none of them reaches a solver deck"),
    "gear-design-only": (
        "a supplementary nose-wheel condition (FAR 23.499): it carries nose "
        "reactions only, with no main-gear reaction anywhere in the family, so "
        "it is a local gear-design case rather than an airplane in equilibrium "
        "and there is nothing for a balanced case to balance. It is not "
        "missing from the deliverable -- the gear load report carries it, with "
        "all thirty-three cases"),
    "side-twin-by-reflection": (
        "the opposite drift direction of the side-load case before it (FAR "
        "23.485), which this analysis produces by REFLECTING that case rather "
        "than assembling it a second time -- so it is in the deck, under its "
        "own case id, as the twin. Assembling both would put two handedness "
        "mechanisms in one step; deriving it instead gives the reflection "
        "operator the one independent check it has, against the manual's own "
        "figures for this case"),
    "htail-symmetric": (
        "a symmetric horizontal-tail condition: it is already in every balanced "
        "case, as the trim tail load the assembled airplane is balanced against, "
        "so only the 23.427(a) unsymmetrical condition -- the one with a "
        "left/right hand -- is assembled as a case of its own"),
    "no-htail-loads": (
        "no horizontal-tail spanwise load distribution is available for it, so "
        "there is no unsymmetrical tail load to assemble the case around"),
    "no-fin-loads": (
        "no vertical-tail spanwise load distribution is available for it, so "
        "there is no fin side load to assemble the case around"),
    "no-vn-point": (
        "its V-n point is not in the flight envelope, so the case has no "
        "flight condition to be assembled at"),
    "no-cg-case": (
        # "source case", not "V-n point": this reason is reached by the ground
        # family too, whose case number is LANDLOAD's (R6-C3). The condition's
        # own name, beside it in the record, says which table it numbers into.
        "its source case names a loading this project does not define, so the "
        "case has no weight or CG"),
    "loading-not-derivable": (
        "its payload loading is not derivable from the itemized weight "
        "database -- a CG the items cannot actually produce has no honest "
        "inertia set, and inventing one would put fictitious mass into the "
        "very balance the case exists to demonstrate"),
}


@dataclass(frozen=True)
class SkippedCondition:
    """One condition SELECT named that :func:`build_balanced_cases` did not
    assemble, and why (review F-C7).

    Not persisted and not a schema type: it is a statement *about* a run, minted
    with the cases and travelling beside them onto the ``ModuleResult``, the deck
    ``$`` block and the report. ``code`` is the stable machine identity (a key of
    :data:`SKIP_REASONS`); ``reason`` is the sentence rendered.
    """
    component: str
    label: str
    case: Optional[int]
    code: str
    reason: str
    #: Which table :attr:`case` numbers into -- LANDLOAD's for a ground
    #: condition, FLTLOADS' V-n for a flight one (R6-C3). Carried rather than
    #: inferred from ``component`` so the record states its own family, and
    #: defaulted to the flight family because that is what a skip minted from a
    #: SELECT condition is.
    ground: bool = False

    @property
    def name(self) -> str:
        """The condition, named as the family that produced it names it."""
        where = (f" ({source_case_name(self.case, self.ground, short=True)})"
                 if self.case is not None else "")
        return f"{self.component} {self.label}{where}"


def _skip(cond, code: str) -> SkippedCondition:
    return SkippedCondition(component=cond.component, label=cond.label,
                            case=cond.case, code=code, reason=SKIP_REASONS[code],
                            ground=isinstance(cond, _GroundCondition))


@dataclass(frozen=True)
class _GroundCondition:
    """A LANDLOAD case wearing the shape :func:`_skip` expects.

    ``SkippedCondition`` was written around SELECT's conditions, which carry
    ``component``/``label``/``case``. A ground case has all three under different
    names, so this adapts rather than duplicating the record type -- the
    deliverable's completeness statement must read as one list, not two.
    """

    gear: GearCaseLoads

    @property
    def component(self) -> str:
        return "landing_gear"

    @property
    def label(self) -> str:
        return self.gear.description

    @property
    def case(self) -> int:
        return self.gear.case


def skipped_condition_lines(skipped: Sequence[SkippedCondition]) -> List[str]:
    """The record as text, **one line per reason** -- the single owner of the
    wording every surface states it in (deck ``$`` block, report, UI).

    Grouped rather than one line per condition because the reasons repeat and the
    conditions do not: on ``ga6_normal`` a dozen h-tail, fuselage and ground
    conditions share the one "not a balanced family" sentence, and repeating it
    per condition buried the record it exists to make readable. Reasons appear in
    the order SELECT first hit them; conditions in SELECT's order within each.
    """
    grouped: List[Tuple[str, List[str]]] = []
    index = {}
    for s in skipped:
        if s.code not in index:
            index[s.code] = len(grouped)
            grouped.append((s.reason, []))
        grouped[index[s.code]][1].append(s.name)
    return [f"{reason}: {', '.join(names)}" for reason, names in grouped]


def skipped_block(skipped: Sequence[SkippedCondition]) -> List[str]:
    """The F-C7 record as deck comment lines, wrapped inside 72 columns.

    Printed whether or not anything was skipped: "every condition assembled" is
    the completeness statement, and a block that appears only on a lossy run
    cannot be told from a deck written before the record existed.

    Owned here, beside the wording, since #284: the LRA deck -- the one solver
    deck that ships (note 56 D-56.8) -- renders it as well as the assembled
    producer, and the shipping deck must not import it from the internal one.
    """
    out = ["$",
           "$ ------------------------------ CONDITIONS NOT ASSEMBLED (SELECT set)"]
    lines = skipped_condition_lines(skipped)
    if not lines:
        out.append("$ None -- every condition SELECT named assembled into a case.")
        return out
    for line in lines:
        out += [f"$ {ln}" for ln in textwrap.wrap(line, width=70,
                                                 initial_indent="- ",
                                                 subsequent_indent="    ")]
    return out


def carry_sources_absent(result: BalancedCaseResult) -> bool:
    """No cut reaction is applied in an assembled case (plan 11 §4's seam rule).

    The wing carry-through is *internal* to a full-span model -- the solver
    recovers it — so applying it as well would react the wing twice. Structural
    here (``assemble`` never reads ``body_loads``); this is the drift guard.
    """
    return not any(ld.source in ("reaction", "root", "carry", "correction")
                   for ld in result.loads)


#: Title of the F-C7 record row on the ``ModuleResult``. A constant because it is
#: the string the report and the guard test both look the record up by.
SKIPPED_RECORD_TITLE = "Assembly record -- conditions not assembled"


def _skipped_record(skipped: Sequence[SkippedCondition]):
    """The F-C7 record as a :class:`ConditionResult` (review F-C7).

    Emitted **whether or not anything was skipped**: "every condition SELECT
    named assembled" is the statement the deliverable was missing, and a record
    that appears only when something is wrong cannot be told from one that was
    never produced. It carries no ``case_ref`` -- it is a statement about the run,
    not a load case, so it mints no case index row -- and its one value is a
    dimensionless count, which the ULTIMATE boundary passes through unscaled.
    """
    from ...models import ConditionResult, LoadValue

    lines = skipped_condition_lines(skipped)
    note = (" | ".join(lines) if lines else
            "every condition SELECT named was assembled into a balanced case")
    return ConditionResult(
        title=SKIPPED_RECORD_TITLE,
        far_reference="",
        values=[LoadValue("Conditions not assembled", float(len(skipped)), "",
                          key="balanced_skipped_count")],
        note=note,
    )
