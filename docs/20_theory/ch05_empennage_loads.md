# Chapter 5 — Empennage Loads: Horizontal Tail, Vertical Tail, and One Engine Out

*(Chapter stub — template, cases, assumptions and validation populated; the
full method walk-through with worked examples follows in a later step. The
per-module equation citations remain authoritative in
[`00_theory_sources.md`](00_theory_sources.md) §Per-module equation citations;
the lateral *balanced-airplane* cases built on these loads are chapter 9 —
[`ch09_balanced_airplane.md`](ch09_balanced_airplane.md) §7.)*

## Scope & regulatory basis

The empennage's design conditions and distributed loads: horizontal-tail
balancing (FAR 23.421), maneuvering (23.423), gust (23.425) and unsymmetrical
(23.427) conditions; vertical-tail maneuvering (23.441), gust (23.443),
outboard-fin/T-tail interaction (23.445) and the one-engine-out yaw transient
(23.367); the chordwise pressure profile (TAILDIST, Reference 1 Ch 10), the
spanwise distribution (`tail_span`), the discrete control-surface path with
the hinge moment, and the T-tail transfer.

## Cases analyzed — two pipelines, no SELECT pruning

Unlike the wing (chapter 4), the empennage's cases never pass through a
critical-condition prune. Two pipelines feed it:

**Envelope-derived balancing loads.** For every balanced V-n point (chapter 3
§13) there is a balancing horizontal-tail load; SELECT resolves each into the
angle-of-attack load at 25 % tail MAC and the camber (elevator) load at 50 %,
and selects the largest up and largest down balancing load flaps-retracted
(23.421). These cases trace to the envelope inventory.

**Regulation-prescribed discrete conditions**, evaluated *at* the chapter-3
design speeds but not selected from the matrix:

| Surface | Condition | FAR basis |
|---|---|---|
| H-tail | unchecked / checked pitch maneuvers | 23.423 |
| H-tail | vertical gust at VC/VD | 23.425 |
| H-tail | unsymmetrical distribution (100 % / (100 − 10·n) % sides of the symmetric case) | 23.427(a) |
| V-tail | sudden full rudder at VA | 23.441(a)(1) |
| V-tail | yaw to 19.5° sideslip, rudder held | 23.441(a)(2) |
| V-tail | 15° yaw, rudder neutral | 23.441(a)(3) |
| V-tail | lateral gust at VC | 23.443(b) |
| V-tail | **one engine out** — the yaw transient after critical-engine failure | 23.367 |
| T-tail | h-tail loads carried by the fin — the transfer pairing | 23.445 / note 51 (AC 23-9 method) |

**The down-select is deferred, not absent:** all conditions run, and
criticality is decided by the **two-sided spanwise envelope** (max *and* min
per station, both edges — chapter 2 §2.3). SELECT prunes *before* analysis;
the empennage envelopes *after*. Both chapters state this contrast because
losing it is how a governing down-load case disappears.

### One engine out (23.367) — three ways unlike everything else here

1. **It is the suite's only time-marching simulation.** ONENGOUT (Ch 11)
   integrates the post-failure yaw transient — thrust/windmill-drag asymmetry,
   pilot applying full rudder at peak yaw rate but not before 2 s
   (23.367(b)), recovery — by explicit Euler steps, and reports the maximum
   vertical-tail load. Every other v-tail case is static.
2. **It is one of the two ULT families.** 23.367(a)(2)'s
   disconnection/blade-loss loads are prescribed already ultimate
   (`ULT SF=1.0`, apply nothing further) — one of only two conditions in the
   project carrying the `-ULT` marker (chapter 2 §2.7).
3. **Its oracle is the deferred one.** The printed one-engine-out oracle is
   Appendix B (the 10-place twin), absent from the bundled PDF, so the module
   is closure-locked at the sub-formula level against `ONENGOUT.BAS` — the
   most exposed family in the provenance table
   ([`00_theory_sources.md`](00_theory_sources.md) §The families still
   running on internal identities only).

It shares the v-tail aero terms (lift-curve slope, rudder effectiveness, the
large-deflection factor) with the static rudder cases through one owner
(`sloads/modules/_vtail.py`), which is why it lives in this chapter; the
engine-mount chapter (7) only cross-references it.

## Method (outline)

- **Chordwise:** TAILDIST (Ch 10) places the angle-of-attack load at 25 %
  chord and the camber load at 50 %, building the per-chord-station pressure
  profile whose net trailing-edge pressure is identically zero.
