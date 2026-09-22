- **Every engine-mount condition states its own point of application (#210, tier S, 2026-09-22).**
  The 23.361(b)(1) sudden-stoppage torque, the 23.371(b) gyroscopic condition and
  the FAR 25 supplemental 25.371 case carried no `loc_*` values while the
  conditions beside them for the same engine did, and the render boundary filled
  the gap from the condition each followed (note 44 OR-193) -- the proper repair,
  the producer stating the point, waited on the 0.8.2 freeze of `modules/engine.py`.
  The producer states it now: one owner, `engine._applied_at`, emits the three
  values on all nine conditions at the engine's combined engine-plus-propeller CG,
  the point the six torque and side-load cases always stated; `render._running_locations`
  is the identity it was filed to become: a condition's own point or a blank,
  never a neighbour's -- the one-engine-out fin and rudder cases, which state
  no single point, stay blank as they always printed. A pure couple and a three-point condition each state one
  point, so each says what it means: the stoppage note records that a free couple
  about the thrust line takes the combined CG for indexing only; the two
  gyroscopic notes record that the stated point is where the vertical load acts,
  the couples are free, and the thrust acts on the thrust line at the propeller
  hub, offset by the CG-to-hub distance -- the moment a reader summing about the
  mount from the index would otherwise lose. Which beam-model grid takes the
  couple stays with #286. Gates: G-OR-138 rewritten as the producer's property
  (`tests/test_oracle_report_vn.py::test_every_engine_condition_states_its_own_point`,
  every condition at its engine's combined CG, no two engines sharing one, a
  pointless condition left blank rather than filled) plus
  `::test_the_pointless_conditions_say_what_their_point_means`. No load and no
  point moved on any fixture; the one digest channel that moved is the engine
  text report (`txt/engine`, ATR 42), which now prints the three point rows and
  the note on each formerly pointless condition, and it is regenerated.
