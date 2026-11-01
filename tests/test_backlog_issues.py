"""The backlog ↔ issues bridge on the live backlog (design note 28 MD-5; slimmed #359).

`scripts/backlog_issues.py check` needs `gh` and is a close/release step, not a
test. What can be asserted offline: the parser sees every priority-table row with
a band, a tier and a tag; `render` is a pure function that drops exactly the rows
whose issues are closed; the band headers name distinct, un-cut releases; and
the file is mission + rules + table, with nothing below the table.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPT = os.path.join(_ROOT, "scripts", "backlog_issues.py")
_BACKLOG = os.path.join(_ROOT, "docs", "30_future", "00_backlog.md")


@pytest.fixture(scope="module")
def bi():
    spec = importlib.util.spec_from_file_location("backlog_issues", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["backlog_issues"] = mod  # dataclasses resolve the module through sys.modules
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def backlog_text():
    with open(_BACKLOG, encoding="utf-8") as fh:
        return fh.read()


def test_every_priority_table_row_is_parsed_with_band_tier_tag(bi, backlog_text):
    rows_in_file = [ln for ln in backlog_text.splitlines() if re.match(r"^\|\s*\d+\s*\|", ln)]
    rows = [it for it in bi.parse_backlog(backlog_text) if it.kind == "row"]
    assert len(rows) == len(rows_in_file) > 0
    for r in rows:
        kinds = {lb.split(":")[0] for lb in r.labels}
        assert {"band", "tier", "tag", "kind"} <= kinds, r.title
        assert r.title and len(r.title) <= 120
        assert r.existing is not None, f"row {r.pri} in band {r.band} carries no (#N)"


def test_render_is_the_identity_on_open_issues_and_drops_exactly_the_closed_row(bi, backlog_text):
    """A row is **owned by the ``(#N)`` in its Item cell**. A later ``(#N)`` in
    the same line is a cross-reference to another row's issue, and closing
    *that* issue must not delete this row."""
    refs = bi.table_refs(backlog_text)
    assert refs
    states = {n: "OPEN" for n in refs}
    assert bi.render_backlog(backlog_text, states) == backlog_text
    first = refs[0]
    states[first] = "CLOSED"
    rendered = bi.render_backlog(backlog_text, states)
    kept = [ln for ln in backlog_text.splitlines() if bi.row_ref(ln) != first]
    assert rendered == "\n".join(kept) + "\n"
    citing = [ln for ln in backlog_text.splitlines()
              if bi.ITEM_ROW.match(ln) and bi.row_ref(ln) != first and f"(#{first})" in ln]
    for ln in citing:
        assert ln in rendered.splitlines(), f"row owned by #{bi.row_ref(ln)} was dropped for citing #{first}"
    # An issue the states do not know leaves its row alone.
    assert bi.render_backlog(backlog_text, {}) == backlog_text


def test_render_dry_run_writes_nothing(bi, backlog_text, monkeypatch, capsys):
    refs = bi.table_refs(backlog_text)
    monkeypatch.setattr(bi, "fetch_states", lambda: {refs[0]: "CLOSED"})
    assert bi.main(["render", "--dry-run"]) == 0
    with open(_BACKLOG, encoding="utf-8") as fh:
        assert fh.read() == backlog_text
    out = capsys.readouterr().out
    assert "drop:" in out and "nothing written" in out


def test_render_closing_treats_the_named_issue_as_closed(bi, backlog_text, monkeypatch, capsys):
    refs = bi.table_refs(backlog_text)
    monkeypatch.setattr(bi, "fetch_states", lambda: {n: "OPEN" for n in refs})
    assert bi.main(["render", "--dry-run", "--closing", str(refs[-1])]) == 0
    assert f"(#{refs[-1]})" in capsys.readouterr().out


def test_the_backlog_carries_no_body_below_the_table(backlog_text):
    """The table is a generated view (#359): nothing a closure would have to
    hand-edit may live below it, and no narrative may hide behind it."""
    lines = backlog_text.splitlines()
    header = next(i for i, ln in enumerate(lines) if ln.startswith("| Pri |"))
    stray = [ln for ln in lines[header:] if ln.strip() and not ln.startswith("|")]
    assert stray == [], f"prose below the priority table: {stray[:3]}"


# --- band -> milestone (issue #46, 2026-08-25) -------------------------------

def test_every_band_header_is_parsed_including_the_multi_character_ones(bi, backlog_text):
    """`BAND_ROW` matched a single letter until 2026-08-25, so the **B2** header
    never matched and every row beneath it inherited band **B**; the same defect
    recurred one digit wider at **B10** (2026-10-03). Both regexes read `\\d{0,2}`."""
    headers = [ln for ln in backlog_text.splitlines() if re.match(r"^\|\s*\*\*[A-Z]\d{0,2}\s+[—-]", ln)]
    parsed = bi.band_milestones(backlog_text)
    assert len(parsed) == len(headers) > 0, (
        f"{len(headers)} band header row(s) in the file, {len(parsed)} parsed: {sorted(parsed)}"
    )
    assert any(len(b) > 1 for b in parsed), "no multi-character band in the table — the regression pin"


def test_a_band_names_the_release_it_ships_in_or_names_none(bi, backlog_text):
    """The map is read from the header text, never hardcoded: band letters move at
    every re-cut. Only a band that names no release — 'when the module is next
    touched' — may map to ``None``."""
    milestones = bi.band_milestones(backlog_text)
    named = {b: v for b, v in milestones.items() if v}
    assert named, "no band header names a release"
    assert len(set(named.values())) == len(named), f"two bands name the same release: {named}"
    for band, ship in milestones.items():
        if ship is None:
            header = next(ln for ln in backlog_text.splitlines()
                          if re.match(rf"^\|\s*\*\*{band}\s+[—-]", ln))
            assert "when the module is next touched" in header, (
                f"band {band} names no release and is not the maintenance band: {header[:120]}"
            )


def test_a_rows_issue_is_its_item_cell_not_a_cross_reference(bi):
    """A row is identified by the ``(#N)`` in its **Item** cell. Other cells cite
    other rows' issues in prose, and reading the whole line put #29 under band D,
    where the milestone check would have demanded it carry no milestone."""
    line = "| 13 | Calc-side function size (#17) | the view functions wait for the review (#29) | V | S / S | — |"
    assert bi.row_ref(line) == 17
    assert bi.row_bands("| **D — maintenance, when the module is next touched** ||||||\n" + line) == {17: "D"}


def test_no_open_row_sits_in_a_band_whose_release_is_already_cut(bi, backlog_text):
    """The offline half of the #71 case: that issue sat open on the already-cut
    0.7.1 while its row was in the 0.8.0 band. A band still in the table may not
    name a release ``CHANGELOG.md`` shows as shipped."""
    cut = bi.cut_milestones()
    assert cut, "no released section parsed out of CHANGELOG.md — the pattern broke"
    shipped = {b: v for b, v in bi.band_milestones(backlog_text).items() if v in cut}
    assert not shipped, (
        f"band(s) naming an already-cut release: {shipped}. Retire the band at the cut "
        "(RELEASE_PROCESS.md §4) — rows under it can never ship."
    )


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-n", "0", "-q"]))
