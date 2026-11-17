# Validation Rationale — Why the Results Can Be Trusted

A loads tool is only as good as the evidence that its numbers are right. This
page states, for a user, **what that evidence is, how it is kept, and where its
limits are**. It is a map: every claim links the document or test that owns it,
and nothing here restates a number an owner already states.

## 1. The claim, and what it is measured against

sloads replicates the **FAR 23 LOADS** suite (H. C. McMaster; FAA report
DOT/FAA/AR-96/46). The suite's manual prints a complete worked airplane — the
six-place GA single of Appendix A — and that printed output is the reference:
a module is correct when it reproduces the manual's printed figures.

The comparison is made at a tolerance of ±0.1 %, with the printed number and
its page kept in the test that asserts it. The equations are written in modern
form (`math.pi`, no single-precision constants), so the tolerance absorbs the
original's rounding and nothing larger.

## 2. Two kinds of evidence

Every analysis module carries exactly one of two gates. The vocabulary is
defined in [Chapter 1 §1.6](ch01_introduction.md), and the status of each
module is stated once, in
[Theory & Equation Sources §Oracle status](00_theory_sources.md#oracle-status).

- **Oracle-locked.** The module's output is asserted against the printed
  Appendix A figures within the tolerance, page-cited.
- **Closure-locked.** Where no printed figure exists — the twin-engine paths
  (Appendix B is not in the available copy of the manual) and everything concept
  mode adds above the printed airplane — the gate is a stated physics invariant:
  an equilibrium that must close, an integral that must equal a known total, or
  agreement with an independent producer of the same quantity.

The split records *what the evidence is*; it is not a quality ranking. An
analytic closure is often stronger evidence than a three-figure page match.

**No module ships without a gate.** The mapping from each registered module to
its gate tests and its printed source or invariant is
[`tests/module_gates.py`](../../tests/module_gates.py), and the suite fails if
a module registers without a row, if a named gate test disappears, or if an
oracle's page citation leaves its test.

## 3. Keeping the reference honest

A test that can never fail is not evidence. Two rules, stated in
[§Oracle provenance and gate independence](00_theory_sources.md#provenance),
guard against that:

- **Provenance.** Every reference number states where it came from —
  transcribed from the printed page, or not available — so a reference cannot
  quietly shrink to the cases that happen to pass.
- **Independence.** No gate re-derives the rule it checks, and no input is
  back-solved from the output it is meant to validate.

Where the manual itself is wrong, the tool does not silently follow it or
silently depart from it. Each deliberate deviation is approved, cited to an
authority, and listed in the
[register of approved corrections](02_approved_corrections.md); the test keeps
the manual's original figure beside the corrected one.

## 4. The assembled airplane and the exported deck

Module-level agreement does not by itself show that the delivered load set is
consistent. Three further checks act on the assembled result:

- **Balanced-airplane closure.** Each assembled case is a free-free airplane
  in equilibrium. Its out-of-balance residual is measured *before* it is
  closed, gated against stated acceptance bounds, and reported as part of the
  deliverable. The method, the bounds and the record are in
  [Chapter 9](ch09_balanced_airplane.md).
- **Card-text equilibrium.** The exported sbeam deck is summed *from its own
  card text* and closed against `nz × W` — without the safety factor, because
  every delivered load is LIMIT. See [Chapter 11](ch11_export_sbeam.md).
- **Solver round-trip.** The exported decks are solved by the real sbeam solver
  and the recovered internal loads are compared with sloads' own, so the deck is
  verified as the solver reads it, not as sloads wrote it
  ([Chapter 11](ch11_export_sbeam.md)).

The LIMIT contract itself is gated: the suite scans for any place a safety
factor is multiplied into a delivered number, and checks that every artifact
states the factor it did not apply
([Theory & Equation Sources](00_theory_sources.md), §Limit vs. ultimate loads).

## 5. When the checks run

All of the above are automated tests, and they run on every change: the oracle
and closure gates, the equilibrium checks and the drift guards in the main
suite, and the solver round-trip as its own job. A change that moves a
validated number cannot merge. The workflow definition is the authority for
what runs: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).

## 6. What validation does not claim

Agreement with the manual shows the *method is implemented correctly*; it does
not make the method more accurate than it is. The base method is a rigid
airplane, balanced at discrete points of the V-n envelope, with approximate
spanwise airloads. Its own uncertainty against a higher-fidelity analysis is
stated in
[§Base-method uncertainty](00_theory_sources.md#base-method-uncertainty), and
each theory chapter lists its own assumptions and limitations.

Concept mode extends the method to airplanes larger than the printed example.
It reduces exactly to the validated core on GA inputs and is closure-locked
above it; it has no printed reference of its own.

A per-module validation matrix — source page, printed value, computed value
and tolerance for each gate — is planned as a generated companion to this page
(issue #413). Until it exists, `tests/module_gates.py` is the complete
per-module statement.
