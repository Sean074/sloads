# Every exported LRA deck solves, or the export refuses (design note 55)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-10 (owner); implementing on `dev/v0.8.3`.** Agreed in
chat under the solo profile (`DEVELOPMENT_PROCESS.md` §0; rule 1's working-alone
branch), as drafted — **D-55.2's tolerance decided at 5 % of `ds`** and
**D-55.5 decided as a hard refusal**, both the values this note proposed.
**Amended 2026-09-10 after AGREED: D-55.6 added during implementation.**
Fixing D-55.1 revealed it — re-parenting `ga6_normal`'s gear ties moved them
onto the very node the support picker had clamped, and the fixture went from
"will not factor" to "solves with a 569.49 lb reaction against a ~0 applied
set". The rule that prevents it was already written and documented in
`roundtrip._supportable`; `lra_model` carried only half of it. Recorded as a
decision rather than folded silently into D-55.1 because it changes the deck's
support node on two fixtures, and the owner agreed five decisions, not six.
Raised by #172 (review R-1),
band B4 Pri 29. Drafted after a diagnosis pass on all six shipped fixtures;
the numbers in §1 are measured at `dev/v0.8.3` `c79ddf8`, i.e. with note 54's
joint register (D-54.5) in place.

**Tier L** (the mission claim). The Phase-C mission says the exported deck
*solves in sbeam with verified global equilibrium, continuously in CI*. Today
that is demonstrated on two of six shipped fixtures, and the CLI exports the
other four without a word. This note decides how that claim is made true or
honestly withdrawn, per fixture.

---

## 1. What the code does today, and what is missing

`export/lra_model` builds a free-free stick model — `CBAR` chains on the load
reference axes, `RBE2` ties for the posts, attachments, gear and engines, one
clamped fuselage node. Since #262 (note 54 D-54.5) every **tie node position**
is a copy of the joint register. What has no owner is the *skeleton's
solvability*: whether the chains and ties the exporter emits form a matrix a
solver will factor.

Two shipped fixtures do not solve. They fail for two different reasons, and the
diagnosis below shows both reasons are the same class — **how a joint node is
attached to the chain it lands on**, which is exactly the territory D-54.5 took
ownership of and phase 2 was always going to inherit.

### 1.1 `ga6_normal` — a rigid chain sbeam refuses

`GRID 7605` is the rear-spar post (`lra-post A`, station 105.6). It is:

* **dependent** in the hub→rear-post tie — *"rear-spar post (BM-2): the aft body
  + empennage cantilever hangs here"*; and
* **independent** in two further ties — *"main gear (R/L) → fuselage (carrier
  BODY, G-2)"*.

So the model states `gear → post → hub` as a chain of rigid elements, and sbeam
refuses chained rigid elements. Measured across the fixtures, this is the only
such conflict anywhere:

| fixture | `RBE2`s | dependent-and-independent GRIDs |
|---|---|---|
| `ga6_normal` | 9 | **1** (`7605`, `lra-post A`) |
| `baron_58` / `cessna_210` / `atr42_100` / `dhc8_dash8` / `concept_regional_jet` | 9–10 | 0 |

**The same defect was already solved once and not swept.** The engine path folds
its two ties into one, with the reason in the code: *"one RBE2, hub folded in --
sbeam refuses chained rigid elements"* (R-9). The gear path, added for the same
model in the same idiom, never got it. **And the exclusion rule already exists
too**: the support picker is
`next(n for n in reversed(fus_fwd) if n.gid not in dependents)` — *pick a body
node that is not already an `RBE2` dependent*. The body-tie parent picker,
`_nearest_station(fus_all, x)`, has no such filter. One rule, written twice,
applied in one of the two places (`CLAUDE.md` rule 4).

### 1.2 `cessna_210` — a sliver element, not a topology error

The reported symptom is a singular matrix. It is **not** a disconnected or
degenerate skeleton: all six fixtures have one connected component, no
zero-length element, no duplicate node position, and a worst `CBAR` orientation
conditioning of 0.28 (a parallel orientation vector would be 0). What
`cessna_210` has is a **sliver element** at the h-tail attachment:

| fixture | shortest `CBAR` | where | max/min length | solves? |
|---|---|---|---|---|
| `cessna_210` | **0.0769 in** | `lra-attach R` | **1638** | **no — singular** |
| `baron_58` | **0.1270 in** | `lra-attach L` | **1464** | *not in the gate* |
| `ga6_normal` | 1.3648 in | `lra-attach R` | 113 | no — §1.1 |
| `atr42_100` | 5.5024 in | `lra-attach C` | 66 | yes |
| `dhc8_dash8` | 5.7518 in | `lra-attach C` | 64 | *not in the gate* |
| `concept_regional_jet` | 7.4313 in | `lra-attach C` | 46 | yes |

