# sloads complies with sstandards Rev A: the conformance test, the statement and the recorded deviations (design note 68)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-10-03** (owner, in session, under the solo profile —
rule 1's working-alone branch). PROPOSED the same day; the owner ruled **Q1 and
Q2 of §5 as recommended** (the `moment_transfer` block is a skip, not a
deviation, and the vendored vectors live at `tests/data/sstandards_rev_A.json`),
so D-68.1…D-68.7 stand as written. Drafted for **#354** (tier L, milestone 0.8.9),
filed from the 2026-10-03 sconfig/sstandards process review. sstandards Rev A
(issued 2026-10-03, `../../../sstandards/CONVENTIONS.md`) is the shared
frames/signs/units standard for the sconfig → sloads → sbeam chain; its §8
lists sloads as "pending" against a backlog item that was never filed. This
note settles which conformance-vector blocks bind to which sloads code owners,
which blocks are skipped and why, and the two recorded deviations — the
questions #354's acceptance leaves open. Implementation is one tier-L step on
`dev/v0.8.9` after this note is AGREED.

**Tier L.** A contract is adopted (an external standard becomes citable
authority), a test file is added, and `CONVENTIONS.md` gains a compliance
statement. **No delivered load moves.** No calc module changes, no constant
changes value, no shipped digest changes — the two places sloads differs from
Rev A are *recorded as deviations*, never edited (§3).

**Conventions:** `CONVENTIONS.md` §1 (the sloads frame this note shows equals
sstandards frame A), §2 (units channels), §7 (single-source owners — every
binding below names one). **Precedent:** sconfig's `tests/test_sstandards.py`
(the first adopter: constants, angles, mac, percent_mac tested; frame_A_to_B
and moment_transfer skipped with reasons); note 61 CV-1 (today-content lands in
`10_standard`, so the compliance statement lives in `CONVENTIONS.md`, not here).

## 1. Measurements (2026-10-03, at `dev/v0.8.9` after #333)

- **The frames already agree.** sstandards §1 frame A is +x aft, +y right,
  +z up, inches; §6.1 says frame A **is** NASTRAN basic CID 0 with an identity
  transform. `CONVENTIONS.md` §1 and `export/coordinates.py` state exactly
  that today (`SBEAM_CID = 0`, identity). Nothing moves.
- **The §6 boundary is already guarded.** Consistent N·mm·t·s deck units:
  `units.deliverable_units` (§6.2). Loads as physical FORCE/MOMENT in CID 0:
  the export channel with G-OR-71/72/73 (§6.3). These guards predate Rev A;
  the conformance test does not duplicate them, it cites them.
