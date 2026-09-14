- **The 0.8.4 closure review: the JSON editor works again after a load, and every
  delivered file states the moment senses the right way round (tier S,
  2026-09-14).** The review of the converged front-end before the cut found four
  defects the green gate could not see, three of them in shipped content or the
  page the convergence depends on.

- **The Project JSON Editor was empty after the first project load.**
  `app_shell/project_editor.py` stamped its text key at import — `widget_key`
  evaluated once per process, at generation 0 — and re-stamped it per render,
  so after `adopt()` bumped the generation the seed was written to
  `g0::_project_editor_text` while the widget read `g1::g0::…`; Apply reported
  *Invalid JSON: Expecting value: line 1 column 1* and Reload wrote the same
  dead key. The escape hatch note 57 D-57.3 sequenced first was unusable on any
  loaded project, and no test rendered it. The key is now stamped at the use
  site; `widget_key` replaces a stale stamp instead of nesting one (rule 4 — the
  class, not the instance); `tests/test_widget_freshness.py` refuses a
  module-level `widget_key(...)` in any GUI source; and the new
  `tests/test_project_editor.py` renders the page at generations 0, 1 and 3 and
  round-trips an edit through Apply.

- **The AXES stanza on every delivered file had +Mx and +Mz backwards.**
  `export/coordinates.AXES_NOTES` said *positive Mx rolls right wing down …
  positive Mz yaws nose right*; for the frame the same stanza declares (x aft,
  y starboard, z up) the right-hand rule gives starboard wing **up** and nose to
  **port** — which is what `CONVENTIONS.md` §7, the report's own *Axes and sign
  conventions* section and `bending_moment_vector` all say, so the built
  `report.tex` contradicted itself between its methods stamp and its front
  matter, and the wrong sentence landed in band on all six applied CSVs, the
  case index, the gear and safety-factor tables, every module CSV, `METHODS.txt`
  and both decks. The senses now live once as `coordinates.MOMENT_SENSES`, the
  stamp and `conventions_tex` both read the sentence built from them, and
  `tests/test_delivered_frame_statement.py` derives each sense from the axes by
  the cross product rather than asserting the words are present.

- **The six applied CSV headers pointed at a file nothing writes.** The `Case ID`
  header sent the reader to `<project>_case_index.csv`, the retired export
  bundle's name; the index that ships is the package's `data/case_index.csv` —
  the #245 defect class a second time, three weeks after #245. The name is
  `report/tables.CASE_INDEX_FILENAME`, read by the package writer and the
  header alike, and `tests/test_package_data.py` asserts the header names a file
  the package carries. `CONVENTIONS.md` and `PROGRAM_SPEC.md` follow.

- **The weight seed button then offered to delete what it had seeded.** #269's
  seed extended the rows in the button body, which cannot move the retained
  row counter, so the next render warned *the row count says 24, but Items
  still holds 41* and rendered **Delete the last 17 row(s)** — the rows just
  added, under a contract that says *never deletes*. The seed is an `on_click`
  callback now, moving the counter the way row deletion always has
  (`tests/test_weight_seed.py`).

- **Swept with them.** `cli.py` still tracebacked on a project file whose top
  level is a JSON list (`AttributeError` out of the schema gate); the gate now
  refuses it as the error contract's `ValueError`, on every route.
  `GUI_USER_GUIDE.md` §6 said the *Export phase applies the ×1.5 factor* and
  shipped ultimate CSVs — contradicting §1 of the same document and note 49 —
  and §6/§8 still routed users through a Start phase, six phases and an editor
  that loads files; all re-cut to the converged GUI. The backlog rows that
  ruling 4 of the 2026-09-11 re-cut said close at #270 (#148, #247–#252, #259)
  are removed with their `app/views/` bodies, #29 is re-scoped to the surviving
  GUI and inherits L-8d's mutation half, and the two `40_history/` references
  follow note 61.
