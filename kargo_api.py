"""
Kargo Guzergah Sistemi - Mock API
Bu sistem sehirler arasi guzergahi hesaplar
"""

TURKISH_CITIES = [
    "Izmir", "Istanbul", "Ankara", "Antalya", "Bursa", "Eskisehir",
    "Konya", "Gaziantep", "Mersin", "Adana", "Diyarbakir", "Samsun",
    "Trabzon", "Erzurum", "Denizli", "Manisa", "Kocaeli", "Sakarya",
    "Aydin", "Mugla", "Hatay", "Kahramanmaras", "Corum", "Cankiri",
    "Afyonkarahisar", "Usak", "Kutahya", "Bilecik", "Bolu", "Duzce",
    "Edirne", "Tekirdag", "Kirklareli", "Balikesir", "Canakkale", "Nigde",
    "Aksaray", "Karaman", "Kirsehir", "Nevsehir", "Yozgat", "Sivas",
    "Kayseri", "Malatya", "Elazig", "Tunceli", "Bingol", "Mus", "Bitlis",
    "Van", "Agri", "Kars", "Ardahan", "Igdir", "Bayburt", "Gumushane",
    "Giresun", "Ordu", "Tokat", "Amasya", "Kirikkale", "Sanliurfa",
    "Mardin", "Batman", "Sirnak", "Siirt", "Hakkari", "Osmaniye",
    "Isparta", "Burdur", "Kastamonu", "Karabuk", "Bartin", "Zonguldak"
]

