# Otherwhere — Technical Specification

## 1. Project Overview

**Project Name:** Otherwhere

**Tagline:** AI-curated travel inspiration board for discovering destinations based on vibes, not filters.

**Core Purpose:** Build a visually striking, full-stack MVP that demonstrates strong frontend engineering, UX sensibility, and pragmatic use of AI. The product allows users to discover travel destinations based on vibe-driven input (e.g., "chill", "low tourists", "warm but not too hot"), rather than traditional filters like country or budget alone.

**Key Principles:**
* Showcase frontend polish and interaction design as the primary value
* Use AI in a controlled, explainable, and production-realistic way
* Avoid brittle or expensive ML training pipelines
* Be fully achievable within GCP free tier
* This is a discovery and inspiration tool, not a travel booking app

---

## 2. Core Design Philosophy

### 2.1 What This Is Not
* Not a pure LLM chatbot
* Not a traditional recommender trained on user behavior
* Not a black-box classifier that needs frequent retraining

### 2.2 What This Is
A semantic retrieval system over structured geographic data, where:
* Destinations are represented as fixed feature vectors
* User intent is translated into target feature constraints
* Results are ranked by distance to intent, not by label prediction
* **AI is used as a semantic translator, not a decision maker**

This design provides:
* Full control over behavior
* Easy extensibility
* No retraining when adding or changing "vibes"

---

## 3. Technology Stack

### 3.1 Frontend
* **Framework:** Vite + React 18+
* **Language:** TypeScript
* **Styling:** Tailwind CSS
* **State Management:**
  - Zustand (UI state: search filters, selected destination, UI flags)
  - TanStack Query (server state: API calls, caching, loading states)
* **Routing:** React Router (client-side routing for destination detail pages)
* **Build Tool:** Vite

**Decision Rationale:**
- Vite chosen over Next.js: No need for SSR/SSG since destination pages are supplementary views, not primary entry points
- TypeScript for type safety around feature vectors and API contracts
- Tailwind for rapid iteration on "visually striking" UI
- Zustand + TanStack Query for clean separation of UI state vs server state

### 3.2 Backend
* **Language:** Go 1.21+
* **Router:** chi (lightweight, idiomatic, good middleware support)
* **Logging:** slog (standard library, structured logging)
* **API Style:** REST

**Endpoints:**
- `POST /api/search` — Semantic search with user query
- `GET /api/destinations/:id` — Get single destination details
- `GET /api/destinations` — Browse all destinations (optional)

**Decision Rationale:**
- Go for production-grade API: fast, lightweight, excellent for Cloud Run
- chi for clean URL parameter extraction and CORS middleware
- slog for structured logging (crucial for debugging LLM translations)

### 3.3 Data Ingestion
* **Language:** Python 3.10+
* **Key Libraries:**
  - requests (API calls)
  - pandas (data wrangling and normalization)
  - geopy (distance calculations)

**Decision Rationale:**
- Python excels at ETL tasks: rich ecosystem for data processing
- NumPy/pandas for efficient vector normalization
- Better tooling for OpenStreetMap/Wikidata API interactions
- Data scripts run locally or as Cloud Functions (not part of runtime API)

### 3.4 AI / LLM
* **Model:** Google Gemini 1.5 Flash (via Vertex AI)
* **Usage:** Semantic translation only (user query → feature constraints JSON)
* **Free Tier:** 1,500 requests/day

**Decision Rationale:**
- Free tier covers entire MVP usage
- Native GCP integration (same auth as Firestore/Cloud Storage)
- Cheapest paid option if scaling beyond free tier ($0.075/1M tokens)
- Built-in JSON mode for structured output

### 3.5 Infrastructure

**Local Development:**
- **Firestore Emulator:** Docker (isolated, disposable)
- **Go API:** Native (fast iteration with live reload)
- **Vite Dev Server:** Native (instant HMR)

**Production (GCP):**
- **Cloud Run:** Go API hosting (serverless, auto-scaling)
- **Firestore:** Destination storage (NoSQL document database)
- **Cloud Storage:** Image caching (Wikimedia Commons images)
- **Vertex AI:** Gemini 1.5 Flash access

**Decision Rationale:**
- Hybrid local dev (Docker emulator + native Go/Vite) for speed
- GCP stack for unified ecosystem and free tier benefits
- Defer GCP setup until after local development works

