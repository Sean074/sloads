"""What a delivered file says about the frame its numbers are in (#242).

The 2026-09-08 CSV review checked the requirement these files exist to serve --
contents in airplane global coordinates, readable without the repository -- and
found the **data** met it and the **self-description** did not (findings C2 and
C3):

* no delivered file anywhere said which way ``+x`` points. The per-file blocks
  said "right-handed about the airplane axes" and named torsion axes, which
  presumes the frame rather than stating it, and the methods stamp -- the one
  statement every channel carries -- had no AXES block at all;
* the one column that named an axis, ``MyyAxis``, named the wrong one on the
  fin, whose torsion ``applied_body_moments`` puts in ``Mz`` because a lateral
  load can make no moment about ``y``;
* the gear report states two frames in one row -- the manual's ground line and
  the airplane datum -- and named neither, which an AXES stanza covering the
  whole file would have made worse rather than better;
* the V-n conditions file carried nineteen columns and the definitions of five
  of them stayed on the page.

These guards hold each half, and hold the shape of the fix: the axis words have
**one owner** (``export.coordinates``), rendered by one block, so a file cannot
acquire a second spelling of the frame.

Reference: 2026-09-08 oracle report/GUI/CSV review §4 C2+C3+C4; ``CONVENTIONS.md``
§1; issue #242.
"""

import csv
import io as _io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from imperial_baseline import EXAMPLES, artifacts  # noqa: E402

from sloads import io  # noqa: E402
from sloads.export.coordinates import AIRPLANE_AXES, AXES_NOTES  # noqa: E402
from sloads.report import applied as ap  # noqa: E402
from sloads.report import methods as M  # noqa: E402
from sloads.report import oracle_sections as osec  # noqa: E402
from sloads.report import tables as rt  # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: The applied channels the baseline renders, keyed the way it keys them.
_APPLIED = tuple(f"sbeam/{c}_applied" for c in
                 ("wing", "body", "htail", "vtail", "landing_gear", "engine"))


def _project(example="ga6_normal.project.json"):
    return io.load_project(os.path.join(_ROOT, "examples", example))


def _rows(text):
    """The data rows of one delivered CSV, its ``#`` header block dropped."""
    body = "\n".join(ln for ln in text.splitlines() if not ln.startswith("#"))
    return list(csv.DictReader(_io.StringIO(body)))


# --------------------------------------------------------------------------- #
# C2 -- the frame is stated, once, on every channel
# --------------------------------------------------------------------------- #
def test_every_stamped_channel_states_which_way_the_axes_point():
    """The stanza reaches the CSV, the deck and the prose alike.

    One statement wrapped per channel is the whole design of the stamp (G8-3);
    the axis block is only worth having if it inherits that, because the reader
    it is written for is the one holding a single forwarded file.
    """
    project = _project()
    channels = {
        "prose": M.methods_statement(project),
        "csv": M.csv_comment_block(project),
        "bdf": M.bdf_comment_block(project),
    }
    for name, text in channels.items():
        assert "AXES:" in text, f"{name} carries no axis statement"
        for symbol, axis_name, sense in AIRPLANE_AXES:
            assert f"{symbol} = {axis_name}, {sense}" in text, (
                f"{name} does not state the {symbol} axis")
        for note in AXES_NOTES:
            assert note in text, f"{name} drops an axis note"


def test_the_axis_words_have_exactly_one_home():
    """No second spelling of the frame anywhere in the package.

    The defect this closes is not "the sentence is missing" but "the sentence is
    a convention nobody owns": a frame restated per file is a frame that survives
    an axis flip. ``export/coordinates`` is the declared single edit-point for
    the map (``CONVENTIONS.md`` §1), so it is where the words live, and every
    other module reads them.
    """
    senses = [sense for _s, _n, sense in AIRPLANE_AXES]
    for dirpath, dirnames, filenames in os.walk(os.path.join(_ROOT, "sloads")):
        dirnames[:] = [d for d in dirnames if not d.startswith("__")]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8").read()
            for sense in senses:
                if sense in text:
                    assert path.endswith(os.path.join("export", "coordinates.py")), (
                        f"{path} spells an axis sense that "
                        f"export/coordinates.py owns: {sense!r}")


