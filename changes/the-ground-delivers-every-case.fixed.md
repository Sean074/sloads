- **The nose gear's critical ground case was never reported (design note 44 OR-185, tier L, 2026-09-07).**
  `landing._critical` ranked each FAR family on `max(main-wheel resultant,
  nose-wheel resultant)` and returned one case. That is not a tie-break between
  two candidates for one title — it is a comparison between two different gears,
  and the loser's larger reaction on the *other* gear was discarded. On every
  shipped example the two-wheel level landing won 23.479(a) on main-wheel load,
  so the **three-wheel level landing never appeared as a critical case** although
  its nose reaction is the largest of the family (1786.8 lb on `ga6_normal`,
  4194.3 on `baron_58`, 8178.8 on `concept_regional_jet`) — and it is the
  condition the fuselage section's own advisory sends a reader to the landing
  section to find. Each family is now ranked once per gear it loads, and the
  shipped condition set goes from 40 to 42.
- **A multi-engine load-case index placed one engine's loads at the other engine's butt line (OR-193).**
  Two of the six engine-mount conditions — the 23.361(b)(1) sudden-stoppage torque
  and the 23.371(b) gyroscopic condition — carry no `loc_*` values while the four
  beside them for the same engine do, and `load_cases_to_rows` filled the gap
  with the **first** location in the whole set. So the right-hand engine's
  stoppage torque and its four gyroscopic sub-cases were published at the
  left-hand engine's station: ten rows on `atr42_100` and `dhc8_dash8`, fifteen
  on `concept_regional_jet`, each a real load on the wrong side of the airplane.
  A condition with no location of its own now takes the point of the condition it
  follows, which is that engine's. The producer stating the point on every
  condition it emits is the proper repair and is filed: `modules/engine.py` is
  frozen for 0.8.2.
- **Seven markdown emphasis markers were reaching the printed page, and the class had no guard.**
  `latex.py` has no `**` → `\textbf` conversion and never had one, so a marker
  written into a figure caption, a table note or a body paragraph is always a
  literal artefact. Section 12 shipped seven and the previous iteration's were
  caught by eye, which is what makes it a class rather than a slip. Stripped, and
  swept: no rendered oracle document on any shipped report may contain `**` or a
  non-ASCII character, asserted over every section, caption, note and appendix.
- **`backlog_issues.py create` filed 19 duplicate issues for rows that already named their own.**
  The bridge's two halves disagreed: `rewrite_backlog` has always skipped a line
  carrying `(#N)`, while `create` consulted only the persisted map — which is
  keyed on a **truncated title**, so rewording a row made its key miss and the
  row was filed again. One run on 2026-09-07 opened #194–#208 and #211–#214 for
  rows whose own text named their number in the line the parser had just read,
  plus three issues titled from parser fragments (`"#170"`, `"#171"`,
  `"Overtaken by note 49, close on GitHub:"`). `Item` now carries the number its
  line already states, `create` adopts it instead of filing, a defect bullet
  whose heading is only a pointer adopts the issue it names, and a heading ending
  in a colon is a lead-in rather than a defect. The map is re-pointed at the
  numbers the backlog states and every promoted defect bullet now carries its
  own `(#N)` in the file, so the record is self-describing and the cache can be
  rebuilt from it rather than trusted. The measure of the fix: run against a
  **wiped** map the bridge would now file **three** items — two defect bullets and
  the D-5 design decision, none of which the backlog stamps — where the same file
  produced 32, and **no table row** among them, which is the half that mattered.
  (Corrected 2026-09-07: this fragment first said *one* item, counting only the
  decision.) The
  22 spurious issues are closed, each pointing at the one it duplicates. Three
  guards, one of them asserting the cache has not drifted from the record.
