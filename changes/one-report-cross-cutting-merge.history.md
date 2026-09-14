- **The two reports become one (#278, note 60 D-60.7…D-60.11, tier M, 2026-09-13)** —
  Note 57's convergence retired `app/views/` and, through it, a 2,632-line document
  it never named: `app/views/export_report.py` was the only production consumer of
  `content.build_report`, so deleting the page would have deleted the summary report
  and taken with it the only statement of the airplane reference frame either front
  end makes, the only FAR 23 Subpart C coverage matrix, and the document-level
  governing safety-factor table. Note 60 named the deletion and conditioned it on a
  merge; this step is the merge. Four cross-cutting sections now print as the oracle
  report's front matter after the introduction, through a declared
  `FRONT_SECTIONS` table that leaves the analysis section set derived from the
  workflow and lets the body renumber itself around them. They are built once, by
  `sloads/report/front_sections.py`, and printed by both documents while both exist,
  because a merge implemented as a copy is the drift the convergence was called for.
  The fourth asset — the bundle manifest — closed a gap of its own: the document now
  carries its own list of the files that travel with it, control files and `data/`
  alike, computed with the document rather than at packaging time. What is *not*
  merged is declared key by key in an audit table a guard test reads, so no section
  of the retiring document leaves without a successor or a stated reason; that audit
  is what forced decisions on the approved-corrections table and on the balanced
  free-free cases rather than letting either be lost between two changes that each
  looked complete. `build_report` itself is untouched: it is deleted with the page
  at #270, after its content has reached its new home.
