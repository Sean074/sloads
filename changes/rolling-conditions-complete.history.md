## Step — The rolling conditions arrive complete: condition A's lift on the delivered ACRL side, the Amdt 23-48 75 %, a derived unbalanced moment and the TORS aileron increment (#306, design note 52 D-52.1…D-52.13, tier L, 2026-09-25)

**Objective.** Deliver FAR 23.349's two rolling cases whole. SELECT always
picked `ACRL` and `TORS`, and WINGINER always had the unit-roll physics, but
the unbalanced rolling moment had to be typed by hand (a derived `ACRL`
carried zero, #258), the delivered `ACRL` variant flew the `AC ROLL` point's
airplane-average lift rather than condition A's (≈ 19 % low on the governing
side's net root bending), the other-side percentage was the manual's
pre-1996 70→75 % rule where 23.349(a)(2) as amended by Amdt 23-48 says 75 %
flat, the TORS `Δcm = −0.01·δ` increment was selected on but never applied,
the variant table ranked `ACRL` without its couple (#295), and an acrobatic
project got the normal percentage silently.

**Deliverables.** `constants.other_side_percent` (75 %, acrobatic refused
with `UnsupportedCategoryError`) is the one percentage owner, read by
FLTLOADS's `AC ROLL` factor `(100 + p)/200 · n₁` (3.25 → 3.325 on the GA6).
A new `modules/rolling.py` owns condition A's point and root bending, the
derived `UNB = −(1 − p/100) · M_root(A)`, the roll acceleration, the CAM 3.222
steady-roll schedule SELECT's torsion proxy now reads, and the TORS `Δcm`
table built on the existing v52 aileron butt lines. `resolve_wing_cases`
completes every `ACRL` case from those owners (entered values win); the
variant table builds `ACRL` rows at condition A's air with the derived couple
in the inertia; the balanced deck reads the same resolved couple, deriving it
at the balanced case's own point where an entered filter list omits `ACRL`.
The delivered wing conditions publish the derivation (percentage, condition
A's CL/V/root, UNB, θ̈ on `ACRL`; the deflection schedule on `TORS`). Schema
v69: `WingLoadCase.unbal_moment` is optional, blank derived; `_hop_68`
writes `null` for every stored zero. `ga6_normal`'s `ACRL` row is retired to
derived. The three "UNB comes from AILERON" statements are corrected.
`CONVENTIONS.md` §7 gains three owner rows; the approved-corrections entry,
ch04, ch09, `theory_sources.md`, `PROGRAM_SPEC.md` and D-29 carry the
shipped statement. One Imperial digest wave, 66 channels: FLTLOADS, SELECT, BALLOADS and the balanced and LRA decks moved on every fixture (the `AC ROLL` factor, the published derivation, every `ACRL` now a handed pair with its couple); NETLOADS, WINGINER and the wing applied deck on the GA6, the ATR and the RJ, whose wing lists run `ACRL`; the case index on all but the RJ. AIRLOADS, AILERON, the body, gear and tail channels did not move. Report §3 gains 3.3 *Rolling conditions* (the method, the percentage, the UNB derivation table and the deflection schedule; the two subsections after it renumber through the owner) and the Wing Loads page a caption stating the couple.

**Test.** `tests/test_rolling_conditions.py` holds G-52.1–G-52.13: the
Appendix A case 160 as a **test-built case** at its printed inputs reproduces
WINGINER p. 219 (θ̈ −13.287, root Sz −1126, Mxx −124,095, Myy +30,410) and
NETLOADS p. 225, so the `.BAS` math stays locked under the amended rule; the
derived UNB at the printed condition A is 128,619; the delivered `ACRL` air
equals condition A's to the identity on every variant; TORS with blank butt
lines is p. 226, with BL 109.28–201 its root ΔMyy is −18,667; drift guards
forbid the retired rule's literals and a second producer of the couple.
FLTLOADS case 20 is held at the manual's factor and asserted at the amended
one. D-29's divergence pin is replaced by the condition A equality.

**Key decisions.** (1) SELECT's `ACRL` pick on the GA6 moved from 12,000 ft
to sea level (V-n case 40): at the amended factor the CG2 roll points' LZW
tie across altitude to 0.13 %, inside the balance's 0.5 %; the build follows
SELECT's criterion and note 52 §9 leaves a tie band to the owner. The GA6
delivers UNB −129,142 and a net root MX of +400,817 (+2.7 % on the print).
(2) θ̈ is published in rad/s² — WINGINER prints it unlabelled and
`UNB·g/I_wxx` is 1/s². (3) Every fixture's `ACRL` is now a handed pair: the
ATR, the Baron and `concept_heavy` assembled a symmetric `ACRL` with no couple
before. (4) The TORS increment is wing-chain only; the balanced TORS stays the
symmetric trim case.
