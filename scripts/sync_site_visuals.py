#!/usr/bin/env python3
from __future__ import annotations

import struct
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISUAL_DIR = ROOT / "assets" / "visuals"

ASSETS = {
    "vessaxor-hero.png": (
        "https://raw.githubusercontent.com/vessaxor-spec/vessaxor-spec/main/assets/banner/vessaxor-hero-banner.png",
        (2172, 724),
    ),
    "teo-banner.png": (
        "https://raw.githubusercontent.com/vessaxor-spec/The-ever-evolving-orchestration-/main/assets/banner/teo-banner-hd-optimized.png",
        (2172, 724),
    ),
    "grox-banner.png": (
        "https://raw.githubusercontent.com/vessaxor-spec/GroX/main/assets/banner/grox-banner-hd-optimized.png",
        (2172, 724),
    ),
}

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(payload: bytes) -> tuple[int, int]:
    if len(payload) < 24 or payload[:8] != PNG_SIGNATURE or payload[12:16] != b"IHDR":
        raise RuntimeError("asset is not a valid PNG with an IHDR header")
    width, height = struct.unpack(">II", payload[16:24])
    return width, height


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "vessaxor-pages-visual-sync"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main() -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)

    for filename, (url, expected_dimensions) in ASSETS.items():
        payload = fetch(url)
        dimensions = png_dimensions(payload)

        if dimensions != expected_dimensions:
            raise RuntimeError(
                f"{filename} dimensions changed: {dimensions}, expected {expected_dimensions}"
            )
        if len(payload) < 900_000:
            raise RuntimeError(
                f"{filename} is unexpectedly small ({len(payload)} bytes); refusing possible degraded asset"
            )

        destination = VISUAL_DIR / filename
        with tempfile.NamedTemporaryFile(dir=VISUAL_DIR, delete=False) as handle:
            handle.write(payload)
            temporary = Path(handle.name)
        temporary.replace(destination)
        print(f"synced {filename}: {dimensions[0]}x{dimensions[1]}, {len(payload)} bytes")


if __name__ == "__main__":
    main()
