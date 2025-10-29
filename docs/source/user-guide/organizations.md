# Organizations

## Creating an Organization

1. Go to Settings → Organizations
2. Click "Create Organization"
3. Enter organization name
4. Add team members

## Organization Features

### Shared Test Results

All organization members can:
- View shared test results
- Submit results to organization tests
- Receive notifications

### Access Control

Organization admins can:
- Add/remove members
- Configure organization settings
- Manage billing

### GitHub Integration

Connect your GitHub organization:
1. Install Nyrkiö GitHub App
2. Grant organization access
3. Automatic member sync

## Organization Tests

Submit results to organization:

```bash
curl -X POST "https://api.nyrkio.com/api/v0/orgs/result/test-name" \
  -H "Authorization: Bearer TOKEN" \
  -d @results.json
```
