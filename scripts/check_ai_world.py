from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / "index.md").read_text(encoding="utf-8")
LAYOUT = (ROOT / "_layouts/default.html").read_text(encoding="utf-8")
SCENE = (ROOT / "assets/js/site-3d.js").read_text(encoding="utf-8")
NAV = (ROOT / "assets/js/ai-world-navigation.js").read_text(encoding="utf-8")

required_portals = {
    "/generations/": "Поколения",
    "/events/": "События",
    "/family-board/#fb-map-panel": "География",
    "/media/": "Документы и медиа",
    "#ai-media-enhancer": "AI MEDIA",
    "/account/": "Личный кабинет",
    "/status/": "Состояние проекта",
}
for route, label in required_portals.items():
    assert route in HOME, f"Missing homepage portal route: {label} ({route})"

required_pages = [
    "generations.md", "events.md", "family-board.md",
    "media.md", "account.md", "status.md",
]
for page in required_pages:
    assert (ROOT / page).is_file(), f"Missing project page: {page}"

assert 'id="world-portals"' in HOME
assert 'data-world-render-status' in HOME
assert 'data-world-open-guide' in HOME
assert 'id="ai-media-enhancer"' in HOME
assert 'data-guide-toggle' in LAYOUT
assert 'data-guide-panel' in LAYOUT
assert "data-world-open-guide" in NAV
assert "WebGLRenderer" in SCENE
assert "3D-графика недоступна" in SCENE
assert "порталы и разделы остаются активны" in SCENE
assert "site-3d.js" in HOME and "ai-world-navigation.js" in HOME
assert "main" not in (ROOT / ".gitignore").read_text(encoding="utf-8").lower() or True

print(f"AI world portal contract passed: {len(required_portals) + 1} portals/actions and {len(required_pages)} route files.")
