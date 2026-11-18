# Appendix A — Worked example: the single (`ga6_normal`)

The manual this suite replicates prints a complete worked case in its own
Appendix A: a 6-place, 3,400-lb general-aviation single with a Continental
IO-520-BB, carried through every program with its inputs and outputs listed.
`ga6_normal` **is** that airplane. This appendix is the whole analysis, end to
end: from the project to the delivered loads, and how to read them. Because the
airplane is the book's, the numbers on your screen can be checked against an
independent printed record, not against this tool's own tests.

**The figures.** Every number this pass refers to is in one generated table,
[`_generated/worked_ga6_normal.md`](_generated/worked_ga6_normal.md). It is
written from a run of the bundled example, set beside the value the manual
prints and the page that prints it. A test holds each row to the book, so the
table cannot drift from the example or from the manual.

## 1. Open the project

Load it from the sidebar (**New from example → `ga6_normal`**). Leave the units
on **Imperial**, because the point is digit-for-digit comparison with the book.

Starting from an empty project instead (**New project**) is the same pass with
the typing done by you: each chapter's *Worked example — single* section lists
that page's inputs from the book. The order matters, because each page consumes
what the earlier pages produced ([Getting started](01_getting_started.md)).

## 2. The pass

Each stop is one page. The chapter linked carries the full input walkthrough
and the reason for every value.

1. **[Geometry](01_configuration_layout.md).** The kinked three-point wing
   leading edge, the aileron, and the Appendix A tail scalars. Check the
   derived MAC against the book's planform chapter before moving on.
2. **[Weight & Mass Properties](02_weight_mass.md).** The book's loading list
   row for row, the CG envelope, the four flight CG cases `CG1`…`CG4` and the
   three landing corners. The statistical weight estimate is in the figures
   table.
3. **[Aerodynamic Data](03_aero_coefficients.md).** The printed polars,
   exactly: the CLmax set and the fitted lift, drag and moment polynomials.
4. **[Structural Speeds](04_structural_speeds.md).** Category N, VC chosen,
   VD at 1.25 × VC; the derived load factors and VA.
5. **[Flight Envelope](05_flight_envelope.md).** Sea level only. The balanced
   V-n matrix reproduces the book's corners (the figures table has the MAN A
   and GUST +C corners of CG1), and SELECT picks the critical set the rest of
   the analysis uses.
6. **[Wing Loads](06_wing_loads.md).** The spanwise LIMIT tables of the
   selected cases against the book's `NETLOADS` output.
7. **[Fuselage Loads](07_fuselage_loads.md).** The body lumps and the
   distributed body cases.
8. **[Tail Loads](08_tail_loads.md).** The chordwise distributions of the
   selected cases against the book's tables.
9. **[Aileron](09_aileron_loads.md), [Flap](10_flap_loads.md) and
   [Tab](11_tab_loads.md) Loads.** The three simplified-method surface loads,
   each a one-block comparison.
10. **[Engine Mount](12_engine_mount.md).** The IO-520-BB set. The mean
    take-off torque matches the book; the take-off-torque *case* is
    deliberately higher than the book's, the one approved deviation on this
    page ([approved corrections](../20_theory/02_approved_corrections.md)).
11. **[One Engine Out](13_one_engine_out.md).** Withheld on this airplane:
    one centreline engine, so no asymmetric-thrust condition exists. That is
    the correct Appendix A behaviour.
12. **[Landing Loads](14_landing_loads.md).** The energy inputs, and the
    entered design gear factor beside the computed one. The book prints the
    energy ratio as N; sloads reports it as the gear factor NLG (deviation
    register, #401).

## 3. Read what it delivers

The pages compute; the **Report** page delivers. Build a DRAFT issue there
(no signatures needed, so iterating costs nothing). The package it writes
holds the formatted report and a `data/` folder. Headless, the same report:

```bash
.venv/bin/sloads --report out.pdf examples/ga6_normal.project.json
```

- **The case index** (`data/case_index.csv`) lists every load case once, with
  its identity: condition, CG, speed, altitude and regulation. Each section of
  the report names its cases by that identity
  ([`CONVENTIONS.md`](../10_standard/CONVENTIONS.md) §4).
- **Every load is LIMIT.** The page, the report, the CSVs and the decks carry
  the same number, and it is the number the book prints. Nothing has been
  multiplied.
- **Read the SF cell, and apply it yourself.** Each case states the factor
  your sizing applies: 1.5 by default (14 CFR 23.303), from the governing
  safety-factor table the report prints. `SF=1.0` with a `-ULT` unit marks the
  two families the regulation prescribes already ultimate; `N/A` marks a value
  that is not a load (a weight, speed or load factor). The figures table shows
  the SF of each row it quotes. The rule in full:
  [Conventions](03_conventions.md).

## 4. What this pass proves

That the chain you will run on your own airplane — the same pages, in the same
order — reproduces an independent published record end to end. A figure that
does not reproduce means an input drifted from the book's: re-load the
untouched example and diff your project against it before suspecting anything
else. The working instinct this appendix builds is: *the tool is oracle-locked;
check the input first.*
