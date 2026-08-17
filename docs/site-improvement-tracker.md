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

- [x] P01 Generate responsive WebP derivatives for VESSAXOR, TEO, and GroX from approved source PNGs while retaining those PNG fallbacks.
- [x] P02 Add `srcset`/`sizes` responsive image delivery.
- [x] P03 Mark hero as high-priority LCP media with `fetchpriority="high"`.
- [x] P04 Disable mobile header backdrop-filter cost.
- [x] P05 Measure the deployed production site with Google Lighthouse and record mobile/desktop evidence. Real-user CrUX field data is not inferred or claimed from lab results.

## Phase 5 — Discoverability, supply chain, and regression control

- [x] S01 Add a deliberate VESSAXOR favicon.
- [x] S02 Improve search title from brand-only to descriptive persistent-AI/orchestration positioning.
- [x] S03 Add a dedicated 1200×630 social preview instead of using the 3:1 README hero.
- [x] S04 Pin GitHub Actions to immutable full commit SHAs and scope permissions per job.
- [x] S05 Pin approved hero/TEO/GroX source assets by SHA-256 digest.
- [x] S06 Expand CI validation for duplicate IDs, broken internal anchors, image alt text, heading order, responsive assets, micro-type floor, focus styles, SEO surfaces, and visual dimensions.
- [x] S07 Produce full-page desktop/mobile render screenshots as CI artifacts for human regression review.

## Final gate

- [x] G01 PR build succeeds on the exact reviewed head.
- [x] G02 Desktop full-page render reviewed with no overflow, clipping, broken content, or hierarchy regression.
- [x] G03 Mobile full-page render reviewed with no overflow, clipping, broken content, or interaction regression.
- [x] G04 Production Pages deployment succeeds.
- [x] G05 Production Lighthouse/performance measurement recorded with no material lab-performance, accessibility, best-practices, or SEO failure requiring further remediation.

## Evidence

- PR run #16 correctly failed when the proposed `ffmpeg` runtime dependency was absent on the GitHub Ubuntu 24.04 runner. The dependency was not bypassed or installed ad hoc.
- The media path was redesigned and locally proven with `scripts/build_site_media.mjs`: Node built-ins drive headless Chrome through the Chrome DevTools Protocol, embedding the approved PNG source directly into the capture document. No npm, Python imaging library, system package installation, localhost content navigation, or external media service is required in the production build path.
- A subsequent runner exposed only a temporary Chrome-profile deletion race after all media had already generated. Lifecycle handling was corrected with browser shutdown, bounded cleanup retries, and non-critical ephemeral-profile cleanup handling rather than weakening any site validation.
- PR run #30 passed source-state refresh, digest-pinned banner sync, responsive-media generation, expanded static validation, JavaScript syntax checks, full-page render capture, and render-artifact upload.
- CI full-page desktop evidence: 1440×6137; all VESSAXOR/TEO/GroX visuals loaded, no horizontal overflow, clipping, missing sections, or hierarchy regression observed.
- CI full-page mobile evidence: 390×7049; all VESSAXOR/TEO/GroX visuals loaded, no horizontal overflow, broken stacking, missing sections, or interaction-layout regression observed.
- Production workflow run #32 (`31970482935`) completed successfully after PR #5: validation, responsive-media generation, Pages artifact construction, render review, and GitHub Pages deployment all passed.
- An initial official PageSpeed Insights API attempt in evidence run #33 was rejected with HTTP 429 because Google's shared unkeyed API project had exhausted its daily query quota. This was recorded as an external quota failure, not treated as site evidence and not bypassed with fabricated results.
- Google Lighthouse `13.4.1` was then run directly against the live production URL in evidence run #35 (`31970834269`), pinned to the official release for the one-time measurement.
- Lighthouse mobile: Performance **100**, Accessibility **100**, Best Practices **100**, SEO **100**; FCP **0.823 s**, LCP **1.071 s**, Speed Index **0.823 s**, TBT **0 ms**, CLS **0.000**.
- Lighthouse desktop: Performance **100**, Accessibility **100**, Best Practices **100**, SEO **100**; FCP **0.220 s**, LCP **0.284 s**, Speed Index **0.220 s**, TBT **0 ms**, CLS **0.000**.
- Lighthouse is controlled lab evidence. CrUX real-user field metrics, including field INP, are not supplied by this evidence path and are therefore not claimed. Absence of a real-user claim is not converted into synthetic field data.
- The build-time source visual sync remains fail-closed on exact dimensions and approved SHA-256 digests for VESSAXOR, TEO, and GroX source banners.

## Senior-principal remediation program state

**CLOSED — all approved senior-principal audit remediation items and final evidence gates are complete as of 16 Aug 2026.**

---

## Program 2 — Public Surface Evolution

Approved 17 Aug 2026 after review of the VESSAXOR swarm audit and follow-up practical improvement plan.

Goal: turn the portfolio from a description of rigorous systems into a visible demonstration of rigorous systems without reopening already-proven accessibility, performance, mobile, or deployment architecture work without new evidence.

Completion standard: implementation items may be marked complete when source changes and local validation exist. Deployment gates remain open until the exact branch head passes GitHub Actions, rendered review, Pages deployment, and production smoke verification.

### P0 — Hero reliability and production resilience

