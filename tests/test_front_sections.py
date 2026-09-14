"""The summary report's cross-cutting sections, in the document that survives.

Design note 60 D-60.7 … D-60.11, gates 11 and 12. ``app/views/export_report.py``
was the front-end consumer of ``content.build_report``, so note 57 D-57.1
retired the summary report by deleting a page -- and would have taken with it
the only statement of the axis system and sign conventions either front end
made, and the only FAR 23 Subpart C coverage matrix. Four assets merged into the
oracle report as front matter at **#278**; everything else was declared
superseded in writing, and **#270** then deleted the document.

Two gates live here:

* **11** -- the merged sections render, for every bundled example, and
  ``conventions_tex.py`` and ``coverage.py`` have a production consumer that is
  not the retired document, so the merge cannot quietly become dead code.
* **12** -- no section of the retired document left unaccounted: the audit table
  is read against :data:`front_sections.RETIRED_SUMMARY_SECTIONS` -- the section
  list, kept beside the audit when ``content.py`` lost it, because an accounting
  whose subject has been deleted accounts for nothing -- and a key that is
  neither merged nor superseded-with-a-reason fails the suite. A design note
  cannot fail a build; this can.
"""

import ast
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sloads.modules  # noqa: F401
from sloads import io as sloads_io
from sloads.models.report import default_spec
from sloads.report import front_sections as fs
from sloads.report import oracle_content as oc
from sloads.report.oracle_latex import render_oracle_document

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = [
    "ga6_normal", "baron_58", "atr42_100", "concept_regional_jet",
    "concept_heavy",
]

#: The front-matter keys the merge added, and what each must not be empty of.
_MERGED = ("conventions", "factors", "coverage", "package_files")


def _doc(example):
    project = sloads_io.load_project(
        os.path.join(_ROOT, "examples", f"{example}.project.json"))
    return build(project)


def build(project):
    return oc.build_oracle_document(project, default_spec())


def _section(doc, key):
    return doc.sections[oc.front_index(key)]


# --------------------------------------------------------------------------- #
# Gate 11: the merged sections render, on every example
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", _EXAMPLES)
def test_every_merged_section_is_built_and_carries_content(example):
    """A merged section that renders empty is a deletion with a heading on it.

    Each of the four is asserted against what it exists to say: the frame (a
    table of senses and the three diagrams), the factor that is not applied (a
    row per condition family), what the run did and did not cover (a row per
    regulation), and what travels with the document (a row per file).
    """
    doc = _doc(example)
    for key in _MERGED:
        section = _section(doc, key)
        titles = {f.key: f.title for f in oc.FRONT_SECTIONS}
        assert section.title.endswith(titles[key])
        assert not section.absent_reason, (
            f"{key} states a reason instead of content: {section.absent_reason}")
        assert section.body, f"{key} prints no prose"
        assert section.tables and section.tables[0].rows, (
            f"{key} prints an empty table")
    assert len(_section(doc, "conventions").figures) == 3, (
        "the three sign-convention diagrams are the statement's other half")


@pytest.mark.parametrize("example", _EXAMPLES)
def test_the_merged_sections_reach_the_rendered_document(example):
    """Built is not rendered: the assertion is on the ``.tex`` the package ships."""
    doc = _doc(example)
    tex = render_oracle_document(doc)
    for key in _MERGED:
        assert _section(doc, key).title in tex
    # The frame statement itself, not just its heading -- the one sentence a
    # structures analyst cannot read the rest of the document without.
    from sloads.report.conventions_tex import FRAME_FRAGMENTS
    for fragment in FRAME_FRAGMENTS:
        assert fragment in tex


def test_the_front_matter_comes_before_the_analysis_body():
    """D-60.9: an axes section belongs *before* what it governs.

    Appendices were the rejected alternative -- an appendix is appended, never
    inserted (OR-50) -- so the ordering is the decision and is asserted.
    """
    doc = _doc("ga6_normal")
    titles = [s.title for s in doc.sections]
    last_front = max(titles.index(_section(doc, key).title) for key in _MERGED)
    first_body = min(i for i, t in enumerate(titles)
                     if t.endswith("Loads Configuration"))
    assert last_front < first_body


