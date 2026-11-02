# sloads

A modern Python + Streamlit replication of the **FAR 23 LOADS** suite (Hal C.
McMaster, Aero Science Software): the structural design **limit** loads of a
small aircraft under FAR Part 23 Subpart C, from one `project.json`, through a
page-per-step GUI or a CLI, out to load-case tables, a technical report and an
**sbeam** beam-model deck for sizing. The FAR23 core is validated against the
manual's printed worked examples; a `concept` mode grows it toward larger
airplanes. **License:** MIT (see [LICENSE](LICENSE)).

## Quickstart

**Python 3.12, and only 3.12.** The developer's gate and CI run one
interpreter, so a byte that differs between two Pythons cannot pass one and fail
the other (#327); `pip` refuses any other version, and so does the test suite.

Two ways in. **To develop, or to run the bundled examples** (only the clone
ships them), clone the repository and install it editable; everything else in
this file assumes that tree:

```bash
git clone https://github.com/Sean074/sloads.git && cd sloads
python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev]"   # not `python3`: whatever that resolves to is refused
.venv/bin/sloads-oracle                                          # the GUI (or: .venv/bin/streamlit run oracle_app/Oracle.py)
.venv/bin/sloads engine examples/ga6_normal.project.json -o engine_loads.csv   # one CLI case: the manual's Appendix A airplane
```

The same steps on Windows, where the python.org installer's versioned command
is `py -3.12` and the venv's programs are under `.venv\Scripts\` — one command
per line, because `&&` is not in every Windows shell:

```bat
git clone https://github.com/Sean074/sloads.git
cd sloads
py -3.12 -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
.venv\Scripts\sloads-oracle
.venv\Scripts\sloads engine examples\ga6_normal.project.json -o engine_loads.csv
```

**To run the program alone**, install the wheel that every tag's
[release page](https://github.com/Sean074/sloads/releases) carries (#396) into
a venv of its own — the two file names are on the page, `vX.Y.Z` is the tag:

```bash
python3.12 -m venv sloads-env && sloads-env/bin/pip install https://github.com/Sean074/sloads/releases/download/vX.Y.Z/sloads-X.Y.Z-py3-none-any.whl
sloads-env/bin/sloads-oracle                                     # the same GUI and CLI, from anywhere
```

The wheel ships the GUI and the CLI but not `examples/`: the CLI line above
then takes a `project.json` saved from the GUI, or one downloaded from the
repository's [`examples/`](examples/) folder.

On Windows the wheel install takes the same two substitutions, `py -3.12` and
`sloads-env\Scripts\`. Either install registers `sloads` and the `cli` module
on `sys.path`, so imports work from anywhere, including inside Streamlit.

Where to read next:

- **Using the GUI, page by page:** [`docs/60_guide/00_index.md`](docs/60_guide/00_index.md)
  (start at [Getting started](docs/60_guide/01_getting_started.md)); the
  task-oriented guide to the whole application, including the report and the
  sbeam deck, is [`docs/10_standard/GUI_USER_GUIDE.md`](docs/10_standard/GUI_USER_GUIDE.md).
- **What ships and what every number means:** [`CAPABILITIES.md`](CAPABILITIES.md);
  the conventions (axes, signs, units, the limit/ultimate contract) are
  [`docs/10_standard/CONVENTIONS.md`](docs/10_standard/CONVENTIONS.md).
- **Contributing:** [`CONTRIBUTING.md`](CONTRIBUTING.md), then the standard in
  [`docs/10_standard/`](docs/10_standard/00_program_overview.md); the whole
  documentation tree is mapped by [`docs/00_INDEX.md`](docs/00_INDEX.md).
- **Release notes:** [`docs/90_record/CHANGELOG.md`](docs/90_record/CHANGELOG.md).

## What it is

The original suite is the 22-program package that computes the structural
design loads a small aircraft must sustain under **FAR Part 23 Subpart C —
Structure**. sloads ports those programs into one shared calc package and is
being grown into an **initial-concept distributed-loads tool**: a `concept`
mode that can exceed the FAR23 weight/seat limits, assessment against similar
airplanes, per-component distributed loads (wing / body / tail + simplified
control-surface distributions), and export to **sbeam** for structural sizing.
The FAR23 replication core stays validated against the manual; concept mode is
a superset of it. See
[`docs/30_future/01_concept_loads_plan.md`](docs/30_future/01_concept_loads_plan.md).

The codebase is a shared pure-calc package (`sloads`) plus a multi-page
Streamlit UI (`oracle_app/` over the shared `app_shell/`) and a CLI (`cli.py`).
A single reloadable `project.json` carries every module's inputs; each module
emits its own load-case CSV.

> **Release state.** Core analysis developed per FAR 23 LOADS and the GUI production-ready; concept-mode features in beta.
>
> *(One owner: `app_shell.components.RELEASE_STATE`, which the GUI's About
> panel and `CAPABILITIES.md` also carry, and which `pyproject.toml`'s
> `Development Status :: 4 - Beta` classifier points at — a trove value cannot
> express a mixed state. Guarded by `tests/test_doc_currency.py`.)*
>
> **Status:** Phases 0–2 and Phase-C Steps **C0–C11** complete — **all 22 of 22**
> Reference 1 Appendix-C suite programs ported (ENGLOADS, WTESTIMA, WTONECG, WTENV,
> WINGGEOM, STRSPEED, MACHLIM, TAU, AIRLOADS, AIRLOAD4, FLTLOADS, SELECT, WINGINER,
> NETLOADS, TAILDIST, AILERON, FLAPLOAD, TABLOADS, ONENGOUT, LGFACTOR, LANDLOAD,
> BALLOADS) plus two modern modules (`configuration`, `body_loads`). The current
> schema version, test count and coverage are whatever CI reports on the latest
> commit — see the Actions tab and the changelog, not a number baked in here. The
> wing distributed-loads
> vertical slice (geometry → speeds → V-n envelope → airloads → inertia → net)
> exports to sbeam; the critical-load selection (wing / h-tail / v-tail / fuselage),
> chordwise tail distribution, simplified control-surface distributions (aileron /
> flap / tab), one-engine-out vertical-tail transient, and tricycle-gear
> landing/ground loads are complete (FAR23 path oracle-locked). Step-by-step plan
> for remaining refinements: `docs/30_future/00_backlog.md`; Phase-C narrative:
> `docs/30_future/01_concept_loads_plan.md`; roadmap: `docs/10_standard/PROJECT_GUIDE.md`.

## Layout

```
sloads/                 # shared, pure-calc package (no I/O in calc)
├── constants.py          # g, pi (math.pi), unit factors, atmosphere — centralized
├── models/               # Project + per-domain slices, ConditionResult, ModuleResult, SCHEMA_VERSION
├── units.py              # Imperial<->SI conversion at the I/O boundary
├── io.py                 # load/save project JSON; load-case CSV writer
├── registry.py           # name -> run(project) -> ModuleResult
├── workflow.py           # the step graph and the GUI page set — the nav SSOT
├── report/               # the oracle technical report: sections, figures, LaTeX, the issue package
├── export/               # output renderers (sbeam bridge); not registered modules
└── modules/              # one file per program (engine, weight_*, wing_*, airloads,
                          #   flight_envelope, select, net_loads, body_loads, configuration, …)
app_shell/               # the app-layer shell: project state, sidebar, page scaffold, unit boundary, JSON editor, figures
oracle_app/
└── Oracle.py             # st.navigation entry point — the page set from workflow.gui_pages() (the analysis steps, plus the JSON editor, fleet comparison and Report)
cli.py                    # python cli.py engine project.json -o out.csv
tests/                    # pytest; each module vs the manual's appendices
examples/                 # ga6_normal (Appendix A) + baron_58 (normal-cat twin), atr42_100 + atr42_300_seed (its sconfig re-sizing) + concept_regional_jet (concept) run the full workflow; concept_heavy is a minimal concept-core demo (V-n → Flight Envelope only)
docs/                     # by type: 10_standard, 20_theory, 25_notes, 30_future, 60_guide, 90_record (see docs/00_INDEX.md)
pyproject.toml            # build metadata, deps, ruff + pytest/coverage config
cspell.json               # domain wordlist
```

## Developing

`pyproject.toml` is the single dependency source — `pip install -e .` for the
runtime set, `pip install -e ".[dev]"` for the supported developer install (a
second `requirements.txt` list was deleted at 0.5.0 because it had drifted from
it). The green-build gate, run from the venv:

```bash
pytest                                                      # the suite
ruff check sloads/ cli.py oracle.py app_shell/ oracle_app/ scripts/                        # lint
mypy                                                        # type check (sloads/)
```

CI (`.github/workflows/ci.yml`) runs the same three on 3.12 for every pull
request, every push to a `dev/**` milestone branch and the push to `main`,
which alone adds the coverage measurement. How work moves (branches, closure,
issues) is [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Validation & math fidelity

The math is **modernized** (`math.pi`, clean equations). The manual's printed
worked-example figures are used as **tolerance-based** regression oracles
(±0.1%), not exact oracles — see `docs/10_standard/PROJECT_GUIDE.md §6`. The oracle is
Reference 1 (`FAR23Loads_Code.pdf`, McMaster's theory manual). **Appendix A**
(6-place GA single, p131) is the printed oracle and is in hand; **Appendix B**
(10-place twin turboprop, p251) is **absent from the bundled PDF**, so modules with
GA-single figures are *oracle-locked* against Appendix A while twin/turboprop-only
cases (e.g. `one_engine_out`, the turbopropeller engine-mount case) are
*closure-locked* to the `.BAS` source with the printed twin oracle deferred. The
canonical, per-module validation status lives in
[`docs/20_theory/00_theory_sources.md` § Oracle status](docs/20_theory/00_theory_sources.md#oracle-status).

## Units

A sidebar toggle switches inputs and results between **Imperial** (lb, in, ft-lb,
hp) and **SI** (kg, mm, N·m, kW). It is purely a presentation layer: calculations
always run in the Imperial units of the original program (`sloads/units.py`
converts at the boundary). Saved project JSON is always canonical Imperial.

## Disclaimer

This project is an independent, modern **open replication** of the FAR23 loads
suite (DOT/FAA/AR-96/46; Hal C. McMaster's CAE theory manual, Aero Science
Software). It is intended as an educational and exploratory engineering tool,
validated against the worked examples printed in the reference manual.

It is **not affiliated with, endorsed by, or associated with McGettrick
Structural Engineering, Inc. or DARcorporation**, whose "FAR 23 LOADS" is a
separate commercial product.

Results are **not certified** for safety-critical, regulated, or
certification structural design. The replication modernises the math (clean
equations, `math.pi`) and validates to a ±0.1% tolerance against the manual's
printed figures — it is not bit-for-bit identical to the original program.
Verify any results against the original suite, an established method, and
competent engineering judgement before relying on them for design or
airworthiness decisions.

The software is provided "as is", without warranty of any kind. See the
[LICENSE](LICENSE) file for the full disclaimer of liability.

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Sean O'Meara.
