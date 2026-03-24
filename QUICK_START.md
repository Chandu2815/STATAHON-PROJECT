# ⚡ QUICK START GUIDE - STATAHON PROJECT

## 🎯 ONE COMMAND TO START EVERYTHING

```bash
cd "/Users/arunsudhaveni/Desktop/STATAHON PROJECT"
./start.sh
```

OR if that doesn't work:

```bash
cd "/Users/arunsudhaveni/Desktop/STATAHON PROJECT"
python3.13 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

---

## ✨ THEN OPEN IN BROWSER - ALL THESE PAGES WORK!

| Click to Open | URL |
|---------------|-----|
| 🏠 **HOME PAGE** | http://127.0.0.1:8000/ |
| 📝 **REGISTER** | http://127.0.0.1:8000/register |
| 🔐 **LOGIN** | http://127.0.0.1:8000/login |
| 📊 **DASHBOARD** | http://127.0.0.1:8000/dashboard |
| 👨‍💼 **ADMIN PANEL** | http://127.0.0.1:8000/admin |
| 📚 **API DOCUMENTATION** | http://127.0.0.1:8000/docs |

---

## 📋 WHAT TO EXPECT

✅ Server starts on port 8000  
✅ All 5 frontend pages work  
✅ Admin dashboard with full features  
✅ User authentication (login/register)  
✅ API endpoints for data queries  
✅ Interactive API documentation  
✅ Beautiful UI with professional design  

---

## 🛑 STOP THE SERVER

Press: **CTRL + C** (in the terminal)

---

## 📊 AVAILABLE PAGES

### 1. **Landing Page** (`/`)
- Main entrance to the application
- Shows platform statistics
- Links to login/register

### 2. **Register** (`/register`)
- User registration form
- Create new account
- Email and password required

### 3. **Login** (`/login`)
- User login form
- Enter credentials
- Access your account

### 4. **Dashboard** (`/dashboard`)
- User data dashboard
- View your data
- Run queries
- Export results

### 5. **Admin Panel** (`/admin`)
- Administrative controls
- User management
- System settings
- Analytics and reports

---

## 🔌 API ENDPOINTS (for programmers)

**Base URL:** `http://127.0.0.1:8000/api/v1`

```bash
# Register
POST /auth/register

# Login
POST /auth/login

# Get Datasets
GET /datasets/

# Query Data
GET /query?state=Maharashtra&limit=10

# Logout
POST /auth/logout
```

---

## ✅ COMPLETE!

**Everything is ready to run!**

Just execute: `./start.sh` or `python3.13 -m uvicorn main:app --host 127.0.0.1 --port 8000`

Then open your browser to any of the pages listed above.

---

**Version:** 1.0.0 - Complete STATAHON Application  
**Date:** 24 March 2026  
**Status:** ✅ READY TO USE
