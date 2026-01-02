# Data Ingestion

Python scripts for fetching, processing, and normalizing destination data from open sources.

## Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Data Sources

- **OpenStreetMap (Overpass API)** - POIs, amenities, geographic features
- **Wikidata** - Population, GDP, climate data
- **Wikipedia API** - Pageview statistics (popularity proxy)
- **World Bank Open Data** - Economic indicators
- **UNESCO** - Heritage sites
- **WWF/UNEP** - Biodiversity data

## Workflow

1. **Fetch** - Download raw data from APIs
2. **Extract** - Parse and extract relevant features
3. **Normalize** - Scale features to [0, 1] ranges
4. **Export** - Output JSON for Firestore upload

## Scripts (to be created)

- `fetch_destinations.py` - Main data ingestion script
- `normalize.py` - Feature normalization utilities
- `upload_firestore.py` - Upload to Firestore

## Output

Generates `destinations.json` with normalized feature vectors ready for upload to Firestore.
