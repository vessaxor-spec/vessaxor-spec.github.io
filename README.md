# VESSAXOR Systems Portfolio

Public GitHub Pages portfolio for `vessaxor-spec`.

The site is intentionally static and dependency-light. Public project state is refreshed at build time from the VESSAXOR profile repository and the public GitHub release API. No analytics, trackers, cookies, or external JavaScript frameworks are included in the baseline.

## Local preview

Serve the repository root with any static HTTP server, for example:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Public-state pipeline

- curated focus source: `vessaxor-spec/vessaxor-spec/profile/status.toml`
- release truth: GitHub Releases for TEO and GroX
- generated site data: `data/projects.json`
- deployment: GitHub Pages via `.github/workflows/deploy-pages.yml`
