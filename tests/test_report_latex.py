"""The ``.tex`` renderer and its pgfplots figures (Step G8.5).

The renderer's failure modes are cheap to pin and expensive to miss:

* **An unescaped special aborts the compile** (or, worse, typesets silently
  wrong) the first time a project is called "Model 100 & 100A" — and every
  project name, engineer, condition label and unit string is user-supplied.
* **A non-deterministic render** makes the diff between two revisions of one
  report unreadable, which is the whole point of a controlled document
  (``SUMMARY_REPORT.md`` §2).
* **A figure that quietly loses its data** leaves a blank axis where a boundary
  should be; §4.3 requires the corner points to be readable *and* plotted.

These run without a TeX engine — compiling is ``test_pdf_compile.py``'s job.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sloads.modules  # noqa: F401  (module registration)
from sloads import Project, io
from sloads.modules.structural_speeds import design_speed_values
from sloads.report.content import PlotData, Series, build_report
from sloads.report.latex import NOT_ANALYSED_MARKER, render_document, render_report
from sloads.report.plots_tex import escape, plot_tex, vn_diagram_tex
from sloads.units import UnitSystem

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")
_CONCEPT = os.path.join(_EXAMPLES, "concept_regional_jet.project.json")
_CONCEPT_HEAVY = os.path.join(_EXAMPLES, "concept_heavy.project.json")
#: A second FAR 23 (non-concept) fixture, so the concept-caveat test proves the
#: caveat is conditional rather than merely present. Every twin in ``examples/``
#: is a concept-category airplane, which is why this one is another GA single.
_GA_2 = os.path.join(_EXAMPLES, "cessna_210.project.json")
_TWIN = os.path.join(_EXAMPLES, "dhc8_dash8.project.json")


def _tex(path=_GA, **kwargs) -> str:
    kwargs.setdefault("tool_version", "test")
    return render_report(io.load_project(path), **kwargs)


# --------------------------------------------------------------------------- #
# It renders at all, for every fixture family
# --------------------------------------------------------------------------- #
def test_renders_for_every_fixture_family():
    for path in (_GA, _TWIN, _CONCEPT, _CONCEPT_HEAVY):
        tex = _tex(path)
        assert tex.startswith("\\documentclass")
        assert tex.rstrip().endswith(r"\end{document}")
        assert r"\tableofcontents" in tex


def test_renders_for_an_empty_project():
    """A half-filled project still produces a document — the sections it cannot
    fill say so (§3.4)."""
    tex = render_report(Project(name="empty"))
    assert r"\end{document}" in tex
    assert r"\textbf{Not analysed.}" in tex


def test_two_renders_are_byte_identical():
    """§2: determinism. A timestamp is the caller's to supply, never the
    renderer's to read from the clock."""
    kwargs = dict(tool_version="test", generated="2026-08-05 09:00")
    assert _tex(**kwargs) == _tex(**kwargs)


# --------------------------------------------------------------------------- #
# Escaping
# --------------------------------------------------------------------------- #
def test_escapes_latex_specials_in_a_project_name():
    project = io.load_project(_GA)
    project.name = "Model 100 & 100A_50% #2 ~$x^2$"
    project.engineer = "A. Engineer {contract}"
    tex = render_report(project, tool_version="test")
    # The raw specials never reach the document...
    assert "100A_50" not in tex
    assert "& 100A" not in tex.replace(r"\& 100A", "")
    # ...and their escaped forms do.
    for escaped in (r"\&", r"\_", r"\%", r"\#", r"\textasciitilde{}",
                    r"\textasciicircum{}", r"\{", r"\}"):
        assert escaped in tex


def test_escape_maps_units_and_prose_glyphs_to_portable_latex():
    """The unit labels and prose carry glyphs pdflatex cannot typeset raw."""
    assert escape("N·m") == r"N$\cdot$m"
    assert escape("m²") == r"m\textsuperscript{2}"
    assert escape("lb/in^2-ULT") == r"lb/in\textasciicircum{}2-ULT"
    assert escape("a — b") == "a --- b"
    assert escape("α") == r"$\alpha$"
    # Anything left outside ASCII is dropped rather than risking the compile.
    assert escape("ok中") == "ok"


def test_si_render_carries_si_markers_only():
    tex = _tex(system=UnitSystem.SI)
    assert "N-ULT" in tex and "Nm-ULT" in tex
    assert "lbs-ULT" not in tex


