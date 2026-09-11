- **The deliverable tables that are not decks move to `report/` (note 56 D-56.1,
  tier M, 2026-09-10).** The case index, the governing safety-factor table, the
  gear interface report and the export-scope filter they share are now
  `sloads/report/tables.py` (409 lines). None of them emits bulk data or knows
  what a GRID is — they are documents, and `report/` is where documents are
  assembled, which is why `report/content.py` and the oracle sections were
  already reaching back across the package to import them.

  Every row, column, header and byte is unchanged; the frozen Imperial digest is
  the proof. `sbeam_bridge.py` drops 3,013 → **2,639** lines.

  **The export package no longer re-exports them**, and a guard asserts it does
  not: a re-export would leave one name at two addresses, which is the condition
  D-56.1 exists to end. `sloads.export.__init__`'s docstring says where they went
  instead. Consumers re-pointed: `report/content.py`, `cli.py`, the Export page
  and the Landing-loads page.

  Two allowlists keyed on the old path were corrected — `test_envelope_owner`'s
  `_ALLOWED` (the reason belongs to the table, not to the bridge) and
  `test_ultimate_contract`'s `_ULT_CHANNEL`, which reads download-call text and
  would have passed silently on a page whose call had moved to a new alias. That
  is the second text guard this note has caught keyed to a name it was about to
  lose, after G-OR-71 in the previous slice.
