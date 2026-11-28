# KOMAROVA_CORE — third-party components and script intake policy

**Status:** approved working policy  
**Target branch:** `core-backend-foundation`  
**Scope:** scripts, libraries, packages, models, browser userscripts, templates and other third-party components considered for KOMAROVA_CORE.

## 1. Purpose

KOMAROVA_CORE should reuse suitable free and open-source components where this is safer and more maintainable than writing everything from scratch. The project is currently intended for family and other non-commercial use. That purpose is recorded as project context, but it does not cancel copyright, license conditions, attribution duties, source-disclosure obligations, model/data terms, or security review.

This policy is an engineering intake rule, not legal advice. If a component's terms are unclear or impose obligations that cannot confidently be met, do not integrate it until the terms are reviewed or the author grants permission.

## 2. Non-commercial use and permission

1. Non-commercial intent is not, by itself, permission to copy, modify, redistribute, host, or bundle someone else's code.
2. A public repository, package registry entry, forum post, or downloadable archive is not automatically licensed for reuse.
3. A missing license means the default copyright rules apply. Do not copy or integrate the component without explicit permission or another clearly applicable legal basis.
4. A license that says **non-commercial only** may be considered only after checking its exact definition of non-commercial use and all other conditions. Do not assume that family use, donations, public hosting, or future project changes are automatically covered.
5. MIT, BSD, Apache-2.0, GPL, LGPL, MPL, AGPL and other licenses are not interchangeable. Record the exact license and version. Check attribution, notices, source availability, patent, copyleft, network-use and redistribution requirements that apply to the intended use.
6. Review licenses for model weights, datasets, fonts, images, videos and other assets separately from the source-code license.
7. Do not remove copyright notices, license texts, author attribution, or required notices.

## 3. Approved discovery sources

Sources are discovery channels, not trust guarantees:

- GitHub, GitLab, Codeberg and SourceForge — source repositories and release history.
- PowerShell Gallery — PowerShell modules and scripts.
- PyPI — Python packages.
- npm — JavaScript packages.
- Greasy Fork — browser userscripts.
- Hugging Face — models, datasets and inference utilities; review each model/dataset card and its terms.
- Reddit and other forums — ideas, recommendations and links only. Forum snippets are not a source-code license and should not be copied as implementation.

Other sources may be added after the same review.

## 4. Intake and security gates

No third-party component may be placed in the production runtime merely because it appears popular or has a permissive license.

For each candidate:

1. Record the canonical project URL, publisher/maintainer, exact release/tag/commit and retrieval date.
2. Identify the license from the actual repository/package release. Save the license text or a stable reference and note whether it covers code, assets, models and dependencies.
3. Read the source. Reject obfuscated, packed, unexplained generated or remotely substituted code unless its origin and behavior can be independently verified.
4. Inspect install/build scripts, dependency manifests, transitive dependencies, post-install hooks, binary assets and update mechanisms.
5. Review network destinations, telemetry, credential handling, file-system access, subprocess execution, shell/PowerShell commands, registry changes, persistence, scheduled tasks and deletion operations.
6. Run suitable static analysis and dependency/vulnerability checks. For PowerShell, use PSScriptAnalyzer where applicable. For Python/JavaScript, use ecosystem-appropriate linters and dependency scanners.
7. Test in an isolated disposable environment with dummy data and no production credentials. Deny network access unless a documented test requires specific destinations.
8. Verify behavior and outputs. Record test evidence, limitations and known vulnerabilities.
9. Pin the exact version or commit and calculate SHA-256 for downloaded source archives/binaries where practical. Do not silently follow mutable branches or unpinned package versions in production.
10. Approve, reject, or defer the candidate in the component registry. Re-review on version upgrades or material changes.

A clean static scan is not proof that code is safe. Human source review and isolation remain required.

## 5. KOMAROVA_CORE-specific safety requirements

- Never give an untrusted component access to real family originals, OAuth tokens, service-role keys, passwords, private archive data or production storage.
- Never commit credentials, private family files, personal filesystem paths, or real archive manifests to Git.
- Original family files remain immutable. Any transformation creates a separate derivative with a new MATERIAL-ID and a link to its source.
- A component must not delete, move, overwrite, publish or share family files unless that exact action is part of an approved workflow with explicit user confirmation and audit logging.
- Keep third-party components behind replaceable adapters where practical. The authoritative registry, PERSON-ID/EVENT-ID/PLACE-ID/MATERIAL-ID values, permissions and audit history remain owned by KOMAROVA_CORE.
- Do not introduce a new paid dependency or hosting requirement without checking the free tier, usage limits, data terms and likely costs.
- Do not claim a component is installed, connected, safe, or operational until the relevant integration and runtime tests pass.

## 6. Component registry

Maintain one entry per component/version. Use `unknown` rather than guessing. A candidate is not approved while required fields or review evidence are missing.

| Field | Required value |
|---|---|
| Component ID | Stable internal identifier |
| Name and purpose | What it does in KOMAROVA_CORE |
| Source URL | Canonical upstream repository or registry page |
| Publisher | Author or maintainer |
| Version / commit | Exact immutable release reference |
| License | Exact identifier and version, or `NO LICENSE` |
| License scope | Code, dependencies, assets, model weights, datasets |
| Notices | Attribution, license files and other obligations |
| SHA-256 | Hash of the reviewed artifact, where practical |
| Dependencies | Direct and transitive dependencies |
| Permissions | Filesystem, network, process, registry and credential access |
| Security review | Reviewer, date, tools and findings |
| Isolated test | Environment, test data and result |
| Deployment location | Repository path, backend service, local path or storage location |
| Data access | Exact data classes the component can access |
| Status | `candidate`, `reviewing`, `approved`, `rejected`, `deferred`, `retired` |
| Approval | Evidence and scope of approval |
| Re-review trigger | New version, changed dependencies, incident or license change |

No third-party component is approved by default. An empty registry means no candidate has yet passed this intake process.

## 7. Initial tool guidance

- PowerShell scripts: inspect the full source and module manifest; run PSScriptAnalyzer; test with least privilege in a disposable Windows environment.
- Python packages: inspect package metadata, source distribution/wheel contents, dependencies and build hooks; pin versions and test in a virtual environment.
- JavaScript/browser userscripts: inspect every permission and remote `@require` / `@resource` dependency; reject unexplained credential collection, broad page access or remote code loading.
- AI models and media tools: review code license, model-weight license, dataset terms, hardware requirements and whether processing can remain local/private.
- Forum recommendations: use them to discover candidates, never as proof of licensing, safety or compatibility.

## 8. Acceptance rule

A component may move to `approved` only when its intended use is compatible with the recorded terms, its source and dependencies have been reviewed, isolated tests have passed, the exact version is pinned, and its deployment/data-access scope is documented.

If any of these conditions is unknown, the status remains `candidate`, `reviewing` or `deferred`.