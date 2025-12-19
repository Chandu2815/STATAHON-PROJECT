# Landing Page Updated - PLFS Datasets Now Featured

## Changes Made to Frontend (app/api/frontend.py)

### 1. Updated Statistics Section
**Before:**
- 1,472 PLFS Records
- 695 District Codes
- 377 Survey Items
- 20+ API Endpoints

**After:**
- **517K+ Survey Records** (Total across all datasets)
- **102K Households** (CHHV1 dataset)
- **415K Individuals** (CPERV1 dataset)
- **25+ API Endpoints** (Updated count)

### 2. Enhanced Available Datasets Section
Added two new prominent dataset cards with gradient backgrounds:

#### 🏠 Household Survey (CHHV1) - Orange Gradient
- **~102,000 households** | 38 fields
- Demographics, expenditure, social groups, consumption patterns
- **Filters:** State, District, Sector, Quarter, Religion, Social Group
- Links to API documentation

#### 👥 Person Survey (CPERV1) - Blue Gradient
- **~415,000 individuals** | 140 fields
- Employment status, education, earnings, daily activities
- **Filters:** Age, Sex, Education, Employment Status, Industry, Occupation
- Links to API documentation

Kept existing datasets:
- District Codes (695 records)
- Item Codes (377 records)
- Data Layout (400 records)

### 3. Updated Example Queries Section
**Added real-world query examples:**

**Household Survey Query:**
```
GET /api/query/household_survey?filters={"State_Ut_Code": 28, "Sector": 1, "Social_Group": 2}
# Rural households from SC social group in Karnataka
```

**Person Survey Query:**
```
GET /api/query/person_survey?filters={"Age": {"$gte": 25, "$lte": 35}, "Sex": 1, "Sector": 2}
# Urban males aged 25-35
```

Shows support for:
- Complex filtering with operators ($gte, $lte, $in)
- Multi-field queries
- Demographic and geographic filters

## Visual Improvements

1. **Gradient Backgrounds:** New dataset cards use eye-catching gradients
   - Household: Warm orange gradient (#ffecd2 to #fcb69f)
   - Person: Cool blue gradient (#a1c4fd to #c2e9fb)

2. **Better Information Hierarchy:**
   - Record counts prominently displayed
   - Field counts shown
   - Key filter capabilities listed
   - Direct links to API docs

3. **Enhanced Statistics:**
   - Shows real data volumes
   - Highlights the scale of available data
   - Updated endpoint count

## Access the Updated Landing Page

**URL:** http://localhost:8080/

The landing page now prominently features:
- ✅ PLFS Household Survey dataset (CHHV1)
- ✅ PLFS Person Survey dataset (CPERV1)
- ✅ Real statistics (517K+ total records)
- ✅ Practical query examples
- ✅ Visual distinction with gradients
- ✅ Comprehensive filtering information

## What Users See Now

When users visit the homepage, they immediately see:
1. Updated statistics showing massive survey data (517K+ records)
2. Two prominently displayed PLFS datasets with detailed info
3. Clear filtering capabilities for each dataset
4. Real-world query examples they can try
5. Links to full API documentation

The landing page now effectively showcases the new PLFS datasets and makes it clear what data is available and how to query it!
