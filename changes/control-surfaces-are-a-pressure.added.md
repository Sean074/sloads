- **The oracle report gains sections 7, 8 and 9 — aileron, flap and tab (note 44 §19
  OR-147, tier L, 2026-09-07).** Each states the critical condition, the load it
  produces and the pressure to apply, over the surface Section 2 already draws. They
  add **no appendix, no station table and no CSV**: the A–E pattern exists because a
  wing, a body and a tail deliver a distributed load a structures model integrates
  station by station, and a control surface delivers a pressure the reader applies.
  **G-OR-95** holds the appendix set at A–E, so "no appendix" is a checked property of
  the document rather than an intention.

- **Two figures per section: how to apply the load, and where (OR-153).** The chordwise
  application diagram draws the profile against the fraction of the surface's local
  chord, with the hinge line and the point the resultant acts at marked; it is built
  from the module's own profile, so it exists on every project that runs the module.
  The planform locator shades the surface on its host, drawn from Section 2's entered
  outlines through the same owner §2.1 uses. Where an outline is not entered the
  locator states the absence — measured, that is the flap and the elevator on three of
  the four examples — and says in the same breath that the loads and pressures are
  unaffected, because they are computed from the entered areas and not from a shape.

- **The spanwise distribution is stated, where the oracle leaves it ambiguous
  (OR-151).** The pressure is uniform along the span and the chordwise profile is in
  fractions of the *local* surface chord. That is not an assumption added by the
  document: each of the three equations divides a load by an **area**, so the pressure
  is uniform over that area by construction. **G-OR-97** holds the printed profile to
  it — mean pressure times the entered area is the printed load, on every case of every
  shipped example — so a future edit cannot move the profile or the area without the
  other.

- **One sign convention, in the same words in all three (OR-150).** Pressure is
  positive acting normal to the control surface's own plane, in the sense a
  trailing-edge-down deflection produces; a positive pressure gives a nose-down moment
  about the hinge line and a negative pressure, which a trailing-edge-up throw produces,
  gives a trailing-edge-down moment about it. The airplane axis that normal is belongs
  to the host — `z` for a wing- or horizontal-tail-borne surface, `y` for a rudder — and
  is named rather than left to the reader.
