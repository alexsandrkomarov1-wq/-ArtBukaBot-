from pathlib import Path

root = Path(__file__).resolve().parents[1]
page = (root / "media.md").read_text(encoding="utf-8")
script = (root / "assets/js/media-library.js").read_text(encoding="utf-8")
layout = (root / "_layouts/default.html").read_text(encoding="utf-8")

required_ids = [
    "media-file-input", "media-image", "media-video", "media-prev",
    "media-next", "media-slideshow", "media-fullscreen", "media-download",
    "media-list", "media-status",
]
for element_id in required_ids:
    assert f'id="{element_id}"' in page, f"Missing media UI element: {element_id}"
    assert f'byId("{element_id}")' in script or element_id == "media-file-input", f"Missing JS binding: {element_id}"

assert "URL.createObjectURL" in script
assert "URL.revokeObjectURL" in script
assert "video.load()" in script
assert "requestFullscreen()" in script
assert "setInterval" in script
assert "Этот режим не загружает их в архив" in page
assert 'for="media-file-input"' in page
assert 'id="archive-catalog"' in page and 'id="archive-storage"' in page
assert 'id="supabase-connect-form"' in page and 'id="cloud-upload-form"' in page
assert "supabase-archive.js" in page
assert "не загружены на сервер" in script
assert "/media/" in layout and "Архив фото и видео" in layout
print("Media viewer contract checks passed.")
