"""``ReportDocument`` -> LaTeX source (Step G8.5).

The renderer is deliberately dumb: it makes no engineering decisions, converts no
units and scales nothing. Every number and every unit marker was decided in
:mod:`sloads.report.content`; this module only decides where they sit on the page.
That split is what makes the content testable without matching LaTeX strings, and
this module testable without a TeX engine.

What it *does* own, and why each matters:

* **Escaping.** Every user-supplied string (project name, engineer, condition
  labels, unit strings) goes through :func:`~sloads.report.plots_tex.escape`. A
  project called ``"Model 100 & 100A"`` or a unit string ``lb/in^2-ULT`` would
  otherwise abort the compile or typeset silently wrong.
* **Controlled-document furniture** (decision G8-1): a title page with the
  document-control and signature block, a table of contents, ``fancyhdr`` running
  heads carrying the project and revision, "page *n* of *m*" footers, and
  ``longtable`` for tables that cross a page break.
* **Absence.** A section with an ``absent_reason`` renders that sentence in place
  of its content -- never an empty table or an empty axis (SUMMARY_REPORT.md §3.4).

Determinism: nothing here reads the clock or a hash-ordered container, so two
renders of one :class:`~sloads.report.content.ReportDocument` are byte-identical
(SUMMARY_REPORT.md §2). Pure: no filesystem, no subprocess. Compiling the result
to PDF needs both and lives in :mod:`sloads.export.pdf`.
"""

from __future__ import annotations

import math
from typing import List, Tuple

from ..units import IN_TO_MM
from .content import Figure, ReportDocument, Section, Table
from .methods import STANDING_DISCLAIMER
from .plots_tex import escape, figure_body_tex

