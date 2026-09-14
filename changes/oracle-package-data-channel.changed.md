- **The issue package's `data/` becomes the oracle GUI's only tabular channel
  (#245, tier M, 2026-09-13).** Three channels carried the same numbers, and the
  one an analyst actually needed carried nothing. Every results block offered a
  CSV and a McMaster print-format text twin (~20 blocks × 2); the sidebar built
  a whole-project results zip; the applied load sets shipped from `app/`'s
  export page and therefore not from the surviving front end at all — while the
  oracle report's Appendix F said in printed prose that its table is "the same
  set as the file `landing_gear_applied_loads.csv`", a file no production path
  wrote anywhere. OR-23 planned `data/` for this at design note 44 and OR-42
  deferred it; a package held five control files and no data. It now ships the
  six `*_applied_loads.csv`, `vn_conditions.csv`, `case_index.csv`,
  `safety_factors.csv`, `gear_loads.csv`, one `load_cases/<module>.csv` per
  module that produced a result, one file per appendix table no named file
  carries, and one file per figure the document draws. Owner:
  `sloads/report/package_data.py`; the rules are `ORACLE_REPORT.md` §1a.

- **One generation path, from one built document (#245).** `OracleDocument` now
  carries the reduced project and the module results its sections were built
  from, and the data emitter reads both off it. Not tidiness: the document is
  built from the *oracle projection* rather than from the project file, and an
  emitter handed the caller's own project would write files that disagree with
  the pages they are shipped beside — the failure `vn_conditions_csv` already
  had to guard against alone (G-OR-136). There is no second run of any module
  and no second formatter, so a file and the page that summarises it cannot
  describe different analyses.

- **The per-module downloads and the results zip retire, with nothing built to
  replace them (#245, note 60 D-60.12).** `sloads/report/results_zip.py` and its
  test are deleted; `app_shell/sidebar.py`'s two-step build-and-download block
  goes with them, and the `channel` parameter it was the only consumer of —
  every load sloads delivers has been LIMIT since note 49 OR-116, so the
  argument named a choice with one value. `oracle_app/results.py` loses
  `Artifact` and `page_artifacts` and renders a single caption per page saying
  where the files are instead. The text twins were porting-era verification
  artifacts and are not reproduced: the page-cited oracle tests carry that
  comparison.

- **The column inventory #245 required is a test, not a one-pass check (#245).**
  `tests/test_package_data.py::test_every_retired_per_module_csv_is_in_the_package_byte_for_byte`
  compares each `load_cases/<module>.csv` against `io.load_cases_csv` itself —
  the call the retired button made — on every bundled example, so "no column was
  lost" is asserted on every build rather than remembered from one session. The
  two checks the issue named by hand both came back clean and are recorded here:
  the **balanced V-n matrix** and the envelope module's own 300-point table are
  different quantities and both ship (`vn_conditions.csv` and
  `load_cases/flight_envelope.csv`); LANDLOAD's **primed ground-line set** is in
  `gear_loads.csv`'s `Ground-line V/D/S` columns, so retiring the text report it
  used to be read from loses nothing.

- **The one-engine-inoperative yaw march gets a file, and so does every other
  figure (#245).** The inventory's real find: section 11 draws the transient as
  two figures per case and has no printed table of it, the module's own CSV
  carries six summary rows, and the finer time history existed only behind a
  button on a page #270 deletes — so the march would have been lost between two
  changes that each looked complete. The emitter is generic over
  `content.PlotData` rather than special-cased for it: `figures/<key>.csv`,
  long form, one row per plotted point with the series it belongs to, for every
  figure the document draws. 44 to 54 files on the bundled examples, and the
  next curve whose numbers a reader wants needs no second discovery.

- **Every shipped file is self-describing, and the document lists them (#245).**
  G-OR-15 and G-OR-17 had bodies written at design note 44 and were vacuous for
  a fortnight because there was no data to assert them over. Each file now
  carries its own four-line header — what it is, which step produced it, where
  the document summarises it, and the build's analysis fingerprint — above the
  methods statement that supplies the units, the axes and the factor stated and
  not applied. The document's front matter gained a **Data reference** table
  built from the file list itself, so the `.tex` names every file the package
  carries and the package carries every file the `.tex` names.

- **G-OR-73 re-cut to the consolidated set (#245).** Its document half read four
  applied CSVs this repository's test file rebuilt by hand; it now also scans
  every file `package_data.data_files` decides to ship — the gear and engine
  applied sets, the V-n conditions, the gear report and every module's load
  cases, none of which had a basis gate at all. A file added to the package is
  gated the day it is added rather than the day somebody remembers the list.
