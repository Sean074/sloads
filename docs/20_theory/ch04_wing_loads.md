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
| `NMAA` | largest resultant among the negative maneuver/gust points | 23.333(b)/(c) |
| `ACRL` | largest `LZW` among the accelerated-roll points | 23.349(a) |
| `TORS` | steady-roll condition with the most negative aileron-induced torsion proxy, aileron deflection per CAM 3.222 | 23.349(b) |

The selected set becomes the wing's case list — the conditions AIRLOADS
re-evaluates for distributed airloads and WINGINER/NETLOADS combine with
inertia. Every wing case id traces to one of these criteria; contrast the
empennage and ground families, which run **all** their conditions and envelope
after analysis (chapters 5 and 8 state the same contrast from their side).

## Method (outline)

1. **Airload distribution** — Schrenk's approximation (Ch 7): the spanwise
   loading is the mean of the planform chord distribution and the elliptic
   distribution, split into additional and basic (twist) lift; the swept /
   high-Mach branch (AIRLOAD4, Ch 12) is auto-selected above 15° quarter-chord
   sweep or design Mach 0.4.
2. **Spanwise inertia** — WINGINER's strip masses (panel weight plus
   concentrated items, per side) under the case's load factor, plus the
   unit-roll recurrence for the accelerated-roll case.
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
  in-band wherever the case is rendered; on the backlog. The roll-case design
  of record (semispan side, `UNB` from the condition's own root bending) is
  `docs/30_future/52_wing_roll_cases_note.md`.
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
- FAR 23.333, 23.349; CAM 3.222 (aileron deflection schedule).
- `docs/30_future/52_wing_roll_cases_note.md` — the roll-case design of
  record.
