- **What the beam grids cost the distribution is published (note 56 D-56.10,
  tier L, 2026-09-12).** The ninth slice of note 56, and the one D-56.9 owed the
  same day it landed: the applied appendices had begun saying *"what the lumping
  costs the distribution is stated in the VMT comparison"* and no such
  comparison existed. It does now, as **Appendix G** — one table of the widest
  gap per internal-load channel per member over every case, and four figures
  drawing that gap along the span. The owner is the new
  `sloads/report/lumping.py`, and the whole appendix rests on one sentence: an
  internal load at a cut is the static resultant of everything outboard of it,
  transferred to the cut. Written that way it serves a wing, a fuselage, a
  horizontal tail and a fin from one function, with no per-component
  integration path to keep in step, and it reuses the LM-1 owner the
  aggregation itself routes through.
- **D-56.10 was amended twice before any code, per rule 1.** *(i) There is no
  shared critical case to draw.* The decision called for four figures on one
  case so they could be read together; the four components' condition registers
  are disjoint by construction — `W-nn`, `F-nn`, `HT-nn`, `VT-nn`, each
  surface's own FAR conditions — so no case is run by more than one of them and
  the premise was simply false about the data. Each figure now names its own,
  and it is the case that bends that member hardest; the case where the
  *lumping* is worst is a different question and the table answers it over every
  case. A guard pins the disjointness so the amendment cannot outlive its
  reason silently. *(ii) The figures plot the gap, not the two curves.* Three
  channels in two versions is six colourless lines carrying three different
  dimensions; no single y-axis holds that honestly and no greyscale reader
  separates it. Nothing is lost, because both sets are already printed in full —
  the station set in B.2 and C.2, the delivered set in B.1, C.1, D and E — so
  the difference was the one thing the report did not carry.
- **The generic computation is cross-checked against the owner it
  generalises.** `report.applied.sob_internal_loads` states the wing's internal
  load at the side-of-body cut and has been gated against the solver's own CBAR
  end force since step 13. The new curve reproduces it — shear, bending **and**
  torsion — at the wing root of every case of four fixtures. That check is what
  made it safe to write one function for four members rather than four
  integrations; without it the appendix would rest on arithmetic nothing else
  had ever agreed with.
- **The numbers are larger than the decision assumed, and the fuselage is the
  outlier.** Worst deviation as a share of the channel's own peak, over every
  case, on the four loaded fixtures: wing shear 19–35 %, wing bending 3–5 %,
  wing torsion 17–77 %; both tails under 1.1 % in bending, 6–14 % in shear,
  9–21 % in torsion; **fuselage shear 82–197 %** and fuselage bending 14–19 %.
  The fuselage number is real rather than an artifact — on
  `concept_regional_jet` a ~107,000 lb spar carry-through reaction lands on a
  node one bay from where it acts, against a peak station shear of 54,588 lb.
  Ruling 15 says state it and do not gate it, and it is stated; it is also the
  strongest argument yet that the fuselage's owned mesh points should include
  the carry-through stations, which D-56.4's mesh does not currently guarantee.
  That is recorded in the note and owed an issue of its own; it is not fixed
  here, because this slice's job is to measure and changing the mesh to improve
  its own measurement in the same change would be marking its own paper.
- **Bending survives lumping best on every member of every fixture** — under
  5 %, against tens of per cent in shear and torsion. That is the expected
  shape, because bending is an integral of the shear: moving a load a short
  distance perturbs it by the load times that distance, while the shear at a
  crossed cut moves by the whole load. It is worth a reader knowing, since
  bending is what most of the structure is sized by, and the appendix's prose
  says so rather than leaving four figures to imply it.
- **Three guards outside the feature caught its defects**, which is the argument
  for having them at all: the platform-stability sweep refused three keyed
  `min`/`max` picks and sent them through `picks.extreme`; the rendered-LaTeX
  sweep refused markdown emphasis in the new appendix prose; and the
  package-layout guard refused the new module until `PROJECT_GUIDE.md` §4 listed
  it. None of the three is about lumping, and all three were right.
- **The fin's withholding is honoured.** OR-133 withholds the fin's spanwise
  loads on a non-conventional layout, so Appendix G omits the fin comparison
  there rather than publishing sideways a set section 6 declined to publish.
  `atr42_100` and `concept_regional_jet` are T-tails, so the guard is live in
  both directions on the shipped fixture set. A channel with no producer — the
  fuselage carries no torsion in this analysis — is left out of its figure
  rather than drawn flat, so no legend entry invites a reader to hunt for a line
  hidden under the axis.
- **Docs and gates.** `ORACLE_REPORT.md` §3.14 and a section-register row;
  `PROGRAM_SPEC.md`'s applied-set entry; `PROJECT_GUIDE.md` §4; and — reversing
  the note's own "no citation" line for this one decision —
  `docs/20_theory/00_theory_sources.md` gains the lumping rule: what LM-1
  preserves exactly, what it does not, and why there is no printed oracle and no
  tolerance for the second half. Ten tests in `tests/test_lumping.py`,
  including a hand-computed cantilever whose numbers are written out rather than
  compared against a second implementation.
