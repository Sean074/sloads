- **The engine's thrust line is an input (design note 53, tier L, 2026-09-07).**
  `EngineInput.thrust_line_aft` and `thrust_line_fwd` state the line as two
  points in the airplane frame, with `(0, 0, 0)` meaning not entered — the
  sentinel `LandingGearInput.attach` already uses. The forward point is forward
  **because it is entered as such**, never inferred from the smaller fuselage
  station, so a pusher installation is expressible with no special case
  anywhere. Both or neither: one point alone states no direction and is refused
  by name, as are two points that coincide. An engine that states no line is resolved about the
  airplane's forward axis and marked **ASSUMED** on every deliverable that prints
  it. Entered on the Engine Mount page, drawn on the Configuration & Layout
  three-view and on the oracle report's three views of the installation.

- **The propeller's rotation direction is an input, per engine
  (`EngineInput.prop_direction`).** Clockwise seen from the pilot's seat by
  default — what every published torque already assumed — so no existing project
  moves by a pound-foot. A counter-clockwise engine reverses the sign of every
  torque it delivers to the airframe, in every deliverable that carries one. Per
  engine rather than per airplane, because a counter-rotating twin is the
  configuration the field exists for. It reuses `RotorDirection`, which the
  schema has carried on `Rotor` since the turbine rotor model and which nothing
  read until now.

- **`derived_geometry.engine_thrust_segments`**, the one producer of an engine's
  thrust line as something to draw, read by both three-view consumers so they
  cannot disagree about where a line runs or how long an assumed one is. The
  length of an assumed line is a fraction of the body, not of the plot, so the
  same engine draws the same line in the report and in the GUI.
