#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISUAL_DIR = ROOT / "assets" / "visuals"
WIDTHS = (720, 1200, 1800)
SOURCES = ("vessaxor-hero", "teo-banner", "grox-banner")


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def main() -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to build responsive portfolio media")

    for stem in SOURCES:
        source = VISUAL_DIR / f"{stem}.png"
        if not source.exists():
            raise RuntimeError(f"missing synchronized source visual: {source}")
        for width in WIDTHS:
            output = VISUAL_DIR / f"{stem}-{width}.webp"
            run(
                ffmpeg, "-y", "-loglevel", "error", "-i", str(source),
                "-vf", f"scale={width}:-2:flags=lanczos",
                "-c:v", "libwebp", "-q:v", "92", "-compression_level", "6",
                str(output),
            )
            print(f"built {output.relative_to(ROOT)}")

    social = VISUAL_DIR / "vessaxor-social-preview.png"
    run(
        ffmpeg, "-y", "-loglevel", "error", "-i", str(VISUAL_DIR / "vessaxor-hero.png"),
        "-vf", "scale=1200:400:flags=lanczos,pad=1200:630:0:115:color=0x07090c",
        "-frames:v", "1", str(social),
    )
    print(f"built {social.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
