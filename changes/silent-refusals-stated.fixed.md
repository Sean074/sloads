- **A refused input no longer goes silent: the T-tail checks say they could not run, a refused engine or one-engine-out family is recorded in the deck, and the dihedral warning reads the entered field (#344, tier S, 2026-10-04).**
  The T-tail induced-roll check returned no warnings at all when the spanwise
  tail build refused its input, and its dihedral warning fired only when a fin
  condition resolved. The engine-mount and one-engine-out deck families were
  emptied, unrecorded, when ENGLOADS or ONENGOUT refused. Each now states the
  refusal — `ttail_induced_roll_unchecked` on the tail page, a `family-refused`
  entry in the record of conditions not assembled — and the dihedral is read
  through one typed reader, `tail_geometry.htail_dihedral_deg`. The sweep
  found three more of the class, now refused by name: ONENGOUT read a refused
  STRSPEED input as "no VS" and dropped the 23.367 low-end case (and flew a
  refused engine on the right-hand fin sense), and a tail outline entered but
  not integrable read as "no planform entered" or an elevator of area 0. Every other
  silent `ValueError` catch in `sloads/` states its reason
  (`# refusal:`), held by a new AST guard. No shipped fixture or delivered
  load moves.
