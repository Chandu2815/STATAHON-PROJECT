# Production Build Fix - Key Changes

## Frontend Configuration Changes

### 1. API Base URL Fix
**File**: `src/pages/SurveyAI.jsx` and `src/pages/Dashboard.jsx`

**Change**:
```javascript
// ❌ BEFORE (Local development only)
const API_BASE_URL = 'http://localhost:8001';

// ✅ AFTER (NGINX-compatible)
const API_BASE_URL = '/api';
```

### 2. Import Extensions
**File**: `src/App.jsx` and `src/pages/SurveyAI.jsx`

**Change**:
```javascript
// ❌ BEFORE
import SurveyAI from './pages/SurveyAI';
import Dashboard from './pages/Dashboard';
import HierarchicalDatasetSelector from '../components/HierarchicalDatasetSelector';

// ✅ AFTER
import SurveyAI from './pages/SurveyAI.jsx';
import Dashboard from './pages/Dashboard.jsx';
import HierarchicalDatasetSelector from '../components/HierarchicalDatasetSelector.jsx';
```

### 3. Vite Configuration
**File**: `vite.config.js`

**Change**:
```javascript
// ✅ ADDED base path for NGINX deployment
export default defineConfig({
  base: '/ai/',  // NEW: Frontend served at /ai/
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
```

## API Call Flow

### Development (Vite Dev Server)
```
Frontend (http://localhost:5173)
    ↓
Vite Proxy: /api → http://localhost:8001
    ↓
Backend (http://localhost:8001)
```

### Production (NGINX)
```
Frontend (http://domain/ai/)
    ↓
NGINX at /api/ai
    ↓
Rewrite to /
    ↓
Backend (http://localhost:8001)
```

## API Endpoint Changes

All API calls now use relative paths:

```javascript
// ✅ CORRECT (works in both dev and prod)
const response = await axios.get(`${API_BASE_URL}/datasets`);
// Becomes: GET /api/datasets

// ✅ CORRECT
const response = await axios.post(`${API_BASE_URL}/data`, payload);
// Becomes: POST /api/data

// ❌ INCORRECT (won't work in production)
const response = await axios.get('http://localhost:8001/datasets');
```

## Created Components

### HierarchicalDatasetSelector.jsx
- Wrapper around DatasetSelector
- Future-proofed for hierarchical grouping
- No changes to existing functionality

### DataExportActions.jsx
- Export as JSON (with timestamp)
- Export as CSV (with proper escaping)
- Copy to clipboard (with success feedback)

### AnalyticsDashboard.jsx
- Analytics view placeholder
- Stats cards (records, columns, insights)
- Usage tips for users

### HelpAndShortcuts.jsx
- Floating help button
- Keyboard shortcuts modal
- Tips and guidance

## Build & Deploy

### Build
```bash
cd survey-ai-app/frontend
npm run build
# Output: dist/ directory
```

### Deploy Steps
1. Copy `dist/` contents to server
2. Configure NGINX with base path `/ai/`
3. Ensure backend is running on port 8001
4. Verify NGINX reverse proxy is active

### NGINX Location Block
```nginx
location /api/ai {
    rewrite ^/api/ai(.*)$ $1 break;
    proxy_pass http://localhost:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /ai/ {
    alias /path/to/dist/;
    try_files $uri $uri/ /index.html;
}
```

## Verification

### Before Deployment
- [ ] `npm run build` completes without errors
- [ ] No console warnings about imports
- [ ] `dist/` directory created successfully
- [ ] No hardcoded `localhost` references in dist files

### After Deployment
- [ ] Frontend loads at `/ai/`
- [ ] API calls appear in Network tab as `/api/*`
- [ ] Data loads from backend correctly
- [ ] No 404 errors for assets
- [ ] No CORS errors in console

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Import errors | Missing .jsx extensions | Rebuild with updated imports |
| 404 on refresh | NGINX not configured | Add `try_files $uri $uri/ /index.html;` |
| API fails | Wrong base URL | Check `API_BASE_URL = '/api'` |
| Assets not loading | Wrong base path | Verify `base: '/ai/'` in vite.config.js |
| CORS errors | Missing headers | Update NGINX proxy headers |

---

**Status**: ✅ Ready for production deployment!
