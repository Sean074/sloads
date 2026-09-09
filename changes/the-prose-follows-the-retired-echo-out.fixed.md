- **The report GUI stated the retired deselection behavior, and two provenance
  sentences pointed at the retired input echo (#237, 2026-09-08 review G2+G3,
  tier S, 2026-09-08).** The report page's selection caption promised the
  safeguard the document deliberately does not provide — "a deselected section
  is still printed, stating that it was excluded" — where the agreed, guarded
  rule (ORACLE_REPORT.md §3.1) is silent omission with renumbering; it now
  states that rule and its rationale. Two pointers survived OR-194's retirement
  of the input echo: the printed fingerprint caption ("the input echo remains
  the definitive record", `oracle_latex.py`) and the provenance banner's
  mismatch message ("read the input echo to see what moved", `fingerprint.py`);
  both now name the packaged `project.json`, OR-194's machine-readable record.
  Two docstring-only mentions swept by hand (`models/report.py`,
  `oracle_sections.py`). Guard: G-OR-74 gained a retired-claims scan ("input
  echo" banned in both rendered documents and the GUI literal sweep), the sweep
  now reads `oracle_app/report.py` (the milestone's new page — not under the
  OR-13 freeze, unlike the rest of the tree), the mismatch message is asserted
  at its owner, and a quoted witness proves the new pattern bites.
