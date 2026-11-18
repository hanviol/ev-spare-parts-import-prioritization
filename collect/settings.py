"""Settings for all collectors."""

from datetime import date

USER_AGENT = "Mozilla/5.0 (compatible; ev-parts-research/1.0; internship project)"
DELAY_SECONDS = 1.5
TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
MAX_PAGES = None  # None = all pages

RUN_DATE = date.today().isoformat()
OUTPUT_DIR = f"data/raw/{RUN_DATE}"

# Adey Market: model page slugs -> label
ADEY_BASE = "https://adey-market.com"

ADEY_MODELS = {
    # Assignment candidates
    "byd-seagull-dolphin-mini-atto-1": "BYD Seagull",
    "byd-yuan-up-atto-2": "BYD Yuan Up",
    "changan-benben-e-star": "Changan Benben E-Star",
    "toyota-bz-series-bz4x-bz3-bz3x-bz5": "Toyota bZ series",
    "volkswagen-id-4": "VW ID.4",
    "volkswagen-id-4-crozz-faw-vw": "VW ID.4 Crozz",
    "volkswagen-id-6": "VW ID.6",
    # Other EVs (some pages mix EV and plug-in hybrid)
    "byd-yuan-plus-atto-3": "BYD Yuan Plus",
    "byd-sealion-05-06-07": "BYD Sealion",
    "byd-song-plus": "BYD Song Plus",
    "byd-tang": "BYD Tang",
    "byd-qin-plus": "BYD Qin Plus",
    "byd-leopard-fangchengbao": "BYD Leopard",
    "byd-seal": "BYD Seal",
    "byd-yuan": "BYD Yuan",
    "byd-song": "BYD Song",
    "changan-deepal-changan-ev-brand": "Changan Deepal",
    "dongfeng-nammi": "Dongfeng Nammi",
    "gac-aion-aion-y": "GAC Aion Y",
    "leapmotor-t03": "Leapmotor T03",
    "neta-hozon-auto-neta-u": "Neta U",
    "neta-hozon-auto-neta-aya-formerly-neta-v": "Neta Aya",
    "bmw-ix3": "BMW iX3",
    "tesla-model-y": "Tesla Model Y",
}

ADEY_MAKES = ["byd", "toyota", "volkswagen", "changan"]  # page 1 only, for seller counts

# Jiji: label -> search parameters
JIJI_API = "https://jiji.com.et/api_web/v1/listing"

JIJI_SEARCHES = {
    "filter: powertrain=Electric": {"filter_attr_7177_powertrain": "Electric"},
    "seagull": {"query": "seagull"},
    "yuan up": {"query": "yuan up"},
    "e-star": {"query": "e-star"},
    "benben": {"query": "benben"},
    "bz4x": {"query": "bz4x"},
    "id.4": {"query": "id.4"},
    "id.6": {"query": "id.6"},
    "yuan plus": {"query": "yuan plus"},
    "sealion": {"query": "sealion"},
    "song plus": {"query": "song plus"},
    "byd e2": {"query": "byd e2"},
    "dolphin": {"query": "dolphin"},
    "bz3": {"query": "bz3"},
}

# Mekina: electric only
MEKINA_API = "https://www.mekina.net/api/cars/search"
MEKINA_FILTER = {"fuel": "Electric"}
MEKINA_PAGE_SIZE = 50

# AfroMekina: electric only
AFROMEKINA_API = "https://api.afromekina.com/api/listings/filter"
AFROMEKINA_FILTER = {"fuel_type": "electric", "per_page": 24}

# Gezat: electric only
GEZAT_ELECTRIC_URL = "https://gezat.et/cars-for-sale/electric"

# ---------------- Parts collection (run_parts.py) ----------------
PARTS_OUTPUT_DIR = f"data/raw/parts-{RUN_DATE}"

# Jiji car-parts section: label -> search text (vehicles + part words, English and Amharic)
JIJI_PARTS_SEARCHES = {
    "id4": "id4", "id6": "id6", "bz4x": "bz4x", "yuan up": "yuan up", "atto 2": "atto 2",
    "brake pad": "brake pad", "brake disc": "brake disc", "shock absorber": "shock absorber",
    "suspension": "suspension", "headlight": "headlight", "head light": "head light",
    "tail light": "tail light", "side mirror": "side mirror", "bumper": "bumper", "fender": "fender",
    "tire": "tire", "tyre": "tyre", "car battery": "car battery", "12v battery": "12v battery",
    "am: brake pad": "ፍሬን ሸራ", "am: bumper": "ፓራወልት", "am: fender": "ፈረፋንጎ",
    "am: shock absorber": "አሞርዛተር", "am: light": "ማብራት", "am: tyre": "ጎማ", "am: battery": "ባትሪ",
}

# Landin Parts: China-market VW parts (ID.4 / ID.6), RMB prices
LANDIN_VW_URL = "https://www.landinparts.com/volkswagen/"

# evprotec (Dubai): WooCommerce store API, category id -> label
EVPROTEC_API = "https://evprotec.com/wp-json/wc/store/v1/products"
EVPROTEC_CATEGORIES = {417: "vw-id4", 418: "vw-id6", 664: "vw-id6-x"}

# Toyota genuine parts (French dealer site), bZ4X 2023 FWD and AWD, Europe
TOYOTA_BASE = "https://www.pieces-toyota.fr"
TOYOTA_VERSIONS = [
    "/toyota-voiture/BZ4X/2023/BZ4X/XEAM10L-MWDPSW/561210",
    "/toyota-voiture/BZ4X/2023/BZ4X/YEAM15L-MWDPSW/561210",
]
TOYOTA_GROUP_WORDS = ["ETRIER DE FREIN", "MOYEU", "AMORTISSEUR", "PARE-CHOCS", "CAPOT ET AILES", "PHARES",
                      "FEUX ARRIERE", "RETROVISEUR", "BATTERIE ET CABLES", "DISQUE DE ROUE"]  # brake discs are in the hub groups
TOYOTA_DELAY_SECONDS = 5  # crawl-delay in robots.txt

# asiautos (China): Shopify product feed, BYD parts incl. Yuan Up / Atto 2
ASIAUTOS_FEED = "https://asiautos.net/products.json"
ASIAUTOS_MAX_PAGES = 2  # store rate-limits; newest products (incl. Yuan Up range) are on the first pages

# NHTSA (US): complaints and recalls; ID.4 stands in for the ID.6 (same MEB platform)
NHTSA_COMPLAINTS = "https://api.nhtsa.gov/complaints/complaintsByVehicle"
NHTSA_RECALLS = "https://api.nhtsa.gov/recalls/recallsByVehicle"
NHTSA_VEHICLES = [
    ("TOYOTA", "BZ4X", [2023, 2024, 2025]),
    ("VOLKSWAGEN", "ID.4", [2021, 2022, 2023, 2024, 2025]),
]

# National Bank of Ethiopia: official daily exchange rates
NBE_RATES_API = "https://api.nbe.gov.et/api/filter-exchange-rates"

# Blocked sources: requested once so the source log records the result
CHECK_ONLY_SOURCES = {
    "engocha": "https://engocha.com/classifieds/217218-byd-seagull",
}
