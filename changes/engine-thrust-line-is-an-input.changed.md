- **Section 10 resolves each engine's loads about its entered thrust line, not
  about a line derived from the engine CG and the hub (design note 53 D-53.3,
  superseding note 44 OR-161).** The derived axis was a line between two *mass*
  stations and inherited every error in either: measured **14.0°** off the
  airplane axis on `ga6_normal` and **71.6°** — very nearly straight up — on
  `cessna_210`, whose engine CG waterline is a filed defect. On `ga6_normal` the
  section now prints `Mx +737.34 / Mz 0` for 23.361(a)(1) and `+740.44 / 0` for
  (a)(2), where it printed `+715.32 / −178.83` and `+718.34 / −179.58`. The
  **magnitude is unchanged** — `|M|` is 737.3383 and 740.4429 either way — so
  this does not change how hard the mount is worked; it corrects which axis the
  work is about. Section 10.1 states the rotation per engine and states why the
  gyroscopic condition is exempt from it.

- **Project schema v62 → v63**, additive and an identity hop: `None` on both
  thrust-line points is exactly the v62 state, since the schema carried no thrust
  line at all, and clockwise is what every published torque already assumed.
