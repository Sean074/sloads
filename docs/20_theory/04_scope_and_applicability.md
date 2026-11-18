# Scope and Applicability — What sloads Covers, and Where It Stops

This page is the one place that says which airplanes sloads is built for, what
it does not model, and **which way each omission errs**. Each limit names the
code or document that owns it; the values live there, not here, except where a
guard test pins this page to its owner (`tests/test_book.py`).

What sloads computes is listed in [`CAPABILITIES.md`](../../CAPABILITIES.md).
Why its numbers can be trusted is the
[validation rationale](03_validation_rationale.md).

## 1. What it covers

- **The structural design loads of 14 CFR Part 23 Subpart C**, by the method of
  McMaster's FAR 23 LOADS suite: flight, control-surface, engine and ground
  conditions, delivered as **limit** loads with the safety factor stated per
  case ([`CONVENTIONS.md`](../10_standard/CONVENTIONS.md)).
- **Categories** Normal, Utility and Acrobatic, plus sloads' own **concept**
  category, which takes the chosen load factors verbatim and extends the method
  to larger airplanes (owner: `CATEGORIES` in `sloads/models/inputs.py`).
- **Gear:** tricycle only (`sloads/modules/landing.py`,
  FAA User's Guide Table 2.1).
- **Engines:** a single nose engine, two wing engines, or four wing engines —
  layouts `1N`, `2W` and `4W` (`EngineLayout` in `sloads/models/enums.py`).
  Reciprocating and turbopropeller installations.
- **Tails:** conventional, T-tail and V-tail (`TailType`, same file).

Every run's report carries a **coverage table** that classifies each Subpart C
regulation as covered, not applicable to this airplane, not analysed in this run,
or out of scope for the tool (`sloads/report/coverage.py`). That table, not this
page, is the authority for a particular airplane.

## 2. Range

- **Weight and seats.** The FAR 23 core is calibrated to the pre-Amendment 23-64
  applicability band of 14 CFR 23.1: **12,500 lb** and **9 passenger seats**
  (`FAR23_MAX_WEIGHT_LB` and `FAR23_MAX_PASSENGER_SEATS` in `sloads/constants.py`).
  Above it nothing is blocked: the GUI shows a banner and offers concept mode
  (`sloads/applicability.py`). Concept mode has no printed oracle; it is
  checked by physics closure instead
  ([§Concept-mode closure validation](00_theory_sources.md#concept-mode-closure-validation-step-p1-2)).
- **Speed and Mach.** Airspeeds are equivalent (KEAS). Compressibility enters
  the airplane lift and moment curves by the subsonic Glauert factor
  (`sloads/aero_curves.py`); nothing models transonic flow. The T-tail induced
  rolling moment (AC 23-9) has no compressibility term, and every subcase above
  **Mach 0.6** is warned (`AC23_9_MACH_WARN` in `sloads/constants.py`, an
  engineering threshold, design note 51 D-51.8).
- **Part 25 airplanes** run in concept mode with the Part 25 rows that have been
  built; the rest are listed in §3.

## 3. What is not modelled, and which way it errs

"Not delivered" means the loads are simply absent: the gap is total, not a bias,
and the loads must come from another source. A row that errs **unconservative**
delivers a load that is too low.

| Limit | Which way it errs | Owner |
|---|---|---|
| **Rigid airplane, Schrenk spanwise airloads**, lumped balancing tail load: no aeroelastic redistribution, no lifting-line | Either way; order 5–10 % on a distributed load, better on integrated totals | [§Base-method uncertainty](00_theory_sources.md#base-method-uncertainty) |
| **Tailwheel gear** (23.497) and multiple-wheel units (23.511) | Not delivered | `sloads/modules/landing.py`; coverage table |
| **Engine failure on a turbofan or turbojet** (23.367): thrust and windmilling drag are propeller models | Unconservative; the module refuses when the failed engine has no propeller | `PROPELLER_ONLY_NOTE`, `sloads/modules/one_engine_out.py` |
| **Engine layouts other than 1N/2W/4W** (aft-fuselage, centreline push-pull) | Not delivered; refused | `EngineLayout`, `sloads/models/enums.py` |
| **Pressurisation**: no cabin differential-pressure case, none combined with flight or ground cases | Not delivered; a permanent exclusion | `pressurization` limitation, `sloads/report/methods.py` |
| **Flight and ground cases enveloped together** | Not delivered; the consumer takes the worse family per station | `ground-flight-separate-families`, same file |
| **Gust**: the Part 23 gust load-factor formula (23.341) only; no Part 25 tuned discrete gust or continuous turbulence (25.341) | Not established for a transport | not tracked yet |
| **T-tail induced rolling moment above Mach 0.6** | Not established; warned per subcase | design note 51 D-51.8 |
| **Aileron rolling moment** applied as one free couple at the wing aerodynamic centre | Either way on local station loads; the totals are exact | `AILERON_COUPLE_NOTE`, `sloads/modules/balance/constants.py` |
| **Control-surface chordwise distributions**: the standard simplified forms | Either way on local loads | `sloads/report/methods.py` |
| **Part 25 rows not yet built**: per-wheel and axle loads, 25.343(b) reserve fuel, transport flutter MFC, 25.351 yaw overswing, 25.345 flaps-down | Not delivered; the 25.351 fin load is low on the overswing phase | issue #412 |
| **Regulations outside the suite**: control-system loads, ground gust, water, jacking, towing and others | Not delivered | the `out_of_scope` rows of `sloads/report/coverage.py` |

Each standing limitation in the table is also printed in every report and
export, from the same owner (`_standing_limitations` in
`sloads/report/methods.py`).

## 4. Accuracy

- [Validation rationale](03_validation_rationale.md): what is checked, against
  what, and what validation does not claim.
- [Base-method uncertainty](00_theory_sources.md#base-method-uncertainty): the
  method's own error bar against a higher-fidelity analysis.
- [Approved corrections](02_approved_corrections.md): every place sloads
  deliberately departs from the manual, and why.

sloads is **not certified** for regulated structural design; its results should
be checked by competent engineering judgement before use
([`CAPABILITIES.md` §3](../../CAPABILITIES.md#3-verification-basis-and-limits)).
