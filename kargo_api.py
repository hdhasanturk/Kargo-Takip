"""
Kargo Guzergah Sistemi - Mock API
Bu sistem sehirler arasi guzergahi hesaplar.
"""

import json
import logging
import math
import os
import sqlite3
import unicodedata
from collections import deque
from pathlib import Path

import requests
from dotenv import load_dotenv

from database import get_ship24_tracker_id, set_ship24_tracker_id

load_dotenv()

TURKISH_CITIES = [
    "Adana", "Adiyaman", "Afyonkarahisar", "Agri", "Aksaray", "Amasya",
    "Ankara", "Antalya", "Ardahan", "Artvin", "Aydin", "Balikesir",
    "Bartin", "Batman", "Bayburt", "Bilecik", "Bingol", "Bitlis",
    "Bolu", "Burdur", "Bursa", "Canakkale", "Cankiri", "Corum",
    "Denizli", "Diyarbakir", "Duzce", "Edirne", "Elazig", "Erzincan",
    "Erzurum", "Eskisehir", "Gaziantep", "Giresun", "Gumushane",
    "Hakkari", "Hatay", "Igdir", "Isparta", "Istanbul", "Izmir",
    "Kahramanmaras", "Karabuk", "Karaman", "Kars", "Kastamonu",
    "Kayseri", "Kirikkale", "Kirklareli", "Kirsehir", "Kilis",
    "Kocaeli", "Konya", "Kutahya", "Malatya", "Manisa", "Mardin",
    "Mersin", "Mugla", "Mus", "Nevsehir", "Nigde", "Ordu",
    "Osmaniye", "Rize", "Sakarya", "Samsun", "Sanliurfa", "Siirt",
    "Sinop", "Sirnak", "Sivas", "Tekirdag", "Tokat", "Trabzon", "Tunceli",
    "Usak", "Van", "Yalova", "Yozgat", "Zonguldak",
]

