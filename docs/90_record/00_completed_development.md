# Completed Development

The authoritative record of what has shipped: completed modules/phases, key
decisions, and resolved defects. Items move here from
[`../30_future/00_backlog.md`](../30_future/00_backlog.md) the moment they close,
with a matching `CHANGELOG.md` entry.

Each entry uses the step format: **Objective**, **Deliverables**, **Test /
Acceptance**, **Key decisions**.

**Live cycle only.** This file holds the current release cycle plus the previous
release cut. Older blocks roll into frozen, do-not-edit archives at each release
(`RELEASE_PROCESS.md` §4): the 0.8.3 cycle and the 0.8.2 cut are in
[`62_completed_development_to_0.8.3.md`](62_completed_development_to_0.8.3.md),
the 0.8.2 cycle and the 0.8.1 cut in
[`59_completed_development_to_0.8.2.md`](59_completed_development_to_0.8.2.md),
the 0.8.1 cycle and the 0.8.0 cut in
[`51_completed_development_to_0.8.1.md`](51_completed_development_to_0.8.1.md),
the 0.7.1 and 0.7.2 release cuts in
[`41_completed_development_to_0.8.0.md`](41_completed_development_to_0.8.0.md),
the 0.7.0 cycle and the 0.7.0 cut in
[`37_completed_development_to_0.7.1.md`](37_completed_development_to_0.7.1.md),
the 0.6.0 cycle and the 0.5.0 cut in
[`35_completed_development_to_0.6.0.md`](35_completed_development_to_0.6.0.md),
everything before 0.5.0 in
[`11_completed_development_to_0.5.0.md`](11_completed_development_to_0.5.0.md).
Tier S closures do not write here (a `changes/` fragment is their record); tier M
writes one paragraph, tier L the full step format — **as a `changes/<slug>.history.md`
fragment** (design note 28 MD-4), rolled to the top of this file at release cut, so
concurrent PRs never edit the same line here. Only the release-cut block itself is
written directly, by the release manager.

---

## Release cut: **sloads 0.8.5** (correctness and tooling on the converged surface), tag `v0.8.5`, 2026-09-16

