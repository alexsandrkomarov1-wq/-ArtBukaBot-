#!/usr/bin/env bash
set -Eeuo pipefail

: "${DATABASE_URL:?DATABASE_URL must be configured}"
: "${CORE_MEDIA_ROOT:?CORE_MEDIA_ROOT must be configured}"
: "${CORE_BACKUP_DIR:?CORE_BACKUP_DIR must be configured}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$CORE_BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$CORE_BACKUP_DIR/komarova-core-$STAMP.kcb"

cd "$ROOT"
python3 -m scripts.private_backup create "$DEST"
python3 -m scripts.private_backup verify "$DEST"
printf 'BACKUP_VERIFIED=%s\n' "$DEST"
