## Step — Every exported LRA deck solves, or the export refuses (#172, design note 55, tier L, 2026-09-10)

**Objective.** Make the Phase-C mission claim true per fixture. *"The exported
deck solves in sbeam with verified global equilibrium, continuously in CI"* was
demonstrated on `concept_regional_jet` and `atr42_100`; `ga6_normal` and
`cessna_210` did not solve, `baron_58` and `dhc8_dash8` were never asked, and
the CLI exported all four without a refusal or a caveat. The roundtrip LRA leg's
matrix was the set of fixtures that passed it, so the claim was tested against
its own survivors.

**Agreed first.** Design note 55 (AGREED 2026-09-10, owner), D-55.1…D-55.5, with
D-55.2's tolerance decided at 5 % of `ds` and D-55.5's posture as a hard
refusal. **D-55.6 was added during implementation and the note amended** — see
the key decisions below.

**What the diagnosis found.** The two reported failures had different symptoms
and one cause: *how a joint node joins the chain it lands on* — the sibling of
note 54 D-54.5's *where a joint node sits*, and the phase-2 half that row
forecast.

* `ga6_normal`: `GRID 7605`, the rear-spar post, was **dependent** in the hub tie
  (BM-2) and **independent** in both main-gear ties, because the nearest body
  station to the trunnions is the post. That states `gear → post → hub` in rigid
  links, which sbeam refuses. It was the only such conflict across all six
  fixtures — and the rule that prevents it existed twice already, in the engine
  path's *"one RBE2, hub folded in — sbeam refuses chained rigid elements"* and
  in the support picker's `n.gid not in dependents`.
* `cessna_210`: **not** a topology error. All six fixtures are singly connected
  with no zero-length element, no duplicate node and a worst `CBAR` orientation
  conditioning of 0.28. The h-tail attachment landed **0.0769 in** from a strip
  station — 1.07 % of that chain's `ds` — for a **1638:1** element-length ratio
  on a deck the module's own comment records as running within ~4× of sbeam's
  1e15 refusal. `baron_58` was next at 0.1266 in / 1.33 %; `ga6_normal`'s
  equivalent neighbour is a legitimate 33.66 %, so the two populations separate
  by a factor of 25.

**Deliverables.** In `export/lra_model.py`: the body-tie parent picker gains the
not-already-a-dependent filter (D-55.1); `_insert_on_chain` gains `merge_tol`
and the absorb-into-the-joint semantics (D-55.2), swept per rule 4 to the
hinge/actuator parents on the same chains; `_COINCIDENT_TOL` is documented as
float equality only and `JOINT_MERGE_FRACTION` becomes the geometric owner
(D-55.3); `_refuse_unsolvable_skeleton` is the LM-4 backstop (D-55.5); the
support picker excludes both ends of every `RBE2` (D-55.6).
`tests/test_sbeam_roundtrip.py` gains `LRA_SOLVE_MATRIX` — every CLI-exportable
fixture (D-55.4) — beside `SOB_MATRIX`, which keeps its two SOB-specific
assertions and loses a stale comment about `ga6_normal` having no body data.
`CONVENTIONS.md` §7 gains the skeleton-solvability row; `PROGRAM_SPEC.md`'s LRA
section states the three invariants and the widened gate.

**Test.** Gates 1–3 and D-55.6's precondition are four parametrized guards in
`tests/test_lra_model.py`, each **mutation-tested**: reverting the fixes fails
them on exactly the fixtures the issue named — gate 1 on `ga6_normal`, gate 2 on
`cessna_210` and `baron_58`. Gate 5 is the widened solve gate, run against the
locally installed sbeam: **all six fixtures solve in Imperial**, with the
reaction equal to minus the applied resultant. Gate 6: every delivered load
byte-identical on all six; of 330 baseline channels only `sbeam/lra_model`
moved, on three fixtures, and the per-subcase deck resultant is unchanged
(worst 2.5e-9 of the largest applied card). A regression test covers a project
with no vertical tail, which is the shape no fixture is and which the D-55.2
work briefly broke.

**Key decisions.** (1) *Fix the skeleton, do not refuse.* #172 offered
refuse-with-stated-absence **or** fix; both defects had a correct, cheap fix and
a written precedent in the same file, so refusing four of six fixtures would
have withdrawn the mission claim rather than met it. D-55.5's refusal stays as
the backstop and fires on nothing shipped. (2) *The station is absorbed into the
joint, never the reverse.* Snapping the joint onto the nearby station is the
obvious sliver fix and is note 54 D-54.5 inverted — it would place an owned
location by the mesh. Gate 4 asserts `tests/test_joints.py` still passes
unchanged, so this note cannot undo the last one. (3) *The gear re-parents, it
does not re-route.* Folding it into the hub tie as the engine path folds its hub
would state a load path the project did not enter: `ga6_normal` enters
`carrier BODY`, so its gear still reaches a fuselage node, one station off the
post. (4) **D-55.6 was found by fixing D-55.1 and is recorded as its own
decision.** Re-parenting the gear ties moved them onto the very node the support
picker had clamped, and `ga6_normal` went from *will not factor* to *solves with
a 569.49 lb reaction against a ~0 applied set* — strictly worse. The preventing
rule was already written and explained in `roundtrip._supportable`; `lra_model`
carried half of it. Folding it silently into D-55.1 would have hidden a change
to the support node on two fixtures, so the note was amended and the owner
flagged. (5) *The positional support ordering is kept.* A
nearest-the-carry-through variant was implemented and measured: it changes only
`cessna_210`'s clamp and no gate outcome, so the smaller diff and the shipped
idiom win; D-55.6 changes which nodes are eligible, not the order. (6)
*`ga6_normal`'s SI deck joins the regional jet's existing strict `xfail`.* It is
the same pre-existing sbeam limitation — a dense-path 1e15 condition heuristic
reading a units artifact of the mm frame, where the Imperial twin of the
identical model solves exactly. The fixture sits on that edge because it has
only two untied fuselage nodes, both far from the wing; a dedicated support node
beside the carry-through would move it off permanently and is deferred in §8
with its promoting condition rather than guessed at here.
