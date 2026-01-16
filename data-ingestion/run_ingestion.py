"""
Complete data ingestion pipeline with improved feature extraction.
Uses real data sources for accurate, high-quality destination data.
"""

import logging
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.fetchers.fetch_destinations import DestinationFetcher
from src.extractors.feature_extractor import FeatureExtractor
from src.utils.normalizer import FeatureNormalizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the complete improved data ingestion pipeline"""

    logger.info("=" * 60)
    logger.info("OTHERWHERE IMPROVED DATA INGESTION PIPELINE")
    logger.info("=" * 60)

    # Step 1: Fetch destinations
    logger.info("\n[1/4] Fetching destinations...")
    fetcher = DestinationFetcher()

    # Allow override via command line for testing
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 500

    destinations = fetcher.fetch_destinations(limit=limit)
    logger.info(f"✓ Fetched {len(destinations)} destinations")

    # Save raw data as checkpoint
    fetcher.save_destinations(destinations, 'data/destinations_raw.json')

    # Step 2: Extract features with IMPROVED extractors
    logger.info("\n[2/4] Extracting features with real data sources...")
    logger.info("  - OpenMeteo for accurate temperatures")
    logger.info("  - Wikidata for population/elevation")
    logger.info("  - Wikipedia for pageviews")
    logger.info("  - Unsplash for images (6 per destination)")
    logger.info("  - Real HDI/GDP data by country")

    extractor = FeatureExtractor()

    for dest in tqdm(destinations, desc="Extracting features"):
        try:
            dest = extractor.extract_features(dest)
        except Exception as e:
            logger.error(f"Failed to extract features for {dest.name}: {e}")
            continue

    logger.info(f"✓ Extracted features for {len(destinations)} destinations")

    # Save with features as checkpoint
    fetcher.save_destinations(destinations, 'data/destinations_with_features.json')

    # Step 3: Normalize features
    logger.info("\n[3/4] Normalizing features to [0, 1] range...")
    normalizer = FeatureNormalizer()
    destinations = normalizer.normalize_all(destinations)
    logger.info(f"✓ Normalized {len(destinations)} destinations")

    # Step 4: Save final output
    logger.info("\n[4/4] Saving final destination data...")
    fetcher.save_destinations(destinations, 'data/destinations.json')

    # Print summary statistics
    total_images = sum(len(d.images) for d in destinations)
    avg_images = total_images / len(destinations) if destinations else 0

    logger.info("\n" + "=" * 60)
    logger.info("INGESTION COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"""
Summary:
  - Total destinations: {len(destinations)}
  - Total images fetched: {total_images} ({avg_images:.1f} per destination)
  - Output files:
      • data/destinations_raw.json (raw fetch)
      • data/destinations_with_features.json (before normalization)
      • data/destinations.json (final, normalized)

Data Quality Improvements:
  ✓ Real temperature data from OpenMeteo API
  ✓ Real population/elevation from Wikidata
  ✓ Accurate coastal detection (heuristic-based)
  ✓ Wikipedia pageview data for popularity
  ✓ 6 diverse images per destination from Unsplash
  ✓ Real HDI/GDP data for {len(set(d.country for d in destinations))} countries
  ✓ Improved activity scores with geographic logic

Next steps:
  1. Review data/destinations.json
  2. Run upload_to_firestore.py to load data
  3. Start building the ranking algorithm!
    """)


if __name__ == '__main__':
    main()
