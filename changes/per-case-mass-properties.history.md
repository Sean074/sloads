## Step — WTONECG reports every CG case's loading of record and labels the all-items sum as the database ceiling: per-case mass properties on the page and in the report, the Geometry gear angles per case, one owner for the mass state (#382, design note 70, tier L, 2026-10-17)

**Objective.** WTONECG's one condition and the persisted `Project.mass` were
the sum of every weight-database row. On the Appendix A airplane that sum is
the aft-gross loading (p136), which is why the oracle held and nobody looked;
on every other bundled fixture it is the database *ceiling* (G-14), not a
loading: 43,308 lb against an MTOW of 36,817 on `atr42_100`, 6,540 against
5,500 on `baron_58`. The Ixx / Iyy / Izz / Ixz on the Weight & Mass Properties
page and in report §2.2 therefore belonged to no case — the ATR's Ixx is
160,600 slug-ft² with the wing fuel aboard and 34,600 without, and the page
showed the first for everything — and `configuration.cg_estimate` drew the
tip-back, overturn and static margin at a CG the airplane cannot fly at.
Every CG case already had a loading of record (note 63 D-25), and ONENGOUT
already computed its own per-case inertia from it (#333 ruling 4). Design
note 70 generalizes that: one row per CG case, the ceiling labelled and last.

**Deliverables.**
- **`weight_onecg.case_mass_properties`** (D-70.1/D-70.2) — the one owner of
  "the mass properties of case X": for every `weight.cg_cases[]` entry, FLIGHT
  and GROUND alike, `weights_and_inertia` over the items of its loading of
  record (`mass_distribution.derive_case_loadings`); a case whose loading does
  not derive gets no row and one stated reason (`baron_58`'s `fwd regardless`);
  the all-rows sum closes the list under `CEILING_TITLE` ("Database ceiling
  (every row aboard)"). `run` emits one condition per row; `build_mass` /
  `refresh_mass` persist the same rows. `mass_basis` (the heaviest FLIGHT case,
  aft-most on a tie) moves here from ONENGOUT, which re-exports it;
  `basis_row` is the one representative row every single-CG reader takes.
- **Schema v77 → v78** (`_hop_77`, D-70.3): `MassCase.ceiling: bool` marks the
  sum by a typed field, never a name; a v77 `mass` block (the one "itemized
  loading" row) is dropped by the hop and re-derived — the slice is derived data
  (`derived.py`) and no entered value is touched. `gear_down` is `True` on every
  row: the data base carries no gear-up position, so the gear-up variant the
  `MassResult` docstring promised is a stated limitation (Q4). The five
  examples are re-stamped; `EXPECTED_FIELDS_HASH` re-pinned.
- **ONENGOUT's `_mass_state`** reads its basis case's row through
  `case_mass_properties` (one computation; G-70.3 holds the identity on every
  fixture with a FLIGHT basis). Its deck and march numbers do not move.
- **Geometry page gear angles per case** (D-70.4, review C3): `cg_estimate`
  returns `basis_row`'s CG labelled by case ("Weight DB, aft gross"; the ceiling
  only when nothing else exists, labelled "database ceiling"); the gear
  condition emits tip-back and overturn for every case row (`… -- <case>`) and
  names the governing case on the headline pair (minimum tip-back, maximum
  overturn). On `atr42_100` the governing tip-back is `aft max landing` at
  19.5° and the governing overturn `fwd max landing` at 64.1°.
- **`cg_cases.seed_landing_cases`** seeds its waterline placeholder from the
  basis row (D-70.5), no longer from a loading that cannot fly.
- **Report §2.2** prints one table, one row per case and the ceiling last
  (`oracle_sections._mass_properties_table`, D-70.6): W, Xcg, Zcg, Ixx, Iyy,
  Izz, Ixz, θ, in the document's unit system; the SELECT inertia advisory in
  the GUI quotes the basis row by name (D-70.7).
- **Docs** (D-70.8): `PROGRAM_SPEC.md` §WTONECG reads/writes/notes rewritten;
  §SELECT no longer claims to read `Project.mass` (it never did — rod estimate
  or typed override); the configuration section's `cases[0]` sentence replaced;
  `theory_sources.md`'s WTONECG row cites the note; `CONVENTIONS.md` §7 gains
  the mass-properties owner row. `DATA_DICTIONARY.md` and the guide's generated
  pages regenerated.

**Test.** `tests/test_weight_onecg.py` — the Appendix A p136 pins stand
unchanged and a new test holds that the ceiling condition `run` emits *is*
that result (G-70.1); every fixture's rows equal `weights_and_inertia` over
each case's loading of record, in case order, ceiling last and heaviest,
skipped cases stated (G-70.2/G-70.4); the Baron `fwd regardless` case derives
no row and says why; `basis_row`'s fallback order. `tests/test_one_engine_out.py`
— the march's mass state is the WTONECG row of the same case (G-70.3).
`tests/test_configuration.py` — the labels name the case, the per-case rows
and the governing pair on a synthetic slice and on four fixtures, the ceiling
never used as a CG while a case row exists (G-70.5). Imperial digests: one
wave, `txt/csv weight_onecg` on all five fixtures and `txt/csv configuration`
on the four with gear geometry — neither a load module; every load module's
digest is unchanged (G-70.6). Gates: ruff, mypy and the whole suite green.

**Key decisions.** Q1–Q5 of note 70 §3 ruled as recommended (owner,
2026-10-17): GROUND cases get rows too; SELECT's blank-Izz default is **not**
switched to the database value (rod estimate +38 % on ga6, +51 % ATR, +71 % RJ
over the case value — conservative on every fixture and the ga6 SELECT oracle
is computed with it; M4-4 stays parked on that pair, its prerequisite now
delivered); gear angles per case with the governing case named; gear-up rows
parked as a stated limitation; a typed `MassCase.ceiling` field at v78.
