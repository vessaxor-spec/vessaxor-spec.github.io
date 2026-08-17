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
- [ ] P311 Exact-head GitHub Actions validates generation, state synchronization, Chromium render/reliability checks, and Firefox matrix.
- [ ] P312 Human review confirms the state-only change causes no layout or hierarchy regression.
- [ ] P313 Production Pages deployment succeeds after merge.
- [ ] P314 Production live HTTP and Firefox gates pass on the deployed state-integrity change.

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

**IN PROGRESS — canonical profile state is reconciled and merged. Portfolio build-time static-state synchronization and drift validation are implemented on `agent/public-state-integrity`; exact-head CI and production gates remain open. External discoverability work begins only after this integrity gate closes.**
