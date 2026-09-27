- **The weight estimate's engine count is `engine_count`, so `engines` names only the engine list (#276, tier S, 2026-09-27).**
  `WeightEstimationInput.engines`, WTESTIMA's `NOENGS`, shared its name with
  `Project.engines`, and the units guard walks the schema by bare field name,
  so it reached the list first and never asked whether the count was
  classified. The guard ran with that one name pinned as a known exception;
  the rename empties it, and one field name now means one kind of thing
  everywhere. The schema goes to v70 with no hop, since v69 was never released
  (#310); the field-registry path is `weight.estimation.engine_count`, and the
  five examples are re-stamped with the same counts, so no load, deck or
  digest moves.
