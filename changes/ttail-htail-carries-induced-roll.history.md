## Step — A T-tail's horizontal tail carries the AC 23-9 induced rolling moment: each fin condition carrying it gets its own horizontal-tail condition, the deck applies the moment on the horizontal tail rather than as a fin-tip couple, and the one-engine-out march reads an entered windmill drag coefficient (#334 with #335 riding, design note 51 D-51.12/D-51.4b/D-51.7a/D-51.13 and design note 66 D-66.12b, tier L, 2026-10-04)

**Objective.** Close #334 and #335. Note 51 §9 sized the induced moment for the fin on the owner's assumption that it does not size the horizontal tail, and D-51.7 checked that assumption. On the ATR it failed: on the one-engine-out VD case, half the moment per side was 142.6 % of the horizontal tail's governing root bending, warned and not carried.

Measured first (note 51 §10.1, note 66 §13):

- **The ATR's governing h-tail root bending moves** with the moment carried, from GUST DN RETRACTED's 161,404 lb-in to ONE ENGINE OUT VD's 233,122 (+44.4 %, LIMIT). The RJ's stays at 349,920.
- **About two thirds of the ATR's one-engine-out fin load is the Glauert windmill bound,** which assumes no propeller drag limiting at all. The march could not read a cited coefficient (D-66.12a ruling (a′)). At ATR VD the peak fin load is 16,040 lb on the bound, and 11,196 / 8,314 lb at 0.25 / 0.10.

**Deliverables.**
- **The march reads the entered coefficient (D-66.12b).**
  - `CaseInputs.windmill_cd` carries it from `one_engine_out.entered_windmill_cd`.
  - `one_engine_out.windmill_drag` is the one drag owner: the entered coefficient's `C_D·q·πD²/4`, else the Glauert term.
  - `simulate` and `engine_forces_at` both read it, and `engine_forces_at`'s `windmill_cd` parameter retires. The hub drag, the fin load and the closure's yaw are one airplane state.
  - The balanced case's statement that its fin load is the bound's retires. The family refuses a non-positive coefficient by name before the march runs (#343 kept).
  - The ATR keeps the bound: no cited value (owner).
- **The horizontal tail carries `M_r` (D-51.12).**
  - `tail_span.induced_roll_stations`: the 23.427(a) case's chord-proportional shape at 25 % chord, antisymmetric, scaled so that `Σ fz·y = M_r`. Stored on `InducedRoll.stations`.
  - One h-tail condition per T-tail fin condition carrying it, `INDUCED ROLL — <fin condition>`, built by `_induced_roll_htail`. It is the fin transfer's T-5 trim load (split into `LT25`/`LT50` so its centre of pressure is the published `x_air`), plus the tail's inertia at the pair's load factor, plus the induced strips.
  - The condition takes the fin condition's safety factor (one-engine-out VC stays `ULT SF=1.0`) and FAR 23.427(c), with IDs from `case_ids.HTAIL_BAND_TTAIL` (HT-20…HT-49).
  - It reaches the h-tail table, the applied CSV, the case index and the report's h-tail section. `tail_span.chord_centroid` generalises `mid_chord_centroid`.
- **The deck (D-51.4b).**
  - `balance.applied.vtail_sets` applies the induced strips on the h-tail member, `source` `htail-induced-roll`, sides R/L, where it applied a fin-tip couple. The trim load is already in the case, lumped.
  - `INDUCED_ROLL_NOTE` is rewritten. The port twin reflects the strips through `reflect_load`.
- **The check retires (D-51.7a).**
  - `check_htail_under_induced_roll`, `InducedRoll.htail_ratio`, the `induced_roll_htail_pct` result row and the `ttail_induced_roll_sizes_htail` warning go.
  - Schema v76, with an identity `_hop_75`: result fields only, written to no file. The examples are restamped.
- **#335 ruled (a) (D-51.13).** T-5 is the only pairing policy, on AC 23-9 ¶5d p5. Plan 09 §8's row closes.
- **Docs:**
  - `PROGRAM_SPEC.md`: the T-tail fin, the new h-tail condition, the deck's lateral and one-engine-out cases, ONENGOUT's reads.
  - `CONVENTIONS.md` §7: the induced-moment row and the one-engine-out row.
  - `theory_sources.md`: the 23.427 row (¶5a, ¶5d's pairing) and the OEI windmill row (23.367(a)'s single-malfunction clause).
  - Plan 09 §8 closed. Notes 51 §10 and 66 §13 marked SHIPPED.
  - `DATA_DICTIONARY.md` regenerated.
- **Digests.** The RJ and ATR each move seven channels: `case_index`, `csv/tail_span`, `txt/tail_span`, `txt/balance`, `sbeam/htail_applied`, `sbeam/balanced_deck` and `sbeam/lra_model`. ga6, the Baron and concept_heavy are byte-identical (G-51.11).

**Test.**
- `tests/test_ttail_induced_roll.py`:
  - G-51.12: each induced set has `Σ fz = 0`, `Σ fz·y = M_r`, and each root carries `M_r/2` (1e-9).
  - G-51.13: each `INDUCED ROLL` condition's per-side root bending, all twelve rows of §10.1, plus its factor, reference and HT-20 band (±0.1 %).
  - G-51.14: the governing h-tail root bending, ATR 233,122 and RJ 349,920 (±0.1 %).
  - G-51.15: the deck rebuilt with the retired fin-tip couple gives the same `ṗ`, `q̇`, `ṙ` and fin-root `Mx` (1e-9).
  - G-51.16: the trim part is the fin transfer's `fz` and trim moment about the tip (1e-9).
  - G-51.3/G-51.6 re-cut to one induced set on the h-tail member. G-51.9 retired. G-51.11 extended to the new condition.
- `tests/test_engine_out_cases.py`:
  - D-66.12b delivery: the march's drag, the hub pair and a smaller fin load with a coefficient entered.
  - G-66.9 holds on an entered coefficient with no `ΔM` term.
  - The ATR VD fin load is 16,040 / 11,196 / 8,314 lb (±0.1 %).
- `tests/test_tail_span.py`: the root-bending and centreline-roll closures add `±M_r/2` and `M_r` on an `INDUCED ROLL` condition. The span/chord parity states the new condition beside `HTAIL UNSYM`.
- `tests/test_schema_guards.py`: the v76 hash. `tests/fixtures_imperial/digests.json` is regenerated.

**Key decisions.**
1. **One shape owner.** The induced set is `distribute`'s own chord-proportional strips with the 23.427(a) side scales, not a second linear antisymmetric shape.
2. **The deck carries the strips, not the condition.** The balanced case already holds the trim tail load lumped, so only the induced set is added. Adding the strips beside the couple would have double-counted the roll.
3. **The inertia lever is the h-tail's own convention.** G-51.16 gates the trim part's total `fz` and its air moment about the fin tip. The inertia is smeared at each strip's reference axis, as on every h-tail condition and HTAIL UNSYM, not at the transfer's lumped mid-chord station.
4. **The bound stays the ATR's fallback.** An autofeather switch would be an uncited factor, and 23.367(a)'s single-malfunction clause makes the limiter the failed item. The power-level question is under 1 % at ATR VD and stays parked.
