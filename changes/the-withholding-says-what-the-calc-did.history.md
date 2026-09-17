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
