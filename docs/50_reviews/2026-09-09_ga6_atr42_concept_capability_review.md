# 2026-09-09 — GA6 + ATR-42 concept capability review (both GUIs)

**Scope (owner-commissioned, 2026-09-09):** a code review of current capability, a
review of the open-issue record against it, and provision for critical future
capability — summarized as the deficient capability and erroneous output found by
analysing a **GA6** (the in-envelope reference) and an **ATR 42-300 type**
airplane (twin PW120 turboprop, 36,817 lb, high wing, T-tail, pressurized —
a deliberate concept-mode stress test far past the FAR 23 band) through the
**oracle GUI** and the **sloads GUI**. GA6 is treated as the regression baseline
for the 2026-09-08 review; only new deficiencies are flagged.

**Method.** Working tree on `dev/v0.8.3` at the 0.8.2 release state. Live GUI
exercise: `atr42_100.project.json` loaded through the oracle GUI's own example
loader, all fourteen pages walked in-session, the 121-page issue package built
from the Report page and compiled with tectonic (two passes); the sloads GUI
driven on the same project (dashboard, Tail Span Loads, Aileron Loads,
Export & Report) plus a GA6 pass. Both aircraft's full balanced free-free decks
generated from the export owner and their case maps, skip blocks and closure
residuals read line by line. CLI shakedown of every registered module on both
fixtures. GA6's report package rebuilt from the same code path the GUI's Build
button calls and diffed against the 2026-09-08 findings.

**Disposition.** Every finding below was filed the same session (rule 5): new
issues **#254** (A1, OR-133 vs T7), **#255** (A2, Tail Span prose), **#256**
(A3, engine-figure legends), **#257** (A4, mass reconcile to the document),
**#258** (A5, derived-ACRL couple statement), **#259** (A6, dashboard 🟡
legend), **#260** (§4, `atr42_100` fixture reconcile). Milestones are the
owner's call — each body carries its suggestion. A7 (stale-server ops note) is
recorded here, not filed.

---

## 1. Verdict

**The concept superset held.** The ATR-42 — 2.7× the commuter weight cap,
category C concept — runs the entire primary chain without a crash: V-n over
three altitudes with the 23.333(c) gust taper, gyroscopic engine-mount cases for
the turboprop, a signed-butt-line OEI transient with Izz read from the heaviest
mass case, a 121-page report that compiles clean, and a 43-SUBCASE balanced
free-free deck whose 28 unassembled SELECT conditions are all *principled,
stated* exclusions — not failures. The stated-limitation discipline is the
strongest part of the product: concept category, pressurization exclusion,
T-tail withholding, L-7 status and the ASSUMED thrust line all reach the
delivered document in band.

**Where it is deficient** is (a) three places where a *statement and the
delivered content disagree* — the oracle report withholds the fin's spanwise
loads claiming the T-tail load path "is not modelled" while `tail_span`'s T7
transfer models exactly that path for the deck; the Tail Span page's fixed
closing prose contradicts its own T-TAIL bullet; a derived ACRL assembles with
a silently zero aileron couple — (b) layout defects only a long-designation
twin exposes (the engine-figure legend overflows the margin on all three
views), and (c) the bundled `atr42_100` example itself, which is internally
inconsistent enough (planform area 18 % under the type's, wing-item mass 3.4×
the panel integration, fuselage stations 3,741 lb short) that it undermines the
concept fixture's role as a demonstration. GA6 regression is fully green: every
0.8.2 fix from the 09-08 review holds in the rebuilt document, and the open
items (#239, #240, #245) reproduce exactly as filed.

## 2. GA6 regression baseline

Rebuilt `report` package from `ga6_normal` compiles with **zero** TeX warnings.
Checked against the 09-08 filings:

| Finding | State |
|---|---|
| #227 attitude-label swap | **Fixed** — level-landing figure names cases 1–6/10–12, tail-down names 7–9 |
| #228 gyro boilerplate | **Fixed** — conditioned: "every engine on this airplane is a reciprocating…", no gyro case printed and none claimed |
| #230 dangling `section_ref` | **Fixed** — no unresolved keys |
| #229/#233–#236/#238 | Not re-verified individually; no regression symptom surfaced in the rebuilt tex |
| #239 ULTIMATE captions | **Still open, confirmed live** — the caption sits over LIMIT tables *and* over non-load blocks (Structural Speeds, Mach Limit) |
| #244 riders | **Confirmed live** — "Traceback (for a bug report)" renders under expected cannot-run-yet states on a fresh empty project |
| #245 channel gap | **Confirmed** — the ATR issue package contains `MANIFEST.txt`, `build.json`, `project.json`, `report.json`, `report.tex` and **no `data/`**; the report's reader cannot obtain its appendices as files from the oracle GUI |

sloads GUI on GA6: dashboard, Export & Report render fully (44 SUBCASEs,
control-surface deck present). No new GA6 finding.

## 3. ATR-42 findings — erroneous or self-contradicting output

**A1 — OR-133's withholding statement is stale against T7 (owner decision
needed).** Appendix E withholds the fin's spanwise loads: *"That load path is
not modelled, so the vertical tail's spanwise loads are withheld rather than
printed."* But `tail_span.ttail_transfer` (T7, landed 2026-08-16) models
precisely that path — the horizontal tail's concurrent load rides the fin tip —
and the sloads GUI + export decks deliver 8 fin spanwise cases (including OEI)
for the same project. The two front-ends disagree about what the suite can do.
Either lift OR-133 for T-tail projects (print Appendix E from the T7 set) or
reword the statement to say the *oracle document* withholds by policy while the
deck carries the T7-transferred loads. Guarded by `test_oracle_report_tail.py`
(G-OR-87), so the change is a deliberate re-cut, not a drive-by.

