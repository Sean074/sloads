- **A User guide link in the GUI sidebar opens the published book (#429, tier S, 2026-11-16).**
  It sits beside About on every page. The book and repository URLs have one
  owner, `sloads/_urls.py`, which `scripts/build_book.py` reads for the book's
  `site_url`; guards pin the sidebar, the README and the Pages address to it.
