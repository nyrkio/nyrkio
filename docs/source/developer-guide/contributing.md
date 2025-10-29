# Contributing

Thank you for your interest in contributing to Nyrkiö!

## Getting Started

1. **Fork the repository**
   ```bash
   gh repo fork nyrkio/nyrkio --clone
   ```

2. **Set up development environment**
   ```bash
   cd nyrkio
   git submodule init && git submodule update
   cd backend && poetry install && cd ..
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature-name
   ```

## Development Workflow

### 1. Make Changes

Edit code in the appropriate directory:
- Backend: `backend/`
- Frontend: `frontend/`
- Documentation: `docs/`

### 2. Run Tests

```bash
cd backend
./runtests.sh all
```

Ensure all tests pass before submitting PR.

### 3. Format and Lint

```bash
./runtests.sh format --fix
./runtests.sh lint --fix
```

### 4. Update Documentation

If you're adding features or changing behavior:
- Update relevant docs in `docs/source/`
- Update DEVELOPMENT.md if needed
- Update README.md if needed

### 5. Write Tests

All new features must include tests:
- Unit tests for new functions
- Integration tests for new endpoints
- Frontend tests for new components

### 6. Commit Changes

Use conventional commit messages:

```bash
git add .
git commit -m "feat: add support for custom metrics"
```

**Commit types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 7. Push and Create PR

```bash
git push origin feature-name
gh pr create --title "Add support for custom metrics" --body "Description..."
```

## Code Standards

### Python (Backend)

**Style Guide:**
- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Maximum line length: 100 characters

**Example:**
```python
async def calculate_change_magnitude(
    before: list[float],
    after: list[float]
) -> float:
    """Calculate percentage change between two datasets.

    Args:
        before: Data points before change
        after: Data points after change

    Returns:
        Percentage change as float (0.15 = 15%)
    """
    before_mean = sum(before) / len(before)
    after_mean = sum(after) / len(after)
    return (after_mean - before_mean) / before_mean
```

### JavaScript/React (Frontend)

**Style Guide:**
- Use ESLint configuration
- Functional components with hooks
- PropTypes or TypeScript
- Descriptive component names

**Example:**
```jsx
import PropTypes from 'prop-types';

/**
 * Display performance metric with change indicator
 */
export function MetricDisplay({ name, value, change }) {
  const changeClass = change > 0 ? 'increase' : 'decrease';

  return (
    <div className="metric">
      <h3>{name}</h3>
      <span className="value">{value}</span>
      <span className={changeClass}>{change}%</span>
    </div>
  );
}

MetricDisplay.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.number.isRequired,
  change: PropTypes.number
};
```

## Testing Requirements

### Backend Tests

All backend changes must include:

1. **Unit tests** for new functions
2. **Integration tests** for new endpoints
3. **Coverage** of at least 80% for new code

Run tests:
```bash
cd backend
./runtests.sh all
```

### Frontend Tests

Frontend changes should include:

1. **Component tests** for new components
2. **Integration tests** for user flows
3. **Snapshot tests** where appropriate

Run tests:
```bash
cd frontend
npm run test
```

## Documentation

Update documentation for:

- **New features** → User guide
- **API changes** → API reference
- **Architecture changes** → Developer guide
- **Configuration** → Installation guide

Documentation format:
- Markdown files in `docs/source/`
- Build locally: `cd docs && sphinx-build -b html source build/html`

## Pull Request Process

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted and linted
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### PR Description

Include:

1. **What** - What does this PR do?
2. **Why** - Why is this change needed?
3. **How** - How does it work?
4. **Testing** - How was it tested?

Example:
```markdown
## What
Adds support for custom metric units in test results.

## Why
Users need to specify custom units (e.g., "req/s", "MB/s") that aren't predefined.

## How
- Extended Metric model to accept arbitrary unit strings
- Added validation to ensure unit is non-empty
- Updated frontend to display custom units

## Testing
- Added unit tests for new validation
- Integration test for custom unit submission
- Manual testing with various unit strings
```

### Review Process

1. Automated CI checks must pass
2. At least one maintainer approval required
3. Address review feedback
4. Squash commits if needed
5. Maintainer will merge when ready

## Issue Guidelines

### Reporting Bugs

Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version, etc.)
- Relevant logs or screenshots

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Impact on existing functionality

## Code Review Guidelines

### As a Reviewer

- Be respectful and constructive
- Focus on code, not the person
- Suggest improvements with examples
- Approve when standards are met

### As an Author

- Respond to all feedback
- Ask questions if unclear
- Make requested changes
- Update PR description if scope changes

## Community Guidelines

- Be welcoming and inclusive
- Respect different viewpoints
- Accept constructive criticism
- Focus on what's best for the project

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions or discuss ideas
- **DEVELOPMENT.md**: Detailed development guide
- **Slack** (if available): Real-time communication

## Recognition

Contributors are recognized in:
- Release notes
- Contributors list
- GitHub insights

Thank you for contributing to Nyrkiö!
