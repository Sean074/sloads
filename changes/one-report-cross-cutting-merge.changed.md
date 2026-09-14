- **The summary report's cross-cutting sections merge into the oracle report, and
  the retiring document's every section is accounted for in writing (#278, note 60
  D-60.7…D-60.11, tier M, 2026-09-13).** `app/views/export_report.py` is the only
  production consumer of `content.build_report`, so note 57 D-57.1's deletion of
  `app/views/` retires the summary report — and with it the **only** statement of
  the axis system and sign conventions either front end makes, and the **only**
  FAR 23 Subpart C coverage matrix. Four assets moved into the surviving document
  first, as numbered front matter after the introduction: axes and sign
  conventions, the governing safety-factor table, the FAR coverage matrix and the
  bundle manifest.
- **The front-matter slot is data, so the section plan stays derived.**
  `oracle_content.FRONT_SECTIONS` is now a table of `(key, title)` rather than one
  literal, and the analysis body renumbers itself around it because numbering is a
  function of position (G-OR-2 survives the re-cut on the OR-16 pattern, note 60
  D-60.9). Cross-references to front matter go through `front_ref`, like every
  other reference in the document. Appendices were the rejected alternative: an
  appendix is appended, never inserted, and a section stating the frame every later
  number is in belongs before what it governs.
- **One builder, two documents.** `sloads/report/front_sections.py` owns the four
  sections and takes its heading as an argument; `content.py` calls it rather than
  keeping a second copy, so the two reports print the same table rows until the
  first is deleted (practice 3 — a merge implemented as a copy is the drift the
  convergence exists to end). `conventions_tex.py` and `coverage.py` keep a
  consumer that outlives the page, asserted rather than assumed.
- **The document states what travels with it.** `OracleDocument` now carries its
  own `data/` file list, so the bundle-manifest section is an ordinary built
  section listing the control files and the data files together — a list computed
  only at packaging time would leave a section INCLUDED in the plan and absent in
  the render. #245's *Data reference* table is that section now, widened to the
  whole package; `MANIFEST.txt` still states the same set with hashes, from the
  same two owners.
- **Nothing leaves unaccounted.** Every key of `content.SECTIONS` is declared in
  `front_sections.SUMMARY_DISPOSITION` with the front section it merged into, its
  successor, or the reason it retires — a table `tests/test_front_sections.py`
  reads, so a section cannot be dropped silently (note 60 gates 11 and 12). The
  audit is what turned up the cases that needed a decision rather than a
  presumption: the approved-corrections table, which describes the tool and
  reaches a reader through the methods statement in every shipped file's header;
  and the balanced free-free cases, whose honesty statement is written in band on
  the deck that carries each case.
- **`build_report` is untouched and still builds.** It is deleted with the page at
  #270, after the merge and never before it (D-60.11) — the document's content
  reaches its new home before its old home is removed.
