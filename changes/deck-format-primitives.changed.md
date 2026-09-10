- **The deck-writing primitives get their own module (CH-4, #15, tier S, 2026-09-09).**
  `sloads/export/deck_format.py` is now the single owner of *how a bulk-data card is
  written* — the NASTRAN number format (`fmt`), the vector-card triple with its dust
  snapping (`fmt3`, `snap_zero`, `CARD_TOL`), the `SF` spelling (`sf_str`), the 72-column
  `$` comment wrap (`comment`), the `$`-block stamp (`stamped`) and the placeholder
  `MAT1`/`PBAR` section properties a determinate stick model needs to be solvable. Five
  sibling writers — `mass_cards`, `balanced_deck`, `lra_model`, `lra_import`, `roundtrip`
  — reached across the package for these through `sbeam_bridge`'s underscore; a private
  imported from another module is not private, it is an undeclared API whose every rename
  is a silent breakage. The names are public at their new owner and the cross-imports are
  gone. Pure move: no deck byte, CSV cell or printed figure changes, and the oracle,
  closure and frozen-Imperial-digest suites are unmoved. `CONVENTIONS.md` §7's
  platform-stable-bytes row and `PROJECT_GUIDE.md` §4 name the new owner.
  `test_platform_stability.py`'s emitted-value sweep now patches the formatter at **every**
  binding rather than at one module's — with the primitive outside `sbeam_bridge`, the old
  single patch would have shrunk a 159,407-value population sweep to one file's cards
  without failing.
