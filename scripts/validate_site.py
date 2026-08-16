#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import struct
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
DATA = ROOT / "data" / "projects.json"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"
SITE_URL = "https://vessaxor-spec.github.io/"

EXPECTED_PNGS = {
    "assets/visuals/vessaxor-hero.png": (2172, 724),
    "assets/visuals/teo-banner.png": (2172, 724),
    "assets/visuals/grox-banner.png": (2172, 724),
    "assets/visuals/vessaxor-social-preview.png": (1200, 630),
}
EXPECTED_WEBPS = {
    "assets/visuals/vessaxor-hero-720.webp": (720, 240),
    "assets/visuals/vessaxor-hero-1200.webp": (1200, 400),
    "assets/visuals/vessaxor-hero-1800.webp": (1800, 600),
    "assets/visuals/teo-banner-720.webp": (720, 240),
    "assets/visuals/teo-banner-1200.webp": (1200, 400),
    "assets/visuals/teo-banner-1800.webp": (1800, 600),
    "assets/visuals/grox-banner-720.webp": (720, 240),
    "assets/visuals/grox-banner-1200.webp": (1200, 400),
    "assets/visuals/grox-banner-1800.webp": (1800, 600),
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    if len(payload) < 24 or payload[:8] != PNG_SIGNATURE or payload[12:16] != b"IHDR":
        raise RuntimeError(f"{path} is not a valid PNG")
    return struct.unpack(">II", payload[16:24])


def webp_dimensions(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    if len(payload) < 30 or payload[:4] != b"RIFF" or payload[8:12] != b"WEBP":
        raise RuntimeError(f"{path} is not a valid WebP")
    chunk = payload[12:16]
    if chunk == b"VP8 ":
        if payload[23:26] != b"\x9d\x01\x2a":
            raise RuntimeError(f"{path} has an invalid VP8 frame header")
        width = int.from_bytes(payload[26:28], "little") & 0x3FFF
        height = int.from_bytes(payload[28:30], "little") & 0x3FFF
        return width, height
    raise RuntimeError(f"{path} uses unsupported WebP chunk {chunk!r}")


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.internal_links: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.headings: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(str(attributes["id"]))
        href = attributes.get("href")
        if tag == "a" and href and href.startswith("#") and len(href) > 1:
            self.internal_links.append(href[1:])
        if tag == "img":
            self.images.append(attributes)
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1]))


def validate_html(html: str) -> None:
    parser = AuditParser()
    parser.feed(html)
    duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    if duplicates:
        raise RuntimeError(f"duplicate HTML ids: {duplicates}")
    missing_targets = sorted(set(parser.internal_links) - set(parser.ids))
    if missing_targets:
        raise RuntimeError(f"broken internal anchors: {missing_targets}")
    for image in parser.images:
        alt = image.get("alt")
        if alt is None or not alt.strip():
            raise RuntimeError(f"image missing non-empty alt text: {image.get('src')}")
    for previous, current in zip(parser.headings, parser.headings[1:]):
        if current > previous + 1:
            raise RuntimeError(f"heading level jumps from h{previous} to h{current}")


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    validate_html(html)

    required_fragments = [
        'id="systems"', 'id="relation"', 'id="state"', 'id="work"', 'id="principles"', 'id="source"',
        'fetchpriority="high"', 'type="image/webp"', 'srcset=',
        '<meta name="robots" content="index,follow,max-image-preview:large" />',
        '<link rel="canonical" href="https://vessaxor-spec.github.io/" />',
        '<link rel="sitemap" type="application/xml" href="https://vessaxor-spec.github.io/sitemap.xml" />',
        'vessaxor-social-preview.png', 'vessaxor-favicon.svg', '"@type": "WebSite"',
        '<title>VESSAXOR — Persistent AI Systems & Orchestration</title>',
    ]
    for fragment in required_fragments:
        if fragment not in html:
            raise RuntimeError(f"index.html missing required fragment: {fragment}")

    forbidden_fragments = ["teo-social-preview-v2.webp", "grox-social-preview-v2.webp", "principles-grid", "Loading current public focus"]
    for fragment in forbidden_fragments:
        if fragment in html:
            raise RuntimeError(f"index.html still contains stale/degraded fragment: {fragment}")

    if ":focus-visible" not in css:
        raise RuntimeError("styles.css missing explicit focus-visible treatment")
    if "min-height: 44px" not in css:
        raise RuntimeError("styles.css missing 44px interactive target floor")
    if "--faint: #78818b" not in css:
        raise RuntimeError("styles.css missing approved accessible faint-text token")

    tiny_rem = []
    for match in re.finditer(r"font-size:\s*([0-9]*\.?[0-9]+)rem", css):
        value = float(match.group(1))
        if value < 0.70:
            tiny_rem.append(value)
    if tiny_rem:
        raise RuntimeError(f"styles.css contains sub-0.70rem font sizes: {tiny_rem}")

    favicon = ROOT / "assets" / "visuals" / "vessaxor-favicon.svg"
    if not favicon.exists() or "<svg" not in favicon.read_text(encoding="utf-8"):
        raise RuntimeError("missing or invalid VESSAXOR SVG favicon")

    if not ROBOTS.exists():
        raise RuntimeError("missing robots.txt")
    robots = ROBOTS.read_text(encoding="utf-8")
    for fragment in ("User-agent: *", "Allow: /", "Sitemap: https://vessaxor-spec.github.io/sitemap.xml"):
        if fragment not in robots:
            raise RuntimeError(f"robots.txt missing required directive: {fragment}")

    if not SITEMAP.exists():
        raise RuntimeError("missing sitemap.xml")
    try:
        root = ET.parse(SITEMAP).getroot()
    except ET.ParseError as exc:
        raise RuntimeError(f"sitemap.xml is invalid XML: {exc}") from exc
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locations = [node.text.strip() for node in root.findall(f"{namespace}url/{namespace}loc") if node.text and node.text.strip()]
    if SITE_URL not in locations:
        raise RuntimeError(f"sitemap.xml missing canonical homepage URL: {SITE_URL}")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    for key in ("teo", "grox"):
        project = data["projects"][key]
        for field in ("release", "status", "focus"):
            if not isinstance(project.get(field), str) or not project[field].strip():
                raise RuntimeError(f"projects.json missing projects.{key}.{field}")

    for relative, expected in EXPECTED_PNGS.items():
        path = ROOT / relative
        if not path.exists():
            raise RuntimeError(f"missing PNG visual: {relative}")
        actual = png_dimensions(path)
        if actual != expected:
            raise RuntimeError(f"{relative} dimensions {actual} do not match {expected}")

    for relative, expected in EXPECTED_WEBPS.items():
        path = ROOT / relative
        if not path.exists():
            raise RuntimeError(f"missing responsive WebP: {relative}")
        actual = webp_dimensions(path)
        if actual != expected:
            raise RuntimeError(f"{relative} dimensions {actual} do not match {expected}")

    print("site validation passed")


if __name__ == "__main__":
    main()
