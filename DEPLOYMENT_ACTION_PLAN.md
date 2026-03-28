# 🚨 FIX: "Resource not found" on statquery.in/survey-ai

## THE PROBLEM
Your server is showing `{"detail":"Resource not found"}` which means NGINX is NOT serving the frontend - it's forwarding to the backend API instead.

## THE CAUSE
NGINX configuration is missing or incorrect. It needs to:
1. Serve `index.html` from `/var/www/survey-ai/dist/`
2. Handle React routing by redirecting to `index.html` on 404
3. Proxy API requests to backend

---

## ✅ IMMEDIATE FIX

### Step 1️⃣: SSH to Your Server
```bash
ssh ubuntu@statquery.in
# or
ssh user@statquery.in
```

### Step 2️⃣: Run Setup Script
Copy the exact NGINX config below:

```bash
sudo nano /etc/nginx/sites-available/statquery
```

**Paste this exactly:**

```nginx
server {
    listen 80;
    server_name statquery.in;

    location /survey-ai/ {
        alias /var/www/survey-ai/dist/;
        try_files $uri $uri/ /index.html;
    }

    location /api/ai/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Press: `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 3️⃣: Enable and Restart NGINX
```bash
sudo ln -sf /etc/nginx/sites-available/statquery /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

### Step 4️⃣: Deploy Frontend Files

**On your LOCAL machine:**
```bash
cd /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/survey-ai-app/frontend

# Build frontend
npm run build

# Deploy to server
scp -r dist/* ubuntu@statquery.in:/var/www/survey-ai/dist/

# Set permissions
ssh ubuntu@statquery.in 'sudo chown -R www-data:www-data /var/www/survey-ai && sudo chmod -R 755 /var/www/survey-ai'
```

---

### Step 5️⃣: Test

**In browser:**
- Open: `http://statquery.in/survey-ai/`
- Should show: Survey Data Dashboard with dropdown
- Should NOT show: `{"detail":"Resource not found"}`

**In terminal:**
```bash
curl http://statquery.in/survey-ai/ | head -20
# Should show: <!DOCTYPE html>

curl http://statquery.in/api/ai/health
# Should show: {"status":"healthy",...}
```

---

## ✅ VERIFY SETUP

**On server, check:**
```bash
# Files deployed?
ls -la /var/www/survey-ai/dist/
# Should show: index.html, assets/

# NGINX config correct?
sudo nginx -t
# Should show: test is successful

# Can access frontend?
curl -I http://statquery.in/survey-ai/
# Should show: HTTP/1.1 200 OK

# Can access API?
curl -I http://statquery.in/api/ai/health
# Should show: HTTP/1.1 200 OK
```

All 4 should pass ✅

---

## 🔥 IF STILL NOT WORKING

Check these in order:

1. **Are files deployed?**
   ```bash
   sudo ls -la /var/www/survey-ai/dist/index.html
   # If "No such file", files not copied
   ```

2. **Is NGINX config correct?**
   ```bash
   sudo cat /etc/nginx/sites-available/statquery | grep -A 3 "survey-ai"
   # Should show: alias and try_files
   ```

3. **Are nginx changes applied?**
   ```bash
   sudo systemctl restart nginx
   sudo systemctl status nginx
   # Should show: active (running)
   ```

4. **Check error logs:**
   ```bash
   sudo tail -20 /var/log/nginx/error.log
   # Look for file not found errors
   ```

---

## 📋 EXACT COMMANDS (Copy & Paste)

### On Server:
```bash
# 1. Create config
sudo nano /etc/nginx/sites-available/statquery

# 2. Enable site
sudo ln -sf /etc/nginx/sites-available/statquery /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 3. Test
sudo nginx -t

# 4. Restart
sudo systemctl restart nginx

# 5. Verify
curl -I http://statquery.in/survey-ai/
```

### On Local Machine:
```bash
# Build
cd survey-ai-app/frontend && npm run build

# Deploy
scp -r dist/* ubuntu@statquery.in:/var/www/survey-ai/dist/

# Fix permissions
ssh ubuntu@statquery.in 'sudo chown -R www-data:www-data /var/www/survey-ai'
```

---

## 🎯 WHAT HAPPENS WHEN FIXED

```
Client: GET /survey-ai/
  ↓
NGINX: Check /var/www/survey-ai/dist/index.html
  ↓
Found: Serve index.html ✅
  ↓
Browser: Loads React app
  ↓
App: Shows "Survey Data Dashboard"
  ↓
Dropdown: Shows datasets from /api/ai/datasets/hierarchical

Client: GET /api/ai/health
  ↓
NGINX: Proxy to 127.0.0.1:8001
  ↓
Backend: Returns health status ✅
```

---

## 📞 NEED HELP?

Reply with output of:
```bash
sudo ls -la /var/www/survey-ai/dist/
sudo nginx -T | grep -A 20 "survey-ai"
curl -I http://statquery.in/survey-ai/
sudo tail -10 /var/log/nginx/error.log
```

This will help me see exactly what's wrong.
