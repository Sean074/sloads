# Chapter 4 — Wing Loads: Selection, Distribution, and the Roll Cases

*(Chapter stub — template, cases, assumptions and validation populated; the
full method walk-through with worked examples follows in a later step. The
per-module equation citations remain authoritative in
[`00_theory_sources.md`](00_theory_sources.md) §Per-module equation citations.)*

## Scope & regulatory basis

The wing's critical flight conditions and their spanwise/chordwise distributed
loads: critical-condition selection (SELECT, Reference 1 Ch 9), distributed
airloads (AIRLOADS Ch 7, the AIRLOAD4 swept/high-Mach branch Ch 12), spanwise
inertia (WINGINER Ch 13), and the net shear/bending/torsion tables (NETLOADS
Ch 14) at the load reference axis. Regulations: FAR 23.333 (flight envelope),
23.337/23.341 (the factors behind the envelope, chapter 3), 23.349 (rolling
conditions).

## Cases analyzed — the SELECT down-select

The wing (and fuselage, chapter 6) is the family that **prunes before
analysis**: SELECT reads the balanced V-n matrix (chapter 3 §13) and searches
it for the governing condition per criterion (SELECT.BAS subroutine 3000):

| Case | Criterion over the matrix | FAR basis |
|---|---|---|
| `PHAA` | largest resultant `√(LZW² + DX²)` among the positive stall-line / VA maneuver points | 23.333(b) |
| `PLAA` | largest resultant among the VD maneuver / VD gust points | 23.333(b) |
| `PMAA` | largest `LZW` among the VC maneuver / +VC gust points | 23.333(b)/(c) |
| `NMAA` | largest resultant among the negative VC maneuver / −VC gust points (narrowed from the `.BAS`'s five negative labels, design note 62 D-62.1) | 23.333(b)/(c) |
| `ACRL` | largest `LZW` among the accelerated-roll points | 23.349(a) |
| `TORS` | steady-roll condition with the most negative aileron-induced torsion proxy, aileron deflection per CAM 3.222 | 23.349(b) |
| `NHAA` | largest resultant among the negative stall-line points (STALL −N, STALL −1G) — above the `.BAS`, design note 62 | 23.333(b)/(c), 23.337(b) |
| `NLAA` | largest resultant among the negative VD maneuver / −VD gust points — above the `.BAS`, design note 62 | 23.333(b)/(c) |
| `PNZ` | the largest load factor over every positive-family point, tie-break largest resultant — the point that sizes the wing-mounted masses, whatever weight it occurs at (design note 62 D-62.8) | 23.337(a), 23.341 |
| `NNZ` | the most negative load factor over every negative-family point, tie-break largest resultant (design note 62 D-62.8) | 23.337(b), 23.341 |

A negative slot (`NHAA`/`NMAA`/`NLAA`/`NNZ`) admits a point only when the
**wing's** lift is negative (`LZW < 0`), and `PNZ` only when it is positive:
the slot is a wing selector, and a point with `nz < 0` but `LZW > 0` (the
tail-heavy corner of a negative gust) loads the wing upward and belongs to no
down-load slot (D-62.2). A slot with no eligible point is **empty**, and a
`PNZ`/`NNZ` point another slot already delivers is not delivered twice
(D-62.8) — one physical condition, one id. The four slots above the `.BAS`
are the concept-mode superset rule: the six Appendix A picks are the same
points on the same figures.

**Each slot is then assessed at every flight mass state** (design note 63
D-63.7, #292). The criterion above, applied within the points balanced at
one weight/CG case, names that family's point at that case; run at the
case's own loading (chapter 13's inertia relief is the case's wing fuel and
wing-mounted masses, not a fixed list) it gives one net root bending per
slot per case, and the slot is **delivered at the variant whose signed root
`Mxx` is the extreme** — largest for the positive-lift slots, most negative
for the negative ones. On a wing-fuel airplane the zero-fuel loading at the
aft limit removes the relief and takes the up-bending slots from the MTOW
point (`baron_58`: seven of nine slots move to `mzfw aft`); on the Appendix A
airplane, whose fuel is in the fuselage, every slot's governing run is its
air pick, which is the oracle lock. The air pick over the whole matrix stays
queryable as `select.air_picks`; the report's §3.2 prints the full variant
table with the governing row marked. Two slots keep their air pick by
definition: `TORS`, whose criterion is torsion, and `PNZ`/`NNZ`, whose
criterion is the load factor — re-pointing them by bending would deliver a
condition their id does not name. A variant within the V-n balance's own
noise of the air pick (0.5 %) is a tie the air pick keeps. The FLIGHT cases a
max zero-fuel weight seeds (D-63.5: `mzfw aft`, `mzfw fwd`, `full fuel aft`,
each with its loading) are what puts the zero-fuel state in the matrix.

The selected set becomes the wing's case list — the conditions AIRLOADS
re-evaluates for distributed airloads and WINGINER/NETLOADS combine with
inertia. Every wing case id traces to one of these criteria; contrast the
empennage and ground families, which run **all** their conditions and envelope
after analysis (chapters 5 and 8 state the same contrast from their side).

## The rolling conditions — origin and derivation (FAR 23.349)

The two rolling slots, `ACRL` and `TORS`, are the wing's only unsymmetrical
flight conditions, and both are **constructed from a symmetric manoeuvre**
rather than analysed as a roll. The regulation says so itself. 14 CFR 23.349,
*Rolling conditions* (as amended through Amdt 23-48, 61 FR 5144, 1996):

> (a) *Unsymmetrical wing loads appropriate to the category. Unless the
> following values result in unrealistic loads, the rolling accelerations may
> be obtained by modifying the symmetrical flight conditions in §23.333(d) as
> follows:* (1) *For the acrobatic category, in conditions A and F, assume
> that 100 percent of the semispan wing airload acts on one side of the plane
> of symmetry and 60 percent of this load acts on the other side.* (2) *For
> normal, utility, and commuter categories, in Condition A, assume that 100
> percent of the semispan wing airload acts on one side of the airplane and
> 75 percent of this load acts on the other side.*
>
> (b) *The loads resulting from the aileron deflections and speeds specified
> in §23.455, in combination with an airplane load factor of at least two
> thirds of the positive maneuvering load factor used for design. Unless the
> following values result in unrealistic loads, the effect of aileron
> displacement on wing torsion may be accounted for by adding the following
> increment to the basic airfoil moment coefficient over the aileron portion
> of the span in the critical condition determined in §23.333(d):*
> Δcₘ = −0.01 δ, *δ the down aileron deflection in degrees.*

**Paragraph (a) — the accelerated roll (`ACRL`).** Condition A is the corner
of the 23.333(d) envelope where the positive stall line meets the limit
manoeuvre load factor n₁ — FLTLOADS's `STALL +N` point, *not* the point at
V_A (Reference 1 Ch 13 p. 96, footnote). The rule keeps 100 % of that
condition's semispan air load on one side and a fraction p on the other:
**75 %** for normal, utility and commuter; **60 %** for acrobatic, on
conditions A and F both. The airplane as a whole then carries the average of
the two sides, a load factor of `(100 + p)/200 · n₁`, and that is the V-n
point FLTLOADS balances as `AC ROLL` at the condition A speed for every
configuration, CG and altitude (`flight_envelope._config_points`; 0.875·n₁ =
3.325 on the Appendix A airplane at p = 75). SELECT picks the `AC ROLL` point
with the largest wing lift (SELECT.BAS line 3330; Ch 9 p. 68 says "largest
resultant airload"). The rolling moment the airplane is *not* meant to balance
is the difference between the two sides' root bending,

> **UNB = (1 − p/100) · M_root(condition A)**,

and the manual (Ch 12 pp. 91–92, Ch 13 pp. 95–96) computes it by hand from the
AIRLOADS run of condition A and types it into WINGINER, which reacts it by roll
acceleration alone — nothing else in a free-free airplane can — through the
unit-roll inertia set `Fz_r = W·y·10⁵/I_wxx`, `I_wxx = 2·ΣW·y²` (panel strips
and concentrated masses alike), scaled by `UNB/10⁵`, with `θ̈ = UNB·g/I_wxx`
(WINGINER.BAS 1350–1620, 1760–1810; the §"roll closure" below verifies the
reaction strip for strip). The governing side's **air load is condition A's**
distribution at the same weight, altitude and CG — AIRLOADS at condition A's
CL and speed (Appendix A case 142 for case 160, p. 208) — while the inertia is
the `AC ROLL` point's own n_z and n_x; net = air − inertia, and the manual
prints the 100 % side only (p. 225 "100 PERCENT SIDE"); the other side is the
same rows scaled by p. No aileron enters paragraph (a): the up- and down-going
aileron's differential lift has no spanwise carrier in this method (§Assumptions
below), and the couple is the construction's, not the aileron's.

Worked numbers, Appendix A airplane (W 3400 lb, n₁ 3.8, CG2, 12,000 ft):

| | Manual (71.03 %, pre-1996 rule) | 23.349(a)(2) as amended (75 %) |
|---|---|---|
| condition A root bending, lb-in (p. 212) | 514,475 | 514,475 |
| UNB, lb-in | 149,043 (p. 96) | 128,619 |
| airplane load factor at `AC ROLL` | 3.25 | 3.325 |
| θ̈, deg/s² (p. 219) | −13.287 | ≈ −11.47 |
| WINGINER root M_xx, lb-in (p. 219) | −124,095 | ≈ −115,500 |
| net root M_x, 100 % side, lb-in (p. 225) | +390,380 | ≈ +399,000 |

The manual's linear 70→75 % rule (Ch 12 p. 91: 70 % at 1000 lb rising to
75 % at 12,500 lb) is the pre-Amdt 23-48 wording; the amended flat 75 % is the
rule of record here — [`02_approved_corrections.md`](02_approved_corrections.md)
§23.349(a)(2). The full-span assembled deck (chapter 9) carries the same
condition in its own representation: the averaged lift balanced at the
`AC ROLL` load factor, the couple `−UNB` at the wing aerodynamic centre, and
the closure-roll relief `k·w·y` that the identity below proves is WINGINER's
own unit-roll set — statically equivalent in total force and rolling moment to
the two-sided construction, while the semispan station tables are the
governing side.

