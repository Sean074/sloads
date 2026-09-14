"""What the issue package's ``data/`` carries, and which owner each file is (#245).

Design note 44 OR-22/OR-23, deferred by OR-42 and delivered here. A report issue
is a *package*, and the claim ``oracle_package`` makes for it is that the data
behind the document travels with the document. Until this module existed the
package held five files and no data at all: Appendix F named
``landing_gear_applied_loads.csv`` in its own prose and no production path wrote
that file anywhere, while the applied sets shipped only from the retiring
``app/`` export page. An analyst holding the report could not obtain its
appendices as files.

**One generation path.** Every file here is built from the *same* owner the
document renders from, and from the *same* object: :class:`OracleDocument`
carries the reduced project and the module results the sections were built from,
so a data file cannot describe a different analysis from the page that
summarises it. There is no second run and no second formatter.

**What lands here, and why only this.** ``data/`` carries what a reader cannot
otherwise get as numbers:

* ``load_cases/<module>.csv`` -- one per module that produced a result. This is
  the channel the per-module download buttons used to be (#245 item 2), through
  the identical owner, so no column of theirs is lost with them.
* the **named** deliverable sets -- the six ``*_applied_loads.csv``, the V-n
  conditions, the case index, the governing safety-factor table and the gear
  report. These are the files the report's own prose and the bundle manifest
  already name, and they carry solver-channel columns a printed table cannot fit.
* one file per **appendix table** no named file carries -- the cumulative
  distributions of B.2 and C.2, Appendix A's mass cases, Appendix G's lumping
  comparison. A table that *is* carried says so in :attr:`Table.data_file` and is
  not written twice.
* one file per **figure** the document draws. A curve has no printed table, so
  its numbers exist nowhere else; the one-engine-inoperative yaw march is the
  case the #245 column inventory found, and the emitter is generic because
  the next such curve should not need a second finding.

The body's own tables are deliberately **not** re-emitted one by one: they are
printed in the document the package carries, and the module file above is their
superset. A per-printed-table file would put the same numbers in the package a
third time under a name nothing cites.

The document's own list of these files is the bundle-manifest front section
(:func:`sloads.report.front_sections.package_files_section`), which #278 widened
to every file the package carries -- the data half of it is still built from the
list below, so a file cannot be added to the package without appearing there.

**Pure**, like the rest of :mod:`sloads.report`: this module returns file
*contents*; :mod:`sloads.export.report_package` writes them. Nothing here reads
the clock or the filesystem.
"""

from __future__ import annotations

import io as _io
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, List, Sequence, Tuple

from .. import csv_text
from ..models import Project

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .content import Figure, Section, Table
    from .oracle_content import OracleDocument

#: The package subdirectory every file below lives in. **The owner of the name**;
#: :mod:`sloads.report.oracle_package` re-exports it so a caller assembling a
#: package has one import for the package's shape.
DATA_DIR = "data"

#: Where the per-module load-case files sit inside ``data/``.
#:
#: A subdirectory and not a flat prefix because there are twenty-odd of them and
#: they are the one family a reader browses as a family -- the spelling the
#: retiring export bundle used for the same set, kept so a script that walked
#: ``load_cases/`` still walks it.
LOAD_CASES_DIR = "load_cases"

#: Where a figure's own numbers sit.
FIGURES_DIR = "figures"

#: The column a generic emitter puts a plot's series name in.
#:
#: Figures are written **long**, one row per point, rather than wide with a
#: column per curve: a figure's series do not in general share an x -- a planform
#: outline and the loads reference axis drawn on it have neither the same
#: stations nor the same count -- and a wide file would have to pad, which
#: invents points the analysis never computed.
FIGURE_COLUMNS: Tuple[str, ...] = ("Kind", "Series")


@dataclass(frozen=True)
class DataFile:
    """One file of ``data/``, with the manifest facts §4.7 requires of it.

    ``name`` is relative to the package root and always starts with
    :data:`DATA_DIR`, because that is the path the manifest prints and the
    document cites -- a name that had to be joined by its consumer would be a
    second place the layout is decided.
    """

    name: str
    content: str
    contents: str
    units: str = "--"
    summarised_in: str = "--"


