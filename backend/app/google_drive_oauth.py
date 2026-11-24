from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from datetime import timedelta
from urllib.parse import urlencode

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import AuditEvent, GoogleDriveAccount, GoogleOAuthState, User, new_id, utc_now

DRIVE_METADATA_SCOPE = "https://www.googleapis.com/auth/drive.metadata.readonly"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
GOOGLE_ABOUT_URL = "https://www.googleapis.com/drive/v3/about"


def _encryption_key() -> bytes:
    raw = os.getenv("CORE_OAUTH_ENCRYPTION_KEY", "").strip()
    if not raw:
        raise RuntimeError("CORE_OAUTH_ENCRYPTION_KEY is not configured")
    try:
        key = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    except Exception as exc:
        raise RuntimeError("CORE_OAUTH_ENCRYPTION_KEY must be URL-safe base64") from exc
    if len(key) != 32:
        raise RuntimeError("CORE_OAUTH_ENCRYPTION_KEY must decode to exactly 32 bytes")
    return key


def encrypt_refresh_token(token: str, user_id: str) -> str:
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(_encryption_key()).encrypt(
        nonce, token.encode("utf-8"), f"google-drive:{user_id}".encode("utf-8")
    )
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")


def decrypt_refresh_token(value: str, user_id: str) -> str:
    payload = base64.urlsafe_b64decode(value.encode("ascii"))
    nonce, ciphertext = payload[:12], payload[12:]
    plaintext = AESGCM(_encryption_key()).decrypt(
        nonce, ciphertext, f"google-drive:{user_id}".encode("utf-8")
    )
    return plaintext.decode("utf-8")


def _oauth_config() -> tuple[str, str, str]:
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("GOOGLE_DRIVE_REDIRECT_URI", "").strip()
    missing = [
        name for name, value in (
            ("GOOGLE_OAUTH_CLIENT_ID", client_id),
            ("GOOGLE_OAUTH_CLIENT_SECRET", client_secret),
            ("GOOGLE_DRIVE_REDIRECT_URI", redirect_uri),
        ) if not value
    ]
    if missing:
        raise HTTPException(
            status_code=503,
            detail="Google Drive OAuth is not configured: " + ", ".join(missing),
        )
    if not redirect_uri.startswith("https://") and not redirect_uri.startswith("http://localhost"):
        raise HTTPException(status_code=503, detail="Google Drive callback must use HTTPS")
    try:
        _encryption_key()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return client_id, client_secret, redirect_uri


