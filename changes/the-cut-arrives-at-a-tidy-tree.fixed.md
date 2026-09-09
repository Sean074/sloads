- **The notes directory and the backlog agree with reality at the 0.8.2 cut
  (issue #190, tier S, 2026-09-08).** The 2026-09-04 project review's direct
  answer to "the backlog and notes are bloated and uncoordinated", taken in one
  pass ahead of the cut. Status headers: notes 46, 47 and 50 now say SHIPPED
  with the step that shipped them (50 was found stale by the same sweep — the
  issue predated it), note 48 says its 0.8.2 half shipped and note 49 carries
  OR-85/86, and note 44 says every agreed iteration through §22 is built rather
  than "nothing built". Archived to `docs/40_history/` under their own numbers
  (the notes-35–43 precedent): 09, 11, 24, 32, 34, 45, 46, 47, 48 and 50, with
  every inbound link in docs, code docstrings and tests re-pointed — except the
  two in frozen `sloads/modules/` docstrings (`tail_span.py`, `balance.py`),
  which are left stale rather than edited without an OR-15 admission.
  `00_backlog.md`'s "Where things stand (2026-08-29)" narrative and the five
  superseded stacked re-cut preambles rolled to
  `40_history/44_backlog_state_narrative_to_2026-08-29.md` per the file's own
  2026-08-16 precedent; the live table apparatus (system of record, ordering
  rules, removal rule, review additions, the priority table) stays. Note 03's
  dead "Phase G" backlog pointer re-aimed at the #29/0.9.0 band; note 01
  carries a phase-complete banner. The six #29-pre-assigned parked rows
  (M4-11b, L-8b/c/d/e/f) moved into the backlog's 0.9.0 band with bodies and
  filed as #247–#252 by the bridge, so `02_parked.md` again means off-mission
  only. Rule-6 numbers stated on the
  parks that lacked them: M4-19 and M4-21 park at **0** (the term is off by
  default / evaluates to zero on every emitted balanced trim point), and M4-4
  gets its measured pair — the Ch 9 `Iyy` approximation is +32 % over the
  per-CG precise value on `ga6_normal` and +123 % on `baron_58`, conservative
  in sign and oracle-locked, which is the pair that parks it. The step-14
  indeterminate-path mention gained the stub body it never had. The milestone
  half of the issue (thirteen unmilestoned defects, #171) was closed by the
  owner in the 2026-09-08 review session; the remaining milestone assignments
  and the `_staging_tmp2/` deletion are the owner's `gh`/local actions.