CITY_CONNECTIONS = {
    "Izmir": ["Manisa", "Aydin", "Denizli"],
    "Manisa": ["Izmir", "Usak", "Kutahya", "Bilecik"],
    "Aydin": ["Izmir", "Denizli", "Mugla"],
    "Denizli": ["Aydin", "Izmir", "Usak", "Afyonkarahisar", "Antalya"],
    "Mugla": ["Aydin", "Denizli", "Antalya"],
    "Usak": ["Manisa", "Kutahya", "Denizli", "Afyonkarahisar"],
    "Kutahya": ["Manisa", "Usak", "Bursa", "Eskisehir", "Afyonkarahisar"],
    "Afyonkarahisar": ["Usak", "Kutahya", "Konya", "Eskisehir", "Denizli"],
    "Eskisehir": ["Kutahya", "Bursa", "Bilecik", "Ankara", "Konya"],
    "Bursa": ["Kutahya", "Eskisehir", "Bilecik", "Istanbul", "Yalova"],
    "Bilecik": ["Bursa", "Eskisehir", "Kocaeli", "Ankara", "Kirsehir"],
    "Istanbul": ["Kocaeli", "Tekirdag", "Edirne"],
    "Kocaeli": ["Istanbul", "Bursa", "Sakarya", "Yalova"],
    "Sakarya": ["Kocaeli", "Duzce", "Bolu", "Bilecik"],
    "Duzce": ["Sakarya", "Bolu", "Zonguldak", "Bartin", "Karabuk"],
    "Bolu": ["Sakarya", "Duzce", "Ankara", "Eskisehir", "Kirsehir"],
    "Ankara": ["Eskisehir", "Bilecik", "Kirsehir", "Cankiri", "Kirikkale", "Konya", "Kırıkkale"],
    "Konya": ["Eskisehir", "Ankara", "Aksaray", "Karaman", "Isparta", "Antalya", "Afyonkarahisar"],
    "Aksaray": ["Konya", "Nevsehir", "Kirsehir", "Ankara"],
    "Nevsehir": ["Aksaray", "Kirsehir", "Niğde", "Kayseri"],
    "Kirsehir": ["Ankara", "Bilecik", "Cankiri", "Kırıkkale", "Nevsehir", "Yozgat"],
    "Cankiri": ["Ankara", "Kirsehir", "Bartin", "Karabuk", "Corum"],
    "Kirikkale": ["Ankara", "Kirsehir", "Yozgat", "Sivas", "Kayseri"],
    "Yozgat": ["Kirikkale", "Kirsehir", "Sivas", "Kayseri", "Corum", "Amasya"],
    "Sivas": ["Kirikkale", "Yozgat", "Kayseri", "Erzincan", "Giresun", "Ordu", "Amasya"],
    "Kayseri": ["Nevsehir", "Yozgat", "Sivas", "Kırıkkale", "Nigde", "Adana", "Kahramanmaras"],
    "Nigde": ["Nevsehir", "Kayseri", "Adana", "Aksaray", "Konya"],
    "Adana": ["Nigde", "Kayseri", "Kahramanmaras", "Osmaniye", "Mersin"],
    "Mersin": ["Antalya", "Konya", "Karaman", "Adana", "Nigde", "Osmaniye"],
    "Osmaniye": ["Adana", "Kahramanmaras", "Hatay", "Gaziantep", "Mersin"],
    "Kahramanmaras": ["Adana", "Sivas", "Kayseri", "Osmaniye", "Gaziantep", "Malatya", "Elazig"],
    "Gaziantep": ["Osmaniye", "Kahramanmaras", "Sanliurfa", "Adiyaman", "Kilis", "Hatay"],
    "Kilis": ["Gaziantep", "Hatay", "Sanliurfa"],
    "Hatay": ["Osmaniye", "Gaziantep", "Kilis", "Adana"],
    "Sanliurfa": ["Gaziantep", "Kilis", "Adiyaman", "Mardin", "Diyarbakir"],
    "Adiyaman": ["Sanliurfa", "Gaziantep", "Kahramanmaras", "Malatya", "Diyarbakir"],
    "Malatya": ["Kahramanmaras", "Adiyaman", "Elazig", "Tunceli", "Erzincan", "Sivas"],
    "Elazig": ["Malatya", "Tunceli", "Bingol", "Erzurum", "Erzincan"],
    "Tunceli": ["Elazig", "Erzincan", "Erzurum", "Bingol"],
    "Bingol": ["Elazig", "Tunceli", "Erzurum", "Mus", "Bitlis"],
    "Erzincan": ["Sivas", "Kirsehir", "Giresun", "Gumushane", "Erzurum", "Elazig", "Tunceli"],
    "Erzurum": ["Erzincan", "Gumushane", "Bayburt", "Ardahan", "Kars", "Agri", "Bitlis", "Mus", "Bingol", "Tunceli"],
    "Gumushane": ["Erzurum", "Bayburt", "Giresun", "Trabzon", "Erzincan"],
    "Bayburt": ["Erzurum", "Gumushane", "Giresun"],
    "Giresun": ["Gumushane", "Bayburt", "Trabzon", "Sivas", "Ordu", "Erzincan"],
    "Trabzon": ["Giresun", "Bayburt", "Rize", "Gumushane", "Erzurum"],
    "Rize": ["Trabzon", "Artvin", "Erzurum"],
    "Ordu": ["Giresun", "Sivas", "Tokat", "Amasya", "Corum"],
    "Tokat": ["Ordu", "Amasya", "Sivas", "Yozgat", "Kirsehir"],
    "Amasya": ["Ordu", "Tokat", "Yozgat", "Sivas", "Corum", "Cankiri"],
    "Corum": ["Amasya", "Yozgat", "Cankiri", "Bartin", "Karabuk", "Amasya"],
    "Bartin": ["Cankiri", "Corum", "Karabuk", "Zonguldak"],
    "Karabuk": ["Bartin", "Cankiri", "Corum", "Zonguldak", "Bolu", "Duzce"],
    "Zonguldak": ["Bartin", "Karabuk", "Bolu", "Duzce"],
    "Isparta": ["Antalya", "Konya", "Burdur", "Afyonkarahisar"],
    "Burdur": ["Antalya", "Isparta", "Denizli"],
    "Antalya": ["Burdur", "Isparta", "Konya", "Mersin", "Mugla", "Denizli"],
    "Karaman": ["Konya", "Mersin", "Aksaray"],
    "Mus": ["Bitlis", "Bingol", "Erzurum", "Agri", "Van"],
    "Bitlis": ["Mus", "Bingol", "Erzurum", "Van", "Batman", "Agri"],
    "Agri": ["Erzurum", "Mus", "Bitlis", "Van", "Kars", "Igdir"],
    "Van": ["Agri", "Bitlis", "Mus", "Hakkari", "Sirnak"],
    "Hakkari": ["Van", "Sirnak", "Cukurca", "Yuksekova"],
    "Sirnak": ["Van", "Hakkari", "Batman", "Mardin", "Siirt", "Cukurca"],
    "Batman": ["Sirnak", "Mardin", "Siirt", "Bitlis", "Mus"],
    "Mardin": ["Batman", "Sirnak", "Siirt", "Sanliurfa", "Diyarbakir"],
    "Siirt": ["Batman", "Mardin", "Sirnak", "Sirnak", "Hakkari"],
    "Kars": ["Erzurum", "Ardahan", "Igdir", "Agri"],
    "Ardahan": ["Erzurum", "Kars", "Artvin"],
    "Igdir": ["Kars", "Agri", "Erzurum"],
    "Artvin": ["Rize", "Ardahan", "Erzurum"],
    "Tekirdag": ["Istanbul", "Edirne", "Kirklareli"],
    "Edirne": ["Istanbul", "Tekirdag", "Kirklareli"],
    "Kirklareli": ["Istanbul", "Tekirdag", "Edirne"],
    "Balikesir": ["Canakkale", "Manisa", "Kutahya", "Bursa"],
    "Canakkale": ["Balikesir", "Bursa", "Yalova"],
    "Yalova": ["Istanbul", "Kocaeli", "Bursa", "Canakkale"],
    "Kırıkkale": ["Ankara", "Kirsehir", "Yozgat", "Sivas", "Kayseri"],
}


