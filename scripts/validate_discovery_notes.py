#!/usr/bin/env python3
from __future__ import annotations

import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes" / "index.html"
EVIDENCE = ROOT / "evidence" / "index.html"
SITEMAP = ROOT / "sitemap.xml"
NOTES_URL = "https://vessaxor-spec.github.io/notes/"


class NotesParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.headings: list[int] = []
        self.h1_count = 0
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(str(attributes["id"]))
        if tag == "a" and attributes.get("href"):
            self.links.append(str(attributes["href"]))
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.headings.append(level)
            if level == 1:
                self.h1_count += 1


def main() -> None:
    if not NOTES.exists():
        raise RuntimeError("missing notes/index.html")

    html = NOTES.read_text(encoding="utf-8")
    parser = NotesParser()
    parser.feed(html)

    if parser.h1_count != 1:
        raise RuntimeError(f"notes/index.html must contain exactly one h1, found {parser.h1_count}")
    duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicates:
        raise RuntimeError(f"notes/index.html duplicate ids: {duplicates}")
    for previous, current in zip(parser.headings, parser.headings[1:]):
        if current > previous + 1:
            raise RuntimeError(f"notes/index.html heading jump from h{previous} to h{current}")

    required_fragments = [
        '<meta name="robots" content="index,follow,max-image-preview:large" />',
        f'<link rel="canonical" href="{NOTES_URL}" />',
        '"@type": "TechArticle"',
        '<title>Governed AI Architecture Notes — VESSAXOR</title>',
        'id="persistent-ai"',
        'id="governed-orchestration"',
        'id="bounded-execution"',
        'id="evidence-bearing"',
        'id="boundaries"',
        'id="sources"',
        'persistent AI systems',
        'GOVERNED AI ORCHESTRATION',
        'BOUNDED AI EXECUTION',
        'EVIDENCE-BEARING EXECUTION',
    ]
    for fragment in required_fragments:
        if fragment not in html:
            raise RuntimeError(f"notes/index.html missing required discovery fragment: {fragment}")

    required_links = {
        "/teo/",
        "/grox/",
        "/evidence/",
        "https://github.com/vessaxor-spec/The-ever-evolving-orchestration-",
        "https://github.com/vessaxor-spec/GroX",
    }
    missing_links = sorted(required_links - set(parser.links))
    if missing_links:
        raise RuntimeError(f"notes/index.html missing primary links: {missing_links}")

    evidence = EVIDENCE.read_text(encoding="utf-8")
    if 'href="/notes/"' not in evidence:
        raise RuntimeError("evidence/index.html must link to /notes/")

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    root = ET.parse(SITEMAP).getroot()
    locations = {
        node.text.strip()
        for node in root.findall(f"{namespace}url/{namespace}loc")
        if node.text and node.text.strip()
    }
    if NOTES_URL not in locations:
        raise RuntimeError("sitemap.xml missing technical notes URL")

    print("technical notes discovery validation passed")


if __name__ == "__main__":
    main()
