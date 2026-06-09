# Survey AI Filter System - Quick Reference Card

## 🚀 Quick Start

### Start Backend
```bash
cd /Users/arunsudhaveni/STATAHON\ PROJECT
python -m uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd /Users/arunsudhaveni/STATAHON\ PROJECT/survey-ai-app/frontend
npm run dev  # http://localhost:5173
```

---

## 📍 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai/datasets/hierarchical` | GET | List all datasets |
| `/api/ai/columns/{dataset}` | GET | Get columns |
| `/api/ai/distinct/{dataset}/{col}` | GET | Get distinct values |
| `/api/ai/data` | POST | Query with filters |
| `/api/ai/statistics/{dataset}` | GET | Get stats |
| `/api/ai/reference/states` | GET | Get states |
| `/api/ai/reference/districts` | GET | Get districts |

---

## 🔌 Example API Calls

### Get All Datasets
```bash
curl http://localhost:8000/api/ai/datasets/hierarchical
```

### Get Columns
```bash
curl http://localhost:8000/api/ai/columns/household_survey
```

### Get Distinct Districts (All)
```bash
curl http://localhost:8000/api/ai/distinct/household_survey/district_code
```

### Get Districts for State 28
```bash
curl "http://localhost:8000/api/ai/distinct/household_survey/district_code?filters=%7B%22state_code%22:28%7D"
```

### Query Data
```bash
curl -X POST http://localhost:8000/api/ai/data \
  -H "Content-Type: application/json" \
  -d '{
    "table": "household_survey",
    "columns": ["state_code", "district_code"],
    "filters": {"state_code": 28},
    "limit": 100
  }'
```

---

## 🐛 Debugging

### Check Logs
- **Backend**: Terminal where you ran uvicorn
- **Frontend**: Browser console (F12)

### Common Issues

| Issue | Solution |
|-------|----------|
| "No filters available" | Select at least 1 column |
| Dropdown won't populate | Check backend logs |
| "Network error" | Make sure backend is running |
| No data returned | Try broader filters |

---

## 📊 Filter Hierarchy

```
State Code (Primary)
    ↓
District Code (Depends on State)
    ↓
Sector / Tehsil / Block (Depend on State + District)
    ↓
Village / Other (Depend on above)
```

---

## ✅ Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:5173
- [ ] Datasets load in dropdown
- [ ] Columns appear after dataset select
- [ ] Filter dropdowns populate with values
- [ ] Selecting state updates district list
- [ ] Selecting values allows data query
- [ ] Data displays in table
- [ ] Pagination works
- [ ] "Clear Filters" button works

---

## 📁 Key Files

| File | Purpose | Modified |
|------|---------|----------|
| `app/api/ai.py` | Filter API | ✅ NEW |
| `app/main.py` | Router registration | ✅ |
| `FiltersPanel.jsx` | Filter UI | ✅ |
| `SurveyAI.jsx` | Main page | ✅ |

---

## 🔍 Console Logs

Watch for these logs in browser console:

```
[Survey AI] Fetching hierarchical datasets...
[Survey AI] Successfully loaded datasets: 3
[API] GET /api/ai/columns/household_survey
[Filter] state_code: 37 options loaded
[Survey AI] Fetching data with payload: {...}
```

---

## 💾 Database Setup

For best performance, add indexes:

```sql
CREATE INDEX idx_household_state ON household_survey(state_code);
CREATE INDEX idx_household_district ON household_survey(state_code, district_code);
```

---

## 🎯 Typical Workflow

1. **Select Dataset** → Choose "household_survey"
2. **Select Columns** → Check "state_code", "district_code"
3. **Select Filter** → state_code = 28
4. **Observe Update** → district_code shows only AP districts
5. **Select Filter** → district_code = 5
6. **Query Data** → Click "Saturate & Pulse System"
7. **View Results** → See filtered data in table

---

## 🚨 Error Messages

| Message | Meaning | Fix |
|---------|---------|-----|
| "Please select a dataset" | No dataset chosen | Click dataset dropdown |
| "Please select at least one column" | No columns selected | Check column checkboxes |
| "Please select at least one filter" | No filter values selected | Choose filter values |
| "Network error" | API unreachable | Start backend |
| "Table not found" | Invalid dataset | Check database |

---

## 💡 Tips

- **Cascade works top-down**: Always select state before district
- **Fewer filters = faster**: Use specific combinations
- **Check console**: All debug info in browser console
- **Pagination**: Large result sets auto-paginate
- **Types matter**: Backend auto-converts types

---

## 🔧 Configuration

**Backend**: Port 8000 (configurable in startup command)
**Frontend**: Port 5173 (Vite default)
**Database**: PostgreSQL (configured in .env)
**Max Results**: 10,000 per query

---

## 📚 Documentation Files

1. **FILTER_SYSTEM_FIX.md** - Complete guide (300+ lines)
2. **FILTER_SYSTEM_QUICKSTART.md** - Testing guide (150+ lines)
3. **FILTER_SYSTEM_ARCHITECTURE.md** - Architecture (200+ lines)
4. **FILTER_SYSTEM_IMPLEMENTATION_COMPLETE.md** - Summary (180+ lines)

---

## 🌐 Production Deployment

**VPS Address**: 187.127.138.4
**SSH User**: root
**Password**: Statathon@2026

**Deployment Steps**:
1. SSH to VPS
2. Clone repository
3. Install dependencies
4. Start backend
5. Start frontend
6. Configure domain
7. Set up SSL

---

## 📞 Support

- Check documentation above
- Review console logs
- Inspect network calls (DevTools → Network tab)
- Check database connectivity
- Verify credentials and permissions

---

## ✨ Features

✅ Cascading filters
✅ Dynamic value loading
✅ Error handling
✅ Type conversion
✅ Logging
✅ Pagination
✅ Performance optimized
✅ SQL injection prevention

---

## 🎓 Learning Path

1. Read FILTER_SYSTEM_FIX.md (architecture)
2. Read FILTER_SYSTEM_QUICKSTART.md (testing)
3. Review app/api/ai.py (backend code)
4. Review FiltersPanel.jsx (frontend code)
5. Test all scenarios
6. Deploy to production

---

**Status**: ✅ Production Ready

**Last Updated**: June 9, 2026
