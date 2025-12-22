# PLFS CSV Data Integration Guide

This guide explains how to integrate the PLFS (Periodic Labour Force Survey) CSV files into the dataset system.

## Overview

Two large CSV files have been prepared for integration:
- **chhv1.csv** (13.4 MB) - Household Survey Data
- **cperv1.csv** (123.9 MB) - Person Survey Data

## Files Created

### Configuration Files
- `config/datasets/household_survey.yaml` - Configuration for chhv1.csv
- `config/datasets/person_survey.yaml` - Configuration for cperv1.csv

### Ingestion Scripts
- `ingest_csv_data.py` - Core CSV ingestion engine with batch processing
- `ingest_plfs_data.py` - Batch script to ingest both CSV files
- `test_csv_ingestion.py` - Verification and testing script

## Quick Start

### 1. Verify CSV Files
```powershell
python test_csv_ingestion.py
```
This will:
- Check if CSV files exist
- Display file sizes and column information
- Show sample data from each file
- Create a small test sample

### 2. Ingest Single Dataset
```powershell
# Household Survey (smaller, faster)
python ingest_csv_data.py --csv chhv1.csv --config config/datasets/household_survey.yaml

# Person Survey (larger, takes more time)
python ingest_csv_data.py --csv cperv1.csv --config config/datasets/person_survey.yaml
```

### 3. Ingest Both Datasets
```powershell
python ingest_plfs_data.py
```
This will process both CSV files sequentially.

## What Happens During Ingestion

1. **Configuration Loading** - Reads YAML config with schema definitions
2. **Table Creation** - Creates database table based on CSV structure
3. **Dataset Registration** - Registers dataset in the `datasets` table
4. **Batch Processing** - Ingests data in chunks of 10,000 rows
5. **Index Creation** - Creates indexes for better query performance

## Expected Results

### Household Survey (chhv1.csv)
- **Rows**: ~101,959
- **Columns**: 38
- **Key fields**: Panel, State, District, Sector, Household demographics, Expenditure data
- **Table name**: `household_survey`

### Person Survey (cperv1.csv)
- **Rows**: To be determined (file is 123MB)
- **Columns**: To be auto-detected
- **Key fields**: Person demographics, Employment status, Education, Occupation
- **Table name**: `person_survey`

## Querying the Data

Once ingested, you can query through the API:

### Example Queries

```bash
# Get household data for a specific state
GET /api/query/household_survey?filters={"State_Ut_Code": 28}

# Get person data by sector (Rural/Urban)
GET /api/query/person_survey?filters={"Sector": 1}

# Complex query with multiple filters
GET /api/query/household_survey?filters={"Quarter": "Q3", "Sector": 2, "Social_Group": 1}
```

### Available Filters (Household Survey)

- **Geographic**: State_Ut_Code, District_Code, NSS_Region, Sector
- **Temporal**: Quarter, Month_of_Survey, Survey_Date
- **Demographics**: Household_Size, Religion, Social_Group, Household_Type
- **Economic**: Usual_Expenditure, Monthly_Consumer_Expenditure

### Available Filters (Person Survey)

- **Geographic**: State_Ut_Code, District_Code, Sector
- **Demographics**: Age, Sex, Marital_Status, Person_Serial_No
- **Employment**: Current_Activity_Status, Usual_Principal_Activity, Employment_Type
- **Education**: General_Education

## Database Tables

After ingestion, the following tables will be created:

```sql
-- Household Survey
household_survey
  - All 38 columns from chhv1.csv
  - id (auto-increment primary key)
  - created_at, updated_at (timestamps)

-- Person Survey
person_survey
  - All columns from cperv1.csv (auto-detected)
  - id (auto-increment primary key)
  - created_at, updated_at (timestamps)
```

## Performance Notes

- **Chunk Size**: 10,000 rows per batch (configurable)
- **Memory**: Processes data in chunks to handle large files
- **Indexes**: Creates indexes on frequently queried columns
- **Time Estimates**:
  - chhv1.csv (13MB): ~30-60 seconds
  - cperv1.csv (123MB): ~5-10 minutes

## Troubleshooting

### File Not Found
Ensure CSV files are in the project root directory:
```powershell
Get-ChildItem *.csv
```

### Memory Issues
If you encounter memory issues with cperv1.csv, adjust chunk size in `ingest_csv_data.py`:
```python
self.chunk_size = 5000  # Reduce from 10000
```

### Database Locked
If SQLite database is locked:
```powershell
# Stop the server
# Wait a few seconds
# Try ingestion again
```

### Missing Dependencies
Install required packages:
```powershell
pip install pandas pyyaml sqlalchemy openpyxl
```

## Integration with API

The ingested datasets are automatically available through:

1. **Dataset List API**: `/api/datasets/` - Shows all available datasets
2. **Dataset Info API**: `/api/datasets/{dataset_id}` - Get schema and metadata
3. **Query API**: `/api/query/{table_name}` - Query with filters
4. **Export API**: `/api/export/{dataset_id}` - Export filtered results

## Data Dictionary

### Household Survey Fields

- **Panel**: Survey panel identifier (e.g., P4)
- **Sector**: 1=Rural, 2=Urban
- **State_Ut_Code**: State/UT code as per NSS classification
- **District_Code**: District code
- **Household_Size**: Number of household members
- **Household_Type**: 1=Self-employed, 2=Regular wage, 3=Casual labour, 4=Others
- **Religion**: 1=Hinduism, 2=Islam, 3=Christianity, 4=Sikhism, etc.
- **Social_Group**: 1=ST, 2=SC, 3=OBC, 9=Others
- **Monthly_Consumer_Expenditure**: Monthly per capita consumer expenditure

### Person Survey Fields

Person-level employment and demographic data (schema auto-detected during ingestion).

## Next Steps

After successful ingestion:

1. Verify data through API: `GET /api/datasets/`
2. Test queries with filters
3. Check data quality and completeness
4. Create visualizations or reports
5. Set up access controls and pricing tiers

## Support

For issues or questions:
- Check logs during ingestion for detailed error messages
- Verify CSV file integrity
- Ensure database is not locked by other processes
- Check disk space (needs ~2-3x CSV file size for processing)
