# 🚀 Survey AI - Quick Start Guide

## ⚡ Fastest Way to Get Started (Recommended)

### Option 1: Using the Startup Script (Recommended)

**On macOS/Linux:**
```bash
cd survey-ai-app
chmod +x start.sh
./start.sh
```

**On Windows (PowerShell):**
```powershell
cd survey-ai-app
npm install  # frontend
pip install -r backend/requirements.txt  # backend
# Start in two separate terminals:
# Terminal 1: cd backend && python main.py
# Terminal 2: cd frontend && npm run dev
```

The script will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start backend on `http://localhost:8001`
- ✅ Start frontend on `http://localhost:5173`
- ✅ Open demo login page

---

## 📋 Manual Setup (Step-by-Step)

### Step 1: Backend Setup

```bash
# Navigate to backend
cd survey-ai-app/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your database credentials
# (Update DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME as needed)

# Start backend server
python main.py
```

✅ Backend running on: `http://localhost:8001`

### Step 2: Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd survey-ai-app/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running on: `http://localhost:5173`

### Step 3: Access the Application

Open your browser and visit: `http://localhost:5173`

---

## 🔐 Demo Login

You have two options:

1. **Demo Login**
   - Click "Try Demo" button
   - Automatically logged in with demo credentials

2. **Test Login**
   - Email: `demo@survey-ai.com`
   - Password: (any password)

---

## 📊 Using Survey AI

### Dashboard
1. After login, you'll see the Dashboard
2. View statistics about available datasets
3. Click "Explore Data" or use sidebar to go to Survey AI

### Survey AI (Data Explorer)
1. **Select a Dataset** - Choose from available datasets
2. **Choose Columns** - Select which columns to display
3. **Apply Filters** - Add filters based on data types
4. **View Data** - Browse results in the table
5. **See Charts** - Check visualizations automatically generated

---

## ⚙️ Configuration

### Database Connection

Edit `backend/.env`:

```
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=survey_db
```

### Frontend Configuration

Edit `frontend/src/` constants if backend is on different URL:

```javascript
const API_BASE_URL = 'http://localhost:8001';
```

---

## 🛑 Stopping the Application

### Using Startup Script
```bash
# Press Ctrl+C in the terminal where start.sh is running
```

### Manual Cleanup
```bash
# Find and kill processes
# macOS/Linux:
lsof -i :8001    # Find backend
lsof -i :5173    # Find frontend
kill -9 PID      # Kill by PID

# Windows:
netstat -ano | findstr :8001
taskkill /PID 1234 /F
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```
Error: Could not connect to database
Solution: 
- Check PostgreSQL is running
- Verify credentials in .env (DB_PASSWORD, DB_HOST, etc.)
- Try: psql -U postgres -h 127.0.0.1
```

### Port Already in Use
```
Error: Address already in use
Solution:
- Kill existing process: lsof -i :8001 | awk 'NR>1 {print $2}' | xargs kill -9
- Or change PORT in backend/main.py
```

### Frontend Dependencies Error
```
Error: npm ERR! missing script: "dev"
Solution:
- Delete node_modules: rm -rf node_modules
- Reinstall: npm install
- Run: npm run dev
```

### Database Connection Failed
```
Solution steps:
1. Verify PostgreSQL is running
2. Check .env credentials match your PostgreSQL setup
3. Create database if needed: createdb survey_db
4. Test connection: psql -U postgres -h 127.0.0.1 -d survey_db
```

---

## 📚 Project Structure

```
survey-ai-app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment template
│   └── .env                 # Your configuration (create this)
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx         # React entry point
│   │   ├── App.jsx          # Main app component
│   │   ├── pages/           # Page components
│   │   └── components/      # Reusable components
│   ├── package.json         # Node dependencies
│   └── index.html          # HTML entry point
│
├── start.sh                 # Startup script
├── README.md               # Full documentation
└── QUICK_START.md          # This file
```

---

## 🎯 Next Steps

1. **Explore Datasets**
   - Select a dataset
   - Choose columns to display
   - Apply filters to narrow results

2. **View Visualizations**
   - Automatic charts generated for numeric data
   - Multiple chart types available
   - Interactive tooltips

3. **Export Data**
   - (Optional feature to be added)
   - Download filtered results
   - Export as CSV/JSON

4. **Customize Settings**
   - Go to Settings page
   - Configure preferences
   - Change display options

---

## 📖 Commands Reference

### Backend Commands
```bash
# Start backend
python main.py

# Check API health
curl http://localhost:8001/health

# View API documentation
# Visit: http://localhost:8001/docs
```

### Frontend Commands
```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm install          # Install dependencies
npm list             # List installed packages
```

### Database Commands
```bash
# Connect to PostgreSQL
psql -U postgres -h 127.0.0.1 -d survey_db

# List tables in database
\dt

# Exit PostgreSQL
\q
```

---

## 🌐 API Endpoints Quick Reference

- `GET /health` - Health check
- `GET /datasets` - List all datasets
- `GET /columns/{table}` - Get table columns
- `POST /data` - Fetch data with filters
- `GET /statistics/{table}` - Get table statistics

Full API docs: `http://localhost:8001/docs`

---

## 💡 Tips & Tricks

1. **Fast Demo**
   - Click "Try Demo" for instant access
   - No credentials needed
   - Full feature access

2. **Performance**
   - Start with smaller datasets first
   - Limit rows per page if slow
   - Close unused applications

3. **Development**
   - Frontend has hot reload (auto-refresh on save)
   - Backend needs restart for code changes
   - Check browser console for frontend errors

4. **Database**
   - Never destroy survey_db in development
   - Keep backup of important data
   - Test queries before running

---

## 🆘 Getting Help

1. **Check Logs**
   - Frontend: Browser console (F12)
   - Backend: Terminal output
   - Database: PostgreSQL logs

2. **Common Issues**
   - Clear browser cache: Ctrl+Shift+Del
   - Restart servers completely
   - Check firewall settings

3. **Resources**
   - Backend API Docs: http://localhost:8001/docs
   - Frontend Console: F12 in browser
   - README.md for full documentation

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] Can login to application
- [ ] Dashboard displays statistics
- [ ] Can select a dataset
- [ ] Can view data in table
- [ ] Charts are visible
- [ ] Filters work correctly
- [ ] Settings page accessible
- [ ] Can logout successfully

---

**You're all set! Happy exploring! 🎉**

Start with the startup script for the easiest experience:
```bash
cd survey-ai-app && chmod +x start.sh && ./start.sh
```
