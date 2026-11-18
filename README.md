# EV Spare-Parts Import Prioritization

Which EV replacement parts should a new importer in Ethiopia stock first?
This project collects public marketplace evidence, cleans it, scores vehicles and
parts with an explainable formula, and recommends the five highest-priority parts.

The result is a provisional recommendation based on public listings, not a demand forecast.
Listing counts show market visibility, not sales or registrations.

## Repository layout

```
collect/              scrapers that collect the raw data
  settings.py         models, searches, delays, output folders
  helpers.py          polite fetching, request log, snapshots, privacy filter, saving
  run_all.py          vehicle listings: Adey, Jiji, Mekina, AfroMekina, Gezat
  run_parts.py        parts evidence: Jiji parts, Landin, evprotec, Toyota, asiautos, NHTSA, NBE
  <source>.py         one collector per source
Azarya_Melkamu.ipynb  analysis notebook (Colab)
requirements.txt
```

## Raw data

Raw data is **not** committed. Each collection run is published as a
[GitHub Release](https://github.com/hanviol/ev-spare-parts-import-prioritization/releases),
and the notebook downloads the files from a pinned release tag.
Files are raw: nothing is cleaned, merged or de-duplicated. All cleaning happens in the notebook.

### Vehicle listings (`raw-vehicles-2026-11-18`)

| File | Contents |
|---|---|
| `listings_adey.csv` | Listing cards from 24 EV model pages |
| `adey_page_summary.csv` | Listings, unique sellers and price range per model/make page |
| `listings_jiji.csv` | Jiji ads from 13 model searches + the "Electric" filter |
| `listings_mekina.csv` | Mekina electric listings |
| `listings_afromekina.csv` | AfroMekina electric listings |
| `listings_gezat.csv` | Gezat electric listings |

### Parts evidence (`raw-parts-2026-11-18`)

Part categories: brake pads, brake discs, 12V battery, tyres, headlights, tail lights, side mirrors, bumpers,
fenders, shock absorbers. Tyres and the 12V battery replace wiper blades and cabin-air filters, which had almost
no evidence.

| File | Contents |
|---|---|
| `parts_jiji_parts.csv` | Local parts ads in Ethiopia (ETB) from vehicle and part searches |
| `parts_landin.csv` | China-market VW parts incl. ID.4 / ID.6 (part and OE numbers, RMB prices) |
| `parts_evprotec.csv` | VW ID.4 / ID.6 parts from a Dubai EV parts store (AED prices, stock) |
| `parts_toyota.csv` | Genuine Toyota bZ4X parts (part numbers, EUR prices) |
| `parts_asiautos.csv` | BYD parts incl. Yuan Up / Atto 2 (BYD part numbers; prices are placeholders) |
| `nhtsa_complaints.csv`, `nhtsa_recalls.csv` | US owner complaints and recalls: bZ4X and ID.4 |
| `exchange_rates_nbe.csv` | Official National Bank of Ethiopia exchange rates |

Both releases also contain `source_log.csv` (every request: URL, UTC time, status),
`snapshots.zip` (every page / JSON response) and `checksums.txt` (SHA-256 of each file).

## Sources

| Source | Method | Notes |
|---|---|---|
| [Adey Market](https://adey-market.com) | HTML model pages | Aggregates Telegram channels, dealer sites and YouTube. `/item/` pages are disallowed by robots.txt, so only category pages are read |
| [Jiji Ethiopia](https://jiji.com.et) | JSON listing endpoint | Cars and car-parts sections. Search is fuzzy; matches are checked against titles during cleaning |
| [Mekina.net](https://www.mekina.net) | JSON search endpoint | `fuel=Electric` filter |
| [AfroMekina](https://afromekina.com) | JSON filter endpoint | `fuel_type=electric` filter. Overlaps with Adey |
| [Gezat](https://gezat.et/cars-for-sale/electric) | HTML cards | Likely shares listings with Mekina |
| [Landin Parts](https://www.landinparts.com/volkswagen/) | HTML page | Body and lighting parts only |
| [evprotec](https://evprotec.com) | WooCommerce store API | Marks parts shared by ID.4 and ID.6 |
| [pieces-toyota.fr](https://www.pieces-toyota.fr) | HTML pages | European bZ4X builds; 5 s crawl delay |
| [asiautos](https://asiautos.net) | Shopify product feed | Prices are placeholders |
| [NHTSA](https://www.nhtsa.gov/nhtsa-datasets-and-apis) | Official API | ID.4 stands in for the ID.6 (same platform) |
| [National Bank of Ethiopia](https://nbe.gov.et/exchange/indicatives-rates/) | Official API | Daily rates |
| Engocha, exist.ae, Made-in-China, fansbyd, Glyn Hopkin | none | Blocked (403/429) or disallow automated access; not used |

The JSON endpoints are the ones each site's own pages call. They are undocumented and may change.

## Running the collectors

```bash
pip install -r requirements.txt
python collect/run_all.py            # vehicle listings (about 25 minutes)
python collect/run_parts.py          # parts evidence (about 20 minutes)
```

Add `--quick` for a short test run. Output goes to `data/raw/<date>/` and `data/raw/parts-<date>/`.

## Known limitations

- No public registration or sales data by model; listing counts and unique sellers are proxies.
- One snapshot measures recent listing activity, not the vehicle parc.
- Some Adey model pages (Sealion, Song Plus, Tang, Qin Plus, Leopard) mix EV and plug-in hybrid listings.
- Duplicates exist within and across sources (cross-posting, repeated searches).
- No collectable supplier prices for the BYD Yuan Up; local Jiji prices are used for all vehicles.
- Toyota catalogue prices are for European builds; Ethiopian bZ4X are often China-built.
