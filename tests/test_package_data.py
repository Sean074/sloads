"""The issue package's ``data/`` is the oracle GUI's only tabular channel (#245).

Design note 44 OR-22/OR-23, deferred by OR-42 and delivered here; design note 57
§1.3 and note 60 D-60.12 for why it is the *only* one. Three channels carried the
same numbers before this change -- a CSV and a McMaster-format text twin on every
results block, a whole-project zip in the sidebar, and the applied sets, which
shipped from ``app/``'s export page alone and therefore not from the surviving
front end at all. Appendix F named ``landing_gear_applied_loads.csv`` in printed
prose and nothing wrote it.

What this file guards is the consolidation, in both directions:

* nothing was **lost** -- every column of every retiring per-module CSV is in
  ``data/``, through the identical owner, which is the column inventory #245
  made a precondition, made structural instead of remembered;
* nothing is **duplicated** -- a table a named file carries is not written a
  second time under a generated name;
* the two things the inventory found that no channel carried -- the yaw
  transient march, and the applied sets of the gear and the engine -- are in it.

``tests/test_oracle_report_package.py`` holds G-OR-15 and G-OR-17 on the written
package; ``tests/test_deck_basis.py`` holds G-OR-73 over the same set; this file
holds the owner.
"""

import csv
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sloads.modules  # noqa: E402, F401
from sloads import io as sloads_io  # noqa: E402
from sloads.models.report import default_spec  # noqa: E402
from sloads.report import package_data as pd  # noqa: E402
from sloads.report.oracle_content import build_oracle_document  # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = [
    "ga6_normal", "baron_58", "atr42_100", "concept_regional_jet",
    "concept_heavy",
]


def _doc(example):
    project = sloads_io.load_project(
        os.path.join(_ROOT, "examples", f"{example}.project.json"))
    return build_oracle_document(project, default_spec())


def _files(example):
    return pd.data_files(_doc(example))


def _body(text):
    return [ln for ln in text.splitlines() if ln and not ln.startswith("#")]


# --------------------------------------------------------------------------- #
# Nothing was lost: the column inventory, made structural
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", _EXAMPLES)
def test_every_retired_per_module_csv_is_in_the_package_byte_for_byte(example):
    """#245's precondition: no column of the retiring buttons goes with them.

    The per-module CSV button called ``io.load_cases_csv(result)`` with the
    methods stamp, and so does the package's ``load_cases/<module>.csv``. The
    assertion is byte equality of the rows, not a column-set comparison, because
    "the same owner" is a claim that can be made true by construction and a
    column list is a claim that has to be maintained.

    Written as a test rather than recorded as a one-pass inventory on purpose:
    the inventory the issue asked for answers the question once, and the buttons
    can only be retired once. This answers it on every build.
    """
    doc = _doc(example)
    files = {f.name: f.content for f in pd.data_files(doc)}
    checked = 0
    for module, result in doc.results.items():
        if result is None:
            continue
        name = f"{pd.DATA_DIR}/{pd.LOAD_CASES_DIR}/{module}.csv"
        expected = _body(sloads_io.load_cases_csv(result, system=doc.system))
        if len(expected) <= 1:
            assert name not in files, (
                f"{name} ships rows the module does not produce")
            continue
        assert name in files, (
            f"{module} produced load cases and the package carries no file of "
            "them -- a column of the retired download button went with it")
        assert _body(files[name]) == expected, (
            f"{name} is not what the retired {module} CSV button served")
        checked += 1
    assert checked, f"{example}: no module file checked -- the gate is vacuous"


@pytest.mark.parametrize("example", ["baron_58", "atr42_100"])
def test_the_yaw_transient_march_reaches_a_file(example):
    """The one thing the #245 inventory found that no channel carried.

    Section 11 draws the one-engine-inoperative march as a pair of figures per
    case, and a figure has no printed table: the module's own CSV carries six
    summary rows, and the finer time history existed only behind a button on
    ``app/views/one_engine_out.py``, which #270 deletes. So the march would have
    been lost between two changes that each looked complete.

    The emitter is generic -- every figure's data is written, not this one's --
    which is rule 4's half of the same finding: the next curve whose numbers a
    reader wants should not need its own discovery.
    """
    names = {f.name for f in _files(example)}
    marches = [n for n in names if "/oei-" in n and n.endswith("-load.csv")]
    assert marches, (
        "the yaw transient is drawn and its numbers ship nowhere: "
        + str(sorted(n for n in names if pd.FIGURES_DIR in n))[:300])
    content = next(f.content for f in _files(example) if f.name == marches[0])
    rows = list(csv.reader(_body(content)))
    assert rows[0][:2] == list(pd.FIGURE_COLUMNS)
    assert rows[0][2].startswith("Time"), rows[0]
    assert len({r[1] for r in rows[1:] if r[0] == "line"}) >= 3, (
        "the march ships fewer curves than the figure draws")
    assert len(rows) > 50, "the march ships fewer points than it was computed at"


