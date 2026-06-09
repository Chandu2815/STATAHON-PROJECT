# Survey AI - Quick Troubleshooting Guide

## Current Status
✅ Frontend built successfully at `/survey-ai-app/frontend/dist/`
✅ Backend running at `localhost:8001`
❌ Production deployment at `statquery.in/survey-ai` showing "Resource not found"

---

## Issue: "Resource not found" at statquery.in/survey-ai

### Root Cause
NGINX on statquery.in is not properly configured to:
1. Serve React SPA (Single Page Application)
2. Redirect all routes to `index.html`
3. Proxy API requests to backend

### Immediate Fix Required

**On your server (statquery.in), update NGINX config:**

```bash
sudo nano /etc/nginx/sites-available/survey-ai
```

**Replace with this configuration:**

```nginx
server {
    listen 80;
    server_name statquery.in;

    # Survey AI Frontend
    location /survey-ai/ {
        alias /var/www/survey-ai/dist/;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ai/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Then apply changes:**

```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## Local Testing (Before Deployment)

### Step 1: Test Backend API

```bash
# Test health endpoint
curl http://localhost:8001/health

# Expected output:
# {"status":"healthy","message":"Survey AI API is running"}

# Test datasets endpoint
curl http://localhost:8001/datasets/hierarchical

# Expected output:
# {"success":true,"data":{"HCES":[...],"PLFS":[...],...},"total_datasets":35}
```

### Step 2: Test Frontend Build Locally

```bash
cd /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/survey-ai-app/frontend

# Preview production build
npm run preview

# This will serve at http://localhost:4173/survey-ai/
# Open in browser and test:
# - Datasets load in dropdown ✓
# - Data explorer works ✓
# - Filtering functions ✓
```

### Step 3: Test in Development Mode

```bash
cd /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/survey-ai-app/frontend

# Start dev server
npm run dev

# Open http://localhost:5173/survey-ai/
# This uses Vite proxy: /api/ai → http://localhost:8001
```

---

## Deployment Checklist

### On Local Machine:

- [ ] Frontend builds with `npm run build`
- [ ] Build output at `survey-ai-app/frontend/dist/`
- [ ] Preview works with `npm run preview`
- [ ] All files present:
  - `dist/index.html`
  - `dist/assets/index-*.js`
  - `dist/assets/index-*.css`

### On Production Server:

- [ ] SSH to server: `ssh user@statquery.in`
- [ ] Deploy files: `sudo cp -r dist/* /var/www/survey-ai/dist/`
- [ ] NGINX config updated with `alias /var/www/survey-ai/dist/;` and `try_files $uri $uri/ /index.html;`
- [ ] Permissions set: `sudo chown -R www-data:www-data /var/www/survey-ai`
- [ ] NGINX restarted: `sudo systemctl restart nginx`

### Testing After Deployment:

```bash
# Test frontend loads
curl http://statquery.in/survey-ai/ | head -20

# Should show HTML starting with <!DOCTYPE html>
# NOT: {"detail":"Resource not found"}

# Test API
curl http://statquery.in/api/ai/health

# Should return: {"status":"healthy",...}

# Test pagination
curl http://statquery.in/api/ai/datasets/hierarchical | jq '.data | keys'

# Should show: ["HCES", "PLFS", "Survey", "Other"]
```

---

## Common Issues & Fixes

### Issue 1: Still getting "Resource not found"

**Cause:** Files not deployed or NGINX config incorrect

**Fix:**
```bash
# Verify files are in place
ls -la /var/www/survey-ai/dist/

# Should show: index.html, assets/ directory

# Verify NGINX config
sudo nginx -T | grep -A 20 "survey-ai"

# If config looks wrong, regenerate and test
sudo nginx -t
```

### Issue 2: Assets (CSS/JS) not loading

**Cause:** Wrong base path in Vite build

**Fix:**
- ✅ Already fixed in `vite.config.js` with `base: '/survey-ai/'`
- Force rebuild: `npm run build`
- Clear browser cache: `Ctrl+Shift+Delete`

