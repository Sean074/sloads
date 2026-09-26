"""What an applied-load row says about *which* case it belongs to (#241).

The applied CSVs carried a ``Case`` column holding the case's **description**,
which is prose and is not an identity: LANDLOAD's 33 ground conditions share
eight of them, and a twin's two mounts shared all three of theirs. The minted
``case_id`` -- the key the load-case index is built on -- was populated on every
row and emitted on none, so the delivered file could not be joined to the index
that states each case's condition, CG, speed and FAR paragraph.

These guards hold the three halves of the fix:

* every row states its ``Case ID``, and that id is one the case index names --
  the round trip, run over every bundled example and every component;
* the id tells apart what the description cannot -- all 33 gear cases, and a
  twin's two engine mounts;
* the identity has **one owner** (``applied.case_identity``), so a producer
  added later cannot go on reading the ``CaseRef`` its own way.

Reference: 2026-09-08 oracle report/GUI/CSV review §4; note 44 OR-141.
"""

import ast
import csv
import io as _io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from imperial_baseline import EXAMPLES, artifacts  # noqa: E402

from sloads.case_ids import index_case_id  # noqa: E402
from sloads.modules.engine import engine_tags  # noqa: E402
from sloads.report import applied as ap  # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: The applied channels the baseline renders, keyed the way it keys them.
_APPLIED = tuple(f"sbeam/{c}_applied" for c in
                 ("wing", "body", "htail", "vtail", "landing_gear", "engine"))


def _rows(text):
    """The data rows of one delivered CSV, its ``#`` header block dropped."""
    body = "\n".join(ln for ln in text.splitlines() if not ln.startswith("#"))
    return list(csv.DictReader(_io.StringIO(body)))


def _bundle(example):
    """``(applied rows by channel, index rows by id)`` for one example."""
    art = artifacts(example)
    applied = {k: _rows(art[k]) for k in _APPLIED if art.get(k)}
    index = {r["ID"]: r for r in _rows(art.get("case_index", ""))}
    return applied, index


@pytest.mark.parametrize("example", EXAMPLES)
def test_every_applied_row_joins_to_the_case_index(example):
    """The round trip: every ``Case ID`` delivered is an id the index states.

    The join is the whole point of the column -- a row that names an id no index
    row carries is worse than the blank it replaced, because it reads as a
    reference and is not one.
    """
    applied, index = _bundle(example)
    assert applied, example
    assert index, example
    for channel, rows in applied.items():
        assert rows, (example, channel)
        for row in rows:
            assert row["Case ID"], (example, channel, row["Case"])
            # Through the vocabulary's own strip: one index row stands for the
            # gyro condition's four sign combinations, which the file delivers
            # as four rows under four ids (Step D1).
            assert index_case_id(row["Case ID"]) in index, (
                example, channel, row["Case ID"])


@pytest.mark.parametrize("example", EXAMPLES)
def test_the_loading_column_is_the_index_s_cg_and_is_never_invented(example):
    """``Loading`` is copied from the case's own ``CaseRef``, not re-derived.

    Which makes the file and the index the same statement about the same case:
    the column is the index's ``CG`` cell for that id, blank included.
    """
    applied, index = _bundle(example)
    for channel, rows in applied.items():
        for row in rows:
            assert row["Loading"] == index[index_case_id(row["Case ID"])]["CG"], (
                example, channel, row["Case ID"])


def test_the_gear_file_tells_its_thirty_three_cases_apart():
    """Eight descriptions, 33 cases -- and now 33 rows a reader can separate.

    The defect in one assertion: ``Case`` collapses the set by a factor of four,
    and the three loadings a description is flown at are what it collapses.
    """
    applied, _index = _bundle("baron_58.project.json")
    rows = applied["sbeam/landing_gear_applied"]
    assert len({r["Case"] for r in rows}) == 8
    assert len({r["Case ID"] for r in rows}) == 33
    # Every case names its loading, and the three of case 1-3 are distinct.
    assert all(r["Loading"] for r in rows)
    assert len({r["Loading"] for r in rows
                if r["Case ID"] in ("LG-01", "LG-02", "LG-03")}) == 3


