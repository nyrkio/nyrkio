# Architecture

Comprehensive architecture documentation for Nyrkiö.

## Topics

- [Overview](overview.md) - High-level system architecture
- [Change Detection](change-detection.md) - E-Divisive algorithm and Hunter integration
- [Database](database.md) - MongoDB schema and indexing strategy
- [Caching](caching.md) - Performance optimization with caching

## Key Technologies

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: React, Vite
- **Database**: MongoDB
- **Change Detection**: Apache Otava (Hunter)
- **Authentication**: JWT
- **Deployment**: Docker, Nginx

## Design Principles

1. **Async First** - All I/O operations are async
2. **Stateless API** - Horizontal scaling support
3. **Data Locality** - Minimize database queries
4. **Progressive Enhancement** - Works without JavaScript
5. **API-First** - Strong API contracts
