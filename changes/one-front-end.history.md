## Step — One front-end (#270, design note 57 D-57.1 + D-57.6, tier L, 2026-09-13)

**Objective.** End the two-front-end drift class by deleting the front-end the
mission bar does not need, after — and only after — everything worth keeping had
been ported into the one that survives. Note 57's §1.4/§1.5 priced the
alternative: hardening `app/views/` through the 0.9.0 band buys maintenance on a
surface whose every capability duplicates a surviving owner, while the drift
class is structural for as long as two front-ends exist. D-57.8's rule governed
the sequence and was honoured to the letter — #265 through #269 built the
survivor's editor, field tiers, plots, fleet page and seed button, and #278
merged the summary report's cross-cutting sections into the surviving document
— so this step removes and re-cuts, and adds no capability.

**Deliverables.** `app/` deleted: `Home.py` and 21 `views/*.py`, 8,461 lines.
With it, the artifacts whose only consumer it was: `content.build_report` and
its nine section builders, `latex.render_document`/`render_report` and the
document furniture (title page, running heads), `report/bundle.py`,
`export/workbook.py` and the `openpyxl` dependency. `content.py` falls from
2,639 lines to 653 — the content model (`Section`, `Table`, `Figure`,
`PlotData`, `Units`, `ComponentLoads`) plus the three plot-data producers the
document and the GUI both draw from — and `latex.py` becomes the emitters
`oracle_latex.py` assembles a document from. `workflow.py` gains `GuiPage`,
`NON_STEP_PAGES` and `gui_pages()`; `Oracle.py` builds its navigation from that
declaration and names no page set of its own. `validation.PAGE_EXPORT` becomes
`PAGE_REPORT` and its five checks re-point at the page that writes the
deliverable. `cli.py --report` renders the surviving document, `cli._load` gives
every route the one error contract, and `report/methods.py`'s channel sentence
names the surviving human channels.

**Test.** Note 57 §4's eight gates, each asserted rather than asserted-about.
**No load moves** (gate 1): the Appendix A oracles, twin closure suites, report
baselines and every delivered CSV are untouched — this step edits no calc
module. **A project the retired GUI saved opens here** (gate 2, OG-13 widened):
`test_oracle_gui.py` reverses the G6 round-trip, driving every bundled example's
full unreduced project through all fourteen pages, because the question a user
has is not whether two peers can read each other's files but whether the file
they already saved still opens. **`_GUI_TREES` covers the survivor whole** (5)
and **exactly one `st.set_page_config`** (6) hold unchanged over one tree. **The
no-edit journey** (7): `test_gui_journey.py` is re-aimed at the surviving
renderer, and its `KNOWN_OPEN` list is **empty and asserted empty** — it carried
five #148 diffs that the `app/views/` freeze forbade fixing, all of them
properties of a page that rebuilds its slice from its own widgets, which is what
a hand-written view does and a generic renderer over the field registry does
not. **No retired page is reachable** (8): `gui_pages()`, the navigation and the
workflow guards agree, and ruff/mypy leave no import edge. Six test files were
deleted with the pages they drove and fourteen re-aimed; three guards that read
`app/views/*.py` sources were re-cut to sweep the surviving display trees rather
than name files, because a surface that is not on a list is a surface the guard
does not reach.

**Key decisions.**

- **The page set stays derived and states its exceptions.** D-57.1 widened the
  rule from `oracle_steps()` to a stated set; the implementation makes the
  stated half a declaration with a reason per row (`NON_STEP_PAGES`) rather than
  three hand-appended blocks in the entry point. Gate G2's claim — *there is no
  page list* — then covers the whole page set instead of the derived part of it.
- **`PHASES` shrinks to four.** `Start`, `Load-case plotting` and `Export` held
  the six GUI-only steps and nothing else. Keeping them would leave three phases
  no step can ever be in, which is drift with a name; what they described did
  not retire with them — the project is carried by the shell, the figures are
  drawn on the pages that produce them (#267), and the deliverables leave through
  the CLI and the Report page — but none of those is a step of the analysis,
  which is what the tuple partitions.
- **Two analysis steps keep no page.** `tail_span_loads` and `balanced_cases`
  run registered calc modules whose deliverables are the report's tail-span
  appendix and the balanced deck. `STEPS` is what the suite does, not what the
  GUI shows, and saying so in the module docstring was cheaper than folding two
  real steps into a mapping built for contributors.
- **The audit outlives its subject.** `front_sections.SUMMARY_DISPOSITION` was
  written at #278 saying it would retire with `content.py`. It does not:
  `content.SECTIONS` moved beside it as `RETIRED_SUMMARY_SECTIONS`, because an
  accounting whose subject has been deleted accounts for nothing, and note 60's
  gate 12 would have stopped being enforced at exactly the commit that made it
  matter.
- **Three rules that lived in a page moved to an owner, rather than dying with
  it.** M4-17c's zero-waterline refusal is `validation.landing_cg_below_axle`,
  a pure predicate the GUI renders on the page its tag names. G-53.7's
  "clockwise seen from the pilot's seat" is the `prop_direction` field's own
  registry row, so it reaches the GUI, the data dictionary and the report's
  field provenance together. #124's horsepower precedence is guarded by a sweep
  asserting no display module reads the fields at all. Each was a caption in a
  deleted file; each is now the one place the rule is stated.
- **R-57.5's rename and the Phase G plan's roll to history stay deferred.**
  Note 57 §6/§8 puts both at the 0.8.4 cut rather than in a row, and the branch
  taken keeps the `oracle_app` name and the `sloads-oracle` entry point. What
  this step takes from that list is the lint-path half the issue names: `app/`
  leaves the ruff scope in CI, `solo_close.sh`, `CLAUDE.md` and `README.md`, and
  `smoke_test.sh` boots one front-end because there is one.
