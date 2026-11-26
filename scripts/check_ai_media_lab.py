#!/usr/bin/env python3
"""Static contract checks for the AI media lab and its real backend routes."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
home = (root / "index.md").read_text(encoding="utf-8")
media = (root / "media.md").read_text(encoding="utf-8")
ai_js = (root / "assets/js/ai-media-enhancer.js").read_text(encoding="utf-8")
archive_js = (root / "assets/js/supabase-archive.js").read_text(encoding="utf-8")
atmosphere = (root / "assets/js/media-atmosphere.js").read_text(encoding="utf-8")
guide = (root / "assets/js/site-guide.js").read_text(encoding="utf-8")
api = (root / "backend/app/cloud_archive_api.py").read_text(encoding="utf-8")
worker = (root / "backend/app/ai_media_worker.py").read_text(encoding="utf-8")
workflow = (root / ".github/workflows/pages-build.yml").read_text(encoding="utf-8")
registry_client = (root / "assets/js/registry-client.js").read_text(encoding="utf-8")
family_board = (root / "family-board.md").read_text(encoding="utf-8")
family_map = (root / "assets/js/family-board-map.js").read_text(encoding="utf-8")
generations = (root / "generations.md").read_text(encoding="utf-8")
events = (root / "events.md").read_text(encoding="utf-8")

def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("AI media lab contract failed: " + message)

require('id="ai-media-enhancer"' in home and 'data-ai-media-lab' in home, "AI media workspace is missing")
require("ezenhancer.ai" not in home.lower(), "AI MEDIA must not redirect users to an external enhancer")
require("ai-media-internal-engine" in home and "ВНУТРЕННИЙ AI-КОНВЕЙЕР KOMAROVA_CORE" in home, "internal AI processing notice is missing")
require("data-ai-connect-form" not in home and "data-ai-api-url" not in home, "AI editor must not expose backend URL or login fields")
require("АВТОМАТИЧЕСКОЕ AI-УЛУЧШЕНИЕ" in home, "automatic AI enhancement instructions are missing")
require("data-ai-connect-form" not in ai_js and "accessToken" not in ai_js, "AI editor must not depend on manual browser credentials")
require("cloud-person-id" not in media and "cloud-event-id" not in media and "cloud-place-id" not in media, "archive upload must not ask users to type entity identifiers")
for selector in ("data-ai-upload", "data-ai-view", "data-ai-export", "data-ai-original-preview", "data-ai-result-preview"):
    require(selector in home, "missing interactive AI media control: " + selector)
for route in ('@router.post("/items/{archive_item_id}/scan")', '@router.post("/items/{archive_item_id}/enhance")', '@router.get("/items/{archive_item_id}/content")'):
    require(route in api, "backend worker route is missing: " + route)
require("MAX_BYTES = 100 * 1024 * 1024" in ai_js and "MAX_PIXELS = 30000000" in ai_js, "local file safety limits are missing")
require("Проверка SHA-256" in ai_js and "sourceHashBefore !== sourceHashAfter" in ai_js, "original integrity check is missing")
require("ClamAV не запускалась" in ai_js and "фиктивный ролик не создаётся" in ai_js and "AI-ДВИЖОК НЕ УСТАНОВЛЕН" in ai_js, "disconnected worker must be reported honestly")
for route in ('@router.post("/items/{archive_item_id}/scan")', '@router.post("/items/{archive_item_id}/enhance")', '@router.get("/items/{archive_item_id}/content")'):
    require(route in api, "backend route missing: " + route)
require('Depends(require_roles("owner", "moderator"))' in api, "scan/enhancement privilege checks are missing")
require("if source == output: raise ValueError" in worker, "worker must refuse to overwrite the original")
require("source.stat().st_size > MAX_INPUT_BYTES" in worker and "scan_or_fail(source)" in worker, "worker scan and size guard are missing")
require("Real-ESRGAN NCNN Vulkan x{scale}" in worker, "Real-ESRGAN engine contract is missing")
require("sessionStorage" not in archive_js and "localStorage" not in archive_js, "Supabase credentials and tokens must remain in page memory")
require("/auth/v1/token?grant_type=password" in archive_js and "/storage/v1/object/" in archive_js, "Supabase Auth and private Storage routes are missing")
require("archive_items" in archive_js and "sha256" in archive_js and "M-" in archive_js, "archive registry, checksum and MATERIAL-ID are missing")
require("service_role" in media.lower(), "page must warn against exposing the service role key")
require("cloud-username" in media and "type=\"email\"" in media, "private archive account login must remain separate from the AI editor")
require("ezenhancer.ai" not in ai_js.lower(), "AI MEDIA must not direct users to an external enhancer")
require("sceneManuallySelected" in atmosphere, "manual nature scene selection must not be overridden by the auto-cycle")
require("generations:" in guide and "events:" in guide and "family:" in guide, "contextual navigation tabs are incomplete")
require("Частный backend не отвечает" in registry_client, "registry pages must explain API connection failures")
require('data-fb-tab="board"' in family_board and 'data-fb-tab="map"' in family_board and 'id="fb-map-panel"' in family_board, "family board tabs are missing")
require('button.addEventListener("click"' in family_map and "fb-map-panel" in family_map, "family board tab interaction is missing")
for page_name, page in (("home", home), ("media", media), ("generations", generations), ("events", events)):
    for tag in re.findall(r"<input[^>]*type=[\\\"']password[\\\"'][^>]*>", page, re.I):
        require("value=" not in tag.lower(), page_name + " password input must be empty by default")
        require('autocomplete="off"' in tag.lower(), page_name + " password input must not request browser autofill")
require("node --check assets/js/media-atmosphere.js" in workflow, "atmosphere JavaScript syntax is not checked")
require("node --check assets/js/cloud-archive.js" in workflow, "archive JavaScript syntax is not checked")
require("python3 scripts/check_ai_media_lab.py" in workflow, "AI media contract checker is not in CI")
print("AI media lab and navigation contract passed.")
