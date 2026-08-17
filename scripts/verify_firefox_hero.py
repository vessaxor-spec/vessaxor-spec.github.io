#!/usr/bin/env python3
"""Cold-load the VESSAXOR hero in runner-provided Firefox via raw WebDriver.

No third-party Python package is required. GitHub's Ubuntu runner provides Firefox
and geckodriver; this script talks to geckodriver with Python's standard library.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def resolve_binary(name: str, env_name: str, fallbacks: list[str]) -> str:
    candidates: list[str] = []
    found = shutil.which(name)
    if found:
        candidates.append(found)
    env_value = os.environ.get(env_name)
    if env_value:
        env_path = Path(env_value)
        candidates.append(str(env_path / name) if env_path.is_dir() else str(env_path))
    candidates.extend(fallbacks)
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    raise RuntimeError(f"{name} not found; checked: {candidates}")


class WebDriver:
    def __init__(self, geckodriver: str, firefox: str) -> None:
        self.port = free_port()
        self.base = f"http://127.0.0.1:{self.port}"
        self.process = subprocess.Popen(
            [geckodriver, "--host", "127.0.0.1", "--port", str(self.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.firefox = firefox
        self.session_id: str | None = None
        self._wait_ready()

    def _request(self, method: str, path: str, payload: dict | None = None, timeout: float = 30.0):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base + path,
            data=body,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"WebDriver {method} {path} failed: HTTP {error.code}: {detail}") from error

    def _wait_ready(self) -> None:
        deadline = time.monotonic() + 15.0
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                output = self.process.stdout.read() if self.process.stdout else ""
                raise RuntimeError(f"geckodriver exited early ({self.process.returncode}): {output}")
            try:
                status = self._request("GET", "/status", timeout=1.0)
                if status.get("value", {}).get("ready") is True:
                    return
            except Exception as error:  # bounded startup polling
                last_error = error
            time.sleep(0.1)
        raise RuntimeError(f"geckodriver did not become ready: {last_error}")

    def new_session(self) -> dict:
        response = self._request(
            "POST",
            "/session",
            {
                "capabilities": {
                    "alwaysMatch": {
                        "browserName": "firefox",
                        "acceptInsecureCerts": False,
                        "moz:firefoxOptions": {
                            "binary": self.firefox,
                            "args": ["-headless"],
                            "prefs": {
                                "browser.shell.checkDefaultBrowser": False,
                                "browser.startup.page": 0,
                            },
                        },
                    }
                }
            },
            timeout=45.0,
        )
        value = response.get("value", {})
        self.session_id = value.get("sessionId")
        if not self.session_id:
            raise RuntimeError(f"Firefox session did not return a session id: {response}")
        return value.get("capabilities", {})

    def close_session(self) -> None:
        if not self.session_id:
            return
        session = self.session_id
        self.session_id = None
        try:
            self._request("DELETE", f"/session/{session}", timeout=15.0)
        except Exception as error:
            print(f"warning: Firefox session cleanup failed: {error}", file=sys.stderr)

    def stop(self) -> None:
        self.close_session()
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5.0)

    def _session_request(self, method: str, suffix: str, payload: dict | None = None, timeout: float = 30.0):
        if not self.session_id:
            raise RuntimeError("Firefox session is not active")
        return self._request(method, f"/session/{self.session_id}{suffix}", payload, timeout)

    def set_window(self, width: int, height: int) -> None:
        self._session_request("POST", "/window/rect", {"width": width, "height": height})

    def navigate(self, url: str) -> None:
        self._session_request("POST", "/url", {"url": url}, timeout=45.0)

    def execute(self, script: str):
        response = self._session_request("POST", "/execute/sync", {"script": script, "args": []})
        return response.get("value")


INSPECT_SCRIPT = r"""
const frame = document.querySelector('.hero-art[data-reliable-media]');
const image = frame?.querySelector('img');
const fallback = frame?.querySelector('.media-fallback');
const fallbackStyle = fallback ? getComputedStyle(fallback) : null;
const rect = fallback?.getBoundingClientRect();
return {
  readyState: document.readyState,
  hasMain: document.querySelector('#main') !== null,
  hasFrame: Boolean(frame),
  hasImage: Boolean(image),
  state: frame?.dataset.mediaState || null,
  complete: image?.complete || false,
  naturalWidth: image?.naturalWidth || 0,
  naturalHeight: image?.naturalHeight || 0,
  currentSrc: image?.currentSrc || image?.src || null,
  fallbackOpacity: fallbackStyle?.opacity || null,
  fallbackWidth: rect?.width || 0,
  fallbackHeight: rect?.height || 0
};
"""


def with_probe(url: str, iteration: int, width: int) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.extend([("r06_firefox", str(iteration)), ("viewport", str(width))])
    return urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(query)))


def inspect_until_settled(driver: WebDriver, timeout: float = 12.0) -> dict:
    deadline = time.monotonic() + timeout
    last: dict = {}
    while time.monotonic() < deadline:
        value = driver.execute(INSPECT_SCRIPT)
        if isinstance(value, dict):
            last = value
            if (
                value.get("readyState") == "complete"
                and value.get("hasMain")
                and value.get("hasFrame")
                and value.get("hasImage")
                and (value.get("state") in {"loaded", "failed"} or int(value.get("naturalWidth") or 0) > 0)
            ):
                time.sleep(0.25)
                refreshed = driver.execute(INSPECT_SCRIPT)
                return refreshed if isinstance(refreshed, dict) else last
        time.sleep(0.1)
    return last


def run_probe(driver: WebDriver, base_url: str, iteration: int, width: int, height: int) -> dict:
    capabilities = driver.new_session()
    browser_name = str(capabilities.get("browserName", "")).lower()
    if browser_name != "firefox":
        raise RuntimeError(f"Expected Firefox session, got capabilities: {capabilities}")
    try:
        driver.set_window(width, height)
        target = with_probe(base_url, iteration, width)
        driver.navigate(target)
        verdict = inspect_until_settled(driver)
        verdict["browserVersion"] = capabilities.get("browserVersion")
        verdict["platformName"] = capabilities.get("platformName")
        verdict["viewport"] = f"{width}x{height}"
        verdict["iteration"] = iteration
        verdict["target"] = target
        if not verdict.get("hasFrame") or not verdict.get("hasImage"):
            raise RuntimeError(f"Firefox hero reliability markup missing: {json.dumps(verdict, sort_keys=True)}")
        if verdict.get("state") == "failed" or int(verdict.get("naturalWidth") or 0) <= 0:
            raise RuntimeError(
                "Firefox reproduced a hero media-load failure. "
                f"Fail-visible state: {json.dumps(verdict, sort_keys=True)}"
            )
        if verdict.get("state") != "loaded":
            raise RuntimeError(f"Firefox hero did not settle to loaded state: {json.dumps(verdict, sort_keys=True)}")
        return verdict
    finally:
        driver.close_session()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/")
    parser.add_argument("--iterations", type=int, default=8)
    args = parser.parse_args()
    if args.iterations < 2:
        parser.error("--iterations must be at least 2 so both desktop and mobile are exercised")

    geckodriver = resolve_binary(
        "geckodriver",
        "GECKOWEBDRIVER",
        ["/usr/local/bin/geckodriver", "/usr/local/share/gecko_driver/geckodriver"],
    )
    firefox = resolve_binary("firefox", "FIREFOX_BIN", ["/usr/bin/firefox", "/usr/local/bin/firefox"])
    driver = WebDriver(geckodriver, firefox)
    viewports = [(1440, 1000), (390, 844)]
    results: list[dict] = []
    try:
        for index in range(args.iterations):
            width, height = viewports[index % len(viewports)]
            verdict = run_probe(driver, args.base_url, index + 1, width, height)
            results.append(verdict)
            print(
                "firefox cold-load passed "
                f"iteration={index + 1}/{args.iterations} viewport={verdict['viewport']} "
                f"browser={verdict.get('browserVersion')} width={verdict.get('naturalWidth')} "
                f"state={verdict.get('state')} src={verdict.get('currentSrc')}"
            )
    finally:
        driver.stop()

    versions = sorted({str(result.get("browserVersion")) for result in results})
    print(
        f"Firefox R06 bounded reproduction matrix passed: {len(results)} cold sessions, "
        f"desktop/mobile alternated, browser versions={versions}. No hero media failure reproduced."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
