# VESSAXOR Public State Integrity & Discoverability Tracker

Approved continuation: 17 Aug 2026.

This ledger tracks the post–Public Surface Evolution maintenance work needed to keep public-facing state synchronized with canonical repository truth and to improve discovery signals without creating a parallel source of truth.

## Program 3 — Public State Integrity

### S3.1 — Recalibration

- [x] P301 Recalibrate against current portfolio repository truth before further changes.
- [x] P302 Confirm Program 2, including bounded Firefox R06 investigation, is already closed with continuous Chromium/Firefox regression coverage.
- [x] P303 Detect GroX public-state drift: canonical GroX is `v0.8.0`, while committed portfolio/profile fallbacks still contained `v0.7.1` / A6-era wording.

### S3.2 — Profile source reconciliation

- [x] P304 Refresh canonical curated profile state to 17 Aug 2026 and current GroX post-evolution wording.
- [x] P305 Preserve TEO's current evidence-governed documentation replay focus.
- [x] P306 Regenerate the profile README through the existing workflow rather than hand-editing generated blocks; branch run #10 (`32040390234`) passed and produced GroX `v0.8.0`.
- [x] P307 Merge profile PR #4 so the portfolio generator consumes the reconciled canonical profile source.

### S3.3 — Deployment-artifact state synchronization

- [x] P308 Extend `generate_site_data.py` so the generated public-state payload also synchronizes state-bound text in the deployable HTML surfaces.
- [x] P309 Reconcile the committed `data/projects.json` fallback to GroX `v0.8.0` and the 17 Aug 2026 curated state.
- [x] P310 Add fail-closed validation requiring deployed static HTML state to match generated JSON state for homepage, TEO, GroX, and Evidence surfaces.
- [x] P311 Exact-head GitHub Actions validates generation, state synchronization, Chromium render/reliability checks, and Firefox matrix.
- [x] P312 Human review confirms the state-only change causes no layout or hierarchy regression.
- [x] P313 Production Pages deployment succeeds after merge.
- [x] P314 Production live HTTP and Firefox gates pass on the deployed state-integrity change.

### Program 3 evidence

- Profile PR #4 reconciled the curated public source to 17 Aug 2026 / GroX `v0.8.0`; branch run #10 (`32040390234`) and post-merge main run #11 (`32040715013`) passed.
- Site PR #11 exact head `85a7a28b13e0041482c8cf06eff5aa37680944e9` passed run #58 (`32040850841`): canonical state generation, deployable HTML synchronization, pinned visual synchronization, HTML/JSON state equality, Chromium render/reliability, eight Firefox cold-load sessions, and render-artifact publication.
- Human review of the PR #11 render artifact found no layout, hierarchy, responsive, or media regression; visible changes were limited to reconciled public-state text.
- Production run #59 (`32041046639`) failed safely before artifact construction on a raw-host HTTP 503 while reading canonical profile state. PR #12 added bounded authenticated state-fetch resilience without allowing stale fallback.
- Production run #61 (`32041284100`) then proved state retrieval but failed safely before deployment when one parallel Pages-build runner exhausted four raw-host visual retries with HTTP 429 while the validation runner passed the same visual gate.
- PR #13 moved canonical profile and approved visual inputs from `raw.githubusercontent.com` to authenticated GitHub Contents API reads while retaining freshness, repository allowlisting, release lookup, exact SHA-256, exact dimensions, atomic replacement, and fail-closed validation.
- PR #13 exact head `c809785da78f767f9e96c29f1e019ff53fc3e557` passed run #62 (`32041499889`) across state/API reads, all three pinned visual reads, state equality, Chromium, eight Firefox cold loads, and artifact publication.
- Production run #63 (`32041589000`) passed both `build-pages` and `validate`, deployed GitHub Pages successfully, passed live page/media HTTP smoke, and passed four deployed Firefox cold-load sessions against the actual production site.

### Program 3 state

**CLOSED / CONTINUOUS STATE-INTEGRITY COVERAGE — canonical profile state, generated JSON, deployable static HTML, approved visual identity, Chromium rendering, Firefox cold loads, production HTTP reachability, and cross-repository source retrieval are governed by fail-closed checks. Raw-CDN build inputs have been removed from the critical source path.**

## Program 4 — External Discoverability

### D4.1 — Current signal audit

- [x] D401 Recheck external search footprint; VESSAXOR remains weakly surfaced despite strong technical SEO.
- [x] D402 Audit GitHub discovery metadata.
  - Site repository: no description, homepage, or topics.
  - Profile repository: no description, homepage, or topics.
  - TEO: strong description/topics, empty homepage field.
  - GroX: strong description/topics, empty homepage field.
  - GitHub user profile: strong bio, empty website/blog field.
