# LGFACTOR's energy ratio is the gear factor: the wing lift is subtracted twice (design note 72; #401)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-11-01** (#401; closure under the #359 rules, so one
`changes/` fragment and no history entry). AGREED 2026-11-01 — no code (owner,
in session, under the solo profile — rule 1's working-alone branch). PROPOSED
the same day. The owner ruled **Q1–Q6 as recommended** (§5):
- the p236 deviation is approved;
- `ga6_normal` keeps N = 3.167, with a fixture note;
- the three 2.67 fixtures are cleared, so the energy value governs;
- this ships before F25-4;
- the unsprung-mass residual is stated;
- textbook corroboration is not blocking.

Drafted for finding **P-1** of
[`2026-11-01_critical_review_physics_atr42_docs.md`](../50_reviews/2026-11-01_critical_review_physics_atr42_docs.md)
(Critical, unconservative). Filed as **#401**.

**Scope.** One equation's output is mislabelled. The LGFACTOR energy balance
yields the **ground reaction (gear) factor** `n_j`, and the code reports it as
the **airplane inertia factor** `N`, then derives `NLG = N − L`. That
subtracts the wing lift a second time. The fix relabels the ratio:
`NLG = ratio` and `N = ratio + L`. It deviates from Appendix A p236, so it needs
an entry in [`02_approved_corrections.md`](../20_theory/02_approved_corrections.md).
**This note amends note 40's LF-3** ("`landing_load_factor()` is unchanged"). It
leaves every other LF decision in force, LF-1 in particular: `N` and `L` are the
inputs and `NLG = N − L` is derived from the governing `N`.

**Sources reviewed (verified 2026-11-01):**
`sloads/modules/landing.py` (`landing_load_factor` :104-126,
`governing_load_factors` :129-150, the entered-below-computed caution :906-913,
`run` :1097-1130, `nvp` :577-583), `sloads/report/oracle_sections.py`
:8601-8617, `oracle_app/form.py` :317-319, `tests/test_landing.py` :145-151 and
:625, `examples/*.project.json`.
Theory, all in Ref 1 (`FAR23Loads_Code.pdf`):
- **14 CFR 23.473(d), (e) and (g)** as Ref 1 prints them on p125;
- `LGFACTOR.BAS` (Ref 1 p483);
- `LANDLOAD.BAS` line 100 `NAP=NLG+LF` (Ref 1 p467);
- oracles Appendix A p236 (LGFACTOR) and p230 (LANDLOAD).

Conventions: [`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §3. Load
factors are dimensionless limit quantities, never scaled to ultimate. This note
does not change that.

---

## 1. The defect

### 1.1 The equation, as coded and as printed

```
V      = clamp(4.4·(W/S)^0.25, 7, 10)                                 23.473(d)
ratio  = [W·V²/2g + W(1−L)(S_strut + d_tire)/12]
         / [W(η_tire·d_tire + η_strut·S_strut)/12]                   LGFACTOR.BAS p483
N      = ratio            ← mislabelled                             landing.py:125
NLG    = ratio − L        ← lift subtracted twice                   landing.py:126
```

The denominator is the work done by the **gear force** over the stroke, written
as the peak gear force `n_j·W` times the efficiency-weighted stroke. The
numerator already credits the lift through `(1−L)`: the descent energy the gear
absorbs is the kinetic energy plus the net weight `W − L·W` acting through the
stroke. So the ratio is `F_gear,max / W = n_j`. That is the ground reaction
factor, and the lift appears nowhere else.

The regulation fixes which is which. **23.473(e)** (Ref 1 p125): *"The ground
reaction load factor may be equal to the inertia load factor minus the ratio of
the above assumed wing lift to the airplane weight."* That gives
`N = n_j + L`.

Two places in this module already agree with it, so the module contradicts
itself:
- `LANDLOAD.BAS` line 100, `NAP = NLG + LF` (Ref 1 p467), which the port carries
  as `K = NAP/NLG·K0`;
- `nvp = (2·VMP + VNP + L·W)/W` (`landing.py:579`), where the inertia factor is
  the gear reactions plus the lift.

The 23.473(g) floors also differ by exactly 0.67 (2.67 against 2.0).

The p236 oracle does not catch this. It locks McMaster's arithmetic and his
label together: `ratio = 3.0951` matches the printed `N`. Both are wrong in the
same way.

### 1.2 Independent confirmation (2026-11-01)

The finding has three independent checks besides the regulation text:

| Check | Method | Result |
|---|---|---|
| **Closed-form SDOF** | A rigid mass on an oleo-like gear `F = k·y + c·ẏ|ẏ|`. Constant lift `L·W`, 10 fps, explicit integration to first maximum compression, no energy equation used. The measured `η` and stroke are then put into LGFACTOR's ratio | L = 0.667: simulated `F/W = 5.000`, simulated `N = 5.667`, ratio **4.9999**. The ratio is `n_j`; the code's NLG of 4.333 is 13 % low |
| **sgear multibody, ATR main gear** (`sgear/examples/atr_mlg.sgear.json`, `DropCase`, 10 fps, energy window to first `v_z = 0`) | Trailing-link gear, Daniels oleo, tire, 2.8 % unsprung mass | see the table below |
| **sgear, Daniels A-6 rig** (L = 1.0 only: below that its tire law leaves its range, Appendix A) | Telescopic oleo, NASA CR-201601 | ratio 2.698 against `n_j` 2.867 (−5.9 %). The code's NLG is 1.698 (**−40.8 %**) |

| sgear ATR MLG | `n_j` (peak ΣF_z/W) | `N` (peak a_z/g + 1) | N − n_j | ratio vs n_j | code NLG vs n_j |
|---|---|---|---|---|---|
| L = 0 | 3.950 | 3.839 | −0.11 | 3.826 (−3.1 %) | 3.826 (−3.1 %) |
| L = 0.667 | 1.988 | 2.591 | **+0.60** | 1.888 (−5.0 %) | **1.221 (−38.6 %)** |
| L = 1.0 | 1.455 | 2.399 | **+0.94** | 1.363 (−6.3 %) | **0.363 (−75.1 %)** |

What the sgear runs show:
- The ratio tracks `n_j` within 3–6 % at every L.
- `N − n_j` comes out at 0.90–0.95 × L, as 23.473(e) says. The shortfall is the
  unsprung mass, plus the fact that peak deceleration and peak gear force are
  not simultaneous.
- The 3–6 % residual is the kinetic energy of the unsprung mass, which the
  single-mass balance omits. It is **non-conservative and inside** the base
  method's band (`theory_sources.md` §Base-method uncertainty). Q5 asks whether
  to state it.

These are evidence for the ruling, not CI gates: sgear is not a dependency. The
script is reproduced in Appendix A of this note so the check can be re-run.

**Textbook corroboration (read 2026-11-01, at closure).** Lomax (*Structural
Loads Analysis for Commercial Transport Aircraft*, AIAA 1996) does not carry
McMaster's efficiency balance; it takes the peak gear reaction from the drop
test and derives the inertia factor from it by adding the lift share: Eq. (6.20)
`nz = 1 + 2·VMG/MLW` (p83, Table 6.3 footnote), and for three wheels
`VMGr + VMGl + VNG = nz·W − L = W(nz − 1)` since `L = W` under 25.473(a)(2),
Eqs. (6.25)–(6.26), p86. That is `N = n_j + L` at `L = 1`, the 23.473(e)
relation, with the gear factor as the measured quantity. Curry (*Aircraft
Landing Gear Design*, AIAA 1988) is still not in the library (Q6).

### 1.3 Effect on the fleet (measured 2026-11-01, `build_landing`)

The ratio itself does not move. Only its label does.

| Fixture | L | entered N | ratio | energy N / NLG today | energy N / NLG fixed | governing NLG today → fixed |
|---|---|---|---|---|---|---|
| `ga6_normal` | 0.667 | 3.167 | 3.0970 | 3.0970 / 2.4300 | **3.7640** / 3.0970 | 2.500 → 2.500 (entered N governs) |
| `baron_58` | 0.667 | — | 3.3642 | 3.3642 / 2.6972 | **4.0312** / 3.3642 | **2.6972 → 3.3642 (+24.7 %)** |
| `atr42_100` | 0.667 | 2.67 | 2.3755 | 2.3755 / 1.7085 | **3.0425** / 2.3755 | 2.003 → 2.003; **2.3755 (+18.6 %) if N is cleared (Q3)** |
| `atr42_300_seed` *(untracked)* | 0.667 | 2.67 | 2.3755 | as `atr42_100` | as `atr42_100` | as `atr42_100` |
| `concept_regional_jet` | 0.667 | 2.67 | 2.3755 | as `atr42_100` | as `atr42_100` | as `atr42_100` |
| `concept_heavy` | — | — | — | no landing slice | — | — |
| `atr42_100` at **L = 1.0** (F25-4 basis) | 1.0 | — | 1.8649 | 1.8649 / **0.8649** | **2.8649** / 1.8649 | **0.8649 → 1.8649 (+116 %)** |

Delivered peak reactions on `baron_58` under the fix (no fixture edit):

| Reaction | Change |
|---|---|
| main vertical `VMP` | 7,283 → 9,083 lb (+24.7 %) |
| main drag `DMP` | 2,926 → 3,418 lb (+16.8 %) |
| nose vertical `VNP` | 5,260 → 6,460 lb (+22.8 %) |
| nose drag `DNP` | 2,096 → 2,431 lb (+16.0 %) |

The drag rises less than the vertical because `K = NAP/NLG·K0` falls from
1.247·K0 to 1.198·K0 as NLG grows. **Open at implementation:** on `atr42_100`
with N cleared, the vertical peaks move +39 % against today's energy value, but
the peak drag (`DMP`, `DNP`) does not move at all. The governing drag case
evidently reads something other than NLG. The implementing step must name it
(G-72.4) before the number is trusted.

**Rule 6:** a +16 % to +25 % change on delivered gear reactions is well above the
5–10 % band. At the Part 25 basis the code's NLG is less than half the right
value. This outranks every [V] row.

---

## 2. Decisions (D-72.1 … D-72.8)

| # | Decision | Rationale |
|---|---|---|
| **D-72.1** | **`landing_load_factor()` returns `gear_load_factor = ratio` and `airplane_load_factor = ratio + L`.** The ratio's arithmetic is unchanged. This amends note 40 LF-3 and leaves LF-1, LF-2 and LF-4 to LF-12 in force. | §1.1 and §1.2. The defect is a label, so the fix is a relabelling. |
| **D-72.2** | **An approved oracle deviation for p236**, recorded in `02_approved_corrections.md` in the #133/#134 form. The printed `N 3.0951` stays in the test as the *printed* column and is asserted against the corrected **`NLG`**. The printed `NLG 2.4281` is kept as a comment. The corrected `N` is `3.0951 + 0.667 = 3.7621`. Cited to 23.473(e) (Ref 1 p125), with LANDLOAD line 100 (p467) as McMaster's own consistent statement. | Policy in `02_approved_corrections.md`: the owner approves in the PR, plus the full trail. The printed number still pins the arithmetic at ±0.1 %; only the field it pins moves. |
| **D-72.3** | **p230 does not move.** `ga6_normal` keeps `N = 3.167` (LF-9), the governing path is unchanged (`NLG = N − L = 2.5`), and the page reproduces exactly. | p230 is reproducible at NLG 2.5 and no other value (note 40 §1.3). The entered N governs, so D-72.1 cannot reach it. |
| **D-72.4** | **The entered-below-computed caution (LF-7) now fires on `ga6_normal`**: 3.167 entered against an energy N of 3.764. It also fires on the three 2.67 fixtures unless Q3 clears them. The caution's wording is unchanged. | This is the honest state. McMaster's own design N sits below his own estimate once the estimate is labelled correctly. LGFACTOR is a design-stage estimate (Ref 1 p125: "should be revised … so as to be not less than that determined by tests"), so a caution and not a block is right. Q2 asks whether ga6 should carry a fixture note saying so. |
| **D-72.5** | **No schema change.** No field is added, removed or reinterpreted: `airplane_load_factor` is still the governing N when entered. A stored project's N means what it always meant; only the *computed* value beside it changes. | Unlike LF-8, nothing in a saved file changes meaning. |
| **D-72.6** | **The oracle report's LGFACTOR block** (`oracle_sections.py:8601-8617`) gains the printed/corrected pair on both rows, as the #133 rows do, and states the deviation in band. `methods.APPROVED_CORRECTIONS` declares it when the step ships. | Every artifact states what it deviates from (G-OR-73/74 spirit). The report is where a reader compares against p236. |
| **D-72.7** | **The docstrings and labels that state the defect as intent are rewritten.** That covers `LoadFactorResult` (`NLG = N - L` on the energy pair), `landing_load_factor`'s docstring, `run()`'s "energy N/NLG rows" note at :1104, `PROGRAM_SPEC.md` §LGFACTOR and the `theory_sources.md` landing row. The *governing* `NLG = N − L` statements stay: they are correct. | A comment that says the wrong thing is how the next session re-derives the defect. |
| **D-72.8** | **The rule-4 sweep is part of the step (§4)**, with a guard: an energy-balance closure test that every future energy or work balance must pass (G-72.1). | One closure test that runs the physics independently is what was missing. The oracle could not see it. |

---

## 3. Closure gates (G-72.1 … G-72.6)

Benchmark-first (rule 2). Identities are exact (`rel_tol=1e-9`). The oracle is
±0.1 %. The closure simulation is held to 1e-3, set by its time step.

| Gate | Statement | Expected numbers |
|---|---|---|
| **G-72.1** (energy-balance closure, independent of the equation) | A zero-dependency single-mass drop: `F = k·y + c·ẏ|ẏ|`, constant lift `L·W`, integrated to first maximum compression. The `η` and stroke measured from the simulation are put into `landing_load_factor`'s ratio. Assert `gear_load_factor == F_max/W` and `airplane_load_factor == (F_max + L·W)/W`, both at 1e-3, for L ∈ {0, 0.667, 1.0}. Pre-fix, this fails by exactly L. | L = 0.667, k = 12 W/ft, c = 0.05: `F/W` 5.000, N 5.667 |
| **G-72.2** (p236, printed column kept) | `sink_rate_fps` 9.0048; `gear_load_factor` 3.0951 against **printed N**; `airplane_load_factor` 3.7621 (= printed N + L). The manual's labelling is recorded in the test comment with the register link. | ±0.1 % |
| **G-72.3** (identity) | `airplane_load_factor − gear_load_factor == L` exactly, for every fixture and for L ∈ {0, 0.667, 1.0}. G-LF-3 (`NVP == N` on cases 4–9) passes unmodified. | 1e-9 |
| **G-72.4** (fleet) | §1.3's governing N and NLG per fixture, and `baron_58`'s four peak reactions as printed. The `atr42_100` drag-peak invariance is explained by name in the test docstring, or it is a defect and is filed. | baron VMP 9,083 / DMP 3,418 / VNP 6,460 / DNP 2,431 lb |
| **G-72.5** (p230 invariance) | Every Appendix A p230 to p233 cell passes unmodified on `ga6_normal`. | unchanged |
| **G-72.6** (the caution) | The LF-7 caution fires on `ga6_normal` (3.167 < 3.764) and on whichever 2.67 fixtures Q3 leaves entered. It does not fire on `baron_58`. | — |

**Closure tier: L.** This means:
- this note at AGREED;
- the register entry (D-72.2), dropping its `ships with` marker in the implementing PR;
- `PROGRAM_SPEC.md` §LGFACTOR and the `theory_sources.md` landing row;
- the oracle report rows (D-72.6) and the methods statement;
- a **full-format** history fragment and a `changes/` fragment;
- the fixture edits Q3 decides;
- `docs/60_guide/14_landing_loads.md`, if it quotes an energy N.

---

## 4. The sweep (rule 4: generalize on first find)

The defect class is *a printed figure that is the only check on an energy or
work balance, or a lift credit applied in two places*. These are the places
searched on 2026-11-01:

| Site | Verdict |
|---|---|
| `landing.landing_load_factor` | **This note.** |
| `landing.governing_load_factors`, `balance/ground.py` (`NLG = N − L`; `assemble_ground` applies `L × W`) | **Correct.** These take the *governing* N, so the lift is applied once. No change. |
| `landing.py:577-583` `nvp` | **Correct.** It is the 23.473(e) relation, and is why the module contradicts itself. |
| Other `energy`/`stroke`/`efficiency` hits in `sloads/` (`convergence`, `aero_curves`, `fuselage_moment`, `lateral_body_aero`, …) | **None is an energy balance.** The hits are unrelated uses of the words. To be re-confirmed by reading each one at implementation. |
| `theory_sources.md` landing row (line 158) | **Citation slip, same area.** It quotes the *"wing lift not exceeding two-thirds"* text as **23.473(g)**, but Ref 1 p125 prints it as **(e)**; (g) is the floors. Fixed in the same change. |

The structural half is G-72.1. The closure test sits beside the oracle, so the
oracle is no longer the only check on the balance.

---

## 5. Questions for the owner — ruled 2026-11-01, all as recommended

| # | Question | Recommendation (**ruled as written**) |
|---|---|---|
| **Q1** | Approve the p236 deviation (D-72.2)? | **Yes.** Three independent checks agree with 23.473(e), and McMaster's own LANDLOAD agrees too. |
| **Q2** | `ga6_normal` keeps N = 3.167 and the caution now fires (D-72.4). Add a fixture note saying the oracle airplane's design N is below its own corrected estimate? | **Yes, a note in the fixture's `.sources.md`.** Do not change the N: that would break p230 for no delivered benefit. |
| **Q3** | The three 2.67 fixtures (`atr42_100`, `atr42_300_seed`, `concept_regional_jet`). The 2.67 was the 23.473(g) floor, entered because the mislabelled energy N of 2.3755 sat below it. With the fix, the energy N is 3.0425. Clear N so the energy value governs (NLG +18.6 %), or keep 2.67 under the caution? | **Clear it** (review P-1 action 4). The floor was chosen against an under-computed number. Keeping it delivers gear reactions 16 % below the airplane's own estimate. |
| **Q4** | Does this ship before the F25-4 landing variant (L = 1.0, 6 fps at MTOW)? | **Yes, it is a prerequisite.** At L = 1.0 the code's NLG is less than half the right value (§1.3), so F25-4 built on it would be wrong from the start. |
| **Q5** | State the unsprung-mass residual (§1.2: −3 % to −6 %, non-conservative) in `PROGRAM_SPEC.md` §LGFACTOR? | **Yes, one sentence, no correction.** It is inside the base-method band and LGFACTOR is an estimate to be superseded by test (23.473(f)). |
| **Q6** | Textbook corroboration (Lomax, Curry). | **Not blocking.** 23.473(e) is a primary source already in Ref 1. If the books are added to the library, the page is added to the register entry. |

---

## Appendix A — the sgear cross-check script (2026-11-01)

Run from the sgear repository as
`.venv/bin/python -I sgear_lgfactor.py examples/atr_mlg.sgear.json`. The
script integrates to first maximum compression. On the ATR gear that gives the
same travel as sgear's own `metrics.landing_metrics`, which integrates to the
airframe's lowest height.

The Daniels rig is reported at L = 1.0 only. At L < 1 its cubic `fz_poly` tire
law is driven past its fitted range: the law peaks at 110.9 kN at 123 mm and
reaches zero at 197 mm. The rig then falls through the ground (4.4 m of tire
deflection at L = 0), and sgear reports a load factor anyway. sgear's table-form
tire law raises past its last row and the polynomial form does not. That is
filed to sgear; it does not affect the ATR runs.

```python
import sys
import numpy as np
from sgear.io import load as load_model
from sgear.cases import DropCase

path = sys.argv[1]
for L in (0.0, 0.667, 1.0):
    model = load_model(path)
    af = model.airframe()
    g = model.gravity_m_s2
    W = af.mass_kg * g
    V = 3.048                                     # 10 fps
    r = DropCase(sink_rate_m_s=V, lift_fraction=L, t_end_s=0.8,
                 dt_s=2e-4, out_dt_s=2e-4).run(model)
    tires = [e for e in model.elements if e.type == "tire"]
    Fz = np.sum([r[f"{t.id}.Fz"] for t in tires], axis=0)
    z, vz, az = r[f"{af.id}.z"], r[f"{af.id}.vz"], r[f"{af.id}.az"]
    j = 5 + int(np.argmax(vz[5:] >= 0.0))         # first max compression
    d = float(z[0] - z[j])
    Fmax = float(np.max(Fz[: j + 1]))
    work = float(np.sum(0.5 * (Fz[1:j+1] + Fz[:j]) * -np.diff(z[: j + 1])))
    eta = work / (Fmax * d)
    n_gear, n_inertia = Fmax / W, float(np.max(az[: j + 1])) / g + 1.0
    ratio = (V**2 / (2 * g) + (1 - L) * d) / (eta * d)
    print(L, n_gear, n_inertia, ratio, ratio - L)
```
