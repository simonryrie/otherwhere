"""
GeoNames data loader for cities.
Loads city data from GeoNames dataset (local file, no API calls).
"""

import csv
import logging
from typing import List, Dict, Optional
from src.models.destination_schema import Continent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Map GeoNames continent codes to our Continent enum
CONTINENT_MAP = {
    'AF': Continent.AFRICA,
    'AS': Continent.ASIA,
    'EU': Continent.EUROPE,
    'NA': Continent.NORTH_AMERICA,
    'SA': Continent.SOUTH_AMERICA,
    'OC': Continent.OCEANIA,
}

# Map country codes to continents (will be populated from countryInfo.txt)
COUNTRY_TO_CONTINENT = {}


class GeoNamesLoader:
    """Loads city data from GeoNames dataset"""

    def __init__(self, cities_file: str = 'data/cities15000.txt', country_file: str = 'data/countryInfo.txt'):
        self.cities_file = cities_file
        self.country_file = country_file
        self._load_country_info()

    def _load_country_info(self):
        """Load country to continent mapping from countryInfo.txt"""
        logger.info("Loading country info...")

        with open(self.country_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Skip comments
                if line.startswith('#'):
                    continue

                parts = line.strip().split('\t')
                if len(parts) >= 9:
                    country_code = parts[0]  # ISO2 code
                    country_name = parts[4]  # Country name
                    continent_code = parts[8]  # Continent code

                    if continent_code in CONTINENT_MAP:
                        COUNTRY_TO_CONTINENT[country_code] = {
                            'continent': CONTINENT_MAP[continent_code],
                            'name': country_name
                        }

        logger.info(f"Loaded {len(COUNTRY_TO_CONTINENT)} country mappings")

    def load_cities(self, min_population: int = 15000, limit: Optional[int] = None) -> List[Dict]:
        """
        Load cities from GeoNames dataset.

        GeoNames format (tab-separated):
        0: geonameid
        1: name
        2: asciiname
        3: alternatenames
        4: latitude
        5: longitude
        6: feature class
        7: feature code
        8: country code
        9: cc2
        10: admin1 code
        11: admin2 code
        12: admin3 code
        13: admin4 code
        14: population
        15: elevation
        16: dem
        17: timezone
        18: modification date
        """
        logger.info(f"Loading cities from {self.cities_file}...")

        cities = []

        with open(self.cities_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')

            for row in reader:
                if len(row) < 19:
                    continue

                try:
                    population = int(row[14]) if row[14] else 0

                    # Filter by population
                    if population < min_population:
                        continue

                    country_code = row[8]

                    # Get continent from country code
                    country_info = COUNTRY_TO_CONTINENT.get(country_code)
                    if not country_info:
                        continue  # Skip if we can't determine continent

                    city = {
                        'geonameid': row[0],
                        'name': row[1],
                        'asciiname': row[2],
                        'lat': float(row[4]),
                        'lon': float(row[5]),
                        'country_code': country_code,
                        'country': country_info['name'],
                        'continent': country_info['continent'],
                        'population': population,
                        'elevation': int(row[15]) if row[15] else 0,
                        'timezone': row[17],
                        'type': 'city'
                    }

                    cities.append(city)

                    if limit and len(cities) >= limit:
                        break

                except (ValueError, IndexError) as e:
                    logger.debug(f"Skipping invalid row: {e}")
                    continue

        logger.info(f"Loaded {len(cities)} cities")
        return cities

    def get_diverse_cities(self, target: int = 400, max_per_country: int = 10) -> List[Dict]:
        """
        Get a diverse set of cities with better country representation.

        Strategy:
        1. Ensure smaller countries are represented (max 10 cities per country)
        2. Prioritize cities by population within each country
        3. Use round-robin to distribute across countries, not just big countries
        """
        # Load cities with moderate population threshold
        all_cities = self.load_cities(min_population=50000)

        # Group by country first
        by_country = {}
        for city in all_cities:
            country = city['country']
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(city)

        # For each country, limit to max_per_country cities (sorted by population)
        for country, cities in by_country.items():
            cities.sort(key=lambda c: c['population'], reverse=True)
            by_country[country] = cities[:max_per_country]

        # Group countries by continent
        countries_by_continent = {}
        for country, cities in by_country.items():
            if not cities:
                continue
            continent = cities[0]['continent']
            if continent not in countries_by_continent:
                countries_by_continent[continent] = []
            countries_by_continent[continent].append(country)

        # Distribute quota across continents
        result = []
        continent_quotas = {
            Continent.EUROPE: int(target * 0.25),      # 25%
            Continent.ASIA: int(target * 0.30),         # 30%
            Continent.NORTH_AMERICA: int(target * 0.15), # 15%
            Continent.SOUTH_AMERICA: int(target * 0.10), # 10%
            Continent.AFRICA: int(target * 0.12),       # 12%
            Continent.OCEANIA: int(target * 0.08),      # 8%
        }

        for continent, quota in continent_quotas.items():
            countries = countries_by_continent.get(continent, [])
            if not countries:
                continue

            # Round-robin selection across countries
            # This ensures smaller countries get representation
            selected = []
            country_indices = {country: 0 for country in countries}

            # Keep cycling through countries until we hit quota
            while len(selected) < quota:
                added_any = False
                for country in countries:
                    if country_indices[country] < len(by_country[country]):
                        selected.append(by_country[country][country_indices[country]])
                        country_indices[country] += 1
                        added_any = True

                        if len(selected) >= quota:
                            break

                # If we couldn't add any more cities, break
                if not added_any:
                    break

            result.extend(selected)

            # Count unique countries
            unique_countries = len(set(city['country'] for city in selected))
            logger.info(f"{continent.value}: {len(selected)} cities from {unique_countries} countries")

        total_countries = len(set(city['country'] for city in result))
        logger.info(f"Total selected: {len(result)} cities from {total_countries} countries")
        return result
