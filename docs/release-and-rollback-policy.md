# KOMAROVA_CORE release checkpoints and rollback policy

**Status:** active operating policy  
**Initial stable checkpoint:** `backup/stable-2026-11-23`  
**Checkpoint commit:** `88001c897af387d69a2477f500a097666b32f0b7`

## 1. Purpose

KOMAROVA_CORE must remain recoverable while it evolves. A new feature is not allowed to destroy the last known working version. Changes are developed and verified separately before they replace the active public branch.

## 2. Branch roles

- `main`: protected reference branch; do not modify without explicit owner approval.
- `core-backend-foundation`: active integration and GitHub Pages deployment branch.
- `feature/*`: isolated work for a defined change; validate before promotion.
- `backup/stable-YYYY-MM-DD`: immutable-by-convention checkpoint of the last verified working state. Never use it for feature development.

The initial checkpoint branch `backup/stable-2026-11-23` points to commit `88001c897af387d69a2477f500a097666b32f0b7`, the verified state before the homepage family-gallery and Mars changes. The first promoted homepage release is `abcb245d9e93a3d0e037947aaf3cd52f8f6b30c9`.

## 3. Required change sequence

1. Read the current active branch head and relevant files before editing.
2. Confirm that the last known good commit is reachable and that a backup checkpoint branch exists.
3. Create a focused `feature/*` branch from the active head.
4. Make the smallest coherent change set. Do not mix unrelated refactors.
5. Run static build, local-link checks, backend tests and any relevant functional browser checks against the exact candidate commit.
6. Open a pull request for review/CI without merging to `main`. The PR is a verification mechanism; it does not authorize changing `main`.
7. Promote only the tested commit to `core-backend-foundation` using a fast-forward update with an expected previous SHA. Do not force-push.
8. Wait for the Pages deployment workflow to succeed, then inspect the actual published URL and exercise the changed user paths.
9. Record the promoted commit, workflow run IDs, test outcomes and public verification result in the release log.

## 4. Rollback

- Never delete or rewrite the backup checkpoint.
- If a candidate fails before promotion, leave the active branch unchanged and fix the feature branch.
- If a promoted change breaks production, stop further changes and restore the last known good state by a reviewed revert commit on `core-backend-foundation`; if a revert cannot be produced safely, restore the saved checkpoint through a reviewed fast-forward/recovery procedure. Keep the failed commits in history for diagnosis.
- After rollback, verify the published site and run the same checks again.
- Do not change `main` as part of an emergency rollback unless the owner explicitly approves it.

## 5. What counts as a release

A release is considered launched only when all of the following are true:

- the candidate commit is identified;
- relevant CI checks pass on that exact commit;
- GitHub Pages deployment completes successfully;
- the live public page returns successfully and the changed paths are functionally checked;
- unsupported/private features are clearly marked as unavailable or planned;
- a rollback checkpoint remains available.

A green build alone is not a release. A design mockup is not a working feature. Documentation is not implementation.

## 6. Release log

| Date | Candidate | Scope | Verification |
|---|---|---|---|
| 2026-11-23 | `88001c897af387d69a2477f500a097666b32f0b7` | Stable pre-homepage-gallery checkpoint | Pages build, backend tests and deployment passed; account map manual search was browser-tested |
| 2026-11-23 | `abcb245d9e93a3d0e037947aaf3cd52f8f6b30c9` | Homepage portrait gallery and NASA Mars feature | Pages build 45247644371: success; backend tests 45247644556: success (43 passed); Pages deployment 45247643872: success; live homepage HTTP 200 with four portrait slots, Internet Archive and NASA Mars links verified |

## 7. Privacy and data integrity

No private family photos, names, contact details, documents, chat data, credentials or tokens may be added to the public repository as part of a release. Public portrait cards may display only an approved derivative and only after the private backend supports per-person permissions and publication approval. The static homepage currently uses neutral empty frames.
