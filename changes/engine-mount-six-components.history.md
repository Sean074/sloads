## Step 162 — The engine mount takes six components at one point (note 44 §20, tier L, 2026-09-07)

**Objective.** Give the oracle report its Section 10: what the engine-mount
conditions were computed from, where their loads act, and all six components of
each in the airplane's own axes — the oracle prints a load factor, one load, a
point and a single torque with no axis at all. Building it turned up two defects
and a wrong sign of my own, and the sign is the part worth recording.

**Agreed first.** Design note 44 §20 (**OR-158 … OR-170**), settled with the
owner in session on 2026-09-07 before any code, from seven answered questions:
the application point stays the oracle's, the published sense is what the engine
applies to the airframe and is to be stated explicitly, the thrust axis is
resolved into the global frame with a second table giving the torque and thrust
about the thrust line, thrust is not a component of the 23.361/23.363 cases, each
gyroscopic sign combination is its own case, one row per engine, and all three
views draw the airframe outlines where they are available. Gates **G-OR-104 …
G-OR-112**.

**The sign, derived rather than chosen (OR-162).** The first implementation
negated the module's torque to turn "the reaction" into "the applied load", which
made Section 10's `Mx` equal to the load-case file's `ENG MOUNT TORQUE` — the two
conventions agreeing, which is the one outcome that means one of them has been
lost. Third law, twice, settles it: a propeller turning clockwise from the
pilot's seat is driven by `+Q`, returns `−Q` to the engine, is held by `+Q` from
the mount, and the engine therefore delivers **`−Q`** to the airframe. `−Q` is
exactly what `mx_mount_torque` already carries, so nothing is negated — it is
*rotated*. With the thrust line pointing forward, `−Q` about it is `mx = +Q`
about the aft-positive `x` axis, which carries starboard up: the left roll a
clockwise propeller produces. Two independent readings agreeing is what makes the
sign derived, and it is why the printed scalar and the printed `Mx` carry
opposite signs — which **G-OR-105** now holds them to, in both the equal-magnitude
case and the inclined-axis case.

**The defect in the fixture (OR-170).** Measuring for OR-159 found `ga6_normal`
printing its application point at waterline **3.166** where Appendix A p227
prints **93.022**. Both entered CG waterlines were wrong — the propeller's `x`
in the engine's `z` slot, the printed *combined* `z` in the propeller's — and the
page supplies the right pair (92 and 100) exactly. The fixture's own comment
recorded why it survived: *"XPROP chosen so combined XPP = 17.91"*, and no test
asserted `zpp`. Under rule 6 the defect outranked the iteration it was found in.
`cessna_210` carries the same shape of error with no page to correct it from and
is filed with its number.

**The defect in the owner.** `load_cases_to_rows` decided whether a condition
fans into sign combinations by matching its FAR *reference* against `23.371(b)`.
`25.371` packs the same four sub-cases under a different reference, so on any
FAR-25-enabled turbopropeller project the Engine Mount page's load-case file
printed one row with **no moments at all**. Fixed at the owner by asking the
keys the sub-cases are carried in, which is what identifies them (rule 4).

**Deliverables.**
- `export/coordinates.py` — `engine_thrust_axis` and `engine_applied_load`, the
  one owner of the thrust line and of the resolution onto airplane axes, with
  `ASSUMED_THRUST_AXIS` for the installation that locates no hub.
- `derived_geometry.py` — `fuselage_outline(project, frame)`, the first and only
  producer of a drawn body, in each of the three views, reading
  `fuselage_centreline` for the side view's datum.
- `report/oracle_sections.py` — `_engine_mount` and its two subsections, the two
  load tables, the three view figures, and `_ENGINE_SHORT_NAMES` so a
  ten-column table carries a name and not a sentence. `build_section` now renders
  a builder-discovered absence instead of dropping it.
- `report/render.py` — `_has_gyro_subcases`, and both fan-out branches through it.
- `tests/test_oracle_report_engine.py` — new, 19 gates, the nine of §20 across
  four shipped examples including the twin and the assumed-axis turbopropeller.

**Test.** **G-OR-104** is the one that matters: for every case of every engine of
every shipped example, the six printed components are recomputed from the
module's own values **through `engine_applied_load`** and compared cell for cell,
so a component added later cannot inherit a literal at a call site. Beside it:
the Appendix A engine reaching the document including the waterline OR-170 fixed;
the four gyroscopic ids `a`–`d` with the vertical and thrust constant across
them; both engines of a twin at mirrored butt lines; an assumed axis marked and a
derived one not, asserted in both directions on shipped data; and the three views
built on a project with no geometry at all. Suite **3695 passed**, ruff and mypy
clean, and all three shipped reports still compile with no LaTeX warnings.

**Key decisions.** OR-159 keeps three stations in the document and quotes the
loads about exactly one — the other two are the deck's nodes, and a reader
transferring the set needs the offsets more than they need them hidden. OR-164
prints `Fx = 0` in the torque cases rather than filling it from the engine's
entered design thrust, because that is a flight input and not a 23.361 component;
OR-167 prints one sense of the side load and states the other, because fanning it
into two would be the report minting a case the analysis did not run — which is
the line OR-165's four gyroscopic cases are on the other side of.
