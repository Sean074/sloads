## Step 165 — The ground delivers every case (design note 44 §22, tier L, 2026-09-07)

**Objective.** Section 12, Landing Gear Loads — the oracle report's last derived
analysis section. With it the body is complete: every `oracle_steps()` step with
a `bas` that produces results has a built section, and `IMPLEMENTED` stops being
a subset of `analysis_steps()`. It is also the first section since Section 2 that
all three shipped reports carry, which is why the iteration needed no new
fixture.

**Agreed first.** Design note 44 §22 (**OR-183 … OR-193**, gates **G-OR-123 …
G-OR-130**), settled with the owner in session on 2026-09-07 before any code,
from three findings and eleven answered questions. The note carries **one OR-15
admission**, scoped to `modules/landing.py` and to two changes in it, re-pinned
in the frozen manifest with the scope recorded beside the hash.

**The finding that reshaped the section (OR-185).** Scoping the section against
the module showed the per-family "critical reaction" summaries were answering the
wrong question. `_critical` ranked each FAR family on `max(main-wheel resultant,
nose-wheel resultant)` and returned one case — which is not a tie-break between
two candidates for one title but a **comparison between two different gears**:
the winner sizes one of them and the loser's larger reaction on the other was
discarded. Measured: on all three shipped examples the two-wheel level landing
wins 23.479(a) on main-wheel load, so the **three-wheel level landing appeared in
no summary at all**, although its nose reaction is the largest of the family —
`1786.8` lb on `ga6_normal`, `4194.3` on `baron_58`, `8178.8` on
`concept_regional_jet` — and it is the condition Section 4's own advisory sends a
reader to Section 12 by name to find. A cross-reference is a promise the target
keeps; before this step the target did not contain it. Each family is now ranked
once per gear it loads, 40 conditions become 42, and **G-OR-129** asserts the
class rather than the instance.

**And the deeper one the owner ruled on (OR-184).** Presented with the fix, the
owner's answer went further: *"add all conditions, no critical case down-select
can be done without considering the airplane loads."* A ground case sizes a gear
member through a load path this analysis does not model — a drag brace, a side
brace, a trunnion — so ranking 33 conditions on any single scalar removes the
case a reader needs. Section 12 and Appendix F therefore carry **every** case,
the summaries are labelled a reading aid in the table's own note, and the CSV
header says so in capitals. What was scoped as a report section became a ruling
about what a loads analysis may hand a downstream discipline.

**A second defect, found building the engine file (OR-193).** Two of the six
engine-mount conditions — the 23.361(b)(1) sudden-stoppage torque and the 23.371(b)
gyroscopic condition — carry no `loc_*` values while the four beside them for the
same engine do, and `load_cases_to_rows` filled the gap with the **first**
location in the whole set. The right-hand engine's stoppage torque and its four
gyroscopic sub-cases were therefore published at the **left-hand** engine's butt
line: ten rows on `atr42_100` and `dhc8_dash8`, fifteen on
`concept_regional_jet`. Not a blank column — a real load at a point on the wrong
side of the airplane, which a blank would at least have invited a reader to ask
about. A condition with no location of its own now takes the point of the
condition it follows, verified against every shipped example and gated. The
producer stating the point on every condition it emits is the proper repair and
is filed: `modules/engine.py` is frozen.

**The 344 of 347 (OR-186).** The measurement that answered a question filed at
the end of §21. Every landing row reached the load-case index with no load — 40
of 40 — and sweeping the registry the figure is **344 of 347** rows on
`ga6_normal`, **543 of 555** on `baron_58`, **587 of 617** on
`concept_regional_jet`. Not a landing defect: `load_cases_to_rows`' own docstring
says its columns are *"the load components an engine mount must react"*, and a
landing case has three legs at three points and cannot be expressed in it at all.
The owner's ruling — *"a separate CSV file for each structural element … then
they can be specifically shaped for the loads presented in that csv"* — is the
general form of what four components already had, and the landing gear and the
engine mount now join them. The index itself is left unchanged and filed, because
reshaping it is a schema decision touching every producer.

**Deliverables.**
- `modules/landing.py` — the whole of the frozen file's part, under the grant:
  `landing_geometry` public so §12.1 can print the p230 oracle from the function
  the reactions were computed by, and `critical_reaction` with a gear argument.
- `export/sbeam_bridge.py` — `gear_applied_load_rows`, `engine_applied_load_rows`,
  two new `APPLIED_COMPONENTS` and two new `APPLIED_CSV_NAMES`, each with the
  in-file note its element needs.
- `report/render.py` — `point_load_records` as the single owner of the
  six-components-at-one-point extraction the index performed inline, with the
  ft-lb → lb-in conversion read off the value's own units; `_running_locations`
  carrying OR-193's fix; `_global_location` removed rather than left beside its
  replacement.
- `report/oracle_content.py` — `GEAR_LOAD_CASES` and Appendix F;
  `landing_loads` in `IMPLEMENTED`.
- `report/oracle_sections.py` — `_landing_loads` and its three subsections, six
  tables, `_attitude_figure` × 3 and `_gear_appendix`.
- `tests/test_oracle_report_landing.py` — new, 20 gates, the eight of §22.

**Test.** **G-OR-124** is the one that matters: the 23.479(a) nose row is a
three-wheel level landing and its main row is a two-wheel one, on every shipped
example, asserted against a **re-rank of the full matrix** rather than a stored
number. Beside it: all 33 cases in both the section and the appendix by case
number, so no down-select can creep back in; every appendix row's point compared
*through* `application_point_of` rather than against a literal; the three
figures' case lists asserted to partition 1-33 exactly and against `attitude_of`,
so a figure cannot come to claim geometry the reactions were not computed in; and
the fuselage advisory's forward reference swept across `_body_advisories`. Two
sibling tests that pinned the whole appendix list were rewritten to assert the
property they were about — that *their* step owns no appendix — since the list
form failed the day another section earned one and said nothing about theirs.

Lever arms verified against the manual's own figures: p235's braked roll prints
`AP 77.052 / BP 17.760 / DP 94.811 / CP 42.981` and §12.1 reproduces all four;
p234's level landing prints `K = .324`, `GAMMA = 17.978`, `BETA = 13.921` at a
ground angle of `4.057`, and so does the table. Suite green, ruff and mypy clean.
The Imperial baseline moved on exactly four channels — the landing CSV and text
report (two new summary conditions) and the case index and engine CSV (OR-193) —
and `csv/engine` moved only on the multi-engine examples, which is the location
defect confirming its own scope.

**Key decisions.** OR-184 is the one with reach beyond this section: it says that
where the loads analysis cannot see the load path, completeness beats ranking,
and it is the first time this project has stated that. OR-183 folds the free body
into the conditions subsection rather than giving it a fourth, because a reaction
and the point it is delivered at are one statement. OR-192 leaves a project with
no `landing` slice in the ABSENT state and **not** in §21's `NOT_APPLICABLE`: it
is missing an input, not exempt from a regulation, and the distinction is the
whole reason that state was created.
