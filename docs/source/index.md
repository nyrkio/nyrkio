# Nyrkiö Documentation

**Open Source Performance Change Detection Platform**

Nyrkiö is an open-source platform for continuous performance engineering that detects even small performance changes (down to 0.5-1%) in noisy test data using state-of-the-art change point detection algorithms.

```{toctree}
---
maxdepth: 2
caption: Getting Started
---
getting-started/index
getting-started/installation
getting-started/quick-start
getting-started/concepts
```

```{toctree}
---
maxdepth: 2
caption: User Guide
---
user-guide/index
user-guide/submitting-results
user-guide/viewing-changes
user-guide/configuration
user-guide/notifications
user-guide/organizations
user-guide/pull-requests
```

```{toctree}
---
maxdepth: 2
caption: API Reference
---
api-reference/index
api-reference/rest-api
api-reference/authentication
api-reference/data-models
api-reference/cli
```

```{toctree}
---
maxdepth: 2
caption: Developer Guide
---
developer-guide/index
developer-guide/architecture
developer-guide/backend
developer-guide/frontend
developer-guide/testing
developer-guide/contributing
```

```{toctree}
---
maxdepth: 2
caption: Architecture
---
architecture/index
architecture/overview
architecture/change-detection
architecture/database
architecture/caching
```

```{toctree}
---
maxdepth: 2
caption: Deployment
---
deployment/index
deployment/docker
deployment/production
deployment/configuration
deployment/monitoring
```

## Features

- **Accurate Change Detection**: Detect performance changes as small as 0.5-1%
- **Handles Noisy Data**: Advanced algorithms work with real-world noisy performance data
- **GitHub Integration**: Native support for GitHub Actions and Pull Requests
- **Multiple Notifications**: Slack and GitHub issue/comment notifications
- **Team Collaboration**: Organization support for shared performance tracking
- **Public Dashboards**: Share performance results publicly
- **REST API**: Easy integration with any CI/CD system
- **Open Source**: Apache 2.0 licensed

## Quick Links

- [Installation Guide](getting-started/installation.md)
- [API Documentation](api-reference/rest-api.md)
- [GitHub Repository](https://github.com/nyrkio/nyrkio)
- [Live Demo](https://nyrkio.com)

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
