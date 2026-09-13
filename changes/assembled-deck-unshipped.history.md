- **The package delivers one solver artifact (note 56 D-56.8 + §8, tier L,
  2026-09-12).** The tenth slice of note 56 and the last of its implementation.
  The assembled full-span free-free deck stops being a shipped artifact: four
  surfaces retire in one change — the Balanced Cases page's stamped download,
  the Export & Report page's row, the `.bdf` inside the bundle `.zip`, and
  `cli.py --export-target balanced` — and the report's Appendix A manifest
  loses its row with them, because a controlling document naming a file the
  reader was never given is review F-D2's defect pointing the other way.
  `EXPORT_TARGETS` goes 4 → **3**, not the note's 2: D-56.1 reclassified the
  gear interface report as a *document* and this is still its only headless
  route.
- **Review F-D2's finding is honoured, not undone.** All four retired surfaces
  were added by 0.5.0 row 1 / D-R2 against a finding that the mission's primary
  deliverable was page-only, unstamped and unnamed by the controlling document.
  It is still reachable headless, stamped, bundled and named — it is the **LRA
  beam model** now, which carries the same assembled cases transferred onto the
  beam's own grids. Nothing left the deliverable; one of two files carrying the
  same load sets did. F-D1's reachability gate moved to follow the artifact
  rather than retiring with the file it was first written about.
- **`balanced_deck` survives, and not as a courtesy.** D-56.8's own wording —
  "its cases feed the LRA transfer and the report's `balanced_case_rows`" —
  names `build_balanced_cases` and `balanced_case_rows`, both of which live
  elsewhere; read literally, the deck writer had no consumer and should have
  been deleted like the other five. It has one and it is load-bearing: the deck
  text is the **un-aggregated load set at each load's true position**, and its
  resultant is what the transferred set is gated against (gate 13's anchor,
  `test_the_transferred_set_has_the_balanced_decks_resultant`). Deleting it
  would have deleted the reference the deliverable is checked against.
- **§8 resolved: the round-trip wrapper collapses.** `sloads/export/roundtrip.py`
  529 → **186** lines. Roughly two-thirds of it was `wrap_as_stick_model`, which
  read a deck's `GRID` cards and *invented* a tree of `CBAR`s, a `MAT1`/`PBAR`
  section, a determinate support and a case control, so that an **elementless**
  deck — a load set on a node cloud — could be handed to a linear static solve
  at all. D-56.2 deleted the per-component decks and D-56.8 unshipped the
  assembled one, so none is left; the LRA model writes its own elements and its
  own support and goes to the solver exactly as it ships. The wrapper's own
  guard had said this before it was deleted: it *refused* a deck that already
  carried `CBAR`s, because a wrapped copy is not the shipped artifact. Retired
  with it: `Support`, `Topology`, the property / element / constraint /
  case-control builders, the coincident-node collapse, the `roundtrip-rbe2` EID
  band and three wrapper unit tests.
- **Two names moved to the code that allocates them.** `_orientation` →
  `deck_format.orientation_vector`, because `lra_model` — the one deck writer
  left — was importing a private name out of a test harness to build its bars.
  `SPC_SID` → `deck_format.SPC_SID`, read by both writers: the harness held the
  constant while the two writers each spelled `1` into an f-string, so the band
  registry's declared owner was not the code that allocates the id.
- **Three solver legs moved onto the shipped deck and are stronger there** — the
  reversed-fin mutation, the displaced-`GRID` mutation and the subcase-routing
  check. The first two used to run through elements the harness made up; they
  now run through the structure that ships, and the fin mutation is applied to
  the case *before* the transfer, so it calibrates the delivery path as well as
  the solve. Their subject moved from `ga6_normal` to `atr42_100`, the fixture
  whose beam deck solves in both unit systems.
  `test_assembled_deck_reacts_to_zero` retires into
  `test_the_lra_model_solves_and_reacts_only_the_residual`, which makes the same
  free-free claim about the deck a reader is handed, over four fixtures rather
  than two.
- **The gear leg would not move, and that is Appendix G's finding arriving from
  the other side.** G-13's assertion was pointed at the beam deck first and
  failed: the deck's nose-gear trunnion carries 3,334.8 lb on
  `concept_regional_jet` against the gear report's 3,597.8, because D-56.9 sums
  whatever is nearest onto the same grid. That is the aggregation working as
  specified — Appendix G is where its size is published — and asserting the
  report's number at that grid would be asserting the lumping away. The leg
  stays on the assembled set, where a gear reference point is still a node of
  its own; it reads card text and never solved anything, so nothing is lost by
  its subject not being the shipped file.
- **Two narrowings, stated rather than absorbed.** The free-free solve xfails on
  the SI decks of `ga6_normal` and `concept_regional_jet` — sbeam's dense-path
  condition heuristic, already pinned — so those two fixtures lose an SI
  free-free solve the wrapped deck did carry; SI still runs on `baron_58` and
  `atr42_100`, and both of the xfailing fixtures solve in Imperial, which is
  what says their decks are sound. And "every assembled case reaches the deck,
  and each lateral one carries real side load", asserted *inside* the retired
  solve, becomes an assertion on the deck's card text, which is where it is
  observable.
- **`PROGRAM_SPEC.md`'s export prose was stale from D-56.2 and is re-cut here**
  (rule 4). Its validation bullet still described solving a wing stick deck and
  a fuselage deck through the test-only wrapper, and its CLI bullet still listed
  ten targets with `wing` as the default — artifacts deleted a slice earlier.
  Leaving demonstrably false prose in a spec while editing the paragraph above
  it is worse than the scope discipline that would defer it to §7's sweep.
  `PROJECT_GUIDE.md` §4's two tree lines and `CONVENTIONS.md` §7's skeleton row
  follow the code. **#173 and #176 close as superseded, not fixed:** both are
  defects in an artifact that no longer ships.
