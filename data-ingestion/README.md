# Otherwhere Data Ingestion Pipeline

This directory contains the data ingestion pipeline for the Otherwhere travel recommendation app. The pipeline fetches destination data from various sources, extracts features, and generates a comprehensive dataset ready for upload to Firestore.

## Overview

The pipeline performs the following steps:

1. **Fetch Destinations**: Retrieves cities and curated regions from GeoNames database
2. **Extract Features**: Gathers real data from multiple APIs:
   - Climate data from OpenMeteo
   - Population & elevation from Wikidata
   - Popularity metrics from Wikipedia pageviews
   - Images from Unsplash (6 diverse images per destination)
   - Country-level data (HDI, GDP, etc.)
3. **Normalize Features**: Scales all features to [0, 1] range
4. **Output**: Generates `destinations.json` ready for Firestore upload

## Prerequisites

### 1. Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. GeoNames Data Files

Download the required GeoNames data files:

```bash
# Download cities database (cities with population > 15,000)
curl -O https://download.geonames.org/export/dump/cities15000.zip
unzip cities15000.zip

# Download country info
curl -O https://download.geonames.org/export/dump/countryInfo.txt
```

**What these files contain:**
- `cities15000.txt`: Database of ~25,000 cities worldwide with population > 15,000
- `countryInfo.txt`: Country metadata including ISO codes, capital cities, population, area

### 3. API Keys

Create a `.env` file in this directory with your API credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your keys
```

**Required API keys:**
- **Unsplash API**: Get your free API key at https://unsplash.com/developers
  - Sign up for an account
  - Create a new application
  - Copy your Access Key and Secret Key
  - For production use (>50 requests/hour), apply for production approval

**Note**: Other APIs (OpenMeteo, Wikipedia, Wikidata) do not require API keys.

### 4. Environment File Format

Your `.env` file should look like this:

```bash
UNSPLASH_ACCESS_KEY=your_access_key_here
UNSPLASH_SECRET_KEY=your_secret_key_here
```

## Running the Ingestion

### Full Ingestion (500 destinations)

```bash
# Activate virtual environment
source venv/bin/activate

# Run full ingestion
python run_ingestion.py
```

This will:
- Fetch 496 destinations (371 cities + 125 curated regions)
- Extract features using real APIs
- Fetch 6 diverse images per destination from Unsplash
- Normalize all features
- Generate three output files

**Expected runtime**: ~45 minutes (depends on API response times)

### Test Run (Limited destinations)

```bash
# Run with only 20 destinations for testing
python run_ingestion.py 20
```

## Output Files

The pipeline generates three JSON files:

1. **`destinations_raw.json`**: Raw data from GeoNames (checkpoint)
2. **`destinations_with_features.json`**: After feature extraction, before normalization (checkpoint)
3. **`destinations.json`**: Final output with normalized features (ready for Firestore)

### Output File Structure

Each destination in `destinations.json` includes:

```json
{
  "id": "unique-destination-id",
  "name": "Paris",
  "country": "France",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "population": 2138551,
  "features": {
    "temp_summer": 0.65,
    "temp_winter": 0.35,
    "is_coastal": 0.0,
    "elevation_normalized": 0.05,
    "beach_activities": 0.1,
    "outdoor_activities": 0.7,
    "cultural_activities": 0.95,
    "nightlife": 0.85,
    "shopping": 0.9,
    "cost_of_living": 0.8,
    "safety": 0.75,
    "popularity": 0.92
  },
  "images": [
    {
      "url": "https://images.unsplash.com/photo-...",
      "photographer_name": "John Doe",
      "photographer_url": "https://unsplash.com/@johndoe",
      "download_url": "https://api.unsplash.com/photos/.../download"
    }
  ]
}
```

## Directory Structure

```
data-ingestion/
├── README.md                          # This file
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Python dependencies
├── run_ingestion.py                   # Main entry point
│
├── src/                               # Source code
│   ├── models/                        # Data models
│   │   └── destination_schema.py
│   │
│   ├── fetchers/                      # Data fetching modules
│   │   ├── fetch_destinations.py
│   │   ├── geonames_loader.py
│   │   ├── wikidata_fetcher.py
│   │   └── unsplash_images.py
│   │
│   ├── extractors/                    # Feature extraction
│   │   └── feature_extractor.py
│   │
│   ├── utils/                         # Utility modules
│   │   ├── coastal_checker.py
│   │   ├── normalizer.py
│   │   └── api_clients.py
│   │
│   └── data/                          # Static data
│       └── manual_regions.py
│
└── data/                              # Data files (gitignored)
    ├── cities15000.txt
    ├── cities15000.zip
    ├── countryInfo.txt
    ├── destinations.json
    ├── destinations_raw.json
    └── destinations_with_features.json
