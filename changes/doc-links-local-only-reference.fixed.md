- **The doc-link guard stops failing CI on links into the local-only
  `reference/` tree (tier S, 2026-09-14).** Note 61's CV-6 guard
  (`tests/test_doc_links.py`) went red on its own closure commit: three links
  into `reference/` resolved locally and not on the runner, because that
  directory is gitignored whole — the manuals and circulars are copyright
  material kept on the developer's machine, as CLAUDE.md says. A link into a
  local-only tree is now accepted rather than checked; every other relative
  link is held to existing exactly as before.