The mechanism: `_insert_on_chain` puts the attachment node at its own butt line
and keeps every strip station around it. Where the two nearly coincide, the
chain gets a sliver:

| fixture | strip `ds` | `y_att` | nearest station | gap | as % of `ds` |
|---|---|---|---|---|---|
| `cessna_210` | 7.200 | 10.877 | 10.800 | 0.0769 in | **1.07 %** |
| `baron_58` | 9.550 | 4.648 | 4.775 | 0.1266 in | **1.33 %** |
| `ga6_normal` | 3.655 | 6.713 | 5.482 | 1.2303 in | 33.66 % |
| `atr42_100` | 11.000 | 0.000 | −5.500 | 5.5000 in | 50.00 % |

A 0.0769 in bar carrying the same placeholder `PBAR` as a 126 in bar is ~4e9 in
bending stiffness ratio before `E` and `A` are counted — and the module's own
support comment records that this deck already runs within a factor of ~4 of
sbeam's 1e15 singularity refusal (*"the SI (mm) stiffness conditions at 1.6e15,
over sbeam's 1e15 refusal; here it is 2.8e14. Measured on atr42_100"*). The
insertion tolerance that would have prevented it, `_COINCIDENT_TOL`, is an
**absolute 1e-6 in** — a float-equality epsilon standing in for a geometric
question, so it never fires on a 1 %-of-a-strip near-miss.

**The two failing fixtures are exactly the two with a sliver.** `baron_58` is
the next to fail and is not in the gate to say so.

### 1.3 The gate is narrower than the claim

`tests/test_sbeam_roundtrip.py`'s `SOB_MATRIX` is
`("concept_regional_jet.project.json", "atr42_100.project.json")` — the two
fixtures that pass. `baron_58` and `dhc8_dash8` are conflict-free and
sliver-light respectively, so they may well already solve; nothing asks them.
Meanwhile `cli.py --export-target lra` exports for `ga6_normal` and
`cessna_210` with no refusal and no in-band caveat, which is the part of this
that reaches a user.

---

## 2. Governing basis

* `CONVENTIONS.md` §7 — one owner plus a drift guard per cross-cutting rule;
  §7's newest row is the joint register itself.
* Note 24 **BM-1…BM-5** (the agreed beam model) and note 27 **LM-1…LM-7** (the
  implementation decisions), including **LM-4**'s refusal contract: the
  exporter names the missing datum rather than building on a guess.
* Note 54 **D-54.5** — a joint is an owned location, a stated arm, a DOF set and
  a basis. This note is the phase-2 half the D-54.5 row forecast: *"`lra_model`'s
  node placement and `tail_span`/T7's lever arms become reads of the register"*.
  Node **placement** landed in #262; how a placed node **joins the structure**
  is what remains.
* `CLAUDE.md` rule 4 — a defect fix sweeps its class (the engine fold, §1.1).
* The mission statement in `CLAUDE.md`: the deck *solves in sbeam with verified
  global equilibrium, continuously in CI*.

**Acceptance frame.** This note moves **no delivered load**. Every change it
proposes is to the LRA deck's skeleton; `transferred_case_loads` preserves the
balanced case's resultant under LM-1 wherever the nodes sit, exactly as #262
demonstrated. Where a `GRID` or an element moves, the move is the stated, gated
fix.

---

## 3. Decisions proposed

