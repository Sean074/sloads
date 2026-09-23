# The negative angle-of-attack wing slots, above SELECT.BAS (design note 62)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-09-17** (#288; the shipping measurements that differ
from the gates as written are §8). Previously **AGREED 2026-09-17** (owner, in session, under the solo profile —
`DEVELOPMENT_PROCESS.md` §0; rule 1's working-alone branch; PROPOSED and
reviewed the same day — the critical-advocate review's findings and the
owner's rulings on them are §2 rulings 4–5, D-62.8 and the amended D-62.2,
D-62.4, G-62.3). The rulings in
§2 are the owner's, taken in chat on 2026-09-17; they are the **case-set
shape decision** the backlog's B7 row 1 (#164) has waited on since 2026-09-14.
Filed as **#288** (band B7, 0.8.6). This note is scoped to **SELECT's wing search alone**. The companion change
the same discussion agreed — wing mass states in the Wing Loads step, so
each selected case runs at every disposable-mass state (inertia relief) — is
**the next note**, not this one (§6).

**Tier L.** A new load-case family on the wing: **four** SELECT slots the
`.BAS` does not have — the negative angle-of-attack pair NHAA/NLAA (D-62.1)
and the load-factor-extreme pair PNZ/NNZ (D-62.8) — four fixed case ids,
and a deck that gains up to four subcases. No oracle moves (§4 gate 1); the
six Appendix A picks are the same points on the same figures.

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

The +0.35 g point is the visible case of a wider set. A balanced point can
carry a **negative airplane load factor with positive wing lift** when the
tail down-load exceeds the small negative `nz·W` — the 0 g "MAN −D" points
of the normal and commuter categories (nz = −0.0, LZW a few hundred pounds
up) are the same thing. Measured in the VD family alone, the points
`LZW < 0` excludes and how many of those have `nz < 0`:

| Fixture | Excluded by `LZW < 0` | of which `nz < 0`, wing lift up |
|---|---|---|
| atr42_100 | 26 | 15 |
| concept_regional_jet | 13 | 2 |
| baron_58 | 9 | 0 |
| ga6_normal | 4 | 1 |
| concept_heavy | 1 | 0 |

None of them changes a pick in §4 G-62.2; the table exists so a reader who
expects the negative slots to mean "negative g" sees why the gate tests the
wing's own lift instead (D-62.2).

### 1.4a The extreme load-factor points are not delivered, on either sign

Every slot picks on air load, so the heavy case wins, and the point with the
largest |nz| in the matrix — at minimum weight, where the 23.341 gust factor
is highest — reaches no deliverable. With the negative triad of D-62.1 in
place (measured 2026-09-17):

| Fixture | Most negative nz, wing lift down | Delivered by a slot? | Largest positive nz | Delivered? |
|---|---|---|---|---|
| ga6_normal | GUST −C −3.25 g, CG4 | no (NMAA −2.43 g at CG3) | GUST +C 5.25 g, CG4 | no (PMAA 3.96 g at CG2) |
| atr42_100 | GUST −C −1.44 g, min weight | no (NMAA −1.00 g fwd gross) | GUST +C 3.44 g, min weight | no (all three 2.50 g) |
| baron_58 | GUST −C −2.35 g, fwd regardless | yes (NMAA) | GUST +C 4.34 g, fwd regardless | no (all three 3.65 g) |
| concept_regional_jet | GUST −C −1.80 g, min weight | yes (NMAA) | GUST +C 3.80 g, min weight | no (2.50–2.87 g) |
| concept_heavy | MAN −C −2.00 g | yes (NMAA) | MAN C 4.00 g | yes (PMAA) |

On the GA6 the undelivered points are 5.25 g and −3.25 g against delivered
3.96 g and −2.43 g. That is the case that sizes everything hung on the wing
by its own mass — engine mounts, tank attachments, wing-mounted gear,
stores, the tip region where inertia is a large share of the net load —
and it is a defect on the six shipped slots today, not only on the new
ones. Root bending is normally the heavy case, which is why the `.BAS`
criterion never met it (D-62.8).

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
* `sloads/modules/balance/air.py` `build_balanced_cases` — carries a
  condition only when its V-n point's CG case has a **derivable** loading
  (plan 12 C-1), else records a `loading-not-derivable` skip. Measured: every
  FLIGHT case derives on ga6_normal, atr42_100, concept_regional_jet and
  concept_heavy; on baron_58 "fwd gross" and "fwd regardless" do **not**, and
  NLAA's Baron pick (§4 G-62.2) is at "fwd regardless".
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
4. **(review finding 1)** A new slot whose CG case has no derivable loading
   is a `loading-not-derivable` skip like any of the six, stated by #284;
   #288 does not enter or repair loadings (D-62.4, G-62.3).