# --------------------------------------------------------------------------- #
# The content that must reach the page (§3.1, §4.1, §4.4)
# --------------------------------------------------------------------------- #
def test_title_page_states_the_basis_the_units_and_the_signature_block():
    tex = _tex()
    # Inverted by note 49 OR-116/OR-117: the title page states the basis AND
    # whose job the factor is, because "LIMIT" alone leaves a reader to guess
    # whether sizing has already happened.
    assert "All loads are LIMIT" in tex
    assert "applied nowhere" in tex and "sizing analysis" in tex
    assert "Airspeed is KEAS" in tex
    assert r"\hrulefill" in tex, "unsigned control rows must still leave a line"
    assert r"\pageref{LastPage}" in tex, "a controlled document numbers page n of m"


def test_the_sf_column_is_present_and_the_ult_marker_is_not_on_data():
    """Under note 49 OR-116 the report is LIMIT, so the ``SF`` column carries the
    basis and no data cell is marked ``-ULT``.

    This replaces ``test_ultimate_markers_and_sf_columns_are_present``, which
    asserted ``"lbs-ULT" in tex``. That assertion still passes today -- but only
    because the methods stamp *explains* the marker in prose ("...which state
    SF=1.0 and carry a '-ULT' marker (lbs-ULT, ...)"). A gate satisfied by the
    explanation of a thing rather than the thing is no gate at all, which is why
    the check below is on table rows and the prose is excluded from it.
    """
    tex = _tex()
    assert r"\textbf{SF}" in tex, "the SF column carries the basis; it must exist"
    # The GA fixture exports no already-ultimate case to a report table, so every
    # marker in the document belongs to the stamp's own explanation of it.
    explanation = tex.split("-ULT' marker")[0] if "-ULT' marker" in tex else tex
    assert "-ULT" not in explanation, (
        "a data cell is marked -ULT on a LIMIT report; under OR-118 the marker "
        "survives only on 23.367(a)(2) and 23.561(b)")


def test_not_analysed_rows_are_visually_distinct_without_colour():
    """§4.4: the coverage matrix is how a reviewer finds gaps, so its gap rows
    are emphasised — in bold, because §4.3 requires greyscale legibility."""
    tex = _tex()
    assert r"\textbf{" + NOT_ANALYSED_MARKER + "}" in tex
    assert "color" not in tex.lower().replace("hidelinks", "")


def test_concept_caveat_appears_only_in_concept_fixtures():
    for path in (_CONCEPT, _CONCEPT_HEAVY):
        assert "UNVERIFIED EXTRAPOLATION" in _tex(path)
    for path in (_GA, _GA_2):
        assert "UNVERIFIED EXTRAPOLATION" not in _tex(path)


def test_wide_tables_drop_to_a_smaller_font_rather_than_overflowing():
    tex = _tex()
    assert r"\footnotesize" in tex
    assert r"\begin{longtable}" in tex


# --------------------------------------------------------------------------- #
# Figures
# --------------------------------------------------------------------------- #
def test_vn_figure_plots_the_corner_speeds_it_tabulates():
    """§4.3: the plotted boundary and the corner table are the same numbers."""
    project = io.load_project(_GA)
    speeds = design_speed_values(project, project.speeds)
    doc = build_report(project, tool_version="test")
    figure = doc.section("V-n diagram").figures[0]
    tex = vn_diagram_tex(figure.data)
    coordinates = [float(m) for m in re.findall(r"\(([-0-9.e+]+),", tex)]
    assert any(abs(v - speeds.va) < 0.5 for v in coordinates), "VA is not plotted"
    assert any(abs(v - speeds.vd) < 0.5 for v in coordinates), "VD is not plotted"
    corner = doc.section("V-n diagram").tables[0]
    assert [row[0] for row in corner.rows] == ["VS", "VSF", "VA", "VC", "VD", "VF"]


def test_figures_are_greyscale_line_styles_not_colours():
    """§4.3: traces are distinguished by line style, never by colour — a report
    is read in greyscale print as often as on screen."""
    tex = _tex()
    for style in ("solid", "dashed", "dotted"):
        assert style in tex
    assert "[black," in tex
    assert r"\definecolor" not in tex and "color=" not in tex