@pytest.mark.parametrize("example", _EXAMPLES)
def test_every_figure_the_document_draws_ships_its_numbers(example):
    """A curve with no file is a picture a reader cannot check.

    The other direction of the same rule G-OR-17 states for the ``.tex``: what
    the document draws, the package carries. A figure that could not be built
    states an ``absent_reason`` instead and has no numbers to ship, which is
    the one exemption and is the producer's own statement.
    """
    doc = _doc(example)
    drawn = set()

    def walk(section):
        for figure in section.figures:
            if figure.data is not None:
                drawn.add(figure.key)
        for child in section.subsections:
            walk(child)

    for section in doc.sections:
        walk(section)
    shipped = {os.path.basename(f.name)[: -len(".csv")]
               for f in pd.data_files(doc)
               if f"/{pd.FIGURES_DIR}/" in f.name}
    assert not drawn - shipped, sorted(drawn - shipped)


# --------------------------------------------------------------------------- #
# Nothing is duplicated
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", _EXAMPLES)
def test_a_table_a_named_file_carries_is_not_written_twice(example):
    """``Table.data_file`` is the producer saying "mine is already shipped".

    Appendix B.1 *is* ``wing_applied_loads.csv``; emitting it again under a
    generated name would put one set of numbers in the package twice, under one
    name the report's prose cites and another nothing does. The reader then has
    two files and no way to know they are the same -- which is the duplication
    ``data/`` was consolidated to end, reappearing inside it.
    """
    doc = _doc(example)
    declared = set()

    def walk(section):
        for table in section.tables:
            if table.data_file:
                declared.add(table.data_file)
        for child in section.subsections:
            walk(child)

    for section in doc.sections:
        walk(section)
    names = [f.name for f in pd.data_files(doc)]
    for name in declared:
        assert f"{pd.DATA_DIR}/{name}" in names, (
            f"a table names {name} as its data file and the package has none")
    # No generated appendix file whose slug names a declared file's own table.
    generated = [n for n in names
                 if os.path.basename(n).startswith("appendix_")]
    for name in generated:
        assert "applied" not in name and "balanced_flight" not in name, (
            f"{name} looks like a second copy of a named applied or V-n file")


@pytest.mark.parametrize("example", _EXAMPLES)
def test_no_data_file_is_written_twice_or_escapes_its_directory(example):
    """Names are unique and stay inside ``data/``.

    ``export.report_package.write_members`` refuses a member that resolves
    outside the package root; this is the same rule one step earlier, where a
    name is decided rather than written, so a bad name fails in the pure layer
    a test can see it in.
    """
    names = [f.name for f in _files(example)]
    assert len(names) == len(set(names)), sorted(
        n for n in names if names.count(n) > 1)
    for name in names:
        assert name.startswith(pd.DATA_DIR + "/"), name
        assert ".." not in name.split("/"), name


# --------------------------------------------------------------------------- #
# The channel's own hygiene
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", _EXAMPLES)
def test_no_data_file_mixes_its_line_endings(example):
    """#242's rule, on the channel #245 created.

    Every writer here goes through ``sloads.csv_text``, so this cannot drift
    quietly -- but ``data/`` is where a new emitter would be added, and a
    generic one that reached for ``csv.writer`` would put CRLF rows under LF
    prose in eighty files at once instead of one.
    """
    for f in _files(example):
        assert "\r" not in f.content, f"{f.name} mixes CRLF and LF"


@pytest.mark.parametrize("example", _EXAMPLES)
def test_every_file_states_what_it_is_for_in_the_manifest(example):
    """``SUMMARY_REPORT.md`` §4.7: a manifest row is not a file name.

    The rule is structural in :class:`PackageMember` -- units and conventions
    are fields, so a member cannot be built without them -- and this is the half
    that field cannot enforce: that the prose says something. A row reading
    "--" for every column is a listed file, not a described one.
    """
    for f in _files(example):
        assert len(f.contents) > 40, (f.name, f.contents)
        assert f.summarised_in and f.summarised_in != "--", f.name
        assert f.units and f.units != "--", f.name


def test_the_data_directory_has_one_owner():
    """``oracle_package`` places the files; ``package_data`` decides them.

    Two modules spelling ``"data"`` would be two answers to where the directory
    is, which is the class practice 3 exists to prevent -- and the one the
    backlog already has an open row for elsewhere in this package (#273, two
    owners for ``report.json``).
    """
    from sloads.report import oracle_package as op

    assert op.DATA_DIR is pd.DATA_DIR
    source = os.path.join(_ROOT, "sloads", "report", "oracle_package.py")
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    assert 'DATA_DIR = "data"' not in text, (
        "oracle_package spells the directory name again instead of citing "
        "package_data, which owns it")


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
