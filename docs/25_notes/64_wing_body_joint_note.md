# The wing-to-body joint: one post, two body cantilevers, and nothing integrated through the box (design note 64)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: SHIPPED 2026-09-21** (PROPOSED, AGREED and shipped the same day —
owner, in session, under the solo profile, `DEVELOPMENT_PROCESS.md` §0; rule
1's working-alone branch; the three questions of §8 are **ruled** there and
written into D-64.5, D-64.6 and §7; **§7b** is the implementation record,
including the re-measured Appendix G table and the two in-code amendments). Filed against **#275** (band B7, 0.8.6), which this
note **re-cuts**: the row's stated resolution — own the carry-through stations
in the fuselage mesh — is withdrawn in §2 and replaced by the joint
idealisation below. The owner's rulings of 2026-09-21 are §2; the
measurements that prompted them are §1.

**Tier L.** A change to the assembled model's load path (the rigid centre-box
hub and the two spar posts of note 24 BM-2/R-12 become one vertical post and
a beam through the box), a change to what the Ch 15 body-loads module
publishes (two cantilevers, a stated sign, no integration through the box,
M4-1's linear smear retired), and a new convention in `CONVENTIONS.md`. No
oracle moves (§4 gate 8): AIRLOADS/WINGINER/SELECT are untouched, and Ch 15
ships no printed table (`theory_sources.md`, the `body_loads` row).

**Conventions:** `CONVENTIONS.md` (axes and signs; §7 SSOT table — this note
adds one row, the body cantilever sign; the seam rule "the fuselage beam
carries everything except the wing"). **Theory:** Ref 1 Ch 15 p103 (the
unbalanced moment reacted at the wing attachments), note 24 R-3/R-4/R-11/R-12
and BM-2 (the joint as shipped), note 04 (M4-1, the closure and the smear),
note 50 (the spar stations are entered fuselage stations), note 54 D-54.5
(joints are placed by the register), note 55 D-55.1/D-55.6 (rigid-tie and
support rules), note 56 D-56.4/D-56.10 and §7b finding 3 (the mesh, the
lumping comparison, and the measurement that opened #275).

---

## 1. Measurements (2026-09-20/21, at `dev/v0.8.6` after #222)

### 1.1 What the 183 % was

Appendix G's fuselage comparison is defined as *"the resultant of everything
aft of a station, whichever side of the carry-through it falls on"*
(`report/lumping.py`, `_MEMBERS`). Every fuselage cut is therefore a
nose-to-tail cumulative that passes **through** the box. Body loads places the
wing reaction as M4-1's linear line load lumped onto five stations across
`[x_f, x_r]` (`CARRY_THROUGH_NODES`); the mesh owns only the two posts and, by
BM-2, has no element between them; so the three interior stations route to the
nearer post and cross that post's cut on the way.

| Fixture | Worst fuselage shear deviation, shipped | Where | What moved |
|---|---|---|---|
| `concept_regional_jet` | **183 %** of a 45,878 lb peak (83,887 lb) | rear post, FS 567 | the carry station at FS 552.5 (83,887 lb) moved 14.5 in aft onto the post |
| `baron_58` | 111 % | rear post | the same shape |
| `ga6_normal` | 48 % | rear post | mass stations ahead of a node landing on it |
| `atr42_100` | 43 % | FS 347.9 | mass stations ahead of a node; **two errors cancel at its rear post** — a 19,280 lb carry station and a 12,771 lb mass station 1.9 in ahead of the post move onto it in opposite signs |

The row's number was the concept jet's, and the mesh was never the defect:
the *integration* ran through a region that is not a beam.

### 1.2 The wing shows the same artifact

The worst wing shear deviation is at the **side-of-body cut on all four
loaded fixtures** (GA6 19 %, Baron 30 %, ATR 29 %, jet 29 %). The strips
inboard of the SOB land on the SOB node (note 24 R-3's collapse) and the
comparison counts them there, while its station curve — and the deck's own
SOB statement, `applied.sob_internal_loads` — exclude them. The comparison is
the odd one out.

### 1.3 The joint geometry the rulings assume, per fixture

"Straight across" (§2 ruling 3) puts the wing station at the SOB's own
fuselage station. It lies between the spars on every fixture that builds a
model; `concept_heavy` refuses upstream (no resolvable SOB) and is unchanged.

| Fixture | front spar `x_f` | wing station (SOB `x`) | rear spar `x_r` | wing LRA at BL 0 (for contrast) | post height (body beam `z` − wing `z` at the station) |
|---|---|---|---|---|---|
| `ga6_normal` | 65.2 | **89.8** | 105.6 | 85.4 | ~7 in |
| `baron_58` | 78.8 | **95.0** | 112.4 | 95.6 | ~8 in |
| `atr42_100` | 384.0 | **403.7** | 422.0 | 403.0 | ~6 in |
| `concept_regional_jet` | 509.0 | **559.2** | 567.0 | 538.0 | ~5.5 in |

On the swept jet the straight-across segment sits 21 in aft of the LRA's own
BL 0 point. That is the rule's choice, made on purpose (§3 D-64.3), and the
inboard strips' lever-arm couples carry the difference exactly (LM-1).

### 1.4 What is already as ruled

The deck already builds the two body cantilevers and starts the wing at the
SOB. `roundtrip._supportable` and the support picker already keep the clamp
off every rigid tie. The SOB closed form already excludes inboard strips. The
mass model is grids at each item's own CG, unconnected (D-56.6), and is not
touched by anything here.

---

## 2. Owner rulings (2026-09-21, in chat)

1. **The fuselage LRA between the two spars is not a valid beam region.** The
   incremental (applied) loads in that region are calculated and stated; the
   fuselage integration runs **nose → front spar** and **tail → rear spar**.
   The wing integrates **tip → side of body**. *(This withdraws #275's
   resolution: no load station is added to the mesh; the integrations that ran
   through the box are corrected instead — which is also what note 56 §7b
   finding 3 asked for when it refused to change the mesh to improve its own
   measurement.)*
2. **The fuselage beam has a grid at the front spar, at the rear spar, and at
   the wing station on the centreline**, and a beam continues from the front
   spar to the wing post to the rear spar (its internal loads in the box not
   reported).
3. **The wing LRA has a grid at the side of body and extends to the
   centreline straight across**, at the SOB's own fuselage station and
   waterline. The wing station lies **between the two spars**.
4. **A vertical post connects the wing to the fuselage**, rigid, at the wing
   station.
5. **Fuselage vertical shear and bending are positive for up loads in either
   body**, so a 2.5 g manoeuvre produces down (negative) bending in both the
   forward and the aft fuselage.
6. **No oracle exists for the wing reaction on the body** (Ch 15 prints no
   station table; the fitting pair is M4-1's own solve), so the reaction is
   stated at **one wing station**.
7. **The oracle-locked wing tables are untouched.** "Integrated to the side of
   body" applies to the LRA deliverables — the deck, the SOB statement,
   Appendix G — not to AIRLOADS/WINGINER's cumulative tables, which run to the
   centreline as printed.

---

## 3. Decisions

| Decision | Ruling | Alternatives considered |
|---|---|---|
| **D-64.1** | **One post, one tree.** The rigid centre-box hub and its four ties (hub → SOB R, hub → SOB L, hub → front post, hub → rear post) retire. The fuselage is **one chain nose → tail** with owned points at `x_f`, the wing station `x_w` and `x_r`; the two box elements `x_f→x_w→x_r` carry no intermediate grid (the box is owned points only — it is a load path, not a member being analysed). The wing is **one chain tip → SOB → BL 0 → SOB → tip**, the inboard segments straight across (D-64.3), likewise with no intermediate grid. **Exactly one `RBE2`** joins them: the fuselage grid at `x_w` independent, the wing BL 0 grid dependent, all six DOF. The model stays a tree — one body, one wing, one connection — so it stays statically determinate under rigid ties, which was R-12's whole reason for the split-fuselage default; R-12's objection was to a continuous fuselage on **two** posts, and this has one. | *Keep the hub and add box nodes as hub dependents* (the #275 row): puts load stations into a mesh that is load-blind by design (D-56.4) and leaves a rigid region pretending to be a beam. *Two posts (a rigid link at each spar)*: indeterminate under placeholder stiffness — R-12's rejected case, still rejected. *A stiffness carry-through element*: step 14's, needs a section the project does not carry. |
| **D-64.2** | **The body is integrated as two cantilevers and nothing is integrated through the box.** `body_loads` publishes the forward body from the nose to `x_f` and the aft body from the tail to `x_r`, each from its free end toward its spar. A station inside `[x_f, x_r]` — a mass item, the wing reaction — is published as an **applied** row and belongs to neither integration; the station table prints no running shear or moment for it. The forward table is numerically what it is today; the aft table changes sign (D-64.4); the box goes blank. | *Keep the nose-to-tail cumulative and blank only the box*: leaves the aft body with the sign of the forward body's closure rather than its own cantilever's, which is the confusion ruling 5 removes. |
| **D-64.3** | **Straight across.** The wing's inboard segment runs from the SOB joint to BL 0 at the SOB's fuselage station and waterline, `(x_sob, 0, z_sob)`; that point **is the wing station** `x_w`, and the fuselage grid at `x_w` is `(x_w, 0, z_body(x_w))` on the body's own LRA. The post is the vertical between them. The joint register owns both points (D-54.5): `WING_SOB`'s counterpart becomes the straight-across BL 0 point, `WING_SPAR_POST` keeps the two spar stations, and a new `WING_POST` names the fuselage end. **Refusal:** `x_w` outside `[x_f, x_r]` is an `LraRefusal` naming the three stations, on the same footing as an SOB outboard of the tip. | *Extrapolate the LRA to BL 0*: on a swept wing this puts the wing station 21 in from where the SOB joint is (jet: 538 vs 559), and the strips inboard of the SOB are not on the LRA anyway. Rejected by ruling 3. *Refuse when `x_w` differs from the LRA's BL 0 point*: a swept wing is not an error. |
| **D-64.4** | **Body cantilever sign, single-sourced.** In either body, shear and bending are **positive for an up load**: forward body `V(x) = Σ_{x_i < x} fz_i`, `M(x) = Σ_{x_i < x} fz_i (x − x_i)`; aft body `V(x) = Σ_{x_i > x} fz_i`, `M(x) = Σ_{x_i > x} fz_i (x_i − x)`. A positive-`nz` inertia set therefore gives negative bending in both bodies. Owner: `modules/body_loads.py` (the integrator), with the rule stated once and read by Appendix G's fuselage curves; a `CONVENTIONS.md` §7 row names it and its guard. | *Keep the nose-to-tail sign aft of the box*: rejected by ruling 5. *Put the sign rule in prose only*: rule 3 says no. |
| **D-64.5** | **The wing reaction on the body is one load at the wing station.** `body_loads` closes the free body by the resultant `R = −Σ fz` and the couple `M_w = −Σ fz_i (x_i − x_w)` of everything on the body (mass stations, tail load), applied at `x_w` — exactly what the post carries. **M4-1's linear smear retires** with `CARRY_THROUGH_NODES`, `_linear_load_nodes` and the `"carry"` station family: it existed to smooth a region ruling 1 says is not a beam. The reaction is exact by construction at any mesh, so no node-count or `d → 0` gate is needed. **The `closure_artifact` fallback retires with it** (§8 ruling 1): the reaction is physically sourced, so the whole-body correction has no job left, and a project whose wing station cannot be placed is refused by name — `body_loads` states it as the exporter already does — rather than closed by a correction with no source. `CLOSURE_ARTIFACT_CAVEAT`, the `"correction"` station family and the `closure_artifact` flag go with it. The Ch 15 **fitting pair** stays as a reported quantity: `R_f`, `R_r` are the static equivalent of `(R, M_w)` at the two spars (`R_r = (M_w + R (x_w − x_f))/d`, `R_f = R − R_r`), the same 2×2 as today with the moment taken about the wing station; section 4.4 keeps printing them, provenance and grade unchanged. | *Apply the two fitting loads on the beam* (the manual's literal form): two point loads across a region with no beam, and the deck's post carries one resultant anyway. *Retire 4.4*: the fitting designer still needs the pair; it is a statement, not a load path. |
| **D-64.6** | **Appendix G integrates as the deck does.** The fuselage comparison becomes two cantilevers with D-64.4's sign, cuts nose → `x_f` and tail → `x_r`, and **no cut inside the box**. The wing comparison's cuts run tip → SOB. A load that lands on a **root node** (the SOB grid, either post grid) belongs to the box: it is excluded from that root's cut in both curves, because the element outboard of the root — what the roundtrip gate measures — never sees it. `_AT_THE_CUT`'s "a load at the cut counts as outboard" stays for every interior cut. A body-loads station **exactly at** `x_f` or `x_r` follows the root rule (§8 ruling 2): it is published as a box row and enters neither cantilever. Ruling 15 of note 56 stands: the deviation is stated, not bounded. | *Leave the comparison nose-to-tail*: it is what produced a 183 % number for a mesh that was right. *Bound it now that the artifact is gone*: still a function of the user's grid count; a number nobody has agreed. |
| **D-64.7** | **The SOB closed form keeps its value and gains its words.** `sob_internal_loads` already excludes inboard strips; it now states that a load on the SOB grid is the box's, matching D-64.6 and the roundtrip cut, so the two ways of stating the SOB load (R-3) cannot disagree about the node itself. Inboard strips land on the inboard segment's nearest grid (SOB or BL 0) with the exact couple, never on the fuselage. | *Count on-node loads as outboard* (the docstring's present wording): contradicts the element the solver reports. |
| **D-64.8** | **Ties and the support are unchanged in rule.** A body tie inside the box parents on the nearest **free** box grid (D-55.1 — `x_w` is independent in the post's `RBE2` and may parent; the wing BL 0 grid is dependent and may not). The clamp stays the forward-chain grid nearest the front post that is in no `RBE2` (D-55.6). `tie_xs`' exclusion of the box retires with the box's non-existence. | — |
| **D-64.9** | **The mesh counts are unchanged**: `lra_mesh.fuselage` still means grids per body cantilever between its owned points; the box and the wing's inboard segments take none. No schema hop. | *Add a box count*: a knob for a region that reports nothing. |

---

## 4. Gates (benchmark-first; every one on every CLI-exportable fixture)

1. **Topology.** The fuselage member is one chain nose → tail through `x_f`,
   `x_w`, `x_r`; the wing member is one chain tip → tip through BL 0; the deck
   carries **exactly one** `RBE2` between them, wing-side dependent; the
   element graph is a tree. `test_the_split_fuselage_has_no_element_through_the_carry_through`
   and `test_the_wing_chain_starts_at_the_sob_and_inboard_strips_collapse_there`
   invert into this gate.
2. **Free-free solve** — `test_the_lra_model_solves_and_reacts_only_the_residual`,
   unchanged in form, both unit systems.
3. **Cut-side sums at four cuts** —
   `test_the_lra_named_node_internal_loads_are_the_cut_side_sums` extended from
   the SOB and the front post to **the rear post and the post itself**: the
   `RBE2`'s transmitted force equals the resultant of everything on the wing
   side, i.e. the wing reaction on the body, and the two box elements either
   side of `x_w` carry the forward and aft cantilever sums respectively.
4. **Body closure, two cantilevers.** Per condition: the forward table's
   terminal `(V, M)` at `x_f` equals the forward set's resultant and moment;
   the aft table's at `x_r` likewise; the two terminals, the box's applied rows
   and the reaction `(R, M_w)` at `x_w` sum to zero force and zero moment to
   1e-9 of `nz·W·MAC`. Replaces `test_body_net_closes_in_equilibrium`'s
   terminal-zero form. `test_closure_is_independent_of_the_carry_through_node_count`
   and `test_carry_through_collapses_onto_the_two_point_solve_as_d_shrinks`
   retire with the smear (their subject no longer exists).
5. **Sign.** A pure-inertia positive-`nz` case has `M < 0` at every interior
   station of **both** bodies (ruling 5 as a test), and the owner's
   `CONVENTIONS.md` §7 row names this test.
6. **The fitting pair is the static equivalent of the one reaction** —
   `test_spar_reactions_carry_the_unbalanced_moment` re-targeted: `R_f + R_r = R`
   and their moment about `x_w` equals `M_w`.
7. **Appendix G.** The fuselage comparison has no cut inside `[x_f, x_r]`; no
   `"carry"` row exists to lump; the wing curve's root cut excludes on-node
   loads in both curves. The re-measured worst deviations are **printed in
   §7b at implementation** for the four fixtures (expected: the fuselage falls
   to its mass-station crossing, the wing's SOB term to zero). No tolerance
   (note 56 ruling 15). `test_every_surface_states_what_its_lumping_cost` and
   `test_the_station_curve_at_the_root_is_the_side_of_body_owner` hold.
8. **The oracle does not move.** AIRLOADS/WINGINER/SELECT digest channels are
   byte-identical; `tests/test_select.py` and every Appendix A test pass
   unchanged. **Channels that move, stated:** `csv/body_loads`,
   `txt/body_loads` (aft sign, box blank, carry rows gone), the fuselage
   applied set (`*_fuselage_applied*`, one reaction row replaces five), the
   LRA deck, and the report's Appendix C.2/G. Nothing else.
9. **Refusal by name.** A project whose wing station is outside its spars is
   refused with the three stations in the message; mutation-tested by moving
   a fixture's spar.
10. **Joint register.** `tests/test_joints.py`'s walk passes with the new
    `WING_POST` and the re-pointed `WING_SOB` counterpart; every tie end is a
    copy of a register location (D-54.5).
11. **Doc currency.** `tests/test_doc_currency.py` passes, its citation guard
    included: the new `CONVENTIONS.md` §7 row names gate 5's test by its real
    name, so a renamed guard fails the standard rather than the note.

---

## 5. Effect vs error bar (rule 6)

This is a **defect with first-order effect on shipped content**, which
outranks every fidelity item: Appendix G tells a reader that the fuselage
lumping costs up to 183 % of the peak shear on the concept jet and 111 % on
the Baron, and the number is an artifact of integrating through a region the
model has no beam in. The corrected statement is the mass-station crossing
alone. The body-loads table's aft sign and the blank box are presentation of
the same physics, and the deck's forward-post internal load is unchanged
(gate 3). The joint change moves no delivered load resultant (gate 2, gate 8).

---

## 6. What this supersedes, and what it leaves

- **Note 24 R-3** (the wing beam *starts* at the SOB): amended — it starts at
  the SOB **as a member for integration** and continues to BL 0 as structure.
  **R-4**'s posts as rigid links to the SOB nodes and **BM-2**'s "no element
  spans the carry-through": superseded by D-64.1. **R-12** stands in its
  reasoning and is satisfied: one post keeps the model a tree.
- **Note 04 / M4-1:** the closure survives (both DOF, exact); the linear smear,
  its constant and its two gates retire (D-64.5). The fitting pair survives as
  a report quantity.
- **Note 50:** unchanged — the spar stations are entered fuselage stations and
  they now bound the box and are two of its three grids.
- **Note 55 D-55.1/D-55.6:** unchanged in rule; one dependent grid instead of
  four to keep clear of.
- **Note 56 D-56.4:** unchanged — the mesh stays load-blind; the box and the
  inboard wing segments are owned points with no intermediates (D-64.9).
  **D-56.10** stands; its fuselage definition is corrected by D-64.6. **§7b
  finding 3** is closed by this note, and its instinct (do not touch the mesh)
  was right.
- **Note 56 gate 10** (`test_the_lra_mesh_is_load_blind`) holds and now also
  covers the box.
- **#275**'s row: retitled to this note's subject, tier **L**, dependency
  "note 64 at AGREED". **#283** (the beam-model page) draws the model this note
  changes; it stays after this.
- **Left alone:** the mass model (D-56.6), the tail ties, gear and engine ties,
  the support picker, the import path (`lra_import` maps by family and tag;
  the new `lra-wing-centre` and `lra-post W` tags are added to the family
  list), and every oracle table.

---

## 7. Closure obligations (tier L)

1. `PROGRAM_SPEC.md`: the `body_loads` **Writes/Validation** bullets (two
   cantilevers, the sign, the one-station reaction, the fitting pair as a
   statement, the smear gone) and the LRA section's joint paragraph (one post,
   the box beam, the wing to BL 0, the refusal).
2. `CONVENTIONS.md`: the body cantilever sign as a §7 row with owner and guard;
   the seam rule's wording ("enters as the carry-through *reaction*") kept.
3. `theory_sources.md`: the `body_loads` row (Ch 15 p103 — the two-pass
   method kept, the reaction stated at the wing station, the smear struck with
   its date) and the `export/lra_model` row's topology sentence.
4. `ch06_body_loads.md`: the method steps 3–4 rewritten to the two cantilevers.
5. `changes/wing-body-joint.history.md` in full step format; this note flipped
   to SHIPPED with §7b (implementation record, including the re-measured
   Appendix G table and any in-code amendment).
6. The `closure_artifact` caveat's three consumers — the `$ CAVEAT:` header
   lines, the Net Fuselage Loads page warning and the Export page caption —
   removed with the path (D-64.5), and `PROGRAM_SPEC.md`'s sentence about
   them struck.
7. Digests regenerated for the stated channels only (gate 8); the backlog row
   removed; #275 closed by `scripts/solo_close.sh`.

---

## 8. Rulings taken at AGREED (owner, 2026-09-21, in chat)

1. **The no-carry-through fallback retires.** Under D-64.5 the reaction at the
   wing station closes both DOF with a physical source, so the flagged
   whole-body correction (`closure_artifact`) has nothing left to close; a
   project with no planform has no wing station either, and `body_loads`
   refuses by name — the exporter's existing behaviour, now shared. Written
   into D-64.5 and §7 item 6.
2. **A mass station exactly at a spar is the box's.** It is published as a box
   row and enters neither cantilever, the same rule as a load on a root grid.
   Written into D-64.6.
3. **This note carries no image.** The existing-vs-proposed joint drawing made
   for the discussion (drawn from the real `concept_regional_jet` model) stays
   out of the tree; the shipped drawing is `scripts/plot_lra_model.py`'s,
   which #283 promotes to the beam-model page and which will show the joint
   as this note leaves it.

---

## 7b. Implementation record (#275, shipped 2026-09-21)

**What landed, against the gates.** The joint register (`sloads/joints.py`)
states the four joints of D-64.1/D-64.3 and what spans each arm
(`Joint.element`: the wing post `RBE2`, the SOB and spar arms `CBAR`), refuses
a wing station outside its spars by name, and owns the wing station for the
calc (`wing_station`). `export/lra_model.py` builds the wing chain tip → SOB →
centre (straight across) → SOB → tip, the fuselage chain nose → front spar →
wing station → rear spar → tail with the box as three owned grids, one `RBE2`
(fuselage `lra-post W` independent, wing `lra-centre C` dependent), and states
each member's box on `LraModel.boxes`; the clamp lands on the front-spar grid,
which is in no `RBE2` now. `modules/body_loads.py` integrates two cantilevers
from their free ends (`_cantilever`), closes the free body with one reaction
`(R, M_w)` at the wing station, reports the fitting pair as its static
equivalent, publishes every station's `region` and the reaction row's
`couple`, owns the sign (`cantilever_sign`) and the closure
(`closure_residuals`), and refuses an unplaceable post with the register's
sentence; `CARRY_THROUGH_NODES`, `_linear_load_nodes`, the `"carry"` and
`"correction"` station families, `closure_artifact` and
`CLOSURE_ARTIFACT_CAVEAT` are gone. `report/lumping.py` reads the box and the
sign (D-64.6); `report/applied.py` carries the reaction's couple as the row's
`My` and skips the spar rows; the report's 4.3 method paragraph, 4.4 closure
sentence, Appendix C.2 (a `Region` column, blank running loads on box rows)
and the methods block state the new statement. Gates 1–11 are
`test_the_box_is_two_elements_through_the_wing_station_and_one_post`,
`test_the_lra_model_solves_and_reacts_only_the_residual`,
`test_the_lra_named_node_internal_loads_are_the_cut_side_sums` (now four
cuts: SOB, front spar, rear spar, the box element beside the post),
`test_the_two_cantilevers_and_the_box_close_the_free_body`,
`test_a_positive_load_factor_bends_both_bodies_down`,
`test_spar_reactions_are_the_static_equivalent_of_the_one_reaction`,
`test_no_cut_lies_inside_the_box_and_no_load_crosses_a_root` and
`test_the_fuselage_comparison_reads_its_aft_sign_from_the_integrator`, the
digest sweep, `test_an_unplaceable_wing_post_is_refused_by_name`, the joint
walk with `Joint.element`, and `tests/test_doc_currency.py`.

**Appendix G, re-measured** (worst deviation over every case as a share of
the channel's own peak; shipped figures from §1 in brackets):

| Fixture | fuselage shear | fuselage bending | wing shear | wing torsion |
|---|---|---|---|---|
| `concept_regional_jet` | **44 %** at FS 460 (183 %) | 4 % (14 %) | 8 % (29 %) | 4 % |
| `baron_58` | **40 %** (111 %) | 3 % (19 %) | 27 % at BL 97 (30 %) | 14 % |
| `ga6_normal` | **33 %** (48 %) | 4 % (15 %) | 8 % (19 %) | 12 % |
| `atr42_100` | **80 %** at the rear spar (43 %) | 4 % (7 %) | 12 % (29 %) | 53 % |

Every number left is mass-station crossing — a load ahead of a grid landing
on it — which is D-56.4's accepted cost and a function of the grid count. The
jet's worst moved from the rear post to FS 460, a mass station ahead of a
forward-body grid. The ATR rose exactly as §1.1 predicted: its two cancelling
errors at the rear spar were a 19,280 lb carry station (gone) and a 12,771 lb
mass station 1.9 in ahead of the spar grid (still landing on it), and the
second now stands alone. Fuselage bending fell to 3–4 % everywhere.

**Three in-code amendments, recorded here rather than silently made.**

1. **D-64.7's on-node clause is the lumped set's, not the closed form's.**
   `sob_internal_loads` keeps counting a strip *coincident* with the SOB as
   outboard: it works on strip positions, no shipped strip sits on the SOB,
   and `test_the_station_curve_at_the_root_is_the_side_of_body_owner` gates
   the generic curve against it at a single cut with no box, where the
   interior rule applies. The root exclusion lives where the grid exists —
   `lumping._curve` with a box (gate 7) — and the wing's SOB deviation fell to
   the honest crossing of the first outboard strips onto the SOB grid.
2. **A full planform with no body datum keeps its body loads on an assumed
   wing station.** `concept_heavy` enters no side of body and no fuselage
   width, so "straight across from the SOB" has nothing to start from — and
   §8 ruling 1 was given on the premise that only a project with *no
   planform* has no wing station. Refusing it would have retired a shipped
   fixture's fuselage loads, its Appendix C, its mass-gap statements and its
   body rows in the case index, for want of one body datum. So the register
   places the wing post on the **wing LRA's own centreline point, flagged
   ASSUMED** (`WING_STATION_CENTRELINE`, the OV-1 pattern: blank derives,
   graded), still checked to lie between the spars, and carries its sentence
   onto every `BodyLoadResult.wing_station_note`, which 4.1 prints beside the
   spars. The LRA model still refuses the project — it has no SOB joint to
   start the wing at — so only the calc reads that post. D-64.3's rejected
   "extrapolate the LRA" stands where an SOB exists: on a swept wing the two
   differ, and the joint is where the body is. Gate:
   `test_a_project_with_no_side_of_body_reacts_the_wing_at_an_assumed_station`.
3. **D-64.9 is amended: a schema hop after all.** Two *result* dataclasses
   changed shape (`BodyStationLoad` gains `region`/`couple`,
   `BodyLoadResult` gains the one-station reaction and its note and loses
   `closure_artifact`), and the shape guard demands a hop for any persisted
   change, additive or not. v67 → v68, `_hop_67` an identity, the examples
   re-stamped, the delivered loads that move being the note's own (gate 8),
   not the hop's.

**Digest channels that moved** (gate 8, measured against the pre-change
snapshot): `sbeam/body_applied` on the four loaded fixtures (one reaction row
with its couple replaces five carry rows), `sbeam/lra_model` on the four that
build a model, `sbeam/wing_applied` on the same four (the inboard strips now
land on the wing box's grids), and `sbeam/body_applied` on `concept_heavy`,
whose wing station is now the assumed centreline one (amendment 2). The `body_loads` CSV/text channels of the loaded fixtures
are the p198 critical summary, which did not move; the station table with
its aft sign and blank box rows is the body applied set and Appendix C.2.
Every AIRLOADS/WINGINER/SELECT channel is byte-identical.
