## Step 159 — The oracle report states the vertical tail's loads (tier L, 2026-09-07)

**Objective.** Close the tail partition: give the oracle technical report its fourth
load-bearing section, the vertical tail and its rudder, as the mirror of section 5 —
and make the restriction sloads has always had on non-conventional empennages a thing
the document *states* rather than a thing a reader has to know.

**Agreed first.** Design note 44 §17 (**OR-128 … OR-138**), agreed with the owner on
2026-09-06, which had already settled section 6 in full when section 5 was built. Two
questions the note could not reach were put to the owner before any code and answered
in session on 2026-09-07: whether the loads reference axis survives the withholding
(it does — question (a)), and whether the condition register may look complete when it
is not (it may not — **OR-133a**). A third amendment, **OR-134a**, was forced by
implementation and is the substance of half this step.

**Deliverables.**
- `report/oracle_sections.py` — `_vtail_loads` and `_vtail_station_appendix`, which are
  two lines each: section 5's builder took the surface as a parameter, so the whole of
  section 6 and the 2026-09-07 review's five rulings arrived in it for free. Plus the
  OR-133 withholding (`_vtail_withheld`, `_non_conventional_statement`,
  `_NON_CONVENTIONAL_BODY`), the OR-133a note on the register and the summary, and
  `_inertia_basis` for OR-135's yaw-inertia provenance.
- `report/oracle_content.py` — `vtail_loads` joins `IMPLEMENTED`; Appendix E is built.
- `tail_geometry.py` — `tail_layout` and `is_conventional_tail`, the owners every
  consumer reads the arrangement through. `models/enums.py` — `TailType` stops calling
  itself "a layout sketch distinction only".
- `field_registry.py` — `geometry.parametric.tail_type` and
  `geometry.surfaces[].ref_axis_pct` marked `supplied`, each with its G5 measurement in
  the basis cell.
- `tests/test_oracle_report_vtail.py` — 22 gates, including the class drift guard.

**Key decisions.**
- **6.1's station table survives the withholding (owner, question (a)).** The loads
  reference axis is entered geometry resolved through a planform — the same numbers
  §2.1's three-view is drawn from — and withholding verifiable geometry to document a
  *load* limitation costs the reader something and documents nothing. The reason goes
  in the table's own note, so a station list above a withheld subsection cannot read as
  loads that merely failed to compute.
- **A short condition set says so, and names the case (OR-133a).** OR-133's scope was
  6.5 and Appendix E, but it names two unmodelled paths and only one is about the
  loads; the other is about the *condition list*, which 6.2 and 6.3 still print in full.
  A four-row table that looks complete reads as a measured completeness — OR-61's
  argument one deliverable over — and the summary is the table an analyst stops at.
  Named rather than counted, because OR-133's own distinction is that this is an
  omitted condition and not an understated one, and because a named case is one note
  51's D-51.1 can delete when it ships.
- **The withholding is stated ahead of the results test.** `build_tail_span` still
  returns the vertical tail's loads — they are what the balanced deck's lateral cases
  close ΣFy = 0 against, so withholding them in the calc would stop three fixtures
  assembling to document a limitation in them. The report must therefore never say
  "not produced" about loads that were, so the arrangement is checked first and the
  lead is **"Not supported"**.
- **G-OR-87 diffs against `CRUCIFORM`, not `T_TAIL`.** A T-tail is not only a report
  state: `is_t_tail` moves the horizontal tail onto the fin and adds the tip transfer,
  so a conventional-versus-T-tail diff of section 5 fails on real geometry and proves
  nothing about the withholding. `CRUCIFORM` is read by the report and by nothing else,
  so the diff changes exactly one thing and every difference it finds is attributable
  to it.

**The defect this step found (OR-134a).** OR-134 had required the `TailType` docstring
and a `CONVENTIONS.md` §7 row. That was not sufficient, and the insufficiency was
invisible until the feature was built against it: **the document is a function of
`reduce_to_oracle_inputs`** (OR-43), and `tail_type` sat outside the oracle input set,
so it was reset to `CONVENTIONAL` before the report ever read it. OR-133 fired on
nothing — `atr42_100` printed 40 rows of the loads the ruling withholds. Marking the
field `supplied` fixes it and needs no frozen-file edit, because the oracle form builds
from the registry.

