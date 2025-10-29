# [![nyrkio-logo]][product]

Nyrkiö is an open source platform for change detection in a *Continuous Performance Engineering*
workflow.

- Submit results using a [REST API][nyrkio-getting-started] or [GitHub Action][github-action]
- Uses state of the art change point detection algorithm to find performance regressions and improvements in noisy data.
  Nyrkiö can find even small regressions down to 0.5% - 1%.
- Integrates with GitHub to identify the git commit that caused a change in performance

## Using Nyrkiö Change Detection

This software runs [nyrkio.com][dotcom]. Some links to get you started:

[Getting Started with Nyrkiö in 3 easy steps][nyrkio-getting-started]

[Read more about how it works and who else is using it][product]

![nyrkio-footer-graph]

## Developers

### Apache Otava (incubating)

Nyrkiö is a web service around the 8 year old, battle tested [Apache Otava (incubating)][otava]
command line tool. Otava was created and open sourced by the performance teams at MongoDB (2017) and
Datastax (2020). It is used by technology companies large and small, such as Netflix, Dremio, Hazelcast...

### Nyrkiö (.com)

Also the web service itself is open source.

The frontend is implemented using React and the backend is built on top of FastAPI and Pydantic.

## Quick Start for Developers

### Installation

Clone the repository and install dependencies:

```bash
git clone git@github.com:nyrkio/nyrkio.git
cd nyrkio

# Initialize submodules
git submodule init
git submodule update

# Install backend dependencies
cd backend
poetry install
cd ..

# Create environment file
cat > .env.backend << 'EOF'
DB_URL=mongodb://localhost:27017/nyrkiodb
DB_NAME=nyrkiodb
POSTMARK_API_KEY=
GITHUB_CLIENT_SECRET=
SECRET_KEY=
API_PORT=8001
EOF
```

**Prerequisites:**
- Python 3.8+
- Poetry (`curl -sSL https://install.python-poetry.org | python3 -`)
- MongoDB (locally or via Docker)
- Node.js & npm (for frontend)

### Running the Backend

After installation, you can start the backend using:

```bash
# Start backend server (runs on port 8001 by default)
python3 etc/nyrkio_backend.py start

# Check backend status
python3 etc/nyrkio_backend.py status

# Stop backend server
python3 etc/nyrkio_backend.py stop

# Restart backend server
python3 etc/nyrkio_backend.py restart
```

The backend API will be available at:
- API: http://localhost:8001
- OpenAPI docs: http://localhost:8001/docs

To customize the port, edit the `.env.backend` file and set `API_PORT` to your desired port.

### Running the Full Stack with Docker

To run the complete stack (backend, webhooks, MongoDB, nginx):

```bash
# Start Docker stack
python3 etc/nyrkio_docker.py start

# Check Docker stack status
python3 etc/nyrkio_docker.py status

# Stop Docker stack
python3 etc/nyrkio_docker.py stop

# Restart Docker stack
python3 etc/nyrkio_docker.py restart
```

Services will be available at:
- Backend API: http://localhost:8000
- Webhooks: http://localhost:8080
- Nginx proxy: http://localhost:80
- MongoDB: localhost:27017

### Frontend Development

If you want to hack on the frontend you can run `npm` directly from inside of the `frontend` directory.
The configuration file `vite.config.js` can be pointing to the real nyrkio.com backend API.

```bash
cd frontend
npm install
npm run dev
```

### Manual Installation

If you prefer to install manually:

```bash
git clone git@github.com:nyrkio/nyrkio.git
cd nyrkio
git submodule init
git submodule update

# Create environment file
cat > .env.backend << END
DB_URL=mongodb://mongodb.nyrkio.local:27017/mongodb
DB_NAME=nyrkiodb
POSTMARK_API_KEY=
GITHUB_CLIENT_SECRET=
SECRET_KEY=
API_PORT=8001

#HUNTER_CONFIG=
#GRAFANA_USER=
#GRAFANA_PASSWORD=
END

# Install dependencies
cd backend
poetry install

# Start backend
cd ..
python3 etc/nyrkio_backend.py start
```

For Docker-based deployment:

```bash
export IMAGE_TAG=$(git rev-parse HEAD)
docker compose -f docker-compose.dev.yml up --build
```

### Contributing Changes

Please open a pull request with your changes against the `main` branch. PRs allow us to run linters and tests against your modifications.

## References

- [The Use of Change Point Detection to Identify Software Performance Regressions in a Continuous Integration System](https://arxiv.org/pdf/2003.00584)
- [Hunter: Using Change Point Detection to Hunt for Performance](https://arxiv.org/pdf/2301.03034.pdf)


[product]: https://nyrkio.com/product
[dotcom]: https://nyrkio.com
[nyrkio-getting-started]: https://nyrkio.com/docs/getting-started
[nyrkio-logo]: https://nyrkio.com/p/logo/full/Brown/NyrkioLogo_Final_Full_Brown-200px.png
[nyrkio-footer-graph]: https://nyrkio.com/assets/footer-white-graphic-8R7Ap4-5.png
[github-action]: https://github.com/nyrkio/change-detection
[otava]: https://otava.apache.org

## License

Licensed under the [Apache License, Version 2.0](https://opensource.org/license/apache-2-0/) ("the license"); you may not use these files except in compliance with the License. You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0


Apache and Apache Otava are trademarks of the Apache Software Foundation
Nyrkiö and Nyrkiö Change Detection are trademarks of Nyrkiö Oy






