from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASEURL = "/-ArtBukaBot-"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.anchors: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("href", "src"):
            value = values.get(key)
            if value:
                self.links.append(value)
        anchor = values.get("id") or values.get("name")
        if anchor:
            self.anchors.add(anchor)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    if not root.is_dir():
        print(f"ERROR: site directory does not exist: {root}")
        return 1

    pages = sorted(root.rglob("*.html"))
    if not pages:
        print("ERROR: Jekyll output contains no HTML pages")
        return 1

    known_anchors: dict[Path, set[str]] = {}
    parsed: dict[Path, PageParser] = {}
    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page] = parser
        known_anchors[page] = parser.anchors

    errors: list[str] = []
    checked = 0
    for page, parser in parsed.items():
        for raw in parser.links:
            parts = urlsplit(raw)
            if parts.scheme or parts.netloc or raw.startswith(("mailto:", "tel:", "data:", "javascript:")):
                continue

            path_text = unquote(parts.path)
            if not path_text:
                target = page
            else:
                if path_text == BASEURL:
                    path_text = "/"
                elif path_text.startswith(BASEURL + "/"):
                    path_text = path_text[len(BASEURL):]
                elif path_text.startswith("/"):
                    errors.append(f"{page.relative_to(root)}: local URL missing Pages baseurl: {raw}")
                    continue
                target = (root / path_text.lstrip("/")).resolve()

            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                errors.append(f"{page.relative_to(root)}: missing target for {raw}")
                continue
            checked += 1

            if parts.fragment:
                fragment = unquote(parts.fragment)
                if target.suffix.lower() == ".html":
                    if target not in known_anchors:
                        anchor_parser = PageParser()
                        anchor_parser.feed(target.read_text(encoding="utf-8"))
                        known_anchors[target] = anchor_parser.anchors
                    if fragment not in known_anchors[target]:
                        errors.append(f"{page.relative_to(root)}: missing anchor #{fragment} in {target.relative_to(root)}")

    if errors:
        print("GitHub Pages link check failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"GitHub Pages link check passed: {len(pages)} HTML pages, {checked} local links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