CITY_CONNECTIONS = {
    "Adana": ["Kayseri", "Kahramanmaras", "Mersin", "Nigde", "Osmaniye"],
    "Adiyaman": ["Diyarbakir", "Gaziantep", "Kahramanmaras", "Malatya", "Sanliurfa"],
    "Afyonkarahisar": ["Antalya", "Denizli", "Eskisehir", "Konya", "Kutahya", "Usak"],
    "Agri": ["Bitlis", "Erzurum", "Igdir", "Kars", "Van"],
    "Aksaray": ["Ankara", "Karaman", "Kirikkale", "Kirsehir", "Konya", "Nevsehir", "Nigde"],
    "Amasya": ["Corum", "Ordu", "Samsun", "Tokat", "Yozgat"],
    "Ankara": ["Aksaray", "Bilecik", "Bolu", "Cankiri", "Eskisehir", "Kirikkale", "Kirsehir", "Konya"],
    "Antalya": ["Afyonkarahisar", "Burdur", "Denizli", "Isparta", "Konya", "Mersin", "Mugla"],
    "Ardahan": ["Artvin", "Erzurum", "Kars"],
    "Artvin": ["Ardahan", "Erzurum", "Rize"],
    "Aydin": ["Denizli", "Izmir", "Mugla"],
    "Balikesir": ["Bursa", "Canakkale", "Kutahya", "Manisa"],
    "Bartin": ["Karabuk", "Kastamonu", "Zonguldak"],
    "Batman": ["Bitlis", "Diyarbakir", "Mardin", "Mus", "Siirt", "Sirnak"],
    "Bayburt": ["Erzincan", "Erzurum", "Giresun", "Gumushane", "Trabzon"],
    "Bilecik": ["Ankara", "Bursa", "Eskisehir", "Kocaeli", "Kutahya", "Sakarya"],
    "Bingol": ["Bitlis", "Diyarbakir", "Elazig", "Erzurum", "Mus", "Tunceli"],
    "Bitlis": ["Agri", "Batman", "Bingol", "Mus", "Siirt", "Van"],
    "Bolu": ["Ankara", "Duzce", "Eskisehir", "Karabuk", "Sakarya", "Zonguldak"],
    "Burdur": ["Antalya", "Denizli", "Isparta", "Mugla"],
    "Bursa": ["Balikesir", "Bilecik", "Canakkale", "Kocaeli", "Kutahya", "Yalova"],
    "Canakkale": ["Balikesir", "Bursa", "Tekirdag"],
    "Cankiri": ["Ankara", "Corum", "Karabuk", "Kirikkale", "Kirsehir"],
    "Corum": ["Amasya", "Cankiri", "Samsun", "Sinop", "Tokat", "Yozgat"],
    "Denizli": ["Afyonkarahisar", "Antalya", "Aydin", "Burdur", "Izmir", "Manisa", "Mugla", "Usak"],
    "Diyarbakir": ["Adiyaman", "Batman", "Bingol", "Elazig", "Mardin", "Mus", "Sanliurfa", "Siirt"],
    "Duzce": ["Bolu", "Sakarya", "Zonguldak"],
    "Edirne": ["Kirklareli", "Tekirdag"],
    "Elazig": ["Bingol", "Diyarbakir", "Erzincan", "Erzurum", "Malatya", "Tunceli"],
    "Erzincan": ["Bayburt", "Elazig", "Erzurum", "Giresun", "Gumushane", "Malatya", "Sivas", "Tunceli"],
    "Erzurum": ["Agri", "Ardahan", "Artvin", "Bayburt", "Bingol", "Bitlis", "Elazig", "Erzincan", "Kars", "Mus", "Rize"],
    "Eskisehir": ["Afyonkarahisar", "Ankara", "Bilecik", "Bolu", "Bursa", "Kutahya", "Konya"],
    "Gaziantep": ["Adiyaman", "Hatay", "Kahramanmaras", "Kilis", "Osmaniye", "Sanliurfa"],
    "Giresun": ["Bayburt", "Erzincan", "Gumushane", "Ordu", "Sivas", "Trabzon"],
    "Gumushane": ["Bayburt", "Erzincan", "Erzurum", "Giresun", "Trabzon"],
    "Hakkari": ["Siirt", "Sirnak", "Van"],
    "Hatay": ["Adana", "Gaziantep", "Kilis", "Osmaniye"],
    "Igdir": ["Agri", "Kars"],
    "Isparta": ["Afyonkarahisar", "Antalya", "Burdur", "Konya"],
    "Istanbul": ["Kocaeli", "Kirklareli", "Tekirdag", "Yalova"],
    "Izmir": ["Aydin", "Denizli", "Manisa"],
    "Kahramanmaras": ["Adana", "Adiyaman", "Gaziantep", "Kayseri", "Malatya", "Osmaniye", "Sivas"],
    "Karabuk": ["Bartin", "Bolu", "Cankiri", "Kastamonu", "Zonguldak"],
    "Karaman": ["Aksaray", "Konya", "Mersin", "Nigde"],
    "Kars": ["Agri", "Ardahan", "Erzurum", "Igdir"],
    "Kastamonu": ["Bartin", "Karabuk", "Sinop", "Zonguldak"],
    "Kayseri": ["Adana", "Kahramanmaras", "Kirikkale", "Nevsehir", "Nigde", "Sivas", "Yozgat"],
    "Kirikkale": ["Aksaray", "Ankara", "Cankiri", "Kayseri", "Kirsehir", "Yozgat"],
    "Kirklareli": ["Edirne", "Istanbul", "Tekirdag"],
    "Kirsehir": ["Aksaray", "Ankara", "Cankiri", "Kirikkale", "Nevsehir", "Yozgat"],
    "Kilis": ["Gaziantep", "Hatay", "Sanliurfa"],
    "Kocaeli": ["Bilecik", "Bursa", "Istanbul", "Sakarya", "Yalova"],
    "Konya": ["Afyonkarahisar", "Aksaray", "Ankara", "Antalya", "Eskisehir", "Isparta", "Karaman", "Mersin", "Nigde"],
    "Kutahya": ["Afyonkarahisar", "Balikesir", "Bilecik", "Bursa", "Eskisehir", "Manisa", "Usak"],
    "Malatya": ["Adiyaman", "Elazig", "Erzincan", "Kahramanmaras", "Sivas"],
    "Manisa": ["Balikesir", "Denizli", "Izmir", "Kutahya", "Usak"],
    "Mardin": ["Batman", "Diyarbakir", "Sanliurfa", "Siirt", "Sirnak"],
    "Mersin": ["Adana", "Antalya", "Karaman", "Konya", "Nigde", "Osmaniye"],
    "Mugla": ["Antalya", "Aydin", "Burdur", "Denizli"],
    "Mus": ["Batman", "Bingol", "Bitlis", "Erzurum", "Van"],
    "Nevsehir": ["Aksaray", "Kayseri", "Kirikkale", "Kirsehir", "Nigde", "Yozgat"],
    "Nigde": ["Adana", "Aksaray", "Karaman", "Kayseri", "Konya", "Mersin", "Nevsehir"],
    "Ordu": ["Amasya", "Giresun", "Samsun", "Sivas", "Tokat"],
    "Osmaniye": ["Adana", "Gaziantep", "Hatay", "Kahramanmaras", "Mersin"],
    "Rize": ["Artvin", "Erzurum", "Trabzon"],
    "Sakarya": ["Bilecik", "Bolu", "Duzce", "Kocaeli"],
    "Samsun": ["Amasya", "Corum", "Ordu", "Sinop", "Tokat"],
    "Sanliurfa": ["Adiyaman", "Diyarbakir", "Gaziantep", "Kilis", "Mardin"],
    "Siirt": ["Batman", "Bitlis", "Hakkari", "Mardin", "Sirnak"],
    "Sirnak": ["Batman", "Hakkari", "Mardin", "Siirt", "Van"],
    "Sivas": ["Erzincan", "Giresun", "Kahramanmaras", "Kayseri", "Malatya", "Ordu", "Tokat", "Yozgat"],
    "Tekirdag": ["Canakkale", "Edirne", "Istanbul", "Kirklareli"],
    "Tokat": ["Amasya", "Corum", "Ordu", "Samsun", "Sivas", "Yozgat"],
    "Trabzon": ["Bayburt", "Giresun", "Gumushane", "Rize"],
    "Tunceli": ["Bingol", "Elazig", "Erzincan", "Erzurum"],
    "Usak": ["Afyonkarahisar", "Denizli", "Kutahya", "Manisa"],
    "Van": ["Agri", "Bitlis", "Hakkari", "Mus", "Sirnak"],
    "Yalova": ["Bursa", "Istanbul", "Kocaeli"],
    "Yozgat": ["Amasya", "Corum", "Kayseri", "Kirikkale", "Kirsehir", "Nevsehir", "Sivas", "Tokat"],
    "Zonguldak": ["Bartin", "Bolu", "Duzce", "Karabuk", "Kastamonu"],
}

