- **A stale AGREED header on a shipped design note now fails CI (issue #183,
  tier S, 2026-09-08).** Three of the last four tier-L closures left their
  note's Status at plain AGREED (46/47/48, review R-13), and the #128 guard
  never fired because it matches only explicit "unbuilt" phrasing — while
  `RELEASE_PROCESS.md` §4 step 3 rolls notes to `docs/40_history/` **by status
  header**, so an unflipped note is skipped by the roll and a wrong status
  enters the permanent record. The flip half shipped with #190 (which found
  note 50 equally stale); this change adds the guard and, sweeping with it,
  found and flipped a fifth the issue did not know about: **note 53**, whose
  work shipped 2026-09-07 as step 163 in step 162's commit `175369e`. The
  guard (`test_doc_currency.py`) uses the same in-repo proxy as #128, narrowed
  to where it is unambiguous: a `changes/*.history.md` fragment whose own
  `## Step` heading names "(design) note N" is that note's closure record, and
  note N's Status paragraph must then carry SHIPPED/BUILT/✅. A prose mention
  in a fragment body ("until note 51 lands") deliberately does not count —
  note 51 is exactly that case today and stays AGREED. Proven both ways:
  reverting note 53's header fails the guard on that note alone.