5. **(review finding 2a)** SELECT gains the load-factor-extreme pair
   **PNZ/NNZ** (D-62.8), in the same issue, on the same gate shape. The
   negative slots select on the **wing's** lift sign, and the note says
   why (§1.4, D-62.2).

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
  it either. **The sign tested is the wing's lift, not the airplane's load
  factor**, because the slot is a wing selector: a point with `nz < 0` and
  `LZW > 0` (§1.4's table — 15 on the ATR) loads the wing *upward* and
  belongs to no down-load slot, while a point with `LZW < 0` at small
  positive nz (none on any fixture, but a large up-tail-load could make
  one) is a genuine wing down-load. `LZW < 0` alone is therefore the rule;
  `nz < 0` is neither necessary nor sufficient. The same rule mirrored —
  `LZW > 0` — is PNZ's eligibility (D-62.8).
- **D-62.3 — Fixed ids: NHAA is W-07, NLAA is W-08, PNZ is W-09, NNZ is
  W-10.** Appended to `WING_SLOTS` after TORS in that order; W-01…W-06 do
  not move and no persisted `selected_case_ids` or exported deck re-reads.
- **D-62.4 — The deck carries them.** NHAA, NLAA, PNZ and NNZ join
  `SYMMETRIC_WING_CONDITIONS` (none is a roll point, so no unbalanced
  rolling moment, exactly as NMAA), so the LRA deck gains **up to four
  symmetric wing subcases** and the assembled producer balances them under
  G-OR-72 like the rest. An **empty** slot (D-62.2) is a gap in the W- band, not a skip
  for #284 to state; a slot whose winning CG case has no derivable loading
  is a `loading-not-derivable` skip **exactly as the six slots before it**
  (review 2026-09-17, finding 1: on `baron_58` NLAA's pick sits at "fwd
  regardless", which the search cannot derive today, so W-08 is skipped
  there until that loading is entered -- #290 -- or the fixture's item
  database is corrected in the baseline wave).
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
- **D-62.8 — The load-factor-extreme pair, PNZ and NNZ (owner, review
  finding 2a).** Two further slots on the pattern of D-62.1, selecting on
  **load factor** rather than air load, so the point that sizes the
  wing-mounted masses is delivered whatever weight it occurs at (§1.4a):

  | Slot | Candidates | Eligible | Picks | Tie-break | FAR basis |
  |---|---|---|---|---|---|
  | **PNZ** | every positive-family label (STALL +N, MAN A, MAN D, GUST D, GUST +D, MAN C, GUST +C) | `LZW > 0` | largest `nz` | largest resultant | 23.337(a), 23.341 |
  | **NNZ** | every negative-family label (STALL −N, STALL −1G, MAN −C, GUST −C, MAN −D, GUST −D) | `LZW < 0` | most negative `nz` | largest resultant | 23.337(b), 23.341 |

  The roll families (AC ROLL, ST ROL) are not candidates: their load factor
  is two-thirds of the manoeuvre value by construction (23.349) and they have
  their own slots. **Coincidence rule:** a PNZ/NNZ point that is already
  another slot's pick is **not delivered a second time** — the slot is
  empty and its id is a gap in the band, so one physical condition never
  carries two ids (`case_ids` M4-2 decision 1). Measured: NNZ coincides
  with NMAA on baron_58, concept_regional_jet and concept_heavy, PNZ with
  PMAA on concept_heavy; on ga6_normal and atr42_100 both are new points
  (§4 G-62.2). These two slots are also an extension above the `.BAS`
  (D-62.6), gated like NHAA/NLAA (D-62.5), and they are what makes note
  63's D-63.7 a question of *mass state* only: the nz extremes are already
  in the slot set, so the variant expansion never has to recover them.

  **In-code amendment at #294 (0.8.6 pre-cut review, 2026-09-22) — the
  coincidence rule is a delivery rule, applied once, to the delivered set.**
  As shipped it ran on the *air* picks, before note 63's re-pointing: on
  baron_58 and concept_regional_jet NNZ was emptied against NMAA's air
  pick, NMAA then moved to a zero-fuel case, and the 23.337(b) extreme
  (Baron V-n case 153 at −2.345 g, RJ case 213 at −1.805 g) was carried by
  nothing in the one deck that ships. `wing_slot_picks` is now the search
  alone, `select.air_picks` lists every slot's pick whatever the other slots
  picked, and `select_wing` applies `_coincidence_rule` after the
  re-pointing: a PNZ/NNZ slot is empty only when the point it would deliver
  is another *delivered* slot's. Two rulings travel with it: (i) the tie in
  the table above is the balance's own band — two points converged to one
  target differ by up to `2 × constants.NZ_BALANCE_TOL` (0.01 g) and are one
  load factor, the tie going to the larger resultant; the shipped 1e-9
  relative tie never matched two balanced points, so the resultant
  tie-break never fired (on concept_heavy PNZ's air pick is now MAN A at
  4.001 g over GUST +C at 4.002 g, and it still coincides, with PHAA); and
  (ii) an air-pick slot (`AIR_PICK_SLOTS`) keeps its air pick without
  exception — `wing_variant_table` assesses every air pick at its own CG
  case, so the row always exists, and `_mark_governing` raises rather than
  re-points such a slot on bending. Measured after: NNZ is delivered on the
  Baron (W-10, at "fwd regardless", the record's until #290) and on the RJ
  (W-10, assembled); the heavy's PNZ/NNZ still coincide (with PHAA and
  NHAA) and are empty at delivery; ga6_normal and atr42_100 do not move.
  Gates: G-62.1 gains its loss side — on every fixture each eligible
  PNZ/NNZ extreme is carried by some delivered wing case — G-62.2 is
  re-pinned on the air picks, G-62.5 holds the tie band to the tolerance
  owner, and G-63.3 asserts the air pick for every air-pick slot with no
  "assessed and not delivered" escape.

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
   NMAA's narrowing to the VC pair returns the same point on the GA6 (§1.3
   case 53), the Baron and the RJ; on the ATR and the heavy the `.BAS`'s
   NMAA was the STALL −N point, which is NHAA's now, and NMAA moves to the
   VC point (G-62.2's table; §8 corrects the AGREED text, which said the
   ATR alone moves).
