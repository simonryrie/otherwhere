"""
Wikidata fetcher for cities and tourist regions.
Single data source for all destinations.
"""

import logging
import time
from typing import List, Dict
import requests
from src.models.destination_schema import Continent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Map Wikidata country IDs to continents
COUNTRY_TO_CONTINENT = {
    # Europe
    'Q38': Continent.EUROPE,     # Italy
    'Q29': Continent.EUROPE,     # Spain
    'Q45': Continent.EUROPE,     # Portugal
    'Q142': Continent.EUROPE,    # France
    'Q31': Continent.EUROPE,     # Belgium
    'Q55': Continent.EUROPE,     # Netherlands
    'Q183': Continent.EUROPE,    # Germany
    'Q39': Continent.EUROPE,     # Switzerland
    'Q40': Continent.EUROPE,     # Austria
    'Q33': Continent.EUROPE,     # Finland
    'Q34': Continent.EUROPE,     # Sweden
    'Q20': Continent.EUROPE,     # Norway
    'Q35': Continent.EUROPE,     # Denmark
    'Q36': Continent.EUROPE,     # Poland
    'Q213': Continent.EUROPE,    # Czech Republic
    'Q28': Continent.EUROPE,     # Hungary
    'Q218': Continent.EUROPE,    # Romania
    'Q224': Continent.EUROPE,    # Croatia
    'Q41': Continent.EUROPE,     # Greece
    'Q229': Continent.EUROPE,    # Cyprus
    'Q145': Continent.EUROPE,    # United Kingdom
    'Q27': Continent.EUROPE,     # Ireland
    'Q221': Continent.EUROPE,    # North Macedonia
    'Q222': Continent.EUROPE,    # Albania
    'Q403': Continent.EUROPE,    # Serbia
    'Q211': Continent.EUROPE,    # Latvia
    'Q212': Continent.EUROPE,    # Ukraine
    'Q184': Continent.EUROPE,    # Belarus
    'Q37': Continent.EUROPE,     # Lithuania
    'Q191': Continent.EUROPE,    # Estonia
    'Q258': Continent.EUROPE,    # Malta
    'Q233': Continent.EUROPE,    # Malta

    # Asia
    'Q252': Continent.ASIA,      # Indonesia
    'Q869': Continent.ASIA,      # Thailand
    'Q928': Continent.ASIA,      # Philippines
    'Q833': Continent.ASIA,      # Malaysia
    'Q334': Continent.ASIA,      # Singapore
    'Q668': Continent.ASIA,      # India
    'Q17': Continent.ASIA,       # Japan
    'Q148': Continent.ASIA,      # China
    'Q884': Continent.ASIA,      # South Korea
    'Q881': Continent.ASIA,      # Vietnam
    'Q967': Continent.ASIA,      # Bhutan
    'Q837': Continent.ASIA,      # Nepal
    'Q851': Continent.ASIA,      # Saudi Arabia
    'Q878': Continent.ASIA,      # UAE
    'Q846': Continent.ASIA,      # Qatar
    'Q398': Continent.ASIA,      # Bahrain
    'Q810': Continent.ASIA,      # Jordan
    'Q822': Continent.ASIA,      # Lebanon
    'Q865': Continent.ASIA,      # Taiwan
    'Q863': Continent.ASIA,      # Tajikistan
    'Q232': Continent.ASIA,      # Kazakhstan
    'Q854': Continent.ASIA,      # Sri Lanka
    'Q889': Continent.ASIA,      # Afghanistan
    'Q843': Continent.ASIA,      # Pakistan
    'Q874': Continent.ASIA,      # Turkmenistan
    'Q424': Continent.ASIA,      # Cambodia
    'Q819': Continent.ASIA,      # Laos
    'Q836': Continent.ASIA,      # Myanmar
    'Q711': Continent.ASIA,      # Mongolia
    'Q423': Continent.ASIA,      # North Korea

    # North America
    'Q30': Continent.NORTH_AMERICA,   # USA
    'Q16': Continent.NORTH_AMERICA,   # Canada
    'Q96': Continent.NORTH_AMERICA,   # Mexico
    'Q241': Continent.NORTH_AMERICA,  # Cuba
    'Q792': Continent.NORTH_AMERICA,  # El Salvador
    'Q774': Continent.NORTH_AMERICA,  # Guatemala
    'Q778': Continent.NORTH_AMERICA,  # Bahamas
    'Q766': Continent.NORTH_AMERICA,  # Jamaica
    'Q790': Continent.NORTH_AMERICA,  # Haiti
    'Q786': Continent.NORTH_AMERICA,  # Dominican Republic
    'Q800': Continent.NORTH_AMERICA,  # Costa Rica
    'Q804': Continent.NORTH_AMERICA,  # Panama
    'Q811': Continent.NORTH_AMERICA,  # Nicaragua
    'Q783': Continent.NORTH_AMERICA,  # Honduras
    'Q242': Continent.NORTH_AMERICA,  # Belize

    # South America
    'Q155': Continent.SOUTH_AMERICA,  # Brazil
    'Q739': Continent.SOUTH_AMERICA,  # Colombia
    'Q717': Continent.SOUTH_AMERICA,  # Venezuela
    'Q419': Continent.SOUTH_AMERICA,  # Peru
    'Q298': Continent.SOUTH_AMERICA,  # Chile
    'Q414': Continent.SOUTH_AMERICA,  # Argentina
    'Q736': Continent.SOUTH_AMERICA,  # Ecuador
    'Q750': Continent.SOUTH_AMERICA,  # Bolivia
    'Q77': Continent.SOUTH_AMERICA,   # Uruguay
    'Q734': Continent.SOUTH_AMERICA,  # Guyana
    'Q730': Continent.SOUTH_AMERICA,  # Suriname
    'Q774': Continent.SOUTH_AMERICA,  # Paraguay

    # Africa
    'Q1033': Continent.AFRICA,   # Nigeria
    'Q1013': Continent.AFRICA,   # Ivory Coast
    'Q1028': Continent.AFRICA,   # Morocco
    'Q79': Continent.AFRICA,     # Egypt
    'Q1049': Continent.AFRICA,   # Sudan
    'Q1037': Continent.AFRICA,   # Rwanda
    'Q1019': Continent.AFRICA,   # Madagascar
    'Q1025': Continent.AFRICA,   # Mauritius
    'Q1042': Continent.AFRICA,   # Seychelles
    'Q1041': Continent.AFRICA,   # Senegal
    'Q1027': Continent.AFRICA,   # Mauritania
    'Q1036': Continent.AFRICA,   # Uganda
    'Q114': Continent.AFRICA,    # Kenya
    'Q924': Continent.AFRICA,    # Tanzania
    'Q948': Continent.AFRICA,    # Tunisia
    'Q977': Continent.AFRICA,    # Ghana
    'Q258': Continent.AFRICA,    # South Africa
    'Q1000': Continent.AFRICA,   # Angola
    'Q1005': Continent.AFRICA,   # Gambia
    'Q1007': Continent.AFRICA,   # Guinea
    'Q1014': Continent.AFRICA,   # Liberia
    'Q1020': Continent.AFRICA,   # Malawi
    'Q1029': Continent.AFRICA,   # Morocco
    'Q1030': Continent.AFRICA,   # Namibia
    'Q1032': Continent.AFRICA,   # Niger
    'Q117': Continent.AFRICA,    # Ghana
    'Q1039': Continent.AFRICA,   # São Tomé and Príncipe
    'Q1044': Continent.AFRICA,   # Sierra Leone
    'Q1050': Continent.AFRICA,   # Eswatini
    'Q954': Continent.AFRICA,    # Zimbabwe
    'Q953': Continent.AFRICA,    # Zambia
    'Q1009': Continent.AFRICA,   # Cameroon
    'Q963': Continent.AFRICA,    # Botswana
    'Q912': Continent.AFRICA,    # Mali
    'Q1007': Continent.AFRICA,   # Guinea-Bissau

    # Oceania
    'Q408': Continent.OCEANIA,   # Australia
    'Q664': Continent.OCEANIA,   # New Zealand
    'Q691': Continent.OCEANIA,   # Papua New Guinea
    'Q712': Continent.OCEANIA,   # Fiji
    'Q678': Continent.OCEANIA,   # Tonga
    'Q683': Continent.OCEANIA,   # Samoa
    'Q709': Continent.OCEANIA,   # Marshall Islands
    'Q692': Continent.OCEANIA,   # Palau
    'Q710': Continent.OCEANIA,   # Kiribati
    'Q697': Continent.OCEANIA,   # Nauru
    'Q686': Continent.OCEANIA,   # Vanuatu
    'Q678': Continent.OCEANIA,   # Tonga
}


