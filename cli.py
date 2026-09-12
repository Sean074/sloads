"""Command-line runner for the sloads suite.

Run one module against a project file and emit its load-case CSV (or a text
report to stdout):

    python cli.py engine examples/ga6_normal.project.json -o engine_loads.csv
    python cli.py engine examples/ga6_normal.project.json        # text to stdout
    python cli.py --list                                         # registered modules

Or export the solver deliverables. ``--export-target`` is the whole menu --
every artifact the Export & Report page writes is reachable headless, because
the concept-loads -> sbeam sizing loop is meant to be scripted.

**Note 56 D-56.2 cut this menu from ten targets to four.** The six that went
(``wing``, ``body``, ``tail``, ``htail-span``, ``vtail-span``, ``control``)
wrote *per-component* decks: each one a separate structural model of one piece
of the airplane, sharing an ID space with the deliverable and borrowing GIDs
from it. The deliverable is the whole airplane, balanced, with aero and inertia
together -- so the per-component views were four extra model concepts to
maintain and none of them was what ships.

===============  ===========================================================
target           what it writes
===============  ===========================================================
``lra``          the LRA beam model (step 12) -- node lines on the load
                 reference axes, CBAR chains, rigid posts/attachments/gear/
                 engine ties, the balanced cases' load sets transferred onto
                 the nodes. With ``--lra-import MODEL.bdf`` the loads are
                 instead transferred onto the imported model's own nodes,
                 under its GIDs (the named-node contract maps the families)
``balanced``     the assembled full-span balanced free-free deck
``gear``         the landing gear interface load definition (decision G-12) --
                 per case and per leg, the reaction at the tyre contact patch
                 with its strut state and ground angle, and the same reaction
                 at the gear reference point
``mass``         the CONM2/MASSSET mass model (same artifacts, same owner and
                 same names as ``--export-conm2``)
===============  ===========================================================

There is no default target any more: ``wing`` was the default because it was
the first thing the bridge could write, and a menu whose default has been
deleted should ask rather than guess.

    python cli.py --export-sbeam out --export-target lra examples/ga6_normal.project.json
    python cli.py --export-sbeam out --export-target balanced examples/ga6_normal.project.json
    python cli.py --export-conm2 out examples/ga6_normal.project.json

Or render the consolidated **summary report** (Step G8) -- the controlling
document of a loads deliverable. The ``.tex`` is always written; ask for a
``.pdf`` path and it is compiled too, when a TeX engine is on ``PATH``:

    python cli.py --report out.tex examples/ga6_normal.project.json
    python cli.py --report out.pdf examples/ga6_normal.project.json --units si

Output units follow ``--units imperial|si`` (default: the project's own
preference, else Imperial). An sbeam deck is written in the **solver** unit set,
which in SI is N / mm / N*mm / MPa -- consistent by construction, unlike the
N*m a report uses (M4-20 D-19).

**Every file written here carries the Step G8.3 methods & limitations stamp**
(``#`` on a CSV, ``$`` on a deck), exactly as the GUI bundle does: a headless
export states its ULTIMATE basis, its category and its approved corrections
in-band, so a file forwarded on its own is still self-describing (L-8g).

**Error contract** (one, for every export route): an absent input slice or an
invalid input is reported as ``error: <message>`` on stderr with exit status 1 --
never a traceback, and never a silently empty artifact. The one deliberate
exception is the ``control`` target, where an *absent* control-surface slice
(``MissingInputError``) skips that surface, because the three surfaces are
independent; an *invalid* one still fails the run, and a target where every
surface is absent fails too.
"""

from __future__ import annotations

import argparse
import sys

from sloads import MissingInputError, io, registry
from sloads.report import LoadChannel, module_text_report, text_report
from sloads.units import UnitSystem, convert_results, unit_system_from