2. **G-62.1 — The negative-triad invariant.** For every fixture and every
   negative slot: the delivered point is a member of the slot's candidate
   labels, has `LZW < 0`, and no other V-n point with those labels and
   `LZW < 0` has a larger resultant; and a slot with no eligible candidate
   is absent from the critical set rather than filled. **And the
   load-factor invariant (D-62.8):** PNZ's point has the largest `nz` of
   every eligible positive-family point and NNZ's the most negative of
   every eligible negative-family point; a PNZ/NNZ point that equals
   another slot's pick is absent, and a critical set never carries one V-n
   case number under two wing ids.
3. **G-62.2 — The frozen picks.** The regression baseline for the new slots
   is the table below, held by the Imperial digest and by name in the test:

   | Fixture | NHAA | NMAA | NLAA |
   |---|---|---|---|
   | ga6_normal | STALL −N case 28, −1.52 g, 113.5 kt, CG2, 0 ft, R 5,105 — *since #164 (2026-09-20): case 108, 112.3 kt, 12,000 ft, R 5,137* | GUST −C case 53 (unchanged) — *since #164: case 133, −2.80 g, 12,000 ft, R 7,834* | GUST −D case 72, −1.69 g, 212.5 kt, CG4, 0 ft, R 3,226 — *since #164: case 152, −2.08 g, 12,000 ft, R 4,034* |
   | baron_58 | STALL −N case 28, −1.46 g, 134.2 kt, fwd gross, 0 ft, R 8,011 | GUST −C case 113, −2.35 g, 195 kt, fwd regardless, 10,000 ft, R 9,844 | GUST −D case 112, −1.21 g, 248 kt, fwd regardless, 10,000 ft, R 4,884 |
   | atr42_100 | STALL −N case 128, −1.00 g, 170.9 kt, fwd gross, 12,000 ft, R 36,841 | MAN −C case 227, −1.00 g, 183.3 kt, fwd gross, 25,000 ft, R 36,594 | GUST −D case 172, −0.63 g, 300 kt, min weight, 12,000 ft, R 12,055 |
   | concept_regional_jet | STALL −N case 128, −1.00 g, 150.5 kt, fwd gross, 20,000 ft, R 34,454 | GUST −C case 173, −1.80 g, 310 kt, min weight, 20,000 ft, R 35,650 | GUST −D case 172, −0.80 g, 350 kt, min weight, 20,000 ft, R 14,457 |
   | concept_heavy | STALL −N case 8, −2.00 g, 195.3 kt, CGmax, 0 ft, R 32,405 (32,463 before #291) | MAN −C case 7, −2.00 g, 250 kt, CGmax, 0 ft, R 32,273 (32,367) | GUST −D case 12, −0.02 g, 312.5 kt, CGmax, 0 ft, R 2,752 (2,335) |

   And the load-factor pair (D-62.8), with the coincidence rule applied:

   | Fixture | PNZ (W-09) | NNZ (W-10) |
   |---|---|---|
   | ga6_normal | GUST +C case 70, +5.25 g, 170 kt, CG4, 0 ft, R 11,335 — *since #164: case 150, +5.81 g, 12,000 ft, R 12,508* | GUST −C case 73, −3.25 g, 170 kt, CG4, 0 ft, R 6,644 — *since #164: case 153, −3.81 g, 12,000 ft, R 7,834* |
   | baron_58 | GUST +C case 110, +4.34 g, 195 kt, fwd regardless, 10,000 ft, R 18,961 | **empty** — coincides with NMAA (case 113) |
   | atr42_100 | GUST +C case 170, +3.44 g, 240 kt, min weight, 12,000 ft, R 67,231 | GUST −C case 173, −1.44 g, 240 kt, min weight, 12,000 ft, R 27,272 |
   | concept_regional_jet | GUST +C case 170, +3.80 g, 310 kt, min weight, 20,000 ft, R 82,102 | **empty** — coincides with NMAA (case 173) |
   | concept_heavy | **empty** — coincides with PHAA (case 3; the three 4.0 g manoeuvre points tie on `nz` and MAN A has the largest resultant) | **empty** — coincides with NMAA (case 7) |

   Resultants in lb, LIMIT, before any inertia. The Baron's PNZ sits at
   "fwd regardless", which is not derivable (§1.5), so the deck skips W-09
   there under G-62.3. The ATR's NMAA moves from
   case 128 to case 227 under the narrowing (128 belongs to NHAA now), and the
   heavy's from case 8 to case 7 for the same reason (§8); every other
   fixture's NMAA is the same point as today. V-n case numbers are the
   matrix's own and **renumber when #164 adds 12,000 ft to the GA6**; the
   gate names the point by label, load factor, speed, CG and altitude, not by
   number, so it survives that. *#164 shipped 2026-09-20: every GA6 slot
   above now governs at 12,000 ft (the gust factor grows with altitude, the
   stall speed shrinks with the compressibility correction), and the gate's
   table was re-pinned to the italic values.*
4. **G-62.3 — The deck.** On every CLI-exportable fixture the LRA deck's
   SUBCASE set gains W-07 and W-08 wherever the slot is non-empty **and**
   its CG case resolves to a derivable loading, each closing G-OR-72 and
   G-OR-73 like the six before it. Where the CG case is not derivable the
   slot appears in #284's skip record as `loading-not-derivable`, and the
   test asserts that record names it (`baron_58` W-08 at "fwd regardless",
   D-62.4). Neither slot is ever silently absent.
5. **G-62.4 — Case ids.** `tests/test_case_ids.py`: W-07…W-10 are minted
   for NHAA/NLAA/PNZ/NNZ and for nothing else; a critical set that omits
   any of them leaves the gap; the hand-authored band W-20+ is unaffected.
6. **Report.** §3.2's run register prints every non-empty new row on every
   fixture with `run = no` (D-62.7: no fixture derives its wing-case
   table), and `test_oracle_report.py`'s per-label run assertion — today an
   exact six-key dict — is extended to the slots the GA6 delivers (all
   four). `safety_factors.prescribes_factor`'s docstring counts and any
   other "six wing conditions" prose are swept in the same change.

## 5. Effect vs error bar (rule 6)

Not a fidelity item: it is a **coverage** defect on shipped content. A
down-load case for one spar is absent from every deliverable, and on the
ATR the absent case is a −1.44 g gust at the lightest wing; on the GA6 the
5.25 g and −3.25 g points, the largest load factors in the matrix, are
absent against delivered 3.96 g and −2.43 g (§1.4a). Rule 6's second
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
- **Leaves to the next note (note 63, #289):** wing mass states in the Wing Loads step —
  over the **ten** slots this note delivers (six `.BAS` + NHAA/NLAA + PNZ/NNZ) —
  named disposable-mass states on `WingMassInput`, WINGINER/NETLOADS run
  per selected case per state, the base model when none is entered. The
  air-load pick per slot stays the one balanced at SELECT's CG case; that
  a heavy pick run at zero fuel is conservative, not exact, is the caveat
  that note states.
- **Leaves parked, with its number:** a pick on **net** root bending
  instead of air resultant. Whether it would ever change a slot's point is
  measurable only once mass states exist; measured then, filed then.

## 7. Closure obligations (tier L)

`PROGRAM_SPEC.md` SELECT section + case-id rule (four slots);
`ch04_wing_loads.md` table (four rows);
`theory_sources.md` SELECT row; `CONVENTIONS.md` §case identity unchanged
(the id rule already admits gaps); one `changes/<slug>.history.md` fragment
in full step format; one Imperial digest wave (`select`, the deck, the
report register; **not** `net_loads`/`wing_inertia`/`airloads`); this note
flipped to `shipped <date>`; #164's dependency column updated.

## 8. Shipping measurements (2026-09-17, #288)

What the implementation found that the AGREED text did not say, and where
each landed. Every pick in §4's tables reproduced by name on every fixture
(G-62.1, G-62.2); the digests that moved are exactly §7's list (`select`,
`balance`, the two decks, the case index) and `net_loads`, `wing_inertia`
and `airloads` did not move on any fixture.

1. **NMAA moves on the heavy as well as the ATR.** The `.BAS`'s NMAA on
   `concept_heavy` was STALL −N (case 8, R 32,463), which is NHAA's; NMAA
   is MAN −C (case 7, R 32,367). Gate 1's "every other fixture" is corrected
   above. The heavy's PNZ coincides with PHAA, not PMAA (G-62.2's cell
   corrected).
