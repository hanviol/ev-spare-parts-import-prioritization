"""evprotec (Dubai): VW ID.4 / ID.6 parts from the public WooCommerce store API."""

import json

import helpers
import settings

SOURCE = "evprotec"


def product_to_row(product, category):
    prices = product.get("prices") or {}
    minor = prices.get("currency_minor_unit") or 0
    price = int(prices["price"]) / 10 ** minor if prices.get("price") else None

    return {
        "product_id": product.get("id"),
        "sku": product.get("sku"),
        "name": product.get("name"),
        "category": category,
        "price": price,
        "currency": prices.get("currency_code"),
        "in_stock": product.get("is_in_stock"),
        "stock_text": helpers.dig(product, "stock_availability", "text"),
        "product_url": product.get("permalink"),
        "collected_at_utc": helpers.now_utc(),
    }


def scrape():
    rows = []
    for category_id, category in settings.EVPROTEC_CATEGORIES.items():
        page = 1
        while True:
            params = {"category": category_id, "per_page": 100, "page": page}
            response = helpers.fetch(settings.EVPROTEC_API, params=params, source=SOURCE, note=category)
            if response is None:
                break

            products = json.loads(response.text)
            if not products:
                break
            helpers.save_snapshot(SOURCE, f"{category}_page-{page:03d}", response.text, "json")

            for product in products:
                rows.append(product_to_row(product, category))
            print(f"  evprotec  {category:<10} page {page}  ({len(products)} products)")
            page += 1

    return rows
