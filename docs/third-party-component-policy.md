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

## 9. Additional discovery sources and repository handling

The following sources are added to the discovery list. They are intake locations only; none is an automatic approval or a place to execute downloaded code directly:

- PowerShell Gallery: https://www.powershellgallery.com/ — discover administration, diagnostics, backup, file-management and automation modules. Microsoft describes the Gallery as community-owned and untrusted by default for production dependency use; download for review, then promote only a pinned, reviewed version into the project's controlled component set.
- Greasy Fork: https://greasyfork.org/ — discover browser userscripts only where browser automation genuinely helps the project. Read the complete source and every metadata directive. Greasy Fork requires readable, non-obfuscated source and license/copyright compliance; external executable code is restricted and must be inspected separately.
- Reddit discussion supplied for discovery: https://www.reddit.com/r/Notion/comments/ndlz9i/devs_where_do_you_host_your_automation_scripts/?tl=ru — community discussion about where developers host automation scripts. Treat recommendations as leads, not proof of availability, security, license or suitability. Re-check each service's current terms and free-tier limits before use.
- GitHub/GitLab/Codeberg: prefer upstream source repositories with release tags, commit history, security advisories and issue tracking. Pin a commit or release; do not install from a moving branch.

Useful primary review references:
- PowerShell Gallery publishing and signing guidance: https://learn.microsoft.com/en-us/powershell/gallery/concepts/publishing-guidelines
- PowerShell repository trust guidance: https://learn.microsoft.com/en-us/powershell/gallery/powershellget/supported-repositories
- Greasy Fork source-code rules: https://greasyfork.org/ru/help/code-rules
- Greasy Fork external-code policy: https://greasyfork.org/en/help/external-scripts

## 10. Domain, DNS, servers and hosting inventory

Keep domain registration, DNS, hosting, compute servers, object storage, database and source-code hosting as separate infrastructure records. A domain name does not provide a server, and a hosting account does not automatically provide private archive storage.

The `.su` top-level domain is the historic country-code domain assigned to the Soviet Union in 1990 and is still administered today. It is a domain namespace only; it is not a Soviet server network, hosting provider, data-centre location or guarantee of free hosting. Treat any proposed `.su` domain as an optional naming/identity choice, not as the archive's storage or compute solution.

For every domain/hosting/server candidate, record:
- provider and official service URL;
- domain name and registrar (if applicable), renewal price and transfer/expiry rules;
- DNS provider and control of DNS records;
- server/hosting type (static hosting, VPS, dedicated server, managed application, object storage, database);
- physical region/data residency, operator and jurisdiction, where verifiable;
- CPU, RAM, disk type/capacity, traffic and bandwidth limits;
- maximum single-object upload size, request/body timeout and resumable/multipart upload support;
- TLS/HTTPS, backups, restore/export, snapshots and retention;
- private access controls, encryption, audit logs and account recovery;
- free-tier conditions, quotas, inactivity suspension, payment requirements and overage costs;
- deployment method, supported runtime, repository integration and rollback;
- terms of service, privacy/data-processing terms and account ownership;
- evidence URL, check date and status.

Do not infer that a provider is free, that a domain includes hosting, or that a stated storage quota is also the maximum size of one uploaded file. Verify those limits separately from current official documentation. Never migrate family originals or change production DNS based only on a forum recommendation.

Initial domain/hosting research entries:
| Candidate | Official URL | What it is | Initial status |
|---|---|---|---|
| .SU namespace | https://www.ripn.su/en/domen-su/history/ | Historic domain namespace; not hosting | research only |
| Register.su | https://register.su/questions-about-su-domains/ | .SU registration information | research only; verify current registrar terms/pricing |
| PowerShell Gallery | https://www.powershellgallery.com/ | Script/module repository, not hosting for KOMAROVA_CORE | discovery only |
| Greasy Fork | https://greasyfork.org/ | Browser userscript repository, not server hosting | discovery only |
| Reddit thread supplied by owner | https://www.reddit.com/r/Notion/comments/ndlz9i/devs_where_do_you_host_your_automation_scripts/?tl=ru | Community leads on automation hosting | discovery only |

No new domain has been registered, no hosting account has been created, and no server or DNS configuration has been changed by this documentation update.