def test_the_frame_statement_does_not_depend_on_the_airplane():
    """Two different projects get the same axis stanza, to the byte.

    It is the suite's frame, not a property of a configuration; a block that
    could differ between two bundles is a block a reader has to compare.
    """
    blocks = set()
    for example in ("ga6_normal.project.json", "baron_58.project.json"):
        text = M.methods_statement(_project(example))
        start = text.index("AXES:")
        blocks.add(text[start:text.index("\n\n", start)])
    assert len(blocks) == 1


# --------------------------------------------------------------------------- #
# C3 -- a column name may not claim an axis its own file contradicts
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_no_delivered_header_still_says_myyaxis(example):
    """``MyyAxis`` is gone from the applied files -- it was false on one of six.

    The fin's torsion is ``Mz``. A column called ``MyyAxis`` beside an all-zero
    ``My`` column is the C3 defect in miniature: a frame claim the data next to
    it does not honour.
    """
    for channel, text in artifacts(example).items():
        if channel not in _APPLIED:
            continue
        header = next(ln for ln in text.splitlines() if not ln.startswith("#"))
        assert "MyyAxis" not in header, f"{channel} still names MyyAxis"
        assert "TorsionAxis" in header, f"{channel} names no torsion axis"


def test_a_surfaces_torsion_is_in_the_moment_column_of_its_own_span_axis():
    """The claim ``MyyAxis`` got backwards, asserted from the physics.

    A surface's torsion is about its **span** axis: the h-tail spans in ``y``
    and its torsion is ``My``; the fin spans in ``z`` and its torsion is ``Mz``,
    and its ``My`` is identically zero because a lateral load makes no moment
    about ``y``. Read off the station-level set, which is where that statement
    is about the calc's own free moments -- the delivered rows are at the LRA
    grids and carry the transfer couple of their offsets on every axis, which is
    exactly the distinction the old column name elided.
    """
    from sloads.modules.tail_span import build_tail_span

    project = _project()
    spans = build_tail_span(project)
    for component, torsion, empty in (("htail", 1, 2), ("vtail", 2, 1)):
        rows = ap.station_applied_loads(component, spans[component], project)
        moments = [ap.applied_body_moments(r) for r in rows]
        assert any(m[torsion] for m in moments), component
        assert not any(m[empty] for m in moments), (
            f"{component}: a moment appears on an axis its load cannot make one about")
        assert all(r.torsion_axis for r in rows), component


def test_the_tail_files_say_a_control_row_is_a_surface_normal_load():
    """C3's own example: the rudder's normal load is lateral, and says so.

    The deleted ``control_surface_loads.csv`` labelled that column ``Fz`` on
    every surface. The rows survived into the tail applied files, resolved onto
    the right airplane axis by ``tail_force_to_airplane`` -- the numbers were
    never wrong -- but nothing told the reader that the number in ``Fy`` on a
    fin row is a surface-normal load rather than a sideslip load.
    """
    htail, vtail = ap._APPLIED_CSV_WHAT["htail"], ap._APPLIED_CSV_WHAT["vtail"]
    for note in (htail, vtail):
        assert "control" in note and "NORMAL" in note
    assert "lateral" in vtail and "not Fz" in vtail


# --------------------------------------------------------------------------- #
# C3 -- a file may not publish a zero its own rows contradict
# --------------------------------------------------------------------------- #
_LOAD_COLUMNS = ("Fx", "Fy", "Fz", "Mx", "My", "Mz")


def _zero_and_filled(text):
    """``(columns zero in every row, columns some row fills)`` for one file."""
    rows = _rows(text)
    if not rows:
        return set(), set()
    key = {c.split(" ")[0]: c for c in rows[0] if c.split(" ")[0] in _LOAD_COLUMNS}
    zero, filled = set(), set()
    for name, col in key.items():
        (zero if all(float(r[col]) == 0.0 for r in rows) else filled).add(name)
    return zero, filled


