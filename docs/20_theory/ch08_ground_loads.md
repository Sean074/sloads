# Chapter 8 — Ground and Landing Loads

*(Chapter stub — template, cases, assumptions and validation populated; the
full method walk-through follows in a later step. The balanced ground cases —
the `n_z = 0` free-free solve, the LANDLOAD identity gate and the worked
three-case example — are already written in
[`ch09_balanced_airplane.md`](ch09_balanced_airplane.md) §9, which this
chapter deliberately does not duplicate.)*

## Scope & regulatory basis

The landing-gear reactions and the ground condition family: FAR 23.471–23.511
(limit ground loads: level landing, tail-down, one-wheel, side load, braked
roll, supplementary nose/tail conditions, with every embedded multiplier a
limit quantity — the governing safety-factor table's ground row). Module:
LANDLOAD (Reference 1 Ch 20), plus the gear free-body consumers documented in
`PROGRAM_SPEC.md`.

## Cases analyzed — the family's own conditions, enveloped after

Ground cases derive entirely from their own FAR sections; nothing passes
through SELECT and no V-n point exists for them. Like the empennage, the
family runs **all** its conditions and criticality falls out of the two-sided
envelope downstream. Two standing rules shape how the results may be read:

- **Ground and flight are separate governing families** — never compared for
  a maximum, never merged into one envelope, because their fuselage station
  extremes belong to different total load states (companion pressure cases
  sloads does not model). Decided permanently (G-9/D-28, `CONVENTIONS.md`
  §1).
- **A ground case is a balanced free-free case with no base load factor**
  (G-1/G-6): its inertia enters at `n_z = 0` and the whole rigid-body field
  is solved, which is what 23.471's "rational or conservative manner" asks
  for. The solve, and why the 1 % residual gate does not apply, is chapter 9
  §9.

## Method (outline)

LANDLOAD computes the wheel reactions per attitude from the descent-velocity
energy method and the prescribed load factors, at the **two design weights**:
the reduced design landing weight for the level / tail-down / one-wheel
cases, MTOW (via `WR = MTOW/MLW`) for the side / braked-roll / nose
supplementary ones (14 CFR 23.473(b)/(c)). Reactions are stated per wheel in
airplane axes (V +up, D +aft, S +starboard — SC-5), applied at the point
Appendix A's own columns name — the **axle** on the landing attitudes, the
**ground contact point** on the handling ones — and transferred to the gear
reference point as a change of description, not of load (G-2/G-12/AP-1,
`CONVENTIONS.md` §1).

## Assumptions & limitations

- **Wing lift through impact is a certification-basis choice, not physics:**
  FAR 23 assumes lift ≤ 2/3·W, FAR 25 permits lift = W. `L` is a free input
  with both bases captioned; the hard bound is the 23.473(g) floors, refused
  in a FAR 23 category and warned in concept (note 37 LF-4).
- **The reduced landing weight is fuel burned off, not payload left behind**
  (G-5): a `GROUND` loading burns its consumable rows continuously before any
  discretionary item is dropped — on a wing-fuel airplane the difference is
  not cosmetic, because burning fuel removes wing inertia relief.
- **MTOW is a single scalar, constant across the CG range** (G-14) — stated
  because on some airplanes it varies with CG.
- **The gear reaction's carrier (`BODY`/`WING`) is an explicit input**: a
  wing-carried reaction relieves inboard wing bending and reaches the
  fuselage only through the carry-through; guessing it is wrong in both
  directions at once, and the mass model must agree with it
  (`CONVENTIONS.md` §1).
- **Two approved sign corrections stand against the printed source** (the
  register [`02_approved_corrections.md`](02_approved_corrections.md) is the
  record): LANDLOAD's `BETA` carries the wrong sign on attitudes 2 and 3
  (#133), and its airplane-datum lift term and moment transform carry the
  same wrong sign (#134). Both are deviations *from the manual*, approved
  with the full trail; the ported equations follow the corrected physics and
  the tests carry both the printed and corrected figures.

## How it is validated

**Oracle-locked by transcription.** LANDLOAD's Appendix A pages (p231–233)
are transcriptions of rendered pages — recorded as such under provenance rule
P-1, because those pages were mis-classified as unusable from a garbled text
layer for a year while a sign error lived in the unchecked gap (the incident
behind P-1 itself; hub §Oracle provenance).

**Plus an independent witness.** The `gear_loads` free-body path reaches the
same load factors through lever arms with no mass matrix anywhere in it — a
second producer sharing no derivation (hub provenance table). Downstream, the
balanced ground cases are gated by LANDLOAD's own closed-form
`NVP`/`NDP`/`NS`, consumed **only** in the gate: rotate the solved field back
to the ground line through the case's own `ρ` and it reproduces all three
exactly (chapter 9 §9).

## Sources

- Reference 1 Ch 20; Appendix A p231–233 (transcribed oracle pages).
- 14 CFR 23.471–23.511, 23.473(b)/(c)/(g), 23.485(d).
- [`02_approved_corrections.md`](02_approved_corrections.md) — the two sign
  corrections; `docs/40_history/42_ground_frame_note.md` and
  `docs/40_history/43_application_point_note.md` — the frame and
  application-point decisions.
