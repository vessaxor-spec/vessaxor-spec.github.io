#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://vessaxor-spec.github.io/"
TARGETS = {
    "": ("text/html", b"Architecture above models."),
    "teo/": ("text/html", b"Who should do the work?"),
    "grox/": ("text/html", b"How does intent become durable action?"),
    "evidence/": ("text/html", b"Show what the claim rests on."),
    "assets/visuals/vessaxor-hero-720.webp": ("image/webp", None),
    "assets/visuals/vessaxor-hero-1200.webp": ("image/webp", None),
    "assets/visuals/vessaxor-hero-1800.webp": ("image/webp", None),
    "assets/visuals/vessaxor-hero.png": ("image/png", None),
    "assets/visuals/teo-banner-1200.webp": ("image/webp", None),
    "assets/visuals/grox-banner-1200.webp": ("image/webp", None),
}


def fetch(url: str) -> tuple[str, bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "vessaxor-production-smoke/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        content_type = response.headers.get_content_type()
        payload = response.read()
        return content_type, payload


def verify_once(base_url: str) -> list[str]:
    failures: list[str] = []
    for relative, (expected_type, marker) in TARGETS.items():
        url = urllib.parse.urljoin(base_url, relative)
        try:
            content_type, payload = fetch(url)
        except (urllib.error.URLError, TimeoutError) as exc:
            failures.append(f"{url}: request failed: {exc}")
            continue
        if content_type != expected_type:
            failures.append(f"{url}: content type {content_type!r}, expected {expected_type!r}")
        minimum = 500 if expected_type == "text/html" else 2000
        if len(payload) < minimum:
            failures.append(f"{url}: payload only {len(payload)} bytes, expected >= {minimum}")
        if marker and marker not in payload:
            failures.append(f"{url}: expected page marker missing")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the deployed VESSAXOR Pages surface.")
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    parser.add_argument("--attempts", type=int, default=8)
    parser.add_argument("--delay", type=float, default=5.0)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/") + "/"
    last_failures: list[str] = []
    for attempt in range(1, args.attempts + 1):
        last_failures = verify_once(base_url)
        if not last_failures:
            print(f"production smoke passed on attempt {attempt}: {base_url}")
            return
        print(f"production smoke attempt {attempt}/{args.attempts} failed:")
        for failure in last_failures:
            print(f"- {failure}")
        if attempt < args.attempts:
            time.sleep(args.delay)

    raise SystemExit("production smoke failed after bounded retries")


if __name__ == "__main__":
    main()