def get_cities():
    """Tum sehirleri dondurur"""
    return sorted(TURKISH_CITIES)


def calculate_route(start_city, end_city):
    """Iki sehir arasinda guzergahi hesaplar"""
    if start_city == end_city:
        return [start_city]
    
    start_city = start_city.strip()
    end_city = end_city.strip()
    
    visited = set()
    queue = [[start_city]]
    
    while queue:
        path = queue.pop(0)
        current = path[-1]
        
        if current == end_city:
            return path
        
        if current in visited:
            continue
        visited.add(current)
        
        if current in CITY_CONNECTIONS:
            for next_city in CITY_CONNECTIONS[current]:
                if next_city not in visited:
                    new_path = path + [next_city]
                    queue.append(new_path)
    
    return [start_city, end_city]


def get_next_city(route, current_city):
    """Mevcut sehirden bir sonraki sehri dondurur"""
    if current_city not in route:
        return route[-1] if route else current_city
    
    current_index = route.index(current_city)
    if current_index < len(route) - 1:
        return route[current_index + 1]
    return current_city


def get_route_progress(route, current_city):
    """Guzergah ilerlemesini dondurur"""
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
        "total_cities": len(route)
    }


def estimate_delivery_time(route):
    """Tahmini teslim suresini hesaplar (gun)"""
    if len(route) <= 2:
        return 1
    elif len(route) <= 4:
        return 2
    elif len(route) <= 6:
        return 3
    else:
        return 4


def format_route(route):
    """Guzergahi string olarak dondurur"""
    if not route:
        return ""
    return ",".join(route)


def calculate_distance_km(route):
    if not route or len(route) <= 1:
        return 0
    # Mock mesafe: her sehir gecisi ortalama 85 km
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

    base_price = 35
    billable_cost = billable * 18
    distance_cost = distance_km * 0.12
    delivery_surcharge = 15 if delivery_type == "Adrese Teslim" else 0

    total = round(base_price + billable_cost + distance_cost + delivery_surcharge, 2)
    return {
        "price": total,
        "desi": desi,
        "distance_km": distance_km,
        "billable_weight": round(billable, 2),
    }


def get_shipment_status(tracking_number, courier):
    """Detay ekrani icin basit mock kargo verisi dondurur."""
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