CITY_ALIASES = {
    "adiyaman": "Adiyaman",
    "afyon": "Afyonkarahisar",
    "agri": "Agri",
    "ankara": "Ankara",
    "antalya": "Antalya",
    "ardahan": "Ardahan",
    "artvin": "Artvin",
    "aydin": "Aydin",
    "balikesir": "Balikesir",
    "bartin": "Bartin",
    "batman": "Batman",
    "bayburt": "Bayburt",
    "bilecik": "Bilecik",
    "bingol": "Bingol",
    "bitlis": "Bitlis",
    "bolu": "Bolu",
    "burdur": "Burdur",
    "bursa": "Bursa",
    "canakkale": "Canakkale",
    "cankiri": "Cankiri",
    "corum": "Corum",
    "denizli": "Denizli",
    "diyarbakir": "Diyarbakir",
    "duzce": "Duzce",
    "edirne": "Edirne",
    "elazig": "Elazig",
    "erzincan": "Erzincan",
    "erzurum": "Erzurum",
    "eskisehir": "Eskisehir",
    "gaziantep": "Gaziantep",
    "giresun": "Giresun",
    "gumushane": "Gumushane",
    "hakkari": "Hakkari",
    "hatay": "Hatay",
    "igdir": "Igdir",
    "isparta": "Isparta",
    "istanbul": "Istanbul",
    "izmir": "Izmir",
    "kahramanmaras": "Kahramanmaras",
    "karabuk": "Karabuk",
    "karaman": "Karaman",
    "kars": "Kars",
    "kastamonu": "Kastamonu",
    "kayseri": "Kayseri",
    "kirikkale": "Kirikkale",
    "kirklareli": "Kirklareli",
    "kirsehir": "Kirsehir",
    "kilis": "Kilis",
    "kocaeli": "Kocaeli",
    "konya": "Konya",
    "kutahya": "Kutahya",
    "malatya": "Malatya",
    "manisa": "Manisa",
    "mardin": "Mardin",
    "mersin": "Mersin",
    "mugla": "Mugla",
    "mus": "Mus",
    "nevsehir": "Nevsehir",
    "nigde": "Nigde",
    "ordu": "Ordu",
    "osmaniye": "Osmaniye",
    "rize": "Rize",
    "sakarya": "Sakarya",
    "samsun": "Samsun",
    "sanliurfa": "Sanliurfa",
    "siirt": "Siirt",
    "sinop": "Sinop",
    "sirnak": "Sirnak",
    "sivas": "Sivas",
    "tekirdag": "Tekirdag",
    "tokat": "Tokat",
    "trabzon": "Trabzon",
    "tunceli": "Tunceli",
    "usak": "Usak",
    "van": "Van",
    "yalova": "Yalova",
    "yozgat": "Yozgat",
    "zonguldak": "Zonguldak",
}