**A2 — Tail Span Loads page contradicts itself on a T-tail.** The
case-conditional bullet says the h-tail beam has **one** support — "the fin-tip
joint on the centreline… A fuselage-side pair would describe a load path this
airplane does not have" — while the fixed paragraph under the plot says "The
horizontal tail is a full-span beam… **reacted at the fuselage attachment
stations marked above**", and the plot's marker legend says "attachment". The
calc is right (T7); the fixed prose is a conventional-tail sentence rendered
unconditionally. Same defect class as #235 (fixed text wrong per
configuration); rule 4 sweep: any other fixed prose in `app/views` that assumes
the conventional layout.

**A3 — engine-installation figure legends overflow the text width** (all three
views, `Overfull \hbox` 167 pt ≈ 2.3 in, clipped at the right margin). Two
long entries — "PRATT & WHITNEY CANADA PW120 (LH) thrust line (ASSUMED)" — sit
side by side in one legend row. Invisible on GA6 (short designation, one
engine); guaranteed on any twin with real designations. Same figures: the two
application-point markers are coincident in side view and their number labels
overprint ("1" unreadable under "2"). Companion class to #240's marker-label
collisions.

**A4 — the fuselage mass shortfall never reaches the delivered document.** The
GUI's `mass_fuselage_reconcile` cross-check correctly warns (entered stations
25,210 lb vs 28,951 lb of non-wing items, −3,741 lb / 13 %), but neither the
report nor the deck states it: a reader of the issued document rides a fuselage
mass model 13 % short with no flag. The suite's own ethos (every artifact
states what it did not apply) argues the reconcile belongs in the report's
fuselage section and the `fuselage_loads.bdf` header, not only on a transient
GUI page.

**A5 — a derived ACRL assembles with a silently zero rolling couple.** The ATR
deck's W-05 ACRL is symmetric, unhanded, `wdot` roll = 0 — because a derived
wing case carries `unbal_moment = 0` (the couple comes from AILERON, whose
slice this project lacks; `wing_inertia.py:411` documents the limitation). GA6
assembles the handed pair with its measured −149,043 lb-in. The deck header
carries **no statement** that the couple is zero-by-derivation — the B7
in-band statement only renders when a couple exists. A stress analyst reading
the ATR deck cannot tell a steady-roll-has-no-couple from a
couldn't-compute-the-couple. State it in band, like the ASSUMED thrust line.

**A6 — dashboard 🟡 semantics for absent optional slices.** Aileron/Flap/Tab
show 🟡 "inputs ready, open the page to compute" when the slice does not exist;
opening the page computes nothing — it shows the input form plus "Could not
compute… no 'aileron_loads' inputs". Legend wording, not logic: the state is
"upstream ready, this page's own inputs not entered".

**A7 — stale-server hazard (ops note, no code change).** A sloads GUI server
left running across a refactor serves mixed module state: the 8502 instance
(started before the 0.8.2-cut commits) crashes Export & Report with
`ImportError: planform_geometry_condition`, while the current tree imports
clean. Worth one line in `CONTRIBUTING.md`/dev docs: restart Streamlit servers
after pulling.

## 4. ATR-42 findings — the example fixture itself

`atr42_100.project.json` is internally inconsistent in ways the GUIs surface
(the cross-checks all fired — the derive/override machinery works) but a
demonstration fixture should not carry:

