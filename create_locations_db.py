import json
import os
import sqlite3

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "turkiye_locations.db")
JSON_PATH = os.path.join("turkiye-city-county-district-neighborhood-main", "data.json")
SQL_CREATE_PATH = os.path.join("sql", "create_location_tables.sql")


def _load_sql_script(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"SQL script bulunamadi: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _normalize_city_list(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("cities", "data", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return list(data.values())

    return []


def _get_or_create_city(cursor, cache, name):
    if name in cache:
        return cache[name]

    cursor.execute("INSERT OR IGNORE INTO cities (name) VALUES (?)", (name,))
    cursor.execute("SELECT id FROM cities WHERE name = ?", (name,))
    city_id = cursor.fetchone()[0]
    cache[name] = city_id
    return city_id


def _get_or_create_county(cursor, cache, city_id, name):
    key = (city_id, name)
    if key in cache:
        return cache[key]

    cursor.execute(
        "INSERT OR IGNORE INTO counties (city_id, name) VALUES (?, ?)",
        (city_id, name),
    )
    cursor.execute(
        "SELECT id FROM counties WHERE city_id = ? AND name = ?",
        (city_id, name),
    )
    county_id = cursor.fetchone()[0]
    cache[key] = county_id
    return county_id


def _get_or_create_district(cursor, cache, county_id, name):
    key = (county_id, name)
    if key in cache:
        return cache[key]

    cursor.execute(
        "INSERT OR IGNORE INTO districts (county_id, name) VALUES (?, ?)",
        (county_id, name),
    )
    cursor.execute(
        "SELECT id FROM districts WHERE county_id = ? AND name = ?",
        (county_id, name),
    )
    district_id = cursor.fetchone()[0]
    cache[key] = district_id
    return district_id


def create_locations_db():
    os.makedirs(DB_DIR, exist_ok=True)

    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"JSON dosyasi bulunamadi: {JSON_PATH}")

    schema = _load_sql_script(SQL_CREATE_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.executescript(schema)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = _normalize_city_list(json.load(f))

    city_cache = {}
    county_cache = {}
    district_cache = {}

    for city in data:
        city_name = (city.get("name") or "").strip()
        if not city_name:
            continue

        city_id = _get_or_create_city(cursor, city_cache, city_name)
        for county in city.get("counties", []):
            county_name = (county.get("name") or "").strip()
            if not county_name:
                continue

            county_id = _get_or_create_county(cursor, county_cache, city_id, county_name)
            for district in county.get("districts", []):
                district_name = (district.get("name") or "").strip()
                if not district_name:
                    continue

                district_id = _get_or_create_district(cursor, district_cache, county_id, district_name)
                for neighborhood in district.get("neighborhoods", []):
                    neighborhood_name = (neighborhood.get("name") or "").strip()
                    if not neighborhood_name:
                        continue

                    neighborhood_code = neighborhood.get("code")
                    cursor.execute(
                        "INSERT OR IGNORE INTO neighborhoods (district_id, name, code) VALUES (?, ?, ?)",
                        (district_id, neighborhood_name, neighborhood_code),
                    )

    conn.commit()
    conn.close()

    print(f"Konum veritabani olusturuldu: {DB_PATH}")


if __name__ == "__main__":
    create_locations_db()
