from pathlib import Path

root = Path(__file__).resolve().parents[1]
page = (root / "media.md").read_text(encoding="utf-8")
client = (root / "assets/js/supabase-archive.js").read_text(encoding="utf-8")
schema = (root / "backend/supabase/001_private_media_archive.sql").read_text(encoding="utf-8")
layout = (root / "_layouts/default.html").read_text(encoding="utf-8")

required_page = (
    'id="supabase-connect-form"', 'id="supabase-project-url"',
    'id="supabase-anon-key"', 'id="cloud-login-form"',
    'id="cloud-upload-form"', 'id="archive-storage"',
    'id="archive-upload"', 'id="archive-catalog"',
)
for token in required_page:
    assert token in page, f"Missing archive page control: {token}"

for token in (
    '/auth/v1/token?grant_type=password',
    '/storage/v1/object/',
    '/rest/v1/archive_items',
    'crypto.subtle.digest',
    'x-upsert',
    'accessToken = result.access_token',
    'storageUploaded',
    'MATERIAL-ID',
):
    assert token in client or token in page, f"Missing Supabase client contract: {token}"

assert "service_role" in page.lower()
assert "localStorage" not in client and "sessionStorage" not in client
assert "public = false" in schema
assert "enable row level security" in schema.lower()
assert "auth.uid()" in schema
assert "for insert to authenticated" in schema.lower()
assert "for select to authenticated" in schema.lower()
assert "sha256" in schema.lower()
assert "original_material_id" in schema
assert "supabase-archive.js" in page
assert "/media/" in layout and "География" in layout
assert "ezenhancer.ai" not in client.lower()
print("Supabase private archive contract passed.")
