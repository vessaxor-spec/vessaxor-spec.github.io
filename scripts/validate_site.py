#!/usr/bin/env python3
from __future__ import annotations

import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DATA = ROOT / "data" / "projects.json"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"
SITE_URL = "https://vessaxor-spec.github.io/"

EXPECTED_VISUALS = {
    "assets/visuals/vessaxor-hero.png": (2172, 724),
    "assets/visuals/teo-banner.png": (2172, 724),
    "assets/visuals/grox-banner.png": (2172, 724),
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    if len(payload) < 24 or payload[:8] != PNG_SIGNATURE or payload[12:16] != b"IHDR":
        raise RuntimeError(f"{path} is not a valid PNG")
    return struct.unpack(">II", payload[16:24])


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")

    required_fragments = [
        'id="systems"',
        'id="relation"',
        'id="state"',
        'id="work"',
        'id="principles"',
        "./assets/visuals/vessaxor-hero.png",
        "./assets/visuals/teo-banner.png",
        "./assets/visuals/grox-banner.png",
        '<meta name="robots" content="index,follow,max-image-preview:large" />',
        '<link rel="canonical" href="https://vessaxor-spec.github.io/" />',
        '<link rel="sitemap" type="application/xml" href="https://vessaxor-spec.github.io/sitemap.xml" />',
        '"@type": "WebSite"',
    ]
    for fragment in required_fragments:
        if fragment not in html:
            raise RuntimeError(f"index.html missing required fragment: {fragment}")

    forbidden_fragments = [
        "teo-social-preview-v2.webp",
        "grox-social-preview-v2.webp",
        "Loading current public focus",
    ]
    for fragment in forbidden_fragments:
        if fragment in html:
            raise RuntimeError(f"index.html still contains stale/degraded fragment: {fragment}")

    if not ROBOTS.exists():
        raise RuntimeError("missing robots.txt")
    robots = ROBOTS.read_text(encoding="utf-8")
    for fragment in (
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://vessaxor-spec.github.io/sitemap.xml",
    ):
        if fragment not in robots:
            raise RuntimeError(f"robots.txt missing required directive: {fragment}")

    if not SITEMAP.exists():
        raise RuntimeError("missing sitemap.xml")
    try:
        root = ET.parse(SITEMAP).getroot()
    except ET.ParseError as exc:
        raise RuntimeError(f"sitemap.xml is invalid XML: {exc}") from exc
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locations = [
        node.text.strip()
        for node in root.findall(f"{namespace}url/{namespace}loc")
        if node.text and node.text.strip()
    ]
    if SITE_URL not in locations:
        raise RuntimeError(f"sitemap.xml missing canonical homepage URL: {SITE_URL}")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    for key in ("teo", "grox"):
        project = data["projects"][key]
        for field in ("release", "status", "focus"):
            if not isinstance(project.get(field), str) or not project[field].strip():
                raise RuntimeError(f"projects.json missing projects.{key}.{field}")

    for relative, expected in EXPECTED_VISUALS.items():
        path = ROOT / relative
        if not path.exists():
            raise RuntimeError(f"missing synchronized visual: {relative}")
        actual = png_dimensions(path)
        if actual != expected:
            raise RuntimeError(f"{relative} dimensions {actual} do not match {expected}")

    print("site validation passed")


if __name__ == "__main__":
    main()
