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
- [ ] D403 Add reciprocal public-overview links from TEO and GroX README entry surfaces after public-state integrity closes.
- [ ] D404 Improve repository/profile About metadata where a governed write path is available; connector currently exposes no repository/profile metadata mutation, so this remains explicitly unclaimed.
- [ ] D405 Recheck search discovery after reciprocal links and metadata changes have had time to be indexed; do not convert indexing delay into a false failure or success claim.

## Current state

**PROGRAM 3 CLOSED / PROGRAM 4 ACTIVE — public-state integrity is production-qualified. The next executable step is D403: add reciprocal public-overview links from TEO and GroX README entry surfaces. Repository/profile About metadata remains an explicit tool-capability gap, and search re-evaluation remains time-dependent.**