def test_plot_tex_is_empty_when_there_is_nothing_to_draw():
    """An empty axis is worse than a stated absence, so the emitter refuses."""
    assert plot_tex(PlotData("x", "y", [])) == ""
    assert plot_tex(PlotData("x", "y", [Series("empty", [], [])])) == ""


def test_plot_tex_labels_are_escaped():
    tex = plot_tex(PlotData("V & n", "Weight (m²)", [Series("a_b", [0, 1], [0, 1])]))
    assert r"V \& n" in tex and r"m\textsuperscript{2}" in tex and r"a\_b" in tex


def _anchor_of(tex: str, label: str) -> str:
    """The ``anchor=`` a marker label was emitted with."""
    match = re.search(r"\\node\[anchor=([a-z ]+), font=\\tiny\] at "
                      r"\(axis cs:[^)]*\) \{" + re.escape(label) + r"\};", tex)
    assert match, f"no marker label {label!r} in the emitted figure"
    return match.group(1)


def test_an_uncrowded_marker_label_still_sits_above_its_point():
    """The placement rule must not move a label that had no reason to move.

    Every marker label was ``anchor=south`` before 2026-09-01. That is still the
    right answer wherever nothing is in the way, and it leads the candidate
    order so it also wins every tie -- which is what keeps the change confined
    to the labels that were actually colliding.
    """
    data = PlotData("x", "y", [Series("line", [0.0, 10.0], [0.0, 0.0])],
                    points=[("alone", 5.0, 8.0)])
    assert _anchor_of(plot_tex(data), "alone") == "south"


def test_a_marker_label_is_placed_off_the_line_it_sits_on():
    """A label is not written through the ink beside it.

    The marker here sits just below a horizontal line, which is where the GA6's
    gust design points sit on the V-n boundary: ``anchor=south`` would put the
    text straight across it. The rule is only required to move the label off the
    line, not to prefer a particular side -- asserting the side would be
    asserting the arithmetic rather than the property.
    """
    data = PlotData("x", "y", [Series("line", [0.0, 10.0], [1.0, 1.0]),
                               Series("frame", [0.0, 10.0], [0.0, 4.0])],
                    points=[("on the line", 5.0, 0.97)])
    assert _anchor_of(plot_tex(data), "on the line") != "south"


def test_a_long_label_is_scored_over_its_whole_length():
    """A label is a box, not the point at the end nearest its marker.

    Scoring one point beside the marker placed the GA6's "CG3 / fwd light" so
    that its first character cleared the loading edge and the remaining fourteen
    did not. Same geometry both times here: only the length of the text differs,
    and the long one has to go somewhere the short one need not.
    """
    # A vertical line a short label clears and a long one reaches across.
    series = [Series("frame", [0.0, 10.0], [0.0, 0.0]),
              Series("wall", [6.0, 6.0], [0.0, 10.0])]
    short = PlotData("x", "y", series, points=[("x", 5.0, 5.0)])
    long = PlotData("x", "y", series,
                    points=[("a considerably longer label", 5.0, 5.0)])
    assert _anchor_of(plot_tex(short), "x") == "south"
    assert _anchor_of(plot_tex(long), "a considerably longer label") != "south"


def test_the_axes_print_fixed_ticks_rather_than_a_shared_multiplier():
    """An altitude axis said "0.5 1 1.5" under a "*10^4" (owner, 2026-09-01).

    A reviewer signing a report reads a tick; they should not have to decode
    one. Asserted on the emitter rather than on one figure, because the next
    axis with a large range must not have to rediscover this.
    """
    tex = plot_tex(PlotData("V", "Altitude (ft)",
                            [Series("h", [1.0, 2.0], [0.0, 18000.0])]))
    assert "scaled ticks=false" in tex
    assert tex.count("/pgf/number format/fixed") == 2       # both axes
    assert tex.count("/pgf/number format/1000 sep={,}") == 2


def test_figures_do_not_float_away_from_their_corner_table():
    tex = _tex()
    assert r"\begin{figure}[H]" in tex
    assert r"\begin{figure}[htbp]" not in tex


