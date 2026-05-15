import sqlite3

conn = sqlite3.connect("data/turkiye_locations.db")
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", c.fetchall())

for table_name in [row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
    c.execute(f"PRAGMA table_info({table_name})")
    print(f"\n{table_name} columns:", c.fetchall())
    c.execute(f"SELECT COUNT(*) FROM {table_name}")
    print(f"{table_name} count:", c.fetchone()[0])
    c.execute(f"SELECT * FROM {table_name} LIMIT 3")
    print(f"{table_name} sample:", c.fetchall())

conn.close()
