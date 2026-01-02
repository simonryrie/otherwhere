"""
Destination data schema for Python data ingestion scripts.
Matches TypeScript and Go type definitions.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class DestinationType(str, Enum):
    """Type of destination"""
    CITY = "city"
    REGION = "region"


class Continent(str, Enum):
    """Major geographic regions"""
    EUROPE = "Europe"
    ASIA = "Asia"
    AFRICA = "Africa"
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
    OCEANIA = "Oceania"


@dataclass
class Location:
    """Geographic coordinates"""
    lat: float
    lon: float

    def to_dict(self):
        return {"lat": self.lat, "lon": self.lon}


@dataclass
class DestinationFeatures:
    """
    All feature values normalized to [0, 1] range.
    These are used for vibe-based ranking.
    """
    # Climate
    avg_temp_c: float = 0.0

    # Tourism & Popularity
    tourism_density: float = 0.0
    wikipedia_pageviews: float = 0.0
    accommodation_density: float = 0.0

    # Urbanization
    population: float = 0.0
    population_density: float = 0.0

    # Nature & Geography
    coast_distance_km: float = 0.0
    nature_ratio: float = 0.0
    elevation: float = 0.0

    # Activities (all normalized 0-1 scores)
    skiing_score: float = 0.0
    water_sports_score: float = 0.0
    hiking_score: float = 0.0
    wildlife_score: float = 0.0
    nightlife_density: float = 0.0

    # Development & Cultural Context
    development_level: float = 0.0
    gdp_per_capita: float = 0.0

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "avg_temp_c": self.avg_temp_c,
            "tourism_density": self.tourism_density,
            "wikipedia_pageviews": self.wikipedia_pageviews,
            "accommodation_density": self.accommodation_density,
            "population": self.population,
            "population_density": self.population_density,
            "coast_distance_km": self.coast_distance_km,
            "nature_ratio": self.nature_ratio,
            "elevation": self.elevation,
            "skiing_score": self.skiing_score,
            "water_sports_score": self.water_sports_score,
            "hiking_score": self.hiking_score,
            "wildlife_score": self.wildlife_score,
            "nightlife_density": self.nightlife_density,
            "development_level": self.development_level,
            "gdp_per_capita": self.gdp_per_capita,
        }


@dataclass
class Destination:
    """Complete destination object"""
    # Identity
    id: str
    name: str

    # Geographic metadata (for filtering)
    country: str
    continent: Continent
    region: Optional[str] = None

    # Type and location
    type: DestinationType = DestinationType.CITY
    location: Location = field(default_factory=lambda: Location(0.0, 0.0))

    # Features (for vibe-based ranking)
    features: DestinationFeatures = field(default_factory=DestinationFeatures)

    # Media and description
    images: List[str] = field(default_factory=list)
    description: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON/Firestore serialization"""
        data = {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "continent": self.continent.value,
            "type": self.type.value,
            "location": self.location.to_dict(),
            "features": self.features.to_dict(),
            "images": self.images,
        }

        if self.region:
            data["region"] = self.region

        if self.description:
            data["description"] = self.description

        return data
