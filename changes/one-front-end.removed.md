- **The second front-end retires: 22 pages, 8,461 lines, and the document that
  shipped from one of them (#270, design note 57 D-57.1 + D-57.6 as amended by
  note 60 D-60.11, tier L, 2026-09-13).** `app/Home.py` and its 21 `app/views/`
  pages are deleted, and `oracle_app/` is *the* sloads GUI. The convergence's
  closing step: note 57 measured two front-ends over one calc package as a
  structural drift class rather than a capability, and D-57.8 required the
  survivor complete before anything was removed — which #265–#269 and #278 did,
  so this step only removes.

  **Deleted with the page set:** `content.build_report` and its nine section
  builders (`content.py` 2,639 → 653 lines); `latex.render_document` /
  `render_report` and the title page and running heads with them, leaving
  `latex.py` the section/table/figure emitters `oracle_latex.py` builds on;
  `sloads/report/bundle.py`, the Export zip's member list, whose only consumer
  was the page; and `sloads/export/workbook.py` with its `openpyxl` dependency
  (the owner having ruled the `.xlsx` unused, and #245's `data/` being the
  single tabular channel — no replacement is built). Five pages retired without
  port, each citing its successor: `dashboard` (the shell's sidebar carries the
  project), `results_review` (`oracle_app/results.py`), `export_report` (the CLI
  and the Report page), `tail_span_loads` (the report's tail-span appendix) and
  `balanced_cases` (the balanced deck and `balanced_case_rows`).

- **The page set is still derived, and now states its exceptions (D-57.1).**
  `workflow.gui_pages()` is the owner: the fourteen derived analysis pages
  (`oracle_steps()` — *runs a `.BAS` program, or produces a slice such a step
  requires*) plus `workflow.NON_STEP_PAGES`, three pages that are not steps of
  the analysis and each declare why — the Project JSON Editor, the Aircraft
  Comparison and the Report. Gate G2 survives the re-cut on the OR-16 pattern:
  adding a `bas` to a step still adds a page with no GUI edit, and what is
  listed is only the set no analysis can derive. `STEPS` loses the six GUI-only
  rows that were page declarations and nothing else, and `PHASES` drops from
  seven to four — `Start`, `Load-case plotting` and `Export` held those rows
  and would otherwise be phases no step can be in, which a new guard refuses.
  `tail_span_loads` and `balanced_cases` stay: they run registered calc modules
  and always were analysis rather than presentation.

- **Two claims about the retired front-end turned out to be wrong, and both had
  no test.** `cli.py --report` was a second production consumer of
  `content.build_report` — note 60 and #278's backlog row both called the Export
  page the only one — so the flag broke silently when the builder went and the
  suite stayed green. It now renders the surviving document (the document alone;
  the issue package is the Report page's) and `tests/test_cli.py` holds it to
  the reachability rule the export menu has always had. Widening that guard
  found the CLI's one error contract covered everything the *analysis* could
  refuse and not the thing every route does first: `io.load_project` sat outside
  every route's `try`, so a file that was not JSON came out as a traceback on all
  four. `cli._load` is now the single entry and `cli.main` the single handler
  (rule 4 — the fix sweeps the class it was found in).

- **`data/case_index.csv` gains the assembled column it shipped without.** The
  package's case index was built from the applied sets and the module results
  and not from the assembled cases, so its `LOAD/SUBCASE (assembled)` column was
  empty on every row: a reader holding the LRA beam model — the primary
  deliverable — could not trace a `SUBCASE` back through the one tabular channel
  there is. It shipped that way from #245 and was invisible while the summary
  report printed a complete index beside it. Found by re-pointing that report's
  index-agreement test at the artifact that ships.
