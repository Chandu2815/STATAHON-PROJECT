# Quick Start Guide - Role-Based Portal

## 🚀 Access the Portal

### **Main URL**: http://localhost:8080

## 📋 Test Accounts

| Role | Username | Password | Redirects To |
|------|----------|----------|--------------|
| **Admin** | `admin` | `admin123` | API Docs (`/docs`) |
| **Researcher** | `researcher1` | `researcher123` | Dashboard (`/dashboard`) |
| **Public** | `publicuser` | `public123` | Dashboard (`/dashboard`) |

## 🔐 Login Steps

1. Go to: http://localhost:8080/login
2. Enter username and password
3. Click "Login"
4. Automatically redirected based on your role

## 📊 What Each User Sees

### Admin Users → API Documentation
- Full Swagger UI interface
- Direct API endpoint access
- User management
- System configuration
- Database operations

### Researchers & Public → User Dashboard
- Query builder with filters
- Interactive results table
- Export to CSV
- Credits balance
- Statistics overview

## 🔍 Sample Query (Dashboard)

1. **Select Dataset**: Person Survey (PLFS)
2. **Choose State**: Telangana
3. **Select Gender**: Male
4. **Pick Age Group**: 15-29
5. **Click**: "Run Query"
6. **Result**: 10,006+ records displayed
7. **Export**: Download as CSV

## ⚡ Quick Links

- **Login Page**: http://localhost:8080/login
- **Landing Page**: http://localhost:8080/
- **Dashboard**: http://localhost:8080/dashboard
- **API Docs**: http://localhost:8080/docs

## 💡 Key Features

✅ Role-based automatic routing  
✅ Secure JWT authentication  
✅ User-friendly query builder  
✅ Real-time results display  
✅ CSV export functionality  
✅ Credits tracking system  

## 🛠️ Current Status

✓ Server running on http://localhost:8080  
✓ 3 example users created  
✓ Login page active
✓ Dashboard functional  
✓ API docs accessible  
✓ 517,029 records available  
✓ 5 datasets ready to query  

## Test It Now!

**Open in browser**: http://localhost:8080/login

Try logging in with any of the example accounts above!