def test_the_summary_content_sets_no_data_ref():
    """The structural half of the standalone rule.

    ``Table.data_ref`` is what makes a table read a shipped fragment instead of
    inlining its rows (design note 44, OR-23) -- correct for the oracle report's
    issue package, wrong for a report delivered as a bare ``.tex`` download.
    Asserting it over the content model says *why* the string scan below passes,
    and it keeps saying so if the renderer's syntax ever changes.
    """
    from sloads.report.content import build_report

    for path in (_GA, _CONCEPT):
        doc = build_report(io.load_project(path), tool_version="test")
        stack = list(doc.sections)
        while stack:
            section = stack.pop()
            stack.extend(section.subsections)
            for table in section.tables:
                assert not table.data_ref, (
                    f"{table.title!r} would read an external fragment, and the "
                    "summary report is delivered as a standalone .tex")


def test_the_standalone_tex_references_no_external_file():
    """SUMMARY_REPORT.md §2 *Data reference*: a report delivered as a standalone
    ``.tex`` -- which this one is, via the Export page's own download button --
    SHALL NOT reference any external file. The packaged-report permission (design
    note 44 OR-23) is scoped to reports that travel with a manifest, so the
    summary report keeps every table and every figure coordinate inline.
    """
    tex = _tex()
    for command in (r"\includegraphics", r"\input{", r"\include{",
                    r"\pgfplotstableread", r"\lstinputlisting", r"\subfile"):
        assert command not in tex, (
            f"{command} makes the standalone .tex depend on a file the Export "
            f"page's '.tex' download does not carry (SUMMARY_REPORT.md §2)")
    # ``addplot table {file}`` is the pgfplots form of the same dependency;
    # ``addplot table[...] {x y ...}`` with inline rows is the permitted one.
    for match in re.finditer(r"\\addplot[^;]*?table[^;{]*\{([^{}]*)\}", tex):
        assert "\n" in match.group(1) or match.group(1).strip() == "", (
            "an addplot table reads an external data file: " + match.group(1)[:60])


def test_render_document_and_render_report_agree():
    project = io.load_project(_GA)
    doc = build_report(project, tool_version="test")
    assert render_document(doc) == render_report(project, tool_version="test")


if __name__ == "__main__":  # zero-dependency self-runner (see PROGRAM_SPEC)
    import traceback

    failures = 0
    for name, fn in sorted(list(globals().items())):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"ok   {name}")
        except Exception:
            failures += 1
            print(f"FAIL {name}")
            traceback.print_exc()
    raise SystemExit(1 if failures else 0)


def test_a_short_table_is_one_unbreakable_float_and_a_long_one_is_not():
    r"""A table that fits a page must move whole, never split.

    ``longtable`` split the Baron's five-row Mach table between its last row and
    ``\endlastfoot``, printing the repeated header and the bottom rule alone at
    the top of the next page with no data under them (GUI review, 2026-08-30).
    No inter-row penalty prevents that break, because the foot is not a row.

    Both halves are asserted. A table too long for any page still has to break,
    and turning *every* table into a float would put an unsplittable
    hundred-row case index somewhere no page can hold it.
    """
    from sloads.report.content import Table
    from sloads.report.latex import UNBREAKABLE_ROWS, table_tex

    def _table(n):
        return Table(title="T", columns=["a", "b"],
                     rows=[[str(i), "x"] for i in range(n)])

    short = table_tex(_table(UNBREAKABLE_ROWS))
    assert r"\begin{table}[H]" in short and r"\begin{tabular}" in short
    assert "longtable" not in short, "a page-sized table was left splittable"

    long = table_tex(_table(UNBREAKABLE_ROWS + 1))
    assert r"\begin{longtable}" in long
    assert r"\begin{table}[H]" not in long, (
        "a table too long for a page cannot be an unbreakable float")


def test_a_figure_caption_carries_a_short_form_for_the_list_of_figures():
    r"""``\caption[short]{long}``: the list gets the title, the page gets the
    explanation.

    Without it the front matter repeated every word of every caption -- and a
    caption in a report a reviewer signs has to explain the figure, so the
    captions are long by design.
    """
    from sloads.report.content import Figure, PlotData, Series
    from sloads.report.latex import figure_tex

    figure = Figure(key="vn", title="A title",
                    data=PlotData("x", "y", [Series("s", [0.0, 1.0], [0.0, 1.0])]),
                    caption="A long explanatory sentence.")
    tex = figure_tex(figure)
    assert r"\caption[A title]{A title: A long explanatory sentence.}" in tex