_CITY_REPLACE = str.maketrans({
    "\u0131": "i",
    "\u0130": "i",
    "\u011f": "g",
    "\u011e": "g",
    "\u00fc": "u",
    "\u00dc": "u",
    "\u015f": "s",
    "\u015e": "s",
    "\u00f6": "o",
    "\u00d6": "o",
    "\u00e7": "c",
    "\u00c7": "c",
})

_BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = _BASE_DIR / "logs"
SHIP24_LOG_PATH = LOG_DIR / "ship24.log"
LOCATION_DATA_PATH = _BASE_DIR / "turkiye-city-county-district-neighborhood-main" / "data.json"
LOCATION_DB_PATH = _BASE_DIR / "data" / "turkiye_locations.db"
_LOCATION_DATA = None
_LOCATION_INDEX = None
_CITY_NAME_MAP = None

SHIP24_BASE_URL = os.getenv("SHIP24_BASE_URL", "https://api.ship24.com/public/v1")
SHIP24_TIMEOUT = float(os.getenv("SHIP24_TIMEOUT", "12"))
SHIP24_API_KEY = os.getenv("SHIP24_API_KEY", "").strip()
SHIP24_ENABLED = os.getenv("SHIP24_ENABLED", "1").lower() not in ("0", "false", "no")

OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")
OSRM_PROFILE = os.getenv("OSRM_PROFILE", "driving")
OSRM_TIMEOUT = float(os.getenv("OSRM_TIMEOUT", "6"))
OSRM_ENABLED = os.getenv("OSRM_ENABLED", "1").lower() not in ("0", "false", "no")
OSRM_GEOCODE_URL = os.getenv("OSRM_GEOCODE_URL", "https://nominatim.openstreetmap.org/search")
OSRM_GEOCODE_ENABLED = os.getenv("OSRM_GEOCODE_ENABLED", "1").lower() not in ("0", "false", "no")
ROAD_DISTANCE_FACTOR = float(os.getenv("ROAD_DISTANCE_FACTOR", "1.2"))
_CITY_COORDS_CACHE = None
_OSRM_DISTANCE_CACHE = {}
_CITY_COORDS_PATH = _BASE_DIR / "data" / "city_coords.json"


