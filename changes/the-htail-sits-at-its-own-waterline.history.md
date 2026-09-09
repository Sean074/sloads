- **The h-tail sits at its own waterline (#236, 2026-09-08 review R12, tier M,
  2026-09-08)** — `LayoutInput.h_tail_z`, until now a three-view sketch offset,
  became a real analysis input: the new single owner
  `tail_geometry.h_tail_waterline` (the fin root's twin — fin tip on a T-tail,
  mid-fin on a defaulted cruciform, `root_waterline_z + h_tail_z` where entered,
  the wing-root plane marked ASSUMED with a loud note otherwise) places the
  h-tail's load stations through `tail_span`, so §5.1's station table,
  Appendix D and the exported GRIDs moved together from the GA-6's wing-root
  placeholder (WL 78.5, printed as an airplane coordinate — 32.5 in below the
  real surface for any reader importing the points) to the entered WL 111. Both
  report tables state the waterline's provenance from the same owner, the
  reviewed filed scope (a disclosure sentence) having been widened to this by
  the owner's option-B ruling with an OR-15 admission over
  `sloads/modules/tail_span.py`. No delivered load moved — the surface loads in
  fz only, so z places points, not forces. `ga6_normal` and `baron_58` enter
  their offsets; the blank fixtures print the ASSUMED disclosure. Guards: the
  owner's branches, a three-view-vs-load-path drift guard, and a two-direction
  report guard on the entered and blanked GA-6.
