# The figures and the one report (design note 60)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-09-13** — Block A landed with
[#267](https://github.com/Sean074/sloads/issues/267) (twenty figures, one
owner), Block B with [#278](https://github.com/Sean074/sloads/issues/278) (the
cross-cutting merge) and [#270](https://github.com/Sean074/sloads/issues/270)
(D-60.11: `build_report`, the summary LaTeX path and `report/bundle.py` deleted
with the page, after the merge). One deviation from D-60.10, taken at #270 and
recorded in its history entry: the audit table did **not** retire with
`content.py` — the section list moved beside it as
`front_sections.RETIRED_SUMMARY_SECTIONS`, because an accounting whose subject
has been deleted accounts for nothing and gate 12 would otherwise have stopped
being enforced at the commit that made it matter.

**AGREED 2026-09-13** (owner, in session, under the solo profile —
`DEVELOPMENT_PROCESS.md` §0; rule 1's working-alone branch). Drafted the same
day on `dev/v0.8.4`, from the owner-commissioned critical review of band B5
taken immediately after the 0.8.3 cut. It **amends design note 57** — which
stays AGREED and whose D-57.1, D-57.2, D-57.3, D-57.5, D-57.7 and D-57.8 are
untouched — on two points its own measurements did not reach:

* **D-57.4 undercounted the figures and prescribed the wrong owner.** The port
  list names four figure families; the front-end carries **twenty**. And
  "written fresh … the app's implementations are the spec, not the source"
  would have built a second figure owner beside the report's, which is the
  drift class note 57 §1.5 cites as the reason to converge at all.
* **D-57.6 retires a document it does not name.** `export_report` is the only
  production consumer of `sloads/report/content.py`'s `build_report`, so
  retiring the page retires the **summary report** — and with it the only
  statement of the axis system and sign conventions either front-end makes, and
  the only FAR 23 Subpart C coverage matrix.

**Tier L.** A document merges and a figure layer gains an owner. **No delivered
load changes, no calc change, no schema change** — every module, deck and CSV
is untouched; the work is in the shell layer (`app_shell/`, `oracle_app/`) and
in the report's presentation layer (`sloads/report/`).

Measurements in §1 are taken at `dev/v0.8.4`, 2026-09-13, with 0.8.3 cut and
tagged and note 56 shipped.

---

## 1. What the code does today, and what note 57 did not measure

### 1.1 Twenty figures, and nine of the thirteen pages carrying them are shared

`app/views/` is **22 pages, 8,787 lines** (note 57 §1.1 measured 8,802 before
note 56's seven consumer edits landed). Of those pages, **thirteen carry a
chart**, at **twenty call sites** — one figure each.

Note 57 §1.3 concluded that plots were one of four capabilities the survivor
lacks by counting **app-only pages**. That count is right and the conclusion it
supports is wrong: **nine of the thirteen plot-carrying pages are shared
analysis steps**, rendered in `oracle_app` today with no figure at all. Only
four (`tail_span_loads`, `balanced_cases`, `loads_plots`,
`aircraft_comparison`) are app-only, so a page-level audit cannot see the other
sixteen figures going.

| # | Figure | Page | Report `PlotData` today | Named by D-57.4 |
|---|---|---|---|---|
| 1 | Three-view (top/side/front, LRA overlay) | configuration_layout | per-surface planforms only | yes |
| 2 | V-n diagram | flight_envelope | `_vn_figure` | yes |
| 3 | Balancing tail load vs CG | flight_envelope | no | §8 deferred |
| 4 | Static margin vs CG | flight_envelope | no | §8 deferred |
| 5 | Weight/CG envelope | weight_mass | `weight_cg_plot_data` | **no** |
| 6 | Item weight vs fuselage station | weight_mass | no | **no** |
| 7 | Speed–altitude flight limits | structural_speeds | `speed_altitude_plot_data` | **no** |
| 8 | CL/CD/CM coefficient curves | aero_coefficients | yes | **no** |
| 9 | Spanwise span load c·cl | wing_loads | yes | **no** |
| 10 | Wing net load station (shear/BM/torsion) | wing_loads | yes | yes |
| 11 | Fuselage net load station | fuselage_loads | yes | yes |
| 12 | Tail chordwise net pressure | tail_loads | yes | **no** |
| 13 | OEI yaw response (θ, θ̇) | one_engine_out | yes | **no** |
| 14 | OEI fin load history | one_engine_out | yes | **no** |
| 15 | Tail span strip Fz | tail_span_loads | yes | **no** |
| 16 | Balanced-case spanwise applied load | balanced_cases | yes | **no** |
| 17 | VMT spanwise/chordwise overlays + envelope | loads_plots | yes | yes |
| 18 | Wing + fuselage total-loads snapshot | loads_plots | no | yes |
| 19 | Imported vs computed (external CSV) | loads_plots | **no** | yes |
| 20 | Fleet comparison | aircraft_comparison | no | D-57.5 |

*Where each row landed, 2026-09-13:* rows 1–2, 5, 7–17 ported at **#267**; rows 3–4 gained producers there (§7); row 20 at **#268**; row 6 at the residue row after it; row 18 **retires superseded** by rows 10 and 11 and row 19 is **deferred** on an inbound CSV channel — §9's amendment of the same day.

`oracle_app/` is **5 modules, 3,031 lines** and contains **zero chart calls of
any kind** — note 57 §1.3's measurement, still true.

### 1.2 The figure data already has an owner, and the two reports already share it

`content.PlotData` (`content.py:176`) is a frozen, **renderer-agnostic**
dataclass — `x_label`, `y_label`, `series`, `points`, `vlines`, `points_label`
— built for exactly this and consumed by `plots_tex` to emit TikZ. **Nineteen
producers** build one: seventeen in `oracle_sections.py`, two in `content.py`.
And the pattern of one producer serving two documents is already in the tree:
`oracle_sections.py:73` imports `speed_altitude_plot_data` and
`weight_cg_plot_data` from `content.py`.

So D-57.4's "the app's implementations are the spec, not the source" solved the
wrong problem. The complexity it refuses to import (`_tab_design_speeds` F(72),
`_three_view` F(63)) is *emitter* complexity; the *data* is already owned, and
re-deriving it from result slices would put the screen figure and the printed
figure under two owners that can disagree — #239's class, which §1.5 uses to
justify the convergence, re-created by the convergence's own port ruling.

What genuinely is not owned is small: three of the twenty figures have no
`PlotData` producer (#6, #18, #19), and the three-view assembles from geometry
primitives that already live in `sloads/` (`configuration.wing_polylines`,
`configuration.lra_overlays`, `wing_geometry.surface_top_outline`), so its cost
is subplot plumbing, not derivation.

### 1.3 The real cost of the figure port: producers are bundle-bound

The GUI's use is **checking inputs before running the whole process**, which
requires a figure buildable from a `Project` alone. Exactly **three** producers
are that today — `_vn_figure(project)` (private), `speed_altitude_plot_data`
and `weight_cg_plot_data`. The remaining sixteen sit inside
`oracle_sections.py` (**8,231 lines**), reachable only through a built report
bundle. Making each callable per figure is the work, and it is why #267 is not
the M-tier row the backlog carries.

### 1.4 D-57.6 retires the summary report without naming it

`render_report` → `content.build_report` has **one production consumer**:
`app/views/export_report.py:361`. Every other caller is a test (eight test
files). D-57.6 deletes that page, so the **summary report document — 2,632
lines of `content.py`, organised by topic against the oracle report's
per-step organisation — goes with it**, unnamed in note 57 §6 and unlisted in
its §7 closure obligations.

Two owner modules have that document as their sole consumer and die with it:

| Asset | Owner | Lines | Sole consumer | In the oracle report |
|---|---|---|---|---|
| **Axes and sign conventions** — three prose paragraphs, a **16-row** table cited row-by-row to `CONVENTIONS.md`, and three static TikZ diagrams (`sign_axes`, `sign_controls`, `sign_beams`, `conventions_tex.py:259`, emitted at `plots_tex.py:414`) | `conventions_tex.py` | 276 | `content.py:854` | **No** — only per-figure and per-table sign statements at point of use |
| **FAR 23 Subpart C coverage matrix** — what was analysed, and what was **not** | `coverage.py` | 241 | `content.py:51` | **No** |
| **Governing safety factors** (document-level table) | `content._factors_section` | — | the summary report | **No** — factors are stated per case and per row |
| **Bundle manifest** (Appendix A: what ships, and where it is summarised) | `content._manifest_rows` | — | the summary report | Partly — `oracle_package.MANIFEST.txt` is a file manifest, not a document appendix |

The structural reason the axes section never appeared in the oracle report is
that the oracle report has nowhere to put it: its section plan is **derived from
the analysis steps** (`oracle_content.SECTION_GROUPS` + `SECTION_SPLITS` + seven
appendices), and a cross-cutting topical section belongs to no step.

Shipping 0.8.4 without the merge would leave one surviving document that states
no axis system and no coverage of what was not analysed. That is a first-order
effect on shipped content, which rule 6 ranks above every [V] item.

---

## 2. Governing basis

### 2.1 The standing rulings that make this lawful rather than novel

* **C210-15** (oracle GUI fidelity ruling): the fidelity target is the
  *analysis contract*, not the original prompt sequence. Figures are free.
* **OR-16** (note 44): a page registered outside the derived step set is
  precedent, already exercised once by the Report page.
* **`CLAUDE.md` practice 3** (make it structural): a cross-cutting convention
  gets a single-source owner **plus a drift guard**, never a prose rule. It is
  the whole argument of Block A.
* **`CLAUDE.md` practice 2** (benchmark-first): #267 as filed has no gate at
  all. Note 57 §4's eight gates cover the editor, the tiers, field coverage,
  basis statements, the screen sweep, `set_page_config`, the journey and
  reachability — and no figure.
* **Note 57 R-57.3**, closing sentence: *"Any line of this table the owner
  moves, moves."* Block A moves several.

### 2.2 Rulings (owner, 2026-09-13, in session — each taken as proposed)

1. **R-60.1 — the figure set.** Pre-run and post-run figures are both useful.
   **At a minimum, every figure the oracle report carries also appears in the
   GUI.** The port list is the twenty of §1.1, not D-57.4's four.
2. **R-60.2 — the figure owner.** Whichever is more efficient — and it is
   **reuse**: one `PlotData` producer set, two renderers. D-57.4's
   "written fresh" is withdrawn.
3. **R-60.3 — #267 becomes tier L** and carries its decisions here rather than
   being discovered during implementation.
4. **R-60.4 — the CSV channel.** The per-module CSV and text buttons retire
   with the results zip; everything is packed in the report export page, whose
   `data/` (#245) is the single tabular channel. (Confirms and widens the
   backlog's #245 row.)
5. **R-60.5 — the report merge.** The four cross-cutting assets of §1.4 merge
   into the oracle report — **axes and sign conventions, the FAR coverage
   matrix, the governing safety-factor table, and the bundle manifest**. They
   land as a **front-matter group after the Introduction, before the step
   sections**. Everything else in the summary report is declared superseded by
   the step sections, **in writing, section by section**.
6. **R-60.6 — one note, two decision blocks** (this document).

---

## 3. Decision block A — the figures

| # | Decision | Alternative rejected |
|---|---|---|
| **D-60.1** | **One `PlotData` producer set, two renderers.** `content.PlotData` stays the single owner of what a figure *is*; `plots_tex`/`planform_tex` (LaTeX) and a new `app_shell/plots.py` (Plotly) are peers over it. The GUI never derives figure data of its own. | *D-57.4's "written fresh from the result slices".* Withdrawn: it creates the second figure owner that §1.5's drift class is made of, and it is more work than reuse (§1.2). |
| **D-60.2** | **Parity is structural.** A drift guard walks figure keys both ways: a report figure with no GUI renderer, or a GUI figure with no report producer, fails the suite. This is how R-60.1's *"at a minimum the report's figures appear in the GUI"* is held — by construction, not by diligence. | *A prose rule plus review.* Rejected under practice 3; the SSOT table in `CONVENTIONS.md` §7 gains the figure row. |
| **D-60.3** | **Producers become callable per figure.** Each takes a `Project` and, only where the figure genuinely needs one, the module results — rather than a built report bundle. `_vn_figure` is promoted public beside the two already public. The extraction inside `oracle_sections.py` is the bulk of #267. | *Build the whole bundle to draw one figure.* Rejected: it defeats the stated use — checking inputs **before** running the whole process — and makes every GUI page pay for the document. |
| **D-60.4** | **Every figure is classified `pre-run` or `post-run`**, by one stated rule: *pre-run means buildable from the `Project` alone*. The GUI states which it is showing, so a reader never mistakes an input echo for a result. The classification is data beside the figure key, walked by D-60.2's guard, not a comment. | *Leave it implicit.* Rejected: the distinction is the capability being ported, so it is the thing most worth naming. |
| **D-60.5** | **#267 is tier L**, scoped to the twenty figures of §1.1. R-57.3's port/retire table is amended to that list; no figure retires without port except by a line of this note. | *Hold M and cut the list to fit.* Rejected under R-60.1. |
| **D-60.6** | **A figure gate joins note 57 §4** (gate 9): every figure builds for every bundled example without raising, and states its `absent_reason` where it cannot. D-60.2's parity guard is gate 10. | *Ship #267 against prose.* Rejected under practice 2 — the rule that applies to concept-mode physics applies here with the same force. |

**Swept under rule 4 while the guards are re-cut:** `_GUI_TREES` has two
owners — `tests/test_basis_statements.py:301` (`("app", "app_shell")`, which
excludes `oracle_app` and is why #239 exists) and
`tests/test_app_shell.py:920`. They converge on one.

---

## 4. Decision block B — the one report

| # | Decision | Alternative rejected |
|---|---|---|
| **D-60.7** | **The summary report's retirement is declared, not incidental.** D-57.6 retires `build_report`'s only production consumer and therefore the document; this note names it, so it leaves by decision rather than as a side effect of deleting a page. | *Leave it implicit in D-57.6.* Rejected: an unnamed deletion of a whole document is exactly what a design note exists to prevent. |
| **D-60.8** | **Four cross-cutting assets merge** into the oracle report: axes and sign conventions (prose, the 16-row cited table, the three static diagrams), the FAR 23 Subpart C coverage matrix, the document-level governing safety-factor table, and the bundle manifest. `conventions_tex.py` and `coverage.py` survive under their new consumer. | *Let them go with the page.* Rejected: the survivor would state no axis system and no account of what was not analysed. *Point-of-use statements suffice.* Rejected: they say what a figure's signs are, never what the frame is. |
| **D-60.9** | **They land as a front-matter group, after the Introduction and before the step sections**, through `oracle_content.FRONT_SECTIONS` — today `("Introduction",)`, the designed slot — so the section plan stays **derived** and gate G-OR-2's rule survives re-cut exactly as gate G2 did under OR-16. | *Appendices.* Rejected on OR-50: an appendix is appended, never inserted, and an axes section belongs **before** what it governs. *A code branch in `section_plan`.* Rejected: the guard tests must read the same table the builder does, which is why `SECTION_GROUPS` is data. |
| **D-60.10** | **Everything else is declared superseded, section by section, in writing.** The note's merge step carries a table: every section of `content.SECTIONS` with either its successor in the oracle report or a stated reason it retires. That written audit is what makes this a merge rather than a silent deletion. | *Merge what looks useful.* Rejected: it is unauditable, and the asset most at risk is the one nobody thought to look for. |
| **D-60.11** | **`build_report`, the summary LaTeX path and their test-only residue delete with #270**, after the merge has landed. Ordering is the point: the document's content reaches its new home before its old home is removed. | *Delete first, merge after.* Rejected: it ships a 0.8.4 with the gap in it. |
| **D-60.12** | **#245 widens:** the per-module CSV and text buttons retire with the results zip, and the report export page packs everything. `data/` is the single tabular channel, and no replacement per-module download is built. | *Keep per-module downloads for convenience.* Rejected under R-60.4 and the same duplication argument that retired the workbook (note 57's 2026-09-11 amendment). |

---

## 5. Gates

Note 57 §4's gates 1–8 stand unchanged. This note adds:

9. **Every figure builds for every bundled example** without raising, and
   states its `absent_reason` where it cannot (D-60.6).
10. **Figure parity, both ways** — no report figure without a GUI renderer, no
    GUI figure without a report producer; the classification of D-60.4 is
    walked by the same guard (D-60.2).
11. **The merged sections render** in the oracle report for every bundled
    example, and `conventions_tex.py`/`coverage.py` have a production consumer
    after #270 — asserted, so the merge cannot silently become dead code.
12. **No section leaves unaccounted:** a test reads D-60.10's audit table and
    fails if a `content.SECTIONS` key is neither merged nor declared
    superseded with a reason.

Two of note 57's own gates move, because they depend on work its sequence
placed after them:

* **Gates 4 and 5 move from #270 to #266.** Gate 4 (every extension widget
  states its basis) and gate 5 (G-OR-74's screen sweep covers the survivor) are
  enforced by `tests/test_basis_statements.py`, whose `_GUI_TREES` excludes
  `oracle_app`. Including it **is #239**, which the 2026-09-11 re-cut left in
  band B6 — after the band that depends on it. #239 moves into B5, ahead of
  #266.
* **Gate 7 is asserted after #266, not only at #270.** The `KNOWN_OPEN` list
  dies with the pages that own it, but #266 adds 79 fields to the survivor's
  renderer, and the no-op-Apply class could be re-imported with them.
  `tests/test_oracle_journey.py` carries no `KNOWN_OPEN` today; the gate is
  that it still carries none once the extension tier renders.

---

## 6. Effect vs error bar (rule 6)

Not a physics or fidelity item, so rule 6 does not gate it: **no delivered load
changes**, note 57 gate 1 unchanged. Block B is ranked by the other half of
rule 6 — a defect with first-order effect on shipped content outranks every [V]
item — because shipping the single surviving document with no axis system
stated is that defect, and D-57.6 as written creates it.

---

## 7. What this supersedes / corrects

* **Note 57 D-57.4** — the port list and the "written fresh" ruling are
  replaced by Block A. Its rejection of *importing the existing view functions*
  stands: nothing in `app/views/` is imported. What is reused is `sloads/`'s own
  figure data, which was never `app/`'s.
* **Note 57 D-57.6** — amended by D-60.7/D-60.11: the retirement now names the
  document it takes and is conditioned on the merge.
* **Note 57 §4** — gains gates 9–12; gates 4, 5 and 7 re-aimed at the rows that
  can actually hold them.
* **Note 57 §8** — *"porting the trim & stability sweep"* is no longer deferred
  as a follow-on: figures 3 and 4 of §1.1 (balancing tail load vs CG, static
  margin vs CG) are in the port list. The **sweep** itself — re-running the
  balance across a CG range — stays deferred; only its two figures port.
* **The backlog's band B5** — two rows added (#239 pulled forward from B6; the
  merge filed new), one re-tiered (#267 M → L). Sequence in §10.
* **Note 32's OG-2 / gate G-OR-2** are amended, not withdrawn, on the same
  pattern note 57 used for OG-1/OG-2: the section plan stays derived, and
  `FRONT_SECTIONS` is where a declared non-step section lives.
* **No `theory_sources.md` citation** — stated explicitly: this note changes no
  equation and cites no oracle. Note 57 gate 1 is why.
* **No schema change** — `SCHEMA_VERSION` stands.

---

## 8. Closure obligations

**This note's own landing is tier S** — one `changes/<slug>.changed.md`
fragment and the backlog band-B5 edits, no history entry. That is the precedent
note 57 set: it landed inside the 2026-09-11 backlog re-cut bullet
(`CHANGELOG.md` §0.8.3) with no bullet of its own, because an AGREED plan that
files issues changes the plan, not the product.

The **tier-L closure is owed by the work this note plans**, at the rows that do
it:

* **#267** — `changes/` pair in full step format; `CONVENTIONS.md` §7 SSOT
  table gains the figure-owner row; `GUI_design.md` re-pointed.
* **#278 (the merge)** — `changes/` pair; `PROGRAM_SPEC.md`'s report section
  re-cut to one document; `00_program_overview.md` where it names the two.
* **#270** — unchanged from note 57 §7, plus the deletion of `build_report`
  and the summary LaTeX path.
* `docs/00_INDEX.md` — row for this note *(landed with the draft)*.

---

## 9. Deferred

**Amended 2026-09-13 (owner, in session), after #267 and #268 shipped.** The
three figures of §1.1 that #267 could not port were reported at its close and
ruled on here. **Figure 6 — item weight against fuselage station — ports**, at
the residue row after #268: it was blocked only because ``PlotData`` could not
express a cloud of named points, and #268 added exactly that for the fleet
scatters (`Series.marker` / `Series.labels`), so the figure is a labelled point
per data-base row rather than the stem the retiring GUI drew. It is a **pre-run**
family on ``weight_mass`` and the oracle report's section 2.2 prints it, so it
meets gate 10 like every other. **Figure 18 — the wing + fuselage total-loads
snapshot — retires superseded**: its two halves are figures 10 and 11, which
#267 put on the pages that compute them, and a third axis carrying both adds a
view rather than a fact. **Figure 19 — imported against computed — is deferred,
not retired**: it is blocked on a capability the survivor does not have at all
(an inbound CSV channel for an externally computed distribution), which is a
design note's worth of questions — columns, stations, units, and what a
disagreement means — and not figure plumbing. `sloads/report/lra_import.py`
already reads an external GRID/CBAR *model*, so the appetite is real; the
figure is its first consumer when the channel is designed. Recorded here rather
than left for #270 to discover.

* **An inbound CSV channel for an externally computed load distribution**, and
  §1.1's figure 19 over it — deferred as above, and filed in the backlog's
  band C (*additional analysis capability, design notes first*). #245 settles `data/` as the
  single **outbound** tabular channel; this is the other direction and is not
  in its scope.
* **The trim & stability sweep** (note 57 §8) — the re-run of the balance
  across a CG range. Its two figures port (§7); the sweep does not.
* **R-57.5's rename mechanics** — unchanged, still at the end of the milestone.
* **A view toggle hiding the extension tier** — unchanged.
* **`app_shell/` slimming** — **done 2026-09-13** (note 57 §8 carries the
  measurement). `limit_csv`'s three CSV builders and the whole of
  `optional_slice` were what the deletion left unreachable; the module itself
  stays, because its `*_limit_rows` half is what the analysis pages' station
  tables are built from.

---

## 10. The band B5 sequence, revised

```
#265  JSON editor to app_shell/                        (S)   note 57 D-57.3
#239  oracle_app into _GUI_TREES                       (S)   pulled from B6 — gates 4/5 need it
#266  Two marked field tiers                           (M)   D-57.2; gates 4, 5, 7 assert here
#267  Figures: one producer set, two renderers         (L)   D-60.1…D-60.6
#268  Fleet comparison ports                           (S–M) D-57.5
#269  Seed button, built with its hardening            (S)   D-57.7
#241  Applied-load CSV case identity                   (M)
#242  The axis stanza                                  (S)
#245  data/ the single CSV channel (widened)           (M)   D-60.12
#278  Summary-report merge, then build_report retires  (M–L) D-60.7…D-60.11
#270  app/views/ retires; derived set re-cut           (L)   D-57.1 + D-57.6
#255  Tail Span Loads prose — closes superseded at #270 (S)
```

Note 57's D-57.8 rule is unchanged and still governs: **the surviving GUI is
complete before anything is removed.** Two rows are added to satisfy it rather
than to extend it.
