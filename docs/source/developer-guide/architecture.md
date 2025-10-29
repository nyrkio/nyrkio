# Architecture Overview

Nyrkiö follows a modern three-tier web architecture with microservices patterns.

## System Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│   Frontend   │────▶│   Backend   │
│   (React)   │◀────│    (Vite)    │◀────│  (FastAPI)  │
└─────────────┘     └──────────────┘     └─────────────┘
                                                 │
                                                 ▼
                           ┌──────────────────────────────────┐
                           │                                  │
                    ┌──────▼──────┐              ┌──────────▼──────┐
                    │   MongoDB   │              │     Hunter      │
                    │  (Database) │              │ (Change Detect) │
                    └─────────────┘              └─────────────────┘
```

## Frontend (React + Vite)

**Technology Stack:**
- React 18 with functional components
- Vite for build tooling
- React Router for navigation
- TanStack Query for data fetching
- Recharts for visualization

**Key Features:**
- Fast HMR (Hot Module Replacement)
- Code splitting
- Lazy loading
- Responsive design

## Backend (FastAPI)

**Technology Stack:**
- FastAPI web framework
- Uvicorn ASGI server
- Pydantic for validation
- Motor for async MongoDB access
- JWT for authentication

**Architecture Patterns:**
- RESTful API design
- Async/await throughout
- Dependency injection
- Repository pattern for data access

## Database (MongoDB)

**Collections:**
- `users` - User accounts
- `tests` - Test configurations
- `results` - Test results
- `changes` - Detected change points
- `organizations` - Team workspaces

**Indexes:**
- Compound indexes for query optimization
- TTL indexes for data expiration
- Text indexes for search

## Change Detection (Hunter)

Apache Otava (Hunter submodule) provides change point detection:

- **Algorithm**: E-Divisive with permutation testing
- **Language**: Python
- **Integration**: Called as library from backend

## Communication Flow

### Submit Test Results

```
Browser → POST /api/v0/result/{test_name}
         → FastAPI validates with Pydantic
         → MongoDB stores result
         → Hunter analyzes for changes
         → Response with change_id
```

### View Results

```
Browser → GET /api/v0/result/{test_name}
        → FastAPI queries MongoDB
        → Data transformation
        → JSON response
        → React renders charts
```

## Security

- JWT tokens for authentication
- HTTPS for all production traffic
- CORS configuration for frontend
- Rate limiting per token
- Input validation with Pydantic

## Scalability

- Stateless API servers (horizontal scaling)
- MongoDB replica sets
- Redis caching layer (optional)
- CDN for static assets
- Async operations throughout
