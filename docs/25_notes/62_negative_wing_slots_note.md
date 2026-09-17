# The negative angle-of-attack wing slots, above SELECT.BAS (design note 62)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: PROPOSED 2026-09-17** (owner, in session, under the solo profile —
`DEVELOPMENT_PROCESS.md` §0; rule 1's working-alone branch). The rulings in
§2 are the owner's, taken in chat on 2026-09-17; they are the **case-set
shape decision** the backlog's B7 row 1 (#164) has waited on since 2026-09-14.
Filed as **#288** (band B7, 0.8.6). This note is scoped to **SELECT's wing search alone**. The companion change
the same discussion agreed — wing mass states in the Wing Loads step, so
each selected case runs at every disposable-mass state (inertia relief) — is
**the next note**, not this one (§6).

**Tier L.** A new load-case family on the wing: two SELECT slots the
`.BAS` does not have, two fixed case ids, and a deck that gains two
subcases. No oracle moves (§4 gate 1); the six Appendix A picks are the
same points on the same figures.

---

## 1. Measurements (2026-09-17, at `dev/v0.8.6` = tag `v0.8.5`)

### 1.1 How SELECT's wing search works

FLTLOADS balances every flight condition at every entered altitude
(`flight_loads.altitudes_ft`), every balance configuration and every FLIGHT
weight/CG case, so the V-n matrix is `altitudes × configs × CG cases × 20
conditions` (a flapped configuration is balanced at sea level only,
FLTLOADS.BAS line 3000). Each `VnPoint` carries its load factor, EAS,
altitude, CG case, wing lift `LZW` (normal to the reference, less tail) and
airplane drag `DX`. SELECT.BAS subroutine 3000 (Appendix C, lines
2990–3540) then runs **six named searches over the whole matrix**, one per
FAR 23.333 / 23.349 family; each returns exactly one point, so the wing
gets six delivered cases whatever the matrix size (`select_wing`,
`sloads/modules/select.py`). The search is on **air load only** — the
resultant or `LZW` of the balanced point before any inertia relief — at
whatever altitude and CG case wins:

| Slot | Candidates | Picks the point with | What the case is for (typically governs) |
|---|---|---|---|
| **PHAA** | STALL +N, MAN A | largest resultant `√(LZW² + DX²)` | lift at CL-max, CP furthest forward, chord force forward: **front spar** cap bending and web shear, forward chord bending `Mzz`; usually the maximum root shear and bending at the heaviest weight (Appendix A case 22, the net-loads worked example) |
| **PLAA** | MAN D, GUST D | largest resultant | limit n at VD, small CL, CP furthest aft, largest nose-down air torsion and drag: **rear spar** bending and shear, box skin shear in the nose-down sense, drag bracing, aft chord bending |
| **PMAA** | MAN C, GUST +C | largest `LZW` | the VC gust is often the largest n in the envelope: **root bending `Mxx` and upper-skin compression** on a gust-critical wing; picked on `LZW` for that reason |
| **NMAA** | STALL −N, MAN −C, MAN −D, GUST −C, GUST −D | largest resultant | load reversal: **lower skin and lower caps in compression**, ribs and attachments under reversed load, a strut in compression |
| **ACRL** | AC ROLL | largest `LZW` | two-thirds n with ailerons deflected: **outer-wing bending and shear** outboard of the aileron, the aileron hinge and backup rib, the unbalanced rolling moment the fuselage carries as differential root shear |
| **TORS** | ST ROL A, ST ROL C, ST ROL D | most negative `(CM − 0.01·δ)·G·V²`, δ per CAM 3.222 | aileron pitching-moment increment added to the aerofoil CM at high q: **torsion-box skin shear**, the rear spar as the box's aft wall, aileron hinge loads; ST ROL C usually wins because the VD deflection is halved |

Two properties of the method matter for what follows. First, it is a
**per-family maximum, not an envelope**: one point per family is delivered
and every other point in the family is discarded, so a family whose
members load different members of the wing box needs one slot per member.
Second, it is a **pick on air load at the winning weight**: the point
with the largest air resultant is normally a heavy case, which is also the
case with the most wing-mass relief, and no net-load quantity enters the
choice. The second property is the subject of the next note, not this one.

### 1.2 What SELECT.BAS does on the negative side

Three positive slots, **one negative**. NMAA's candidate set is every
negative label at once, picked on the largest resultant (`_NMAA`,
`select_wing`). STALL −1G is balanced by FLTLOADS but is a candidate of
nothing.

