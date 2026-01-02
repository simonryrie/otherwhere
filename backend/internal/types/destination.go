package types

// DestinationType represents whether a destination is a city or region
type DestinationType string

const (
	City   DestinationType = "city"
	Region DestinationType = "region"
)

// Continent represents the major geographic regions
type Continent string

const (
	Europe       Continent = "Europe"
	Asia         Continent = "Asia"
	Africa       Continent = "Africa"
	NorthAmerica Continent = "North America"
	SouthAmerica Continent = "South America"
	Oceania      Continent = "Oceania"
)

// Location represents geographic coordinates
type Location struct {
	Lat float64 `json:"lat" firestore:"lat"`
	Lon float64 `json:"lon" firestore:"lon"`
}

// DestinationFeatures contains all normalized feature values [0, 1]
type DestinationFeatures struct {
	// Climate
	AvgTempC float64 `json:"avg_temp_c" firestore:"avg_temp_c"`

	// Tourism & Popularity
	TourismDensity        float64 `json:"tourism_density" firestore:"tourism_density"`
	WikipediaPageviews    float64 `json:"wikipedia_pageviews" firestore:"wikipedia_pageviews"`
	AccommodationDensity  float64 `json:"accommodation_density" firestore:"accommodation_density"`

	// Urbanization
	Population        float64 `json:"population" firestore:"population"`
	PopulationDensity float64 `json:"population_density" firestore:"population_density"`

	// Nature & Geography
	CoastDistanceKm float64 `json:"coast_distance_km" firestore:"coast_distance_km"`
	NatureRatio     float64 `json:"nature_ratio" firestore:"nature_ratio"`
	Elevation       float64 `json:"elevation" firestore:"elevation"`

	// Activities (all normalized 0-1 scores)
	SkiingScore      float64 `json:"skiing_score" firestore:"skiing_score"`
	WaterSportsScore float64 `json:"water_sports_score" firestore:"water_sports_score"`
	HikingScore      float64 `json:"hiking_score" firestore:"hiking_score"`
	WildlifeScore    float64 `json:"wildlife_score" firestore:"wildlife_score"`
	NightlifeDensity float64 `json:"nightlife_density" firestore:"nightlife_density"`

	// Development & Cultural Context
	DevelopmentLevel float64 `json:"development_level" firestore:"development_level"`
	GDPPerCapita     float64 `json:"gdp_per_capita" firestore:"gdp_per_capita"`
}

// FeatureConstraint represents min/max constraints for a feature
type FeatureConstraint struct {
	Min *float64 `json:"min,omitempty"`
	Max *float64 `json:"max,omitempty"`
}

// SearchConstraints maps feature names to their constraints
type SearchConstraints map[string]FeatureConstraint

// GeographicFilters for filtering by location
type GeographicFilters struct {
	Continent *Continent `json:"continent,omitempty"`
	Region    *string    `json:"region,omitempty"`
	Country   *string    `json:"country,omitempty"`
}

// Destination represents a complete destination object
type Destination struct {
	// Identity
	ID   string `json:"id" firestore:"id"`
	Name string `json:"name" firestore:"name"`

	// Geographic metadata (for filtering)
	Country   string     `json:"country" firestore:"country"`
	Continent Continent  `json:"continent" firestore:"continent"`
	Region    *string    `json:"region,omitempty" firestore:"region,omitempty"`

	// Type and location
	Type     DestinationType `json:"type" firestore:"type"`
	Location Location        `json:"location" firestore:"location"`

	// Features (for vibe-based ranking)
	Features DestinationFeatures `json:"features" firestore:"features"`

	// Media and description
	Images      []string `json:"images" firestore:"images"`
	Description *string  `json:"description,omitempty" firestore:"description,omitempty"`
}

// SearchRequest represents a search query
type SearchRequest struct {
	Query       string             `json:"query"`
	Constraints *SearchConstraints `json:"constraints,omitempty"`
	Filters     *GeographicFilters `json:"filters,omitempty"`
}

// SearchResponse represents search results
type SearchResponse struct {
	Destinations []Destination `json:"destinations"`
	Total        int           `json:"total"`
}

// DestinationsResponse represents a list of destinations
type DestinationsResponse struct {
	Destinations []Destination `json:"destinations"`
	Total        int           `json:"total"`
}
