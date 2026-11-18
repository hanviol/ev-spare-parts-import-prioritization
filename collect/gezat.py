"""Gezat: electric listing cards."""

from bs4 import BeautifulSoup

import helpers
import settings

SOURCE = "gezat"


def card_to_row(card):
    # Card text order: price | currency | year | make | model | "km · fuel · gearbox" | location
    pieces = [text for text in card.stripped_strings if text != "View details"]

    def piece(number):
        return pieces[number] if len(pieces) > number else ""

    specs = [part.strip() for part in piece(5).split("·")]

    href = card.get("href", "")
    return {
        "listing_id": href.split("/")[-1],
        "listing_url": "https://gezat.et" + href,
        "price_text": piece(0),
        "currency": piece(1),
        "year": piece(2),
        "make": piece(3),
        "model": piece(4),
        "mileage_text": specs[0] if len(specs) > 0 else "",
        "fuel_type": specs[1] if len(specs) > 1 else "",
        "transmission": specs[2] if len(specs) > 2 else "",
        "location": piece(6),
        "card_text_raw": " | ".join(pieces),
    }


def scrape(max_pages=None):
    rows = []
    page = 1

    while True:
        response = helpers.fetch(settings.GEZAT_ELECTRIC_URL, params={"page": page},
                                 source=SOURCE, note="electric listings")
        if response is None:
            break

        helpers.save_snapshot(SOURCE, f"electric_page-{page:03d}", response.text, "html")
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("a.gl-card[href^='/listings/']")

        for card in cards:
            row = card_to_row(card)
            row["page"] = page
            row["collected_at_utc"] = helpers.now_utc()
            rows.append(row)

        print(f"  gezat page {page}  ({len(cards)} cards)")

        has_next_page = soup.select_one(f"a[href*='page={page + 1}']") is not None
        if not cards or not has_next_page:
            break
        if max_pages is not None and page >= max_pages:
            break
        page += 1

    return rows
