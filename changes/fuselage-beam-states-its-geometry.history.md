## Step 158 — The fuselage beam states its geometry, and the body LRA is read (tier L, 2026-09-07)

**Objective.** Answer the owner's review of sections 4 and 5 against the built
document: give the fuselage beam table the coordinates it was missing, draw the body
in side view, and settle where the body beam actually runs — which turned out to be
the question the review was really asking.

**Agreed first.** With the owner in session on 2026-09-07, in four questions asked one
at a time, each answered before the next was framed. The fourth was asked only because
the third's answer failed a test the moment it was implemented.

**Deliverables.**
- `models/inputs.py`, `mass_distribution.py`, `migrations.py` — schema **v62**:
  `FuselageStation.y`/`.z`, blank-deriving from the item database's weight-weighted
  centroid; identity hop.
- `derived_geometry.py` — `FuselageLra` and `fuselage_lra`, the single owner of where
  the body beam runs, with the out-of-body guard.
- `export/lra_model.py` — the body chain asks that owner instead of the centre line.
- `examples/*.json` — six corrected `ref_waterline` values.
- `report/oracle_sections.py` — 4.1's side view; Table 21's Y and Z; the case
  reference as the key of the pull-up, fitting and tail tables; Appendix C's X/Y/Z;
  section 5's input-data subsection, reordered state table, hinge-moment statement and
  applied-load Appendix D.

**Key decisions.**
- **Where the mass is and where the beam runs are two statements, and both are
  kept.** The first framing of the schema change treated `FuselageStation.z` and
  `ref_waterline` as two spellings of one quantity, which is the duplication class this
  milestone has removed twice. The owner corrected it: `ref_waterline` was always meant
  to be the fuselage LRA. They are different quantities about the same station, and on
  `ga6_normal` they differ by up to 50 in.
- **`ref_waterline` was read by nothing, and the field registry said so.** *"Reserved:
  stored and round-tripped, but consumed by no current calculation … any value, 0
  included, is currently equivalent (#94, C210-34 owner ruling)."* The component deck
  put the beam at `z = 0`; the airplane model ran it on the section-centre line. That
  sentence is now false and the row says what replaced it.
- **The fixture data was placeholder, and the test that proved it was a solve.** Wiring
  the entered values up dropped the ATR-42's body beam 77 in below its body and made
  the LRA deck singular. Measured across the fleet: four of six waterlines lay outside
  their own fuselage, the Dash-8's by 47 in, with three unrelated airplanes entering the
  same round `100.0`. The owner ruled the values corrected rather than the wiring
  softened, so each is set to its own body's centre line — which reproduces the previous
  node positions to 0.03 in, the rounding of an entered number, so no deck geometry
  moves and no load changes.
- **The correction carries a stated risk.** Entering a value that equals the derived
  one, and having it then report `assumed=False`, is exactly the mechanism that produced
  the fin-root defect (note 19 §10.2's "pin today's assumed value as a stated one"). It
  was flagged before the values were written, and the mitigation is the guard rather
  than the note: `fuselage_lra` states a waterline that lies outside its own body, so
  the specific failure these six values had cannot recur unnoticed. Entering measured
  LRA waterlines remains open work.
- **A guard that breaks a shipped input field is the wrong guard.** The first
  implementation raised on an out-of-body waterline. That would have made
  `ref_waterline` untypable on any project whose body is entered, so it states instead
  — the same ruling the fin root's disagreement note carries, and for the same reason.
- **Absence is stated where a reader will look for it.** The owner asked why there is no
  hinge moment. It is not a missing input: the hinge line is known, and the elevator
  load is modelled smeared into the surface. 5.5 now says so and names the two inputs
  that would change it, and the two empty columns are removed — a column of dashes is
  not a statement.
- **Appendix D is a deck, so it carries only what a deck needs.** Applied load, at its
  point, in airplane axes. No `Fx` column: this analysis models no chordwise tail force
  and no empennage dihedral, so the other components are absent by construction rather
  than zero by measurement (OR-61), and the appendix states both absences.

**Test.** Three gates on the new owner in `test_derived_geometry.py` — the entered
waterline leads and is straight, a blank one derives station by station from the centre
line, neither gives a zero that announces itself; a waterline outside its own body says
so while still being used; and no shipped fixture carries one. Four new gates in
`test_oracle_report_fuselage.py` (the side view draws mass, beam and both load paths;
the beam table states both waterlines and which the analysis reads; the fuselage tables
key on the case reference; Appendix C places every station) and four in
`test_oracle_report_tail.py` (the input-data subsection draws the surface with its axis
and states it station by station; the hinge-moment absence is stated and its columns
removed; Appendix D places every load on the airplane in airplane axes). The schema hop
is guarded as an identity, and the Imperial baseline moves on `sbeam/lra_model` alone,
on the five fixtures with a fuselage outline and on none without one.
