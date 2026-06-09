# Survey AI Filter System - Quick Start Guide

## Running the Application

### Backend

```bash
# From /Users/arunsudhaveni/STATAHON PROJECT/
cd app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend

```bash
# From /Users/arunsudhaveni/STATAHON PROJECT/survey-ai-app/frontend/
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`

---

## Testing the Filters

### 1. Open Browser DevTools

Press `F12` to open the browser console. This will show all debug logs.

### 2. Navigate to Survey AI

Go to `http://localhost:5173` and click "Survey AI" or go directly to the Survey AI page.

### 3. Watch the Console

You'll see logs like:

```
[Survey AI] Fetching hierarchical datasets...
[Survey AI] Successfully loaded datasets: Household Surveys, Person Surveys, Enterprise Surveys
[Survey AI] Selected dataset: household_survey
[Survey AI] Fetching columns for household_survey...
[Survey AI] Loaded 45 columns: state_code, district_code, sector, ...
```

### 4. Test Filter Dropdowns

Once columns are loaded:

1. Click on "Step 2: Vector Mapping & Selection"
2. Select a few columns (at least 3) including `state_code` and `district_code`
3. You should see the filter dropdowns appear in "Step 3: Conditional Logic Engine"
4. Observe the console logs showing which filters are loading

### 5. Select a State

In the state_code filter:
1. Click on the dropdown
2. Select a state (e.g., "28 - Andhra Pradesh")
3. Watch the console for a log showing which districts are loaded

### 6. Select a District

Now the district_code filter should only show districts from that state:
1. Click on the district_code dropdown
2. You should see a filtered list

### 7. Query Data

Once you have at least 2 filters selected (e.g., state=28, district=5):
1. Click "Saturate & Pulse System" button
2. The button should become enabled (not grayed out)
3. Data will load below

---

## API Testing with cURL

### Get Datasets

```bash
curl -X GET http://localhost:8000/api/ai/datasets/hierarchical
```

### Get Columns

```bash
curl -X GET http://localhost:8000/api/ai/columns/household_survey
```

### Get Distinct States

```bash
curl -X GET http://localhost:8000/api/ai/distinct/household_survey/state_code?limit=100
```

### Get Districts for a State

```bash
curl -X GET "http://localhost:8000/api/ai/distinct/household_survey/district_code?filters=%7B%22state_code%22%3A28%7D"
```

Note: `%7B%22state_code%22%3A28%7D` is URL-encoded `{"state_code":28}`

### Query Data

```bash
curl -X POST http://localhost:8000/api/ai/data \
  -H "Content-Type: application/json" \
  -d '{
    "table": "household_survey",
    "columns": ["state_code", "district_code", "sector"],
    "filters": {"state_code": 28},
    "limit": 100
  }'
```

---

## Troubleshooting

### Issue: "No filters available"

**Solution**:
1. Make sure you selected at least 1 column
2. Check browser console for errors
3. Make sure the dataset has data

---

### Issue: Dropdowns show "-- Loading..." but never finish

**Solution**:
1. Check browser console for network errors
2. Check backend logs for database errors
3. Try refreshing the page
4. Make sure the table exists in the database

---

### Issue: "Please select at least one filter" message

**Solution**:
This is normal! You need to select at least one filter value before querying data. This prevents accidental full scans.

---

### Issue: "Column 'X' not found in table"

**Solution**:
The column name you selected doesn't exist in the table. This might mean:
1. The database doesn't have this column
2. The column was misspelled
3. The table structure changed

---

### Issue: No data returned

**Solution**:
1. The filters you selected might have no matching records
2. Try different filter values
3. Try removing some filters to get a broader result set

---

## Console Logs Explained

### [Filter] Logs

```
[Filter] sector: 5 options
```
This means the sector filter loaded 5 different values.

---

### [Survey AI] Logs

```
[Survey AI] Fetching data with payload: {...}
[Survey AI] Successfully fetched 85 records (total: 12500)
```
This shows data was successfully retrieved.

---

### [API] Logs

```
[API] GET /api/ai/distinct/household_survey/state_code
[API] Response: {success: true, data: [...]}
```
This shows what API calls are being made and their responses.

---

## Performance Tips

1. **Use Specific Filters**: Broader filters (fewer conditions) take longer
2. **Select Fewer Columns**: Fewer columns = faster queries
3. **Start with State**: Always filter by state first for cascading benefits
4. **Pagination**: Data loads in pages, so large result sets are manageable

---

## Database Indexes for Performance

To improve query performance, add these indexes to your database:

```sql
-- For household_survey table
CREATE INDEX idx_household_state ON household_survey(state_code);
CREATE INDEX idx_household_state_district ON household_survey(state_code, district_code);
CREATE INDEX idx_household_sector ON household_survey(sector);

-- For person_survey table
CREATE INDEX idx_person_state ON person_survey(state_code);
CREATE INDEX idx_person_district ON person_survey(state_code, district_code);

-- For enterprise_survey table
CREATE INDEX idx_enterprise_state ON enterprise_survey(state_code);
CREATE INDEX idx_enterprise_district ON enterprise_survey(state_code, district_code);
```

---

## Keyboard Shortcuts

- **Ctrl/Cmd + K**: Clear all filters

---

## Features Implemented

✅ **Cascading Filters**: Select one filter, others update automatically
✅ **Loading States**: Shows "Loading..." while fetching
✅ **Error Messages**: Clear messages when things go wrong
✅ **Pagination**: Results show 12 per page, navigable
✅ **Type Conversion**: Automatic int/float/string conversion
✅ **Logging**: Complete audit trail in console
✅ **Filter Requirements**: Requires at least 1 filter before query
✅ **Filter Summary**: Shows which filters are active

---

## Next Steps

1. Test all filter combinations
2. Add database indexes for performance
3. Configure your database connection
4. Load your survey data into the database
5. Verify all filters work with your data
6. Go live!

---

## Support

If you encounter issues:

1. Check the browser console (F12)
2. Check the backend logs (terminal where you ran `uvicorn`)
3. Review the `FILTER_SYSTEM_FIX.md` documentation
4. Check database connectivity

---

Happy filtering! 🚀
