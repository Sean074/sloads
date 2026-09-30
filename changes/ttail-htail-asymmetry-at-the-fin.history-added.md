## Step — A T-tail's fin carries the horizontal tail's asymmetry: the AC 23-9 induced rolling moment in every fin condition, one-engine-out included, and the 23.427(a) case through the fin, with the horizontal-tail assumption checked (#328, design note 51 D-51.1a–D-51.11, tier L, 2026-09-29)

**Objective.** Close #328. Note 51 had been AGREED since 2026-09-06 with no issue and no code, and was written against the per-component fin deck note 56 deleted. It was re-scoped against the LRA deck and re-AGREED in session (§9). What the tree did on the two shipped T-tails, measured first:

- **The 23.427(a) roll.** It reached the fin root in the deck exactly (RJ ±72,547, ATR ±30,622 lb-in), but no gate asserted it and the fin view never showed it.
- **The AC 23-9 ¶5a induced rolling moment.** It was absent everywhere. On the RJ it is 27–73 % of the fin's root bending.
- **The ATR's one-engine-out cases.** They govern its fin (889,475 lb-in, 3.6× the four 23.441/23.443 conditions), which meets the trigger note 51 §8 had set for adding them.

**Deliverables.**
- **The induced rolling moment (D-51.3a/D-51.3b).** `tail_span.induced_roll_moment` computes `M_r = 0.3 q S_H b_H β` and returns an `InducedRoll` record: the moment, β, q, Mach, altitude, basis and dihedral.
  - **β.** The fin's own side load, expressed as an angle on SELECT's AVT. This reproduces `RD·EFV·EFFECTV`, the owner's net 19.5° − that, and 15° exactly, and gives each engine-out case its peak fin load as an angle. The side gust takes the AC's `1.2 U/V`.
  - **Sense.** The moment has the sign of the fin's own root rolling moment (AC ¶5d).
  - **Magnitudes.** RJ 137–374k lb-in. ATR 54–162k lb-in in the four fin conditions, and 329k (VC, ultimate) and 459k (VD) lb-in in the engine-out cases.
- **The fin view (D-51.1, D-51.1a, D-51.10).**
  - `TipTransfer.mxx` carries the induced moment, along with its record (`induced`) and the pairing point (`paired_case`). T-16 is narrowed to the symmetric pairing.
  - An engine-out fin result is paired at the 1 g parent the deck assembles it on. That lookup now has one owner, `engine_out_cases.oei_parent_point`, and the march altitude has one owner, `one_engine_out.case_altitude_ft`.
  - `ttail_transfer_to_airplane` passes `mxx` through, and the applied-load row carries it.
  - Each fin result publishes its root rolling moment including the tip set (`vtail_root_mxx_with_tip`).
- **`HTAIL UNSYM` (D-51.2a).** A new fin condition, VT-20, in a new band `VTAIL_BAND_TTAIL` (23.427(c)).
  - Its tip carries the 23.427(a) table's own stations: `fz`, `myy` about the tip, and the net roll `mxx`. The fin carries no air load of its own in it.
  - It is in the fin view only. The deck's 23.427(a) case already carries the roll, as strips (D-51.5a).
- **The deck (D-51.4a).** Each T-tail lateral and one-engine-out case carries one free couple at the fin tip, source `vtail-induced-roll`, read from the transfer's `induced` record and never from `mxx`.
  - The closure's roll acceleration ṗ reacts it, and the case states it in band (`INDUCED_ROLL_NOTE`).
  - The deck's fin-root moment goes up by exactly `M_r`: RJ yaw 15° from 522,579 to 833,148 lb-in; ATR engine-out VD from 889,475 to 1,348,459 lb-in.
