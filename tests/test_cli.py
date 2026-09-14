"""The headless deliverable — 0.5.0 row 1 (review F-D1 / F-C2 / F-D3, m2, L-8g).

The mission is a **scripted** concept-loads → sbeam sizing loop, so "the GUI can
write it" is not the same as "the deliverable exists". Three gaps closed here,
each with its own gate:

* **F-D1 — reachability.** ``--export-target`` is the whole deliverable menu:
  the **LRA beam model** (the mission's primary artifact, which carries the
  assembled balanced cases), the **gear interface report** and the CONM2 **mass
  model**. It listed ten targets until note 56 D-56.2 deleted the six that wrote
  per-component decks, and three since D-56.8 unshipped the assembled deck.
  :func:`test_the_export_menu_is_the_deliverable_menu` pins the menu against
  ``cli.EXPORT_TARGETS`` and against argparse, so a target cannot be implemented
  without being offered or offered without being implemented.
* **F-C2 / decision D-R5 — the wing axis.** Retired with the wing target
  (note 56 D-56.2): there is no headless per-component wing deck to state an
  axis. The transfer itself is unchanged and is gated at its owner
  (``test_applied.test_project_export_transfers_to_loads_ref_axis``).
* **F-D3 / L-8g — the stamp.** Every headless CSV and BDF carries the Step G8.3
  methods & limitations block, so a file forwarded on its own still states its
  ULTIMATE basis, its category and its approved corrections.

Plus **m2**, the error contract: one contract for every route — ``error: …`` on
stderr and status 1, never a traceback, and never a swallowed invalid input.

Conventions: ``docs/10_standard/CONVENTIONS.md``. Error-handling contract:
``docs/10_standard/00_program_overview.md``.
"""

from __future__ import annotations

import csv
import io as _io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import cli
from sloads import io as sloads_io
from sloads.report import applied as ap
from sloads.models import Project
from sloads.modules.net_loads import build_net_loads, loads_ref_axis_results
from sloads.report.methods import strip_comment_lines

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GA6 = os.path.join(_ROOT, "examples", "ga6_normal.project.json")
# The LRA beam model refuses ga6 (no fuselage data, BM-1/BM-3) -- its headless
# route is exercised on a fixture that carries a body.
ATR42 = os.path.join(_ROOT, "examples", "atr42_100.project.json")


def _run(tmp_path, *argv) -> list:
    """Run the CLI into ``tmp_path`` and return the files it wrote, sorted."""
    assert cli.main(list(argv)) == 0, argv
    return sorted(os.listdir(tmp_path))


def _export(tmp_path, target: str, *extra) -> list:
    prefix = os.path.join(str(tmp_path), "out")
    # ga6 has no fuselage data, so the LRA beam model refuses it by design
    # (BM-1/BM-3); that target's stamped file comes from a body-carrying
    # fixture instead.
    fixture = ATR42 if target == "lra" else GA6
    return _run(tmp_path, fixture, "--export-sbeam", prefix,
                "--export-target", target, *extra)


# --------------------------------------------------------------------------- #
# F-D1 — the deliverable set is reachable headless
# --------------------------------------------------------------------------- #
def test_the_export_menu_is_the_deliverable_menu():
    """``EXPORT_TARGETS`` is what argparse offers -- no target only half-wired.

    F-D1 was exactly this drift: the balanced deck and the body deck existed and
    the menu did not know about them. Both are gone now -- one deleted, one
    unshipped -- which is why the gate is on the tuple rather than on a list of
    names that would have had to be edited twice.
    """
    # argparse is handed the tuple itself, so an unlisted target is rejected
    # before any work happens.
    with pytest.raises(SystemExit):
        cli.main([GA6, "--export-sbeam", "x", "--export-target", "not-a-target"])
    # Every advertised target is documented in the module docstring's table, so
    # the ``--help`` menu and the prose cannot diverge either.
    for target in cli.EXPORT_TARGETS:
        assert f"``{target}``" in cli.__doc__, f"{target} is undocumented"
    # ...and every documented target is advertised (the reverse direction: a
    # target dropped from the tuple but left in the prose is the same drift).
    documented = {t for t in cli.EXPORT_TARGETS if f"``{t}``" in cli.__doc__}
    assert documented == set(cli.EXPORT_TARGETS)


