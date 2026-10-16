# One owner per geometry quantity on the Geometry page: the parametric wing, the fuselage scalars and the control-surface areas (design note 69)

**Owner:** @Sean074 · **Reviewers:** — *(design note 28 MD-6)*

**Status: AGREED 2026-10-16 — no code** (owner, in session, under the solo
profile — rule 1's working-alone branch). PROPOSED the same day; the owner ruled
Q1–Q4 of §3 **as recommended** (Q1 delete, Q2 move, Q3 accept, Q4 park), so
D-69.1…D-69.12 stand as written. Drafted for #377, #378 and #379, which share one
defect class: the Geometry page asks for a quantity that the geometry entered on
the same page already determines, stores both, and ties them together loosely or
not at all. This note sets one rule for the class (D-69.1) and applies it field by
field. Implementation is one tier-L step on `dev/v0.9.0`; D-69.11 (data only) may
land first.

**Tier L.** Schema change (v76 → v77: fields removed from `LayoutInput`, two
moved to `FuselageOutline`), and the page sections are restructured.
**No delivered load moves on any shipped example except `atr42_100`.** That one
moves by its own data correction (D-69.11), not by any mechanism in this note.
The Appendix A oracle and the twin closures are untouched (G-69.1).

**Conventions:** `CONVENTIONS.md` §2 (airplane axes: stations, butt lines and
waterlines in inches) and §7 (single owners; this note removes nine stored
copies and adds no owner). **Theory:** no new physics. Every derivation is an
existing owned computation: the WINGGEOM strip integral
(`wing_geometry.surface_properties`), the D-54.1 boundary-line split
(`tail_geometry.control_hinge_areas`) and the outline summary
(`derived_geometry.fuselage_summary`). **Precedent:**
- note 39 OV-1/OV-9/OV-12, cited in the code as "note 36": falsy-derive, typed-overrides, the collapsed-override caption, no load moves on a fully specified project;
- note 54 D-54.1: tail scalars blank-derive from the boundary lines;
- #70 / PB-17: a displayed number that is not the governing number is worse than none;
- #234: the report's Table 1 stopped printing the parametric cross-check;
- note 63 OV-1: a meaning is a typed field, never a name match.

---

## 1. Measurements (2026-10-16, `dev/v0.9.0` at f1354a7)

### 1.1 The parametric wing scalars (#377)

`geometry.parametric` holds five scalars the `wing` polylines determine:
`wing_area_sqft`, `aspect_ratio`, `taper_ratio`, `le_sweep_deg` and
`le_root_x`. **No load module reads them.**
- STRSPEED integrates the planform (`derived_geometry.planform_area_sqft`).
- TAU derives its taper from the polylines (`taper_ratio_from_planform`).

Their readers are three non-load consumers:

| Reader | What it does with them |
|---|---|
| `configuration.configuration_properties` (`configuration.py:681`) | Rebuilds a two-point trapezoid from them (`wing_planform` → `wing_polylines` → `wing_surface`) and integrates *that*. The Geometry page's results table shows span, root and tip chord, MAC, XLEMAC, YLEMAC and AR, plus the tail-volume neutral point, **of the trapezoid, not of the wing the analysis uses.** |
| `fleet.subject_from_project` (`fleet.py:472`, `:486`) | Plots parametric area and AR **in preference to** the planform's. |
| `validation._check_area` / `_check_area_mismatch` (`validation.py:205`, `:259`) | Sign check, and a 5 % area-mismatch warning. AR, taper, sweep and LE station are never compared. |

Plus the seed button (`configuration.parametric_wing_seed`, #95; fixed at #376),
which exists only to copy the planform into these five.

**The page's results table disagrees with the analysis today:**

| Example | Geometry page (trapezoid) MAC / XLEMAC / AR | Stored planform MAC / XLEMAC / AR | XLEMAC apart |
|---|---|---|---|
| `ga6_normal` | 69.35 / **56.73** / 6.10 | 69.28 / **63.62** / 6.09 | 6.9 in (10 % MAC) |
| `atr42_100` | 89.21 / 377.68 / 11.08 | 89.46 / 372.80 / 11.08 | 4.9 in (5.5 % MAC) |
| `concept_regional_jet` | 101.82 / 561.41 / 8.71 | 101.44 / 561.33 / 8.75 | 0.1 in |
| `baron_58` | 65.52 / 66.67 / 7.19 | 65.33 / 66.67 / 7.21 | 0 |
| `concept_heavy` | 70.00 / 217.78 / 8.92 | identical | 0 |

This is #234's finding (GA-6 56.73 vs 63.62), fixed in the report and still live
on the page. Every %MAC the analysis states, and the neutral point printed beside
it on the same page, are in different frames.

**The typed scalars against the planform:**

| Example | Area (typed vs planform) | AR | Taper |
|---|---|---|---|
| `concept_regional_jet` | 500.0 vs 497.75 (0.45 %) | 8.712 vs 8.751 | 0.25 vs 0.248 |
| `baron_58` | 199.2 vs 198.625 (0.29 %) | 7.186 vs 7.206 | 0.5 vs 0.5 |
| `ga6_normal` | 184.121 vs 184.157 (0.02 %) | 6.095 vs 6.094 | equal |
| `atr42_100`, `concept_heavy` | equal | equal | equal |

**Taper has two derivations** (#377):
- `wing_layout_from_surface` (`configuration.py:142`) uses the first and last polyline points.
- `taper_ratio_from_planform` (`derived_geometry.py:366`) uses the shared inboard-most and outboard-most butt lines.

They agree on every shipped example, including the two three-point (cranked)
wings, and can disagree on a polyline whose LE and TE break at different stations.

### 1.2 The fuselage scalars (#378)

| Field | Today | Readers |
|---|---|---|
| `parametric.fuselage_length`, `_width`, `_height` | **Already never persisted** (`io._LAYOUT_DERIVED`, `io.py:1379`). `sync_geometry_derived` overwrites them from the outline on every run (`derived_geometry.py:1087`). | `configuration.py:471` (fuselage station); `derived_geometry.sob_station` (width; it already falls back to `fuselage_summary`, `:829`); `tail_geometry.py:811` (fin-root fallback, height); `validation.py:212`. |
| `parametric.body_drag_waterline_z` | Entered; 0 → the wing plane (`body_drag_waterline`, `derived_geometry.py:961`). It is also the default for every blank `z_centre` (`fuselage_centreline`). | The FLTLOADS body-drag line; the fuselage beam axis. |
| `empennage.airplane_length_in` (SELECT LF) | Entered; read only through `derived_geometry.airplane_length_in` (`:558`). | SELECT Iyy and default Izz (`select.py:1083`, `:1408`). |

The registry's `resolves` text on `fuselage_length` says "a typed length stands"
with no outline "and seeds the outline when an older file loads". **Neither is
true.** The field is not written to the file, and the #93 gate refuses every
older file.

**LF against the outline length.** The registry comment above
`fuselage_length` calls LF a "candidate 19th duplicate, NOT declared… not held
equal on any fixture". It is held equal on every fixture that has both:

| Example | LF typed | Outline length | Apart |
|---|---|---|---|
| `atr42_100` | 892.8 | 892.8 | 0 |
| `baron_58` | 358.0 | 358.0 | 0 |
| `concept_regional_jet` | 1056.0 | 1056.0 | 0 |
| `ga6_normal` (Appendix A) | 318.264 | 318.26 | 0.0013 % |
| `concept_heavy` | 0 | (no outline) | n/a |

**`atr42_100`'s outline** has 3 sections and no `z_centre`. The body is
therefore placed at the body-drag default, WL 179.64 (the wing plane):
- the high wing's root (WL 170) sits mid-body;
- both gear attach points sit about 70 in below the underside;
- the sources file states that 179.6 as "the body's own section-centre line".

### 1.3 The control-surface areas (#379)

**SA is one aileron, and SF is one flap.** The typed areas match the one-side
polyline integral (`area_per_side`) on every example that has the surface:

| Example | SAFWD + SAAFT vs aileron polyline | SF vs flap polyline | E typed vs polyline (mid-span / area-weighted) |
|---|---|---|---|
| `ga6_normal` (Appendix A) | 6.488 vs 6.474 (0.22 %) | 10.7 vs 10.721 (0.20 %) | **0.27 vs 0.252 / 0.245 (7–9 %)** |
| `atr42_100` | 13.79 vs 13.784 (0.04 %) | 53.6 vs 53.583 (0.03 %) | 0.30 vs 0.279 / 0.286 (5–7 %) |
| `baron_58` | 7.60 vs 7.608 (0.11 %) | no flap surface | n/a |
| `concept_regional_jet` | 15.0 vs 14.991 (0.06 %) | no flap surface | n/a |

- **No example enters an aileron `hinge_line`**, so the SAFWD/SAAFT *split* is not derivable from any shipped geometry. Only the total is.
- The tail controls already work the way #379 asks (note 54 D-54.1, `tail_geometry.py:626-646`; 1 % `PLANFORM_TOLERANCE`, `tail_geometry.py:139`). `CONTROL_PARENT` already lists `aileron` and `flap` (`:354`). Only their area derivation was never extended.

### 1.4 The override marking these fields would use

Note 39's collapsed fields render through `form._collapsed_note`. It warns on a
typed value that disagrees with its owner at `cross_check.CROSS_CHECK_REL` =
**0.1 %** (#243).

On the Appendix A airplane that band would warn against the oracle's own
printed inputs:
- the aileron, 0.22 % apart;
- the flap SF, 0.20 % apart.

The hinge-halves check (`validation.py:1683`) records the same problem and keeps
a 1 % band for it.

**#345 item 5** (a typed zero never warns in `_copy_note`) **does not touch
these fields.** They render through `_collapsed_note`, where 0 *is* blank,
meaning derive. The #377 and #379 bodies say otherwise; this note corrects them.

---

## 2. Decisions (D-69.1 … D-69.12)

| # | Decision | Rationale |
|---|---|---|
| **D-69.1** | **The rule.** A quantity the entered geometry determines has **one owner** in `derived_geometry` (or `tail_geometry` for a control surface). A stored copy is then one of two things. **(a)** A **collapsed override** (note 39 OV-1/OV-9) **when an original-suite program reads it as an input**: the oracle needs it typed, so it stays, falsy-derives, and a typed value is marked. **(b)** **Deleted** when no original-suite program reads it. A copy kept "for display" is neither. | Consolidation over decoration. A copy no oracle input needs has no reason to exist, and every one of them has drifted (§1.1, §1.2). |
| **D-69.2** | **The five parametric wing scalars are deleted** (D-69.1(b); **Q1**). `configuration` is a modern addition with no `.BAS` oracle (`configuration.py:60`), and nothing else reads them for a load. Specifically: <ul><li>`configuration_properties` integrates the stored `wing` surface through the planform owners (`resolved_surfaces`), and its condition is retitled "Wing planform (WINGGEOM)".</li><li>The stability condition takes the planform MAC frame (`MacReference(..., "planform", "wing")`, as `configuration.py:557` already claims).</li><li>`fleet` reads the planform only.</li><li>`validation._check_area_mismatch` and the parametric branch of `_check_area` retire, because nothing remains to disagree.</li><li>Retired: `wing_planform`, `wing_polylines`, `wing_surface`, `wing_layout_from_surface`, `parametric_wing_seed`, `RECORD_SEEDS` and `form._offer_record_seed` / `_seed_record` (with #376's test, which guarded a button that no longer exists).</li><li>A project with no `wing` surface gets configuration's not-ready message naming the surface.</li></ul> | Fixes §1.1's frame split at its source, and **dissolves #377's two-taper problem**: `wing_layout_from_surface` was the second derivation, so `taper_ratio_from_planform` becomes the only one. |
| **D-69.3** | **The three fuselage summaries are deleted** from `LayoutInput`. Readers call `fuselage_summary` directly: <ul><li>`configuration.py:471` (length);</li><li>`sob_station` (width; its parametric read goes and the outline read it already falls back to stays);</li><li>`tail_geometry.py:811` (height);</li><li>`validation.py:212`.</li></ul> `sync_geometry_derived`'s write, the `EXTERNAL_VALUES` / `DISPLAY_ONLY` entries for `fuselage_length` (`field_registry.py:695`, `:721`), the three registry rows and `io._LAYOUT_DERIVED` all retire. | They are already unpersisted in-memory copies (§1.2). The false `resolves` text retires with them. |
| **D-69.4** | **`FuselageOutline` gains the two body scalars**, beside `sections`: <ul><li>**`body_drag_waterline_z`**, moved from `LayoutInput` with unchanged semantics. 0 means the wing plane, through `body_drag_waterline` as today.</li><li>**`airplane_length_in`** (SELECT LF), moved from `EmpennageInput` and made a **collapsed override**. A blank falsy-derives from `fuselage_summary`'s length through `derived_geometry.airplane_length_in`, which is already its single read point, so `select.py` does not change. A typed value overrides and is marked.</li></ul> The "candidate 19th duplicate" comment is replaced by the declared `derived_from` (**Q2**). | LF is an original SELECT input (D-69.1(a)): Appendix A types it, so it stays typed in the oracle and derives elsewhere. The drag waterline defaults the centreline (§1.2), so it belongs with the outline it defaults. |
| **D-69.5** | **The page.** The Geometry page reads, in order: <ol><li>**Surfaces**;</li><li>**Fuselage**: `body_drag_waterline_z`, LF and the outline table under **one** heading, with the derived length, width and height shown as a computed caption under the table, not as fields;</li><li>**Engines** (#380, when it lands);</li><li>**Parametric**: what remains is `dihedral_deg`, `root_waterline_z`, `datum_x`, `h_tail_z`, `htail_dihedral_deg` and `tail_type`, the quantities the polylines cannot carry because they hold no Z;</li><li>**Empennage**;</li><li>the aileron and flap sections;</li><li>gear.</li></ol> The fuselage record and its `sections[]` list are two record prefixes, so the renderer gives them one heading (**Q3**), guarded. | The owner's ask in #378, kept to what the data model supports. |
| **D-69.6** | **One control-surface area owner.** `tail_geometry`'s control-area block (`:626-646`) becomes a function over any `CONTROL_PARENT` member. It returns the one-side area and, when a `hinge_line` is entered, the fwd/aft split, both from `surface_properties` / `control_hinge_areas` as today. The tail scalars and the wing controls both call it. | Rule 3: one integrator, not a second one for the wing controls. |
| **D-69.7** | **Aileron SAFWD / SAAFT become collapsed overrides** that derive only when the `aileron` surface carries a `hinge_line` (the split needs it). Without one they stay typed, and a new consistency warning `aileron_area_mismatch` compares SAFWD + SAAFT with the one-side polyline area at **1 %**. | §1.3: SA is one aileron (all four examples ≤ 0.22 %). No shipped geometry has the hinge, so derivation never fires on an example. The warning is the part #379 can deliver today. |
| **D-69.8** | **Flap SF becomes a collapsed override**, derived from the `flap` surface's one-side area. `flap_area_mismatch` warns at 1 % when typed. | §1.3: SF is one flap (≤ 0.20 % on both examples with a flap surface). |
| **D-69.9** | **Flap E is not derived. It is parked with its number** (rule 6, **Q4**). The polylines give 0.245–0.252 on the Appendix A airplane against the printed **0.27** (7–9 %), and 0.279–0.286 against 0.30 on `atr42_100`. The drawn flap does not carry E as Abbott & von Doenhoff Fig 98 uses it (the reference chord, or the extended chord of a slotted or Fowler flap). A derived E would contradict the oracle's own input by more than the method's sensitivity. It stays typed with no marking; the park entry names the 7–9 %. | A derivation that disagrees with the printed input is not the same quantity. |
| **D-69.10** | **A collapsed override may state its own disagreement band.** The registry gains a per-path band read by `_collapsed_note`, with `CROSS_CHECK_REL` (0.1 %) remaining the default. SAFWD/SAAFT and SF take **1 %**, citing the hinge-halves precedent (`validation.py:1683`) and `PLANFORM_TOLERANCE`. LF keeps 0.1 % (ga6 is 0.0013 %). | Without it, the Appendix A airplane's printed inputs are flagged as errors on the page (§1.4). |
| **D-69.11** | **`atr42_100`'s fuselage is corrected** (#378 part 1): <ul><li>the 18-section outline sconfig generated for the same airplane, every section with `z_centre` (WL 110.2 through the cabin, rising to 131.07 at the tail);</li><li>length (892.8) and maximum section (106.3) unchanged, [A]; nose, tailcone and centreline [E];</li><li>the sources file's "Fuselage beam waterline" entry corrected.</li></ul> Nothing else from sconfig is taken. The nose-gear attach (WL 50 at x 95, below even the new underside, about WL 61) is checked against the [F] front elevation and corrected or explained. | Data, not mechanism. It moves `atr42_100`'s fuselage beam axis by about 70 in, plus the slender-body moment with the section areas. |
| **D-69.12** | **Schema v76 → v77**, one hop, which for each file: <ul><li>moves `geometry.parametric.body_drag_waterline_z` → `geometry.fuselage.body_drag_waterline_z`;</li><li>moves `geometry.empennage.airplane_length_in` → `geometry.fuselage.airplane_length_in`;</li><li>drops the five parametric wing keys;</li><li>creates `geometry.fuselage` with empty `sections` when a moved value is non-zero and none exists.</li></ul> Every example is regenerated through it. The dropped parametric values (`baron_58` 199.2, `concept_regional_jet` 500.0, which differ from their planforms) are recorded in the step's history entry, since nothing reads them after D-69.2. | One bump for all three issues, which was #377 and #378's reason to share a note. |

---

## 3. Questions for the owner

| # | Question | Recommendation |
|---|---|---|
| **Q1** | Delete the five parametric wing scalars (D-69.2), or keep them as collapsed overrides derived from the planform and marked when typed, as #377 was filed? | **Delete.** The only thing they feed that is not a copy of the planform is a different MAC frame from the analysis's (§1.1). Derive-and-mark would keep a field whose correct value is always the planform's. |
| **Q2** | Move LF into the Fuselage record (D-69.4), or leave it on `EmpennageInput` (SELECT's record) as a collapsed override and accept it rendering under Empennage? | **Move.** It is the airplane's length, and its owner is the outline. |
| **Q3** | One "Fuselage" heading over two record prefixes (the scalars and the `sections[]` table): accept a renderer rule that merges adjacent groups sharing a `DISPLAY_GROUPS` title, guarded by a test? | **Accept**, guarded so a merged section's add/remove controls still render once. |
| **Q4** | Park flap E (D-69.9), or derive it at the flap's mid-span and accept the 7–9 % disagreement with Appendix A's printed input on blank? | **Park.** |

---

## 4. Closure gates (G-69.1 … G-69.7)

Benchmark-first (rule 2). Identities exact (`rel_tol=1e-9`) unless stated.

| Gate | Statement | Expected numbers |
|---|---|---|
| **G-69.1** (oracle and delivered-load invariance) | The Appendix A oracle suite (±0.1 %), the twin closures and the Imperial digests pass unchanged. Every delivered load of `ga6_normal`, `baron_58`, `concept_regional_jet` and `concept_heavy` is bit-identical before and after. | Zero diffs. The deleted fields fed no load (§1.1, §1.2); LF, SAFWD/SAAFT and SF stay typed on every example. |
| **G-69.2** (the page's planform is the analysis's) | `configuration`'s planform condition equals `surface_properties` of the stored `wing` surface, and its neutral point is stated in the planform MAC frame. | `ga6_normal` XLEMAC **63.62** (was 56.73), MAC 69.28, AR 6.09. `atr42_100` XLEMAC **372.80** (was 377.68), MAC 89.46. The neutral-point stations are recomputed and stated in the PR. |
| **G-69.3** (LF derives) | A blank LF resolves to `fuselage_summary`'s length; a typed LF governs; SELECT's inertias read the resolved value. | `ga6_normal` blank → 318.26; Iyy scales by (318.26 / 318.264)², i.e. −0.0025 %, inside the oracle band. `atr42_100` 892.8 either way. |
| **G-69.4** (control areas) | A blank SF resolves to the flap's one-side polyline area. An aileron with a `hinge_line` resolves SAFWD/SAAFT to `control_hinge_areas` (one side). The mismatch warnings are silent on every shipped example and fire on a 2 % perturbation. The 1 % band is read from the registry, not spelled in `form.py`. | `ga6_normal` SF blank → 10.721. `atr42_100` → 53.583. Warnings: 0 of 6 example pairs (the largest is 0.22 %). |
| **G-69.5** (schema) | A v76 file loads through the hop. The moved values land on `geometry.fuselage`; the five wing keys are gone. A v77 file round-trips. `applied_hops(76)` names the hop. | Every example regenerated; the dropped values (§D-69.12) listed in the history entry. |
| **G-69.6** (the page) | The Geometry page's section order is D-69.5's. No path under `geometry.parametric` or `geometry.empennage` is a fuselage quantity. The Fuselage heading renders once, with one set of record controls. | Guarded by registry order plus a `test_oracle_gui` render check. |
| **G-69.7** (`atr42_100` data) | `fuselage_centreline` reports `CENTRELINE_ENTERED`, and the summary is unchanged. Every delivered value that moves is listed in the PR with its old and new value. | Centreline WL 110.2–131.07 (was 179.64 flat). Summary (892.8, 106.3, 106.3) unchanged, so derived LF and SOB width are unchanged. |

**Closure tier:** L. This note at AGREED first, then:
- the schema-ledger entry;
- `PROGRAM_SPEC.md` (configuration, AILERON and FLAPLOAD inputs, SELECT LF, the Geometry page);
- `theory_sources.md`: one sentence each for the SF / SA derivation and E's park;
- the regenerated DATA_DICTIONARY and page guide;
- a full-format history fragment;
- a `02_parked.md` entry for flap E.

**Sequencing.** D-69.11 (data only) may land first, alone, as #378 part 1. The rest
is one step. #380 (Engines section) slots into D-69.5's order when it lands, and
#381's three-view draws the corrected outline.
