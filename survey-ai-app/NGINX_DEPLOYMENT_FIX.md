# NGINX Configuration Fix for Survey AI Frontend

## Problem
The frontend is returning "Resource not found" error at `statquery.in/survey-ai` because NGINX isn't properly configured to serve the React Single Page Application (SPA).

## Root Cause
NGINX needs to:
1. Serve the frontend files from the `/dist` directory
2. Handle SPA routing by redirecting all requests to `index.html`
3. Proxy API requests to the backend at `localhost:8001`

---

## Solution: NGINX Configuration

### Step 1: Create the NGINX Configuration File

SSH to your server and create/edit the NGINX config:

```bash
sudo nano /etc/nginx/sites-available/survey-ai
```

### Step 2: Add the Correct Configuration

```nginx
# Survey AI Configuration
server {
    listen 80;
    server_name statquery.in;

    # Redirect HTTP to HTTPS (if using HTTPS)
    # Uncomment if SSL is configured:
    # return 301 https://$server_name$request_uri;

    # Survey AI Frontend at /survey-ai/
    location /survey-ai/ {
        alias /var/www/survey-ai/dist/;
        
        # CRITICAL: SPA routing - redirect all 404s to index.html
        try_files $uri $uri/ /index.html;
        
        # Cache busting for assets
        location ~ \.(js|css)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Don't cache index.html
        location = /index.html {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
    }

    # API Proxy at /api/ai/
    location /api/ai/ {
        proxy_pass http://localhost:8001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers (if needed)
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
    }

    # Health check endpoint for backend
    location /health {
        proxy_pass http://localhost:8001/health;
    }
}
```

### Step 3: Enable the Configuration

```bash
# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/survey-ai /etc/nginx/sites-enabled/

# Test NGINX configuration
sudo nginx -t

# If test passes, restart NGINX
sudo systemctl restart nginx
```

### Step 4: Deploy Frontend Files

Copy the built frontend files to the NGINX directory:

```bash
# Create the directory if it doesn't exist
sudo mkdir -p /var/www/survey-ai

# Copy dist files
sudo cp -r /path/to/survey-ai-app/frontend/dist/* /var/www/survey-ai/dist/

# Set proper permissions
sudo chown -R www-data:www-data /var/www/survey-ai
sudo chmod -R 755 /var/www/survey-ai
```

### Step 5: Verify Deployment

Test the endpoints:

```bash
# Test frontend
curl http://statquery.in/survey-ai/

# Should return HTML content, not "Resource not found"

# Test API
curl http://statquery.in/api/ai/health

# Should return: {"status":"healthy","message":"Survey AI API is running"}

# Test hierarchical datasets
curl http://statquery.in/api/ai/datasets/hierarchical

# Should return datasets organized by category
```

---

## Alternative: Using Subdomain (Recommended)

If you prefer cleaner URLs, configure a subdomain:

```nginx
server {
    listen 80;
    server_name survey-ai.statquery.in;

    location / {
        alias /var/www/survey-ai/dist/;
        try_files $uri $uri/ /index.html;
        
        location ~ \.(js|css)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        location = /index.html {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
    }

    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then update your environment variables:

```env
VITE_API_URL=https://survey-ai.statquery.in/api
```

---

## Troubleshooting

### Issue: Still getting "Resource not found"

**Solution:**
```bash
# Check if dist files are correctly placed
ls -la /var/www/survey-ai/dist/

# Verify NGINX is reading the config
sudo nginx -t

# Check NGINX error logs
sudo tail -f /var/log/nginx/error.log

# Check access logs
sudo tail -f /var/log/nginx/access.log
```

### Issue: API requests returning 404

**Solution:**
```bash
# Verify backend is running
curl http://localhost:8001/health

# Check if proxy is working
curl -i http://statquery.in/api/ai/health

# Look for X-Forwarded headers in backend logs
```

### Issue: CSS/JS not loading

**Solution:**
- Check browser Network tab (F12 → Network)
- Look for correct URLs: `/survey-ai/assets/...`
- Clear browser cache (Ctrl+Shift+Delete)
- Verify file permissions: `sudo chmod -R 755 /var/www/survey-ai`

---

## Production Deployment Checklist

- [ ] NGINX config file created at `/etc/nginx/sites-available/survey-ai`
- [ ] Configuration tested with `sudo nginx -t`
- [ ] Frontend files copied to `/var/www/survey-ai/dist/`
- [ ] File permissions set correctly (`755`)
- [ ] NGINX restarted: `sudo systemctl restart nginx`
- [ ] Frontend loads at `statquery.in/survey-ai/`
- [ ] API endpoint responds at `statquery.in/api/ai/health`
- [ ] Datasets load in dropdown
- [ ] Data explorer works with filtering

---

## Quick Deploy Script

Save this as `deploy.sh` and run on your server:

```bash
#!/bin/bash

# Stop on error
set -e

echo "🚀 Deploying Survey AI Frontend..."

# Build frontend
echo "📦 Building frontend..."
cd ~/survey-ai-app/frontend
npm run build

# Deploy to NGINX
echo "📁 Deploying to NGINX..."
sudo cp -r dist/* /var/www/survey-ai/dist/
sudo chown -R www-data:www-data /var/www/survey-ai

# Verify
echo "✅ Checking deployment..."
curl -s http://statquery.in/api/ai/health | head -50

echo "✅ Deployment complete!"
```

Run it:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Environment File for Production

Update `survey-ai-app/frontend/.env.production`:

```env
VITE_API_URL=https://statquery.in/api/ai
```

This ensures API calls go to the correct backend in production.

---

## Next Steps

1. **Update Sidebar component** (already done) ✅
   - Passes token to external Survey AI URL

2. **Configure NGINX** (follow above steps)
   - Deploy frontend files
   - Set up proxy routes
   - Configure SPA routing

3. **Restart backend**
   - Ensure port 8001 is accessible

4. **Test endpoints**
   - Frontend: `statquery.in/survey-ai`
   - API: `statquery.in/api/ai/health`
   - Datasets: `statquery.in/api/ai/datasets/hierarchical`

---

## Support Links

- [NGINX SPA Configuration](https://router.vuejs.org/guide/essentials/history-mode.html#nginx)
- [NGINX Proxy Documentation](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