- [x] D403 Add reciprocal public-overview links from TEO and GroX README entry surfaces after public-state integrity closes.
- [ ] D404 Improve repository/profile About metadata where a governed write path is available. The connected GitHub capability was re-audited on 19 Aug 2026 and still exposes no mutation action for repository description, homepage, topics, or user-profile website; this remains a verified capability gap rather than an unattempted item.
- [x] D405 Recheck search discovery after the reciprocal links had an initial indexing interval. On 19 Aug 2026, exact searches for the VESSAXOR site, `VESSAXOR` + `Living Systems Lab`, TEO + VESSAXOR, and GroX + its exact public tagline still returned unrelated results rather than VESSAXOR surfaces. This is negative evidence of current discoverability, not proof that a particular search engine has never indexed the site.
- [x] D406 Add a crawlable `/notes/` technical-notes surface using plain-language search terms for persistent AI systems, governed AI orchestration, bounded AI execution, evidence-bearing execution, verification, recovery, TEO, and GroX; link it from the existing Evidence surface and sitemap without creating a new source of system truth.
- [x] D407 Require exact-head CI to validate the notes contract and desktop/mobile layout before merge.
- [ ] D408 Require production build, deployment, live HTTP reachability, and existing deployed Firefox verification after merge. Production verification now additionally publishes exact-SHA commit status `vessaxor/pages-production`; D408 remains open until that status is observed green on `main`.
- [ ] D409 Recheck external discovery after the technical-notes surface has had a meaningful indexing interval; keep this separate from D405 so a negative first recheck is not overwritten by later evidence.

### Program 4 evidence

- TEO PR #177 added exactly one `Public overview` link to `https://vessaxor-spec.github.io/teo/`; Reference Implementation CI run #772 (`32041919992`) passed repository layout, compilation, automated tests, regulated specialist evidence, JSON schemas, linked configuration, and the end-to-end example before merge as `4b4f07fc448b48c9b551e5ae759dd02cf1bb8d24`.
- GroX PR #59 added exactly one `Public overview` link to `https://vessaxor-spec.github.io/grox/`; GroX CI run #160 (`32041926390`) passed Python 3.11–3.14 regression coverage, wheel-bootstrap portability, and the full Python 3.12 post-Apex experiment/mutation/integrated-qualification path before merge as `40e8234aecb23d5775e3c407b6ed19a054b35f84`.
- Both flagship repositories therefore now link outward to their dedicated VESSAXOR public overview, while the portfolio already links back to the canonical repositories. This establishes reciprocal crawl/discovery paths without making the portfolio authoritative over either system.
- The 19 Aug 2026 external search recheck did not surface the VESSAXOR pages for four exact/near-exact discovery queries. D405 therefore records a completed negative checkpoint rather than claiming indexing success.
- The GitHub connector was re-audited on 19 Aug 2026 for `topics` and `homepage` mutation capabilities; no writable repository About/topics/homepage or user-profile website action is exposed, so D404 remains capability-blocked.
- PR #18 exact head `434db03997df6c7e0626e6c49601b90bbf14959a` passed run #77 (`32255044149`): public-state refresh, approved visual sync, responsive media generation, static validation, the dedicated technical-notes discovery contract, desktop/mobile layout checks including `/notes/`, hero reliability, eight Firefox cold-load sessions, and render-artifact publication.
- PR #18 was squash-merged to `main` as `f014baec8f7b864b6df9bcf571a235a43b23d0e7`. The connected GitHub wrapper cannot enumerate push-triggered workflow runs by commit SHA, so a durable exact-SHA production receipt is being added rather than inferring D408 from missing run-list visibility.

## Program 5 — Hero Delivery Quality

### V5.1 — Retry and diagnosis

- [x] V501 Retry the previously infrastructure-blocked Pages workflow. Run #67 (`32042281408`) ultimately passed build, validation, deployment, live HTTP smoke, and deployed Firefox after GitHub action-distribution throttling cleared.
- [x] V502 Diagnose hero softness: the homepage preloaded a 1200px WebP for every desktop and exposed responsive WebPs only through 1800px despite an approved 2172x724 lossless master.

### V5.2 — High-density delivery

- [x] V503 Raise VESSAXOR hero WebP generation quality from 90 to 96 while leaving TEO/GroX media generation unchanged at quality 90.
- [x] V504 Preload 720px WebP on mobile and 1800px WebP on standard-density desktop.
- [x] V505 Route desktop displays at 1.5dppx or higher to the approved lossless 2172x724 PNG master.
- [x] V506 Preserve the first generated-2172-WebP attempt as negative evidence: automated CI passed, but human render review found the derivative visually unusable, so it was rejected before merge.
- [x] V507 PR #16 exact head `69e666c8c1be65a34fad483644ae753b80bad2eb` passed run #71 (`32070032591`) across media generation, static validation, Chromium render/reliability, eight Firefox cold loads, and artifact publication.
- [x] V508 Human review of run #71 confirmed the hero is visible and sharper than the prior accepted desktop render; the corrected strategy uses the lossless master rather than a generated 2172px derivative.
- [x] V509 Production merge `c8947c9babebaee698ab57a91d8c2192abdc452c` passed run #72 (`32070333281`) across Pages build, full validation, deployment, live HTTP smoke, and deployed Firefox cold loads.

### Program 5 state

**CLOSED / CONTINUOUS HERO-DELIVERY COVERAGE — mobile retains an efficient 720px path, standard-density desktop receives higher-quality WebP media, high-density desktop receives the approved lossless master, and Chromium/Firefox plus human render review remain evidence gates for hero changes.**

## Current state

**PROGRAM 3 CLOSED / PROGRAM 4 ACTIVE / PROGRAM 5 CLOSED — public-state integrity and hero delivery quality are production-qualified. D403 and D405–D407 are complete; D404 remains connector-capability blocked; D408 is the current exact-SHA production gate; D409 is the next time-dependent external indexing recheck.**
