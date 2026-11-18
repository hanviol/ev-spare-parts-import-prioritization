"""Mekina.net: JSON search endpoint, electric cars only."""

import json

import helpers
import settings

SOURCE = "mekina"


def remove_personal_data(data):
    """Blank seller name, phone and social links."""
    for vehicle in data.get("vehicles", []):
        seller = helpers.dig(vehicle, "car", "attributes", "seller")
        if isinstance(seller, dict):
            seller["name"] = "[removed]"
            seller["phone"] = "[removed]"
            seller["social_media"] = "[removed]"
    return data


def vehicle_to_row(vehicle):
    car = helpers.dig(vehicle, "car", "attributes") or {}
    specs = car.get("car_ch") or {}

    return {
        "listing_id": car.get("displayId"),  # internal "id" can be negative
        "listing_url": "https://www.mekina.net/cars/" + (vehicle.get("permalink") or ""),
        "title": car.get("title"),
        "make": helpers.dig(specs, "brand", "data", "attributes", "name"),
        "model": helpers.dig(specs, "model", "data", "attributes", "name"),
        "year": specs.get("year_made"),
        "fuel_type": specs.get("fuel"),
        "transmission": specs.get("transmission"),
        "mileage_km": specs.get("mileage"),
        "color": specs.get("color"),
        "body_type": helpers.dig(specs, "body_type", "data", "attributes", "type"),
        "price_value": helpers.dig(car, "price", "price"),
        "currency": helpers.dig(car, "price", "currency"),
        "price_type": helpers.dig(car, "price", "price_type", "data", "attributes", "type"),
        "seller_type": helpers.dig(car, "seller", "seller_type", "data", "attributes", "type"),
        "location": car.get("location"),
        "status": car.get("status"),
        "created_at": car.get("createdAt"),
        "published_at": car.get("car_publication_date"),
        "updated_at": car.get("updatedAt"),
        "expires_at": car.get("car_expiration_date"),
        "visits": car.get("visits"),
        "is_featured": car.get("featured"),
        "is_premium": car.get("premium"),
    }


def scrape(max_pages=None):
    rows = []
    page = 1

    while True:
        params = {"page": page, "pageSize": settings.MEKINA_PAGE_SIZE}
        params.update(settings.MEKINA_FILTER)
        response = helpers.fetch(settings.MEKINA_API, params=params, source=SOURCE, note="electric listings")
        if response is None:
            break

        data = remove_personal_data(json.loads(response.text))
        helpers.save_snapshot(SOURCE, f"electric_page-{page:03d}", json.dumps(data, ensure_ascii=False), "json")

        vehicles = data.get("vehicles", [])
        page_count = helpers.dig(data, "pagination", "pageCount") or 1

        for vehicle in vehicles:
            row = vehicle_to_row(vehicle)
            row["search_total_reported"] = data.get("total")
            row["page"] = page
            row["collected_at_utc"] = helpers.now_utc()
            rows.append(row)

        print(f"  mekina page {page}/{page_count}  ({len(vehicles)} listings)")

        if not vehicles or page >= page_count:
            break
        if max_pages is not None and page >= max_pages:
            break
        page += 1

    return rows
