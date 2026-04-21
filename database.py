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
        "sender_district": "TEXT DEFAULT ''",
        "sender_neighborhood": "TEXT DEFAULT ''",
    }

    for column_name, column_type in required_columns.items():
        if column_name not in existing:
            cursor.execute(f"ALTER TABLE shipments ADD COLUMN {column_name} {column_type}")


def generate_tracking_number():
    chars = string.digits
    return ''.join(random.choice(chars) for _ in range(12))


def create_user(username, password, name):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, name) VALUES (?, ?, ?)",
            (username, password_hash, name)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "username": username, "name": name}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


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
                 weight, volume, price, payment_price, route, delivery_type="Adrese Teslim",
                 shipment_note="", distance_km=0, desi=0, party_type="gonderici",
                 sender_district="", sender_neighborhood=""):
    tracking_number = generate_tracking_number()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO shipments 
           (tracking_number, sender_name, sender_phone, sender_address, sender_city,
            receiver_name, receiver_phone, receiver_address, receiver_city,
            weight, volume, price, payment_price, status, route, created_date, last_update,
            delivery_type, shipment_note, distance_km, desi, party_type, sender_district, sender_neighborhood)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (tracking_number, sender_name, sender_phone, sender_address, sender_city,
         receiver_name, receiver_phone, receiver_address, receiver_city,
         weight, volume, price, payment_price, "Hazirlaniyor", route, now, now,
         delivery_type, shipment_note, distance_km, desi, party_type, sender_district, sender_neighborhood)
    )
    conn.commit()
    conn.close()
    return tracking_number


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


def update_shipment_location(tracking_number, current_city, status, route):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE shipments SET current_city = ?, status = ?, route = ?, last_update = ? WHERE tracking_number = ?",
        (current_city, status, route, now, tracking_number)
    )
    conn.commit()
    conn.close()
    
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
