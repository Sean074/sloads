# Balanced cases are flagged past the elevator stop, tail stall and fin stall (design note 73; #404)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-11-02** (#404; closure under the #359 rules, so one
`changes/` fragment and no history entry). AGREED 2026-11-02 — no code (owner, in session, under the solo
profile — rule 1's working-alone branch). PROPOSED the same day. The owner ruled
Q1–Q6 (§4):
- the positive tail-α limit **mirrors** the negative one (Q1);
- the ATR fixtures take sconfig's **−1.0°** stabiliser incidence (Q2);
- the fin limit is **entered only, with no default and no follow-up** (Q3);
- Q4–Q6 are ruled as recommended.

Drafted for review finding **A-2** of
[`2026-11-01_critical_review_physics_atr42_docs.md`](../50_reviews/2026-11-01_critical_review_physics_atr42_docs.md)
(Major). It absorbs #353 (rule 4).

**Scope.** The rational h-tail balance (`select.htail_balance`, Ref 1 Ch 9) solves
whatever elevator δ closes the CG moment. The fin march (`one_engine_out`, ONENGOUT)
forms whatever fin angle the yaw needs. Neither is checked against what the airplane
can reach, so unflyable states are delivered as design loads. This note adds a
**feasibility flag** on every balanced case:
- elevator δ against its stop, or stabiliser travel for a movable stabiliser;
- h-tail angle of attack and lift against stall;
- fin angle against stall.

The flag is stated in the report, the validation warnings and the deck subcase
comment. **No case is dropped and no load moves.** The ATR incidence fixture
edit (D-73.8) is the only change to delivered numbers.

Out of scope:
- iced-tail limits (sconfig's `iced_tail_factor`; sloads has no ice condition);
- elevator stall and nonlinear δ effectiveness;
- re-solving a flagged case at the limit.

The limits and the stabiliser logic are sconfig's, already cited there. They are
ported with their citations, not re-derived:
- sconfig `aero.clh_max`: Roskam Pt VII p44, Torenbeek §9.4.1 p325;
- `deck.tail_alpha_min_deg`: Torenbeek p326;
- `LowSpeedTrim.check`: sconfig theory doc 24, T4–T6.

Conventions: [`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §2 (δ TE-down +,
incidence LE-up +, α in deg). The flags are statements, not loads, so §3's LIMIT
contract is untouched.

---

## 2. Decisions (D-73.1 … D-73.10)

| # | Decision | Rationale |
|---|---|---|
| **D-73.1** | **One feasibility owner,** `sloads/feasibility.py`: `htail_state(lt25, lt, δ, V, ti)` and `vtail_state(α, limit)`, each returning a `Feasibility` of the checks run (value, limit, pass) and its `flags`. `select.stamp_feasibility` calls them once over the whole critical set and stores the flags on `CriticalCondition.feasibility`; every surface reads that field. Nothing re-derives a limit. | Rule 3. A second copy of the stop test is how one family drifts. |
| **D-73.2** | **Effective tail α is backed out of the AoA load:** `α_eff = LT25 / (a_h/57.3 · q · S_h)`. This is the #353 / `VtailCase.vtail_alpha_deg` definition, used for both surfaces. | It sees the gust increment, which the published trim `AT` omits (`select.py:1232-1273`), and the 23.423(b) increment. One definition for every family. |
| **D-73.3** | **Tail stall limit:** `TailLoadsInput.tail_stall_alpha_deg`, default **14.32°**. The 0.25 rad is Torenbeek p326, as sconfig `tail_alpha_min_deg` uses it. Applied as **\|α_eff\| ≤ limit** (Q1). Tail lift is checked too: `\|C_L,h\| ≤ \|clh_max\|`, with C_L,h = LT/(q·S_h). The default C_L,h cap is sconfig's `clh_max(stabiliser, A_h, "full")`, mirrored the same way; an entered `clh_max` bypasses it. | The owner ruled the limits entered, with a cited default. The lift cap is where the movable-stabiliser range widens: −0.35·A_h^⅓ fixed, −1.2 adjustable at full elevator, −1.0 all-moving. It binds only on the 23.423(a) full-throw cases (§3, D-73.11). |
| **D-73.4** | **Stabiliser type,** `TailLoadsInput.stabiliser`, coded `F` fixed \| `A` adjustable \| `M` all-moving (`STABILISER_TYPES`), default `F`. A movable stabiliser requires `stabiliser_incidence_nu_deg` / `_nd_deg` and refuses by name if they are absent. | This is sconfig's enum and its rule. `fixed` is today's suite, so the oracle is untouched. |
| **D-73.5** | **Authority test by type** (sconfig `LowSpeedTrim.check`, T4–T6):<br>• `F`: `−te_up ≤ δ ≤ te_down`, inclusive, so the 23.423(a) full-throw cases sit exactly on it.<br>• `A`: the stabiliser takes the 1 g trim (`i_h = IT + τ·δ_1g`, clamped to [nu, nd]; `δ_1g` from the matrix's 1 g point at the case's CG, configuration and altitude, nearest speed). The **residual** `δ − (i_h − IT)/τ` is checked against the stops; the tail α moves by `i_h − IT`.<br>• `M`: the required `IT + τ·δ` lies within [nu, nd], and the tail α is `α_eff + τ·δ`. No elevator check. | The trimmable stabiliser's extra authority is in the trim, not the elevator. The balance itself is unchanged: the flag never re-solves the load. |
| **D-73.6** | **Fin limit:** `VTailLoadsInput.vtail_stall_alpha_deg: Optional[float] = None`, **entered only** (Q3). When it is entered, it is checked on every fin family: the ONENGOUT peak `vtail_alpha_deg` and the four SELECT v-tail conditions. When it is absent, each fin condition's report note states `feasibility.VTAIL_NOT_CHECKED` (no run-level note exists on `ModuleResult`), and no fin flag fires. No shipped fixture enters one. | Q3: running the linear fin to large β is the simplified method's accepted practice (23.441 itself prescribes 15° and 19.5°), and this suite does not model fin stall. This closes #353 as a statement. |
| **D-73.7** | **The wing families** (PHAA … NNZ, ACRL) take their state from `htail_balance` re-run at their `VnPoint`, as BALLOADS does. The flag judges the *rational* state. The case still carries FLTLOADS' lumped `vn.lt`. | Owner ruling, 2026-11-02. The flag's text says which balance it judged. |
| **D-73.8** | **ATR fixtures:** `tail_incidence_deg` +1.0 → **−1.0 [E]** in `atr42_100` and `atr42_300_seed`, with the sconfig provenance in `.sources.md`. sconfig records the +1.0 as "inherited unsourced from the v0.1.0 baseline"; the −1.0 follows Torenbeek §9.4.1 p324, a small negative incidence. | Q2. IT moves the LT25/LT50 split and the rational total (the ATR UNSYMMETRICAL −4,468 → −4,533 lb), so the ATR moves in every tail channel. It shares **one Imperial digest wave** with the flag text (D-73.9). |
| **D-73.9** | **Where the flag goes.** The flag text, e.g. `FEASIBILITY: elevator -27.90 deg past the 25.00 deg TE-up stop (rational balance)`, goes to:<br>• SELECT's condition note in the report;<br>• `BalancedCaseResult.notes`, which the deck writes as `$ NOTE:` (`balanced_deck.py:381`);<br>• one `ConsistencyWarning` per flagged condition, code `balance_infeasible`, **except** a flag on a prescribed state (`feasibility.is_prescribed`, D-73.11). | The plumbing exists. The #333 warning `oei_case_not_recovered` is the pattern. |
| **D-73.10** | **The family table:** `queries.FEASIBILITY_FAMILIES`, built from the `balance/queries.py` predicates. Each family is either *checked* or *exempt with a reason*: ground has no aero. Engine-mount is exempt: its parent is a flight V-n point scaled to the mount's load factor, not a delivered condition, so it has no balanced tail state of its own (amended 2026-11-02 at implementation; the draft said it inherited its parent's flags). | It makes the drift guard (G-73.6) possible. A new family fails CI until it is classified. |
| **D-73.11** | **A prescribed throw is flagged, worded as the rule's** (owner ruling at implementation, 2026-11-02; Q4 carried to the h-tail). On the 23.423(a) unchecked manoeuvre the linear tail lift at full elevator exceeds the C_L,h cap on every fixture (0.59–0.85 against 0.56–0.59). The flag fires and says "the elevator throw is prescribed by 23.423(a), so the method's linear load is conservative". It is stated in the report and the deck and raises **no warning**: it is not an input to correct. | The regulation sets the state; the flag tells the reader the delivered load is above what the tail can make. |
| **D-73.12** | **UNSYMMETRICAL carries its governing condition's flags,** named (`[the state of …, which 23.427(a) distributes]`), and is not judged on its own scaled total. | It copies the governing split unscaled while its total is `0.5·(1 + pc)` of it (AS-2), so judging the two together would mix two states. |

---

## 3. Closure gates (G-73.1 … G-73.7)

Identities are exact. The measured figures are from 2026-11-02 at IT −1.0 on the
ATR fixtures and are frozen by name. They are not oracles; rule 2's second branch
applies.

| Gate | Statement | Expected numbers |
|---|---|---|
| **G-73.1** (oracle lock) | `ga6_normal`: Appendix A bit-for-bit. Its only flags are the three prescribed ones (UNCHECKED MAN DN/UP, UNSYMMETRICAL, D-73.11), and no `balance_infeasible` warning is raised. | 3 prescribed flags, 0 warnings, 0 fin flags |
| **G-73.2** (ATR, the A-2 finding) | Outside the prescribed flags, `atr42_100` raises one flag: the elevator stop on **BAL DN RETRACTED**, with one warning. `atr42_300_seed` is the same. The delivered PHAA, ACRL and NHAA are the aft-CG mass state (note 63: δ −20.8°, −16.1°, +13.8°) and carry none. The forward-CG air picks the draft measured are not delivered. | δ −27.90° / −27.54°, ±0.005° |
| **G-73.3** (RJ, tail α) | `concept_regional_jet` raises stop **and** tail-α flags on PHAA (δ −34.68°, α 18.52°), ACRL (−29.47°, 15.45°) and BAL UP RETRACTED (−25.79°, 17.40°), and a stop flag only on NHAA (+23.72°). The balanced PHAA, ACRL R/L, NHAA and UNSYMMETRICAL R/L carry them. | ±0.005° |
| **G-73.4** (constructed trips) | One built case per check fires exactly its own flag: δ past each stop, +α and −α past the limit, C_L,h past the cap, and the fin past an entered limit, worded per Q4 on a 23.441 prescribed angle. A case on the limit does not fire, so the 23.423(a) full throw passes the **stop** check. | 1 flag each |
| **G-73.5** (movable stabiliser) | `atr42_100` BAL DN RETRACTED with `stabiliser = A` and nu/nd = −6°/+2° clears the stop flag. With nu = −1° (= IT, no nose-up travel) it does not. `M` with −20°/+5° clears it and drops the elevator check. | flag / no flag |
| **G-73.6** (drift guard) | On every fixture every assembled case is claimed by a `FEASIBILITY_FAMILIES` row. A checked case carries exactly its SELECT condition's flags, twin included; an exempt case carries none. | — |
| **G-73.7** (no load moves) | No load CSV moves on `ga6_normal`, `baron_58` or the RJ, and every balanced-deck card line on `ga6_normal` and the RJ is byte-identical to `HEAD`: only `$` comments and the text report move. The ATR moves by D-73.8. | one digest wave |

**Closure tier: L.** It requires:
- this note at AGREED;
- `SCHEMA_VERSION` bump plus a migration (the new fields default to today's behaviour);
- `PROGRAM_SPEC.md` (SELECT, ONENGOUT, balance; the #353 sentence at `:501` replaced);
- a `theory_sources.md` row citing Roskam, Torenbeek and sconfig docs 20 and 24;
- `DATA_DICTIONARY.md` regenerated;
- one ATR digest wave, named in the fragment;
- one `changes/` fragment.

---

## 4. Questions for the owner — ruled 2026-11-02

| # | Question | Ruling |
|---|---|---|
| **Q1** | Positive tail-α and C_L,h limits? | **Ruled 2026-11-02: mirror the negative one** (`\|α\|`, `\|C_L,h\|`). |
| **Q2** | ATR stabiliser incidence? | **Ruled 2026-11-02: sconfig's −1.0 [E]** (D-73.8). |
| **Q3** | Fin stall default. The h-tail's 14.32° fires on every SELECT yaw case (23.441 prescribes 15° and 19.5°) on every fixture, `ga6_normal` included. A low-AR fin stalls later. | **Ruled: entered only, no default, no follow-up.** Running the fin to large β is typical of the simplified analysis, and fin stall is not modelled. If the field is absent, the fin is not checked, and the report states that. |
| **Q4** | Are the regulation-prescribed fin angles (23.441(a)(2), (a)(3)) checked at all? | **Ruled as recommended: checked when a limit is entered, worded "prescribed by 23.441".** The structure must carry the load either way, so the flag says the angle is the rule's, not the balance's. |
| **Q5** | The ONENGOUT VS cases run at 21°–25° fin α on all three twins (VS is the VMC substitute). If Q3 enters a limit, they flag. Is that expected? | **Ruled: yes**, when a limit is entered. It is #353's finding, and it is why #405 (the OEI basis) follows this note. |
| **Q6** | Should a flagged case still govern? | **Ruled: yes, and the flag says so** (A-2: "do not drop the case"). Re-solving at the limit is a different method, and it is not in scope. |
