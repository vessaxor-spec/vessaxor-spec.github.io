#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import struct
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISUAL_DIR = ROOT / "assets" / "visuals"

ASSETS = {
    "vessaxor-hero.png": {
        "url": "https://raw.githubusercontent.com/vessaxor-spec/vessaxor-spec/main/assets/banner/vessaxor-hero-banner.png",
        "dimensions": (2172, 724),
        "sha256": "2945c2d9db9cc3cee1685ac6b3c4e8e8ca6c9aacfbce7d4e1ca8b6b22a677798",
    },
    "teo-banner.png": {
        "url": "https://raw.githubusercontent.com/vessaxor-spec/The-ever-evolving-orchestration-/main/assets/banner/teo-banner-hd-optimized.png",
        "dimensions": (2172, 724),
        "sha256": "6839a4b87d42f0e86104688e931e42e2aac065278b3403bc4e968051628fb2e7",
    },
    "grox-banner.png": {
        "url": "https://raw.githubusercontent.com/vessaxor-spec/GroX/main/assets/banner/grox-banner-hd-optimized.png",
        "dimensions": (2172, 724),
        "sha256": "009a6f95c41ed1c20b2501cf8eff608da211563e846b842cd06995e9b94e0a05",
    },
}

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(payload: bytes) -> tuple[int, int]:
    if len(payload) < 24 or payload[:8] != PNG_SIGNATURE or payload[12:16] != b"IHDR":
        raise RuntimeError("asset is not a valid PNG with an IHDR header")
    return struct.unpack(">II", payload[16:24])


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "vessaxor-pages-visual-sync"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main() -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    for filename, spec in ASSETS.items():
        payload = fetch(spec["url"])
        dimensions = png_dimensions(payload)
        digest = hashlib.sha256(payload).hexdigest()
        if dimensions != spec["dimensions"]:
            raise RuntimeError(f"{filename} dimensions changed: {dimensions}, expected {spec['dimensions']}")
        if digest != spec["sha256"]:
            raise RuntimeError(f"{filename} digest changed: {digest}; explicit visual approval required")
        destination = VISUAL_DIR / filename
        with tempfile.NamedTemporaryFile(dir=VISUAL_DIR, delete=False) as handle:
            handle.write(payload)
            temporary = Path(handle.name)
        temporary.replace(destination)
        print(f"synced {filename}: {dimensions[0]}x{dimensions[1]}, sha256={digest}")


if __name__ == "__main__":
    main()