**Paragraph (b) — the steady roll (`TORS`).** The aileron deflection schedule
of 23.455, full δ at V_A, `(V_A/V_C)·δ` at V_C and `0.5·(V_A/V_D)·δ` at V_D
(CAM 3.222(b)(3) for the halving), at two thirds of n₁ — FLTLOADS's
`ST ROL A/C/D` points. The steady roll has no unbalanced moment: the aileron
couple is balanced by roll damping, so the case is symmetric in bending and
TORS exists for **torsion**. SELECT ranks the three points on the torsion proxy
`(cₘ − 0.01·δ)·q` (Ch 12 p. 93), which is paragraph (b)'s increment; the
delivered distribution applies the increment over the aileron span through the
per-station section-cₘ mechanism when the aileron butt lines are entered and
reduces to the printed run when they are blank — the manual's own worked
example entered a uniform cₘ (p. 216) and skipped its Ch 12 instruction, which
is why Appendix A passes without the increment (design note 52 §2, D-52.5).

**What the code carries today, until design note 52 ships** (backlog B8): the
unbalanced moment is an entered field (`wing_mass.cases[].unbal_moment`), a
derived `ACRL` case carries zero, the delivered `ACRL` variant is built at the
`AC ROLL` point's own averaged lift rather than condition A's, the percentage
in FLTLOADS is the manual's linear rule with no category branch, and the TORS
increment is applied in selection but not in the delivered distribution.
Design note 52 (amended 2026-09-22) is the design of record for closing all
five; the WINGINER inertia math and the SELECT pick are oracle-locked as they
stand.