def _get_ship24_logger():
    logger = logging.getLogger("ship24")
    if logger.handlers:
        return logger

    LOG_DIR.mkdir(exist_ok=True)
    handler = logging.FileHandler(SHIP24_LOG_PATH, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def _norm_city(value):
    text = (value or "").strip()
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower().translate(_CITY_REPLACE)


def _resolve_city_name(city):
    normalized = _norm_city(city)
    if normalized in CITY_ALIASES:
        return CITY_ALIASES[normalized]
    return (city or "").strip()


def _get_city_name_map():
    global _CITY_NAME_MAP
    if _CITY_NAME_MAP is not None:
        return _CITY_NAME_MAP

    conn = _get_location_connection()
    if not conn:
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM cities")
        rows = cursor.fetchall()
        _CITY_NAME_MAP = {_norm_city(row[0]): row[0] for row in rows}
        return _CITY_NAME_MAP
    finally:
        conn.close()


def _resolve_city_name_from_db(city):
    normalized = _norm_city(city)
    alias = CITY_ALIASES.get(normalized)
    if alias:
        normalized = _norm_city(alias)

    name_map = _get_city_name_map()
    if name_map:
        return name_map.get(normalized, alias or (city or "").strip())

    return alias or (city or "").strip()


def _load_city_coords_cache():
    global _CITY_COORDS_CACHE
    if _CITY_COORDS_CACHE is not None:
        return _CITY_COORDS_CACHE

    _CITY_COORDS_CACHE = {}
    try:
        if _CITY_COORDS_PATH.exists():
            with open(_CITY_COORDS_PATH, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                _CITY_COORDS_CACHE = data
    except (OSError, ValueError):
        _CITY_COORDS_CACHE = {}

    return _CITY_COORDS_CACHE


def _save_city_coords_cache():
    if _CITY_COORDS_CACHE is None:
        return

    try:
        _CITY_COORDS_PATH.parent.mkdir(exist_ok=True)
        with open(_CITY_COORDS_PATH, "w", encoding="utf-8") as handle:
            json.dump(_CITY_COORDS_CACHE, handle, ensure_ascii=True)
    except OSError:
        pass


def _geocode_city(city_name):
    if not OSRM_GEOCODE_ENABLED or not city_name:
        return None

    params = {
        "format": "json",
        "limit": 1,
        "city": city_name,
        "country": "Turkey",
    }
    headers = {
        "User-Agent": "kargo-takip/1.0",
    }

    try:
        response = requests.get(
            OSRM_GEOCODE_URL,
            params=params,
            headers=headers,
            timeout=OSRM_TIMEOUT,
        )
        if response.status_code >= 400:
            return None
        data = response.json()
        if not data:
            return None
        item = data[0]
        return float(item["lat"]), float(item["lon"])
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None


def _get_city_coords(city):
    city_name = _resolve_city_name_from_db(city) or _resolve_city_name(city)
    if not city_name:
        return None

    cache = _load_city_coords_cache()
    coords = cache.get(city_name)
    if isinstance(coords, list) and len(coords) == 2:
        return coords[0], coords[1]

    coords = _geocode_city(city_name)
    if coords:
        cache[city_name] = [coords[0], coords[1]]
        _save_city_coords_cache()
    return coords


def _osrm_distance_km(start_city, end_city):
    if not OSRM_ENABLED:
        return None

    cache_key = f"{OSRM_PROFILE}:{start_city}->{end_city}"
    if cache_key in _OSRM_DISTANCE_CACHE:
        return _OSRM_DISTANCE_CACHE[cache_key]

    start_coords = _get_city_coords(start_city)
    end_coords = _get_city_coords(end_city)
    if not start_coords or not end_coords:
        return None

    start_lat, start_lon = start_coords
    end_lat, end_lon = end_coords

    url = (
        f"{OSRM_BASE_URL.rstrip('/')}/route/v1/{OSRM_PROFILE}/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
    )
    params = {"overview": "false"}

    try:
        response = requests.get(url, params=params, timeout=OSRM_TIMEOUT)
        if response.status_code >= 400:
            return None
        payload = response.json()
        if payload.get("code") not in ("Ok", "OK", None):
            return None
        routes = payload.get("routes") or []
        if not routes:
            return None
        distance_m = routes[0].get("distance")
        if distance_m is None:
            return None
        distance_km = float(distance_m) / 1000
        _OSRM_DISTANCE_CACHE[cache_key] = distance_km
        return distance_km
    except (requests.RequestException, ValueError, TypeError):
        return None


def _haversine_km(start_coords, end_coords):
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371 * c


def _segment_distance_km(start_city, end_city):
    distance = _osrm_distance_km(start_city, end_city)
    if distance is not None:
        return distance

    start_coords = _get_city_coords(start_city)
    end_coords = _get_city_coords(end_city)
    if start_coords and end_coords:
        return _haversine_km(start_coords, end_coords) * ROAD_DISTANCE_FACTOR

    return None


def _load_location_data():
    global _LOCATION_DATA
    if _LOCATION_DATA is None:
        try:
            with open(LOCATION_DATA_PATH, "r", encoding="utf-8") as file:
                _LOCATION_DATA = json.load(file)
        except FileNotFoundError:
            _LOCATION_DATA = []
    return _LOCATION_DATA


def _build_location_index():
    global _LOCATION_INDEX
    if _LOCATION_INDEX is not None:
        return _LOCATION_INDEX

    _LOCATION_INDEX = {}
    for city in _load_location_data():
        city_name = city.get("name", "")
        _LOCATION_INDEX[_norm_city(city_name)] = city
    return _LOCATION_INDEX


def _default_counties_for_city(city):
    return [f"{city} Merkez"]


def _default_districts_for_county(county):
    return [f"{county} Merkez"]


def _default_neighborhoods_for_district(district):
    return [f"{district} Merkez", f"{district} Yeni Mahalle", f"{district} Cumhuriyet"]


def _get_location_connection():
    if not os.path.exists(LOCATION_DB_PATH):
        return None
    conn = sqlite3.connect(LOCATION_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_cities():
    conn = _get_location_connection()
    if not conn:
        return sorted(TURKISH_CITIES)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM cities ORDER BY name")
        cities = [row[0] for row in cursor.fetchall()]
        return cities if cities else sorted(TURKISH_CITIES)
    except Exception as e:
        print(f"Error in get_cities: {e}")
        return sorted(TURKISH_CITIES)
    finally:
        conn.close()


def get_counties_by_city(city):
    conn = _get_location_connection()
    if not conn:
        return _default_counties_for_city(city)
    city = _resolve_city_name_from_db(city)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT c.name FROM counties c
               JOIN cities ci ON c.city_id = ci.id
               WHERE ci.name = ?
               ORDER BY c.name""",
            (city,)
        )
        rows = cursor.fetchall()
        counties = [row[0] for row in rows]
        return counties if counties else _default_counties_for_city(city)
    except Exception as e:
        print(f"Error in get_counties_by_city: {e}")
        return _default_counties_for_city(city)
    finally:
        conn.close()


def get_districts_by_county(city, county):
    conn = _get_location_connection()
    if not conn:
        return _default_districts_for_county(county)
    city = _resolve_city_name_from_db(city)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT d.name FROM districts d
               JOIN counties c ON d.county_id = c.id
               JOIN cities ci ON c.city_id = ci.id
               WHERE ci.name = ? AND c.name = ?
               ORDER BY d.name""",
            (city, county)
        )
        rows = cursor.fetchall()
        districts = [row[0] for row in rows]
        return districts if districts else _default_districts_for_county(county)
    except Exception as e:
        print(f"Error in get_districts_by_county: {e}")
        return _default_districts_for_county(county)
    finally:
        conn.close()


def get_neighborhoods_by_county(city, county):
    conn = _get_location_connection()
    if not conn:
        return _default_neighborhoods_for_district(county)
    city = _resolve_city_name_from_db(city)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT n.name FROM neighborhoods n
               JOIN districts d ON n.district_id = d.id
               JOIN counties c ON d.county_id = c.id
               JOIN cities ci ON c.city_id = ci.id
               WHERE ci.name = ? AND c.name = ?
               ORDER BY n.name""",
            (city, county)
        )
        rows = cursor.fetchall()
        neighborhoods = [row[0] for row in rows]
        return neighborhoods if neighborhoods else _default_neighborhoods_for_district(county)
    except Exception as e:
        print(f"Error in get_neighborhoods_by_county: {e}")
        return _default_neighborhoods_for_district(county)
    finally:
        conn.close()


def get_neighborhoods_by_district(city, county, district):
    conn = _get_location_connection()
    if not conn:
        return _default_neighborhoods_for_district(district)
    city = _resolve_city_name_from_db(city)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT n.name FROM neighborhoods n
               JOIN districts d ON n.district_id = d.id
               JOIN counties c ON d.county_id = c.id
               JOIN cities ci ON c.city_id = ci.id
               WHERE ci.name = ? AND c.name = ? AND d.name = ?
               ORDER BY n.name""",
            (city, county, district)
        )
        rows = cursor.fetchall()
        neighborhoods = [row[0] for row in rows]
        return neighborhoods if neighborhoods else _default_neighborhoods_for_district(district)
    except Exception as e:
        print(f"Error in get_neighborhoods_by_district: {e}")
        return _default_neighborhoods_for_district(district)
    finally:
        conn.close()


def calculate_route(start_city, end_city):
    start_city = _resolve_city_name(start_city)
    end_city = _resolve_city_name(end_city)

    if start_city == end_city:
        return [start_city]

    visited = {start_city}
    queue = deque([[start_city]])

    while queue:
        path = queue.popleft()
        current = path[-1]

        if current == end_city:
            return path

        for next_city in CITY_CONNECTIONS.get(current, []):
            if next_city in visited:
                continue
            visited.add(next_city)
            queue.append(path + [next_city])

    return [start_city, end_city]


def get_next_city(route, current_city):
    if current_city not in route:
        return route[-1] if route else current_city

    current_index = route.index(current_city)
    if current_index < len(route) - 1:
        return route[current_index + 1]
    return current_city


def get_route_progress(route, current_city):
    if current_city not in route:
        return {"progress": 0, "remaining": route, "completed": []}

    current_index = route.index(current_city)
    completed = route[:current_index + 1]
    remaining = route[current_index + 1:]
    progress = int(((current_index + 1) / len(route)) * 100)

    return {
        "progress": progress,
        "remaining": remaining,
        "completed": completed,
        "current_index": current_index,
        "total_cities": len(route),
    }


def estimate_delivery_time(route):
    if len(route) <= 2:
        return 1
    if len(route) <= 4:
        return 2
    if len(route) <= 6:
        return 3
    return 4


def format_route(route):
    if not route:
        return ""
    return ",".join(route)


def calculate_distance_km(route):
    if not route or len(route) <= 1:
        return 0
    total_distance = 0
    for index in range(len(route) - 1):
        segment_distance = _segment_distance_km(route[index], route[index + 1])
        if segment_distance is None:
            return (len(route) - 1) * 85
        total_distance += segment_distance

    return round(total_distance)


def calculate_desi(volume_cm3):
    if not volume_cm3:
        return 0
    return round(float(volume_cm3) / 3000, 2)


def calculate_shipping_price(weight_kg, volume_cm3, route, delivery_type="Adrese Teslim"):
    weight = max(float(weight_kg or 0), 0)
    desi = calculate_desi(volume_cm3)
    billable = max(weight, desi)
    distance_km = calculate_distance_km(route)

    if billable <= 1:
        base_price = 74
    elif billable <= 5:
        base_price = 94
    elif billable <= 10:
        base_price = 119
    elif billable <= 20:
        base_price = 169
    else:
        base_price = 219 + ((billable - 20) * 6)

    if distance_km <= 300:
        distance_multiplier = 1.00
    elif distance_km <= 700:
        distance_multiplier = 1.18
    else:
        distance_multiplier = 1.35

    delivery_surcharge = 18 if delivery_type == "Adrese Teslim" else 0

    total = round((base_price * distance_multiplier) + delivery_surcharge, 2)
    return {
        "price": total,
        "desi": desi,
        "distance_km": distance_km,
        "billable_weight": round(billable, 2),
    }


def _ship24_is_enabled():
    return SHIP24_ENABLED and bool(SHIP24_API_KEY)


def _ship24_request(method, endpoint, payload=None):
    if not _ship24_is_enabled():
        return None, "Ship24 API key missing"

    url = f"{SHIP24_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {SHIP24_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.request(
            method,
            url,
            json=payload,
            headers=headers,
            timeout=SHIP24_TIMEOUT,
        )
    except requests.RequestException as exc:
        return None, str(exc)

    if response.status_code >= 400:
        return None, f"HTTP {response.status_code}: {response.text}"

    try:
        return response.json(), None
    except ValueError:
        return None, "Invalid JSON response"


