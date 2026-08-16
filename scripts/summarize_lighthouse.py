#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

INPUTS = {
    "mobile": Path("lighthouse-mobile.json"),
    "desktop": Path("lighthouse-desktop.json"),
}
OUTPUT = Path("lighthouse-summary.json")


def score(categories: dict, key: str) -> int | None:
    value = categories.get(key, {}).get("score")
    if isinstance(value, (int, float)):
        return round(value * 100)
    return None


def numeric(audits: dict, key: str, divisor: float = 1.0) -> float | None:
    value = audits.get(key, {}).get("numericValue")
    if isinstance(value, (int, float)):
        return round(value / divisor, 3)
    return None


def summarize(path: Path, strategy: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    categories = payload.get("categories") or {}
    audits = payload.get("audits") or {}
    config = payload.get("configSettings") or {}
    return {
        "strategy": strategy,
        "requested_url": payload.get("requestedUrl"),
        "final_url": payload.get("finalDisplayedUrl") or payload.get("finalUrl"),
        "fetch_time": payload.get("fetchTime"),
        "lighthouse_version": payload.get("lighthouseVersion"),
        "form_factor": config.get("formFactor"),
        "throttling_method": config.get("throttlingMethod"),
        "scores": {
            "performance": score(categories, "performance"),
            "accessibility": score(categories, "accessibility"),
            "best_practices": score(categories, "best-practices"),
            "seo": score(categories, "seo"),
        },
        "lab": {
            "fcp_seconds": numeric(audits, "first-contentful-paint", 1000),
            "lcp_seconds": numeric(audits, "largest-contentful-paint", 1000),
            "speed_index_seconds": numeric(audits, "speed-index", 1000),
            "tbt_ms": numeric(audits, "total-blocking-time"),
            "cls": numeric(audits, "cumulative-layout-shift"),
        },
    }


def main() -> None:
    report = {
        "target": "https://vessaxor-spec.github.io/",
        "source": "Google Lighthouse 13.4.1 CLI",
        "field_data": {
            "available": False,
            "note": "Lighthouse is lab data. Real-user CrUX/Core Web Vitals field data is not inferred from this report.",
        },
        "results": [summarize(path, strategy) for strategy, path in INPUTS.items()],
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    for item in report["results"]:
        scores = item["scores"]
        lab = item["lab"]
        print(f"LIGHTHOUSE strategy={item['strategy']} version={item['lighthouse_version']}")
        print(
            "  scores "
            f"performance={scores['performance']} "
            f"accessibility={scores['accessibility']} "
            f"best_practices={scores['best_practices']} "
            f"seo={scores['seo']}"
        )
        print(
            "  lab "
            f"FCP={lab['fcp_seconds']}s "
            f"LCP={lab['lcp_seconds']}s "
            f"SpeedIndex={lab['speed_index_seconds']}s "
            f"TBT={lab['tbt_ms']}ms "
            f"CLS={lab['cls']}"
        )
    print("  CrUX field data: not supplied by Lighthouse; no real-user claim made")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
