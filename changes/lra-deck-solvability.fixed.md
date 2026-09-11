- **Every exported LRA deck solves, and the solve gate covers every fixture
  (#172, design note 55 D-55.1…D-55.6, tier L, 2026-09-10).** The mission claim
  is that the exported deck solves in sbeam with verified global equilibrium;
  it was demonstrated on two of six shipped fixtures, and the CLI exported the
  other four without a word. Three defects, all in **how a joint node joins the
  structure** — the sibling of note 54's *where a joint node sits*:
  **(1)** a body tie could parent on a node that was already an `RBE2`
  dependent, so `ga6_normal` stated `gear → rear-spar post → hub` as a chain of
  rigid elements, which sbeam refuses outright; the tie parent now takes the
  same not-already-a-dependent rule the support picker had carried since the
  model shipped. **(2)** A joint inserted near an existing strip station left a
  **sliver element** — `cessna_210`'s h-tail attachment landed 0.0769 in from a
  station (1.07 % of that chain's `ds`) for a 1638:1 element-length ratio and
  the singular solve the issue reported, with `baron_58` next at 0.1266 in /
  1.33 % and in no gate to say so. A station that close is now absorbed
  **into** the joint, which keeps the register's owned location (note 54
  D-54.5 is not negotiable) while the merged node keeps the station's `GID`, so
  its load routes there unchanged under LM-1. The governing tolerance is
  `JOINT_MERGE_FRACTION` — a fraction of the chain's own strip width, because
  "is this the same station" is a geometric question and had been answered by a
  1e-6 float-equality epsilon. **(3)** The support picker excluded `RBE2`
  dependents but not independents, although `roundtrip._supportable` applies
  both and documents why: `recover_reactions` never subtracts a load a rigid
  element transfers *onto* a constrained node, so it returns as reaction —
  measured at **569.49 lb** of Fx on `ga6_normal` against an applied set closing
  to 0.0002 lb. All three are now gated invariants, and a skeleton that still
  violates one is an `LraRefusal` naming it rather than a deck that dies in the
  user's solver. The solve gate widens from the two fixtures that passed to
  **every CLI-exportable fixture**: all six now solve in Imperial, with
  `concept_regional_jet` and `ga6_normal` remaining strict `xfail` in SI only on
  sbeam's pre-existing dense-path condition heuristic. No delivered load moves;
  `sbeam/lra_model` bytes move on `ga6_normal`, `baron_58` and `cessna_210`.
