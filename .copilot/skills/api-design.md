# Skill: REST API Design
# Survey-AI Dataset Explorer System

## Scope
This skill applies to API endpoint design for all Survey-AI backends (Node.js and FastAPI).

## Core Concepts

### Response Format Standard
All API responses must follow this structure:

```json
{
  "success": boolean,
  "data": { /* payload */ },
  "meta": {
    "timestamp": "ISO-8601 string",
    "version": "API version",
    "requestId": "unique request ID",
    "duration": 123  // milliseconds (optional)
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "meta": {
    "timestamp": "ISO-8601 string",
    "statusCode": 400
  }
}
```

## API Endpoint Standards

### Authentication Endpoints

**POST /api/auth/register**
- Request: `{ email, password, name }`
- Response: `{ user: { id, email, name }, token }`
- Status: 201 Created
- Errors: 400 (invalid input), 409 (email exists)

```javascript
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "researcher"
    },
    "token": "jwt-token-here"
  },
  "meta": { "timestamp": "2026-03-28T10:30:00Z" }
}
```

**POST /api/auth/login**
- Request: `{ email, password }`
- Response: `{ user: { id, email, name }, token, expiresIn }`
- Status: 200 OK
- Errors: 401 (invalid credentials), 404 (user not found)

```javascript
{
  "success": true,
  "data": {
    "user": { "id": "uuid", "email": "user@example.com" },
    "token": "jwt-token",
    "expiresIn": 3600
  },
  "meta": { "timestamp": "2026-03-28T10:30:00Z" }
}
```

**POST /api/auth/logout**
- Request: `{ }` (with Authorization header)
- Response: `{ message: "Logged out successfully" }`
- Status: 200 OK

### Dataset Endpoints (FastAPI - Port 8001)

**GET /datasets/hierarchical**
- Purpose: Get all datasets organized by category
- Query Parameters: None
- Response: Hierarchical structure with categories
- Status: 200 OK

```json
{
  "success": true,
  "data": {
    "HCES": [
      {
        "id": "hces_household",
        "name": "hces_household",
        "label": "Household Consumption & Expenditure",
        "records": 261000,
        "columns": 45,
        "category": "HCES"
      }
    ],
    "PLFS": [
      {
        "id": "plfs_labour",
        "name": "plfs_labour",
        "label": "Periodic Labour Force Survey",
        "records": 150000,
        "columns": 32,
        "category": "PLFS"
      }
    ],
    "Survey": [],
    "Other": []
  },
  "meta": {
    "timestamp": "2026-03-28T10:30:00Z",
    "totalDatasets": 3
  }
}
```

**GET /datasets/{dataset_id}/metadata**
- Purpose: Get full metadata for a specific dataset
- Path Parameters: dataset_id (string)
- Response: Dataset metadata with column details
- Status: 200 OK
- Errors: 404 (dataset not found)

```json
{
  "success": true,
  "data": {
    "id": "hces_household",
    "name": "hces_household",
    "label": "Household Consumption & Expenditure",
    "category": "HCES",
    "records": 261000,
    "description": "Survey data for household consumption patterns",
    "columns": [
      {
        "name": "household_id",
        "type": "integer",
        "nullable": false,
        "description": "Unique household identifier"
      },
      {
        "name": "state",
        "type": "string",
        "nullable": false,
        "description": "State code"
      },
      {
        "name": "quantity",
        "type": "float",
        "nullable": true,
        "description": "Purchase quantity"
      }
    ],
    "indexedColumns": ["household_id", "state"],
    "lastUpdated": "2026-03-28T00:00:00Z"
  },
  "meta": { "timestamp": "2026-03-28T10:30:00Z" }
}
```

**GET /datasets/{dataset_id}/preview**
- Purpose: Get sample rows from dataset
- Path Parameters: dataset_id (string)
- Query Parameters: limit=10 (default), offset=0 (default)
- Response: Sample data rows
- Status: 200 OK

```json
{
  "success": true,
  "data": {
    "columns": ["household_id", "state", "quantity"],
    "rows": [
      [1, "Bihar", 45.5],
      [2, "Bihar", 32.3],
      [3, "Delhi", 78.9]
    ]
  },
  "meta": {
    "timestamp": "2026-03-28T10:30:00Z",
    "total": 261000,
    "limit": 10,
    "offset": 0
  }
}
```

**GET /datasets/search?query=**
- Purpose: Search datasets by name/description
- Query Parameters: query (string), category (optional)
- Response: Array of matching datasets
- Status: 200 OK

```json
{
  "success": true,
  "data": [
    {
      "id": "hces_household",
      "name": "hces_household",
      "label": "Household Consumption",
      "category": "HCES",
      "records": 261000
    }
  ],
  "meta": { "timestamp": "2026-03-28T10:30:00Z", "count": 1 }
}
```

### Analytics Endpoints

**GET /analytics/summary/{dataset_id}**
- Purpose: Get summary statistics for dataset
- Path Parameters: dataset_id (string)
- Response: Record count, completion %, active columns
- Status: 200 OK

