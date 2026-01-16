"""
Feature normalization to [0, 1] range.
"""

import numpy as np
import pandas as pd
from typing import List
from src.models.destination_schema import Destination, DestinationFeatures
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureNormalizer:
    """Normalizes destination features to [0, 1] range"""

    def __init__(self):
        self.stats = {}

    def normalize_all(self, destinations: List[Destination]) -> List[Destination]:
        """Normalize all features across all destinations"""
        if not destinations:
            return destinations

        logger.info(f"Normalizing features for {len(destinations)} destinations...")

        # First pass: collect all values to calculate min/max/percentiles
        self._calculate_statistics(destinations)

        # Second pass: normalize each destination
        for dest in destinations:
            dest.features = self._normalize_features(dest.features)

        logger.info("Normalization complete")
        return destinations

    def _calculate_statistics(self, destinations: List[Destination]):
        """Calculate min, max, and percentiles for each feature"""
        # Collect all feature values
        feature_values = {}

        for dest in destinations:
            features = dest.features
            for field_name in features.__dataclass_fields__:
                value = getattr(features, field_name)
                if field_name not in feature_values:
                    feature_values[field_name] = []
                feature_values[field_name].append(value)

        # Calculate statistics
        for field_name, values in feature_values.items():
            values_array = np.array([v for v in values if v is not None and v > 0])

            if len(values_array) == 0:
                self.stats[field_name] = {'min': 0, 'max': 1, 'median': 0.5}
                continue

            self.stats[field_name] = {
                'min': float(np.min(values_array)),
                'max': float(np.max(values_array)),
                'median': float(np.median(values_array)),
                'p25': float(np.percentile(values_array, 25)),
                'p75': float(np.percentile(values_array, 75)),
                'p90': float(np.percentile(values_array, 90))
            }

        logger.info(f"Calculated statistics for {len(self.stats)} features")

    def _normalize_features(self, features: DestinationFeatures) -> DestinationFeatures:
        """Normalize a single destination's features"""

        # Temperature (range -15°C to 45°C for extreme climates)
        features.avg_temp_c = self._normalize_linear(
            features.avg_temp_c, min_val=-15, max_val=45
        )

        # Tourism metrics (percentile-based)
        features.tourism_density = self._normalize_percentile(
            features.tourism_density, 'tourism_density'
        )
        features.accommodation_density = self._normalize_percentile(
            features.accommodation_density, 'accommodation_density'
        )
        features.nightlife_density = self._normalize_percentile(
            features.nightlife_density, 'nightlife_density'
        )

        # Wikipedia pageviews (log scale + percentile)
        if features.wikipedia_pageviews > 0:
            log_pageviews = np.log1p(features.wikipedia_pageviews)
            features.wikipedia_pageviews = self._normalize_value(
                log_pageviews, 'wikipedia_pageviews'
            )
        else:
            features.wikipedia_pageviews = 0.0

        # Geography
        features.coast_distance_km = self._normalize_linear(
            features.coast_distance_km, min_val=0, max_val=500
        )
        features.nature_ratio = self._normalize_percentile(
            features.nature_ratio, 'nature_ratio'
        )

        # Activity scores (percentile-based)
        features.skiing_score = self._normalize_percentile(
            features.skiing_score, 'skiing_score'
        )
        # water_sports_score is already in [0, 1] (binary coastal check) - skip normalization
        # features.water_sports_score - keep as-is
        features.hiking_score = self._normalize_percentile(
            features.hiking_score, 'hiking_score'
        )
        features.wildlife_score = self._normalize_percentile(
            features.wildlife_score, 'wildlife_score'
        )

        # Development metrics (already in [0, 1] as placeholders)
        # features.development_level and features.gdp_per_capita are already normalized

        return features

    def _normalize_linear(self, value: float, min_val: float, max_val: float) -> float:
        """Linear normalization to [0, 1]"""
        if value is None or value <= min_val:
            return 0.0
        if value >= max_val:
            return 1.0
        return (value - min_val) / (max_val - min_val)

    def _normalize_log(self, value: float) -> float:
        """Log scale normalization"""
        if value <= 0:
            return 0.0
        log_val = np.log1p(value)
        # Normalize between log(1000) and log(10M) roughly
        return min(log_val / 16.0, 1.0)

    def _normalize_percentile(self, value: float, feature_name: str) -> float:
        """Percentile-based normalization"""
        if value <= 0:
            return 0.0

        if feature_name not in self.stats:
            return 0.5

        stats = self.stats[feature_name]
        min_val = stats['min']
        max_val = stats['max']

        if max_val == min_val:
            return 0.5

        normalized = (value - min_val) / (max_val - min_val)
        return min(max(normalized, 0.0), 1.0)

    def _normalize_value(self, value: float, feature_name: str) -> float:
        """Generic normalization using calculated statistics"""
        if feature_name not in self.stats:
            return 0.5

        stats = self.stats[feature_name]
        return self._normalize_linear(value, stats['min'], stats['max'])