The positive triad exists because **centre-of-pressure position, not load
magnitude alone, decides which spar governs**: the forward-CP stall-line
point loads the front spar, the aft-CP VD point loads the rear spar and the
torsion box, the VC gust point carries the largest root bending on a
gust-critical wing (`docs/20_theory/ch04_wing_loads.md` §"SELECT
down-select"). The negative side has no such triad: whichever negative point
has the largest resultant is delivered, and the other spar's down-load case
is discarded at SELECT with nothing said. This is the CAR 3 / ANC-1
heritage set (PHAA, PLAA, **NHAA, NLAA**) with its two negative members
collapsed into one.

### 1.3 What the one slot discards, on the shipped fixtures

Measured through `select.default_envelope` + `select._pick` on every
fixture (V-n matrix sizes: ga6_normal 80, baron_58 180, atr42_100 300,
concept_regional_jet 200, concept_heavy 20):

| Fixture | NMAA today (one pick) | Dropped: stall-line negative | Dropped: VD negative |
|---|---|---|---|
| ga6_normal | GUST −C, −2.43 g, CG3, 0 ft, case 53, R 6,772 | STALL −N −1.52 g CG2, case 28, R 5,105 (forward CP) | GUST −D −1.69 g CG4, case 72, R 3,226 |
| atr42_100 | STALL −N, −1.00 g, fwd gross, 12,000 ft, case 128, R 36,841 | — (it is the pick) | GUST −D −0.63 g min weight, case 172, R 12,055; **and** GUST −C −1.44 g min weight, case 173, R 27,272 |

On the ATR the pick between STALL −N (case 128) and MAN −C (case 227,
R 36,594) is decided by the **drag term** of the resultant, and the
−1.44 g gust at minimum weight — the lightest wing, the least inertia
relief, the highest gust factor — reaches no wing distribution, no report
row and no deck subcase. On the GA6 the forward-CP stall point is the one
discarded.

### 1.4 A positive point can win a negative slot

Restricting nothing but the label, the VD family's largest resultant on
two fixtures is a point with **positive** wing lift: atr42_100 GUST −D at
25,000 ft balances to **+0.35 g** (case 232, LZW +13,352 lb) because the
gust increment at that altitude is smaller than 1 g; concept_heavy's MAN −D
is the category's **0 g** point (case 6, LZW +373 lb). Today's NMAA never
meets this because a stall-line or VC point always out-resultants them, but
a VD-only slot would deliver a positive-lift "negative" case unless
eligibility is stated (D-62.2).

### 1.5 Where a new slot reaches

Every consumer of the wing slot list, found by `WING_SLOTS` and the label
tuples:

* `sloads/case_ids.py` `WING_SLOTS` — the fixed id per slot (W-01…W-06 today;
  the band runs to W-19).
* `sloads/modules/select.py` `select_wing` — the picks; `_condition` wraps
  each as a `CriticalCondition` with `nx = -DX/W`.
* `sloads/modules/wing_inertia.py` `resolve_wing_cases` — derives
  `WingMassInput.cases` from SELECT's wing set **only when the table is
  empty**. **Every shipped fixture enters explicit rows** (ga6_normal
  PHAA/TORS/ACRL; baron_58 PHAA/TORS; atr42_100 PHAA; concept_regional_jet
  PHAA/TORS/ACRL; concept_heavy PHAA), so on no fixture does a new slot reach
  WINGINER, AIRLOADS or NETLOADS. The Appendix A net-loads oracles (cases
  22/160/138) are unreachable by construction.
* `sloads/modules/balance/constants.py` `SYMMETRIC_WING_CONDITIONS` — the
  wing conditions the balanced producer assembles, hence the **LRA deck's
  wing subcases** (note 56 D-56.8/D-56.9). A slot not in this tuple is a
  SELECT condition the deck does not carry, which #284 would then have to
  state as a skip.
* The oracle report's §3.2 run register and the case index (note 44 OR-54),
  which print every SELECT wing condition; `tests/test_oracle_report.py`
  asserts the run column per label.
* `docs/10_standard/PROGRAM_SPEC.md` (SELECT's writes, the case-id rule at
  "PHAA 1, PLAA 2, …"), `docs/20_theory/ch04_wing_loads.md` §"SELECT
  down-select" table, `docs/20_theory/00_theory_sources.md` SELECT row.

## 2. Owner rulings (2026-09-17, in chat)

1. **SELECT gains two wing slots, NHAA and NLAA**, and NMAA is narrowed to
   the VC pair, so the negative side carries the same angle-of-attack triad
   as the positive side. Two additional, not three: NMAA keeps its name, its
   id and its Appendix A pick.
2. **Inertia relief is not SELECT's problem.** SELECT stays an air-load
   selector; the per-mass-state variants are handled in the Wing Loads step
   (WINGINER/NETLOADS) by the next note. Nothing in this note selects on
   net load or on weight case.
3. This is one issue — **#288** — tier L, in band B7 (0.8.6, the baseline wave), ahead of #164.

## 3. Decisions

- **D-62.1 — The negative triad.** `select_wing` picks, on the largest
  resultant `√(LZW² + DX²)` (the PHAA/PLAA criterion, which the `.BAS`
  already uses for NMAA):

  | Slot | Candidates | FAR basis | Typically sizes |
  |---|---|---|---|
  | **NHAA** | STALL −N, STALL −1G | 23.333(b)/(c), 23.337(b) | front spar and lower forward skin in compression; reversed rib loads |
  | **NMAA** (narrowed) | MAN −C, GUST −C | 23.333(b)/(c) | lower caps and skin, root down bending, a strut in compression |
  | **NLAA** | MAN −D, GUST −D | 23.333(b)/(c) | rear spar under reversed load, nose-up torsion at VD |

  STALL −1G joins NHAA's candidates so the slot is well-defined on a
  category whose `n_neg` is −1.0 (the two labels then coincide, as on the
  ATR) and on one whose negative envelope is a −1 g floor.
- **D-62.2 — A negative slot admits negative lift only.** A candidate is
  eligible when `LZW < 0`; a slot with no eligible candidate is **empty**,
  which `case_ids` already spells as a gap in the W- band (W-01 is PHAA
  because it is PHAA). §1.4 is why: without the rule NLAA delivers a
  +0.35 g point on the ATR as a "negative low angle of attack" case. The
  rule is applied to all three negative slots, so NMAA cannot regress into
  it either.
- **D-62.3 — Fixed ids: NHAA is W-07, NLAA is W-08.** Appended to
  `WING_SLOTS` after TORS; W-01…W-06 do not move and no persisted
  `selected_case_ids` or exported deck re-reads.
- **D-62.4 — The deck carries them.** NHAA and NLAA join
  `SYMMETRIC_WING_CONDITIONS` (a negative point has no unbalanced rolling
  moment, exactly as NMAA), so the LRA deck gains **two symmetric wing
  subcases** and the assembled producer balances them under G-OR-72 like
  the rest. They are not skips for #284 to state.
- **D-62.5 — The six Appendix A picks are locked, the two new slots are
  closure-gated.** The manual prints no NHAA/NLAA figure (it has no such
  slot), so rule 2's second branch applies: a stated invariant in CI (§4
  gates 2–3) plus the frozen per-fixture picks of §4 as the regression
  baseline.
