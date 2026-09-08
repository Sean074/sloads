## Step 163 — The engine's thrust line is an input (design note 53, tier L, 2026-09-07)

**Landed in Step 162's commit, `175369e`.** The two steps were built in one
working tree and `solo_close.sh` gates and stages the whole of it, so this step's
files went in under *"The engine mount takes six components at one point"*. Both
are recorded here as the separate steps they are — separate design notes,
separate gate sets, separate fragments — and the changelog is assembled from
these fragments rather than from commit messages, so nothing is lost by the
sharing. Noted because a reader tracing this step to a commit of its own will not
find one.

**Objective.** Section 10 shipped a day earlier resolving each engine's torque
and thrust onto the airplane axes, and it needed an axis to resolve them about.
The schema had never carried one, so note 44 OR-161 derived it from the engine CG
to the propeller hub — with a caveat printed beside it and a backlog entry filed
the same day. This step replaces the derivation with an input, and makes the
propeller's rotation an input beside it.

**Agreed first.** Design note 53 (**D-53.1 … D-53.9**, gates **G-53.1 …
G-53.9**), settled with the owner in session on 2026-09-07 before any code, from
six answered questions. The note **carries two of the owner's OR-15 admissions**, both narrow:
`sloads/modules/engine.py` for the torque sign and nothing else — not a refactor,
not a rename, not formatting in the same file — and `oracle_app/form.py` for two
`MEMBER_LABELS` rows, asked for only once it was clear there was no way round it
(a composite field in the oracle input set renders as "1, 2" unless its members
are named, and that table is the only place the naming lives). Both files are
re-pinned in the frozen manifest with the scope recorded beside the hash.

**Why a derived axis had to go (D-53.3).** The line from an engine's CG to its
hub is not the shaft; it is a line between two *mass* stations, and it inherits
every error in either. Measured: **14.0°** off the airplane axis on
`ga6_normal`, whose stations are correct against Appendix A p227 — which put an
`Mz` of −178.8 ft-lb into section 10.2 for an airplane that has no such moment —
and **71.6°**, very nearly straight up, on `cessna_210`, whose engine CG
waterline is a filed defect. A derivation that turns a station error into an
orientation is worse than an assumption that says it is one. So: **two grades of
provenance, not three** — entered, or the airplane's forward axis marked ASSUMED.
The move was checked through the owner before it was agreed: `ga6_normal`'s
23.361(a)(1) goes from `Mx +715.32 / Mz −178.83` to `Mx +737.34 / Mz 0`, with
`Mx == −torque` an **exact** float equality and `|M|` unchanged at 737.3383. The
axis was spreading one torque across two axes, not adding one.

**The sign, and the flooring (D-53.5).** A propeller turning clockwise from the
pilot's seat delivers `−Q` to the airframe, so a counter-clockwise one delivers
`+Q`. That reaches every deliverable carrying a torque — the load-case file, the
case index, the text report, section 10 — because a direction honoured in one
and assumed in another is two conventions for one load, which is the defect
G-OR-105 exists to prevent. **G-53.1 failed on its first run**, and usefully:
BASIC's `INT` *floors*, so applying the sign inside the flooring made a
counter-clockwise stoppage torque 1 ft-lb smaller in magnitude than a clockwise
one — a rounding difference presented as a load difference. `_floored_torque`
now floors the oracle's own clockwise value and mirrors it.

**Deliverables.**
- `models/inputs.py` + `io.py` + `migrations.py` + `models/project.py` —
  `thrust_line_aft`/`thrust_line_fwd`/`prop_direction` on `EngineInput`, the
  round trip that keeps `None` distinct from `(0, 0, 0)`, and schema **v62 →
  v63** as an identity hop.
- `export/coordinates.py` — `engine_thrust_axis` becomes the entered-line owner
  with `ThrustLineError` for a half-entered pair; `ASSUMED_THRUST_AXIS` names the
  fallback.
- `modules/engine.py` — `torque_sense` and `_floored_torque`, and nothing else.
  The whole of the frozen file's part in this note, under the grant.
- `derived_geometry.py` — `engine_thrust_segments`, one owner for both
  three-views, written at the second time of asking after it was briefly a copy
  in each (rule 3).
- `field_registry.py` — three rows, all `supplied` with the G5 result that earns
  the mark stated in the basis, and both points registered in
  `SENTINEL_DEFAULTS`. Without it the oracle projection strips them and the
  report cannot see a line the user entered.
- `app/views/engine_mount.py` — the controls, with the sign convention stated
  beside them (D-53.7, the owner's requirement in as many words);
  `app/views/configuration_layout.py` — the line drawn on the three-view.
- `tests/test_engine_thrust_line.py` — new, 19 gates, the nine of note 53.

**Test.** **G-53.1** is the one that matters: a counter-clockwise engine's
torque is the *exact* negative of the same engine's clockwise torque, condition
for condition, in the module, the load-case file and the text report — and it is
what found the flooring defect. Beside it: the axis is not moved by moving either
CG station (D-53.3 said as the thing it forbids); a half-entered line refused by
name in both directions; a pusher resolving to the same sign as a tractor, which
is what makes "no tractor assumption" true rather than merely stated; the
gyroscopic set unchanged either way; and clockwise costing nothing, with the
Appendix A figures held through the default. Suite green, ruff and mypy clean.

**Key decisions.** D-53.2 states which point is forward rather than inferring it,
and that single choice is what removes every tractor assumption from the section.
D-53.6 exempts the gyroscopic condition and *says so in the document*, on the
same reasoning that has the thrust zeros printed rather than blanked: an omission
a reader can mistake for an oversight is worth a sentence. D-53.8 stops at the
input — `hub_thrust_set` still applies a pure `−x` thrust, gated by G-53.9,
because honouring an inclined line changes the trim solution and not just the
card it writes, and that needs a note of its own.
