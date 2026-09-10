## Step — The boundary lines are entered once, and the scalars derive (#25 step 2, design note 54 D-54.1/D-54.8, tier L, 2026-09-10)

**Objective.** Close the 0.8.3 headline's schema half: boundaries that are
physically one line were entered several times with nothing checking the copies
agree — `ga6_normal`'s elevator TE was byte-identical to its h-tail TE, its
rudder TE was the fin TE plus a closure point, and the nine h-tail and ten
v-tail planform scalars were hand-typed readings of surfaces the project
already carried as polylines. After this step one tail group is **five entered
lines** — tail LE, tail TE, control LE, control hinge line, and the control TE
*derived* from the parent's — and every `[D]`-marked scalar of the step-1 seam
derives from them wherever it is blank.

**Agreed first.** Design note 54 (AGREED 2026-09-09, owner), D-54.1 for the
boundary-line model and D-54.8 for the declared dihedral field; #25 step 1
(the marked seam, tier M, 2026-09-10) landed the machine-readable membership
this step consumes.

**Deliverables.** Schema v65 (`SurfaceInput.hinge_line`, control
`trailing_edge` allowed empty, `LayoutInput.htail_dihedral_deg`, the two tail
blocks physically regrouped into the seam order; identity hop, examples
re-stamped). The resolution owners in `sloads/tail_geometry.py`:
`CONTROL_PARENT`/`TAIL_CONTROL`, `derived_control_trailing_edge` (parent TE
over the control's span, end-closure to the control's own LE endpoint where it
departs), `validate_control_trailing_edge` (the copies-agree guard, hard on
the tail groups), `resolved_control_surface`/`resolved_surfaces` (the read
every control-polyline consumer goes through: the WINGGEOM integrator,
AIRLOADS' Schrenk pass, the report's planform figures),
`control_hinge_areas` (the hinge split, integrated by the one planform owner
so the halves and the whole cannot drift), and `boundary_derived_scalars`
(the `{field: value}` set `effective_tail_inputs`/`effective_vtail_inputs`
and `resolve_tail_planform` take for blank fields only). `ga6_normal` sheds
its elevator and rudder trailing edges — the derivation reproduces Appendix
A's printed coordinate tables (p153, p149) byte-for-byte, pinned in the test
that replaced them.

**Test.** Note 54 gate 7: every derived scalar the GA6 boundary lines supply
lands on its printed Appendix A figure within ±0.1 % (h-tail p151, elevator
p153, rudder p149; the fin against the printed-planform scalars) —
`test_the_boundary_model_predicts_the_printed_appendix_a_figures` — so the
transcriptions became checked predictions. Gate 8: the frozen Imperial
digests are **byte-identical** across the whole step, re-stamp included.
Mechanism gates: derived-TE byte-identity, the +1.00 % aileron end-closure
number from #25's own row (why an entered control TE survives), the
off-parent refusal, the analytic hinge split and its two refusals, the
whole-seam blank-derive walk, the v65 round-trip, and D-54.8's boundary — a
6° declared dihedral moves nothing any module renders.

**Key decisions.** (1) *Blank derives, typed overrides* — the oracle fixtures
keep their Appendix A transcriptions, so the model lands with zero movement in
any delivered load; the derivation is proven against the print, not by
re-baselining onto itself. (2) The copies-agree guard is **hard on the tail
groups only**: three shipped fixtures' estimated aileron polylines sit
0.04–9.4 in off their wing TE, and reconciling that data is the #260/D-54.6
fixture wave's deliberate, baseline-moving work — a guard that fired today
would have forced silent fixture edits inside a no-movement step. (3) The
fixed-surface TE line of D-54.1's five is carried by the parent TE + control
LE pair wherever the two coincide; a separately-entered stabilizer TE
(shroud/overlap geometry) has no consumer and no printed oracle yet
(Appendix A p152 prints the h-stabilizer run the future gate would use), so
it waits for its consumer rather than shipping as an unread field. (4) The
tail blocks' physical regrouping rode this bump exactly as step 1's fragment
promised — field order is a persisted shape, and the reorder spent the
version hop the boundary model was already paying for.