class WikidataDestinationFetcher:
    """Fetches cities and regions from Wikidata"""

    SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OtherwhereTravelApp/1.0 (Educational project)'
        })

    def fetch_cities(self, min_population: int = 50000, limit: int = 400) -> List[Dict]:
        """Fetch cities from Wikidata"""
        logger.info(f"Fetching cities with population >= {min_population}...")

        query = f"""
        SELECT DISTINCT ?city ?cityLabel ?countryLabel ?country ?lat ?lon ?population WHERE {{
          ?city wdt:P31/wdt:P279* wd:Q515 .  # Instance of city
          ?city wdt:P17 ?country .
          ?city wdt:P625 ?coords .
          ?city wdt:P1082 ?population .

          FILTER(?population >= {min_population})

          BIND(geof:latitude(?coords) AS ?lat)
          BIND(geof:longitude(?coords) AS ?lon)

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        ORDER BY DESC(?population)
        LIMIT {limit}
        """

        return self._execute_query(query, 'city')

    def fetch_regions(self, limit: int = 100) -> List[Dict]:
        """Fetch tourist regions from Wikidata"""
        logger.info("Fetching tourist regions...")

        query = f"""
        SELECT DISTINCT ?region ?regionLabel ?countryLabel ?country ?lat ?lon ?population WHERE {{
          VALUES ?type {{
            wd:Q1799794    # tourist region
            wd:Q1620908    # historical region (famous ones)
          }}

          ?region wdt:P31 ?type .
          ?region wdt:P17 ?country .
          ?region wdt:P625 ?coords .

          # Must have English Wikipedia article (indicates notability)
          ?article schema:about ?region .
          ?article schema:isPartOf <https://en.wikipedia.org/> .

          OPTIONAL {{ ?region wdt:P1082 ?population . }}

          BIND(geof:latitude(?coords) AS ?lat)
          BIND(geof:longitude(?coords) AS ?lon)

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """

        return self._execute_query(query, 'region')

    def _execute_query(self, query: str, dest_type: str) -> List[Dict]:
        """Execute SPARQL query and parse results"""
        try:
            response = self.session.get(
                self.SPARQL_ENDPOINT,
                params={'query': query, 'format': 'json'},
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            destinations = []
            seen_names = set()

            for item in data['results']['bindings']:
                try:
                    name = item['cityLabel']['value'] if 'cityLabel' in item else item['regionLabel']['value']

                    # Skip duplicates
                    if name in seen_names:
                        continue
                    seen_names.add(name)

                    # Get country Wikidata ID
                    country_uri = item['country']['value']
                    country_id = country_uri.split('/')[-1]

                    # Map to continent
                    continent = COUNTRY_TO_CONTINENT.get(country_id)
                    if not continent:
                        logger.debug(f"Skipping {name}: unknown country {country_id}")
                        continue

                    dest = {
                        'name': name,
                        'lat': float(item['lat']['value']),
                        'lon': float(item['lon']['value']),
                        'country': item.get('countryLabel', {}).get('value', 'Unknown'),
                        'continent': continent,
                        'population': int(item['population']['value']) if 'population' in item else 0,
                        'type': dest_type
                    }

                    destinations.append(dest)

                except (KeyError, ValueError) as e:
                    logger.debug(f"Skipping destination due to error: {e}")
                    continue

            logger.info(f"Fetched {len(destinations)} {dest_type}s from Wikidata")

            # Respectful delay
            time.sleep(2)

            return destinations

        except Exception as e:
            logger.error(f"Failed to fetch {dest_type}s from Wikidata: {e}")
            return []

    def fetch_all_destinations(self, cities_limit: int = 400, regions_limit: int = 100) -> List[Dict]:
        """Fetch both cities and regions"""
        logger.info("Fetching all destinations from Wikidata...")

        cities = self.fetch_cities(min_population=50000, limit=cities_limit)
        regions = self.fetch_regions(limit=regions_limit)

        all_destinations = cities + regions

        logger.info(f"Total destinations fetched: {len(all_destinations)} ({len(cities)} cities + {len(regions)} regions)")

        return all_destinations
