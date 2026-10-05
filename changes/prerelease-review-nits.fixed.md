- **Five nits from the 0.8.9 pre-release review: warnings number engines from 1, the silent-refusal guard sees a multi-statement body, the validation march states its cost, an entered VMC is tested through the deck, and a doubled word is gone (#367, tier S, 2026-10-04).**
  The windmill-coefficient warning and refusal named an engine `engines[0]`
  while the #331 warning said `engine 1`. Every warning and refusal now names
  it through one owner, `engine.engine_name`: one-based, with the
  designation, as the engine-loads section and the case labels number it
  (#231). The #344 AST guard scanned only one-statement handler bodies, so
  `x = []` then `continue` would have landed unflagged. It now scans a body
  of any length, and a probe test keeps that edge closed; no unstated catch
  surfaced. `_check_oei_not_recovered` re-runs the ONENGOUT march because
  `Project` publishes no result to read. The cost is stated where the check
  lives: 5 ms on the ATR and 9 ms on the Baron, against 0.27 s and 0.14 s for
  the whole validation pass. A deck-level test enters the Baron's published
  VMC (84 KIAS) and asserts that the pair reaches the deck on the same 1 g
  stall point as VS, not on VC's. No shipped fixture or delivered load moves.