- **Spanwise:** `tail_span` distributes SELECT's `LT25`/`LT50` totals
  chord-proportionally per strip, with d'Alembert inertia signed by the load
  factor alone; the h-tail beam is full-span tip-to-tip, the v-tail a single
  surface in `fy`/`mzz` (chapter 2 §2.5).
- **Control surfaces:** the elevator/rudder load is SELECT's, decomposed and
  re-entered at the hinges with the hinge moment `HM = L_cs·(c_e/3)` — exact,
  because the aft-of-hinge pressure block is always a triangle.
- **T-tail:** each v-tail case carries the balancing h-tail load at its own
  V-n point plus that point's h-tail inertia, at the fin's last node.

## Assumptions & limitations

- **The spanwise shape is chord-proportional** (decision T-2) — not a
  lifting-surface solution. Deliberate: it makes every closure target analytic
  (below), and the base-method uncertainty band already covers the shape
  difference.
- **Tail inertia is signed by `−n` unconditionally** (decision T-9). The
  intuitive "inertia opposes air load" rule is wrong for a tail in the
  unconservative direction: the conditions that size a GA horizontal tail are
  down-load, and an opposing rule would relieve exactly them.
- **The attachment stations are geometry, not load** (T-8a): no Appendix A
  figure moves with them, so the h-tail attachment is a single owner returning
  stations *with their provenance*, and the consumer reads the stated basis
  rather than inferring one.
- **Conditions publishing no control-surface load of their own** get one
  *derived* by integrating the aft-of-hinge block, and every artifact marks it
  derived — derive-and-mark, never silently filled.
- **The one-engine-out transient is explicit Euler** at the entered time step,
  with the manual's thrust/windmill schedule (Glauert windmill drag); its twin
  oracle is deferred (above).
- The lateral *airplane* response built on these fin loads (n_y, ψ̈, ṗ, the
  wing-body sideslip term and its conservatism statement) is chapter 9's; the
  fin's own inertia relief and its stated unconservative direction is
  chapter 10 §fin-inertia.

## How it is validated

Appendix A gives the tail's **totals** (SELECT) and its **chordwise** profile
(TAILDIST) and stops — both oracle-locked per the hub's rows. Everything
spanwise is gated by the closure set below (moved from the hub; steps T1–T7,
2026-08-08/13), whose strength is that every target is **analytic** rather
than a re-run of the quadrature. Gates in `tests/test_tail_span.py`.

### The spanwise closures (T1–T5)

Per strip `j` of the **whole** planform area `S`, with `LT25`/`LT50` read
from SELECT and never recomputed (T-7):

    w25 = k_side·LT25·(c_j·dy)/S      w50 = k_side·LT50·(c_j·dy)/S
    fz  = w25 + w50                  tor = w25·(x_lra − x_25) + w50·(x_lra − x_50)
    fi  = −n_n·W_surf·(c_j·dy)/S     (d'Alembert, T-9; n_n = the surface's own normal-axis factor)
    fa  = −n_a·W_surf·(c_j·dy)/S     (axial along the span — the vertical tail only)

`W_surf` is derived from the `htail`/`vtail`-tagged `weight.items`, not
entered (chapter 10).

| Closure | Analytic target | Why it is not a tautology |
|---|---|---|
| **Force** | Σ air = `LT25 + LT50` exactly | The target is SELECT's own total; a factor-of-two in the half/full bookkeeping lands here |
| **Bending** | root = `L_half · ȳ`, with `ȳ = (b/3)(c_r + 2c_t)/(c_r + c_t)` | The centroid is computed from the planform, not from the load table |
| **Centreline rolling** | `(L_RH − L_LH)·ȳ` — **identically zero for every symmetric case** | The gate the full-span topology buys; a per-side deck cannot state it, and a mirrored-wrong half or mis-signed side scale is invisible to a force sum |
| **Torsion** | `(LT25+LT50)·x̄_lra − LT25·x̄_25 − LT50·x̄_50`, area-weighted | Assembled from area-weighted chordwise means, a different computation from the per-strip sum |
| **Inertia** | Σ = `−n·W_surf`, **signed by `n` alone** | Companion test asserts a *down*-load case comes out **larger** in magnitude than air alone |
| **Reduction** | LRA at 25 % chord ⇒ the `LT25` torsion term vanishes identically | Same property the wing's LRA transfer is pinned by |

