"""Shared helpers: polite fetching, request log, snapshots, privacy filter."""

import os
import re
import time
import urllib.robotparser
from datetime import datetime, timezone
from urllib.parse import urlparse

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


def fetch(url, params=None, source="", note=""):
    """Download a URL with delay and retries. Returns the response or None."""
    full_url = requests.Request("GET", url, params=params).prepare().url

    if not is_allowed_by_robots(full_url):
        log_request(source, full_url, status="skipped: robots.txt", note=note)
        return None

    for attempt in range(1, settings.MAX_RETRIES + 1):
        time.sleep(settings.DELAY_SECONDS)
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
        if response.status_code in (403, 404):
            return None
        time.sleep(settings.DELAY_SECONDS * attempt)

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


def dig(data, *keys):
    """Read nested JSON safely: dig(car, "price", "currency") or None."""
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data
