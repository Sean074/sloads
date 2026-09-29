## Step — The engine axial loads of both deck families: the one-engine-out hub carries the propeller's own windmill drag when entered and the stated Glauert bound otherwise, and every gyroscopic case applies every engine at one airplane state (#319, design note 66 D-66.12a/D-66.4a, tier L, 2026-09-29)

**Objective.** Close #319, the 0.8.7 release review's question whether the axial loads the two new families put at the hubs stand as LIMIT loads. The one-engine-out case delivered ONENGOUT's Glauert windmill drag (on the ATR +13,004 lb at VC and +20,319 lb at VD at the failed hub), a term the method used only as a yaw forcing and the manual calls the most the drag "can not be more than" (Ch 11 p88); nothing said it was a bound. Each 23.371(b)/25.371 case thrust its own engine alone, so on the ATR 10,865 lb at y = ±161 in, a 1.75 M lb-in yaw that the closure reacted with an acceleration no part of the airplane produced.

**Deliverables.**
- **The windmill drag (D-66.12a).** A new optional input, `EngineInput.windmill_drag_cd`: the windmilling propeller's disc drag coefficient, from the maker's data or the 23.367(a)(3) history. Schema v71; `_hop_70` is an identity and the first hop after a released schema.
  - When it is entered, the failed hub carries `C_D · q · πD²/4` on the march's own ramp. The owner is `one_engine_out.windmill_drag_from_cd`. `disc_drag_coefficient` reads the bound back from the Glauert term (0.502), so the coefficient is never restated.
  - When it is blank, the hub carries the Glauert term, and every case states it as the method's conservative upper bound and names the input that replaces it.
  - The ONENGOUT march and the fin loads always use the bound.
  - A twin is reflected only when both engines enter the same coefficient.
- **The gyroscopic cases (D-66.4a).**
  - Every engine's ENGLOADS thrust and couples are applied at the same sub-case, and every entered hub thrust is replaced.
  - ENGLOADS now signs the propeller's spin by `prop_direction` (`engine.spin_sense`, `engine.angular_momentum`), as it already signed a turbine rotor's by its `max_rpm`. A sub-case's signs are therefore the airplane's rates on every engine. This amends note 53 D-53.6. No ENGLOADS number moves, because every fixture propeller is clockwise.
  - The case keeps its engine's EM id. It states the net axial force the `n_x` relief reacts, and whether the engines spin together.
  - On the ATR, co-rotating: the couples add, `ṙ` goes from −0.0022 to ±0.0004 (in the closure's per-inch units), and `Δn_x` from −0.79 to −1.12.
  - On the RJ, whose fans counter-rotate: the couples cancel.
  - The report's §10 rotation statement is corrected to match.
- **The #321 engine riders.**
  - `IN_PER_FT` and `VERTICAL_KEYS` are used instead of local copies.
  - `ROTATION_FIXED_SOURCES` and `engine_member` have one owner, in `balance.applied`, which `lra_model` uses too. The restatement and its guard are gone.
  - `coordinates.side_of` is the one side tag.
  - `_MIRROR_TOL` is split into a length tolerance and a load tolerance.
  - Two cases are now recorded instead of shipped: a case scaled by zero (`unscalable`) and a hub off the engine's butt line (`hub-off-arm`).
  - The missing type hints are added.
- **The digest wave: 10 Imperial channels.**
  - `atr42_100` and `concept_regional_jet`: the balance CSV and text, the balanced deck and the LRA deck, from the gyroscopic cases.
  - `baron_58`: the balanced deck and the balance text, from the one-engine-out statement alone. No OEI number moves.
  - `ga6_normal` and `concept_heavy` are unchanged.

**Test.**
- `tests/test_engine_mount_cases.py`:
  - G-66.4 carries every engine's increment at its own nodes.
  - G-66.5 builds the parent without every entered thrust.
  - G-66.17: every gyroscopic case thrusts every engine and, on a symmetric installation, yaws on none.
  - The sub-case is the airplane's rates on every engine: the ATR's couples add, the RJ's cancel, and a counter-clockwise propeller's are reversed.
  - A zero scale is recorded.
- `tests/test_engine_out_cases.py`:
  - The entered coefficient is delivered and the bound is stated.
  - G-66.9 as amended: `[I]{Δω̇} = ΔM` of the drag difference.
  - A twin needs both engines' coefficients to agree.
  - A hub off the arm is recorded.
- `tests/test_hub_thrust.py`: G-12b as amended.

**Key decisions.**
1. **The pairing rule was re-ruled in the build.** Note 66 §12 as first agreed paired counter-rotating engines by flipping both signs, keyed on `prop_direction`. The RJ showed that ENGLOADS already signed a rotor's spin and not a propeller's. The owner ruled (a): sign the propeller's spin too, and pair sub-case k with k. `Rotor.direction`, which no code reads while the sign lives in `max_rpm`, is filed as #332.
2. **The fin load keeps the bound's forcing.** An entered coefficient moves only the hub load and the closure's yaw, by exactly its own moment. Owner ruling (a′).
