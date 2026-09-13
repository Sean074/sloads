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
