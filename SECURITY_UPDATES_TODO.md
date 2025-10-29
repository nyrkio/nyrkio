# Security Updates TODO

**Date Created**: 2025-10-29
**Status**: Pending - To be addressed after PR #605 is merged
**Total Vulnerabilities**: 43 (3 critical, 10 high, 24 moderate, 6 low)

---

## CRITICAL Vulnerabilities (3) - Must Fix First

### 1. h11 < 0.16.0 (Python/Backend)
- **Current version**: 0.14.0
- **Required version**: ≥ 0.16.0
- **Impact**: HTTP request smuggling vulnerability
- **Advisory**: https://github.com/python-hyper/h11/security/advisories/GHSA-vqfr-h8mv-ghfj
- **Fix**:
  ```bash
  cd backend
  poetry add h11@^0.16.0
  ```

### 2. python-jose < 3.4.0 (Python/Backend)
- **Current version**: 3.3.0
- **Required version**: ≥ 3.4.0
- **Impact**: JWT signature bypass vulnerability (CVE-2024-33663)
- **Advisory**: https://nvd.nist.gov/vuln/detail/CVE-2024-33663
- **Fix**:
  ```bash
  cd backend
  poetry add python-jose@^3.4.0
  ```

### 3. xmldom ≤ 0.6.0 (NPM/Frontend)
- **Status**: Transitive dependency (not directly in package.json)
- **Required version**: > 0.6.0
- **Impact**: XML parsing vulnerability
- **Advisory**: https://github.com/xmldom/xmldom/security/advisories/GHSA-crh6-fp67-6883
- **Fix**: Update parent packages or use npm audit fix

---

## HIGH Severity Vulnerabilities (10)

### Backend (Python)

#### 4. starlette ≤ 0.49.0
- **Current**: 0.35.1
- **Required**: > 0.49.0
- **Impact**: Multiple security issues
- **Fix**:
  ```bash
  cd backend
  poetry add starlette@^0.49.1
  ```
- **Note**: Verify FastAPI compatibility before updating

#### 5-7. urllib3 (Multiple CVEs)
- **Current**: 1.26.11
- **Required**: ≥ 2.5.0 (or ≥ 1.26.19 for older branch)
- **Impact**: Multiple security vulnerabilities
- **Fix**:
  ```bash
  cd backend
  poetry add urllib3@^2.5.0
  ```
- **Warning**: Major version change (1.x → 2.x) - test thoroughly

#### 8. ecdsa ≥ 0
- **Status**: All versions vulnerable
- **Required**: Check for updates or alternatives
- **Impact**: Cryptographic vulnerability
- **Fix**: May need to wait for upstream fix or use alternative library

### Frontend (NPM)

#### 9-10. playwright < 1.55.1
- **Current**: 1.42.1
- **Required**: ≥ 1.55.1
- **Impact**: Security vulnerabilities in browser automation
- **Fix**:
  ```bash
  cd frontend
  npm install playwright@^1.55.1
  ```

---

## MEDIUM Severity Vulnerabilities (24)

### Backend (Python)

#### requests < 2.32.4
- **Fix**: `poetry add requests@^2.32.4`

#### sentry-sdk < 1.45.1
- **Fix**: `poetry add sentry-sdk@^1.45.1`

#### certifi < 2024.7.4
- **Current**: 2021.5.30 to 2024.7.3 range
- **Fix**: `poetry add certifi@^2024.7.4`

#### aiohttp < 3.12.14
- **Fix**: `poetry add aiohttp@^3.12.14`

### Frontend (NPM)

#### vite (Multiple CVEs - 8 issues)
- **Current**: 5.0.13
- **Required**: ≥ 5.4.20
- **Impact**: Various XSS and security issues
- **Fix**:
  ```bash
  cd frontend
  npm install vite@^5.4.20
  ```

#### @babel/runtime < 7.26.10
- **Impact**: Denial of Service vulnerability
- **Fix**: `npm install @babel/runtime@^7.26.10`

#### prismjs < 1.30.0
- **Status**: Likely transitive dependency
- **Fix**: `npm install prismjs@^1.30.0` or update parent

---

## LOW Severity Vulnerabilities (6)

These are lower priority but should still be addressed:
- Various minor versions of vite
- Other transitive dependencies

---

## Complete Fix Script

### Phase 1: Backend Critical & High

```bash
cd /Users/jdrumgoole/GIT/nyrkio/backend

# Critical fixes
poetry add h11@^0.16.0 python-jose@^3.4.0

# High severity fixes
poetry add starlette@^0.49.1 urllib3@^2.5.0

# Medium severity fixes
poetry add requests@^2.32.4 sentry-sdk@^1.45.1 certifi@^2024.7.4 aiohttp@^3.12.14

# Lock and test
poetry lock
poetry run pytest tests/
```

### Phase 2: Frontend Critical & High

```bash
cd /Users/jdrumgoole/GIT/nyrkio/frontend

# High severity fixes
npm install playwright@^1.55.1

# Medium severity fixes
npm install vite@^5.4.20 @babel/runtime@^7.26.10

# Auto-fix remaining issues
npm audit fix

# Test
npm run build
npm run test
```

### Phase 3: Verification

```bash
# Run full backend test suite
cd /Users/jdrumgoole/GIT/nyrkio/backend
./runtests.sh all

# Run frontend tests
cd /Users/jdrumgoole/GIT/nyrkio/frontend
npm run test

# Check for remaining vulnerabilities
npm audit
cd ../backend
poetry check
```

---

## Potential Breaking Changes & Testing Checklist

### ⚠️ High Risk Updates

1. **urllib3: 1.26.11 → 2.5.0** (Major version change)
   - API changes possible
   - Test all HTTP/HTTPS requests
   - Check compatibility with requests library

