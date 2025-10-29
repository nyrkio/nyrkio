# System Overview

Nyrkiö follows a three-tier architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        Internet                          │
└──────────────────────────┬──────────────────────────────┘
                           │
                  ┌────────▼────────┐
                  │  Nginx (443)    │  ← SSL Termination
                  │  Reverse Proxy  │  ← Rate Limiting
                  └────────┬────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌─────▼──────┐   ┌─────▼──────┐   ┌─────▼──────┐
   │  Frontend  │   │  Backend   │   │  Webhooks  │
   │   (Vite)   │   │ (FastAPI)  │   │  Service   │
   │  Port 5173 │   │  Port 8001 │   │  Port 8080 │
   └────────────┘   └─────┬──────┘   └─────┬──────┘
                          │                 │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
             ┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
             │   MongoDB   │ │  Hunter  │ │   GitHub    │
             │  Port 27017 │ │  (Local) │ │     API     │
             └─────────────┘ └──────────┘ └─────────────┘
```

## Components

### Frontend (React + Vite)

**Responsibilities:**
- User interface rendering
- Data visualization (charts, graphs)
- Client-side routing
- API requests to backend
- Real-time updates

**Technology:**
- React 18 with hooks
- Vite for fast development/build
- TanStack Query for data fetching
- Recharts for visualization
- React Router for navigation

**Deployment:**
- Development: Vite dev server (port 5173)
- Production: Static files served by Nginx

### Backend (FastAPI)

**Responsibilities:**
- REST API endpoints
- Authentication and authorization
- Business logic
- Database operations
- Change point detection
- Notifications (Slack, GitHub)

**Technology:**
- FastAPI web framework
- Uvicorn ASGI server
- Motor (async MongoDB driver)
- Pydantic for validation
- JWT for auth tokens

**Deployment:**
- Development: Uvicorn with auto-reload
- Production: Uvicorn + Gunicorn workers

### Database (MongoDB)

**Responsibilities:**
- Persistent storage
- Test results
- User accounts
- Change points
- Configuration

**Schema:**
- `users` - User accounts and settings
- `tests` - Test configurations
- `results` - Time-series performance data
- `changes` - Detected change points
- `organizations` - Team workspaces

**Scaling:**
- Replica sets for high availability
- Sharding for large datasets
- Indexes for query performance

### Change Detection (Hunter)

**Responsibilities:**
- Statistical change point detection
- E-Divisive algorithm implementation
- Significance testing
- Magnitude calculation

**Integration:**
- Git submodule in `backend/hunter/`
- Called as Python library
- Async execution
- Cached results

### Webhooks Service

**Responsibilities:**
- GitHub webhook handling
- PR comment posting
- Issue creation
- Status updates

**Technology:**
- FastAPI microservice
- Async HTTP requests
- GitHub API integration

## Data Flow

### Submit Test Results

```
┌────────┐   POST /api/v0/result/{test}   ┌─────────┐
│        │──────────────────────────────▶│         │
│ Client │                                │ Backend │
│        │◀──────────────────────────────│         │
└────────┘        200 + change_id        └────┬────┘
                                               │
                                        ┌──────▼──────┐
                                        │   Validate  │
                                        │  with       │
                                        │  Pydantic   │
                                        └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │   Store in  │
                                        │   MongoDB   │
                                        └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │   Analyze   │
                                        │   with      │
                                        │   Hunter    │
                                        └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │   Notify    │
                                        │   if needed │
                                        └─────────────┘
```

### View Results

```
┌────────┐   GET /api/v0/result/{test}    ┌─────────┐
│        │──────────────────────────────▶│         │
│ Client │                                │ Backend │
│        │◀──────────────────────────────│         │
└────────┘   200 + JSON data             └────┬────┘
                                               │
                                        ┌──────▼──────┐
                                        │   Query     │
                                        │   MongoDB   │
                                        └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │  Transform  │
                                        │    data     │
                                        └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │   Add       │
                                        │   metadata  │
                                        └─────────────┘
```

## Security

### Authentication Flow

```
1. User → GitHub OAuth
2. GitHub → Authorization Code
3. Backend → Exchange for Token
4. Backend → Create JWT
5. Backend → Return JWT to User
6. User → Include JWT in all requests
7. Backend → Validate JWT
```

### Security Measures

- HTTPS for all production traffic
- JWT tokens with expiration
- CORS configuration
- Rate limiting per token
- Input validation (Pydantic)
- MongoDB connection encryption
- Secret management (environment variables)

## Scalability

### Horizontal Scaling

- **Backend**: Stateless, can run multiple instances
- **Frontend**: Static files, CDN distribution
- **Database**: MongoDB replica sets + sharding

### Vertical Scaling

- **Backend**: Multi-process Gunicorn
- **Database**: Larger instance size
- **Caching**: Redis for hot data

### Performance Optimization

- Async I/O throughout
- Database indexing
- Query optimization
- Result caching
- Lazy loading in frontend
- Code splitting
