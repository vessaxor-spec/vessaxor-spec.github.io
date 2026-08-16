# VESSAXOR Systems Portfolio

Public GitHub Pages portfolio for `vessaxor-spec`.

The site is intentionally static and dependency-light. Public project state is refreshed at build time from the VESSAXOR profile repository and the public GitHub release API. Approved VESSAXOR, TEO, and GroX banner assets are also synchronized at build time into the Pages artifact, keeping the deployed site self-contained while avoiding stale or degraded local copies.

No analytics, trackers, cookies, or external JavaScript frameworks are included.

## Local preview

Serve the repository root with any static HTTP server, for example:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

The committed `data/projects.json` is a current fallback snapshot. The three full-resolution portfolio visuals are build-generated and are therefore guaranteed only after running the sync step below.

## Build validation

```bash
python3 scripts/generate_site_data.py
python3 scripts/sync_site_visuals.py
python3 scripts/validate_site.py
```

The visual sync fails closed if any approved banner is no longer a 2172×724 PNG or becomes unexpectedly small, preventing a low-resolution replacement from silently reaching production.

## Search discovery

The site exposes a minimal crawl/indexing foundation:

- `robots.txt` permits public crawling and advertises the canonical sitemap
- `sitemap.xml` lists the canonical portfolio homepage
- `index.html` declares `index,follow`, the canonical URL, large-image preview permission, and WebSite structured data
- `scripts/validate_site.py` fails the Pages build if these discovery surfaces disappear or drift from the canonical site URL

Google Search Console ownership and indexing requests are intentionally external to this repository. A future Search Console verification token can be added without changing the public portfolio architecture.

## Public-state pipeline

- curated focus source: `vessaxor-spec/vessaxor-spec/profile/status.toml`
- release truth: GitHub Releases for TEO and GroX
- approved visual sources: the current VESSAXOR, TEO, and GroX repository banners
- generated site data: `data/projects.json`
- generated deployment visuals: `assets/visuals/vessaxor-hero.png`, `teo-banner.png`, and `grox-banner.png`
- validation: `scripts/validate_site.py`
- deployment: GitHub Pages via `.github/workflows/deploy-pages.yml`
- pull requests: build and validation only; deployment remains restricted to non-PR events
