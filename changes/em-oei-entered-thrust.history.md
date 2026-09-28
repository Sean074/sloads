- **A condition that prescribes an engine's thrust replaces the entered one: the 23.371(b)/25.371 gyroscopic case's engine carries ENGLOADS's max-continuous thrust alone and a one-engine-out case ONENGOUT's pair alone (#313, design note 66, tier M, 2026-09-27)** —
  An entered `thrust_lb` (#10) is applied at every engine's hub in every
  flight case, and the engine-mount builder keeps it unscaled on purpose; the
  gyroscopic increment then added ENGLOADS's thrust at the same hub, and the
  one-engine-out case added ONENGOUT's live-thrust / windmill-drag pair beside
  the entered thrust on both engines. On an `atr42_100` copy with 4,000 lb
  entered per engine the left engine's gyroscopic case carried 14,865 lb
  (10,865 + 4,000), and the one-engine-out case gave the failed engine 4,000
  lb of thrust beside its 13,004 lb windmill drag and the live engine 5,921 lb
  (1,921 + 4,000). `hub_thrust_set` now tags each hub force with its engine
  (`carrier = engine-<i>`, the D-66.6 rule, so an entered thrust also routes
  to its own engine's LRA member) and leaves out the engines a condition names
  as `replaced`, saying so in band: a gyroscopic case's parent is assembled
  without its own engine's entered thrust, the other engines keep theirs, a
  torque case keeps all, and an engine-out case — ONENGOUT models a twin, so
  its pair is the whole thrust state — carries none. The "Applied engine
  thrust" row and `is_powered` read the entered thrust only, as they did; the
  engine-mount docstring's claim that ENGLOADS's thrust made a case powered is
  corrected (the family's gate exemption is `is_engine_mount`). Latent: no
  shipped fixture enters thrust, so no delivered load, card or case moves.
  Gate G-12 in `tests/test_hub_thrust.py` — no hub in any case of a powered
  build carries two thrusts; the gyroscopic engine's thrust is the unpowered
  build's; the engine-out pair is the unpowered build's.
