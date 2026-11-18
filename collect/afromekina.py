"""AfroMekina: JSON filter endpoint, electric cars only."""

import json

import helpers
import settings

SOURCE = "afromekina"

PERSONAL_FIELDS = ["user", "phone", "seller_phone", "description"]


def remove_personal_data(data):
    """Remove seller contact details; keep only dealership id and name."""
    for listing in helpers.dig(data, "data", "listings") or []:
        for field in PERSONAL_FIELDS:
            if field in listing:
                listing[field] = "[removed]"
        dealership = listing.get("dealership")
        if isinstance(dealership, dict):
            listing["dealership"] = {"id": dealership.get("id"), "name": dealership.get("name")}
    return data


def listing_url(listing):
    """e.g. https://afromekina.com/cars/changan-q05-2026-13709"""
    words = f"{listing.get('brand')} {listing.get('model')} {listing.get('year')}".lower().split()
    return "https://afromekina.com/cars/" + "-".join(words) + f"-{listing.get('id')}"


def listing_to_row(listing):
    return {
        "listing_id": listing.get("id"),
        "listing_url": listing_url(listing),
        "title": helpers.remove_contact_details(listing.get("title")),
        "make": listing.get("brand"),
        "model": listing.get("model"),
        "trim": listing.get("trim"),
        "year": listing.get("year"),
        "fuel_type": listing.get("fuel_type"),
        "condition": listing.get("condition"),
        "transmission": listing.get("transmission"),
        "body_type": listing.get("body_type"),
        "mileage_km": listing.get("mileage"),
        "price_value": listing.get("price"),
        "currency": listing.get("currency"),
        "price_type": listing.get("price_type"),
        "has_bank_loan": listing.get("has_bank_loan"),
        "seller_type": listing.get("role_type"),
        "seller_account_id": listing.get("user_id"),
        "dealership_name": helpers.dig(listing, "dealership", "name"),
        "location": listing.get("location"),
        "status": listing.get("status"),
        "created_at": listing.get("created_at"),
        "published_at": listing.get("published_at"),
        "updated_at": listing.get("updated_at"),
        "expires_at": listing.get("expires_at"),
        "views_count": listing.get("views_count"),
        "is_featured": listing.get("is_featured"),
    }


def scrape(max_pages=None):
    rows = []
    page = 1

    while True:
        params = {"page": page}
        params.update(settings.AFROMEKINA_FILTER)
        response = helpers.fetch(settings.AFROMEKINA_API, params=params,
                                 source=SOURCE, note="electric listings")
        if response is None:
            break

        data = remove_personal_data(json.loads(response.text))
        helpers.save_snapshot(SOURCE, f"electric_page-{page:03d}", json.dumps(data, ensure_ascii=False), "json")

        listings = helpers.dig(data, "data", "listings") or []
        pagination = helpers.dig(data, "data", "pagination") or {}
        last_page = pagination.get("last_page") or 1

        for listing in listings:
            row = listing_to_row(listing)
            row["search_total_reported"] = pagination.get("total")
            row["page"] = page
            row["collected_at_utc"] = helpers.now_utc()
            rows.append(row)

        print(f"  afromekina page {page}/{last_page}  ({len(listings)} listings)")

        if not listings or page >= last_page:
            break
        if max_pages is not None and page >= max_pages:
            break
        page += 1

    return rows
