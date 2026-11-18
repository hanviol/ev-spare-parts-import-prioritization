# EV Spare-Parts Import Prioritization

Which EV replacement parts should a new importer in Ethiopia stock first?
This project collects public marketplace evidence, cleans it, scores vehicles and
parts with an explainable formula, and recommends the five highest-priority parts.

The result is a provisional recommendation based on public listings, not a demand forecast.
Listing counts show market visibility, not sales or registrations.

## Repository layout

```
collect/            scrapers that collect the raw data
  settings.py       models, searches, delays, output folder
  helpers.py        polite fetching, request log, snapshots, privacy filter
  adey.py           Adey Market
  jiji.py           Jiji Ethiopia
  mekina.py         Mekina.net
  afromekina.py     AfroMekina
  gezat.py          Gezat
  run_all.py        runs all collectors
Azarya_Melkamu.ipynb  analysis notebook (Colab)
requirements.txt
```

## Raw data

Raw data is **not** committed. Each collection run is published as a
[GitHub Release](https://github.com/hanviol/ev-spare-parts-import-prioritization/releases),
and the notebook downloads the files from a pinned release tag, so the analysis
always starts from the same frozen data.

| File | Contents |
|---|---|
| `listings_adey.csv` | Listing cards from 24 EV model pages |
| `adey_page_summary.csv` | Listings, unique sellers and price range per model/make page |
| `listings_jiji.csv` | Jiji ads from 13 model searches + the "Electric" filter |
| `listings_mekina.csv` | Mekina electric listings |
| `listings_afromekina.csv` | AfroMekina electric listings |
| `listings_gezat.csv` | Gezat electric listings |
| `source_log.csv` | Every request: URL, UTC time, HTTP status |
| `snapshots.zip` | Copy of every page / JSON response the sites returned |
| `checksums.txt` | SHA-256 of each file, checked by the notebook |

Files are raw: nothing is cleaned, merged or de-duplicated. All cleaning happens in the notebook.

## Sources

| Source | Method | Notes |
|---|---|---|
| [Adey Market](https://adey-market.com) | HTML model pages | Aggregates Telegram channels, dealer sites and YouTube. `/item/` pages are disallowed by robots.txt, so only category pages are read |
| [Jiji Ethiopia](https://jiji.com.et) | JSON listing endpoint | Search is fuzzy; matches are checked against titles during cleaning. Make/model/year are parsed from titles |
| [Mekina.net](https://www.mekina.net) | JSON search endpoint | `fuel=Electric` filter |
| [AfroMekina](https://afromekina.com) | JSON filter endpoint | `fuel_type=electric` filter. Overlaps with Adey |
| [Gezat](https://gezat.et/cars-for-sale/electric) | HTML cards | Likely shares listings with Mekina |
| Engocha | none | Returns 403 Forbidden; recorded in the source log |

The JSON endpoints are the ones each site's own pages call. They are undocumented and may change.

## Ethics and privacy

- robots.txt is checked before every request; 1.5 s delay between requests; honest User-Agent.
- Seller names, phone numbers, emails and free-text descriptions returned by the
  Mekina and AfroMekina endpoints are not saved.
- Phone numbers and email addresses are removed from every saved field and snapshot,
  because the raw data is published.
- Internal seller account IDs are kept only to count unique sellers.

## Running the collectors

```bash
pip install -r requirements.txt
python collect/run_all.py --quick   # test: 1 page per model/search
python collect/run_all.py           # full run (about 25 minutes)
```

Output goes to `data/raw/<date>/`.

## Known limitations

- No public registration or sales data by model; listing counts and unique sellers are proxies.
- One snapshot measures listing activity in a ~2–3 month window, not the vehicle parc.
- Some Adey model pages (Sealion, Song Plus, Tang, Qin Plus, Leopard) mix EV and plug-in hybrid listings.
- Duplicates exist within and across sources (cross-posting, repeated searches).
