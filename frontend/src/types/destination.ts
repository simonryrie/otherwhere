// Destination type (city or region)
export type DestinationType = 'city' | 'region'

// Continents
export type Continent =
  | 'Europe'
  | 'Asia'
  | 'Africa'
  | 'North America'
  | 'South America'
  | 'Oceania'

// Geographic location
export interface Location {
  lat: number
  lon: number
}

// All feature values are normalized to [0, 1] range
export interface DestinationFeatures {
  // Climate
  avg_temp_c: number              // Average temperature (normalized)

  // Tourism & Popularity
  tourism_density: number          // Tourism POI density
  wikipedia_pageviews: number      // Popularity proxy (normalized)
  accommodation_density: number    // Hotels/lodging density

  // Urbanization
  population: number               // Population (normalized)
  population_density: number       // People per km²

  // Nature & Geography
  coast_distance_km: number        // Distance to coast (normalized, 0 = on coast)
  nature_ratio: number             // Parks, forests, beaches ratio
  elevation: number                // Elevation/mountain proximity

  // Activities (all normalized 0-1 scores)
  skiing_score: number             // Ski resort density
  water_sports_score: number       // Beaches, marinas, diving
  hiking_score: number             // Trails, parks
  wildlife_score: number           // Protected areas, reserves
  nightlife_density: number        // Bars, clubs, entertainment

  // Development & Cultural Context
  development_level: number        // Modern infrastructure index
  gdp_per_capita: number          // Economic indicator (normalized)
}

// Feature constraint (for search queries)
export interface FeatureConstraint {
  min?: number
  max?: number
}

// Search constraints from LLM or user input
export type SearchConstraints = Partial<Record<keyof DestinationFeatures, FeatureConstraint>>

// Geographic filters
export interface GeographicFilters {
  continent?: Continent
  region?: string      // e.g., "Eastern Europe", "Southeast Asia", "Caribbean"
  country?: string
}

// Complete destination object
export interface Destination {
  // Identity
  id: string
  name: string

  // Geographic metadata (for filtering)
  country: string
  continent: Continent
  region?: string      // Optional sub-region

  // Type and location
  type: DestinationType
  location: Location

  // Features (for vibe-based ranking)
  features: DestinationFeatures

  // Media and description
  images: string[]
  description?: string
}

// Search request
export interface SearchRequest {
  query: string                      // Free-text query
  constraints?: SearchConstraints    // Optional pre-parsed feature constraints
  filters?: GeographicFilters        // Optional geographic filters
}

// Search response
export interface SearchResponse {
  destinations: Destination[]
  total: number
}

// Destination list response
export interface DestinationsResponse {
  destinations: Destination[]
  total: number
}
