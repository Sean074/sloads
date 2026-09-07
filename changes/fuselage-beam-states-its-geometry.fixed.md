- **The fuselage LRA waterline is read (tier L, 2026-09-07).**
  `FuselageMassInput.ref_waterline` has been documented since it was added as the
  waterline the body's mass distribution is carried along, and nothing read it:
  the component deck put the body beam at `z = 0` ("the component in isolation")
  and the airplane LRA model ran it on the fuselage section-centre line. On
  `ga6_normal` that is 23.5 in from where the project file says the beam is, and
  the field registry recorded the state as *"reserved … any value, 0 included, is
  currently equivalent"*. `derived_geometry.fuselage_lra` is now the single owner
  — entered waterline, else the section-centre line, else a loud zero — and
  `export/lra_model` asks it. The third instance of one defect class this
  milestone: an entered value with the right intent, shadowed by a derived
  stand-in, with nothing saying so.

- **Four of six fixtures placed their body beam outside their own fuselage
  (tier L, 2026-09-07).** Found by wiring the waterline up: `atr42_100` 35 in
  below its floor, `dhc8_dash8` 47 in, `cessna_210` 10, `ga6_normal` 5 — and
  three unrelated airplanes all entering the same round `100.0`, which is what a
  placeholder looks like. Using them as entered made the ATR-42's LRA deck
  singular. Every value is corrected to its own body's centre line, and
  `fuselage_lra` states a waterline that lies outside the body it belongs to
  rather than trusting it, so the class cannot recur silently. The corrected
  values reproduce the previous node positions to the rounding of an entered
  number (0.03 in), so no deck geometry moves and no load changes.
