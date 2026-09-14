# Chapter 11 — Export and the sbeam Bridge

*(Chapter stub — template, assumptions and the validation record populated;
the deck-format walk-through follows in a later step.)*

## Scope

The delivery boundary: `FORCE`/`MOMENT`/`CONM2` bulk data for the sbeam
solver, the coordinate mapping, the consistent-unit solver channel, and the two
gates that hold the deliverable itself — equilibrium re-derived from the emitted
card text, and an independent solve of the deck as it ships.

**What ships, since design note 56.** One solver deck, the **LRA beam model** of
the whole free-free airplane, plus the **CONM2 mass model**, which is a mass
statement rather than a solve. The five per-component decks are deleted (D-56.2)
and the elementless assembled deck no longer leaves the tool (D-56.8); it
survives inside the package as the un-aggregated load set at each load's own
position, which is what the beam model's re-aggregated set is checked against.
Much of the validation record below was written against the retired artifacts
and is kept as the record — each part says what it now applies to.

## The contract in one place

- **The frame is the identity** — sloads axes are already NASTRAN basic
  CID 0, and `export/coordinates.py` is the only place anything is multiplied
  on the way out (chapter 2 §2.1).
- **Solver decks use the consistent-unit channel** (N·mm, MPa in SI;
  all-1.0 Imperial except mass), resolved once per bundle; every file states
  its unit set in band (chapter 2 §2.6).
- **Every load is LIMIT and every deck states, per subcase, the factor it
  did not apply** (chapter 2 §2.7). Closure is exact rather than scaled, and
  the assembled reference set's resultant is asserted against `nz × W`
  *without* the factor — the one check the scale-invariant gates structurally
  could not provide. It is asserted on the internal assembled deck (G-OR-72),
  which is where that load set is written at full precision; the shipped beam
  deck inherits the basis, because its cards are the same set re-aggregated.
- **Subcase identity derives from the case id**, never from position in an
  export (chapter 2 §2.8).
- **Beam torsion vs rigid-body moment:** the wing deck's `MOMENT` cards carry
  each strip's *free* torsion at its own node, so the sweep/dihedral transfer
  is the solver's to generate — the resolution of design note 46 recorded in
  the export-boundary section below.

## Assumptions & limitations

- **No cut model ships any more** (note 56 D-56.2). Each per-component deck
  used to be one: it carried its cut reactions as applied loads, stated its
  moment closure about its own reference, and its case set was disjoint from the
  other decks' by construction, so no cross-deck sum was meaningful (finding 1
  below). The surviving deck is the whole airplane, so it has one reference and
  no cut reaction to double-apply.
- **The beam mesh is a discretisation, and it costs something** (D-56.4/D-56.9).
  The beam's nodes are decided from geometry, not from the load stations, so the
  distributed set is re-aggregated onto them by the LM-1 transfer. That moves no
  resultant — a gate — but it does move the *internal* load at a cut. How much,
  per surface and per channel, is published rather than assumed: oracle report
  Appendix G, and `00_theory_sources.md` §"The lumping rule".
- **The solver has no inertia relief in SOL 101**, so the free-free decks
  carry a statically determinate support; "reactions ≈ 0" is the free-free
  proof, computed from geometry sbeam derives itself (finding 2 in the
  round-trip section).
- **`GRAV`-driven rotational inertia is not recoverable from a `CONM2` set**
  (no `RFORCE` in sbeam): pitch/yaw inertia loading stays checked by
  sloads-side closure (chapter 10 §CONM2).

## How it is validated — the record (moved from the theory hub)

### The export-boundary closure gate (step 1, 2026-08-08)

The identities above are evaluated on in-memory results. Because concept mode has
no printed oracle, the **deliverable itself** needs a stated closure gate too
(`CLAUDE.md` required practice 2) — the deck a solver actually reads, not the
objects it was rendered from. `sloads/export/equilibrium.py` re-derives Σ`FORCE`
and Σ`MOMENT` **from the emitted card text**, about the per-component reference
of `CONVENTIONS.md` §1, and `tests/test_export_equilibrium.py` sweeps every
shipped example × {Imperial, SI}.

The table below is the gate **as written against the five per-component decks**,
kept because it records what each component's resultant *is* and why. Those
decks retired at note 56 D-56.2; the identities did not, because they were never
properties of the files. They are now asserted on the applied load set the one
surviving deck is built from — the same numbers, one artifact instead of five —
and the assembled reference set keeps the moment closure it always had, about
the airplane rather than about five separate cuts.