---

## 4. High-Level User Experience

1. User enters free-text description (e.g., "chill, low tourists, coastal, warm but not too hot")
2. System interprets intent into numeric feature preferences via Gemini
3. Destinations are ranked by similarity to those preferences
4. Results displayed in image-forward grid/list UI
5. User clicks destination → detail page/modal (client-side route)
6. User can explore, refine search, share destination URLs

---

## 5. Destination Data Model

### 5.1 Destination Granularity
The system supports both **cities** and **regions** as first-class destinations.

**Examples:**
- Cities: Lisbon, Kyoto, Medellín
- Regions: Algarve, Amalfi Coast, Patagonia, Bali

**Design Rationale:**
* Many travel "vibes" are better represented at regional level
* Regions allow richer inspiration without fine-grained POI accuracy
* Both represented identically as feature vectors (differ only in spatial extent)

**Target MVP Dataset:** ~500 destinations globally, auto-selected for diversity and quality (balanced mix of cities and regions, data-driven selection)

### 5.2 Core Feature Categories

Each destination is represented as a normalized feature vector with these dimensions:

#### Climate
* Average temperature (°C)
* Climate classification (Köppen)

#### Tourism & Popularity
* Tourism POI density (hotels, attractions)
* Wikipedia pageview volume (popularity proxy)
* Accommodation density

#### Urbanization
* Population
* Population density

#### Nature & Geography
* Coast proximity
* Nature feature ratio (parks, forests, beaches)
* Elevation / mountain proximity

#### Activities & Recreation
Activities inferred from OpenStreetMap tagged features, aggregated at city/region level.
Represented as relative availability scores (not binary flags):
* Skiing → density of ski resorts, lifts, alpine facilities
* Water sports → beaches, marinas, surf spots, diving sites
* Hiking → trails, national parks, elevation variance
* Wildlife/safaris → protected areas, reserves, national parks

#### Development & Cultural Context
Development-level signals treated as proxies, derived from multiple sources:
* GDP per capita (Wikidata / World Bank)
* Urban infrastructure density (OSM amenities per km²)
* Internet penetration proxies
* Presence of modern infrastructure (airports, transit hubs)

These combine into interpretable dimensions:
* modern ↔ traditional
* highly developed ↔ developing
* luxury ↔ budget-oriented

#### Wildlife & Biodiversity
Inferred from:
* Proximity and density of protected areas (national parks, reserves)
* UNESCO natural heritage sites
* Biodiversity hotspot datasets (WWF / UNEP open data)

### 5.3 Example Destination Schema

```json
{
  "id": "pt-lagos",
  "name": "Lagos",
  "country": "Portugal",
  "type": "city",
  "location": {
    "lat": 37.1028,
    "lon": -8.6731
  },
  "features": {
    "avg_temp_c": 22.5,
    "population_density": 0.28,
    "tourism_density": 0.22,
    "nature_ratio": 0.62,
    "nightlife_density": 0.08,
    "coast_distance_km": 1.2,
    "wikipedia_pageviews": 14500,
    "skiing_score": 0.0,
    "water_sports_score": 0.85,
    "hiking_score": 0.45,
    "wildlife_score": 0.15,
    "development_level": 0.78
  },
  "images": [
    "https://commons.wikimedia.org/wiki/File:Lagos_beach.jpg"
  ]
}
```

All features normalized to [0, 1] ranges wherever possible.

---

## 6. Data Sources (Free / Open)

### 6.1 Geographic & Feature Data
* **OpenStreetMap (Overpass API)**
  - Amenities, tourism POIs, leisure features
  - Trails, ski resorts, marinas, beaches
  - Urban infrastructure density
* **Wikidata**
  - Population, GDP per capita
  - Climate classifications
  - UNESCO heritage references
* **Wikipedia REST API**
  - Pageviews (tourism popularity proxy)
  - Descriptions and categories
* **World Bank Open Data**
  - Economic and development indicators
* **UNESCO Open Data**
  - Cultural and natural heritage sites
* **WWF / UNEP Open Biodiversity Datasets**
  - Protected areas
  - Biodiversity hotspot regions

### 6.2 Images
Primary sources:
* Wikipedia / Wikimedia Commons (CC-licensed)
* Optional: Unsplash / Pixabay

