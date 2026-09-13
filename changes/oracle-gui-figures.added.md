- **The oracle GUI gains every figure the oracle report carries, under one owner
  (#267, design note 60 D-60.1…D-60.6, tier L, 2026-09-13).** The surviving
  front-end carried no chart of any kind while the retiring one carried twenty,
  nine of them on pages the survivor already rendered. `sloads/report/figures.py`
  is the new **figure catalogue** — one row per figure *family*, naming the page
  that shows it, the producer that builds it, and whether it is **pre-run**
  (entered data drawn, rendered under the form so a shape can be checked before
  the analysis is run) or **post-run** (a result, rendered under the results,
  every load on it LIMIT). `app_shell/plots.py` renders a `PlotData` as Plotly
  and is a **peer** of `plots_tex`'s TikZ over the same producer set: the GUI
  derives no figure data of its own, and a guard walks the GUI trees for a
  `PlotData` or `Series` constructor to keep it that way.

- **Nineteen figure producers become callable per figure (#267, note 60 D-60.3).**
  They were reachable only through a built report bundle, which defeats the use
  the port was asked for — checking the inputs *before* running the whole
  process. Each is now a public function of `oracle_sections.py` taking a
  `Project` and, where the figure genuinely needs them, the module results; the
  report's own section builders call the same functions, so there is one
  construction of each figure and not two.

- **The report gains the balancing tail load and the static margin against CG
  (#267, note 60 §7).** The two figures note 57 §8 deferred, built from the
  existing `trim_sweep` and the Configuration module's tail-volume neutral
  point — swept at the heaviest loading over the entered CG range, with the
  project's own cases marked on the curve. The interactive sweep (a reader
  choosing the loading, the range and the station count) stays deferred.

- **`Figure.family` (#267, note 60 D-60.2).** A key names one drawing, a family
  names the kind, and the two differ wherever a producer emits a run — `vn_0 …
  vn_14` is one family, because how many V-n diagrams a project has is a fact
  about its loadings. Carried as data stated by the producer, not pattern-matched
  out of a key by the guard.
