# `changes/` — changelog fragments

One small file per closed item, instead of an edit to `CHANGELOG.md`. This is the
**only** way `[Unreleased]` content is written (design note 26, 2026-08-16); the
release cut assembles the fragments (`RELEASE_PROCESS.md` §4).

## Writing a fragment

File name: `<slug>.<type>.md`

- `slug` — short kebab-case identity of the change (`gear-csv-ult-marker`,
  `backlog-generated-view`). Lower-case letters, digits, hyphens.
- `type` — one of `breaking`, `added`, `changed`, `fixed`, `removed`: selects the
  `### Breaking` / `### Added` / … subsection at build time.

**One fragment per closure, every tier, one bullet of at most 60 words** (#359,
2026-11-01). The change stated in a sentence, with the issue number, tier and
date in the lead's parenthetical; the issue body and the design note hold the
rest, and `git log` holds the commit. `solo_close.sh` refuses a longer one.

```markdown
- **Gear report CSV meets the load-output contract (#R6-C2, tier M, 2026-08-16).**
  `-ULT` markers on every load column and an `SF` column per case.
```

History fragments (`<slug>.history.md`, design note 28 MD-4) retired on
2026-11-01: `docs/90_record/00_completed_development.md` is frozen, and a
`.history*.md` is refused by the guard and by `solo_close.sh`.

## Building the changelog (release cut only — `RELEASE_PROCESS.md` §4)

```bash
.venv/bin/python scripts/build_changelog.py --dry-run          # preview the section
.venv/bin/python scripts/build_changelog.py 0.6.0 --date 2026-08-20
```

The builder merges every fragment into the existing `[Unreleased]` body by
subsection (fragments first, then any legacy hand-written text), renames the
heading to `## [0.6.0] — 2026-08-20`, opens a fresh empty `[Unreleased]` and
deletes the consumed fragments. Until the cut, `ls changes/` *is* the release's
history.

## Guard

`tests/test_changelog_fragments.py` fails on a mis-named fragment, a body that is
not a bullet, or a history fragment. `README.md` is the only non-fragment file
allowed here.
