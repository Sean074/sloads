# `project.json` Input Data Dictionary

> **Generated file — do not edit by hand.** Produced by [`docs/generate_data_dict.py`](../generate_data_dict.py) from the `sloads/models/` dataclasses. Regenerate after any schema change: `.venv/bin/python docs/generate_data_dict.py`.

Schema version: **81**.

This dictionary covers the **input** slices of `Project` (`sloads/models/project.py`) — the fields that make up a `project.json`. The result slices (`envelope`, `mass`, `loads`) are computed outputs and are out of scope.

**Column meaning & caveats:**

- *Type* / *Default* are introspected from the dataclass (`typing.get_type_hints` / `dataclasses.fields`) — authoritative.
- *Units / notes* reproduces the field's inline `# comment` verbatim (falling back to a guess from the name suffix, e.g. `_lb`→lb). Comments are prose, not a structured units field — treat it as a hint.
- *Owning page* and *Consumed by* are **slice-level**, not per-field: `workflow.py` tracks data flow per slice, so every field inherits its root slice's page and consumer list. Owning page is the workflow step that `produces` the slice (with a small override table in the generator for slices workflow doesn't attribute); *Consumed by* lists the calc modules whose source reads `.<slice>`.

## Project slice map

The top-level `Project` fields. `name`/`engineer`/`date` are free-text metadata; `schema_version` is set by `io.py`. The rest are the input slices detailed below.

| Slice | Type | Owning page | Consumed by | Role |
| --- | --- | --- | --- | --- |
| `engines` | `List[EngineInput]` | Engine Mount Loads / Geometry | `balance`, `engine`, `flap`, `one_engine_out`, `weight_estimate`, `wing_geometry` | Engine-mount inputs (one per engine) |
| `engine_layout` | `Optional[EngineLayout] (enum)` | Geometry | `wing_geometry` | Engine layout constraint (enum) |
| `weight` | `Optional[WeightInput]` | Weight & Mass Properties | `configuration`, `engine`, `select`, `weight_envelope`, `weight_estimate`, `weight_onecg` | Weight database (WTESTIMA / WTONECG / WTENV) |
| `geometry` | `Optional[GeometryInput]` | Aerodynamic Data / Geometry / Weight & Mass Properties | `airloads`, `balance`, `configuration`, `flap`, `landing`, `net_loads`, `rolling`, `tail_span`, `weight_envelope`, `wing_geometry`, `wing_inertia`, `wing_variants` | Geometry single-source (WINGGEOM + fuselage + empennage) |
| `speeds` | `Optional[StructuralSpeedsInput]` | Structural Speeds | `aileron`, `engine`, `flap`, `flight_envelope`, `mach_limit`, `one_engine_out`, `rolling`, `structural_speeds`, `tab` | Structural design speeds & load factors (STRSPEED) |
| `aero` | `Optional[AeroInput]` | Wing Loads | `airloads`, `balance`, `net_loads`, `rolling`, `wing_variants` | Spanwise airload inputs (AIRLOADS) |
| `aero_coeffs` | `Optional[AeroCoefficientsInput]` | Aerodynamic Data | `balance`, `flight_envelope`, `one_engine_out`, `select`, `structural_speeds` | Airplane-less-tail aero coefficients (FLTLOADS input) |
| `flight_loads` | `Optional[FlightLoadsInput]` | Flight Envelope (V-n) | `balance`, `balloads`, `body_loads`, `flight_envelope`, `select`, `tail_span` | Flight envelope / balancing tail loads (FLTLOADS) |
| `wing_mass` | `Optional[WingMassInput]` | Weight & Mass Properties / Wing Loads | `balance`, `net_loads`, `rolling`, `wing_inertia`, `wing_variants` | Wing-mass distribution & load cases (WINGINER) |
| `fuselage_mass` | `Optional[FuselageMassInput]` | Weight & Mass Properties | `body_loads` | Fuselage mass distribution (SELECT / Ch 15) |
| `tail_mass` | `List[TailMassInput]` | Weight & Mass Properties | `tail_span` | Empennage surface mass override — derived from the component-tagged weight.items by default (plan 09 T-3) |
| `select_input` | `Optional[SelectInput]` | Aerodynamic Data / Geometry / Weight & Mass Properties | `select` | Critical-load selection inputs (SELECT) |
| `tail_loads` | `TailLoadsInput` | Aerodynamic Data / Geometry | `balloads`, `body_loads`, `select`, `tail_span`, `taildist` | Rational horizontal-tail inputs (via geometry.empennage) |
| `vtail_loads` | `VTailLoadsInput` | Geometry / Weight & Mass Properties | `balance`, `one_engine_out`, `select`, `tail_span`, `taildist` | Rational vertical-tail inputs (via geometry.empennage) |
| `aileron_loads` | `Optional[AileronLoadsInput]` | Aileron Loads / Geometry | `aileron`, `rolling`, `select` | Aileron simplified loads (AILERON) |
| `flap_loads` | `Optional[FlapLoadsInput]` | Flap Loads / Geometry | `flap` | Flap simplified loads (FLAPLOAD) |
| `tab_loads` | `Optional[TabLoadsInput]` | Tab Loads | `tab` | Tab simplified loads (TABLOADS) |
| `one_engine_out` | `Optional[OneEngineOutInput]` | One Engine Out | `balance`, `one_engine_out`, `select`, `tail_span` | One-engine-out v-tail loads (ONENGOUT) |
| `landing` | `Optional[LandingInput]` | Landing Loads | `balance`, `landing` | Landing loads (LANDLOAD / GEARLOAD) |
| `lra_mesh` | `Optional[LraMeshInput]` | Beam Model | — | LRA beam mesh: node count per member (design note 56 D-56.4) |
| `include_far25` | `bool` | Engine Mount Loads | `balance`, `engine` | Opt-in FAR 25 supplemental cases (flag) |