All six closures are additionally checked against a **tapered and swept**
planform, because every shipped fixture takes the derived rectangle — without
that, the torsion transfer term (identically zero on an unswept surface)
would never be exercised. Deck-side, the same conditions are gated twice
more: the invariant sweep gains a spanwise h-tail row (force, and the
centreline rolling moment: zero symmetric, non-zero for 23.427(a)) and a
v-tail row (the load is `Fy` and the torsion `Mzz` — a force-only check in
the wrong component would still "close"), and the round-trip harness solves
both decks in the real sbeam (chapter 11).

### The discrete control-surface path and the first hinge moment (T6)

Also without a printed oracle, and gated the same way. The control-surface
load itself is **not** new physics — it is SELECT's elevator load and its
rudder counterpart, Appendix-A-locked and here only *read*, decomposed into
the two parts it is the sum of so each can leave the spanwise distribution
from the chord station TAILDIST placed it at. What is new is where that load
enters the structure, and the moment it makes about the hinge line:

    c_e   = (Saft/S)·CAVE                 aft-of-hinge chord              (TAILDIST)
    e     = c_e/3                         centroid of the aft-of-hinge block
    HM    = L_cs·e                        the hinge moment
    hinge i: F_i = k_side·L_cs·t_i        chord-weighted tributary, Σ t_i = 1
             M_i = F_i·(x_lra − x_hl)
    actuator: M_a = −HM

**The third is exact, not a rule of thumb.** TAILDIST's net trailing-edge
pressure is identically zero, so the pressure block aft of the hinge line is
*always* a triangle running from its hinge-line value to nothing — whatever
the condition, whatever the deflection — and a triangle's centroid is a third
of its base. That is what lets the suite's first hinge-moment output be gated
by a closed form instead of a quadrature.

| Closure | Analytic target | Why it is not a tautology |
|---|---|---|
| **Cross-mode force** | `ΣF(discrete) == ΣF(smeared)`, `rel_tol 1e-12` | The identity is a property of the *construction* (exactly `L_cs` removed, exactly `L_cs` applied), not of the strip quadrature |
| **Hinge set** | `Σ F_hinge == L_cs`; the actuator carries no force at all | The load arrives from SELECT and is shared by a tributary rule the test derives independently |
| **Chordwise identity** | hinge torsion + actuator couple = `L_cs·(x_lra − x_cp)`, `x_cp = x_hl + c_e/3` | Reverse the actuator's sign and the sum lands on the hinge *line* — a 4.86 in chordwise error on ga6 with nothing else in the deck to notice it |
| **Cross-mode torsion** | moves by exactly `att·x_25 + cam·x_50 − L_cs·x_cp` | Stated as an identity rather than "within a tolerance", so the difference is *explained* rather than merely bounded |
| **Mode isolation** | no attachment geometry ⇒ every shipped deck and Imperial digest unchanged | The default path is pinned byte-for-byte, so a discrete-mode defect cannot leak into the mode nobody selected |

### The T-tail transfer (T7)

A rational-pairing decision (T-5) rather than a closure: for each v-tail
case, the **balancing** horizontal-tail load at that case's own V-n point
plus that point's h-tail inertia, carried at the fin's last node. Its gate is
a free-body statement read from the deck's own card text — the fin deck's
resultant about the origin equals the v-tail-only resultant plus the
transferred set at its stated node — plus byte-level gating isolation: flip
`tail_type` back to conventional and the deck returns exactly.
`concept_regional_jet` is the suite's only T-tail fixture. The asymmetric
T-tail transfer method of record is `docs/30_future/51_ttail_asymmetric_transfer_note.md`.

### One engine out

Closure-locked: each step exact to `ONENGOUT.BAS` (thrust, windmill drag, the
two tail-load terms, the moment equation and the integration), plus the two
twin-turboprop fixtures executing the module end to end in
`tests/test_one_engine_out.py`. The printed twin oracle remains a deferred
item, recorded as such in the hub's provenance table.

## Sources

- Reference 1 Ch 9 (SELECT — tail criticals), Ch 10 (TAILDIST), Ch 11
  (ONENGOUT); Appendix A oracle pages per the hub's per-module rows.
- FAR 23.367, 23.421–23.427, 23.441–23.445; AC 23-9 (T-tail method, note 51).
- `docs/30_future/51_ttail_asymmetric_transfer_note.md` — the T-tail
  asymmetric transfer design note.
