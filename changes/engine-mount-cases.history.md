## Step — The deck carries the engine: every 23.361/23.371 mount condition that pairs with a flight state is an assembled free-free case at the engine's own nodes, and every balanced case states its own safety factor (#286, design note 66 D-66.1…D-66.9, tier L, 2026-09-26)

**Objective.** Close #286: ENGLOADS computed every engine-mount condition and
the LRA deck had a mount and a hub node per engine since note 24 R-9, yet no
engine condition reached the deck — a nacelle, mount or attachment sized from
it saw no engine case, and the deck said nothing about the absence. The owner
agreed design note 66 the same day (Q1–Q7 as recommended).

**Deliverables.** A new balanced family, `balance/engine_cases.py`, appended
after the ground families: per engine, never mirrored, ids ENGLOADS's own
`EM-nn`. Each case is an assembled flight case in SELECT's delivered PHAA block
(PHAA's point for 23.361(a)(1)/(a)(2), `BAL C` for (a)(3) and FAR
25.361(a)(3)(i)/(ii), `MAN A` for 23.371(b)/25.371) scaled by one constant to
the load factor ENGLOADS states for the engine, plus the engine's own torque,
gyroscopic couples and thrust through `coordinates.engine_applied_load`, at the
mount and hub nodes of that engine. ENGLOADS's vertical is never re-applied —
the engine's mass is in the parent's inertia at that `n`. The torque is trimmed
by an equal and opposite `aileron-trim` couple (note 21 P-9); the gyro couples
and thrust are closed by the rigid-body relief. 23.363 and 23.361(b)(1) are
mount-local and named in the deck's not-assembled block with their reason. The
LRA model gains a member per engine and routes an EM load by its `carrier`.
Every balanced case now stamps its own safety factor from the governing table
(`safety_factors.stamp`), so the deck's basis sentence states the case's factor
rather than the field's default — 1.5 everywhere today. Each gyroscopic sign
combination is now a condition with its own `EM` id (`engine.split_gyro`,
`mount_conditions`; the render-time `a`–`d` suffix retired), and 25.371's A2
vertical is read wherever the 2.5 g one was (`load_keys.FZ_VERTICAL_A2`).
One Imperial digest wave, 26 channels: the balanced and LRA decks, the balance module's CSV and text and the case index move on the four engine fixtures (the EM subcases, the not-assembled engine lines); the engine CSV, text and applied-load file move on the two turboprops (the gyro split's ids; the RJ's 25.371 vertical, 0 before). `concept_heavy` has no engine and did not move.

**Test.** `tests/test_engine_mount_cases.py`: the deck carries exactly the
ruled set per fixture (G-66.2); every case's SF is the table's (G-66.1); each
EM case flies at ENGLOADS's `n` with no re-applied vertical, and the itemised
engine weighs ENGLOADS's `PPWT` to the pound where the database itemises it
(G-66.3); the increment is `engine_applied_load` of ENGLOADS's scalars and
lands on its own engine's nodes (G-66.4); every case closes in six DOF (G-66.5);
the torque nets no roll and no EM case is handed (G-66.7); the RJ's 25.371
rows carry their vertical (G-66.12). The round-trip solve gate passes on every
engine fixture with the new subcases (G-66.6).

**Key decisions.** (1) The regional jet's database lumps both engines as one
3,400 lb centreline row against ENGLOADS's 2 × 1,550 lb: its EM cases are
correct for the airplane as entered, and the discrepancy is recorded in note
66 §10, not fixed. (2) The family is exempt from the flight trim gate — the
case it scales is gated as itself — and is judged by G-66.x. (3) The gyro split
renumbers the turboprops' later EM ids (the ATR's right engine moves from
EM-07… to EM-10…).