| # | Decision | Alternative rejected |
|---|---|---|
| **D-55.1** | **A body tie never parents on a node that is already a dependent.** `_nearest_station` gains the filter the support picker already applies — the nearest fuselage-chain node *that is not an `RBE2` dependent* — so `gear → post → hub` becomes `gear → (neighbouring body station) → …` and no rigid chain is emitted. On `ga6_normal` the main-gear ties move one body station off the rear post; no other fixture is touched. | *Folding the gear into the hub tie, as the engine path does.* Rejected: the engine's hub and mount are one installation and fold naturally, but the gear's entered carrier is **BODY** (`carrier BODY, G-2`), and hanging it off the wing centre-box hub would state a load path the project did not enter. Re-parenting keeps the entered carrier true. |
| **D-55.2** | **A strip station that nearly coincides with a joint node is absorbed by the joint**, on a tolerance stated as a fraction of the local strip width `ds` rather than as an absolute epsilon. The **joint keeps the register's location** — D-54.5 is not negotiable, and a joint that snaps to a strip station is a joint placed by the mesh — and the absorbed station's load routes to it under LM-1, which is resultant-preserving. Proposed tolerance **5 % of `ds`**: it absorbs `cessna_210` (1.07 %) and `baron_58` (1.33 %) with a 25× margin to `ga6_normal`'s legitimate 33.66 % neighbour. | *Snapping the joint to the station.* Rejected: it moves an owned location by up to 5 % of a strip to suit the mesh, which is D-54.5 inverted. *Keeping the absolute `_COINCIDENT_TOL`.* Rejected: it is a float-equality epsilon answering a geometric question, and it is why the sliver exists. |
| **D-55.3** | **`_COINCIDENT_TOL` splits into its two jobs.** The absolute epsilon stays where it is genuinely float equality; the geometric "is this the same station" test becomes the D-55.2 relative tolerance, with one owner and a name that says which it is. | *One tolerance for both.* Rejected: conflating them is the defect. |
| **D-55.4** | **Every CLI-exportable fixture joins the solve gate.** `SOB_MATRIX` widens from two fixtures to every shipped example the CLI will export an LRA deck for. The gate is the mission claim; a matrix chosen from the passing set cannot test it. | *Adding only the two fixed fixtures.* Rejected: `baron_58` and `dhc8_dash8` are untested today and would remain so by accident. |
| **D-55.6** | **The support node is in no `RBE2` at all — neither end.** *(Added during implementation, 2026-09-10; see the amendment note below.)* `roundtrip._supportable` has always applied both exclusions and records why the second is load-bearing: sbeam's `recover_reactions` subtracts the raw applied vector at the constrained DOFs, so a load a rigid element transfers **onto** a constrained node is never subtracted and comes back out as reaction. `lra_model`'s own picker implemented only the first — the same rule, in two files, applied in one. Measured: `ga6_normal` recovered **569.49 lb** of Fx against an applied set closing to 0.0002 lb, and `baron_58` the same through its nose-gear tie. | *Leaving the picker as it was.* Not viable: D-55.1 re-parents a gear tie onto a forward body node, and on `ga6_normal` that node **was** the support — so without D-55.6 the fixture goes from "will not factor" to "solves with a wrong reaction", which is strictly worse. |
| **D-55.5** | **The exporter refuses a deck it knows will not solve.** A skeleton that still carries a rigid chain or a sliver after D-55.1/D-55.2 is an `LraRefusal` naming the condition, on the LM-4 contract and the BM-1 posture `concept_heavy` already gets — so the CLI can never emit a deck that silently fails in the user's solver. Expected to fire on **no** shipped fixture once D-55.1/D-55.2 land; it is the backstop, not the fix. | *Refuse-only, no skeleton fix* (#172's stated either/or). Rejected: both defects have a correct, cheap fix and a precedent in the file; refusing four of six fixtures would withdraw the mission claim rather than meet it. |

**Decided at AGREED (owner, 2026-09-10):** D-55.2's tolerance is **5 % of
`ds`** — the data separates cleanly anywhere between ~3 % and ~25 %, and 5 %
keeps a 25× margin to `ga6_normal`'s legitimate 33.66 % neighbour while
absorbing both slivers. D-55.5 is a **hard refusal**, not an in-band caveat:
a deck that will not solve is the LM-4 missing-datum posture, and a caveat
still hands the user a file that fails in their solver. Both are named
constants, so either is a one-line revision if a later fixture argues for it.

---

## 4. Gates

All identities against the owners (`rel_tol=1e-9` unless stated).

1. **No rigid chain, any fixture.** A registry-style walk: no `GRID` is both an
   `RBE2` dependent and an `RBE2` independent, and none is dependent in more
   than one tie. Fails today on `ga6_normal` `GRID 7605` and nowhere else — the
   has-teeth control is that pre-fix state.
2. **No sliver, any fixture.** Every `CBAR` is at least the D-55.2 tolerance
   long relative to its chain's `ds`. Today: `cessna_210` 0.0769 in / 1.07 %
   and `baron_58` 0.1266 in / 1.33 % fail; after D-55.2 the shortest elements
   on those two become their next real strip spacing (7.200 / 9.550 in).
3. **The gear keeps its entered carrier.** On `ga6_normal` the main-gear ties
   still reach a **fuselage** node (`carrier BODY`), one station off the rear
   post, never the centre-box hub — the D-55.1 alternative asserted against.
4. **The joint keeps its owned location.** `tests/test_joints.py`'s D-54.7 walk
   still passes unchanged on all six fixtures: D-55.2 absorbs stations into
   joints, never the reverse. This is the gate that keeps this note from
   undoing #262.
