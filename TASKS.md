# Development Tasks

## Phase 1: Project Setup

### 1. ✅ Project Structure
- Created monorepo at `/Users/simon/otherwhere/`
- Directories: `frontend/`, `backend/`, `data-ingestion/`, `docs/`

### 2. ✅ Git & Documentation
- Initialized Git repository
- Created comprehensive `.gitignore`
- Created `Spec.md` with full technical specification

### 3. Documentation Files
**Status:** In Progress

Create:
- `Todo.md` - Detailed task breakdown
- `Claude.md` - AI assistant context file

---

## Phase 2: Frontend Setup

### 4. Initialize Vite + React + TypeScript
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

### 5. Install Dependencies
```bash
npm install tailwindcss postcss autoprefixer
npm install zustand @tanstack/react-query
npm install react-router-dom
```

Configure Tailwind, set up folder structure.

---

## Phase 3: Backend Setup

### 6. Initialize Go Module
```bash
cd backend
go mod init github.com/username/otherwhere
go get github.com/go-chi/chi/v5
go get github.com/go-chi/cors
```

Create basic server with chi router and slog.

### 7. Docker Compose
Create `docker-compose.yml` with Firestore emulator.

---

## Phase 4: Data Pipeline

### 8. Python Environment
```bash
cd data-ingestion
python3 -m venv venv
source venv/bin/activate
```

Create `requirements.txt` with: requests, pandas, geopy

### 9. Define Schema
Create shared destination schema in:
- `backend/types/destination.go`
- `frontend/src/types/destination.ts`

### 10. Data Ingestion Script
Build Python script to:
- Fetch from OSM Overpass API
- Fetch from Wikidata
- Normalize features to [0,1]
- Output JSON

---

## Phase 5: Core Backend Logic

### 11. Ranking Algorithm
Implement distance-based scoring in Go.

### 12. API Endpoints
- `POST /api/search`
- `GET /api/destinations/:id`
- `GET /api/destinations`

---

## Phase 6: Frontend UI

### 13. Layout & Routing
- Home page with search
- Results page
- Destination detail route

### 14. Search Component
- Input field
- Results grid/list
- Loading states (TanStack Query)

### 15. Destination Detail
Client-side route showing full destination info.

---

## Phase 7: AI Integration (Deferred)

### 16. Gemini Integration
Add semantic translation in Go API.
Requires GCP setup first.

---

## Phase 8: Deployment (Post-MVP)

### 17. GCP Setup
- Create project
- Enable APIs
- Service account

### 18. Deploy API
Cloud Run deployment.

### 19. Deploy Frontend
Static hosting on Cloud Storage.

### 20. Images
Wikimedia Commons integration and caching.

---

**See Spec.md for full details on each component.**
