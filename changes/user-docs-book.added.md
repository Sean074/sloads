- **The user documentation builds as a searchable book for GitHub Pages (#427, tier S, 2026-11-10).**
  `scripts/build_book.py` stages the guides, theory, input-file reference and a new
  validation rationale page and rewrites out-of-book links; `docs.yml` builds it
  with Zensical and deploys from `main`. Guard: `tests/test_book.py`.