```

## Pipeline Components

### Core Scripts

- **`run_ingestion.py`**: Main entry point, orchestrates the entire pipeline
- **`src/fetchers/fetch_destinations.py`**: Fetches destinations from GeoNames
- **`src/extractors/feature_extractor.py`**: Extracts features using real APIs
- **`src/utils/normalizer.py`**: Normalizes features to [0, 1] range
- **`src/models/destination_schema.py`**: Data models and schemas

### Helper Modules

- **`src/fetchers/geonames_loader.py`**: Loads and parses GeoNames data files
- **`src/data/manual_regions.py`**: Curated list of popular tourist regions
- **`src/utils/coastal_checker.py`**: Determines if a location is coastal
- **`src/fetchers/wikidata_fetcher.py`**: Fetches population and elevation from Wikidata
- **`src/fetchers/unsplash_images.py`**: Fetches diverse images from Unsplash API
- **`src/utils/api_clients.py`**: API clients for OpenMeteo, Wikipedia, etc.

## Data Sources

### Real APIs Used

1. **OpenMeteo API**: Accurate temperature data
   - Free, no API key required
   - Historical climate data

2. **Wikidata**: Population and elevation data
   - Free, no API key required
   - Structured data from Wikipedia

3. **Wikipedia Pageviews API**: Popularity metrics
   - Free, no API key required
   - 30-day pageview counts

4. **Unsplash API**: High-quality destination images
   - Free tier: 50 requests/hour
   - Production tier: Unlimited (requires approval)
   - 6 diverse query types per destination:
     - Landmark views
     - Street scenes
     - Aerial views
     - Cultural scenes
     - Local food
     - Generic destination photos

### Geographic Diversity

The pipeline ensures geographic diversity:
- Selects cities from 177 countries
- Maximum 10 cities per country
- Includes 125 curated tourist regions (e.g., "Scottish Highlands", "Amalfi Coast")
- Round-robin selection by continent

## Troubleshooting

### Missing GeoNames Files

If you see errors about missing data files:

```bash
# Re-download the files
curl -O https://download.geonames.org/export/dump/cities15000.zip
unzip cities15000.zip
curl -O https://download.geonames.org/export/dump/countryInfo.txt
```

### Unsplash Rate Limiting

If you see 403 errors or rate limit warnings:
- Check your API key is correct in `.env`
- Demo accounts are limited to 50 requests/hour
- Apply for production approval at https://unsplash.com/oauth/applications
- Use a smaller test run: `python run_improved_ingestion.py 20`

### Import Errors

If you see Python import errors:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

After running the ingestion:

1. **Review the data**: Check `destinations.json` to verify output quality
2. **Upload to Firestore**: Run the upload script (to be created)
3. **Build ranking algorithm**: Use the normalized features for personalized recommendations

## Notes

- All temperatures are in Celsius
- All features are normalized to [0, 1] range for easier comparison
- Image URLs include proper Unsplash attribution metadata
- The pipeline is idempotent - safe to re-run
- Checkpoint files allow resuming if interrupted
