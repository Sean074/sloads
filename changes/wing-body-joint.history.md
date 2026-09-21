## Step — The wing-to-body joint is one post, two body cantilevers, and nothing integrated through the box (#275, design note 64 D-64.1…D-64.9, tier L, 2026-09-21)

**Objective.** Close the defect design note 64 measured: Appendix G's
fuselage comparison integrated the body nose to tail through the
carry-through, where the LRA model has no beam, so M4-1's five carry
stations routed onto a spar post crossed its cut and the report stated a
183 % "lumping" deviation on `concept_regional_jet` and 111 % on
`baron_58`; the wing's side-of-body cut counted the inboard strips the
deck's own SOB statement excludes. The owner ruled the joint wrong in kind:
the box between the spars is not a beam region, the body is integrated from
each free end to its spar, the wing to the side of body, and one vertical
post connects them.

**Deliverables.** The joint register states four joints and what spans each
arm (`Joint.element`): the side-of-body pair whose arms run straight across
to the wing centre grid at the SOB's own station and waterline (D-64.3), the
two spar grids whose arms run along the body to the wing-station grid, and
the one rigid **wing post** (`WING_POST`, side `W`); a wing station outside
its spars is refused by name, and `joints.wing_station` owns it for the
calc. The LRA model builds the wing beam tip → SOB → centre → SOB → tip, the
fuselage beam nose → front spar → wing station → rear spar → tail with the
box as three owned grids and two elements, and one `RBE2` between them; the
centre hub and its four ties and BM-2's elementless carry-through retire;
`LraModel.boxes` states where each member's integration stops. `body_loads`
integrates two cantilevers from their free ends, shear and bending
**positive for an up load** in either body (D-64.4, owner `cantilever_sign`,
a `CONVENTIONS.md` §7 row), closes the free body with one reaction — force
and couple at the wing station, what the post transmits (D-64.5) — reports
the spar fitting pair as its static equivalent, publishes each station's
`region` and the reaction's `couple`, and refuses an unplaceable post with
the register's sentence; M4-1's linear smear, `CARRY_THROUGH_NODES`, the
`"carry"`/`"correction"` families and the `closure_artifact` fallback with
its caveat are gone. Appendix G integrates as the deck does: no cut inside
the box, the roots' on-node loads the box's, the aft sign read from the
integrator (D-64.6). The report's 4.3 method, 4.4 closure sentence,
Appendix C.2 (a `Region` column, box rows blank) and the methods block, the
body-loads CSV (`Region`, `My_free`), `PROGRAM_SPEC.md` (body_loads, the LRA
joint), `CONVENTIONS.md` §7, `theory_sources.md` and `ch06` state it.

**Test.** Gates 1–11 of the note on every CLI-exportable fixture: the box is
two elements and the post the only wing-body connection; the free-free
solve; the cut-side sums at the SOB, both spar grids and the box element
beside the post; the two-cantilever closure to 1e-9; a positive load factor
bends both bodies down; the fitting pair recovers the reaction; no cut
inside the box and no load crossing a root; every oracle channel
byte-identical; refusal by name, mutation-tested by moving a fixture's
spars; the joint walk with `Joint.element`; doc currency. Re-measured
Appendix G (note 64 §7b): fuselage shear 183 → 44 % on the jet, 111 → 40 %
on the Baron, 48 → 33 % on GA6, and 43 → 80 % on the ATR where two
cancelling errors became one; fuselage bending 14–19 % → 3–4 %; wing shear
19–35 % → 8–27 %. Everything left is mass-station crossing.

**Key decisions.** One post keeps the model a tree at the joint, which is
R-12's condition — its objection was to two posts. Straight across, not the
extrapolated LRA (21 in apart on the swept jet). The reaction at one
station because Ch 15 prints no table to match; the fitting pair survives
as a statement. The whole-body fallback retires because the reaction is
physically sourced; a project with a planform and no body datum
(`concept_heavy`, no side of body and no fuselage width) reacts the wing at
the LRA's centreline point flagged ASSUMED, the sentence carried on every
result and printed beside the spars (§7b amendment 2), while the LRA model
still refuses it. The result shapes forced a schema hop, v67 → v68, an
identity (amendment 3). The oracle-locked wing tables still run to the
centreline; only the LRA deliverables integrate to the SOB.
