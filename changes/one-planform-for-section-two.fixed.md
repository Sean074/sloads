- **Section 2.1's wing table printed a different MAC/XLEMAC pair than every
  %MAC in the document, under 2.2's claim that they were one (#234, 2026-09-08
  review R10, tier S, 2026-09-08).**
  Table 1 was the configuration module's *parametric cross-check* — WINGGEOM's
  integration of a two-point trapezoid regenerated from the layout scalars —
  while the spanwise distributions and the %MAC reference integrate the stored
  surface polylines; on the GA-6's cranked wing the two are 6.9 in of XLEMAC
  apart (56.73 vs 63.62), and 2.2's note attributed its pair to "the wing
  planform stated in 2.1", so a reader converting %MAC with Table 1's numbers
  landed on different stations than the document's with no warning. 2.1 now
  prints the stored planform's own integration through a new owner accessor,
  `derived_geometry.planform_geometry_condition` (resolving the same surface
  `mac_reference` reads, honouring gate DG-3's producer/owner shape), with a
  note naming the polylines it integrated; the parametric condition remains
  only as the fallback when no
  stored wing integrates — the case where 2.2 has no planform pair to
  attribute either. The typed wing area S and the `envelope.xlemac`/`mac`
  pair stay legitimate overrides and are named as such where printed; the
  integrated areas leave the table so STRSPEED's governing S is stated once.
  Register rule added (ORACLE_REPORT.md §2.1). Guard: 2.1's MAC and XLE(MAC)
  rows must equal the %MAC reference's formatted pair — proven distinct from
  the trapezoid's — and 2.2's note must print that pair and its provenance.