- [x] R01 Add a fail-visible, asset-independent hero fallback so media failure cannot become a black void.
- [x] R02 Add bounded client-side media recovery: responsive source failure retries the approved PNG fallback, then exposes the static fallback if recovery also fails.
- [x] R03 Add an explicit hero preload for the primary desktop WebP candidate without introducing a new runtime dependency.
- [x] R04 Extend render validation to exercise the media error path and assert the fallback remains visible.
- [x] R05 Add a post-deploy production smoke verifier for the homepage, new public pages, hero derivatives, PNG fallback, and flagship banners.
- [ ] R06 Reproduce the reported intermittent hero failure in a non-Chromium browser engine. Current CI has Chromium only; no new third-party browser runtime is introduced without evidence that the remaining repro gap justifies the supply-chain and maintenance cost.

### P1 — Outsider comprehension

- [x] O01 Add a short orientation layer: what VESSAXOR is, what it is not, and why the architecture matters.
- [x] O02 Lead TEO and GroX descriptions with plain-language meaning before exact native system terminology.
- [x] O03 Preserve current release/state evidence in the hero and system surfaces.
- [x] O04 Move dense principles behind native progressive disclosure rather than forcing them into the primary scan path.

### P2 — Architecture and real evidence

- [x] E01 Add visible TEO routing flow from task/effective risk through responsibility, capability, implementation, verifier, and evidence-bearing outcome.
- [x] E02 Add visible GroX Mission flow from Commander intent through Pilot GorXu, Mission, Standing Crew, Mission Order, evidence, and verification.
- [x] E03 Add concrete public examples from the real TEO `plan`/`finalize` lifecycle and GroX bounded Mission/reconstitution surfaces.
- [x] E04 Pair examples with explicit evidence boundaries so reference capability, staged scope, experiments, and qualified operating state are not overclaimed.

### P3 — Dedicated system pages and progressive depth

- [x] M01 Add `/teo/` as an indexable technical overview with plain-language definition, native architecture, executable evidence, current state, and primary sources.
- [x] M02 Add `/grox/` as an indexable technical overview with command spine, Mission flow, bounded evidence, current state, and primary sources.
- [x] M03 Add `/evidence/` as a public evidence surface rather than forcing visitors directly from homepage copy into repository internals.
- [x] M04 Keep the homepage as the portfolio-level orientation and route deeper detail to dedicated surfaces.

### P4 — Claim-to-evidence public design pattern

- [x] C01 Establish `Claim → Evidence → Boundary → Primary source` as a reusable public interface pattern.
- [x] C02 Apply the pattern to both flagship systems and to the VESSAXOR site itself.
- [x] C03 Keep primary repositories and canonical stewardship records authoritative; the portfolio does not become a parallel source of truth.

### P5 — Discoverability and indexable surface

- [x] D01 Expand the sitemap from one URL to the homepage plus TEO, GroX, and Evidence pages.
- [x] D02 Give each new page a distinct title, description, canonical URL, Open Graph/Twitter metadata, and JSON-LD WebPage context.
- [x] D03 Add strong internal linking among the homepage, system pages, evidence surface, and primary repositories.
- [x] D04 Extend static validation to all public pages and their canonical/search surfaces.

### Program 2 deployment gates

- [x] G201 Exact branch-head GitHub Actions validation passes.
- [x] G202 Full homepage desktop/mobile render review passes with no overflow, missing media, or hierarchy regression.
- [x] G203 Dedicated TEO/GroX/Evidence layouts pass desktop and mobile overflow/media checks.
- [x] G204 GitHub Pages production deployment succeeds after merge.
- [x] G205 Post-deploy production smoke confirms all public pages and critical hero/banner assets resolve from the live Pages surface.

### Program 2 production evidence

- Final PR #7 review head `d51356c18852ac1e4e4cfe6248c7528f11b1be0f` passed GitHub Actions run #47 (`32006231647`): source refresh, visual synchronization, responsive-media generation, four-page static validation, homepage desktop/mobile render review, dedicated TEO/GroX/Evidence desktop/mobile layout checks, forced hero-fallback verification, and render-artifact upload.
- Human review rejected an earlier overlong homepage even though CI was green. The accepted render reduced the homepage from 7490 to 6966 px on desktop and from 10530 to 8643 px on mobile while moving full architecture depth to the dedicated system pages.
- PR #7 was squash-merged to `main` as `e6581ae398d8b6d706d4b1b1d24fb2dd4dc34aa6`.
- Production workflow run #48 (`32006382178`) passed validation, Pages artifact construction, render/reliability review, GitHub Pages deployment, and the new `verify-production` live smoke job.
- The live smoke gate verified the deployed homepage, `/teo/`, `/grox/`, `/evidence/`, the hero 720/1200/1800 WebP derivatives, the approved hero PNG fallback, and the TEO/GroX flagship banner assets with bounded retries.
- The external web-fetch tool could not independently fetch the GitHub Pages URL in this session; that tool-layer cache/safety failure is not treated as contrary production evidence. The governed GitHub Actions smoke test is the recorded production reachability evidence.

### Program 2 current state

**DEPLOYED / PRODUCTION GATES PASS — P1 through P5 are implemented and production-verified. P0 fail-visible hardening and live production reachability checks are operational. R06 remains open because the originally reported intermittent hero failure has not yet been reproduced in a non-Chromium engine; this is retained as an explicit evidence gap rather than converted into a false root-cause claim.**
