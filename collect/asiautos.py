"""asiautos (China): BYD parts from the public Shopify product feed (part numbers; prices are placeholders)."""

import json

import helpers
import settings

SOURCE = "asiautos"


def product_to_row(product):
    variant = (product.get("variants") or [{}])[0]
    return {
        "product_id": product.get("id"),
        "title": product.get("title"),
        "product_type": product.get("product_type"),
        "tags": ", ".join(product.get("tags") or []),
        "price": variant.get("price"),
        "available": variant.get("available"),
        "product_url": "https://asiautos.net/products/" + (product.get("handle") or ""),
        "updated_at": product.get("updated_at"),
        "collected_at_utc": helpers.now_utc(),
    }


def scrape():
    rows = []
    page = 1
    while page <= settings.ASIAUTOS_MAX_PAGES:
        response = helpers.fetch(settings.ASIAUTOS_FEED, params={"limit": 250, "page": page},
                                 source=SOURCE, note="all products", delay=15)  # rate-limited below this
        if response is None:
            break

        products = json.loads(response.text).get("products", [])
        if not products:
            break

        # Keep the snapshot small: drop the long HTML descriptions
        for product in products:
            product.pop("body_html", None)
        helpers.save_snapshot(SOURCE, f"products_page-{page:03d}", json.dumps(products, ensure_ascii=False), "json")

        rows.extend(product_to_row(product) for product in products)
        print(f"  asiautos  page {page}  ({len(products)} products)")
        page += 1

    return rows
