"""NHTSA (US): owner complaints and recalls by model year."""

import json

import helpers
import settings

SOURCE = "nhtsa"


def scrape():
    complaints = []
    recalls = []

    for make, model, years in settings.NHTSA_VEHICLES:
        for year in years:
            params = {"make": make, "model": model, "modelYear": year}

            response = helpers.fetch(settings.NHTSA_COMPLAINTS, params=params, source=SOURCE, note="complaints")
            if response is not None:
                helpers.save_snapshot(SOURCE, f"complaints_{model}_{year}", response.text, "json")
                for item in json.loads(response.text).get("results", []):
                    complaints.append({
                        "make": make, "model": model, "model_year": year,
                        "odi_number": item.get("odiNumber"),
                        "date_filed": item.get("dateComplaintFiled"),
                        "components": item.get("components"),
                        "summary": helpers.remove_contact_details(item.get("summary")),
                        "crash": item.get("crash"),
                        "fire": item.get("fire"),
                        "collected_at_utc": helpers.now_utc(),
                    })

            response = helpers.fetch(settings.NHTSA_RECALLS, params=params, source=SOURCE, note="recalls")
            if response is not None:
                helpers.save_snapshot(SOURCE, f"recalls_{model}_{year}", response.text, "json")
                for item in json.loads(response.text).get("results", []):
                    recalls.append({
                        "make": make, "model": model, "model_year": year,
                        "campaign": item.get("NHTSACampaignNumber"),
                        "report_date": item.get("ReportReceivedDate"),
                        "component": item.get("Component"),
                        "summary": item.get("Summary"),
                        "collected_at_utc": helpers.now_utc(),
                    })

            print(f"  nhtsa  {model} {year}: {len(complaints)} complaints, {len(recalls)} recalls so far")

    return complaints, recalls
