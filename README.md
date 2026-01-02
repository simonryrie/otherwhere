# Otherwhere

AI-curated travel inspiration board for discovering destinations based on vibes, not filters.

## Project Structure

```
otherwhere/
├── frontend/          # Vite + React + TypeScript
├── backend/           # Go REST API
├── data-ingestion/    # Python scripts for destination data
├── docs/              # Additional documentation
├── Spec.md            # Complete technical specification
├── Todo.md            # Detailed task breakdown
└── Claude.md          # AI assistant context and guidelines
```

## Quick Start

### Prerequisites

- Node.js 18+
- Go 1.21+
- Python 3.10+
- Docker (for Firestore emulator)

### Local Development

```bash
# Start Firestore emulator
docker-compose up firestore

# Run Go API (in another terminal)
cd backend
go run main.go

# Run frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Stack

**Frontend:**
- Vite + React + TypeScript
- Tailwind CSS
- Zustand (UI state) + TanStack Query (server state)
- React Router

**Backend:**
- Go with chi router and slog
- REST API

**Data:**
- Python for ETL (OpenStreetMap, Wikidata, Wikipedia)
- Firestore (destination storage)

**AI:**
- Google Gemini 1.5 Flash (semantic translation)

**Infrastructure:**
- GCP Cloud Run (API hosting)
- GCP Firestore (database)
- GCP Cloud Storage (images)

## Documentation

See [Spec.md](./Spec.md) for complete technical specification.

See [Todo.md](./Todo.md) for detailed development roadmap.

See [Claude.md](./Claude.md) for AI-assisted development context.
