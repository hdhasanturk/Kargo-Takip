import os
from kargo_api import LOCATION_DB_PATH, get_counties_by_city, get_neighborhoods_by_county, get_cities

print("DB path:", LOCATION_DB_PATH)
print("DB exists:", os.path.exists(LOCATION_DB_PATH))

cities = get_cities()
print("Cities count:", len(cities))
print("First city:", cities[0])

counties = get_counties_by_city(cities[0])
print(f"{cities[0]} counties:", len(counties), counties[:3] if counties else "EMPTY")

if counties:
    neighborhoods = get_neighborhoods_by_county(cities[0], counties[0])
    print(f"{counties[0]} mahalleler:", len(neighborhoods), neighborhoods[:3] if neighborhoods else "EMPTY")
