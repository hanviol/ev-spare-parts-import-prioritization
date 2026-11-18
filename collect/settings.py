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

# Blocked sources: requested once so the source log records the result
CHECK_ONLY_SOURCES = {
    "engocha": "https://engocha.com/classifieds/217218-byd-seagull",
}
