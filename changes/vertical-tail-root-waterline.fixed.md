- **The vertical tail is placed by its own geometry, and placed once (#160,
  tier L, 2026-09-06).** `tail_geometry.fin_root_waterline` asks the entered
  `vtail` polyline first: it states the fin's placement directly, in the
  waterline datum the rest of the geometry is entered in, where every branch
  below it reconstructs that placement from something else. The explicit
  `vtail_root_waterline_z` is not a typed override of it (note 36 OV-1) but a
  second spelling of one measurement, so a disagreement is resolved to the
  polyline and `FinRoot.note` names the value it did not use — stated in band
  rather than refused, because the scalar is a shipped input field and has to
  stay typable. Guard: no shipped project may carry a disagreeing pair.

- **`ga6_normal`'s fin was modelled 33 in low for 20 days (#160, tier L,
  2026-09-06).** It carried `vtail_root_waterline_z = 78.5` — the airplane's
  *wing* root waterline, entered 2026-08-17 as note 19 §10.2 step (i)'s
  "zero-movement change that pins today's assumed value as a stated one" so that
  step (ii)'s body outline would have an attributable digest wave. Step (ii)
  shipped in the same pass and could never take effect: `explicit` led the
  resolution order, so the pin shadowed both the outline it was scaffolding for
  (98.44) and the fin's own entered edges (111.5), while reporting itself
  `assumed=False`. The pin is cleared. The fin's roll arm `z_fin − z_cg` goes
  11.89 → 44.89 in and the four lateral cases' roll accelerations move 5–12×
  (`SUDDEN RUDDER` −6.888 → −85.952 deg/s²), yaw ~2 % through `Ixz`. The fin
  load and `n_y` are bit-identical on every fixture, which is the check that a
  lever arm moved and not the aerodynamics. No Appendix A oracle moves — the
  lateral cases have no printed oracle and are pinned by measurement.

- **Five fins were entered symmetric, and were each reported at twice their own
  size (#160, tier L, 2026-09-06).** `baron_58`, `cessna_210`, `atr42_100`,
  `dhc8_dash8` and `concept_regional_jet` set `symmetric: true` on a vertical
  tail. `wing_geometry.surface_properties` reads that flag for the area/span/AR
  bookkeeping, so each fin was reported at `2 × area` and `2 × span` against its
  own entered scalars (`baron_58` 48.58 ft², span 132.0, AR 2.49 against an
  entered 24.30, 66.0, 1.26) — and `airloads.resolve_aero_surfaces` reads the
  same flag as *the* predicate for "is this a lifting surface AIRLOADS
  analyses", so every one of the five also shipped a **Schrenk symmetric
  spanwise lift distribution for its fin**, computed on the doubled aspect ratio
  and printed under `FAR 23.301`. Both are gone. The guard checks the reported
  geometry against the entered scalars rather than the flag, so it is the same
  gate the day someone reaches the same wrong number another way.

- **The same five fins were entered root-relative (#160, tier L, 2026-09-06).**
  Their polylines were based at waterline 0 while the load path placed each fin
  on the body, so §2.1 drew every one on the airplane centreline — 110 in low on
  `baron_58`. Each is rebased onto its own resolved root (`baron_58` 110.0
  entered; `cessna_210` 100.2, `atr42_100` 191.2 and `dhc8_dash8` 203.5 from
  their own fuselage outlines; the RJ's 87.0 from the T-tail relation, exact).
  One convention now: **a fin polyline's second coordinate is a waterline in the
  airplane datum**, which is how `ga6_normal` always entered its own.

- **The surface has one name: the vertical tail (owner ruling, tier S,
  2026-09-06).** "v-tail" where space requires, `vtail` as the code token —
  matching the regulation, the schema, the component key and what the reports
  already print. Stated in `CONVENTIONS.md` §7.2, because today the *data* is
  spelled `vtail_*` while the owners that place and load it are spelled `fin_*`,
  which is one thing under two names inside one call chain. The identifier sweep
  is filed for the 0.8.2 cut (it reaches frozen `modules/tail_span.py`); new code
  takes the agreed name from the first line.