| Deck | Force closure | Moment closure | Basis |
|---|---|---|---|
| Wing | Σ`FORCE`.Fz/Fx = SF × root `Sz`/`Sx` | the **full rigid-body** `m` about the root station = SF × root `Mxx`/`Myy`/`−Mzz`, at every station and not only the root | Ch 14 (net loads); WINGINER quadrature |
| Body | Σ`FORCE`.Fz = 0 | Σ`FORCE` moment about the aft-most `GRID` = 0 | **Ch 15 p103** — the fuselage beam is assembled free-free (inertia + tail air load + wing carry-through), so its equilibrium statement is `Σ = 0` |
| Tail | Σ`FORCE` = SF × (`LT25`+`LT50`) on the surface's normal axis (h-tail `Fz`, fin `Fy`) | chordwise first moment = the profile's own (deck ↔ CSV cannot disagree), about `My` / `Mz` respectively | Ch 10 |
| Control | Σ`FORCE`.Fz = SF × critical load | — (no geometry; chord-fraction profile) | AILERON/FLAPLOAD/TABLOADS |

Two findings recorded because they are the kind that get re-proposed:

1. **The invariant is not `Σ FORCE = n·W`.** That form (as originally worded) is
   unrealizable per-component: the body deck already closes to *zero*, the decks'
   case ids are disjoint by construction so no case pairs a wing, body and tail
   block, and the wing deck is a root-clamped half-span whose root shear is not
   `n·W/2` (fuselage-carried lift plus inertia relief; and doubling is wrong for
   the antisymmetric cases outright). The assembled-airframe `n·W` closure was
   left as a separate item at the time; it landed as G-OR-72, and with the
   per-component decks gone it is the only form of the invariant left.
2. **A beam torsion is not a rigid-body moment** — see `CONVENTIONS.md` §1 —
   **but the wing deck's torsion now is one** (design note 46 OR-67/OR-68,
   2026-09-03). While the `MOMENT` cards were increments of the cumulative
   `Myy` they already contained the sweep/dihedral transfer of the outboard
   shear, so only the bare card sum could be asserted; measured against the
   published table under the rigid-body accumulation a solver performs, the
   exported torsion was wrong by 151/190/120 % on `ga6_normal`
   (PHAA/TORS/ACRL) and 34/21 % on `baron_58`, while shear and both bending
   columns closed exactly — which is why differencing survived the closure
   sweep for as long as it did. The cards now carry each strip's **free**
   torsion at its own node, so the transfer is the solver's to generate and
   the claim is `m.y`. Closure gate: the six-component resultant of the applied
   set reproduces `Sx`/`Sz`/`Mxx`/`Myy`/`−Mzz` at every station of every case
   of both example airplanes to ~2.5e-15 relative
   (`tests/test_applied.py::test_the_applied_set_reproduces_the_whole_vmt_at_every_station`;
   from the deck's own text,
   `tests/test_export_equilibrium.py::test_wing_deck_reproduces_the_station_table_at_every_node`).

Tolerances have one owner (`equilibrium.REL_TOL` / `ZERO_REL_TOL`): `1e-4`
relative against a non-zero target, and against a **zero** target
`1e-6 × Σ|term| + 1e-3` in deck units — summed, not maxed, because the error
being bounded is accumulated `%.6E` card truncation (~5e-7 per card). A moment
term is summed **before** the cross product cancels, and against the *absolute*
coordinate the card format rounds rather than the arm: a swept, dihedralled
wing's torsion is a small difference of two large products, and budgeting it by
the cancelled result called a 44 N·mm text-rounding residue a physics failure
(note 46).

### The solver round-trip as a closure gate (step 2, 2026-08-08)

The gate above reads the deck's own card text; this one hands the deck to
**another program**. Where no printed oracle exists, an independent *consumer*
reproducing the numbers is the strongest substitute available (`CLAUDE.md`
required practice 2), and it is the only form that covers whether the deliverable
is solvable at all. `sloads/export/roundtrip.py` parses and solves each deck
through sbeam's own `parse_bdf` / `run_sol101`, and
`tests/test_sbeam_roundtrip.py` sweeps the shipped deck over four fixtures ×
{Imperial, SI}. Design note:
`docs/25_notes/17_sbeam_roundtrip_ci_harness_plan.md`.

**The harness collapsed at note 56 D-56.8/§8.** Two thirds of `roundtrip.py` was
`wrap_as_stick_model`, which invented `CBAR`s, a `MAT1`/`PBAR` section, a
determinate support and a case control so that an *elementless* deck could be
solved at all. Its own guard refused a deck that already carried elements — a
wrapped copy is not the shipped artifact, and it said so. With the per-component
decks deleted and the assembled one unshipped there is no elementless deck left
to wrap: the beam model writes its own elements and supports and goes to the
solver exactly as it ships. The four solver assertions the wrapper carried moved
onto that deck rather than retiring. The table below is likewise the record of
the wrapped-deck era; the "Assembled full-span" row is the one whose subject
survives, now read on the beam model.