Images cached in GCP Cloud Storage for:
* Performance
* Stability
* Thumbnail generation

---

## 7. Vibe Tags: Design and Control

### 7.1 Key Decision
**Vibe tags are not predicted by a trained classifier.**

Instead:
* Tags are conceptual shortcuts for feature preferences
* Defined as configuration, not training data
* No retraining required when adding/changing tags

### 7.2 Example Vibe Definitions

```json
{
  "chill": {
    "population_density": { "max": 0.35 },
    "nightlife_density": { "max": 0.3 },
    "nature_ratio": { "min": 0.5 },
    "avg_temp_c": { "min": 18, "max": 28 }
  },
  "low_tourists": {
    "tourism_density": { "max": 0.4 },
    "wikipedia_pageviews": { "max": 20000 }
  },
  "adventurous": {
    "hiking_score": { "min": 0.6 },
    "water_sports_score": { "min": 0.5 },
    "nature_ratio": { "min": 0.6 }
  }
}
```

---

## 8. AI Usage: Semantic Translation

### 8.1 Why This Approach
The system uses an LLM **only** to translate human language into structured numeric constraints.

**It does NOT:**
* Rank destinations
* Decide what is "best"
* Generate factual data

This is one of the most reliable and low-risk uses of LLMs.

### 8.2 Primary Path: LLM-Based Semantic Translation

**User input:**
```
"Chill, low tourists, warm but not too hot"
```

**Gemini prompt (structured):**
```
Convert this user query into destination feature constraints.
Output valid JSON matching this schema:

{
  "population_density": { "min"?: number, "max"?: number },
  "tourism_density": { "min"?: number, "max"?: number },
  "avg_temp_c": { "min"?: number, "max"?: number },
  "nature_ratio": { "min"?: number, "max"?: number },
  ...
}

User query: "Chill, low tourists, warm but not too hot"
```

**Gemini output (validated and clamped):**
```json
{
  "population_density": { "max": 0.3 },
  "tourism_density": { "max": 0.25 },
  "avg_temp_c": { "min": 20, "max": 27 },
  "nature_ratio": { "min": 0.5 }
}
```

**Strict schema validation** in Go ensures determinism and safety.

### 8.3 Fallback Strategy (Post-MVP)

Although not required for MVP, the system is designed so a rule-based fallback can be added later with minimal effort.

**Purpose:**
* Provide resilience if LLM is unavailable
* Ensure app can always return results
* Avoid blocking UX on external dependencies

**Approach:**
* Match known keywords (chill, beach, mountain, warm, etc.)
* Apply conservative feature constraints
* Ignore unknown terms safely
* If no signals detected → neutral ranking + UI prompt to refine

---

## 9. Ranking & Retrieval Logic

Destinations ranked using a **distance-based scoring function**.

**Conceptual model:**
* Each destination = feature vector
* User intent = target vector with ranges
* Score = weighted distance from target

**Algorithm:**
1. For each destination, calculate distance from target constraints
2. Features with constraints get higher weight
3. Sort by distance (ascending = best match)

**Example:**
```
User wants: { "avg_temp_c": { "min": 20, "max": 27 }, "tourism_density": { "max": 0.3 } }

Destination A: { "avg_temp_c": 23, "tourism_density": 0.15 } → Distance: 0.05
Destination B: { "avg_temp_c": 32, "tourism_density": 0.6 } → Distance: 0.85

Ranking: A > B
```

This is:
* Explainable
* Deterministic
* Easy to tune

---

## 10. System Architecture

### 10.1 Frontend (React)

**Responsibilities:**
* User input & refinement UI
* Destination browsing experience
* Image-driven presentation
* Client-side routing for detail pages

**Key focus:**
* Animations and transitions
* Visual hierarchy
* Exploration-first UX
* Fast, responsive interface

### 10.2 Backend (Go)

**Responsibilities:**
* Data ingestion & normalization (Python scripts)
* Feature vector storage (Firestore)
* Semantic translation orchestration (Gemini API)
* Ranking and filtering logic
* REST API endpoints

### 10.3 Data Pipeline (Python)

**Workflow:**
1. Fetch data from OSM, Wikidata, Wikipedia APIs
2. Extract and normalize features
3. Calculate derived metrics (densities, ratios, scores)
4. Output normalized destination JSON
5. Upload to Firestore (one-time or periodic)

