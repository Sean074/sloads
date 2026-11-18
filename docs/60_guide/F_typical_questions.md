# Appendix F — Typical questions

The questions a first user asks, each answered by a pointer to the section that
owns the answer. A page's own error messages are decoded in
[Appendix C](C_troubleshooting.md); this page is for the questions behind them.

## About the numbers

**Are these loads limit or ultimate?** Limit, everywhere: on the pages, in the
report, the CSVs and the decks. The two exceptions are marked `-ULT` with
`SF=1.0`. → [Conventions](03_conventions.md);
[`CONVENTIONS.md` §3](../10_standard/CONVENTIONS.md#3-limit-load-contract-stated-never-applied).

**Where do I apply the 1.5?** In your sizing analysis, not here. Each case
states its factor in an `SF` column (or an `SF=` line on a deck subcase), from
the governing safety-factor table the report prints.
→ [GUI user guide §5](../10_standard/GUI_USER_GUIDE.md#5-reading-the-results).

**How do I know the numbers are right?** Run [Appendix A](A_worked_single.md):
the bundled single is the manual's own worked airplane, and its figures are
set beside the printed ones. For what the suite checks, and against what, read
the [validation rationale](../20_theory/03_validation_rationale.md).

**Why does my result differ from the manual's?** First suspect an input:
re-load the untouched example and compare. Where sloads departs from the
manual on purpose, the reason is in the
[approved corrections](../20_theory/02_approved_corrections.md).

**Which case governs my wing?** SELECT picks the critical conditions on the
[Flight Envelope](05_flight_envelope.md) page; the report's case index lists
every case with its identity ([Appendix A §3](A_worked_single.md#3-read-what-it-delivers)).

**Which way is positive?** Axes, signs and the loads reference axis are in
[`CONVENTIONS.md` §1](../10_standard/CONVENTIONS.md#1-frames-and-axes).

## About the airplane

**Can I use it for an airplane over 12,500 lb, or a jet?** Yes, in concept
mode, with the limits the
[Scope and limits](../20_theory/04_scope_and_applicability.md) page states.
[Appendix E](E_worked_concept.md) works a 48-seat twin through.

**What does sloads not model?** Tailwheel gear, pressurisation, turbofan
engine failure, the Part 25 dynamic gust and more, each with the way it errs.
→ [Scope and limits](../20_theory/04_scope_and_applicability.md).

**What does this field mean, and which page owns it?** Each chapter links its
generated field table; every field in one place is the
[data dictionary](../10_standard/DATA_DICTIONARY.md).

## About getting the loads out

**Can I work in SI?** Yes: the sidebar's units toggle changes what you see
and type, never what is stored. [Appendix B](B_worked_twin.md) works a whole
airplane in SI and shows the stored file is unchanged.

**How do I get the loads into my structural model?** The **Beam Model** page
writes the balanced load set as a solver deck.
→ [Appendix E §3](E_worked_concept.md#3-the-deliverable-the-balanced-beam-model);
[Where next](D_where_next.md).

**How do I get the numbers as files?** The **Report** page writes an issue
package whose `data/` folder holds every case as CSV.
→ [Appendix A §3](A_worked_single.md#3-read-what-it-delivers).
