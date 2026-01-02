# Claude.md - AI Assistant Context

## Project Overview

**Otherwhere** is an AI-curated travel inspiration board that helps users discover destinations based on vibes (e.g., "chill, low tourists, warm") rather than traditional filters.

**Key Principle:** AI translates user intent into feature constraints. It does NOT rank destinations or make decisions.

---

## Architecture

- **Frontend:** Vite + React + TypeScript + Tailwind
- **Backend:** Go (chi router, slog logging)
- **Data:** Python scripts for ETL
- **AI:** Gemini 1.5 Flash (semantic translation only)
- **Infrastructure:** GCP (Cloud Run, Firestore, Cloud Storage)

---

## Code Style & Preferences

### TypeScript/React
- Use functional components with hooks
- Zustand for UI state, TanStack Query for server state
- Tailwind for styling (no CSS-in-JS)
- Prefer explicit types over inference where it aids readability
- Keep components small and focused

### Go
- Use `slog` for all logging (structured, JSON format)
- Chi for routing with middleware pattern
- Keep handlers thin, business logic in separate packages
- Error handling: explicit returns, no panics in request handlers
- Use `context.Context` for cancellation and timeouts

### Python
- Type hints where helpful (not everywhere)
- Pandas for data wrangling
- Keep scripts simple and readable
- Document data transformations with comments
- Use `requests` for HTTP, avoid overcomplicated async

---

## Important Decisions

### What NOT to Do
- ❌ Don't add SSR/SSG (Vite is sufficient)
- ❌ Don't train ML models (use semantic translation only)
- ❌ Don't add user accounts in MVP
- ❌ Don't add map view in MVP (deferred to v2)
- ❌ Don't over-engineer (keep it simple)

### Key Constraints
- Feature vectors are normalized to [0, 1]
- Destinations are pre-computed (no runtime ETL)
- LLM output must be validated against JSON schema
- All features are explainable (no black boxes)

---

## Development Workflow

### Local Development
```bash
# Terminal 1: Firestore emulator
docker-compose up firestore

# Terminal 2: Go API
cd backend && go run main.go

# Terminal 3: Vite
cd frontend && npm run dev
```

### GCP Integration
Deferred until local development is complete.

---

## Common Patterns

### Destination Feature Vector
All destinations have this structure:
```typescript
{
  id: string
  name: string
  country: string
  type: "city" | "region"
  location: { lat: number, lon: number }
  features: {
    avg_temp_c: number          // [0, 1] normalized
    population_density: number   // [0, 1]
    tourism_density: number      // [0, 1]
    nature_ratio: number         // [0, 1]
    // ... more features
  }
  images: string[]
}
```

### Semantic Translation Flow
1. User input: "chill, warm, low tourists"
2. Gemini translates to: `{ tourism_density: { max: 0.3 }, avg_temp_c: { min: 20 } }`
3. Go validates JSON schema
4. Go ranks destinations by distance from constraints
5. Frontend displays results

---

## When Helping

### Prioritize
1. **Frontend polish** - This is a visual product
2. **Explainability** - All decisions must be traceable
3. **Simplicity** - MVP scope, avoid feature creep
4. **Type safety** - Shared schema between TS/Go

### Ask Before
- Adding new dependencies
- Changing the semantic translation approach
- Adding features outside MVP scope
- Modifying the ranking algorithm

### Refer to Spec.md
For detailed technical decisions, data sources, and architecture.

---

## Current Status

**Phase:** Initial setup
**Next:** Frontend and backend scaffolding

See TASKS.md for detailed task breakdown.
