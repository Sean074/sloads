# 13. One Engine Out

*Original program(s):* `ONENGOUT`.

## What this page is for

`ONENGOUT` simulates the engine-failure condition of 14 CFR 23.367: one
engine's thrust decays while its windmilling propeller's drag builds, the
asymmetric couple yaws the airplane, the pilot's corrective rudder arrives
after a delay, and the program marches the yaw dynamics in time to find the
vertical-tail loads of the transient and the recovery. It is the page the
twin exists for: the condition is *defined* by an engine off the
centreline.

On a single-engine airplane this page **withholds its form** and says why —
with one centreline engine the yawing couple is identically zero and there
is no condition to analyse ([Appendix C](C_troubleshooting.md)).

## Before this page

[Engine Mount](12_engine_mount.md) must carry the engines — the failed
engine's power, propeller disc and butt line are the forcing function — and
the yaw inertia and CG default from the heaviest FLIGHT loading on
[Weight & Mass Properties](02_weight_mass.md) (the aft-most, where several
tie at the design weight). The speeds evaluated come from
[Structural Speeds](04_structural_speeds.md).

## The inputs

The generated field table for this page:
[`_generated/one_engine_out.md`](_generated/one_engine_out.md).

**The event's timing.** Thrust decay time, windmill-drag build-up time, the
pilot's rudder travel time, and the integration time step. These are the
original program's inputs, and the customary values are short: the thrust
is gone in a fraction of a second, the drag arrives over a couple of
seconds, the rudder starts moving after the recognition delay the
regulation's method assumes.

**Which engine fails.** The failed-engine index on a multi — with identical
engines at symmetric butt lines the choice is a mirror; with different
installations, fail the critical one (and run both to prove which that is).

**Power basis.** Whether the live engine holds takeoff or max-continuous
power — the regulation's condition is at takeoff power; the choice is
yours to state, not the tool's to assume.

**The low end.** The minimum control speed, KEAS, cited to the flight
manual or type certificate. 23.367(a) considers both failure cases from VMC
upward, so it is the low-end case. Blank, the derived clean stall speed
stands in for it, which the manual permits and the case states. The
substitution only holds where the stall speed is at or above VMC. The
take-off altitude is where the low end is flown (blank: sea level), because
minimum control is a take-off condition.

**State overrides.** Evaluation speeds (blank runs the design-speed set),
the altitude VC and VD are flown at (blank: the shoulder), and the yaw
inertia and CG. Blank derives both from the heaviest FLIGHT loading, which
is why the database's inertias matter
([Weight & Mass Properties](02_weight_mass.md)). With no FLIGHT case whose
loading the database can produce, the page refuses rather than size the
condition on every item at once.

## Screenshots

![The One Engine Out page with the Baron twin loaded in SI: the timing
inputs and the failed-engine choice](img/13_one_engine_out__page-baron-58.png)

## Worked example — single (`ga6_normal`)

The page's honest answer for the single is the refusal: one engine on the
centreline, no condition. Nothing to enter, and the guide's Appendix A pass
skips it accordingly.

## Worked example — twin (`baron_58`)

Timing at the customary values — half-second thrust decay, two-second
windmill build, 0.3-second rudder travel, 0.05-second step — failing the
left engine at takeoff power, speeds left to the design set, inertia and CG
left to derive from the `aft gross` loading. The results run the condition
at VC and VD at the shoulder altitude and at the stall-speed floor at sea
level. No minimum control speed is cited, so the derived clean stall stands
in for it per the manual's method, and on this airplane the stall-speed case
recovers at the edge of controllability. The published rudder-load history is where you see the
regulation's story frame by frame: thrust gone, drag grown, rudder in,
yaw rate peaked and recovered.

## Results on this page

One condition per evaluated speed. Read the classifications carefully —
this page mixes them deliberately, and each case's note states its basis:
the failure cases the regulation defines at ultimate are **already ultimate
at SF = 1.0** and carry the `-ULT` marker; the ones it defines as limit are
delivered **LIMIT, stating SF = 1.5**, like every other load in the tool;
the low-end case is the entered minimum control speed, or a stated
substitution (clean stall for minimum control speed) per the manual's
method. Each case carries the
evaluated speed, the peak windmill drag and thrust asymmetry, the yaw-rate
peak and the vertical-tail loads of the transient and recovery.

Sanity checks: the asymmetric thrust at a given speed is roughly
`power × 0.85 / speed` in consistent units (the program's own relation);
the yaw forcing scales with the failed engine's butt line — a doubled arm
doubles the couple; and a "not recovered" verdict at a speed near stall is
the condition being genuinely below the controllable floor, not a crash. Such
a case delivers no load, and it is stated rather than dropped: in band, in
the page's warnings with its speed, altitude, fin incidence and load, and in
the exported deck's record of conditions not assembled.

## Common mistakes

- **Hunting for this condition on a centreline airplane.** The withheld
  form is the answer; see Appendix C.
- **Zero or placeholder inertias in the weight database.** The yaw
  transient divides by Izz; garbage in, garbage rate out. Enter the heavy
  items' inertias before trusting the time history.
- **Leaving the minimum control speed blank on an airplane whose VMC is
  above its stall speed.** The stall-floor case then runs below VMC and does
  not recover; the warning says so. Enter the cited VMC.
- **Reading every case as SF = 1.5.** The mixed classifications are the
  regulation's own; the note on each case says which you are looking at.
- **A propeller with no disc.** The windmill-drag model is propeller
  physics; the page refuses a zero-diameter disc by name rather than
  reporting a zero-drag failure.
