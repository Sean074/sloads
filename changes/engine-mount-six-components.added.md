- **Section 10, Engine Mount Loads, in the oracle report (note 44 §20, tier L,
  2026-09-07).** Two subsections. **10.1 Input Data** states the entered engine
  and propeller data one column per engine, the three stations in play — the
  beam model's mount node, its hub node and the combined engine + propeller CG
  the loads act at — the thrust axis as direction cosines, the case list by
  regulation, and the sign convention. **10.2 Critical Cases** states all six
  airplane-axis components of the load each condition applies to the airframe,
  one row per case per engine, and beside it the torque about the engine's own
  thrust line and the thrust along it — the two scalars the six were resolved
  from, so a reader can repeat the resolution rather than take it. Every case is
  LIMIT with its factor stated and applied nowhere; the section adds no appendix,
  because a mount takes a point load and not a distribution.

- **Three views of the engine installation, drawing whatever airframe the project
  enters (note 44 §20 OR-168/OR-169).** Side, front and plan, each with the
  fuselage from its section table, the wing and the empennage through the owners
  Section 2 and the three-view sketch already use, and every engine's mount node,
  hub node, application point and thrust line marked on it. A project that enters
  no outline still gets all three: the engines are the subject and the airframe
  is context. `derived_geometry.fuselage_outline` is the new single owner of the
  drawn body — the section table had been in the schema since the schema had a
  body, and nothing drew it.

- **`export/coordinates.engine_thrust_axis` and `engine_applied_load`**, the one
  owner of an engine's thrust line and of the airplane-axis resolution of the
  torque and thrust that act about it. `CONVENTIONS.md` §1 already makes this
  module the single edit point for every axis resolution in the suite; the report
  asks it rather than restating its signs, the same shape OR-146 gave the fin's
  torsion.
