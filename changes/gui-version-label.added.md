- **The GUI names the program and its release (#430, tier S, 2026-11-16).**
  `sloads vX.Y.Z` heads the sidebar on every page and the browser tab, both
  from `sloads.__version__` through `app_shell.components.PROGRAM_LABEL`;
  guards fail if either drifts or a GUI string types the version.
