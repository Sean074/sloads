## Step — Each SELECT wing slot runs at every FLIGHT mass state and the net-governing run is the delivered case; MZFW seeds the zero-fuel cases with their loadings (#292, design note 63 D-63.5 and D-63.7, tier L, 2026-09-18)

**Objective.** Close the second half of design note 63: after #289 every
inertia load read its case's loading, but every wing slot was still
delivered at the mass state of its own V-n point's CG case, so a slot whose
air pick sat at MTOW was never assessed at zero fuel, where the wing fuel's
relief is gone and root bending is highest; and no case reached the
zero-fuel state at all, because nothing seeded one. This is the variants
step of the R-63.4 scope split (ruled 2026-09-17), landing directly after
#289 and before the loading editor #290.

**Deliverables.** **The seeds (D-63.5).** `cg_cases.max_zero_fuel_weight`
owns `weight.max_zero_fuel_weight_lb` in the MLW shape (`0` = not entered,
refuses when required, the estimate `max_zero_fuel_weight_estimate` = OEW +
max payload offered and never written; the design-weight ordering chain
reads it). When it is entered, `seed_flight_cases` appends `mzfw aft`,
`mzfw fwd` and `full fuel aft` (`MZFW_CASE_NAMES`) **with their loadings**:
`mass_distribution.seed_loading_search` is the third search objective
beside the exact-subset search and the ground burn-down — over the payload
subsets (consumables off, or every consumable row at 1.0) it takes a
whole-row loading that is inside the limits as it is and **clips** one
that is not, scaling one payload row by the largest fraction that brings it
under the cap (MZFW, or MTOW for the full-fuel seed) and inside the aft and
weight-dependent forward lines (`validation.wtenv_fwd_cg_limit_line`, the
forward limit resolved once as a callable); the aft seeds take the heaviest
such loading, ties aft-most, the forward seed the one nearest the forward
line, ties heavier; the database's own ballast row is payload; a seed
coinciding with a case already seeded (D-25a's weight band, the search's
0.5 in, `echo_weight_tolerance` / `cg_match_tolerance`) is not written.
`LoadingDefinition.fractions` accepts any discretionary row, not only a
consumable one — a part-filled hold is a loading. **The variants
(D-63.7).** `modules/wing_variants.py` (pure, unregistered, never
persisted) assesses every slot at every FLIGHT case: `select.wing_slot_picks`
applies each family's own criterion within the points balanced at the
case, `wing_mass_state` gives the case's loading, one `fold_units` per
case, and air + inertia root `Mxx` is the comparison (unchanged by the LRA
transfer). `select_wing` delivers each slot at the governing run — the
extreme signed root `Mxx`, largest for the positive-lift slots and most
negative for the negative ones (`SLOT_LIFT_SIGN`) — under the slot's W id,
with the run key naming the point and a `note` naming both runs where it
moved; SELECT.BAS 3000's search over the whole matrix stays as
`select.air_picks`. Three in-code amendments to D-63.7, recorded in note 63
§11: the torsion and load-factor slots (`AIR_PICK_SLOTS`: TORS, PNZ, NNZ)
keep their air pick because their criterion is not the bending; a variant
within the FLTLOADS balance's own noise of the air pick
(`GOVERNING_TIE_REL`, 0.5 %) is a tie the air pick keeps; the coincidence
rule is applied to the delivered set, not within each case. **The
filter.** `wing_inertia.resolve_wing_cases` reads an entered
`wing_mass.cases` list as a filter on the slots: a case naming a slot with
no `case` of its own takes the slot's delivered point, so its mass state,
CG and run key follow the selection; every fixture's hand-entered
nz/nx/CL/V are gone (the ACRL couples stay; the Baron's `aft gross` pins
of #289 go with them). **The fixtures.** MZFW entered on `atr42_100`
(33,510 lb), `baron_58` (5,270 lb) and `concept_regional_jet` (29,500 lb)
and their FLIGHT cases re-seeded (the Baron's hand cases keep, its two
MZFW cases appended); `ga6_normal` keeps its four Appendix A cases so the
oracle's V-n numbering does not move. **The surfaces.** The Flight
Envelope page's SELECT sub-tables and the `select` CSV gain `CG case` and
`Run` (`report.critical_rows`); the report's §3.2 prints the slot × case
variant table with the governing row marked and its provenance sentence
states that an entered list is a filter; the balanced deck's subcase mass
set follows the delivered run's CG case by construction. `PROGRAM_SPEC.md`
(payload_cases, SELECT, NETLOADS), `ch04_wing_loads.md`,
`theory_sources.md`'s SELECT row, `04_far25_gap_analysis.md` (25.321 to
**A**), the data dictionary and note 63 (SHIPPED, §11) state it.

