"""
Reliable coastal location checker using elevation + geographic heuristics.
Much faster and more reliable than external APIs.
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Landlocked countries
LANDLOCKED_COUNTRIES = {
    'Afghanistan', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan',
    'Belarus', 'Bhutan', 'Bolivia', 'Botswana', 'Burkina Faso',
    'Burundi', 'Central African Republic', 'Chad', 'Czech Republic', 'Czechia',
    'Ethiopia', 'Hungary', 'Kazakhstan', 'Kosovo', 'Kyrgyzstan',
    'Laos', 'Lesotho', 'Liechtenstein', 'Luxembourg', 'Malawi',
    'Mali', 'Moldova', 'Mongolia', 'Nepal', 'Niger',
    'North Macedonia', 'Paraguay', 'Rwanda', 'San Marino', 'Serbia',
    'Slovakia', 'South Sudan', 'Swaziland', 'Switzerland', 'Tajikistan',
    'Turkmenistan', 'Uganda', 'Uzbekistan', 'Vatican City', 'Zambia',
    'Zimbabwe'
}

# Known coastal cities (to override heuristics)
COASTAL_CITIES = {
    'Barcelona', 'Valencia', 'Málaga', 'Lisbon', 'Porto', 'Nice', 'Marseille', 'Cannes',
    'Naples', 'Genoa', 'Venice', 'Palermo', 'Athens', 'Thessaloniki', 'Santorini',
    'Mykonos', 'Istanbul', 'Antalya', 'Split', 'Dubrovnik', 'Copenhagen', 'Helsinki',
    'Stockholm', 'Oslo', 'Bergen', 'Amsterdam', 'Rotterdam', 'Dublin', 'Cork',
    'Galway', 'Edinburgh', 'Glasgow', 'Brighton', 'Liverpool', 'Portsmouth',
    'Tokyo', 'Yokohama', 'Osaka', 'Hong Kong', 'Singapore', 'Phuket', 'Mumbai',
    'Chennai', 'Dubai', 'Abu Dhabi', 'Tel Aviv', 'Haifa', 'Miami', 'Los Angeles',
    'San Francisco', 'Seattle', 'San Diego', 'Vancouver', 'Rio de Janeiro',
    'Salvador', 'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Auckland', 'Cape Town',
    'Durban', 'Lagos', 'Casablanca', 'Alexandria', 'Tunis', 'Tangier',
    'New York', 'Algarve', 'Amalfi', 'Costa del Sol', 'Shanghai', 'London',
    'Shenzhen', 'Guangzhou', 'St Petersburg', 'Saint Petersburg'
}

# Known inland cities (to override heuristics)
INLAND_CITIES = {
    'Paris', 'Berlin', 'Madrid', 'Rome', 'Vienna', 'Prague', 'Budapest', 'Warsaw',
    'Krakow', 'Munich', 'Zurich', 'Geneva', 'Lyon', 'Milan', 'Florence', 'Moscow',
    'St Petersburg', 'Kiev', 'Minsk', 'Delhi', 'Bangalore', 'Hyderabad', 'Beijing',
    'Chengdu', 'Xi\'an', 'Las Vegas', 'Phoenix', 'Denver', 'Dallas', 'Atlanta',
    'Chicago', 'Mexico City', 'São Paulo', 'Brasília', 'Nairobi', 'Johannesburg',
    'Addis Ababa', 'Bangkok', 'Hanoi'
}


class CoastalChecker:
    """Check if a location is coastal using elevation + geographic heuristics"""

    def __init__(self):
        pass

    def is_coastal(self, lat: float, lon: float, city_name: str = '', country: str = '', elevation: float = None) -> bool:
        """
        Check if location is coastal.

        Uses a combination of:
        1. Known coastal/inland city lists
        2. Landlocked country check
        3. Elevation heuristic (coastal cities typically < 50m)

        Args:
            lat: Latitude
            lon: Longitude
            city_name: City name for lookup
            country: Country name
            elevation: Elevation in meters (if known)

        Returns:
            True if coastal, False if inland
        """
        # Check known coastal cities
        city_lower = city_name.lower()
        for coastal_city in COASTAL_CITIES:
            if coastal_city.lower() in city_lower:
                return True

        # Check known inland cities
        for inland_city in INLAND_CITIES:
            if inland_city.lower() in city_lower:
                return False

        # Check if landlocked country
        if country in LANDLOCKED_COUNTRIES:
            return False

        # Use elevation heuristic
        if elevation is not None:
            if elevation < 50:
                # Low elevation in non-landlocked country -> likely coastal
                return True
            elif elevation > 200:
                # High elevation -> definitely not coastal
                return False

        # Default: assume not coastal (conservative)
        return False

    def get_water_sports_score(self, is_coastal: bool) -> float:
        """
        Get water sports score based on coastal status.

        Args:
            is_coastal: Result from is_coastal()

        Returns:
            1.0 if coastal
            0.0 if inland
        """
        return 1.0 if is_coastal else 0.0