#: Packages the ``.tex`` needs. All are in a standard TeX distribution and in the
#: tectonic bundle -- SUMMARY_REPORT.md §2 forbids anything more exotic, and
#: forbids external image files (hence pgfplots rather than \includegraphics).
#: §2's *Data reference* clause (amended 2026-08-30) lets a report delivered as a
#: **package** read manifest-listed data files from inside it; this report is also
#: offered as a standalone ``.tex`` download, so it references no external file at
#: all -- everything it draws is inline (guarded in ``test_report_latex.py``).
PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=22mm,includeheadfoot]{geometry}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{fancyhdr}
\usepackage{float}
\usepackage{lastpage}
\usepackage{pdflscape}
\usepackage{pgfplots}
\usepackage[hidelinks]{hyperref}
\pgfplotsset{compat=1.16}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.6em}
\renewcommand{\arraystretch}{1.15}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
% The width a table's columns share out between them: the text block less the
% inter-column padding, so proportioned columns fit exactly (see _column_spec).
\newlength{\sltablewidth}
"""

#: The "not analysed" marker. Bold rather than coloured: §4.3/§4.4 require the
#: document to stay legible in greyscale, so nothing may be encoded by colour.
NOT_ANALYSED_MARKER = "NOT ANALYSED"


def _headers(doc: ReportDocument) -> str:
    control = dict(doc.control)
    left = escape(doc.project_name)
    revision = control.get("Revision", "")
    right = escape(f"Rev {revision}") if revision else escape("Rev —")
    return "\n".join([
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        f"\\fancyhead[L]{{\\small {left}}}",
        f"\\fancyhead[R]{{\\small {right}}}",
        r"\fancyfoot[L]{\small LIMIT loads --- SF stated per case, applied nowhere}",
        r"\fancyfoot[R]{\small Page \thepage\ of \pageref{LastPage}}",
        r"\renewcommand{\headrulewidth}{0.4pt}",
        r"\renewcommand{\footrulewidth}{0.4pt}",
        # The running head is set in ``\small``, which is taller than the 12pt
        # ``\headheight`` ``geometry`` leaves by default, and ``fancyhdr`` warned
        # about it once per page -- 77 warnings on the report's own example, all
        # of them the same warning, which is the noise a real one hides in.
        # ``includeheadfoot`` is already set, so the text block moves with it and
        # the margin stays 22mm.
        r"\setlength{\headheight}{14pt}",
    ])


def _title_page(doc: ReportDocument) -> str:
    """Title page + document control + signature block (SUMMARY_REPORT.md §4.1)."""
    rows = []
    for label, value in doc.control:
        if not value and label in ("Checked by", "Approved by", "Revision", "Date"):
            # The signature block SHALL exist even when unsigned: a ruled blank is
            # a line to sign, whereas a dropped row reads as an oversight.
            cell = r"\rule{0pt}{1.2em}\hrulefill"
        else:
            cell = escape(value) or r"\textit{(not set)}"
        rows.append(f"{escape(label)} & {cell} \\\\")
    return "\n".join([
        r"\begin{titlepage}",
        r"\thispagestyle{empty}",
        r"\begin{center}",
        r"{\Large\bfseries " + escape(doc.title) + r"}\\[0.6em]",
        r"{\LARGE " + escape(doc.project_name) + r"}\\[0.4em]",
        r"{\large\bfseries " + escape(doc.badge) + r"}",
        r"\end{center}",
        r"\vspace{1.6em}",
        r"\begin{center}",
        r"\begin{tabular}{@{}l L{0.6\textwidth}@{}}",
        r"\toprule",
        "\n".join(rows),
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{center}",
        r"\vfill",
        r"\begin{center}\begin{minipage}{0.86\textwidth}",
        r"\textbf{Load basis.} " + escape(doc.basis) + r"\\[0.4em]",
        r"\textbf{Units.} " + escape(doc.units_note) + r"\\[0.4em]",
        # Quoted, never restated: the disclaimer is one wording (methods.py), and
        # the title page adds only its pointer to the section that expands it.
        r"\textbf{Status.} " + escape(
            f"{STANDING_DISCLAIMER} See the methods and limitations section."
        ),
        r"\end{minipage}\end{center}",
        r"\vspace{1.2em}",
        r"\end{titlepage}",
    ])


def paragraphs_tex(text: str) -> str:
    """Escaped prose, preserving the statement's paragraphs and indented lines.

    The methods statement is a plain-text block with meaning in its layout (an
    indented ``  - exceedance`` line under its heading). Blank lines separate
    paragraphs; an indented or bulleted line starts a new typeset line inside the
    paragraph rather than being reflowed into it, which would run the exceedance
    list into one sentence.
    """
    out: List[str] = []
    for block in text.replace("\r\n", "\n").split("\n\n"):
        lines = [ln for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        rendered: List[str] = []
        for ln in lines:
            indented = ln[:1].isspace() or ln.lstrip().startswith("-")
            piece = escape(ln.strip())
            if rendered and indented:
                rendered.append(r"\\" + "\n" + piece)
            elif rendered:
                rendered.append(" " + piece)
            else:
                rendered.append(piece)
        out.append("".join(rendered))
    return "\n\n".join(out)


# --------------------------------------------------------------------------- #
# Column widths
# --------------------------------------------------------------------------- #
# A ``p`` column wraps between words but never inside one, so a column narrower
# than its widest unbreakable token (a case ID, "6.833e+05", the header word
# "Maximum") does not wrap -- it prints on top of the next column. Proportioning
# columns by character count alone is therefore not enough: a column's share must
# also be at least what its longest token needs. The model below works in points
# so "at least" means something, using the page geometry this module's own
# preamble sets.
#: A4 (210mm) less the 22mm margins in :data:`PREAMBLE`, in TeX points.
TEXT_WIDTH_PT = (210.0 - 2 * 22.0) * 72.27 / IN_TO_MM
#: The same page turned, **measured** rather than derived from the paper size.
#:
#: A table inside a ``landscape`` environment has this much room, not
#: :data:`TEXT_WIDTH_PT`. Sizing every table to the portrait width regardless
#: squeezed the appendices -- which are all landscape -- into two-thirds of the
#: page they were actually printed on, and pushed the Baron's applied-wing-load
#: table below its own floor for want of space that was there all along.
#:
#: A4's long edge less the margins is 719.9pt, and that is **wrong** by 67pt:
#: ``includeheadfoot`` takes the running head and footer out of the text block,
#: and ``lscape`` swaps in the reduced ``\textheight``. The figure below is
#: ``\the\linewidth`` inside ``\begin{landscape}`` on this module's own
#: preamble. It is taken at the *draft* footskip, the larger of the two, so it
#: understates the room a signed report has -- which is the safe direction: a
#: column then gets slightly more width than asked for, never less.
LANDSCAPE_WIDTH_PT = 652.85
#: LaTeX's default half-gutter, applied twice per column.
TABCOLSEP_PT = 6.0
#: Latin Modern glyph widths at ``\footnotesize``, in TeX points.
#:
#: **Measured, not modelled.** Every printable ASCII character was set in a box
#: and its ``\wd`` read back, on this module's own preamble (11pt article,
#: ``lmodern``, T1). The tables below are that reading, and summing them
#: reproduces a real word's width to a hundredth of a point.
#:
#: What they replace is the reason they exist. The widths used to be a
#: four-class model -- upper, lower, digit, narrow -- scaled off a 0.5 em
#: average, and a model is only ever as good as its worst word. Its worst word
#: was ``assumed``: 34.02pt of Latin Modern against a predicted 30.24, so the
#: Spars column of the wing-attach fitting table was floored 0.79pt below the
#: only token it had to hold, and every row of it overprinted by that much.
#: The floor is a content guarantee (see :func:`_column_widths_pt`), and a
#: guarantee computed from an approximation is not one.
#:
#: Anything outside the table -- an accented letter, an en dash -- is taken as
#: a digit's width, which is Latin Modern's 0.5 em and close to its average.
_GLYPH_PT = {
    '!': 2.57, '"': 3.487, '#': 7.708, '$': 4.625, '%': 7.708, '&': 7.194, "'": 2.57,
    '(': 3.597, ')': 3.597, '*': 4.625, '+': 7.194, ',': 2.57, '-': 3.083, '.': 2.57,
    '/': 4.625, '0': 4.625, '1': 4.625, '2': 4.625, '3': 4.625, '4': 4.625, '5': 4.625,
    '6': 4.625, '7': 4.625, '8': 4.625, '9': 4.625, ':': 2.57, ';': 2.57, '<': 7.194,
    '=': 7.194, '>': 7.194, '?': 4.368, '@': 7.194, 'A': 6.936, 'B': 6.551, 'C': 6.68,
    'D': 7.065, 'E': 6.295, 'F': 6.037, 'G': 7.258, 'H': 6.936, 'I': 3.339, 'J': 4.753,
    'K': 7.193, 'L': 5.78, 'M': 8.478, 'N': 6.936, 'O': 7.194, 'P': 6.295, 'Q': 7.194,
    'R': 6.808, 'S': 5.139, 'T': 6.68, 'U': 6.936, 'V': 6.936, 'W': 9.505, 'X': 6.936,
    'Y': 6.936, 'Z': 5.653, '[': 2.57, '\\': 4.625, ']': 2.57, '^': 5.0, '_': 6.936,
    '`': 2.57, 'a': 4.625, 'b': 5.139, 'c': 4.111, 'd': 5.139, 'e': 4.114, 'f': 2.826,
    'g': 4.625, 'h': 5.139, 'i': 2.57, 'j': 2.826, 'k': 4.882, 'l': 2.57, 'm': 7.708,
    'n': 5.139, 'o': 4.625, 'p': 5.139, 'q': 4.882, 'r': 3.618, 's': 3.649, 't': 3.597,
    'u': 5.139, 'v': 4.882, 'w': 6.68, 'x': 4.882, 'y': 4.882, 'z': 4.111, '{': 4.625,
    '|': 2.57, '}': 4.625, '~': 5.0,
}

_GLYPH_BOLD_PT = {
    '!': 3.242, '"': 4.488, '#': 8.875, '$': 5.325, '%': 8.875, '&': 8.283, "'": 2.958,
    '(': 4.142, ')': 4.142, '*': 5.325, '+': 8.283, ',': 2.958, '-': 3.55, '.': 2.958,
    '/': 5.325, '0': 5.325, '1': 5.325, '2': 5.325, '3': 5.325, '4': 5.325, '5': 5.325,
    '6': 5.325, '7': 5.325, '8': 5.325, '9': 5.325, ':': 2.958, ';': 2.958, '<': 8.05,
    '=': 8.283, '>': 8.05, '?': 5.029, '@': 8.283, 'A': 8.036, 'B': 7.568, 'C': 7.691,
    'D': 8.159, 'E': 6.989, 'F': 6.693, 'G': 8.369, 'H': 8.319, 'I': 4.017, 'J': 5.497,
    'K': 8.332, 'L': 6.397, 'M': 10.094, 'N': 8.319, 'O': 8.0, 'P': 7.272, 'Q': 8.0,
    'R': 8.197, 'S': 5.917, 'T': 7.408, 'U': 8.178, 'V': 8.036, 'W': 11.005,
    'X': 8.036, 'Y': 8.08, 'Z': 6.508, '[': 2.968, '\\': 5.175, ']': 2.958, '^': 5.299,
    '_': 8.287, '`': 2.958, 'a': 5.371, 'b': 5.917, 'c': 4.733, 'd': 5.917, 'e': 4.887,
    'f': 4.309, 'g': 5.425, 'h': 5.92, 'i': 2.958, 'j': 3.254, 'k': 5.695, 'l': 2.958,
    'm': 8.881, 'n': 5.92, 'o': 5.325, 'p': 5.917, 'q': 5.794, 'r': 4.393, 's': 4.201,
    't': 4.142, 'u': 5.92, 'v': 5.621, 'w': 7.702, 'x': 5.65, 'y': 5.621, 'z': 4.733,
    '{': 5.175, '|': 2.875, '}': 5.175, '~': 5.245,
}

#: Width of a character not in the tables above: a digit's, Latin Modern's 0.5 em.
_DEFAULT_GLYPH_PT = 4.625
#: Table font sizes, as a scale on the ``\footnotesize`` widths above.
#:
#: One font at two sizes, so the scale is exact: the alphabet measures
#: 118.01pt at ``\footnotesize`` and 127.58pt at ``\small``. The old model put
#: the ratio at 5.0/4.5, which is 2.8 % wide of it.
_SIZE_SCALE = {r"\footnotesize": 1.0, r"\small": 1.0811}


def _token_width(token: str, *, bold: bool = False) -> float:
    r"""``token``'s width at ``\footnotesize``, in points.

    Kerning is not modelled: the sum of the glyphs is at worst a few tenths of
    a point wide of the truth, which for a floor is the safe direction.
    """
    glyphs = _GLYPH_BOLD_PT if bold else _GLYPH_PT
    return math.fsum(glyphs.get(ch, _DEFAULT_GLYPH_PT) for ch in token)


#: Cell width beyond which a column stops asking for more and wraps instead --
#: one long note must not squeeze every other column to nothing. About 26
#: characters at ``\footnotesize``.
_MAX_CELL_PT = 117.0
#: Slack added to every column so a token never sits flush against the rule.
_PAD_PT = 3.0


def _column_asks_pt(table: Table, size: str
                    ) -> Tuple[List[float], List[float], List[float]]:
    """``(required, desired, natural)`` in points, per column, at ``size``.

    ``required`` is the width the column's longest **unbreakable token** needs:
    a ``p`` column wraps between words and never inside one, so a column
    narrower than this does not wrap, it overprints its neighbour. It is a
    floor, and :func:`_column_widths_pt` treats it as one.

    The header is measured **in the bold face**, because it is set bold -- from
    :data:`_GLYPH_BOLD_PT`, not by scaling the roman widths. Latin Modern's
    bold is not one factor wider: a bold comma is 15 % over its roman, a bold
    ``W`` 4 %, and a header is exactly the short mixed string where the spread
    between them decides whether it fits.
    """
    scale = _SIZE_SCALE[size]
    required: List[float] = []
    desired: List[float] = []
    natural: List[float] = []
    for i, header in enumerate(table.columns):
        body = [str(row[i]) for row in table.rows if i < len(row)]
        head_word = max((_token_width(w, bold=True) for w in header.split()),
                        default=1.0)
        head_cell = _token_width(header, bold=True)
        longest_word = max([head_word]
                           + [_token_width(w) for cell in body
                              for w in cell.split()])
        longest_cell = max([head_cell] + [_token_width(c) for c in body] or [1.0])
        required.append(longest_word * scale + _PAD_PT)
        desired.append(max(min(longest_cell, _MAX_CELL_PT) * scale + _PAD_PT,
                           required[-1]))
        natural.append(max(longest_cell * scale + _PAD_PT, desired[-1]))
    return required, desired, natural


def _column_widths_pt(table: Table, size: str, available: float) -> List[float]:
    """Column widths in points: what each column wants, capped to what fits.

    Each column asks for ``desired`` (its typical cell, capped) but **never less
    than** ``required`` (its longest unbreakable token). When the asks exceed
    the page, the excess is taken from the columns that have slack between the
    two -- so a wide prose column shrinks and wraps while a numeric column keeps
    the width its numbers need.

    **The floor is absolute.** This used to scale every column proportionally
    when the slack ran out, floor included, and the result was not a tight table
    but a corrupt one: on ``ga6_normal`` the ``14 CFR`` column of the pull-up
    manoeuvre table needed 63pt for ``23.423(a)(1)`` and was given 26, so the
    regulation printed on top of the CG case as ``23.423(a)(1)G4`` and a reader
    could not tell which CG case the condition was run at. A table that will not
    fit is turned onto its side by :func:`_table_size_and_spec`; it is never
    made to overlap itself. Returning widths that sum past ``available`` is the
    honest outcome of last resort -- visible, and impossible to mistake for a
    number.
    """
    required, desired, natural = _column_asks_pt(table, size)
    excess = math.fsum(desired) - available
    if excess <= 0:
        # Room to spare: hand it to the columns the cap held back, so a two-column
        # table of prose fills the page instead of sitting in a narrow ribbon.
        unmet = [n - d for n, d in zip(natural, desired)]
        total_unmet = math.fsum(unmet)
        if total_unmet <= 0:
            return desired
        spare = -excess
        share = min(1.0, spare / total_unmet)
        return [d + un * share for d, un in zip(desired, unmet)]
    slack = [d - r for d, r in zip(desired, required)]
    total_slack = math.fsum(slack)
    if total_slack >= excess:
        return [d - excess * s / total_slack for d, s in zip(desired, slack)]
    return required


#: Row count up to which a table is set as one unbreakable float.
#:
#: Above it a table cannot fit a page whatever is done to it, and ``longtable``
#: -- which is what handles that honestly -- takes over. The threshold is
#: deliberately generous: nearly every table this report prints is a handful of
#: rows, and the failure this prevents (a header and a rule stranded above no
#: data) is worse than a table drifting to the next page.
UNBREAKABLE_ROWS = 30


def _fits(table: Table, size: str, available: float) -> bool:
    """Whether ``table`` can hold **every** unbreakable token at ``size``."""
    required, _desired, _natural = _column_asks_pt(table, size)
    return math.fsum(required) <= available + 0.01


def table_orientation(table: Table, *, in_landscape: bool = False) -> bool:
    r"""Whether this table has to be turned onto its side to hold its content.

    ``False`` when it fits the upright text block at one of its sizes, or when
    the section is landscape already. A table is turned only when it cannot be
    set upright without a column falling below the width its longest token needs
    -- the failure that used to print one column on top of another.

    Turning is the remedy rather than a third, smaller type size (owner,
    2026-09-07): another step down buys about 12 % and fails again on the next
    wide table, while the page has 53 % more room the moment it is turned, and
    8pt type in a signed engineering document is a worse trade than a rotated
    page. The mechanism is the one the appendices already use.
    """
    if in_landscape:
        return False
    available = TEXT_WIDTH_PT - 2 * TABCOLSEP_PT * len(table.columns)
    sizes = (r"\footnotesize",) if table.small else (r"\small", r"\footnotesize")
    return not any(_fits(table, size, available) for size in sizes)


def _table_size_and_spec(table: Table, *,
                         in_landscape: bool = False) -> Tuple[str, str]:
    r"""``(font-size command, column spec)`` for ``table``.

    A table that cannot hold its own tokens at ``\small`` drops to
    ``\footnotesize`` rather than overflowing -- the case index and the coverage
    matrix are wide by nature, and shrinking the type is the trade §4.4 already
    accepts for them. One that cannot hold them at ``\footnotesize`` either is
    set on a turned page, and is measured against the width it will actually
    have there.
    """
    ncols = len(table.columns)
    turned = in_landscape or table_orientation(table)
    page = LANDSCAPE_WIDTH_PT if turned else TEXT_WIDTH_PT
    available = page - 2 * TABCOLSEP_PT * ncols
    sizes = (r"\footnotesize",) if table.small else (r"\small", r"\footnotesize")
    # The last size is used whether or not it fits -- there is nothing smaller to
    # fall back to. Seeding from it (rather than from ``None``) keeps both names
    # bound on every path, so neither the reader nor a type checker has to prove
    # the loop runs at least once.
    size = sizes[-1]
    widths = _column_widths_pt(table, size, available)
    for candidate in sizes:
        size = candidate
        widths = _column_widths_pt(table, candidate, available)
        if math.fsum(widths) <= available + 0.01:
            break
    # Columns share out ``\sltablewidth`` -- the text block with the inter-column
    # padding already taken off (:func:`_table_tex` sets it). Subtracting the
    # padding per column as well would take it twice and leave every column a few
    # points too narrow, which is exactly how a number ends up on top of its
    # neighbour.
    specs = [r"L{%.4f\sltablewidth}" % (w / available) for w in widths]
    return size, "@{}" + "".join(specs) + "@{}"


def _cell(table: Table, column: str, value: str) -> str:
    text = escape(value)
    if table.status_column and column == table.status_column and \
            value.strip().upper() == NOT_ANALYSED_MARKER:
        return r"\textbf{" + text + "}"
    return text


def table_tex(table: Table, *, in_landscape: bool = False) -> str:
    """One table as a ``longtable`` (booktabs rules, repeated header on a break).

    ``in_landscape`` says the section is turned already, so this table both
    measures against the wider page and must not open a ``landscape``
    environment of its own -- nesting them would turn the page back.
    """
    if not table.rows:
        return ""
    ncols = len(table.columns)
    header = " & ".join(r"\textbf{" + escape(c) + "}" for c in table.columns) + r" \\"
    body = []
    last = len(table.rows) - 1
    for index, row in enumerate(table.rows):
        cells = [_cell(table, table.columns[i] if i < ncols else "", str(row[i]))
                 for i in range(min(ncols, len(row)))]
        cells += [""] * (ncols - len(cells))
        # ``\\*`` forbids a page break after this row. Applied to the first and
        # the last, which is widow and orphan control for a table: without it
        # longtable happily broke between the final row and ``\endlastfoot``,
        # printing the repeated header and the bottom rule alone at the top of
        # the next page with no data under them (Baron 58, section 2.3, GUI
        # review 2026-08-30). Only those two rows are pinned, so a genuinely
        # long table -- the case index, the coverage matrix -- still breaks
        # wherever it needs to.
        terminator = r" \\*" if index in (0, last) and last > 0 else r" \\"
        body.append(" & ".join(cells) + terminator)
    if table.data_ref:
        # A packaged report ships the table's body as a generated fragment and
        # reads it here (OR-23). The document therefore cannot disagree with the
        # data it ships, because it is the same bytes -- which is why no
        # drift-guard between two renderings is owed. Permitted by
        # ``SUMMARY_REPORT.md`` §2 *Data reference* for a manifest-carrying
        # package only; a standalone ``.tex`` sets no ``data_ref`` and is
        # guarded to keep it that way.
        return r"\input{" + table.data_ref + "}"
    turned = table_orientation(table, in_landscape=in_landscape)
    size, spec = _table_size_and_spec(table, in_landscape=in_landscape or turned)
    width = r"\setlength{\sltablewidth}{\dimexpr\linewidth-%d\tabcolsep\relax}" % (2 * ncols)
    if len(table.rows) <= UNBREAKABLE_ROWS:
        # A table short enough to fit a page is set as one unbreakable float, so
        # it moves whole rather than splitting. ``longtable`` split the Baron's
        # five-row Mach table between its last row and ``\endlastfoot`` and put
        # the repeated header and the bottom rule alone at the top of the next
        # page, under no data (GUI review, 2026-08-30) -- a break that no
        # inter-row penalty prevents, because the foot is not a row.
        #
        # ``[H]``, the same placement the figures use and for the same reason:
        # a table belongs to the prose above it. ``[!ht]`` was tried first and
        # floated four of the Baron's five section-2 tables onto a page of their
        # own, away from the subsections that introduce them. ``[H]`` does not
        # float -- when the table will not fit, the page breaks and the whole
        # table moves, which is the behaviour wanted here.
        out = [
            r"\begin{table}[H]", r"\centering", "{" + size, width,
            r"\caption{" + escape(table.title) + "}",
            r"\begin{tabular}{" + spec + "}",
            r"\toprule", header, r"\midrule",
            "\n".join(body),
            r"\bottomrule",
            r"\end{tabular}}", r"\end{table}",
        ]
    else:
        out = [
            "{" + size, width,
            r"\begin{longtable}{" + spec + "}",
            r"\caption{" + escape(table.title) + r"}\\",
            r"\toprule", header, r"\midrule", r"\endfirsthead",
            r"\toprule", header, r"\midrule", r"\endhead",
            r"\bottomrule", r"\endlastfoot",
            "\n".join(body),
            r"\end{longtable}}",
        ]
    if table.note:
        out.append(r"{\footnotesize\textit{" + escape(table.note) + "}}")
    body_tex = "\n".join(out)
    if turned:
        # ``pdflscape`` clears the page, so the table lands on a turned page of
        # its own with its caption and its note. That is the cost of the ruling
        # and it is paid here rather than by a column overprinting another.
        body_tex = "\n".join([r"\begin{landscape}", body_tex, r"\end{landscape}"])
    return body_tex


def figure_tex(figure: Figure) -> str:
    body = figure_body_tex(figure)
    if not body:
        # An absent figure states why in place of the axis (§3.4). The reason is
        # a bare phrase in the content model, so the "Not analysed" marker is
        # added exactly once here rather than baked into every reason string.
        reason = figure.absent_reason or "no data for this figure"
        return (r"\textbf{" + escape(figure.title) + r" --- not analysed.} "
                + escape(reason))
    # ``[H]`` (the ``float`` package), not ``[htbp]``: each figure is followed by
    # its own corner-point table (§4.3), and a float that drifts three pages away
    # from the numbers it belongs to breaks that pairing.
    # The optional argument is what the List of Figures carries. Without it a
    # caption that explains the figure -- which a caption in a report a reviewer
    # signs has to -- is repeated in full in the front matter, once per figure,
    # and the list stops being a list. The title alone is the entry.
    parts = [r"\begin{figure}[H]", r"\centering", body,
             r"\caption[" + escape(figure.title) + "]{" + escape(figure.title)
             + (": " + escape(figure.caption) if figure.caption else "") + "}",
             r"\end{figure}"]
    return "\n".join(parts)


def section_tex(section: Section, level: int, *,
                in_landscape: bool = False) -> str:
    r"""One section (and its subsections), unnumbered but present in the ToC.

    ``\section*`` rather than ``\section`` because the content model already
    carries the document's own numbering ("1. Input summary", "Appendix A ..."),
    and letting LaTeX number them too would print "1 1. Input summary".

    ``in_landscape`` is inherited by the subsections, because ``landscape`` is a
    property of the *appendix* while its tables live in its subsections: read
    off the subsection alone, a table inside a turned appendix would believe it
    was upright, measure against the narrow page and open a second ``landscape``
    environment -- which turns the page back to portrait.
    """
    turned = in_landscape or section.landscape
    command = {0: "section", 1: "subsection", 2: "subsubsection"}.get(level, "paragraph")
    title = escape(section.title)
    out = []
    if section.page_break and not section.landscape:
        # ``landscape`` breaks the page itself; emitting both would leave a blank.
        out.append(r"\clearpage")
    out += [f"\\{command}*{{{title}}}",
           f"\\addcontentsline{{toc}}{{{command}}}{{{title}}}"]
    if section.absent_reason:
        out.append(r"\textbf{" + escape(section.absent_lead) + ".} "
                   + escape(section.absent_reason))
    for paragraph in section.body:
        out.append(paragraphs_tex(paragraph))
    for figure in section.figures:
        out.append(figure_tex(figure))
    for table in section.tables:
        out.append(table_tex(table, in_landscape=turned))
    for sub in section.subsections:
        out.append(section_tex(sub, level + 1, in_landscape=turned))
    body = "\n\n".join(p for p in out if p)
    if section.landscape:
        body = "\n\n".join([r"\begin{landscape}", body, r"\end{landscape}"])
    return body


def render_document(doc: ReportDocument) -> str:
    """The whole ``.tex`` source for ``doc``."""
    parts = [
        PREAMBLE,
        _headers(doc),
        r"\begin{document}",
        _title_page(doc),
        r"\tableofcontents",
        r"\newpage",
    ]
    parts += [section_tex(s, 0) for s in doc.sections]
    parts.append(r"\end{document}")
    return "\n\n".join(parts).rstrip() + "\n"


def render_report(project, **kwargs) -> str:
    """Build and render in one call: ``Project`` -> ``.tex`` source.

    ``kwargs`` are :func:`sloads.report.content.build_report`'s -- ``system``,
    ``generated``, ``tool_version``, ``scope``, ``deselected_case_ids`` and the
    precomputed ``module_results``/``components``.
    """
    from .content import build_report

    return render_document(build_report(project, **kwargs))


__all__ = [
    "PREAMBLE",
    "escape",
    "figure_tex",
    "paragraphs_tex",
    "render_document",
    "render_report",
    "section_tex",
    "table_tex",
]
