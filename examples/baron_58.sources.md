# `baron_58.project.json` — data sources register

The oracle GUI user guide's worked twin (design note 34, UG-9): a Beechcraft
**Baron 58**, normal category, two Continental **IO-550-C** — the
configuration of Model 58 serials **TH-1396 through TH-2124** (plus TH-1389).

**Construction rule (UG-9).** Every certified value below is cited to the
document it was read in. Everything not published — mass breakdown, planform
chords, tail areas, nacelle butt line, aero coefficients — is **estimated**,
marked **[E]**, and never presented as the airplane's certified value. The
example exists to teach the tool; where an estimate is load-bearing the guide
says so. Stored values are Imperial (the project file's canonical channel);
the guide enters and reads this example in **SI** (UG-12).

## Primary sources

| Tag | Document |
|-----|----------|
| [A] | FAA Aircraft Specification **3A16, Rev 82** (Jan 31 2007), Section X (Model 58) and propeller item 13 |
| [B] | Beechcraft **Baron G58 Specification and Description**, Feb 2016 Rev A (Textron Aviation) — same airframe as the late Model 58 |
| [C] | Baron 58 **POH/AFM 58-590000-21**, Section II (airspeed limitations) and the flight-load-factors page |
| [E] | Estimated: statistical GA-twin value, or derived from the constructed planform. Not certified data. |

## Certified / published values used

| Quantity | Value | Source |
|----------|-------|--------|
| Certification basis, category | CAR 3 (as amended May 15 1956), **Normal** | [A] |
| Max takeoff weight | 5,500 lb | [A] |
| Max landing weight | 5,400 lb | [A] |
| Basic empty weight (typical) | 4,010 lb | [B] |
| CG limits | +78.3 to +86.0 in at 5,500 lb; +78.0 fwd at 5,400 lb; +74.0 to +86.0 at ≤4,200 lb | [A] |
| Datum | 83.1 in forward of the front-spar jack pads | [A] |
| Vne / Vno / Va / Vfe(30°) / Vle | 223 / 195 / 156 / 122 / 152 kt CAS | [A], [C] |
| Engines | 2 × Continental IO-550-C, 300 hp at 2,700 rpm (all operations) | [A] |
| Propellers | McCauley 3AF32C512 / 82NEA-5, 3 blades, 77 in dia, 82.5 lb each | [A] item 13 |
| Wing span / area / dihedral / c/4 sweep | 454 in / 199.2 ft² / 6.0° / 0.0° | [B] |
| Horizontal tail span | 191 in | [B] |
| Overall length | 358 in | [B] |
| Main gear track | 115 in | [B] |
| Usable fuel (standard) | 136 US gal at arm +82 | [A] |
| Seats / occupant arms | 6 (2 at +75, 2 at +117, 2 at +150) | [A] |
| Baggage | 300 lb at +15 (nose); 400 lb at +150 (rear) | [A] |
| Limit maneuver load factor | +4.2 g flaps up (POH figure at 5,400 lb; entered as STRSPEED's chosen n, so condition A flies at it, and as ENGLOADS' LIMNZ, which agrees with it — #331; the 23.337 minimum at 5,500 lb would be 3.648) | [C] |
| Airfoils | NACA 23016.5 root / 23010.5 tip (UIUC airfoil-usage guide, secondary) | [E]-class |
| Engine dry weight | 433 lb (IO-550 family, secondary reference — not read from TCDS E3SO) | [E]-class |

## Estimated values [E] and their anchors

- **Wing planform**: root 84 in / tip 42 in (taper 0.5). Anchored: the
  straight quarter-chord this gives sits at sta 83.0 ≈ the front-spar jack
  pads at 83.1 [A], and the trapezoid area (198.6 ft²) is within 0.3 % of the
  published 199.2 ft² [B]. MAC 65.3 in at buttline 101, x-LEMAC 66.7 — the
  WTENV %-MAC limits in the file are the [A] station limits through this MAC.
- **Tail areas**: h-tail 53 ft² on the published 191-in span; v-tail 24.3 ft²,
  66-in span. Statistical GA-twin proportions; tail stations placed against
  the published 358-in length [B].
- **Elevator and rudder** (design note 69 D-69.17, 2026-10-16): `elevator` and
  `rudder` surfaces entered as constant-chord-fraction polylines with a
  `hinge_line` (the trailing edge derives from the parent, D-54.1), constructed
  to integrate to the former typed SELECT scalars within 0.1 % -- SE fwd/aft
  **2.1 / 18.9** ft² (both sides) and SR fwd/aft **0.9 / 8.1** ft² -- with the
  hinge placed to the typed fwd/aft ratio. The six SELECT scalars (SE, SEFWDHL,
  SEAFTHL, SR, SRFWDHL, SRAFTHL) are now blank and derive from the polylines.
  [E], anchored on the former estimate; the tail loads move by the construction
  residual only (under 0.02 %).
- **Nacelle butt line ±66 in**: outboard of the 57.5-in gear half-track [B]
  (the mains retract into the nacelles), giving the 77-in prop [A] ~28 in of
  fuselage clearance.
- **Chosen Vd 248 kt**: from Vne = 0.9 Vd with the published Vne 223 [A]. No
  design dive speed is published.
- **CLmax clean 1.15 / flaps 1.53**: derived from typical published stall
  speeds (~84 kt clean, ~73 kt landing) at MTOW through the constructed wing
  loading — the module's clean 1-g stall reproduces ~84 KEAS.
- **Mass breakdown**: statistical component split summing to the published
  4,010 lb empty [B] at sta 78.3; discretionary rows (occupants, baggage,
  fuel) sit at the [A] arms. The `aft gross` case (5,500 lb at the [A] aft
  limit 86.0) states its loading since #337: the MZFW payload (every seat,
  nose hold 0.1458, rear hold 0.2656) plus 230 lb of fuel (both tanks at
  0.3194). Its waterline 96.56 is that loading's own (D-26a; no source states
  a flight waterline). Until #337 it was searched, and the search closed it
  with 4 occupants and no pilot, at waterline 95.88. Each
  roled ground case **states its loading** (D-25 `loading` records). Inertias
  are order-of-magnitude estimates.