def _path(*parts: str) -> str:
    return "/".join((DATA_DIR,) + parts)


# --------------------------------------------------------------------------- #
# The header every file carries (G-OR-15)
# --------------------------------------------------------------------------- #
def data_header(doc: "OracleDocument", *, name: str, step_key: str,
                drawn_by: str) -> str:
    """The ``#`` block that makes one ``data/`` file self-describing.

    ``SUMMARY_REPORT.md`` §3.1 applied to a detached file, which is what
    **G-OR-15** asserts: a file that has been forwarded out of its package must
    still state its units, its basis and the factor it does not apply, which way
    its axes point, *which analysis step produced it* and *which build it came
    from*. The first four are the methods stamp -- one statement, one owner
    (:mod:`sloads.report.methods`), wrapped for this channel -- and the last two
    are this block's own four lines.

    The fingerprint is the document's, not a hash of this file: the question a
    reader asks of a stray CSV is which *analysis* it came out of, and the
    fingerprint is the answer the report's own title page gives. A per-file hash
    would answer a question the manifest already answers, and answer the reader's
    one not at all.
    """
    from .methods import csv_comment_block

    lines = [f"# DATA FILE: {name}",
             f"# PRODUCED BY: {step_key or 'the report generator'}",
             f"# SUMMARISED IN: {drawn_by}"]
    if doc.fingerprint:
        lines.append(f"# ANALYSIS FINGERPRINT: {doc.fingerprint} "
                     f"(version {doc.fingerprint_version})")
    else:
        # Stated as absent rather than omitted: a header with no fingerprint line
        # reads as a build that forgot one, and a reader cannot tell that from a
        # build that had none to give (a package assembled without the field
        # registry, which the CLI path can do).
        lines.append("# ANALYSIS FINGERPRINT: not computed for this build")
    lines.append("#")
    return "\n".join(lines) + "\n" + csv_comment_block(
        doc.project if doc.project is not None else Project())


# --------------------------------------------------------------------------- #
# The generic emitters
# --------------------------------------------------------------------------- #
def table_csv(table: "Table") -> str:
    """One printed table as a CSV -- its own columns, its own cells.

    The cells are the document's: already converted, already rounded, already
    carrying the ``-ULT`` marker in their heading where the whole table is
    ultimate. That is the point -- this file is *the table*, so it must not be a
    second formatting of the same numbers that can round differently from the
    page beside it.

    The table's note travels with it, ``#``-prefixed above the header row, for
    the reason the V-n file learnt at #242: a note that defines five of the
    columns is part of the table, and a file forwarded alone had the columns and
    not the definitions.
    """
    from .oracle_sections import _csv_note

    buf = _io.StringIO()
    writer = csv_text.writer(buf)
    writer.writerow(list(table.columns))
    for row in table.rows:
        writer.writerow(list(row))
    return _csv_note(table.note) + buf.getvalue()


def figure_csv(figure: "Figure") -> str:
    """One figure's own numbers, long form.

    ``Kind`` says what the row is part of, because a figure carries four kinds of
    geometry and they are not the same statement: a ``line`` is a computed curve,
    ``region`` its closed variant (a planform outline), ``points`` a cloud or a
    set of labelled markers, and ``vline`` a labelled reference station with no
    ordinate at all. Flattening them into one nameless list would leave a reader
    unable to tell the wing's outline from the loads applied along it.

    The axis labels are the column headings, units included, so the file states
    its quantities the way the printed axis does.
    """
    data = figure.data
    buf = _io.StringIO()
    writer = csv_text.writer(buf)
    if data is None:
        return ""
    writer.writerow(list(FIGURE_COLUMNS) + [data.x_label, data.y_label])
    for series in data.series:
        kind = "points" if series.marker else ("region" if series.closed else "line")
        for index, (x, y) in enumerate(zip(series.x, series.y)):
            name = (series.labels[index]
                    if index < len(series.labels) else series.name)
            writer.writerow([kind, name, _num(x), _num(y)])
    for label, x, y in data.points:
        writer.writerow(["points", label, _num(x), _num(y)])
    for label, x in data.vlines:
        writer.writerow(["vline", label, _num(x), ""])
    return buf.getvalue()


