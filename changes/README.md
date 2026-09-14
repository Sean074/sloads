# `changes/` — changelog fragments

One small file per closed item, instead of an edit to the 5,000-line
`CHANGELOG.md`. This is the **only** way `[Unreleased]` content is written
(design note `docs/30_future/26_doc_volume_reduction_note.md`, 2026-08-16).

## Writing a fragment

File name: `<slug>.<type>.md`

- `slug` — short kebab-case identity of the change (`gear-csv-ult-marker`,
  `step-14-pbar-passthrough`, `r6-d5-tree-guard`). Lower-case letters, digits,
  hyphens.
- `type` — one of `breaking`, `added`, `changed`, `fixed`, `removed` (a
  changelog bullet; selects the `### Breaking` / `### Added` / … subsection at
  build time) **or `history`** / `history-<type>` (design note 28 MD-4: the
  tier-M paragraph or tier-L full-step entry for
  `docs/90_record/00_completed_development.md`, rolled to the top of that file
  at release cut, newest first).

**One telling per closure (design note 61 CV-2).** A tier-M/L closure writes
**one** fragment — the history entry — and the builder *derives* its
`CHANGELOG.md` bullet from the bold lead phrase the entry already opens with.
Tier S writes one typed fragment as before. The pair used to be two hand-written
narratives of the same change, ~780 words per item across both, and the second
was a re-flowed compression of the first; deriving the bullet keeps every word
that was ever written and stops writing it twice.

- `<slug>.history.md` → the derived bullet lands in `### Changed`.
- `<slug>.history-added.md` (or `-fixed`, `-removed`, `-breaking`) → names the
  subsection instead.
- Write a `<slug>.<type>.md` **as well** only when the consumer-facing bullet
  genuinely differs from the lead phrase; a hand-written bullet suppresses the
  derived one for that slug.

File body (changelog types): one or more Markdown bullets, **exactly** as they should appear in
`CHANGELOG.md` — start with `- `, bold lead phrase, tier and date in the lead,
cite the design note / backlog row / review ID as the project already does:

```markdown
- **Gear report CSV meets the load-output contract (R6-C2, tier M, 2026-08-16).**
  `-ULT` markers on every load column, an `SF` column per case, …
```

Multi-paragraph bullets are fine (indent continuation lines two spaces).

File body (`history`): a tier-M paragraph starting `- **Title (…, tier M, date)** —`
or a tier-L step starting `## Step N — …` / `**Step N — …**` in the history
file's step format (Objective / Deliverables / Test / Key decisions).

The **bold lead phrase** — or the `## Step N — …` heading — is what becomes the
changelog bullet, so write it as one: the change stated in a sentence, with the
issue number, tier and date in the parenthetical. Everything after it is the
history entry proper and stays out of the changelog. A history fragment with no
lead phrase to derive from is refused by the guard, at write time rather than at
release time.

## Building the changelog (release cut only — `RELEASE_PROCESS.md` §4)

```bash
.venv/bin/python scripts/build_changelog.py --dry-run          # preview the section
.venv/bin/python scripts/build_changelog.py 0.6.0 --date 2026-08-20
```

The builder merges every changelog fragment into the existing `[Unreleased]`
body by subsection (fragments first, then any legacy hand-written text), renames
the heading to `## [0.6.0] — 2026-08-20`, opens a fresh empty `[Unreleased]`,
inserts every `*.history.md` entry directly under the history file's header
rule (the live cycle below is byte-identical), and deletes the consumed
fragments. Nothing else in either file is touched. Until the cut, `ls changes/`
*is* the release's history.

## Guard

`tests/test_changelog_fragments.py` fails on a mis-named fragment or a body
that is not a bullet, and warns when the live history file passes its size
threshold. `README.md` is the only non-fragment file allowed here.
