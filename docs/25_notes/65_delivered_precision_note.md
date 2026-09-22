# Every delivered cell prints at the precision its unit prescribes (design note 65)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-21** (PROPOSED and AGREED the same day — owner, in
session, under the solo profile, `DEVELOPMENT_PROCESS.md` §0; rule 1's
working-alone branch; the three questions of §8 are **ruled** there and
written into D-65.4 and D-65.6).
Filed against **#161** (band B7, 0.8.6, tier M): the 2026-09-01 owner PDF
review's OR-14 finding that `format_value` prints inconsistent precision and
flips notation on integral values, held until the 0.8.2 freeze lifted and
sequenced **last** in the baseline wave because it reformats what every other
row produces. #260 and #293 were the rows ahead of it; both shipped
2026-09-21. The owner's rulings of 2026-09-21 are §2; the measurements that
shape them are §1.

**Tier M.** A behaviour change to an existing capability — how a number
becomes text on the human channel (report, case index, CSVs, module text
views, the GUI results tables) — with no schema hop and no load moved. The
solver channel is outside it (§3, D-65.8): `deck_format.fmt` prints NASTRAN
seven-figure scientific by its own contract and its own gate.

**Conventions:** `CONVENTIONS.md` §7 — this note **amends two rows**: *How
many digits a GUI shows a value at* (`units.display_format`, the entered
channel) gains the delivered channel and becomes one row with two owners in
the same file; *Platform-stable deliverable bytes* (d) is reworded, because
the "two far-apart spellings" it quantizes between no longer exist (the
quantization itself stays). **Theory:** none — no equation is touched.
`theory_sources.md` §Base-method uncertainty is the datum for §5.
**Precedent:** note 44 OR-14 (a defect in frozen code is filed, not fixed —
the finding this note pays), OR-194 (inputs are not re-echoed; the packaged
`project.json` is their record), PB-22 (widget precision is a property of the
quantity, not the page — the rule this note extends from the entered channel
to the delivered one), #147 (the twelve-figure quantization, kept), #232 (the
SI channel converts by the Imperial unit string — the key this note reuses).

---

## 1. Measurements (2026-09-21, at `dev/v0.8.6` after #293)

### 1.1 What `format_value` does today

One function, `sloads/report/render.py::format_value`, renders every numeric
cell of the human channel: 113 call sites in the package (92 in
`oracle_sections.py`, 11 in `render.py`, 4 in `front_sections.py`, 2 in
`content.py`, 4 in `oracle_app/`) and about 100 test assertions that go
through it rather than pinning strings. Its rule has two branches on the
twelve-figure-quantized value: an integral value prints in full (`str(int)`),
everything else prints `%.4g`. Three faults follow from `%g`, all visible in
one table of `ga6_normal`'s governing loads:

| Cell | Prints today | Fault |
|---|---|---|
| Fuselage load on wing (lb) | `1.336e+04` | `%g` switches to exponent form when the exponent reaches the precision, so any non-integral load above 9,999.5 is scientific |
| Unbalanced moment about CG (lb-in) | `2.438e+05` | the same, one column over |
| a load of 24000.0 beside 24000.4 | `24000` beside `2.4e+04` | the integral branch prints in full, its neighbour does not — two notations in one column |
| a factor of 2.400 | `2.4` | `%g` strips significant zeros, so two cells at the same precision read as different precisions |
| CL | `0.4718` | correct — four significant figures is right for a coefficient |

### 1.2 The population

Every `LoadValue` the three shipped fixtures (`ga6_normal`, `baron_58`,
`atr42_100`) emit across every registered module, walked from
`registry.run_all_modules` (scratchpad `proto161.py`):

| Measure | Value |
|---|---|
| Cells | 29,283 |
| In exponent form today | 2,592 (8.9 %) |
| Cells the §3 rule changes | 13,835 (47.2 %) — almost all by keeping a trailing zero or fixing a decimal count |
| Cells that reach the §3 three-figure floor | 1,912 |
| Distinct unit strings emitted | 23 (§3 tables every one) |

The SI channel makes the notation fault worse, not better: a pound-force
becomes 4.4 newtons and an inch-pound 0.113 N·m, so nearly every SI load cell
crosses the `%g` threshold — `4448.2216` lb prints `4448`, the same load
converted prints `1.979e+04`.