def _num(value: float) -> str:
    """A plot ordinate as text, at the precision the figure was built with.

    ``repr`` and not a fixed format: a figure's data is the analysis's own
    floats, and rounding them here would make the file disagree with the curve
    it is the numbers of -- by a hair, invisibly, which is the worst amount.

    Negative zero is written as zero. It is the one normalisation, and it is not
    a rounding: ``-0.0`` and ``0.0`` are the same ordinate, and which one a
    geometry builder happens to produce depends on the order it subtracted in.
    The journey gate caught it -- a wing planform typed through the GUI closed
    its outline at ``-0.0`` where the same planform loaded from a file closed it
    at ``0.0`` -- and a file that changes because of that is a file that will
    fail the determinism gate for no reason a reader could ever see.
    """
    number = float(value)
    return repr(number + 0.0 if number == 0 else number)


# --------------------------------------------------------------------------- #
# The named deliverable sets
# --------------------------------------------------------------------------- #
#: The files the report's own prose, and the retiring export bundle's manifest,
#: already name -- ``(file name, step key, appendix title, what it contains)``.
#:
#: Named rather than derived because the *name* is the thing being kept: Appendix
#: F says "the same set as the file ``landing_gear_applied_loads.csv``" in its
#: printed prose, and a generated name would have let that sentence come to
#: point at nothing -- which, until #245, is exactly what it did.
_APPLIED_SETS: Tuple[Tuple[str, str, str], ...] = (
    ("wing", "wing_loads", "Wing loads by station"),
    ("fuselage", "fuselage_loads", "Fuselage loads by station"),
    ("htail", "htail_loads", "Horizontal tail loads by station"),
    ("vtail", "vtail_loads", "Vertical tail loads by station"),
    ("landing_gear", "landing_loads", "Landing gear loads by case"),
    # The engine mount has no appendix of its own -- six components at one point
    # is a section's table, not a distribution (note 44 OR-158) -- but it is one
    # of the six delivered applied sets, and a set that ships from nowhere is the
    # defect this module was written for. It names its *section* instead.
    ("engine", "engine_mount", ""),
)


def _has_rows(text: str) -> bool:
    """Whether a rendered CSV carries data, as opposed to a header and a heading.

    Every owner below prepends the file's ``#`` block and writes its column row
    even when the analysis produced nothing, so "did this produce anything" is a
    question about the rows and not about the string being non-empty. An empty
    member is omitted rather than shipped blank -- the manifest then does not
    name it, which is how the package has always stated an absent artifact.
    """
    rows = [line for line in text.splitlines()
            if line.strip() and not line.startswith("#")]
    return len(rows) > 1


def _ref(doc: "OracleDocument", step_key: str, appendix_title: str) -> str:
    """Where the document summarises a named file: its appendix, else its section."""
    from .oracle_content import appendix_ref, section_ref

    if appendix_title:
        name = appendix_ref(appendix_title)
        if name:
            return name
    return section_ref(doc.plan, step_key) if doc.plan else "the analysis sections"