**Go API reads pre-computed data at runtime** (no heavy processing in request path)

### 10.4 GCP Services (Free Tier)

* **Cloud Run** — Go API hosting (serverless, auto-scaling)
* **Firestore** — Destination metadata and features
* **Cloud Storage** — Images & thumbnails
* **Vertex AI** — Gemini 1.5 Flash access

---

## 11. MVP Scope

### Included
* ~500 global destinations (cities + regions, auto-selected for diversity)
* Core vibe-based search using Gemini semantic translation
* Image-forward results UI (grid/list view)
* Destination detail page (client-side route)
* Deterministic ranking via feature-distance scoring
* Graceful handling of invalid or empty semantic output

### Explicitly Out of Scope (for MVP)
* User accounts
* Personalization
* Real-time data updates
* Bookings or pricing
* Map view (deferred to v2 with Mapbox)
* Rule-based semantic fallback (post-MVP enhancement)

---

## 12. Development Workflow

### 12.1 Local Development Setup

**Prerequisites:**
- Node.js 18+
- Go 1.21+
- Python 3.10+
- Docker (for Firestore emulator)

**Start services:**
```bash
# Terminal 1: Firestore emulator
docker-compose up firestore

# Terminal 2: Go API with live reload
cd backend
air  # or: go run main.go

# Terminal 3: Vite dev server
cd frontend
npm run dev
```

### 12.2 Data Ingestion Workflow

```bash
cd data-ingestion
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run ingestion script
python ingest_destinations.py

# Output: destinations.json → upload to Firestore
```

### 12.3 Deployment Workflow (Post-MVP)

1. **Set up GCP project**
   - Enable Cloud Run, Firestore, Cloud Storage, Vertex AI APIs
   - Create service account with appropriate permissions

2. **Deploy Go API to Cloud Run**
   ```bash
   cd backend
   gcloud run deploy otherwhere-api --source .
   ```

3. **Deploy frontend**
   ```bash
   cd frontend
   npm run build
   # Upload dist/ to Cloud Storage bucket with CDN
   ```

4. **Upload destination data to Firestore**
   ```bash
   cd data-ingestion
   python upload_to_firestore.py
   ```

---

## 13. Potential Future Enhancements (Post-MVP)

* Saved moodboards / collections
* User feedback loop ("more like this")
* Social sharing (Open Graph meta tags for destination pages)
* Collaborative planning
* Seasonal filtering (e.g., "best time to visit")
* Multi-modal input (image → vibe extraction)
* Map view (Mapbox GL JS integration)
* Rule-based semantic fallback (keyword matching)

---

## 14. Why This Project Works as a Portfolio Piece

* Demonstrates strong frontend and UX focus (visually striking, interaction design)
* Shows system design maturity (clean separation of concerns, production-realistic)
* Uses AI in a realistic, explainable way (not a black box)
* Avoids common junior pitfalls (overtraining, brittle ML pipelines)
* Easy to discuss and defend in interviews (clear design rationale)
* Full-stack demonstration (React, Go, Python, GCP, AI integration)

---

## 15. Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Frontend Framework** | Vite + React | Faster than Next.js for non-SSR app, simpler deployment |
| **Language** | TypeScript | Type safety for feature vectors and API contracts |
| **Styling** | Tailwind CSS | Rapid iteration on visually striking UI |
| **State Management** | Zustand + TanStack Query | Clean separation of UI state vs server state |
| **Backend Language** | Go | Fast, lightweight, production-grade for Cloud Run |
| **Data Ingestion** | Python | Superior tooling for ETL and data wrangling |
| **LLM** | Gemini 1.5 Flash | Free tier, native GCP integration, cheapest paid option |
| **Database** | Firestore | Native GCP, NoSQL fits destination documents well |
| **Hosting** | Cloud Run + Cloud Storage | Serverless, auto-scaling, free tier friendly |
| **Local Dev** | Hybrid (Docker emulator + native) | Speed of native dev with isolation of Docker |
| **Map View** | Deferred to v2 | Focus MVP on core discovery UX |
| **Dataset Size** | ~500 destinations | Large enough to showcase semantic search value |

---

**Last Updated:** 2025-12-31
