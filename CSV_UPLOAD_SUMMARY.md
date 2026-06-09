# CSV Data Upload Summary

## Files Successfully Prepared for Integration

I've set up a complete system to integrate your PLFS CSV files into the project's database system with filtering capabilities.

### CSV Files Detected

1. **chhv1.csv** - Household Survey Data
   - Size: 12.78 MB
   - Rows: ~101,957 households
   - Columns: 38 fields
   - Contains: Household demographics, expenditure, social groups, survey details

2. **cperv1.csv** - Person Survey Data
   - Size: 118.17 MB
   - Rows: ~415,549 persons
   - Columns: 140 fields
   - Contains: Individual demographics, employment, education, daily activities, earnings

## What Was Created

### Configuration Files
✓ **config/datasets/household_survey.yaml**
  - Complete schema with all 38 columns from chhv1.csv
  - Filterable fields: State, District, Sector, Quarter, Social_Group, Religion, etc.
  - Indexes for location, time period, and demographic queries

✓ **config/datasets/person_survey.yaml**
  - Schema for 140 columns from cperv1.csv
  - Filterable fields: Age, Sex, Education, Employment status, Industry, Occupation
  - Supports person-level employment and activity analysis

### Ingestion Scripts
✓ **ingest_csv_data.py** - Core ingestion engine
  - Batch processing (10,000 rows at a time) for large files
  - Automatic table creation from CSV structure
  - Progress tracking and error handling
  - Creates database indexes for fast queries

✓ **ingest_plfs_data.py** - Batch processor
  - Ingests both CSV files sequentially
  - Summary reporting for all datasets

✓ **ingest_csv.ps1** - PowerShell menu interface
  - User-friendly menu to select what to ingest
  - Automatic virtual environment activation
  - Progress display

### Testing & Documentation
✓ **test_csv_ingestion.py** - Verification tool
  - Validates CSV files are readable
  - Shows file statistics and sample data
  - Creates test samples for validation

✓ **CSV_INTEGRATION_GUIDE.md** - Complete documentation
  - Step-by-step instructions
  - Query examples
  - Troubleshooting guide
  - Data dictionary

## How to Use

### Quick Start - Run Ingestion

**Option 1: Interactive Menu**
```powershell
.\ingest_csv.ps1
```
This will show a menu where you can choose:
- Ingest household data only (faster, ~1 minute)
- Ingest person data only (~5-10 minutes)
- Ingest both datasets (~10-15 minutes)
- Just run verification test

**Option 2: Direct Commands**
```powershell
# Household survey only
python ingest_csv_data.py --csv chhv1.csv --config config/datasets/household_survey.yaml

# Person survey only
python ingest_csv_data.py --csv cperv1.csv --config config/datasets/person_survey.yaml

# Both datasets
python ingest_plfs_data.py
```

**Option 3: Test First**
```powershell
python test_csv_ingestion.py
```

### After Ingestion

Once ingested, the data will be available through your API:

**List all datasets:**
```
GET http://localhost:8080/api/datasets/
```

**Query household data:**
```
GET /api/query/household_survey?filters={"State_Ut_Code": 28, "Sector": 1}
```

**Query person data:**
```
GET /api/query/person_survey?filters={"Age": 25, "Sex": 1, "Sector": 2}
```

**Export filtered data:**
```
POST /api/export/household_survey
{
  "filters": {"Quarter": "Q3", "Social_Group": 1},
  "format": "csv"
}
```

## Key Features

### Household Survey (chhv1.csv)
- **Geographic Filtering**: State, District, NSS Region, Sector (Rural/Urban)
- **Temporal Filtering**: Quarter, Month, Survey Date
- **Demographic Filtering**: Household Size, Religion, Social Group
- **Economic Analysis**: Expenditure data, consumption patterns

### Person Survey (cperv1.csv)
- **Demographic Analysis**: Age, Sex, Marital Status, Education Level
- **Employment Data**: Current activity, Principal/Subsidiary status
- **Industry & Occupation**: NIC codes, NCO codes
- **Earnings**: Wages, salaried earnings, self-employed income
- **Daily Activities**: 7-day activity tracking with hours and wages

### Performance Optimizations
- Batch processing prevents memory issues
- Automatic indexing on frequently queried fields
- Efficient filtering on geographic and demographic dimensions
- Support for complex multi-field queries

## Data Structure

### Database Tables Created
```
household_survey
  - All 38 columns from chhv1.csv
  - Indexes on: State+District, Quarter+Month, Sector, Social_Group
  - ~102K rows

person_survey
  - All 140 columns from cperv1.csv
  - Indexes on: State+District, Sector, Age+Sex, Activity Status
  - ~415K rows
```

## Next Steps

1. **Run Ingestion**
   ```powershell
   .\ingest_csv.ps1
   ```

2. **Verify Data**
   - Check API: `GET /api/datasets/`
   - Test a query: `GET /api/query/household_survey?limit=10`

3. **Integrate with Frontend**
   - Add dataset selectors to UI
   - Create filter interfaces
   - Build visualizations

4. **Set Up Access Control**
   - Configure pricing tiers
   - Set authentication requirements
   - Define rate limits

## Filtering Examples

### Household Survey Queries

**Rural households in Karnataka (State code 29):**
```json
{"State_Ut_Code": 29, "Sector": 1}
```

**Q3 data for SC social group:**
```json
{"Quarter": "Q3", "Social_Group": 2}
```

**High expenditure households (>15000):**
```json
{"Monthly_Consumer_Expenditure": {"$gte": 15000}}
```

### Person Survey Queries

**Males aged 25-35 in urban areas:**
```json
{"Sex": 1, "Age": {"$gte": 25, "$lte": 35}, "Sector": 2}
```

**Employed persons in specific industry:**
```json
{"Principal_Status_Code": 31, "Principal_Industry_Code": 84119}
```

**Persons with higher education:**
```json
{"General_Education_Level": {"$gte": 8}}
```

## Technical Details

- **Processing**: Chunks of 10,000 rows
- **Memory efficient**: Streaming from CSV
- **Transaction safe**: Rollback on errors
- **Progress tracking**: Real-time feedback
- **Error handling**: Continues on non-critical errors

## File Locations

```
Project Root/
├── chhv1.csv                              # Household data
├── cperv1.csv                             # Person data
├── ingest_csv_data.py                     # Core ingestion
├── ingest_plfs_data.py                    # Batch processor
├── ingest_csv.ps1                         # PowerShell menu
├── test_csv_ingestion.py                  # Testing tool
├── CSV_INTEGRATION_GUIDE.md               # Full guide
└── config/datasets/
    ├── household_survey.yaml              # Household config
    └── person_survey.yaml                 # Person config
```

## Support

For detailed documentation, see [CSV_INTEGRATION_GUIDE.md](CSV_INTEGRATION_GUIDE.md)

---

**Ready to ingest?** Run: `.\ingest_csv.ps1`