def _named_files(doc: "OracleDocument") -> List[DataFile]:
    """The V-n conditions, the six applied sets, and the report's three tables."""
    from . import tables as rt
    from .applied import APPLIED_CSV_NAMES, applied_load_csv
    from .oracle_sections import (
        VN_CONDITIONS_CSV,
        applied_set_source,
        vn_conditions_csv,
    )

    project = doc.project
    if project is None:
        return []
    system = doc.system
    out: List[DataFile] = []

    def add(name: str, step_key: str, appendix_title: str, contents: str,
            units: str, build: Callable[[str], str], ref: str = "") -> None:
        ref = ref or _ref(doc, step_key, appendix_title)
        header = data_header(doc, name=_path(name), step_key=step_key,
                             drawn_by=ref)
        try:
            content = build(header)
        except Exception:      # see the module docstring of
            # ``run_sections``: a half-filled project must still build a package,
            # and a producer that raises on one means that file is absent, not
            # that the package is.
            return
        if not _has_rows(content):
            return
        out.append(DataFile(_path(name), content, contents=contents, units=units,
                            summarised_in=ref))

    def _applied(component: str) -> Callable[[str], str]:
        """One component's builder, bound -- not a lambda closing over the loop."""
        def build(header: str) -> str:
            return applied_load_csv(applied_set_source(project, component),
                                    header, system=system, component=component,
                                    project=project)
        return build

    def _case_index(header: str) -> str:
        groups: List[Sequence[object]] = [
            applied_set_source(project, c)
            for c in ("wing", "fuselage", "htail", "vtail")]
        groups += [r.conditions for r in doc.results.values() if r is not None]
        # The assembled cases, by the same route the deck writes them (design
        # note 17). Without them the index names none of the handed L/R cases
        # the LRA deck subcases are, and its "LOAD/SUBCASE (assembled)" column
        # is empty on every row -- so a reader holding the primary deliverable
        # cannot trace a SUBCASE back through the one tabular channel there is.
        # It shipped that way from #245; the gap was invisible while the summary
        # report printed a complete index beside it, and #270 deleted that
        # report.
        from ..export.balanced_deck import build_balanced_cases
        try:
            assembled = build_balanced_cases(project) or []
        except Exception:      # the same rule as ``add`` below: a project that
            assembled = []     # assembles nothing has no assembled column, not
                               # no index.
        return rt.case_index_csv_from(*groups, header_comment=header,
                                      assembled=assembled)

    human = ("as stated in this manifest's Units section")
    solver = ("the solver channel the exported deck is written in "
              "(N, mm and N-mm in SI; lb, in and lb-in in Imperial), stated in "
              "the column headings")

    add(VN_CONDITIONS_CSV, "flight_envelope", "Balanced flight conditions (V-n)",
        "Every balanced flight condition the envelope produces, one flat row per "
        "point: the flight state and the four loads that balance it, with the "
        "case id each point was selected as. The matrix every section's critical "
        "conditions are chosen from.",
        human, lambda h: vn_conditions_csv(project, h, system=system))

    for component, step_key, appendix in _APPLIED_SETS:
        add(APPLIED_CSV_NAMES[component], step_key, appendix,
            f"The {component.replace('_', ' ')} applied load set: what to apply, "
            "where, for which case, at what factor. One row per load point per "
            "case, at the LRA beam grids, LIMIT throughout. This is the file a "
            "structures model is built from -- nothing in it is a running total.",
            solver,
            _applied(component))

    # Built from the live results, not from the project's persisted slices: the
    # report recomputes every distribution it prints (the slices on a stored
    # project are inputs, not a run), so a case index read off the file would
    # name a different set of cases from the document beside it. The order is
    # the export page's -- distributions first, because first-seen defines a
    # row's flight condition.
    add("case_index.csv", "", "",
        "Every load case the analysis produced, with its condition, its "
        "regulation and the factor it states and does not apply -- the index a "
        "reader traces a case id back through.",
        human, _case_index,
        # Not "section 1": these three are the document's cross-cutting tables
        # and belong to no one section. Saying where they are actually used
        # beats naming the section a "" step key happens to resolve to, which is
        # the Introduction and is not where a reader meets a case id.
        ref="every section that states a case id")
    add("safety_factors.csv", "", "",
        "The governing safety-factor table: one row per condition family, each "
        "with the basis of its factor. The authority every per-case SF in this "
        "package is a view of.",
        human, lambda h: rt.safety_factors_csv(project, header_comment=h),
        ref="the SF column of every load table, and the methods statement")
    add("gear_loads.csv", "landing_loads", "",
        "The gear load report: one row per ground case per loaded leg, stating "
        "each reaction in the manual's ground-line frame at the contact patch "
        "and in airplane axes at the datum, with the couple that carries it to "
        "the gear reference point.",
        human, lambda h: rt.gear_report_csv(project, h, system=system))
    return out


