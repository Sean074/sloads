- **Four process-doc corrections from the 2026-09-04 project review (issue
  #189, tier S, 2026-09-08).** (1) `00_backlog.md`'s head no longer keeps a
  prose list of live design notes — the guarded `docs/00_INDEX.md` is the
  index; the list had already drifted once (closed 09 listed, 45–49 omitted).
  (2) `DEVELOPMENT_PROCESS.md` §5's "`30_future/` holds only `00_backlog.md`,
  the live notes, and nothing else" now names what the directory actually
  holds: the plan files and `02_parked.md` too. (3) `GIT_FLOW_GUIDE.docx` is
  demoted from `10_standard/` to
  `docs/40_history/49_git_flow_guide_to_2026-08-16.docx` — it advertised the
  squash flow the process retired at the 0.7.2 cut, and a binary doc's currency
  rests on a prose promise no test can check (precedent CR-D-4); its
  `WORKFLOW_COMMANDS.txt` INDEX row's stale "merge-commit PR" phrase is swept
  to rebase-merged in the same pass. (4) `00_program_overview.md`'s "`io.py` is
  the only place dataclasses meet JSON/CSV" is scoped to calc dataclasses —
  `sloads/export/` writes the deliverable files and always has. Guarded
  (`test_doc_currency.py::test_the_standard_tree_holds_only_guardable_text_formats`):
  a non-`.md`/`.txt` file in `docs/10_standard/` fails CI. Proven both ways: a
  scratch `.docx` dropped into the tree fails the guard.
