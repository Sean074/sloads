# Down-select on the ultimate basis; deliver LIMIT (design note 58)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-09-11** (owner, in session, under the solo profile —
`DEVELOPMENT_PROCESS.md` §0; rule 1's working-alone branch). The rulings in
§2 are the owner's, taken in chat on 2026-09-11. This note **re-scopes and
closes #193**: the down-select half ships here; the deliver-at-ULTIMATE half
is **decided, not done** (D-58.1).

**Tier M.** A behavior change to an existing capability — the basis on which
one load case is ranked against another — with **no delivered load value
changing** on any shipped fixture (§4 gate 1 measures it). The load-output
contract (note 49) is not reversed; it is confirmed.

---

## 1. Measurements (2026-09-11, at `dev/v0.8.3`)

### 1.1 The defect, and where it can live

An envelope or governing-case pick taken over cases whose *prescribed* factors
differ is a maximum of quantities that are not comparable: a 2,000 lb LIMIT
case at SF 1.5 sizes more structure than a 2,500 lb case at SF 1.0, and a
raw-magnitude pick names the second. The only in-suite ULTIMATE family is the
23.367(a)(2) engine-failure set (`safety_factors` classifies 23.561(b) too,
but `report/coverage.py` records it `in_suite=False` — no producer emits it),
so a mixed set exists exactly where the OEI v-tail conditions compete: the fin
critical set after note 44 OR-172's admission (`select._with_engine_failure`),
and the OEI family **internally** — its VC case is ULTIMATE SF 1.0 beside its
VD/VS cases at 1.5 (`one_engine_out._load_cases`).

### 1.2 The full site inventory (production code)

A complete sweep of every cross-case ranking or reduction in `sloads/`, `app/`
and `oracle_app/` found:

* **One mixed-factor reduction**: the Loads Plots page's two-sided pointwise
  envelope (`app/views/loads_plots.py:217` and its CSV twin at `:288`),
  through the shared owner `report/render.py::envelope_extremes`. For the
  v-tail it envelopes the chordwise sets of `default_critical` — SF 1.0 OEI
  curves against SF 1.5 SELECT curves — on raw LIMIT magnitude, publishing
  the result as an unlabelled "envelope" trace and CSV row that reads no
  `safety_factor` at all.
* **Every other site is uniform**: SELECT's per-family picks, the gear
  `critical_reaction`, the wing/fuselage station-extremes tables
  (`content._station_extremes_table` — the OEI conditions are
  `component="vtail"` and never enter `build_net_loads`/`build_body_loads`),
  and every within-one-result or geometry pick. `tail_span` and `taildist`
  build one result per condition and reduce across nothing.
* **The governing-fin statement** (G-OR-113: sections 6 and 11 name the same
  critical case) is asserted by its gate with a raw-LIMIT `max` — test-side,
  not production, but it is the pick of record for the admission and carries
  the same basis defect.

### 1.3 The effect on shipped content is zero

Measured on both twins: the 23.367(a)(1) VD case dominates the fin set **on
both bases** — `baron_58` 2,155.8 lb LIMIT / 3,233.7 ult against the ULTIMATE
case's 1,489.1; `atr42_100` 12,829.3 / 19,243.9 against 9,045.8. For a pick to
flip, the ULTIMATE case would need to come within 1/1.5 of the largest LIMIT
case; today it is ~2.2× away. No shipped pick, envelope edge, digest or report
byte moves under this note — which is gate 1.

### 1.4 A neighbouring defect, found and filed separately

The summary report's v-tail *governing conditions* table reads
`ComponentLoads.critical` built from `build_critical` (no OEI rows), while the
chordwise table beside it renders `default_critical`'s set (with them) — two
tables in one section disagreeing about the condition set. That is a
set-membership defect of the OR-172/OR-174 two-consumers class, not a
ranking-basis defect, and it is filed as its own issue rather than folded in
(rule 5).

---

## 2. Owner rulings (2026-09-11, in chat)