@pytest.mark.parametrize("example", EXAMPLES)
def test_no_applied_file_claims_a_zero_its_own_rows_fill(example):
    """The defect the derived block exists to make impossible.

    Note 56 D-56.9 re-aggregated the delivered set onto the LRA grids, where each
    load carries the lever-arm couple of its offset -- and moments appeared on
    three axes four of the six hand-written notes had called zero "throughout".
    The numbers moved and the prose did not, which is the one direction a
    written-out convention cannot defend itself in.
    """
    for component in ("wing", "fuselage", "htail", "vtail",
                      "landing_gear", "engine"):
        channel = f"sbeam/{'body' if component == 'fuselage' else component}_applied"
        text = artifacts(example).get(channel)
        if not text:
            continue
        _zero, filled = _zero_and_filled(text)
        head = "\n".join(ln for ln in text.splitlines() if ln.startswith("#"))
        for name in filled:
            assert f"{name} is zero" not in head, (
                f"{channel} says {name} is zero and then fills it")


@pytest.mark.parametrize("example", EXAMPLES)
def test_every_zero_column_is_accounted_for_in_the_file(example):
    """A zero is published with a statement, structural or incidental (OR-140).

    Both kinds, and never the wrong one: a column the model cannot fill is not
    the same thing as a column this airplane happens to leave empty, and a reader
    who is told the second is the first will design around a load that the next
    configuration produces.
    """
    for component in ("wing", "fuselage", "htail", "vtail",
                      "landing_gear", "engine"):
        channel = f"sbeam/{'body' if component == 'fuselage' else component}_applied"
        text = artifacts(example).get(channel)
        if not text:
            continue
        zero, _filled = _zero_and_filled(text)
        head = "\n".join(ln for ln in text.splitlines() if ln.startswith("#"))
        reasons = ap._APPLIED_ZERO_REASONS[component]
        for name in zero:
            assert f"{name} is zero in every row" in head, (
                f"{channel}: {name} is zero in every row and unstated")
            if name in reasons:
                assert "STRUCTURAL ZEROS" in head
            else:
                assert "ALSO ZERO, but not structurally" in head


def test_no_structural_zero_reason_outlives_its_column():
    """A reason in the table names a column that is empty on every example.

    The stale half of the same defect, caught from the other side: a reason kept
    for a column the model has since learned to fill would print a false
    statement on the first airplane that filled it.
    """
    for example in EXAMPLES:
        art = artifacts(example)
        for component, reasons in ap._APPLIED_ZERO_REASONS.items():
            channel = f"sbeam/{'body' if component == 'fuselage' else component}_applied"
            text = art.get(channel)
            if not text:
                continue
            _zero, filled = _zero_and_filled(text)
            stale = sorted(set(reasons) & filled)
            assert not stale, (
                f"{component}: {stale} carry a structural-zero reason and are "
                f"filled on {example}")


@pytest.mark.parametrize("example", EXAMPLES)
def test_a_file_at_grids_says_it_is_at_grids(example):
    """The sentence whose absence let the zeros go stale.

    A row at a beam grid carries the couple of its own offset to that grid; a
    row at a load station does not. Without the statement a fin row's Mx reads
    as a rolling moment on the fin. Asserted both ways round -- the two
    components that are never re-aggregated must not claim it.
    """
    from sloads.export.lra_model import build_lra_model

    art = artifacts(example)
    try:
        build_lra_model(_project(example))
        has_beam = True
    except ValueError:
        # No named datum, or a planform its scalar geometry contradicts: the
        # applied set falls back to the load stations and must not claim grids.
        has_beam = False
    for component in ("wing", "fuselage", "htail", "vtail",
                      "landing_gear", "engine"):
        channel = f"sbeam/{'body' if component == 'fuselage' else component}_applied"
        text = art.get(channel)
        if not text:
            continue
        says = "at the LRA beam model's grids" in text
        if component in ap._NOT_RE_AGGREGATED or not has_beam:
            assert not says, f"{channel} is not at grids and says it is"
        else:
            assert says, f"{channel} is at grids and does not say so"


