# MoSPI Data Portal Infrastructure (DPI)

## Overview
A scalable Data Portal Infrastructure built for the Ministry of Statistics and Programme Implementation (MoSPI) to enable efficient data access, querying, and management of statistical datasets.

## Features

### Core Requirements
- ✅ **Structured Database Ingestion**: Load datasets into relational databases with metadata preservation
- ✅ **Configurable Query Framework**: Schema and relationship definitions via configuration files
- ✅ **RESTful API Layer**: Comprehensive API for data access
- ✅ **Multi-dimensional Filtering**: Support for complex queries (state/gender/age/charts)
- ✅ **Access Control & Usage Metering**: Rate limiting, volume caps, and usage tracking
- ✅ **Micro-Payment Integration**: Simulate pricing model with test gateway
- ✅ **Developer Experience**: OpenAPI/Swagger documentation, Postman collections

### Bonus Features
- Reusable architecture for other government datasets
- Time-to-insight reduced
- Equitable access for citizens, researchers, and policymakers
- Scalable data access infrastructure

## Tech Stack

- **Backend**: Python 3.10+ with FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based auth with role-based access control
- **Documentation**: OpenAPI 3.0 (Swagger UI)
- **Data Processing**: Pandas for data ingestion
- **Caching**: Redis (optional)

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── dataset.py
│   │   └── user.py
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── dataset.py
│   │   └── user.py
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   ├── datasets.py
│   │   ├── query.py
│   │   └── auth.py
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── query_builder.py
│   │   ├── access_control.py
│   │   └── payment.py
│   └── middleware/                # Custom middleware
│       ├── __init__.py
│       └── rate_limiter.py
├── config/                        # Configuration files
│   ├── datasets/                  # Dataset metadata configs
│   │   └── sample_dataset.yaml
│   └── schema.yaml
├── data/                          # Sample data
│   └── sample_census_data.csv
├── tests/                         # Unit tests
│   └── __init__.py
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 13 or higher

### Setup

1. **Clone the repository**
```bash
cd "c:\Users\Dell\OneDrive\Desktop\Chandu\STATATHON\Statathon 2"
```

2. **Create virtual environment**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Initialize database**
```bash
python -m app.database
```

6. **Ingest sample data**
```bash
python -m app.services.ingestion --config config/datasets/sample_dataset.yaml
```

## Available Datasets

### PLFS Survey Data (Production Ready)

Two comprehensive datasets from the Periodic Labour Force Survey (PLFS) are available:

#### 1. Household Survey (chhv1.csv)
- **Size**: 13 MB | **Records**: ~102K households
- **Key Features**: Household demographics, expenditure patterns, social groups
- **Filters**: State, District, Sector (Rural/Urban), Quarter, Religion, Social Group
- **Use Cases**: Household economic analysis, expenditure studies, demographic research

#### 2. Person Survey (cperv1.csv)
- **Size**: 118 MB | **Records**: ~415K individuals  
- **Key Features**: Employment status, education, earnings, daily activities
- **Filters**: Age, Sex, Education Level, Employment Status, Industry, Occupation
- **Use Cases**: Labour force analysis, employment studies, skill assessment

### Quick Start - Ingest PLFS Data

```powershell
# Interactive menu
.\ingest_csv.ps1

# Or directly
python ingest_plfs_data.py
```

For detailed instructions, see [CSV_INTEGRATION_GUIDE.md](CSV_INTEGRATION_GUIDE.md)

## Usage

### Start the API server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Examples

#### 1. Query Data with Filters
```bash
GET /api/v1/query?dataset=census&state=Maharashtra&gender=female&age=15-29
```

#### 2. Get Dataset Metadata
```bash
GET /api/v1/datasets/{dataset_id}/metadata
```

#### 3. Usage Metering
```bash
GET /api/v1/users/me/usage
```

## Configuration

### Dataset Configuration (YAML)
```yaml
dataset:
  name: "Census Data 2021"
  table_name: "census_2021"
  schema:
    - name: "state"
      type: "string"
      filterable: true
    - name: "gender"
      type: "string"
      filterable: true
    - name: "age_group"
      type: "string"
      filterable: true
  relationships:
    - type: "one-to-many"
      foreign_key: "district_id"
```

## Access Control

### User Roles
- **Public**: Limited queries, rate-limited
- **Researcher**: Extended quota
- **Premium**: Unlimited access with micro-payments
- **Admin**: Full access to all datasets

### Rate Limiting
- Public: 100 requests/day
- Researcher: 1000 requests/day
- Premium: Pay-per-use model

## Development

### Run Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black app/

# Lint
flake8 app/
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Datasets
- `GET /api/v1/datasets` - List all datasets
- `GET /api/v1/datasets/{id}` - Get dataset details
- `POST /api/v1/datasets/ingest` - Ingest new dataset (Admin)

### Query
- `GET /api/v1/query` - Query data with filters
- `POST /api/v1/query/advanced` - Advanced query with aggregations

### Usage & Billing
- `GET /api/v1/users/me/usage` - Get current usage stats
- `POST /api/v1/payment/topup` - Add credits (micro-payment)

## Deployment

### Docker
```bash
docker build -t mospi-dpi .
docker run -p 8000:8000 mospi-dpi
```

### Production Considerations
- Use Gunicorn/Uvicorn workers
- Enable HTTPS with SSL certificates
- Setup PostgreSQL with proper indexing
- Implement Redis for caching
- Monitor with Prometheus/Grafana

## Contributing
Contributions are welcome! Please follow the standard Git workflow.

## License
MIT License

## Contact
For questions or support, please contact the development team.

---
**Built for Statathon 2 - Empowering data-driven governance**
