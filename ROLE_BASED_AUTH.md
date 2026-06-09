# Role-Based Authentication System

## Overview
The MoSPI Data Portal now features a complete role-based authentication system with separate interfaces for different user types.

## Access URLs

### 🌐 Main Portal
- **Landing Page**: http://localhost:8080/
- **Login Page**: http://localhost:8080/login
- **User Dashboard**: http://localhost:8080/dashboard (Public & Researchers)
- **API Documentation**: http://localhost:8080/docs (Admins)

## User Roles & Access

### 1. 👤 Public Users
- **Purpose**: Basic access to public datasets
- **Access**: User dashboard with query interface
- **Credits**: 10 credits (free tier)
- **Features**:
  - View available datasets
  - Run basic queries with filters
  - Export results to CSV
  - Limited to 100 records per query

### 2. 🔬 Researchers
- **Purpose**: Advanced data analysis and research
- **Access**: User dashboard with enhanced features
- **Credits**: 100 credits
- **Features**:
  - All public user features
  - Higher query limits (up to 10,000 records)
  - Access to premium datasets
  - Priority query processing

### 3. ⚙️ Administrators
- **Purpose**: System management and API access
- **Access**: Full API documentation interface
- **Credits**: 1000 credits (unlimited)
- **Features**:
  - Full access to all API endpoints
  - User management capabilities
  - System configuration
  - Direct database access via API

## Demo Accounts

### Admin Account
```
Username: admin
Password: admin123
Redirects to: /docs (API Documentation)
```

### Researcher Account
```
Username: researcher1
Password: researcher123
Redirects to: /dashboard (User Dashboard)
```

### Public Account
```
Username: publicuser
Password: public123
Redirects to: /dashboard (User Dashboard)
```

## Login Flow

1. **All users start at**: http://localhost:8080/login
2. **Enter credentials** (username + password)
3. **System authenticates** and returns:
   - JWT access token
   - User role (admin/researcher/public)
   - Username
4. **Automatic redirect based on role**:
   - Admin → `/docs` (Swagger API documentation)
   - Researcher/Public → `/dashboard` (User-friendly interface)

## Dashboard Features

### Query Builder
- **Dataset Selection**: Choose from available datasets
  - Household Survey (PLFS)
  - Person Survey (PLFS)
  - Sample Census Data

- **Filters Available**:
  - State/UT (Telangana, Maharashtra, etc.)
  - Gender (Male, Female, Transgender)
  - Age Group (0-14, 15-29, 30-59, 60+)
  - District (based on selected state)
  - Custom limits (1-10,000 records)

### Results Display
- Interactive table with all query results
- Total record count
- Export to CSV functionality
- Pagination for large result sets

### Statistics Dashboard
- Total available datasets: 5
- Total records: 517,029
- Queries executed today
- Available credits balance

## API Changes

### Enhanced Login Endpoint
**Endpoint**: `POST /auth/login`

**Request** (Form Data):
```
username: admin
password: admin123
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_role": "admin",
  "username": "admin"
}
```

### Token Usage
All authenticated endpoints require:
```
Authorization: Bearer <access_token>
```

The token is automatically stored in localStorage and sent with all API requests from the dashboard.

## File Structure

```
app/
├── templates/
│   ├── login.html          # Login page for all users
│   └── dashboard.html      # Dashboard for public/researchers
├── api/
│   ├── auth.py             # Enhanced with role info in login response
│   └── frontend.py         # Added /login and /dashboard routes
└── models/
    └── user.py             # UserRole enum (public, researcher, admin)
```

## Security Features

1. **Password Hashing**: All passwords stored with bcrypt
2. **JWT Tokens**: Secure token-based authentication
3. **Role-Based Access Control**: Automatic route protection
4. **Token Expiration**: Configurable session timeout
5. **CORS Protection**: Cross-origin request validation

## Usage Examples

### Example 1: Public User Flow
```
1. Visit http://localhost:8080/login
2. Login with: publicuser / public123
3. Redirected to /dashboard
4. Select "Person Survey (PLFS)" dataset
5. Filter: State=TELANGANA, Gender=MALE, Age=15-29
6. Click "Run Query"
7. View 10,006 matching records
8. Export results to CSV
```

### Example 2: Admin Flow
```
1. Visit http://localhost:8080/login
2. Login with: admin / admin123
3. Redirected to /docs
4. Access full API documentation
5. Test endpoints directly from Swagger UI
6. Manage users, datasets, and system settings
```

### Example 3: Researcher Flow
```
1. Visit http://localhost:8080/login
2. Login with: researcher1 / researcher123
3. Redirected to /dashboard
4. Query with higher limits (10,000 records)
5. Access premium datasets
6. Download large result sets
```

## Testing

### 1. Test Login Page
```powershell
# Check if login page loads
Invoke-WebRequest http://localhost:8080/login
```

### 2. Test Authentication
```powershell
# Login as admin
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8080/auth/login" `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "username=admin&password=admin123"

# Check role in response
$response.user_role  # Should be "admin"
```

### 3. Test Dashboard Access
```powershell
# Check if dashboard loads
Invoke-WebRequest http://localhost:8080/dashboard
```

## Troubleshooting

### Issue: Login page shows "Login page not found"
**Solution**: Ensure `app/templates/login.html` exists

### Issue: Dashboard shows blank page
**Solution**: Ensure `app/templates/dashboard.html` exists

### Issue: Redirect not working after login
**Solution**: Check browser console for JavaScript errors, ensure localStorage is enabled

### Issue: Token expired error
**Solution**: Logout and login again to get fresh token

### Issue: "Unauthorized" on API calls
**Solution**: Ensure Authorization header is set with valid Bearer token

## Credits System

- **Public users**: Start with 10 credits
- **Researchers**: Start with 100 credits
- **Admins**: Start with 1000 credits
- **Query costs**:
  - Basic query (< 100 records): 0.1 credits
  - Medium query (100-1000 records): 0.5 credits
  - Large query (> 1000 records): 1 credit
- **Top-up**: Contact admin for credit purchases

## Next Steps

1. **Customize Dashboard**: Modify `dashboard.html` for your needs
2. **Add More Filters**: Update query form with additional fields
3. **Create Reports**: Add visualization components
4. **Implement Payments**: Integrate payment gateway for credit purchases
5. **Add Analytics**: Track user behavior and popular queries

## Support

For issues or questions:
- Email: support@mospi.gov.in
- API Docs: http://localhost:8080/docs
- GitHub: https://github.com/Chandu2815/STATAHON-PROJECT