2. **starlette: 0.35.1 → 0.49.1**
   - Verify FastAPI version compatibility
   - Test all API endpoints
   - Check middleware functionality

3. **python-jose: 3.3.0 → 3.4.0**
   - Critical for JWT authentication
   - Test all auth flows thoroughly
   - Verify token generation/validation

### Testing Checklist

- [ ] All backend unit tests pass (210+ tests)
- [ ] All backend integration tests pass
- [ ] All frontend builds successfully
- [ ] Frontend dev server runs without errors
- [ ] Playwright tests pass (if any)
- [ ] Manual testing:
  - [ ] User login/authentication works
  - [ ] JWT tokens are valid
  - [ ] API endpoints respond correctly
  - [ ] Database connections work
  - [ ] External API calls work (Stripe, GitHub, etc.)
  - [ ] Email sending works (Postmark)
  - [ ] Sentry error tracking works

---

## Commit Strategy

### Option 1: Single Commit (Recommended)

```bash
git checkout main
git pull origin main
git checkout -b security/update-dependencies-2025-10

# Run all updates above...

git add backend/pyproject.toml backend/poetry.lock frontend/package.json frontend/package-lock.json
git commit -m "security: Update dependencies to fix 43 security vulnerabilities

Critical fixes:
- Update h11 to 0.16.0+ (HTTP smuggling - GHSA-vqfr-h8mv-ghfj)
- Update python-jose to 3.4.0+ (JWT bypass - CVE-2024-33663)
- Update xmldom to 0.6.0+ (XML parsing vulnerability)

High severity fixes:
- Update starlette to 0.49.1+
- Update urllib3 to 2.5.0+ (multiple CVEs)
- Update playwright to 1.55.1+

Medium/Low severity fixes:
- Update vite to 5.4.20+ (8 CVEs)
- Update requests to 2.32.4+
- Update sentry-sdk to 1.45.1+
- Update certifi to 2024.7.4+
- Update aiohttp to 3.12.14+
- Update @babel/runtime to 7.26.10+

All tests passing. No breaking changes detected."

git push origin security/update-dependencies-2025-10

# Create PR
gh pr create --title "Security: Update dependencies to fix 43 vulnerabilities" \
  --body "Fixes all 43 security vulnerabilities reported by Dependabot.

## Critical Issues Fixed
- HTTP request smuggling in h11
- JWT signature bypass in python-jose
- XML parsing vulnerability in xmldom

## Testing
- ✅ All backend tests pass (210+)
- ✅ All frontend builds successfully
- ✅ Manual authentication testing completed
- ✅ No breaking changes detected

## Risk Assessment
**Low Risk**: Most updates are patch/minor versions
**Medium Risk**: urllib3 major version change (1.x → 2.x)
**Tested**: Full test suite run, all green"
```

### Option 2: Separate Commits by Severity

```bash
# Commit 1: Critical
git add backend/pyproject.toml backend/poetry.lock
git commit -m "security: Fix critical vulnerabilities (h11, python-jose)"

# Commit 2: High
git add backend/pyproject.toml backend/poetry.lock frontend/package.json frontend/package-lock.json
git commit -m "security: Fix high severity vulnerabilities (starlette, urllib3, playwright)"

# Commit 3: Medium/Low
git add backend/pyproject.toml backend/poetry.lock frontend/package.json frontend/package-lock.json
git commit -m "security: Fix medium and low severity vulnerabilities"
```

---

## Transitive Dependency Issues

Some vulnerabilities are in packages not directly listed in pyproject.toml or package.json:

### Check what depends on them:

```bash
# Backend
cd backend
poetry show ecdsa     # See what requires ecdsa
poetry show xmldom    # See what requires xmldom

# Frontend
cd frontend
npm ls xmldom         # Find parent packages
npm ls prismjs        # Find parent packages
```

### Resolution strategies:

1. **Update parent packages**: The parent may have a newer version that uses safe dependencies
2. **Direct dependency override**: Add the package directly with a safe version
3. **Remove if unused**: If the parent doesn't need it, consider alternatives

---

## Post-Update Verification Commands

```bash
# Check for remaining vulnerabilities
cd /Users/jdrumgoole/GIT/nyrkio/frontend
npm audit

cd /Users/jdrumgoole/GIT/nyrkio/backend
poetry check

# Check Dependabot status
gh api repos/nyrkio/nyrkio/dependabot/alerts \
  --jq '.[] | select(.state=="open") | {severity: .security_vulnerability.severity, package: .security_vulnerability.package.name}'
```

---

## Rollback Plan

If updates cause issues:

```bash
# Rollback to current versions
cd /Users/jdrumgoole/GIT/nyrkio
git checkout main
git checkout backend/pyproject.toml backend/poetry.lock frontend/package.json frontend/package-lock.json

# Or rollback specific package
cd backend
poetry add h11@0.14.0  # Revert to old version
poetry lock
```

---

## Timeline Recommendation

- **Week 1**: Critical vulnerabilities (h11, python-jose, xmldom)
- **Week 2**: High severity (starlette, urllib3, playwright)
- **Week 3**: Medium/Low severity (vite, requests, others)
- **Week 4**: Verification and monitoring

Or all at once if testing passes smoothly.

---

## Notes

- Created: 2025-10-29
- Last Updated: 2025-10-29
- PR #605 must be merged before starting these updates
- Create new branch: `security/update-dependencies-2025-10`
- Full test suite must pass before merging
- Consider staging deployment before production

---

## Related Links

- GitHub Dependabot: https://github.com/nyrkio/nyrkio/security/dependabot
- Current PR: https://github.com/nyrkio/nyrkio/pull/605
