# The geometry model owns the joints (design note 54)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-09 (owner); implementing on `dev/v0.8.3`.** Agreed in
chat under the solo profile (`DEVELOPMENT_PROCESS.md` §0; rule 1's
working-alone branch). **D-54.3 decided (owner: clamp + straight axis)**;
**D-54.4 decided (owner: mass-item branch)**. Drafted from the 2026-09-09
T-tail capability assessment and the approved three-phase plan; this note is
phase 1. **Shipped so far:** #223 (2026-09-09), D-54.2/#220, D-54.3/#219,
D-54.4/#261, and D-54.1/D-54.8 (#25 steps 1+2, schema v65) — all 2026-09-10;
the fixed-surface TE line of D-54.1's five is carried by the parent-TE +
control-LE pair and waits for a consumer (stated in
`changes/boundary-line-model.history.md`, owner to confirm). Remaining:
D-54.5 (joint register), D-54.6 (#260, rides the baseline wave), D-54.7
(the registry-walking drift guard).

**Tier L** (schema/contract change: the empennage boundary-line model of #25
plus a joint register). It is the design note #25's tier-L step has waited for,
and the tail-geometry cluster's rows (#223, #220, #219, #261, #260) land inside
or immediately after it in the order §3 states.

## 1. What the code does today, and what is missing

Every inter-component load transfer in the assembled models is an `RBE2`
between nodes at their true airplane-frame positions
(`sloads/export/lra_model.py`): fin root tied to the fuselage node at its own
station (R-5), the h-tail centreline tied to the fin tip on a T-tail (R-6), the
attachment pair to the fuselage otherwise, the SOB pair to the wing hub and the
hub to the two spar posts (BM-2). A rigid tie across a real offset carries the
exact lever-arm couple, so the **mechanism is statically exact by
construction** — the 2026-09-09 assessment found nothing to change in it.

What the mechanism rests on is the **node positions**, and every one of them is
*derived* by intersecting independently-entered data: fin `root_z` from the
polyline (L-1), the h-tail waterline from `tail_geometry.h_tail_waterline`
(#236), the fuselage beam from `fuselage_lra`, the spar posts from
`carry_through` — ASSUMED at %-of-root-chord on **all six** shipped fixtures,
as is the SOB. Nothing checks that these separately-resolved quantities
describe the *same joint*, and nothing states the offset arms the ties span.
The open defects on the record are all instances of that one hole:

- **#261** — the conventional h-tail fallback returns the wing-root plane:
  `cessna_210`'s h-tail sits at WL 86.0 ASSUMED, ~14 in below the surface the
  three-view draws, and the placeholder is printed as an airplane coordinate in
  Appendix D and the deck `GRID`s.
- **#260 E5** — `atr42_100` declares `t_tail` with `h_tail_z = 0.0`. The
  T-tail branch happens to outrank the entered value, so the resolution is
  right *by branch order*, and nothing says the entered field contradicts the
  relation and is not used. E4 is the same class on the fin span
  (967.2 typed vs 968 drawn).
- **#219** — `resolve_tail_planform` rebases GA6's raked fin root onto one
  waterline and the LRA swings aft at the root.
- **#220** — the plane a surface is defined in is positional, not declared;
  `XYPoint`'s documented "butt line Y" is false for the fin.
- **Unstated tip-joint arms** — on the three T-tail fixtures the fin-tip LRA
  point and the h-tail centreline LRA point are **25.6 / 26.1 / 26.7 in apart
  in x** (`atr42_100` / `dhc8_dash8` / `concept_regional_jet`): a real rigid
  arm the R-6 tie spans, implied by two planforms and validated by nothing.
  Note 51's transfer moments (D-51.2/D-51.3) are computed from exactly these
  arms.
- **#25** — boundaries that are physically one line are entered several times
  with nothing checking the copies agree.

One statement covers all of them: **a joint between two components must be a
first-class geometric entity — an owned location, stated offset arms, a DOF
set and a basis — not an emergent coincidence of separately-entered surfaces**
(CLAUDE.md rule 3; `CONVENTIONS.md` §7's SSOT discipline applied to
positions).

## 2. Governing basis

This is a geometry-contract note, not a physics note: no FAR condition and no
oracle changes. The authorities it builds on:

- `CONVENTIONS.md` §1 (axes; `export/coordinates.py` the single edit point for
  every axis resolution) and §7 (single-source owners, rule 2: one surface is
  placed once).
- Plan 09 T-1/T-8/T-8a (the `SurfaceInput` reuse, the attachment owner with a
  named basis) and note 18 §5.1 L-1 (the fin-root owner and its resolution
  order) — the pattern this note extends from *placement of a surface* to
  *placement of a joint*.
- Note 24 (the LRA beam model: R-5/R-6 ties, BM-2 posts) — the consumer whose
  node positions become reads of the joint register.
- #25's backlog body — the boundary-line model this note carries as its
  entered-geometry layer.
- Appendix A stays a tolerance oracle for every derived scalar the boundary
  model begins predicting (elevator/stabilizer/rudder areas, ±0.1 %,
  page-cited) — the one place a printed oracle does gate this note.

**Baseline invariance is the acceptance frame:** on fixtures whose entered
data already resolves correctly, this note moves **no** load and no `GRID`;
where a position moves (the #261 fallback, the #260 fixture pass), the move is
itself the stated, gated fix.

## 3. Decisions proposed

| # | Decision | Alternative rejected |
|---|----------|----------------------|
| D-54.1 | **The boundary-line model (#25 step 2):** five independently entered lines per tail group (tail LE, tail TE, fixed-surface TE, control hinge, control LE); the control's TE is the parent's along the interior of its span with an end-closure point where it departs. `wing_geometry.surface_properties` derives every area, span, MAC, MAC station and AR the h-tail/v-tail input blocks carry today as hand-entered scalars (9 of 17 and 9 of 15 fields); control travels and setting angles stay. #25 step 1 (group and mark the derived fields, tier M) lands first. Appendix A's printed elevator/stabilizer/rudder figures become **predictions** (±0.1 %, page-cited) | Keeping the scalars entered with a validator per pair — that is today's shape, and it is exactly what lets one surface be described twice, differently (#25's opening sentence) |
| D-54.2 | **`surface_plane(component)` owner (#220):** one authority for the plane each surface spans (fin in z), replacing the five name-test branches; docstrings corrected. **No** user-selected plane field yet — it belongs with V-tail/cruciform support, deferred §8. Lands after the #223 `fin_*`→`vtail_*` rename, which goes first in the cluster (owner ruling 2026-09-06, `CONVENTIONS.md` §7.2) | A per-call-site convention — the five branches are the drift this note exists to end |
| D-54.3 | **The LRA is defined on the resolved planform with the raked-root ruling made explicit (#219).** Decided (owner, 2026-09-09): below the span where both edges exist, the chord stays clamped (today's `planform_boundary` rule, which the GA6 area defect already justified) and the **axis continues on its last defined slope** rather than being re-evaluated on the clamped chord — the kink is an artifact of pointwise evaluation, not of the surface. Square-root fins are byte-unchanged | Extrapolating the short edge (the 8 % area over-read the clamp was written against); refusing the raked root (refuses `ga6_normal`, a shipped oracle fixture) |
| D-54.4 | **The h-tail waterline owner is completed (#261).** The T-tail (fin-tip) and cruciform (mid-fin) branches stand. Conventional order, decided (owner, 2026-09-09): `h_tail_z` entered → h-tail **mass item's `z`** (ASSUMED, basis `mass-item`) → wing-root plane with the loud note (today's fallback, now last). Plus the **two-spellings rule** from the fin-root owner applied here: a declared T-tail with an entered `h_tail_z` whose implied waterline disagrees with the fin tip by more than `PLANFORM_TOLERANCE` of the fin span gets the fin tip *and an in-band note naming the entered value as NOT USED* (the #260 E5 pattern made loud). Swept per rule 4, guarded on both conventional fixtures | Requiring `h_tail_z` (refuses two shipped fixtures); leaving the wing-root fallback silent (the 2026-09-08 R12 finding — the placeholder printed as an airplane coordinate) |
| D-54.5 | **The joint register:** one resolution owner (proposed `sloads/joints.py`, or a `geometry` submodule — final home decided at AGREED) producing, per project, the typed set: `fin_root→fuselage` (station + vertical arm to the fuselage LRA), `fin_tip↔htail_centreline` (T-tail; the x-offset between the two LRA endpoints), `htail_attach` pair (conventional; adopts `htail_attachment`'s basis), `wing_sob` + `wing_spar_posts` (adopts `carry_through`; entered `front/rear_spar_x_in` promoted from ASSUMED where the fixture pass enters them). Each joint carries location, offset arms, DOF set and basis, with the ASSUMED/entered provenance grades the suite already uses. `lra_model.py`'s node placement and `tail_span`/T7's lever arms become **reads of the register** (phase 2 of the plan); this note ships the register and its guards | New entered override fields per joint — deferred (§8) until a fixture needs one; the register's value is validation and single ownership, not more inputs |
| D-54.6 | **Fixture reconciliation:** `atr42_100` end-to-end from published ATR 42-300 data (#260 — planform area, wing items, fuselage stations, the E4/E5 tail entries), the same sweep on `dhc8_dash8`, and entered spar stations where the airplane's data states them — so the register's closure numbers exercise true arms and the ASSUMED count drops on the record. Baselines move; rides the baseline wave with #261 as the backlog already sequences | Leaving the fixtures as-is and gating on them anyway — gates pinned to wrong geometry certify the wrong airplane |
| D-54.7 | **The drift guard (rule 3):** one registry-walking test — for every joint on every fixture, the exported tie-node positions equal the register's location, the tie's offset arms equal the stated arms, and the tie exists. Exact (`rel_tol=1e-9`): positions are copies of one owner, not measurements | Per-defect regression tests — #261, #219 and #260 E5 were each invisible to the tests beside them; the class needs one guard, not three |
| D-54.8 | **Stabilizer dihedral becomes a declared field now, physics still deferred** (#25's own ruling — deferred as unexercised, *not* a rule-6 park). The field exists so note 51's D-51.3 guard ("refuse or warn on appreciable T-tail dihedral", AC 23-9 ¶4b) has something to read — the real ATR 42 and Dash 8 both carry visible tailplane dihedral, and a guard with no input is a guard that never fires | Adding the field with the induced-moment correction — no method adopted (AC 23-9 gives none; DATCOM carryover is note 51's stated upgrade path) |

## 4. Gates (the closure targets, with expected numbers)

All identities against the owners (`rel_tol=1e-9` unless stated); the
boundary-model scalars gate against Appendix A at ±0.1 % where printed.

1. **Fin-root joint:** register location equals the L-1 owner's resolution on
   every fixture — `ga6_normal` **111.5** (geometry), `baron_58` **110.0**,
   `cessna_210` **100.2**, `atr42_100` **191.2**, `dhc8_dash8` **203.5**,
   `concept_regional_jet` **87.0** — and the LRA-model fin-root node sits on
   it, with the vertical arm to the fuselage-LRA node stated.
2. **T-tail tip joint:** register waterline equals fin root + fin span —
   `atr42_100` **316.2**, `dhc8_dash8` **333.5**, `concept_regional_jet`
   **225.0** — equals `h_tail_waterline`'s fin-tip branch, **and the stated
   x-arm equals the measured LRA offset**: **−25.6 / −26.1 / −26.7 in**
   (h-tail centreline LRA forward of the fin-tip LRA). The R-6 tie spans
   exactly that arm.
3. **Conventional attachment joint:** register pair equals `htail_attachment`
   with its basis — `ga6_normal` ±6.7, `baron_58` ±4.6, `cessna_210`
   ±10.9 in (fuselage outline at the h-tail LRA station, ASSUMED) — and the
   D-54.4 waterline: `ga6_normal` **111.0** (entered) unchanged; `cessna_210`
   moves off **86.0**/wing-root to the mass-item branch (expected value pinned
   at implementation from the fixture's item table, the move itself the gated
   fix).
4. **Wing joints:** register SOB and post stations equal `sob_station` /
   `carry_through` per fixture; the ASSUMED grade survives into the register
   and every deliverable note; where D-54.6 enters spar stations the grade
   flips to entered and the note disappears — both directions asserted.
5. **#219:** the GA6 fin LRA has no slope discontinuity at the root
   (monotone station-to-station axis direction through the rebased region);
   square-root fins byte-identical.
6. **#260 E4/E5:** the reconciled `atr42_100` loads with zero override
   warnings; a constructed declared-T-tail-with-contradicting-`h_tail_z`
   project produces the D-54.4 NOT-USED note (asserted verbatim class, like
   the fin-root two-spellings note).
7. **Boundary-model scalars:** each derived area/span/MAC equals its Appendix A
   printed figure within ±0.1 % (page cited per figure) on the oracle
   fixtures; `validate_tail_planform`'s scalar-vs-polyline comparison retires
   where the scalar is no longer entered.
8. **Baseline invariance:** on fixtures untouched by D-54.4/D-54.6, every
   delivered load and every exported `GRID` byte-identical before/after the
   register lands.
9. Doc-currency, schema (additive, v-next), `DATA_DICTIONARY.md` regenerated
   via the generator.

## 5. Effect vs error bar (rule 6)

Geometry rows are arm errors, so their effect is stated on the moments the
arms make (band ±5–10 %, `theory_sources.md` §Base-method uncertainty):

| Item | Effect | Verdict |
|---|---|---|
| Unstated T-tail tip-joint x-arm (D-54.5 gate 2) | ~26 in on all three T-tail fixtures. Note 51's `HTAIL UNSYM` tip set (RJ `lt25` 3,840.9 / `lt50` 8,312.8 lb) crosses this arm: ~100 k lb-in-class `Myy` content whose lever nothing validates today — the gate that must exist **before** D-51.2's numbers are certified | **Ranks** — enabling-defect class for note 51 |
| #261 conventional fallback | No delivered load (the h-tail loads in `fz` only) but Appendix D and the deck `GRID`s publish the placeholder as an airplane coordinate — `cessna_210` ~14 in low today, the GA6 was 32.5 in low until its `h_tail_z` was entered | **Ranks** — shipped-content defect (R12), not a fidelity item |
| Spar posts ASSUMED on 6/6 fixtures | Sets where wing root load enters the fuselage bays; global equilibrium closes either way, the bay-level introduction does not | **Ranks with D-54.6** — resolved by entering data, not by method |
| #219 root kink | Localized axis direction error at one station on one fixture | Rides D-54.3 — defect-class, no separate rank needed |
| Dihedral (D-54.8) | Field only; the physics stays deferred — AC 23-9's own warning (¶4b, ~+50 % on M_r at 6°) is the number that will promote it when a fixture declares one | Deferred, not parked — #25's ruling stands |

## 6. What this supersedes / corrects

- `h_tail_waterline`'s wing-root fallback demoted to last with its note kept
  loud (#261); the #236 owner otherwise stands.
- `resolve_tail_planform`'s raked-root behavior made a stated decision
  (D-54.3) instead of an artifact (#219).
- The five surface-plane name-tests replaced by the D-54.2 owner (#220).
- `validate_tail_planform`'s scalar-vs-polyline drift guard retires
  field-by-field as D-54.1 stops entering the scalars it compares.
- The frozen-list entries this note touches (the LRA beam model at its
  determinate paths) gain a pointer here as the scoped reopening — node
  *placement* only; the tie topology and the determinate-path posture are
  untouched.

## 7. Closure obligations (tier L)

`PROGRAM_SPEC.md` geometry/tail-span/export sections; `PROJECT_GUIDE.md`
`Project` schema; `CONVENTIONS.md` §7 gains the joint-register row (owner +
drift guard); `theory_sources.md` needs no new physics row — the Appendix A
citations move onto the derived scalars' gate; `DATA_DICTIONARY.md`
regenerated; history fragment in full step format; changes fragments; #223's
rename note travels ahead of this note's code per the backlog sequencing.

## 8. Deferred (each with the condition that promotes it)

- **Entered per-joint override fields** — when a real airplane's joint is not
  where the register derives it (e.g. a bullhorn-mounted stabilizer whose
  pivot is off the LRA); the register's basis grades are built to receive
  them.
- **User-selected surface plane** — with V-tail/cruciform support (#220's own
  ruling; the V-tail pass is parked to OR-11).
- **The stiffness carry-through (step 14 / R-12)** — the fore/aft split of the
  wing root moment between the posts is a stiffness question; this note owns
  only *where* the posts are.
- **Dihedral physics** — promoted when a fixture declares a dihedral and
  note 51's guard fires (D-54.8).
- **`body_loads`' T-tail entry point** (the tail load into the component
  fuselage view at the fin-root joint) — phase 2 of the approved plan,
  consuming this note's register; filed there, not here.
- **Cruciform mid-fin joint loads** — the register places it (the mid-fin
  branch exists); a cruciform load path waits for a cruciform fixture with a
  consumer.
