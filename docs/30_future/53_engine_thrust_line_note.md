# The engine's thrust line is an input (design note 53)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-07 (owner, in session) — no code yet.** Drafted from the
owner's ruling: *"The thrust line I want to change. The user should input it and
the geometry section of the GUI should support this. Two points would be
sufficient, the user should also define the rotation direction. If the user does
not define, assume it is in the x direction."* — and from the six answers that
followed (A: OR-15 granted for the torque sign; B: blank means x; C: agree
positive prop rotation; D: agree per engine, reusing the enum; E: agree the
gyroscopic exemption; Q4: the balanced cases are filed, not fixed).

**Tier L** — additive schema change, a **sign change in the frozen solver**, GUI,
report, and two new single-source owners.

**This note carries two of the owner's OR-15 admissions**, both granted in
session on 2026-09-07, both narrow, both recorded here, cited in the commit and
lapsing with the step:

1. **`sloads/modules/engine.py`** — for **the torque sign and nothing else**:
   not a refactor, not a rename, not formatting in the same file.
   `torque_sense` and `_floored_torque` are the whole of it.
2. **`oracle_app/form.py`** — for **two `MEMBER_LABELS` rows and nothing else**.
   Asked for only after it was clear there was no way round it: a composite
   field in the oracle input set must have its members named or the GUI renders
   them as "1, 2", and that table is the only place the naming lives. Additive;
   no existing field's behaviour changes.

Both files' hashes are re-pinned in `tests/test_frozen_set.py` with the scope of
the admission recorded beside them, which is the authority trail that guard asks
for.


## 1. What the code does today, and what is missing

Section 10 shipped on 2026-09-07 (note 44 §20, Step 162) resolving each engine's
torque and thrust onto the airplane axes. It needs a thrust line to resolve them
about, and the schema has never carried one, so **OR-161 derived it** as the
direction from the engine CG to the propeller hub — the only two stations the
schema does carry. That derivation shipped with a caveat printed beside it and a
backlog entry filed the same day, and the measurements are why:

| Example | Derived axis | Angle off `x` |
|---|---|---|
| `ga6_normal` | `(−0.9701, 0, +0.2425)` | **14.0°** nose-up |
| `cessna_210` | `(−0.3162, 0, +0.9487)` | **71.6°** — very nearly straight up |
| `baron_58` (both) | `(−1, 0, 0)` | 0° |
| `concept_regional_jet` (both) | `(−1, 0, 0)` ASSUMED | — (hub entered at the engine CG) |

**The line from an engine's CG to its hub is not the shaft axis**, and nothing
made it one. It is the line between a *mass* station and a *mass* station, and it
inherits every error in either: the C210's 71.6° is that airplane's own entered
CG waterline — a filed defect (backlog, 2026-09-07) — turned into an axis and
then into a moment component. On `ga6_normal`, whose stations are now correct
against Appendix A p227, the 14° still put `Mz = 178.8 ft-lb` into section 10.2
for an airplane that has no such moment.

Two further things are missing, and the rotation direction is the sharper one:

- **The propeller's rotation direction is not an input**, and the torque sign
  assumes one. `modules/engine.py` publishes `mx_mount_torque = −Q` for every
  engine, which is correct for a propeller turning clockwise from the pilot's
  seat and backwards for one turning the other way. A counter-rotating twin —
  ordinary in this class of airplane — cannot be stated at all.