**Objective.** Close band **B6** — the first milestone worked on the one
front-end 0.8.4 left, and deliberately a *correctness* milestone rather than a
feature one: fourteen rows, no owner decision among them, chosen on 2026-09-14
when the twenty-five-row band was split four ways so that the two decisions
still owed (#164's case-set shape, #222's baseline wave) gate only the
milestone that consumes them. Its charter was the safety-factor contract's
last mile and the shipped statements that were wrong or missing, with the
tooling this milestone runs at every closure repaired first.

**Deliverables** (the `[0.8.5]` changelog section is the release note):
- **The safety-factor cluster closes (#179, #180, #177, tier M each).** The
  governing table has had an owner since M4-8; every defect in the cluster was a
  caller who never asked it. The classifier now classifies the one reference an
  exact-reference row names instead of returning outright, and a section number
  it reads must be one a family can place. **Fifteen** defaulting reads on the
  delivery side, not the two the finding named — one able to print an SF of
  zero, four turning "no factor prescribed" into a printed 1.5 — now read through
  `export.deck_format.case_sf` and render through `report.render.sf_cell`, which
  prints `N/A` where the table prescribes nothing. And `registry.register`
  stores every module's `run` wrapped in the table, so a result that has not
  been past it is not something a caller can obtain — the sweep found **five**
  surfaces running modules unstamped, the oracle report's own run point among
  them.
- **The issued document says what the calc did (#282, #254, #272, #257, #216,
  tier M each).** The user guide is a gated channel (G-OR-74 walks
  `docs/60_guide/` as prose) and its sixteen pre-OR-116 sentences are corrected;
  the non-conventional-tail withholding states what was computed, per
  arrangement; every section reads SELECT's critical set through its one owner
  (the v-tail set was enumerated twice and the governing case omitted on every
  shipped twin); all **four** reconciliations between the suite's two mass
  models are stated on the page, one of which had reached nothing at all; and
  the two estimated aileron polylines are reconciled to their entered areas so
  the report's disagreement statement has nothing to say on any shipped
  airplane.
- **The tooling this milestone ran at every closure (#280, #273, tier M; #186,
  #188, #175, #191, tier S).** The backlog tool stops destroying a defect's
  body on a word-score fold (it had done so three times); one owner per
  issue-package filename; a presence guard that every registered module has an
  oracle or closure gate (`tests/module_gates.py`, 23 rows); a red sbeam-drift
  run files a pinned issue; every `test_structural_speeds` assertion holds at
  ±0.1 % or says why it cannot; and `modules/balance.py` becomes the
  `modules/balance/` package with no import line elsewhere changed.
- **Found at the cut and fixed pre-cut (the §3 review, tier S):** the lumping
  comparison's dataclass still carried the `0.0` SF default #180 had made
  unreachable; 4.1 built #257's two reconciliation sentences twice; four tier-M
  history fragments were written as bare paragraphs rather than the bullet
  form `changes/README.md` states. Also the GUI journey's reach into a private
  Streamlit attribute, which 1.64 renamed — failed on CI, green locally — is
  replaced by the public tester API with every remaining private reach declared.
- **Version** `0.8.4` → **`0.8.5`**. Schema **v66 unchanged** — the milestone
  corrected statements and readers, not the input model.
- **Changelog cut** — `scripts/build_changelog.py 0.8.5 --date 2026-09-16 --roll`:
  **9 fragments** consumed into `## [0.8.5]`, **10 history entries** rolled to
  the top of this file, a fresh empty `[Unreleased]` opened.
- **Record roll** (`RELEASE_PROCESS.md` §4 step 3): no note moves (note 61
  CV-3). The changelog stood at 1,477 lines before the cut and would have
  crossed 1,500 with it, so it rolled in the same pass: the 0.8.3 block froze
  into [`CHANGELOG_to_0.8.3.md`](CHANGELOG_to_0.8.3.md). This file stood at
  720 lines and did not roll.
- **Gates at cut:** `pytest` **3,591 passed / 7 skipped / 2 xfailed / 0 failed**
  (3,539 at the 0.8.4 cut), `ruff` clean, `mypy` clean (`sloads/`, 108 source
  files), `scripts/smoke_test.sh` **PASS**, `scripts/backlog_issues.py check`
  clean, `scripts/branch_protection_snapshot.py --check` matches on 7 tracked
  keys, the §3.5 by-hand walk done by the owner, no open CRITICAL/MAJOR review
  findings. The **7 skips and 2 xfails are the same set as at 0.8.4**
  (§3.3): the skips are fixture-conditional — a parametrized check that a
  bundled example carries no input for states so and skips rather than
  asserting on an absent slice — and the two xfails are the SI-frame LRA
  round trips on `concept_regional_jet` and `ga6_normal`, refused by sbeam's
  dense-path condition heuristic and solving exactly in Imperial (note 55 §8's
  deferred support-node item; the test docstring states it).

**Key decisions.** *The policy had an owner all along; the defects were the
callers.* Three times in one day the deferred latent item's neighbourhood held
more than the item — #179's sweep found a second misreading in the same
classifier, #180's found fifteen defaulting reads where two were named, #177's
found five unstamped surfaces where one was — which is the standing argument
against letting a latent defect sit: the deferral is lawful, the company it
keeps is never inspected. The milestone's other decision was made at its
opening: a defect with first-order effect on shipped content outranks every
[V] row, and four rows moved from 0.9.0 into the band on that rule alone.

---

- **The backlog tool stops throwing away a defect's body: a defect folds into a table row only on an explicit pin, and no bullet with a body is collapsed onto another item's issue number (#280, tier M, 2026-09-15)** — the tool every closure in this milestone runs, corrupting the record it is supposed to keep.

  `issue_set` folded a defect bullet into a priority-table row on `_containment`, which divides shared significant words by the **smaller** title's word count. *No engine-mount case reaches the LRA deck* shares `{case, loads, index}` with *The load-case index carries no loads for 344 of 347 rows* and scores **0.60**, over the 0.5 threshold. `main` then aliased the folded title into the persisted map, and `rewrite_backlog` replaced the defect's twenty-line body with `- #209 — …`, an unrelated, already-filed issue. It happened on 2026-09-08 (`07b24e2`), was restored and struck on 2026-09-11, reproduced exactly on 2026-09-13, and — measured on the live backlog at the start of this closure — would have happened a third time on the next `rewrite`. Nothing in the path ever asked whether the fold was right, and the loss is silent: the body is restorable only because someone noticed.

  The fix is two rules that do not depend on each other. A **defect bullet folds only on an explicit `PINNED_PAIRS` entry**; the word score keeps working for detail sections, which really are longer restatements of their row and carry nothing the row does not, while a defect bullet is an independent finding with a body of its own. And `uncollapsible` — consulted by `rewrite_backlog`, not by the matcher — **refuses to collapse a bullet with a body onto a number another item's title also holds**, which is what an unpinned fold looks like from the rewriter and also what a stale key in `backlog_issue_map.json` looks like (the truncated-title drift that opened 19 duplicate issues on 2026-09-07). `issue_set` decides what is folded, `uncollapsible` decides what may be destroyed, and a body survives unless both agree. `tests/test_backlog_issues.py` asserts both against the historical pair by name, including that it still scores over the threshold: the fix is the rule, not a number that happens to separate today's titles.

  Generalising the class (practice 4) found the parser's other silent loss. `DEFECT_BULLET` matched `^- \*\*(.+?)\*\*` on one physical line, so a bullet whose bold heading wrapped onto a second line was invisible to `plan`, `create` and `rewrite` together — and two open defects with twenty-line bodies sat in that blind spot. Reading the heading across the wrap makes them visible, which raised the question of what had been keeping them unfiled: nothing but the wrap. **Unfiled by choice** is now a state the tool holds — a defect bullet whose body carries that phrase is listed by `plan`, never filed by `create`, never collapsed by `rewrite` — and the three findings the backlog states on purpose without scheduling them say so, each re-verified live at this closure: no mount condition reaches the deck (`transferred_case_loads` still takes a `BalancedCaseResult`, and `engine_applied_load` is reached only from `report/oracle_sections.py`); no hinge moment is computed for an aileron, elevator or rudder, and `AileronLoadsInput.hinges_span_in`/`actuator_span_in` are still read by `io`, `units` and `field_registry` and by no calc; and `aileron_loads` still computes the VA/VC/VD deflection schedule internally while `AileronResult` returns no deflection field.

- **The governing safety-factor table reaches its "flagged, never defaulted" promise by one path: an exact-reference row classifies the one reference it names instead of returning outright, and a section number the classifier reads must be one a family can place (#179, tier M, 2026-09-15)** — the two ways a case's FAR reference could be read as something it is not.

  `classify` carries `_EXACT`, two rows that override the section ranges because 23.367(a)(2) is an ULTIMATE case sitting inside the LIMIT flight-loads range 23.321–23.371. It was implemented as *an exact row wins outright*: a containment test that returned before the multi-reference agreement check below it. That is a larger claim than the one the rows exist to make. A reference naming a LIMIT section beside the exact ultimate one — `"23.361(a)(1) / 23.367(a)(2)"` — resolved to `engine_ultimate`, **SF 1.0**, the unconservative answer, decided by word order; the identical disagreement between two *ranged* sections was flagged and stated at 1.5. It is the one hole where the table's promise degrades to silently-first-match, and it is latent: no producer emits such a string, re-checked at this closure against every `far_reference` literal in the package. An exact row now classifies its own reference and nothing else, matched by position rather than containment — `"23.367(a)(1)/23.367(a)(2)"` names section 23.367 twice and only the second is the ultimate family, so the pair is ambiguous where a containment test would have handed (a)(1) the exact row's 1.0 — and the agreement rule is the only way out of the function, for exact and ranged references alike.

  Generalising the class (practice 4) found the classifier's other misreading, in the regex rather than the control flow. `_REF_RE` took two or three digits with nothing required after them, so a four-digit Subpart G citation was chopped: STRSPEED's `"23.1505/23.1511"` read as sections **23.150 and 23.151**, numbers no range holds and no regulation carries, and `"23.1505/23.335(b)(4)"` was reported unclassified because of the half-section invented beside its real flight-loads reference. Both strings come from `operational_implications`, the advisory placard path, which nothing stamps today — which is exactly why the shipped-fixture defaulted-case gate never saw either. A four-digit section is now simply not a Subpart C reference and is not matched at all.

  The guard for the class is independent of both regexes: `test_every_section_the_classifier_reads_is_one_a_family_can_place` walks every reference every shipped fixture produces, plus the advisory conditions the case gates do not reach, and fails naming the string if a number the classifier extracts lands in no family. `CONVENTIONS.md` §7 states both rules where it already states the flag.

- **Every reconciliation between the suite's two mass models is stated in the issued document, gated by name and by effect (#257, tier M, 2026-09-16)** — three of the four reached the Weight & Mass screen and no certification-facing page, while the entered fuselage station table they compare against sits 13–41 % under the beam the analysis actually integrates on every shipped fixture.

  The row was filed by review A4 on 2026-09-09 as "the issued document rides a station mass model short of the airplane's own item table", and asked for the entered-versus-derived totals in the report's fuselage input data and in the `fuselage_loads.bdf` header. Half of that was already history and half was still true. Plan 11 step B1 had made the item database authoritative on 2026-08-08: `fuselage_beam_stations` returns the derived table unless the project marks its entered stations an explicit override, no shipped fixture does, and the oracle projection strips the override switch anyway — so no document has ridden a short beam since. And there is no `fuselage_loads.bdf`: note 56 D-56.2 deleted the five per-component decks, and the two decks that survive, the LRA beam model and the CONM2 mass cards, are built from the item database itself through `derive_case_loadings`, so neither carries a shortfall to state. That half of the deliverable resolved to nothing to do, and is recorded here rather than left as a row somebody re-reads next milestone.

  What was still true is what the document did *not* say. 4.1 stated that the beam is derived, that the project also carries N entered stations, and that the beam and the wing account for the whole airplane. It never stated how far apart the two tables are, and a station count is not a measure of disagreement: on `ga6_normal` those five entered stations weigh 2,578 lb against the beam's 3,070, on `concept_regional_jet` nine of them weigh 18,000 lb against 30,600 — 41 % of the beam. A reader who knows the project by the table they typed had nothing on the page telling them they are reading a different airplane. 4.1 now states the gap as a weight and a share of the beam, through `mass_distribution.fuselage_reconciliation` — the same check the screen states, restated through the units owner rather than by quoting the check's Imperial diagnostic sentence beside a table in kilograms.

  The class, swept (practice 4), is *a reconciliation between the two mass models that no issued document states*, and it had four members, not one. `untagged_tail_surfaces` is stated in the same paragraph, because what it reports is a fact about that beam: `concept_heavy` tags no weight item to the fin, so whatever of the fin's mass the database holds rides the fuselage beam inside a fuselage-carried item. `wing_mass_tie` reached the CLI and the screen as the `wing_mass_tie_open` validator (design note 29 WF-4) and no document; 3.2 now states whether the itemized wing rows and the mass WINGINER distributes are one wing, which they are on all five fixtures. `tail_reconciliation` reached **nothing at all** — not the screen, not the report, only its own tests — so 5.4/6.4, which had always said "the surface's own weight is applied against it at the condition's load factor", now say which weight that is and whether it was derived or entered as an override. That sentence made one silent answer audible: `concept_heavy`'s fin has no tagged item and no entered panel weight, so its distribution is air alone — stated now as an absent inertia relief, which is the defect step B1 was made to end, rather than rendered as a weightless surface. A subsection that renders no distribution states no weight, because none was applied; the fin's spanwise loads are withheld on every arrangement (OR-133) and a withheld section states the withholding.

  Gated twice, because the two gates fail on different things. `test_every_mass_reconciliation_is_read_by_the_issued_document` parses `mass_distribution.py` for every public function whose return annotation names a `MassCheck` and requires `sloads/report/` to import it — AST-parsed, for the reason the sibling scans are: the module's own docstring names `MassCheck` in prose more often than the signatures use it. It found a fifth producer the sweep had not, which is the gate earning its place on the day it was written. `test_the_issued_document_states_every_mass_gap_it_ships_with` builds the oracle document on each of the five fixtures and requires the numbers on the page, so a check routed through a function nobody renders still fails; proved to have teeth by removing the four statements and watching all five fixtures fail.

  The fifth producer is exempted in writing rather than swept in. `case_loading_checks` compares a derived payload loading against its flight case's entered weight and CG echo — a different pair from the two mass models — and its derived branch holds the match to 1e-9 where the same module's own `CaseLoading` docstring states that a zero-ballast loading matches only within `_CG_MATCH_TOL`, 0.5 in. It therefore reports a failure on four of the five shipped fixtures that is not one, between 0.0024 and 0.0044 in, and routing it to the document today would print those false alarms on four certification documents. Underneath the noise sits one real disagreement: `baron_58`'s `aft gross` loading is at zcg 95.884 in against the 100.0 its case states, 4.12 in past that same tolerance, on a closure-locked twin whose balanced cases run on the loading and not on the echo. Both halves were invisible for one reason — the function has no caller outside its own tests, so nothing ever printed what it found. Filed with a body in the backlog's open-defects index, named in the exemption, and the exemption itself is guarded against going stale.

- **No reader on the delivery side defaults a safety factor: the five dedicated load carriers read theirs through `export.deck_format.case_sf`, a condition's is read off the condition and may be `None`, and every SF cell is rendered by `report.render.sf_cell`, which prints `N/A` where the governing table prescribed nothing (#180, tier M, 2026-09-15)** — the last place the factor policy was decided by a default rather than read from its owner.

  Review R-10 named two `getattr(item, "safety_factor", ULTIMATE_FACTOR)` fallbacks, the pattern `export.deck_format.case_sf` forbids in its own docstring ("no `getattr` fallback that would mask an attribute rename", M4-16) and `safety_factors` opens by recording the removal of. The sweep found fifteen defaulting reads, all on the delivery side: eight on dedicated load carriers in `report/oracle_sections.py`, four on `ConditionResult`s, one in `report/lumping.py`, one in `safety_factors.shared_basis_factor` itself, and one on a tail-pressure record. Two of the three sites the finding named no longer existed — `report/content.py`'s went with the front-end convergence — which is the ordinary fate of a defect filed by line number and left for five weeks; the class it belonged to had meanwhile grown.

  They are dead today, and that is the argument for removing them rather than against it: every producer mints the field, so no fallback fires, and the day one does is the day a rename has already happened and a delivered document is quietly stating a flat 1.5 — or, in the lumping comparison, an `SF` of **0.0**, a factor no regulation prescribes. The four `ConditionResult` reads were worse than dead. `float(condition.safety_factor or ULTIMATE_FACTOR)` turns `None` — the governing table's statement that a condition **prescribes no factor at all** (#154, note 48 OR-83) — into a printed `1.5`, which is exactly the false claim #154 was filed for, surviving in the one module that renders its own SF cells instead of going through `render.sf_cell`. Reproduced before the change and pinned after it: a flap condition carrying `None` printed `1.5`, and now prints `N/A`.

  Two signatures were widened to say what was already true rather than to admit a new case. `Units.load`/`load_value` take `Optional[float]`, because the factor reaching them is stated and applied nowhere (OR-116, `del sf`) — a condition that prescribes none need not invent a number to get through the unit boundary — and `_EngineCase.sf` likewise. `render._sf_cell` became public `sf_cell`: it is the one place a factor becomes text, and a section that renders its own cell is a section that can print a number where the table prescribed none. Nothing in any shipped document moves: no condition on either airframe carries `None` today, which is what made the whole class latent.

  The guard is structural and does not depend on the reviewer finding the next one (practice 3): `tests/test_safety_factors.py::test_no_factor_is_read_through_a_getattr_fallback` parses every module under `sloads/` with `ast` and fails on a three-argument `getattr` naming `safety_factor` — parsed rather than grepped, so the prose in `safety_factors` quoting the banned pattern is not mistaken for code that still does it. `CONVENTIONS.md` §7 states the rule beside the classifier's. The module docstring of `report/oracle_sections.py` was carrying a stale "known upstream oddity, filed not yet fixed" paragraph claiming #154 had not landed and that the module never prints a condition's SF; it does, in two tables, which is how the defect lived there.

- **Every runner the registry hands out stamps: `register` stores the module's `run` wrapped in the project's governing safety-factor table, so a result that has not been past the table is not something a caller can obtain (#177, tier M, 2026-09-15)** — the factor policy had an owner from M4-8 onward, and every defect left in it was a caller who never asked the owner.

  Review R-6 named one surface, the oracle GUI's per-module blocks, and one file that has since been deleted with `app/`. The sweep found that stamping lived in `registry.run_all_modules` and its reporting twin and **nowhere else**, and that five callers ran a module without them: the GUI's per-module blocks, `report/oracle_content.run_sections` — the oracle report's own single run point — `report/figures.py`'s step figures, `report/applied.py`'s engine rows behind the deck, and the fleet view's weight estimate. A sixth bypass was an import rather than a call: `report/oracle_sections.py` imported `modules.configuration.run` directly for the static-margin figure.

  What that cost was measured on all five fixtures before anything changed. Every one of them produces **thirty to fifty** conditions that state no load — a Mach limit, a structural speed, a configuration summary, a weight envelope point — and `ConditionResult.safety_factor` defaults to `ULTIMATE_FACTOR`, so on the unstamped surfaces each of them printed a flat `1.5` where the stamped path states `N/A`. That is #154's false claim, the one #180 had just finished removing from the render side, surviving on the document the certification reader actually receives. The override half stayed latent only because no shipped fixture carries an override — but "an override is silently not honoured" is the one thing the G-11 mitigations promise never happens, and it was happening on every surface but two.

  The fix is not five stamps. `registry.register` stores `_stamping(fn)`, so `get(name)`, `run_all_modules` and a direct `_REGISTRY` read all yield a runner that has applied the table; the two run-everything helpers dropped the trailing `stamp()` they used to be the sole custodians of, and the static-margin figure goes through `get("configuration")` like everything else. Stamping is idempotent — the table is a pure function of the project — so `report.content`, which stamps its own assembled groups, is not fighting it.

  Making it structural forced a disagreement the two surfaces had been keeping apart. `modules/tail_span.py` hardwired `far_reference="23.421"` on every derived spanwise condition while inheriting the parent case's factor, and that field is what `safety_factors.classify` reads. Fifteen of the nineteen conditions came out right by coincidence, `control_system` being 1.5 as well; the two derived from the **23.367(a)(2)** engine-failure case arrived already ULTIMATE at SF 1.0 and were classified into a limit family, so on `baron_58` and `atr42_100` the case index and the deck stated 1.5 for a case the oracle report stated 1.0 for. `case_ref` has carried the true reference all along — TAILDIST's spec has stated that rule since its own hardcoded `23.421` was removed — so the condition now names its case, the producer and the table agree everywhere, and the two cases state SF 1.0 with the `-ULT` marker the regulation prescribes them (owner's call, 2026-09-15). Fifteen references stop claiming to be control-surface loads they are not. The Imperial baseline was regenerated for that and only that: on both twins the `tail_span` CSV and text now state `23.367(a)(2)`, `SF 1`, and the `-ULT` marker on the two cases, and no other channel of any fixture moved a byte.

  Four guards, in `tests/test_safety_factors.py`. `test_no_module_runner_is_reachable_unstamped` asserts both halves of the rule — that every entry in the registry carries the wrapper, and, by an `ast` walk of `sloads/`, that no module's `run` is imported directly outside `sloads/modules/`, which is the one way back to an unstamped result. The other three pin the behaviour the structure is for: a single runner honours a project override, states `None` where the table prescribes no factor, and a derived spanwise condition names its own case. `CONVENTIONS.md` §7 and the TAILSPAN section of `PROGRAM_SPEC.md` state the rules beside the classifier's.

- **Every section of the oracle report reads SELECT's critical set through its one owner, gated by name and by effect (#272, tier M, 2026-09-16)** — two consumers still called `build_critical` directly, and note 44 OR-172's admission of the 23.367 fin conditions lives between that search and `default_critical`, so either of them could enumerate the set without its governing case.

  The row was filed from note 58's ranking-site sweep on 2026-09-11 against the summary report, whose v-tail governing table and chordwise table disagreed about the condition set in one section. That report was deleted with `app/` at #270. The 2026-09-14 re-cut checked whether the class had gone with it, found the oracle report still calling `build_critical` at one section and `default_critical` at another, and moved the row into 0.8.5 under rule 6. That was the right call for the wrong pair: the surviving `build_critical` site is §3.2's wing selection register, and the conditions OR-172 admits are `component="vtail"`, so the two routes cannot disagree there today. Measured before anything was changed — on all five shipped fixtures the h-tail and v-tail condition register, aerodynamic state, critical-loads, chordwise and spanwise tables and Appendix E already name one set each, and `build_critical` and `default_critical` differ in the fin's rows and nowhere else.

  Latent is not fixed, and §3.2 is the reason. It tells the reader in as many words that its cases are "the same cases the summary, the distributions and the station-by-station appendix state — one set, projected four ways", which is a claim about every section of the document and is asserted by a route free to disagree with the one the other sections take. The second consumer, `report/content.component_loads`, carried the bypass with a docstring explaining that it recomputes live "exactly as the Critical Loads and Results Review pages do" — pages that went with `app/` at #270. The comment outlived the reason for it by a milestone, and the function now has no caller outside the test suite at all.

  Both read `select.default_critical` now: the persisted set when the project carries one, else the search run fresh, which is the same route §4, §5, §6, `taildist` and `tail_span` have always taken. No shipped byte moves — the oracle document is content-identical on all five fixtures — and no baseline was regenerated.

  Gated twice, deliberately, because the two gates fail on different things. `test_no_calc_code_calls_build_critical_outside_the_owner` parses `sloads/` for an import or a call of the search and allows one file, the owner, with its reason stated; it is a sibling of the `project.envelope` scan already in that file, which covers the other way past the same owner, and it is AST-based for the same reason — this class is discussed in prose far more often than it is used, and the module docstring alone would trip a regex four times. Proved backwards on the retired shape: two hits on the code that was there, none on a file that only names it in prose. `test_every_case_keyed_table_in_the_section_names_the_same_conditions` asks the finished document instead, requiring every case-keyed table in Sections 5 and 6 and their appendices to name the same case ids, so a second enumeration that is not spelled `build_critical` — a cached list, a filtered persisted set, a second search — is caught by its effect. Its companion asserts the 23.367 rows reach all of those tables on both twins, because a set-agreement gate that ran only on single-engine fixtures would pass while agreeing on the wrong set. Both were shown to have teeth by re-introducing the bypass on the tail route: the condition register drops to four rows while the chordwise table beside it keeps ten, which is the two-tables-disagree shape the row was filed for, printed.

  The withheld half of the row's own deliverable is worth stating: `report/tables.py` and `modules/body_loads.py` still read `project.envelope.critical` directly, and both keep their existing exemptions — the case index renders what the project carries rather than computing loads, and `_critical_fuselage` is a documented narrow variant that takes fuselage conditions through `select_fuselage` so a body deck does not require well-formed tail inputs. Neither is a persisted-else-compute decision, which is the rule the owner owns.

- **One owner per issue-package filename, and G-12's inertia notes reach the delivered file (#273, tier M, 2026-09-14)** — the #16 sweep's residue, closed as two slices of one defect class: a thing written in the code and not delivered where it was meant to be.

  `io.py` owns every path the issue package needs (OR-28/OR-30), and `report/oracle_package.py` was respelling two of them as its own string literals — `PACKAGE_SPEC`/`PACKAGE_BUILD` beside `REPORT_SPEC_FILENAME`/`BUILD_STAMP_FILENAME`, two constant pairs naming one file each. That is the duplicated-owner class practice 3 exists to prevent, and its failure is silent: a rename in the owner that left the second spelling alone would split the package in two without failing anything at the rename site. The two now *are* the owner's names, cited in both directions, and `tests/test_oracle_report_package.py::test_the_package_filenames_have_one_owner` asserts identity rather than equality — two literals that happen to match today are exactly the state this closes.

  `gear_loads.LEG_WEIGHT_UNSET_NOTE` and `UNSPRUNG_NOTE` were public, in `__all__`, cited from three docstrings — one of which says the first is "stated in-band on every surface that renders it" — and neither reached a byte of any delivered file. The gear load report is the only surface that renders the inertia term, so it is the surface that owed them. Its header block now states the unsprung limit unconditionally, because the number is in every row, and explains every blank inertia cell. Writing that explanation found the second half: a blank cell has **two** unrelated causes, and the note as filed would have been wrong on whichever rows it did not mean. No leg weight was entered, so the free body is shown open (G-12a) — or the case is the 23.499 supplementary nose-wheel family, whose airplane vertical load factor is zero, which blanks the cell on a leg that *is* weighed. On the shipped `ga6_normal` fixture every leg is weighed and nine rows are blank for the second reason, so a single merged note would have told that reader a weight is missing where none is. `NO_AIRPLANE_INERTIA_NOTE` is the second cause's delivered half — the code comment that carried it is now the note's citation — and each conditional note prints only when the file contains the rows it explains. `tests/test_gear_report.py::test_the_g12_inertia_notes_reach_the_delivered_file` asserts on the rendered text and not on the constants: the defect was that the constants existed and the text did not.

  `_GEAR_REPORT_NOTES` became `_GEAR_REPORT_FRAMES`, the fixed opening of a block `_gear_report_notes` now assembles (`CONVENTIONS.md` §7's two-frames row follows the rename). The `#`-wrapper that builds a note block moved from `report/oracle_sections._csv_note` — private, and already being reached for across modules by name — to `csv_text.note_block`, beside the line ending and for the same reason: the shape of a delivered CSV's text has one owner. Four Imperial baseline digests regenerate, all of them the `gear_report` channel.

- **Every shipped control surface is drawn over the area its loads were run on: the two estimated aileron polylines are reconciled to their entered areas, and the report's disagreement statement now has nothing to say on any shipped airplane (#216, tier M, 2026-09-16)** — two entered numbers had described one surface, 4 % and 44 % apart, and the wider of the two was not even drawn on the wing it was cut into.

  OR-152 settled in September that the pressure has one owner — the module — and that a drawn outline is a locator, never a divisor: where the entered analysis area and the entered planform outline disagree by more than 2 %, the section states the discrepancy rather than resolving it silently. That ruling deliberately left the data question open, and this is it. Three of the four examples then shipped disagreed; `cessna_210` retired at #264 with its +5 %, and what was left was `baron_58` at −3.9 % and `concept_regional_jet` at −43.6 % against entered areas of 7.600 and 15.0 sq ft. `ga6_normal`, whose aileron and flap both come from Appendix A's own figures, agrees to 0.2 % and is untouched.

  Which of the two numbers is the airplane was decided per example, from that airplane's own data, and it came out the same way on both. The entered area is what every pinned load and pressure divides by, and is as old as the fixture; the outlines are the estimated polylines `PROGRAM_SPEC` already named as awaiting the #260/D-54.6 wave — and the jet's was estimated badly enough to fail the physical fact D-54.1 rests on, its trailing edge sitting **9.4 in** off the wing trailing edge it is supposed to *be*. So both outlines were redrawn on the wing's own trailing edge with their inboard station solved for the entered area: `baron_58` from BL 130 to **BL 127.0**, holding the 25.0 %-chord hinge line its own polyline already traced, enclosing 7.608 against 7.600 sq ft; `concept_regional_jet` from BL 300 to **BL 257.2** at 0.30 chord — the only wing-control chord fraction that project enters, its flap's — enclosing 14.99 against 15.0. Both are now inside 0.2 %, and the furthest any shipped wing control sits off its parent's trailing edge is 0.04 in, so `validate_control_trailing_edge` would pass all four today; extending the hard refusal from the tail groups to the wing controls is left as the one-line change it now is, for the wave that owns their geometry.

  No load moved, no pressure moved, no deck row and no case-index row moved. What moved is the aileron's own published planform, in WING_GEOMETRY on those two airplanes and nowhere else: `baron_58` 1052 → 1096 in² with its span 80 → 83 in, `concept_regional_jet` 1218 → 2159 in² with its span 84 → 126.8 in, plus each MAC and MAC station. Two channels on two of five examples — the Imperial digests were regenerated for exactly that, which is the milestone's one baseline movement before the wave in 0.8.6.

  The flap half of the row is closed the other way, deliberately. `baron_58` and `concept_regional_jet` carry a `flap_loads` slice and draw no flap, and no flap outline exists anywhere in either project — so drawing one is invention rather than reconciliation, which is the line T-17 holds and which OR-153 already answered by rendering the stated absence instead of an empty axis. The jet supplies the second reason: its entered 55 sq ft is 1.3–1.4× the 38–42 sq ft a stowed 30 %-chord flap encloses over the span its wing leaves between the fuselage and the reconciled aileron, which is what a Fowler flap's extended area looks like rather than a defect — so a stowed outline drawn beside it would print a permanent 2 %-rule disagreement about nothing.

  Fixing the fixtures removed both of G-OR-98's and G-OR-99's exercisers, which is the ordinary hazard of a gate pinned to a fixture being wrong: the under sense of the disagreement had just lost its two airplanes the way the over sense lost `cessna_210`, and the gates would have gone on passing while asserting nothing. Both now contradict a shipped outline in memory — `_outline_scaled` scales one drawn chord about its trailing edge and touches nothing the analysis reads — so the entered area, the load and the pressure stay the shipped airplane's and what is tested is the document's response to an outline that disagrees. That restores the over sense as well, and `test_every_shipped_outline_encloses_the_area_its_loads_were_run_on` holds the reconciliation itself, since the report would otherwise go on stating, correctly, that an airplane disagrees with itself.

- **The user guide is a gated channel: G-OR-74 walks `docs/60_guide/` as prose, and the sixteen sentences that still taught the pre-OR-116 contract are corrected (#282, tier M, 2026-09-15)** — the guide is the document that teaches the contract, and it was the last channel asserting it with no owner.

  `03_conventions.md` §"LIMIT and ULTIMATE" stated *"Every deliverable load is ULTIMATE. The factor is applied exactly once, at the render/export boundary"* — the rule note 49 OR-116 inverted — and it stated it for the whole of the milestone that removed the multiply. Twelve chapters repeated it in their *Results* sections, each naming its blocks' basis as `(ULTIMATE, -ULT units, SF stated)`; two *Common mistakes* entries told the reader to divide a figure by its SF before comparing with the book, and one told them the two wing blocks "differ by exactly the safety factor". They do not differ at all. Every numeric gate was green throughout, for the reason G-OR-73 and G-OR-74 were each written down: nothing read the prose.

  The sweep is a read, not a `sed`. Twenty-four uses of the word across sixteen files went in and eight came out, and the eight that survive are the true ones: the two families 14 CFR defines at ultimate, and the blocks that are not loads at all (geometry, mass properties, speeds and load factors, which prescribe no factor and print `N/A`). What each chapter may claim was checked against the code rather than against the neighbouring chapter — every module run on both worked examples, its conditions' stamped factors and unit markers tabulated — which is how the guide now says that the only `-ULT` a reader will ever meet is 23.367(a)(2), in One Engine Out and, on a twin, in the two v-tail rows Tail Loads acquired at #177. 23.561(b) is the contract's other prescribed-ultimate family and no module in the suite produces it.

  `03_conventions.md` no longer restates the contract: it points at `CONVENTIONS.md` §3, its owner, and keeps only what a user needs — that every delivered load is limit, that the `SF` column states the factor the sizing step applies, that `N/A` is a statement and not a missing number, and where the two already-ultimate cases live.

  The gate is the point. `assert_states_limit` now walks every Markdown file under `docs/60_guide/`, on the same terms as the GUI sweep: static text, read at the source, so no chapter escapes by being one nobody opens. Extending it cost four new claim shapes, and the two that matter say something about the checker. A chapter states a block's basis in a **parenthetical with no verb in it** — `(ULTIMATE, -ULT units, SF stated)` — and every pattern written until now was built around a verb, so the gate read past the guide's most common assertion fifteen times over. And `LIMIT × 1.5`, written in the deliverable's own capitals, read straight past an ASCII-lowercase `limit x` pattern: the normaliser folds typography but not case. Both were checked backwards — each of the fifteen retired sentences is asserted to fail the gate — because a pattern that catches nothing is a gate that passes for the wrong reason.

  Nothing was regenerated: `docs/60_guide/_generated/` is field tables from `field_registry.py` and carries no basis prose, so the generator needed no edit and G-UG-2 stayed green.

- **The oracle report's non-conventional-tail withholding says what the calc
  actually did, per arrangement, and is gated against it (#254, tier M,
  2026-09-16)** — the statement had claimed the horizontal tail's load path
  through the fin "is not modelled" since note 44 OR-133 agreed that wording on
  2026-09-07. Plan 09's T7 then put the horizontal tail's concurrent set on a
  T-tail's fin tip, and the sentence was never re-read: on every T-tail the
  report went on saying the path was unmodelled while `tail_span` was modelling
  it, so the document and the calc disagreed about what the suite can do. The
  2026-09-09 review caught it as review item A1; note 56 narrowed it on
  2026-09-12, when the spanwise fin deck that carried the lumped transfer was
  deleted and the question survived against the LRA model's fin-tip joint alone.

  What the calc does was measured rather than inferred. On both shipped T-tails
  the four fin conditions that name a V-n point carry a tip set — `atr42_100`
  Fz +258 lb / Myy +21,820 lb-in on three of them and −994 lb / −38,502 lb-in on
  the fourth — and `atr42_100`'s four engine-out rows name no V-n point, so they
  pair with no concurrent horizontal-tail load and carry nothing. A cruciform or
  V-tail transfers nothing at all: `ttail_transfer` is gated on `is_t_tail`, not
  on "non-conventional". Three different answers were being printed as one.

  So the wording is now three statements read off one owner. A T-tail says the
  fin-tip transfer *is* modelled, that what it carries is the surface's symmetric
  concurrent set, and that the conditions it is carried in are the ones sideslip
  and rudder deflection load asymmetrically; a V-tail or cruciform says no part
  of the path is carried; and neither claims every condition transfers, because
  the engine-out rows do not. The predicate is `is_t_tail` — the same owner
  `modules/tail_span.py` gates the transfer on — rather than a second reading of
  the field, so the document cannot describe a load path the calc resolved
  differently. Section 5's pointer, which restated the claim in miniature, drops
  it and points.

  **The withholding itself does not move, and never rested on the transfer.** The
  fin's spanwise loads are withheld because 23.427(a)'s unsymmetrical case is
  absent from the set entirely — an omitted condition, not an understated one —
  and because the asymmetry inside the four conditions that are analysed is worth
  27 to 73 per cent of the governing fin case's own root bending (note 51). Both
  are as true on a T-tail with a symmetric tip transfer as they were without one.
  What changes is that 6.5 now says it is a policy, quantified, rather than
  offering a false statement about the model as the reason.

  G-OR-87 is re-cut around the drift rather than around the wording: the new
  `test_the_withholdings_reason_matches_what_the_calc_modelled` asks
  `build_tail_span` for the transfer on every `TailType` and decides from that
  which sentence 6.5 is allowed to print, so the next arrangement to acquire a
  transfer moves the prose or fails. A rewording alone would have drifted back
  the same way this one did. The existing G-OR-87 diff is untouched: it still
  runs `CONVENTIONAL` against `CRUCIFORM`, the arrangement the report reads and
  nothing else does.

  The three standing restatements of the retired claim went with it —
  `CONVENTIONS.md` §7's tail-arrangement row, which contradicted itself inside
  one sentence by naming the T7 transfer and then calling the path unmodelled;
  `TailType`'s docstring; and `theory_sources.md`'s `taildist` row — and
  `ORACLE_REPORT.md` carries the per-arrangement rule and the re-cut gate. No
  delivered number moved: this closure is prose, one predicate and one test.

## Release cut: **sloads 0.8.4** (the two front-ends converge on one), tag `v0.8.4`, 2026-09-14

**Objective.** Close band **B5**. The suite had grown **two** Streamlit
front-ends over the same calc package — `app/Home.py` with 21 `app/views/`
pages, and the oracle GUI derived from `workflow.py` — and every cross-cutting
change was being paid twice, in two dialects, with the two disagreeing about
what the program does. Design note **57** ruled that one survives and named the
rule that made the removal safe: **D-57.8, the survivor is complete before
anything is removed.** Design note **60**, written immediately after the 0.8.3
cut, amended it with what a page-level audit could not see — the retiring
front-end carried **twenty** figures, not the four D-57.4 named, and
`app/views/export_report.py` was the only production consumer of
`content.build_report`, so retiring the pages would have retired the **summary
report** without naming it. The milestone is therefore mostly *port*, and the
deletion is its last step rather than its first.

**Deliverables** (the `[0.8.4]` changelog section is the release note):
- **One front-end (#270, note 57 D-57.1 + D-57.6, tier L).** `app/views/` and
  `app/Home.py` deleted — **22 pages, 8,461 lines** — with
  `content.build_report`, the summary report's LaTeX path, `report/bundle.py`
  and the `.xlsx` workbook. The page set is `workflow.gui_pages()`: the fourteen
  derived analysis steps plus three declared non-step pages, so a page cannot be
  added to the GUI without being a step or declaring itself an exception.
- **Twenty figures port under one owner (#267, note 60 D-60.1…D-60.6, tier L).**
  `sloads/report/figures.py` is the figure catalogue — one row per *family*,
  naming the page, the producer and whether it is pre-run or post-run;
  `app_shell/plots.py` renders a `PlotData` as Plotly and is a **peer** of
  `plots_tex`'s TikZ over the same producers, with a guard walking the GUI trees
  for a `PlotData` or `Series` constructor so the GUI derives no figure data of
  its own. Nineteen producers became callable per figure, which is the use the
  port was asked for: checking an input before running the whole process.
- **The fleet comparison ports and stops owning anything (#268, D-57.5, tier M).**
  Phase C's *assess against similar airplanes* is now `oracle_app/fleet.py`,
  marked ✦ as an sloads extension and registered on the navigation only. The
  reference fleet moved to `sloads/data/` (a `pip install sloads` had carried no
  fleet to compare against) and the subject's priority chain moved into
  `sloads.fleet` — where gate DG-3 caught it integrating the wing planform
  itself, a fifth owner invisible to the guard while it lived in `app/`.
- **The survivor completed before the removal (#266, #269, #245, the report
  merge, tier M each).** Every input field rendered, in two marked tiers; the
  weight data base's seed button adds rather than replaces (closing **#78**);
  the issue package's `data/` becomes the one tabular channel, with the
  per-module downloads and the results zip retired against a column inventory
  that is a test rather than a one-pass check; and the summary report's
  cross-cutting sections — the axis statement and the FAR 23 Subpart C coverage
  matrix — merge into the oracle report **before** `build_report` goes, so the
  document that ships is the one that carries them.
- **The delivered files say which case and which frame (#241, #242, tier M each).**
  A row's case was named by its *description*, and a description is not an
  identity — LANDLOAD's 33 ground conditions share eight of them, and a twin's
  two engine mounts published six conditions under three strings; `case_ids.index_case_id`
  is now the one owner of the suffixes. Every delivered file states the frame
  its numbers are in, `MyyAxis` becomes `TorsionAxis` because the fin's torsion
  is `Mz`, and the AXES stanza's **+Mx and +Mz were backwards on every file**.
- **The record corpus splits by function (note 61, tier M).** Design notes leave
  the status-driven move behind and are filed in `25_notes/` from the day they
  are written; `90_record/` leaves the default search path; a tier-M/L closure
  writes **one** fragment whose changelog bullet is derived from its lead phrase.
  This cut is the first run of that rule.
- **The end-of-milestone sweep (note 57 §6/§8, tier S).** The `app_shell/`
  slimming removed the five names the deletion left unreachable — the three
  `*_limit_csv` writers, whose only callers were the deleted pages once #245
  settled `data/`, and the whole of `optional_slice`, whose Apply-button form of
  the #143 rule has no Apply step left to serve (the rule survives at
  `oracle_app/form.py`'s named gestures, and `CONVENTIONS.md` §7 now points
  there). Around forty statements in the code that still described two
  front-ends are re-cut, and the **release-state sentence** stops naming a GUI
  that does not exist. **R-57.5's rename executes as nothing:** the ruling took
  the branch where the name and the `sloads-oracle` entry point stand, and the
  milestone changed the *argument* for a rename, not the decision — if it is
  taken up it is its own row with its own deprecation of the console script.
- **Found at the cut and fixed pre-cut (the §3.5 read):** the Tail Loads
  advisory sent readers to a **Tail Span Loads** page #270 had deleted, and its
  guard pinned the wording rather than the rule, so it passed over a caption
  pointing at nothing. The advisory now names the report's *Spanwise loads*
  subsections and the export decks, and the guard asserts that no caption names
  a step absent from `workflow.gui_pages()`. `README.md`'s layout tree, which
  still drew `sloads/report.py` and `sloads/models.py` as modules, went with it.
- **Version** `0.8.3` → **`0.8.4`**. Schema **v66 unchanged** — the milestone
  moved front-ends, not the input model.
- **Changelog cut** — `scripts/build_changelog.py 0.8.4 --date 2026-09-14 --roll`:
  **16 fragments** consumed into `## [0.8.4]`, **11 history entries** rolled to
  the top of this file, a fresh empty `[Unreleased]` opened.
- **Record roll** (`RELEASE_PROCESS.md` §4 step 3, amended by note 61): **no
  note moves** — CV-3 retired that step, and a note's Status line is what
  changes when its work ships. Both live record files were over the
  **1,500-line** threshold, so both rolled in the one pass: everything below the
  0.8.3 cut block froze into
  [`62_completed_development_to_0.8.3.md`](62_completed_development_to_0.8.3.md),
  and the changelog's blocks older than 0.8.3 into
  [`CHANGELOG_to_0.8.2.md`](CHANGELOG_to_0.8.2.md) — the first run of CV-5, and
  the reason the changelog had reached 11,249 lines.
- **Gates at cut:** `pytest` **3,539 passed / 7 skipped / 2 xfailed / 0 failed**
  (3,422 at the 0.8.3 cut), `ruff` clean, `mypy` clean (`sloads/`, 100 source
  files), `scripts/smoke_test.sh` **PASS** (the one GUI boots through the
  `sloads-oracle` console script, CLI CSV checked), `scripts/backlog_issues.py check`
  clean, `scripts/branch_protection_snapshot.py --check` matches on 7 tracked
  keys, the §3.5 by-hand walk done by the owner, no open CRITICAL/MAJOR review
  findings.

**Key decisions.** *Two implementations of one thing do not cost twice the
effort — they cost the ability to say what the program does.* The measured
saving from converging was **one** tier-S row of duplicated work, and that was
never the case for it: it was that a shipped statement had two owners, so the
GUI could describe a capability the other GUI had and this one did not, and no
gate could tell. The milestone's real deliverable is that there is now one
answer to every question a reader asks of the interface.

*Complete the survivor first, and the deletion becomes arithmetic.* D-57.8 is
why #270 is one commit at the end of a milestone rather than a fortnight of
regressions: by the time the pages went, everything they did was already done
somewhere the surviving GUI could reach. Note 60 is what that rule looks like
when it is enforced honestly — the audit that produced D-57.4's four figures was
wrong by a factor of five, and the correction cost two rows and a re-tier rather
than a shipped gap.

*A guard that pins wording outlives the thing it was guarding.* The Tail Loads
caption named a page that had been deleted, and its test passed the whole time
because it asserted the caption's *text*. The re-aimed guard asserts the
property — no caption names a step the GUI has no page for — which is the same
correction the milestone made to the figure catalogue and to `CONVENTIONS.md`
§7: state the rule at an owner, not the instance at a copy.

**Band B5 retired with the cut; band B6 (0.8.5 — the defect and polish cleanup,
on the converged surface) is the milestone in flight.**

- **The applied-load CSVs state their case identity (#241, 2026-09-08 review §4,
  tier M, 2026-09-13)** — the six delivered applied-load files named each row's
  case by its *description*, and a description is not an identity. LANDLOAD's 33
  ground conditions share eight of them — one description, three loadings, three
  different sets of wheel reactions — so the gear file delivered 33 cases a
  reader could separate into eight groups and no further, and the Baron's two
  `CONTINENTAL IO-550-C` mounts published six conditions under three strings. The
  id that would have settled it, `AppliedLoad.case_id`, was populated on every
  row by every producer and emitted by none; the report's own applied appendix
  printed it while the file beside it did not, so the page and the file were not
  in fact the same row. All six files now lead with `Case ID`, `Case` and
  `Loading`: the minted id the load-case index is keyed by, the description, and
  the named CG the case was computed at (blank where the case names none, never
  guessed). The two identity strings are read off the case's own `CaseRef` by one
  owner, `report/applied.case_identity`, rather than by each of the five
  producers spelling the read for itself, and the header block of every file says
  what the three columns are and that `Case` is not unique. The twin's half of
  the finding was not a file defect at all: the per-engine tag was the engine
  *designation*, which two engines of one model share, and it was applied to the
  title *after* the `CaseRef` was minted — so the index itself described `EM-01`
  and `EM-04` in the same words. `modules/engine.engine_tags` now mints one
  distinct label per installation — the designation where it already separates
  them, plus the side (off the engine's own butt line) where it does not, plus
  the engine's position in the rare case that still collides — and the tag goes
  on before the id is minted. Nothing renames on an installation whose engines
  differ, so no single-engine title in any shipped example moved. A delivered id
  the index lists under a shorter name now joins through one owner too,
  `case_ids.index_case_id`: a handed twin (`W-05R`) and the 23.371(b) gyro
  condition's four sign combinations (`EM-06a…d`, which one `ConditionResult`
  cannot carry four `CaseRef`s for, Step D1) are suffixes on an id that *is*
  listed, and `report/render`'s minter reads the same suffix alphabet that strip
  removes. Guarded by `tests/test_applied_case_identity.py`: the round trip —
  every delivered `Case ID`, on every bundled example and all six components, is
  an id the case index names, and every `Loading` cell is that index row's own
  `CG` — plus the two collapses asserted directly (33 ids under 8 descriptions;
  six mounts under six), the gyro suffix stated rather than tolerated, and an AST
  walk of `report/applied.py` that fails any `AppliedLoad` construction which
  does not state its identity, so a producer added later cannot half-fill the
  columns. The Imperial baseline gained the gear and engine applied channels in
  the same change: four of the six were digested and two were not, which is how
  the bytes of the file with the most cases in it came to move unguarded. Every
  digest that moved is one of those six files, the engine module's own CSV/text
  output on the three multi-engine examples, and their case index.

- **The delivered files start saying which way their axes point, and stop
  stating zeros their own rows fill (#242, 2026-09-08 review C2+C3+C4, tier M,
  2026-09-13)** — the review checked the CSVs against the requirement they exist
  to serve, found the *data* airplane-global and frame-correct throughout, and
  found the *self-description* missing the one sentence a forwarded file cannot
  do without: nothing anywhere said that `x` is the fuselage station positive
  aft. Note 56 narrowed the finding on its way here — the deck-companion span,
  chordwise and fitting CSVs it also covered went with their decks, and with
  them `tail_chordwise.csv`'s second meaning of `Axis` and
  `control_surface_loads.csv`'s `Fz`-on-a-lateral-normal — so what was left was
  the report's own set and the two halves of C3 that had survived into it. The
  fix is one stanza in the methods stamp, because the stamp is the single
  statement every channel already wraps (G8-3), and the axis words live in
  `export/coordinates` rather than in the stamp, because `CONVENTIONS.md` §1
  already names that module the single edit-point for the map and a sentence
  that is not beside the thing it describes is a sentence that outlives it. Two
  exceptions are declared rather than papered over: the gear report carries the
  manual's ground-line frame in three of its columns and airplane axes in every
  other, and says so in its own block; and the applied files' torsion-axis
  column was renamed `TorsionAxis` because the fin's torsion is `Mz` and a
  column asserting `Myy` was, on one of six files, exactly the class of claim
  the issue was filed about. Working the file set turned up the same defect from
  the direction prose cannot defend itself in: note 56 D-56.9 had re-aggregated
  the delivered rows onto the LRA grids, where each load carries the lever-arm
  couple of its own offset, and the hand-written structural-zero blocks — the
  numbers having moved and the sentences not — were declaring `Mx`, `My` or `Mz`
  zero "throughout" on four of the six files while the rows beside them were
  filled. So OR-140's apparatus was split: whether a column is zero is now
  **measured** from the rows being written, the prose supplies only the reason,
  a zero that belongs to this configuration rather than to the model is stated
  as that, and a file at grids says it is at grids. C4's riders were taken where
  they were the same defect class — the V-n file now carries the two table notes
  that define five of its nineteen columns, read off the `Table` objects the
  appendix renders so the two cannot drift, and `sloads/csv_text.py` owns the
  line terminator that every stamped file used to mix — and left where they were
  not: the `lbf`/`psi` display vocabulary lives entirely in `app/views/`, which
  #270 deletes, and the `N·m` middot is an encoding decision (a UTF-8 BOM, or an
  ASCII-ised SI vocabulary) that moves the whole SI channel and wants an owner
  ruling rather than a rider on an axis stanza. Guarded by
  `tests/test_delivered_frame_statement.py`: every stamped channel states all
  three axes and their senses; the axis words appear in no second place under
  `sloads/`; the stanza is identical on two different airplanes; the gear
  report places every one of its frame-bearing columns on one side of the split,
  checked against the field list so a column added later fails rather than
  passes; no applied file claims a zero its own rows fill and no reason outlives
  its column, over every bundled example and all six components; a file at grids
  says so and one that is not does not; and no delivered channel, decks
  included, contains a carriage return.

## Step — One front-end (#270, design note 57 D-57.1 + D-57.6, tier L, 2026-09-13)

**Objective.** End the two-front-end drift class by deleting the front-end the
mission bar does not need, after — and only after — everything worth keeping had
been ported into the one that survives. Note 57's §1.4/§1.5 priced the
alternative: hardening `app/views/` through the 0.9.0 band buys maintenance on a
surface whose every capability duplicates a surviving owner, while the drift
class is structural for as long as two front-ends exist. D-57.8's rule governed
the sequence and was honoured to the letter — #265 through #269 built the
survivor's editor, field tiers, plots, fleet page and seed button, and #278
merged the summary report's cross-cutting sections into the surviving document
— so this step removes and re-cuts, and adds no capability.

**Deliverables.** `app/` deleted: `Home.py` and 21 `views/*.py`, 8,461 lines.
With it, the artifacts whose only consumer it was: `content.build_report` and
its nine section builders, `latex.render_document`/`render_report` and the
document furniture (title page, running heads), `report/bundle.py`,
`export/workbook.py` and the `openpyxl` dependency. `content.py` falls from
2,639 lines to 653 — the content model (`Section`, `Table`, `Figure`,
`PlotData`, `Units`, `ComponentLoads`) plus the three plot-data producers the
document and the GUI both draw from — and `latex.py` becomes the emitters
`oracle_latex.py` assembles a document from. `workflow.py` gains `GuiPage`,
`NON_STEP_PAGES` and `gui_pages()`; `Oracle.py` builds its navigation from that
declaration and names no page set of its own. `validation.PAGE_EXPORT` becomes
`PAGE_REPORT` and its five checks re-point at the page that writes the
deliverable. `cli.py --report` renders the surviving document, `cli._load` gives
every route the one error contract, and `report/methods.py`'s channel sentence
names the surviving human channels.

**Test.** Note 57 §4's eight gates, each asserted rather than asserted-about.
**No load moves** (gate 1): the Appendix A oracles, twin closure suites, report
baselines and every delivered CSV are untouched — this step edits no calc
module. **A project the retired GUI saved opens here** (gate 2, OG-13 widened):
`test_oracle_gui.py` reverses the G6 round-trip, driving every bundled example's
full unreduced project through all fourteen pages, because the question a user
has is not whether two peers can read each other's files but whether the file
they already saved still opens. **`_GUI_TREES` covers the survivor whole** (5)
and **exactly one `st.set_page_config`** (6) hold unchanged over one tree. **The
no-edit journey** (7): `test_gui_journey.py` is re-aimed at the surviving
renderer, and its `KNOWN_OPEN` list is **empty and asserted empty** — it carried
five #148 diffs that the `app/views/` freeze forbade fixing, all of them
properties of a page that rebuilds its slice from its own widgets, which is what
a hand-written view does and a generic renderer over the field registry does
not. **No retired page is reachable** (8): `gui_pages()`, the navigation and the
workflow guards agree, and ruff/mypy leave no import edge. Six test files were
deleted with the pages they drove and fourteen re-aimed; three guards that read
`app/views/*.py` sources were re-cut to sweep the surviving display trees rather
than name files, because a surface that is not on a list is a surface the guard
does not reach.

**Key decisions.**

- **The page set stays derived and states its exceptions.** D-57.1 widened the
  rule from `oracle_steps()` to a stated set; the implementation makes the
  stated half a declaration with a reason per row (`NON_STEP_PAGES`) rather than
  three hand-appended blocks in the entry point. Gate G2's claim — *there is no
  page list* — then covers the whole page set instead of the derived part of it.
- **`PHASES` shrinks to four.** `Start`, `Load-case plotting` and `Export` held
  the six GUI-only steps and nothing else. Keeping them would leave three phases
  no step can ever be in, which is drift with a name; what they described did
  not retire with them — the project is carried by the shell, the figures are
  drawn on the pages that produce them (#267), and the deliverables leave through
  the CLI and the Report page — but none of those is a step of the analysis,
  which is what the tuple partitions.
- **Two analysis steps keep no page.** `tail_span_loads` and `balanced_cases`
  run registered calc modules whose deliverables are the report's tail-span
  appendix and the balanced deck. `STEPS` is what the suite does, not what the
  GUI shows, and saying so in the module docstring was cheaper than folding two
  real steps into a mapping built for contributors.
- **The audit outlives its subject.** `front_sections.SUMMARY_DISPOSITION` was
  written at #278 saying it would retire with `content.py`. It does not:
  `content.SECTIONS` moved beside it as `RETIRED_SUMMARY_SECTIONS`, because an
  accounting whose subject has been deleted accounts for nothing, and note 60's
  gate 12 would have stopped being enforced at exactly the commit that made it
  matter.
- **Three rules that lived in a page moved to an owner, rather than dying with
  it.** M4-17c's zero-waterline refusal is `validation.landing_cg_below_axle`,
  a pure predicate the GUI renders on the page its tag names. G-53.7's
  "clockwise seen from the pilot's seat" is the `prop_direction` field's own
  registry row, so it reaches the GUI, the data dictionary and the report's
  field provenance together. #124's horsepower precedence is guarded by a sweep
  asserting no display module reads the fields at all. Each was a caption in a
  deleted file; each is now the one place the rule is stated.
- **R-57.5's rename and the Phase G plan's roll to history stay deferred.**
  Note 57 §6/§8 puts both at the 0.8.4 cut rather than in a row, and the branch
  taken keeps the `oracle_app` name and the `sloads-oracle` entry point. What
  this step takes from that list is the lint-path half the issue names: `app/`
  leaves the ruff scope in CI, `solo_close.sh`, `CLAUDE.md` and `README.md`, and
  `smoke_test.sh` boots one front-end because there is one.

- **The two reports become one (#278, note 60 D-60.7…D-60.11, tier M, 2026-09-13)** —
  Note 57's convergence retired `app/views/` and, through it, a 2,632-line document
  it never named: `app/views/export_report.py` was the only production consumer of
  `content.build_report`, so deleting the page would have deleted the summary report
  and taken with it the only statement of the airplane reference frame either front
  end makes, the only FAR 23 Subpart C coverage matrix, and the document-level
  governing safety-factor table. Note 60 named the deletion and conditioned it on a
  merge; this step is the merge. Four cross-cutting sections now print as the oracle
  report's front matter after the introduction, through a declared
  `FRONT_SECTIONS` table that leaves the analysis section set derived from the
  workflow and lets the body renumber itself around them. They are built once, by
  `sloads/report/front_sections.py`, and printed by both documents while both exist,
  because a merge implemented as a copy is the drift the convergence was called for.
  The fourth asset — the bundle manifest — closed a gap of its own: the document now
  carries its own list of the files that travel with it, control files and `data/`
  alike, computed with the document rather than at packaging time. What is *not*
  merged is declared key by key in an audit table a guard test reads, so no section
  of the retiring document leaves without a successor or a stated reason; that audit
  is what forced decisions on the approved-corrections table and on the balanced
  free-free cases rather than letting either be lost between two changes that each
  looked complete. `build_report` itself is untouched: it is deleted with the page
  at #270, after its content has reached its new home.

- **The oracle GUI renders every input path in two marked field tiers (#266, design note 57 D-57.2, tier M, 2026-09-13)** —
  the second row of band B5 and the one the convergence depends on: `app/views/` cannot retire while 83 fields are
  enterable only there. The barrier was one line — `page_groups` filtering on `oracle_input_paths()` — and the charter
  it enforced (note 32 OG-1/OG-2, *"the original suite's inputs, and nothing this replication added"*) had no way to
  distinguish *not asked for by the original programs* from *unreachable*. Both tiers render now; `field_registry.tier_of`
  classifies every path `SUITE`/`EXTENSION`/`JSON_ONLY`, and the extension tier is marked on the widget rather than
  gathered into a section, because a record holds fields of both tiers and a second section over one record emits its
  row counter, its seed and its remove control a second time under the same Streamlit key — D-57.2's *"marked section
  per page"* amended to marking that travels with the field. Marking is applied in `form._field_label` and `form._help`
  alone, the two functions every widget passes through, so a grid column is marked in the only place a grid column can
  be. `oracle_input_paths()` keeps its name and its callers but stops claiming to bound what the GUI writes: what it
  bounds — and what gate G5 was always really testing — is the tier, *with only these fields populated every
  oracle-page module still runs and every Appendix A oracle still passes*. Twenty fields on three records whose path
  crosses a `[]` hop stay JSON-editor-only, declared in `JSON_ONLY_RECORDS` with the reason, and note 57 gate 3's
  registry-walking guard re-derives that classification from the renderer's own addressing so it cannot be used to hide
  anything. Gates 4 and 5 (note 60 §5) assert here: every extension widget marked and stating its basis, and G-OR-74's
  screen sweep reading the tree at all — which is #239, closed the day before for this row.

- **The figure residue is ruled on rather than deleted (note 60 §9 amended
  2026-09-13, tier M, 2026-09-13)** — #267 ported sixteen of note 60 §1.1's
  twenty figures and #268 took the fleet comparison, leaving three that had no
  report producer. They were reported at #267's close instead of being allowed
  to disappear with `app/views/` at #270, and the owner ruled on all three in
  session. **Figure 6, item weight against fuselage station, ports here.** The
  reason it could not port at #267 was that `PlotData` had no way to express a
  cloud of named points; #268 added `Series.marker` and `Series.labels` for the
  fleet scatters, which made this figure a producer of about fifty lines —
  `content.item_station_plot_data`, one series per `MassItemKind` so that a
  heavy item at an extreme station can be read as the airplane or as a loading,
  named points on hover, and the oracle report's section 2.2 printing it beside
  the weight/CG envelope so it satisfies gate 10 like every other family. The
  shapes that tell the three kinds apart are stated in the existing
  `Series.style` channel as a pgfplots `mark=` token and honoured by both
  renderers, shape and not colour because §4.3 requires the printed figure to
  read in greyscale. **Figure 18, the wing + fuselage snapshot, retires
  superseded** by the two distributions #267 put on the pages that compute them.
  **Figure 19, imported against computed, is deferred with the capability it
  needs** — an inbound channel for an externally computed load distribution,
  filed in backlog band C — *additional analysis
  capability, design notes first* — and requiring a design note at AGREED first,
  because the hard part is the contract (columns, stations, units, and what a
  disagreement means) and not the overlay. The point of the row is that #270
  now deletes a page and not a capability nobody decided about.

## Step — Twenty figures port under one owner (#267, design note 60 D-60.1…D-60.6, tier L, 2026-09-13)

**Objective.** Give the surviving front-end the figures it lacks, without
giving the project a second owner of what a figure is. Note 57 D-57.1 makes
`oracle_app/` the survivor and D-57.8 requires it complete before anything is
removed; at 0.8.3 it contained **zero chart calls** while `app/views/` carried
twenty at thirteen pages, **nine of which are shared analysis steps** the
survivor already rendered with no figure at all. Note 57 §1.3 had counted
app-only pages and so could not see the other sixteen figures going, and
D-57.4's *written fresh — the app's implementations are the spec, not the
source* would have built a second figure owner beside the report's, which is
the drift class (#239) the whole convergence exists to end.

**Agreed first.** Design note 60 (AGREED 2026-09-13, owner), Block A. It
amends note 57: D-57.4's four-figure port list and its *written fresh* ruling
are **withdrawn** (R-60.2, D-60.1), #267 is re-tiered M → L (R-60.3, D-60.5),
and gates 9 and 10 join note 57 §4 (D-60.6, D-60.2).

**Deliverables.** `sloads/report/figures.py` — the catalogue: `Stage`
(`PRE_RUN`/`POST_RUN`), `FigureFamily`, `catalogue()`, `families_for_step`,
`results_for_step` and `build_step_figures`, thirty-nine families over the
fourteen oracle pages. `Figure.family` on the content model, defaulted to the
key so a single-instance producer states nothing and a multi-instance one must.
Nineteen figure builders lifted out of `oracle_sections.py`'s section builders
into public functions (`geometry_figures`, `vn_figures`, `wing_distribution_figures`,
`tail_chord_figures`, `oei_figures`, `attitude_figures`, `lumping_figures`, …),
each taking a `Project` and, where needed, the module results — and the section
builders re-pointed at them, so the document and the screen are one
construction. `app_shell/plots.py` — the Plotly peer of `plots_tex`: it
translates the producers' pgfplots line styles to dash patterns and weights,
colours the traces (a screen has no greyscale constraint; the stated encoding
is kept as well, so a reader with the PDF open sees the same dashed curve),
closes and fills a `Series.closed` region, holds a drawing to a 1:1 aspect and
a graph to none, and renders a figure's `absent_reason` rather than an empty
axis. `oracle_app/figures.py` — two blocks per page, *what is entered* above the
results and *what was computed* below them, each stating which it is.
Two figures gained producers they never had: the balancing tail load against CG
and the static margin against CG (note 60 §7), built from `trim_sweep` and the
Configuration module's tail-volume neutral point and printed by the oracle
report's flight-envelope subsection.

**Test.** `tests/test_figures.py` holds note 60 §5's two new gates.
**Gate 9** — every family builds for every bundled example without raising and
every instance carries either `PlotData` or an `absent_reason`; asserted on a
blank `Project` too, because a project being checked before it is complete is
the pre-run tier's normal subject. **Gate 10** — parity both ways, walked over
families against the **built** oracle report rather than against a list: a
report figure with no catalogue row fails, and so does a catalogue row no
document produces. Both directions were mutation-checked (dropping
`lumping_wing`, adding a family nothing produces, and removing `family="vn"`
from the V-n producer each fail the suite). Beside them, the page-level half in
`tests/test_oracle_gui.py`: each of the fourteen pages renders exactly the
blocks its catalogue rows imply, the stage note is present, and no GUI module
anywhere constructs a `PlotData` or a `Series`.

**Key decisions.** *One producer set, two renderers* (D-60.1) — the alternative
was a second derivation, which is the defect. *Families, not keys* (D-60.2) —
the guard must not parse `vn_0` into `vn`, or it would be the guard and not the
producer deciding what a family is. *Pre-run means entered data drawn, and it is
stated per family rather than derived from the argument list* (D-60.4) — five
delivered load distributions reach the calc directly from a `Project`, so
classifying on "takes no results" would have labelled them input echoes, which
is precisely the mistake the classification exists to prevent. *Parity is
checked against the document, not a list* — a list in a test is a second
catalogue, and that is how D-57.4 came to name four of the twenty figures that
were actually there.

**Not ported, and why.** Three of note 60 §1.1's twenty have no report
producer and do not gain one here: *item weight against fuselage station* is a
stem/bar shape `PlotData` has no member for; the *wing + fuselage total-loads
snapshot* is a composite of two distributions that now render on their own
pages; and *imported against computed* needs an external-CSV import channel the
survivor has no page for and which #245 is still deciding. The *fleet
comparison* is #268. Each is a figure the retiring GUI carries, so they are
named here rather than left to be discovered when `app/views/` is deleted.
**Ruled 2026-09-13, after #268** (owner, in session; note 60 §9 amended): *item
weight against fuselage station* **ports** at the residue row — #268 gave
`PlotData` the cloud of named points it had been missing, so the blocker was
gone the moment the fleet scatters landed; the *snapshot* **retires superseded**
by the two distributions now drawn on the pages that compute them; and *imported
against computed* is **deferred with the inbound CSV channel it needs**
(backlog band C), not retired, so #270 removes a page and not a capability nobody
decided about.

- **The fleet comparison ports to the surviving GUI (#268, design note 57
  D-57.5, tier M, 2026-09-13)** — the Phase-C *assess against similar airplanes*
  requirement lands in `oracle_app/` as a marked **✦** extension page, on the
  navigation only and never in the derived step set, at the url path `fleet`
  because `aircraft_comparison` is a workflow step key and a non-step reachable
  at a step's URL is what gate G2 exists to prevent. The port's real content is
  what it stopped owning. The bundled reference fleet moved from `app/data/`
  into `sloads/data/` and is read by `sloads.fleet.reference_fleet`; the
  subject's priority chain moved out of the page as
  `sloads.fleet.subject_from_project`; the six scatters became `PlotData`
  producers in `sloads/report/fleet_figures.py`; and the readout, tabs and fleet
  table became `app_shell/fleet_view.py`, which the retiring page now calls
  unchanged — two pages, one implementation, for the milestone in which both
  exist. D-57.5's *rewritten, not imported* was not followed; the amendment
  was **ratified by the owner in session, 2026-09-13**: note 60 D-60.1
  withdrew exactly that rule for figures
  on the ground that a second derivation is a second owner, the subject chain is
  the same class of thing, and it carries the 2026-08-15 fix that had stopped a
  regional jet being plotted 1,800 lb above any weight its loadings can reach —
  a rewrite would have been a rewrite of that fix. The move paid for itself
  immediately: gate DG-3 forbids anything in `sloads/` from integrating the wing
  planform itself, the page had been doing exactly that since M2-5 and was
  invisible to the guard while it lived in `app/`, and the subject now reads
  area, aspect ratio and span through `derived_geometry`'s resolvers — the
  single owner of what area the analysis actually uses (#70) — with the
  placement unchanged to the last ulp on every bundled example. Making the figures
  producer-owned needed three additions to the figure model, which could not
  express a scatter at all: `Series.marker`, `Series.labels` and
  `PlotData.log_x`/`log_y`, honoured by the Plotly renderer and — bar the
  per-point labels, which are a hover and not a printed node — by `plots_tex`,
  so the set can be printed the day a document asks for it. The figures are
  deliberately **not** in `sloads/report/figures.py`'s step catalogue and not in
  the oracle report: every family in that catalogue is drawn on the page whose
  programs produce it and is held against the built document by gate 10, and the
  fleet comparison runs no program. Guarded by `tests/test_fleet_figures.py` —
  the six figures build for every bundled example, the CSV has exactly one
  reader in the whole tree, neither front-end defines a derivation of its own,
  and both renderers honour the marker and the log axes.

- **The weight-estimate seed is built fresh, and built merging (#269, design
  note 57 D-57.7, tier M, 2026-09-13)** — the surviving GUI had no way to copy
  WTESTIMA's component weights into the itemized data base WTONECG and WTENV
  actually read, and the retiring GUI had one that replaced every entered item
  and captioned the replacement underneath the button that had already done it
  (#78, C210-9). D-57.7 refused to port the defect into its new home and fix it
  later, so both halves land in the first version. Of *merge, refuse or
  replace*, the answer is **merge**, chosen because it is the only one of the
  three that is idempotent: the seed matches on item name, adds only what the
  data base does not already name, never overwrites and never deletes, so
  pressing it a second time after positioning half the rows picks up the other
  half and disturbs nothing. The plan is built before the click and states
  itself above the button — how many rows it adds, how many it leaves alone,
  and that nothing is replaced. The second half is the one the numbers care
  about: WTESTIMA gives weights and nothing else, so a seeded row arrives at
  station 0 untagged, where `infer_component` carries it on the fuselage beam
  at zero moment arm and it moves the CG and the body shear while looking like
  data the user entered. Both GUIs now show `mass_distribution.unplaced_warning`
  as a warning that persists until each row has an `x` station and a
  `component` tag, and the predicate is written generally — a row counted into
  existence and left blank is the same row. Every part of that is owned in
  `sloads/` (`weight_estimate.SEED_CONTRACT`/`SeedPlan`/`seed_plan`/`seeded_items`
  and `mass_distribution.unplaced_items`/`unplaced_warning`), reached from the
  oracle form through the new `field_registry.TABLE_SEEDS` — `RECORD_SEEDS`'
  analogue for a `…[]` table — which is what let the retiring `app/` page be
  pointed at the same owner instead of being left holding a live destructive
  button for the rest of the milestone. Nothing moved out of `app/`, so this is
  not the port D-57.7 rejected; it does mean #270 deletes a page that owns none
  of it, and it closes **#78** superseded. Guarded by
  `tests/test_weight_seed.py`: an entered row survives a seed unchanged in
  weight, station and tag; a second seed offers nothing; a name already present
  is matched regardless of case or spacing; a project with no mission inputs is
  told why rather than crashing; a seeded row is named as unplaced until it is
  both positioned and tagged, while a zero-weight blank is not; and
  `estimate_to_mass_items` has exactly one caller in the whole tree.

- **The issue package's `data/` becomes the oracle GUI's only tabular channel (#245, tier M, 2026-09-13)** — OR-23's `data/` externalisation, planned at design note 44, deferred by OR-42 and delivered here under the consolidation ruling of note 57 §1.3 and note 60 D-60.12. The defect was a shape rather than a number: three channels carried the same tables — a CSV and a text twin on every results block, the sidebar's whole-project results zip, and the applied load sets, which shipped only from `app/`'s export page and so were unobtainable from the front end that survives — while the package a report issue *is* held five control files and no data, and Appendix F named `landing_gear_applied_loads.csv` in printed prose that pointed at nothing. `sloads/report/package_data.py` now decides what `data/` carries and `oracle_package` places it: the six applied sets, the balanced V-n conditions, the case index, the governing safety-factor table, the gear report, one load-case file per module that produced a result, one file per appendix table no named file carries, and one file per figure the document draws. All of it comes from the owners the document renders from and from the *same* built document — `OracleDocument` gained the reduced project and the module results, so there is no second run and no second formatter — and each file states its units, its axes, the factor it does not apply, its producing step and the build fingerprint, with the document's own front matter listing them. The per-module buttons and the zip retired with no replacement built (`results_zip.py` deleted, `Artifact`/`page_artifacts` gone, the sidebar's `channel` parameter with them), and the column inventory the retirement was conditioned on became a test that compares each module file byte-for-byte against `io.load_cases_csv` rather than a check done once. Its two named cases came back clean — the V-n matrix and the envelope's 300-point table are different quantities and both ship; LANDLOAD's primed ground-line set is in `gear_loads.csv` — and its real find was the one-engine-inoperative yaw march, drawn as figures with no tabular channel anywhere and about to be deleted with `app/views/one_engine_out.py`: the fix is a generic emitter over `content.PlotData`, so every figure ships its numbers. G-OR-15 and G-OR-17, vacuous since they were written, got their real bodies; G-OR-73 widened from four hand-rebuilt CSVs to everything the package ships; gate G7 was re-cut from "one download call site" to "no download but the project file".

- **The record stops outnumbering the authority: notes split out, the record filed apart, one telling per closure (note 61, tier M, 2026-09-14)** — the documentation machinery was measured rather than described, and the cost turned out not to be volume but search. `10_standard` + `20_theory` held 12,489 lines against 27,928 lines of pure record with no reader, and every term a maintainer actually looks up returned two to three times more hits from the record than from the authority (`LRA` 34 against 14, `envelope` 42 against 19) — every one of them a dated snapshot, and the ratio worsening each cycle because the record grows with time while the live corpus grows with the code. The blocker was that `40_history/` was two corpora fused under one name: 52 of its 61 files were design notes that 18 files under `tests/` cite as the standing authority for physics, so the record could not be moved out of the way without exiling the physics with it. CV-3 split it by function — 54 notes to `docs/25_notes/` whatever their status, since a note that has shipped is still the authority for what it decided, which is why filing them by shipped-ness was wrong — and CV-4 then moved the remaining 18 record files and `CHANGELOG.md` to `docs/90_record/`, out of the default search path, with `CLAUDE.md` saying so. 72 files moved, no body edited, 114 files' references rewritten. CV-2 ended the tier-M duplicate telling: note 26's DV-4 had removed it at tier S on the premise that the two files answer different questions, which this cycle's 12 items falsified at 780 words each — the history fragment was a re-flowed compression of the changelog fragment, same findings, same causes. A tier-M/L closure now writes one fragment and `build_changelog.py` derives the changelog bullet from the lead phrase the entry already opens with, so nothing is capped and nothing is lost; a hand-written bullet still wins where the consumer-facing wording genuinely differs (this entry is the first use of the mechanism). CV-1 added the question that stops the leak recurring — *does a reader of the code today need this, or only a reader asking what happened?* — because durable understanding landing in the narrative is how the narrative became load-bearing in the first place. CV-5 gave `CHANGELOG.md` the archive rule note 26 DV-1 gave the history and not it: 11,249 lines against the history's rolled 1,388, now sharing the same 1,500-line trigger and `--roll`. CV-6 shipped the guard the move needed, `tests/test_doc_links.py`, and it paid immediately: twelve live links were already dead before the move — notes renumbered without their inbound links, a theory chapter renamed, the FAR 25 gap analysis cited under `20_theory/` — all fixed here. `docs/90_record/` is exempt from it, because a frozen archive links to the tree it was written against and DV-1 forbids editing it to keep a test green. Two links are left standing and named in `_KNOWN_DEAD`: note 40 cites two `app/views/` files, and `app/` was deleted wholesale at #270 — 37 live documents still reference it, seven of them in `10_standard/` and `CLAUDE.md`, which is the GUI retirement's currency debt and wants its own item; `CONTRIBUTING.md`'s lint command was the one instance that had actually gone wrong (it still named `app/` and omitted `oracle.py`/`oracle_app/`, so the command as printed exits 1) and is fixed here under practice 4. Retired with DV-5: the status-driven note move at release cut. Deferred: the length half of #187's INDEX-row rule still covers `30_future/` only — the status half was widened to the 54 note rows (20 cleaned), but 44 rows exceed the cap and trimming each is a content edit, not a consequence of re-filing.

## Release cut: **sloads 0.8.3** (the empennage geometry model, and the export package closing on one solver artifact), tag `v0.8.3`, 2026-09-13

**Objective.** Close band **B4**. The milestone opened on its named deliverable
— the **T-tail empennage geometry model** (#25) — and closed on the one that
grew out of it: `sloads/export/` shipped **four parallel model concepts** in one
ID space, three of which were not the deliverable, and the deliverable borrowed
GIDs from artifacts nobody consumed. Design note **56** reduced the package to
**one solver artifact plus the mass model**. The two are the same problem seen
twice — where a joint node *sits* (note 54) and how the model that carries it is
*built* (note 56) — which is why they landed in one milestone.

**Deliverables** (the `[0.8.3]` changelog section is the release note):
- **The empennage geometry model (#25, design note 54, tier L, schema v65).**
  The tail group's geometry is **entered once as boundary lines** and the
  scalars derive: the seam between fixed surface and control surface is marked
  in the input blocks (step 1), and the planform scalars each surface used to
  carry independently become reads of the entered polylines (step 2). Around it
  the cluster: the joint register — a joint is an **owned location, a stated arm
  and a DOF set** (#262, D-54.5/D-54.7, `sloads/joints.py`, importing three
  owners so it can live inside none of them); the conventional h-tail off the
  wing-root waterline (#261, D-54.4); a raked fin root that no longer kinks the
  loads reference axis (#219, D-54.3); one owner for the plane a surface is
  defined in (#220, D-54.2); one name per surface, `fin_*` retired for `vtail_*`
  (#223). **D-54.6 alone remains**, riding the baseline wave in 0.8.5, so note
  54 stays live.
- **The export package closes on one solver artifact (#263, design note 56,
  tier L, ten slices).** The five **per-component decks are deleted** (D-56.2);
  the assembled balanced deck is **unshipped**, demoted to an internal producer
  the LRA transfer and the report's tables consume (D-56.8); `sbeam_bridge.py`
  **ceases to exist** — the applied-load model and the report's deliverable
  tables were never a bridge to sbeam and move to `report/applied.py` and
  `report/tables.py` under their right names (D-56.1), with no shim and two
  guards refusing one. What ships is the **LRA beam model** and the CONM2 mass
  model: the LRA owns every grid it writes (D-56.3), takes a **joint-driven mesh
  decided from geometry** rather than one welded to the load stations (D-56.4),
  and carries the applied set summed onto its own grids with the exact
  lever-arm couple (D-56.9); every `CONM2` sits on its own `GRID` at its own
  item's CG (D-56.6). `EXPORT_TARGETS` 10 → **3**, `sloads/export/` 8,603 lines
  across 15 modules → **5,316 across 14**.
- **What the beam grids cost the distribution is published, not discovered
  (D-56.10).** New **Appendix G** and the new owner `report/lumping.py`: the
  widest gap in each internal-load channel of each member over every case, plus
  four figures along the span. The **resultant** is preserved exactly and gated
  by LM-1; the **distribution** it moves is a real discretization difference, so
  it is stated. No solver is in the loop and there is no acceptance tolerance —
  the size of the difference is a function of the grid counts the project sets.
- **Every exported LRA deck solves (#172, design note 55, tier L).** Three
  defects in *how a joint node joins the structure*: a body tie parenting on a
  node already an `RBE2` dependent (a rigid chain sbeam refuses outright), a
  joint inserted beside an existing station leaving a **sliver element**
  (`cessna_210` at 1.07 % of `ds`, 1638:1), and a support picker that excluded
  rigid dependents but not independents — **569.49 lb** of recovered reaction
  against an applied set closing to 0.0002 lb. All three are gated invariants,
  a skeleton that violates one is an `LraRefusal` naming it, and the solve gate
  widens from the two fixtures that passed to **every CLI-exportable fixture**.
  This is the milestone's mission claim made true rather than asserted.
- **The load-output contract consolidated (#193, note 58, tier M; #170; #175).**
  Governing-case comparisons key on **|value| × SF** so a 2,000 lb case at 1.5
  is not out-ranked by a 2,500 lb case at 1.0, and a mixed-factor envelope
  refuses by name; no delivered load value moves on any fixture. The contract's
  statements get **one owner** and eight copies collapse onto it; a machine
  rating in load units stops being a load (#170).
- **The plan re-cuts into three milestones (tier S, 2026-09-11).** 0.8.3 closes
  the export contract, **0.8.4** converges the two front-ends on one (note 57,
  AGREED), **0.8.5** takes the defect-and-polish tail on the converged surface —
  because note 57 sat AGREED, filed and sequenced, gated on a 21-row tail with
  no relation to this milestone's charter. Bands B5 and B6 carry them.
- **Hygiene as its own items:** the deck-writing primitives get their own module
  (#15, CH-4); six dead public names leave `sloads/` with a gate keeping the
  seventh from arriving (#16, CH-5); the round-trip stick-model wrapper retires
  with the last elementless deck, 529 → **186** lines; `cessna_210` and
  `dhc8_dash8` retire from the bundled examples (#264) while `baron_58` joins
  the Imperial output baseline and the example list becomes structural (#271);
  the theory documentation becomes a chaptered manual; the certification-basis
  matrix leaves the ranked backlog under rule 6 (#47, closed not-planned); the
  backlog is re-scoped onto the package note 56 left behind, and its open-defects
  index loses two wrong issue numbers, a deleted body and three closed entries.
- **The band re-opened once, and drained before the cut (#274).** The
  issue-bookkeeping pass that followed #263 found **seven** rendered statements
  — the oracle report's §7 and gear sections, four GUI captions and a help
  string — plus the `$` header inside the one deck that ships, all describing
  the export package the note had just deleted. A defect with first-order effect
  on shipped content outranks every [V] item, and 0.8.3 could not knowingly cut
  a report naming artifacts it does not build. Filed, fixed and closed the same
  day; the deliberate carve-out is the case index's `LOAD/SUBCASE (component)` /
  `(assembled)` headers, which move a shipped CSV header across three owners and
  are **#209**'s decision, stated at `LOAD_ID_COLUMN` rather than left to be
  inferred.
- **Found at the cut and fixed pre-cut (the §3.5 walk):** three more shipped
  statements of #274's class that its sweep had not reached — the Wing Loads
  caption offering "all three files" and describing the span-load file beside
  them, the Fuselage Loads caption offering "both files" and naming the body
  span CSV, and the SI methods stamp's "the sbeam solver decks **and their span
  CSVs**" — all naming companion files D-56.2 deleted. With them the last
  `*_ULT.csv` filename in the tree, `wing_applied_loads_ULT.csv`, which note 49
  **OR-81** had held for exactly this milestone: the file is LIMIT like every
  other, and a name asserting otherwise is the one statement a reader cannot
  check against the content.
- **Version** `0.8.2` → **`0.8.3`**. Schema **v61 → v66** across the cycle
  (the boundary-line model's v65 among them); `io.py` still loads older saves.
- **Changelog cut** — `scripts/build_changelog.py 0.8.3 --date 2026-09-13`:
  **34 fragments** consumed into `## [0.8.3]`, **20 history entries** rolled to
  the top of this file, a fresh empty `[Unreleased]` opened.
- **History roll** (`RELEASE_PROCESS.md` §4.3): notes **55** and **56** move to
  `40_history/` keeping their numbers; note **54** stays live on D-54.6 alone
  and note **58** on D-58.1 (decided, not done) — the mechanical rule rolls a
  note whole when its status reads shipped, never by halves; notes 21/49/51/52/57
  stay with their open milestones. The live file passed the **1,500-line
  threshold**, so everything below the 0.8.2 cut block froze verbatim into
  [`59_completed_development_to_0.8.2.md`](59_completed_development_to_0.8.2.md).
- **Gates at cut:** `pytest` **3,422 passed / 17 skipped / 2 xfailed / 0 failed**, `ruff` clean, `mypy` clean
  (`sloads/`, 98 source files), `scripts/smoke_test.sh` **PASS** (both front-ends boot, CLI CSV checked),
  `scripts/backlog_issues.py check` clean,
  `scripts/branch_protection_snapshot.py --check` matches on 7 tracked keys,
  the §3.5 by-hand walk done by the owner, no open CRITICAL/MAJOR review
  findings. The four statements above came out of a read of the pages that
  precedes that walk, not out of it.

**Key decisions.** *A deliverable is what a consumer holds, and everything else
is scaffolding that has to justify itself.* The package had grown four model
concepts because each was easier to add than to reconcile, and the cost was not
maintenance time but **truth**: the shipped model borrowed GIDs from decks that
were not deliverables, and the report described a package the bundle did not
carry. Two rulings made the reduction cheap enough to take. Nothing downstream
reproduces an sbeam output, so decks, digests and GIDs were free to move and the
renumber happened once. And sizing belongs to the stress analyst, outside
sloads: core sloads produces an LRA beam model with arbitrary beam properties
plus the load cards on its grids, to prove the cases solve — that is the whole
job, and it is what let ~4,000 lines go without withdrawing a claim.

*The mesh was the tell.* A beam welded to the load stations is a **degenerate
special case that hides the general one**: when beam nodes *are* load stations
the spanwise half of the transfer is identity, so every CI fixture exercised the
degenerate path while arbitrary-grid routing — what a real user meets first —
was least covered. Cutting the mesh loose made the generated model *one instance
of the contract the imported model obeys*, and note 55's sliver class died
structurally rather than by tolerance.

*Publish the cost of your own discretization.* D-56.9 sums the applied set onto
grids the mesh chose from geometry, so a moment that is zero at a station is
generally not zero at a grid. The resultant is gated; the distribution moves.
Appendix G exists because the honest response to "this changed something we
cannot bound" is to measure and print it, not to pick a tolerance that would
fail a coarse mesh behaving exactly as specified.

**Band B4 retired with the cut; band B5 (0.8.4 — the two front-ends converge on
one, design note 57) is the milestone in flight.**
