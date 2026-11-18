"""Landin Parts: all VW parts on one page (China-market models incl. ID.4 / ID.6)."""

import json

from bs4 import BeautifulSoup

import helpers
import settings

SOURCE = "landin"


def scrape():
    response = helpers.fetch(settings.LANDIN_VW_URL, source=SOURCE, note="volkswagen parts")
    if response is None:
        return []

    helpers.save_snapshot(SOURCE, "volkswagen", response.text, "html")
    soup = BeautifulSoup(response.text, "html.parser")

    rows = []
    for card in soup.select("div.product-card-wrap"):
        button = card.select_one("button.add-cart-btn")
        if button is None:
            continue
        item = json.loads(button["data-item"])  # {"s": part no, "n": name, "o": OE, "m": model, "p": price}
        rows.append({
            "part_no": item.get("s"),
            "oe_number": item.get("o"),
            "name": item.get("n"),
            "model": item.get("m"),
            "category": card.get("data-cat"),
            "price_text": item.get("p"),
            "part_url": "https://www.landinparts.com" + item.get("u", ""),
            "collected_at_utc": helpers.now_utc(),
        })

    print(f"  landin  {len(rows)} VW parts")
    return rows
