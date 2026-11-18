"""
Collect vehicle listings and save raw data to data/raw/<date>/.

    python collect/run_all.py           full run
    python collect/run_all.py --quick   1 page per model/search
"""

import os
import sys

import adey
import afromekina
import gezat
import helpers
import jiji
import mekina
import settings


def main():
    quick = "--quick" in sys.argv
    max_pages = 1 if quick else settings.MAX_PAGES
    if quick:
        helpers.OUTPUT_DIR = settings.OUTPUT_DIR + "-quick-test"

    os.makedirs(helpers.OUTPUT_DIR, exist_ok=True)
    print(f"Collecting into {helpers.OUTPUT_DIR} (max pages: {max_pages or 'all'})\n")

    collectors = [
        ("adey", lambda: adey.scrape(max_pages)),
        ("jiji", lambda: jiji.scrape(max_pages)),
        ("mekina", lambda: mekina.scrape(max_pages)),
        ("afromekina", lambda: afromekina.scrape(max_pages)),
        ("gezat", lambda: gezat.scrape(max_pages)),
    ]
    for name, run in collectors:
        print(f"--- {name} ---")
        try:
            result = run()
        except Exception as error:
            print(f"!! {name} failed: {error}")
            helpers.log_request(name, "", status=f"collector failed: {error}")
            continue

        if name == "adey":
            listings, summary = result
            helpers.save_csv(listings, "listings_adey.csv")
            helpers.save_csv(summary, "adey_page_summary.csv")
        else:
            helpers.save_csv(result, f"listings_{name}.csv")
        print()

    for name, url in settings.CHECK_ONLY_SOURCES.items():
        helpers.fetch(url, source=name, note="availability check only")

    helpers.finish_run()


if __name__ == "__main__":
    main()
