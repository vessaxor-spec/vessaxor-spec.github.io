#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import tomllib
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "projects.json"
STATUS_URL = "https://raw.githubusercontent.com/vessaxor-spec/vessaxor-spec/main/profile/status.toml"
REPOS = {
    "teo": "vessaxor-spec/The-ever-evolving-orchestration-",
    "grox": "vessaxor-spec/GroX",
}


def request(url: str) -> bytes:
    headers = {"User-Agent": "vessaxor-pages-builder", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as response:
        return response.read()


def latest_release(repository: str) -> str:
    payload = json.loads(request(f"https://api.github.com/repos/{repository}/releases/latest"))
    tag = payload.get("tag_name")
    if not isinstance(tag, str) or not tag:
        raise RuntimeError(f"No latest release tag for {repository}")
    return tag


def display_date(value: date) -> str:
    return value.strftime("%d %b %Y").lstrip("0")


def validate_freshness(status: dict) -> date:
    profile = status["profile"]
    reviewed_at = profile["reviewed_at"]
    if not isinstance(reviewed_at, date):
        reviewed_at = date.fromisoformat(str(reviewed_at))

    max_age_days = int(profile.get("max_age_days", 45))
    today = datetime.now(timezone.utc).date()
    delta = (today - reviewed_at).days

    # A one-day future value is permitted for the Bratislava/UTC date boundary.
    if delta < -1:
        raise RuntimeError("profile.reviewed_at is unexpectedly in the future")
    if delta > max_age_days:
        raise RuntimeError(
            f"Curated profile state is stale: reviewed {delta} days ago, limit is {max_age_days}"
        )
    return reviewed_at


def main() -> None:
    status = tomllib.loads(request(STATUS_URL).decode("utf-8"))
    reviewed_at = validate_freshness(status)

    for key, repository in REPOS.items():
        configured = status["projects"][key]["repository"]
        if configured != repository:
            raise RuntimeError(f"Unexpected repository configured for {key}: {configured}")

    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "profile": {"reviewed_at": display_date(reviewed_at)},
        "projects": {
            "teo": {
                "release": latest_release(REPOS["teo"]),
                "status": status["projects"]["teo"]["status"],
                "focus": status["projects"]["teo"]["focus"],
            },
            "grox": {
                "release": latest_release(REPOS["grox"]),
                "status": status["projects"]["grox"]["status"],
                "focus": status["projects"]["grox"]["focus"],
            },
        },
        "research": {"focus": status["research"]["focus"]},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
