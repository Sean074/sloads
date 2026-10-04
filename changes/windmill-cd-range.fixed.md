- **An entered windmill drag coefficient must be positive, and one above the Glauert bound is warned with both numbers; every entered engine magnitude is refused by name unless positive (#343, tier S, 2026-10-04).**
  A negative `windmill_drag_cd` delivered a forward thrust at the failed
  engine's hub in the balanced one-engine-out cases, and zero delivered no
  drag; either closed as cleanly as a right value. Both are now refused by
  name before any case is assembled, and warned on the engine page
  (`windmill_drag_cd_range`); a value above the bound the manual says the drag
  cannot exceed (0.502) is delivered as entered and warned. The same class
  swept through ENGLOADS: `takeoff_hp`, `max_cont_hp`, `max_engine_torque`,
  `cruise_torque`, `stop_time_s` and an entered `max_accel_torque` are refused
  unless positive (a zero stoppage time divided by zero), and an entered
  `prop_inertia` unless zero or positive. No shipped fixture or delivered load
  moves.
