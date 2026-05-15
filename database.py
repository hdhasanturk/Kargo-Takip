import sqlite3
import hashlib
import random
import string
from datetime import datetime

DB_PATH = "kargo_takip.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'personel'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT UNIQUE NOT NULL,
            sender_name TEXT NOT NULL,
            sender_phone TEXT,
            sender_address TEXT,
            sender_city TEXT,
            receiver_name TEXT NOT NULL,
            receiver_phone TEXT,
            receiver_address TEXT,
            receiver_city TEXT,
            current_city TEXT DEFAULT 'Merkez',
            weight REAL DEFAULT 0,
            volume REAL DEFAULT 0,
            price REAL DEFAULT 0,
            payment_price REAL DEFAULT 0,
            status TEXT DEFAULT 'Hazirlaniyor',
            route TEXT DEFAULT '',
            created_date TEXT,
            last_update TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shipment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id INTEGER,
            tracking_number TEXT NOT NULL,
            status TEXT NOT NULL,
            location_city TEXT DEFAULT '',
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (shipment_id) REFERENCES shipments(id)
        )
    ''')

    _ensure_shipment_columns(cursor)

    conn.commit()
    conn.close()
    print("Veritabani olusturuldu.")


def _ensure_shipment_columns(cursor):
    cursor.execute("PRAGMA table_info(shipments)")
    existing = {row[1] for row in cursor.fetchall()}

    required_columns = {
        "delivery_type": "TEXT DEFAULT 'Adrese Teslim'",
        "shipment_note": "TEXT DEFAULT ''",
        "distance_km": "REAL DEFAULT 0",
        "desi": "REAL DEFAULT 0",
        "party_type": "TEXT DEFAULT 'gonderici'",
        "sender_county": "TEXT DEFAULT ''",
        "sender_neighborhood": "TEXT DEFAULT ''",
        "receiver_county": "TEXT DEFAULT ''",
        "receiver_neighborhood": "TEXT DEFAULT ''",
        "courier": "TEXT DEFAULT ''",
        "real_tracking_number": "TEXT DEFAULT ''",
        "ship24_tracker_id": "TEXT DEFAULT ''",
        "parcels_json": "TEXT DEFAULT ''",
        "estimated_delivery_date": "TEXT DEFAULT ''",
    }

    for column_name, column_type in required_columns.items():
        if column_name not in existing:
            cursor.execute(f"ALTER TABLE shipments ADD COLUMN {column_name} {column_type}")


def generate_tracking_number():
    chars = string.digits
    return ''.join(random.choice(chars) for _ in range(12))


def _tracking_number_exists(cursor, tracking_number):
    cursor.execute(
        "SELECT 1 FROM shipments WHERE tracking_number = ? LIMIT 1",
        (tracking_number,),
    )
    return cursor.fetchone() is not None


def create_user(username, password, name, role="personel"):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, name, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, name, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "username": username, "name": name, "role": role}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def ensure_default_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    existing_admin = cursor.fetchone()
    conn.close()

    if existing_admin:
        return False

    create_user("admin", "123456", "Yonetici", role="admin")
    return True


def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] == password_hash:
            return dict(user)
    return None


def add_shipment(sender_name, sender_phone, sender_address, sender_city,
                 receiver_name, receiver_phone, receiver_address, receiver_city,
                 receiver_county, receiver_neighborhood,
                  weight, volume, price, payment_price, route, delivery_type="Adrese Teslim",
                  shipment_note="", distance_km=0, desi=0, party_type="gonderici",
                  sender_county="", sender_neighborhood="", courier="", real_tracking_number="",
                  ship24_tracker_id="", parcels_json="", estimated_delivery_date=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        tracking_number = None
        for _ in range(20):
            candidate = generate_tracking_number()
            if not _tracking_number_exists(cursor, candidate):
                tracking_number = candidate
                break

        if not tracking_number:
            raise RuntimeError("Benzersiz takip numarasi uretilemedi.")

        cursor.execute(
            """INSERT INTO shipments 
               (tracking_number, sender_name, sender_phone, sender_address, sender_city,
                                receiver_name, receiver_phone, receiver_address, receiver_city, receiver_county, receiver_neighborhood,
                weight, volume, price, payment_price, status, route, created_date, last_update,
                     delivery_type, shipment_note, distance_km, desi, party_type, sender_county, sender_neighborhood,
                                          courier, real_tracking_number, ship24_tracker_id, parcels_json, estimated_delivery_date)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tracking_number, sender_name, sender_phone, sender_address, sender_city,
                         receiver_name, receiver_phone, receiver_address, receiver_city, receiver_county, receiver_neighborhood,
                         weight, volume, price, payment_price, "Hazirlaniyor", route, now, now,
                 delivery_type, shipment_note, distance_km, desi, party_type, sender_county, sender_neighborhood,
                                 courier, real_tracking_number, ship24_tracker_id, parcels_json, estimated_delivery_date)
        )
        conn.commit()
        insert_history(tracking_number, "Hazirlaniyor", sender_city, "Kargo kaydi olusturuldu.")
        return tracking_number
    finally:
        conn.close()


def get_all_shipments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipments ORDER BY created_date DESC")
    shipments = cursor.fetchall()
    conn.close()
    return [dict(s) for s in shipments]


def get_shipment_by_tracking(tracking_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipments WHERE tracking_number = ?", (tracking_number,))
    shipment = cursor.fetchone()
    conn.close()
    return dict(shipment) if shipment else None


def get_shipment_for_party(tracking_number, party_type, phone):
    if party_type not in ("gonderici", "alici"):
        return None

    phone_column = "sender_phone" if party_type == "gonderici" else "receiver_phone"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM shipments WHERE tracking_number = ? AND {phone_column} = ?",
        (tracking_number, phone),
    )
    shipment = cursor.fetchone()
    conn.close()
    return dict(shipment) if shipment else None


def get_ship24_tracker_id(tracking_number):
    if not tracking_number:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT ship24_tracker_id
           FROM shipments
           WHERE real_tracking_number = ? OR tracking_number = ?
           ORDER BY id DESC
           LIMIT 1""",
        (tracking_number, tracking_number),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    tracker_id = row["ship24_tracker_id"]
    return tracker_id if tracker_id else None


def set_ship24_tracker_id(tracking_number, tracker_id):
    if not tracking_number or not tracker_id:
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE shipments
           SET ship24_tracker_id = ?
           WHERE real_tracking_number = ? OR tracking_number = ?""",
        (tracker_id, tracking_number, tracking_number),
    )
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated


def get_shipment(shipment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
    shipment = cursor.fetchone()
    conn.close()
    return dict(shipment) if shipment else None


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, name, role FROM users ORDER BY id DESC")
    users = cursor.fetchall()
    conn.close()
    return [dict(u) for u in users]


def insert_history(tracking_number, status, location_city="", description=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM shipments WHERE tracking_number = ?",
        (tracking_number,)
    )
    shipment = cursor.fetchone()
    if not shipment:
        conn.close()
        return
    cursor.execute(
        "INSERT INTO shipment_history (shipment_id, tracking_number, status, location_city, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (shipment["id"], tracking_number, status, location_city, description, now)
    )
    conn.commit()
    conn.close()


def get_history(tracking_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM shipment_history WHERE tracking_number = ? ORDER BY created_at ASC",
        (tracking_number,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_shipment_location(tracking_number, current_city, status, route):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT status, current_city FROM shipments WHERE tracking_number = ?",
        (tracking_number,)
    )
    old = cursor.fetchone()

    cursor.execute(
        "UPDATE shipments SET current_city = ?, status = ?, route = ?, last_update = ? WHERE tracking_number = ?",
        (current_city, status, route, now, tracking_number)
    )
    conn.commit()
    conn.close()

    loc = current_city or "Merkez"
    desc = {
        "Hazirlaniyor": "Kargo kaydi olusturuldu.",
        "Yolda": f"Kargo {loc} bolgesine ulasti.",
        "Teslim Edildi": f"Kargo {loc}'de teslim edildi.",
    }.get(status, f"Durum guncellendi: {status}")

    insert_history(tracking_number, status, current_city, desc)

    if status == "Teslim Edildi":
        shipment = get_shipment_by_tracking(tracking_number)
        print(f"\n=== BILDIRIM ===")
        print(f"Kargo teslim edildi!")
        print(f"Takip No: {tracking_number}")
        print(f"Alici: {shipment['receiver_name']}")
        print(f"Alici Telefon: {shipment['receiver_phone']}")
        print(f"=================\n")


def delete_shipment(tracking_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shipments WHERE tracking_number = ?", (tracking_number,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
