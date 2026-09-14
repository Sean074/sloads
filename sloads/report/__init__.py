"""Rendering and reporting: tables, text, and the controlled issue document.

``sloads/report.py`` became this package at **Step G8.1**, the same mechanical
move ``models.py`` -> ``models/`` made at M3-1. Everything that existed before
lives in :mod:`sloads.report.render` and is re-exported here, so every prior
import (``from sloads.report import load_cases_to_rows``) keeps working
unchanged.

Layout:

* :mod:`~sloads.report.render`   -- tables, the text report, and the
  **limit -> ultimate boundary** for tabular output (pre-existing code).
* :mod:`~sloads.report.methods`  -- the single source of the methods &
  limitations statement, plus its CSV ``#`` / BDF ``$`` comment-block wrappers.
* :mod:`~sloads.report.coverage` -- the FAR 23 Subpart C coverage matrix.
* :mod:`~sloads.report.content`   -- the content model (:class:`Section`,
  :class:`Table`, :class:`Figure`, :class:`PlotData`) and the plot data the
  documents and the GUI draw from: *what a report says*.
* :mod:`~sloads.report.front_sections` -- the cross-cutting sections: axes and
  sign conventions, the governing factors, the FAR coverage matrix, the package
  file list.
* :mod:`~sloads.report.oracle_content` -- ``Project`` + module results ->
  :class:`~sloads.report.oracle_content.OracleDocument`.
* :mod:`~sloads.report.latex`     -- ``Section`` -> ``.tex``: *how it looks*;
  :mod:`~sloads.report.oracle_latex` assembles the document around it.
* :mod:`~sloads.report.plots_tex` -- the figures as pgfplots source.

The content/renderer split is what lets a test assert
``doc.section("Design speeds").table.rows`` instead of matching LaTeX strings.
The document's content rules are ``docs/10_standard/ORACLE_REPORT.md``.

**One document, since #270.** There were two: this package built the oracle
report *and* the summary report ``app/views/export_report.py`` downloaded. That
front-end retired (note 57, D-57.6) and took its only consumer with it, so
``content.build_report`` and the document half of :mod:`~sloads.report.latex`
were deleted with it (note 60, D-60.11) -- after the four cross-cutting sections
only the summary report had were merged into the surviving document at #278.

Everything in this package is **pure**: no filesystem, no subprocess, no
Streamlit. Compiling a ``.tex`` to PDF needs both, so that one impure piece lives
outside, in :mod:`sloads.export.pdf`, and nothing here imports it.
"""

from __future__ import annotations

from .content import (
    ComponentLoads,
    Figure,
    PlotData,
    Section,
    Series,
    Table,
    component_loads,
)
from .coverage import (
    COVERED,
    FAR23_SUBPART_C,
    NOT_ANALYSED,
    NOT_APPLICABLE,
    OUT_OF_SCOPE,
    CoverageRow,
    coverage_matrix,
    coverage_summary,
)
from .methods import (
    bdf_comment_block,
    csv_comment_block,
    methods_statement,
    strip_comment_lines,
)
from .render import (
    SUMMARY_GROUP_BY,
    SUMMARY_SHAPES,
    LoadChannel,
    critical_rows,
    envelope_extremes,
    format_value,
    governing_loads_table,
    has_load_case_data,
    load_cases_to_rows,
    module_text_report,
    results_to_rows,
    summary_rows,
    text_report,
    ultimate_units,
    weight_station_rows,
)

__all__ = [
    "COVERED",
    "FAR23_SUBPART_C",
    "NOT_ANALYSED",
    "NOT_APPLICABLE",
    "OUT_OF_SCOPE",
    "SUMMARY_GROUP_BY",
    "SUMMARY_SHAPES",
    "ComponentLoads",
    "CoverageRow",
    "Figure",
    "LoadChannel",
    "PlotData",
    "Section",
    "Series",
    "Table",
    "bdf_comment_block",
    # --- G8.4-G8.5: the summary report document ----------------------------- #
    "component_loads",
    # --- G8.4: FAR 23 Subpart C coverage ----------------------------------- #
    "coverage_matrix",
    "coverage_summary",
    "critical_rows",
    "csv_comment_block",
    "envelope_extremes",
    "format_value",
    "governing_loads_table",
    "has_load_case_data",
    "load_cases_to_rows",
    # --- G8.3: the methods & limitations statement ------------------------- #
    "methods_statement",
    "module_text_report",
    "results_to_rows",
    "strip_comment_lines",
    "summary_rows",
    "text_report",
    "ultimate_units",
    "weight_station_rows",
]