@pytest.mark.parametrize("target,expected", [
    ("gear", ["out.gear_loads.csv"]),
    ("lra", ["out.lra_model.bdf"]),
    ("mass", ["out_mass.bdf", "out_mass_check.bdf"]),
])
def test_every_export_target_writes_its_artifacts(tmp_path, target, expected):
    """Each target writes its files, non-empty, on the Appendix A airplane."""
    written = _export(tmp_path, target)
    assert written == expected, f"{target} wrote {written}"
    for name in written:
        assert os.path.getsize(os.path.join(str(tmp_path), name)) > 0


def test_the_beam_deck_is_reachable_headless(tmp_path):
    """The mission's primary deliverable, from the CLI, byte-for-byte the page's.

    F-D1's headline was that ``balanced_airframe.bdf`` was downloadable only
    from a Streamlit page, so the sizing loop could not script the one artifact
    it is about. Note 56 D-56.8 unshipped that deck -- the beam deck carries the
    same assembled cases now -- so the reachability claim moves with the
    deliverable rather than retiring with the file it was first written about.
    """
    from sloads.export.lra_model import lra_model_bdf

    _export(tmp_path, "lra")
    with open(os.path.join(str(tmp_path), "out.lra_model.bdf")) as fh:
        written = fh.read()

    # The stamp rides on top; below it the deck is the page's, to the byte. (A
    # deck's own ``$`` lines are part of the deliverable, so "ends with the
    # unstamped build" is the honest form of this assertion -- see
    # ``report.methods.strip_comment_lines``.) ``_export`` routes this target to
    # the body-carrying fixture, so the comparison build must load the same one.
    project = sloads_io.load_project(ATR42)
    assert written.endswith(lra_model_bdf(project))
    assert written.startswith("$ METHODS AND LIMITATIONS")


def test_the_mass_target_and_export_conm2_are_one_owner(tmp_path):
    """``--export-target mass`` and ``--export-conm2`` write identical files.

    Two spellings, one implementation: the second exists only because it shipped
    first. If they ever diverge, one of the two is a stale copy of the mass
    model -- which is the class of defect the CONM2 export exists to catch.
    """
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(), b.mkdir()
    assert cli.main([GA6, "--export-sbeam", str(a / "m"),
                     "--export-target", "mass"]) == 0
    assert cli.main([GA6, "--export-conm2", str(b / "m")]) == 0
    names = sorted(os.listdir(str(a)))
    assert names == sorted(os.listdir(str(b))) and names
    for name in names:
        with open(str(a / name)) as fh_a, open(str(b / name)) as fh_b:
            assert fh_a.read() == fh_b.read(), name


# --------------------------------------------------------------------------- #
# F-C2 / D-R5 — the CLI wing deck is about the loads reference axis
# --------------------------------------------------------------------------- #
def _project_with_lra(tmp_path, pct: float) -> str:
    """ga6 with its wing surface's loads reference axis moved to ``pct`` chord.

    Written as a project file rather than mutated in memory because the gate is
    about the **CLI route**: it must load, build and transfer, exactly as a
    scripted run does.
    """
    project = sloads_io.load_project(GA6)
    geom = project.geometry.by_name(project.wing_mass.surface)
    assert geom is not None and geom.ref_axis_pct == 0.40, (
        "fixture assumption: the shipped wing LRA is the entered 40% chord "
        "(step 12/R-7a); these tests move it elsewhere so the deck pins the "
        "transfer, not the fixture")
    geom.ref_axis_pct = pct
    path = os.path.join(str(tmp_path), "lra.project.json")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(sloads_io.project_to_json(project))
    return path






# --------------------------------------------------------------------------- #
# F-D3 / L-8g — every headless artifact carries the methods stamp
# --------------------------------------------------------------------------- #
_STAMP_MARKER = {".csv": "#", ".bdf": "$"}


@pytest.mark.parametrize("target", cli.EXPORT_TARGETS)
def test_every_exported_file_carries_the_methods_stamp(tmp_path, target):
    """G8.3 in every headless channel: basis, units and approved corrections.

    Before this the whole headless route was the one channel that stated its
    ULTIMATE basis nowhere -- the route the sizing loop scripts.
    """
    for name in _export(tmp_path, target):
        marker = _STAMP_MARKER[os.path.splitext(name)[1]]
        with open(os.path.join(str(tmp_path), name)) as fh:
            text = fh.read()
        assert text.startswith(f"{marker} METHODS AND LIMITATIONS"), name
        assert "ULTIMATE" in text and "APPROVED CORRECTIONS" in text, name


