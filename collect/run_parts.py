"""
Collect parts evidence and save raw data to data/raw/parts-<date>/.

    python collect/run_parts.py           full run
    python collect/run_parts.py --quick   1 page per Jiji search
"""

import os
import sys

import asiautos
import evprotec
import helpers
import jiji
import landin
import nbe
import nhtsa
import settings
import toyota_parts


def main():
    quick = "--quick" in sys.argv
    max_pages = 1 if quick else settings.MAX_PAGES
    helpers.OUTPUT_DIR = settings.PARTS_OUTPUT_DIR + ("-quick-test" if quick else "")

    os.makedirs(helpers.OUTPUT_DIR, exist_ok=True)
    print(f"Collecting into {helpers.OUTPUT_DIR}\n")

    collectors = [
        ("jiji_parts", lambda: jiji.scrape_parts(max_pages)),
        ("landin", landin.scrape),
        ("evprotec", evprotec.scrape),
        ("toyota", toyota_parts.scrape),
        ("asiautos", asiautos.scrape),
        ("nhtsa", nhtsa.scrape),
        ("nbe", nbe.scrape),
    ]
    for name, run in collectors:
        print(f"--- {name} ---")
        try:
            result = run()
        except Exception as error:
            print(f"!! {name} failed: {error}")
            helpers.log_request(name, "", status=f"collector failed: {error}")
            continue

        if name == "nhtsa":
            complaints, recalls = result
            helpers.save_csv(complaints, "nhtsa_complaints.csv")
            helpers.save_csv(recalls, "nhtsa_recalls.csv")
        elif name == "nbe":
            helpers.save_csv(result, "exchange_rates_nbe.csv")
        else:
            helpers.save_csv(result, f"parts_{name}.csv")
        print()

    helpers.finish_run()


if __name__ == "__main__":
    main()
