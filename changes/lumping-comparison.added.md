- **The oracle report states what the beam grids cost the distribution (note 56
  D-56.10, tier L, 2026-09-12).** New **Appendix G**: one table of the widest
  gap in each internal-load channel of each member, over every case, and four
  figures — wing, fuselage, horizontal tail, fin — plotting that gap along the
  span for the case that bends the member hardest. It is the counterpart to
  D-56.9, which sums the applied set onto the beam's grids: the set's
  **resultant** is preserved exactly and gated, and this is where the
  **distribution** it moves is stated instead of left to be discovered.
- **New owner `sloads/report/lumping.py`.** The internal load at a cut is the
  static resultant of everything outboard of it, transferred to the cut through
  the same LM-1 owner the aggregation uses — one rule for shear, bending and
  torsion on all four members — evaluated twice about the same cuts, once from
  the load stations and once from the delivered set. **No solver is in the
  loop**, so the figure is a discretization comparison and not an idealisation
  one, and it is reproducible in CI. Cross-checked against
  `sob_internal_loads`, the single-cut instance it generalises, at the wing root
  of every case of four fixtures.
- **There is no acceptance tolerance, and the appendix says so.** The size of
  the difference is a function of the grid counts the project sets, so a fixed
  limit would fail a coarse mesh behaving exactly as specified.
