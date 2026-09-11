- **The deliverable tables that are not decks move to `report/` (note 56 D-56.1,
  tier M, 2026-09-10)** — The second slice of note 56, and the safe half of
  D-56.1's three-way split. The case index, the governing safety-factor table,
  the gear interface report and the export-scope filter had lived in
  `export/sbeam_bridge.py` since the first consumer happened to be there, and
  stayed through five milestones; none of them emits a card. The move was
  chosen to go first because gate 1 makes it the thing that stops the later
  deletions taking the oracle report with them — `report/content.py`,
  `report/oracle_sections.py` and `report/methods.py` reach into the bridge at
  ten sites, so deleting the per-component decks (D-56.2) before rehoming what
  they sit beside would have removed the one actively-used deliverable along
  with four unused ones. A dependency scan settled the order: this group's
  closure needs **nothing** from the code that stays and **nothing** reaches
  back into it, so it moves whole, while the applied-load family does not (see
  below). 409 lines out; `sbeam_bridge.py` 3,013 → 2,639. The export package
  stops re-exporting the moved names rather than keeping a shim, and a guard
  asserts their absence — under ruling 1 nothing downstream reproduces, so a
  compatibility alias would buy nothing and would leave one name at two
  addresses, which is the condition D-56.1 exists to end. Deliverables are
  byte-identical across the move (gate 8, gate 1). **Two allowlists keyed on the
  old path had to be corrected, and one of them mattered:**
  `test_ultimate_contract`'s `_ULT_CHANNEL` matches the *call text* at each GUI
  download site to decide whether a CSV is ultimate by construction, so a page
  whose call had moved to a new module alias would have gone on passing while
  the guard no longer recognised it. That is the second text guard this note has
  caught keyed to a name it was about to lose, after G-OR-71 in the first slice,
  and it confirms the standing caution recorded there. **What it did not move,
  and why:** `sob_internal_loads` and `CENTERLINE_CLAMP_NOTE` are report-only in
  their consumers but are still referenced by deck writers that D-56.2 deletes,
  so moving them now would have required either a reversed `export → report`
  import or a deferred one to break the cycle; both are worse than waiting one
  step. The applied-load family stayed for a substantive reason rather than a
  mechanical one: `AppliedLoad.gid` is a **per-component deck's** GID, and
  G-OR-90 — the gate asserting every card the deck writes at a GID is the
  appendix's row at that GID — reads `tail_span_force_moment_cards`, which
  D-56.2 deletes on the grounds that it has no production consumer. True, but it
  is the authority for that gate, so deleting it removes the gate rather than a
  deck. What the appendix's `gid` column means once the per-component decks are
  gone was a decision note 56 had not recorded; raising it produced **rulings
  10–12 and D-56.9** in the same session, and the note is amended with them here
  — the LRA grids are where the loads and moments are *calculated*, so the
  appendix row and the card are one object at one point again and G-OR-90 keeps
  its row-for-card form against a different authority. Two of the note's own
  statements are reversed by that amendment and marked in place rather than
  edited away: §5's acceptance of a coarser wing distribution (which held only
  while the grids were somewhere to hang a check) and §7's "no schema change"
  (settable per-component grid counts are persisted input, so `SCHEMA_VERSION`
  bumps 65 → 66 with a migration hop). Neither affects this slice's code; both
  had to be recorded before the next one starts.