def _normalize_courier_code(courier_name):
    """Map Turkish courier names to Ship24 courier codes."""
    if not courier_name:
        return None
    
    # Turkish name → Ship24 code mapping
    mapping = {
        "Yurt İçi Kargo": "yurtici",
        "Yurtici": "yurtici",
        "yurtici": "yurtici",
        "Aras": "aras",
        "aras": "aras",
        "PTT": "ptt",
        "ptt": "ppt",
        "UPS": "ups",
        "ups": "ups",
        "FedEx": "fedex",
        "fedex": "fedex",
        "DHL": "dhl",
        "dhl": "dhl",
        "TNT": "tnt",
        "tnt": "tnt",
    }
    
    courier_lower = str(courier_name).strip()
    return mapping.get(courier_lower) or mapping.get(courier_lower.lower()) or courier_lower.lower()


def _ship24_create_tracker(tracking_number, courier_code=None):
    payload = {"trackingNumber": tracking_number}
    if courier_code:
        payload["courierCode"] = courier_code

    data, error = _ship24_request("POST", "/trackers", payload)
    if error:
        return None, error

    tracker = (data or {}).get("data", {}).get("tracker") or {}
    tracker_id = tracker.get("trackerId") or tracker.get("id")
    if not tracker_id:
        return None, "Tracker id missing"
    return tracker_id, None


