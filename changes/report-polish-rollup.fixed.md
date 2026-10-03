- **The 2026-09-08 review's report-polish rollup is closed: one moment unit, a side-load row that names its wheel, labels that do not stack, captions that describe what is drawn, a true airspeed tagged as one, the pitch inertia's basis stated, a references list, and appendices that promise no row they do not print (#240, tier S, 2026-10-02).**
  Each of R13-R23 read against the 0.8.8 report. **R13:** the engine-mount
  moment and torque columns were the document's one ft-lb channel; they are
  stated in lb-in like every other moment, and the torque note says the oracle
  prints them in ft-lb. **R14:** the per-wheel table's note says each 23.485
  row is one main wheel -- the odd case the 0.5 W inboard wheel, the even the
  0.33 W outboard -- and that the other wheel's is its partner's. **R16:**
  `plots_tex`'s label placer scores a label against the labels already placed,
  scales its footprint to a drawing's own aspect, and steps a crowded label out
  onto a leader line; the ground attitudes' three landing-CG labels no longer
  stack. **R18:** the engine views' caption said every arrow ran from the
  mount node to the hub, which an ASSUMED arrow does not, and told the reader
  to enter the propeller CG to replace one; it describes both kinds of arrow
  and names the thrust line's two points. **R19:** the tail appendices said
  their rows were strips followed by control and T-tail transfer nodes, rows
  note 56 D-56.9 folded into the grids; the sentence says so, and names the
  transfer only on a T-tail. Appendix B states that W-50 and up are the
  aileron's, flap's and tabs' ids, from `case_ids`' bands. **R20:** the speed
  of sound is tagged `kt(TAS)`, a new unconverted row beside `kt(EAS)`, not
  "633 kt(EAS)"; the frozen Imperial baseline is regenerated for it, and the
  only channels that move are each example's `csv/` and `txt/`
  `structural_speeds`, by that unit tag alone. **R21:** a comment said SELECT reads the h-tail pitch inertia
  from the weight database "in every case" and suppressed its basis; it is
  always the rod estimate x 0.44, and the state table says so beside the
  v-tail's yaw-inertia statement. **R22:** "Reference 1" is defined in a
  References subsection owned by `report.methods.REFERENCES`. **R23:** the
  fuselage Sz/Myy captions say "every curve", and Appendix A states that its
  nineteen columns are printed as two tables. R15's empty continuation page,
  R16's mass labels and R23's lowercase lead no longer reproduce.
  `tests/test_oracle_report_polish.py` pins each. No delivered load moves.
