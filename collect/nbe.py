"""National Bank of Ethiopia: official exchange rates (latest day with data)."""

import json
from datetime import date, timedelta

import helpers
import settings

SOURCE = "nbe"


def scrape():
    day = date.today()
    for _ in range(10):  # weekends/holidays have no rates, so step back up to 10 days
        response = helpers.fetch(settings.NBE_RATES_API, params={"date": day.isoformat()},
                                 source=SOURCE, note="exchange rates")
        rates = json.loads(response.text).get("data", []) if response is not None else []
        if rates:
            helpers.save_snapshot(SOURCE, f"rates_{day.isoformat()}", response.text, "json")
            rows = [{
                "rate_date": item.get("date"),
                "currency": helpers.dig(item, "currency", "code"),
                "currency_name": helpers.dig(item, "currency", "name"),
                "buying_etb": item.get("buying"),
                "selling_etb": item.get("selling"),
                "weighted_average_etb": item.get("weighted_average"),
                "collected_at_utc": helpers.now_utc(),
            } for item in rates]
            print(f"  nbe  {len(rows)} rates for {day.isoformat()}")
            return rows
        day = day - timedelta(days=1)
    return []