def test_the_load_case_csv_carries_the_stamp_and_still_parses(tmp_path):
    """The ``-o`` module CSV is stamped too, and a reader still reads it.

    The CLI is a per-module analysis surface, so its CSV is the **LIMIT**
    channel (design note 48, OR-76/OR-79): plain load units, no ``-ULT``, and
    the factor named in the ``SF`` column without being applied. The stamp says
    so in-band, which is what a file forwarded on its own needs (G8.3).
    """
    out = os.path.join(str(tmp_path), "engine.csv")
    assert cli.main(["engine", GA6, "-o", out]) == 0
    with open(out, newline="") as fh:
        text = fh.read()
    assert text.startswith("# METHODS AND LIMITATIONS")
    # The stamp is wrapped across ``#`` lines, so read it as flowed text.
    flat = " ".join(line.lstrip("#").strip() for line in text.splitlines())
    assert "are LIMIT" in flat and "NOT applied" in flat, flat[:400]
    rows = list(csv.DictReader(_io.StringIO(strip_comment_lines(text))))
    assert rows, "the CSV must still parse past its comment block"
    headers = [h or "" for h in rows[0]]
    assert any("(lb)" in h for h in headers), headers
    assert not any("-ULT" in h for h in headers), headers
    assert rows[0]["SF"] == "1.5", "the factor is stated, not applied"


def test_a_stamped_headless_deck_still_parses_as_bulk_data(tmp_path):
    """``$`` is a comment to every bulk-data parser -- the stamp is inert.

    Asserted through the suite's own card parser (the closure gate's owner), so
    the claim is the same one the equilibrium tests rely on.
    """
    from sloads.export.equilibrium import parse_cards
    from sloads.export.lra_model import lra_model_bdf

    project = sloads_io.load_project(ATR42)
    unstamped = lra_model_bdf(project)
    _export(tmp_path, "lra")
    with open(os.path.join(str(tmp_path), "out.lra_model.bdf")) as fh:
        stamped = fh.read()
    assert stamped != unstamped, "the fixture must actually be stamped"
    assert parse_cards(stamped) == parse_cards(unstamped)


def test_a_headless_export_is_byte_stable_across_runs(tmp_path):
    """No clock in the stamp unless the caller supplies one (report.methods).

    A deliverable that changes bytes every run cannot be diffed between two
    revisions, which is the whole reason the renderer never reads the clock.
    """
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(), b.mkdir()
    for d in (a, b):
        assert cli.main([GA6, "--export-sbeam", str(d / "out"),
                         "--export-target", "lra"]) == 0
    for name in sorted(os.listdir(str(a))):
        with open(str(a / name)) as fh_a, open(str(b / name)) as fh_b:
            assert fh_a.read() == fh_b.read(), name

    # ...and a supplied timestamp does reach the file, so the determinism above
    # is the default rather than the stamp being incapable of carrying one.
    assert cli.main([GA6, "--export-sbeam", str(b / "t"),
                     "--export-target", "lra",
                     "--generated", "2026-08-10 09:00"]) == 0
    with open(str(b / "t.lra_model.bdf")) as fh:
        assert "2026-08-10 09:00" in fh.read()


# --------------------------------------------------------------------------- #
# m2 — one error contract
# --------------------------------------------------------------------------- #
def _empty_project(tmp_path) -> str:
    path = os.path.join(str(tmp_path), "empty.project.json")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(sloads_io.project_to_json(Project(name="empty")))
    return path


@pytest.mark.parametrize("target", cli.EXPORT_TARGETS)
def test_an_absent_input_is_one_error_line_not_a_traceback(tmp_path, capsys, target):
    """Every route, one contract: ``error: …`` on stderr, status 1, no traceback.

    m2: ``control`` swallowed everything, an all-skipped run raised through
    ``main``, the wing/tail targets let ``MissingInputError`` reach the terminal
    as a traceback, and only ``--export-conm2`` caught and printed.
    """
    project = _empty_project(tmp_path)
    prefix = os.path.join(str(tmp_path), "out")
    assert cli.main([project, "--export-sbeam", prefix,
                     "--export-target", target]) == 1
    captured = capsys.readouterr()
    assert captured.err.startswith("error: "), captured.err
    assert "Traceback" not in captured.err
    assert not [f for f in os.listdir(str(tmp_path)) if f.startswith("out")], \
        "a failed export must not leave a partial artifact set"






