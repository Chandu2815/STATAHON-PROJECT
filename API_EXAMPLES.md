# MoSPI Data Portal Infrastructure - API Examples

## Authentication

### Register a New User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "researcher@university.edu",
  "username": "researcher01",
  "password": "securePassword123!",
  "full_name": "Dr. Research Scholar",
  "role": "researcher"
}
```

### Login
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=researcher01&password=securePassword123!
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Query Examples

### 1. Simple Filter - Female population in Maharashtra, age 15-29
```bash
GET /api/v1/query?dataset=census&state=Maharashtra&gender=Female&age_group=15-29
Authorization: Bearer YOUR_TOKEN
```

### 2. Multiple Filters with Pagination
```bash
GET /api/v1/query?dataset=census&state=Karnataka&gender=Male&year=2021&limit=10&offset=0
Authorization: Bearer YOUR_TOKEN
```

### 3. Ordered Results
```bash
GET /api/v1/query?dataset=census&state=Delhi&order_by=population&order_direction=desc
Authorization: Bearer YOUR_TOKEN
```

### 4. Advanced Query with POST
```bash
POST /api/v1/query
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "dataset": "census",
  "filters": {
    "state": "Maharashtra",
    "gender": "Female",
    "age_group": "15-29"
  },
  "fields": ["state", "district", "population", "literacy_rate"],
  "limit": 50,
  "offset": 0,
  "order_by": "literacy_rate",
  "order_direction": "desc"
}
```

Response:
```json
{
  "dataset": "census",
  "total_records": 2,
  "returned_records": 2,
  "data": [
    {
      "state": "Maharashtra",
      "district": "Mumbai",
      "population": 1180000,
      "literacy_rate": 89.7
    },
    {
      "state": "Maharashtra",
      "district": "Pune",
      "population": 850000,
      "literacy_rate": 88.9
    }
  ],
  "query_time_ms": 12.45
}
```

## Dataset Management

### List All Datasets
```bash
GET /api/v1/datasets
Authorization: Bearer YOUR_TOKEN
```

### Get Dataset Details
```bash
GET /api/v1/datasets/1
Authorization: Bearer YOUR_TOKEN
```

### Create New Dataset (Admin Only)
```bash
POST /api/v1/datasets
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "name": "Economic Survey 2023",
  "description": "Annual economic data",
  "table_name": "economic_survey_2023",
  "config": {
    "schema": [
      {"name": "state", "type": "string"},
      {"name": "gdp", "type": "float"}
    ]
  }
}
```

## User & Billing

### Get My Usage Statistics
```bash
GET /api/v1/users/me/usage
Authorization: Bearer YOUR_TOKEN
```

Response:
```json
{
  "user_id": 1,
  "total_requests": 150,
  "requests_today": 25,
  "total_data_transferred_mb": 45.67,
  "credits_remaining": 8.45,
  "last_request": "2025-12-11T10:30:00Z",
  "rate_limit": 1000,
  "volume_limit_mb": 100
}
```

### Top Up Credits
```bash
POST /api/v1/users/me/topup?amount=100
Authorization: Bearer YOUR_TOKEN
```

Response:
```json
{
  "id": 123,
  "user_id": 1,
  "amount": 100.0,
  "transaction_type": "topup",
  "description": "Credit topup of 100.0 credits",
  "status": "completed",
  "payment_gateway_ref": "PAY-A1B2C3D4E5F6",
  "created_at": "2025-12-11T10:35:00Z"
}
```

### Upgrade to Premium
```bash
POST /api/v1/users/me/upgrade-premium
Authorization: Bearer YOUR_TOKEN
```

### Get Transaction History
```bash
GET /api/v1/users/me/transactions?limit=20
Authorization: Bearer YOUR_TOKEN
```

### Get Pricing Information
```bash
GET /api/v1/users/pricing
```

Response:
```json
{
  "pricing": {
    "query": 0.01,
    "data_mb": 0.1,
    "premium_subscription": 100.0
  },
  "currency": "credits",
  "description": "Pay-per-use pricing model for data access"
}
```

## Real-World Use Cases

### Use Case 1: Gender-wise Literacy Analysis
```bash
GET /api/v1/query?dataset=census&gender=Female&order_by=literacy_rate&order_direction=desc&limit=10
```

### Use Case 2: State-wise Population Comparison
```bash
POST /api/v1/query
{
  "dataset": "census",
  "filters": {
    "age_group": "15-29"
  },
  "fields": ["state", "gender", "population"],
  "order_by": "population",
  "order_direction": "desc"
}
```

### Use Case 3: District-level Employment Data
```bash
GET /api/v1/query?dataset=census&state=Karnataka&order_by=employment_rate&order_direction=desc
```

## Error Responses

### Rate Limit Exceeded
```json
{
  "detail": "Rate limit exceeded. Your limit is 100 requests per day."
}
```

### Insufficient Credits
```json
{
  "detail": "Insufficient credits. Required: 0.15, Available: 0.05"
}
```

### Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### Not Found
```json
{
  "detail": "Dataset 'invalid_dataset' not found"
}
```