- **`sloads/constants.py` against the `constants` vector block (rel_tol 1e-5):**
  `G = 32.174` passes (1.5e-6 from exact, admitted by the block's own note);
  `KT_TO_FPS = 1.6878099` passes; **`RHO_SL = 0.002378` fails** (0.045 % from
  ISA 0.0023769) and **`KT_TO_FPS_SUITE = 1.15·88/60` fails** (0.068 % from
  exact) — both kept deliberately so the ported BASIC programs reproduce their
  printed Appendix A oracles (`constants.py` says so in place).
- **MAC has an owner:** `derived_geometry.mac_reference` /
  `pct_mac_to_station` (the `mac` and `percent_mac` blocks, §4.1/§4.2).
- **No frame-B code exists.** sloads carries no flight-mechanics
  stability-axes transform; every delivered quantity is frame A (§2.2 block
  has nothing to bind to).
- **No single vector moment-transfer helper exists.** The ported modules
  compute per-axis scalar moments as the `.BAS` listings do, and those paths
  are oracle-locked (the backlog invariant: no calc-math change to the FAR23
  path). Rerouting them through one `M = (r − o) × F` helper (§1.4) would be
  a calc-math change far beyond #354.
- **The dangling pointer:** sstandards §8 and its README cite "sloads backlog
  R5", which does not exist; the row must cite #354.

## 2. Decisions

- **D-68.1 — the statement.** `CONVENTIONS.md` §1 gains one line:
  `Complies with sstandards Rev A` with a link, the deviations table (D-68.5)
  beside it. `CONVENTIONS.md` keeps only sloads-specific conventions'
  authority; for the shared set it defers to sstandards. No existing section
  is deleted in this step — pruning duplicated shared prose is follow-on
  hygiene, not closure.
- **D-68.2 — the vendored vectors.** `conventions_vectors.json` at Rev A is
  **copied** to `tests/data/sstandards_rev_A.json` (the sstandards README's
  own path convention; copied, never imported or fetched — sstandards §0.1).
  A new revision lands as a new file beside it, adopted as its own tier-L item.
- **D-68.3 — blocks tested, and their owners.**

  | Block (§§) | sloads owner | Tolerance (from the block) |
  |---|---|---|
  | `constants` (5.7) | `sloads/constants.py` (`G`, `KT_TO_FPS`, …) and `sloads/units.py` conversion factors | rel 1e-5, deviations excepted |
  | `angles` (5.4) | the deg↔rad boundary (`math.radians`/`math.degrees` as used by `units.py`) | rel 1e-12 |
  | `mac` (4.1) | `derived_geometry.mac_reference` | per block |
  | `percent_mac` (4.2) | `derived_geometry.pct_mac_to_station` | per block |

- **D-68.4 — blocks skipped, with recorded reasons** (sstandards §0.2 allows
  a skip; sconfig set the precedent):
  - `frame_A_to_B` (2.2): sloads has no frame-B code; every delivered
    quantity is frame A.
  - `moment_transfer` (1.3/1.4/3.2): the ported FAR23 modules compute scalar
    per-axis moments per the `.BAS` listings and are oracle-locked; the
    export channel is the §6.1 identity, so no transfer code exists to bind.
    Recorded as a **skip**, not a deviation — sloads does not disagree with
    §1.4's result, it has no single helper to point the vectors at.
- **D-68.5 — the deviations, recorded in both places** (sloads
  `CONVENTIONS.md` and sstandards §8, per sstandards §0.2):
  - **D-SL1:** `RHO_SL = 0.002378 slug/ft³` (vs ISA 0.0023769), kept so the
    ported programs reproduce the printed oracles.
  - **D-SL2:** `KT_TO_FPS_SUITE = 1.15·88/60 ft/s per kt` (vs exact
    1.6878099), same reason; the exact `KT_TO_FPS` exists beside it for
    everything non-suite.
  - The conformance test asserts the deviations **at their deviated values**
    — a drift guard in both directions: toward ISA breaks the oracles, away
    from the recorded value breaks the record.
- **D-68.6 — the sstandards side.** The §8 sloads row becomes
  `A / conformant / D-SL1, D-SL2` citing #354, and the README compliance
  table follows; "backlog R5" disappears. (sstandards edits ride the same
  step; sstandards is a separate repo, so its commit is the owner's.)
- **D-68.7 — no calc change, restated as a gate.** If any vector outside
  D-SL1/D-SL2 fails against its owner, the failure is filed as its own issue
  and resolved there — this step never edits a constant or an equation to
  make a vector pass.

## 3. Validation

- `tests/test_sstandards.py` green: four blocks tested against the D-68.3
  owners at the blocks' own tolerances; two blocks skipped, each skip
  asserted present with its D-68.4 reason string; D-SL1/D-SL2 asserted at
  their deviated values.
- Appendix A oracles, the twin closure locks and the full suite unchanged —
  the step touches no calc path.
- `test_doc_currency.py` / `test_doc_links.py` green after the
  `CONVENTIONS.md` edit (the Rev A citation is provenance, not a volatile
  number; the cross-repo link is cited as a path, not an in-repo link).

## 4. Affected code and docs

`tests/test_sstandards.py` (new), `tests/data/sstandards_rev_A.json` (new,
vendored), `docs/10_standard/CONVENTIONS.md` (statement + deviations table),
`docs/20_theory/00_theory_sources.md` (sstandards Rev A listed as a cited
source), one `changes/<slug>.history.md` fragment in full step format
(tier L). In sstandards: `CONVENTIONS.md` §8 and `README.md` (D-68.6).

## 5. Resolved questions (owner, 2026-10-03, both as recommended)

- **Q1 — `moment_transfer` is a skip, not a deviation.** A deviation asserts
  a different answer; sloads gives the same answer by a different route (the
  oracle-locked scalar per-axis paths). D-68.4 stands as written.
- **Q2 — the vendored vectors live at `tests/data/sstandards_rev_A.json`.**
  The sstandards README's own path, kept for cross-project likeness over
  house fixture naming. D-68.2 stands as written.
