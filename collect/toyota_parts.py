"""Toyota genuine parts (pieces-toyota.fr): bZ4X part groups with EUR prices."""

from bs4 import BeautifulSoup

import helpers
import settings

SOURCE = "toyota"


def text_of(element):
    if element is None:
        return ""
    return element.get_text(" ", strip=True)


def read_parts(html, version, group_name):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for part in soup.select('[itemtype="http://schema.org/Product"]'):
        price = part.select_one('[itemprop="price"]')
        currency = part.select_one('[itemprop="priceCurrency"]')
        availability = part.select_one('[itemprop="availability"]')
        rows.append({
            "version": version,
            "group": group_name,
            "item_ref": text_of(part.select_one(".ref-libelle")),
            "name_fr": text_of(part.select_one('[itemprop="name"]')),
            "part_no": text_of(part.select_one('[itemprop="mpn"]')),
            "price": price.get("content") if price else None,
            "currency": currency.get("content") if currency else None,
            "availability": (availability.get("href") or availability.get("content")) if availability else None,
            "collected_at_utc": helpers.now_utc(),
        })
    return rows


def scrape():
    rows = []
    for version_path in settings.TOYOTA_VERSIONS:
        version = version_path.split("/")[-2]
        response = helpers.fetch(settings.TOYOTA_BASE + version_path, source=SOURCE,
                                 note=version, delay=settings.TOYOTA_DELAY_SECONDS)
        if response is None:
            continue
        helpers.save_snapshot(SOURCE, f"{version}_groups", response.text, "html")

        # Part groups whose name contains one of our keywords
        soup = BeautifulSoup(response.text, "html.parser")
        groups = {}
        for link in soup.select("a[href]"):
            name = text_of(link).split(" pour TOYOTA")[0]
            if version_path + "/" in link["href"] and any(word in name for word in settings.TOYOTA_GROUP_WORDS):
                groups[link["href"]] = name

        for href, group_name in groups.items():
            group_response = helpers.fetch(settings.TOYOTA_BASE + href, source=SOURCE,
                                           note=group_name, delay=settings.TOYOTA_DELAY_SECONDS)
            if group_response is None:
                continue
            group_id = href.rstrip("/").split("/")[-1]
            helpers.save_snapshot(SOURCE, f"{version}_{group_id}", group_response.text, "html")
            parts = read_parts(group_response.text, version, group_name)
            rows.extend(parts)
            print(f"  toyota  {version}  {group_name[:40]:<40} ({len(parts)} parts)")

    return rows
