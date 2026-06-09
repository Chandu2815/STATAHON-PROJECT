# ⚠️ CRITICAL: NGINX Configuration for statquery.in

## THE PROBLEM
Your server is returning `{"detail":"Resource not found"}` which looks like a FastAPI error, not a web server error. This means:
1. NGINX is forwarding the request to the backend
2. The backend is treating it as an API request
3. The frontend files are NOT being served

## THE SOLUTION

You need to update NGINX on `statquery.in` to properly serve the React frontend BEFORE trying to proxy to the backend.

---

## Step 1: SSH to Your Server

```bash
ssh user@statquery.in
# or
ssh ubuntu@statquery.in
```

---

## Step 2: Create/Update the Site Configuration

```bash
sudo nano /etc/nginx/sites-available/statquery
```

Replace the entire content with this exact configuration:

```nginx
# Survey AI Main Configuration
server {
    listen 80;
    listen [::]:80;
    server_name statquery.in;

    # Root directory for main site
    root /var/www/html;

    # === CRITICAL: Survey AI Frontend ===
    # Must come BEFORE the proxy config
    location /survey-ai/ {
        # IMPORTANT: This directory must contain index.html and assets/
        alias /var/www/survey-ai/dist/;
        
        # THIS IS CRITICAL FOR REACT SPA: Redirect all 404s to index.html
        # This allows React Router to handle all routes
        try_files $uri $uri/ /index.html;
        
        # Caching for assets (long cache for versioned files)
        location ~ \.(js|css)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Don't cache index.html (no cache)
        location = /index.html {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
    }

    # === API Proxy (AFTER frontend config) ===
    location /api/ai/ {
        # Proxy to backend on port 8001
        proxy_pass http://127.0.0.1:8001/;
        
        # Important headers for proxying
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /api/health {
        proxy_pass http://127.0.0.1:8001/health;
    }

    # Other locations (default)
    location / {
        index index.html;
        try_files $uri $uri/ =404;
    }
}
```

---

## Step 3: Enable the Configuration

```bash
# Test the configuration before applying
sudo nginx -t

# If test passes, enable the site
sudo ln -sf /etc/nginx/sites-available/statquery /etc/nginx/sites-enabled/

# Disable default if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# Restart NGINX
sudo systemctl restart nginx

# Verify it's running
sudo systemctl status nginx
```

---

## Step 4: Deploy the Frontend Files

ON YOUR LOCAL MACHINE:
```bash
cd /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/survey-ai-app/frontend

# Make sure latest build exists
npm run build

# List files to verify
ls -la dist/
# Should show: index.html, assets/
```

THEN ON YOUR SERVER:
```bash
# Create directory if needed
sudo mkdir -p /var/www/survey-ai/dist

# Copy files from your local machine
# Option A: Using SCP (from your local machine)
scp -r /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/survey-ai-app/frontend/dist/* user@statquery.in:/var/www/survey-ai/dist/

# Option B: If files are already on server, copy them
# sudo rm -rf /var/www/survey-ai/dist/*
# sudo cp -r ~/survey-ai-app/frontend/dist/* /var/www/survey-ai/dist/

# Set correct permissions
sudo chown -R www-data:www-data /var/www/survey-ai
sudo chmod -R 755 /var/www/survey-ai
sudo chmod -R 644 /var/www/survey-ai/dist/*
sudo chmod -R 755 /var/www/survey-ai/dist/assets
```

Verify files are in place:
```bash
ls -la /var/www/survey-ai/dist/
# Should show:
# -rw-r--r-- ... index.html
# drwxr-xr-x ... assets
# -rw-r--r-- ... assets/index-*.js
# -rw-r--r-- ... assets/index-*.css
```

---

## Step 5: Verify Everything Works

### Test 1: Frontend Loads
```bash
curl -s http://statquery.in/survey-ai/ | head -5
# Should return HTML like:
# <!DOCTYPE html>
# <html lang="en">
# NOT: {"detail":"Resource not found"}
```

### Test 2: API Works
```bash
curl -s http://statquery.in/api/health
# Should return:
# {"status":"healthy","message":"Survey AI API is running"}
```

### Test 3: Datasets Load
```bash
curl -s http://statquery.in/api/ai/datasets/hierarchical | head -10
# Should return JSON with HCES, PLFS, Survey, Other categories
```

