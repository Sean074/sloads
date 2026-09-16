# Conventions

The rules below are stated once, here, and every chapter leans on them. Their
single owner in the repository is
[`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) — this page summarises what
a user needs and links the authority; where the two could ever disagree, the
owner wins.

## Axes and stations

All positions are entered in **airplane axes, in inches**:

- **x** — fuselage station, positive **aft**;
- **y** — butt line, positive **right** (starboard);
- **z** — waterline, positive **up**.

The **datum** (x = 0) is yours to choose; every station in the project simply
measures from it. Use your airplane's established datum — the worked twin
keeps its type-certificate datum so the certificate's arms can be typed in
unchanged. Loads follow the same frame: lift is +z, drag is +x, and every
reported torsion names the axis it is taken about.

Spanwise positions on a surface are butt lines from the centreline; planforms
are entered as leading- and trailing-edge corner points in these same
station/butt-line coordinates on the [Geometry](01_configuration_layout.md)
page.

## Frames: airplane datum and ground line

The axes above are the **airplane datum**, and almost every page in the guide
works in it alone. The ground-loads chain is the exception, because the
original suite works there in two frames and prints both:

- **Airplane datum** — the body FS/WL axes above. This is the **delivered**
  frame: what a beam model applies, what the export decks carry, and what the
  downloaded CSV states.
- **Ground line** — perpendicular and parallel to the runway through the
  wheels' contact patches, the frame a gear engineer reads a reaction in.
  LANDLOAD computes in it and the manual prints it as the "primed" set
  (VMP, DMP, NVP…). It is an analysis view rather than a deliverable, and it
  rides in the gear report's own `Ground-line V/D/S` columns.

The two differ by a rotation of the attitude's ground angle, so the same
reaction has different components in each and the frame is part of the
number's meaning. Wherever a value names a frame, that name travels with it:
on screen, as a `Frame` column in the module's file, and as a header block in
`data/gear_loads.csv` naming the frame of every column it has.
[Landing Loads](14_landing_loads.md) is where you will meet both.

A delivered force also names **where it acts** — its point of application, in
the same airplane-datum coordinates, stated both as `x/y/z` numbers and, where
the point has a name (a wheel's axle, its ground contact point), as a word in
an `Applied at` column. A force without a point is not yet a load a structural
model can take.

## Units and the Imperial/SI boundary

The calculation, like the original suite, runs in **Imperial units**
(lb, in, kt), and the project file stores Imperial values. The sidebar's
units toggle is a **display boundary**: with SI selected, every input widget
and result table converts on the way in and out, and nothing about the stored
project or the computed loads changes. Two consequences worth trusting:

- You can enter an airplane wholly in SI — the guide's twin is worked that
  way end to end — and reopen it in Imperial to see the same airplane.
- **Airspeeds and altitudes never convert**: knots EAS and feet in both
  systems, the aviation standard.

Every downloaded file states its unit set in-band, so a CSV on its own says
what its columns mean.

## LIMIT loads, and the factor that is stated

This is the guide's one statement of the contract; each chapter's *Results*
section only says which of its blocks are loads and which are not.

FAR 23 distinguishes **limit** loads (the largest expected in service) from
**ultimate** loads (limit × the factor of safety, normally 1.5 per
14 CFR 23.303). Which of the two this tool hands you, and who applies the
factor, is owned by
[`CONVENTIONS.md` §3](../10_standard/CONVENTIONS.md#3-limit-load-contract--stated-never-applied)
— what a user needs from it:

- **Every load the tool delivers is LIMIT**: on screen, in the case index, in
  the report and in every exported file, including the solver deck. No step
  multiplies a load by the factor.
- **Every case states the factor it did not apply.** The `SF` column is that
  factor, read from the governing safety-factor table — one row per FAR
  condition family, each with a stated basis. Applying it belongs to the
  sizing step downstream: size to `value × SF`.
- A block that is **not loads** — speeds, load factors, weights, geometry,
  diagnostics — prescribes no factor at all, and its `SF` cell reads **N/A**.
  That is a statement, not a missing number.
- **`ULT SF=1.0` means the case is already defined at ultimate**, not that the
  factor was skipped: a few 14 CFR conditions are written that way and leave
  nothing to apply. You meet them in
  [One Engine Out](13_one_engine_out.md) and, on a twin, in the v-tail rows of
  [Tail Loads](08_tail_loads.md) — both are 23.367(a)(2).
- **The `-ULT` marker is part of the units string** (`lbs-ULT`, `lb-in-ULT`)
  and appears on those cases and no others, which is what makes it worth
  noticing. Plain units mean limit.

When you cross-check the single against the manual's printed Appendix A
figures, nothing has to be undone in either direction: the book prints limit
loads and so does the tool.

## Reading a results table

Every page renders its program's results as one table per result block,
below the input form. The recurring columns:

- **ID** — the case identity (`W-01`, `HT-03`, `LG-05`…), minted once by the
  first program that names the condition and kept by every later view of it.
- **FAR** — the regulation paragraph the case implements (`23.421`…).
- **Condition** — the case in words, as the original program named it.
- **Component / CG / Speed / Altitude** — the state the case is computed at.
- **Quantity, Value, Units** — one row per reported quantity, units carrying
  the `-ULT` marker on the already-ultimate cases above and nowhere else.
- **SF** — the case's stated safety factor, as above.
- **Frame / Applied at** — the frame the value is stated in and the named
  point the force acts at, per the section above.

A column that no row on the page fills is dropped rather than shown empty, so
a page of properties renders as Condition / Quantity / Value / Units, and only
the pages that work in two frames carry `Frame` and `Applied at`.

## Reading a CSV out of the package

The results on screen come as files from the **Report** page: build an issue
and open its `data/` folder. `data/load_cases/<module>.csv` is the table the
page shows, written from the same data, so the two cannot disagree — plus an
in-band statement of the units, the axes and the factor that is stated and not
applied. Open them in any spreadsheet; nothing in them is scaled, renamed, or
rounded differently from what you saw on the page.

Where a program works in **two frames**, both are carried and the columns say
which is which. LANDLOAD is the case in point: `data/gear_loads.csv` states
each reaction twice — `Ground-line V/D/S` at the tyre contact patch, the
manual's primed set, and `Datum Fx/Fy/Fz` in airplane axes — so the analysis
view a gear engineer reads is in the package, not only on a page.

Per-block CSV and text download buttons used to do this job, and a results zip
in the sidebar did it a third time. All three retired into `data/` at #245: one
channel, one set of names, one manifest.
