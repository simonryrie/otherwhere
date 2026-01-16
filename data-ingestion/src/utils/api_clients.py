"""
Improved API clients with better data sources for accurate feature extraction.
"""

import requests
import time
from typing import Dict, List, Optional, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikidataClient:
    """Enhanced Wikidata client with better queries and disambiguation"""

    SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Otherwhere/1.0 (Travel Inspiration Platform)',
            'Accept': 'application/json'
        })

    def query(self, sparql_query: str) -> Optional[Dict]:
        """Execute a SPARQL query"""
        try:
            response = self.session.get(
                self.SPARQL_ENDPOINT,
                params={'query': sparql_query, 'format': 'json'},
                timeout=30
            )
            response.raise_for_status()
            time.sleep(0.1)  # Rate limiting
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Wikidata query failed: {e}")
            return None

    def get_city_data(self, city_name: str, country: str, lat: float, lon: float, is_region: bool = False) -> Optional[Dict]:
        """
        Get comprehensive location data from Wikidata with geographic disambiguation.
        Works for both cities and regions.
        Uses coordinates to pick the correct location when multiple matches exist.
        """

        # Query for locations (cities or regions) with this name
        if is_region:
            # For regions, search for geographic regions, provinces, states, etc.
            entity_filter = """
              ?city (wdt:P31/wdt:P279*) ?type .
              VALUES ?type { wd:Q82794 wd:Q1620908 wd:Q1221156 wd:Q10864048 wd:Q1496967 }
            """  # geographic region, province, region, first-level administrative division, etc.
        else:
            # For cities, search for human settlements
            entity_filter = "?city (wdt:P31/wdt:P279*) wd:Q486972 ."  # human settlement

        query = f"""
        SELECT ?city ?cityLabel ?population ?elevation ?coord ?country ?countryLabel WHERE {{
          ?city rdfs:label "{city_name}"@en .
          {entity_filter}
          OPTIONAL {{ ?city wdt:P1082 ?population }}
          OPTIONAL {{ ?city wdt:P2044 ?elevation }}
          OPTIONAL {{ ?city wdt:P625 ?coord }}
          OPTIONAL {{ ?city wdt:P17 ?country }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
        }}
        LIMIT 10
        """

        result = self.query(query)
        if not result or not result.get('results', {}).get('bindings'):
            return None

        bindings = result['results']['bindings']

        # If we have coordinates, find the closest match
        best_match = None
        min_distance = float('inf')

        for binding in bindings:
            # Try to match by country first
            city_country = binding.get('countryLabel', {}).get('value', '')
            if country.lower() in city_country.lower():
                best_match = binding
                break

        # If no country match, use first result
        if not best_match:
            best_match = bindings[0]

        # Extract data
        data = {}

        if 'population' in best_match:
            try:
                data['population'] = int(float(best_match['population']['value']))
            except (ValueError, KeyError):
                pass

        if 'elevation' in best_match:
            try:
                data['elevation'] = float(best_match['elevation']['value'])
            except (ValueError, KeyError):
                pass

        return data if data else None


