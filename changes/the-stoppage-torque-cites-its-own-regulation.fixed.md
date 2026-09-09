- **The sudden-stoppage torque was cited under the gyroscopic regulation
  (tier S, 2026-09-08).** Five prose sites attributed the engine sudden-stoppage
  torque condition to 23.371(c) — but 14 CFR 23.371 is the gyroscopic and
  aerodynamic engine-mount section and has no such paragraph; sudden stoppage
  is 23.361(b)(1), as the emitting module (`modules/engine.py`), the case-title
  map (`report/oracle_sections.py`) and `safety_factors.py` all already state.
  Corrected in the `_running_locations` docstring (`report/render.py`), the
  G-OR-138 guard's docstring (`tests/test_oracle_report_vn.py`), backlog row 38
  (the #210 producer repair) and the two OR-193 change fragments awaiting the
  0.8.2 cut. The neighbouring "gyroscopic condition of 23.371(b)" citation was
  checked against its owner and is correct. No behavior change; every code
  `far_reference` was already right.
