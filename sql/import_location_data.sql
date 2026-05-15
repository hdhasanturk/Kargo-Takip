PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS tmp_cities;
DROP TABLE IF EXISTS tmp_counties;
DROP TABLE IF EXISTS tmp_districts;
DROP TABLE IF EXISTS tmp_neighborhoods;

CREATE TEMP TABLE tmp_cities (
    city_name TEXT,
    city_value TEXT
);

INSERT INTO tmp_cities (city_name, city_value)
SELECT
    json_extract(city.value, '$.name') AS city_name,
    city.value AS city_value
FROM raw_json,
     json_each(raw_json.json) AS city;

CREATE TEMP TABLE tmp_counties (
    city_name TEXT,
    county_name TEXT,
    county_value TEXT
);

INSERT INTO tmp_counties (city_name, county_name, county_value)
SELECT
    tmp_cities.city_name,
    json_extract(county.value, '$.name') AS county_name,
    county.value AS county_value
FROM tmp_cities,
     json_each(tmp_cities.city_value, '$.counties') AS county;

CREATE TEMP TABLE tmp_districts (
    city_name TEXT,
    county_name TEXT,
    district_name TEXT,
    district_value TEXT
);

INSERT INTO tmp_districts (city_name, county_name, district_name, district_value)
SELECT
    tmp_counties.city_name,
    tmp_counties.county_name,
    json_extract(district.value, '$.name') AS district_name,
    district.value AS district_value
FROM tmp_counties,
     json_each(tmp_counties.county_value, '$.districts') AS district;

CREATE TEMP TABLE tmp_neighborhoods (
    city_name TEXT,
    county_name TEXT,
    district_name TEXT,
    neighborhood_name TEXT,
    neighborhood_code TEXT
);

INSERT INTO tmp_neighborhoods (city_name, county_name, district_name, neighborhood_name, neighborhood_code)
SELECT
    tmp_districts.city_name,
    tmp_districts.county_name,
    tmp_districts.district_name,
    json_extract(neighborhood.value, '$.name') AS neighborhood_name,
    json_extract(neighborhood.value, '$.code') AS neighborhood_code
FROM tmp_districts,
     json_each(tmp_districts.district_value, '$.neighborhoods') AS neighborhood;

INSERT OR IGNORE INTO cities (name)
SELECT DISTINCT city_name FROM tmp_cities;

INSERT OR IGNORE INTO counties (city_id, name)
SELECT
    cities.id,
    tmp_counties.county_name
FROM tmp_counties
JOIN cities ON cities.name = tmp_counties.city_name;

INSERT OR IGNORE INTO districts (county_id, name)
SELECT
    counties.id,
    tmp_districts.district_name
FROM tmp_districts
JOIN cities ON cities.name = tmp_districts.city_name
JOIN counties ON counties.name = tmp_districts.county_name
    AND counties.city_id = cities.id;

INSERT OR IGNORE INTO neighborhoods (district_id, name, code)
SELECT
    districts.id,
    tmp_neighborhoods.neighborhood_name,
    tmp_neighborhoods.neighborhood_code
FROM tmp_neighborhoods
JOIN cities ON cities.name = tmp_neighborhoods.city_name
JOIN counties ON counties.name = tmp_neighborhoods.county_name
    AND counties.city_id = cities.id
JOIN districts ON districts.name = tmp_neighborhoods.district_name
    AND districts.county_id = counties.id;

DROP TABLE IF EXISTS tmp_neighborhoods;
DROP TABLE IF EXISTS tmp_districts;
DROP TABLE IF EXISTS tmp_counties;
DROP TABLE IF EXISTS tmp_cities;
