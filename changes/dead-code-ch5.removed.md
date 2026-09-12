- **Six dead public names leave `sloads/`, and a gate keeps the seventh from
  arriving (#16 / CH-5, tier S, 2026-09-11).** `balanced_deck.write_balanced_deck`,
  `mass_cards.write_conm2_fragment`, `mass_cards.write_mass_check_deck` and
  `mass_distribution.all_checks` — the four the 2026-08-16 scope review named,
  re-verified on this tree as definition-plus-`__all__` and nothing else — are
  deleted. Under rule 4 the sweep took the same class across the tree and found
  two more with no consumer *anywhere*: `report.tables.write_safety_factors_csv`,
  a fifth instance of the identical `write_X(project, path)`-wrapping-`X(project)`
  shape, orphaned when note 56 D-56.1 moved the report tables out of the export
  bridge, and `field_registry.paths_for_page`. New guard
  `tests/test_no_orphan_writers.py` fails when any `write_*` in `sloads/` has no
  caller in the calc package, either shell, the scripts, the CLI entry points or
  the suite — proven against a reintroduced orphan before it was removed.

  **The "demote the ~12 no-consumer public names" half does not ship, and the
  number is why.** Re-measured on this tree, `sloads/` carries **200** public
  top-level names with no consumer outside their own module, not twelve — and
  the review's own two examples have both evaporated: `gear_loads.contact_patch`
  gained an external consumer since 2026-08-16, and `sbeam_bridge.subcase_map`
  sits in the file note 56 D-56.1 dissolves, so demoting it is churn on a
  deletion. The 200 are dominated by module result dataclasses (`DesignSpeeds`,
  `MassCheck`, `Joint`) and single-source constant families whose members are
  public by declaration — the `MASS_EID_*` id bands, `WING_BAND_*`, and the
  encoded-but-dormant commuter tier that `GUI_design.md` documents as dormant
  and a blind sweep would have deleted. Demoting those would fight rule 3, not
  serve it. The mechanical part of the row shipped with a gate; the judgment
  part is closed **decided, not done**, with the measurement above as the record.