## Method (outline)

1. **Airload distribution** — Schrenk's approximation (Ch 7): the spanwise
   loading is the mean of the planform chord distribution and the elliptic
   distribution, split into additional and basic (twist) lift; the swept /
   high-Mach branch (AIRLOAD4, Ch 12) is auto-selected above 15° quarter-chord
   sweep or design Mach 0.4.
2. **Spanwise inertia** — WINGINER's strip masses (the panel derived from the
   `WING`-tagged `PANEL` items plus the `POINT` rows of the case's own loading,
   per side — one mass model, design note 63) under the case's load factor,
   plus the unit-roll recurrence for the accelerated-roll case.
3. **Net loads** — NETLOADS integrates air minus inertia to the running shear,
   bending and LRA torsion tables per station (the station-table conventions
   of chapter 2 §2.3).

## Assumptions & limitations

- **Schrenk is the spanwise basis** — no lifting-line, no aeroelastic
  redistribution. Good to order 5–10 % on a distributed load; integrated
  totals close far tighter ([`00_theory_sources.md`](00_theory_sources.md)
  §Base-method uncertainty, the effect-vs-error-bar datum).
- **Gust cases reuse the manoeuvre spanwise shape** (decision D-31) — a
  recorded decision, inside the Schrenk band by construction; it re-opens only
  if the wing airload basis itself moves off Schrenk.