| Deck | What the solver must reproduce | Independent of the cards? |
|---|---|---|
| Wing (stick, as exported) | reaction = −Σ applied (force and moment, about the deck's own clamped node); reaction `T3` and element-1 end-B `SHEAR-1`/`BENDING-2`/`BENDING-1` = SF × root `Sz`/`Mxx`/`−Mzz` | **Yes** for the last two — the target is the NETLOADS quadrature (`r.stations[0]`), while the cards come from `wing_nodal_loads` |
| Body (test-only wrapper, determinate support) | the deck **solves**; Σ reactions = 0; and every element's `SHEAR-1`/`BENDING-2 B` = −SF × cumulative `Sz` / +SF × cumulative `Myy`, station by station | **Yes** — sbeam reassembles the whole Ch 15 p103 cumulative table from the `FORCE` cards and `GRID` coordinates alone |
| Tail (test-only wrapper, clamped at the LE station) | the deck solves; reaction `T3` = −SF × (`LT25`+`LT50`); reaction moment about the LE station = the chordwise first moment | Partly — the total is Ch 10's, the moment is the deck's own profile |
| Assembled full-span (as exported) | the deck solves and **all six** reaction components are zero at its determinate support | **Yes** — the target is the constant 0 |

Three points of substance, none of them re-derivable from the card-sum gate:

1. **Never a root-node moment comparison** (decision S-6). The wing stick model's
   clamped node sits half a strip inboard of station 0 and, on a swept wing,
   offset in `x`, so its reaction moment is *not* station-0 `Mxx`/`Myy` — on
   `ga6_normal` PHAA, −1.847E5 against a −91,410 lb-in root torsion. Element 1 is
   the exception the identities rest on: `_root_node` copies station 0's `x` and
   `z`, so that element lies exactly along `y` and its local frame is a fixed
   permutation of the airplane axes.
2. **"Reactions ≈ 0" is the free-free proof, not a modelling convenience.** SOL
   101 has no inertia relief (sbeam's `SUPORT` is SOL 144 only), so the free-free
   decks carry a **statically determinate** support, which by construction
   carries exactly the residual the applied set fails to balance — computed from
   the lever arms *sbeam* derives from the deck's `GRID` cards, not the ones
   sloads used. A deck that closes on paper but reacts non-zero here has a
   geometry error no card sum can see; the third negative test below demonstrates
   exactly that.
3. **The gate is shown to bite.** Three mutation tests assert it *fails*: a wing
   `FORCE` card scaled by 1.01, two `SUBCASE`s' `LOAD` ids swapped, and one body
   `GRID` displaced by 1 % — the last of which leaves every force sum in the deck
   closing exactly, so only the solve can catch it.

Tolerances are the export-boundary gate's own (`equilibrium.closes`), deliberately:
the two gates must never disagree about what "equal" means.

**Recorded solver finding (2026-08-08).** sbeam's `recover_reactions` subtracts
the *unreduced* applied vector at the constrained DOFs, so a load that a rigid
element transfers onto a constrained node is never subtracted and reappears as
reaction. Found here: `concept_regional_jet`'s fuselage carries the tail air load
at exactly a mass lump's station, and the support at that node reported 1738.13 lb
against an applied set closing to 0.007 lb — to the pound, the tied node's own
load. The harness supported elsewhere, via `roundtrip._supportable`, which cost
nothing since determinacy needs two distinct positions and not two particular
ones; that rule now lives in `lra_model`'s support picker, which is its sole
owner since D-56.8 retired the wrapper. This is a finding *about sbeam*, filed for that repository, not a sloads
defect.

These hold to machine precision on the concept fixture (wing/tail rel ≈ 1e-16, body
terminal shear ≈ 1e-12 lb). The wing-`Nz·W` and tail-moment identities deliberately
re-use the FLTLOADS equilibrium formulas — their purpose is to prove the **concept
branch stays balanced** (no silent NaN / unbalanced result), not to re-derive the
aero. The FAR23 identity (concept reduces exactly to FAR23 on GA inputs) is a
separate guard, Step P1-3.

## Sources

- `CONVENTIONS.md` §1–§4 — the frame, units, LIMIT and case-identity
  contracts the export honours.
- Design note 46 (`docs/40_history/`, wing free-torsion cards) and
  `docs/25_notes/17_sbeam_roundtrip_ci_harness_plan.md` — the round-trip
  harness design.
- [`00_theory_sources.md`](00_theory_sources.md) — the concept-closure
  identity table this boundary is the last row of.