# --------------------------------------------------------------------------- #
# The per-module load-case files (the retiring download buttons' channel)
# --------------------------------------------------------------------------- #
def _load_case_files(doc: "OracleDocument") -> List[DataFile]:
    """One file per module that produced a result, through the same owner.

    :func:`sloads.io.load_cases_csv` is the call the per-module CSV button made
    and the call ``cli.py`` makes, so retiring the button moves the channel and
    changes no byte of what it carried (#245 item 2). Keyed by the mapping
    :func:`~sloads.report.oracle_content.run_sections` returns, which means a
    *folded* module -- WTONECG under Weight & Mass Properties -- gets its own
    file under its own name, exactly as it had its own download block.
    """
    from .. import io as io_

    project = doc.project
    if project is None:
        return []
    out: List[DataFile] = []
    for name in sorted(doc.results):
        result = doc.results[name]
        if result is None:
            continue
        ref = _ref(doc, name, "")
        path = _path(LOAD_CASES_DIR, f"{name}.csv")
        header = data_header(doc, name=path, step_key=name, drawn_by=ref)
        try:
            content = io_.load_cases_csv(result, header, system=doc.system)
        except Exception:      # as above
            continue
        if not _has_rows(content):
            continue
        out.append(DataFile(
            path, content,
            contents=f"Every load case {name} produced, as the module itself "
                     "states them: one row per structural load case, or the "
                     "module's own property table where it computes no cases.",
            units="as stated in this manifest's Units section",
            summarised_in=ref))
    return out


# --------------------------------------------------------------------------- #
# The document's own tables and figures
# --------------------------------------------------------------------------- #
#: What a file whose numbers are the document's own says in the manifest's
#: ``units`` column: the package states one unit system, and these files are in
#: it. The applied sets say something else, because they are not.
_MANIFEST_UNITS = "as stated in this manifest's Units section"


def _slug(text: str) -> str:
    """A file-name stem from a printed title: lowercase, words joined by ``_``."""
    keep = [c.lower() if c.isalnum() else " " for c in text]
    return "_".join("".join(keep).split())[:60]


def _walk(section: "Section", tables: List["Table"],
          figures: List["Figure"]) -> None:
    tables.extend(section.tables)
    figures.extend(section.figures)
    for child in section.subsections:
        _walk(child, tables, figures)


def _document_files(doc: "OracleDocument") -> List[DataFile]:
    """One file per appendix table no named file carries, and one per figure."""
    from .oracle_content import appendix_heading, appendix_plan, heading

    index = {}
    for row in doc.plan:
        index[heading(row.number, row.title)] = (row.step_key,
                                                 f"section {row.number}")
    for row in appendix_plan(doc.plan):
        index[appendix_heading(row.title)] = (row.step_key,
                                              f"Appendix {row.number}")
    out: List[DataFile] = []
    seen = set()
    for section in doc.sections:
        step_key, ref = index.get(section.title, ("", section.title))
        tables: List["Table"] = []
        figures: List["Figure"] = []
        _walk(section, tables, figures)

        def keep(name: str, content: str, contents: str,
                 key: str = step_key, where: str = ref) -> None:
            if name in seen or not content:
                return
            seen.add(name)
            out.append(DataFile(
                name, data_header(doc, name=name, step_key=key,
                                  drawn_by=where) + content,
                contents=contents, units=_MANIFEST_UNITS,
                summarised_in=where))

        # Appendix tables only. A body table is printed in the document the
        # package carries and its module file is its superset; an appendix table
        # is the deliverable itself. One that a named file already carries says
        # so and is not written twice.
        if section.title.startswith("Appendix "):
            for table in tables:
                if table.data_file:
                    continue
                keep(_path(f"{_slug(ref)}_{_slug(table.title)}.csv"),
                     table_csv(table),
                     f"{table.title} -- {ref}'s table, as its own file.")
        for figure in figures:
            if figure.data is None:
                continue
            keep(_path(FIGURES_DIR, f"{figure.key}.csv"), figure_csv(figure),
                 f'The numbers behind the figure "{figure.title}" in {ref}: one '
                 "row per plotted point, so a curve the document draws can be "
                 "read as data.")
    return out


def data_files(doc: "OracleDocument") -> List[DataFile]:
    """Every file the issue package's ``data/`` carries, in write order.

    The one entry point, and the subject of **G-OR-15** (each file states its
    own units, basis, axes, step and build) and **G-OR-17** (no orphan in
    either direction between ``data/`` and the document).
    """
    return _named_files(doc) + _load_case_files(doc) + _document_files(doc)


__all__ = [
    "DATA_DIR",
    "FIGURES_DIR",
    "FIGURE_COLUMNS",
    "LOAD_CASES_DIR",
    "DataFile",
    "data_files",
    "data_header",
    "figure_csv",
    "table_csv",
]