1. **Delivered loads stay LIMIT, permanently.** The attempt to deliver
   factored output was problematic in development; the oracle GUI's posture —
   everything LIMIT, the SF stated and applied nowhere — is the contract, and
   every output aligns with it. This closes #193's deliver-at-ULTIMATE half
   **decided, not done**: note 49 OR-116 stands by ruling rather than by
   default, and the double-factoring class it killed stays dead. (Reverses
   the owner's 2026-09-07 stated intent, deliberately, by the same owner.)
2. **Every comparison between load cases is made on the ultimate basis** —
   `|value| × prescribed SF` — wherever a governing case is named or a
   reduction is taken across cases. On a uniform-factor set this is the raw
   ranking by construction, so nothing moves anywhere factors agree.
3. **Fix it everywhere**, i.e. structurally: one owner for the basis, and the
   one mixed-capable reduction made unable to compare across factors silently.

---

## 3. Decisions

| # | Decision | Alternative rejected |
|---|---|---|
| **D-58.1** | **#193 closes re-scoped.** The down-select half is this note; the conversion half is decided-not-done per ruling 1. The backlog Mission's "#193 is the standing proposal to reverse this" clause is removed — there is no standing proposal. | *Keep the reversal parked with an activation.* Rejected by ruling 1: the owner has decided the destination, not deferred it. A future consumer that wants factored decks raises a new question against a stated decision, which is what the register is for. |
| **D-58.2** | **`safety_factors.ultimate_basis(value, safety_factor)` is the comparison-basis owner** — `abs(value) × SF`, the quantity structure is sized to. Governing-case naming across load cases keys on it (through `picks.extreme` where a pick is published, keeping the platform-stable-tie rule). `safety_factors` owns it because the factor semantics live there (M4-8/G-11); `picks` keeps owning tie mechanics. | *A free function beside `extreme`.* Rejected: the rule is about what a factor means, not about picking; splitting it from the governing table re-creates the two-owners drift #239 exemplifies. |
| **D-58.3** | **A pointwise envelope is a same-basis construct.** `envelope_extremes` takes the per-series factors as a **required** argument and **refuses a mixed-factor selection by name** (`safety_factors.uniform_factor` decides "same basis"); the caller renders the per-case curves and states in band why the envelope is withheld. Rationale: an envelope publishes *values*, and there is no honest mixed value to publish — the LIMIT envelope is not a governance statement across differing SF, an ultimate-scaled trace would deliver a factored load (G-OR-71's class), and the LIMIT values of ultimate-basis winners draw a non-enveloping curve. Flagged, never defaulted. | *Label the mixed envelope instead of withholding it.* Rejected: the trace's whole meaning is "the governing edge"; a caption cannot repair a curve whose construction answers the wrong question. *Scale to ultimate for display.* Rejected: it publishes a factored load, reversing note 49 for one trace. |
| **D-58.4** | **G-OR-113 re-keys to the ultimate basis** and gains the pin that no shipped governing pick changes (§1.3's numbers); a synthetic mixed set where the two bases disagree gives the rule its teeth. | *Leave the gate at LIMIT.* Rejected: the gate is the pick of record for OR-172's admission, and it encodes the defect. |
| **D-58.5** | **`envelope_extremes` keeps publishing raw values via plain `max`/`min`.** The platform-stable-tie rule (`picks.extreme`) protects *pick identity*; a pointwise value envelope publishes no identity, and `max` over floats is deterministic. Stated so the exemption is deliberate. | — |

---

## 4. Gates

1. **No delivered byte moves.** All digests, baselines and report fixtures
   byte-identical — §1.3 measured why, this proves it.
2. **The teeth test**: a constructed set where an SF 1.0 case beats an SF 1.5
   case only on the ultimate basis — the governing pick names it, and the
   envelope refusal fires with the factors in the message.
3. **The no-flip pin**: on `baron_58` and `atr42_100`, the governing fin case
   is the same on both bases, asserted with §1.3's margins so a fixture that
   closes the gap announces itself.
4. **The structural guard**: `envelope_extremes` cannot be called without
   factors (signature), and the mixed-refusal branch is exercised in CI.
5. **G-OR-113 holds re-keyed** — sections 6 and 11 still name the same
   critical fin case, now on the basis the structure is sized to.

---

## 5. Effect vs error bar (rule 6)

No delivered load changes (gate 1); the ranked effect today is zero (§1.3).
The justification is the correctness of the *rule*, bought while it is free:
the first fixture or entered project whose ULTIMATE case comes within 1.5× of
its largest LIMIT case gets the right governing statement instead of a wrong
one nothing would have flagged.

## 6. What this supersedes / touches

* **#193** — closed by this note's implementation (D-58.1); its band-B2 row
  leaves the table; `CLAUDE.md`/backlog Mission prose drops the
  standing-proposal clause.
* **Note 49** — confirmed, not amended; G-OR-71/72/73/74 untouched.
* **§1.4's set-membership defect** — filed separately, not fixed here.
* **`CONVENTIONS.md` §7** — a row for the comparison-basis owner + guard.

## 7. Closure obligations (tier M)

`changes/<slug>.changed.md` + one-paragraph `changes/<slug>.history.md`;
`CONVENTIONS.md` §7 row and the load-output contract's selection sentence;
`CLAUDE.md` load-output summary only if its prose names #193 (it does not —
the backlog Mission does, and that clause goes); `docs/00_INDEX.md` row
*(landed with the note)*. No `theory_sources.md` citation — no equation
changes; gate 1 is why.
