## Step — The joints between components get an owner (#262, design note 54 D-54.5/D-54.7, tier L, 2026-09-10)

**Objective.** Close note 54's remaining decision pair. Every inter-component
transfer in the LRA beam model is an `RBE2`, and a rigid tie across a real
offset carries the exact lever-arm couple — so the *mechanism* was always
statically exact. What had no owner was the **node positions**: each end of each
tie was resolved independently, from separately entered data, by whichever
expression was nearest to hand, and nothing compared the two. Note 54 §1 states
the covering rule — *a joint between two components must be a first-class
geometric entity: an owned location, stated offset arms, a DOF set and a basis,
not an emergent coincidence of separately-entered surfaces.*

**Agreed first.** Design note 54 (AGREED 2026-09-09, owner), D-54.5 for the
register and D-54.7 for its drift guard. The note left the register's home open
("`sloads/joints.py`, or a `geometry` submodule — final home decided at
AGREED"); decided at implementation as `sloads/joints.py`, because the register
must import `tail_geometry`, `derived_geometry` **and** `modules/tail_span` and
so can live inside none of them, `modules/` is reserved for
`run(project) -> ModuleResult` producers, and calc may not import `export/` —
`lra_model` importing `joints` is the correct direction.

**What the register found.** Three of the five joint kinds already agreed with
their owners at `rel_tol=1e-9` (fin root, wing SOB, spar posts — the fin-root
waterlines reproduce note 54 gate 1's table exactly: 111.5 / 110.0 / 100.2 /
191.2 / 203.5 / 87.0). Two did not:

| fixture | R-6 tie as exported | the owners' arm | error |
|---|---|---|---|
| `atr42_100` | dx −23.228, dz +6.250 | dx −25.600, dz 0 | 2.37 in x, 6.25 in z |
| `dhc8_dash8` | dx −23.753, dz +6.500 | dx −26.100, dz 0 | 2.35 in x, 6.50 in z |
| `concept_regional_jet` | dx −20.876, dz +6.900 | dx −26.680, dz 0 | **5.80 in x (−22 %)**, 6.90 in z |

`vtail_chain[-1]` was the outermost fin **strip midpoint**, half a strip below
the surface's own top — the whole of the spurious `z` — and the h-tail
centreline node was interpolated off the strip-station polyline at `y = 0`,
which on a swept surface answers with the innermost strip's station rather than
the centreline's. The conventional attachment pair carried the same defect in
miniature: the node interpolated off the chain while the body station it reacts
against came from the planform owner, 0.356 in apart on `ga6_normal` and 0.010
on `baron_58`. These are the arms note 51's D-51.2/D-51.3 transfer moments are
computed across, which is why note 54 §5 ranks this as note 51's enabling gate.

**Deliverables.** `sloads/joints.py`: `JointName`, a frozen `Joint` (name, side,
`location`, `arm`, `to`, `node_family`, `dof`, `basis`, `assumed`, `note`),
`Refusal`, `JointRegister` and `joints(project)`. One uniform `Joint` with a
**pair modelled as two rows** rather than a per-kind type union — the h-tail
attachments, the SOB nodes and the spar posts are each two physical points with
two GIDs already, and flattening them is what lets the drift guard walk the
register with no per-kind branch. `location` is always a full airplane point,
never a station scalar: the two joints that were wrong were wrong in a
coordinate a scalar form would have dropped. `export/lra_model` reads the
register for the SOB pair and hub, the posts, the fin root, the new
`lra-fin-tip` node, the h-tail centreline and the attachment pair, and raises
`LraRefusal` from the register's refusal reasons; `_insert_on_chain` gains an
optional owned `pos`. `wing_geometry.chord_fraction_x` is extracted as the
single owner of the chord-fraction line, replacing the copies in
`TailPlanform.x_at` and `net_loads.to_loads_ref_axis`. `CONVENTIONS.md` §7 gains
the joint-register and chord-fraction rows; `PROGRAM_SPEC.md`'s LRA section and
`PROJECT_GUIDE.md`'s package tree follow. **No schema change — v65 stands**, so
`DATA_DICTIONARY.md` regeneration is a no-op, and note 54 §7 rules that no
`theory_sources.md` row is owed (this places geometry; it adopts no method).

**Test.** `tests/test_joints.py`, four guards in the shapes the suite already
uses. The D-54.7 walk parses the **emitted deck text** — `GRID` cards, their
`$ SLOADS-NODE` tags and the `RBE2`s — rather than the `LraModel` object, since
once `lra_model` reads the register an in-memory comparison would be very nearly
tautological; the 1e-9 copy identity is asserted against the built model and the
deck is then held to the writer's own precision (1e-3 in, an order of magnitude
below the smallest defect this guard chases, `baron_58`'s 0.010 in). It walks
whatever the register produced and has no fixture list of its own, so a joint
added is guarded the day it exists; `test_the_joint_set_partitions_by_layout` is
its guard-on-the-guard, pinning every fixture to a non-empty, layout-correct set
and failing on any `JointName` with no producer. `test_the_walk_would_have_caught_the_tip_joint_arm`
restores the pre-register construction and states what it cost. Gate 4 is
written data-driven against `carry_through(project).assumed` — with the entered
direction on a constructed project, since no shipped fixture enters its spar
stations — so #260 flipping any fixture needs no edit here. The walk was
mutation-tested: reintroducing the old tip placement fails it on exactly the
three T-tails.

**Key decisions.** (1) *Placement rewired now, not in phase 2.* D-54.7's own
wording — "positions are copies of one owner, not measurements" — forecloses
the softer reading: two independent computations compared at 1e-9 is a
measurement, and a register that disagreed with the deck on three of six
fixtures would be a *sixth* independent copy, the thing note 54 §1 exists to
stop. (2) *Gate 8 re-scoped, with the numbers* (owner, 2026-09-10; recorded in
the note). Byte-identical `GRID`s and "the register owns placement" are
incompatible. What holds: every **delivered load** is byte-identical on all six
fixtures — of 330 baseline channels exactly one moved, `sbeam/lra_model`, on
five (`cessna_210` is byte-identical) — and equilibrium is preserved exactly,
the per-subcase deck resultant unchanged to four significant figures with the
largest change 5.2e-8 of the largest applied card, because `transferred_case_loads`
holds the balanced resultant under LM-1 wherever the nodes sit. (3) *Refusals
are carried as grades, not raised.* The register is calc-side and will be read
by consumers that must not refuse (the report's provenance sentences today,
`body_loads`' T-tail entry point in phase 2); whether a missing joint is fatal
is the exporter's policy (BM-3), so `lra_model` keeps raising `LraRefusal` — but
reads its reason from the register, so the two cannot drift. (4) *T7's `x_tip`
was investigated and dismissed, not filed.* `tail_span.py:1159` feeds the same
outermost-strip station into `ttail_transfer`, which looks like the same defect;
it is not. `sbeam_bridge` applies the transfer's force **and** its free moment
at that same node, so `(F at P, M about P)` is a statically exact decomposition
and the resultant about any reference is independent of `x_tip` —
`tail_span.py:1155` says so deliberately. Moving it would only be correct if the
application node moved too, and that node is a strip midpoint from the aero
integration, so it would reopen the strip scheme and its oracle for no change in
any delivered load. Left alone. (5) *The chord-fraction owner was extracted
first.* The expression existed twice and the register would have made it three;
per rule 3 the formula got an owner before the register read it, which is also
what makes the tip arm's `z` member zero **by construction** — `h_tail_waterline`'s
fin-tip branch *is* `root_z + span`, so note 54 gate 2's first clause is proved
rather than asserted. (6) The fin chain gains one `CBAR`, shifting `lra-cbar`
EIDs on the three T-tail decks: numbering, not posture. The scoped reopening
note 54 §6 grants is node *placement* only — the same four tie kinds, the same
`123456` DOF, the same `SPC1` support rule, all untouched.