def test_the_marker_legend_is_named_by_the_figure_not_by_the_emitter():
    """``PlotData.points_label`` owns it.

    Hard-coded in the emitter, the oracle report's gust design points were
    labelled "Design CG cases" -- a legend naming a different figure entirely.
    """
    from sloads.report.content import PlotData
    from sloads.report.plots_tex import plot_tex

    data = PlotData("x", "y", points=[("p", 1.0, 2.0)],
                    points_label="Gust design points")
    assert r"\addlegendentry{Gust design points}" in plot_tex(data)
    # The default is preserved, so the summary report's figure is unchanged.
    assert PlotData("x", "y").points_label == "Design CG cases"


# --------------------------------------------------------------------------- #
# Column widths: the floor, and the page that is turned to honour it
# --------------------------------------------------------------------------- #
def _every_oracle_table():
    """Every table both shipped reports print, with its section's orientation."""
    from sloads.models.report import ReportSpec
    from sloads.report.oracle_content import build_oracle_document

    def walk(section, turned=False):
        # ``landscape`` is a property of the appendix while its tables live in
        # its subsections, so the flag is inherited here exactly as
        # ``section_tex`` inherits it.
        turned = turned or section.landscape
        out = [(turned, t) for t in section.tables]
        for sub in section.subsections:
            out += walk(sub, turned)
        return out

    for name in ("ga6_normal", "baron_58"):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "examples", f"{name}.project.json")
        doc = build_oracle_document(io.load_project(path), ReportSpec())
        for section in doc.sections:
            for turned, table in walk(section):
                if table.rows:
                    yield name, turned, table


def test_no_column_is_narrower_than_its_longest_unbreakable_token():
    """A ``p`` column wraps between words and never inside one, so a column
    below this floor does not wrap -- it prints on top of its neighbour.

    This is the gate for a defect that shipped: the width solver used to scale
    every column proportionally when the slack ran out, floor included. On
    ``ga6_normal`` the ``14 CFR`` column of the pull-up manoeuvre table needed
    63pt for ``23.423(a)(1)`` and was given 26, so the regulation printed over
    the CG case as ``23.423(a)(1)G4`` and a reader could not tell which CG case
    the condition was run at. Asserted over every table of both shipped
    reports, at the size and on the page each is actually set on.
    """
    import math

    from sloads.report import latex as L

    for name, in_landscape, table in _every_oracle_table():
        turned = in_landscape or L.table_orientation(table)
        size, _spec = L._table_size_and_spec(table, in_landscape=turned)
        page = L.LANDSCAPE_WIDTH_PT if turned else L.TEXT_WIDTH_PT
        available = page - 2 * L.TABCOLSEP_PT * len(table.columns)
        required, _d, _n = L._column_asks_pt(table, size)
        widths = L._column_widths_pt(table, size, available)
        for column, floor, width in zip(table.columns, required, widths):
            assert width >= floor - 0.01, (
                f"{name}: {table.title!r} column {column!r} is {width:.1f}pt "
                f"against a floor of {floor:.1f}pt -- its longest token will "
                f"print on top of the next column")
        # ...and the sum still fits the page it is set on, so honouring the
        # floor has not simply moved the overflow to the right-hand margin.
        assert math.fsum(widths) <= available + 0.01, (name, table.title)


def test_the_glyph_widths_are_the_widths_tex_actually_sets():
    """The width tables are measurements, and this is the measurement.

    Every column width in this report is a sum of :data:`~sloads.report.latex._GLYPH_PT`,
    and the floor that stops a token overprinting its neighbour is only as
    honest as those numbers. The words below were set by ``tectonic`` on this
    module's own preamble and their ``\\wd`` read back; the widths on the right
    are what TeX measured, in points.

    This is the gate for a defect that shipped. The widths used to be a
    four-class model scaled off a 0.5 em average, and it put ``assumed`` at
    30.24pt against the 34.02 below -- so the Spars column of the wing-attach
    fitting table was floored 3.8pt under the one token it had to hold, and
    every row of it ran over. The floor test passed throughout: it checked the
    solver against the same wrong ruler the solver used.

    Kerning is not modelled, so the sum may run a fraction **over** a real
    word (``entered`` by 0.26pt) -- the safe direction for a floor. It may not
    run under.
    """
    from sloads.report import latex as L

    measured = [
        # word, tectonic's \wd at \footnotesize, set bold
        ("assumed", 34.02278, False),
        ("entered", 29.57951, False),
        ("UNSYMMETRICAL", 85.42184, False),
        ("23.423(a)(1)", 49.33250, False),
        ("-2.356e+06", 44.71180, False),
        ("Condition", 46.15263, True),
        ("Case", 21.95612, True),
        ("(KEAS)", 37.55678, True),
    ]
    for word, width_pt, bold in measured:
        got = L._token_width(word, bold=bold)
        assert got >= width_pt - 0.02, (
            f"{word!r} is measured at {got:.2f}pt against TeX's {width_pt:.2f}pt "
            f"-- a column floored on it will let it overprint the next column")
        assert got <= width_pt + 0.40, (
            f"{word!r} is measured at {got:.2f}pt against TeX's {width_pt:.2f}pt "
            f"-- columns will be wider than their contents need")

    # ...and the two table sizes are one font, so their ratio is exact: the
    # alphabet measures 118.01314pt at \footnotesize and 127.58365pt at \small.
    assert L._SIZE_SCALE[r"\footnotesize"] == 1.0
    assert abs(L._SIZE_SCALE[r"\small"] - 127.58365 / 118.01314) < 0.001


