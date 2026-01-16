"""
Main script to fetch destination data.
Uses GeoNames for cities + curated list for regions.
"""

import json
import logging
from typing import List, Dict
from tqdm import tqdm

from src.models.destination_schema import Destination, DestinationType, Continent, Location, DestinationFeatures
from src.fetchers.geonames_loader import GeoNamesLoader
from src.data.manual_regions import get_regions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DestinationFetcher:
    """Fetches and processes destination data"""

    def __init__(self):
        self.geonames_loader = GeoNamesLoader()

    def fetch_destinations(self, limit: int = 500) -> List[Destination]:
        """Fetch destinations from GeoNames + manual regions"""
        logger.info(f"Fetching up to {limit} destinations...")

        # Calculate split (75% cities, 25% regions to get ~135 regions)
        cities_limit = int(limit * 0.75)  # ~375 cities
        regions_limit = min(135, int(limit * 0.25))  # ~125-135 regions

        # Fetch cities from GeoNames
        logger.info(f"Loading {cities_limit} cities from GeoNames...")
        raw_cities = self.geonames_loader.get_diverse_cities(target=cities_limit)

        # Fetch regions from curated list
        logger.info(f"Loading {regions_limit} regions from curated list...")
        raw_regions = get_regions(limit=regions_limit)

        # Combine
        raw_destinations = raw_cities + raw_regions

        # Convert to Destination objects
        all_destinations = []
        for raw_dest in tqdm(raw_destinations, desc="Creating destination objects"):
            dest = self.create_destination_from_raw(raw_dest)
            if dest:
                all_destinations.append(dest)

        logger.info(f"Created {len(all_destinations)} destination objects")
        return all_destinations[:limit]

    def create_destination_from_raw(self, raw_dest: Dict) -> Destination:
        """Create a Destination object from raw Wikidata data"""
        try:
            # Generate ID from name
            dest_id = self.generate_id(raw_dest['name'])

            # Determine destination type
            dest_type = DestinationType.CITY if raw_dest['type'] == 'city' else DestinationType.REGION

            # Create destination with basic info
            destination = Destination(
                id=dest_id,
                name=raw_dest['name'],
                country=raw_dest['country'],
                continent=raw_dest['continent'],
                region=None,  # Will be populated later if needed
                type=dest_type,
                location=Location(
                    lat=raw_dest['lat'],
                    lon=raw_dest['lon']
                ),
                features=DestinationFeatures(),  # Will be populated in feature extraction step
                images=[],  # Will be populated later
                description=None
            )

            return destination

        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to create destination from {raw_dest.get('name', 'unknown')}: {e}")
            return None

    def generate_id(self, name: str) -> str:
        """Generate a URL-safe ID from a name"""
        import re
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        id_str = name.lower()
        id_str = re.sub(r'[^\w\s-]', '', id_str)
        id_str = re.sub(r'[-\s]+', '-', id_str)
        return id_str.strip('-')

    def save_destinations(self, destinations: List[Destination], filename: str = 'destinations.json'):
        """Save destinations to JSON file"""
        data = [dest.to_dict() for dest in destinations]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(destinations)} destinations to {filename}")


def main():
    """Main execution function"""
    fetcher = DestinationFetcher()

    # Fetch destinations
    destinations = fetcher.fetch_destinations(limit=500)

    # Save to JSON
    fetcher.save_destinations(destinations, 'destinations_raw.json')

    logger.info(f"""
    ✅ Initial fetch complete!

    Next steps:
    1. Run feature extraction script to populate features
    2. Normalize all features to [0, 1]
    3. Add images from Wikimedia Commons
    4. Upload to Firestore
    """)


if __name__ == '__main__':
    main()
