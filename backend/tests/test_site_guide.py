from pathlib import Path
def test_site_guide_is_included_and_has_accessible_contextual_controls():
    root=Path(__file__).resolve().parents[2]
    layout=(root/"_layouts"/"default.html").read_text(encoding="utf-8")
    script=(root/"assets"/"js"/"site-guide.js").read_text(encoding="utf-8")
    assert 'id="site-guide"' in layout
    assert 'data-guide-toggle' in layout and 'data-guide-panel' in layout
    assert 'aria-expanded="false"' in layout
    assert "site-guide-tooltip" in layout
    assert 'media:{title:' in script and 'account:{title:' in script and 'status:{title:' in script
    assert "window.sessionStorage" in script