- **D-62.6 — This is an extension above the `.BAS`, not an oracle
  deviation.** The `.BAS`'s six picks reproduce unchanged on GA inputs;
  the two slots are additive, which is the concept-mode superset rule
  (`CLAUDE.md` Mission). Nothing enters `02_approved_corrections.md`;
  `theory_sources.md`'s SELECT row cites this note for the two slots and
  `ch04_wing_loads.md`'s table gains two rows.
- **D-62.7 — Fixtures' explicit wing-case tables are not touched here.**
  §1.5: every fixture enters `wing_mass.cases` by hand, so WINGINER/
  NETLOADS/AIRLOADS output does not move on any fixture in this issue. Which
  fixture rows should give way to the derived set (the ATR's one mislabelled
  `PHAA` at −2.5 g is #260 E6) is a fixture question for the baseline wave,
  ordered after this note and after the mass-state note.

## 4. Gates

1. **The oracle does not move.** `tests/test_select.py`'s Appendix A table
   (PHAA 22, PLAA, PMAA, NMAA GUST −C −0.433 at 170 kt CG3, ACRL, TORS)
   passes unchanged, and every existing Imperial digest under `select`,
   `net_loads`, `wing_inertia`, `airloads` for the six slots is byte-identical.
   NMAA's narrowing to the VC pair returns the same point on every fixture
   (§1.3 GA6 case 53; measured on all five).
2. **G-62.1 — The negative-triad invariant.** For every fixture and every
   negative slot: the delivered point is a member of the slot's candidate
   labels, has `LZW < 0`, and no other V-n point with those labels and
   `LZW < 0` has a larger resultant; and a slot with no eligible candidate
   is absent from the critical set rather than filled.
3. **G-62.2 — The frozen picks.** The regression baseline for the new slots
   is the table below, held by the Imperial digest and by name in the test:

   | Fixture | NHAA | NMAA | NLAA |
   |---|---|---|---|
   | ga6_normal | STALL −N case 28, −1.52 g, 113.5 kt, CG2, 0 ft, R 5,105 | GUST −C case 53 (unchanged) | GUST −D case 72, −1.69 g, 212.5 kt, CG4, 0 ft, R 3,226 |
   | baron_58 | STALL −N case 28, −1.46 g, 134.2 kt, fwd gross, 0 ft, R 8,011 | GUST −C case 113, −2.35 g, 195 kt, fwd regardless, 10,000 ft, R 9,844 | GUST −D case 112, −1.21 g, 248 kt, fwd regardless, 10,000 ft, R 4,884 |
   | atr42_100 | STALL −N case 128, −1.00 g, 170.9 kt, fwd gross, 12,000 ft, R 36,841 | MAN −C case 227, −1.00 g, 183.3 kt, fwd gross, 25,000 ft, R 36,594 | GUST −D case 172, −0.63 g, 300 kt, min weight, 12,000 ft, R 12,055 |
   | concept_regional_jet | STALL −N case 128, −1.00 g, 150.5 kt, fwd gross, 20,000 ft, R 34,454 | GUST −C case 173, −1.80 g, 310 kt, min weight, 20,000 ft, R 35,650 | GUST −D case 172, −0.80 g, 350 kt, min weight, 20,000 ft, R 14,457 |
   | concept_heavy | STALL −N case 8, −2.00 g, 195.3 kt, CGmax, 0 ft, R 32,463 | MAN −C case 7, −2.00 g, 250 kt, CGmax, 0 ft, R 32,367 | GUST −D case 12, −0.02 g, 312.5 kt, CGmax, 0 ft, R 2,335 |

   Resultants in lb, LIMIT, before any inertia. The ATR's NMAA moves from
   case 128 to case 227 under the narrowing (128 belongs to NHAA now); every
   other fixture's NMAA is the same point as today. V-n case numbers are the
   matrix's own and **renumber when #164 adds 12,000 ft to the GA6**; the
   gate names the point by label, load factor, speed, CG and altitude, not by
   number, so it survives that.
4. **G-62.3 — The deck.** On every CLI-exportable fixture the LRA deck's
   SUBCASE set gains exactly W-07 and W-08 (where the slot is non-empty),
   each closing G-OR-72 and G-OR-73 like the six before it; #284's skip
   record does not list them.
5. **G-62.4 — Case ids.** `tests/test_case_ids.py`: W-07/W-08 are minted for
   NHAA/NLAA and for nothing else; a critical set that omits either leaves
   the gap; the hand-authored band W-20+ is unaffected.
6. **Report.** §3.2's run register prints both rows on every fixture with
   `run = no` (D-62.7: no fixture derives its wing-case table), and
   `test_oracle_report.py`'s per-label run assertion is extended to them.

## 5. Effect vs error bar (rule 6)

Not a fidelity item: it is a **coverage** defect on shipped content. A
down-load case for one spar is absent from every deliverable, and on the
ATR the absent case is a −1.44 g gust at the lightest wing. Rule 6's second
sentence applies (a first-order gap on shipped content outranks every
fidelity item).

## 6. What this supersedes / touches, and what it leaves

- Supersedes nothing. Amends `ch04_wing_loads.md`'s SELECT table (two rows,
  NMAA's criterion narrowed) and `PROGRAM_SPEC.md`'s SELECT writes and
  case-id rule; `theory_sources.md` SELECT row cites this note.
- **Settles #164's "owner decision on the case-set shape"** for the negative
  side. #164's own work (GA6 `altitudes_ft` and the V-n renumber it costs)
  is unchanged in scope and follows this issue in the wave, since its
  renumber moves the case numbers the §4 table names.
- **Leaves to the next note:** wing mass states in the Wing Loads step —
  named disposable-mass states on `WingMassInput`, WINGINER/NETLOADS run
  per selected case per state, the base model when none is entered. The
  air-load pick per slot stays the one balanced at SELECT's CG case; that
  a heavy pick run at zero fuel is conservative, not exact, is the caveat
  that note states.
- **Leaves parked, with its number:** a pick on **net** root bending
  instead of air resultant. Whether it would ever change a slot's point is
  measurable only once mass states exist; measured then, filed then.

## 7. Closure obligations (tier L)

`PROGRAM_SPEC.md` SELECT section + case-id rule; `ch04_wing_loads.md` table;
`theory_sources.md` SELECT row; `CONVENTIONS.md` §case identity unchanged
(the id rule already admits gaps); one `changes/<slug>.history.md` fragment
in full step format; one Imperial digest wave (`select`, the deck, the
report register; **not** `net_loads`/`wing_inertia`/`airloads`); this note
flipped to `shipped <date>`; #164's dependency column updated.