def _ship24_extract_tracking(data):
    payload = (data or {}).get("data", {})
    trackings = payload.get("trackings") or []
    if trackings:
        return trackings[0]
    return payload.get("tracking") or {}


def _ship24_format_location(value):
    if isinstance(value, dict):
        parts = [value.get("city"), value.get("state"), value.get("country")]
        return ", ".join([part for part in parts if part])
    if value is None:
        return ""
    return str(value)


def _ship24_map_status(raw_status):
    if not raw_status:
        return "Yolda"

    status = str(raw_status).lower()
    delivered = {"delivered", "delivered_to_pickup", "delivered_to_destination", "delivered_to_customer"}
    in_transit = {"in_transit", "transit", "out_for_delivery", "arrived"}
    pending = {"pending", "info_received", "pre_transit", "created"}

    if status in delivered:
        return "Teslim Edildi"
    if status in in_transit:
        return "Yolda"
    if status in pending:
        return "Hazirlaniyor"
    return "Yolda"


def _ship24_event_date(event):
    return (
        event.get("datetime")
        or event.get("timestamp")
        or event.get("time")
        or event.get("date")
        or ""
    )


def _ship24_build_movements(events):
    movements = []
    for event in events or []:
        location = _ship24_format_location(event.get("location"))
        description = (
            event.get("description")
            or event.get("statusDescription")
            or event.get("status")
            or event.get("event")
            or ""
        )
        movements.append(
            {
                "date": _ship24_event_date(event) or "-",
                "location": location or "-",
                "description": description or "-",
            }
        )
    return movements