# --------------------------------------------------------------------------- #
# C3 -- the one file with two frames names both
# --------------------------------------------------------------------------- #
def test_the_gear_report_names_the_frame_of_every_column_it_has():
    """A file with two frames may not inherit a stanza written for one.

    Every coordinate and load column is named in the file's own note, on one
    side or the other of the ground-line/airplane split -- checked against the
    field list itself, so a column added later is a failure rather than a
    silently unclassified one.
    """
    note = rt._GEAR_REPORT_NOTES
    assert "GROUND-LINE" in note and "airplane axes" in note
    framed = [f for f in rt._GEAR_REPORT_FIELDS
              if f.startswith(("Patch ", "Ground-line ", "Datum ",
                               "Ref point ", "Transfer "))]
    assert framed, "the gear report has no frame-bearing columns to check"
    for field in framed:
        head, tail = field.rsplit(" ", 1)
        assert f"{head} " in note or field in note, (
            f"the gear report's note does not place {field!r} in a frame")
        assert tail in note or f"{head}/" in note or field in note


def test_the_gear_report_states_its_frames_with_no_stamp_above_it():
    """The note stands on its own.

    One caller downloads this file without a methods stamp, so a note that said
    "the stanza above" would be pointing at nothing on the copy most likely to
    be read alone.
    """
    text = rt.gear_report_csv(_project())
    assert "above" not in rt._GEAR_REPORT_NOTES
    assert "GROUND-LINE" in text.split("ID,Case,")[0]


# --------------------------------------------------------------------------- #
# C4 -- a file defines its own columns, and is one text
# --------------------------------------------------------------------------- #
def test_the_vn_file_carries_the_definitions_its_page_prints():
    """M(W+F), LZW, LT, DX and NX are defined in the file, from the page's words.

    The notes are read off the same ``Table`` objects the appendix renders, so
    this asserts the identity rather than a copy: a reworded page note that did
    not reach the file would fail here.
    """
    project = _project()
    text = osec.vn_conditions_csv(project)
    assert text
    notes = " ".join(ln.lstrip("# ") for ln in text.splitlines()
                     if ln.startswith("#"))
    for term in ("M(W+F)", "LZW", "LT", "DX", "NX"):
        assert term in notes, f"{term} is undefined in the V-n file"
    assert "LIMIT" in notes
    # Page-relative language would be a lie in a file that joins the two tables
    # into one row.
    assert "table below" not in notes and "case above" not in notes


@pytest.mark.parametrize("example", EXAMPLES)
def test_no_delivered_channel_mixes_its_line_endings(example):
    """One file, one line ending (``csv_text.CSV_LINE_TERMINATOR``).

    Every stamped CSV used to be LF in its comment block and CRLF in its rows,
    because the prose was joined by hand and the data came from :mod:`csv`'s
    default. Asserted over every channel the baseline renders, decks included,
    so the rule is the package's and not the CSV writers' alone.
    """
    for channel, text in artifacts(example).items():
        assert "\r" not in text, f"{channel} carries a carriage return"


def test_the_line_ending_has_one_owner():
    """No writer may set its own terminator.

    The failure this prevents is invisible in every viewer: a ``csv.writer``
    added later without the argument writes a file that looks right and is mixed
    on disk. So the argument is not passed at call sites at all -- the two
    constructions are made by ``sloads.csv_text``.
    """
    for dirpath, dirnames, filenames in os.walk(os.path.join(_ROOT, "sloads")):
        dirnames[:] = [d for d in dirnames if not d.startswith("__")]
        for fn in filenames:
            if not fn.endswith(".py") or fn == "csv_text.py":
                continue
            text = open(os.path.join(dirpath, fn), encoding="utf-8").read()
            assert "csv.writer(" not in text and "csv.DictWriter(" not in text, (
                f"{fn} builds a CSV writer of its own; use sloads.csv_text")


if __name__ == "__main__":  # pragma: no cover - zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
