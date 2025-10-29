# Developer Guide

Welcome to the Nyrkiö developer guide! This section covers everything you need to contribute to the project.

## Quick Setup

```bash
# Clone and setup
git clone https://github.com/nyrkio/nyrkio.git
cd nyrkio
git submodule init && git submodule update

# Install backend
cd backend
poetry install
cd ..

# Start backend
python3 etc/nyrkio_backend.py start

# Start frontend (separate terminal)
python3 etc/nyrkio_frontend.py start
```

## Development Topics

- **[Architecture](architecture.md)** - System design and component overview
- **[Backend Development](backend.md)** - FastAPI backend development
- **[Frontend Development](frontend.md)** - React frontend development
- **[Testing](testing.md)** - Writing and running tests
- **[Contributing](contributing.md)** - Contribution guidelines

## Prerequisites

- Python 3.8+
- Poetry
- Node.js & npm
- MongoDB
- Git

See [Installation](../getting-started/installation.md) for detailed setup instructions.

## Project Structure

```
nyrkio/
├── backend/              # FastAPI backend
│   ├── api/             # API endpoints
│   ├── core/            # Business logic
│   ├── db/              # Database models
│   ├── github/          # GitHub integration
│   ├── notifiers/       # Notification services
│   ├── tests/           # Unit tests
│   └── hunter/          # Change detection (submodule)
├── frontend/             # React frontend
│   ├── src/             # React components
│   ├── public/          # Static assets
│   └── vite.config.*.js # Vite configurations
├── docs/                 # Sphinx documentation
├── etc/                  # Management scripts
├── nginx/                # Nginx configuration
└── docker-compose.*.yml  # Docker configurations
```

## Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature-name
   ```

2. **Make changes**
   - Edit code in relevant directories
   - Backend changes auto-reload with `--reload` flag
   - Frontend uses Vite's hot module replacement

3. **Run tests**
   ```bash
   cd backend
   ./runtests.sh all
   ```

4. **Format and lint**
   ```bash
   ./runtests.sh format --fix
   ./runtests.sh lint --fix
   ```

5. **Commit and push**
   ```bash
   git add .
   git commit -m "Description"
   git push origin feature-name
   ```

6. **Create pull request**
   - Open PR on GitHub against `main` branch
   - Ensure CI checks pass
   - Request review

## Code Standards

### Python (Backend)

- **Style**: Follow PEP 8
- **Formatter**: Ruff
- **Linter**: Ruff
- **Type hints**: Use type annotations
- **Docstrings**: Google style

### JavaScript/React (Frontend)

- **Style**: ESLint configuration
- **Formatter**: Prettier
- **Components**: Functional components with hooks
- **State**: React hooks and context

### Testing

- **Backend**: pytest with >80% coverage
- **Frontend**: Vitest for unit tests
- **Integration**: Full API integration tests

## Documentation

- **Format**: Markdown (using MyST parser)
- **Tool**: Sphinx
- **Hosting**: ReadTheDocs
- **Location**: `docs/source/`

Update documentation when making changes:
```bash
cd docs
sphinx-build -b html source build/html
```

## Getting Help

- GitHub Issues: https://github.com/nyrkio/nyrkio/issues
- Discussions: https://github.com/nyrkio/nyrkio/discussions
- DEVELOPMENT.md: Detailed development guide