def _get_ship24_status(tracking_number, courier=None):
    if not _ship24_is_enabled():
        return None, "Ship24 disabled or missing API key"

    logger = _get_ship24_logger()
    courier = _normalize_courier_code(courier)

    data = None
    tracker_id = get_ship24_tracker_id(tracking_number)
    if tracker_id:
        data, error = _ship24_request("GET", f"/trackers/{tracker_id}/results")
        if error:
            data = None
            tracker_id = None

    if not tracker_id:
        tracker_id, error = _ship24_create_tracker(tracking_number, courier_code=courier)
        if error:
            logger.warning(
                "Ship24 tracker error: %s (tracking=%s, courier=%s)",
                error,
                tracking_number,
                courier,
            )
            return None, error
        set_ship24_tracker_id(tracking_number, tracker_id)

    if data is None:
        data, error = _ship24_request("GET", f"/trackers/{tracker_id}/results")
        if error:
            logger.warning(
                "Ship24 results error: %s (tracking=%s, courier=%s)",
                error,
                tracking_number,
                courier,
            )
            return None, error

    tracking = _ship24_extract_tracking(data)
    if not tracking:
        logger.warning("Ship24 tracking data missing (tracking=%s)", tracking_number)
        return None, "Tracking data missing"

    courier_info = tracking.get("courier") or {}
    if isinstance(courier_info, dict):
        courier_name = courier_info.get("name") or courier_info.get("code")
    else:
        courier_name = str(courier_info) if courier_info else None

    raw_status = (
        tracking.get("status")
        or (tracking.get("shipment") or {}).get("status")
        or ((tracking.get("shipment") or {}).get("delivery") or {}).get("status")
    )
    status = _ship24_map_status(raw_status)

    events = tracking.get("events")
    if not events:
        events = (tracking.get("shipment") or {}).get("events") or []

    movements = _ship24_build_movements(events)
    last_update = (
        tracking.get("lastUpdated")
        or (tracking.get("shipment") or {}).get("lastUpdated")
        or (movements[0]["date"] if movements else "")
        or "-"
    )

    return {
        "tracking_number": tracking_number,
        "courier": courier_name or courier or "Ship24",
        "status": status,
        "last_update": last_update,
        "movements": movements,
    }, None


def _get_shipment_status_mock(tracking_number, courier):
    return {
        "tracking_number": tracking_number,
        "courier": courier or "Sistem Ici Dagitim",
        "status": "Yolda",
        "last_update": "Bugun",
        "movements": [
            {
                "date": "Bugun",
                "location": "Transfer Merkezi",
                "description": "Kargo dagitim merkezine ulasti.",
            }
        ],
    }


def get_shipment_status(tracking_number, courier=None):
    logger = _get_ship24_logger()
    ship24_status, error = _get_ship24_status(tracking_number, courier)
    if ship24_status:
        ship24_status["source"] = "ship24"
        ship24_status["error"] = None
        return ship24_status

    mock_status = _get_shipment_status_mock(tracking_number, courier)
    mock_status["source"] = "mock"
    mock_status["error"] = error
    if error:
        logger.info(
            "Ship24 fallback to mock: tracking=%s courier=%s error=%s",
            tracking_number,
            courier,
            error,
        )
    return mock_status
