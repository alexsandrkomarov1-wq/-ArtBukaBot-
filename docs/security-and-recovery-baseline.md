# KOMAROVA_CORE security and recovery baseline

Status: implementation foundation committed to a feature branch; production controls are NOT active until the backend is deployed behind the selected provider and the operational checks below are completed.

## Mandatory controls

1. HTTPS for every public connection.
2. Malware scanning of uploaded files with ClamAV.
3. Fail-closed quarantine until a clean scan and checksum verification.
4. Provider-edge DDoS protection for L3/L4/L7.
5. Daily backup of the database and private media objects.
6. SHA-256 verification and database integrity checks for every backup.
7. Scheduled restore drills into a separate, empty destination.
8. Original media and every derivative included as separate files in the backup; the original is never overwritten.

## Implemented in this repository

- Uploads are stored as private quarantined objects. The existing content endpoint refuses access unless the archive record is `available` and the blob is `verified`.
- `POST /api/v1/archive/items/{id}/scan` is an owner/moderator-only ClamAV scan operation. It verifies stored length and SHA-256 before scanning. A clean result releases the object; an infected result marks it infected and keeps it inaccessible; missing scanner, timeout, integrity mismatch, and scanner errors leave the object quarantined.
- Complete local SQLite + media backup utility: `python -m scripts.private_backup create <destination.kcb>`.
- Verify: `python -m scripts.private_backup verify <destination.kcb>`.
- Restore to a NEW empty directory: `python -m scripts.private_backup restore <source.kcb> <new-directory>`.
- The bundle contains the SQLite online backup, all regular files under `CORE_MEDIA_ROOT` (including quarantine originals and derivatives), and a SHA-256 manifest. Symlinks are rejected. Existing destinations are never overwritten.
- The restore operation revalidates archive checksums, SQLite integrity, foreign keys, required schema tables, and restored media checksums.

## Daily backup scheduling

Run the backend on a persistent private host. Set `DATABASE_URL` to a file-backed SQLite database and `CORE_MEDIA_ROOT` to the private media directory. Set `CORE_BACKUP_DIR` to a separate mounted backup volume or off-site mounted storage.

Example daily cron entry (02:20 UTC):

```cron
20 2 * * * cd /opt/komarova-core && DATABASE_URL='sqlite:////var/lib/komarova-core/core.sqlite3' CORE_MEDIA_ROOT='/var/lib/komarova-core/media' CORE_BACKUP_DIR='/mnt/backup/komarova-core' /bin/bash ops/backup-daily.sh >> /var/log/komarova-core-backup.log 2>&1
```

The scheduled job creates a timestamped bundle and immediately verifies it. The backup target must be on a separate disk or off-site volume; a second folder on the same ephemeral container disk is not a backup. Protect backup volumes with filesystem permissions and encryption at rest. Replicate to a second independent location and monitor job exit status. Retention is controlled by the backup provider; this project does not claim indefinite retention unless the provider contract and storage capacity guarantee it.

## HTTPS and edge protection

- GitHub Pages serves the current static site over HTTPS using GitHub-managed certificates. This does not provide a configurable WAF or establish protection for a future private API.
- For the private API, use the supplied Caddy reverse-proxy template in `ops/Caddyfile`. Caddy obtains and renews public certificates automatically through ACME when a real DNS hostname points to the host and inbound ports 80/443 are reachable.
- Put the public DNS hostname behind a provider proxy with L3/L4/L7 DDoS mitigation (for example, Cloudflare proxy) and enable its WAF/rate-limiting controls where available. The edge provider must proxy both DNS A/AAAA/CNAME records; direct origin access should be restricted to the provider's published IP ranges.
- DDoS mitigation is an upstream provider capability, not something an application library or this repository can switch on. No custom domain, DNS proxy, API host, or provider account is configured by this change. Do not expose the API publicly until those settings are verified.

## ClamAV deployment

Install ClamAV daemon and `clamdscan` on the same private worker host/container as the API process, keep virus definitions updated, and set `CORE_CLAMDSCAN_BINARY` if the executable has a different path. The scan endpoint deliberately fails closed when the scanner is absent or unavailable. Do not mount the private media directory into the public web root.

The scanner endpoint currently performs an authenticated on-demand scan of a quarantined object. A production rollout should add a durable queue/worker to scan every upload automatically, with retry and alerting. Until that worker is deployed, uploads remain quarantined and cannot be viewed; a manual scan endpoint is not equivalent to a continuously running antivirus service.

## Backup scope and limitations

The complete backup utility currently supports file-backed SQLite and local `CORE_MEDIA_ROOT`. It deliberately refuses PostgreSQL and remote object-storage backends rather than silently producing an incomplete backup. Before using PostgreSQL or remote S3-compatible storage in production, implement and test `pg_dump` plus object-store inventory/download and checksum verification. Never report a full backup when only the database or only media was copied.

A restore drill must be performed at least monthly into a separate host or isolated directory. Record the backup timestamp, verification result, restore duration, and recovered file/database counts. Keep the source backup unchanged.

## Production release checklist

- [ ] Backend deployed on a persistent private host; no public filesystem exposure.
- [ ] Real hostname, DNS, Caddy HTTPS certificate, renewal and redirect verified.
- [ ] Edge DDoS/WAF provider configured; origin locked to provider traffic.
- [ ] ClamAV daemon active, signatures current, clean/infected/error test files verified.
- [ ] Automatic upload scan queue and alerting deployed.
- [ ] Daily database + media backup scheduled to independent storage.
- [ ] Backup encryption and access control verified.
- [ ] Backup integrity job alerts on failure.
- [ ] Monthly restore drill passes.
- [ ] Original and derivative checksums and MATERIAL-ID relationships survive restore.
- [ ] No real family data stored in the public GitHub repository or GitHub Pages.

Until every applicable item is checked against a live deployment, the project status remains DEVELOPMENT / NOT PRODUCTION-READY.
