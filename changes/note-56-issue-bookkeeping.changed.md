- **The backlog is re-scoped onto the package note 56 left behind (tier S, 2026-09-12).**
  Seven surviving rows carried note 56 as a *forecast*; each now states what
  landed. #241's `AppliedLoad` fix has an address (`report/applied.py`) and the
  six `*_applied_loads.csv` files are the only applied-load CSVs left; #242
  narrows to the report's own files, with the control-surface `Fz` question
  surviving as rows *inside* the h-tail and fin files rather than as a file;
  #209's case index landed at `report/tables.py`, so its decision now touches
  three owners (`load_cases_to_rows`, `load_cases_csv`, the index itself);
  #191 loses the `sbeam_bridge.py` half and re-measures its candidates
  (`balance.py` 2,842, `report/content.py` 2,625, the new `report/applied.py`
  1,561); #254 and #245 restate their narrowings as landed. **#17's forecast was
  wrong in one half and says so**: `_export_sbeam` was not deleted with the
  per-component targets — it lost its branches and stands at 53, off the list —
  and `_manifest_rows` measures 131, not the 155 the row carried.

- **Three findings owed since note 56 are filed, and band B4 re-opens for one of
  them (tier S, 2026-09-12).** #274: the oracle report's balanced-cases
  paragraph and the Balanced Cases page still call the assembled model the
  primary deliverable and the per-component decks its analysis views, and the
  wing-root note attributes the `lra-sob` reporting node to the deleted wing
  stick deck — three false statements in shipped content, which the ordering
  rules put above every [V] item, so 0.8.3 does not cut over them. #275: the LRA
  mesh guarantees no fuselage owned point at the spar carry-through, and
  Appendix G measures the cost (fuselage shear 82–197 % of the channel's own
  peak; a ~107,000 lb reaction one bay from where it acts on
  `concept_regional_jet`). #276: `WeightEstimationInput.engines` is a count
  where `Project.engines` is a list, invisible to the units walker's totality
  gate and pinned meanwhile in `_KNOWN_AMBIGUOUS`.
