- **The shell is slimmed of what only the retired front-end called, and the
  statements that outlived it are re-cut (note 57 §8, tier S, 2026-09-13).**
  The end-of-milestone sweep #270 deferred: what the deletion left unreachable,
  measured by reachability from the production trees rather than by reading.
  Five public names had no caller outside the tests that pinned them.
  `app_shell/limit_csv.py` loses `wing_limit_csv` / `body_limit_csv` /
  `tail_limit_csv` — the per-page CSV download builders, whose callers were
  `app/views/` and whose channel is now the issue package's `data/` (#245); the
  `*_limit_rows` half they wrapped feeds the analysis pages' on-screen station
  tables and stays, with the units contract asserted on the rows rather than on
  the file. `app_shell/optional_slice.py` goes whole: its rule was *an Apply may
  not create an `Optional` slice out of nothing*, and the surviving GUI has no
  Apply step — it has #143's named add/remove gestures, which is the same rule
  in its stronger form. `CONVENTIONS.md` §7's row for it is re-pointed at those
  gestures rather than deleted, because the convention outlived its
  Apply-button owner. Nothing else in the shell was orphaned, which is what
  OG-B was for.

- **The release-state sentence stops naming a GUI that does not exist (tier S,
  2026-09-13).** `app_shell.components.RELEASE_STATE` — carried verbatim by
  `README.md`, `CAPABILITIES.md` and the About panel — said *"the oracle GUI
  production-ready; additional features and the full sloads GUI in beta"*. Half
  of that named the front-end #270 deleted, and "oracle" no longer distinguishes
  one GUI from another. It now reads *"Core analysis developed per FAR 23 LOADS
  and the GUI production-ready; concept-mode features in beta"*: the same mixed
  claim, about the software that exists. Its own docstring says to update it at
  a cut and not between them, and this is the cut. R-57.5's rename of the
  package and console script stays deferred and is now the only thing that
  claim's wording waits on.

- **Every statement in the code that still described two front-ends is re-cut
  (tier S, 2026-09-13).** Roughly forty sites across `sloads/`, `app_shell/` and
  `oracle_app/` said *"both GUIs"*, *"either GUI"* or *"the main GUI's <page>"*
  in the present tense — the standing justification for a single owner, written
  when there were two consumers to keep in step. The rule survives the second
  consumer; the sentence has to say so. Where the reason was historical it is
  put in the past tense and kept, because *why* an owner is where it is remains
  the useful half. Three were wrong rather than merely dated: `sloads/io.py`
  told a reader to run `streamlit run app/Home.py`; the Tail Loads page's
  caption sent them to a **Tail Span Loads** page that no longer exists, for the
  spanwise station table that is in the report's *Spanwise loads* subsections
  and the export decks; and `README.md`'s layout tree still drew `app/Home.py`
  and `app/views/` (and, from further back, `sloads/report.py` and
  `sloads/models.py` as modules).