## Field tables

One table per input dataclass, in slice order (nested types follow the slice that first references them). A field typed as another dataclass is detailed in that dataclass's own table.

### `EngineInput`

Complete input set for an engine-mount loads run.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `engine_designation` | `str` | e.g. "CONTINENTAL IO-520-BB" | `''` |
| `prop_designation` | `str` | e.g. "HAM STD 1803" | `''` |
| `engine_type` | `EngineType` |  | `EngineType.RECIPROCATING` |
| `limit_load_factor` | `float` | LIMNZ | `0.0` |
| `engine_weight_lb` | `float` | ENGWT | `0.0` |
| `engine_cg` | `Tuple[float, float, float]` | XENG, YENG, ZENG | `(0.0, 0.0, 0.0)` |
| `prop_weight_lb` | `float` | PROPWT | `0.0` |
| `prop_diameter_in` | `float` | PROPDIA | `0.0` |
| `prop_inertia` | `Optional[float]` | measured propeller polar inertia, slug-ft^2 (overrides geometry) | `None` |
| `prop_blades` | `int` | NOBLADES | `0` |
| `takeoff_rpm` | `float` | TORPM | `0.0` |
| `max_cont_rpm` | `float` | CONTRPM | `0.0` |
| `prop_cg` | `Tuple[float, float, float]` | XPROP, YPROP, ZPROP | `(0.0, 0.0, 0.0)` |
| `takeoff_hp` | `Optional[float]` | TOHP | `None` |
| `max_cont_hp` | `Optional[float]` | MAXCONTHP | `None` |
| `cylinders` | `Optional[int]` | CYL | `None` |
| `max_engine_torque` | `Optional[float]` | ENGTORQ, ft-lb | `None` |
| `cruise_torque` | `Optional[float]` | CRUZTORQ, ft-lb | `None` |
| `hub_weight_lb` | `Optional[float]` | HUBWT | `None` |
| `stop_time_s` | `Optional[float]` | DT, sudden-stoppage time | `None` |
| `rotors` | `List[Rotor]` |  | `[] (factory)` |
| `max_accel_torque` | `Optional[float]` | FAR 25.361(a)(3)(ii) max accelerating torque, ft-lb | `None` |
| `thrust_lb` | `Optional[float]` | lb | `None` |
| `design_yaw_rate_rad_s` | `Optional[float]` | concept real yaw rate (25.371) | `None` |
| `design_pitch_rate_rad_s` | `Optional[float]` | concept real pitch rate (25.371) | `None` |
| `engine_mass_item` | `str` |  | `''` |
| `prop_mass_item` | `str` |  | `''` |
| `thrust_line_aft` | `Tuple[float, float, float]` |  | `(0.0, 0.0, 0.0)` |
| `thrust_line_fwd` | `Tuple[float, float, float]` |  | `(0.0, 0.0, 0.0)` |
| `prop_direction` | `RotorDirection` |  | `RotorDirection.CLOCKWISE` |
| `mounted_on` | `Optional[str]` | "fuselage" \| "wing" | `None` |
| `windmill_drag_cd` | `Optional[float]` |  | `None` |

### `Rotor`

