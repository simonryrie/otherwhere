"""
Improved feature extraction using accurate data sources.
"""

import logging
import time
import math
from typing import Dict, Optional
from src.models.destination_schema import Destination, DestinationFeatures
from src.utils.api_clients import (
    WikidataClient,
    OpenMeteoClient,
    CountryDataClient,
    OpenElevationClient,
    WikipediaClient
)
from src.utils.coastal_checker import CoastalChecker
from src.fetchers.unsplash_images import UnsplashImageClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extracts features using accurate external data sources"""

    def __init__(self, unsplash_key: str = None):
        self.wikidata_client = WikidataClient()
        self.weather_client = OpenMeteoClient()
        self.wikipedia_client = WikipediaClient()
        self.image_client = UnsplashImageClient(access_key=unsplash_key)
        self.coastal_checker = CoastalChecker()
        self.country_data = CountryDataClient()
        self.elevation_client = OpenElevationClient()

    def extract_features(self, destination: Destination) -> Destination:
        """
        Extract all features for a destination using real data sources.
        Returns the destination object with populated features and images.
        """
        logger.info(f"Extracting features for {destination.name}...")

        features = DestinationFeatures()

        # Skip Wikidata for now (rate limiting issues)
        wikidata_props = {}

        # Get climate data from OpenMeteo
        climate_data = self._get_climate_data(destination)

        # Get Wikipedia pageviews
        pageviews = self.wikipedia_client.get_pageviews(destination.name)

        # Get country-level data
        country_info = self.country_data.get_country_data(destination.country)

        # Extract features
        features = self._extract_base_features(destination, wikidata_props, features)
        features = self._extract_climate_features(destination, climate_data, features)
        features = self._extract_geography_features(destination, wikidata_props, features)
        features = self._extract_activity_features(destination, features)
        features = self._extract_popularity_features(destination, pageviews, features)
        features = self._extract_development_features(destination, country_info, features)

        # Get images from Unsplash (6 diverse images)
        images, download_urls = self.image_client.get_destination_images(
            destination.name,
            destination.country,
            dest_type=destination.type.value,
            limit=6
        )

        # Update destination
        destination.features = features
        destination.images = images
        destination.image_download_urls = download_urls

        # Small delay to be respectful
        time.sleep(0.2)

        return destination

    def _get_wikidata_properties(self, dest: Destination) -> Dict:
        """Fetch relevant properties from Wikidata"""
        try:
            is_region = dest.type.value == 'region'
            data = self.wikidata_client.get_city_data(
                dest.name, dest.country, dest.location.lat, dest.location.lon,
                is_region=is_region
            )
            return data if data else {}
        except Exception as e:
            logger.warning(f"Failed to get Wikidata properties for {dest.name}: {e}")
            return {}

    def _get_climate_data(self, dest: Destination) -> Dict:
        """Fetch climate data from OpenMeteo"""
        try:
            data = self.weather_client.get_climate_data(
                dest.location.lat, dest.location.lon
            )
            return data if data else {}
        except Exception as e:
            logger.warning(f"Failed to get climate data for {dest.name}: {e}")
            return {}

    def _extract_base_features(self, dest: Destination, props: Dict, features: DestinationFeatures) -> DestinationFeatures:
        """Extract basic features (currently none without Wikidata)"""
        # Population and elevation removed - were from Wikidata which is disabled
        return features

    def _extract_climate_features(self, dest: Destination, climate: Dict, features: DestinationFeatures) -> DestinationFeatures:
        """Extract climate-related features from real weather data"""

        # Use actual temperature data from OpenMeteo
        if 'avg_temp_c' in climate and climate['avg_temp_c'] is not None:
            features.avg_temp_c = climate['avg_temp_c']
        else:
            # If API fails, use latitude-based estimation as last resort
            lat = abs(dest.location.lat)
            if lat < 23.5:  # Tropics
                features.avg_temp_c = 26
            elif lat < 40:  # Subtropics
                features.avg_temp_c = 18
            elif lat < 60:  # Temperate
                features.avg_temp_c = 10
            else:  # Polar
                features.avg_temp_c = 0

        return features

    def _extract_geography_features(self, dest: Destination, props: Dict, features: DestinationFeatures) -> DestinationFeatures:
        """Extract geographic features using real data"""
        lat, lon = dest.location.lat, dest.location.lon

        # Get elevation from Open-Elevation API
        elevation = self.elevation_client.get_elevation(lat, lon)

        # Check if coastal using elevation data
        is_coastal = self.coastal_checker.is_coastal(
            lat, lon,
            city_name=dest.name,
            country=dest.country,
            elevation=elevation
        )
        # Store as binary: 0 if coastal, 500 if inland
        features.coast_distance_km = 0 if is_coastal else 500

        # Nature ratio - improved logic with known nature regions
        NATURE_REGIONS = ['Algarve', 'Tuscany', 'Provence', 'Amalfi', 'Costa del Sol',
                           'Iceland', 'Patagonia', 'Scottish Highlands', 'Lake District',
                           'Dolomites', 'Swiss Alps', 'Pyrenees', 'Fjords', 'Lapland']

        if any(region.lower() in dest.name.lower() for region in NATURE_REGIONS):
            features.nature_ratio = 0.9
        elif dest.type.value == 'region':
            features.nature_ratio = 0.7  # Regions generally more natural
        else:
            features.nature_ratio = 0.3  # Default for cities

        return features

    def _extract_activity_features(self, dest: Destination, features: DestinationFeatures) -> DestinationFeatures:
        """Extract activity-related features using improved heuristics"""
        lat, lon = dest.location.lat, dest.location.lon

        # Skiing score - based on known ski regions and latitude (no elevation data)
        known_ski_regions = [
            # Alps
            (45.0, 47.0, 6.0, 14.0),
            # Pyrenees
            (42.0, 43.0, -2.0, 3.0),
            # Rockies
            (37.0, 51.0, -120.0, -105.0),
            # Scandinavia
            (59.0, 70.0, 5.0, 30.0),
        ]

        in_ski_region = any(
            lat_min <= lat <= lat_max and lon_min <= lon <= lon_max
            for lat_min, lat_max, lon_min, lon_max in known_ski_regions
        )

        if in_ski_region:
            features.skiing_score = 0.7  # Likely has skiing
        else:
            features.skiing_score = 0.0

        # Water sports score - simple coastal check
        if features.coast_distance_km == 0:
            # Coastal - full water sports potential
            features.water_sports_score = 1.0
        elif features.coast_distance_km == 100:
            # Unknown - conservative default
            features.water_sports_score = 0.1
        else:
            # Inland - no water sports
            features.water_sports_score = 0.0

        # Hiking score - based on known hiking regions and nature ratio
        KNOWN_HIKING_REGIONS = ['Alps', 'Pyrenees', 'Dolomites', 'Scottish Highlands',
                                 'Lake District', 'Patagonia', 'Nepal', 'Iceland', 'Himalayas',
                                 'Andes', 'Rockies', 'Appalachian', 'New Zealand']

        nature_bonus = features.nature_ratio * 0.5

        # Known hiking destination bonus
        if any(region.lower() in dest.name.lower() or region.lower() in dest.country.lower()
               for region in KNOWN_HIKING_REGIONS):
            features.hiking_score = min(nature_bonus + 0.5, 1.0)
        else:
            features.hiking_score = min(nature_bonus, 1.0)

        # Wildlife score - improved with known wildlife regions
        WILDLIFE_HOTSPOTS = ['Kenya', 'Tanzania', 'Botswana', 'South Africa', 'Costa Rica',
                              'Galápagos', 'Amazon', 'Borneo', 'Madagascar', 'Alaska',
                              'Yellowstone', 'Serengeti', 'Kruger', 'Masai Mara', 'Okavango',
                              'Pantanal', 'Ranthambore', 'Chitwan']

        if any(region.lower() in dest.name.lower() or region.lower() in dest.country.lower()
               for region in WILDLIFE_HOTSPOTS):
            features.wildlife_score = 0.9
        elif features.nature_ratio > 0.7:
            features.wildlife_score = 0.7  # High nature
        elif features.nature_ratio > 0.5:
            features.wildlife_score = 0.4
        else:
            features.wildlife_score = features.nature_ratio * 0.2

        # Nightlife density - improved logic
        NIGHTLIFE_CITIES = ['Berlin', 'Amsterdam', 'Barcelona', 'Ibiza', 'Las Vegas',
                             'Bangkok', 'Miami', 'New York', 'London', 'Tokyo', 'Seoul',
                             'Prague', 'Budapest', 'Tel Aviv', 'Dubai', 'Paris']

        if any(city.lower() in dest.name.lower() for city in NIGHTLIFE_CITIES):
            features.nightlife_density = 0.9
        elif dest.type.value == 'region':
            features.nightlife_density = 0.1  # Regions typically low nightlife
        elif dest.type.value == 'city':
            features.nightlife_density = 0.4  # Default for cities without specific data
        else:
            features.nightlife_density = 0.1

        return features

    def _extract_popularity_features(self, dest: Destination, pageviews: Optional[int], features: DestinationFeatures) -> DestinationFeatures:
        """Extract popularity-related features"""

        # Wikipedia pageviews
        features.wikipedia_pageviews = pageviews if pageviews else 0

        # Tourism density - improved calculation using log scale for pageviews
        if features.wikipedia_pageviews > 0:
            # Log scale for pageviews (range: 7K-500K in our data)
            # log(10K)≈9.2, log(100K)≈11.5, log(500K)≈13.1
            log_views = math.log1p(features.wikipedia_pageviews)
            # Normalize 8-14 range to [0, 1]
            features.tourism_density = (log_views - 8) / 6
            features.tourism_density = max(0.0, min(features.tourism_density, 1.0))
        else:
            features.tourism_density = 0.1  # Low default for no data

        # Boost for known major tourist destinations
        major_tourist_destinations = [
            'Paris', 'London', 'Rome', 'Barcelona', 'Dubai', 'New York',
            'Tokyo', 'Bangkok', 'Singapore', 'Istanbul', 'Venice', 'Florence',
            'Santorini', 'Bali', 'Maldives', 'Machu Picchu', 'Petra', 'Iceland',
            'Tuscany', 'Provence', 'Algarve', 'Amalfi'
        ]

        if any(city.lower() in dest.name.lower() for city in major_tourist_destinations):
            features.tourism_density = min(features.tourism_density * 1.2, 1.0)

        # Accommodation density - correlated with tourism
        features.accommodation_density = features.tourism_density * 0.8

        return features

    def _extract_development_features(self, dest: Destination, country_data: Dict, features: DestinationFeatures) -> DestinationFeatures:
        """Extract development-level features from country data"""

        # Use real HDI data
        features.development_level = country_data.get('hdi', 0.7)

        # Use real GDP per capita (normalized to [0, 1])
        # Max GDP per capita is ~100k, normalize to that
        gdp_raw = country_data.get('gdp_per_capita', 15.0)  # in thousands
        features.gdp_per_capita = min(gdp_raw / 100.0, 1.0)

        return features