Generalising on first find (rule 4) turned up the same defect one field over, and a
worse one: **`geometry.surfaces[].ref_axis_pct` was reset too.** All seven shipped
examples enter 40 % of chord; the document stated 25 %. `ga6_normal`'s horizontal-tail
root torsion printed **34.5 lb-in** where the analysis computes **60.8**,
`concept_regional_jet`'s **3645.3** against **4141.7**, and every applied-load `X` in
Appendices D and E sat **3–6 in** off the deck card the appendix says it is the same
load as. This had shipped with section 5 six days earlier, and it contradicted an
agreed ruling: **OR-51** says *"`ga6_normal` enters `ref_axis: 0.4`, so its wing
torsion is delivered about the LRA 40 % chord with the 25 %-chord oracle value beside
it — the report must not print one and call it the other."* The section 3 gate written
on 2026-09-01 had asserted `25% chord` and explained the defect in its own docstring as
though it were the ruling. Both fields are `supplied` now, the gate reads the axis from
the project, and the class has a **drift guard** rather than a prose rule: for every
shipped example and both surfaces, the beam the document states its loads about is the
beam the analysis ran.

This is the fourth instance this milestone of one defect class — *an entered value with
the right intent, shadowed by a derived stand-in, with nothing saying so* — after the
fin root waterline, the fin `symmetric` flag and the fuselage LRA. It is the first in
which the shadowing agent was the oracle projection rather than a resolution order, and
the first where a gate had been written that locked the defect in place. Filed and not
fixed: `weight.items[].consumable` is reset the same way, moving
`concept_regional_jet`'s horizontal-tail root `Fz` **−175.6 → −214.5 lb** — same class,
weight slice, on a fixture the report is not built for; the drift guard names it rather
than exempting it silently.

**The owner's review of the built section, and the typeset page (2026-09-07).** Two
findings came from reading the document rather than the code, and both are in this step.

*The vertical tail's loads reference axis was drawn along its root.* `WingStationLoad`
says its coordinates are airplane axes; for the wing and the horizontal tail they are,
which is why section 5 read them directly and was correct, and why the error was
invisible until a second surface used the same builder. On the fin `y` is the span
coordinate in the surface's own plane and `z` is the root waterline it is measured from,
so 6.1's figure drew a flat row of markers along the constant 111.5 root instead of
climbing to 167.1, and its station table called the height above the root a butt line.
The mapping already had an owner — `export.coordinates.tail_station_to_airplane`, which
is why the deck and Appendices D and E were right — and 6.1 now goes through it. This is
the same shape as OR-134a one layer down: a value whose meaning is decided elsewhere,
with the type it is stored in asserting the opposite. The docstring that asserted it has
been corrected.

*A table printed one column on top of another.* The width solver documents a floor — a
column is never narrower than its longest unbreakable token — and its last fallback
scaled every column straight past it. Table 25's `14 CFR` column needed 63pt for
`23.423(a)(1)` and was given 26, so the regulation overprinted the CG case as
`23.423(a)(1)G4`: not a tight table but a corrupt one, in which case identity could not
be read. The floor is absolute now, and a table that cannot be set upright is **turned**
(owner, 2026-09-07) rather than shrunk a third time — another size step buys about 12 %
and fails on the next wide table, while turning the page buys 53 % and never puts 8pt
type in a signed document. Fixing it exposed two more: every landscape appendix was
being sized against the portrait width, and `fancyhdr` had been warning once per page,
77 times, that the running head did not fit. Building `ga6_normal` went from 33 overfull
boxes and 77 `fancyhdr` warnings, worst 23.3pt, to **4 overfull boxes, worst 0.79pt**.

**Filed, not fixed.** The fin's root is raked — `ga6_normal`'s vertical tail meets the
body with its leading edge at waterline 117.0 and its trailing edge at 111.5 — and the
planform resolver rebases both onto a single root at 111.5. The bottom two load stations
then sit at X 284.9 and 268.9 against 262.9 immediately above them, so the axis kinks aft
at the root. Visible in Figure 24 now that the axis is drawn in the right plane at all.

**Test.** `tests/test_oracle_report_vtail.py` — G-OR-80 (five subsections, mirrored),
G-OR-83 (SELECT's own unscaled totals; every Appendix A condition present under the
oracle's name), G-OR-86 (a rudder load on all four conditions, both fixtures), G-OR-87
(the withholding over every `TailType`, the shipped T-tails, the `CRUCIFORM` diff, and
the companion gate that the calc still produces the loads on all three T-tail
fixtures), G-OR-88 (the yaw inertia's provenance), OR-131 (neither section borrows the
other's requirements), OR-133a both ways, and the reduction drift guard, plus three
gates on the loads reference axis: the fin's stations climb a waterline and stay on the
centreline, the horizontal tail's still span a butt line and share one waterline, and
each figure draws its axis in the plane its surface is in. `tests/test_report_latex.py`
— no column narrower than its own floor and the widths still fitting the page, on every
table of both shipped reports; a table turned only when no upright size holds it, both
directions, with the one that is pinned; exactly one landscape environment per turned
table; both renderers declaring their head height; and the glyph tables held to eight
words TeX itself measured. The widths behind that floor are now measurements rather
than a four-class model, which is what closed the last four warnings: all three shipped
examples build clean. Suite **3629 passed**, ruff and mypy clean.