- **Pilot (#337, design note 75)**: the pilot is its own `MINIMUM` row tagged
  `required_crew`, 170 lb at the [A] front-seat arm +75. The weight is [E], the
  23.25(b)(2) standard crewmember (UG §4.3.1.2 p4-3); no source gives this
  airplane's. `Front passenger` (170 lb, same point) is discretionary. Until
  #337 both sat in one discretionary row, so the minimum flight weight
  (4,100 lb at 78.36) and `aft max landing` flew with nobody at the controls.
  The minimum flight weight is now 4,270 lb at 78.22.
- **Payload cases (note 75 §2)**: the MZFW and full-fuel corners are built to
  the owner's rule, each waterline from its own loading (D-26a):
  - `mzfw aft`: 5,270 lb at the [A] aft limit 86.00. Every passenger is
    aboard; the nose hold is at 0.1688 and the rear at 0.2484.
  - `mzfw fwd`: 5,270 lb at **79.61**, the most forward 5,270 lb the rows
    reach (station-order fill: nose hold, front seat, mid seats, then the
    rear hold at 0.475). The forward limit there is 77.54, so the corner is
    **2.07 in short** of it. It is kept at the extreme and not ballasted.
  - `fwd gross` (below) is the full-fuel forward corner.
  - `full fuel aft`: 5,500 lb at **85.37**, the most aft that full fuel and
    510 lb of payload reach (aft seats, rear hold at 0.425). The aft limit is
    86.0, so the corner is **0.63 in short**.
  - `aft max landing` and `fwd max landing`: on the limits at the 5,400 lb
    landing weight since #422 (design note 76 Q1 (a)). Aft, 86.0: the MZFW
    payload plus 130 lb of fuel, re-split onto the line. Forward, 77.96: the
    MZFW payload cannot reach it, so full fuel and the least payload. They
    were the two MZFW payloads plus fuel wherever that put them (85.90,
    79.67).
- **Baggage rows (#309)**: nose baggage is the [A] 300 lb at +15 (it carried
  150 lb until #309), and the [A] 400 lb rear compartment at +150 is its own
  row; the rear row's waterline 100 is [E], the seats' own, since no source
  states it. Every loading entered before the correction carries the nose
  hold at 0.5, so each is the same mass it was.
- **`fwd gross` (#309)**: the [A] forward limit at gross weight (5,500 lb at
  78.3) is entered as a loading of this database with no ballast — pilot and
  front passenger, both wing tanks full, the nose hold at 0.4881 (146.4 lb) and
  the mid passengers at 0.5693 (193.6 lb), solved to weigh 5,500 lb at 78.30 — and its waterline 95.75 is that
  loading's own (D-26a). The whole-row search cannot find it (it asked for
  13 % ballast); two part-filled rows reach it.
- **`fwd regardless` is not a loading of this airplane (#309)**: the [A]
  forward limit at 4,200 lb (74.0) lies 2.85 in forward of the most-forward
  4,200 lb loading (76.85: the empty airplane, unusable fuel and 100 lb of
  nose baggage), and no ballast inside the fuselage closes it. The case is
  kept as entered and flagged (`envelope_point_unreachable`, the 2.2 case
  table): FLTLOADS balances its weight and CG, no assembled case carries it,
  and its waterline 99.0 has no source and no loading to take one from.
- **Gear geometry**: axle stations/waterlines, 8-in oleo stroke, 20-in tire —
  statistical; tread is the published 115 in [B], oleo strut type per the
  Baron's air-oil gear.
- **Aero coefficients** (section slope 0.107/deg, cm −0.008, polar, twist,
  elevator/rudder throws and hinge splits, tab data): handbook-typical values
  for the 230-series sections and a GA twin; none are published data.

- **One-engine-out feather and timing** (design note 74 D-74.3, D-74.11, #405,
  2026-11-02): `feather_travel_time_s` 1.0 s on both engines, [E], the owner's
  estimate of the blade travel to feather (Q3); no maker's figure is in hand. The
  pilot starts the feather 2 s after the failure (23.367(b), an owner assumption).
  No autofeather is modelled; the Baron's propellers are feathered by hand. The
  fuel-flow `thrust_decay_time_s` 0.5 s and `windmill_drag_time_s` 2.0 s have **no
  source**; Lomax (1996) p. 42 gives 1 s to several seconds for a fuel-flow
  interruption, so they are an open input gap, not a datum.

## Cross-checks the file passes

- Loads every page of the oracle GUI; all 14 run without error (gate G-UG-4,
  `tests/test_guide.py`), including ONENGOUT with the off-centreline failed
  engine.
- The one limit it cannot reach is warned on load (`envelope_point_unreachable`
  for `fwd regardless`, the case and the entered limit, with
  `wing_case_loading_not_derivable` for its inertia) and nothing else: loading CG inside the WTENV
  envelope, the G-4/G-14 weight chain, the note-29 wing-mass tie
  (items tagged `wing` = 2 × (WINGINER panel + concentrated)) all close.
- The oracle **reduction reproduces it exactly** (`tests/test_oracle_inputs.py`
  `EXACT`): every load-bearing field is an original-suite input — engine and
  propeller weight/CG are entered directly on the ENGLOADS records (duplicated
  into the weight database rows at the same values, the cessna_210 pattern).
  The one declared exception is the pilot feather (design note 74), a sloads
  input that moves the one-engine-out fin cases
  (`test_oracle_inputs.PILOT_FEATHER`).
