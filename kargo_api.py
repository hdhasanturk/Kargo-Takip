"""
Kargo Guzergah Sistemi - Mock API
Bu sistem sehirler arasi guzergahi hesaplar.
"""

import json
from collections import deque
from pathlib import Path

from database import get_db_connection

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

LOCATION_DATA_PATH = (
    Path(__file__).resolve().parent
    / "turkiye-city-county-district-neighborhood-main"
    / "data.json"
)
_LOCATION_DATA = None
_LOCATION_INDEX = None


def _norm_city(value):
    return (value or "").strip().lower().translate(_CITY_REPLACE)


def _resolve_city_name(city):
    normalized = _norm_city(city)
    if normalized in CITY_ALIASES:
        return CITY_ALIASES[normalized]
    return (city or "").strip()


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


def get_cities():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM cities ORDER BY name")
        cities = [row[0] for row in cursor.fetchall()]
        conn.close()
        return cities if cities else sorted(TURKISH_CITIES)
    except Exception as e:
        print(f"Error in get_cities: {e}")
        return sorted(TURKISH_CITIES)


def get_counties_by_city(city):
    try:
        conn = get_db_connection()
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
        conn.close()
        return counties if counties else _default_counties_for_city(city)
    except Exception as e:
        print(f"Error in get_counties_by_city: {e}")
        return _default_counties_for_city(city)


def get_districts_by_county(city, county):
    try:
        conn = get_db_connection()
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
        conn.close()
        return districts if districts else _default_districts_for_county(county)
    except Exception as e:
        print(f"Error in get_districts_by_county: {e}")
        return _default_districts_for_county(county)


def get_neighborhoods_by_district(city, county, district):
    try:
        conn = get_db_connection()
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
        conn.close()
        return neighborhoods if neighborhoods else _default_neighborhoods_for_district(district)
    except Exception as e:
        print(f"Error in get_neighborhoods_by_district: {e}")
        return _default_neighborhoods_for_district(district)


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
    return (len(route) - 1) * 85


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


def get_shipment_status(tracking_number, courier):
    return {
        "tracking_number": tracking_number,
        "courier": courier,
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