2. **The residual gate's scale floors at 1 g** (`BalancedCaseResult.gate_load_factor`,
   `CONVENTIONS.md` §residual). The heavy's NLAA is a −0.024 g VD gust: its
   pre-closure residual against `n·W` read 31 % force / 13 % pitch, and
   0.75 % / 0.32 % against the airplane's weight — the loads the case
   actually carries. No case above 1 g moves. Owner's ruling at shipping.
3. **A forward non-wing axial force inside the trusted window, on the
   heavy's new NMAA** (alpha −9.8°, 0.2° inside the window's edge, dCD
   +0.0169). The previous NMAA point sat outside the window and clamped;
   the VC point does not, and the sign gate of
   `test_the_non_wing_drag_is_a_consistent_parasite_offset` calls it what it
   is — a fixture aero-data defect in the heavy's crude polar. Recorded with
   its number in `tests/test_balance.py::_DELTA_CD_FORWARD_INSIDE_WINDOW`,
   asserted both ways so it cannot outlive the defect; the fix is the
   fixture's polar, filed as **#291**. **Resolved 2026-09-20 (#291):** the
   cause was the polar's shape, not the point — `CD = 0.025 + 0.05·CL²` has
   its minimum at `CL = 0` on a wing whose lift fit reads `CL = 0.3` at zero
   alpha, so at negative CL it under-read the drag by the missing linear
   term. Re-entered as `CD = 0.0295 − 0.03·CL + 0.05·CL²` (same quadratic,
   minimum at the zero-alpha CL); NMAA reads dCD −0.0039, every heavy case
   inside the window is negative, the record is empty, and NHAA (outside the
   window) still clamps at 0.24 % / 0.65 %. The heavy's sixteen digest
   channels moved, `balance` through the decks, since the polar enters every
   balanced point's drag; the same picks win every slot, and §4's heavy
   resultants (G-62.2's frozen table) are re-pinned with the old values
   beside them.
4. **Ratchets and clamps re-pinned with the cause stated** (in
   `test_balance.py`): NHAA clamps on the ATR, the RJ and the heavy (stall-line
   alpha −12.8 / −18.7 / −14.3°, the point that clamped under NMAA's name
   before); the ATR's new NMAA at 25,000 ft still clamps; NLAA's force
   residual is the largest symmetric one on the GA6 (1.15 %) and the RJ
   (1.16 %) — a VD gust at small negative load factor, where the tail load is
   a larger share of the balance — inside the 2.5 % acceptance with pitch at
   a tenth of its gate; the ATR's "min weight" case assembles for the first
   time (NLAA, PNZ, NNZ all sit on it) and its closure Izz is pinned.
