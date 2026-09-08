# 2026-09-08 — Oracle GUI, oracle report and sectional-CSV review

**Scope (owner-commissioned, 2026-09-07):** a detailed technical review of (1) the
oracle GUI as the interface for entering the analysis inputs, (2) the oracle
technical report for accuracy and readability — a document for the stress
analyst, providing the data to apply and assess the structure without needing to
explain — and (3) the sectional-loads CSV channel for parseability, consistency,
and correctness in airplane-global coordinates per `CONVENTIONS.md` §1. Plus a
summary of Appendix A printed results missing from the report.

**Method.** Working tree on `dev/v0.8.2` as of 2026-09-08 (landing iteration in
flight). Two issue packages built through the GUI itself — `LR-GA6-001_RevA`
(112 pp, Imperial, provenance baselined) and `LR-B58-001_RevA` (120 pp, SI) —
both compiled clean with tectonic (two passes). Every delivered CSV generated
from its owner for both aircraft and parsed with pandas both ways. The GUI
driven live (project load, all fourteen pages, report page end-to-end, fresh
grid/field entry sampled on Geometry/Weight). Appendix A of
`reference/FAR23Loads_Code.pdf` inventoried page-by-page (pp131–250) for the
coverage diff; numerical spot-checks against the printed oracle and against the
documents' own closures throughout.

