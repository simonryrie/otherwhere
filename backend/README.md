# Otherwhere Backend

Go REST API for the Otherwhere travel inspiration platform.

## Structure

```
backend/
├── cmd/
│   └── server/          # Main application entry point
├── internal/
│   ├── handlers/        # HTTP request handlers
│   ├── types/           # Data types and models
│   └── ranking/         # Destination ranking logic
├── go.mod
└── go.sum
```

## Running Locally

```bash
# Run the server
go run cmd/server/main.go

# Server will start on http://localhost:8080
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/destinations` - List all destinations
- `GET /api/destinations/:id` - Get destination by ID
- `POST /api/search` - Search destinations with semantic query

## Dependencies

- **chi** - Lightweight HTTP router
- **cors** - CORS middleware
- **slog** - Structured logging (standard library)

## Development

The server uses structured JSON logging via slog. All logs are output to stdout.

CORS is configured for local development to allow requests from:
- http://localhost:5173
- http://localhost:5174
