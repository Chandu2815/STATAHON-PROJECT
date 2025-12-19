# PLFS CSV Data Integration - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CSV DATA FILES                          │
├─────────────────────────────────────────────────────────────────┤
│  chhv1.csv (13 MB)           cperv1.csv (118 MB)               │
│  • 101,957 households        • 415,549 persons                  │
│  • 38 columns                • 140 columns                      │
│  • Demographics              • Employment data                  │
│  • Expenditure data          • Education info                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  household_survey.yaml       person_survey.yaml                 │
│  • Schema definition         • Schema definition                │
│  • Filterable fields         • Filterable fields                │
│  • Indexes                   • Indexes                          │
│  • Access rules              • Access rules                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION ENGINE                            │
├─────────────────────────────────────────────────────────────────┤
│  ingest_csv_data.py                                             │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. Load Configuration                                     │ │
│  │ 2. Read CSV in Chunks (10,000 rows/batch)               │ │
│  │ 3. Create Database Table                                  │ │
│  │ 4. Insert Data (Transaction-safe)                        │ │
│  │ 5. Create Indexes                                         │ │
│  │ 6. Register Dataset                                       │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE (SQLite)                          │
├─────────────────────────────────────────────────────────────────┤
│  Tables:                                                        │
│  • household_survey (102K rows, 38 columns)                    │
│  • person_survey (415K rows, 140 columns)                      │
│  • datasets (metadata)                                          │
│                                                                  │
│  Indexes:                                                       │
│  • idx_location (State + District)                             │
│  • idx_time (Quarter + Month)                                  │
│  • idx_demographics (Age + Sex)                                │
│  • idx_sector (Rural/Urban)                                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Endpoints:                                             │
│  • GET /api/datasets/          → List all datasets             │
│  • GET /api/datasets/{id}      → Dataset info & schema         │
│  • GET /api/query/{table}      → Query with filters            │
│  • POST /api/export/{id}       → Export filtered data          │
│                                                                  │
│  Features:                                                      │
│  ✓ Multi-field filtering                                       │
│  ✓ Pagination                                                   │
│  ✓ Aggregations                                                 │
│  ✓ Access control                                               │
│  ✓ Rate limiting                                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT APPLICATIONS                        │
├─────────────────────────────────────────────────────────────────┤
│  • Web Dashboard                                                │
│  • Mobile Apps                                                  │
│  • Research Tools                                               │
│  • Data Analytics Platforms                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Ingestion Process

```
CSV File → Read Sample → Create Table Schema → Batch Processing
                                                     ↓
                                              ┌─────────────┐
                                              │ Chunk 1     │
                                              │ (10K rows)  │
                                              └─────────────┘
                                                     ↓
                                              ┌─────────────┐
                                              │ Chunk 2     │
                                              │ (10K rows)  │
                                              └─────────────┘
                                                     ↓
                                                   ...
                                                     ↓
                                              ┌─────────────┐
                                              │ Chunk N     │
                                              │ (remaining) │
                                              └─────────────┘
                                                     ↓
                                            Create Indexes
                                                     ↓
                                            Register Dataset
                                                     ↓
                                                 Complete!
```

### Query Process

```
API Request → Authentication → Rate Limit Check → Parse Filters
                                                        ↓
                                               Build SQL Query
                                                        ↓
                                            Apply Filters & Joins
                                                        ↓
                                                Execute Query
                                                        ↓
                                               Format Results
                                                        ↓
                                            Return JSON/CSV/Excel
```

## Key Components

### 1. Configuration Files
```yaml
config/datasets/
├── household_survey.yaml     # Household data config
└── person_survey.yaml        # Person data config
```

### 2. Ingestion Scripts
```
ingest_csv_data.py           # Core engine
ingest_plfs_data.py          # Batch processor
ingest_csv.ps1               # User interface
test_csv_ingestion.py        # Verification
```

### 3. API Endpoints
```
/api/datasets/               # Dataset management
/api/query/{table}           # Data querying
/api/export/{id}             # Data export
/api/users/                  # Access control
```

## Filtering Capabilities

### Household Survey Filters

```
Geographic:
├── State_Ut_Code (28 states/UTs)
├── District_Code
├── NSS_Region
└── Sector (Rural=1, Urban=2)

Temporal:
├── Quarter (Q1, Q2, Q3, Q4)
├── Month_of_Survey (1-12)
└── Survey_Date

Demographic:
├── Household_Size
├── Household_Type (1-4)
├── Religion (1-9)
└── Social_Group (ST=1, SC=2, OBC=3)

Economic:
├── Usual_Expenditure
├── Monthly_Consumer_Expenditure
├── Annual_Clothing_Expenditure
└── Annual_Durables_Expenditure
```

### Person Survey Filters

```
Demographics:
├── Age (0-100+)
├── Sex (Male=1, Female=2)
├── Marital_Status
└── Relationship_To_Head

Education:
├── General_Education_Level
├── Technical_Education_Level
└── Years_Formal_Education

Employment:
├── Principal_Status_Code
├── Subsidiary_Status_Code
├── CWS_Status_Code
├── Principal_Industry_Code
├── Principal_Occupation_Code
└── Employment_Type

Economic:
├── CWS_Earnings_Salaried
├── CWS_Earnings_SelfEmployed
└── Wage data (daily)
```

## Performance Metrics

### Ingestion Performance
- **Household Survey**: ~30-60 seconds
- **Person Survey**: ~5-10 minutes
- **Batch Size**: 10,000 rows
- **Memory Usage**: <500 MB (streaming)

### Query Performance
- **Simple Filter**: <100ms
- **Multiple Filters**: <500ms
- **Aggregations**: <2s
- **Export (1000 rows)**: <1s

## Security & Access

```
┌─────────────────────────────────────────┐
│         Access Control Layer            │
├─────────────────────────────────────────┤
│  JWT Authentication                     │
│  Role-Based Access (RBAC)               │
│  Rate Limiting                          │
│  Usage Metering                         │
│  API Key Management                     │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│           Pricing Tiers                 │
├─────────────────────────────────────────┤
│  Free:      100 queries/day             │
│  Basic:     1,000 queries/day           │
│  Premium:   Unlimited (pay-per-use)     │
└─────────────────────────────────────────┘
```

## Usage Examples

### Example 1: Rural Households in Karnataka
```bash
GET /api/query/household_survey?filters={
  "State_Ut_Code": 29,
  "Sector": 1
}
```

### Example 2: Employed Males (25-35) in Urban Areas
```bash
GET /api/query/person_survey?filters={
  "Sex": 1,
  "Age": {"$gte": 25, "$lte": 35},
  "Sector": 2,
  "Principal_Status_Code": 31
}
```

### Example 3: Export High-Expenditure Households
```bash
POST /api/export/household_survey
{
  "filters": {
    "Monthly_Consumer_Expenditure": {"$gte": 15000}
  },
  "format": "csv"
}
```

## Monitoring & Maintenance

### Health Checks
- Database connectivity
- API response times
- Disk space usage
- Query performance

### Logs
- Ingestion progress
- Query execution times
- Error tracking
- Access patterns

---

**For detailed implementation guide, see:** [CSV_INTEGRATION_GUIDE.md](CSV_INTEGRATION_GUIDE.md)
