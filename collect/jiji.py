"""Jiji Ethiopia: JSON listing endpoint, one run per search in settings."""

import json

import helpers
import settings

SOURCE = "jiji"


def advert_to_row(advert):
    # Make/model/year are often missing in search results; parsed from title later.
    attrs = {}
    for item in advert.get("attrs") or []:
        attrs[item.get("name")] = item.get("value")

    schema = advert.get("schema_org") or {}

    return {
        "listing_id": advert.get("id"),
        "listing_url": "https://jiji.com.et" + (advert.get("url") or ""),
        "title": helpers.remove_contact_details(advert.get("title")),
        "price_value": helpers.dig(advert, "price_obj", "value"),
        "price_text": advert.get("price_title"),
        "make": helpers.dig(schema, "brand", "name"),
        "model": schema.get("model"),
        "year": schema.get("vehicleModelDate"),
        "color": schema.get("color"),
        "condition": attrs.get("Condition"),
        "transmission": attrs.get("Transmission"),
        "mileage_km": attrs.get("Mileage"),
        "fuel_type": schema.get("fuelType"),
        "region": advert.get("region_name"),
        "region_parent": advert.get("region_parent_name"),
        "seller_account_id": advert.get("user_id"),
        "is_boosted": advert.get("is_boost"),
        "listing_age_label": "; ".join(str(label.get("value")) for label in advert.get("labels") or []),
    }


def scrape_search(label, extra_params, max_pages):
    rows = []
    page = 1

    while True:
        params = {"slug": "cars", "page": page}
        params.update(extra_params)

        response = helpers.fetch(settings.JIJI_API, params=params, source=SOURCE, note=label)
        if response is None:
            break

        safe_label = label.replace(" ", "_").replace(":", "").replace("=", "-").replace(".", "")
        helpers.save_snapshot(SOURCE, f"{safe_label}_page-{page:03d}", response.text, "json")

        data = json.loads(response.text)
        adverts = helpers.dig(data, "adverts_list", "adverts") or []
        total = helpers.dig(data, "adverts_list", "count")

        for advert in adverts:
            row = advert_to_row(advert)
            row["search_label"] = label
            row["search_total_reported"] = total
            row["page"] = page
            row["collected_at_utc"] = helpers.now_utc()
            rows.append(row)

        print(f"  jiji  {label:<28} page {page}  ({len(adverts)} ads, {total} reported)")

        if not adverts or not data.get("next_url"):
            break
        if max_pages is not None and page >= max_pages:
            break
        page += 1

    return rows


def scrape(max_pages=None):
    all_rows = []
    for label, extra_params in settings.JIJI_SEARCHES.items():
        all_rows.extend(scrape_search(label, extra_params, max_pages))
    return all_rows