def test_a_twins_two_mounts_no_longer_share_one_case_string():
    """Six engine cases, six descriptions, six ids -- three per engine.

    The Baron fits two ``CONTINENTAL IO-550-C``, so the designation alone named
    both and the index described ``EM-01`` and ``EM-04`` identically.
    """
    applied, index = _bundle("baron_58.project.json")
    rows = applied["sbeam/engine_applied"]
    assert len(rows) == 6
    assert len({r["Case ID"] for r in rows}) == 6
    assert len({r["Case"] for r in rows}) == 6
    assert "left" in index["EM-01"]["Condition"]
    assert "right" in index["EM-04"]["Condition"]


def test_a_gyro_sub_case_is_a_case_the_index_lists():
    """The four sign combinations are four rows **and four indexed cases**
    (design note 66 Q7, #286): each is its own condition with its own ``EM``
    id, so the applied file and the index join on the id itself -- there is no
    suffix to strip any more, and no id the index does not list."""
    applied, index = _bundle("atr42_100.project.json")
    rows = applied["sbeam/engine_applied"]
    gyro = [r["Case ID"] for r in rows if "Gyroscopic" in r["Case"]]
    assert gyro, "no gyro rows -- has the 23.371(b) condition moved?"
    assert len(gyro) == len(set(gyro)) == 8, gyro      # 4 per engine, distinct
    for case_id in gyro:
        assert case_id in index
    assert index_case_id("W-05R") == "W-05"
    assert index_case_id("EM-06") == "EM-06"


def test_engine_tags_separate_engines_only_when_the_designation_cannot():
    """Distinct designations are left alone; equal ones take their side.

    Nothing renames on an installation whose engines already differ, which is
    why no single-engine or mixed-designation title in any shipped example moves.
    """
    from dataclasses import replace

    from sloads.models import EngineInput

    def eng(name, y):
        return replace(EngineInput(), engine_designation=name,
                       engine_cg=(0.0, y, 0.0))

    assert engine_tags([eng("LEFT", -60.0), eng("RIGHT", 60.0)]) == ["LEFT", "RIGHT"]
    assert engine_tags([eng("IO-550", -60.0), eng("IO-550", 60.0)]) == [
        "IO-550, left", "IO-550, right"]
    # Four of one model, two a side: the side is no longer enough and the
    # engine's place in the installation settles the rest.
    four = engine_tags([eng("T56", -120.0), eng("T56", -60.0),
                        eng("T56", 60.0), eng("T56", 120.0)])
    assert len(set(four)) == 4
    assert four[0].startswith("T56, left")
    # An engine with no designation at all still ends up named and distinct.
    assert len(set(engine_tags([eng("", -60.0), eng("", 60.0)]))) == 2


def test_every_applied_row_takes_its_identity_from_the_one_owner():
    """No producer may spell the ``CaseRef`` read for itself (rule 3).

    Each ``AppliedLoad(...)`` in the module either states ``loading=`` beside
    its ``case_id=``, or is the engine set, whose cases name no CG and whose row
    says so in a comment. A producer added later that reaches into ``case_ref``
    on its own fails here rather than shipping a file whose identity columns are
    half filled.
    """
    path = os.path.join(_ROOT, "sloads", "report", "applied.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    owners = {}
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef):
            continue
        for node in ast.walk(func):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "AppliedLoad"):
                names = {kw.arg for kw in node.keywords}
                owners.setdefault(func.name, []).append(names)
    assert owners, "no AppliedLoad construction found -- has the module moved?"
    for name, calls in owners.items():
        for names in calls:
            assert "case_id" in names, name
            if name != "engine_applied_load_rows":
                assert "loading" in names, name


def test_the_identity_columns_lead_the_delivered_row():
    """Header order is part of the contract the appendices state (D-21).

    The identity comes first and the units band stays where it was: a consumer
    reading by position finds the load vector at the offset the file's own
    header row names, and the writer reads its unit-bearing headings out of the
    same list, so the two cannot disagree.
    """
    from sloads.export.deck_format import solver_units
    from sloads.units import UnitSystem

    fields = ap._applied_csv_fields(solver_units(UnitSystem.IMPERIAL))
    assert fields[:5] == ["Case ID", "Case", "Loading", "Station", "GID"]
    assert fields[-2:] == ["TorsionAxis", "SF"]
    assert [f.split(" ")[0] for f in fields[5:14]] == [
        "X", "Y", "Z", "Fx", "Fy", "Fz", "Mx", "My", "Mz"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
