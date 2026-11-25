#!/usr/bin/env python3
"""Static contract checks for the AI media lab and its real backend routes."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
home = (root / "index.md").read_text(encoding="utf-8")
media = (root / "media.md").read_text(encoding="utf-8")
ai_js = (root / "assets/js/ai-media-enhancer.js").read_text(encoding="utf-8")
archive_js = (root / "assets/js/cloud-archive.js").read_text(encoding="utf-8")
atmosphere = (root / "assets/js/media-atmosphere.js").read_text(encoding="utf-8")
guide = (root / "assets/js/site-guide.js").read_text(encoding="utf-8")
api = (root / "backend/app/cloud_archive_api.py").read_text(encoding="utf-8")
worker = (root / "backend/app/ai_media_worker.py").read_text(encoding="utf-8")
workflow = (root / ".github/workflows/pages-build.yml").read_text(encoding="utf-8")

def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("AI media lab contract failed: " + message)

require('id="ai-media-enhancer"' in home and 'data-ai-media-lab' in home, "AI media workspace is missing")
require('data-ai-connect-form' in home and 'data-ai-api-url' in home, "private backend connection form is missing")
password = re.search(r'<input[^>]*data-ai-password[^>]*>', home, re.I)
require(password is not None and 'type="password"' in password.group(0), "AI media password must be masked")
require("value=" not in password.group(0).lower(), "AI media password field must be empty by default")
for selector in ("data-ai-upload", "data-ai-view", "data-ai-export", "data-ai-original-preview", "data-ai-result-preview"):
    require(selector in home, "missing interactive AI media control: " + selector)
for endpoint in ('"/api/v1/auth/login"', '"/api/v1/archive/items"', '"/scan"', '"/enhance"', '"/content"'):
    require(endpoint in ai_js, "frontend is missing endpoint contract: " + endpoint)
require("accessToken = payload.access_token" in ai_js and "sessionStorage" not in ai_js, "AI session token must remain in page memory only")
require("passwordInput.value = \"\"" in ai_js, "password must be cleared after connection")
require("MAX_BYTES = 100 * 1024 * 1024" in ai_js and "MAX_PIXELS = 30000000" in ai_js, "local file safety limits are missing")
require("Проверка SHA-256" in ai_js and "sourceHashBefore !== sourceHashAfter" in ai_js, "original integrity check is missing")
require("ClamAV не запускался" in ai_js and "поддельная копия" in ai_js, "disconnected worker must be reported honestly")
for route in ('@router.post("/items/{archive_item_id}/scan")', '@router.post("/items/{archive_item_id}/enhance")', '@router.get("/items/{archive_item_id}/content")'):
    require(route in api, "backend route missing: " + route)
require('Depends(require_roles("owner", "moderator"))' in api, "scan/enhancement privilege checks are missing")
require("if source == output: raise ValueError" in worker, "worker must refuse to overwrite the original")
require("source.stat().st_size > MAX_INPUT_BYTES" in worker and "scan_or_fail(source)" in worker, "worker scan and size guard are missing")
require("Real-ESRGAN NCNN Vulkan x{scale}" in worker, "Real-ESRGAN engine contract is missing")
require("sessionStorage" not in archive_js, "private archive access token must not persist in sessionStorage")
require("Частный backend пока недоступен" in archive_js and "friendlyError" in archive_js, "archive offline state must be clear")
require("sceneManuallySelected" in atmosphere, "manual nature scene selection must not be overridden by the auto-cycle")
require("generations:" in guide and "events:" in guide and "family:" in guide, "contextual navigation tabs are incomplete")
require("node --check assets/js/media-atmosphere.js" in workflow, "atmosphere JavaScript syntax is not checked")
require("node --check assets/js/cloud-archive.js" in workflow, "archive JavaScript syntax is not checked")
require("python3 scripts/check_ai_media_lab.py" in workflow, "AI media contract checker is not in CI")
print("AI media lab contract passed.")
