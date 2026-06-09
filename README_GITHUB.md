# MoSPI Data Portal Infrastructure

A comprehensive RESTful API platform for accessing and querying real Indian government statistical data from the Periodic Labour Force Survey (PLFS).

## 🎯 Project Overview

This project implements a complete **Data Portal Infrastructure** based on the Ministry of Statistics and Programme Implementation (MoSPI) requirements. It provides secure, efficient access to 1,472 real PLFS records through a modern RESTful API.

### ✨ Key Features

- **Multi-dimensional Data Access**: Query 695 district codes, 377 survey item codes, and 400 data layout records
- **Role-Based Access Control**: 4 user tiers (PUBLIC, RESEARCHER, PREMIUM, ADMIN) with different rate limits
- **Micro-Payment System**: Credit-based usage metering and billing
- **RESTful API**: 20 endpoints with OpenAPI/Swagger documentation
- **Real Government Data**: Authentic PLFS data from microdata.gov.in
- **Multi-Format Ingestion**: Supports XLSX, DOCX, PDF, and CSV formats
- **JWT Authentication**: Secure token-based authentication

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd "Statathon 2"
```

2. **Create virtual environment**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start the server**
```bash
.\start.ps1
```

Server will run at: http://127.0.0.1:8080

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://127.0.0.1:8080/docs
- **ReDoc**: http://127.0.0.1:8080/redoc

### Test Credentials
- Username: `tester`
- Password: `test1234`
- Role: `researcher`

## 🔧 Usage

### Method 1: Easy Query Tool (Recommended)
```bash
python query_data.py
```
Interactive menu to:
- View data summary
- Search districts and item codes
- Filter by state or block
- Browse sample records

### Method 2: Verify All Requirements
```bash
python verify_requirements.py
```
Tests all 7 problem statement requirements.

### Method 3: Direct API Testing
```bash
python test_real_data.py
```

## 📊 Real Data Statistics

- **695 District Codes** - All India districts with NSS codes
- **377 Item Codes** - Survey items across 8 blocks
- **400 Data Layout Records** - Structure definitions
- **Source**: microdata.gov.in (PLFS Survey)

## 🏗️ Architecture

```
app/
├── api/              # API route handlers
│   ├── auth.py       # Authentication endpoints
│   ├── datasets.py   # Dataset management
│   ├── plfs.py       # PLFS data queries
│   ├── query.py      # Advanced queries
│   └── users.py      # User management
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── services/         # Business logic
└── main.py           # FastAPI application
```

## 🎫 User Roles & Rate Limits

| Role | Daily Requests | Credits |
|------|---------------|---------|
| PUBLIC | 100 | 1,000 |
| RESEARCHER | 1,000 | 1,000 |
| PREMIUM | 10,000 | 1,000 |
| ADMIN | Unlimited | Unlimited |

## 🔐 Authentication

### Register
```bash
POST /api/v1/auth/register
{
  "username": "researcher01",
  "email": "researcher@example.com",
  "password": "SecurePass123",
  "full_name": "Data Researcher",
  "role": "researcher"
}
```

### Login
```bash
POST /api/v1/auth/login
{
  "username": "researcher01",
  "password": "SecurePass123"
}
```

### Use Token
```bash
Authorization: Bearer <your_token>
```

## 📋 Problem Statement Requirements

All 7 requirements implemented and verified:

✅ **Requirement 1**: Database Ingestion Framework  
✅ **Requirement 2**: Query Framework  
✅ **Requirement 3**: RESTful API  
✅ **Requirement 4**: Multi-dimensional Filtering  
✅ **Requirement 5**: Role-Based Access Control  
✅ **Requirement 6**: Micro-Payment System  
✅ **Requirement 7**: Developer Documentation  

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: SQLite with SQLAlchemy 2.0.23
- **Authentication**: JWT (python-jose)
- **Security**: bcrypt 4.0.1
- **Data Processing**: pandas 2.1.3, openpyxl, python-docx
- **Server**: uvicorn

## 📁 Project Structure

```
Statathon 2/
├── app/                    # Main application
├── data/                   # Data files (PLFS XLSX, DOCX, PDF)
├── mospi_dpi.db           # SQLite database
├── requirements.txt       # Python dependencies
├── start.ps1              # Quick start script
├── query_data.py          # Easy query tool
├── verify_requirements.py # Requirement tester
└── README.md              # This file
```

## 🧪 Testing

Run all requirement tests:
```bash
python verify_requirements.py
```

Expected output: **7/7 tests passing (100%)**

## 📝 License

This project was created for the STATATHON competition.

## 👥 Team

Created by Team Chandu for STATATHON 2

## 📞 Support

For issues or questions, please check:
- API Documentation: http://127.0.0.1:8080/docs
- Test the API with `query_data.py`
- Run verification with `verify_requirements.py`

---

**Built with ❤️ for MoSPI Data Portal Infrastructure**