A turbine or compressor rotor, used for sudden-stoppage and gyro loads.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `diameter_in` | `float` | rotor diameter, inches | `**required**` |
| `weight_lb` | `float` | rotor weight, lb | `**required**` |
| `max_rpm` | `float` | signed; clockwise (pilot's view) is positive | `**required**` |
| `rotor_type` | `RotorType` |  | `RotorType.TURBINE` |
| `inertia` | `Optional[float]` | measured polar inertia, slug-ft^2 (overrides geometry) | `None` |

### `WeightInput`

The single shared weight database read by every mass-properties module.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `estimation` | `Optional[WeightEstimationInput]` |  | `None` |
| `items` | `List[MassItem]` |  | `[] (factory)` |
| `envelope` | `Optional[WeightEnvelopeInput]` |  | `None` |
| `cg_cases` | `List[CgCase]` |  | `[] (factory)` |
| `max_landing_weight_lb` | `float` | MLW -- SSOT (G-4); moved off LandingInput | `0.0` |
| `max_takeoff_weight_lb` | `float` | MTOW -- SSOT (G-14); a single CG-independent | `0.0` |
| `max_zero_fuel_weight_lb` | `float` | MZFW -- SSOT (note 63 D-63.5); 0 = not entered. | `0.0` |

### `WeightEstimationInput`

Mission inputs for WTESTIMA (the statistical weight estimate).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `airplane` | `str` |  | `''` |
| `max_continuous_hp` | `float` | HP -- combined total; override value (see class doc) | `0.0` |
| `override_max_continuous_hp` | `bool` | use the stored total instead of the engine sum | `False` |
| `engine_count` | `int` | NOENGS; 0 = derive from len(Project.engines) (#385, OV-1) | `0` |
| `seats` | `int` | SEATS (170 lb each) -- total occupant seats | `1` |
| `crew` | `int` | flight crew (170 lb each); part of the operating | `1` |
| `cruise_hours` | `float` | HOURS on full tanks at cruise power | `0.0` |
| `baggage_lb` | `float` | BAG | `0.0` |
| `pressurized` | `bool` | P$ = "P" | `False` |
| `engine_weight_type` | `EngineWeightType` |  | `EngineWeightType.RECIP_4CYCLE` |

### `MassItem`

One row of the weight database: a component's weight and station.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `name` | `str` |  | `**required**` |
| `weight_lb` | `float` | lb | `**required**` |
| `x` | `float` |  | `0.0` |
| `y` | `float` |  | `0.0` |
| `z` | `float` |  | `0.0` |
| `ixx` | `float` |  | `0.0` |
| `iyy` | `float` |  | `0.0` |
| `izz` | `float` |  | `0.0` |
| `kind` | `MassItemKind` |  | `MassItemKind.EMPTY` |
| `component` | `Optional[MassComponent]` |  | `None` |
| `consumable` | `bool` |  | `False` |
| `usable_fuel` | `bool` |  | `False` |
| `wing_fraction` | `float` |  | `0.0` |
| `carriage` | `WingCarriage` |  | `WingCarriage.PANEL` |
| `gear` | `Optional[GearLeg]` |  | `None` |

### `WeightEnvelopeInput`

Structural weight/CG limits for WTENV (the discretionary-loading envelope).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `gross_weight` | `float` |  | `0.0` |
| `aft_gross_pct_mac` | `float` | % MAC | `0.0` |
| `fwd_gross_pct_mac` | `float` | % MAC | `0.0` |
| `fwd_regardless_pct_mac` | `float` | % MAC | `0.0` |
| `fwd_regardless_weight` | `float` |  | `0.0` |
| `wing_surface` | `str` |  | `'wing'` |
| `xlemac` | `Optional[float]` |  | `None` |
| `mac` | `Optional[float]` |  | `None` |
| `fuselage_nose_x` | `Optional[float]` |  | `None` |
| `fuselage_tail_x` | `Optional[float]` |  | `None` |

### `CgCase`

One weight / centre-of-gravity case balanced over the flight envelope.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `name` | `str` |  | `**required**` |
| `weight_lb` | `float` | lb | `**required**` |
| `xcg` | `float` |  | `**required**` |
| `zcg` | `float` |  | `**required**` |
| `analyses` | `set[AnalysisKind]` |  | `{<AnalysisKind.FLIGHT: 'flight'>} (factory)` |
| `role` | `Optional[GroundCaseRole]` |  | `None` |
| `loading` | `Optional[LoadingDefinition]` |  | `None` |

### `LoadingDefinition`

Which useful load is aboard for one weight/CG case (decision **D-25**).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `aboard` | `List[str]` |  | `[] (factory)` |
| `fractions` | `dict[str, float]` |  | `{} (factory)` |
| `ballast` | `Optional[MassItem]` |  | `None` |

### `GeometryInput`

The single geometry source of truth (Step G1): parametric layout, the WINGGEOM lifting-surface planforms, and the fuselage outline.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `surfaces` | `List[SurfaceInput]` |  | `[] (factory)` |
| `parametric` | `Optional[LayoutInput]` |  | `None` |
| `fuselage` | `Optional[FuselageOutline]` |  | `None` |
| `empennage` | `Optional[EmpennageInput]` |  | `None` |
| `landing_gear` | `Optional[LandingGearGeometry]` |  | `None` |

### `SurfaceInput`

One aerodynamic surface for WINGGEOM, defined by its edge polylines.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `name` | `str` |  | `**required**` |
| `leading_edge` | `List[Tuple[float, float]]` |  | `**required**` |
| `trailing_edge` | `List[Tuple[float, float]]` |  | `**required**` |
| `symmetric` | `bool` |  | `True` |
| `elements` | `int` |  | `20` |
| `tip_cap_width_in` | `float` | rounded tip-cap width, in; 0 = square tip (OV-4) | `0.0` |
| `ref_axis_pct` | `Optional[float]` | fraction of chord; None -> not entered (R-7c) | `None` |
| `front_spar_x_in` | `Optional[float]` | fuselage station, in; None -> derived default (OR-121) | `None` |
| `rear_spar_x_in` | `Optional[float]` | fuselage station, in; None -> derived default (OR-121) | `None` |
| `sob_y_in` | `Optional[float]` | side-of-body butt line, in; None -> assumed fallback (BM-1) | `None` |
| `hinge_line` | `List[Tuple[float, float]]` | control hinge axis; empty = not entered (D-54.1) | `[] (factory)` |
| `control_load_mode` | `str` |  | `'smeared'` |
| `hinges_span_in` | `List[float]` | in | `[] (factory)` |
| `actuator_span_in` | `float` | in | `0.0` |

### `LayoutInput`

General configuration & layout: what the polylines cannot carry.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `datum_x` | `float` | fuselage station of the nose datum reference, in | `0.0` |
| `dihedral_deg` | `float` | geometric dihedral | `0.0` |
| `root_waterline_z` | `float` | waterline of the root chord (25% MAC reference), in | `0.0` |
| `tail_type` | `TailType` | empennage arrangement | `TailType.CONVENTIONAL` |
| `h_tail_z` | `float` | h-tail vertical offset from root_waterline_z, in | `0.0` |
| `htail_dihedral_deg` | `float` | declared stabilizer dihedral, deg (physics deferred, D-54.8) | `0.0` |

### `FuselageOutline`

The fuselage body outline: cross-sections ordered nose -> tail (Step G1).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `sections` | `List[FuselageSection]` |  | `[] (factory)` |
| `body_drag_waterline_z` | `float` | 0 -> derived (zw), marked assumed | `0.0` |
| `airplane_length_in` | `float` | LF; 0 -> derived from the outline length | `0.0` |
| `beam_waterline_z` | `float` |  | `0.0` |

### `EmpennageInput`

Single-source empennage + control-surface geometry (Step G6).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `htail` | `Optional[TailLoadsInput]` |  | `None` |
| `vtail` | `Optional[VTailLoadsInput]` |  | `None` |

### `LandingGearGeometry`

Single-source landing-gear geometry (Step G6b).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `main_gear` | `LandingGearInput` |  | `LandingGearInput() (factory)` |
| `nose_gear` | `LandingGearInput` |  | `LandingGearInput() (factory)` |
| `tread_in` | `float` | TREAD (distance between main wheels) | `0.0` |

### `FuselageSection`

One fuselage cross-section station for the body outline (Step G1).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `x` | `float` |  | `**required**` |
| `width` | `float` |  | `**required**` |
| `height` | `float` |  | `**required**` |
| `z_centre` | `Optional[float]` |  | `None` |

### `TailLoadsInput`

Geometry/aero inputs for SELECT's rational horizontal-tail loads (Ch 9).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `aspect_ratio_wing` | `float` | [D] ARW (downwash; from the wing planform) | `0.0` |
| `aspect_ratio_htail` | `float` | [D] ARHT (tail lift slope) | `0.0` |
| `htail_area_sqft` | `float` | [D] ST | `0.0` |
| `htail_semispan_in` | `float` | [D] BLHTAIL (tail semi-span, inches) | `0.0` |
| `xt25` | `float` | [D] fuselage station of 25% tail MAC | `0.0` |
| `xt50` | `float` | [D] fuselage station of 50% tail MAC | `0.0` |
| `elevator_area_sqft` | `float` | [D] SE (total elevator area) | `0.0` |
| `elevator_fwd_hinge_sqft` | `float` | [D] SEFWDHL | `0.0` |
| `elevator_aft_hinge_sqft` | `float` | [D] SEAFTHL | `0.0` |
| `tail_incidence_deg` | `float` | IT (WL to tail chord) | `0.0` |
| `wing_zero_lift_cruise_deg` | `float` | IW, cruise config | `0.0` |
| `wing_zero_lift_enroute_deg` | `float` | IW, enroute config | `0.0` |
| `wing_zero_lift_landing_deg` | `float` | IW, landing config | `0.0` |
| `elevator_effectiveness` | `float` | dalpha/ddelta_e as a fraction of AHT | `0.0` |
| `elevator_te_up_deg` | `float` | EUP (full trailing-edge-up) | `0.0` |
| `elevator_te_down_deg` | `float` | EDN (full trailing-edge-down) | `0.0` |
| `wing_lift_slope_per_rad` | `float` | AW (gust downwash relief 1 - 36*aw/ARW) | `0.0` |
| `stabiliser` | `str` | STABILISER_TYPES code | `'F'` |
| `stabiliser_incidence_nu_deg` | `Optional[float]` | required unless F (fixed) | `None` |
| `stabiliser_incidence_nd_deg` | `Optional[float]` | required unless F (fixed) | `None` |
| `tail_stall_alpha_deg` | `float` | \|alpha_tail\| limit (Torenbeek p326) | `14.32` |
| `clh_max` | `Optional[float]` | \|C_L,h\| limit; blank -> Roskam Pt VII p44 by type | `None` |

### `VTailLoadsInput`

Geometry/aero inputs for SELECT's rational vertical-tail loads (Ch 9).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `vtail_area_sqft` | `float` | [D] SV | `0.0` |
| `vtail_span_in` | `float` | [D] BLHTAIL (vertical-tail span, inches) | `0.0` |
| `vtail_mac_in` | `float` | [D] VMAC (inches; VMAC_ft = VMAC_in/12) | `0.0` |
| `aspect_ratio_vtail` | `float` | [D] ARVT | `0.0` |
| `xv25` | `float` | [D] fuselage station of 25% vtail MAC | `0.0` |
| `xv50` | `float` | [D] fuselage station of 50% vtail MAC (ONENGOUT camber load) | `0.0` |
| `rudder_area_sqft` | `float` | [D] SR | `0.0` |
| `rudder_fwd_hinge_sqft` | `float` | [D] SRFWDHL | `0.0` |
| `rudder_aft_hinge_sqft` | `float` | [D] SRAFTHL | `0.0` |
| `wing_span_in` | `float` | [D] B (inches; IZZ uses B_ft = B_in/12; from the wing planform) | `0.0` |
| `rudder_deflection_deg` | `float` | RD (full rudder) | `0.0` |
| `rudder_large_deflection_factor` | `float` | EFV (subr 10000 chart; ~1.0) | `1.0` |
| `izz_slugft2` | `float` | 0 -> compute the default IZZ | `0.0` |
| `vtail_root_waterline_z` | `float` | 0 -> derived, marked assumed | `0.0` |
| `vtail_stall_alpha_deg` | `Optional[float]` | \|alpha_vtail\| limit, deg | `None` |

### `LandingGearInput`

One landing-gear leg's strut geometry for LANDLOAD (tricycle gear only).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `axle_compressed` | `Tuple[float, float]` | (X, Z) at 25% (oleo) / 100% (spring) deflection | `(0.0, 0.0)` |
| `axle_static` | `Tuple[float, float]` | (X, Z) static | `(0.0, 0.0)` |
| `axle_extended` | `Tuple[float, float]` | (X, Z) fully extended (reference) | `(0.0, 0.0)` |
| `rolling_radius_in` | `float` | RM / RN | `0.0` |
| `strut` | `str` | a STRUT_TYPES code; normalised in __post_init__ | `'O'` |
| `carrier` | `Optional[GearCarrier]` | BODY \| WING -- no default (G-2) | `None` |
| `attach` | `Tuple[float, float, float]` | (X, Y, Z) trunnion / airframe node, in | `(0.0, 0.0, 0.0)` |
| `weight_lb` | `float` | whole leg, trunnion down (G-12a) | `0.0` |

### `StructuralSpeedsInput`

Inputs for STRSPEED (design speeds & limit maneuver load factors).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `category` | `str` | a CATEGORIES code; normalised in __post_init__ | `'N'` |
| `weight_lb` | `float` | lb | `0.0` |
| `occupants` | `Optional[int]` | total souls on board; the FAR 23 seat-limit | `None` |
| `wing_area_sqft` | `Optional[float]` | else read from geometry wing | `None` |
| `vh_kt` | `float` | max speed at sea level (KEAS) | `0.0` |
| `shoulder_altitude_ft` | `float` | for the MC/MD Mach numbers AND the | `0.0` |
| `wing_surface` | `str` |  | `'wing'` |
| `chosen_vc` | `Optional[float]` |  | `None` |
| `chosen_vd` | `Optional[float]` |  | `None` |
| `chosen_va` | `Optional[float]` |  | `None` |
| `chosen_vf` | `Optional[float]` |  | `None` |
| `chosen_n` | `Optional[float]` | chosen positive maneuver load factor | `None` |
| `chosen_nneg` | `Optional[float]` | chosen negative maneuver load factor | `None` |
| `mach_limit` | `Optional[MachLimitInput]` | MACHLIM inputs (Project.speeds.mach_limit) | `None` |
| `vd_basis` | `VdBasis` |  | `VdBasis.SPEED_RATIO` |
| `mach_margin_min` | `Optional[float]` | None -> MACH_MARGIN_DEFAULT (0.07) | `None` |
| `mach_margin_basis` | `Optional[str]` | rational-analysis / HSPF justification | `None` |
| `vb_kt` | `Optional[float]` | KEAS | `None` |
| `no_yellow_arc` | `bool` | turbine / 23.335(b)(4): use VMO/MMO | `False` |
| `target_vne` | `Optional[float]` | desired never-exceed VNE (KEAS) | `None` |
| `target_vno` | `Optional[float]` | desired max structural cruise VNO (KEAS) | `None` |
| `target_vmo` | `Optional[float]` | desired max operating VMO (KEAS, turbine) | `None` |
| `target_mmo` | `Optional[float]` | desired max operating MMO (Mach, turbine) | `None` |
| `target_vfe` | `Optional[float]` | desired flap extended VFE (KEAS) | `None` |

### `MachLimitInput`

Inputs for MACHLIM (the Mach-limit lines on the flight-limits diagram).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `max_operating_altitude_ft` | `float` | ft | `0.0` |
| `increment_ft` | `float` | ft | `1000.0` |

### `AeroInput`

The aerodynamic-input database read by AIRLOADS (one entry per surface).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `surfaces` | `List[AeroSurfaceInput]` |  | `[] (factory)` |

### `AeroSurfaceInput`

Per-surface aerodynamic inputs AIRLOADS needs on top of the WINGGEOM planform.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `name` | `str` |  | `'wing'` |
| `section_slope` | `float` | mo, section lift-curve slope, per degree | `0.1075` |
| `taper_ratio` | `float` | tip chord / centreline chord (for TAU) | `0.0` |
| `tip_ratio` | `float` | rounded-tip width / semi-span (for TAU) | `0.0` |
| `tau` | `Optional[float]` | override; else computed from taper/tip ratio | `None` |
| `twist` | `List[Tuple[float, float]]` | (Y, zero-lift angle deg), inboard->outboard | `[] (factory)` |
| `target_cl` | `float` | wing CL the combined distribution is evaluated at | `1.0` |
| `profile_drag` | `List[Tuple[float, float]]` | (Y, CDO) | `[] (factory)` |
| `section_cm` | `List[Tuple[float, float]]` | (Y, CM) | `[] (factory)` |
| `sweep_deg` | `float` | deg | `0.0` |
| `design_mach` | `float` |  | `0.0` |

### `AeroCoefficientsInput`

Airplane-less-tail aerodynamic coefficient sets -- ``Project.aero_coeffs``.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `cruise` | `Optional[AeroCoeffSet]` |  | `None` |
| `flaps_down` | `Optional[AeroCoeffSet]` |  | `None` |
| `fuselage_moment` | `Optional[FuselageMomentInput]` |  | `None` |
| `lateral_body_aero` | `Optional[LateralBodyAeroInput]` | v54, L-7 | `None` |
| `clmax_clean` | `float` |  | `0.0` |
| `clmax_clean_neg` | `float` |  | `0.0` |
| `clmax_flap` | `float` |  | `0.0` |

### `AeroCoeffSet`

One configuration's airplane-less-tail aerodynamic coefficients.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `name` | `str` | "CRUISE" \| "LANDING" \| "ENROUTE" | `**required**` |
| `lift` | `Tuple[float, float, float, float, float]` | C0..C4 (CL vs alpha deg) | `**required**` |
| `drag` | `Tuple[float, float, float, float, float]` | D0..D4 (CD vs CL) | `**required**` |
| `moment` | `Tuple[float, float, float, float, float]` | M0..M4 (CM vs alpha deg) | `**required**` |
| `stall_cl` | `float` |  | `0.0` |
| `neg_stall_cl` | `float` |  | `0.0` |
| `flaps_down` | `bool` |  | `False` |

### `FuselageMomentInput`

Munk slender-body fuselage pitching-moment increment (Step G4).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `enabled` | `bool` |  | `False` |
| `d_cm_dalpha` | `float` | per degree; added to the airplane-less-tail M1 | `0.0` |

### `LateralBodyAeroInput`

Lumped wing-body lateral aero in sideslip -- ``Cy_beta`` / ``Cn_beta`` (L-7).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `enabled` | `bool` |  | `False` |
| `cy_beta` | `Optional[float]` | per degree; None -> DATCOM 5.2.1.1 | `None` |
| `cn_beta` | `Optional[float]` | per degree about xw; None -> DATCOM 5.2.3.1 | `None` |

### `FlightLoadsInput`

Inputs for FLTLOADS (the V-n flight envelope + balancing tail loads).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `xtc` | `float` |  | `0.0` |
| `xtf` | `float` |  | `0.0` |
| `mn` | `float` |  | `0.1` |
| `altitudes_ft` | `List[float]` | ft | `[0.0] (factory)` |

### `WingMassInput`

Inputs for WINGINER (the spanwise wing-mass *shape* + load cases).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `tip_root_density_ratio` | `float` |  | `1.0` |
| `inboard_rib_y` | `float` |  | `0.0` |
| `surface` | `str` |  | `'wing'` |
| `panel_weight_override_lb` | `Optional[float]` | lb | `None` |
| `cases` | `List[WingLoadCase]` |  | `[] (factory)` |

### `WingLoadCase`

One critical wing condition WINGINER/NETLOADS evaluate (WINGINER.BAS 1660-1710).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `name` | `str` | "PHAA" / "ACRL" / "TORS" / ... | `**required**` |
| `case` | `Optional[int]` |  | `None` |
| `nz` | `Optional[float]` |  | `None` |
| `nx` | `Optional[float]` |  | `None` |
| `unbal_moment` | `Optional[float]` | blank = derived on ACRL (D-52.2, v69) | `None` |
| `cl` | `Optional[float]` |  | `None` |
| `v_eas_kt` | `Optional[float]` | KEAS | `None` |
| `cg` | `Optional[str]` | mass state: a FLIGHT CG case name (D-63.6) | `None` |

### `FuselageMassInput`

Inputs for the fuselage net-load distribution (SELECT / Ref 1 Ch 15).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `stations` | `List[FuselageStation]` |  | `[] (factory)` |
| `stations_are_override` | `bool` |  | `False` |

### `FuselageStation`

One longitudinal fuselage reference station for the net-load integration.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `x` | `float` |  | `**required**` |
| `weight_lb` | `float` | lb | `0.0` |
| `y` | `float` |  | `0.0` |
| `z` | `float` |  | `0.0` |

### `TailMassInput`

Surface mass for one empennage surface's distributed inertia (plan 09 T-3).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `surface` | `str` | "htail" \| "vtail" | `'htail'` |
| `panel_weight_lb` | `float` | whole surface (both sides for the h-tail) | `0.0` |
| `weight_is_override` | `bool` |  | `False` |

### `SelectInput`

Inputs for SELECT's critical-load search (Ch 9) beyond the V-n matrix.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `full_down_aileron_deg` | `float` | deg | `0.0` |
| `basic_airfoil_cm` | `float` |  | `0.0` |
| `wing_weight_lb` | `float` | lb | `0.0` |

### `AileronLoadsInput`

Inputs for AILERON (FAR 23.349 / 23.455 / CAM 3.222), Ref 1 Ch 16.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `down_deflection_deg` | `float` | ADEG (full trailing-edge-down, +) | `0.0` |
| `up_deflection_deg` | `float` | AUPDEG (full trailing-edge-up, magnitude) | `0.0` |
| `area_fwd_hinge_sqft` | `float` | SAFWD | `0.0` |
| `area_aft_hinge_sqft` | `float` | SAAFT | `0.0` |
| `surface` | `str` |  | `'aileron'` |
| `inboard_y_in` | `Optional[float]` | surface inboard butt line, in | `None` |
| `outboard_y_in` | `Optional[float]` | surface outboard butt line, in | `None` |
| `hinges_span_in` | `List[float]` | hinge butt lines, in | `[] (factory)` |
| `actuator_span_in` | `float` | actuator butt line, in; 0 = not entered | `0.0` |

### `FlapLoadsInput`

Inputs for FLAPLOAD (FAR 23.345 / 23.457), Ref 1 Ch 17.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `gust_load_factor` | `float` | NG (flaps-extended gust limit factor) | `0.0` |
| `flap_area_one_side_sqft` | `float` | SF | `0.0` |
| `flap_deflection_deg` | `float` | DELTA | `0.0` |
| `flap_chord_ratio` | `float` | E = flap chord / wing chord | `0.0` |
| `nacelle_frontal_area_sqft` | `float` | AF (nacelle or fuselage frontal area) | `0.0` |
| `engine_butt_line_in` | `float` | BLPROP (0 -> fuselage-mounted) | `0.0` |
| `surface` | `str` |  | `'flap'` |
| `inboard_y_in` | `Optional[float]` | surface inboard butt line, in | `None` |
| `outboard_y_in` | `Optional[float]` | surface outboard butt line, in | `None` |
| `hinges_span_in` | `List[float]` | hinge butt lines, in | `[] (factory)` |
| `actuator_span_in` | `float` | actuator butt line, in; 0 = not entered | `0.0` |

### `TabLoadsInput`

Inputs for TABLOADS: the set of control-surface tabs to size (Ref 1 Ch 18).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `tabs` | `List[TabSpec]` |  | `[] (factory)` |

### `TabSpec`

One control-surface tab for TABLOADS (FAR 23.409 / CAM 3.224), Ref 1 Ch 18.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `surface` | `str` | host surface (wing/htail/vtail) | `'htail'` |
| `mac_in` | `float` | MACTAB (tab MAC chord, in) | `0.0` |
| `area_sqft` | `float` | STAB (tab area, sq ft; STAB_in = area_sqft*144) | `0.0` |
| `station_in` | `float` | BL (wing/htail) or WL (vtail) of tab MAC | `0.0` |
| `airfoil_chord_in` | `float` | CAIRFOIL (host-airfoil chord at the tab MAC, in) | `0.0` |
| `deflection_deg` | `float` | DELTATAB (max tab deflection, deg) | `0.0` |

### `OneEngineOutInput`

Inputs for ONENGOUT (FAR 23.367, Reference 1 Ch 11; ONENGOUT.BAS).

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `thrust_decay_time_s` | `float` | TIME2DECAY (thrust -> 0) | `0.0` |
| `windmill_drag_time_s` | `float` | TIME2DRAG (windmill drag -> max) | `0.0` |
| `rudder_travel_time_s` | `float` | INCTIMERUD (time to full rudder) | `0.0` |
| `time_step_s` | `float` | DT (Euler step; program suggests 0.05) | `0.05` |
| `failed_engine_index` | `int` | which Project.engines[] entry fails | `0` |
| `use_takeoff_power` | `bool` | MAXHP = take-off HP (else max-continuous) | `False` |
| `altitude_ft` | `Optional[float]` | VC/VD; default: Project.speeds.shoulder_altitude_ft | `None` |
| `speeds_kt` | `List[float]` | default: [VC, VD, VMC or VS] from speeds | `[] (factory)` |
| `izz_slugft2` | `float` | 0 -> from the mass-basis FLIGHT loading | `0.0` |
| `xcg_in` | `float` | 0 -> from the mass-basis FLIGHT loading | `0.0` |
| `vmc_kt` | `Optional[float]` | minimum control speed, KEAS, cited; blank -> VS substituted | `None` |
| `takeoff_altitude_ft` | `float` | the low-end (VMC/VS) case's altitude | `0.0` |

### `LandingInput`

Inputs for the ground-load conditions (LGFACTOR + LANDLOAD), Ref 1 Ch 20.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `strut_stroke_in` | `float` | SSTRUT (fully extended -> compressed) | `0.0` |
| `tire_od_in` | `float` | OD (outer diameter of tyre) | `0.0` |
| `hub_diameter_in` | `float` | ID (hub diameter) | `0.0` |
| `lift_factor` | `float` | L (wing lift factor; 0.667 FAR 23.473, 1.0 FAR 25.473) | `0.667` |
| `tail_down_angle_deg` | `float` | GRA(3) (ground line to WL, tail-down bump) | `0.0` |
| `airplane_load_factor` | `Optional[float]` |  | `None` |

### `LraMeshInput`

How finely the LRA beam model is meshed -- one count per member.

| Field | Type | Units / notes | Default |
| --- | --- | --- | --- |
| `wing_grids` | `Optional[int]` |  | `None` |
| `fuselage_grids` | `Optional[int]` |  | `None` |
| `htail_grids` | `Optional[int]` |  | `None` |
| `vtail_grids` | `Optional[int]` |  | `None` |

## Enumerations

- **`AnalysisKind`** — `FLIGHT` = `'flight'`, `GROUND` = `'ground'`. Which analysis a weight/CG case is run for (decision G-3).
- **`EngineLayout`** — `SINGLE_NOSE` = `'1N'`, `TWIN_WING` = `'2W'`, `QUAD_WING` = `'4W'`. Where the engines sit, constrained to the layouts the suite models.
- **`EngineType`** — `RECIPROCATING` = `'R'`, `TURBOPROP` = `'T'`.
- **`EngineWeightType`** — `RECIP_4CYCLE` = `'RF'`, `RECIP_2CYCLE` = `'RT'`, `TURBOCHARGED` = `'TC'`, `TURBOPROP` = `'TP'`, `LIQUID_COOLED` = `'LC'`. Engine family used by WTESTIMA's installed-weight correlation (WTESTIMA.BAS     lines 230-290): the two-letter codes of the original program.
- **`GearCarrier`** — `BODY` = `'body'`, `WING` = `'wing'`. Which structure carries a landing-gear leg's reaction (decision G-2).
- **`GearLeg`** — `MAIN` = `'main'`, `NOSE` = `'nose'`. Which landing-gear leg a weight-database row belongs to (#384).
- **`GroundCaseRole`** — `AFT_MAX_LANDING` = `'aft_max_landing'`, `FWD_MAX_LANDING` = `'fwd_max_landing'`, `FWD_LIGHT` = `'fwd_light'`. The role a ``GROUND`` case plays in LANDLOAD's three-loading contract (G-3a).
- **`MassComponent`** — `WING` = `'wing'`, `FUSELAGE` = `'fuselage'`, `HTAIL` = `'htail'`, `VTAIL` = `'vtail'`. Which structural component a mass item is carried by (plan 11 B-2, step B1).
- **`MassItemKind`** — `EMPTY` = `'empty'`, `MINIMUM` = `'minimum'`, `DISCRETIONARY` = `'discretionary'`. Where a mass item sits in the loading hierarchy of WTONECG/WTENV.
- **`RotorDirection`** — `CLOCKWISE` = `'CW'`, `COUNTERCLOCKWISE` = `'CC'`.
- **`RotorType`** — `COMPRESSOR` = `'C'`, `TURBINE` = `'T'`.
- **`TailType`** — `CONVENTIONAL` = `'conventional'`, `T_TAIL` = `'t_tail'`, `V_TAIL` = `'v_tail'`, `CRUCIFORM` = `'cruciform'`. Empennage arrangement -- a **structural** classification (note 44 OR-134).
- **`VdBasis`** — `SPEED_RATIO` = `'speed_ratio'`, `MACH_MARGIN` = `'mach_margin'`. Which regulatory route sets the design dive speed VD (F25-2).
- **`WingCarriage`** — `PANEL` = `'panel'`, `POINT` = `'point'`. How the wing reacts a ``WING``-carried mass part (design note 63, D-63.3).

