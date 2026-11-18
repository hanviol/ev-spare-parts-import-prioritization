"""Adey Market: listing cards from each model page (/item/ pages are not fetched)."""

import re

from bs4 import BeautifulSoup

import helpers
import settings

SOURCE = "adey"


def text_of(element):
    if element is None:
        return ""
    return element.get_text(" ", strip=True)


def read_page_header(soup):
    """Read 'N listings from M sellers', page count and price range."""
    page_text = soup.get_text(" ", strip=True)
    header = {}

    match = re.search(r"([\d,]+)\s*listings\s*from\s*([\d,]+)\s*sellers", page_text)
    header["listings_total"] = match.group(1) if match else None
    header["sellers_total"] = match.group(2) if match else None

    match = re.search(r"page\s*(\d+)\s*of\s*(\d+)", page_text)
    header["page_count"] = int(match.group(2)) if match else 1

    for label in soup.select("dl dt"):
        value = label.find_next_sibling("dd")
        name = text_of(label).lower()
        if name in ("lowest", "typical", "highest"):
            header[f"price_{name}"] = text_of(value)

    return header


def read_listing_cards(soup):
    rows = []
    for card in soup.select("a.pcard"):
        currency = text_of(card.select_one(".pcard-cur"))
        price_text = text_of(card.select_one(".pcard-price"))
        if currency:
            price_text = price_text.replace(currency, "").strip()
        if not price_text and "Price on request" in text_of(card):
            price_text = "Price on request"

        # e.g. "AFROMEKINA · Addis Ababa · 4h ago" (parts may be missing)
        meta = helpers.remove_contact_details(text_of(card.select_one(".pcard-meta")))
        meta_parts = [part.strip() for part in meta.split("·") if part.strip()]
        seller = meta_parts[0] if meta_parts else ""
        location = ""
        posted = ""
        for part in meta_parts[1:]:
            if "ago" in part or part.lower() in ("just now", "yesterday"):
                posted = part
            else:
                location = part

        href = card.get("href", "")
        rows.append({
            "listing_id": href.split("/")[-1].split("-")[0],
            "listing_url": settings.ADEY_BASE + href,
            "title": helpers.remove_contact_details(text_of(card.select_one(".pcard-title"))),
            "price_text": price_text,
            "currency": currency,
            "source_type": text_of(card.select_one(".pcard-src")),
            "seller": seller,
            "location": location,
            "posted_text": posted,
            "meta_raw": meta,
        })
    return rows


def scrape_model(slug, model_label, max_pages):
    url = f"{settings.ADEY_BASE}/categories/cars/{slug}"
    rows = []
    header = {}
    page = 1

    while True:
        response = helpers.fetch(url, params={"page": page}, source=SOURCE, note=model_label)
        if response is None:
            break

        helpers.save_snapshot(SOURCE, f"{slug}_page-{page:03d}", response.text, "html")
        soup = BeautifulSoup(response.text, "html.parser")

        if page == 1:
            header = read_page_header(soup)

        cards = read_listing_cards(soup)
        if not cards:
            break

        for card in cards:
            card["model_page"] = slug
            card["model_label"] = model_label
            card["page"] = page
            card["collected_at_utc"] = helpers.now_utc()
            rows.append(card)

        print(f"  adey  {model_label:<22} page {page}/{header.get('page_count')}  ({len(cards)} cards)")

        if page >= header.get("page_count", 1):
            break
        if max_pages is not None and page >= max_pages:
            break
        page += 1

    return rows, header


def scrape(max_pages=None):
    """Returns (listing_rows, summary_rows)."""
    all_rows = []
    summary_rows = []

    for slug, model_label in settings.ADEY_MODELS.items():
        rows, header = scrape_model(slug, model_label, max_pages)
        all_rows.extend(rows)
        summary_rows.append({
            "level": "model",
            "page_slug": slug,
            "label": model_label,
            "cards_collected": len(rows),
            "collected_at_utc": helpers.now_utc(),
            **header,
        })

    for make in settings.ADEY_MAKES:
        url = f"{settings.ADEY_BASE}/categories/cars/{make}"
        response = helpers.fetch(url, source=SOURCE, note=f"make page: {make}")
        if response is None:
            continue
        helpers.save_snapshot(SOURCE, f"make_{make}_page-001", response.text, "html")
        header = read_page_header(BeautifulSoup(response.text, "html.parser"))
        summary_rows.append({
            "level": "make",
            "page_slug": make,
            "label": make,
            "cards_collected": 0,
            "collected_at_utc": helpers.now_utc(),
            **header,
        })

    return all_rows, summary_rows
