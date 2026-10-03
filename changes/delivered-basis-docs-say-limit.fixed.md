- **The capability summary and the report standard state the delivered basis the code ships: LIMIT, with the factor stated and applied nowhere (#342, tier S, 2026-10-03).**
  Three current-truth documents still carried the contract note 49 OR-116
  reversed — `CAPABILITIES.md` ("Everything deliverable is ULTIMATE … the
  safety factor is applied once at the render/export boundary", plus the five
  per-component decks note 56 deleted and the `ULTIMATE twin` OR-81 retired),
  `SUMMARY_REPORT.md` §5's exclusion row ("The deliverable is ultimate
  throughout") with its §4.6 and SI-marker siblings, and
  `ch09_balanced_airplane.md`'s units line ("applied once at the export
  boundary") — so the first document a new reader opens told an analyst not
  to apply the factor the deck did not apply. All three now state the shipped
  contract, and the class is structural (rule 3):
  `tests/test_doc_currency.py` scans every current-truth doc,
  `CAPABILITIES.md` included, for the retired-contract phrase class — which
  found the `ch09` instance the hand sweep had missed, on its first run.
  `90_record/` stays out of scope, where the sentences state what was true on
  a date. Found by the 0.8.8 pre-release review.
