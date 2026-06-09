# Dataset Column Analysis & Filter Mapping

## Dataset Overview

### 1. Household Survey (PLFS) - ID: 4
**Table Name:** `household_survey`  
**Total Records:** 101,957  
**Level:** Household-level data

#### Key Columns:
- **State_Ut_Code** (INTEGER) - State/UT code (1-37)
- **District_Code** (INTEGER) - District code
- **Sector** (INTEGER) - 1=Rural, 2=Urban
- **Quarter** (TEXT) - Survey quarter (Q1, Q2, Q3, Q4)
- **Visit** (TEXT) - Visit number (V1, V2)
- **Household_Size** (INTEGER) - Number of household members
- **Household_Type** (INTEGER) - Type of household
- **Religion** (INTEGER) - Religion code
- **Social_Group** (INTEGER) - Social group code
- **Monthly_Consumer_Expenditure** (INTEGER) - Monthly consumption expenditure
- **Usual_Expenditure** (INTEGER) - Usual monthly expenditure
- **Annual_Clothing_Expenditure** (INTEGER)
- **Annual_Durables_Expenditure** (INTEGER)

#### Available Filters:
✅ State (via State_Ut_Code)  
✅ District (via District_Code)  
✅ Sector (Rural/Urban)  
❌ Gender - NOT AVAILABLE (household level)  
❌ Age - NOT AVAILABLE (household level)

---

### 2. Person Survey (PLFS) - ID: 5
**Table Name:** `person_survey`  
**Total Records:** 413,549  
**Level:** Individual person-level data

#### Key Columns:
- **State_UT_Code** (INTEGER) - State/UT code (1-37) [Note: Different casing from household]
- **District_Code** (INTEGER) - District code
- **Sector** (INTEGER) - 1=Rural, 2=Urban
- **Sex** (INTEGER) - 1=Male, 2=Female, 3=Transgender
- **Age** (INTEGER) - Age in years (0-112)
- **Marital_Status** (INTEGER) - Marital status code
- **General_Education_Level** (INTEGER) - Education level
- **Technical_Education_Level** (INTEGER)
- **Years_Formal_Education** (INTEGER)
- **Principal_Status_Code** (INTEGER) - Employment status
- **Principal_Industry_Code** (REAL) - Industry code
- **Principal_Occupation_Code** (REAL) - Occupation code
- **CWS_Status_Code** (INTEGER) - Current Weekly Status code
- **CWS_Earnings_Salaried** (INTEGER) - Weekly earnings for salaried
- **CWS_Earnings_SelfEmployed** (INTEGER) - Weekly earnings for self-employed

#### Available Filters:
✅ State (via State_UT_Code)  
✅ District (via District_Code)  
✅ Sector (Rural/Urban)  
✅ Gender (via Sex: 1=Male, 2=Female, 3=Transgender)  
✅ Age (0-112 years, supports ranges like 15-29)

---

## Filter Implementation

### API Query Parameters:
```
GET /api/v1/query?dataset={id}&state={STATE_NAME}&gender={GENDER}&age_group={AGE_RANGE}&year={SECTOR}&limit={LIMIT}
```

### Parameter Mapping:

| UI Filter | API Parameter | Person Survey Column | Household Survey Column | Values |
|-----------|---------------|---------------------|------------------------|--------|
| State | `state` | State_UT_Code | State_Ut_Code | State names (converted to codes 1-37) |
| District | `district` | District_Code | District_Code | District codes |
| Gender | `gender` | Sex | ❌ N/A | MALE/FEMALE/TRANSGENDER → 1/2/3 |
| Age Group | `age_group` | Age | ❌ N/A | "15-29" → {$gte: 15, $lte: 29} |
| Sector | `year` | Sector | Sector | 1=Rural, 2=Urban |
| Limit | `limit` | - | - | 1-10000 |

### State Code Mapping (1-37):
All 36 Indian states and UTs are mapped to codes 1-37:
- 1: Jammu and Kashmir
- 2: Himachal Pradesh
- 3: Punjab
- 4: Chandigarh
- 5: Uttarakhand
- 6: Haryana
- 7: Delhi
- 8: Rajasthan
- 9: Uttar Pradesh
- 10: Bihar
- 11: Sikkim
- 12: Arunachal Pradesh
- 13: Nagaland
- 14: Manipur
- 15: Mizoram
- 16: Tripura
- 17: Meghalaya
- 18: Assam
- 19: West Bengal
- 20: Jharkhand
- 21: Odisha
- 22: Chhattisgarh
- 23: Madhya Pradesh
- 24: Gujarat
- 25: Daman and Diu / DNH and DD
- 27: Maharashtra
- 28: Andhra Pradesh
- 29: Karnataka
- 30: Goa
- 31: Lakshadweep
- 32: Kerala
- 33: Tamil Nadu
- 34: Puducherry
- 35: Andaman and Nicobar Islands
- 36: Telangana
- 37: Ladakh

### Dashboard Behavior:
- **Household Survey selected:** Gender and Age filters are hidden
- **Person Survey selected:** All filters are visible
- Info message shows dataset type and available records

### Known Issues Fixed:
1. ✅ Column name case sensitivity (State_UT_Code vs State_Ut_Code)
2. ✅ Gender/Age filters now only apply to Person Survey
3. ✅ State code mapping completed for all 36 states/UTs
4. ✅ Sector filter added (Rural/Urban)

### State Distribution:
Household Survey has data for all 36 states ranging from 192 records (Lakshadweep) to 9,080 records (Uttar Pradesh).
