#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import time
import tomllib
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "projects.json"
STATUS_URL = "https://api.github.com/repos/vessaxor-spec/vessaxor-spec/contents/profile/status.toml?ref=main"
REPOS = {
    "teo": "vessaxor-spec/The-ever-evolving-orchestration-",
    "grox": "vessaxor-spec/GroX",
}
TRANSIENT_HTTP = {429, 500, 502, 503, 504}
MAX_REQUEST_ATTEMPTS = 4

STATIC_BINDINGS: dict[Path, dict[str, tuple[str, ...]]] = {
    ROOT / "index.html": {
        "hero-teo-release": ("projects", "teo", "release"),
        "hero-teo-status": ("projects", "teo", "status"),
        "hero-grox-release": ("projects", "grox", "release"),
        "hero-grox-status": ("projects", "grox", "status"),
        "teo-release": ("projects", "teo", "release"),
        "teo-status": ("projects", "teo", "status"),
        "grox-release": ("projects", "grox", "release"),
        "grox-status": ("projects", "grox", "status"),
        "state-teo-release": ("projects", "teo", "release"),
        "state-teo-status": ("projects", "teo", "status"),
        "state-grox-release": ("projects", "grox", "release"),
        "state-grox-status": ("projects", "grox", "status"),
        "teo-focus": ("projects", "teo", "focus"),
        "grox-focus": ("projects", "grox", "focus"),
        "research-focus": ("research", "focus"),
    },
    ROOT / "teo" / "index.html": {
        "teo-release": ("projects", "teo", "release"),
        "teo-status": ("projects", "teo", "status"),
        "teo-focus": ("projects", "teo", "focus"),
    },
    ROOT / "grox" / "index.html": {
        "grox-release": ("projects", "grox", "release"),
        "grox-status": ("projects", "grox", "status"),
        "grox-focus": ("projects", "grox", "focus"),
    },
    ROOT / "evidence" / "index.html": {
        "state-teo-release": ("projects", "teo", "release"),
        "state-teo-status": ("projects", "teo", "status"),
        "state-grox-release": ("projects", "grox", "release"),
        "state-grox-status": ("projects", "grox", "status"),
    },
}


def request(url: str, *, accept: str = "application/vnd.github+json") -> bytes:
    headers = {
        "User-Agent": "vessaxor-pages-builder",
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(1, MAX_REQUEST_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=20
            ) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in TRANSIENT_HTTP or attempt == MAX_REQUEST_ATTEMPTS:
                raise
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt == MAX_REQUEST_ATTEMPTS:
                raise

        delay = min(2 ** (attempt - 1), 8)
        print(
            f"transient public-state request failure; retrying in {delay}s "
            f"(attempt {attempt}/{MAX_REQUEST_ATTEMPTS})"
        )
        time.sleep(delay)

    raise RuntimeError(f"public-state request failed after retries: {last_error}")


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


def nested_value(payload: dict[str, Any], path: tuple[str, ...]) -> str:
    value: Any = payload
    for key in path:
        if not isinstance(value, dict) or key not in value:
            raise RuntimeError(f"Missing public-state path: {'.'.join(path)}")
        value = value[key]
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"Public-state value must be a non-empty string: {'.'.join(path)}")
    return value


def replace_element_text(document: str, element_id: str, value: str) -> str:
    pattern = re.compile(
        rf'(<(?P<tag>[A-Za-z][\w:-]*)\b[^>]*\bid=["\']{re.escape(element_id)}["\'][^>]*>)(.*?)(</(?P=tag)>)',
        re.DOTALL,
    )
    replacement = html.escape(value, quote=False)
    updated, count = pattern.subn(
        lambda match: f"{match.group(1)}{replacement}{match.group(4)}",
        document,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"Expected exactly one element with id={element_id!r}")
    return updated


def sync_static_surfaces(payload: dict[str, Any], reviewed_at: date) -> None:
    for path, bindings in STATIC_BINDINGS.items():
        document = path.read_text(encoding="utf-8")
        updated = document
        for element_id, value_path in bindings.items():
            updated = replace_element_text(updated, element_id, nested_value(payload, value_path))

        if path == ROOT / "evidence" / "index.html":
            updated = replace_element_text(updated, "reviewed-at", f"reviewed {display_date(reviewed_at)}")

        if updated != document:
            path.write_text(updated, encoding="utf-8")
            print(f"synchronized {path.relative_to(ROOT)}")


def main() -> None:
    status = tomllib.loads(
        request(STATUS_URL, accept="application/vnd.github.raw+json").decode("utf-8")
    )
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
    sync_static_surfaces(payload, reviewed_at)


if __name__ == "__main__":
    main()
