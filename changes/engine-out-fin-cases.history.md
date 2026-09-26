## Step — The one-engine-out fin reaches the deck: ONENGOUT's peak instant is an assembled lateral case on a 1 g parent with the engine pair beside the fin, and the fin load it publishes now resists its engine's yaw (#285, design note 66 D-66.10…D-66.16, tier L, 2026-09-26)

**Objective.** Close #285: SELECT names ONENGOUT's 23.367 fin conditions on
every twin — on the ATR 3.6x its largest static fin case, the fin and aft
fuselage's sizing load — and the assembler skipped all of them as out of
family, on a deferral to a per-component fin deck that note 56 deleted.

**Deliverables.** A new balanced family, `balance/engine_out_cases.py`,
appended after the engine-mount family: each recovered ONENGOUT condition at
its instant of peak total fin load, assembled on FLTLOADS's 1 g point for the
speed (`BAL C` / `BAL D` / `STALL 1G`) at the heaviest derivable FLIGHT CG case
and the V-n altitude nearest ONENGOUT's, carrying the fin distribution
`tail_span` builds and the engine pair at that instant — the live engine's
thrust at the mirror of the failed hub and the failed engine's remaining
thrust and windmill drag at its hub, from `one_engine_out.engine_forces_at`,
the march's own schedule. One engine's failure is computed per speed; the
mirrored engine's is its reflected twin under its own VT id. No L-7 term, said
in band; unrecovered marches recorded (`not-recovered`). The 23.367(a)(2) cases
state `ULT SF=1.0` through #286's stamp. **The published fin sign is
corrected**: ONENGOUT gave every fin load (and δ, α_tail) the sense that adds
to its own engine's yaw while its β carried the nose's; the fin now resists
(`+y` engine → `+y` fin load, SELECT's static convention) and β keeps the
nose's sense. Magnitudes and the fin envelope are unchanged; which engine's
case carries which sign flips. One Imperial digest wave, 32 channels: on the two twins the balanced and LRA decks, the balance output and the case index gain the family, and the one-engine-out, tail-span, chordwise and v-tail applied outputs move with the sign correction (12 each); on the other three fixtures only the deck headers and the balance text move, for the reworded out-of-family sentence.

**Test.** `tests/test_engine_out_cases.py`: one computed case and its twin per
recovered speed (G-66.8); the closure's yaw is ONENGOUT's ψ̈ after the Izz ratio
to 2–3 % (G-66.9, gated at 5 %); the fin opposes the engine pair, and a
positive β carries a negative fin load; each twin carries the other engine's
own fin load (G-66.10); the ATR's unrecovered VS is recorded (G-66.11); SF 1.0
on 23.367(a)(2) (G-66.14); no L-7 load and the statement in band (G-66.15);
the 1 g half closes inside 1 % (G-66.16); `engine_forces_at` reproduces the
march's engine moment at every instant.

**Key decisions.** (1) The sign correction reverses note 44 OR-173's stated
rule — found because the balanced case is the first place the fin and the
engine met; recorded in note 66 §11 for the owner. (2) The family is exempt
from the trim gate for the engine pair's pitch couple (6.4 % of n·W·MAC on the
ATR's VC case — the pair's axial force at the hub waterline), the powered
cases' standing; the 1 g half is gated instead.