#: Every headless export target, in the order the module docstring lists them.
#: This tuple is the deliverable menu -- review F-D1 was that the menu and the
#: deliverable set had diverged, so a test pins them together rather than a
#: comment asking future readers to keep them in step.
#:
#: **Ten to four** (note 56 D-56.2). ``wing``, ``body``, ``tail``,
#: ``htail-span``, ``vtail-span`` and ``control`` wrote the per-component solver
#: decks, which are deleted: they were parallel model concepts sharing an ID
#: space with the deliverable, and none of them was the deliverable.
#:
#: The note's own summary says this tuple goes to ``("lra", "mass")``. It does
#: not, on two counts, and the difference is deliberate. ``gear`` survives
#: because D-56.1 -- the same note -- reclassified the gear interface report as
#: a **document**, not a deck, and moved it to ``report.tables``; it ships in
#: the bundle and is the only headless route to it. ``balanced`` survives
#: because demoting the balanced deck to an internal producer turns on whether
#: ``roundtrip.py`` collapses to the single LRA solve gate, which is still open
#: (note 56 §8). Dropping either on the strength of a count would remove a live
#: deliverable ahead of its replacement.
EXPORT_TARGETS = ("balanced", "gear", "mass", "lra")


def resolve_units(project, flag=None) -> UnitSystem:
    """The unit system this run's output is rendered in.

    Resolution order, highest first: the ``--units`` flag, the project's own
    ``unit_system`` preference, then Imperial. A run with no flag and a project
    that never chose reproduces today's output exactly.
    """
    if flag:
        return unit_system_from(flag)
    return unit_system_from(getattr(project, "unit_system", None))


def _stamps(project, system: UnitSystem, generated: str = "",
            csv_channel: LoadChannel = LoadChannel.LIMIT):
    """``(csv_stamp, bdf_stamp)`` -- the Step G8.3 methods & limitations block.

    The headless counterpart of the Export & Report page's one-stamp-per-bundle
    build (L-8g / review F-D3): built once per run from the *resolved* unit
    system, then handed to every writer, so the files of one export cannot
    disagree with each other -- or with their own numbers -- about their basis
    or their units.

    ``scope`` is always the full case set: the Critical Loads opt-out selection
    is a GUI session state, so a headless export has nothing to filter and
    nothing to warn a recipient about. ``generated`` is the caller's timestamp
    and defaults to absent, which keeps two headless runs of one project
    byte-identical (the renderer never reads the clock -- see
    ``report.methods``).

    ``csv_channel`` is the basis of the CSV stamp alone (design note 48): the
    sbeam export's companion CSVs are ULTIMATE like the deck they describe,
    while the per-module ``-o`` CSV is the LIMIT channel and its stamp must say
    so. The BDF stamp is always ULTIMATE — a deck has no other basis.
    """
    from sloads.report.methods import bdf_comment_block, csv_comment_block

    kwargs = {"tool_version": _tool_version(), "scope": "full case set",
                  "system": system, "generated": generated or None}
    return (csv_comment_block(project, channel=csv_channel, **kwargs),
            bdf_comment_block(project, **kwargs))


def _export_conm2(project, prefix: str,
                  system: UnitSystem = UnitSystem.IMPERIAL,
                  bdf_stamp: str = "") -> int:
    """Write the CONM2/MASSSET mass model (plan 12 C-4).

    Three artifacts, and the split matters: the **fragment** is the mass model
    alone, for pasting into a model that already has the nodes; the **check
    deck** is self-contained and runnable (MASSSET + GRAV, and deliberately no
    load cards at all); the **inertia-only** file is sloads' own contribution,
    for comparing against what sbeam recovers -- never for applying.

    ``system`` is resolved once and passed to every writer, so the files of one
    export cannot disagree about their units (D-19), and ``bdf_stamp`` likewise
    so all three state one basis.

    A project with no weight database raises (caught by ``main``'s one error
    contract); a project that has one but from which no payload case is
    derivable still gets its fragment, with the two per-case artifacts reported
    as absent by name -- an unbuildable check deck is a fact about the data, not
    a failed run.
    """
    from sloads.export import mass_cards as mc

    fragment = mc.conm2_fragment(project, header_comment=bdf_stamp, system=system)

    label = "Imperial" if system == UnitSystem.IMPERIAL else "SI"
    written = []
    path = f"{prefix}_mass.bdf"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(fragment)
    written.append(path)

    # ``inertia_only`` retired with note 56 D-56.7: it cross-checked sloads'
    # reduction of a mass to a beam station, and D-56.6 leaves no reduction.
    for name, build in (("mass_check", mc.mass_check_deck),):
        try:
            text = build(project, header_comment=bdf_stamp, system=system)
        except ValueError as exc:
            print(f"note: no {name} deck -- {exc}", file=sys.stderr)
            continue
        path = f"{prefix}_{name}.bdf"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        written.append(path)

    _, loadings = mc.mass_cards(project)
    print(f"Wrote {', '.join(written)} ({label}; "
          f"{len(loadings)} derivable payload case(s))")
    return 0


