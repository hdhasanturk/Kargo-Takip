PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS counties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    UNIQUE(city_id, name)
);

CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    county_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (county_id) REFERENCES counties(id) ON DELETE CASCADE,
    UNIQUE(county_id, name)
);

CREATE TABLE IF NOT EXISTS neighborhoods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code TEXT,
    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
    UNIQUE(district_id, name, code)
);

CREATE INDEX IF NOT EXISTS idx_counties_city_id ON counties(city_id);
CREATE INDEX IF NOT EXISTS idx_districts_county_id ON districts(county_id);
CREATE INDEX IF NOT EXISTS idx_neighborhoods_district_id ON neighborhoods(district_id);