def test_the_front_matter_is_the_front_section_builders_output():
    """One builder, and now one document (practice 3).

    It asserted the two documents printed the *same objects'* content -- same
    table title, same rows -- because a merge implemented as a copy is the
    duplication the convergence exists to end. #270 deleted the second document,
    so the copy it guarded against cannot exist; what is still worth pinning is
    that the document's front matter is these builders' output and not a second
    rendering grown inside ``oracle_content``.
    """
    project = sloads_io.load_project(
        os.path.join(_ROOT, "examples", "ga6_normal.project.json"))
    oracle = build(project)
    for key, builder in (("conventions", fs.conventions_section),
                         ("factors", None)):
        section = _section(oracle, key)
        assert section.tables, key
        if builder is not None:
            mine = builder(section.title)
            assert [t.title for t in mine.tables] == [t.title for t in section.tables]
            assert mine.tables[0].rows == section.tables[0].rows
            assert [f.key for f in mine.figures] == [f.key for f in section.figures]
    # ...and nothing rebuilt them: ``oracle_content`` calls the owner.
    with open(os.path.join(_ROOT, "sloads", "report", "oracle_content.py"),
              encoding="utf-8") as fh:
        source = fh.read()
    for name in ("conventions_section", "governing_factors_section",
                 "coverage_section", "package_files_section"):
        assert name in source, (
            f"the document's front matter no longer calls {name} -- a second "
            "builder is a second owner")


def test_the_merged_owners_keep_a_consumer_that_outlives_the_summary_report():
    """Gate 11's other half: not dead code after #270.

    ``conventions_tex`` and ``coverage`` had one consumer each, and #270 deletes
    it. The merge is only real if something that survives imports them -- this
    reads the imports rather than trusting that it does, because a merge whose
    consumer is the module being deleted is the failure mode.
    """
    doomed = {os.path.join(_ROOT, "sloads", "report", "content.py")}
    found = {"conventions_tex": [], "coverage": []}
    for folder in ("sloads",):
        for base, _, names in os.walk(os.path.join(_ROOT, folder)):
            for name in names:
                path = os.path.join(base, name)
                if not name.endswith(".py") or path in doomed:
                    continue
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                for module in found:
                    if f"from .{module} import" in text or f".{module} " in text:
                        found[module].append(os.path.relpath(path, _ROOT))
    for module, consumers in found.items():
        assert consumers, (
            f"{module}.py has no consumer outside the retiring summary report")


# --------------------------------------------------------------------------- #
# Gate 12: no section of the retiring document leaves unaccounted
# --------------------------------------------------------------------------- #
def test_every_retiring_section_is_declared_merged_or_superseded():
    """D-60.10, made enforceable.

    The asset most at risk in a merge is the one nobody thought to look for, so
    the audit is a table a test reads rather than prose in a note.
    """
    keys = [key for key, _ in fs.RETIRED_SUMMARY_SECTIONS]
    assert not fs.undeclared_sections(keys), (
        "sections of the retiring summary report with no stated successor and "
        f"no stated reason: {fs.undeclared_sections(keys)}")


def test_the_audit_names_no_section_the_document_does_not_have():
    """The other direction: a row for a key that no longer exists is a stale
    audit, and a stale audit is worse than none -- it reads as coverage."""
    keys = {key for key, _ in fs.RETIRED_SUMMARY_SECTIONS}
    strays = [d.key for d in fs.SUMMARY_DISPOSITION if d.key not in keys]
    assert not strays, strays


def test_every_merged_row_points_at_a_section_that_exists():
    """A row claiming a merge must name front matter the document carries."""
    front = {f.key for f in oc.FRONT_SECTIONS}
    for row in fs.SUMMARY_DISPOSITION:
        if not row.merged_into:
            continue
        assert row.merged_into in front, (
            f"{row.key} is declared merged into {row.merged_into}, which is no "
            "front-matter section")
    merged = {row.merged_into for row in fs.SUMMARY_DISPOSITION if row.merged_into}
    assert merged == set(_MERGED) - {"package_files"}, (
        "a front-matter section the merge added that no retiring section "
        f"accounts for, or the other way round: {merged}")


def test_the_audit_is_one_row_per_key():
    """A second row for one key is two decisions about the same section."""
    keys = [d.key for d in fs.SUMMARY_DISPOSITION]
    assert len(keys) == len(set(keys)), keys


def test_the_front_matter_writes_no_section_number_of_its_own():
    """Numbering has one owner (F-R2), and the merge must not acquire a second.

    ``front_sections`` takes its heading as an argument for exactly this
    reason; a literal "2." in it would be a number that cannot renumber itself
    when a section is inserted above it.
    """
    source = os.path.join(_ROOT, "sloads", "report", "front_sections.py")
    with open(source, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert "§" not in node.value or "§CASEREF" in node.value, (
                f"a section reference written as a literal: {node.value!r}")


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