- **The stated limits (D-51.7, D-51.8).**
  - `check_htail_under_induced_roll` compares `M_r/2` per side with the horizontal tail's governing root bending, on one factor basis, and states the ratio on each result. RJ ≤ 53.4 %; ATR VC 67.9 %. The ATR's VD engine-out case is **142.2 %**, so its warning fires on the shipped fixture.
  - `validation._check_ttail_induced_roll` raises three warnings on the Tail Loads page: `ttail_induced_roll_sizes_htail`, `ttail_induced_roll_mach` (above 0.6, owner Q2; the RJ's side gust is Mach 0.692) and `ttail_htail_dihedral`.
- **The report (D-51.11).**
  - A T-tail's fin is no longer withheld: 6.5 and Appendix E publish, and 6.5 states the three tip sets and each condition's numbers.
  - Section 5's pointer says the horizontal tail's loads exclude the induced moment.
  - A V-tail and a cruciform still withhold. The dead T-tail branches of the withholding text are removed.
- **Rider (rule 4).** The 23.333(c) gust velocity had four copies (`flight_envelope`, `vn_diagram`, and SELECT's lateral and h-tail gusts). It now has one owner, `constants.gust_ude_fps`, and no conventional fixture's digest moved.
- **Schema v72, with an identity `_hop_71`.** `TipTransfer` is persisted, so the new fields (`mxx`, `paired_case` and `induced`, which holds an `InducedRoll`) change a persisted shape. Note 51 D-51.1's "no hop" predated #310's released-schema rule and is corrected in §9.7. The five examples are re-stamped.
- **Note 21 §5** now letters the fin-with-horizontal case 23.427(c).
- **The digest wave: 16 Imperial channels**, the same 8 on each T-tail (`concept_regional_jet`, `atr42_100`): the case index, the balance CSV and text, the tail-span CSV and text, the balanced deck, the LRA deck, and the fin's applied deck. `ga6_normal`, `baron_58` and `concept_heavy` do not move.

**Test.**
- `tests/test_ttail_induced_roll.py` (new) covers G-51.1 to G-51.11:
  - the (b) roll at the deck's fin root;
  - the engine-out pairing is the deck's own;
  - `HTAIL UNSYM` is its table's own set;
  - the deck carries one couple and never the lumped set, and its fin root equals the fin's own load plus `M_r`;
  - the formula identity and the note's measured figures;
  - the sense;
  - the fin view's root with the tip set;
  - the AC's own 4–6× band (RJ 4.28×/5.15×, ATR 4.18×/5.29×);
  - the h-tail check warns on the ATR's VD engine-out case alone;
  - the Mach warning fires on the RJ side gust alone;
  - an entered dihedral is warned and scales nothing;
  - a conventional layout carries none of it;
  - the gust rule has one owner (an AST check).
- Re-cut tests:
  - `test_balance.py`: the fin set includes the couple, and the lateral pins moved (ṗ +27–83 %, ṙ < 4 %; fin load and Ny unchanged).
  - `test_tail_span.py`: `HTAIL UNSYM` is excepted from the SELECT-pairing and chordwise gates.
  - `test_oracle_report_vtail.py`: a V-tail and a cruciform withhold and a T-tail publishes, and the case-keyed tables allow VT-20 in the spanwise pair.
  - `test_lumping.py` and `test_tail_transforms.py`.

**Key decisions.**
1. **One β rule instead of four.** Expressing each condition's own fin load as an angle makes the owner's net-β ruling (D-51.3a) fall out with no special case, and gives the engine-out cases a β without a second model.
2. **The couple is read from `induced`, never from `mxx`.** `mxx` also carries the 23.427(a) roll on `HTAIL UNSYM`, which the deck already has as strips. Reading `mxx` would count it twice.
3. **The h-tail check is on one factor basis.** The engine-out VC case is ultimate (SF 1.0) and the horizontal tail's governing case is limit. Compared raw, it would read 101.8 %; on one basis it is 67.9 %.
4. **Open: D-51.9, the ATR's tailplane dihedral.** No citable value was found in session (neither Jane's [C] nor a measurable [A] three-view was available), so the fixture still enters 0. The guard is gated on a constructed project. **Deferred with its trigger met:** the ATR's VD engine-out case puts `M_r/2` at 142 % of the horizontal tail's root bending, and the horizontal tail's own loads do not carry it. That is filed as its own issue.