### 1.3 What the entered channel already does

The GUI's number widgets have had a per-quantity precision owner since
PB-22: `units.display_format` returns `%g` for a dimensionless field (so
FLTLOADS' `0.004128` shows as entered) and `%.4f` for a dimensioned one, and
`tests/test_oracle_gui.py` fails any renderer that writes a format literal of
its own. That is the "as entered" half of the owner's question in §2 and it
is already paid; nothing in this note touches it. The delivered channel has
no such owner — `format_value` takes a value and nothing else, so it cannot
know whether it is printing a coefficient or a bending moment.

### 1.4 Two observations the walk made, outside this note

- `select.py`'s *CP of total load* (`% tail MAC`) reaches 2.7 × 10⁵ on the
  ATR: the centre of pressure of a tail load passing through zero. The §3
  rule prints it honestly (`267700.00`); whether SELECT should state a CP of
  a vanishing load at all is SELECT's question, not a formatting one, and is
  not filed here (its magnitude is a diagnostic, not a delivered load).
- Sixteen hand-written float formats survive in `sloads/report/`
  (`applied.py` 4, `tables.py` 4, `oracle_sections.py` 5, `latex.py`,
  `plots_tex.py`, `render.py` 1 each). The PB-22 guard scans only
  `oracle_app/` and `app_shell/`. D-65.7 extends it.

## 2. Owner rulings (2026-09-21, in chat)

1. **Per-quantity precision, keyed on the unit** ("option one"): a force
   and a coefficient do not deserve the same rule. The uniform fix (no
   notation switch, trailing zeros kept) and the per-unit decimal count land
   **together** in one change, not as two steps.
2. **Entered precision is not preserved to the report.** Considered and
   rejected, with the two reasons recorded so it is not asked again: the
   report deliberately does not re-echo inputs (OR-194 — the packaged
   `project.json` is their exact record), and a value converted to the
   other unit system has no "entered" digit count to keep. The entered
   channel's own precision is PB-22's and unchanged (§1.3).
3. **Percentages print at two decimals**, not one: a 0.01 % MAC step on an
   89-in MAC is 0.009 in, the order the station row's 0.1 in resolves, so a
   CG in percent and a CG in inches carry matching precision.

## 3. Decisions

- **D-65.1 One owner, one file, two channels.** `sloads/units.py` — which
  already owns widget precision (`display_format`) and the Imperial→SI
  conversion keyed by unit string (`_RESULT_TO_SI`) — gains
  `DELIVERED_PRECISION`, a table keyed by the **Imperial unit string a
  `LoadValue` carries**, and `delivered_precision(units) -> Optional[int]`
  (a fixed decimal count, or `None` for the significant-figure rule).
  `format_value(value, units="")` reads it. Nothing in `sloads/report/`
  decides a digit count of its own.
- **D-65.2 The rendering rule.** On the twelve-figure-quantized value
  (`units.canonical`, #147, unchanged): an `int` prints as itself; a unit
  with a fixed decimal count prints at that count, **never** in exponent
  form; a unit with none prints at **four significant figures in plain
  decimal with trailing zeros kept** (`0.4718`, `4.930`, `0.1070`).
  Exponent form survives only below 10⁻⁴ or at and above 10⁹ in magnitude,
  where no delivered load lives. The near-integer cliff #147 quantized
  across cannot recur: there is no integral branch for a float.
- **D-65.3 The three-figure floor.** A fixed-decimal row that would show
  fewer than three significant figures falls to the significant-figure
  rule for that cell: a moment of 0.3 lb-in prints `0.3000`, not `0`; a
  station of 0.004 in prints `0.004239`. This is the one place the two
  styles meet and it is stated once, in the owner. An exact zero prints at
  the row's decimal count (`0`, `0.0`, `0.00`).
- **D-65.4 The table.** Cell counts are §1.2's population.

  | Unit strings (Imperial) | SI label | Cells | Rule | Imperial | SI | Why |
  |---|---|---|---|---|---|---|
  | `lb` (force), `lb` (mass), `lb-in`, `ft-lb`, `in^2`, `lb-in^2`, `slug-ft^2` | N, kg, N·m, m², kg·m² | 12,517 | 0 decimals | `13360`, `243800` | `59428`, `27547` | a load or moment below one unit is noise against §5's band; the row the review is about |
  | `in` | mm | 5,921 | 1 decimal | `112.5`, `403.7` | `2857.5` | stations and arms; the CG owner and the mass model carry stations to 0.1 in |
  | `ft` | ft | 68 | 1 decimal | `12000.0`, `25000.0` | same | altitude, aviation-standard in both systems, never converted (#232 carve-out); one decimal with the stations, so a length is a length (§8 Q2) |
  | `kt(EAS)`, `ft/s` | kt, m/s | 2,222 | 1 decimal | `170.0`, `160.4` | `48.9` | design speeds are pinned to 0.1 kt (VA 160.4 on the ATR) and the manual prints them so |
  | `deg`, `deg/s`, `deg/s^2` | same | 2,371 | 2 decimals | `0.53`, `-3.41` | same | angles of attack and tail angles are small; 0.01° resolves them without pretending more |
  | `lb/in^2`, `lb/ft^2` | kPa, kN/m² | 309 | 2 decimals | `5.21`, `18.47` | `35.92` | pressures and wing loading are order 1–100 |
  | `%`, `%MAC`, `% tail MAC` | same | 1,312 | 2 decimals | `25.30`, `10.00` | same | ruling 3 |
  | `g` | same | 294 | 2 decimals | `3.80`, `-1.52` | same | load factors are quoted to two places in Part 23 and the manual |
  | `` (dimensionless), `1/deg`, `/rad`, `s` | same | 4,266 | 4 significant figures | `0.4718`, `0.1075`, `4.930`, `2.350` | same | coefficients, slopes, times: today's precision kept, minus the notation switch, plus the zeros |
  | any string not tabled | | 0 today | 4 significant figures **and gate 3 fails** | | | the fallback exists so a report never crashes; the gate so a new unit never ships unrowed |

- **D-65.5 The SI channel uses the row of the Imperial unit it converted
  from.** Every SI unit in `HUMAN_SI` is finer than, or within a factor of
  2.2 of, its Imperial source, so the same decimal count is at least as
  meaningful; the row key is the string the converter already reads, so
  there is no second key to drift. `content.py`'s `plain`/`load` pass their
  Imperial `dim` label; `render.py`'s tables pass `lv.units`.
- **D-65.6 The safety-factor cell has no special case.** `sf_cell` and the
  LIMIT statement print the factor under the dimensionless rule (`1.500`,
  `1.000`, `1.250`) like every other unitless quantity. The owner's ruling
  (§8 Q1): a factor is not always a round regulation constant — a future
  25.302-class factor, or a per-condition derived one from the governing
  table, is a number in its own right — so the cell must not carry a rule
  that presumes it is. One rule, no exception, nothing to drift.
- **D-65.7 No renderer writes a digit count.** The PB-22 AST guard extends
  to `sloads/report/`: a format literal or an f-string spec with a
  precision fails unless the line carries a stated exemption (an axis tick
  label, a LaTeX length, a percentage the text composes). The sixteen
  survivors of §1.4 are each routed through `format_value` or exempted with
  the reason, at implementation.
- **D-65.8 The solver channel does not move.** `deck_format.fmt` and every
  `sbeam/*` digest are untouched; gate 5 pins it.
- **D-65.9 Every call site hands over its unit.** The sweep is the cost of
  the item: 113 sites, of which 81 in `oracle_sections.py` format a value
  whose unit is in the section's own column header rather than on the
  line. A site that renders a value with no unit passes nothing and gets
  the dimensionless rule, which is only correct for a dimensionless value —
  so the sweep is a reading of each site, not a mechanical edit.

## 4. Gates (benchmark-first; every one on every shipped fixture)

1. **The rule, by example** — `tests/test_platform_stability.py`: one
   table-driven test stating every row of D-65.4 with an Imperial and an
   SI example, the floor (D-65.3), the zero, an `int`, the two exponent
   windows and the trailing-zero cases; the #147 near-integer pair
   (`-687258.0`, `-687257.9999999999`) prints one string.
2. **No exponent form on the human channel** — every cell of every `txt/*`
   and `csv/*` channel, the case index and the gear report, on every
   shipped fixture, in both unit systems, contains no `e+`/`e-` between
   digits (a value outside D-65.2's window is asserted absent from the
   population, so the window is measured, not assumed).
3. **Every unit string has a row** — the `LoadValue` walk of §1.2 over the
   shipped fixtures, plus every key of `_RESULT_TO_SI` and every label in
   `HUMAN_SI`, is a subset of `DELIVERED_PRECISION`'s keys; the fallback
   row is never reached by a shipped fixture.
4. **No renderer writes a digit count** — D-65.7's AST walk over
   `sloads/report/`, `oracle_app/`, `app_shell/`.
5. **The solver channel did not move** — the digest wave that closes #161
   changes `txt/*`, `csv/*`, `case_index` and `gear_report` only; every
   `sbeam/*` digest byte-matches its pre-#161 value (asserted in the
   closure, recorded in the history fragment).
6. **The ulp guards still hold** — `test_no_printed_deliverable_cell_hangs_on_the_last_ulp`
   passes unchanged: quantization before formatting is kept, and the new
   function is monotone in the value it prints.
7. **The SI cell carries the Imperial row's decimals** — for one load, one
   station, one pressure and one percent per fixture, the SI rendering has
   exactly the decimal count of D-65.4's row.

## 5. Effect vs error bar (rule 6)

Zero, by construction: no load, station, speed or factor changes value; the
note changes the text a value becomes. The datum it is measured against is
the other way round — `theory_sources.md` §Base-method uncertainty puts the
suite's own ceiling at 5–10 % on a distributed load and ±0.1 % on the
integrated totals the oracles pin, so four significant figures (0.05 %
resolution) already states more than the method reproduces, and a whole
pound on a load or 0.01° on an angle loses nothing a consumer could see. The
item is ranked by rule 6's second clause: a defect with first-order effect
on shipped content (every delivered table cell) outranks every fidelity row.

## 6. What this supersedes / touches, and what it leaves

- **Supersedes** the two-branch rule in `format_value` and the "two
  far-apart spellings" wording of `CONVENTIONS.md` §7 row *Platform-stable
  deliverable bytes* (d). The quantization the row owns stays, and stays
  the one owner for both channels (e).
- **Amends** `CONVENTIONS.md` §7 row *How many digits a GUI shows a value
  at* to cover both channels: entered (`display_format`, PB-22, unchanged)
  and delivered (`delivered_precision`, this note), one file, two guards.
- **Touches** every human-channel digest of every fixture (gate 5's list)
  and about 100 test assertions that call `format_value(lv.value)` without
  a unit; each passes `lv.units` at implementation (the helper form
  `format_value(lv.value, lv.units)` is the sweep's idiom).
- **Leaves** the entered channel (§1.3), the solver channel (D-65.8), the
  LaTeX report's structure (it typesets the same strings), and SELECT's CP
  at vanishing load (§1.4).

## 7. Closure obligations (tier M)

- `CONVENTIONS.md` §7: the two rows of §6, present tense.
- `changes/delivered-precision.history.md`, one paragraph, lead phrase the
  changelog derives from (note 61 CV-2).
- Backlog row 6 (#161) removed; the B7 recount.
- One Imperial digest wave on the human channels of every fixture, with the
  `sbeam/*` channels asserted unmoved (gate 5).
- `format_value`'s docstring rewritten to the rule; the #147 paragraph
  shortened to the quantization it still owns.

## 8. Rulings taken at AGREED (owner, 2026-09-21, in chat)

- **Q1 — the safety-factor cell.** Proposed: `1.5`, stripped, as the
  governing table states it. **Ruled: no special case** — the cell prints
  under the dimensionless rule. A safety factor will not always be 1.0 or
  1.5: when the suite applies a 25.302-class factor it is a computed
  number, and a rule that strips it as a constant would misstate it.
  Written into D-65.6.
- **Q2 — altitude decimals.** Proposed: none (`12000`). **Ruled: one
  decimal**, with the stations. Written into D-65.4's `ft` row.
- **Q3 — the unrowed-unit fallback.** Proposed: print at four significant
  figures and fail gate 3. **Ruled: agreed.** D-65.4's last row stands.
