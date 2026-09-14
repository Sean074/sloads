"""The cross-cutting sections both reports print, and who succeeds what (#278).

Design note 60, D-60.7 … D-60.11. The summary report (``content.build_report``)
had one production consumer, ``app/views/export_report.py``, which note 57 D-57.1
deletes -- so retiring the page retires the document, and with it the **only**
statement of the axis system either front end makes and the **only** FAR 23
Subpart C coverage matrix. This module is where those assets live instead: four
builders the oracle report prints as front matter, and the audit table that says
what happens to every other section of the retiring document.

**One builder, two documents.** Until ``content.py`` is deleted at #270 both
reports print these sections, and they print the *same* ones: ``content.py``
calls the builders below rather than keeping a second copy that can drift. That
is CLAUDE.md practice 3 applied to the merge itself -- a merge implemented as a
copy is the duplication the convergence exists to end.

The heading is a parameter because the two documents number differently: the
summary report numbers from :data:`sloads.report.content.SECTIONS` and the
oracle report from :func:`sloads.report.oracle_content.section_number`. Nothing
here writes a section number of its own, and nothing here reads the clock or the
filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Sequence, Tuple

from ..constants import ULTIMATE_FACTOR
from ..models import Project
from ..units import UnitSystem
from .content import Figure, Section, Table
from .coverage import (
    COVERED,
    NOT_ANALYSED,
    NOT_APPLICABLE,
    OUT_OF_SCOPE,
    coverage_matrix,
    coverage_summary,
)
from .render import format_value

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .package_data import DataFile

__all__ = [
    "SUMMARY_DISPOSITION",
    "SectionDisposition",
    "conventions_section",
    "coverage_section",
    "coverage_table",
    "disposition_for",
    "governing_factors_section",
    "package_files_section",
    "undeclared_sections",
]


# --------------------------------------------------------------------------- #
# Axes and sign conventions (design note 15; merged by D-60.8)
# --------------------------------------------------------------------------- #
def conventions_section(heading: str) -> Section:
    """The global sign-convention statement: prose, table and three figures.

    Everything here is read from :mod:`.conventions_tex`, the single source
    (CLAUDE.md practice 3) -- this function only arranges it. It takes no
    project: the conventions are identical in every report, so the section can
    never be absent, and the three figures carry no ``PlotData`` for the same
    reason (``plots_tex.figure_body_tex`` dispatches them ahead of its absence
    test).

    Merged into the oracle report by D-60.8. Point-of-use sign statements were
    the rejected alternative: they say what one figure's signs are, never what
    the frame is, and a loads document that does not state its frame cannot be
    read by the structures analysis it is written for.
    """
    from .conventions_tex import CONVENTION_ROWS, CONVENTION_TABLE_NOTE, CONVENTIONS_PROSE

    return Section(
        heading,
        body=list(CONVENTIONS_PROSE),
        figures=[
            Figure(key="sign_axes", title="Reference frame and state signs",
                   caption="x +aft, y +starboard, z +up (right-handed, identity "
                           "to the solver CID 0); +α nose-up, +β wind from "
                           "starboard; moment senses as drawn"),
            Figure(key="sign_controls", title="Control and rotation signs",
                   caption="elevator TE-down +, rudder TE-to-port + (left "
                           "pedal), aileron hand per case; clockwise from the "
                           "pilot's view + for rotation"),
            Figure(key="sign_beams", title="Shear, moment and torsion diagram "
                                           "conventions",
                   caption="wing integrated tip to root, body nose to tail, "
                           "fin loaded in fy; torsion axes named per figure"),
        ],
        tables=[Table(
            title="Sign conventions of record",
            columns=["Quantity", "Positive sense", "Charter"],
            rows=[list(r) for r in CONVENTION_ROWS],
            note=CONVENTION_TABLE_NOTE,
        )],
    )


# --------------------------------------------------------------------------- #
# Governing safety factors (M4-8 / decision G-11; merged by D-60.8)
# --------------------------------------------------------------------------- #
_FACTORS_PROSE = (
    "Every load in this report and in the exported decks is a LIMIT value. The "
    "row below that governs its condition gives the factor a sizing analysis "
    "must apply to it; sloads states that factor and never applies it. "
    "This table is the authority: the per-case SF stated in the case index "
    "(§CASEREF), in the load-case CSVs and on each deck's SUBCASE header is a "
    "derived view of it, so a report figure and its bulk-data card cannot state "
    "different factors for the same case.",
    "Rows are condition families, not cases, and the family boundaries are 14 CFR "
    "Subpart C's own section groupings — so a case cannot be missed by omitting a "
    "row. The factor is prescribed for load quantities only: load factors, "
    "speeds, weights and geometry take none, and nothing here is scaled by it.",
)

_FACTORS_TABLE_NOTE = (
    "Status 'derived' is the regulation's own value. 'override' is a project-"
    "supplied replacement, which must state a basis and is repeated in the "
    "methods & limitations statement so it reaches a reader who sees only one "
    "file. 'defaulted' would mean a condition this table could not classify, "
    "factored at the conservative 1.5 and flagged; no shipped configuration "
    "produces one."
)


def governing_factors_section(heading: str, project: Project,
                              groups: Iterable[Sequence[Any]], *,
                              case_index_ref: str) -> Section:
    """The governing safety-factor table (M4-8 / decision G-11).

    The table is built from :mod:`sloads.safety_factors`, the single code owner,
    and the *same* object is asked to classify every case in ``groups`` -- so the
    "defaulted" line below is a live statement about this run rather than a claim
    about the code. Each document passes the groups it actually carries.

    ``case_index_ref`` is where that document's reader finds the per-case
    factors: a section reference in the summary report, the shipped case-index
    file in the oracle report's package. Written as a parameter rather than a
    literal for the reason every other cross-reference here is derived (F-R2).
    """
    from ..safety_factors import GoverningTable

    table = GoverningTable.for_project(project)
    for group in groups:
        for item in group:
            table.factor_for(item)

    body = [p.replace("§CASEREF", case_index_ref) for p in _FACTORS_PROSE]
    if table.has_overrides:
        body.append(
            "This project overrides " +
            ", ".join(f"'{r.label}' to SF = {format_value(r.factor)} "
                      f"(regulation: {format_value(r.derived_factor)})"
                      for r in table.overrides) +
            ". An override cannot move a number in this report or on a deck — "
            "sloads applies no factor anywhere — but it does change the factor "
            "stated under that row, and so the ultimate load a sizing analysis "
            "will derive from it.")
    if table.defaulted:
        body.append(
            "DEFAULTED: " + ", ".join(repr(r) for r in table.defaulted) +
            " — condition(s) no row classified. They state "
            f"{format_value(ULTIMATE_FACTOR)} and are flagged here; treat this as a "
            "defect in the governing table, not a property of the airplane.")
    return Section(
        heading,
        body=body,
        tables=[Table(
            title="Governing safety factors of record",
            columns=["Family", "FAR", "Load class", "SF", "Status", "Basis"],
            rows=[[r.label, r.far_reference, r.load_class, format_value(r.factor),
                   r.status, r.basis] for r in table.rows],
            small=True,
            note=_FACTORS_TABLE_NOTE,
        )],
    )


# --------------------------------------------------------------------------- #
# Conditions analysed and FAR coverage (merged by D-60.8)
# --------------------------------------------------------------------------- #
_STATUS_LABEL = {
    COVERED: "covered",
    NOT_APPLICABLE: "not applicable",
    NOT_ANALYSED: "NOT ANALYSED",
    OUT_OF_SCOPE: "out of scope",
}


def coverage_table(project: Project, module_results) -> Tuple[Table, str]:
    """The FAR 23 Subpart C coverage matrix, and its one-line headline.

    Returned as a pair because the two documents place them differently and
    neither should re-derive the counts: the headline is
    :func:`sloads.report.coverage.coverage_summary` rendered, not a second count
    of the same rows.
    """
    refs = [c.far_reference for mr in module_results for c in mr.conditions]
    rows = coverage_matrix(project, refs)
    summary = coverage_summary(rows)
    headline = (
        f"{summary[COVERED]} regulations covered, {summary[NOT_APPLICABLE]} not "
        f"applicable to this airplane, {summary[NOT_ANALYSED]} NOT ANALYSED "
        f"(inputs absent), {summary[OUT_OF_SCOPE]} out of scope for this tool."
    )
    table = Table(
        title="FAR 23 Subpart C coverage",
        columns=["FAR", "Title", "Module", "Status", "Cases", "Reason"],
        rows=[[r.far, r.title, r.module, _STATUS_LABEL[r.status],
               str(r.case_count) if r.case_count else "—", r.reason] for r in rows],
        small=True,
        status_column="Status",
        note="'Not applicable' is an engineering conclusion about this airplane; "
             "'NOT ANALYSED' is a gap in this run that supplying inputs would close; "
             "'out of scope' is a permanent boundary of this tool that must be "
             "covered by other means.",
    )
    return table, headline


_COVERAGE_PROSE = (
    "This section states what was analysed and, more importantly, what was not. "
    "Every regulation of 14 CFR 23 Subpart C this suite can cover is listed "
    "below and classified against the conditions this run actually produced, so "
    "a reviewer can see a gap without reading the whole document to find its "
    "absence. The distinctions are the value of the table: 'not applicable' is "
    "an engineering conclusion about this airplane, 'NOT ANALYSED' is a gap in "
    "this run that supplying inputs would close, and 'out of scope' is a "
    "permanent boundary of this tool that must be covered by other means."
)


def coverage_section(heading: str, project: Project, module_results) -> Section:
    """The coverage matrix as a section of its own (the oracle report's use).

    The summary report prints the same table inside a wider section that also
    carries its case index; here the matrix stands alone, because the oracle
    report identifies cases in the sections that compute them and ships the case
    index as a file of the package.
    """
    table, headline = coverage_table(project, module_results)
    return Section(heading, body=[_COVERAGE_PROSE, headline], tables=[table])


# --------------------------------------------------------------------------- #
# The bundle manifest (SUMMARY_REPORT.md §4.7; merged by D-60.8)
# --------------------------------------------------------------------------- #
def package_files_section(heading: str, *, system: UnitSystem,
                          files: Sequence["DataFile"],
                          control: Sequence[Any]) -> Section:
    """What travels with this document, stated in the document (#245, D-60.8).

    The reader's half of **G-OR-17** -- a file the package carries and the
    document never mentions is a file with no stated provenance -- and the
    summary report's Appendix A bundle manifest, merged. ``MANIFEST.txt`` states
    the same set with hashes; that one is the archivist's instrument and this is
    the reader's, which is why both exist and why both are built from the same
    two owners (:mod:`.package_data` for the data, :mod:`.oracle_package` for
    the control files) rather than from two enumerations that can disagree.
    """
    from .oracle_package import units_sentence

    rows = [[m.name, m.contents, m.summarised_in] for m in control]
    rows += [[f.name, f.contents, f.summarised_in] for f in files]
    body = [units_sentence(system)]
    if files:
        body.append(
            "Every table and every curve in this report is drawn from a file "
            "that travels with it. Each states its own units, the safety factor "
            "it does not apply, the axes its coordinates are in, the analysis "
            "step that produced it and the fingerprint of the build it came "
            "from, so a file forwarded on its own remains readable without this "
            "document.")
    else:
        body.append(
            "This issue carries no data files: no section of it was built from "
            "an analysis that produced any.")
    return Section(heading, body=body, tables=[Table(
        title="Files carried in this package",
        columns=["File", "What it contains", "Summarised in"],
        rows=rows, small=True,
        note="Paths are relative to this package's own directory. The same set "
             "is listed again, with a SHA-256 for each file, in MANIFEST.txt.")])


# --------------------------------------------------------------------------- #
# The audit: what happens to every section of the retiring document (D-60.10)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SectionDisposition:
    """One section of the retiring summary report, and where it went.

    ``merged_into`` names the front-matter section of
    :data:`sloads.report.oracle_content.FRONT_SECTIONS` that now carries it --
    the machine-checkable half, so "merged" is a claim a test can follow rather
    than a word in a sentence. ``successor`` says in prose what carries it where
    no single front section does, and ``reason`` says why it retires. At least
    one of the three is always filled: a section with none is a deletion nobody
    declared, which is what D-60.10 exists to make impossible.
    """

    key: str
    merged_into: str = ""
    successor: str = ""
    reason: str = ""


#: Every key of :data:`sloads.report.content.SECTIONS`, with its disposition.
#:
#: The written audit D-60.10 requires, and the subject of note 60's gate 12: a
#: test reads this table against ``content.SECTIONS`` and fails if a key is
#: neither merged nor declared superseded with a reason. It is deliberately a
#: table and not prose in a design note -- the note cannot fail a build.
#:
#: It retires with ``content.py`` at #270, when the keys it audits no longer
#: exist. Until then it is the record of what the merge decided.
SUMMARY_DISPOSITION: Tuple[SectionDisposition, ...] = (
    SectionDisposition(
        key="inputs",
        successor="the oracle report's Loads Configuration section, and the "
                  "packaged project.json",
        reason="The configuration the analysis ran on is printed per step. The "
               "inputs themselves are deliberately not re-echoed: the project "
               "file in the package is the exact, machine-readable record of "
               "them, and a table transcribing it is a second copy that can "
               "disagree with the first (note 44 OR-194).",
    ),
    SectionDisposition(
        key="conventions",
        merged_into="conventions",
        successor="merged: :func:`conventions_section`, printed as oracle "
                  "front matter after the introduction (D-60.8/D-60.9)",
    ),
    SectionDisposition(
        key="factors",
        merged_into="factors",
        successor="merged: :func:`governing_factors_section` (D-60.8)",
    ),
    SectionDisposition(
        key="envelopes",
        successor="the Flight Envelope section's V-n and speed-altitude "
                  "figures, and the Weight and Mass Properties section's "
                  "weight/CG envelope",
        reason="The oracle report draws each envelope in the section that "
               "computes it, which is where a reader meets its numbers; a "
               "collecting section would draw the same curves a second time.",
    ),
    SectionDisposition(
        key="conditions",
        merged_into="coverage",
        successor="merged: :func:`coverage_section` (D-60.8). The case index "
                  "ships as data/case_index.csv and every section identifies "
                  "its rows by case id.",
        reason="The approved-corrections table is not merged: it describes the "
               "tool rather than this issue, and the oracle report drops that "
               "block from its pre-filled limitations for the same reason "
               "(owner's decision, 2026-08-30). It reaches a reader through the "
               "methods statement carried in every shipped file's header.",
    ),
    SectionDisposition(
        key="results",
        successor="the oracle report's analysis body -- one section per step, "
                  "each with its own governing table",
        reason="The summary report organised by topic what the oracle report "
               "organises by step; the numbers are the same set, from the same "
               "producers, and the per-step organisation is the one a reader "
               "checking a module against Appendix A follows.",
    ),
    SectionDisposition(
        key="balanced",
        successor="the balanced deck's own SUBCASE headers, and Appendix G",
        reason="The oracle report's section set is derived from the oracle step "
               "set (G-OR-2), and balanced_cases is not in it: it runs no .BAS "
               "program and produces no slice one requires. Its honesty "
               "statement travels where it is owed -- each case's pre-closure "
               "residual and closure are written in band on the deck that "
               "carries the case (export/balanced_deck.py), the MASSSET "
               "identity on the mass model, and what summing the applied set "
               "onto the beam grids costs the distribution is Appendix G.",
    ),
    SectionDisposition(
        key="gear",
        successor="the Landing Gear Loads section and Appendix F",
    ),
    SectionDisposition(
        key="methods",
        successor="the front matter's 'Limitations and scope' subsection, "
                  "pre-filled from the same methods statement",
        reason="Four blocks of the shared statement are dropped from the "
               "pre-fill because they describe the tool rather than this issue "
               "(owner's decision, 2026-08-30); the full statement is carried "
               "in the header of every file the package ships.",
    ),
)


def disposition_for(key: str) -> Optional[SectionDisposition]:
    """The audit row for ``key``, or ``None`` if the merge never declared one."""
    return next((d for d in SUMMARY_DISPOSITION if d.key == key), None)


def undeclared_sections(keys: Iterable[str]) -> List[str]:
    """The keys of ``keys`` this audit says nothing about (gate 12)."""
    return [key for key in keys
            if not any(d.key == key and (d.merged_into or d.successor or d.reason)
                       for d in SUMMARY_DISPOSITION)]
