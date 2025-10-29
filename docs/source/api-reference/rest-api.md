# REST API

Base URL: `https://api.nyrkio.com/api/v0`

## Endpoints

### Test Results

#### Submit Results
```
POST /result/{test_name}
```

#### Get Results
```
GET /result/{test_name}
```

#### Delete Results
```
DELETE /result/{test_name}
```

### Change Detection

#### Get Change Points
```
GET /result/{test_name}/changes
```

#### Enable Detection
```
POST /result/{test_name}/changes/enable
```

#### Disable Detection
```
POST /result/{test_name}/changes/disable
```

### Organizations

#### Organization Results
```
POST /orgs/result/{test_name}
GET /orgs/result/{test_name}/changes
```

### Pull Requests

#### Submit PR Results
```
POST /pulls/{owner}/{repo}/{pr_number}/result/{test_name}
```

#### Get PR Changes
```
GET /pulls/{owner}/{repo}/{pr_number}/changes/{commit}
```

See [OpenAPI Documentation](https://api.nyrkio.com/docs) for complete details.