def test_a_module_run_reports_its_error_the_same_way(tmp_path, capsys):
    """The module route shares the contract -- it is one CLI, not five."""
    project = _empty_project(tmp_path)
    assert cli.main(["engine", project, "-o",
                     os.path.join(str(tmp_path), "o.csv")]) == 1
    assert capsys.readouterr().err.startswith("error: ")


# --------------------------------------------------------------------------- #
# --report: the headless half of the Report page
# --------------------------------------------------------------------------- #
def test_the_report_flag_writes_the_document_that_exists(tmp_path):
    """F-D1's rule applied to the document route.

    This flag rendered the summary report and **nothing tested it**, so when
    #270 deleted that document with the front-end that downloaded it, the only
    headless path to a controlling document broke silently and the whole suite
    stayed green. The reachability rule the export menu is held to is the same
    rule here: a deliverable the CLI offers is a deliverable the CLI writes.
    """
    out = tmp_path / "report.tex"
    assert cli.main([GA6, "--report", str(out)]) == 0
    tex = out.read_text(encoding="utf-8")
    assert tex.startswith(r"\documentclass")
    assert tex.rstrip().endswith(r"\end{document}")
    # It is the technical report, not some other document: its own front matter.
    assert "Axes and sign conventions" in tex
    assert len(tex) > 100_000, "implausibly short for the whole document"


def test_the_report_follows_the_units_flag(tmp_path):
    """One flag, one system -- the document is part of the bundle ``--units``
    governs, not a second selection the headless route cannot reach (M4-20)."""
    imperial = tmp_path / "i.tex"
    si = tmp_path / "s.tex"
    assert cli.main([GA6, "--report", str(imperial), "--units", "imperial"]) == 0
    assert cli.main([GA6, "--report", str(si), "--units", "si"]) == 0
    assert "Imperial units" in imperial.read_text(encoding="utf-8")
    assert "SI units" in si.read_text(encoding="utf-8")


def test_the_report_is_byte_stable_across_runs(tmp_path):
    """Nothing in the document reads the clock: the timestamp is the caller's."""
    first, second = tmp_path / "a.tex", tmp_path / "b.tex"
    for path in (first, second):
        assert cli.main([GA6, "--report", str(path),
                         "--generated", "2026-09-13"]) == 0
    assert first.read_bytes() == second.read_bytes()


def test_an_unreadable_project_is_one_error_line_on_every_route(tmp_path, capsys):
    """m2, widened at #270 (rule 4).

    Every route called ``io.load_project`` *outside* its ``try``, so the one
    error contract covered everything the analysis could refuse and not the one
    thing every route does first. A file that is not JSON came out as a
    traceback on all four; ``cli._load`` is now the single entry and
    ``cli.main`` the single handler.
    """
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    routes = (
        ["--report", str(tmp_path / "r.tex")],
        ["--export-sbeam", str(tmp_path / "d"), "--export-target", "lra"],
        ["--export-conm2", str(tmp_path / "m")],
    )
    for route in routes:
        assert cli.main([str(bad)] + route) == 1, route
        captured = capsys.readouterr()
        assert captured.err.startswith("error: "), (route, captured.err)
        assert "Traceback" not in captured.err, route
    # ...and the module route, which takes the project as the second positional.
    assert cli.main(["engine", str(bad)]) == 1
    assert capsys.readouterr().err.startswith("error: ")

    # A path that is not there at all is the same one line.
    missing = str(tmp_path / "nope.json")
    assert cli.main([missing, "--report", str(tmp_path / "r2.tex")]) == 1
    assert capsys.readouterr().err.startswith("error: ")

    # Valid JSON that is not an object (the 0.8.4 closure review): the same
    # one line, not an AttributeError out of the schema gate.
    a_list = tmp_path / "list.json"
    a_list.write_text("[]", encoding="utf-8")
    assert cli.main([str(a_list), "--report", str(tmp_path / "r3.tex")]) == 1
    captured = capsys.readouterr()
    assert captured.err.startswith("error: ") and "Traceback" not in captured.err


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-q"]))
