- **Every delivered file now states the frame its numbers are in (#242, tier M,
  2026-09-13).** The requirement the CSVs exist to serve — contents in airplane
  global coordinates, readable without the repository — was met by the data and
  not by the self-description: the per-file blocks said "right-handed about the
  airplane axes" and named torsion axes, and no delivered file anywhere said
  that `x` is the fuselage station positive aft. An **AXES** stanza now sits
  beside the UNITS one in the methods stamp, so it lands in band on the six
  applied CSVs, the case index, the gear report, the safety-factor table, the
  per-module CSVs, the V-n conditions file, `METHODS.txt` and the decks at once.
  The words are owned by `export/coordinates.AIRPLANE_AXES` / `AXES_NOTES` —
  beside the map they describe, which is already the declared single edit-point
  for an axis flip — and are rendered by one block and nothing else.

- **The one file that carries two frames now names both (#242).** The gear load
  report states each reaction twice: `Ground-line V/D/S` in the manual's
  ground-line frame at the contact patch, and `Patch`/`Datum`/`Ref point`/
  `Transfer` in airplane axes. A stanza saying "airplane axes" above a file
  where nine columns are not would have been worse than saying nothing, so the
  exception is stated in the file's own header block, beside the columns it
  applies to, and stands on its own for the one caller that downloads the file
  unstamped.

- **`MyyAxis` is `TorsionAxis`, because the fin's torsion is `Mz` (#242).** A
  lateral load makes no moment about `y`, and `applied_body_moments` has put the
  fin's torsion in `Mz` since note 44 OR-142 — so on one of the six applied
  files the column naming the torsion axis asserted an axis the data beside it
  did not honour. One name, true on every file. `net_loads.wing_load_rows` keeps
  `MyyAxis`: it is a wing-only table where the torsion really is `Myy`, and its
  schema is the published interchange format the external-comparison import
  reads.

- **A control-surface row says it is a surface-normal load (#242).** The
  deleted `control_surface_loads.csv` labelled that column `Fz` on every surface
  including the rudder. The rows survived into the h-tail and fin applied files
  correctly resolved — the numbers were never wrong — but nothing told the
  reader that the number in `Fy` on a fin row is the surface normal rather than
  a sideslip load. Both tail files now say so.

- **A file's structural zeros are measured, not asserted (#242).** OR-140's rule
  is that a zero column is published, never dropped, and the reason it is zero
  is published beside it. Both halves were prose — and note 56 D-56.9 then
  re-aggregated the delivered set onto the LRA grids, where each load carries
  the lever-arm couple of its own offset, so moments appeared on three axes that
  four of the six files still called zero "throughout". The claim is now read
  off the rows being written and the prose supplies only the reason; a column
  this configuration happens to leave empty is stated as that and not as
  something the model cannot fill; and a re-aggregated file states that its rows
  are at grids and that its moment columns therefore carry arms as well as free
  moments — the sentence whose absence let the zeros go stale.

- **The V-n conditions file carries the definitions its page prints (#242).** It
  had nineteen columns and left `M(W+F)`, `LZW`, `LT`, `DX` and `NX` defined only
  in the appendix's table notes. It now carries both notes, read off the same
  `Table` objects the appendix renders, and the notes lost their "above"/"below"
  so that they are true of a file that joins the two tables into one row.

- **A delivered CSV has one line ending (#242).** Every stamped file was LF in
  its comment block and CRLF in its rows, the prose being joined by hand and the
  data coming from `csv`'s default. `sloads/csv_text.py` owns the terminator and
  the two writer constructions the package makes; no call site passes
  `lineterminator=`, because a writer added without it produces a file that
  looks right in every viewer and is mixed on disk.