**Disposition.** Every finding below was filed the same session (rule 5): new
issues **#227–#246**, comments on **#165/#180/#219**, **#171 closed** as fixed
in-tree, and the thirteen unmilestoned defects (#20, #193, #209, #210,
#216–#223, #226) milestoned per their own bodies (recorded on #190).

---

## 1. Verdict

The document is structurally sound and the **LIMIT/SF contract held everywhere
it was checked numerically**: SF stated per case and applied nowhere; `-ULT`
only on the two prescribed families; structural zeros printed with their missing
producer named; Appendix F forces are exact rotations of the ground-line
reactions; the V-n register closes LZW+LT ≈ nz·W and NX = −DX/W on all 80 rows;
fuselage cumulative loads close to ~1e−13; VT mirror cases mirror exactly. The
appendices are unusually well-armored as an FEA hand-off.

It is not ready to leave DRAFT: an attitude-label swap that sends a reader to
the wrong gear geometry (#227), cross-references that deny content the document
carries (#230), boilerplate promising gyroscopic cases that don't exist (#228),
a load table with no SF column (#229), and on the Baron a sign-less OEI input
table (#231) and an incomplete SI conversion (#232). On the GUI, the frozen
results captions still call LIMIT tables ULTIMATE (#239) — the understrength
direction. The CSVs are frame-correct but the gear applied file collapses 33
cases onto 8 identical case strings (#241) and no file states the axis
directions (#242).

## 2. GUI findings

| # | Finding | Filed |
|---|---|---|
| G1 | Module Results captions claim "ULTIMATE loads (= limit × SF)" over LIMIT tables; self-contradicting beside the LIMIT station blocks; also sits over non-load blocks. Frozen (`oracle_app/results.py:116`); the half #192 deferred. | **#239** (0.8.3) |
| G2 | Report page caption states the retired deselection behavior (still-printed-with-reason) vs the agreed silent-omission-and-renumber. | **#237** (0.8.2) |
| G3 | Two "input echo" pointers survived OR-194 (provenance banner; printed Introduction). | **#237** |
| G4 | Row-counter commits stray keystrokes — 4501 rows from one mistyped digit; display showed 1 while state held 4501. | **#244** (0.9.0) |
| G5 | Grid editors drop keystrokes just after opening; a rerun focus-steal ate a typed field once. Platform behavior; document. | #244 rider |
| G6 | Override cross-check warnings fire below display precision ("This is 0.4356 but … says 0.4356"). | **#243** (0.8.3) |
| G7 | Refresh/deep-link silently discards the session's project. Platform; document. | #244 rider |
| G8 | Empty project shows "Traceback (for a bug report)" under expected cannot-run-yet states. | #244 rider |

**Strengths worth keeping verbatim:** the derive/override provenance captions;
the hinge-area cross-checks firing on load; the wing-cases REPLACE warning; the
Landing page's two-frame note; OEO's single-engine N/A statement; DRAFT-by-
default signatures; the build result naming its directory; the provenance
baseline warning, which fired correctly the moment the project was swapped
under a baselined spec.

## 3. Report findings

Fix-before-Rev-A (all 0.8.2): **#227** attitude-label swap + 7–9 double-claimed
(root cause `oracle_sections.py:6771` positional lookup; loads verified right);
**#228** gyro boilerplate unconditioned on engine type; **#229** Appendix B
"every selected case" claim + B.2's missing SF column and truncated footnote
(the no-negative-case substance is #165); **#230** dangling `section_ref` keys
(`flight_envelope_cases` never existed; `tail_loads` retired by OR-129) — plus
the guard that every referenced key exists in the plan; **#231** Baron OEI
butt-line signs + engine-identity flip; **#232** SI residue sweep; **#233**
23.367(a)(2) noun disagreement across intro/methods/safety-factor table
(companion to #178); **#234** the two MAC/XLEMAC pairs with a misattributing
note; **#235** planform provenance as fixed text, wrong on both aircraft in
opposite directions; **#236** the h-tail wing-root-waterline placeholder printed
as an airplane coordinate, unstated; **#238** `ORACLE_REPORT.md` register
missing §3.11/§3.12/V-n rows plus three stale entries.

Polish (0.8.3): **#240** rollup — ft-lb engine-moment channel, single-SMP
per-wheel claim, empty table-continuation page, marker-label collisions, thrust-
line arrow endpoints, inapplicable T-tail boilerplate, "633 kt(EAS)" TAS
mislabel, unprovenanced rod-estimate Iyy, undefined "Reference 1", caption nits.
Already filed elsewhere: number formatting #161; fin-root axis kink #219
(verified: stations 1–2 sit on the raked-root stub chords — real geometry
needing one stated sentence, not a wrong row).

**What checked out numerically** (beyond §1): Table 64 equilibrium; Table 58
resultants vs Table 60 components; EM-01 Fz = −0.75·4.2·W_eng+prop; HT-09's
RH/LH split summing to its total; torsion axes named at every printed torsion;
the applied/cumulative split and free-moment-only rule consistent throughout;
§11's SF=1.0 basis stated in-band with the fin-inertia absence quantified.

## 4. CSV findings

All fifteen files per aircraft parse cleanly (`#` comment headers, comma
delimiter, no locale traps); one 14-column applied shape everywhere; the export
channel is genuinely airplane-global (gear points at the manual's own
axle/contact points at ±tread/2; engine rows at the OR-170 combined CG; wing
rows on the swept, dihedraled LRA with zeros printed and My the free moment;
+RD → +fy verified). Filed: **#241** case identity (33 gear cases on 8 Case
strings; `AppliedLoad.case_id` populated but unemitted; Baron engines share one
Case string); **#242** no axes-direction statement in any delivered file, the
control-surface `Fz` label on a lateral normal, `tail_span`'s unstated force
frame, and the two meanings of `Axis`; **#245** the channel gap — the applied
CSVs ship only from `app/`'s export page while the oracle package's `data/` is
deferred (OR-42), so the report's own reader cannot obtain its appendices as
files from the oracle GUI.

## 5. Appendix A coverage diff

Filed as **#246** (eight owner decisions): WTESTIMA's entire output; MACHLIM's
MNE/MFC values and V(FC) column; the airplane-less-tail drag polar; the
air/inertia split and WINGINER's three unit cases (plus densities and panel
IXX); SELECT h-tail CP-of-total and per-condition unbalanced moments; TAILDIST's
per-BL/per-WL station-chord pressure tables; WINGGEOM's wing element table;
LANDLOAD's ground-line unbalanced moments. Deliberate exclusions already
registered elsewhere (input echo OR-194, flaps-down #163, WTENV vertex names,
stall curve OR-40, FS-50% OR-112, 23.427(a) M1-4, no engine column OR-197) are
not re-flagged. The full page-cited inventory is in the session record.

## 6. Existing-issue pass

Requested alongside the filing: #171 closed (all seven examples verified at
2-space indent in-tree); #180 commented (site count grew 2 → 4); #219 commented
(numerical verification + report-statement suggestion); #165 commented (report
evidence). Milestones assigned: 0.8.3 → #216, #219, #220, #222, #223; 0.9.0 →
#193, #209, #210, #217, #218, #221, #226; 1.0.0 → #20. #176, #170, #172, #173,
#175 spot-checked as still valid and left as milestoned.