```json
{
  "success": true,
  "data": {
    "totalRecords": 261000,
    "columnCount": 45,
    "activeColumns": 38,
    "dataCompletion": 94.5,
    "lastUpdated": "2026-03-28T00:00:00Z"
  },
  "meta": { "timestamp": "2026-03-28T10:30:00Z" }
}
```

**GET /analytics/distribution/{dataset_id}/{column}**
- Purpose: Get value distribution for a column
- Path Parameters: dataset_id, column (string)
- Query Parameters: limit=20 (top values)
- Response: Distribution data for charting
- Status: 200 OK

```json
{
  "success": true,
  "data": {
    "column": "state",
    "type": "categorical",
    "values": [
      { "label": "Bihar", "count": 45000, "percentage": 17.2 },
      { "label": "Delhi", "count": 38000, "percentage": 14.6 },
      { "label": "Maharashtra", "count": 32000, "percentage": 12.3 }
    ]
  },
  "meta": { "timestamp": "2026-03-28T10:30:00Z", "total": 261000 }
}
```

**POST /analytics/query**
- Purpose: Execute analytics query with filters
- Request Body:
  ```json
  {
    "dataset_id": "hces_household",
    "columns": ["state", "quantity"],
    "filters": {
      "state": "Bihar",
      "quantity_min": 10,
      "quantity_max": 100
    },
    "groupBy": "state",
    "aggregation": "count"
  }
  ```
- Response: Aggregated/filtered dataset results
- Status: 200 OK

```json
{
  "success": true,
  "data": {
    "query": { /* submitted query */ },
    "results": [
      { "state": "Bihar", "count": 5000, "avg_quantity": 45.3 },
      { "state": "Delhi", "count": 3500, "avg_quantity": 52.1 }
    ]
  },
  "meta": {
    "timestamp": "2026-03-28T10:30:00Z",
    "rowsReturned": 2,
    "executionTime": 145
  }
}
```

## HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET/POST/PATCH |
| 201 | Created | Successful resource creation |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request format/validation error |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (unique constraint) |
| 422 | Unprocessable Entity | Valid format but semantic error |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Service temporarily down |

## Error Code Reference

| Code | Status | Description |
|------|--------|-------------|
| VALIDATION_ERROR | 400 | Invalid request payload |
| UNAUTHORIZED | 401 | Missing or invalid token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| INVALID_EMAIL | 400 | Email format invalid |
| PASSWORD_TOO_SHORT | 400 | Password minimum length |
| EMAIL_EXISTS | 409 | Email already registered |
| DATASET_NOT_FOUND | 404 | Dataset doesn't exist |
| DATABASE_ERROR | 500 | Database operation failed |
| INTERNAL_ERROR | 500 | Unexpected server error |

## Request Validation Rules

### Email Validation
```javascript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
  throw new ValidationError('Invalid email format', 'INVALID_EMAIL');
}
```

### Password Validation
```javascript
if (password.length < 8) {
  throw new ValidationError('Password must be at least 8 characters', 'PASSWORD_TOO_SHORT');
}
```

### Input Sanitization
```javascript
// Trim whitespace
email = email.trim().toLowerCase();

// Remove dangerous characters (if needed)
// Limit string length
if (name.length > 100) {
  throw new ValidationError('Name too long', 'VALIDATION_ERROR');
}
```

## Response Optimization

### Pagination Pattern
```json
{
  "success": true,
  "data": [ /* items */ ],
  "meta": {
    "timestamp": "2026-03-28T10:30:00Z",
    "pagination": {
      "total": 10000,
      "limit": 100,
      "offset": 0,
      "page": 1,
      "pages": 100,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

### Field Selection Pattern
```
GET /datasets?fields=id,name,records
Result: Only includes specified fields
```

### Filtering Pattern
```
GET /datasets?category=HCES&records_min=100000
Result: Filtered by query parameters
```

## API Versioning

Future: Use `/api/v2/` prefix for breaking changes
Currently: `/api/v1/` or `/api/ai/`

## Documentation Standards

- Every endpoint must have OpenAPI/Swagger documentation
- Include request/response examples
- Document all query parameters
- Document all path parameters
- List all possible error responses
- Include rate limiting information

## Code Generation Checklist

- [ ] Use consistent response format
- [ ] Include status codes in comments
- [ ] Validate all input parameters
- [ ] Return appropriate error codes
- [ ] Include response metadata
- [ ] Document with examples
- [ ] Handle edge cases
- [ ] Implement pagination for lists
- [ ] Add rate limiting headers
- [ ] Test with various inputs

## When to Activate This Skill
- Designing new endpoints
- Updating API responses
- Troubleshooting API issues
- Creating API documentation
- Implementing error handling
- Optimizing response formats

## Related Skills
- backend-development (for Node.js endpoints)
- fastapi-development (for Python endpoints)
- database-optimization (for query optimization)
