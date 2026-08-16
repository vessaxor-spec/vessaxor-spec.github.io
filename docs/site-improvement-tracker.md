# VESSAXOR Site Improvement Tracker

This is the canonical remediation ledger for the senior-principal portfolio audit approved on 16 Aug 2026.

Completion standard: an item is complete only when the implementation exists on the remediation branch and the final Pages build plus rendered desktop/mobile verification pass. Items that require post-deploy measurement stay open until production evidence exists.

## Phase 1 — Accessibility and interaction quality

- [x] A01 Raise low-contrast microcopy token above WCAG AA normal-text contrast floor.
- [x] A02 Raise micro-type floor from ~9–10 px to ~11.5 px or larger.
- [x] A03 Increase header navigation and mobile menu hit areas to at least 44 px.
- [x] A04 Add explicit high-contrast `:focus-visible` treatment.
- [x] A05 Improve mobile navigation: Menu/Close state, Escape handling, focus return.

## Phase 2 — Information hierarchy and UX

- [x] U01 Compress the identity hero so flagship work appears earlier.
- [x] U02 Surface TEO/GroX release and state evidence directly in the hero.
- [x] U03 Reduce total vertical length by consolidating redundant sections.
- [x] U04 Merge Public State and Current Work into one operational section.
- [x] U05 Replace jargon-first current-work presentation with human-readable headlines plus exact technical detail.
- [x] U06 Replace the six-card principles grid with a denser editorial manifesto list.

## Phase 3 — Visual-system refinement

- [x] V01 Replace generic Arial-first stack with a modern native system stack; no remote font dependency.
- [x] V02 Reduce repeated eyebrow + huge-heading + boxed-card composition across lower sections.
- [x] V03 Strengthen TEO/GroX differentiation without adding decorative clutter.
- [x] V04 Preserve full 3:1 project/banner identity on mobile instead of forced crop.
- [x] V05 Add active navigation state without increasing motion intensity.

## Phase 4 — Performance and media delivery

- [x] P01 Commit responsive WebP derivatives for VESSAXOR, TEO, and GroX while retaining canonical PNG fallbacks.
- [x] P02 Add `srcset`/`sizes` responsive image delivery.
- [x] P03 Mark hero as high-priority LCP media with `fetchpriority="high"`.
- [x] P04 Disable mobile header backdrop-filter cost.
- [ ] P05 Measure production Lighthouse/Core Web Vitals after deployment and record evidence here.

## Phase 5 — Discoverability, supply chain, and regression control

- [x] S01 Add a deliberate VESSAXOR favicon.
- [x] S02 Improve search title from brand-only to descriptive persistent-AI/orchestration positioning.
- [x] S03 Add a dedicated 1200×630 social preview instead of using the 3:1 README hero.
- [x] S04 Pin GitHub Actions to immutable full commit SHAs and scope permissions per job.
- [x] S05 Pin approved hero/TEO/GroX source assets by SHA-256 digest.
- [x] S06 Expand CI validation for duplicate IDs, broken internal anchors, image alt text, heading order, responsive assets, micro-type floor, focus styles, SEO surfaces, and visual dimensions.
- [x] S07 Produce desktop/mobile render screenshots as CI artifacts for human regression review.

## Final gate

- [ ] G01 PR build succeeds on the exact final head.
- [ ] G02 Desktop 1440×1000 render reviewed with no overflow, clipping, broken content, or hierarchy regression.
- [ ] G03 Mobile 390×844 render reviewed with no overflow, clipping, broken content, or interaction regression.
- [ ] G04 Production Pages deployment succeeds.
- [ ] G05 Production Lighthouse/performance measurement recorded; any material failures remediated before closing this program.

## Evidence

- PR run #16 correctly failed when the proposed `ffmpeg` runtime dependency was absent on the GitHub Ubuntu 24.04 runner. The dependency was not bypassed or installed ad hoc. The design was changed instead: responsive derivatives are committed governed assets, removing the runtime converter from the Pages execution path.
- The build-time source visual sync remains fail-closed on exact dimensions and approved SHA-256 digests for VESSAXOR, TEO, and GroX source banners.
- Final CI, render-review, production deployment, and performance evidence will be recorded as their gates close.
