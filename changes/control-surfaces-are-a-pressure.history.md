## Step 161 — Control surfaces deliver a pressure (note 44 §19, tier L, 2026-09-07)

**Objective.** Give the oracle report its aileron, flap and tab sections — the
geometry, the critical condition and the resulting load, as the printed oracle gives
them on pages 200, 201 and 202 — plus what the oracle does not give: a drawing of the
surface, a drawing of how the pressure is applied to it, a sign convention, and a
statement of the spanwise distribution, which the oracle leaves ambiguous.

**Agreed first.** Design note 44 §19 (**OR-147 … OR-157**), settled with the owner in
session on 2026-09-07 before any code, from the ruling that opens it: *these surfaces
are just pressure loads, so no appendix B, C, D type distributed loads; the aileron and
flap geometry is defined with the main surface in Section 2, use that definition; the
tab is defined with the elevator; the purpose is to show how to apply the pressure load
to the control surface.* Gates **G-OR-95 … G-OR-103**.

**What the analysis leaves ambiguous, and how it is closed.** The oracle prints a
chordwise rule in words and says nothing about the span. The rule is recoverable from
its own equations rather than assumable: the aileron's `W = LAIL/(SAFWD + ½·SAAFT)`, the
flap's `LF = 0.75·p_LE·SF` and the tab's `W = LTAB/1.5/STAB` each divide a load by an
**area**, so the pressure is uniform along the span and the chordwise profile is in
fractions of the local surface chord. Checked against Appendix A exactly: flap
`629/(10.7·144) ÷ 0.75 = 0.5443` against the printed 0.545 psi; tab `84.618/226 × 4/3 =
0.4992` against 0.4992 / 0.2496; aileron `271.44/3.894/144 = 0.4841` against 0.484. Two
consequences are stated rather than left to be inferred — the load per unit span goes
with the local chord, and the aileron's chordwise breakpoint is an *area* fraction, a
chord fraction only where the hinge-chord ratio is constant along the span.

**What the review found.** The area a surface's loads are run on and the area its
entered outline encloses are two entered numbers, and they disagree: the aileron's
outline is −0.2 % against its analysis area on `ga6_normal`, −4 % on `baron_58`, +5 % on
`cessna_210` and **−44 %** on `concept_regional_jet`. Had the locator figure shaded the
outline and divided the load by it — the obvious way to draw it — the regional jet would
have printed a pressure 77 % high for a load nothing had changed: the milestone's
recurring defect, an entered value shadowed by a derived stand-in with nothing saying
so. The pressure therefore has one owner and a drawn outline is never a divisor, and
past 2 % the document states the disagreement instead of resolving it in either
direction. **G-OR-98** asserts it on the airplane where the two are furthest apart.

**Deliverables.**
- `report/oracle_sections.py` — `_aileron_loads`, `_flap_loads` and `_tab_loads` behind
  three new `BUILDERS` entries, on shared owners: `_control_sign_convention` (one
  convention, one wording), `_SPANWISE_RULE`, `_HINGE_MOMENT_ABSENCE`,
  `_control_chord_figure`, `_control_locator_figure`, `_control_case_table`,
  `_profile_centroid`, `_tab_rectangle` and `_area_discrepancy`. `_CONTROL_HOSTS` and
  `_TAB_HOSTS` declare which surface each is cut into and which airplane axis its
  normal is, as data, so a surface added to the schema without a normal fails the suite
  rather than inheriting one.
- `report/oracle_content.py` — the three step keys join `IMPLEMENTED`, which is all it
  takes to turn a stated placeholder into a section.
- `tests/test_oracle_report_control.py` — new, 19 gates over four examples.
- `docs/10_standard/ORACLE_REPORT.md` §3.9 and ten register rows; note 44 §19.

**Test.** The gate that matters is **G-OR-97**, because it holds the *stated* spanwise
rule to the numbers the analysis was built with rather than asserting it in prose. Two
gates were written to fail in both directions — the area disagreement must fire on the
three that disagree and stay silent on the two that agree, and the locator must render
an outline or a sentence and never an empty axis, with both states exercised by the
shipped set. Two defects were caught by the new gates before they shipped: the flap's
slipstream table reached section 2's `_value_table`, which marks a load `-ULT` by
design because no load is meant to reach it, and the flaps-extended candidate table
printed four loads with no `SF` column. Suite green, ruff and mypy clean, and all three
shipped reports compile with no LaTeX warnings.

**Key decisions.** OR-147 is the one the rest follows from: the A–E appendix pattern
does **not** extend to a control surface, because that pattern exists for a load a
structures model integrates station by station and this is a pressure over a surface the
document already draws. OR-154 states no hinge moment at all — no module produces one,
and the sense of it is the sign convention, which is what a reader actually needs to
apply the load. Both are the same restraint the milestone has been applying throughout:
report what the analysis produced, and say plainly what it did not.
