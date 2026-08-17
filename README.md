# VESSAXOR Systems Portfolio

Public GitHub Pages portfolio for `vessaxor-spec`.

The site is intentionally static and dependency-light. Public project state is refreshed at build time from the VESSAXOR profile repository and the public GitHub release API. Approved VESSAXOR, TEO, and GroX source banners are synchronized at build time and pinned by dimensions plus SHA-256 digest so visual identity cannot silently drift.

No analytics, trackers, cookies, remote fonts, external frontend frameworks, or package-manager-installed media tooling are included.

## Improvement program

The canonical implementation and evidence ledger is [`docs/site-improvement-tracker.md`](docs/site-improvement-tracker.md). It contains the closed senior-principal remediation program and the 17 Aug 2026 Public Surface Evolution program covering hero reliability, outsider comprehension, architecture/evidence visualization, dedicated system pages, claim-to-evidence design, and discoverability.

## Public surfaces

- `/` — VESSAXOR portfolio orientation, flagship systems, architecture, and current state
- `/teo/` — TEO technical overview, routing architecture, runnable evidence, boundaries, and primary sources
- `/grox/` — GroX technical overview, command/Mission architecture, persistence/recovery evidence, boundaries, and primary sources
- `/evidence/` — selected `Claim → Evidence → Boundary → Primary source` records across the public systems

The repositories remain authoritative. These pages are explanatory and evidentiary public surfaces, not replacement sources of truth.

## Local preview

Serve the repository root with any static HTTP server, for example:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

The committed `data/projects.json` is a current fallback snapshot. Canonical full-resolution source PNGs are build-synchronized from digest-pinned public sources. Responsive WebP derivatives and the dedicated 1200×630 social preview are generated deterministically from those sources with the headless Chrome runtime already used for render validation. The SVG favicon is committed.

## Build validation

```bash
python3 scripts/generate_site_data.py
python3 scripts/sync_site_visuals.py
node scripts/build_site_media.mjs
python3 scripts/validate_site.py
node --check app.js
```

`scripts/build_site_media.mjs` uses only Node built-ins plus the existing Chrome/Chromium runtime through the Chrome DevTools Protocol. It does not install npm packages, Python imaging libraries, or system packages.

Validation covers all public pages, public state, source-banner identity, responsive media dimensions, duplicate IDs, internal anchors, image alt text, heading order, micro-type floor, accessible focus treatment, canonical/search surfaces, reliability fallback markup, and expected portfolio structure.

Pull-request CI captures homepage desktop/mobile render screenshots, checks dedicated TEO/GroX/Evidence layouts at desktop and mobile widths, and exercises the fail-visible hero fallback path.

## Reliability model

The hero and flagship banners use responsive WebP delivery with approved PNG fallbacks. The hero additionally has an asset-independent HTML/CSS fallback so a media failure cannot reduce the primary visual surface to an empty black field. Client-side recovery removes failed responsive candidates, retries the approved PNG, then exposes the static fallback if media still cannot render.

After Pages deployment, `scripts/verify_production_site.py` probes the live homepage, TEO/GroX/Evidence pages, hero derivatives, PNG fallback, and flagship banners with bounded retries. Build success therefore does not stand in for production asset reachability.

## Search discovery

The site exposes a crawl/indexing foundation:

- `robots.txt` permits public crawling and advertises the canonical sitemap
- `sitemap.xml` lists the homepage plus dedicated TEO, GroX, and Evidence surfaces
- every public page declares index/follow, a distinct canonical URL, descriptive title/description metadata, Open Graph/Twitter metadata, and JSON-LD context
- Google Search Console ownership is retained through the root verification file
- internal links connect the public overview, system explanations, evidence surface, and canonical GitHub repositories

## Public-state and media pipeline

- curated focus source: `vessaxor-spec/vessaxor-spec/profile/status.toml`
- release truth: GitHub Releases for TEO and GroX
- approved source visuals: VESSAXOR, TEO, and GroX repository banners pinned by SHA-256
- generated site data: `data/projects.json`
- build-synchronized source PNGs: `vessaxor-hero.png`, `teo-banner.png`, `grox-banner.png`
- generated responsive media: 720/1200/1800 WebP derivatives plus PNG fallback
- generated social media: 1200×630 VESSAXOR Open Graph preview
- validation: `scripts/validate_site.py`
- render/reliability review: `scripts/capture_site_render.mjs`
- production smoke: `scripts/verify_production_site.py`
- deployment: GitHub Pages via `.github/workflows/deploy-pages.yml`
- pull requests: validation and render review only; Pages deployment remains restricted to non-PR events