**Test.** **G-63.2** (`test_one_mass_model.py`): on `atr42_100` and
`baron_58` the PHAA net root bending at the zero-fuel state exceeds the
full-fuel state's at equal air load and NHAA's inequality reverses.
**G-63.3:** the variant table holds every slot × FLIGHT-case row SELECT
can pick, exactly one governing per slot, the delivered condition is the
governing run, the balanced deck's `$` header names the same run key and
its case is the same CG case. **G-63.3a, the rest:** across a full run no
two `CaseRef`s share a run key with different loads, no W id is carried by
more than one run, on `ga6_normal` every slot's governing run has the run
key of its air pick, and `select.air_picks` on the GA6 asserts the six
Appendix A points unchanged — the note 62 pick tests read `air_picks` too.
The seed: the ga6 in-memory seeds, the ATR's `mzfw aft` (28,410 lb, the
aft hold clipped to 853 lb, note 63 §8.3's row), the coincidence skip, the
clip-not-trim rule, the fraction on a payload row, the MZFW refusal and
chain. One Imperial digest wave: 20 channels on the ATR, 20 on the Baron
and 21 on the jet (the V-n matrix, SELECT, WINGINER, NETLOADS, the balance
and its decks, the mass model, `body_loads`, the case index — the seeded
cases and the re-pointed slots); **one** on `ga6_normal` and one on the
heavy, the `select` CSV with its two new columns — every other GA6 channel
byte-identical, the oracle lock in one number. The balance pins move with
the Baron's eight newly assembling wing slots (its symmetric force ratchet
1.29 % at NLAA on `mzfw fwd`, its NHAA clamped, two closure `Izz` added)
and the jet's NMAA at `fwd regardless`.

**Key decisions.**
- **The ATR does not move; the Baron does.** With the MZFW cases in its
  matrix the ATR's MTOW forward pick still governs every slot — §8.4's
  finding, PMAA 5,850 against `mzfw aft`'s 5,750 ×10³ in-lb (its wing fuel
  sits at 25 % MAC and the zero-fuel loading is 8,400 lb lighter). On the
  Baron seven of nine slots move: PHAA, PLAA, PMAA, ACRL and NHAA to
  `mzfw aft` (PHAA root Mxx 504 → 564 ×10³ in-lb, +12 %), NMAA and NLAA
  to `mzfw fwd` (+36 %, +26 %). The jet's NMAA moves 1.2 %; the heavy has
  one case.
- **TORS, PNZ and NNZ are delivered at their air pick.** Governed by root
  `Mxx` the GA6's Appendix A TORS moved from case 18 to case 38 (+5.7 %)
  and the ATR's PNZ to a mid-gross MAN D point that is not the load-factor
  extreme. A slot's id names a criterion; the variant table still assesses
  those slots and lists them.
- **A 0.5 % tie band, not `TIE_REL`.** The balance's own noise; without it
  the GA6's NLAA re-pointed on 0.44 % and G-63.3a's GA6 clause failed for a
  difference the method cannot resolve. `theory_sources.md`'s base-method
  band (5–10 %) ranks work and does not gate a test, so it is not the
  number used.
- **Clip, do not optimise.** A first draft trimmed rows to improve the
  objective and produced a fifth of a copilot on the GA6; the shipped
  search trims only a loading that is outside, by the least it takes.
- **`ga6_normal` carries no MZFW.** Its seeds are asserted in memory; the
  §8.1 sample's `mzfw fwd` (copilot only) was a hand reading — the search's
  answer coincides with CG4 and is skipped.