- **`Rotor.direction` exists and is read by nothing.** `RotorDirection`
  (`CLOCKWISE`/`COUNTERCLOCKWISE`, *"viewed from rear of engine looking
  forward"*) has been on `Rotor` since the turbine rotor model, carried and never
  consumed.

## 2. Governing basis

No new physics and no new regulation: 14 CFR 23.361/23.363/23.371 are unchanged,
and every load magnitude this note touches is the module's own. What changes is
the **axis** those loads are resolved about and the **sign** one of them carries,
both of which are `CONVENTIONS.md` §1 questions. The sign derivation is note 44
§20 OR-162's, unchanged and restated here only where the direction enters it:
a propeller turning clockwise from the seat is driven by `+Q` from the engine,
returns `−Q` to the engine, is held by `+Q` by the mount, and the engine
therefore delivers `−Q` to the airframe. Reverse the rotation and every step
reverses with it.

## 3. Decisions

| # | Decision | Amends |
|---|---|---|
| **D-53.1** | **The thrust line is an input, entered as two points** *(owner)*. `EngineInput.thrust_line_aft` and `thrust_line_fwd`, both `Vec3` in the airplane frame, inches, with **`(0, 0, 0)` meaning not entered** — the sentinel `LandingGearInput.attach` already uses, registered in `SENTINEL_DEFAULTS` beside it. *(Corrected in implementation, 2026-09-07: the draft said `Optional[Vec3]`. The oracle GUI renders every field generically and a `None` triple came back `(0, 0, 0)` from an untouched render — the #121/#145 load-bearing-blank class reaching a field on its first day, caught by the page's own round-trip gates. Following the schema's existing convention fixes it without touching frozen `oracle_app/form.py`, and a point at the nose datum on the centreline at waterline zero is not a thrust line anybody means.)* Two points rather than a vector because a station is what an analyst measures off a drawing and a direction cosine is not, and because the pair is what the three-view can draw. **Both or neither**: one point entered alone is a half-entered line and is **refused by name** — the C210-21 load-bearing-blank pattern — never silently half-used, and never mixed with a derived second point. | new schema |
| **D-53.2** | **Forward is stated, never inferred** *(owner: agreed)*. `thrust_line_fwd` is the forward point, by name. Nothing infers it from the smaller fuselage station. **There is no tractor assumption anywhere in this**, and the section says so: the torque's sense is about which way the shaft turns *as the pilot sees it*, not about which end of the engine the propeller is on, so a pusher installation resolves identically and needs nothing special. The only thing "forward" fixes is which end of the entered pair the sign convention is read from. | note 44 OR-162 (restated, not changed) |
| **D-53.3** | **Blank means the airplane's `x` axis, and the CG→hub derivation is removed** *(owner: "if the user does not define assume it is in the x direction"; confirmed on the numbers)*. **This supersedes note 44 OR-161.** Two grades of provenance, not three: **entered**, or **ASSUMED** as airplane `−x` (forward) and marked as such on every deliverable that prints it. The derived middle grade goes because §1's measurements show it is not an approximation of the shaft axis but a different quantity that occasionally resembles one. The assumed line passes through `prop_cg`, falling back to `engine_cg`: immaterial to a couple, and the location that matters the day a thrust *force* follows it (D-53.8). **This moves numbers already shipped, and the move was checked through the owner before agreeing it** (2026-09-07): on `ga6_normal`, 23.361(a)(1) goes from `Mx +715.32 / Mz −178.83` to `Mx +737.34 / Mz 0`, and 23.361(a)(2) from `Mx +718.34 / Mz −179.58` to `Mx +740.44 / Mz 0` — `Mx == −torque` as an **exact** float equality, because with the axis at `(−1, 0, 0)` the resolution is a sign flip and nothing else. **The magnitude never moves**: `|M|` is `737.3383` and `740.4429` before and after, so the 14° axis was only spreading one torque across two axes. This decision does not change how hard the mount is worked; it corrects which axis the work is about. | **supersedes note 44 OR-161** |
| **D-53.4** | **The propeller's rotation direction is an input, per engine, defaulting clockwise** *(owner: agreed)*. `EngineInput.prop_direction: RotorDirection = CLOCKWISE`, **reusing the enum `Rotor` already carries** — one enum, one meaning, and its documented viewpoint (*"viewed from rear of engine looking forward"*) is already the pilot's. **Per engine**, because a counter-rotating twin exists in this class and `EngineInput` is per engine; making it an airplane-level field would make the one configuration that needs it the one configuration that cannot be stated. Clockwise by default, so every shipped project and the Appendix A oracle are **bit-identical**. | reuses `RotorDirection` |
| **D-53.5** | **The direction flips the torque at the module, under the OR-15 grant above.** It reaches every deliverable that carries the torque — the Engine Mount page's load-case file, the case index, the text report and the oracle report's section 10 — and not the report alone. A direction honoured in one deliverable and assumed in another is two conventions for one load, which is the defect **G-OR-105** exists to prevent and which note 44 §18 OR-143 is the milestone's cautionary precedent for. **Scope: 23.361(a)(1), 23.361(a)(2), 23.361(a)(3), 23.361(b)(1), 25.361(a)(3)(i), 25.361(a)(3)(ii)** — every case whose published quantity is a torque about the thrust line. | **note 44 OR-13** (admitted under OR-15) |
| **D-53.6** | **The gyroscopic condition is exempt, and the section says why** *(owner: agreed)*. 23.371(b) and 25.371 publish **all four** sign combinations of `±Myy` and `±Mzz`, so the set the mount is checked against is identical whichever way the propeller turns; flipping a sign there would rename four cases and change nothing. Stated in section 10 rather than left to read as an oversight, on the same reasoning that has the thrust zeros printed rather than blanked (OR-164). | OR-164 (same shape) |
| **D-53.7** | **The convention is stated where it is entered and where it is read** *(owner: "this needs to be very explicitly stated in the GUI and the report, especially the sign convention")*. The Engine Mount page states, beside the direction control, that positive is **clockwise seen from the pilot's seat**, that the default is clockwise, and what the two points are. Section 10.1 states the direction **per engine** in its sign paragraph and marks an assumed line as assumed. Neither wording is written twice: both read one owner, the same shape `_control_sign_convention` gave sections 7–9 (note 44 OR-150). | OR-150 (the pattern) |
| **D-53.8** | **The balanced cases are out of scope, and the gap is filed** *(owner: "maybe this should be an issue raised for 0.8.3 or later milestone?")*. `balance.hub_thrust_set` applies `EngineInput.thrust_lb` as a pure `−x` force, and its own docstring says why: *"The P-6 incidence/toe angles (`i_T`, `tau`) have no fields and no estimator, and inventing them would put a lateral and a vertical component into every case on an assumed geometry."* An entered thrust line **is** those missing fields, so this note creates the input that unblocks it and stops there — honouring it would move every balanced case, every deck and the digests, in `modules/balance.py`, which the OR-15 grant does **not** cover. Filed for 0.8.3+ against note 21. | note 21 |
| **D-53.9** | **Entered on the Engine Mount page, drawn on Configuration & Layout** *(owner: Q5/Q6)*. The input sits with the rest of the engine's geometry on `app/views/engine_mount.py`, which already carries both CGs; the Configuration & Layout three-view **draws** it, alongside the engine markers it already places at `engine_cg`. One field, one page, one drawing — not the same control on two pages. The oracle GUI needs no edit: it builds from `field_registry`, so a registry row is enough and `oracle_app/form.py` stays frozen and untouched. | note 44 OR-13 (untouched) |

## 4. Gates

- **G-53.1** — *(D-53.4/D-53.5)* a counter-clockwise engine's torque is the exact
  negative of the same engine's clockwise torque, **in every deliverable that
  carries it**, case for case: the load-case file, the case index, the text
  report and section 10.2's two tables. Asserted on a constructed
  counter-rotating twin, both engines in one project.
- **G-53.2** — **every shipped example is byte-identical.** The Imperial baseline
  digests do not move for the direction default, and `test_engine.py`'s Appendix
  A figures hold at ±0.1 %. The gate that a default is a default.
- **G-53.3** — *(D-53.3)* an entered line is used and an unentered one is marked
  ASSUMED, asserted in **both** directions; and with nothing entered the axis is
  exactly `(−1, 0, 0)`, so `ga6_normal`'s section 10.2 prints `Mz = 0` and its
  `Mx` is the whole torque.
- **G-53.4** — *(D-53.1)* a half-entered line — one point of the two — is refused
  **by name**, and the refusal names the field that is missing. Neither silently
  ignored nor completed from a derived second point.
- **G-53.5** — *(D-53.2)* a pusher installation, entered with its forward point
  aft of its propeller, resolves to the same torque sign as a tractor with the
  same rotation. The gate that D-53.2's "no tractor assumption" is true and not
  merely stated.
- **G-53.6** — *(D-53.6)* the four gyroscopic sub-cases are **unchanged** by the
  rotation direction, all six components, and section 10 states the exemption.
- **G-53.7** — *(D-53.7)* the Engine Mount page states the sign convention beside
  the control, and section 10.1 states each engine's direction; both through one
  owner, so the two cannot word it differently. Asserted on the rendered content
  model and on the GUI journey.
- **G-53.8** — *(D-53.9)* the Configuration & Layout three-view draws each
  engine's thrust line, entered or assumed, and marks which; a project with no
  engine draws none and does not fail.
- **G-53.9** — *(D-53.8)* `hub_thrust_set` still applies a pure `−x` thrust, and
  says so in band, on a project that enters a thrust line. The gate that this
  note's scope held.

## 4a. Found while implementing

- **BASIC's `INT` floors, so the sign cannot be applied inside it.**
  `ENGLOADS.BAS` line 944 prints `INT(-TORQSUDSTOP)` and the port reproduces it
  with `basic_int`. Flooring is not symmetric about zero: `floor(-6824.6)` is
  `-6825` while `floor(+6824.6)` is `+6824`, so applying the direction inside
  the flooring made a counter-clockwise engine publish a stoppage torque **1
  ft-lb smaller in magnitude** than the same engine turning the other way — a
  difference in the rounding, presented as a difference in the load. **G-53.1**
  caught it on the first run. The fix is `_floored_torque`: the oracle's own
  floored value is the *clockwise* one, and a counter-clockwise engine publishes
  its exact negative, so the two are mirrors and the printed figure is
  untouched.
- **The oracle projection strips a field that is not `ORIGINAL` or `supplied`,
  so all three new fields had to earn the `supplied` mark.** OR-21 makes the
  report a function of the oracle projection; left plain, an entered thrust line
  would have been invisible to the very section that exists to resolve loads
  about it, and a counter-rotating engine's report would have stated the wrong
  rotation. Both points are also registered in `SENTINEL_DEFAULTS` — absent
  means assumed-with-a-note, which is the class #98 refuses to filter off an
  oracle page — and each row's basis states the G5 result that earns the mark.
- **A `None` triple does not survive the oracle GUI's generic renderer**, which
  is what turned D-53.1's `Optional[Vec3]` into the zero sentinel above. The
  page's own round-trip gates caught it — `test_view_unit_roundtrip`,
  `test_dirty_flag` and `test_widget_freshness`, eleven failures between them,
  all saying the same thing: rendering the engine page materialised
  `thrust_line_aft: None` into `(0, 0, 0)` and wrote it back. That is the
  load-bearing-blank class the schema already has a convention for.
- **All three fields needed `supplied`, and that moved a gate's dial.** The
  supplied set went to 30 against 198 original fields — 15.15 %, just past the
  15 % line `test_oracle_inputs` has held since #98. The line moves to **16 %**
  with its reason stated in the gate, and each of the three marks is
  demonstrated there: omitted, an entered thrust line is invisible to the
  section that exists to resolve loads about it, and a counter-rotating engine's
  report states a rotation the analysis did not use. The dial has now moved
  twice in the project's life, both times with a class of field behind it and
  never to close a failure.
- **The drawing decision was briefly written twice**, once in the report's three
  views and once in the Configuration sketch, and the two would have disagreed
  about how long an assumed line is drawn the first time either changed. It is
  now `derived_geometry.engine_thrust_segments`, read by both (rule 3). The
  length is a fraction of the **body**, not of the plot, so the same engine
  draws the same line in both documents.

## 5. What this note does not do

- It does not change any load **magnitude**. Every number is the module's own;
  what changes is one sign, under a stated input, and the axis the resolution
  is about.
- It does not touch `modules/balance.py`, `modules/aileron.py`, or any frozen
  file other than `modules/engine.py`, and there only the torque sign.
- It does not give the thrust line a *location* consumer. The two points define a
  direction and are drawn; only D-53.8's parked work would read where the line
  sits.
