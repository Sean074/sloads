- **The note 66 and note 52 gates compare against figures that do not share the code's derivation, and G-66.5 is the gate the note agreed (#318, tier S, 2026-09-28).**
  The 0.8.7 review found gates that re-derived what they checked (P-2). G-66.5
  now assembles each engine-mount case's parent itself, scales it by hand, and
  finds it load for load at the head of the case with only the engine increment
  and its relief after it. Before, it checked a closure true by construction
  and skipped every gyroscopic and inclined-torque case. G-66.3 pins each case's
  load factor from the rule and the engine's entered `limit_load_factor`, not
  from ENGLOADS's vertical ÷ PPWT. G-66.1 pins 1.0 on 23.367(a)(2) and 1.5
  elsewhere, not the safety-factor table the stamp itself asks. G-66.10 compares
  the reflected twin, load for load at rel 1e-9, with the mirrored engine's case
  built directly from its own march (6e-15 on both twins), and its engine pair
  with `engine_forces_at`. The report's OEI butt-line checks compare against
  the entered `engine_cg` rather than the side owner under test; the printed
  butt line itself is unchanged (−66/+66 in on the Baron, −161/+161 on the ATR,
  the entered positions — #285 reversed the fin-load sign, not this). Note 52's
  delivered condition A root and aileron deflection are asserted against the
  print (+516,955 lb-in p. 206, 10.703° p. 93, ±0.1 %), the literal-arithmetic
  knit test is removed, and note 52 states that G-52.4/G-52.11 are
  characterization pins under the amended 75 % rule. From #322:
  `test_rolling_conditions.py` gains its `__main__` runner, loses its
  `sys.path` shim and states UNB with its sign, and the ENGLOADS test name is
  spelled right. No delivered load moves. Found on the way and filed for the
  owner: `baron_58`'s engines enter `limit_load_factor` 4.2 against the
  airplane's 23.337 n₁ of 3.648, so its 23.361(a)(1)/(a)(2) cases fly the
  airplane at 3.15 / 4.2 g.
