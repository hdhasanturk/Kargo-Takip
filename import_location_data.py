import sqlite3
import os

DB_PATH = "kargo_takip.db"
JSON_PATH = "turkiye-city-county-district-neighborhood-main/data.json"
SQL_CREATE_PATH = os.path.join("sql", "create_location_tables.sql")
SQL_IMPORT_PATH = os.path.join("sql", "import_location_data.sql")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _load_sql_script(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"SQL script bulunamadi: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def create_location_tables():
    script = _load_sql_script(SQL_CREATE_PATH)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executescript(script)
    conn.commit()
    conn.close()
    print("Konum tablolari olusturuldu.")

def import_data():
    if not os.path.exists(JSON_PATH):
        print(f"Hata: {JSON_PATH} dosyasi bulunamadi!")
        return

    script = _load_sql_script(SQL_IMPORT_PATH)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        json_text = f.read()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TEMP TABLE IF NOT EXISTS raw_json (json TEXT)")
    cursor.execute("DELETE FROM raw_json")
    cursor.execute("INSERT INTO raw_json (json) VALUES (?)", (json_text,))
    cursor.executescript(script)
    conn.commit()
    conn.close()
    print("Veriler basariyla aktarildi.")

def verify_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM cities")
    city_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM counties")
    county_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM districts")
    district_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM neighborhoods")
    neighborhood_count = cursor.fetchone()["count"]

    conn.close()

    print(f"Sehir sayisi: {city_count}")
    print(f"Ilce sayisi: {county_count}")
    print(f"Mahalle/bucak sayisi: {district_count}")
    print(f"Semt/sokak sayisi: {neighborhood_count}")

if __name__ == "__main__":
    print("Tablolar olusturuluyor...")
    create_location_tables()
    print("Veriler aktariliyor...")
    import_data()
    print("Dogrulaniyor...")
    verify_data()
    print("Islem tamamlandi.")