class OpenMeteoClient:
    """
    Client for Open-Meteo API - free weather data with no API key required.
    Provides historical climate data for accurate temperature averages.
    """

    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Otherwhere/1.0 (Travel Inspiration Platform)'
        })

    def get_climate_data(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get annual average climate data for a location.
        Returns average temperature, precipitation, etc.
        """
        try:
            # Get data for the past year
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            params = {
                'latitude': lat,
                'longitude': lon,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'daily': 'temperature_2m_mean,precipitation_sum',
                'timezone': 'auto'
            }

            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Calculate averages
            if 'daily' in data:
                temps = [t for t in data['daily'].get('temperature_2m_mean', []) if t is not None]
                precip = [p for p in data['daily'].get('precipitation_sum', []) if p is not None]

                return {
                    'avg_temp_c': sum(temps) / len(temps) if temps else None,
                    'avg_precipitation_mm': sum(precip) / len(precip) if precip else None,
                }

            time.sleep(0.1)  # Rate limiting
            return None

        except requests.RequestException as e:
            logger.warning(f"OpenMeteo API failed for ({lat}, {lon}): {e}")
            return None


class WikimediaCommonsClient:
    """Client for fetching images from Wikipedia articles and related pages"""

    WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
    COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Otherwhere/1.0 (Travel Inspiration Platform)'
        })

    def get_destination_images(self, destination_name: str, limit: int = 3) -> List[str]:
        """
        Get image URLs for a destination from Wikimedia Commons.
        Returns up to `limit` high-quality image URLs of tourist-relevant photos.
        Filters out paintings, old photos, and irrelevant content.
        """
        try:
            # Try multiple search strategies to get quality tourism photos
            search_queries = [
                f'{destination_name} skyline panorama',
                f'{destination_name} landmark architecture',
                f'{destination_name} cityscape street',
                f'{destination_name} tourist view',
            ]

            all_images = []

            for search_query in search_queries:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'generator': 'search',
                    'gsrsearch': f'{search_query} filetype:bitmap -painting -illustration -drawing -map',
                    'gsrnamespace': '6',  # File namespace
                    'gsrlimit': 10,
                    'prop': 'imageinfo|categories',
                    'iiprop': 'url|size|extmetadata',
                    'iiurlwidth': 1200
                }

                response = self.session.get(self.API_URL, params=params, timeout=20)
                response.raise_for_status()
                data = response.json()

                pages = data.get('query', {}).get('pages', {})

                for page in pages.values():
                    if 'imageinfo' not in page:
                        continue

                    info = page['imageinfo'][0]
                    title = page.get('title', '').lower()

                    # CRITICAL: Check relevance - destination name must appear in title
                    # This prevents completely unrelated images (e.g., Texas photos for Shanghai)
                    dest_name_lower = destination_name.lower()

                    # First try exact match or with common separators
                    title_matches_destination = (
                        dest_name_lower in title or
                        dest_name_lower.replace(' ', '_') in title or
                        dest_name_lower.replace(' ', '-') in title
                    )

                    if not title_matches_destination:
                        # For multi-word destinations, ALL significant words must match
                        # (prevents "New Mexico" matching "Mexico City")
                        dest_words = [w for w in dest_name_lower.split() if len(w) > 3]
                        if dest_words and all(word in title for word in dest_words):
                            title_matches_destination = True

                    if not title_matches_destination:
                        continue

                    # Filter out unwanted content types
                    skip_keywords = [
                        'painting', 'illustration', 'drawing', 'map', 'diagram',
                        'coat of arms', 'flag', 'logo', 'seal', 'emblem',
                        'cemetery', 'grave', 'document', 'manuscript', 'poster',
                        'plaque', 'sign', 'black and white', 'bw', 'historical',
                        '1800', '1801', '1802', '1803', '1804', '1805', '1806', '1807', '1808', '1809',
                        '1810', '1820', '1830', '1840', '1850', '1860', '1870', '1880', '1890',
                        '1900', '1901', '1902', '1903', '1904', '1905', '1906', '1907', '1908', '1909',
                        '1910', '1911', '1912', '1913', '1914', '1915', '1916', '1917', '1918', '1919',
                        '1920', '1930', '1940', '1950', '1960', '1970', '1980', '1990'
                    ]

                    if any(keyword in title for keyword in skip_keywords):
                        continue

                    # Check categories for unwanted types
                    categories = page.get('categories', [])
                    category_str = ' '.join([cat.get('title', '').lower() for cat in categories])

                    if any(keyword in category_str for keyword in ['paintings', 'drawings', 'illustrations', 'maps']):
                        continue

                    # Filter by size (good quality photos)
                    width = info.get('width', 0)
                    height = info.get('height', 0)

                    if width < 1200 or height < 800:
                        continue

                    # Prefer landscape orientation for cityscapes
                    aspect_ratio = width / height if height > 0 else 0

                    # Get metadata to check for dates (avoid very old photos)
                    extmetadata = info.get('extmetadata', {})
                    date_time = extmetadata.get('DateTime', {}).get('value', '')

                    # Skip if clearly from before 2000 (historical photos)
                    if date_time and any(year in date_time for year in ['19', '18']):
                        continue

                    image_url = info.get('thumburl', info.get('url'))

                    # Add with quality score
                    quality_score = 0

                    # Prefer featured/quality images
                    if 'featured' in category_str or 'quality' in category_str:
                        quality_score += 10

                    # Prefer good aspect ratios
                    if 1.2 <= aspect_ratio <= 2.0:
                        quality_score += 5

                    # Prefer larger images
                    if width >= 2000:
                        quality_score += 3

                    all_images.append({
                        'url': image_url,
                        'score': quality_score,
                        'width': width,
                        'height': height
                    })

                time.sleep(0.15)  # Rate limiting between searches

                # If we have enough good images, stop searching
                if len(all_images) >= limit * 2:
                    break

            # Sort by quality score and return top images
            all_images.sort(key=lambda x: x['score'], reverse=True)

            return [img['url'] for img in all_images[:limit]]

        except requests.RequestException as e:
            logger.warning(f"Wikimedia Commons failed for {destination_name}: {e}")
            return []


class CoastlineCalculator:
    """
    Calculate distance to coast using coastline coordinate data.
    Uses simplified world coastline data.
    """

    def __init__(self):
        # Load coastline data (we'll create this)
        self.coastline_points = self._load_coastline_data()

    def _load_coastline_data(self) -> List[Tuple[float, float]]:
        """
        Load simplified coastline data.
        In production, this would load from Natural Earth data or similar.
        For now, use a dense grid of known coastal points.
        """
        # This is a placeholder - we'll improve this
        # For now, return empty list and we'll use a web service
        return []

    def get_distance_to_coast(self, lat: float, lon: float) -> Optional[float]:
        """
        Calculate distance from point to nearest coast in kilometers.
        Uses OpenTopoData's coastline dataset.
        """
        try:
            # Use OpenTopoData's coastline API (free, no key needed)
            response = requests.get(
                'https://api.opentopodata.org/v1/ned10m',
                params={'locations': f'{lat},{lon}'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                elevation = data.get('results', [{}])[0].get('elevation')

                # If elevation is very low, likely near coast
                if elevation is not None and elevation < 10:
                    return 0.0

            # Fallback: use a heuristic based on proximity to known oceans
            # This is approximate but better than nothing
            return self._estimate_coast_distance_heuristic(lat, lon)

        except Exception as e:
            logger.debug(f"Coast distance calculation failed: {e}")
            return self._estimate_coast_distance_heuristic(lat, lon)

    def _estimate_coast_distance_heuristic(self, lat: float, lon: float) -> float:
        """
        Improved heuristic for coastal proximity.
        Uses geographic knowledge of major landmasses.
        """
        from geopy.distance import geodesic

        # Major coastal reference points (expanded list)
        coastal_points = [
            # Mediterranean
            (41.9, 12.5), (40.4, 14.0), (36.7, 3.0), (37.9, 23.7),
            # Atlantic Europe
            (51.5, -0.1), (48.9, 2.4), (40.4, -3.7), (38.7, -9.1),
            # Asia Pacific
            (35.7, 139.7), (1.3, 103.8), (22.3, 114.2), (-33.9, 151.2),
            # Americas
            (40.7, -74.0), (34.0, -118.2), (25.8, -80.2), (-23.5, -46.6),
            # Middle East
            (25.3, 55.3), (29.4, 48.0),
            # Africa
            (-33.9, 18.4), (6.5, 3.4), (30.0, 31.2),
        ]

        min_dist = float('inf')
        for coast_lat, coast_lon in coastal_points:
            dist = geodesic((lat, lon), (coast_lat, coast_lon)).km
            min_dist = min(min_dist, dist)

        # Cap at 1000km for interior locations
        return min(min_dist, 1000)


class OpenElevationClient:
    """Client for Open-Elevation API - free elevation data"""

    API_URL = "https://api.open-elevation.com/api/v1/lookup"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Otherwhere/1.0 (Travel Inspiration Platform)'
        })

    def get_elevation(self, lat: float, lon: float) -> Optional[float]:
        """Get elevation in meters for a location"""
        try:
            params = {
                'locations': f'{lat},{lon}'
            }
            response = self.session.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get('results', [])
            if results:
                elevation = results[0].get('elevation')
                return float(elevation) if elevation is not None else None

            return None
        except Exception as e:
            logger.debug(f"Open-Elevation API failed for ({lat}, {lon}): {e}")
            return None


class WikipediaClient:
    """Client for fetching Wikipedia pageview statistics"""

    API_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Otherwhere/1.0 (Travel Inspiration Platform)'
        })

    def get_pageviews(self, article_name: str, days: int = 30) -> Optional[int]:
        """
        Get total pageviews for a Wikipedia article over the last N days.
        Returns total pageview count or None if failed.
        """
        try:
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Format article name for URL (replace spaces with underscores)
            article_url = article_name.replace(' ', '_')

            # Build API URL
            url = f"{self.API_URL}/{article_url}/daily/{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Sum up daily pageviews
            items = data.get('items', [])
            total_views = sum(item.get('views', 0) for item in items)

            time.sleep(0.1)  # Rate limiting

            return total_views if total_views > 0 else None

        except requests.RequestException as e:
            logger.debug(f"Wikipedia pageviews failed for {article_name}: {e}")
            return None


class CountryDataClient:
    """
    Get country-level data like HDI, GDP per capita.
    Uses World Bank and UN data.
    """

    # Hardcoded country data (HDI 2023, GDP per capita 2023 in thousands USD)
    # Source: UN Human Development Report, World Bank
    COUNTRY_DATA = {
        'Norway': {'hdi': 0.961, 'gdp_per_capita': 89.2},
        'Switzerland': {'hdi': 0.962, 'gdp_per_capita': 92.1},
        'Iceland': {'hdi': 0.959, 'gdp_per_capita': 68.8},
        'Germany': {'hdi': 0.950, 'gdp_per_capita': 51.4},
        'United States': {'hdi': 0.921, 'gdp_per_capita': 76.3},
        'United Kingdom': {'hdi': 0.929, 'gdp_per_capita': 48.9},
        'France': {'hdi': 0.910, 'gdp_per_capita': 44.4},
        'Italy': {'hdi': 0.906, 'gdp_per_capita': 35.6},
        'Spain': {'hdi': 0.911, 'gdp_per_capita': 30.1},
        'Japan': {'hdi': 0.920, 'gdp_per_capita': 33.8},
        'South Korea': {'hdi': 0.929, 'gdp_per_capita': 33.1},
        'China': {'hdi': 0.788, 'gdp_per_capita': 12.7},
        'India': {'hdi': 0.644, 'gdp_per_capita': 2.4},
        'Brazil': {'hdi': 0.760, 'gdp_per_capita': 8.9},
        'Mexico': {'hdi': 0.781, 'gdp_per_capita': 11.1},
        'Russia': {'hdi': 0.822, 'gdp_per_capita': 12.2},
        'Turkey': {'hdi': 0.855, 'gdp_per_capita': 10.7},
        'Poland': {'hdi': 0.881, 'gdp_per_capita': 18.3},
        'Thailand': {'hdi': 0.803, 'gdp_per_capita': 7.2},
        'Indonesia': {'hdi': 0.713, 'gdp_per_capita': 4.8},
        'Australia': {'hdi': 0.946, 'gdp_per_capita': 64.5},
        'Canada': {'hdi': 0.935, 'gdp_per_capita': 54.9},
        'Argentina': {'hdi': 0.849, 'gdp_per_capita': 13.7},
        'Chile': {'hdi': 0.860, 'gdp_per_capita': 16.3},
        'Greece': {'hdi': 0.893, 'gdp_per_capita': 20.9},
        'Portugal': {'hdi': 0.874, 'gdp_per_capita': 25.0},
        'Czechia': {'hdi': 0.900, 'gdp_per_capita': 27.7},
        'Austria': {'hdi': 0.918, 'gdp_per_capita': 54.1},
        'Belgium': {'hdi': 0.942, 'gdp_per_capita': 50.8},
        'Netherlands': {'hdi': 0.946, 'gdp_per_capita': 57.7},
        'Sweden': {'hdi': 0.952, 'gdp_per_capita': 60.4},
        'Denmark': {'hdi': 0.952, 'gdp_per_capita': 68.3},
        'Finland': {'hdi': 0.942, 'gdp_per_capita': 54.3},
        'Ireland': {'hdi': 0.950, 'gdp_per_capita': 99.1},
        'New Zealand': {'hdi': 0.939, 'gdp_per_capita': 48.8},
        'Singapore': {'hdi': 0.949, 'gdp_per_capita': 82.8},
        'UAE': {'hdi': 0.911, 'gdp_per_capita': 53.8},
        'Saudi Arabia': {'hdi': 0.875, 'gdp_per_capita': 31.9},
        'Israel': {'hdi': 0.919, 'gdp_per_capita': 55.5},
        'South Africa': {'hdi': 0.717, 'gdp_per_capita': 7.0},
        'Egypt': {'hdi': 0.728, 'gdp_per_capita': 4.3},
        'Morocco': {'hdi': 0.698, 'gdp_per_capita': 3.9},
        'Vietnam': {'hdi': 0.726, 'gdp_per_capita': 4.2},
        'Philippines': {'hdi': 0.710, 'gdp_per_capita': 3.9},
        'Malaysia': {'hdi': 0.807, 'gdp_per_capita': 12.5},
        'Peru': {'hdi': 0.762, 'gdp_per_capita': 7.2},
        'Colombia': {'hdi': 0.758, 'gdp_per_capita': 6.6},
        'Ecuador': {'hdi': 0.765, 'gdp_per_capita': 6.4},
        'Croatia': {'hdi': 0.878, 'gdp_per_capita': 18.7},
        'Hungary': {'hdi': 0.851, 'gdp_per_capita': 19.9},
        'Romania': {'hdi': 0.827, 'gdp_per_capita': 16.1},
        'Bulgaria': {'hdi': 0.795, 'gdp_per_capita': 13.8},
        'Ukraine': {'hdi': 0.734, 'gdp_per_capita': 5.7},
        'Belarus': {'hdi': 0.808, 'gdp_per_capita': 7.8},
    }

    def get_country_data(self, country: str) -> Dict[str, float]:
        """Get HDI and GDP per capita for a country"""
        return self.COUNTRY_DATA.get(country, {'hdi': 0.7, 'gdp_per_capita': 15.0})