def _google_about(access_token: str) -> dict:
    response = httpx.get(
        GOOGLE_ABOUT_URL,
        params={"fields": "user(permissionId,emailAddress,displayName),storageQuota(limit,usage,usageInDrive,usageInDriveTrash)"},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20.0,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Google Drive account metadata could not be read")
    return response.json()


def build_google_drive_router(get_db, require_current_user) -> APIRouter:
    router = APIRouter(prefix="/api/v1/integrations/google-drive", tags=["google-drive"])

    @router.get("/connect")
    def begin_connect(
        db: Session = Depends(get_db),
        user: User = Depends(require_current_user),
    ):
        client_id, _, redirect_uri = _oauth_config()
        state = secrets.token_urlsafe(48)
        db.query(GoogleOAuthState).filter(
            GoogleOAuthState.expires_at < utc_now()
        ).delete(synchronize_session=False)
        db.add(GoogleOAuthState(
            state_hash=hashlib.sha256(state.encode("utf-8")).hexdigest(),
            user_id=user.user_id,
            expires_at=utc_now() + timedelta(minutes=10),
        ))
        db.commit()
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": DRIVE_METADATA_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
        }
        return {
            "authorization_url": f"{GOOGLE_AUTH_URL}?{urlencode(params)}",
            "redirect_uri": redirect_uri,
            "requested_access": "read-only Drive account identity and storage quota",
            "expires_in_seconds": 600,
        }

    @router.get("/callback")
    def complete_connect(
        code: str | None = Query(default=None),
        state: str | None = Query(default=None),
        error: str | None = Query(default=None),
        db: Session = Depends(get_db),
    ):
        if not state:
            raise HTTPException(status_code=400, detail="OAuth state is missing")
        state_hash = hashlib.sha256(state.encode("utf-8")).hexdigest()
        pending = db.scalar(select(GoogleOAuthState).where(
            GoogleOAuthState.state_hash == state_hash
        ))
        if pending is None or pending.expires_at <= utc_now():
            if pending is not None:
                db.delete(pending)
                db.commit()
            raise HTTPException(status_code=400, detail="OAuth state is invalid, expired, or already used")
        user_id = pending.user_id
        db.delete(pending)
        db.commit()
        linked_user = db.get(User, user_id)
        if linked_user is None or linked_user.status != "active":
            raise HTTPException(status_code=401, detail="KOMAROVA_CORE account is unavailable")
        if error:
            raise HTTPException(status_code=400, detail="Google authorization was not granted")
        if not code:
            raise HTTPException(status_code=400, detail="Google authorization code is missing")

        client_id, client_secret, redirect_uri = _oauth_config()
        try:
            token_response = httpx.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=20.0,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Google token exchange failed") from exc
        if token_response.status_code != 200:
            raise HTTPException(status_code=502, detail="Google token exchange was rejected")
        token_data = token_response.json()
        refresh_token = token_data.get("refresh_token")
        access_token = token_data.get("access_token")
        granted_scopes = set(token_data.get("scope", "").split())
        if not refresh_token or not access_token:
            raise HTTPException(
                status_code=502,
                detail="Google did not return offline credentials; reconnect and grant consent",
            )
        if DRIVE_METADATA_SCOPE not in granted_scopes:
            raise HTTPException(status_code=403, detail="Google did not grant the required read-only Drive scope")

        about = _google_about(access_token)
        google_user = about.get("user") or {}
        google_user_id = google_user.get("permissionId")
        email = google_user.get("emailAddress")
        if not google_user_id or not email:
            raise HTTPException(status_code=502, detail="Google Drive did not return a stable account identity")
        quota = about.get("storageQuota") or {}

        account = db.scalar(select(GoogleDriveAccount).where(
            GoogleDriveAccount.user_id == user_id
        ))
        encrypted_token = encrypt_refresh_token(refresh_token, user_id)
        if account is None:
            account = GoogleDriveAccount(
                drive_account_id=new_id("GD"),
                user_id=user_id,
                google_user_id=google_user_id,
                email_address=email,
                display_name=google_user.get("displayName"),
                refresh_token_ciphertext=encrypted_token,
                granted_scopes=" ".join(sorted(granted_scopes)),
            )
            db.add(account)
        else:
            account.google_user_id = google_user_id
            account.email_address = email
            account.display_name = google_user.get("displayName")
            account.refresh_token_ciphertext = encrypted_token
            account.granted_scopes = " ".join(sorted(granted_scopes))
            account.revoked_at = None
        db.flush()
        account.quota_limit_bytes = int(quota["limit"]) if quota.get("limit") else None
        account.quota_usage_bytes = int(quota["usage"]) if quota.get("usage") else None
        account.quota_usage_in_drive_bytes = int(quota["usageInDrive"]) if quota.get("usageInDrive") else None
        account.quota_usage_in_trash_bytes = int(quota["usageInDriveTrash"]) if quota.get("usageInDriveTrash") else None
        account.last_quota_at = utc_now()
        db.add(AuditEvent(
            event_type="google_drive.account_connected",
            entity_type="google_drive_account",
            entity_id=account.drive_account_id,
            actor_id=user_id,
            details=json.dumps({"email_address": email, "scope": DRIVE_METADATA_SCOPE}, ensure_ascii=False),
        ))
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="This Google account is already linked to another family user") from exc
        return {
            "status": "connected",
            "provider": "google-drive",
            "email_address": email,
            "display_name": google_user.get("displayName"),
            "access": "metadata_read_only",
            "quota_limit_bytes": account.quota_limit_bytes,
            "quota_usage_bytes": account.quota_usage_bytes,
            "quota_usage_in_drive_bytes": account.quota_usage_in_drive_bytes,
            "quota_usage_in_trash_bytes": account.quota_usage_in_trash_bytes,
            "message": "Google Drive account linked. File contents have not been accessed.",
        }

    @router.get("/status")
    def connection_status(
        db: Session = Depends(get_db),
        user: User = Depends(require_current_user),
    ):
        account = db.scalar(select(GoogleDriveAccount).where(
            GoogleDriveAccount.user_id == user.user_id,
            GoogleDriveAccount.revoked_at.is_(None),
        ))
        if account is None:
            return {"status": "not_connected", "provider": "google-drive"}
        return {
            "status": "connected",
            "provider": "google-drive",
            "email_address": account.email_address,
            "display_name": account.display_name,
            "access": "metadata_read_only",
            "quota_limit_bytes": account.quota_limit_bytes,
            "quota_usage_bytes": account.quota_usage_bytes,
            "quota_usage_in_drive_bytes": account.quota_usage_in_drive_bytes,
            "quota_usage_in_trash_bytes": account.quota_usage_in_trash_bytes,
            "last_quota_at": account.last_quota_at.isoformat() if account.last_quota_at else None,
        }

    @router.post("/refresh-quota")
    def refresh_quota(
        db: Session = Depends(get_db),
        user: User = Depends(require_current_user),
    ):
        _, client_secret, _ = _oauth_config()
        account = db.scalar(select(GoogleDriveAccount).where(
            GoogleDriveAccount.user_id == user.user_id,
            GoogleDriveAccount.revoked_at.is_(None),
        ))
        if account is None:
            raise HTTPException(status_code=404, detail="Google Drive account is not connected")
        refresh_token = decrypt_refresh_token(account.refresh_token_ciphertext, user.user_id)
        try:
            token_response = httpx.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip(),
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                timeout=20.0,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Google access token refresh failed") from exc
        if token_response.status_code != 200:
            raise HTTPException(status_code=502, detail="Google refresh token was rejected; reconnect the account")
        about = _google_about(token_response.json()["access_token"])
        quota = about.get("storageQuota") or {}
        account.quota_limit_bytes = int(quota["limit"]) if quota.get("limit") else None
        account.quota_usage_bytes = int(quota["usage"]) if quota.get("usage") else None
        account.quota_usage_in_drive_bytes = int(quota["usageInDrive"]) if quota.get("usageInDrive") else None
        account.quota_usage_in_trash_bytes = int(quota["usageInDriveTrash"]) if quota.get("usageInDriveTrash") else None
        account.last_quota_at = utc_now()
        db.add(AuditEvent(
            event_type="google_drive.quota_refreshed",
            entity_type="google_drive_account",
            entity_id=account.drive_account_id,
            actor_id=user.user_id,
            details=json.dumps({"quota_updated": True}),
        ))
        db.commit()
        return {
            "status": "ok",
            "quota_limit_bytes": account.quota_limit_bytes,
            "quota_usage_bytes": account.quota_usage_bytes,
            "quota_usage_in_drive_bytes": account.quota_usage_in_drive_bytes,
            "quota_usage_in_trash_bytes": account.quota_usage_in_trash_bytes,
            "last_quota_at": account.last_quota_at.isoformat(),
        }

    @router.delete("/disconnect")
    def disconnect(
        db: Session = Depends(get_db),
        user: User = Depends(require_current_user),
    ):
        _, _, _ = _oauth_config()
        account = db.scalar(select(GoogleDriveAccount).where(
            GoogleDriveAccount.user_id == user.user_id,
            GoogleDriveAccount.revoked_at.is_(None),
        ))
        if account is None:
            return {"status": "not_connected"}
        refresh_token = decrypt_refresh_token(account.refresh_token_ciphertext, user.user_id)
        try:
            response = httpx.post(GOOGLE_REVOKE_URL, params={"token": refresh_token}, timeout=20.0)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Google token revocation request failed") from exc
        if response.status_code not in (200, 400):
            raise HTTPException(status_code=502, detail="Google token revocation was not confirmed")
        db.add(AuditEvent(
            event_type="google_drive.account_disconnected",
            entity_type="google_drive_account",
            entity_id=account.drive_account_id,
            actor_id=user.user_id,
            details=json.dumps({"revoked_at_provider": response.status_code == 200}),
        ))
        db.delete(account)
        db.commit()
        return {"status": "disconnected"}

    return router
