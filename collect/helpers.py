"""Shared helpers: polite fetching, request log, snapshots, privacy filter, saving."""

import hashlib
import os
import re
import shutil
import time
import urllib.robotparser
from datetime import datetime, timezone
from urllib.parse import urlparse

import pandas as pd
import requests

import settings

OUTPUT_DIR = settings.OUTPUT_DIR
REQUEST_LOG = []
_robots_cache = {}

session = requests.Session()
session.headers.update({"User-Agent": settings.USER_AGENT})


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_allowed_by_robots(url):
    """Check the site's robots.txt (downloaded once per site)."""
    parts = urlparse(url)
    site = f"{parts.scheme}://{parts.netloc}"

    if site not in _robots_cache:
        parser = urllib.robotparser.RobotFileParser()
        try:
            response = session.get(site + "/robots.txt", timeout=settings.TIMEOUT_SECONDS)
            parser.parse(response.text.splitlines())
        except requests.RequestException:
            parser.parse([])
        _robots_cache[site] = parser

    return _robots_cache[site].can_fetch(settings.USER_AGENT, url)


def fetch(url, params=None, source="", note="", delay=None):
    """Download a URL with delay and retries. Returns the response or None."""
    full_url = requests.Request("GET", url, params=params).prepare().url
    delay = delay or settings.DELAY_SECONDS

    if not is_allowed_by_robots(full_url):
        log_request(source, full_url, status="skipped: robots.txt", note=note)
        return None

    for attempt in range(1, settings.MAX_RETRIES + 1):
        time.sleep(delay)
        try:
            response = session.get(full_url, timeout=settings.TIMEOUT_SECONDS)
        except requests.RequestException as error:
            log_request(source, full_url, status=f"error: {error.__class__.__name__}",
                        note=f"attempt {attempt}")
            continue

        log_request(source, full_url, status=response.status_code,
                    size=len(response.content), note=note)

        if response.status_code == 200:
            return response
        if response.status_code in (400, 403, 404):
            return None
        if response.status_code == 429:  # rate limited: wait as long as the site asks (max 2 minutes)
            time.sleep(min(int(response.headers.get("Retry-After", 60)), 120))
            continue
        time.sleep(delay * attempt)

    return None


def log_request(source, url, status, size=0, note=""):
    REQUEST_LOG.append({
        "source": source,
        "url": url,
        "requested_at_utc": now_utc(),
        "status": status,
        "bytes": size,
        "note": note,
    })


PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?251[\s-]?|0)[79](?:[\s-]?\d){8}(?!\d)")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def remove_contact_details(text):
    """Remove phone numbers and emails (data is published on GitHub)."""
    if not isinstance(text, str):
        return text
    text = PHONE_PATTERN.sub("[phone removed]", text)
    text = EMAIL_PATTERN.sub("[email removed]", text)
    return text


def save_snapshot(source, name, content, extension):
    """Save a copy of the page/JSON as evidence (contact details removed)."""
    folder = os.path.join(OUTPUT_DIR, "snapshots", source)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{name}.{extension}")
    with open(path, "w", encoding="utf-8") as file:
        file.write(remove_contact_details(content))
    return path


def save_csv(rows, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8")
    print(f"Saved {len(rows):>6} rows -> {path}")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def finish_run():
    """Save the request log, zip the snapshots and write checksums."""
    save_csv(REQUEST_LOG, "source_log.csv")

    snapshots = os.path.join(OUTPUT_DIR, "snapshots")
    if os.path.isdir(snapshots):
        shutil.make_archive(snapshots, "zip", snapshots)
        shutil.rmtree(snapshots)
        print(f"Zipped snapshots -> {snapshots}.zip")

    lines = []
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        if filename != "checksums.txt":
            lines.append(f"{sha256_of(os.path.join(OUTPUT_DIR, filename))}  {filename}")
    with open(os.path.join(OUTPUT_DIR, "checksums.txt"), "w") as file:
        file.write("\n".join(lines) + "\n")
    print("Wrote checksums.txt\nDone.")


def dig(data, *keys):
    """Read nested JSON safely: dig(car, "price", "currency") or None."""
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data
