"""The one place the project's public URLs are written.

Like :mod:`sloads._version`, a module of literals that imports nothing. Two
things read these and must never disagree (#429):

* ``scripts/build_book.py`` -- the book's ``site_url`` and ``repo_url``, and
  every out-of-book link it rewrites to the repository;
* the GUI's **User guide** sidebar link (``app_shell/sidebar.py``).

``BOOK_URL`` is where ``.github/workflows/docs.yml`` deploys: the GitHub Pages
address of ``REPO_URL``. The workflow names no URL (it reads ``page_url`` from
the deploy step), so the guard derives the Pages address from ``REPO_URL``
instead -- ``tests/test_book.py::test_the_book_url_is_the_repos_pages_site``.
``README.md`` carries ``BOOK_URL`` verbatim, pinned by the same file.
"""

REPO_URL = "https://github.com/Sean074/sloads"
BOOK_URL = "https://sean074.github.io/sloads/"

__all__ = ["BOOK_URL", "REPO_URL"]