def test_a_table_is_turned_only_when_it_cannot_be_set_upright():
    """The remedy of last resort, and never before the last resort.

    Turning a table costs the reader a rotated page away from the prose that
    introduces it, so it happens only when no upright size holds every token.
    Both directions: a table that fits is never turned, and one that does not
    always is.
    """
    from sloads.report import latex as L

    turned = set()
    for name, in_landscape, table in _every_oracle_table():
        if in_landscape:
            # Already on a turned page: it must not open a second one.
            assert not L.table_orientation(table, in_landscape=True), table.title
            continue
        fits = any(L._fits(table, size,
                           L.TEXT_WIDTH_PT - 2 * L.TABCOLSEP_PT * len(table.columns))
                   for size in ((r"\footnotesize",) if table.small
                                else (r"\small", r"\footnotesize")))
        assert L.table_orientation(table) is not fits, table.title
        if not fits:
            turned.add((name, table.title))
    # The one table on either airplane that genuinely cannot be set upright:
    # eleven columns of case identity, weight, CG, two stations, three loads, a
    # moment and the factor. Pinned so that a table quietly becoming unfittable
    # is a visible change rather than a silent rotation.
    assert {t for _n, t in turned} == {"Pull-up maneuver fuselage loads (LIMIT)"}


def test_a_turned_table_opens_exactly_one_landscape_environment():
    """Nesting landscape environments turns the page back to portrait."""
    from sloads.report import latex as L

    for _name, in_landscape, table in _every_oracle_table():
        tex = L.table_tex(table, in_landscape=in_landscape)
        opens = tex.count(r"\begin{landscape}")
        assert opens == tex.count(r"\end{landscape}")
        assert opens <= 1, table.title
        if in_landscape:
            assert opens == 0, table.title


def test_the_running_head_declares_the_height_it_needs():
    """``fancyhdr`` warned once per page -- 77 times on the report's own example
    -- that a ``\\small`` head does not fit the 12pt default. Both reports set
    their own head, so both are asserted; the warning is noise a real one hides
    in."""
    from sloads.models.report import ReportSpec
    from sloads.report.oracle_content import build_oracle_document
    from sloads.report.oracle_latex import render_oracle_document

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "examples", "ga6_normal.project.json")
    oracle = render_oracle_document(build_oracle_document(io.load_project(path),
                                                          ReportSpec()))
    assert r"\setlength{\headheight}{14pt}" in oracle
    summary = render_report(io.load_project(path))
    assert r"\setlength{\headheight}{14pt}" in summary


def test_an_unnamed_series_takes_no_legend_entry():
    """A series with no name is the same thing as the one beside it -- a
    planform's mirrored half, the second arrow of an axis key -- so it is drawn
    ``forget plot`` and claims no legend row. A blank row reads as a series whose
    label went missing, which is what every planform figure printed until
    2026-09-07: ``_region_series`` documented this behaviour and the emitter did
    not have it.
    """
    from sloads.report.content import PlotData, Series
    from sloads.report.plots_tex import plot_tex

    tex = plot_tex(PlotData("x", "y", [Series("Named", [0.0, 1.0], [0.0, 1.0]),
                                       Series("", [0.0, 1.0], [1.0, 0.0])]))
    assert tex.count(r"\addlegendentry") == 1
    assert tex.count("forget plot") == 1
    assert r"\addlegendentry{}" not in tex