### Issue 3: API returns 404

**Cause:** Backend not running or API proxy broken

**Fix:**
```bash
# Check backend
curl http://localhost:8001/health

# If not running, start it:
cd /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/survey-ai-app/backend
python -m uvicorn main:app --port 8001 --host 0.0.0.0

# On production, check proxy:
sudo tail -f /var/log/nginx/error.log
```

### Issue 4: Token not passing through

**Cause:** Sidebar redirect not working

**Fix:**
- Check localStorage in browser (F12 → Application → Local Storage)
- Should show `authToken` key with value
- Check URL when redirected: `statquery.in/survey-ai?token=<value>`

---

## Development vs Production URLs

### Development (localhost)
- Frontend: `http://localhost:5173/survey-ai/`
- API: `http://localhost:5173/api/ai/` (Vite proxy)
- Backend: `http://localhost:8001/`
- Uses: `.env` file

### Production (statquery.in)
- Frontend: `http://statquery.in/survey-ai/`
- API: `http://statquery.in/api/ai/` (NGINX proxy)
- Backend: `http://localhost:8001/` (same server)
- Uses: `.env.production` file

---

## Browser Console Debugging

Open DevTools (F12) and check:

### Console Tab
```javascript
// Check if app loaded
console.logs should show:
// "🔄 Fetching hierarchical datasets from /api/ai/datasets/hierarchical"
// "✅ Hierarchical datasets response: {success: true, ...}"
```

### Network Tab
```
Look for requests:
- GET /survey-ai/index.html → 200 OK ✓
- GET /survey-ai/assets/index-*.js → 200 OK ✓
- GET /survey-ai/assets/index-*.css → 200 OK ✓
- GET /api/ai/datasets/hierarchical → 200 OK ✓

If any GET → 404, that's the issue
```

### Application Tab
```
Local Storage should contain:
- authToken: "demo-token-..."
- userEmail: "user@example.com"
```

---

## Step-by-Step Fix (For statquery.in)

### 1. SSH to Server
```bash
ssh ubuntu@statquery.in  # or your user
```

### 2. Update NGINX Config
```bash
# Backup old config
sudo cp /etc/nginx/sites-available/survey-ai /etc/nginx/sites-available/survey-ai.bak

# Edit config
sudo nano /etc/nginx/sites-available/survey-ai

# Paste the configuration from NGINX_DEPLOYMENT_FIX.md
```

### 3. Deploy Latest Frontend
```bash
# On your local machine, build and copy
cd survey-ai-app/frontend
npm run build

# Then on the server:
sudo rm -rf /var/www/survey-ai/dist/*
sudo cp -r dist/* /var/www/survey-ai/dist/
```

### 4. Restart NGINX
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Test
```bash
curl http://statquery.in/survey-ai/
# Should return HTML, not error
```

---

## Files That Were Fixed

✅ **Vite Config** (`vite.config.js`)
- Set base path to `/survey-ai/`
- Proxy `/api/ai/` to `localhost:8001`

✅ **API Integration** (`src/pages/SurveyAI.jsx`)
- Uses `/api/ai/datasets/hierarchical` endpoint
- Fixed axios instance with baseURL

✅ **Hierarchical Datasets** (`src/components/HierarchicalDatasetSelector.jsx`)
- Displays data organized by category
- Proper search and filtering

✅ **External Redirect** (`src/components/Sidebar.jsx`)
- Passes token to external Survey AI URL
- Handles authentication

---

## Quick Links

📄 **Full Deployment Guide:** See `NGINX_DEPLOYMENT_FIX.md`
📄 **Build Guides:** See `QUICK_BUILD_GUIDE.md` and `PRODUCTION_DEPLOYMENT_GUIDE.md`
🔗 **Frontend Build:** `/survey-ai-app/frontend/dist/`
🔗 **Backend:** Port 8001

---

## Need Help?

1. Check browser console (F12) for errors
2. Check NGINX error logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify backend: `curl http://localhost:8001/health`
4. Rebuild frontend: `npm run build`
5. Review NGINX config matches provided template exactly
