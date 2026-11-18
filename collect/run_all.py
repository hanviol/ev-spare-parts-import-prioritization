"""
Run all collectors and save raw data to data/raw/<date>/.

    python collect/run_all.py           full run
    python collect/run_all.py --quick   1 page per model/search
"""

import hashlib
import os
import shutil
import sys

import pandas as pd

import adey
import afromekina
import gezat
import helpers
import jiji
import mekina
import settings


def save_csv(rows, filename):
    path = os.path.join(helpers.OUTPUT_DIR, filename)
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8")
    print(f"Saved {len(rows):>6} rows -> {path}")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


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
            save_csv(listings, "listings_adey.csv")
            save_csv(summary, "adey_page_summary.csv")
        else:
            save_csv(result, f"listings_{name}.csv")
        print()

    for name, url in settings.CHECK_ONLY_SOURCES.items():
        helpers.fetch(url, source=name, note="availability check only")

    save_csv(helpers.REQUEST_LOG, "source_log.csv")

    snapshots = os.path.join(helpers.OUTPUT_DIR, "snapshots")
    if os.path.isdir(snapshots):
        shutil.make_archive(snapshots, "zip", snapshots)
        shutil.rmtree(snapshots)
        print(f"Zipped snapshots -> {snapshots}.zip")

    lines = []
    for filename in sorted(os.listdir(helpers.OUTPUT_DIR)):
        if filename != "checksums.txt":
            lines.append(f"{sha256_of(os.path.join(helpers.OUTPUT_DIR, filename))}  {filename}")
    with open(os.path.join(helpers.OUTPUT_DIR, "checksums.txt"), "w") as file:
        file.write("\n".join(lines) + "\n")
    print("Wrote checksums.txt\nDone.")


if __name__ == "__main__":
    main()