- **The aileron's own lift increment has no spanwise carrier** on the
  accelerated-roll case: the couple is lumped at the wing aerodynamic centre,
  which reduces exactly to the oracle-locked WINGINER model (inertia reaction
  only) but omits the differential lift from `ACRL` wing bending. Stated
  in-band wherever the case is rendered; on the backlog. This is faithful to
  23.349(a), which prescribes the percentage construction and no aileron term
  (§"The rolling conditions" above). The roll-case design of record (semispan
  side, `UNB` from condition A's root bending, condition A's lift on the
  delivered side, the amended 75 %) is
  `docs/25_notes/52_wing_roll_cases_note.md`.
- **The Mach threshold for the swept branch is Reference 1's 0.4** (the User's
  Guide says 0.5); kept conservative because no `.BAS` oracle exists for the
  selection itself (M1-8, `PROGRAM_SPEC.md` airloads row).

## How it is validated

**Oracle-locked at the totals and the stations.** SELECT's critical wing
conditions and the NETLOADS station tables are asserted against Appendix A's
printed "Critical Wing Loads" and net-loads pages within ±0.1 % — the
per-module rows in [`00_theory_sources.md`](00_theory_sources.md) carry the
page citations. The AIRLOAD4 swept branch, with no printed swept oracle, is
gated by its reduction invariant (Λ = 0 lands on the locked unswept oracle)
plus the swept-CL renormalization closure.

### The rolling case's roll closure (moved from the hub; step B7, 2026-08-08)

The balanced-case residual gate (chapter 9) is a *smallness* gate: the
residual before closure must be under 1 %. An **antisymmetric** case cannot be
gated that way, because what it is out of balance in is not an error. On an
accelerated-roll condition (FAR 23.349) the applied aileron couple is 6.71 %
of `n·W·b/2` on `ga6_normal` and 2.00 % on `concept_regional_jet`, and the
airplane is *supposed* not to balance it — it rolls. The couple is reacted by
roll acceleration, exactly as drag is reacted by `nx`: nothing else in a
free-free model can.

So the gate here is an **identity against an independent producer** instead.
Closing the roll residual with mass-proportional relief `k·w_i·y_i`
(physically `−m_i·ṗ·y_i`) must reproduce **WINGINER's own unit-roll inertia
distribution** — `fz_r[i] = w_i·y_i·10⁵/Iwxx`, WINGINER.BAS's
accelerated-roll case, which is oracle-locked FAR 23 code that this step did
not touch and that knows nothing about the balance layer:

| | ga6_normal ACRL | concept_regional_jet ACRL |
|---|---|---|
| UNB (in-lb) | −149,043 | −600,000 |
| per-strip closure ÷ `ur·fz_r` | **1.000000** | **1.000000** |
| net force added by the roll term | 6.4e-14 lb | 2.3e-13 lb |
| `residual_mx` vs `−UNB` | exact | exact |
| all six DOF after relief | machine precision | machine precision |

The wing-item/WINGINER-panel scale (0.9903 and 1.0100) **cancels
identically**, because the closure normalises on the same masses the assembled
model carries — which is why the agreement is exact rather than approximate,
and why it is a gate rather than a coincidence. Both twins then solve in the
real sbeam with determinate-support reactions ≈ 0.

Sign, recovered rather than assumed: WINGINER's unit-roll set produces a
rolling moment of exactly `+UNB` (its normalisation makes `Σ y·fz_r =
100,000` for a unit case, verified), and NETLOADS enters inertia opposing the
air load — so the *aero* couple is `−UNB`. The strip-for-strip identity is
what confirms that sign is right rather than merely self-consistent.

## Sources

- Reference 1 Ch 7 (AIRLOADS), Ch 9 (SELECT), Ch 12 (AIRLOAD4), Ch 13
  (WINGINER), Ch 14 (NETLOADS); Appendix A oracle pages per the hub's
  per-module rows.
- FAR 23.333, 23.349 (as amended by Amdt 23-48, 61 FR 5144, 1996-02-09 —
  the 75 % other side), 23.455; CAM 3.222 (aileron deflection schedule).
- `docs/25_notes/52_wing_roll_cases_note.md` — the roll-case design of
  record.
