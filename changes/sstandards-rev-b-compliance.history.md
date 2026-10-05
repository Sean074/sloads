## Step — sloads complies with sstandards Rev B: a conformance test checks sloads' own owners against the vendored vectors, `CONVENTIONS.md` states compliance with the deviations D-SL1 and D-SL2, and the standard's §8 row cites #354 (#354, design note 68 D-68.1…D-68.10, tier L, 2026-10-04)

**Objective.** Close #354. sstandards is the shared standard for frames, signs and units across sconfig → sloads → sbeam. Its §8 listed sloads as "pending (sloads backlog R5)", and no such item had been filed. Note 68 was agreed against Rev A on 2026-10-03. Rev B issued the next day: it changes no frame, sign or internal unit, adds the SI input and output files, and adds five constants. The owner ruled that the step adopts Rev B (note 68 §6).

**No delivered load moves.** No calc module, constant or digest changes. The two places where sloads differs from the standard are recorded as deviations and not edited.

**Deliverables.**
- **The vendored vectors.** `tests/data/sstandards_rev_B.json` is a byte-identical copy of the issued Rev B `conventions_vectors.json`. It is copied, never imported or fetched (D-68.2/D-68.8).
- **The conformance test, `tests/test_sstandards.py`.**
  - Four blocks are tested against their owners, at each block's own tolerance:
    - `constants` against `constants.py` and `units.py`;
    - `angles` against `RAD_PER_DEG`, `DEG_PER_RAD` and `math.radians`;
    - `mac` against WINGGEOM's closed-form `surface_properties`;
    - `percent_mac` against `pct_mac_to_station` and `station_to_pct_mac`.
  - Two blocks are skipped, each with its reason: `frame_A_to_B` and `moment_transfer` (D-68.4).
  - Every `constants` key is decided (D-68.9). It is bound to an owner, recorded as a deviation, or declared ownerless with its reason. The ownerless keys are `rho0_kg_m3`, `us_gal_to_L` and `kt_to_m_s`.
  - §5.5's `lbf_to_N / lbm_to_kg = g0` holds exactly.
  - Rev B's practice clauses (§5.1, §5.6, §5.9–§5.11 and §6) name the existing gates that hold them, and the test asserts that each gate still exists (D-68.10).
- **The statement.** `CONVENTIONS.md` opens with `Complies with sstandards Rev B` and the deviations table. A §7 row records the conformance owner and its gates.
- **The deviations (D-68.5).**
  - **D-SL1:** `RHO_SL = 0.002378`, which is +0.047 % from ISA.
  - **D-SL2:** `KT_TO_FPS_SUITE = 1.15·88/60`, which is −0.068 % from exact and serves `VSF` only.
  - Both are kept so the ported programs reproduce their printed oracles. Both are asserted at their recorded values and outside tolerance, so a deviation that is ever made to conform has to be retired by name.
- **Docs:** `theory_sources.md` cites sstandards Rev B. Note 68 is amended with §6 and marked SHIPPED.
- **sstandards (separate repository, the owner's commit):**
  - §8's sloads row reads `B / conformant / D-SL1, D-SL2`, citing #354.
  - The README status table follows it.
  - "backlog R5" is gone.

**Test.** `tests/test_sstandards.py` has ten tests, all green. The rest of the suite is unchanged.

**Key decisions.**
1. **Rev B, not Rev A.** Certifying against a revision that was superseded the day before would have filed this step's own follow-on.
2. **Totality over the constants.** sconfig's precedent bound a subset of the constants block and passed over the rest. Here every key needs a decision, so a constant added by a later revision fails the test until it is decided, the same way a new block does.
3. **Cite the gates, do not duplicate them.** The §5.9–§5.11 and §6 boundary already has its own gates. The conformance test checks that they exist, and does not re-run their checks.
