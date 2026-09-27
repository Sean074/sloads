- **The oracle journey's round budget counts only the reruns that type values, so `atr42_100` converges again (#311, tier S, 2026-09-27).**
  `_type_page` spent one rerun per #143 "Add" click from the same 16-round
  budget as its typing rounds. `atr42_100`'s weight page needs an add per
  entered case loading and ballast, 19 reruns in all, so its three journey
  tests errored in the slow lane, which `solo_close` does not run. The adds
  now sit outside the budget and are bounded by the page instead: each button
  is clicked once and must be gone after its rerun. The failure message is
  read from the final render; it had printed the last typing round's list,
  which showed every weight field blank. Test-only.
