# Appendix D — Where next

This guide covers the GUI as the original suite's own input set: the fourteen
analysis pages, and the questions those programs ask. The application is larger
than that, and everything else is in the same place — since **#270** there is
one front-end, and what used to be "the other GUI" is the rest of this one.

```bash
.venv/bin/streamlit run oracle_app/Oracle.py      # or: sloads-oracle
```

The task-oriented guide to the whole application is
[`GUI_USER_GUIDE.md`](../10_standard/GUI_USER_GUIDE.md).

## What the rest of the application adds

- **Plots.** The V-n envelope drawn, spanwise load diagrams, planform and
  configuration sketches — the pictures this guide's tables imply. They are on
  the pages that produce them, in two marked blocks: what is entered, and what
  was computed.
- **The sbeam export decks.** Distributed per-component loads on a load
  reference axis and the solver decks (`FORCE`/`MOMENT` bulk data with verified
  equilibrium) — the bridge from loads to structural sizing. Headless:
  `sloads --export-sbeam out --export-target lra <project.json>`.
- **The report.** The **Report** page renders the formatted loads report and
  writes it as an issue package, whose `data/` folder carries every module's
  load cases, the applied load sets, the case index and the governing
  safety-factor table as CSV. Headless: `sloads --report out.pdf <project.json>`.
- **Concept mode.** The superset for airplanes beyond the FAR 23 band —
  concept configurations, supplemental FAR 25 cases, applicability flagging —
  which reduces exactly to what you used here on a conforming GA input.
- **The full input surface.** Fields the original suite never had (load
  reference axes, distributed masses, rotor records, declared design rates).
  They render on the same pages, marked **✦** and each stating why sloads asks
  — leave them unfilled and the GUI asks exactly what the original programs
  asked. Each is visible in this guide's generated field tables as
  `sloads`-origin.

## When to read on

Stay with this guide while the question is *"what are this airplane's FAR 23
loads, as the original suite would compute them?"* — the fourteen pages answer
it with the smallest possible input surface and the printed-oracle pedigree of
[Appendix A](A_worked_single.md). Read on when you need the loads *delivered*
somewhere: plotted, distributed on a beam axis, exported to a solver, bound
into a report — or when the airplane itself outgrows the FAR 23 band. Nothing
moves and nothing converts; the same project, the same pages, more of them
filled in.
