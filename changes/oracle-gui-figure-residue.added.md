- **The last of note 60 §1.1's twenty figures is settled (note 60 §9 amended
  2026-09-13, tier M, 2026-09-13).** Three figures had no report producer at
  #267 and were reported at its close rather than left for `app/views/`'s
  deletion to discover. Each now has a ruling: one ports, one retires
  superseded, one is deferred with the capability it actually needs.

- **Item weight against fuselage station ports (note 60 §1.1 figure 6).** Every
  row of the weight data base drawn at its entered station, split by loading
  kind — empty weight, minimum flight weight, discretionary — each kind with its
  own marker shape, because *when* an item is aboard is the first thing a mass
  at an extreme station has to be read against. It is a **pre-run** family on
  the Weight & Mass page and the oracle report's section 2.2 prints it, so it
  meets the parity gate like every other figure. It was blocked at #267 only
  because the model had no way to say "a cloud of named points"; #268 added
  exactly that for the fleet scatters, so the blocker was gone as soon as they
  landed.

- **A marker series may state its shape (`mark=…` in `Series.style`).** Honoured
  by both renderers — `plots_tex` emits the pgfplots mark, `app_shell/plots.py`
  maps it to a Plotly symbol. Shape rather than colour, because
  `SUMMARY_REPORT.md` §4.3 requires a printed figure to read in greyscale and
  three clouds of identical dots are one cloud. No new member: the style channel
  the producers already write was the right place.

- **The wing + fuselage total-loads snapshot retires superseded (figure 18).**
  Its two halves are the wing and fuselage net-load distributions, which #267
  put on the pages that compute them; a third axis carrying both adds a view,
  not a fact.

- **Imported against computed is deferred, not retired (figure 19).** It needs
  an **inbound** CSV channel the survivor does not have — which columns, which
  stations, which units, and what a disagreement between the two is *said* to
  be: a design note's worth of questions, not figure plumbing. Filed as backlog
  band C — *additional analysis capability, design notes first* — with the
  figure named as its first consumer. #245 settles `data/` as
  the single *outbound* tabular channel and does not cover this direction.
