# 🚀 STATAHON PROJECT - HOW TO RUN

## Quick Start (Easiest Way)

### Option 1: Use the Start Script
```bash
cd "/Users/arunsudhaveni/Desktop/STATAHON PROJECT"
./start.sh
```

### Option 2: Run with Python Directly
```bash
cd "/Users/arunsudhaveni/Desktop/STATAHON PROJECT"
python3.13 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Option 3: Run with Python Script
```bash
cd "/Users/arunsudhaveni/Desktop/STATAHON PROJECT"
python3.13 main.py
```

---

## ✅ Once Running - Access These Pages

### **Frontend Pages (User Interfaces)**

| Page | URL | Description |
|------|-----|-------------|
| 🏠 **Landing Page** | http://127.0.0.1:8000/ | Main home page |
| 📝 **Register** | http://127.0.0.1:8000/register | User registration |
| 🔐 **Login** | http://127.0.0.1:8000/login | User login |
| 📊 **Dashboard** | http://127.0.0.1:8000/dashboard | User dashboard |
| 👨‍💼 **Admin Panel** | http://127.0.0.1:8000/admin | Admin dashboard |

### **API & Documentation**

| Resource | URL | Description |
|----------|-----|-------------|
| 📚 **Swagger Docs** | http://127.0.0.1:8000/docs | Interactive API documentation |
| 📖 **ReDoc** | http://127.0.0.1:8000/redoc | Alternative API documentation |
| 🏥 **Health Check** | http://127.0.0.1:8000/api/v1/auth/health | API health status |

### **API Endpoints Examples**

```bash
# Register a user
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get datasets
curl http://127.0.0.1:8000/api/v1/datasets/

# Query data
curl "http://127.0.0.1:8000/api/v1/query?state=Maharashtra&limit=10"
```

---

## 🛠️ Prerequisites

Make sure you have:
- ✅ Python 3.13 installed
- ✅ PostgreSQL running (if using SQL database)
- ✅ Virtual environment activated (`.venv`)
- ✅ All dependencies installed (`pip install -r requirements.txt`)

---

## 📋 Services Expected to Run

When the application starts, these services should be active:

✅ **FastAPI Server** - Running on port 8000
✅ **PostgreSQL Database** - Connected and ready
✅ **Static Files** - Served from `/static`
✅ **Frontend Templates** - Served from `/app/templates`

---

## 🔍 Verify Everything is Working

```bash
# Check if server is running
lsof -i :8000

# Test the landing page
curl http://127.0.0.1:8000/

# Check API health
curl http://127.0.0.1:8000/api/v1/auth/health

# View recent logs
tail -f /tmp/statahon.log  # If logging is configured
```

---

## ⚙️ Project Structure

```
STATAHON PROJECT/
├── main.py                 # Entry point (imports app/main.py)
├── app/
│   ├── main.py            # FastAPI app with all routes
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database setup
│   ├── auth.py            # Authentication module
│   ├── api/               # API endpoints folder
│   │   ├── auth.py        # Auth routes
│   │   ├── datasets.py    # Dataset routes
│   │   ├── query.py       # Query routes
│   │   ├── users.py       # User management
│   │   ├── frontend.py    # Frontend pages (pages are here!)
│   │   └── ...
│   ├── templates/         # HTML Pages
│   │   ├── index.html     # Landing page
│   │   ├── login.html     # Login page
│   │   ├── register.html  # Registration page
│   │   ├── dashboard.html # User dashboard
│   │   ├── admin_dashboard.html  # Admin panel
│   │   └── ...
│   └── static/            # CSS, JS, Images
├── db.py                  # Database connection (legacy)
├── requirements.txt       # Python dependencies
└── .env                   # Configuration file

```

---

## 🎯 What Happens When You Run It?

1. ✅ FastAPI server starts on `http://127.0.0.1:8000`
2. ✅ Database connects successfully
3. ✅ All frontend routes become available:
   - Landing page → `/`
   - Login page → `/login`
   - Register page → `/register`
   - Dashboard → `/dashboard`
   - Admin panel → `/admin`
4. ✅ API endpoints become available at `/api/v1/*`
5. ✅ Static files served from `/static/*`
6. ✅ Interactive docs at `/docs`

---

## 📱 Browser Access

Open your web browser and visit:
- **Home**: http://127.0.0.1:8000/
- **Register**: http://127.0.0.1:8000/register
- **Login**: http://127.0.0.1:8000/login
- **Dashboard**: http://127.0.0.1:8000/dashboard
- **Admin**: http://127.0.0.1:8000/admin

---

## 🛑 Stop the Server

Press `CTRL+C` in the terminal where the server is running.

---

## ✨ Summary

**To run the project:**
```bash
cd "/Users/arunsudhaveni/Desktop/STATAHON PROJECT"
python3.13 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

**Then visit:**
- Landing Page: http://127.0.0.1:8000/
- All pages listed above will work automatically

**Everything should work automatically!** 🎉

---

**Created:** 24 March 2026  
**Version:** 1.0.0 - Complete STATAHON Application
