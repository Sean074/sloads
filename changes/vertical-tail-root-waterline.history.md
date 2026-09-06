## Step 156 — One vertical tail, one size, one place (#160, tier L, 2026-09-06)

**Objective.** Close #160 — *"the Baron's fin is entered symmetric and zero-based"* —
and the defect class behind it: the vertical tail's size and its placement were each
stated twice, in two places, with nothing checking the copies agree.

**Agreed first.** With the owner in session on 2026-09-06, in four steps, after the
investigation quantified each half. `CLAUDE.md` rule 1's chat route (working alone);
the numbers that justified each step are in the deliverables below and pinned in CI.

**Deliverables.**
- `tail_geometry.fin_root_waterline` — the entered `vtail` polyline becomes the first
  branch of the resolution order, ahead of the explicit scalar, and a disagreeing pair
  is resolved to the polyline with `FinRoot.note` naming the value not used.
  `tail_geometry.entered_fin_root` is the one reader of the polyline's datum.
- `examples/` — five fins re-entered as single surfaces on absolute waterlines;
  `ga6_normal`'s `vtail_root_waterline_z` pin cleared.
- `tests/test_tail_geometry.py` — `test_no_fixture_places_its_fin_twice` and
  `test_no_fixture_doubles_its_fin`, the two drift guards; `_FIN_ROOT` re-pinned.
- `CONVENTIONS.md` §7 (SSOT row + two §7.2 rules), `theory_sources.md` (the lateral
  balance's measured lever-arm sensitivity).

**Key decisions.**
- **The entered polyline leads the explicit scalar.** Every other branch reconstructs
  the fin's placement from something else — a scalar typed on another page, the T-tail
  relation, the body's top at the fin station. The polyline states it. The two are
  therefore **not** note 36 OV-1's blank-derives / typed-overrides pair but two
  spellings of one measurement, which is why precedence alone is not the whole answer
  and the disagreement is stated as well as resolved.
- **Stated in band, not refused.** `validate_tail_planform` raises on the same
  duplication class one level down (area against span), and the difference is
  deliberate: that conflict has no rule to pick between its two representations, this
  one does. Raising here would also make `vtail_root_waterline_z` un-typable on any
  project with an entered fin, which is a shipped input field — a guard that breaks an
  input field is the wrong guard.
- **`ga6_normal`'s 78.5 was scaffolding, not a measurement.** Note 19 §10.2 step (i)
  entered it on 2026-08-17 as "a zero-movement change that pins today's assumed value
  as a stated one", so that step (ii)'s body outline would land with an attributable
  digest wave. Step (ii) shipped in the same pass and was shadowed by step (i) from the
  moment it landed, because `explicit` led the order. Three answers for one waterline
  — 78.5 pinned, 98.44 from the outline entered to supersede it, 111.5 from the fin's
  own edges — and the one that won was the one nobody measured, reported
  `assumed=False`. **The lesson is the ordering, not the number:** scaffolding entered
  at the top of a resolution order is indistinguishable from data.
- **The roll arm is where it lands, and the load is the control.** `z_fin − z_cg` goes
  11.89 → 44.89 in on ga6 and the four lateral roll accelerations move 5–12×
  (`SUDDEN RUDDER` −6.888 → −85.952 deg/s²); yaw moves ~2 % through `Ixz`. `L_v` and
  `n_y` are **bit-identical on all five lateral fixtures**, 0.0000 % on every case,
  which is what makes this a lever arm moving rather than the aerodynamics. No
  Appendix A oracle moves: the lateral cases have never had a printed one and are
  pinned by measurement in both directions.
- **`SurfaceInput.symmetric` is load-bearing on a fin, in two places.**
  `wing_geometry.surface_properties` reads it for the area/span/AR bookkeeping, and
  `airloads.resolve_aero_surfaces` reads it as the predicate for *"is this a lifting
  surface AIRLOADS analyses"*. The five mis-flagged fins were therefore reported at
  twice their own area and span **and** shipped a Schrenk symmetric spanwise lift
  distribution for a vertical tail, on the doubled aspect ratio, under `FAR 23.301`.
  The second consequence was not in #160 as filed and was found by asking why
  `csv/airloads` moved in the digest wave — the drift check earning its keep.
- **The guards check effects, not flags.** `test_no_fixture_doubles_its_fin` asserts
  WINGGEOM's reported fin area and span against the entered `vtail_area_sqft` /
  `vtail_span_in` and asserts the fin is absent from `resolve_aero_surfaces`, rather
  than asserting `symmetric is False`. It is then the same gate the day the same wrong
  number is reached by another route.
- **One convention for a fin polyline's second coordinate:** a waterline in the
  airplane datum, which is how `ga6_normal` always entered its own. The five that were
  root-relative are rebased onto their own resolved roots, rounded to the 0.1 in an
  entered waterline is measured to (≤ 0.05 in of lever arm, ~0.1 % of `ṗ` on three
  fixtures, nothing on the RJ).

**Test.** Five new or re-aimed gates plus the pinned baselines. The two drift guards
run per fixture; `_FIN_ROOT` re-pins every fin as `basis="geometry"`, `assumed=False`;
the three derivation-branch tests now strip the polyline first, since a fixture that
has one no longer reaches a derivation branch at all — which is the ordering working.
`test_the_vertical_tail_is_drawn_in_its_own_frame_and_never_mirrored` sets the
`symmetric` flag itself instead of borrowing `baron_58`'s (a guard whose premise is a
bug elsewhere dies when the bug is fixed) and checks the plotted waterlines against the
fin's own root rather than against zero — `y >= 0` is true of a fin lying on the datum,
which was the defect. The frozen Imperial baseline moves on six channel families, each
mapped to the edit that caused it before it was regenerated: `airloads` and
`wing_geometry` on the five flag fixes, `balance` on the roll arm, `tail_span` /
`vtail_span_cards` / `lra_model` / `balanced_deck` on the fin waterlines, and
`htail_span_cards` on the two T-tails whose horizontal surface sits on the fin tip.
`concept_heavy`, which enters no `vtail` surface, does not move at all.