| # | Inconsistency | Consequence |
|---|---|---|
| E1 | Planform integrates to **480.6 ft²**; the type's area (and the project's own `speeds.wing_area_sqft`) is **586.6 ft²** — stored but ignored because the planform owns the field | W/S 76.6 vs 62.8 psf: every stall speed, gust point and wing loading is computed on a wing 18 % small; the stale JSON field misleads |
| E2 | Wing-tagged items total **8,830 lb** vs WINGINER's integrated panel mass **2,624 lb** — the deck patches with `wing inertia scaled ×3.3650` (GA6: ×0.9903) | Wing inertia relief distribution is a 3.4× smeared guess; stated in band, but the fixture shouldn't need it |
| E3 | Fuselage stations total **25,210 lb** vs **28,951 lb** non-wing items (−3,741 lb, 8 entered vs 15 derived stations) | Fuselage shears/bendings under-read ~13 % |
| E4 | `vtail_span_in` 967.2 typed vs planform 968; `aspect_ratio_wing` 10.9 vs planform 13.54; `wing_lift_slope_per_rad` 5.3 vs cruise-set 4.58; `stall_cl` 1.55 vs `clmax_clean` 2.009; wing-weight 2,650 lb vs Ch 9 stand-in 3,314 lb | Five override warnings fire on load — correct behavior, wrong fixture state |
| E5 | No `aileron_loads`/`flap_loads`/`tab_loads` slices (→ A5's zero ACRL couple; control-surface deck "Not available"); `h_tail_z = 0.0` on a declared T-tail | The concept fixture demonstrates less than the suite can deliver |

One fix (tier M, one session): reconcile the fixture from published ATR 42-300
data end to end, with the planform re-drawn to the true area, the mass model
summing, and the three control-surface slices entered — companion to #216's
entered-vs-drawn class and #164's fixture-quality precedent.

## 5. Critical future capability (ATR-42 class), ranked

Ranked by first-order effect on shipped content for this class; existing rows
cited rather than duplicated (rule 5 — no parallel series):

1. **T-tail empennage geometry model** — the 0.8.3 headline (#25, note 51
   AGREED). The AC 23-9 method lands the h-tail-on-fin loads that A1/A2 dance
   around; resolves the OR-133 question properly.
2. **OEI fin cases in the balanced deck** — currently per-component only
   (plan 13 §4: a transient is not a steady balanced case — sound), but on a
   wing-mounted twin the OEI fin load is a primary fin/aft-fuselage sizing
   case, and a sizing loop working from `balanced_airframe.bdf` alone never
   sees it. Candidate: assemble the *peak instant* as a quasi-static lateral
   case, same machinery as B8a-3's rudder cases. Needs a design note.
3. **Aileron lift-increment distribution** (#14, band D Pri 9) — the lumped
   couple is stated (B7), but for a 968-in span the ~70 %-span distribution
   moves wing torsion materially; rule 6 measurement would rank it.
4. **Multi-wheel gear legs** — the ATR-42's twin-wheel mains are entered as
   one-wheel legs; per-wheel loads (and #241's case identity) inherit the
   single-wheel assumption. Currently unstated in the gear appendix.
5. **Pressurization** — permanently excluded (D-24) and stated in band; stays
   excluded, but the exclusion statement is doing heavy lifting for this class
   and must survive every re-cut (G-OR-73/74 already gate it).
6. **Lateral body aero L-7 on by default for large fuselages** — the
   limitations page itself quantifies the opposite-direction errors; a
   36,000-lb pressurized barrel is where the DATCOM term stops being optional.
7. **#245** — the oracle package `data/` channel: for a GUI-friendliness
   milestone, the report's own reader still cannot obtain its appendices as
   files (§2 above, confirmed on the ATR build).

## 6. What checked out (worth recording)

Category line "C · Concept (no 23.337 cap)" on page and title block; V-n
matrix 300 points over three altitudes with the 23.333(c) Ude taper
(`_gust_ude`); gyroscopic EM-06a–d assembled for the turboprop with the
±Myy/±Mzz sign convention stated; OEI Izz 6.66e4 slug-ft² correctly read from
the heaviest mass case (not the slice's zero), butt lines signed and explained
(#231's fix generalizing); landing energy N 2.3755 vs governing 2.67 with the
FAR 25.473 L=1.0 guidance beside 23.473's; the 28 unassembled conditions each
named with a reason in the deck's own `$` block; flight-case closure residuals
0.2–3.6 % of n·W (inside `FORCE_RESIDUAL_ACCEPTANCE`) with HT-09's large
pre-closure residual being the 23.427(a) physics, closed exactly; the sbeam
roundtrip/equilibrium CI matrices already carry `atr42_100`; every
cross-check the 09-08 review praised fired correctly on the ATR's inconsistent
inputs — which is how §4 was found.
