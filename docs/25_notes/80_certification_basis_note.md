# The certification basis is one project field, with one owner (design note 80; #441)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-11-26 — no code.** The owner ruled in session, under the solo profile
(rule 1's working-alone branch): every recommendation in §4 is agreed as written. PROPOSED
the same day, drafted from #441 and the 2026-11-26 status review. Split from #410 so that
#437, #438 and #411 can read a basis without waiting for the transport gust schedule.

**Scope.** sloads cannot say "this project is on the Part 25 basis". The schema carries a
certification category (`speeds.category`: N, U, A, or C for concept) and one flag,
`Project.include_far25`, that only adds the 25.361 and 25.371 engine cases. Three agreed
notes (77, 78, 79) each say "on the Part 25 basis" and name #410 as the owner of that
switch. This note makes the basis a project field with one read point, folds
`include_far25` into it, states it in every deliverable, and adds the guard that stops a
second owner appearing.

Out of scope:
- any new Part 25 load case, check or schedule (#410, #411, #412, #437–#440 own theirs);
- the amendment level within a Part, and the choice between the pre-Amdt 25-86 gust rule
  and U_ref/F_g (Q3, #410);
- CS-25 or JAR-25 as a separate basis (not distinguished);
- a distinct Commuter category (`constants.py:256-258`, dormant);
- re-deriving any fixture onto Part 25 (#444 for the ATR);
- the regulation coverage matrix, which lists Part 23 Subpart C only (Q5);
- any change to a Part 23 result, case id or Appendix A oracle.

Conventions: [`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §3 (every load LIMIT, the
factor stated and applied nowhere; `safety_factors._RANGES` already classifies Parts 23 and
25 by the same section ranges, so no factor moves), §4 (fixed case ids), §7 (a
cross-cutting convention gets a single-source owner and a drift guard).

## 2. Decisions

| # | Decision | Rationale |
|---|---|---|
| **D-80.1** | **One field, `Project.certification_basis`, an enum with two members: Part 23 and Part 25.** It sits on `Project`, not on `speeds`. | The basis is read by the engine, landing, roll and gust rows alike. `speeds.category` is one slice's input. |
| **D-80.2** | **Absent means Part 23, and the writer omits the key on Part 23.** | Every GA project stays byte-identical on save. `include_far25` is written the same way today (`io.py:1600`). |
| **D-80.3** | **The basis and the category are separate axes.** N, U and A remain Part 23 categories. C remains "chosen load factors, no 23.337 cap". Part 25 with N, U or A is flagged by the loader and its results are withheld; it is not refused at construction. | A Part 25 airplane has no 23.337 category. Flag-not-raise is #66's rule: a file the GUI can write must reopen. |
| **D-80.4** | **`include_far25` is removed.** A migration hop sets the basis to Part 25 where the flag was true and drops the key, with a migration note. `engine.run_all` and `engine.mount_conditions` take the basis in its place. | One owner. Note 77 Q4 refused a temporary key for the same reason. Consolidated, not kept beside the new field. |
| **D-80.5** | **One read point: `Project.is_part25`**, beside `is_concept`. No module compares the raw field. | `is_concept` is the precedent (`models/project.py:516`): a single property the modules read. |
| **D-80.6** | **A Part 25 row registry, `sloads/basis.py`**: one row per Part 25-only rule sloads builds, each with its regulation paragraph and owning module. On this note's ship it holds 25.361(a)(3)(i), 25.361(a)(3)(ii) and 25.371. | It is what D-80.7 prints and what G-80.4 checks. Each later item adds its row with its case. |
| **D-80.7** | **The basis is stated in band in every deliverable**: both reports, the case index, each applied-load CSV and the deck header. On Part 25 the statement lists the registry's rows and says the remaining loads are the Part 23 method. | Selecting Part 25 does not make the set a Part 25 set. `04_scope_and_applicability.md` already says a Part 25 airplane runs "with the Part 25 rows that have been built"; the deliverable must say which. |
| **D-80.8** | **Rows keyed on category C stay there, except the 25.335(b) Mach-margin dive speed, which moves to the basis (Q2).** | It is the only C-keyed row that emits a Part 25 `far_reference` (`structural_speeds.py:522`). The others (advisory K_d floor, landing floors as warnings, the extrapolation notes) are concept-mode behaviour, not Part 25 rules. |
| **D-80.9** | **The GUI offers the basis once, on the configuration page.** The `include_far25` entry leaves the engine page (`field_registry.py:1981`). | One input, one place. |
| **D-80.10** | **A project over the Part 23 weight or seat limit on the Part 23 basis says so in every deliverable of D-80.7**, not only in the GUI banner: the limit exceeded, and that the loads are the Part 23 method extrapolated. No project is refused. The banner names the basis field (Q4). | `atr42_100` is such a project. Category C lifts the Part 23 caps; it does not change the rule set (Q8), and a reader of the deck cannot see a banner. |
| **D-80.11** | **`SCHEMA_VERSION` bumps by one with its hop registered**; the data dictionary and the published schema are regenerated. | `migrations.py`: every bump registers a hop, identity or not. |

## 3. Gates

| Gate | Statement | Expected numbers |
|---|---|---|
| **G-80.1** | **Part 23 unchanged.** `ga6_normal`, `baron_58`, `concept_heavy` and `atr42_100` (flag absent today): results, case ids and digests identical to the parent commit; the saved JSON carries no basis key; every Appendix A oracle is green. | Byte-identical. |
| **G-80.2** | **Migration.** A file at the parent schema with `include_far25: true` loads as Part 25 with the flag gone and one migration note; with the flag false or absent it loads as Part 23 with no note. Save and reload is stable. | `atr42_300_seed` and `concept_regional_jet`: engine-mount conditions and deck subcases identical to the parent commit (counts stated in the test from the parent). |
| **G-80.3** | **Owner guard (class).** No `include_far25` remains in `sloads/`, `app_shell/`, `oracle_app/`, `cli.py` or the examples. No module outside `models/project.py`, `io.py`, `migrations.py` and `basis.py` reads `certification_basis`. | An AST scan; fails if a module compares the raw field. |
| **G-80.4** | **Registry guard (class).** On every shipped fixture: every result whose `far_reference` names a Part 25 paragraph is in the registry, and appears only when `is_part25` is true. | Would fail today for any concept project on the Mach-margin dive speed (D-80.8); whether a shipped fixture is one is measured at build. |
| **G-80.5** | **Stated in band.** Each deliverable of D-80.7 carries the basis line on both bases; on Part 25 it names every registry row. Joined to G-OR-73 and G-OR-74. | Text gate over the deck, both reports, the case index and the CSVs. |
| **G-80.6** | **Invalid pair.** Part 25 with category N, U or A loads, is flagged once by name, and delivers no results. | One flag; no exception. |
| **G-80.7** | **Over-limit statement.** A Part 23-basis project over `FAR23_MAX_WEIGHT_LB` or the seat limit carries D-80.10's sentence in each deliverable; one inside the limits, and any Part 25 project, does not. | `atr42_100` (36,817 lb): present. `ga6_normal`, `baron_58`: absent. |
| **G-80.8** | **Schema.** The published schema equals the generated one; the released-schema fixtures load through the chain. | `tests/test_migrations.py` green with the new hop. |

## 4. Questions

| # | Question | Recommendation |
|---|---|---|
| **Q1** — ruled **yes, require C** | **Does Part 25 require category C?** D-80.3 flags N, U and A. On Part 25 the load factor is the 25.337(b) formula with a 2.5 floor, which #410 will check against the entered value. | **Yes, require C for now.** #410 decides whether n₁ becomes derived on Part 25; until then "chosen" is the honest description of what the ATR fixtures do. |
| **Q2** — ruled **move it** | **The Mach-margin dive speed is allowed on any category C project today.** Moving it to the basis (D-80.8) changes what a Part 23 concept project using it is told. | **Move it, and have the hop set Part 25 for a file with `vd_basis` = Mach margin**, with a migration note. No file changes its numbers. Which shipped fixtures use the route is measured at build and stated in G-80.2. |
| **Q3** — ruled **not here** | **Is the amendment level a field?** The ATR's original basis is the pre-Amdt 25-86 gust rule; the current rule is U_ref/F_g. | **Not here.** #410 rules which gust rule sloads builds. If both are ever built, the choice is a second field then, not a third value of this one. |
| **Q4** — ruled **yes, and in every deliverable (D-80.10)** | **Should the applicability banner point at the basis?** Today a project over the Part 23 weight or seat limit is told to use concept mode (`applicability.py`). | **Yes: one sentence added** naming the basis field. No project is refused. Ruled further: the over-limit statement goes in every deliverable (D-80.10, G-80.7). |
| **Q5** — ruled **own item, #412** | **The coverage matrix lists Part 23 Subpart C only** (`report/coverage.py`). On Part 25 it reports against the wrong table. | **Its own item, ranked under #412.** D-80.7's statement covers the gap honestly meanwhile. |
| **Q6** — ruled **`"part23"` / `"part25"`** | **Field values and name.** `certification_basis` with JSON values `"23"` and `"25"`, or `"part23"` and `"part25"`? | **`"part23"` / `"part25"`.** A bare number reads as a count in a project file. |
| **Q7** — ruled **this item** | **After this ships, do #437, #438 and #411 depend on this item or on #410?** | **On this item.** Their notes ask for the basis only. #439 keeps #410 (it needs the gust schedule). The backlog rows are edited at agreement. |
| **Q8** — ruled **no, two axes** | **Should category C simply mean Part 25, with no new field?** C was read that way by the owner; in the code it lifts the Part 23 caps and changes no rule (`structural_speeds.py:183`, `landing.py:893`). | **No.** Concept mode must reduce exactly to the FAR 23 core on GA inputs (`tests/test_concept.py`), and every Part 25 case added later would break that. `concept_heavy`, an 18,000 lb commuter twin, wants the caps off and not the transport rules on. |