5. **Every CLI-exportable fixture solves** (D-55.4), with the reaction equal to
   minus the applied resultant ≈ 0 and the SOB / front-post internal loads
   equal to the cut-side sums — the existing LRA roundtrip assertions, run over
   the widened matrix. **Result as landed:** all six solve in Imperial;
   `concept_regional_jet` and `ga6_normal` remain strict `xfail` in **SI**
   only, on sbeam's pre-existing dense-path 1e15 condition heuristic — a units
   artifact of the mm frame (equilibrated, the same matrix conditions ~1.3e9)
   whose Imperial twin solves exactly. The regional jet was already pinned that
   way before this note; `ga6_normal` joins it for the opposite reason — it is
   the smallest airframe *and* has only two untied fuselage nodes (nose and
   tail), so D-55.6 necessarily leaves the clamp far from the wing.
   Precondition, guarded separately: the support node is in no `RBE2`
   (D-55.6).
6. **Load invariance.** Every delivered load byte-identical on all six
   fixtures; the per-subcase LRA deck resultant unchanged to the precision #262
   established (≤1e-7 of the largest applied card). `sbeam/lra_model` GRID/CBAR
   bytes move on `ga6_normal`, `cessna_210` and `baron_58`; the re-stamp is
   stated with its numbers.
7. Doc-currency; no schema change expected (nothing here is an input).

---

## 5. Effect vs error bar (rule 6)

| item | effect | rank |
|---|---|---|
| `ga6_normal` rigid chain, `cessna_210` sliver | The deck does not solve at all, and the CLI exports it anyway. This is not a fidelity item — it is the mission claim failing on 2 of 6 fixtures, with 2 more untested | **Ranks** — first-order defect on shipped content |
| `baron_58` at 1.33 % of `ds` | Not in the solve gate, so its status is unknown; it is the next sliver in line and would fail the same way | **Ranks** — with D-55.4, it costs nothing extra |
| Placeholder `PBAR` conditioning generally | The deck already runs within ~4× of sbeam's 1e15 refusal on the SI channel. Real sections are step 14's (R-12); this note only removes the *self-inflicted* 1e3-ratio slivers | Parked — with step 14, **with the 2.8e14 number that parks it** |

---

## 6. What this supersedes / corrects

* `_COINCIDENT_TOL`'s single absolute value is split (D-55.3); its geometric
  half gains the relative form and an owner.
* `_nearest_station` gains the not-already-a-dependent rule the support picker
  has carried since the model shipped — the two become one stated rule.
* The engine path's "hub folded in" comment stops being the only place the
  chained-rigid-element constraint is recorded; it becomes a gated invariant
  (gate 1).
* The support picker gains the second half of the rule `roundtrip._supportable`
  already applied (D-55.6); the two halves stop living in two files. The
  positional ordering (`reversed(fus_fwd)`, then the aft chain) is **kept** —
  D-55.6 changes which nodes are *eligible*, not the order, and a
  nearest-the-carry-through variant was measured to change only
  `cessna_210`'s clamp with no effect on any gate.
* The frozen-list entry *"the LRA beam model at its determinate paths"* gains a
  pointer here as a second scoped reopening — **how a node joins the chain**,
  the sibling of note 54 §6's *where a node sits*. The tie topology, the DOF
  sets and the determinate-path posture are untouched; D-55.1 changes which
  body station one tie parents on, not what the tie means.

---

## 7. Closure obligations (tier L)

`PROGRAM_SPEC.md`'s LRA export section (the refusal list and the skeleton
paragraph); `CONVENTIONS.md` §7 gains the **rigid-chain / minimum-element**
row with its owner and guard; no `theory_sources.md` row (this places
structure, it adopts no method); `changes/<slug>.fixed.md` +
`changes/<slug>.history.md` in full step format; the Imperial baseline
re-stamped with its numbers stated; #172 closed with the branch SHA.

---

## 8. Deferred

* **Real section properties** (step 14 / R-12) — the conditioning headroom this
  note buys is not a substitute; promoting condition is the sizing loop needing
  recovered internal loads it can trust.
* **The h-tail span between its two rigid attachments** stays
  placeholder-stiffness-dependent and the header keeps saying so (R-12).
* **`tail_span`/T7's lever arms becoming reads of the register** — the rest of
  D-54.5's phase 2. #262 established that T7 is statically exact as written, so
  this is a consolidation, not a defect, and it waits for note 51's transfer
  work to be its consumer.
* **A support node beside the carry-through.** `ga6_normal` has only two untied
  fuselage nodes, both far from the wing, which is why its SI deck sits on
  sbeam's condition heuristic. A node that exists only to be clamped — on the
  fuselage chain, in no tie, beside the carry-through — would move it off that
  edge permanently. Not taken here: it adds a node to every deck to fix one
  fixture's interaction with one solver's heuristic, and the Imperial twin
  already proves the deck sound. Promoting condition: a second fixture landing
  on the same edge, or sbeam equilibrating before its check (which retires the
  problem instead).
* **A general mesh-quality gate** (aspect ratios, chain monotonicity) beyond
  gate 2's minimum length — no fixture needs one today.