### Test 4: In Browser
1. Open: `http://statquery.in/survey-ai/`
2. Look for: Survey Data Dashboard page
3. Check browser DevTools (F12):
   - Console should show: `🔄 Fetching hierarchical datasets...`
   - Network should show: `/survey-ai/` returns 200, `/api/ai/...` returns 200
   - NO 404 errors

---

## TROUBLESHOOTING

### Still Getting "Resource not found"?

**Step 1: Check files are deployed**
```bash
sudo ls -la /var/www/survey-ai/dist/
# Must show index.html and assets directory
# If empty or missing, file deployment failed
```

**Step 2: Check NGINX config**
```bash
sudo nginx -T | grep -A 30 "location /survey-ai"
# Verify:
# - "alias /var/www/survey-ai/dist/;" is present
# - "try_files $uri $uri/ /index.html;" is present
```

**Step 3: Check NGINX error logs**
```bash
sudo tail -f /var/log/nginx/error.log

# You might see errors like:
# open() "/var/www/survey-ai/dist/index.html" failed (2: No such file or directory)
# This means files aren't deployed
```

**Step 4: Check file permissions**
```bash
sudo ls -l /var/www/survey-ai/dist/index.html
# Should show: -rw-r--r-- (644)

# If owned by root (not www-data), fix with:
sudo chown www-data:www-data /var/www/survey-ai/dist/*
```

**Step 5: Force NGINX reload**
```bash
sudo systemctl stop nginx
sudo systemctl start nginx
# or
sudo systemctl restart nginx
```

---

## VERIFY CORRECT SETUP

### Directory Structure (on server)
```
/var/www/survey-ai/dist/
├── index.html           ← Main React app
├── assets/
│   ├── index-*.js       ← JavaScript bundle
│   ├── index-*.css      ← CSS bundle
│   └── ...
```

### NGINX Config Structure
```
location /survey-ai/ {
    alias /var/www/survey-ai/dist/;
    try_files $uri $uri/ /index.html;  ← CRITICAL
}

location /api/ai/ {
    proxy_pass http://127.0.0.1:8001/;  ← CRITICAL
}
```

### Expected Behavior
```
Request: statquery.in/survey-ai/
↓
NGINX checks: /var/www/survey-ai/dist/index.html
↓
File found → Return HTML ✅

Request: statquery.in/survey-ai/some-route (doesn't exist)
↓
NGINX tries: /uri /uri/ /index.html
↓
/index.html found → React Router handles it ✅

Request: statquery.in/api/ai/datasets
↓
NGINX proxies to: 127.0.0.1:8001/datasets
↓
Backend responds ✅
```

---

## QUICK CHECKLIST

- [ ] SSH to server
- [ ] Update NGINX config at `/etc/nginx/sites-available/statquery`
- [ ] Config has `/survey-ai/` location block
- [ ] Config has `alias /var/www/survey-ai/dist/;`
- [ ] Config has `try_files $uri $uri/ /index.html;`
- [ ] Config has `/api/ai/` proxy block
- [ ] `sudo nginx -t` passes
- [ ] `sudo systemctl restart nginx` succeeds
- [ ] `/var/www/survey-ai/dist/index.html` exists
- [ ] `curl http://statquery.in/survey-ai/` returns HTML
- [ ] `curl http://statquery.in/api/health` returns JSON
- [ ] Browser opens `statquery.in/survey-ai/` and shows Survey AI app

---

## IMPORTANT NOTES

⚠️ **Order Matters**: The `/survey-ai/` location MUST come BEFORE `/api/` location in NGINX config
⚠️ **Alias vs Root**: Using `alias` not `root` with subpaths
⚠️ **try_files**: This is CRITICAL for React SPA - tells NGINX to serve index.html for all 404s
⚠️ **Permissions**: NGINX (www-data) must be able to read files

---

## STILL NOT WORKING?

If you're still seeing errors, reply with:
1. Output of: `sudo ls -la /var/www/survey-ai/dist/`
2. Output of: `sudo nginx -t`
3. Output of: `curl -I http://statquery.in/survey-ai/`
4. Output of: `sudo tail -20 /var/log/nginx/error.log`

This will help diagnose exactly what's wrong.