def _export_sbeam(project, prefix: str, target: str,
                  system: UnitSystem = UnitSystem.IMPERIAL,
                  csv_stamp: str = "", bdf_stamp: str = "",
                  lra_import: str = "") -> int:
    """Build the loads for ``target`` and write the sbeam export artifacts.

    ``system`` is resolved once here and passed to every writer, so the files of
    one export cannot disagree with each other about their units (M4-20 D-19);
    ``csv_stamp``/``bdf_stamp`` ride along for the same reason (G8.3).

    Nothing here catches an exception: an absent or invalid input reaches
    ``main``'s single error contract.
    """
    from sloads.report import tables as rt

    if target == "gear":
        # The gear report needs LANDLOAD output and gear geometry and **no mass
        # model**, so it reaches airplanes the assembled ground cases do not --
        # which is why it is its own target rather than a file the balanced
        # target happens to drop beside its deck.
        csv_path = f"{prefix}.gear_loads.csv"
        rt.write_gear_report_csv(project, csv_path, header_comment=csv_stamp,
                                 system=system)
        rows = rt.gear_report_rows(project)
        print(f"Wrote {len(rows)} gear interface load row(s) to: {csv_path}")
        return 0

    if target == "lra":
        # The third deliverable (note 24 R-1). A missing datum raises
        # LraRefusal (a ValueError), which main's one error contract reports
        # as ``error: <the datum>`` -- a refused model is a stated absence,
        # never a traceback and never an empty file.
        if lra_import:
            from sloads.export.lra_import import write_lra_loads_on_imported_model

            out_path = f"{prefix}.lra_loads.bdf"
            write_lra_loads_on_imported_model(project, lra_import, out_path,
                                              header_comment=bdf_stamp,
                                              system=system)
            print(f"Wrote balanced-case loads on the imported model "
                  f"{lra_import} to: {out_path}")
            return 0
        from sloads.export.lra_model import write_lra_model_bdf

        bdf_path = f"{prefix}.lra_model.bdf"
        write_lra_model_bdf(project, bdf_path, header_comment=bdf_stamp,
                            system=system)
        print(f"Wrote the LRA beam model to: {bdf_path}")
        return 0

    if target == "balanced":
        from sloads.export.balanced_deck import balanced_deck
        from sloads.modules.balance import build_balanced_cases

        # Assembled once here rather than inside the writer, so the count printed
        # is the deck's own case set and not a second pass that might differ.
        skipped = []
        cases = build_balanced_cases(project, skipped)
        bdf_path = f"{prefix}.balanced_airframe.bdf"
        with open(bdf_path, "w", encoding="utf-8") as fh:
            fh.write(balanced_deck(project, header_comment=bdf_stamp, system=system,
                                   cases=cases, skipped=skipped))
        note = f"; {len(skipped)} condition(s) not assembled" if skipped else ""
        print(f"Wrote {len(cases)} balanced case(s) to: {bdf_path}{note}")
        return 0

    raise MissingInputError(
        f"unknown export target {target!r} -- expected one of "
        + ", ".join(EXPORT_TARGETS))


