- **The applied load set is re-aggregated onto the LRA grids (note 56 D-56.9,
  tier L, 2026-09-12).** The eighth slice of note 56, and the one the decision
  had to be rewritten for. Implementation reached D-56.9 as written — *"the
  appendices quote the node the deck carries the load at"* — and found it
  unbuildable: the LRA deck emits one `SUBCASE` per **balanced** case and sums
  every source onto each node, so a card at a grid corresponds to no single
  station-level row and the card-first gate had nothing to match. The owner's
  answer (rulings 13–15, 2026-09-12) went further than the options put up: the
  loads are **summed** to the LRA grids, not relabelled with them, and the
  report states the difference that produces. `applied_loads` now returns one
  row per (case, grid) through LM-1 — `gear_loads.transfer_couple`, the same
  owner `lra_model.transferred_case_loads` uses, so there is one routing rule
  and not a second written for the report. `station_applied_loads` keeps the
  un-lumped set under its own name; `project` becomes required.
- **A cross-case defect, caught by a guard that was not looking for it.** The
  first version keyed the accumulator by `gid` alone. `applied_loads` returns
  every case concatenated, so `W-01`'s load at a grid was summed into `W-02`'s,
  collapsing the file to one row per grid under an arbitrary case's label and
  factor. None of the new gates saw it — the *mixed-basis safety-factor* guard
  did, on `atr42_100`, because the merged row took one case's SF into a file
  that should have carried two. Keyed by `(case, gid)`, and gate 13 is asserted
  per case for the same reason.
- **The structural zeros are gone, and that is the physics working.** Moving a
  force across an offset makes a couple about the transverse axes — which is
  precisely what keeps the resultant exact. `Mx` goes from identically zero at
  the stations to **839 lb-in** on `baron_58`'s h-tail rows and 869 on its fin,
  and the fin gains a small real `My` (1.2–4.8 lb-in) from its axial `Fz` moved
  fore-aft. G-OR-92 failed, correctly. The appendix notes are re-cut through one
  shared wording, `LUMPED_SET_NOTE`, because four paraphrases of one claim is
  how note 44 OR-139 happened; `ORACLE_REPORT.md`'s B.1 rules are re-cut to
  match, distinguishing what is zero at a station from what is zero in the
  delivered set.
- **A concentrated mass stops being an appendix row of its own.** It is summed
  into its grid's row, so "Engine+prop+nacelle" is no longer a caption anywhere
  in B.1. A real loss of reader value, stated in the spec rather than absorbed:
  the item's identity and weight live in the weights tables, and B.1 promises
  the load a model is given. #166's actual requirement — that the point-mass
  inertia relief is not silently missing, 4,821.5 lb of a 5,004.1 lb root shear
  on `baron_58` — is unchanged, and its gate is re-aimed at that rather than at
  the caption it used to be checked through.
- **Two gates were comparing points and only now had to say so.** The SI
  root-closure gate took moments about the first row's point, which used to be
  the root station and is now the first grid; re-pointed at the root station's
  own coordinates it closes exactly through a full CSV round trip, which states
  LM-1 more strongly than the arithmetic test beside it. The B.1-vs-CSV gate
  began failing by 4 lb-in on a 14,464 lb-in `Mx` — both sides are one list, but
  the table renders four significant figures (`-1.446e+04`) and the CSV carries
  the full value. Invisible while `Mx` was zero everywhere. The rendering is
  #161's row; the gate takes a relative tolerance with the reason recorded.
- **A refusal that was not the refusal.** `build_lra_model` raises `LraRefusal`
  for a named missing datum, but `require_integrable_planform` raises a plain
  `ValueError` — so catching only the subclass turned `oracle_report_vtail`'s
  deliberately inconsistent fixture from a rendered appendix into a crash. Every
  `ValueError` from that builder means one thing here: no beam, so the
  station-level set, with `gid` a station number as it was before D-56.9.
- **The digest baseline is the evidence this went as intended.** Exactly four
  channels moved — `sbeam/{wing,body,htail,vtail}_applied` — and 52 held
  byte-identical. That is gate 8 with its one stated exception, read off the
  artifacts rather than argued.
- **What is not done.** D-56.10's VMT comparison has its reference curve
  (`station_applied_loads`, public and gated) and nothing draws it, so the
  appendix notes point at a comparison that does not exist yet. That is the next
  slice, not a later one.
