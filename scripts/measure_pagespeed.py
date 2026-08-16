#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TARGET_URL = "https://vessaxor-spec.github.io/"
API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
OUTPUT = Path("pagespeed-report.json")
STRATEGIES = ("mobile", "desktop")
CATEGORIES = ("performance", "accessibility", "best-practices", "seo")


def request_pagespeed(strategy: str) -> dict:
    params = [
        ("url", TARGET_URL),
        ("strategy", strategy),
    ]
    params.extend(("category", category) for category in CATEGORIES)
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "vessaxor-pagespeed-evidence/1.0",
    }

    last_error: Exception | None = None
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 3:
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"PageSpeed API HTTP {exc.code}: {body[:1000]}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == 3:
                raise RuntimeError(f"PageSpeed API request failed: {exc}") from exc
        time.sleep(2 ** attempt)
    raise RuntimeError(f"PageSpeed API request failed: {last_error}")


def audit_numeric(audits: dict, key: str, divisor: float = 1.0) -> float | None:
    value = audits.get(key, {}).get("numericValue")
    if isinstance(value, (int, float)):
        return round(value / divisor, 3)
    return None


def category_score(categories: dict, key: str) -> int | None:
    score = categories.get(key, {}).get("score")
    if isinstance(score, (int, float)):
        return round(score * 100)
    return None


def field_summary(experience: dict | None) -> dict:
    if not isinstance(experience, dict):
        return {"available": False}
    metrics = experience.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        return {"available": False}

    result: dict[str, object] = {
        "available": True,
        "overall_category": experience.get("overall_category"),
    }
    for key in ("LARGEST_CONTENTFUL_PAINT_MS", "INTERACTION_TO_NEXT_PAINT", "CUMULATIVE_LAYOUT_SHIFT_SCORE"):
        metric = metrics.get(key)
        if not isinstance(metric, dict):
            continue
        item: dict[str, object] = {"category": metric.get("category")}
        percentile = metric.get("percentile")
        if isinstance(percentile, (int, float)):
            if key == "LARGEST_CONTENTFUL_PAINT_MS":
                item["p75_seconds"] = round(percentile / 1000, 3)
            elif key == "CUMULATIVE_LAYOUT_SHIFT_SCORE":
                item["p75"] = round(percentile / 100, 3)
            else:
                item["p75_ms"] = round(percentile, 1)
        result[key] = item
    return result


def summarize(payload: dict, strategy: str) -> dict:
    lighthouse = payload.get("lighthouseResult") or {}
    categories = lighthouse.get("categories") or {}
    audits = lighthouse.get("audits") or {}

    return {
        "strategy": strategy,
        "tested_url": payload.get("id") or TARGET_URL,
        "fetch_time": lighthouse.get("fetchTime"),
        "lighthouse_version": lighthouse.get("lighthouseVersion"),
        "scores": {
            "performance": category_score(categories, "performance"),
            "accessibility": category_score(categories, "accessibility"),
            "best_practices": category_score(categories, "best-practices"),
            "seo": category_score(categories, "seo"),
        },
        "lab": {
            "fcp_seconds": audit_numeric(audits, "first-contentful-paint", 1000),
            "lcp_seconds": audit_numeric(audits, "largest-contentful-paint", 1000),
            "speed_index_seconds": audit_numeric(audits, "speed-index", 1000),
            "tbt_ms": audit_numeric(audits, "total-blocking-time"),
            "cls": audit_numeric(audits, "cumulative-layout-shift"),
        },
        "field_url": field_summary(payload.get("loadingExperience")),
        "field_origin": field_summary(payload.get("originLoadingExperience")),
    }


def print_summary(item: dict) -> None:
    scores = item["scores"]
    lab = item["lab"]
    print(f"PAGESPEED strategy={item['strategy']}")
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
    print(f"  CrUX URL field data available={item['field_url']['available']}")
    print(f"  CrUX origin field data available={item['field_origin']['available']}")


def main() -> None:
    report = {
        "target": TARGET_URL,
        "source": "Google PageSpeed Insights API v5",
        "results": [],
    }
    for strategy in STRATEGIES:
        payload = request_pagespeed(strategy)
        item = summarize(payload, strategy)
        report["results"].append(item)
        print_summary(item)

    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