def _tool_version() -> str:
    """The installed package version, for the report's provenance block."""
    try:
        from importlib.metadata import PackageNotFoundError, version
    except ImportError:  # pragma: no cover - Python < 3.8
        return ""
    try:
        return version("sloads")
    except PackageNotFoundError:  # pragma: no cover - source checkout without install
        return ""


def _write_report(project, path: str, system: UnitSystem, generated: str = "") -> int:
    """Render the summary report to ``path`` (``.tex``, or ``.pdf`` to compile it).

    The ``.tex`` is the primary artifact and is written in both cases (beside the
    PDF), per decision G8-1: a machine with no TeX engine still gets the complete
    document source. ``generated`` is passed through so the caller owns the
    timestamp -- the renderer never reads the clock.
    """
    from sloads.report.latex import render_report

    tex = render_report(project, system=system, generated=generated,
                        tool_version=_tool_version())
    tex_path = path[:-4] + ".tex" if path.lower().endswith(".pdf") else path
    with open(tex_path, "w", encoding="utf-8") as fh:
        fh.write(tex)
    print(f"Wrote {tex_path}")
    if not path.lower().endswith(".pdf"):
        return 0

    from sloads.export.pdf import compile_pdf

    result = compile_pdf(tex)
    if not result.ok:
        print(f"PDF not produced: {result.log}", file=sys.stderr)
        return 1
    with open(path, "wb") as fh:
        fh.write(result.pdf)
    print(f"Wrote {path} ({len(result.pdf)} bytes, {result.engine})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run a sloads module on a project.")
    parser.add_argument("module", nargs="?", help="module name, e.g. 'engine'")
    parser.add_argument("project", nargs="?", help="path to project.json")
    parser.add_argument("-o", "--output", help="write load-case CSV to this path")
    parser.add_argument("--list", action="store_true", help="list registered modules and exit")
    parser.add_argument(
        "--export-sbeam", metavar="PREFIX",
        help="export loads to sbeam files prefixed with PREFIX; which loads is "
             "--export-target, which is required. PROJECT is then the second "
             "positional argument",
    )
    parser.add_argument(
        "--export-target",
        choices=EXPORT_TARGETS,
        default="lra",
        help="with --export-sbeam, which deliverable to export (default: lra). "
             "'lra' is the LRA beam model (step 12) -- the primary deliverable; "
             "'balanced' is the assembled full-span free-free deck; 'gear' is "
             "the landing gear interface load definition; 'mass' is "
             "the CONM2/MASSSET model, identical to --export-conm2",
    )
    parser.add_argument(
        "--lra-import", metavar="MODEL_BDF", default="",
        help="with --export-target lra: transfer the balanced-case loads onto "
             "this external GRID/CBAR beam model instead of the "
             "geometry-derived one -- the imported node line becomes the LRA "
             "and the cards are written under its own GIDs (the $ SLOADS-NODE "
             "named-node contract maps the families; nearest-node is the "
             "marked-assumed fallback)",
    )
    parser.add_argument(
        "--report", metavar="PATH",
        help="render the consolidated summary report to PATH (.tex; a .pdf path "
             "also compiles it when a TeX engine is available). PROJECT is then "
             "the second positional argument",
    )
    parser.add_argument(
        "--generated", metavar="STAMP", default="",
        help="the generation timestamp printed on the report title page and in "
             "every export's methods stamp (supplied by the caller so two runs "
             "stay byte-identical; omitted by default)",
    )
    parser.add_argument(
        "--export-conm2", metavar="PREFIX",
        help="write the CONM2/MASSSET mass model: PREFIX_mass.bdf (the model "
             "entire -- GRID at each item's CG + CONM2 + MASSSET) and "
             "PREFIX_mass_check.bdf (the same with case control and GRAV)",
    )
    parser.add_argument(
        "--units", choices=("imperial", "si"), default=None,
        help="unit system for the output; overrides the project's own preference "
             "for this run (default: the project's, else imperial)",
    )
    args = parser.parse_args(argv)

    if args.list:
        print("\n".join(registry.available()) or "(none registered)")
        return 0

    # --export-sbeam takes the project from the first positional (module slot) so
    # the module name is not required for an export-only run.
    if args.export_sbeam:
        project_path = args.module or args.project
        if not project_path:
            parser.error("--export-sbeam requires a project.json path")
        project = io.load_project(project_path)
        system = resolve_units(project, args.units)
        csv_stamp, bdf_stamp = _stamps(project, system, args.generated)
        # One error contract for every export route (review m2): an absent or
        # invalid input is a one-line `error:` on stderr and status 1, never a
        # traceback. The routes themselves catch nothing.
        try:
            if args.export_target == "mass":
                return _export_conm2(project, args.export_sbeam, system, bdf_stamp)
            return _export_sbeam(project, args.export_sbeam,
                                 args.export_target,
                                 system, csv_stamp, bdf_stamp,
                                 lra_import=args.lra_import)
        except ValueError as exc:      # MissingInputError included -- it subclasses
            print(f"error: {exc}", file=sys.stderr)
            return 1

    # --export-conm2 follows --export-sbeam's shape: project from the first
    # positional, no module name needed. It is the same owner (and the same file
    # names) as `--export-target mass`; both spellings are kept because this one
    # shipped first.
    if args.export_conm2:
        project_path = args.module or args.project
        if not project_path:
            parser.error("--export-conm2 requires a project.json path")
        project = io.load_project(project_path)
        system = resolve_units(project, args.units)
        _, bdf_stamp = _stamps(project, system, args.generated)
        try:
            return _export_conm2(project, args.export_conm2, system, bdf_stamp)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    # --report likewise takes the project from the first positional, so no module
    # name is needed for a report-only run.
    if args.report:
        project_path = args.module or args.project
        if not project_path:
            parser.error("--report requires a project.json path")
        project = io.load_project(project_path)
        return _write_report(project, args.report,
                             resolve_units(project, args.units), args.generated)

    if not args.module or not args.project:
        parser.error("module and project are required (or use --list / "
                     "--export-sbeam / --report)")

    try:
        run = registry.get(args.module)
    except KeyError as exc:
        parser.error(str(exc))

    project = io.load_project(args.project)
    try:
        result = run(project)
    except ValueError as exc:          # same one contract as the export routes
        print(f"error: {exc}", file=sys.stderr)
        return 1
    system = resolve_units(project, args.units)
    # The two text reports take *converted* results plus a display label; the CSV
    # writer converts internally (M4-20 step 3), so it gets the raw results and
    # the system -- handing it ``conditions`` would be a double conversion.
    # All three render on the LIMIT channel (design note 48, OR-76/OR-79): the
    # CLI's per-module output is an analysis surface, so it states the calc's own
    # loads and names the factor without applying it. The ULTIMATE deliverables
    # are ``sloads export``'s deck and the technical report.
    conditions = convert_results(result.conditions, system)
    label = "Imperial" if system == UnitSystem.IMPERIAL else "SI"

    if args.output:
        # A downloaded CSV leaves the tool, so it owes the same G8.3 basis
        # statement the GUI's does -- the text report to stdout does not, being
        # a terminal view rather than an artifact.
        csv_stamp, _ = _stamps(project, system, args.generated,
                               csv_channel=LoadChannel.LIMIT)
        io.write_load_cases_csv(result.conditions, args.output,
                                header_comment=csv_stamp, system=system,
                                channel=LoadChannel.LIMIT)
        print(f"Wrote {len(conditions)} condition(s) to {args.output} ({label})")
    elif args.module == "engine" and project.engine is not None:
        print(text_report(project.engine, conditions, unit_system=label,
                          channel=LoadChannel.LIMIT))
    else:
        print(module_text_report(result.module, conditions,
                                 channel=LoadChannel.LIMIT))

    return 0


if __name__ == "__main__":
    sys.exit(main())
