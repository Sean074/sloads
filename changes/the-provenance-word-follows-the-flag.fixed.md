- **Planform provenance was fixed text, able to say "entered" over a derived
  planform (#235, 2026-09-08 review R11, tier S, 2026-09-08).**
  The reviewed reports got it wrong in both directions: GA-6's §2.1 prose said
  "generated" over entered polylines (that leg fell with #234, which replaced
  the parametric cross-check condition in §2.1), and the reviewed Baron report
  derived both tail planforms yet said "entered" in every caption — polylines
  the Baron example has since gained with #160's real tail geometry, so the
  fixture no longer reproduces it. The structural defect remained: the words
  lived in independent fixed strings ("as entered … entered vertices" in the
  planform and LRA figure captions, the "cannot be drawn as entered" refusals,
  the pressure-locator opening, the §2.1 DERIVED prose) with only the
  "Planform basis" table row actually consulting the supplied-flag. One
  wording owner now (`oracle_sections._PROVENANCE_WORD`, keyed on
  `_planform_assumed`, which asks `resolve_tail_planform`): the basis rows,
  both caption families, the refusals and the prose all build their word from
  it, so a caption cannot claim a provenance the flag does not. Register rule
  added (ORACLE_REPORT.md §2.1). Guard: both directions — GA-6 (supplied)
  must say "entered" with no DERIVED claim, and the Baron stripped of its
  tail surfaces (the reviewed state) must say DERIVED in the basis rows,
  absent-figure reasons and prose with no "entered" claim; proven to bite on
  a re-fixed basis row.
