"""Private cloud-provider adapters for KOMAROVA_CORE.

Credentials are read only from server environment variables. Provider IDs are
opaque and must never be exposed as public download URLs.
"""
from __future__ import annotations

import hashlib
import http.client
import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen


class CloudProviderError(RuntimeError):
    pass


def _json_request(url: str, *, method: str = "GET", headers: dict | None = None,
                  payload: dict | None = None, timeout: int = 60) -> dict:
    request_headers = dict(headers or {})
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    request = Request(url, data=body, headers=request_headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except HTTPError as exc:
        detail = exc.read(2048).decode("utf-8", "replace")
        raise CloudProviderError(f"http_{exc.code}:{detail[:300]}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise CloudProviderError(f"network_error:{type(exc).__name__}") from exc


def _download(url: str, destination: Path, headers: dict | None = None) -> tuple[int, str]:
    request = Request(url, headers=headers or {})
    digest = hashlib.sha256()
    size = 0
    try:
        with urlopen(request, timeout=120) as response, destination.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)
                size += len(chunk)
    except HTTPError as exc:
        raise CloudProviderError(f"download_http_{exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise CloudProviderError(f"download_network_error:{type(exc).__name__}") from exc
    return size, digest.hexdigest()


class OneDriveProvider:
    name = "onedrive"
    GRAPH = "https://graph.microsoft.com/v1.0"
    CHUNK_BYTES = 10 * 1024 * 1024  # multiple of Graph's 320 KiB requirement

    def __init__(self) -> None:
        self.folder_id = os.getenv("ONEDRIVE_FOLDER_ID", "").strip()
        self.access_token = os.getenv("ONEDRIVE_ACCESS_TOKEN", "").strip()
        self.refresh_token = os.getenv("ONEDRIVE_REFRESH_TOKEN", "").strip()
        self.client_id = os.getenv("ONEDRIVE_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET", "").strip()
        self.tenant = os.getenv("ONEDRIVE_TENANT_ID", "consumers").strip() or "consumers"
        if not self.folder_id:
            raise CloudProviderError("onedrive_folder_id_missing")
        if not self.access_token and not all((self.refresh_token, self.client_id)):
            raise CloudProviderError("onedrive_credentials_missing")

    def _token(self) -> str:
        if self.access_token:
            return self.access_token
        # Form encoding is required by Microsoft's token endpoint.
        body = urlencode({
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
            "scope": "offline_access Files.ReadWrite",
            **({"client_secret": self.client_secret} if self.client_secret else {}),
        }).encode("utf-8")
        request = Request(
            f"https://login.microsoftonline.com/{quote(self.tenant, safe='')}/oauth2/v2.0/token",
            data=body, headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise CloudProviderError("onedrive_token_refresh_failed") from exc
        self.access_token = data.get("access_token", "")
        if not self.access_token:
            raise CloudProviderError("onedrive_access_token_missing")
        return self.access_token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token()}"}

    def quota(self) -> dict[str, int | None]:
        data = _json_request(f"{self.GRAPH}/me/drive?$select=quota", headers=self._headers())
        quota = data.get("quota") or {}
        total, used = quota.get("total"), quota.get("used")
        remaining = quota.get("remaining")
        if remaining is None and isinstance(total, int) and isinstance(used, int):
            remaining = max(0, total - used)
        return {"total_bytes": total, "used_bytes": used, "remaining_bytes": remaining}

    def upload(self, source: Path, *, blob_id: str, filename: str, size_bytes: int) -> str:
        safe_name = f"{blob_id}_{Path(filename).name}"
        url = (f"{self.GRAPH}/me/drive/items/{quote(self.folder_id, safe='')}:/"
               f"{quote(safe_name, safe='')}:/createUploadSession")
        session = _json_request(
            url, method="POST", headers=self._headers(),
            payload={"item": {"@microsoft.graph.conflictBehavior": "fail", "name": safe_name}},
        )
        upload_url = session.get("uploadUrl")
        if not upload_url:
            raise CloudProviderError("onedrive_upload_session_missing")
        offset = 0
        with source.open("rb") as stream:
            while offset < size_bytes:
                chunk = stream.read(min(self.CHUNK_BYTES, size_bytes - offset))
                if not chunk:
                    raise CloudProviderError("source_file_truncated")
                end = offset + len(chunk) - 1
                request = Request(upload_url, data=chunk, headers={
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {offset}-{end}/{size_bytes}",
                }, method="PUT")
                try:
                    with urlopen(request, timeout=180) as response:
                        data = json.loads(response.read().decode("utf-8")) if response.length != 0 else {}
                except HTTPError as exc:
                    if exc.code in (416, 429, 500, 502, 503, 504):
                        # Query session state and continue from the server's first missing range.
                        state = _json_request(upload_url)
                        ranges = state.get("nextExpectedRanges") or []
                        if not ranges:
                            raise CloudProviderError(f"onedrive_upload_http_{exc.code}") from exc
                        offset = int(ranges[0].split("-", 1)[0])
                        stream.seek(offset)
                        time.sleep(2)
                        continue
                    raise CloudProviderError(f"onedrive_upload_http_{exc.code}") from exc
                if "id" in data:
                    return data["id"]
                offset += len(chunk)
        raise CloudProviderError("onedrive_upload_incomplete")

    def download(self, remote_id: str, destination: Path) -> tuple[int, str]:
        # Graph returns a short-lived pre-authenticated redirect for /content.
        url = f"{self.GRAPH}/me/drive/items/{quote(remote_id, safe='')}/content"
        request = Request(url, headers=self._headers())
        try:
            with urlopen(request, timeout=60) as response:
                redirect = response.geturl()
        except Exception as exc:
            raise CloudProviderError("onedrive_download_link_failed") from exc
        return _download(redirect, destination)


class YandexDiskProvider:
    name = "yandex-disk"
    API = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self) -> None:
        self.token = os.getenv("YANDEX_DISK_ACCESS_TOKEN", "").strip()
        self.root = os.getenv("YANDEX_DISK_ROOT", "/KOMAROVA_CORE").strip().rstrip("/")
        if not self.token:
            raise CloudProviderError("yandex_disk_token_missing")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"OAuth {self.token}"}

    def quota(self) -> dict[str, int | None]:
        data = _json_request(self.API, headers=self._headers())
        total, used = data.get("total_space"), data.get("used_space")
        return {
            "total_bytes": total, "used_bytes": used,
            "remaining_bytes": max(0, total - used) if isinstance(total, int) and isinstance(used, int) else None,
        }

    def upload(self, source: Path, *, blob_id: str, filename: str, size_bytes: int) -> str:
        # Yandex Disk's public REST upload flow provides one upload URL, not a
        # resumable chunk-session API. Retry is handled by the durable outbox.
        remote_path = f"{self.root}/{blob_id}_{Path(filename).name}"
        params = urlencode({"path": remote_path, "overwrite": "false"})
        data = _json_request(f"{self.API}/resources/upload?{params}", headers=self._headers())
        href = data.get("href")
        if not href:
            raise CloudProviderError("yandex_upload_href_missing")
        parsed = urlsplit(href)
        if parsed.scheme != "https" or not parsed.hostname:
            raise CloudProviderError("yandex_upload_url_invalid")
        connection = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=300)
        try:
            connection.putrequest("PUT", parsed.path + (f"?{parsed.query}" if parsed.query else ""))
            connection.putheader("Content-Type", "application/octet-stream")
            connection.putheader("Content-Length", str(size_bytes))
            connection.endheaders()
            with source.open("rb") as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    connection.send(chunk)
            response = connection.getresponse()
            response.read()
            if response.status not in (201, 202):
                raise CloudProviderError(f"yandex_upload_http_{response.status}")
        except (OSError, TimeoutError) as exc:
            raise CloudProviderError(f"yandex_upload_network_error:{type(exc).__name__}") from exc
        finally:
            connection.close()
        return remote_path

    def download(self, remote_id: str, destination: Path) -> tuple[int, str]:
        params = urlencode({"path": remote_id})
        data = _json_request(f"{self.API}/resources/download?{params}", headers=self._headers())
        href = data.get("href")
        if not href:
            raise CloudProviderError("yandex_download_href_missing")
        return _download(href, destination)


def build_provider(name: str):
    normalized = name.strip().lower()
    if normalized == "onedrive":
        return OneDriveProvider()
    if normalized in {"yandex", "yandex-disk"}:
        return YandexDiskProvider()
    raise CloudProviderError(f"unsupported_provider:{normalized}")
