# VESSAXOR Systems Portfolio

Public GitHub Pages portfolio for `vessaxor-spec`.

The site is intentionally static and dependency-light. Public project state is refreshed at build time from the VESSAXOR profile repository and the public GitHub release API. Approved VESSAXOR, TEO, and GroX source banners are synchronized at build time and pinned by dimensions plus SHA-256 digest so visual identity cannot silently drift.

No analytics, trackers, cookies, remote fonts, or external frontend frameworks are included.

## Improvement program

The senior-principal audit remediation is tracked in [`docs/site-improvement-tracker.md`](docs/site-improvement-tracker.md). An item is not considered closed until implementation and its required validation evidence are both present.

## Local preview

Serve the repository root with any static HTTP server, for example:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

The committed `data/projects.json` is a current fallback snapshot. Canonical full-resolution source PNGs are build-synchronized; responsive WebP derivatives and the social preview are generated deterministically from the pinned source visuals; the SVG favicon is committed.

## Build validation

```bash
python3 scripts/generate_site_data.py
python3 scripts/sync_site_visuals.py
python3 scripts/build_site_media.py
python3 scripts/validate_site.py
node --check app.js
```

Validation covers public state, source-banner identity, responsive media dimensions, duplicate IDs, internal anchors, image alt text, heading-order regressions, micro-type floor, accessible focus treatment, SEO discovery surfaces, and expected portfolio structure.

Pull-request CI also captures desktop and mobile render screenshots for human visual regression review.

## Search discovery

The site exposes a minimal crawl/indexing foundation:

- `robots.txt` permits public crawling and advertises the canonical sitemap
- `sitemap.xml` lists the canonical portfolio homepage
- `index.html` declares `index,follow`, the canonical URL, large-image preview permission, WebSite structured data, a dedicated favicon, and a dedicated 1200×630 social preview
- Google Search Console ownership is retained through the root verification file

## Public-state and media pipeline

- curated focus source: `vessaxor-spec/vessaxor-spec/profile/status.toml`
- release truth: GitHub Releases for TEO and GroX
- approved source visuals: VESSAXOR, TEO, and GroX repository banners pinned by SHA-256
- generated site data: `data/projects.json`
- build-synchronized source PNGs: `vessaxor-hero.png`, `teo-banner.png`, `grox-banner.png`
- responsive media: generated 720/1200/1800 WebP derivatives plus PNG fallback
- validation: `scripts/validate_site.py`
- deployment: GitHub Pages via `.github/workflows/deploy-pages.yml`
- pull requests: validation and render review only; Pages deployment remains restricted to non-PR events
