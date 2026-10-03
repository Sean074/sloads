- **A non-finite number cannot reach a delivered deck: the card formatter refuses a NaN or an infinity by name, as every other delivered channel already does (#341, tier S, 2026-10-03).**
  `%E` of a NaN is the string `NAN`, and `deck_format.fmt` had no finite
  guard, so the solver channel — the primary deliverable — was the one
  channel that would print an upstream defect into a shipped `.bdf` while
  the Beam Model page showed the success toast (`units.format_value` has
  guarded every human/CSV cell since #303/#316). `fmt` now raises
  `NonFiniteValue`, and because every `.bdf` writer formats its card values
  through `fmt`/`fmt3`, the single raise covers the package. `fmt3` refuses
  before its dust snap, where the guard found a second path worse than the
  first: an infinite component is also the card's own scale, so `snap_zero`
  floored every component against it and the card printed all zeros —
  silently. Found by the 0.8.8 pre-release review.
